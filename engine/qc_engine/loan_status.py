"""
021-touchless-audit-run: severity-tiered loan status (research.md Item 1).

`engine.py`'s own `RunResult.disposition` is binary (AUTO_CLEARED /
NEEDS_REVIEW) -- there is no CRITICAL-vs-WARNING/INFO split anywhere in the
engine's own disposition logic, and this feature's demo needs one
(PASS / FAILED / NEEDS_REVIEW). This is a new, pure, read-only mapping
function over the engine's existing `RunResult.qc_failures`/`needs_review`
properties -- NOT a change to `engine.py` itself (Non-Negotiable #1/#2
forbid touching the pure, signed-artifact-driven engine to special-case one
demo's status vocabulary).

`ERROR` is not produced here -- it's assigned by the calling layer (the
backend route) when the Python process itself fails to complete, never by a
successful engine run (data-model.md's "Audit Verdict").
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, os.path.dirname(_HERE))

from qc_engine.engine import RunResult  # noqa: E402

PASS = "PASS"
FAILED = "FAILED"
NEEDS_REVIEW = "NEEDS_REVIEW"


def derive_loan_status(run_result: RunResult) -> str:
    """PASS (zero qc_failures) / FAILED (>=1 CRITICAL-severity qc_failure) /
    NEEDS_REVIEW (qc_failures or needs_review present, none CRITICAL)."""
    qc_failures = run_result.qc_failures
    if any(r.severity == "CRITICAL" for r in qc_failures):
        return FAILED
    if qc_failures or run_result.needs_review:
        return NEEDS_REVIEW
    return PASS
