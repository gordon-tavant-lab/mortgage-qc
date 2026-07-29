"""
Finding #2: tests for `find_structural_kind_mismatches()`
(`p0/qc_engine/compiler/kind_selection_audit.py`) -- the deterministic (no
LLM call) gate that flags a compiled `agree_categorical`/`agree_numeric`
check (doc-vs-*system*) whose field structurally has no system side to
compare against (`field_catalog.json`'s `expected_sources == ["doc"]`), the
general form of the two hand-fixed miscompiles in
`known_compile_corrections.py`.

Mirrors `test_operator_consistency.py`'s exact structure and conventions:
(1) a true-positive floor against the real, currently-shipped
`run_008_comprehensive_8442/ruleset.json` (regenerated fresh here, not read
back from the saved suspects file -- not circular); (2) a MEASURED (not
assumed-zero) false-positive check against checks that already legitimately
use `agree_doc_categorical`/`agree_doc_numeric`; (3)+(4) unit tests proving
`assemble_ruleset()` now applies `apply_known_compile_corrections()`
automatically and excludes NEW (unaudited) structural mismatches from the
signed Ruleset, rather than either shipping them uncorrected or silently
including a structurally-wrong comparison.

`run_008_comprehensive_8442/ruleset.json` itself is read-only in every test
below -- never written to (per task scope: SME correction of that shipped
artifact is out of scope here).

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_P0 = os.path.dirname(_HERE)
_REPO_ROOT = os.path.dirname(_P0)
if _P0 not in sys.path:
    sys.path.insert(0, _P0)

from qc_engine.catalog import load_catalog  # noqa: E402
from qc_engine.compiler import compile_llm as C  # noqa: E402
from qc_engine.compiler.known_compile_corrections import (  # noqa: E402
    apply_known_compile_corrections, KNOWN_CORRECTIONS)
from qc_engine.compiler.kind_selection_audit import find_structural_kind_mismatches  # noqa: E402
from qc_engine.ruleset import Check  # noqa: E402

_RULESET_PATH = os.path.join(
    _P0, "compile_runs", "run_008_comprehensive_8442", "ruleset.json")
_CATALOG_PATH = os.path.join(_P0, "qc_engine", "field_catalog.json")
_SUSPECTS_PATH = os.path.join(
    _REPO_ROOT, "output", "doc_vs_doc_miscompile_suspects_2026-07-29.json")


def _load_checks_fresh():
    """Loads run_008's real checks directly from disk -- a fresh read, never
    mutating the file itself (kept read-only per task scope)."""
    with open(_RULESET_PATH) as f:
        wrapper = json.load(f)
    return [Check(**c) for c in wrapper["content"]["checks"]]


@pytest.fixture(scope="module")
def catalog():
    return load_catalog(_CATALOG_PATH)


@pytest.fixture(scope="module")
def corrected_checks(catalog):
    """run_008's checks, loaded fresh from disk, with the known 2-item
    allowlist applied -- the same order assemble_ruleset() now applies
    automatically (corrections BEFORE the structural detector runs)."""
    checks = _load_checks_fresh()
    apply_known_compile_corrections(checks)
    return checks


@pytest.fixture(scope="module")
def saved_suspect_ids():
    with open(_SUSPECTS_PATH) as f:
        data = json.load(f)
    return {s["check_id"] for s in data["suspects"]}


# --- floor test --------------------------------------------------------------

def test_true_positive_floor_reproduces_saved_suspects(catalog, corrected_checks, saved_suspect_ids):
    """Independently regenerated (fresh disk read + fresh detector run, not
    read back from the saved suspects file) -- reproduces at least every
    check_id captured in output/doc_vs_doc_miscompile_suspects_2026-07-29.json.
    A floor, not a ceiling, mirroring test_operator_consistency.py's SC-001
    convention."""
    mismatches = find_structural_kind_mismatches(corrected_checks, catalog)
    flagged_ids = {m["check_id"] for m in mismatches}

    missing = saved_suspect_ids - flagged_ids
    assert not missing, (
        f"{len(missing)} check_ids from the saved suspects file were NOT "
        f"reproduced by a fresh detector run: {sorted(missing)}"
    )
    assert len(mismatches) >= len(saved_suspect_ids)


def test_named_six_suspects_are_flagged(catalog, corrected_checks):
    """The 6 named check_ids from the task description are confirmed present
    in the detector's real output against the real ruleset."""
    named_six = {
        "cash-to-borrower-cd-vs-approval-consistent", "gla-sqft-consistency",
        "1008-appraiser-name-license-agree", "1008-loan-purpose-agree",
        "urla-marital-status-agree", "loan-purpose-1003-vs-1008-du-agree",
    }
    mismatches = find_structural_kind_mismatches(corrected_checks, catalog)
    flagged_ids = {m["check_id"] for m in mismatches}
    missing = named_six - flagged_ids
    assert not missing, f"named suspects not flagged: {sorted(missing)}"


def test_known_corrections_are_not_reflagged(catalog, corrected_checks):
    """The 2 checks known_compile_corrections.py already fixes must NOT
    appear in the detector's output when run against the corrected list
    (their kind is now agree_doc_categorical, outside the detector's scope)."""
    mismatches = find_structural_kind_mismatches(corrected_checks, catalog)
    flagged_ids = {m["check_id"] for m in mismatches}
    for known_id in KNOWN_CORRECTIONS:
        assert known_id not in flagged_ids, (
            f"{known_id} is already corrected by known_compile_corrections.py "
            "and must not be re-flagged as a structural mismatch"
        )


# --- false-positive test (measured, not assumed) -----------------------------

def test_false_positive_rate_against_legitimate_doc_vs_doc_checks(catalog, corrected_checks):
    """Measures (does not assume) the false-positive rate against checks
    that already legitimately use kind=agree_doc_categorical/agree_doc_numeric
    -- the detector's scope is agree_categorical/agree_numeric only (see
    kind_selection_audit.py), so by construction it should never touch these,
    but this test actually runs the detector and counts, following
    test_operator_consistency.py's SC-002 "measured, not assumed" pattern."""
    doc_vs_doc_checks = [
        c for c in corrected_checks
        if c.kind in ("agree_doc_categorical", "agree_doc_numeric")
    ]
    assert len(doc_vs_doc_checks) > 0, (
        "expected at least the known_compile_corrections.py-corrected checks "
        "to be present as agree_doc_categorical/agree_doc_numeric"
    )

    mismatches = find_structural_kind_mismatches(corrected_checks, catalog)
    flagged_ids = {m["check_id"] for m in mismatches}

    false_positives = [c.id for c in doc_vs_doc_checks if c.id in flagged_ids]
    fp_rate = len(false_positives) / len(doc_vs_doc_checks)
    print(f"\n[doc-vs-doc FP check] measured false-positive rate against "
          f"{len(doc_vs_doc_checks)} legitimate agree_doc_categorical/"
          f"agree_doc_numeric checks: {len(false_positives)} ({fp_rate:.2%})")
    for check_id in false_positives:
        print(f"  FALSE POSITIVE: {check_id}")

    assert fp_rate == 0.0, (
        f"false-positive rate {fp_rate:.2%} against legitimate doc-vs-doc "
        f"checks -- the detector must never flag these: {false_positives}"
    )


def test_no_mismatch_for_field_with_a_real_system_source(catalog):
    """A synthetic check whose field has expected_sources including "los"
    (a real system source exists) must not be flagged, even though its kind
    is agree_categorical -- this IS a legitimate doc-vs-system comparison."""
    # note_rate is a real catalog entry with a system source (los/mismo).
    entry = catalog.get("note_rate")
    assert entry is not None, "test setup requires note_rate to exist in the catalog"
    assert entry.expected_sources != ["doc"], (
        "test setup requires note_rate to have a real system source"
    )
    chk = Check(id="synthetic-legit-doc-vs-system", name="x", field_name="note_rate",
                kind="agree_categorical", severity="WARNING", phase="RECONCILE")
    mismatches = find_structural_kind_mismatches([chk], catalog)
    assert mismatches == []


def test_unresolved_field_name_is_not_flagged(catalog):
    """A check whose field_name doesn't resolve in the catalog at all is left
    to the separate referential-integrity gate -- not this detector's job."""
    chk = Check(id="synthetic-unresolved", name="x", field_name="totally_unknown_field_xyz",
                kind="agree_categorical", severity="WARNING", phase="RECONCILE")
    mismatches = find_structural_kind_mismatches([chk], catalog)
    assert mismatches == []


# --- assemble_ruleset() wiring: known corrections applied automatically -----

def test_assemble_ruleset_applies_known_corrections_automatically():
    """Proves apply_known_compile_corrections() now runs INSIDE
    assemble_ruleset() itself -- not just independently callable. A minimal
    draft whose check has id 'employment-dates-1003-vs-docs-agree' and kind
    wrongly set to 'agree_categorical' comes out of assemble_ruleset() with
    kind == 'agree_doc_categorical' and the known compare_field_name."""
    check = Check(
        id="employment-dates-1003-vs-docs-agree", name="Employment Dates 1003 vs. Docs",
        field_name="employment_start_date_1003", kind="agree_categorical",
        severity="CRITICAL", phase="QC",
    )
    draft = C.CompiledCheckDraft(
        row_id="row-known-correction", check=check,
        source_text="Employment dates on 1003 do not match supporting employment documentation",
        extracted_intent="Fails when 1003 employment dates disagree with supporting docs.",
    )
    rs = C.assemble_ruleset([draft], ruleset_id="batch-known-correction", version=1,
                            signed_by="test", signed_at="2026-07-29T00:00:00Z")

    assert len(rs.checks) == 1, "the known-corrected check must still be signed, not excluded"
    signed_check = rs.checks[0]
    assert signed_check.id == "employment-dates-1003-vs-docs-agree"
    assert signed_check.kind == "agree_doc_categorical", (
        f"expected kind to be auto-corrected to agree_doc_categorical, got {signed_check.kind!r}"
    )
    assert signed_check.compare_field_name == "employment_start_date_voe", (
        f"expected compare_field_name to be auto-corrected, got {signed_check.compare_field_name!r}"
    )


# --- assemble_ruleset() wiring: NEW structural mismatches are excluded -----

def test_assemble_ruleset_excludes_new_structural_mismatch():
    """A structural mismatch that is NOT in KNOWN_CORRECTIONS (a brand-new
    instance of this bug class) is excluded from the signed Ruleset by
    assemble_ruleset() -- never silently included with a guessed fix, per
    the constitution's zero-false-auto-clear gate."""
    catalog = load_catalog(_CATALOG_PATH)
    # Pick a real doc-only field from the catalog that ISN'T one of the two
    # known-correction field names, so this is genuinely a NEW mismatch.
    doc_only_field = next(
        e.field_name for e in catalog.entries
        if e.expected_sources == ["doc"]
        and e.field_name not in ("employment_start_date_1003", "title_vesting_1003")
    )
    good_check = Check(
        id="chk-good", name="Good check", field_name="note_rate",
        kind="predicate", severity="INFO", predicate="is_true",
    )
    bad_check = Check(
        id="chk-new-structural-mismatch", name="Bad check", field_name=doc_only_field,
        kind="agree_categorical", severity="WARNING", phase="RECONCILE",
    )
    drafts = [
        C.CompiledCheckDraft(row_id="row-good", check=good_check,
                              source_text="x", extracted_intent="x"),
        C.CompiledCheckDraft(row_id="row-bad", check=bad_check,
                              source_text="y", extracted_intent="y"),
    ]
    rs = C.assemble_ruleset(drafts, ruleset_id="batch-new-mismatch", version=1,
                            signed_by="test", signed_at="2026-07-29T00:00:00Z")

    signed_ids = {c.id for c in rs.checks}
    assert "chk-good" in signed_ids, "the unrelated, correctly-compiled check must still be signed"
    assert "chk-new-structural-mismatch" not in signed_ids, (
        "a NEW (unaudited) structural kind mismatch must be excluded from the signed Ruleset, "
        "not silently included with a guessed compare_field_name"
    )
    # Also excluded from provenance/intent_records -- fully out of the signed artifact.
    assert "chk-new-structural-mismatch" not in {p.check_id for p in rs.provenance}
    assert "chk-new-structural-mismatch" not in {r.check_id for r in rs.intent_records}


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
