import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

// FR-016 (spec024): route/block/check authoring here MUST NOT alter or interact with the
// live QC-audit demo's data source -- these are two deliberately separate surfaces
// (spec019/020). Static-text guard, not just "doesn't happen to import it today", so a
// future edit that reaches for dataSourceContext/auditRuns fails loudly instead of silently
// crossing the boundary.
const AUTHORING_FILES = [
  "RouteDetail.tsx",
  "BlockDetail.tsx",
  "RouteDagView.tsx",
  "BlockMembershipModal.tsx",
  "Modal.tsx",
];

const FORBIDDEN_REFERENCES = ["dataSourceContext", "auditRuns"];

const here = dirname(fileURLToPath(import.meta.url));

describe("FR-016: authoring surface stays isolated from the live QC-audit state", () => {
  it.each(AUTHORING_FILES)("%s does not reference the audit-demo data source", (file) => {
    const source = readFileSync(resolve(here, "..", file), "utf-8");
    for (const forbidden of FORBIDDEN_REFERENCES) {
      expect(source).not.toContain(forbidden);
    }
  });
});
