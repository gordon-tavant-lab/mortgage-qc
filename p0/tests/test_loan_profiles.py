"""
Tests for p0/qc_engine/build_loan_profiles.py -- the persisted loan-side
derived-fact profiles (storage/loan_profiles/v1/loan_<NN>.json). Closes the
"extracted loan ontology" gap: `gift_funds_used` was previously derived only
in-memory during run_011 (`_panel()`); this makes the derivation an on-disk
artifact with explicit provenance.

Run from repo root: python3 -m pytest p0/tests/test_loan_profiles.py -v
Python 3.9 compatible.
"""
from __future__ import annotations

import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FROM_DOCS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fixtures", "from_docs")
)
sys.path.insert(0, FROM_DOCS_DIR)

from fixture_loader import load_canonical_loan  # noqa: E402

from qc_engine.build_loan_profiles import (  # noqa: E402
    LOAN_NUMBERS,
    OUT_DIR,
    DERIVED_FACT,
    SOURCE_FACT,
    build_all_profiles,
    build_profile,
    derive_gift_funds_used,
)
from qc_engine.model import CanonicalLoan  # noqa: E402


def _load_shipped_profile(n: str):
    path = os.path.join(OUT_DIR, "loan_{}.json".format(n))
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _rebuild_serialized(n: str) -> bytes:
    """Re-derive loan_<n>'s profile in-memory and serialize it with the same
    settings the build script uses, for byte-identical comparison."""
    fixture_path = os.path.join(FROM_DOCS_DIR, "loan_{}.json".format(n))
    loan = load_canonical_loan(fixture_path)
    profile = build_profile(loan)
    return (json.dumps(profile, indent=2, sort_keys=True) + "\n").encode("utf-8")


# --- (a) shipped artifacts load, and rebuilding is byte-identical -----------

def test_all_five_shipped_profiles_exist_and_load():
    for n in LOAN_NUMBERS:
        profile = _load_shipped_profile(n)
        assert profile["profile_version"] == 1
        assert "loan_id" in profile
        assert ("derived_facts" in profile) != ("underivable" in profile)


def test_rebuilding_produces_byte_identical_json_for_all_five_loans():
    for n in LOAN_NUMBERS:
        path = os.path.join(OUT_DIR, "loan_{}.json".format(n))
        with open(path, "rb") as f:
            on_disk = f.read()
        rebuilt = _rebuild_serialized(n)
        assert on_disk == rebuilt, "loan_{} profile is not byte-identical on rebuild".format(n)


def test_build_all_profiles_writes_exactly_five_files_in_order():
    written = build_all_profiles()
    assert len(written) == 5
    assert [os.path.basename(p) for p in written] == [
        "loan_{}.json".format(n) for n in LOAN_NUMBERS
    ]


# --- (b) derived value matches the source fixture's doc_present_gift_letter -

def test_each_profile_derived_value_matches_source_fixture_fact():
    for n in LOAN_NUMBERS:
        fixture_path = os.path.join(FROM_DOCS_DIR, "loan_{}.json".format(n))
        loan = load_canonical_loan(fixture_path)
        source_value = loan.facts.get(SOURCE_FACT)

        profile = _load_shipped_profile(n)

        if source_value in ("true", "false"):
            assert "derived_facts" in profile
            derived = profile["derived_facts"][DERIVED_FACT]
            assert derived["value"] == source_value
            assert derived["derived_from"] == {"fact": SOURCE_FACT, "value": source_value}
        else:
            assert "underivable" in profile


# --- (c) known real facts: loan 02 true, loan 01 false ----------------------

def test_loan_02_profile_says_gift_funds_used_true():
    profile = _load_shipped_profile("02")
    assert profile["loan_id"] == "2025-1004-FHA-002"
    assert profile["derived_facts"][DERIVED_FACT]["value"] == "true"


def test_loan_01_profile_says_gift_funds_used_false():
    profile = _load_shipped_profile("01")
    assert profile["loan_id"] == "2025-0917-001"
    assert profile["derived_facts"][DERIVED_FACT]["value"] == "false"


# --- (d) missing/invalid source fact -> underivable, never a guess ----------

def _make_loan(facts):
    return CanonicalLoan(loan_id="TEST-LOAN", loan_type="Test", fields={}, facts=facts)


def test_missing_source_fact_yields_underivable_not_a_guess():
    loan = _make_loan(facts={})  # doc_present_gift_letter absent entirely
    result = derive_gift_funds_used(loan)

    assert "derived_facts" not in result
    assert "underivable" in result
    entry = result["underivable"][DERIVED_FACT]
    assert "missing" in entry["reason"].lower()
    assert entry["attempted_from"] == {"fact": SOURCE_FACT, "value": None}


def test_unrecognized_source_fact_value_yields_underivable_not_a_guess():
    loan = _make_loan(facts={SOURCE_FACT: "unknown"})
    result = derive_gift_funds_used(loan)

    assert "derived_facts" not in result
    assert "underivable" in result
    entry = result["underivable"][DERIVED_FACT]
    assert "unrecognized" in entry["reason"].lower()
    assert entry["attempted_from"] == {"fact": SOURCE_FACT, "value": "unknown"}


def test_valid_source_fact_values_do_produce_derived_facts():
    for value in ("true", "false"):
        loan = _make_loan(facts={SOURCE_FACT: value})
        result = derive_gift_funds_used(loan)
        assert "underivable" not in result
        assert result["derived_facts"][DERIVED_FACT]["value"] == value
        assert result["derived_facts"][DERIVED_FACT]["derived_from"] == {
            "fact": SOURCE_FACT,
            "value": value,
        }


def test_build_profile_is_pure_and_does_not_mutate_loan_facts():
    loan = _make_loan(facts={SOURCE_FACT: "true"})
    before = copy.deepcopy(loan.facts)
    build_profile(loan)
    assert loan.facts == before
