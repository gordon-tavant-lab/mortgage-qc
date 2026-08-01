import { useState } from "react";
import { ArrowLeft, ScanEye, PlayCircle, ClipboardCheck, MapPin } from "lucide-react";
import { MOCK_LOANS, MOCK_ROUTES, MOCK_FINDINGS } from "../data/mockData";
import { DataSourceBanner } from "./DataSourceBanner";
import { LoanStatusBadge } from "./StatusBadge";
import { InspectSources } from "./InspectSources";
import { ApplyView } from "./ApplyView";
import { ExceptionReview } from "./ExceptionReview";
import { PullApplicationButton } from "./PullApplicationButton";
import { LiveApplicationPanel } from "./LiveApplicationPanel";
import { useDataSource } from "../lib/dataSourceContext";
import type { LoanDetailTab } from "../lib/nav";

interface LoanDetailProps {
  loanId: string;
  initialTab: LoanDetailTab;
  onBack: () => void;
}

export function LoanDetail({ loanId, initialTab, onBack }: LoanDetailProps) {
  const [tab, setTab] = useState<LoanDetailTab>(initialTab);
  const { mode } = useDataSource();
  const loan = MOCK_LOANS.find((l) => l.loanId === loanId) ?? MOCK_LOANS[0];
  const route = MOCK_ROUTES.find((r) => r.id === loan.routeId);
  const unresolvedCount = MOCK_FINDINGS.filter(
    (f) => f.loanId === loanId && f.mitigation === "UNRESOLVED"
  ).length;

  const TABS: { id: LoanDetailTab; label: string; icon: typeof ScanEye; badge?: number }[] = [
    { id: "inspect", label: "Inspect Sources", icon: ScanEye },
    { id: "apply", label: "Apply", icon: PlayCircle },
    { id: "exceptions", label: "Exceptions", icon: ClipboardCheck, badge: unresolvedCount },
  ];

  return (
    <div className="space-y-6 pb-12">
      <DataSourceBanner />

      <div>
        <button
          onClick={onBack}
          className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-700"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          All Loans
        </button>

        <div className="mt-3 flex flex-wrap items-start justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="font-mono text-lg font-bold text-slate-900">{loan.loanId}</h2>
              <LoanStatusBadge status={loan.status} />
            </div>
            <div className="mt-0.5 text-sm text-slate-600">
              {loan.borrowerName} · {loan.loanType}
            </div>
            <div className="mt-1 flex items-center gap-1.5 text-xs text-slate-400">
              <MapPin className="h-3 w-3" />
              {loan.propertyAddress}
            </div>
          </div>
          <div className="text-right text-xs text-slate-500">
            <div className="font-semibold text-slate-700">{route?.name}</div>
            <div className="mt-0.5 text-slate-400">{route?.description}</div>
          </div>
        </div>
      </div>

      {loan.applicationId && (
        <div className="space-y-3">
          <PullApplicationButton applicationId={loan.applicationId} />
          {mode === "live" && <LiveApplicationPanel applicationId={loan.applicationId} />}
        </div>
      )}

      <div className="flex items-center gap-1 rounded-xl border border-slate-200 bg-white p-1 shadow-[var(--shadow-panel)]">
        {TABS.map((t) => {
          const isActive = tab === t.id;
          const Icon = t.icon;
          return (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`flex items-center gap-1.5 rounded-lg px-3.5 py-2 text-xs font-semibold transition-all ${
                isActive ? "bg-blue-600 text-white shadow-sm" : "text-slate-500 hover:bg-slate-50 hover:text-slate-800"
              }`}
            >
              <Icon className="h-3.5 w-3.5" />
              {t.label}
              {!!t.badge && (
                <span
                  className={`flex h-4 w-4 items-center justify-center rounded-full text-[10px] font-bold ${
                    isActive ? "bg-white/25 text-white" : "bg-rose-500 text-white"
                  }`}
                >
                  {t.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {tab === "inspect" && <InspectSources />}
      {tab === "apply" && <ApplyView />}
      {tab === "exceptions" && <ExceptionReview loanId={loanId} />}
    </div>
  );
}
