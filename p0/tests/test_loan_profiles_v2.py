"""
Tests for p0/qc_engine/build_loan_profiles_v2.py -- the two new loan-side
derivations (loan_transaction_type, appraisal_in_file) added 2026-07-27 on
top of v1's gift_funds_used, after an explicit feasibility check found these
are the only two of the 16-fact vocabulary with a direct, already-extracted
signal on the 5 real loan fixtures.

Run: python3 -m pytest p0/tests/test_loan_profiles_v2.py -v
Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FROM_DOCS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fixtures", "from_docs"))
sys.path.insert(0, FROM_DOCS_DIR)

from fixture_loader import load_canonical_loan  # noqa: E402

from qc_engine.build_loan_profiles_v2 import (  # noqa: E402
    LOAN_NUMBERS,
    OUT_DIR,
    PROFILE_VERSION,
    build_all_profiles,
    build_profile,
    derive_appraisal_in_file,
    derive_loan_transaction_type,
)
from qc_engine.model import CanonicalLoan, SourceValue  # noqa: E402


def _load_shipped_profile(n: str):
    with open(os.path.join(OUT_DIR, "loan_{}.json".format(n)), "r", encoding="utf-8") as f:
        return json.load(f)


def _make_loan(fields=None, facts=None):
    return CanonicalLoan(loan_id="TEST-LOAN", loan_type="Test",
                         fields=fields or {}, facts=facts or {})


# --- shipped artifacts ------------------------------------------------------

def test_all_five_shipped_v2_profiles_exist_with_version_2():
    for n in LOAN_NUMBERS:
        profile = _load_shipped_profile(n)
        assert profile["profile_version"] == 2
        assert PROFILE_VERSION == 2


def test_rebuild_is_byte_identical_for_all_five_loans():
    for n in LOAN_NUMBERS:
        fixture_path = os.path.join(FROM_DOCS_DIR, "loan_{}.json".format(n))
        loan = load_canonical_loan(fixture_path)
        rebuilt = (json.dumps(build_profile(loan), indent=2, sort_keys=True) + "\n").encode("utf-8")
        with open(os.path.join(OUT_DIR, "loan_{}.json".format(n)), "rb") as f:
            on_disk = f.read()
        assert on_disk == rebuilt


def test_build_all_profiles_writes_five_files():
    written = build_all_profiles()
    assert len(written) == 5


# --- known real values across the 5 loans (verified by hand against fixtures) --

def test_all_five_loans_derive_gift_funds_used():
    expected = {"01": "false", "02": "true", "03": "false", "04": "false", "05": "false"}
    for n, val in expected.items():
        profile = _load_shipped_profile(n)
        assert profile["derived_facts"]["gift_funds_used"]["value"] == val


def test_all_five_loans_derive_loan_transaction_type():
    expected = {"01": "purchase", "02": "purchase", "03": "purchase",
               "04": "refinance", "05": "purchase"}
    for n, val in expected.items():
        profile = _load_shipped_profile(n)
        assert profile["derived_facts"]["loan_transaction_type"]["value"] == val


def test_four_of_five_loans_derive_appraisal_in_file_true():
    for n in ("01", "03", "04", "05"):
        profile = _load_shipped_profile(n)
        assert profile["derived_facts"]["appraisal_in_file"]["value"] == "true"


def test_loan_02_appraisal_in_file_is_honestly_underivable_not_false():
    """The load-bearing negative-space test: loan_02 (FHA) has no positive
    appraisal signal in this narrow fixture, so it MUST be underivable --
    never silently defaulted to 'false', which would be a real, wrong claim
    about a document that may well exist in the actual closing package."""
    profile = _load_shipped_profile("02")
    assert "appraisal_in_file" not in profile.get("derived_facts", {})
    entry = profile["underivable"]["appraisal_in_file"]
    assert "narrow" in entry["reason"].lower() or "no positive" in entry["reason"].lower()


def test_loan_02_both_derived_and_underivable_present_together():
    """v2's structural change from v1: a profile can carry BOTH keys at once,
    per-fact, not the old global either/or."""
    profile = _load_shipped_profile("02")
    assert "derived_facts" in profile and "underivable" in profile
    assert set(profile["derived_facts"]) == {"gift_funds_used", "loan_transaction_type"}
    assert set(profile["underivable"]) == {"appraisal_in_file"}


# --- unit tests: never guess ------------------------------------------------

def test_loan_transaction_type_missing_field_is_underivable():
    loan = _make_loan(fields={})
    result = derive_loan_transaction_type(loan)
    assert "underivable" in result
    assert result["underivable"]["loan_transaction_type"]["attempted_from"]["value"] is None


def test_loan_transaction_type_unrecognized_text_is_underivable_never_guessed():
    loan = _make_loan(fields={"loan_purpose_general_1003": SourceValue(doc="Home Equity Line")})
    result = derive_loan_transaction_type(loan)
    assert "underivable" in result
    assert "not in the recognized" in result["underivable"]["loan_transaction_type"]["reason"]


def test_loan_transaction_type_recognized_text_maps_correctly():
    loan = _make_loan(fields={"loan_purpose_general_1003": SourceValue(doc="Purchase")})
    result = derive_loan_transaction_type(loan)
    assert result["derived_facts"]["loan_transaction_type"]["value"] == "purchase"


def test_appraisal_in_file_false_reading_on_program_fact_is_not_a_negative_signal():
    """A loan with doc_present_va_appraisal='false' and doc_present_usda_
    appraisal='false' (the generic default on almost every loan) and no
    appraised_value field must be underivable, NOT false."""
    loan = _make_loan(facts={"doc_present_va_appraisal": "false",
                             "doc_present_usda_appraisal": "false"})
    result = derive_appraisal_in_file(loan)
    assert "underivable" in result
    assert "appraisal_in_file" not in result.get("derived_facts", {})


def test_appraisal_in_file_true_from_appraised_value_alone():
    loan = _make_loan(fields={"appraised_value": SourceValue(doc="300000.00")})
    result = derive_appraisal_in_file(loan)
    assert result["derived_facts"]["appraisal_in_file"]["value"] == "true"


def test_appraisal_in_file_true_from_program_fact_alone():
    loan = _make_loan(facts={"doc_present_va_appraisal": "true"})
    result = derive_appraisal_in_file(loan)
    assert result["derived_facts"]["appraisal_in_file"]["value"] == "true"
