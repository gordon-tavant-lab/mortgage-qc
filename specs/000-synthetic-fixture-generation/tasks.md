# Tasks: Synthetic Loan Fixture Generation (Document-Derived, Dev-Mode)

**Input**: Design documents from `specs/000-synthetic-fixture-generation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md, contracts/defect-verification-manifest.md

**Tests**: Included — this project's constitution makes eval/regression-proof foundational
(Principle III), and this feature's own acceptance gate (SC-001, FR-005/006) is explicitly required
to be executable, not just documented.

**Organization**: Tasks grouped by user story (spec.md P1/P1/P2/P3). The two P1 stories (US1 fixtures,
US2 defect gate) are technically dependent on catalog fields that spec.md frames as US3's (P2)
concern — this is resolved in Phase 2 (Foundational): the catalog is extended and grounded there
(unblocking US1/US2 immediately), and US3's own phase carries the *acceptance* proof (grounding
citations reviewed, referential-integrity/zero-regression validator run as this feature's own gate)
rather than re-doing the JSON authoring. See Dependencies & Execution Order.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Maps to spec.md's US1–US4. Setup/Foundational/Polish carry no story label.

---

## Phase 1: Setup

**Done when:**
- `p0/fixtures/from_docs/` exists with the structure plan.md specifies
- `p0/tests/test_fixture_generation.py` exists and collects (even with zero test bodies yet)
- The dev-only/not-Touchless disclaimer (Principle IV, FR-003) is in place before any extraction code is written

- [X] T001 Create the `p0/fixtures/from_docs/` subpackage directory structure (`doc_patterns/`
      subdirectory, empty `__init__.py` if needed to mirror `p0/eval_synth/`'s package style) and
      write `p0/fixtures/from_docs/README.md` stating plainly: this is dev/test fixture generation
      over the 5 synthetic loans in `demo/syn/`, it is **not** the Touchless production extractor, it
      makes no claim about real/non-synthetic document accuracy, and it does not implement the
      doc-vs-doc reconcile check-kind (only produces the two independently-cited fields for whoever
      specifies `003c`) — per plan.md's Project Structure and spec.md FR-003/FR-010, Edge Cases
      → Done when: `p0/fixtures/from_docs/README.md` exists and contains all three disclaimers
      (not-Touchless, no real-document accuracy claim, doc-vs-doc deferred to `003c`) in plain text
- [X] T002 [P] Create `p0/tests/test_fixture_generation.py` module skeleton — docstring describing
      its purpose (pytest coverage for `extract_pdf`/`extract_xml`/`build_fixtures`/
      `verify_against_defects`, per plan.md's Project Structure), imports from the not-yet-written
      `p0.fixtures.from_docs` modules wrapped so collection doesn't fail before those modules exist
      (e.g. import inside test functions, or `pytest.importorskip`), no test bodies yet
      → Done when: `python3 -m pytest p0/tests/test_fixture_generation.py --collect-only` exits 0
      with zero tests collected (skeleton present, nothing broken)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The catalog/manifest groundwork every user story needs. Both P1 stories (US1, US2)
structurally require the ~26 new catalog fields to exist before defect-bearing fields can be
extracted or verified — deferring this to US3's phase (as its P2 label alone would suggest) would
block both P1 stories. This phase does the authoring; US3's phase (below) carries the acceptance
proof that the authoring was properly grounded, not ad hoc.

**⚠️ CRITICAL**: No user-story work in Phase 3+ can begin until this phase is complete.

**Done when:**
- `defect_manifest.json` has exactly 25 entries, matching the 25 distinct planted defects (26 `<!-- DEFECT ... -->` XML comments on disk — loan 01's defect #4 is annotated twice, at the liabilities total and again in the credit-report section; corrected 2026-07-26, spec audit)
  across the 5 loans' MISMO exports, in `contracts/defect-verification-manifest.md`'s format
- Every `field_name`/`compare_field_name` referenced in the manifest resolves to a
  `field_catalog.json` entry
- `field_catalog.json` still passes `001a`'s existing referential-integrity and zero-regression tests
  after the additions
- `qc_engine/mismo.py` extracts every new field whose `expected_sources` includes `"mismo"`

- [X] T003 Read all 25 `<!-- DEFECT ... -->` comments from the 5 loans' MISMO XML files
      (`demo/syn/loan 01/09_Loan_Data_MISMO.xml`, `loan 02/09_...`, `loan 03/07_...`,
      `loan 04/07_...`, `loan 05/06_...`) and transcribe them into
      `p0/fixtures/from_docs/defect_manifest.json`, one entry per defect (25 total, 5 per loan),
      exactly per `contracts/defect-verification-manifest.md`'s JSON format (`loan_id`,
      `defect_number`, `description`, `field_name`, `compare_field_name` where the defect is
      doc-vs-doc per research.md decision #4, `expected_relationship` ∈
      `mismatch|missing|threshold_breach|stale`, `expected_values`, `source_document`) — assign a
      canonical `field_name` (and `compare_field_name` for the doc-vs-doc cases: loan01 defects #1,
      #2, #4; loan04 defects #1, #2) to every defect as part of this transcription
      → Done when: `p0/fixtures/from_docs/defect_manifest.json` is valid JSON with exactly 25 array
      entries, 5 per distinct `loan_id`, and every entry's `description` matches its source XML
      comment verbatim
- [X] T004 Add one `field_catalog.json` entry (per `001a`'s pinned schema in
      `specs/001a-field-catalog/contracts/field-catalog-schema.md` — no schema change) for every
      distinct `field_name`/`compare_field_name` in `defect_manifest.json` (T003) not already among
      the existing 7 seed fields — each new entry's `description` documents the exact
      `p0/eval_synth/taxonomy.json` archetype id + condition text that justifies it (data-model.md's
      `RuleGroundedCatalogEntry` convention, research.md decision #3), e.g. an entry grounded in the
      `MISMATCH` archetype's condition *"the manner in which title is held on the 1003 does not match
      the title commitment"*, or the `MISSING`/`UNSIGNED`/`THRESHOLD`/`EXPIRED` archetypes for the
      presence/ratio/staleness-flavored defects; set `expected_sources` to `["doc", "mismo"]` for
      genuine doc-vs-system fields (e.g. an FHA-case-number field whose system side is a portal
      lookup) and to `["doc"]` only for fields that are one side of a doc-vs-doc pair (research.md
      decision #4 — never force a second document value into `sources{}`) (depends on T003)
      → Done when: `field_catalog.json` is valid JSON, `field_name` remains unique across all
      entries, every `field_name`/`compare_field_name` from `defect_manifest.json` now resolves to an
      entry, and every new entry's `description` contains a taxonomy.json archetype id
- [X] T005 Run `001a`'s existing referential-integrity and zero-regression validator/tests against
      the extended `field_catalog.json` (T004) — the same validation `001a` already implemented,
      no shortcut for this feature (FR-009) (depends on T004)
      → Done when: the existing catalog validator reports zero referential-integrity violations and
      the existing engine test suite (`p0/tests/test_p0.py`,
      `p0/tests/test_predicate_archetypes.py`, `p0/tests/test_threshold_archetypes.py`) still passes
      unmodified against the extended catalog
- [X] T006 Extend `p0/qc_engine/mismo.py`'s field extraction (adding `_first_text`/`_child_text`/block
      lookups following the existing namespace-agnostic local-name pattern, not a rewrite) to cover
      every new field from T004 whose `expected_sources` includes `"mismo"`, reading the actual
      elements present in the 5 loans' MISMO exports (depends on T004)
      → Done when: calling `mismo.parse_mismo()` against each of the 5 loans'
      `*_Loan_Data_MISMO.xml` files returns a value for every new mismo-sourced field that file's
      loan actually carries, with zero change to the function's existing return values for the
      original 7 fields (`borrower_name`, `borrower_ssn`, `note_rate`, `loan_amount`,
      `property_address`, `flood_zone`, `note_signed` if present, `term_months`, `property_value`,
      `purchase_price`, `loan_id`)

**Checkpoint**: Catalog and manifest groundwork complete. US1–US4 phases below can now proceed.

---

## Phase 3: User Story 1 — Engine and eval tests run against document-derived fixtures (Priority: P1) 🎯 MVP

**Goal**: Produce 5 `CanonicalLoan`-shaped fixtures, one per synthetic loan, each populated only from
that loan's own documents/MISMO export, loadable by the existing engine/eval with zero code changes.

**Independent Test**: Load each of the 5 generated fixtures through the existing
`CanonicalLoan`/`SourceValue` model with zero code changes; confirm all 5 load without error.

**Done when:**
- Exactly 5 fixture JSON files exist under `p0/fixtures/from_docs/`, one per loan
- Each fixture's fields come only from its own loan's folder (no cross-loan leakage)
- Each fixture loads into `CanonicalLoan` and scores via `p0/eval_synth`'s existing scorer with zero
  changes to the scorer

### Tests for User Story 1 ⚠️ (write first, confirm they fail before `build_fixtures.py` exists)

- [X] T007 [P] [US1] Test in `p0/tests/test_fixture_generation.py`: running `build_fixtures.py`
      produces exactly 5 fixture JSON files under `p0/fixtures/from_docs/`, one per loan, each
      fixture's `loan_id` matching that loan's own MISMO `LoanIdentifier`; confirm this fails today
      (module doesn't exist yet) (depends on T002)
      → Done when: the test is present, currently fails (import/collection error since
      `build_fixtures.py` doesn't exist yet), and asserts exactly 5 files + matching `loan_id`s once
      it can run
- [X] T008 [P] [US1] Test in `p0/tests/test_fixture_generation.py`: for each of the 5 fixtures, every
      populated field's citation (where present) names only a document from that loan's own
      `demo/syn/loan 0N/` folder — no field's citation or value is traceable to a different loan's
      documents (spec.md Acceptance Scenario 1, no cross-loan data leakage); confirm this fails today
      (depends on T002)
      → Done when: the test is present, currently fails (nothing to load yet), and asserts zero
      cross-loan citations once fixtures exist

### Implementation for User Story 1

- [X] T009 [P] [US1] Author per-document-type extraction patterns as data (not code-per-doc) in
      `p0/fixtures/from_docs/doc_patterns/{urla_1003,voe,credit_report,appraisal_1004,
      title_commitment,closing_disclosure,fha_docs,va_docs,usda_docs}.yaml` — label-anchored regex
      patterns keyed to the `field_catalog.json` fields from T004, derived by inspecting each loan's
      actual PDFs via `pdftotext -layout "demo/syn/loan 0N/NN_Document.pdf"` (all 33 PDFs are
      confirmed born-digital text per research.md decision #1 — no OCR needed) (depends on T004)
      → Done when: one `doc_patterns/*.yaml` file exists per document type listed, each with at
      least one label-anchored pattern per field it's expected to resolve
- [X] T010 [US1] Implement `p0/fixtures/from_docs/extract_pdf.py`: for each of the 33 PDFs, invoke
      `pdftotext -layout` as a subprocess, apply the matching `doc_patterns/*.yaml` pattern set for
      that document's type, and return per-field `{value, DocCitation(doc_name, page_num,
      segment_snippet)}` — deterministic pattern matching is the only primary path; an LLM
      (Bedrock, `temperature=0`) fallback is permitted only when no pattern resolves a field, and
      must be flagged distinctly in the output so `doc_confidence` (T012) can reflect it honestly
      (plan.md Technical Context, research.md decision #6) (depends on T009)
      → Done when: running `extract_pdf.py` against all 33 PDFs returns a value+citation for every
      field its patterns are expected to resolve, with identical output across repeated runs
      (byte-deterministic, plan.md Constraints)
- [X] T011 [US1] Implement `p0/fixtures/from_docs/extract_xml.py` as a thin wrapper over the extended
      `qc_engine/mismo.py` (T006) — invoked per loan, returning the `sources.mismo` side for every
      in-scope field (depends on T006)
      → Done when: running `extract_xml.py` against all 5 loans' MISMO exports returns the
      `sources.mismo` value for every field `mismo.parse_mismo()` (T006) resolves for that loan
- [X] T012 [US1] Implement `p0/fixtures/from_docs/build_fixtures.py`: for each of the 5 loans, merge
      `extract_pdf.py`'s truth+citation output (T010) and `extract_xml.py`'s `sources.mismo` output
      (T011) into one `CanonicalLoan` JSON fixture conforming to `001b`'s `SourceEnvelope`/inbound-
      contract shape (`specs/001b-source-envelope-and-inbound-contracts/contracts/`), setting
      `doc_confidence` honestly per extraction method (high/near-1.0 for a clean pattern match, lower
      and justified only for an LLM-fallback field — never a hardcoded flat default, research.md
      decision #6), writing output to `p0/fixtures/from_docs/loan_0N.json`, using only that loan's own
      folder as input (depends on T010, T011)
      → Done when: running `build_fixtures.py` writes exactly 5 `loan_0N.json` files, each parseable
      as `CanonicalLoan`, re-running it produces byte-identical output
- [X] T013 [P] [US1] Run T007–T008 again; confirm both green (depends on T012)
      → Done when: `python3 -m pytest p0/tests/test_fixture_generation.py -k "T007 or T008 or
      build_fixtures or cross_loan" -q` (or the equivalent test names actually chosen) exits 0
- [X] T014 [P] [US1] Test in `p0/tests/test_fixture_generation.py`: each of the 5 generated fixture
      JSON files loads into `p0/qc_engine/model.py`'s `CanonicalLoan` with zero code changes to
      `model.py`, and scores via `p0/eval_synth`'s existing scorer/`eval.py` with zero changes to the
      scorer itself (spec.md Acceptance Scenario 2, FR-008) (depends on T012)
      → Done when: the test passes, and `git diff` shows zero changes to `p0/qc_engine/model.py` or
      `p0/eval_synth`'s scorer module

**Checkpoint**: US1 delivered — 5 real, document-derived fixtures exist, load cleanly, and are
isolated per loan. Independently valuable even before US2's defect gate passes.

---

## Phase 4: User Story 2 — A fixture is never trusted until it proves itself against known answers (Priority: P1)

**Goal**: Every one of the 25 documented, embedded defects across the 5 loans is reproduced exactly
by the generated fixtures — a hard, mechanical, zero-partial-credit gate.

**Independent Test**: Run the verification step against the 5 generated fixtures; confirm it reports
all 25 known defects reproduced, with any non-25/25 result treated as a failure, not a warning.

**Done when:**
- `verify_against_defects.py` reports `25/25 matched` against the real generated fixtures
- A deliberately-broken fixture (missing one defect) is reported as `24/25` and the script exits
  non-zero — proving there is no partial-credit path

### Tests for User Story 2 ⚠️ (write first, confirm they fail before `verify_against_defects.py` exists)

- [X] T015 [P] [US2] Test in `p0/tests/test_fixture_generation.py`: running
      `verify_against_defects.py` against the 5 real fixtures (T012) asserts the aggregate result is
      exactly `25/25`; confirm this fails today (module doesn't exist yet) (depends on T003, T012)
      → Done when: the test is present, currently fails (import/collection error), and asserts
      exactly `25/25` once `verify_against_defects.py` exists
- [X] T016 [P] [US2] Test in `p0/tests/test_fixture_generation.py`: construct a synthetic "broken"
      fixture derived from one real fixture with exactly one of its 5 documented defects silently
      patched to match instead of mismatch (spec.md Edge Cases: 24/25 must not be treated as
      "mostly done"); assert `verify_against_defects.py` reports `24/25` for that loan and the
      overall run exits non-zero / raises rather than passing; confirm this fails today (depends on
      T003)
      → Done when: the test is present, currently fails (nothing to run yet), and asserts a `24/25`
      result plus non-zero exit/raised exception once `verify_against_defects.py` exists

### Implementation for User Story 2

- [X] T017 [US2] Implement `p0/fixtures/from_docs/verify_against_defects.py`: for each of
      `defect_manifest.json`'s 25 entries (T003), load the corresponding generated `CanonicalLoan`
      fixture (T012), resolve `field_name` (and `compare_field_name` if present), assert the
      extracted values match `expected_values` exactly — or, for `expected_relationship: "missing"`,
      that the field genuinely resolves to absent, never a fabricated placeholder (spec.md Edge
      Cases) — and report a per-defect breakdown (loan/field/matched-or-not) plus the aggregate
      `N/25`; treat anything less than `25/25` as a hard failure (non-zero exit / raised exception),
      never a warning to log and continue past (FR-005/FR-006, contracts/defect-verification-
      manifest.md Verification semantics) (depends on T003, T012)
      → Done when: `python3 p0/fixtures/from_docs/verify_against_defects.py` runs to completion,
      prints a per-defect breakdown plus an aggregate `N/25`, and exits non-zero whenever `N < 25`
- [X] T018 [P] [US2] Run T015–T016 again; confirm both green (depends on T017)
      → Done when: both tests pass against the real `verify_against_defects.py` implementation
- [X] T019 [US2] If T015 does not report `25/25` on first run against the real fixtures: iterate on
      `doc_patterns/*.yaml` (T009), `extract_pdf.py` (T010), `extract_xml.py` (T011), or the catalog
      entries (T004) until it does — this is the feature's actual accuracy-proving work, not a
      formality; do not proceed to Phase 5/6 or wire fixtures anywhere downstream until this passes
      (depends on T018)
      → Done when: `python3 p0/fixtures/from_docs/verify_against_defects.py` prints exactly
      `25/25 matched` against the 5 real generated fixtures

**Checkpoint**: 25/25 achieved and mechanically pinned. Per FR-006, fixtures are not considered
trustworthy — and MUST NOT be wired into any downstream engine/eval test run — until this checkpoint
is green.

---

## Phase 5: User Story 3 — The field vocabulary is grounded in real rules (Priority: P2)

**Goal**: Prove, as an explicit acceptance check (not just a byproduct of Phase 2's authoring), that
every new catalog field is traceable to a real rule taxonomy archetype, and that the extended catalog
still passes its own governance with zero regression.

**Independent Test**: Review the new catalog entries and confirm each cites the specific real-rule
archetype/condition that justifies its existence.

**Done when:**
- Every new `field_catalog.json` entry (from T004) has a reviewable, non-empty taxonomy.json
  archetype citation
- The catalog's referential-integrity and zero-regression validation (already run once in T005)
  passes again as this feature's own named acceptance gate

- [X] T020 [US3] Produce a grounding review artifact — a short table/section (in
      `p0/fixtures/from_docs/README.md` or a sibling doc) listing every new `field_catalog.json`
      entry from T004 alongside the exact `taxonomy.json` archetype id and condition text it is
      grounded in, confirming none were added merely because they happen to appear in one of the 5
      loans (SC-003, spec.md Acceptance Scenario 1) (depends on T004)
      → Done when: the grounding table lists every new `field_catalog.json` field with a named
      `taxonomy.json` archetype id and condition text, one row per new field, zero blanks
- [X] T021 [P] [US3] Test in `p0/tests/test_fixture_generation.py`: assert every new
      `field_catalog.json` entry from T004 has a non-empty grounding citation (a real `taxonomy.json`
      archetype id) present in its `description`, per the grounding table (T020) (depends on T020)
      → Done when: the test passes, confirming zero new fields lack a taxonomy.json archetype
      citation in their description
- [X] T022 [US3] Re-run the catalog's existing referential-integrity validator and zero-regression
      test suite (first run in T005) as this feature's own explicit, named acceptance gate for US3 —
      confirm zero regressions against prior engine verdicts (FR-009, SC-004) (depends on T005, T004
      final state)
      → Done when: the validator and full existing engine test suite pass again against the final
      catalog state with zero regressions

**Checkpoint**: Catalog growth is proven grounded, not ad hoc, and the shared governance artifact
(`field_catalog.json`) remains regression-free.

---

## Phase 6: User Story 4 — Every extracted value is traceable to exactly where it came from (Priority: P3)

**Goal**: Every document-sourced field value carries a full citation; every genuinely
system-of-record-sourced value carries an honest, non-fabricated provenance note instead.

**Independent Test**: Sample generated fixtures and confirm every document-sourced field has a
non-empty citation with document name, page number, and source text.

**Done when:**
- 100% of document-sourced field values across all 5 fixtures carry a non-empty
  `{doc_name, page_num, segment_snippet}` citation
- Any genuinely system-sourced (non-document) field carries a lightweight provenance note instead of
  a fabricated document/page citation

- [X] T023 [P] [US4] Test in `p0/tests/test_fixture_generation.py`: sample all 5 generated fixtures
      (T012); assert every `truth`-side (document-sourced) field value carries a non-empty
      `DocCitation{doc_name, page_num, segment_snippet}` (SC-002, spec.md Acceptance Scenario 1)
      (depends on T012)
      → Done when: the test passes, confirming 100% of document-sourced field values across all 5
      fixtures carry a non-empty citation
- [X] T024 [P] [US4] Test in `p0/tests/test_fixture_generation.py`: for any field genuinely sourced
      from a system-of-record rather than a document (e.g. an FHA-case-number field's system side —
      research.md decision #4's non-doc-vs-doc case), assert it carries a lightweight
      source-provenance note appropriate to a non-document origin, and never a fabricated
      document-name/page-number citation (spec.md Acceptance Scenario 2) (depends on T012)
      → Done when: the test passes, confirming every genuinely system-sourced field carries a
      provenance note and zero fabricated doc/page citations exist
- [X] T025 [US4] Where T023/T024 find gaps, patch `extract_pdf.py` (T010) / `extract_xml.py` (T011) /
      `build_fixtures.py` (T012) until citations/provenance notes are complete; re-run T023–T024 to
      confirm green (depends on T023, T024)
      → Done when: T023 and T024 both pass against the final `build_fixtures.py` output

**Checkpoint**: Full audit trail — every extracted value, document- or system-sourced, is
traceable to exactly where it came from.

---

## Phase 7: Polish & Cross-Cutting

- [X] T026 Run the full existing suite unmodified — `p0/tests/test_p0.py`,
      `p0/tests/test_predicate_archetypes.py`, `p0/tests/test_threshold_archetypes.py`,
      `p0/eval_synth/test_properties.py`, `python3 p0/harness.py` (bit-exact determinism digest) —
      plus the new `p0/tests/test_fixture_generation.py`; confirm zero regression (SC-004)
      → Done when: `python3 -m pytest p0/tests/ p0/eval_synth/test_properties.py -q` exits 0 with no
      failures, and `python3 p0/harness.py`'s digest is unchanged from its pre-feature value
- [X] T027 Confirm `p0/fixtures/from_docs/README.md`'s three disclaimers from T001 (not-Touchless,
      no real-document accuracy claim, doc-vs-doc deferred to `003c`) still accurately describe what
      was actually built, and update them if implementation diverged from plan.md
      → Done when: README.md's disclaimers match the as-built code with no stale claims
- [X] T028 Add a post-hoc "Implementation Notes" section to `plan.md` recording what was actually
      built — final task count, any amendment discovered during implementation, the final count of
      new catalog fields added, and `verify_against_defects.py`'s final `25/25` result — mirroring
      `001a`/`001b`/`002a`/`002b`/`003a`/`003b`'s own post-implementation notes convention
      → Done when: `plan.md` has an "Implementation Notes" section referencing the actual task
      count and the 25/25 verification result
- [X] T029 (added post-implementation, per quickstart.md step 5) Wire the 5 document-derived
      fixtures into the real engine test suite (`p0/tests/test_p0.py`), not just
      `test_fixture_generation.py`'s eval-scorer-level proof (T014) — run each fixture through
      `qc_engine.run()` (the same entry point `golden_loans()` uses), alongside (not replacing) the
      hand-authored golden set, confirming zero code changes to `run()`/`model.py` and zero
      regression on the pre-existing determinism digest
      → Done when: `p0/tests/test_p0.py::test_document_derived_loans_run_through_the_real_engine`
      passes, `python3 -m pytest p0/tests/ p0/eval_synth/test_properties.py -q` shows 92 passed
      (91 + 1), and `python3 p0/harness.py`'s digest is unchanged
      (`8510a0a8b4b6996e047fc8534e094394ba72aae396305b0d2ecad3d6924634db`)
- [X] T030 (added post-implementation, per Gordon's ask for "the actual data" + a review of
      `examples/mortgage-qc/schemas/extraction/*.yaml` for extraction breadth) Add comprehensive-
      coverage fields across every document type present in the 5 loans, as a second grounding
      category distinct from T004's rule-grounded 32 — self-identified per-entry, never conflated
      → Done when: `field_catalog.json` has 95 entries (39 + 56), `verify_against_defects.py`
      still reports 25/25, `test_every_new_catalog_field_has_taxonomy_grounding_citation` and the
      new `test_comprehensive_coverage_fields_do_not_masquerade_as_rule_grounded` both pass, full
      suite shows 93 passed, and the determinism digest is unchanged
- [X] T031 (added post-implementation, per Gordon's ask for "page number/section/titles/metadata
      for citation purposes") Extend `DocCitation` (`document_title`/`section`/`field_label`,
      additive/optional) and populate them in `extract_pdf.py`; `to_dict()` must only emit the new
      keys when set, so `golden.py`'s existing citations stay byte-identical and the determinism
      digest referenced across 8 other specs is not disturbed
      → Done when: `test_citation_carries_document_title_section_and_field_label` passes, 100% of
      document-sourced fields carry a non-empty `document_title`, at least some carry a genuine
      (non-title-echoing) `section` and a clean (no dangling punctuation) `field_label`,
      `verify_against_defects.py` still reports 25/25, full suite shows 94 passed, and
      `python3 p0/harness.py`'s digest is unchanged
      (`8510a0a8b4b6996e047fc8534e094394ba72aae396305b0d2ecad3d6924634db`)
- [X] T032 (added post-implementation, per Gordon's direct question "did we extract data from all
      the PDF files? is it comprehensive? and align with the rules questions") Audit real-document
      coverage against `demo/syn/`, close any gap found, and verify rule-relevance against the real
      AMQ workbook rather than assume it
      → Done when: `test_every_real_loan_document_is_matched_by_a_doc_pattern` passes (32/32 real
      documents matched, only the answer-key excluded), `paystub.json`/`disclosure_package_index.json`
      exist with fields verified against `demo/rules/PF and PC Sept 2025 AMQs - Retail.xlsx` real
      conditions, `verify_against_defects.py` still reports 25/25, full suite shows 95 passed, and
      the determinism digest is unchanged
- [X] T033 (added post-implementation, per Gordon's direct question "why is the truth for this null,
      looks like there is an address in the mismo field") Write doc-side extraction patterns for the
      5 original seed catalog fields (`property_address`, `note_rate`, `loan_amount`,
      `borrower_name`, `borrower_ssn`) — previously only their `sources.mismo` side was ever
      populated (by pre-existing `mismo.py`, unrelated to this feature); no `doc_patterns/*.json`
      file had ever targeted these field names themselves
      → Done when: `test_original_seed_fields_get_doc_side_truth_not_just_mismo` passes (all 5
      fields non-null across all 5 loans, `borrower_name` matches the loan's actual borrower, not a
      dollar amount from an unrelated line), running the 5 fixtures through `qc_engine.run()` with
      `demo_ruleset()` produces genuine `PASS`/`FLAG` verdicts on `chk-borrower-name`/`chk-note-rate`/
      `chk-principal`/`chk-property-address` (not blanket N/A), `verify_against_defects.py` still
      reports 25/25, full suite shows 96 passed, and the determinism digest is unchanged
- [X] T034 (added post-implementation, per Gordon's ask to "pull the doc-side truth into more of the
      seed fields") Fix `property_value` (same mismo-only gap as `property_address`) and wire
      `build_fixtures.py`'s always-empty `facts{}` so `chk-ltv-max` can read real values; confirm
      `flood_zone`/`note_signed` are honest, undocumented-source absences, not a pattern gap
      → Done when: `test_property_value_gets_doc_side_truth_and_facts_are_derived` passes (all 5
      loans have non-null `property_value` truth and populated `facts`, loan 01's derived LTV matches
      its own answer key's stated 80% within tolerance), `verify_against_defects.py` still reports
      25/25, full suite shows 97 passed, and the determinism digest is unchanged
- [X] T035 (added post-implementation, per Gordon's ask to "keep expanding field coverage") Density
      review found loans 02-05's program-specific documents (FHA Connection, Gift Letter, CAIVRS,
      VA COE/NOV, USDA GUS/Property Eligibility, Payoff Statement, Self-Employed Income Index) still
      only carried their original 1-2 defect-narrow fields; loan 01's documents already got
      comprehensive treatment. Add 48 new fields across 8 pattern files closing that gap
      → Done when: `field_catalog.json` has 159 entries (111 + 48), field density rises for loans
      02-05 (spot-checked against source text, not assumed), a full sweep finds zero dirty
      `field_label`s or missing `document_title`s across all 159 fields, `verify_against_defects.py`
      still reports 25/25, full suite still shows 97 passed, and the determinism digest is unchanged
- [X] T036 (added post-implementation, per Gordon's ask to "extract remaining bulk data like bank
      transactions and credit trade lines") Build a table-row extraction primitive (indexed scalar
      fields per row, since `001a`'s schema has no array type) for the bank statement's 16-row
      ledger, the credit report's 4 trade lines, and the appraisal's 3-row comparable-sales grid
      → Done when: `test_bank_ledger_reconciles_to_the_penny` passes (beginning + credits - debits =
      ending balance to the penny, independent of any single-value spot check), all 16 transaction
      rows and 4 trade lines and 3 comps are present with correct citations, `field_catalog.json` has
      261 entries (159 + 102), `verify_against_defects.py` still reports 25/25, full suite shows 98
      passed, and the determinism digest is unchanged
- [X] T037 (added post-implementation, per Gordon's ask to "check loan 02-05" for the same class of
      untapped bulk data) Systematic per-document review found 5 more tables: loan 01's 1003
      Assets/Liabilities (missed by T036 entirely), loan 02's FHA appraisal MPR items, loan 04's
      Mortgage Payment History (all 12 months) and Self-Employed Income Documentation checklist
      → Done when: `test_round4_tables_have_correct_row_counts_and_no_page_break_collisions` passes
      (locks in the page-break bug fix in `_extract_simple_table`/`_extract_bank_ledger`, where a
      table's row counter resetting per-page silently collided row numbers across a page break —
      caught via loan 01's own Assets table, which straddles pdftotext's page 1/2 split), 108 new
      catalog fields (369 total), an independent hand-arithmetic check (1003 liabilities sum to
      $684.00/mo) passes, `verify_against_defects.py` still reports 25/25, full suite shows 99
      passed, and the determinism digest is unchanged
- [X] T038 (added post-implementation, per Gordon's ask to keep expanding coverage, naming the
      credit report's inquiry table specifically) Extract the last remaining known table: 2 rows
      (Date/Bureau/Requesting Party) — one is part of the undisclosed-liability defect's own paper
      trail (defect #4)
      → Done when: `test_credit_inquiry_table_extracted` passes, 6 new catalog fields (375 total),
      every other document across all 5 loans reconfirmed single-record (no further tables found),
      `verify_against_defects.py` still reports 25/25, full suite shows 100 passed, and the
      determinism digest is unchanged
- [X] T039 (added post-implementation, per Gordon's ask to "start wiring the new fields into actual
      checks") Categorize all 25 known defects by required check-kind, then wire the 20 that map to
      already-built kinds (predicate, ratio_threshold field_value, agree_categorical) into a new
      ruleset — deliberately separate from `ruleset_demo.py`, whose exact content is pinned in
      `harness.py`'s digest. 2 new derived fields (`appraisal_staleness_days`, `nov_days_after_closing`)
      computed in `build_fixtures.py` for the 2 date-diff defects (no new engine code — lands in
      `fields{}` so the existing `field_value` mode can check it). The remaining 5 defects are genuine
      doc-vs-doc mismatches with no check-kind yet — explicitly not built, deferred to 003c per
      research.md decision #4.
      → Done when: `p0/fixtures/ruleset_defects.py` passes referential integrity against the catalog,
      all 20 wirable defects produce their correct verdict (`FAIL`, or `FLAG` for the one
      doc-vs-system reconcile check) on the exact loan the manifest names, every threshold/derived
      check resolves `NOT_APPLICABLE` (not a false FAIL/PASS) on the 4 loans it doesn't apply to,
      `verify_against_defects.py` still reports 25/25, full suite shows 103 passed, and the
      determinism digest is unchanged
- [X] T040 (added post-implementation, per Gordon's ask to "focus on [fixing the 13 predicate checks'
      false-FAIL on inapplicable loans] first") Gate each of the 13 predicate checks by whether it
      actually applies to a given loan, instead of running all 13 unconditionally against all 5 loans.
      3 different gates, not 1: 7 by document-presence (a new `_derive_document_presence_facts()` in
      `build_fixtures.py`, stored in `facts{}`, not `fields{}`), 2 by property-age
      (`year_built_appraisal` < 1978, conservative gate-IN when unknown), 4 by loan program (no PDF
      exists anywhere for these, so document-presence can't gate them). New
      `defects_ruleset_for(loan)` in `ruleset_defects.py` is the real evaluation entrypoint; the old
      `defects_ruleset()` is kept as the unfiltered universe for referential-integrity checks only.
      Zero engine.py/model.py changes — pure ruleset-assembly logic, each loan effectively getting its
      own Route.
      → Done when: `test_predicate_checks_are_gated_by_applicability_not_universal` locks in the exact
      applicable-check set per loan (including the documented lead-paint residual on loans without
      year data), loan 01 shows only 1 of 13 predicate checks firing (down from all 13),
      `verify_against_defects.py` still reports 25/25, full suite shows 104 passed, and the
      determinism digest is unchanged

---

## Dependencies & Execution Order

- **Phase 1 (Setup, T001–T002)** has no dependencies; both tasks parallelizable.
- **Phase 2 (Foundational, T003–T006)** blocks all of Phase 3–6. T004 depends on T003; T005 depends
  on T004; T006 depends on T004. Although the catalog-grounding *concern* is labeled US3 (P2) in
  spec.md, the catalog *entries themselves* are a hard technical prerequisite for US1 (full field
  population) and US2 (defect-field resolution) — both P1 — so their authoring lives here, not in
  Phase 5. Phase 5 (US3) still carries the acceptance proof that this authoring was properly
  grounded and regression-free.
- **Phase 3 (US1, T007–T014)** depends on Phase 2 in full (needs T004's fields and T006's mismo
  extraction). Independently shippable once done — does not require US2/US3/US4.
- **Phase 4 (US2, T015–T019)** depends on Phase 3's `build_fixtures.py` (T012) and Phase 2's
  `defect_manifest.json` (T003). This is the feature's hard trustworthiness gate (FR-006) — nothing
  after this phase may be described as "wired downstream" until it passes 25/25.
- **Phase 5 (US3, T020–T022)** depends on T004/T005 (Phase 2) already existing; it re-validates and
  documents what Phase 2 built rather than re-authoring it.
- **Phase 6 (US4, T023–T025)** depends on Phase 3's `build_fixtures.py` (T012); independent of
  Phase 4/5 — can run in parallel with them once T012 exists.
- **T026–T028 (Polish)** run last, after all user stories are complete.

## Parallel Execution Examples

```
# Phase 1 — both independent:
Task: "T001 Create p0/fixtures/from_docs/ skeleton + README disclaimers"
Task: "T002 Create p0/tests/test_fixture_generation.py skeleton"

# Phase 3 (US1) — tests-first, parallel:
Task: "T007 Test: build_fixtures.py produces exactly 5 fixtures"
Task: "T008 Test: no cross-loan data leakage"

# Phase 6 (US4) can run alongside Phase 4/5 once T012 (Phase 3) exists:
Task: "T023 Test: every doc-sourced value has a non-empty citation"
Task: "T024 Test: system-sourced values carry a provenance note, not a fabricated citation"
```

## Implementation Strategy

**MVP first**: Phase 1 → Phase 2 (Foundational) → Phase 3 (US1) delivers real, isolated,
model-compatible fixtures — independently valuable even before the defect gate is proven.

**Incremental delivery from there**:
1. Phase 4 (US2) proves those fixtures are actually trustworthy (25/25) — the feature's real bar.
2. Phase 5 (US3) proves the catalog growth underneath US1/US2 was principled, not convenient.
3. Phase 6 (US4) rounds out the audit trail (citations/provenance) — valuable but not blocking
   US1/US2's correctness claim, matching spec.md's stated priority (P3).
4. Phase 7 closes out with the zero-regression proof and documentation, matching this repo's
   established `001a`–`003b` convention.
