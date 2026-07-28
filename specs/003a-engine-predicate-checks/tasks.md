# Tasks: Predicate Check Engine

**Input**: Design documents from `specs/003a-engine-predicate-checks/`
**Prerequisites**: plan.md, spec.md

**Tests**: Included — this project's constitution makes eval/regression-proof foundational
(Principle III); spec.md's SC-005 is an explicit zero-regression gate, and SC-001–004 are the
correctness/safety proof this feature exists to produce, not optional polish.

**Organization**: Tasks grouped by user story (spec.md P1/P1/P2), TDD-ordered (tests before the fix
they pin down), per the constitution's rule that each slice ships with its own proof.

## Phase 1: Setup

- [x] T001 Create `p0/tests/test_predicate_archetypes.py` module skeleton (imports from
      `qc_engine.engine`/`qc_engine.model`/`qc_engine.ruleset`, module docstring per the existing
      `p0/tests/test_p0.py` style) — no test bodies yet

---

## Phase 2: User Story 1 — Missing truth value correctly FAILs a predicate check (Priority: P1) 🎯 MVP

**Goal**: Fix the concrete `002a`-carried bug — `doc=None` on a predicate check must produce `FAIL`,
not `NOT_APPLICABLE` (spec.md FR-001/002/003).

**Independent Test**: Construct a loan with `doc=None` on a field carrying an `is_present` check and
one carrying an `is_true` check; confirm both report `FAIL`.

### Tests for User Story 1 ⚠️ (write first, confirm they FAIL against today's engine before touching engine.py)

- [x] T002 [P] [US1] Test in `p0/tests/test_p0.py`: an `is_present`-kind check against
      `SourceValue(doc=None)` currently reports `NOT_APPLICABLE` — write the test asserting the
      *correct* target behavior (`FAIL`); confirm it fails against today's `engine.py` (red)
- [x] T003 [P] [US1] Test in `p0/tests/test_p0.py`: an `is_true`-kind check against
      `SourceValue(doc=None)` asserting `FAIL`; confirm it fails against today's `engine.py` (red)
- [x] T004 [P] [US1] Regression test in `p0/tests/test_p0.py`: the pre-existing, already-correct
      non-`None` cases are unchanged — `is_present` with `doc=""` → `FAIL`, `doc="present-value"` →
      `PASS`; `is_true` with `doc=False` → `FAIL`, `doc=True` → `PASS`. Confirm these already pass
      against today's `engine.py` (they're not part of the bug — this task locks them as the
      "don't break this" boundary before the fix touches the same function)

### Implementation for User Story 1

- [x] T005 [US1] In `p0/qc_engine/engine.py`'s `_eval_check`, remove the blanket
      `if sv.doc is None: res.status = "NOT_APPLICABLE"; ...; return res` early-return inside the
      `kind == "predicate"` branch. Let `is_true`'s (`sv.doc is True`) and `is_present`'s
      (`sv.doc is not None and str(sv.doc).strip() != ""`) existing logic run unconditionally —
      both already evaluate to the correct `FAIL` when `sv.doc is None`, so no new branching logic
      is needed, only the removal of the branch that currently pre-empts it (depends on T002–T004
      existing as red tests)
- [x] T006 [US1] Run T002–T004 again; confirm all green — the fix is exactly the removal in T005,
      nothing else changed

**Checkpoint**: The concrete `002a`-carried bug is fixed and pinned by regression tests. This alone
is independently shippable — it does not require US2/US3 to be valuable.

---

## Phase 3: User Story 2 — Engine proven correct across the real predicate archetype set (Priority: P1)

**Goal**: Prove `is_true`/`is_present` evaluate correctly at the scale of the 5 real archetypes
(`MISSING`/`UNSIGNED`/`EXPIRED`/`INCOMPLETE`/`POLICY`, 2,937 conditions), not just the demo's one
check (spec.md FR-004/005).

**Independent Test**: For each archetype's representative sample, construct pass-case/fail-case
loans and confirm the engine produces the taxonomy's declared `expected_verdict`.

### Tests for User Story 2

- [x] T007 [US2] In `p0/tests/test_predicate_archetypes.py`, build a small fixture helper that reads
      `p0/eval_synth/taxonomy.json`'s `archetypes` list and, for each of `MISSING`/`UNSIGNED`/
      `INCOMPLETE`/`POLICY`/`EXPIRED`, exposes its 3 existing `examples` strings (no fabricated
      conditions — reuses what `taxonomy.json` already carries) (depends on T001)
- [x] T008 [P] [US2] Test: for each `MISSING`-archetype example, construct an `is_present` `Check`
      + a fail-case loan (`doc=None`, the archetype's own defect) and a pass-case loan
      (`doc="present-value"`); assert `FAIL`/`PASS` respectively for all 3 examples (depends on T007;
      depends on T005 for the fail-case to be reachable at all)
- [x] T009 [P] [US2] Test: for each `UNSIGNED`-archetype example, construct an `is_true` `Check` +
      fail-case (`doc=False`) and pass-case (`doc=True`) loans; assert `FAIL`/`PASS` (depends on
      T007)
- [x] T010 [P] [US2] Test: for each `INCOMPLETE`-archetype example, construct an `is_true` `Check` +
      fail-case (`doc=False`) and pass-case (`doc=True`) loans; assert `FAIL`/`PASS` (depends on
      T007)
- [x] T011 [P] [US2] Test: for each `POLICY`-archetype example, construct an `is_true` `Check` +
      fail-case (`doc=False`) and pass-case (`doc=True`) loans; assert `FAIL`/`PASS` (depends on
      T007)
- [x] T012 [P] [US2] Test: for each `EXPIRED`-archetype example, construct an `is_true` `Check`
      modeling a pre-computed staleness boolean (e.g. `field_name="disclosure_timely"`) + fail-case
      (`doc=False`, "not provided timely") and pass-case (`doc=True`) loans; assert `FAIL`/`PASS` —
      confirms the engine needs no date-arithmetic logic of its own for this archetype (spec.md
      FR-007, Assumptions) (depends on T007)
- [x] T013 [US2] Test (SC-003): assemble every fail-case loan from T008–T012 into one `RunResult`
      per loan against a `Ruleset` containing that loan's check; assert `RunResult.auto_cleared` is
      `False` for every one — zero false-auto-clears across the full archetype batch (depends on
      T008–T012)

**Checkpoint**: All 5 predicate archetypes are proven correct at representative scale, with an
explicit zero-false-auto-clear gate. Builds on US1's fix (T005) — the `MISSING` archetype's fail-case
(T008) is only reachable once T005 lands.

---

## Phase 4: User Story 3 — Confidence gate holds at archetype scale (Priority: P2)

**Goal**: Confirm the existing confidence gate (ruling #8) still correctly withholds auto-clear for
predicate checks once exercised beyond the single demo check (spec.md FR-006).

**Independent Test**: A pass-case predicate check with `doc_confidence` below floor downgrades to
`NEEDS_REVIEW`; at/above floor it does not.

### Tests for User Story 3

- [x] T014 [P] [US3] Test in `p0/tests/test_predicate_archetypes.py`: reusing 2-3 pass-case loans
      from T009–T011 (`UNSIGNED`/`INCOMPLETE`/`POLICY`, `is_true`), set `doc_confidence=0.5` (below
      `DEFAULT_CONFIDENCE_FLOOR=0.80`); assert each result is `NEEDS_REVIEW`, not `PASS` (depends on
      T009–T011)
- [x] T015 [P] [US3] Test: the same loans with `doc_confidence=0.95` (at/above floor); assert clean
      `PASS` with no review flag (regression confirming the gate isn't over-triggering) (depends on
      T009–T011)

**Checkpoint**: The confidence gate is proven, not assumed, to generalize across the real archetype
set.

---

## Phase 5: Polish & Cross-Cutting

- [x] T016 Run the full existing suite unmodified: `p0/tests/test_p0.py`,
      `p0/eval_synth/test_properties.py`, `p0/harness.py` (1000-run bit-exact digest) — confirm zero
      regression (SC-005); record the digest for the plan.md post-hoc implementation note
- [x] T017 Add a post-hoc "Implementation Notes" section to `plan.md` (mirroring `001a`/`001b`/`002b`'s
      own post-implementation notes) recording: final task count, any amendment discovered during
      implementation, and the before/after `harness.py` digest confirming SC-005

## Dependencies & Execution Order

- **T001** (setup) blocks all of Phase 3.
- **Phase 2 (US1, T002–T006)** is the MVP slice — independently shippable, no dependency on
  Phase 3/4.
- **Phase 3 (US2, T007–T013)** depends on **T005** (US1's fix) for the `MISSING` archetype's
  fail-case to be reachable; T008–T012 are parallelizable `[P]` against each other once T007 exists.
- **Phase 4 (US3, T014–T015)** depends on Phase 3's pass-case fixtures (T009–T011) existing first.
- **T016–T017** run last, after all user stories are complete.

## Parallel Example

```
# T008–T012 (Phase 3, one archetype each) can run together once T007 exists:
Task: "MISSING archetype pass/fail coverage in test_predicate_archetypes.py"
Task: "UNSIGNED archetype pass/fail coverage in test_predicate_archetypes.py"
Task: "INCOMPLETE archetype pass/fail coverage in test_predicate_archetypes.py"
Task: "POLICY archetype pass/fail coverage in test_predicate_archetypes.py"
Task: "EXPIRED archetype pass/fail coverage in test_predicate_archetypes.py"
```
