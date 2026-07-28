"""
002g FR-008 -- golden-panel replay: before a vocabulary or ruleset change
ships, replay a fixed panel of already-known loans through the old and new
versions and report exactly which (loan, check) resolutions change.

Adopted from a researched open-source precedent (002g spec.md Research,
source 5 -- `Sanctioned`'s "replay all 360 golden personas through both
versions; the report shows who flips"): a policy change should never ship on
the assertion that it's safe -- the panel proves what it actually flips,
before sign-off, at zero cost (pure engine runs, no LLM, no network).

Python 3.9 compatible.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .engine import run
from .model import CanonicalLoan
from .ruleset import Ruleset


@dataclass
class StatusFlip:
    loan_id: str
    check_id: str
    old_status: str
    new_status: str


@dataclass
class ReplayReport:
    """`flips` is the load-bearing output: empty means the change is proven
    behavior-neutral on the panel; non-empty names exactly what an SME must
    look at before signing. `only_in_old`/`only_in_new` catch check-set
    membership changes (a check added/removed between versions is a real
    change too, not a flip)."""
    loans_replayed: int = 0
    checks_compared: int = 0
    flips: List[StatusFlip] = field(default_factory=list)
    only_in_old: List[str] = field(default_factory=list)
    only_in_new: List[str] = field(default_factory=list)


def replay(loans: List[CanonicalLoan], old_ruleset: Ruleset,
           new_ruleset: Ruleset) -> ReplayReport:
    report = ReplayReport(loans_replayed=len(loans))
    old_ids = {c.id for c in old_ruleset.checks}
    new_ids = {c.id for c in new_ruleset.checks}
    report.only_in_old = sorted(old_ids - new_ids)
    report.only_in_new = sorted(new_ids - old_ids)
    shared = old_ids & new_ids

    for loan in loans:
        old_by_id: Dict[str, str] = {r.check_id: r.status
                                     for r in run(loan, old_ruleset).results}
        new_by_id: Dict[str, str] = {r.check_id: r.status
                                     for r in run(loan, new_ruleset).results}
        for check_id in sorted(shared):
            report.checks_compared += 1
            if old_by_id[check_id] != new_by_id[check_id]:
                report.flips.append(StatusFlip(
                    loan_id=loan.loan_id, check_id=check_id,
                    old_status=old_by_id[check_id],
                    new_status=new_by_id[check_id],
                ))
    return report
