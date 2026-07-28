"""
Synthetic-eval runner — the reportable artifact for the no-real-loans workaround.

Generates N labeled loans (ground truth by construction), runs the deterministic
engine, scores against the constructed labels, and emits a JSON artifact + a
console report with per-archetype coverage. This is the eval that lets us PRESS
ON before Kayla's real loans land — and the harness stays ready to re-run on real
loans the day they arrive (swap the loan source, keep the scorer).

Run:  python3 eval.py            # default 5000 loans
      python3 eval.py 20000 --runtag=nightly
Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict
from typing import Any, Dict, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import generator as G                                         # noqa: E402
from test_properties import score                             # noqa: E402


def coverage_by_archetype(loans: List[G.LabeledLoan]) -> Dict[str, int]:
    """How many loans exercised each mutation archetype (for the 'did we cover
    the real check set' question)."""
    cov: Counter = Counter()
    for _loan, _exp, prov in loans:
        for label in prov["mutations"]:
            arch = label.split(":", 1)[0]
            cov[arch] += 1
        if not prov["mutations"]:
            cov["CLEAN"] += 1
    return dict(cov.most_common())


def main() -> int:
    n = 5000
    runtag = "manual"
    for a in sys.argv[1:]:
        if a.startswith("--runtag="):
            runtag = a.split("=", 1)[1]
        elif a.isdigit():
            n = int(a)

    loans = G.generate(n)
    s = score(loans)
    cov = coverage_by_archetype(loans)
    kinds = Counter(prov["kind"] for _, _, prov in loans)

    print(f"\n=== SYNTHETIC EVAL — engine vs ground-truth-by-construction ===")
    print(f"  loans generated : {s['loans']}  (mix: {dict(kinds)})")
    print(f"  checks scored   : {s['checks_scored']}")
    print(f"  exact-match     : {s['exact_match']} ({s['exact_match_rate']})")
    fc = s["false_auto_clear_count"]
    print(f"  FALSE-AUTO-CLEARS: {fc}  {'✓ none (mandatory)' if fc == 0 else '✗ SAFETY FAILURE'}")
    print(f"\n  archetype coverage (loans exercising each):")
    for arch, cnt in cov.items():
        print(f"    {arch:<14} {cnt}")
    if s["mismatches"]:
        print(f"\n  label mismatches ({len(s['mismatches'])}):")
        for m in s["mismatches"][:10]:
            print(f"    - {m}")

    passed = fc == 0 and not s["mismatches"]
    print(f"\n  === SYNTHETIC EVAL {'PASSED ✓' if passed else 'FAILED ✗'} ===\n")

    artifact = {
        "eval": "synthetic ground-truth-by-construction",
        "runtag": runtag,
        "n_loans": s["loans"],
        "mix": dict(kinds),
        "checks_scored": s["checks_scored"],
        "exact_match": s["exact_match"],
        "exact_match_rate": s["exact_match_rate"],
        "false_auto_clear_count": fc,
        "false_auto_clears": s["false_auto_clears"],
        "archetype_coverage": cov,
        "mismatches": s["mismatches"][:50],
        "passed": passed,
        "what_this_proves": (
            "Given the data, the deterministic engine computes the correct "
            "verdict per the signed rule spec, at scale, with zero false-auto-"
            "clears — across defect archetypes derived from the real AMQ "
            "workbooks. Labels are exact because we INJECTED each defect."
        ),
        "honest_residual": (
            "Synthetic defect DISTRIBUTION != real-world distribution; we only "
            "catch failure modes we inject. Mitigations: (1) archetypes are "
            "derived from the real 800+ check workbook (taxonomy.py), so "
            "coverage tracks the actual rule set; (2) the mutation->expected "
            "mapping is SME-signable (a rules review, not a loan hunt); "
            "(3) extraction/OCR realism is NOT modeled here — that is the one "
            "piece that still wants real files, tracked as a separate gap."
        ),
    }
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"synth_eval_{runtag}.json")
    with open(out_path, "w") as fh:
        json.dump(artifact, fh, indent=2, sort_keys=False)
    print(f"  artifact -> {out_path}\n")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
