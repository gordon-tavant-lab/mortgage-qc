import { ArrowRight, Home, MapPin } from "lucide-react";
import { motion } from "motion/react";
import { MOCK_LOANS, MOCK_ROUTES } from "../data/mockData";
import { SampleDataBanner } from "./SampleDataBanner";
import { LoanStatusBadge } from "./StatusBadge";
import type { ViewId } from "../lib/nav";

interface LoanQueueProps {
  onOpenLoan: (view: ViewId) => void;
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
                onClick={() => onOpenLoan("apply")}
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
