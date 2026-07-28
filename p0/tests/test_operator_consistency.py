"""
002d: tests for `operator_consistency_check()` -- the deterministic (no LLM
call) gate that flags a compiled `ratio_threshold` Check whose `operator`
direction contradicts its own `message_pass` text.

Scope: (1) the two confirmed-bad checks (`fnm-ltv-mi-required`,
`ltv-exceeds-80-without-mi`) and the 45-check true-positive floor from
`output/operator_inversion_suspects_2026-07-24.json` (SC-001); (2) the
false-positive rate against the ~450 checks in `post_closing_only_ruleset.json`
NOT in that suspect set (SC-002) -- measured and reported, not assumed zero.

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))
_QC_ENGINE = os.path.join(os.path.dirname(_HERE), "qc_engine")

import sys  # noqa: E402
if _QC_ENGINE not in sys.path:
    sys.path.insert(0, os.path.dirname(_HERE))
if os.path.dirname(_QC_ENGINE) not in sys.path:
    sys.path.insert(0, os.path.dirname(_QC_ENGINE))

from qc_engine.compiler.compile_llm import operator_consistency_check  # noqa: E402
from qc_engine.ruleset import Check  # noqa: E402

_RULESET_PATH = os.path.join(_REPO_ROOT, "result", "rules", "post_closing_only_ruleset.json")
_SUSPECTS_PATH = os.path.join(_REPO_ROOT, "output", "operator_inversion_suspects_2026-07-24.json")


def _load_ratio_threshold_checks():
    """Every ratio_threshold entry in the real, currently-signed ruleset
    (kept unde-duplicated by id -- a check_id can legitimately carry more
    than one distinct compiled body across product variants, and de-duping
    by id alone would hide a bad copy behind a good one sharing the same
    id)."""
    with open(_RULESET_PATH) as f:
        data = json.load(f)
    return [c for c in data["content"]["checks"] if c["kind"] == "ratio_threshold"]


def _load_suspect_ids():
    with open(_SUSPECTS_PATH) as f:
        data = json.load(f)
    return {s["check_id"] for s in data["suspects"]}


def _check_from_raw(raw: dict) -> Check:
    kwargs = {k: v for k, v in raw.items() if k in Check.__dataclass_fields__}
    return Check(**kwargs)


@pytest.fixture(scope="module")
def raw_ratio_threshold_checks():
    return _load_ratio_threshold_checks()


@pytest.fixture(scope="module")
def suspect_ids():
    return _load_suspect_ids()


def test_confirmed_bad_checks_are_flagged(raw_ratio_threshold_checks):
    """The two checks that produced the real, reported false positive at
    loan 01's exact 80% LTV boundary (spec.md's opening finding) must be
    flagged."""
    by_id = {c["id"]: c for c in raw_ratio_threshold_checks}
    for check_id in ("fnm-ltv-mi-required", "ltv-exceeds-80-without-mi"):
        assert check_id in by_id, f"{check_id} not found in the real ruleset fixture"
        chk = _check_from_raw(by_id[check_id])
        reason = operator_consistency_check(chk)
        assert reason is not None, f"{check_id} should be flagged, got None"


def test_true_positive_floor_reproduces_the_45_suspects(raw_ratio_threshold_checks, suspect_ids):
    """SC-001: the formalized gate, run against every ratio_threshold check in
    the real ruleset, flags at least the 45 checks the manual heuristic scan
    already found -- a floor, not a ceiling (Acceptance Scenario 3 permits
    the gate catching additional phrasings the manual scan didn't)."""
    flagged_ids = set()
    for raw in raw_ratio_threshold_checks:
        chk = _check_from_raw(raw)
        if operator_consistency_check(chk) is not None:
            flagged_ids.add(chk.id)

    missing = suspect_ids - flagged_ids
    assert not missing, (
        f"{len(missing)} of the 45 known suspects were NOT flagged (SC-001 floor "
        f"violated): {sorted(missing)}"
    )


def test_false_positive_rate_against_correct_checks(raw_ratio_threshold_checks, suspect_ids):
    """SC-002/FR-007: measure (not assume) the false-positive rate against
    checks NOT in the 45-suspect set. Reported honestly regardless of outcome
    -- per Edge Cases, a small number of additional catches sharing the exact
    same message_pass/operator contradiction pattern as the confirmed 45 are
    plausible genuine defects the manual scan simply missed, not heuristic
    noise; this test documents the count and the specific checks rather than
    silently asserting zero."""
    correct_sample = [c for c in raw_ratio_threshold_checks if c["id"] not in suspect_ids]
    assert len(correct_sample) > 400, "expected a large representative correct-check sample"

    false_positives = []
    for raw in correct_sample:
        chk = _check_from_raw(raw)
        reason = operator_consistency_check(chk)
        if reason is not None:
            false_positives.append((chk.id, chk.operator, reason))

    fp_rate = len(false_positives) / len(correct_sample)
    print(f"\n[SC-002] false-positive rate against {len(correct_sample)} correct checks: "
          f"{len(false_positives)} ({fp_rate:.2%})")
    for check_id, operator, reason in false_positives:
        print(f"  FLAGGED (not in the 45): {check_id} operator={operator!r} -- {reason}")

    # Validated during implementation (an ad-hoc scan script, since superseded
    # by operator_consistency_check() itself, against the real
    # ruleset): exactly 3 additional catches, each the same compound-OR
    # contradiction pattern as the confirmed 45 (e.g. "X is below N%; Y
    # requirement does not apply" with operator ">="). A materially higher
    # rate would indicate the phrase table itself regressed.
    assert fp_rate < 0.02, (
        f"false-positive rate {fp_rate:.2%} exceeds the validated ~0.7% baseline -- "
        f"investigate before shipping (SC-002)"
    )


def test_no_signal_does_not_flag():
    """Edge Cases: a check whose message_pass contains no recognized
    comparison phrase is not flagged -- absence of a contradiction signal is
    not evidence of a contradiction."""
    chk = Check(
        id="no-signal-example", name="x", field_name="some_field",
        kind="ratio_threshold", severity="WARNING", phase="QC",
        ratio="field_value", threshold="5", operator=">",
        message_pass="Value is within the program guideline.",
        message_fail="Value is outside the program guideline.",
    )
    assert operator_consistency_check(chk) is None


def test_consistent_check_not_flagged():
    """A correctly-compiled check (operator matches its own message_pass
    direction) must not be flagged -- no regression on the ~450
    already-correct checks (Acceptance Scenario 2)."""
    chk = Check(
        id="consistent-example", name="x", field_name="ltv",
        kind="ratio_threshold", severity="WARNING", phase="QC",
        ratio="ltv", threshold="80", operator="<=",
        message_pass="LTV is at or below 80%; MI not required.",
        message_fail="LTV exceeds 80%; MI is required.",
    )
    assert operator_consistency_check(chk) is None


def test_inverted_check_is_flagged():
    """The exact defect class this feature exists to catch: FAIL-framed
    defect_text transcribed literally instead of inverted."""
    chk = Check(
        id="inverted-example", name="x", field_name="ltv",
        kind="ratio_threshold", severity="WARNING", phase="QC",
        ratio="ltv", threshold="80", operator=">",
        message_pass="LTV is at or below 80%; MI not required.",
        message_fail="LTV exceeds 80%; MI is required.",
    )
    reason = operator_consistency_check(chk)
    assert reason is not None
    assert "<=" in reason or "<" in reason
