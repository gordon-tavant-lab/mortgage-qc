# Implementation Plan: Predicate Check Engine

**Branch**: `003a-engine-predicate-checks` | **Date**: 2026-07-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/003a-engine-predicate-checks/spec.md`

## Summary

Fix the one concrete defect `002a` found in `p0/qc_engine/engine.py`'s predicate branch — a
truly-missing truth-document value (`doc=None`) silently reports `NOT_APPLICABLE` instead of
`FAIL`, exactly backwards from what the `MISSING` archetype (1,807 of 2,937 real predicate
conditions) requires — and prove the already-correct parts of that branch (`is_true`/`is_present`
on non-missing values) hold across a representative sample of all 5 real predicate archetypes
(`MISSING`/`UNSIGNED`/`EXPIRED`/`INCOMPLETE`/`POLICY`), not just the demo's single hand-authored
check. This is a hardening feature, not a new-architecture feature: no new dataclass, check kind,
or predicate vocabulary is introduced.

## Technical Context

**Language/Version**: Python 3.9-compatible (project-wide constraint).
**Primary Dependencies**: None new — the fix is a ~5-line change to an existing function
(`p0/qc_engine/engine.py::_eval_check`); test fixtures reuse `CanonicalLoan`/`SourceValue`
(`model.py`) and `Check` (`ruleset.py`) unmodified.
**Storage**: None new. Test fixtures are constructed in-memory (mirrors `p0/experiment_002a/score_drafts.py`'s
`_score_predicate` pattern), not a new data file.
**Testing**: Extends `p0/tests/test_p0.py` with the FR-001/002/003 bug-fix regression tests, plus a
new `p0/tests/test_predicate_archetypes.py` covering FR-004/005/006 (SC-002/003/004) — one
pass-case/fail-case pair per representative condition, drawn from the `examples` already present in
`p0/eval_synth/taxonomy.json` for each of the 5 predicate archetypes (no fabricated conditions).
**Target Platform**: Local execution, same as all of `p0/` — no service.
**Project Type**: Bug fix + test hardening to the existing `qc_engine` package.
**Performance Goals**: N/A — no change to the engine's O(1)-per-check evaluation cost; removing an
early-return does not add computation.
**Constraints**: Zero regression against the existing P0 golden set and `harness.py`'s bit-exact
digest (SC-005) — this is a correctness fix, not a behavior-widening feature, so anything that was
correctly `PASS`/`FAIL` before must remain so; only the `doc=None` case changes (from
`NOT_APPLICABLE` to `FAIL`).
**Scale/Scope**: A representative constructed sample per archetype (the 3 `examples` `taxonomy.json`
already carries for each of the 5 predicate archetypes — 15 representative conditions, 30
pass/fail test cases total), not an attempt to construct all 2,937 real conditions individually
(that exhaustive construction is `005`'s eventual job, once its scenario-generation is
data-driven off the field catalog — see `output/ROADMAP.md` §005's v0.6 amendment. `003a` proves
the *mechanism* is correct at representative scale; it does not substitute for `005`).

## Constitution Check

*GATE: evaluated against `.specify/memory/constitution.md` v1.1.0.* *(Corrected 2026-07-26: constitution was already v1.1.1 at this plan's date — the version cite was stale; no gate outcome changes.)*

| Principle | Status | Note |
|---|---|---|
| I — Determinism of the correct computation | ✅ PASS (this is what the fix restores) | `is_present`/`is_true` are pure boolean comparisons over the loan's truth value; removing the early-return does not introduce any non-determinism — it makes the *correct* deterministic outcome (`FAIL` on missing) reachable, where today an incorrect deterministic outcome (`NOT_APPLICABLE`) was reached instead. |
| II — Compile, then run | ✅ PASS / N/A | No LLM touches this feature at all — it evaluates already-signed `Check`s produced by `002b`. FR-007 explicitly refuses to add date-arithmetic logic that would blur this. |
| III — Eval is foundational | ✅ PASS | SC-002/003/004 make correctness across all 5 archetypes and zero-false-auto-clear explicit, testable gates — not asserted by extrapolation from the one demo check. |
| IV — Build the core, assume the periphery | ✅ PASS | This is the Apply-surface engine itself — the core. No extraction or LOS-integration work is touched (FR-008). |
| V — Source independence | N/A this feature | Predicate checks are single-source (doc only) by definition (`kind="predicate"` has no `system_value()` comparison) — source independence is `003c`'s (reconcile) concern, not this one's. |
| VI — Configurable by non-technical users | N/A this feature | No authoring-surface change; this feature touches only the engine's evaluation logic, not anything an SME configures. |
| VII — Configuration is authored data | ✅ PASS / N/A | `Check.predicate` (`is_true`/`is_present`) is already authored data per `002b`; this feature doesn't add to or change that vocabulary (FR-007), it fixes how the existing vocabulary is *evaluated*. |

**No unjustified violations. Complexity Tracking is empty.**

## Project Structure

### Documentation (this feature)

```text
specs/003a-engine-predicate-checks/
├── spec.md
├── plan.md                  # This file
└── tasks.md                 # Phase 2 output (/speckit-tasks)
```

No `research.md` / `data-model.md` / `contracts/` — deliberately omitted. Unlike `001a`/`001b`/`002b`,
this feature introduces no new entity, schema, or architecture decision to research; it is a bug fix
to an existing, already-designed function plus test coverage proving the existing design holds at
real scale. Writing placeholder design docs for a decision that was already made in `001a`'s/`ruleset.py`'s
original design would not add signal.

### Source Code (repository root)

```text
p0/qc_engine/
├── engine.py                # MODIFIED — _eval_check's predicate branch: remove the blanket
│                             #   sv.doc is None early-return (FR-001/002/003); is_true/is_present's
│                             #   own logic already produces the correct FAIL once reached.
├── model.py                 # existing — unchanged
├── ruleset.py                # existing — unchanged (no new Check fields)
└── catalog.py                 # existing — unchanged

p0/tests/
├── test_p0.py                 # EXTENDED — regression tests for FR-001/002/003 (the bug fix itself)
│                             #   + a confirmation that pre-existing non-None predicate behavior
│                             #   (doc="" / doc=False / doc=True / doc="present-value") is unchanged
└── test_predicate_archetypes.py   # NEW — FR-004/005/006 (SC-002/003/004): one pass/fail pair per
                              #   representative condition across MISSING/UNSIGNED/EXPIRED/
                              #   INCOMPLETE/POLICY, drawn from taxonomy.json's existing `examples`
```

**Structure Decision**: A targeted modification to `engine.py`'s existing `_eval_check` function —
no new module. Test coverage splits into two files: `test_p0.py` keeps the direct bug-fix regression
(small, mechanical), while a new `test_predicate_archetypes.py` holds the archetype-scale coverage
(FR-004/005/006), so the two concerns — "is the specific bug fixed" vs. "does the branch hold up
across the real archetype set" — stay independently readable and independently re-runnable, mirroring
how `p0/experiment_002a/score_drafts.py` separated per-kind scoring functions.

## Complexity Tracking

*No entries — no Constitution Check violations require justification.*

## Implementation Notes (post-hoc — what was actually built)

Implemented per `tasks.md` (T001–T017 complete). No amendments — the plan matched what was built
exactly, which is expected for a fix this scoped: a 5-line change (the removal of one early-return
in `_eval_check`) plus two test files.

- **The fix (T005)** was smaller than anticipated: `is_true`'s (`sv.doc is True`) and `is_present`'s
  (`sv.doc is not None and str(sv.doc).strip() != ""`) existing logic already evaluates correctly to
  `FAIL` for `sv.doc is None` — no new branching was needed, only deleting the blanket early-return
  that pre-empted them.
- **Result**: 3 new regression tests in `p0/tests/test_p0.py` (56 total, all passing, up from 53) +
  8 new tests in the new `p0/tests/test_predicate_archetypes.py` (US2/US3, archetype + confidence-gate
  coverage) = 64 total across the suite. `p0/eval_synth/test_properties.py`'s 7 tests unaffected.
  `p0/harness.py`'s determinism digest is **byte-identical before/after this feature**
  (`8510a0a8b4b6996e047fc8534e094394ba72aae396305b0d2ecad3d6924634db` — the same digest `001a`'s own
  plan.md recorded) — SC-005 proven directly, not assumed.
- **`p0/experiment_002a/score_drafts.py` was left untouched**, per `002b`'s own precedent ("`002a`'s
  own throwaway experiment code... untouched; this feature is a fresh, production-scoped
  implementation, not an extension of `p0/experiment_002a/`'s throwaway scripts"). Its `_score_predicate`
  docstring still describes the now-fixed bug as a historical note about the engine *at the time the
  spike ran* — accurate as a record of what `002a` found, even though `engine.py` no longer exhibits it.
- **EXPIRED's staleness semantics remain unresolved**, exactly as scoped (FR-007) — `test_predicate_archetypes.py`
  models it as a pre-computed boolean, which is not yet confirmed as the real compile strategy. Carried
  forward as an open item for `002b`'s compiler policy and Kayla's eventual review, same as `002a` left
  it.
