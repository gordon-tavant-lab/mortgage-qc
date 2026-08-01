// touchlessClient.ts — the single chokepoint both route files call through: isValidUuid()
// (INVALID_INPUT guard), buildUrl() (against the fixed, server-configured TOUCHLESS_BASE_URL
// — never client-influenced, the SSRF guard per plan.md §2.6 / security-review.md §2), and
// authorizedGet() (attaches Bearer token via tokenCache, single-retry-on-401, verifies
// response content-type, enforces the configured request timeout). UUID validation must not
// be duplicated/forgotten in a route handler (plan.md §6 open item #4).

import { config } from "./config";
import { ErrorCode, TouchlessProxyError } from "./errors";
import { getValidToken, invalidate } from "./tokenCache";

const UUID_RE = /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/;

/** Validate a path param is a well-formed UUID before it reaches any outbound URL. */
export function isValidUuid(value: string): boolean {
  if (typeof value !== "string") return false;
  return UUID_RE.test(value);
}

/**
 * Build an outbound URL against the fixed TOUCHLESS_BASE_URL. `path` is always joined as a
 * path segment relative to the fixed base host — it is never treated as (or allowed to
 * become) a full URL that could re-host the request to a different origin, per
 * security-review.md §2's SSRF guard.
 */
export function buildUrl(path: string): string {
  const base = new URL(config.touchlessBaseUrl);
  // Strip a leading scheme/host if a caller mistakenly hands in something URL-shaped —
  // treat everything after the last occurrence of "://" (if any) as a bare path, and always
  // anchor the result to `base`. This guarantees the returned URL's origin is always the
  // fixed TOUCHLESS_BASE_URL, never an attacker-controlled host embedded in `path`.
  const schemeStripped = path.replace(/^[a-zA-Z][a-zA-Z0-9+.-]*:\/\/[^/]+/, "");
  const normalizedPath = schemeStripped.startsWith("/") ? schemeStripped : `/${schemeStripped}`;
  return new URL(normalizedPath, base).toString();
}

function safeErrorMessage(prefix: string): string {
  // Generic, categorized message only — never includes the raw upstream body/headers.
  return prefix;
}

export type ExpectedContentType = "application/pdf" | "application/json";

interface AuthorizedGetOptions {
  /** If provided, a successful (2xx) response's content-type is checked against this. */
  expectedContentType?: ExpectedContentType;
}

/**
 * Perform an authenticated GET against Touchless, with single-retry-on-401. Attaches the
 * cached Bearer token, enforces `config.requestTimeoutMs` via AbortSignal, and (when
 * `expectedContentType` is given) verifies the response's content-type on a 2xx before
 * returning it to the caller — a mismatch is surfaced as UNEXPECTED_CONTENT_TYPE.
 */
export async function authorizedGet(
  path: string,
  options: AuthorizedGetOptions = {},
): Promise<Response> {
  const url = buildUrl(path);

  const doFetch = async (): Promise<Response> => {
    const token = await getValidToken();
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), config.requestTimeoutMs);
    try {
      return await fetch(url, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        signal: controller.signal,
      });
    } catch (err) {
      if (err instanceof Error && err.name === "AbortError") {
        throw new TouchlessProxyError(
          ErrorCode.TIMEOUT,
          safeErrorMessage("The upstream Touchless call exceeded its deadline."),
          null,
        );
      }
      throw err;
    } finally {
      clearTimeout(timeout);
    }
  };

  let res = await doFetch();

  if (res.status === 401) {
    // Single retry-on-401: discard the cached token, get exactly one fresh token, retry the
    // original call exactly once. If that retry also 401s, surface AUTH_FAILURE — never a
    // further retry (security-review.md §4.3 / MUST-FIX #5).
    invalidate();
    res = await doFetch();
    if (res.status === 401) {
      throw new TouchlessProxyError(
        ErrorCode.AUTH_FAILURE,
        safeErrorMessage("Touchless authentication failed after one retry."),
        401,
      );
    }
  }

  if (res.status === 404) {
    throw new TouchlessProxyError(
      ErrorCode.NOT_FOUND,
      safeErrorMessage("The requested resource was not found."),
      404,
    );
  }

  if (!res.ok) {
    throw new TouchlessProxyError(
      ErrorCode.UPSTREAM_ERROR,
      safeErrorMessage("The upstream Touchless call failed."),
      res.status,
    );
  }

  if (options.expectedContentType) {
    const contentType = res.headers.get("content-type") ?? "";
    if (!contentType.includes(options.expectedContentType)) {
      throw new TouchlessProxyError(
        ErrorCode.UNEXPECTED_CONTENT_TYPE,
        safeErrorMessage("The upstream response did not match the expected content type."),
        res.status,
      );
    }
  }

  return res;
}
