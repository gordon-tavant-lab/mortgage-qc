// tokenCache.test.ts — T009 unit tests: OAuth token acquisition + in-memory caching.
// Traces to plan.md §2.1. Every outbound call is `global.fetch`, mocked — never real network.
//
// RED (expected, Phase 5): tokenCache.ts is currently a Phase-6 stub whose exported functions
// throw `"not implemented — Phase 6"`. Every test below is written against the *contract*
// tokenCache.ts's own file-header comment documents, not against any implementation detail,
// so it should start passing unmodified once Phase 6 lands.
import { beforeEach, describe, expect, it, vi } from "vitest";
import { fakeTokenPayload, jsonResponse } from "./helpers/mockFetch";

async function freshTokenCache() {
  vi.resetModules();
  const fetchMock = vi.fn();
  vi.stubGlobal("fetch", fetchMock);
  const mod = await import("../tokenCache");
  return { tokenCache: mod, fetchMock };
}

describe("tokenCache.getValidToken", () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
  });

  it("fetches a token on first call", async () => {
    const { tokenCache, fetchMock } = await freshTokenCache();
    fetchMock.mockResolvedValue(jsonResponse(fakeTokenPayload("token-abc")));

    const token = await tokenCache.getValidToken();

    expect(token).toBe("token-abc");
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("does NOT re-fetch a token on a second call within the cache window", async () => {
    const { tokenCache, fetchMock } = await freshTokenCache();
    fetchMock.mockResolvedValue(jsonResponse(fakeTokenPayload("token-abc")));

    const first = await tokenCache.getValidToken();
    const second = await tokenCache.getValidToken();

    expect(first).toBe("token-abc");
    expect(second).toBe("token-abc");
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("requests the OAuth client_credentials grant against the configured base URL", async () => {
    const { tokenCache, fetchMock } = await freshTokenCache();
    fetchMock.mockResolvedValue(jsonResponse(fakeTokenPayload()));

    await tokenCache.getValidToken();

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [urlArg] = fetchMock.mock.calls[0] as [string, RequestInit?];
    expect(String(urlArg)).toContain("oauth/token");
    expect(String(urlArg)).toContain("grant_type=client_credentials");
    // Must never be built against anything other than the fixed, server-configured base host.
    expect(String(urlArg).startsWith(process.env.TOUCHLESS_BASE_URL as string)).toBe(true);
  });

  it("fetches a new token again after invalidate() is called", async () => {
    const { tokenCache, fetchMock } = await freshTokenCache();
    fetchMock
      .mockResolvedValueOnce(jsonResponse(fakeTokenPayload("token-1")))
      .mockResolvedValueOnce(jsonResponse(fakeTokenPayload("token-2")));

    const first = await tokenCache.getValidToken();
    tokenCache.invalidate();
    const second = await tokenCache.getValidToken();

    expect(first).toBe("token-1");
    expect(second).toBe("token-2");
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });
});
