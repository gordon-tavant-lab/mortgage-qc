"""
COVERAGE tier -- does every compiled check in a candidate Ruleset have at
least one proven pass/fail scenario? (spec.md FR-005, SC-002; 005 User
Story 3, wired to User Story 1's constructor.)

Iterates every `Check` in a candidate `Ruleset`, calls
`scenario_construction.construct_scenario` exactly once per check (no
hand-written per-field mutation code -- SC-002), and tallies
checks_covered / checks_total / named construction failures. This answers a
DIFFERENT question than VOLUME (does zero-false-auto-clear hold at scale) or
GOLDEN (did a known-correct case regress): "does every check the candidate
ruleset actually contains have a proven scenario at all?"

Python 3.9 compatible.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qc_engine.ruleset import Ruleset  # noqa: E402

import scenario_construction as SC  # noqa: E402


@dataclass
class CoverageResult:
    checks_total: int
    checks_covered: int
    coverage_fraction: float
    construction_failures: List[Dict[str, Any]] = field(default_factory=list)


def compute_coverage(ruleset: Ruleset) -> CoverageResult:
    """Calls `scenario_construction.construct_scenario(chk)` once per `chk`
    in `ruleset.checks` -- zero hand-written per-field mutation code added to
    reach this coverage (SC-002). A check whose kind has no registered
    strategy (or whose construction otherwise fails) is named in
    `construction_failures`, never silently dropped from the total."""
    total = len(ruleset.checks)
    covered = 0
    failures: List[Dict[str, Any]] = []
    for chk in ruleset.checks:
        scenario = SC.construct_scenario(chk)
        if scenario.ok:
            covered += 1
        else:
            failures.append({
                "check_id": scenario.check_id,
                "kind": scenario.kind,
                "error": scenario.error,
            })
    fraction = (covered / total) if total else 1.0
    return CoverageResult(checks_total=total, checks_covered=covered,
                          coverage_fraction=fraction,
                          construction_failures=failures)


def main() -> int:
    import json
    from fixtures.ruleset_demo import demo_ruleset
    result = compute_coverage(demo_ruleset())
    print(f"COVERAGE: {result.checks_covered}/{result.checks_total} "
          f"({result.coverage_fraction:.1%})")
    if result.construction_failures:
        print(json.dumps(result.construction_failures, indent=2))
    return 0 if result.checks_covered == result.checks_total else 1


if __name__ == "__main__":
    raise SystemExit(main())
