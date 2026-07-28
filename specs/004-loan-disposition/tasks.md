# Tasks: Loan Disposition (Composition Layer)

**Input**: Design documents from `specs/004-loan-disposition/`
**Prerequisites**: plan.md, data-model.md, spec.md

**Tests**: Included — this project's constitution makes eval/regression-proof foundational
(Principle III); SC-001–005 are the correctness/safety proof this feature exists to produce.

**Organization**: Tasks grouped by user story (spec.md P1/P1/P1). Unlike `003c` (proof-only, zero
engine change), this feature makes a small real addition to `engine.py` — tests for US1/US2 are
written to fail first (red), confirming they actually exercise new behavior, then the implementation
lands and turns them green, per the TDD discipline `003a`/`003b` established.

## Phase 1: Setup

- [X] T001 Create `p0/tests/test_loan_disposition.py` module skeleton (imports from
      `qc_engine`/`qc_engine.model`/`qc_engine.ruleset`, module docstring per the existing
      `p0/tests/test_reconcile_archetypes.py` style) — no test bodies yet
      → Done when: the file imports cleanly (`python -m pytest p0/tests/test_loan_disposition.py --collect-only` exits 0) with zero tests collected

---

## Phase 2: User Story 1 — Every reason a loan needs review is a distinct, inspectable tag (Priority: P1) 🎯 MVP

**Done when:**
- A QC-phase FAIL/WARNING tags `"EXCEPTION"`
- A confidence-withheld PASS tags `"LOW_CONFIDENCE"`
- A reconcile one-side-absent tags `"SOURCE_INCOMPLETE"`
- Multiple simultaneous reasons on one loan all surface in `review_reasons` together

### Tests for User Story 1 ⚠️ (write first, confirm they FAIL against today's engine before touching engine.py)

- [X] T002 [P] [US1] Test in `p0/tests/test_loan_disposition.py`: a loan with one QC-phase
      (`predicate` or `ratio_threshold`) `FAIL` — construct it, run it, assert
      `CheckResult.review_reason == "EXCEPTION"` and the loan's `RunResult.review_reasons == {"EXCEPTION"}`;
      confirm this fails against today's `engine.py` (no `review_reason` attribute exists yet — red)
- [X] T003 [P] [US1] Test: a loan with a `PASS` downgraded by the confidence gate (`doc_confidence`
      below `DEFAULT_CONFIDENCE_FLOOR`) — assert `review_reason == "LOW_CONFIDENCE"` and
      `review_reasons == {"LOW_CONFIDENCE"}`; confirm red
- [X] T004 [P] [US1] Test: a loan with a reconcile (`agree_categorical` or `agree_numeric`) check
      resolving one-side-absent — assert `review_reason == "SOURCE_INCOMPLETE"` and
      `review_reasons == {"SOURCE_INCOMPLETE"}`; confirm red
- [X] T005 [US1] Test: a loan with both a QC-phase failure AND a confidence-withheld pass together —
      assert `review_reasons == {"EXCEPTION", "LOW_CONFIDENCE"}` (multi-label, both present, neither
      suppresses the other); confirm red (depends on T002, T003 patterns existing first)
- [X] T006 [P] [US1] Test: a clean loan (no failures, nothing withheld, nothing incomplete) — assert
      `review_reasons == set()`; this one is expected to already PASS against today's engine trivially
      (an empty set requires no new attribute to exist as truthy) — included as the baseline negative
      case, not a red test

### Implementation for User Story 1

- [X] T007 [US1] In `p0/qc_engine/engine.py`, add `review_reason: Optional[str] = None` to the
      `CheckResult` dataclass (depends on T002–T005 existing as red tests)
- [X] T008 [US1] In `_eval_check`, immediately after the main `kind` dispatch (`if/elif` chain) and
      before the confidence-gate block, insert the generic tagging rule:
      `if res.phase == PHASE_QC and res.status in ("FAIL", "WARNING"): res.review_reason = "EXCEPTION"`
      `elif res.phase == PHASE_RECONCILE and res.status == "NEEDS_REVIEW": res.review_reason = "SOURCE_INCOMPLETE"`
      (single insertion point, not duplicated per check-kind — see plan.md's Structure Decision)
- [X] T009 [US1] In the existing confidence-gate block (the `if res.status == "PASS" and ...
      doc_confidence < confidence_floor:` block), add `res.review_reason = "LOW_CONFIDENCE"` alongside
      the existing `res.status = "NEEDS_REVIEW"` line
- [X] T010 [US1] Add `review_reasons` and `disposition` properties to `RunResult`:
      `review_reasons -> {r.review_reason for r in self.results if r.review_reason}`;
      `disposition -> "NEEDS_REVIEW" if self.review_reasons else "AUTO_CLEARED"`
- [X] T011 [US1] Run T002–T006 again; confirm all green

**Checkpoint**: Every check that needs review carries a structural, inspectable reason; a loan's full
set of reasons is computable. Independently valuable — does not require US2/US3 to be true.

---

## Phase 3: User Story 2 — FLAGs never contribute a reason tag (Priority: P1)

**Done when:**
- A reconcile `FLAG` (alone or in any combination) never produces a `review_reason`
- A loan with a `FLAG` and nothing else is `AUTO_CLEARED` with empty `review_reasons`
- A loan with a `FLAG` and a genuine QC failure tags only `"EXCEPTION"` — never a tag attributable to
  the `FLAG`

### Tests for User Story 2

- [X] T012 [P] [US2] Test: a loan with one genuine reconcile divergence (`FLAG`, constructed via
      `eval_synth.generator.assert_independently_constructed`, same independence-guard discipline
      `003c` used) and nothing else — assert `disposition == "AUTO_CLEARED"` and
      `review_reasons == set()` (depends on T007–T010 existing)
- [X] T013 [P] [US2] Test: a loan with multiple `FLAG`s (both `agree_categorical` and
      `agree_numeric`) and nothing else — assert still `AUTO_CLEARED`, still empty `review_reasons`
- [X] T014 [US2] Test: a loan with a `FLAG` **and** a genuine QC failure — assert
      `review_reasons == {"EXCEPTION"}` exactly (not `{"EXCEPTION", <anything-flag-related>}`)

**Checkpoint**: The two-step model's safety promise (Principle V) holds through the new tag
mechanism, not just the pre-existing `auto_cleared` boolean.

---

## Phase 4: User Story 3 — The tag vocabulary is genuinely open (Priority: P1)

**Done when:**
- A `review_reason` value the aggregation code has never seen before surfaces correctly in
  `review_reasons`, unmodified
- The same tag on two different checks in one loan surfaces once (set semantics, not a multiset)

### Tests for User Story 3

- [X] T015 [P] [US3] Test: manually construct a `CheckResult` (not via `_eval_check` — direct
      dataclass construction, simulating a hypothetical future check-kind) carrying
      `review_reason="FUTURE_TAG_NEVER_SEEN_BEFORE"`; assemble it into a `RunResult`; assert
      `review_reasons` contains that exact string and `disposition == "NEEDS_REVIEW"` — zero changes
      to `review_reasons`'s own implementation required to pass this (proves genericity, SC-004)
- [X] T016 [P] [US3] Test: two different `CheckResult`s on the same loan both carrying
      `review_reason="EXCEPTION"` (e.g. two independent QC failures) — assert `review_reasons`
      contains `"EXCEPTION"` exactly once (`len(review_reasons) == 1` for this tag), proving set
      semantics over list/multiset

---

## Phase 5: Polish & Cross-Cutting

- [X] T017 [P] Test (FR-006/SC-003, backward-compatibility): for every loan constructed across
      T002–T014, assert `auto_cleared is True` if and only if `disposition == "AUTO_CLEARED"` — no
      disagreement in either direction, across the full sample
- [X] T018 Run the full existing suite unmodified: `p0/tests/test_p0.py`,
      `p0/eval_synth/test_properties.py`, `p0/tests/test_fixture_generation.py` (000's suite),
      `p0/tests/test_predicate_archetypes.py`, `p0/tests/test_threshold_archetypes.py`,
      `p0/tests/test_reconcile_archetypes.py`, plus `p0/harness.py`'s 1000-run digest — confirm zero
      regression (SC-005)
- [X] T019 Add a post-hoc "Implementation Notes" section to `plan.md` recording: final task count,
      total new test count, before/after `harness.py` digest confirming SC-005, and confirmation that
      `CheckResult`/`RunResult` are the only modules touched

## Dependencies & Execution Order

- **T001** (setup) blocks all of Phase 2.
- **Phase 2 (US1, T002–T011)** is the MVP slice — the tagging mechanism itself. T002–T004, T006 are
  parallelizable `[P]` as red tests; implementation (T007–T010) is sequential (same file, same
  function); T011 confirms green.
- **Phase 3 (US2, T012–T014)** depends on Phase 2's implementation existing (T007–T010) — it proves a
  safety property of the same mechanism, not new mechanism.
- **Phase 4 (US3, T015–T016)** depends on T010 (`review_reasons`'s implementation) — proves it's
  generic by direct dataclass construction, not through `_eval_check` at all.
- **T017–T019** run last, after all user stories are complete.

## Parallel Example

```
# T002–T004, T006 (Phase 2, one reason-tag case each) can run together once T001 exists:
Task: "QC-phase FAIL/WARNING -> EXCEPTION tag, red test"
Task: "Confidence-gate downgrade -> LOW_CONFIDENCE tag, red test"
Task: "Reconcile one-side-absent -> SOURCE_INCOMPLETE tag, red test"
Task: "Clean loan -> empty review_reasons, baseline case"

# T012–T013 (Phase 3, FLAG-exclusion cases) can run together once T007-T010 exist:
Task: "Single FLAG, nothing else -> AUTO_CLEARED, empty reasons"
Task: "Multiple FLAGs, nothing else -> still AUTO_CLEARED, empty reasons"
```
