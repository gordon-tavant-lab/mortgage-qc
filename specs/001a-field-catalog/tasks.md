# Tasks: Field Catalog

**Input**: Design documents from `specs/001a-field-catalog/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/field-catalog-schema.md

**Tests**: Included — this project's constitution makes eval/regression-proof foundational
(Principle III) and spec.md's SC-002 is explicitly a zero-regression test gate, not optional polish.

**Organization**: Tasks grouped by user story (spec.md P1/P2/P3), per the constitution's rule that
each slice ships with its own proof, not a single undifferentiated build.

## Phase 1: Setup

- [x] T001 Create `p0/qc_engine/catalog.py` module skeleton (imports, module docstring per the
      existing `ruleset.py`/`model.py` style)
- [x] T002 [P] Create seed `p0/qc_engine/field_catalog.json` (empty `entries: []`, valid per
      `contracts/field-catalog-schema.md`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**⚠️ CRITICAL**: All three user stories need the catalog structure + hashing to exist first.

- [x] T003 Implement `FieldCatalogEntry` dataclass (`field_name`, `data_type`, `enum_values`,
      `expected_sources`, `citation_required`, `confidence_required`, `description`) in
      `p0/qc_engine/catalog.py`, per `data-model.md`
- [x] T004 Implement `FieldCatalog` dataclass (`catalog_id`, `version`, `entries`,
      `engine_version`) with `canonical_content()`/`sha256()` mirroring
      `p0/qc_engine/ruleset.py`'s `Ruleset` pattern exactly, in `p0/qc_engine/catalog.py`
      (depends on T003)
- [x] T005 Implement catalog load/parse in `p0/qc_engine/catalog.py`: reject a malformed file
      entirely (duplicate `field_name`, unparseable JSON, an `enum` entry missing `enum_values`) —
      never partially load (FR-009) (depends on T003)
- [x] T006 Export `FieldCatalog`, `FieldCatalogEntry`, catalog-loading function from
      `p0/qc_engine/__init__.py` (depends on T004, T005)
- [x] T007 [P] Seed `p0/qc_engine/field_catalog.json` with entries for the 7 fields the existing
      P0 demo ruleset actually references by `field_name` (`note_signed`, `note_rate`,
      `property_address`, `borrower_ssn`, `loan_amount`, `borrower_name`, `flood_zone`) so later
      regression tests have real data to validate against. **Amendment during implementation**:
      `property_value` is dropped from this list — it's only ever read via `loan.facts` (the
      `ratio_threshold`/LTV mechanism), never through a `field_name`-based `Check`, so it isn't
      part of 001a's declared scope (see data-model.md's facts-vs-fields boundary). Cataloging it
      would have sat as a permanently "unused" entry misrepresenting what this feature governs.
      (depends on T005)

**Checkpoint**: Foundation ready — user story work can begin.

---

## Phase 3: User Story 1 — Referential Integrity (Priority: P1) 🎯 MVP

**Goal**: A check can never silently reference a field that doesn't exist (spec.md US1).

**Independent Test**: Author a check with a typo'd `field_name`; confirm validation rejects it
before any loan is scored.

### Tests for User Story 1 ⚠️ (write first, confirm FAIL before implementation)

- [x] T008 [P] [US1] Test: a check referencing an unresolved `field_name` fails validation
      loudly, naming the check and the field, in `p0/tests/test_p0.py`
- [x] T009 [P] [US1] Test: a check referencing an existing catalog entry passes validation, in
      `p0/tests/test_p0.py`
- [x] T010 [P] [US1] Test: renaming/removing a catalog entry causes an existing check's
      validation to fail loudly on the next run (spec.md Edge Case), in `p0/tests/test_p0.py`

### Implementation for User Story 1

- [x] T011 [US1] Implement `validate_referential_integrity(ruleset, catalog)` in
      `p0/qc_engine/catalog.py` — raises immediately, naming both the offending check and the
      missing field (FR-003, FR-004) (depends on T004)
- [x] T012 [US1] Wire `validate_referential_integrity` into `p0/harness.py`'s existing pre-run
      validation step, alongside the current sign-off-integrity check — load-time, once, not
      per-check (research.md decision #2) (depends on T011)

**Checkpoint**: US1 fully functional and independently testable.

---

## Phase 4: User Story 2 — Add a Field, Zero Code Change (Priority: P2)

**Goal**: Adding a field is an authoring act, not a code change (spec.md US2).

**Independent Test**: Add a synthetic field to `field_catalog.json` only; author and validate a
check against it with no `p0/qc_engine/*.py` diff.

### Tests for User Story 2 ⚠️

- [x] T013 [P] [US2] Test: adding a synthetic field via `field_catalog.json` alone (no code
      change) lets a new check reference and validate against it, in `p0/tests/test_p0.py`

### Implementation for User Story 2

- [x] T014 [US2] Run the full existing P0 golden-set suite (`p0/harness.py`) and
      `p0/eval_synth` property tests through the catalog-validated path; confirm zero regression
      (SC-002) (depends on T012)
- [x] T015 [US2] Implement the unused-catalog-entry report (FR-008) in `p0/qc_engine/catalog.py`
      — entries with zero referencing checks are listed, not rejected (depends on T011)

**Checkpoint**: US1 + US2 both independently functional.

---

## Phase 5: User Story 3 — Signed, Hashed Authored Artifact (Priority: P3)

**Goal**: The catalog is a signed artifact an SME can review, even before the authoring UI exists
(spec.md US3).

**Independent Test**: Hash an unchanged catalog file twice — identical digest; change one entry —
digest changes.

### Tests for User Story 3 ⚠️

- [x] T016 [P] [US3] Test: hashing an unchanged `field_catalog.json` twice yields an identical
      SHA-256 digest, in `p0/tests/test_p0.py`
- [x] T017 [P] [US3] Test: changing one entry's `data_type` changes the resulting hash, in
      `p0/tests/test_p0.py`

### Implementation for User Story 3

*(No new implementation — `FieldCatalog.sha256()` from T004 already covers this; this phase is
proof that the foundational hashing work satisfies US3's acceptance scenarios.)*

**Checkpoint**: All three user stories independently functional.

---

## Final Phase: Polish & Cross-Cutting

- [x] T018 [P] Run `quickstart.md`'s full validation sequence end-to-end
- [x] T019 Docs agent: capture an ADR noting the catalog generalization (continuous documentation
      per `output/ROADMAP.md`'s Authored Configuration Model section) — captured as an
      "Implementation Notes" section in `plan.md` rather than a new `docs/adr/` directory, since no
      prior ADR-directory convention existed in this project

---

## Dependencies & Execution Order

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup — **blocks all user stories**.
- **US1 (P1)**: Depends on Foundational only. Start here — it's the safety-critical MVP.
- **US2 (P2)**: Depends on Foundational + US1's `validate_referential_integrity` (T011) for the
  unused-entry report (T015); the "zero code change" proof (T013/T014) only needs Foundational.
- **US3 (P3)**: Depends on Foundational only (T004's hashing) — genuinely independent of US1/US2,
  could run in parallel with either.
- **Polish**: Depends on US1 + US2 + US3 complete.

### Parallel opportunities

- T001/T002 (Setup) in parallel.
- T008/T009/T010 (US1 tests) in parallel with each other.
- T013 (US2 test) can start as soon as Foundational is done — doesn't need US1 complete.
- T016/T017 (US3 tests) can run any time after T004 — fully parallel to US1/US2 work.

## Implementation Strategy

**MVP = US1 only** (referential integrity) — this is the safety-critical reason the feature
exists; ship it and validate before layering US2/US3. US2 and US3 are provable independently and
can follow in either order once Foundational + US1 are green.
