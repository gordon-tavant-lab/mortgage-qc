"""
012 User Story 2 (T014) -- an examiner can trace a real loan's verdict back
to its inputs, rounding, rule version, and citation.

`007`'s hash-chained `AuditLog`/`verify_chain()` mechanism is already built
and already proven against synthetic artifacts. This file proves
`eval_real.audit_trace` -- the NEW module that runs the unmodified engine
against a real-shaped adapted loan, appends to a real `AuditLog`, and renders
a human-readable `ExaminerTraceReport` -- holds up the same way against a
real-shaped citation (a real page number, a real extracted snippet), for the
first time.

SAFETY: the loan below is a hand-authored SYNTHETIC stand-in (mirrors the
shape a real, adapted loan would have -- real-shaped `DocCitation`s with
document names/pages/snippets -- but every value is fake). No real loan id,
borrower name, address, SSN, or S3 path appears anywhere in this file.

Python 3.9 compatible. `eval_real.audit_trace` does not exist yet -- every
test that needs it is expected to fail RED via ImportError until T015/T016
land (tasks.md). Imports are deferred inside each test function so this file
stays collectible by pytest before the package exists.
"""
from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "eval_synth"))

from qc_engine import AuditLog  # noqa: E402
from qc_engine.model import DocCitation  # noqa: E402

import generator as G  # noqa: E402
from fixtures.ruleset_demo import demo_ruleset  # noqa: E402

RULESET = demo_ruleset()

STANDIN_LOAN_ID = "SYN-STANDIN-AUDIT-001"
STANDIN_BORROWER_NAME = "Jamie Q. Testborrower"
STANDIN_URLA_DOC = f"{STANDIN_LOAN_ID}-urla1003.pdf"
STANDIN_NOTE_DOC = f"{STANDIN_LOAN_ID}-promissorynote.pdf"


def _build_mixed_verdict_loan():
    """A synthetic stand-in loan, real-shaped: `chk-borrower-name` PASSes,
    `chk-note-signed` FAILs (note_signed forced False) -- guarantees at
    least one PASS and one FAIL verdict from a single run, as US2's
    Acceptance Scenario 3 requires. Citations carry real-shaped (but fake)
    document names/pages/snippets, not placeholders."""
    loan = G.build_clean(seed=99)
    loan.loan_id = STANDIN_LOAN_ID
    loan.fields["borrower_name"].citation = DocCitation(
        doc_name=STANDIN_URLA_DOC, page_num=3,
        segment_snippet=f"Borrower: {STANDIN_BORROWER_NAME}",
    )
    loan.fields["note_signed"].doc = False
    loan.fields["note_signed"].citation = DocCitation(
        doc_name=STANDIN_NOTE_DOC, page_num=12,
        segment_snippet="[No signature block present]",
    )
    return loan


# --------------------------------------------------------------------------- #
# verify_chain() True/False against a real-shaped run.
# --------------------------------------------------------------------------- #
def test_verify_chain_true_for_a_real_shaped_adapted_loan_run():
    from eval_real.audit_trace import run_and_append

    loan = _build_mixed_verdict_loan()
    audit_log = AuditLog(":memory:")

    run_and_append(loan, RULESET, audit_log, signed_at="2026-07-27T00:00:00Z")

    assert audit_log.verify_chain() is True


def test_verify_chain_false_after_tamper_simulation():
    """Tamper with one stored historical record directly (not through the
    AuditLog API -- exactly the attack this chain exists to catch) and
    confirm verify_chain() flips to False."""
    from eval_real.audit_trace import run_and_append

    loan = _build_mixed_verdict_loan()
    audit_log = AuditLog(":memory:")
    run_and_append(loan, RULESET, audit_log, signed_at="2026-07-27T00:00:00Z")
    assert audit_log.verify_chain() is True  # sanity, before tampering

    audit_log.conn.execute(
        "UPDATE audit_runs SET payload_json = ? WHERE seq = 1",
        ('{"tampered": true}',),
    )
    audit_log.conn.commit()

    assert audit_log.verify_chain() is False


def test_verify_chain_holds_across_multiple_real_shaped_runs_appended():
    """SC-002's own framing scores multiple real loans into the same log --
    proven here with several synthetic stand-ins to exercise the chain
    across >1 record without needing live real-loan data."""
    from eval_real.audit_trace import run_and_append

    audit_log = AuditLog(":memory:")
    for i in range(3):
        loan = _build_mixed_verdict_loan()
        loan.loan_id = f"{STANDIN_LOAN_ID}-{i}"
        run_and_append(loan, RULESET, audit_log, signed_at="2026-07-27T00:00:00Z")

    assert audit_log.verify_chain() is True
    assert len(audit_log.records()) == 3


# --------------------------------------------------------------------------- #
# ExaminerTraceReport -- FR-008's full audit walk, for one PASS and one
# FAIL/FLAG verdict.
# --------------------------------------------------------------------------- #
def test_examiner_trace_report_for_pass_verdict_names_full_audit_walk():
    from eval_real.audit_trace import run_and_append, build_examiner_trace

    loan = _build_mixed_verdict_loan()
    audit_log = AuditLog(":memory:")
    run_result = run_and_append(loan, RULESET, audit_log, signed_at="2026-07-27T00:00:00Z")

    trace = build_examiner_trace(run_result, "chk-borrower-name")

    assert trace["check_id"] == "chk-borrower-name"
    assert trace["verdict"] == "PASS"
    assert trace["ruleset_version"] == RULESET.version
    assert trace["ruleset_sha256"] == RULESET.sha256()
    assert "inputs" in trace and trace["inputs"]
    # Doc-sourced value -> real document name/page/segment, not a placeholder.
    assert trace["citation"]["doc_name"] == STANDIN_URLA_DOC
    assert trace["citation"]["page_num"] == 3
    assert STANDIN_BORROWER_NAME in trace["citation"]["segment_snippet"]


def test_examiner_trace_report_for_fail_verdict_names_full_audit_walk():
    from eval_real.audit_trace import run_and_append, build_examiner_trace

    loan = _build_mixed_verdict_loan()
    audit_log = AuditLog(":memory:")
    run_result = run_and_append(loan, RULESET, audit_log, signed_at="2026-07-27T00:00:00Z")

    trace = build_examiner_trace(run_result, "chk-note-signed")

    assert trace["check_id"] == "chk-note-signed"
    assert trace["verdict"] in ("FAIL", "FLAG")
    assert trace["ruleset_version"] == RULESET.version
    assert trace["ruleset_sha256"] == RULESET.sha256()
    assert trace["citation"]["doc_name"] == STANDIN_NOTE_DOC
    assert trace["citation"]["page_num"] == 12


def test_examiner_trace_report_is_human_readable_without_engine_source():
    """SC-003: independently walkable start-to-finish by a reader without
    needing to read qc_engine source code -- asserted here as a required
    human-readable narrative field naming the rule and the verdict in plain
    text, not just structured keys a reader would need the engine's own
    field names to decode."""
    from eval_real.audit_trace import run_and_append, build_examiner_trace

    loan = _build_mixed_verdict_loan()
    audit_log = AuditLog(":memory:")
    run_result = run_and_append(loan, RULESET, audit_log, signed_at="2026-07-27T00:00:00Z")

    trace = build_examiner_trace(run_result, "chk-note-signed")

    assert "narrative" in trace and isinstance(trace["narrative"], str)
    assert len(trace["narrative"]) > 0
    assert "chk-note-signed" in trace["narrative"] or "note" in trace["narrative"].lower()


# --------------------------------------------------------------------------- #
# Live/manual-only -- the TRUE real-loan variant, NOT executed here.
# --------------------------------------------------------------------------- #
@pytest.mark.skip(
    reason="Requires a real adapted loan (live AWS S3 access to the real "
           "closed-loan bundles already acquired for this feature -- see "
           "spec.md Foundation section) to produce a genuinely real "
           "DocCitation-backed examiner trace; not available in this test "
           "environment. This project's own convention keeps AWS-dependent "
           "runs out of `pytest p0/tests`. Run manually via "
           "eval_real.adapter + eval_real.audit_trace once credentials "
           "exist -- never as part of the default CI/pytest suite."
)
def test_examiner_trace_against_a_real_acquired_loan_LIVE_MANUAL_ONLY():
    """SC-003's true, live variant. Intentionally not implemented -- this
    stub exists only to name where that live check belongs, without
    executing it or referencing any real loan id, S3 path, or PII value in
    this repository."""
    pytest.skip("live S3 + real loan run -- manual only, see docstring")
