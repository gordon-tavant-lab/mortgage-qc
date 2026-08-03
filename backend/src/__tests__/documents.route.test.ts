// documents.route.test.ts — T010 integration tests:
//   GET /api/touchless/documents/:documentId
//   GET /api/touchless/documents/:documentId/ocr
// against the real Express app (via supertest), every outbound Touchless call mocked at
// `global.fetch`. Traces to FR-006, FR-007, FR-009, plan.md §2.6.
//
// RED (expected, Phase 5): routes/documents.ts currently always calls
// `next(new Error("... not implemented — Phase 6"))`.
import { beforeEach, describe, expect, it, vi } from "vitest";
import request from "supertest";
import {
  fakeTokenPayload,
  freshApp,
  jsonResponse,
  pdfResponse,
  textResponse,
} from "./helpers/mockFetch";
import { expectMessageIsSafe, expectValidErrorEnvelope } from "./helpers/envelope";

// Example documentId from plan.md §2.6's own OCR response sample.
const KNOWN_DOCUMENT_ID = "632a9c26-d636-4564-b89d-256a5dfe70d4";

describe("GET /api/touchless/documents/:documentId", () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
  });

  it("Acceptance Scenario US2.1 — returns the real PDF bytes, Content-Type: application/pdf", async () => {
    const { app, fetchMock } = await freshApp();
    const bytes = new Uint8Array([0x25, 0x50, 0x44, 0x46, 0x2d, 0x31, 0x2e, 0x34]); // "%PDF-1.4"
    fetchMock
      .mockResolvedValueOnce(jsonResponse(fakeTokenPayload()))
      .mockResolvedValueOnce(pdfResponse(bytes));

    const res = await request(app).get(`/api/touchless/documents/${KNOWN_DOCUMENT_ID}`);

    expect(res.status).toBe(200);
    expect(res.headers["content-type"]).toMatch(/application\/pdf/);
    expect(Buffer.compare(res.body as Buffer, Buffer.from(bytes))).toBe(0);
  });

  it("Acceptance Scenario US2.3 — a non-PDF content-type from Touchless is UNEXPECTED_CONTENT_TYPE, not a silent pass-through", async () => {
    const { app, fetchMock } = await freshApp();
    fetchMock
      .mockResolvedValueOnce(jsonResponse(fakeTokenPayload()))
      .mockResolvedValueOnce(textResponse("<html>not a pdf</html>", 200, "text/html"));

    const res = await request(app).get(`/api/touchless/documents/${KNOWN_DOCUMENT_ID}`);

    expect(res.status).toBe(502);
    expectValidErrorEnvelope(res.body, "UNEXPECTED_CONTENT_TYPE");
  });

  it("Acceptance Scenario US2.3 — a 404 from Touchless passes through as NOT_FOUND", async () => {
    const { app, fetchMock } = await freshApp();
    fetchMock
      .mockResolvedValueOnce(jsonResponse(fakeTokenPayload()))
      .mockResolvedValueOnce(jsonResponse({ detail: "no such document" }, 404));

    const res = await request(app).get(`/api/touchless/documents/${KNOWN_DOCUMENT_ID}`);

    expect(res.status).toBe(404);
    expectValidErrorEnvelope(res.body, "NOT_FOUND");
  });

  it("rejects a malformed documentId with INVALID_INPUT and never reaches the outbound mock", async () => {
    const { app, fetchMock } = await freshApp();

    const res = await request(app).get("/api/touchless/documents/not-a-uuid");

    expect(res.status).toBe(400);
    expectValidErrorEnvelope(res.body, "INVALID_INPUT");
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it(
    "returns TIMEOUT when the upstream document call hangs past the configured deadline",
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

      const res = await request(app).get(`/api/touchless/documents/${KNOWN_DOCUMENT_ID}`);

      expect(res.status).toBe(504);
      expectValidErrorEnvelope(res.body, "TIMEOUT");
    },
    3000,
  );
});

describe("GET /api/touchless/documents/:documentId/ocr", () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
  });

  it("Acceptance Scenario US2.1 — returns the real extracted-field data (name, value, confidence)", async () => {
    const { app, fetchMock } = await freshApp();
    // Touchless's real /ocr response is a BARE top-level array, not wrapped in an
    // envelope object — verified live 2026-08-01 against the QA gateway, see
    // output/TOUCHLESS-API-LIVE-TEST-2026-08-01.md.
    const ocrFields = [
      { name: "Borrower_First_Name", value: "ANDY", confidence: 100.0 },
      { name: "Borrower_SSN", value: "999-60-3333", confidence: 0.0 },
    ];
    fetchMock
      .mockResolvedValueOnce(jsonResponse(fakeTokenPayload()))
      .mockResolvedValueOnce(jsonResponse(ocrFields));

    const res = await request(app).get(`/api/touchless/documents/${KNOWN_DOCUMENT_ID}/ocr`);

    expect(res.status).toBe(200);
    expect(res.body.documentId).toBe(KNOWN_DOCUMENT_ID);
    expect(res.body.fields).toEqual(ocrFields);
  });

  it("accepts a valid JSON body even when Touchless mislabels it Content-Type: text/plain (verified live vendor quirk, output/TOUCHLESS-API-LIVE-TEST-2026-08-01.md)", async () => {
    const { app, fetchMock } = await freshApp();
    const ocrFields = [{ name: "DocumentType", value: "Credit Report", confidence: 100.0 }];
    fetchMock
      .mockResolvedValueOnce(jsonResponse(fakeTokenPayload()))
      .mockResolvedValueOnce(textResponse(JSON.stringify(ocrFields), 200, "text/plain"));

    const res = await request(app).get(`/api/touchless/documents/${KNOWN_DOCUMENT_ID}/ocr`);

    expect(res.status).toBe(200);
    expect(res.body.fields).toEqual(ocrFields);
  });

  it("passes through a confidence value above 100 unmodified — no clamping/normalizing (plan.md §2.6)", async () => {
    const { app, fetchMock } = await freshApp();
    const ocrFields = [{ name: "Some_Field", value: "x", confidence: 102.0 }];
    fetchMock
      .mockResolvedValueOnce(jsonResponse(fakeTokenPayload()))
      .mockResolvedValueOnce(jsonResponse(ocrFields));

    const res = await request(app).get(`/api/touchless/documents/${KNOWN_DOCUMENT_ID}/ocr`);

    expect(res.status).toBe(200);
    expect(res.body.fields[0].confidence).toBe(102.0);
  });

  it("021-touchless-audit-run live finding (2026-08-02): normalizes Touchless's alternate flat-structured-object OCR shape (e.g. Gift Letter, Purchase Agreement) into the same {name,value} field list, with confidence omitted rather than fabricated", async () => {
    const { app, fetchMock } = await freshApp();
    // Real shape B, verified live against the QA gateway for the real demo loan's Gift
    // Letter document -- a single-element array containing one flat object of named
    // fields, with NO confidence anywhere (unlike shape A's {name,value,confidence}[]).
    const structuredBody = [
      {
        donorName: "John America",
        donorAddress: "5485 Lake Road, Columbine Hills, CO 80123",
        isItSigned: true,
        amountDeposited: "10000.00",
      },
    ];
    fetchMock
      .mockResolvedValueOnce(jsonResponse(fakeTokenPayload()))
      .mockResolvedValueOnce(jsonResponse(structuredBody));

    const res = await request(app).get(`/api/touchless/documents/${KNOWN_DOCUMENT_ID}/ocr`);

    expect(res.status).toBe(200);
    expect(res.body.fields).toEqual(
      expect.arrayContaining([
        { name: "donorName", value: "John America" },
        { name: "donorAddress", value: "5485 Lake Road, Columbine Hills, CO 80123" },
        { name: "isItSigned", value: "true" },
        { name: "amountDeposited", value: "10000.00" },
      ]),
    );
    // Never fabricates a confidence value for a shape that genuinely has none.
    for (const field of res.body.fields) {
      expect(field).not.toHaveProperty("confidence");
    }
  });

  it("Acceptance Scenario US2.3 — a zero-field OCR response is UNEXPECTED_CONTENT_TYPE, not a successful empty result (Edge Case)", async () => {
    const { app, fetchMock } = await freshApp();
    fetchMock
      .mockResolvedValueOnce(jsonResponse(fakeTokenPayload()))
      .mockResolvedValueOnce(jsonResponse([]));

    const res = await request(app).get(`/api/touchless/documents/${KNOWN_DOCUMENT_ID}/ocr`);

    expect(res.status).toBe(502);
    expectValidErrorEnvelope(res.body, "UNEXPECTED_CONTENT_TYPE");
  });

  it("treats a shape that doesn't parse as {name,value,confidence}[] as UNEXPECTED_CONTENT_TYPE", async () => {
    const { app, fetchMock } = await freshApp();
    fetchMock
      .mockResolvedValueOnce(jsonResponse(fakeTokenPayload()))
      .mockResolvedValueOnce(jsonResponse({ unexpected: "shape" }));

    const res = await request(app).get(`/api/touchless/documents/${KNOWN_DOCUMENT_ID}/ocr`);

    expect(res.status).toBe(502);
    expectValidErrorEnvelope(res.body, "UNEXPECTED_CONTENT_TYPE");
  });

  it("rejects a malformed documentId with INVALID_INPUT and never reaches the outbound mock", async () => {
    const { app, fetchMock } = await freshApp();

    const res = await request(app).get(
      `/api/touchless/documents/${encodeURIComponent("../etc/passwd")}/ocr`,
    );

    expect([400, 404]).toContain(res.status);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("never leaks a raw upstream error body or PII into the error envelope's message", async () => {
    const { app, fetchMock } = await freshApp();
    const sensitiveUpstreamBody = { status: 404, borrowerSsn: "123-45-6789" };
    fetchMock
      .mockResolvedValueOnce(jsonResponse(fakeTokenPayload()))
      .mockResolvedValueOnce(jsonResponse(sensitiveUpstreamBody, 404));

    const res = await request(app).get(`/api/touchless/documents/${KNOWN_DOCUMENT_ID}/ocr`);

    expectValidErrorEnvelope(res.body, "NOT_FOUND");
    expectMessageIsSafe(res.body, ["123-45-6789", JSON.stringify(sensitiveUpstreamBody)]);
  });
});
