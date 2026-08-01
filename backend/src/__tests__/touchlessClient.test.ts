// touchlessClient.test.ts — T009 unit tests for the single chokepoint both route files call
// through: isValidUuid() (INVALID_INPUT guard) and buildUrl() (SSRF guard — fixed base host,
// never client-influenced). Traces to plan.md §2.6, security-review.md §2,
// plan.md §6 open item #4 ("this validation lands in touchlessClient.ts itself").
//
// RED (expected, Phase 5): every exported function currently throws
// "not implemented — Phase 6" unconditionally.
import { beforeEach, describe, expect, it, vi } from "vitest";

async function freshTouchlessClient() {
  vi.resetModules();
  return import("../touchlessClient");
}

describe("touchlessClient.isValidUuid", () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
  });

  it("accepts a well-formed UUID", async () => {
    const client = await freshTouchlessClient();
    expect(client.isValidUuid("0eb57730-6d2e-4a6d-8db3-bc1217c77b90")).toBe(true);
  });

  it.each([
    ["not-a-uuid", "not-a-uuid"],
    ["path traversal attempt", "../etc/passwd"],
    ["empty string", ""],
    ["too short", "0eb57730-6d2e-4a6d-8db3"],
    ["sql-injection-shaped", "'; DROP TABLE applications; --"],
    ["url-shaped (SSRF attempt)", "http://evil.example.com/"],
    ["uuid plus trailing junk", "0eb57730-6d2e-4a6d-8db3-bc1217c77b90/../.."],
  ])("rejects a malformed applicationId/documentId: %s (%s)", async (_label, malformed) => {
    const client = await freshTouchlessClient();
    expect(client.isValidUuid(malformed)).toBe(false);
  });
});

describe("touchlessClient.buildUrl", () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
  });

  it("builds a URL rooted at the fixed, server-configured TOUCHLESS_BASE_URL", async () => {
    const client = await freshTouchlessClient();
    const url = client.buildUrl("/store/application/results/0eb57730-6d2e-4a6d-8db3-bc1217c77b90");
    expect(url.startsWith(process.env.TOUCHLESS_BASE_URL as string)).toBe(true);
    expect(url).toContain("/store/application/results/0eb57730-6d2e-4a6d-8db3-bc1217c77b90");
  });

  it("never lets a path segment redirect the request to a different host (SSRF guard)", async () => {
    const client = await freshTouchlessClient();
    // Even if a caller (mistakenly) hands buildUrl something host-like, the resulting URL
    // must still be anchored to the fixed base host, never re-hosted to the attacker value.
    const url = client.buildUrl("http://attacker.example.com/store/documents/read/x");
    expect(url.startsWith(process.env.TOUCHLESS_BASE_URL as string)).toBe(true);
    expect(url).not.toContain("attacker.example.com");
  });
});
