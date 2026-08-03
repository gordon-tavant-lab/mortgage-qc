import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BlockMembershipModal } from "../BlockMembershipModal";
import type { Block } from "../../lib/types";

const BLOCK: Block = {
  id: "conv-assets",
  name: "Assets",
  description: "Asset verification checks",
  checkIds: ["a", "b", "c"],
};

describe("BlockMembershipModal", () => {
  it("shows Activate label and calls onConfirm for an inactive block", () => {
    const onConfirm = vi.fn();
    render(<BlockMembershipModal block={BLOCK} isActive={false} usedElsewhere={0} onConfirm={onConfirm} />);
    expect(screen.getByText("Assets")).toBeInTheDocument();
    const btn = screen.getByText(/Activate on this route/);
    fireEvent.click(btn);
    expect(onConfirm).toHaveBeenCalledTimes(1);
  });

  it("shows Deactivate label for an active block", () => {
    render(<BlockMembershipModal block={BLOCK} isActive usedElsewhere={0} onConfirm={vi.fn()} />);
    expect(screen.getByText(/Deactivate on this route/)).toBeInTheDocument();
  });

  it("does not call onConfirm without a click", () => {
    const onConfirm = vi.fn();
    render(<BlockMembershipModal block={BLOCK} isActive={false} usedElsewhere={0} onConfirm={onConfirm} />);
    expect(onConfirm).not.toHaveBeenCalled();
  });

  it("shows the other-routes badge when usedElsewhere > 0", () => {
    render(<BlockMembershipModal block={BLOCK} isActive={false} usedElsewhere={2} onConfirm={vi.fn()} />);
    expect(screen.getByText(/also active in 2 other routes/)).toBeInTheDocument();
  });
});
