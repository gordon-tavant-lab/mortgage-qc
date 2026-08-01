// middleware/requestLogger.ts — metadata-only request logging (method, path template, status,
// latency, requestId) — NEVER request/response bodies, per security-review.md §3.1/§3.4 (PII
// must never appear in logs).

import { randomUUID } from "crypto";
import { Request, Response, NextFunction } from "express";

declare module "express-serve-static-core" {
  interface Request {
    /** Short correlation id, generated per-request, echoed in the §2.5 error envelope. */
    requestId?: string;
  }
}

export function requestLogger(req: Request, res: Response, next: NextFunction): void {
  const requestId = randomUUID().split("-")[0];
  req.requestId = requestId;
  const startedAt = Date.now();

  res.on("finish", () => {
    // Metadata only: method, route path *template* when Express matched one (never the raw
    // path with real ID substituted in, per security-review.md §3.1's pattern discipline),
    // status code, latency, and the correlation id. Never the request/response body.
    const pathTemplate = req.route ? `${req.baseUrl}${req.route.path}` : req.path;
    // eslint-disable-next-line no-console
    console.log(
      JSON.stringify({
        method: req.method,
        path: pathTemplate,
        status: res.statusCode,
        latencyMs: Date.now() - startedAt,
        requestId,
      }),
    );
  });

  next();
}
