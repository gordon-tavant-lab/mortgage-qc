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
  confidence: number;
}

/**
 * A valid OCR response is a non-empty array of {name, value, confidence} objects. Per plan.md
 * §2.6/Edge Cases, a zero-field array or any other shape is treated as UNEXPECTED_CONTENT_TYPE
 * — never a successful empty result. Confidence is passed through exactly as received
 * (unclamped, unnormalized — values above 100 are expected, per CLAUDE.md's live-test finding).
 */
function isValidOcrFields(value: unknown): value is OcrField[] {
  if (!Array.isArray(value) || value.length === 0) return false;
  return value.every(
    (item) =>
      typeof item === "object" &&
      item !== null &&
      typeof (item as Record<string, unknown>).name === "string" &&
      typeof (item as Record<string, unknown>).value === "string" &&
      typeof (item as Record<string, unknown>).confidence === "number",
  );
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
      // below (isValidOcrFields) is the real correctness gate for this endpoint instead.
      const upstreamRes = await authorizedGet(`/store/documents/read/${documentId}/ocr`);

      // Touchless's real OCR response is a BARE top-level JSON array of
      // {name, value, confidence} objects -- verified live against the QA gateway,
      // see output/TOUCHLESS-API-LIVE-TEST-2026-08-01.md. It is NOT wrapped in a
      // `{fields: [...]}` envelope; an earlier version of this route assumed that
      // wrapping and would have thrown UNEXPECTED_CONTENT_TYPE on every real call.
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

      if (!isValidOcrFields(body)) {
        throw new TouchlessProxyError(
          ErrorCode.UNEXPECTED_CONTENT_TYPE,
          "The OCR response did not contain the expected field data.",
          null,
        );
      }

      res.status(200).json({
        documentId,
        fetchedAt: new Date().toISOString(),
        fields: body,
      });
    } catch (err) {
      next(err);
    }
  },
);
