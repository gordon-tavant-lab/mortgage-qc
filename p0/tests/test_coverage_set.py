"""
005 US1(COVERAGE)/US3 -- the COVERAGE tier: does every compiled check have a
proven scenario? (spec.md FR-005, SC-002).

RED-STATE NOTICE: `p0/eval_synth/coverage_set.py` does not exist yet (and
depends on `p0/eval_synth/scenario_construction.py`, which also does not
exist yet). This file is written FIRST, against the module contract
documented below.

ASSUMED MODULE CONTRACT for `p0/eval_synth/coverage_set.py`:

    @dataclass
    class CoverageResult:
        checks_total: int
        checks_covered: int
        coverage_fraction: float                 # checks_covered / checks_total
        construction_failures: List[Dict[str, Any]]
            # each: {"check_id", "kind", "error"} -- named, mirroring
            # scenario_construction.ConstructedScenario's own failure record
            # (FR-002), never aggregated away.

    def compute_coverage(ruleset: Ruleset) -> CoverageResult:
        '''Calls scenario_construction.construct_scenario(chk) once per
        chk in ruleset.checks (no hand-written per-field mutation code,
        spec.md SC-002); tallies checks_covered/checks_total/failures.'''

Run from p0/:  python -m pytest tests/test_coverage_set.py -v
Python 3.9 compatible.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "eval_synth"))

from qc_engine.ruleset import Check, Ruleset                  # noqa: E402

# The modules under test -- neither exists yet (red state, expected).
import scenario_construction as SC                              # noqa: E402
import coverage_set                                              # noqa: E402


def _sample_checks_all_six_kinds():
    """One representative Check per live engine kind (real field_catalog.json
    entries -- same fields test_scenario_construction.py uses, so this file
    stays consistent with that one rather than inventing a second field
    list)."""
    return [
        Check(id="chk-cov-predicate", name="ARM disclosure present",
              field_name="arm_preloan_disclosure_present", kind="predicate",
              predicate="is_true", severity="CRITICAL"),
        Check(id="chk-cov-ratio", name="LTV within program max", field_name="",
              kind="ratio_threshold", ratio="ltv", severity="CRITICAL",
              threshold="95.000", operator="<="),
        Check(id="chk-cov-agree-cat", name="Borrower name agreement",
              field_name="borrower_name", kind="agree_categorical",
              severity="CRITICAL", sources=["doc", "los"], normalizer="identity"),
        Check(id="chk-cov-agree-num", name="Note rate agreement",
              field_name="note_rate", kind="agree_numeric", severity="CRITICAL",
              sources=["doc", "los"], tolerance="0.001"),
        Check(id="chk-cov-agree-doc-cat", name="Loan purpose agrees 1003 vs CD",
              field_name="loan_purpose_1003", compare_field_name="loan_purpose_cd",
              kind="agree_doc_categorical", severity="CRITICAL", sources=["doc"],
              normalizer="identity"),
        Check(id="chk-cov-agree-doc-num", name="Liability agrees 1003 vs credit report",
              field_name="liability_disclosed_on_1003",
              compare_field_name="liability_amount_credit_report",
              kind="agree_doc_numeric", severity="CRITICAL", sources=["doc"],
              tolerance="0"),
    ]


# --- T026: full coverage across all 6 kinds (SC-002) ------------------------
def test_coverage_reports_full_coverage_across_all_six_kinds():
    checks = _sample_checks_all_six_kinds()
    ruleset = Ruleset(ruleset_id="rs-coverage-full", version=1, checks=checks)

    result = coverage_set.compute_coverage(ruleset)

    assert result.checks_total == len(checks) == 6
    assert result.checks_covered == 6, (
        f"expected full coverage with zero hand-written per-field mutation "
        f"code; construction_failures={result.construction_failures}")
    assert result.coverage_fraction == 1.0
    assert result.construction_failures == []


# --- T026 (continued): one kind deliberately unregistered -> coverage
#     correctly decrements, and the gap is named, not silently dropped ------
def test_coverage_decrements_and_names_gap_when_one_kind_is_unregistered(monkeypatch):
    checks = _sample_checks_all_six_kinds()
    ruleset = Ruleset(ruleset_id="rs-coverage-partial", version=1, checks=checks)

    # Deliberately remove agree_doc_numeric's registered strategy -- mirrors
    # spec.md Gap 4 (a check kind added by 003d that a not-yet-updated
    # constructor has never heard of).
    monkeypatch.delitem(SC.STRATEGIES, "agree_doc_numeric", raising=False)

    result = coverage_set.compute_coverage(ruleset)

    assert result.checks_total == 6
    assert result.checks_covered == 5, (
        "removing one kind's strategy must decrement checks_covered by "
        "exactly the number of checks of that kind (1 here), not silently "
        "keep reporting full coverage")
    assert result.coverage_fraction == 5 / 6
    assert len(result.construction_failures) == 1
    failure = result.construction_failures[0]
    assert failure["check_id"] == "chk-cov-agree-doc-num"
    assert failure["kind"] == "agree_doc_numeric"
    assert failure["error"], "the gap must be named (an error string), never dropped silently"


def test_coverage_of_empty_ruleset_is_vacuously_complete():
    empty = Ruleset(ruleset_id="rs-coverage-empty", version=1, checks=[])
    result = coverage_set.compute_coverage(empty)
    assert result.checks_total == 0
    assert result.checks_covered == 0
    assert result.coverage_fraction == 1.0
    assert result.construction_failures == []


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
