// auditFindings.ts — 021-touchless-audit-run (US5, FR-013): derives real, engine-computed
// Finding[] entries from a real audit run's RunResult, for ExceptionReview.tsx to render
// alongside (or in place of) the existing mock findings. Mirrors p0/qc_engine/engine.py's
// own `qc_failures` property exactly (phase === "QC" && status in (FAIL, WARNING)) --
// the ONLY pass/fail axis; RECONCILE-phase FLAGs are informational, not exceptions.
import type { Finding, Severity } from "./types";

// Mirrors p0/qc_engine/engine.py's CheckResult.to_dict() shape exactly (snake_case field
// names, camelCase citation keys from DocCitation.to_dict()).
interface RealCitation {
  docName: string;
  pageNum: number;
  segmentSnippet: string;
  documentIds?: string[];
}

interface RealCheckResult {
  check_id: string;
  check_name: string;
  severity: Severity;
  status: "PASS" | "FAIL" | "WARNING" | "FLAG" | "NEEDS_REVIEW" | "NOT_APPLICABLE";
  phase: string;
  message: string;
  citation: RealCitation | null;
}

interface RealRunResult {
  results: RealCheckResult[];
}

function isRealRunResult(value: unknown): value is RealRunResult {
  return (
    typeof value === "object" &&
    value !== null &&
    Array.isArray((value as { results?: unknown }).results)
  );
}

/** Real QC failures only (RunResult.qc_failures' own definition) -- never RECONCILE flags. */
export function findingsFromRunResult(loanId: string, runResult: unknown): Finding[] {
  if (!isRealRunResult(runResult)) return [];

  return runResult.results
    .filter((r) => r.phase === "QC" && (r.status === "FAIL" || r.status === "WARNING"))
    .map((r) => ({
      id: `real-${loanId}-${r.check_id}`,
      loanId,
      checkName: r.check_name,
      severity: r.severity,
      message: r.message,
      citation: r.citation
        ? {
            doc: r.citation.docName,
            page: r.citation.pageNum,
            segment: r.citation.segmentSnippet,
            documentIds: r.citation.documentIds,
          }
        : undefined,
      mitigation: "UNRESOLVED" as const,
    }));
}
