"""
012 Foundational (T004/T005) -- the PII scan gate itself.

FR-012 / SC-004 make one thing non-negotiable: no raw real-loan PII value
(borrower name, address, SSN fragment) may ever reach a git-tracked path in
this repository. A scan gate nobody has ever watched actually catch a
planted match is not a real gate -- it's a comment. This file proves
`eval_real.pii_scan` catches a KNOWN, FAKE, PII-*shaped* string before it
ever touches a real loan.

SAFETY: every value in this file is hand-authored and synthetic. None of it
is drawn from, or resembles in any traceable way, the three real closed
loans this feature ingests -- no real loan id, no real borrower name, no
real address, no real SSN fragment, no real S3 path or credential appears
anywhere below. "123-45-6789" is the well-known placeholder SSN pattern used
throughout software testing/documentation (RFC-adjacent convention, e.g. IRS
publication examples) -- it is not, and has never been, a real person's SSN.

Python 3.9 compatible. `eval_real.pii_scan` does not exist yet -- every test
below is expected to fail RED via ImportError until it is implemented (see
tasks.md T004). Imports are deferred inside each test function (rather than
at module scope) so this file stays collectible by pytest even before the
package exists -- the same convention used by the other three new 012 test
files in this directory.
"""
from __future__ import annotations

import os

import pytest

# A synthetic, well-known PII-*shaped* placeholder value -- not a real SSN.
FAKE_SSN_PATTERN = "123-45-6789"
# A synthetic, obviously-fake borrower name -- never appears in any real
# loan bundle this project has ever touched.
FAKE_BORROWER_NAME = "Jamie Q. Testborrower"
# A synthetic, obviously-fake property address.
FAKE_ADDRESS = "1 Fake Test Lane, Testville, TS 00000"


def _write(tmp_path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return str(p)


def test_pii_scan_detects_a_planted_known_pattern(tmp_path):
    """T005: plant a KNOWN, FAKE PII-shaped string in a temp fixture file;
    confirm the scan gate catches it."""
    from eval_real.pii_scan import scan_paths

    dirty_path = _write(
        tmp_path, "dirty_fixture.json",
        '{"borrower_ssn_full": "%s", "note": "synthetic test fixture only"}'
        % FAKE_SSN_PATTERN,
    )

    report = scan_paths([dirty_path], patterns=[FAKE_SSN_PATTERN])

    assert report.clean is False
    assert len(report.matches) >= 1
    matched_paths = {m.path for m in report.matches}
    assert dirty_path in matched_paths


def test_pii_scan_detects_a_planted_known_name_pattern(tmp_path):
    """A second, independent planted pattern (a name, not just an SSN
    shape) -- confirms the gate isn't accidentally SSN-regex-only."""
    from eval_real.pii_scan import scan_paths

    dirty_path = _write(
        tmp_path, "dirty_name_fixture.txt",
        f"Borrower on file: {FAKE_BORROWER_NAME}\n",
    )

    report = scan_paths([dirty_path], patterns=[FAKE_BORROWER_NAME])

    assert report.clean is False
    assert any(m.path == dirty_path for m in report.matches)


def test_pii_scan_clean_fixture_passes(tmp_path):
    """A fixture that does NOT contain any of the given patterns must be
    reported clean -- the gate must not cry wolf on ordinary content."""
    from eval_real.pii_scan import scan_paths

    clean_path = _write(
        tmp_path, "clean_fixture.json",
        '{"check_id": "chk-note-signed", "status": "PASS", '
        '"message": "no PII in this fixture at all"}',
    )

    report = scan_paths(
        [clean_path], patterns=[FAKE_SSN_PATTERN, FAKE_BORROWER_NAME, FAKE_ADDRESS]
    )

    assert report.clean is True
    assert report.matches == []


def test_pii_scan_reports_zero_matches_across_multiple_clean_paths(tmp_path):
    """Scanning several clean paths at once stays clean -- the gate operates
    over a *set* of git-tracked paths (SC-004's own framing), not just one
    file at a time."""
    from eval_real.pii_scan import scan_paths

    p1 = _write(tmp_path, "a.json", '{"a": 1}')
    p2 = _write(tmp_path, "b.json", '{"b": 2}')
    p3 = _write(tmp_path, "c.md", "# nothing sensitive here\n")

    report = scan_paths([p1, p2, p3], patterns=[FAKE_SSN_PATTERN, FAKE_BORROWER_NAME])

    assert report.clean is True
    assert report.matches == []


def test_pii_scan_flags_which_specific_pattern_matched(tmp_path):
    """The gate must fail LOUDLY and specifically -- a caller needs to know
    *which* known pattern matched, not just that "something" did, so the
    person clearing the gate can find and redact the exact value."""
    from eval_real.pii_scan import scan_paths

    dirty_path = _write(
        tmp_path, "dirty_multi.json",
        '{"ssn": "%s", "borrower": "unrelated clean text"}' % FAKE_SSN_PATTERN,
    )

    report = scan_paths([dirty_path], patterns=[FAKE_SSN_PATTERN, FAKE_BORROWER_NAME])

    assert report.clean is False
    matched_patterns = {m.pattern for m in report.matches}
    assert FAKE_SSN_PATTERN in matched_patterns
    assert FAKE_BORROWER_NAME not in matched_patterns


def test_pii_scan_handles_missing_path_without_crashing(tmp_path):
    """A path that doesn't exist (e.g. a file already deleted between
    staging and the gate running) must not crash the gate -- it's a
    pre-commit check, not a place to blow up someone's commit for an
    unrelated reason."""
    from eval_real.pii_scan import scan_paths

    missing_path = os.path.join(str(tmp_path), "does_not_exist.json")

    report = scan_paths([missing_path], patterns=[FAKE_SSN_PATTERN])

    assert report.clean is True
    assert report.matches == []


def test_pii_scan_gate_raises_or_signals_failure_for_commit_use(tmp_path):
    """T006: the gate must be usable as a hard pre-commit-style check -- a
    caller needs a way to turn "not clean" into a loud failure, not just an
    inspectable report object that's easy to ignore."""
    from eval_real.pii_scan import scan_paths, PiiScanGateError, assert_clean

    dirty_path = _write(
        tmp_path, "dirty_for_gate.json", '{"ssn": "%s"}' % FAKE_SSN_PATTERN,
    )

    with pytest.raises(PiiScanGateError):
        assert_clean([dirty_path], patterns=[FAKE_SSN_PATTERN])

    clean_path = _write(tmp_path, "clean_for_gate.json", '{"ok": true}')
    # Must not raise on a clean path.
    assert_clean([clean_path], patterns=[FAKE_SSN_PATTERN])
