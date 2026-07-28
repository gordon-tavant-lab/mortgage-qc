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

Run:  python3 -m pytest test_properties.py -q
  or: python3 test_properties.py          # plain-run scorer summary
Python 3.9 compatible.
"""
from __future__ import annotations

import os
import sys
from decimal import Decimal
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qc_engine import run as engine_run                       # noqa: E402
from qc_engine import money as M                              # noqa: E402
from qc_engine.reconcile import normalize                     # noqa: E402
from fixtures.ruleset_demo import demo_ruleset                # noqa: E402

import generator as G                                         # noqa: E402

RULESET = demo_ruleset()


def _verdicts(loan) -> Dict[str, str]:
    res = engine_run(loan, RULESET)
    return {r.check_id: r.status for r in res.results}


# --------------------------------------------------------------------------- #
# 1. Constructed-label scoring
# --------------------------------------------------------------------------- #
def score(loans: List[G.LabeledLoan]) -> Dict[str, object]:
    total = match = 0
    false_clears: List[str] = []
    mismatches: List[str] = []
    for loan, expected, prov in loans:
        got = _verdicts(loan)
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
    s = score(G.generate(400))
    assert s["false_auto_clear_count"] == 0, \
        f"CATASTROPHIC: false-auto-clears {s['false_auto_clears'][:5]}"
    assert s["exact_match_rate"] == 1.0, \
        f"label mismatches: {s['mismatches'][:5]}"


def test_zero_false_clear_is_mandatory():
    """Even at high volume, never clear an injected FAIL defect."""
    s = score(G.generate(2000, start_seed=50000))
    assert s["false_auto_clear_count"] == 0, s["false_auto_clears"][:10]


# --------------------------------------------------------------------------- #
# 2. Metamorphic / property invariants (label-free)
# --------------------------------------------------------------------------- #
def test_ltv_monotonicity():
    """Raising loan_amount only moves LTV verdict PASS->FAIL, never reverse."""
    base = G.build_clean(seed=7)
    value = Decimal(base.facts["property_value"])
    prev_failed = False
    for pct in ["50", "80", "90", "94.999", "95.000", "95.001", "98", "110"]:
        base.facts["loan_amount"] = str((value * Decimal(pct) / Decimal("100")))
        v = _verdicts(base)["chk-ltv-max"]
        failed = (v == "FAIL")
        if prev_failed:
            assert failed, f"LTV verdict flipped FAIL->PASS at {pct}% (non-monotonic)"
        prev_failed = prev_failed or failed


def test_reconcile_pass_iff_normalized_equal():
    """A categorical reconcile is PASS iff normalized(doc)==normalized(system)."""
    loan = G.build_clean(seed=11)
    # equal case
    assert _verdicts(loan)["chk-property-address"] == "PASS"
    # diverged case
    sv = loan.fields["property_address"]
    sv.los = str(sv.doc) + " DIFFERENT 99"
    sv.mismo = sv.los
    eq = normalize("address", sv.doc) == normalize("address", sv.los)
    verdict = _verdicts(loan)["chk-property-address"]
    assert (verdict == "PASS") == eq, \
        f"reconcile verdict {verdict} disagrees with normalized-equality {eq}"


def test_engine_ltv_matches_independent_decimal():
    """The engine must not mark its own homework: recompute LTV a second,
    independent way and require equality on many loans."""
    for seed in range(2000, 2100):
        loan = G.build_clean(seed)
        la = Decimal(loan.facts["loan_amount"])
        pv = Decimal(loan.facts["property_value"])
        independent = (la / pv * Decimal("100")).quantize(Decimal("0.001"))
        engine_val = M.ltv_percent(loan.facts["loan_amount"],
                                   loan.facts["property_value"])
        assert engine_val == independent, \
            f"{loan.loan_id}: engine LTV {engine_val} != independent {independent}"


def test_confidence_gate_withholds_autoclear():
    """A PASS relying on a sub-floor extraction is withheld to NEEDS_REVIEW."""
    loan, expected, _ = G.make_single(seed=321, archetype="CONFIDENCE")
    got = _verdicts(loan)
    assert got["chk-note-rate"] == "NEEDS_REVIEW", got["chk-note-rate"]


def test_generator_is_deterministic():
    """Same (n, seed) -> identical loans + identical labels."""
    a = G.generate(50, start_seed=999)
    b = G.generate(50, start_seed=999)
    assert [l.loan_id for l, _, _ in a] == [l.loan_id for l, _, _ in b]
    assert [e for _, e, _ in a] == [e for _, e, _ in b]


def main() -> int:
    print("\n=== CONSTRUCTED-LABEL SCORE (engine vs by-construction truth) ===")
    s = score(G.generate(2000))
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
