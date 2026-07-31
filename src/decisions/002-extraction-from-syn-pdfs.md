# 002 — Loan data comes from demo/syn PDFs + MISMO XML, parsed directly (incl. signatures)

**Status:** Accepted 2026-07-29 (Gordon)

## Decision
The pilot does NOT consume `p0/` fixture JSON. It extracts loan data itself from
`demo/syn/loan 0X/` — the PDFs (via `pdftotext -layout`, deterministic) and the MISMO
3.4 XML — including **signature recognition**, because several checks verify signature
presence.

## How signatures are recognized (synthetic corpus)
The synthetic PDFs render signatures as text lines (e.g. `Signatures — John A. Smith
(electronic, 09/12/2025)`, `Section III — Borrower Certification *** UNSIGNED —
signature line blank ***`, `SAR Signature  B. Whitfield`). The extractor emits
`sig_<doc>_<role>_present` booleans with citations to those lines. For real scanned
documents this becomes a CV problem (Textract SIGNATURES / Document AI) — out of scope
for the pilot; the *fact shape* (signer role, present, page, confidence) is designed to
be compatible with that future source.

## Honesty rule for the synthetic `*** ... ***` markers
The synthetic docs contain `*** ... ***` stage-direction markers. The extractor strips
them from **values** (so the machine never reads the answer key) but keeps the full raw
line as the citation **snippet** (what an auditor would see). Document-absence facts
come from (a) the loan folder inventory (no matching file) or (b) explicit "NOT IN FILE"
rows in genuine index/summary documents — never from the answer-key PDF (`00_Loan_
Summary_And_Answer_Key.pdf` is excluded from extraction entirely).

## Derived fields
A few deterministic derivations are computed at extraction time with dual citations
(e.g. `appraisal_age_days` = closing_date − appraisal_effective_date), mirroring the
p0 engine's Track A2 derivation pattern.

## Evidence
- `src/shacl_pilot/extract_loan.py` — the extractor; answer-key PDF skipped at line 237 ("answer key is NEVER parsed"); `*** ... ***` markers stripped from values but kept in citation snippets, per the docstring.
- `src/shacl_pilot/out/loan_01_extraction.json` … `loan_05_extraction.json` — extraction outputs for all five loans (fields, facts, entities, docs_present, citations).
- `demo/syn/loan 01/` … `loan 05/` — the source PDF + MISMO folders (e.g. `00_Loan_Summary_And_Answer_Key.pdf`, `01_Final_1003_URLA.pdf`).
- Signature facts (`sig_*_present`) and derived fields present in the extraction JSONs with their citing lines as snippets.
