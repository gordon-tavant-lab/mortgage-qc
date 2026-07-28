"""
The 90-second money moment — the demo that wins the room.

A loan whose LTV sits EXACTLY on the 95.000% tolerance boundary. We show:
  (1) the Decimal computation with the explicit, auditable rounding policy,
  (2) the same verdict produced N times, byte-identical,
  (3) the contrast: naive IEEE-754 float math drifts at the boundary and can
      flip the pass/fail — which is exactly the buyback risk the regulator
      audits, and exactly what an LLM-at-runtime POC cannot rule out.

Run:  python prove.py
Python 3.9 compatible.
"""
from __future__ import annotations

from decimal import Decimal

from qc_engine import money as M
from qc_engine import run
from fixtures.ruleset_demo import demo_ruleset
from fixtures.golden import golden_loans


def naive_float_ltv(loan_amount: str, value: str) -> float:
    """How a careless implementation would do it — for contrast only."""
    return float(loan_amount) / float(value) * 100.0


def main() -> None:
    # A boundary case engineered so float vs Decimal can disagree at the line.
    cases = [
        ("332500.00", "350000.00", "95.000"),   # exactly 95.000 -> PASS
        ("332502.00", "350000.00", "95.000"),   # crosses at 3dp -> must FAIL
        ("100000.00", "105263.16", "95.000"),   # float-fragile ratio
    ]
    threshold = Decimal("95.000")
    print("\n=== LTV BOUNDARY — DETERMINISTIC DECIMAL vs NAIVE FLOAT ===")
    print(f"  rounding policy: ROUND_HALF_EVEN, scale=0.001, threshold <= {threshold}%\n")
    print(f"  {'loan':>12} {'value':>12} {'Decimal LTV':>12} {'verdict':>8} "
          f"{'float LTV':>20} {'float verdict':>14}")
    for la, pv, _thr in cases:
        d_ltv = M.ltv_percent(la, pv)
        d_pass = d_ltv <= threshold
        f_ltv = naive_float_ltv(la, pv)
        f_pass = f_ltv <= 95.000
        flag = "  <-- FLIP!" if d_pass != f_pass else ""
        print(f"  {la:>12} {pv:>12} {M.decimal_str(d_ltv):>12} "
              f"{'PASS' if d_pass else 'FAIL':>8} {repr(f_ltv):>20} "
              f"{'PASS' if f_pass else 'FAIL':>14}{flag}")

    # Bit-exact repetition on the boundary loan via the real engine.
    print("\n=== SAME LOAN, 1000 RUNS, BYTE-IDENTICAL ===")
    rs = demo_ruleset()
    boundary = [l for l, _ in golden_loans() if l.loan_id == "LN-BOUNDARY"][0]
    digests = set()
    for _ in range(1000):
        res = run(boundary, rs)
        ltv = [r for r in res.results if r.check_id == "chk-ltv-max"][0]
        digests.add((ltv.compared_value, ltv.status, ltv.rounding))
    (cv, status, rounding), = digests  # exactly one unique tuple or this unpacks-fails
    print(f"  unique (ltv, verdict, rounding) tuples across 1000 runs: {len(digests)}")
    print(f"  LTV={cv}%  verdict={status}  rounding={rounding}")
    print(f"  -> {'DETERMINISTIC ✓' if len(digests) == 1 else 'NON-DETERMINISTIC ✗'}")
    print("\n  The regulator's question — 'show me how you got that number' —")
    print("  is answered by the Decimal value + the named rounding policy.")
    print("  An LLM at runtime cannot promise this number twice.\n")


if __name__ == "__main__":
    main()
