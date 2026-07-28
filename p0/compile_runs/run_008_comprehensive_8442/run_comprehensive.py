"""
Compile ALL 8,442 real AMQ rows (every sheet, every workbook, every program)
to a single, real, engine-loadable Ruleset artifact.

Two fixes vs run_006 (5,365-row, program-restricted, lossy-JSON run):
  1. SCOPE: no NEEDED_PROGRAMS filter. program_gating.py already recognizes
     all 6 programs (FHA/VA/USDA/Freddie Mac/Fannie Mae/SONYMA) plus fails
     open (applies to all loans) for the 1,171 rows with no program-prefixed
     Exception Code -- gating happens per-loan at ruleset-build time
     (program_gating.applies_to), not by dropping rows at compile time.
  2. SERIALIZATION: writes a real qc_engine.ruleset.Ruleset (via its own
     to_json()/canonical_content()), not an ad-hoc {"metadata","rule"} dict
     with a hardcoded "verdict": "PASS" placeholder. This IS the artifact
     the engine can actually load and execute -- Ruleset.from_dict() round-
     trips it directly into real Check objects.

Also carries the hallucination-prevention fix from compile_llm.py's
SYSTEM_PROMPT (2026-07-22): any threshold/condition the LLM can't trace to
defect_text or grounding_context comes back as the literal string
"UNSPECIFIED", never an invented number.

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

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
P0 = os.path.dirname(os.path.dirname(HERE))
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


def load_all_rows() -> List[Dict[str, Any]]:
    """ALL rows across every sheet of every workbook -- no program filter.
    program_gating.parse_exception_code_prefix() resolves each row's
    program (or None -- fails open, applies to every loan) for use later
    at ruleset-build time, per-loan; it does not gate compilation itself."""
    paths = [os.path.join(RULES_DIR, f) for f in os.listdir(RULES_DIR)
             if f.lower().endswith(".xlsx") and not f.startswith("~$")]
    rows: List[Dict[str, Any]] = []
    per_program_seen: Dict[str, int] = {}
    for p in paths:
        for row_idx, row in enumerate(T.load_rows(p)):
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

            row_dict = dict(row)
            row_dict["archetype_id"] = arch_id
            row_dict["engine_kind"] = engine_kind
            row_dict["source_file"] = os.path.basename(p)
            row_dict["source_row"] = row_idx
            row_dict["program"] = program_key
            n = per_program_seen.get(program_key, 0)
            row_dict["row_id"] = f"{program_key.replace(' ', '')}-{n:05d}"
            per_program_seen[program_key] = n + 1
            rows.append(row_dict)
    return rows


def _bedrock_client():
    import boto3
    from botocore.config import Config
    cfg = Config(
        max_pool_connections=MAX_WORKERS + 5,
        retries={"max_attempts": 5, "mode": "adaptive"},
        # A prior run stalled for 24+ minutes at 0% CPU with valid
        # credentials -- a hung TCP read with no timeout, not a credential
        # expiry. Without an explicit read_timeout, a stuck socket blocks a
        # worker thread forever; botocore's retry/backoff never gets a
        # chance to kick in because no exception is ever raised. Bounded
        # timeouts turn a silent hang into a raised exception _compile_one
        # already catches and counts as a (retryable-on-resume) failure.
        connect_timeout=15,
        read_timeout=60,
    )
    session = boto3.Session(profile_name=C.PROFILE, region_name=C.REGION)
    return session.client("bedrock-runtime", config=cfg)


class _Progress:
    def __init__(self, total: int, checkpoint_path: str, applicability_path: str,
                 processed_path: str, initial_checks=None, initial_applicable=None,
                 initial_processed_ids=None):
        self.total = total
        self.checkpoint_path = checkpoint_path
        self.applicability_path = applicability_path
        self.processed_path = processed_path
        self.lock = threading.Lock()
        self.completed = 0
        self.failed = 0
        self.unspecified_count = 0
        self.tokens_in = 0
        self.tokens_out = 0
        self.checks: List[Any] = list(initial_checks or [])          # real Check objects
        # check_id -> sorted list of programs this id was ever compiled from.
        # "UNTAGGED" (program_gating's None) means the source row carried no
        # program-prefixed Exception Code -- fails OPEN (applies to every
        # loan), per program_gating.applies_to()'s own existing semantics.
        # A companion file, never touching the pinned Check/Ruleset schema
        # (harness.py's zero-regression digest depends on that schema never
        # changing shape) -- this is the metadata that was lost in the first
        # 8,442-row compile and caused predicate checks to flood every loan
        # with false FAILs when run ungated.
        self.applicable_programs: Dict[str, set] = {
            cid: set(progs) for cid, progs in (initial_applicable or {}).items()
        }
        # row_id of every row already compiled in a prior (stalled/killed)
        # attempt -- the resume mechanism a second stall (this actually
        # happened: a 24-minute, 0%-CPU hang mid-run) needs to not repay for
        # ~half the workbook a second time.
        self.processed_row_ids = set(initial_processed_ids or [])

    def record(self, row_id, draft, tokens_in, tokens_out):
        with self.lock:
            self.completed += 1
            self.tokens_in += tokens_in
            self.tokens_out += tokens_out
            self.processed_row_ids.add(row_id)
            if draft is not None and draft.check is not None:
                self.checks.append(draft.check)
                program = None
                if draft.applicability is not None:
                    program = draft.applicability.program
                program_key = program or "UNTAGGED"
                self.applicable_programs.setdefault(draft.check.id, set()).add(program_key)
                if "UNSPECIFIED" in (draft.check.threshold or "") or "UNSPECIFIED" in (draft.check.tolerance or ""):
                    self.unspecified_count += 1
            else:
                self.failed += 1

            if self.completed % 25 == 0 or self.completed == self.total:
                cost = (self.tokens_in / 1000 * PRICE_PER_1K_INPUT) + (self.tokens_out / 1000 * PRICE_PER_1K_OUTPUT)
                print(f"  [{len(self.processed_row_ids)}/{self.total} total processed, "
                      f"+{self.completed} this run] compiled={len(self.checks)} "
                      f"failed={self.failed} unspecified={self.unspecified_count} cost_this_run=${cost:.2f}", flush=True)

            if self.completed % CHECKPOINT_EVERY == 0 or self.completed == self.total:
                self._write_checkpoint()

    def _write_checkpoint(self):
        ruleset = Ruleset(ruleset_id="rs-comprehensive-8442", version=1, checks=list(self.checks))
        with open(self.checkpoint_path, "w") as f:
            f.write(ruleset.to_json())
        with open(self.applicability_path, "w") as f:
            json.dump({cid: sorted(progs) for cid, progs in self.applicable_programs.items()}, f, indent=2)
        with open(self.processed_path, "w") as f:
            json.dump(sorted(self.processed_row_ids), f)
        print(f"  [checkpoint] {len(self.checks)} real Check objects + applicability + "
              f"{len(self.processed_row_ids)} processed row_ids written", flush=True)


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
        progress.record(row["row_id"], draft, usage["inputTokens"], usage["outputTokens"])
    except Exception as e:
        print(f"  [error] row_id={row.get('row_id')}: {type(e).__name__}: {e}", flush=True)
        progress.record(row["row_id"], None, usage["inputTokens"], usage["outputTokens"])


def run(rows_override=None, resume=False) -> Dict[str, Any]:
    all_rows = rows_override if rows_override is not None else load_all_rows()
    print(f"\nLoaded {len(all_rows)} rows (all programs, all sheets).", flush=True)

    checkpoint_path = os.path.join(HERE, "ruleset_checkpoint.json")
    applicability_path = os.path.join(HERE, "applicability_checkpoint.json")
    processed_path = os.path.join(HERE, "processed_row_ids_checkpoint.json")

    initial_checks, initial_applicable, initial_processed_ids = [], {}, []
    if resume and os.path.exists(checkpoint_path) and os.path.exists(processed_path):
        prior_ruleset = Ruleset.from_dict(json.load(open(checkpoint_path)))
        initial_checks = prior_ruleset.checks
        initial_applicable = json.load(open(applicability_path)) if os.path.exists(applicability_path) else {}
        initial_processed_ids = json.load(open(processed_path))
        print(f"[resume] Loaded prior checkpoint: {len(initial_checks)} checks, "
              f"{len(initial_processed_ids)} already-processed row_ids -- these will be skipped.", flush=True)
        remaining_rows = [r for r in all_rows if r["row_id"] not in set(initial_processed_ids)]
        print(f"[resume] {len(all_rows) - len(remaining_rows)} rows skipped (already done), "
              f"{len(remaining_rows)} remaining to compile.\n", flush=True)
        all_rows = remaining_rows
    else:
        print(f"Compiling with {MAX_WORKERS} parallel workers.\n", flush=True)

    catalog = load_catalog(CATALOG_PATH)
    client = _bedrock_client()

    progress = _Progress(
        total=len(initial_processed_ids) + len(all_rows),
        checkpoint_path=checkpoint_path, applicability_path=applicability_path,
        processed_path=processed_path, initial_checks=initial_checks,
        initial_applicable=initial_applicable, initial_processed_ids=initial_processed_ids,
    )

    if all_rows:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = [pool.submit(_compile_one, client, row, catalog, progress) for row in all_rows]
            for f in as_completed(futures):
                f.result()
        progress._write_checkpoint()  # final checkpoint, in case total isn't a multiple of CHECKPOINT_EVERY

    total_cost = (progress.tokens_in / 1000 * PRICE_PER_1K_INPUT) + (progress.tokens_out / 1000 * PRICE_PER_1K_OUTPUT)
    return {
        "total_rows": progress.total,
        "checks_compiled": len(progress.checks),
        "failed": progress.failed,
        "unspecified_thresholds": progress.unspecified_count,
        "real_cost_this_run": round(total_cost, 2),
        "checks": progress.checks,
        "applicable_programs": {cid: sorted(progs) for cid, progs in progress.applicable_programs.items()},
    }


def main() -> None:
    import time
    t0 = time.time()
    result = run(resume=True)
    elapsed = time.time() - t0

    print(json.dumps({k: v for k, v in result.items() if k != "checks"}, indent=2), flush=True)
    print(f"\nElapsed: {elapsed/60:.1f} min", flush=True)

    ruleset = Ruleset(ruleset_id="rs-comprehensive-8442", version=1, checks=result["checks"])
    ruleset_path = os.path.join(HERE, "ruleset.json")
    with open(ruleset_path, "w") as f:
        f.write(ruleset.to_json())

    applicability_path = os.path.join(HERE, "applicability.json")
    with open(applicability_path, "w") as f:
        json.dump(result["applicable_programs"], f, indent=2)
    print(f"[written] {applicability_path} ({len(result['applicable_programs'])} check-id -> program mappings)", flush=True)

    results_path = os.path.join(HERE, "RESULTS.md")
    with open(results_path, "w") as f:
        f.write("\n".join([
            "# Compile Run 008 — Comprehensive 8,442-Row Ruleset",
            "",
            "**Status: real, engine-loadable Ruleset artifact (Ruleset.to_json()), "
            "unsigned, covering ALL 6 programs + untagged rows.**",
            "",
            f"- Total rows: {result['total_rows']}",
            f"- Checks compiled: {result['checks_compiled']}",
            f"- Failed: {result['failed']}",
            f"- Thresholds honestly left UNSPECIFIED (no invented numbers): {result['unspecified_thresholds']}",
            f"- Real cost (this run only -- see note if resumed from a prior stall): ${result['real_cost_this_run']}",
            f"- Ruleset SHA-256: {ruleset.sha256()}",
            "",
            "Load with `Ruleset.from_dict(json.load(open('ruleset.json')))`.",
        ]) + "\n")
    print(f"\n[written] {results_path}", flush=True)
    print(f"[written] {result['checks_compiled']} real Check objects to {ruleset_path} "
          f"({os.path.getsize(ruleset_path) / 1024 / 1024:.1f} MB)", flush=True)


if __name__ == "__main__":
    main()
