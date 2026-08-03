# Feature Specification: Route/Block DAG Visualization & Authoring Editor

**Feature Branch**: `feature/live-demo-engine-wiring` (continuing, not a new branch)
**Created**: 2026-08-03
**Status**: Draft
**Input**: User description: "Rule-author page (RouteDetail/BlockDetail) upgrade: live DAG visualization, modal editing, pagination, not-yet-buildable filtering, block/check membership editing, and real AMQ-derived check counts."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add or remove a block from a route (Priority: P1)

A rule author viewing a route (e.g. "Conventional") wants to control which blocks are
actually part of that route — turning a block on adds every check in that block to the
route's compiled ruleset; turning it off removes them. Today the "Available Blocks" list is
inert (every block is always active, the list always reads "0 / All blocks are active on
this route") — there is no real way to change route membership.

**Why this priority**: Every other capability in this spec (the live DAG, in particular)
is only meaningful once a route's block membership can actually change. This is the
foundational editing capability everything else builds on.

**Independent Test**: Open a route, click a block in "Available Blocks" to activate it,
confirm it now appears in "Active Blocks" with its real check count; click it again (or a
control in "Active Blocks") to deactivate it, confirm it moves back. Reload the page and
confirm the change persisted for the session.

**Acceptance Scenarios**:

1. **Given** a route with an inactive block, **When** the rule author clicks that block in
   "Available Blocks", **Then** the block becomes active on the route, moves to (or is
   reflected in) "Active Blocks", and the route's total active check count updates to
   include that block's real checks.
2. **Given** a route with an active block, **When** the rule author removes it, **Then**
   the block becomes inactive, no longer contributes checks to the route's active total,
   and reappears as available to re-add.
3. **Given** a block is being added or removed, **When** the rule author confirms the
   action, **Then** the edit happens through a popup modal (dimmed page background) rather
   than an inline form that shifts page layout.

---

### User Story 2 - See the route's active blocks as a live diagram (Priority: P2)

A rule author or someone demonstrating this product wants to see, at a glance, what an
audit run actually does for a given route — the real sequence/set of active blocks shown as
a connected diagram, not just a flat list — and wants that diagram to visibly update the
moment a block is turned on or off (User Story 1), without reloading the page or running
anything.

**Why this priority**: This is the requested visual centerpiece, but it depends on User
Story 1 existing first (a DAG with no way to change its inputs is just a static picture).

**Independent Test**: With User Story 1 available, open a route, note the diagram's current
nodes, add a previously-inactive block, and confirm a new node for it appears in the
diagram within the same interaction (no reload). Remove an active block and confirm its
node disappears the same way.

**Acceptance Scenarios**:

1. **Given** a route with N active blocks, **When** the rule author opens that route's
   page, **Then** a diagram is shown, positioned between the route's title/description and
   the Available/Active block lists, with exactly N nodes representing those active blocks.
2. **Given** the diagram is visible, **When** the rule author activates a previously-inactive
   block (User Story 1), **Then** a node for that block appears in the diagram immediately,
   with no page reload and no separate action required.
3. **Given** the diagram is visible, **When** the rule author deactivates an active block,
   **Then** that block's node disappears from the diagram immediately.
4. **Given** the diagram, **When** the rule author looks at it, **Then** it reads left-to-
   right (or top-to-bottom) as a real process — the route's active blocks in a defined
   sequence, not an unordered scatter of boxes — consistent with how this product already
   frames its audit process as a pipeline elsewhere.

---

### User Story 3 - Add or remove a check from a block (Priority: P3)

A rule author viewing a block (e.g. "Property - Appraisal") wants to control which
individual checks within that block are active, the same way User Story 1 controls which
blocks are active within a route.

**Why this priority**: Parallel capability to User Story 1, one level down (check-within-
block instead of block-within-route). Independently valuable and independently testable,
but not a prerequisite for the DAG (which operates at block granularity).

**Independent Test**: Open a block, click a check in "Available Checks" to activate it,
confirm it's reflected as active with an updated count; deactivate it and confirm it
reverts.

**Acceptance Scenarios**:

1. **Given** a block with an inactive check, **When** the rule author activates it via the
   Available Checks box, **Then** the check becomes part of the block's active set and the
   block's active check count updates.
2. **Given** an active check, **When** the rule author removes it, **Then** it's no longer
   part of the block's active set and can be re-added later.
3. **Given** a check is being edited (its catalog field, operator, threshold, severity,
   messages, or citation), **When** the rule author opens that editor, **Then** it opens as
   a popup modal (dimmed page background), matching User Story 1's block-editing modal
   pattern — not the current inline "Edit Check" panel that pushes page content around.

---

### User Story 4 - Find the checks/blocks that matter without an overwhelming list (Priority: P4)

A rule author browsing a block's Available Checks list (which can run into the hundreds)
wants to page through it in manageable chunks, and wants checks that aren't yet buildable
(no compiled logic exists for them yet) hidden by default so the list foregrounds checks
they can actually act on — while still being able to reveal the not-yet-buildable ones on
demand.

**Why this priority**: Pure usability/readability improvement over already-existing lists;
valuable on its own but not blocking the other stories.

**Independent Test**: Open a block whose Available Checks list exceeds 25 items, confirm it's
paginated at 25 per page with working Previous/Next controls; confirm not-yet-buildable
checks are absent from the list by default; toggle the "show not built" checkbox and
confirm they appear, toggle it off and confirm they're hidden again.

**Acceptance Scenarios**:

1. **Given** a list (Available Blocks, Active Blocks, or Available Checks) with more than 25
   items, **When** the rule author views it, **Then** it shows 25 items per page with
   controls to move between pages and a clear "showing X-Y of Z" indicator.
2. **Given** the Available Checks list, **When** the rule author has not touched the "show
   not built" control, **Then** every check with no compiled logic yet (not-yet-buildable)
   is hidden from the list and excluded from its shown counts.
3. **Given** the "show not built" checkbox, **When** the rule author checks it, **Then**
   the not-yet-buildable checks appear in the list (clearly marked as such, matching this
   product's existing "not yet buildable" labeling); **When** they uncheck it, **Then**
   those checks are hidden again.

---

### User Story 5 - See an honest, non-fabricated check count on FHA/VA/USDA routes (Priority: P5)

Someone reviewing the FHA, VA, or USDA routes wants the shown block/check counts to reflect
reality: the gold ruleset is compiled from the Fannie Mae Selling Guide and covers
Conventional loans only. FHA, VA, and USDA have no checks compiled into the gold ruleset
today. The route pages should show those programs' real block structure (the same 16
blocks Conventional has) with an honest zero check count, not a fabricated non-zero
placeholder styled to look like a real, compiled number.

**Why this priority**: A data-honesty fix, independent of every UI capability above —
valuable on its own, lowest priority only because it removes a value rather than adding an
interaction.

**Independent Test**: Open the FHA (or VA, or USDA) route and confirm it shows the same 16
blocks as Conventional, each with 0 checks, and the route/block check-count totals read 0 —
not the previous simulated non-zero placeholder ("16 blocks / 221 checks") that was
identical across all three programs.

**Acceptance Scenarios**:

1. **Given** the FHA route, **When** its blocks and check count are shown, **Then** the same
   16 blocks Conventional has are listed, and the total check count reads 0 (no fabricated
   non-zero value).
2. **Given** VA and USDA routes, **When** their blocks and counts are shown, **Then** each
   shows the same 16-block structure with 0 checks — consistent with each other because
   they share the same real underlying fact (no gold-ruleset coverage), not because of a
   copied placeholder value.
3. **Given** the demo as a whole, **When** a viewer looks for real, compiled checks, **Then**
   they only ever appear under the Conventional route and its blocks — FHA/VA/USDA never
   display checks that don't actually exist in the gold ruleset.

### Edge Cases

- What happens when a rule author tries to deactivate the last active block on a route (a
  route with zero active blocks)? The system should allow it — an author mid-edit may
  intentionally clear a route before rebuilding it — but the route's dependent views (e.g.
  the live DAG) must handle an empty active set gracefully (no broken/empty diagram render).
- What happens when a check being edited in the modal has unsaved changes and the rule
  author dismisses the modal (clicks outside it, presses Escape, or clicks a close
  control)? Changes must not be silently applied — dismissing without an explicit save/
  confirm action discards the edit.
- What happens when the "show not built" toggle is on and the rule author also applies the
  existing Search/Severity/Kind/AOR filters? Both must combine correctly — not-yet-buildable
  checks that match the current filters appear; ones that don't, don't.
- What happens on a route/block whose available list has fewer than 25 items? Pagination
  controls should not appear (or should appear in a disabled/inert single-page state) rather
  than showing a confusing "Page 1 of 1" for a 3-item list.
- What happens if the AMQ workbook data underlying a program's (FHA/VA/USDA) real check
  count is later regenerated/recompiled? The shown counts must reflect the current real
  data, not a stale cached number from a previous generation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Rule authors MUST be able to activate a currently-inactive block on a route
  from the "Available Blocks" list, and deactivate a currently-active block from the
  "Active Blocks" list.
- **FR-002**: Block activation/deactivation on a route MUST open as a popup modal dialog
  (page content behind it visibly dimmed), not as an inline panel that reflows the page.
- **FR-003**: A route's active-block total and active-check total MUST update immediately
  after a block is activated or deactivated, without requiring a page reload.
- **FR-004**: Every route page MUST show a diagram of that route's currently-active blocks,
  positioned between the route's title/description and its Available/Active block lists.
- **FR-005**: The diagram MUST re-render to add or remove a block's node within the same
  interaction that activates or deactivates that block (User Story 1) — no reload, no
  separate manual refresh/run action.
- **FR-006**: The diagram MUST present the active blocks as a connected, directed sequence
  (a real process flow), not an unordered set of disconnected boxes.
- **FR-007**: Rule authors MUST be able to activate a currently-inactive check within a
  block from that block's "Available Checks" list, and deactivate an active one.
- **FR-008**: The existing check editor (catalog field, operator, threshold, severity, pass/
  fail messages, source citation) MUST open as a popup modal dialog (page content behind it
  visibly dimmed), replacing its current inline/full-width presentation.
- **FR-009**: Dismissing either modal (block-edit or check-edit) without an explicit save/
  confirm action MUST discard any in-progress changes.
- **FR-010**: Any list of Available Blocks, Active Blocks, or Available Checks with more
  than 25 items MUST be paginated at 25 items per page, with Previous/Next navigation and a
  "showing X-Y of Z" indicator, consistent with this product's existing pagination pattern.
- **FR-011**: The Available Checks list MUST hide checks with no compiled/buildable logic
  ("not yet buildable"/not-compiled) by default.
- **FR-012**: The Available Checks list MUST offer a checkbox control (alongside the
  existing Search/Severity/Kind/AOR filters) that, when checked, reveals the not-yet-
  buildable checks in the list, and hides them again when unchecked.
- **FR-013**: The not-built visibility toggle (FR-012) MUST combine correctly with the
  existing Search/Severity/Kind/AOR filters (a hidden not-built check that also fails an
  active filter stays hidden; a shown not-built check that matches all active filters
  appears).
- **FR-014**: The FHA, VA, and USDA routes MUST show the same 16-block structure
  Conventional has, with each block's check count and each route's total check count shown
  as 0 (no checks), removing the current fixed, simulated non-zero placeholder value shared
  across all three.
- **FR-015**: Real, non-zero, compiled checks MUST only ever be shown under the Conventional
  route and its blocks — the gold ruleset covers Conventional (Fannie Mae Selling Guide)
  only, so FHA/VA/USDA MUST NOT display any fabricated check content, past or future.
- **FR-016**: All block/check activation, deactivation, and check-edit actions in this
  feature MUST modify route/block authoring state only — they MUST NOT alter or interact
  with a loan's live QC-audit result (the separate LoanQueue/LoanDetail/ApplyView/
  InspectSources flow).

### Key Entities

- **Route**: A named program path (e.g. Conventional, FHA, VA, USDA) with a title,
  description, and a set of blocks each marked active or inactive for that route; the
  active set determines the route's live DAG and its compiled check total.
- **Block**: A named category of related checks (e.g. "Property - Appraisal"); belongs to
  one or more routes, and within a given route is either active (contributing its checks)
  or available-but-inactive.
- **Check**: A single compiled (or not-yet-compiled/"not built") rule-catalog assertion
  within a block; has a severity, kind, area-of-responsibility, and (if compiled) an
  editable definition (catalog field, operator, threshold, pass/fail messages, source
  citation).
- **DAG node**: The diagram's visual representation of one active block on a route;
  exists only while that block is active, in the order the route's active blocks run.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A rule author can go from "route with block X inactive" to "route with block
  X active and visibly represented as a new node in the DAG" in a single click plus modal
  confirmation, with the diagram update visible within the same interaction (no reload).
- **SC-002**: On any block or route whose available list exceeds 25 items, no more than 25
  items are shown on any one page, and the current page's position is always stated (e.g.
  "Page 2 of 9").
- **SC-003**: With the not-built toggle in its default (off) state, 100% of checks shown in
  an Available Checks list are ones with real, compiled logic — zero not-yet-buildable
  checks visible until the author explicitly opts in.
- **SC-004**: FHA, VA, and USDA each show the same 16 blocks as Conventional with a check
  count of 0 (not a fabricated non-zero placeholder), and this holds on every page load —
  zero instances of a non-zero check appearing under any of the three programs.
- **SC-005**: Every block-edit and check-edit interaction opens as a modal with a visibly
  dimmed page background, and closing it without confirming discards the edit 100% of the
  time (verified by attempting a discard-and-recheck on at least one block edit and one
  check edit).

## Assumptions

- The route/block/check activation state introduced here lives in the same session-scoped
  authoring store (`rulesetStore.ts`) that already backs this page's existing "Restore to
  Gold" reset — it is not expected to persist across a browser session unless that existing
  store's own persistence behavior says otherwise (this spec does not change that
  behavior).
- "Not yet buildable" / "not built" refers to the existing NOT_COMPILED check-compile-state
  concept already established elsewhere in this product (spec019's compile-state
  discipline) — this feature does not introduce a new state, only a new visibility control
  over the existing one.
- The live DAG is read-only in the sense that a rule author cannot rearrange, rename, or
  directly edit nodes from within the diagram itself — all editing happens through the
  existing Available/Active list boxes and their modals; the diagram is a visualization of
  that state, not a second editing surface.
- FHA/VA/USDA's check counts (User Story 5) are corrected to 0, not derived from the AMQ
  workbook. Confirmed with Gordon (2026-08-02, `g-os-contrarian` check) that the gold
  ruleset is compiled from the Fannie Mae Selling Guide and covers Conventional only; FHA,
  VA, and USDA have no compiled checks today. Those three routes keep the same 16 blocks as
  Conventional (structural parity), but with 0 checks each — an honest empty state rather
  than the AMQ-workbook-derived "real" count originally requested, since no per-program AMQ
  data is compiled into anything this demo runs checks against. The demo's real, compiled
  checks are shown under Conventional only.
- This feature continues on the existing `feature/live-demo-engine-wiring` branch and PR
  (#9) rather than opening a new branch/PR, consistent with how the last several rounds of
  work on this demo have been delivered.
