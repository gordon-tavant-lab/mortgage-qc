import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RouteDetail } from "../RouteDetail";
import type { Block, Route } from "../../lib/types";

function block(id: string, name: string): Block {
  return { id, name, description: `${name} description`, checkIds: [] };
}

const TWO_BLOCKS: Block[] = [block("conv-assets", "Assets"), block("conv-income", "Income")];

function baseRoute(overrides: Partial<Route> = {}): Route {
  return { id: "conventional", name: "Conventional", description: "test route", blockIds: [], ...overrides };
}

describe("RouteDetail", () => {
  it("opens the membership modal on Available Blocks row click instead of toggling immediately", () => {
    const onToggleBlock = vi.fn();
    render(
      <RouteDetail
        route={baseRoute()}
        blocks={TWO_BLOCKS}
        allRoutes={[baseRoute()]}
        onToggleBlock={onToggleBlock}
        onOpenBlock={vi.fn()}
        onBack={vi.fn()}
      />
    );
    fireEvent.click(screen.getAllByTitle("Activate this block on the route")[0]);
    expect(onToggleBlock).not.toHaveBeenCalled();
    expect(screen.getByText("Edit block membership")).toBeInTheDocument();
  });

  it("calls onToggleBlock when the modal is confirmed, then closes", () => {
    const onToggleBlock = vi.fn();
    render(
      <RouteDetail
        route={baseRoute()}
        blocks={TWO_BLOCKS}
        allRoutes={[baseRoute()]}
        onToggleBlock={onToggleBlock}
        onOpenBlock={vi.fn()}
        onBack={vi.fn()}
      />
    );
    fireEvent.click(screen.getAllByTitle("Activate this block on the route")[0]);
    fireEvent.click(screen.getByText(/Activate on this route/));
    expect(onToggleBlock).toHaveBeenCalledWith("conv-assets");
    expect(screen.queryByText("Edit block membership")).not.toBeInTheDocument();
  });

  it("dismissing the modal without confirming never calls onToggleBlock", () => {
    const onToggleBlock = vi.fn();
    render(
      <RouteDetail
        route={baseRoute()}
        blocks={TWO_BLOCKS}
        allRoutes={[baseRoute()]}
        onToggleBlock={onToggleBlock}
        onOpenBlock={vi.fn()}
        onBack={vi.fn()}
      />
    );
    fireEvent.click(screen.getAllByTitle("Activate this block on the route")[0]);
    fireEvent.keyDown(window, { key: "Escape" });
    expect(onToggleBlock).not.toHaveBeenCalled();
    expect(screen.queryByText("Edit block membership")).not.toBeInTheDocument();
  });

  it("the DAG shows a node for every active block and updates immediately when blockIds changes", () => {
    const { rerender } = render(
      <RouteDetail
        route={baseRoute({ blockIds: ["conv-assets"] })}
        blocks={TWO_BLOCKS}
        allRoutes={[baseRoute({ blockIds: ["conv-assets"] })]}
        onToggleBlock={vi.fn()}
        onOpenBlock={vi.fn()}
        onBack={vi.fn()}
      />
    );
    expect(screen.getByText("Active Block Sequence").parentElement).toHaveTextContent("Assets");
    expect(screen.getByText("Active Block Sequence").parentElement).not.toHaveTextContent("Income");
    rerender(
      <RouteDetail
        route={baseRoute({ blockIds: ["conv-assets", "conv-income"] })}
        blocks={TWO_BLOCKS}
        allRoutes={[baseRoute({ blockIds: ["conv-assets", "conv-income"] })]}
        onToggleBlock={vi.fn()}
        onOpenBlock={vi.fn()}
        onBack={vi.fn()}
      />
    );
    expect(screen.getByText("Active Block Sequence").parentElement).toHaveTextContent("Income");
  });

  it("paginates the Available Blocks list at 25 per page", () => {
    const manyBlocks: Block[] = Array.from({ length: 30 }, (_, i) => block(`conv-b${i}`, `Block ${i}`));
    render(
      <RouteDetail
        route={baseRoute()}
        blocks={manyBlocks}
        allRoutes={[baseRoute()]}
        onToggleBlock={vi.fn()}
        onOpenBlock={vi.fn()}
        onBack={vi.fn()}
      />
    );
    expect(screen.getByText("Showing 1–25 of 30")).toBeInTheDocument();
    expect(screen.getByText("Page 1 of 2")).toBeInTheDocument();
    fireEvent.click(screen.getByText("Next"));
    expect(screen.getByText("Showing 26–30 of 30")).toBeInTheDocument();
  });

  it("shows no pagination controls for a list under 25 items", () => {
    render(
      <RouteDetail
        route={baseRoute()}
        blocks={TWO_BLOCKS}
        allRoutes={[baseRoute()]}
        onToggleBlock={vi.fn()}
        onOpenBlock={vi.fn()}
        onBack={vi.fn()}
      />
    );
    expect(screen.queryByText(/^Showing /)).not.toBeInTheDocument();
  });
});
