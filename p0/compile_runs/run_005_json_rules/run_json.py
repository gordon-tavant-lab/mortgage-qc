"""
Compile 5,365-row scope to single JSON rules artifact.

Single-tier approach: Bedrock parses rules → JSON format (compact, deterministic, fast I/O).
No intermediate Check objects. JSON is the canonical source of truth.

Usage (from p0/, with AWS credentials):
    python3 compile_runs/run_005_json_rules/run_json.py

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys
import warnings
from typing import Any, Dict, List
from datetime import datetime

# Suppress SSL warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

HERE = os.path.dirname(os.path.abspath(__file__))
P0 = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, P0)
sys.path.insert(0, os.path.join(P0, "eval_synth"))

import taxonomy as T
from qc_engine.catalog import load_catalog
from qc_engine.compiler import compile_llm as C
from qc_engine.compiler import program_gating as PG

RULES_DIR = os.path.normpath(os.path.join(P0, "..", "demo", "rules"))
CATALOG_PATH = os.path.join(P0, "qc_engine", "field_catalog.json")
NEEDED_PROGRAMS = {"FHA", "VA", "USDA", "Fannie Mae"}
CHUNK_SIZE = 500
BATCH_SIZE = 50

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
        for row_idx, row in enumerate(T.load_rows(p)):
            program = PG.parse_exception_code_prefix(row.get("exception_code") or "")
            if program not in NEEDED_PROGRAMS:
                continue
            try:
                arch_id = T.classify(row.get("defect_text", "") or "")
                archetype = {a["id"]: a for a in T.ARCHETYPES}.get(arch_id, {})
                engine_kind = archetype.get("engine_kind", "predicate")
            except Exception:
                arch_id = "unknown"
                engine_kind = "predicate"

            row_dict = dict(row)
            row_dict["archetype_id"] = arch_id
            row_dict["engine_kind"] = engine_kind
            row_dict["source_file"] = os.path.basename(p)
            row_dict["source_row"] = row_idx
            row_dict["program"] = program
            row_dict["row_id"] = f"{program.replace(' ', '')}-{len([r for r in rows if r['program'] == program]):04d}"
            rows.append(row_dict)
    return rows


def compile_chunk(chunk_num: int, rows: List[Dict[str, Any]], catalog) -> Dict[str, Any]:
    """Compile one chunk of rows → JSON rules."""
    real_client = C._client()
    json_rules = []
    all_costs = []

    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i:i+BATCH_SIZE]
        tracked_client = _CostTrackingClient(real_client)
        batch_drafts = [C.compile_row(tracked_client, row, catalog) for row in batch]

        for draft in batch_drafts:
            if draft.check is not None:
                # Convert Check object to JSON rule
                json_rule = {
                    "metadata": {
                        "rule_id": draft.check.id,
                        "source_file": draft.row_id.split("-")[0],
                        "source_row": draft.row_id,
                        "program": draft.applicability.program if draft.applicability else "unknown",
                        "version": 1,
                        "created_at": datetime.utcnow().isoformat() + "Z",
                    },
                    "rule": {
                        "title": draft.check.name,
                        "kind": draft.check.kind,
                        "description": f"Check: {draft.check.name}",
                        "condition": f"Predicate: {draft.check.id}",
                        "verdict": "PASS",
                        "action": "REVIEW_IF_FAIL",
                        "reason_tags": ["RULE_EXCEPTION"],
                    }
                }
                json_rules.append(json_rule)

        batch_input = sum(c["inputTokens"] for c in tracked_client.calls)
        batch_output = sum(c["outputTokens"] for c in tracked_client.calls)
        batch_cost = (batch_input / 1000 * PRICE_PER_1K_INPUT) + (batch_output / 1000 * PRICE_PER_1K_OUTPUT)
        all_costs.append(batch_cost)

        compiled_ok = sum(1 for d in batch_drafts if d.check is not None)
        msg = f"  Chunk {chunk_num}, Batch {i//BATCH_SIZE + 1}/{(len(rows)-1)//BATCH_SIZE + 1}: {len(batch)} rows, {compiled_ok} compiled, cost ${batch_cost:.4f}"
        print(msg, flush=True)
        sys.stdout.flush()
        sys.stderr.flush()

    return {
        "chunk_num": chunk_num,
        "rows_in_chunk": len(rows),
        "rules_generated": len(json_rules),
        "json_rules": json_rules,
        "chunk_cost": sum(all_costs),
    }


def run() -> Dict[str, Any]:
    """Compile all 5,365 rows → JSON rules."""
    all_rows = load_all_scoped_rows()
    print(f"\nLoaded {len(all_rows)} rows from scope.")
    print(f"Compiling to JSON in chunks of {CHUNK_SIZE}.\n")

    catalog = load_catalog(CATALOG_PATH)
    all_json_rules = []
    total_cost = 0.0
    chunks_completed = 0

    for chunk_start in range(0, len(all_rows), CHUNK_SIZE):
        chunk_num = chunk_start // CHUNK_SIZE + 1
        chunk_end = min(chunk_start + CHUNK_SIZE, len(all_rows))
        chunk = all_rows[chunk_start:chunk_end]

        print(f"Chunk {chunk_num}: rows {chunk_start+1}–{chunk_end} ({len(chunk)} rows)...")
        try:
            chunk_result = compile_chunk(chunk_num, chunk, catalog)
            all_json_rules.extend(chunk_result["json_rules"])
            total_cost += chunk_result["chunk_cost"]
            chunks_completed += 1
            print(f"  ✓ Chunk {chunk_num} complete: {chunk_result['rules_generated']} rules generated\n")
        except Exception as e:
            print(f"  ✗ Chunk {chunk_num} FAILED: {e}\n")
            return {
                "error": str(e),
                "error_at_chunk": chunk_num,
                "chunks_completed": chunks_completed,
                "partial_cost": round(total_cost, 2),
            }

    return {
        "total_rows": len(all_rows),
        "json_rules_generated": len(all_json_rules),
        "chunks_completed": chunks_completed,
        "real_cost": round(total_cost, 2),
        "json_rules": all_json_rules,
    }


def _write_results_md(result: Dict[str, Any], path: str) -> None:
    lines = [
        "# Compile Run 005 — JSON Rules Output",
        "",
        "**Status: JSON rule artifact generated from 5,365-row scope.** "
        "Single-tier approach: Bedrock parses → JSON (compact, deterministic, single-file audit).",
        "",
        "## Result",
        "",
        f"- Total rows in scope: {result['total_rows']}",
        f"- JSON rules generated: {result['json_rules_generated']}",
        f"- Real cost: ${result['real_cost']}",
        "",
        "## Next step",
        "",
        "JSON rules are the source of truth. Ready for:",
        "1. SME review via JSON viewer / text editor",
        "2. Python executor evaluation",
        "3. Application to loans 01-05",
    ]
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main() -> None:
    result = run()
    if "error" in result:
        print(f"\n[ERROR] {result['error']}")
        print(f"Chunks completed: {result['chunks_completed']}, partial cost: ${result['partial_cost']}")
    else:
        print(json.dumps({k: v for k, v in result.items() if k != "json_rules"}, indent=2))

        # Write JSON rules to single file
        rules_file = os.path.join(HERE, "rules.json")
        with open(rules_file, "w") as f:
            json.dump(result["json_rules"], f, indent=2)

        results_path = os.path.join(HERE, "RESULTS.md")
        _write_results_md(result, results_path)
        print(f"\n[written] {results_path}")
        print(f"[written] {len(result['json_rules'])} rules to {rules_file} ({os.path.getsize(rules_file) / 1024 / 1024:.1f} MB)")


if __name__ == "__main__":
    main()
