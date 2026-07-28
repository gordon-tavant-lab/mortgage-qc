"""
004 -- loan disposition (composition layer).

Composes a loan's full RunResult into a binary Disposition (AUTO_CLEARED /
NEEDS_REVIEW) plus an open, multi-label review_reasons tag set naming *why*.
Unlike 003c (zero engine touch), this feature makes one small, deliberate
addition to engine.py: CheckResult.review_reason, tagged generically by
phase+status (not per check-kind) immediately after _eval_check's main
dispatch, plus one line in the existing confidence-gate block.

US1: every reason a check needs review is a distinct, inspectable tag, and a
loan's review_reasons is the correct set (including multi-label when more
than one concern is present).
US2: a reconcile FLAG never contributes a tag, at any combination -- the
two-step model's safety promise (Principle V) holds through the new
mechanism.
US3: the tag vocabulary is genuinely open -- a tag the aggregation logic has
never seen before surfaces correctly with zero changes to review_reasons's
own implementation, and repeated tags across checks dedupe to one.

Run from p0/:  python -m pytest tests/test_loan_disposition.py -v
Python 3.9 compatible.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "eval_synth"))

from qc_engine import run
from qc_engine.engine import CheckResult, RunResult, DEFAULT_CONFIDENCE_FLOOR
from qc_engine.model import CanonicalLoan, SourceValue
from qc_engine.ruleset import Check, Ruleset
import generator as G


def _run_single(chk, loan):
    rs = Ruleset(ruleset_id=f"t-{chk.id}", version=1, checks=[chk])
    return run(loan, rs)


# --- T002: QC-phase FAIL/WARNING -> EXCEPTION -------------------------------
def _exception_check():
    return Check(id="chk-disp-exception", name="Note signed (disposition proof)",
                 field_name="note_signed", kind="predicate", predicate="is_true",
                 severity="CRITICAL", sources=["doc"],
                 message_fail="Promissory note is unsigned.")


def test_qc_failure_tags_exception():
    chk = _exception_check()
    loan = CanonicalLoan(loan_id="LN-DISP-EXCEPTION",
                         fields={"note_signed": SourceValue(doc=False)})
    res = _run_single(chk, loan)
    assert res.results[0].review_reason == "EXCEPTION"
    assert res.review_reasons == {"EXCEPTION"}
    assert res.disposition == "NEEDS_REVIEW"


# --- T003: confidence-gate downgrade -> LOW_CONFIDENCE ----------------------
def _credit_floor_check():
    return Check(id="chk-disp-lowconf", name="Credit score floor (disposition proof)",
                 field_name="credit_score", kind="ratio_threshold",
                 severity="CRITICAL", ratio="field_value",
                 threshold="500", operator=">=")


def test_confidence_withheld_tags_low_confidence():
    chk = _credit_floor_check()
    loan = CanonicalLoan(loan_id="LN-DISP-LOWCONF",
                         fields={"credit_score": SourceValue(
                             doc=620, doc_confidence=DEFAULT_CONFIDENCE_FLOOR - 0.01)})
    res = _run_single(chk, loan)
    assert res.results[0].status == "NEEDS_REVIEW", res.results[0].status
    assert res.results[0].review_reason == "LOW_CONFIDENCE"
    assert res.review_reasons == {"LOW_CONFIDENCE"}
    assert res.disposition == "NEEDS_REVIEW"


# --- T004: reconcile one-side-absent -> SOURCE_INCOMPLETE -------------------
def _ssn_check():
    return Check(id="chk-disp-ssn", name="SSN agreement (disposition proof)",
                 field_name="borrower_ssn", kind="agree_categorical",
                 severity="CRITICAL", sources=["doc", "los"],
                 normalizer="ssn_last4")


def test_reconcile_one_side_absent_tags_source_incomplete():
    chk = _ssn_check()
    loan = CanonicalLoan(loan_id="LN-DISP-INCOMPLETE",
                         fields={"borrower_ssn": SourceValue(doc="123-45-6789", sources={})})
    res = _run_single(chk, loan)
    assert res.results[0].status == "NEEDS_REVIEW", res.results[0].status
    assert res.results[0].review_reason == "SOURCE_INCOMPLETE"
    assert res.review_reasons == {"SOURCE_INCOMPLETE"}
    assert res.disposition == "NEEDS_REVIEW"


# --- T005: multi-label -- two distinct reasons on one loan simultaneously --
def test_multiple_reasons_are_multi_label_not_precedence():
    rs = Ruleset(ruleset_id="t-multi-reason", version=1,
                 checks=[_exception_check(), _credit_floor_check()])
    loan = CanonicalLoan(
        loan_id="LN-DISP-MULTI",
        fields={
            "note_signed": SourceValue(doc=False),
            "credit_score": SourceValue(doc=620, doc_confidence=DEFAULT_CONFIDENCE_FLOOR - 0.01),
        },
    )
    res = run(loan, rs)
    assert res.review_reasons == {"EXCEPTION", "LOW_CONFIDENCE"}
    assert res.disposition == "NEEDS_REVIEW"


# --- T006: clean loan -> empty review_reasons -------------------------------
def test_clean_loan_has_empty_review_reasons():
    chk = _exception_check()
    loan = CanonicalLoan(loan_id="LN-DISP-CLEAN",
                         fields={"note_signed": SourceValue(doc=True)})
    res = _run_single(chk, loan)
    assert res.review_reasons == set()
    assert res.disposition == "AUTO_CLEARED"


# --- T012/T013: US2 -- FLAG(s) alone never tag, never block auto-clear -----
def test_single_flag_alone_is_auto_cleared_no_reasons():
    chk = _ssn_check()
    truth, sources = "123-45-6789", {"los": "987-65-4321"}
    G.assert_independently_constructed(truth, sources, expect_divergent_keys=["los"])
    loan = CanonicalLoan(loan_id="LN-DISP-FLAG-ONLY",
                         fields={"borrower_ssn": SourceValue(doc=truth, sources=sources)})
    res = _run_single(chk, loan)
    assert res.results[0].status == "FLAG", res.results[0].status
    assert res.results[0].review_reason is None
    assert res.review_reasons == set()
    assert res.disposition == "AUTO_CLEARED"


def test_multiple_flags_alone_still_auto_cleared_no_reasons():
    rate_chk = Check(id="chk-disp-rate", name="Note rate agreement (disposition proof)",
                      field_name="note_rate", kind="agree_numeric",
                      severity="CRITICAL", sources=["doc", "los"], tolerance="0.001")
    ssn_chk = _ssn_check()
    rs = Ruleset(ruleset_id="t-multi-flag", version=1, checks=[ssn_chk, rate_chk])

    ssn_truth, ssn_sources = "123-45-6789", {"los": "987-65-4321"}
    G.assert_independently_constructed(ssn_truth, ssn_sources, expect_divergent_keys=["los"])
    rate_truth, rate_sources = "6.250", {"los": "6.375"}
    G.assert_independently_constructed(rate_truth, rate_sources, expect_divergent_keys=["los"])

    loan = CanonicalLoan(
        loan_id="LN-DISP-MULTI-FLAG",
        fields={
            "borrower_ssn": SourceValue(doc=ssn_truth, sources=ssn_sources),
            "note_rate": SourceValue(doc=rate_truth, sources=rate_sources),
        },
    )
    res = run(loan, rs)
    assert len(res.flags) == 2, res.flags
    assert res.review_reasons == set()
    assert res.disposition == "AUTO_CLEARED"


# --- T014: FLAG + genuine QC failure -> reasons are EXCEPTION only ---------
def test_flag_plus_qc_failure_tags_exception_only():
    rs = Ruleset(ruleset_id="t-flag-plus-exception", version=1,
                 checks=[_ssn_check(), _exception_check()])
    ssn_truth, ssn_sources = "123-45-6789", {"los": "987-65-4321"}
    G.assert_independently_constructed(ssn_truth, ssn_sources, expect_divergent_keys=["los"])
    loan = CanonicalLoan(
        loan_id="LN-DISP-FLAG-PLUS-EXCEPTION",
        fields={
            "borrower_ssn": SourceValue(doc=ssn_truth, sources=ssn_sources),
            "note_signed": SourceValue(doc=False),
        },
    )
    res = run(loan, rs)
    assert len(res.flags) == 1, res.flags
    assert res.review_reasons == {"EXCEPTION"}
    assert res.disposition == "NEEDS_REVIEW"


# --- T015/T016: US3 -- the tag vocabulary is genuinely open -----------------
def test_never_seen_before_tag_surfaces_with_zero_aggregation_changes():
    # Direct CheckResult construction -- simulates a hypothetical future
    # check-kind, bypassing _eval_check entirely. review_reasons must still
    # pick it up correctly: proves the aggregator is generic over tag
    # identity, not a hardcoded switch (SC-004).
    novel = CheckResult(check_id="future-chk", check_name="Future check",
                        severity="CRITICAL", status="FAIL", field_name="x",
                        review_reason="FUTURE_TAG_NEVER_SEEN_BEFORE")
    res = RunResult(loan_id="LN-DISP-FUTURE", ruleset_id="t-future", ruleset_version=1,
                    ruleset_sha256="deadbeef", engine_version="v1", results=[novel])
    assert res.review_reasons == {"FUTURE_TAG_NEVER_SEEN_BEFORE"}
    assert res.disposition == "NEEDS_REVIEW"


def test_repeated_tag_across_checks_dedupes_to_one():
    r1 = CheckResult(check_id="c1", check_name="Check 1", severity="CRITICAL",
                     status="FAIL", field_name="x", phase="QC", review_reason="EXCEPTION")
    r2 = CheckResult(check_id="c2", check_name="Check 2", severity="CRITICAL",
                     status="FAIL", field_name="y", phase="QC", review_reason="EXCEPTION")
    res = RunResult(loan_id="LN-DISP-DEDUP", ruleset_id="t-dedup", ruleset_version=1,
                    ruleset_sha256="deadbeef", engine_version="v1", results=[r1, r2])
    assert res.review_reasons == {"EXCEPTION"}
    assert len(res.review_reasons) == 1


# --- T017: auto_cleared <=> disposition == AUTO_CLEARED, across every case -
def test_auto_cleared_matches_disposition_across_all_constructed_cases():
    cases = []

    chk = _exception_check()
    cases.append(_run_single(chk, CanonicalLoan(
        loan_id="LN-EQUIV-EXCEPTION", fields={"note_signed": SourceValue(doc=False)})))

    lowconf_chk = _credit_floor_check()
    cases.append(_run_single(lowconf_chk, CanonicalLoan(
        loan_id="LN-EQUIV-LOWCONF",
        fields={"credit_score": SourceValue(doc=620, doc_confidence=0.5)})))

    ssn_chk = _ssn_check()
    cases.append(_run_single(ssn_chk, CanonicalLoan(
        loan_id="LN-EQUIV-INCOMPLETE",
        fields={"borrower_ssn": SourceValue(doc="123-45-6789", sources={})})))

    cases.append(_run_single(chk, CanonicalLoan(
        loan_id="LN-EQUIV-CLEAN", fields={"note_signed": SourceValue(doc=True)})))

    ssn_truth, ssn_sources = "123-45-6789", {"los": "987-65-4321"}
    G.assert_independently_constructed(ssn_truth, ssn_sources, expect_divergent_keys=["los"])
    cases.append(_run_single(ssn_chk, CanonicalLoan(
        loan_id="LN-EQUIV-FLAG-ONLY",
        fields={"borrower_ssn": SourceValue(doc=ssn_truth, sources=ssn_sources)})))

    for res in cases:
        assert (res.auto_cleared is True) == (res.disposition == "AUTO_CLEARED"), (
            res.loan_id, res.auto_cleared, res.disposition)


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
