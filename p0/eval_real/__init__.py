"""
012-real-loan-distribution-eval -- ingests already-acquired real closed loans
as an additional GOLDEN/VOLUME source into 005's `eval_synth` promotion gate.

Sibling package to `p0/eval_synth/`. See `specs/012-real-loan-distribution-eval/`
(spec.md/plan.md/tasks.md) for the full requirements this package satisfies.

Modules:
  - `pii_scan`          -- FR-012/SC-004: the scan gate no real-loan artifact
                           may skip before landing in a git-tracked path.
  - `mapping_gaps`       -- FR-004: named, never-silently-dropped unmapped
                           fields.
  - `adapter`            -- FR-001/002: RealLoanAdapter, bundle -> LabeledLoan
                           tuple.
  - `audit_trace`        -- FR-007/008: real-loan proof of the already-built
                           AuditLog hash chain + ExaminerTraceReport.
  - `bakeoff_real`       -- FR-009/010/011: G3 methodology re-run + real
                           cost/token measurement, independent of expert-label
                           availability.
  - `qc_doc_extraction`  -- FR-006: extraction patterns for the real bundles'
                           own already-classified, field-unextracted
                           third-party QC documents.
  - `s3_client`          -- thin, read-only boto3 wrapper (profile
                           'gordon-chan') for the manual/live real-bucket run
                           only (never CI).

PII discipline (FR-012): no raw real-loan value (borrower name, address, SSN
fragment) may ever land in a git-tracked file. `local_cache/` is
.gitignore-excluded for exactly this reason -- see this feature's spec.md
Risks.

Python 3.9 compatible.
"""
from __future__ import annotations
