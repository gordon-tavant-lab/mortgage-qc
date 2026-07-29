import { useState } from "react";
import {
  FileSpreadsheet,
  ArrowRight,
  Code2,
  MessageSquareText,
  AlertTriangle,
  ShieldCheck,
  CheckCircle2,
} from "lucide-react";
import { MOCK_CHECKS, MOCK_SIGNED_RULESET } from "../data/mockData";
import { SampleDataBanner } from "./SampleDataBanner";
import { SeverityBadge } from "./StatusBadge";
import { SourceCitation } from "./SourceCitation";
import { compiledGateSummary } from "../lib/checkFormat";

export function ImportAndSignView() {
  const [editCounts, setEditCounts] = useState<Record<string, number>>({});
  const [signed, setSigned] = useState(false);

  const totalEdits = Object.values(editCounts).reduce((a, b) => a + b, 0);
  const isSignOffTheater = totalEdits === 0;

  const bumpEdit = (checkId: string) =>
    setEditCounts((prev) => ({ ...prev, [checkId]: (prev[checkId] ?? 0) + 1 }));

  return (
    <div className="space-y-6 pb-12">
      <SampleDataBanner />

      <div>
        <h2 className="font-display text-xl font-bold text-slate-900">Author — Import &amp; Sign</h2>
        <p className="mt-1 max-w-2xl text-sm text-slate-500">
          The AMQ workbook is already a structured authoring source. Import what the SME already
          maintains, review exactly what the compiler made of it, and sign. No free-text rule
          authoring in this surface — that is deliberate, see{" "}
          <span className="font-mono text-xs">output/AUTHORING-UX-DECISION.md</span>.
        </p>
      </div>

      <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-[var(--shadow-panel)]">
        <div className="rounded-lg border border-blue-100 bg-blue-50 p-2 text-blue-600">
          <FileSpreadsheet className="h-5 w-5" />
        </div>
        <div className="flex-1">
          <div className="text-sm font-bold text-slate-900">AMQ_Post_Closing_Workbook_2026.xlsx</div>
          <div className="text-xs text-slate-500">
            {MOCK_CHECKS.length} conditions parsed for this route · imported 2026-07-20
          </div>
        </div>
        <span className="rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-[11px] font-bold text-emerald-700">
          Imported
        </span>
      </div>

      <div>
        <h3 className="text-sm font-bold text-slate-900">Diff-and-Sign Review</h3>
        <p className="mt-0.5 text-xs text-slate-500">
          Source condition ↔ compiled gate ↔ plain-English restatement, side by side, per rule.
        </p>
      </div>

      <div className="space-y-3">
        {MOCK_CHECKS.map((check) => (
          <div key={check.id} className="rounded-xl border border-slate-200 bg-white p-4 shadow-[var(--shadow-panel)]">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-slate-900">{check.name}</span>
                <SeverityBadge severity={check.severity} />
              </div>
              <label htmlFor={`sme-corrected-${check.id}`} className="flex items-center gap-1.5 text-[11px] text-slate-400">
                <input
                  id={`sme-corrected-${check.id}`}
                  name={`sme-corrected-${check.id}`}
                  type="checkbox"
                  className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                  onChange={() => bumpEdit(check.id)}
                />
                Mark as SME-corrected
              </label>
            </div>

            <div className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-3">
              <div>
                <div className="mb-1 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wide text-slate-400">
                  <FileSpreadsheet className="h-3 w-3" /> Source Condition (AMQ row)
                </div>
                <div className="rounded-lg border border-slate-100 bg-slate-50 p-2.5 text-[11px] leading-relaxed text-slate-600">
                  {check.sourceCondition}
                </div>
                <div className="mt-1.5">
                  <SourceCitation check={check} compact />
                </div>
              </div>
              <div>
                <div className="mb-1 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wide text-slate-400">
                  <Code2 className="h-3 w-3" /> Compiled Gate
                </div>
                <div className="rounded-lg border border-slate-800 bg-slate-900 p-2.5 font-mono text-[11px] text-slate-200">
                  {compiledGateSummary(check)}
                </div>
              </div>
              <div>
                <div className="mb-1 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wide text-slate-400">
                  <MessageSquareText className="h-3 w-3" /> Plain-English Restatement
                </div>
                <div className="rounded-lg border border-blue-100 bg-blue-50 p-2.5 text-[11px] leading-relaxed text-blue-900">
                  {check.plainEnglish}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="space-y-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-[var(--shadow-panel)]">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3 text-xs text-slate-600">
            <span>
              SME Edit Distance:{" "}
              <strong className={`font-mono ${isSignOffTheater ? "font-bold text-amber-600" : "text-emerald-600"}`}>
                {totalEdits} human edits
              </strong>
            </span>
            {isSignOffTheater && (
              <span className="flex items-center gap-1 rounded border border-amber-200 bg-amber-50 px-2 py-0.5 text-[11px] text-amber-700">
                <AlertTriangle className="h-3 w-3" />
                Sign-off theater warning: zero SME edits recorded
              </span>
            )}
          </div>

          {signed ? (
            <span className="flex items-center gap-1.5 text-xs font-semibold text-emerald-600">
              <CheckCircle2 className="h-4 w-4" />
              Signed by {MOCK_SIGNED_RULESET.signedBy}
            </span>
          ) : (
            <button
              onClick={() => setSigned(true)}
              className="flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-xs font-semibold text-white shadow-sm transition hover:bg-blue-700"
            >
              <ShieldCheck className="h-4 w-4" />
              Sign &amp; Pin Version
            </button>
          )}
        </div>
        <p className="border-t border-slate-100 pt-3 text-[11px] text-slate-400">
          Signing binds to this human-corrected artifact. The signed artifact's SHA-256 hash is what
          executes deterministically against every loan — never re-derived at runtime.
        </p>
      </div>

      <div className="flex justify-end">
        <button className="flex items-center gap-2 text-xs font-semibold text-blue-600 hover:text-blue-700">
          Continue to Routes <ArrowRight className="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  );
}
