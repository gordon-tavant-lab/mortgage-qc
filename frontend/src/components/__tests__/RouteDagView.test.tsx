import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RouteDagView } from "../RouteDagView";
import type { Block, Route } from "../../lib/types";

function block(id: string, name: string, checkCount = 0): Block {
  return {
    id,
    name,
    description: `${name} description`,
    checkIds: Array.from({ length: checkCount }, (_, i) => `${id}-check-${i}`),
  };
}

const BLOCKS: Block[] = [block("conv-assets", "Assets", 5), block("conv-income", "Income", 3), block("conv-appraisal", "Appraisal", 2)];

function route(blockIds: string[]): Route {
  return { id: "conventional", name: "Conventional", description: "test route", blockIds };
}

describe("RouteDagView", () => {
  it("renders one node per active block, in blockIds order", () => {
    render(<RouteDagView route={route(["conv-income", "conv-assets"])} blocks={BLOCKS} />);
    const names = screen.getAllByText(/^(Assets|Income|Appraisal)$/).map((el) => el.textContent);
    expect(names).toEqual(["Income", "Assets"]);
  });

  it("renders an empty-state message for a route with zero active blocks", () => {
    render(<RouteDagView route={route([])} blocks={BLOCKS} />);
    expect(screen.getByText(/No blocks are active on this route yet/)).toBeInTheDocument();
  });

  it("adds a node when blockIds gains an entry (re-render, no reload)", () => {
    const { rerender } = render(<RouteDagView route={route(["conv-assets"])} blocks={BLOCKS} />);
    expect(screen.queryByText("Income")).not.toBeInTheDocument();
    rerender(<RouteDagView route={route(["conv-assets", "conv-income"])} blocks={BLOCKS} />);
    expect(screen.getByText("Income")).toBeInTheDocument();
  });

  it("removes a node when blockIds loses an entry", () => {
    const { rerender } = render(<RouteDagView route={route(["conv-assets", "conv-income"])} blocks={BLOCKS} />);
    expect(screen.getByText("Income")).toBeInTheDocument();
    rerender(<RouteDagView route={route(["conv-assets"])} blocks={BLOCKS} />);
    expect(screen.queryByText("Income")).not.toBeInTheDocument();
  });

  it("renders no Edit button when onEdit is not provided", () => {
    render(<RouteDagView route={route(["conv-assets"])} blocks={BLOCKS} />);
    expect(screen.queryByText("Edit")).not.toBeInTheDocument();
  });

  it("renders an Edit button and calls onEdit when clicked", () => {
    const onEdit = vi.fn();
    render(<RouteDagView route={route(["conv-assets"])} blocks={BLOCKS} onEdit={onEdit} />);
    fireEvent.click(screen.getByText("Edit"));
    expect(onEdit).toHaveBeenCalledTimes(1);
  });
});
