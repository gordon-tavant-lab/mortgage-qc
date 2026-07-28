"""
Full 5,365-row compile: all rows in the 5-loan scope
(output/RULE-PROGRAM-GATING-FINDINGS.md §8: FHA + VA + USDA + Fannie Mae).
Batches to avoid timeout, tracks real cost per batch, assembles a candidate
unsigned ruleset covering the entire scope.

Real Bedrock calls (Sonnet 4.6, temperature=0). Cost: ~$243 (measured, not
estimated, based on run_001's real average of $0.045/row).

Usage (from p0/, with AWS credentials):
    python3 compile_runs/run_002_full_5loan_scope/run_full.py
Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
P0 = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, P0)
sys.path.insert(0, os.path.join(P0, "eval_synth"))

import taxonomy as T  # noqa: E402
from qc_engine.catalog import FieldCatalog, ReferentialIntegrityError, load_catalog, \
    validate_referential_integrity  # noqa: E402
from qc_engine.compiler import compile_llm as C  # noqa: E402
from qc_engine.compiler import program_gating as PG  # noqa: E402
from qc_engine.ruleset import Ruleset  # noqa: E402

RULES_DIR = os.path.normpath(os.path.join(P0, "..", "demo", "rules"))
CATALOG_PATH = os.path.join(P0, "qc_engine", "field_catalog.json")
NEEDED_PROGRAMS = {"FHA", "VA", "USDA", "Fannie Mae"}
BATCH_SIZE = 50  # 50 rows per batch to keep Bedrock latency reasonable

# Pricing: Sonnet 4.6 on-demand, us-east-1
PRICE_PER_1K_INPUT = 0.003
PRICE_PER_1K_OUTPUT = 0.015


class _CostTrackingClient:
    def __init__(self, real_client):
        self._client = real_client
        self.calls: List[Dict[str, int]] = []

    def converse(self, **kwargs):
        resp = self._client.converse(**kwargs)
        usage = resp.get("usage", {})
        self.calls.append({
            "inputTokens": usage.get("inputTokens", 0),
            "outputTokens": usage.get("outputTokens", 0),
        })
        return resp


def load_all_scoped_rows() -> List[Dict[str, Any]]:
    """All 5,365 real rows in the scope."""
    paths = [os.path.join(RULES_DIR, f) for f in os.listdir(RULES_DIR)
             if f.lower().endswith(".xlsx") and not f.startswith("~$")]
    rows = []
    for p in paths:
        for row in T.load_rows(p):
            program = PG.parse_exception_code_prefix(row.get("exception_code") or "")
            if program not in NEEDED_PROGRAMS:
                continue
            arch_id = T.classify(row.get("defect_text", "") or "")
            engine_kind = {a["id"]: a for a in T.ARCHETYPES}.get(arch_id, {}).get("engine_kind", "predicate")
            row = dict(row)
            row["archetype_id"] = arch_id
            row["engine_kind"] = engine_kind
            row["source_file"] = os.path.basename(p)
            row["program"] = program
            row["row_id"] = f"{program.replace(' ', '')}-{len([r for r in rows if r['program'] == program]):04d}"
            rows.append(row)
    return rows


def run() -> Dict[str, Any]:
    """Compile all 5,365 rows in batches."""
    all_rows = load_all_scoped_rows()
    catalog = load_catalog(CATALOG_PATH)
    real_client = C._client()

    all_drafts = []
    all_costs = []
    batch_results = []

    for i in range(0, len(all_rows), BATCH_SIZE):
        batch = all_rows[i:i+BATCH_SIZE]
        tracked_client = _CostTrackingClient(real_client)
        batch_drafts = [C.compile_row(tracked_client, row, catalog) for row in batch]
        all_drafts.extend(batch_drafts)

        batch_input = sum(c["inputTokens"] for c in tracked_client.calls)
        batch_output = sum(c["outputTokens"] for c in tracked_client.calls)
        batch_cost = (batch_input / 1000 * PRICE_PER_1K_INPUT) + (batch_output / 1000 * PRICE_PER_1K_OUTPUT)
        all_costs.append(batch_cost)

        compiled_ok = sum(1 for d in batch_drafts if d.check is not None)
        failed = sum(1 for d in batch_drafts if d.check is None)

        batch_results.append({
            "batch_num": i // BATCH_SIZE + 1,
            "rows_in_batch": len(batch),
            "compiled_ok": compiled_ok,
            "failed": failed,
            "input_tokens": batch_input,
            "output_tokens": batch_output,
            "batch_cost_usd": round(batch_cost, 4),
        })
        print(f"Batch {i//BATCH_SIZE + 1}/{(len(all_rows)-1)//BATCH_SIZE + 1}: {len(batch)} rows, {compiled_ok} compiled, cost ${batch_cost:.4f}")

    compiled = [d for d in all_drafts if d.check is not None]
    failed = [d for d in all_drafts if d.check is None]

    # Referential-integrity screen
    proposed_entries = [d.proposed_field_entry for d in compiled if d.proposed_field_entry]
    working_catalog = FieldCatalog(
        catalog_id=catalog.catalog_id, version=catalog.version,
        entries=catalog.entries + proposed_entries,
    )
    candidate_ruleset = Ruleset(
        ruleset_id="run-002-full-5loan-scope-candidate", version=1,
        checks=[d.check for d in compiled],
    )
    try:
        validate_referential_integrity(candidate_ruleset, working_catalog)
        integrity_ok = True
        integrity_error = None
    except ReferentialIntegrityError as e:
        integrity_ok = False
        integrity_error = str(e)

    total_input = sum(c["inputTokens"] for c in [item for batch_res in batch_results for c in ({"inputTokens": batch_res["input_tokens"]},)])
    total_output = sum(c["outputTokens"] for c in [item for batch_res in batch_results for c in ({"outputTokens": batch_res["output_tokens"]},)])
    total_input = sum(b["input_tokens"] for b in batch_results)
    total_output = sum(b["output_tokens"] for b in batch_results)
    real_cost = sum(all_costs)

    grounded = [d for d in compiled if d.grounding is not None]

    program_dist = {}
    for d in compiled:
        prog = d.applicability.program if d.applicability else "unknown"
        program_dist[prog] = program_dist.get(prog, 0) + 1

    return {
        "total_rows": len(all_rows),
        "rows_attempted": len(all_rows),
        "compiled_ok": len(compiled),
        "parse_failures": len(failed),
        "grounded_count": len(grounded),
        "referential_integrity": "PASSED" if integrity_ok else f"BLOCKED: {integrity_error}",
        "proposed_new_fields": len(proposed_entries),
        "batch_results": batch_results,
        "real_cost": {
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "real_usd_total": round(real_cost, 2),
            "usd_per_row": round(real_cost / len(all_rows), 5),
        },
        "program_distribution": program_dist,
        "drafts_summary": {
            "total": len(all_drafts),
            "compiled": len(compiled),
            "failed": len(failed),
        },
    }


def _write_results_md(result: Dict[str, Any], path: str) -> None:
    lines = [
        "# Compile Run 002 — Full 5-Loan Scope",
        "",
        "**Status: real, unsigned, referential-integrity-screened candidate "
        "checks covering the entire 5,365-row scope.** Real Bedrock calls "
        "(Sonnet 4.6, temperature=0), real measured cost. Full rules-parsing "
        "process for the 5-loan scope (FHA + VA + USDA + Fannie Mae, per "
        "`output/RULE-PROGRAM-GATING-FINDINGS.md` §8).",
        "",
        "## Result",
        "",
        f"- Total rows in scope: {result['total_rows']}",
        f"- Compiled successfully: {result['compiled_ok']}",
        f"- Parse failures: {result['parse_failures']}",
        f"- Grounded (had signed KB): {result['grounded_count']}",
        f"- Referential integrity: **{result['referential_integrity']}**",
        f"- New fields proposed: {result['proposed_new_fields']}",
        "",
        "## Real cost (measured across all batches)",
        "",
        f"- Total input tokens: {result['real_cost']['total_input_tokens']:,}",
        f"- Total output tokens: {result['real_cost']['total_output_tokens']:,}",
        f"- Real spend: **${result['real_cost']['real_usd_total']}**",
        f"- Cost per row: ${result['real_cost']['usd_per_row']}",
        "",
        "## Batch summary",
        "",
    ]
    for b in result["batch_results"]:
        lines.append(f"- Batch {b['batch_num']}: {b['rows_in_batch']} rows → {b['compiled_ok']} compiled, cost ${b['batch_cost_usd']}")
    lines += [
        "",
        "## Compiled by program",
        "",
    ]
    for prog, count in sorted(result["program_distribution"].items()):
        lines.append(f"- {prog}: {count}")
    lines += [
        "",
        "## Next step",
        "",
        "This is a full, unsigned candidate ruleset. SME review and sign-off "
        "required before this can be run against real loans, per the existing "
        "`002b`/`002c` provenance discipline.",
    ]
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main() -> None:
    result = run()
    print(json.dumps(result, indent=2))
    results_path = os.path.join(HERE, "RESULTS.md")
    _write_results_md(result, results_path)
    print(f"\n[written] {results_path}")


if __name__ == "__main__":
    main()
