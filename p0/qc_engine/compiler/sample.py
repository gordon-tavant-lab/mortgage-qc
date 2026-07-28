"""
Production batch sampler (002b) — generalizes
`p0/experiment_002a/sample_rows.py`'s stratified-sampling pattern from a fixed
n=24 throwaway spike sample into a parameterized, real-batch draw (N > 24,
spec.md SC-001).

Deterministic: same seed -> same sample, forever (mirrors the p0/ discipline
of no un-seeded randomness). Not an extension of `p0/experiment_002a/`'s
scripts (spec.md Edge Cases) -- this reimplements the same classification call
against `p0/eval_synth/taxonomy.py` directly, as a production module.

Python 3.9 compatible.
"""
from __future__ import annotations

import os
import random
import sys
from collections import defaultdict
from typing import Any, Dict, List, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
_P0 = os.path.dirname(os.path.dirname(_HERE))  # .../p0
_EVAL_SYNTH = os.path.join(_P0, "eval_synth")
if _EVAL_SYNTH not in sys.path:
    sys.path.insert(0, _EVAL_SYNTH)

import taxonomy as T  # noqa: E402

_PROD_ROOT = os.path.dirname(_P0)  # .../mortgage-qc-prod
RULES_DIR = os.path.join(_PROD_ROOT, "demo", "rules")

# engine_kind -> the broader stratification bucket (mirrors research.md's
# 70/20/10 real-prevalence split, expressed in engine_kind terms since several
# archetype ids share one engine_kind).
KIND_BUCKET = {
    "predicate": "predicate",
    "ratio_threshold": "ratio_threshold",
    "agree_categorical": "reconcile",
    "agree_numeric": "reconcile",
}

DEFAULT_SEED = 20260702
DEFAULT_MIX_RATIOS = {"predicate": 0.70, "ratio_threshold": 0.20, "reconcile": 0.10}


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


def stratified_sample(
    n_total: int, seed: int = DEFAULT_SEED,
    mix_ratios: Optional[Dict[str, float]] = None,
) -> List[Dict[str, Any]]:
    """Draw n_total real rows, stratified across predicate/ratio_threshold/
    reconcile in roughly the given ratios (default: real-prevalence 70/20/10).
    n_total > 24 is the point of this module (spec.md SC-001); smaller values
    work too but 002a already proved the mechanism at n=24."""
    mix_ratios = mix_ratios or DEFAULT_MIX_RATIOS
    by_bucket = classify_all_rows()
    rng = random.Random(seed)
    target_mix = {b: round(n_total * r) for b, r in mix_ratios.items()}
    sample: List[Dict[str, Any]] = []
    for bucket, target_n in target_mix.items():
        pool = by_bucket.get(bucket, [])
        if not pool:
            continue
        n = min(target_n, len(pool))
        picked = rng.sample(pool, n)
        for i, row in enumerate(picked):
            row = dict(row)
            row["row_id"] = f"{bucket}-{i:03d}"
            sample.append(row)
    return sample
