# Tasks: Route/Block DAG Visualization & Authoring Editor

**Input**: Design documents from `specs/024-route-dag-editor/`
**Prerequisites**: plan.md, spec.md

**Tests**: Vitest coverage is included per user story (existing project convention — every
component in `frontend/src/components/__tests__/` has a matching test file).

**Organization**: Tasks are grouped by user story (US1-US5 from spec.md) in priority order.
US1/US2/US4 all touch `RouteDetail.tsx`; US3/US4 both touch `BlockDetail.tsx` — those tasks are
marked non-parallel (no `[P]`) and sequenced within each file's story group accordingly.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task serves

## Phase 1: Setup — shared modal component

**Purpose**: US1 and US3 both need a modal to render inside; build it once, first, so neither
story blocks on the other.

- [x] T001 Create `frontend/src/components/Modal.tsx` — extract the scrim+centered-panel markup
  already duplicated in `ExceptionReview.tsx:192-217` / `RetrievedDocumentViewer.tsx:43` into a
  shared `{ open, onClose, title?, children }` component; Escape key and outside-click (scrim
  click) both call `onClose`, inner panel click `stopPropagation`s
- [x] T002 [P] Create `frontend/src/components/__tests__/Modal.test.tsx` — covers: renders
  children when `open`, calls `onClose` on scrim click, calls `onClose` on Escape, does not call
  `onClose` on inner-panel click

**Checkpoint**: Modal is ready; US1 and US3 can each build on it independently.

---

## Phase 2: User Story 1 - Add or remove a block from a route (Priority: P1)

**Goal**: Block activation/deactivation on a route opens as a modal instead of the current
one-click list-row button, with an explicit confirm action.

**Independent Test**: From the Available Blocks list, open a block, confirm activation in the
modal, see it move to Active Blocks; from Active Blocks, open a block, confirm deactivation, see
it move back — with a dismiss-without-confirm path that changes nothing.

- [x] T003 [US1] Create `frontend/src/components/BlockMembershipModal.tsx` — renders inside
  `<Modal>` (T001); shows the block's name/description and an Activate/Deactivate confirm button
  wired to the existing `onToggleBlock(blockId)` callback `RouteDetail.tsx` already receives from
  `RoutesFlow.tsx`'s `toggleBlockActive` (no new activation logic — this wraps the existing one)
- [x] T004 [US1] Modify `frontend/src/components/RouteDetail.tsx` — Available Blocks and Active
  Blocks row clicks open `<BlockMembershipModal>` (via new local `selectedBlockId` state) instead
  of the current direct `ArrowRightCircle`/`ArrowLeftCircle` one-click toggle; confirming inside
  the modal calls `onToggleBlock` and closes the modal; dismissing does not call it (FR-009)
- [x] T005 [P] [US1] Create `frontend/src/components/__tests__/BlockMembershipModal.test.tsx` —
  covers: renders block name, Activate/Deactivate label reflects current membership, confirm calls
  `onToggleBlock` once, dismiss calls it zero times
- [x] T006 [US1] Update `frontend/src/components/__tests__/RouteDetail.test.tsx` — covers: row
  click opens modal (not immediate toggle), confirm moves block between lists, Escape/outside-
  click dismiss leaves block membership unchanged (depends on T004)

**Checkpoint**: US1 is independently functional and testable here — block add/remove works via
modal, in isolation from US2-US5.

---

## Phase 3: User Story 2 - See the route's active blocks as a live diagram (Priority: P2)

**Goal**: A live DAG of the route's currently-active blocks, positioned between the route
title/description and the two list boxes, updating with no reload as blocks are added/removed.

**Independent Test**: Activate a block (via US1's modal) and confirm its node appears in the DAG
immediately; deactivate one and confirm its node disappears immediately — no reload.

- [x] T007 [US2] Create `frontend/src/components/RouteDagView.tsx` — mirrors
  `QcAuditProcessFlow.tsx`'s existing flexbox-row + `ArrowRight`-connector pattern; props
  `{ route: Route, blocks: Block[] }`; derives its node list via
  `route.blockIds.map(id => blocks.find(b => b.id === id)).filter(Boolean)` — a pure function of
  already-owned state (FR-006: connected, directed sequence, not an unordered set)
- [x] T008 [P] [US2] Create `frontend/src/components/__tests__/RouteDagView.test.tsx` — covers:
  renders one node per active block in `route.blockIds` order, renders zero nodes gracefully for
  an empty active set (Edge Case), re-renders new/removed nodes when `route.blockIds` changes
- [x] T009 [US2] Modify `frontend/src/components/RouteDetail.tsx` — render `<RouteDagView
  route={route} blocks={blocks} />` between the title/description block and the two list boxes
  (depends on T004; same file, sequenced after US1's edit)
- [x] T010 [US2] Update `frontend/src/components/__tests__/RouteDetail.test.tsx` — covers: DAG
  gains a node immediately after a US1 modal-confirmed activation, loses a node immediately after
  a deactivation, empty-active-set route renders the DAG without error (depends on T009)

**Checkpoint**: US1 and US2 together are independently functional — activate/deactivate a block
via modal, watch the DAG update live, with no dependency on US3/US4/US5.

---

## Phase 4: User Story 3 - Add or remove a check from a block (Priority: P3)

**Goal**: The existing inline "Edit Check" panel becomes a modal (matching US1's pattern);
dismissing without an explicit save discards in-progress edits.

**Independent Test**: Open a check from Available/Active Checks, confirm the editor renders in a
modal with a dimmed background, edit a field, dismiss without saving, reopen and confirm the
field reverted; edit again and save, confirm the change persisted.

- [x] T011 [US3] Modify `frontend/src/components/BlockDetail.tsx` — relocate the inline
  `CheckEditor` render (currently lines 242-248, page-bottom) into `<Modal open={selectedCheckId
  != null} onClose={...}>`; on modal open, snapshot the selected check's editable field values
  into new local state; on close-without-explicit-save, restore the snapshot via `onUpdateCheck`
  before clearing `selectedCheckId` (FR-009 — `CheckEditor`'s existing auto-commit-on-change
  behavior is preserved, this only adds the discard-on-dismiss wrapper)
- [x] T012 [US3] Modify `frontend/src/components/BlockDetail.tsx` — add an explicit Save/Done
  button inside the modal (distinct from dismiss) that clears the snapshot without restoring it,
  so an explicit save always keeps the in-progress edits (depends on T011, same file)
- [x] T013 [P] [US3] Update `frontend/src/components/__tests__/BlockDetail.test.tsx` — covers:
  selecting a check opens the modal, editing a field then dismissing (Escape/outside-click)
  reverts it, editing then clicking Save/Done keeps it (depends on T012)

**Checkpoint**: US1, US2, US3 together are independently functional.

---

## Phase 5: User Story 4 - Find the checks/blocks that matter without an overwhelming list
(Priority: P4)

**Goal**: Pagination (25/page) on the four Available/Active lists across both pages, plus a
default-hidden "not built" toggle on BlockDetail's Available Checks list.

**Independent Test**: On a list with >25 items, confirm only 25 show per page with working
Previous/Next and a correct "Showing X-Y of Z"/"Page N of M" readout; on BlockDetail, confirm
NOT_COMPILED checks are hidden by default and the toggle correctly shows/hides them, combined
correctly with the existing Search/Severity/Kind/AOR filters.

- [x] T014 [P] [US4] Modify `frontend/src/components/RouteDetail.tsx` — add `PAGE_SIZE = 25` and
  the pagination shape already used in `LoanQueue.tsx`/`ApplyView.tsx` (`totalPages`,
  `currentPage`, `.slice()`, Previous/Next, "Showing X-Y of Z", "Page N of M") to both the
  Available Blocks and Active Blocks lists independently (separate page state per list); page
  resets to 0 when the underlying list changes (depends on T009, same file)
- [x] T015 [US4] Modify `frontend/src/components/CheckFilterBar.tsx` — add a "Show not built"
  checkbox to the existing Search/Severity/Kind/AOR filter bar, wired into `CheckFilterState`
  (default `false`)
- [x] T016 [US4] Modify `frontend/src/components/BlockDetail.tsx` — Available Checks list filters
  out `compileState === "NOT_COMPILED"` checks unless the new toggle (T015) is on; combine
  correctly with existing `filterChecks()` (a not-built check that also fails an active
  Search/Severity/Kind/AOR filter stays hidden either way) (depends on T012, T015)
- [x] T017 [US4] Modify `frontend/src/components/BlockDetail.tsx` — add the same `PAGE_SIZE = 25`
  pagination shape (T014) to both the Available Checks and Active Checks lists (depends on T016,
  same file)
- [x] T018 [P] [US4] Update `frontend/src/components/__tests__/RouteDetail.test.tsx` — covers:
  >25-item list shows exactly 25 per page, Previous/Next bounds-check, page resets on filter
  change; <25-item list renders no pagination controls (Edge Case) (depends on T014)
- [x] T019 [P] [US4] Update `frontend/src/components/__tests__/BlockDetail.test.tsx` — covers:
  NOT_COMPILED checks hidden by default, toggle reveals/hides them, toggle + existing filters
  combine correctly (Edge Case), pagination shape matches T018's (depends on T017)

**Checkpoint**: US1-US4 together are independently functional and testable.

---

## Phase 6: User Story 5 - See an honest, non-fabricated check count on FHA/VA/USDA routes
(Priority: P5)

**Goal**: FHA/VA/USDA show the same 16-block structure as Conventional with 0 checks each,
replacing the current fabricated non-zero simulated placeholder.

**Independent Test**: Open the FHA (or VA, or USDA) route; confirm the same 16 blocks as
Conventional are listed, each showing 0 checks, and the route's total check count reads 0.

- [x] T020 [US5] Modify `frontend/scripts/build_gold_catalog.py` — remove the three
  `build_simulated_program_blocks("fha"|"va"|"usda", ...)` call sites (~lines 260-262) and the
  function itself if now unused; FHA/VA/USDA routes' blocks get the same names/descriptions as
  Conventional's 16 blocks but `checkIds: []`; update the route `description` text (~lines
  275-295) to remove the "check counts are simulated" language
- [x] T021 [US5] Modify `frontend/src/components/BlockDetail.tsx` — confirm/correct the
  `isGovernmentBlock`/`gov-`-prefix empty-available-list check (line 55-58) so it also recognizes
  `fha-`/`va-`/`usda-`-prefixed blocks as always-empty (or, simpler: since T020 already gives
  those blocks `checkIds: []`, verify the existing `checks.filter(...)` logic naturally renders an
  empty list without needing a prefix-based special case at all — resolve at implementation time,
  whichever requires the smaller diff)
- [x] T022 [US5] Run `python3 frontend/scripts/build_gold_catalog.py` to regenerate
  `frontend/src/data/goldCatalog.json`; verify the output log confirms 0 simulated checks for
  fha/va/usda (depends on T020)
- [x] T023 [P] [US5] Update or add a test confirming FHA/VA/USDA routes render 16 blocks with 0
  checks each, e.g. in `frontend/src/components/__tests__/RouteDetail.test.tsx` or a new
  `goldCatalog.test.ts` asserting on the regenerated JSON directly (depends on T022)

**Checkpoint**: All 5 user stories are independently functional and testable.

---

## Phase 7: Polish & cross-cutting

**Purpose**: Final verification across the whole feature.

- [x] T024 Run `npx tsc -b` from `frontend/` — must be clean
- [x] T025 Run `npx vitest run` from `frontend/` — all tests (new and pre-existing) must pass
- [x] T026 Run `npm run build` from `frontend/` — must be clean
- [x] T027 Manual verification pass (chrome-devtools MCP screenshot review if the shared browser
  profile is free this session, otherwise a description of what to visually check): DAG updates
  live on block add/remove, both modals dim the background and discard on dismiss, pagination
  controls appear/behave correctly on both pages, not-built toggle default-hidden state, FHA/VA/
  USDA routes show 0 checks

## Dependencies & Execution Order

- Phase 1 (Modal) blocks Phase 2 (US1) and Phase 4 (US3) — both render inside `<Modal>`.
- Phase 2 (US1) blocks Phase 3 (US2) — same file (`RouteDetail.tsx`), US2's DAG placement edit
  lands after US1's modal-conversion edit.
- Phase 3 (US2) blocks Phase 5's `RouteDetail.tsx` pagination tasks (T014, T018) — same file.
- Phase 4 (US3) blocks Phase 5's `BlockDetail.tsx` tasks (T016, T017, T019) — same file.
- Phase 6 (US5) has no file overlap with Phases 2-5 (`build_gold_catalog.py` +
  `BlockDetail.tsx`'s empty-list path, which US3/US4 don't touch) — could run in parallel with
  Phases 2-5 if desired, sequenced last here only for a clean linear checkpoint story.
- Phase 7 always runs last.

## Implementation Strategy

**MVP first**: Phase 1 + Phase 2 (US1) alone already ships a real, independently valuable
capability — block activation as a confirm-modal instead of an accidental one-click toggle.
Phase 3 (US2, the DAG) is the visually compelling addition most of the original request centers
on. Phases 4-6 are independently deliverable polish/honesty passes that can land in any order
after their file-dependency prerequisites.

---

## Phase 8: User Story 6 - Keep the route page focused on the DAG, edit block membership on
demand (Priority: P6)

**Goal**: Route page loads DAG-only; the two list boxes move into a popup modal opened via a
new Edit control in the DAG's top-right corner.

**Independent Test**: Load a route page, confirm only the DAG renders; click Edit, confirm both
list boxes appear in a modal with the page dimmed; dismiss, confirm DAG-only again.

- [x] T028 [US6] Modify `frontend/src/components/RouteDagView.tsx` — add an `onEdit` prop and
  render a small Edit button/icon in the top-right corner of the DAG panel header
- [x] T029 [US6] Modify `frontend/src/components/RouteDetail.tsx` — add `editModalOpen` state
  (default `false`); move the entire Available/Active Blocks two-column grid (including its
  pagination) inside `<Modal open={editModalOpen} onClose={...} title="Edit Blocks">`; wire
  `<RouteDagView onEdit={() => setEditModalOpen(true)} .../>`
- [x] T030 [P] [US6] Update `frontend/src/components/__tests__/RouteDetail.test.tsx` — covers:
  list boxes absent on initial render, Edit button opens the modal revealing both list boxes,
  dismissing the modal hides them again, existing block-membership-modal flow (nested inside)
  still works unchanged
- [x] T031 [P] [US6] Update `frontend/src/components/__tests__/RouteDagView.test.tsx` — covers:
  Edit button renders and calls `onEdit` when clicked

**Checkpoint**: All 6 user stories are independently functional and testable.
