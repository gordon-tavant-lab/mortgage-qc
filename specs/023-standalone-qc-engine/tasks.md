# Tasks: Standalone `engine/` — the definitive official QC audit engine

**Input**: Design documents from `specs/023-standalone-qc-engine/`
**Prerequisites**: plan.md, spec.md

**Tests**: This feature's own correctness test IS one of its deliverables (FR-004, US2) — the
25/25 standing-gate harness travels with the copy so `engine/` can prove itself standalone.
Included below as real tasks, not optional scaffolding.

**Organization**: Tasks are grouped by user story (US1/US2/US3 from spec.md) so each can be
verified independently, though in practice they share the same copy operation (Phase 1).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task serves

## Phase 0: Pre-flight (resolve the one pre-existing loose end)

- [x] T001 Revert pre-existing, unrelated uncommitted drift in
  `p0/fixtures/from_docs/loan_02.json`, `loan_03.json`, `loan_05.json` (accidental citation-text
  truncation, unrelated to this feature) via `git checkout --` so `engine/` inherits clean data
  and `p0/`'s tree returns to its last-known-good committed state. *(Done ahead of task
  generation — see spec.md Assumptions.)*

## Phase 1: Setup — create the directory skeleton

**Purpose**: Establish `engine/`'s structure before any file lands in it. Serves US1/US2/US3
jointly (there's no independent "US1-only" subset of the directory tree).

- [x] T002 Create `engine/qc_engine/`, `engine/qc_engine/compiler/`,
  `engine/qc_engine/adapters/`, `engine/fixtures/from_docs/` (all via `mkdir -p`)

## Phase 2: Core copy — the engine package (blocks US1)

**Purpose**: Copy the traced-minimal `qc_engine/` core. No user story is testable until this
phase completes.

- [x] T003 [P] Copy `p0/qc_engine/__init__.py` → `engine/qc_engine/__init__.py`
- [x] T004 [P] Copy `p0/qc_engine/money.py` → `engine/qc_engine/money.py`
- [x] T005 [P] Copy `p0/qc_engine/model.py` → `engine/qc_engine/model.py`
- [x] T006 [P] Copy `p0/qc_engine/reconcile.py` → `engine/qc_engine/reconcile.py`
- [x] T007 [P] Copy `p0/qc_engine/ruleset.py` → `engine/qc_engine/ruleset.py`
- [x] T008 [P] Copy `p0/qc_engine/catalog.py` → `engine/qc_engine/catalog.py`
- [x] T009 [P] Copy `p0/qc_engine/engine.py` → `engine/qc_engine/engine.py`
- [x] T010 [P] Copy `p0/qc_engine/audit.py` → `engine/qc_engine/audit.py`
- [x] T011 [P] Copy `p0/qc_engine/mismo.py` → `engine/qc_engine/mismo.py` (FR-005)
- [x] T012 [P] Copy `p0/qc_engine/field_catalog.json` → `engine/qc_engine/field_catalog.json` (FR-004)

---

## Phase 3: User Story 1 - Run the QC engine without any experimental baggage (Priority: P1)

**Goal**: A complete, standalone compile-and-evaluate pipeline exists in `engine/`, producing
the same verdicts as `p0/`.

**Independent Test**: Run the adapter then the compiler from `engine/` against the real
Touchless sample loan; verdict distribution matches `p0/`'s current run exactly (SC-002).

- [x] T013 [P] [US1] Copy `p0/qc_engine/compiler/__init__.py` →
  `engine/qc_engine/compiler/__init__.py`
- [x] T014 [US1] Copy `p0/qc_engine/compiler/import_gold_ruleset.py` →
  `engine/qc_engine/compiler/import_gold_ruleset.py` (depends on T003–T012, T013)
- [x] T015 [US1] Edit `RUN_DIR` in `engine/qc_engine/compiler/import_gold_ruleset.py` from the
  literal `compile_runs/bakeoff_gold_touchless_2026-07-31` to `compile_runs/default` (FR-007;
  the ONE deliberate code diff between this copy and `p0/`'s original — depends on T014)
- [x] T016 [P] [US1] Copy `p0/qc_engine/adapters/__init__.py` →
  `engine/qc_engine/adapters/__init__.py`
- [x] T017 [P] [US1] Copy `p0/qc_engine/adapters/touchless_adapter.py` →
  `engine/qc_engine/adapters/touchless_adapter.py`
- [x] T018 [US1] Copy `p0/fixtures/from_docs/fixture_loader.py` →
  `engine/fixtures/from_docs/fixture_loader.py` (required at runtime by
  `import_gold_ruleset.py`'s `main()`, see plan.md Technical Context)
- [x] T019 [US1] Verify (Acceptance Scenario 1+2): run
  `engine/qc_engine/adapters/touchless_adapter.py` against
  `demo/touchless/loan_application.json` + `extracted_data_e59d57a9-...json`, then run
  `engine/qc_engine/compiler/import_gold_ruleset.py --loan-fixture <output>`; confirm verdict
  distribution == PASS 133 / NEEDS_REVIEW 92 / NOT_APPLICABLE 443 / NOT_COMPILED 437 (SC-002)

**Checkpoint**: US1 is independently functional and testable here.

---

## Phase 4: User Story 2 - Prove the engine's own correctness claim standalone (Priority: P2)

**Goal**: `engine/` can run its own 25/25 standing gate with zero dependency on `p0/`.

**Independent Test**: `verify_against_defects.py` reports 25/25 from inside `engine/` (SC-003).

- [x] T020 [P] [US2] Copy `p0/fixtures/from_docs/verify_against_defects.py` →
  `engine/fixtures/from_docs/verify_against_defects.py`
- [x] T021 [P] [US2] Copy `p0/fixtures/from_docs/defect_manifest.json` →
  `engine/fixtures/from_docs/defect_manifest.json`
- [x] T022 [P] [US2] Copy `p0/fixtures/from_docs/loan_01.json` through `loan_05.json` (5 files) →
  `engine/fixtures/from_docs/` (post T001's drift revert — copying the clean, committed versions)
- [x] T023 [US2] Verify (Acceptance Scenario 1): run
  `engine/fixtures/from_docs/verify_against_defects.py` standalone; confirm 25/25 (SC-003) with
  no import reaching into `p0/` (depends on T005 for `fixture_loader.py`'s `qc_engine.model`
  dependency, T018, T020–T022)

**Checkpoint**: US2 is independently verifiable here, and US1+US2 together mean `engine/` is
functionally and correctness-wise complete.

---

## Phase 5: User Story 3 - `p0/` remains fully intact after the extraction (Priority: P1)

**Goal**: Confirm the entire extraction was additive-only.

**Independent Test**: `git diff` under `p0/` is empty; `p0/`'s own gates are unchanged.

- [x] T024 [US3] Verify (Acceptance Scenario 1): `git status`/`git diff` shows zero modifications
  under `p0/` (SC-004) — depends on all copy tasks above being complete (nothing left to
  accidentally touch)
- [x] T025 [US3] Verify (Acceptance Scenario 2): re-run `pytest p0/` (expect 445 passed / 3
  skipped / 1 xfailed) and `p0/fixtures/from_docs/verify_against_defects.py` (expect 25/25);
  confirm identical to pre-extraction results (SC-005)

---

## Phase 6: Polish — the one new authored file

**Purpose**: Meet FR-009 — a copy with no explanation doesn't meet the "definitive official
engine" bar.

- [x] T026 [P] Author `engine/README.md`: the three-command flow (adapt → compile+evaluate →
  verify), a note that `storage/rules/gold/data/` is read by relative path and lives outside this
  folder, and a one-line pointer that `p0/` remains the experimental/historical workspace this
  copy was extracted from
- [x] T027 Final verification (Acceptance Scenario 3 / SC-001): `find engine -type f` matches
  the planned file list in plan.md's Project Structure exactly; confirm the README alone (no
  session context) is sufficient to run the three-command flow

## Dependencies & Execution Order

- Phase 0 (done) → Phase 1 → Phase 2 → Phase 3 (US1) → Phase 4 (US2) → Phase 5 (US3) → Phase 6
- Within Phase 2, T003–T012 are all `[P]` (independent file copies, no cross-dependencies)
- T014 depends on the full Phase 2 set landing first (imports `qc_engine.ruleset`)
- T015 must follow T014 (edits the file T014 just copied)
- T019 depends on the complete Phase 3 copy set (T013–T018)
- T023 depends on T005 (already done, Phase 2) + T018 (Phase 3) + T020–T022 (this phase)
- T024/T025 depend on every copy task above completing (nothing left that could still touch `p0/`)
- T026 has no code dependency (pure authoring) but is sequenced last since it documents the
  finished result; T027 depends on T026

## Parallel Example

```
# Phase 2 core files can all be copied together (10 independent file operations):
T003, T004, T005, T006, T007, T008, T009, T010, T011, T012
```

## Implementation Strategy

**MVP first**: Phase 1 + Phase 2 + Phase 3 (T002–T019) alone already delivers US1 — a working,
standalone compile-and-evaluate pipeline. Phases 4–6 add self-verification, the `p0/`-intact
guarantee, and documentation on top, but US1 is real value on its own the moment T019 passes.
