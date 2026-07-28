"""
Identifies which check IDs in the existing comprehensive ruleset
(result/rules/comprehensive_ruleset.json, 8,399 checks) were derived from
PRE-FUNDING rows -- out of scope for this project (CLAUDE.md: the engine
QCs a closed, FUNDED loan file, post-closing, only). Confirmed by direct
inspection: 3,344 of the 8,442 source rows (39.6%) carry a "Questionnaire
Name" of "Pre-Funding ..." rather than "Post-Closing ...", split across
both real workbooks:
  - Private Bank Oct 2025 PC and Nov 2025 PF.xlsx / "Pre Funding Nov 2025" sheet: 8 rows
  - PF and PC Sept 2025 AMQs - Retail.xlsx / "Report 1" sheet: 3,336 rows
    (same sheet as the post-closing rows -- distinguished only by this
    column, not by a separate sheet)

This does NOT recompile the full 8,442-row scope (that already happened,
$394.30, result/rules/comprehensive_ruleset.json). It compiles ONLY the
3,344 pre-funding rows, cheaper (~$156 estimated), to answer one question:
which check IDs does this out-of-scope content produce? Relies on the
G3 bake-off finding (temp=0 Sonnet 4.6 is byte-identical across runs) --
re-compiling a row reproduces the same check.id it already produced in the
main compile, so the resulting ID set is a reliable (not guessed)
cross-reference, never a text-similarity heuristic.

Writes a NEW file (result/rules/prefunding_check_ids.json) -- the existing
comprehensive_ruleset.json / comprehensive_applicability.json are
untouched, per direct instruction.

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys
import threading
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List

import openpyxl

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
P0 = os.path.dirname(os.path.dirname(HERE))
RESULT_DIR = os.path.normpath(os.path.join(P0, "..", "result"))
sys.path.insert(0, P0)
sys.path.insert(0, os.path.join(P0, "eval_synth"))

import taxonomy as T
from qc_engine.catalog import load_catalog
from qc_engine.compiler import compile_llm as C
from qc_engine.compiler import program_gating as PG

RULES_DIR = os.path.normpath(os.path.join(P0, "..", "demo", "rules"))
CATALOG_PATH = os.path.join(P0, "qc_engine", "field_catalog.json")

MAX_WORKERS = 20
PRICE_PER_1K_INPUT = 0.003
PRICE_PER_1K_OUTPUT = 0.015


def load_prefunding_rows() -> List[Dict[str, Any]]:
    """Same row-enrichment as run_comprehensive.py's load_all_rows() (archetype,
    engine_kind, row_id, program), PLUS a stage tag from column 0
    ("Questionnaire Name") -- filtered to pre-funding rows only. Reuses
    taxonomy.py's shift-aware column mapping directly (never re-derives
    column indices ad hoc) to avoid the exact column-misalignment bug
    010a already found and fixed once in this codebase."""
    paths = [os.path.join(RULES_DIR, f) for f in os.listdir(RULES_DIR)
             if f.lower().endswith(".xlsx") and not f.startswith("~$")]
    rows: List[Dict[str, Any]] = []
    per_program_seen: Dict[str, int] = {}

    for p in paths:
        wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
        for ws in wb.worksheets:
            for row_idx, r in enumerate(ws.iter_rows(min_row=5, values_only=True)):
                if not r or len(r) <= T.COL_CATEGORY:
                    continue
                qname = r[0] if len(r) > 0 else None
                cols = (T._SHIFTED_COLS if qname == T._SHIFTED_QUESTIONNAIRE_NAME else T._STANDARD_COLS)
                exc_idx = cols["exception_code"]
                if len(r) <= exc_idx or r[exc_idx] is None:
                    continue

                qname_str = str(qname or "")
                if "Pre-Funding" not in qname_str and "Pre Funding" not in qname_str:
                    continue  # keep pre-funding rows only

                sql_idx = cols["sql_criteria"]
                sql_val = r[sql_idx] if len(r) > sql_idx else None
                row = {
                    "category": r[cols["category"]] if len(r) > cols["category"] else None,
                    "qcode": r[cols["qcode"]] if len(r) > cols["qcode"] else None,
                    "defect_text": str(r[cols["defect_text"]] or "") if len(r) > cols["defect_text"] else "",
                    "sql_criteria": str(sql_val) if sql_val is not None else "",
                    "exception_code": r[exc_idx],
                    "significance": r[cols["significance"]] if len(r) > cols["significance"] else None,
                }

                exc = row.get("exception_code") or ""
                program = PG.parse_exception_code_prefix(exc)
                program_key = program or "UNTAGGED"
                try:
                    arch_id = T.classify(row.get("defect_text", "") or "")
                    archetype = {a["id"]: a for a in T.ARCHETYPES}.get(arch_id, {})
                    engine_kind = archetype.get("engine_kind", "predicate")
                except Exception:
                    engine_kind = "predicate"

                row["engine_kind"] = engine_kind
                row["source_file"] = os.path.basename(p)
                row["source_row"] = row_idx
                row["program"] = program_key
                n = per_program_seen.get(program_key, 0)
                row["row_id"] = f"PF-{program_key.replace(' ', '')}-{n:05d}"
                per_program_seen[program_key] = n + 1
                rows.append(row)
        wb.close()
    return rows


def _bedrock_client():
    import boto3
    from botocore.config import Config
    cfg = Config(
        max_pool_connections=MAX_WORKERS + 5,
        retries={"max_attempts": 5, "mode": "adaptive"},
        connect_timeout=15,
        read_timeout=60,
    )
    session = boto3.Session(profile_name=C.PROFILE, region_name=C.REGION)
    return session.client("bedrock-runtime", config=cfg)


class _Progress:
    def __init__(self, total: int):
        self.total = total
        self.lock = threading.Lock()
        self.completed = 0
        self.failed = 0
        self.tokens_in = 0
        self.tokens_out = 0
        self.check_ids: set = set()

    def record(self, draft, tokens_in, tokens_out):
        with self.lock:
            self.completed += 1
            self.tokens_in += tokens_in
            self.tokens_out += tokens_out
            if draft is not None and draft.check is not None:
                self.check_ids.add(draft.check.id)
            else:
                self.failed += 1
            if self.completed % 25 == 0 or self.completed == self.total:
                cost = (self.tokens_in / 1000 * PRICE_PER_1K_INPUT) + (self.tokens_out / 1000 * PRICE_PER_1K_OUTPUT)
                print(f"  [{self.completed}/{self.total}] unique_ids_so_far={len(self.check_ids)} "
                      f"failed={self.failed} cost=${cost:.2f}", flush=True)


def _compile_one(client, row, catalog, progress: "_Progress"):
    usage = {"inputTokens": 0, "outputTokens": 0}

    class _TrackedClient:
        def converse(self, **kwargs):
            resp = client.converse(**kwargs)
            u = resp.get("usage", {})
            usage["inputTokens"] += u.get("inputTokens", 0)
            usage["outputTokens"] += u.get("outputTokens", 0)
            return resp

    tracked = _TrackedClient()
    try:
        draft = C.compile_row(tracked, row, catalog)
        progress.record(draft, usage["inputTokens"], usage["outputTokens"])
    except Exception as e:
        print(f"  [error] row_id={row.get('row_id')}: {type(e).__name__}: {e}", flush=True)
        progress.record(None, usage["inputTokens"], usage["outputTokens"])


def main() -> None:
    import time
    t0 = time.time()

    rows = load_prefunding_rows()
    print(f"Loaded {len(rows)} pre-funding rows (expect 3,344).\n", flush=True)

    catalog = load_catalog(CATALOG_PATH)
    client = _bedrock_client()
    progress = _Progress(total=len(rows))

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = [pool.submit(_compile_one, client, row, catalog, progress) for row in rows]
        for f in as_completed(futures):
            f.result()

    elapsed = time.time() - t0
    total_cost = (progress.tokens_in / 1000 * PRICE_PER_1K_INPUT) + (progress.tokens_out / 1000 * PRICE_PER_1K_OUTPUT)

    # Cross-reference against the EXISTING comprehensive ruleset: which of
    # these pre-funding-derived IDs also appear in the main ruleset (i.e.
    # need excluding from post-closing QC runs).
    main_ruleset = json.load(open(os.path.join(RESULT_DIR, "rules", "comprehensive_ruleset.json")))
    main_ids = set(c["id"] for c in main_ruleset["content"]["checks"])
    overlap = progress.check_ids & main_ids
    prefunding_only_not_in_main = progress.check_ids - main_ids

    out = {
        "generated": "2026-07-23",
        "purpose": "Check IDs to EXCLUDE from post-closing QC runs -- derived from pre-funding-only source rows.",
        "method": "Re-compiled ONLY the 3,344 pre-funding rows (not the full 8,442) -- relies on confirmed "
                  "temp=0 determinism (G3 bake-off) so re-running a row reproduces the same check.id already "
                  "in the main ruleset, not a text-similarity guess.",
        "source_rows_compiled": len(rows),
        "failed_to_compile": progress.failed,
        "unique_check_ids_from_prefunding_rows": len(progress.check_ids),
        "of_those_also_present_in_main_comprehensive_ruleset": len(overlap),
        "of_those_NOT_found_in_main_ruleset": len(prefunding_only_not_in_main),
        "real_cost": round(total_cost, 2),
        "elapsed_minutes": round(elapsed / 60, 1),
        "exclude_from_qc_runs": sorted(overlap),
        "prefunding_ids_not_matched_in_main_ruleset": sorted(prefunding_only_not_in_main),
    }

    out_path_local = os.path.join(HERE, "prefunding_check_ids.json")
    with open(out_path_local, "w") as f:
        json.dump(out, f, indent=2)

    out_path_store = os.path.join(RESULT_DIR, "rules", "prefunding_check_ids.json")
    with open(out_path_store, "w") as f:
        json.dump(out, f, indent=2)

    print(f"\nUnique check IDs from pre-funding rows: {len(progress.check_ids)}", flush=True)
    print(f"  Also present in main ruleset (exclude these): {len(overlap)}", flush=True)
    print(f"  Not matched in main ruleset (unexpected, worth a look): {len(prefunding_only_not_in_main)}", flush=True)
    print(f"Real cost: ${total_cost:.2f}  |  Elapsed: {elapsed/60:.1f} min", flush=True)
    print(f"\n[written] {out_path_local}", flush=True)
    print(f"[written] {out_path_store} (NEW file -- comprehensive_ruleset.json untouched)", flush=True)


if __name__ == "__main__":
    main()
