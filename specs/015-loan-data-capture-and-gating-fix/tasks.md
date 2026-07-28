# Tasks: Loan Data-Capture & Precondition-Gating Fix (+ FIBO Alignment)

## Phase 0 — Field & Precondition Coverage Gate (build + run first)

- T001: Build `run_016_coverage_gate` — pull every `PreconditionProposal.field_name` from
  `ontology_pipeline.run_layers()` (including `FLAGGED`), check catalog/extraction/population status
  for each.
- T002: Extend the gate to also check every distinct `Check.field_name`/`compare_field_name` across
  `comprehensive_e2e_v6_ruleset.json` the same way (broader net beyond gating dimensions).
- T003: Curate a short FIBO `LOAN`/`RealEstateLoans` concept list (loan program/investor type,
  occupancy, property type, income type) and add as a third cross-check.
- T004: Run the gate against the current (pre-fix) repo state. Confirm it reports
  `loan_program_1003`/`income_type_used_for_qualification` as real gaps (SC-006).
- T005: Document the gate as a standing, required pass (short section in `CLAUDE.md` or `output/`).

## Phase A — the three required fixes

### Issue 3
- T006: Swap `run_015`'s `APPLICABILITY_PATH` to `post_closing_only_applicability.json`; update the
  docstring. Verify 0 `NO_TAG_FOUND` in isolation.

### Issue 2
- T007: `engine.py`'s `predicate`/`is_true` branch: `None` → `NEEDS_REVIEW`/`APPLICABILITY_UNKNOWN`,
  early return. `is_present` untouched. Fix the stale adjacent comment.
- T008: Rename/reassert `test_p0.py::test_is_true_missing_doc_fails` with a dated comment.
- T009: Add a new test: `is_true` + `None` → `NEEDS_REVIEW`.
- T010: Add/confirm a regression-pin test: `is_present` + `None` → `FAIL` unchanged.
- T011: `pytest p0/tests -v` — zero unexpected failures.
- T012: `harness.py` — compare digest to baseline; state result explicitly (expected unchanged).
- T013: `verify_against_defects.py` — confirm 25/25.

### Issue 1
- T014: Add `loan_program_1003` pattern to `doc_patterns/urla_1003.json`.
- T015: Add `loan_program_1003` entry to `field_catalog.json`.
- T016: Regenerate all 5 fixtures (`build_fixtures.py`); `verify_against_defects.py` → 25/25
  (hard gate). Diff-check: only `loan_program_1003` is new across all 5 fixtures.
- T017: `derive_loan_program()`: add GSE-marker branch on `loan_program_1003`, consulted after the
  existing presence-field path. Edit `build_loan_profiles_v3.py` in place.
- T018: Regenerate `storage/loan_profiles/v3/*.json`. Diff-check: only loans 01/04 change.
- T019: `program_gating.py::applies_to()`: prefer the real derived `loan_program` fact, fall back to
  the existing string-match path.
- T020: Verify `test_program_applicability_gating.py` unchanged for bare loans (no `loan_program`
  fact) — including the existing no-signal `AMBIGUOUS` assertions.
- T021: Add new test: Fannie-tagged check → `True`, Freddie-tagged check → `False` (not `AMBIGUOUS`),
  for a loan shaped like post-fix loan 01.
- T022: Rewrite the 3 tests pinning the old "underivable" outcome
  (`test_loan_profiles_v3.py` ×2, `test_occupancy_applicability_gating.py`'s
  `test_apply_derived_facts_writes_nothing_for_underivable_entries`) — keep the
  "writes-nothing-when-genuinely-underivable" invariant covered.
- T023: Full verification: `pytest`, `harness.py` (expect unchanged), `verify_against_defects.py`
  (25/25).
- T024: `cp p0/fixtures/from_docs/loan_0*.json result/loans/`.

### Regeneration + spec 014 follow-up
- T025: Re-run `run_015`; rewrite `honest_program_ambiguity_note`; add `known_caveats` (real
  `signoff_summary` + fix summary).
- T026: Produce `loan_04_all.json` (Gordon confirmed: fix both loans).
- T027: After Phase A/B are green, re-run `run_014_decision_narrative_panel/build_and_run.py`;
  refresh spec 014's status header with new real numbers.

## Phase B — ontology-grounded high-leverage fixes

- T028: Add `income_type_used_for_qualification` extraction pattern + catalog entry (confirm exact
  VOE/1003 source line at implementation time).
- T029: Add `derive_income_type()` to `build_loan_profiles_v3.py`.
- T030: Regenerate fixtures + profiles for all 5 loans (same diff-check discipline as T016/T018).
- T031: Verify self-employment-gated checks resolve `NOT_APPLICABLE` for loan 01 (not
  `APPLICABILITY_UNKNOWN`).
- T032: Register Question 571085's loan-product-type taxonomy through `002g`'s sign-off mechanism
  (confirm exact fact binding — same `loan_program` or a sibling `loan_product_type`).
- T033: Re-run precondition attachment; confirm ~165+ checks move `FLAGGED` → `applies_if`-gated.
- T034: Register Question 570606's asset-type taxonomy split (`fact-closing-funds-asset-type` vs.
  `fact-gift-funds-used`) through the same sign-off mechanism.
- T035: Re-run precondition attachment; confirm ~102 checks resolve.
- T036: Phase B full verification: `pytest`, `harness.py`, `verify_against_defects.py` (25/25),
  `run_013`'s attached/flagged counts moving as predicted.
- T037: Regenerate `loan_01_all.json`/`loan_04_all.json` once more on top of Phase A's regeneration.

## Phase C — Layer 1 (explicit decision)

- T038: Once Phase 0's real numbers are in hand, make and record an explicit go/no-go decision on
  running Layer 1 against the remaining fully-unconditional checks, sized to time actually available.

## FIBO documentation (do regardless of Phase C timing)

- T039: Add a dated architecture-decision section to `CLAUDE.md` (near Non-Negotiable #1) — FIBO as
  the permanent vocabulary-alignment framework, boundary stated explicitly (no reasoner in `engine.py`).
- T040: Write `output/FIBO-ONTOLOGY-ADOPTION-DECISION.md`.
- T041: Add a `ROADMAP.md` entry for the future full-migration spec.

## Final verification (all phases)

- T042: `pytest p0/tests -v` — zero unexpected failures, all changed assertions dated/commented.
- T043: `harness.py` digest — explicit final comparison to
  `82175d076579e31a50971d8b20ea4b63848bea9f9b53c30dd96524071842e5ec`.
- T044: `verify_against_defects.py` — final 25/25 confirmation.
- T045: `git diff` review of all regenerated fixtures/profiles — confirm scope matches each step's
  own diff-check description, nothing else.
- T046: Re-open `loan_01_all.json`/`loan_04_all.json` — confirm `NO_TAG_FOUND == 0`, definite GSE
  classification, no ungated-predicate-missing-data FAILs, `known_caveats` present.
- T047: Confirm spec 014's status header reflects fresh numbers, no stale figures left uncorrected.
