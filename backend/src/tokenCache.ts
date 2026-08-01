// tokenCache.ts — in-memory {accessToken, expiresAt} OAuth token cache, per plan.md §2.1's
// token caching/refresh strategy (refresh on expiry-minus-margin, or on first 401; single
// retry, then AUTH_FAILURE — the retry loop itself lives in touchlessClient.ts, this module
// only owns the cache).

import { config } from "./config";

export interface CachedToken {
  accessToken: string;
  expiresAt: number;
}

// Refresh a small margin before actual expiry so a call started just before expiry doesn't
// race the token dying mid-flight (plan.md §2.1).
const REFRESH_MARGIN_MS = 60_000;

let cachedToken: CachedToken | null = null;

interface TokenResponseBody {
  access_token: string;
  expires_in: number;
}

async function requestNewToken(): Promise<CachedToken> {
  const url = new URL(
    "/userservice/oauth/token?grant_type=client_credentials",
    config.touchlessBaseUrl,
  ).toString();

  const basicAuth = Buffer.from(
    `${config.touchlessClientId}:${config.touchlessClientSecret}`,
  ).toString("base64");

  const res = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Basic ${basicAuth}`,
    },
  });

  if (!res.ok) {
    throw new Error(`Touchless OAuth token request failed with status ${res.status}`);
  }

  const body = (await res.json()) as TokenResponseBody;

  return {
    accessToken: body.access_token,
    expiresAt: Date.now() + body.expires_in * 1000,
  };
}

/** Return a valid cached token, refreshing from Touchless if expired/absent. */
export async function getValidToken(): Promise<string> {
  if (cachedToken && Date.now() < cachedToken.expiresAt - REFRESH_MARGIN_MS) {
    return cachedToken.accessToken;
  }

  cachedToken = await requestNewToken();
  return cachedToken.accessToken;
}

/** Discard the cached token (called on a 401 from a forwarded call). */
export function invalidate(): void {
  cachedToken = null;
}
