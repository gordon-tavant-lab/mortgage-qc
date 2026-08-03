import { useEffect } from "react";
import { Bug, Clock, FileQuestion, FileWarning, SearchX, ServerCrash, ShieldAlert, X } from "lucide-react";
import { useDataSource } from "../lib/dataSourceContext";
import type { ErrorCode } from "../lib/touchlessApi";

// RetrievedDocumentViewer — FR-006/FR-008/FR-009/SC-002. A modal that shows the REAL retrieved
// document (Blob -> ObjectURL -> native <iframe> PDF render, per plan.md §2.2 -- no pdf.js) plus
// its OCR field table. This is source content, not a QC verdict -- no pass/fail/checkmark visual
// language anywhere in this component (compliance-review.md's UI-presentation note).
interface RetrievedDocumentViewerProps {
  documentId: string;
  onClose: () => void;
}

const ERROR_COPY: Record<ErrorCode, { icon: typeof FileWarning; title: string }> = {
  AUTH_FAILURE: { icon: ShieldAlert, title: "Authentication Failed" },
  NOT_FOUND: { icon: SearchX, title: "Document Not Found" },
  TIMEOUT: { icon: Clock, title: "Request Timed Out" },
  UNEXPECTED_CONTENT_TYPE: { icon: FileQuestion, title: "Unexpected Content" },
  UPSTREAM_ERROR: { icon: ServerCrash, title: "Touchless Error" },
  INVALID_INPUT: { icon: FileWarning, title: "Invalid Request" },
  PROXY_ERROR: { icon: Bug, title: "Proxy Error" },
};

export function RetrievedDocumentViewer({ documentId, onClose }: RetrievedDocumentViewerProps) {
  const { retrievedDocuments, documentError, getOrFetchDocument } = useDataSource();
  const retrieved = retrievedDocuments.get(documentId);
  const error = documentError(documentId);

  useEffect(() => {
    // Fetch-once, no automatic retry (per FR-005's discipline extended to documents): only
    // fetch when there's neither a cached result nor an existing error to explain the absence.
    if (!retrievedDocuments.has(documentId) && !documentError(documentId)) {
      void getOrFetchDocument(documentId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [documentId]);

  const errorCopy = error ? ERROR_COPY[error.code as ErrorCode] : undefined;
  const ErrorIcon = errorCopy?.icon ?? FileWarning;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-6">
      <div className="flex max-h-[85vh] w-full max-w-4xl flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-150 px-4 py-3">
          <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Retrieved Document — Touchless Live Content
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700"
            aria-label="Close"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {error && (
            <div
              data-testid={`document-error-${error.code}`}
              className="flex items-start gap-2 rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800"
            >
              <ErrorIcon className="mt-0.5 h-4 w-4 shrink-0" />
              <div>
                <div className="font-semibold">{errorCopy?.title ?? "Error"}</div>
                <div className="mt-0.5 text-rose-700">{error.message}</div>
              </div>
            </div>
          )}

          {!error && !retrieved && (
            <div className="flex items-center justify-center py-12 text-sm text-slate-400">
              Retrieving document from Touchless…
            </div>
          )}

          {!error && retrieved && (
            <div className="space-y-4">
              <div className="overflow-hidden rounded-lg border border-slate-200">
                <iframe
                  title={`Retrieved document ${documentId}`}
                  src={retrieved.pdfObjectUrl}
                  className="h-[420px] w-full"
                />
              </div>

              <div>
                <div className="mb-1.5 text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                  Extracted Fields ({retrieved.ocrFields.length})
                </div>
                {retrieved.ocrFields.length === 0 ? (
                  <div className="text-xs text-slate-400">No fields extracted for this document.</div>
                ) : (
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="text-slate-400">
                        <th className="pb-1 font-semibold">Field</th>
                        <th className="pb-1 font-semibold">Value</th>
                        <th className="pb-1 font-semibold">Confidence</th>
                      </tr>
                    </thead>
                    <tbody>
                      {retrieved.ocrFields.map((field) => (
                        <tr key={field.name} className="border-t border-slate-100">
                          <td className="py-1 font-mono text-slate-600">{field.name}</td>
                          <td className="py-1 text-slate-800">{field.value}</td>
                          {/* Confidence shown exactly as returned -- never clamped/normalized/
                              labeled "invalid" for values outside [0,100] (CLAUDE.md live-test
                              finding: values up to 102.0 are real and must pass through as-is).
                              Some document types' real OCR response omits confidence entirely
                              (backend's normalizeOcrResponse() docstring) -- shown honestly as
                              "—", never fabricated. */}
                          <td className="py-1 text-slate-500">{field.confidence ?? "—"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
