// routes/health.ts — GET /api/health liveness check, no auth. Used by local dev and any
// future deploy healthcheck (plan.md §2.6).

import { Router, Request, Response } from "express";

export const healthRouter = Router();

healthRouter.get("/health", (_req: Request, res: Response) => {
  res.status(200).json({ status: "ok" });
});
