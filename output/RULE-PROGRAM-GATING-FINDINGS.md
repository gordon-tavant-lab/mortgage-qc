# Rule-to-Program Gating — Findings from the Real AMQ Workbooks

**Date**: 2026-07-20 (revised same day — see "Revision history" at the bottom)
**Trigger**: Gordon's question — "not all rules will be applicable to the loans, since some rules
are set to test different types of loans (FHA, Jumbo, etc.) — can we check if this is true?" —
followed by a direct request to fully audit `demo/rules/*.xlsx` (every column, every sheet) and
research the mortgage post-closing QC domain before building anything further.
**Method**: Direct inspection of `demo/rules/*.xlsx` via `openpyxl`, cross-checked against cited
external research (Fannie Mae Selling Guide, HUD Handbook 4000.1, CFPB) — every number below was
counted from the actual files or sourced from a cited document, not recalled or estimated.
**Status**: Verified finding, implemented (`010a-program-applicability-gating`). This document is
the corrected, final version — an earlier same-day version contained two errors, corrected here and
disclosed in the revision history rather than silently overwritten.

---

## Headline

**Gordon's belief is correct.** The real workbook encodes loan-program applicability in a
machine-readable way, primarily via a per-row Exception Code that carries a program prefix on 86%
of real rows, supplemented by a per-row SQL-style gating clause. Getting to this final, accurate
picture took two rounds of self-correction — both disclosed below, not smoothed over — because the
first pass read the wrong column, and the second pass didn't yet know one entire questionnaire
exports its columns in a different order than the other three.

---

## 1. The real data, corrected final counts

| | Count |
|---|---|
| Total real defect rows (has an Exception Code), across all 4 questionnaires / 3 sheets | **8,442** |
| Rows carrying a parseable per-row SQL gating clause ("Question Criteria") | 7,815 (92.6%) |
| Rows tagged with one of the 6 confirmed program prefixes (Exception Code) | **7,241 (85.8%)** |

## 2. The primary mechanism: the Exception Code prefix

| Prefix | Program | Real rows tagged | Format |
|---|---|---|---|
| `O-FNM-` | Fannie Mae | 2,676 | dash-delimited |
| `O-FRD-` | Freddie Mac | 1,860 | dash-delimited |
| `O-FHA-` | FHA | 1,104 | dash-delimited |
| `O-RHS-` | USDA (Rural Housing Service) | 865 | dash-delimited |
| `O-VA-` | VA | 720 | dash-delimited |
| `SONYMA` | State of New York Mortgage Agency | 46 | **space-delimited** (`SONYMA`, `SONYMA HDFC`, `SONYMA Tax `, ...) — confirmed by direct inspection to never carry a trailing dash, a genuinely different format from the other 5 |

Maps directly onto the 5 synthetic loans' own programs (`2025-0917-001`=Conventional/Fannie,
`2025-1004-FHA-002`=FHA, `2025-1108-VA-003`=VA, `2025-1215-FRD-004`=Freddie, `2025-1122-USDA-005`=
USDA). **SONYMA is added to the mapping table per Gordon's explicit direction (2026-07-20) even
though no synthetic loan fixture exists to test it against yet** — same posture as the still-
unconfirmed Jumbo tag (0 keyword hits in either workbook).

Other prefixes (`O-TILA-`, `O-ECOA-`, `O-FDPA-`, `O-HMDA-`, `O-CFPB-`, `O-FinCEN-`, `O-FCRA-`,
`O-ESIGN-`, `O-FED-`, `O-EPD-`, `O-CNTL-`, `O-BP-`) are federal-regulation, defect-type, or
administrative categories — confirmed by external research (§6 below) to be real, standard
compliance domains, not a program — correctly treated as applying to every program (fail-open).

## 3. The secondary mechanism: the per-row SQL gating clause

Every real defect row can carry its own `SELECT DISTINCT Loans.LoanID FROM Loans WHERE ...` clause,
narrowing applicability further on top of the program tag. Confirmed field/value pairs, captured
from the correct column across all 8,442 rows:

| Gated field | Distinct values | Notes |
|---|---|---|
| `QC_Policy` | `FHA`, `VA`, `USDA`, `Fannie Mae`, `Freddie Mac` | Agrees with, and independently confirms, the Exception Code prefix — belt and suspenders on the same row |
| `PropertyType` | 10 values (Condo/Co-op/PUD ×3 variants/2-4 unit/Manufactured, incl. 2 misspellings — `Condminium` and `Condo` alongside the correctly-spelled `Condominium`) | |
| `Occupancy` | 8 values (`Owner Occupied`, `Investment`, `Second Home`, `Primary`, `Primary Residence`, `1 Unit`, `2-4 Unit`, `Mixed-Use`) | **Directly answers the roadmap's own motivating example for this feature** ("owner-occupied vs. investment apply distinct rule sets") — encoded, not something to derive |
| `Underwriting_Type` | 6 values (`Desktop Underwriter`, `Loan Product Advisor`, `GUS`, `Manually Underwritten`, `Automated Underwriting`, `Loan Prospector`) | The AUS type |
| `LoanType` | `Conventional`, `Portfolio`, `Portfolio DHM` | |
| `LoanPurposeType` | `Construction`, `Purchase` | |
| `AddressState` | `NY` | |

**This feature (`010a`) implements PropertyType narrowing only** — Occupancy, Underwriting_Type,
LoanType, and LoanPurposeType are real, already-encoded, and confirmed usable, but explicitly
deferred to a future increment of `010a` itself (not `010b` — these are *already encoded*, not
*derived*, so they belong to `010a`'s own scope, just not this first pass). Named here so the
distinction survives: `010b`'s "derive remaining gating dimensions" framing may need less new work
than the roadmap originally assumed, once this increment happens.

## 4. A distinct, unrelated column: `Question Criteria by Questions`

Populated on 4,631 of 8,021 rows in the original (uncorrected) count — questionnaire branching logic
(whether this row's condition is even asked, based on how an *earlier question in the same audit*
was answered), not program gating. Not touched by this feature.

## 5. Two self-corrections made getting to this final picture

Disclosed in full, not smoothed over — both were caught by direct inspection, not by a second-guess
of the first pass alone:

1. **First correction (same day, earlier draft of this doc)**: the first pass searched column 6
   ("Question Response") for SQL clauses and found "615 gating rows," concluding the SQL mechanism
   was narrow and secondary (only ever gating on a blanket `QC_Policy = 'Fannie Mae'`, never
   FHA/VA/USDA). **This was wrong** — the real per-row SQL clause lives in column 7 ("Question
   Criteria"), populated on 96% of *standard-schema* rows, with `QC_Policy` carrying all 5 real GSE/
   agency values, not just Fannie Mae. The "615 rows" turned out to be an artifact of the second,
   larger correction below, not a real separate row category.
2. **Second correction (this revision)**: one entire questionnaire — **"Post-Closing Private Bank
   Oct 2025" (802 rows, confirmed 100% of that questionnaire, not a subset)** — exports every column
   from "Question Code" onward **one position left** of the shared 14-column header used by the
   other 3 sources. Its real Exception Code lives where the header labels "Question Answers
   Exception Name" (index 3), not "Exception Code" (index 8, which instead holds a severity word for
   these rows). Once corrected: the "615 standalone SQL-gating rows" from correction #1 disappear
   entirely (`sql_gating_rows_excluded` → 0) — they were shifted rows being misread as if their
   defect-text column held a raw SQL clause. Total real row count rose from 8,021 to **8,442** (421
   rows that were previously silently dropped, because their column-8 value under the wrong mapping
   was blank, are now correctly included). Confirmed isolated to this one questionnaire — the other
   3 sources (both Retail sheets, the small Private Bank "Pre Funding Nov 2025" sheet) read
   correctly under the standard mapping.

Fixed in `p0/eval_synth/taxonomy.py`'s `load_rows()` — detects the shifted questionnaire by
`Questionnaire Name` (the one field guaranteed correctly positioned regardless of the shift) and
applies a separate column map. Also found and fixed along the way: `taxonomy.py`'s own `main()`
listed Excel's `~$`-prefixed lock/temp files as real workbooks, crashing whenever the source files
were open in Excel — unrelated to the gating work, fixed in the same pass since it blocked running
the corrected loader at all.

## 6. Domain research (external, cited) — what this data actually means

A research pass (WebFetch/Tavily/Exa against Fannie Mae Selling Guide, HUD Handbook 4000.1, CFPB,
and industry QC sources) confirmed:

- **Post-closing QC is a real, investor-mandated process** (Fannie Mae Selling Guide D1-3; HUD
  Handbook 4000.1) — an independent function re-verifies closed loans on a sample (random +
  discretionary, the latter targeting fraud-risk/early-default loans), with findings reported and
  retained for years.
- **"Critical/Major/Minor" has real teeth**: Fannie Mae's Guide (D1-1-01) requires the *highest*
  tier to mean "this defect alone makes the loan ineligible for delivery" — i.e., buyback-triggering
  — while leaving exact tier definitions to the lender. This workbook's 3-tier scheme is the
  standard industry pattern, not house-specific noise. FHA runs a parallel, more codified 4-tier
  taxonomy (Handbook 4000.1 Appendix 8.0).
- **AOR (Area of Responsibility)** — routing findings to `Underwriter`/`Processor`/`Closer` — is a
  real, standard QC practice (defect-rate accountability by origination-chain role), not specific to
  this workbook's software. **Out of scope for `010a`** (it's a routing dimension, not a program
  gate) — worth a roadmap note for `008` (exception queue) later.
- **SONYMA** confirmed as a real NY state housing-finance program (est. 1970).
- **EPD** confirmed as Early Payment Default — a loan defaulting shortly after closing, an
  industry-wide fraud/underwriting-error signal and discretionary-QC-sample trigger.
- **Fannie Mae Form 1033** confirmed as their post-closing collateral/appraisal-quality review
  mechanism (2021+) — explains that category's ~102 rows.
- **ATR-QM** confirmed as the Dodd-Frank Ability-to-Repay/Qualified-Mortgage rule (12 CFR 1026,
  implementing Reg Z) — a federal compliance category, correctly treated as program-agnostic.
- **The stakes**: a QC finding leads to repurchase ("buyback") demand, indemnification, or
  regulatory exposure — confirms this project's own determinism/audit-defensibility thesis is
  proportionate to the real consequences, not overbuilt.

## 7. What this changes going forward

- `output/ROADMAP.md`'s `010a` entry corrected to name the Exception Code prefix (6 programs,
  including SONYMA) as primary, the per-row SQL clause (PropertyType built; Occupancy/
  Underwriting_Type/LoanType/LoanPurposeType found but deferred) as secondary.
- `010b`'s framing may need revisiting once the deferred SQL-clause dimensions are built — some of
  what it assumed needs *deriving* is already *encoded*.
- Severity-taxonomy alignment (this workbook's Critical/Major/Minor vs. `engine.py`'s CRITICAL/
  WARNING/INFO) and AOR-based routing are both real, confirmed, out-of-scope-for-`010a` findings —
  named for whichever future spec (likely `006`/`008`) is positioned to use them.

## 8. Pre-test compile-scope assumption: loan 01 / loan 04 treated as Fannie Mae

**Status: an explicit, documented test simplification — not a derived finding.** Do not treat this
as a real gating result; it exists so a small LLM-compile pre-test has a bounded row set to run
against, ahead of `010b` making the underlying signal real.

- **The gap this papers over**: neither loan 01 nor loan 04's real MISMO data carries a GSE-investor
  field. Both report `MortgageType = Conventional` and nothing more specific. Loan 04's fixture
  label ("Freddie Mac Cash-Out Refi" in `build_fixtures.py`'s `LOAN_PACKAGES`) is descriptive
  metadata the fixture author typed in — the code's own comment says it's "never used by
  `verify_against_defects.py`'s field-level checks." So both loans are genuinely ambiguous between
  Fannie Mae and Freddie Mac from the data alone (§5's `AMBIGUOUS` sentinel in `program_gating.py`
  returns exactly this for both).
- **The assumption**: for scoping *this* pre-test only, loan 01 and loan 04 are assumed Fannie Mae.
  Freddie Mac is dropped from the pre-test's compile scope entirely as a result.
- **Effect on scope**: relevant rows drop from the conservative (Fannie ∪ Freddie, both kept because
  ambiguous) **7,225 / 8,442 (85.6%)** down to **5,365 / 8,442 (63.5%)** — Fannie Mae (2,676) + FHA
  (1,104) + USDA (865) + VA (720). SONYMA (46) and untagged (1,171) rows remain out of scope
  regardless, unchanged from §1.
- **How this gets made real**: `010b-derive-remaining-gating-dimensions` is where a real AUS/
  investor/lender field gets added to the loan data (via `000`'s synthetic generator or real fixture
  data) so Fannie-vs-Freddie resolves from evidence instead of assumption. When that lands, this
  section should be struck through or replaced, not left standing as if it were still current.

## Revision history

- **2026-07-20, first version**: found the Exception Code prefix (5 programs) and a "615-row SQL
  gating" mechanism, both read from the wrong column for one questionnaire.
- **2026-07-20, this revision**: corrected after a full column/sheet audit + domain research —
  fixed the column read, added SONYMA (space-delimited format, 46 rows), found the real 8,442-row
  total, found the SQL clause's fuller field set (Occupancy, Underwriting_Type, etc.), and retired
  the "615 rows" claim as an artifact of the column-shift bug, not a real finding.
- **2026-07-20, §8 added**: documented the loan 01/04 assumed-Fannie pre-test scoping simplification
  (7,225 → 5,365 relevant rows) ahead of a real LLM-compile pre-test — explicitly flagged as an
  assumption to retire once `010b` adds a real investor/AUS field.
