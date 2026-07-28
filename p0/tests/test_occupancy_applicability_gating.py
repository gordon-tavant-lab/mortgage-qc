"""
010b -- occupancy gates a real, already-compiled check
(`insurance-docs-support-owner-occupancy`), via a new derived fact
(`occupancy_type`) and a new wiring function
(`qc_engine.apply_loan_profile.apply_derived_facts`).

Covers tasks.md T008 (referential integrity for the two new catalog
entries), T017-T022 (User Story 2 -- the real check's applies_if gate,
mirroring test_conditional_applicability.py's existing constructed-
CanonicalLoan pattern). `applies_if`'s consumption mechanism itself
(002e's `_eval_applies_if`) is NOT re-tested here -- that's
test_conditional_applicability.py's concern; this file only tests that a
REAL derived fact + a REAL compiled check compose correctly end-to-end
(spec.md Why This Feature Exists, Gap 2).

Written FIRST (red phase): `qc_engine.apply_loan_profile` and
`qc_engine.build_loan_profiles_v3` do not exist yet, so every test in this
module is expected to fail at COLLECTION with ImportError/ModuleNotFoundError
until a future implementation pass adds them (spec.md FR-002/FR-003/FR-006).

Run: python3 -m pytest p0/tests/test_occupancy_applicability_gating.py -v
Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_P0 = os.path.dirname(_HERE)
if _P0 not in sys.path:
    sys.path.insert(0, _P0)
_REPO_ROOT = os.path.dirname(_P0)
_FROM_DOCS = os.path.join(_P0, "fixtures", "from_docs")
if _FROM_DOCS not in sys.path:
    sys.path.insert(0, _FROM_DOCS)

import pytest  # noqa: E402

from fixture_loader import load_canonical_loan  # noqa: E402

from qc_engine import run  # noqa: E402
from qc_engine.catalog import FieldCatalog, load_catalog, \
    validate_referential_integrity  # noqa: E402
from qc_engine.model import CanonicalLoan, SourceValue  # noqa: E402
from qc_engine.ruleset import Check, Ruleset  # noqa: E402

# Expected red until implementation lands (spec.md FR-002/FR-003/FR-006,
# tasks.md T002/T014/T023/T030): this whole module fails to collect with
# ImportError until build_loan_profiles_v3.py and apply_loan_profile.py
# both exist.
from qc_engine.apply_loan_profile import apply_derived_facts  # noqa: E402
from qc_engine.build_loan_profiles_v3 import derive_occupancy_type, \
    derive_loan_program  # noqa: E402

CATALOG_PATH = os.path.join(_P0, "qc_engine", "field_catalog.json")
RULESET_PATH = os.path.join(_REPO_ROOT, "result", "rules", "post_closing_only_ruleset.json")
LOAN_02_FIXTURE = os.path.join(_FROM_DOCS, "loan_02.json")
CHECK_ID = "insurance-docs-support-owner-occupancy"


def _real_check_dict():
    """The REAL, already-compiled check's dict, as it exists on disk today
    (pre-FR-007 -- no applies_if set yet). Reading straight from the shipped
    artifact keeps this test honest against the actual check this feature
    exists to wire, not a hand-authored look-alike."""
    with open(RULESET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    for c in data["content"]["checks"]:
        if c["id"] == CHECK_ID:
            return c
    raise AssertionError(
        "check '{}' not found in {} -- has it been renamed or removed?".format(
            CHECK_ID, RULESET_PATH))


def _gated_check(applies_if):
    raw = dict(_real_check_dict())
    raw["applies_if"] = applies_if
    return Check(**raw)


def _run_single(chk: Check, loan: CanonicalLoan):
    rs = Ruleset(ruleset_id="t-{}".format(chk.id), version=1, checks=[chk])
    return run(loan, rs)


OWNER_OCCUPIED_GATE = [{"field_name": "occupancy_type", "operator": "==", "value": "owner_occupied"}]


# =============================================================================
# T008 -- referential integrity for the two new catalog entries (Phase 2 /
# SC-004)
# =============================================================================

def test_field_catalog_resolves_occupancy_type_and_loan_program():
    """spec.md FR-005: both new facts must be resolvable catalog entries, so
    validate_referential_integrity() resolves them when referenced by a
    compiled check's field_name or applies_if.field_name, rather than
    raising ReferentialIntegrityError the moment either fact is used."""
    catalog = load_catalog(CATALOG_PATH)
    assert isinstance(catalog, FieldCatalog)
    occupancy_entry = catalog.get("occupancy_type")
    program_entry = catalog.get("loan_program")
    assert occupancy_entry is not None, (
        "field_catalog.json is missing the 'occupancy_type' entry (FR-005)")
    assert program_entry is not None, (
        "field_catalog.json is missing the 'loan_program' entry (FR-005)")
    assert occupancy_entry.data_type == "enum"
    assert set(occupancy_entry.enum_values or []) == {"owner_occupied", "second_home", "investment"}
    assert program_entry.data_type == "enum"
    assert set(program_entry.enum_values or []) == {
        "Conventional", "FHA", "VA", "USDA", "Freddie Mac", "Fannie Mae", "SONYMA"}


def test_referential_integrity_accepts_applies_if_on_occupancy_type():
    """SC-004: a tiny Ruleset whose Check.applies_if references
    occupancy_type passes validate_referential_integrity() against the
    REAL, on-disk field_catalog.json without raising."""
    catalog = load_catalog(CATALOG_PATH)
    chk = _gated_check(OWNER_OCCUPIED_GATE)
    rs = Ruleset(ruleset_id="t-ri-occupancy", version=1, checks=[chk])
    validate_referential_integrity(rs, catalog)  # must not raise


# =============================================================================
# T017 -- documents the "before" state (spec.md FR-007 not yet applied)
# =============================================================================

def test_real_check_currently_has_no_applies_if_before_this_feature():
    """Documents the 'before' state this feature changes (tasks.md T017):
    today, `insurance-docs-support-owner-occupancy` runs unconditionally.
    Once FR-007 lands (tasks.md T024), this specific assertion is expected
    to flip -- this test's job is only to pin down the starting point, not
    to remain true forever."""
    raw = _real_check_dict()
    assert raw.get("applies_if") is None


# =============================================================================
# T018-T019 -- apply_derived_facts (FR-006's wiring function)
# =============================================================================

def test_apply_derived_facts_writes_occupancy_type_for_loan_02():
    """tasks.md T018: apply_derived_facts(loan, profile) writes
    loan.fields['occupancy_type'] = SourceValue(doc='owner_occupied') for
    loan_02's real fixture, and does NOT overwrite loan.fields
    ['occupancy_1003'] (the source field the derivation itself read) --
    FR-006's never-shadow-a-real-field guarantee, spec.md Edge Cases."""
    loan = load_canonical_loan(LOAN_02_FIXTURE)
    original_occupancy_1003 = loan.get("occupancy_1003").doc
    profile = derive_occupancy_type(loan)

    wired = apply_derived_facts(loan, profile)

    assert wired.fields["occupancy_type"].doc == "owner_occupied"
    assert wired.get("occupancy_1003").doc == original_occupancy_1003


def test_apply_derived_facts_never_overwrites_an_existing_field_of_the_same_name():
    """The direct FR-006 / Edge Cases proof: if `loan.fields['occupancy_type']`
    is ALREADY populated (e.g. a future Touchless extraction widening),
    apply_derived_facts MUST NOT overwrite it with the derived value -- a
    derived fact only fills a gap, never shadows a genuinely extracted one
    (Non-Negotiable #1: the document is the source of truth)."""
    loan = load_canonical_loan(LOAN_02_FIXTURE)
    loan.fields["occupancy_type"] = SourceValue(doc="ALREADY_EXTRACTED_DO_NOT_OVERWRITE")
    profile = derive_occupancy_type(loan)  # would derive "owner_occupied"

    wired = apply_derived_facts(loan, profile)

    assert wired.fields["occupancy_type"].doc == "ALREADY_EXTRACTED_DO_NOT_OVERWRITE"


def test_apply_derived_facts_writes_nothing_for_underivable_entries():
    """tasks.md T019: given a profile entry under `underivable` (not
    `derived_facts`) for some fact, apply_derived_facts writes NOTHING to
    loan.fields for that fact name -- loan_01's real, honestly-underivable
    loan_program case (spec.md Why This Feature Exists)."""
    loan = load_canonical_loan(os.path.join(_FROM_DOCS, "loan_01.json"))
    profile = derive_loan_program(loan)
    assert "loan_program" in profile.get("underivable", {}), (
        "loan_01 is expected to be honestly underivable for loan_program "
        "(spec.md Why This Feature Exists table) -- if this now derives a "
        "value, the fixture or the derivation logic changed; re-verify "
        "before trusting this test")

    wired = apply_derived_facts(loan, profile)

    assert "loan_program" not in wired.fields


# =============================================================================
# T020-T022 -- the real check's applies_if gate, end to end
# =============================================================================

def test_real_check_gated_evaluates_normally_once_occupancy_resolves_owner_occupied():
    """spec.md Acceptance Scenario 1 / SC-002: the real check, gated on
    occupancy_type == owner_occupied, evaluates its own predicate: is_true
    logic EXACTLY as it would have before this feature -- the gate does not
    change behavior once it passes. Proven both ways (PASS and FAIL), per
    the same non-regression discipline 002e's own Acceptance Scenario 2
    established (test_conditional_applicability.py's
    test_applies_if_true_condition_evaluates_normally)."""
    loan = load_canonical_loan(LOAN_02_FIXTURE)
    profile = derive_occupancy_type(loan)
    wired = apply_derived_facts(loan, profile)
    assert wired.fields["occupancy_type"].doc == "owner_occupied"

    gated = _gated_check(OWNER_OCCUPIED_GATE)
    ungated = _gated_check(None)

    # PASS side
    wired.fields["insurance_docs_support_owner_occupancy"] = SourceValue(doc=True)
    gated_result = _run_single(gated, wired).results[0]
    ungated_result = _run_single(ungated, wired).results[0]
    assert gated_result.status == ungated_result.status == "PASS"

    # FAIL side -- the gate must not silently flip a genuine defect to PASS.
    wired.fields["insurance_docs_support_owner_occupancy"] = SourceValue(doc=False)
    gated_result_fail = _run_single(gated, wired).results[0]
    ungated_result_fail = _run_single(ungated, wired).results[0]
    assert gated_result_fail.status == ungated_result_fail.status == "FAIL"


def test_real_check_gated_resolves_not_applicable_for_investment_property():
    """spec.md Acceptance Scenario 2 / SC-002: a constructed loan whose
    occupancy resolves 'investment' (occupancy_1003='Investment Property' --
    no real fixture carries this text today, spec.md Edge Cases, disclosed
    as constructed-fixture-only) resolves NOT_APPLICABLE against the same
    gated check."""
    loan = CanonicalLoan(loan_id="LN-010B-INVESTMENT", loan_type="Test", fields={
        "occupancy_1003": SourceValue(doc="Investment Property"),
        "insurance_docs_support_owner_occupancy": SourceValue(doc=True),
    })
    profile = derive_occupancy_type(loan)
    wired = apply_derived_facts(loan, profile)
    assert wired.fields["occupancy_type"].doc == "investment"

    gated = _gated_check(OWNER_OCCUPIED_GATE)
    result = _run_single(gated, wired).results[0]
    assert result.status == "NOT_APPLICABLE"
    assert result.review_reason is None


def test_real_check_gated_resolves_needs_review_when_occupancy_type_never_wired():
    """spec.md Acceptance Scenario 3: a loan where occupancy_type was never
    derivable/wired (absent from loan.fields entirely, i.e. apply_derived_
    facts never ran, or ran and found nothing to write) resolves
    NEEDS_REVIEW with review_reason == 'APPLICABILITY_UNKNOWN' -- 002e's
    existing FR-003 behavior, unmodified, now exercised by a real derived
    fact's absence instead of only a hand-authored test fixture."""
    loan = CanonicalLoan(loan_id="LN-010B-UNWIRED", loan_type="Test", fields={
        "insurance_docs_support_owner_occupancy": SourceValue(doc=True),
        # occupancy_type deliberately absent -- genuinely unknown, not false.
    })
    gated = _gated_check(OWNER_OCCUPIED_GATE)
    result = _run_single(gated, loan).results[0]
    assert result.status == "NEEDS_REVIEW"
    assert result.review_reason == "APPLICABILITY_UNKNOWN"


# =============================================================================
# FR-010 -- the applies_if gate composes with, and does not supersede,
# 010a's own program-applicability tag on the same check.
# =============================================================================

def test_applicability_json_fannie_mae_tag_untouched_by_this_feature():
    """FR-010: the applies_if gate on insurance-docs-support-owner-occupancy
    must not change 010a's own, separate program-applicability tag
    (['Fannie Mae']) on the same check -- the two gating layers compose,
    neither supersedes the other."""
    applicability_path = os.path.join(
        _REPO_ROOT, "result", "rules", "post_closing_only_applicability.json")
    with open(applicability_path, "r", encoding="utf-8") as f:
        applicability = json.load(f)
    assert applicability.get(CHECK_ID) == ["Fannie Mae"]
