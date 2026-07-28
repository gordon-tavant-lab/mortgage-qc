"""
Chunked 5,365-row compile: breaks into 500-row chunks to avoid AWS credential
expiration mid-run. Each chunk is independent; chunks are compiled sequentially.

Real Bedrock calls (Sonnet 4.6, temperature=0). Same cost as run_002 but more
resilient to credential/timeout issues.

Usage (from p0/, with AWS credentials):
    python3 compile_runs/run_003_chunked_5loan_scope/run_chunked.py
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
CHUNK_SIZE = 500  # compile 500 rows per chunk to stay within credential window
BATCH_SIZE = 50   # 50 rows per batch within each chunk

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


def compile_chunk(chunk_num: int, rows: List[Dict[str, Any]], catalog: FieldCatalog) -> Dict[str, Any]:
    """Compile one chunk of rows."""
    real_client = C._client()
    all_drafts = []
    all_costs = []

    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i:i+BATCH_SIZE]
        tracked_client = _CostTrackingClient(real_client)
        batch_drafts = [C.compile_row(tracked_client, row, catalog) for row in batch]
        all_drafts.extend(batch_drafts)

        batch_input = sum(c["inputTokens"] for c in tracked_client.calls)
        batch_output = sum(c["outputTokens"] for c in tracked_client.calls)
        batch_cost = (batch_input / 1000 * PRICE_PER_1K_INPUT) + (batch_output / 1000 * PRICE_PER_1K_OUTPUT)
        all_costs.append(batch_cost)

        compiled_ok = sum(1 for d in batch_drafts if d.check is not None)
        failed = sum(1 for d in batch_drafts if d.check is None)

        print(f"  Chunk {chunk_num}, Batch {i//BATCH_SIZE + 1}/{(len(rows)-1)//BATCH_SIZE + 1}: "
              f"{len(batch)} rows, {compiled_ok} compiled, cost ${batch_cost:.4f}")

    compiled = [d for d in all_drafts if d.check is not None]
    failed = [d for d in all_drafts if d.check is None]
    total_input = sum(sum(c.get("inputTokens", 0) for c in tracked_client.calls)
                      for tracked_client in [_CostTrackingClient(C._client())])  # dummy
    total_output = sum(sum(c.get("outputTokens", 0) for c in tracked_client.calls)
                       for tracked_client in [_CostTrackingClient(C._client())])

    # Re-compute from all_costs
    total_cost = sum(all_costs)

    grounded = [d for d in compiled if d.grounding is not None]

    program_dist = {}
    for d in compiled:
        prog = d.applicability.program if d.applicability else "unknown"
        program_dist[prog] = program_dist.get(prog, 0) + 1

    return {
        "chunk_num": chunk_num,
        "rows_in_chunk": len(rows),
        "compiled_ok": len(compiled),
        "parse_failures": len(failed),
        "grounded_count": len(grounded),
        "drafts": compiled,
        "proposed_field_entries": [d.proposed_field_entry for d in compiled if d.proposed_field_entry],
        "program_distribution": program_dist,
        "chunk_cost": round(total_cost, 2),
    }


def run() -> Dict[str, Any]:
    """Compile all 5,365 rows in chunks."""
    all_rows = load_all_scoped_rows()
    print(f"\nLoaded {len(all_rows)} rows from scope.")
    print(f"Compiling in chunks of {CHUNK_SIZE} (batches of {BATCH_SIZE} within each chunk).\n")

    catalog = load_catalog(CATALOG_PATH)
    all_chunk_results = []
    all_drafts = []
    total_cost = 0.0

    for chunk_start in range(0, len(all_rows), CHUNK_SIZE):
        chunk_num = chunk_start // CHUNK_SIZE + 1
        chunk_end = min(chunk_start + CHUNK_SIZE, len(all_rows))
        chunk = all_rows[chunk_start:chunk_end]

        print(f"Chunk {chunk_num}: rows {chunk_start+1}–{chunk_end} ({len(chunk)} rows)...")
        try:
            chunk_result = compile_chunk(chunk_num, chunk, catalog)
            all_chunk_results.append(chunk_result)
            all_drafts.extend(chunk_result["drafts"])
            total_cost += chunk_result["chunk_cost"]
            print(f"  ✓ Chunk {chunk_num} complete: {chunk_result['compiled_ok']}/{len(chunk)} compiled, "
                  f"cost ${chunk_result['chunk_cost']}\n")
        except Exception as e:
            print(f"  ✗ Chunk {chunk_num} FAILED: {e}\n")
            return {
                "error": str(e),
                "error_at_chunk": chunk_num,
                "chunks_completed": len(all_chunk_results),
                "partial_cost": round(total_cost, 2),
            }

    # Aggregate and validate
    compiled = all_drafts
    all_proposed = [d.proposed_field_entry for d in compiled if d.proposed_field_entry]

    # Deduplicate: remove proposed entries that already exist in base catalog or duplicated across proposals
    base_field_names = {e.field_name for e in catalog.entries}
    seen_proposed = set()
    proposed_entries = []
    for entry in all_proposed:
        if entry.field_name not in base_field_names and entry.field_name not in seen_proposed:
            proposed_entries.append(entry)
            seen_proposed.add(entry.field_name)

    working_catalog = FieldCatalog(
        catalog_id=catalog.catalog_id, version=catalog.version,
        entries=catalog.entries + proposed_entries,
    )
    candidate_ruleset = Ruleset(
        ruleset_id="run-003-chunked-5loan-scope-candidate", version=1,
        checks=[d.check for d in compiled],
    )
    try:
        validate_referential_integrity(candidate_ruleset, working_catalog)
        integrity_ok = True
        integrity_error = None
    except ReferentialIntegrityError as e:
        integrity_ok = False
        integrity_error = str(e)

    program_dist = {}
    for d in compiled:
        prog = d.applicability.program if d.applicability else "unknown"
        program_dist[prog] = program_dist.get(prog, 0) + 1

    return {
        "total_rows": len(all_rows),
        "compiled_ok": len(compiled),
        "parse_failures": sum(r["parse_failures"] for r in all_chunk_results),
        "grounded_count": sum(r["grounded_count"] for r in all_chunk_results),
        "referential_integrity": "PASSED" if integrity_ok else f"BLOCKED: {integrity_error}",
        "proposed_new_fields": len(proposed_entries),
        "chunks_completed": len(all_chunk_results),
        "real_cost": round(total_cost, 2),
        "program_distribution": program_dist,
        "chunk_results": all_chunk_results,
    }


def _write_results_md(result: Dict[str, Any], path: str) -> None:
    lines = [
        "# Compile Run 003 — Full 5-Loan Scope (Chunked)",
        "",
        "**Status: real, unsigned, referential-integrity-screened candidate "
        "checks covering the entire 5,365-row scope.** Compiled in chunks of 500 rows "
        "to avoid AWS credential expiration during the ~40-minute run. Real Bedrock calls "
        "(Sonnet 4.6, temperature=0), real measured cost.",
        "",
        "## Result",
        "",
        f"- Total rows in scope: {result['total_rows']}",
        f"- Compiled successfully: {result['compiled_ok']}",
        f"- Parse failures: {result['parse_failures']}",
        f"- Grounded (had signed KB): {result['grounded_count']}",
        f"- Referential integrity: **{result['referential_integrity']}**",
        f"- New fields proposed: {result['proposed_new_fields']}",
        f"- Chunks completed: {result['chunks_completed']}",
        "",
        "## Real cost (measured across all chunks)",
        "",
        f"- Real spend: **${result['real_cost']}**",
        f"- Cost per row: ${result['real_cost'] / result['total_rows']:.5f}",
        "",
        "## Chunk summary",
        "",
    ]
    if "chunk_results" in result:
        for r in result["chunk_results"]:
            lines.append(f"- Chunk {r['chunk_num']}: {r['rows_in_chunk']} rows → {r['compiled_ok']} compiled, cost ${r['chunk_cost']}")
    lines += [
        "",
        "## Compiled by program",
        "",
    ]
    for prog, count in sorted(result.get("program_distribution", {}).items()):
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
    if "error" in result:
        print(f"\n[ERROR] {result['error']}")
        print(f"Chunks completed: {result['chunks_completed']}, partial cost: ${result['partial_cost']}")
    else:
        print(json.dumps({k: v for k, v in result.items() if k != "chunk_results"}, indent=2))
        results_path = os.path.join(HERE, "RESULTS.md")
        _write_results_md(result, results_path)
        print(f"\n[written] {results_path}")


if __name__ == "__main__":
    main()
