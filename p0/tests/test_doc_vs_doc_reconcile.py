"""
003d -- doc-vs-doc reconcile check engine (agree_doc_categorical/
agree_doc_numeric).

Unlike 003c (proof-only, zero engine changes), this feature adds real,
additive engine capability: two new check kinds that compare two
independently-named DOCUMENT fields against each other -- neither side is a
system source, so these never touch SourceValue.sources{} at all (that's
what keeps 001b's source-independence guard meaningful for the pre-existing
agree_categorical/agree_numeric, which this feature does not modify).

US1: the mechanism produces correct verdicts across agreement, genuine
divergence, one-side-absent, both-absent -- for both the categorical and
numeric kind, plus numeric tolerance boundaries and the UNSPECIFIED-tolerance
honesty guard.

US2 (the single highest-stakes property specific to this feature): a genuine
doc-vs-doc mismatch resolves FAIL with review_reason="EXCEPTION" -- the QC
failure path -- never the informational FLAG path agree_categorical uses for
doc-vs-system disagreement. Getting this backwards would silently
under-report real defects, exactly the failure mode that motivated this
feature (title-vesting/employment-date mismatches landing on a message-less
NEEDS_REVIEW instead of a real verdict).

Independence discipline: generator.py's assert_independently_constructed is
shaped for SourceValue.sources{} (doc-vs-system) and doesn't apply here --
doc-vs-doc has no sources{} dict on either side. The equivalent discipline is
simpler and enforced directly: divergent-case fixtures below use literally
different, unrelated values on the two fields (not a copy-then-mutate
pattern), so a genuine mismatch is unambiguous by construction.

Run from p0/:  python -m pytest tests/test_doc_vs_doc_reconcile.py -v
Python 3.9 compatible.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qc_engine import run
from qc_engine.catalog import (FieldCatalog, FieldCatalogEntry,
                                ReferentialIntegrityError,
                                validate_referential_integrity)
from qc_engine.model import CanonicalLoan, SourceValue
from qc_engine.ruleset import Check, Ruleset


def _run_single(chk, loan):
    rs = Ruleset(ruleset_id=f"t-{chk.id}", version=1, checks=[chk])
    return run(loan, rs)


# --- categorical fixture: employment start date, 1003 vs VOE ---------------
def _employment_date_check(check_id="chk-docdoc-employment-date"):
    return Check(id=check_id, name="Employment start date agrees across documents",
                 field_name="employment_start_date_1003",
                 compare_field_name="employment_start_date_voe",
                 kind="agree_doc_categorical", severity="CRITICAL", sources=["doc"],
                 normalizer="identity",
                 message_fail="Employment start date on the 1003 does not match the VOE.")


def test_doc_categorical_agreement_produces_pass():
    chk = _employment_date_check()
    loan = CanonicalLoan(loan_id="LN-DOCDOC-AGREE", fields={
        "employment_start_date_1003": SourceValue(doc="03/15/2018"),
        "employment_start_date_voe": SourceValue(doc="03/15/2018"),
    })
    res = _run_single(chk, loan)
    assert res.results[0].status == "PASS", res.results[0].status


def test_doc_categorical_genuine_divergence_produces_fail_never_flag():
    # The core behavioral proof this feature exists for: a doc-vs-doc
    # mismatch is a real defect (FAIL), not the informational FLAG
    # agree_categorical would produce for an analogous doc-vs-system case.
    chk = _employment_date_check()
    loan = CanonicalLoan(loan_id="LN-DOCDOC-DIVERGE", fields={
        "employment_start_date_1003": SourceValue(doc="03/15/2018"),
        "employment_start_date_voe": SourceValue(doc="05/01/2019"),
    })
    res = _run_single(chk, loan)
    assert res.results[0].status == "FAIL", res.results[0].status
    assert res.results[0].severity == "CRITICAL", res.results[0].severity


def test_doc_categorical_one_side_absent_needs_review_source_incomplete():
    chk = _employment_date_check()
    loan = CanonicalLoan(loan_id="LN-DOCDOC-ONESIDE", fields={
        "employment_start_date_1003": SourceValue(doc="03/15/2018"),
        "employment_start_date_voe": SourceValue(doc=None),
    })
    res = _run_single(chk, loan)
    assert res.results[0].status == "NEEDS_REVIEW", res.results[0].status
    assert res.results[0].review_reason == "SOURCE_INCOMPLETE", res.results[0].review_reason


def test_doc_categorical_both_absent_not_applicable():
    chk = _employment_date_check()
    loan = CanonicalLoan(loan_id="LN-DOCDOC-NEITHER", fields={
        "employment_start_date_1003": SourceValue(doc=None),
        "employment_start_date_voe": SourceValue(doc=None),
    })
    res = _run_single(chk, loan)
    assert res.results[0].status == "NOT_APPLICABLE", res.results[0].status


# --- numeric fixture: CD payoff amount vs payoff statement amount ----------
def _payoff_check(check_id="chk-docdoc-payoff", tolerance="0"):
    return Check(id=check_id, name="CD payoff amount agrees with payoff statement",
                 field_name="cd_payoff_amount", compare_field_name="payoff_statement_amount",
                 kind="agree_doc_numeric", severity="CRITICAL", sources=["doc"],
                 tolerance=tolerance,
                 message_fail="CD payoff amount does not match the payoff statement.")


def test_doc_numeric_agreement_produces_pass():
    chk = _payoff_check()
    loan = CanonicalLoan(loan_id="LN-DOCNUM-AGREE", fields={
        "cd_payoff_amount": SourceValue(doc="250000.00"),
        "payoff_statement_amount": SourceValue(doc="250000.00"),
    })
    res = _run_single(chk, loan)
    assert res.results[0].status == "PASS", res.results[0].status


def test_doc_numeric_within_tolerance_produces_pass():
    chk = _payoff_check(tolerance="10.00")
    loan = CanonicalLoan(loan_id="LN-DOCNUM-WITHIN", fields={
        "cd_payoff_amount": SourceValue(doc="250000.00"),
        "payoff_statement_amount": SourceValue(doc="250005.00"),
    })
    res = _run_single(chk, loan)
    assert res.results[0].status == "PASS", res.results[0].status


def test_doc_numeric_outside_tolerance_produces_fail_never_flag():
    chk = _payoff_check(tolerance="0")
    loan = CanonicalLoan(loan_id="LN-DOCNUM-OUTSIDE", fields={
        "cd_payoff_amount": SourceValue(doc="250000.00"),
        "payoff_statement_amount": SourceValue(doc="244545.00"),
    })
    res = _run_single(chk, loan)
    assert res.results[0].status == "FAIL", res.results[0].status
    assert res.results[0].severity == "CRITICAL", res.results[0].severity


def test_doc_numeric_one_side_absent_needs_review_source_incomplete():
    chk = _payoff_check()
    loan = CanonicalLoan(loan_id="LN-DOCNUM-ONESIDE", fields={
        "cd_payoff_amount": SourceValue(doc="250000.00"),
        "payoff_statement_amount": SourceValue(doc=None),
    })
    res = _run_single(chk, loan)
    assert res.results[0].status == "NEEDS_REVIEW", res.results[0].status
    assert res.results[0].review_reason == "SOURCE_INCOMPLETE", res.results[0].review_reason


def test_doc_numeric_both_absent_not_applicable():
    chk = _payoff_check()
    loan = CanonicalLoan(loan_id="LN-DOCNUM-NEITHER", fields={
        "cd_payoff_amount": SourceValue(doc=None),
        "payoff_statement_amount": SourceValue(doc=None),
    })
    res = _run_single(chk, loan)
    assert res.results[0].status == "NOT_APPLICABLE", res.results[0].status


def test_doc_numeric_unspecified_tolerance_needs_review_not_crash():
    # Same honesty guard as agree_numeric/ratio_threshold: the compiler
    # honestly declined to invent a tolerance -- must surface to a human,
    # never crash on Decimal("UNSPECIFIED") and never silently NOT_APPLICABLE.
    chk = _payoff_check(tolerance="UNSPECIFIED")
    loan = CanonicalLoan(loan_id="LN-DOCNUM-UNSPECIFIED", fields={
        "cd_payoff_amount": SourceValue(doc="250000.00"),
        "payoff_statement_amount": SourceValue(doc="250000.00"),
    })
    res = _run_single(chk, loan)
    assert res.results[0].status == "NEEDS_REVIEW", res.results[0].status
    assert res.results[0].review_reason == "UNSPECIFIED_THRESHOLD", res.results[0].review_reason


# --- US2: phase/disposition proof -- FAIL/EXCEPTION, not FLAG --------------
def test_doc_vs_doc_mismatch_phase_is_qc_not_reconcile():
    # _phase_for() is unmodified -- the two new kinds are simply absent from
    # its RECONCILE-inference tuple, so they default to QC for free. Verified
    # directly, not assumed, since this is the mechanism that makes the
    # disposition proof below correct with zero extra dispatch code.
    chk = _employment_date_check()
    loan = CanonicalLoan(loan_id="LN-DOCDOC-PHASE", fields={
        "employment_start_date_1003": SourceValue(doc="03/15/2018"),
        "employment_start_date_voe": SourceValue(doc="03/15/2018"),
    })
    res = _run_single(chk, loan)
    assert res.results[0].phase == "QC", res.results[0].phase


def test_lone_doc_vs_doc_mismatch_drives_disposition_needs_review():
    chk = _employment_date_check()
    loan = CanonicalLoan(loan_id="LN-DOCDOC-DISPOSITION", fields={
        "employment_start_date_1003": SourceValue(doc="03/15/2018"),
        "employment_start_date_voe": SourceValue(doc="05/01/2019"),
    })
    res = _run_single(chk, loan)
    assert len(res.qc_failures) == 1, res.qc_failures
    assert len(res.flags) == 0, res.flags
    assert res.disposition == "NEEDS_REVIEW", res.disposition
    assert res.review_reasons == {"EXCEPTION"}, res.review_reasons
    assert res.auto_cleared is False, res.auto_cleared


# --- referential integrity: compare_field_name resolved too ----------------
def _tiny_catalog():
    return FieldCatalog(catalog_id="t-cat", version=1, entries=[
        FieldCatalogEntry(field_name="employment_start_date_1003", data_type="date",
                          expected_sources=["doc"]),
        FieldCatalogEntry(field_name="employment_start_date_voe", data_type="date",
                          expected_sources=["doc"]),
    ])


def test_referential_integrity_accepts_valid_compare_field_name():
    chk = _employment_date_check()
    rs = Ruleset(ruleset_id="t-ri-ok", version=1, checks=[chk])
    validate_referential_integrity(rs, _tiny_catalog())  # must not raise


def test_referential_integrity_rejects_bad_compare_field_name():
    chk = Check(id="chk-bad-compare", name="Bad compare field",
               field_name="employment_start_date_1003",
               compare_field_name="this_field_does_not_exist_anywhere",
               kind="agree_doc_categorical", severity="CRITICAL", normalizer="identity")
    rs = Ruleset(ruleset_id="t-ri-bad", version=1, checks=[chk])
    try:
        validate_referential_integrity(rs, _tiny_catalog())
        assert False, "expected ReferentialIntegrityError"
    except ReferentialIntegrityError as e:
        assert "this_field_does_not_exist_anywhere" in str(e)


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
