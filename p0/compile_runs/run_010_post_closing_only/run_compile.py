"""
Compile ONLY the 5,098 confirmed POST-CLOSING rows from demo/rules (excluding
the 3,344 confirmed pre-funding rows) into a NEW, standalone ruleset.

This supersedes run_009's approach (compile everything, then guess which
already-compiled check IDs to exclude by cross-referencing a separately
pre-funding-only compile). That approach had a real bug: a check ID
producible from a pre-funding row was excluded even when the SAME real-world
condition is *also* asked on a post-closing row -- since IDs are
content-deterministic, "this ID showed up when I compiled pre-funding rows"
does NOT mean "this check is exclusively pre-funding." Confirmed concretely:
`title-vesting-1003-vs-commitment` and `employment-dates-1003-vs-docs-agree`
are both legitimate, real client rules (compiled correctly from demo/rules),
both landed in `prefunding_check_ids.json`'s exclude list, and both would
have been wrongly dropped from every QC run.

Compiling the true post-closing-only row set directly avoids this class of
bug entirely -- no set-subtraction heuristic, no reliance on "also appeared
elsewhere" logic. Whatever comes out of THIS compile is definitionally
post-closing, full stop.

Also carries two compiler fixes made just before this run (compile_llm.py's
SYSTEM_PROMPT), found while investigating why a specific row's threshold
came back UNSPECIFIED despite stating "less than 2 yrs" in its own text:
  1. `ratio` now has three legal values (ltv | dti | field_value) instead of
     being force-fit into ltv/dti for every ratio_threshold check -- fixes a
     silent wrong-computation bug that affected 267 unique checks in the
     prior (run_008) comprehensive compile.
  2. The UNSPECIFIED-threshold guard no longer treats an informally-worded
     but explicit number ("less than 2 yrs", "within 30 days") as
     insufficiently stated -- only a genuinely absent number now yields
     UNSPECIFIED. 74 of 286 UNSPECIFIED checks in run_008 had a literal
     number sitting in their own generated message text; this was an
     internal-consistency bug in the compiler's output, not real ambiguity
     in the source rows.

NEW this run (vs run_008/run_009): persists row-level provenance --
row_id, source_file, sheet/questionnaire_name, exception_code, program --
into a companion file (post_closing_only_provenance.json), keyed by
check_id. Never persisted before (program-applicability and pre-funding
check-ID sets both hit this same "didn't persist enough metadata" mistake
already this session) -- marginal cost is ~zero since it's already computed
during compile, and it means "which source row(s) produced this check" is
answerable by lookup going forward, not by re-investigation.

Writes ONLY new files -- comprehensive_ruleset.json / applicability.json /
prefunding_check_ids.json (run_008/run_009's artifacts) are left untouched,
per explicit instruction to keep both.

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
from qc_engine.ruleset import Ruleset
from qc_engine.compiler import compile_llm as C
from qc_engine.compiler import program_gating as PG

RULES_DIR = os.path.normpath(os.path.join(P0, "..", "demo", "rules"))
CATALOG_PATH = os.path.join(P0, "qc_engine", "field_catalog.json")

MAX_WORKERS = 20
CHECKPOINT_EVERY = 250

PRICE_PER_1K_INPUT = 0.003
PRICE_PER_1K_OUTPUT = 0.015


def load_post_closing_rows() -> List[Dict[str, Any]]:
    """Every row EXCEPT confirmed pre-funding rows -- reuses taxonomy.py's
    real shift-aware column mapping directly (never re-derives column
    indices ad hoc -- 010a already found and fixed that exact bug once).
    Confirmed exact split by direct count: 5,098 post-closing / 3,344
    pre-funding / 0 unlabeled, across both real workbooks."""
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
                if "Pre-Funding" in qname_str or "Pre Funding" in qname_str:
                    continue  # exclude pre-funding rows -- the whole point of this run

                sql_idx = cols["sql_criteria"]
                sql_val = r[sql_idx] if len(r) > sql_idx else None
                row = {
                    "category": r[cols["category"]] if len(r) > cols["category"] else None,
                    "qcode": r[cols["qcode"]] if len(r) > cols["qcode"] else None,
                    "defect_text": str(r[cols["defect_text"]] or "") if len(r) > cols["defect_text"] else "",
                    "sql_criteria": str(sql_val) if sql_val is not None else "",
                    "exception_code": r[exc_idx],
                    "significance": r[cols["significance"]] if len(r) > cols["significance"] else None,
                    "questionnaire_name": qname_str,
                    "sheet_name": ws.title,
                }

                exc = row.get("exception_code") or ""
                program = PG.parse_exception_code_prefix(exc)
                program_key = program or "UNTAGGED"
                try:
                    arch_id = T.classify(row.get("defect_text", "") or "")
                    archetype = {a["id"]: a for a in T.ARCHETYPES}.get(arch_id, {})
                    engine_kind = archetype.get("engine_kind", "predicate")
                except Exception:
                    arch_id = "unknown"
                    engine_kind = "predicate"

                row["archetype_id"] = arch_id
                row["engine_kind"] = engine_kind
                row["source_file"] = os.path.basename(p)
                row["source_row"] = row_idx
                row["program"] = program_key
                n = per_program_seen.get(program_key, 0)
                row["row_id"] = f"PC-{program_key.replace(' ', '')}-{n:05d}"
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
    def __init__(self, total: int, checkpoint_path: str, applicability_path: str,
                 provenance_path: str, processed_path: str,
                 initial_checks=None, initial_applicable=None,
                 initial_provenance=None, initial_processed_ids=None):
        self.total = total
        self.checkpoint_path = checkpoint_path
        self.applicability_path = applicability_path
        self.provenance_path = provenance_path
        self.processed_path = processed_path
        self.lock = threading.Lock()
        self.completed = 0
        self.failed = 0
        self.retried = 0
        self.unspecified_count = 0
        self.tokens_in = 0
        self.tokens_out = 0
        self.checks: List[Any] = list(initial_checks or [])
        self.applicable_programs: Dict[str, set] = {
            cid: set(progs) for cid, progs in (initial_applicable or {}).items()
        }
        # check_id -> list of {row_id, source_file, sheet_name, source_row,
        # exception_code, program} -- every source row that produced this
        # check ID (a check can come from more than one row -- the same
        # real-world condition restated per program sheet).
        self.provenance: Dict[str, List[Dict[str, Any]]] = dict(initial_provenance or {})
        self.processed_row_ids = set(initial_processed_ids or [])
        self.permanently_failed_row_ids: List[str] = []

    def record(self, row, draft, tokens_in, tokens_out):
        with self.lock:
            self.completed += 1
            self.tokens_in += tokens_in
            self.tokens_out += tokens_out
            self.processed_row_ids.add(row["row_id"])
            if draft is not None and draft.check is not None:
                self.checks.append(draft.check)
                program = None
                if draft.applicability is not None:
                    program = draft.applicability.program
                program_key = program or "UNTAGGED"
                self.applicable_programs.setdefault(draft.check.id, set()).add(program_key)
                self.provenance.setdefault(draft.check.id, []).append({
                    "row_id": row["row_id"],
                    "source_file": row["source_file"],
                    "sheet_name": row["sheet_name"],
                    "source_row": row["source_row"],
                    "exception_code": row.get("exception_code"),
                    "program": program_key,
                })
                if "UNSPECIFIED" in (draft.check.threshold or "") or "UNSPECIFIED" in (draft.check.tolerance or ""):
                    self.unspecified_count += 1
            else:
                self.failed += 1

            if self.completed % 25 == 0 or self.completed == self.total:
                cost = (self.tokens_in / 1000 * PRICE_PER_1K_INPUT) + (self.tokens_out / 1000 * PRICE_PER_1K_OUTPUT)
                print(f"  [{len(self.processed_row_ids)}/{self.total} total processed] "
                      f"compiled={len(self.checks)} unique_ids={len(self.provenance)} "
                      f"failed={self.failed} unspecified={self.unspecified_count} cost=${cost:.2f}", flush=True)

            if self.completed % CHECKPOINT_EVERY == 0 or self.completed == self.total:
                self._write_checkpoint()

    def _write_checkpoint(self):
        ruleset = Ruleset(ruleset_id="rs-post-closing-only", version=1, checks=list(self.checks))
        with open(self.checkpoint_path, "w") as f:
            f.write(ruleset.to_json())
        with open(self.applicability_path, "w") as f:
            json.dump({cid: sorted(progs) for cid, progs in self.applicable_programs.items()}, f, indent=2)
        with open(self.provenance_path, "w") as f:
            json.dump(self.provenance, f, indent=2)
        with open(self.processed_path, "w") as f:
            json.dump(sorted(self.processed_row_ids), f)
        print(f"  [checkpoint] {len(self.checks)} checks + applicability + provenance + "
              f"{len(self.processed_row_ids)} processed row_ids written", flush=True)


def _compile_one(client, row, catalog, progress: "_Progress", is_retry=False):
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
        if draft.check is None and not is_retry:
            # one retry before counting as a real failure
            draft = C.compile_row(tracked, row, catalog)
            with progress.lock:
                progress.retried += 1
        progress.record(row, draft, usage["inputTokens"], usage["outputTokens"])
        if draft.check is None:
            with progress.lock:
                progress.permanently_failed_row_ids.append(row["row_id"])
    except Exception as e:
        print(f"  [error] row_id={row.get('row_id')}: {type(e).__name__}: {e}", flush=True)
        progress.record(row, None, usage["inputTokens"], usage["outputTokens"])
        with progress.lock:
            progress.permanently_failed_row_ids.append(row["row_id"])


def run(rows_override=None, resume=False) -> Dict[str, Any]:
    all_rows = rows_override if rows_override is not None else load_post_closing_rows()
    print(f"\nLoaded {len(all_rows)} post-closing rows (pre-funding excluded). Expect 5,098.", flush=True)

    checkpoint_path = os.path.join(HERE, "ruleset_checkpoint.json")
    applicability_path = os.path.join(HERE, "applicability_checkpoint.json")
    provenance_path = os.path.join(HERE, "provenance_checkpoint.json")
    processed_path = os.path.join(HERE, "processed_row_ids_checkpoint.json")

    initial_checks, initial_applicable, initial_provenance, initial_processed_ids = [], {}, {}, []
    if resume and os.path.exists(checkpoint_path) and os.path.exists(processed_path):
        prior_ruleset = Ruleset.from_dict(json.load(open(checkpoint_path)))
        initial_checks = prior_ruleset.checks
        initial_applicable = json.load(open(applicability_path)) if os.path.exists(applicability_path) else {}
        initial_provenance = json.load(open(provenance_path)) if os.path.exists(provenance_path) else {}
        initial_processed_ids = json.load(open(processed_path))
        print(f"[resume] Loaded prior checkpoint: {len(initial_checks)} checks, "
              f"{len(initial_processed_ids)} already-processed row_ids -- these will be skipped.", flush=True)
        remaining_rows = [r for r in all_rows if r["row_id"] not in set(initial_processed_ids)]
        all_rows = remaining_rows
        print(f"[resume] {len(all_rows)} rows remaining.\n", flush=True)
    else:
        print(f"Compiling with {MAX_WORKERS} parallel workers.\n", flush=True)

    catalog = load_catalog(CATALOG_PATH)
    client = _bedrock_client()

    progress = _Progress(
        total=len(initial_processed_ids) + len(all_rows),
        checkpoint_path=checkpoint_path, applicability_path=applicability_path,
        provenance_path=provenance_path, processed_path=processed_path,
        initial_checks=initial_checks, initial_applicable=initial_applicable,
        initial_provenance=initial_provenance, initial_processed_ids=initial_processed_ids,
    )

    if all_rows:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = [pool.submit(_compile_one, client, row, catalog, progress) for row in all_rows]
            for f in as_completed(futures):
                f.result()
        progress._write_checkpoint()

    total_cost = (progress.tokens_in / 1000 * PRICE_PER_1K_INPUT) + (progress.tokens_out / 1000 * PRICE_PER_1K_OUTPUT)
    return {
        "total_rows": progress.total,
        "checks_compiled": len(progress.checks),
        "unique_check_ids": len(progress.provenance),
        "failed_after_retry": progress.failed,
        "retried_count": progress.retried,
        "permanently_failed_row_ids": progress.permanently_failed_row_ids,
        "unspecified_thresholds": progress.unspecified_count,
        "real_cost_this_run": round(total_cost, 2),
        "checks": progress.checks,
        "applicable_programs": {cid: sorted(progs) for cid, progs in progress.applicable_programs.items()},
        "provenance": progress.provenance,
    }


def main() -> None:
    import time
    t0 = time.time()
    result = run(resume=True)
    elapsed = time.time() - t0

    print(json.dumps({k: v for k, v in result.items() if k not in ("checks", "provenance")}, indent=2), flush=True)
    print(f"\nElapsed: {elapsed/60:.1f} min", flush=True)

    ruleset = Ruleset(ruleset_id="rs-post-closing-only", version=1, checks=result["checks"])

    # Local copies (this run's own directory)
    ruleset_path = os.path.join(HERE, "ruleset.json")
    with open(ruleset_path, "w") as f:
        f.write(ruleset.to_json())
    applicability_path = os.path.join(HERE, "applicability.json")
    with open(applicability_path, "w") as f:
        json.dump(result["applicable_programs"], f, indent=2)
    provenance_path = os.path.join(HERE, "provenance.json")
    with open(provenance_path, "w") as f:
        json.dump(result["provenance"], f, indent=2)

    # NEW files in the central store -- comprehensive_ruleset.json /
    # applicability.json / prefunding_check_ids.json (run_008/009) untouched.
    store_ruleset_path = os.path.join(RESULT_DIR, "rules", "post_closing_only_ruleset.json")
    with open(store_ruleset_path, "w") as f:
        f.write(ruleset.to_json())
    store_applicability_path = os.path.join(RESULT_DIR, "rules", "post_closing_only_applicability.json")
    with open(store_applicability_path, "w") as f:
        json.dump(result["applicable_programs"], f, indent=2)
    store_provenance_path = os.path.join(RESULT_DIR, "rules", "post_closing_only_provenance.json")
    with open(store_provenance_path, "w") as f:
        json.dump(result["provenance"], f, indent=2)

    print(f"\n[written] {store_ruleset_path} ({result['checks_compiled']} checks, "
          f"{result['unique_check_ids']} unique IDs, {os.path.getsize(store_ruleset_path) / 1024 / 1024:.1f} MB)", flush=True)
    print(f"[written] {store_applicability_path}", flush=True)
    print(f"[written] {store_provenance_path} (row-level traceability -- NEW, never persisted before)", flush=True)
    if result["permanently_failed_row_ids"]:
        print(f"\n[warning] {len(result['permanently_failed_row_ids'])} rows failed to compile "
              f"even after retry: {result['permanently_failed_row_ids']}", flush=True)
    else:
        print(f"\n[clean] 0 rows failed to compile (after up to 1 retry each).", flush=True)


if __name__ == "__main__":
    main()
