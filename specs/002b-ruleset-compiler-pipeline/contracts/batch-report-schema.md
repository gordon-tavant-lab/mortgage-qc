# Contract: Batch Compile Report (the reduce-step output)

The artifact an SME reviews before signing a compiled batch — the reduce phase of research.md
Decision 1, combining FR-003 (consistency), FR-006 (sign-off-theater), FR-007/FR-008 (pattern
flags), and User Story 3's referential-integrity screen into one reviewable report per batch.

```json
{
  "batch_id": "string",
  "rows_compiled": "integer — SC-001's N",
  "referential_integrity": {
    "resolved": ["check_id", "..."],
    "signable_pending_catalog_entry": ["check_id", "..."],
    "blocked": [{"check_id": "string", "reason": "string — names the check and the missing field"}]
  },
  "consistency_report": {
    "duplicate_flags": [
      {"field_name_a": "string", "field_name_b": "string", "edit_distance": "integer",
       "check_ids": ["string", "..."]}
    ]
  },
  "pattern_flags": [
    {"check_id": "string", "flag_type": "opaque_boolean_risk | archetype_mismatch_risk",
     "reason": "string"}
  ],
  "signoff_theater_check": {
    "note": "computed AFTER sign-off via Ruleset.signoff_summary() — this report's pre-sign shape has no edit-distance data yet; listed here for completeness of the full compile-to-sign lifecycle."
  }
}
```

## Consumption rules

- `blocked` checks are **hard-blocked** from sign-off (User Story 3, non-negotiable — the only hard
  block in this feature).
- `signable_pending_catalog_entry` checks are blocked **until** their paired `proposed_field_entry`
  is itself signed (research.md Decision 2) — at that point they move to resolved for any
  *subsequent* batch, since the catalog has grown.
- `duplicate_flags` and `pattern_flags` are **advisory only** — spec.md Edge Cases is explicit these
  route to human attention and do not themselves block sign-off.
- `signoff_theater_check` is computed after sign-off, from `Ruleset.signoff_summary()` (existing,
  unmodified) — included here only to document the full lifecycle; it is not part of this report's
  pre-sign JSON in practice.

## Non-goals

- Does not define the authoring UI (`009a/b/c`) that would eventually render this report — this is a
  data contract, not a screen design.
- Does not define product/program gating (`010a/b`).
