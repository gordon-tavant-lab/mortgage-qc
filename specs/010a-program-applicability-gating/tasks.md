# Tasks: Program Applicability Gating

**Input**: Design documents from `specs/010a-program-applicability-gating/`
**Prerequisites**: plan.md, spec.md

**Tests**: Included — this project's constitution makes eval/regression-proof foundational
(Principle III); SC-001–005 are the correctness/safety proof this feature exists to produce.

**Organization**: Tasks grouped by user story (spec.md P1/P2/P3). US1's mapping logic is new code —
tests are written to fail first (red), confirming they exercise real new behavior, per the TDD
discipline `002b`/`003a`/`003b` established.

## Phase 1: Setup

- [x] T001 Create `p0/qc_engine/compiler/program_gating.py` module skeleton (module docstring per
      the existing `compiler/*.py` style; imports only) — no logic yet
      → Done when: the module imports cleanly with zero errors
- [x] T002 Create `p0/tests/test_program_applicability_gating.py` module skeleton — no test bodies
      yet
      → Done when: `python -m pytest p0/tests/test_program_applicability_gating.py --collect-only`
      exits 0 with zero tests collected

---

## Phase 2: User Story 1 — A compiled check only fires for the program it's tagged for (Priority: P1) 🎯 MVP

**Done when:**
- Each of the 5 confirmed Exception Code prefixes maps to its program correctly
- A gated ruleset build for a given synthetic loan includes only checks whose program matches
- The Fannie/Freddie "Conventional" ambiguity is surfaced inspectably, never silently guessed
- An untagged row (no program prefix) defaults to applying across every program

### Tests for User Story 1 ⚠️ (write first, confirm they FAIL before implementation)

- [x] T003 [P] [US1] Test: `parse_exception_code_prefix("O-FHA-15293")` (and the other 4 real
      prefixes, using the actual codes captured in `output/RULE-PROGRAM-GATING-FINDINGS.md` §2) each
      resolve to the correct program string; confirm red (function doesn't exist yet), in
      `p0/tests/test_program_applicability_gating.py`
- [x] T004 [P] [US1] Test: a `CompiledCheckDraft`-shaped fixture derived from an `O-FHA-`-prefixed
      row, gated against all 5 synthetic loans' real `loan_type` values (`"Conventional Purchase"`,
      `"FHA Purchase"`, `"VA Purchase"`, `"Freddie Mac Cash-Out Refi"`, `"USDA RHS 502 Guaranteed"`)
      — applies only to the FHA loan; confirm red
- [x] T005 [P] [US1] Test: same pattern for `O-VA-`, `O-RHS-`, `O-FRD-` — each applies only to its
      one matching synthetic loan; confirm red
- [x] T006 [US1] Test: an `O-FNM-`-prefixed check gated against the `"Conventional Purchase"` loan —
      assert the ambiguity-surfacing behavior (FR-005) fires (e.g. a returned flag/log entry, not a
      silent True/False), not a bare boolean; confirm red
- [x] T007 [P] [US1] Test: a row with no program-prefixed Exception Code (e.g. `O-TILA-...`) and no
      SQL clause — applies to all 5 synthetic loans (fail-open default, FR-004); this one may already
      pass trivially depending on the default's implementation — included as the baseline case, not
      necessarily a red test

### Implementation for User Story 1

- [x] T008 [US1] In `program_gating.py`, implement the 5-entry `_PREFIX_TO_PROGRAM` table and
      `parse_exception_code_prefix(exception_code: str) -> Optional[str]` (depends on T003–T007
      existing as tests)
- [x] T009 [US1] In `program_gating.py`, implement `_loan_type_matches_program(loan_type: str,
      program: str) -> bool` covering the 5 confirmed `loan_type` strings, with the Fannie/Freddie
      ambiguity path returning an explicit ambiguous-marker (not `True`/`False`) per FR-005
- [x] T010 [US1] In `program_gating.py`, implement `applies_to(loan: CanonicalLoan, applicability)
      -> bool` — the gate a ruleset build calls per check, generalizing
      `ruleset_defects.py::_check_applies`'s program-gate branch
- [x] T011 [US1] In `compiler/compile_llm.py`, add an `applicability` field to `CompiledCheckDraft`
      and populate it from `row["exception_code"]` via `program_gating.parse_exception_code_prefix`
      at compile time (depends on T008)
- [x] T012 [US1] Run T003–T007 again; confirm all green

**Checkpoint**: A compiled check's program applicability is derivable and correctly gates a ruleset
build for each of the 5 synthetic loans' real programs. Independently valuable — does not require
US2/US3 to be true.

---

## Phase 3: User Story 2 — The SQL-clause mechanism narrows further where encoded (Priority: P2)

**Done when:**
- A row carrying both an Exception Code program prefix and a SQL clause narrows on both
- A row with no SQL clause is gated by the Exception Code prefix alone, unaffected

### Tests for User Story 2

- [x] T013 [P] [US2] Test: a fixture built from a real captured SQL clause (e.g. `O-FNM-` prefix +
      `WHERE (Loans.QC_Policy = 'Fannie Mae') AND (Loans.PropertyType = 'Condominium')`, verbatim
      from `output/RULE-PROGRAM-GATING-FINDINGS.md` §3) — applies only to a matching-program loan
      whose property type is also Condominium; excluded for a matching-program, non-condo loan
      (depends on T008–T010 existing)
- [x] T014 [P] [US2] Test: a row with no SQL clause at all — gating result unchanged from
      Exception-Code-prefix-alone (US1); the absence of a clause never narrows further

### Implementation for User Story 2

- [x] T015 [US2] In `program_gating.py`, implement `parse_sql_gating_clause(clause_text: str) ->
      Dict[str, Any]` extracting the 5 confirmed field/value patterns (`PropertyType`, `QC_Policy`,
      `LoanPurposeType`, `LoanType`, `AddressState`) via the same `Loans\.(\w+)\s*=\s*'([^']*)'`
      pattern used to derive them in `output/RULE-PROGRAM-GATING-FINDINGS.md`
- [x] T016 [US2] In `applies_to()`, AND the SQL-clause-derived filter (if present) against the
      program-prefix result from US1 — never OR, never a replacement (FR-003)
- [x] T017 [US2] Run T013–T014 again; confirm both green

**Checkpoint**: The secondary mechanism narrows correctly on top of the primary one, and is
correctly inert when absent.

---

## Phase 4: User Story 3 — Every rule row is actually read (Priority: P3)

**Done when:**
- `taxonomy.py`'s row-loader reads every sheet in a workbook file, not only the first

### Tests for User Story 3

- [x] T018 [US3] Test: loading rows from the Private Bank workbook returns rows from both
      `Post Closing Oct 2025` and `Pre Funding Nov 2025` sheets — assert the previously-unread
      `PB-FormDoc` exception code (or an equivalent second-sheet row) is present in the result;
      confirm red against today's `load_rows()` (single-sheet)

### Implementation for User Story 3

- [x] T019 [US3] In `p0/eval_synth/taxonomy.py`'s `load_rows()`, iterate `wb.worksheets` instead of
      indexing `wb[wb.sheetnames[0]]`
- [x] T020 [US3] Run T018 again; confirm green
- [x] T021 [US3] Re-run `python3 p0/eval_synth/taxonomy.py` and confirm `total_defect_conditions`,
      `classified`, and `classified_pct` in `taxonomy.json` update to reflect the now-included second
      sheet's rows (small, expected delta — document the before/after counts in this task's
      completion note, don't silently overwrite without recording the change)

---

## Phase 5: Polish & Cross-Cutting

- [x] T022 [P] Test (FR-008, backward-compatibility): `ruleset_defects.py`'s 21 checks and their
      existing hand-derived gates are untouched — run `p0/tests/test_p0.py`'s existing suite plus
      `python3 p0/fixtures/from_docs/verify_against_defects.py` and confirm 25/25 still passes
- [x] T023 Run the full existing suite unmodified: `python3 -m pytest p0/ -q` and `python3
      p0/harness.py`, confirm zero regression (SC-004) — the digest
      (`a3f702c12969f7eb657471796c95e2a493d459c4c55663fa8fc18ac31e8c1d09`) must be unchanged, since
      this feature touches no engine/model/ruleset code
- [x] T024 Add a post-hoc "Implementation Notes" section to `plan.md` recording: final task count,
      total new test count, the `taxonomy.json` before/after delta from T021, and confirmation that
      `engine.py`/`model.py`/`ruleset.py`/`reconcile.py` were not touched

## Dependencies & Execution Order

- **T001–T002** (setup) block all of Phase 2.
- **Phase 2 (US1, T003–T012)** is the MVP slice. T003–T005, T007 are parallelizable `[P]` as red
  tests; T006 depends on the same fixture pattern as T003–T005 existing first; implementation
  (T008–T011) is sequential (same module); T012 confirms green.
- **Phase 3 (US2, T013–T017)** depends on Phase 2's implementation existing (T008–T010) — it adds a
  narrowing filter on top of the same mechanism, not new mechanism.
- **Phase 4 (US3, T018–T021)** is independent of Phases 2–3 (a different file, `taxonomy.py`) — can
  run in parallel with either, sequenced last here only for narrative order.
- **T022–T024** run last, after all user stories are complete.

## Phase 6: Amendments (found mid-build, not in the original plan)

Two rounds of self-correction happened during implementation, both disclosed in
`output/RULE-PROGRAM-GATING-FINDINGS.md`'s revision history and in `plan.md`'s Implementation
Notes — the tasks below record what was actually done to fix them, since T001–T024 above describe
the *original* (partially incorrect) plan, not silently rewritten to pretend it was always right.

- [x] T025 Fix `taxonomy.py`'s `load_rows()`: detect the "Post-Closing Private Bank Oct 2025"
      questionnaire (by `Questionnaire Name`, column A) and apply a separate, shifted column map —
      its real Exception Code/defect_text/sql_criteria/significance are each one column left of
      where the shared header claims. Verified against a real row (`O-FNM-15339`).
- [x] T026 Extend `load_rows()` to capture each row's own SQL gating clause ("Question Criteria") as
      a new `sql_criteria` field — previously dropped entirely, needed by `parse_sql_gating_clause`.
- [x] T027 Fix `taxonomy.py`'s `main()` to exclude Excel's `~$`-prefixed lock/temp files from its
      workbook listing (crashed with `BadZipFile` when the source files were open in Excel;
      `compiler/sample.py` already excluded these, `taxonomy.py` did not).
- [x] T028 Add `SONYMA` to `program_gating.py`'s `_PREFIX_TO_PROGRAM` table (6th confirmed program,
      per Gordon's explicit direction) and extend `parse_exception_code_prefix` to handle its
      space-delimited format (`SONYMA`, `SONYMA HDFC`, `SONYMA Tax `) alongside the other 5's
      dash-delimited format.
- [x] T029 Test: SONYMA's space-delimited codes resolve correctly despite the format difference.
- [x] T030 Test: a SONYMA-tagged check applied against all 5 existing synthetic loans is
      unambiguously excluded from all 5 (untested-against-a-real-fixture, but verified not to
      silently match anything).
- [x] T031 Test: `load_rows()` against the shifted questionnaire returns the corrected
      exception_code/defect_text/sql_criteria/significance for a known real row.
- [x] T032 Re-run T022–T024's full regression check after all amendments: 144/144 tests pass
      (up from 128), digest unchanged (`a3f702c12969f7eb657471796c95e2a493d459c4c55663fa8fc18ac31e8c1d09`),
      25/25 known defects.

## Parallel Example

```
# T003–T005, T007 (Phase 2, one prefix/default case each) can run together once T001–T002 exist:
Task: "O-FHA- prefix maps and gates correctly, red test"
Task: "O-VA-/O-RHS-/O-FRD- prefixes map and gate correctly, red test"
Task: "Untagged row fails open across all 5 loans, baseline case"

# T013–T014 (Phase 3, SQL-clause narrowing) can run together once T008–T010 exist:
Task: "SQL clause narrows a program-matched check further"
Task: "No SQL clause leaves the prefix-alone result unchanged"
```
