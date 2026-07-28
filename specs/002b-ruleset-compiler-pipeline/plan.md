# Implementation Plan: Ruleset Compiler Pipeline

**Branch**: `002b-ruleset-compiler-pipeline` | **Date**: 2026-07-02 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/002b-ruleset-compiler-pipeline/spec.md`
**Depends on**: `001a-field-catalog` (implemented), `002a-compile-fidelity-spike` (provisional
PROCEED, 2026-07-01 — AI self-review pending Kayla's confirmation).

## Summary

Scale the already-proven compile→correct→sign mechanism (`p0/qc_engine/ruleset.py`'s `Check`/
`RuleProvenance`/`Ruleset`, proven at an 8-check demo scale) and the compile pattern `002a` validated
at n=24 real rows into a production batch pipeline: chunked map-reduce over the real AMQ workbook
(research.md Decision 1), a pre-sign referential-integrity screen reusing `001a`'s validator
unmodified (Decision 4), a propose-then-sign path for field-catalog growth at batch scale
(Decision 2), automated consistency and pattern-risk flagging carried forward directly from what
`002a`'s self-review found (FR-003/007/008), and a permanent, retrievable intent-registration triple
per compiled check (FR-011, User Story 5) — so the audit trail explains not just the arithmetic but
the judgment a rule was compiled from. No new artifact format, no new signing mechanism, no runtime
LLM call anywhere.

## Technical Context

**Language/Version**: Python 3.9-compatible (project-wide constraint).
**Primary Dependencies**: `boto3` + Bedrock (reused pattern from `p0/experiment_002a/compile_llm.py`
/ `p0/experiment_g3/llm_arm.py`), `openpyxl` (reused from `p0/eval_synth/taxonomy.py`). **No new
dependencies** — fuzzy field-name matching (FR-003) reuses `ruleset.py`'s existing `_edit_distance`
helper rather than adding a library (research.md Decision 3).
**Storage**: Flat files — a signed `Ruleset` (extended with `intent_records`) and a grown
`FieldCatalog` (extended by signed `proposed_field_entry` additions), both already file-based
artifacts per `001a`/the existing `ruleset.py`. No database.
**Testing**: Extends `p0/tests/test_p0.py`; zero-regression against the existing golden set and hash
digests is a hard gate (every prior feature's determinism digest and catalog hash must remain
byte-identical, since this feature is purely additive to `Ruleset`/`FieldCatalogEntry`).
**Target Platform**: Local execution + one Bedrock API call per sampled row at compile time only
(FR-009) — no service, no network call inside `qc_engine.engine.run`.
**Project Type**: Production module under `p0/qc_engine/compiler/` — **not** an extension of
`p0/experiment_002a/`'s throwaway scripts (spec.md Edge Cases is explicit on this; that directory's
scripts stay untouched, per its own FR-008).
**Performance Goals**: N/A for this feature (a config-time batch job, not a per-loan runtime path);
batch size scoped to "N > 24" (SC-001), not the full 4,192-condition production corpus in one run (4,651 classified / 8,442 total in the regenerated post-010a taxonomy — count-basis note, 2026-07-26 audit).
**Constraints**: Every LLM call at config/compile time only (Principle II, FR-009); zero regression
against all existing test suites and hash digests; no new artifact schema (FR-001); no authoring UI
or product/program gating built here (FR-010).
**Scale/Scope**: Proves the pipeline at production batch scale (dozens-to-hundreds of rows, beyond
`002a`'s n=24) — not the full workbook in one pass; running the full 4,192-condition corpus through
this pipeline is a later, operational use of the same mechanism, not a requirement of this feature.

## Constitution Check

*GATE: evaluated against `.specify/memory/constitution.md` v1.1.1.*

| Principle | Status | Note |
|---|---|---|
| I — Determinism of the correct computation | ✅ PASS | The compile pipeline never changes how `qc_engine.engine.run` executes a signed `Ruleset` — it only produces one. SC-005 makes "zero LLM/network calls during `engine.run`" an explicit, tested gate, not an assumption. |
| II — Compile, then run | ✅ PASS (this is what the feature implements) | Every LLM call is confined to the map step (FR-009); FR-011's intent-registration is documented explicitly as an audit-record addition, not a second runtime path — the engine still reads only the compiled `Check`. Sign-off binds to the human-corrected artifact and edit-distance is measured (FR-004, reusing `RuleProvenance` verbatim); zero-edit batches are flagged loudly (FR-006), never silently passed. |
| III — Eval is foundational | ✅ PASS / scope note | This feature does not build a new eval mechanism — `005-eval-harness-as-promotion-gate` is where CI-scale scoring of compiled rulesets lands (roadmap distinction already established: `002a` uses the pre-existing `eval_synth` scorer directly; `005` productionizes it). `002b`'s own correctness gate is narrower and already fully specified: referential integrity before sign-off (User Story 3) and the two `002a`-derived pattern flags (User Story 4) — not a re-invention of eval. |
| IV — Build the core, assume the periphery | ✅ PASS | FR-010 explicitly excludes the authoring UI (`009a/b/c`) and product/program gating (`010a/b`) from this feature's surface; extraction/LOS integration remain untouched. |
| V — Source independence | ✅ PASS | This feature doesn't touch runtime source reconciliation (that's `003c`'s engine slice). It reinforces the principle at compile time instead: FR-008's `archetype_mismatch_risk` flag exists specifically to catch a drafted `agree_categorical`/`agree_numeric` check whose source condition is *not* a genuine two-independent-source comparison at all (`002a`'s `reconcile-00`/`reconcile-01` finding) — i.e., it flags a compile-time risk of a check that would silently violate Principle V once it reached the engine, before that ever happens. |
| VI — Configurable by non-technical users | N/A this feature | The authoring UI (`009a/b/c`) does not exist yet; sign-off in this feature is direct data inspection of the batch report (`contracts/batch-report-schema.md`), the same procedural posture `001a`/`002a` already used and explicitly disclosed as provisional until `009` ships. |
| VII — Configuration is authored data | ✅ PASS (this is what the feature extends) | This feature is the first to apply Principle VII's "one model across all four authored layers" claim concretely across *two* layers in a single pipeline: checks (existing `Check`/`RuleProvenance`) **and** the field-catalog vocabulary (`FieldCatalogEntry`, via the new propose-then-sign path, research.md Decision 2) — both authored → SME-corrected → signed → identified by SHA-256 → executed by version-pinned code. No new mechanism invented; the existing signing pattern is applied to a second layer. |

**No unjustified violations. Complexity Tracking is empty.**

## Project Structure

### Documentation (this feature)

```text
specs/002b-ruleset-compiler-pipeline/
├── spec.md
├── plan.md                          # This file
├── research.md                      # Phase 0 — 4 decisions: batch strategy, catalog growth,
│                                     #   duplicate detection, referential-integrity screening
├── data-model.md                    # Phase 1 — CompiledCheckDraft, RuleIntentRecord,
│                                     #   ConsistencyReport, PatternFlag, batch referential screen
├── contracts/
│   ├── compiled-check-draft-schema.md   # LLM → structured output (generalizes 002a's contract)
│   └── batch-report-schema.md            # the reduce-step / pre-sign SME review artifact
├── quickstart.md                    # Phase 1 — the 7-step run sequence
└── tasks.md                         # Phase 2 output (/speckit-tasks — not created by this plan)
```

### Source Code (repository root)

A fresh, production-scoped package — not an extension of `p0/experiment_002a/`'s throwaway scripts
(spec.md Edge Cases; that spike's own FR-008 disclaims exactly this):

```text
p0/qc_engine/
├── ruleset.py                # EXTENDED — new RuleIntentRecord dataclass; Ruleset gains
│                              #   intent_records: List[RuleIntentRecord] (additive, NOT part of
│                              #   canonical_content(), so sha256() is unaffected); intent_for()
│                              #   lookup method. Check, RuleProvenance, existing Ruleset fields
│                              #   UNCHANGED — Ruleset.sha256()/unedited_rules()/signoff_summary()
│                              #   reused verbatim, not modified.
├── catalog.py                 # UNCHANGED — validate_referential_integrity, FieldCatalogEntry,
│                              #   FieldCatalog reused verbatim (research.md Decision 4: wrapped,
│                              #   never modified).
└── compiler/                  # NEW package — this feature's actual surface
    ├── __init__.py
    ├── sample.py               # generalizes experiment_002a/sample_rows.py: draws N > 24 real
    │                           #   rows from taxonomy.py's classified workbook rows
    ├── compile_llm.py          # the map step — generalizes experiment_002a/compile_llm.py's
    │                           #   proven Bedrock harness (Sonnet 4.6, temp=0, one row per call);
    │                           #   emits CompiledCheckDraft (check + source_text + extracted_intent
    │                           #   + optional proposed_field_entry)
    ├── consistency.py          # the reduce step — FR-003, ConsistencyReport via ruleset.py's
    │                           #   existing _edit_distance (no new dependency)
    ├── pattern_flags.py        # FR-007/FR-008 — deterministic regex/keyword heuristics (same
    │                           #   style as eval_synth/taxonomy.py's ARCHETYPES matching), NOT a
    │                           #   second LLM call
    ├── catalog_screen.py       # User Story 3 — screen_batch_referential_integrity(), wraps
    │                           #   catalog.validate_referential_integrity per-candidate-check
    └── report.py               # assembles contracts/batch-report-schema.md's shape from the
                                  #   map + reduce + screen outputs, for SME review

p0/tests/
└── test_p0.py                  # EXTENDED — SC-001 through SC-006, zero-regression re-verified
```

**Structure Decision**: New `p0/qc_engine/compiler/` package, not a modification to `ruleset.py`'s
or `catalog.py`'s existing logic beyond the one additive field on `Ruleset`. This mirrors `001a`'s
own structure decision (extend the data model additively; keep the proven signing mechanism
untouched) and keeps the compile pipeline's substantial new logic (LLM orchestration, heuristic
flagging, batch reporting) cleanly separated from the engine/artifact code every other feature
already depends on and has zero-regression-tested against.

## Complexity Tracking

*No entries — no Constitution Check violations require justification.*

## Implementation Notes (post-hoc — what was actually built)

Implemented per `tasks.md` (T001–T030 complete; T031 is this note). All 31 tasks landed; one
significant amendment surfaced during implementation — found via a real 30-row production batch
run against `demo/rules/*.xlsx`, not by inspection — documented rather than glossed over:

- **A malformed `proposed_field_entry` was silently discarding a perfectly valid compiled `Check`.**
  The first real end-to-end run (Sonnet 4.6, 30 real rows, seed `20260702`) produced 27/30
  successful compiles and **3 full parse failures** — all three `agree_categorical`-kind rows,
  all three failing with `FieldCatalogEntry '...': data_type=enum requires non-empty enum_values`.
  Reading the failure showed the *check itself* had compiled correctly; only the LLM's proposed new
  catalog entry (research.md Decision 2) was malformed (`data_type: "enum"` with no `enum_values`),
  and `compile_row`'s original single `try`/`except` wrapped *both* constructions together, so one
  bad proposal took down an otherwise-good `Check` with it. This directly matters for SC-001 (N real
  rows should produce N drafts) and User Story 3 (referential-integrity screening should be the
  thing that blocks a check, not an unrelated crash upstream of screening ever happening).
  - **Fix, two parts**: (1) `SYSTEM_PROMPT` now requires `enum_values` whenever
    `data_type: "enum"` is proposed, and instructs the model to prefer `"string"` over guessing at
    an enum's members when unsure — a prompt-level fix. (2) `compile_row` now separates `Check`
    construction (still a hard failure — an uncompileable check is genuinely unusable) from
    `FieldCatalogEntry` construction (a **soft** failure — the check is kept, `proposed_field_entry`
    is `None`, and the referential-integrity screen correctly reports it as `blocked` with the real
    reason, rather than the row vanishing from the batch entirely with a misleading "parse error").
  - **Verified**: a second real run with the identical seed and the same 30 rows produced **30/30**
    successful compiles, 0 full parse failures, 0 proposal rejections — confirming both the prompt
    fix and the error-isolation fix, not just one or the other.
- **Result**: `p0/qc_engine/compiler/` package (`sample.py`, `compile_llm.py`, `catalog_screen.py`,
  `consistency.py`, `pattern_flags.py`, `report.py`) built per plan.md's Structure Decision, with
  `Ruleset` extended by the additive `intent_records: List[RuleIntentRecord]` field (FR-011). 15 new
  tests added to `p0/tests/test_p0.py` (53 total, all passing), covering SC-001 through SC-006 via
  synthetic `CompiledCheckDraft` fixtures — deterministic and free, reserving the real Bedrock call
  for the manual quickstart run above, mirroring `002a`'s own precedent of keeping the live-LLM
  script outside the free/fast pytest suite. The pre-existing determinism digest
  (`8510a0a8b4b6996e047fc8534e094394ba72aae396305b0d2ecad3d6924634db`) and the `001a` field-catalog
  hash (`4a4fefe92d1f7b94396a16492ffa78b340e719b1963f905c821a6e2e82ee6189`) are both confirmed
  byte-identical after this feature — `Ruleset.intent_records` and the new `compiler/` package are
  purely additive, as designed.
- **Not yet done, by design**: no real batch has been *signed* (procedural SME sign-off, direct data
  inspection of `contracts/batch-report-schema.md`'s shape, per `001a`/`002a`'s own precedent — the
  authoring UI, `009a/b/c`, does not exist yet). The 30-row run above is a mechanism proof, not a
  production ruleset — every `FieldCatalogEntry` it proposed remains unsigned and the field catalog
  itself is unchanged on disk.
