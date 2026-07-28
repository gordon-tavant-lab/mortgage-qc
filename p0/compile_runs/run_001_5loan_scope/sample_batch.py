"""
Starts the real rules-parsing process: draws a bounded, stratified FIRST
batch from the 5,365-row scope decided in
output/RULE-PROGRAM-GATING-FINDINGS.md §8 (FHA + VA + USDA + Fannie Mae,
loan 01/04 assumed Fannie), proportional to each program's real share of
that scope. Deliberately bounded, not the full 5,365 -- this run exists to
get real per-row cost/quality data before committing to the rest (mirrors
002a's own precedent of starting at n=24, not the full corpus).

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import random
import sys
from collections import defaultdict
from typing import Any, Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
P0 = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, P0)
sys.path.insert(0, os.path.join(P0, "eval_synth"))

import taxonomy as T  # noqa: E402
from qc_engine.compiler import program_gating as PG  # noqa: E402

RULES_DIR = os.path.join(P0, "..", "demo", "rules")
RULES_DIR = os.path.normpath(RULES_DIR)

NEEDED_PROGRAMS = {"FHA", "VA", "USDA", "Fannie Mae"}
SEED = 20260720
TARGET_TOTAL = 40  # bounded first tranche, proportional by program share


def load_scoped_rows() -> Dict[str, List[Dict[str, Any]]]:
    """All real rows in the 5,365-row §8 scope, bucketed by program."""
    paths = [os.path.join(RULES_DIR, f) for f in os.listdir(RULES_DIR)
             if f.lower().endswith(".xlsx") and not f.startswith("~$")]
    by_program: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    arch_by_id = {a["id"]: a for a in T.ARCHETYPES}
    for p in paths:
        for row in T.load_rows(p):
            program = PG.parse_exception_code_prefix(row.get("exception_code") or "")
            if program not in NEEDED_PROGRAMS:
                continue
            arch_id = T.classify(row.get("defect_text", "") or "")
            engine_kind = arch_by_id[arch_id]["engine_kind"] if arch_id else None
            row = dict(row)
            row["archetype_id"] = arch_id
            row["engine_kind"] = engine_kind or "predicate"  # LLM decides for real; this is only a sampling hint
            row["source_file"] = os.path.basename(p)
            row["program"] = program
            by_program[program].append(row)
    return by_program


def stratified_sample() -> List[Dict[str, Any]]:
    by_program = load_scoped_rows()
    total_scoped = sum(len(v) for v in by_program.values())
    rng = random.Random(SEED)
    sample: List[Dict[str, Any]] = []
    for program, pool in by_program.items():
        share = len(pool) / total_scoped
        n = max(1, round(share * TARGET_TOTAL))
        n = min(n, len(pool))
        picked = rng.sample(pool, n)
        for i, row in enumerate(picked):
            row = dict(row)
            row["row_id"] = f"{program.replace(' ', '')}-{i:03d}"
            sample.append(row)
    return sample


def main() -> int:
    sample = stratified_sample()
    dist_program: Dict[str, int] = defaultdict(int)
    dist_kind: Dict[str, int] = defaultdict(int)
    for row in sample:
        dist_program[row["program"]] += 1
        dist_kind[row["engine_kind"]] += 1
    out = {
        "seed": SEED,
        "target_total": TARGET_TOTAL,
        "actual_count": len(sample),
        "program_distribution": dict(dist_program),
        "kind_distribution_sampling_hint": dict(dist_kind),
        "rows": sample,
    }
    out_path = os.path.join(HERE, "sampled_batch.json")
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=False)
    print(f"Sampled {len(sample)} rows -> {out_path}")
    print(f"By program: {dict(dist_program)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
