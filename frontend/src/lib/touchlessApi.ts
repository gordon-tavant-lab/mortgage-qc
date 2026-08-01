// touchlessApi.ts — thin fetch wrappers against the backend Touchless proxy
// (spec 020-touchless-api-integration, plan.md §2.6). The browser NEVER calls
// Touchless directly and never sees vendor credentials — every call here is a
// same-origin request to `/api/touchless/*` (proxied to the backend by
// vite.config.ts's `server.proxy` in dev, or served same-origin in a real
// deployment).
//
// Every non-2xx response is parsed as the plan.md §2.5 error envelope; if
// parsing itself fails (e.g. something upstream of the proxy — a dev server,
// a load balancer — returns non-JSON), callers still get a well-formed
// envelope via a generic PROXY_ERROR fallback rather than an unhandled parse
// exception.

export type ErrorCode =
  | "AUTH_FAILURE"
  | "NOT_FOUND"
  | "TIMEOUT"
  | "UNEXPECTED_CONTENT_TYPE"
  | "UPSTREAM_ERROR"
  | "INVALID_INPUT"
  | "PROXY_ERROR";

export interface ErrorEnvelope {
  code: ErrorCode;
  message: string;
  upstreamStatus: number | null;
  retryable: boolean;
  requestId: string;
  timestamp: string;
}

export class TouchlessApiError extends Error {
  envelope: ErrorEnvelope;

  constructor(envelope: ErrorEnvelope) {
    super(envelope.message);
    this.name = "TouchlessApiError";
    this.envelope = envelope;
  }
}

function genericProxyErrorEnvelope(): ErrorEnvelope {
  return {
    code: "PROXY_ERROR",
    message: "An unexpected error occurred contacting the Touchless proxy.",
    upstreamStatus: null,
    retryable: false,
    requestId: "unknown",
    timestamp: new Date().toISOString(),
  };
}

async function parseErrorEnvelope(response: Response): Promise<ErrorEnvelope> {
  try {
    const body = (await response.json()) as { error?: ErrorEnvelope };
    if (body && typeof body === "object" && body.error && typeof body.error.code === "string") {
      return body.error;
    }
    return genericProxyErrorEnvelope();
  } catch {
    return genericProxyErrorEnvelope();
  }
}

export interface PullApplicationResponse {
  applicationId: string;
  fetchedAt: string;
  source: "live";
  application: unknown;
}

/** FR-001/FR-002: POST /api/touchless/applications/:applicationId/pull */
export async function pullApplication(applicationId: string): Promise<PullApplicationResponse> {
  const response = await fetch(`/api/touchless/applications/${encodeURIComponent(applicationId)}/pull`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new TouchlessApiError(await parseErrorEnvelope(response));
  }
  return (await response.json()) as PullApplicationResponse;
}

/** FR-006/FR-007/FR-008: GET /api/touchless/documents/:documentId — raw PDF bytes. */
export async function getDocument(documentId: string): Promise<Blob> {
  const response = await fetch(`/api/touchless/documents/${encodeURIComponent(documentId)}`);
  if (!response.ok) {
    throw new TouchlessApiError(await parseErrorEnvelope(response));
  }
  return await response.blob();
}

export interface OcrField {
  name: string;
  value: string;
  confidence: number;
}

export interface DocumentOcrResponse {
  documentId: string;
  fetchedAt: string;
  fields: OcrField[];
}

/** FR-009: GET /api/touchless/documents/:documentId/ocr — extracted field data. */
export async function getDocumentOcr(documentId: string): Promise<DocumentOcrResponse> {
  const response = await fetch(`/api/touchless/documents/${encodeURIComponent(documentId)}/ocr`);
  if (!response.ok) {
    throw new TouchlessApiError(await parseErrorEnvelope(response));
  }
  return (await response.json()) as DocumentOcrResponse;
}
