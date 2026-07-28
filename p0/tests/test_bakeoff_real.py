"""
012 User Story 3 (T018) -- the G3 bake-off re-runs on real loans; real
cost/token measurement ships independent of expert labels.

`p0/experiment_g3`'s locked D1/D2/D3 methodology already proved determinism
and directional accuracy on 6 synthetic loans. `eval_real.bakeoff_real`
re-runs that SAME methodology against a real (or, for this test file, a
real-shaped synthetic stand-in) adapted loan. FR-011 makes one thing
non-negotiable: if no expert-adjudicated label exists yet for any check on
any real loan, the accuracy/D2 section MUST read an explicit `"BLOCKED"`
status naming the missing dependency -- never silently omitted. FR-010 makes
a second thing non-negotiable: the cost/token (D3) measurement ships
regardless of whether any label exists.

The real Arm B call (`p0/experiment_g3/llm_arm.py`'s Bedrock session) is a
genuinely live, credentialed, non-deterministic-to-construct external call --
this project's own convention keeps AWS-dependent runs out of
`pytest p0/tests` (mirrors `llm_arm.py` itself, which is not part of the
suite). So every test below that exercises `bakeoff_real`'s REPORT-SHAPING
logic injects a FAKE, offline `evaluate_fn` stub matching `llm_arm
.evaluate_llm`'s own `(loan, ruleset, model_id) -> (verdicts, tokens)`
signature -- proving the BLOCKED/populated-D3 report logic deterministically,
without ever calling Bedrock. The one test that would require an actual live
call against a real, full-extraction-scale payload is explicitly
skip-marked at the bottom of this file.

SAFETY: every loan id, verdict, and token count below is hand-authored and
synthetic. No real loan id, real S3 path, real AWS credential, or real PII
value appears anywhere in this file.

Python 3.9 compatible. `eval_real.bakeoff_real` does not exist yet -- every
test that needs it is expected to fail RED via ImportError until T019/T020
land (tasks.md). Imports are deferred inside each test function so this file
stays collectible by pytest before the package exists.
"""
from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "eval_synth"))

import generator as G  # noqa: E402
from fixtures.ruleset_demo import demo_ruleset  # noqa: E402

RULESET = demo_ruleset()
STANDIN_LOAN_ID = "SYN-STANDIN-BAKEOFF-001"


def _standin_loan():
    loan = G.build_clean(seed=777)
    loan.loan_id = STANDIN_LOAN_ID
    return loan


def _fake_evaluate_fn(loan, ruleset, model_id="fake-model"):
    """A deterministic, offline stand-in for `llm_arm.evaluate_llm` --
    matches its `(loan, ruleset, model_id) -> (verdicts, tokens)` return
    shape exactly, so `bakeoff_real` can accept either interchangeably.
    Never calls Bedrock, never touches the network."""
    verdicts = {c.id: "PASS" for c in ruleset.checks}
    tokens = {"input_tokens": 1234, "output_tokens": 56}
    return verdicts, tokens


# --------------------------------------------------------------------------- #
# FR-011: accuracy/D2 explicitly BLOCKED when no expert labels exist.
# --------------------------------------------------------------------------- #
def test_d2_accuracy_section_reports_blocked_when_no_expert_labels():
    from eval_real.bakeoff_real import run_bakeoff_real

    loan = _standin_loan()
    report = run_bakeoff_real(
        loan, RULESET, expert_labels=None, evaluate_fn=_fake_evaluate_fn,
    )

    assert report["d2_accuracy"]["status"] == "BLOCKED"
    assert isinstance(report["d2_accuracy"].get("reason"), str)
    assert len(report["d2_accuracy"]["reason"]) > 0


def test_d2_accuracy_blocked_status_is_never_silently_omitted():
    """A missing/absent d2_accuracy key would be indistinguishable from "we
    forgot to check" -- FR-011 requires the section to always be present."""
    from eval_real.bakeoff_real import run_bakeoff_real

    loan = _standin_loan()
    report = run_bakeoff_real(
        loan, RULESET, expert_labels=None, evaluate_fn=_fake_evaluate_fn,
    )

    assert "d2_accuracy" in report


# --------------------------------------------------------------------------- #
# FR-010: cost/token (D3) measurement is populated regardless of labels.
# --------------------------------------------------------------------------- #
def test_d3_cost_section_populated_and_non_null_with_zero_labels():
    from eval_real.bakeoff_real import run_bakeoff_real

    loan = _standin_loan()
    report = run_bakeoff_real(
        loan, RULESET, expert_labels=None, evaluate_fn=_fake_evaluate_fn,
    )

    d3 = report["d3_cost"]
    assert d3 is not None
    assert d3["token_count"] is not None and d3["token_count"] > 0
    assert d3["cost_at_10k_loans_usd"] is not None
    assert d3["cost_at_10k_loans_usd"] >= 0


def test_d3_cost_section_populated_even_when_labels_are_present():
    """FR-010's "independent of whether any expert label yet exists" cuts
    both ways -- D3 must also be present when labels DO exist, not folded
    away in favor of the D1/D2 section."""
    from eval_real.bakeoff_real import run_bakeoff_real

    loan = _standin_loan()
    # A TEST-ONLY synthetic label stand-in (T020's own framing -- no real
    # expert-adjudicated label exists at spec-writing time).
    synthetic_labels = {"chk-borrower-name": "PASS"}

    report = run_bakeoff_real(
        loan, RULESET, expert_labels=synthetic_labels, evaluate_fn=_fake_evaluate_fn,
    )

    assert report["d3_cost"] is not None
    assert report["d3_cost"]["token_count"] > 0


# --------------------------------------------------------------------------- #
# FR-009: when a labeled subset DOES exist, report D1 + D2 in RESULTS.md's
# existing table shape.
# --------------------------------------------------------------------------- #
def test_d1_d2_reported_when_a_synthetic_label_stand_in_is_supplied():
    from eval_real.bakeoff_real import run_bakeoff_real

    loan = _standin_loan()
    synthetic_labels = {"chk-borrower-name": "PASS"}

    report = run_bakeoff_real(
        loan, RULESET, expert_labels=synthetic_labels, evaluate_fn=_fake_evaluate_fn,
    )

    assert report["d2_accuracy"]["status"] != "BLOCKED"
    assert "exact_match_rate" in report["d2_accuracy"]
    assert "false_auto_clear_count" in report["d2_accuracy"]
    assert report["d1_determinism"] is not None


def test_d1_determinism_reflects_byte_identical_repeat_calls():
    """D1 asks: are Arm B's repeated verdict sets byte-identical? With a
    deterministic fake evaluate_fn, this must hold -- proving the
    determinism-reporting *logic* itself, independent of whether the real
    LLM call is actually deterministic (that's G3's own, already-answered
    question)."""
    from eval_real.bakeoff_real import run_bakeoff_real

    loan = _standin_loan()
    synthetic_labels = {"chk-borrower-name": "PASS"}

    report = run_bakeoff_real(
        loan, RULESET, expert_labels=synthetic_labels, evaluate_fn=_fake_evaluate_fn,
    )

    assert report["d1_determinism"]["byte_identical"] is True


# --------------------------------------------------------------------------- #
# Live/manual-only -- the TRUE real-loan, real-Bedrock variant.
# --------------------------------------------------------------------------- #
@pytest.mark.skip(
    reason="Requires a real, full-extraction-scale payload from a real "
           "already-acquired loan (live AWS S3 access, see spec.md "
           "Foundation section) AND a live AWS Bedrock call (profile "
           "'gordon-chan', mirrors p0/experiment_g3/llm_arm.py) to measure "
           "a genuine per-loan token count/cost -- neither is available or "
           "appropriate in this test environment. This project's own "
           "convention keeps AWS-dependent runs out of `pytest p0/tests`. "
           "Run manually via eval_real.adapter + eval_real.bakeoff_real "
           "once credentials exist -- never as part of the default "
           "CI/pytest suite."
)
def test_real_loan_real_bedrock_cost_measurement_LIVE_MANUAL_ONLY():
    """FR-010's true, live variant (the real-payload D3 measurement).
    Intentionally not implemented -- this stub exists only to name where
    that live check belongs, without executing it or referencing any real
    loan id, S3 path, AWS credential, or PII value in this repository."""
    pytest.skip("live S3 + live Bedrock real-loan run -- manual only, see docstring")
