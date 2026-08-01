import { useState } from "react";
import { ChevronDown, Radio } from "lucide-react";
import { useDataSource } from "../lib/dataSourceContext";
import { RetrievedDocumentViewer } from "./RetrievedDocumentViewer";

// LiveApplicationPanel — shown on LoanDetail once a live application has been pulled.
// Summarizes the raw Touchless `application` payload (loanSummary + documents[]) and lets the
// reviewer open the REAL retrieved document/OCR content per documentId. This is source
// content, not a QC verdict -- no pass/fail/checkmark visual language here (compliance-
// review.md's UI-presentation note). Additive to, not a retrofit of, the existing mock
// citation UI (plan.md §4).
interface LiveApplicationPanelProps {
  applicationId: string;
}

interface DocumentSummary {
  documentId: string;
  documentType?: string;
  source?: string;
}

function asRecord(value: unknown): Record<string, unknown> | undefined {
  return value && typeof value === "object" ? (value as Record<string, unknown>) : undefined;
}

function extractLoanSummary(application: unknown): [string, string | number | boolean][] {
  const summary = asRecord(asRecord(application)?.loanSummary);
  if (!summary) return [];
  return Object.entries(summary).filter(
    (entry): entry is [string, string | number | boolean] =>
      typeof entry[1] === "string" || typeof entry[1] === "number" || typeof entry[1] === "boolean",
  );
}

function extractDocuments(application: unknown): DocumentSummary[] {
  const rawDocuments = asRecord(application)?.documents;
  if (!Array.isArray(rawDocuments)) return [];

  const summaries: DocumentSummary[] = [];
  for (const entry of rawDocuments) {
    const doc = asRecord(entry);
    if (!doc) continue;
    const documentId = doc.documentId ?? doc.id;
    if (typeof documentId !== "string") continue;
    const documentType = doc.documentType ?? doc.type ?? doc.name;
    const source = doc.source ?? doc.sourceType;
    summaries.push({
      documentId,
      documentType: typeof documentType === "string" ? documentType : undefined,
      source: typeof source === "string" ? source : undefined,
    });
  }
  return summaries;
}

function formatFieldLabel(key: string): string {
  return key
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/^./, (c) => c.toUpperCase());
}

function formatFetchedAt(iso: string): string {
  const parsed = new Date(iso);
  return Number.isNaN(parsed.getTime()) ? iso : parsed.toLocaleTimeString();
}

export function LiveApplicationPanel({ applicationId }: LiveApplicationPanelProps) {
  const { pulledApplications } = useDataSource();
  const [documentsExpanded, setDocumentsExpanded] = useState(false);
  const [viewingDocumentId, setViewingDocumentId] = useState<string | null>(null);

  const pulled = pulledApplications.get(applicationId);
  if (!pulled) return null;

  const summaryFields = extractLoanSummary(pulled.application);
  const documents = extractDocuments(pulled.application);

  return (
    <div className="space-y-3 rounded-xl border border-blue-100 bg-blue-50/40 p-4">
      <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-blue-700">
        <Radio className="h-3.5 w-3.5" />
        Live Touchless Application — pulled {formatFetchedAt(pulled.fetchedAt)}
      </div>

      {summaryFields.length > 0 && (
        <dl className="grid grid-cols-2 gap-x-6 gap-y-1.5 text-xs sm:grid-cols-3">
          {summaryFields.map(([key, value]) => (
            <div key={key}>
              <dt className="text-slate-400">{formatFieldLabel(key)}</dt>
              <dd className="font-medium text-slate-800">{String(value)}</dd>
            </div>
          ))}
        </dl>
      )}

      <div>
        <button
          type="button"
          onClick={() => setDocumentsExpanded((v) => !v)}
          className="flex items-center gap-1.5 text-xs font-semibold text-blue-700 hover:text-blue-900"
        >
          <ChevronDown
            className={`h-3.5 w-3.5 transition-transform ${documentsExpanded ? "rotate-180" : ""}`}
          />
          Documents ({documents.length})
        </button>

        {documentsExpanded && (
          <div className="mt-2 max-h-72 overflow-y-auto rounded-lg border border-slate-200 bg-white">
            {documents.length === 0 ? (
              <div className="p-3 text-xs text-slate-400">No documents on this application.</div>
            ) : (
              <table className="w-full text-left text-xs">
                <thead className="sticky top-0 bg-slate-50 text-slate-400">
                  <tr>
                    <th className="px-3 py-1.5 font-semibold">Type</th>
                    <th className="px-3 py-1.5 font-semibold">Source</th>
                    <th className="px-3 py-1.5 font-semibold">Document ID</th>
                    <th className="px-3 py-1.5" />
                  </tr>
                </thead>
                <tbody>
                  {documents.map((doc) => (
                    <tr key={doc.documentId} className="border-t border-slate-100">
                      <td className="px-3 py-1.5 text-slate-700">{doc.documentType ?? "Unclassified"}</td>
                      <td className="px-3 py-1.5 text-slate-500">{doc.source ?? "—"}</td>
                      <td className="px-3 py-1.5 font-mono text-slate-400">{doc.documentId}</td>
                      <td className="px-3 py-1.5 text-right">
                        <button
                          type="button"
                          onClick={() => setViewingDocumentId(doc.documentId)}
                          className="rounded border border-blue-200 bg-blue-50 px-2 py-0.5 text-[11px] font-semibold text-blue-700 hover:bg-blue-100"
                        >
                          View Document
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
      </div>

      {viewingDocumentId && (
        <RetrievedDocumentViewer
          documentId={viewingDocumentId}
          onClose={() => setViewingDocumentId(null)}
        />
      )}
    </div>
  );
}
