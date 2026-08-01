# backend — Touchless API proxy

Server-side proxy for the Touchless QA gateway (spec `020-touchless-api-integration`). This is a
new, sibling top-level directory to `frontend/` — kept **out** of `frontend/`'s Vite build tree on
purpose, so vendor credentials and server-only code can never accidentally end up in a browser
bundle. See `specs/020-touchless-api-integration/plan.md` §3 for the full rationale.

**Non-negotiable this proxy must respect** (CLAUDE.md #1 / plan.md): pulled Touchless data is
display/citation-only. It never feeds `p0/qc_engine`'s deterministic evaluation, and this backend
has zero shared code with `p0/`.

## What this is (and isn't)

- A thin, mostly-stateless HTTP proxy between the frontend and the Touchless QA gateway.
- Holds a short-lived in-memory OAuth token cache — the only server-side state.
- Never writes pulled data to disk. Never sends vendor credentials or a bearer token to the browser.

This scaffold (Phase 4) wires the skeleton only. The real proxy logic (OAuth token exchange,
request forwarding, UUID validation, error mapping) is implemented in Phase 6 — see the stub file
headers in `src/` for what each file will eventually contain.

## Run it

```bash
cd backend
npm install
cp .env.example .env   # then fill in real values — see "Required environment variables" below
npm run dev            # starts the Express server on PORT (default 4000), auto-reloads on change
```

Other scripts:

```bash
npm run build      # tsc -p tsconfig.json -> dist/
npm start           # node dist/server.js (run the built output)
npm run typecheck   # tsc --noEmit
npm run audit        # npm audit --audit-level=high
```

Health check once running:

```bash
curl http://localhost:4000/api/health
# {"status":"ok"}
```

## Required environment variables

All required at startup — `config.ts` fails fast (throws before the server binds) if any are
missing. See `.env.example` for the committed placeholder template; `.env` itself is gitignored
and must never be committed (root `.gitignore`'s `.env` / `.env.*` patterns cover this).

| Variable | Purpose |
|---|---|
| `TOUCHLESS_CLIENT_ID` | OAuth client id for the `client_credentials` grant against the Touchless gateway |
| `TOUCHLESS_CLIENT_SECRET` | OAuth client secret — QA-tier only, never a production secret |
| `TOUCHLESS_BASE_URL` | Fixed base host for all outbound Touchless calls (e.g. `https://qa-touchless.tavant.com`) — never client-influenced, this is the SSRF guard |
| `PORT` | Port this Express server listens on in dev (frontend's `vite.config.ts` proxies `/api` here) |
| `REQUEST_TIMEOUT_MS` | Outbound request timeout before the proxy returns a `TIMEOUT` error envelope |

## Token caching & refresh

The proxy holds exactly one OAuth token in memory at a time (`tokenCache.ts`) — this is its only
server-side state besides request-scoped values. Useful to know when debugging an auth failure:

- A cached token is reused until `expiresAt` minus a 60-second margin, then a fresh token is
  requested via `POST /userservice/oauth/token?grant_type=client_credentials` (HTTP Basic auth with
  `TOUCHLESS_CLIENT_ID`/`TOUCHLESS_CLIENT_SECRET`). The margin exists so a call started just before
  expiry doesn't race the token dying mid-flight.
- On a `401` from any forwarded Touchless call, the proxy discards the cached token, requests exactly
  **one** fresh token, and retries the original call **exactly once**. If that retry also returns
  `401`, the proxy gives up and returns an `AUTH_FAILURE` error envelope to the browser — it does not
  retry further. If you see `AUTH_FAILURE` in the browser, the credentials themselves are the first
  thing to check (`TOUCHLESS_CLIENT_ID`/`TOUCHLESS_CLIENT_SECRET` in `.env`), not a transient network
  blip.
- Observed QA-tier token lifetime is `expires_in ≈ 59999s` (~16.7 hours), so natural expiry is
  unlikely to occur mid-demo — the refresh-on-401 path is what you'll actually see fire if the QA
  secret is ever rotated or revoked.
- Restarting the proxy (`npm run dev`) always clears this cache — there is no persistence across
  process restarts by design (see `src/decisions/032-backend-proxy-node-express-sibling-directory.md`
  and the security review's token-handling section).

## Dev integration with `frontend/`

`frontend/vite.config.ts` proxies `/api` to this server's dev port so the browser only ever talks
same-origin — no CORS needed in the common local-dev case. Run both dev servers side by side:

```bash
# terminal 1
cd backend && npm run dev

# terminal 2
cd frontend && npm run dev
```

## Where this fits

Full architecture, API contract, and error taxonomy: `specs/020-touchless-api-integration/plan.md`.
Full task breakdown: `specs/020-touchless-api-integration/tasks.md`.
