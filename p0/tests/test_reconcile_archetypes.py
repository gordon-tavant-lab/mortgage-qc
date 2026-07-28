"""
003c -- reconcile check engine, proven at representative INACCURATE/MISMATCH-
archetype scale.

Unlike 003a/003b, this feature fixes no bug and closes no vocabulary gap --
agree_categorical/agree_numeric are already fully implemented and proven
generically by 001b (test_p0.py's test_reconcile_check_compares_independently_
populated_sources, test_mismo_only_loan_resolves_system_value_unchanged,
test_new_named_source_readable_with_zero_engine_changes) and exercised by
demo_ruleset()'s 6 hand-authored checks. Every test below is a PROOF test,
expected to pass against today's engine.py unmodified -- not a red-then-green
fix (spec.md's own framing).

US1: the mechanism holds at real archetype scale, anchored on the one real,
structurally-clean, doc-vs-system sampled row 002a found (reconcile-01, an
SSN discrepancy -- p0/experiment_002a/artifacts/sampled_rows.json), plus
representative agree_categorical/agree_numeric pairs and absent-value cases.

US2: the FLAG-vs-FAIL / RECONCILE-vs-QC phase partition holds safely in BOTH
directions under a mixed ruleset -- a reconcile FLAG must never leak into
qc_failures or block auto_cleared; a genuine QC failure (predicate or
ratio_threshold) must never be misclassified as a FLAG.

Explicitly NOT covered here (spec.md Edge Cases/Assumptions, output/ROADMAP.md
Tension #5): the doc-vs-doc majority of real MISMATCH conditions (two
independent DOCUMENT values, e.g. 1003 vs VOE) -- the current SourceValue
model has one doc slot + named system sources, no slot for a second document.
Also not covered: reconcile-00 (ambiguous comparison structure) and the
INACCURATE archetype's completeness-flavored examples -- open compiler-
classification questions, not resolved by this engine spec.

Run from p0/:  python -m pytest tests/test_reconcile_archetypes.py -v
Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "eval_synth"))

from qc_engine import run
from qc_engine.model import CanonicalLoan, SourceValue
from qc_engine.ruleset import Check, Ruleset
import generator as G

SAMPLED_ROWS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiment_002a", "artifacts", "sampled_rows.json")


def _load_reconcile_01():
    """T002: reads the real reconcile-01 row 002a sampled directly from
    demo/rules/*.xlsx -- no fabricated condition text."""
    with open(SAMPLED_ROWS_PATH) as f:
        rows = json.load(f)["rows"]
    row = next(r for r in rows if r.get("row_id") == "reconcile-01")
    assert row["archetype_id"] == "MISMATCH"
    assert row["engine_kind"] == "agree_categorical"
    assert "Social Security number" in row["defect_text"]
    return row


RECONCILE_01 = _load_reconcile_01()


def _run_single(chk, loan):
    rs = Ruleset(ruleset_id=f"t-{chk.id}", version=1, checks=[chk])
    return run(loan, rs)


def _ssn_check(check_id="chk-recon-ssn"):
    """Mirrors demo_ruleset()'s chk-borrower-ssn (field_name="borrower_ssn",
    normalizer="ssn_last4") under an independent id -- proof coverage for
    this feature must not depend on ruleset_demo.py's digest-pinned content."""
    return Check(id=check_id, name=RECONCILE_01["defect_text"],
                 field_name="borrower_ssn", kind="agree_categorical",
                 severity="CRITICAL", sources=["doc", "los"],
                 normalizer="ssn_last4",
                 message_fail="SSN discrepancy between document and system.")


# --- T003: SSN agreement (the real reconcile-01 condition, doc-vs-system) --
def _assert_ssn_agreement_correct():
    chk = _ssn_check()
    loan = CanonicalLoan(loan_id="LN-SSN-AGREE",
                         fields={"borrower_ssn": SourceValue(
                             doc="123-45-6789", sources={"los": "123-45-6789"})})
    res = _run_single(chk, loan)
    assert res.results[0].status == "PASS", res.results[0].status
    return res


def test_ssn_agreement_produces_pass():
    _assert_ssn_agreement_correct()


# --- T004: SSN genuine divergence -- FLAG, never FAIL ----------------------
def _assert_ssn_divergence_correct():
    chk = _ssn_check()
    truth = "123-45-6789"
    sources = {"los": "987-65-4321"}
    # Independence-guard discipline (001b's own pattern): confirm the
    # divergence is real, not a mutation that left sources unchanged.
    G.assert_independently_constructed(truth, sources, expect_divergent_keys=["los"])
    loan = CanonicalLoan(loan_id="LN-SSN-DIVERGE",
                         fields={"borrower_ssn": SourceValue(doc=truth, sources=sources)})
    res = _run_single(chk, loan)
    assert res.results[0].status == "FLAG", res.results[0].status
    assert res.results[0].severity == "INFO", res.results[0].severity
    return res


def test_ssn_genuine_divergence_produces_flag_never_fail():
    _assert_ssn_divergence_correct()


# --- T005: representative agree_numeric pair, at/within/outside tolerance --
def _rate_check(check_id="chk-recon-rate"):
    """Mirrors demo_ruleset()'s chk-note-rate (agree_numeric, tolerance=0.001)."""
    return Check(id=check_id, name="Note rate agreement (reconcile proof)",
                 field_name="note_rate", kind="agree_numeric",
                 severity="CRITICAL", sources=["doc", "los"],
                 tolerance="0.001",
                 message_fail="Note rate differs beyond tolerance.")


def _assert_rate_agree_numeric_correct():
    chk = _rate_check()
    at_loan = CanonicalLoan(loan_id="LN-RATE-EXACT",
                            fields={"note_rate": SourceValue(
                                doc="6.250", sources={"los": "6.250"})})
    within_loan = CanonicalLoan(loan_id="LN-RATE-WITHIN",
                                fields={"note_rate": SourceValue(
                                    doc="6.250", sources={"los": "6.2505"})})
    outside_truth, outside_sources = "6.250", {"los": "6.375"}
    G.assert_independently_constructed(outside_truth, outside_sources,
                                        expect_divergent_keys=["los"])
    outside_loan = CanonicalLoan(loan_id="LN-RATE-OUTSIDE",
                                 fields={"note_rate": SourceValue(
                                     doc=outside_truth, sources=outside_sources)})
    at_res = _run_single(chk, at_loan)
    within_res = _run_single(chk, within_loan)
    outside_res = _run_single(chk, outside_loan)
    assert at_res.results[0].status == "PASS", at_res.results[0].status
    assert within_res.results[0].status == "PASS", within_res.results[0].status
    assert outside_res.results[0].status == "FLAG", outside_res.results[0].status
    assert outside_res.results[0].severity == "INFO", outside_res.results[0].severity
    return outside_res


def test_rate_agree_numeric_correctness_at_within_outside_tolerance():
    _assert_rate_agree_numeric_correct()


# --- T006: one-side-absent (NEEDS_REVIEW) / both-absent (NOT_APPLICABLE) ---
def test_reconcile_one_side_absent_needs_review():
    chk = _ssn_check()
    loan = CanonicalLoan(loan_id="LN-SSN-NOSSYS",
                         fields={"borrower_ssn": SourceValue(doc="123-45-6789", sources={})})
    res = _run_single(chk, loan)
    assert res.results[0].status == "NEEDS_REVIEW", res.results[0].status


def test_reconcile_both_absent_not_applicable():
    chk = _ssn_check()
    loan = CanonicalLoan(loan_id="LN-SSN-NEITHER",
                         fields={"borrower_ssn": SourceValue(doc=None, sources={})})
    res = _run_single(chk, loan)
    assert res.results[0].status == "NOT_APPLICABLE", res.results[0].status


# --- T007-T010: US2, FLAG-vs-FAIL partition under a mixed ruleset ----------
def _note_signed_check(check_id="chk-recon-note-signed"):
    """Mirrors demo_ruleset()'s chk-note-signed (predicate, is_true)."""
    return Check(id=check_id, name="Promissory note signed",
                 field_name="note_signed", kind="predicate", predicate="is_true",
                 severity="CRITICAL", sources=["doc"],
                 message_fail="Promissory note is unsigned.")


def _ltv_check(check_id="chk-recon-ltv-95"):
    """Mirrors demo_ruleset()'s chk-ltv-max (ratio_threshold, ltv)."""
    return Check(id=check_id, name="LTV within program max (95%)",
                 field_name="", kind="ratio_threshold", ratio="ltv",
                 severity="CRITICAL", threshold="95", operator="<=")


def _mixed_ruleset():
    """T007: one reconcile check + one predicate QC check + one ratio_threshold
    QC check -- both field_name values (borrower_ssn, note_signed) are
    already-registered p0-seed-catalog fields, so this ruleset passes
    referential integrity cleanly without inventing new catalog entries."""
    return Ruleset(ruleset_id="rs-reconcile-mixed-proof", version=1, checks=[
        _ssn_check("chk-mixed-ssn"),
        _note_signed_check("chk-mixed-note-signed"),
        _ltv_check("chk-mixed-ltv"),
    ])


def _referential_integrity_ok(ruleset):
    from qc_engine.catalog import load_catalog, validate_referential_integrity
    catalog_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "qc_engine", "field_catalog.json")
    validate_referential_integrity(ruleset, load_catalog(catalog_path))  # must not raise


def test_mixed_ruleset_passes_referential_integrity():
    _referential_integrity_ok(_mixed_ruleset())


def test_divergence_only_flags_never_blocks_autoclear():
    # T008: reconcile diverges, everything else clean -- flags non-empty,
    # qc_failures empty, auto_cleared True.
    rs = _mixed_ruleset()
    loan = CanonicalLoan(
        loan_id="LN-MIXED-DIVERGENCE-ONLY",
        fields={
            "borrower_ssn": SourceValue(doc="123-45-6789", sources={"los": "987-65-4321"}),
            "note_signed": SourceValue(doc=True),
        },
        facts={"loan_amount": "300000.00", "property_value": "350000.00"},
    )
    res = run(loan, rs)
    assert len(res.flags) == 1, res.flags
    assert len(res.qc_failures) == 0, res.qc_failures
    assert res.auto_cleared is True


def test_qc_failure_only_never_read_as_flag():
    # T009: QC (predicate) fails, reconcile clean -- qc_failures non-empty,
    # flags empty, auto_cleared False.
    rs = _mixed_ruleset()
    loan = CanonicalLoan(
        loan_id="LN-MIXED-QC-FAILURE-ONLY",
        fields={
            "borrower_ssn": SourceValue(doc="123-45-6789", sources={"los": "123-45-6789"}),
            "note_signed": SourceValue(doc=False),
        },
        facts={"loan_amount": "300000.00", "property_value": "350000.00"},
    )
    res = run(loan, rs)
    assert len(res.qc_failures) == 1, res.qc_failures
    assert len(res.flags) == 0, res.flags
    assert res.auto_cleared is False


def test_both_present_surface_in_separate_buckets_simultaneously():
    # T010: divergence AND QC failure together -- both surface, auto_cleared
    # False (the QC failure alone is sufficient; the FLAG is not what blocks it).
    rs = _mixed_ruleset()
    loan = CanonicalLoan(
        loan_id="LN-MIXED-BOTH",
        fields={
            "borrower_ssn": SourceValue(doc="123-45-6789", sources={"los": "987-65-4321"}),
            "note_signed": SourceValue(doc=False),
        },
        facts={"loan_amount": "300000.00", "property_value": "350000.00"},
    )
    res = run(loan, rs)
    assert len(res.flags) == 1, res.flags
    assert len(res.qc_failures) == 1, res.qc_failures
    assert res.auto_cleared is False


# --- T011: zero-leak at scale, both directions (spec.md SC-003/004) --------
def test_zero_reconcile_flags_leak_into_qc_failures_across_batch():
    # Every genuine-divergence fixture from US1 (T004/T005/borrower_ssn again
    # here) run through the mixed ruleset with the QC side clean -- confirm
    # none of them ever produces a qc_failure or blocks auto_cleared.
    rs = _mixed_ruleset()
    divergent_loans = [
        CanonicalLoan(
            loan_id="LN-BATCH-SSN-DIVERGE",
            fields={
                "borrower_ssn": SourceValue(doc="123-45-6789", sources={"los": "987-65-4321"}),
                "note_signed": SourceValue(doc=True),
            },
            facts={"loan_amount": "300000.00", "property_value": "350000.00"},
        ),
        CanonicalLoan(
            loan_id="LN-BATCH-SSN-DIVERGE-2",
            fields={
                "borrower_ssn": SourceValue(doc="111-22-3333", sources={"los": "444-55-6666"}),
                "note_signed": SourceValue(doc=True),
            },
            facts={"loan_amount": "300000.00", "property_value": "350000.00"},
        ),
    ]
    for loan in divergent_loans:
        res = run(loan, rs)
        assert len(res.qc_failures) == 0, (loan.loan_id, res.qc_failures)
        assert res.auto_cleared is True, (loan.loan_id, "a reconcile FLAG blocked auto_cleared")


def test_zero_qc_failures_misclassified_as_flags_across_batch():
    # The inverse direction: genuine QC failures of BOTH kinds this feature
    # touches (predicate, ratio_threshold) reconciled cleanly -- confirm
    # neither is ever misread as an informational flags-only condition.
    rs = _mixed_ruleset()
    unsigned_loan = CanonicalLoan(
        loan_id="LN-BATCH-UNSIGNED",
        fields={
            "borrower_ssn": SourceValue(doc="123-45-6789", sources={"los": "123-45-6789"}),
            "note_signed": SourceValue(doc=False),
        },
        facts={"loan_amount": "300000.00", "property_value": "350000.00"},
    )
    ltv_over_loan = CanonicalLoan(
        loan_id="LN-BATCH-LTV-OVER",
        fields={
            "borrower_ssn": SourceValue(doc="123-45-6789", sources={"los": "123-45-6789"}),
            "note_signed": SourceValue(doc=True),
        },
        facts={"loan_amount": "340000.00", "property_value": "350000.00"},
    )
    for loan in (unsigned_loan, ltv_over_loan):
        res = run(loan, rs)
        assert len(res.qc_failures) == 1, (loan.loan_id, res.qc_failures)
        assert len(res.flags) == 0, (loan.loan_id, res.flags)
        assert res.auto_cleared is False, (loan.loan_id, res.auto_cleared)


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
