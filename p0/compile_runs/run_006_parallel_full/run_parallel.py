"""
Compile 5,365-row scope to a single JSON rules artifact, in parallel.

Same compile_row() logic as run_003/run_004/run_005 — the only change is
concurrency: each row's Bedrock call is I/O-bound (~7-8s waiting on the
network), so a thread pool overlaps them instead of running one at a time.
Confirmed via run_poc_json (100 rows, sequential, 7.9s/row average) that
compute time on this machine is near-zero between calls — the wait is
Bedrock's, not ours. Bedrock quota (checked via `aws service-quotas`) is
10,000 req/min for Sonnet 4.6 cross-region inference, far above anything
this run needs.

Checkpoints every CHECKPOINT_EVERY completed rows so a killed/interrupted
run doesn't lose already-paid-for compilations (this failure mode already
hit us once — a run appeared to hang with no partial output on disk).

Usage (from p0/, with AWS credentials):
    python3 compile_runs/run_006_parallel_full/run_parallel.py

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys
import threading
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any, Dict, List

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

MAX_WORKERS = 20
CHECKPOINT_EVERY = 250

PRICE_PER_1K_INPUT = 0.003
PRICE_PER_1K_OUTPUT = 0.015


def load_all_scoped_rows() -> List[Dict[str, Any]]:
    """All 5,365 real rows in the scope."""
    paths = [os.path.join(RULES_DIR, f) for f in os.listdir(RULES_DIR)
             if f.lower().endswith(".xlsx") and not f.startswith("~$")]
    rows: List[Dict[str, Any]] = []
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


def _bedrock_client():
    """A Bedrock client tuned for concurrent use: enough HTTP connections in
    the pool for MAX_WORKERS threads, plus adaptive retry so throttling
    (extremely unlikely at our quota headroom, but possible under bursts)
    backs off instead of failing the row."""
    import boto3
    from botocore.config import Config
    cfg = Config(
        max_pool_connections=MAX_WORKERS + 5,
        retries={"max_attempts": 5, "mode": "adaptive"},
    )
    session = boto3.Session(profile_name=C.PROFILE, region_name=C.REGION)
    return session.client("bedrock-runtime", config=cfg)


def _draft_to_json_rule(draft) -> Dict[str, Any]:
    return {
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
        },
    }


class _Progress:
    """Thread-safe counters + checkpoint writer."""

    def __init__(self, total: int, checkpoint_path: str):
        self.total = total
        self.checkpoint_path = checkpoint_path
        self.lock = threading.Lock()
        self.completed = 0
        self.failed = 0
        self.tokens_in = 0
        self.tokens_out = 0
        self.json_rules: List[Dict[str, Any]] = []

    def record(self, json_rule, tokens_in, tokens_out, ok: bool):
        with self.lock:
            self.completed += 1
            self.tokens_in += tokens_in
            self.tokens_out += tokens_out
            if ok and json_rule is not None:
                self.json_rules.append(json_rule)
            else:
                self.failed += 1

            if self.completed % 25 == 0 or self.completed == self.total:
                cost = (self.tokens_in / 1000 * PRICE_PER_1K_INPUT) + (self.tokens_out / 1000 * PRICE_PER_1K_OUTPUT)
                print(f"  [{self.completed}/{self.total}] compiled={len(self.json_rules)} "
                      f"failed={self.failed} cost=${cost:.2f}", flush=True)

            if self.completed % CHECKPOINT_EVERY == 0 or self.completed == self.total:
                with open(self.checkpoint_path, "w") as f:
                    json.dump(self.json_rules, f, indent=2)
                print(f"  [checkpoint] {len(self.json_rules)} rules written to {self.checkpoint_path}", flush=True)


def _compile_one(client, row, catalog, progress: _Progress):
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
        json_rule = _draft_to_json_rule(draft) if draft.check is not None else None
        progress.record(json_rule, usage["inputTokens"], usage["outputTokens"], ok=draft.check is not None)
    except Exception as e:
        print(f"  [error] row_id={row.get('row_id')}: {type(e).__name__}: {e}", flush=True)
        progress.record(None, usage["inputTokens"], usage["outputTokens"], ok=False)


def run() -> Dict[str, Any]:
    all_rows = load_all_scoped_rows()
    print(f"\nLoaded {len(all_rows)} rows from scope.", flush=True)
    print(f"Compiling with {MAX_WORKERS} parallel workers.\n", flush=True)

    catalog = load_catalog(CATALOG_PATH)
    client = _bedrock_client()

    checkpoint_path = os.path.join(HERE, "rules_checkpoint.json")
    progress = _Progress(total=len(all_rows), checkpoint_path=checkpoint_path)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = [pool.submit(_compile_one, client, row, catalog, progress) for row in all_rows]
        for f in as_completed(futures):
            f.result()  # re-raise any thread-level exception we didn't catch

    total_cost = (progress.tokens_in / 1000 * PRICE_PER_1K_INPUT) + (progress.tokens_out / 1000 * PRICE_PER_1K_OUTPUT)
    return {
        "total_rows": len(all_rows),
        "json_rules_generated": len(progress.json_rules),
        "failed": progress.failed,
        "real_cost": round(total_cost, 2),
        "json_rules": progress.json_rules,
    }


def _write_results_md(result: Dict[str, Any], path: str) -> None:
    lines = [
        "# Compile Run 006 — Parallel JSON Rules Output",
        "",
        "**Status: JSON rule artifact generated from 5,365-row scope, compiled with "
        f"{MAX_WORKERS} parallel Bedrock workers.**",
        "",
        "## Result",
        "",
        f"- Total rows in scope: {result['total_rows']}",
        f"- JSON rules generated: {result['json_rules_generated']}",
        f"- Failed: {result['failed']}",
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
    import time
    t0 = time.time()
    result = run()
    elapsed = time.time() - t0

    print(json.dumps({k: v for k, v in result.items() if k != "json_rules"}, indent=2), flush=True)
    print(f"\nElapsed: {elapsed/60:.1f} min", flush=True)

    rules_file = os.path.join(HERE, "rules.json")
    with open(rules_file, "w") as f:
        json.dump(result["json_rules"], f, indent=2)

    results_path = os.path.join(HERE, "RESULTS.md")
    _write_results_md(result, results_path)
    print(f"\n[written] {results_path}", flush=True)
    print(f"[written] {len(result['json_rules'])} rules to {rules_file} "
          f"({os.path.getsize(rules_file) / 1024 / 1024:.1f} MB)", flush=True)


if __name__ == "__main__":
    main()
