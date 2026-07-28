# Implementation Plan: Reconcile Check Engine

**Branch**: `003c-engine-reconcile-checks` | **Date**: 2026-07-16 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/003c-engine-reconcile-checks/spec.md`

## Summary

Unlike `003a`/`003b`, this feature closes no vocabulary gap in existing code — `p0/qc_engine/engine.py`'s
`agree_categorical`/`agree_numeric` branches already work, generically, for any named source
(proven by `001b`'s tests and exercised by `demo_ruleset()`'s 6 checks plus
`000-synthetic-fixture-generation`'s `chk-def-fha-case-number`). What's missing is proof at the scale
of the real reconcile archetypes (INACCURATE 263 + MISMATCH 139 ≈ 402 conditions), anchored on the
one real, structurally-clean, doc-vs-system sampled row (`reconcile-01`, an SSN discrepancy), plus an
explicit, tested proof that the FLAG-vs-FAIL / RECONCILE-vs-QC phase partition holds safely in both
directions at that scale. This is a proof-and-documentation feature, not a code-change feature: **no
new `Check.kind`, no new dataclass field, and — per spec.md's own discovery — no attempt to build
doc-vs-doc comparison**, which the real MISMATCH archetype's examples predominantly need but which
the current `SourceValue` model (one `doc` slot + named system sources) cannot represent. That gap is
named, not silently absorbed into this feature's scope (see spec.md Edge Cases/Assumptions and
`output/ROADMAP.md` Tension #5).

## Technical Context

**Language/Version**: Python 3.9-compatible (project-wide constraint).
**Primary Dependencies**: None new — this feature adds **zero lines** to `engine.py`/`model.py`/
`ruleset.py`/`reconcile.py`; it constructs test fixtures against the already-implemented
`agree_categorical`/`agree_numeric` branches, reusing `CanonicalLoan`/`SourceValue` (`model.py`) and
`Check` (`ruleset.py`) unmodified.
**Storage**: None new. Test fixtures are constructed in-memory, same pattern as `003a`'s
`test_predicate_archetypes.py` and `003b`'s `test_threshold_archetypes.py`.
**Testing**: New `p0/tests/test_reconcile_archetypes.py` covering US1 (FR-001/002 — the real
`reconcile-01` SSN-discrepancy row, plus representative `agree_categorical`/`agree_numeric` pairs at
agreement/genuine-divergence/one-side-absent/both-absent) and US2 (FR-003/004 — a mixed ruleset
proving the FLAG-vs-FAIL phase partition holds in both directions, zero leakage either way).
**Target Platform**: Local execution, same as all of `p0/` — no service.
**Project Type**: Archetype-scale proof + honest scope documentation for an already-implemented
engine branch — even more so than `003b` (which at least added one new `elif` branch), this feature
changes no engine code at all.
**Performance Goals**: N/A — no engine change; no new evaluation cost.
**Constraints**: Zero regression against the existing P0 golden set, `001b`'s reconcile tests,
`demo_ruleset()`'s 6 reconcile checks, `000`'s `chk-def-fha-case-number`, and `harness.py`'s bit-exact
digest. A reconcile `FLAG` must never appear in `qc_failures`/`exceptions` or block `auto_cleared`
(SAFE gate); a genuine QC failure must never be misclassified as a reconcile `FLAG` in a mixed
ruleset (the inverse SAFE direction, novel to this feature — `003a`/`003b` never ran a check kind
requiring both directions to be adversarially proven together).
**Scale/Scope**: A representative constructed sample anchored on the one real `002a`-sampled,
structurally-clean doc-vs-system row (`reconcile-01`) plus representative categorical/numeric
agree-pairs and a mixed-ruleset FLAG-vs-FAIL scenario — not an attempt to construct all 402 real
conditions individually (`005`'s eventual job, per `003b`'s own precedent). Scope explicitly
**excludes** the doc-vs-doc majority of real MISMATCH conditions (employment dates, loan purpose,
title vesting — see spec.md) and the two ambiguous real rows (`reconcile-00`; INACCURATE's
completeness-flavored examples) whose comparison structure isn't confirmed from the AMQ text alone —
named as open questions, not resolved here.

## Constitution Check

*GATE: evaluated against `.specify/memory/constitution.md` v1.1.1.*

| Principle | Status | Note |
|---|---|---|
| I — Determinism of the correct computation | ✅ PASS | `agree_categorical`/`agree_numeric` already use pure, deterministic normalizers (`reconcile.py`) and `Decimal`/`within_tolerance` for numeric comparison — no float, no wall-clock, no network. This feature adds no new computation path, only proves the existing one at scale. |
| II — Compile, then run | ✅ PASS / N/A | No LLM touches this feature — it evaluates already-signed `Check`s produced by `002b`. FR-006 explicitly refuses to resolve ambiguous real rows (`reconcile-00`, INACCURATE's examples) rather than guessing at their intended comparison structure. |
| III — Eval is foundational | ✅ PASS | SC-001–004 make correctness at real-archetype scale and the FLAG-vs-FAIL partition (both directions) explicit, testable gates — not asserted by extrapolation from the demo's 6 checks. |
| IV — Build the core, assume the periphery | ✅ PASS | This is the Apply-surface engine's Step-1 (reconcile) — the core. No extraction/LOS work touched (FR-007). |
| V — Source independence | ✅ PASS | This IS the source-independence feature — `agree_categorical`/`agree_numeric` compare the independently-populated doc (truth) and system (`los`/`mismo`) paths `001b`'s N-source envelope generalized. FR-005 is the honest boundary of that claim: independence across doc-vs-*system* is proven; doc-vs-*doc* (two independent documents, neither a system source) is a distinct, unbuilt capability, named not assumed. |
| VI — Configurable by non-technical users | N/A this feature | No authoring-surface change; this feature touches only test/proof coverage of an existing evaluation branch. |
| VII — Configuration is authored data | ✅ PASS | No new `Check` fields introduced; `kind="agree_categorical"/"agree_numeric"`, `normalizer`, `tolerance` are exactly the existing authored-data shape `002b`'s compiler already emits. |

**No unjustified violations. Complexity Tracking is empty.**

## Project Structure

### Documentation (this feature)

```text
specs/003c-engine-reconcile-checks/
├── spec.md
├── plan.md                  # This file
└── tasks.md                 # Phase 2 output (/speckit-tasks)
```

No `research.md` / `data-model.md` / `contracts/` — same precedent `003a`/`003b` established: this
feature introduces no new entity, schema, or architecture decision to research. The one genuine
discovery this feature surfaces (the doc-vs-doc majority of real MISMATCH conditions, and the
ambiguous `reconcile-00`/INACCURATE rows) is a **scope boundary**, not a design question this feature
resolves — it is documented directly in spec.md's preamble/Edge Cases/Assumptions and tracked as
`output/ROADMAP.md` Tension #5, the same place `003b` put its own bundled-condition-rows finding
rather than inventing a separate research artifact for it.

### Source Code (repository root)

```text
p0/qc_engine/
├── engine.py                 # UNCHANGED — agree_categorical/agree_numeric branches already
│                              #   implemented (proven by 001b); this feature adds zero lines here.
├── reconcile.py               # UNCHANGED — normalizer table already implemented.
├── model.py                   # UNCHANGED — SourceValue's one doc + named-system-sources shape is
│                              #   exactly what this feature proves correct; NOT extended to
│                              #   represent multiple named document sources (spec.md FR-005).
└── ruleset.py                 # UNCHANGED — no new Check fields.

p0/tests/
└── test_reconcile_archetypes.py   # NEW — US1/US2 (FR-001–004, SC-001–004): the real reconcile-01
                              #   (SSN discrepancy) pass/flag cases, representative agree_categorical/
                              #   agree_numeric pairs (agreement, genuine divergence via
                              #   eval_synth.generator's assert_independently_constructed discipline,
                              #   one-side-absent, both-absent), and a mixed ruleset (agree_* +
                              #   predicate + ratio_threshold) proving the FLAG-vs-FAIL partition
                              #   holds in both directions.
```

**Structure Decision**: No engine module changes at all — this feature is pure test/proof coverage
added as one new file, `test_reconcile_archetypes.py`, mirroring `003a`'s
`test_predicate_archetypes.py` and `003b`'s `test_threshold_archetypes.py` naming and shape. Kept
separate from `p0/tests/test_p0.py` for the same reason `003a`/`003b` split theirs: the direct
mechanism (already proven, unchanged) stays in `test_p0.py`'s existing `001b` reconcile tests, while
this feature's new archetype-scale coverage is independently readable and re-runnable on its own.

## Complexity Tracking

*No entries — no Constitution Check violations require justification.*

## Implementation Notes (post-hoc — what was actually built)

Implemented per `tasks.md` (T001–T013 complete). No amendments — the plan matched what was built
exactly, which is expected for a proof-only feature: one new test file, zero engine code changes.

- **All 11 tests passed on their first run**, unlike `003a`/`003b`'s red-then-green fixes — expected
  and correct, since `agree_categorical`/`agree_numeric` were already fully implemented (proven by
  `001b`) before this feature began. `git diff --stat` against `engine.py`/`model.py`/`ruleset.py`/
  `reconcile.py`/`catalog.py`/`money.py` confirmed zero lines changed in any engine module.
- **US1 (T002–T006)**: the real `reconcile-01` (SSN discrepancy) row anchors the agreement/divergence
  proof, mirroring `demo_ruleset()`'s own `chk-borrower-ssn` shape under an independent check id (so
  this feature's proof coverage never depends on `ruleset_demo.py`'s digest-pinned content). The
  genuine-divergence fixture (T004) and the outside-tolerance `agree_numeric` fixture (T005) both
  route through `eval_synth.generator.assert_independently_constructed` before asserting — the same
  independence-guard discipline `001b`'s own tests apply, confirming the "divergence" is real and not
  a mutation that silently left `sources` unchanged.
- **US2 (T007–T011)**: a 3-check mixed ruleset (`agree_categorical` SSN + `predicate` note-signed +
  `ratio_threshold` LTV) proves the FLAG-vs-FAIL partition holds in all four combinations
  (divergence-only, QC-failure-only, both-together, and a 2-loan batch generalizing each direction
  across multiple fixtures) — `borrower_ssn`/`note_signed` are both pre-existing `p0-seed-catalog`
  fields, so the mixed ruleset passes `catalog.validate_referential_integrity` without inventing new
  catalog entries.
- **Result**: 11 new tests in the new `p0/tests/test_reconcile_archetypes.py` (115 total across the
  suite, up from 104). `p0/harness.py`'s determinism digest is **byte-identical before/after this
  feature** (`8510a0a8b4b6996e047fc8534e094394ba72aae396305b0d2ecad3d6924634db` — the same digest
  every prior spec's plan.md has recorded since `001a`) — SC-006 proven directly. `25/25` known
  defects (`000-synthetic-fixture-generation`'s own gate) unaffected.
- **The doc-vs-doc exclusion held exactly as scoped** — no task in `tasks.md` touched it, and no
  implementation pressure arose to quietly patch it in. It remains tracked at
  `output/ROADMAP.md` Tension #5, not resolved here.
