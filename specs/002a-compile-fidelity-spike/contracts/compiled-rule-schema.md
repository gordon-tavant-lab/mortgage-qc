# Contract: Compiled Rule Draft (LLM → structured output)

The LLM's config-time output, one per `SampledWorkbookRow`, must conform to a superset of the
existing `Check` schema in `p0/qc_engine/ruleset.py` (reused verbatim — no new schema invented,
per `research.md` decision #2), plus one field the spike adds for the SME review artifact.

## Required output (per sampled row)

```json
{
  "row_id": "string — links back to the source workbook row",
  "check": {
    "id": "string",
    "name": "string",
    "field_name": "string — the field this check reads",
    "kind": "predicate | ratio_threshold | agree_categorical | agree_numeric",
    "severity": "CRITICAL | WARNING | INFO",
    "phase": "RECONCILE | QC",
    "sources": ["doc", "los"],
    "normalizer": "identity | ... (only for agree_categorical)",
    "tolerance": "0 (Decimal string, only for agree_numeric)",
    "predicate": "string (only for kind=predicate)",
    "ratio": "ltv | dti (only for kind=ratio_threshold)",
    "threshold": "Decimal string percent (only for kind=ratio_threshold)",
    "operator": "<= | < | >= | > | == (only for kind=ratio_threshold)",
    "message_pass": "string",
    "message_fail": "string"
  },
  "plain_english_restatement": "string — a human-readable restatement of what this check does, used ONLY by the SME reviewer to judge intent; never used by the engine"
}
```

## Validation (before scoring)

1. `check.kind` MUST be one of the four values the engine already recognizes (`p0/qc_engine/ruleset.py`).
2. `check.field_name` MUST be non-empty (full referential-integrity validation against the field
   catalog is 001a's concern, not yet implemented as a runtime gate — this spike checks presence
   only, and notes any drafted field name that doesn't map to a real loan concept for the SME's
   awareness during review).
3. A row whose LLM output fails to parse into this schema at all is recorded as `runnable: false`
   and scored as a runnability failure (FR-003) — it does not silently drop out of the sample.

## Non-goals

- This contract does **not** define the production compiler's output format (`002b`'s concern).
  It defines only what this spike's throwaway compile step must produce to be scoreable.
- No runtime consumption of this schema — every instance produced by this spike is either scored
  by `p0/eval_synth` at config time or discarded when the spike concludes (FR-008, FR-009).
