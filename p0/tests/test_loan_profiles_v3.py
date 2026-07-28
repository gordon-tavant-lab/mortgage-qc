"""
Tests for p0/qc_engine/build_loan_profiles_v3.py -- the two new loan-side
derivations (occupancy_type, loan_program) added on top of v2's 3 existing
derivations (gift_funds_used, loan_transaction_type, appraisal_in_file),
per specs/010b-derive-remaining-gating-dimensions.

Covers tasks.md T009-T013 (User Story 1 -- derive_occupancy_type) and
T026-T029 (User Story 3 -- derive_loan_program). Written FIRST (red phase):
`qc_engine.build_loan_profiles_v3` does not exist yet, so every test in this
module is expected to fail at COLLECTION with ImportError/ModuleNotFoundError
until a future implementation pass adds it (spec.md FR-002/FR-003).

Mirrors test_loan_profiles_v2.py's exact conventions: fixture loading via
fixture_loader.load_canonical_loan against the real fixtures in
p0/fixtures/from_docs/, and constructed CanonicalLoan instances (via
_make_loan) for the edge cases spec.md's own Edge Cases section discloses as
"proven only against constructed fixtures, not a real extracted loan" (all 5
real fixtures are owner-occupied -- see spec.md Edge Cases).

Run: python3 -m pytest p0/tests/test_loan_profiles_v3.py -v
Python 3.9 compatible.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FROM_DOCS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fixtures", "from_docs"))
sys.path.insert(0, FROM_DOCS_DIR)

from fixture_loader import load_canonical_loan  # noqa: E402

# Expected red until implementation lands (spec.md FR-002/FR-003, tasks.md
# T001/T014/T030): this whole module fails to collect with ImportError until
# build_loan_profiles_v3.py exists.
from qc_engine.build_loan_profiles_v3 import (  # noqa: E402
    derive_loan_program,
    derive_occupancy_type,
)
from qc_engine.model import CanonicalLoan, SourceValue  # noqa: E402


def _fixture_path(n: str) -> str:
    return os.path.join(FROM_DOCS_DIR, "loan_{}.json".format(n))


def _make_loan(fields=None, facts=None):
    return CanonicalLoan(loan_id="TEST-LOAN", loan_type="Test",
                         fields=fields or {}, facts=facts or {})


# =============================================================================
# User Story 1 -- derive_occupancy_type (tasks.md T009-T013)
# =============================================================================

# --- T009: loan_02's real fixture -------------------------------------------

def test_derive_occupancy_type_loan_02_real_fixture_resolves_owner_occupied():
    """spec.md Acceptance Scenario 1: loan_02's real occupancy_1003 reads
    'Primary Residence (First-Time Homebuyer)' -- must resolve owner_occupied
    with derived_from naming the source field and the literal text."""
    loan = load_canonical_loan(_fixture_path("02"))
    assert loan.get("occupancy_1003").doc == "Primary Residence (First-Time Homebuyer)"

    result = derive_occupancy_type(loan)
    entry = result["derived_facts"]["occupancy_type"]
    assert entry["value"] == "owner_occupied"
    assert entry["derived_from"]["field"] == "occupancy_1003"
    assert entry["derived_from"]["value"] == "Primary Residence (First-Time Homebuyer)"


# --- T010: loan_01/03/04/05's real fixtures ---------------------------------

def test_derive_occupancy_type_all_five_real_loans_resolve_owner_occupied():
    """spec.md SC-001 / Acceptance Scenario 1: all 5 real loan fixtures are,
    in fact, owner-occupied (spec.md Edge Cases -- a real, disclosed
    data-diversity limit, not claimed beyond it). Confirmed by direct read of
    each fixture's occupancy_1003 value: loan_01/03/04/05 read 'Primary
    Residence'; loan_02 reads 'Primary Residence (First-Time Homebuyer)'
    (T009, above)."""
    expected_raw = {
        "01": "Primary Residence",
        "02": "Primary Residence (First-Time Homebuyer)",
        "03": "Primary Residence",
        "04": "Primary Residence",
        "05": "Primary Residence",
    }
    for n, raw in expected_raw.items():
        loan = load_canonical_loan(_fixture_path(n))
        assert loan.get("occupancy_1003").doc == raw, (
            "fixture loan_{} occupancy_1003 changed underneath this test -- "
            "re-verify against the real fixture before trusting this "
            "assertion".format(n))
        result = derive_occupancy_type(loan)
        entry = result["derived_facts"]["occupancy_type"]
        assert entry["value"] == "owner_occupied", (
            "loan_{} expected owner_occupied, got {!r}".format(n, entry.get("value")))
        assert entry["derived_from"]["field"] == "occupancy_1003"
        assert entry["derived_from"]["value"] == raw


# --- T011: constructed "Investment Property" --------------------------------

def test_derive_occupancy_type_constructed_investment_property_resolves_investment():
    """spec.md Acceptance Scenario 2: the real ULAD/URLA occupancy checkbox
    option 'Investment Property' -- no real fixture carries this text today
    (spec.md Edge Cases), so this is a CONSTRUCTED CanonicalLoan, disclosed
    as such, not tested against a real extracted loan. Proves the map
    recognizes the industry-standard token set, not only the 5 fixtures'
    own narrow text."""
    loan = _make_loan(fields={"occupancy_1003": SourceValue(doc="Investment Property")})
    result = derive_occupancy_type(loan)
    entry = result["derived_facts"]["occupancy_type"]
    assert entry["value"] == "investment"


# --- T012: constructed "Second Home" ----------------------------------------

def test_derive_occupancy_type_constructed_second_home_resolves_second_home():
    """Same constructed-fixture-only disclosure as T011 -- no real fixture
    carries 'Second Home' occupancy text today."""
    loan = _make_loan(fields={"occupancy_1003": SourceValue(doc="Second Home")})
    result = derive_occupancy_type(loan)
    entry = result["derived_facts"]["occupancy_type"]
    assert entry["value"] == "second_home"


# --- T013: unrecognized text -> underivable, never guessed ------------------

def test_derive_occupancy_type_unrecognized_text_is_underivable_never_guessed():
    """spec.md Acceptance Scenario 3 / FR-002: an occupancy_1003 value
    outside the recognized literal-variant map must resolve underivable --
    never a fuzzy/substring match, never a guessed default."""
    loan = _make_loan(fields={"occupancy_1003": SourceValue(doc="Occupied by Relative")})
    result = derive_occupancy_type(loan)
    assert "underivable" in result
    assert "occupancy_type" not in result.get("derived_facts", {})
    entry = result["underivable"]["occupancy_type"]
    assert entry["reason"]


def test_derive_occupancy_type_missing_field_is_underivable_never_guessed():
    """The missing-field companion to T013 -- mirrors
    test_loan_transaction_type_missing_field_is_underivable's existing
    discipline in test_loan_profiles_v2.py."""
    loan = _make_loan(fields={})
    result = derive_occupancy_type(loan)
    assert "underivable" in result
    assert "occupancy_type" not in result.get("derived_facts", {})


# =============================================================================
# User Story 3 -- derive_loan_program (tasks.md T026-T029)
# =============================================================================

# --- T026: loan_02 (FHA) -----------------------------------------------------

def test_derive_loan_program_loan_02_real_fixture_resolves_fha():
    """spec.md Acceptance Scenario 1 / SC-003: loan_02's real
    fha_case_number_1003 ('381-9927164', confirmed by direct fixture read)
    is present and cited -- unambiguous FHA signal."""
    loan = load_canonical_loan(_fixture_path("02"))
    assert loan.get("fha_case_number_1003").doc == "381-9927164"

    result = derive_loan_program(loan)
    entry = result["derived_facts"]["loan_program"]
    assert entry["value"] == "FHA"
    assert entry["derived_from"]["field"] == "fha_case_number_1003"
    assert entry["derived_from"]["value"] == "381-9927164"


# --- T027: loan_03 (VA) / loan_05 (USDA) ------------------------------------

def test_derive_loan_program_loan_03_real_fixture_resolves_va():
    """loan_03's real va_lgy_case_number ('LGY-2025-4471903', confirmed by
    direct fixture read) is present and cited -- unambiguous VA signal."""
    loan = load_canonical_loan(_fixture_path("03"))
    assert loan.get("va_lgy_case_number").doc == "LGY-2025-4471903"

    result = derive_loan_program(loan)
    entry = result["derived_facts"]["loan_program"]
    assert entry["value"] == "VA"
    assert entry["derived_from"]["field"] == "va_lgy_case_number"
    assert entry["derived_from"]["value"] == "LGY-2025-4471903"


def test_derive_loan_program_loan_05_real_fixture_resolves_usda():
    """loan_05's real usda_gus_id ('GUS-2025-8817709', confirmed by direct
    fixture read) is present and cited -- unambiguous USDA signal."""
    loan = load_canonical_loan(_fixture_path("05"))
    assert loan.get("usda_gus_id").doc == "GUS-2025-8817709"

    result = derive_loan_program(loan)
    entry = result["derived_facts"]["loan_program"]
    assert entry["value"] == "USDA"
    assert entry["derived_from"]["field"] == "usda_gus_id"
    assert entry["derived_from"]["value"] == "GUS-2025-8817709"


# --- T028: loan_01 -- Conventional but Fannie/Freddie ambiguous ------------

def test_derive_loan_program_loan_01_real_fixture_is_underivable_ambiguous():
    """spec.md Acceptance Scenario 2 / SC-003: loan_01's real loan_type_cd
    reads 'Conventional' (cited) but carries no GSE-specific citable field --
    'Conventional' alone cannot distinguish Fannie Mae vs. Freddie Mac (the
    same ambiguity program_gating.py's own AMBIGUOUS sentinel already exists
    to surface at the SQL-clause layer). Must be underivable, with a reason
    naming the ambiguity explicitly -- never a silent guess in either
    direction."""
    loan = load_canonical_loan(_fixture_path("01"))
    assert loan.get("loan_type_cd").doc == "Conventional"
    for gse_field in ("fha_case_number_1003", "va_lgy_case_number", "usda_gus_id"):
        assert loan.get(gse_field).doc is None, (
            "loan_01 unexpectedly carries a GSE-specific field {!r} -- this "
            "would make the fixture no longer represent the ambiguous case "
            "this test exists to prove".format(gse_field))

    result = derive_loan_program(loan)
    assert "underivable" in result
    assert "loan_program" not in result.get("derived_facts", {})
    reason = result["underivable"]["loan_program"]["reason"].lower()
    assert "fannie" in reason
    assert "freddie" in reason
    assert "ambig" in reason


# --- T029: loan_04 -- no program-identifying field at all -------------------

def test_derive_loan_program_loan_04_real_fixture_is_underivable_no_signal():
    """spec.md Acceptance Scenario 3 / SC-003: loan_04 carries ZERO
    program-identifying field of any kind in `fields` (confirmed by direct
    fixture read) -- its top-level loan_type label ('Freddie Mac Cash-Out
    Refi') is uncited fixture-authoring metadata, never a citable doc-
    extracted signal. Must be underivable, with a reason DISTINGUISHABLE
    from loan_01's ambiguity reason -- 'no citable signal found' is a
    different failure mode from 'signal found but ambiguous' and the two
    must not be conflated."""
    loan = load_canonical_loan(_fixture_path("04"))
    for program_field in ("fha_case_number_1003", "va_lgy_case_number",
                          "usda_gus_id", "loan_type_cd"):
        assert loan.get(program_field).doc is None, (
            "loan_04 unexpectedly carries {!r} -- this would make the "
            "fixture no longer represent the zero-signal case this test "
            "exists to prove".format(program_field))

    result = derive_loan_program(loan)
    assert "underivable" in result
    assert "loan_program" not in result.get("derived_facts", {})
    reason = result["underivable"]["loan_program"]["reason"].lower()
    assert "ambig" not in reason  # distinct failure mode from loan_01's

    # And the two honest-underivable reasons must not be conflated.
    loan_01 = load_canonical_loan(_fixture_path("01"))
    reason_01 = derive_loan_program(loan_01)["underivable"]["loan_program"]["reason"]
    assert reason_01.lower() != reason
