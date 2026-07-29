"""
Regression test: loan 01's 5 documented defects (`defect_manifest.json`)
against the comprehensive v8 ruleset (3,203 checks), run through the real
engine -- not the resolved-field-value check `verify_against_defects.py`
already does (that's a different, complementary gate: it confirms the
*fixture* resolves the right field values, not that a *check* fires FAIL
on them).

Baseline before the 2026-07-28 fix: only defect #3 (large deposit) was
correctly caught as FAIL; #1 and #2 were miscompiled (`agree_categorical`
doc-vs-system instead of `agree_doc_categorical` doc-vs-doc) and resolved to
NEEDS_REVIEW; #4 has no catalogued precondition field and needs a
set-membership check-kind this engine doesn't have; #5 has no check at all
-- the "5-mile comp distance" rule doesn't exist anywhere in either sheet of
the real AMQ source workbook.

Run from repo root:  python3 -m pytest p0/tests/test_loan01_defects_vs_comprehensive_ruleset.py -v
Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys

import pytest

_P0 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_REPO_ROOT = os.path.dirname(_P0)
sys.path.insert(0, _P0)
sys.path.insert(0, os.path.join(_P0, "fixtures", "from_docs"))

from fixture_loader import load_canonical_loan  # noqa: E402
from qc_engine.compiler.document_presence_gating import (  # noqa: E402
    apply_document_presence_gates)
from qc_engine.compiler.known_compile_corrections import (  # noqa: E402
    apply_known_compile_corrections)
from qc_engine.engine import run  # noqa: E402
from qc_engine.model import SourceValue  # noqa: E402
from qc_engine.ruleset import Check, Ruleset  # noqa: E402

LOAN_JSON = os.path.join(_P0, "fixtures", "from_docs", "loan_01.json")
# Track F (2026-07-28): v4 instead of v3 -- strict superset (v3's 6
# derivations + doc_present_* passthrough), so apply_document_presence_gates
# below can actually resolve. Single source of truth with run_018.
# Track A2 (2026-07-29): v5 instead of v4 -- strict superset (v4's 7
# derivations + 4 new precondition derivations: appraisal_waiver_type,
# borrower_income_type, credit_report_present_for_all_applicants,
# closing_funds_asset_type). Single source of truth with run_018.
LOAN_PROFILE_V3 = os.path.join(_REPO_ROOT, "storage", "loan_profiles", "v5", "loan_01.json")
RULESET_PATH = os.path.join(_REPO_ROOT, "result", "rules", "comprehensive_e2e_v8_ruleset.json")


@pytest.fixture(scope="module")
def loan01_results():
    """Loads loan 01 + v3 derived facts, applies the known compile
    corrections (same shared module run_018 uses -- single source of truth,
    no risk of test/production drift), runs the engine once."""
    loan = load_canonical_loan(LOAN_JSON)
    with open(LOAN_PROFILE_V3) as f:
        profile = json.load(f)
    for fact_name, entry in profile.get("derived_facts", {}).items():
        loan.fields[fact_name] = SourceValue(doc=entry["value"])

    with open(RULESET_PATH) as f:
        wrapper = json.load(f)
    checks = [Check(**c) for c in wrapper["content"]["checks"]]
    apply_known_compile_corrections(checks)
    apply_document_presence_gates(checks)
    rs = Ruleset(ruleset_id=wrapper["content"]["ruleset_id"],
                 version=wrapper["content"]["version"], checks=checks)

    result = run(loan, rs)
    return {r.check_id: r for r in result.results}, {c.id: c for c in checks}


# --- Defect #1: employment date mismatch (1003 vs VOE) ----------------------

def test_defect_1_employment_dates_fails(loan01_results):
    results, _ = loan01_results
    r = results["employment-dates-1003-vs-docs-agree"]
    assert r.status == "FAIL", (
        "defect #1 (1003 employment start 03/15/2018 vs VOE 05/01/2019) "
        "should FAIL after the agree_doc_categorical correction; got {0}".format(r.status))


# --- Defect #2: title vesting mismatch (1003 vs Title Commitment) -----------

def test_defect_2_title_vesting_fails(loan01_results):
    results, _ = loan01_results
    r = results["title-vesting-1003-vs-commitment"]
    assert r.status == "FAIL", (
        "defect #2 (1003 'a married man' vs Title Commitment TBE) should FAIL "
        "after the agree_doc_categorical correction; got {0}".format(r.status))


# --- Defect #3: unsourced large deposit (already correct -- regression guard)

def test_defect_3_large_deposit_fails(loan01_results):
    results, _ = loan01_results
    r = results["large-deposit-source-not-acceptable"]
    assert r.status == "FAIL", (
        "defect #3 ($15,000 unsourced deposit) was already correctly caught -- "
        "a change here is a real regression, got {0}".format(r.status))


# --- Defect #4: undisclosed liability -- needs a check-kind this engine lacks

@pytest.mark.xfail(
    reason=(
        "defect #4 (undisclosed $412/mo Ally Bank auto liability) needs a "
        "set-membership/line-item-reconciliation check-kind ('does this trade "
        "line appear anywhere in the 1003's disclosed liability list') that "
        "the engine does not have -- only single-value comparisons "
        "(predicate/ratio_threshold/agree_categorical/agree_numeric/"
        "agree_doc_categorical/agree_doc_numeric) exist. The check's own "
        "applies_if precondition, credit_report_present_for_all_applicants, "
        "is also not in field_catalog.json at all, and the check is compiled "
        "with threshold: UNSPECIFIED -- two independent reasons it can't "
        "resolve today, on top of the missing check-kind. See "
        "output/ROADMAP.md #018-set-membership-check-kind."
    ),
    strict=True,
)
def test_defect_4_undisclosed_debt_fails(loan01_results):
    results, _ = loan01_results
    r = results["undisclosed-debt-dti-gap"]
    assert r.status == "FAIL"


# --- Defect #5: appraisal comp distance -- confirmed not a code gap ---------

def test_defect_5_no_matching_check_exists(loan01_results):
    """Defect #5 (Comp #2 distance 8.5mi exceeds guideline) has no
    corresponding check in the ruleset -- confirmed the underlying "5-mile
    comp distance" rule doesn't exist in either sheet of the real AMQ source
    workbook (Post-Closing 5,520 rows, Pre-Funding 4,825 rows -- zero matches
    in both). This is a source-data absence, not a code gap: nothing to fix
    here. This test intentionally asserts the absence rather than being
    silently omitted -- if a check is ever added for this, this test starts
    failing and forces someone to update it instead of staying green forever."""
    _, checks_by_id = loan01_results
    ids_mentioning_comp_distance = [
        cid for cid, chk in checks_by_id.items()
        if "comp" in cid.lower() and ("distance" in cid.lower() or "mile" in cid.lower())
    ]
    # va-appraisal-comp-distance-explanation exists but is VA-program-tagged
    # (loan 01 is Fannie Mae) and checks for presence of an explanation, not
    # a mileage threshold -- not a match for defect #5.
    assert ids_mentioning_comp_distance == ["va-appraisal-comp-distance-explanation"], (
        "expected only the known non-matching VA explanation-presence check; "
        "if a real comp-distance-threshold check now exists, defect #5 may be "
        "fixable -- update this test and output/ROADMAP.md accordingly. "
        "Found: {0}".format(ids_mentioning_comp_distance))
