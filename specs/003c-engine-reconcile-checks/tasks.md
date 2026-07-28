# Tasks: Reconcile Check Engine

**Input**: Design documents from `specs/003c-engine-reconcile-checks/`
**Prerequisites**: plan.md, spec.md

**Tests**: Included — this project's constitution makes eval/regression-proof foundational
(Principle III); spec.md's SC-006 is an explicit zero-regression gate, and SC-001–004 are the
correctness/safety proof this feature exists to produce, not optional polish.

**Note on TDD ordering**: unlike `003a`/`003b`, this feature fixes no bug and closes no vocabulary
gap — `agree_categorical`/`agree_numeric` are already fully implemented (proven generically by
`001b`). Every test below is a **proof test**, expected to pass against today's `engine.py`
immediately, not a red-then-green fix. No task instructs writing a test that is expected to fail.

**Organization**: Tasks grouped by user story (spec.md P1/P1), per the constitution's rule that each
slice ships with its own proof.

## Phase 1: Setup

- [X] T001 Create `p0/tests/test_reconcile_archetypes.py` module skeleton (imports from
      `qc_engine`/`qc_engine.model`/`qc_engine.ruleset`, module docstring per the existing
      `p0/tests/test_threshold_archetypes.py` style, describing this feature's scope and its
      explicit doc-vs-doc exclusion) — no test bodies yet
      → Done when: the file imports cleanly (`python -m pytest p0/tests/test_reconcile_archetypes.py --collect-only` exits 0) with zero tests collected

---

## Phase 2: User Story 1 — Reconcile mechanism proven correct at real archetype scale (Priority: P1) 🎯 MVP

**Done when:**
- The real `reconcile-01` (SSN discrepancy) condition produces `PASS` when doc/system agree and
  `FLAG` (never `FAIL`) when they genuinely diverge
- Representative `agree_categorical` and `agree_numeric` pairs all produce the correct verdict
  (agreement, genuine divergence, one-side-absent → `NEEDS_REVIEW`, both-absent → `NOT_APPLICABLE`)

**Independent Test**: Construct a loan with independently-populated doc (truth) and system (`los`/
`mismo`) values for an SSN-shaped field; build one agreeing case and one genuinely-diverging case
(independence-guard verified); confirm the engine produces the correct verdict in both directions,
plus a representative categorical and numeric pair.

- [X] T002 [US1] In `p0/tests/test_reconcile_archetypes.py`, build a fixture helper that reads
      `p0/experiment_002a/artifacts/sampled_rows.json` and exposes the real `reconcile-01` row
      (`defect_text`: "SFC 162 not used where there was a discrepancy identified with the Social
      Security number") — no fabricated condition, same discipline `003b`'s `test_threshold_archetypes.py`
      already applies to `ratio_threshold-00` (depends on T001)
      → Done when: the helper returns the row's `row_id`, `defect_text`, and `archetype_id` exactly as stored in `sampled_rows.json`
- [X] T003 [P] [US1] Test: an `agree_categorical` check (`normalizer="ssn_last4"`, mirroring
      `demo_ruleset()`'s existing `chk-borrower-ssn`) against a loan whose doc (truth) and system
      (`los`) SSN values agree after normalization — assert `PASS` (depends on T001)
      → Done when: the test passes against today's engine.py unmodified
- [X] T004 [P] [US1] Test: the same check against a loan whose doc and system SSN values genuinely
      diverge, constructed via `eval_synth.generator.assert_independently_constructed` (the same
      independence-guard discipline `001b`'s own tests apply — no mutation that "diverges" by
      leaving `sources` unchanged) — assert `FLAG` with `severity="INFO"`, never `FAIL` (depends on
      T001)
      → Done when: the test passes against today's engine.py unmodified, and fails loudly (raises) if the fixture's divergence is constructed by only changing `truth` without changing `sources`
- [X] T005 [P] [US1] Test: a representative `agree_numeric` pair (a rate or dollar amount, mirroring
      `demo_ruleset()`'s `chk-note-rate`/`chk-principal`) at, within, and outside an authored
      tolerance — assert the correct verdict for all three using `Decimal`/`within_tolerance`, no
      float touching the comparison (depends on T001)
      → Done when: the test passes against today's engine.py unmodified
- [X] T006 [P] [US1] Test: one side absent (doc present, system absent — or the reverse) resolves
      `NEEDS_REVIEW`; both sides absent resolves `NOT_APPLICABLE` — regression proof at this
      feature's own scale, not just `001b`'s narrower coverage (depends on T001)
      → Done when: the test passes against today's engine.py unmodified

**Checkpoint**: The reconcile mechanism (`agree_categorical`/`agree_numeric`) is proven correct at
real archetype scale, anchored on the one real, structurally-clean, doc-vs-system sampled condition.
This alone is independently valuable — it does not require US2 to be true.

---

## Phase 3: User Story 2 — FLAG-vs-FAIL separation holds safely at scale, in both directions (Priority: P1)

**Done when:**
- A genuine reconcile divergence with no QC failure produces `flags` non-empty, `qc_failures` empty,
  `auto_cleared=True`
- A genuine QC failure with no reconcile divergence produces `qc_failures` non-empty, `flags` empty,
  `auto_cleared=False`
- A loan with both surfaces each in its correct, separate bucket simultaneously
- Zero instances, across the full US1 constructed sample, of a reconcile `FLAG` leaking into
  `qc_failures`/blocking `auto_cleared`, or a QC failure being misclassified as a `FLAG`

**Independent Test**: Build a mixed ruleset spanning `agree_categorical`, `agree_numeric`,
`predicate`, and `ratio_threshold` checks against one loan with both a genuine reconcile divergence
and a genuine QC failure; confirm each surfaces only in its correct bucket and `auto_cleared` is
`False` (blocked by the QC failure, not the FLAG).

- [X] T007 [US2] In `p0/tests/test_reconcile_archetypes.py`, build a mixed `Ruleset` containing one
      `agree_categorical` check (reusing T004's divergent SSN fixture) and one `predicate` check
      (`is_true`, against an absent/False field — a genuine, unrelated QC failure) — the fixture
      construction task other US2 tasks depend on (depends on T004)
      → Done when: the mixed Ruleset passes `catalog.validate_referential_integrity` cleanly
- [X] T008 [P] [US2] Test: a loan with the reconcile divergence only (predicate check field
      genuinely present/true) — assert `flags` non-empty, `qc_failures` empty, `auto_cleared=True`
      (depends on T007)
      → Done when: the test passes against today's engine.py unmodified
- [X] T009 [P] [US2] Test: a loan with the QC failure only (SSN fields agree) — assert
      `qc_failures` non-empty, `flags` empty, `auto_cleared=False` (depends on T007)
      → Done when: the test passes against today's engine.py unmodified
- [X] T010 [P] [US2] Test: a loan with both the divergence and the QC failure — assert both surface
      simultaneously in their correct separate buckets and `auto_cleared=False` (the QC failure
      alone is sufficient to block it) (depends on T007)
      → Done when: the test passes against today's engine.py unmodified
- [X] T011 [US2] Test (SC-003/004 at scale): assemble every genuine-divergence case from US1
      (T004–T006) into `RunResult`s; assert zero instances of a reconcile `FLAG` appearing in
      `qc_failures`/`exceptions` or blocking `auto_cleared` on its own, across the full batch
      (depends on T004, T005, T006, T008–T010)
      → Done when: the test passes against today's engine.py unmodified with zero exceptions found in the full batch

**Checkpoint**: The single highest-stakes property specific to this check-kind — safe, correct
partitioning of FLAG vs FAIL — is proven at scale, in both directions, not just spot-checked by the
demo's one mixed run.

---

## Phase 4: Polish & Cross-Cutting

- [X] T012 Run the full existing suite unmodified: `p0/tests/test_p0.py`, `p0/eval_synth/test_properties.py`,
      `p0/tests/test_fixture_generation.py` (000's suite, includes `chk-def-fha-case-number`),
      `p0/tests/test_predicate_archetypes.py`, `p0/tests/test_threshold_archetypes.py`, and
      `p0/harness.py` (1000-run bit-exact digest) — confirm zero regression (SC-006)
      → Done when: every test file passes with zero failures and `p0/harness.py`'s digest matches `8510a0a8b4b6996e047fc8534e094394ba72aae396305b0d2ecad3d6924634db` exactly
- [X] T013 Add a post-hoc "Implementation Notes" section to `plan.md` (mirroring
      `001a`/`001b`/`002b`/`003a`/`003b`'s own post-implementation notes) recording: final task
      count, total test count added, the before/after `harness.py` digest confirming SC-006, and any
      amendment discovered while writing the proof tests
      → Done when: plan.md contains an "Implementation Notes" section with the confirmed digest value

## Dependencies & Execution Order

- **T001** (setup) blocks everything else.
- **Phase 2 (US1, T002–T006)** is the MVP slice — independently valuable, no dependency on Phase 3.
  T003–T006 are parallelizable `[P]` against each other once T001/T002 exist.
- **Phase 3 (US2, T007–T011)** depends on T004's divergent SSN fixture (reused, not duplicated) and
  on T005/T006 existing before T011's full-batch assertion. T008–T010 are parallelizable `[P]`
  against each other once T007 exists.
- **T012–T013** run last, after both user stories are complete.

## Parallel Example

```
# T003–T006 (Phase 2, one agree_* case each) can run together once T001/T002 exist:
Task: "SSN agreement case (reconcile-01) in test_reconcile_archetypes.py"
Task: "SSN genuine divergence case in test_reconcile_archetypes.py"
Task: "agree_numeric representative pair in test_reconcile_archetypes.py"
Task: "one-side-absent / both-absent regression in test_reconcile_archetypes.py"

# T008–T010 (Phase 3, one partition scenario each) can run together once T007 exists:
Task: "divergence-only auto_cleared=True case"
Task: "QC-failure-only auto_cleared=False case"
Task: "both-present simultaneous-buckets case"
```
