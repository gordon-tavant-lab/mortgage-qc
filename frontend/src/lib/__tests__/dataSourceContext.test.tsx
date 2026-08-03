// dataSourceContext.test.tsx — T011 unit tests for `DataSourceProvider`/`useDataSource()`
// (spec 020, plan.md §2.3/§2.4/§3). Traces to FR-003, FR-004, FR-005.
//
// ASSUMED CONTRACT (plan.md's file-layout comment only names `mode`, `setMode`,
// `pulledApplications`/`retrievedDocuments` Maps, `pullApplication(id)`, and
// `getOrFetchDocument(id)` — it does not spell out the exact shape of loading/error state or
// the "explicit, separate re-pull action" FR-005 requires). This test file fixes that
// contract so Phase 6 has something concrete to implement against:
//   useDataSource(): {
//     mode: "stored" | "live"; setMode(mode): void;
//     pulledApplications: Map<string, PulledApplication>;
//     retrievedDocuments: Map<string, RetrievedDocument>;
//     pullApplication(id: string, options?: { force?: boolean }): Promise<void>;
//     getOrFetchDocument(id: string): Promise<void>;
//     isPullingApplication(id: string): boolean;
//     applicationError(id: string): ErrorEnvelope | undefined;
//   }
// `pullApplication(id, { force: true })` is this file's proposed answer to FR-005's "explicit,
// separate re-pull action" — a second, distinct call shape on the same function, not a second
// exported function name, since plan.md's file layout lists only one. If Phase 6 lands a
// different shape (e.g. a separate `rePullApplication`), update this file alongside it.
//
// RED (expected, Phase 5): `dataSourceContext.tsx` doesn't exist yet — every test below fails
// at the top-level import.
import type { ReactNode } from "react";
import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { DataSourceProvider, useDataSource } from "../dataSourceContext";

const APPLICATION_ID = "0eb57730-6d2e-4a6d-8db3-bc1217c77b90";

function wrapper({ children }: { children: ReactNode }) {
  return <DataSourceProvider>{children}</DataSourceProvider>;
}

function mockPullResponse(applicationId: string, overrides: Record<string, unknown> = {}) {
  return new Response(
    JSON.stringify({
      applicationId,
      fetchedAt: new Date().toISOString(),
      source: "live",
      application: { loanSummary: { status: "CLEAR" } },
      ...overrides,
    }),
    { status: 200, headers: { "content-type": "application/json" } },
  );
}

describe("useDataSource", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("Acceptance Scenario US3.1 — the toggle defaults to 'stored'", () => {
    const { result } = renderHook(() => useDataSource(), { wrapper });
    expect(result.current.mode).toBe("stored");
  });

  it("Acceptance Scenario US3.2 — setMode('live') flips the active data source", () => {
    const { result } = renderHook(() => useDataSource(), { wrapper });

    act(() => {
      result.current.setMode("live");
    });

    expect(result.current.mode).toBe("live");
  });

  it("Acceptance Scenario US3.3 — a fresh provider mount (new session) always resets to 'stored', never persists", () => {
    const { result, unmount } = renderHook(() => useDataSource(), { wrapper });
    act(() => {
      result.current.setMode("live");
    });
    expect(result.current.mode).toBe("live");

    // Simulates a new browser session: no sessionStorage/localStorage exists to survive this,
    // by design (FR-004, plan.md §2.3) — a fresh mount must start from "stored" again.
    unmount();
    const remount = renderHook(() => useDataSource(), { wrapper });

    expect(remount.result.current.mode).toBe("stored");
  });

  it("Acceptance Scenario US1.1 / US1.2 — pullApplication(id) fetches once and caches; a second call for the same id does not re-fetch", async () => {
    // mockImplementation (not mockResolvedValue) -- each call needs its OWN Response
    // instance, since a real fetch() Response body can only be read once via .json(),
    // and this test now exercises 3 real fetch calls per pull (application + the
    // spec021 FR-003 auto-triggered audit run + live-demo-engine-wiring's own
    // auto-triggered decision-narrative call once that audit resolves), each of which
    // calls .json().
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(mockPullResponse(APPLICATION_ID)));
    vi.stubGlobal("fetch", fetchMock);

    const { result } = renderHook(() => useDataSource(), { wrapper });

    await act(async () => {
      await result.current.pullApplication(APPLICATION_ID);
    });
    await act(async () => {
      await result.current.pullApplication(APPLICATION_ID);
    });

    // 3 calls, not 1: spec021 FR-003 auto-triggers a real audit run the instant a pull
    // resolves (POST /api/audit/:id/run), and that audit run's own success path
    // auto-triggers the decision narrative (POST /api/audit/:id/narrative) -- the second
    // pullApplication() call is a cache hit (no re-fetch of the application itself, still
    // true to this test's own name), but the FIRST call's chain (pull -> audit -> narrative)
    // is 3 genuine fetch calls.
    expect(fetchMock).toHaveBeenCalledTimes(3);
    expect(result.current.pulledApplications.get(APPLICATION_ID)).toBeDefined();
  });

  it("FR-005 — an explicit re-pull (force) action triggers a genuinely new fetch", async () => {
    // See the previous test's comment: a fresh Response instance per call is required
    // now that each pull also triggers its own audit-run fetch (spec021 FR-003) and each
    // audit run triggers its own narrative fetch (live-demo-engine-wiring).
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(mockPullResponse(APPLICATION_ID)));
    vi.stubGlobal("fetch", fetchMock);

    const { result } = renderHook(() => useDataSource(), { wrapper });

    await act(async () => {
      await result.current.pullApplication(APPLICATION_ID);
    });
    await act(async () => {
      await result.current.pullApplication(APPLICATION_ID, { force: true });
    });

    // 6 calls, not 2: each pull (including the forced re-pull, which bypasses the
    // cache-hit guard entirely) auto-triggers its own audit run (spec021 FR-003), which
    // auto-triggers its own narrative generation -- (pull + audit + narrative) x 2 = 6.
    expect(fetchMock).toHaveBeenCalledTimes(6);
  });

  it("Acceptance Scenario US1.3 — a failed pull surfaces an error and does not populate stale/fixture data in its place", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          error: {
            code: "NOT_FOUND",
            message: "The requested application could not be found.",
            upstreamStatus: 404,
            retryable: false,
            requestId: "req-1",
            timestamp: new Date().toISOString(),
          },
        }),
        { status: 404, headers: { "content-type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    const { result } = renderHook(() => useDataSource(), { wrapper });

    await act(async () => {
      await result.current.pullApplication(APPLICATION_ID);
    });

    await waitFor(() => {
      expect(result.current.applicationError(APPLICATION_ID)).toBeDefined();
    });
    expect(result.current.applicationError(APPLICATION_ID)?.code).toBe("NOT_FOUND");
    expect(result.current.pulledApplications.has(APPLICATION_ID)).toBe(false);
  });

  it("021-touchless-audit-run US2/T025 — resetFetchedApplications() clears the pulled application, its audit run, and any errors, matching a fresh provider mount", async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(mockPullResponse(APPLICATION_ID)));
    vi.stubGlobal("fetch", fetchMock);

    const { result } = renderHook(() => useDataSource(), { wrapper });

    await act(async () => {
      await result.current.pullApplication(APPLICATION_ID);
    });
    expect(result.current.pulledApplications.has(APPLICATION_ID)).toBe(true);
    await waitFor(() => {
      expect(result.current.auditRuns.has(APPLICATION_ID)).toBe(true);
    });

    act(() => {
      result.current.resetFetchedApplications();
    });

    expect(result.current.pulledApplications.size).toBe(0);
    expect(result.current.auditRuns.size).toBe(0);
    expect(result.current.applicationError(APPLICATION_ID)).toBeUndefined();
    expect(result.current.isPullingApplication(APPLICATION_ID)).toBe(false);
  });

  it("021-touchless-audit-run US2/T025 — resetFetchedApplications() also clears retrieved documents/errors, so a citation-viewed document doesn't survive a restore", async () => {
    const { result } = renderHook(() => useDataSource(), { wrapper });

    act(() => {
      result.current.resetFetchedApplications();
    });

    expect(result.current.retrievedDocuments.size).toBe(0);
    expect(result.current.documentError("any-doc-id")).toBeUndefined();
  });
});
