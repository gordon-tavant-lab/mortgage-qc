# Data Model: Synthetic Loan Fixture Generation

This feature introduces no new runtime dataclasses to the engine — it produces data that conforms to
`p0/qc_engine/model.py`'s existing `CanonicalLoan`/`SourceValue`/`DocCitation` (unchanged) and extends
`p0/qc_engine/field_catalog.json`'s existing `FieldCatalogEntry` shape (unchanged, per `001a`'s
pinned schema). The entities below are this feature's own — the inputs and intermediate artifacts
that produce those existing shapes.

## SyntheticLoanPackage (input, not a new class — a folder convention)

| Field | Type | Notes |
|---|---|---|
| `loan_id` | string | The MISMO `LoanIdentifier`, e.g. `2025-0917-001` — matches `CanonicalLoan.loan_id`. |
| `loan_program` | string | e.g. "Conventional Purchase", "FHA Purchase", "VA Purchase", "Freddie Mac Cash-Out Refi", "USDA RHS 502 Guaranteed" — informs which `doc_patterns/*.yaml` apply. |
| `folder` | path | `demo/syn/loan 0{1-5}/` — the source-of-truth document set. |
| `documents` | list of files | Numbered `NN_Description.pdf`/`.xml` — the loan's closing package. |
| `mismo_path` | path | The loan's `*_Loan_Data_MISMO.xml` — the system-side (`sources.mismo`) source. |
| `known_defects` | list of 5 `KnownDefect` | Parsed from `<!-- DEFECT ... -->` XML comments — the ground-truth answer key for this loan. |

## KnownDefect (the ground-truth answer key, parsed from source XML comments)

| Field | Type | Notes |
|---|---|---|
| `loan_id` | string | Which loan this defect belongs to. |
| `defect_number` | int (1-5) | Position within the loan's 5 documented defects. |
| `description` | string | The literal `<!-- DEFECT #N: ... -->` comment text — the human-readable ground truth. |
| `field_name` | string | The primary catalog field this defect exercises. |
| `compare_field_name` | string, optional | For doc-vs-doc defects (research.md decision #4), the second field being compared. |
| `expected_relationship` | enum: `mismatch` \| `missing` \| `threshold_breach` \| `stale` | Which check-kind archetype (from `taxonomy.json`) this defect maps to. |
| `source_document` | string | Which specific PDF/XML the defect is drawn from — feeds the citation. |

Formalized as the machine-readable manifest in `contracts/defect-verification-manifest.md`.

## ExtractedFieldFixture (conforms to existing `SourceValue`, not a new type)

| `SourceValue` field | How this feature populates it |
|---|---|
| `truth` | The document-extracted value (deterministic pattern match, or LLM-fallback result). |
| `sources["mismo"]` | Populated via extended `qc_engine/mismo.py` output. |
| `sources["fhac"]` (etc.) | For genuine doc-vs-**system** fields only (e.g. FHA case number vs. the FHA Connection portal) — never for doc-vs-doc pairs (research.md decision #4). |
| `citation` | `DocCitation{doc_name, page_num, segment_snippet}` — mandatory for every `truth` value (FR-002). |
| `doc_confidence` | Honest, method-derived (research.md decision #6) — not a hardcoded default. |

## RuleGroundedCatalogEntry (conforms to existing `FieldCatalogEntry`, `001a`'s schema, unchanged)

Every new entry added to `field_catalog.json` by this feature additionally carries, **as
documentation alongside the entry** (not a new JSON schema field — `001a`'s schema is not modified),
a note of the form: *"Grounded in taxonomy.json archetype `<ARCHETYPE_ID>`, category `<category>` —
e.g. exact match to real condition: '<condition text>'"*. This satisfies SC-003 without touching
`001a`'s already-implemented, zero-regression-gated schema.

## DefectVerificationResult (the 25/25 gate's own output — new, small, this feature's)

| Field | Type | Notes |
|---|---|---|
| `loan_id` | string | |
| `defect_number` | int | |
| `expected` | (from `KnownDefect`) | |
| `actual` | (from the generated fixture) | |
| `matched` | bool | `True` only if the fixture reproduces the documented discrepancy/absence exactly. |

Aggregate result: `25/25 matched` is the only passing state (SC-001); anything less is a hard failure
(FR-006) — no partial-credit path exists.

## Relationships

```
SyntheticLoanPackage (1) ──has──> KnownDefect (5)
SyntheticLoanPackage (1) ──produces, via extract_pdf.py + extract_xml.py──> ExtractedFieldFixture (N, one per catalog field)
ExtractedFieldFixture (N) ──assembled by build_fixtures.py into──> CanonicalLoan (1, existing shape, unchanged)
KnownDefect (25 total) + CanonicalLoan (5) ──checked by verify_against_defects.py──> DefectVerificationResult (25)
```
