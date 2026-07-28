# Implementation Plan: Source Envelope and Inbound Contracts

**Branch**: `001b-source-envelope-and-inbound-contracts` | **Date**: 2026-07-01 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001b-source-envelope-and-inbound-contracts/spec.md`
**Depends on**: `001a-field-catalog` (planned; see `../001a-field-catalog/plan.md`)

## Summary

Generalize the engine's fixed `{doc, los, mismo}` field attributes into a source-agnostic
`{truth, sources: {name → value}}` envelope — N system sources, no code change per source — while
preserving today's exact LOS-else-MISMO fallback behavior. Pin the Touchless and LOS/MISMO inbound
contracts as reviewable schemas. This is the scaling bet + the source-independence guarantee
(Principle V) that the reconcile archetype (`003c`) and every future multi-source scenario depend on.

## Technical Context

**Language/Version**: Python 3.9-compatible (project-wide constraint).
**Primary Dependencies**: None new.
**Storage**: No new storage — a data-model generalization inside `qc_engine`; inbound contracts are
documentation, not a new integration (Principle IV — Touchless/LOS are consumed, not built).
**Testing**: Extends `p0/tests/test_p0.py` — zero-regression against the P0 golden set (SC-001), a
new independent-construction test-fixture helper (SC-003), a MISMO-only-loan regression case (SC-005).
**Target Platform**: Same as all of `p0/` — no service, no network call.
**Project Type**: Library extension to `qc_engine`, depends on `001a`.
**Performance Goals**: N/A.
**Constraints**: Zero regression against the P0 golden set; `truth` always document-sourced
(Principle V); no multi-source reconciliation logic built (out of scope, roadmap feature 013).
**Scale/Scope**: A new named source addable via configuration alone (FR-004); this feature does not
require populating more than the existing `los`/`mismo` sources for any real loan today.

## Constitution Check

*GATE: evaluated against `.specify/memory/constitution.md` v1.1.0.*

| Principle | Status | Note |
|---|---|---|
| I — Determinism of the correct computation | ✅ PASS | Purely a data-shape generalization; no model, network, or wall-clock introduced. Zero-regression against the golden set is an explicit gate (SC-001). |
| II — Compile, then run | N/A this feature | No LLM involvement at all. |
| III — Eval is foundational | ✅ PASS | SC-001/SC-002 make zero-regression against the existing proven suite an explicit, testable requirement — not an assumption. |
| IV — Build the core, assume the periphery | ✅ PASS | The Touchless extractor and LOS connector are explicitly *not* built here (contracts/inbound-contracts.md Non-goals) — only the schema they must conform to, and the engine-side generalization to consume it. |
| V — Source independence | ✅ PASS (this is what the feature implements) | `truth` is always document-sourced by construction (FR-002); the independence *guard* is correctly scoped to test-fixture construction, not runtime data (research.md decision #2) — a meaningful distinction, not a weakening of the principle: production data is independent structurally, so the guard belongs where the actual risk lives. |
| VI — Configurable by non-technical users | N/A this feature | No authoring surface touched. |
| VII — Configuration is authored data | ✅ PASS / N/A | `source_priority` defaults are code-level constants for this feature; per-field overrides are expressed via `001a`'s catalog (already authored data) — this feature doesn't introduce a second authoring surface. |

**No unjustified violations. Complexity Tracking is empty.**

## Project Structure

### Documentation (this feature)

```text
specs/001b-source-envelope-and-inbound-contracts/
├── spec.md
├── plan.md                  # This file
├── research.md               # Phase 0 — envelope shape, source-independence-as-test-discipline, contract reuse
├── data-model.md             # Phase 1 — SourceEnvelope, inbound contracts, test-independence helper
├── contracts/
│   └── inbound-contracts.md      # Pinned Touchless + LOS/MISMO schemas (closes GAP 1 for this scope)
├── quickstart.md              # Phase 1 — add-a-source workflow, independence-test discipline
└── tasks.md                   # Phase 2 output (/speckit-tasks — not created by this plan)
```

### Source Code (repository root)

Extends `qc_engine`, depends on `001a`'s `catalog.py`/`field_catalog.json` already being in place:

```text
p0/qc_engine/
├── model.py                 # MODIFIED — SourceValue's doc/los/mismo generalizes to truth/sources;
│                             #   system_value() becomes the priority-ordered lookup (data-model.md)
├── catalog.py                # existing (001a) — FieldCatalogEntry gains source_priority (optional field)
├── reconcile.py               # existing — unchanged logic, now reads through the generalized envelope
└── engine.py                  # existing — unchanged; _eval_check reads sv.doc/sv.system_value()
                                #   equivalents through the new envelope's accessor methods, same call shape

p0/eval_synth/
└── generator.py               # EXTENDED — gains assert_independently_constructed(...) helper,
                                #   applied to existing + new reconcile fixtures

p0/tests/
└── test_p0.py                 # EXTENDED — zero-regression suite, MISMO-only-loan case,
                                #   independent-construction assertion tests
```

**Structure Decision**: Modify `model.py` in place (the fixed attributes generalize into the new
envelope shape) rather than adding a parallel new class — `SourceValue` has exactly one direct
consumer pattern (`sv.doc`, `sv.system_value()`) across the engine, so generalizing it directly is
lower-risk than maintaining two parallel field-value shapes during a transition. Zero-regression
(SC-001) is the safety net for this in-place change, not a parallel-implementation strategy.

## Complexity Tracking

*No entries — no Constitution Check violations require justification.*

## Implementation Notes (post-hoc — what was actually built)

Implemented per `tasks.md` (T001–T017 complete; T018 is this note). One significant amendment
surfaced during implementation — not anticipated at plan time, and important enough to document
carefully rather than gloss over:

- **`assert_independently_constructed`'s definition was wrong as originally specified, and was
  corrected before implementation, not after.** `data-model.md` originally said the guard should
  "raise if a test fixture derives a `sources` entry directly from `truth` ... or a transform of it."
  Reading the actual, already-proven mutation operators in `p0/eval_synth/generator.py`
  (`mut_mismatch_categorical`, `mut_mismatch_numeric`, `mut_inaccurate`) before writing the guard
  showed this definition would have **flagged legitimate, working test code** — those operators
  deliberately compute `sources.los` as a transform of `truth` (e.g. `str(sv.doc) + " UNIT 9"`) to
  construct a *controlled* divergence for reconcile-mismatch testing. That's standard, correct test
  authorship, not a violation of source independence.
  - **The actual trap, found instead**: `p0/eval_synth/generator.py`'s `build_clean()` passes the
    *literal same value* to `doc`, `los`, and `mismo` (e.g. `SourceValue(doc=name, los=name,
    mismo=name)`, one variable, not three independently-drawn values that happen to agree) — this
    is the real "LOS-only data is trivially identical" pattern CLAUDE.md #3 warns about. Not fixed
    here: `build_clean()` is proven, zero-regression-critical foundation code, and fixing its
    internal randomness design is out of `001b`'s scope (this feature generalizes the envelope
    *shape*, not the fixture generator's construction method) — but it is not silently swept under
    either. Flagged here for whoever next touches `eval_synth`'s clean-loan construction.
  - **The corrected, implemented definition**: the guard now checks that a mutation *claiming* to
    construct a divergence (`expect_divergent_keys`) actually produces one — catching a *failed*
    divergence (e.g. a copy-paste bug that silently leaves `sources == truth`), which is the trap
    that would make a reconcile test pass for the wrong reason, unnoticed. Verified: it correctly
    passes on all three existing mutation operators (they do construct real divergence) and
    correctly raises on a synthetic failed-divergence case (`test_independence_guard_catches_failed_divergence`).
- **Result**: `SourceValue` generalized to `{truth, sources, source_priority}` with backward-
  compatible, **read-write** `doc`/`los`/`mismo` properties (confirmed necessary by grep before
  implementation — `eval_synth`'s mutation operators both read and write these attributes
  post-construction). `p0/qc_engine/engine.py` and `reconcile.py` required **zero changes** — both
  already called only `sv.doc` / `sv.system_value()`, exactly as `plan.md`'s Structure Decision
  predicted. 9 new tests added to `p0/tests/test_p0.py` (38 total, all passing). The determinism
  digest is byte-identical before and after this feature
  (`8510a0a8b4b6996e047fc8534e094394ba72aae396305b0d2ecad3d6924634db`, the same digest recorded in
  `001a`'s plan.md) — SC-001 proven directly, twice now across two features. The field-catalog hash
  (`4a4fefe9...`) is also unchanged, since `FieldCatalogEntry`'s new `source_priority` field is
  omitted from `to_dict()` when unset.
