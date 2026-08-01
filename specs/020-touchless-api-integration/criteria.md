# Success Criteria: Touchless API Integration (020)

Gates each phase 4-8 is looped against (MVP mode, max 5 iterations per phase). Derived from
`spec.md` Success Criteria (SC-001..SC-005), `plan.md`, `security-review.md`, and
`compliance-review.md`.

## Phase 4 (SCAFFOLD) — exit criteria
- [ ] `backend/` builds (`tsc --noEmit` clean) and starts; `GET /api/health` → 200.
- [ ] `frontend/` still builds unchanged (`npm run build` in `frontend/`).
- [ ] `backend/.env` is git-ignored (verify via `git check-ignore -v backend/.env`); no secret
      committed anywhere in the diff.
- [ ] `npm audit --audit-level=high` runs (informational at this stage — doesn't need to be
      clean yet, just wired).

## Phase 5 (TEST — Red) — exit criteria
- [ ] Tests exist for every case in `tasks.md` T009-T012.
- [ ] All new tests FAIL (no implementation yet) — confirms Red, not a false-green from an
      empty/no-op test.
- [ ] 100% of spec Acceptance Scenarios (US1 3 scenarios, US2 3 scenarios, US3 3 scenarios) have
      at least one corresponding test.

## Phase 6 (IMPLEMENT — Green) — exit criteria
- [ ] All Phase 5 tests now PASS.
- [ ] SC-001: pulling a known application populates the loan detail view within 5s (manual/e2e
      timing check against the QA API).
- [ ] SC-002: the retrieved document viewer is visibly distinct from the existing simulated
      `PdfViewerModal` reference (design-review confirms — no shared hardcoded content).
- [ ] SC-003: reaching the Stored/Live toggle takes ≤3 actions from the main screen, and it is
      NOT visible in the primary nav bar (only inside the settings menu).
- [ ] SC-004: 100% of simulated failure modes (kill the mocked upstream, force a 401, force a
      timeout, force a 404, force a non-PDF response) show a distinct visible error — zero
      silent blank/stale-fallback states.
- [ ] SC-005: `grep` sweep (security-review.md §1c) across `frontend/src/` and any built
      `dist/` bundle for `VITE_`+touchless-credential patterns and the literal QA secret/client_id
      strings returns zero matches.
- [ ] FR-010 zero-regression check: no diff touches `p0/qc_engine/`, `CheckResult`, or
      `LoanEvaluation` — grep the PR diff for those paths; any match fails this gate.

## Phase 7 (REFACTOR) — exit criteria
- [ ] Zero duplicated UUID-validation or error-mapping logic across route files.
- [ ] No dead code / no leftover scaffolding TODOs.
- [ ] All Phase 6 tests still pass after refactor (no regression).

## Phase 8 (VALIDATE) — exit criteria (all four loops must pass; security + compliance are
BLOCKING per this project's regulated profile)
- [ ] **Review**: every FR-001..FR-013 traced to a shipped code path; every SC-001..SC-005
      verified against real running code, not just the plan.
- [ ] **Security**: all 7 MUST-FIX items from `security-review.md` re-verified against actual
      code (not the plan) — untracked-secret fix confirmed still in place, UUID validation
      confirmed present at the single chokepoint, PII-safe logging confirmed by reading the
      actual logger config, dependency audit run for real with a clean (or explicitly
      risk-accepted) result, CORS lock confirmed in `server.ts`.
- [ ] **Compliance**: BLOCKING-2 (storage mechanism is in-memory/sessionStorage, never
      localStorage) and BLOCKING-3 (logging excludes full bodies) re-verified against actual
      shipped code.
- [ ] No BLOCKING or MUST-FIX item from either review remains open without an explicit,
      documented risk-acceptance from the team lead.

## Explicit non-goals for this validation (do not fail the gate on these)
- Full penetration test (MVP tier is dependency-audit-plus-OWASP-light, not a pentest).
- Production credential handling.
- pdf.js/page-level citation fidelity.
- Spot-checking `documentId == indexedDocId` beyond Credit Report (T034 is nice-to-have).
