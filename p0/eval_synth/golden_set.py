"""
GOLDEN tier -- did a known-correct case regress between a previously-promoted
baseline Ruleset and a candidate Ruleset? (spec.md FR-005/007, SC-004; 005
User Story 3.)

Replays a fixed, version-controlled panel of `(loan, expected_verdicts,
provenance)` triples (`p0/fixtures/golden_panel.py` by default) against the
candidate ruleset, and reports every verdict that FLIPS relative to a
baseline. Per spec.md Edge Cases: a flip is not automatically treated as a
regression (an intended correction can flip a verdict on purpose) -- this
module's job is only to report every flip explicitly, named, never
aggregated away into a bare count; a human (or the promotion gate's own
FR-007 acknowledgment requirement) decides what to do with it.

When `baseline` is omitted (the "no prior-promoted ruleset exists yet" edge
case, spec.md Edge Cases), each panel entry's own pinned `expected_verdicts`
stand in as the baseline -- so GOLDEN is still meaningful on a project's very
first candidate ruleset, not just on a second-and-later one.

Python 3.9 compatible.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qc_engine.model import CanonicalLoan  # noqa: E402
from qc_engine.ruleset import Ruleset  # noqa: E402
from qc_engine.engine import run as engine_run  # noqa: E402

from fixtures import golden_panel as _default_panel  # noqa: E402

LabeledLoan = Tuple[CanonicalLoan, Dict[str, str], Dict[str, Any]]


@dataclass
class GoldenFlip:
    check_id: str
    loan_id: str
    baseline_status: str
    candidate_status: str


@dataclass
class GoldenResult:
    panel_version: str
    total_cases: int
    regressions: List[GoldenFlip] = field(default_factory=list)


def _verdicts(loan: CanonicalLoan, ruleset: Ruleset) -> Dict[str, str]:
    res = engine_run(loan, ruleset)
    return {r.check_id: r.status for r in res.results}


def replay_golden_panel(
    candidate: Ruleset,
    baseline: Optional[Ruleset] = None,
    panel: Optional[List[LabeledLoan]] = None,
    panel_version: Optional[str] = None,
) -> GoldenResult:
    """Replays `panel` (defaults to `golden_panel.PANEL` /
    `golden_panel.PANEL_VERSION` when not given) against `candidate`. For
    each `(loan, expected_verdicts, provenance)` entry: `baseline_status` for
    a check_id is the live `baseline` ruleset's verdict when `baseline` is
    given, else the panel's own pinned `expected_verdicts[check_id]`. A
    `GoldenFlip` is recorded whenever `candidate`'s verdict differs from
    `baseline_status` for a check_id the candidate ruleset actually contains
    a verdict for (FR-007)."""
    if panel is None:
        panel = _default_panel.PANEL
        if panel_version is None:
            panel_version = _default_panel.PANEL_VERSION
    if panel_version is None:
        panel_version = _default_panel.PANEL_VERSION

    regressions: List[GoldenFlip] = []
    for loan, expected_verdicts, _prov in panel:
        candidate_verdicts = _verdicts(loan, candidate)
        baseline_verdicts = _verdicts(loan, baseline) if baseline is not None else None
        for check_id, expected_status in expected_verdicts.items():
            candidate_status = candidate_verdicts.get(check_id)
            if candidate_status is None:
                # This candidate ruleset does not contain this check at all
                # -- nothing to compare, not this tier's concern.
                continue
            baseline_status = (baseline_verdicts.get(check_id)
                               if baseline_verdicts is not None else expected_status)
            if candidate_status != baseline_status:
                regressions.append(GoldenFlip(
                    check_id=check_id, loan_id=loan.loan_id,
                    baseline_status=baseline_status, candidate_status=candidate_status))
    return GoldenResult(panel_version=panel_version, total_cases=len(panel),
                        regressions=regressions)


def main() -> int:
    from fixtures.ruleset_demo import demo_ruleset
    result = replay_golden_panel(candidate=demo_ruleset())
    print(f"GOLDEN: panel_version={result.panel_version} "
          f"total_cases={result.total_cases} regressions={len(result.regressions)}")
    for flip in result.regressions:
        print(f"  {flip.check_id}/{flip.loan_id}: "
              f"{flip.baseline_status} -> {flip.candidate_status}")
    return 0 if not result.regressions else 1


if __name__ == "__main__":
    raise SystemExit(main())
