# Implementation Plan: Route/Block DAG Visualization & Authoring Editor

**Branch**: `feature/live-demo-engine-wiring` (see spec.md's Assumptions — continues the existing
PR #9 branch rather than opening a new `024-*` branch) | **Date**: 2026-08-02 | **Spec**:
[spec.md](./spec.md)
**Input**: Feature specification from `specs/024-route-dag-editor/spec.md`

## Summary

Upgrade the rule-author page suite (`RouteDetail.tsx`, `BlockDetail.tsx`) with six independent
capabilities: a live-updating DAG of a route's active blocks, a reusable modal component that
replaces the inline check editor and gains a new block-membership editor, pagination on four
existing lists, a default-hidden "not built" visibility toggle, a data-honesty fix that replaces
FHA/VA/USDA's fabricated non-zero check counts with a real zero, and (added 2026-08-03, User
Story 6) a UI-focus refinement that hides the Available/Active Blocks list boxes behind an Edit
control on the DAG, so the route page opens DAG-only. No new backend, no new data store, no new
external interface — every capability extends state and patterns that already exist in
`RoutesFlow.tsx` (the owner of `routes`/`blocks`/`checks` state) and its two child pages. The only
non-UI change is a one-time re-run of `frontend/scripts/build_gold_catalog.py` after removing its
FHA/VA/USDA simulation logic.

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
No new routes, no new pages.

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
| VII. Configuration is authored data | Yes | Directly served by User Story 5: removes `build_gold_catalog.py`'s fabricated FHA/VA/USDA check counts (an explicit prior override of this principle, flagged in that script's own docstring) and restores an honest 0 — the divergence between "looks real" and "is real" is corrected, not perpetuated. |

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
│                                    #   also paginated
├── CheckFilterBar.tsx               # MODIFIED — add the "Show not built" checkbox alongside the
│                                    #   existing Search/Severity/Kind/AOR controls (US4 FR-012)
└── __tests__/
    ├── RouteDagView.test.tsx        # NEW
    ├── Modal.test.tsx               # NEW
    ├── RouteDetail.test.tsx         # MODIFIED — pagination + modal interaction coverage
    └── BlockDetail.test.tsx         # MODIFIED — pagination + not-built toggle + modal coverage

frontend/scripts/
└── build_gold_catalog.py            # MODIFIED — remove build_simulated_program_blocks() calls
                                      #   for fha/va/usda (lines ~260-262); those three routes'
                                      #   blocks get empty checkIds instead (US5, FR-014/015)

frontend/src/data/
└── goldCatalog.json                 # REGENERATED — re-run build_gold_catalog.py after the
                                      #   script edit above; committed as a data file, not source
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

## Complexity Tracking

*(Empty — Constitution Check passed with no violations to justify.)*
