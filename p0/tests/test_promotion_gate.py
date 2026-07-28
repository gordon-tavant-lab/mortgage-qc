"""
005 US2/US3(VOLUME)/US4/US5 -- the hard-block promotion gate
(spec.md FR-006/007/009/010, SC-003/005).

RED-STATE NOTICE: `p0/eval_synth/promotion_gate.py` does not exist yet. This
file is written FIRST, against the module contract documented below.

ASSUMED MODULE CONTRACT for `p0/eval_synth/promotion_gate.py`:

    @dataclass
    class PromotionGateResult:
        promotion_decision: str        # "PROMOTE" | "BLOCK"
        exit_code: int                 # 0 == promote, non-zero == block
        false_auto_clears: List[Dict[str, Any]]
            # each: {"check_id", "loan_id", "expected", "actual"} -- named,
            # never aggregated away into a bare count (FR-006).
        golden: Dict[str, Any]
        coverage: Dict[str, Any]
        volume: Dict[str, Any]         # includes "auto_clear_rate" (SC-005)
                                        # and "false_auto_clear_count"
        invariants: Dict[str, Dict[str, Any]]
            # keyed by invariant name (e.g. "ltv_monotonicity"); each value
            # has at least {"applicable": bool, "passed": bool} (FR-008).
        def to_dict(self) -> Dict[str, Any]: ...

    def run_promotion_gate(
        candidate: Ruleset,
        baseline: Optional[Ruleset] = None,
        volume_n: int = 5000,
        volume_loans: Optional[List[Tuple[CanonicalLoan, Dict[str, str], Dict[str, Any]]]] = None,
    ) -> PromotionGateResult:
        '''The single CI-runnable entry point (FR-009). `volume_loans`, when
        given, REPLACES the default `generator.generate(volume_n)` population
        -- the injection point this test suite uses to construct exact,
        deterministic false-auto-clear/PROMOTE cases without depending on
        the generator's own random mix. Each `(loan, expected_verdicts,
        provenance)` triple scores identically regardless of what
        `provenance` contains (FR-010/US5) -- a synthetic mutation record and
        an `{"provenance": "expert-labeled"}` stand-in for a future real
        loan (feature 012) must not be special-cased.'''

Run from p0/:  python -m pytest tests/test_promotion_gate.py -v
Python 3.9 compatible.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "eval_synth"))

from qc_engine.model import CanonicalLoan                    # noqa: E402
from qc_engine.ruleset import Check, Ruleset                 # noqa: E402
from fixtures.ruleset_demo import demo_ruleset                # noqa: E402

import generator as G                                          # noqa: E402

# The module under test -- does not exist yet (red state, expected).
import promotion_gate                                          # noqa: E402


def _ltv_check(operator: str, check_id: str = "chk-ltv-max") -> Check:
    return Check(id=check_id, name="LTV within program max (95%)",
                 field_name="", kind="ratio_threshold", ratio="ltv",
                 severity="CRITICAL", threshold="95.000", operator=operator,
                 message_fail="LTV exceeds program maximum of 95%.")


def _single_ltv_ruleset(operator: str) -> Ruleset:
    return Ruleset(ruleset_id="candidate-single-ltv", version=1,
                    checks=[_ltv_check(operator)])


# --- T018: injected false-auto-clear -> non-zero exit + BLOCK, named case --
def test_injected_false_auto_clear_blocks_promotion():
    # THRESHOLD archetype: LTV pushed to 96% of value -- ground truth (by
    # construction, generator.py) says chk-ltv-max must FAIL.
    loan, expected, prov = G.make_single(seed=42, archetype="THRESHOLD")
    # MISWIRED candidate: operator inverted (">=" instead of "<="), so the
    # SAME 96%-over loan resolves PASS under this (bad) rule -- a genuine
    # false-auto-clear, not a fabricated one (spec.md US2 Independent Test).
    miswired = _single_ltv_ruleset(operator=">=")

    result = promotion_gate.run_promotion_gate(
        candidate=miswired, volume_loans=[(loan, expected, prov)])

    assert result.exit_code != 0
    assert result.promotion_decision == "BLOCK"
    assert result.false_auto_clears, "the offending case must be named, not just counted"
    named = result.false_auto_clears[0]
    assert named["check_id"] == "chk-ltv-max"
    assert named["loan_id"] == loan.loan_id
    assert named["expected"] == "FAIL"
    assert named["actual"] == "PASS"


# --- T019: zero injected defects -> exit 0, PROMOTE ------------------------
def test_zero_false_auto_clears_promotes():
    loan, expected, prov = G.make_single(seed=42, archetype="THRESHOLD")
    correctly_wired = _single_ltv_ruleset(operator="<=")

    result = promotion_gate.run_promotion_gate(
        candidate=correctly_wired, volume_loans=[(loan, expected, prov)])

    assert result.exit_code == 0
    assert result.promotion_decision == "PROMOTE"
    assert result.false_auto_clears == []


# --- T020: the gate itself is deterministic (US2 Acceptance Scenario 3) ----
def test_block_decision_is_deterministic_on_rerun():
    loan, expected, prov = G.make_single(seed=42, archetype="THRESHOLD")
    miswired = _single_ltv_ruleset(operator=">=")

    result_a = promotion_gate.run_promotion_gate(
        candidate=miswired, volume_loans=[(loan, expected, prov)])
    result_b = promotion_gate.run_promotion_gate(
        candidate=miswired, volume_loans=[(loan, expected, prov)])

    assert result_a.promotion_decision == result_b.promotion_decision == "BLOCK"
    assert result_a.exit_code == result_b.exit_code
    assert result_a.false_auto_clears == result_b.false_auto_clears
    assert result_a.to_dict() == result_b.to_dict()


# --- T027: VOLUME reports auto_clear_rate alongside false_auto_clear_count
#     (SC-005) -- placed here (not test_coverage_set.py/test_golden_set.py)
#     because plan.md's Project Structure wires VOLUME's auto_clear_rate
#     metric into promotion_gate.py's orchestration (T031/T032), the file
#     this suite already exercises end to end. -------------------------------
def test_volume_tier_reports_auto_clear_rate_and_zero_false_clears_on_clean_candidate():
    result = promotion_gate.run_promotion_gate(
        candidate=demo_ruleset(), volume_loans=G.generate(200, start_seed=91000))

    assert "auto_clear_rate" in result.volume
    assert 0.0 <= result.volume["auto_clear_rate"] <= 1.0
    assert result.volume["false_auto_clear_count"] == 0
    assert result.promotion_decision == "PROMOTE"


def test_volume_tier_false_auto_clear_count_nonzero_triggers_block():
    loan, expected, prov = G.make_single(seed=42, archetype="THRESHOLD")
    miswired = _single_ltv_ruleset(operator=">=")

    result = promotion_gate.run_promotion_gate(
        candidate=miswired, volume_loans=[(loan, expected, prov)])

    assert result.volume["false_auto_clear_count"] > 0
    assert result.promotion_decision == "BLOCK"


# --- T034-equivalent: the generalized monotonicity invariant runs against
#     the CANDIDATE ruleset actually under test, not a hardcoded
#     demo_ruleset() (spec.md FR-008/US4). Exercised here (rather than a
#     direct edit to eval_synth/test_properties.py, which plan.md marks
#     MODIFIED production-adjacent code, not one of this task's four named
#     test files) via promotion_gate's own orchestration, which US4's tasks
#     (T038) wire the generalized invariant suite into. ----------------------
def test_promotion_gate_ltv_monotonicity_invariant_applicable_and_passes():
    candidate = _single_ltv_ruleset(operator="<=")
    result = promotion_gate.run_promotion_gate(
        candidate=candidate, volume_loans=G.generate(20, start_seed=77000))

    assert "ltv_monotonicity" in result.invariants
    inv = result.invariants["ltv_monotonicity"]
    assert inv["applicable"] is True
    assert inv["passed"] is True


# --- T035-equivalent: a ruleset with NO ratio_threshold check at all -------
def test_promotion_gate_ltv_monotonicity_invariant_not_applicable_when_no_ratio_threshold_check():
    no_ltv_check = Check(id="chk-only-predicate", name="Note signed",
                          field_name="note_signed", kind="predicate",
                          predicate="is_true", severity="CRITICAL")
    candidate = Ruleset(ruleset_id="candidate-no-ltv", version=1, checks=[no_ltv_check])

    result = promotion_gate.run_promotion_gate(
        candidate=candidate, volume_loans=G.generate(10, start_seed=88000))

    assert "ltv_monotonicity" in result.invariants
    inv = result.invariants["ltv_monotonicity"]
    assert inv["applicable"] is False, (
        "an invariant whose relevant check kind is absent from the ruleset "
        "under test must be reported not-applicable, never silently passed "
        "or errored (spec.md US4 Acceptance Scenario 2)")


# --- T040: the scorer does not distinguish loan provenance (FR-010/US5) ----
def test_expert_labeled_stand_in_scores_identically_to_synthetic_loan():
    """A `(loan, expected_verdicts)` pair tagged `provenance: "expert-labeled"`
    (no mutation-archetype metadata -- the shape feature 012's real loans are
    expected to eventually carry) must score through the exact same path as
    a synthetic constructed-by-mutation LabeledLoan, with no special-casing."""
    synthetic_loan, synthetic_expected, synthetic_prov = G.make_single(
        seed=42, archetype="THRESHOLD")
    expert_labeled_loan = CanonicalLoan(loan_id="REAL-LOAN-STANDIN-001",
                                        facts=dict(synthetic_loan.facts),
                                        fields=dict(synthetic_loan.fields))
    expert_labeled_expected = dict(synthetic_expected)
    expert_labeled_prov = {"provenance": "expert-labeled"}  # no "mutations" key at all

    candidate = _single_ltv_ruleset(operator="<=")

    result_synthetic = promotion_gate.run_promotion_gate(
        candidate=candidate,
        volume_loans=[(synthetic_loan, synthetic_expected, synthetic_prov)])
    result_expert = promotion_gate.run_promotion_gate(
        candidate=candidate,
        volume_loans=[(expert_labeled_loan, expert_labeled_expected, expert_labeled_prov)])

    # Identical result SHAPE (same keys/tier structure) and identical
    # decision -- the scorer's interface must not branch on provenance.
    assert set(result_synthetic.to_dict().keys()) == set(result_expert.to_dict().keys())
    assert result_synthetic.promotion_decision == result_expert.promotion_decision == "PROMOTE"
    assert result_synthetic.volume["false_auto_clear_count"] == result_expert.volume["false_auto_clear_count"] == 0


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
