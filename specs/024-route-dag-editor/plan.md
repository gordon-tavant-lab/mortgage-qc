# Implementation Plan: Route/Block DAG Visualization & Authoring Editor

**Branch**: `feature/live-demo-engine-wiring` (see spec.md's Assumptions — continues the existing
PR #9 branch rather than opening a new `024-*` branch) | **Date**: 2026-08-02 | **Spec**:
[spec.md](./spec.md)
**Input**: Feature specification from `specs/024-route-dag-editor/spec.md`

## Summary

Upgrade the rule-author page suite (`RouteDetail.tsx`, `BlockDetail.tsx`) with ten independent
capabilities: a live-updating DAG of a route's active blocks, a reusable modal component that
replaces the inline check editor and gains a new block-membership editor, pagination on four
existing lists, a default-hidden "not built" visibility toggle, a data-honesty fix that replaces
FHA/VA/USDA's fabricated non-zero check counts with a real zero, (added 2026-08-03, User Story 6)
a UI-focus refinement that hides the Available/Active Blocks list boxes behind an Edit control on
the DAG, (added 2026-08-03, User Stories 7/8) catalog-level create/remove for blocks and checks --
a brand-new block/check can be authored from the Available Blocks/Available Checks list, and one
sitting unused in Available can be permanently deleted (never an Active/wired one) -- (added
2026-08-03, User Story 9) letting an Available Blocks row navigate to that block's checks the same
way an Active Blocks row already does, without requiring activation first -- and (added
2026-08-03, User Story 10, Gordon's explicit override of US5/FR-015) real, per-program,
per-category check counts for FHA/VA/USDA, imported directly from the raw AMQ Sept 2025 workbook
(`storage/rules/gold/source/amqs-sept-2025-retail.xlsx`) instead of an honest zero -- every
imported check is real and individually inspectable but stays `NOT_COMPILED`/`NOT_ASSESSED`,
since none of them have been through this project's field-mapping/compile step. Also fixes a real
bug (FR-027) found during live use: a newly-created check is always not-yet-buildable, and the
Available Checks list hid not-yet-buildable checks by default, so a just-created check would
silently vanish -- creating a check now also reveals it. No new backend, no new external
interface — every capability extends state and patterns that already exist in `RoutesFlow.tsx`
(the owner of `routes`/`blocks`/`checks` state) and its two child pages, plus one new data-import
path in `build_gold_catalog.py` (US10) that reads the raw AMQ workbook directly for the first
time, alongside its existing already-compiled-JSON path for Conventional.

## Technical Context

**Language/Version**: TypeScript (React 18, Vite) — matches the existing `frontend/` app;
Python 3.9-compatible for the one `build_gold_catalog.py` edit (project-wide constraint).
**Primary Dependencies**: None new. Reuses `lucide-react` (already a dependency, for icons in the
DAG nodes and modal chrome) and Tailwind utility classes already used throughout `frontend/src`.
No DAG-layout library is introduced — User Story 2 requires a linear connected sequence (the
existing `QcAuditProcessFlow.tsx` pattern: flexbox row + `ArrowRight` connectors), not a
general-purpose graph layout, so a library would be scope creep, not a requirement.
**Storage**: No new storage. Route/Block/Check activation state continues to live in
`RoutesFlow.tsx`'s local `useState`, autosaved via the existing `rulesetStore.saveDraft()` /
`localStorage` (`mortgage-qc-ruleset-draft-v1`) — this feature adds no new persistence layer.
**Testing**: Vitest + React Testing Library (existing `frontend/src/**/__tests__/` convention).
**Target Platform**: Browser (Vite dev server / static build) — no server-side change.
**Project Type**: Web frontend, single project (`frontend/`); one accompanying Python data-gen
script edit + a one-time regenerated JSON artifact (`frontend/src/data/goldCatalog.json`).
**Performance Goals**: N/A — this is an authoring-time UI feature with small (dozens to low
hundreds of items) lists; no perceptible-latency requirement beyond "no reload" (FR-003, FR-005).
**Constraints**: Every block/check add-remove action must only touch `RoutesFlow.tsx`'s authoring
state, never the live QC-audit demo's `dataSourceContext.tsx`/`auditRuns` state (FR-016 — these
are two deliberately separate surfaces in this codebase, established in spec019/020). The DAG,
pagination, and toggle must all work with zero backend calls (everything is already in memory).
**Scale/Scope**: 2 pages modified (`RouteDetail.tsx`, `BlockDetail.tsx`), 1 new shared `Modal.tsx`
component (extracted from the two existing inline-duplicated modal patterns in
`ExceptionReview.tsx` / `RetrievedDocumentViewer.tsx`; gains a `widthClassName` prop for US6's
wider Edit-Blocks modal), 1 new `RouteDagView.tsx` component (gains an `onEdit` prop + top-right
Edit button for US6), 2 new modal-content components (`BlockMembershipModal.tsx`, wrapping the
existing inline `CheckEditor`), 1 script edit (`build_gold_catalog.py`) + 1 regenerated data file.
US7/US8 add no new components -- `createBlock`/`removeBlockIfUnused`/`createCheck`/
`removeCheckIfUnused` are new handlers on `RoutesFlow.tsx` (the existing state owner), wired into
inline create-form/remove-confirm UI added directly to `RouteDetail.tsx`/`BlockDetail.tsx`
(mirroring `RouteList.tsx`'s existing New Route/Remove Route pattern), plus a small fix to
`rulesetStore.ts`'s `reconcileDraft` (see Component responsibility notes) and a `CheckEditor` Name
field. No new routes, no new pages.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Applies? | Assessment |
|---|---|---|
| I. Determinism of the correct computation | No | This feature doesn't touch check evaluation logic — it's authoring-surface UI (which blocks/checks are active) and a visualization of that state, not a computation. |
| II. Compile, then run | No | No LLM involvement anywhere in this feature. |
| III. Eval is foundational | No | Not implicated — no eval/ground-truth surface is touched. |
| IV. Build the core, assume the periphery | Yes | The DAG deliberately reuses the existing linear-flow visual pattern (`QcAuditProcessFlow.tsx`) instead of adopting a graph-layout library; the modal deliberately extracts the two already-duplicated inline patterns instead of inventing new modal chrome — scope discipline over novelty. |
| V. Source independence | No | Not implicated — no LOS/MISMO/Touchless reconciliation is touched. |
| VI. Configurable by non-technical users | Yes | Directly served — this feature *is* the non-technical rule author's editing surface (block/check activation, membership). User Stories 1/3/5 exist specifically to make that surface usable and honest. |
| VII. Configuration is authored data | Yes | Served three ways, one of them a deliberate, explicit override: User Story 5 first removed `build_gold_catalog.py`'s fabricated FHA/VA/USDA check counts and restored an honest 0; User Stories 7/8 (FR-023) extend the same discipline to authoring itself; User Story 10 (2026-08-03) then explicitly *overrides* US5's display decision at Gordon's informed request (confirmed via `/grill-me`) -- FHA/VA/USDA now show real, non-fabricated AMQ-workbook counts styled like Conventional's, but the underlying honesty is preserved structurally: every imported check stays `compileState: NOT_COMPILED` / `authorability: NOT_ASSESSED`, so nothing is presented as compiled/runnable that isn't. |

**Result: PASS, no violations.** No entry needed in Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/024-route-dag-editor/
├── plan.md              # This file
├── checklists/
│   └── requirements.md  # Spec quality checklist (completed during /speckit-specify)
└── tasks.md             # Phase 2 output (/speckit-tasks — next step)
```

See also `output/LIVE-DEMO-ENGINE-WIRING-LOG-2026-08-02.md` (items 16-18) — the branch's
running session log, documenting this feature's full implementation/verification history
outside the formal spec-kit artifacts above (referenced from spec.md's Related Documentation).

No `research.md` — every technical question (DAG layout approach, modal pattern source, pagination
pattern source, FHA/VA/USDA fix location) was already resolved by direct source inspection before
this plan was written (see Technical Context above and the codebase survey it's based on). No
`data-model.md` — this feature introduces no new persisted entity; `Route`/`Block`/`Check`
(`frontend/src/lib/types.ts`) are unchanged, only their existing `blockIds`/`checkIds` membership
arrays gain new UI to edit them (Available Blocks already has live add UI per `RouteDetail.tsx`
today; this plan's data-shape delta is confined to what's listed in Key Entities below). No
`contracts/` — this is a pure frontend feature with no new external interface; nothing outside
`frontend/` calls into any of these components.

### Source Code (repository root)

```text
frontend/src/components/
├── Modal.tsx                       # NEW — shared scrim+centered-panel component, extracted
│                                    #   from ExceptionReview.tsx / RetrievedDocumentViewer.tsx's
│                                    #   duplicated inline pattern (US1 FR-002, US3 FR-008)
├── RouteDagView.tsx                # NEW — live DAG of a route's active blocks (US2, FR-004..006)
├── BlockMembershipModal.tsx         # NEW — "activate/deactivate this block on this route" modal
│                                    #   content, rendered inside <Modal> (US1, FR-001/002)
├── RouteDetail.tsx                  # MODIFIED — renders <RouteDagView> between title and the
│                                    #   two list boxes; Available/Active Block rows open
│                                    #   <BlockMembershipModal> instead of the current direct
│                                    #   ArrowRightCircle/ArrowLeftCircle one-click toggle
│                                    #   (US1 FR-002); both lists paginated 25/page (US4 FR-010)
├── BlockDetail.tsx                  # MODIFIED — inline <CheckEditor> now renders inside <Modal>
│                                    #   instead of at the page bottom (US3 FR-008); Available
│                                    #   Checks list gets the not-built toggle (US4 FR-011/012/
│                                    #   013) and pagination (US4 FR-010); Active Checks list
│                                    #   also paginated; Available Checks pool now computed for
│                                    #   every block (not Conventional-only) and scoped by each
│                                    #   check's `{program}-amq-` id prefix, not category alone
│                                    #   (US10, FR-029/030, regression fix); "show not built"
│                                    #   defaults on for non-Conventional blocks (US10 FR-011
│                                    #   tension resolution)
├── CheckFilterBar.tsx               # MODIFIED — add the "Show not built" checkbox alongside the
│                                    #   existing Search/Severity/Kind/AOR controls (US4 FR-012)
├── RoutesFlow.tsx                   # MODIFIED — new createBlock/removeBlockIfUnused/createCheck/
│                                    #   removeCheckIfUnused handlers (US7 FR-020/021, US8 FR-022/
│                                    #   024); restoreToGold also resets `nav` to the route list
│                                    #   (regression fix -- a custom route/block/check it deletes
│                                    #   could otherwise leave `nav` pointing at nothing)
└── __tests__/
    ├── RouteDagView.test.tsx        # NEW
    ├── Modal.test.tsx               # NEW
    ├── RouteDetail.test.tsx         # MODIFIED — pagination + modal interaction + US7 create/
    │                                #   remove-block + US9 navigation coverage
    └── BlockDetail.test.tsx         # MODIFIED — pagination + not-built toggle + modal + US8
                                     #   create/remove-check + Check Name rename + US10
                                     #   per-program availability/default-filter/cross-program-
                                     #   scoping regression coverage

frontend/scripts/
└── build_gold_catalog.py            # MODIFIED (US5, then US10) — first replaced
                                      #   build_simulated_program_blocks() with an honest empty
                                      #   checkIds (US5, FR-014/015); US10 replaces THAT with
                                      #   build_program_blocks_and_checks(), reading
                                      #   storage/rules/gold/source/amqs-sept-2025-retail.xlsx
                                      #   directly (Post-Closing only, "Discarded" category
                                      #   excluded, deduped by (category, Exception Code)) to
                                      #   produce real FHA/VA/USDA checks (FR-028..031)

frontend/src/data/
└── goldCatalog.json                 # REGENERATED — re-run build_gold_catalog.py after the
                                      #   script edit above; committed as a data file, not source

frontend/src/lib/
├── types.ts                         # MODIFIED — Authorability gains NOT_ASSESSED (US10,
│                                    #   FR-031): distinct from NOT_MECHANIZABLE, which implies
│                                    #   a real assessment attempt was made and failed
├── rulesetStore.ts                  # MODIFIED — reconcileDraft() no longer prunes a custom
│                                    #   (never-gold) check on reload; see Component responsibility
│                                    #   notes (US8 regression guard)
└── __tests__/
    └── rulesetStore.test.ts         # NEW — reconcileDraft: prunes a truly-missing gold check,
                                      #   keeps a custom one
```

**Structure Decision**: Single-project layout — this feature lives entirely inside the existing
`frontend/` app (Option 1, no `src/`/`tests/` top-level split, matching how every prior demo-app
feature in this repo has landed). No new top-level directory. The one non-`frontend/` touch is the
`goldCatalog.json` regeneration, which is a data artifact, not new source.

### Component responsibility notes (traced against the existing codebase, not assumed)

- **`Modal.tsx`** copies the exact markup already duplicated in `ExceptionReview.tsx:192-217` /
  `RetrievedDocumentViewer.tsx:43` (`fixed inset-0 z-50 flex items-center justify-center
  bg-slate-950/40 p-4 backdrop-blur-sm`, inner panel `stopPropagation`-guarded) — a consolidation,
  not a new visual language. Props: `open`, `onClose`, `children`, optional `title`, optional
  `widthClassName` (added for US6's wider Edit-Blocks modal; defaults to the original
  `max-w-2xl`). Escape-key and outside-click both call `onClose` (FR-009: dismiss-without-save
  discards).
- **`RouteDagView.tsx`** mirrors `QcAuditProcessFlow.tsx`'s existing flexbox-row +
  `ArrowRight`-connector pattern exactly (same component already ships in this app for the QC
  audit process flow), fed by `route.blockIds.map(id => blocks.find(b => b.id === id))` — a pure
  function of already-owned state, so FR-005's "no reload" requirement is satisfied for free (any
  React re-render from `RoutesFlow.tsx`'s existing `toggleBlockActive` state update already
  re-derives this list).
- **`BlockMembershipModal.tsx`** wraps the *existing* activate/deactivate action
  (`RoutesFlow.tsx`'s `toggleBlockActive`, already wired to `RouteDetail.tsx`'s
  `ArrowRightCircle`/`ArrowLeftCircle` buttons) — FR-001's "add/remove a block" capability already
  works today; this plan's job is only to move that action from a one-click list-row button into a
  confirm-style modal (FR-002), not to build new activation logic.
- **`CheckEditor`** (`BlockDetail.tsx:366-630`) is relocated into `<Modal>`, not rewritten — its
  auto-commit-on-change behavior is preserved; FR-009's "discard on dismiss" is satisfied by
  snapshotting the check's field values when the modal opens and restoring them on close-without-
  explicit-save (a new, small piece of local state in `BlockDetail.tsx`, since `CheckEditor` today
  has no dirty-tracking — this is the one genuinely new interaction pattern in the whole feature).
- **FHA/VA/USDA fix** deletes `build_simulated_program_blocks()`'s three call sites
  (`build_gold_catalog.py:260-262`) and the "check counts are simulated" route-description text
  (lines ~275-295), replacing them with blocks that carry the same names/descriptions as
  Conventional's 16 blocks but an empty `checkIds: []` — `BlockDetail.tsx`'s existing
  `isGovernmentBlock`/`gov-` empty-available-list path (line 55-58) already proves this exact
  zero-checks rendering works; the fix only needs `fha-`/`va-`/`usda-` prefixed blocks to hit that
  same empty-list path (or, more simply, be recognized as always-empty regardless of prefix, since
  the current `gov-`-only check is itself now stale — confirm and correct at implementation time).
- **`createBlock`/`createCheck`** (US7/US8, `RoutesFlow.tsx`) mint an id via a module-level
  counter (mirroring the existing `routeCounter` pattern for `createRoute`), stamped with the
  route's `ROUTE_BLOCK_PREFIX` (exported from `RouteDetail.tsx`) so the new block is filtered as
  relevant/available on the route it was created from; `createCheck` sets `category` to the
  block's own name so it's filtered into that block's Available Checks pool the same way. Neither
  auto-adds the new entity to any `blockIds`/`checkIds` membership array — it starts, and stays,
  unwired until explicitly activated via the existing US1/US3 modals. `createCheck` always returns
  `kind: "predicate"`, `authorability: "NEEDS_FIELDS"`, `compileState: "NOT_COMPILED"` — an honest,
  authored-not-compiled default (FR-023); other check kinds aren't authorable via this flow since
  `CheckEditor` has no kind switcher (out of scope, not silently worked around).
- **`removeBlockIfUnused`/`removeCheckIfUnused`** (US7/US8, `RoutesFlow.tsx`) resolve the spec's
  open cross-route-safety question: refuse (return `false`, delete nothing) if the entity is still
  referenced by *any* route's `blockIds` / *any* block's `checkIds` — not just the one the removal
  request came from — since a custom, unprefixed route can share the same block/check pool as
  another route. `RouteDetail.tsx`/`BlockDetail.tsx` surface the refusal as an inline message
  rather than silently no-oping.
- **`reconcileDraft` fix** (`rulesetStore.ts`, US8 regression guard): before this feature, this
  function rebuilt the saved draft's `checks` array from ONLY the ids present in the current gold
  catalog — correct when every check was gold-sourced, but it would have silently deleted (and
  misreported as "missing") any custom-authored check on the very next reload. Fixed by also
  treating any check id prefixed `custom-check-` (the convention `createCheck` uses) as known-valid,
  regardless of whether it's in the gold catalog. Covered by a new `rulesetStore.test.ts`.
- **`restoreToGold` nav-reset fix** (`RoutesFlow.tsx`, discovered during live verification, not
  spec'd in advance): resetting to gold can now delete a custom route/block the rule author is
  currently viewing (previously only possible for custom routes; US7 adds custom blocks as a second
  path to the same pre-existing gap) — with `nav` left pointing at a now-nonexistent route/block,
  no `nav.level` branch matched and the page rendered blank. Fixed by having `restoreToGold` also
  call `setNav({ level: "list" })`, returning to the route list every time, matching `backToList`'s
  existing behavior for the equivalent manual action.
- **US9 navigation** (`RouteDetail.tsx`): the Available Blocks row's name/description `<div>`
  becomes a `<button onClick={() => onOpenBlock(block.id)}>`, and a trailing `ChevronRight`
  button is added after Activate — an exact mirror of the Active Blocks row's existing
  `onOpenBlock` wiring (FR-026), not a new navigation mechanism. Activate and Remove stay
  separate icon buttons, so the navigation click never fires either action (FR-026, Edge Case).
- **FR-027 fix** (`BlockDetail.tsx`'s `handleCreateCheck`): a newly-created check is always
  `NOT_COMPILED` (FR-023), and Available Checks hides `NOT_COMPILED` checks by default (FR-011)
  — confirmed live as a real bug, the check an author just created would vanish from the list
  they were looking at. Fixed by also calling `setAvailableFilter((prev) => ({ ...prev,
  showNotBuilt: true }))` at creation time, per the Assumption already recorded in spec.md —
  reusing the existing not-built toggle rather than adding a second, parallel visibility rule.
- **`build_program_blocks_and_checks`** (US10, `build_gold_catalog.py`) replaces
  `build_empty_program_blocks`: opens the raw AMQ workbook directly (`openpyxl`, read-only),
  filters to Post-Closing rows outside the "Discarded" category, tags each row to a program by
  parsing the literal `Loans.QC_Policy = 'X'` string out of its "Question Criteria" column (a
  SQL-shaped precondition text this project only ever reads, never executes), and dedupes by
  `(category, Exception Code)` before emitting one `Check` per distinct exception. Every
  imported check id is stamped `"{program}-amq-{slug}"` -- the load-bearing convention the
  frontend fix below depends on.
- **`BlockDetail.tsx`'s Available Checks scoping fix** (US10, found live during verification):
  removing the old `isRealCoverageBlock` (Conventional-only) gate on the availability
  computation was necessary once FHA/VA/USDA carried real checks, but doing so naively (category
  match only) let an FHA block's pool pull in Conventional's real compiled checks sharing the
  same category text, and vice versa -- a real regression, not a hypothetical one, caught by
  opening a live FHA block and seeing `O-FNM-*` (Conventional) checks in its Available list.
  Fixed with `PROGRAM_CHECK_ID_PREFIXES`: a program block's pool is filtered to its own
  `{program}-amq-` prefix; Conventional's pool excludes all three program prefixes. `isConventionalBlock` (renamed from `isRealCoverageBlock`) is kept as a narrower flag gating
  only check *creation* (US8's "New Check" stays Conventional-only, a deliberate scope choice,
  not one US10 forces).
- **Default "show not built"** (US10, `BlockDetail.tsx`): `defaultAvailableFilter()` returns
  `showNotBuilt: true` when `!isConventionalBlock`, applied both on initial mount and on the
  existing block-navigation reset `useEffect` -- Conventional keeps FR-011's original
  default-hide behavior (most of its checks ARE compiled; the exception is worth hiding).

## Complexity Tracking

*(Empty — Constitution Check passed with no violations to justify.)*
