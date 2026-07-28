# Data Model: Compile-Fidelity Spike

All entities are throwaway artifacts for this spike (flat files), not durable system state.
Field names match what `p0/eval_synth/taxonomy.py` and `p0/qc_engine/ruleset.py` already use,
so the spike's outputs plug directly into the existing scorer without translation.

## SampledWorkbookRow

One real AMQ defect condition drawn from `demo/rules/*.xlsx`, the unit of compile input (FR-001).

| Field | Type | Source | Notes |
|---|---|---|---|
| `row_id` | string | workbook row index | stable identifier back to the source file/row |
| `question_text` | string | AMQ column (question) | the SME-facing question |
| `response_text` | string | AMQ column 7 (response) | the defect condition — the failure mode itself |
| `exception_code` | string | AMQ column 9 | maps toward `taxonomy.py`'s archetype classification |
| `significance` | string | AMQ column 10 | severity tag already encoded in the sheet |
| `archetype` | enum: predicate / ratio_threshold / reconcile | derived via `taxonomy.py` classification | drives FR-007's stratified sampling |
| `amq_category` | string | workbook sheet/category | reported alongside findings (SC-006), not stratified on (research.md #1) |

## CompiledRuleDraft

The LLM's config-time output for one `SampledWorkbookRow` — a candidate rule before SME review (FR-002).

| Field | Type | Source | Notes |
|---|---|---|---|
| `row_id` | string | links back to `SampledWorkbookRow` | |
| `check_kind` | enum: predicate / ratio_threshold / agree_categorical / agree_numeric | LLM output | must match `p0/qc_engine/ruleset.py`'s `Check` kind vocabulary |
| `field_name` | string | LLM output | must resolve against the field catalog (001a) once it exists; for this spike, checked for internal consistency only (001a is a sibling dependency, not yet implemented) |
| `comparison` | object (operator + threshold/expected value) | LLM output | the executable predicate itself |
| `plain_english_restatement` | string | LLM output | required for the SME review artifact — lets Kayla judge intent without reading raw JSON. **Note added 2026-07-01**: for this throwaway spike, the field is used only during review, per the contract's own language. `002b` (the production compiler this spike de-risks) makes this permanent — the extracted intent is retained as part of the signed artifact, not discarded after sign-off (see `002b/spec.md` FR-011). Not a scope change here; this spike's own artifacts are throwaway regardless (FR-008). |
| `runnable` | bool | scored by `p0/eval_synth` | does it parse/execute as a valid `Check` at all |
| `constructed_label_score` | pass / fail | scored by `p0/eval_synth` | FR-003's runnability + correctness metric |

## InterpretationFidelityJudgment

The SME's independent verdict on one `CompiledRuleDraft`, made against the source row — the finding
User Story 2 exists to produce (FR-004).

| Field | Type | Source | Notes |
|---|---|---|---|
| `row_id` | string | links back to `SampledWorkbookRow` / `CompiledRuleDraft` | |
| `verdict` | enum: correct / incorrect / ambiguous | Kayla, reading `response_text` vs. `plain_english_restatement` | never derived from or overridden by `constructed_label_score` (FR-004, Edge Case 1) |
| `sme_correction` | string (free text) or structured `Check` edit | Kayla | the corrected rule if `verdict != correct` |
| `edit_distance` | int | computed via `p0/qc_engine/ruleset.py`'s existing edit-distance function | FR-005 — reuses the existing function, not a new metric |
| `reviewer_note` | string, optional | Kayla | free-text rationale, useful for `002b`'s eventual design even though this spike's code is throwaway |

## PreRegisteredDecisionRule

The locked, timestamped thresholds and PROCEED/RECONSIDER/KILL mapping — written before any row is
scored (FR-006, SC-001). See `pre-registration.md` (Phase 1 output, this plan) for the actual locked
document; this entity just names its required fields for traceability.

| Field | Type | Notes |
|---|---|---|
| `locked_at` | timestamp | must predate the first `constructed_label_score` (SC-001) |
| `interpretation_fidelity_threshold` | percent | e.g. "≥ X% correct → does not disqualify" |
| `sme_correction_threshold` | edit-distance stat | e.g. mean edit-distance below/above a stated bound |
| `verdict_mapping` | PROCEED / RECONSIDER / KILL rule | evaluated in a fixed order, mirroring G3's D1/D2/D3 structure |

## SpikeFinding (the deliverable)

The spike's single output artifact — everything else is throwaway (FR-008).

| Field | Type | Notes |
|---|---|---|
| `sample_archetype_distribution` | {predicate: n, ratio_threshold: n, reconcile: n} | SC-006 |
| `interpretation_error_rate` | percent | SC-004, distinct from `constructed_label` pass rate (FR-010) |
| `mean_edit_distance` | float | SC-004 |
| `zero_edit_batch_flag` | bool | User Story 3, Acceptance Scenario 2 — sign-off-theater signal |
| `verdict` | PROCEED / RECONSIDER / KILL | SC-005, evaluated against `PreRegisteredDecisionRule` |
