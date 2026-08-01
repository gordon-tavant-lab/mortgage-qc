// server.ts — Express app bootstrap (plan.md §3): CORS locked to the frontend's own
// origin, JSON body parsing, route mounting, and a central error-handling middleware.
// Real proxy logic (OAuth, forwarding, error mapping) is Phase 6 — this file only wires
// the shape so Phase 6 implementers can slot handlers into an already-running skeleton.

import express, { Express, Request, Response, NextFunction } from "express";
import { config } from "./config";
import { healthRouter } from "./routes/health";
import { applicationsRouter } from "./routes/applications";
import { documentsRouter } from "./routes/documents";
import { requestLogger } from "./middleware/requestLogger";
import { errorHandler } from "./middleware/errorHandler";

// Locked to the frontend's own dev origin (frontend/vite.config.ts server.port).
// In dev, Vite's own server.proxy keeps requests same-origin from the browser's
// perspective, so this CORS lock is a defense-in-depth backstop, not the primary
// same-origin mechanism (security-review.md §5.1).
const FRONTEND_ORIGIN = "http://localhost:3000";

export function createApp(): Express {
  const app = express();

  app.use((req: Request, res: Response, next: NextFunction) => {
    res.setHeader("Access-Control-Allow-Origin", FRONTEND_ORIGIN);
    res.setHeader("Vary", "Origin");
    res.setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
    res.setHeader("Access-Control-Allow-Headers", "Content-Type");
    if (req.method === "OPTIONS") {
      res.sendStatus(204);
      return;
    }
    next();
  });

  app.use(express.json());
  app.use(requestLogger);

  // Route mounting.
  app.use("/api", healthRouter);
  app.use("/api/touchless", applicationsRouter);
  app.use("/api/touchless", documentsRouter);

  // Central error-handling middleware — must be mounted last.
  app.use(errorHandler);

  return app;
}

if (require.main === module) {
  const app = createApp();
  app.listen(config.port, () => {
    // eslint-disable-next-line no-console
    console.log(`backend listening on http://localhost:${config.port}`);
  });
}
