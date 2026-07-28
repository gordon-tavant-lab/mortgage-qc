# Contract: Touchless + LOS/MISMO Inbound Interfaces

Closes `output/FOUNDATION-READINESS.md` GAP 1 for this feature's scope — these were prose in
THESIS.md/CLAUDE.md; pinned here as reviewable schemas, mapped onto `001a`'s field catalog.

## Touchless inbound contract (per extracted field)

```json
{
  "field_name": "note_rate",
  "value": "6.125",
  "document_classification": "Promissory_Note",
  "citation": {"doc_name": "Promissory_Note.pdf", "page_num": 3, "segment_snippet": "..."},
  "confidence": 0.97
}
```

Maps to `SourceEnvelope.truth` (+ `citation`, `doc_confidence`). `field_name` MUST resolve to a
`001a` `FieldCatalogEntry` — if it doesn't, this is exactly the referential-integrity failure `001a`
guards against, now surfaced at the ingest boundary.

## LOS/MISMO inbound contract (per system-side field)

```json
{
  "field_name": "note_rate",
  "value": "6.125",
  "source_name": "los | mismo"
}
```

Maps to `SourceEnvelope.sources[source_name]`. A lender providing only a MISMO 3.4/ULAD-DU export
supplies `source_name: "mismo"` for every field; `system_value()`'s priority order (`data-model.md`)
still resolves correctly with no `los` entries present at all.

## Non-goals

- Does not build the Touchless extractor or the LOS connector (Principle IV — consumed, not built).
- Does not define multi-LOS reconciliation (two or more `sources` entries compared against each
  other) — that's the demoted v3 interface (roadmap feature 013), not this contract's concern.
- Does not define a second *truth*-side source (a future settlement-agent/title feed) — tracked as
  the roadmap's "Future truth-side widening (A3)" note, out of scope here.
