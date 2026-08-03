# Data Model: Real-Engine Audit Run

## Entities

### Compiled Audit Ruleset (new — Python, `p0/qc_engine/ruleset.py`'s `Ruleset`)

A `Ruleset` (existing dataclass, unchanged shape) whose `checks: List[Check]` is populated by a
new compiler reading the same source `frontend/scripts/build_gold_catalog.py` already reads
(`storage/rules/gold/data/{rules_compiled.json,rules_atomic.json}`), filtered to the subset whose
evidence field has a confident document-type mapping (research.md Item 2).

| Field (on `Check`) | Source | Notes |
|---|---|---|
| `id` | gold rule/atomic-rule id, slugified (reuse `build_gold_catalog.py`'s `slugify()`) | same id scheme as `goldCatalog.json`, so a check can be cross-referenced between the authoring UI and this ruleset |
| `name` | `finding.exception_code` | |
| `field_name` | canonical field id from the document-type mapping table (research.md Item 2), NOT the raw gold `fieldId` if the mapping renames it | must match a key the adapter actually populates |
| `kind` | `predicate` (only kind in the resolvable subset — all confidently-mapped checks are `doc_presence`) | |
| `severity` | mapped via the same `SEVERITY_MAP` as `build_gold_catalog.py` (`Critical`→`CRITICAL`, `Major`→`WARNING`, `Minor`/`Note`→`INFO`) | drives the severity-tiered loan status (research.md Item 1) |
| `predicate` | `"is_present"` | matches `engine.py`'s existing dispatch |
| `phase` | left blank (engine infers `QC` for `predicate` kind) | |
| `sources` | `[]` (unused — `predicate` kind reads `truth` only) | |

**Validation rule**: every `Check.field_name` MUST have a corresponding entry in the document-type
mapping table (Item 2) at compile time — the compiler asserts this and excludes (does not error
on) any check whose field isn't in the confidently-resolvable set, per the Safety Gate.

### Document-Type Mapping Table (new — Python, small hand-authored lookup)

`{canonical_field_id: str -> touchless_document_type: str}`, e.g.:

```python
{
    "bank_statement": "Bank Statement",
    "paystub": "Paystub",
    "W2": "W2",
    "gift_letter": "Gift Letter",
    "schedule_k1": "Schedule K-1 - Form 1065",
    "tax_return": "Form 1040",
    "sales_contract": "Purchase Agreement",
    # URLA_1003_final maps to a SET of document types (combined presence check)
    "URLA_1003_final": [
        "URLA - Borrower Information", "URLA - Lender Loan Information",
        "URLA - Continuation Sheet", "URLA - Unmarried Addendum",
    ],
}
```

Hand-authored, not derived — a ~10-entry table is simpler and more auditable than a fuzzy matcher
for this scope (research.md Item 2's rejected alternative).

### Evaluated Loan (Touchless → `CanonicalLoan`, new adapter — Python)

`CanonicalLoan.fields[canonical_field_id] = SourceValue(truth=<presence indicator>)` built from the
pulled `loan_application.json`'s `documents[]` array. `doc_confidence` is deliberately never set
(stays `None`, its default) — confidence scoring is out of scope for this feature entirely
(research.md Item 3); the engine is deterministic and this feature does not layer a probabilistic
signal on top of it. Because `doc_confidence` is always `None`, `engine.py`'s existing confidence
gate (which only fires `if ... sv.doc_confidence is not None ...`) structurally never triggers —
unmodified engine code, simply never exercised by this feature's data.

1. For each mapping-table entry, check whether any document in `documents[]` has a matching
   `documentType` (or, for `URLA_1003_final`, whether *any* of its mapped types is present).
2. If present: `truth = True`.
3. If absent from `documents[]`: `truth = None` (predicate `is_present` correctly evaluates to
   `FAIL` — a real, honest "this document is missing" finding, not a mapping artifact).

Citation: `DocCitation(doc_name=<matched documentType>, page_num=0, segment_snippet="Touchless
documents[] presence check", document_ids=[<real documentId>, ...])` — page-level citation isn't
available (per spec021 FR-011's honest disclosure), but the real `documentId`(s) of every matched
document ARE available and populated (FR-013, research.md Item 8) so the citation is genuinely
clickable, not just a text label. For single-document checks this list has exactly one entry; for
`URLA_1003_final` (mapped to 4 possible document types) it can have up to 4 — all present entries,
never truncated to the first match.

### `DocCitation` (revised — `p0/qc_engine/model.py`, one small additive field)

```python
document_ids: Optional[List[str]] = None  # NEW — real Touchless documentId(s) this citation
                                            # resolves to, when known. Plural because a single
                                            # check's evidence can span more than one real
                                            # document (research.md Item 8).
```

`to_dict()` emits `documentIds` only when populated, following the exact convention already used
for `document_title`/`section`/`field_label`. This is the one narrow, precedented exception to
"the engine's data model stays unmodified" — additive metadata, no change to any evaluation
dispatch in `engine.py`.

### Audit Verdict (new — the derived, severity-tiered outcome)

```python
{
    "run_result": RunResult.to_dict(),  # existing engine.py shape, unmodified
    "loan_status": "PASS" | "FAILED" | "NEEDS_REVIEW",  # research.md Item 1's mapping
    "compiled_check_count": int,   # size of the filtered ruleset actually run
    "excluded_check_count": int,   # 208 minus compiled_check_count, for honest reporting
}
```

`ERROR` is not produced by this function — it's assigned by the calling layer (the new backend
route) when the Python process itself fails to complete (non-zero exit, malformed stdout, or a
timeout) rather than by any successful engine run.

### Loan Status (revised — frontend `frontend/src/lib/types.ts`)

```typescript
export type LoanStatus = "PASS" | "FAILED" | "NEEDS_REVIEW" | "RESOLVED";
// RUNNING and ERROR are NOT added to this persisted union (per FR-006/FR-006a) --
// modeled as separate, transient/display-only state (see below), never stored
// alongside a loan's persisted status.
```

A loan's *display* state is derived, not a single stored field:

```typescript
type LoanDisplayState =
  | { kind: "idle"; status: LoanStatus }        // no run in flight
  | { kind: "running" }                          // transient, FR-004
  | { kind: "error"; message: string };          // transient, FR-006a -- never in queue grid
```

### Loan Queue (revised — `frontend/src/data/mockData.ts`)

20 `Loan` entries total. 19 cosmetic (realistic borrower/property/loan-type text, `status: "PASS"`,
no `applicationId`); 1 real (existing `applicationId: "0eb57730-..."`, participates in the full
lifecycle above).

### FHA / VA / USDA Routes (revised — `frontend/scripts/build_gold_catalog.py`)

Replaces the single `government` route with three: `fha`, `va`, `usda`, each with the same 16
blocks (id-prefixed `fha-`/`va-`/`usda-`, following the existing `conv-`/`gov-` convention) and a
**simulated** non-zero `checkIds` count per block — generated, not gold-sourced, per FR-009's
explicit, documented exception. A reasonable generation approach (decided at implementation time,
not load-bearing here): scale each block's simulated count proportionally to Conventional's real
per-block count, so the relative "which blocks have more coverage" shape looks plausible rather
than uniform/arbitrary.

## State Transitions (Loan Status)

```
(not fetched) --[fetch resolves]--> RUNNING --[engine completes, 0 qc_failures/needs_review]--> PASS
                                            --[engine completes, >=1 CRITICAL qc_failure]--> FAILED
                                            --[engine completes, qc_failure/needs_review, no CRITICAL]--> NEEDS_REVIEW
                                            --[process fails/times out/malformed output]--> ERROR (not shown in queue grid)
NEEDS_REVIEW --[human clears every flagged finding via existing mitigation flow]--> RESOLVED
(any state) --[Restore to Gold clicked]--> (not fetched)
```
