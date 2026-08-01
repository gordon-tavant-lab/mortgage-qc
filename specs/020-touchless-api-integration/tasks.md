# Tasks: Touchless API Integration (Pull Application + Document Citation Retrieval)

Source: `spec.md` (locked) + `plan.md` (locked architecture) + `security-review.md` +
`compliance-review.md`. Mode: MVP. Every task traces to a spec FR or a MUST-FIX/BLOCKING
review item — see the "Traces to" tag on each.

## Phase 0 — Repo hygiene (fix now, independent of build; already done by team-lead 2026-08-01)

- T000: [DONE] Scrub cleartext `client_secret` from
  `docs/architecture/api/TLP-QA-QC-Creds.postman_environment`, add `*.postman_environment` to
  root `.gitignore`. Traces to: security-review.md MUST-FIX #1, compliance-review.md BLOCKING-1.

## Phase 4 — SCAFFOLD (backend proxy skeleton + CI)

- T001: Scaffold `backend/` (Node/Express 5 + TypeScript) per `plan.md` §3 file layout —
  `package.json`, `tsconfig.json`, `.env.example` (placeholder values only), `README.md`.
- T002: `backend/.env` (gitignored, not committed) populated with the real QA credentials
  (`TOUCHLESS_CLIENT_ID=<REDACTED-QA-CLIENT-ID>`, `TOUCHLESS_CLIENT_SECRET=<real QA secret>`,
  `TOUCHLESS_BASE_URL=https://qa-touchless.tavant.com`) for local/demo runs only.
- T003: `server.ts` bootstrap — CORS locked to frontend origin only, JSON parsing, route
  mounting, central error middleware. Traces to: security-review.md MUST-FIX #6.
- T004: `config.ts` — fail-fast startup if any required env var is missing.
- T005: `GET /api/health` liveness route.
- T006: `vite.config.ts` — add `server.proxy` for `/api` → backend dev port (same-origin in dev).
- T007: Add `npm audit --audit-level=high` to `backend/package.json` scripts + CI/scaffold
  check. Traces to: security-review.md MUST-FIX #7.
- T008: Scaffold criteria: `npm run build` (frontend) and `npm run build`/`tsc --noEmit`
  (backend) both succeed; `GET /api/health` returns 200; CI green.

## Phase 5 — TEST, Red (write before implementation, expect failing)

- T009: Backend unit tests (mocked Touchless HTTP calls — never a real secret in test
  fixtures, per security-review.md §1b) for: token acquisition + caching, single-retry-on-401
  then `AUTH_FAILURE`, UUID validation rejecting malformed IDs with `INVALID_INPUT`,
  `NOT_FOUND` passthrough, `TIMEOUT` on a simulated slow upstream, `UNEXPECTED_CONTENT_TYPE`
  on a non-PDF/non-JSON response and on zero-field OCR responses.
- T010: Backend integration test: `POST /api/touchless/applications/:id/pull` happy path
  against a mocked upstream, and each error code returns the exact JSON envelope shape from
  plan.md §2.5.
- T011: Frontend unit tests for `dataSourceContext.tsx` — toggle defaults to "stored", fetch-once
  caching (second call for the same ID does not re-fetch), re-pull clears just that one key.
- T012: Frontend component tests: `PullApplicationButton` idle/loading/cached/error states;
  `RetrievedDocumentViewer` renders distinct error states per error code (not a blank screen).
  Traces to: FR-012, SC-004.
- T013: Confirm all of T009-T012 FAIL (no implementation exists yet) — Red confirmed.

## Phase 6 — IMPLEMENT, Green

### Backend (implementer: backend stream)
- T014: `tokenCache.ts` + `touchlessClient.ts` (UUID allowlist, fixed base host, single-retry-on-401).
  Traces to: FR-007, security-review.md MUST-FIX #3 and #5.
- T015: `errors.ts` (ErrorCode enum + envelope) + `middleware/errorHandler.ts`.
- T016: `routes/applications.ts` — `POST /api/touchless/applications/:applicationId/pull`.
  Traces to: FR-001, FR-002.
- T017: `routes/documents.ts` — `GET /api/touchless/documents/:documentId` (+ `/ocr`).
  Traces to: FR-006, FR-007, FR-009.
- T018: `middleware/requestLogger.ts` — metadata-only (method, path template, status, latency,
  requestId), never full bodies. Traces to: security-review.md MUST-FIX #4,
  compliance-review.md BLOCKING-3.
- T019: Run the `grep` verification from security-review.md §1c across `frontend/` (zero
  `VITE_`-prefixed Touchless references, zero copy-pasted secret strings), plus a sweep of the
  diff for `p0/qc_engine/`, `CheckResult`, and `LoanEvaluation` references (must be zero).
  Traces to: SC-005, FR-010.

### Frontend (implementer: frontend stream, coordinate with design skill for UI)
- T020: `lib/touchlessApi.ts` — fetch wrappers, parse error envelope.
- T021: `lib/dataSourceContext.tsx` — `DataSourceProvider`/`useDataSource()`, in-memory only
  (never `localStorage`; `sessionStorage` acceptable per plan.md §2.3 but in-memory chosen).
  Traces to: FR-003, FR-004, FR-005, FR-013, security/compliance BLOCKING-2.
- T022: `components/SettingsMenu.tsx` + `DataSourceToggle.tsx` — tucked in `Navbar.tsx`, not a
  4th main nav tab. Traces to: FR-003, SC-003.
- T023: `components/PullApplicationButton.tsx` on `LoanDetail`. Traces to: FR-001, SC-001.
- T024: `components/LiveApplicationPanel.tsx` — lists pulled `documents[]`.
- T025: `components/RetrievedDocumentViewer.tsx` — Blob/ObjectURL `<iframe>` + OCR fields table,
  distinct error states. Do NOT revoke the ObjectURL on modal close — see plan.md §2.2 (would break
  the fetch-once-per-session cache from T021); no explicit revocation needed this pass.
  Traces to: FR-006, FR-008, FR-009, SC-002.
- T026: Extend `SampleDataBanner.tsx` → `DataSourceBanner.tsx` (Stored/Live indicator).
  Traces to: FR-011.
- T027: Invoke `g-create-design --mode frontend` (or equivalent design-review pass) against
  `output/DEMO-UX-LESSONS.md` before calling the UI done — confirm no pass/fail/checkmark
  visual language on pulled/citation content (compliance-review.md's UI-presentation note).
- T028: Confirm T009-T012 now PASS (Green).

## Phase 7 — REFACTOR

- T029: Consistency pass — naming, dead code, duplicate error-handling logic consolidated into
  `touchlessClient.ts`'s single chokepoint (security-review.md open item #4/plan.md §6.4).
- T030: Confirm the UUID-validation chokepoint is not duplicated/forgotten in either route file.

## Phase 8 — VALIDATE (parallel loops)

- T031: `reviewer` — spec compliance pass against every FR-001..FR-013 and SC-001..SC-005.
- T032: `security` — MVP-light re-verification of all 7 MUST-FIX items now that code exists;
  dependency audit run for real; Vite-bundle grep run for real.
- T033: `compliance` — re-verify BLOCKING-2 (storage mechanism) and BLOCKING-3 (logging) against
  actual shipped code, not just the plan's stated intent.
- T034 (optional, nice-to-have, non-blocking): spot-check `documentId == indexedDocId` against
  2-3 more Touchless document types beyond Credit Report.

## Phase 9: Convergence

- [ ] T035 Manually verify all three user stories in a live browser session with both dev
  servers running — pull the known application, open a citation's real document, toggle
  Stored↔Live — per CLAUDE.md's UI-verification mandate (missing)
- [X] T036 Run the T027 design-review pass (`g-create-design --mode frontend` or equivalent)
  against `output/DEMO-UX-LESSONS.md`; no evidence it has run yet per FR-011 (missing) —
  DONE 2026-08-01: reviewed all 6 new components against DEMO-UX-LESSONS.md §1/§5 directly.
  Clean: no pass/fail/checkmark visual language, honest Stored/Live provenance banners
  (extends the "sim badge" pattern), progressive disclosure on the documents list, no
  fabricated citations. No code changes needed.
- [X] T037 Convert the T019 grep verification (credential-leak sweep + FR-010's
  `p0/qc_engine`/`CheckResult`/`LoanEvaluation` zero-regression sweep) from a one-time manual
  check into a committed script or CI step per SC-005, FR-010 (partial) —
  DONE 2026-08-01: `backend/scripts/verify-no-leaks.sh`, wired as `npm run verify:no-leaks`,
  both greps automated and negative-tested (confirmed it actually fails on a real violation).
  Found and fixed a real regression while writing this: the `.gitignore` `src/` rule from the
  earlier Phase 8 fix was unanchored and had silently hidden all of `backend/src/` from git
  entirely (untracked, invisible to `git add`) — changed to `/src/` so it stays scoped to the
  top-level Python sandbox only.

## Phase 10: Convergence

- [ ] T038 Manually verify all three user stories (US1/AC1, US2/AC1, US3/AC1) in a live
  browser session — same underlying gap as T035, carried forward because the blocker changed:
  the stale chrome-devtools-mcp lock was cleared, but this session's own browser-tool
  connection dropped as a side effect and has not reconnected. Achievable via a fresh session
  or manual click-through against `npm run dev` in both `backend/` and `frontend/` (missing)

## Explicitly out of scope (do not create tasks for these)

- Any change to `p0/qc_engine`, `CheckResult`, or `LoanEvaluation`.
- MISMO XML retrieval.
- Production credential provisioning/rotation.
- Any new database or on-disk cache.
- Per-loan or loan-detail-page toggle placement.
- pdf.js integration / page-level deep-linking.
