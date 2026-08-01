// src/test/setup.ts — global test setup (vitest `setupFiles`, see vite.config.ts `test.setupFiles`).
// Extends `expect` with jest-dom matchers (toBeInTheDocument, toHaveTextContent, etc.) for
// every test file in the suite.
import "@testing-library/jest-dom/vitest";
import { afterEach } from "vitest";
import { cleanup } from "@testing-library/react";

// `vite.config.ts` does not set `test.globals: true`, so testing-library's own
// auto-cleanup (which detects a global `afterEach`) never registers. Without this,
// `render()` calls across tests in the same file are never unmounted, so multiple
// stale elements from earlier tests remain in the DOM and later `getByRole` queries
// that expect exactly one match throw a "multiple elements found" error.
afterEach(() => {
  cleanup();
});
