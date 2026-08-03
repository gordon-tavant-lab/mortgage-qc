// dataSourceContext.tsx — DataSourceProvider + useDataSource() (spec 020, plan.md §2.3/§2.4).
// Traces to FR-003, FR-004, FR-005.
//
// In-memory only: mode + both caches live in React state, never sessionStorage/localStorage
// (plan.md §2.3) — a reload resets the whole live-data experience together, which is the more
// honest behavior per plan.md's reasoning (no "why does it say Live but show nothing" moment).
// The backend proxy performs no caching of its own (plan.md §2.4) — this is the ONLY cache.
import {
  createContext,
  useCallback,
  useContext,
  useRef,
  useState,
  type ReactNode,
} from "react";
import {
  TouchlessApiError,
  getDocument,
  getDocumentOcr,
  pullApplication as pullApplicationRequest,
  type ErrorEnvelope,
  type OcrField,
} from "./touchlessApi";
import { generateNarrativeRequest, runAuditRequest, type AuditRunResponse, type NarrativeResponse } from "./auditApi";
import type { Loan, LoanDisplayState } from "./types";

export type DataSourceMode = "stored" | "live";

// 021-touchless-audit-run: the real, engine-computed outcome of one audit run for a
// pulled applicationId. "running" is transient (FR-004); "resolved" carries the actual
// RunResult-derived verdict (never fabricated, per FR-003/SC-002); "error" is the
// subprocess-failure case (FR-006a) -- never a real engine verdict, and the caller
// (LoanQueue.tsx) must never render it as if it were one.
export type AuditRunState =
  | { status: "running" }
  | { status: "resolved"; result: AuditRunResponse }
  | { status: "error"; message: string };

// live-demo-engine-wiring (spec014): same running/resolved/error shape as AuditRunState,
// for the LLM-authored decision narrative -- a separate, on-demand, real Bedrock call
// (never fired automatically alongside the audit run above).
export type NarrativeState =
  | { status: "generating" }
  | { status: "resolved"; result: NarrativeResponse }
  | { status: "error"; message: string };

export interface PulledApplication {
  applicationId: string;
  fetchedAt: string;
  source: "live";
  application: unknown;
}

export interface RetrievedDocument {
  documentId: string;
  fetchedAt: string;
  pdfObjectUrl: string;
  ocrFields: OcrField[];
}

interface DataSourceContextValue {
  mode: DataSourceMode;
  setMode: (mode: DataSourceMode) => void;
  pulledApplications: Map<string, PulledApplication>;
  retrievedDocuments: Map<string, RetrievedDocument>;
  auditRuns: Map<string, AuditRunState>;
  runAudit: (applicationId: string) => Promise<void>;
  narratives: Map<string, NarrativeState>;
  generateNarrative: (applicationId: string) => Promise<void>;
  resetFetchedApplications: () => void;
  pullApplication: (applicationId: string, options?: { force?: boolean }) => Promise<void>;
  getOrFetchDocument: (documentId: string) => Promise<void>;
  isPullingApplication: (applicationId: string) => boolean;
  applicationError: (applicationId: string) => ErrorEnvelope | undefined;
  documentError: (documentId: string) => ErrorEnvelope | undefined;
}

const DataSourceContext = createContext<DataSourceContextValue | undefined>(undefined);

function genericErrorEnvelope(): ErrorEnvelope {
  return {
    code: "PROXY_ERROR",
    message: "An unexpected error occurred.",
    upstreamStatus: null,
    retryable: false,
    requestId: "unknown",
    timestamp: new Date().toISOString(),
  };
}

function toEnvelope(err: unknown): ErrorEnvelope {
  return err instanceof TouchlessApiError ? err.envelope : genericErrorEnvelope();
}

export function DataSourceProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<DataSourceMode>("stored");
  const [pulledApplications, setPulledApplications] = useState<Map<string, PulledApplication>>(
    () => new Map(),
  );
  const [retrievedDocuments, setRetrievedDocuments] = useState<Map<string, RetrievedDocument>>(
    () => new Map(),
  );
  const [pullingIds, setPullingIds] = useState<Set<string>>(() => new Set());
  const [applicationErrors, setApplicationErrors] = useState<Map<string, ErrorEnvelope>>(
    () => new Map(),
  );
  const [documentErrors, setDocumentErrors] = useState<Map<string, ErrorEnvelope>>(() => new Map());
  const [auditRuns, setAuditRuns] = useState<Map<string, AuditRunState>>(() => new Map());
  const [narratives, setNarratives] = useState<Map<string, NarrativeState>>(() => new Map());

  // Guards against a duplicate in-flight fetch for the same documentId (e.g. two viewers
  // mounting for the same citation almost simultaneously) without needing a render-visible
  // "isFetchingDocument" state — no test currently depends on that being observable.
  const fetchingDocumentIds = useRef<Set<string>>(new Set());

  // live-demo-engine-wiring (spec014): generates the decision narrative for an already-
  // pulled, already-run application. Fired automatically the instant a real audit run
  // resolves (see runAudit below, Gordon's explicit call) -- a real, billed Bedrock call
  // every time, not gated behind a separate button anymore.
  const generateNarrative = useCallback(async (applicationId: string) => {
    setNarratives((prev) => {
      const next = new Map(prev);
      next.set(applicationId, { status: "generating" });
      return next;
    });

    try {
      const result = await generateNarrativeRequest(applicationId);
      setNarratives((prev) => {
        const next = new Map(prev);
        next.set(applicationId, { status: "resolved", result });
        return next;
      });
    } catch (err) {
      const envelope = toEnvelope(err);
      setNarratives((prev) => {
        const next = new Map(prev);
        next.set(applicationId, { status: "error", message: envelope.message });
        return next;
      });
    }
  }, []);

  // 021-touchless-audit-run FR-003: triggers the real deterministic-engine run for an
  // already-pulled application. No dependency on component state -- setAuditRuns's
  // functional-update form means this never needs `auditRuns` itself in its deps.
  const runAudit = useCallback(async (applicationId: string) => {
    setAuditRuns((prev) => {
      const next = new Map(prev);
      next.set(applicationId, { status: "running" });
      return next;
    });

    try {
      const result = await runAuditRequest(applicationId);
      setAuditRuns((prev) => {
        const next = new Map(prev);
        next.set(applicationId, { status: "resolved", result });
        return next;
      });
      // live-demo-engine-wiring: the narrative generates the instant the audit resolves --
      // same "no second click" discipline FR-003 already established for pull -> run.
      void generateNarrative(applicationId);
    } catch (err) {
      const envelope = toEnvelope(err);
      setAuditRuns((prev) => {
        const next = new Map(prev);
        next.set(applicationId, { status: "error", message: envelope.message });
        return next;
      });
    }
  }, [generateNarrative]);

  const pullApplication = useCallback(
    async (applicationId: string, options?: { force?: boolean }) => {
      const force = options?.force ?? false;
      if (!force && pulledApplications.has(applicationId)) {
        return;
      }

      setPullingIds((prev) => {
        const next = new Set(prev);
        next.add(applicationId);
        return next;
      });
      setApplicationErrors((prev) => {
        if (!prev.has(applicationId)) return prev;
        const next = new Map(prev);
        next.delete(applicationId);
        return next;
      });

      try {
        const result = await pullApplicationRequest(applicationId);
        setPulledApplications((prev) => {
          const next = new Map(prev);
          next.set(applicationId, {
            applicationId: result.applicationId,
            fetchedAt: result.fetchedAt,
            source: result.source,
            application: result.application,
          });
          return next;
        });
        // FR-003: the audit run fires the instant the fetch resolves -- no second click,
        // no separate user action. Fire-and-forget from the caller's perspective; runAudit
        // manages its own "running" -> "resolved"/"error" state independently.
        void runAudit(applicationId);
      } catch (err) {
        const envelope = toEnvelope(err);
        setApplicationErrors((prev) => {
          const next = new Map(prev);
          next.set(applicationId, envelope);
          return next;
        });
      } finally {
        setPullingIds((prev) => {
          const next = new Set(prev);
          next.delete(applicationId);
          return next;
        });
      }
    },
    [pulledApplications, runAudit],
  );

  const getOrFetchDocument = useCallback(
    async (documentId: string) => {
      if (retrievedDocuments.has(documentId)) return;
      if (fetchingDocumentIds.current.has(documentId)) return;

      fetchingDocumentIds.current.add(documentId);
      setDocumentErrors((prev) => {
        if (!prev.has(documentId)) return prev;
        const next = new Map(prev);
        next.delete(documentId);
        return next;
      });

      try {
        const [blob, ocr] = await Promise.all([getDocument(documentId), getDocumentOcr(documentId)]);
        const pdfObjectUrl = URL.createObjectURL(blob);
        setRetrievedDocuments((prev) => {
          const next = new Map(prev);
          next.set(documentId, {
            documentId,
            fetchedAt: ocr.fetchedAt,
            pdfObjectUrl,
            ocrFields: ocr.fields,
          });
          return next;
        });
      } catch (err) {
        const envelope = toEnvelope(err);
        setDocumentErrors((prev) => {
          const next = new Map(prev);
          next.set(documentId, envelope);
          return next;
        });
      } finally {
        fetchingDocumentIds.current.delete(documentId);
      }
    },
    [retrievedDocuments],
  );

  // 021-touchless-audit-run (US2, T025): wired into RoutesFlow.tsx's existing "Restore to
  // Gold" (019's own reset control) so ONE button resets the whole demo, not just the
  // authored-ruleset draft -- clears every piece of fetched/derived state this feature
  // added, so a post-restore session is indistinguishable from a fresh page load.
  const resetFetchedApplications = useCallback(() => {
    setPulledApplications(new Map());
    setPullingIds(new Set());
    setApplicationErrors(new Map());
    setAuditRuns(new Map());
    setNarratives(new Map());
    setRetrievedDocuments(new Map());
    setDocumentErrors(new Map());
  }, []);

  const isPullingApplication = useCallback(
    (applicationId: string) => pullingIds.has(applicationId),
    [pullingIds],
  );
  const applicationError = useCallback(
    (applicationId: string) => applicationErrors.get(applicationId),
    [applicationErrors],
  );
  const documentError = useCallback(
    (documentId: string) => documentErrors.get(documentId),
    [documentErrors],
  );

  const value: DataSourceContextValue = {
    mode,
    setMode,
    pulledApplications,
    retrievedDocuments,
    auditRuns,
    runAudit,
    narratives,
    generateNarrative,
    resetFetchedApplications,
    pullApplication,
    getOrFetchDocument,
    isPullingApplication,
    applicationError,
    documentError,
  };

  return <DataSourceContext.Provider value={value}>{children}</DataSourceContext.Provider>;
}

export function useDataSource(): DataSourceContextValue {
  const ctx = useContext(DataSourceContext);
  if (!ctx) {
    throw new Error("useDataSource must be used within a DataSourceProvider");
  }
  return ctx;
}

// 021-touchless-audit-run: the single source of truth for how a loan's status should be
// DISPLAYED -- never read loan.status directly for an applicationId-bearing loan (that
// would either show a stale seed or, worse, look like a real verdict before one exists).
// Cosmetic loans (no applicationId) always resolve to their static mock status.
//
// Deliberately takes `ctx` as a parameter rather than being a `useXyz()` hook that calls
// `useDataSource()` internally: an internal same-module call to `useDataSource()` bypasses
// `vi.spyOn(dataSourceContext, "useDataSource")` (ES module bindings resolve internal calls
// directly, not through the exported namespace object) -- this codebase's own established
// component-test convention (RetrievedDocumentViewer.test.tsx, ExceptionReview.test.tsx)
// depends on that spy actually working. Callers do `const ctx = useDataSource(); const
// display = deriveLoanDisplayState(loan, ctx);` instead.
export function deriveLoanDisplayState(loan: Loan, ctx: DataSourceContextValue): LoanDisplayState {
  if (!loan.applicationId) {
    return { kind: "resolved", status: loan.status };
  }
  const audit = ctx.auditRuns.get(loan.applicationId);
  if (!audit) return { kind: "not_fetched" };
  if (audit.status === "running") return { kind: "running" };
  if (audit.status === "error") return { kind: "error", message: audit.message };
  return { kind: "resolved", status: audit.result.loanStatus };
}
