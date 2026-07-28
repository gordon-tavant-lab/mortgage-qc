# Provenance — `loans/`

| File | Loan ID | Program |
|---|---|---|
| `loan_01.json` | 2025-0917-001 | Conventional Purchase |
| `loan_02.json` | 2025-1004-FHA-002 | FHA Purchase |
| `loan_03.json` | 2025-1108-VA-003 | VA Purchase |
| `loan_04.json` | 2025-1215-FRD-004 | Freddie Mac Cash-Out Refi |
| `loan_05.json` | 2025-1122-USDA-005 | USDA RHS 502 Guaranteed |

Each is a `CanonicalLoan`-shaped JSON: `loan_id`, `loan_type`, `facts` (routing metadata like
`doc_present_bank_statement`), and `fields` (every extracted data point, each with `truth`,
`doc_confidence`, `sources`, and a full audit `citation` — document name, page, section, exact
text snippet).

## Source

- **Extracted:** synthetic loan packages in `demo/syn/loan 0{1-5}/` (33 born-digital PDFs + MISMO
  3.4 XML per loan) — 25 known defects deliberately planted across the 5 loans
  (`p0/fixtures/from_docs/defect_manifest.json` is the ground-truth answer key).
- **Pipeline:** `extract_pdf.py` (`pdftotext -layout` + label-anchored regex, `doc_patterns/*.json`)
  + `extract_xml.py` (MISMO) → merged by `build_fixtures.py` → gated by
  `verify_against_defects.py` (25/25 match required before use downstream).
- **Coverage:** 377 fields in `qc_engine/field_catalog.json` as of last extraction; comprehensive
  at the field level a real QC rule would reference (not a full-text/line-item OCR dump — see
  `fixtures/from_docs/README.md`'s "Honest scope boundary" section for exactly what depth this is
  and isn't).
- **Confirmed (not assumed):** the QA/QC engine reads *only* this JSON at evaluation time —
  `fixture_loader.py::load_canonical_loan()` opens the JSON fixture and nothing else; no PDF access
  anywhere in the evaluation path. See `output/COMPREHENSIVE-RULESET-OVERNIGHT-REPORT-2026-07-23.md`
  §4 for the direct code-level confirmation.

## How to refresh

```bash
cd p0/fixtures/from_docs
python3 build_fixtures.py
python3 verify_against_defects.py   # MUST pass 25/25 before promoting
cp loan_0*.json ../../../result/loans/
```
