import { describe, expect, it } from "vitest";
import { reconcileDraft } from "../rulesetStore";
import type { Block, Check, Route } from "../types";

function check(id: string, category = "Assets"): Check {
  return {
    id,
    name: id,
    kind: "predicate",
    category,
    fieldId: "some_field",
    predicate: "is_true",
    operator: "<=",
    threshold: "",
    severity: "WARNING",
    description: `${id} description`,
  };
}

function block(id: string, checkIds: string[]): Block {
  return { id, name: id, description: "", checkIds };
}

const ROUTES: Route[] = [{ id: "conventional", name: "Conventional", description: "", blockIds: [] }];

describe("reconcileDraft", () => {
  it("prunes a check id that no longer exists in the current gold catalog", () => {
    const draft = {
      routes: ROUTES,
      blocks: [block("conv-assets", ["gold-1", "gold-removed"])],
      checks: [check("gold-1"), check("gold-removed")],
    };
    const { content, missingCheckIds } = reconcileDraft(draft, [check("gold-1")]);
    expect(missingCheckIds).toEqual(["gold-removed"]);
    expect(content.checks.map((c) => c.id)).toEqual(["gold-1"]);
    expect(content.blocks[0].checkIds).toEqual(["gold-1"]);
  });

  // spec024 US8 regression guard: before this fix, reconcileDraft rebuilt `checks`
  // from ONLY the ids present in the current gold catalog -- so a rule-author-created
  // check (never gold-sourced, id prefixed "custom-check-") was silently deleted, and
  // its owning block's checkIds entry misreported as "missing", on every reload.
  it("keeps a custom-authored check (not gold-sourced) instead of treating it as missing", () => {
    const draft = {
      routes: ROUTES,
      blocks: [block("conv-assets", ["gold-1", "custom-check-1"])],
      checks: [check("gold-1"), check("custom-check-1")],
    };
    const { content, missingCheckIds } = reconcileDraft(draft, [check("gold-1")]);
    expect(missingCheckIds).toEqual([]);
    expect(content.checks.map((c) => c.id).sort()).toEqual(["custom-check-1", "gold-1"]);
    expect(content.blocks[0].checkIds).toEqual(["gold-1", "custom-check-1"]);
  });
});
