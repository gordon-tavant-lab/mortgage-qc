# Implementation Plan: Field Catalog

**Branch**: `001a-field-catalog` | **Date**: 2026-07-01 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001a-field-catalog/spec.md`

## Summary

Generalize the engine's fixed, hardcoded loan field slots into a schema-driven, signed field
catalog — authored data that declares every field's type, expected sources, and citation/confidence
requirements — so the engine scales to hundreds of fields (the 800+ checks) without engine code
changes, and so a check's field reference can never silently resolve to nothing (the referential-
integrity SAFE gate). This is the engine's true prerequisite: `003a/b/c` (the archetype slices) and
`002b` (the compiler) both consume the vocabulary this feature declares.

## Technical Context

**Language/Version**: Python 3.9-compatible (project-wide constraint).
**Primary Dependencies**: None new — stdlib `json` + `hashlib` only, reusing
`p0/qc_engine/ruleset.py`'s exact canonical-hashing pattern.
**Storage**: A single JSON file (`p0/qc_engine/field_catalog.json`), co-located with engine code.
**Testing**: Extends `p0/tests/test_p0.py` — referential-integrity tests, catalog-hashing tests,
zero-regression tests against the existing golden set. No new framework.
**Target Platform**: Local execution, same as all of `p0/` — no service.
**Project Type**: Library extension to the existing `qc_engine` package.
**Performance Goals**: N/A — catalog validation is a one-time, load-time operation, not a per-loan
or per-check runtime cost.
**Constraints**: Zero regression against the P0 golden set (SC-002); the per-field envelope shape
must stay fixed even as the field set grows (Principle VII, FR-002).
**Scale/Scope**: Schema must represent the vocabulary implied by all 4,192 classified conditions in
`taxonomy.json` without further schema changes (SC-004) — authoring all 4,192 entries is not in
scope for this feature.

## Constitution Check

*GATE: evaluated against `.specify/memory/constitution.md` v1.1.0.*

| Principle | Status | Note |
|---|---|---|
| I — Determinism of the correct computation | ✅ PASS | The catalog is static, signed, authored data — it introduces no model, network, or wall-clock into any evaluation path. Referential-integrity validation runs once at load time, not per-loan. |
| II — Compile, then run | ✅ PASS / N/A | No LLM is involved in this feature at all — the catalog is hand-authored for the MVP (spec.md Assumptions); LLM-assisted authoring is `009c`, unspecced and conditional. |
| III — Eval is foundational | ✅ PASS | SC-002 makes zero-regression against the existing P0 golden set + eval_synth property tests an explicit, testable gate — the catalog's introduction is proven not to change engine behavior, not merely assumed to be safe. |
| IV — Build the core, assume the periphery | ✅ PASS | This is the engine's vocabulary layer — squarely "the core" (Apply surface). No extraction or LOS-integration work is touched. |
| V — Source independence | ✅ PASS / N/A | `expected_sources` is declarative metadata about *which* sources a field expects, not a comparison mechanism itself — the actual doc-vs-system independence guarantee is `001b`'s and `003c`'s concern, both downstream of this feature. |
| VI — Configurable by non-technical users | N/A this feature | Authoring UX is `009`, unspecced. The catalog is hand-authored JSON for the MVP (spec.md Assumptions), consistent with 001a's own scope note. |
| VII — Configuration is authored data | ✅ PASS (this is what the feature implements) | The catalog is authored → (procedurally reviewed, pending 009) → identified by SHA-256 → consumed by a version-pinned interpreter (the referential-integrity validator + the engine). Directly implements the fluid-field-set / fixed-envelope boundary Principle VII names. |

**No unjustified violations. Complexity Tracking is empty.**

## Project Structure

### Documentation (this feature)

```text
specs/001a-field-catalog/
├── spec.md
├── plan.md                  # This file
├── research.md               # Phase 0 — JSON-not-YAML, load-time-not-runtime validation
├── data-model.md             # Phase 1 — FieldCatalogEntry, FieldCatalog, FieldEnvelope, validator
├── contracts/
│   └── field-catalog-schema.md   # Pinned JSON schema (closes GAP 1 for this feature)
├── quickstart.md              # Phase 1 — the day-to-day "add a field" workflow
└── tasks.md                   # Phase 2 output (/speckit-tasks — not created by this plan)
```

### Source Code (repository root)

A durable extension to the existing `qc_engine` package — not a new service, not a throwaway spike
(unlike `002a`). New files sit alongside the existing engine modules, matching the codebase's
established convention (code + its data file co-located, per `p0/eval_synth/taxonomy.py` +
`taxonomy.json`):

```text
p0/qc_engine/
├── __init__.py            # existing — export FieldCatalog, FieldCatalogEntry, validate_referential_integrity
├── model.py                # existing — SourceValue/CanonicalLoan; FieldEnvelope maps onto SourceValue, no change needed here for 001a
├── ruleset.py               # existing — Check/Ruleset; referenced for the canonical-hashing pattern this feature reuses
├── engine.py                # existing — unchanged by this feature (validation happens before run(), not inside _eval_check)
├── catalog.py               # NEW — FieldCatalogEntry, FieldCatalog dataclasses; canonical_content()/sha256() mirroring Ruleset's pattern
├── field_catalog.json       # NEW — the authored catalog data file (empty/seed entries initially; grows as 003a/b/c land)
└── (validation lives in catalog.py, e.g. validate_referential_integrity(ruleset, catalog))

p0/tests/
└── test_p0.py               # EXTENDED — new tests: referential-integrity rejection, catalog hash stability,
                              #   zero-regression against the existing golden set with the catalog in the load path
```

**Structure Decision**: New module `catalog.py` alongside the existing `qc_engine` modules, not a
new top-level package — this is a vocabulary layer the existing engine consumes, not a separate
service. Mirrors the `taxonomy.py` + `taxonomy.json` code-and-data-together convention already
established in `p0/eval_synth/`, and reuses `ruleset.py`'s exact hashing shape rather than
introducing a second canonicalization scheme.

## Complexity Tracking

*No entries — no Constitution Check violations require justification.*

## Implementation Notes (post-hoc — what was actually built)

Implemented per `tasks.md` (T001–T018 complete; this note is T019). One amendment surfaced during
implementation, not anticipated at plan time:

- **[Superseded 2026-07-26 — see note at end of this bullet]** **`property_value` dropped from the seed catalog.** The plan assumed 6-7 demo fields including
  `property_value`, but tracing the actual engine code (`p0/qc_engine/engine.py`'s `ratio_threshold`
  branch) showed it's read exclusively via `loan.facts`, never through a `field_name`-based `Check`
  — the LTV check (`chk-ltv-max`) carries `field_name=""` by design. Cataloging `property_value` as
  a field-catalog entry would have misrepresented scope (it would sit permanently in the
  unused-entries report, FR-008, for a reason unrelated to what that report exists to surface). The
  referential-integrity validator (`validate_referential_integrity`) explicitly exempts
  `ratio_threshold` checks with an empty `field_name` — a small, honest scope boundary matching
  `model.py`'s own facts-vs-fields distinction, not a workaround.
  **[2026-07-26 note, spec audit]**: a later working-tree change (uncommitted at audit time) adds
  `property_value` to `field_catalog.json` (377 → 378 entries) as part of the document-extraction
  coverage expansion — the original exclusion rationale (the demo LTV check reads its operands
  internally) still holds for the *demo* check, but the field is now a real extracted document value
  in its own right. Disclosed here so the exclusion note above doesn't silently contradict the
  shipped catalog.
- **Result**: 7 seed catalog entries (`borrower_name`, `borrower_ssn`, `note_rate`, `loan_amount`,
  `property_address`, `flood_zone`, `note_signed`), all referenced by the existing demo ruleset,
  zero unused entries. 10 new tests added to `p0/tests/test_p0.py` (29 total, all passing).
  `p0/harness.py`'s determinism digest is byte-identical before/after this feature
  (`8510a0a8b4b6996e047fc8534e094394ba72aae396305b0d2ecad3d6924634db`) — SC-002 proven directly, not
  assumed.

## Future Scaling Note (added 2026-07-01, from prior-art audit)

`output/PRIOR-ART-OLAV-MORTGAGE-QC.md` identifies `examples/mortgage-qc/config/qc_questions.json` and
`block_questions.json` — a real, lender-curated question/exception-code vocabulary derived from the
same AMQ workbooks `taxonomy.py` parses — as a candidate **additional** grounding source when this
catalog scales beyond its current 7-field seed toward the full 800+ checks. This does not change what
was built (the seed catalog and referential-integrity mechanism are unaffected); it's a note for
whoever authors the next batch of catalog entries to consult that source alongside `taxonomy.json`'s
archetype classification, which serves a different purpose (synthetic eval generation, not the real
vocabulary itself).
