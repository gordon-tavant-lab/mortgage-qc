// helpers/mockFetch.ts — small builders for fake upstream `Response` objects, plus the
// module-reset + dynamic-import dance every test file needs so each test starts with a
// clean `tokenCache` module (its cached token is a module-level singleton, so tests that
// don't reset it would leak state and become order-dependent — forbidden per the "tests
// must be independent" rule).
import { vi } from "vitest";
import type { Express } from "express";

/** A valid application/json 200 (or any status) response, built with the real `Response`. */
export function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

/** A non-JSON, non-PDF body — used to simulate UNEXPECTED_CONTENT_TYPE from a mis-set header. */
export function textResponse(body: string, status = 200, contentType = "text/html"): Response {
  return new Response(body, {
    status,
    headers: { "content-type": contentType },
  });
}

/** A real application/pdf byte response. */
export function pdfResponse(bytes: Uint8Array = new Uint8Array([0x25, 0x50, 0x44, 0x46]), status = 200): Response {
  return new Response(bytes, {
    status,
    headers: { "content-type": "application/pdf" },
  });
}

/**
 * A response whose promise never settles until the caller's `AbortSignal` (if any was passed
 * to `fetch`) fires — simulating a hung/slow upstream without a real multi-second `setTimeout`.
 * If the implementation under test doesn't wire an AbortSignal at all, this Promise simply
 * never resolves; the enclosing `it(...)`'s own (short) test timeout is the backstop that
 * turns that into a fast, loud test failure rather than a real hang.
 */
export function hangingResponse(init?: RequestInit): Promise<Response> {
  return new Promise((_resolve, reject) => {
    init?.signal?.addEventListener("abort", () => {
      reject(new DOMException("The operation was aborted.", "AbortError"));
    });
  });
}

/** Standard fake token payload for a successful OAuth exchange. */
export function fakeTokenPayload(accessToken = "fake-access-token", expiresIn = 59999) {
  return { access_token: accessToken, expires_in: expiresIn };
}

/**
 * Resets the module registry and re-imports `server.ts` fresh, so each test gets its own
 * `tokenCache` module-level state (no cached token leaking in from a previous test) and its
 * own fetch mock wiring. Call this from a `beforeEach` in every route-level test file.
 */
export async function freshApp(): Promise<{ app: Express; fetchMock: ReturnType<typeof vi.fn> }> {
  vi.resetModules();
  const fetchMock = vi.fn();
  vi.stubGlobal("fetch", fetchMock);
  const mod = await import("../../server");
  return { app: mod.createApp(), fetchMock };
}
