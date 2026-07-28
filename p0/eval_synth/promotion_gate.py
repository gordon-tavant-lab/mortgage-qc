"""
promotion_gate.py -- the single CI-runnable promotion-gate entry point for a
candidate compiled `Ruleset` (spec.md FR-006/007/008/009, SC-003/004/005;
005 User Story 2, orchestrating User Stories 1/3/4).

WHAT THIS PROVES: today, `eval.py` computes `false_auto_clear_count` and
prints "SAFETY FAILURE," but nothing in this repository consumes its exit
code as an actual gate -- a candidate ruleset with a genuine false-auto-clear
defect can be promoted with no mechanism stopping it (spec.md's core gap).
This module makes that block real: it orchestrates three separately-
reportable test tiers plus the label-free metamorphic invariants, and
returns a single `PromotionGateResult` whose `promotion_decision`
("PROMOTE" | "BLOCK") and `exit_code` (0 | non-zero) are the enforceable
contract every later caller (a CI runner, a Makefile target, a pre-commit
hook -- none of which exist in this repo yet, spec.md Assumptions) is meant
to act on.

THE THREE TIERS (spec.md FR-005), each answering a different question:
  - GOLDEN   (`golden_set.py`)      -- did a known-correct case regress?
  - COVERAGE (`coverage_set.py`)    -- does every compiled check have a
                                        proven pass/fail scenario at all?
  - VOLUME   (`generator.py` + this module's own scoring loop, mirroring
              `eval.py`)            -- at realistic population scale, what
                                        fraction auto-clears, and does
                                        zero-false-auto-clear still hold?
Plus the GENERALIZED label-free metamorphic invariants
(`test_properties.run_invariants`, FR-008) -- monotonicity, reconcile
soundness, engine self-consistency, confidence gate -- run against the
CANDIDATE ruleset actually under test, each reporting `{"applicable": bool,
"passed": bool}` (never silently passed/errored when the relevant check kind
is absent from the candidate).

THE HARD BLOCK (FR-006): a false-auto-clear collected from ANY of the three
tiers -- not just VOLUME -- sets `promotion_decision = "BLOCK"` and a
non-zero `exit_code`; each offending case is named (check id, loan id,
expected-vs-actual verdict), never aggregated away into a bare count.

CLI USAGE:
    python3 promotion_gate.py                     # gate demo_ruleset(), N=5000
    python3 promotion_gate.py 20000                # gate demo_ruleset(), N=20000
Exit code: 0 = PROMOTE, non-zero (1) = BLOCK -- mirrors `eval.py`'s existing
exit-code convention (`eval.py:107`, `return 0 if passed else 1`). Writes a
JSON artifact to `p0/eval_synth/artifacts/promotion_gate_result.json`,
extending `eval.py`'s artifact shape with `golden`/`coverage`/`volume`/
`invariants` sections and a top-level `promotion_decision` field.

PROGRAMMATIC USAGE (the contract every test in `p0/tests/test_promotion_gate.py`
exercises directly):
    result = run_promotion_gate(candidate=some_ruleset)
    result = run_promotion_gate(candidate=some_ruleset, baseline=prior_ruleset)
    result = run_promotion_gate(candidate=some_ruleset,
                                volume_loans=[(loan, expected_verdicts, provenance), ...])
`volume_loans`, when given, REPLACES the default `generator.generate(volume_n)`
population -- the injection point used to construct exact, deterministic
false-auto-clear/PROMOTE test cases without depending on the generator's own
random mix. Every `(loan, expected_verdicts, provenance)` triple scores
identically regardless of what `provenance` contains (FR-010/US5) -- this
module never branches on it.

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qc_engine.model import CanonicalLoan  # noqa: E402
from qc_engine.ruleset import Ruleset  # noqa: E402
from qc_engine.engine import run as engine_run  # noqa: E402

import generator as G  # noqa: E402
import scenario_construction as SC  # noqa: E402
import coverage_set as CS  # noqa: E402
import golden_set as GS  # noqa: E402
from test_properties import run_invariants  # noqa: E402
from fixtures.ruleset_demo import demo_ruleset  # noqa: E402

LabeledLoan = Tuple[CanonicalLoan, Dict[str, str], Dict[str, Any]]


@dataclass
class PromotionGateResult:
    promotion_decision: str        # "PROMOTE" | "BLOCK"
    exit_code: int                 # 0 == promote, non-zero == block
    false_auto_clears: List[Dict[str, Any]] = field(default_factory=list)
    golden: Dict[str, Any] = field(default_factory=dict)
    coverage: Dict[str, Any] = field(default_factory=dict)
    volume: Dict[str, Any] = field(default_factory=dict)
    invariants: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "promotion_decision": self.promotion_decision,
            "exit_code": self.exit_code,
            "false_auto_clears": self.false_auto_clears,
            "golden": self.golden,
            "coverage": self.coverage,
            "volume": self.volume,
            "invariants": self.invariants,
        }


# --------------------------------------------------------------------------- #
# VOLUME tier -- reuses generator.py's population (or an injected
# `volume_loans` list, the deterministic-test injection point), scored
# against the CANDIDATE ruleset. Reports auto_clear_rate alongside the
# existing false_auto_clear_count metric (SC-005).
# --------------------------------------------------------------------------- #
def _run_volume_tier(candidate: Ruleset,
                     loans: List[LabeledLoan]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    false_clears: List[Dict[str, Any]] = []
    scored = 0
    match = 0
    auto_clear_count = 0
    for loan, expected, _prov in loans:
        res = engine_run(loan, candidate)
        got = {r.check_id: r.status for r in res.results}
        if res.auto_cleared:
            auto_clear_count += 1
        for check_id, exp_status in expected.items():
            if check_id not in got:
                continue
            scored += 1
            actual = got[check_id]
            if actual == exp_status:
                match += 1
            if exp_status == "FAIL" and actual == "PASS":
                false_clears.append({"check_id": check_id, "loan_id": loan.loan_id,
                                      "expected": exp_status, "actual": actual})
    n = len(loans)
    volume = {
        "n_loans": n,
        "checks_scored": scored,
        "exact_match": match,
        "exact_match_rate": round(match / scored, 4) if scored else 1.0,
        "false_auto_clear_count": len(false_clears),
        "auto_clear_rate": round(auto_clear_count / n, 4) if n else 0.0,
    }
    return volume, false_clears


# --------------------------------------------------------------------------- #
# COVERAGE-sourced false-auto-clears: for every check with a successfully
# constructed scenario whose fail-case should itself resolve FAIL (a QC-phase
# defect, not an informational FLAG), confirm running that fail-case loan
# through the candidate ruleset does not silently auto-clear to PASS. This
# catches a defect COVERAGE alone can name even with no volume_loans/baseline
# given at all (spec.md FR-006: "in ANY of the three tiers").
# --------------------------------------------------------------------------- #
def _coverage_false_auto_clears(candidate: Ruleset) -> List[Dict[str, Any]]:
    false_clears: List[Dict[str, Any]] = []
    for chk in candidate.checks:
        scenario = SC.construct_scenario(chk)
        if not scenario.ok or scenario.expected_fail_status != "FAIL" or scenario.fail_loan is None:
            continue
        probe = Ruleset(ruleset_id=f"coverage-probe-{chk.id}", version=1, checks=[chk])
        res = engine_run(scenario.fail_loan, probe)
        actual = res.results[0].status if res.results else None
        if actual == "PASS":
            false_clears.append({"check_id": chk.id, "loan_id": scenario.fail_loan.loan_id,
                                  "expected": scenario.expected_fail_status, "actual": actual})
    return false_clears


def run_promotion_gate(
    candidate: Ruleset,
    baseline: Optional[Ruleset] = None,
    volume_n: int = 5000,
    volume_loans: Optional[List[LabeledLoan]] = None,
) -> PromotionGateResult:
    """The single CI-runnable entry point (FR-009). Orchestrates GOLDEN +
    COVERAGE + VOLUME + the generalized metamorphic invariants against
    `candidate`, collects every false-auto-clear across all three tiers, and
    returns a deterministic `PromotionGateResult` (US2 Acceptance Scenario 3
    -- re-running with identical inputs produces an identical result)."""
    loans = volume_loans if volume_loans is not None else G.generate(volume_n)
    volume, volume_false_clears = _run_volume_tier(candidate, loans)

    coverage_result = CS.compute_coverage(candidate)
    coverage = {
        "checks_total": coverage_result.checks_total,
        "checks_covered": coverage_result.checks_covered,
        "coverage_fraction": coverage_result.coverage_fraction,
        "construction_failures": list(coverage_result.construction_failures),
    }
    coverage_false_clears = _coverage_false_auto_clears(candidate)

    golden_result = GS.replay_golden_panel(candidate=candidate, baseline=baseline)
    golden = {
        "panel_version": golden_result.panel_version,
        "total_cases": golden_result.total_cases,
        "regressions": [
            {"check_id": f.check_id, "loan_id": f.loan_id,
             "baseline_status": f.baseline_status, "candidate_status": f.candidate_status}
            for f in golden_result.regressions
        ],
    }
    # A GOLDEN flip FROM a known FAIL TO an auto-cleared PASS is itself a
    # false-auto-clear (FR-006 "in any of the three tiers"); any OTHER flip
    # is reported in `golden.regressions` but does not by itself block here
    # (spec.md Edge Cases: a flip can be an intended correction -- FR-007's
    # human-acknowledgment requirement is the caller-facing gate for those,
    # not an automatic BLOCK).
    golden_false_clears = [
        {"check_id": f.check_id, "loan_id": f.loan_id,
         "expected": f.baseline_status, "actual": f.candidate_status}
        for f in golden_result.regressions
        if f.baseline_status == "FAIL" and f.candidate_status == "PASS"
    ]

    invariants = run_invariants(candidate)

    false_auto_clears = volume_false_clears + coverage_false_clears + golden_false_clears
    promotion_decision = "BLOCK" if false_auto_clears else "PROMOTE"
    exit_code = 0 if promotion_decision == "PROMOTE" else 1

    return PromotionGateResult(
        promotion_decision=promotion_decision,
        exit_code=exit_code,
        false_auto_clears=false_auto_clears,
        golden=golden,
        coverage=coverage,
        volume=volume,
        invariants=invariants,
    )


def main() -> int:
    n = 5000
    for a in sys.argv[1:]:
        if a.isdigit():
            n = int(a)

    candidate = demo_ruleset()
    result = run_promotion_gate(candidate=candidate, volume_n=n)

    print("\n=== PROMOTION GATE ===")
    print(f"  candidate       : {candidate.ruleset_id} v{candidate.version}")
    print(f"  GOLDEN          : panel={result.golden['panel_version']} "
          f"cases={result.golden['total_cases']} "
          f"regressions={len(result.golden['regressions'])}")
    print(f"  COVERAGE        : {result.coverage['checks_covered']}/"
          f"{result.coverage['checks_total']} "
          f"({result.coverage['coverage_fraction']:.1%})")
    print(f"  VOLUME          : n={result.volume['n_loans']} "
          f"auto_clear_rate={result.volume['auto_clear_rate']} "
          f"false_auto_clear_count={result.volume['false_auto_clear_count']}")
    print(f"  INVARIANTS      : " + ", ".join(
        f"{name}={'n/a' if not v['applicable'] else ('OK' if v['passed'] else 'FAIL')}"
        for name, v in result.invariants.items()))
    print(f"\n  PROMOTION_DECISION: {result.promotion_decision}")
    if result.false_auto_clears:
        print(f"  FALSE-AUTO-CLEARS ({len(result.false_auto_clears)}):")
        for fc in result.false_auto_clears[:10]:
            print(f"    - {fc['check_id']}/{fc['loan_id']}: "
                  f"expected {fc['expected']}, got {fc['actual']}")

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "promotion_gate_result.json")
    with open(out_path, "w") as fh:
        json.dump(result.to_dict(), fh, indent=2, sort_keys=False)
    print(f"\n  artifact -> {out_path}\n")

    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
