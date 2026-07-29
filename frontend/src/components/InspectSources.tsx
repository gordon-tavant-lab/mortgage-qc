import { FileText, Database, FileCode, CheckCircle2, AlertTriangle } from "lucide-react";
import { MOCK_SOURCE_ALIGNMENT, MOCK_LOANS } from "../data/mockData";
import { SampleDataBanner } from "./SampleDataBanner";

export function InspectSources() {
  const misalignedCount = MOCK_SOURCE_ALIGNMENT.filter((r) => !r.aligned).length;

  return (
    <div className="space-y-6 pb-12">
      <SampleDataBanner />

      <div>
        <h2 className="font-display text-xl font-bold text-slate-900">Inspect Sources</h2>
        <p className="mt-1 text-sm text-slate-500">
          A sanity check before you trust the run — three genuinely independent origins, reconciled
          field by field. Reviewing <span className="font-mono font-semibold">{MOCK_LOANS[0].loanId}</span>.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        {[
          { icon: FileText, label: "Closing Document", sub: "Source of truth — title company, post-closing" },
          { icon: Database, label: "LOS Export", sub: "Loan Origination System, via connector" },
          { icon: FileCode, label: "MISMO 3.4 XML", sub: "Title company or LOS export" },
        ].map((s) => (
          <div key={s.label} className="flex items-start gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-[var(--shadow-panel)]">
            <div className="rounded-lg border border-blue-100 bg-blue-50 p-2 text-blue-600">
              <s.icon className="h-4 w-4" />
            </div>
            <div>
              <div className="text-sm font-bold text-slate-900">{s.label}</div>
              <div className="mt-0.5 text-xs text-slate-500">{s.sub}</div>
            </div>
          </div>
        ))}
      </div>

      {misalignedCount > 0 && (
        <div className="flex items-center gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs font-medium text-amber-800">
          <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
          {misalignedCount} field{misalignedCount > 1 ? "s" : ""} disagree across sources — these will
          surface as informational reconciliation flags when the engine runs, not automatic failures.
        </div>
      )}

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-[var(--shadow-panel)]">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50 text-xs font-semibold uppercase tracking-wide text-slate-500">
              <th className="px-4 py-3">Field</th>
              <th className="px-4 py-3">Closing Doc</th>
              <th className="px-4 py-3">LOS Export</th>
              <th className="px-4 py-3">MISMO XML</th>
              <th className="px-4 py-3">Alignment</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {MOCK_SOURCE_ALIGNMENT.map((row) => (
              <tr key={row.fieldId} className={row.aligned ? "" : "bg-amber-50/40"}>
                <td className="px-4 py-3 text-xs font-semibold text-slate-900">{row.fieldName}</td>
                <td className="px-4 py-3 font-mono text-xs text-slate-700">{row.docValue ?? "—"}</td>
                <td className="px-4 py-3 font-mono text-xs text-slate-700">{row.losValue ?? "—"}</td>
                <td className="px-4 py-3 font-mono text-xs text-slate-700">{row.mismoValue ?? "—"}</td>
                <td className="px-4 py-3">
                  {row.aligned ? (
                    <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-600">
                      <span className="h-2 w-2 rounded-full bg-emerald-500" />
                      Aligned
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-amber-600">
                      <span className="h-2 w-2 animate-pulse-dot rounded-full bg-amber-500" />
                      Misaligned
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex justify-end">
        <button className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-xs font-semibold text-white shadow-sm transition hover:bg-blue-700">
          <CheckCircle2 className="h-4 w-4" />
          Proceed to Apply
        </button>
      </div>
    </div>
  );
}
