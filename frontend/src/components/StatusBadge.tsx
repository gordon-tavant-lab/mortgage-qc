import type { CheckStatus, LoanStatus, Severity } from "../lib/types";

const CHECK_STATUS_STYLES: Record<CheckStatus, string> = {
  PASS: "bg-emerald-50 text-emerald-700 border-emerald-200",
  FAIL: "bg-rose-50 text-rose-700 border-rose-200",
  WARNING: "bg-amber-50 text-amber-700 border-amber-200",
  FLAG: "bg-blue-50 text-blue-700 border-blue-200",
  NEEDS_REVIEW: "bg-amber-50 text-amber-700 border-amber-200",
  NOT_APPLICABLE: "bg-slate-100 text-slate-500 border-slate-200",
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

const LOAN_STATUS_STYLES: Record<LoanStatus, string> = {
  PENDING: "bg-slate-100 text-slate-600 border-slate-200",
  AUTO_CLEARED: "bg-emerald-50 text-emerald-700 border-emerald-200",
  EXCEPTION: "bg-rose-50 text-rose-700 border-rose-200",
  RESOLVED: "bg-blue-50 text-blue-700 border-blue-200",
};

const LOAN_STATUS_LABELS: Record<LoanStatus, string> = {
  PENDING: "Pending",
  AUTO_CLEARED: "Auto-Cleared",
  EXCEPTION: "Exception",
  RESOLVED: "Resolved",
};

export function LoanStatusBadge({ status }: { status: LoanStatus }) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-bold ${LOAN_STATUS_STYLES[status]}`}
    >
      {LOAN_STATUS_LABELS[status]}
    </span>
  );
}
