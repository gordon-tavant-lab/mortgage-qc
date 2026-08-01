// middleware/errorHandler.ts — central Express 5 error-handling middleware: map a
// TouchlessProxyError's ErrorCode (see errors.ts) to the JSON envelope + HTTP status from
// plan.md §2.5, and fall back to a generic PROXY_ERROR (500) for anything unrecognized.
// Mounted last in server.ts so Express 5's auto-forwarded rejected-promise errors land here
// too.

import { Request, Response, NextFunction } from "express";
import { statusForErrorCode, toErrorEnvelope } from "../errors";

export function errorHandler(
  err: unknown,
  req: Request,
  res: Response,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  _next: NextFunction,
): void {
  const requestId = req.requestId ?? "unknown";
  const envelope = toErrorEnvelope(err, requestId);
  res.status(statusForErrorCode(envelope.error.code)).json(envelope);
}
