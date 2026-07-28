# Implementation Plan: Ratio/Threshold Check Engine

**Branch**: `003b-engine-ratio-threshold-checks` | **Date**: 2026-07-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/003b-engine-ratio-threshold-checks/spec.md`

## Summary

Close the one concrete gap `002a` found in `p0/qc_engine/engine.py`'s `ratio_threshold` branch — it
only supports `ratio in ("ltv", "dti")`, but real THRESHOLD-archetype rows include plain single-field
numeric floors (e.g. a minimum credit score) that are not ratios at all — by adding a
`ratio="field_value"` mode to the existing branch, removing a confirmed-dead line found while reading
the branch closely, and proving the already-correct parts (`ltv`/`dti`) plus the new mode hold across
a representative sample of the real THRESHOLD archetype (853 conditions), not just the demo's single
hand-authored check. This is a hardening feature, not a new-architecture feature: no new `Check.kind`
or dataclass field is introduced.

## Technical Context

**Language/Version**: Python 3.9-compatible (project-wide constraint).
**Primary Dependencies**: None new — the fix adds one `elif` branch (~15 lines) to an existing
function (`p0/qc_engine/engine.py::_eval_check`) plus removes one dead line; test fixtures reuse
`CanonicalLoan`/`SourceValue` (`model.py`) and `Check` (`ruleset.py`) unmodified.
**Storage**: None new. Test fixtures are constructed in-memory, mirroring `003a`'s
`test_predicate_archetypes.py` pattern.
**Testing**: Extends `p0/tests/test_p0.py` with the FR-001/002/004 regression tests (new
`field_value` mode + dead-line removal), plus a new `p0/tests/test_threshold_archetypes.py` covering
FR-005/006/007 (SC-002/003/005) — pass-case/fail-case/boundary sets for LTV, DTI, and the real
`ratio_threshold-00` credit-score-floor row drawn from
`p0/experiment_002a/artifacts/sampled_rows.json` (no fabricated conditions).
**Target Platform**: Local execution, same as all of `p0/` — no service.
**Project Type**: Vocabulary-widening fix + test hardening to the existing `qc_engine` package.
**Performance Goals**: N/A — no change to the engine's O(1)-per-check evaluation cost; the new
`elif` branch adds one comparison path, not a loop or new I/O.
**Constraints**: Zero regression against the existing P0 golden set and `harness.py`'s bit-exact
digest (SC-006) — `ltv`/`dti` behavior must be byte-for-byte unchanged; only a new `ratio` value
(`field_value`) is added, and one dead line is removed with no observable effect (SC-004 proves this
directly via the unchanged digest, not just by inspection).
**Scale/Scope**: A representative constructed sample per case (LTV pass/fail/boundary, DTI
pass/fail, and the one real `field_value` row `002a` actually sampled — `ratio_threshold-00`), not an
attempt to construct all 853 real conditions individually (that exhaustive construction is `005`'s
eventual job, once its scenario-generation is data-driven off the field catalog — see
`output/ROADMAP.md` §005's v0.6 amendment). `003b` proves the *mechanism* is correct at
representative scale for the vocabulary it introduces, the same limited claim `003a` made for
predicate scale.

## Constitution Check

*GATE: evaluated against `.specify/memory/constitution.md` v1.1.0.* *(Corrected 2026-07-26: constitution was already v1.1.1 at this plan's date — the version cite was stale; no gate outcome changes.)*

| Principle | Status | Note |
|---|---|---|
| I — Determinism of the correct computation | ✅ PASS | `field_value` is a pure Decimal comparison over the loan's truth value (`M.to_decimal` + `chk.operator`), no float, no wall-clock, no network. Removing the dead `res.threshold` line does not change any computed verdict. |
| II — Compile, then run | ✅ PASS / N/A | No LLM touches this feature — it evaluates already-signed `Check`s produced by `002b`. FR-008 explicitly refuses to decompose the multi-condition real rows, which would require judgment calls this engine spec does not make. |
| III — Eval is foundational | ✅ PASS | SC-002/003/005 make correctness across LTV/DTI/field_value and zero-false-auto-clear explicit, testable gates — not asserted by extrapolation from the one demo check, matching `003a`'s bar. |
| IV — Build the core, assume the periphery | ✅ PASS | This is the Apply-surface engine itself — the core. No extraction or LOS-integration work is touched (FR-008). |
| V — Source independence | N/A this feature | `ratio_threshold` checks (LTV/DTI/field_value) are single-source (doc/facts only) by definition — no `system_value()` comparison. Source independence is `003c`'s (reconcile) concern. |
| VI — Configurable by non-technical users | N/A this feature | No authoring-surface change; this feature touches only the engine's evaluation logic. |
| VII — Configuration is authored data | ✅ PASS | `Check.ratio`'s new `"field_value"` value is already authored data per `002b`'s existing `Check` schema (no new field); this feature widens the *evaluated* vocabulary of an existing authored-data field, not the schema itself. |

**No unjustified violations. Complexity Tracking is empty.**

## Project Structure

### Documentation (this feature)

```text
specs/003b-engine-ratio-threshold-checks/
├── spec.md
├── plan.md                  # This file
└── tasks.md                 # Phase 2 output (/speckit-tasks)
```

No `research.md` / `data-model.md` / `contracts/` — deliberately omitted, same precedent `003a`
established: this feature introduces no new entity, schema, or architecture decision to research; it
widens an existing field's accepted vocabulary and hardens test coverage around an already-designed
function.

### Source Code (repository root)

```text
p0/qc_engine/
├── engine.py                # MODIFIED — _eval_check's ratio_threshold branch: add
│                             #   `elif chk.ratio == "field_value"` (FR-001/002), remove the dead
│                             #   `res.threshold = ...` line (FR-004).
├── money.py                  # existing — unchanged (field_value reuses M.to_decimal directly, no
│                             #   new quantize scale — a raw field value has no policy-mandated
│                             #   rounding scale the way a computed LTV/DTI percent does)
├── model.py                 # existing — unchanged
├── ruleset.py                # existing — unchanged (no new Check fields; "field_value" is a new
│                             #   accepted string value for the existing `ratio` field)
└── catalog.py                 # existing — unchanged (the referential-integrity exemption for
                              #   ratio_threshold checks with field_name="" already does not apply
                              #   to field_value checks, which have a real field_name)

p0/tests/
├── test_p0.py                 # EXTENDED — regression tests for FR-001/002/004 (the new mode + the
│                             #   dead-line removal) + confirmation that pre-existing ltv/dti
│                             #   behavior is unchanged
└── test_threshold_archetypes.py   # NEW — FR-005/006/007 (SC-002/003/005): pass/fail/boundary sets
                              #   for LTV, DTI, and the real ratio_threshold-00 row, drawn from
                              #   p0/experiment_002a/artifacts/sampled_rows.json
```

**Structure Decision**: A targeted addition to `engine.py`'s existing `_eval_check` function — no new
module, mirroring `003a`'s "modify one function, no new module" shape. Test coverage splits into two
files for the same reason `003a` split them: `test_p0.py` keeps the direct fix regression (small,
mechanical), while `test_threshold_archetypes.py` holds the archetype-scale coverage, so "is the
vocabulary gap closed" and "does the branch hold up across the real archetype set" stay independently
readable and re-runnable.

## Complexity Tracking

*No entries — no Constitution Check violations require justification.*

## Implementation Notes (post-hoc — what was actually built)

Implemented per `tasks.md` (T001–T019 complete). No amendments — the plan matched what was built
exactly, which is expected for a fix this scoped: a new `elif` branch (~14 lines) in `_eval_check`,
one dead-line removal, and two test files.

- **The fix (T007)** was exactly as scoped: `elif chk.ratio == "field_value":` reads `sv.doc`
  (already resolved at the top of `_eval_check` via `loan.get(chk.field_name)`), returns
  `NOT_APPLICABLE` early on `None` (mirroring `ltv`/`dti`'s missing-facts pattern), otherwise sets
  `value = M.to_decimal(sv.doc)` with no quantize — falling through to the existing threshold-compare
  code shared with `ltv`/`dti`. The dead `res.threshold = chk.threshold if hasattr(res, "threshold")
  else None` line (T008) was deleted outright; `res.tolerance = chk.threshold` (unchanged, two lines
  later) already carries the audit-relevant value, confirmed by `test_dead_threshold_attribute_never_serialized`
  passing identically before and after.
- **Result**: 5 new regression tests in `p0/tests/test_p0.py` (69 total, up from 64) + 7 new tests in
  the new `p0/tests/test_threshold_archetypes.py` (US2/US3: LTV/DTI/field_value archetype coverage,
  an exact-boundary case, zero-false-auto-clear, and the confidence-gate proof) = 76 total across the
  suite. `p0/eval_synth/test_properties.py`'s 7 tests unaffected. `p0/harness.py`'s determinism digest
  is **byte-identical before/after this feature**
  (`8510a0a8b4b6996e047fc8534e094394ba72aae396305b0d2ecad3d6924634db` — the same digest `001a`'s and
  `003a`'s plan.md both recorded) — SC-006 proven directly, not assumed.
- **US3's confidence-gate finding turned out to be a genuine, useful discovery, not just a
  regression check**: `ltv`/`dti` checks (`field_name=""`, reading `loan.facts`) resolve to the
  model's default empty `SourceValue` at the confidence-gate check, so they **structurally cannot**
  carry a real `doc_confidence` — the gate has never been reachable by any `ratio_threshold` check
  until `field_value`. `test_ltv_dti_confidence_structurally_unreachable` (T017) records this
  explicitly so the asymmetry between `field_value`'s and `ltv`/`dti`'s confidence-gate behavior
  reads as intentional in future work, not an inconsistency to "fix."
- **Only the real, 002a-sampled `ratio_threshold-00` row was used for `field_value` proof**, per
  spec.md's Assumptions — `-01`/`-02`/`-03`/`-04` were confirmed by `002a`'s own review to bundle
  multiple comparisons into a single AMQ row and are explicitly out of scope (FR-008); no fabricated
  condition was substituted for them.
- **`p0/experiment_002a/`'s throwaway artifacts were read, not modified** — `sampled_rows.json` was
  consumed as a fixture source (T010) exactly as `003a` consumed `taxonomy.json`'s `examples`, per the
  same "throwaway code stays throwaway" precedent `002b`/`003a` established.
