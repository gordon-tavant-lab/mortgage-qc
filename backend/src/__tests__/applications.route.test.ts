// applications.route.test.ts — T010 integration tests:
//   POST /api/touchless/applications/:applicationId/pull
// against the real Express app (via supertest, no real network listener), with every
// outbound Touchless call mocked at `global.fetch`. Traces to FR-001, FR-002, plan.md §2.6.
//
// RED (expected, Phase 5): routes/applications.ts currently always calls
// `next(new Error("... not implemented — Phase 6"))`, so every assertion on status/body
// below will fail against today's scaffold-only 500 PROXY_ERROR fallback.
import { beforeEach, describe, expect, it, vi } from "vitest";
import request from "supertest";
import { fakeTokenPayload, freshApp, jsonResponse } from "./helpers/mockFetch";
import { expectMessageIsSafe, expectValidErrorEnvelope } from "./helpers/envelope";

const KNOWN_APPLICATION_ID = "0eb57730-6d2e-4a6d-8db3-bc1217c77b90";
const ANOTHER_APPLICATION_ID = "11111111-2222-4333-8444-555555555555";

describe("POST /api/touchless/applications/:applicationId/pull", () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
  });

  it("Acceptance Scenario US1.1 — happy path pulls live data through the backend proxy", async () => {
    const { app, fetchMock } = await freshApp();
    const rawApplication = { applicationId: KNOWN_APPLICATION_ID, loanSummary: { status: "CLEAR" } };
    fetchMock
      .mockResolvedValueOnce(jsonResponse(fakeTokenPayload())) // token exchange
      .mockResolvedValueOnce(jsonResponse(rawApplication)); // application pull

    const res = await request(app).post(`/api/touchless/applications/${KNOWN_APPLICATION_ID}/pull`);

    expect(res.status).toBe(200);
    expect(res.body).toMatchObject({
      applicationId: KNOWN_APPLICATION_ID,
      source: "live",
      application: rawApplication,
    });
    expect(typeof res.body.fetchedAt).toBe("string");
    expect(Number.isNaN(Date.parse(res.body.fetchedAt))).toBe(false);
  });

  it("Acceptance Scenario US1.2 — a second pull for a different id reuses the cached OAuth token (no re-fetch of the token itself)", async () => {
    const { app, fetchMock } = await freshApp();
    fetchMock
      .mockResolvedValueOnce(jsonResponse(fakeTokenPayload())) // token exchange (once)
      .mockResolvedValueOnce(jsonResponse({ applicationId: KNOWN_APPLICATION_ID }))
      .mockResolvedValueOnce(jsonResponse({ applicationId: ANOTHER_APPLICATION_ID }));

    const first = await request(app).post(`/api/touchless/applications/${KNOWN_APPLICATION_ID}/pull`);
    const second = await request(app).post(`/api/touchless/applications/${ANOTHER_APPLICATION_ID}/pull`);

    expect(first.status).toBe(200);
    expect(second.status).toBe(200);
    // Token endpoint call count must stay at 1 across both requests — this proves the
    // in-memory token cache, not just that both requests happened to succeed.
    const tokenCalls = fetchMock.mock.calls.filter(([url]) => String(url).includes("oauth/token"));
    expect(tokenCalls).toHaveLength(1);
    expect(fetchMock).toHaveBeenCalledTimes(3);
  });

  it("Acceptance Scenario US1.3 — an unknown applicationId surfaces NOT_FOUND, not stale/fixture data", async () => {
    const { app, fetchMock } = await freshApp();
    fetchMock
      .mockResolvedValueOnce(jsonResponse(fakeTokenPayload()))
      .mockResolvedValueOnce(jsonResponse({ detail: "no such application" }, 404));

    const res = await request(app).post(`/api/touchless/applications/${KNOWN_APPLICATION_ID}/pull`);

    expect(res.status).toBe(404);
    expectValidErrorEnvelope(res.body, "NOT_FOUND");
    expect(res.body.error.retryable).toBe(false);
  });

  it("rejects a malformed applicationId with INVALID_INPUT and never reaches the outbound mock", async () => {
    const { app, fetchMock } = await freshApp();

    const res = await request(app).post("/api/touchless/applications/not-a-uuid/pull");

    expect(res.status).toBe(400);
    expectValidErrorEnvelope(res.body, "INVALID_INPUT");
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("rejects a path-traversal-shaped applicationId with INVALID_INPUT and never reaches the outbound mock", async () => {
    const { app, fetchMock } = await freshApp();

    const res = await request(app).post(
      `/api/touchless/applications/${encodeURIComponent("../etc/passwd")}/pull`,
    );

    expect([400, 404]).toContain(res.status); // Express may 404 the route match itself; either
    // way the outbound Touchless call must never fire for an invalid id.
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("Acceptance Scenario US1.3 — single-retry-on-401 exhausted returns AUTH_FAILURE (never an infinite retry loop)", async () => {
    const { app, fetchMock } = await freshApp();
    fetchMock
      .mockResolvedValueOnce(jsonResponse(fakeTokenPayload("token-1"))) // initial token
      .mockResolvedValueOnce(jsonResponse({ detail: "unauthorized" }, 401)) // first attempt 401s
      .mockResolvedValueOnce(jsonResponse(fakeTokenPayload("token-2"))) // exactly one refresh
      .mockResolvedValueOnce(jsonResponse({ detail: "unauthorized" }, 401)); // retry also 401s

    const res = await request(app).post(`/api/touchless/applications/${KNOWN_APPLICATION_ID}/pull`);

    expect(res.status).toBe(502);
    expectValidErrorEnvelope(res.body, "AUTH_FAILURE");
    expect(res.body.error.retryable).toBe(true);
    // Bounded: token, data(401), token-refresh, data-retry(401) — exactly 4, never more.
    expect(fetchMock).toHaveBeenCalledTimes(4);
  });

  it(
    "returns TIMEOUT when the upstream application call hangs past the configured deadline",
    async () => {
      const { app, fetchMock } = await freshApp();
      fetchMock.mockImplementation((url: string, init?: RequestInit) => {
        if (String(url).includes("oauth/token")) {
          return Promise.resolve(jsonResponse(fakeTokenPayload()));
        }
        return new Promise<Response>((_resolve, reject) => {
          init?.signal?.addEventListener("abort", () => {
            reject(new DOMException("The operation was aborted.", "AbortError"));
          });
        });
      });

      const res = await request(app).post(`/api/touchless/applications/${KNOWN_APPLICATION_ID}/pull`);

      expect(res.status).toBe(504);
      expectValidErrorEnvelope(res.body, "TIMEOUT");
      expect(res.body.error.retryable).toBe(true);
    },
    3000,
  );

  it("never leaks a raw upstream error body or PII into the error envelope's message", async () => {
    const { app, fetchMock } = await freshApp();
    const sensitiveUpstreamBody = {
      status: 404,
      borrowerSsn: "123-45-6789",
      borrowerName: "Jane Q. Borrower",
    };
    fetchMock
      .mockResolvedValueOnce(jsonResponse(fakeTokenPayload()))
      .mockResolvedValueOnce(jsonResponse(sensitiveUpstreamBody, 404));

    const res = await request(app).post(`/api/touchless/applications/${KNOWN_APPLICATION_ID}/pull`);

    expectValidErrorEnvelope(res.body, "NOT_FOUND");
    expectMessageIsSafe(res.body, ["123-45-6789", "Jane Q. Borrower", JSON.stringify(sensitiveUpstreamBody)]);
  });
});
