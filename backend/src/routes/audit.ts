// routes/audit.ts — 021-touchless-audit-run: POST /api/audit/:applicationId/run
// Triggers a real deterministic-engine evaluation of an already-pulled application. Reuses
// 020's isValidUuid() guard and ErrorEnvelope/ErrorCode shape (contracts/audit-run.md) rather
// than inventing a parallel error format. Invokes the engine/ pipeline (compiler + adapter +
// engine.run()) via a single Python subprocess (research.md Item 5) — no engine logic runs in
// this process or in the browser (constitution Principle II).
//
// live-demo-engine-wiring: rewired from p0/qc_engine/run_touchless_audit_for_demo.py to
// engine/qc_engine/run_touchless_audit_for_demo.py — engine/ is the standalone, definitive
// QC audit engine (engine/README.md); p0/ remains the historical/experimental workspace where
// that pipeline was proven out. Same subprocess contract, only the script path changed.

import { execFile } from "child_process";
import { Router, Request, Response, NextFunction } from "express";
import { mkdtemp, rm, writeFile } from "fs/promises";
import { tmpdir } from "os";
import { join } from "path";
import { promisify } from "util";
import { getApplication } from "../applicationStore";
import { ErrorCode, TouchlessProxyError } from "../errors";
import { isValidUuid } from "../touchlessClient";

export const auditRouter = Router();

const execFileAsync = promisify(execFile);

// backend/src/routes -> backend/src -> backend -> mortgage-qc-prod -> p0/qc_engine/...
const AUDIT_SCRIPT_PATH = join(
  __dirname, "..", "..", "..", "engine", "qc_engine", "run_touchless_audit_for_demo.py",
);
// live-demo-engine-wiring (spec014 port): a real, billed Bedrock LLM call -- generated
// on demand only (a button), never fired automatically alongside the deterministic
// audit run above.
const NARRATIVE_SCRIPT_PATH = join(
  __dirname, "..", "..", "..", "engine", "qc_engine", "run_decision_narrative_for_demo.py",
);
const SUBPROCESS_TIMEOUT_MS = 30_000;
const NARRATIVE_SUBPROCESS_TIMEOUT_MS = 60_000;

interface AuditScriptOutput {
  loanStatus: string;
  compiledCheckCount: number;
  excludedCheckCount: number;
  runResult: unknown;
}

function isValidAuditScriptOutput(value: unknown): value is AuditScriptOutput {
  if (typeof value !== "object" || value === null) return false;
  const v = value as Record<string, unknown>;
  return (
    typeof v.loanStatus === "string" &&
    typeof v.compiledCheckCount === "number" &&
    typeof v.excludedCheckCount === "number" &&
    v.runResult !== undefined
  );
}

interface NarrativeScriptOutput {
  loan_id: string;
  disposition: string;
  review_reasons: string[];
  narrative_text: string | null;
  referenced_check_ids: string[];
  referenced_guide_citations: string[];
  generated_at: string;
  model: string;
  validation_attempts: number;
}

function isValidNarrativeScriptOutput(value: unknown): value is NarrativeScriptOutput {
  if (typeof value !== "object" || value === null) return false;
  const v = value as Record<string, unknown>;
  return (
    typeof v.loan_id === "string" &&
    typeof v.disposition === "string" &&
    Array.isArray(v.review_reasons) &&
    (v.narrative_text === null || typeof v.narrative_text === "string") &&
    Array.isArray(v.referenced_check_ids) &&
    Array.isArray(v.referenced_guide_citations)
  );
}

auditRouter.post(
  "/audit/:applicationId/run",
  async (req: Request, res: Response, next: NextFunction) => {
    let tmpDir: string | undefined;
    try {
      const applicationId = String(req.params.applicationId ?? "");

      if (!isValidUuid(applicationId)) {
        throw new TouchlessProxyError(
          ErrorCode.INVALID_INPUT,
          "The provided applicationId is not a valid identifier.",
          null,
        );
      }

      const application = getApplication(applicationId);
      if (application === undefined) {
        throw new TouchlessProxyError(
          ErrorCode.NOT_FOUND,
          "No application has been pulled for this applicationId this session.",
          null,
        );
      }

      tmpDir = await mkdtemp(join(tmpdir(), "audit021-"));
      const loanPath = join(tmpDir, "loan_application.json");
      await writeFile(loanPath, JSON.stringify(application));

      // live-demo-engine-wiring: real wall-clock time of the actual engine subprocess
      // (compile ruleset + adapt loan + run every check) -- never a fabricated/estimated
      // figure, measured around the same execFile call the response is built from.
      const startedAt = Date.now();
      let stdout: string;
      try {
        const result = await execFileAsync(
          "python3",
          [AUDIT_SCRIPT_PATH, "--loan", loanPath],
          { timeout: SUBPROCESS_TIMEOUT_MS },
        );
        stdout = result.stdout;
      } catch (subprocessErr) {
        throw new TouchlessProxyError(
          ErrorCode.PROXY_ERROR,
          `The audit-run subprocess failed: ${(subprocessErr as Error).message}`,
          null,
        );
      }

      let parsed: unknown;
      try {
        parsed = JSON.parse(stdout);
      } catch {
        throw new TouchlessProxyError(
          ErrorCode.PROXY_ERROR,
          "The audit-run subprocess produced unparseable output.",
          null,
        );
      }

      if (!isValidAuditScriptOutput(parsed)) {
        throw new TouchlessProxyError(
          ErrorCode.PROXY_ERROR,
          "The audit-run subprocess produced output in an unexpected shape.",
          null,
        );
      }

      res.status(200).json({
        applicationId,
        evaluatedAt: new Date().toISOString(),
        durationMs: Date.now() - startedAt,
        loanStatus: parsed.loanStatus,
        compiledCheckCount: parsed.compiledCheckCount,
        excludedCheckCount: parsed.excludedCheckCount,
        runResult: parsed.runResult,
      });
    } catch (err) {
      next(err);
    } finally {
      if (tmpDir) {
        await rm(tmpDir, { recursive: true, force: true });
      }
    }
  },
);

// live-demo-engine-wiring (spec014): POST /api/audit/:applicationId/narrative -- generates
// the decision narrative for an already-pulled, already-real loan. On-demand only (a real
// Bedrock LLM call, real cost) -- never fired automatically by the audit run above.
auditRouter.post(
  "/audit/:applicationId/narrative",
  async (req: Request, res: Response, next: NextFunction) => {
    let tmpDir: string | undefined;
    try {
      const applicationId = String(req.params.applicationId ?? "");

      if (!isValidUuid(applicationId)) {
        throw new TouchlessProxyError(
          ErrorCode.INVALID_INPUT,
          "The provided applicationId is not a valid identifier.",
          null,
        );
      }

      const application = getApplication(applicationId);
      if (application === undefined) {
        throw new TouchlessProxyError(
          ErrorCode.NOT_FOUND,
          "No application has been pulled for this applicationId this session.",
          null,
        );
      }

      tmpDir = await mkdtemp(join(tmpdir(), "narrative021-"));
      const loanPath = join(tmpDir, "loan_application.json");
      await writeFile(loanPath, JSON.stringify(application));

      let stdout: string;
      try {
        const result = await execFileAsync(
          "python3",
          [NARRATIVE_SCRIPT_PATH, "--loan", loanPath],
          { timeout: NARRATIVE_SUBPROCESS_TIMEOUT_MS },
        );
        stdout = result.stdout;
      } catch (subprocessErr) {
        throw new TouchlessProxyError(
          ErrorCode.PROXY_ERROR,
          `The decision-narrative subprocess failed: ${(subprocessErr as Error).message}`,
          null,
        );
      }

      let parsed: unknown;
      try {
        parsed = JSON.parse(stdout);
      } catch {
        throw new TouchlessProxyError(
          ErrorCode.PROXY_ERROR,
          "The decision-narrative subprocess produced unparseable output.",
          null,
        );
      }

      if (!isValidNarrativeScriptOutput(parsed)) {
        throw new TouchlessProxyError(
          ErrorCode.PROXY_ERROR,
          "The decision-narrative subprocess produced output in an unexpected shape.",
          null,
        );
      }

      res.status(200).json({
        applicationId,
        generatedAt: parsed.generated_at,
        disposition: parsed.disposition,
        reviewReasons: parsed.review_reasons,
        narrativeText: parsed.narrative_text,
        referencedCheckIds: parsed.referenced_check_ids,
        referencedGuideCitations: parsed.referenced_guide_citations,
        model: parsed.model,
        validationAttempts: parsed.validation_attempts,
      });
    } catch (err) {
      next(err);
    } finally {
      if (tmpDir) {
        await rm(tmpDir, { recursive: true, force: true });
      }
    }
  },
);
