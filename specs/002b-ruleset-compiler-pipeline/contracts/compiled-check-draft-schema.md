# Contract: Compiled Check Draft (production LLM → structured output)

The per-row LLM output contract for this feature's map step (research.md Decision 1). Generalizes
`002a`'s spike contract (`specs/002a-compile-fidelity-spike/contracts/compiled-rule-schema.md`) from
a throwaway n=24 scoring artifact into the permanent production shape — same `check` schema
(verbatim, no new fields on `Check` itself), with `plain_english_restatement` now framed as a
**retained field**, not a discard-after-review one (FR-011, User Story 5), plus one addition:
`proposed_field_entry` (research.md Decision 2).

## Required output (per sampled row)

```json
{
  "row_id": "string — links back to the source workbook row",
  "check": {
    "id": "string", "name": "string", "field_name": "string",
    "kind": "predicate | ratio_threshold | agree_categorical | agree_numeric",
    "severity": "CRITICAL | WARNING | INFO",
    "phase": "RECONCILE | QC",
    "sources": ["doc", "los"],
    "normalizer": "identity | ...", "tolerance": "0",
    "predicate": "is_true | is_present", "ratio": "ltv | dti",
    "threshold": "Decimal string percent", "operator": "<= | < | >= | > | ==",
    "message_pass": "string", "message_fail": "string"
  },
  "plain_english_restatement": "string — FR-011(b): the extracted intent. RETAINED PERMANENTLY as part of the signed Ruleset's intent_records — not discarded once SME review is complete. The engine never reads this field at evaluation time (Principle II unchanged); it is an audit-record field.",
  "proposed_field_entry": {
    "field_name": "string — matches check.field_name",
    "data_type": "string | decimal | date | boolean | enum",
    "expected_sources": ["doc", "los"],
    "citation_required": "boolean",
    "confidence_required": "boolean",
    "description": "string"
  }
}
```

`proposed_field_entry` is present **only** when `check.field_name` does not already resolve against
the current `001a` `FieldCatalog` at compile time — when present, it is a **draft** `FieldCatalogEntry`
(`p0/qc_engine/catalog.py`, unmodified schema) requiring its own SME sign-off before the catalog
actually grows (research.md Decision 2); it is never auto-registered.

## Validation (before a draft is eligible for sign-off)

1. `check.kind` MUST be one of the four values the engine already recognizes.
2. `check.field_name` MUST resolve against the `001a` catalog **or** carry a non-null
   `proposed_field_entry` — otherwise the draft is `blocked` (FR-002, User Story 3), not merely
   flagged.
3. `plain_english_restatement` MUST be non-empty — FR-011 requires the extracted-intent leg of the
   retained triple to exist for every signed check; an empty restatement is a compile failure, not a
   silently-permitted gap.
4. A row whose LLM output fails to parse is recorded with `parse_error` set (mirrors
   `experiment_002a/compile_llm.py`'s `_parse_error` field) and does not silently drop from the batch
   report.

## Relationship to `002a`'s contract

This is the same `check` shape `002a` proved compileable at n=24 — no schema drift. Two things
changed going from spike to production: (a) `plain_english_restatement`'s framing (retained record,
not review-only scratch), and (b) the new `proposed_field_entry` (needed only because a real batch
references far more fields than `001a`'s current 7-entry seed catalog covers — `002a`'s 24-row
sample was too small to force this).
