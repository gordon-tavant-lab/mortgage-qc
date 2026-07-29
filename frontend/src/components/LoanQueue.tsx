import { ArrowRight, Home, MapPin, AlertOctagon, ChevronRight } from "lucide-react";
import { motion } from "motion/react";
import { MOCK_LOANS, MOCK_ROUTES, MOCK_FINDINGS } from "../data/mockData";
import { SampleDataBanner } from "./SampleDataBanner";
import { LoanStatusBadge, SeverityBadge } from "./StatusBadge";
import type { LoanDetailTab } from "../lib/nav";

interface LoanQueueProps {
  onOpenLoan: (loanId: string, tab?: LoanDetailTab) => void;
}

export function LoanQueue({ onOpenLoan }: LoanQueueProps) {
  const routeName = (routeId: string) =>
    MOCK_ROUTES.find((r) => r.id === routeId)?.name ?? routeId;

  const counts = {
    PENDING: MOCK_LOANS.filter((l) => l.status === "PENDING").length,
    AUTO_CLEARED: MOCK_LOANS.filter((l) => l.status === "AUTO_CLEARED").length,
    EXCEPTION: MOCK_LOANS.filter((l) => l.status === "EXCEPTION").length,
    RESOLVED: MOCK_LOANS.filter((l) => l.status === "RESOLVED").length,
  };

  const unresolved = MOCK_FINDINGS.filter((f) => f.mitigation === "UNRESOLVED");
  const criticalUnresolved = unresolved.filter((f) => f.severity === "CRITICAL").length;

  return (
    <div className="space-y-6 pb-12">
      <SampleDataBanner />

      <div>
        <h2 className="font-display text-xl font-bold text-slate-900">Loan Queue</h2>
        <p className="mt-1 text-sm text-slate-500">
          Point a route at a target set of loans and run on demand. "I'm done with this loan.
          Next one, next one, next one."
        </p>
      </div>

      {/* Exception dashboard — surfaces the portfolio's open exceptions here,
          rather than behind a separate nav destination, so the most urgent
          human-judgment items are the first thing anyone sees. */}
      <div className="overflow-hidden rounded-xl border border-rose-200 bg-rose-50/40 shadow-[var(--shadow-panel)]">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-rose-100 bg-rose-50 px-4 py-3">
          <div className="flex items-center gap-2">
            <AlertOctagon className="h-4 w-4 text-rose-600" />
            <h3 className="text-sm font-bold text-rose-900">Open Exceptions</h3>
          </div>
          <div className="flex items-center gap-3 text-xs font-semibold">
            <span className="text-rose-700">{unresolved.length} unresolved</span>
            <span className="text-rose-400">·</span>
            <span className="text-rose-700">{criticalUnresolved} critical</span>
          </div>
        </div>
        {unresolved.length === 0 ? (
          <div className="px-4 py-6 text-center text-xs text-slate-500">
            No unresolved exceptions across the portfolio.
          </div>
        ) : (
          <div className="divide-y divide-rose-100/70">
            {unresolved.map((f) => (
              <button
                key={f.id}
                onClick={() => onOpenLoan(f.loanId, "exceptions")}
                className="flex w-full items-center justify-between gap-3 px-4 py-2.5 text-left transition hover:bg-rose-50"
              >
                <div className="flex min-w-0 items-center gap-3">
                  <span className="shrink-0 font-mono text-[11px] font-bold text-slate-500">{f.loanId}</span>
                  <span className="truncate text-xs font-semibold text-slate-800">{f.checkName}</span>
                  <SeverityBadge severity={f.severity} />
                </div>
                <ChevronRight className="h-3.5 w-3.5 shrink-0 text-slate-400" />
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {(
          [
            ["PENDING", "Pending", "text-slate-600"],
            ["AUTO_CLEARED", "Auto-Cleared", "text-emerald-600"],
            ["EXCEPTION", "Exception", "text-rose-600"],
            ["RESOLVED", "Resolved", "text-blue-600"],
          ] as const
        ).map(([key, label, color]) => (
          <div key={key} className="rounded-xl border border-slate-200 bg-white p-4 shadow-[var(--shadow-panel)]">
            <div className="text-xs font-medium text-slate-500">{label}</div>
            <div className={`mt-1 font-mono text-2xl font-bold ${color}`}>{counts[key]}</div>
          </div>
        ))}
      </div>

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-[var(--shadow-panel)]">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50 text-xs font-semibold uppercase tracking-wide text-slate-500">
              <th className="px-4 py-3">Loan</th>
              <th className="px-4 py-3">Property</th>
              <th className="px-4 py-3">Route</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {MOCK_LOANS.map((loan, i) => (
              <motion.tr
                key={loan.loanId}
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.03 }}
                className="group cursor-pointer hover:bg-slate-50/70"
                onClick={() => onOpenLoan(loan.loanId)}
              >
                <td className="px-4 py-3">
                  <div className="font-mono text-xs font-bold text-slate-900">{loan.loanId}</div>
                  <div className="text-xs text-slate-500">
                    {loan.borrowerName} · {loan.loanType}
                  </div>
                </td>
                <td className="px-4 py-3 text-xs text-slate-600">
                  <div className="flex items-center gap-1.5">
                    <MapPin className="h-3 w-3 shrink-0 text-slate-400" />
                    <span className="max-w-[220px] truncate">{loan.propertyAddress}</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1.5 text-xs text-slate-600">
                    <Home className="h-3 w-3 shrink-0 text-slate-400" />
                    <span className="max-w-[200px] truncate">{routeName(loan.routeId)}</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <LoanStatusBadge status={loan.status} />
                </td>
                <td className="px-4 py-3 text-right">
                  <span className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 opacity-0 transition-opacity group-hover:opacity-100">
                    Open <ArrowRight className="h-3 w-3" />
                  </span>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
