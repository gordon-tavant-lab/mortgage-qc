// audit.route.test.ts — 021-touchless-audit-run T014: POST /api/audit/:applicationId/run
// against the real Express app, with the Python subprocess mocked at child_process.execFile
// (never actually spawning python3 in this test suite) and the Touchless pull call mocked at
// global.fetch (per applications.route.test.ts's own convention) to seed applicationStore.
import { beforeEach, describe, expect, it, vi } from "vitest";
import request from "supertest";
import type { Express } from "express";
import { fakeTokenPayload, jsonResponse } from "./helpers/mockFetch";
import { expectValidErrorEnvelope } from "./helpers/envelope";

const KNOWN_APPLICATION_ID = "0eb57730-6d2e-4a6d-8db3-bc1217c77b90";
const NEVER_PULLED_APPLICATION_ID = "11111111-2222-4333-8444-555555555555";

const execFileMock = vi.fn();

vi.mock("child_process", () => ({
  execFile: (...args: unknown[]) => execFileMock(...args),
}));

/** Same freshApp() shape as helpers/mockFetch.ts, but also wires the child_process mock
 * fresh per test (vi.resetModules() means routes/audit.ts's own `promisify(execFile)`
 * binding must be re-created against the mock each time too). */
async function freshAppWithAuditMock(): Promise<{ app: Express; fetchMock: ReturnType<typeof vi.fn> }> {
  vi.resetModules();
  execFileMock.mockReset();
  const fetchMock = vi.fn();
  vi.stubGlobal("fetch", fetchMock);
  const mod = await import("../server");
  return { app: mod.createApp(), fetchMock };
}

/** Seeds applicationStore via a real pull-route call (mocked upstream), matching how the
 * audit route's NOT_FOUND guard is actually meant to be satisfied. */
async function pullApplication(app: Express, fetchMock: ReturnType<typeof vi.fn>, applicationId: string, application: unknown) {
  fetchMock
    .mockResolvedValueOnce(jsonResponse(fakeTokenPayload()))
    .mockResolvedValueOnce(jsonResponse(application));
  const res = await request(app).post(`/api/touchless/applications/${applicationId}/pull`);
  expect(res.status).toBe(200);
}

/** execFile's real signature is (file, args, options, callback) — mock it callback-style so
 * util.promisify(execFile) wraps it exactly as it would the real Node API. */
function mockSuccessfulRun(output: Record<string, unknown>) {
  execFileMock.mockImplementation((_file, _args, _options, callback) => {
    callback(null, { stdout: JSON.stringify(output), stderr: "" });
  });
}

describe("POST /api/audit/:applicationId/run", () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
  });

  it("200s with the audit-run response shape after a successful subprocess run", async () => {
    const { app, fetchMock } = await freshAppWithAuditMock();
    await pullApplication(app, fetchMock, KNOWN_APPLICATION_ID, {
      applicationId: KNOWN_APPLICATION_ID,
      documents: [],
    });
    mockSuccessfulRun({
      loanStatus: "PASS",
      compiledCheckCount: 37,
      excludedCheckCount: 171,
      runResult: { results: [] },
    });

    const res = await request(app).post(`/api/audit/${KNOWN_APPLICATION_ID}/run`);

    expect(res.status).toBe(200);
    expect(res.body).toMatchObject({
      applicationId: KNOWN_APPLICATION_ID,
      loanStatus: "PASS",
      compiledCheckCount: 37,
      excludedCheckCount: 171,
      runResult: { results: [] },
    });
    expect(typeof res.body.evaluatedAt).toBe("string");
    expect(Number.isNaN(Date.parse(res.body.evaluatedAt))).toBe(false);
  });

  it("NOT_FOUND when applicationId was never pulled this session", async () => {
    const { app } = await freshAppWithAuditMock();

    const res = await request(app).post(`/api/audit/${NEVER_PULLED_APPLICATION_ID}/run`);

    expect(res.status).toBe(404);
    expectValidErrorEnvelope(res.body, "NOT_FOUND");
    expect(execFileMock).not.toHaveBeenCalled();
  });

  it("INVALID_INPUT for a malformed applicationId, never invoking the subprocess", async () => {
    const { app } = await freshAppWithAuditMock();

    const res = await request(app).post("/api/audit/not-a-uuid/run");

    expect(res.status).toBe(400);
    expectValidErrorEnvelope(res.body, "INVALID_INPUT");
    expect(execFileMock).not.toHaveBeenCalled();
  });

  it("PROXY_ERROR when the subprocess exits non-zero", async () => {
    const { app, fetchMock } = await freshAppWithAuditMock();
    await pullApplication(app, fetchMock, KNOWN_APPLICATION_ID, { applicationId: KNOWN_APPLICATION_ID });
    execFileMock.mockImplementation((_file, _args, _options, callback) => {
      callback(new Error("Command failed with exit code 1"), { stdout: "", stderr: "Traceback..." });
    });

    const res = await request(app).post(`/api/audit/${KNOWN_APPLICATION_ID}/run`);

    expect(res.status).toBe(500);
    expectValidErrorEnvelope(res.body, "PROXY_ERROR");
  });

  it("PROXY_ERROR when the subprocess produces unparseable stdout", async () => {
    const { app, fetchMock } = await freshAppWithAuditMock();
    await pullApplication(app, fetchMock, KNOWN_APPLICATION_ID, { applicationId: KNOWN_APPLICATION_ID });
    execFileMock.mockImplementation((_file, _args, _options, callback) => {
      callback(null, { stdout: "not json at all", stderr: "" });
    });

    const res = await request(app).post(`/api/audit/${KNOWN_APPLICATION_ID}/run`);

    expect(res.status).toBe(500);
    expectValidErrorEnvelope(res.body, "PROXY_ERROR");
  });

  it("PROXY_ERROR when the subprocess produces valid JSON in an unexpected shape", async () => {
    const { app, fetchMock } = await freshAppWithAuditMock();
    await pullApplication(app, fetchMock, KNOWN_APPLICATION_ID, { applicationId: KNOWN_APPLICATION_ID });
    mockSuccessfulRun({ unexpected: "shape" });

    const res = await request(app).post(`/api/audit/${KNOWN_APPLICATION_ID}/run`);

    expect(res.status).toBe(500);
    expectValidErrorEnvelope(res.body, "PROXY_ERROR");
  });
});
