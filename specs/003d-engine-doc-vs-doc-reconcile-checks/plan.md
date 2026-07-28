# Implementation Plan: Doc-vs-Doc Reconcile Check Engine

**Branch**: `003d-engine-doc-vs-doc-reconcile-checks` | **Date**: 2026-07-23 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/003d-engine-doc-vs-doc-reconcile-checks/spec.md`

## Summary

Unlike `003c` (a proof-only feature that changed no engine code), this feature adds real, additive
capability: two new `Check` kinds, `agree_doc_categorical`/`agree_doc_numeric`, that compare two
independently-named document fields against each other — closing the exact gap `003c`'s FR-005
declined to build. The design is deliberately minimal: one new optional `Check` field
(`compare_field_name`), two new dispatch branches in `engine.py` that reuse the existing normalizer/
tolerance machinery verbatim, and a compile-time (not taxonomy-time) decision rule in `compile_llm.py`
for when to emit the new kinds. `SourceValue`/`model.py` and the source-independence guard `001b`
built are untouched — the new kinds never read `sources{}}`, which is what keeps that guard's
existing guarantee for `agree_categorical`/`agree_numeric` meaningful.

Phase 1 (this feature's actual scope) proves the mechanism against the 5 known doc-vs-doc defects by
hand-authoring `Check` objects directly in `p0/fixtures/ruleset_defects.py` — zero LLM cost. Phase 2
(recompiling the full rulebook to find more real-world doc-vs-doc conditions at scale) is explicitly
a separate, later, real-spend decision — not built or committed here.

## Technical Context

**Language/Version**: Python 3.9-compatible (project-wide constraint).
**Primary Dependencies**: None new. Extends `p0/qc_engine/engine.py`, `ruleset.py`, `catalog.py`,
`compiler/compile_llm.py`, `compiler/pattern_flags.py` — all existing modules, no new imports.
**Storage**: None new. Same fixture-file pattern as `000`/`003a`/`003b`/`003c`.
**Testing**: New `p0/tests/test_doc_vs_doc_reconcile.py` (engine-branch unit tests, mirroring
`test_reconcile_archetypes.py`'s structure) plus extensions to `p0/tests/test_p0.py` (digest
re-baseline) and `p0/tests/test_fixture_generation.py` (25/25 known-defect coverage, was 20/25).
**Target Platform**: Local execution, same as all of `p0/` — no service.
**Project Type**: Engine capability addition + compiler prompt extension + hand-authored fixture
proof. Real code change, unlike `003c`.
**Performance Goals**: N/A — two new `elif` branches, same evaluation cost class as the existing
`agree_categorical`/`agree_numeric` branches they sit beside.
**Constraints**: `SourceValue`/`model.py` MUST NOT change (spec FR-009). The `Check` digest WILL
change for every existing ruleset (an unavoidable consequence of `asdict()`-based hashing) — this is
a required, deliberate re-baseline (spec Edge Cases), not a regression to avoid. A doc-vs-doc
mismatch MUST resolve `FAIL`/`EXCEPTION`, never the reconcile-`FLAG` path (spec US2) — this is the
single highest-stakes property specific to this feature, since getting it wrong silently
under-reports real defects the same way the pre-existing gap already did.
**Scale/Scope**: Phase 1 — the 5 known doc-vs-doc defects, hand-authored, zero compile cost. Phase 2
(the estimated 14-26 additional real conditions across the full 8,442-row rulebook) is explicitly
out of scope for this plan (spec FR-010).

## Constitution Check

*GATE: evaluated against `.specify/memory/constitution.md` v1.1.1.*

| Principle | Status | Note |
|---|---|---|
| I — Determinism of the correct computation | ✅ PASS | The two new branches are pure functions of `loan`/`chk` — same `Decimal`/normalizer machinery `agree_categorical`/`agree_numeric` already use deterministically. No float, no wall-clock, no network. |
| II — Compile, then run | ✅ PASS | The compiler decides doc-vs-doc vs. doc-vs-system once, at compile time, using `expected_sources` — the engine never makes this judgment call at evaluation time; it only dispatches on the already-authored `kind`. |
| III — Eval is foundational | ✅ PASS | SC-001–004 make Phase 1 correctness (all 5 known defects, correct status) and the FAIL-not-FLAG property explicit, testable gates. |
| IV — Build the core, assume the periphery | ✅ PASS | This is the Apply-surface engine's reconcile step — the core. No extraction/LOS work touched. |
| V — Source independence | ✅ PASS | This feature explicitly preserves `001b`'s guard by NEVER routing doc-vs-doc comparisons through `sources{}}` — a new, separate, non-guarded path for a genuinely different shape (two documents, not doc-vs-system), rather than weakening the existing guard's meaning. |
| VI — Configurable by non-technical users | N/A this feature | No authoring-surface change; the two new kinds are authored the same way as the four existing ones (via `002b`'s compiler or hand-authored `Check` objects). |
| VII — Configuration is authored data | ✅ PASS | `compare_field_name` is authored data on `Check`, exactly like `field_name`/`normalizer`/`tolerance` — no new runtime logic that isn't data-driven. |

**No unjustified violations. Complexity Tracking is empty.**

## Project Structure

### Documentation (this feature)

```text
specs/003d-engine-doc-vs-doc-reconcile-checks/
├── spec.md
├── plan.md                  # This file
├── tasks.md
└── criteria.md
```

No `research.md`/`data-model.md`/`contracts/` — the one design decision this feature makes (two new
kinds mirroring the existing categorical/numeric split, one new optional field) is documented
directly in spec.md/this plan; it does not warrant a separate research artifact, consistent with
`003a`/`003b`/`003c`'s precedent of keeping small, well-bounded engine slices light on ceremony.

### Source Code (repository root)

```text
p0/qc_engine/
├── ruleset.py                 # Check gains compare_field_name: Optional[str] = None
├── engine.py                  # _eval_check gains two new elif branches
├── catalog.py                 # validate_referential_integrity resolves compare_field_name too
└── compiler/
    ├── compile_llm.py         # expected_sources in payload; source-shape decision rule; schema key
    └── pattern_flags.py       # _flag_archetype_mismatch_risk kind gate extended

p0/fixtures/
└── ruleset_defects.py         # 5 new hand-authored Check objects; stale docstring corrected

p0/tests/
├── test_doc_vs_doc_reconcile.py   # NEW — engine-branch + phase/disposition tests
├── test_p0.py                     # digest re-baseline (004 precedent)
└── test_fixture_generation.py     # 20/25 -> 25/25 known-defect coverage

output/
└── ROADMAP.md                 # Tension #5 updated/closed
```

## Complexity Tracking

*(empty — no constitution violations to justify)*

## Implementation Notes (post-hoc — what was actually built)

Implemented per `tasks.md` (T001-T019 complete), 2026-07-23. All decisions in this plan held as
written, with three real refinements discovered during implementation, not anticipated in the
original design:

1. **The compiler payload was missing `expected_sources`, confirmed by reading `compile_llm.py`
   directly** — `_existing_catalog_fields()` sent the LLM only `{field_name, data_type}`, never the
   `expected_sources` signal the whole source-shape decision depends on. Fixed as part of T010
   (already anticipated in the plan, but worth noting the bug was real, not hypothetical).
2. **`compile_row` cleaned kwargs by the upstream `engine_kind`, not the LLM's own chosen `kind`** —
   `_clean_check_kwargs(row["engine_kind"], parsed["check"])` would have silently stripped
   `compare_field_name` off every doc-vs-doc check the compiler correctly chose to emit, since
   `engine_kind` stays `agree_categorical`/`agree_numeric` (the family) while the LLM's actual
   output `kind` becomes `agree_doc_categorical`/`agree_doc_numeric`. This was NOT explicitly
   named in the original plan — found by tracing the compile path end-to-end while implementing
   T011/T012, and fixed by cleaning against `parsed["check"].get("kind", row["engine_kind"])`
   instead. Left unfixed, Phase 2 (a future recompile) would have silently produced zero working
   doc-vs-doc checks despite the compiler prompt correctly asking for them — a bug that only
   manifests when Phase 2 actually runs, invisible to Phase 1's fixture-only proof.
3. **The digest re-baseline confirmed empirically, not just predicted**: `PRE_MIGRATION_BASELINE`/
   `PRE_EXISTING_BASELINE`/`PRE_004_BASELINE` all moved from `8510a0a8...` to
   `13cc7f52805a7afda0e14b3ccfac50399b23f09ea6ffb80c0ff7cc99db4617f9`; the full digest moved from
   `POST_004_BASELINE` (`a3f702c1...`) to `POST_003D_BASELINE`
   (`365dc672e73e8cbb16deb82cd4395afeba7f7e3ed642616d1d25e4ba4e425f56`) — confirmed identically by
   both `pytest tests/test_p0.py` and a direct `python3 harness.py` run. `harness.py`'s own
   "byte-identical across 1000 runs: YES" plus precision=1.0/recall=1.0 against labeled outcomes
   confirmed the move is pure schema-shape (new `Check.compare_field_name` field), not any
   behavioral drift in `demo_ruleset()`'s actual checks.

End-to-end proof against the real loan fixtures (not just synthetic test cases): all 5 known
doc-vs-doc defects now resolve correctly via `defects_ruleset_for()` — `chk-def-employment-dates-
agree`/`chk-def-title-vesting-agree` (loan 01) and `chk-def-loan-purpose-agree`/`chk-def-cd-payoff-
agree` (loan 04) all `FAIL`/`EXCEPTION`; `chk-def-liability-disclosed-agree` (loan 01) correctly
`NEEDS_REVIEW`/`SOURCE_INCOMPLETE` since the credit-report side is populated but the 1003 side is
genuinely absent. `test_wired_checks_catch_all_25_known_defects` (renamed from `..._20_wirable...`)
proves this as a permanent regression test: 25/25 known defects, not 20/25.

Full suite: 172/172 passing (`pytest p0/tests -v`), zero unrelated regressions. Phase 2 (recompiling
the full 8,442-row rulebook) intentionally not started — remains a separate future decision per
spec FR-010.
