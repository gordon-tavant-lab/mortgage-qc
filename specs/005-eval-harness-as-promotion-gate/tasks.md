# Tasks: Eval Harness as Promotion Gate

**Input**: Design documents from `specs/005-eval-harness-as-promotion-gate/`
**Prerequisites**: plan.md, spec.md

**Tests**: Included — this project's constitution makes eval/regression-proof foundational
(Principle III), and this feature's entire purpose is proving a set of safety-critical behaviors
(hard block, coverage, regression) — SC-001 through SC-006 are the deliverable, not optional polish.

**Organization**: Tasks grouped by user story (spec.md P1/P1/P2/P2/P3), TDD-ordered within each
story where the story is proving a specific behavior change.

## Phase 1: Setup

- [ ] T001 Create `p0/eval_synth/scenario_construction.py` module skeleton (imports from
      `qc_engine.model`/`qc_engine.ruleset`/`qc_engine.engine`, loads `field_catalog.json`, module
      docstring per the existing `p0/eval_synth/generator.py` style) — no strategies implemented yet
- [ ] T002 [P] Create `p0/tests/test_scenario_construction.py` module skeleton
- [ ] T003 [P] Create `p0/tests/test_promotion_gate.py` module skeleton

---

## Phase 2: User Story 1 — Any compiled check gets an automatic constructed pass/fail scenario (Priority: P1) 🎯 MVP

**Goal**: Promote `score_drafts.py`'s `SCORERS` pattern into a real, reusable component covering all
6 live check kinds, `applies_if` preconditions, and two-field doc-vs-doc construction (spec.md
FR-001–004).

**Independent Test**: Feed a `Check` of each of the 6 kinds through the generalized constructor with
no field-specific mutation code; confirm pass-case/fail-case loans produce the expected verdict pair
via `qc_engine.engine.run`.

### Tests for User Story 1 ⚠️ (write first, confirm they FAIL before implementation)

- [ ] T004 [P] [US1] Test in `test_scenario_construction.py`: a `predicate`-kind `Check`
      (`is_true`/`is_present`) constructs a pass-case + fail-case loan that resolve `PASS`/`FAIL`
      via `qc_engine.engine.run` — ported from `score_drafts.py`'s `_score_predicate` logic, not a
      new algorithm (depends on T001)
- [ ] T005 [P] [US1] Test: a `ratio_threshold`-kind `Check` (both `ltv` and `dti`) constructs a
      pass-case + fail-case loan straddling `threshold` per `operator`, resolving `PASS`/`FAIL` —
      ported from `_score_ratio_threshold` (depends on T001)
- [ ] T006 [P] [US1] Test: an `agree_categorical`-kind `Check` constructs a pass-case (doc==system)
      + fail-case (doc!=system) loan, resolving `PASS`/`FLAG` — ported from `_score_agree_categorical`
      (depends on T001)
- [ ] T007 [P] [US1] Test: an `agree_numeric`-kind `Check` constructs a pass-case (within
      `tolerance`) + fail-case (beyond `tolerance`) loan, resolving `PASS`/`FLAG` — ported from
      `_score_agree_numeric` (depends on T001)
- [ ] T008 [P] [US1] **New coverage** (spec.md Gap 4): test an `agree_doc_categorical`-kind `Check`
      (`field_name` + `compare_field_name` both set) constructs a pass-case (two matching
      independently-set document values) + fail-case (two diverging document values) loan,
      resolving `PASS`/`FAIL` (QC phase, per `003d` — not `FLAG`) — confirms
      `SourceValue.sources{}` is never populated on either field (FR-004) (depends on T001)
- [ ] T009 [P] [US1] **New coverage** (spec.md Gap 4): same as T008 for `agree_doc_numeric`
      (numeric tolerance instead of categorical match) (depends on T001)
- [ ] T010 [P] [US1] Test: a `Check` carrying one `applies_if` precondition constructs a loan whose
      facts satisfy that precondition before the check's own pass/fail logic is evaluated — confirm
      the constructed fail-case actually resolves `FAIL`/`FLAG` (not `NOT_APPLICABLE`) (FR-003)
      (depends on T001)
- [ ] T011 [P] [US1] Test: a `Check` whose `kind` is not in the registry produces an explicit,
      structured construction-failure record (not a silent skip, not a raised exception that kills
      the whole run) (FR-002) (depends on T001)

### Implementation for User Story 1

- [ ] T012 [US1] In `scenario_construction.py`, implement `_construct_predicate` and
      `_construct_ratio_threshold`, porting `score_drafts.py::_score_predicate`/
      `_score_ratio_threshold` logic into loan-pair-returning form (not score-returning) (depends on
      T004, T005 existing as red tests)
- [ ] T013 [P] [US1] Implement `_construct_agree_categorical` and `_construct_agree_numeric`,
      porting `_score_agree_categorical`/`_score_agree_numeric` (depends on T006, T007)
- [ ] T014 [US1] Implement `_construct_agree_doc_categorical` and `_construct_agree_doc_numeric` —
      new strategies, no existing port available; construct two independent document-extracted
      `SourceValue`s (never populating `.sources{}`) per `003d`'s semantics (depends on T008, T009)
- [ ] T015 [US1] Implement the `applies_if`-precondition-setting helper: given a `Check.applies_if`
      list, set the constructed loan's `facts`/`fields` so every condition holds, before handing off
      to the kind-specific strategy (depends on T010)
- [ ] T016 [US1] Assemble `STRATEGIES: Dict[str, Callable]` registry (the generalized, 6-kind
      successor to `SCORERS`) and the public `construct_scenario(chk: Check) -> ConstructedScenario`
      entry point; unregistered kinds produce the structured failure record from T011 (depends on
      T012–T015)
- [ ] T017 [US1] Run T004–T011 again; confirm all green

**Checkpoint**: Generalized scenario construction covers all 6 live check kinds + `applies_if`. This
alone is independently valuable (proves the v0.6 amendment's core mechanism) even before COVERAGE/
GOLDEN/VOLUME wire it in.

---

## Phase 3: User Story 2 — Zero false-auto-clear is a hard block, not an advisory report (Priority: P1)

**Goal**: Make the existing `false_auto_clear_count == 0` check an enforced promotion block, not a
printed number (spec.md FR-006).

**Independent Test**: A candidate ruleset with a deliberately injected false-auto-clear defect
causes the gate to exit non-zero and report `promotion_decision: "BLOCK"`.

### Tests for User Story 2

- [ ] T018 [P] [US2] Test in `test_promotion_gate.py`: construct a candidate `Ruleset` with one
      check deliberately miswired to `PASS` a known-bad loan (an injected false-auto-clear); running
      `promotion_gate.py`'s entry function against it returns a non-zero exit code and
      `promotion_decision == "BLOCK"`, naming the specific check id + loan + expected-vs-actual
      verdict (depends on T003)
- [ ] T019 [P] [US2] Test: the same candidate ruleset with zero injected defects returns exit `0`
      and `promotion_decision == "PROMOTE"` (depends on T003)
- [ ] T020 [P] [US2] Test: re-running the same `BLOCK` case twice produces byte-identical
      `promotion_decision` + named-cases output both times (determinism of the gate itself) (depends
      on T003)

### Implementation for User Story 2

- [ ] T021 [US2] In `promotion_gate.py`, implement the top-level orchestration function:
      run GOLDEN + COVERAGE + VOLUME (initially VOLUME alone is wired via T001-era `generator.py`/
      `eval.py` reuse; GOLDEN/COVERAGE land fully in Phase 4), collect every false-auto-clear across
      all tiers, and set `promotion_decision = "BLOCK"` if the collected count is nonzero, else
      `"PROMOTE"` (depends on T018, T019 existing as red tests)
- [ ] T022 [US2] Wire the function's return value to a process exit code (`0`/non-zero) at the
      script's `if __name__ == "__main__"` entry point, mirroring `eval.py`'s existing exit-code
      convention (`eval.py:107`) (depends on T021)
- [ ] T023 [US2] Run T018–T020 again; confirm all green

**Checkpoint**: The Safety gate ("a single false-clear blocks the change") is now literally
enforced by a script's exit code, not just printed. Independently shippable even before GOLDEN/
COVERAGE tiers exist (VOLUME alone already proves this).

---

## Phase 4: User Story 3 — GOLDEN, COVERAGE, and VOLUME each answer a distinct question (Priority: P2)

**Goal**: Separate today's one blended population into three named, separately-reportable tiers
(spec.md FR-005).

**Independent Test**: Run the gate against a candidate ruleset; confirm three distinct metrics
(`golden.regressions`, `coverage.checks_covered/checks_total`, `volume.auto_clear_rate`) appear in
the artifact.

### Tests for User Story 3

- [ ] T024 [P] [US3] Test in a new `p0/tests/test_golden_set.py`: replaying an unchanged candidate
      ruleset against `golden_panel.py`'s fixed panel reports zero regressions and names the panel
      version (depends on T001)
- [ ] T025 [P] [US3] Test: replaying a candidate ruleset with one deliberately flipped check verdict
      (vs. the baseline ruleset) reports exactly that one flip (SC-004) (depends on T024)
- [ ] T026 [P] [US3] Test in a new `p0/tests/test_coverage_set.py`: running COVERAGE against a
      ruleset of N checks (mixing all 6 kinds) reports `checks_covered == N` when every kind has a
      registered strategy, and correctly decrements when one check's kind is deliberately
      unregistered (SC-002) (depends on T016)
- [ ] T027 [P] [US3] Test: running VOLUME (reusing `generator.py`/`eval.py`'s existing population)
      reports an `auto_clear_rate` field alongside the pre-existing `false_auto_clear_count` (SC-005)
      (depends on T001)

### Implementation for User Story 3

- [ ] T028 [P] [US3] Create `p0/fixtures/golden_panel.py`: a small, version-controlled panel seeded
      from `p0/fixtures/ruleset_defects.py`'s existing 25 known planted defects (spec.md
      Assumptions) — each entry a `(loan, expected_verdicts, panel_version)` tuple
- [ ] T029 [US3] Create `p0/eval_synth/golden_set.py`: replay logic against `golden_panel.py`,
      diffing candidate-vs-baseline verdicts, reporting flips (depends on T024, T025, T028)
- [ ] T030 [US3] Create `p0/eval_synth/coverage_set.py`: iterate every `Check` in a candidate
      `Ruleset`, call `scenario_construction.construct_scenario`, tally
      `checks_covered`/`checks_total`/construction failures (depends on T026, T016)
- [ ] T031 [US3] Extend VOLUME reporting (in `eval.py` or `promotion_gate.py`) with an
      `auto_clear_rate` metric computed from the existing generated population's verdict mix
      (depends on T027)
- [ ] T032 [US3] Wire `golden_set.py` + `coverage_set.py` + the extended VOLUME reporting into
      `promotion_gate.py`'s orchestration function from T021, replacing its VOLUME-only interim
      implementation with the full three-tier artifact (depends on T029, T030, T031)
- [ ] T033 [US3] Run T024–T027 again; confirm all green

**Checkpoint**: All three named tiers exist, each independently reportable, each feeding the same
hard-block decision from Phase 3.

---

## Phase 5: User Story 4 — Label-free metamorphic invariants run against any candidate ruleset (Priority: P2)

**Goal**: Generalize `test_properties.py`'s invariants to take a `Ruleset` parameter instead of the
hardcoded `demo_ruleset()` module constant (spec.md FR-008).

**Independent Test**: Run the invariant suite against two different rulesets (the existing demo one
and one containing an `agree_doc_categorical` check); confirm each invariant evaluates against the
ruleset it's actually given.

### Tests for User Story 4

- [ ] T034 [P] [US4] Test: the monotonicity invariant, called with an explicit `ratio_threshold`
      ruleset parameter (not the module-level `RULESET`), confirms `PASS → FAIL` only as
      `loan_amount` rises, for that ruleset's own check id
- [ ] T035 [P] [US4] Test: the monotonicity invariant, called against a ruleset with no
      `ratio_threshold` check at all, reports "not applicable" for that run rather than erroring or
      silently passing

### Implementation for User Story 4

- [ ] T036 [US4] Refactor `test_properties.py`'s invariant functions to accept a `ruleset: Ruleset`
      parameter, removing the module-level `RULESET = demo_ruleset()` hardcoding; existing callers
      (including `eval.py`) pass `demo_ruleset()` explicitly to preserve today's behavior unchanged
      (depends on T034, T035 existing as red tests)
- [ ] T037 [US4] Add the not-applicable reporting path for invariants whose relevant check kind is
      absent from the given ruleset (depends on T036)
- [ ] T038 [US4] Wire the generalized invariant suite into `promotion_gate.py`'s orchestration,
      called against the actual candidate ruleset under test (depends on T036, T037, T032)
- [ ] T039 [US4] Run T034–T035 again; confirm all green; run the full pre-existing
      `test_properties.py` suite unmodified-behavior-wise against `demo_ruleset()` to confirm no
      regression in the invariants' existing proven behavior

**Checkpoint**: The gate's label-free invariants are now genuinely reusable across every ruleset
version, not a second hardcoded artifact.

---

## Phase 6: User Story 5 — The harness absorbs real loans with no rework (Priority: P3)

**Goal**: Confirm the scorer's `(loan, expected_verdicts)` interface doesn't distinguish
synthetically-constructed scenarios from a future expert-labeled real loan (spec.md FR-010).

**Independent Test**: A constructed stand-in for `012`'s expected real-loan shape (provenance
`"expert-labeled"`) scores identically to a synthetic labeled loan, through the same function.

### Tests for User Story 5

- [ ] T040 [US5] Test: construct a `(loan, expected_verdicts)` pair tagged with provenance
      `"expert-labeled"` (no mutation-archetype metadata); confirm it scores through the same
      `score()`/gate-scoring path as a synthetic `LabeledLoan`, producing an identical result shape

### Implementation for User Story 5

- [ ] T041 [US5] Confirm (and adjust if needed) that the scorer function's signature accepts any
      `(CanonicalLoan, Dict[str, str], Dict[str, Any])` triple regardless of what the provenance
      dict contains — no code branch keyed on "how was this loan produced" (depends on T040)

**Checkpoint**: `012`, when it lands, is a new loan *source* feeding the existing scorer — not a
second harness.

---

## Phase 7: Polish & Cross-Cutting

- [ ] T042 Run the full existing suite unmodified: `p0/tests/test_p0.py`,
      `p0/eval_synth/test_properties.py` (both its old demo-ruleset-only call sites and the new
      generalized ones), `p0/harness.py` (bit-exact digest) — confirm zero regression (SC-006);
      record the before/after digest for plan.md's post-hoc note
- [ ] T043 [P] Document `promotion_gate.py`'s CLI usage (args, exit-code contract, artifact shape)
      in a module docstring, mirroring `eval.py`'s existing docstring convention — the interface a
      future CI wiring task or a Makefile/pre-commit hook would invoke
- [ ] T044 Add a post-hoc "Implementation Notes" section to `plan.md` recording: final task count,
      any amendment discovered during implementation, the before/after `harness.py` digest (SC-006),
      and the real coverage-fraction number SC-002 measured against a real compiled ruleset

## Dependencies & Execution Order

- **Phase 1 (Setup, T001–T003)** blocks all of Phase 2.
- **Phase 2 (US1, T004–T017)** is the foundational MVP slice — every later phase's construction
  needs (COVERAGE in Phase 4, the injected-defect fixtures in Phase 3) depend on
  `scenario_construction.py` existing (T016).
- **Phase 3 (US2, T018–T023)** depends on Phase 2 only loosely (it can prove the hard-block
  contract using VOLUME alone, via existing `generator.py`/`eval.py`); COVERAGE-sourced
  false-auto-clears are added when Phase 4 lands.
- **Phase 4 (US3, T024–T033)** depends on Phase 2 (T016, for COVERAGE) and Phase 3 (T021, the
  orchestration function it extends).
- **Phase 5 (US4, T034–T039)** depends on Phase 4's orchestration (T032) to wire the generalized
  invariants into the same gate run.
- **Phase 6 (US5, T040–T041)** has no hard dependency on Phases 2–5 — it can run any time after
  Phase 1, but is sequenced last as the lowest-priority (P3) confirmation.
- **T042–T044** run last, after all user stories are complete.

## Parallel Example

```
# T004–T011 (Phase 2, one check-kind or precondition case each) can run together once T001 exists:
Task: "predicate construction test in test_scenario_construction.py"
Task: "ratio_threshold construction test in test_scenario_construction.py"
Task: "agree_categorical construction test in test_scenario_construction.py"
Task: "agree_numeric construction test in test_scenario_construction.py"
Task: "agree_doc_categorical construction test in test_scenario_construction.py"
Task: "agree_doc_numeric construction test in test_scenario_construction.py"
Task: "applies_if precondition test in test_scenario_construction.py"
```
