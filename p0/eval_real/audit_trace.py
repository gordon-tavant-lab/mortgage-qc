"""
012 User Story 2 (T015/T016) -- the mock-audit exit criterion (FR-007/008).

`007` already built the hash-chained `AuditLog`/`verify_chain()` mechanism
and already proved it against synthetic artifacts. This module is the first
time that chain is exercised against a real-adapted loan's own real
citations (a real document name, page number, extracted segment) -- it
consumes `qc_engine.engine.run` and `qc_engine.audit.AuditLog` completely
unmodified (FR-014), it does not add new engine or chain machinery.

Two things live here:
  - `run_and_append`: runs the unmodified engine against an adapted loan,
    appends the resulting `RunResult` to a real `AuditLog` (FR-007).
  - `build_examiner_trace`: renders one `CheckResult` (by check_id) from a
    `RunResult` into a human-readable `ExaminerTraceReport` -- rule id,
    signed ruleset version + SHA-256, every input `SourceValue`, any
    normalization/rounding, the verdict, and -- for doc-sourced values -- the
    real source document name/page/segment (FR-008). Every field FR-008
    requires already exists on `CheckResult`/`RunResult` (007's own shape);
    this is a re-projection into examiner-readable snake_case + a plain-
    English narrative sentence, not a new engine field.

Python 3.9 compatible.
"""
from __future__ import annotations

import os
import sys
from typing import Any, Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qc_engine import AuditLog, run as engine_run  # noqa: E402
from qc_engine.engine import RunResult  # noqa: E402
from qc_engine.model import CanonicalLoan  # noqa: E402
from qc_engine.ruleset import Ruleset  # noqa: E402


def run_and_append(loan: CanonicalLoan, ruleset: Ruleset, audit_log: AuditLog,
                    signed_at: str) -> RunResult:
    """FR-007: run the unmodified engine against `loan`, append the
    resulting `RunResult` to `audit_log`. `signed_at` is caller-injected
    (never wall-clock), matching the engine's own pure-function discipline
    (`qc_engine.engine`'s module docstring) -- reproducible runs, not a
    hidden nondeterministic input smuggled in through the audit layer."""
    run_result = engine_run(loan, ruleset)
    audit_log.append(run_result, signed_at=signed_at)
    return run_result


def _find_result(run_result: RunResult, check_id: str):
    for r in run_result.results:
        if r.check_id == check_id:
            return r
    raise KeyError(f"check_id {check_id!r} not found in this RunResult "
                    f"(loan_id={run_result.loan_id!r})")


def _citation_for_trace(citation: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """`CheckResult.citation` is already-built, camelCase JSON
    (`docName`/`pageNum`/`segmentSnippet`, per `DocCitation.to_dict()`) --
    the ExaminerTraceReport is a distinct, examiner-facing contract (FR-008
    names `doc name/page number/segment` in plain terms), so this
    re-projects into snake_case rather than reusing the engine's own
    wire-format keys verbatim."""
    if not citation:
        return None
    return {
        "doc_name": citation.get("docName"),
        "page_num": citation.get("pageNum"),
        "segment_snippet": citation.get("segmentSnippet"),
    }


def _narrative(check_id: str, check_name: str, verdict: str, message: str,
               ruleset_version: int, ruleset_sha256: str) -> str:
    """SC-003: a reader must be able to walk this start-to-finish without
    reading qc_engine source code -- a plain-English sentence naming the
    check, the verdict, and why, plus the exact signed-ruleset identity an
    examiner would cite."""
    return (
        f"Check {check_id} ({check_name}) was evaluated under ruleset "
        f"version {ruleset_version} (SHA-256 {ruleset_sha256}). "
        f"Verdict: {verdict}. {message}".strip()
    )


def build_examiner_trace(run_result: RunResult, check_id: str) -> Dict[str, Any]:
    """FR-008: the full examiner audit walk for one check's verdict from one
    run -- rule id, ruleset version/hash, every input `SourceValue`, any
    normalization/rounding applied, the verdict, and (for doc-sourced
    values) the real document name/page/segment."""
    cr = _find_result(run_result, check_id)
    trace: Dict[str, Any] = {
        "check_id": cr.check_id,
        "check_name": cr.check_name,
        "severity": cr.severity,
        "verdict": cr.status,
        "phase": cr.phase,
        "ruleset_id": run_result.ruleset_id,
        "ruleset_version": run_result.ruleset_version,
        "ruleset_sha256": run_result.ruleset_sha256,
        "engine_version": run_result.engine_version,
        "inputs": cr.inputs,
        "normalized": cr.normalized,
        "compared_value": cr.compared_value,
        "rounding": cr.rounding,
        "tolerance": cr.tolerance,
        "doc_confidence": cr.doc_confidence,
        "message": cr.message,
        "review_reason": cr.review_reason,
        "citation": _citation_for_trace(cr.citation),
    }
    trace["narrative"] = _narrative(
        cr.check_id, cr.check_name, cr.status, cr.message,
        run_result.ruleset_version, run_result.ruleset_sha256,
    )
    return trace
