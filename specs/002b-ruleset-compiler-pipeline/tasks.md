# Tasks: Ruleset Compiler Pipeline

**Input**: Design documents from `specs/002b-ruleset-compiler-pipeline/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included — SC-001 through SC-006 are explicit, measurable gates (spec.md Success
Criteria), not optional; zero regression against every prior feature's hash/digest is a hard gate
(Principle I).

**Organization**: Tasks grouped by user story (spec.md P1/P1/P1/P2/P1), plus one cross-cutting phase
for FR-003 (duplicate-vocabulary detection), which spec.md defines as a bare functional requirement
with no dedicated User Story of its own (no Independent Test / Acceptance Scenarios attached to it
directly — only SC-002).

**Scoping finding (from reading `catalog.py` before writing this file)**:
`validate_referential_integrity` raises on the *first* unresolved check in a `Ruleset` and stops —
proven correct for its one-shot use in `p0/harness.py`, but insufficient for User Story 3's
per-check, batch-scale reporting need. T017 below wraps it (calls it once per candidate check via a
throwaway single-check `Ruleset`); it does **not** modify the function itself, preserving spec.md's
explicit "reuse verbatim" requirement (research.md Decision 4).

## Phase 1: Setup

- [x] T001 [P] Grep all call sites of `Ruleset(...)`, `Ruleset.to_json()`, `Ruleset.from_dict()`
      across `p0/qc_engine/`, `p0/tests/`, `p0/harness.py` to confirm the planned additive
      `intent_records` field cannot break an existing caller (mirrors `001b`'s T001 diligence
      pattern before touching a shared dataclass)
- [x] T002 [P] Scaffold `p0/qc_engine/compiler/` package (`__init__.py`) per plan.md's Project
      Structure — the fresh production module distinct from `p0/experiment_002a/`'s throwaway
      scripts (spec.md Edge Cases)

---

## Phase 2: Foundational (Blocking Prerequisites)

**⚠️ CRITICAL**: User Stories 1 and 5 both depend on the extended `Ruleset` shape existing first;
User Story 1 depends on a real-row batch sampler existing first.

- [x] T003 Add `RuleIntentRecord` dataclass + `Ruleset.intent_records: List[RuleIntentRecord]` field
      (default empty list) + `Ruleset.intent_for(check_id)` lookup method in
      `p0/qc_engine/ruleset.py`, per data-model.md §2 (depends on T001)
- [x] T004 Extend `Ruleset.to_json()`/`Ruleset.from_dict()` to persist/restore `intent_records`,
      mirroring the existing `provenance` list's persistence pattern exactly. Verify
      `canonical_content()` and `sha256()` are **untouched** (still only `ruleset_id`/`version`/
      `engine_version`/`checks`) — every existing determinism digest and catalog hash from `001a`/
      `001b` must remain byte-identical (depends on T003)
- [x] T005 [P] Generalize `p0/experiment_002a/sample_rows.py`'s stratified-sampling pattern into
      `p0/qc_engine/compiler/sample.py`: draws N > 24 real rows from `p0/eval_synth/taxonomy.py`'s
      already-classified workbook rows — a production module, not a throwaway-experiment extension
      (depends on T002)

**Checkpoint**: Foundation ready — user story work can begin.

---

## Phase 3: User Story 1 — Compile a real batch into the same signed-artifact shape (Priority: P1) 🎯 MVP

**Goal**: Scale `002a`'s n=24-proven compile mechanism to a production batch, producing `Check`
drafts conforming exactly to the existing schema, assembled into a `Ruleset` with a stable SHA-256.

**Independent Test**: Compile a batch of N > 24 real workbook rows; confirm N `Check` drafts are
produced, each a valid `Check` instance, with zero new fields.

### Tests for User Story 1 ⚠️ (write first, confirm FAIL before implementation)

- [x] T006 [P] [US1] Test: compiling a batch of N > 24 rows produces N valid `Check` drafts, each an
      instance of the existing dataclass with no new fields (spec.md US1 Scenario 1), in
      `p0/tests/test_p0.py`
- [x] T007 [P] [US1] Test: `Ruleset.sha256()` is stable and reproducible over an assembled compiled
      batch (spec.md US1 Scenario 2), in `p0/tests/test_p0.py`

### Implementation for User Story 1

- [x] T008 [US1] Implement `CompiledCheckDraft` dataclass in `p0/qc_engine/compiler/compile_llm.py`
      per data-model.md §1 (`row_id`, `check`, `source_text`, `extracted_intent`,
      `proposed_field_entry`, `parse_error`) (depends on T005)
- [x] T009 [US1] Implement the map step: generalize `p0/experiment_002a/compile_llm.py`'s proven
      Bedrock harness (Sonnet 4.6, temperature=0, the existing `SYSTEM_PROMPT` pattern, one row per
      call — research.md Decision 1) into a reusable per-row compile function producing
      `CompiledCheckDraft` (depends on T008)
- [x] T010 [US1] Implement batch assembly: a list of `CompiledCheckDraft.check` + per-draft
      `RuleProvenance` into a `Ruleset`, reusing `Ruleset`/`RuleProvenance` unmodified (depends on
      T009, T004)

**Checkpoint**: US1 fully functional and independently testable — a real batch compiles and hashes.

---

## Phase 4: Cross-cutting — Duplicate-vocabulary consistency report (FR-003, no dedicated User Story)

**Goal**: Detect two or more drafted checks that reference the same underlying concept under
different `field_name`s — advisory, does not block sign-off (spec.md Edge Cases).

- [x] T011 [P] Test: a synthetic batch containing two checks referencing the same concept under
      different field names is caught by the consistency report 100% of the time (SC-002), in
      `p0/tests/test_p0.py`
- [x] T012 Implement `ConsistencyReport`/`DuplicateVocabularyFlag` in
      `p0/qc_engine/compiler/consistency.py`, reusing `ruleset.py`'s existing `_edit_distance`
      helper for fuzzy field-name clustering — **no new dependency** (research.md Decision 3),
      per data-model.md §3 (depends on T010)

**Checkpoint**: US1 + consistency reporting functional.

---

## Phase 5: User Story 2 — Zero-edit sign-off is surfaced loudly, never passed as a quiet win (Priority: P1)

**Goal**: Extend the existing `unedited_rules()`/`signoff_summary()` sign-off-theater mechanism to
report correctly at batch scale (dozens-to-hundreds of checks), per constitution Principle II.

**Independent Test**: Sign a batch with zero edits; confirm the flag fires. Sign the same batch with
a realistic edit-distance distribution; confirm it does not.

### Tests for User Story 2 ⚠️

- [x] T013 [P] [US2] Test: signing a batch with zero edits across every rule triggers the sign-off-
      theater flag (spec.md US2 Scenario 1, SC-004), in `p0/tests/test_p0.py`
- [x] T014 [P] [US2] Test: signing the same batch with a realistic non-zero edit-distance
      distribution does **not** trigger the flag (spec.md US2 Scenario 2, SC-004), in
      `p0/tests/test_p0.py`

### Implementation for User Story 2

- [x] T015 [US2] Confirm `Ruleset.unedited_rules()`/`signoff_summary()` (existing, **unmodified**)
      operate correctly over a batch-scale `provenance` list (dozens-to-hundreds of entries) —
      verification, not new code, since both methods already iterate `self.provenance` generically
      (plan.md data-model.md §6) (depends on T010)

**Checkpoint**: US1 + US2 + consistency reporting functional.

---

## Phase 6: User Story 3 — No compiled check can be signed with an unresolved field reference (Priority: P1)

**Goal**: Move `001a`'s referential-integrity SAFE gate earlier — into the compile pipeline, before
a drafted rule is eligible for SME sign-off at all — without modifying the existing validator.

**Independent Test**: Compile a batch where the LLM drafts a check against a field name not present
in the `001a` catalog and with no inferable proposal; confirm the pipeline blocks that check from
being marked sign-off-ready.

### Tests for User Story 3 ⚠️

- [x] T016 [P] [US3] Test: a drafted check whose `field_name` doesn't resolve and carries no
      `proposed_field_entry` is blocked from sign-off, naming the check and missing field (spec.md
      US3 Scenario 1), in `p0/tests/test_p0.py`
- [x] T017 [P] [US3] Test: a drafted check whose `field_name` does resolve proceeds to the sign-off
      stage normally (spec.md US3 Scenario 2), in `p0/tests/test_p0.py`
- [x] T018 [P] [US3] Test: SC-001 combined — a batch of N > 24 rows, where every draft is correctly
      resolved / signable-pending-catalog-entry / blocked by the referential-integrity screen before
      any sign-off eligibility is granted, in `p0/tests/test_p0.py`

### Implementation for User Story 3

- [x] T019 [US3] Implement `screen_batch_referential_integrity()` in
      `p0/qc_engine/compiler/catalog_screen.py` — wraps `catalog.validate_referential_integrity`
      once per candidate check via a throwaway single-check `Ruleset`, the existing validator
      **completely unmodified** (research.md Decision 4; see Scoping finding above) (depends on
      T010)
- [x] T020 [US3] Implement propose-then-sign catalog growth (research.md Decision 2): when a
      `field_name` doesn't resolve, draft a candidate `FieldCatalogEntry` (inferring `data_type`/
      `expected_sources` from the source row) as `CompiledCheckDraft.proposed_field_entry`,
      distinguishing `signable_pending_catalog_entry` from `blocked` in the batch report shape
      (data-model.md §5) (depends on T019)

**Checkpoint**: US1 + US2 + US3 + consistency reporting functional.

---

## Phase 7: User Story 4 — The two `002a`-found patterns are caught automatically at scale (Priority: P2)

**Goal**: Automatically flag the two concrete failure patterns `002a`'s self-review found by hand
(opaque pre-computed boolean; misclassified reconcile check) — a batch can't quietly slip past these
the way a 24-row hand review could.

**Independent Test**: Feed the compiler a synthetic `predicate-08`-shaped row and a
`reconcile-00`/`01`-shaped row; confirm both are flagged for human attention, never silently
compiled and passed through.

### Tests for User Story 4 ⚠️

- [x] T021 [P] [US4] Test: a synthetic `predicate`-kind row describing a two-value comparison (the
      `predicate-08` pattern) is flagged `opaque_boolean_risk` (spec.md US4 Scenario 1, SC-003), in
      `p0/tests/test_p0.py`
- [x] T022 [P] [US4] Test: a synthetic `agree_categorical`/`agree_numeric`-kind row whose text
      doesn't describe a genuine two-independent-source comparison (the `reconcile-00`/`01` pattern)
      is flagged `archetype_mismatch_risk` (spec.md US4 Scenario 2, SC-003), in
      `p0/tests/test_p0.py`

### Implementation for User Story 4

- [x] T023 [P] [US4] Implement `pattern_flags.py`'s `opaque_boolean_risk` heuristic (FR-007) — a
      deterministic regex/keyword match over `source_text` for `predicate`-kind checks (same style
      as `eval_synth/taxonomy.py`'s `ARCHETYPES` matching; **not** a second LLM call), per
      data-model.md §4 (depends on T010)
- [x] T024 [P] [US4] Implement `pattern_flags.py`'s `archetype_mismatch_risk` heuristic (FR-008) —
      a deterministic regex/keyword match over `source_text` for `agree_categorical`/
      `agree_numeric`-kind checks, per data-model.md §4 (depends on T010)

**Checkpoint**: US1 + US2 + US3 + US4 + consistency reporting functional.

---

## Phase 8: User Story 5 — The extracted intent is permanently registered, not discarded (Priority: P1)

**Goal**: Retain the source rule/guidance text, the LLM's extracted intent, and the deterministic
logic together as one auditable, retrievable triple for the life of the signed artifact.

**Independent Test**: Take a signed `Check` from a compiled `Ruleset`; confirm its source text and
extracted intent can both be retrieved alongside the deterministic logic.

### Tests for User Story 5 ⚠️

- [x] T025 [P] [US5] Test: for every `Check` in a signed `Ruleset`, `source_text` + `extracted_intent`
      + the deterministic logic are all retrievable together via `Ruleset.intent_for()` (spec.md US5
      Scenario 1, SC-006 — 0 checks missing any of the three), in `p0/tests/test_p0.py`
- [x] T026 [P] [US5] Test: `qc_engine.engine.run` evaluating a compiled `Ruleset` makes zero LLM/
      network calls — confirmed by running with AWS credentials removed from the environment and
      observing no failure (spec.md US5 Scenario 2, SC-005), in `p0/tests/test_p0.py`

### Implementation for User Story 5

- [x] T027 [US5] Wire the map step (T009) to populate a `RuleIntentRecord` per compiled check, and
      wire batch assembly (T010) to attach it into `Ruleset.intent_records` (depends on T004, T009,
      T010)

**Checkpoint**: All five user stories + cross-cutting consistency reporting independently
functional.

---

## Final Phase: Polish & Cross-Cutting

- [x] T028 Implement `report.py`: assemble `contracts/batch-report-schema.md`'s shape from the map
      step (T009), the consistency report (T012), the pattern flags (T023, T024), and the
      referential-integrity screen (T019, T020) into one SME-reviewable batch report (depends on
      T012, T019, T020, T023, T024)
- [x] T029 [P] Run `quickstart.md`'s full 7-step sequence end-to-end against a real N > 24 batch
      (depends on all implementation tasks above)
- [x] T030 Run the full zero-regression suite (`p0/harness.py`'s 1000-run determinism digest,
      `p0/tests/test_p0.py`, `p0/eval_synth` property tests) and confirm the recorded baseline
      digest (`8510a0a8b4b6996e047fc8534e094394ba72aae396305b0d2ecad3d6924634db`) and the `001a`
      field-catalog hash are unchanged — this feature is purely additive (depends on T029)
- [x] T031 Capture implementation notes in `plan.md` (mirroring `001a`/`001b`'s pattern) — what was
      actually built vs. planned, any amendments found during implementation

---

## Dependencies & Execution Order

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup — **blocks US1 and US5** (both need the extended
  `Ruleset` shape); T005 also gates US1 (needs a real-row sampler).
- **US1 (P1)**: Depends on Foundational. This is the mechanism itself — everything else in this
  feature operates on its output (`Ruleset` from T010).
- **Cross-cutting consistency (FR-003)**: Depends on US1 (T010) — no dedicated User Story, but
  gates nothing else; can run any time after T010.
- **US2 (P1)**: Depends on US1 (T010) only — `unedited_rules()`/`signoff_summary()` already exist
  and are verified, not built.
- **US3 (P1)**: Depends on US1 (T010) only — independent of US2, US4.
- **US4 (P2)**: Depends on US1 (T010) only — independent of US2, US3, US5; lowest priority, can
  slip if time-constrained without blocking the P1 stories.
- **US5 (P1)**: Depends on Foundational (T004, for `intent_records`) and US1 (T009, T010).
- **Polish**: T028 depends on the cross-cutting report + US3 + US4 outputs existing; T030 (zero-
  regression) should run last, after every user story's changes are in, to prove the whole feature
  is additive-only.

### Parallel opportunities

- T006/T007 (US1 tests), T013/T014 (US2 tests), T016/T017/T018 (US3 tests), T021/T022 (US4 tests),
  T025/T026 (US5 tests), T011 (consistency test) — all independent test-writing, can run in parallel
  across stories once Foundational is done.
- T023 and T024 (US4's two heuristics) are fully parallel to each other.
- US2, US3, and US4's *implementation* tasks (T015; T019-T020; T023-T024) are mutually independent
  once T010 exists — three separate engineers/agents could take one story each with no shared-file
  conflicts (each lives in its own new module under `compiler/`).

## Implementation Strategy

**MVP = US1 + US2 + US3 + US5** (the four P1 stories) — these are what make a real batch both
compileable *and* safe to sign at all (US3's hard block), with the sign-off-integrity signal
(US2) and the audit-trail requirement (US5) that make the compiled artifact trustworthy, not just
functional. **US4 (P2) is additive quality-assurance on top of the mechanism** — the direct,
concrete legacy of what `002a`'s self-review found by hand, valuable but not load-bearing for the
core compile→screen→sign loop to work. The cross-cutting consistency report (FR-003) is cheap
(reuses an existing helper) and can land alongside US1 with little marginal cost.
