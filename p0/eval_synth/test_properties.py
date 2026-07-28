"""
Property + metamorphic tests — correctness WITHOUT human labels.

Two kinds of assurance, neither of which needs real loans:

1. CONSTRUCTED-LABEL scoring (the headline): run the engine over generated
   loans whose verdicts we know by construction, and assert the engine matches.
   The catastrophic metric is FALSE-AUTO-CLEAR (engine says cleared where a
   defect was injected) — zero is mandatory.

2. METAMORPHIC / property invariants (no labels at all): truths that must hold
   for ANY loan, used to catch engine bugs the constructed labels might miss:
     - Monotonicity: raising loan_amount can only move the LTV verdict
       PASS -> FAIL, never the reverse.
     - Reconcile soundness: a categorical reconcile is PASS iff the normalized
       doc == normalized system.
     - Self-consistency: the engine's LTV equals an independent Decimal
       recomputation (the engine isn't trusted to mark its own homework — we
       recompute the ratio a second way and compare).
     - Confidence gate: a PASS built on a sub-floor extraction is withheld to
       NEEDS_REVIEW.

005 FR-008/US4 generalization: every invariant below now takes an explicit
`ruleset: Ruleset` parameter instead of reading a module-level hardcoded
`RULESET = demo_ruleset()` constant — so the same invariant suite runs
against ANY candidate ruleset the promotion gate (`promotion_gate.py`) is
asked to evaluate, not just the one demo ruleset. Each invariant picks its
OWN representative check out of the ruleset it's given (e.g. the first
`ratio_threshold`/`ltv` check for monotonicity) rather than assuming a fixed
check id — and reports `{"applicable": False, ...}` rather than silently
passing or erroring when the ruleset under test has no check of the relevant
kind at all (US4 Acceptance Scenario 2). Existing callers — the pytest
`test_*` functions below, and `eval.py` — now pass `demo_ruleset()`
explicitly, preserving today's behavior unchanged (`score()` still defaults
to `demo_ruleset()` when no ruleset is given, for the other, not-yet-built
012-spec test files that already call `score(loans)` with one argument).

Run:  python3 -m pytest test_properties.py -q
  or: python3 test_properties.py          # plain-run scorer summary
Python 3.9 compatible.
"""
from __future__ import annotations

import os
import sys
from decimal import Decimal
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qc_engine import run as engine_run                       # noqa: E402
from qc_engine import money as M                              # noqa: E402
from qc_engine.model import SourceValue                       # noqa: E402
from qc_engine.reconcile import normalize                     # noqa: E402
from qc_engine.ruleset import Ruleset                          # noqa: E402
from fixtures.ruleset_demo import demo_ruleset                # noqa: E402

import generator as G                                         # noqa: E402


def _verdicts(loan, ruleset: Ruleset) -> Dict[str, str]:
    res = engine_run(loan, ruleset)
    return {r.check_id: r.status for r in res.results}


# --------------------------------------------------------------------------- #
# 1. Constructed-label scoring
# --------------------------------------------------------------------------- #
def score(loans: List[G.LabeledLoan], ruleset: Optional[Ruleset] = None) -> Dict[str, object]:
    """Score `loans` against `ruleset` (defaults to `demo_ruleset()` when
    omitted, so pre-existing callers that pass only `loans` -- e.g. other,
    not-yet-built specs' test files -- keep working unchanged; 005 FR-008
    generalizes this to accept any candidate ruleset explicitly)."""
    if ruleset is None:
        ruleset = demo_ruleset()
    total = match = 0
    false_clears: List[str] = []
    mismatches: List[str] = []
    for loan, expected, prov in loans:
        got = _verdicts(loan, ruleset)
        for cid, exp in expected.items():
            if cid not in got:          # check not applicable to this loan
                continue
            total += 1
            if got[cid] == exp:
                match += 1
            else:
                mismatches.append(
                    f"{loan.loan_id}/{cid}: expected {exp}, got {got[cid]} "
                    f"[{'; '.join(prov['mutations']) or 'clean'}]")
            # false-auto-clear: a real injected defect (FAIL truth) that the
            # engine PASSed.
            if exp == "FAIL" and got[cid] == "PASS":
                false_clears.append(f"{loan.loan_id}/{cid}")
    return {
        "loans": len(loans),
        "checks_scored": total,
        "exact_match": match,
        "exact_match_rate": round(match / total, 4) if total else 1.0,
        "false_auto_clears": false_clears,
        "false_auto_clear_count": len(false_clears),
        "mismatches": mismatches,
    }


def test_constructed_labels_exact_match():
    """Engine verdicts match the by-construction ground truth on a large set."""
    s = score(G.generate(400), demo_ruleset())
    assert s["false_auto_clear_count"] == 0, \
        f"CATASTROPHIC: false-auto-clears {s['false_auto_clears'][:5]}"
    assert s["exact_match_rate"] == 1.0, \
        f"label mismatches: {s['mismatches'][:5]}"


def test_zero_false_clear_is_mandatory():
    """Even at high volume, never clear an injected FAIL defect."""
    s = score(G.generate(2000, start_seed=50000), demo_ruleset())
    assert s["false_auto_clear_count"] == 0, s["false_auto_clears"][:10]


# --------------------------------------------------------------------------- #
# 2. Metamorphic / property invariants (label-free) -- generalized (FR-008)
# --------------------------------------------------------------------------- #
def ltv_monotonicity_invariant(ruleset: Ruleset) -> Dict[str, Any]:
    """Raising loan_amount only moves the ruleset's OWN ltv ratio_threshold
    check's verdict PASS->FAIL, never the reverse. Not applicable if
    `ruleset` has no ratio_threshold/ltv check at all (US4 Acceptance
    Scenario 2)."""
    ltv_checks = [c for c in ruleset.checks
                 if c.kind == "ratio_threshold" and c.ratio == "ltv"]
    if not ltv_checks:
        return {"applicable": False, "passed": None,
                "detail": "no ratio_threshold/ltv check present in this ruleset"}
    chk = ltv_checks[0]
    base = G.build_clean(seed=7)
    value = Decimal(base.facts["property_value"])
    prev_failed = False
    for pct in ["50", "80", "90", "94.999", "95.000", "95.001", "98", "110"]:
        base.facts["loan_amount"] = str((value * Decimal(pct) / Decimal("100")))
        v = _verdicts(base, ruleset).get(chk.id)
        failed = (v == "FAIL")
        if prev_failed and not failed:
            return {"applicable": True, "passed": False,
                    "detail": f"LTV verdict flipped FAIL->PASS at {pct}% "
                              f"(check {chk.id}, non-monotonic)"}
        prev_failed = prev_failed or failed
    return {"applicable": True, "passed": True, "detail": None}


def reconcile_soundness_invariant(ruleset: Ruleset) -> Dict[str, Any]:
    """A categorical reconcile is PASS iff normalized(doc)==normalized(system)
    -- tested against the ruleset's own first agree_categorical check. Not
    applicable if `ruleset` has no agree_categorical check at all."""
    agree_checks = [c for c in ruleset.checks if c.kind == "agree_categorical"]
    if not agree_checks:
        return {"applicable": False, "passed": None,
                "detail": "no agree_categorical check present in this ruleset"}
    chk = agree_checks[0]
    loan = G.build_clean(seed=11)
    sv = loan.fields.get(chk.field_name)
    if sv is None:
        sv = SourceValue(doc="RECONCILE_BASE", los="RECONCILE_BASE", doc_confidence=0.99)
        loan.fields[chk.field_name] = sv
    else:
        sv.los = sv.doc  # start from a genuinely equal case
    eq_verdict = _verdicts(loan, ruleset).get(chk.id)
    if eq_verdict != "PASS":
        return {"applicable": True, "passed": False,
                "detail": f"equal-values case resolved {eq_verdict}, expected PASS"}
    sv.los = str(sv.doc) + " DIFFERENT 99"
    eq = normalize(chk.normalizer, sv.doc) == normalize(chk.normalizer, sv.los)
    verdict = _verdicts(loan, ruleset).get(chk.id)
    passed = (verdict == "PASS") == eq
    return {"applicable": True, "passed": passed,
            "detail": None if passed else
            f"verdict {verdict} disagrees with normalized-equality {eq}"}


def engine_ltv_self_consistency_invariant(ruleset: Ruleset) -> Dict[str, Any]:
    """The engine must not mark its own homework: recompute LTV a second,
    independent way and require equality on many loans. Gated on the ruleset
    actually containing an ltv check (otherwise this invariant is testing
    engine math the ruleset under evaluation never exercises)."""
    ltv_checks = [c for c in ruleset.checks
                 if c.kind == "ratio_threshold" and c.ratio == "ltv"]
    if not ltv_checks:
        return {"applicable": False, "passed": None,
                "detail": "no ratio_threshold/ltv check present in this ruleset"}
    for seed in range(2000, 2100):
        loan = G.build_clean(seed)
        la = Decimal(loan.facts["loan_amount"])
        pv = Decimal(loan.facts["property_value"])
        independent = (la / pv * Decimal("100")).quantize(Decimal("0.001"))
        engine_val = M.ltv_percent(loan.facts["loan_amount"], loan.facts["property_value"])
        if engine_val != independent:
            return {"applicable": True, "passed": False,
                    "detail": f"{loan.loan_id}: engine LTV {engine_val} != "
                              f"independent {independent}"}
    return {"applicable": True, "passed": True, "detail": None}


def confidence_gate_invariant(ruleset: Ruleset) -> Dict[str, Any]:
    """A PASS relying on a sub-floor extraction is withheld to NEEDS_REVIEW
    -- tested against the ruleset's own first agree_categorical/agree_numeric
    check with a field_name set (the confidence gate in engine.py is
    kind-agnostic, applied uniformly post-dispatch to any PASS). Not
    applicable if `ruleset` has no such check."""
    candidates = [c for c in ruleset.checks
                 if c.kind in ("agree_categorical", "agree_numeric") and c.field_name]
    if not candidates:
        return {"applicable": False, "passed": None,
                "detail": "no agree_categorical/agree_numeric check present in this ruleset"}
    chk = candidates[0]
    loan = G.build_clean(seed=321)
    sv = loan.fields.get(chk.field_name)
    if sv is None:
        return {"applicable": False, "passed": None,
                "detail": f"clean fixture has no value for {chk.field_name}"}
    sv.doc_confidence = 0.55   # below the 0.80 floor
    verdict = _verdicts(loan, ruleset).get(chk.id)
    passed = verdict == "NEEDS_REVIEW"
    return {"applicable": True, "passed": passed,
            "detail": None if passed else f"expected NEEDS_REVIEW, got {verdict}"}


INVARIANTS = {
    "ltv_monotonicity": ltv_monotonicity_invariant,
    "reconcile_soundness": reconcile_soundness_invariant,
    "engine_ltv_self_consistency": engine_ltv_self_consistency_invariant,
    "confidence_gate": confidence_gate_invariant,
}


def run_invariants(ruleset: Ruleset) -> Dict[str, Dict[str, Any]]:
    """Run every registered invariant against `ruleset`, keyed by name --
    the generalized suite `promotion_gate.py` wires in (FR-008)."""
    return {name: fn(ruleset) for name, fn in INVARIANTS.items()}


# --- pytest test_* functions -- explicit demo_ruleset() callers, preserving
# today's exact proven behavior (T036/T039: zero regression) -------------- #
def test_ltv_monotonicity():
    result = ltv_monotonicity_invariant(demo_ruleset())
    assert result["applicable"] is True
    assert result["passed"] is True, result.get("detail")


def test_reconcile_pass_iff_normalized_equal():
    result = reconcile_soundness_invariant(demo_ruleset())
    assert result["applicable"] is True
    assert result["passed"] is True, result.get("detail")


def test_engine_ltv_matches_independent_decimal():
    result = engine_ltv_self_consistency_invariant(demo_ruleset())
    assert result["applicable"] is True
    assert result["passed"] is True, result.get("detail")


def test_confidence_gate_withholds_autoclear():
    result = confidence_gate_invariant(demo_ruleset())
    assert result["applicable"] is True
    assert result["passed"] is True, result.get("detail")


def test_generator_is_deterministic():
    """Same (n, seed) -> identical loans + identical labels."""
    a = G.generate(50, start_seed=999)
    b = G.generate(50, start_seed=999)
    assert [l.loan_id for l, _, _ in a] == [l.loan_id for l, _, _ in b]
    assert [e for _, e, _ in a] == [e for _, e, _ in b]


def main() -> int:
    print("\n=== CONSTRUCTED-LABEL SCORE (engine vs by-construction truth) ===")
    s = score(G.generate(2000), demo_ruleset())
    print(f"  loans={s['loans']}  checks={s['checks_scored']}  "
          f"exact-match={s['exact_match']} ({s['exact_match_rate']})")
    print(f"  FALSE-AUTO-CLEARS: {s['false_auto_clear_count']} "
          f"{'✓ none' if s['false_auto_clear_count']==0 else '✗ ' + str(s['false_auto_clears'][:5])}")
    if s["mismatches"]:
        print(f"  mismatches ({len(s['mismatches'])}):")
        for m in s["mismatches"][:8]:
            print(f"    - {m}")
    else:
        print("  all constructed labels matched ✓")
    return 0 if s["false_auto_clear_count"] == 0 and not s["mismatches"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
