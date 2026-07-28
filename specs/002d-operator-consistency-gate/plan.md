# Implementation Plan: Operator-Direction Consistency Gate

**Branch**: `002d-operator-consistency-gate` | **Date**: 2026-07-24 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/002d-operator-consistency-gate/spec.md`

## Summary

A small, well-bounded compiler-hardening feature: two independent additions to
`p0/qc_engine/compiler/compile_llm.py`, no engine changes, no schema changes. (1) `SYSTEM_PROMPT`
gains an explicit statement of the PASS-condition convention plus inversion few-shot examples —
prevention. (2) A new, deterministic (non-LLM) consistency-check function compares a compiled
`ratio_threshold` check's structured `operator`/`threshold` against its own natural-language
`message_pass`/`message_fail` text, flagging contradictions — detection, formalizing the manual scan
that already found 45/495 suspect checks into permanent, automatic compile-batch behavior. Both
additions were directly recommended by external research (arXiv:2411.01414 names the failure class;
arXiv:2604.25031's roundtrip-verification pattern is the direct analog for the detection half, made
cheaper here since both sides already exist from one LLM call).

## Technical Context

**Language/Version**: Python 3.9-compatible (project-wide constraint).
**Primary Dependencies**: None new. Extends `p0/qc_engine/compiler/compile_llm.py` only.
**Storage**: None new.
**Testing**: New unit tests for the consistency-check function (`p0/tests/test_operator_consistency.py`),
run against both the 45 known-suspect checks (must all flag) and a representative correct-check
sample (must not flag — false-positive measurement, FR-007/SC-002).
**Target Platform**: Local execution, same as all of `p0/`.
**Project Type**: Compiler-prompt extension + one new deterministic validation function. No new
architecture.
**Performance Goals**: N/A — the consistency check is a string/regex comparison over already-generated
text, negligible cost per check, no new LLM calls (FR-005).
**Constraints**: MUST NOT change `engine.py`'s `ratio_threshold` evaluation (FR-006 — confirmed
correct already). MUST NOT require a second LLM call (FR-005). MUST measure false positives against
real correct checks before shipping (FR-007), not assume safety from the true-positive result alone.
**Scale/Scope**: Applies to every `ratio_threshold` check in every future compile batch; this feature
does not re-sign the currently-shipped ruleset (that's separate housekeeping, spec Assumptions).

## Constitution Check

*GATE: evaluated against `.specify/memory/constitution.md` v1.1.1.*

| Principle | Status | Note |
|---|---|---|
| I — Determinism of the correct computation | ✅ PASS | The consistency gate is a pure function of already-generated text; no wall-clock, no network, no new model call. |
| II — Compile, then run | ✅ PASS | Both fixes operate entirely at compile time — the prompt change shapes what the LLM emits; the gate screens it before sign-off. The engine (run time) is untouched. |
| III — Eval is foundational | ✅ PASS | SC-001/002 make both the true-positive floor and the false-positive rate explicit, measured gates — not assumed. |
| IV — Build the core, assume the periphery | ✅ PASS | This is a compiler-spine hardening, in scope for the core determinism/audit claim (a wrong operator is a wrong verdict, silently). |
| V — Source independence | N/A | Not touched — this feature doesn't concern doc-vs-system comparison. |
| VII — Configuration is authored data | ✅ PASS | The gate operates on the same authored `Check` fields already in the schema; no new runtime logic that isn't data-driven. |

**No unjustified violations. Complexity Tracking is empty.**

## Project Structure

### Documentation (this feature)

```text
specs/002d-operator-consistency-gate/
├── spec.md
├── plan.md                  # This file
├── tasks.md
└── criteria.md
```

### Source Code (repository root)

```text
p0/qc_engine/compiler/
└── compile_llm.py             # SYSTEM_PROMPT gains PASS-condition convention + few-shot examples;
                                # new operator_consistency_check() function; wired into compile_batch/
                                # assemble_ruleset so a flagged check is excluded from auto-sign

p0/tests/
└── test_operator_consistency.py   # NEW — unit tests against the 45 known suspects + a correct-check
                                    # sample (false-positive measurement)

output/
└── operator_inversion_suspects_2026-07-24.json   # existing artifact, the reference true-positive set
```

## Complexity Tracking

*(empty — no constitution violations to justify)*
