# SME Review Packet — income-verification block triage

**616 rules / 580 unique (question, condition) groups.** Every classification
below is a *proposal* pending your review — mark each check agree / correct.
Bins: GREEN = automatable now · YELLOW = automatable after data/guide work ·
RED = stays human · NOT_A_CHECK = pass/N-A answer option, not a defect rule.

**Source workbook:** `PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv` — row numbers below are Excel-style
(header = row 1), so you can open the sheet and jump straight to each rule.

**Note on this block vs the first two:** dedup collapse (616 rules -> 580 groups, ~1.06x) sits between application-verification's ~1.5x and asset-verification's ~1.02x. GREEN is 100% doc_presence auto-compiles (0% 'mapped' — the block's one hand-built shape, SelfEmployedDocsShape, is wired to zero AMQ exception codes today, the same latent-shape bug already fixed for GiftEvidenceShape/LargeDepositShape). Given ~474 groups needing real judgment (more than double asset-verification's ~210), six recurring exception-code families that repeat verbatim under many different AMQ question categories (Income Breakdown x19, VVOE Inactive x7, 3rdParty x5, IncomeWork x5, plus smaller ones) were classified once per family rather than once per repetition; the remaining groups were classified by a deterministic keyword scan of each row's own text against a curated list of income-document families, stating per group which specific document/fact family is missing — see `layer2_triage_income.py`'s module docstring for the full method and decision 021 for the six individually hand-verified RED calls and the two verified READY_TO_BUILD candidates.

## Headline

| Bin | Groups | Rules | % of defect groups |
|---|---|---|---|
| GREEN | 28 | 28 | 6% |
| YELLOW | 467 | 482 | 93% |
| RED | 6 | 6 | 1% |
| NOT_A_CHECK | 79 | 100 | — |

## READY TO BUILD candidates (flagged, not implemented)

- **G512** (O-VA, row 2487, codes O-VA-00364): WIRE, don't build — SelfEmployedDocsShape (CHK-INC-001) already checks exactly this fact (borrower_self_employed AND (ytd_pnl_in_file=false OR ytd_balance_sheet_in_file=false)), extracted today from loan 04's Self-Employed Income Documentation Index (both facts populate: that index marks both docs NOT IN FILE). MAPPED_SHAPES wires the shape to ZERO amq_exception_codes today. Row's exception_description ('the file did not contain a YTD profit and loss statement and current balance sheet') reads naturally as the same either-missing test the shape already implements.
- **G529** (O-FHA, row 2410, codes O-FHA-02293): WIRE, don't build — same fact as O-VA-00364, FHA wording variant ('A YTD P&L and balance sheet was required but not in the file'). Verified: a full-text keyword sweep of every other self-employed/business-income row in this block found no other agency row mentioning both 'profit and loss' and 'balance sheet' together — these two are the only matches.

## GREEN

### G057 — O-FHA-02309 [O-FHA]
- **Q:** Were all AUS specific other income requirements met?
- **Defect condition:** The legal agreement establishing annuity & receipt of annuity income were not verified & documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2106
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: bank_statement
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier — already works.
- **SME:** [ ] agree [ ] correct: ______

### G066 — O-FRD-57133 [O-FRD]
- **Q:** Were all Alimony, Child Support and/or Maintenance income requirements met?
- **Defect condition:** Receipt of alimony/child supp/maint in borr's acct, 3rd party money app, or govn't stmt not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2094
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: bank_statement
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier — already works.
- **SME:** [ ] agree [ ] correct: ______

### G078 — O-FRD-50431 [O-FRD]
- **Q:** Were all Part-Time, Second Job, Seasonal and/or Unemployment income requirements met?
- **Defect condition:** 2nd job pay missing YTD paystub, W2s or VOE & 10 day PCV for Streamlined Accept and Standard Doc
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2476
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: voe
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier — already works.
- **SME:** [ ] agree [ ] correct: ______

### G085 — O-FRD-50005 [O-FRD]
- **Q:** Were all Social Security, Retirement and/or Disability income requirements met?
- **Defect condition:** Long-term disability did not meet history and continuance req's &/or req'd documents not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2328
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: bank_statement
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier — already works.
- **SME:** [ ] agree [ ] correct: ______

### G088 — O-FRD-00409 [O-FRD]
- **Q:** Were all Social Security, Retirement and/or Disability income requirements met?
- **Defect condition:** Retirement income did not meet history and continuance req's &/or req'd documents not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2453
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: bank_statement
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier — already works.
- **SME:** [ ] agree [ ] correct: ______

### G101 — O-FRD-03078 [O-FRD]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** Contractor/contingent income used, most recent 2 yr 1099s, YTD paystubs & tax returns not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2178
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: paystub
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier — already works.
- **SME:** [ ] agree [ ] correct: ______

### G164 — O-RHS-50551 [O-RHS]
- **Q:** Were all annual household income requirements met?
- **Defect condition:** Evidence borrower is not an owner in familial owned employer not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2193
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: voe
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier — already works.
- **SME:** [ ] agree [ ] correct: ______

### G175 — O-FNM-51829 [O-FNM]
- **Q:** Were all anticipated income requirements met?
- **Defect condition:** Employment start date within 30 days prior to the Note date missing offer/contract & paystub or VVOE
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2107
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: paystub
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier — already works.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.2-02 — Standards for Employment-Related Income (PDF p.330)
- **Guide candidate:** B3-3.3-07 — Restricted Stock Units and Restricted Stock Employment Income (PDF p.344)
- **SME:** [ ] agree [ ] correct: ______

### G194 — O-FNM-00347 [O-FNM]
- **Q:** Were all base pay (salary and hourly), bonus, tip, and overtime income requirements met?
- **Defect condition:** Combination of paystub and previous 2 yrs W2s or a VOE to verify bonus and OT income not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2131
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: voe
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier — already works.
- **Guide candidate:** B3-3.3-02 — Bonus, Commission, Overtime, and Tip Income (PDF p.335)
- **Guide candidate:** B3-3.3-01 — Base Income (PDF p.333)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G204 — O-FNM-00348 [O-FNM]
- **Q:** Were all commission income requirements met?
- **Defect condition:** Combination of paystub and previous 2 yrs W-2s or a VOE to verify commission income not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2152
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: voe
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier — already works.
- **Guide candidate:** B3-3.3-02 — Bonus, Commission, Overtime, and Tip Income (PDF p.335)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.1-01 — General Income Information (PDF p.318)
- **SME:** [ ] agree [ ] correct: ______

### G225 — O-FHA-50021 [O-FHA]
- **Q:** Were all employment income requirements met?
- **Defect condition:** A VOE or alternative documentation acceptable to FHA covering the last 2 years was not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2541
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: voe
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier — already works.
- **SME:** [ ] agree [ ] correct: ______

### G239 — O-FHA-50022 [O-FHA]
- **Q:** Were all employment income requirements met?
- **Defect condition:** Reverification of employment or VVOE was not in the file or not within 10 days of Note date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2457
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: voe
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier — already works.
- **SME:** [ ] agree [ ] correct: ______

### G257 — O-VA-00315 [O-VA]
- **Q:** Were all general income and verification requirements met?
- **Defect condition:** Alt Docs-Missing one or more req’d docs, 30 day paystub, W2s, VVOE
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2100
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: paystub
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier — already works.
- **SME:** [ ] agree [ ] correct: ______

### G273 — O-RHS-02720 [O-RHS]
- **Q:** Were all general income verification requirements met?
- **Defect condition:** Alt doc missing VOE, recent paystub reasonable to YTD earnings & 10 bus day VVOE/other written verif
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2099
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: voe
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier — already works.
- **SME:** [ ] agree [ ] correct: ______

### G274 — O-RHS-59422 [O-RHS]
- **Q:** Were all general income verification requirements met?
- **Defect condition:** File missing prior employment proof: W-2, VOE, 3rd-party verif, education, or military docs
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2406
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: voe
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier — already works.
- **SME:** [ ] agree [ ] correct: ______

### G317 — O-FRD-50424 [O-FRD]
- **Q:** Were all income verification requirements met?
- **Defect condition:** VOE missing signature, printed name, title, contact info of the rep who verified the information
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2570
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: voe
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier — already works.
- **SME:** [ ] agree [ ] correct: ______

### G321 — O-FRD-50422 [O-FRD]
- **Q:** Were all income verification requirements met?
- **Defect condition:** YTD paystub did not contain all identifying & earnings info required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2580
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: paystub
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier — already works.
- **SME:** [ ] agree [ ] correct: ______

### G345 — O-FRD-50426 [O-FRD]
- **Q:** Were all military income requirements met?
- **Defect condition:** Written VOE for current military active-duty did not contain all req'd info
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2354
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: voe
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier — already works.
- **SME:** [ ] agree [ ] correct: ______

### G362 — O-FRD-50008 [O-FRD]
- **Q:** Were all other income requirements met?
- **Defect condition:** A standard VOE, employer letter, paystub reflecting the housing allowance was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2233
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: voe
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier — already works.
- **SME:** [ ] agree [ ] correct: ______

### G365 — O-FRD-50433 [O-FRD]
- **Q:** Were all other income requirements met?
- **Defect condition:** All documentation requirements for auto allowance was not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2122
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: voe
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier — already works.
- **SME:** [ ] agree [ ] correct: ______

### G398 — O-FRD-50014 [O-FRD]
- **Q:** Were all other income requirements met?
- **Defect condition:** Verification tip income has been received for the previous two years was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2176
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: voe
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier — already works.
- **SME:** [ ] agree [ ] correct: ______

### G406 — O-FRD-03079 [O-FRD]
- **Q:** Were all overtime, bonus, tips, or commission income requirements met?
- **Defect condition:** Commission income missing YTD paystub with most recent 2 yrs W2s or VOE &/or 10 day PCV
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2153
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: voe
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier — already works.
- **SME:** [ ] agree [ ] correct: ______

### G409 — O-FRD-50011 [O-FRD]
- **Q:** Were all overtime, bonus, tips, or commission income requirements met?
- **Defect condition:** Verification that the OT/bonus income has been received for the last two years was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2132
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: voe
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier — already works.
- **SME:** [ ] agree [ ] correct: ______

### G428 — O-FRD-00413 [O-FRD]
- **Q:** Were all rental income requirements met?
- **Defect condition:** Lease unavail for 2-4 OO/1-4 NOO/non-subj inv bought/rented in last year missing Form 72 or Form 100
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2062
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: appraisal
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier — already works.
- **SME:** [ ] agree [ ] correct: ______

### G462 — O-FNM-57392 [O-FNM]
- **Q:** Were all restricted stock units and restricted stock income requirements met?_x000D_
- **Defect condition:** Missing RSU/RS stmt showing previous year(s) distribution & number of vested shares/cash equivalent
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2441
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: bank_statement
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier — already works.
- **Guide candidate:** B3-3.3-07 — Restricted Stock Units and Restricted Stock Employment Income (PDF p.344)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **SME:** [ ] agree [ ] correct: ______

### G463 — O-FNM-57393 [O-FNM]
- **Q:** Were all restricted stock units and restricted stock income requirements met?_x000D_
- **Defect condition:** Missing completed VOE reflecting distributions or a recent paystub showing receipt of RSU/RS income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2445
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: voe
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier — already works.
- **Guide candidate:** B3-3.3-07 — Restricted Stock Units and Restricted Stock Employment Income (PDF p.344)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.1-01 — General Income Information (PDF p.318)
- **SME:** [ ] agree [ ] correct: ______

### G568 — O-FNM-55906 [O-FNM]
- **Q:** Were all verbal verification of employment requirements met?
- **Defect condition:** Missing employer work email exchange dated within 10 business days PTC for alternative VOE method
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2101
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: voe
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier — already works.
- **Guide candidate:** B3-3.1-04 — Verbal Veriﬁcation of Employment (PDF p.324)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.2-02 — Standards for Employment-Related Income (PDF p.330)
- **SME:** [ ] agree [ ] correct: ______

### G579 — O-RHS-02775 [O-RHS]
- **Q:** Were all wage earner income requirements met?
- **Defect condition:** Verbal verification of employment no more than 10 bus. days prior to the note date was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2563
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: voe
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier — already works.
- **SME:** [ ] agree [ ] correct: ______

## YELLOW

### G001 — O-VA-00399 [O-VA]
- **Q:** Did the Alimony, Child Support and/or Maintenance income meet all requirements and was it calculated correctly?
- **Defect condition:** Alimony/child support/maintenance missing legal docs &/or history and continuance req's not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2090
- **Severity:** Critical
- **Data needed:** alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once alimony/child-support legal decree or written agreement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G002 — O-VA-58301 [O-VA]
- **Q:** Did the Alimony, Child Support and/or Maintenance income meet all requirements and was it calculated correctly?
- **Defect condition:** The alimony, child support and/or maintenance income was not calculated correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2092
- **Severity:** Critical
- **Data needed:** alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once alimony/child-support legal decree or written agreement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G004 — O-VA-50764 [O-VA]
- **Q:** Did the Military income meet all requirements and was it calculated correctly?
- **Defect condition:** Applicant is active military without a Military Leave and Earnings Statement provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2350
- **Severity:** Critical
- **Data needed:** military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once military Leave & Earnings Statement (LES) / VA benefits award letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G005 — O-VA-03073 [O-VA]
- **Q:** Did the Military income meet all requirements and was it calculated correctly?
- **Defect condition:** Borr is in Nat'l Guard or Reserves, no analysis of impact to income due to activation in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2341
- **Severity:** Critical
- **Data needed:** military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once military Leave & Earnings Statement (LES) / VA benefits award letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G006 — O-VA-00313 [O-VA]
- **Q:** Did the Military income meet all requirements and was it calculated correctly?
- **Defect condition:** Service member within 12 mos of release from active duty, employment intentions were not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2502
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once military Leave & Earnings Statement (LES) / VA benefits award letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G007 — O-VA-58299 [O-VA]
- **Q:** Did the Military income meet all requirements and was it calculated correctly?
- **Defect condition:** The military income was not calculated correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2348
- **Severity:** Critical
- **Data needed:** military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once military Leave & Earnings Statement (LES) / VA benefits award letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G008 — O-VA-50765 [O-VA]
- **Q:** Did the Military income meet all requirements and was it calculated correctly?
- **Defect condition:** The type, amount, history of receipt not documented for other military allowances
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2342
- **Severity:** Critical
- **Data needed:** military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once military Leave & Earnings Statement (LES) / VA benefits award letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G009 — O-VA-00321 [O-VA]
- **Q:** Did the Military income meet all requirements and was it calculated correctly?
- **Defect condition:** Verification of the military quarters allowance was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2352
- **Severity:** Critical
- **Data needed:** military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once military Leave & Earnings Statement (LES) / VA benefits award letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G011 — O-VA-00318 [O-VA]
- **Q:** Did the Part-Time, Second Job, Seasonal and/or Unemployment income meet all requirements and was it calculated correctly?
- **Defect condition:** 2nd job, part-time, bonus used w/out supporting documents &/or history & continuance req's not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2386
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G012 — O-VA-50013 [O-VA]
- **Q:** Did the Part-Time, Second Job, Seasonal and/or Unemployment income meet all requirements and was it calculated correctly?
- **Defect condition:** The file does not contain evidence of the seasonal income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2472
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G013 — O-VA-50014 [O-VA]
- **Q:** Did the Part-Time, Second Job, Seasonal and/or Unemployment income meet all requirements and was it calculated correctly?
- **Defect condition:** The file does not contain satisfactory evidence of the unemployment income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2546
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G014 — O-VA-58298 [O-VA]
- **Q:** Did the Part-Time, Second Job, Seasonal and/or Unemployment income meet all requirements and was it calculated correctly?
- **Defect condition:** The part-time, second job, seasonal and/or unemployment income was not calculated correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2396
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G016 — O-VA-55972 [O-VA]
- **Q:** Did the Social Security, Retirement and/or Disability income meet all requirements and was it calculated correctly?
- **Defect condition:** No VA award letter, bank stmt or similar to document monthly retirement, pension &/or disability
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2455
- **Severity:** Critical
- **Data needed:** benefits/award letter (SSA, VA, pension, or disability payer) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once benefits/award letter (SSA, VA, pension, or disability payer) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G017 — O-VA-00398 [O-VA]
- **Q:** Did the Social Security, Retirement and/or Disability income meet all requirements and was it calculated correctly?
- **Defect condition:** Retirement, royalty, deposit accts used without all req'd docs &/or did not meet history/cont req's
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2451
- **Severity:** Critical
- **Data needed:** disability-benefits payer statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once disability-benefits payer statement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G018 — O-VA-58300 [O-VA]
- **Q:** Did the Social Security, Retirement and/or Disability income meet all requirements and was it calculated correctly?
- **Defect condition:** The social security, retirement and/or disability income was not calculated correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2514
- **Severity:** Critical
- **Data needed:** disability-benefits payer statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once disability-benefits payer statement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G020 — O-VA-50766 [O-VA]
- **Q:** Did the other income meet all requirements and was it calculated correctly?
- **Defect condition:** A copy of the govn't issued Mortgage Credit Certificate not in file where MCC's were used
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2361
- **Severity:** Critical
- **Data needed:** Mortgage Credit Certificate (MCC) document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once Mortgage Credit Certificate (MCC) document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G021 — O-VA-00322 [O-VA]
- **Q:** Did the other income meet all requirements and was it calculated correctly?
- **Defect condition:** Car Allowance- Net amount by which the allowance exceeds the actual expense was not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2118
- **Severity:** Critical
- **Data needed:** automobile-allowance employer letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once automobile-allowance employer letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G022 — O-VA-00401 [O-VA]
- **Q:** Did the other income meet all requirements and was it calculated correctly?
- **Defect condition:** Documentation verifying tax exempt income will continue & remain untaxed was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2518
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G023 — O-VA-50011 [O-VA]
- **Q:** Did the other income meet all requirements and was it calculated correctly?
- **Defect condition:** File does not contain satisfactory evidence of total gross qualifying foster care income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2212
- **Severity:** Critical
- **Data needed:** foster-care sponsoring-organization verification letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once foster-care sponsoring-organization verification letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G024 — O-VA-00400 [O-VA]
- **Q:** Did the other income meet all requirements and was it calculated correctly?
- **Defect condition:** Income from public assistance was considered without documenting at least a 3-year continuance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2416
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G027 — O-VA-50012 [O-VA]
- **Q:** Did the other income meet all requirements and was it calculated correctly?
- **Defect condition:** Royalty payments used and the file does not contain satisfactory evidence of the income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2459
- **Severity:** Critical
- **Data needed:** royalty contract/agreement + tax-return schedule — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once royalty contract/agreement + tax-return schedule is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G028 — O-VA-58302 [O-VA]
- **Q:** Did the other income meet all requirements and was it calculated correctly?
- **Defect condition:** The other income  used to qualify was not calculated correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2385
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G029 — O-VA-55742 [O-VA]
- **Q:** Did the other income meet all requirements and was it calculated correctly?
- **Defect condition:** The trust income history of receipt and at least 3 years continuance was not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2539
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** trust agreement/trustee statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once trust agreement/trustee statement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G030 — O-VA-00320 [O-VA]
- **Q:** Did the overtime, bonus or commission income meet all requirements and was it calculated correctly?
- **Defect condition:** Comm. income does not satisfy VA's requirement of having continued for 2 yrs to be considered stable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2155, 2156
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G031 — O-VA-50763 [O-VA]
- **Q:** Did the overtime, bonus or commission income meet all requirements and was it calculated correctly?
- **Defect condition:** Income from OT, part-time, 2nd job or bonuses not verified for past 2 yrs or unlikely to continue
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2393
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G032 — O-VA-51188 [O-VA]
- **Q:** Did the overtime, bonus or commission income meet all requirements and was it calculated correctly?
- **Defect condition:** The file did not document the YTD, basis for payments & pay frequency for commission income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2150
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G033 — O-VA-58296 [O-VA]
- **Q:** Did the overtime, bonus or commission income meet all requirements and was it calculated correctly?
- **Defect condition:** The overtime, bonus and/or commission income was not calculated correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2392
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G035 — O-VA-00404 [O-VA]
- **Q:** Did the rental income meet all requirements and was it calculated correctly?
- **Defect condition:** Multi-unit property rental income used without documenting prior landlord experience
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2313
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G036 — O-VA-51060 [O-VA]
- **Q:** Did the rental income meet all requirements and was it calculated correctly?
- **Defect condition:** Rental income considered without a copy of the lease or rental agreement in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2314
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G037 — O-VA-50804 [O-VA]
- **Q:** Did the rental income meet all requirements and was it calculated correctly?
- **Defect condition:** Rental income used to qualify was not calculated correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2429
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G038 — O-VA-00405 [O-VA]
- **Q:** Did the rental income meet all requirements and was it calculated correctly?
- **Defect condition:** Two yrs rental income not documented w/ copies of signed tax returns/schedules
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2433
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G040 — O-VA-00308 [O-VA]
- **Q:** Did the wage earner income meet all requirements and was it calculated correctly?
- **Defect condition:** All income from employment was not verified for each individual contractually obligated on the loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2184
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G041 — O-VA-00310 [O-VA]
- **Q:** Did the wage earner income meet all requirements and was it calculated correctly?
- **Defect condition:** Current employment less than 12 mos & continued employment is unreasonable & analysis not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2319
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G042 — O-VA-50819 [O-VA]
- **Q:** Did the wage earner income meet all requirements and was it calculated correctly?
- **Defect condition:** The wage income was not calculated correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2261
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G043 — 3rdParty [O-VA]
- **Q:** Did the wage earner income meet all requirements and was it calculated correctly?
- **Defect condition:** Vendor for 3rd party VOE was not Equifax/TWN or manual process not followed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2068
- **Severity:** Critical
- **Data needed:** a VOE-vendor-name field (e.g. Equifax/The Work Number) — not currently captured from any document
- **Rationale:** Recurs identically under 5 different AMQ question categories. Crisp presence/identity check once a vendor-name field exists; no such field is in FIELD_SPECS['voe'] today.
- **SME:** [ ] agree [ ] correct: ______

### G046 — O-FRD-59130 [O-FRD]
- **Q:** Were additional self-employed income requirements met?
- **Defect condition:** SE income calc incorrectly &/or Form 91/Income Calc Report/FHLMC Calc Cert or similar was missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2486
- **Severity:** Critical
- **Data needed:** income-calculation worksheet/tool output — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once income-calculation worksheet/tool output is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G047 — O-FRD-56077 [O-FRD]
- **Q:** Were all 1099 income requirements met?
- **Defect condition:** 1099 income less than 2 yrs without a written analysis & documentation justifying stability
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2059
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** 1099 (or Form 4137 tip-income) tax form — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once 1099 (or Form 4137 tip-income) tax form is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G048 — O-FRD-56079 [O-FRD]
- **Q:** Were all 1099 income requirements met?
- **Defect condition:** 1099 income not averaged correctly using the documented history & expense reduction as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2056
- **Severity:** Critical
- **Data needed:** 1099 (or Form 4137 tip-income) tax form — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once 1099 (or Form 4137 tip-income) tax form is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G049 — O-FRD-56078 [O-FRD]
- **Q:** Were all 1099 income requirements met?
- **Defect condition:** 1099 income not documented as likely to continue for at least the next 3 years
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2057
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** 1099 (or Form 4137 tip-income) tax form — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once 1099 (or Form 4137 tip-income) tax form is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G050 — O-FRD-56076 [O-FRD]
- **Q:** Were all 1099 income requirements met?
- **Defect condition:** 1099 income not documented with 2 years 1099's, YTD paystubs/equivalent & pgs 1 & 2 tax returns
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2058
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** 1099 (or Form 4137 tip-income) tax form — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once 1099 (or Form 4137 tip-income) tax form is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G052 — O-FRD-56081 [O-FRD]
- **Q:** Were all 1099 income requirements met?
- **Defect condition:** Schedule C 1099 expenses exceed 5% of gross receipts or sales after deducting non-cash expenses
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2465
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** Schedule C business tax-return page — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once Schedule C business tax-return page is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G053 — O-FRD-56083 [O-FRD]
- **Q:** Were all 1099 income requirements met?
- **Defect condition:** Schedule C does not reflect a 12-month history of 1099 income and reported expenses
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2468
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** Schedule C business tax-return page — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once Schedule C business tax-return page is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G054 — O-FRD-56080 [O-FRD]
- **Q:** Were all 1099 income requirements met?
- **Defect condition:** Schedule C gross receipts or sales do not equal to the total amount(s) reported on IRS Form 1099(s)
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2467
- **Severity:** Critical
- **Data needed:** Schedule C business tax-return page — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once Schedule C business tax-return page is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G055 — O-FRD-56082 [O-FRD]
- **Q:** Were all 1099 income requirements met?
- **Defect condition:** Schedule C used for 1099 income is reported an amount for the cost of goods sold
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2466
- **Severity:** Critical
- **Data needed:** Schedule C business tax-return page — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once Schedule C business tax-return page is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G058 — O-FHA-02306 [O-FHA]
- **Q:** Were all AUS specific other income requirements met?
- **Defect condition:** Three years tax returns were not obtained to evaluate the borrower's earnings trend of capital gains
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2146
- **Severity:** Critical
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G059 — O-FHA-02291 [O-FHA]
- **Q:** Were all AUS specific self-employment income requirements met?
- **Defect condition:** Business tax returns for the most recent 2 yrs, including all schedules, or an alt not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2139
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G061 — O-FRD-00407 [O-FRD]
- **Q:** Were all Alimony, Child Support and/or Maintenance income requirements met?
- **Defect condition:** Alimony/child supp/maintenance not supported w/ legal docs &/or 6 mos history & continuance not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2093
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once alimony/child-support legal decree or written agreement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G062 — O-FRD-51643 [O-FRD]
- **Q:** Were all Alimony, Child Support and/or Maintenance income requirements met?
- **Defect condition:** Alimony/maintenance payments with more than 10 mos left was not deducted from gross monthly income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2095
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once alimony/child-support legal decree or written agreement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G063 — O-FRD-50006 [O-FRD]
- **Q:** Were all Alimony, Child Support and/or Maintenance income requirements met?
- **Defect condition:** Foster income-2 yr history from organization verifying total gross qualifying income not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2211
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once alimony/child-support legal decree or written agreement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G064 — Income Breakdown [O-FRD]
- **Q:** Were all Alimony, Child Support and/or Maintenance income requirements met?
- **Defect condition:** Income submitted to AUS is not accurate - broken out and/or categorized correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2252
- **Severity:** Critical
- **Data needed:** a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute
- **Rationale:** Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- **SME:** [ ] agree [ ] correct: ______

### G067 — O-FHA-00780, O-FNM-00045, O-FRD-00039, O-VA-55432 [O-FHA/O-FNM/O-FRD/O-VA]
- **Q:** Were all IRS Form 4506-C requirements met?
- **Defect condition:** 4506-C not completed & signed prior to or at closing for each borrower whose income used to qualify
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2304, 2305, 2306, 2307
- **Severity:** Major/Minor
- **Data needed:** IRS Form 4506-C/8821 tax-transcript consent form — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once IRS Form 4506-C/8821 tax-transcript consent form is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.6-02 — Income Reported on IRS Form 1040 (PDF p.391)
- **Guide candidate:** B3-3.6-03 — Income or Loss Reported on IRS Form 1040, Schedule C (PDF p.393)
- **Guide candidate:** B3-3.6-04 — Income or Loss Reported on IRS Form 1040, Schedule D (PDF p.394)
- **SME:** [ ] agree [ ] correct: ______

### G068 — O-RHS-02765 [O-RHS]
- **Q:** Were all IRS Form 4506-C requirements met?
- **Defect condition:** A completed & signed 4506-C/8821 not in the file for each adult household member, as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2308
- **Severity:** Critical
- **Data needed:** IRS Form 4506-C/8821 tax-transcript consent form — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once IRS Form 4506-C/8821 tax-transcript consent form is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G069 — O-FNM-55308, O-FRD-55720 [O-FHA/O-FNM/O-FRD/O-RHS/O-VA]
- **Q:** Were all IRS Form 4506-C requirements met?
- **Defect condition:** Non Code 10 IRS rejection & evidence of attempts to get a corrected & signed 4506-C not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2071, 2072, 2073, 2074, 2075
- **Severity:** Critical
- **Data needed:** IRS Form 4506-C/8821 tax-transcript consent form — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once IRS Form 4506-C/8821 tax-transcript consent form is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.6-02 — Income Reported on IRS Form 1040 (PDF p.391)
- **Guide candidate:** B3-3.6-03 — Income or Loss Reported on IRS Form 1040, Schedule C (PDF p.393)
- **Guide candidate:** B3-3.6-04 — Income or Loss Reported on IRS Form 1040, Schedule D (PDF p.394)
- **SME:** [ ] agree [ ] correct: ______

### G071 — O-FNM-55722, O-FRD-55721 [O-FNM/O-FRD]
- **Q:** Were all IRS Form 4506-C requirements met?
- **Defect condition:** Steps not taken to confirm borr identity & escalated as applicable for IRS 4506-C Code 10 rejection
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2069, 2070
- **Severity:** Critical
- **Data needed:** IRS Form 4506-C/8821 tax-transcript consent form — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once IRS Form 4506-C/8821 tax-transcript consent form is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.6-02 — Income Reported on IRS Form 1040 (PDF p.391)
- **Guide candidate:** B3-3.6-03 — Income or Loss Reported on IRS Form 1040, Schedule C (PDF p.393)
- **Guide candidate:** B3-3.6-04 — Income or Loss Reported on IRS Form 1040, Schedule D (PDF p.394)
- **SME:** [ ] agree [ ] correct: ______

### G072 — Epic4506C [O-FHA/O-FNM/O-FRD/O-RHS/O-VA]
- **Q:** Were all IRS Form 4506-C requirements met?
- **Defect condition:** The 4506C screen in EPIC is incomplete or incorrect (IE. Record of Account)
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2186, 2187, 2188, 2189, 2190
- **Severity:** Major
- **Data needed:** a lender-system (EPIC) 4506-C screen-completeness fact — not derivable from any loan document; this is internal LOS/servicing-system screen data, not a document in the closed-loan file
- **Rationale:** Recurs across all 5 agencies under 'IRS Form 4506-C requirements'; genuinely different in kind from the other 4506-C rows (which check the signed FORM itself) — this checks an internal system screen's state, closer to the Bucket-C external-system-state pattern flagged for the NMLS/RE-license rules (decisions 016/017) than a document-presence gap, though not itself a live external registry lookup. Kept YELLOW, flagged for a human to consider whether it belongs in scope at all.
- **Guide candidate:** B3-3.6-02 — Income Reported on IRS Form 1040 (PDF p.391)
- **Guide candidate:** B3-3.6-03 — Income or Loss Reported on IRS Form 1040, Schedule C (PDF p.393)
- **Guide candidate:** B3-3.6-04 — Income or Loss Reported on IRS Form 1040, Schedule D (PDF p.394)
- **SME:** [ ] agree [ ] correct: ______

### G073 — O-FRD-57518 [O-FRD]
- **Q:** Were all IRS Form 4506-C requirements met?
- **Defect condition:** The signed IRS Form 4506-C or an alternate acceptable form was not retained in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2503, 2504
- **Severity:** Critical
- **Data needed:** IRS Form 4506-C/8821 tax-transcript consent form — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once IRS Form 4506-C/8821 tax-transcript consent form is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G075 — O-FRD-52257 [O-FRD]
- **Q:** Were all IRS verification requirements met?
- **Defect condition:** Taxpayer’s consent form did not include all entities that information can be shared with
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2521
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G076 — O-FRD-52256 [O-FRD]
- **Q:** Were all IRS verification requirements met?
- **Defect condition:** Taxpayer’s consent was required and the consent form is not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2520
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G077 — O-FRD-50430 [O-FRD]
- **Q:** Were all Part-Time, Second Job, Seasonal and/or Unemployment income requirements met?
- **Defect condition:** 2nd job of 1 year but less than 2 years did not meet stability requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2475
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G080 — O-FRD-03086 [O-FRD]
- **Q:** Were all Part-Time, Second Job, Seasonal and/or Unemployment income requirements met?
- **Defect condition:** Seasonal unemployment history & continuance req's not met &/or no evidence of receipt for last 2 yrs
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2473
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G081 — O-FRD-54303 [O-FRD]
- **Q:** Were all Social Security, Retirement and/or Disability income requirements met?
- **Defect condition:** Borr not qualified on lesser of the future long-term or current short-term disability payments
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2219
- **Severity:** Critical
- **Data needed:** disability-benefits payer statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once disability-benefits payer statement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G082 — O-FRD-54302 [O-FRD]
- **Q:** Were all Social Security, Retirement and/or Disability income requirements met?
- **Defect condition:** Future long-term disability used & no current short-term converting to long-term &/or not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2221
- **Severity:** Critical
- **Data needed:** disability-benefits payer statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once disability-benefits payer statement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G083 — O-FRD-54304 [O-FRD]
- **Q:** Were all Social Security, Retirement and/or Disability income requirements met?
- **Defect condition:** Future long-term disability used and the source, type, amount, and payment frequency not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2220
- **Severity:** Critical
- **Data needed:** disability-benefits payer statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once disability-benefits payer statement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G084 — Income Breakdown [O-FRD]
- **Q:** Were all Social Security, Retirement and/or Disability income requirements met?
- **Defect condition:** Income submitted to AUS is not accurate - broken out and/or categorized correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2247
- **Severity:** Critical
- **Data needed:** a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute
- **Rationale:** Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- **SME:** [ ] agree [ ] correct: ______

### G087 — O-FRD-00415 [O-FRD]
- **Q:** Were all Social Security, Retirement and/or Disability income requirements met?
- **Defect condition:** Retirement assets as income-Documentation verifying source, amt, frequency & receipt not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2447
- **Severity:** Critical
- **Data needed:** retirement-account statement (401(k)/IRA/Keogh/pension) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once retirement-account statement (401(k)/IRA/Keogh/pension) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G089 — O-FRD-50441 [O-FRD]
- **Q:** Were all Social Security, Retirement and/or Disability income requirements met?
- **Defect condition:** SSA verification letter or evidence of receipt of benefit not in the file for Social Security income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2510
- **Severity:** Critical
- **Data needed:** 1099 (or Form 4137 tip-income) tax form — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once 1099 (or Form 4137 tip-income) tax form is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G090 — O-RHS-02760 [O-RHS]
- **Q:** Were all additional annual household income requirements met?
- **Defect condition:** Adjusted annual income included a child care expense deduction without documenting eligibility
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2149
- **Severity:** Critical
- **Data needed:** RHS household-income deduction eligibility documentation — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once RHS household-income deduction eligibility documentation is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G091 — O-RHS-02759 [O-RHS]
- **Q:** Were all additional annual household income requirements met?
- **Defect condition:** Adjusted annual income included a dependent deduction without documenting the deduction is eligible
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2162
- **Severity:** Critical
- **Data needed:** RHS household-income deduction eligibility documentation — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once RHS household-income deduction eligibility documentation is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G092 — O-RHS-02761 [O-RHS]
- **Q:** Were all additional annual household income requirements met?
- **Defect condition:** Adjusted annual income included an elderly household deduction without documenting eligibility
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2169
- **Severity:** Critical
- **Data needed:** RHS household-income deduction eligibility documentation — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once RHS household-income deduction eligibility documentation is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G093 — O-RHS-02763 [O-RHS]
- **Q:** Were all additional annual household income requirements met?
- **Defect condition:** Adjusted annual income included elderly medical expenses deduction without documenting eligibility
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2170
- **Severity:** Critical
- **Data needed:** RHS household-income deduction eligibility documentation — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once RHS household-income deduction eligibility documentation is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G094 — O-RHS-02762 [O-RHS]
- **Q:** Were all additional annual household income requirements met?
- **Defect condition:** Borrower is ineligible for household member with disabilities deduction
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2232
- **Severity:** Critical
- **Data needed:** RHS household-income deduction eligibility documentation — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once RHS household-income deduction eligibility documentation is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G095 — O-RHS-02779 [O-RHS]
- **Q:** Were all additional annual household income requirements met?
- **Defect condition:** Income from trust funds for household annual income calculation purposes not documented & verified
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2533
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G096 — O-RHS-02781 [O-RHS]
- **Q:** Were all additional annual household income requirements met?
- **Defect condition:** Lump sum receipts, such as inheritance, capital gains or lottery wins not documented & verified
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2332
- **Severity:** Critical
- **Data needed:** capital-gains tax-return schedule (Schedule D) history — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once capital-gains tax-return schedule (Schedule D) history is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G098 — O-RHS-02778 [O-RHS]
- **Q:** Were all additional annual household income requirements met?
- **Defect condition:** Verification of real property equity/capital invest not documented for inclusion in annual income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2412
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G099 — O-FNM-00435 [O-FNM]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** A copy of the mortgage credit certificate was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2357
- **Severity:** Critical
- **Data needed:** Mortgage Credit Certificate (MCC) document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once Mortgage Credit Certificate (MCC) document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.3-06 — Mortgage Diﬀerential Payments Income (PDF p.343)
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **SME:** [ ] agree [ ] correct: ______

### G100 — O-RHS-50546 [O-RHS]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** Appropriate docs for other non-employed income w/in last 12 mos not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2371
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** 1099 (or Form 4137 tip-income) tax form — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once 1099 (or Form 4137 tip-income) tax form is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G102 — O-FRD-03092 [O-FRD]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** Employed by a family member/interested party & the most recent years tax returns were not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2369
- **Severity:** Critical
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G103 — O-FRD-58602 [O-FRD]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** Entire amt non-taxable income used without addtl docs &/or grossed up income calculated incorrectly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2519
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G104 — O-FRD-58285 [O-FRD]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** Family/int party employed & tax return/transcript don't support current income & prior year not used
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2370
- **Severity:** Major
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G105 — O-FRD-50442 [O-FRD]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** Foreign income used without obtaining US federal income tax returns
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2208
- **Severity:** Critical
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G106 — O-FNM-55666 [O-FNM]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** Foreign income was used without being translated to U.S. dollars
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2210
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **Guide candidate:** A3-3-03 — Other Servicing Arrangements (PDF p.131)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G107 — O-RHS-50547 [O-RHS]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** Household assets to annual income calculated incorrectly for cash value greater or less than $5,000
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2111
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G108 — O-FNM-00436 [O-FNM]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** In a loan relying on capital gains, file does not contain signed tax returns for the past two years
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2145
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.4-05 — Capital Gains Income (PDF p.357)
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **SME:** [ ] agree [ ] correct: ______

### G109 — O-RHS-50548 [O-RHS]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** Income amt of assets sold for less than value w/in the last 2 yrs incorrect
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2325
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G110 — O-FRD-50009 [O-FRD]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** Interest/dividend-Tax rtrns verifying 2yr receipt & sufficient assets to support income not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2166
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G111 — O-FNM-02572 [O-FNM]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** K-1 income shows < 25% ownership and documentation demonstrating the income may be used not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2469
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** K-1 / Form 1065 / 1120S business tax-return schedule — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once K-1 / Form 1065 / 1120S business tax-return schedule is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **Guide candidate:** B3-3.4-19 — Schedule K-1 Income <25% Ownership (PDF p.378)
- **SME:** [ ] agree [ ] correct: ______

### G112 — O-FNM-51012 [O-FNM]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** LTV over 70% or 80% if owner is at least 62 years old where employment related assets used as income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2182
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** employment-related-asset / lump-sum-distribution qualifying-income documentation — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once employment-related-asset / lump-sum-distribution qualifying-income documentation is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.4-06 — Employment Related Assets as Qualifying Income (PDF p.358)
- **Guide candidate:** B3-3.2-02 — Standards for Employment-Related Income (PDF p.330)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **SME:** [ ] agree [ ] correct: ______

### G113 — O-FNM-54028 [O-FNM]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** Monthly amt of employment related assets as income calculated incorrectly &/or req's for use not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2183
- **Severity:** Critical
- **Data needed:** employment-related-asset / lump-sum-distribution qualifying-income documentation — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once employment-related-asset / lump-sum-distribution qualifying-income documentation is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.4-06 — Employment Related Assets as Qualifying Income (PDF p.358)
- **Guide candidate:** B3-3.2-02 — Standards for Employment-Related Income (PDF p.330)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **SME:** [ ] agree [ ] correct: ______

### G114 — O-RHS-02754 [O-RHS]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** Mortgage credit certificate used and written documentation verifying the payments was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2360
- **Severity:** Critical
- **Data needed:** Mortgage Credit Certificate (MCC) document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once Mortgage Credit Certificate (MCC) document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G115 — O-FNM-00438 [O-FNM]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** Non-occupant borrower income used in manual UW with an unacceptable LTV and is a NOO residence
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2336
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **SME:** [ ] agree [ ] correct: ______

### G116 — O-RHS-54270 [O-RHS]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** Non-taxable income was not grossed up 25% for repayment income as needed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2227
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G118 — O-RHS-50012 [O-RHS]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** Notes Receivable-Existence of the note & consistent pymts for last 12 mos not verified & documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2377
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G119 — O-FRD-00408 [O-FRD]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** Public assistance-Documentation verifying amount, frequency and duration was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2415
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G120 — O-FNM-00437 [O-FNM]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** Royalty-Tax returns, contract/alt documentation and 12 mo receipt with 3 yr continuance not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2458
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** Schedule E rental-income tax-return page — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once Schedule E rental-income tax-return page is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.1-02 — Tax Return and Transcript Documentation Requirements (PDF p.320)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **SME:** [ ] agree [ ] correct: ______

### G121 — O-RHS-02755 [O-RHS]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** Section 8 used to reduce PITI without documenting the benefit is paid directly to the servicer
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2480
- **Severity:** Critical
- **Data needed:** Section 8 / Housing Choice Voucher award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once Section 8 / Housing Choice Voucher award letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G123 — O-FRD-50004 [O-FRD]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** Tax returns for the past 2 yrs & evidence of sufficient assets to support capital gains not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2144
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G124 — O-FRD-50443 [O-FRD]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** Tax-exempt income was used without meeting all documentation/requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2517
- **Severity:** Critical
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G125 — O-FRD-00410 [O-FRD]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** Temporary leave income used and the income does not meet Freddie Mac's requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2523
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G126 — O-FNM-55665 [O-FNM]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** The file did not contain 2 years tax returns including foreign income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2209
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **Guide candidate:** B3-3.6-01 — General Information on Analyzing Individual Tax Returns (PDF p.390)
- **SME:** [ ] agree [ ] correct: ______

### G127 — O-RHS-51844 [O-RHS]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** The income has a sharp increase/decrease of 20% or more that was not supported and logical
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2276
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G128 — O-RHS-50013 [O-RHS]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** Unreimbursed employee/business expenses deducted from annual income not deducted from repymt income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2549
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G129 — O-FNM-55677 [O-FNM]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** Virtual currency was considered as an asset based income type
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2275
- **Severity:** Critical
- **Data needed:** cryptocurrency/virtual-currency income-conversion documentation (same gap flagged in the asset-verification triage) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once cryptocurrency/virtual-currency income-conversion documentation (same gap flagged in the asset-verification triage) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **Guide candidate:** B3-4.1-04 — Virtual Currency (PDF p.429)
- **Guide candidate:** A3-3-03 — Other Servicing Arrangements (PDF p.131)
- **SME:** [ ] agree [ ] correct: ______

### G130 — O-FRD-57800 [O-FRD]
- **Q:** Were all additional rental income requirements met?
- **Defect condition:** 2 mos rent or 1st mo & security dep not cashed/deposited, 3rd party xfer, or in escrow as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2103
- **Severity:** Major
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G131 — O-FHA-58784 [O-FHA]
- **Q:** Were all additional rental income requirements met?
- **Defect condition:** A 12 month avg of boarder rental income not used where documented for only 9 of the last 12 months
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2368
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G132 — O-FHA-58783 [O-FHA]
- **Q:** Were all additional rental income requirements met?
- **Defect condition:** Boarder rental income used as effective income exceeds 30% of the effective income used to qualify
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2337
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G133 — O-FRD-57502 [O-FRD]
- **Q:** Were all additional rental income requirements met?
- **Defect condition:** Existing lease not current & fully executed for a subject property refinance or non-subject property
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2422
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G134 — O-FRD-58044 [O-FRD]
- **Q:** Were all additional rental income requirements met?
- **Defect condition:** Investment purchase-multiple borr's live in same property w/out evidence at least 1 owns/rents
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2301
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G135 — O-FRD-51122 [O-FRD]
- **Q:** Were all additional rental income requirements met?
- **Defect condition:** Lease used in lieu of a tax return for rental income w/out evidence the property was out of service
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2438
- **Severity:** Critical
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G136 — O-FRD-03173 [O-FRD]
- **Q:** Were all additional rental income requirements met?
- **Defect condition:** Long-term rental income did not meet the Option 1 criteria of the stability and continuance req's
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2382
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G137 — O-FRD-57503 [O-FRD]
- **Q:** Were all additional rental income requirements met?
- **Defect condition:** New lease 1st rental pymt date is due after the 1st mtg pymt date in a refi or non-subject property
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2423
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G139 — O-FRD-51123 [O-FRD]
- **Q:** Were all additional rental income requirements met?
- **Defect condition:** Primary converted to a rental & rental income added to monthly income and not just to offset PITI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2409
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G140 — O-FRD-58045 [O-FRD]
- **Q:** Were all additional rental income requirements met?
- **Defect condition:** Qualifying rental income based on the number of days in service as per Sch E without meeting req's
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2160
- **Severity:** Critical
- **Data needed:** Schedule E rental-income tax-return page — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once Schedule E rental-income tax-return page is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G141 — O-FRD-50444 [O-FRD]
- **Q:** Were all additional rental income requirements met?
- **Defect condition:** Rental income not calculated correctly &/or negative rent not added to the borrower's liabilities
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2428
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G142 — O-FRD-03174 [O-FRD]
- **Q:** Were all additional rental income requirements met?
- **Defect condition:** Short-term rental income did not meet the Option 2 criteria of the stability and continuance req's
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2383
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G143 — O-RHS-50557 [O-RHS]
- **Q:** Were all additional self-employment income requirements met?
- **Defect condition:** Business debt excluded from DTI - no evidence business paid for last 12 mos
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2134
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G145 — O-RHS-02774 [O-RHS]
- **Q:** Were all additional self-employment income requirements met?
- **Defect condition:** The file did not document that the business is operational within 30 days of the loan closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2565
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G146 — O-RHS-50556 [O-RHS]
- **Q:** Were all additional self-employment income requirements met?
- **Defect condition:** The self employment income calculated incorrectly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2493
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G147 — O-RHS-50545 [O-RHS]
- **Q:** Were all additional self-employment income requirements met?
- **Defect condition:** Written analysis of income not in the file for self employment
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2148
- **Severity:** Major
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G148 — O-RHS-56135 [O-RHS]
- **Q:** Were all additional self-employment income requirements met?
- **Defect condition:** “Business Owner” or “Self-Employed” selected in GUS & the borr's ownership interest is less than 25%
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2322
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** GUS findings / USDA residual-income worksheet field — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once GUS findings / USDA residual-income worksheet field is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G149 — O-RHS-02742 [O-RHS]
- **Q:** Were all alimony, child support and/or maintenance income requirements met?
- **Defect condition:** Alimony/child support/maintenance missing legal docs &/or history and continuance req's not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2088
- **Severity:** Critical
- **Data needed:** alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once alimony/child-support legal decree or written agreement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G150 — O-RHS-56136 [O-RHS]
- **Q:** Were all alimony, child support and/or maintenance income requirements met?
- **Defect condition:** An average of child support/maintenance was not used where the payments are inconsistent
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2288
- **Severity:** Critical
- **Data needed:** alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once alimony/child-support legal decree or written agreement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G152 — O-FHA-56215 [O-FHA]
- **Q:** Were all alimony, child support, and maintenance income requirements met?
- **Defect condition:** 2 yr avg not used for inconsistent court ordered alimony/child supp/maintenance pymts in last 3 mos
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2158
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once alimony/child-support legal decree or written agreement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G153 — O-FHA-56214 [O-FHA]
- **Q:** Were all alimony, child support, and maintenance income requirements met?
- **Defect condition:** 2 yr avg not used for inconsistent voluntary alimony, child support, maintenance pymts in last 6 mos
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2572
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once alimony/child-support legal decree or written agreement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G154 — O-FHA-50023 [O-FHA]
- **Q:** Were all alimony, child support, and maintenance income requirements met?
- **Defect condition:** Divorce decree, separation agreement, court order/voluntary pmt agreement with receipt not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2089
- **Severity:** Critical
- **Data needed:** alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once alimony/child-support legal decree or written agreement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G156 — O-FNM-54027 [O-FNM]
- **Q:** Were all alimony, child support, maintenance, or other nontaxable income requirements met?
- **Defect condition:** Alimony, child support, maintenance not on 1003 & not requested by borrower  to use as income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2333
- **Severity:** Critical
- **Data needed:** alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once alimony/child-support legal decree or written agreement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.4-02 — Alimony, Child Support, Equalization Payments, or Separate Maintenance (PDF p.352)
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **SME:** [ ] agree [ ] correct: ______

### G157 — O-FNM-00421 [O-FNM]
- **Q:** Were all alimony, child support, maintenance, or other nontaxable income requirements met?
- **Defect condition:** Documentation verifying alimony/child support income will continue for at least 3 years not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2087
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once alimony/child-support legal decree or written agreement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.4-02 — Alimony, Child Support, Equalization Payments, or Separate Maintenance (PDF p.352)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **SME:** [ ] agree [ ] correct: ______

### G158 — Income Breakdown [O-FNM]
- **Q:** Were all alimony, child support, maintenance, or other nontaxable income requirements met?
- **Defect condition:** Income submitted to AUS is not accurate - broken out and/or categorized correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2239
- **Severity:** Critical
- **Data needed:** a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute
- **Rationale:** Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- **Guide candidate:** B3-3.4-02 — Alimony, Child Support, Equalization Payments, or Separate Maintenance (PDF p.352)
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **Guide candidate:** A3-3-03 — Other Servicing Arrangements (PDF p.131)
- **SME:** [ ] agree [ ] correct: ______

### G159 — O-FNM-55661 [O-FNM]
- **Q:** Were all alimony, child support, maintenance, or other nontaxable income requirements met?
- **Defect condition:** Minimum of 6 mos alimony/child support/maintenance full & timely pay history not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2091
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once alimony/child-support legal decree or written agreement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.4-02 — Alimony, Child Support, Equalization Payments, or Separate Maintenance (PDF p.352)
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **Guide candidate:** A3-3-03 — Other Servicing Arrangements (PDF p.131)
- **SME:** [ ] agree [ ] correct: ______

### G161 — O-FNM-58797 [O-FNM]
- **Q:** Were all alimony, child support, maintenance, or other nontaxable income requirements met?
- **Defect condition:** Other types of nontaxable income were considered without documents to verify nontaxable status
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2375
- **Severity:** Critical
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.4-02 — Alimony, Child Support, Equalization Payments, or Separate Maintenance (PDF p.352)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **SME:** [ ] agree [ ] correct: ______

### G162 — O-FNM-57443 [O-FNM]
- **Q:** Were all alimony, child support, maintenance, or other nontaxable income requirements met?
- **Defect condition:** The "grossed up" calculation for child support income was not calculated correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2226
- **Severity:** Critical
- **Data needed:** alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once alimony/child-support legal decree or written agreement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.4-02 — Alimony, Child Support, Equalization Payments, or Separate Maintenance (PDF p.352)
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **Guide candidate:** A3-3-03 — Other Servicing Arrangements (PDF p.131)
- **SME:** [ ] agree [ ] correct: ______

### G163 — O-FNM-58800 [O-FNM]
- **Q:** Were all alimony, child support, maintenance, or other nontaxable income requirements met?
- **Defect condition:** The "grossed up" calculation of other nontaxable income was not calculated correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2389
- **Severity:** Critical
- **Data needed:** alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once alimony/child-support legal decree or written agreement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.4-02 — Alimony, Child Support, Equalization Payments, or Separate Maintenance (PDF p.352)
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **Guide candidate:** A3-3-03 — Other Servicing Arrangements (PDF p.131)
- **SME:** [ ] agree [ ] correct: ______

### G165 — O-RHS-51017 [O-RHS]
- **Q:** Were all annual household income requirements met?
- **Defect condition:** Net family assets that exceed $50,000 were not considered in the annual income calculation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2366
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G166 — O-RHS-50549 [O-RHS]
- **Q:** Were all annual household income requirements met?
- **Defect condition:** No evidence employment gaps were analyzed determining income is stable and dependable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2181
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G169 — O-RHS-02764 [O-RHS]
- **Q:** Were all annual household income requirements met?
- **Defect condition:** The applicant's adjusted annual household income exceeds applicable moderate income program limit
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2078
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G170 — O-RHS-51845 [O-RHS]
- **Q:** Were all annual household income requirements met?
- **Defect condition:** Time in college, tech school or career HS cert used toward annual repayment w/out a certificate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2167
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G171 — O-RHS-02776 [O-RHS]
- **Q:** Were all annual household income requirements met?
- **Defect condition:** Verification of investment accounts used as income assets was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2270
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G172 — O-FNM-51832 [O-FNM]
- **Q:** Were all anticipated income requirements met?
- **Defect condition:** Anticipated income-start date greater than 30 days prior to or greater than 90 days after Note date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2110
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** employment offer/contract letter (anticipated/new-employment income) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once employment offer/contract letter (anticipated/new-employment income) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.1-01 — General Income Information (PDF p.318)
- **Guide candidate:** B3-3.1-03 — Income Calculator (PDF p.323)
- **SME:** [ ] agree [ ] correct: ______

### G173 — O-FNM-51831 [O-FNM]
- **Q:** Were all anticipated income requirements met?
- **Defect condition:** Anticipated income-w/out new paystub & loan feature, financial resource & reserve req's not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2109
- **Severity:** Critical
- **Data needed:** employment offer/contract letter (anticipated/new-employment income) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once employment offer/contract letter (anticipated/new-employment income) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B5-6-03 — HomeReady Mortgage Loan Pricing, Mortgage Insurance, and Special Feature Codes (PDF p.818)
- **Guide candidate:** B5-7-02 — High LTV Reﬁnance Underwriting, Documentation, and Collateral Requirements for the New Loan (PDF p.824)
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **SME:** [ ] agree [ ] correct: ______

### G174 — O-FNM-51830 [O-FNM]
- **Q:** Were all anticipated income requirements met?
- **Defect condition:** Employment start date is within 90 days after Note date missing an employment offer/contract
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2108
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** employment offer/contract letter (anticipated/new-employment income) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once employment offer/contract letter (anticipated/new-employment income) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.2-02 — Standards for Employment-Related Income (PDF p.330)
- **Guide candidate:** B3-3.3-07 — Restricted Stock Units and Restricted Stock Employment Income (PDF p.344)
- **SME:** [ ] agree [ ] correct: ______

### G177 — O-FNM-57264 [O-FNM]
- **Q:** Were all anticipated income requirements met?
- **Defect condition:** The offer or contract for employment is by a family member or interested party to the transaction
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2294
- **Severity:** Critical
- **Data needed:** employment offer/contract letter (anticipated/new-employment income) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once employment offer/contract letter (anticipated/new-employment income) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.2-02 — Standards for Employment-Related Income (PDF p.330)
- **Guide candidate:** B3-3.3-07 — Restricted Stock Units and Restricted Stock Employment Income (PDF p.344)
- **SME:** [ ] agree [ ] correct: ______

### G178 — O-FRD-50446 [O-FRD]
- **Q:** Were all asset used as income qualification requirements met?
- **Defect condition:** All req's not met relying on retirement assets as a basis for qualification
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2450
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G179 — O-FRD-00417 [O-FRD]
- **Q:** Were all asset used as income qualification requirements met?
- **Defect condition:** Assets from sale of business proceeds & no documentation borr was sole owner &/or doc req's not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2464
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G181 — O-FRD-55524 [O-FRD]
- **Q:** Were all asset used as income qualification requirements met?
- **Defect condition:** Cryptocurrency was considered as an asset based income type
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2274
- **Severity:** Critical
- **Data needed:** cryptocurrency/virtual-currency income-conversion documentation (same gap flagged in the asset-verification triage) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once cryptocurrency/virtual-currency income-conversion documentation (same gap flagged in the asset-verification triage) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G182 — O-FRD-50445 [O-FRD]
- **Q:** Were all asset used as income qualification requirements met?
- **Defect condition:** Eligibility requirements for asset qualification not met &/or the DTI calculation was incorrect
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2113
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G183 — O-FRD-51642 [O-FRD]
- **Q:** Were all asset used as income qualification requirements met?
- **Defect condition:** Eligible assets used as a basis for repayment of obligations not divided by 240 for the DTI ratio
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2114
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G184 — Income Breakdown [O-FRD]
- **Q:** Were all asset used as income qualification requirements met?
- **Defect condition:** Income submitted to AUS is not accurate - broken out and/or categorized correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2251
- **Severity:** Critical
- **Data needed:** a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute
- **Rationale:** Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- **SME:** [ ] agree [ ] correct: ______

### G185 — O-FRD-55525 [O-FRD]
- **Q:** Were all asset used as income qualification requirements met?
- **Defect condition:** Income that is paid to the borrower in cryptocurrency was used for qualification
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2159
- **Severity:** Critical
- **Data needed:** cryptocurrency/virtual-currency income-conversion documentation (same gap flagged in the asset-verification triage) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once cryptocurrency/virtual-currency income-conversion documentation (same gap flagged in the asset-verification triage) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G187 — O-FRD-00416 [O-FRD]
- **Q:** Were all asset used as income qualification requirements met?
- **Defect condition:** Verification of access to lump-sum distribution & assets are not a source of income not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2331
- **Severity:** Critical
- **Data needed:** retirement-account statement (401(k)/IRA/Keogh/pension) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once retirement-account statement (401(k)/IRA/Keogh/pension) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G188 — O-FHA-02287 [O-FHA]
- **Q:** Were all automobile allowance requirements met?
- **Defect condition:** Auto allowance received from the employer for the previous two years was not verified and documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2120
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** automobile-allowance employer letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once automobile-allowance employer letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G189 — O-FNM-55662 [O-FNM]
- **Q:** Were all automobile allowance requirements met?
- **Defect condition:** Auto allowance was considered stable income & full amt of allowance was not added to monthly income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2124
- **Severity:** Critical
- **Data needed:** automobile-allowance employer letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once automobile-allowance employer letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.1-01 — General Income Information (PDF p.318)
- **Guide candidate:** B3-3.1-03 — Income Calculator (PDF p.323)
- **SME:** [ ] agree [ ] correct: ______

### G190 — O-FNM-00342 [O-FNM]
- **Q:** Were all automobile allowance requirements met?
- **Defect condition:** Documentation verifying borrower has received auto allowance for at least 2 yrs was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2121
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** automobile-allowance employer letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once automobile-allowance employer letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B2-2-01 — General Borrower Eligibility Requirements (PDF p.241)
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **Guide candidate:** B2-2-03 — Multiple Financed Properties for the Same Borrower (PDF p.244)
- **SME:** [ ] agree [ ] correct: ______

### G191 — O-FNM-55663 [O-FNM]
- **Q:** Were all automobile allowance requirements met?
- **Defect condition:** Full lease/debt pymt not added to the debt obligations as applicable for an automobile allowance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2123
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-6-05 — Monthly Debt Obligations (PDF p.522)
- **Guide candidate:** A2-1-01 — Contractual Obligations for Sellers/Servicers (PDF p.21)
- **Guide candidate:** B3-3.3-04 — Housing (Parsonage) and Automobile Allowances (PDF p.341)
- **SME:** [ ] agree [ ] correct: ______

### G192 — Income Breakdown [O-FNM]
- **Q:** Were all automobile allowance requirements met?
- **Defect condition:** Income submitted to AUS is not accurate - broken out and/or categorized correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2237
- **Severity:** Critical
- **Data needed:** a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute
- **Rationale:** Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **Guide candidate:** B2-1.3-03 — Cash-Out Reﬁnance Transactions (PDF p.197)
- **SME:** [ ] agree [ ] correct: ______

### G195 — O-FNM-00339 [O-FNM]
- **Q:** Were all base pay (salary and hourly), bonus, tip, and overtime income requirements met?
- **Defect condition:** Documentation verifying the applicant has received tip income for the previous 2 yrs not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2529
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **Guide candidate:** B3-3.3-02 — Bonus, Commission, Overtime, and Tip Income (PDF p.335)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.3-01 — Base Income (PDF p.333)
- **SME:** [ ] agree [ ] correct: ______

### G196 — O-FNM-00346 [O-FNM]
- **Q:** Were all base pay (salary and hourly), bonus, tip, and overtime income requirements met?
- **Defect condition:** File does not contain a completed VOE or the most recent paystub & two years W-2s or as per DU
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2125
- **Severity:** Critical
- **Data needed:** W-2 form(s) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once W-2 form(s) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.3-02 — Bonus, Commission, Overtime, and Tip Income (PDF p.335)
- **Guide candidate:** B3-3.3-01 — Base Income (PDF p.333)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G197 — O-FNM-00333 [O-FNM]
- **Q:** Were all base pay (salary and hourly), bonus, tip, and overtime income requirements met?
- **Defect condition:** Income used did not have 2 yr history & no comp factors given to offset the shorter income history
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2323
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **Guide candidate:** B3-3.3-02 — Bonus, Commission, Overtime, and Tip Income (PDF p.335)
- **Guide candidate:** B3-3.3-01 — Base Income (PDF p.333)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G199 — O-FNM-00338 [O-FNM]
- **Q:** Were all base pay (salary and hourly), bonus, tip, and overtime income requirements met?
- **Defect condition:** Verification that the OT/bonus income has been received for the last two years was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2391
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **Guide candidate:** B3-3.3-02 — Bonus, Commission, Overtime, and Tip Income (PDF p.335)
- **Guide candidate:** B3-3.3-01 — Base Income (PDF p.333)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G200 — O-FNM-57320 [O-FNM]
- **Q:** Were all business income requirements met?
- **Defect condition:** 1 yr business tax returns used where business existence or at least 25% ownership is less than 5 yrs
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2380
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.4-19 — Schedule K-1 Income <25% Ownership (PDF p.378)
- **Guide candidate:** B3-3.6-01 — General Information on Analyzing Individual Tax Returns (PDF p.390)
- **SME:** [ ] agree [ ] correct: ______

### G201 — O-FNM-00379 [O-FNM]
- **Q:** Were all business income requirements met?
- **Defect condition:** Most recent 2yrs signed bus. tax returns, including all schedules/tax transcripts not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2140
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.6-01 — General Information on Analyzing Individual Tax Returns (PDF p.390)
- **Guide candidate:** B3-3.1-01 — General Income Information (PDF p.318)
- **SME:** [ ] agree [ ] correct: ______

### G203 — O-FNM-00386 [O-FNM]
- **Q:** Were all business income requirements met?
- **Defect condition:** Underwriter did not provide a written analysis of the applicant's business income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2136
- **Severity:** Critical
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.1-01 — General Income Information (PDF p.318)
- **Guide candidate:** B3-3.1-03 — Income Calculator (PDF p.323)
- **SME:** [ ] agree [ ] correct: ______

### G206 — O-FHA-02282 [O-FHA]
- **Q:** Were all commission income requirements met?
- **Defect condition:** Verification that commission income has been received for 1 yr and will continue was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2151
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G207 — O-FHA-02296 [O-FHA]
- **Q:** Were all disability income requirements met?
- **Defect condition:** Borrower’s receipt of benefits from the disability insurance provider was not verified & documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2164
- **Severity:** Critical
- **Data needed:** disability-benefits payer statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once disability-benefits payer statement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G208 — O-FNM-00423 [O-FNM]
- **Q:** Were all disability income requirements met?
- **Defect condition:** Missing long term disability eligibility confirmation, amount, frequency & end date or as per DU
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2329
- **Severity:** Critical
- **Data needed:** disability-benefits payer statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once disability-benefits payer statement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.4-09 — Long-term Disability Income (PDF p.364)
- **Guide candidate:** A2-3.2-02 — Enforcement Relief for Breaches of Certain Representations and Warranties Related to Underwriting and Eligibility (PDF p.65)
- **Guide candidate:** A4-1-01 — Maintaining Seller/Servicer Eligibility (PDF p.151)
- **SME:** [ ] agree [ ] correct: ______

### G210 — O-FHA-57251 [O-FHA]
- **Q:** Were all disability income requirements met?
- **Defect condition:** VA disability not documented with VA's last benefits letter & acceptable evidence of receipt
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2552
- **Severity:** Critical
- **Data needed:** benefits/award letter (SSA, VA, pension, or disability payer) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once benefits/award letter (SSA, VA, pension, or disability payer) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G212 — O-FHA-57250 [O-FHA]
- **Q:** Were all employer housing subsidy income requirements met?
- **Defect condition:** The employer housing subsidy was used to offset the mortgage payment
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2175
- **Severity:** Critical
- **Data needed:** employer housing-subsidy / parsonage agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once employer housing-subsidy / parsonage agreement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G213 — O-FHA-02280 [O-FHA]
- **Q:** Were all employer housing subsidy income requirements met?
- **Defect condition:** The existence and the amount of the employer housing subsidy was not verified and documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2174
- **Severity:** Critical
- **Data needed:** employer housing-subsidy / parsonage agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once employer housing-subsidy / parsonage agreement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G214 — O-FNM-00336 [O-FNM]
- **Q:** Were all employment documentation requirements met?
- **Defect condition:** 3rd party employment verification was used but documentation does not meet Fannie Mae's requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2525
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** A2-5-01 — Fannie Mae Trade Name and Trademarks (PDF p.102)
- **Guide candidate:** A3-1-01 — Fannie Mae’s Technology Products (PDF p.106)
- **SME:** [ ] agree [ ] correct: ______

### G215 — EmploymentGaps [O-FNM]
- **Q:** Were all employment documentation requirements met?
- **Defect condition:** Gaps in employment were not addressed as required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2271
- **Severity:** Critical
- **Machine checks:** presence of an employment-gap explanation
- **Data needed:** an employment-gap-explanation document/field — not currently captured
- **Rationale:** Recurs under 2 AMQ question categories (FNM/VA); pure presence check, same pattern as many other 'X not addressed/documented' rows in this block.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-2-04 — DU Documentation Requirements (PDF p.305)
- **Guide candidate:** B3-3.1-02 — Tax Return and Transcript Documentation Requirements (PDF p.320)
- **SME:** [ ] agree [ ] correct: ______

### G217 — O-FNM-00335 [O-FNM]
- **Q:** Were all employment documentation requirements met?
- **Defect condition:** Paystub not within 30 days &/or did not have YTD earnings or sufficient pay info to calculate income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2401
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** paystub — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once paystub is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.2-02 — Standards for Employment-Related Income (PDF p.330)
- **Guide candidate:** B3-3.3-07 — Restricted Stock Units and Restricted Stock Employment Income (PDF p.344)
- **SME:** [ ] agree [ ] correct: ______

### G218 — O-FNM-52820 [O-FNM]
- **Q:** Were all employment documentation requirements met?
- **Defect condition:** Paystubs and W2's source was not a third party ex: HR, payroll, personnel dept, payroll vendor etc
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2402
- **Severity:** Critical
- **Data needed:** W-2 form(s) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once W-2 form(s) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** A3-3-01 — Outsourcing of Mortgage Processing and Third-Party Originations (PDF p.123)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** C1-2-03 — Ownership of Mortgage Loans Prior to Purchase or Securitization and Third-Party Security Interests (PDF p.951)
- **SME:** [ ] agree [ ] correct: ______

### G219 — O-FNM-50249 [O-FNM]
- **Q:** Were all employment documentation requirements met?
- **Defect condition:** The W2's obtained did not cover the number of years that were required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2295
- **Severity:** Critical
- **Data needed:** W-2 form(s) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once W-2 form(s) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-2-04 — DU Documentation Requirements (PDF p.305)
- **Guide candidate:** B3-3.1-02 — Tax Return and Transcript Documentation Requirements (PDF p.320)
- **SME:** [ ] agree [ ] correct: ______

### G220 — O-FNM-00334 [O-FNM]
- **Q:** Were all employment documentation requirements met?
- **Defect condition:** The employer did not complete all required fields on the standard VOE form 1005
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2287
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B1-1-02 — Blanket Authorization Form (PDF p.170)
- **Guide candidate:** B3-2-04 — DU Documentation Requirements (PDF p.305)
- **SME:** [ ] agree [ ] correct: ______

### G221 — IncomeWork [O-FNM]
- **Q:** Were all employment documentation requirements met?
- **Defect condition:** The income calculation worksheet is not located in the file or is incomplete/inaccurate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2283
- **Severity:** Major
- **Machine checks:** presence of an income-calculation worksheet
- **Stays human:** 'income discrepancies were not explained' clause (appended, open-ended)
- **Data needed:** income-calculation-worksheet document type — not in the corpus
- **Rationale:** Recurs identically under 5 different AMQ question categories. Presence half is crisp once the worksheet doc type is modeled; the appended discrepancy-explanation clause stays partly human, same pattern as asset-verification's G007 (crisp presence + appended open catch-all kept YELLOW, not RED).
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.2-02 — Standards for Employment-Related Income (PDF p.330)
- **Guide candidate:** B3-3.3-07 — Restricted Stock Units and Restricted Stock Employment Income (PDF p.344)
- **SME:** [ ] agree [ ] correct: ______

### G222 — RentalCalcDoc [O-FNM]
- **Q:** Were all employment documentation requirements met?
- **Defect condition:** The net rental income/loss worksheet was not utilized when applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2425
- **Severity:** Major
- **Machine checks:** presence of a net-rental-income/loss worksheet
- **Data needed:** net-rental-income worksheet document type — not in the corpus
- **Rationale:** Single AMQ row (O-FNM); crisp presence check once the worksheet doc type is modeled; no rental-income document of any kind exists in the 5-loan corpus today.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.2-02 — Standards for Employment-Related Income (PDF p.330)
- **Guide candidate:** B3-3.3-07 — Restricted Stock Units and Restricted Stock Employment Income (PDF p.344)
- **SME:** [ ] agree [ ] correct: ______

### G223 — O-FNM-52819 [O-FNM]
- **Q:** Were all employment documentation requirements met?
- **Defect condition:** The paystubs and/or W2's were incomplete or were illegible
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2234
- **Severity:** Critical
- **Data needed:** W-2 form(s) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once W-2 form(s) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-2-04 — DU Documentation Requirements (PDF p.305)
- **Guide candidate:** B3-3.1-02 — Tax Return and Transcript Documentation Requirements (PDF p.320)
- **SME:** [ ] agree [ ] correct: ______

### G224 — O-FNM-50250 [O-FNM]
- **Q:** Were all employment documentation requirements met?
- **Defect condition:** The paystubs/W2's did not clearly identify the borrower as the employee
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2133
- **Severity:** Critical
- **Data needed:** W-2 form(s) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once W-2 form(s) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B2-2-01 — General Borrower Eligibility Requirements (PDF p.241)
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **SME:** [ ] agree [ ] correct: ______

### G226 — O-FHA-55588 [O-FHA]
- **Q:** Were all employment income requirements met?
- **Defect condition:** Alternative employment req's not met w/ most recent YTD paystub, 2 years W2s & a completed VVOE
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2098
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** verbal VOE (VVOE) call/database log — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once verbal VOE (VVOE) call/database log is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G227 — O-FHA-51273 [O-FHA]
- **Q:** Were all employment income requirements met?
- **Defect condition:** Data on the electronic reverification of employment was not current w/in 30 days of the verification
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2171
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G228 — O-FHA-02276 [O-FHA]
- **Q:** Were all employment income requirements met?
- **Defect condition:** Direct verification of the borrower's prior 2 years employment history was not obtained as required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2399, 2400
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G229 — O-FNM-50011 [O-FNM]
- **Q:** Were all employment income requirements met?
- **Defect condition:** Employed by a family member/interested party & the most recent years tax returns were not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2194
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.2-02 — Standards for Employment-Related Income (PDF p.330)
- **SME:** [ ] agree [ ] correct: ______

### G230 — O-FNM-50815 [O-FNM]
- **Q:** Were all employment income requirements met?
- **Defect condition:** Income calculation requirements were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2257
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.2-02 — Standards for Employment-Related Income (PDF p.330)
- **Guide candidate:** B3-3.3-07 — Restricted Stock Units and Restricted Stock Employment Income (PDF p.344)
- **SME:** [ ] agree [ ] correct: ______

### G231 — O-FNM-00439 [O-FNM]
- **Q:** Were all employment income requirements met?
- **Defect condition:** Income has a defined expiration date & documentation verifying 3 year continuance was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2281
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.2-02 — Standards for Employment-Related Income (PDF p.330)
- **Guide candidate:** B3-3.3-07 — Restricted Stock Units and Restricted Stock Employment Income (PDF p.344)
- **SME:** [ ] agree [ ] correct: ______

### G232 — DecliningIncDocument [O-FNM]
- **Q:** Were all employment income requirements met?
- **Defect condition:** Income is declining and no explanation has been provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2267
- **Severity:** Critical
- **Machine checks:** multi-year income trend detection (declining year-over-year) + presence of a written explanation
- **Data needed:** multi-year per-income-type income history (not currently extracted beyond a single point-in-time base_monthly_income_1003) + an explanation-document presence fact
- **Rationale:** Recurs under 2 AMQ question categories (general employment income, self-employed). No judgment word in the condition itself ('declining' and 'no explanation provided' are both factual, not evaluative) — blocked purely on missing multi-year income data, not a rule-clarity problem.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.2-02 — Standards for Employment-Related Income (PDF p.330)
- **Guide candidate:** B3-3.3-07 — Restricted Stock Units and Restricted Stock Employment Income (PDF p.344)
- **SME:** [ ] agree [ ] correct: ______

### G233 — Income Breakdown [O-FNM]
- **Q:** Were all employment income requirements met?
- **Defect condition:** Income submitted to AUS is not accurate - broken out and/or categorized correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2236
- **Severity:** Critical
- **Data needed:** a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute
- **Rationale:** Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.2-02 — Standards for Employment-Related Income (PDF p.330)
- **Guide candidate:** B3-3.3-07 — Restricted Stock Units and Restricted Stock Employment Income (PDF p.344)
- **SME:** [ ] agree [ ] correct: ______

### G234 — O-FNM-55678 [O-FNM]
- **Q:** Were all employment income requirements met?
- **Defect condition:** Income that is paid to the borrower in virtual currency was used for qualification
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2569
- **Severity:** Critical
- **Data needed:** cryptocurrency/virtual-currency income-conversion documentation (same gap flagged in the asset-verification triage) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once cryptocurrency/virtual-currency income-conversion documentation (same gap flagged in the asset-verification triage) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.2-02 — Standards for Employment-Related Income (PDF p.330)
- **Guide candidate:** B3-3.3-07 — Restricted Stock Units and Restricted Stock Employment Income (PDF p.344)
- **SME:** [ ] agree [ ] correct: ______

### G235 — O-FHA-55589 [O-FHA]
- **Q:** Were all employment income requirements met?
- **Defect condition:** No direct verification of past employment & OT, bonus &/or tip income used in lieu of only base pay
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2566
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G237 — O-FHA-51274 [O-FHA]
- **Q:** Were all employment income requirements met?
- **Defect condition:** Not same employer for 2 yrs and no direct verification without meeting all req's for 2 yr history
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2163
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** IRS Form 4506-C/8821 tax-transcript consent form — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once IRS Form 4506-C/8821 tax-transcript consent form is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G238 — O-FHA-55591 [O-FHA]
- **Q:** Were all employment income requirements met?
- **Defect condition:** Not the same employer for 2 yrs & 1 or more acceptable documents verifying 2 yr history not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2326
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G240 — VVOE Inactive [O-FHA]
- **Q:** Were all employment income requirements met?
- **Defect condition:** The verbal verification of employment does not show borrower in an active status
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2556
- **Severity:** Critical
- **Data needed:** a VVOE (verbal verification of employment) log/status fact — not currently modeled; the corpus has a written/signed VOE (loan 01) but no distinct verbal-VOE artifact with an active/inactive status field
- **Rationale:** Recurs identically under 7 different AMQ question categories. The written VOE this pilot extracts (employment_start_date_voe) is a different document from a VVOE call/database log; no such artifact exists in any of the 5 synthetic loans.
- **SME:** [ ] agree [ ] correct: ______

### G241 — O-FHA-55587 [O-FHA]
- **Q:** Were all employment income requirements met?
- **Defect condition:** Traditional employment req's not met w/ a paystub & 2 year VOE or direct electronic VOE by a TPV
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2531
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** paystub — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once paystub is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G242 — O-FNM-00352 [O-FNM]
- **Q:** Were all employment income requirements met?
- **Defect condition:** Variable income used, history of receipt, frequency and trending of the amount were not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2553
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.2-02 — Standards for Employment-Related Income (PDF p.330)
- **Guide candidate:** B3-3.3-07 — Restricted Stock Units and Restricted Stock Employment Income (PDF p.344)
- **SME:** [ ] agree [ ] correct: ______

### G243 — 3rdParty [O-FHA]
- **Q:** Were all employment income requirements met?
- **Defect condition:** Vendor for 3rd party VOE was not Equifax/TWN or manual process not followed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2064
- **Severity:** Critical
- **Data needed:** a VOE-vendor-name field (e.g. Equifax/The Work Number) — not currently captured from any document
- **Rationale:** Recurs identically under 5 different AMQ question categories. Crisp presence/identity check once a vendor-name field exists; no such field is in FIELD_SPECS['voe'] today.
- **SME:** [ ] agree [ ] correct: ______

### G244 — O-FHA-02281 [O-FHA]
- **Q:** Were all family-owned business income requirements met?
- **Defect condition:** Documentation verifying that borrower is not an owner in the family-owned business was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2197
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G246 — O-FHA-56944 [O-FHA]
- **Q:** Were all family-owned business income requirements met?
- **Defect condition:** Signed personal tax returns/tax transcripts not obtained where employed by a family-owned business
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2196
- **Severity:** Critical
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G247 — O-FRD-59248 [O-FRD]
- **Q:** Were all fluctuating income requirements met?
- **Defect condition:** At least 12 mos stable income not used when excluding a time period for an event unlikely to recur
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2191
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G248 — O-FRD-58102 [O-FRD]
- **Q:** Were all fluctuating income requirements met?
- **Defect condition:** Fluctuating income calc based on shorter # of mos w/out written justification &/or supporting docs
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2205
- **Severity:** Major
- **Data needed:** multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G249 — O-FRD-52331 [O-FRD]
- **Q:** Were all fluctuating income requirements met?
- **Defect condition:** Fluctuation is > 10% but less than or = 30% without supporting documentation/additional analysis
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2273
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G250 — O-FRD-59245 [O-FRD]
- **Q:** Were all fluctuating income requirements met?
- **Defect condition:** Income considered fluctuating earnings for minor base hour variations of an hour or less per week
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2356
- **Severity:** Major
- **Data needed:** multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G251 — O-FRD-52329 [O-FRD]
- **Q:** Were all fluctuating income requirements met?
- **Defect condition:** Income is fluctuating hourly employment earnings without a minimum employment history 12 months
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2204
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G252 — O-FRD-59246 [O-FRD]
- **Q:** Were all fluctuating income requirements met?
- **Defect condition:** Min req'd hours considered non-fluctuating; additional hours not qualified as fluctuating earnings
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2202
- **Severity:** Critical
- **Data needed:** multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G253 — O-FRD-59247 [O-FRD]
- **Q:** Were all fluctuating income requirements met?
- **Defect condition:** No addtl documentation provided to support using less than avg of recent year(s) & YTD to qualify
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2201
- **Severity:** Critical
- **Data needed:** multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G255 — O-FRD-57266 [O-FRD]
- **Q:** Were all fluctuating income requirements met?
- **Defect condition:** The degree of fluctuation is > 30% with no addt'l analysis/documents for stability & calculation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2272
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G256 — O-FRD-50435 [O-FRD]
- **Q:** Were all fluctuating income requirements met?
- **Defect condition:** The income was calculated incorrectly for the borrower with income that is fluctuating in nature
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2203
- **Severity:** Critical
- **Data needed:** multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G258 — O-VA-00317 [O-VA]
- **Q:** Were all general income and verification requirements met?
- **Defect condition:** File does not contain required documentation of any previous employment needed to document 2 yrs
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2117
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G259 — Income Breakdown [O-VA]
- **Q:** Were all general income and verification requirements met?
- **Defect condition:** Income submitted to AUS is not accurate - broken out and/or categorized correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2255
- **Severity:** Critical
- **Data needed:** a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute
- **Rationale:** Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- **SME:** [ ] agree [ ] correct: ______

### G260 — O-VA-00312 [O-VA]
- **Q:** Were all general income and verification requirements met?
- **Defect condition:** The employment verification service used did not  provide full verification data for all applicants
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2185
- **Severity:** Major
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G261 — O-VA-00316 [O-VA]
- **Q:** Were all general income and verification requirements met?
- **Defect condition:** The file does not contain the required documentation of current employment
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2115
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G262 — O-VA-00311 [O-VA]
- **Q:** Were all general income and verification requirements met?
- **Defect condition:** The file does not contain the required explanation for any gaps in employment
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2116
- **Severity:** Major
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G263 — IncomeWork [O-VA]
- **Q:** Were all general income and verification requirements met?
- **Defect condition:** The income calculation worksheet is not located in the file or is incomplete/inaccurate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2286
- **Severity:** Major
- **Machine checks:** presence of an income-calculation worksheet
- **Stays human:** 'income discrepancies were not explained' clause (appended, open-ended)
- **Data needed:** income-calculation-worksheet document type — not in the corpus
- **Rationale:** Recurs identically under 5 different AMQ question categories. Presence half is crisp once the worksheet doc type is modeled; the appended discrepancy-explanation clause stays partly human, same pattern as asset-verification's G007 (crisp presence + appended open catch-all kept YELLOW, not RED).
- **SME:** [ ] agree [ ] correct: ______

### G264 — O-VA-00653 [O-VA]
- **Q:** Were all general income and verification requirements met?
- **Defect condition:** The residual income was insufficient as per family size and geographic region
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2440
- **Severity:** Critical
- **Data needed:** GUS findings / USDA residual-income worksheet field — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once GUS findings / USDA residual-income worksheet field is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G265 — VVOE Inactive [O-VA]
- **Q:** Were all general income and verification requirements met?
- **Defect condition:** The verbal verification of employment does not show borrower in an active status
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2562
- **Severity:** Critical
- **Data needed:** a VVOE (verbal verification of employment) log/status fact — not currently modeled; the corpus has a written/signed VOE (loan 01) but no distinct verbal-VOE artifact with an active/inactive status field
- **Rationale:** Recurs identically under 7 different AMQ question categories. The written VOE this pilot extracts (employment_start_date_voe) is a different document from a VVOE call/database log; no such artifact exists in any of the 5 synthetic loans.
- **SME:** [ ] agree [ ] correct: ______

### G267 — O-FHA-50673 [O-FHA]
- **Q:** Were all general income requirements met?
- **Defect condition:** Effective income used to qualify was calculated incorrectly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2200
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G268 — O-FHA-50817 [O-FHA]
- **Q:** Were all general income requirements met?
- **Defect condition:** Income calculation requirements were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2256
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G269 — Income Breakdown [O-FHA]
- **Q:** Were all general income requirements met?
- **Defect condition:** Income submitted to AUS is not accurate - broken out and/or categorized correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2235
- **Severity:** Critical
- **Data needed:** a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute
- **Rationale:** Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- **SME:** [ ] agree [ ] correct: ______

### G270 — O-FHA-00602 [O-FHA]
- **Q:** Were all general income requirements met?
- **Defect condition:** Income was included in qualifying that did not meet the definition of effective income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2168
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G272 — IncomeWork [O-FHA]
- **Q:** Were all general income requirements met?
- **Defect condition:** The income calculation worksheet is not located in the file or is incomplete/inaccurate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2282
- **Severity:** Major
- **Machine checks:** presence of an income-calculation worksheet
- **Stays human:** 'income discrepancies were not explained' clause (appended, open-ended)
- **Data needed:** income-calculation-worksheet document type — not in the corpus
- **Rationale:** Recurs identically under 5 different AMQ question categories. Presence half is crisp once the worksheet doc type is modeled; the appended discrepancy-explanation clause stays partly human, same pattern as asset-verification's G007 (crisp presence + appended open catch-all kept YELLOW, not RED).
- **SME:** [ ] agree [ ] correct: ______

### G275 — O-RHS-02719 [O-RHS]
- **Q:** Were all general income verification requirements met?
- **Defect condition:** Full doc did not include 2 yrs W2s or tax trans, 1 mo paystubs & a 10 bus VVOE/other written verif
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2218
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** verbal VOE (VVOE) call/database log — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once verbal VOE (VVOE) call/database log is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G276 — O-RHS-02766 [O-RHS]
- **Q:** Were all general income verification requirements met?
- **Defect condition:** IRS tax transcripts for validation of household income for 2 years was not obtained
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2312
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G277 — Income Breakdown [O-RHS]
- **Q:** Were all general income verification requirements met?
- **Defect condition:** Income submitted to AUS is not accurate - broken out and/or categorized correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2254
- **Severity:** Critical
- **Data needed:** a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute
- **Rationale:** Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- **SME:** [ ] agree [ ] correct: ______

### G278 — O-RHS-50544 [O-RHS]
- **Q:** Were all general income verification requirements met?
- **Defect condition:** Initial or reverification VVOE did not contain all required information
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2567
- **Severity:** Critical
- **Data needed:** verbal VOE (VVOE) call/database log — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once verbal VOE (VVOE) call/database log is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G280 — O-RHS-59377 [O-RHS]
- **Q:** Were all general income verification requirements met?
- **Defect condition:** Specific income types: Annual income, history, continuation, and/or documentation reqs were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2513
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G281 — IncomeWork [O-RHS]
- **Q:** Were all general income verification requirements met?
- **Defect condition:** The income calculation worksheet is not located in the file or is incomplete/inaccurate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2285
- **Severity:** Major
- **Machine checks:** presence of an income-calculation worksheet
- **Stays human:** 'income discrepancies were not explained' clause (appended, open-ended)
- **Data needed:** income-calculation-worksheet document type — not in the corpus
- **Rationale:** Recurs identically under 5 different AMQ question categories. Presence half is crisp once the worksheet doc type is modeled; the appended discrepancy-explanation clause stays partly human, same pattern as asset-verification's G007 (crisp presence + appended open catch-all kept YELLOW, not RED).
- **SME:** [ ] agree [ ] correct: ______

### G282 — VVOE Inactive [O-RHS]
- **Q:** Were all general income verification requirements met?
- **Defect condition:** The verbal verification of employment does not show borrower in an active status
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2561
- **Severity:** Critical
- **Data needed:** a VVOE (verbal verification of employment) log/status fact — not currently modeled; the corpus has a written/signed VOE (loan 01) but no distinct verbal-VOE artifact with an active/inactive status field
- **Rationale:** Recurs identically under 7 different AMQ question categories. The written VOE this pilot extracts (employment_start_date_voe) is a different document from a VVOE call/database log; no such artifact exists in any of the 5 synthetic loans.
- **SME:** [ ] agree [ ] correct: ______

### G283 — O-FNM-50013 [O-FNM]
- **Q:** Were all housing assistance income requirements met?
- **Defect condition:** Housing/Parsonage income receipt for last 12 mths and/or continuance for next 3 years not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2198
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** employer housing-subsidy / parsonage agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once employer housing-subsidy / parsonage agreement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.3-04 — Housing (Parsonage) and Automobile Allowances (PDF p.341)
- **Guide candidate:** B3-3.4-12 — Public Assistance Income (PDF p.368)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G284 — Income Breakdown [O-FNM]
- **Q:** Were all housing assistance income requirements met?
- **Defect condition:** Income submitted to AUS is not accurate - broken out and/or categorized correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2240
- **Severity:** Critical
- **Data needed:** a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute
- **Rationale:** Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- **Guide candidate:** B3-3.4-12 — Public Assistance Income (PDF p.368)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **SME:** [ ] agree [ ] correct: ______

### G286 — O-FNM-57790 [O-FNM]
- **Q:** Were all housing assistance income requirements met?
- **Defect condition:** Section 8 housing voucher income is nontaxable and an adjusted gross income was not developed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2479
- **Severity:** Major
- **Data needed:** Section 8 / Housing Choice Voucher award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once Section 8 / Housing Choice Voucher award letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.4-14 — Section 8 Housing Choice Voucher Homeownership Program Payments (PDF p.370)
- **Guide candidate:** B3-3.4-12 — Public Assistance Income (PDF p.368)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G287 — O-FNM-50012 [O-FNM]
- **Q:** Were all housing assistance income requirements met?
- **Defect condition:** Section 8 vouchers-Voucher from public housing agency stating payment amount & duration not obtained
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2478
- **Severity:** Critical
- **Data needed:** Section 8 / Housing Choice Voucher award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once Section 8 / Housing Choice Voucher award letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.4-12 — Public Assistance Income (PDF p.368)
- **Guide candidate:** B3-3.4-14 — Section 8 Housing Choice Voucher Homeownership Program Payments (PDF p.370)
- **Guide candidate:** B3-3.4-13 — Royalty Payment Income (PDF p.369)
- **SME:** [ ] agree [ ] correct: ______

### G288 — O-FHA-02298 [O-FHA]
- **Q:** Were all housing assistance requirements met?
- **Defect condition:** MCC-Documentation verifying governmental entity subsidizes the mortgage payments was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2359
- **Severity:** Critical
- **Data needed:** Mortgage Credit Certificate (MCC) document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once Mortgage Credit Certificate (MCC) document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G290 — O-FHA-02299 [O-FHA]
- **Q:** Were all housing assistance requirements met?
- **Defect condition:** Section 8 vouchers-Documentation verifying borrower receives Housing Choice subsidies not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2483
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** Section 8 / Housing Choice Voucher award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once Section 8 / Housing Choice Voucher award letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G291 — O-FHA-54823 [O-FHA]
- **Q:** Were all housing assistance requirements met?
- **Defect condition:** The amount of the mortgage credit certificate tax rebate was not documented and verified
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2363
- **Severity:** Critical
- **Data needed:** Mortgage Credit Certificate (MCC) document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once Mortgage Credit Certificate (MCC) document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G292 — O-FHA-54824 [O-FHA]
- **Q:** Were all housing assistance requirements met?
- **Defect condition:** The current mortgage credit certificate subsidy rate was not used to calculate the effective income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2362
- **Severity:** Critical
- **Data needed:** Mortgage Credit Certificate (MCC) document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once Mortgage Credit Certificate (MCC) document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G293 — O-FHA-02300 [O-FHA]
- **Q:** Were all housing assistance requirements met?
- **Defect condition:** The public assistance income received from the government agency was not verified and documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2414
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G294 — O-FRD-50434 [O-FRD]
- **Q:** Were all income calculation requirements met?
- **Defect condition:** Calculation methods for base non-fluctuating employment earnings incorrect
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2372
- **Severity:** Critical
- **Data needed:** multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G295 — O-FRD-50816 [O-FRD]
- **Q:** Were all income calculation requirements met?
- **Defect condition:** Income calculation requirements were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2260
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G296 — Income Breakdown [O-FRD]
- **Q:** Were all income calculation requirements met?
- **Defect condition:** Income submitted to AUS is not accurate - broken out and/or categorized correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2246
- **Severity:** Critical
- **Data needed:** a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute
- **Rationale:** Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- **SME:** [ ] agree [ ] correct: ______

### G298 — IncomeWork [O-FRD]
- **Q:** Were all income calculation requirements met?
- **Defect condition:** The income calculation worksheet is not located in the file or is incomplete/inaccurate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2284
- **Severity:** Major
- **Machine checks:** presence of an income-calculation worksheet
- **Stays human:** 'income discrepancies were not explained' clause (appended, open-ended)
- **Data needed:** income-calculation-worksheet document type — not in the corpus
- **Rationale:** Recurs identically under 5 different AMQ question categories. Presence half is crisp once the worksheet doc type is modeled; the appended discrepancy-explanation clause stays partly human, same pattern as asset-verification's G007 (crisp presence + appended open catch-all kept YELLOW, not RED).
- **SME:** [ ] agree [ ] correct: ______

### G299 — VVOE Inactive [O-FRD]
- **Q:** Were all income calculation requirements met?
- **Defect condition:** The verbal verification of employment does not show borrower in an active status
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2559
- **Severity:** Critical
- **Data needed:** a VVOE (verbal verification of employment) log/status fact — not currently modeled; the corpus has a written/signed VOE (loan 01) but no distinct verbal-VOE artifact with an active/inactive status field
- **Rationale:** Recurs identically under 7 different AMQ question categories. The written VOE this pilot extracts (employment_start_date_voe) is a different document from a VVOE call/database log; no such artifact exists in any of the 5 synthetic loans.
- **SME:** [ ] agree [ ] correct: ______

### G300 — O-FRD-50419 [O-FRD]
- **Q:** Were all income stability requirements met?
- **Defect condition:** Analysis of income and/or asset qualification source and amount not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2577
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G301 — O-FHA-02284 [O-FHA]
- **Q:** Were all income stability requirements met?
- **Defect condition:** Change in line of work/change of employers over 3x in last 12 mos & income stability not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2217
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G302 — O-FHA-02285 [O-FHA]
- **Q:** Were all income stability requirements met?
- **Defect condition:** Employment gap 6 mos or more & not currently employed for at least 6 mos &/or no 2 yr history
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2179
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G303 — O-FRD-03077 [O-FRD]
- **Q:** Were all income stability requirements met?
- **Defect condition:** Less than 2 yr employment history & documentation req's not met to justifying stable employment
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2408
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G304 — O-FRD-50421 [O-FRD]
- **Q:** Were all income stability requirements met?
- **Defect condition:** Likeliness to continue not evaluated correct based on income/earnings type
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2266
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G306 — O-FHA-02286 [O-FHA]
- **Q:** Were all income stability requirements met?
- **Defect condition:** Temp income reduction-Current income as effective income used w/out meeting all requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2522
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G307 — O-FRD-57265 [O-FRD]
- **Q:** Were all income stability requirements met?
- **Defect condition:** The income written analysis did not include all required topics
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2578
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G308 — O-FRD-57987 [O-FRD]
- **Q:** Were all income verification requirements met?
- **Defect condition:** Email verification as a VVOE alt not dated w/in 10 business days &/or did not include all req'd info
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2102
- **Severity:** Major
- **Data needed:** verbal VOE (VVOE) call/database log — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once verbal VOE (VVOE) call/database log is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G309 — O-FRD-52178 [O-FRD]
- **Q:** Were all income verification requirements met?
- **Defect condition:** Military leave & earnings stmt used to meet the 10 day PCV requirement not dated within 120 days
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2096
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once military Leave & Earnings Statement (LES) / VA benefits award letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G312 — O-FRD-50423 [O-FRD]
- **Q:** Were all income verification requirements met?
- **Defect condition:** The required W2 or acceptable alternative was not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2576
- **Severity:** Critical
- **Data needed:** W-2 form(s) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once W-2 form(s) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G313 — VVOE Inactive [O-FRD]
- **Q:** Were all income verification requirements met?
- **Defect condition:** The verbal verification of employment does not show borrower in an active status
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2558
- **Severity:** Critical
- **Data needed:** a VVOE (verbal verification of employment) log/status fact — not currently modeled; the corpus has a written/signed VOE (loan 01) but no distinct verbal-VOE artifact with an active/inactive status field
- **Rationale:** Recurs identically under 7 different AMQ question categories. The written VOE this pilot extracts (employment_start_date_voe) is a different document from a VVOE call/database log; no such artifact exists in any of the 5 synthetic loans.
- **SME:** [ ] agree [ ] correct: ______

### G314 — O-FRD-54339 [O-FRD]
- **Q:** Were all income verification requirements met?
- **Defect condition:** Third-party 10-day PCV used and name/contact information for the service provider not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2526
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G315 — O-FRD-50425 [O-FRD]
- **Q:** Were all income verification requirements met?
- **Defect condition:** VOE did not provide all required employment & earning information for most recent 1 or 2 yr period
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2571
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G316 — O-FRD-50427 [O-FRD]
- **Q:** Were all income verification requirements met?
- **Defect condition:** VOE for prior employment did not contain all required employment/earnings information
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2407
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G318 — O-FRD-50428 [O-FRD]
- **Q:** Were all income verification requirements met?
- **Defect condition:** VVOE or alternative missing or not dated w/in 10 business days of the Note &/or missing information
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2060
- **Severity:** Critical
- **Data needed:** verbal VOE (VVOE) call/database log — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once verbal VOE (VVOE) call/database log is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G319 — 3rdParty [O-FRD]
- **Q:** Were all income verification requirements met?
- **Defect condition:** Vendor for 3rd party VOE was not Equifax/TWN or manual process not followed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2066
- **Severity:** Critical
- **Data needed:** a VOE-vendor-name field (e.g. Equifax/The Work Number) — not currently captured from any document
- **Rationale:** Recurs identically under 5 different AMQ question categories. Crisp presence/identity check once a vendor-name field exists; no such field is in FIELD_SPECS['voe'] today.
- **SME:** [ ] agree [ ] correct: ______

### G320 — O-FRD-00332 [O-FRD]
- **Q:** Were all income verification requirements met?
- **Defect condition:** Verification of income from 3rd party was used, but did not meet 3rd party verification requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2528
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G322 — O-FRD-57379 [O-FRD]
- **Q:** Were all income verification requirements met?
- **Defect condition:** YTD paystub not last prior to Note date & paid through date over 15 business days prior to Note date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2575
- **Severity:** Critical
- **Data needed:** paystub — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once paystub is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G323 — O-FHA-50014 [O-FHA]
- **Q:** Were all investment income requirements met?
- **Defect condition:** Interest & dividend-Most recent 2 yrs tax returns & most recent account statement were not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2297
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G324 — O-FHA-02305 [O-FHA]
- **Q:** Were all investment income requirements met?
- **Defect condition:** Investment-Not verified & documented with tax returns for previous 2yrs & most recent acct statement
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2299
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G326 — O-FHA-50693 [O-FHA]
- **Q:** Were all manually underwritten other income requirements met?
- **Defect condition:** Income grossed up, amount/source of the income & current tax rate applicable not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2374
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G328 — O-FHA-02292 [O-FHA]
- **Q:** Were all manually underwritten self-employed income requirements met?
- **Defect condition:** Manual underwrite of SE borrower missing last 2 yrs complete individual & business tax returns
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2335
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G330 — O-FHA-02294 [O-FHA]
- **Q:** Were all manually underwritten self-employed income requirements met?
- **Defect condition:** Self employment income from a corporation used to qualify; a business credit report was not obtained
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2334
- **Severity:** Critical
- **Data needed:** business tax return / business credit report / business-existence verification — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once business tax return / business credit report / business-existence verification is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G331 — O-FNM-50251 [O-FNM]
- **Q:** Were all military income requirements met?
- **Defect condition:** "Other" military income (not base pay) was not documented as stable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2387, 2388
- **Severity:** Critical
- **Data needed:** military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once military Leave & Earnings Statement (LES) / VA benefits award letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.3-01 — Base Income (PDF p.333)
- **Guide candidate:** B3-3.3-05 — Military Income (PDF p.342)
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **SME:** [ ] agree [ ] correct: ______

### G332 — O-FHA-02283 [O-FHA]
- **Q:** Were all military income requirements met?
- **Defect condition:** A copy of the military leave and earnings statement was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2346
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once military Leave & Earnings Statement (LES) / VA benefits award letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G333 — O-RHS-02745 [O-RHS]
- **Q:** Were all military income requirements met?
- **Defect condition:** A verification from VA was not in the file to support the direct compensation from VA benefits
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2551
- **Severity:** Critical
- **Data needed:** military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once military Leave & Earnings Statement (LES) / VA benefits award letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G334 — Income Breakdown [O-FNM/O-FRD]
- **Q:** Were all military income requirements met?
- **Defect condition:** Income submitted to AUS is not accurate - broken out and/or categorized correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2243, 2248
- **Severity:** Critical
- **Data needed:** a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute
- **Rationale:** Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- **Guide candidate:** B3-3.3-05 — Military Income (PDF p.342)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **SME:** [ ] agree [ ] correct: ______

### G335 — O-FNM-55392 [O-FNM]
- **Q:** Were all military income requirements met?
- **Defect condition:** Military LES not dated within 120 calendar days as req'd when used in lieu of a VVOE
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2351
- **Severity:** Critical
- **Data needed:** verbal VOE (VVOE) call/database log — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once verbal VOE (VVOE) call/database log is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.3-05 — Military Income (PDF p.342)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.1-01 — General Income Information (PDF p.318)
- **SME:** [ ] agree [ ] correct: ______

### G336 — O-FNM-55391 [O-FNM]
- **Q:** Were all military income requirements met?
- **Defect condition:** Military base pay & entitlements was not documented with the most recent leave & earnings statement
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2349
- **Severity:** Critical
- **Data needed:** military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once military Leave & Earnings Statement (LES) / VA benefits award letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.3-01 — Base Income (PDF p.333)
- **Guide candidate:** B3-3.3-05 — Military Income (PDF p.342)
- **Guide candidate:** B3-3.3-09 — Temporary Leave Income (PDF p.347)
- **SME:** [ ] agree [ ] correct: ______

### G337 — O-FRD-59276 [O-FRD]
- **Q:** Were all military income requirements met?
- **Defect condition:** Military base pay &/or entitlements not documented as likely to continue for at least the next 3 yrs
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2344
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once military Leave & Earnings Statement (LES) / VA benefits award letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G338 — O-FRD-03075 [O-FRD]
- **Q:** Were all military income requirements met?
- **Defect condition:** Military base pay not documented w/ YTD Leave & Earnings Stmt or VOE with all YTD & 10-day PCV
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2343
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once military Leave & Earnings Statement (LES) / VA benefits award letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G339 — O-FRD-03084 [O-FRD]
- **Q:** Were all military income requirements met?
- **Defect condition:** Military entitlements not documented w/ YTD Leave & Earnings Stmt or VOE with all YTD & 10-day PCV
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2345
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once military Leave & Earnings Statement (LES) / VA benefits award letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G340 — O-RHS-02727 [O-RHS]
- **Q:** Were all military income requirements met?
- **Defect condition:** Military income was not verified as continuous, regular and likely to continue
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2347
- **Severity:** Critical
- **Data needed:** military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once military Leave & Earnings Statement (LES) / VA benefits award letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G341 — O-FRD-52178 [O-FRD]
- **Q:** Were all military income requirements met?
- **Defect condition:** Military leave & earnings stmt used to meet the 10 day PCV requirement not dated within 120 days
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2097
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once military Leave & Earnings Statement (LES) / VA benefits award letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G343 — O-FRD-59277 [O-FRD]
- **Q:** Were all military income requirements met?
- **Defect condition:** Reserve & Nat'l Guard income history of receipt for 1 yr &/or 3 yrs continuance was not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2439
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once military Leave & Earnings Statement (LES) / VA benefits award letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G344 — O-FRD-03085 [O-FRD]
- **Q:** Were all military income requirements met?
- **Defect condition:** Reserve and Nat'l Guard income not documented w/YTD L&E stmt & W-2 or VOE w/ all YTD & 10-day PCV
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2353
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once military Leave & Earnings Statement (LES) / VA benefits award letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G348 — O-FRD-50432 [O-FRD]
- **Q:** Were all new employment income requirements met?
- **Defect condition:** All req's not met for new employment w/ income starting after the note date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2367
- **Severity:** Critical
- **Data needed:** employment offer/contract letter (anticipated/new-employment income) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once employment offer/contract letter (anticipated/new-employment income) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G349 — O-FRD-50429 [O-FRD]
- **Q:** Were all new employment income requirements met?
- **Defect condition:** Ext absence, new to work or recent employment gaps w/out documentation supporting stable employment
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2180
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** employment offer/contract letter (anticipated/new-employment income) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once employment offer/contract letter (anticipated/new-employment income) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G350 — O-FRD-53927 [O-FRD]
- **Q:** Were all new employment income requirements met?
- **Defect condition:** Income type unacceptable to use where employment history is more than 1 year but less than 2
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2172
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** employment offer/contract letter (anticipated/new-employment income) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once employment offer/contract letter (anticipated/new-employment income) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G352 — O-FRD-51684 [O-FRD]
- **Q:** Were all new employment income requirements met?
- **Defect condition:** Qualifying income is future current employer salary increase not documented &/or all req's not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2265
- **Severity:** Critical
- **Data needed:** employment offer/contract letter (anticipated/new-employment income) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once employment offer/contract letter (anticipated/new-employment income) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G353 — O-RHS-56138 [O-RHS]
- **Q:** Were all other income requirements met, continued?
- **Defect condition:** Guardianship/conservatorship income amount currently being received was not documented in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2230
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G354 — O-RHS-57763 [O-RHS]
- **Q:** Were all other income requirements met, continued?
- **Defect condition:** Most recent assets from applicants/household members at application not used in annual income review
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2143
- **Severity:** Major
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G356 — O-RHS-57142 [O-RHS]
- **Q:** Were all other income requirements met, continued?
- **Defect condition:** Personal & business asset accounts are co-mingled & not included in calculation of net family assets
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2142
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G357 — O-RHS-56137 [O-RHS]
- **Q:** Were all other income requirements met, continued?
- **Defect condition:** Section 8 Housing Vouchers not documented with a benefit/award letter verifying the subsidy amount
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2477
- **Severity:** Critical
- **Data needed:** benefits/award letter (SSA, VA, pension, or disability payer) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once benefits/award letter (SSA, VA, pension, or disability payer) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G358 — O-RHS-54188 [O-RHS]
- **Q:** Were all other income requirements met, continued?
- **Defect condition:** The mortgage credit certificate (MCC) amount used as qualifying income was calculated incorrectly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2340
- **Severity:** Critical
- **Data needed:** Mortgage Credit Certificate (MCC) document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once Mortgage Credit Certificate (MCC) document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G359 — O-RHS-54186 [O-RHS]
- **Q:** Were all other income requirements met, continued?
- **Defect condition:** The mortgage credit certificate (MCC) award letter/contract with the rate of credit not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2339
- **Severity:** Critical
- **Data needed:** benefits/award letter (SSA, VA, pension, or disability payer) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once benefits/award letter (SSA, VA, pension, or disability payer) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G360 — O-FHA-54826 [O-FHA]
- **Q:** Were all other income requirements met?
- **Defect condition:** 2 yr history of foster care, pymt &/or continuance not validated on written foster care verification
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2216
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** foster-care sponsoring-organization verification letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once foster-care sponsoring-organization verification letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G361 — O-FNM-00430 [O-FNM]
- **Q:** Were all other income requirements met?
- **Defect condition:** A letter or distribution form from VA stating the benefits will continue for 3 yrs was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2550
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **Guide candidate:** B3-3.6-02 — Income Reported on IRS Form 1040 (PDF p.391)
- **Guide candidate:** B3-3.6-03 — Income or Loss Reported on IRS Form 1040, Schedule C (PDF p.393)
- **SME:** [ ] agree [ ] correct: ______

### G363 — O-FHA-54825 [O-FHA]
- **Q:** Were all other income requirements met?
- **Defect condition:** A written verification of foster care payment was not obtained from the organization providing it
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2215
- **Severity:** Critical
- **Data needed:** foster-care sponsoring-organization verification letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once foster-care sponsoring-organization verification letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G364 — O-FRD-03083 [O-FRD]
- **Q:** Were all other income requirements met?
- **Defect condition:** Agreement from employer stating terms including scheduled amt & duration of payments not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2364
- **Severity:** Critical
- **Data needed:** employer-subsidy / mortgage-differential agreement letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once employer-subsidy / mortgage-differential agreement letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G366 — O-RHS-02730 [O-RHS]
- **Q:** Were all other income requirements met?
- **Defect condition:** Auto allowance or expense acct payments considered without all history & continuance req's being met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2119
- **Severity:** Critical
- **Data needed:** automobile-allowance employer letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once automobile-allowance employer letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G367 — O-FNM-00432 [O-FNM]
- **Q:** Were all other income requirements met?
- **Defect condition:** Boarders-Documentation verifying history of shared residency/rent payment for 12 mos not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2127
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **Guide candidate:** B3-3.4-13 — Royalty Payment Income (PDF p.369)
- **SME:** [ ] agree [ ] correct: ______

### G368 — O-RHS-02728 [O-RHS]
- **Q:** Were all other income requirements met?
- **Defect condition:** Consecutive 2 yr history receiving tip income & that it is likely to continue for 3 yrs not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2530
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G369 — O-RHS-02733 [O-RHS]
- **Q:** Were all other income requirements met?
- **Defect condition:** Current employment less than 12 mos or notable earnings increase w/out documenting income stability
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2280
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G370 — O-RHS-02731 [O-RHS]
- **Q:** Were all other income requirements met?
- **Defect condition:** Employed by a family-owned bus. & evidence that applicant is not owner of the business not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2195
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G371 — O-RHS-02744 [O-RHS]
- **Q:** Were all other income requirements met?
- **Defect condition:** Employer housing allowance was not documented as established &/or continuance requirements not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2173
- **Severity:** Critical
- **Data needed:** employer housing-subsidy / parsonage agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once employer housing-subsidy / parsonage agreement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G372 — O-FNM-00431 [O-FNM]
- **Q:** Were all other income requirements met?
- **Defect condition:** Foster care is considered without all required documentation and terms being met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2213
- **Severity:** Critical
- **Data needed:** foster-care sponsoring-organization verification letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once foster-care sponsoring-organization verification letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.4-07 — Foster-Care Income (PDF p.362)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **SME:** [ ] agree [ ] correct: ______

### G373 — O-RHS-02746 [O-RHS]
- **Q:** Were all other income requirements met?
- **Defect condition:** Govnt assistance funds used and not documented &/or history and continuance requirements not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2224
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G374 — O-FRD-50007 [O-FRD]
- **Q:** Were all other income requirements met?
- **Defect condition:** Homeownership Voucher history/cont req's not met &/or documentation did not provide required info
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2231
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G375 — O-FNM-50815 [O-FNM]
- **Q:** Were all other income requirements met?
- **Defect condition:** Income calculation requirements were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2259
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **Guide candidate:** A3-3-03 — Other Servicing Arrangements (PDF p.131)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G376 — Income Breakdown [O-FNM]
- **Q:** Were all other income requirements met?
- **Defect condition:** Income submitted to AUS is not accurate - broken out and/or categorized correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2242
- **Severity:** Critical
- **Data needed:** a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute
- **Rationale:** Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **Guide candidate:** A3-3-03 — Other Servicing Arrangements (PDF p.131)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G377 — O-FNM-00427 [O-FNM]
- **Q:** Were all other income requirements met?
- **Defect condition:** Interest & dividend-Copies of tax returns or account statements verifying 2 yrs receipt not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2296
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.4-08 — Interest and Dividend Income (PDF p.363)
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **SME:** [ ] agree [ ] correct: ______

### G378 — O-RHS-02743 [O-RHS]
- **Q:** Were all other income requirements met?
- **Defect condition:** Interest/dividend income not a 2 yr avg less cash to close &/or history & continuance req's not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2298
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G379 — Paystub Loans [O-FRD]
- **Q:** Were all other income requirements met?
- **Defect condition:** Loans/deductions listed on the paystubs were not addressed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2327
- **Severity:** Critical
- **Data needed:** a paystub-level 'loans/deductions' line-item field — not in FIELD_SPECS['paystub'] today
- **Rationale:** Single AMQ row (O-FRD); crisp cross-check against liabilities/DTI once the paystub deduction-line field exists.
- **SME:** [ ] agree [ ] correct: ______

### G380 — O-FRD-00418 [O-FRD]
- **Q:** Were all other income requirements met?
- **Defect condition:** MCC income did not meet documentation &/or qualifying requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2358
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** Mortgage Credit Certificate (MCC) document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once Mortgage Credit Certificate (MCC) document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G381 — O-RHS-02732 [O-RHS]
- **Q:** Were all other income requirements met?
- **Defect condition:** No 2 yr income history & the file did not document the analysis used supporting income stability
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2515
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G382 — O-FRD-50438 [O-FRD]
- **Q:** Were all other income requirements met?
- **Defect condition:** Non-employment/non-self-employment "other" income used was not calculated correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2384
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G383 — O-FHA-02311 [O-FHA]
- **Q:** Were all other income requirements met?
- **Defect condition:** Non-taxable income grossed-up and income used to qualify was not adequately documented & supported
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2225
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G385 — O-FHA-02310, O-FRD-50010 [O-FHA/O-FRD]
- **Q:** Were all other income requirements met?
- **Defect condition:** Notes Receivable-Existence of the note & consistent pymts for last 12 mos not verified & documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2376, 2378
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** notes-receivable promissory note + deposit evidence — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once notes-receivable promissory note + deposit evidence is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G386 — O-FNM-00428 [O-FNM]
- **Q:** Were all other income requirements met?
- **Defect condition:** Notes Receivable-Note & deposit slips/tax returns/bank stmts documenting 12 mo receipt not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2379
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.4-11 — Notes Receivable Income (PDF p.367)
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **SME:** [ ] agree [ ] correct: ______

### G387 — O-FNM-00424 [O-FNM]
- **Q:** Were all other income requirements met?
- **Defect condition:** Public assistance-Letters/exhibits from paying agency stating amt, frequency & duration not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2417
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **Guide candidate:** B3-3.4-12 — Public Assistance Income (PDF p.368)
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **Guide candidate:** A3-3-03 — Other Servicing Arrangements (PDF p.131)
- **SME:** [ ] agree [ ] correct: ______

### G388 — O-FNM-55664 [O-FNM]
- **Q:** Were all other income requirements met?
- **Defect condition:** Rental income from a live-in personal assistant for a disabled borrower exceeded 30% of gross income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2403
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **Guide candidate:** B3-3.8-01 — Rental Income (PDF p.406)
- **Guide candidate:** A3-3-03 — Other Servicing Arrangements (PDF p.131)
- **SME:** [ ] agree [ ] correct: ______

### G389 — O-FRD-50012 [O-FRD]
- **Q:** Were all other income requirements met?
- **Defect condition:** Royalty-Tax returns, contract/alt documentation and 12 mo receipt with 3 yr continuance not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2460
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G390 — Income - Other [O-FNM]
- **Q:** Were all other income requirements met?
- **Defect condition:** SSI has been grossed up without proper documentation supporting it
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2277
- **Severity:** Critical
- **Data needed:** SSI gross-up documentation fields — not currently captured
- **Rationale:** Single AMQ row (O-FNM); presence/support check once the gross-up documentation field exists.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **Guide candidate:** A3-3-03 — Other Servicing Arrangements (PDF p.131)
- **SME:** [ ] agree [ ] correct: ______

### G391 — O-RHS-50569 [O-RHS]
- **Q:** Were all other income requirements met?
- **Defect condition:** Sect 8 Homeownership Voucher not used as repayment income or offset to PITI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2481, 2482
- **Severity:** Critical
- **Data needed:** Section 8 / Housing Choice Voucher award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once Section 8 / Housing Choice Voucher award letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G392 — O-FNM-00425 [O-FNM]
- **Q:** Were all other income requirements met?
- **Defect condition:** Temporary leave income used and the income does not meet Fannie Mae's requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2524
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **Guide candidate:** B3-3.3-09 — Temporary Leave Income (PDF p.347)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** A2-5-01 — Fannie Mae Trade Name and Trademarks (PDF p.102)
- **SME:** [ ] agree [ ] correct: ______

### G393 — O-FHA-02307 [O-FHA]
- **Q:** Were all other income requirements met?
- **Defect condition:** The expected income was not verified and documented in writing with the employer
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2192
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G394 — O-FNM-00429 [O-FNM]
- **Q:** Were all other income requirements met?
- **Defect condition:** The file does not contain a written verification from the employer for the employer's subsidy
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2365
- **Severity:** Critical
- **Data needed:** employer-subsidy / mortgage-differential agreement letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once employer-subsidy / mortgage-differential agreement letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **Guide candidate:** A3-3-03 — Other Servicing Arrangements (PDF p.131)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G395 — O-FHA-54827 [O-FHA]
- **Q:** Were all other income requirements met?
- **Defect condition:** The foster care income was not calculated using the lesser of last year or 2 year average
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2214
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** foster-care sponsoring-organization verification letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once foster-care sponsoring-organization verification letter is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G396 — O-FHA-02308 [O-FHA]
- **Q:** Were all other income requirements met?
- **Defect condition:** The frequency, duration and amount of the trust distribution were not verified and documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2534
- **Severity:** Critical
- **Data needed:** trust agreement/trustee statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once trust agreement/trustee statement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G397 — O-RHS-02729 [O-RHS]
- **Q:** Were all other income requirements met?
- **Defect condition:** The job/increase in income not verified by employer in writing & scheduled to begin within 60 days
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2411
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G399 — O-RHS-02722 [O-RHS]
- **Q:** Were all overtime, bonus and commission income requirements met?
- **Defect condition:** 2 consecutive year history of paying OT/bonus income along with 3 year continuance was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2317
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G400 — O-RHS-02725 [O-RHS]
- **Q:** Were all overtime, bonus and commission income requirements met?
- **Defect condition:** Commission income considered without the analysis being documented to support the income is stable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2154
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G401 — O-RHS-02724 [O-RHS]
- **Q:** Were all overtime, bonus and commission income requirements met?
- **Defect condition:** Commission income was considered without history and continuance requirements being met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2316
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G403 — O-RHS-02723 [O-RHS]
- **Q:** Were all overtime, bonus and commission income requirements met?
- **Defect condition:** OT & bonus income used & written analysis supporting decision to use additional income not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2130
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G405 — O-FHA-02278 [O-FHA]
- **Q:** Were all overtime, bonus or tip income requirements met?
- **Defect condition:** Verification that the OT/bonus/tip income has been received for 1 yr and will continue not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2390
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G408 — O-FRD-03082 [O-FRD]
- **Q:** Were all overtime, bonus, tips, or commission income requirements met?
- **Defect condition:** Tip income used, Form 4137 and tax returns for the most recent two years were not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2147
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** 1099 (or Form 4137 tip-income) tax form — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once 1099 (or Form 4137 tip-income) tax form is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G411 — O-RHS-02726 [O-RHS]
- **Q:** Were all part-Time, second job, seasonal and/or unemployment income requirements met?
- **Defect condition:** Part-time, secondary, seasonal or unemployment income used without history and continuance req's met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2318
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G412 — O-RHS-51058 [O-RHS]
- **Q:** Were all part-Time, second job, seasonal and/or unemployment income requirements met?
- **Defect condition:** Part-time, secondary, seasonal or unemployment is considered w/out analysis to support stable income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2398
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G414 — O-FHA-02277 [O-FHA]
- **Q:** Were all part-time employment income requirements met?
- **Defect condition:** Verification the PT job has been uninterrupted for past 2 yrs and is likely to continue not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2397
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G415 — O-FRD-03168 [O-FRD]
- **Q:** Were all rental income requirements met?
- **Defect condition:** 2-4 OO or 1-4 NOO schedule E or lease rent not supported by current market rents without comment
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2061
- **Severity:** Critical
- **Data needed:** Schedule E rental-income tax-return page — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once Schedule E rental-income tax-return page is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G416 — O-FNM-00434 [O-FNM]
- **Q:** Were all rental income requirements met?
- **Defect condition:** A lease was used in place of IRS Form 1040, Sch E, to document rental income without justification
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2548
- **Severity:** Critical
- **Data needed:** Schedule E rental-income tax-return page — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once Schedule E rental-income tax-return page is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.6-02 — Income Reported on IRS Form 1040 (PDF p.391)
- **Guide candidate:** B3-3.6-03 — Income or Loss Reported on IRS Form 1040, Schedule C (PDF p.393)
- **Guide candidate:** B3-3.6-04 — Income or Loss Reported on IRS Form 1040, Schedule D (PDF p.394)
- **SME:** [ ] agree [ ] correct: ______

### G417 — O-FHA-57261 [O-FHA]
- **Q:** Were all rental income requirements met?
- **Defect condition:** ADU rental income used as effective income exceeded 30% of the effective income used to qualify
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2080
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G418 — O-FHA-02304 [O-FHA]
- **Q:** Were all rental income requirements met?
- **Defect condition:** Boarder income did not include 12 mos history & signed agrmnt w/ terms & intent to continue boarding
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2126
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G419 — O-FNM-00433 [O-FNM]
- **Q:** Were all rental income requirements met?
- **Defect condition:** Correct documents not used to calculate rental income as per rent history, property & loan type
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2431
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.8-01 — Rental Income (PDF p.406)
- **Guide candidate:** C1-2-01 — General Information on Delivering Loan Data and Documents (PDF p.947)
- **SME:** [ ] agree [ ] correct: ______

### G420 — O-FRD-57501 [O-FRD]
- **Q:** Were all rental income requirements met?
- **Defect condition:** Existing lease in a purchase was not current & fully executed in the seller's name as the landlord
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2418
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G421 — O-FHA-58782 [O-FHA]
- **Q:** Were all rental income requirements met?
- **Defect condition:** File did not document boarder rent received for at least 9 of the most recent 12 months
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2129
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G422 — O-FRD-03171 [O-FRD]
- **Q:** Were all rental income requirements met?
- **Defect condition:** File did not document the req'd property management experience for investment property rental income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2300
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G423 — O-FHA-58781 [O-FHA]
- **Q:** Were all rental income requirements met?
- **Defect condition:** File did not verify boarder’s address is the same as borr’s address where boarder income was used
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2128
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G424 — O-FNM-57317 [O-FNM]
- **Q:** Were all rental income requirements met?
- **Defect condition:** Form 1007/1025 not provided & lease terms were not in effect with receipt of 2 months rental pymts
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2293
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.6-02 — Income Reported on IRS Form 1040 (PDF p.391)
- **Guide candidate:** B3-3.6-03 — Income or Loss Reported on IRS Form 1040, Schedule C (PDF p.393)
- **Guide candidate:** B3-3.6-04 — Income or Loss Reported on IRS Form 1040, Schedule D (PDF p.394)
- **SME:** [ ] agree [ ] correct: ______

### G425 — O-FRD-00414 [O-FRD]
- **Q:** Were all rental income requirements met?
- **Defect condition:** Form 72/1000 or 2 mos rent/deposit & 1st mos rent multi unit/non-subj invest bought/rented last yr
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2063
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G426 — O-FNM-55656 [O-FNM]
- **Q:** Were all rental income requirements met?
- **Defect condition:** Gross rents & expenses through a partnership or S corp & business return w/ form 8825 not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2394
- **Severity:** Critical
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.6-02 — Income Reported on IRS Form 1040 (PDF p.391)
- **Guide candidate:** B3-3.6-03 — Income or Loss Reported on IRS Form 1040, Schedule C (PDF p.393)
- **Guide candidate:** B3-3.6-04 — Income or Loss Reported on IRS Form 1040, Schedule D (PDF p.394)
- **SME:** [ ] agree [ ] correct: ______

### G427 — O-FHA-02303 [O-FHA]
- **Q:** Were all rental income requirements met?
- **Defect condition:** Investment property rental income not documented as req'd per length of ownership & property type
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2434
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G429 — O-FHA-51275 [O-FHA]
- **Q:** Were all rental income requirements met?
- **Defect condition:** Lesser of monthly op income or 75% of fair market rent not used for subj rent with limited history
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2430
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G430 — O-RHS-02747 [O-RHS]
- **Q:** Were all rental income requirements met?
- **Defect condition:** Long term rental income used without last 2 years tax returns including Schedule E &/or signed lease
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2330
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** Schedule E rental-income tax-return page — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once Schedule E rental-income tax-return page is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G431 — O-FRD-03169 [O-FRD]
- **Q:** Were all rental income requirements met?
- **Defect condition:** No lease with reasonable efforts determining lease availability or Form 72/1000 in a purchase
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2516
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G433 — O-FHA-57262 [O-FHA]
- **Q:** Were all rental income requirements met?
- **Defect condition:** Proposed rental income was not documented with a URAR & a Single Family Comparable Rent Schedule
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2413
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G434 — O-FRD-03170 [O-FRD]
- **Q:** Were all rental income requirements met?
- **Defect condition:** Purchase or rental start in last year & no purchase or conversion date &/or lease not used in refi
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2424
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G435 — O-FNM-55655 [O-FNM]
- **Q:** Were all rental income requirements met?
- **Defect condition:** Rental income analysis & documentation based on the time the rental was in service was inappropriate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2419, 2420
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.8-01 — Rental Income (PDF p.406)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G436 — O-FNM-50252 [O-FNM]
- **Q:** Were all rental income requirements met?
- **Defect condition:** Rental income calculated incorrectly &/or not added to income or debts
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2427
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.8-01 — Rental Income (PDF p.406)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.1-01 — General Income Information (PDF p.318)
- **SME:** [ ] agree [ ] correct: ______

### G437 — O-FRD-00412 [O-FRD]
- **Q:** Were all rental income requirements met?
- **Defect condition:** Rental income eligibility &/or continuance req's not met as applicable per property/occupancy types
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2223
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G438 — O-FNM-57986 [O-FNM]
- **Q:** Were all rental income requirements met?
- **Defect condition:** Rental income from a 1 unit w/ an ADU or 2-4 unit primary was not entered as Accessory Unit Income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2079
- **Severity:** Major
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.8-01 — Rental Income (PDF p.406)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.1-01 — General Income Information (PDF p.318)
- **SME:** [ ] agree [ ] correct: ______

### G439 — O-FRD-00411 [O-FRD]
- **Q:** Were all rental income requirements met?
- **Defect condition:** Rental income from live-in-aide and documentation verifying income meets guidelines was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2432
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G440 — O-RHS-02748 [O-RHS]
- **Q:** Were all rental income requirements met?
- **Defect condition:** Rental income received less than 24 mos was not excluded &/or the full debt not considered in ratios
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2437
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G441 — O-FNM-51850 [O-FNM]
- **Q:** Were all rental income requirements met?
- **Defect condition:** Rental income req's for current housing exp & rental history for 1-4 or 2-4 transactions not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2426
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.8-01 — Rental Income (PDF p.406)
- **Guide candidate:** A2-4.1-03 — Electronic Records, Signatures, and Transactions (PDF p.89)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G442 — O-FHA-57252 [O-FHA]
- **Q:** Were all rental income requirements met?
- **Defect condition:** Rental income used from the property being vacated by the borr who is not moving over 100 mi away
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2436
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G443 — O-FHA-02302 [O-FHA]
- **Q:** Were all rental income requirements met?
- **Defect condition:** Subject rental income not documented as required as per the length of ownership and property type
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2435
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G444 — O-FRD-03172 [O-FRD]
- **Q:** Were all rental income requirements met?
- **Defect condition:** The amount of rental income relied on is not within the maximum allowable net rental income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2338
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G445 — O-FNM-57316 [O-FNM]
- **Q:** Were all rental income requirements met?
- **Defect condition:** The file did not contain FNMA Form 1007 or Form 1025, as applicable, or did not meet all form req's
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2199
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.6-02 — Income Reported on IRS Form 1040 (PDF p.391)
- **Guide candidate:** B3-3.6-03 — Income or Loss Reported on IRS Form 1040, Schedule C (PDF p.393)
- **Guide candidate:** B3-3.6-04 — Income or Loss Reported on IRS Form 1040, Schedule D (PDF p.394)
- **SME:** [ ] agree [ ] correct: ______

### G446 — O-FNM-52892 [O-FNM]
- **Q:** Were all rental income requirements met?
- **Defect condition:** The lease transferred to the borr impacts first lien position or enforceability of the subject loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2315
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.8-01 — Rental Income (PDF p.406)
- **Guide candidate:** B5-3.2-06 — HomeStyle Renovation: Renovation Contract, Renovation Loan Agreement, and Lien Waiver (PDF p.757)
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **SME:** [ ] agree [ ] correct: ______

### G448 — O-FRD-55897 [O-FRD]
- **Q:** Were all requirements met for a property with rental income generated from an accessory dwelling unit?_x000D_
- **Defect condition:** ADU rental analysis did not include 3 comp rentals supporting market rent with 1 having a rented ADU
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2082
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G449 — O-FRD-55898 [O-FRD]
- **Q:** Were all requirements met for a property with rental income generated from an accessory dwelling unit?_x000D_
- **Defect condition:** ADU rental income exceeded 30% of the total stable monthly income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2085
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G450 — O-FRD-55896 [O-FRD]
- **Q:** Were all requirements met for a property with rental income generated from an accessory dwelling unit?_x000D_
- **Defect condition:** An ACE appraisal offer was accepted where rental income from an ADU was used
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2083
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G451 — O-FRD-57773 [O-FRD]
- **Q:** Were all requirements met for a property with rental income generated from an accessory dwelling unit?_x000D_
- **Defect condition:** Comparables in the Sales Comparison Approach section did not include at least 1 comp with an ADU
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2081
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G452 — O-FRD-57500 [O-FRD]
- **Q:** Were all requirements met for a property with rental income generated from an accessory dwelling unit?_x000D_
- **Defect condition:** Min income documentation req's not met as applicable for a purchase/NCO refi with ADU rental income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2084
- **Severity:** Critical
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G454 — O-FRD-55899 [O-FRD]
- **Q:** Were all requirements met for a property with rental income generated from an accessory dwelling unit?_x000D_
- **Defect condition:** Qualifying borr did not do landlord education or 1 yr landlord experience using ADU rental income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2086
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once lease / Schedule E / Form 1007-1025 rental-income document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G455 — O-FRD-56104 [O-FRD]
- **Q:** Were all requirements met for borrowers with business ownership interest of less than 25% reporting income on IRS K-1?
- **Defect condition:** 2 year history or 1 w/ supporting documentation of receipt of K-1 income w/ less than 25% ownership
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2309
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** K-1 / Form 1065 / 1120S business tax-return schedule — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once K-1 / Form 1065 / 1120S business tax-return schedule is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G456 — O-FRD-56102 [O-FRD]
- **Q:** Were all requirements met for borrowers with business ownership interest of less than 25% reporting income on IRS K-1?
- **Defect condition:** 2yrs K-1s not in the file where borrower receives income from business with less than 25% ownership
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2310
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** K-1 / Form 1065 / 1120S business tax-return schedule — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once K-1 / Form 1065 / 1120S business tax-return schedule is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G457 — O-FRD-56103 [O-FRD]
- **Q:** Were all requirements met for borrowers with business ownership interest of less than 25% reporting income on IRS K-1?
- **Defect condition:** Available YTD info not in the file where income is rec'd from business with less than 25% ownership
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2579
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** K-1 / Form 1065 / 1120S business tax-return schedule — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once K-1 / Form 1065 / 1120S business tax-return schedule is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G458 — O-FRD-56105 [O-FRD]
- **Q:** Were all requirements met for borrowers with business ownership interest of less than 25% reporting income on IRS K-1?
- **Defect condition:** Current business existence not documented for borrower with less than 25% ownership & K-1 income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2320, 2321
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** K-1 / Form 1065 / 1120S business tax-return schedule — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once K-1 / Form 1065 / 1120S business tax-return schedule is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G460 — Income Breakdown [O-FNM/O-FRD]
- **Q:** Were all restricted stock units and restricted stock income requirements met?_x000D_
- **Defect condition:** Income submitted to AUS is not accurate - broken out and/or categorized correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2245, 2253
- **Severity:** Critical
- **Data needed:** a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute
- **Rationale:** Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- **Guide candidate:** B3-3.3-07 — Restricted Stock Units and Restricted Stock Employment Income (PDF p.344)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **SME:** [ ] agree [ ] correct: ______

### G461 — O-FNM-57394 [O-FNM]
- **Q:** Were all restricted stock units and restricted stock income requirements met?_x000D_
- **Defect condition:** Missing IRS W-2s covering the most recent two-year period reflecting RSU/RS distributions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2446
- **Severity:** Critical
- **Data needed:** RSU/restricted-stock vesting-schedule document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once RSU/restricted-stock vesting-schedule document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.3-07 — Restricted Stock Units and Restricted Stock Employment Income (PDF p.344)
- **Guide candidate:** B3-3.6-02 — Income Reported on IRS Form 1040 (PDF p.391)
- **Guide candidate:** B3-3.6-03 — Income or Loss Reported on IRS Form 1040, Schedule C (PDF p.393)
- **SME:** [ ] agree [ ] correct: ______

### G464 — O-FNM-57391 [O-FNM]
- **Q:** Were all restricted stock units and restricted stock income requirements met?_x000D_
- **Defect condition:** No documentation RSU/RS is publicly traded &/or is missing the current vesting schedule
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2444
- **Severity:** Critical
- **Data needed:** RSU/restricted-stock vesting-schedule document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once RSU/restricted-stock vesting-schedule document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.3-07 — Restricted Stock Units and Restricted Stock Employment Income (PDF p.344)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.4-19 — Schedule K-1 Income <25% Ownership (PDF p.378)
- **SME:** [ ] agree [ ] correct: ______

### G465 — O-FRD-51146 [O-FRD]
- **Q:** Were all restricted stock units and restricted stock income requirements met?_x000D_
- **Defect condition:** No evidence RS/RSU is publicly traded, vesting schedule is in effect &/or previous year pay out
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2442
- **Severity:** Critical
- **Data needed:** RSU/restricted-stock vesting-schedule document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once RSU/restricted-stock vesting-schedule document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G466 — O-FRD-58854 [O-FRD]
- **Q:** Were all restricted stock units and restricted stock income requirements met?_x000D_
- **Defect condition:** Non-recurring RS/RSU income did not have at least 3 yrs vesting & distribution left on vesting sch
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2373
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** RSU/restricted-stock vesting-schedule document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once RSU/restricted-stock vesting-schedule document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G468 — O-FRD-58852 [O-FRD]
- **Q:** Were all restricted stock units and restricted stock income requirements met?_x000D_
- **Defect condition:** Performance RS/RSU with employer is 12-24 mos & calculated using less time that was not supported
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2461
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** RSU/restricted-stock vesting-schedule document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once RSU/restricted-stock vesting-schedule document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G469 — O-FRD-58853 [O-FRD]
- **Q:** Were all restricted stock units and restricted stock income requirements met?_x000D_
- **Defect condition:** RS/RSU income awarded on a recurring basis was not likely to continue for at least 3 years
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2421
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** RSU/restricted-stock vesting-schedule document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once RSU/restricted-stock vesting-schedule document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G470 — O-FRD-58856 [O-FRD]
- **Q:** Were all restricted stock units and restricted stock income requirements met?_x000D_
- **Defect condition:** RS/RSU income not calculated correctly as per the form the vested RS or RSU are distributed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2463
- **Severity:** Critical
- **Data needed:** RSU/restricted-stock vesting-schedule document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once RSU/restricted-stock vesting-schedule document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G471 — O-FRD-50811 [O-FRD]
- **Q:** Were all restricted stock units and restricted stock income requirements met?_x000D_
- **Defect condition:** RS/RSU stock considered without meeting history/continuance, documentation reqs &/or 10 day PCV
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2443
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** RSU/restricted-stock vesting-schedule document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once RSU/restricted-stock vesting-schedule document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G472 — O-FNM-57390 [O-FNM]
- **Q:** Were all restricted stock units and restricted stock income requirements met?_x000D_
- **Defect condition:** Restricted stock was not documented as vested and distributed to the borrower without restrictions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2568
- **Severity:** Critical
- **Data needed:** RSU/restricted-stock vesting-schedule document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once RSU/restricted-stock vesting-schedule document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.3-07 — Restricted Stock Units and Restricted Stock Employment Income (PDF p.344)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B2-2-01 — General Borrower Eligibility Requirements (PDF p.241)
- **SME:** [ ] agree [ ] correct: ______

### G473 — O-FRD-58855 [O-FRD]
- **Q:** Were all restricted stock units and restricted stock income requirements met?_x000D_
- **Defect condition:** The 200-day simple moving avg stock price as basis for calculating RS/RSU income not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2462
- **Severity:** Critical
- **Data needed:** RSU/restricted-stock vesting-schedule document — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once RSU/restricted-stock vesting-schedule document is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G474 — O-FHA-50674 [O-FHA]
- **Q:** Were all retirement income requirements met?
- **Defect condition:** A Benefits Letter &/or likeliness to continue for 3 yrs not documented for social security income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2506
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** 1099 (or Form 4137 tip-income) tax form — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once 1099 (or Form 4137 tip-income) tax form is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G475 — O-FNM-00419 [O-FNM]
- **Q:** Were all retirement income requirements met?
- **Defect condition:** File is missing the SSA award letter, SSA-1099, last signed tax returns or proof of current receipt
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2509
- **Severity:** Critical
- **Data needed:** 1099 (or Form 4137 tip-income) tax form — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once 1099 (or Form 4137 tip-income) tax form is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.4-03 — Annuity, Pension, or Retirement Income (PDF p.354)
- **Guide candidate:** B3-3.6-01 — General Information on Analyzing Individual Tax Returns (PDF p.390)
- **SME:** [ ] agree [ ] correct: ______

### G476 — Income Breakdown [O-FNM]
- **Q:** Were all retirement income requirements met?
- **Defect condition:** Income submitted to AUS is not accurate - broken out and/or categorized correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2238
- **Severity:** Critical
- **Data needed:** a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute
- **Rationale:** Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- **Guide candidate:** B3-3.4-03 — Annuity, Pension, or Retirement Income (PDF p.354)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **SME:** [ ] agree [ ] correct: ______

### G477 — O-FNM-57444 [O-FNM]
- **Q:** Were all retirement income requirements met?
- **Defect condition:** Incorrect percentage used to "gross up" the verified nontaxable social security income as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2228
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **Guide candidate:** B3-3.4-15 — Social Security Income (PDF p.371)
- **Guide candidate:** B3-3.4-03 — Annuity, Pension, or Retirement Income (PDF p.354)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G478 — O-FNM-55987 [O-FNM]
- **Q:** Were all retirement income requirements met?
- **Defect condition:** Missing award letter, 3 yr cont & receipt of SSI drawn from another's acct or own to benefit another
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2505
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** benefits/award letter (SSA, VA, pension, or disability payer) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once benefits/award letter (SSA, VA, pension, or disability payer) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.4-03 — Annuity, Pension, or Retirement Income (PDF p.354)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.1-01 — General Income Information (PDF p.318)
- **SME:** [ ] agree [ ] correct: ______

### G479 — O-FNM-57445 [O-FNM]
- **Q:** Were all retirement income requirements met?
- **Defect condition:** More than 15% was used to "gross up" SSI without documentation to support the income is nontaxable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2229
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.4-03 — Annuity, Pension, or Retirement Income (PDF p.354)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G481 — O-FHA-50675 [O-FHA]
- **Q:** Were all retirement income requirements met?
- **Defect condition:** Recurring  receipt & likeliness to cont. for 3 yrs not documented for IRA/401(k) income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2302
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** retirement-account statement (401(k)/IRA/Keogh/pension) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once retirement-account statement (401(k)/IRA/Keogh/pension) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G482 — O-FNM-54030 [O-FNM]
- **Q:** Were all retirement income requirements met?
- **Defect condition:** Retirement income from a 401(k), IRA, or Keogh acct without 3 yr continuance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2454
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** retirement-account statement (401(k)/IRA/Keogh/pension) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once retirement-account statement (401(k)/IRA/Keogh/pension) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.4-03 — Annuity, Pension, or Retirement Income (PDF p.354)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.1-01 — General Income Information (PDF p.318)
- **SME:** [ ] agree [ ] correct: ______

### G483 — O-FNM-00420 [O-FNM]
- **Q:** Were all retirement income requirements met?
- **Defect condition:** Retirement, annuity or pension not verified using allowable documentation or as required by DU
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2448
- **Severity:** Critical
- **Data needed:** retirement-account statement (401(k)/IRA/Keogh/pension) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once retirement-account statement (401(k)/IRA/Keogh/pension) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.4-03 — Annuity, Pension, or Retirement Income (PDF p.354)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **SME:** [ ] agree [ ] correct: ______

### G484 — O-FNM-54029 [O-FNM]
- **Q:** Were all retirement income requirements met?
- **Defect condition:** Retirement, annuity, pension income used w/out evidence borr has unrestricted access w/out penalty
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2449
- **Severity:** Critical
- **Data needed:** retirement-account statement (401(k)/IRA/Keogh/pension) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once retirement-account statement (401(k)/IRA/Keogh/pension) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.4-03 — Annuity, Pension, or Retirement Income (PDF p.354)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **SME:** [ ] agree [ ] correct: ______

### G485 — O-FNM-55660 [O-FNM]
- **Q:** Were all retirement income requirements met?
- **Defect condition:** SSI from another person's acct or for a dependent was used to qualify w/out a 3- yr continuance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2507
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **Guide candidate:** B3-3.4-03 — Annuity, Pension, or Retirement Income (PDF p.354)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **SME:** [ ] agree [ ] correct: ______

### G486 — O-FHA-02301 [O-FHA]
- **Q:** Were all retirement income requirements met?
- **Defect condition:** The borrower’s receipt of the retirement income was not verified and documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2452
- **Severity:** Critical
- **Data needed:** benefits/award letter (SSA, VA, pension, or disability payer) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once benefits/award letter (SSA, VA, pension, or disability payer) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G488 — O-FHA-02279 [O-FHA]
- **Q:** Were all seasonal employment income requirements met?
- **Defect condition:** Two year verification of seasonal work and that it is reasonably likely to continue was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2470
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G489 — O-FHA-50019 [O-FHA]
- **Q:** Were all seasonal employment income requirements met?
- **Defect condition:** Unemployment income used & 2 yrs signed tax returns with evidence of continuance was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2544
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G490 — O-FNM-00340 [O-FNM]
- **Q:** Were all secondary and seasonal employment income requirements met?
- **Defect condition:** Documentation verifying 2nd job income has been uninterrupted for the previous 2 yrs not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2474
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.2-02 — Standards for Employment-Related Income (PDF p.330)
- **Guide candidate:** B3-3.3-07 — Restricted Stock Units and Restricted Stock Employment Income (PDF p.344)
- **SME:** [ ] agree [ ] correct: ______

### G491 — O-FNM-00341 [O-FNM]
- **Q:** Were all secondary and seasonal employment income requirements met?
- **Defect condition:** Last 2 years of seasonal work not documented or as per DU
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2471
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.2-02 — Standards for Employment-Related Income (PDF p.330)
- **Guide candidate:** B3-3.3-07 — Restricted Stock Units and Restricted Stock Employment Income (PDF p.344)
- **SME:** [ ] agree [ ] correct: ______

### G493 — O-FNM-54120 [O-FNM]
- **Q:** Were all secondary and seasonal employment income requirements met?
- **Defect condition:** Secondary employment has a gap of over 1 month in last 12 mos & employment not changed to seasonal
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2222
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.2-02 — Standards for Employment-Related Income (PDF p.330)
- **Guide candidate:** B3-3.3-07 — Restricted Stock Units and Restricted Stock Employment Income (PDF p.344)
- **SME:** [ ] agree [ ] correct: ______

### G494 — O-FRD-03088 [O-FRD]
- **Q:** Were all self-employed income requirements met?
- **Defect condition:** Business in existence 5+ years & most recent 1 yr signed tax return not provided or as per LP
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2511
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G495 — O-FRD-03089 [O-FRD]
- **Q:** Were all self-employed income requirements met?
- **Defect condition:** Business in existence less than 5 years & last 2 years signed tax returns not provided or as per LP
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2512
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G496 — O-FRD-58283 [O-FRD]
- **Q:** Were all self-employed income requirements met?
- **Defect condition:** Business structure owner interest % change so the business is no longer considered the same business
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2137
- **Severity:** Major
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G497 — O-FRD-54127 [O-FRD]
- **Q:** Were all self-employed income requirements met?
- **Defect condition:** File is missing the required IRS confirmation transcripts not available for the prior year
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2303
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G498 — Income Breakdown [O-FRD]
- **Q:** Were all self-employed income requirements met?
- **Defect condition:** Income submitted to AUS is not accurate - broken out and/or categorized correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2249
- **Severity:** Critical
- **Data needed:** a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute
- **Rationale:** Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- **SME:** [ ] agree [ ] correct: ______

### G499 — O-FRD-00373 [O-FRD]
- **Q:** Were all self-employed income requirements met?
- **Defect condition:** Last two years business tax returns with all applicable schedules were not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2395
- **Severity:** Critical
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G500 — O-FRD-54126 [O-FRD]
- **Q:** Were all self-employed income requirements met?
- **Defect condition:** Most recent year tax returns not filed and an extension from the IRS not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2311
- **Severity:** Critical
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G501 — O-FRD-03091 [O-FRD]
- **Q:** Were all self-employed income requirements met?
- **Defect condition:** No Verification of existence of business from 3rd party/acceptable alt within 120 days of note date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2135
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G502 — O-FRD-58284 [O-FRD]
- **Q:** Were all self-employed income requirements met?
- **Defect condition:** No evaluation the current and prior business structures can be treated as the same business
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2138
- **Severity:** Major
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G504 — O-FRD-50436 [O-FRD]
- **Q:** Were all self-employed income requirements met?
- **Defect condition:** SE < 2 yrs & no combined 2 yr history from current & prior in similar industry & stability analysis
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2497
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G505 — O-FRD-58282 [O-FRD]
- **Q:** Were all self-employed income requirements met?
- **Defect condition:** SE < 2 yrs & qual income not the lesser of the stable monthly income from the new or previous income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2324
- **Severity:** Major
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G506 — O-FRD-00374 [O-FRD]
- **Q:** Were all self-employed income requirements met?
- **Defect condition:** The Freddie Mac Income Analysis Form was not provided in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2484
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G507 — O-FNM-57319 [O-FNM]
- **Q:** Were all self-employed requirements met?
- **Defect condition:** 1 yr personal tax returns used where business existence or at least 25% ownership is less than 5 yrs
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2381
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.6-01 — General Information on Analyzing Individual Tax Returns (PDF p.390)
- **Guide candidate:** A2-4.1-02 — Ownership and Retention of Loan Files and Records (PDF p.83)
- **SME:** [ ] agree [ ] correct: ______

### G508 — O-VA-00368 [O-VA]
- **Q:** Were all self-employed requirements met?
- **Defect condition:** Corp or partnership missing 2 yrs signed business tax returns & all  schedules or as per AUS
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2141
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G509 — O-FNM-02573 [O-FNM]
- **Q:** Were all self-employed requirements met?
- **Defect condition:** Documentation demonstrating the K-1 income may be used to qualify was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2488
- **Severity:** Critical
- **Data needed:** K-1 / Form 1065 / 1120S business tax-return schedule — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once K-1 / Form 1065 / 1120S business tax-return schedule is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-2-04 — DU Documentation Requirements (PDF p.305)
- **SME:** [ ] agree [ ] correct: ______

### G510 — IncomeSEVerification [O-FNM]
- **Q:** Were all self-employed requirements met?
- **Defect condition:** Documentation from a third party provider for the borrower’s business was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2279
- **Severity:** Major
- **Machine checks:** presence of a third-party business-verification document (e.g. CPA letter)
- **Data needed:** CPA-letter/third-party-verification document type — not in the corpus
- **Rationale:** Single AMQ row (O-FNM); exception_description names the specific missing artifact plainly ('CPA letter not provided') — crisp presence check once that doc type is modeled.
- **Guide candidate:** A3-3-01 — Outsourcing of Mortgage Processing and Third-Party Originations (PDF p.123)
- **Guide candidate:** C1-2-03 — Ownership of Mortgage Loans Prior to Purchase or Securitization and Third-Party Security Interests (PDF p.951)
- **Guide candidate:** B2-2-01 — General Borrower Eligibility Requirements (PDF p.241)
- **SME:** [ ] agree [ ] correct: ______

### G511 — O-VA-00369 [O-VA]
- **Q:** Were all self-employed requirements met?
- **Defect condition:** Evidence of the borrower's ownership in a corporation or partnership not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2157
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G512 — O-VA-00364 [O-VA]
- **Q:** Were all self-employed requirements met?
- **Defect condition:** File missing a YTD P&L and current balance sheet as applicable or as per AUS for self-employed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2487
- **Severity:** Critical
- **Machine checks:** SelfEmployedDocsShape's existing borrower_self_employed + ytd_pnl_in_file/ytd_balance_sheet_in_file logic
- **Data needed:** none if wired — see READY_TO_BUILD
- **Rationale:** READY TO BUILD candidate — verified per decision-018 discipline; see module docstring / decision 021.
- **READY TO BUILD:** WIRE, don't build — SelfEmployedDocsShape (CHK-INC-001) already checks exactly this fact (borrower_self_employed AND (ytd_pnl_in_file=false OR ytd_balance_sheet_in_file=false)), extracted today from loan 04's Self-Employed Income Documentation Index (both facts populate: that index marks both docs NOT IN FILE). MAPPED_SHAPES wires the shape to ZERO amq_exception_codes today. Row's exception_description ('the file did not contain a YTD profit and loss statement and current balance sheet') reads naturally as the same either-missing test the shape already implements.
- **SME:** [ ] agree [ ] correct: ______

### G513 — O-FNM-50815 [O-FNM]
- **Q:** Were all self-employed requirements met?
- **Defect condition:** Income calculation requirements were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2258
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.1-01 — General Income Information (PDF p.318)
- **Guide candidate:** B3-3.1-03 — Income Calculator (PDF p.323)
- **SME:** [ ] agree [ ] correct: ______

### G514 — DecliningIncDocument [O-FNM]
- **Q:** Were all self-employed requirements met?
- **Defect condition:** Income is declining and no explanation has been provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2268
- **Severity:** Critical
- **Machine checks:** multi-year income trend detection (declining year-over-year) + presence of a written explanation
- **Data needed:** multi-year per-income-type income history (not currently extracted beyond a single point-in-time base_monthly_income_1003) + an explanation-document presence fact
- **Rationale:** Recurs under 2 AMQ question categories (general employment income, self-employed). No judgment word in the condition itself ('declining' and 'no explanation provided' are both factual, not evaluative) — blocked purely on missing multi-year income data, not a rule-clarity problem.
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.1-01 — General Income Information (PDF p.318)
- **Guide candidate:** B3-3.1-03 — Income Calculator (PDF p.323)
- **SME:** [ ] agree [ ] correct: ______

### G515 — Income Breakdown [O-FNM]
- **Q:** Were all self-employed requirements met?
- **Defect condition:** Income submitted to AUS is not accurate - broken out and/or categorized correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2241
- **Severity:** Critical
- **Data needed:** a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute
- **Rationale:** Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **Guide candidate:** B2-1.3-03 — Cash-Out Reﬁnance Transactions (PDF p.197)
- **SME:** [ ] agree [ ] correct: ______

### G516 — SE Deductions [O-FNM]
- **Q:** Were all self-employed requirements met?
- **Defect condition:** Meals and Entertainment & Mtg < 1 Yr not deducted
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2278
- **Severity:** Critical
- **Data needed:** Schedule C 'meals & entertainment' and 'notes payable < 1 year' deduction line items — not in FIELD_SPECS for any self-employed doc type today
- **Rationale:** Single AMQ row (O-FNM, self-employed block); crisp math once the two named Schedule C line items are extracted — genuinely a Schedule C tax-return field, not in the 5-loan corpus (loan 04's SE index tracks only P&L/balance-sheet presence, not line-item detail).
- **SME:** [ ] agree [ ] correct: ______

### G517 — O-VA-00366 [O-VA]
- **Q:** Were all self-employed requirements met?
- **Defect condition:** Missing 2 years signed individual tax returns or IRS transcripts including all applicable schedules
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2490
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G518 — O-FNM-00378 [O-FNM]
- **Q:** Were all self-employed requirements met?
- **Defect condition:** Most recent 2yrs signed tax returns, including all applicable schedules/tax transcripts not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2489
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.6-01 — General Information on Analyzing Individual Tax Returns (PDF p.390)
- **Guide candidate:** B3-3.1-02 — Tax Return and Transcript Documentation Requirements (PDF p.320)
- **SME:** [ ] agree [ ] correct: ______

### G520 — O-FNM-57386 [O-FNM]
- **Q:** Were all self-employed requirements met?
- **Defect condition:** Qualifying income used the amount calculated by Income Calculator, addt'l lender req's were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2262
- **Severity:** Critical
- **Data needed:** income-calculation worksheet/tool output — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once income-calculation worksheet/tool output is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.1-03 — Income Calculator (PDF p.323)
- **Guide candidate:** B3-3.4-06 — Employment Related Assets as Qualifying Income (PDF p.358)
- **Guide candidate:** A2-3.1-01 — Lender Breach of Contract (PDF p.56)
- **SME:** [ ] agree [ ] correct: ______

### G521 — O-FNM-59117 [O-FNM]
- **Q:** Were all self-employed requirements met?
- **Defect condition:** Self-employed income calculated incorrectly and the optional Income Calculator tool was not used
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2289
- **Severity:** Critical
- **Data needed:** income-calculation worksheet/tool output — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once income-calculation worksheet/tool output is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.1-03 — Income Calculator (PDF p.323)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.1-01 — General Income Information (PDF p.318)
- **SME:** [ ] agree [ ] correct: ______

### G522 — O-FNM-57387 [O-FNM]
- **Q:** Were all self-employed requirements met?
- **Defect condition:** The Income Calculator was used, and qualifying income exceeded the amount calculated by the tool
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2264
- **Severity:** Critical
- **Data needed:** income-calculation worksheet/tool output — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once income-calculation worksheet/tool output is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.1-03 — Income Calculator (PDF p.323)
- **Guide candidate:** B3-3.4-06 — Employment Related Assets as Qualifying Income (PDF p.358)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G523 — O-VA-58297 [O-VA]
- **Q:** Were all self-employed requirements met?
- **Defect condition:** The self-employment income was not calculated correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2499
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G524 — O-FNM-00384 [O-FNM]
- **Q:** Were all self-employed requirements met?
- **Defect condition:** Underwriter did not provide a written analysis of the applicant's individual tax returns
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2291
- **Severity:** Critical
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.6-01 — General Information on Analyzing Individual Tax Returns (PDF p.390)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.1-02 — Tax Return and Transcript Documentation Requirements (PDF p.320)
- **SME:** [ ] agree [ ] correct: ______

### G525 — O-FNM-57385 [O-FNM]
- **Q:** Were all self-employed requirements met?
- **Defect condition:** Where the Income Calculator was used, the Income Calculator findings report was not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2263
- **Severity:** Critical
- **Data needed:** income-calculation worksheet/tool output — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once income-calculation worksheet/tool output is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-2-11 — DU Underwriting Findings Report (PDF p.316)
- **Guide candidate:** B3-3.1-03 — Income Calculator (PDF p.323)
- **Guide candidate:** A4-1-03 — Report of Changes in the Seller/Servicer’s Organization (PDF p.162)
- **SME:** [ ] agree [ ] correct: ______

### G527 — O-FHA-55658 [O-FHA]
- **Q:** Were all self-employment income requirements met?
- **Defect condition:** 2 yrs business returns not in file & SE income not increasing, business assets used &/or is CO refi
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2290
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G528 — O-RHS-50555 [O-RHS]
- **Q:** Were all self-employment income requirements met?
- **Defect condition:** 2 yrs business tax return with applicable schedules not in file as req'd
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2494, 2495, 2496
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G529 — O-FHA-02293 [O-FHA]
- **Q:** Were all self-employment income requirements met?
- **Defect condition:** A YTD profit and loss statement and balance sheet were not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2410
- **Severity:** Critical
- **Machine checks:** SelfEmployedDocsShape's existing borrower_self_employed + ytd_pnl_in_file/ytd_balance_sheet_in_file logic
- **Data needed:** none if wired — see READY_TO_BUILD
- **Rationale:** READY TO BUILD candidate — verified per decision-018 discipline; see module docstring / decision 021.
- **READY TO BUILD:** WIRE, don't build — same fact as O-VA-00364, FHA wording variant ('A YTD P&L and balance sheet was required but not in the file'). Verified: a full-text keyword sweep of every other self-employed/business-income row in this block found no other agency row mentioning both 'profit and loss' and 'balance sheet' together — these two are the only matches.
- **SME:** [ ] agree [ ] correct: ______

### G530 — O-RHS-02735 [O-RHS]
- **Q:** Were all self-employment income requirements met?
- **Defect condition:** Additional business income for self-employed borr considered without written analysis to justify
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2076
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G531 — O-RHS-02739 [O-RHS]
- **Q:** Were all self-employment income requirements met?
- **Defect condition:** An analysis establishing stability of income over the previous 2 years was not completed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2498
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** self-employed income-analysis form (Form 91/1084/1088) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once self-employed income-analysis form (Form 91/1084/1088) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G532 — O-RHS-50552 [O-RHS]
- **Q:** Were all self-employment income requirements met?
- **Defect condition:** Borr considered self-employ owns >25% w/out analysis stable/likely to cont
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2492
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G533 — O-FHA-02290 [O-FHA]
- **Q:** Were all self-employment income requirements met?
- **Defect condition:** Complete tax returns for the most recent two years, including all schedules were not obtained
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2292
- **Severity:** Critical
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G535 — O-FHA-02295 [O-FHA]
- **Q:** Were all self-employment income requirements met?
- **Defect condition:** The UW did not analyze the tax returns to determine the borrower’s gross self-employment income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2485
- **Severity:** Critical
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G536 — O-RHS-02734 [O-RHS]
- **Q:** Were all self-employment income requirements met?
- **Defect condition:** The borrower's self-employment income does not meet the income history requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2355
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G537 — O-FHA-02288 [O-FHA]
- **Q:** Were all self-employment income requirements met?
- **Defect condition:** The self-employment income history did not meet HUD's two-year requirement for effective income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2501
- **Severity:** Critical
- **Data needed:** income-type-specific source fields (not yet in FIELD_SPECS)
- **Rationale:** No document family is named in this row's own text (question, response, and exception description all read) — the condition reduces to a bare 'calculated/met requirements' statement. The underlying math or requirement IS defined by the relevant agency's Selling/AMQ guide for this income type (a citation, not a new number, per this project's grounding rule), but no income-type-specific source field for it exists in the 5-loan corpus yet — blocked on missing fixture/field breadth, not rule clarity.
- **SME:** [ ] agree [ ] correct: ______

### G540 — O-RHS-02784 [O-RHS]
- **Q:** Were all social security, retirement and/or disability income requirements met?
- **Defect condition:** Assets used included unallowable retirement accounts/pensions/Keogh accounts
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2543
- **Severity:** Critical
- **Data needed:** retirement-account statement (401(k)/IRA/Keogh/pension) — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once retirement-account statement (401(k)/IRA/Keogh/pension) is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G541 — O-RHS-50010 [O-RHS]
- **Q:** Were all social security, retirement and/or disability income requirements met?
- **Defect condition:** File missing a disability benefits statement verifying the payment amount and payment frequency
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2165
- **Severity:** Critical
- **Data needed:** disability-benefits payer statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once disability-benefits payer statement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G543 — O-RHS-57764 [O-RHS]
- **Q:** Were all social security, retirement and/or disability income requirements met?
- **Defect condition:** SSI used as repayment income was not documented to continue for at least 3 years into the mortgage
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2508
- **Severity:** Major
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** disability-benefits payer statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once disability-benefits payer statement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G544 — O-RHS-02741 [O-RHS]
- **Q:** Were all social security, retirement and/or disability income requirements met?
- **Defect condition:** The lender did not obtain documentation from the source verifying the retirement income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2456
- **Severity:** Critical
- **Data needed:** disability-benefits payer statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once disability-benefits payer statement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G545 — O-FRD-57516 [O-FRD]
- **Q:** Were all trust income requirements met?
- **Defect condition:** 1-year history of receipt not documented for trust income with pre-determined fixed payment amounts
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2405
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** trust agreement/trustee statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once trust agreement/trustee statement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G546 — O-FRD-57515 [O-FRD]
- **Q:** Were all trust income requirements met?
- **Defect condition:** 2-year history of receipt not documented for trust income based on historical fluctuating payments
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2206
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** trust agreement/trustee statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once trust agreement/trustee statement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G547 — Income Breakdown [O-FRD]
- **Q:** Were all trust income requirements met?
- **Defect condition:** Income submitted to AUS is not accurate - broken out and/or categorized correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2250
- **Severity:** Critical
- **Data needed:** a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute
- **Rationale:** Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- **SME:** [ ] agree [ ] correct: ______

### G548 — O-RHS-02749 [O-RHS]
- **Q:** Were all trust income requirements met?
- **Defect condition:** Missing Trust Agreement or trustee statement confirming amount, frequency, and 3 yrs continuance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2535
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** trust agreement/trustee statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once trust agreement/trustee statement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G550 — O-FRD-50440 [O-FRD]
- **Q:** Were all trust income requirements met?
- **Defect condition:** Pre-determined fixed payment trust income did not meet all doc requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2404
- **Severity:** Critical
- **Data needed:** trust agreement/trustee statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once trust agreement/trustee statement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G551 — O-FRD-50015 [O-FRD]
- **Q:** Were all trust income requirements met?
- **Defect condition:** Trust agreement/trustee's stmt confirming the amount, frequency & duration of payments not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2207
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **SME:** [ ] agree [ ] correct: ______

### G552 — O-FNM-57140 [O-FNM]
- **Q:** Were all trust income requirements met?_x000D_
- **Defect condition:** Employment-related assets were liquidated to a trust w/in 1 yr of application & did not meet req's
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2177
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** trust agreement/trustee statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once trust agreement/trustee statement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.4-06 — Employment Related Assets as Qualifying Income (PDF p.358)
- **Guide candidate:** B3-3.2-02 — Standards for Employment-Related Income (PDF p.330)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **SME:** [ ] agree [ ] correct: ______

### G553 — Income Breakdown [O-FNM]
- **Q:** Were all trust income requirements met?_x000D_
- **Defect condition:** Income submitted to AUS is not accurate - broken out and/or categorized correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2244
- **Severity:** Critical
- **Data needed:** a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute
- **Rationale:** Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- **Guide candidate:** B3-3.4-16 — Trust Income (PDF p.374)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **SME:** [ ] agree [ ] correct: ______

### G555 — O-FNM-57788 [O-FNM]
- **Q:** Were all trust income requirements met?_x000D_
- **Defect condition:** The trust verification documentation did not clearly identify the date the trust was created
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2532
- **Severity:** Major
- **Data needed:** trust agreement/trustee statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once trust agreement/trustee statement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.4-16 — Trust Income (PDF p.374)
- **Guide candidate:** B8-5-02 — Inter Vivos Revocable Trust Mortgage Documentation and Signature Requirements (PDF p.921)
- **SME:** [ ] agree [ ] correct: ______

### G556 — O-FNM-57141 [O-FNM]
- **Q:** Were all trust income requirements met?_x000D_
- **Defect condition:** The variable trust payment income was not calculated correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2555
- **Severity:** Critical
- **Data needed:** trust agreement/trustee statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once trust agreement/trustee statement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.4-13 — Royalty Payment Income (PDF p.369)
- **Guide candidate:** B3-3.4-16 — Trust Income (PDF p.374)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G557 — O-FNM-00426 [O-FNM]
- **Q:** Were all trust income requirements met?_x000D_
- **Defect condition:** Trust agmt/trustee stmt/trust tax returns confirming amt, frequency & income type rec'd not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2537
- **Severity:** Critical
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.4-16 — Trust Income (PDF p.374)
- **Guide candidate:** B3-3.6-01 — General Information on Analyzing Individual Tax Returns (PDF p.390)
- **SME:** [ ] agree [ ] correct: ______

### G558 — O-FNM-57137 [O-FNM]
- **Q:** Were all trust income requirements met?_x000D_
- **Defect condition:** Trust income is a fixed payment from a depleting asset without documenting 3 years of continuance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2536
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** trust agreement/trustee statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once trust agreement/trustee statement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.4-13 — Royalty Payment Income (PDF p.369)
- **Guide candidate:** B3-3.4-16 — Trust Income (PDF p.374)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G559 — O-FNM-57139 [O-FNM]
- **Q:** Were all trust income requirements met?_x000D_
- **Defect condition:** Trust income pymts are fixed & 12 mos of receipt not documented & did not meet other conditions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2538
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** trust agreement/trustee statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once trust agreement/trustee statement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **Guide candidate:** B3-3.4-16 — Trust Income (PDF p.374)
- **Guide candidate:** A3-3-03 — Other Servicing Arrangements (PDF p.131)
- **SME:** [ ] agree [ ] correct: ______

### G560 — O-FNM-57138 [O-FNM]
- **Q:** Were all trust income requirements met?_x000D_
- **Defect condition:** Trust income pymts are variable & a 24 mos history of receipt not documented with 2 yrs tax returns
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2540
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.4-16 — Trust Income (PDF p.374)
- **Guide candidate:** B3-3.6-01 — General Information on Analyzing Individual Tax Returns (PDF p.390)
- **SME:** [ ] agree [ ] correct: ______

### G561 — O-FNM-57789 [O-FNM]
- **Q:** Were all trust income requirements met?_x000D_
- **Defect condition:** Variable trust income rec'd at least 1 yr but less than 2 yrs used w/out offsetting positive factors
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2554
- **Severity:** Major
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** trust agreement/trustee statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once trust agreement/trustee statement is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.4-16 — Trust Income (PDF p.374)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **SME:** [ ] agree [ ] correct: ______

### G563 — O-FNM-00422 [O-FNM]
- **Q:** Were all unemployment income requirements met?
- **Defect condition:** Unemployment income used w/out 2 yrs signed tax returns documenting consistent receipt or as per DU
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2547
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.4-17 — Unemployment Beneﬁts Income (PDF p.376)
- **Guide candidate:** B3-3.6-01 — General Information on Analyzing Individual Tax Returns (PDF p.390)
- **SME:** [ ] agree [ ] correct: ______

### G564 — O-FNM-52800 [O-FNM]
- **Q:** Were all unemployment income requirements met?
- **Defect condition:** Unemployment income used was not clearly associated with seasonal income as per the tax returns
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2545
- **Severity:** Critical
- **Data needed:** personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once personal/business tax return or IRS transcript is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.3-08 — Seasonal Income (PDF p.346)
- **Guide candidate:** B3-3.4-17 — Unemployment Beneﬁts Income (PDF p.376)
- **SME:** [ ] agree [ ] correct: ______

### G565 — O-FNM-00351 [O-FNM]
- **Q:** Were all verbal verification of employment requirements met?
- **Defect condition:** A VVOE was not obtained or was not dated within 10 business days of the note date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2564
- **Severity:** Critical
- **Data needed:** verbal VOE (VVOE) call/database log — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once verbal VOE (VVOE) call/database log is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.1-04 — Verbal Veriﬁcation of Employment (PDF p.324)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.2-02 — Standards for Employment-Related Income (PDF p.330)
- **SME:** [ ] agree [ ] correct: ______

### G566 — O-FNM-55908 [O-FNM]
- **Q:** Were all verbal verification of employment requirements met?
- **Defect condition:** Alternative VOE method employer email did not include all required information
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2105
- **Severity:** Critical
- **Data needed:** verbal VOE (VVOE) call/database log — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once verbal VOE (VVOE) call/database log is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.1-04 — Verbal Veriﬁcation of Employment (PDF p.324)
- **Guide candidate:** A2-2-02 — Delivery Information and Delivery-Option Speciﬁc Representations and Warranties (PDF p.34)
- **Guide candidate:** A3-4-01 — Conﬁdentiality of Information (PDF p.137)
- **SME:** [ ] agree [ ] correct: ______

### G567 — O-FNM-55907 [O-FNM]
- **Q:** Were all verbal verification of employment requirements met?
- **Defect condition:** File did not confirm the employer email address is accurate for an alternative VOE method
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2104
- **Severity:** Critical
- **Data needed:** verbal VOE (VVOE) call/database log — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once verbal VOE (VVOE) call/database log is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.1-04 — Verbal Veriﬁcation of Employment (PDF p.324)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.2-02 — Standards for Employment-Related Income (PDF p.330)
- **SME:** [ ] agree [ ] correct: ______

### G570 — VVOE Inactive [O-FNM]
- **Q:** Were all verbal verification of employment requirements met?
- **Defect condition:** The verbal verification of employment does not show borrower in an active status
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2557
- **Severity:** Critical
- **Data needed:** a VVOE (verbal verification of employment) log/status fact — not currently modeled; the corpus has a written/signed VOE (loan 01) but no distinct verbal-VOE artifact with an active/inactive status field
- **Rationale:** Recurs identically under 7 different AMQ question categories. The written VOE this pilot extracts (employment_start_date_voe) is a different document from a VVOE call/database log; no such artifact exists in any of the 5 synthetic loans.
- **Guide candidate:** B3-3.1-04 — Verbal Veriﬁcation of Employment (PDF p.324)
- **Guide candidate:** B2-2-01 — General Borrower Eligibility Requirements (PDF p.241)
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **SME:** [ ] agree [ ] correct: ______

### G571 — O-FNM-52165 [O-FNM]
- **Q:** Were all verbal verification of employment requirements met?
- **Defect condition:** Third-party vendor database data used to obtain the VVOE was older than 35 days of the note date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2527
- **Severity:** Critical
- **Machine checks:** threshold/date comparison once the field exists
- **Data needed:** verbal VOE (VVOE) call/database log — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/threshold check once verbal VOE (VVOE) call/database log is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** A3-3-01 — Outsourcing of Mortgage Processing and Third-Party Originations (PDF p.123)
- **Guide candidate:** B3-3.1-04 — Verbal Veriﬁcation of Employment (PDF p.324)
- **Guide candidate:** C1-2-03 — Ownership of Mortgage Loans Prior to Purchase or Securitization and Third-Party Security Interests (PDF p.951)
- **SME:** [ ] agree [ ] correct: ______

### G572 — O-FNM-57389 [O-FNM]
- **Q:** Were all verbal verification of employment requirements met?
- **Defect condition:** VVOE alt bank stmnts not within 15 business days before the note &/or do not contain all req'd info
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2573
- **Severity:** Critical
- **Data needed:** verbal VOE (VVOE) call/database log — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once verbal VOE (VVOE) call/database log is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.1-04 — Verbal Veriﬁcation of Employment (PDF p.324)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.2-02 — Standards for Employment-Related Income (PDF p.330)
- **SME:** [ ] agree [ ] correct: ______

### G573 — O-FNM-57388 [O-FNM]
- **Q:** Were all verbal verification of employment requirements met?
- **Defect condition:** VVOE alt paystub not within 15 business days before the note &/or does not contain all req'd info
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2574
- **Severity:** Critical
- **Data needed:** verbal VOE (VVOE) call/database log — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once verbal VOE (VVOE) call/database log is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.1-04 — Verbal Veriﬁcation of Employment (PDF p.324)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.2-02 — Standards for Employment-Related Income (PDF p.330)
- **SME:** [ ] agree [ ] correct: ______

### G574 — O-FNM-53031 [O-FNM]
- **Q:** Were all verbal verification of employment requirements met?
- **Defect condition:** VVOE not obtained or not dated within 120 calendar days of the note date for self-employed income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2491
- **Severity:** Critical
- **Data needed:** verbal VOE (VVOE) call/database log — not among the doc/field types the 5-loan synthetic corpus extracts today
- **Rationale:** Crisp presence/documentation check once verbal VOE (VVOE) call/database log is captured; this income sub-type's documentation is absent from all 5 synthetic loans (which cover one W-2 wage-earner profile, one self-employed profile with only P&L/balance-sheet presence tracked, and one USDA income-limit profile) — same root cause as the asset-verification triage's dominant finding, not a rule-clarity problem.
- **Guide candidate:** B3-3.1-04 — Verbal Veriﬁcation of Employment (PDF p.324)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.2-02 — Standards for Employment-Related Income (PDF p.330)
- **SME:** [ ] agree [ ] correct: ______

### G575 — 3rdParty [O-FNM]
- **Q:** Were all verbal verification of employment requirements met?
- **Defect condition:** Vendor for 3rd party VOE was not Equifax/TWN or manual process not followed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2065
- **Severity:** Critical
- **Data needed:** a VOE-vendor-name field (e.g. Equifax/The Work Number) — not currently captured from any document
- **Rationale:** Recurs identically under 5 different AMQ question categories. Crisp presence/identity check once a vendor-name field exists; no such field is in FIELD_SPECS['voe'] today.
- **Guide candidate:** B3-3.1-04 — Verbal Veriﬁcation of Employment (PDF p.324)
- **Guide candidate:** A3-3-01 — Outsourcing of Mortgage Processing and Third-Party Originations (PDF p.123)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **SME:** [ ] agree [ ] correct: ______

### G577 — VVOE Inactive [O-RHS]
- **Q:** Were all wage earner income requirements met?
- **Defect condition:** The verbal verification of employment does not show borrower in an active status
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2560
- **Severity:** Critical
- **Data needed:** a VVOE (verbal verification of employment) log/status fact — not currently modeled; the corpus has a written/signed VOE (loan 01) but no distinct verbal-VOE artifact with an active/inactive status field
- **Rationale:** Recurs identically under 7 different AMQ question categories. The written VOE this pilot extracts (employment_start_date_voe) is a different document from a VVOE call/database log; no such artifact exists in any of the 5 synthetic loans.
- **SME:** [ ] agree [ ] correct: ______

### G578 — 3rdParty [O-RHS]
- **Q:** Were all wage earner income requirements met?
- **Defect condition:** Vendor for 3rd party VOE was not Equifax/TWN or manual process not followed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2067
- **Severity:** Critical
- **Data needed:** a VOE-vendor-name field (e.g. Equifax/The Work Number) — not currently captured from any document
- **Rationale:** Recurs identically under 5 different AMQ question categories. Crisp presence/identity check once a vendor-name field exists; no such field is in FIELD_SPECS['voe'] today.
- **SME:** [ ] agree [ ] correct: ______

## RED

### G025 — O-VA-00406 [O-VA]
- **Q:** Did the other income meet all requirements and was it calculated correctly?
- **Defect condition:** Income used not addressed by VA was not sufficiently documented &/or continuance was unreasonable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2542
- **Severity:** Critical
- **Stays human:** 'not addressed by VA' undefined-income-type catch-all + 'continuance was unreasonable' judgment
- **Rationale:** Income source not otherwise addressed by VA guidance is, by definition, not enumerable today — no defined document or threshold exists to check against until an SME decomposes what 'sufficiently documented' would even mean for an unnamed income type. Same catch-all pattern as asset-verification's G018/G023/G196 (VA/RHS bare 'all requirements' rows).
- **SME:** [ ] agree [ ] correct: ______

### G122 — O-RHS-02785 [O-RHS]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** Significant increase/decrease in income and UW analysis does not support stability and continuance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2161
- **Severity:** Critical
- **Stays human:** underwriter's own stability/continuance analysis judged 'does not support' its conclusion — an adequacy-of-analysis judgment, not mere presence
- **Rationale:** Distinct from the many 'analysis not documented' rows elsewhere in this block (which are presence checks, kept YELLOW): here the analysis EXISTS and the question is whether its content 'supports' stability and continuance — a judgment on analytical adequacy with no defined bright-line test, same class as asset-verification's G228 (underwriter review-completeness sweep).
- **SME:** [ ] agree [ ] correct: ______

### G168 — O-RHS-02829 [O-RHS]
- **Q:** Were all annual household income requirements met?
- **Defect condition:** Noted income discrepancies were not resolved and documented in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2269
- **Severity:** Critical
- **Stays human:** cross-file 'noted income discrepancies... resolved' sweep
- **Rationale:** Open-ended discrepancy-resolution judgment scoped to 'noted' discrepancies with no definition of which ones or what standard resolves them — same class as application-verification's G07 (file-wide discrepancies-not-explained catch-all).
- **SME:** [ ] agree [ ] correct: ______

### G180 — O-FRD-50420 [O-FRD]
- **Q:** Were all asset used as income qualification requirements met?
- **Defect condition:** Assets used as income not reasonable/stable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2112
- **Severity:** Critical
- **Stays human:** 'reasonable and stable' judgment on an asset-based income source, with no accompanying threshold or document named
- **Rationale:** Bare reasonableness/stability determination — exception_description adds no crisp element ('without determining that the source... and/or the amount... was reasonable and stable'). Same class as asset-verification's G035 (unreasonable-savings judgment with no computable data behind it either).
- **SME:** [ ] agree [ ] correct: ______

### G310 — O-FRD-55384 [O-FRD]
- **Q:** Were all income verification requirements met?
- **Defect condition:** Necessary additional documentation not obtained to evaluate, justify and explain the qualification
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2077
- **Severity:** Critical
- **Stays human:** 'necessary additional documentation... to evaluate, justify and explain the qualification' — fully open-ended, no specific document or fact named
- **Rationale:** Bare catch-all with zero stated specifics, same pattern as asset-verification's G101 ('third-party verification requirements', unspecified).
- **SME:** [ ] agree [ ] correct: ______

### G538 — O-FHA-02289 [O-FHA]
- **Q:** Were all self-employment income requirements met?
- **Defect condition:** The self-employment income is not stable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2500
- **Severity:** Critical
- **Stays human:** 'self-employment income is not stable' — bare conclusion, no accompanying document or threshold
- **Rationale:** exception_description adds nothing beyond restating the conclusion ('did not meet stability requirements'). Distinct from the many self-employed rows elsewhere in this block that name a specific document (tax returns, P&L, business credit report) — this one names none.
- **SME:** [ ] agree [ ] correct: ______

## NOT_A_CHECK

### G003 —  [O-VA]
- **Q:** Did the Alimony, Child Support and/or Maintenance income meet all requirements and was it calculated correctly?
- **Defect condition:** Yes, all Alimony, Child Support and/or Maintenance income requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2773
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G010 —  [O-VA]
- **Q:** Did the Military income meet all requirements and was it calculated correctly?
- **Defect condition:** Yes, all Military income requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2771
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G015 —  [O-VA]
- **Q:** Did the Part-Time, Second Job, Seasonal and/or Unemployment income meet all requirements and was it calculated correctly?
- **Defect condition:** Yes, all Part-Time, Second Job, Seasonal and/or Unemployment income requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2770
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G019 —  [O-VA]
- **Q:** Did the Social Security, Retirement and/or Disability income meet all requirements and was it calculated correctly?
- **Defect condition:** Yes, all Social Security, Retirement and/or Disability income requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2772
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G026 —  [O-VA]
- **Q:** Did the other income meet all requirements and was it calculated correctly?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2774, 2775
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G034 —  [O-VA]
- **Q:** Did the overtime, bonus or commission income meet all requirements and was it calculated correctly?
- **Defect condition:** Yes, all overtime, bonus or commission income requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2767
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G039 —  [O-VA]
- **Q:** Did the rental income meet all requirements and was it calculated correctly?
- **Defect condition:** Yes, all rental income requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2769
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G044 —  [O-VA]
- **Q:** Did the wage earner income meet all requirements and was it calculated correctly?
- **Defect condition:** Yes, all wage earner income requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2766
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G045 —  [O-FRD]
- **Q:** Were additional self-employed income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2730, 2731
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G051 —  [O-FRD]
- **Q:** Were all 1099 income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2722, 2723
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G056 —  [O-FHA]
- **Q:** Were all AUS specific other income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2636, 2637
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G060 —  [O-FHA]
- **Q:** Were all AUS specific self-employment income requirements met?
- **Defect condition:** Yes, all   self-employment income requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2635
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G065 —  [O-FRD]
- **Q:** Were all Alimony, Child Support and/or Maintenance income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2714, 2715
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G070 —  [O-FHA/O-FNM/O-FRD/O-RHS/O-VA]
- **Q:** Were all IRS Form 4506-C requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2638, 2639, 2652, 2653, 2720, 2721, 2764, 2765, 2777, 2778
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G074 —  [O-FRD]
- **Q:** Were all IRS verification requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2688, 2689
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G079 —  [O-FRD]
- **Q:** Were all Part-Time, Second Job, Seasonal and/or Unemployment income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2702, 2703
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G086 —  [O-FRD]
- **Q:** Were all Social Security, Retirement and/or Disability income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2694, 2695
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G097 —  [O-RHS]
- **Q:** Were all additional annual household income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2760, 2761
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G117 —  [O-FNM/O-FRD/O-RHS]
- **Q:** Were all additional other income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2677, 2678, 2718, 2719, 2742, 2743
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G138 —  [O-FHA/O-FRD]
- **Q:** Were all additional rental income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2640, 2641, 2708, 2709
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G144 —  [O-RHS]
- **Q:** Were all additional self-employment income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2748, 2749
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G151 —  [O-RHS]
- **Q:** Were all alimony, child support and/or maintenance income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2752, 2753
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G155 —  [O-FHA]
- **Q:** Were all alimony, child support, and maintenance income requirements met?
- **Defect condition:** Yes, all   alimony, child support, and maintenance income requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2617
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G160 —  [O-FNM]
- **Q:** Were all alimony, child support, maintenance, or other nontaxable income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2661, 2662
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G167 —  [O-RHS]
- **Q:** Were all annual household income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2758, 2759
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G176 —  [O-FNM]
- **Q:** Were all anticipated income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2669, 2670
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G186 —  [O-FRD]
- **Q:** Were all asset used as income qualification requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2712, 2713
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G193 —  [O-FHA/O-FNM]
- **Q:** Were all automobile allowance requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2621, 2622, 2657, 2658
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G198 —  [O-FNM]
- **Q:** Were all base pay (salary and hourly), bonus, tip, and overtime income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2646, 2647
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G202 —  [O-FNM]
- **Q:** Were all business income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2671, 2672
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G205 —  [O-FHA/O-FNM]
- **Q:** Were all commission income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2610, 2611, 2648, 2649
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G209 —  [O-FHA/O-FNM]
- **Q:** Were all disability income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2615, 2616, 2665, 2666
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G211 —  [O-FHA]
- **Q:** Were all employer housing subsidy income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2606, 2607
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G216 —  [O-FNM]
- **Q:** Were all employment documentation requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2644, 2645
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G236 —  [O-FHA/O-FNM]
- **Q:** Were all employment income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2598, 2599, 2642, 2643
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G245 —  [O-FHA]
- **Q:** Were all family-owned business income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2608, 2609
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G254 —  [O-FRD]
- **Q:** Were all fluctuating income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2696, 2697
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G266 —  [O-VA]
- **Q:** Were all general income and verification requirements met?
- **Defect condition:** Yes, all general income and verification requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2776
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G271 —  [O-FHA]
- **Q:** Were all general income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2596, 2597
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G279 —  [O-RHS]
- **Q:** Were all general income verification requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2762, 2763
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G285 —  [O-FNM]
- **Q:** Were all housing assistance income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2667, 2668
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G289 —  [O-FHA]
- **Q:** Were all housing assistance requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2619, 2620
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G297 —  [O-FRD]
- **Q:** Were all income calculation requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2690, 2691
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G305 —  [O-FHA/O-FRD]
- **Q:** Were all income stability requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2613, 2614, 2684, 2685
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G311 —  [O-FRD]
- **Q:** Were all income verification requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2686, 2687
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G325 —  [O-FHA]
- **Q:** Were all investment income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2627, 2628
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G327 —  [O-FHA]
- **Q:** Were all manually underwritten other income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2633, 2634
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G329 —  [O-FHA]
- **Q:** Were all manually underwritten self-employed income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2631, 2632
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G342 —  [O-FRD/O-RHS]
- **Q:** Were all military income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2700, 2701, 2738, 2739
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G346 —  [O-FHA]
- **Q:** Were all military income requirements met?
- **Defect condition:** Yes, all   military income requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2618
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G347 —  [O-FNM]
- **Q:** Were all military income requirements met?
- **Defect condition:** Yes, all military income requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2679
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G351 —  [O-FRD]
- **Q:** Were all new employment income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2698, 2699
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G355 —  [O-RHS]
- **Q:** Were all other income requirements met, continued?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2744, 2745
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G384 —  [O-FHA/O-FNM/O-FRD/O-RHS]
- **Q:** Were all other income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2629, 2630, 2675, 2676, 2716, 2717, 2740, 2741
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G402 —  [O-RHS]
- **Q:** Were all overtime, bonus and commission income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2734, 2735
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G404 —  [O-FHA]
- **Q:** Were all overtime, bonus or tip income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2602, 2603
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G407 —  [O-FRD]
- **Q:** Were all overtime, bonus, tips, or commission income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2692, 2693
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G410 —  [O-RHS]
- **Q:** Were all part-Time, second job, seasonal and/or unemployment income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2736, 2737
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G413 —  [O-FHA]
- **Q:** Were all part-time employment income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2600, 2601
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G432 —  [O-FHA/O-FRD/O-RHS]
- **Q:** Were all rental income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2625, 2626, 2706, 2707, 2754, 2755
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G447 —  [O-FNM]
- **Q:** Were all rental income requirements met?
- **Defect condition:** Yes, all rental income requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2656
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G453 —  [O-FRD]
- **Q:** Were all requirements met for a property with rental income generated from an accessory dwelling unit?_x000D_
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2728, 2729
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G459 —  [O-FRD]
- **Q:** Were all requirements met for borrowers with business ownership interest of less than 25% reporting income on IRS K-1?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2724, 2725
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G467 —  [O-FNM/O-FRD]
- **Q:** Were all restricted stock units and restricted stock income requirements met?_x000D_
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2682, 2683, 2726, 2727
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G480 —  [O-FHA/O-FNM]
- **Q:** Were all retirement income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2623, 2624, 2659, 2660
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G487 —  [O-FHA]
- **Q:** Were all seasonal employment income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2604, 2605
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G492 —  [O-FNM]
- **Q:** Were all secondary and seasonal employment income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2650, 2651
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G503 —  [O-FRD]
- **Q:** Were all self-employed income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2704, 2705
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G519 —  [O-FNM]
- **Q:** Were all self-employed requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2673, 2674
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G526 —  [O-VA]
- **Q:** Were all self-employed requirements met?
- **Defect condition:** Yes, all self-employment income requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2768
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G534 —  [O-RHS]
- **Q:** Were all self-employment income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2746, 2747
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G539 —  [O-FHA]
- **Q:** Were all self-employment income requirements met?
- **Defect condition:** Yes, all self-employment income requirements have been met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 2612
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G542 —  [O-RHS]
- **Q:** Were all social security, retirement and/or disability income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2750, 2751
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G549 —  [O-FRD/O-RHS]
- **Q:** Were all trust income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2710, 2711, 2756, 2757
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G554 —  [O-FNM]
- **Q:** Were all trust income requirements met?_x000D_
- **Defect condition:** Not applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2680, 2681
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G562 —  [O-FNM]
- **Q:** Were all unemployment income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2663, 2664
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G569 —  [O-FNM]
- **Q:** Were all verbal verification of employment requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2654, 2655
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G576 —  [O-RHS]
- **Q:** Were all wage earner income requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2732, 2733
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G580 —  [GENERIC]
- **Q:** What type of income was used to qualify the loan?
- **Defect condition:** Alimony, Child Support, Maintenance and/or Other Nontaxable Income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2581, 2582, 2583, 2584, 2585, 2586, 2587, 2588, 2589, 2590, 2591, 2592, 2593, 2594, 2595
- **Rationale:** Screening/categorization answer branch ('what type of income was used'), not a defect condition — same pattern as application-verification's LEP-applicability screening group and asset-verification's group 291.
- **SME:** [ ] agree [ ] correct: ______

