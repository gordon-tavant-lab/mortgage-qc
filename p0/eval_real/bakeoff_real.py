"""
012 User Story 3 (T019/T020) -- the G3 bake-off re-runs on real loans; a
real cost/token measurement ships independent of expert labels (FR-009/010/
011).

Re-uses `p0/experiment_g3/bakeoff.py`'s own LOCKED D1/D2/D3 methodology and
pricing table (`PRICING`, `REGIONAL_PREMIUM`, `SCALE_LOANS`) -- this module
does not invent a second cost model or a second determinism definition, it
re-applies the pre-registered one to a real (or real-shaped) loan.

`evaluate_fn` is injected with `llm_arm.evaluate_llm`'s own
`(loan, ruleset, model_id) -> (verdicts, tokens)` signature so this module's
report-shaping logic (BLOCKED-vs-populated D2, always-populated D3) is
provable offline with a deterministic fake, exactly as
`p0/tests/test_bakeoff_real.py` does -- the live Bedrock call itself stays a
manual, non-CI integration run (mirrors `llm_arm.py`'s own exclusion from
`pytest p0/tests`).

FR-011: if `expert_labels` is falsy, `d2_accuracy` MUST read an explicit
`"BLOCKED"` status naming the missing dependency -- never silently omitted.
FR-010: `d3_cost` MUST be populated regardless of whether `expert_labels` is
given.

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys
from decimal import Decimal
from typing import Any, Callable, Dict, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qc_engine.model import CanonicalLoan  # noqa: E402
from qc_engine.ruleset import Ruleset  # noqa: E402

from experiment_g3.bakeoff import PRICING, REGIONAL_PREMIUM, SCALE_LOANS  # noqa: E402

EvaluateFn = Callable[..., Tuple[Dict[str, str], Dict[str, int]]]

DEFAULT_PRICING_KEY = "haiku"  # matches G3's own RESULTS.md headline arm


def _blocked_reason() -> str:
    return (
        "No expert-adjudicated verdict labels exist yet for any check on "
        "this loan (the G1 dependency, per spec.md Assumptions/FR-011) -- "
        "the accuracy/false-auto-clear comparison cannot be computed until "
        "at least one labeled check exists."
    )


def _d2_accuracy(verdicts: Dict[str, str],
                  expert_labels: Optional[Dict[str, str]]) -> Dict[str, Any]:
    if not expert_labels:
        return {"status": "BLOCKED", "reason": _blocked_reason()}

    total = 0
    match = 0
    false_clears = 0
    for check_id, expected in expert_labels.items():
        got = verdicts.get(check_id)
        if got is None:
            continue
        total += 1
        if got == expected:
            match += 1
        if expected == "FAIL" and got == "PASS":
            false_clears += 1

    return {
        "status": "REPORTED",
        "checks_scored": total,
        "exact_match_rate": round(match / total, 4) if total else 1.0,
        "false_auto_clear_count": false_clears,
    }


def _d1_determinism(verdicts_a: Dict[str, str], verdicts_b: Dict[str, str],
                     model_id: str) -> Dict[str, Any]:
    """Are two evaluate_fn calls' verdict sets byte-identical? (D1's own
    definition, RESULTS.md.) With a deterministic evaluate_fn (temperature=0
    Bedrock call, or the test's deterministic fake), this holds; this
    function proves the *reporting logic*, not the model's own determinism
    (G3's RESULTS.md already answered that question for the synthetic
    6-loan sample)."""
    a_json = json.dumps(verdicts_a, sort_keys=True)
    b_json = json.dumps(verdicts_b, sort_keys=True)
    return {"byte_identical": a_json == b_json, "model_id": model_id, "repeats": 2}


def _d3_cost(tokens: Dict[str, int], pricing_key: str) -> Dict[str, Any]:
    """FR-010: real per-loan token count -> cost-at-10k-loans, using G3's own
    LOCKED pricing table + regional premium + scale (imported, not
    re-derived) -- replaces the "$700-$3,500/10k-run, reasoned not computed"
    gap with an actual, measured number once run against a real,
    full-extraction-scale payload."""
    pricing = PRICING[pricing_key]
    input_tokens = int(tokens.get("input_tokens", 0) or 0)
    output_tokens = int(tokens.get("output_tokens", 0) or 0)
    token_count = input_tokens + output_tokens

    in_cost = (Decimal(input_tokens) * SCALE_LOANS / Decimal(1_000_000)) * pricing["input"]
    out_cost = (Decimal(output_tokens) * SCALE_LOANS / Decimal(1_000_000)) * pricing["output"]
    cost_global = in_cost + out_cost
    cost_regional = cost_global * REGIONAL_PREMIUM

    return {
        "model": pricing["label"],
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "token_count": token_count,
        "scale_loans": SCALE_LOANS,
        "cost_at_10k_loans_usd": float(round(cost_global, 2)),
        "cost_at_10k_loans_regional_usd": float(round(cost_regional, 2)),
    }


def run_bakeoff_real(loan: CanonicalLoan, ruleset: Ruleset,
                      expert_labels: Optional[Dict[str, str]],
                      evaluate_fn: EvaluateFn,
                      model_id: str = "default",
                      pricing_key: str = DEFAULT_PRICING_KEY) -> Dict[str, Any]:
    """Re-runs G3's locked D1/D2/D3 methodology against one real (or
    real-shaped) adapted loan.

    `evaluate_fn` must match `llm_arm.evaluate_llm`'s own signature:
    `(loan, ruleset, model_id) -> (verdicts: Dict[check_id, status], tokens:
    Dict[str, int])`. Called twice (D1's own determinism check needs >=2
    repeats); the SECOND call's tokens are the ones D3 reports (arbitrary
    but fixed choice -- either call is representative for a deterministic
    evaluate_fn; G3's own methodology only needs one loan's tokens per run).
    """
    verdicts_1, tokens_1 = evaluate_fn(loan, ruleset, model_id)
    verdicts_2, _tokens_2 = evaluate_fn(loan, ruleset, model_id)

    d1 = _d1_determinism(verdicts_1, verdicts_2, model_id)
    d2 = _d2_accuracy(verdicts_1, expert_labels)
    d3 = _d3_cost(tokens_1, pricing_key)

    return {
        "loan_id": loan.loan_id,
        "model_id": model_id,
        "d1_determinism": d1,
        "d2_accuracy": d2,
        "d3_cost": d3,
    }
