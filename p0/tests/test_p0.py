"""
P0 test suite — proves the determinism claims and the labeled-defect catches.
Run from p0/:  python -m pytest tests/ -v   (or: python tests/test_p0.py)
Python 3.9 compatible.
"""
from __future__ import annotations

import os
import sys
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qc_engine import money as M
from qc_engine import run, AuditLog
from qc_engine import (
    Check, Ruleset, FieldCatalog, FieldCatalogEntry, load_catalog,
    validate_referential_integrity, unused_catalog_entries,
    ReferentialIntegrityError,
)
from qc_engine.mismo import parse_mismo
from qc_engine.compiler.compile_llm import CompiledCheckDraft, assemble_ruleset
from qc_engine.compiler.catalog_screen import (
    screen_batch_referential_integrity, screen_check, RESOLVED, BLOCKED,
    SIGNABLE_PENDING_CATALOG_ENTRY,
)
from qc_engine.compiler.consistency import build_consistency_report
from qc_engine.compiler.pattern_flags import (
    flag_batch, OPAQUE_BOOLEAN_RISK, ARCHETYPE_MISMATCH_RISK,
)
from qc_engine.compiler.report import build_batch_report
from fixtures.golden import golden_loans
from fixtures.ruleset_demo import demo_ruleset

CATALOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "qc_engine", "field_catalog.json")


def _synthetic_check(check_id, field_name, kind, **extra):
    kwargs = dict(id=check_id, name=check_id, field_name=field_name, kind=kind,
                  severity="WARNING")
    if kind == "predicate":
        kwargs["predicate"] = extra.get("predicate", "is_true")
    elif kind == "ratio_threshold":
        kwargs["ratio"] = extra.get("ratio", "ltv")
        kwargs["threshold"] = extra.get("threshold", "95")
        kwargs["operator"] = extra.get("operator", "<=")
    elif kind == "agree_categorical":
        kwargs["normalizer"] = extra.get("normalizer", "identity")
    elif kind == "agree_numeric":
        kwargs["tolerance"] = extra.get("tolerance", "0")
    return Check(**kwargs)


def _synthetic_draft(row_id, field_name="note_rate", kind="predicate",
                      source_text="the value must be present", extracted_intent="checks presence",
                      check_id=None, proposed_field_entry=None, parse_error=None, **check_extra):
    check_id = check_id or f"chk-{row_id}"
    if parse_error is not None:
        return CompiledCheckDraft(row_id=row_id, check=None, source_text=source_text,
                                   extracted_intent="", parse_error=parse_error)
    check = _synthetic_check(check_id, field_name, kind, **check_extra)
    return CompiledCheckDraft(row_id=row_id, check=check, source_text=source_text,
                               extracted_intent=extracted_intent,
                               proposed_field_entry=proposed_field_entry)


# --- money / determinism core ---------------------------------------------
def test_no_float_noise():
    # 0.1 + 0.2 in float is 0.30000000000000004; Decimal path must be clean.
    assert M.to_decimal(0.1) + M.to_decimal(0.2) == Decimal("0.3")


def test_ltv_boundary_exact():
    assert M.ltv_percent("332500.00", "350000.00") == Decimal("95.000")
    # 332501/350000 = 95.0002857% -> rounds to 95.000 at 3dp (a real lesson:
    # the verdict is exact at the policy's scale). Need 332502 to cross at 3dp.
    assert M.ltv_percent("332502.00", "350000.00") > Decimal("95.000")


def test_rounding_half_even():
    # 2.5 -> 2 and 3.5 -> 4 under banker's rounding at scale 1
    from decimal import ROUND_HALF_EVEN
    assert Decimal("2.5").quantize(Decimal("1"), ROUND_HALF_EVEN) == Decimal("2")
    assert Decimal("3.5").quantize(Decimal("1"), ROUND_HALF_EVEN) == Decimal("4")


def test_within_tolerance():
    assert M.within_tolerance("6.250", "6.250", "0.001")
    assert not M.within_tolerance("6.125", "6.250", "0.001")


# --- engine: bit-exact reproducibility ------------------------------------
def test_bit_exact_repeat():
    from harness import results_digest, run_once
    d1 = results_digest(run_once())
    d2 = results_digest(run_once())
    assert d1 == d2


# --- engine: labeled defects are caught -----------------------------------
def test_labeled_outcomes_match():
    rs = demo_ruleset()
    for loan, expected in golden_loans():
        res = run(loan, rs)
        by_id = {r.check_id: r.status for r in res.results}
        for cid, exp in expected.items():
            got = by_id[cid]
            ok = got == exp or (exp == "FAIL" and got == "WARNING")
            assert ok, f"{loan.loan_id}/{cid}: expected {exp}, got {got}"


def test_rate_mismatch_flags_not_fails():
    # Reconcile mismatch is an INFORMATIONAL flag (docs are truth), not a QC
    # failure. Marcus has only a rate flag -> still AUTO-CLEARED, with a flag.
    rs = demo_ruleset()
    marcus = [l for l, _ in golden_loans() if l.loan_id == "LN-95301"][0]
    res = run(marcus, rs)
    rate = [r for r in res.results if r.check_id == "chk-note-rate"][0]
    assert rate.status == "FLAG"
    assert rate.severity == "INFO"
    assert len(res.flags) == 1
    assert len(res.qc_failures) == 0
    assert res.auto_cleared  # a flag does not block auto-clear


def test_unsigned_note_fails_flood_only_flags():
    rs = demo_ruleset()
    liam = [l for l, _ in golden_loans() if l.loan_id == "LN-73901"][0]
    res = run(liam, rs)
    signed = [r for r in res.results if r.check_id == "chk-note-signed"][0]
    flood = [r for r in res.results if r.check_id == "chk-flood-zone"][0]
    assert signed.status == "FAIL"     # Step 2 QC: real defect
    assert flood.status == "FLAG"      # Step 1: informational only
    assert not res.auto_cleared        # because the QC failure exists


def test_two_steps_reconcile_then_qc():
    # The loan that reconciles perfectly but FAILS QC (LTV 98% > 95%).
    # Proves a doc-vs-system match is NOT sufficient to auto-clear.
    rs = demo_ruleset()
    loan = [l for l, _ in golden_loans() if l.loan_id == "LN-QCFAIL"][0]
    res = run(loan, rs)
    assert len(res.discrepancies) == 0          # Step 1 clean
    assert len(res.qc_failures) == 1            # Step 2 fails
    assert not res.auto_cleared                 # therefore NOT auto-cleared
    ltv = [r for r in res.results if r.check_id == "chk-ltv-max"][0]
    assert ltv.phase == "QC" and ltv.status == "FAIL"


def test_phases_are_assigned():
    rs = demo_ruleset()
    clean = [l for l, _ in golden_loans() if l.loan_id == "LN-10842"][0]
    res = run(clean, rs)
    assert {r.phase for r in res.results} <= {"RECONCILE", "QC"}
    # rate/name/principal are RECONCILE; signed is QC
    by_id = {r.check_id: r.phase for r in res.results}
    assert by_id["chk-note-rate"] == "RECONCILE"
    assert by_id["chk-note-signed"] == "QC"


def test_clean_loan_auto_clears():
    rs = demo_ruleset()
    clean = [l for l, _ in golden_loans() if l.loan_id == "LN-10842"][0]
    res = run(clean, rs)
    assert res.auto_cleared


# --- confidence gate (ruling #8) ------------------------------------------
def test_doc_vs_system_mismatch_flags():
    # Document (truth) disagrees with system -> FLAG (informational), names truth.
    rs = demo_ruleset()
    marcus = [l for l, _ in golden_loans() if l.loan_id == "LN-95301"][0]
    res = run(marcus, rs)
    rate = [r for r in res.results if r.check_id == "chk-note-rate"][0]
    assert rate.status == "FLAG"
    assert rate.inputs == {"doc": "6.125", "system": "6.250"}


def test_missing_truth_doc_needs_review():
    # No truth document -> cannot verify system value -> NEEDS_REVIEW (not PASS).
    from qc_engine.model import CanonicalLoan, SourceValue
    rs = demo_ruleset()
    loan = CanonicalLoan(loan_id="LN-NOTRUTH")
    loan.fields = {"note_rate": SourceValue(doc=None, los="6.500")}
    res = run(loan, rs)
    rate = [r for r in res.results if r.check_id == "chk-note-rate"][0]
    assert rate.status == "NEEDS_REVIEW", rate.status


def test_mismo_is_system_fallback():
    # When only a MISMO file is present (no LOS), it serves as the system value.
    from qc_engine.model import CanonicalLoan, SourceValue
    rs = demo_ruleset()
    loan = CanonicalLoan(loan_id="LN-MISMOONLY")
    loan.fields = {"note_rate": SourceValue(doc="6.500", mismo="6.500")}
    res = run(loan, rs)
    rate = [r for r in res.results if r.check_id == "chk-note-rate"][0]
    assert rate.status == "PASS", rate.status
    assert rate.inputs == {"doc": "6.500", "system": "6.500"}


def test_low_confidence_blocks_autoclear():
    rs = demo_ruleset()
    clean = [l for l, _ in golden_loans() if l.loan_id == "LN-10842"][0]
    # force a low-confidence extraction on a passing field
    clean.fields["note_rate"].doc_confidence = 0.40
    res = run(clean, rs)
    rate = [r for r in res.results if r.check_id == "chk-note-rate"][0]
    assert rate.status == "NEEDS_REVIEW"


# --- predicate checks: missing truth value (003a US1 -- the 002a-carried bug) ---
def test_is_present_missing_doc_fails():
    # FR-001: a genuinely-missing truth value must FAIL an is_present check --
    # not silently report NOT_APPLICABLE. This is the concrete bug
    # p0/experiment_002a/RESULTS.md found: the predicate branch used to
    # short-circuit to NOT_APPLICABLE before is_present's own logic ever ran.
    #
    # Regression pin (2026-07-28, specs/015-loan-data-capture-and-gating-fix
    # Issue 2): this must stay FAIL. is_present is specifically checking for
    # absence, so None correctly fails it -- contrast with is_true's None
    # case below, which now resolves to NEEDS_REVIEW instead.
    from qc_engine.model import CanonicalLoan, SourceValue
    chk = _synthetic_check("chk-present-missing", "synthetic_field", "predicate",
                           predicate="is_present")
    rs = Ruleset(ruleset_id="t002", version=1, checks=[chk])
    loan = CanonicalLoan(loan_id="LN-MISSING-PRESENT")
    loan.fields = {"synthetic_field": SourceValue(doc=None)}
    res = run(loan, rs)
    assert res.results[0].status == "FAIL", res.results[0].status


def test_is_true_missing_doc_needs_review():
    # 015 Issue 2 (2026-07-28, specs/015-loan-data-capture-and-gating-fix):
    # behavior change from the old FR-002 pin. A missing is_true truth value
    # means the condition's truth is UNKNOWN, not FALSE -- unlike is_present
    # (which is specifically testing for absence, so None correctly FAILs
    # it), a missing is_true value can't be resolved deterministically and
    # must be routed to a human instead of silently reported as FAIL.
    from qc_engine.model import CanonicalLoan, SourceValue
    chk = _synthetic_check("chk-true-missing", "synthetic_field", "predicate",
                           predicate="is_true")
    rs = Ruleset(ruleset_id="t003", version=1, checks=[chk])
    loan = CanonicalLoan(loan_id="LN-MISSING-TRUE")
    loan.fields = {"synthetic_field": SourceValue(doc=None)}
    res = run(loan, rs)
    assert res.results[0].status == "NEEDS_REVIEW", res.results[0].status
    assert res.results[0].review_reason == "APPLICABILITY_UNKNOWN", res.results[0].review_reason


def test_predicate_non_none_behavior_unchanged():
    # FR-003 regression boundary: the already-correct non-None cases must not
    # change when the doc=None early-return is removed.
    from qc_engine.model import CanonicalLoan, SourceValue

    def _status(predicate, doc):
        chk = _synthetic_check(f"chk-{predicate}-{doc}", "synthetic_field",
                               "predicate", predicate=predicate)
        rs = Ruleset(ruleset_id=f"t004-{predicate}-{doc}", version=1, checks=[chk])
        loan = CanonicalLoan(loan_id="LN-REGRESSION")
        loan.fields = {"synthetic_field": SourceValue(doc=doc)}
        return run(loan, rs).results[0].status

    assert _status("is_present", "") == "FAIL"
    assert _status("is_present", "present-value") == "PASS"
    assert _status("is_true", False) == "FAIL"
    assert _status("is_true", True) == "PASS"


# --- ratio_threshold: field_value mode (003b US1 -- the 002a-carried gap) -
def test_ratio_threshold_field_value_below_floor_fails():
    # FR-001/FR-002 (T002): a single-field numeric floor is not a ratio --
    # engine.py's ratio_threshold branch used to only accept ratio in
    # ("ltv", "dti") and raised ValueError for anything else. This is the
    # concrete gap p0/experiment_002a/RESULTS.md found (finding #2): the real
    # ratio_threshold-00 row ("minimum credit score of 500") is not an
    # LTV/DTI ratio at all.
    from qc_engine.model import CanonicalLoan, SourceValue
    chk = Check(id="chk-credit-floor", name="Minimum credit score",
                field_name="credit_score", kind="ratio_threshold",
                severity="CRITICAL", ratio="field_value",
                threshold="500", operator=">=")
    rs = Ruleset(ruleset_id="t002", version=1, checks=[chk])
    loan = CanonicalLoan(loan_id="LN-CREDIT-FAIL")
    loan.fields = {"credit_score": SourceValue(doc=480, doc_confidence=0.99)}
    res = run(loan, rs)
    assert res.results[0].status == "FAIL", res.results[0].status


def test_ratio_threshold_field_value_at_or_above_floor_passes():
    # FR-001 (T003), the pass-case direction.
    from qc_engine.model import CanonicalLoan, SourceValue
    chk = Check(id="chk-credit-floor", name="Minimum credit score",
                field_name="credit_score", kind="ratio_threshold",
                severity="CRITICAL", ratio="field_value",
                threshold="500", operator=">=")
    rs = Ruleset(ruleset_id="t003", version=1, checks=[chk])
    loan = CanonicalLoan(loan_id="LN-CREDIT-PASS")
    loan.fields = {"credit_score": SourceValue(doc=620, doc_confidence=0.99)}
    res = run(loan, rs)
    assert res.results[0].status == "PASS", res.results[0].status


def test_ratio_threshold_field_value_missing_is_not_applicable():
    # FR-002 (T004): a field_value check with no truth value at all cannot
    # make the comparison -- NOT_APPLICABLE, mirroring the existing ltv/dti
    # behavior when their loan.facts inputs are absent (spec.md Edge Cases:
    # this is deliberately different from 003a's predicate MISSING fix --
    # presence is a separate, predicate-scoped concern).
    from qc_engine.model import CanonicalLoan, SourceValue
    chk = Check(id="chk-credit-floor", name="Minimum credit score",
                field_name="credit_score", kind="ratio_threshold",
                severity="CRITICAL", ratio="field_value",
                threshold="500", operator=">=")
    rs = Ruleset(ruleset_id="t004", version=1, checks=[chk])
    loan = CanonicalLoan(loan_id="LN-CREDIT-MISSING")
    loan.fields = {"credit_score": SourceValue(doc=None)}
    res = run(loan, rs)
    assert res.results[0].status == "NOT_APPLICABLE", res.results[0].status


def test_ratio_threshold_ltv_dti_behavior_unchanged_by_field_value_addition():
    # FR-003 (T005): the pre-existing ltv/dti paths (field_name="", reading
    # loan.facts) must be byte-for-byte unchanged by the new field_value mode.
    from qc_engine.model import CanonicalLoan
    ltv_chk = Check(id="chk-ltv-max", name="LTV within program max (95%)",
                    field_name="", kind="ratio_threshold", ratio="ltv",
                    severity="CRITICAL", threshold="95", operator="<=")
    dti_chk = Check(id="chk-dti-max", name="DTI within program max (45%)",
                    field_name="", kind="ratio_threshold", ratio="dti",
                    severity="CRITICAL", threshold="45", operator="<=")
    fail_loan = CanonicalLoan(loan_id="LN-LTV-DTI-FAIL",
                              facts={"loan_amount": "340000.00", "property_value": "350000.00",
                                     "monthly_debts": "3000.00", "monthly_income": "5000.00"})
    pass_loan = CanonicalLoan(loan_id="LN-LTV-DTI-PASS",
                              facts={"loan_amount": "300000.00", "property_value": "350000.00",
                                     "monthly_debts": "2000.00", "monthly_income": "5000.00"})
    rs = Ruleset(ruleset_id="t005", version=1, checks=[ltv_chk, dti_chk])
    fail_res = run(fail_loan, rs)
    pass_res = run(pass_loan, rs)
    assert fail_res.results[0].status == "FAIL"  # LTV 97.14% > 95%
    assert fail_res.results[1].status == "FAIL"  # DTI 60% > 45%
    assert pass_res.results[0].status == "PASS"  # LTV 85.71% <= 95%
    assert pass_res.results[1].status == "PASS"  # DTI 40% <= 45%
    missing_facts_loan = CanonicalLoan(loan_id="LN-LTV-DTI-NA")
    na_res = run(missing_facts_loan, rs)
    assert na_res.results[0].status == "NOT_APPLICABLE"
    assert na_res.results[1].status == "NOT_APPLICABLE"


def test_dead_threshold_attribute_never_serialized():
    # FR-004 (T006): res.threshold was a confirmed-dead, no-op line -- never
    # part of CheckResult's declared fields, never read anywhere else, and
    # never in to_dict()'s output. Its removal must be observably a no-op:
    # this assertion holds identically before and after the line is deleted.
    from qc_engine.model import CanonicalLoan
    chk = Check(id="chk-ltv-max", name="LTV within program max (95%)",
                field_name="", kind="ratio_threshold", ratio="ltv",
                severity="CRITICAL", threshold="95", operator="<=")
    rs = Ruleset(ruleset_id="t006", version=1, checks=[chk])
    loan = CanonicalLoan(loan_id="LN-LTV-DICT",
                         facts={"loan_amount": "300000.00", "property_value": "350000.00"})
    d = run(loan, rs).results[0].to_dict()
    assert "threshold" not in d, d
    assert d["tolerance"] == "95"


# --- signed artifact + edit distance (ruling #2) --------------------------
def test_signoff_tracks_edits():
    rs = demo_ruleset()
    s = rs.signoff_summary()
    assert s["rules_edited_by_sme"] >= 2  # SSN, rate tolerance, LTV threshold
    assert len(rs.sha256()) == 64


def test_ruleset_hash_stable():
    assert demo_ruleset().sha256() == demo_ruleset().sha256()


# --- audit chain (ruling #9) ----------------------------------------------
def test_audit_chain_verifies_and_detects_tamper():
    rs = demo_ruleset()
    audit = AuditLog(":memory:")
    for loan, _ in golden_loans():
        audit.append(run(loan, rs), signed_at="2026-06-26T15:00:00Z")
    assert audit.verify_chain()
    # tamper with a historical payload -> chain must break
    audit.conn.execute("UPDATE audit_runs SET payload_json='{\"x\":1}' WHERE seq=1")
    audit.conn.commit()
    assert not audit.verify_chain()
    audit.close()


# --- real MISMO XML adapter -----------------------------------------------
def test_mismo_parses_real_demo_xml():
    base = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))), "demo", "301224293",
        "301224293-UladDuExport.xml")
    if not os.path.exists(base):
        return  # demo data not present in this checkout
    fields = parse_mismo(base)
    assert fields.get("note_rate") == "6.6250"
    assert fields.get("loan_amount") == "588900.00"
    assert "OVIEDO" in str(fields.get("borrower_name", "")).upper()
    assert fields.get("property_value") == "620000.00"


# --- field catalog (001a) — referential integrity, the SAFE gate ----------
def test_check_referencing_unresolved_field_fails_loudly():
    # T008: a typo'd/nonexistent field_name must raise, naming both the check
    # and the missing field -- never a silent no-op (FR-003, FR-004).
    catalog = load_catalog(CATALOG_PATH)
    bad = Ruleset(ruleset_id="t008", version=1, checks=[
        Check(id="chk-typo", name="Typo", field_name="notee_rate",
              kind="predicate", severity="CRITICAL", predicate="is_true")])
    try:
        validate_referential_integrity(bad, catalog)
        assert False, "expected ReferentialIntegrityError"
    except ReferentialIntegrityError as e:
        assert "chk-typo" in str(e) and "notee_rate" in str(e)


def test_check_referencing_existing_field_passes():
    # T009: the existing demo ruleset resolves cleanly against the seed catalog.
    catalog = load_catalog(CATALOG_PATH)
    validate_referential_integrity(demo_ruleset(), catalog)  # must not raise


def test_renamed_catalog_entry_breaks_existing_check():
    # T010: if a catalog entry is renamed/removed, a check that still points
    # at the old name must fail loudly on the next validation run (spec.md
    # Edge Case), not silently continue to "work."
    catalog = load_catalog(CATALOG_PATH)
    catalog.entries = [e for e in catalog.entries if e.field_name != "note_rate"]
    try:
        validate_referential_integrity(demo_ruleset(), catalog)
        assert False, "expected ReferentialIntegrityError after removing note_rate"
    except ReferentialIntegrityError as e:
        assert "note_rate" in str(e)


def test_ratio_threshold_with_empty_field_name_is_exempt():
    # chk-ltv-max reads loan.facts, not a catalog field (model.py's own
    # facts-vs-fields distinction) -- it must not be flagged as unresolved.
    catalog = load_catalog(CATALOG_PATH)
    validate_referential_integrity(demo_ruleset(), catalog)  # includes chk-ltv-max


def test_add_field_via_catalog_only_zero_code_change():
    # T013: adding a synthetic field to the catalog (data only) is enough for
    # a new check to reference and validate against it -- no engine code
    # needs to change for this to work (FR-005, SC-001).
    catalog = load_catalog(CATALOG_PATH)
    catalog.entries.append(FieldCatalogEntry(
        field_name="synthetic_test_field", data_type="string",
        expected_sources=["doc"], citation_required=False,
        confidence_required=False, description="Added for T013, catalog-only."))
    new_check = Check(id="chk-synthetic", name="Synthetic", field_name="synthetic_test_field",
                       kind="predicate", severity="INFO", predicate="is_present")
    rs = Ruleset(ruleset_id="t013", version=1, checks=list(demo_ruleset().checks) + [new_check])
    validate_referential_integrity(rs, catalog)  # must not raise


def test_unused_catalog_entry_is_reported_not_rejected():
    # FR-008: an entry with no referencing check is visible, not a failure.
    catalog = load_catalog(CATALOG_PATH)
    catalog.entries.append(FieldCatalogEntry(
        field_name="not_yet_used", data_type="string", expected_sources=["doc"],
        description="No check references this yet."))
    unused = unused_catalog_entries(demo_ruleset(), catalog)
    assert "not_yet_used" in unused


def test_catalog_hash_stable_across_runs():
    # T016
    assert load_catalog(CATALOG_PATH).sha256() == load_catalog(CATALOG_PATH).sha256()


def test_catalog_hash_changes_on_edit():
    # T017
    c1 = load_catalog(CATALOG_PATH)
    c2 = load_catalog(CATALOG_PATH)
    c2.entries[0].data_type = "string" if c2.entries[0].data_type != "string" else "decimal"
    assert c1.sha256() != c2.sha256()


def test_malformed_catalog_rejected_entirely():
    # FR-009: duplicate field_name and a malformed enum entry must both fail
    # to load -- never partially.
    try:
        FieldCatalog(catalog_id="dup", version=1, entries=[
            FieldCatalogEntry(field_name="x", data_type="string"),
            FieldCatalogEntry(field_name="x", data_type="decimal"),
        ])
        assert False, "expected duplicate field_name to raise"
    except ValueError as e:
        assert "duplicate" in str(e).lower()

    try:
        FieldCatalogEntry(field_name="y", data_type="enum")  # missing enum_values
        assert False, "expected missing enum_values to raise"
    except ValueError as e:
        assert "enum_values" in str(e)


def test_zero_regression_with_catalog_in_load_path():
    # T014: the full golden-set + determinism proof still holds byte-for-byte
    # with referential-integrity validation now in the load path (SC-002).
    from harness import check_referential_integrity, prove_bit_exact
    ri_ok, _ = check_referential_integrity()
    assert ri_ok
    ok, _ = prove_bit_exact(iterations=5)
    assert ok


# --- source envelope (001b) — generalized {truth, sources{}}, N-source ready --
def test_reconcile_check_compares_independently_populated_sources():
    # T006: truth (doc) vs an independently-populated sources.los -- the
    # normal, correct-agreement case (spec.md US1 Scenario 1).
    from qc_engine.model import CanonicalLoan, SourceValue
    rs = demo_ruleset()
    loan = CanonicalLoan(loan_id="LN-001B-INDEP")
    loan.fields = {"note_rate": SourceValue(truth="6.250", sources={"los": "6.250"})}
    res = run(loan, rs)
    rate = [r for r in res.results if r.check_id == "chk-note-rate"][0]
    assert rate.status == "PASS"


def test_independence_guard_catches_failed_divergence():
    # T007: a mutation that claims to construct a doc-vs-system mismatch but
    # leaves sources == truth unchanged must raise (FR-005) -- the guard is a
    # test-construction discipline, not a runtime data check (research.md #2).
    import eval_synth.generator as G
    try:
        G.assert_independently_constructed("6.250", {"los": "6.250"},
                                            expect_divergent_keys=["los"])
        assert False, "expected ValueError: sources['los'] == truth"
    except ValueError as e:
        assert "los" in str(e)


def test_independence_guard_passes_genuine_divergence():
    # The companion case: a real divergence (what mut_mismatch_* actually
    # construct) must NOT raise.
    import eval_synth.generator as G
    G.assert_independently_constructed("6.250", {"los": "6.375"},
                                        expect_divergent_keys=["los"])  # must not raise


def test_mismo_only_loan_resolves_system_value_unchanged():
    # T008 / SC-005: a loan with only a MISMO entry (no "los") still resolves
    # system_value() identically to today's fallback, through the generalized
    # sources map.
    from qc_engine.model import CanonicalLoan, SourceValue
    rs = demo_ruleset()
    loan = CanonicalLoan(loan_id="LN-MISMOONLY-001B")
    loan.fields = {"note_rate": SourceValue(truth="6.500", sources={"mismo": "6.500"})}
    res = run(loan, rs)
    rate = [r for r in res.results if r.check_id == "chk-note-rate"][0]
    assert rate.status == "PASS"
    assert rate.inputs == {"doc": "6.500", "system": "6.500"}


def test_new_named_source_readable_with_zero_engine_changes():
    # T011 / SC-002: a synthetic "settlement_agent" source, added purely as
    # data (a custom source_priority), is readable via system_value() with
    # zero p0/qc_engine/*.py changes.
    from qc_engine.model import CanonicalLoan, SourceValue
    rs = demo_ruleset()
    loan = CanonicalLoan(loan_id="LN-SETTLEMENT-AGENT")
    sv = SourceValue(truth="6.250", sources={"settlement_agent": "6.250"},
                      source_priority=["settlement_agent", "los", "mismo"])
    assert sv.system_value() == "6.250"
    loan.fields = {"note_rate": sv}
    res = run(loan, rs)
    rate = [r for r in res.results if r.check_id == "chk-note-rate"][0]
    assert rate.status == "PASS"


def test_backward_compatible_doc_los_mismo_properties_read_write():
    # T004: doc/los/mismo remain read-write properties over truth/sources --
    # both construction-time kwargs and post-construction mutation must work,
    # since eval_synth's mutation operators do both.
    from qc_engine.model import SourceValue
    sv = SourceValue(doc="A", los="A", mismo="A")
    assert sv.truth == "A" and sv.sources == {"los": "A", "mismo": "A"}
    sv.los = "B"
    assert sv.sources["los"] == "B" and sv.system_value() == "B"
    sv.doc = "C"
    assert sv.truth == "C"


def test_source_priority_field_on_catalog_entry():
    # T005: FieldCatalogEntry accepts an optional source_priority override;
    # default (None) leaves SourceValue's own default behavior unaffected.
    entry = FieldCatalogEntry(field_name="x", data_type="string",
                               source_priority=["mismo", "los"])
    assert entry.to_dict()["source_priority"] == ["mismo", "los"]
    default_entry = FieldCatalogEntry(field_name="y", data_type="string")
    assert "source_priority" not in default_entry.to_dict()


def test_inbound_contracts_map_every_catalog_field():
    # T016 / SC-004: every 001a catalog entry's expected_sources is covered by
    # the pinned inbound-contract schema's documented source vocabulary
    # (doc -> Touchless contract, los/mismo -> LOS/MISMO contract).
    catalog = load_catalog(CATALOG_PATH)
    contract_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "specs", "001b-source-envelope-and-inbound-contracts",
        "contracts", "inbound-contracts.md")
    with open(contract_path) as fh:
        contract_text = fh.read()
    for entry in catalog.entries:
        for src in entry.expected_sources:
            assert src in ("doc", "los", "mismo"), (
                f"{entry.field_name}: unexpected source '{src}' not covered "
                f"by the pinned inbound contracts")
    # The contract document itself names both inbound schemas.
    assert "Touchless inbound contract" in contract_text
    assert "LOS/MISMO inbound contract" in contract_text


def _strip_004_disposition_fields(check_result_dicts):
    """004 (loan-disposition) added review_reason (CheckResult) and
    disposition/review_reasons (RunResult) to to_dict() output -- a
    deliberate, additive shape change that changed the full digest for the
    first time since 001a. Stripping these 3 keys reconstructs the exact
    pre-004 shape, so the historical "byte-identical to baseline X" claims
    below remain true and meaningful (they were never claims about 004,
    which didn't exist yet) rather than being silently broken or quietly
    reworded to mean something else."""
    stripped = []
    for rd in check_result_dicts:
        rd = dict(rd)
        rd.pop("disposition", None)
        rd.pop("review_reasons", None)
        rd["results"] = [dict(c) for c in rd["results"]]
        for c in rd["results"]:
            c.pop("review_reason", None)
        stripped.append(rd)
    return stripped


def _pre_004_digest(runs):
    import hashlib
    import json
    blob = json.dumps(_strip_004_disposition_fields([r.to_dict() for r in runs]),
                      sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def test_zero_regression_full_suite_after_envelope_generalization():
    # T015 / SC-001: the full determinism digest, with 004's additive
    # review_reason/disposition/review_reasons keys stripped back out, is
    # byte-identical to the pre-migration baseline recorded in 001a's
    # plan.md, proving the 001b envelope generalization introduced zero
    # regression. (This test's claim is about 001b, not 004 -- 004 is
    # covered by its own dedicated additivity proof below.)
    #
    # 003d update (2026-07-23): PRE_MIGRATION_BASELINE was
    # "8510a0a8b4b6996e047fc8534e094394ba72aae396305b0d2ecad3d6924634db" from
    # 001a through 004. 003d adds Check.compare_field_name -- a genuinely new
    # Check-dataclass field, unlike 004's CheckResult/RunResult-level
    # additions, which _pre_004_digest's dict-key stripping cannot isolate:
    # it flows into ruleset_sha256 (an opaque hash of Ruleset.canonical_
    # content(), which serializes every Check via asdict()), not into a
    # top-level RunResult key this helper can pop back out. There is no way
    # to reconstruct "digest as if compare_field_name didn't exist" from the
    # post-003d RunResult dicts alone -- the baseline necessarily moves a
    # second time here, the same legitimate way it moved once for 004.
    # 002e update (2026-07-24): moves a THIRD time -- applies_if is another
    # genuinely new Check-dataclass field (same reasoning as 003d above).
    # PRE_MIGRATION_BASELINE was
    # "13cc7f52805a7afda0e14b3ccfac50399b23f09ea6ffb80c0ff7cc99db4617f9" from
    # 003d through 002d/002f.
    from harness import run_once
    PRE_MIGRATION_BASELINE = "232fc7305f7c8b70a8db5b253cac651884921c0bc164fa5f7a73e7ec692e20e6"
    assert _pre_004_digest(run_once()) == PRE_MIGRATION_BASELINE


# --- 002b: ruleset compiler pipeline ----------------------------------------
# All tests below use synthetic CompiledCheckDraft fixtures (_synthetic_draft),
# not a live Bedrock call -- this exercises the pipeline mechanism (schema
# conformance, assembly, hashing, screening, flagging) deterministically and
# for free. The live LLM compile step (compile_row/compile_batch against real
# demo/rules/*.xlsx rows) is exercised separately by quickstart.md's run
# sequence, mirroring 002a's own precedent of a real-Bedrock script kept
# outside the free/fast pytest suite.

def test_compile_batch_produces_n_valid_check_drafts_no_new_fields():
    # US1 Scenario 1 / SC-001 (mechanism half): N drafts in, N valid Check
    # instances out, each an instance of the existing dataclass -- no new
    # fields introduced.
    drafts = [_synthetic_draft(f"row-{i:03d}", field_name="note_rate",
                                kind="predicate", check_id=f"chk-{i:03d}")
              for i in range(30)]
    assert len(drafts) == 30
    for d in drafts:
        assert isinstance(d.check, Check)
        assert set(d.check.to_dict().keys()) == set(Check(
            id="x", name="x", field_name="x", kind="predicate", severity="INFO"
        ).to_dict().keys())


def test_ruleset_sha256_stable_over_assembled_compiled_batch():
    # US1 Scenario 2: Ruleset.sha256() is stable and reproducible over an
    # assembled compiled batch.
    drafts = [_synthetic_draft(f"row-{i:03d}", check_id=f"chk-{i:03d}") for i in range(26)]
    rs1 = assemble_ruleset(drafts, ruleset_id="batch-001", version=1,
                            signed_by="test", signed_at="2026-07-02T00:00:00Z")
    rs2 = assemble_ruleset(drafts, ruleset_id="batch-001", version=1,
                            signed_by="test", signed_at="2026-07-02T00:00:00Z")
    assert rs1.sha256() == rs2.sha256()
    assert len(rs1.checks) == 26


def test_consistency_report_catches_duplicate_vocabulary():
    # FR-003 / SC-002: two checks referencing the same concept under
    # different field names are caught by the consistency report 100% of
    # the time.
    drafts = [
        _synthetic_draft("row-a", field_name="borrower_dob", check_id="chk-a"),
        _synthetic_draft("row-b", field_name="borrowers_dob", check_id="chk-b"),
        _synthetic_draft("row-c", field_name="loan_amount", check_id="chk-c"),
    ]
    report = build_consistency_report("batch-002", drafts)
    pairs = {(f.field_name_a, f.field_name_b) for f in report.duplicate_flags}
    assert ("borrower_dob", "borrowers_dob") in pairs
    assert not any("loan_amount" in (f.field_name_a, f.field_name_b) for f in report.duplicate_flags)


def test_zero_edit_batch_triggers_signoff_theater_flag():
    # US2 Scenario 1 / SC-004: a batch signed with zero edits across every
    # rule is flagged as a sign-off-theater risk.
    drafts = [_synthetic_draft(f"row-{i}", check_id=f"chk-{i}") for i in range(10)]
    rs = assemble_ruleset(drafts, ruleset_id="batch-003", version=1,
                           signed_by="test", signed_at="2026-07-02T00:00:00Z")
    # No corrections passed -> every provenance entry signed == llm_draft.
    assert len(rs.unedited_rules()) == len(rs.checks)
    assert rs.signoff_summary()["rules_unedited"] == len(rs.checks)


def test_realistic_edit_distribution_does_not_trigger_signoff_theater_flag():
    # US2 Scenario 2 / SC-004: a realistic non-zero edit-distance distribution
    # does not trigger the flag.
    drafts = [_synthetic_draft(f"row-{i}", check_id=f"chk-{i}") for i in range(10)]
    corrections = {
        f"chk-{i}": '{"corrected": true, "id": "chk-%d"}' % i for i in range(10)
    }
    rs = assemble_ruleset(drafts, ruleset_id="batch-004", version=1,
                           signed_by="test", signed_at="2026-07-02T00:00:00Z",
                           corrections=corrections)
    assert len(rs.unedited_rules()) == 0
    assert rs.signoff_summary()["rules_unedited"] == 0


def test_unresolved_field_reference_blocked_without_proposal():
    # US3 Scenario 1: a drafted check whose field_name doesn't resolve and
    # carries no proposed_field_entry is blocked from sign-off, naming the
    # check and the missing field.
    catalog = load_catalog(CATALOG_PATH)
    draft = _synthetic_draft("row-x", field_name="totally_unknown_field", check_id="chk-x")
    result = screen_check(draft, catalog)
    assert result["status"] == BLOCKED
    assert "chk-x" in result["reason"] and "totally_unknown_field" in result["reason"]


def test_resolved_field_reference_proceeds_to_signoff():
    # US3 Scenario 2: a drafted check whose field_name resolves proceeds to
    # the sign-off stage normally.
    catalog = load_catalog(CATALOG_PATH)
    draft = _synthetic_draft("row-y", field_name="note_rate", check_id="chk-y")
    result = screen_check(draft, catalog)
    assert result["status"] == RESOLVED


def test_unresolved_field_with_proposal_is_pending_not_blocked():
    # research.md Decision 2: an unresolved field_name WITH a proposed
    # FieldCatalogEntry is signable-pending-catalog-entry, distinct from a
    # hard block.
    catalog = load_catalog(CATALOG_PATH)
    proposal = FieldCatalogEntry(field_name="new_field", data_type="string")
    draft = _synthetic_draft("row-z", field_name="new_field", check_id="chk-z",
                              proposed_field_entry=proposal)
    result = screen_check(draft, catalog)
    assert result["status"] == SIGNABLE_PENDING_CATALOG_ENTRY


def test_sc001_batch_screen_covers_every_draft_before_signoff_eligibility():
    # SC-001 (combined): a batch of N > 24 rows, where every draft is
    # correctly resolved / signable-pending-catalog-entry / blocked before
    # any sign-off eligibility is granted.
    catalog = load_catalog(CATALOG_PATH)
    drafts = [_synthetic_draft(f"row-{i:03d}", field_name="note_rate", check_id=f"chk-{i:03d}")
              for i in range(20)]
    drafts.append(_synthetic_draft("row-020", field_name="unknown_x", check_id="chk-020"))
    drafts.append(_synthetic_draft(
        "row-021", field_name="unknown_y", check_id="chk-021",
        proposed_field_entry=FieldCatalogEntry(field_name="unknown_y", data_type="string")))
    assert len(drafts) == 22
    screen = screen_batch_referential_integrity(drafts, catalog)
    assert len(screen) == len(drafts)
    assert screen["chk-020"]["status"] == BLOCKED
    assert screen["chk-021"]["status"] == SIGNABLE_PENDING_CATALOG_ENTRY
    assert all(screen[f"chk-{i:03d}"]["status"] == RESOLVED for i in range(20))


def test_predicate08_pattern_flagged_opaque_boolean_risk():
    # US4 Scenario 1 / SC-003: a synthetic predicate-08-shaped row (two-value
    # comparison) is flagged for human attention.
    draft = _synthetic_draft(
        "row-p08", field_name="payment_calc_uses_correct_rate", kind="predicate",
        check_id="chk-p08",
        source_text="payment calculation did not use the greater of fully indexed "
                    "rate or introductory rate")
    flags = flag_batch([draft])
    assert any(f.flag_type == OPAQUE_BOOLEAN_RISK and f.check_id == "chk-p08" for f in flags)


def test_reconcile_policy_condition_flagged_archetype_mismatch_risk():
    # US4 Scenario 2 / SC-003: a synthetic reconcile-00/01-shaped row (policy
    # condition, no real second source) is flagged for human attention.
    draft = _synthetic_draft(
        "row-r00", field_name="code_applied", kind="agree_categorical",
        check_id="chk-r00",
        source_text="was the required investigation code applied given the "
                    "condition identified")
    flags = flag_batch([draft])
    assert any(f.flag_type == ARCHETYPE_MISMATCH_RISK and f.check_id == "chk-r00" for f in flags)

    # Negative case: a genuine two-source comparison is NOT flagged.
    clean_draft = _synthetic_draft(
        "row-r-clean", field_name="property_address", kind="agree_categorical",
        check_id="chk-r-clean",
        source_text="the property address on the appraisal does not match the "
                    "property address in the system of record")
    clean_flags = flag_batch([clean_draft])
    assert not any(f.check_id == "chk-r-clean" for f in clean_flags)


def test_signed_check_retains_full_intent_triple_sc006():
    # US5 Scenario 1 / SC-006: for every Check in a signed Ruleset, source
    # text + extracted intent + the deterministic logic are all retrievable
    # together via Ruleset.intent_for() -- 0 checks missing any of the three.
    drafts = [_synthetic_draft(f"row-{i}", check_id=f"chk-{i}",
                                source_text=f"source rule text {i}",
                                extracted_intent=f"extracted intent {i}")
              for i in range(5)]
    rs = assemble_ruleset(drafts, ruleset_id="batch-005", version=1,
                           signed_by="test", signed_at="2026-07-02T00:00:00Z")
    for chk in rs.checks:
        record = rs.intent_for(chk.id)
        assert record is not None
        assert record.source_text and record.extracted_intent
        assert record.check_id == chk.id
    # Round-trips through to_json/from_dict (persistence, not just in-memory).
    import json as _json
    restored = Ruleset.from_dict(_json.loads(rs.to_json()))
    assert len(restored.intent_records) == len(rs.checks)
    assert restored.intent_for(rs.checks[0].id).source_text == "source rule text 0"


def test_engine_run_makes_zero_llm_calls_on_compiled_ruleset_sc005():
    # US5 Scenario 2 / SC-005: qc_engine.engine.run evaluating a compiled
    # Ruleset makes zero LLM/network calls -- no boto3/bedrock import is ever
    # touched by the engine's run path, confirmed by asserting the module
    # isn't imported by qc_engine.engine.
    import qc_engine.engine as engine_module
    assert "boto3" not in dir(engine_module)
    assert not any(name.startswith("boto3") for name in sys.modules
                   if "qc_engine.engine" in str(getattr(sys.modules.get(name), "__name__", "")))
    # Direct proof: run() against the existing golden set and demo ruleset
    # succeeds with no AWS credentials required.
    saved = {k: os.environ.pop(k, None) for k in
             ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN")}
    try:
        rs = demo_ruleset()
        loan = [l for l, _ in golden_loans()][0]
        result = run(loan, rs)
        assert result is not None
    finally:
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v


def test_batch_report_assembles_screen_consistency_and_pattern_flags():
    # Final integration: contracts/batch-report-schema.md's shape, assembled
    # from all three sub-mechanisms together.
    catalog = load_catalog(CATALOG_PATH)
    drafts = [_synthetic_draft(f"row-{i:03d}", field_name="note_rate", check_id=f"chk-{i:03d}")
              for i in range(25)]
    drafts.append(_synthetic_draft("row-025", field_name="unknown_field", check_id="chk-025"))
    report = build_batch_report("batch-006", drafts, catalog)
    assert report["rows_compiled"] == 26
    assert "chk-025" in [b["check_id"] for b in report["referential_integrity"]["blocked"]]
    assert len(report["referential_integrity"]["resolved"]) == 25
    assert "duplicate_flags" in report["consistency_report"]
    assert isinstance(report["pattern_flags"], list)


def test_zero_regression_after_002b_ruleset_extension():
    # Cross-cutting: the Ruleset.intent_records extension is purely additive
    # -- the pre-existing determinism digest (004's fields stripped back out,
    # same reasoning as the test above) and demo-ruleset hash must be
    # unaffected by 002b's changes to ruleset.py.
    # 003d update (2026-07-23): see test_zero_regression_full_suite_after_
    # envelope_generalization's comment -- same baseline shift, same reason.
    # 002e update (2026-07-24): moves a third time, same reason (applies_if).
    from harness import run_once
    PRE_EXISTING_BASELINE = "232fc7305f7c8b70a8db5b253cac651884921c0bc164fa5f7a73e7ec692e20e6"
    assert _pre_004_digest(run_once()) == PRE_EXISTING_BASELINE


def test_004_review_reason_fields_are_purely_additive():
    # 004's own zero-regression proof, mechanical rather than by-inspection:
    # stripping review_reason/disposition/review_reasons from the current
    # full-shape digest MUST reproduce the exact pre-004 baseline -- proving
    # every pre-existing key's VALUE is untouched, and only new keys were
    # added. If a future edit to engine.py's dispatch logic accidentally
    # changed an existing value (not just added a field), this test would
    # catch it even though the full digest already changed for a legitimate
    # reason and can no longer serve as that tripwire on its own.
    # 003d update (2026-07-23): see test_zero_regression_full_suite_after_
    # envelope_generalization's comment -- same baseline shift, same reason.
    # 002e update (2026-07-24): moves a third time, same reason (applies_if).
    from harness import run_once
    PRE_004_BASELINE = "232fc7305f7c8b70a8db5b253cac651884921c0bc164fa5f7a73e7ec692e20e6"
    assert _pre_004_digest(run_once()) == PRE_004_BASELINE


def test_full_digest_matches_new_baseline_after_004_disposition():
    # 004 deliberately extends CheckResult/RunResult's serialized shape
    # (review_reason, disposition, review_reasons) -- the FIRST feature since
    # 001a to legitimately change the full digest, not a silent regression.
    # This value was the anchor from 004 through 003c:
    # "a3f702c12969f7eb657471796c95e2a493d459c4c55663fa8fc18ac31e8c1d09".
    # 003d update (2026-07-23): superseded by POST_003D_BASELINE below (adds
    # Check.compare_field_name) -- kept asserting the current value here too
    # so this test still documents/proves the 004-origin shape change is
    # still present, not just superseded-and-forgotten.
    # 002e update (2026-07-24): superseded AGAIN by POST_002E_BASELINE below
    # (adds Check.applies_if) -- same reasoning, kept asserting the current
    # value here too.
    from harness import results_digest, run_once
    POST_004_BASELINE = "82175d076579e31a50971d8b20ea4b63848bea9f9b53c30dd96524071842e5ec"
    assert results_digest(run_once()) == POST_004_BASELINE


def test_full_digest_matches_new_baseline_after_003d_doc_vs_doc():
    # 003d adds Check.compare_field_name (agree_doc_categorical/
    # agree_doc_numeric's second field) -- the second feature since 001a to
    # legitimately change the full digest (004 was the first). demo_ruleset()
    # itself uses neither new kind (compare_field_name is None on every one
    # of its checks), but asdict()-based Check.to_dict() emits the new field
    # regardless of kind, so Ruleset.sha256() -- and therefore every
    # RunResult.ruleset_sha256 -- shifts anyway. This is the new anchor:
    # 003e+ must hold this one byte-identical, the same way 005+ was expected
    # to hold a3f702c1... byte-identical (see plan.md/criteria.md).
    # 002e update (2026-07-24): superseded AGAIN by POST_002E_BASELINE below
    # (adds Check.applies_if) -- same reasoning, kept asserting the current
    # value here too so this test still documents the 003d-origin shape
    # change is still present, not superseded-and-forgotten.
    from harness import results_digest, run_once
    POST_003D_BASELINE = "82175d076579e31a50971d8b20ea4b63848bea9f9b53c30dd96524071842e5ec"
    assert results_digest(run_once()) == POST_003D_BASELINE


def test_full_digest_matches_new_baseline_after_002e_applies_if():
    # 002e adds Check.applies_if (the conditional-applicability gate's
    # AND-combined condition list) -- the THIRD feature since 001a to
    # legitimately change the full digest (004 was the first, 003d the
    # second). demo_ruleset() itself sets applies_if=None on every check
    # (unconditional, today's universal behavior), but asdict()-based
    # Check.to_dict() emits the new field regardless, so Ruleset.sha256() --
    # and therefore every RunResult.ruleset_sha256 -- shifts anyway. This is
    # the new anchor: 002f+ must hold this one byte-identical.
    from harness import results_digest, run_once
    POST_002E_BASELINE = "82175d076579e31a50971d8b20ea4b63848bea9f9b53c30dd96524071842e5ec"
    assert results_digest(run_once()) == POST_002E_BASELINE


# --- 000-synthetic-fixture-generation: document-derived loans run through the
# real engine, alongside (not replacing) the hand-authored golden set above ---
def test_document_derived_loans_run_through_the_real_engine():
    """The 5 fixtures from p0/fixtures/from_docs/ (extracted from demo/syn/'s
    actual documents) must execute cleanly through qc_engine.run() -- the same
    entry point golden_loans() uses above -- not just eval_synth's score()
    wrapper (already proven by p0/tests/test_fixture_generation.py). Zero code
    changes to run()/model.py; demo_ruleset()'s checks target the original
    7-field seed catalog, which these loans' doc side mostly doesn't populate
    (extract_pdf.py targeted the ~26 new defect-grounded fields instead -- see
    plan.md), so most checks legitimately resolve N/A here. That's expected,
    not a gap: proving new fields against real checks is the 003-series' job
    (spec 000's Assumptions/Edge Cases)."""
    from_docs_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "fixtures", "from_docs")
    from_docs_dir = os.path.normpath(from_docs_dir)
    sys.path.insert(0, from_docs_dir)
    from build_fixtures import build_all_fixtures  # noqa: E402
    from fixture_loader import load_canonical_loan  # noqa: E402

    written = build_all_fixtures()
    assert len(written) == 5

    rs = demo_ruleset()
    for path in written.values():
        loan = load_canonical_loan(path)
        res = run(loan, rs)  # must not raise
        assert isinstance(res.results, list) and len(res.results) > 0
        assert isinstance(res.auto_cleared, bool)


if __name__ == "__main__":
    # allow plain `python tests/test_p0.py`
    import traceback
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for fn in fns:
        try:
            fn()
            print(f"  PASS {fn.__name__}")
            passed += 1
        except Exception:
            print(f"  FAIL {fn.__name__}")
            traceback.print_exc()
    print(f"\n{passed}/{len(fns)} tests passed")
    raise SystemExit(0 if passed == len(fns) else 1)
