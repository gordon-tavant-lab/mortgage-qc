/// <reference types="vitest/config" />
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 3000,
    proxy: {
      // Forward same-origin /api/* calls to the backend/ Touchless proxy (spec 020)
      // in dev, so the browser never talks cross-origin and never holds vendor
      // credentials. See specs/020-touchless-api-integration/plan.md §2.6/§3.
      "/api": {
        target: "http://localhost:4000",
        changeOrigin: true,
      },
    },
  },
  test: {
    // Feature 020, Phase 5 (TEST, Red): component/hook tests need a DOM.
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    include: ["src/**/*.test.{ts,tsx}"],
    testTimeout: 5000,
    restoreMocks: true,
  },
})
