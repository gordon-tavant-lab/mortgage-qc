"""
The real compile run: takes sampled_batch.json (39 real rows, stratified
across the 4 programs the 5 loans actually need -- see
output/RULE-PROGRAM-GATING-FINDINGS.md §8) and compiles each through
compile_llm.compile_row -- one real Bedrock call per row, Sonnet 4.6,
temperature=0, unchanged production path (010a program-gating + 002c
grounding both apply automatically inside compile_row; only FHA has a
signed KB today, from the 002c proof, so grounding only fires there).

Wraps the Bedrock client to capture real per-call token usage -- no
modification to compile_llm.py itself -- so this run reports real cost, not
an estimate, and can extrapolate to the full 5,365-row §8 scope.

Bounded first tranche of the real rules-parsing process. Output is a
candidate (UNSIGNED) ruleset -- referential-integrity-screened but not
signed off, since no SME has reviewed these compiled checks yet. Sign-off
is a separate, explicit step (mirrors 002c's own discipline).

Usage (from p0/, with AWS credentials configured):
    python3 compile_runs/run_001_5loan_scope/run_batch.py
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

from qc_engine.catalog import FieldCatalog, ReferentialIntegrityError, load_catalog, \
    validate_referential_integrity  # noqa: E402
from qc_engine.compiler import compile_llm as C  # noqa: E402
from qc_engine.ruleset import Ruleset  # noqa: E402

CATALOG_PATH = os.path.join(P0, "qc_engine", "field_catalog.json")


class _CostTrackingClient:
    """Duck-typed wrapper around the real Bedrock client -- compile_row only
    ever calls .converse(), so this transparently records real usage without
    touching compile_llm.py's production code."""

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


# Sonnet 4.6 on-demand Bedrock pricing (us-east-1, per the compile call's own
# MODEL_SONNET), $/1K tokens -- input $0.003, output $0.015 as of this run.
PRICE_PER_1K_INPUT = 0.003
PRICE_PER_1K_OUTPUT = 0.015


def run() -> Dict[str, Any]:
    sample = json.load(open(os.path.join(HERE, "sampled_batch.json")))
    rows = sample["rows"]
    catalog = load_catalog(CATALOG_PATH)

    real_client = C._client()
    tracked_client = _CostTrackingClient(real_client)

    drafts = [C.compile_row(tracked_client, row, catalog) for row in rows]

    compiled = [d for d in drafts if d.check is not None]
    failed = [d for d in drafts if d.check is None]

    # Referential-integrity screen (existing 002b mechanism) -- add any
    # proposed new fields first, exactly what a real intake run would do.
    proposed_entries = [d.proposed_field_entry for d in compiled if d.proposed_field_entry]
    working_catalog = FieldCatalog(
        catalog_id=catalog.catalog_id, version=catalog.version,
        entries=catalog.entries + proposed_entries,
    )
    candidate_ruleset = Ruleset(
        ruleset_id="run-001-5loan-scope-candidate", version=1,
        checks=[d.check for d in compiled],
    )
    try:
        validate_referential_integrity(candidate_ruleset, working_catalog)
        integrity_ok = True
        integrity_error = None
    except ReferentialIntegrityError as e:
        integrity_ok = False
        integrity_error = str(e)

    total_input = sum(c["inputTokens"] for c in tracked_client.calls)
    total_output = sum(c["outputTokens"] for c in tracked_client.calls)
    real_cost = (total_input / 1000 * PRICE_PER_1K_INPUT) + (total_output / 1000 * PRICE_PER_1K_OUTPUT)
    cost_per_row = real_cost / len(rows) if rows else 0.0

    FULL_SCOPE = 5365
    ALREADY_HAVE = len(rows)  # this run's own rows count toward the full scope
    remaining = FULL_SCOPE - ALREADY_HAVE
    extrapolated_remaining_cost = cost_per_row * remaining
    extrapolated_full_cost = cost_per_row * FULL_SCOPE

    grounded = [d for d in compiled if d.grounding is not None]

    return {
        "rows_attempted": len(rows),
        "compiled_ok": len(compiled),
        "parse_failures": len(failed),
        "failure_row_ids": [d.row_id for d in failed],
        "failure_reasons": [d.parse_error for d in failed],
        "grounded_count": len(grounded),
        "grounded_row_ids": [d.row_id for d in grounded],
        "referential_integrity": "PASSED" if integrity_ok else f"BLOCKED: {integrity_error}",
        "proposed_new_fields": len(proposed_entries),
        "real_cost": {
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "real_usd_this_run": round(real_cost, 4),
            "usd_per_row": round(cost_per_row, 5),
        },
        "extrapolation_to_full_5365_scope": {
            "rows_already_compiled_this_run": ALREADY_HAVE,
            "rows_remaining": remaining,
            "estimated_usd_for_remaining_rows": round(extrapolated_remaining_cost, 2),
            "estimated_usd_for_full_5365_scope": round(extrapolated_full_cost, 2),
        },
        "drafts": [
            {
                "row_id": d.row_id,
                "check_id": d.check.id if d.check else None,
                "check_name": d.check.name if d.check else None,
                "kind": d.check.kind if d.check else None,
                "parse_error": d.parse_error,
                "grounded": d.grounding is not None,
                "applicability_program": d.applicability.program if d.applicability else None,
            }
            for d in drafts
        ],
    }


def _write_results_md(result: Dict[str, Any], path: str) -> None:
    lines = [
        "# Compile Run 001 — 5-Loan Scope, First Real Tranche",
        "",
        "**Status: real, unsigned, referential-integrity-screened candidate "
        "checks — NOT yet SME-reviewed or signed off.** Real Bedrock calls "
        "(Sonnet 4.6, temperature=0), real cost, real per-row parse results. "
        "First bounded tranche of the real rules-parsing process, drawn from "
        "the 5,365-row scope in `output/RULE-PROGRAM-GATING-FINDINGS.md` §8.",
        "",
        "## Result",
        "",
        f"- Rows attempted: {result['rows_attempted']}",
        f"- Compiled successfully: {result['compiled_ok']}",
        f"- Parse failures: {result['parse_failures']} "
        f"({', '.join(result['failure_row_ids']) if result['failure_row_ids'] else 'none'})",
        f"- Grounded (had a signed KB to retrieve from — FHA only, from 002c): "
        f"{result['grounded_count']} ({', '.join(result['grounded_row_ids']) if result['grounded_row_ids'] else 'none'})",
        f"- Referential integrity: **{result['referential_integrity']}**",
        f"- New fields proposed: {result['proposed_new_fields']}",
        "",
        "## Real cost (measured, not estimated)",
        "",
        f"- Total input tokens: {result['real_cost']['total_input_tokens']:,}",
        f"- Total output tokens: {result['real_cost']['total_output_tokens']:,}",
        f"- Real spend this run: **${result['real_cost']['real_usd_this_run']}**",
        f"- Real cost per row: **${result['real_cost']['usd_per_row']}**",
        "",
        "## Extrapolation to the full 5,365-row §8 scope",
        "",
        f"- Rows compiled so far: {result['extrapolation_to_full_5365_scope']['rows_already_compiled_this_run']}",
        f"- Rows remaining: {result['extrapolation_to_full_5365_scope']['rows_remaining']}",
        f"- Estimated cost for the remaining rows: "
        f"**${result['extrapolation_to_full_5365_scope']['estimated_usd_for_remaining_rows']}**",
        f"- Estimated cost for the full 5,365-row scope: "
        f"**${result['extrapolation_to_full_5365_scope']['estimated_usd_for_full_5365_scope']}**",
        "",
        "This is a linear extrapolation off this run's real average — actual "
        "full-scope cost will vary with row length/complexity, but this is "
        "real measured data, not the earlier full-extraction-payload estimate "
        "from `THESIS.md` (which measured a different thing — running the QC "
        "engine over loan files, not compiling rule rows).",
        "",
        "## Compiled checks (this tranche)",
        "",
    ]
    for d in result["drafts"]:
        if d["check_id"]:
            g = " [grounded]" if d["grounded"] else ""
            lines.append(f"- `{d['check_id']}` ({d['kind']}, program={d['applicability_program']}){g}")
        else:
            lines.append(f"- {d['row_id']}: PARSE FAILED — {d['parse_error']}")
    lines.append("")
    lines.append("## Next step")
    lines.append("")
    lines.append(
        "This tranche is unsigned. Before it (or the remaining "
        f"{result['extrapolation_to_full_5365_scope']['rows_remaining']} rows) can run against real "
        "loans, an SME needs to review and sign off per the existing `002b`/`002c` provenance "
        "mechanism (`RuleProvenance`, `assemble_ruleset`) — not done by this script."
    )
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main() -> None:
    result = run()
    print(json.dumps(
        {k: v for k, v in result.items() if k != "drafts"}, indent=2,
    ))
    results_path = os.path.join(HERE, "RESULTS.md")
    _write_results_md(result, results_path)
    print(f"\n[written] {results_path}")
    drafts_path = os.path.join(HERE, "compiled_drafts.json")
    with open(drafts_path, "w") as f:
        json.dump(result["drafts"], f, indent=2)
    print(f"[written] {drafts_path}")


if __name__ == "__main__":
    main()
