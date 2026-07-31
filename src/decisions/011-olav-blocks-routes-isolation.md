# 011 — Olav block taxonomy for categorization; per-program routes; full src/ isolation

**Status:** Accepted 2026-07-29 (Gordon)

## Blocks (Image #2 / docs/research/olav-demo-yaml/blocks_manifest.json)
Rules are categorized into Olav's block taxonomy by a fixed AMQ-category → block_id
mapping (validated against `blocks_manifest.json` at compile time — the compiler
refuses to run if a block id drifts):
Application→application-verification, Fannie Mae Form 1033→appraisal-form-1033,
Assets→asset-verification, Certification/Endorsement/Delivery→certification-delivery,
Closing→closing-documents-review, ATR-QM→compliance-review,
Credit-Liabilities→credit-liabilities-review, DVS→data-validation-services,
EPD→epd-review, Income→income-verification, Information Integrity→information-integrity,
Insurance→insurance-review, Loan Documents→loan-documents-review,
Product Specific→product-specific-check, Property-Appraisal→property-appraisal-review,
Underwriting→underwriting-review. ("Discarded" is excluded, counted.)

## Routes (Image #1 / olav-demo-yaml route_*.yaml)
Same DAG shape as Olav's post-closing routes — intake → fan-out to all catalog
blocks → fan-in → report — one route per program (conventional-fnm, fha, va,
freddie-refi, usda). Differences from Olav, deliberately:
- intake/route selection is a deterministic lookup from the loan's own documents
  (1003 program line + MISMO), recorded in the run output — not an LLM classification;
- block payloads are compiled rules executed by a validator — not runtime prompts;
- the program filter (decision 010) does the per-loan narrowing Olav delegates to
  the LLM reading `CRITERIA:` prose.
The FHA/VA narrative blocks (fha-compliance-check, va-eligibility-check) appear in
their routes with 0 compiled rules — porting narrative regulation into rules is
Layer-2 work.

## Isolation (Gordon: "we should not be working with previous implementation outside of src/")
The pilot imports/reads NOTHING from `p0/`. Loan 01's answer key is transcribed to
`src/shacl_pilot/answer_keys/loan_01_answers.md` (reconciliation only; the extractor
still never parses any answer-key PDF). Inputs from outside src/ are DATA ONLY:
`demo/syn/` loan documents + `demo/syn/Answers.md` (Gordon-authored ground truth) and
the read-only `docs/research/olav-demo-yaml/` reference. The AMQ CSV lives in
`src/doc/`.
