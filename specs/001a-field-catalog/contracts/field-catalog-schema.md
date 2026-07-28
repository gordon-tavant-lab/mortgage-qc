# Contract: Field Catalog JSON Schema

The pinned schema for the catalog artifact — closes `output/FOUNDATION-READINESS.md` GAP 1 for this
feature's scope. Consumers: the referential-integrity validator (this feature), the engine slices
(`003a/b/c`), and eventually the authoring surfaces (`009a/b`, out of scope here but designed not to
require a schema change when they arrive).

## Format

```json
{
  "catalog_id": "string",
  "version": 1,
  "engine_version": "p0-1.0.0",
  "entries": [
    {
      "field_name": "note_rate",
      "data_type": "decimal | string | date | boolean | enum",
      "enum_values": ["only present if data_type=enum"],
      "expected_sources": ["doc", "los"],
      "citation_required": true,
      "confidence_required": true,
      "description": "The note's contractual interest rate."
    }
  ]
}
```

## Validation rules (enforced at load time, per `research.md` decision #2)

1. `field_name` MUST be unique across `entries` (FR-009).
2. `expected_sources` values MUST be drawn from `{"doc", "los", "mismo"}` for this feature — the
   generalized N-source vocabulary is `001b`'s scope; this field's *name* (`expected_sources`, a
   list) is chosen so `001b` can widen the allowed values without renaming the field or changing
   consumers' access pattern (FR-010).
3. `enum_values` MUST be present if and only if `data_type == "enum"`.
4. A malformed catalog file (unparseable JSON, duplicate `field_name`, an `enum` entry missing
   `enum_values`) MUST fail to load entirely — never partially load (FR-009, spec.md Edge Cases).
5. Every `Check.field_name` in a `Ruleset` being loaded alongside this catalog MUST resolve to an
   `entries[].field_name` — enforced by the referential-integrity validator (FR-003, FR-004), not by
   this schema alone (the schema defines the catalog's shape; the validator defines the *cross*-
   artifact contract between catalog and ruleset).

## Non-goals

- Does not define the authoring UI's input format (`009` — out of scope).
- Does not define the N-source `{truth, sources{}}` envelope (`001b` — out of scope; this schema's
  `expected_sources` field is deliberately named to not require a shape change when `001b` lands).
