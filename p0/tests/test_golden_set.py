"""
005 US3 (GOLDEN tier) -- fixed regression panel replay (spec.md FR-005/007,
SC-004).

RED-STATE NOTICE: `p0/eval_synth/golden_set.py` AND `p0/fixtures/golden_panel.py`
do not exist yet. This file is written FIRST, against the module contracts
documented below.

ASSUMED MODULE CONTRACT for `p0/eval_synth/golden_set.py`:

    @dataclass
    class GoldenFlip:
        check_id: str
        loan_id: str
        baseline_status: str
        candidate_status: str

    @dataclass
    class GoldenResult:
        panel_version: str
        total_cases: int
        regressions: List[GoldenFlip]     # spec.md: "golden.regressions"

    def replay_golden_panel(
        candidate: Ruleset,
        baseline: Optional[Ruleset] = None,
        panel: Optional[List[Tuple[CanonicalLoan, Dict[str, str], Dict[str, Any]]]] = None,
        panel_version: Optional[str] = None,
    ) -> GoldenResult:
        '''Replays `panel` (defaults to `golden_panel.PANEL` /
        `golden_panel.PANEL_VERSION` when not given -- the injection point
        this test suite uses for a deterministic, isolated flip case) against
        `candidate`. For each `(loan, expected_verdicts, provenance)` entry:
        `baseline_status` for a check_id is the live `baseline` ruleset's
        verdict when `baseline` is given, else the panel's own pinned
        `expected_verdicts[check_id]` (the "no prior-promoted baseline yet"
        edge case, spec.md Edge Cases). A GoldenFlip is recorded whenever
        `candidate`'s verdict differs from `baseline_status` for a check_id
        present in `expected_verdicts` (FR-007).'''

ASSUMED MODULE CONTRACT for `p0/fixtures/golden_panel.py` (seeded from
`p0/fixtures/ruleset_defects.py`'s 25 planted defects, spec.md Assumptions):

    PANEL_VERSION: str
    PANEL: List[Tuple[CanonicalLoan, Dict[str, str], Dict[str, Any]]]

Run from p0/:  python -m pytest tests/test_golden_set.py -v
Python 3.9 compatible.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "eval_synth"))

from qc_engine.model import CanonicalLoan, SourceValue        # noqa: E402
from qc_engine.ruleset import Check, Ruleset                  # noqa: E402

# The modules under test -- neither exists yet (red state, expected).
import golden_set                                               # noqa: E402
from fixtures import golden_panel                                # noqa: E402


def _ltv_check(operator: str) -> Check:
    return Check(id="chk-ltv-max", name="LTV within program max (95%)",
                 field_name="", kind="ratio_threshold", ratio="ltv",
                 severity="CRITICAL", threshold="95.000", operator=operator,
                 message_fail="LTV exceeds program maximum of 95%.")


def _ltv_loan(loan_id: str, ltv_pct: str) -> CanonicalLoan:
    return CanonicalLoan(loan_id=loan_id,
                         facts={"property_value": "100.00", "loan_amount": ltv_pct})


# --- T024: unchanged candidate ruleset -> zero regressions, panel named ----
def test_golden_replay_unchanged_ruleset_reports_zero_regressions_and_names_panel_version():
    correctly_wired = Ruleset(ruleset_id="rs-unchanged", version=1,
                              checks=[_ltv_check(operator="<=")])
    result = golden_set.replay_golden_panel(candidate=correctly_wired,
                                            baseline=correctly_wired)
    assert result.regressions == []
    assert result.panel_version == golden_panel.PANEL_VERSION
    assert result.total_cases >= 1, "golden_panel.PANEL must be non-empty"


# --- T025: one deliberately flipped verdict -> exactly one reported flip
#     (SC-004) -------------------------------------------------------------
def test_golden_replay_reports_exactly_one_flip():
    baseline = Ruleset(ruleset_id="rs-baseline", version=1,
                       checks=[_ltv_check(operator="<=")])
    # MISWIRED candidate: operator inverted, flipping the verdict for a
    # 96%-over loan the fixed panel already knows must FAIL.
    candidate = Ruleset(ruleset_id="rs-candidate", version=2,
                        checks=[_ltv_check(operator=">=")])

    over_loan = _ltv_loan("LN-GOLDEN-OVER", "96.00")
    isolated_panel = [
        (over_loan, {"chk-ltv-max": "FAIL"}, {"panel_version": "test-v0", "seed_source": "unit-test"}),
    ]

    result = golden_set.replay_golden_panel(
        candidate=candidate, baseline=baseline,
        panel=isolated_panel, panel_version="test-v0")

    assert result.panel_version == "test-v0"
    assert len(result.regressions) == 1, result.regressions
    flip = result.regressions[0]
    assert flip.check_id == "chk-ltv-max"
    assert flip.loan_id == "LN-GOLDEN-OVER"
    assert flip.baseline_status == "FAIL"
    assert flip.candidate_status == "PASS"


def test_golden_replay_reports_zero_flips_when_candidate_matches_baseline():
    baseline = Ruleset(ruleset_id="rs-baseline", version=1,
                       checks=[_ltv_check(operator="<=")])
    candidate = Ruleset(ruleset_id="rs-candidate-unchanged", version=2,
                        checks=[_ltv_check(operator="<=")])

    over_loan = _ltv_loan("LN-GOLDEN-OVER-2", "96.00")
    under_loan = _ltv_loan("LN-GOLDEN-UNDER-2", "80.00")
    isolated_panel = [
        (over_loan, {"chk-ltv-max": "FAIL"}, {"panel_version": "test-v0"}),
        (under_loan, {"chk-ltv-max": "PASS"}, {"panel_version": "test-v0"}),
    ]

    result = golden_set.replay_golden_panel(
        candidate=candidate, baseline=baseline,
        panel=isolated_panel, panel_version="test-v0")

    assert result.regressions == []
    assert result.total_cases == 2


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
