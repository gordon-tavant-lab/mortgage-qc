// LoanQueue.test.tsx — 021-touchless-audit-run T035 (SC-006): forcing an audit-run error
// (e.g. the Python subprocess failing, or the backend being killed mid-run -- see
// backend/src/__tests__/audit.route.test.ts's PROXY_ERROR coverage for that side) must
// never surface as an error badge in the Loan Queue grid (FR-006a) -- that state belongs
// in the loan detail view / the fetch trigger's own inline message instead.
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LoanQueue } from "../LoanQueue";
import { LoanDetail } from "../LoanDetail";
import * as dataSourceContext from "../../lib/dataSourceContext";

const APPLICATION_ID = "0eb57730-6d2e-4a6d-8db3-bc1217c77b90"; // LN-2026-9042
const LOAN_ID = "LN-2026-9042";

function mockUseDataSource(overrides: Partial<ReturnType<typeof dataSourceContext.useDataSource>>) {
  return vi.spyOn(dataSourceContext, "useDataSource").mockReturnValue({
    mode: "live",
    setMode: vi.fn(),
    pulledApplications: new Map(),
    retrievedDocuments: new Map(),
    auditRuns: new Map(),
    runAudit: vi.fn(),
    narratives: new Map(),
    generateNarrative: vi.fn(),
    resetFetchedApplications: vi.fn(),
    pullApplication: vi.fn(),
    getOrFetchDocument: vi.fn(),
    isPullingApplication: () => false,
    applicationError: () => undefined,
    documentError: () => undefined,
    ...overrides,
  } as unknown as ReturnType<typeof dataSourceContext.useDataSource>);
}

function errorAuditRuns(message: string) {
  return new Map([[APPLICATION_ID, { status: "error" as const, message }]]);
}

describe("LoanQueue — SC-006 error-path suppression", () => {
  it("renders zero error badges in the grid when the real demo loan's audit run failed", () => {
    mockUseDataSource({
      auditRuns: errorAuditRuns("The audit-run subprocess failed: Command failed with exit code 1"),
    });

    render(<LoanQueue onOpenLoan={vi.fn()} />);

    expect(screen.queryByText(/error/i)).not.toBeInTheDocument();
    // The affected row falls back to the same neutral look as "not yet evaluated" --
    // confirm that IS shown, proving the row still renders (not silently hidden either).
    expect(screen.getByText("Not Yet Evaluated")).toBeInTheDocument();
  });

  it("still shows the 19 cosmetic loans' PASS badges normally alongside the errored real loan", () => {
    mockUseDataSource({
      auditRuns: errorAuditRuns("subprocess failure"),
    });

    render(<LoanQueue onOpenLoan={vi.fn()} />);

    expect(screen.getAllByText("Pass").length).toBeGreaterThan(0);
  });
});

describe("LoanDetail — the error DOES surface here, per SC-006's other half", () => {
  it("shows the error state in the loan detail view when the audit run failed", () => {
    mockUseDataSource({
      auditRuns: errorAuditRuns("The audit-run subprocess produced unparseable output."),
    });

    render(<LoanDetail loanId={LOAN_ID} initialTab="inspect" onBack={vi.fn()} />);

    expect(screen.getByText("Error")).toBeInTheDocument();
  });
});
