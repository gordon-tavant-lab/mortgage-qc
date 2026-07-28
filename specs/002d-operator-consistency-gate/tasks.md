# Tasks: Operator-Direction Consistency Gate

**Input**: Design documents from `specs/002d-operator-consistency-gate/`
**Prerequisites**: plan.md, spec.md

**Tests**: Included — SC-001/002 (true-positive floor + false-positive rate) are the correctness
proof this feature exists to produce.

**Organization**: Tasks grouped by user story.

## Phase 1: Setup

- [ ] T001 Create `p0/tests/test_operator_consistency.py` module skeleton (imports, docstring
      describing scope: the 45-check true-positive floor + false-positive measurement against correct
      checks) — no test bodies yet
      → Done when: `pytest p0/tests/test_operator_consistency.py --collect-only` exits 0 with zero
      tests collected

---

## Phase 2: User Story 1 — New compiles don't invert the operator (Priority: P1) 🎯 MVP

**Done when:** `SYSTEM_PROMPT` states the PASS-condition convention explicitly with inversion
few-shot examples; a recompile of known FAIL-framed rows produces the correct operator.

**Independent Test**: Recompile a small sample of known FAIL-framed source rows (including the two
confirmed-bad checks' original rows) with the updated prompt; confirm the emitted operator now
matches the PASS condition.

- [ ] T002 [US1] Extend `compile_llm.py`'s `SYSTEM_PROMPT`: add an explicit statement that
      `operator`/`threshold` must always express the PASS condition, with 2+ few-shot examples
      inverting a FAIL-framed source sentence (e.g. "exceeds 80%" → `operator: "<="`)
- [ ] T003 [US1] Recompile the two confirmed-bad checks' original source rows (locate via
      `result/rules/post_closing_only_provenance.json`) with the updated prompt; confirm the emitted
      operator is now `<=` matching `message_pass` (manual/scripted verification, not a pytest case —
      this exercises the real Bedrock call) (depends on T002)
- [ ] T004 [US1] Recompile a small sample of already-correctly-compiled PASS-framed rows with the
      updated prompt; confirm the operator is unchanged (no new inversion introduced in the opposite
      direction) (depends on T002)

---

## Phase 3: User Story 2 — Already-compiled inconsistent checks are caught, not silently signed (Priority: P1)

**Done when:** A deterministic `operator_consistency_check()` function exists, flags the 45 known
suspects, does not flag a representative correct-check sample, and is wired into the compile-batch
pipeline so a flagged check is excluded from `assemble_ruleset`'s signed set.

**Independent Test**: Run the function against `post_closing_only_ruleset.json`; confirm both known-
bad checks and at least 45 total checks are flagged; confirm a representative correct-check sample is
not flagged.

- [ ] T005 [US2] In `compile_llm.py`, add `operator_consistency_check(check: Check) -> Optional[str]`
      — formalizing `output/operator_inversion_suspects_2026-07-24.json`'s heuristic script into
      reusable code; returns a reason string if inconsistent, `None` if consistent or unmeasurable
      (Edge Cases: no recognized phrase → `None`, not a flag)
- [ ] T006 [US2] In `test_operator_consistency.py`: assert `fnm-ltv-mi-required` and
      `ltv-exceeds-80-without-mi` (loaded from the real ruleset fixture) are both flagged (depends on
      T005)
- [ ] T007 [US2] In `test_operator_consistency.py`: run the function against all unique
      `ratio_threshold` checks in `post_closing_only_ruleset.json`; assert the flagged set is a
      superset of the 45 checks in `output/operator_inversion_suspects_2026-07-24.json` (SC-001)
      (depends on T005)
- [ ] T008 [US2] In `test_operator_consistency.py`: measure and report the false-positive rate against
      the checks NOT in the 45-suspect set (SC-002) — assert this rate is zero, or if not, surface the
      specific false positives for manual review before this feature is considered done (depends on
      T005)
- [ ] T009 [US2] Wire `operator_consistency_check()` into the compile-batch pipeline (`compile_batch`
      and/or `assemble_ruleset`): a flagged check is excluded from the signed `Ruleset`, present in
      batch output for SME review — mirroring how a `parse_error`d draft is already handled (depends
      on T005, T008 passing)

---

## Phase 4: Polish & Cross-Cutting

- [ ] T010 Run `pytest p0/tests -v` in full; confirm zero unrelated regressions
- [ ] T011 Update `output/ROADMAP.md` Tension 9 to reflect this feature's shipped scope (the
      operator-direction half closed; the conditional-applicability half remains open, tracked to
      `002e`)

## Dependencies & Execution Order

- Phase 1 (T001) blocks everything.
- Phase 2 (T002-T004) and Phase 3 (T005-T009) are independent of each other — both depend only on
  T001 — and can proceed in parallel.
- T009 depends on T005 AND T008 (false-positive measurement must pass before wiring the gate to
  exclude checks from sign-off — an unmeasured gate should not start blocking real compiles).
- T010-T011 are the closing sequence.

## Parallel Example

```
# Phase 2 (prompt fix) and Phase 3 (consistency-check function) touch different concerns
# and can proceed together once T001 exists:
Task: "Extend SYSTEM_PROMPT with PASS-condition convention + few-shot examples"
Task: "Add operator_consistency_check() function + true/false-positive tests"
```
