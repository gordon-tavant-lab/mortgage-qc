# Implementation Plan: Compile-Fidelity Spike

**Branch**: `002a-compile-fidelity-spike` | **Date**: 2026-06-30 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/002a-compile-fidelity-spike/spec.md`

## Summary

Test, on a real (not synthetic) slice of the AMQ workbook, whether an LLM can compile a workbook row
into a rule that (a) runs correctly against `p0/eval_synth`'s constructed-label scorer and (b)
captures the lender's actual intent, per an SME's independent judgment — reporting a pre-registered
PROCEED / RECONSIDER / KILL verdict rather than a shipped capability. This is the highest-risk
irreversible item in the roadmap (§002a, Tension 6): if the compiler cannot reliably interpret the
real workbook, `002b` and everything downstream of it needs rethinking before more is built on the
assumption it works.

## Technical Context

**Language/Version**: Python 3.9-compatible (project-wide constraint).
**Primary Dependencies**: `boto3` + Bedrock (reused pattern from `p0/experiment_g3/llm_arm.py`),
`openpyxl` (reused from `p0/eval_synth/taxonomy.py`). No new dependencies.
**Storage**: Flat files only (sampled rows, drafts, SME review doc, finding) — no database.
**Testing**: Reuses the existing `p0/eval_synth` scorer directly; no new test framework introduced.
**Target Platform**: Local execution + one Bedrock API call per sampled row (config time only).
**Project Type**: Throwaway experiment / spike script — explicitly not a service or library.
**Performance Goals**: N/A — a one-time ~20-30-row compile-and-score run, not performance-sensitive.
**Constraints**: Every LLM call at config/compile time only (Principle II); zero LLM calls in any
runtime evaluation path.
**Scale/Scope**: ~20-30 sampled rows (research.md #1). Full-workbook compilation (7,398 conditions)
is explicitly `002b`'s scope, gated on this spike's verdict.

## Constitution Check

*GATE: evaluated against `.specify/memory/constitution.md` v1.1.0.*

| Principle | Status | Note |
|---|---|---|
| I — Determinism of the correct computation | ✅ PASS | The spike does not change how the engine executes rules; a `CompiledRuleDraft`'s `check` object, once drafted, is evaluated by the existing deterministic engine exactly like any other `Check`. The spike's *compile step* is the thing under test, not the engine's runtime determinism. |
| II — Compile, then run | ✅ PASS (by design — this is what's tested) | Every LLM call happens at config/compile time (FR-002, FR-009). No runtime LLM call is introduced anywhere. |
| III — Eval is foundational | ✅ PASS | Reuses `p0/eval_synth`'s scorer directly (FR-003) rather than asserting correctness without measurement; adds the interpretation-fidelity metric eval_synth cannot itself produce (FR-004, FR-010). |
| IV — Build the core, assume the periphery | ✅ PASS | Tests the compiler mechanism (core, per Principle II); does not touch extraction or LOS integration. |
| V — Source independence | ⚠️ NOTED, not violated | ~10% of the sample is `reconcile`-kind (agree_categorical/agree_numeric). The LLM must be instructed that a reconcile check's comparison value cannot derive from the same source as the truth value — the same source-independence guard 001b will formalize. This spike checks this by construction in its reconcile-row prompts, not via a runtime guard (001b's SAFE gate doesn't exist yet). |
| VI — Configurable by non-technical users | N/A this feature | Authoring UX is roadmap feature `009`, unspecced. The SME review package (`contracts/sme-review-package.md`) is a static document handoff, not an authoring surface. |
| VII — Configuration is authored data | N/A this feature (by design) | This spike's artifacts are explicitly **not** signed/hashed into a production ruleset (FR-008) — Principle VII governs *committed* configuration; a throwaway spike that never commits its output is outside that principle's scope, consistent with the constitution's own "de-risk before committing" framing. |

**No unjustified violations. Complexity Tracking section below is empty — nothing to justify.**

## Project Structure

### Documentation (this feature)

```text
specs/002a-compile-fidelity-spike/
├── spec.md                  # Feature spec (already written)
├── plan.md                  # This file
├── research.md              # Phase 0 output — sample size, structured-output approach, SME review shape
├── data-model.md            # Phase 1 output — SampledWorkbookRow, CompiledRuleDraft, InterpretationFidelityJudgment, PreRegisteredDecisionRule, SpikeFinding
├── contracts/
│   ├── compiled-rule-schema.md    # LLM → structured output contract
│   └── sme-review-package.md      # spike → Kayla handoff contract
├── quickstart.md             # Phase 1 output — the 7-step run sequence
├── pre-registration.md       # LOCKED decision rule (must predate any scored row — SC-001)
└── tasks.md                  # Phase 2 output (/speckit-tasks — not created by this plan; never created at all — the spike executed directly from this plan. Noted 2026-07-26, spec audit)
```

### Source Code (repository root)

This is a throwaway spike, not a new service or module — no new package under `p0/qc_engine/` is
warranted (that would imply durability the spike explicitly disclaims, per FR-008). Scratch scripts
live under `p0/experiment_002a/` (mirroring the existing `p0/experiment_g3/` convention for a
pre-registered, throwaway experiment):

```text
p0/experiment_002a/
├── PRE-REGISTRATION.md   # copy or symlink of specs/002a-compile-fidelity-spike/pre-registration.md,
│                         #   kept alongside other experiments per the p0/experiment_g3/ precedent
├── sample_rows.py        # step 1 — stratified sample from taxonomy.py's classified rows
├── compile_llm.py        # step 2 — LLM compile call, reusing llm_arm.py's Bedrock harness pattern
├── score_drafts.py       # step 3 — feeds drafts into the existing p0/eval_synth scorer
├── build_review_package.py  # step 4 — assembles the SME review document
├── apply_decision_rule.py   # step 6 — evaluates pre-registration.md's D1/D2/D3 against collected results
├── artifacts/            # scored drafts, SME review doc (filled in), and the final finding — throwaway
└── RESULTS.md            # step 7 — the finding, mirroring p0/experiment_g3/RESULTS.md's format
```

**Structure Decision**: Mirror the existing `p0/experiment_g3/` pattern exactly (a self-contained,
throwaway experiment directory under `p0/`, with its own pre-registration and RESULTS.md) rather
than inventing a new convention — this project already has one proven shape for "pre-registered
experiment that produces a finding, not a feature," and reusing it keeps the two experiments
directly comparable.

## Complexity Tracking

*No entries — no Constitution Check violations require justification.*
