# Tasks: Conditional-Applicability Gating

> **Post-hoc note (2026-07-26, spec audit)**: Phase 1 (engine side — T001–T006 scope) shipped
> 2026-07-25, with the test file named `test_conditional_applicability.py` rather than the
> `test_applicability_gating.py` planned below. The compile-side tasks (T007–T011: SYSTEM_PROMPT
> `applies_if` extraction, real-row recompiles) were **never executed** — that scope moved to
> `002g-canonical-loan-fact-vocabulary`. Checkboxes below are left as-authored; this note is the
> record of what actually happened.

**Input**: Design documents from `specs/002e-conditional-applicability-gating/`
**Prerequisites**: plan.md, spec.md

**Tests**: Included — SC-001/002/003 are the correctness/safety proof this feature exists to produce;
SC-005 is the zero-*unrelated*-regression gate.

**Note on TDD ordering**: mirrors `003d` — the new-gate tests are written and expected to FAIL until
the corresponding `ruleset.py`/`engine.py` changes land, then pass.

**Organization**: Tasks grouped by user story, per this project's convention that each slice ships
with its own proof.

## Phase 1: Setup

- [ ] T001 Add `applies_if: Optional[List[Dict[str, str]]] = None` to `Check` (`p0/qc_engine/ruleset.py`);
      update the class docstring to describe the field (a list of AND-combined conditions, each keyed
      `field_name`/`operator`/`value`; operator ∈ `==`/`!=`/`<=`/`>=`/`<`/`>`/`in`/`between`) and its
      default (unconditional, today's universal behavior) — list shape confirmed necessary by real
      prior art (`output/AGENT-LAB-SCENARIO-CONSOLE-FINDINGS-2026-07-24.md`: compound conditions are
      the norm, not the exception)
      → Done when: `Check(id="x", name="x", field_name="a", kind="predicate", severity="CRITICAL",
      applies_if=[{"field_name": "gift_funds_used", "operator": "==", "value": "true"}])` constructs
      without error, and a 2-condition list also constructs without error
- [ ] T002 Create `p0/tests/test_applicability_gating.py` module skeleton (imports, docstring
      describing scope: precondition holds / doesn't hold / unknown, plus the real loan-01 gift-fund
      fixture proof) — no test bodies yet
      → Done when: `pytest p0/tests/test_applicability_gating.py --collect-only` exits 0 with zero
      tests collected

---

## Phase 2: User Story 1 — A conditionally-scoped check resolves NOT_APPLICABLE cleanly (Priority: P1) 🎯 MVP

**Done when:**
- A check with `applies_if` resolves `NOT_APPLICABLE` when the loan's data doesn't satisfy it,
  evaluates normally when it does, and `NEEDS_REVIEW` when the precondition field itself is unknown
- A check with `applies_if=None` is byte-for-byte unaffected

**Independent Test**: Build a loan whose data doesn't satisfy a check's `applies_if`; confirm
`NOT_APPLICABLE`. Build one that does; confirm normal `kind` evaluation, unaffected.

- [ ] T003 [US1] In `engine.py`'s `_eval_check`, add the applicability gate at the confirmed insertion
      point (immediately after `res` is constructed, before the `if chk.kind ==` chain begins): if
      `chk.applies_if` is set, iterate its condition list; for each condition, read
      `loan.get(condition["field_name"])` and evaluate against `condition["operator"]`/`["value"]`
      (supporting `==`/`!=`/`<=`/`>=`/`<`/`>`/`in`/`between`); if any condition definitely does not
      hold, set `res.status = "NOT_APPLICABLE"` and return early (short-circuit); if a condition's
      field is absent (unknown) and no other condition has already definitely failed, set
      `res.status = "NEEDS_REVIEW"`, an explicit `review_reason` (e.g. `"APPLICABILITY_UNKNOWN"`),
      and return early; otherwise (every condition satisfied, or `applies_if` is `None`) fall through
      to the existing kind-dispatch chain unchanged (depends on T001)
- [ ] T004 [US1] In `test_applicability_gating.py`: precondition doesn't hold → `NOT_APPLICABLE`;
      precondition holds → normal kind evaluation (construct a case with a simple `predicate` check to
      prove fall-through is unaffected); precondition field unknown/absent → `NEEDS_REVIEW` +
      explicit `review_reason`; `applies_if=None` → byte-for-byte identical to a check without the
      field (regression proof); a **compound** (2+ condition) `applies_if` AND-combines correctly
      (one condition failing → `NOT_APPLICABLE` even if the other holds); an `in`-operator condition
      and a `between`-operator condition each evaluate correctly (depends on T003)
- [ ] T005 [US1] Extend `p0/qc_engine/catalog.py`'s `validate_referential_integrity()` to also resolve
      every condition's `field_name` within `chk.applies_if` when present; add a test asserting a bad
      `field_name` anywhere in the condition list is rejected at load time (depends on T001)
- [ ] T006 [US1] Real-fixture proof: reconstruct loan 01's actual gift-fund scenario (no gift funds
      used) as a test fixture; hand-author a `Check` with `applies_if` gating a gift-fund-related
      field, mirroring `ruleset_defects.py`'s existing hand-authoring pattern; confirm it resolves
      `NOT_APPLICABLE` — the concrete SME-confirmed case this feature exists to fix (SC-001) (depends
      on T003)

---

## Phase 3: User Story 2 — The compiler extracts applicability only from a row's own text (Priority: P1)

**Done when:**
- `SYSTEM_PROMPT` extracts `applies_if` only when `defect_text` states/implies it, defaults to `None`
  when uncertain, and never originates a precondition from `grounding_context` alone
- A representative compile sample shows the unconditional majority still compiling with
  `applies_if=None`

**Independent Test**: Compile rows with (a) an explicit precondition, (b) none, (c) an ambiguous case;
confirm (a) extracts correctly, (b)/(c) default to `None`.

- [ ] T007 [US2] Extend `compile_llm.py`'s `SYSTEM_PROMPT`: add the sequential extraction technique
      (locate/quote any conditional-trigger clause in `defect_text` before extracting the check's own
      pass/fail condition), the closed checklist of known gating dimensions (gift/grant funds used,
      property type condo/co-op/PUD, VA/USDA/FHA-specific scenarios, co-borrower present,
      self-employment income used — confirm/extend this list against a real sample of the workbook
      during this task), the `applies_if` output schema key, and the explicit never-invent +
      safe-default-to-None rule (mirroring the existing `UNSPECIFIED`-threshold rule's wording and
      rationale)
- [ ] T008 [US2] Recompile the real gift-fund row (`O-FRD-15499`/equivalent in `demo/rules/*.xlsx`,
      the same row underlying loan 01's SME-confirmed case) with the updated prompt; confirm
      `applies_if` is set and traceable to a quoted span of `defect_text` (depends on T007)
- [ ] T009 [US2] Recompile a representative sample of rows with no stated precondition (the
      unconditional majority); confirm `applies_if` stays `None` for all of them — no regression
      toward over-triggering (depends on T007)
- [ ] T010 [US2] Recompile a row where a precondition is arguably implied but not clearly stated;
      confirm the compiler defaults to `applies_if=None` rather than guessing (depends on T007)
- [ ] T011 [US2] Extend `_existing_catalog_fields()`/`proposed_field_entry` flow (if a gating
      dimension's target field doesn't already exist in the catalog) — confirm the existing mechanism
      (unchanged) correctly proposes it; no new field-catalog code (depends on T007)

---

## Phase 4: Polish & Cross-Cutting

- [ ] T012 Digest re-baseline in `p0/tests/test_p0.py`: following the `003d`/`004` precedent exactly —
      update the digest-pinned tests, add a new baseline test with the real, freshly-computed SHA-256
      (depends on T001)
- [ ] T013 Run `pytest p0/tests -v` in full; confirm zero unrelated regressions
- [ ] T014 Re-run loan 01 against a recompiled or hand-corrected ruleset including the T008 check;
      confirm the gift-fund-related result now resolves `NOT_APPLICABLE` instead of the previous
      unresolved gap/exception (SC-001, end-to-end, not just the unit-test proof from T006) (depends
      on T008, T013)
- [ ] T015 Update `output/ROADMAP.md` Tension 9 to reflect this feature's shipped scope and mark the
      conditional-applicability half closed/scheduled

## Dependencies & Execution Order

- Phase 1 (T001-T002) blocks everything.
- Phase 2 (T003-T006) and Phase 3 (T007-T011) are independent of each other (engine gate vs. compiler
  prompt) and can proceed in parallel once T001 lands.
- T014 depends on both T008 (compiler produces the real check) and T013 (full suite green).
- T012-T015 are the closing verification sequence.

## Parallel Example

```
# Phase 2 (engine gate) and Phase 3 (compiler prompt) touch different files and can run together
# once T001 exists:
Task: "Add the applicability gate to engine.py's _eval_check"
Task: "Extend SYSTEM_PROMPT with sequential precondition extraction + closed checklist"
```
