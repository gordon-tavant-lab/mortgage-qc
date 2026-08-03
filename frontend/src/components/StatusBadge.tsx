import type { CheckStatus, LoanDisplayState, LoanStatus, Severity } from "../lib/types";

const CHECK_STATUS_STYLES: Record<CheckStatus, string> = {
  PASS: "bg-emerald-50 text-emerald-700 border-emerald-200",
  FAIL: "bg-rose-50 text-rose-700 border-rose-200",
  WARNING: "bg-amber-50 text-amber-700 border-amber-200",
  FLAG: "bg-blue-50 text-blue-700 border-blue-200",
  NEEDS_REVIEW: "bg-amber-50 text-amber-700 border-amber-200",
  NOT_APPLICABLE: "bg-slate-100 text-slate-500 border-slate-200",
  // Distinct from NOT_APPLICABLE (ran, gated out) and never green -- this check has no
  // executable logic yet, so it never ran at all. Dashed border keeps it visually
  // distinct from every real verdict, per spec019 FR-016's compile-state discipline.
  NOT_COMPILED: "bg-white text-slate-400 border-slate-300 border-dashed",
};

export function CheckStatusBadge({ status }: { status: CheckStatus }) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-bold ${CHECK_STATUS_STYLES[status]}`}
    >
      {status}
    </span>
  );
}

const SEVERITY_STYLES: Record<Severity, string> = {
  CRITICAL: "bg-rose-50 text-rose-700 border-rose-100",
  WARNING: "bg-amber-50 text-amber-700 border-amber-100",
  INFO: "bg-blue-50 text-blue-700 border-blue-100",
};

export function SeverityBadge({ severity }: { severity: Severity }) {
  return (
    <span
      className={`rounded border px-1.5 py-0.5 font-mono text-[10px] uppercase ${SEVERITY_STYLES[severity]}`}
    >
      {severity}
    </span>
  );
}

// Revised for spec021 (2026-08-02) -- see types.ts's LoanStatus for the vocabulary change.
const LOAN_STATUS_STYLES: Record<LoanStatus, string> = {
  PASS: "bg-emerald-50 text-emerald-700 border-emerald-200",
  FAILED: "bg-rose-50 text-rose-700 border-rose-200",
  NEEDS_REVIEW: "bg-amber-50 text-amber-700 border-amber-200",
  RESOLVED: "bg-blue-50 text-blue-700 border-blue-200",
  ERROR: "bg-rose-50 text-rose-700 border-rose-200",
};

const LOAN_STATUS_LABELS: Record<LoanStatus, string> = {
  PASS: "Pass",
  FAILED: "Failed",
  NEEDS_REVIEW: "Needs Review",
  RESOLVED: "Resolved",
  ERROR: "Error",
};

// LoanStatusBadge now takes a derived LoanDisplayState (dataSourceContext.tsx's
// deriveLoanDisplayState()), not a bare LoanStatus -- it must be able to render the
// transient "running"/"not yet fetched" states too, per spec021 FR-004/FR-006a, never
// fabricating a PASS/FAIL badge before a real verdict exists.
export function LoanStatusBadge({ display }: { display: LoanDisplayState }) {
  if (display.kind === "running") {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full border border-blue-200 bg-blue-50 px-2.5 py-1 text-[11px] font-bold text-blue-700">
        <span className="h-1.5 w-1.5 animate-pulse-dot rounded-full bg-blue-500" />
        Running…
      </span>
    );
  }
  if (display.kind === "not_fetched") {
    return (
      <span className="inline-flex items-center rounded-full border border-dashed border-slate-300 bg-white px-2.5 py-1 text-[11px] font-bold text-slate-400">
        Not Yet Evaluated
      </span>
    );
  }
  if (display.kind === "error") {
    return (
      <span
        className="inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-bold border-rose-200 bg-rose-50 text-rose-700"
        title={display.message}
      >
        Error
      </span>
    );
  }
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-bold ${LOAN_STATUS_STYLES[display.status]}`}
    >
      {LOAN_STATUS_LABELS[display.status]}
    </span>
  );
}
