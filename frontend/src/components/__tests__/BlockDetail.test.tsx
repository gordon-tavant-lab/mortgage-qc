import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BlockDetail } from "../BlockDetail";
import type { Block, Check } from "../../lib/types";

function check(id: string, overrides: Partial<Check> = {}): Check {
  return {
    id,
    name: id,
    kind: "predicate",
    category: "Assets",
    fieldId: "some_field",
    predicate: "is_true",
    operator: "<=",
    threshold: "",
    severity: "WARNING",
    description: `${id} description`,
    authorability: "COMPILABLE",
    compileState: "COMPILED",
    ...overrides,
  };
}

const CONV_BLOCK: Block = { id: "conv-assets", name: "Assets", description: "Assets block", checkIds: ["active-1"] };
const FHA_BLOCK: Block = { id: "fha-assets", name: "Assets", description: "FHA assets block", checkIds: [] };

describe("BlockDetail", () => {
  it("hides NOT_COMPILED checks in Available Checks by default", () => {
    const checks: Check[] = [
      check("active-1"),
      check("avail-compiled", { category: "Assets" }),
      check("avail-not-built", {
        category: "Assets",
        authorability: "NEEDS_FIELDS",
        compileState: "NOT_COMPILED",
      }),
    ];
    render(
      <BlockDetail
        block={CONV_BLOCK}
        routeName="Conventional"
        checks={checks}
        allBlocks={[CONV_BLOCK]}
        onToggleCheck={vi.fn()}
        onUpdateCheck={vi.fn()}
        onBack={vi.fn()}
      />
    );
    expect(screen.getByText("avail-compiled")).toBeInTheDocument();
    expect(screen.queryByText("avail-not-built")).not.toBeInTheDocument();
  });

  it("reveals NOT_COMPILED checks when 'Show not built' is checked, hides again when unchecked", () => {
    const checks: Check[] = [
      check("active-1"),
      check("avail-not-built", {
        category: "Assets",
        authorability: "NEEDS_FIELDS",
        compileState: "NOT_COMPILED",
      }),
    ];
    render(
      <BlockDetail
        block={CONV_BLOCK}
        routeName="Conventional"
        checks={checks}
        allBlocks={[CONV_BLOCK]}
        onToggleCheck={vi.fn()}
        onUpdateCheck={vi.fn()}
        onBack={vi.fn()}
      />
    );
    const toggle = screen.getAllByLabelText("Show not built")[0];
    fireEvent.click(toggle);
    expect(screen.getByText("avail-not-built")).toBeInTheDocument();
    fireEvent.click(toggle);
    expect(screen.queryByText("avail-not-built")).not.toBeInTheDocument();
  });

  it("FHA/VA/USDA blocks (non-conv- prefix) always show zero available checks", () => {
    const checks: Check[] = [check("some-conv-check", { category: "Assets" })];
    render(
      <BlockDetail
        block={FHA_BLOCK}
        routeName="FHA"
        checks={checks}
        allBlocks={[FHA_BLOCK]}
        onToggleCheck={vi.fn()}
        onUpdateCheck={vi.fn()}
        onBack={vi.fn()}
      />
    );
    expect(screen.getByText(/gold ruleset covers Conventional only/)).toBeInTheDocument();
    expect(screen.queryByText("some-conv-check")).not.toBeInTheDocument();
  });

  it("paginates the Available Checks list at 25 per page", () => {
    const checks: Check[] = [
      check("active-1"),
      ...Array.from({ length: 30 }, (_, i) => check(`avail-${i}`, { category: "Assets" })),
    ];
    render(
      <BlockDetail
        block={CONV_BLOCK}
        routeName="Conventional"
        checks={checks}
        allBlocks={[CONV_BLOCK]}
        onToggleCheck={vi.fn()}
        onUpdateCheck={vi.fn()}
        onBack={vi.fn()}
      />
    );
    expect(screen.getByText("Showing 1–25 of 30")).toBeInTheDocument();
  });

  it("opens the check editor as a modal on Pencil click, not inline by default", () => {
    const checks: Check[] = [check("active-1", { messagePass: "orig pass", messageFail: "orig fail" })];
    render(
      <BlockDetail
        block={CONV_BLOCK}
        routeName="Conventional"
        checks={checks}
        allBlocks={[CONV_BLOCK]}
        onToggleCheck={vi.fn()}
        onUpdateCheck={vi.fn()}
        onBack={vi.fn()}
      />
    );
    expect(screen.queryByText("Edit Check")).not.toBeInTheDocument();
    fireEvent.click(screen.getByTitle("Edit this check's gate"));
    expect(screen.getByText("Edit Check")).toBeInTheDocument();
  });

  it("discards an in-progress edit on Cancel (reverts via onUpdateCheck with the snapshot)", () => {
    const checks: Check[] = [check("active-1", { messageFail: "orig fail" })];
    const onUpdateCheck = vi.fn();
    render(
      <BlockDetail
        block={CONV_BLOCK}
        routeName="Conventional"
        checks={checks}
        allBlocks={[CONV_BLOCK]}
        onToggleCheck={vi.fn()}
        onUpdateCheck={onUpdateCheck}
        onBack={vi.fn()}
      />
    );
    fireEvent.click(screen.getByTitle("Edit this check's gate"));
    const failBox = screen.getByLabelText("Fail Message");
    fireEvent.change(failBox, { target: { value: "edited fail" } });
    expect(onUpdateCheck).toHaveBeenCalledWith("active-1", expect.objectContaining({ messageFail: "edited fail" }));
    fireEvent.click(screen.getByText("Cancel"));
    // The revert call restores the pre-edit snapshot value.
    expect(onUpdateCheck).toHaveBeenLastCalledWith("active-1", expect.objectContaining({ messageFail: "orig fail" }));
    expect(screen.queryByText("Edit Check")).not.toBeInTheDocument();
  });

  it("keeps an in-progress edit on Done (no revert call)", () => {
    const checks: Check[] = [check("active-1", { messageFail: "orig fail" })];
    const onUpdateCheck = vi.fn();
    render(
      <BlockDetail
        block={CONV_BLOCK}
        routeName="Conventional"
        checks={checks}
        allBlocks={[CONV_BLOCK]}
        onToggleCheck={vi.fn()}
        onUpdateCheck={onUpdateCheck}
        onBack={vi.fn()}
      />
    );
    fireEvent.click(screen.getByTitle("Edit this check's gate"));
    const failBox = screen.getByLabelText("Fail Message");
    fireEvent.change(failBox, { target: { value: "edited fail" } });
    onUpdateCheck.mockClear();
    fireEvent.click(screen.getByText("Done"));
    expect(onUpdateCheck).not.toHaveBeenCalled();
    expect(screen.queryByText("Edit Check")).not.toBeInTheDocument();
  });
});
