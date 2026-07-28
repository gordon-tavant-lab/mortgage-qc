# Data Model: Field Catalog

## FieldCatalogEntry

One vocabulary item — the unit of "adding a data element as an authoring act" (FR-001, FR-005).

| Field | Type | Notes |
|---|---|---|
| `field_name` | string | canonical name, e.g. `note_rate`, `loan_amount` — must be unique across the catalog (FR-009) |
| `data_type` | enum: string / decimal / date / boolean / enum | maps onto the existing Decimal-safe types already used in `p0/qc_engine/money.py` — no new type system (spec.md Assumptions) |
| `enum_values` | list[string], present only if `data_type=enum` | e.g. loan-purpose codes |
| `expected_sources` | list[string], drawn from `{doc, los, mismo}` for this feature | forward-compatible naming so `001b`'s generalization to a named `sources{}` map requires no rework (FR-010) |
| `citation_required` | bool | whether a doc-sourced value for this field must carry a `DocCitation` |
| `confidence_required` | bool | whether a doc-sourced value for this field must carry a `doc_confidence` |
| `description` | string | human-readable label, for review/audit purposes |

## FieldCatalog

The full, versioned, signed collection (FR-006).

| Field | Type | Notes |
|---|---|---|
| `catalog_id` | string | mirrors `Ruleset.ruleset_id`'s naming convention |
| `version` | int | mirrors `Ruleset.version` |
| `entries` | list[FieldCatalogEntry] | the vocabulary |
| `engine_version` | string | mirrors `Ruleset.engine_version` (pinned) |

### Canonical hashing (reuses `p0/qc_engine/ruleset.py`'s exact pattern, FR-006)

```
canonical_content() -> {catalog_id, version, engine_version, entries: [entry dicts]}
sha256() -> hashlib.sha256(json.dumps(canonical_content(), sort_keys=True, separators=(",", ":")))
```

Same function shape as `Ruleset.canonical_content()`/`Ruleset.sha256()` — not reinvented, per
`research.md` decision #1's JSON-everywhere consistency.

## FieldEnvelope (the stable, fixed shape — FR-002)

Not a new class: this **is** `p0/qc_engine/model.py`'s existing `SourceValue`, described here as the
contract every field value conforms to, per the catalog's declaration of which fields exist. FR-002
requires this shape to stay fixed even as the field set grows — it does not require inventing a new
Python type.

| Field (existing, `SourceValue`) | Maps to spec.md's envelope field |
|---|---|
| `doc` | `value` (from the document/truth side) |
| `los` / `mismo` | `source_origin` (system-side value; `001b` generalizes this to a named map) |
| `citation` | `citation` |
| `doc_confidence` | `confidence` |

## ReferentialIntegrityValidator (the SAFE-gate mechanism — FR-003, FR-004)

Not a data entity but the validation function this feature adds: given a `Ruleset` (list of
`Check`s, each with a `field_name`) and a `FieldCatalog`, confirm every `Check.field_name` resolves
to a `FieldCatalogEntry.field_name`. Runs once at load time (`research.md` decision #2), before any
loan is scored, mirroring `p0/harness.py`'s existing "validate once, before the run loop" pattern.
An unresolved reference raises immediately, naming both the offending check and the missing field —
never a silent skip (FR-004, spec.md Edge Cases).

## Unused-Entry Report (FR-008 — visibility, not a failure)

A catalog entry with zero referencing checks is reported, not rejected — the catalog may legitimately
run ahead of the checks that will consume it as `003a/b/c` land.
