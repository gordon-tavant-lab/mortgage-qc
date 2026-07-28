"""
002c -- multi-model judge panel, escalate-on-any-disagreement.

Reduces SME review load without trusting a single model's self-review: 2+
judge models from a different model family than the compiler score each
compiled rule against its source text and KB grounding. Deliberately
conservative (spec.md US4/FR-008): unanimous, confident agreement ->
auto-approve; ANY disagreement, or any judge's confidence below threshold,
-> escalate -- never a majority-vote auto-approve. This is a direct response
to researched findings (spec.md preamble) that judge panels have real,
correlated blind spots, not a hypothetical caution.

Only the pure escalation logic is tested here (no live model calls) --
judge_check()'s real Bedrock calls are exercised separately, same precedent
compile_llm.py's compile_row()/compile_batch() already set.

Run from p0/:  python -m pytest tests/test_judge_panel.py -v
Python 3.9 compatible.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qc_engine.compiler import judge_panel as J


def _verdict(agrees, confidence=0.95, reasoning="looks correct"):
    return J.JudgeVerdict(judge_model="test-model", agrees=agrees,
                          confidence=confidence, reasoning=reasoning)


# --- T023: unanimous agreement -> auto-approve ------------------------------
def test_unanimous_agreement_auto_approves():
    verdicts = [_verdict(True), _verdict(True)]
    assert J.escalate_or_approve(verdicts) == "AUTO_APPROVED"


# --- T024: any disagreement -> escalate, never majority-vote ---------------
def test_any_disagreement_escalates():
    verdicts = [_verdict(True), _verdict(False)]
    assert J.escalate_or_approve(verdicts) == "ESCALATED"


def test_majority_agreement_still_escalates_on_one_dissent():
    # 2-of-3 agree -- a majority-vote scheme would auto-approve this. This
    # feature deliberately does not: FR-008 requires unanimous agreement.
    verdicts = [_verdict(True), _verdict(True), _verdict(False)]
    assert J.escalate_or_approve(verdicts) == "ESCALATED"


# --- T025: escalation preserves every judge's individual reasoning ---------
def test_escalation_preserves_every_judges_reasoning():
    verdicts = [_verdict(True, reasoning="matches the HUD requirement exactly"),
               _verdict(False, reasoning="threshold looks inverted vs. source text")]
    result = J.judge_batch_result(verdicts)
    assert result["outcome"] == "ESCALATED"
    assert len(result["verdicts"]) == 2
    assert result["verdicts"][0]["reasoning"] == "matches the HUD requirement exactly"
    assert result["verdicts"][1]["reasoning"] == "threshold looks inverted vs. source text"


# --- T026: low confidence escalates even if all verdicts nominally agree ---
def test_low_confidence_escalates_despite_agreement():
    verdicts = [_verdict(True, confidence=0.95), _verdict(True, confidence=0.55)]
    assert J.escalate_or_approve(verdicts, confidence_threshold=0.8) == "ESCALATED"


def test_confidence_threshold_is_configurable_not_hardcoded():
    # FR-010: no literature-standard threshold exists -- it must be a real
    # parameter, not a baked-in constant this function silently assumes.
    verdicts = [_verdict(True, confidence=0.7), _verdict(True, confidence=0.7)]
    assert J.escalate_or_approve(verdicts, confidence_threshold=0.6) == "AUTO_APPROVED"
    assert J.escalate_or_approve(verdicts, confidence_threshold=0.8) == "ESCALATED"


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
