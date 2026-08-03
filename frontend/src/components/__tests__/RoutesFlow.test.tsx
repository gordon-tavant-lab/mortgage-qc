// RoutesFlow.test.tsx — spec024 Phase 13/T049 (from /speckit-converge): a real regression
// (restoreToGold could leave `nav` pointing at a route/block it had just deleted, rendering a
// blank page -- fixed by having restoreToGold also reset `nav` to the list) was previously
// verified only by live manual browser testing, per spec.md's Edge Case "Is a deleted custom
// block/check recoverable?". This locks that behavior in for CI.
import type { ReactNode } from "react";
import { render, screen, fireEvent, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { RoutesFlow } from "../RoutesFlow";
import { DataSourceProvider } from "../../lib/dataSourceContext";

function wrapper({ children }: { children: ReactNode }) {
  return <DataSourceProvider>{children}</DataSourceProvider>;
}

describe("RoutesFlow: restoreToGold", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  it("clears a custom block and resets nav to the route list, even while viewing that block", () => {
    render(<RoutesFlow />, { wrapper });

    fireEvent.click(screen.getByRole("button", { name: /^Conventional/ }));
    fireEvent.click(screen.getByTitle("Edit which blocks are active on this route"));
    fireEvent.click(screen.getByText("New Block"));
    fireEvent.change(screen.getByLabelText("Block Name"), { target: { value: "Regression Test Block" } });
    fireEvent.click(screen.getByText("Create Block"));

    // Activate it so it's reachable from the Active Blocks list (only Active rows navigate).
    fireEvent.click(screen.getByTitle("Activate this block on the route"));
    fireEvent.click(screen.getByText(/Activate on this route/));

    // Navigate into the new block's BlockDetail page.
    const modal = screen.getByText("Edit Blocks").closest('[role="dialog"]') as HTMLElement;
    fireEvent.click(within(modal).getByText("Regression Test Block"));

    expect(screen.getByRole("heading", { name: "Regression Test Block" })).toBeInTheDocument();

    // Reset while still viewing the now-to-be-deleted custom block.
    fireEvent.click(screen.getByTitle("Discard local edits and reset to the original gold-sourced catalog"));

    // Must land back on the route list -- not a blank page, not still on the deleted block.
    expect(screen.getByText("Configured Routes")).toBeInTheDocument();
    expect(screen.queryByText("Regression Test Block")).not.toBeInTheDocument();
  });
});
