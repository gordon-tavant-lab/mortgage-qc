// errors.ts — ErrorCode enum, TouchlessProxyError class, and toErrorEnvelope() serializer
// per plan.md §2.5's error taxonomy (AUTH_FAILURE, NOT_FOUND, TIMEOUT,
// UNEXPECTED_CONTENT_TYPE, INVALID_INPUT, UPSTREAM_ERROR, PROXY_ERROR).

export enum ErrorCode {
  AUTH_FAILURE = "AUTH_FAILURE",
  NOT_FOUND = "NOT_FOUND",
  TIMEOUT = "TIMEOUT",
  UNEXPECTED_CONTENT_TYPE = "UNEXPECTED_CONTENT_TYPE",
  INVALID_INPUT = "INVALID_INPUT",
  UPSTREAM_ERROR = "UPSTREAM_ERROR",
  PROXY_ERROR = "PROXY_ERROR",
}

export interface ErrorEnvelope {
  error: {
    code: ErrorCode;
    message: string;
    upstreamStatus: number | null;
    retryable: boolean;
    requestId: string;
    timestamp: string;
  };
}

/**
 * Thrown by touchlessClient.ts / route handlers, caught by errorHandler.ts. The `message`
 * passed here is for internal/debugging purposes only (e.g. it could be logged server-side by
 * a future debug-only path) — it is deliberately NOT what toErrorEnvelope() surfaces to the
 * browser. The envelope's `message` is always derived from `code` alone (see MESSAGE_BY_CODE
 * below), so a call site can never accidentally leak a raw vendor body or PII into the
 * client-visible error just by constructing this with an unsafe string.
 */
export class TouchlessProxyError extends Error {
  constructor(
    public readonly code: ErrorCode,
    message: string,
    public readonly upstreamStatus: number | null = null,
  ) {
    super(message);
    this.name = "TouchlessProxyError";
  }
}

// retryable=true for AUTH_FAILURE, TIMEOUT, UPSTREAM_ERROR (plan.md §2.5 table); everything
// else (NOT_FOUND, INVALID_INPUT, UNEXPECTED_CONTENT_TYPE, PROXY_ERROR) is not retryable —
// retrying the identical request against the identical malformed/missing resource won't help.
const RETRYABLE_BY_CODE: Record<ErrorCode, boolean> = {
  [ErrorCode.AUTH_FAILURE]: true,
  [ErrorCode.NOT_FOUND]: false,
  [ErrorCode.TIMEOUT]: true,
  [ErrorCode.UNEXPECTED_CONTENT_TYPE]: false,
  [ErrorCode.INVALID_INPUT]: false,
  [ErrorCode.UPSTREAM_ERROR]: true,
  [ErrorCode.PROXY_ERROR]: false,
};

// HTTP status returned to the browser per plan.md §2.5's table.
const STATUS_BY_CODE: Record<ErrorCode, number> = {
  [ErrorCode.AUTH_FAILURE]: 502,
  [ErrorCode.NOT_FOUND]: 404,
  [ErrorCode.TIMEOUT]: 504,
  [ErrorCode.UNEXPECTED_CONTENT_TYPE]: 502,
  [ErrorCode.INVALID_INPUT]: 400,
  [ErrorCode.UPSTREAM_ERROR]: 502,
  [ErrorCode.PROXY_ERROR]: 500,
};

// The ONLY source of a client-visible error message. Generic and categorized per code, per
// plan.md §2.5 / security-review.md §3.3 — deliberately never derived from a thrown error's
// own `.message`, so a raw vendor response body or PII accidentally passed into a
// TouchlessProxyError's constructor at some call site can never reach the browser. This is a
// structural guarantee, not a per-call-site discipline.
const MESSAGE_BY_CODE: Record<ErrorCode, string> = {
  [ErrorCode.AUTH_FAILURE]: "Touchless authentication failed after one retry.",
  [ErrorCode.NOT_FOUND]: "The requested resource was not found.",
  [ErrorCode.TIMEOUT]: "The upstream Touchless call exceeded its deadline.",
  [ErrorCode.UNEXPECTED_CONTENT_TYPE]:
    "The upstream response did not match the expected format.",
  [ErrorCode.INVALID_INPUT]: "The provided identifier is not valid.",
  [ErrorCode.UPSTREAM_ERROR]: "The upstream Touchless call failed.",
  [ErrorCode.PROXY_ERROR]: "An unexpected internal error occurred.",
};

/** Map an ErrorCode to the HTTP status returned to the browser (plan.md §2.5 table). */
export function statusForErrorCode(code: ErrorCode): number {
  return STATUS_BY_CODE[code] ?? 500;
}

/**
 * Map a TouchlessProxyError (or unknown error) to the §2.5 JSON envelope. `message` is always
 * the fixed, generic, per-code string from MESSAGE_BY_CODE — never the raw vendor body, a
 * stack trace, or PII, regardless of what the underlying error's own `.message` contains.
 */
export function toErrorEnvelope(err: unknown, requestId: string): ErrorEnvelope {
  const timestamp = new Date().toISOString();

  if (err instanceof TouchlessProxyError) {
    return {
      error: {
        code: err.code,
        message: MESSAGE_BY_CODE[err.code],
        upstreamStatus: err.upstreamStatus,
        retryable: RETRYABLE_BY_CODE[err.code],
        requestId,
        timestamp,
      },
    };
  }

  return {
    error: {
      code: ErrorCode.PROXY_ERROR,
      message: MESSAGE_BY_CODE[ErrorCode.PROXY_ERROR],
      upstreamStatus: null,
      retryable: false,
      requestId,
      timestamp,
    },
  };
}
