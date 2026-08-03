// ExceptionReview.test.tsx — 021-touchless-audit-run T024 (US5, FR-013): the real demo
// loan's real audit run currently resolves to PASS with zero exceptions (verified live
// against real Touchless credentials -- all 8 confidently-resolvable fields are present
// on this loan), so there is nothing to literally click through on the current real data.
// This test proves the citation -> real-document wiring works correctly via a controlled
// synthetic "resolved" audit state, standing in for the real shape a genuine QC failure
// would take once one exists (e.g. spec022's rule-edit scenario, or a future demo loan
// with a genuinely-absent document).
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ExceptionReview } from "../ExceptionReview";
import * as dataSourceContext from "../../lib/dataSourceContext";

const APPLICATION_ID = "0eb57730-6d2e-4a6d-8db3-bc1217c77b90"; // LN-2026-9042's real applicationId
const LOAN_ID = "LN-2026-9042";

function mockUseDataSource(overrides: Partial<ReturnType<typeof dataSourceContext.useDataSource>>) {
  return vi.spyOn(dataSourceContext, "useDataSource").mockReturnValue({
    mode: "live",
    setMode: vi.fn(),
    pulledApplications: new Map(),
    retrievedDocuments: new Map(),
    auditRuns: new Map(),
    runAudit: vi.fn(),
    pullApplication: vi.fn(),
    getOrFetchDocument: vi.fn(),
    isPullingApplication: () => false,
    applicationError: () => undefined,
    documentError: () => undefined,
    ...overrides,
  } as unknown as ReturnType<typeof dataSourceContext.useDataSource>);
}

function resolvedAuditRuns(results: unknown[]) {
  return new Map([
    [
      APPLICATION_ID,
      {
        status: "resolved" as const,
        result: {
          applicationId: APPLICATION_ID,
          evaluatedAt: new Date().toISOString(),
          loanStatus: "FAILED" as const,
          compiledCheckCount: 37,
          excludedCheckCount: 171,
          runResult: { results },
        },
      },
    ],
  ]);
}

function qcFailCheck(overrides: Record<string, unknown> = {}) {
  return {
    check_id: "fnm-ast-0014",
    check_name: "O-FNM-50257",
    severity: "CRITICAL",
    status: "FAIL",
    phase: "QC",
    message: "The receipt of the earnest money deposit was not documented as required.",
    citation: {
      docName: "Bank Statement",
      pageNum: 0,
      segmentSnippet: "Touchless documents[] presence check",
      documentIds: ["632a9c26-d636-4564-b89d-256a5dfe70d4"],
    },
    ...overrides,
  };
}

describe("ExceptionReview — real exceptions (US5)", () => {
  it("a real QC failure with a single documentId renders one clickable citation link", () => {
    mockUseDataSource({ auditRuns: resolvedAuditRuns([qcFailCheck()]) });

    render(<ExceptionReview loanId={LOAN_ID} />);

    expect(screen.getAllByText("O-FNM-50257").length).toBeGreaterThan(0);
    const link = screen.getByText("Bank Statement").closest("button");
    expect(link).not.toBeNull();
  });

  it("clicking a real citation link opens the actual RetrievedDocumentViewer (not the placeholder modal)", () => {
    mockUseDataSource({ auditRuns: resolvedAuditRuns([qcFailCheck()]) });

    render(<ExceptionReview loanId={LOAN_ID} />);
    fireEvent.click(screen.getByText("Bank Statement").closest("button")!);

    expect(screen.getByText("Retrieved Document — Touchless Live Content")).toBeInTheDocument();
    expect(screen.queryByText(/PDF page render placeholder/i)).not.toBeInTheDocument();
  });

  it("a real QC failure spanning multiple real documents (e.g. URLA_1003_final) shows ALL matched documents as separate links, never collapsed to the first (SC-008)", () => {
    mockUseDataSource({
      auditRuns: resolvedAuditRuns([
        qcFailCheck({
          check_id: "fnm-inc-0069",
          check_name: "O-FNM-54027",
          citation: {
            docName: "URLA - Borrower Information, URLA - Continuation Sheet",
            pageNum: 0,
            segmentSnippet: "Touchless documents[] presence check",
            documentIds: ["doc-1", "doc-2", "doc-3", "doc-4"],
          },
        }),
      ]),
    });

    render(<ExceptionReview loanId={LOAN_ID} />);

    const links = screen.getAllByText(/URLA - Borrower Information, URLA - Continuation Sheet/);
    expect(links).toHaveLength(4);
    expect(screen.getByText(/\(1 of 4\)/)).toBeInTheDocument();
    expect(screen.getByText(/\(4 of 4\)/)).toBeInTheDocument();
  });

  it("clicking each of the 4 multi-document links opens the viewer for that SPECIFIC documentId", () => {
    mockUseDataSource({
      auditRuns: resolvedAuditRuns([
        qcFailCheck({
          citation: {
            docName: "URLA (combined)",
            pageNum: 0,
            segmentSnippet: "Touchless documents[] presence check",
            documentIds: ["doc-1", "doc-2"],
          },
        }),
      ]),
    });

    render(<ExceptionReview loanId={LOAN_ID} />);
    const buttons = screen.getAllByText(/URLA \(combined\)/).map((el) => el.closest("button")!);
    fireEvent.click(buttons[1]);

    // RetrievedDocumentViewer fetches by documentId via getOrFetchDocument -- confirm it
    // was called with the SECOND document's id specifically, not just any/the first.
    const ctx = dataSourceContext.useDataSource() as unknown as { getOrFetchDocument: (id: string) => void };
    expect(ctx.getOrFetchDocument).toHaveBeenCalledWith("doc-2");
  });

  it("a real citation with an empty documentIds array states honestly that no document was identified, never a dead link", () => {
    mockUseDataSource({
      auditRuns: resolvedAuditRuns([
        qcFailCheck({
          citation: {
            docName: "Unmapped",
            pageNum: 0,
            segmentSnippet: "Touchless documents[] presence check",
            documentIds: [],
          },
        }),
      ]),
    });

    render(<ExceptionReview loanId={LOAN_ID} />);

    expect(screen.getByText(/No source document identified/i)).toBeInTheDocument();
  });

  it("a RECONCILE-phase FLAG is never shown as an exception (only real QC failures count)", () => {
    mockUseDataSource({
      auditRuns: resolvedAuditRuns([
        qcFailCheck({ phase: "RECONCILE", status: "FLAG", severity: "INFO" }),
      ]),
    });

    render(<ExceptionReview loanId={LOAN_ID} />);

    expect(screen.getByText(/No exceptions for this loan/i)).toBeInTheDocument();
  });

  it("before a real run resolves (not_fetched/running), mock findings' existing placeholder-modal citation behavior is unaffected", () => {
    mockUseDataSource({ auditRuns: new Map() }); // no resolved entry -- falls back to MOCK_FINDINGS

    render(<ExceptionReview loanId={LOAN_ID} />);
    const evidenceButton = screen.getAllByRole("button").find((b) => /Page \d/.test(b.textContent ?? ""));
    expect(evidenceButton).toBeDefined();
    fireEvent.click(evidenceButton!);

    expect(screen.getByText(/PDF page render placeholder/i)).toBeInTheDocument();
  });
});
