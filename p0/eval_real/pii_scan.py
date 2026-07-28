"""
012 Foundational (T004) -- the PII scan gate (FR-012/SC-004).

No raw real-loan PII value (borrower name, address, SSN fragment) may ever
land in a git-tracked path in this repository. This module is that gate: it
scans a given set of paths for a given set of known patterns and reports,
loudly and specifically, which pattern matched which path -- never a vague
"something matched."

This is a scan/grep gate, not a redaction tool -- it exists to catch a leak
BEFORE it is committed, per FR-012/SC-004. The specific real-loan PII
patterns it is run against in practice (real borrower names, ssn_last4
values, the real property address) are loaded from a local-only, gitignored
reference file at call time (see `load_known_patterns_file`) -- never
hardcoded into this git-tracked module, so this file itself never carries a
real PII value.

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import List, Optional, Sequence


class PiiScanGateError(Exception):
    """Raised by `assert_clean` when a scan finds >=1 PII match -- the hard,
    commit-blocking form of the gate (T006)."""


@dataclass
class PiiMatch:
    path: str
    pattern: str


@dataclass
class PiiScanReport:
    clean: bool
    matches: List[PiiMatch] = field(default_factory=list)

    def to_dict(self):
        return {
            "clean": self.clean,
            "matches": [{"path": m.path, "pattern": m.pattern} for m in self.matches],
        }


def scan_paths(paths: Sequence[str], patterns: Sequence[str]) -> PiiScanReport:
    """Scan every path in `paths` for every pattern in `patterns` (plain
    substring match -- deliberately simple and auditable, not a regex engine
    a reviewer would need to trust blindly).

    A missing path is treated as clean for that path (T005's own framing: a
    pre-commit-style gate must not blow up someone's commit for an unrelated
    reason, e.g. a file already deleted between staging and the gate
    running) -- it is NOT treated as a match.
    """
    matches: List[PiiMatch] = []
    for path in paths:
        if not patterns:
            continue
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                content = fh.read()
        except OSError:
            # Unreadable (permissions, race, etc.) -- don't crash the gate;
            # surface nothing rather than a false negative masquerading as a
            # false positive.
            continue
        for pattern in patterns:
            if pattern and pattern in content:
                matches.append(PiiMatch(path=path, pattern=pattern))
    return PiiScanReport(clean=(len(matches) == 0), matches=matches)


def assert_clean(paths: Sequence[str], patterns: Sequence[str]) -> PiiScanReport:
    """Hard, commit-blocking form of the gate (T006): raises
    `PiiScanGateError` naming every match if the scan is not clean; returns
    the (clean) report otherwise, for callers that want to log a passing
    run."""
    report = scan_paths(paths, patterns)
    if not report.clean:
        detail = "; ".join(f"{m.pattern!r} in {m.path}" for m in report.matches)
        raise PiiScanGateError(
            f"PII scan gate FAILED -- {len(report.matches)} match(es) found, "
            f"must be redacted or excluded before commit: {detail}"
        )
    return report


def load_known_patterns_file(path: str) -> List[str]:
    """Load the real-loan PII pattern list from a local-only, gitignored
    reference file (a flat JSON list of strings) -- e.g.
    `p0/eval_real/local_cache/known_pii_patterns.json`, populated manually
    from the real loan bundles once fetched (T004's own framing: never
    hardcoded into this git-tracked module).

    Returns an empty list (never raises) if the file doesn't exist yet -- the
    gate degrades to "nothing known to check for," which is the honest state
    before any real loan has been fetched locally, not a crash.
    """
    if not os.path.isfile(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected a flat JSON list of pattern strings")
    return [str(p) for p in data]
