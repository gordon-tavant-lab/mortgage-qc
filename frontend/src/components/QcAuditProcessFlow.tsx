import { ArrowRight, Database, FileCode, FileText, Radio } from "lucide-react";

// QcAuditProcessFlow — visual replacement for the earlier 3 plain, unconnected cards.
// Same real content (the 3 sequential Touchless retrieval calls, confirmed on the
// 2026-08-01 Touchless call), now shown as a connected process: Touchless API -> the 3
// real GET calls -> feeds the deterministic engine. Purely presentational -- no new
// claims beyond what InspectSources.tsx's own copy already states.
const STEPS = [
  {
    icon: Radio,
    label: "Touchless API",
    sub: "Real loan, real documents",
    kind: "source" as const,
  },
  {
    icon: FileText,
    label: "1. Application Results",
    sub: "GET status + summary metadata for the whole application",
    kind: "step" as const,
  },
  {
    icon: Database,
    label: "2. Indexed Documents",
    sub: "GET the list of documents Touchless has indexed",
    kind: "step" as const,
  },
  {
    icon: FileCode,
    label: "3. Extracted Data",
    sub: "GET the structured fields extracted from each document",
    kind: "step" as const,
  },
  {
    icon: ArrowRight,
    label: "Deterministic Engine",
    sub: "Compiles the gold ruleset, runs every check",
    kind: "sink" as const,
  },
];

export function QcAuditProcessFlow() {
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white p-5 shadow-[var(--shadow-panel)]">
      <div className="flex min-w-max items-center">
        {STEPS.map((step, i) => (
          <div key={step.label} className="flex items-center">
            {i > 0 && (
              <ArrowRight className="mx-1 h-4 w-4 shrink-0 text-blue-300 sm:mx-2" />
            )}
            <div
              className={`flex w-40 flex-col items-center gap-1.5 rounded-xl border p-3 text-center sm:w-44 ${
                step.kind === "step"
                  ? "border-blue-200 bg-blue-50/60"
                  : "border-slate-200 bg-slate-50"
              }`}
            >
              <div
                className={`rounded-lg p-2 ${
                  step.kind === "step" ? "bg-blue-100 text-blue-700" : "bg-slate-200 text-slate-600"
                }`}
              >
                <step.icon className="h-4 w-4" />
              </div>
              <div className="text-xs font-bold text-slate-900">{step.label}</div>
              <div className="text-[11px] leading-snug text-slate-500">{step.sub}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
