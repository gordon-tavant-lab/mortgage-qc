# `fixtures/from_docs/` — synthetic-loan fixture generation (dev/test only)

This subpackage turns the 5 synthetic loan packages in `demo/syn/loan 0{1-5}/` into
`CanonicalLoan`-shaped JSON fixtures for engine and eval testing. It exists at the same
architectural layer as `p0/eval_synth/` and `p0/fixtures/golden.py` — a dev/test data
generator, not a production system.

## What this is not

- **Not the Touchless production extractor.** Touchless is the upstream contract that will
  eventually deliver extracted fields + document classification for real, closed loan files
  (see the project `CLAUDE.md`, Principle IV — "build the core, assume the periphery"). This
  code is throwaway dev/test tooling operating over 5 already-available synthetic loans; it
  makes no claim to be, replace, or preempt that contract.
- **Not a claim of accuracy on real, non-synthetic lender documents.** All 33 source PDFs are
  confirmed born-digital synthetic text (verified via direct `pdftotext -layout` read, zero OCR
  noise) — strictly easier than real, sometimes-scanned lender PDFs. Nothing here says anything
  about extraction accuracy on real documents.
- **Not an implementation of the doc-vs-doc reconcile check-kind.** Several known defects are
  document-vs-document mismatches (e.g. the 1003's employment start date vs. the VOE's). This
  code produces the two independently-cited catalog fields for each such pair; the actual
  comparison logic is deferred to whoever specifies `003c-engine-reconcile-checks`.

## Document coverage (verified 2026-07-16)

All 33 PDFs across the 5 loans are matched by a `doc_patterns/*.json` file **except**
`00_Loan_Summary_And_Answer_Key.pdf` (loan 01) — correctly excluded; it's the synthetic-generator's
own answer key, not a real loan document, and extracting "ground truth" from the ground-truth file
would be circular. That's **32/32 real loan documents covered**, confirmed by a direct filename-match
sweep (`_match_doc_type` against every PDF in `demo/syn/loan 0{1-5}/`), not assumed.

Two real documents were found completely unextracted during a later coverage audit — `03_Paystub_
Most_Recent.pdf` and `05_Initial_Disclosure_Package_Index.pdf` (both loan 01) — and fixed
(`paystub.json`, `disclosure_package_index.json`). The paystub gap mattered beyond simple coverage:
checked directly against the real AMQ workbook (`demo/rules/PF and PC Sept 2025 AMQs - Retail.xlsx`)
and found **43 distinct real conditions reference paystub content** (income verification, YTD
earnings corroboration, employment-date cross-checks, deduction reconciliation) — this wasn't a
document we could afford to skip.

**Honest scope boundary, not a gap**: coverage is at the *field* level (structured data points a
reviewer or a rule would check), not full-text/line-item extraction. A bank statement's aggregate
balances and flagged large deposit are extracted; its full transaction ledger is not. A credit
report's representative scores and the one undisclosed liability are extracted; the full trade-line
table is not. This matches `examples/mortgage-qc`'s own chosen depth (its `bank_statement.yaml` has
one aggregated `large_deposits: array` field, not per-transaction extraction either) — comprehensive
at the field level a QC rule would actually reference, not an OCR dump of every line on the page.

## Citation metadata (added 2026-07-15)

`page_num` alone is nearly useless in this dataset — every source PDF is a single page, so "page 1"
tells a reviewer nothing about *where* on that page. Every doc-sourced citation now also carries:

- **`document_title`** — the source document's own displayed title (e.g. *"Uniform Residential Loan
  Application (Form 1003 / Fannie Mae Form 65)"*), the first non-empty line of the PDF.
- **`section`** — the nearest preceding section/sub-section header on the same page (e.g. *"Section
  1b — Current Employment (Borrower)"*), or `null` when no true sub-section exists above the value
  (never a redundant echo of `document_title` itself).
- **`field_label`** — the literal label text matched (e.g. *"Employment Start Date"*), stripped of
  any dangling punctuation a regex left outside its capture group (e.g. a `$` for currency fields).

`p0/qc_engine/model.py`'s `DocCitation` gained these three fields as **additive, optional** —
`to_dict()` only emits them when populated, so `p0/fixtures/golden.py`'s hand-authored citations
(which never set them) serialize byte-identically to before. This preserves `harness.py`'s bit-exact
digest (`8510a0a8b4b6996e047fc8534e094394ba72aae396305b0d2ecad3d6924634db`, unchanged since `001a`) —
that digest only ever runs `golden_loans()`, never these fixtures, so widening `DocCitation` for one
consumer without forcing every existing caller's serialized shape to change was the deliberate design
choice, not an accident.

`section` detection is a corpus-specific heuristic, not a general PDF-structure parser: these
synthetic documents consistently lay out data as `Label<2+ spaces>Value` (pdftotext -layout preserves
the source column spacing), while section headers never have that multi-space split — a non-empty
line with no run of 2+ spaces is treated as a header. This works well here; it is not a claim that
this heuristic generalizes to arbitrary real lender PDFs (same scope boundary as everything else in
this dev-tooling — see "What this is not," above).

## Pipeline

```
extract_xml.py   -> sources.mismo side, via extended qc_engine/mismo.py
extract_pdf.py   -> truth side + DocCitation, via pdftotext -layout + doc_patterns/*.json
build_fixtures.py -> merges both into 5 CanonicalLoan JSON fixtures (p0/fixtures/from_docs/loan_0N.json)
fixture_loader.py -> loads a fixture JSON back into the real CanonicalLoan/SourceValue/DocCitation
                      classes, with zero changes to qc_engine/model.py
verify_against_defects.py -> the 25/25 hard gate; a fixture set failing this MUST NOT be
                              wired into any downstream engine or eval test run
```

Run `python3 p0/fixtures/from_docs/build_fixtures.py` then
`python3 p0/fixtures/from_docs/verify_against_defects.py` from the repo root — see
`specs/000-synthetic-fixture-generation/quickstart.md` for the full sequence (note: quickstart.md
describes the intended flow; `doc_patterns/*.json` below is the as-built format — see Implementation
Notes in `../../../specs/000-synthetic-fixture-generation/plan.md` for why `.json` replaced the
originally-planned `.yaml`).

`doc_patterns/` holds 15 files (was 13 when written; T032 later added `paystub.json` + `disclosure_package_index.json` — corrected 2026-07-26, spec audit), not the originally-estimated 9 — `fha_docs.json`/`va_docs.json`/
`usda_docs.json` bundle every program-specific document as planned, plus 4 more for document types
the original plan didn't enumerate: `bank_statement.json`, `payoff_statement.json`,
`mortgage_payment_history.json` (the one aggregation-style field —
`mortgage_late_payment_count_12mo` counts 30+-day-late rows rather than a single label/value match,
handled as a small special case in `extract_pdf.py`, not a plain regex capture), and
`self_employed_income_index.json`.

## Catalog grounding

Every one of the 32 new fields added to `p0/qc_engine/field_catalog.json` is grounded in a specific
`p0/eval_synth/taxonomy.json` archetype — not merely in appearing in one of these 5 loans
(`specs/000-synthetic-fixture-generation/research.md` decision #3). Full grounding text lives in
each entry's `description`; the archetype-only summary:

| Field | Archetype | Field | Archetype |
|---|---|---|---|
| `employment_start_date_1003` | MISMATCH | `loan_purpose_1003` | MISMATCH |
| `employment_start_date_voe` | MISMATCH | `loan_purpose_cd` | MISMATCH |
| `title_vesting_1003` | MISMATCH | `cd_payoff_amount` | MISMATCH |
| `title_vesting_commitment` | MISMATCH | `payoff_statement_amount` | MISMATCH |
| `large_deposit_source_documented` | MISSING | `mortgage_late_payment_count_12mo` | THRESHOLD |
| `liability_disclosed_on_1003` | MISMATCH | `appraisal_effective_date` | THRESHOLD |
| `liability_amount_credit_report` | MISMATCH | `self_employed_pl_balance_sheet_present` | MISSING |
| `appraisal_comp_distance_miles` | THRESHOLD | `household_income_usda` | THRESHOLD |
| `hud92900a_certification_signed` | UNSIGNED | `usda_property_eligibility_documented` | MISSING |
| `fha_case_number_1003` | MISMATCH | `piti_ratio` | THRESHOLD |
| `gift_funds_source_documented` | MISSING | `dti_ratio` | THRESHOLD |
| `lead_paint_completion_cert_present` | MISSING | `well_septic_test_documented` | MISSING |
| `fha_amendatory_clause_present` | MISSING | `site_value_justification_documented` | MISSING |
| `notice_of_value_date` | EXPIRED | `arm_preloan_disclosure_present` | MISSING |
| `closing_date` | EXPIRED | `termite_inspection_present` | MISSING |
| | | `lead_paint_disclosure_present` | MISSING |
| | | `va_residual_income_documented` | MISSING |

Two fields (`title_vesting_1003`/`title_vesting_commitment`, `liability_disclosed_on_1003`) cite an
**exact-text match** to a real AMQ condition; the rest cite the correct archetype + category by close
conceptual match. None were added merely because they happen to appear in one of these 5 loans
(SC-003) — see `test_every_new_catalog_field_has_taxonomy_grounding_citation` in
`p0/tests/test_fixture_generation.py` for the machine-checked version of this table.

`fha_case_number_1003` is the one genuine doc-vs-system field (research.md decision #4): its system
side (the FHA Connection portal's case number) is carried under the field's existing `sources["mismo"]`
slot, extracted by `qc_engine/mismo.py` — **not** a new source-name in `expected_sources` (widening
`qc_engine/catalog.py`'s pinned `VALID_SOURCES` would be a change to an already-implemented,
zero-regression-gated validator, out of this feature's scope per FR-009).

## Comprehensive-coverage fields (added 2026-07-15, a second and distinct grounding category)

The 32 fields above exist to prove the 25 known defects. They deliberately don't cover the *rest* of
what these loan files actually contain — Gordon asked for that too: "the fields + the extracted data
from the loan files, the actual data," pointed at `examples/mortgage-qc/schemas/extraction/*.yaml` as
the model for what comprehensive per-document-type extraction looks like (e.g. its `urla_1003.yaml`
alone declares 18 fields — co-borrower, DOB, occupancy, employer, income, assets, liabilities,
declarations — against the 4 defect-narrow 1003 fields this feature had).

56 additional fields were added across all applicable document types actually present in the 5 loans
(URLA 1003, Appraisal, Closing Disclosure, Credit Report, Bank Statement, Title Commitment, VOE,
Payoff Statement, plus the FHA/VA/USDA-specific documents that have no equivalent schema in
`examples/mortgage-qc` at all — those were designed directly from the source PDFs). Their
`field_catalog.json` `description` self-identifies this distinct grounding: *"Comprehensive-coverage
field, modeled on examples/mortgage-qc's extraction schema breadth (schemas/extraction/*.yaml) — not
tied to a specific taxonomy.json defect archetype..."* — never a fabricated taxonomy citation
(`test_comprehensive_coverage_fields_do_not_masquerade_as_rule_grounded` enforces this directly).

**Round 2 (2026-07-16)**: a density review found this initial pass had been uneven — loan 01's
documents (which happen to be the richest, most document-diverse loan) got comprehensive treatment,
but loans 02-05's *program-specific* documents (Gift Letter, CAIVRS, VA COE/NOV, USDA GUS/Property
Eligibility, Payoff Statement, Self-Employed Income Index, FHA Connection) still only carried their
original 1-2 defect-narrow fields, leaving real, substantive document content unextracted. Added 48
more fields (159 total) closing that gap — donor identity for gift letters, CAIVRS screening codes,
VA entitlement/service details, USDA GUS recommendation/income detail, and several
closing-disclosure/title-commitment/payoff-statement fields not yet captured per loan. Field density
for the previously-sparse loans: loan 02 31→46, loan 03 28→41, loan 04 29→36, loan 05 21→28.

**Round 3 (2026-07-16) — bulk line-item data**: the previous two rounds stayed at aggregate/summary
level by design (this file's own stated boundary, below) — on explicit instruction, this round
crosses it for the bank statement's transaction ledger, the credit report's trade lines, and the
appraisal's comparable-sales grid. `001a`'s field-catalog schema has no array `data_type`, so each
repeating row is represented as its own indexed scalar fields (`bank_txn_03_debit_amount`,
`credit_tradeline_02_balance`, `appraisal_comp_02_distance_miles`) rather than one JSON-blob field —
keeping every row individually cited to its own table line, not collapsed into an aggregate.

The bank ledger's Credit/Debit columns needed a genuinely new extraction primitive: they're mutually
exclusive per row, and no regex alone can tell which column a lone captured amount belongs to — only
its character position relative to the header's own column offsets can (confirmed directly against
the PDF text: `Credit` at column 79, `Debit` at column 92, every amount aligns to one or the other
exactly). `extract_pdf.py`'s `_extract_bank_ledger()` reads that position; `_extract_simple_table()`
handles the two unambiguous tables (trade lines, comps) via one regex match per row.

The strongest correctness proof here isn't spot-checking — it's an arithmetic identity the
extraction never targets directly: `beginning_balance + sum(credits) - sum(debits) = ending_balance`,
to the penny, across all 16 transactions. 261 catalog fields total now (up from 159).

**Round 4 (2026-07-16) — checking loans 02-05 for the same untapped bulk data.** A systematic
per-document review (not an assumption that loan 01 was the only rich one) found 5 more repeating-row
tables: loan 01's own 1003 has an Assets table (Checking/Savings/401(k)) and a Liabilities table
(Chase Sapphire/Capital One Auto/Federal Direct Loans — deliberately *not* including the undisclosed
Ally Bank line, per defect #4) that round 3 missed entirely; loan 02's FHA appraisal has a 3-row
MPR/Health & Safety Items table; loan 04's Mortgage Payment History gained all 12 months (previously
only an aggregate late-payment count); loan 04's Self-Employed Income Documentation Index gained its
8-row present-document checklist.

Caught a real bug while verifying, before it shipped: `_extract_simple_table`'s row counter reset to
0 every page. Loan 01's 1003 Assets table straddles a page break (pdftotext splits right after
"Checking"; "Savings"/"401(k)" open page 2), so the counter collided row indices and silently
overwrote "Checking" with "Savings" under the identical field name — the first build produced only 2
of 3 asset rows. Fixed by persisting the counter across pages (and proactively in
`_extract_bank_ledger` too, which hasn't hit this yet only because its one bank statement is
single-page). 108 more catalog fields (369 total). Independent sanity check: the 1003's own 3
liabilities sum to exactly $684.00/mo (85+389+210) by hand arithmetic, not just by trusting the regex.

**Round 5 (2026-07-16) — the credit report's inquiry history.** The last remaining known table: 2
rows (Date/Bureau/Requesting Party) — the borrower's own mortgage-application inquiry, and the Ally
Bank auto inquiry that is itself the undisclosed liability's paper trail (defect #4 — this inquiry is
*why* the auto loan appears on the credit report at all). 6 more catalog fields (375 total). Every
other document across all 5 loans was checked and confirmed to be single-record — this appears to be
the last table in this dataset.

**Round 6 (2026-07-16) — wiring extracted fields into real engine checks.** Everything above grew the
*catalog*; this round is the first to grow the *ruleset* — connecting 20 of the 25 known defects to
actual `Check` objects that produce real `PASS`/`FAIL`/`FLAG` verdicts when run through `qc_engine.run()`,
using only check-kinds the engine already implements (no engine code changed):
- 13 presence/absence defects → `predicate`, `is_true`.
- 4 single-field threshold defects → `ratio_threshold`, mode `field_value` (5 `Check` objects, since
  one manifest entry — the USDA PITI/DTI defect — names two independently checkable ratio fields).
- 2 date-order/date-age defects → also `field_value`, against two new fields `build_fixtures.py` now
  derives (`appraisal_staleness_days`, `nov_days_after_closing`) from already-resolved doc-truth date
  pairs — no citation attached (computed from 2 documents, not read from 1), excluded by name from the
  citation-completeness tests via a new `DERIVED_FIELD_NAMES` constant.
- 1 doc-vs-system mismatch (`fha_case_number_1003` vs its own `sources["mismo"]`) → the *existing*
  `agree_categorical` reconcile check-kind, verbatim — its verdict is `FLAG`, not `FAIL`: the engine's
  own RECONCILE-phase design treats doc-vs-system disagreement as informational (the closing doc is
  truth regardless of system sync), a correct pre-existing behavior this check surfaces for the first
  time, not a gap.

The remaining 5 known defects (`employment_start_date_1003`/`_voe`, `title_vesting_1003`/
`_commitment`, `liability_disclosed_on_1003`/`liability_amount_credit_report`, `loan_purpose_1003`/
`_cd`, `cd_payoff_amount`/`payoff_statement_amount`) are genuine doc-vs-doc comparisons — two
independently-extracted document fields, neither a system source — with no check-kind built yet.
Deliberately not wired: spec 000's own research.md decision #4 defers this to whoever specifies 003c
or a new doc-vs-doc kind.

These checks live in `p0/fixtures/ruleset_defects.py`, deliberately separate from
`p0/fixtures/ruleset_demo.py` — that ruleset's exact content is pinned in `p0/harness.py`'s 1000-run
zero-regression digest and must never be touched by unrelated work. Verified (not assumed) that none
of the new checks false-positive across the other 4 loans: every check resolves `NOT_APPLICABLE` on a
loan/program it doesn't apply to, except `appraisal_staleness_days` on loan 01, which genuinely has
both source dates (a real 25-day gap, correctly `PASS` — well under the 120-day limit that loan 04's
207-day gap breaches). 377 catalog fields total now (up from 375); full suite 103 passed (was 100);
determinism digest unchanged.

**Round 7 (2026-07-16) — gating the 13 predicate checks by applicability.** Round 6's wiring exposed a
real product-quality gap: the 13 "missing document" predicate checks ran unconditionally against all 5
loans, so e.g. loan 01 (Conventional) showed `FAIL` on "HUD-92900-A signed," "USDA property eligibility
documented," etc. — checks for programs it isn't. `predicate`'s `is_true` correctly treats an absent
value as `FAIL` for the loan the check actually applies to (that's the whole point of the MISSING
archetype); the bug was applying every check to every loan regardless of relevance.

The 13 checks aren't homogeneous, so 3 different gates were needed:
- **7 document-presence gated** (self-employment P&L, gift-funds paper trail, large-deposit source,
  HUD-92900A cert, termite inspection, well/septic test, USDA property eligibility) — these are
  borrower/transaction conditions, not program-tied (a self-employed VA borrower needs the same P&L
  check a self-employed Freddie-refi borrower does), so gating by `loan_type` would be wrong. A new
  `_derive_document_presence_facts()` in `build_fixtures.py` checks the loan folder's own filenames
  (e.g. does a `Bank_Statement`/`HUD_92900A`/`Gift_Letter` PDF exist) and stores 7 booleans in
  `facts{}` — not `fields{}`, since these are pure routing metadata, never themselves a Check target,
  so no catalog entry or citation applies.
- **2 property-age gated** (both lead-paint checks) — gated by the already-existing
  `year_built_appraisal` field (< 1978), with a deliberately conservative default when that value is
  unknown: gate the check IN, not out. Absence of contrary evidence should never silently clear a
  compliance check. Honest residual, not a bug: loans 02/04/05 have no year data at all, so both
  lead-paint checks fire for all three (loan 02's own labeled defect is only one of the two) —
  documented and tested explicitly rather than hidden.
- **4 program gated** (FHA Amendatory Clause, ARM Pre-Loan Disclosure, VA residual income, USDA site
  value justification) — no PDF exists anywhere in any of the 5 loans for these (MISMO's
  `InFileIndicator=false` is the only record per `defect_manifest.json`'s own notes), so
  document-presence gating can't work; these fall back to `loan_type` string match instead.

New `defects_ruleset_for(loan) -> Ruleset` in `ruleset_defects.py` is the real evaluation entrypoint —
filters the 21-check universe down to what applies to a specific loan before calling
`qc_engine.run()`. Zero `engine.py`/`model.py` changes: this is pure ruleset-assembly logic, each loan
effectively getting its own Route, matching this product's own "point a route at a target set of
checks" philosophy rather than inventing new engine machinery. Verified empirically: loan 01 now shows
exactly 1 of the 13 predicate checks (its own large-deposit defect) instead of all 13 firing
unconditionally. Full suite 104 passed (was 103); determinism digest unchanged.

Some fields deliberately resolve to `null`/absent for a subset of the 5 loans — e.g.
`employer_name_1003`'s regex matches the label `"Employer"`, which loan 05's USDA-program document
instead labels `"Borrower Employer"`. This is honest behavior, not a bug: the 5 loans use slightly
different label phrasing per program, and a field either matches its document's actual label or it
doesn't — nothing is fabricated to fill a gap. `document_type` coverage is still bounded by what's
physically present in these 5 loans (no W-2, no promissory note, no insurance policy, no verbal VOE —
none of these document types exist in `demo/syn/`), consistent with this feature's stated scope
(spec.md Assumptions: the 5 synthetic loans are the entire input population).
