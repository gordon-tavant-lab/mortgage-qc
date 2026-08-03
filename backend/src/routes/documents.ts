// routes/documents.ts — GET /api/touchless/documents/:documentId (raw PDF bytes, content-type
// verified) and GET /api/touchless/documents/:documentId/ocr (per-field OCR JSON, shape-
// verified, zero-field response treated as UNEXPECTED_CONTENT_TYPE) per plan.md §2.6.
// Traces to FR-006, FR-007, FR-009.

import { Router, Request, Response, NextFunction } from "express";
import { authorizedGet, isValidUuid } from "../touchlessClient";
import { ErrorCode, TouchlessProxyError } from "../errors";

export const documentsRouter = Router();

interface OcrField {
  name: string;
  value: string;
  confidence?: number;
}

/**
 * Touchless's real OCR endpoint returns TWO genuinely different shapes depending on document
 * type -- confirmed live 2026-08-02 against the QA gateway, for the real demo loan's actual
 * 62-document set (a materially different finding from the earlier 2026-08-01 live test, which
 * only exercised documents using shape A):
 *
 *   A) The generic field-list shape (W2, Schedule K-1, Form 1040, ...): a non-empty array of
 *      {name, value, confidence} objects. confidence is passed through exactly as received
 *      (unclamped -- values above 100 are expected, per CLAUDE.md's original live-test finding).
 *
 *   B) A bespoke per-document-type structured shape (Gift Letter, Purchase Agreement, ...): a
 *      single-element array containing ONE flat object whose keys are the document's own named
 *      fields (e.g. Gift Letter's `donorName`/`donorAddress`/...), with NO confidence value at
 *      all. Normalized here into the same {name, value, confidence} shape (name = the field's
 *      own key, value = its stringified value) so the frontend needs only one rendering path --
 *      but confidence is left `undefined` for these, never fabricated to make it look like shape
 *      A's real per-field confidence data.
 *
 * A response matching neither shape (or an empty array) is UNEXPECTED_CONTENT_TYPE, per plan.md
 * §2.6/Edge Cases -- never a successful empty result.
 */
function isFieldListShape(value: unknown): value is OcrField[] {
  if (!Array.isArray(value) || value.length === 0) return false;
  return value.every(
    (item) =>
      typeof item === "object" &&
      item !== null &&
      typeof (item as Record<string, unknown>).name === "string" &&
      typeof (item as Record<string, unknown>).value === "string",
  );
}

function isFlatStructuredObjectShape(value: unknown): value is [Record<string, unknown>] {
  if (!Array.isArray(value) || value.length !== 1) return false;
  const [obj] = value;
  if (typeof obj !== "object" || obj === null || Array.isArray(obj)) return false;
  const entries = Object.entries(obj as Record<string, unknown>);
  return (
    entries.length > 0 &&
    entries.every(([, v]) => v === null || typeof v === "string" || typeof v === "number" || typeof v === "boolean")
  );
}

function normalizeOcrResponse(value: unknown): OcrField[] | null {
  if (isFieldListShape(value)) return value;
  if (isFlatStructuredObjectShape(value)) {
    const [obj] = value;
    return Object.entries(obj).map(([name, v]) => ({ name, value: v === null ? "" : String(v) }));
  }
  return null;
}

documentsRouter.get(
  "/documents/:documentId",
  async (req: Request, res: Response, next: NextFunction) => {
    try {
      const documentId = String(req.params.documentId ?? "");

      if (!isValidUuid(documentId)) {
        throw new TouchlessProxyError(
          ErrorCode.INVALID_INPUT,
          "The provided documentId is not a valid identifier.",
          null,
        );
      }

      const upstreamRes = await authorizedGet(`/store/documents/read/${documentId}`, {
        expectedContentType: "application/pdf",
      });
      const arrayBuffer = await upstreamRes.arrayBuffer();

      res.status(200);
      res.setHeader("Content-Type", "application/pdf");
      res.send(Buffer.from(arrayBuffer));
    } catch (err) {
      next(err);
    }
  },
);

documentsRouter.get(
  "/documents/:documentId/ocr",
  async (req: Request, res: Response, next: NextFunction) => {
    try {
      const documentId = String(req.params.documentId ?? "");

      if (!isValidUuid(documentId)) {
        throw new TouchlessProxyError(
          ErrorCode.INVALID_INPUT,
          "The provided documentId is not a valid identifier.",
          null,
        );
      }

      // No `expectedContentType` gate here: Touchless's real /ocr endpoint mislabels its
      // response as `Content-Type: text/plain` even though the body is JSON -- verified
      // live 2026-08-01 against the QA gateway (output/TOUCHLESS-API-LIVE-TEST-2026-08-01.md).
      // Enforcing "application/json" here rejected every real response. Shape validation
      // below (normalizeOcrResponse) is the real correctness gate for this endpoint instead.
      const upstreamRes = await authorizedGet(`/store/documents/read/${documentId}/ocr`);

      // Touchless's real OCR response is a BARE top-level JSON array (not wrapped in a
      // `{fields: [...]}` envelope) -- verified live against the QA gateway. Its shape
      // depends on document type: see normalizeOcrResponse()'s own docstring for the two
      // real shapes (generic field-list vs. per-document-type flat structured object,
      // found live 2026-08-02 while clicking through the real demo loan's Gift Letter and
      // Purchase Agreement citations -- the original 2026-08-01 live test only happened to
      // exercise document types using the field-list shape).
      let body: unknown;
      try {
        body = await upstreamRes.json();
      } catch {
        throw new TouchlessProxyError(
          ErrorCode.UNEXPECTED_CONTENT_TYPE,
          "The OCR response body could not be parsed as JSON.",
          null,
        );
      }

      const fields = normalizeOcrResponse(body);
      if (!fields) {
        throw new TouchlessProxyError(
          ErrorCode.UNEXPECTED_CONTENT_TYPE,
          "The OCR response did not contain the expected field data.",
          null,
        );
      }

      res.status(200).json({
        documentId,
        fetchedAt: new Date().toISOString(),
        fields,
      });
    } catch (err) {
      next(err);
    }
  },
);
