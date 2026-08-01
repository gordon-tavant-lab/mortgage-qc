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

export type DataSourceMode = "stored" | "live";

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

  // Guards against a duplicate in-flight fetch for the same documentId (e.g. two viewers
  // mounting for the same citation almost simultaneously) without needing a render-visible
  // "isFetchingDocument" state — no test currently depends on that being observable.
  const fetchingDocumentIds = useRef<Set<string>>(new Set());

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
    [pulledApplications],
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
