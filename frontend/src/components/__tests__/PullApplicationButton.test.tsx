// PullApplicationButton.test.tsx — T012 component tests: idle → loading → cached/error
// states, driven by a mocked `useDataSource()` context per state (spec 020, plan.md §3).
// Traces to FR-001, SC-001.
//
// ASSUMED PROPS: `<PullApplicationButton applicationId={string} />` (plan.md: "on LoanDetail" —
// LoanDetail already knows the loan's applicationId in scope). "disabled+tooltip when
// mode='stored'" per plan.md's file-layout comment.
//
// RED (expected, Phase 5): `PullApplicationButton.tsx` doesn't exist yet — every test below
// fails at the top-level import.
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { PullApplicationButton } from "../PullApplicationButton";
import * as dataSourceContext from "../../lib/dataSourceContext";

const APPLICATION_ID = "0eb57730-6d2e-4a6d-8db3-bc1217c77b90";

function mockUseDataSource(overrides: Partial<ReturnType<typeof dataSourceContext.useDataSource>>) {
  return vi.spyOn(dataSourceContext, "useDataSource").mockReturnValue({
    mode: "live",
    setMode: vi.fn(),
    pulledApplications: new Map(),
    retrievedDocuments: new Map(),
    pullApplication: vi.fn(),
    getOrFetchDocument: vi.fn(),
    isPullingApplication: () => false,
    applicationError: () => undefined,
    ...overrides,
  } as ReturnType<typeof dataSourceContext.useDataSource>);
}

describe("PullApplicationButton", () => {
  it("idle state — mode is 'live', nothing pulled yet: button is enabled and invites a pull", () => {
    mockUseDataSource({});

    render(<PullApplicationButton applicationId={APPLICATION_ID} />);

    const button = screen.getByRole("button");
    expect(button).toBeEnabled();
    expect(button).not.toHaveTextContent(/error/i);
  });

  it("disabled state — mode is 'stored': the pull button is disabled (per plan.md file layout)", () => {
    mockUseDataSource({ mode: "stored" });

    render(<PullApplicationButton applicationId={APPLICATION_ID} />);

    expect(screen.getByRole("button")).toBeDisabled();
  });

  it("Acceptance Scenario US1.1 — clicking the idle button triggers pullApplication(applicationId)", async () => {
    const pullApplication = vi.fn().mockResolvedValue(undefined);
    mockUseDataSource({ pullApplication });
    const user = userEvent.setup();

    render(<PullApplicationButton applicationId={APPLICATION_ID} />);
    await user.click(screen.getByRole("button"));

    expect(pullApplication).toHaveBeenCalledWith(APPLICATION_ID);
  });

  it("loading state — shows a distinct loading indicator while the pull is in flight", () => {
    mockUseDataSource({ isPullingApplication: (id: string) => id === APPLICATION_ID });

    render(<PullApplicationButton applicationId={APPLICATION_ID} />);

    expect(screen.getByRole("button")).toHaveTextContent(/pulling|loading/i);
    expect(screen.getByRole("button")).toBeDisabled();
  });

  it("cached state — an already-pulled application shows a distinct 'cached'/'pulled' indicator, not the idle prompt", () => {
    mockUseDataSource({
      pulledApplications: new Map([
        [
          APPLICATION_ID,
          { applicationId: APPLICATION_ID, fetchedAt: new Date().toISOString(), source: "live" as const, application: {} },
        ],
      ]),
    });

    render(<PullApplicationButton applicationId={APPLICATION_ID} />);

    expect(screen.getByRole("button")).toHaveTextContent(/pulled|cached|re-?pull/i);
  });

  it("Acceptance Scenario US1.3 — error state renders a distinct, visible error, never a silent idle-looking button", () => {
    mockUseDataSource({
      applicationError: (id: string) =>
        id === APPLICATION_ID
          ? {
              code: "AUTH_FAILURE",
              message: "Touchless authentication failed after one retry.",
              upstreamStatus: 401,
              retryable: true,
              requestId: "req-err-1",
              timestamp: new Date().toISOString(),
            }
          : undefined,
    });

    render(<PullApplicationButton applicationId={APPLICATION_ID} />);

    expect(screen.getByText(/authentication failed|error|failed/i)).toBeInTheDocument();
  });
});
