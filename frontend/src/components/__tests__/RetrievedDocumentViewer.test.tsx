// RetrievedDocumentViewer.test.tsx — T012 component tests: distinct error states per error
// code (spec Edge Cases: "shown as a distinct error state, not treated as a successful empty
// result"), plus the happy-path real-content render. Traces to FR-006, FR-008, FR-009, SC-002.
//
// ASSUMED PROPS/CONTRACT: `<RetrievedDocumentViewer documentId={string} onClose={() => void} />`,
// reading `useDataSource()`'s `retrievedDocuments` Map + a `documentError(id)` accessor
// (mirroring `applicationError(id)` from dataSourceContext.test.tsx). Each error state renders
// a `data-testid="document-error-<CODE>"` node so "distinct" is asserted structurally, not just
// by loosely matching a message substring (per the task brief: "not just a generic 'error'
// string"). 6 of the 7 plan.md §2.5 codes apply here — INVALID_INPUT is excluded because a
// citation's documentId always comes from an already-pulled, already-validated document list;
// it is not a realistic viewer-level state.
//
// RED (expected, Phase 5): `RetrievedDocumentViewer.tsx` doesn't exist yet — every test below
// fails at the top-level import.
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RetrievedDocumentViewer } from "../RetrievedDocumentViewer";
import * as dataSourceContext from "../../lib/dataSourceContext";

const DOCUMENT_ID = "632a9c26-d636-4564-b89d-256a5dfe70d4";

type ErrorEnvelope = {
  code: string;
  message: string;
  upstreamStatus: number | null;
  retryable: boolean;
  requestId: string;
  timestamp: string;
};

function envelope(code: string, message: string, upstreamStatus: number | null): ErrorEnvelope {
  return {
    code,
    message,
    upstreamStatus,
    retryable: code === "AUTH_FAILURE" || code === "TIMEOUT" || code === "UPSTREAM_ERROR",
    requestId: `req-${code}`,
    timestamp: new Date().toISOString(),
  };
}

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
    documentError: () => undefined,
    ...overrides,
  } as unknown as ReturnType<typeof dataSourceContext.useDataSource>);
}

const ERROR_CASES: [code: string, message: string, upstreamStatus: number | null][] = [
  ["AUTH_FAILURE", "Touchless authentication failed after one retry.", 401],
  ["NOT_FOUND", "The requested document could not be found.", 404],
  ["TIMEOUT", "The request to Touchless timed out.", null],
  ["UNEXPECTED_CONTENT_TYPE", "Touchless returned content in an unexpected format.", 200],
  ["UPSTREAM_ERROR", "Touchless returned an unexpected error.", 500],
  ["PROXY_ERROR", "An internal proxy error occurred.", null],
];

describe("RetrievedDocumentViewer", () => {
  it("Acceptance Scenario US2.1 — renders the real fetched document content, distinct from placeholder text", () => {
    mockUseDataSource({
      retrievedDocuments: new Map([
        [
          DOCUMENT_ID,
          {
            documentId: DOCUMENT_ID,
            fetchedAt: new Date().toISOString(),
            pdfObjectUrl: "blob:mock-object-url",
            ocrFields: [{ name: "Borrower_First_Name", value: "ANDY", confidence: 100.0 }],
          },
        ],
      ]),
    });

    render(<RetrievedDocumentViewer documentId={DOCUMENT_ID} onClose={vi.fn()} />);

    // Must not show the existing simulated-viewer placeholder copy (design distinctness, SC-002).
    expect(screen.queryByText(/placeholder/i)).not.toBeInTheDocument();
    expect(screen.getByText("Borrower_First_Name")).toBeInTheDocument();
    expect(screen.getByText("ANDY")).toBeInTheDocument();
  });

  it.each(ERROR_CASES)(
    "Acceptance Scenario US2.3 — renders a distinct error state for %s (not a blank/successful-looking view)",
    (code, message, upstreamStatus) => {
      mockUseDataSource({
        documentError: (id: string) => (id === DOCUMENT_ID ? envelope(code, message, upstreamStatus) : undefined),
      });

      render(<RetrievedDocumentViewer documentId={DOCUMENT_ID} onClose={vi.fn()} />);

      expect(screen.getByTestId(`document-error-${code}`)).toBeInTheDocument();
      expect(screen.getByText(message)).toBeInTheDocument();
    },
  );

  it("every one of the 6 error codes renders a UNIQUELY distinct testid (no two codes collapse to the same generic state)", () => {
    const seenTestIds = new Set<string>();
    for (const [code, message, upstreamStatus] of ERROR_CASES) {
      mockUseDataSource({
        documentError: (id: string) => (id === DOCUMENT_ID ? envelope(code, message, upstreamStatus) : undefined),
      });
      const { unmount, container } = render(
        <RetrievedDocumentViewer documentId={DOCUMENT_ID} onClose={vi.fn()} />,
      );
      const node = container.querySelector(`[data-testid="document-error-${code}"]`);
      expect(node).not.toBeNull();
      const testId = node!.getAttribute("data-testid")!;
      expect(seenTestIds.has(testId)).toBe(false);
      seenTestIds.add(testId);
      unmount();
    }
    expect(seenTestIds.size).toBe(ERROR_CASES.length);
  });

  it("Acceptance Scenario US2.2 — a documentId already in retrievedDocuments does not trigger getOrFetchDocument again on mount", () => {
    const getOrFetchDocument = vi.fn();
    mockUseDataSource({
      getOrFetchDocument,
      retrievedDocuments: new Map([
        [
          DOCUMENT_ID,
          {
            documentId: DOCUMENT_ID,
            fetchedAt: new Date().toISOString(),
            pdfObjectUrl: "blob:mock-object-url",
            ocrFields: [],
          },
        ],
      ]),
    });

    render(<RetrievedDocumentViewer documentId={DOCUMENT_ID} onClose={vi.fn()} />);

    expect(getOrFetchDocument).not.toHaveBeenCalled();
  });
});
