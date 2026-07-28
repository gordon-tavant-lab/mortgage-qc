# Data Model: Source Envelope and Inbound Contracts

## SourceEnvelope (generalizes `p0/qc_engine/model.py`'s `SourceValue`)

| Field | Type | Notes |
|---|---|---|
| `truth` | Optional[Any] | always the document/closing-file side (Principle V) — replaces `SourceValue.doc` |
| `sources` | Dict[str, Any] | named system-side values, e.g. `{"los": ..., "mismo": ...}` — replaces the fixed `los`/`mismo` attributes; open to new keys without a code change (FR-004) |
| `citation` | Optional[DocCitation] | unchanged from `SourceValue` |
| `doc_confidence` | Optional[float] | unchanged from `SourceValue` |
| `source_priority` | List[str], default `["los", "mismo"]` | resolution order for `system_value()`'s generalized equivalent; overridable per field via `001a`'s catalog metadata (research.md decision #1) |

### `system_value()` generalization

```
def system_value(self) -> Optional[Any]:
    for name in self.source_priority:
        if name in self.sources and self.sources[name] is not None:
            return self.sources[name]
    return None
```

Preserves today's exact `los`-else-`mismo` behavior when `source_priority = ["los", "mismo"]`
(the default) — SC-001, SC-005.

## TouchlessInboundContract (consumed interface — documentation, not a build)

| Field | Maps to |
|---|---|
| extracted field value | `SourceEnvelope.truth` |
| document classification | metadata alongside the extraction batch, not per-field |
| per-field citation | `SourceEnvelope.citation` |
| per-field confidence | `SourceEnvelope.doc_confidence` |

Each extracted field maps onto a `001a` `FieldCatalogEntry` by `field_name`.

## LosMismoInboundContract (consumed interface — documentation, not a build)

| Field | Maps to |
|---|---|
| native LOS export field | `SourceEnvelope.sources["los"]` |
| MISMO 3.4 / ULAD-DU XML field | `SourceEnvelope.sources["mismo"]` (same-data fallback, per `system_value()`'s priority order) |

Both populate the *same* named-source key space — a lender with only a MISMO export still resolves
through the identical `system_value()` logic (spec.md User Story 1, Acceptance Scenario 3).

## SourceIndependenceTestHelper (test-construction discipline, research.md decision #2)

Not a runtime entity — a reusable test-fixture assertion (extends the discipline already present in
`p0/eval_synth/generator.py`, which builds `doc` and `los`/`mismo` from separate random draws).
Signature (illustrative, for planning purposes):

```
assert_independently_constructed(truth_value, sources_dict, construction_trace) -> None
```

Raises if a test fixture derives a `sources` entry directly from `truth` (e.g. `sources["los"] =
truth` or a transform of it) rather than an independently-generated value — catching the exact
CLAUDE.md #3 trap (LOS-only test data making doc-vs-system comparisons trivially identical) at
fixture-construction time, not as a runtime check on production data (which doesn't have this risk —
see research.md decision #2 for why).
