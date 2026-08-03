# Implementation Plan: 019-workbook-first-rule-authoring

**Spec**: `spec.md` (same directory)
**Created**: 2026-07-30
**Reworked**: 2026-08-01 (see spec.md's "2026-08-01 Rework" section and decision
[032](../../src/decisions/032-spec019-rework-onto-gold-ruleset.md))
**Status**: In progress — Phases 0-3 done, Phase 4-5 next, Phases 6-8 deferred (not blocking)

> **Phase 0 gates everything below it, historically.** It's done — see its own section — and its
> finding (decision 031) is why the phases after it now target the gold ruleset instead of
> re-ingesting the workbook a second time. The phases below Phase 0 are the 2026-08-01 rework;
> the original Phase 1 ("ingest the workbook") and Phase 5 ("the compiler," as originally scoped) are
> retired — see spec.md.

---

## Phase 0 · Restore the audit baseline  *(done, historical)*

**Why**: `src/shacl_pilot/out/` holds only `full_5loan_audit_latest.md` and
`green_only_audit_loan01.md`. Every `loan_NN.json` and `loan_NN.ttl` those runs consumed is gone. The
25/25 claim is a report from a past run, not a reproducible fact. If a later change yields 23/25 we
must be able to tell whether we broke two detections or whether it was 23 before we touched anything.

**Steps**

1. For each of `demo/syn/loan 01` … `loan 05`:
   `python3 src/shacl_pilot/extract_loan.py "demo/syn/loan NN" src/shacl_pilot/out/loan_NN.json`
   (the extractor never parses `00_Loan_Summary_And_Answer_Key.pdf` — `ANSWER_KEY_RE` guards it).
2. `python3 src/shacl_pilot/loan_to_rdf.py` for each → `src/shacl_pilot/out/loan_NN.ttl`.
3. `python3 src/shacl_pilot/run_full_ruleset_audit.py <loan_ttl> src/shacl_pilot/compiled/ruleset.json`
   for each loan.
4. **Record the actual detection number** in `specs/019-.../BASELINE.md`, with the per-loan breakdown
   and the shapes-manifest version that produced it.
5. Run twice; confirm byte-identical output (determinism).

**Exit criteria (SC-001)**: `BASELINE.md` exists with a real, dated number. If it is not 25/25, that is
the finding — report it and stop for a scope decision rather than proceeding on a stale premise.

**Result**: 4/20,830 rule-loan pairs, not 25/25. Determinism verified. See `BASELINE.md` and decision
031 — this finding is why the phases below no longer target `demo/syn/loan 01-05` or Pipeline A.

---

## Phase 1 · Gold-to-Check mapper  *(done — replaces the original "ingest the workbook")*

**New**: `frontend/scripts/build_gold_catalog.py`

Reads `storage/rules/gold/data/{rules_compiled.json,rules_atomic.json}` directly and emits
`frontend/src/data/goldCatalog.json`. Independent of both engines (Pipeline A `src/shacl_pilot`,
Pipeline B `p0/qc_engine`) and of the separate, in-progress `gold-ruleset-plan` worktree — a pure
data-shape translation for the authoring UI, not a compile-to-executable-logic step.

1. Map each gold card's defect options (or, when a card has been decomposed, its atomic rules —
   linked via `provenance.parent_card_id`, since `defect_options[].atomic_rule_ids` is never
   populated in the compiled file) to a `Check`: `check_type`→`kind`, `applicability`→`appliesIf`,
   `citations`→`grounding`, `category`→`Block`.
2. **Authorability, re-derived from gold + evidence resolution** (kept from the original FR-005, not
   dropped): `COMPILABLE` only when a real evidence field resolved (an atomic rule's
   `evidence[0].field`/`.name`); otherwise `NEEDS_FIELDS` (doc_presence/doc_completeness/
   cross_doc_consistency/threshold_eligibility/computation without resolved evidence), `NEEDS_SME`
   (`scripted_review`, by design), or `NOT_MECHANIZABLE` (`date_window`/`list_screening`/
   `reverification`/`routing_context`, or an unrecognized `check_type`). Conservative by design —
   caught and fixed one false-clean bug during spot-check: doc-presence checks were initially marked
   `COMPILABLE` unconditionally regardless of whether evidence actually resolved.
3. Two Routes only (Gordon, 2026-08-01 — no Fannie/Freddie or FHA/VA/USDA sub-split anywhere):
   **Conventional** (real gold-sourced checks) and **Government** (same ~16 blocks, zero checks —
   gold has no FHA/VA/USDA/Freddie coverage). Each Route gets its own Block objects per AMQ category
   (ids prefixed `conv-`/`gov-`) so the same category name can carry a different check population
   depending on which Route it's viewed through.

**Exit criteria**: mapper output spot-checked against real gold cards. **Result**: 1,105 checks / 16
blocks per Route — 208 genuinely `COMPILABLE`, 642 `NEEDS_FIELDS`, 108 `NOT_MECHANIZABLE`, 147
`NEEDS_SME`.

---

## Phase 2 · Frontend types  *(done)*

**Modified**: `frontend/src/lib/types.ts`

1. Added `NOT_COMPILED` to `CheckStatus` (never ran, distinct from `NOT_APPLICABLE`).
2. Added missing `agree_doc_numeric` to `Check.kind` (pre-existing gap, unrelated to this rework —
   already implemented in `p0/qc_engine/engine.py:285`, just missing from the frontend union; fixed
   while the file was already being touched).
3. Repurposed `SourceLocator` as `{ruleId, cardId}` (gold has no workbook sheet/row; has stable IDs
   instead). Updated the 12 mock-data call sites and `SourceCitation.tsx`'s rendering to match.
4. Added `Authorability` type + `Check.authorability`/`authorabilityReason`/`compileState` — the
   authorability concept, kept and re-platformed onto gold, not dropped.
5. Left the header comment as-is ("mirrors p0/qc_engine's real classes") — it's already correct;
   the original plan would have "corrected" it to claim a workbook+SHACL provenance that was never
   true (see spec.md's rework section).

**Modified**: `frontend/tsconfig.app.json` — added `resolveJsonModule` for the catalog import.

**Exit criteria**: `tsc -b` clean. **Result**: confirmed clean; `npm run build` also succeeds (2,206
modules, no errors).

---

## Phase 3 · The authoring surface  *(done — this is the page Gordon is focused on)*

**Modified**: `frontend/src/components/RoutesFlow.tsx` — initializes from `GOLD_ROUTES`/
`GOLD_BLOCKS`/`GOLD_CHECKS` (`frontend/src/data/goldCatalog.ts`, a typed loader over Phase 1's
output) instead of mock data.

**Modified**: `frontend/src/components/BlockDetail.tsx`

1. **Authorability-first pool** (FR-008, re-platformed): `COMPILABLE` checks sort first; header
   shows an honest "N compilable / M total" count, replacing the old plain count.
2. **Non-executable never green** (FR-011): dashed border + muted "not yet buildable" badge (with
   the reason on hover) for non-`COMPILABLE` checks in the available pool; an amber "wired, not yet
   buildable" tag in the active list for anything wired despite not being `COMPILABLE` (activation is
   still allowed — flagging for human review is a valid intentional use, not a bug — it's just never
   shown as ready).
3. **Loan-scope honesty, Government blocks** (bug found via Gordon's own review, fixed): the
   available-checks filter matched only on category name (`c.category === block.name`), which meant
   opening a Government block showed the *same* Fannie-sourced checks as its Conventional
   counterpart — an SME could wire a check into a program it was never written for. Fixed with an
   explicit `isGovernmentBlock` guard (by `block.id` prefix): Government blocks now show zero
   available checks, with an honest empty-state message explaining why, not a generic "none left"
   message.

**Modified**: `frontend/src/components/RouteDetail.tsx` — **second duplicate-blocks bug found via
Gordon's own review, fixed**: the available-*blocks* pool (one level up from checks) had the same
flaw — it showed every block not already wired into the *current* route, including the *other*
route's same-category block (e.g. viewing Conventional's "Available Blocks" listed "Assets
(Government)" right next to the real "Assets (Conventional)" in "Active Blocks" — confusing
duplicates, not a real choice). Fixed by scoping both the available and active block pools to the
current route's own id prefix (`conventional`→`conv-`, `government`→`gov-`); custom SME-created
routes (no recognized prefix) keep the original shared-pool behavior.

**Modified**: `frontend/src/components/StatusBadge.tsx`, `SourceCitation.tsx` — supporting styling
and rendering fixes for the type changes above.

**Exit criteria**: `tsc -b` clean, `npm run build` succeeds. Screenshot verification via
chrome-devtools MCP was not possible this session (the shared browser profile was held by another
concurrent session; did not force a restart) — verified instead via clean production build, then
directly by Gordon running the dev server locally, who found and reported both duplicate-blocks bugs
above.

---

## Phase 4 · Rule Catalog screen  *(next)*

**New**: `frontend/src/components/RuleCatalog.tsx` + a `catalog` entry in `lib/nav.ts` and `App.tsx`

Distinct from Phase 3: `BlockDetail` is the *authoring* surface for one block; this is the
*coverage* surface for the whole ruleset — "what does the tool cover today."

1. Render all **1,105** checks with per-block and per-status counts (re-sourced from Phase 1's
   mapper output, not the old `ruleset.json`'s 3,369).
2. Compile state: green `COMPILED` (208 checks, real evidence resolved) vs. yellow `NOT_COMPILED`
   (897) — never reuse the verdict badge color (`StatusBadge.tsx`'s `NOT_COMPILED` styling, already
   built in Phase 2, applies here too).
3. Yellow sub-reason: gold's own `compile.failure_category` / this mapper's `authorabilityReason`,
   not `yellow_blocker_type` (doesn't exist on gold cards).
4. Filters: compile state · authorability · block · severity · Route. Search over check name /
   description / question text.
5. Surface the `NOT_COMPILED` + `NEEDS_FIELDS` intersection as its own view — the
   buildable-but-not-yet-built work queue.
6. Virtualize/group if needed — measure bundle size first; gold's ~1,100 checks is far smaller than
   the old 3,370-check catalog the original plan sized virtualization against.

**Exit criteria**: counts reconcile against a direct recount of Phase 1's mapper output.

---

## Phase 5 · Storage, Save, Export  *(next)*

**New**: `frontend/src/lib/rulesetStore.ts`

Survives near-verbatim from the original plan — this phase never depended on which pipeline compiled
the catalog.

1. Serialize the authored ruleset: `{content: {checks, engine_version, ruleset_id, version}, sha256,
   provenance, intent_records, signoff_summary}`.
2. Save → `localStorage`, keyed by ruleset id. Handle quota exhaustion with an explicit error
   directing the SME to Export.
3. On load, reconcile a stored draft against the current catalog; report checks that no longer exist
   rather than failing silently.
4. Export → download the JSON. Document that a human places it at `storage/rules/vN.json`.
5. Label the control a **local draft**. Never imply a server.
6. Wire `RoutesFlow.tsx` to hydrate from the store, replace `fakeHash()` with a real digest.

**Gold-isolation guard — unchanged and non-negotiable**: `storage/rules/gold/` is read-only reference
data (now committed to this branch, still untracked on `main`). Save/Export MUST target the
`storage/rules/` root only and MUST NEVER write into or delete anything under `storage/rules/gold/`.

**Exit criteria**: activate → Save → reload → persists → Export → downloads valid JSON. Gold-isolation
guard: after Save/Export runs, the file list and hashes under `storage/rules/gold/` MUST be identical
to before.

---

## Phase 6 · Reconcile with the other worktree's converter  *(deferred, not blocking)*

`.claude/worktrees/gold-ruleset-plan` has a working `p0/qc_engine/compiler/import_gold_ruleset.py`
and a live Pipeline A vs. B bake-off — genuinely useful prior art, but that worktree was confirmed
in active use by another session. Do not start this phase until it's confirmed free. When it is: compare
this spec's independent mapper (Phase 1) against that converter's output; reconcile any differences;
decide whether one supersedes the other or both remain (one feeds the authoring UI, one feeds a
future runtime engine).

## Phase 7 · Promotion gate (draft → verified → active)  *(deferred, not blocking)*

Every gold card is `status: draft` today. Needed before any *real audit* runs on gold data — not
needed for the *authoring UI* to exist, which is why it's deferred behind Phases 4-5.

## Phase 8 · Engine extensions  *(deferred, lower priority)*

The ~20% of checks gold can't express yet (`date_window`, computation-formula backlog,
`list_screening`, `reverification`). Not required to ship the author page.

---

## Phase 9 · Correct the misleading docs

**`docs/frontend/SHACL-UI-COMPATIBILITY-ANALYSIS.md`** and **`docs/frontend/RULE-TO-CHECK-UI-MODEL.md`**
— add a superseded-by header pointing at this rework; both still describe a workbook→UI→SHACL flow
that is now itself superseded by workbook→gold→Pipeline-B-shaped-types (Phase 1's mapper).

**`storage/rules/gold/README.md`** — thin update noting it is now spec019's canonical input
(cross-reference constitution v1.2.0 Principle VII, don't duplicate its language).

**`output/ROADMAP.md`** — add a `### 019-workbook-first-rule-authoring` entry noting the 2026-08-01
rework, in the house style of the `015` entry.

**Exit criteria**: `grep -rn "016-shacl-frontend-integration\|src/shacl_pilot/workbook_ingest"`
returns only intentional "superseded by" references.

---

## Sequencing

```
Phase 0 (baseline, done)  ──►  informs the rework decision (031/032), not a build dependency
Phase 1 (gold mapper, done)  ──►  Phase 2 (types, done)  ──►  Phase 3 (authoring, done)
                                                          ├──►  Phase 4  (catalog screen)
                                                          └──►  Phase 5  (storage)
Phase 1 ──────────────────────────────────────────────────────►  Phase 6  (reconcile, deferred)
Phase 6 ──► Phase 7 (promotion gate, deferred) ──► Phase 8 (engine extensions, deferred)
Phase 9  (docs — any time after Phase 1; do last so corrections reflect what was built)
```

Phases 4 and 5 are independent after Phase 3 and can proceed in parallel. Phases 6-8 explicitly wait
— none block shipping the rule-author page.

## Risks

| Risk | Mitigation |
|---|---|
| Authorability verdict too permissive | Conservative by design; caught and fixed one real instance during Phase 1's own spot-check (doc-presence checks marked `COMPILABLE` without resolved evidence) — treat future additions with the same suspicion. |
| Duplicate/confusing blocks across Routes | Found twice during Gordon's own review (checks pool, then blocks pool) — both fixed with explicit id-prefix scoping in Phase 3. Any new per-Route UI surface should scope by this same convention from the start, not discover the gap the same way. |
| `localStorage` quota exceeded | Explicit error + Export path (Phase 5). |
| Reconciling with the other worktree's converter (Phase 6) | Explicitly deferred; do not touch that worktree until confirmed free. |
| `fieldId` validity depends on a field catalog that may not match the eventual audit engine | Documented as an open caveat (spec.md Assumptions) — not blocking, revisit if Pipeline A wins the live bake-off. |
