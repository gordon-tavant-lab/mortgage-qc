# Tasks: Doc-vs-Doc Reconcile Check Engine

**Input**: Design documents from `specs/003d-engine-doc-vs-doc-reconcile-checks/`
**Prerequisites**: plan.md, spec.md

**Tests**: Included — SC-001/002 are the correctness/safety proof this feature exists to produce;
SC-003 is the zero-*unrelated*-regression gate.

**Note on TDD ordering**: unlike `003c`, this feature adds real engine code — the new-kind tests in
Phase 2/3 are written and expected to FAIL until the corresponding `engine.py`/`ruleset.py` changes
land (T004-T006), then pass. This is genuine red-then-green, not proof-only.

**Organization**: Tasks grouped by user story, per the constitution's rule that each slice ships
with its own proof.

## Phase 1: Setup

- [X] T001 Add `compare_field_name: Optional[str] = None` to `Check` (`p0/qc_engine/ruleset.py`);
      update the kind docstring block to list `agree_doc_categorical`/`agree_doc_numeric` and their
      `QC` phase default
      → Done when: `Check(id="x", name="x", field_name="a", kind="agree_doc_categorical",
      severity="CRITICAL", compare_field_name="b")` constructs without error
- [X] T002 Create `p0/tests/test_doc_vs_doc_reconcile.py` module skeleton (imports, module docstring
      describing scope: proves the two new kinds, the FAIL-not-FLAG property, and the
      `SOURCE_INCOMPLETE` one-side-absent case) — no test bodies yet
      → Done when: `pytest p0/tests/test_doc_vs_doc_reconcile.py --collect-only` exits 0 with zero
      tests collected

---

## Phase 2: User Story 1 — A doc-vs-doc mismatch is caught as a real, deterministic defect (Priority: P1) 🎯 MVP

**Done when:**
- `agree_doc_categorical`/`agree_doc_numeric` produce correct verdicts across agreement, genuine
  divergence, one-side-absent, both-absent
- `agree_doc_numeric` correctly handles tolerance boundaries and the `UNSPECIFIED` honesty guard

**Independent Test**: Build a loan with independently-populated doc values for two named fields;
construct one agreeing case and one genuinely-diverging case; confirm correct verdicts for both a
categorical and a numeric pair.

- [X] T003 [US1] In `engine.py`'s `_eval_check`, add the `agree_doc_categorical` branch: lookup
      `loan.get(chk.field_name).doc` and `loan.get(chk.compare_field_name).doc`, both-absent →
      `NOT_APPLICABLE`, one-absent → `NEEDS_REVIEW` + explicit `review_reason="SOURCE_INCOMPLETE"`,
      else normalize both (reuse `R.normalize`) and compare → `PASS`/`FAIL` (depends on T001)
- [X] T004 [US1] Add the `agree_doc_numeric` branch, mirroring `agree_numeric`'s
      `Decimal`/`within_tolerance` logic and its `UNSPECIFIED`-tolerance guard, comparing
      `chk.field_name`/`chk.compare_field_name`'s doc values (depends on T001)
- [X] T005 [US1] In `test_doc_vs_doc_reconcile.py`: categorical agreement → `PASS`; genuine
      divergence (independently constructed, not a same-value copy) → `FAIL`; one-side-absent →
      `NEEDS_REVIEW`/`SOURCE_INCOMPLETE`; both-absent → `NOT_APPLICABLE` (depends on T003)
- [X] T006 [US1] In `test_doc_vs_doc_reconcile.py`: numeric equivalents of T005's four cases, plus
      at/within/outside-tolerance and an `UNSPECIFIED`-tolerance case (depends on T004)
- [X] T007 [US1] Extend `p0/qc_engine/catalog.py`'s `validate_referential_integrity()` to also
      resolve `chk.compare_field_name` when present; add a test asserting a bad `compare_field_name`
      is rejected at load time (depends on T001)

---

## Phase 3: User Story 2 — A doc-vs-doc mismatch is a real defect, not an informational FLAG (Priority: P1)

**Done when:**
- A genuine doc-vs-doc mismatch surfaces in `qc_failures`/`exceptions` with `review_reason=
  "EXCEPTION"`, blocks `auto_cleared`, and is never misclassified as a reconcile `FLAG`

**Independent Test**: Run a loan with a genuine doc-vs-doc mismatch and no other QC failure; confirm
it surfaces as a QC failure, not a reconcile flag.

- [X] T008 [US2] Confirm (by direct code read, not by adding code) that `_phase_for()` is left
      unmodified — the two new kinds are simply absent from its `RECONCILE`-inference tuple, so they
      default to `QC` for free (depends on T003, T004)
- [X] T009 [US2] In `test_doc_vs_doc_reconcile.py`, add the phase/disposition proof: a lone doc-vs-doc
      mismatch produces `qc_failures` non-empty, `disposition == "NEEDS_REVIEW"`,
      `review_reasons == {"EXCEPTION"}` — explicitly asserting it is NOT the `agree_categorical`
      `FLAG` path (depends on T005)

---

## Phase 4: Polish & Cross-Cutting

- [X] T010 Add `expected_sources` to `compile_llm.py`'s `_existing_catalog_fields()` payload
- [X] T011 Extend `compile_llm.py`'s `SYSTEM_PROMPT`: loosen the `kind MUST exactly equal
      engine_kind` constraint for the reconcile family to let the compiler pick doc-vs-system
      (unchanged) vs. doc-vs-doc (new kinds + `compare_field_name`) based on `expected_sources` and
      `defect_text`; add the `compare_field_name` output schema key (depends on T010)
- [X] T012 Extend `compile_llm.py`'s `_KIND_ONLY_FIELDS` for the two new kinds (depends on T001)
- [X] T013 Extend `pattern_flags.py`'s `_flag_archetype_mismatch_risk()` kind gate to include the two
      new kinds (depends on T003, T004)
- [X] T014 In `p0/fixtures/ruleset_defects.py`, hand-author 5 `Check` objects for the 5 known
      defects (3 `agree_doc_categorical`: employment date, title vesting, loan purpose; 2
      `agree_doc_numeric`: liability amount, CD-vs-payoff amount); correct the module docstring
      (currently states these 5 are "not built here... do not add a workaround kind without that
      spec" — now stale) (depends on T003, T004)
- [X] T015 In `p0/tests/test_fixture_generation.py`, extend `field_to_check_id` and the wired-defects
      assertion to cover all 25 known defects (was 20), asserting each resolves its correct expected
      status (depends on T014)
- [X] T016 Digest re-baseline in `p0/tests/test_p0.py`: update the 4 digest-pinned tests per the
      `004` precedent (`PRE_004_BASELINE`/`POST_004_BASELINE` pattern); add
      `test_full_digest_matches_new_baseline_after_003d_doc_vs_doc` with the real, freshly-computed
      SHA-256 (depends on T001)
- [X] T017 Run `pytest p0/tests -v` in full; confirm zero unrelated regressions
- [X] T018 Re-run `p0/compile_runs/run_010_post_closing_only/run_against_loans.py` (or its updated
      equivalent using the T014 checks); confirm loan 01/04's 5 known checks now resolve correctly
      (depends on T014, T017)
- [X] T019 Update `output/ROADMAP.md` Tension #5 to reflect this feature's shipped scope (kinds,
      phase=QC, Phase 1/2 split) and mark it closed/scheduled

## Dependencies & Execution Order

- Phase 1 (T001-T002) blocks everything.
- Phase 2 (T003-T007) blocks Phase 3 (T008-T009).
- Phase 4's compiler tasks (T010-T012) are independent of Phase 2/3 and can run in parallel with
  them once T001 lands.
- T014 (hand-authored fixtures) depends on the engine branches (T003/T004) existing, not on the
  compiler changes (T010-T012) — Phase 1's proof is fixture-based, zero compile cost, per spec
  FR-010.
- T015-T019 are the closing verification sequence and run last, in order.

## Parallel Example

```
# T003/T004 (Phase 2, one engine branch each) can run together once T001 exists:
Task: "Add agree_doc_categorical branch to engine.py"
Task: "Add agree_doc_numeric branch to engine.py"

# T010-T013 (Phase 4 compiler/pattern_flags work) can run together once T001 exists,
# independent of T003-T009:
Task: "Add expected_sources to compile_llm.py payload"
Task: "Extend pattern_flags.py kind gate"
```
