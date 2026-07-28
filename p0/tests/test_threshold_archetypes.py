"""
003b -- ratio/threshold check engine, proven at representative THRESHOLD-
archetype scale.

Complements tests/test_p0.py (which pins the concrete ratio="field_value"
vocabulary-gap fix, US1). This file proves ltv/dti/field_value hold correctly
across representative LTV, DTI, and the real ratio_threshold-00 row (a
minimum-credit-score floor, sampled directly from the AMQ workbook by 002a --
p0/experiment_002a/artifacts/sampled_rows.json), not just the demo's one
hand-authored check (spec.md US2), and that the existing confidence gate
correctly reaches field_value checks -- the first ratio_threshold sub-kind
structurally able to exercise it, since ltv/dti checks read loan.facts and
never carry a real doc_confidence (spec.md US3).

Run from p0/:  python -m pytest tests/test_threshold_archetypes.py -v
Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qc_engine import run
from qc_engine.model import CanonicalLoan, SourceValue
from qc_engine.ruleset import Check, Ruleset

SAMPLED_ROWS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiment_002a", "artifacts", "sampled_rows.json")


def _load_ratio_threshold_00():
    """T010: reads the real ratio_threshold-00 row 002a sampled directly from
    demo/rules/*.xlsx -- no fabricated condition text."""
    with open(SAMPLED_ROWS_PATH) as f:
        rows = json.load(f)["rows"]
    row = next(r for r in rows if r.get("row_id") == "ratio_threshold-00")
    assert row["archetype_id"] == "THRESHOLD"
    assert row["engine_kind"] == "ratio_threshold"
    assert "minimum credit score of 500" in row["defect_text"]
    return row


RATIO_THRESHOLD_00 = _load_ratio_threshold_00()


def _run_single(chk, loan):
    rs = Ruleset(ruleset_id=f"t-{chk.id}", version=1, checks=[chk])
    return run(loan, rs)


# --- T011: LTV at/above/exactly-on threshold (spec.md SC-002) -------------
def _assert_ltv_archetype_correct():
    chk = Check(id="chk-ltv-95", name="LTV within program max (95%)",
                field_name="", kind="ratio_threshold", ratio="ltv",
                severity="CRITICAL", threshold="95", operator="<=")
    fail_loan = CanonicalLoan(loan_id="LN-LTV-OVER",
                              facts={"loan_amount": "340000.00", "property_value": "350000.00"})
    pass_loan = CanonicalLoan(loan_id="LN-LTV-UNDER",
                              facts={"loan_amount": "300000.00", "property_value": "350000.00"})
    boundary_loan = CanonicalLoan(loan_id="LN-LTV-EXACT",
                                  facts={"loan_amount": "332500.00", "property_value": "350000.00"})
    fail_res = _run_single(chk, fail_loan)
    pass_res = _run_single(chk, pass_loan)
    boundary_res = _run_single(chk, boundary_loan)
    assert fail_res.results[0].status == "FAIL", fail_res.results[0].status
    assert pass_res.results[0].status == "PASS", pass_res.results[0].status
    # exactly 95.000% under a <= operator must PASS -- the boundary itself
    # is not a violation (money.py::ltv_percent, ROUND_HALF_EVEN, 3dp).
    assert boundary_res.results[0].status == "PASS", boundary_res.results[0].status
    assert boundary_res.results[0].compared_value == "95.000"
    return fail_res


def test_ltv_archetype_correctness_and_exact_boundary():
    _assert_ltv_archetype_correct()


# --- T012: DTI at/above threshold ------------------------------------------
def _assert_dti_archetype_correct():
    chk = Check(id="chk-dti-45", name="DTI within program max (45%)",
                field_name="", kind="ratio_threshold", ratio="dti",
                severity="CRITICAL", threshold="45", operator="<=")
    fail_loan = CanonicalLoan(loan_id="LN-DTI-OVER",
                              facts={"monthly_debts": "3000.00", "monthly_income": "5000.00"})
    pass_loan = CanonicalLoan(loan_id="LN-DTI-UNDER",
                              facts={"monthly_debts": "2000.00", "monthly_income": "5000.00"})
    fail_res = _run_single(chk, fail_loan)
    pass_res = _run_single(chk, pass_loan)
    assert fail_res.results[0].status == "FAIL", fail_res.results[0].status
    assert pass_res.results[0].status == "PASS", pass_res.results[0].status
    return fail_res


def test_dti_archetype_correctness():
    _assert_dti_archetype_correct()


# --- T013: the real ratio_threshold-00 row, field_value mode --------------
def _credit_floor_check():
    return Check(id="chk-credit-floor", name=RATIO_THRESHOLD_00["defect_text"],
                field_name="credit_score", kind="ratio_threshold",
                severity="CRITICAL", ratio="field_value",
                threshold="500", operator=">=")


def _assert_field_value_archetype_correct():
    chk = _credit_floor_check()
    fail_loan = CanonicalLoan(loan_id="LN-CREDIT-BELOW-FLOOR",
                              fields={"credit_score": SourceValue(doc=480, doc_confidence=0.99)})
    pass_loan = CanonicalLoan(loan_id="LN-CREDIT-AT-FLOOR",
                              fields={"credit_score": SourceValue(doc=500, doc_confidence=0.99)})
    fail_res = _run_single(chk, fail_loan)
    pass_res = _run_single(chk, pass_loan)
    assert fail_res.results[0].status == "FAIL", fail_res.results[0].status
    assert pass_res.results[0].status == "PASS", pass_res.results[0].status
    return fail_res


def test_ratio_threshold_00_field_value_archetype_correctness():
    _assert_field_value_archetype_correct()


# --- T014: zero-false-auto-clear across the full threshold batch (SC-003) --
def test_zero_false_auto_clear_across_threshold_batch():
    fail_results = [
        _assert_ltv_archetype_correct(),
        _assert_dti_archetype_correct(),
        _assert_field_value_archetype_correct(),
    ]
    for res in fail_results:
        assert not res.auto_cleared, (
            f"{res.loan_id}: a FAIL-worthy loan was reported as auto-cleared "
            f"-- false-auto-clear (SC-003 violation)")


# --- T015-T016: confidence gate reaches field_value checks (spec.md US3) --
def test_low_confidence_field_value_pass_withholds_autoclear():
    # FR-007: unlike ltv/dti (which read loan.facts and so never carry a real
    # doc_confidence -- see test_ltv_dti_confidence_structurally_unreachable
    # below), field_value reads a real catalog field via loan.get(), so it is
    # the first ratio_threshold sub-kind that actually flows through the
    # confidence gate (ruling #8).
    chk = _credit_floor_check()
    loan = CanonicalLoan(loan_id="LN-CREDIT-LOWCONF",
                         fields={"credit_score": SourceValue(doc=620, doc_confidence=0.50)})
    res = _run_single(chk, loan)
    assert res.results[0].status == "NEEDS_REVIEW", res.results[0].status


def test_high_confidence_field_value_pass_is_not_downgraded():
    chk = _credit_floor_check()
    loan = CanonicalLoan(loan_id="LN-CREDIT-HIGHCONF",
                         fields={"credit_score": SourceValue(doc=620, doc_confidence=0.95)})
    res = _run_single(chk, loan)
    assert res.results[0].status == "PASS", res.results[0].status


def test_ltv_dti_confidence_structurally_unreachable():
    # T017 (regression, documents the structural gap this feature closes):
    # an ltv-kind check's CheckResult.doc_confidence is None even when the
    # loan's credit_score field carries a real confidence -- ltv/dti read
    # loan.facts (field_name=""), which resolves to the model's default
    # empty SourceValue at the confidence-gate check, not the real field.
    # Not a defect this feature is scoped to fix; recorded so the difference
    # from field_value's behavior above is intentional, not an inconsistency.
    chk = Check(id="chk-ltv-95", name="LTV within program max (95%)",
                field_name="", kind="ratio_threshold", ratio="ltv",
                severity="CRITICAL", threshold="95", operator="<=")
    loan = CanonicalLoan(loan_id="LN-LTV-CONF-GAP",
                         facts={"loan_amount": "300000.00", "property_value": "350000.00"},
                         fields={"credit_score": SourceValue(doc=620, doc_confidence=0.01)})
    res = _run_single(chk, loan)
    assert res.results[0].status == "PASS", res.results[0].status
    assert res.results[0].doc_confidence is None, res.results[0].doc_confidence


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
