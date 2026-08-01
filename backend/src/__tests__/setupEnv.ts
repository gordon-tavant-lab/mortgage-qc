// setupEnv.ts — test-only environment configuration for the whole backend test suite.
//
// IMPORTANT: this file intentionally uses a FAKE secret value, never the real Touchless QA
// credential from backend/.env (that file is gitignored and must never be referenced from a
// test). Every test in this suite mocks `global.fetch` — no test in this directory is allowed
// to make a real network call to qa-touchless.tavant.com.
//
// Runs once before the module graph for each test file is loaded (vitest `setupFiles`), so
// config.ts's fail-fast required-env-var check always sees a complete, valid-looking env.
process.env.TOUCHLESS_CLIENT_ID = "test-client-id";
process.env.TOUCHLESS_CLIENT_SECRET = "test-secret";
process.env.TOUCHLESS_BASE_URL = "https://touchless.invalid.test";
process.env.PORT = "4000";
// Short on purpose: the TIMEOUT test suite relies on this being small so it doesn't have to
// wait real seconds for the proxy's own outbound-call deadline to fire.
process.env.REQUEST_TIMEOUT_MS = "150";
