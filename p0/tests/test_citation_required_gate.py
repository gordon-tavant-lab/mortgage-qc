"""
Finding #5 -- the citation-required gate.

catalog.py's FieldCatalogEntry.citation_required (True for 380 of 385 real
entries in field_catalog.json) was never read anywhere in engine.py: a PASS
on a citation-required field auto-cleared even with no document citation to
point a regulator/reviewer at -- an opaque trace, exactly what the
constitution's Quality Gates section forbids ("every doc-sourced value is
traceable... not an opaque trace").

Mirrors the existing confidence-gate tests' shape exactly: a tiny inline
predicate Check + CanonicalLoan/SourceValue fixture, run() through the real
engine, no mocking framework.

Run from p0/:  python -m pytest tests/test_citation_required_gate.py -v
Python 3.9 compatible.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qc_engine import run
from qc_engine.catalog import FieldCatalog, FieldCatalogEntry
from qc_engine.model import CanonicalLoan, DocCitation, SourceValue
from qc_engine.ruleset import Check, Ruleset


def _presence_check(field_name: str, check_id: str = "chk-citation-gate") -> Check:
    # predicate/is_present: PASS whenever the field's doc value is non-empty
    # -- the simplest kind that can reach a bare PASS with res.citation
    # already populated (or not) straight from _eval_check's unconditional
    # citation = sv.citation.to_dict() ... population point, no other
    # kind-specific branch needed to exercise the gate.
    return Check(id=check_id, name="Field is present", field_name=field_name,
                 kind="predicate", severity="CRITICAL", predicate="is_present")


def _catalog(citation_required: bool) -> FieldCatalog:
    return FieldCatalog(catalog_id="t-citation-cat", version=1, entries=[
        FieldCatalogEntry(field_name="gift_letter_amount", data_type="string",
                          expected_sources=["doc"], citation_required=citation_required),
    ])


def _run_single(chk, loan, catalog=None):
    rs = Ruleset(ruleset_id=f"t-{chk.id}", version=1, checks=[chk])
    return run(loan, rs, catalog=catalog)


def test_citation_required_missing_citation_downgrades_to_needs_review():
    chk = _presence_check("gift_letter_amount")
    loan = CanonicalLoan(loan_id="LN-CITATION-MISSING", fields={
        "gift_letter_amount": SourceValue(doc="5000.00"),  # no citation=...
    })
    res = _run_single(chk, loan, catalog=_catalog(citation_required=True))
    result = res.results[0]
    assert result.status == "NEEDS_REVIEW", result.status
    assert result.review_reason == "MISSING_CITATION", result.review_reason


def test_citation_required_with_citation_present_stays_pass():
    chk = _presence_check("gift_letter_amount")
    loan = CanonicalLoan(loan_id="LN-CITATION-PRESENT", fields={
        "gift_letter_amount": SourceValue(
            doc="5000.00",
            citation=DocCitation(doc_name="gift_letter.pdf", page_num=1,
                                 segment_snippet="Gift amount: $5,000.00"),
        ),
    })
    res = _run_single(chk, loan, catalog=_catalog(citation_required=True))
    result = res.results[0]
    assert result.status == "PASS", result.status
    assert result.review_reason is None, result.review_reason


def test_citation_not_required_missing_citation_stays_pass():
    chk = _presence_check("gift_letter_amount")
    loan = CanonicalLoan(loan_id="LN-CITATION-NOT-REQUIRED", fields={
        "gift_letter_amount": SourceValue(doc="5000.00"),  # no citation
    })
    res = _run_single(chk, loan, catalog=_catalog(citation_required=False))
    result = res.results[0]
    assert result.status == "PASS", result.status
    assert result.review_reason is None, result.review_reason


def test_no_catalog_passed_is_a_total_no_op_backward_compat():
    # The key backward-compatibility proof: every existing caller that never
    # passes catalog= (the overwhelming majority, per this feature's own
    # scope note) must see zero behavior change -- same field, same missing
    # citation, but catalog=None (run()'s default) never triggers the gate.
    chk = _presence_check("gift_letter_amount")
    loan = CanonicalLoan(loan_id="LN-CITATION-NO-CATALOG", fields={
        "gift_letter_amount": SourceValue(doc="5000.00"),  # no citation
    })
    res = _run_single(chk, loan)  # catalog defaults to None
    result = res.results[0]
    assert result.status == "PASS", result.status
    assert result.review_reason is None, result.review_reason


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
