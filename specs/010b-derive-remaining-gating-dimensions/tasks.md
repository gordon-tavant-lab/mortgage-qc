# Tasks: Derive the Remaining Gating Dimensions (Occupancy + Loan Program)

**Input**: Design documents from `specs/010b-derive-remaining-gating-dimensions/`
**Prerequisites**: plan.md, spec.md

**Tests**: Included — this project's constitution makes eval/regression-proof foundational
(Principle III); SC-001–005 are the correctness/safety proof this feature exists to produce.

**Organization**: Tasks grouped by user story (spec.md P1/P2). Tests are written to fail first (red),
confirming they exercise real new behavior, per the TDD discipline `002b`/`002e`/`010a` all established.

## Phase 1: Setup

- [ ] T001 Create `p0/qc_engine/build_loan_profiles_v3.py` module skeleton (module docstring per
      `build_loan_profiles_v2.py`'s existing style; imports v2's 3 existing derivations unchanged) —
      no new derivation logic yet
      → Done when: the module imports cleanly with zero errors
- [ ] T002 Create `p0/qc_engine/apply_loan_profile.py` module skeleton (module docstring naming this
      as the promotion of `run_013`'s one-off `_panel_from_v2_profiles()` pattern, spec.md Gap 2) —
      no logic yet
      → Done when: the module imports cleanly with zero errors
- [ ] T003 [P] Create `p0/tests/test_loan_profiles_v3.py` module skeleton — no test bodies yet
      → Done when: `python -m pytest p0/tests/test_loan_profiles_v3.py --collect-only` exits 0 with
      zero tests collected
- [ ] T004 [P] Create `p0/tests/test_occupancy_applicability_gating.py` module skeleton — no test
      bodies yet
      → Done when: `python -m pytest p0/tests/test_occupancy_applicability_gating.py --collect-only`
      exits 0 with zero tests collected

---

## Phase 2: Foundational — the fact vocabulary + field catalog (blocking prerequisite)

**Purpose**: The 2 new facts must exist as signed vocabulary + resolvable catalog entries before either
derivation or the `applies_if` gate can be built against them.

**CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T005 Author `storage/fact_vocabulary/v7.json`: copy v6's 16 facts unchanged, add
      `occupancy_type` (enum: `owner_occupied`/`second_home`/`investment`; `source_citations`: the
      `pc-retail-0283{7,8,9}`/`02840`/`02841` "owner occupancy" row family, confirmed by direct read of
      `p0/fixtures/ontology_extraction/retail_post_closing_rows.json`) and `loan_program` (enum:
      `Conventional`/`FHA`/`VA`/`USDA`/`Freddie Mac`/`Fannie Mae`/`SONYMA` — `program_gating.py`'s
      existing `_PREFIX_TO_PROGRAM` token set, reused verbatim; `source_citations`: the Exception Code
      prefix family `010a` already established at scale). Sign with
      `signed_by="NOT-A-REAL-SME-pending-kayla-review"`, matching every prior version (FR-001).
- [ ] T006 [P] Add `occupancy_type` entry to `p0/qc_engine/field_catalog.json` (`data_type: "enum"`,
      `enum_values: ["owner_occupied", "second_home", "investment"]`, `citation_required: false`,
      `confidence_required: false`, `expected_sources: ["doc"]`) (FR-005)
- [ ] T007 [P] Add `loan_program` entry to `p0/qc_engine/field_catalog.json` (`data_type: "enum"`,
      `enum_values: ["Conventional", "FHA", "VA", "USDA", "Freddie Mac", "Fannie Mae", "SONYMA"]`,
      `citation_required: false`, `confidence_required: false`, `expected_sources: ["doc"]`) (FR-005)
- [ ] T008 Test: `FieldCatalog` loaded from `field_catalog.json` resolves both new field names via
      `catalog.get()`; a tiny `Ruleset` with a `Check` whose `applies_if` references `occupancy_type`
      passes `validate_referential_integrity()` without raising (SC-004), in
      `p0/tests/test_occupancy_applicability_gating.py`

**Checkpoint**: Both new facts are signed vocabulary entries and resolvable catalog entries. User story
work can now begin.

---

## Phase 3: User Story 1 — Occupancy is derived once, centrally, from the 1003 (Priority: P1) MVP

**Goal**: `derive_occupancy_type` correctly maps known 1003 occupancy text to the canonical token, and
honestly reports `underivable` otherwise.

**Independent Test**: Run the derivation against all 5 real fixtures; confirm 5/5 resolve
`owner_occupied` with a real, cited `derived_from`.

### Tests for User Story 1 (write first, confirm they FAIL before implementation)

- [ ] T009 [P] [US1] Test: `derive_occupancy_type` against loan_02's real fixture
      (`occupancy_1003 = "Primary Residence (First-Time Homebuyer)"`) resolves
      `derived_facts.occupancy_type.value == "owner_occupied"`, `derived_from` names the source field
      and literal text; confirm red (function doesn't exist yet), in
      `p0/tests/test_loan_profiles_v3.py`
- [ ] T010 [P] [US1] Test: same assertion for loan_01/03/04/05's real `occupancy_1003` variants — all
      5 resolve `owner_occupied` (spec.md Acceptance Scenario 1, SC-001); confirm red
- [ ] T011 [P] [US1] Test: a constructed `CanonicalLoan` with `occupancy_1003 = "Investment Property"`
      resolves `"investment"` (Acceptance Scenario 2 — the real ULAD/URLA token, untested against a
      real fixture per spec.md Edge Cases, disclosed as such in this test's own docstring); confirm red
- [ ] T012 [P] [US1] Test: a constructed `CanonicalLoan` with `occupancy_1003 = "Second Home"` resolves
      `"second_home"`; confirm red
- [ ] T013 [P] [US1] Test: a constructed `CanonicalLoan` with an unrecognized `occupancy_1003` value
      (e.g. `"Occupied by Relative"`) resolves `underivable`, never a guessed default (Acceptance
      Scenario 3); confirm red — this one may already pass trivially depending on the default
      implementation, included as the baseline safety case

### Implementation for User Story 1

- [ ] T014 [US1] In `build_loan_profiles_v3.py`, implement the literal `OCCUPANCY_MAP` (enumerated
      text variants only, matching `derive_loan_transaction_type`'s existing
      `LOAN_PURPOSE_MAP` discipline — never fuzzy/substring matching) and
      `derive_occupancy_type(loan) -> Dict[str, Any]` (depends on T009–T013 existing as tests)
- [ ] T015 [US1] Run T009–T013 again; confirm all green
- [ ] T016 [US1] Regenerate `storage/loan_profiles/v3/loan_0{1..5}.json` by running
      `build_loan_profiles_v3.py`'s `build_all_profiles()`; confirm all 5 carry
      `derived_facts.occupancy_type.value == "owner_occupied"` (SC-001)

**Checkpoint**: Occupancy is derivable and citable for all 5 real loans. Independently valuable — does
not require US2/US3 to be true.

---

## Phase 4: User Story 2 — A real, already-compiled check gates on occupancy (Priority: P1)

**Goal**: The real compiled check `insurance-docs-support-owner-occupancy` resolves `NOT_APPLICABLE`
on a non-owner-occupied loan, and evaluates normally on an owner-occupied one — proving the derived
fact is load-bearing, not computed-and-ignored.

**Independent Test**: Build the real check's `Check` object with the new `applies_if`; evaluate against
loan_02 (real, owner-occupied) and a constructed investment-property loan.

### Tests for User Story 2

- [ ] T017 [P] [US2] Test: load `insurance-docs-support-owner-occupancy` from
      `result/rules/post_closing_only_ruleset.json` (pre-T023 state — no `applies_if` yet); confirm its
      current `applies_if` is `None` — documents the "before" state this feature changes, in
      `p0/tests/test_occupancy_applicability_gating.py`
- [ ] T018 [P] [US2] Test: `apply_loan_profile.apply_derived_facts(loan, profile)` writes
      `loan.fields["occupancy_type"] = SourceValue(doc="owner_occupied")` for loan_02's real fixture +
      its v3 profile, and does NOT overwrite `loan.fields["occupancy_1003"]` (FR-006's
      never-shadow-a-real-field guarantee, Edge Cases); confirm red (function doesn't exist yet)
- [ ] T019 [P] [US2] Test: same function, given a profile entry under `underivable` (not
      `derived_facts`) for some fact, writes NOTHING to `loan.fields` for that fact name; confirm red
- [ ] T020 [US2] Test: the real check (with `applies_if` set per FR-007, constructed in-test as a
      `Check(**{...real dict from ruleset.json, "applies_if": [...]})`) evaluated against loan_02's
      real fixture (post-wiring, `occupancy_type` present) evaluates its own `predicate: is_true` logic
      normally — same PASS/FAIL behavior as with no `applies_if` at all (Acceptance Scenario 1); confirm
      red until T023 attaches `applies_if` to the real artifact
- [ ] T021 [US2] Test: the same check evaluated against a constructed `CanonicalLoan` whose
      `occupancy_type` resolves `"investment"` resolves `NOT_APPLICABLE` (Acceptance Scenario 2, SC-002);
      confirm red
- [ ] T022 [US2] Test: the same check evaluated against a loan where `occupancy_type` was never wired
      (absent from `loan.fields`) resolves `NEEDS_REVIEW` with `review_reason == "APPLICABILITY_UNKNOWN"`
      (Acceptance Scenario 3 — `002e`'s existing FR-003 behavior, unmodified); confirm red until wiring
      exists to prove the *unwired* path still behaves correctly

### Implementation for User Story 2

- [ ] T023 [US2] In `p0/qc_engine/apply_loan_profile.py`, implement
      `apply_derived_facts(loan: CanonicalLoan, profile: Dict[str, Any]) -> CanonicalLoan` per FR-006 —
      promoting `run_013`'s `_panel_from_v2_profiles()` inline pattern (`SourceValue(doc=entry["value"])`,
      guarded by `fact_name not in loan.fields`) into tested, reusable code (depends on T018–T019)
- [ ] T024 [US2] Edit `result/rules/post_closing_only_ruleset.json`'s
      `insurance-docs-support-owner-occupancy` entry: add `"applies_if": [{"field_name":
      "occupancy_type", "operator": "==", "value": "owner_occupied"}]` (FR-007); confirm
      `applicability.json`'s existing `["Fannie Mae"]` entry for the same check id is untouched (FR-010)
- [ ] T025 [US2] Run T017, T020–T022 again; confirm all green

**Checkpoint**: A real, already-compiled check now gates on a derived loan fact end-to-end — the
concrete proof this feature exists to produce (spec.md Why This Feature Exists, Gap 2).

---

## Phase 5: User Story 3 — `loan_program` is derived where citable, honestly `underivable` where not (Priority: P2)

**Goal**: `derive_loan_program` resolves FHA/VA/USDA for loan_02/03/05 with citable `derived_from`, and
correctly, distinctly reports `underivable` for loan_01 (ambiguous Fannie/Freddie) and loan_04 (no
citable signal at all).

**Independent Test**: Run the derivation against all 5 real fixtures; confirm the 3-resolved/2-honest-
gaps split (spec.md table, Why This Feature Exists).

### Tests for User Story 3

- [ ] T026 [P] [US3] Test: `derive_loan_program` against loan_02's real fixture
      (`fha_case_number_1003` present) resolves `derived_facts.loan_program.value == "FHA"` with citable
      `derived_from`; confirm red, in `p0/tests/test_loan_profiles_v3.py`
- [ ] T027 [P] [US3] Test: same pattern for loan_03 (`va_lgy_case_number` → `"VA"`) and loan_05
      (`usda_gus_id` → `"USDA"`); confirm red
- [ ] T028 [US3] Test: `derive_loan_program` against loan_01's real fixture
      (`loan_type_cd == "Conventional"`, no GSE-specific citable field) resolves `underivable`, with a
      reason string naming the Fannie/Freddie ambiguity explicitly (Acceptance Scenario 2); confirm red
- [ ] T029 [US3] Test: `derive_loan_program` against loan_04's real fixture (no program-identifying
      field of any kind) resolves `underivable`, with a reason string distinguishable from loan_01's
      (Acceptance Scenario 3 — "no citable signal" vs. "signal found but ambiguous" must not be
      conflated); confirm red

### Implementation for User Story 3

- [ ] T030 [US3] In `build_loan_profiles_v3.py`, implement `derive_loan_program(loan) -> Dict[str, Any]`
      per FR-003 — the per-program presence-marker checks (`fha_case_number_1003`,
      `va_lgy_case_number`, `usda_gus_id`), the `loan_type_cd == "Conventional"`-but-ambiguous case, and
      the no-signal-at-all case, each with a distinct `underivable` reason string (depends on T026–T029)
- [ ] T031 [US3] Add `derive_occupancy_type` + `derive_loan_program` to `build_loan_profiles_v3.py`'s
      `DERIVATIONS` tuple, alongside v2's 3 reused derivations unchanged (FR-004)
- [ ] T032 [US3] Run T026–T029 again; confirm all green
- [ ] T033 [US3] Regenerate `storage/loan_profiles/v3/loan_0{1..5}.json` (final form, all 5
      derivations); confirm loan_02/03/05 carry `loan_program`, loan_01/04 carry it under
      `underivable` with the two distinct reasons (SC-003)

**Checkpoint**: All 5 real loans have a complete, honest v3 profile — 5/5 occupancy resolved, 3/5
loan_program resolved, 2/5 loan_program honestly `underivable`, matching spec.md's disclosed finding
exactly.

---

## Phase 6: Polish & Cross-Cutting

- [ ] T034 [P] Test (non-regression): `p0/tests/test_loan_profiles_v2.py`'s existing suite is
      untouched and still green — v3 does not modify v2's shipped artifacts or derivation functions
      (FR-004's "reuse unchanged" guarantee, proven, not just asserted)
- [ ] T035 [P] Test (non-regression): `p0/tests/test_conditional_applicability.py` and
      `p0/tests/test_program_applicability_gating.py`'s existing suites are untouched and still green —
      this feature adds a new `applies_if` consumer/producer pairing, it does not change either
      mechanism's existing behavior (FR-010)
- [ ] T036 Run the full existing suite unmodified: `python3 -m pytest p0/ -q` and `python3
      p0/harness.py`; confirm zero regression (SC-005) — the digest
      (`82175d076579e31a50971d8b20ea4b63848bea9f9b53c30dd96524071842e5ec`) must be unchanged, since this
      feature touches no `engine.py`/`model.py`/`ruleset.py` evaluation code
- [ ] T037 Add an "Implementation Notes" section to `plan.md` recording: final task count, total new
      test count, the exact `underivable` reason strings shipped for loan_01/loan_04's `loan_program`,
      and confirmation that `engine.py`/`model.py`/`ruleset.py`/`reconcile.py` were not touched

## Dependencies & Execution Order

- **T001–T004** (setup) block all of Phase 2.
- **Phase 2 (T005–T008)** blocks all user stories — both new facts must be signed vocabulary +
  resolvable catalog entries before any derivation or gating logic can reference them.
- **Phase 3 (US1, T009–T016)** is the MVP slice — independently valuable without US2/US3.
- **Phase 4 (US2, T017–T025)** depends on Phase 3's `derive_occupancy_type` existing (T014) to produce
  the `occupancy_type` value US2's wiring/gating tests consume; T023 (`apply_loan_profile.py`) is new,
  parallel-buildable code, but its tests (T018–T019) need Phase 3's real profile output to test against.
- **Phase 5 (US3, T026–T033)** is independent of Phase 4 (different fact, same module) — could run in
  parallel with Phase 4 once Phase 2 is done; sequenced after here only for narrative order.
- **T034–T037** run last, after all user stories are complete.

## Parallel Example

```
# T009–T013 (Phase 3, one occupancy-text case each) can run together once T001–T004/T005–T008 exist:
Task: "loan_02 real fixture resolves owner_occupied, red test"
Task: "loan_01/03/04/05 real fixtures resolve owner_occupied, red test"
Task: "constructed Investment Property loan resolves investment, red test"
Task: "constructed Second Home loan resolves second_home, red test"
Task: "unrecognized occupancy text resolves underivable, baseline case"

# T026–T029 (Phase 5, one loan_program case each) can run together once Phase 2 exists:
Task: "loan_02 FHA case-number signal resolves FHA, red test"
Task: "loan_03/loan_05 VA/USDA signals resolve VA/USDA, red test"
Task: "loan_01 Conventional-but-ambiguous resolves underivable (ambiguity reason), red test"
Task: "loan_04 no-signal-at-all resolves underivable (distinct reason), red test"
```
