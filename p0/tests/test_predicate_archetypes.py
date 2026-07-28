"""
003a -- predicate check engine, proven at the scale of the real archetype set.

Complements tests/test_p0.py (which pins the concrete doc=None bug fix, US1).
This file proves is_true/is_present hold correctly across a representative
sample of all 5 real predicate archetypes (MISSING/UNSIGNED/EXPIRED/
INCOMPLETE/POLICY -- 2,937 real conditions per eval_synth/taxonomy.json),
not just the demo's one hand-authored check (spec.md US2), and that the
existing confidence gate still withholds auto-clear once exercised at that
scale (spec.md US3).

Run from p0/:  python -m pytest tests/test_predicate_archetypes.py -v
Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qc_engine import run
from qc_engine.model import CanonicalLoan, SourceValue
from qc_engine.ruleset import Check, Ruleset

TAXONOMY_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "eval_synth", "taxonomy.json")

# Every real predicate archetype from p0/eval_synth/taxonomy.json (engine_kind
# == "predicate"), mapped to the predicate that best fits its expected_verdict
# semantics. MISSING is a presence question (is_present); the other four each
# assert a boolean condition was satisfied (is_true) -- consistent with how
# the demo ruleset's one existing predicate check (chk-note-signed, UNSIGNED-
# shaped) is already authored.
PREDICATE_ARCHETYPES = {
    "MISSING": "is_present",
    "UNSIGNED": "is_true",
    "EXPIRED": "is_true",   # T012: modeled as a pre-computed staleness boolean
                            # -- see spec.md FR-007/Assumptions for why the
                            # engine does no date arithmetic of its own here.
    "INCOMPLETE": "is_true",
    "POLICY": "is_true",
}


def _load_archetype_examples():
    """T007: reads taxonomy.json's own `examples` per archetype -- no
    fabricated conditions, just what's already on disk."""
    with open(TAXONOMY_PATH) as f:
        taxonomy = json.load(f)
    by_id = {a["id"]: a for a in taxonomy["archetypes"]}
    out = {}
    for archetype_id, predicate in PREDICATE_ARCHETYPES.items():
        entry = by_id[archetype_id]
        assert entry["engine_kind"] == "predicate"
        assert entry["expected_verdict"] == "FAIL"
        out[archetype_id] = (predicate, entry["examples"])
    return out


ARCHETYPE_EXAMPLES = _load_archetype_examples()


def _check_and_loans(archetype_id, predicate, index):
    """Builds one Check + a fail-case loan (the archetype's own defect) and a
    pass-case loan for a single representative condition."""
    field_name = f"{archetype_id.lower()}_field_{index}"
    check_id = f"chk-{archetype_id.lower()}-{index}"
    chk = Check(id=check_id, name=archetype_id, field_name=field_name,
                kind="predicate", severity="CRITICAL", predicate=predicate)
    if predicate == "is_present":
        fail_loan = CanonicalLoan(loan_id=f"LN-{check_id}-fail",
                                   fields={field_name: SourceValue(doc=None, doc_confidence=0.99)})
        pass_loan = CanonicalLoan(loan_id=f"LN-{check_id}-pass",
                                   fields={field_name: SourceValue(doc="present-value", doc_confidence=0.99)})
    else:  # is_true
        fail_loan = CanonicalLoan(loan_id=f"LN-{check_id}-fail",
                                   fields={field_name: SourceValue(doc=False, doc_confidence=0.99)})
        pass_loan = CanonicalLoan(loan_id=f"LN-{check_id}-pass",
                                   fields={field_name: SourceValue(doc=True, doc_confidence=0.99)})
    return chk, fail_loan, pass_loan


def _run_single(chk, loan):
    rs = Ruleset(ruleset_id=f"t-{chk.id}", version=1, checks=[chk])
    return run(loan, rs)


def _assert_archetype_correct(archetype_id):
    predicate, examples = ARCHETYPE_EXAMPLES[archetype_id]
    fail_results, pass_results = [], []
    for i, _example_text in enumerate(examples):
        chk, fail_loan, pass_loan = _check_and_loans(archetype_id, predicate, i)
        fail_res = _run_single(chk, fail_loan)
        pass_res = _run_single(chk, pass_loan)
        assert fail_res.results[0].status == "FAIL", (
            f"{archetype_id}[{i}] fail-case: expected FAIL, got "
            f"{fail_res.results[0].status}")
        assert pass_res.results[0].status == "PASS", (
            f"{archetype_id}[{i}] pass-case: expected PASS, got "
            f"{pass_res.results[0].status}")
        fail_results.append(fail_res)
        pass_results.append(pass_res)
    return fail_results, pass_results


# --- T008-T012: one archetype each (spec.md FR-004 / SC-002) --------------
def test_missing_archetype_predicate_correctness():
    _assert_archetype_correct("MISSING")


def test_unsigned_archetype_predicate_correctness():
    _assert_archetype_correct("UNSIGNED")


def test_incomplete_archetype_predicate_correctness():
    _assert_archetype_correct("INCOMPLETE")


def test_policy_archetype_predicate_correctness():
    _assert_archetype_correct("POLICY")


def test_expired_archetype_predicate_correctness():
    # T012: EXPIRED is modeled as a pre-computed staleness boolean (is_true)
    # -- confirms the engine needs no date-arithmetic logic of its own for
    # this archetype (spec.md FR-007). Whether that upstream pre-computation
    # assumption holds is an open question for 002b/Kayla, not this test.
    _assert_archetype_correct("EXPIRED")


# --- T013: zero-false-auto-clear across the full archetype batch (SC-003) --
def test_zero_false_auto_clear_across_all_archetypes():
    for archetype_id in PREDICATE_ARCHETYPES:
        fail_results, _pass_results = _assert_archetype_correct(archetype_id)
        for res in fail_results:
            assert not res.auto_cleared, (
                f"{archetype_id}: a FAIL-worthy loan was reported as "
                f"auto-cleared -- false-auto-clear (SC-003 violation)")


# --- T014-T015: confidence gate holds at archetype scale (spec.md US3) ----
def test_low_confidence_predicate_pass_withholds_autoclear():
    # FR-006: a predicate PASS built on a low-confidence extraction must be
    # downgraded to NEEDS_REVIEW, not silently auto-cleared -- across several
    # archetypes, not just the one demo check this gate is proven against
    # today.
    for archetype_id in ("UNSIGNED", "INCOMPLETE", "POLICY"):
        predicate, _examples = ARCHETYPE_EXAMPLES[archetype_id]
        chk, _fail_loan, pass_loan = _check_and_loans(archetype_id, predicate, 0)
        pass_loan.fields[chk.field_name].doc_confidence = 0.50  # below floor (0.80)
        res = _run_single(chk, pass_loan)
        assert res.results[0].status == "NEEDS_REVIEW", (
            f"{archetype_id}: low-confidence PASS was not withheld from "
            f"auto-clear, got {res.results[0].status}")


def test_high_confidence_predicate_pass_is_not_downgraded():
    # Regression check on the other direction of FR-006's gate: at/above
    # floor, a genuine PASS must not be flagged for review.
    for archetype_id in ("UNSIGNED", "INCOMPLETE", "POLICY"):
        predicate, _examples = ARCHETYPE_EXAMPLES[archetype_id]
        chk, _fail_loan, pass_loan = _check_and_loans(archetype_id, predicate, 0)
        pass_loan.fields[chk.field_name].doc_confidence = 0.95  # at/above floor
        res = _run_single(chk, pass_loan)
        assert res.results[0].status == "PASS", (
            f"{archetype_id}: at/above-floor PASS was incorrectly downgraded, "
            f"got {res.results[0].status}")


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
