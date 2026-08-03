# Tasks: 019-workbook-first-rule-authoring (reworked 2026-08-01)

**Input**: `spec.md`, `plan.md` (same directory)
**Prerequisites**: plan.md (required)

**Note on this rework**: the original Phase 1/5 tasks (workbook re-ingestion, custom SHACL compiler)
are retired — see `spec.md`'s "2026-08-01 Rework" section and decision
[032](../../src/decisions/032-spec019-rework-onto-gold-ruleset.md). This file reflects the reworked
phase plan in `plan.md`, tracking what's actually been built.

## Phase 0: Restore the audit baseline (done, historical)

- [x] T001 Regenerate `src/shacl_pilot/out/loan_{01..05}.json`/`.ttl` via `extract_loan.py` →
      `loan_to_rdf.py`, run `run_full_ruleset_audit.py` against each, twice (determinism)
      → Done: `specs/019-workbook-first-rule-authoring/BASELINE.md` records 4/20,830 rule-loan pairs
      reaching a verdict, byte-identical across both runs
- [x] T002 Record the finding as decision 031 (`src/decisions/031-demo-target-is-touchless-not-synthetic-loans.md`)
      and flag `BASELINE.md` as superseded-target, not a regression floor

---

## Phase 1: Gold-to-Check mapper (done)

- [x] T003 Create `frontend/scripts/build_gold_catalog.py` reading
      `storage/rules/gold/data/{rules_compiled.json,rules_atomic.json}` directly
      → Done: no dependency on `p0/qc_engine`, `src/shacl_pilot`, or the other in-progress worktree
- [x] T004 Map `check_type`→`kind`, `applicability`→`appliesIf`, `citations`→`grounding`,
      `category`→`Block`; link decomposed atomic rules to their parent card via
      `provenance.parent_card_id` (verified 1:1 against all 46 decomposed cards — NOT via
      `defect_options[].atomic_rule_ids`, which is never populated)
- [x] T005 Derive `authorability`/`authorabilityReason`/`compileState` conservatively — `COMPILABLE`
      only when a real evidence field resolved
      → Done: spot-check caught and fixed a false-clean bug (doc_presence/doc_completeness were
      marked `COMPILABLE` unconditionally); corrected before commit
- [x] T006 Emit two Routes (`conventional`, `government`) with per-Route Block objects
      (`conv-<slug>`/`gov-<slug>`) so the same AMQ category can carry a different check population
      per Route, per Gordon's no-Fannie/Freddie-split call
      → Done: `frontend/src/data/goldCatalog.json` — 1,105 checks, 16 blocks per Route (208
      `COMPILABLE`, 642 `NEEDS_FIELDS`, 108 `NOT_MECHANIZABLE`, 147 `NEEDS_SME`)

---

## Phase 2: Frontend types (done)

- [x] T007 [P] Add `NOT_COMPILED` to `CheckStatus` in `frontend/src/lib/types.ts`
- [x] T008 [P] Add missing `agree_doc_numeric` to `Check.kind` (pre-existing gap, already
      implemented in `p0/qc_engine/engine.py:285`)
- [x] T009 [P] Repurpose `SourceLocator` as `{ruleId, cardId}`; update the 12 mock-data call sites in
      `frontend/src/data/mockData.ts` and `frontend/src/components/SourceCitation.tsx`'s rendering
- [x] T010 [P] Add `Authorability` type + `Check.authorability`/`authorabilityReason`/`compileState`
- [x] T011 Add `resolveJsonModule` to `frontend/tsconfig.app.json`
      → Done when: `npx tsc -b` exits 0 — confirmed

---

## Phase 3: The authoring surface (done — priority page)

- [x] T012 Wire `frontend/src/components/RoutesFlow.tsx` to `GOLD_ROUTES`/`GOLD_BLOCKS`/
      `GOLD_CHECKS` (new `frontend/src/data/goldCatalog.ts` loader) instead of mock data
- [x] T013 `frontend/src/components/BlockDetail.tsx`: authorability-first pool sort, honest
      "N compilable / M total" count, never-green styling for non-`COMPILABLE` checks (available +
      active lists)
- [x] T014 `BlockDetail.tsx`: fix loan-scope-honesty bug — Government blocks now show zero available
      checks via an explicit `isGovernmentBlock` guard, with an honest empty-state message
      → Found via Gordon's own review of the running app
- [x] T015 `frontend/src/components/RouteDetail.tsx`: fix duplicate-blocks bug — scope the
      available/active block pools to the current route's own id prefix (`conv-`/`gov-`) so
      Government's blocks no longer appear as "available" duplicates on Conventional's screen and
      vice versa
      → Found via Gordon's own review of the running app (screenshot)
- [x] T016 [P] Update `frontend/src/components/StatusBadge.tsx` (`NOT_COMPILED` styling) and
      `SourceCitation.tsx` (render `{ruleId, cardId}`) to match the type changes
      → Done when: `npx tsc -b` clean AND `npm run build` succeeds — confirmed (2,206 modules)

---

## Phase 4: Filter/search inside Available & Active checks (done, 2026-08-01)

**Third pass at Phase 4's scope, same day.** First pass: full `RuleCatalog.tsx` screen (deferred).
Second pass: a route-level "Built Checks" tab aggregating `COMPILABLE` checks across a route's active
blocks (built, then reviewed against a screenshot). **Gordon's correction, via screenshot + `/grill-me`
(2026-08-01):** the built-only concept was never meant to be its *own* list — it's filtering *within*
`BlockDetail.tsx`'s existing Available/Active columns, which already show every check (built and not).
The route-level tab was reverted; `RouteDetail.tsx` is back to its pre-Phase-4 form. Final scope: filter
controls (severity · kind · AOR · name/description search) added directly to **both** the Available
(left) and Active (right) columns in `BlockDetail.tsx`, narrowing what's already there rather than
surfacing a separate view. No explicit sort control — existing default ordering (authorability-first
in Available; unchanged order in Active) stays, filters narrow rather than re-sort. T017-T022 IDs
preserved unrenumbered per spec-kit convention; descriptions below reflect what was actually built.

- [x] T017 Add a `aor: string[]` field to `Check` (`frontend/src/lib/types.ts`) and populate it in
      `frontend/scripts/build_gold_catalog.py` from the gold card's `finding.aor` (deduped) →
      regenerated `goldCatalog.json`; 208/1,105 checks are `COMPILABLE`, spanning 3 AOR values
      (Underwriter, Processor, Closer), 3 kinds, 2 severities
- [x] T018 ~~Tab toggle on `RouteDetail.tsx`~~ (reverted — the built-only concept lives inside
      `BlockDetail.tsx`'s existing columns instead, not a separate tab/view; `RouteDetail.tsx` is
      back to its original two-column Blocks-only form)
- [x] T019 `CheckFilterBar` + `filterChecks()` (`BlockDetail.tsx`): reusable filter bar rendered
      above **both** the Available and Active columns, each with independently-scoped state
      (`availableFilter`/`activeFilter`) and options derived from that column's own checks —
      reset to empty on block navigation (`useEffect` keyed on `block.id`)
- [x] T020 ~~Yellow sub-reason from `authorabilityReason`~~ (out of scope — filtering narrows the
      existing columns, which already show `authorabilityReason` via the existing amber "wired, not
      yet buildable" tag; nothing new needed here)
- [x] T021 Filters: severity · kind · AOR, each populated from the real values present in the
      column being filtered (not a static enum), plus a search box over check name + description —
      wired to both Available and Active columns
- [x] T022 ~~Surface the `NOT_COMPILED` + `NEEDS_FIELDS` intersection~~ (deferred — out of scope;
      the Available column already shows both compilable and non-compilable checks together,
      authorability-first, which is the honest-coverage requirement FR-008/FR-011 already cover)

---

## Phase 5: Storage, Save, Restore (next — redefined 2026-08-01)

**Redefined from the original Export-based design**: no Export/download file — replaced with a
**Restore to Gold** button (discard local edits, reset to the original gold-sourced catalog). No
"local draft" labeling requirement either. T026 below is rewritten in place to match (not
renumbered).

- [x] T023 Create `frontend/src/lib/rulesetStore.ts`: serialize
      `{content, sha256, provenance, intent_records, signoff_summary}`
- [x] T024 Save → `localStorage`, auto-persisted on every content change (decoupled from Sign & Pin,
      so a refresh mid-edit never loses work); explicit quota-exceeded error surfaced as a banner
- [x] T025 On load, reconcile a stored draft against the current catalog; missing checks reported via
      a visible banner, not failed silently
- [x] T026 **Restore to Gold button** *(redefined — was Export)*: discards the local `localStorage`
      draft and resets in-memory state back to `GOLD_ROUTES`/`GOLD_BLOCKS`/`GOLD_CHECKS`
      (`goldCatalog.ts`) — a clean reset, not a file download. No "local draft" label.
- [x] T027 Wired `RoutesFlow.tsx` to hydrate from the store on mount; replaced `fakeHash()` with a
      real SHA-256 digest (`crypto.subtle.digest`) computed in `signAndPin`
- [x] T028 **Gold-isolation guard (non-negotiable)**: satisfied structurally, not by runtime
      assertion — `rulesetStore.ts` only ever calls browser `localStorage`, which has zero
      filesystem access; there is no code path by which it could touch `storage/rules/gold/` even
      by accident
      → Done: `tsc -b` clean, `npm run build` succeeds (2,207 modules)

---

## Phase 6: Reconcile with the other worktree's converter (deferred, not blocking)

- [ ] T029 Once `.claude/worktrees/gold-ruleset-plan` is confirmed free, compare this spec's
      independent mapper (Phase 1) against `p0/qc_engine/compiler/import_gold_ruleset.py`'s output;
      reconcile differences

## Phase 7: Promotion gate (deferred, not blocking)

- [ ] T030 Define and implement a `draft → verified → active` lifecycle gate (CLI script) — every
      gold card is `status: draft` today; needed before any real audit runs on gold data, not needed
      for the authoring UI

## Phase 8: Engine extensions (deferred, lower priority)

- [ ] T031 `date_window` kind (62 checks)
- [ ] T032 Computation-formula backlog (gross-up %, ARM qualifying rate, PITIA, points & fees)
- [ ] T033 `list_screening` (needs a versioned reference-dataset loader)
- [ ] T034 `reverification` (needs a re-verification data source)

---

## Phase 9: Correct the misleading docs (done)

- [x] T035 [P] Add superseded-by headers to `docs/frontend/SHACL-UI-COMPATIBILITY-ANALYSIS.md` and
      `docs/frontend/RULE-TO-CHECK-UI-MODEL.md` (both untracked on `main` until this session; now
      tracked in this branch)
- [x] T036 [P] Thin update to `storage/rules/gold/README.md` cross-referencing constitution v1.2.0
      Principle VII
- [x] T037 A `### 019-workbook-first-rule-authoring` entry already existed in `output/ROADMAP.md`
      (contrary to this task's original assumption that one needed adding) — added a
      "superseded again" header to it instead, applied directly to main's live copy (not bundled
      into this branch — that file carries ~100 lines of unrelated uncommitted WIP)
      → Done when: `grep -rn "016-shacl-frontend-integration\|src/shacl_pilot/workbook_ingest"`
      returns only intentional "superseded by" references — confirmed

## Phase 9b: Rework the FR/SC/User Story contradiction found by `/speckit-analyze` (done)

**Found**: `/speckit-analyze` (2026-08-01) caught that the "2026-08-01 Rework" section added to
spec.md only covered the storage-model section — the numbered Functional Requirements (FR-001–017),
Success Criteria (SC-001–012), and User Stories 1-4/7 + Edge Cases still described the retired
workbook-ingestion approach verbatim, contradicting the rework section a few paragraphs above them in
the same file. Flagged CRITICAL (constitution conflict + internal inconsistency).

- [x] T038 Rewrite FR-001/002/003/006/010 as explicitly `RETIRED`; update FR-004/005/007/008/012 to
      reflect what Phase 1-3 actually built; update FR-014/015/016/017 with real counts (1,105/208/897)
      and vocabulary (`authorabilityReason`, not `yellow_blocker_type`)
- [x] T039 Same treatment for SC-002/003/005 (retired), SC-001/004/006/007/008/009/010/012 (updated
      with real results/counts)
- [x] T040 Retire User Story 3 (custom SHACL compiler); update User Story 4's export scenario, User
      Stories 1-2's stale counts/`sourceLocator` claim, and User Story 7's counts/vocabulary; add two
      new Edge Cases for the duplicate-blocks bugs found via Gordon's review
      → Done when: `grep -n "3,369\|3,370\|3,357\|yellow_blocker_type\|workbook_ingest\|ruleset_to_shacl"
      specs/019-workbook-first-rule-authoring/spec.md` returns only retired-and-marked or legitimate
      historical-background hits — confirmed

---

## Dependencies

```
T001-T002 (Phase 0, done) ──► informs 032, not a build dependency
T003-T006 (Phase 1, done) ──► T007-T011 (Phase 2, done) ──► T012-T016 (Phase 3, done)
                                                          ├──► T017-T022 (Phase 4)
                                                          └──► T023-T028 (Phase 5)
T003-T006 ──────────────────────────────────────────────────► T029 (Phase 6, deferred)
T029 ──► T030 (Phase 7, deferred) ──► T031-T034 (Phase 8, deferred)
T035-T037 (Phase 9) — any time after Phase 1; do last
```

Phase 4 and Phase 5 are independent after Phase 3 and can proceed in parallel.

---

## Phase 10: Convergence

Found by `/speckit-converge` (2026-08-01) — real gaps in code already marked done in Phase 3,
plus one noticed while verifying. Not a re-listing of Phase 4/5 (T017-T028), which are already
tracked as pending.

- [ ] T041 Implement FR-009's collapse-by-default behavior above 50 checks per block in
      `frontend/src/components/BlockDetail.tsx` (missing)
- [ ] T042 Add the FR-009 search control (check name / description / question text) to
      `frontend/src/components/BlockDetail.tsx` (missing)
- [ ] T043 Wire `CheckEditor`'s `FieldPicker` in `frontend/src/components/BlockDetail.tsx` to a
      real field source instead of `MOCK_FIELD_CATALOG` per FR-005 / the field-catalog Assumption
      (partial)
