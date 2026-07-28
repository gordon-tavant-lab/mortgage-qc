# Quickstart: Synthetic Loan Fixture Generation

## Generating the fixtures

1. `python3 p0/fixtures/from_docs/extract_xml.py` — parses all 5 MISMO exports via the extended
   `qc_engine/mismo.py`, producing the `sources.mismo` side for every in-scope field.
2. `python3 p0/fixtures/from_docs/extract_pdf.py` — runs `pdftotext -layout` plus the per-document-type
   patterns in `doc_patterns/*.yaml` against all 33 PDFs, producing the `truth` side with citations.
3. `python3 p0/fixtures/from_docs/build_fixtures.py` — merges both sides into 5 `CanonicalLoan` JSON
   fixtures, contract-shaped per `001a`/`001b` (`specs/001b-.../contracts/inbound-contracts.md`).
4. `python3 p0/fixtures/from_docs/verify_against_defects.py` — the hard gate. Expected output:
   `25/25 known defects reproduced exactly`. Anything less blocks step 5.
5. Only after step 4 passes 25/25: wire the fixtures into `p0/eval_synth`/engine tests alongside
   (not replacing) the existing hand-authored golden set (`p0/fixtures/golden.py`).

## Extending the field catalog first (do this before step 2)

- Add each new field to `p0/qc_engine/field_catalog.json`, following `001a`'s existing schema
  (`specs/001a-field-catalog/contracts/field-catalog-schema.md`) exactly — no schema change.
- Alongside each new entry, document which `taxonomy.json` archetype/condition justifies it
  (research.md decision #3) — a field added only because it's convenient for these 5 loans should be
  rejected in review, not merged.
- Re-run `001a`'s existing referential-integrity and zero-regression tests before proceeding — this
  feature does not get a governance shortcut on a shared, governed artifact (FR-009).

## Verifying a fixture is trustworthy

- Run `verify_against_defects.py` and read the per-defect breakdown, not just the aggregate — a
  `24/25` result names exactly which loan/field failed and why.
- Do not wire a fixture set into any downstream test if verification reports anything less than
  25/25 (FR-006) — this is a hard stop, not a warning to note and proceed past.

## Adding a 6th loan later

1. Drop the new loan's folder into `demo/syn/loan 06/` following the existing numbering convention.
2. Add its `<!-- DEFECT ... -->` comments to `contracts/defect-verification-manifest.md`'s manifest
   (or the machine-readable file it's sourced from) — the ground truth must exist *before* extraction
   is trusted, not be reverse-engineered from what the extractor happens to produce.
3. Re-run steps 1-4 above; the aggregate gate becomes `30/30`, not `25/25`.

## What this deliberately does not do

- Does not build, replace, or preempt the Touchless production extractor (Principle IV) — see
  `p0/fixtures/from_docs/README.md` for the explicit dev-only label.
- Does not implement the doc-vs-doc comparison check-kind itself (research.md decision #4) — only
  produces the two independently-cited fields; `003c` (not yet specified) owns the comparison logic.
- Does not claim accuracy against real, non-synthetic lender documents (spec.md footer note).
