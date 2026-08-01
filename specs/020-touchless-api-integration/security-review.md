# Security Review — Touchless API Integration (020)

**Scope**: Backend proxy holding Touchless OAuth client-credentials server-side; forwards 3 call
types (`GET application by applicationId`, `GET document bytes by documentId`, `GET document OCR by
documentId`) from the existing client-side React frontend. No new persistent storage. Data is
display/citation-only — does not feed the deterministic QC engine (spec `020`, FR-010).

**Methodology**: MVP-mode "light" review — dependency-audit-plus-OWASP, not a full penetration test.
This is a proportional review for a 3-endpoint proxy, not an enterprise API gateway.

**Date**: 2026-08-01
**Reviewer**: Security review (Phase 3 PLAN, `g-os-devteam-security`)
**Spec reviewed against**: `specs/020-touchless-api-integration/spec.md` (already passed quality
checklist — scope not relitigated here)
**Architect plan**: `specs/020-touchless-api-integration/plan.md` does not exist yet at review
time — backend stack (Node/Express vs. Python) is undecided. Recommendations below are written
generically and flagged per-stack where the mechanism differs.

---

## Trust boundaries

```
Browser (React, untrusted — public network)
   |  same-origin fetch, session-scoped, NO vendor creds, NO bearer token
   v
Backend proxy (trusted — holds client_id/client_secret, holds bearer token in memory)
   |  OAuth client_credentials -> Bearer token -> forwarded GET
   v
Touchless vendor API (qa-touchless.tavant.com / prod equivalent)
```

Two trust boundary crossings matter: (1) browser -> proxy (must not leak credentials/tokens
downstream, must validate untrusted input before it becomes part of an outbound URL), (2) proxy ->
Touchless (must not leak PII into logs/errors surfaced back across boundary 1).

---

## 1. Credential handling

### 1a. The untracked cleartext-secret file (concrete finding, MUST-FIX)

`docs/architecture/api/TLP-QA-QC-Creds.postman_environment` is untracked (confirmed via `git status`
at review time) and contains, in cleartext JSON:

```json
{"key": "client_secret", "value": "<REDACTED-QA-SECRET>", ...}
```

alongside `client_id = <REDACTED-QA-CLIENT-ID>` and `QAGateway = https://qa-touchless.tavant.com`. This is QA-tier,
not production, but it is a live, currently-working secret (verified live 2026-08-01 per
`output/TOUCHLESS-API-LIVE-TEST-2026-08-01.md`) sitting in plaintext in the working tree, one `git
add -A` / `git add docs/` away from being permanently baked into git history — history that is very
difficult to scrub after the fact.

**Root cause of why it isn't already caught**: the repo's `.gitignore` has a `*credentials*` pattern
(line ~33), but this filename uses `Creds`, not `credentials` — the pattern is a case-sensitive
substring match and does not fire. Confirmed by direct test: `git check-ignore -v
docs/architecture/api/TLP-QA-QC-Creds.postman_environment` returns no match, and `git status` lists
the file as untracked (would be silently hidden if ignored).

**Remediation (concrete, ordered)**:
1. Do **not** `git add` this file as-is, ever.
2. Move the actual secret value out of the file and into a gitignored `.env` (e.g.
   `TOUCHLESS_CLIENT_SECRET=<REDACTED-QA-SECRET>` in a root or backend-local `.env`) — `.env` and `.env.*` are
   already in `.gitignore` (confirmed, lines 33-34 of the root `.gitignore`).
3. Either (a) delete the `.postman_environment` file from the repo entirely once the backend reads
   the secret from the environment instead, or (b) if it's kept for reference (e.g., to hand to
   another engineer setting up Postman locally), scrub the `client_secret` value to a placeholder
   (`"value": "<see 1Password / ask team lead>"`) before it is ever committed.
4. Add a repo-level safety net so this class of file can't recur silently: extend `.gitignore` with
   `*.postman_environment` (Postman environment exports are, by construction, likely to carry live
   secrets — broader and more reliable than hoping every future filename contains the literal
   substring `credentials`).
5. Because the secret has already been "live" (used in a real OAuth exchange, per the live-test doc)
   even though it never entered git history, treat it as reasonable hygiene — not mandatory before
   this ships — to ask the vendor to rotate this QA secret once the proxy is live and reading from
   `.env`, since it has existed in a plaintext file on disk and was referenced in a now-committed
   markdown doc (`output/TOUCHLESS-API-LIVE-TEST-2026-08-01.md` — checked: that file cites the
   *path* to the creds file and the *client_id*, not the secret value itself, so it is not itself a
   leak vector).

### 1b. Backend environment-variable handling

- Backend process reads `TOUCHLESS_CLIENT_ID` / `TOUCHLESS_CLIENT_SECRET` / `TOUCHLESS_BASE_URL`
  from process environment (via `.env` + a loader — `dotenv` for Node, `python-dotenv` or
  `os.environ` for Python) — never hardcoded in source, never in a config file that gets committed.
- Confirm whichever `.env` file is used matches an already-ignored pattern (`.env`, `.env.*` — both
  already present) before any commit that adds backend scaffolding.
- No secret should appear in `p0/`, `frontend/`, or any test fixture committed to git — test/CI runs
  against this proxy should mock the OAuth exchange rather than using a real (even QA-tier) secret in
  a checked-in test file.

### 1c. Vite bundling — confirm nothing server-side leaks into the client bundle (MUST-VERIFY)

Vite only exposes environment variables prefixed `VITE_` to client code (`import.meta.env.VITE_*`);
anything without that prefix is invisible to `import.meta.env` and never bundled. This is the
correct mechanism to rely on, **not an app-level convention that could be forgotten**:
- The Touchless `client_id` / `client_secret` / bearer token / `TOUCHLESS_BASE_URL` (if it should stay
  server-only) MUST be read only in backend/server code, using **non**-`VITE_`-prefixed variable
  names, and MUST NOT be referenced anywhere under `frontend/src/`.
- Verification step for CI or pre-ship check: `grep -r "VITE_" frontend/src/ | grep -i
  "touchless\|client_secret\|client_id\|bearer"` should return nothing. Also worth a one-time `grep
  -r "<REDACTED-QA-SECRET>\|<REDACTED-QA-CLIENT-ID>"` across `frontend/` and any built `dist/` bundle before first release, to
  confirm no accidental copy-paste of the QA secret into frontend code during development.
- If the frontend needs to know *whether* live data is available (e.g., to render the Stored/Live
  toggle) it should ask the backend for a boolean capability flag, never for the credentials or a
  token itself.

---

## 2. SSRF / parameter injection

The proxy takes `applicationId` and `documentId` from the browser and inserts them into an outbound
URL (`GET /store/application/results/{applicationId}`, `GET /store/documents/read/{documentId}`,
`GET /store/documents/read/{documentId}/ocr`). Both IDs are live-confirmed as UUIDs (`applicationId =
0eb57730-6d2e-4a6d-8db3-bc1217c77b90`, `documentId = 632a9c26-d636-4564-b89d-256a5dfe70d4`).

**Risk**: without validation, a crafted `documentId` containing `../`, an absolute URL, encoded
slashes, or control characters could path-traverse within the Touchless host's own path space, or —
if the ID is ever concatenated into a full URL rather than used as a same-host path segment — be used
for SSRF against a different host entirely (the proxy server, running server-side, may have network
reach to internal services the browser doesn't).

**Required mitigation (MUST-FIX, cheap for this shape of input)**:
1. **Format allowlist, not denylist.** Both IDs are UUIDs in every observed case — validate with a
   strict UUID regex (`^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$`)
   before using either value in any outbound request. Reject (400, not 500) anything that doesn't
   match — do not attempt to "clean" or partially accept it.
2. **Never string-concatenate a full URL from user input.** Build the outbound request using a URL
   library's path-join / params mechanism against a **fixed, server-configured base host**
   (`TOUCHLESS_BASE_URL`, never taken from the request) so a value like `https://evil.example.com` or
   `../../admin` in `applicationId` cannot change the target host or escape the intended path prefix.
3. **The base host itself is never client-supplied** — confirm no query param, header, or body field
   from the browser can influence which Touchless host/environment the proxy calls. (Relevant because
   a Stored/Live toggle exists — the toggle should select a server-side code path, not pass a
   base-URL value from the client.)
4. Document-type edge case from the spec (FR-007/Edge Cases: `documentId` assumption verified for one
   document type only) — validation should fail closed and return a distinct, visible error rather
   than forwarding an unvalidated ID "just in case it works," consistent with FR-012's no-silent-
   fallback requirement.

---

## 3. PII handling

The loan/document payloads carry SSN, DOB, full name, and address (synthetic today — "Andy America",
`999-60-3333" — but the code path must be safe by construction since the same code runs against real
data later, per the task brief).

**Required controls (MUST-FIX before this ships against anything beyond synthetic QA data; strongly
recommended even for the QA-only MVP since the code path is what matters, not today's data)**:
1. **Never log full request/response bodies.** Any proxy-level access/debug logging must log
   metadata only — method, path template (`/store/documents/read/:documentId`, not the raw ID if that
   ID could itself be sensitive — UUIDs here aren't PII, but treat this as a pattern, not a one-off
   check), status code, latency, and a correlation/request ID. Never log the Touchless response body
   (contains SSN/DOB/name/address) or the full forwarded request body at `info` level or above.
2. **If body logging is ever needed for debugging**, gate it behind an explicit debug flag that
   defaults off, and redact known-sensitive field names before logging (`Borrower_SSN`,
   `Borrower_DOB`/`Date_Of_Birth`, `*_SSN`, address fields) — a simple allowlist-of-safe-fields or
   denylist-of-known-PII-keys redactor is sufficient at this scale; don't over-build a generic PII
   scrubber for a 3-endpoint MVP.
3. **Error messages returned to the reviewer must not leak PII or vendor internals.** A failed
   Touchless call should surface a generic, categorized error to the browser (`"live pull failed:
   network error"` / `"live pull failed: authentication error"` / `"live pull failed: document not
   found"` — matching FR-012 and the Edge Cases' requirement to distinguish auth failure from
   not-found) — never the raw Touchless response body, which could contain echoed request data or
   internal vendor error detail, and never a stack trace containing a request object that itself held
   the PII payload.
4. **In-memory only, per FR-013** — confirm no accidental disk write (no debug dump to a temp file, no
   default request-logging middleware that writes to a log file on disk) inherits PII by default. This
   is the one area where "no new persistent storage" and "PII handling" overlap — a logging
   middleware added for unrelated reasons (e.g. `morgan` in Express, default `pino` transport) is the
   most likely accidental violation, since it's easy to add without thinking about what's in the
   body.

---

## 4. Token handling

1. **Bearer token must stay server-side, in-memory, never sent to the browser.** The browser talks to
   the proxy using the app's own session mechanism (whatever the app already uses — cookie/session or
   simple same-origin fetch), never with the Touchless bearer token. Confirm no API response echoes
   `access_token` or an `Authorization` header value back to the client.
2. **Expiry/refresh**: the live test confirmed `expires_in: 59999` seconds (~16.7 hours) for QA. Cache
   the token server-side with its expiry timestamp; re-request a new token only when expired (or
   proactively a small margin before expiry, e.g. 60s), not on every forwarded call — avoids
   unnecessary OAuth round-trips against the vendor.
3. **On a 401 from Touchless**: the proxy should attempt **exactly one** re-authentication (discard
   the cached token, request a fresh one, retry the original forwarded call once) — not loop. If the
   retry also 401s, surface a distinct "authentication error" to the browser (per Edge Cases) rather
   than retrying again. A missing retry-cap here is a classic self-inflicted DoS/latency bug (each
   browser request could otherwise trigger unbounded retries against the vendor), so the cap is a
   MUST-FIX, not a nice-to-have, even though the feature is otherwise MVP-light.
4. Token storage should be a simple in-memory variable/module-level cache — no new persistent storage
   needed or wanted here (matches FR-013 and the "effectively stateless per request" assumption).

---

## 5. Transport/CORS

1. **CORS**: the proxy should only accept cross-origin requests (if any) from the app's own known
   origin(s) — set an explicit `Access-Control-Allow-Origin` allowlist (the app's own dev/demo/prod
   origins), not `*`, and do not reflect an arbitrary `Origin` header back. Since frontend and proxy
   are likely served from the same origin in this deployment shape, confirm whether CORS is even
   needed — if same-origin, prefer no CORS headers at all over a permissive misconfiguration.
2. **HTTPS enforcement**: Touchless itself is already HTTPS-only (`https://qa-touchless.tavant.com`).
   For the proxy's own inbound side, HTTPS enforcement in the QA/demo environment is lower-priority
   per this project's MVP-mode framing (environment specifics acknowledged as out of scope by the
   task brief) — but if this proxy is ever exposed beyond localhost (e.g., a shared demo URL), it
   should sit behind TLS termination consistent with however the rest of this app is already served,
   not introduce a new unencrypted listener as a special case for this feature.
3. No new inbound ports/services should be exposed beyond what the existing frontend dev/serve setup
   already uses, beyond the proxy's own listener.

---

## 6. Dependency audit

`specs/020-touchless-api-integration/plan.md` (the architect's implementation plan) does not
exist yet at review time, so the backend stack (Node/Express vs. Python) is undecided. Covering both:

- **If Node/Express (or any `npm`-based backend)**: add `npm audit --audit-level=high` (or
  equivalent, e.g. `npm audit fix` reviewed manually rather than auto-applied blindly) to the CI/local
  pre-ship checklist for the new backend's `package.json`, distinct from the existing
  `frontend/package.json` audit if the backend is a separate package.
- **If Python (`boto3`-adjacent pattern already used elsewhere in this repo, e.g.
  `p0/experiment_g3/llm_arm.py`)**: add `pip-audit` (or `safety`) against the backend's
  `requirements.txt`/`pyproject.toml` to the same pre-ship checklist. Pin exact versions (project-wide
  Python 3.9-compatibility constraint already noted in `CLAUDE.md` — confirm any new HTTP client
  library used (e.g. `requests`, `httpx`) is 3.9-compatible).
- Either way: this is a **new** dependency surface (first backend process in a frontend-only repo per
  current `frontend/package.json` — no server dependencies present today), so this audit must be
  added to CI/scaffold, not assumed to already be covered by an existing job. Treat this as a
  MUST-FIX-BEFORE-SHIP gate per this project's MVP-mode security posture, not a nice-to-have — it's
  the one generic OWASP-adjacent control this review can mandate without knowing the final stack.
- Standard components to check for known CVEs regardless of stack: the OAuth/HTTP client library, any
  JSON body-parsing middleware, and (if used) any PDF-passthrough/streaming library for forwarding
  document bytes to the browser.

---

## 7. Rate limiting / abuse

Lightweight only, per MVP-mode and the proportional scope (3 endpoints, low-traffic internal
demo/reviewer tool, not a public API):
- A simple per-session or per-IP request counter/throttle (e.g., a fixed cap like "N requests per
  minute" using an in-memory counter, no new infra) is sufficient to prevent an accidental client-side
  bug (e.g., a retry loop in the frontend) from hammering the Touchless vendor endpoint or exhausting
  the OAuth token's usefulness.
- This is explicitly **not** the place to add distributed rate limiting, WAF-style bot detection, or
  API-key-tiered quotas — that would be over-engineering for this feature's actual exposure (an
  internal reviewer tool, not a public-facing API). A nice-to-have, not a blocker.

---

## Verdict

**Overall: CONCERNS** — no exploit confirmed against running code (none exists yet; this is a PLAN-
phase review), but there are concrete, actionable items that must be addressed before or during
implementation. None of these block moving to the next SDLC phase; they are checklist items for the
implementer.

### MUST-FIX-BEFORE-SHIP

1. **Untracked cleartext secret** (`docs/architecture/api/TLP-QA-QC-Creds.postman_environment`) — move
   `client_secret` into a gitignored `.env`, scrub or delete the postman-environment file before any
   `git add` touches it, and add `*.postman_environment` to `.gitignore` as a durable guard against
   recurrence. (Section 1a)
2. **Vite bundle verification** — confirm zero `VITE_`-prefixed references to Touchless credentials
   anywhere under `frontend/src/`, and that all vendor-credential/token handling lives exclusively in
   backend code. Run the `grep` checks in Section 1c before first release. (Section 1c)
3. **UUID-format allowlist validation** on both `applicationId` and `documentId`, enforced server-side
   before either value is used in any outbound URL construction; outbound URLs must be built against
   a fixed server-configured base host, never a client-influenced one. Reject non-conforming input
   with 400, fail closed. (Section 2)
4. **No PII in logs or client-visible errors** — proxy logging must exclude full request/response
   bodies by default (metadata-only logging); reviewer-facing error messages must be generic/
   categorized, never the raw vendor response or a stack trace containing the PII payload. (Section 3)
5. **Bearer token never reaches the browser**; single re-auth attempt on 401 (no retry loop) before
   surfacing a distinct authentication-error to the client. (Section 4)
6. **CORS locked to the app's own origin(s)** — no wildcard `Access-Control-Allow-Origin`, no
   reflected-origin misconfiguration. (Section 5)
7. **Dependency audit added to CI/scaffold** for whichever backend stack is chosen (`npm audit` or
   `pip-audit`) before this feature ships — this is the first backend dependency surface in the repo,
   not already covered by an existing job. (Section 6)

### NICE-TO-HAVE (not blocking)

8. Rotate the QA `client_secret` (`<REDACTED-QA-SECRET>`) once the proxy reads it from `.env`, since it has
   existed in a plaintext file on disk — good hygiene, not required given it's QA-tier and never
   entered git history. (Section 1a)
9. Lightweight per-session/per-IP request throttling to guard against an accidental client-side retry
   loop hammering the vendor endpoint. (Section 7)
10. Spot-check the `documentId == indexedDocId` assumption against 2-3 more document types (already
    flagged as a functional/spec-level caveat, not strictly a security finding, but the fail-closed
    validation in item 3 above is what makes an unverified document type safe rather than silently
    wrong).

---

## Phase 8 Re-Verification (2026-08-01, against shipped code — not the plan)

Performed directly (the automated reviewer/security/compliance sub-agents failed 3 times on a
repeated mid-response connection error at this exact step; rather than keep retrying an
infrastructure fault, this re-verification was done by reading and exercising the actual shipped
code, including live calls against the real QA Touchless gateway).

**All 7 MUST-FIX items reconfirmed against actual code:**

1. Untracked-secret fix confirmed still in place: `docs/architecture/api/TLP-QA-QC-Creds.postman_environment`'s `client_secret` is redacted; `*.postman_environment` is in `.gitignore`; the real value lives only in the gitignored `backend/.env` (`git check-ignore -v backend/.env` confirms it).
2. UUID-validation chokepoint confirmed single-sited: `touchlessClient.ts`'s `isValidUuid()` is the only implementation; both `applications.ts` and `documents.ts` import and call it before any outbound network call — no duplicated/divergent validation logic found.
3. Fail-closed content-type/shape validation confirmed present on both document endpoints (`authorizedGet`'s `expectedContentType` gate for the PDF route; `isValidOcrFields()` shape gate for the OCR route) — an unrecognized document type fails loudly (`UNEXPECTED_CONTENT_TYPE`), never silently wrong.
4. PII-safe logging confirmed by reading `middleware/requestLogger.ts` directly: logs method, route-path *template* (not the raw path with a real ID substituted in), status, latency, and a correlation id only — never request/response bodies.
5. Client-facing error messages confirmed structurally incapable of leaking upstream data: `errors.ts`'s `toErrorEnvelope()` always derives the browser-visible `message` from a fixed per-`ErrorCode` lookup table, never from the thrown error's own `.message` — verified by reading the code, not just the doc comment.
6. CORS lock confirmed in `server.ts`: `Access-Control-Allow-Origin` hardcoded to `http://localhost:3000`, no wildcard, no reflected-origin logic.
7. Dependency audit run for real (not "wired but not run"): `npm audit --omit=dev` in both `backend/` and `frontend/` → **0 vulnerabilities**, both re-confirmed after the Phase 8 code changes below.

**SC-005 grep sweep run for real**: searched for the literal `TOUCHLESS_CLIENT_SECRET` and `TOUCHLESS_CLIENT_ID` values from `backend/.env` across `frontend/src backend/src backend/dist frontend/dist` → zero matches. No credential string reaches any client-visible surface.

**FR-010 zero-regression check run for real**: no file under `p0/qc_engine/` touched; `grep -rl "CheckResult|LoanEvaluation"` across every new backend/frontend file → zero matches. This feature's diff genuinely does not touch the deterministic engine.

**Two real defects found during this re-verification, not caught by the Phase 5/6 test suite** (both fixed, both re-verified live against the real QA gateway afterward — see `output/TOUCHLESS-API-LIVE-TEST-2026-08-01.md` for the original live-test baseline these bugs deviated from):

- `routes/documents.ts`'s OCR handler expected Touchless's response wrapped as `{fields: [...]}`; the real endpoint returns a bare top-level array. The Phase 5 test's own mock matched the (wrong) implementation assumption rather than the verified real contract, so 41/41 tests passed while every real call would have failed with `UNEXPECTED_CONTENT_TYPE`. Fixed to parse the bare array directly; regression test added.
- The same handler required `Content-Type: application/json` on the upstream OCR response; the real Touchless `/ocr` endpoint mislabels this specific response as `text/plain` even though the body is JSON (this exact behavior was already documented in `output/TOUCHLESS-API-LIVE-TEST-2026-08-01.md` from the pre-implementation live test, but the implementation didn't account for it). Fixed by dropping the content-type gate for this one endpoint and relying on JSON-shape validation as the correctness check instead; a regression test locks in the `text/plain`-with-valid-JSON case.

**Takeaway for future phases of this project**: mocked unit tests validate internal consistency, not fidelity to the real vendor contract. Both bugs here were only found by re-running the exact live calls documented in the pre-implementation live-test doc — a cheap, repeatable check worth keeping as a standing Phase 6/8 step for any feature integrating a real external API, not just this one.

**Security re-verification verdict: PASS.** No MUST-FIX item is open. The two functional defects found are correctness bugs (now fixed), not security findings — they do not introduce a leak, a bypass, or an unvalidated-input path; they made the feature fail closed and safe, just non-functional.

### POSITIVE SECURITY CONTROLS (already in place / already decided correctly)

- The spec itself already mandates the core architecture correctly: browser never sees vendor
  credentials, proxy holds them server-side, data is display-only and does not feed the deterministic
  QC engine (FR-002, FR-010) — this is the right shape before any code exists.
- `.env` / `.env.*` are already correctly gitignored at the repo root (confirmed by direct read of
  `.gitignore`).
- FR-012 already requires visible, non-silent error handling on failure (no stale/fixture fallback
  masking a live failure) — this is good security-relevant behavior already specified, not something
  this review had to add.
- No new persistent storage is in scope (FR-013) — reduces the data-at-rest attack surface to zero for
  this feature by design.
