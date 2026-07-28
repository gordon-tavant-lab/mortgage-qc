"""
005 US1 -- the generalized scenario constructor (spec.md FR-001-004, SC-001).

RED-STATE NOTICE: `p0/eval_synth/scenario_construction.py` does not exist yet.
This file is written FIRST, against the module contract documented below, so
the future implementation has an unambiguous target (TDD: red, then green).
Every test here is a REAL assertion, not a placeholder -- once
`scenario_construction.py` exists with this shape, these tests should pass
with zero further edits to this file.

ASSUMED MODULE CONTRACT for `p0/eval_synth/scenario_construction.py`
(the promoted, generalized successor to
`p0/experiment_002a/score_drafts.py`'s `SCORERS` dict -- spec.md Key
Entities, plan.md Project Structure):

    @dataclass
    class ConstructedScenario:
        check_id: str
        kind: str
        ok: bool                                   # False == FR-002 failure
        pass_loan: Optional[CanonicalLoan] = None
        fail_loan: Optional[CanonicalLoan] = None
        expected_pass_status: Optional[str] = None  # e.g. "PASS"
        expected_fail_status: Optional[str] = None  # e.g. "FAIL" | "FLAG"
        provenance: Dict[str, Any] = field(default_factory=dict)
        error: Optional[str] = None                 # set iff ok is False

    STRATEGIES: Dict[str, Callable[[Check], ConstructedScenario]]
        # one entry per live engine kind: predicate, ratio_threshold,
        # agree_categorical, agree_numeric, agree_doc_categorical,
        # agree_doc_numeric (FR-001).

    def construct_scenario(chk: Check) -> ConstructedScenario:
        '''Look up chk.kind in STRATEGIES; on a registered kind, build a
        pass-case + fail-case CanonicalLoan (reading field_catalog.json's
        data_type for chk.field_name/compare_field_name -- no per-field
        mutation function), and satisfy every chk.applies_if precondition on
        BOTH constructed loans before returning (FR-003). On an
        unregistered kind, MUST NOT raise -- return ok=False with a non-empty
        `error`, never a silent skip (FR-002).'''

Run from p0/:  python -m pytest tests/test_scenario_construction.py -v
Python 3.9 compatible.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "eval_synth"))

from qc_engine import run                                    # noqa: E402
from qc_engine.model import CanonicalLoan                    # noqa: E402
from qc_engine.ruleset import Check, Ruleset                 # noqa: E402
from qc_engine.catalog import load_catalog                   # noqa: E402

# The module under test -- does not exist yet (red state, expected).
import scenario_construction as SC                            # noqa: E402


CATALOG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "qc_engine", "field_catalog.json")

CATALOG = load_catalog(CATALOG_PATH)

# --- real field_catalog.json entries, one per construction scenario below,
# picked by direct inspection (not invented) so this file never silently
# drifts from the real 379-entry vocabulary the constructor must key off. ---
BOOLEAN_FIELD = "arm_preloan_disclosure_present"      # data_type=boolean
STRING_PRESENCE_FIELD = "appraisal_comp_01_comp_num"  # data_type=string
CATEGORICAL_RECONCILE_FIELD = "borrower_name"          # doc/los/mismo, string
NUMERIC_RECONCILE_FIELD = "note_rate"                  # doc/los/mismo, decimal
DOC_VS_DOC_CATEGORICAL_A = "loan_purpose_1003"          # doc-only, string
DOC_VS_DOC_CATEGORICAL_B = "loan_purpose_cd"            # doc-only, string
DOC_VS_DOC_NUMERIC_A = "liability_disclosed_on_1003"    # doc-only, decimal
DOC_VS_DOC_NUMERIC_B = "liability_amount_credit_report"  # doc-only, decimal
PRECONDITION_FIELD = "loan_purpose_1003"                # doc-only, string


def _assert_real_catalog_entry(field_name: str, expected_data_type: str) -> None:
    entry = CATALOG.get(field_name)
    assert entry is not None, f"{field_name} must be a real field_catalog.json entry"
    assert entry.data_type == expected_data_type, (
        f"{field_name}: expected data_type={expected_data_type}, got {entry.data_type}")


def _run_single(chk: Check, loan: CanonicalLoan):
    rs = Ruleset(ruleset_id=f"t-{chk.id}", version=1, checks=[chk])
    return run(loan, rs)


def _assert_pass_fail_pair(chk: Check, expected_fail_status: str) -> "SC.ConstructedScenario":
    """Shared assertion for T004-T009: construct_scenario succeeds, and
    running BOTH constructed loans through the real engine produces exactly
    the kind's expected verdict pair (spec.md US1 Acceptance Scenario 1)."""
    scn = SC.construct_scenario(chk)
    assert scn.ok, f"construction failed for kind={chk.kind}: {scn.error}"
    assert scn.pass_loan is not None and scn.fail_loan is not None

    pass_res = _run_single(chk, scn.pass_loan)
    fail_res = _run_single(chk, scn.fail_loan)
    assert pass_res.results[0].status == "PASS", (
        f"{chk.kind} pass-case: expected PASS, got {pass_res.results[0].status}")
    assert fail_res.results[0].status == expected_fail_status, (
        f"{chk.kind} fail-case: expected {expected_fail_status}, got "
        f"{fail_res.results[0].status}")
    # The scenario's own recorded expectations must agree with what the real
    # engine just proved -- the constructor isn't allowed to claim a verdict
    # pair it didn't actually verify against the real engine.
    assert scn.expected_pass_status == "PASS"
    assert scn.expected_fail_status == expected_fail_status
    return scn


# --- T004: predicate (is_true and is_present) -------------------------------
def test_construct_scenario_predicate_is_true():
    _assert_real_catalog_entry(BOOLEAN_FIELD, "boolean")
    chk = Check(id="chk-sc-predicate-istrue", name="ARM disclosure present",
                field_name=BOOLEAN_FIELD, kind="predicate",
                predicate="is_true", severity="CRITICAL")
    _assert_pass_fail_pair(chk, expected_fail_status="FAIL")


def test_construct_scenario_predicate_is_present():
    _assert_real_catalog_entry(STRING_PRESENCE_FIELD, "string")
    chk = Check(id="chk-sc-predicate-ispresent", name="Comp number present",
                field_name=STRING_PRESENCE_FIELD, kind="predicate",
                predicate="is_present", severity="CRITICAL")
    _assert_pass_fail_pair(chk, expected_fail_status="FAIL")


# --- T005: ratio_threshold (ltv and dti) ------------------------------------
def test_construct_scenario_ratio_threshold_ltv():
    chk = Check(id="chk-sc-ltv", name="LTV within program max", field_name="",
                kind="ratio_threshold", ratio="ltv", severity="CRITICAL",
                threshold="95.000", operator="<=")
    _assert_pass_fail_pair(chk, expected_fail_status="FAIL")


def test_construct_scenario_ratio_threshold_dti():
    chk = Check(id="chk-sc-dti", name="DTI within program max", field_name="",
                kind="ratio_threshold", ratio="dti", severity="CRITICAL",
                threshold="45.000", operator="<=")
    _assert_pass_fail_pair(chk, expected_fail_status="FAIL")


# --- T006: agree_categorical -------------------------------------------------
def test_construct_scenario_agree_categorical():
    _assert_real_catalog_entry(CATEGORICAL_RECONCILE_FIELD, "string")
    chk = Check(id="chk-sc-agree-cat", name="Borrower name agreement",
                field_name=CATEGORICAL_RECONCILE_FIELD, kind="agree_categorical",
                severity="CRITICAL", sources=["doc", "los"], normalizer="identity")
    _assert_pass_fail_pair(chk, expected_fail_status="FLAG")


# --- T007: agree_numeric ------------------------------------------------------
def test_construct_scenario_agree_numeric():
    _assert_real_catalog_entry(NUMERIC_RECONCILE_FIELD, "decimal")
    chk = Check(id="chk-sc-agree-num", name="Note rate agreement",
                field_name=NUMERIC_RECONCILE_FIELD, kind="agree_numeric",
                severity="CRITICAL", sources=["doc", "los"], tolerance="0.001")
    _assert_pass_fail_pair(chk, expected_fail_status="FLAG")


# --- T008: agree_doc_categorical (new coverage, spec.md Gap 4) --------------
def test_construct_scenario_agree_doc_categorical():
    _assert_real_catalog_entry(DOC_VS_DOC_CATEGORICAL_A, "string")
    _assert_real_catalog_entry(DOC_VS_DOC_CATEGORICAL_B, "string")
    chk = Check(id="chk-sc-agree-doc-cat", name="Loan purpose agrees 1003 vs CD",
                field_name=DOC_VS_DOC_CATEGORICAL_A,
                compare_field_name=DOC_VS_DOC_CATEGORICAL_B,
                kind="agree_doc_categorical", severity="CRITICAL",
                sources=["doc"], normalizer="identity")
    scn = _assert_pass_fail_pair(chk, expected_fail_status="FAIL")  # QC phase -> FAIL, not FLAG
    # FR-004: never populate SourceValue.sources{} on either field -- this
    # kind is doc-vs-doc, never doc-vs-system.
    for loan in (scn.pass_loan, scn.fail_loan):
        assert loan.get(chk.field_name).sources == {}, "field_name must stay doc-only"
        assert loan.get(chk.compare_field_name).sources == {}, "compare_field_name must stay doc-only"


# --- T009: agree_doc_numeric (new coverage, spec.md Gap 4) ------------------
def test_construct_scenario_agree_doc_numeric():
    _assert_real_catalog_entry(DOC_VS_DOC_NUMERIC_A, "decimal")
    _assert_real_catalog_entry(DOC_VS_DOC_NUMERIC_B, "decimal")
    chk = Check(id="chk-sc-agree-doc-num", name="Liability agrees 1003 vs credit report",
                field_name=DOC_VS_DOC_NUMERIC_A,
                compare_field_name=DOC_VS_DOC_NUMERIC_B,
                kind="agree_doc_numeric", severity="CRITICAL",
                sources=["doc"], tolerance="0")
    scn = _assert_pass_fail_pair(chk, expected_fail_status="FAIL")  # QC phase -> FAIL
    for loan in (scn.pass_loan, scn.fail_loan):
        assert loan.get(chk.field_name).sources == {}
        assert loan.get(chk.compare_field_name).sources == {}


# --- T010: applies_if precondition-setting (FR-003) -------------------------
def test_construct_scenario_sets_applies_if_precondition_true_before_evaluating():
    _assert_real_catalog_entry(PRECONDITION_FIELD, "string")
    chk = Check(id="chk-sc-precond", name="ARM disclosure present (Purchase only)",
                field_name=BOOLEAN_FIELD, kind="predicate", predicate="is_true",
                severity="CRITICAL",
                applies_if=[{"field_name": PRECONDITION_FIELD, "operator": "==",
                             "value": "Purchase"}])
    scn = SC.construct_scenario(chk)
    assert scn.ok, scn.error
    for loan in (scn.pass_loan, scn.fail_loan):
        precondition_value = loan.get(PRECONDITION_FIELD).doc
        assert precondition_value is not None, (
            "constructed loan must set the applies_if precondition field, "
            "not leave it unset (which would resolve NEEDS_REVIEW, not "
            "reach the check's own pass/fail logic)")
    pass_res = _run_single(chk, scn.pass_loan)
    fail_res = _run_single(chk, scn.fail_loan)
    # Acceptance Scenario 2: the check must be genuinely REACHED -- never
    # silently resolved NOT_APPLICABLE by an unset precondition.
    assert pass_res.results[0].status == "PASS", pass_res.results[0].status
    assert fail_res.results[0].status == "FAIL", fail_res.results[0].status
    assert pass_res.results[0].status != "NOT_APPLICABLE"
    assert fail_res.results[0].status != "NOT_APPLICABLE"


# --- T011: unregistered kind -> explicit construction failure (FR-002) -----
def test_construct_scenario_unregistered_kind_returns_structured_failure():
    chk = Check(id="chk-sc-unregistered", name="Some future engine kind",
                field_name="some_future_field", kind="totally_unregistered_kind_xyz",
                severity="CRITICAL")
    # Must NOT raise -- a construction-failure record, never an exception
    # that would kill the whole coverage run, and never a silent skip.
    scn = SC.construct_scenario(chk)
    assert scn.ok is False
    assert scn.error, "an explicit, non-empty error must be recorded"
    assert scn.pass_loan is None
    assert scn.fail_loan is None
    assert scn.check_id == chk.id
    assert scn.kind == chk.kind


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
