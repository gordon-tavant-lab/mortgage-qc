// vitest.config.ts — Phase 5 (TEST, Red) test runner config for the Touchless proxy.
// Node environment (this is a server, not a browser target). setupEnv.ts seeds fake
// TOUCHLESS_* env vars BEFORE any test file imports config.ts/server.ts, so tests never
// depend on (or risk leaking) the real backend/.env secret.
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "node",
    setupFiles: ["./src/__tests__/setupEnv.ts"],
    include: ["src/__tests__/**/*.test.ts"],
    testTimeout: 5000,
    hookTimeout: 5000,
    restoreMocks: true,
  },
});
