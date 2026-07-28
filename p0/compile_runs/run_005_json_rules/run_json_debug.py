"""Debug version with explicit progress tracking."""
from __future__ import annotations
import json, os, sys, warnings, time
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
            except:
                engine_kind = "predicate"

            row_dict = dict(row)
            row_dict["engine_kind"] = engine_kind
            row_dict["source_file"] = os.path.basename(p)
            row_dict["source_row"] = row_idx
            row_dict["program"] = program
            row_dict["row_id"] = f"{program.replace(' ', '')}-{len([r for r in rows if r['program'] == program]):04d}"
            rows.append(row_dict)
    return rows

def main():
    print(f"[{time.time():.1f}s] Loading rows...", flush=True)
    all_rows = load_all_scoped_rows()
    print(f"[{time.time():.1f}s] Loaded {len(all_rows)} rows", flush=True)

    print(f"[{time.time():.1f}s] Loading catalog...", flush=True)
    catalog = load_catalog(CATALOG_PATH)
    print(f"[{time.time():.1f}s] Catalog loaded: {len(catalog.entries)} fields", flush=True)

    print(f"[{time.time():.1f}s] Creating Bedrock client...", flush=True)
    client = C._client()
    print(f"[{time.time():.1f}s] Client created", flush=True)

    # Test first 3 rows
    print(f"\n[{time.time():.1f}s] Testing first 3 rows...", flush=True)
    for i in range(min(3, len(all_rows))):
        row = all_rows[i]
        exc_code = row.get("exception_code", "N/A")
        print(f"[{time.time():.1f}s]   Row {i+1}: {exc_code}...", end="", flush=True)

        try:
            print(f" [calling compile_row]", end="", flush=True)
            draft = C.compile_row(client, row, catalog)
            result = "✓" if draft.check else "✗"
            print(f" {result}", flush=True)
        except Exception as e:
            print(f" ✗ {type(e).__name__}: {str(e)[:40]}", flush=True)

    print(f"\n[{time.time():.1f}s] Test complete", flush=True)

if __name__ == "__main__":
    main()
