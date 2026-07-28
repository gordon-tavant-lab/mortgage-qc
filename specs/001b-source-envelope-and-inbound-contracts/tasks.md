# Tasks: Source Envelope and Inbound Contracts

**Input**: Design documents from `specs/001b-source-envelope-and-inbound-contracts/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/inbound-contracts.md

**Tests**: Included — SC-001/FR-009 zero-regression is a hard gate (Principle I/III), not optional. *(Corrected 2026-07-26: originally cited "SC-009", which doesn't exist — spec defines SC-001..SC-005; the zero-regression requirement is FR-009.)*

**Organization**: Tasks grouped by user story (spec.md P1/P1/P2).

**Scoping finding (from grep, before writing this file)**: `.doc`, `.los`, `.mismo` are read **and
written** post-construction in `p0/eval_synth/generator.py` and `test_properties.py` (mutation-based
fixture builders — e.g. `sv.los = str(sv.doc) + " UNIT 9"`). The backward-compatible shim (T004) must
therefore be **read-write** properties, not read-only — confirmed before implementation, not assumed.

## Phase 1: Setup

- [x] T001 Grep all read/write sites of `SourceValue.doc`/`.los`/`.mismo` across
      `p0/qc_engine/`, `p0/eval_synth/`, `p0/tests/`, `p0/fixtures/` to produce the definitive
      call-site list this migration must not break (already partially done — see scoping finding
      above; this task formalizes it as a checklist before touching `model.py`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**⚠️ CRITICAL**: All three user stories depend on the generalized envelope existing first.

- [x] T002 Generalize `SourceValue` in `p0/qc_engine/model.py`: add `truth: Optional[Any]`,
      `sources: Dict[str, Any]`, `source_priority: List[str]` (default `["los", "mismo"]`) fields.
      Provide a backward-compatible constructor accepting `doc`/`los`/`mismo` kwargs (in addition to
      `truth`/`sources`), mapping `doc`→`truth`, `los`→`sources["los"]`, `mismo`→`sources["mismo"]`
      (depends on T001)
- [x] T003 Generalize `system_value()` in `p0/qc_engine/model.py` into a priority-ordered lookup over
      `sources` using `source_priority` — must preserve today's exact LOS-else-MISMO fallback
      behavior bit-for-bit (depends on T002)
- [x] T004 Add **read-write** `doc`, `los`, `mismo` properties on `SourceValue` (getters delegate to
      `truth`/`sources`; setters write into `truth`/`sources`) so every existing call site — including
      the mutation-based fixture builders found in T001 — continues to work with zero changes
      (depends on T002, T003)
- [x] T005 [P] Extend `FieldCatalogEntry` (`p0/qc_engine/catalog.py`, from `001a`) with an optional
      `source_priority` field, defaulting to `None` (falls back to `SourceValue`'s
      `["los", "mismo"]` default) — depends on `001a` being in place (it is), independent of T002-T004

**Checkpoint**: Foundation ready — user story work can begin.

---

## Phase 3: User Story 1 — Source Independence Guard (Priority: P1) 🎯 MVP

**Goal**: Reconcile checks compare genuinely independent sources, never the same data twice.

**Independent Test**: A fixture that derives `sources.los` from `truth` is rejected before scoring.

### Tests for User Story 1 ⚠️ (write first, confirm FAIL before implementation)

- [x] T006 [P] [US1] Test: a reconcile check comparing `truth` against an independently-populated
      `sources.los` runs correctly (spec.md US1 Scenario 1), in `p0/tests/test_p0.py`
- [x] T007 [P] [US1] Test: `assert_independently_constructed(...)` rejects a fixture where
      `sources.los` is derived from `truth` (spec.md US1 Scenario 2, FR-005), in
      `p0/tests/test_p0.py`
- [x] T008 [P] [US1] Test: a MISMO-only loan (no `los` entry in `sources`) still resolves
      `system_value()` identically to today's fallback (spec.md US1 Scenario 3, SC-005), in
      `p0/tests/test_p0.py`

### Implementation for User Story 1

- [x] T009 [US1] Implement `assert_independently_constructed(truth_value, sources_dict,
      construction_trace)` in `p0/eval_synth/generator.py` per `data-model.md` — the
      test-construction discipline (research.md decision #2), not a runtime data validator
      (depends on T002-T004)
- [x] T010 [US1] Apply `assert_independently_constructed` to the existing reconcile mutation
      operators (`mut_mismatch_categorical`, `mut_mismatch_numeric`, `mut_inaccurate`) in
      `p0/eval_synth/generator.py` (depends on T009)

**Checkpoint**: US1 fully functional and independently testable.

---

## Phase 4: User Story 2 — Add a Source, Zero Code Change (Priority: P1)

**Goal**: A new named source (e.g. a settlement-agent feed) is addable via data only.

**Independent Test**: Add `sources["settlement_agent"]` to a test loan; an existing check reads it
with zero `p0/qc_engine/*.py` diff, and the full regression suite stays byte-identical.

### Tests for User Story 2 ⚠️

- [x] T011 [P] [US2] Test: adding a synthetic `"settlement_agent"` entry to a test loan's `sources`
      map is readable via `system_value()`-style access with zero `p0/qc_engine/*.py` changes
      (spec.md US2, SC-002), in `p0/tests/test_p0.py`
- [x] T012 [P] [US2] Test: the full P0 golden-set suite (`p0/harness.py`, 1000-run) and
      `p0/eval_synth` property tests produce byte-identical results pre/post migration (SC-001), in
      `p0/tests/test_p0.py`

### Implementation for User Story 2

- [x] T013 [US2] Confirm `p0/qc_engine/engine.py`'s `_eval_check` requires **zero changes** — it
      already reads only `sv.doc` / `sv.system_value()`, both preserved by T004's backward-compat
      properties (depends on T002-T004; this task is verification, not new code, per plan.md's
      Structure Decision)
- [x] T014 [US2] Confirm `p0/qc_engine/reconcile.py` requires **zero changes** for the same reason
      (depends on T002-T004; verification, not new code)
- [x] T015 [US2] Run `p0/harness.py` (1000-run determinism) + `p0/tests/test_p0.py` (full suite) +
      `p0/eval_synth` property tests; confirm the determinism digest is byte-identical to the
      pre-migration baseline (`8510a0a8b4b6996e047fc8534e094394ba72aae396305b0d2ecad3d6924634db`,
      recorded in `001a`'s `plan.md`) (depends on T009, T010, T013, T014)

**Checkpoint**: US1 + US2 functional, zero regression proven against the recorded baseline digest.

---

## Phase 5: User Story 3 — Inbound Contracts Pinned (Priority: P2)

**Goal**: Touchless and LOS/MISMO inbound contracts are reviewable schemas, not prose.

*(No new implementation — `contracts/inbound-contracts.md` was already produced during planning.
This phase verifies it, rather than building anything new.)*

- [x] T016 [P] [US3] Verify `contracts/inbound-contracts.md` maps every `001a` `FieldCatalogEntry`'s
      `expected_sources` to a contract clause (SC-004) — closes `FOUNDATION-READINESS.md` GAP 1 for
      this feature's scope.

**Checkpoint**: All three user stories independently functional.

---

## Final Phase: Polish & Cross-Cutting

- [x] T017 [P] Run `quickstart.md`'s full validation sequence end-to-end (add-a-source workflow,
      independence-test discipline, MISMO-only-loan case)
- [x] T018 Capture implementation notes in `plan.md` (mirroring `001a`'s pattern) — what was actually
      built vs. planned, any amendments found during implementation

---

## Dependencies & Execution Order

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup — **blocks all user stories**. T005 is independent of
  T002-T004 (only needs `001a`, already in place).
- **US1 (P1)**: Depends on Foundational only. Start here alongside US2 — both are P1 and safety/
  scaling-critical.
- **US2 (P1)**: Depends on Foundational only; T015's full regression run should happen last (after
  US1's fixture changes) to prove zero regression across everything, not just US2's own changes.
- **US3 (P2)**: Depends on nothing new — verification of an already-produced planning artifact; can
  run any time.

### Parallel opportunities

- T006/T007/T008 (US1 tests) in parallel with each other, and with T011/T012 (US2 tests) — different
  test cases, no shared state.
- T005 (catalog extension) fully parallel to T002-T004 (model.py generalization).
- T016 (US3 verification) has no code dependency — can run any time, in parallel with everything.

## Implementation Strategy

**MVP = US1 + US2 together** (both P1, both required for the zero-regression proof to mean anything —
US1 without US2 would prove independence but not scaling; US2 without US1 would prove scaling but not
the safety property the whole envelope generalization exists for). US3 (P2, contract verification) can
land any time before or after.
