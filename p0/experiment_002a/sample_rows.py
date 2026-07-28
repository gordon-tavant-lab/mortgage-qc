"""
Step 1 of the 002a compile-fidelity spike: stratified sample of REAL AMQ rows.

Draws rows from demo/rules/*.xlsx (the same real workbooks taxonomy.py already
classifies), stratified by check-kind category in rough proportion to real
prevalence (predicate ~70% / ratio_threshold ~20% / reconcile ~10%, per
research.md decision #1 and taxonomy.json's archetype counts).

Deterministic: same seed -> same sample, forever (mirrors the p0/ discipline
of no un-seeded randomness).

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import random
import sys
from collections import defaultdict
from typing import Any, Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "eval_synth"))

import taxonomy as T  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PROD = os.path.dirname(os.path.dirname(HERE))
RULES_DIR = os.path.join(PROD, "demo", "rules")

# engine_kind -> the broader stratification bucket (matches research.md #1's
# 70/20/10 split, which is expressed in engine_kind terms, not archetype-id
# terms, since several archetype ids share one engine_kind).
KIND_BUCKET = {
    "predicate": "predicate",
    "ratio_threshold": "ratio_threshold",
    "agree_categorical": "reconcile",
    "agree_numeric": "reconcile",
}

TARGET_TOTAL = 24
TARGET_MIX = {"predicate": 17, "ratio_threshold": 5, "reconcile": 2}  # ~70/20/10 of 24
SEED = 20260701


def classify_all_rows() -> Dict[str, List[Dict[str, Any]]]:
    """All real rows, bucketed by engine_kind (via taxonomy.classify)."""
    paths = [os.path.join(RULES_DIR, f) for f in os.listdir(RULES_DIR)
             if f.lower().endswith(".xlsx") and not f.startswith("~")]
    by_bucket: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    arch_by_id = {a["id"]: a for a in T.ARCHETYPES}
    for p in paths:
        for row in T.load_rows(p):
            arch_id = T.classify(row["defect_text"])
            if arch_id in (None, "SQL_GATING"):
                continue
            engine_kind = arch_by_id[arch_id]["engine_kind"]
            bucket = KIND_BUCKET[engine_kind]
            row = dict(row)
            row["archetype_id"] = arch_id
            row["engine_kind"] = engine_kind
            row["source_file"] = os.path.basename(p)
            by_bucket[bucket].append(row)
    return by_bucket


def stratified_sample() -> List[Dict[str, Any]]:
    by_bucket = classify_all_rows()
    rng = random.Random(SEED)
    sample: List[Dict[str, Any]] = []
    for bucket, target_n in TARGET_MIX.items():
        pool = by_bucket.get(bucket, [])
        if not pool:
            continue
        n = min(target_n, len(pool))
        picked = rng.sample(pool, n)
        for i, row in enumerate(picked):
            row = dict(row)
            row["row_id"] = f"{bucket}-{i:02d}"
            sample.append(row)
    return sample


def main() -> int:
    sample = stratified_sample()
    dist: Dict[str, int] = defaultdict(int)
    for row in sample:
        dist[row["engine_kind"]] += 1
    out = {
        "seed": SEED,
        "target_mix": TARGET_MIX,
        "actual_count": len(sample),
        "archetype_distribution": dict(dist),
        "rows": sample,
    }
    out_path = os.path.join(HERE, "artifacts", "sampled_rows.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=False)
    print(f"Sampled {len(sample)} rows -> {out_path}")
    print(f"Distribution: {dict(dist)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
