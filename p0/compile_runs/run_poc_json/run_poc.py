"""
POC: Compile 100 rows to JSON, validate the format and executor flow.

Fast path to validate the full pipeline (compile → JSON → executor → dispositions)
before committing to 11 hours for full 5,365-row run.

Usage: python3 run_poc.py
Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys
import warnings
from typing import Any, Dict, List
from datetime import datetime

warnings.filterwarnings("ignore")

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
LIMIT = 100  # POC: first 100 rows only


def load_scoped_rows(limit: int) -> List[Dict[str, Any]]:
    """Load up to `limit` rows from the scope."""
    paths = [os.path.join(RULES_DIR, f) for f in os.listdir(RULES_DIR)
             if f.lower().endswith(".xlsx") and not f.startswith("~$")]
    rows = []
    for p in paths:
        for row_idx, row in enumerate(T.load_rows(p)):
            if len(rows) >= limit:
                break
            program = PG.parse_exception_code_prefix(row.get("exception_code") or "")
            if program not in NEEDED_PROGRAMS:
                continue
            try:
                arch_id = T.classify(row.get("defect_text", "") or "")
                archetype = {a["id"]: a for a in T.ARCHETYPES}.get(arch_id, {})
                engine_kind = archetype.get("engine_kind", "predicate")
            except:
                engine_kind = "predicate"

            row_dict = dict(row)
            row_dict["engine_kind"] = engine_kind
            row_dict["source_file"] = os.path.basename(p)
            row_dict["source_row"] = row_idx
            row_dict["program"] = program
            row_dict["row_id"] = f"{program.replace(' ', '')}-{len([r for r in rows if r['program'] == program]):04d}"
            rows.append(row_dict)
        if len(rows) >= limit:
            break
    return rows


def main():
    print(f"\n=== POC: Compile {LIMIT} rows to JSON ===\n")

    print(f"Loading {LIMIT} rows...", flush=True)
    all_rows = load_scoped_rows(LIMIT)
    print(f"✓ Loaded {len(all_rows)} rows", flush=True)

    print(f"Loading catalog...", flush=True)
    catalog = load_catalog(CATALOG_PATH)
    print(f"✓ Catalog: {len(catalog.entries)} fields", flush=True)

    print(f"Creating Bedrock client...", flush=True)
    client = C._client()
    print(f"✓ Client ready\n", flush=True)

    print(f"Compiling {len(all_rows)} rows with Bedrock...")
    json_rules = []
    total_cost = 0.0
    total_tokens_in = 0
    total_tokens_out = 0

    for idx, row in enumerate(all_rows):
        exc_code = row.get("exception_code", "N/A")
        print(f"  [{idx+1:3d}/{len(all_rows)}] {exc_code}...", end="", flush=True)

        # Track tokens for cost
        class CostTracker:
            def __init__(self):
                self.calls = []
            def converse(self, **kwargs):
                resp = client.converse(**kwargs)
                usage = resp.get("usage", {})
                self.calls.append(usage)
                return resp

        tracker = CostTracker()

        try:
            draft = C.compile_row(tracker, row, catalog)

            if draft.check:
                # Convert to JSON
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

                # Track cost
                for call in tracker.calls:
                    total_tokens_in += call.get("inputTokens", 0)
                    total_tokens_out += call.get("outputTokens", 0)

                cost = (total_tokens_in / 1000 * 0.003) + (total_tokens_out / 1000 * 0.015)
                print(f" ✓ (cost so far: ${cost:.2f})", flush=True)
            else:
                print(f" ✗ (parse error)", flush=True)

        except Exception as e:
            print(f" ✗ {type(e).__name__}", flush=True)

    # Write results
    total_cost = (total_tokens_in / 1000 * 0.003) + (total_tokens_out / 1000 * 0.015)

    print(f"\n=== RESULTS ===")
    print(f"Rows compiled: {len(json_rules)}/{len(all_rows)}")
    print(f"Total cost: ${total_cost:.2f}")
    print(f"Tokens: {total_tokens_in} input, {total_tokens_out} output")

    # Save JSON
    rules_file = os.path.join(HERE, "rules_poc.json")
    with open(rules_file, "w") as f:
        json.dump(json_rules, f, indent=2)

    file_size_mb = os.path.getsize(rules_file) / 1024 / 1024
    print(f"✓ Saved: {rules_file} ({file_size_mb:.1f} MB)")

    # Show sample
    if json_rules:
        print(f"\n=== SAMPLE RULE ===")
        sample = json_rules[0]
        print(json.dumps(sample, indent=2))


if __name__ == "__main__":
    main()
