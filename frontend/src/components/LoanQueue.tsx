import { useEffect, useState } from "react";
import { ArrowRight, Home, MapPin } from "lucide-react";
import { motion } from "motion/react";
import { MOCK_LOANS, MOCK_ROUTES } from "../data/mockData";
import { LoanStatusBadge } from "./StatusBadge";
import { deriveLoanDisplayState, useDataSource } from "../lib/dataSourceContext";
import type { Loan, LoanDisplayState, LoanStatus } from "../lib/types";
import type { LoanDetailTab } from "../lib/nav";

const PAGE_SIZE = 20;

interface LoanQueueProps {
  onOpenLoan: (loanId: string, tab?: LoanDetailTab) => void;
}

export function LoanQueue({ onOpenLoan }: LoanQueueProps) {
  const dataSource = useDataSource();
  const [statusFilter, setStatusFilter] = useState<LoanStatus | null>(null);
  const [page, setPage] = useState(0);
  const routeName = (routeId: string) =>
    MOCK_ROUTES.find((r) => r.id === routeId)?.name ?? routeId;

  // live-demo-engine-wiring: the one real Touchless-backed loan starts OFF the queue
  // entirely (not just badged "Not Yet Evaluated") -- the demo should open on a clean,
  // all-cosmetic queue, and only gain this row once "Activate Live Demo" (SettingsMenu)
  // actually triggers a real pull. It then appears already in its live state (running,
  // then resolved) -- deriveLoanDisplayState never returns "not_fetched" for a loan with
  // no applicationId, so cosmetic loans are unaffected by this filter.
  const visibleLoans = MOCK_LOANS.filter(
    (loan) => !loan.applicationId || deriveLoanDisplayState(loan, dataSource).kind !== "not_fetched",
  );

  // These tiles read each loan's static seed status -- a coarse portfolio-health summary,
  // not a live reflection of the one real demo loan's current audit-run state (which is
  // shown per-row instead, via LoanQueueRow's deriveLoanDisplayState()).
  const counts = {
    PASS: MOCK_LOANS.filter((l) => l.status === "PASS").length,
    FAILED: MOCK_LOANS.filter((l) => l.status === "FAILED").length,
    NEEDS_REVIEW: MOCK_LOANS.filter((l) => l.status === "NEEDS_REVIEW").length,
    RESOLVED: MOCK_LOANS.filter((l) => l.status === "RESOLVED").length,
  };

  // Clicking a summary box filters by that loan's actual DISPLAYED status, not its static
  // seed -- for the one real Touchless-backed loan this means its real, engine-derived
  // verdict once resolved. A loan that's still "running" or "not_fetched" never matches
  // any status filter (it doesn't have one of these four yet).
  const filteredLoans = statusFilter
    ? visibleLoans.filter((loan) => {
        const display = deriveLoanDisplayState(loan, dataSource);
        return display.kind === "resolved" && display.status === statusFilter;
      })
    : visibleLoans;

  useEffect(() => {
    setPage(0);
  }, [statusFilter]);

  const totalPages = Math.max(1, Math.ceil(filteredLoans.length / PAGE_SIZE));
  const currentPage = Math.min(page, totalPages - 1);
  const pagedLoans = filteredLoans.slice(currentPage * PAGE_SIZE, currentPage * PAGE_SIZE + PAGE_SIZE);

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h2 className="font-display text-xl font-bold text-slate-900">Loan Queue</h2>
        <p className="mt-1 text-sm text-slate-500">
          Every loan runs the full gold ruleset automatically — real, citation-backed
          verdicts the moment a loan lands in the queue.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {(
          [
            ["PASS", "Pass", "text-emerald-600"],
            ["FAILED", "Failed", "text-rose-600"],
            ["NEEDS_REVIEW", "Needs Review", "text-amber-600"],
            ["RESOLVED", "Resolved", "text-blue-600"],
          ] as const
        ).map(([key, label, color]) => {
          const active = statusFilter === key;
          return (
            <button
              key={key}
              type="button"
              onClick={() => setStatusFilter((prev) => (prev === key ? null : key))}
              className={`rounded-xl border p-4 text-left shadow-[var(--shadow-panel)] transition ${
                active ? "border-blue-400 bg-blue-50/40 ring-2 ring-blue-100" : "border-slate-200 bg-white hover:border-slate-300"
              }`}
            >
              <div className="text-xs font-medium text-slate-500">{label}</div>
              <div className={`mt-1 font-mono text-2xl font-bold ${color}`}>{counts[key]}</div>
            </button>
          );
        })}
      </div>
      {statusFilter && (
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <span>
            Filtered to <span className="font-semibold text-slate-700">{statusFilter.replace("_", " ")}</span> ·{" "}
            {filteredLoans.length} loan{filteredLoans.length === 1 ? "" : "s"}
          </span>
          <button
            type="button"
            onClick={() => setStatusFilter(null)}
            className="font-semibold text-blue-600 hover:underline"
          >
            Clear filter
          </button>
        </div>
      )}

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
            {pagedLoans.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-xs text-slate-400">
                  No loans match the current filter.
                </td>
              </tr>
            ) : (
              pagedLoans.map((loan, i) => (
                <LoanQueueRow
                  key={loan.loanId}
                  loan={loan}
                  index={i}
                  routeName={routeName(loan.routeId)}
                  onOpen={() => onOpenLoan(loan.loanId)}
                />
              ))
            )}
          </tbody>
        </table>
        {filteredLoans.length > PAGE_SIZE && (
          <div className="flex items-center justify-between border-t border-slate-100 px-4 py-3 text-[11px] text-slate-500">
            <span>
              Showing {currentPage * PAGE_SIZE + 1}–{Math.min((currentPage + 1) * PAGE_SIZE, filteredLoans.length)} of{" "}
              {filteredLoans.length}
            </span>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={currentPage === 0}
                className="rounded-lg border border-slate-200 px-2.5 py-1 font-semibold text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
              >
                Previous
              </button>
              <span className="font-mono">
                Page {currentPage + 1} of {totalPages}
              </span>
              <button
                type="button"
                onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                disabled={currentPage >= totalPages - 1}
                className="rounded-lg border border-slate-200 px-2.5 py-1 font-semibold text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

interface LoanQueueRowProps {
  loan: Loan;
  index: number;
  routeName: string;
  onOpen: () => void;
}

// A separate component (not inlined in the .map() above) because it must call
// useDataSource() -- a hook can't be called conditionally/per-iteration inside a
// .map() callback, only at a component's own top level (Rules of Hooks).
function LoanQueueRow({ loan, index, routeName, onOpen }: LoanQueueRowProps) {
  const dataSource = useDataSource();
  const displayState = deriveLoanDisplayState(loan, dataSource);
  // FR-006a / SC-006: the Loan Queue grid never renders an error badge -- that state is
  // surfaced in the loan detail view / the fetch trigger's own inline message instead.
  // Clamp "error" down to the same neutral look as "not yet fetched" for this grid only.
  const gridDisplayState: LoanDisplayState =
    displayState.kind === "error" ? { kind: "not_fetched" } : displayState;

  return (
    <motion.tr
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.03 }}
      className="group cursor-pointer hover:bg-slate-50/70"
      onClick={onOpen}
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
          <span className="max-w-[200px] truncate">{routeName}</span>
        </div>
      </td>
      <td className="px-4 py-3">
        <LoanStatusBadge display={gridDisplayState} />
      </td>
      <td className="px-4 py-3 text-right">
        <span className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 opacity-0 transition-opacity group-hover:opacity-100">
          Open <ArrowRight className="h-3 w-3" />
        </span>
      </td>
    </motion.tr>
  );
}
