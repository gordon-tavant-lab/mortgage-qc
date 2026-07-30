# 003 — Citations are non-negotiable

**Status:** Accepted 2026-07-29 (Gordon) — his words: "critical and important to keep
the citations (non-negotiable)".

## Decision
Every extracted value carries a citation `{doc_name, page, snippet}`. Every SHACL shape
declares which fields it reads (`caro:citesFields`). Every violation in the audit report
is printed WITH the citations of the fields it read, so a reviewer can jump from an
exception straight to the exact document lines — same UX contract as the prod design's
`PdfViewerModal`.

## Implementation
- Extractor: citation captured at match time (doc, page number from `\f` page breaks,
  raw matched line as snippet).
- RDF: each field also gets a `li:cite_<field>` node (doc/page/snippet properties) so
  citations live in the graph, not just the JSON.
- Runner: post-processes each violation → looks up `caro:citesFields` → prints citations
  under the finding.
- Inventory-derived absence facts cite the folder inventory (doc list) — the weakest
  citation form; flagged as such in output.

## Evidence
- `src/shacl_pilot/extract_loan.py` — citations `{doc_name, page, snippet}` captured at match time (page from `\f` breaks), per its docstring.
- `src/shacl_pilot/out/loan_01.ttl` — RDF graph with 49 `li:cite_` citation nodes (doc/page/snippet live in the graph, not just the JSON sidecar).
- `src/shacl_pilot/blocks/*.ttl` — all 9 block files declare `caro:citesFields` on their shapes.
- `src/shacl_pilot/run_audit.py` — `citations_for(...)` prints "cite: ..." lines under every finding (see the finding-output loop near the end of `main`).
- `src/shacl_pilot/blocks/assets.ttl` — example: `LargeDepositShape` cites `base_monthly_income_1003`, `large_deposit_source_documented`; its `sh:message` embeds `[cite: {?cdoc} p.{?cpg}]`.
