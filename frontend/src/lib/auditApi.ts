// auditApi.ts — 021-touchless-audit-run: thin fetch wrapper for the real audit-run
// endpoint (contracts/audit-run.md). Mirrors touchlessApi.ts's own pattern (same backend
// error-envelope shape, reused via TouchlessApiError/ErrorEnvelope rather than a second
// error type) -- the audit route lives at /api/audit/*, a sibling of /api/touchless/*,
// not nested under it.
import { TouchlessApiError, type ErrorEnvelope } from "./touchlessApi";

export interface AuditRunResponse {
  applicationId: string;
  evaluatedAt: string;
  loanStatus: "PASS" | "FAILED" | "NEEDS_REVIEW";
  compiledCheckCount: number;
  excludedCheckCount: number;
  runResult: unknown;
}

function genericProxyErrorEnvelope(): ErrorEnvelope {
  return {
    code: "PROXY_ERROR",
    message: "An unexpected error occurred running the audit.",
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

/** FR-003: POST /api/audit/:applicationId/run */
export async function runAuditRequest(applicationId: string): Promise<AuditRunResponse> {
  const response = await fetch(`/api/audit/${encodeURIComponent(applicationId)}/run`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new TouchlessApiError(await parseErrorEnvelope(response));
  }
  return (await response.json()) as AuditRunResponse;
}
