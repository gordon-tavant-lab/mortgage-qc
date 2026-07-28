"""
012 User Story 1 (T007/T008) -- a real loan scores through the existing
harness with zero scorer rework.

Two independent things are proven here:

1. `eval_real.adapter.RealLoanAdapter` converts a bundle shaped like the real
   S3 extraction output (`{loan}-ulad.json` + `{loan}-citations.json` +
   `consolidated/*.json`) into the exact `LabeledLoan` tuple shape
   `test_properties.score()` already accepts (FR-001/002), records unmapped
   field names as a named `MappingGapReport` entry rather than dropping them
   (FR-004), and never crashes.
2. `test_properties.score()`'s mismatch-message formatting has a real,
   reproducible `KeyError` when a scored tuple's `prov` dict omits the
   `"mutations"` key (FR-003) -- confirmed against TODAY's unpatched
   `score()`, proving the gap spec.md's Foundation section names is real, not
   assumed.

SAFETY: every loan id, borrower name, SSN, and address below is hand-authored
and synthetic -- a stand-in bundle, explicitly NOT one of the real loans this
feature ingests (tasks.md T007's own framing). No real loan id, real S3 path,
or real PII value appears anywhere in this file.

Python 3.9 compatible. `eval_real.adapter` / `eval_real.mapping_gaps` do not
exist yet -- every test that needs them is expected to fail RED via
ImportError until T009/T010 land (tasks.md). Those imports are deferred
inside each test function so this file stays collectible by pytest before
the package exists. T008's regression test needs no new code at all -- it
runs against the CURRENT, already-shipped `test_properties.score()` and is
expected to fail red for a real, already-confirmed reason (see below), not an
ImportError.
"""
from __future__ import annotations

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "eval_synth"))

from qc_engine.model import CanonicalLoan  # noqa: E402

import generator as G  # noqa: E402
import test_properties as TP  # noqa: E402

# A field name guaranteed to have no field_catalog.json counterpart -- picked
# to be obviously synthetic/nonsense, never a plausible real extraction field.
UNMAPPED_FIELD_NAME = "totally_unmapped_synthetic_field_xyz_not_in_catalog"

# Hand-authored, entirely synthetic stand-in values -- never real PII.
STANDIN_LOAN_ID = "SYN-STANDIN-001"
STANDIN_BORROWER_NAME = "Jamie Q. Testborrower"
STANDIN_SSN_LAST4 = "0000"
STANDIN_ADDRESS = "1 Fake Test Lane, Testville, TS 00000"
STANDIN_NOTE_RATE = "6.500"
STANDIN_LOAN_AMOUNT = "300000.00"


def _write_synthetic_bundle(bundle_dir: str, loan_id: str,
                             include_unmapped_field: bool = True) -> None:
    """Writes a small, hand-authored SYNTHETIC bundle mirroring the real S3
    extraction shape (`{loan}-ulad.json`, `{loan}-citations.json`,
    `consolidated/*.json`) -- explicitly a stand-in, not a real loan."""
    os.makedirs(os.path.join(bundle_dir, "consolidated"), exist_ok=True)

    ulad = {
        "loan_id": loan_id,
        "borrowers": [{
            "full_name": STANDIN_BORROWER_NAME,
            "ssn_last4": STANDIN_SSN_LAST4,
        }],
        "property": {"address": STANDIN_ADDRESS},
        "loan_detail": {
            "note_rate": STANDIN_NOTE_RATE,
            "loan_amount": STANDIN_LOAN_AMOUNT,
        },
    }
    if include_unmapped_field:
        ulad["loan_detail"][UNMAPPED_FIELD_NAME] = "some synthetic value, deliberately unmapped"

    with open(os.path.join(bundle_dir, f"{loan_id}-ulad.json"), "w") as f:
        json.dump(ulad, f)

    citations = {
        "discrepancies": [{
            "field": "borrower_name",
            "text_snippet": f"Borrower: {STANDIN_BORROWER_NAME}",
            "page": 3,
            "confidence": 0.97,
            "document": f"{loan_id}-urla1003.pdf",
            "document_type": "urla1003",
        }],
    }
    with open(os.path.join(bundle_dir, f"{loan_id}-citations.json"), "w") as f:
        json.dump(citations, f)

    with open(os.path.join(bundle_dir, "consolidated", "urla1003.json"), "w") as f:
        json.dump({"document_type": "urla1003", "fields": {
            "borrower_name": STANDIN_BORROWER_NAME,
        }}, f)


# --------------------------------------------------------------------------- #
# T007 -- the adapter, against a hand-authored synthetic stand-in bundle.
# --------------------------------------------------------------------------- #
def test_adapter_produces_valid_canonical_loan_from_synthetic_standin_bundle(tmp_path):
    from eval_real.adapter import RealLoanAdapter

    _write_synthetic_bundle(str(tmp_path), STANDIN_LOAN_ID)

    adapter = RealLoanAdapter()
    loan, expected, prov = adapter.adapt(
        bundle_dir=str(tmp_path), loan_id=STANDIN_LOAN_ID,
        expected_verdicts={"chk-borrower-name": "PASS"},
    )

    assert isinstance(loan, CanonicalLoan)
    assert loan.loan_id == STANDIN_LOAN_ID
    assert loan.fields["borrower_name"].truth == STANDIN_BORROWER_NAME


def test_adapter_output_matches_labeled_loan_tuple_shape(tmp_path):
    """FR-002: no new type -- the exact `(CanonicalLoan, Dict[str, str],
    Dict[str, Any])` tuple `score()` already accepts, with prov carrying at
    minimum mutations/source/loan_id."""
    from eval_real.adapter import RealLoanAdapter

    _write_synthetic_bundle(str(tmp_path), STANDIN_LOAN_ID)

    adapter = RealLoanAdapter()
    result = adapter.adapt(
        bundle_dir=str(tmp_path), loan_id=STANDIN_LOAN_ID,
        expected_verdicts={"chk-borrower-name": "PASS"},
    )

    assert isinstance(result, tuple) and len(result) == 3
    loan, expected, prov = result
    assert isinstance(loan, CanonicalLoan)
    assert isinstance(expected, dict)
    assert isinstance(prov, dict)
    assert prov["mutations"] == []
    assert prov["source"] == "expert-labeled"
    assert prov["loan_id"] == STANDIN_LOAN_ID


def test_adapter_output_scores_through_unmodified_score_without_crash(tmp_path):
    """The real point of US1: the adapted tuple must survive
    `test_properties.score()` -- the existing, byte-for-byte unmodified
    scorer -- with no crash and a well-formed report."""
    from eval_real.adapter import RealLoanAdapter

    _write_synthetic_bundle(str(tmp_path), STANDIN_LOAN_ID)

    adapter = RealLoanAdapter()
    labeled_loan = adapter.adapt(
        bundle_dir=str(tmp_path), loan_id=STANDIN_LOAN_ID,
        expected_verdicts={"chk-borrower-name": "PASS"},
    )

    report = TP.score([labeled_loan])
    assert "checks_scored" in report
    assert "exact_match" in report
    assert "false_auto_clear_count" in report


def test_unmapped_field_surfaces_as_named_mapping_gap_not_dropped(tmp_path):
    """FR-004: an extracted field with no field_catalog.json counterpart is
    recorded as a named mapping-gap entry -- never silently dropped, never
    silently coerced into a null SourceValue."""
    from eval_real.adapter import RealLoanAdapter

    _write_synthetic_bundle(str(tmp_path), STANDIN_LOAN_ID, include_unmapped_field=True)

    adapter = RealLoanAdapter()
    loan, _expected, _prov = adapter.adapt(
        bundle_dir=str(tmp_path), loan_id=STANDIN_LOAN_ID, expected_verdicts={},
    )

    gap_report = adapter.last_mapping_gap_report
    gap_field_names = {g.field_name for g in gap_report.gaps}
    assert UNMAPPED_FIELD_NAME in gap_field_names, (
        "an unmapped real field name must appear in the MappingGapReport, "
        "never silently dropped"
    )
    # And it must not have been silently coerced into a CanonicalLoan field
    # under its raw, unmapped name either.
    assert UNMAPPED_FIELD_NAME not in loan.fields


def test_three_synthetic_standin_loans_all_adapt_with_zero_crashes(tmp_path):
    """Mirrors Acceptance Scenario 4 / SC-001's "all 3 loans, zero crashes"
    shape, but against 3 hand-authored SYNTHETIC stand-ins -- the live run
    against the actual 3 real, already-acquired loans (T012) is a separate,
    documented, manual/non-CI script requiring live AWS S3 credentials; see
    the skip-marked test at the bottom of this file."""
    from eval_real.adapter import RealLoanAdapter

    adapter = RealLoanAdapter()
    for i in range(1, 4):
        loan_id = f"SYN-STANDIN-{i:03d}"
        bundle_dir = str(tmp_path / loan_id)
        _write_synthetic_bundle(bundle_dir, loan_id)

        labeled_loan = adapter.adapt(
            bundle_dir=bundle_dir, loan_id=loan_id, expected_verdicts={},
        )
        loan, _expected, _prov = labeled_loan
        assert isinstance(loan, CanonicalLoan)
        # Must score cleanly too (SC-001's second half).
        TP.score([labeled_loan])


# --------------------------------------------------------------------------- #
# T008 -- prove, then close, the score() KeyError gap (FR-003).
#
# This needs no eval_real code at all -- it is a regression test against the
# CURRENT, already-shipped `test_properties.score()`. Run today (before
# FR-003's `prov.get("mutations", [])` hardening lands), it is expected to
# fail RED with exactly `KeyError: 'mutations'` -- confirmed by hand before
# writing this file (see conversation record) and asserted structurally
# below. It will turn green automatically once FR-003 ships, with no edit
# needed to this test.
# --------------------------------------------------------------------------- #
def test_score_does_not_raise_keyerror_when_prov_omits_mutations_key():
    """FR-002/FR-003 regression guard.

    `score()`'s mismatch-message formatting today does
    `'; '.join(prov['mutations']) or 'clean'` unconditionally the instant any
    scored tuple mismatches. A `prov` dict that omits the "mutations" key
    entirely (a real, plausible shape for any tuple producer that doesn't
    follow FR-002's exact minimum contract) currently raises `KeyError`.
    FR-003 hardens this one call site to `prov.get('mutations', [])`.
    """
    loan = G.build_clean(seed=4242)
    # Deliberately WRONG expected verdict (the real verdict is PASS on a
    # clean loan) -- forces score()'s mismatch-message-formatting branch to
    # execute, which is exactly where the unguarded `prov['mutations']`
    # access lives.
    expected = {"chk-note-signed": "FAIL"}
    prov = {"source": "expert-labeled", "loan_id": "SYN-STANDIN-KEYERR"}  # no "mutations" key

    report = TP.score([(loan, expected, prov)])

    assert report["checks_scored"] == 1
    assert report["exact_match"] == 0
    assert len(report["mismatches"]) == 1


def test_score_keyerror_gap_is_specifically_about_the_missing_mutations_key():
    """Names the exact failure mode (not just "it crashes") -- matches
    spec.md's Foundation section finding precisely, so this test can't pass
    for the wrong reason (e.g. a different, unrelated crash)."""
    loan = G.build_clean(seed=4243)
    expected = {"chk-note-signed": "FAIL"}
    prov_missing_mutations = {"source": "expert-labeled", "loan_id": "SYN-STANDIN-KEYERR-2"}

    try:
        TP.score([(loan, expected, prov_missing_mutations)])
    except KeyError as exc:
        pytest.fail(
            "score() must not raise KeyError once FR-003 lands; today (pre-"
            f"patch) it does, specifically on missing key {exc!s} -- this "
            "failure is EXPECTED before FR-003 ships and should read exactly "
            "'mutations' as the missing key."
        )


# --------------------------------------------------------------------------- #
# Live/manual-only (T012) -- NOT executed here, by design.
# --------------------------------------------------------------------------- #
@pytest.mark.skip(
    reason="Requires live AWS S3 access to the real closed-loan bundles "
           "already acquired for this feature (see spec.md Foundation "
           "section) plus Kayla-adjudicated expert labels -- neither is "
           "available in this test environment, and this project's own "
           "convention keeps AWS-dependent runs out of `pytest p0/tests` "
           "(mirrors p0/experiment_g3/llm_arm.py). Run manually via "
           "eval_real.s3_client + eval_real.adapter once credentials and "
           "labels exist -- never as part of the default CI/pytest suite."
)
def test_all_three_real_acquired_loans_adapt_without_crash_LIVE_MANUAL_ONLY():
    """SC-001's true, live variant (T012). Intentionally not implemented --
    this stub exists only to name where that live check belongs and what it
    needs, without executing it or referencing any real loan id, S3 path, or
    PII value in this repository."""
    pytest.skip("live S3 + real loan run -- manual only, see docstring")
