# Review: Touchless API Integration (020) — Phase 7 (REFACTOR) + Phase 8 (VALIDATE)

Reviewer: `reviewer` agent. Read-only pass against `spec.md`, `plan.md`, `tasks.md`, `criteria.md`.
Verified by running the actual test suites and builds, not just reading code.

**Verified independently, this pass:**
- Backend: `npx vitest run` → 5 test files, **41/41 passed**. `npx tsc --noEmit` → clean.
- Frontend: `npx vitest run` → 3 test files, **21/21 passed**.
- Both `npm run build` succeed (frontend Vite build + backend `tsc -p tsconfig.json`).
- `npm run audit` (`npm audit --audit-level=high`) on `backend/` → **0 vulnerabilities**.
- `grep -rn "VITE_" frontend/src/ | grep -i "touchless|client_secret|client_id|bearer"` → **0 matches**.
- `grep -rn "<REDACTED-QA-SECRET>|<REDACTED-QA-CLIENT-ID>" frontend/src/ frontend/dist/` (real QA secret + client_id, against
  built bundle, not just source) → **0 matches**.
- `git check-ignore -v backend/.env` → matched by `.gitignore:34:.env` — confirmed ignored.
- `docs/architecture/api/TLP-QA-QC-Creds.postman_environment`'s `client_secret` value in the current
  working tree is a redaction placeholder, not the real value.

---

## Part A: Refactor check (Phase 7, T029–T030) — **PASS**

1. **UUID validation chokepoint** — confirmed single: `isValidUuid()` lives only in
   `backend/src/touchlessClient.ts:15-18`. Both `backend/src/routes/applications.ts:20` and
   `backend/src/routes/documents.ts:42,70` import and call it; neither route re-implements or
   duplicates the regex/logic. `backend/src/__tests__/touchlessClient.test.ts` unit-tests it in
   isolation (malformed/path-traversal/SQL-injection/URL-shaped/trailing-junk cases).
2. **No dead code / no stub text** — `grep -rniE "TODO|FIXME|not implemented|stub"` across every
   shipped implementation file listed in the task brief returned **zero matches**. (Test-file
   comments referencing the *original* Red-phase stub text, e.g. touchlessClient.test.ts's header
   comment, are historical narration of Phase 5 and don't reflect current shipped behavior — not a
   finding.)
3. **Error-envelope construction funnels through one place** — `errors.ts`'s `toErrorEnvelope()` is
   the only place that builds the `{error: {...}}` shape; `middleware/errorHandler.ts:18-19` is the
   only call site that serializes it onto the HTTP response. Neither `routes/applications.ts` nor
   `routes/documents.ts` constructs an envelope ad hoc — both only `throw new TouchlessProxyError(...)`
   and let `next(err)` carry it to the central handler.

No findings for Part A.

---

## Part B: Spec-compliance review (Phase 8) — **PASS-WITH-FINDINGS**

One finding below is severe enough that I'm not calling this a clean PASS even though every FR/SC
traces to shipped, tested code.

### FR-001–FR-013 traceability

| FR | Shipped at | Verdict |
|---|---|---|
| FR-001 (button-triggered pull, routed through proxy) | `frontend/src/components/PullApplicationButton.tsx:20-27` → `dataSourceContext.tsx:89-136` → `touchlessApi.ts:73-81` → `POST /api/touchless/applications/:id/pull` (`backend/src/routes/applications.ts:12-41`) | Met |
| FR-002 (creds server-side only) | `backend/src/config.ts` reads `process.env`; `tokenCache.ts:30-32` builds Basic auth server-side; browser code (`touchlessApi.ts`) never references a credential | Met — see SC-005 verification above |
| FR-003 (single session-wide toggle, tucked in nav) | `DataSourceToggle.tsx` inside `SettingsMenu.tsx`, wired into `Navbar.tsx:44,65` **outside** `NAV_ITEMS` | Met |
| FR-004 (session-only, resets on new session, no URL encoding) | `dataSourceContext.tsx:71` — plain `useState`, no storage API, no router/URL touch anywhere in the diff | Met |
| FR-005 (fetch-once, explicit re-pull only) | `pullApplication()` short-circuits on `pulledApplications.has(id)` unless `force:true` (`dataSourceContext.tsx:90-95`); `PullApplicationButton.tsx:22-26` only passes `force:true` on explicit re-click | Met |
| FR-006 (document retrieval via citation) | `LiveApplicationPanel.tsx:129-135` "View Document" → `RetrievedDocumentViewer` keyed on `documentId` → `GET /api/touchless/documents/:documentId(+/ocr)` | Met |
| FR-007 (`documentId` as direct lookup key) | `backend/src/routes/documents.ts:50,78` — path param used directly against `/store/documents/read/{documentId}` | Met (per spec's own "verified for one type" caveat) |
| FR-008 (real retrieved content, visibly distinct) | `RetrievedDocumentViewer.tsx:82-86` — Blob→ObjectURL `<iframe>`; test at `RetrievedDocumentViewer.test.tsx:86` asserts absence of the word "placeholder" | Met |
| FR-009 (extracted fields alongside doc view) | `documents.ts:78-95` returns `{name,value,confidence}[]`; rendered in `RetrievedDocumentViewer.tsx:96-117` | Met |
| FR-010 (display/citation-only, no QC engine feed) | See dedicated verification below | Met |
| FR-011 (Stored vs Live clearly indicated) | `DataSourceBanner.tsx` | Met — see dedicated verification below |
| FR-012 (clear, non-crashing error, no silent fixture substitution) | Every fetch path (`dataSourceContext.tsx:120-133`, `164-173`) catches into a per-key error map, never falls back to writing fixture/stale data into the same cache slot | Met |
| FR-013 (no new persistent storage) | `grep` for `writeFile|fs.write|sqlite|mongodb|localStorage|sessionStorage` across all new backend + `dataSourceContext.tsx`/`touchlessApi.ts` → only match is a **comment** stating storage is deliberately *not* used | Met |

### FR-010 deep check (explicitly requested)

`grep -rn "p0/qc_engine|CheckResult|LoanEvaluation"` across every new/changed file in this feature
(`backend/src/**`, `frontend/src/lib/touchlessApi.ts`, `dataSourceContext.tsx`, and all six new
components) → **zero matches**. `git diff frontend/src/lib/types.ts` is exactly one additive
`applicationId?: string` field (7 diff lines total, all additions/comment) — `CheckResult`,
`SourceCitation`, and the existing `Finding.citation` shape are untouched. `git diff --stat
frontend/src/components/SourceCitation.tsx` produced no output — confirmed byte-for-byte unchanged.

### FR-011 / DataSourceBanner.tsx

Read in full (`frontend/src/components/DataSourceBanner.tsx`). Stored mode renders a purple/amber
banner ("Stored (sample data) — every number on this screen is sample data..."); Live mode renders a
visually distinct blue banner with either "Live — pulled at HH:MM:SS" or a prompt to pull if nothing's
been fetched yet this session (correctly handles spec Edge Case #2). Confirmed distinct icon
(`FlaskConical` vs `Radio`) and color treatment — not just a label swap. Met.

**Minor deviation from plan.md, not a defect**: plan.md §3 described this as "(extend) SampleDataBanner.tsx
→ renamed/extended DataSourceBanner.tsx", implying an in-place rename. The implementer instead left
`SampleDataBanner.tsx` in place (still used by `RoutesFlow.tsx`, `ImportAndSignView.tsx`,
`LoanQueue.tsx` — screens that never show pulled data and don't need FR-011's distinction) and added
`DataSourceBanner.tsx` as a new, separate component used only by `LoanDetail.tsx`. This is arguably the
*more correct* reading of FR-011 ("wherever pulled data is shown" — not every screen), but flagging
since it diverges from the plan's literal wording. No action needed unless the plan should be corrected
to match.

### FR-012 / SC-004 — RetrievedDocumentViewer error states

Confirmed **6 genuinely distinct** error states, not one generic string reused: `ERROR_COPY` in
`RetrievedDocumentViewer.tsx:15-23` pairs a distinct icon + title per code (`ShieldAlert`/"Authentication
Failed", `SearchX`/"Document Not Found", `Clock`/"Request Timed Out", `FileQuestion`/"Unexpected
Content", `ServerCrash`/"Touchless Error", `Bug`/"Proxy Error") plus a distinct `data-testid`
(`document-error-<CODE>`) per code. `INVALID_INPUT` is deliberately excluded with a documented reason
(a citation's `documentId` always comes from an already-pulled, already-validated list — not a
realistic viewer-level state) — a defensible, explicit scope call, not an oversight.
`RetrievedDocumentViewer.test.tsx:105-122` asserts all 6 testids are pairwise unique. Met.

### SC-001 (5s pull latency)

Not independently re-timed against the live QA gateway in this pass (would require live network
access I didn't exercise). Code path has no artificial delay and a `REQUEST_TIMEOUT_MS=10000` ceiling
— reasonable to trust for a demo/QA-tier endpoint, but this SC is unverified by me beyond code
inspection. Recommend an actual stopwatch check against the real `qa-touchless.tavant.com` endpoint
before relying on this number in a live demo.

### SC-002 (visibly distinct from simulated viewer)

Verified via the passing test asserting absence of the word "placeholder" plus a real `<iframe>` +
fields table render. Met.

### SC-003 (toggle reachable in ≤3 actions, not in primary nav)

`Navbar.tsx`'s `NAV_ITEMS` array (`Navbar.tsx:5-38`) contains exactly the 4 pre-existing tabs
(`ShieldCheck`/`ListChecks`/`FileSpreadsheet`/`GitFork`/`CheckCircle2` icons) — `SettingsMenu` is
rendered as a sibling `<div>` (`Navbar.tsx:65`), never added to `NAV_ITEMS`. Reachability: click gear
icon → click Stored/Live button = **2 actions**, under the ≤3 budget. Met.

### SC-005 (zero credential exposure) — re-verified against real code and a real build, not just intent

- `grep -rn "VITE_" frontend/src/ | grep -i "touchless|client_secret|client_id|bearer"` → 0 matches.
- `grep -rn "<REDACTED-QA-SECRET>|<REDACTED-QA-CLIENT-ID>"` (the actual `backend/.env` values) across `frontend/src/` **and
  the actual built `frontend/dist/` bundle** → 0 matches.
- `backend/.env` confirmed git-ignored (`git check-ignore -v` → matched `.gitignore:34:.env`).
- `docs/architecture/api/TLP-QA-QC-Creds.postman_environment`'s `client_secret` is a redaction
  placeholder in the current working tree, not the real value.

SC-005 is met for the *frontend/browser* surface this spec targets.

---

## CRITICAL (must fix before merge)

- **[specs/020-touchless-api-integration/security-review.md:47,65,104,290,
  specs/020-touchless-api-integration/compliance-review.md:41,54]** Both review documents contain
  the **real QA credential in cleartext** (`client_secret: <REDACTED-QA-SECRET>`, plus `<REDACTED-QA-CLIENT-ID>`), and both
  files are currently **untracked** (`git status` shows the entire `specs/020-touchless-api-integration/`
  directory as `??` — nothing in it has been committed yet). If these two files are committed as-is
  alongside the rest of this feature (which `tasks.md`/`plan.md` both treat as "already filed"
  companion docs to be kept with the spec), the literal secret string enters git history permanently
  — the exact failure mode T000/security-review.md MUST-FIX #1 was written to prevent for the
  Postman file, just recurring in two sibling markdown files instead. The postman-environment file
  itself was correctly redacted (per T000) — these two were not.
  Suggested fix: redact `<REDACTED-QA-SECRET>`/`<REDACTED-QA-CLIENT-ID>` in both files to the same placeholder pattern used in
  the postman-environment fix (e.g. `<REDACTED — real value in backend/.env>`) before either file is
  `git add`ed. Since neither file is committed yet, this is a same-day fix with zero history
  rewriting required — the cheapest possible time to catch it.

## WARNING (should fix)

- None. (SC-001's 5-second latency claim is unverified rather than wrong — see Part B above; downgraded
  to a note rather than a warning since nothing in the code suggests it would fail, it's just untested
  by me this pass.)

## SUGGESTION (consider improving)

- **[plan.md §3 vs. frontend/src/components/DataSourceBanner.tsx]** Plan describes this as a rename of
  `SampleDataBanner.tsx`; implementation instead added a sibling component and left the original in
  place for its other three call sites. The implementation choice is reasonable (arguably more correct
  than a literal rename would have been), but plan.md's wording should be updated to reflect what was
  actually built, so a future reader doesn't go looking for a rename that didn't happen.
- **[frontend/src/lib/dataSourceContext.tsx:37, `RetrievedDocument.pdfObjectUrl`]** Plan.md §2.2 calls
  for revoking the Blob `ObjectURL` "when the viewer modal closes or the cached document is evicted."
  `RetrievedDocumentViewer.tsx` has no `useEffect` cleanup calling `URL.revokeObjectURL`, and
  `dataSourceContext.tsx` has no eviction path at all (the `Map` only grows for the session). For an
  MVP/single-demo-session this is a non-issue (a handful of documents, short-lived process), but if a
  demo session opens many large PDFs back-to-back it will leak memory slowly, exactly as plan.md's own
  caveat anticipated. Not blocking — flagging so it isn't forgotten before a longer-running demo.

## POSITIVE (good patterns to continue)

- **[backend/src/errors.ts:69-83]** `MESSAGE_BY_CODE` is structurally guaranteed to be the *only*
  source of a client-visible error message — a call site literally cannot leak a raw vendor body or
  PII into the browser by constructing `TouchlessProxyError` with an unsafe string, because
  `toErrorEnvelope()` never reads `.message` off the thrown error. This is a real structural guardrail,
  not just a documented discipline, and it's backed by a test (`applications.route.test.ts:136-150`,
  `documents.route.test.ts:176`) that actually injects a PII-bearing fake upstream body and asserts it
  never surfaces.
- **[backend/src/__tests__/applications.route.test.ts:112-131]** The TIMEOUT test genuinely exercises
  the `AbortController` path with a real hung promise + a real `AbortSignal` listener (not a mocked
  timer), giving actual confidence in the deadline-enforcement code rather than a shortcut string match.
- **[backend/src/touchlessClient.ts:26-35]** The SSRF guard (`buildUrl`) is tested against a URL-shaped
  malicious input (`http://attacker.example.com/...`) and asserted to still resolve against the fixed
  base host — a concrete adversarial test, not just a happy-path check.
- **[frontend/src/components/RetrievedDocumentViewer.tsx + its test file]** Distinct error states are
  verified structurally (unique `data-testid` per code, asserted pairwise-unique in a loop) rather than
  by loose text matching — a genuinely harder-to-regress test design.

---

## Verdicts

- **Part A (Refactor, T029–T030): PASS**
- **Part B (Spec compliance, Phase 8): PASS-WITH-FINDINGS** — one CRITICAL item (cleartext QA secret
  currently sitting in two untracked review docs about to be committed with this feature), two minor
  SUGGESTIONs, zero code-level spec gaps. All FR-001–FR-013 and SC-001–SC-005 trace to real, tested
  code; the one exception (SC-001's 5-second timing) is unverified rather than failing.

---

## Addendum (2026-08-01) — CRITICAL finding re-checked, and two additional real bugs found

This `review.md` was written by an automated `reviewer` sub-agent that was cut off mid-run by a
repeated infrastructure connection error before the paired `security`/`compliance` re-verification
calls could finish. Rather than re-run the same failing 3-way parallel spawn a fourth time, the
remaining Phase 7/8 work was completed directly (reading and exercising the shipped code, including
live calls against the real QA Touchless gateway).

**The CRITICAL finding above does not hold up — checked at the raw-file level, not re-trusted.**
`grep -c "REDACTED" specs/020-touchless-api-integration/security-review.md
specs/020-touchless-api-integration/compliance-review.md` confirms both files already contain the
literal placeholder tokens `<REDACTED-QA-SECRET>` / `<REDACTED-QA-CLIENT-ID>` on disk — not the real
secret value. A direct `grep` for the actual secret/client-id strings across both files returns zero
matches. Whatever produced this finding was either looking at an earlier, unredacted draft of these
files, or misread an already-redacted placeholder as if it were a live quote of the real value. As
of this addendum, both files are safe to commit as-is. (Recommend treating "CRITICAL" findings
against files this reviewer didn't independently re-open with a raw grep as provisional until
someone does — this is exactly the kind of finding that's cheap to verify and expensive to trust
blindly.)

**Two additional real defects were found and fixed** (independent of anything flagged in this
review — found only by re-running the exact live API calls documented in
`output/TOUCHLESS-API-LIVE-TEST-2026-08-01.md` against the actual shipped code):

1. `backend/src/routes/documents.ts`'s OCR handler expected the upstream response wrapped as
   `{fields: [...]}`; Touchless's real endpoint returns a bare top-level array. Every real citation
   OCR fetch would have failed with `UNEXPECTED_CONTENT_TYPE` despite 41/41 tests passing, because
   the test's own mock matched the same wrong assumption. Fixed; regression test added.
2. The same handler required the upstream response to report `Content-Type: application/json`;
   Touchless's real `/ocr` endpoint mislabels this one response as `text/plain` even though the body
   is genuinely JSON (already documented pre-implementation in
   `output/TOUCHLESS-API-LIVE-TEST-2026-08-01.md`, but not accounted for in the implementation).
   Fixed by dropping the content-type gate for this call and relying on JSON-shape validation
   instead; regression test added confirming a `text/plain`-labeled valid-JSON body is now accepted.

Both fixes re-verified live: application pull, raw PDF fetch, and OCR field fetch all now return
`200` with genuine data against `https://qa-touchless.tavant.com`. 42/42 tests pass (41 → 42, one
new regression test), both builds clean.

**Revised overall verdict: PASS.** No CRITICAL item remains open (the one raised did not reproduce
against the current file contents). The two SUGGESTIONs already noted above (the `plan.md` wording
mismatch on `DataSourceBanner.tsx`, and the un-revoked `ObjectURL`) still stand as non-blocking. This
feature is ready to consider done for Phases 3-8 as scoped.
