// routes/applications.ts — POST /api/touchless/applications/:applicationId/pull per plan.md
// §2.6: validate applicationId via touchlessClient.isValidUuid() BEFORE any outbound call,
// call authorizedGet() against /store/application/results/{applicationId}, pass the raw
// application payload through unmodified. Traces to FR-001, FR-002.

import { Router, Request, Response, NextFunction } from "express";
import { authorizedGet, isValidUuid } from "../touchlessClient";
import { ErrorCode, TouchlessProxyError } from "../errors";
import { saveApplication } from "../applicationStore";

export const applicationsRouter = Router();

applicationsRouter.post(
  "/applications/:applicationId/pull",
  async (req: Request, res: Response, next: NextFunction) => {
    try {
      const applicationId = String(req.params.applicationId ?? "");

      // Validate BEFORE any outbound call — assert-order matters (a malformed id must never
      // reach the network, per security-review.md MUST-FIX #3).
      if (!isValidUuid(applicationId)) {
        throw new TouchlessProxyError(
          ErrorCode.INVALID_INPUT,
          "The provided applicationId is not a valid identifier.",
          null,
        );
      }

      const upstreamRes = await authorizedGet(`/store/application/results/${applicationId}`);
      const application = await upstreamRes.json();

      // 021-touchless-audit-run: cache the pulled payload so the audit-run route can
      // evaluate it without a second Touchless call or a request body carrying it back.
      saveApplication(applicationId, application);

      res.status(200).json({
        applicationId,
        fetchedAt: new Date().toISOString(),
        source: "live",
        application,
      });
    } catch (err) {
      next(err);
    }
  },
);
