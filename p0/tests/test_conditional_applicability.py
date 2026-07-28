"""
002e -- conditional-applicability gating (`Check.applies_if`).

Covers spec.md User Story 1's six Acceptance Scenarios (the engine gate
itself) plus SC-001 (the real, SME-confirmed loan 01 gift-fund case) and
SC-004 (referential integrity). `applies_if`'s *sourcing* mechanism is
002f's concern (`test_ontology_extraction.py`); this file only tests
consumption -- translating an already-decided condition list into engine
behavior.

Run from p0/:  python -m pytest tests/test_conditional_applicability.py -v
Python 3.9 compatible.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_P0 = os.path.dirname(_HERE)
if _P0 not in sys.path:
    sys.path.insert(0, _P0)
_FROM_DOCS = os.path.join(_P0, "fixtures", "from_docs")
if _FROM_DOCS not in sys.path:
    sys.path.insert(0, _FROM_DOCS)

import pytest  # noqa: E402

from qc_engine import run  # noqa: E402
from qc_engine.catalog import FieldCatalog, FieldCatalogEntry, ReferentialIntegrityError, \
    validate_referential_integrity  # noqa: E402
from qc_engine.model import CanonicalLoan, SourceValue  # noqa: E402
from qc_engine.ruleset import Check, Ruleset  # noqa: E402
from fixture_loader import load_canonical_loan  # noqa: E402

LOAN_01_FIXTURE = os.path.join(_FROM_DOCS, "loan_01.json")


def _run_single(chk: Check, loan: CanonicalLoan):
    rs = Ruleset(ruleset_id=f"t-{chk.id}", version=1, checks=[chk])
    return run(loan, rs)


def _gift_check(applies_if):
    return Check(
        id="gift-fund-requirements-met", name="Gift fund requirements met",
        field_name="gift_documentation_complete", kind="predicate", predicate="is_true",
        severity="CRITICAL", applies_if=applies_if,
        message_fail="Gift fund documentation is incomplete.",
    )


# --- Acceptance Scenario 1: definite non-match -> NOT_APPLICABLE -----------

def test_applies_if_false_condition_resolves_not_applicable():
    chk = _gift_check([{"field_name": "gift_funds_used", "operator": "==", "value": "true"}])
    loan = CanonicalLoan(loan_id="LN-AS1", fields={
        "gift_funds_used": SourceValue(doc="false"),
        "gift_documentation_complete": SourceValue(doc=True),
    })
    result = _run_single(chk, loan)
    res = result.results[0]
    assert res.status == "NOT_APPLICABLE"
    assert res.review_reason is None  # NOT_APPLICABLE never carries a review reason


# --- Acceptance Scenario 2: condition holds -> normal kind evaluation ------

def test_applies_if_true_condition_evaluates_normally():
    chk = _gift_check([{"field_name": "gift_funds_used", "operator": "==", "value": "true"}])
    loan = CanonicalLoan(loan_id="LN-AS2", fields={
        "gift_funds_used": SourceValue(doc="true"),
        "gift_documentation_complete": SourceValue(doc=True),
    })
    result = _run_single(chk, loan)
    res = result.results[0]
    assert res.status == "PASS"  # predicate is_true, doc=True -> PASS, unaffected by the gate

    # And the FAIL side of the same gate-passes path, to prove the gate
    # doesn't silently change kind-dispatch outcomes either direction.
    loan_fail = CanonicalLoan(loan_id="LN-AS2-fail", fields={
        "gift_funds_used": SourceValue(doc="true"),
        "gift_documentation_complete": SourceValue(doc=False),
    })
    result_fail = _run_single(chk, loan_fail)
    assert result_fail.results[0].status == "FAIL"


# --- Acceptance Scenario 3: applies_if=None -> unchanged behavior ----------

def test_applies_if_none_is_unconditional_unchanged():
    chk = _gift_check(None)
    loan = CanonicalLoan(loan_id="LN-AS3", fields={
        "gift_documentation_complete": SourceValue(doc=True),
    })
    result = _run_single(chk, loan)
    assert result.results[0].status == "PASS"


# --- Acceptance Scenario 4: precondition field unknown -> NEEDS_REVIEW -----

def test_applies_if_unknown_field_resolves_needs_review():
    chk = _gift_check([{"field_name": "gift_funds_used", "operator": "==", "value": "true"}])
    loan = CanonicalLoan(loan_id="LN-AS4", fields={
        "gift_documentation_complete": SourceValue(doc=True),
        # gift_funds_used deliberately absent -- genuinely unknown, not false.
    })
    result = _run_single(chk, loan)
    res = result.results[0]
    assert res.status == "NEEDS_REVIEW"
    assert res.review_reason == "APPLICABILITY_UNKNOWN"


def test_definite_failure_takes_priority_over_unknown_elsewhere():
    """FR-003's ordering: a definite non-match on ANY condition wins over an
    unknown field on another condition, regardless of which was declared
    first."""
    chk = _gift_check([
        {"field_name": "unknown_field", "operator": "==", "value": "x"},
        {"field_name": "gift_funds_used", "operator": "==", "value": "true"},
    ])
    loan = CanonicalLoan(loan_id="LN-PRIORITY", fields={
        "gift_documentation_complete": SourceValue(doc=True),
        "gift_funds_used": SourceValue(doc="false"),  # definite non-match
        # unknown_field deliberately absent
    })
    result = _run_single(chk, loan)
    res = result.results[0]
    assert res.status == "NOT_APPLICABLE"  # not NEEDS_REVIEW


# --- Acceptance Scenario 5: compound (AND-combined) conditions -------------

def test_compound_applies_if_all_must_hold():
    chk = _gift_check([
        {"field_name": "occupancy", "operator": "==", "value": "primary_residence"},
        {"field_name": "property_type", "operator": "==", "value": "manufactured"},
    ])
    both_hold = CanonicalLoan(loan_id="LN-AS5-both", fields={
        "gift_documentation_complete": SourceValue(doc=True),
        "occupancy": SourceValue(doc="primary_residence"),
        "property_type": SourceValue(doc="manufactured"),
    })
    assert _run_single(chk, both_hold).results[0].status == "PASS"

    one_fails = CanonicalLoan(loan_id="LN-AS5-one-fails", fields={
        "gift_documentation_complete": SourceValue(doc=True),
        "occupancy": SourceValue(doc="primary_residence"),
        "property_type": SourceValue(doc="single_family"),  # fails the 2nd condition
    })
    assert _run_single(chk, one_fails).results[0].status == "NOT_APPLICABLE"


# --- Acceptance Scenario 6: `in` and `between` operators -------------------

def test_in_operator_set_membership():
    chk = _gift_check([{"field_name": "property_type", "operator": "in", "value": "condo|co_op|pud"}])
    matches = CanonicalLoan(loan_id="LN-IN-match", fields={
        "gift_documentation_complete": SourceValue(doc=True),
        "property_type": SourceValue(doc="co_op"),
    })
    assert _run_single(chk, matches).results[0].status == "PASS"

    no_match = CanonicalLoan(loan_id="LN-IN-nomatch", fields={
        "gift_documentation_complete": SourceValue(doc=True),
        "property_type": SourceValue(doc="single_family"),
    })
    assert _run_single(chk, no_match).results[0].status == "NOT_APPLICABLE"


def test_between_operator_range():
    chk = _gift_check([{"field_name": "units", "operator": "between", "value": "3|4"}])
    in_range = CanonicalLoan(loan_id="LN-BETWEEN-in", fields={
        "gift_documentation_complete": SourceValue(doc=True),
        "units": SourceValue(doc="3"),
    })
    assert _run_single(chk, in_range).results[0].status == "PASS"

    out_of_range = CanonicalLoan(loan_id="LN-BETWEEN-out", fields={
        "gift_documentation_complete": SourceValue(doc=True),
        "units": SourceValue(doc="2"),
    })
    assert _run_single(chk, out_of_range).results[0].status == "NOT_APPLICABLE"


# --- SC-001: the real, SME-confirmed loan 01 gift-fund case ----------------

def test_loan_01_real_facts_gift_fund_check_resolves_not_applicable():
    """The concrete defect this feature exists to fix (spec.md preamble):
    loan 01 used no gift funds; before this feature the gift-fund-related
    check surfaced as an unresolved gap. Loaded from the real loan 01
    fixture (`fixtures/from_docs/loan_01.json`), which already carries
    `doc_present_gift_letter: "false"` under `facts` (extraction hasn't
    wired a `gift_funds_used` canonical field yet -- this test injects it
    into `fields`, the slot `applies_if` actually reads, mirroring what a
    real extraction pass will eventually populate; see Assumptions)."""
    loan = load_canonical_loan(LOAN_01_FIXTURE)
    assert loan.facts.get("doc_present_gift_letter") == "false"  # confirms this IS loan 01's real fact
    loan.fields["gift_funds_used"] = SourceValue(doc="false")
    loan.fields.setdefault("gift_documentation_complete", SourceValue(doc=None))

    chk = _gift_check([{"field_name": "gift_funds_used", "operator": "==", "value": "true"}])
    result = _run_single(chk, loan)
    res = result.results[0]
    assert res.status == "NOT_APPLICABLE"
    assert "gift_funds_used" in res.message


# --- SC-004: referential integrity ------------------------------------------

def _tiny_catalog():
    return FieldCatalog(catalog_id="t-cat", version=1, entries=[
        FieldCatalogEntry(field_name="gift_documentation_complete", data_type="boolean",
                          expected_sources=["doc"]),
        FieldCatalogEntry(field_name="gift_funds_used", data_type="boolean",
                          expected_sources=["doc"]),
    ])


def test_referential_integrity_accepts_resolvable_applies_if_field():
    chk = _gift_check([{"field_name": "gift_funds_used", "operator": "==", "value": "true"}])
    rs = Ruleset(ruleset_id="t-ri-ok", version=1, checks=[chk])
    validate_referential_integrity(rs, _tiny_catalog())  # must not raise


def test_referential_integrity_rejects_unresolvable_applies_if_field():
    chk = _gift_check([{"field_name": "totally_unknown_field", "operator": "==", "value": "true"}])
    rs = Ruleset(ruleset_id="t-ri-bad", version=1, checks=[chk])
    with pytest.raises(ReferentialIntegrityError):
        validate_referential_integrity(rs, _tiny_catalog())
