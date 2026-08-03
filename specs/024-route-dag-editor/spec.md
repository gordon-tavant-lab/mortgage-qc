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

### User Story 6 - Keep the route page focused on the DAG, edit block membership on demand (Priority: P6)

A rule author or someone demonstrating this product wants the route page to open with
just the DAG visible -- the Available/Active Blocks list boxes are an editing surface, not
something that needs to compete with the diagram for the page's default attention. When
they do want to edit block membership, an explicit Edit action reveals those list boxes in
a popup modal; the existing per-block membership modal (User Story 1) continues to work
unchanged from inside it.

**Why this priority**: A UI-focus refinement built on top of User Stories 1/2 (both must
already exist) -- it changes when/where the existing editing surface is shown, not any
underlying capability.

**Independent Test**: Open a route page and confirm only the DAG is visible (no list boxes
below it); click the Edit control in the DAG's top-right corner and confirm both list boxes
appear in a modal with the page dimmed; dismiss it and confirm the page returns to
DAG-only.

**Acceptance Scenarios**:

1. **Given** a route page loads, **When** the rule author views it, **Then** only the DAG
   is shown -- the Available Blocks and Active Blocks list boxes are not visible until
   explicitly requested.
2. **Given** the DAG is shown, **When** the rule author looks at its top-right corner,
   **Then** an Edit control is present.
3. **Given** the rule author clicks Edit, **When** the modal opens, **Then** both the
   Available Blocks and Active Blocks list boxes appear inside it, with the page behind
   visibly dimmed, and all existing list behavior (pagination, the block-membership modal,
   live DAG updates) continues to work unchanged.
4. **Given** the edit modal is open and the rule author dismisses it, **When** they look at
   the page, **Then** it returns to showing only the DAG (list boxes hidden again).

---

### User Story 7 - Create or permanently remove a block in the catalog (Priority: P7)

A rule author working from the Available Blocks list (inside the Edit Blocks modal, User
Story 6) wants to do more than toggle an existing block's route membership -- they want to
add a brand-new block to the catalog (so it becomes available to activate here and on other
routes that share its program), or permanently remove a block that's sitting unused in
Available and isn't needed at all. This is catalog-level authoring (creating/deleting the
blocks themselves), distinct from User Story 1's route-membership toggle (activating/
deactivating an existing block on one route).

**Why this priority**: Builds on User Story 1/6's editing surface but is a materially bigger
capability (mutating the catalog itself, not just membership) -- sequenced after the
membership/DAG/pagination work is solid.

**Independent Test**: From the Edit Blocks modal, use a "new block" control to create a block
with a name/description; confirm it appears in Available Blocks with 0 checks and can then be
activated via the existing per-block modal (US1). Separately, find a block sitting in
Available, remove it, confirm it disappears from Available (here, and from any other route
that shared it), and does not reappear after a page reload.

**Acceptance Scenarios**:

1. **Given** the Edit Blocks modal, **When** the rule author uses the "add new block" control
   and supplies a name and description, **Then** a new block is created with zero checks and
   appears in the Available Blocks list, not active on this route.
2. **Given** a block sitting in Available Blocks, **When** the rule author uses its remove
   control, **Then** the block is permanently deleted from the catalog and no longer appears
   in Available Blocks.
3. **Given** a block that is currently Active on this route, **When** the rule author looks at
   its row, **Then** no remove control is offered there -- removal is only ever available on
   rows in the Available Blocks list; an author must deactivate a block before it can be
   removed.
4. **Given** a block available on this route but still Active on a different, shared-pool
   route (the existing custom-route shared-pool behavior this codebase already has), **When**
   the rule author tries to remove it, **Then** the system does not silently delete a block
   that's still wired somewhere else (exact block-vs-warn UX is an open planning question --
   see Assumptions).

---

### User Story 8 - Create or permanently remove a check in a block's catalog (Priority: P8)

A rule author working from a block's Available Checks list wants to add a brand-new check to
that block's catalog (defining its catalog field, operator, threshold, severity, messages,
and citation via the same check-editor modal already built for editing existing checks), or
permanently remove a check sitting unused in Available. Parallel capability to User Story 7,
one level down (check-within-block instead of block-within-route).

**Why this priority**: Parallel to User Story 7, sequenced last since it depends on the same
catalog-mutation pattern being proven at the block level first.

**Independent Test**: From a block's Available Checks list, use a "new check" control, fill
out the check editor, confirm the new check appears in Available Checks (not yet active) and
is honestly marked not-yet-buildable rather than presented as a real compiled check.
Separately, remove a check sitting in Available, confirm it's gone from that block's Available
Checks after a page reload.

**Acceptance Scenarios**:

1. **Given** a block's Available Checks list, **When** the rule author uses the "add new
   check" control and fills in the check's catalog field/operator/threshold/severity/
   messages/citation via the existing check-editor modal, **Then** a new check is created for
   this block and appears in Available Checks, not yet active.
2. **Given** a newly-created check (Scenario 1), **When** it is shown anywhere in this
   product, **Then** it is honestly labeled as authored-not-compiled (the existing
   NOT_COMPILED / "not yet buildable" convention) -- it MUST NOT be presented as a real,
   gold-compiled check just because a rule author typed values into its fields.
3. **Given** a check sitting in Available Checks, **When** the rule author uses its remove
   control, **Then** the check is permanently deleted from that block's catalog and no longer
   appears in Available Checks.
4. **Given** a check that is currently Active within its block, **When** the rule author looks
   at its row, **Then** no remove control is offered there -- removal is only ever available
   on rows in the Available Checks list; an author must deactivate a check before it can be
   removed.

---

### User Story 9 - Open a block's checks directly from Available Blocks (Priority: P9)

A rule author browsing Available Blocks (inside the Edit Blocks modal, User Story 6) wants to
inspect or edit a block's checks -- via BlockDetail's Available/Active Checks lists -- without
first having to activate that block on this route. Today only Active Blocks rows navigate to
BlockDetail; an Available Blocks row offers only Activate and Remove (User Stories 1/7), with
no way to see what's actually inside the block before deciding to wire it in.

**Why this priority**: A pure navigation/discoverability gap, sequenced last since it depends
on Available Blocks already having real content worth inspecting (User Story 7's create flow,
in particular, makes this materially more useful -- a newly-created block is empty until its
checks are reviewed or added).

**Independent Test**: Open the Edit Blocks modal, click an Available Blocks row (its name/
description area, not the Activate or Remove icons), confirm it navigates to that block's
BlockDetail page exactly like clicking an Active Blocks row does today; confirm Activate and
Remove still work as separate, explicit controls and are not accidentally triggered by that
navigation click.

**Acceptance Scenarios**:

1. **Given** the Edit Blocks modal, **When** the rule author clicks an Available Blocks row's
   name/description area, **Then** the page navigates to that block's BlockDetail page.
2. **Given** a rule author reached BlockDetail from an Available (not-yet-active) block,
   **When** they view it, **Then** Available/Active Checks and all existing check-editing
   capabilities (User Stories 3, 4, 8) work exactly as they do for a block reached from Active
   Blocks -- checks can be reviewed, added, edited, activated, or removed regardless of whether
   the block itself is active on this route.
3. **Given** the rule author navigates back from that BlockDetail page, **When** they land
   back, **Then** they return to the route's page, matching the existing "back to route"
   behavior for Active-Blocks-originated navigation.
4. **Given** an Available Blocks row, **When** the rule author clicks its Activate or Remove
   icon specifically, **Then** only that action fires -- clicking to view a block's checks
   must never accidentally activate or delete it, and vice versa.

---

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
- What happens if the gold ruleset is later regenerated/recompiled (e.g. new Conventional
  checks compiled in)? FHA/VA/USDA must keep showing 0 checks regardless — their honest
  zero is a fact about program coverage (gold covers Conventional only), not a count that
  could ever legitimately change until real FHA/VA/USDA rules are compiled into the gold
  ruleset itself (out of scope for this feature).
- What happens when removing the last item from Available Blocks/Available Checks leaves that
  list empty? This is already a normal, handled state elsewhere in this spec (e.g. a block
  with "0 compilable / 0 total" available checks) -- removal reaching zero must render the
  same way, not as an error.
- What happens to a route's live DAG or active-check totals when a block/check that is NOT
  active is removed? Nothing -- removal is restricted to Available (inactive) items only, so
  no active route/block total or DAG node is ever affected by a removal.
- Can a rule author create two blocks (or two checks within a block) with the same name? Not
  resolved here -- an open question for `/speckit-plan` (duplicate-name handling), not assumed
  silently.
- Is a deleted custom block/check recoverable? No -- see Assumptions: newly-created entities
  are not part of the gold snapshot, so "Restore to Gold" cannot bring one back once removed.
- What happens when a rule author clicks an Available Blocks row's name/description text versus
  its Activate or Remove icons? Only the name/description area navigates to BlockDetail;
  Activate and Remove remain separate, explicit icon-only controls -- viewing a block's checks
  must never double as activating or deleting it.

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
- **FR-017**: The route page MUST NOT show the Available Blocks / Active Blocks list boxes
  by default -- only the DAG is shown on initial page load.
- **FR-018**: The DAG MUST show an Edit control in its top-right corner.
- **FR-019**: Clicking the Edit control MUST open a popup modal (page content behind it
  visibly dimmed) containing the Available Blocks and Active Blocks list boxes, with all
  existing editing behavior (pagination, the block-membership modal, live DAG updates)
  unchanged within it.
- **FR-020**: The Available Blocks list MUST offer a control to create a new block (name and
  description at minimum), which appears in Available Blocks with zero checks and is not
  automatically active on any route.
- **FR-021**: The Available Blocks list MUST offer a per-row control to permanently delete
  that block from the catalog; the Active Blocks list MUST NOT offer any delete control
  (only deactivate, per FR-001).
- **FR-022**: The Available Checks list (within a block) MUST offer a control to create a new
  check via the existing check-editor modal (catalog field, operator, threshold, severity,
  pass/fail messages, source citation), which appears in Available Checks and is not
  automatically active.
- **FR-023**: A newly-created check MUST be honestly labeled as not-yet-compiled/"not yet
  buildable" (the existing NOT_COMPILED convention, FR-011) -- it MUST NOT display as if it
  were a real, gold-compiled check.
- **FR-024**: The Available Checks list MUST offer a per-row control to permanently delete
  that check from its block's catalog; the Active Checks list MUST NOT offer any delete
  control (only deactivate, per FR-007).
- **FR-025**: Removing a block or check MUST only be possible while it is in the Available
  (inactive) list; there MUST be no way to remove a block/check that is currently Active
  anywhere it's wired.
- **FR-026**: An Available Blocks row MUST support navigating to that block's BlockDetail page
  (its name/description area), the same way an Active Blocks row already does -- without
  requiring the block to be activated on the route first, and without that navigation click
  triggering Activate or Remove.

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
- **SC-006**: From a fresh route page load, the Available/Active Blocks list boxes are not
  present until the Edit control is clicked; after clicking, both appear in a modal; after
  dismissing, they are hidden again -- 100% of the time, on every route.
- **SC-007**: A rule author can create a new block from Available Blocks and see it appear
  there (0 checks, not active) within the same interaction, with no reload.
- **SC-008**: A rule author can create a new check from a block's Available Checks and see it
  appear there, honestly marked not-yet-buildable, within the same interaction, with no
  reload.
- **SC-009**: 100% of remove/delete controls in this feature appear only on Available-list
  rows; zero appear on any Active-list row, for both blocks and checks.
- **SC-010**: From the Edit Blocks modal, clicking any Available Blocks row (outside its
  Activate/Remove icons) navigates to that block's BlockDetail page 100% of the time, whether
  or not the block is active on this route.

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
- User Story 6's Edit modal nests the existing per-block membership modal (User Story 1)
  inside it when a block row is clicked -- two stacked modals is an acceptable pattern for
  this authoring-only surface (confirmed 2026-08-03, following Gordon's follow-up request);
  dismissing the inner modal returns to the outer list-boxes modal, not all the way back to
  the DAG-only view.
- A newly-created block/check (User Stories 7/8) is rule-author-authored data, not a compiled
  gold-ruleset entry -- it starts, and stays, NOT_COMPILED/not-yet-buildable until a real
  compile pipeline (out of scope for this feature) produces it. This feature does not
  fabricate compiled status for anything a human types in (Constitution Principle VII).
- Removing a block/check that is Available on this route but still Active on a different
  route sharing the same block/check pool (the existing shared-pool behavior for custom
  SME-created routes, per `RouteDetail.tsx`'s `ROUTE_BLOCK_PREFIX` comment) is left as an open
  question for `/speckit-plan`: block the removal with a warning, or allow it and let the
  other route silently lose that block/check? Not assumed silently either way.
- Newly-created blocks/checks are not part of the gold-sourced snapshot, so the existing
  "Restore to Gold" control cannot recover one that's been deleted -- deletion here is
  permanent within the session (no undo), which should be made clear in the UI copy at
  implementation time.
- The "add new block"/"add new check" creation UI should reuse the existing "New Route"
  creation pattern already established on the Routes list page (`RoutesFlow.tsx`), consistent
  with this spec's existing constraint to reuse established UI patterns rather than inventing
  new ones.
- User Story 9's navigation reuses the existing `onOpenBlock` callback already wired to Active
  Blocks rows (`RouteDetail.tsx`) -- it is the same navigation, offered from a second entry
  point (Available Blocks), not a new navigation mechanism.

## Related Documentation

- `output/LIVE-DEMO-ENGINE-WIRING-LOG-2026-08-02.md` -- the running session log for the
  `feature/live-demo-engine-wiring` branch (PR #9). Items 16-18 document this spec's full
  lifecycle: the original 7-item request, the User Story 5 contrarian correction (FHA/VA/USDA
  are 0 checks, not AMQ-derived, per the Assumptions entry above), the fan-out/fan-in DAG
  rework, and User Story 6's DAG-only + Edit-modal change -- including verification steps
  (test counts, live-browser checks) not restated in this spec.
