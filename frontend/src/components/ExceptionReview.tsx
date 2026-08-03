import { useEffect, useState } from "react";
import { FileText, ChevronRight, ArrowRight, XCircle, CornerUpRight, PenLine, CheckCircle2, AlertCircle } from "lucide-react";
import { MOCK_FINDINGS, MOCK_LOANS } from "../data/mockData";
import { SeverityBadge } from "./StatusBadge";
import { RetrievedDocumentViewer } from "./RetrievedDocumentViewer";
import { useDataSource } from "../lib/dataSourceContext";
import { findingsFromRunResult } from "../lib/auditFindings";
import type { Finding } from "../lib/types";

const MITIGATION_STYLES: Record<Finding["mitigation"], string> = {
  UNRESOLVED: "bg-slate-100 text-slate-600 border-slate-200",
  OVERRIDDEN: "bg-blue-50 text-blue-700 border-blue-200",
  ESCALATED: "bg-amber-50 text-amber-700 border-amber-200",
  SYSTEM_CORRECTED: "bg-emerald-50 text-emerald-700 border-emerald-200",
};

interface ExceptionReviewProps {
  loanId: string;
}

export function ExceptionReview({ loanId }: ExceptionReviewProps) {
  const loan = MOCK_LOANS.find((l) => l.loanId === loanId);
  const { auditRuns } = useDataSource();
  const audit = loan?.applicationId ? auditRuns.get(loan.applicationId) : undefined;

  // spec021 US5 (FR-013): once a real audit run has resolved for this loan, ITS findings
  // are the only real, engine-computed exceptions -- mock findings remain exactly as
  // before for every other loan/state (before a run, or while one is in flight).
  const [findings, setFindings] = useState<Finding[]>(() =>
    audit?.status === "resolved"
      ? findingsFromRunResult(loanId, audit.result.runResult)
      : MOCK_FINDINGS.filter((f) => f.loanId === loanId),
  );
  const [activeCitation, setActiveCitation] = useState<Finding["citation"] | null>(null);
  const [viewingDocumentId, setViewingDocumentId] = useState<string | null>(null);
  const [index, setIndex] = useState(0);

  // Re-derive if the real audit run resolves AFTER this component already mounted (e.g.
  // the user is already sitting on the Exceptions tab while the auto-triggered run
  // completes in the background).
  useEffect(() => {
    if (audit?.status === "resolved") {
      setFindings(findingsFromRunResult(loanId, audit.result.runResult));
      setIndex(0);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [audit?.status, loanId]);

  const current = findings[index];
  const isLast = index === findings.length - 1;

  const mitigate = (mitigation: Finding["mitigation"]) => {
    setFindings((prev) => prev.map((f, i) => (i === index ? { ...f, mitigation } : f)));
  };

  const clearAndNext = () => {
    if (!isLast) setIndex((i) => i + 1);
  };

  if (findings.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-slate-200 bg-white py-16 text-center">
        <CheckCircle2 className="h-8 w-8 text-emerald-500" />
        <p className="text-sm font-semibold text-slate-700">No exceptions for this loan.</p>
        <p className="max-w-xs text-xs text-slate-500">
          Every check either passed or was auto-cleared — nothing needs human judgment here.
        </p>
      </div>
    );
  }

  if (!current) return null;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="space-y-2 lg:col-span-1">
          {findings.map((f, i) => (
            <button
              key={f.id}
              onClick={() => setIndex(i)}
              className={`w-full rounded-lg border p-3 text-left transition ${
                i === index ? "border-blue-300 bg-blue-50/50" : "border-slate-200 bg-white hover:bg-slate-50"
              }`}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="truncate text-xs font-semibold text-slate-900">{f.checkName}</span>
                <SeverityBadge severity={f.severity} />
              </div>
              <span className={`mt-1.5 inline-block rounded-full border px-2 py-0.5 text-[10px] font-bold ${MITIGATION_STYLES[f.mitigation]}`}>
                {f.mitigation}
              </span>
            </button>
          ))}
        </div>

        <div className="space-y-4 rounded-xl border border-slate-200 bg-white p-5 shadow-[var(--shadow-panel)] lg:col-span-2">
          <div className="flex items-start justify-between gap-3 border-b border-slate-100 pb-4">
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold text-slate-900">{current.checkName}</h3>
                <SeverityBadge severity={current.severity} />
              </div>
              <p className="mt-1.5 text-xs leading-relaxed text-slate-600">{current.message}</p>
            </div>
            <span className="shrink-0 font-mono text-[11px] text-slate-400">
              {index + 1} of {findings.length}
            </span>
          </div>

          {current.citation && (
            <div>
              <div className="mb-1.5 text-[10px] font-semibold uppercase tracking-wide text-slate-400">Evidence</div>
              {current.citation.documentIds ? (
                current.citation.documentIds.length > 0 ? (
                  // Real (Touchless-sourced) exception -- one clickable link per matched
                  // document, never collapsed to just the first (spec021 FR-013). Each
                  // opens the actual RetrievedDocumentViewer (020), not a placeholder.
                  <div className="flex flex-wrap gap-2">
                    {current.citation.documentIds.map((docId, i) => (
                      <button
                        key={docId}
                        onClick={() => setViewingDocumentId(docId)}
                        className="flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-medium text-slate-700 transition hover:border-blue-300 hover:bg-blue-50/50"
                      >
                        <FileText className="h-3.5 w-3.5 text-blue-600" />
                        {current.citation!.doc}
                        {current.citation!.documentIds!.length > 1 && ` (${i + 1} of ${current.citation!.documentIds!.length})`}
                        <ChevronRight className="h-3.5 w-3.5 text-slate-400" />
                      </button>
                    ))}
                  </div>
                ) : (
                  // Shouldn't arise for anything actually compiled in (research.md Item 2's
                  // filtering), but stated honestly rather than a dead/broken link.
                  <div className="flex items-center gap-2 rounded-lg border border-dashed border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-400">
                    <AlertCircle className="h-3.5 w-3.5 shrink-0" />
                    No source document identified for this citation.
                  </div>
                )
              ) : (
                // Mock finding -- existing placeholder-modal behavior, unaffected.
                <button
                  onClick={() => setActiveCitation(current.citation!)}
                  className="flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-medium text-slate-700 transition hover:border-blue-300 hover:bg-blue-50/50"
                >
                  <FileText className="h-3.5 w-3.5 text-blue-600" />
                  {current.citation.doc}, Page {current.citation.page}
                  {current.citation.segment && `, ${current.citation.segment}`}
                  <ChevronRight className="h-3.5 w-3.5 text-slate-400" />
                </button>
              )}
            </div>
          )}

          {current.notes && (
            <div className="rounded-lg border border-slate-100 bg-slate-50 p-3 text-xs italic text-slate-500">
              "{current.notes}"
            </div>
          )}

          <div className="flex flex-wrap items-center gap-2 border-t border-slate-100 pt-4">
            <button
              onClick={() => mitigate("OVERRIDDEN")}
              className="flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"
            >
              <PenLine className="h-3.5 w-3.5" /> Override
            </button>
            <button
              onClick={() => mitigate("ESCALATED")}
              className="flex items-center gap-1.5 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs font-semibold text-amber-700 hover:bg-amber-100"
            >
              <CornerUpRight className="h-3.5 w-3.5" /> Escalate
            </button>
            <button
              onClick={() => mitigate("SYSTEM_CORRECTED")}
              className="flex items-center gap-1.5 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs font-semibold text-emerald-700 hover:bg-emerald-100"
            >
              <XCircle className="h-3.5 w-3.5" /> Mark System-Corrected
            </button>
            <button
              onClick={clearAndNext}
              disabled={isLast}
              className="ml-auto flex items-center gap-1.5 rounded-lg bg-blue-600 px-4 py-2 text-xs font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:opacity-40"
            >
              Clear &amp; Next Exception <ArrowRight className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </div>

      {activeCitation && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 p-4 backdrop-blur-sm"
          onClick={() => setActiveCitation(null)}
        >
          <div
            className="w-full max-w-lg rounded-xl border border-slate-200 bg-white p-5 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
              <FileText className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-bold text-slate-900">{activeCitation.doc}</span>
              <span className="text-xs text-slate-400">Page {activeCitation.page}</span>
            </div>
            <div className="mt-4 flex h-64 items-center justify-center rounded-lg border border-dashed border-slate-200 bg-slate-50 text-xs text-slate-400">
              PDF page render placeholder — deep-links to {activeCitation.doc}#page={activeCitation.page}
            </div>
            <button
              onClick={() => setActiveCitation(null)}
              className="mt-4 w-full rounded-lg border border-slate-200 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-50"
            >
              Close
            </button>
          </div>
        </div>
      )}

      {viewingDocumentId && (
        <RetrievedDocumentViewer
          documentId={viewingDocumentId}
          onClose={() => setViewingDocumentId(null)}
        />
      )}
    </div>
  );
}
