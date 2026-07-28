# Implementation Plan: Eval Harness as Promotion Gate

**Branch**: `005-eval-harness-as-promotion-gate` | **Date**: 2026-07-27 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/005-eval-harness-as-promotion-gate/spec.md`

## Summary

Productionize the already-proven `p0/eval_synth` scorer into a real CI-style promotion gate for
compiled `Ruleset`s, and — per the roadmap's own v0.6 amendment — generalize *scenario construction
itself* so the gate can build a labeled pass/fail test case for **any** compiled `Check` (any
`field_name` + `kind` the real field catalog and compiler produce), not only the ~7 fields
`p0/eval_synth/generator.py` hand-authors mutations for today. The mechanism to generalize already
exists as unpromoted spike code — `p0/experiment_002a/score_drafts.py`'s `SCORERS` dict, proven at
n=24 — and this feature's core engineering act is promoting that pattern, extending it to the 2
check kinds it doesn't yet cover (`agree_doc_categorical`/`agree_doc_numeric`, added by `003d` after
the spike was written) and to `applies_if` precondition-setting (added by `002e`, also after the
spike). On top of that generalized constructor, this feature adds three named test tiers
(GOLDEN/COVERAGE/VOLUME), makes zero-false-auto-clear a real hard block (today it is computed and
printed, not enforced), and ships the whole thing as a single, CI-vendor-agnostic script.

## Technical Context

**Language/Version**: Python 3.9-compatible (project-wide constraint).
**Primary Dependencies**: None new. Reuses `qc_engine.model` (`CanonicalLoan`/`SourceValue`),
`qc_engine.ruleset` (`Check`/`Ruleset`), `qc_engine.engine.run` (the deterministic evaluator being
scored), and `field_catalog.json` (the vocabulary driving generalized construction) — all existing.
**Storage**: Flat files only, consistent with the rest of `p0/`. The GOLDEN panel is a new small,
version-controlled JSON/Python fixture file (mirrors `p0/fixtures/ruleset_defects.py`'s existing
pattern); gate run artifacts remain JSON files under `p0/eval_synth/artifacts/`, extending
`eval.py`'s existing shape — no database.
**Testing**: `pytest p0/tests -v` (existing suite, zero-regression bar) plus new test modules under
`p0/eval_synth/` covering the generalized constructor (SC-001/002), the hard-block behavior
(SC-003), GOLDEN replay (SC-004), and VOLUME reporting (SC-005).
**Target Platform**: Local execution / any CI runner that can execute a Python script and read its
exit code — no service, no specific CI vendor (spec.md FR-009, Assumptions).
**Project Type**: Library/CLI extension to the existing `p0/eval_synth` package — no new project,
no UI.
**Performance Goals**: VOLUME tier at N=5000 (today's default) must complete in the same order of
magnitude as `eval.py` does today (a few seconds, pure in-memory Decimal arithmetic — no I/O, no
network, no model calls). COVERAGE tier's cost is O(checks in the candidate ruleset), each a
handful of engine evaluations — negligible even at the full ~8,442-row rulebook scale.
**Constraints**: Zero regression against the existing suite and `p0/harness.py`'s bit-exact digest
(SC-006) — this feature adds new evaluation *of* rulesets, it must not change the engine's own
evaluation behavior. No runtime LLM call anywhere in this feature (FR-011). Python 3.9 syntax only
(`Optional[...]`, not `X | None`), matching every other `p0/` module.
**Scale/Scope**: Generalizing scenario construction across 6 check kinds and 379 field-catalog
entries (4 `data_type`s); 3 named test tiers; 1 CI-runnable entry-point script. Does not include
building real-loan acquisition (`012`) or a specific CI vendor's workflow file (out of scope,
spec.md FR-012 and Assumptions).

## Constitution Check

*GATE: evaluated against `.specify/memory/constitution.md` v1.1.1.*

| Principle | Status | Note |
|---|---|---|
| I — Determinism of the *correct* computation | PASS | The gate itself must be as deterministic as the engine it scores (spec.md US2 Acceptance Scenario 3: identical `BLOCK` decision on re-run) — no network, no model, no wall-clock inside the constructor or scorer. Decimal arithmetic reused unchanged from `qc_engine.money`. |
| II — Compile, then run | PASS | This feature makes zero LLM calls (FR-011). It evaluates already-compiled, already-signed `Ruleset`s produced by `002b` — it does not compile or interpret anything itself. |
| III — Eval is foundational | PASS (this feature *is* the gate) | Directly implements the constitution's own three-question decomposition: GOLDEN answers "did a known case regress," COVERAGE answers "does every compiled check have a proven scenario," VOLUME answers "at scale, does zero-false-auto-clear hold" — mapping 1:1 onto Principle III's engine-correctness/interpretation-correctness/defect-distribution split. FR-006 makes the Safety gate's "a single false-clear blocks the change" literally true for the first time. |
| IV — Build the core, assume the periphery | PASS | No document extraction, no LOS integration touched. Pure evaluation-of-the-engine's-own-output. |
| V — Source independence | PASS | FR-004's two-field `agree_doc_categorical`/`agree_doc_numeric` construction explicitly never populates `SourceValue.sources{}` for doc-vs-doc checks, preserving `003d`'s independence boundary; single-field `agree_categorical`/`agree_numeric` construction (inherited from `score_drafts.py`) already sets doc and system values independently, matching `generator.py`'s own `assert_independently_constructed` discipline. |
| VI — Configurable by non-technical users | N/A this feature | No authoring-surface change — this is an internal eval/CI mechanism, not something an SME configures directly. |
| VII — Configuration is authored data | PASS | The gate's referential-integrity assumption (Edge Cases: an unresolved `field_name` is `catalog.py`'s failure to catch, not this feature's to re-implement) explicitly defers to the existing SAFE-gate mechanism rather than duplicating it. |

**No unjustified violations. Complexity Tracking is empty.**

## Project Structure

### Documentation (this feature)

```text
specs/005-eval-harness-as-promotion-gate/
├── spec.md
├── plan.md                  # This file
├── tasks.md                 # Phase 2 output (/speckit-tasks)
└── checklists/
    └── requirements.md
```

No `research.md`/`data-model.md`/`contracts/` — deliberately omitted, following `003a`'s own
precedent: this feature promotes and generalizes an already-designed, already-proven pattern
(`score_drafts.py`'s `SCORERS`) rather than researching a new one from scratch. The "research" this
plan would otherwise capture is the direct code-reading already recorded in spec.md's "Foundation
this builds on" / "Gaps confirmed by direct inspection" sections.

### Source Code (repository root)

```text
p0/eval_synth/
├── eval.py                    # MODIFIED — becomes (or delegates to) the CI promotion-gate entry
│                               #   point; gains per-tier reporting and the hard-block exit-code/
│                               #   promotion_decision contract (FR-006/009)
├── generator.py                # UNMODIFIED — its 7 hand-written mutation operators remain the
│                               #   VOLUME-tier population source (spec.md Assumptions); this
│                               #   feature does not touch its existing archetypes
├── scenario_construction.py    # NEW — the generalized, promoted successor to
│                               #   score_drafts.py's SCORERS dict: one construction strategy per
│                               #   Check.kind (6 total, FR-001), reading field_catalog.json's
│                               #   data_type instead of a hand-picked field, setting applies_if
│                               #   preconditions (FR-003), and handling two-field construction for
│                               #   agree_doc_categorical/agree_doc_numeric (FR-004)
├── golden_set.py               # NEW — GOLDEN tier: a small, version-controlled fixed panel +
│                               #   old-vs-new ruleset replay, reporting flips (FR-005/007)
├── coverage_set.py             # NEW — COVERAGE tier: iterates every Check in a candidate
│                               #   Ruleset, calls scenario_construction.py once per check,
│                               #   reports checks_covered/checks_total (FR-005)
├── promotion_gate.py           # NEW — the single CI-runnable entry point (FR-009): orchestrates
│                               #   GOLDEN + COVERAGE + VOLUME (via generator.py/eval.py) + the
│                               #   metamorphic invariants (test_properties.py, generalized),
│                               #   computes promotion_decision, sets exit code
├── test_properties.py          # MODIFIED — invariant functions take a `ruleset: Ruleset`
│                               #   parameter instead of reading the module-level `RULESET`
│                               #   constant (FR-008); an invariant whose relevant check kind is
│                               #   absent from the given ruleset reports not-applicable
├── taxonomy.py / taxonomy.json # UNMODIFIED — archetype coverage reporting reused as-is
└── artifacts/                  # UNMODIFIED location — promotion_gate.py's JSON artifacts land
                                #   here, extending eval.py's existing shape (adds golden/coverage/
                                #   volume sections + promotion_decision)

p0/experiment_002a/score_drafts.py   # UNMODIFIED (FR-013) — remains the throwaway spike record;
                                     # informs scenario_construction.py, is not imported by it

p0/fixtures/
└── golden_panel.py             # NEW — the GOLDEN tier's fixed panel of (loan, expected_verdicts)
                               #   pairs, seeded from p0/fixtures/ruleset_defects.py's existing 25
                               #   known planted defects (spec.md Assumptions) — a version-
                               #   controlled fixture file, not generated at run time

p0/tests/
├── test_scenario_construction.py   # NEW — SC-001/002: one representative Check per kind,
│                                   #   confirms pass/fail construction + real-engine verdict match
├── test_promotion_gate.py          # NEW — SC-003: injected false-auto-clear -> BLOCK + non-zero
│                                   #   exit; SC-004: injected verdict flip -> GOLDEN reports it
└── test_p0.py                     # UNMODIFIED — existing regression suite, re-run for SC-006
```

**Structure Decision**: New capability lands as new modules inside the existing `p0/eval_synth/`
package (the natural home — it already owns the scorer, the generator, and the artifact format),
plus one new fixture file in `p0/fixtures/` (matching where `ruleset_defects.py` already lives) and
two new test modules in `p0/tests/` (matching `003a`'s own precedent of a dedicated new test file
per feature-scale concern, alongside the existing suite). `score_drafts.py` and `generator.py` are
both left in place unmodified — this is a promotion-and-generalization feature, not a rewrite of
already-working code.

## Complexity Tracking

*No entries — no Constitution Check violations require justification.*

## Implementation Notes (post-hoc, T044)

**Shipped 2026-07-27.** All 44 tasks (T001-T044) complete across the 7 phases (Setup, US1-US5,
Polish). Final module set matches this plan's Project Structure exactly:
`p0/eval_synth/scenario_construction.py`, `golden_set.py`, `coverage_set.py`, `promotion_gate.py`
(all NEW), `p0/eval_synth/test_properties.py` (MODIFIED — invariants generalized to an explicit
`ruleset` parameter, FR-008), `p0/eval_synth/eval.py` (MODIFIED minimally — docstring cross-reference
to `promotion_gate.py` + one explicit `demo_ruleset()` call site, no exit-code/artifact-shape change),
`p0/fixtures/golden_panel.py` (NEW). `generator.py`/`taxonomy.py`/`taxonomy.json`/`score_drafts.py`
unmodified, as specified.

**Amendment discovered during implementation (test-isolation, not a spec change):** `test_properties.py`'s
`score()` function is also called (with only 1 positional argument, no `ruleset`) by two files outside
this feature's scope — `p0/tests/test_fixture_generation.py` and `p0/tests/test_real_loan_adapter.py`
(the latter belongs to not-yet-built spec `012`). Rather than requiring `ruleset` as a second positional
argument (which would have broken those pre-existing call sites with a new `TypeError`, replacing their
current, already-expected failure reasons), `score(loans, ruleset: Optional[Ruleset] = None)` defaults to
`demo_ruleset()` when omitted — FR-008's generalization is fully satisfied (every caller *can* pass an
explicit ruleset; `eval.py` and the new invariant functions do), while every pre-existing 1-argument call
site keeps its exact prior behavior. Confirmed by re-running `p0/tests/test_real_loan_adapter.py` before
and after: identical 7-failed/1-skipped/2-passed result, same failure reasons (`ModuleNotFoundError:
No module named 'eval_real'` ×5, `KeyError: 'mutations'` ×1, the matching `pytest.fail(...)` canary ×1)
— a prior draft of this change also defensively rewrote `score()`'s internal `prov['mutations']` access
to `prov.get('mutations', [])`, which accidentally flipped those last two tests from FAILED to PASSED
(silently completing a slice of spec `012`'s own FR-003 as a side effect of this feature). Reverted to
the exact original `prov['mutations']` access — that fix belongs to `012`'s own implementer, with `012`'s
own design context, not to this feature as an uncredited side effect.

**Zero-regression confirmation (SC-006):**
- `cd p0 && python3 -m pytest tests -q --continue-on-collection-errors`: **before** this feature,
  46 failed / 298 passed / 3 skipped / 7 errors (7 collection errors = the 4 red-state test files this
  feature turns green, plus 3 belonging to other not-yet-built specs — `test_decision_narrative.py`,
  `test_loan_profiles_v3.py`, `test_occupancy_applicability_gating.py`). **After**: 46 failed / 322
  passed / 3 skipped / 3 errors — the delta is exactly +24 passed (the 4 new files' own tests) and -4
  errors (those same 4 files now import successfully); the 3 remaining collection errors and all 46
  failures are byte-identical in cause to the baseline, none introduced by this feature.
- `python3 -m pytest eval_synth/test_properties.py -q`: 7 passed (unchanged count; `reconcile_soundness_invariant`
  and `confidence_gate_invariant` now exercise `chk-borrower-name` rather than the original hardcoded
  `chk-property-address`/`chk-note-rate` — an intentional consequence of "pick the ruleset's own first
  matching check" generalization, not a hand-picked substitution; behavior/outcome unchanged, still green).
- `python3 harness.py` (the bit-exact digest, SC-006's specific named gate): **before** and **after** —
  byte-identical: `82175d076579e31a50971d8b20ea4b63848bea9f9b53c30dd96524071842e5ec`, 1000/1000 runs,
  precision=1.0 recall=1.0, ruleset sha256 `30f3794d2768a9b4e9d15134080b7486dc39062b022dde3f2824b5a6678f0d47`
  unchanged — confirms this feature adds new evaluation *of* rulesets without altering the engine's own
  evaluation behavior at all.

**Real coverage-fraction measurement (SC-002), against a real compiled artifact** (
`p0/compile_runs/run_010_post_closing_only/ruleset.json` — 5093 checks compiled from the real
post-closing-only rulebook slice; `run_013_comprehensive_e2e_v6` referenced in criteria.md has no
pre-generated `ruleset.json` in this worktree, so this run's own committed artifact stood in):
**4913/5093 checks covered (96.5%)**, zero hand-written per-field mutation code added to reach it. All
180 construction failures are the SAME named, honest reason: `ratio_threshold` checks whose `threshold`
is `UNSPECIFIED` — the compiler correctly declined to invent a number the source row didn't state
(`CLAUDE.md` Non-Negotiable #1's grounding discipline); this is the expected, by-design residual named in
spec.md's Edge Cases (a `field_value`/`ltv`/`dti` check can't get a constructed pass/fail scenario without
a real threshold to straddle), not a construction-strategy gap this feature failed to cover.
