# Technical Plan: Touchless API Integration (020)

**Feature**: `specs/020-touchless-api-integration/spec.md` (Status: Draft, passed quality checklist — scope not relitigated here)
**Phase**: 3 (PLAN)
**Companion doc**: `specs/020-touchless-api-integration/security-review.md` (security review, already
filed — this plan is written to satisfy every MUST-FIX item in that review, cross-referenced inline
rather than restated in full)
**Non-negotiable this feature must respect**: CLAUDE.md Non-Negotiable #1 — pulled Touchless data is
**display/citation-only** and MUST NOT feed `p0/qc_engine`'s deterministic evaluation (spec FR-010).
This plan contains **zero** changes to `p0/qc_engine`, `p0/compile_runs/`, or any `CheckResult`/
`LoanEvaluation` computation path. If a future spec proposes wiring pulled data into verdicts, it is a
new spec, not an extension of this one.

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│  Browser (frontend/, Vite dev server :3000 or built static bundle)  │
│                                                                       │
│  DataSourceContext (React Context, in-memory)                        │
│   - mode: "stored" | "live"                                          │
│   - pulledApplications: Map<applicationId, PulledApplication>        │
│   - retrievedDocuments: Map<documentId, RetrievedDocument>            │
│                                                                       │
│  DataSourceToggle (in SettingsMenu, tucked in Navbar)                 │
│  PullApplicationButton (LoanDetail)                                   │
│  LiveApplicationPanel (LoanDetail — shows pulled loanSummary +        │
│    documents[] list once pulled)                                     │
│  RetrievedDocumentViewer (modal — PDF <iframe> + OCR fields table)    │
└───────────────────────────────┬───────────────────────────────────────┘
                                 │ same-origin fetch, JSON, NO vendor creds
                                 │ NO bearer token ever sent to browser
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│  backend/ — new Node/Express+TS proxy (this feature's only new       │
│  server-side code; stateless per-request except token cache)         │
│                                                                       │
│  routes/applications.ts   POST /api/touchless/applications/:id/pull  │
│  routes/documents.ts      GET  /api/touchless/documents/:id          │
│                           GET  /api/touchless/documents/:id/ocr       │
│  routes/health.ts          GET  /api/health                           │
│                                                                       │
│  touchlessClient.ts  — validates UUID input, builds outbound URL     │
│    against a FIXED server-configured base host (never client-        │
│    influenced), attaches Bearer token, single-retry-on-401            │
│  tokenCache.ts       — in-memory {access_token, expiresAt}, refreshed │
│    on expiry (with margin) or on first 401                            │
│  errors.ts           — ErrorCode enum + JSON error envelope            │
│  config.ts           — reads TOUCHLESS_CLIENT_ID/SECRET/BASE_URL from │
│    process.env via dotenv, from a gitignored .env (never committed)   │
└───────────────────────────────┬───────────────────────────────────────┘
                                 │ HTTPS, Basic auth (token endpoint) /
                                 │ Bearer (data endpoints)
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Touchless QA Gateway — https://qa-touchless.tavant.com               │
│  POST /userservice/oauth/token?grant_type=client_credentials          │
│  GET  /store/application/results/{applicationId}                     │
│  GET  /store/documents/read/{documentId}                              │
│  GET  /store/documents/read/{documentId}/ocr                          │
└─────────────────────────────────────────────────────────────────────┘
```

**What never happens** (structural, not just conventional): the browser never holds
`client_id`/`client_secret`/bearer token; the proxy never writes pulled data to disk; pulled data never
reaches `p0/qc_engine`, `CheckResult`, or `LoanEvaluation`.

---

## 2. The six decisions

### 2.1 Backend proxy language/framework — **Node/Express 5 + TypeScript**

**Recommendation**: Node.js + Express 5 + TypeScript, as a new top-level `backend/` package, not
FastAPI/Python.

**Why, weighed against the real tradeoff**:
- This proxy has **zero shared code with `p0/qc_engine`** (confirmed in the task brief) — the usual
  "stay in Python for consistency with the rest of the project" argument doesn't actually save any
  import/reuse, only stylistic consistency. There is nothing to import from `p0/` into this proxy or
  vice versa.
- It **does** sit directly adjacent to `frontend/`, which is Vite+React+TS. Colocating the proxy in the
  same language means one `tsconfig`-literate mental model, one package manager (`npm`), and a demo
  operator who already has Node installed for `frontend/` needs no new runtime (no Python venv
  creation ceremony) to run a 3-route proxy. This matters for "keep it minimal" (Non-Negotiable #2) —
  the goal is the smallest possible new surface, not architectural purity.
- **Verified current versions** (live registry check, 2026-08-01): `express@5.2.1` on npm,
  `fastapi==0.141.1` on PyPI — both actively maintained, so this isn't a "pick the unmaintained one"
  tradeoff either way.
- Express 5 (GA since 2024, confirmed current at 5.2.1) auto-forwards rejected promises from `async`
  route handlers to error-handling middleware — Express 4 required manual `try/catch` + `next(err)` in
  every handler or a wrapper util. For a 3-route proxy this removes a whole class of "forgot to catch
  the rejected promise" bugs without adding a dependency, which is a genuine ergonomic win over the
  Express 4 examples most tutorials still show.
- **Security-boundary win from colocation avoided, not gained** — see 2.6/file layout: the proxy
  is a **sibling** directory to `frontend/`, not nested inside it, specifically so Vite's build never
  scans server code (see file layout rationale below). Node-vs-Python doesn't change this; it's a
  directory-placement decision, made independently.
- FastAPI would be an equally defensible choice (Pydantic validation is a real ergonomic plus for
  request-shape enforcement, and it would match the Python skew of `p0/`/`src/`) — this is a genuine
  toss-up resolved in Node's favor by ecosystem colocation with `frontend/`, not by a decisive technical
  argument. Flagging this explicitly so a future maintainer doesn't read this as "Python was ruled
  out" — it wasn't, it was a close call.

**Token caching/refresh strategy** (implements security review §4 verbatim):
- `tokenCache.ts` holds a module-level `{ accessToken: string; expiresAt: number } | null`.
- On any outbound call, if no cached token or `Date.now() >= expiresAt - REFRESH_MARGIN_MS` (margin
  = 60s), request a fresh token via `POST /userservice/oauth/token?grant_type=client_credentials` with
  HTTP Basic auth, cache `{ accessToken, expiresAt: Date.now() + expires_in*1000 }`.
- On a `401` from any forwarded call: discard the cached token, request exactly **one** fresh token,
  retry the original forwarded call **exactly once**. If that retry also fails with `401`, surface
  `AUTH_FAILURE` to the browser — no further retry (avoids the self-inflicted-DoS pattern the security
  review flags in §4.3).
- Given `expires_in ≈ 59999s` (~16.7h) observed live, a real demo session will essentially never hit
  natural expiry — the refresh-on-401 path exists for correctness/robustness, not because it's expected
  to fire often.

### 2.2 PDF rendering approach — **Blob + `ObjectURL` + `<iframe>`** (native browser PDF viewer)

**Recommendation**: fetch the PDF bytes through the proxy, construct a `Blob` with
`type: "application/pdf"`, create `URL.createObjectURL(blob)`, and render it in an `<iframe src=...>`
(or `<embed>`) — relying on the browser's own built-in PDF renderer (Chrome, Firefox, Safari, and Edge
all ship one).

**Why, against the alternatives**:
- The spec's own Assumptions section explicitly biases toward "the simplest approach that shows genuine
  content rather than building a bespoke PDF renderer from scratch" — this is the literal simplest
  option: zero new dependencies, ~10 lines of code (fetch → blob → object URL → iframe `src`).
- **pdf.js** (verified current release `v6.2.108` on GitHub, 2026-08-01) is the standard alternative and
  would be the right call if this feature needed page-level highlighting/deep-linking parity with the
  existing mock citation UX (`ExceptionReview.tsx`'s `#page=N` deep-link pattern, per
  `output/DEMO-UX-LESSONS.md` §1). It isn't justified here for two reasons: (a) it requires a
  worker-script version-pinning setup (a real, if small, maintenance surface for an MVP proxy feature),
  and (b) **the Touchless API doesn't return a page number for a citation today** — the OCR endpoint
  returns `{name, value, confidence}` per field with no page locator, so pdf.js's main advantage
  (jump-to-page) has no data to key off yet regardless of rendering choice. That's a data-availability
  gap, not something pdf.js would fix.
- Native `<iframe>`/`<embed>` still supports basic PDF Open Parameters (`#page=N`) if/when a page number
  ever becomes available from the vendor — so choosing native rendering now doesn't foreclose that
  later; it just doesn't build unused machinery today.
- FR-008 only requires the retrieved content be "visibly and verifiably distinct from placeholder/
  simulated content" (SC-002) — a real embedded PDF trivially satisfies this next to the existing
  `ExceptionReview.tsx` placeholder text ("PDF page render placeholder — deep-links to...").

**Practical detail**: do NOT revoke the `ObjectURL` when the viewer modal closes. §2.4's fetch-once-
per-session cache holds `RetrievedDocument.pdfObjectUrl` for reuse across the whole session — revoking
on close would break a later cache-hit reopen of the same `documentId` (the `<iframe>` would point at a
dead URL). Since this pass has no cache-eviction mechanism (§2.4's `Map`s only grow for the session),
the correct revocation scope would be session-end, not modal-close — and browsers already release all
`ObjectURL`s automatically on page unload/reload, so no explicit revoke call is needed at all. This is a
deliberate, bounded tradeoff: a session that opens many large documents back-to-back holds them all in
memory until the tab closes or reloads — acceptable at MVP/demo scale, revisit only if §2.4 ever grows a
real eviction mechanism.

### 2.3 Data-source toggle state management — **React Context, in-memory only (no `sessionStorage`)**

**Recommendation**: a plain React Context (`DataSourceContext`) holding `mode: "stored" | "live"` in
component state, no `sessionStorage`, no `localStorage`, no URL param.

**Why, against FR-004's exact wording**: *"MUST reset to 'Stored' on a new session and MUST NOT be
encoded in a shareable URL."* Both in-memory state and `sessionStorage` satisfy the URL-encoding
prohibition trivially (neither touches the URL). The real difference is *when* the reset happens:
`sessionStorage` survives a page reload within the same tab and only clears on tab close; in-memory
React state resets on any reload. FR-004 only requires reset-on-new-session (tab close) — it does not
require *surviving* a mid-session reload — so `sessionStorage` would also be spec-compliant. In-memory
state is chosen instead because:
1. It's **strictly simpler** — zero serialization, zero storage-API surface, nothing to keep in sync.
2. It stays **consistent with decision 2.4** (fetch-once-per-session caching is also frontend in-memory
   state). If the toggle survived a reload via `sessionStorage` but the pulled-application cache did
   not, a reload while in "Live" mode would silently land on Live mode with *no* cached data — which
   Edge Case #2 already requires prompting a fresh pull for anyway. Pairing both in one in-memory
   context means a reload resets the whole live-data experience together, which is the more honest,
   less confusing behavior (no "why does it say Live but show nothing" moment).
3. If a future need arises for "survive reload, not tab-close" (e.g., a demo operator wants Live mode to
   persist through an accidental refresh), that is a `sessionStorage` upgrade — cheap to add later,
   not needed now.

### 2.4 Session-scoped fetch-once caching — **Frontend-only, in `DataSourceContext`**

**Recommendation**: two `Map`s held in the same `DataSourceContext` as the toggle:
`pulledApplications: Map<applicationId, PulledApplication>` and
`retrievedDocuments: Map<documentId, RetrievedDocument>`. The backend proxy performs **no** caching of
its own (aside from the OAuth token, which is a proxy-internal concern, not a data cache) — it is a
pure pass-through per the spec's own framing ("the backend proxy is effectively stateless per request,
aside from short-lived token handling").

**Why**: the spec explicitly frames the proxy as stateless-per-request; adding a server-side data cache
would duplicate state across two layers for no benefit (nothing else calls this proxy, there is exactly
one frontend consumer) and would reintroduce exactly the kind of new persistent/semi-persistent state
FR-013 is designed to avoid. Frontend-only caching also makes "refresh requires an explicit, separate
re-pull action" (FR-005) trivial to implement: the pull button is simply "does the Map already have this
key → show cached; else fetch and populate," and a distinct "Re-pull" affordance clears just that one
key and re-fetches.

### 2.5 Error taxonomy and JSON contract

Five distinct error categories, surfaced with a consistent envelope so the frontend can render a
distinguishable message per FR-012/Edge Cases without string-sniffing:

| `code` | Meaning | Typical trigger | HTTP status returned to browser |
|---|---|---|---|
| `AUTH_FAILURE` | Touchless rejected the bearer token even after one refresh-and-retry | Expired/invalid token, both attempts 401 | `502` |
| `NOT_FOUND` | Touchless returned 404 for the given `applicationId`/`documentId` | Unknown/mistyped ID | `404` |
| `TIMEOUT` | The proxy's outbound call to Touchless exceeded its deadline | Network stall, slow upstream | `504` |
| `UNEXPECTED_CONTENT_TYPE` | Response body didn't match the endpoint's expected shape | PDF endpoint returned non-PDF; OCR endpoint returned non-JSON or zero fields | `502` |
| `INVALID_INPUT` | `applicationId`/`documentId` failed the UUID-format allowlist (security review §2) | Malformed ID from the client | `400` |
| `UPSTREAM_ERROR` | Any other non-2xx from Touchless not covered above | Unexpected 5xx, etc. | `502` |
| `PROXY_ERROR` | Unhandled exception inside the proxy itself | Bug, misconfiguration | `500` |

**Response envelope** (every non-2xx proxy response, consistent shape regardless of code):

```json
{
  "error": {
    "code": "AUTH_FAILURE",
    "message": "Touchless authentication failed after one retry.",
    "upstreamStatus": 401,
    "retryable": true,
    "requestId": "a1b2c3d4",
    "timestamp": "2026-08-01T14:22:03.000Z"
  }
}
```

- `message` is a **generic, categorized** string (per security review §3.3) — never the raw Touchless
  response body, never a stack trace. PII never appears in this field.
- `retryable` tells the frontend whether to show a "Retry" affordance (`true` for `TIMEOUT`,
  `UPSTREAM_ERROR`, `AUTH_FAILURE`; `false` for `NOT_FOUND`, `INVALID_INPUT`).
- `requestId` is a short correlation ID logged proxy-side (metadata-only logging, per security review
  §3.1/§3.4) so a demo operator can report "request `a1b2c3d4` failed" without any PII changing hands.
- The frontend's fetch wrapper (`touchlessApi.ts`) always attempts to parse this envelope on any non-2xx
  response and falls back to a generic `PROXY_ERROR`-shaped object if parsing fails (defensive against
  a truly unexpected failure mode, e.g. the proxy process itself being unreachable).

### 2.6 API contract (frontend ↔ new backend)

Base path: `/api/touchless` (proxy listens on its own port in dev, e.g. `:4000`; Vite dev server proxies
`/api` to it via `server.proxy` in `vite.config.ts` so the browser only ever talks same-origin).

**`POST /api/touchless/applications/:applicationId/pull`**
- Path param: `applicationId` (UUID, validated).
- No request body.
- `200` response:
  ```json
  {
    "applicationId": "0eb57730-6d2e-4a6d-8db3-bc1217c77b90",
    "fetchedAt": "2026-08-01T14:22:03.000Z",
    "source": "live",
    "application": { /* raw Touchless application payload, unmodified pass-through */ }
  }
  ```
- Error responses per §2.5 envelope (`AUTH_FAILURE`, `NOT_FOUND`, `TIMEOUT`, `UPSTREAM_ERROR`,
  `INVALID_INPUT`, `PROXY_ERROR`).
- Verb is `POST` (not `GET`) because this is an explicit, user-triggered *action* per FR-001 ("trigger,
  via a button"), not an idempotent read the browser might prefetch — matches the spec's "pull" framing
  and avoids any risk of a browser/CDN treating it as cacheable.

**`GET /api/touchless/documents/:documentId`**
- Path param: `documentId` (UUID, validated).
- `200` response: raw bytes, `Content-Type: application/pdf` passed through unmodified from Touchless.
- If Touchless's `content-type` on a 200 response is anything other than `application/pdf`, the proxy
  treats this as `UNEXPECTED_CONTENT_TYPE` (not a silent pass-through of unknown bytes) and returns the
  JSON error envelope instead of the body.
- Error responses per §2.5.

**`GET /api/touchless/documents/:documentId/ocr`**
- Path param: `documentId` (UUID, validated).
- `200` response:
  ```json
  {
    "documentId": "632a9c26-d636-4564-b89d-256a5dfe70d4",
    "fetchedAt": "2026-08-01T14:22:03.000Z",
    "fields": [
      { "name": "Borrower_First_Name", "value": "ANDY", "confidence": 100.0 },
      { "name": "Borrower_SSN", "value": "999-60-3333", "confidence": 0.0 }
    ]
  }
  ```
- If Touchless returns valid JSON but zero fields, or a shape that doesn't parse as
  `{name, value, confidence}[]`, this is `UNEXPECTED_CONTENT_TYPE` per Edge Cases ("an OCR response
  with zero fields... shown as a distinct error state, not treated as a successful empty result").
- **No confidence-scale assumption is baked in anywhere** — per CLAUDE.md's live-test finding, values up
  to `102.0` are passed through as-is; the frontend must not clamp, normalize, or treat any value as
  "out of range."
- Error responses per §2.5.

**`GET /api/health`** — liveness check, no auth, returns `{ "status": "ok" }`. Used by local dev and any
future deploy healthcheck (per `output/PRIOR-ART-OLAV-MORTGAGE-QC.md`'s reusable 6-point healthcheck
pattern, if this ever gets containerized).

---

## 3. File/directory layout

**Decision: a new top-level `backend/` directory, sibling to `frontend/`, not nested inside it
(`frontend/server/` rejected).**

**Why**: `frontend/`'s `tsconfig`/Vite build is scoped to bundle browser-shipped code; keeping the
proxy's source (and its `.env` secret file) *outside* that directory tree is a structural guarantee —
not just a convention someone has to remember — that server-only code and secrets can never
accidentally end up in a Vite build output. This directly reinforces security review §1c's "Vite only
bundles `VITE_`-prefixed vars" control: putting the two codebases in genuinely separate directories
means there's no `frontend/server/` path a future `import` or a misconfigured `vite.config.ts` glob
could accidentally sweep in. It also matches this repo's existing convention of top-level directories
for distinct concerns (`p0/`, `frontend/`, `docs/`, `src/`) rather than nesting a whole second app
inside one of them.

```
backend/
├── package.json              # express, dotenv, typescript, tsx (dev), @types/express etc.
├── tsconfig.json
├── .env.example               # committed — placeholder values only, e.g. TOUCHLESS_CLIENT_SECRET=<set-me>
│                               # (real .env is already covered by root .gitignore's `.env` / `.env.*`)
├── README.md                  # how to run: npm install && npm run dev; required env vars
└── src/
    ├── server.ts               # Express app bootstrap: CORS (locked to frontend origin, security §5),
    │                            # JSON body parsing, route mounting, central error middleware
    ├── config.ts               # loads TOUCHLESS_CLIENT_ID / TOUCHLESS_CLIENT_SECRET / TOUCHLESS_BASE_URL /
    │                            # PORT / REQUEST_TIMEOUT_MS from process.env via dotenv; throws loudly
    │                            # at startup if a required var is missing (fail fast, not silently)
    ├── tokenCache.ts            # in-memory {accessToken, expiresAt}; getValidToken(), invalidate()
    ├── touchlessClient.ts       # isValidUuid(), buildUrl() against fixed TOUCHLESS_BASE_URL,
    │                            # authorizedGet() with single-retry-on-401, content-type verification
    ├── errors.ts                # ErrorCode enum, TouchlessProxyError class, toErrorEnvelope()
    ├── routes/
    │   ├── applications.ts      # POST /api/touchless/applications/:applicationId/pull
    │   ├── documents.ts         # GET /api/touchless/documents/:documentId (+ /ocr)
    │   └── health.ts            # GET /api/health
    └── middleware/
        ├── errorHandler.ts      # Express 5 central error handler -> JSON envelope (§2.5), maps
        │                        # TouchlessProxyError.code -> HTTP status
        └── requestLogger.ts     # metadata-only logging (method, path template, status, latency,
                                 # requestId) — never logs request/response bodies (security §3.1)
```

**Frontend additions** (`frontend/src/`):

```
lib/
├── touchlessApi.ts             # pullApplication(applicationId), getDocument(documentId),
│                                # getDocumentOcr(documentId) — thin fetch wrappers against
│                                # /api/touchless/*, parse the §2.5 error envelope on failure
└── dataSourceContext.tsx       # DataSourceProvider + useDataSource() hook:
                                 #   mode, setMode, pulledApplications Map, retrievedDocuments Map,
                                 #   pullApplication(id), getOrFetchDocument(id), errors per key

components/
├── SettingsMenu.tsx             # small gear-icon dropdown added to Navbar (NOT a 4th main tab —
│                                 # satisfies SC-003 "not visible in the primary navigation")
├── DataSourceToggle.tsx         # Stored/Live switch, lives inside SettingsMenu
├── PullApplicationButton.tsx    # on LoanDetail; shows idle/loading/cached/error states;
│                                 # disabled+tooltip when mode="stored"
├── LiveApplicationPanel.tsx     # shown on LoanDetail when mode="live" and data is pulled;
│                                 # summarizes loanSummary/borrowersDetail, lists documents[]
│                                 # (documentId, documentName, documentType) each with a
│                                 # "View Document" action
├── RetrievedDocumentViewer.tsx  # modal: fetches (or reuses cached) PDF blob + OCR fields for one
│                                 # documentId; <iframe> + fields table; distinct error states per §2.5
└── (extend) SampleDataBanner.tsx → renamed/extended DataSourceBanner.tsx (FR-011): shows
    "Stored (sample data)" or "Live — pulled at HH:MM:SS" instead of always the same purple banner
```

`frontend/src/App.tsx` wraps its existing tree in `<DataSourceProvider>`; no changes to `ViewId`/nav.ts
are required — the settings menu is a Navbar-local dropdown, not a routed view.

`frontend/vite.config.ts` gains a `server.proxy` entry forwarding `/api` to the backend's dev port, so
`fetch("/api/touchless/...")` stays same-origin in dev (no CORS needed in the common case, consistent
with security review §5.1's preference for "no CORS headers at all" when same-origin is achievable).

---

## 4. Integration point for citations (resolving a real ambiguity, not glossed over)

The existing mock `CheckResult.citation` / `Finding.citation` shape (`{ doc: string; page: number;
segment: string }`, `frontend/src/lib/types.ts`) is **Stored-mode fixture data** — it has no
`documentId` and isn't produced by any Touchless call. Rather than retrofitting that mock shape (which
would blur Stored/Live data and risk exactly the kind of accidental conflation Non-Negotiable #1 exists
to prevent), this feature adds a **separate, additive** browsing surface: `LiveApplicationPanel` lists
the pulled application's actual `documents[]` array (each entry already carries a real `documentId`
per the live-verified data shape) and each row's "View Document" button opens
`RetrievedDocumentViewer` keyed on that `documentId` directly — satisfying US2's "click a citation
tied to a specific `documentId`" without needing to reconcile it with the unrelated Stored-mode mock
citation UI, which is left completely untouched by this feature.

---

## 5. What is explicitly OUT of scope (per spec Assumptions — do not implement)

- No wiring of pulled data into `p0/qc_engine`, `CheckResult`, or `LoanEvaluation` (FR-010).
- No MISMO XML retrieval or change to three-source reconciliation logic (Non-Negotiable #3 unaffected).
- No push/upload capability to Touchless (pull-only).
- No production credential provisioning/rotation process (QA-tier creds only, per spec Assumptions).
- No new persistent storage — no database, no on-disk cache, no file-based session store (FR-013).
- No per-loan or loan-detail-page toggle — the toggle is single, global, session-wide (FR-003).
- No silent auto-refresh of pulled data — re-pull is always an explicit action (FR-005).
- No dev-only gating on the toggle (ships in any build, per spec Assumptions).
- No pdf.js integration, no page-level highlight/deep-link fidelity beyond native `#page=N` support (if
  a page number ever becomes available) — out of scope for this pass per §2.2.
- No server-side data caching in the proxy beyond the OAuth token (frontend-only cache, §2.4).

---

## 6. Open questions for security/compliance review

(Cross-referencing `specs/020-touchless-api-integration/security-review.md`, already filed — these
are the items that review couldn't fully resolve without an architecture decision, now that one exists,
plus a couple this plan surfaced independently.)

1. **The untracked cleartext-secret file** (`docs/architecture/api/TLP-QA-QC-Creds.postman_environment`)
   must be handled *before* any commit touches `docs/architecture/api/` — move `client_secret` into
   `backend/.env` (gitignored), then either delete the postman-environment file or scrub its
   `client_secret` value to a placeholder. Add `*.postman_environment` to root `.gitignore` as a durable
   guard (the existing `*credentials*` pattern doesn't match this filename — confirmed via
   `git check-ignore -v`, case-sensitive substring miss on "Creds" vs "credentials").
2. **Whether the proxy itself needs any access control.** The spec and this plan assume the proxy is
   reachable only by the same-origin frontend in a low-traffic internal demo/reviewer context. If this
   app is ever deployed somewhere reachable beyond a trusted internal network without its own auth
   layer, the proxy becomes a pivot to the (QA-tier, but still real and rate-limited) Touchless
   environment for anyone who can reach it. Worth a explicit decision, not an assumption, before any
   shared/public demo URL is stood up.
3. **PII in logs** — confirm the metadata-only logging discipline (§2.5/§3 of the security review) is
   enforced by code review, not just documented intent; a default `morgan`/`pino` transport added later
   for unrelated debugging is the most likely accidental regression path (flagged in the security
   review as the most probable failure mode, not hypothetical).
4. **SSRF via `documentId`/`applicationId`** — implemented via UUID-format allowlist + fixed base host
   (§2.6, security review §2) — confirm this validation lands in `touchlessClient.ts` itself (a single
   chokepoint both routes call through), not duplicated/forgotten in one of the two route handlers.
5. **CORS** — same-origin via Vite's dev proxy in dev; confirm whatever hosts this in a shared demo
   environment (if any) serves frontend and backend from the same origin too, so no CORS allowlist ever
   needs to be configured at all (simplest and safest option, per security review §5.1).
6. **Dependency audit** — `npm audit --audit-level=high` against `backend/package.json` before first
   ship; this is a **new** dependency surface (first backend in a frontend-only repo) and isn't covered
   by any existing CI job today.
7. **Rate limiting** — a lightweight per-session/per-IP request counter (no new infra) is recommended
   as a guard against an accidental client-side retry loop hammering the vendor endpoint; not a blocker,
   flagged as nice-to-have per the security review.
8. **`documentId == indexedDocId` universality** — verified for one document type (Credit Report) only.
   The fail-closed UUID validation (item 4 above) makes an unverified document type return a distinct,
   visible error rather than silently succeed or silently fail — but a 2-3-document spot-check across
   other `documentType`s (Note, Appraisal, Closing Disclosure) is still worth doing once the proxy
   exists, cheaply, to firm up FR-007's assumption before a demo relies on it for an untested type.
