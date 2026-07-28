# Implementation Plan: Conditional-Applicability Gating

**Branch**: `002e-conditional-applicability-gating` | **Date**: 2026-07-24 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/002e-conditional-applicability-gating/spec.md`

## Summary

Adds one new optional `Check` field (`applies_if`), one new deterministic gating step in `engine.py`
(evaluated before any kind-specific dispatch), one new referential-integrity resolution in
`catalog.py`, and a compiler-prompt extension teaching the LLM to extract this precondition from a
row's own `defect_text` — never from grounding context alone. Architecturally this is the same size
and shape as `003d` (one new optional field, engine gains a new deterministic step, catalog gains one
more thing to resolve, compiler prompt extended) — not a new mechanism, a new *field* evaluated by
the same kind of deterministic comparison every other check kind already uses.

The design is grounded in convergent external research (`output/RULE-COMPILER-FIX-PLAN-2026-07-24.md`
§1): XACML's `Target`/`Condition`/`Effect` split and DMN's condition-columns both independently
converge on "a gate, evaluated first, resolving to a distinct not-applicable outcome" — exactly what
`NOT_APPLICABLE` already is in this engine. Drools' idiom of compiling a gating condition into a
named, inferred fact (`IsAdult(age>=18)`) maps onto treating the precondition target as an ordinary
canonical field, no new representation needed. Real failure-mode data (precision ~93%, recall
60-82% on comparable legal-clause extraction) sets the safe default: uncertain → unconditional
(`applies_if=None`), matching today's behavior — the same asymmetry already governing `UNSPECIFIED`
thresholds.

**Revised 2026-07-24, after reviewing closer-to-home prior art**: Olav's live "Ratio-Space Console"
(`scenario.agent-lab.io`, findings in `output/AGENT-LAB-SCENARIO-CONSOLE-FINDINGS-2026-07-24.md`) — a
sibling Tavant system compiling the same Citizens-engagement guideline overlays into machine-evaluable
constraints — independently confirmed the two-layer gate design (coarse program-level `applies_to[]`
vs. finer loan-fact `scope:`) this plan already proposed, but showed its real compiled output is
**compound** (`scope: occupancy == primary_residence; units between [3, 4]; loan_purpose in
['purchase', 'rate_term_refinance']`) — multiple AND-combined conditions with `in`/`between`
operators, not just a single equality. `applies_if` is revised from a single dict to
`List[Dict[str, str]]` as a direct result (spec FR-001).

Phase 1 (this plan's scope) proves the mechanism against loan 01's real, SME-confirmed gift-fund case
and a representative compile sample — not a full rulebook recompile, mirroring `003d`'s own Phase
1/Phase 2 split.

## Technical Context

**Language/Version**: Python 3.9-compatible (project-wide constraint).
**Primary Dependencies**: None new. Extends `p0/qc_engine/ruleset.py`, `engine.py`, `catalog.py`,
`compiler/compile_llm.py` — all existing modules.
**Storage**: None new.
**Testing**: New `p0/tests/test_applicability_gating.py (shipped as `test_conditional_applicability.py` — naming drift, noted 2026-07-26)` (engine-branch unit tests: precondition
holds/doesn't-hold/unknown, mirroring `003d`'s test structure) plus extensions to `p0/tests/test_p0.py`
(digest re-baseline, `003d`/`004` precedent) and a real-fixture proof against loan 01's actual gift-fund
scenario (SC-001).
**Target Platform**: Local execution, same as all of `p0/`.
**Project Type**: Engine capability addition (one new field, one new deterministic gate) + compiler
prompt extension + real-fixture proof.
**Performance Goals**: N/A — one additional field lookup + comparison per check, same cost class as
every existing deterministic step in `_eval_check`.
**Constraints**: MUST NOT change program-level gating (`010a`) — the two layers compose, spec FR-009.
~~MUST NOT decode the Question-ID column~~ **[REVERSED — stale constraint, flagged 2026-07-26 spec
audit: spec FR-008 now says the opposite — the column IS decodable by clustering and MUST be
attempted first, via `002f` Layer 0]**. `applies_if` extraction MUST be traceable to `defect_text`
itself, never `grounding_context` alone (FR-005) — this is the exact mechanism that satisfies Kayla's
stated constraint from the SME call.
**Scale/Scope**: Phase 1 — loan 01's real gift-fund case plus a representative compile sample proving
the safe-default behavior holds. A full/partial recompile of the 8,442-row rulebook to find additional
conditionally-gated checks at scale is explicitly Phase 2, a separate future decision (spec
Assumptions).

## Constitution Check

*GATE: evaluated against `.specify/memory/constitution.md` v1.1.1.*

| Principle | Status | Note |
|---|---|---|
| I — Determinism of the correct computation | ✅ PASS | The new gating step is a pure function of `loan`/`chk.applies_if` — a plain data comparison, same class as every other deterministic step in `_eval_check`. No LLM at evaluation time. |
| II — Compile, then run | ✅ PASS | The compiler decides `applies_if` once, at compile time, from the row's own text — the engine never re-derives applicability per loan; it only evaluates the already-authored gate. This is the direct fix for the exact runtime-LLM pattern `examples/mortgage-qc` uses instead (confirmed via `docs/architecture/rule-compiler.md` §6 — explicitly not adopted). |
| III — Eval is foundational | ✅ PASS | SC-001-003 make Phase 1 correctness (the real loan-01 case, the gate-passes-unchanged path, the safe-default rate) explicit, testable gates. |
| IV — Build the core, assume the periphery | ✅ PASS | This is the Apply-surface engine's applicability layer — core, not periphery. No extraction/LOS work touched. |
| V — Source independence | N/A | Not touched — `applies_if` reads `loan.get(field_name)`'s truth value, the same access pattern every other kind already uses; no new source-comparison shape. |
| VI — Configurable by non-technical users | N/A this feature | Authored the same way as every other check field — via the compiler (or hand-authored `Check` objects); no new authoring-surface change. |
| VII — Configuration is authored data | ✅ PASS | `applies_if` is authored data on `Check`, exactly like `field_name`/`operator`/`threshold` — no new runtime logic that isn't data-driven. |

**No unjustified violations. Complexity Tracking is empty.**

## Project Structure

### Documentation (this feature)

```text
specs/002e-conditional-applicability-gating/
├── spec.md
├── plan.md                  # This file
├── tasks.md
└── criteria.md
```

### Source Code (repository root)

```text
p0/qc_engine/
├── ruleset.py                 # Check gains applies_if: Optional[List[Dict[str, str]]] = None
├── engine.py                  # _eval_check gains the applicability gate, evaluated before kind
│                               # dispatch (right after `res` is constructed, before the `if chk.kind`
│                               # chain — confirmed insertion point by direct code read)
├── catalog.py                 # validate_referential_integrity resolves applies_if.field_name too
└── compiler/
    └── compile_llm.py         # SYSTEM_PROMPT gains: PASS/precondition extraction sequencing,
                                # closed gating-dimension checklist, applies_if output schema key,
                                # never-invent discipline extended to this field

p0/tests/
├── test_applicability_gating.py   # NEW — engine-branch tests (holds/doesn't-hold/unknown) +
│                                   # real loan-01 gift-fund fixture proof
└── test_p0.py                     # digest re-baseline (003d/004 precedent)

output/
└── ROADMAP.md                 # Tension 9 updated/closed (conditional-applicability half)
```

## Complexity Tracking

*(empty — no constitution violations to justify)*
