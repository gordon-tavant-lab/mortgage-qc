# Tasks: Ratio/Threshold Check Engine

**Input**: Design documents from `specs/003b-engine-ratio-threshold-checks/`
**Prerequisites**: plan.md, spec.md

**Tests**: Included — this project's constitution makes eval/regression-proof foundational
(Principle III); spec.md's SC-006 is an explicit zero-regression gate, and SC-001–005 are the
correctness/safety proof this feature exists to produce, not optional polish.

**Organization**: Tasks grouped by user story (spec.md P1/P1/P2), TDD-ordered (tests before the fix
they pin down), per the constitution's rule that each slice ships with its own proof.

## Phase 1: Setup

- [x] T001 Create `p0/tests/test_threshold_archetypes.py` module skeleton (imports from
      `qc_engine.engine`/`qc_engine.model`/`qc_engine.ruleset`/`qc_engine.money`, module docstring
      per the existing `p0/tests/test_predicate_archetypes.py` style) — no test bodies yet

---

## Phase 2: User Story 1 — `field_value` mode closes the vocabulary gap (Priority: P1) 🎯 MVP

**Goal**: Close the concrete `002a`-carried gap — a `ratio_threshold` check MUST support a
single-field numeric floor/ceiling (`ratio="field_value"`) without forcing it through LTV/DTI
(spec.md FR-001/002/004).

**Independent Test**: Construct a loan with a numeric field below an authored floor; confirm a
`field_value`-mode check reports `FAIL`. At/above floor reports `PASS`. Missing value reports
`NOT_APPLICABLE`.

### Tests for User Story 1 ⚠️ (write first, confirm they FAIL against today's engine before touching engine.py)

- [x] T002 [P] [US1] Test in `p0/tests/test_p0.py`: a `ratio_threshold` check with
      `ratio="field_value"`, `field_name="credit_score"`, `threshold="500"`, `operator=">="`
      against `SourceValue(doc=480)` — confirm it currently raises `ValueError("unknown ratio
      'field_value'")`; write the test asserting the *correct* target behavior (`FAIL`); confirm it
      fails against today's `engine.py` (red)
- [x] T003 [P] [US1] Test in `p0/tests/test_p0.py`: the same check against `SourceValue(doc=620)`
      asserting `PASS`; confirm it fails (raises) against today's `engine.py` (red)
- [x] T004 [P] [US1] Test in `p0/tests/test_p0.py`: the same check against `SourceValue(doc=None)`
      asserting `NOT_APPLICABLE`; confirm it fails (raises) against today's `engine.py` (red)
- [x] T005 [P] [US1] Regression test in `p0/tests/test_p0.py`: the pre-existing `ltv`/`dti` cases
      (`chk-ltv-max`-style, `field_name=""`) are unchanged — reuse `test_ltv_boundary_exact`-style
      assertions and confirm they already pass against today's `engine.py` (they're not part of the
      gap — this task locks them as the "don't break this" boundary before the fix touches the same
      function)
- [x] T006 [P] [US1] Test in `p0/tests/test_p0.py`: confirm the dead
      `res.threshold = chk.threshold if hasattr(res, "threshold") else None` line is inert today —
      assert `CheckResult.to_dict()` for an existing `ltv` check contains no `"threshold"` key
      (only `"tolerance"`) both before and after this feature's change (regression proof for FR-004,
      not a red/green test — this line's removal must be observably a no-op)

### Implementation for User Story 1

- [x] T007 [US1] In `p0/qc_engine/engine.py`'s `_eval_check`, inside the `kind == "ratio_threshold"`
      branch, add `elif chk.ratio == "field_value":` before the `else: raise ValueError(...)`: read
      `sv.doc` (the field's truth value, already resolved at the top of `_eval_check` via
      `loan.get(chk.field_name)`); if `None`, set `res.status = "NOT_APPLICABLE"` with an
      explanatory message and `return res` early (mirroring the existing `ltv`/`dti`
      missing-facts pattern); otherwise set `value = M.to_decimal(sv.doc)` (no `.quantize()` — a raw
      field value has no policy-mandated rounding scale) and `res.inputs = {chk.field_name: sv.doc}`,
      then fall through to the existing `thr = M.to_decimal(chk.threshold)` / operator-comparison /
      `res.compared_value` / `res.tolerance` code shared with `ltv`/`dti` (depends on T002–T006
      existing as red tests)
- [x] T008 [US1] In the same function, remove the dead
      `res.threshold = chk.threshold if hasattr(res, "threshold") else None` line entirely (FR-004);
      the audit-relevant value continues to be carried by the pre-existing
      `res.tolerance = chk.threshold` assignment two lines later
- [x] T009 [US1] Run T002–T006 again; confirm all green — the fix is exactly the new `elif` branch
      (T007) plus the dead-line removal (T008), nothing else changed

**Checkpoint**: The concrete `002a`-carried vocabulary gap is closed and pinned by regression tests.
This alone is independently shippable — it does not require US2/US3 to be valuable.

---

## Phase 3: User Story 2 — Engine proven correct across the real THRESHOLD archetype set (Priority: P1)

**Goal**: Prove `ltv`/`dti`/`field_value` evaluate correctly at representative scale — including the
exact real `ratio_threshold-00` credit-score-floor row `002a` sampled — not just the demo's one
check (spec.md FR-005/006).

**Independent Test**: For LTV, DTI, and `ratio_threshold-00`, construct pass-case/fail-case/boundary
loans and confirm the engine produces the correct verdict.

### Tests for User Story 2

- [x] T010 [US2] In `p0/tests/test_threshold_archetypes.py`, build a small fixture helper that reads
      `p0/experiment_002a/artifacts/sampled_rows.json` and exposes the real `ratio_threshold-00` row
      (`defect_text`: "Sect 203(h)-Borr did not have a minimum credit score of 500...") — no
      fabricated condition text, reuses what `002a` already sampled from the real AMQ workbook
      (depends on T001)
- [x] T011 [P] [US2] Test: LTV at, above, and exactly on an authored threshold (`threshold="95"`,
      `operator="<="`) — fail-case (`loan_amount`/`property_value` implying LTV > 95%), pass-case
      (< 95%), and exact-boundary case (= 95%, `PASS` under `<=`); assert the correct verdict for all
      three, in Decimal, matching `money.py::ltv_percent`'s pinned `ROUND_HALF_EVEN` policy (depends
      on T001)
- [x] T012 [P] [US2] Test: DTI at and above an authored threshold (`threshold="45"`,
      `operator="<="`) — fail-case and pass-case; assert the correct verdict for both (depends on
      T001)
- [x] T013 [P] [US2] Test: for the `ratio_threshold-00` row (T010), construct a `field_value` `Check`
      (`field_name="credit_score"`, `threshold="500"`, `operator=">="`) + a below-floor fail-case loan
      (`doc=480`) and an at/above-floor pass-case loan (`doc=500`); assert `FAIL`/`PASS` respectively
      (depends on T007, T010)
- [x] T014 [US2] Test (SC-003): assemble every fail-case loan from T011–T013 into one `RunResult` per
      loan against a `Ruleset` containing that loan's check; assert `RunResult.auto_cleared` is
      `False` for every one — zero false-auto-clears across the full threshold batch (depends on
      T011–T013)

**Checkpoint**: LTV, DTI, and the new `field_value` mode are all proven correct at representative
scale, including an exact-boundary case and an explicit zero-false-auto-clear gate. Builds on US1's
fix (T007) — the `field_value` fail-case (T013) is only reachable once T007 lands.

---

## Phase 4: User Story 3 — Confidence gate correctly reaches `field_value` checks (Priority: P2)

**Goal**: Confirm the existing confidence gate (ruling #8) correctly applies to `field_value`
checks — the first `ratio_threshold` sub-kind structurally able to reach it, since `ltv`/`dti`
checks read `loan.facts` (never a real `SourceValue`) and so never carry a `doc_confidence` (spec.md
FR-007).

**Independent Test**: A pass-case `field_value` check with `doc_confidence` below floor downgrades to
`NEEDS_REVIEW`; at/above floor it does not.

### Tests for User Story 3

- [x] T015 [P] [US3] Test in `p0/tests/test_threshold_archetypes.py`: reusing the pass-case loan from
      T013 (`field_value`, `doc=620`), set `doc_confidence=0.5` (below
      `DEFAULT_CONFIDENCE_FLOOR=0.80`); assert the result is `NEEDS_REVIEW`, not `PASS` (depends on
      T013)
- [x] T016 [P] [US3] Test: the same loan with `doc_confidence=0.95` (at/above floor); assert clean
      `PASS` with no review flag (regression confirming the gate isn't over-triggering) (depends on
      T013)
- [x] T017 [US3] Test (regression, documents the structural gap this feature closes): confirm an
      `ltv`-kind check's `CheckResult.doc_confidence` is `None` even when the loan's `credit_score`
      field carries a real confidence — proving `ltv`/`dti` structurally cannot reach the confidence
      gate today (not a defect this feature is scoped to fix; recorded so the difference from
      `field_value`'s behavior in T015/T016 is intentional, not an inconsistency)

**Checkpoint**: The confidence gate is proven, not assumed, to correctly reach the new `field_value`
code path.

---

## Phase 5: Polish & Cross-Cutting

- [x] T018 Run the full existing suite unmodified: `p0/tests/test_p0.py`,
      `p0/eval_synth/test_properties.py`, `p0/harness.py` (1000-run bit-exact digest) — confirm zero
      regression (SC-006); record the digest for the plan.md post-hoc implementation note
- [x] T019 Add a post-hoc "Implementation Notes" section to `plan.md` (mirroring
      `001a`/`001b`/`002b`/`003a`'s own post-implementation notes) recording: final task count, any
      amendment discovered during implementation, and the before/after `harness.py` digest confirming
      SC-006

## Dependencies & Execution Order

- **T001** (setup) blocks all of Phase 3.
- **Phase 2 (US1, T002–T009)** is the MVP slice — independently shippable, no dependency on
  Phase 3/4.
- **Phase 3 (US2, T010–T014)** depends on **T007** (US1's new branch) for the `field_value` fail-case
  to be reachable; T011–T013 are parallelizable `[P]` against each other once T001/T010 exist.
- **Phase 4 (US3, T015–T017)** depends on Phase 3's pass-case fixture (T013) existing first.
- **T018–T019** run last, after all user stories are complete.

## Parallel Example

```
# T011–T013 (Phase 3, one ratio-kind each) can run together once T001/T010 exist:
Task: "LTV boundary coverage in test_threshold_archetypes.py"
Task: "DTI coverage in test_threshold_archetypes.py"
Task: "field_value (ratio_threshold-00) coverage in test_threshold_archetypes.py"
```
