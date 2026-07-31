# SME Review Packet — asset-verification block triage

**304 rules / 297 unique (question, condition) groups.** Every classification
below is a *proposal* pending your review — mark each check agree / correct.
Bins: GREEN = automatable now · YELLOW = automatable after data/guide work ·
RED = stays human · NOT_A_CHECK = pass/N-A answer option, not a defect rule.

**Source workbook:** `PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv` — row numbers below are Excel-style
(header = row 1), so you can open the sheet and jump straight to each rule.

**Note on this block vs application-verification:** dedup collapse here is far smaller (304 rules -> 297 groups, ~1.02x, vs 81->54, ~1.5x) — the 5 AMQ agencies write almost entirely independent condition text per asset sub-type. GREEN/NOT_A_CHECK for the ~87 mechanically-resolvable groups are derived directly from amq_compiler.py's own eval_class and a pass/N-A regex, not hand-typed; the ~210 substantive groups below are individually read and classified.

## Headline

| Bin | Groups | Rules | % of defect groups |
|---|---|---|---|
| GREEN | 18 | 18 | 8% |
| YELLOW | 193 | 193 | 85% |
| RED | 17 | 18 | 7% |
| NOT_A_CHECK | 69 | 75 | — |

## READY TO BUILD candidates (flagged, not implemented)

- **G011** (O-VA, row 226): New derivation, no new fixture: 'Borrower has a loan outstanding secured by funds on deposit and these funds were treated as an asset' (O-VA-00262) is checkable by cross-referencing entities extract_loan.py ALREADY extracts — tradelines/urla_liabilities (for the secured loan) against bank_txns (for the deposit treated as an asset) — no new document type needed, just new join logic.
- **G025** (O-FRD, row 102): Extend LargeDepositShape (CHK-AST-001)'s amq_exception_codes to O-FRD-58101 — same unsourced-large-deposit defect the shape already encodes for O-FNM-00215, FRD wording variant. Verify wording match before wiring.
- **G064** (O-FHA, row 217): Extend LargeDepositShape (CHK-AST-001)'s amq_exception_codes to O-FHA-50677-1 — same defect, FHA wording variant ('new accounts & recent deposits over 50% of adjusted income'). Verify wording match.
- **G102** (O-FRD, row 219): Extend LargeDepositShape (CHK-AST-001)'s amq_exception_codes to O-FRD-50451 — condition text is a BYTE-FOR-BYTE duplicate of the already-mapped O-FNM-00215 row (group 287), just filed under a different AMQ question category ('general asset documentation' vs 'verification of deposit assets'). Highest-confidence candidate in this batch.
- **G130** (O-RHS, row 163): Partial win now: 'Borrower received cash back at closing due to a gift of equity, sweat equity, or rent credits' (O-RHS-57768) can be cross-referenced today against cash_out_to_borrower_1003 (already extracted) + gift_transfer_evidence_in_file/gift_letter presence; a full sweat-equity/rent-credit fact still needs new fixtures, but the gift-fund half is buildable now.
- **G135** (O-RHS, row 177): WIRE, don't build — GiftEvidenceShape (CHK-AST-002) already checks exactly this fact (gift_transfer_evidence_in_file), but MAPPED_SHAPES wires it to ZERO amq_exception_codes today (amq_compiler.py: "GiftEvidenceShape": {..."amq_exception_codes": []}). O-RHS-02772 ("No, proof of transfer not provided") is a clean 1-line addition to that list — no new code, no new fixture.

## GREEN

### G042 — Bank Statements [O-FNM]
- **Q:** Were all asset verification documentation requirements met?
- **Defect condition:** The bank statements provided are incomplete and/or missing all required pages
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 107
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: bank_statement
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier (the exception text matches 'not in file/missing/not provided' and names a mappable document type already in the extraction contract) — already works.
- **Guide candidate:** A4-1-02 — Submission of Financial Statements and Reports (PDF p.158)
- **Guide candidate:** B3-2-04 — DU Documentation Requirements (PDF p.305)
- **Guide candidate:** B3-3.1-02 — Tax Return and Transcript Documentation Requirements (PDF p.320)
- **SME:** [ ] agree [ ] correct: ______

### G068 — O-RHS-54263 [O-RHS]
- **Q:** Were all checking/savings asset requirements met?
- **Defect condition:** 2 mos recent bank statements, VOD or other acceptable alternative documents not in file as req'd
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 142
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: bank_statement
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier (the exception text matches 'not in file/missing/not provided' and names a mappable document type already in the extraction contract) — already works.
- **SME:** [ ] agree [ ] correct: ______

### G077 — O-FNM-54871 [O-FNM]
- **Q:** Were all credit card financing and rewards points asset requirements met?
- **Defect condition:** Credit card points not in borr acct & cash value verification & conversion to cash PTC not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 135
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: bank_statement
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier (the exception text matches 'not in file/missing/not provided' and names a mappable document type already in the extraction contract) — already works.
- **Guide candidate:** B3-4.3-16 — Credit Card Financing and Reward Points (PDF p.459)
- **Guide candidate:** B3-4.3-19 — Cash Value of Life Insurance (PDF p.462)
- **Guide candidate:** B5-3.1-01 — Conversion of Construction-to-Permanent Financing: Overview (PDF p.735)
- **SME:** [ ] agree [ ] correct: ______

### G094 — O-FRD-00209 [O-FRD]
- **Q:** Were all general asset documentation requirements met?
- **Defect condition:** A VOD or bank statement for the most recent 2 months, or 1 month if streamlined, was not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 141
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: bank_statement
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier (the exception text matches 'not in file/missing/not provided' and names a mappable document type already in the extraction contract) — already works.
- **SME:** [ ] agree [ ] correct: ______

### G114 — O-FNM-00234 [O-FNM]
- **Q:** Were all gift and/or grant asset requirements met?
- **Defect condition:** The gift letter was not in the file or was unsigned and/or all required information not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 181
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: gift_letter
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier (the exception text matches 'not in file/missing/not provided' and names a mappable document type already in the extraction contract) — already works.
- **Guide candidate:** A2-2-02 — Delivery Information and Delivery-Option Speciﬁc Representations and Warranties (PDF p.34)
- **Guide candidate:** A3-4-01 — Conﬁdentiality of Information (PDF p.137)
- **Guide candidate:** B3-2-01 — General Information on DU (PDF p.287)
- **SME:** [ ] agree [ ] correct: ______

### G123 — O-FRD-00231 [O-FRD]
- **Q:** Were all gift and/or grant fund requirements met?
- **Defect condition:** No, gift letter with all the required information not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 182
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: gift_letter
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier (the exception text matches 'not in file/missing/not provided' and names a mappable document type already in the extraction contract) — already works.
- **SME:** [ ] agree [ ] correct: ______

### G134 — O-RHS-02771 [O-RHS]
- **Q:** Were all gift asset requirements met?
- **Defect condition:** No, gift letter did not state if the gift funds had to be repaid
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 183
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: gift_letter
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier (the exception text matches 'not in file/missing/not provided' and names a mappable document type already in the extraction contract) — already works.
- **SME:** [ ] agree [ ] correct: ______

### G139 — O-FHA-54061 [O-FHA]
- **Q:** Were all gifts requirements met?
- **Defect condition:** Gift xfer to closing agent payment source & donor bank statement evidencing ability not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 193
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: bank_statement
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier (the exception text matches 'not in file/missing/not provided' and names a mappable document type already in the extraction contract) — already works.
- **SME:** [ ] agree [ ] correct: ______

### G140 — O-FHA-02257 [O-FHA]
- **Q:** Were all gifts requirements met?
- **Defect condition:** Signed and dated gift letter not in the file or the letter did not include all required information
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 180
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: gift_letter
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier (the exception text matches 'not in file/missing/not provided' and names a mappable document type already in the extraction contract) — already works.
- **SME:** [ ] agree [ ] correct: ______

### G170 — O-FRD-00265 [O-FRD]
- **Q:** Were all liquidation or sale of asset requirements met?
- **Defect condition:** Missing settlement/closing disclosure statement evidencing proceeds from the sale of real property
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 288
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: closing_disclosure
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier (the exception text matches 'not in file/missing/not provided' and names a mappable document type already in the extraction contract) — already works.
- **SME:** [ ] agree [ ] correct: ______

### G181 — O-RHS-54267 [O-RHS]
- **Q:** Were all net proceeds asset requirements met?
- **Defect condition:** Closing disclosure documenting net proceeds not provided for sale of property
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 247
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: closing_disclosure
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier (the exception text matches 'not in file/missing/not provided' and names a mappable document type already in the extraction contract) — already works.
- **SME:** [ ] agree [ ] correct: ______

### G189 — O-RHS-51019 [O-RHS]
- **Q:** Were all other asset requirements met?
- **Defect condition:** 2 CD stmt not provided, early w/draw penalty not given &/or less of 2 mo avg or current bal not used
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 125
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: closing_disclosure
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier (the exception text matches 'not in file/missing/not provided' and names a mappable document type already in the extraction contract) — already works.
- **SME:** [ ] agree [ ] correct: ______

### G226 — O-FRD-50455 [O-FRD]
- **Q:** Were all real estate commission requirements met?
- **Defect condition:** Closing Disclosure Stmt or credit toward mtg where borr is RE agent getting commission not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 114
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: closing_disclosure
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier (the exception text matches 'not in file/missing/not provided' and names a mappable document type already in the extraction contract) — already works.
- **SME:** [ ] agree [ ] correct: ______

### G232 — O-FNM-55670 [O-FNM]
- **Q:** Were all rent credit for option to purchase asset requirements met?
- **Defect condition:** Rent credit for option to purchase canceled checks/money order receipts for last 12 mos not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 260
- **Severity:** Major
- **Machine checks:** auto-compiled doc-presence check on: bank_statement
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier (the exception text matches 'not in file/missing/not provided' and names a mappable document type already in the extraction contract) — already works.
- **Guide candidate:** A2-2-02 — Delivery Information and Delivery-Option Speciﬁc Representations and Warranties (PDF p.34)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B2-1.3-01 — Purchase Transactions (PDF p.188)
- **SME:** [ ] agree [ ] correct: ______

### G285 — O-FNM-54872 [O-FNM]
- **Q:** Were all verification of deposit assets requirements met?
- **Defect condition:** LCO or CO refinance missing the last 1 month of bank or investment portfolio statements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 253
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: bank_statement
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier (the exception text matches 'not in file/missing/not provided' and names a mappable document type already in the extraction contract) — already works.
- **Guide candidate:** A4-1-02 — Submission of Financial Statements and Reports (PDF p.158)
- **Guide candidate:** B3-3.4-06 — Employment Related Assets as Qualifying Income (PDF p.358)
- **Guide candidate:** B3-3.7-04 — Analyzing Proﬁt and Loss Statements (PDF p.405)
- **SME:** [ ] agree [ ] correct: ______

### G287 — O-FNM-00215 [O-FNM]
- **Q:** Were all verification of deposit assets requirements met?
- **Defect condition:** Source of unknown deposit exceeding 50% of qualifying income not documented &/or account not reduced
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 218
- **Severity:** Critical
- **Machine checks:** already-mapped SHACL shape: LargeDepositShape
- **Rationale:** ALREADY BUILT: LargeDepositShape (see blocks/assets.ttl).
- **Guide candidate:** B3-3.4-06 — Employment Related Assets as Qualifying Income (PDF p.358)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.1-01 — General Income Information (PDF p.318)
- **SME:** [ ] agree [ ] correct: ______

### G288 — O-FNM-50256 [O-FNM]
- **Q:** Were all verification of deposit assets requirements met?
- **Defect condition:** The VOD form was incomplete or not provided direct from the depository
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 332
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: bank_statement
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier (the exception text matches 'not in file/missing/not provided' and names a mappable document type already in the extraction contract) — already works.
- **Guide candidate:** B1-1-02 — Blanket Authorization Form (PDF p.170)
- **Guide candidate:** B3-3.4-06 — Employment Related Assets as Qualifying Income (PDF p.358)
- **Guide candidate:** B3-3.6-02 — Income Reported on IRS Form 1040 (PDF p.391)
- **SME:** [ ] agree [ ] correct: ______

### G294 — O-VA-51667 [O-VA]
- **Q:** Where the transaction allows for gift funds to be used, does the file contain an acceptable gift letter and were the gift funds verified correctly?
- **Defect condition:** A signed & dated gift letter was not in the file or did not provide all required information
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 184
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: gift_letter
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier (the exception text matches 'not in file/missing/not provided' and names a mappable document type already in the extraction contract) — already works.
- **SME:** [ ] agree [ ] correct: ______

## YELLOW

### G001 — O-VA-03098 [O-VA]
- **Q:** Does the file contain sufficient asset documentation for checking/savings?
- **Defect condition:** AUS UW-VOD or last 1 month bank statements do not verify funds on deposit
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 108
- **Severity:** Critical
- **Data needed:** VOD doc type (not in any synthetic loan) or a bank_statement balance-vs-claimed-funds derivation
- **Rationale:** VA AUS-track funds-on-deposit verification; bank_statement exists in the corpus (loan 01) but a distinct VOD form does not, and no field compares statement balance to a claimed asset amount yet.
- **SME:** [ ] agree [ ] correct: ______

### G002 — O-VA-00208 [O-VA]
- **Q:** Does the file contain sufficient asset documentation for checking/savings?
- **Defect condition:** Manual UW-VOD or last 2 mos bank statements do not verify funds on deposit
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 229
- **Severity:** Critical
- **Data needed:** same as G001
- **Rationale:** Same defect as G001, Manual-UW track (2 months, not 1).
- **SME:** [ ] agree [ ] correct: ______

### G004 — O-VA-00263 [O-VA]
- **Q:** Does the file contain sufficient asset documentation for net proceeds?
- **Defect condition:** Current home sale proceeds not documented to verify sale, payoffs and sufficient net proceeds
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 248
- **Severity:** Critical
- **Data needed:** prior-home-sale settlement statement + net-proceeds field (deepen closing_disclosure)
- **Rationale:** Crisp documentation-presence check; closing_disclosure doc type exists in every loan but a distinct prior-sale settlement statement / net-proceeds field is not yet in FIELD_SPECS.
- **SME:** [ ] agree [ ] correct: ______

### G005 — O-VA-50768 [O-VA]
- **Q:** Does the file contain sufficient asset documentation for net proceeds?
- **Defect condition:** The amt of equity the applicant has accumulated for use of sale proceeds not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 289
- **Severity:** Critical
- **Data needed:** sale-proceeds equity-accumulation field, same doc gap as G004
- **Rationale:** Same net-sale-proceeds family as G004.
- **SME:** [ ] agree [ ] correct: ______

### G007 — O-VA-00260 [O-VA]
- **Q:** Does the file contain sufficient asset documentation for secondary financing?
- **Defect condition:** The loan terms of the second mortgage was not documented and/or all requirements not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 293
- **Severity:** Critical
- **Machine checks:** second-mortgage/subordinate-loan note presence
- **Stays human:** catch-all 'and/or all requirements not met'
- **Data needed:** secondary financing note doc type (not in corpus)
- **Rationale:** Presence half is crisp; the appended open-ended 'all requirements' clause stays human.
- **SME:** [ ] agree [ ] correct: ______

### G009 — O-VA-57888 [O-VA]
- **Q:** Does the file contain sufficient documentation for other assets?
- **Defect condition:** A down pymt from borr's own resources not made for the difference in sales price & reasonable value
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 292
- **Severity:** Critical
- **Data needed:** VA NOV reasonable-value + sales-price + down-payment fields (deepen va_nov/1003)
- **Rationale:** va_nov doc exists (loan 03) with nov_issue_date extracted, but not a 'reasonable value' amount field; sales-price/down-payment comparison needs new fields, not a new document.
- **SME:** [ ] agree [ ] correct: ______

### G010 — O-VA-51063 [O-VA]
- **Q:** Does the file contain sufficient documentation for other assets?
- **Defect condition:** AUS Refer-sales price exceeds NOV without funds for the difference plus closing costs being verified
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 110
- **Severity:** Critical
- **Data needed:** same fields as G009 (VA NOV reasonable value vs sales price)
- **Rationale:** Same VA reasonable-value family as G009 (AUS-Refer variant).
- **SME:** [ ] agree [ ] correct: ______

### G011 — O-VA-00262 [O-VA]
- **Q:** Does the file contain sufficient documentation for other assets?
- **Defect condition:** Borrower has a loan outstanding secured by funds on deposit and these funds were treated as an asset
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 226
- **Severity:** Critical
- **Data needed:** cross-reference of tradelines/urla_liabilities against bank_txns (new derivation, no new fixture)
- **Rationale:** READY TO BUILD candidate — see READY_TO_BUILD; both entity types this needs (tradelines, bank_txns) are already extracted for every loan.
- **READY TO BUILD:** New derivation, no new fixture: 'Borrower has a loan outstanding secured by funds on deposit and these funds were treated as an asset' (O-VA-00262) is checkable by cross-referencing entities extract_loan.py ALREADY extracts — tradelines/urla_liabilities (for the secured loan) against bank_txns (for the deposit treated as an asset) — no new document type needed, just new join logic.
- **SME:** [ ] agree [ ] correct: ______

### G013 — O-VA-00230 [O-VA]
- **Q:** Does the file contain sufficient documentation for other assets?
- **Defect condition:** HAP fee to the buyer exceeded $250 and/or all VA, property & occupancy standards were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 201
- **Severity:** Critical
- **Machine checks:** HAP fee > $250 threshold (once HAP data exists)
- **Stays human:** catch-all 'all VA, property & occupancy standards were not met'
- **Data needed:** VA Homebuyer Assistance Program (HAP) fee/agreement doc (not in corpus)
- **Rationale:** The $250 threshold is crisp math once the HAP fee is captured; the appended open-ended standards clause stays human.
- **SME:** [ ] agree [ ] correct: ______

### G015 — O-VA-51189 [O-VA]
- **Q:** Does the file contain sufficient documentation for other assets?
- **Defect condition:** Rental income was considered without the applicable amount of reserves being documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 255
- **Severity:** Critical
- **Data needed:** VA residual-income/reserves worksheet (EXPECTED_DOCS_BY_PROGRAM's residual_income_worksheet entry exists for VA but is not yet a reserves fact)
- **Rationale:** Reserves-for-rental-income is a well-defined number once the worksheet exists; no such document in any of the 5 synthetic loans today.
- **SME:** [ ] agree [ ] correct: ______

### G016 — O-VA-00229 [O-VA]
- **Q:** Does the file contain sufficient documentation for other assets?
- **Defect condition:** Sales price exceeds VA reasonable value and documentation that HAP funds are a grant not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 202
- **Severity:** Critical
- **Data needed:** same VA-reasonable-value fields as G009/G010, plus a HAP-grant field
- **Rationale:** Same reasonable-value family as G009/G010.
- **SME:** [ ] agree [ ] correct: ______

### G017 — O-VA-50767 [O-VA]
- **Q:** Does the file contain sufficient documentation for other assets?
- **Defect condition:** Sufficient assets not documented to cover closing costs & any down payment if applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 123
- **Severity:** Critical
- **Data needed:** closing-cost + down-payment + total-available-assets derivation (deepen 1003/closing_disclosure)
- **Rationale:** Generic cash-to-close sufficiency; both source docs already exist in the corpus, the derived comparison does not.
- **SME:** [ ] agree [ ] correct: ______

### G022 — O-FRD-50465 [O-FRD]
- **Q:** Were all Employer Assisted Homeownership (EAH) benefit requirements met?
- **Defect condition:** Terms of Employer Assisted Homeownership (EAH) Benefit to borr not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 149
- **Severity:** Critical
- **Machine checks:** EAH benefit terms doc presence
- **Data needed:** Employer Assisted Homeownership benefit agreement doc type (not in corpus)
- **Rationale:** Unlike G020, this row IS a crisp presence check ('terms... not in file') — same topic, very different condition, classified independently per instructions.
- **SME:** [ ] agree [ ] correct: ______

### G025 — O-FRD-58101 [O-FRD]
- **Q:** Were all additional general asset documentation requirements met?_x000D_
- **Defect condition:** Large deposit not from the borr's income, acceptable funds awarded to the borr, or eligible asset
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 102
- **Severity:** Critical
- **Machine checks:** unsourced-large-deposit comparison (bank_txns credit_amount vs base_monthly_income_1003)
- **Data needed:** none if wired — see READY_TO_BUILD
- **Rationale:** READY TO BUILD candidate: same defect family as the already-mapped LargeDepositShape (O-FNM-00215) — FRD wording variant.
- **READY TO BUILD:** Extend LargeDepositShape (CHK-AST-001)'s amq_exception_codes to O-FRD-58101 — same unsourced-large-deposit defect the shape already encodes for O-FNM-00215, FRD wording variant. Verify wording match before wiring.
- **SME:** [ ] agree [ ] correct: ______

### G027 — O-FRD-56007 [O-FRD]
- **Q:** Were all additional other asset type requirements met?
- **Defect condition:** Credit card reward points were used without evidence of reward points ownership & their cash value
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 134
- **Severity:** Critical
- **Data needed:** credit-card-rewards statement (ownership + cash value), not in corpus
- **Rationale:** Crisp presence/valuation check; no such document exists in any synthetic loan.
- **SME:** [ ] agree [ ] correct: ______

### G028 — O-FRD-56008 [O-FRD]
- **Q:** Were all additional other asset type requirements met?
- **Defect condition:** No evidence credit card reward points were redeemed for cash prior to closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 136
- **Severity:** Critical
- **Data needed:** same credit-card-rewards doc gap as G027
- **Rationale:** Same family as G027 (redemption-timing variant).
- **SME:** [ ] agree [ ] correct: ______

### G030 — O-FNM-00278 [O-FNM]
- **Q:** Were all anticipated sales proceeds asset requirements met?
- **Defect condition:** Anticipated sale proceeds calculated incorrectly for an owned home listed for sale but not yet sold
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 103
- **Severity:** Critical
- **Data needed:** home-sale listing/contract doc (not in corpus)
- **Rationale:** Sale-proceeds calculation is deterministic math once the listing/contract exists; it doesn't today.
- **Guide candidate:** B3-4.3-10 — Anticipated Sales Proceeds (PDF p.453)
- **Guide candidate:** B2-1.2-03 — Home Equity Combined Loan-to-Value (HCLTV) Ratios (PDF p.182)
- **Guide candidate:** B3-4.3-15 — Borrowed Funds Secured by an Asset (PDF p.458)
- **SME:** [ ] agree [ ] correct: ______

### G031 — O-FNM-51040 [O-FNM]
- **Q:** Were all anticipated sales proceeds asset requirements met?
- **Defect condition:** Like-kind/1031 exchange assets not documented or not compliant with Internal Revenue Code Sect 1031
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 225
- **Severity:** Critical
- **Stays human:** IRC Section 1031 compliance determination
- **Data needed:** 1031-exchange documentation (not in corpus)
- **Rationale:** Presence is checkable once the doc exists; full IRC compliance stays a judgment call layered on top.
- **Guide candidate:** B3-4.3-10 — Anticipated Sales Proceeds (PDF p.453)
- **Guide candidate:** B3-3.4-06 — Employment Related Assets as Qualifying Income (PDF p.358)
- **Guide candidate:** B3-4.2-01 — Veriﬁcation of Deposits and Assets (PDF p.430)
- **SME:** [ ] agree [ ] correct: ______

### G033 — O-FNM-51039 [O-FNM]
- **Q:** Were all anticipated sales proceeds asset requirements met?
- **Defect condition:** Settlement statement documenting sufficient net cash proceeds from a property sale not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 287
- **Severity:** Critical
- **Data needed:** prior-sale settlement statement (distinct from this loan's closing_disclosure)
- **Rationale:** Same net-cash-proceeds-from-a-prior-sale family as G004/G033.
- **Guide candidate:** B3-4.3-10 — Anticipated Sales Proceeds (PDF p.453)
- **Guide candidate:** B3-4.3-20 — Anticipated Savings and Cash-on-Hand (PDF p.463)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **SME:** [ ] agree [ ] correct: ______

### G034 — O-FNM-51041 [O-FNM]
- **Q:** Were all anticipated sales proceeds asset requirements met?
- **Defect condition:** Signed employee relocation buy-out agreement not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 159
- **Severity:** Critical
- **Data needed:** employee relocation buy-out agreement (not in corpus)
- **Rationale:** Crisp doc-presence check; niche document, absent from all 5 synthetic loans.
- **Guide candidate:** B3-4.3-10 — Anticipated Sales Proceeds (PDF p.453)
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **Guide candidate:** B2-1.3-03 — Cash-Out Reﬁnance Transactions (PDF p.197)
- **SME:** [ ] agree [ ] correct: ______

### G037 — DUAssets [O-FNM]
- **Q:** Were all asset verification documentation requirements met?
- **Defect condition:** All assets were not submitted to DU correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 147
- **Severity:** Critical
- **Data needed:** DU (Fannie Mae AUS) findings report, not in corpus
- **Rationale:** This pilot has no AUS-submission export at all for FNM (the RHS-equivalent, GUS findings, IS already partially extracted for loan 05 — a natural next fixture, not built here).
- **Guide candidate:** B3-2-04 — DU Documentation Requirements (PDF p.305)
- **Guide candidate:** B3-3.1-02 — Tax Return and Transcript Documentation Requirements (PDF p.320)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **SME:** [ ] agree [ ] correct: ______

### G038 — O-FNM-56339 [O-FNM]
- **Q:** Were all asset verification documentation requirements met?
- **Defect condition:** Borr was own realtor & the earned commission not on settlement stmt as a credit towards the mtg loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 151
- **Severity:** Major
- **Data needed:** realtor-commission-as-credit field on closing_disclosure (deepen extraction)
- **Rationale:** closing_disclosure exists in every loan; the specific credit-line field does not yet — Bucket-B-style (no new fixture).
- **Guide candidate:** B3-4.3-21 — Borrower's Earned Real Estate Commission (PDF p.464)
- **Guide candidate:** B3-5.1-02 — Determining the Credit Score for a Mortgage Loan (PDF p.474)
- **Guide candidate:** B3-5.4-03 — Documentation and Assessment of a Nontraditional Credit History (PDF p.509)
- **SME:** [ ] agree [ ] correct: ______

### G039 — O-FNM-00217 [O-FNM]
- **Q:** Were all asset verification documentation requirements met?
- **Defect condition:** Depository assets were not documented as per DU
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 143
- **Severity:** Critical
- **Data needed:** same DU-findings gap as G037
- **Rationale:** Same DU-submission family as G037.
- **Guide candidate:** B3-2-04 — DU Documentation Requirements (PDF p.305)
- **Guide candidate:** B3-3.1-02 — Tax Return and Transcript Documentation Requirements (PDF p.320)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **SME:** [ ] agree [ ] correct: ______

### G040 — O-FNM-00218 [O-FNM]
- **Q:** Were all asset verification documentation requirements met?
- **Defect condition:** Earnest money deposit not entered correctly in DU based on if EMD cleared the borr's bank account
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 157
- **Severity:** Critical
- **Data needed:** EMD amount field (1003/purchase contract) cross-referenced against bank_txns debit — same as G081
- **Rationale:** Duplicate condition text to G081 filed under a different AMQ question category (same pattern as G102/G287); both need a new EMD-amount field, not a new fixture.
- **Guide candidate:** B3-4.3-09 — Earnest Money Deposit (PDF p.452)
- **Guide candidate:** B3-2-04 — DU Documentation Requirements (PDF p.305)
- **Guide candidate:** B3-3.1-02 — Tax Return and Transcript Documentation Requirements (PDF p.320)
- **SME:** [ ] agree [ ] correct: ______

### G043 — O-FNM-55916 [O-FNM]
- **Q:** Were all asset verification documentation requirements met?
- **Defect condition:** The loan file did not document sufficient funds for closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 304
- **Severity:** Critical
- **Data needed:** total-closing-funds-needed vs total-assets-available derivation
- **Rationale:** Generic sufficiency check, same family as G073/G103.
- **Guide candidate:** B3-4.3-15 — Borrowed Funds Secured by an Asset (PDF p.458)
- **Guide candidate:** B5-4.1-03 — Texas Section 50(a)(6) Loan Underwriting, Collateral, and Closing Considerations (PDF p.773)
- **Guide candidate:** B5-7-02 — High LTV Reﬁnance Underwriting, Documentation, and Collateral Requirements for the New Loan (PDF p.824)
- **SME:** [ ] agree [ ] correct: ______

### G044 — O-FNM-55675 [O-FNM]
- **Q:** Were all asset verification documentation requirements met?
- **Defect condition:** Virtual currency used as a source of funds was not verified in U.S. dollars prior to closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 331
- **Severity:** Critical
- **Data needed:** cryptocurrency-to-USD exchange confirmation (not in corpus)
- **Rationale:** Same virtual-currency family as G174/G200/G201/G205/G213.
- **Guide candidate:** B3-4.1-04 — Virtual Currency (PDF p.429)
- **Guide candidate:** B3-4.3-15 — Borrowed Funds Secured by an Asset (PDF p.458)
- **Guide candidate:** B3-6-07 — Debts Paid Oﬀ At or Prior to Closing (PDF p.531)
- **SME:** [ ] agree [ ] correct: ______

### G045 — O-FNM-00279 [O-FNM]
- **Q:** Were all borrowed funds secured by an asset requirements met?
- **Defect condition:** Loan proceeds for cash to close without file documenting loan terms and that it is a secured loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 113
- **Severity:** Critical
- **Data needed:** personal/secured loan note (not in corpus)
- **Rationale:** Crisp doc-presence check once the note exists; no such document in any loan today.
- **Guide candidate:** B3-4.3-15 — Borrowed Funds Secured by an Asset (PDF p.458)
- **Guide candidate:** C2-2-04 — Timing of Distribution of Whole Loan Purchase Proceeds (PDF p.986)
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **SME:** [ ] agree [ ] correct: ______

### G047 — O-FNM-00282 [O-FNM]
- **Q:** Were all bridge/swing loan asset requirements met?
- **Defect condition:** Ability to make payments on the new & current home, bridge/swing loan & other debts not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 118
- **Severity:** Critical
- **Data needed:** bridge/swing loan payment-ability worksheet (not in corpus)
- **Rationale:** Same bridge-loan family as G049/G198/G263.
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** B2-1.2-03 — Home Equity Combined Loan-to-Value (HCLTV) Ratios (PDF p.182)
- **Guide candidate:** B3-4.3-14 — Bridge/Swing Loans (PDF p.458)
- **SME:** [ ] agree [ ] correct: ______

### G049 — O-FNM-56360 [O-FNM]
- **Q:** Were all bridge/swing loan asset requirements met?
- **Defect condition:** The bridge loan was cross-collateralized against the new property
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 138
- **Severity:** Critical
- **Data needed:** bridge loan security instrument (not in corpus)
- **Rationale:** Same bridge-loan family as G047.
- **Guide candidate:** B3-4.3-14 — Bridge/Swing Loans (PDF p.458)
- **Guide candidate:** B5-7-02 — High LTV Reﬁnance Underwriting, Documentation, and Collateral Requirements for the New Loan (PDF p.824)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **SME:** [ ] agree [ ] correct: ______

### G050 — O-RHS-51018 [O-RHS]
- **Q:** Were all business account asset requirements met?
- **Defect condition:** 2 mo balance avg not provided for a business account or lower of the 2 mo avg/current bal not used
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 119
- **Severity:** Critical
- **Data needed:** business-account-type flag + 2-month-average-balance derivation (deepen bank_statement)
- **Rationale:** bank_statement doc exists generically, but neither business-vs-personal account classification nor a multi-month average is modeled today.
- **SME:** [ ] agree [ ] correct: ______

### G051 — O-FNM-52793 [O-FNM]
- **Q:** Were all business account asset requirements met?
- **Defect condition:** Business assets used as assets to close and the borrower is not listed as an owner of the account
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 238
- **Severity:** Critical
- **Data needed:** account-ownership field on bank_statement (not currently captured)
- **Rationale:** Same business-account family as G050/G052/G053.
- **Guide candidate:** B2-2-01 — General Borrower Eligibility Requirements (PDF p.241)
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **Guide candidate:** B2-2-03 — Multiple Financed Properties for the Same Borrower (PDF p.244)
- **SME:** [ ] agree [ ] correct: ______

### G052 — O-FNM-02212 [O-FNM]
- **Q:** Were all business account asset requirements met?
- **Defect condition:** Business assets used as down payment, closing costs or reserves & a cash flow analysis not completed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 120
- **Severity:** Critical
- **Data needed:** cash-flow-analysis worksheet (not in corpus)
- **Rationale:** Same business-account family as G050/G051.
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **Guide candidate:** B2-1.3-03 — Cash-Out Reﬁnance Transactions (PDF p.197)
- **Guide candidate:** B3-3.4-06 — Employment Related Assets as Qualifying Income (PDF p.358)
- **SME:** [ ] agree [ ] correct: ______

### G057 — O-FHA-54828 [O-FHA]
- **Q:** Were all cash to close requirements met?
- **Defect condition:** Borr assets insufficient to meet MRI, closing costs/prepaids without seller real estate tax credit
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 249
- **Severity:** Critical
- **Data needed:** MRI + closing-costs/prepaids + seller-tax-credit fields (deepen 1003/closing_disclosure)
- **Rationale:** Compound cash-to-close math; every source doc exists in the corpus, the specific derived comparison does not.
- **SME:** [ ] agree [ ] correct: ______

### G060 — O-FHA-55918 [O-FHA]
- **Q:** Were all cash to close requirements met?
- **Defect condition:** Qualifying borr did not do landlord education or 1 yr landlord experience using ADU rental income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 302, 303
- **Severity:** Critical
- **Data needed:** landlord education certificate / experience documentation (not in corpus)
- **Rationale:** Crisp presence/duration check once the document exists.
- **SME:** [ ] agree [ ] correct: ______

### G061 — O-FHA-00600 [O-FHA]
- **Q:** Were all cash to close requirements met?
- **Defect condition:** The funds derived from the premium pricing were not used to reduce the principal balance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 244
- **Severity:** Critical
- **Data needed:** premium-pricing-credit-application field (deepen closing_disclosure)
- **Rationale:** closing_disclosure exists in every loan; the specific credit-application field does not yet — related to G162.
- **SME:** [ ] agree [ ] correct: ______

### G062 — O-FNM-00280 [O-FNM]
- **Q:** Were all cash value of life insurance asset requirements met?
- **Defect condition:** Cash value loan/surrender of life insurance used without documenting repayment and receipt of funds
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 124
- **Severity:** Critical
- **Data needed:** life insurance policy/surrender statement (not in corpus)
- **Rationale:** Same life-insurance family as G167.
- **Guide candidate:** B3-4.3-19 — Cash Value of Life Insurance (PDF p.462)
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **Guide candidate:** B2-1.2-01 — Loan-to-Value (LTV) Ratios (PDF p.179)
- **SME:** [ ] agree [ ] correct: ______

### G064 — O-FHA-50677-1 [O-FHA]
- **Q:** Were all checking and savings account requirements met?
- **Defect condition:** Source of funds for new accounts & recent deposits over 50% of adjusted income not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 217
- **Severity:** Critical
- **Machine checks:** unsourced-large-deposit comparison (same logic as G025/G102)
- **Data needed:** none if wired — see READY_TO_BUILD
- **Rationale:** READY TO BUILD candidate: FHA wording variant of the already-mapped LargeDepositShape defect.
- **READY TO BUILD:** Extend LargeDepositShape (CHK-AST-001)'s amq_exception_codes to O-FHA-50677-1 — same defect, FHA wording variant ('new accounts & recent deposits over 50% of adjusted income'). Verify wording match.
- **SME:** [ ] agree [ ] correct: ______

### G065 — O-FHA-51276 [O-FHA]
- **Q:** Were all checking and savings account requirements met?
- **Defect condition:** TPV of assets did not cover the last month & data not current w/in 30 days of the verification
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 309
- **Severity:** Critical
- **Data needed:** Third Party Verification (TPV) report doc (not in corpus)
- **Rationale:** Crisp 30-day-currency check once the TPV report exists as a document type.
- **SME:** [ ] agree [ ] correct: ______

### G066 — O-FHA-02251 [O-FHA]
- **Q:** Were all checking and savings account requirements met?
- **Defect condition:** The existence of & amounts in the borrower’s checking and savings accounts not verified & documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 126, 127, 128
- **Severity:** Critical
- **Data needed:** aggregate 'current balance' fact derived from bank_txns (deepen extraction)
- **Rationale:** bank_statement/bank_txns already extract a running balance column; a simple most-recent-balance derivation would make this near-ready — flagged as a secondary READY-TO-BUILD-adjacent candidate, not implemented here.
- **SME:** [ ] agree [ ] correct: ______

### G069 — O-RHS-57143 [O-RHS]
- **Q:** Were all checking/savings asset requirements met?
- **Defect condition:** It was not ensured assets entered into GUS as reserves were available to the applicants post-closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 111
- **Severity:** Critical
- **Data needed:** reserves field on gus_findings (deepen extraction — doc exists for loan 05, field does not)
- **Rationale:** GUS findings doc type is already parsed for USDA loans (usda_income_limit, usda_adjusted_household_income); a post-closing-reserves field is not yet in FIELD_SPECS['gus_findings'] — Bucket-B-style, no new fixture.
- **SME:** [ ] agree [ ] correct: ______

### G070 — O-RHS-54265 [O-RHS]
- **Q:** Were all checking/savings asset requirements met?
- **Defect condition:** Lesser of current balance or previous month’s ending balance not used for required reserves
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 263
- **Severity:** Critical
- **Data needed:** multi-statement balance comparison (deepen bank_statement, or a 2nd month's fixture)
- **Rationale:** Needs either a second month's bank statement (each loan currently has one) or a running-balance derivation from the one statement in hand.
- **SME:** [ ] agree [ ] correct: ______

### G071 — O-RHS-02769 [O-RHS]
- **Q:** Were all checking/savings asset requirements met?
- **Defect condition:** No, asset documentation not reviewed by lender for recent large or unusual deposits
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 252
- **Severity:** Critical
- **Data needed:** lender-review-completed flag (not currently modeled)
- **Rationale:** Related to, but not identical to, the large-deposit family (G025/G064/G102/G287) — this asks whether the LENDER reviewed for large/unusual deposits (a process fact), not a specific dollar threshold, so it is not a blind extension of LargeDepositShape.
- **SME:** [ ] agree [ ] correct: ______

### G072 — O-RHS-55578 [O-RHS]
- **Q:** Were all checking/savings asset requirements met?
- **Defect condition:** Non-payroll deposits were not confirmed as not being from undisclosed income sources
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 235
- **Severity:** Critical
- **Data needed:** payroll-vs-non-payroll deposit classification (deepen bank_txns)
- **Rationale:** bank_txns already extracts each transaction; a payroll/non-payroll categorization does not exist yet.
- **SME:** [ ] agree [ ] correct: ______

### G073 — O-RHS-54264 [O-RHS]
- **Q:** Were all checking/savings asset requirements met?
- **Defect condition:** Sufficient funds for closing were not documented in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 306
- **Severity:** Critical
- **Data needed:** same sufficiency derivation as G043/G103
- **Rationale:** Same generic-sufficiency family as G043.
- **SME:** [ ] agree [ ] correct: ______

### G075 — O-FNM-00290 [O-FNM]
- **Q:** Were all credit card financing and rewards points asset requirements met?
- **Defect condition:** Common customary costs paid by the borr outside of closing on credit card exceeds 2% of the loan amt
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 132
- **Severity:** Major
- **Data needed:** credit-card-paid-costs field + loan-amount comparison (2% threshold; deepen closing_disclosure/1003)
- **Rationale:** Crisp 2% threshold math once the specific field exists; not modeled today.
- **Guide candidate:** B3-4.3-16 — Credit Card Financing and Reward Points (PDF p.459)
- **Guide candidate:** B3-5.1-02 — Determining the Credit Score for a Mortgage Loan (PDF p.474)
- **Guide candidate:** B3-6-07 — Debts Paid Oﬀ At or Prior to Closing (PDF p.531)
- **SME:** [ ] agree [ ] correct: ______

### G076 — O-FNM-55108 [O-FNM]
- **Q:** Were all credit card financing and rewards points asset requirements met?
- **Defect condition:** Credit card points converted to cash qualify as a large deposit missing source as credit card reward
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 133
- **Severity:** Critical
- **Data needed:** credit-card-reward-conversion sourcing doc (not in corpus)
- **Rationale:** Related to the large-deposit family but needs a credit-card-specific sourcing document, not present.
- **Guide candidate:** B3-4.3-16 — Credit Card Financing and Reward Points (PDF p.459)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B2-1.2-04 — Subordinate Financing (PDF p.184)
- **SME:** [ ] agree [ ] correct: ______

### G079 — O-FHA-02260 [O-FHA]
- **Q:** Were all down payment assistance programs requirements met?
- **Defect condition:** File did not document the charitable organization providing the down payment assistance is a 501c
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 146
- **Severity:** Critical
- **Stays human:** 'is a 501c' determination
- **Data needed:** charitable-org / DPA-program documentation (IRS determination letter; not in corpus)
- **Rationale:** Usually evidenced by a document (not a live registry, unlike NMLS) — kept YELLOW, but flagged as a borderline candidate worth a second look before ruling out Bucket C entirely if no such letter is ever produced in practice.
- **SME:** [ ] agree [ ] correct: ______

### G081 — O-FNM-00218 [O-FNM]
- **Q:** Were all earnest money deposit asset requirements met?
- **Defect condition:** Earnest money deposit not entered correctly in DU based on if EMD cleared the borr's bank account
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 154, 155, 156
- **Severity:** Critical
- **Data needed:** same as G040 (duplicate condition, different AMQ question category)
- **Rationale:** Duplicate condition text to G040.
- **Guide candidate:** B3-4.3-09 — Earnest Money Deposit (PDF p.452)
- **Guide candidate:** B3-4.3-15 — Borrowed Funds Secured by an Asset (PDF p.458)
- **Guide candidate:** B3-4.4-01 — DU Asset Veriﬁcation (PDF p.465)
- **SME:** [ ] agree [ ] correct: ______

### G082 — O-RHS-02777 [O-RHS]
- **Q:** Were all earnest money deposit asset requirements met?
- **Defect condition:** No, verification of earnest money on sales contract not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 158
- **Severity:** Critical
- **Data needed:** purchase/sales contract document (not present as a doc type in any synthetic loan)
- **Rationale:** Notable systemic gap: NO purchase contract document exists in any of the 5 synthetic loans — several EMD-family rules (G040/G081/G084/G086) trace back to this same missing document.
- **SME:** [ ] agree [ ] correct: ______

### G084 — O-FRD-00212 [O-FRD]
- **Q:** Were all earnest money deposit requirements met?
- **Defect condition:** No evidence earnest money deposit cleared the borr's account or written statement verifying receipt
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 152
- **Severity:** Critical
- **Data needed:** EMD amount field cross-referenced against bank_txns debit (deepen extraction)
- **Rationale:** Same EMD-clearing family as G040/G081; bank_statement doc exists, EMD-amount field does not.
- **SME:** [ ] agree [ ] correct: ______

### G086 — O-FHA-02247 [O-FHA]
- **Q:** Were all earnest money deposit requirements met?
- **Defect condition:** The EMD exceeded 1% or is deemed excessive without the source being documented and verified
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 153
- **Severity:** Critical
- **Data needed:** EMD amount + sales price fields (1% threshold; deepen 1003/contract)
- **Rationale:** Crisp 1% threshold math once fields exist; same EMD family as G084.
- **SME:** [ ] agree [ ] correct: ______

### G088 — O-FNM-00281 [O-FNM]
- **Q:** Were all employer assistance asset requirements met?
- **Defect condition:** Employer financing provided without the file documenting that the terms meet FNMA req’s
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 161
- **Severity:** Critical
- **Stays human:** 'meets FNMA req's' guideline-compliance judgment
- **Data needed:** employer-financing agreement doc (not in corpus)
- **Rationale:** Presence is crisp; full guideline-compliance determination stays partly human.
- **Guide candidate:** B3-4.3-08 — Employer Assistance (PDF p.450)
- **Guide candidate:** B2-1.2-04 — Subordinate Financing (PDF p.184)
- **Guide candidate:** B3-3.4-12 — Public Assistance Income (PDF p.368)
- **SME:** [ ] agree [ ] correct: ______

### G090 — O-FHA-02265 [O-FHA]
- **Q:** Were all employer assistance benefits requirements met?
- **Defect condition:** Employer assistance used for cash to close without verifying & documenting receipt of the assistance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 160
- **Severity:** Critical
- **Data needed:** employer-assistance award/receipt doc (not in corpus)
- **Rationale:** Crisp presence/receipt check once the document exists.
- **SME:** [ ] agree [ ] correct: ______

### G092 — O-FRD-50462 [O-FRD]
- **Q:** Were all foreign fund requirements met?
- **Defect condition:** Foreign funds were not verified in US dollars prior to closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 174
- **Severity:** Critical
- **Data needed:** foreign-currency exchange confirmation (not in corpus)
- **Rationale:** Same foreign-funds family as G191/G192/G200/G201/G205.
- **SME:** [ ] agree [ ] correct: ______

### G095 — LPA-Assets [O-FRD]
- **Q:** Were all general asset documentation requirements met?
- **Defect condition:** All assets were not submitted to LPA correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 228
- **Severity:** Critical
- **Data needed:** LPA (Freddie Mac AUS) findings report, not in corpus
- **Rationale:** Same AUS-submission gap as G037/G039 (Fannie's DU) — neither AUS export exists in this pilot; RHS's GUS is the only AUS output currently parsed.
- **SME:** [ ] agree [ ] correct: ______

### G096 — O-FRD-52177 [O-FRD]
- **Q:** Were all general asset documentation requirements met?
- **Defect condition:** All req'd info not on asset internet printout downloaded by borrower or financial institution rep
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 216
- **Severity:** Critical
- **Data needed:** asset-internet-printout document (distinct alt-doc type, not in corpus)
- **Rationale:** Crisp completeness check once the specific alt-document format exists.
- **SME:** [ ] agree [ ] correct: ______

### G097 — O-FRD-50450 [O-FRD]
- **Q:** Were all general asset documentation requirements met?
- **Defect condition:** All required information not provided on standard VOD
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 203
- **Severity:** Critical
- **Data needed:** VOD form (distinct from bank_statement; not in corpus)
- **Rationale:** Same VOD-family gap as G001/G002/G105/G256/G257/G286.
- **SME:** [ ] agree [ ] correct: ______

### G099 — O-FRD-50452 [O-FRD]
- **Q:** Were all general asset documentation requirements met?
- **Defect condition:** Minimum contribution not met or not from borrower's own personal funds
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 234
- **Severity:** Critical
- **Data needed:** minimum-contribution + fund-source fields (deepen 1003/closing_disclosure)
- **Rationale:** Crisp comparison once fields exist; doc already in the corpus.
- **SME:** [ ] agree [ ] correct: ______

### G100 — O-FRD-00211 [O-FRD]
- **Q:** Were all general asset documentation requirements met?
- **Defect condition:** New acct within 90 days - documentation verifying funds were from an acceptable source not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 251
- **Severity:** Critical
- **Data needed:** account-open-date field (deepen bank_statement)
- **Rationale:** bank_statement exists; a distinct account-open-date fact (for the 90-day test) does not.
- **SME:** [ ] agree [ ] correct: ______

### G102 — O-FRD-50451 [O-FRD]
- **Q:** Were all general asset documentation requirements met?
- **Defect condition:** Source of unknown deposit exceeding 50% of qualifying income not documented &/or account not reduced
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 219
- **Severity:** Critical
- **Machine checks:** unsourced-large-deposit comparison (identical text to the mapped O-FNM-00215 row)
- **Data needed:** none if wired — see READY_TO_BUILD
- **Rationale:** READY TO BUILD candidate — highest confidence: condition text is a byte-for-byte duplicate of group 287 (already mapped to LargeDepositShape), just filed under a different AMQ question category.
- **READY TO BUILD:** Extend LargeDepositShape (CHK-AST-001)'s amq_exception_codes to O-FRD-50451 — condition text is a BYTE-FOR-BYTE duplicate of the already-mapped O-FNM-00215 row (group 287), just filed under a different AMQ question category ('general asset documentation' vs 'verification of deposit assets'). Highest-confidence candidate in this batch.
- **SME:** [ ] agree [ ] correct: ______

### G103 — O-FRD-55917 [O-FRD]
- **Q:** Were all general asset documentation requirements met?
- **Defect condition:** The loan file did not document sufficient funds for closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 305
- **Severity:** Critical
- **Data needed:** same sufficiency derivation as G043/G073
- **Rationale:** Same generic-sufficiency family as G043.
- **SME:** [ ] agree [ ] correct: ______

### G104 — O-FRD-55657 [O-FRD]
- **Q:** Were all general asset documentation requirements met?
- **Defect condition:** The loan file did not include a written analysis of the asset qualification source and amount
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 335
- **Severity:** Critical
- **Data needed:** underwriter asset-analysis worksheet (not in corpus)
- **Rationale:** Crisp presence check once the document exists.
- **SME:** [ ] agree [ ] correct: ______

### G105 — O-FRD-54341 [O-FRD]
- **Q:** Were all general asset documentation requirements met?
- **Defect condition:** Third-party asset verif did not identify the account with minimum of last 2 digits of account number
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 311
- **Severity:** Critical
- **Data needed:** same VOD-format detail gap as G097
- **Rationale:** Same VOD family as G097.
- **SME:** [ ] agree [ ] correct: ______

### G107 — O-FNM-53864 [O-FNM]
- **Q:** Were all gift and/or grant asset requirements met?
- **Defect condition:** A gift of equity was used as financial reserves
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 188
- **Severity:** Critical
- **Data needed:** gift-of-equity/reserves designation field (deepen gift_letter)
- **Rationale:** gift_letter doc exists (loan 02); a distinct equity-vs-cash + reserves-use field does not yet — Bucket-B-style, no new fixture.
- **Guide candidate:** A4-1-02 — Submission of Financial Statements and Reports (PDF p.158)
- **Guide candidate:** B2-1.2-03 — Home Equity Combined Loan-to-Value (HCLTV) Ratios (PDF p.182)
- **Guide candidate:** B3-4.3-05 — Gifts of Equity (PDF p.445)
- **SME:** [ ] agree [ ] correct: ______

### G108 — O-FNM-00235 [O-FNM]
- **Q:** Were all gift and/or grant asset requirements met?
- **Defect condition:** Donor ability &/or the gift transfer to the borr’s account or to the closing agent not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 315
- **Severity:** Critical
- **Data needed:** donor-ability + transfer-method fields (deepen gift_letter)
- **Rationale:** Plausible near-relative of the gift_transfer_evidence_in_file fact GiftEvidenceShape already checks, but bundles an extra 'donor ability' clause the existing boolean may not cover — worth SME review before wiring, not a blind copy of G135's fix.
- **Guide candidate:** B3-4.3-15 — Borrowed Funds Secured by an Asset (PDF p.458)
- **Guide candidate:** B3-4.4-01 — DU Asset Veriﬁcation (PDF p.465)
- **Guide candidate:** B3-6-07 — Debts Paid Oﬀ At or Prior to Closing (PDF p.531)
- **SME:** [ ] agree [ ] correct: ______

### G109 — O-FNM-00240 [O-FNM]
- **Q:** Were all gift and/or grant asset requirements met?
- **Defect condition:** Gift funds were not entered correctly into DU and/or they were not identified separately as a gift
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 148
- **Severity:** Critical
- **Data needed:** same DU-submission gap as G037, plus a gift-identification flag
- **Rationale:** DU-family gap, same as G037/G039.
- **Guide candidate:** B3-4.3-15 — Borrowed Funds Secured by an Asset (PDF p.458)
- **Guide candidate:** B3-4.2-04 — Pooled Savings (Community Savings Funds) (PDF p.438)
- **Guide candidate:** B3-4.3-01 — Stocks, Stock Options, Bonds, and Mutual Funds (PDF p.439)
- **SME:** [ ] agree [ ] correct: ______

### G110 — O-FNM-51037 [O-FNM]
- **Q:** Were all gift and/or grant asset requirements met?
- **Defect condition:** Gift funds/gift of equity were received from an unacceptable donor
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 324
- **Severity:** Critical
- **Stays human:** donor-acceptability guideline judgment
- **Data needed:** donor-relationship field (deepen gift_letter)
- **Rationale:** Presence of a stated donor/relationship is crisp; whether that relationship is 'acceptable' per guide stays partly human.
- **Guide candidate:** B3-4.3-15 — Borrowed Funds Secured by an Asset (PDF p.458)
- **Guide candidate:** B2-1.2-03 — Home Equity Combined Loan-to-Value (HCLTV) Ratios (PDF p.182)
- **Guide candidate:** B3-4.2-04 — Pooled Savings (Community Savings Funds) (PDF p.438)
- **SME:** [ ] agree [ ] correct: ______

### G111 — O-FNM-00241 [O-FNM]
- **Q:** Were all gift and/or grant asset requirements met?
- **Defect condition:** Gift of equity not documented with a signed gift letter &/or not included on the closing statement
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 186
- **Severity:** Critical
- **Data needed:** equity amount cross-check against closing_disclosure (deepen extraction)
- **Rationale:** Both docs (gift_letter, closing_disclosure) exist in the corpus; the cross-reference field does not.
- **Guide candidate:** B2-1.2-03 — Home Equity Combined Loan-to-Value (HCLTV) Ratios (PDF p.182)
- **Guide candidate:** B3-4.3-05 — Gifts of Equity (PDF p.445)
- **Guide candidate:** B3-4.3-11 — Trade Equity (PDF p.454)
- **SME:** [ ] agree [ ] correct: ______

### G112 — O-FNM-55982 [O-FNM]
- **Q:** Were all gift and/or grant asset requirements met?
- **Defect condition:** Gift used as own funds by donor living w/ borr last 12 mos no evidence both will occupy as primary
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 191
- **Severity:** Major
- **Data needed:** co-residency/occupancy certification doc (not in corpus)
- **Rationale:** Crisp presence check once the document exists; niche, absent from all 5 loans.
- **Guide candidate:** B3-4.3-15 — Borrowed Funds Secured by an Asset (PDF p.458)
- **Guide candidate:** B3-4.2-04 — Pooled Savings (Community Savings Funds) (PDF p.438)
- **Guide candidate:** B3-4.3-01 — Stocks, Stock Options, Bonds, and Mutual Funds (PDF p.439)
- **SME:** [ ] agree [ ] correct: ______

### G113 — O-FNM-51038 [O-FNM]
- **Q:** Were all gift and/or grant asset requirements met?
- **Defect condition:** Pooled gift funds to meet down pymt req, no cert donor has lived w/ borr for 12 mos & will continue
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 242
- **Severity:** Critical
- **Data needed:** same co-residency certification gap as G112
- **Rationale:** Same family as G112 (pooled-gift-funds variant).
- **Guide candidate:** B3-4.2-04 — Pooled Savings (Community Savings Funds) (PDF p.438)
- **Guide candidate:** B3-4.3-15 — Borrowed Funds Secured by an Asset (PDF p.458)
- **Guide candidate:** B3-4.3-01 — Stocks, Stock Options, Bonds, and Mutual Funds (PDF p.439)
- **SME:** [ ] agree [ ] correct: ______

### G115 — FNM-GrantSub [O-FNM]
- **Q:** Were all gift and/or grant asset requirements met?
- **Defect condition:** The grant funds are not submitted under borrower number 1
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 198
- **Severity:** Major
- **Data needed:** DU borrower-number submission detail (AUS-family, not in corpus)
- **Rationale:** Same AUS-submission gap as G037/G039/G095.
- **Guide candidate:** B3-4.3-15 — Borrowed Funds Secured by an Asset (PDF p.458)
- **Guide candidate:** B2-2-01 — General Borrower Eligibility Requirements (PDF p.241)
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **SME:** [ ] agree [ ] correct: ______

### G116 — O-FNM-57880 [O-FNM]
- **Q:** Were all gift and/or grant asset requirements met?
- **Defect condition:** The grant funds award letter or legal agreement and transfer of funds is not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 197
- **Severity:** Major
- **Data needed:** grant award letter / legal agreement (not in corpus)
- **Rationale:** Crisp presence check once the document exists.
- **Guide candidate:** B3-4.3-15 — Borrowed Funds Secured by an Asset (PDF p.458)
- **Guide candidate:** C2-2-06 — Authorization to Transfer Funds (PDF p.989)
- **Guide candidate:** B2-1.5-03 — Legal Requirements (PDF p.236)
- **SME:** [ ] agree [ ] correct: ______

### G117 — O-FNM-00237 [O-FNM]
- **Q:** Were all gift and/or grant asset requirements met?
- **Defect condition:** The grant funds were from an unacceptable entity
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 323
- **Severity:** Critical
- **Stays human:** grant-entity acceptability judgment
- **Data needed:** grant award letter (not in corpus, same as G116)
- **Rationale:** Presence of a stated entity is crisp; guide-based acceptability stays human.
- **Guide candidate:** B3-4.3-15 — Borrowed Funds Secured by an Asset (PDF p.458)
- **Guide candidate:** B3-4.2-04 — Pooled Savings (Community Savings Funds) (PDF p.438)
- **Guide candidate:** B3-4.3-01 — Stocks, Stock Options, Bonds, and Mutual Funds (PDF p.439)
- **SME:** [ ] agree [ ] correct: ______

### G119 — O-FRD-55978 [O-FRD]
- **Q:** Were all gift and/or grant fund requirements met?
- **Defect condition:** Gift funds provided were not from an acceptable donor
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 101
- **Severity:** Critical
- **Stays human:** donor-acceptability guideline judgment
- **Data needed:** donor-relationship field (deepen gift_letter)
- **Rationale:** Same donor-acceptability family as G110 (FRD wording variant).
- **SME:** [ ] agree [ ] correct: ______

### G120 — O-FRD-50463 [O-FRD]
- **Q:** Were all gift and/or grant fund requirements met?
- **Defect condition:** Gift of equity not on the Settlement/Closing Disclosure Statement or amount incorrect
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 187
- **Severity:** Critical
- **Data needed:** equity amount cross-check (deepen gift_letter + closing_disclosure)
- **Rationale:** Same family as G111 (FRD variant).
- **SME:** [ ] agree [ ] correct: ______

### G121 — O-FRD-55979 [O-FRD]
- **Q:** Were all gift and/or grant fund requirements met?
- **Defect condition:** Graduation gift for 1st time homebuyer & diploma/transcripts not provided supporting graduation date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 196
- **Severity:** Critical
- **Data needed:** diploma/transcript documentation (niche, not in corpus)
- **Rationale:** Crisp presence check; graduation-gift program docs don't exist in any synthetic loan.
- **SME:** [ ] agree [ ] correct: ______

### G122 — O-FRD-55980 [O-FRD]
- **Q:** Were all gift and/or grant fund requirements met?
- **Defect condition:** Graduation gift for 1st time homebuyer not deposited to borrower's acct w/in 90 days of graduation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 318
- **Severity:** Critical
- **Data needed:** graduation-date evidence + gift_letter/bank_statement date fields
- **Rationale:** Same graduation-gift family as G121; also needs a graduation-date fact no current document supplies.
- **SME:** [ ] agree [ ] correct: ______

### G124 — O-FRD-00233 [O-FRD]
- **Q:** Were all gift and/or grant fund requirements met?
- **Defect condition:** The  gift or grant from an eligible agency was not documented as required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 179
- **Severity:** Critical
- **Data needed:** agency-eligibility documentation (deepen gift_letter or a new doc, unclear which)
- **Rationale:** Crisp presence check once whatever 'eligible agency' documentation is defined exists.
- **SME:** [ ] agree [ ] correct: ______

### G125 — O-FRD-55981 [O-FRD]
- **Q:** Were all gift and/or grant fund requirements met?
- **Defect condition:** The gift letter did not state the actual or the maximum amount of the gift funds or gift of equity
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 233
- **Severity:** Critical
- **Data needed:** gift-amount-stated field (deepen gift_letter FIELD_SPECS)
- **Rationale:** gift_letter doc exists in the corpus (loan 02); extracting a gift-amount field is a plausible near-term Bucket-B win, though not implemented here.
- **SME:** [ ] agree [ ] correct: ______

### G126 — FRD-GrantSub [O-FRD]
- **Q:** Were all gift and/or grant fund requirements met?
- **Defect condition:** The grant funds are not submitted under borrower number 1
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 199
- **Severity:** Major
- **Data needed:** same DU/LPA borrower-number gap as G115
- **Rationale:** Same family as G115 (FRD variant).
- **SME:** [ ] agree [ ] correct: ______

### G127 — O-FRD-00232 [O-FRD]
- **Q:** Were all gift and/or grant fund requirements met?
- **Defect condition:** Transfer of gift from donor acct to borr acct, closing agent, realtor or builder not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 316
- **Severity:** Critical
- **Data needed:** transfer-method field (deepen gift_letter)
- **Rationale:** Related to the gift_transfer_evidence_in_file family (see G135's READY-TO-BUILD note) but bundles multiple named-recipient variants (donor acct/borr acct/closing agent/realtor/builder) the existing boolean fact likely doesn't distinguish — needs SME review before wiring.
- **SME:** [ ] agree [ ] correct: ______

### G128 — O-FRD-50464 [O-FRD]
- **Q:** Were all gift and/or grant fund requirements met?
- **Defect condition:** Wedding gift funds not documented w/ marriage license &/or not deposited w/in 90 days of marriage
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 334
- **Severity:** Critical
- **Data needed:** marriage license document (niche, not in corpus)
- **Rationale:** Crisp presence/timing check once the document exists.
- **SME:** [ ] agree [ ] correct: ______

### G130 — O-RHS-57768 [O-RHS]
- **Q:** Were all gift asset requirements met?
- **Defect condition:** Borrower received cash back at closing due to a gift of equity, sweat equity, or rent credits
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 163
- **Severity:** Critical
- **Data needed:** cross-reference of cash_out_to_borrower_1003 (already extracted) against gift/sweat-equity/rent-credit facts (partial fixture gap for the latter)
- **Rationale:** READY TO BUILD candidate (partial) — see READY_TO_BUILD.
- **READY TO BUILD:** Partial win now: 'Borrower received cash back at closing due to a gift of equity, sweat equity, or rent credits' (O-RHS-57768) can be cross-referenced today against cash_out_to_borrower_1003 (already extracted) + gift_transfer_evidence_in_file/gift_letter presence; a full sweat-equity/rent-credit fact still needs new fixtures, but the gift-fund half is buildable now.
- **SME:** [ ] agree [ ] correct: ______

### G131 — O-RHS-02773 [O-RHS]
- **Q:** Were all gift asset requirements met?
- **Defect condition:** Check/elec Xfer to the closing agent or the Closing Disclosure did not document the gift at closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 178
- **Severity:** Critical
- **Data needed:** transfer-method field, same gift-transfer family as G108/G127
- **Rationale:** Worth SME review before wiring to the existing gift_transfer_evidence_in_file fact (same caution as G108/G127).
- **SME:** [ ] agree [ ] correct: ______

### G132 — O-RHS-57767 [O-RHS]
- **Q:** Were all gift asset requirements met?
- **Defect condition:** Gift of equity, sweat equity, or rent credits were not applied as a reduction to the purchase price
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 189
- **Severity:** Critical
- **Data needed:** sale-price-reduction field cross-check (deepen closing_disclosure)
- **Rationale:** closing_disclosure exists in every loan; the specific reduction-applied field does not.
- **SME:** [ ] agree [ ] correct: ______

### G133 — O-RHS-02770 [O-RHS]
- **Q:** Were all gift asset requirements met?
- **Defect condition:** No, gift funds did not come from an acceptable source
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 176
- **Severity:** Critical
- **Stays human:** donor-acceptability guideline judgment
- **Data needed:** donor-relationship field (deepen gift_letter)
- **Rationale:** Same donor-acceptability family as G110/G119/G142 (RHS wording variant).
- **SME:** [ ] agree [ ] correct: ______

### G135 — O-RHS-02772 [O-RHS]
- **Q:** Were all gift asset requirements met?
- **Defect condition:** No, proof of transfer not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 177
- **Severity:** Critical
- **Machine checks:** gift_transfer_evidence_in_file (fact ALREADY extracted and checked by GiftEvidenceShape)
- **Data needed:** none — wire this exception code into MAPPED_SHAPES; see READY_TO_BUILD
- **Rationale:** READY TO BUILD candidate — top pick: the check this row needs already exists in code (GiftEvidenceShape/CHK-AST-002) but is wired to zero AMQ exception codes today.
- **READY TO BUILD:** WIRE, don't build — GiftEvidenceShape (CHK-AST-002) already checks exactly this fact (gift_transfer_evidence_in_file), but MAPPED_SHAPES wires it to ZERO amq_exception_codes today (amq_compiler.py: "GiftEvidenceShape": {..."amq_exception_codes": []}). O-RHS-02772 ("No, proof of transfer not provided") is a clean 1-line addition to that list — no new code, no new fixture.
- **SME:** [ ] agree [ ] correct: ______

### G137 — O-FHA-58114 [O-FHA]
- **Q:** Were all gifts requirements met?
- **Defect condition:** For gifts of land, proof of donor ownership and title transfer to the borrower was not obtained
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 190
- **Severity:** Major
- **Data needed:** land-gift title-transfer documentation (niche, not in corpus)
- **Rationale:** Crisp presence check once the document exists.
- **SME:** [ ] agree [ ] correct: ______

### G138 — O-FHA-58113 [O-FHA]
- **Q:** Were all gifts requirements met?
- **Defect condition:** Gift at closing, missing donor payment to closing agent with EFT, or bank certified/cashiers check
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 192
- **Severity:** Major
- **Data needed:** payment-method field (deepen gift_letter/closing_disclosure)
- **Rationale:** Both docs exist in the corpus; the specific EFT/cashier's-check-method field does not.
- **SME:** [ ] agree [ ] correct: ______

### G141 — O-FHA-02259 [O-FHA]
- **Q:** Were all gifts requirements met?
- **Defect condition:** The donor of the gift of equity was not a family member
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 185
- **Severity:** Critical
- **Stays human:** donor-family-member determination
- **Data needed:** donor-relationship field (deepen gift_letter)
- **Rationale:** Same donor-relationship family as G110/G119/G133 (FHA gift-of-equity wording).
- **SME:** [ ] agree [ ] correct: ______

### G142 — O-FHA-02256 [O-FHA]
- **Q:** Were all gifts requirements met?
- **Defect condition:** The gift funds were not provided by an acceptable source
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 297
- **Severity:** Critical
- **Stays human:** donor-acceptability guideline judgment
- **Data needed:** donor-relationship field (deepen gift_letter)
- **Rationale:** Same donor-acceptability family as G110/G119/G133 (FHA wording variant).
- **SME:** [ ] agree [ ] correct: ______

### G144 — O-FRD-50454 [O-FRD]
- **Q:** Were all government bond requirements met?
- **Defect condition:** Govnt bonds ownership not documented &/or value not based on lesser of sale price/redeemable value
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 194
- **Severity:** Critical
- **Data needed:** government bond certificate/statement (not in corpus)
- **Rationale:** Crisp ownership/valuation check once the document exists.
- **SME:** [ ] agree [ ] correct: ______

### G146 — O-FHA-02261 [O-FHA]
- **Q:** Were all grants requirements met?
- **Defect condition:** The borrower's receipt of the grant and terms of use were not verified and documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 166
- **Severity:** Critical
- **Stays human:** 'terms of use' compliance judgment
- **Data needed:** grant award/terms documentation (not in corpus)
- **Rationale:** Receipt-verification is crisp once the doc exists; terms-of-use compliance stays partly human.
- **SME:** [ ] agree [ ] correct: ______

### G148 — O-FRD-50470 [O-FRD]
- **Q:** Were all interested party contribution requirements met?
- **Defect condition:** Amount/source of interested party contribution not documented & shown on the Closing Disclosure
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 210
- **Severity:** Critical
- **Data needed:** IPC amount/source field (deepen closing_disclosure)
- **Rationale:** closing_disclosure exists in every loan; no interested-party-contribution line item is in FIELD_SPECS yet — Bucket-B-style for the whole IPC family (G148-166), no new fixture needed, just new fields on an existing document.
- **SME:** [ ] agree [ ] correct: ______

### G149 — O-FRD-59243 [O-FRD]
- **Q:** Were all interested party contribution requirements met?
- **Defect condition:** Int party financing concessions used for purposes other than closing costs or up to 12 mos HOA dues
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 328
- **Severity:** Critical
- **Data needed:** IPC-use classification field (deepen closing_disclosure)
- **Rationale:** Same IPC family as G148.
- **SME:** [ ] agree [ ] correct: ______

### G150 — O-FRD-50466 [O-FRD]
- **Q:** Were all interested party contribution requirements met?
- **Defect condition:** Interested party financing concessions exceeded limits
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 167
- **Severity:** Critical
- **Data needed:** IPC amount + applicable-limit fields (deepen closing_disclosure)
- **Rationale:** Crisp limit-comparison math once fields exist; same IPC family as G148.
- **SME:** [ ] agree [ ] correct: ______

### G152 — O-FRD-50467 [O-FRD]
- **Q:** Were all interested party contribution requirements met?
- **Defect condition:** Sale price not reduced for contribution/reimbursement &/or LTV not calc using lower price/value
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 291
- **Severity:** Critical
- **Data needed:** sale-price + IPC + LTV recalculation fields (deepen closing_disclosure/1003)
- **Rationale:** Same IPC family as G148.
- **SME:** [ ] agree [ ] correct: ______

### G153 — O-FRD-59244 [O-FRD]
- **Q:** Were all interested party contribution requirements met?
- **Defect condition:** Subject includes undisclosed int party contributions paid outside of closing or includes abatements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 207
- **Severity:** Critical
- **Data needed:** cross-document IPC reconciliation (contract vs CD vs appraisal)
- **Rationale:** Harder than a simple presence check (detecting an UNDISCLOSED item by definition requires comparing multiple documents for inconsistency), but still a factual cross-document comparison, not subjective judgment — kept YELLOW, not RED.
- **SME:** [ ] agree [ ] correct: ______

### G154 — O-FNM-00706 [O-FNM]
- **Q:** Were all interested party contributions requirements met?
- **Defect condition:** Financing concessions over limit are sales concessions not deducted from sales price/LTV not recalc
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 232
- **Severity:** Critical
- **Data needed:** same IPC-limit fields as G150
- **Rationale:** Same IPC family (FNM wording variant).
- **Guide candidate:** B3-4.1-02 — Interested Party Contributions (IPCs) (PDF p.423)
- **Guide candidate:** A3-3-01 — Outsourcing of Mortgage Processing and Third-Party Originations (PDF p.123)
- **Guide candidate:** B2-1.2-01 — Loan-to-Value (LTV) Ratios (PDF p.179)
- **SME:** [ ] agree [ ] correct: ______

### G155 — O-FNM-00833 [O-FNM]
- **Q:** Were all interested party contributions requirements met?
- **Defect condition:** IPC's were used for down payment, reserves req's, or to meet minimum borrower contribution
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 209
- **Severity:** Critical
- **Data needed:** same IPC-use fields as G149
- **Rationale:** Same IPC family (FNM wording variant).
- **Guide candidate:** B3-4.1-02 — Interested Party Contributions (IPCs) (PDF p.423)
- **Guide candidate:** A3-3-01 — Outsourcing of Mortgage Processing and Third-Party Originations (PDF p.123)
- **Guide candidate:** B2-2-01 — General Borrower Eligibility Requirements (PDF p.241)
- **SME:** [ ] agree [ ] correct: ______

### G156 — O-FNM-59274 [O-FNM]
- **Q:** Were all interested party contributions requirements met?
- **Defect condition:** IPCs of non-realty items paid prior to, at or after closing were not considered as sales concessions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 213
- **Severity:** Critical
- **Data needed:** same IPC-use fields as G149
- **Rationale:** Same IPC family (FNM wording variant).
- **Guide candidate:** B3-4.1-02 — Interested Party Contributions (IPCs) (PDF p.423)
- **Guide candidate:** B3-6-07 — Debts Paid Oﬀ At or Prior to Closing (PDF p.531)
- **Guide candidate:** C1-2-03 — Ownership of Mortgage Loans Prior to Purchase or Securitization and Third-Party Security Interests (PDF p.951)
- **SME:** [ ] agree [ ] correct: ______

### G158 — O-FHA-51725 [O-FHA]
- **Q:** Were all interested party contributions requirements met?
- **Defect condition:** Legal document in lieu of contract to document interested party contributions not given to appraiser
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 214
- **Severity:** Critical
- **Data needed:** 'legal document in lieu of contract' (niche IPC doc, not in corpus)
- **Rationale:** Crisp presence check once the document exists; touches appraisal workflow too.
- **SME:** [ ] agree [ ] correct: ______

### G159 — O-FNM-55111 [O-FNM]
- **Q:** Were all interested party contributions requirements met?
- **Defect condition:** Lender gave cash-like incentive that did not meet req's &/or did not document no repayment is req'd
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 220
- **Severity:** Critical
- **Stays human:** 'did not document no repayment is req'd' compliance judgment
- **Data needed:** lender-incentive agreement (not in corpus)
- **Rationale:** Presence is crisp; full requirement-compliance stays partly human.
- **Guide candidate:** B3-4.1-02 — Interested Party Contributions (IPCs) (PDF p.423)
- **Guide candidate:** B3-4.3-06 — Grants and Lender Contributions (PDF p.446)
- **Guide candidate:** A2-2-03 — Document Warranties (PDF p.36)
- **SME:** [ ] agree [ ] correct: ______

### G160 — O-FNM-55112 [O-FNM]
- **Q:** Were all interested party contributions requirements met?
- **Defect condition:** Lender incentive paying off a portion of the loan being refinanced & subject is not a high LTV refi
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 221
- **Severity:** Critical
- **Data needed:** lender-incentive + LTV/refi-type fields (deepen closing_disclosure)
- **Rationale:** Same IPC/lender-incentive family as G159.
- **Guide candidate:** B3-4.1-02 — Interested Party Contributions (IPCs) (PDF p.423)
- **Guide candidate:** B5-7-01 — High LTV Reﬁnance Loan and Borrower Eligibility (PDF p.819)
- **Guide candidate:** B5-7-02 — High LTV Reﬁnance Underwriting, Documentation, and Collateral Requirements for the New Loan (PDF p.824)
- **SME:** [ ] agree [ ] correct: ______

### G162 — O-FNM-55630 [O-FNM]
- **Q:** Were all interested party contributions requirements met?
- **Defect condition:** Premium pricing credit applied to down pymt &/or exceeded the amt needed to offset the closing costs
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 245
- **Severity:** Critical
- **Data needed:** premium-pricing-credit field (deepen closing_disclosure)
- **Rationale:** Same premium-pricing family as G061.
- **Guide candidate:** B3-4.1-02 — Interested Party Contributions (IPCs) (PDF p.423)
- **Guide candidate:** A3-3-01 — Outsourcing of Mortgage Processing and Third-Party Originations (PDF p.123)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G163 — O-FHA-00597 [O-FHA]
- **Q:** Were all interested party contributions requirements met?
- **Defect condition:** Sale price not reduced when the loan amount is based on seller contributions or inducements over 6%
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 208
- **Severity:** Critical
- **Data needed:** same IPC-limit fields as G150 (6% threshold)
- **Rationale:** Same IPC family as G148/G150, crisp threshold math once fields exist.
- **SME:** [ ] agree [ ] correct: ______

### G164 — O-FNM-59273 [O-FNM]
- **Q:** Were all interested party contributions requirements met?
- **Defect condition:** The loan includes an interested party funded payment abatement
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 215
- **Severity:** Critical
- **Data needed:** IPC-abatement field (deepen closing_disclosure)
- **Rationale:** Same IPC family as G148.
- **Guide candidate:** B3-4.1-02 — Interested Party Contributions (IPCs) (PDF p.423)
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **SME:** [ ] agree [ ] correct: ______

### G166 — O-FHA-51724 [O-FHA]
- **Q:** Were all interested party contributions requirements met?
- **Defect condition:** Total interested party contributions not on contract/legal doc, 92900-LT, &/or Closing Disclosure
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 212
- **Severity:** Critical
- **Data needed:** cross-doc IPC total reconciliation (contract/92900-LT/CD)
- **Rationale:** hud_92900a doc type exists (loan 02) though the specific 92900-LT (loan-estimate side) form is distinct; same IPC family as G148.
- **SME:** [ ] agree [ ] correct: ______

### G167 — O-FRD-50460 [O-FRD]
- **Q:** Were all life insurance requirements met?
- **Defect condition:** Life insurance used & stmt not provided with all req'd information &/or liquidation if applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 224
- **Severity:** Critical
- **Stays human:** 'liquidation if applicable' judgment
- **Data needed:** life insurance statement (not in corpus)
- **Rationale:** Same life-insurance family as G062.
- **SME:** [ ] agree [ ] correct: ______

### G169 — O-FRD-55523 [O-FRD]
- **Q:** Were all liquidation or sale of asset requirements met?
- **Defect condition:** Cryptocurrency was considered in the asset calculation to establish the DTI ratio
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 139
- **Severity:** Critical
- **Data needed:** cryptocurrency documentation (not in corpus)
- **Rationale:** Same virtual-currency family as G044/G174/G200/G201/G205/G213.
- **SME:** [ ] agree [ ] correct: ______

### G171 — O-FRD-50461 [O-FRD]
- **Q:** Were all liquidation or sale of asset requirements met?
- **Defect condition:** No evidence of liquidation for applicable accounts that are less than 20% of the amt needed to close
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 106
- **Severity:** Critical
- **Data needed:** 'amount needed to close' + liquidation-evidence fields (20% threshold; deepen extraction)
- **Rationale:** Crisp threshold math once fields exist; bank_statement/1003 exist, specific liquidation-evidence doc likely separate and absent.
- **SME:** [ ] agree [ ] correct: ______

### G173 — O-FRD-00270 [O-FRD]
- **Q:** Were all liquidation or sale of asset requirements met?
- **Defect condition:** Sale proceeds not real estate/exchange-traded securities without a bill of sale or proof of receipt
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 281
- **Severity:** Critical
- **Data needed:** bill-of-sale document (not in corpus)
- **Rationale:** Same personal-property-sale family as G185/G186/G195/G261.
- **SME:** [ ] agree [ ] correct: ______

### G174 — O-FRD-55522 [O-FRD]
- **Q:** Were all liquidation or sale of asset requirements met?
- **Defect condition:** The file did not document that the cryptocurrency source of funds was exchanged for U.S. dollars
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 140
- **Severity:** Critical
- **Data needed:** same cryptocurrency gap as G169
- **Rationale:** Same virtual-currency family as G169.
- **SME:** [ ] agree [ ] correct: ______

### G175 — O-FRD-00268 [O-FRD]
- **Q:** Were all liquidation or sale of asset requirements met?
- **Defect condition:** Traded securities or vested stock used without 2 mos statements, VOD or alt document or as per LPA
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 295
- **Severity:** Critical
- **Data needed:** brokerage/stock statement (not in corpus)
- **Rationale:** Same stocks/bonds family as G144/G214/G262/G273/G275/G281/G283.
- **SME:** [ ] agree [ ] correct: ______

### G176 — O-FHA-02250 [O-FHA]
- **Q:** Were all minimum required investment (MRI) requirements met?
- **Defect condition:** MRI was provided by a source other than the borr that was not a permissible source that meets req's
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 165
- **Severity:** Critical
- **Stays human:** 'permissible source that meets req's' guideline judgment
- **Data needed:** MRI-source field + SME-defined permissible-source list
- **Rationale:** Source-name presence is crisp; full permissibility determination stays partly human.
- **SME:** [ ] agree [ ] correct: ______

### G179 — O-FNM-50255 [O-FNM]
- **Q:** Were all minimum reserve requirements met?
- **Defect condition:** Reserves are insufficient based on the subject loan characteristics or as was required by DU
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 266
- **Severity:** Critical
- **Data needed:** DU reserve-requirement field (AUS-family, not in corpus)
- **Rationale:** Same AUS-submission gap as G037/G039/G095/G243/G244.
- **Guide candidate:** B3-4.1-01 — Minimum Reserve Requirements (PDF p.418)
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **SME:** [ ] agree [ ] correct: ______

### G180 — O-FNM-50254 [O-FNM]
- **Q:** Were all minimum reserve requirements met?
- **Defect condition:** The financial assets provided for reserves were from an unacceptable source
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 268
- **Severity:** Critical
- **Stays human:** 'unacceptable source' guideline judgment
- **Data needed:** reserve-source field
- **Rationale:** Same source-acceptability pattern as the donor-acceptability family.
- **Guide candidate:** B3-4.1-01 — Minimum Reserve Requirements (PDF p.418)
- **Guide candidate:** A4-1-02 — Submission of Financial Statements and Reports (PDF p.158)
- **Guide candidate:** B3-3.4-06 — Employment Related Assets as Qualifying Income (PDF p.358)
- **SME:** [ ] agree [ ] correct: ______

### G182 — O-FHA-50018 [O-FHA]
- **Q:** Were all net proceeds asset requirements met?
- **Defect condition:** Evidence does not exist indicating the borrower is entitled to net proceeds
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 290
- **Severity:** Critical
- **Data needed:** prior-sale entitlement field (deepen closing_disclosure)
- **Rationale:** Same net-proceeds-entitlement family as G183/G187.
- **SME:** [ ] agree [ ] correct: ______

### G183 — O-FHA-02268 [O-FHA]
- **Q:** Were all net proceeds asset requirements met?
- **Defect condition:** Net sale proceeds considered & not verified with a fully executed Closing Disclosure or similar
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 285
- **Severity:** Critical
- **Data needed:** net-proceeds cross-check field (deepen closing_disclosure)
- **Rationale:** closing_disclosure exists in the corpus; the specific net-proceeds-verified field does not — same family as G182.
- **SME:** [ ] agree [ ] correct: ______

### G185 — O-RHS-54266 [O-RHS]
- **Q:** Were all net proceeds asset requirements met?
- **Defect condition:** Ownership, transfer and receipt of proceeds from the sale of personal property not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 284
- **Severity:** Critical
- **Data needed:** bill-of-sale / personal-property-sale doc (not in corpus)
- **Rationale:** Same family as G173/G186/G195.
- **SME:** [ ] agree [ ] correct: ______

### G186 — O-FHA-02266 [O-FHA]
- **Q:** Were all net proceeds asset requirements met?
- **Defect condition:** Personal property sold-item value, bill of sale & borr's receipt/deposit of proceeds not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 283
- **Severity:** Critical
- **Data needed:** same bill-of-sale gap as G185
- **Rationale:** Same personal-property-sale family as G185.
- **SME:** [ ] agree [ ] correct: ______

### G187 — O-FHA-57879 [O-FHA]
- **Q:** Were all net proceeds asset requirements met?
- **Defect condition:** Sale of real prop not documented as arm's length trans & that borrower is entitled to net proceeds
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 105
- **Severity:** Major
- **Data needed:** arm's-length-transaction affidavit (not in corpus)
- **Rationale:** 'Arm's length' is normally evidenced by a specific affidavit/settlement doc, not inherently a subjective call once that doc exists — kept YELLOW, not RED.
- **SME:** [ ] agree [ ] correct: ______

### G191 — O-RHS-57766 [O-RHS]
- **Q:** Were all other asset requirements met?
- **Defect condition:** Foreign asset availability not verified & converted to English or accurate translation not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 172
- **Severity:** Critical
- **Data needed:** foreign asset statement + translation (not in corpus)
- **Rationale:** Same foreign-asset family as G092/G200/G201/G205.
- **SME:** [ ] agree [ ] correct: ______

### G192 — O-RHS-57765 [O-RHS]
- **Q:** Were all other asset requirements met?
- **Defect condition:** Foreign assets not exchanged to U.S. dollars & in a Federal or State regulated financial institution
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 169
- **Severity:** Critical
- **Data needed:** same foreign-asset gap as G191
- **Rationale:** Same foreign-asset family as G191.
- **SME:** [ ] agree [ ] correct: ______

### G195 — O-RHS-02780 [O-RHS]
- **Q:** Were all other asset requirements met?
- **Defect condition:** Value of personal property held for investment purposes was not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 239
- **Severity:** Critical
- **Data needed:** personal-property valuation doc (not in corpus)
- **Rationale:** Same family as G185/G186.
- **SME:** [ ] agree [ ] correct: ______

### G197 — O-FNM-55668 [O-FNM]
- **Q:** Were all other asset type requirements met?
- **Defect condition:** Borr access to trust & effect withdrawal has on qualifying trust income not documented as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 320
- **Severity:** Major
- **Data needed:** trust agreement / trustee statement (not in corpus)
- **Rationale:** Same trust family as G214/G281/G283.
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **Guide candidate:** B3-3.4-06 — Employment Related Assets as Qualifying Income (PDF p.358)
- **Guide candidate:** B3-3.4-16 — Trust Income (PDF p.374)
- **SME:** [ ] agree [ ] correct: ______

### G198 — O-FRD-56003 [O-FRD]
- **Q:** Were all other asset type requirements met?
- **Defect condition:** Bridge loan proceeds - evidence loan is secured by real property & receipt of proceeds not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 117
- **Severity:** Critical
- **Data needed:** bridge loan security/receipt doc (not in corpus)
- **Rationale:** Same bridge-loan family as G047/G049/G263.
- **SME:** [ ] agree [ ] correct: ______

### G199 — O-FRD-00266 [O-FRD]
- **Q:** Were all other asset type requirements met?
- **Defect condition:** Corporate relocation program, the file does not contain a copy of the executed buyout agreement
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 162
- **Severity:** Critical
- **Data needed:** same relocation buy-out agreement gap as G034
- **Rationale:** Same family as G034.
- **SME:** [ ] agree [ ] correct: ______

### G200 — O-FNM-55682 [O-FNM]
- **Q:** Were all other asset type requirements met?
- **Defect condition:** Foreign asset documents was not completed in English or with a complete and accurate translation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 173
- **Severity:** Critical
- **Data needed:** foreign-asset translation doc (not in corpus)
- **Rationale:** Same foreign-asset family as G191/G201/G205.
- **Guide candidate:** A3-3-03 — Other Servicing Arrangements (PDF p.131)
- **Guide candidate:** A3-3-05 — Custody of Mortgage Documents (PDF p.136)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G201 — O-FNM-55681 [O-FNM]
- **Q:** Were all other asset type requirements met?
- **Defect condition:** Foreign assets used as a source of funds was not verified in U.S. dollars prior to closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 171
- **Severity:** Critical
- **Data needed:** same foreign-currency exchange gap as G092
- **Rationale:** Same foreign-funds family as G092/G200/G205.
- **Guide candidate:** B3-4.2-05 — Foreign Assets (PDF p.438)
- **Guide candidate:** B3-4.3-15 — Borrowed Funds Secured by an Asset (PDF p.458)
- **Guide candidate:** B3-6-07 — Debts Paid Oﬀ At or Prior to Closing (PDF p.531)
- **SME:** [ ] agree [ ] correct: ______

### G202 — O-FRD-02619 [O-FRD]
- **Q:** Were all other asset type requirements met?
- **Defect condition:** Funds for closing from credit card, cash advance or unsecured LOC did not meet requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 137
- **Severity:** Critical
- **Data needed:** credit-card/cash-advance/LOC documentation (not in corpus)
- **Rationale:** Related to G027/G223 (unallowable-funds family).
- **SME:** [ ] agree [ ] correct: ______

### G203 — O-FRD-55519 [O-FRD]
- **Q:** Were all other asset type requirements met?
- **Defect condition:** HELOC closing funds not secured by the borrower’s real property &/or HELOC proceeds  not received
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 200
- **Severity:** Critical
- **Data needed:** HELOC agreement + proceeds doc (not in corpus)
- **Rationale:** Crisp presence/security check once the document exists.
- **SME:** [ ] agree [ ] correct: ______

### G204 — O-FRD-00272 [O-FRD]
- **Q:** Were all other asset type requirements met?
- **Defect condition:** No appraisal & copy of trade-in contract to document equity net proceeds of trade in of prior home
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 313
- **Severity:** Critical
- **Data needed:** trade-in contract doc (not in corpus)
- **Rationale:** Same trade-equity family as G220/G221/G279.
- **SME:** [ ] agree [ ] correct: ______

### G205 — O-FNM-55680 [O-FNM]
- **Q:** Were all other asset type requirements met?
- **Defect condition:** No evidence foreign assets were exchanged into U.S. dollars & held in a U.S./state regulated bank
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 168
- **Severity:** Critical
- **Data needed:** same foreign-currency exchange gap as G092/G201
- **Rationale:** Same foreign-funds family as G092/G201.
- **Guide candidate:** B3-4.2-05 — Foreign Assets (PDF p.438)
- **Guide candidate:** A3-3-03 — Other Servicing Arrangements (PDF p.131)
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **SME:** [ ] agree [ ] correct: ______

### G206 — O-FRD-00264 [O-FRD]
- **Q:** Were all other asset type requirements met?
- **Defect condition:** Non-property asset secured loan ineligible source/ownership, value, receipt of funds not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 294
- **Severity:** Critical
- **Data needed:** secured-loan documentation (not in corpus)
- **Rationale:** Related to G045 (personal/secured loan family).
- **SME:** [ ] agree [ ] correct: ______

### G207 — O-FNM-00291 [O-FNM]
- **Q:** Were all other asset type requirements met?
- **Defect condition:** Nonprofit individual development acct used without documentation of deposits or program
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 205
- **Severity:** Critical
- **Data needed:** IDA program documentation (not in corpus)
- **Rationale:** Related to G023 (Individual Development Account family).
- **Guide candidate:** B3-4.2-03 — Individual Development Accounts (PDF p.435)
- **Guide candidate:** B7-3-04 — Individual Property Insurance Requirements for a Unit in a Project Development (PDF p.885)
- **Guide candidate:** A3-3-03 — Other Servicing Arrangements (PDF p.131)
- **SME:** [ ] agree [ ] correct: ______

### G209 — O-FRD-02621 [O-FRD]
- **Q:** Were all other asset type requirements met?
- **Defect condition:** Pooled funds-File did not document that the participants and the source of funds are eligible
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 241
- **Severity:** Critical
- **Stays human:** 'participants... eligible' determination
- **Data needed:** pooled-funds agreement (not in corpus)
- **Rationale:** Related to G196 (pooled-savings family); presence is crisp, eligibility determination stays partly human.
- **SME:** [ ] agree [ ] correct: ______

### G210 — O-FRD-56002 [O-FRD]
- **Q:** Were all other asset type requirements met?
- **Defect condition:** Proceeds from a 1031 exchange was not documented and verified
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 100
- **Severity:** Critical
- **Data needed:** same 1031-exchange documentation gap as G031
- **Rationale:** Same family as G031.
- **SME:** [ ] agree [ ] correct: ______

### G211 — O-FRD-54697 [O-FRD]
- **Q:** Were all other asset type requirements met?
- **Defect condition:** Prorated real estate tax credit by the seller was included in determining enough funds for closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 296
- **Severity:** Critical
- **Data needed:** tax-proration-credit field (deepen closing_disclosure)
- **Rationale:** closing_disclosure exists in every loan; the specific proration-credit field does not.
- **SME:** [ ] agree [ ] correct: ______

### G212 — O-FRD-00275 [O-FRD]
- **Q:** Were all other asset type requirements met?
- **Defect condition:** Rent credited to sale price no rent-sale agmt or credit exceeds difference rent paid & market rent
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 258
- **Severity:** Critical
- **Data needed:** rent-to-own agreement (not in corpus)
- **Rationale:** Same rent-credit family as G217/G231-235.
- **SME:** [ ] agree [ ] correct: ______

### G213 — O-FNM-55674 [O-FNM]
- **Q:** Were all other asset type requirements met?
- **Defect condition:** The file did not document that the virtual currency source of funds was exchanged for U.S. dollars
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 330
- **Severity:** Critical
- **Data needed:** same virtual-currency exchange gap as G044
- **Rationale:** Same virtual-currency family as G044/G169/G174.
- **Guide candidate:** B3-4.1-04 — Virtual Currency (PDF p.429)
- **Guide candidate:** B3-4.3-15 — Borrowed Funds Secured by an Asset (PDF p.458)
- **Guide candidate:** A2-2-03 — Document Warranties (PDF p.36)
- **SME:** [ ] agree [ ] correct: ______

### G214 — O-FNM-55667 [O-FNM]
- **Q:** Were all other asset type requirements met?
- **Defect condition:** The file did not document the value of the trust account from the trust manager or the trustee
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 319
- **Severity:** Major
- **Data needed:** trust manager statement (not in corpus)
- **Rationale:** Same trust family as G197/G281/G283.
- **Guide candidate:** A2-2-03 — Document Warranties (PDF p.36)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **Guide candidate:** A3-3-03 — Other Servicing Arrangements (PDF p.131)
- **SME:** [ ] agree [ ] correct: ______

### G215 — O-FHA-51726 [O-FHA]
- **Q:** Were all other assets requirements met?
- **Defect condition:** A dollar for dollar reduction for the inducement to purchase was not applied to the sales price
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 206
- **Severity:** Critical
- **Data needed:** inducement-to-purchase field (deepen closing_disclosure)
- **Rationale:** Related to the IPC family (G148); doc exists, field does not.
- **SME:** [ ] agree [ ] correct: ______

### G217 — O-FHA-02273 [O-FHA]
- **Q:** Were all other assets requirements met?
- **Defect condition:** Rent credits agreement, market rent value & receipt of rent payments not verified & documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 257
- **Severity:** Critical
- **Data needed:** rent credit agreement (not in corpus)
- **Rationale:** Same rent-credit family as G212/G231-235.
- **SME:** [ ] agree [ ] correct: ______

### G218 — O-FHA-02269 [O-FHA]
- **Q:** Were all other assets requirements met?
- **Defect condition:** Subject commission for cash to close without verifying borr RE license/commission entitlement
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 115
- **Severity:** Critical
- **Stays human:** RE license 'entitlement' verification
- **Data needed:** RE agent license copy (not in corpus) — possible Bucket-C candidate
- **Rationale:** Borderline: a license copy in the file might suffice, but genuinely current license STATUS verification could require a state licensing-board lookup, similar in kind to the discarded NMLS rule (decision 016). Flagged, not unilaterally discarded — a human should decide.
- **SME:** [ ] agree [ ] correct: ______

### G219 — O-FHA-50682 [O-FHA]
- **Q:** Were all other assets requirements met?
- **Defect condition:** Sweat equity used as a source of funds without labor & materials being documented as required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 307
- **Severity:** Critical
- **Data needed:** sweat-equity labor/materials documentation (not in corpus)
- **Rationale:** Same family as G278.
- **SME:** [ ] agree [ ] correct: ______

### G220 — O-FHA-02267 [O-FHA]
- **Q:** Were all other assets requirements met?
- **Defect condition:** The trade-in transaction of manufactured housing and the trade equity not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 231
- **Severity:** Critical
- **Data needed:** trade-in contract/appraisal doc (not in corpus)
- **Rationale:** Same trade-equity family as G204/G221/G279.
- **SME:** [ ] agree [ ] correct: ______

### G221 — O-FHA-02272 [O-FHA]
- **Q:** Were all other assets requirements met?
- **Defect condition:** Trade Equity Transaction- Appraisal and the closing disclosure were not verified and documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 312
- **Severity:** Critical
- **Data needed:** same trade-equity documentation gap as G220
- **Rationale:** Same family as G220.
- **SME:** [ ] agree [ ] correct: ______

### G223 — O-FNM-50263 [O-FNM]
- **Q:** Were all personal unsecured loans asset requirements met?
- **Defect condition:** Unallowable funds used from a personal unsecured loan, credit card or overdraft protection
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 240
- **Severity:** Critical
- **Data needed:** personal-loan/credit documentation (not in corpus)
- **Rationale:** Related to G045/G202 (unallowable-funds family).
- **Guide candidate:** B3-4.3-17 — Personal Unsecured Loans (PDF p.461)
- **Guide candidate:** B3-4.3-15 — Borrowed Funds Secured by an Asset (PDF p.458)
- **Guide candidate:** B3-4.3-16 — Credit Card Financing and Reward Points (PDF p.459)
- **SME:** [ ] agree [ ] correct: ______

### G225 — O-FHA-02255 [O-FHA]
- **Q:** Were all private savings clubs requirements met?
- **Defect condition:** Private savings club used w/out documenting club duration, receipt of funds or reasonability
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 246
- **Severity:** Critical
- **Stays human:** 'reasonability' clause (one of three possible defects in this row)
- **Data needed:** private-savings-club statement (not in corpus)
- **Rationale:** Two of the three listed conditions (club duration, receipt of funds) are crisp facts; only the appended 'reasonability' clause stays human — kept YELLOW, not RED, since it isn't the row's sole condition.
- **SME:** [ ] agree [ ] correct: ______

### G231 — O-FNM-55669 [O-FNM]
- **Q:** Were all rent credit for option to purchase asset requirements met?
- **Defect condition:** Rent credit for option to purchase agmt w/ 12 mos term, rental amt & terms of the lease not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 254
- **Severity:** Major
- **Data needed:** lease/option-to-purchase agreement (not in corpus)
- **Rationale:** Same rent-credit family as G212/G217/G233-235.
- **Guide candidate:** A2-2-02 — Delivery Information and Delivery-Option Speciﬁc Representations and Warranties (PDF p.34)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B2-1.3-01 — Purchase Transactions (PDF p.188)
- **SME:** [ ] agree [ ] correct: ______

### G233 — O-FNM-55671 [O-FNM]
- **Q:** Were all rent credit for option to purchase asset requirements met?
- **Defect condition:** Rent credit for option to purchase market rent was not determined by the subject property appraisal
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 259
- **Severity:** Major
- **Data needed:** market-rent determination field (deepen appraisal, or a rent-schedule addendum)
- **Rationale:** appraisal doc exists in the corpus but doesn't normally capture a market-rent determination — likely needs a distinct rent-schedule addendum.
- **Guide candidate:** B3-6-03 — Monthly Housing Expense for the Subject Property (PDF p.518)
- **Guide candidate:** B4-1.3-02 — Subject and Contract Sections of the Appraisal Report (PDF p.570)
- **Guide candidate:** B4-1.4-07 — Mixed-Use Property Appraisal Requirements (PDF p.626)
- **SME:** [ ] agree [ ] correct: ______

### G234 — O-FNM-00277 [O-FNM]
- **Q:** Were all rent credit for option to purchase asset requirements met?
- **Defect condition:** Rent credit not calculated using the difference between market rent & actual rent paid by the borr
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 261
- **Severity:** Critical
- **Data needed:** market-rent + actual-rent fields (deepen appraisal/lease)
- **Rationale:** Crisp math once fields exist; same rent-credit family as G233.
- **Guide candidate:** A2-2-02 — Delivery Information and Delivery-Option Speciﬁc Representations and Warranties (PDF p.34)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B2-1.3-01 — Purchase Transactions (PDF p.188)
- **SME:** [ ] agree [ ] correct: ______

### G235 — O-FNM-58104 [O-FNM]
- **Q:** Were all rent credit for option to purchase asset requirements met?
- **Defect condition:** Rent-back credit used as source of funds for closing costs, down pymt, or reserves when qualifying
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 256
- **Severity:** Critical
- **Data needed:** rent-back-credit field (deepen closing_disclosure)
- **Rationale:** closing_disclosure exists; the specific rent-back-credit-as-source-of-funds field does not.
- **Guide candidate:** B3-4.3-15 — Borrowed Funds Secured by an Asset (PDF p.458)
- **Guide candidate:** A2-2-02 — Delivery Information and Delivery-Option Speciﬁc Representations and Warranties (PDF p.34)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G236 — O-FHA-02262 [O-FHA]
- **Q:** Were all requirements met for loans obtained to be used as available assets?_x000D_
- **Defect condition:** Collateralized loan used was not documented w/ a copy of the Note and receipt of loan proceeds
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 129
- **Severity:** Critical
- **Data needed:** collateralized-loan note (not in corpus)
- **Rationale:** Related to G045/G206 (secured-loan family).
- **SME:** [ ] agree [ ] correct: ______

### G237 — O-FHA-02264 [O-FHA]
- **Q:** Were all requirements met for loans obtained to be used as available assets?_x000D_
- **Defect condition:** Disaster relief loan used without the promissory note being verified and documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 144
- **Severity:** Critical
- **Data needed:** disaster-relief promissory note (niche, not in corpus)
- **Rationale:** Crisp presence check once the document exists.
- **SME:** [ ] agree [ ] correct: ______

### G238 — O-FHA-02263 [O-FHA]
- **Q:** Were all requirements met for loans obtained to be used as available assets?_x000D_
- **Defect condition:** Existence and amounts in retirement accts and outstanding loan balance not documented and verified
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 270
- **Severity:** Critical
- **Data needed:** retirement account statement (not in corpus)
- **Rationale:** Same retirement family as G249/G251/G252/G254-257.
- **SME:** [ ] agree [ ] correct: ______

### G240 — O-FRD-57988 [O-FRD]
- **Q:** Were all reserve requirements met?
- **Defect condition:** Borr has 1 to 6 financed properties, including the subject, & 2 mos reserves for each not verified
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 264
- **Severity:** Critical
- **Data needed:** financed-property count + reserve-months fields (not modeled — no REO-schedule entity today)
- **Rationale:** Crisp math once a financed-properties schedule is parsed from the 1003; this pilot's extractor doesn't yet treat the 1003's REO section as its own entity.
- **SME:** [ ] agree [ ] correct: ______

### G241 — O-FRD-57989 [O-FRD]
- **Q:** Were all reserve requirements met?
- **Defect condition:** Borr has 7 to 10 financed properties, including the subject, & 8 mos reserves for each not verified
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 265
- **Severity:** Major
- **Data needed:** same financed-property-schedule gap as G240
- **Rationale:** Same family as G240 (7-10 property tier).
- **SME:** [ ] agree [ ] correct: ______

### G243 — O-FRD-50449 [O-FRD]
- **Q:** Were all reserve requirements met?
- **Defect condition:** Reserves are insufficient based on the subject loan characteristics or as was required by LPA
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 267
- **Severity:** Critical
- **Data needed:** LPA reserve-requirement field (AUS-family, not in corpus)
- **Rationale:** Same AUS-submission gap as G179 (Freddie's LPA, not Fannie's DU).
- **SME:** [ ] agree [ ] correct: ______

### G244 — O-FHA-58117 [O-FHA]
- **Q:** Were all reserves/cash to close requirements met?_x000D_
- **Defect condition:** All assets submitted to the AUS were not verified and documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 109
- **Severity:** Major
- **Data needed:** AUS/TOTAL Scorecard findings (FHA's AUS, not in corpus)
- **Rationale:** Same AUS-submission gap as G037/G039/G095/G179/G243.
- **SME:** [ ] agree [ ] correct: ______

### G246 — O-FHA-58118 [O-FHA]
- **Q:** Were all reserves/cash to close requirements met?_x000D_
- **Defect condition:** One month's PITI reserves were not verified and documented for a 1-2 property in a manual UW
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 230
- **Severity:** Major
- **Data needed:** PITI + reserve-months fields (deepen extraction)
- **Rationale:** Same reserves family as G057/G247/G248; crisp math once fields exist.
- **SME:** [ ] agree [ ] correct: ______

### G247 — O-FHA-58115 [O-FHA]
- **Q:** Were all reserves/cash to close requirements met?_x000D_
- **Defect condition:** Rental income used for a 1 unit with an ADU & reserves equivalent to 2 months PITI were not verified
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 237
- **Severity:** Major
- **Data needed:** same PITI-reserves gap as G246
- **Rationale:** Same family as G246 (ADU-rental-income variant).
- **SME:** [ ] agree [ ] correct: ______

### G248 — O-FHA-58116 [O-FHA]
- **Q:** Were all reserves/cash to close requirements met?_x000D_
- **Defect condition:** Three months PITI reserves were not verified and documented for a 3-4 unit property
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 262
- **Severity:** Major
- **Data needed:** same PITI-reserves gap as G246
- **Rationale:** Same family as G246 (3-4 unit variant).
- **SME:** [ ] agree [ ] correct: ______

### G249 — O-FNM-00289 [O-FNM]
- **Q:** Were all retirement account asset requirements met?
- **Defect condition:** No evidence vested funds for down pymt/closing/reserves are allowed regardless of employment status
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 273, 274
- **Severity:** Critical
- **Data needed:** retirement-plan vesting-schedule doc (not in corpus)
- **Rationale:** Same retirement family as G238.
- **Guide candidate:** B3-4.3-15 — Borrowed Funds Secured by an Asset (PDF p.458)
- **Guide candidate:** B3-3.1-04 — Verbal Veriﬁcation of Employment (PDF p.324)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **SME:** [ ] agree [ ] correct: ______

### G251 — O-FHA-54536 [O-FHA]
- **Q:** Were all retirement account requirements met?
- **Defect condition:** Evidence of liquidation of retirement funds needed for closing was not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 279
- **Severity:** Critical
- **Data needed:** same retirement-account-statement gap as G238
- **Rationale:** Same family as G238.
- **SME:** [ ] agree [ ] correct: ______

### G252 — O-FHA-50680 [O-FHA]
- **Q:** Were all retirement account requirements met?
- **Defect condition:** Over 60% of the value of the retirement accounts was considered &/or loans not deducted
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 271, 272
- **Severity:** Critical
- **Data needed:** retirement-account value + outstanding-loan fields (60% threshold)
- **Rationale:** Crisp threshold math once fields exist; same retirement family as G238.
- **SME:** [ ] agree [ ] correct: ______

### G254 — O-FRD-50453 [O-FRD]
- **Q:** Were all retirement fund requirements met?
- **Defect condition:** Liquidation of retirement accts not provided & total was less than 20% of the amt needed to close
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 275
- **Severity:** Critical
- **Data needed:** same retirement-account gap as G238 (20% threshold)
- **Rationale:** Same family as G238.
- **SME:** [ ] agree [ ] correct: ______

### G255 — O-FRD-59252 [O-FRD]
- **Q:** Were all retirement fund requirements met?
- **Defect condition:** Retirement liquidation not required; vested amt used without evidence borr can make withdrawals
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 278
- **Severity:** Critical
- **Data needed:** retirement vesting/withdrawal-evidence field
- **Rationale:** Same retirement family as G238/G249.
- **SME:** [ ] agree [ ] correct: ______

### G256 — O-FRD-55825 [O-FRD]
- **Q:** Were all retirement fund requirements met?
- **Defect condition:** VOD or 1 month statement not provided for streamlined accept documentation of retirement accounts
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 277
- **Severity:** Critical
- **Data needed:** retirement-account VOD (doc-presence-style, doc type absent from corpus)
- **Rationale:** Same VOD family as G097/G105/G286, retirement-specific.
- **SME:** [ ] agree [ ] correct: ______

### G257 — O-FRD-00269 [O-FRD]
- **Q:** Were all retirement fund requirements met?
- **Defect condition:** VOD or 2 months statements not provided for standard documentation of retirement accounts
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 276
- **Severity:** Critical
- **Data needed:** same retirement-VOD gap as G256
- **Rationale:** Same family as G256 (2-month standard-doc variant).
- **SME:** [ ] agree [ ] correct: ______

### G260 — O-FNM-54032 [O-FNM]
- **Q:** Were all sale of personal assets requirements met?
- **Defect condition:** Personal asset sale proceeds exceed 50% of monthly qualifying income w/out an independent valuation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 282
- **Severity:** Critical
- **Data needed:** independent valuation doc for a sold personal asset (not in corpus)
- **Rationale:** The 50%-of-income comparison reuses base_monthly_income_1003 (already extracted), but the independent-valuation requirement is a genuinely separate, absent fixture — not a blind extension of LargeDepositShape.
- **Guide candidate:** B3-3.4-06 — Employment Related Assets as Qualifying Income (PDF p.358)
- **Guide candidate:** B3-4.3-18 — Sale of Personal Assets (PDF p.461)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G261 — O-FNM-54031 [O-FNM]
- **Q:** Were all sale of personal assets requirements met?
- **Defect condition:** Proceeds from the sale of a titled personal asset used without documenting the borrower’s ownership
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 286
- **Severity:** Critical
- **Data needed:** title/ownership + bill-of-sale doc (not in corpus)
- **Rationale:** Same personal-property-sale family as G173/G185/G186/G195.
- **Guide candidate:** B3-4.3-18 — Sale of Personal Assets (PDF p.461)
- **Guide candidate:** A2-4.1-02 — Ownership and Retention of Loan Files and Records (PDF p.83)
- **Guide candidate:** B2-2-01 — General Borrower Eligibility Requirements (PDF p.241)
- **SME:** [ ] agree [ ] correct: ______

### G262 — O-FNM-00284 [O-FNM]
- **Q:** Were all sale of personal assets requirements met?
- **Defect condition:** Source of funds from stocks, bonds, mutual or trust funds used without documenting ownership & value
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 280
- **Severity:** Critical
- **Data needed:** brokerage/trust statement (not in corpus)
- **Rationale:** Same stocks/bonds/trust family as G144/G175/G214/G273/G275/G281/G283.
- **Guide candidate:** B3-4.3-01 — Stocks, Stock Options, Bonds, and Mutual Funds (PDF p.439)
- **Guide candidate:** B3-4.3-18 — Sale of Personal Assets (PDF p.461)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **SME:** [ ] agree [ ] correct: ______

### G263 — O-RHS-54262 [O-RHS]
- **Q:** Were all secondary financing (bridge loan) asset requirements met?
- **Defect condition:** Bridge loan proceeds not documented and/or did not include the payment in the DTI as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 116
- **Severity:** Critical
- **Data needed:** bridge loan documentation (not in corpus)
- **Rationale:** Same bridge-loan family as G047/G049/G198.
- **SME:** [ ] agree [ ] correct: ______

### G266 — O-FHA-00258 [O-FHA]
- **Q:** Were all secondary financing requirements met?
- **Defect condition:** File did not document that the terms of a family loan as source of funds met HUD's criteria
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 164
- **Severity:** Critical
- **Stays human:** 'met HUD's criteria' compliance judgment
- **Data needed:** family loan note (not in corpus)
- **Rationale:** Presence is crisp; full HUD-criteria compliance stays partly human.
- **SME:** [ ] agree [ ] correct: ______

### G267 — O-FHA-00253 [O-FHA]
- **Q:** Were all secondary financing requirements met?
- **Defect condition:** Missing nonprofit secondary financing note/mtg, receipt of funds not documented or all req's not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 236
- **Severity:** Critical
- **Data needed:** nonprofit second-mortgage note (not in corpus)
- **Rationale:** Same secondary-financing family as G007/G198/G236/G268-271.
- **SME:** [ ] agree [ ] correct: ______

### G268 — O-FHA-00254 [O-FHA]
- **Q:** Were all secondary financing requirements met?
- **Defect condition:** Source from nonprofit that is an instrumentality of govt and required documentation not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 195
- **Severity:** Critical
- **Data needed:** same nonprofit secondary-financing gap as G267
- **Rationale:** Same family as G267.
- **SME:** [ ] agree [ ] correct: ______

### G269 — O-FNM-50199 [O-FNM]
- **Q:** Were all secondary financing requirements met?
- **Defect condition:** Subordinate financing was allowed on a Co-op share loan without obtaining a policy exception
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 131
- **Severity:** Critical
- **Stays human:** 'policy exception' approval judgment
- **Data needed:** policy-exception approval doc (not in corpus)
- **Rationale:** Presence of an approval record is crisp; whether an exception was properly granted stays partly human.
- **Guide candidate:** B2-1.2-04 — Subordinate Financing (PDF p.184)
- **Guide candidate:** B4-2.3-04 — Loan Eligibility for Co-op Share Loans (PDF p.712)
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **SME:** [ ] agree [ ] correct: ______

### G270 — O-FNM-50198 [O-FNM]
- **Q:** Were all secondary financing requirements met?
- **Defect condition:** Subordinate lien not evidenced by a note, recorded mtg, &/or not clearly subordinate to 1st mtg lien
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 223
- **Severity:** Critical
- **Data needed:** subordination agreement / recorded mortgage doc (not in corpus)
- **Rationale:** Same secondary-financing family as G267/G269/G271.
- **Guide candidate:** B2-1.2-04 — Subordinate Financing (PDF p.184)
- **Guide candidate:** B3-4.3-16 — Credit Card Financing and Reward Points (PDF p.459)
- **Guide candidate:** B5-3.1-01 — Conversion of Construction-to-Permanent Financing: Overview (PDF p.735)
- **SME:** [ ] agree [ ] correct: ______

### G271 — O-FNM-50200 [O-FNM]
- **Q:** Were all secondary financing requirements met?
- **Defect condition:** The type/terms of subordinate financing unacceptable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 301
- **Severity:** Critical
- **Stays human:** 'unacceptable' terms determination
- **Data needed:** subordinate-financing terms field
- **Rationale:** Terms-presence is crisp; acceptability against guide stays human.
- **Guide candidate:** B2-1.2-04 — Subordinate Financing (PDF p.184)
- **Guide candidate:** B3-4.3-16 — Credit Card Financing and Reward Points (PDF p.459)
- **Guide candidate:** B4-1.1-04 — Unacceptable Appraisal Practices (PDF p.541)
- **SME:** [ ] agree [ ] correct: ______

### G273 — O-FHA-50681 [O-FHA]
- **Q:** Were all stocks and bonds requirements met?
- **Defect condition:** A copy of the stock/bond certificate not provided for non-brokerage accounts
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 299
- **Severity:** Critical
- **Data needed:** stock/bond certificate (not in corpus)
- **Rationale:** Same stocks/bonds family as G144/G175/G262/G275/G281/G283.
- **SME:** [ ] agree [ ] correct: ______

### G275 — O-RHS-54268 [O-RHS]
- **Q:** Were all stocks/bonds asset requirements met?
- **Defect condition:** Stocks or other investment funds not documented w/ stmt with vested balance/withdrawal conditions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 300
- **Severity:** Critical
- **Data needed:** same stock/bond statement gap as G273
- **Rationale:** Same family as G273.
- **SME:** [ ] agree [ ] correct: ______

### G278 — O-FNM-00288 [O-FNM]
- **Q:** Were all sweat equity asset requirements met?
- **Defect condition:** Sweat equity was considered on an unallowable transaction and eligibility requirements were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 308
- **Severity:** Critical
- **Stays human:** 'unallowable transaction' / 'eligibility requirements' judgment
- **Data needed:** sweat-equity documentation (not in corpus)
- **Rationale:** Same family as G219; documentation presence is crisp, transaction-type eligibility stays partly human.
- **Guide candidate:** B3-4.3-13 — Sweat Equity (PDF p.457)
- **Guide candidate:** B5-5.3-03 — Shared Equity Transactions: Eligibility, Underwriting and Collateral Requirements (PDF p.802)
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **SME:** [ ] agree [ ] correct: ______

### G279 — O-FNM-00285 [O-FNM]
- **Q:** Were all trade equity asset requirements met?
- **Defect condition:** No, documentation showing the trade equity meets Fannie Mae's requirements not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 314
- **Severity:** Critical
- **Data needed:** same trade-equity documentation gap as G204/G220/G221
- **Rationale:** Same family as G220.
- **Guide candidate:** A2-5-01 — Fannie Mae Trade Name and Trademarks (PDF p.102)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** A3-1-01 — Fannie Mae’s Technology Products (PDF p.106)
- **SME:** [ ] agree [ ] correct: ______

### G281 — O-FRD-50457 [O-FRD]
- **Q:** Were all trust fund requirements met?
- **Defect condition:** Evidence of receipt of trust funds needed to close not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 321
- **Severity:** Critical
- **Data needed:** trust fund receipt evidence (not in corpus)
- **Rationale:** Same trust family as G197/G214/G283.
- **SME:** [ ] agree [ ] correct: ______

### G283 — O-FRD-50456 [O-FRD]
- **Q:** Were all trust fund requirements met?
- **Defect condition:** Trust funds-No Trust Agmt/Trust Mgr Stmnt naming borr as beneficiary & amount available to disburse
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 322
- **Severity:** Critical
- **Data needed:** trust agreement/trustee statement (not in corpus)
- **Rationale:** Same trust family as G197/G214/G281.
- **SME:** [ ] agree [ ] correct: ______

### G284 — O-FNM-50260 [O-FNM]
- **Q:** Were all verification of deposit assets requirements met?
- **Defect condition:** Funds recently deposited in US bank by non-US citizen were not sourced
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 170
- **Severity:** Critical
- **Data needed:** citizenship/foreign-national documentation (not in corpus)
- **Rationale:** Related to the large-deposit family, but citizenship data isn't modeled at all — a genuinely separate, absent fixture.
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **Guide candidate:** B3-3.4-06 — Employment Related Assets as Qualifying Income (PDF p.358)
- **SME:** [ ] agree [ ] correct: ______

### G286 — O-FNM-00214 [O-FNM]
- **Q:** Were all verification of deposit assets requirements met?
- **Defect condition:** No, a VOD or account statement verifying each account not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 333
- **Severity:** Critical
- **Data needed:** VOD form (not in corpus)
- **Rationale:** Same VOD family as G001/G002/G097/G105/G256/G257.
- **Guide candidate:** B3-3.4-06 — Employment Related Assets as Qualifying Income (PDF p.358)
- **Guide candidate:** B3-4.2-01 — Veriﬁcation of Deposits and Assets (PDF p.430)
- **Guide candidate:** B3-4.2-05 — Foreign Assets (PDF p.438)
- **SME:** [ ] agree [ ] correct: ______

### G289 — O-FNM-50257 [O-FNM]
- **Q:** Were all verification of deposit assets requirements met?
- **Defect condition:** The bank statements did not include all account identifying information
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 112
- **Severity:** Critical
- **Data needed:** account-identifying-information field (deepen bank_statement FIELD_SPECS)
- **Rationale:** bank_statement doc is already parsed for every loan that has one; a distinct account-number/identifying-info field is a plausible near-term Bucket-B win, not implemented here.
- **Guide candidate:** A2-2-02 — Delivery Information and Delivery-Option Speciﬁc Representations and Warranties (PDF p.34)
- **Guide candidate:** A3-4-01 — Conﬁdentiality of Information (PDF p.137)
- **Guide candidate:** A4-1-02 — Submission of Financial Statements and Reports (PDF p.158)
- **SME:** [ ] agree [ ] correct: ______

### G292 — Custodial Acct [GENERIC]
- **Q:** Were the funds from an acceptable source when a custodial account was utilized?
- **Defect condition:** Ineligible custodial account (UTMA) and/or (UGMA) was used to qualify
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 329
- **Severity:** Critical
- **Data needed:** custodial account (UTMA/UGMA) statement (not in corpus)
- **Rationale:** Crisp eligibility check once the document exists.
- **Guide candidate:** B3-2-06 — Approve/Ineligible Recommendations (PDF p.307)
- **Guide candidate:** B3-4.2-04 — Pooled Savings (Community Savings Funds) (PDF p.438)
- **Guide candidate:** B3-4.3-01 — Stocks, Stock Options, Bonds, and Mutual Funds (PDF p.439)
- **SME:** [ ] agree [ ] correct: ______

### G295 — O-VA-51666 [O-VA]
- **Q:** Where the transaction allows for gift funds to be used, does the file contain an acceptable gift letter and were the gift funds verified correctly?
- **Defect condition:** The gift funds were not provided by an acceptable source
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 298
- **Severity:** Critical
- **Stays human:** donor-acceptability guideline judgment
- **Data needed:** donor-relationship field (deepen gift_letter)
- **Rationale:** Same donor-acceptability family as G110/G119/G133/G142 (VA wording variant).
- **SME:** [ ] agree [ ] correct: ______

### G296 — O-VA-51668 [O-VA]
- **Q:** Where the transaction allows for gift funds to be used, does the file contain an acceptable gift letter and were the gift funds verified correctly?
- **Defect condition:** Transfer of gift funds not documented with bank statements or as being received by the closing agent
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 317
- **Severity:** Critical
- **Data needed:** transfer-method field, same gift-transfer family as G108/G127/G131
- **Rationale:** Worth SME review before wiring to gift_transfer_evidence_in_file (same caution as G108/G127/G131).
- **SME:** [ ] agree [ ] correct: ______

## RED

### G012 — O-VA-00261 [O-VA]
- **Q:** Does the file contain sufficient documentation for other assets?
- **Defect condition:** Funds saved at home did not document reasonable explanation from the borrower of how money was saved
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 175
- **Severity:** Critical
- **Stays human:** 'reasonable explanation... how money was saved'
- **Rationale:** Narrative/judgment call on the borrower's own explanation — same class as application-verification's judgment-word REDs.
- **SME:** [ ] agree [ ] correct: ______

### G018 — O-FRD-50459 [O-FRD]
- **Q:** Were all Community Savings System funds requirements met?
- **Defect condition:** All requirements not met for use of funds in a Community Savings System
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 130
- **Severity:** Critical
- **Stays human:** open-ended 'all requirements not met for use of funds in a Community Savings System'
- **Rationale:** Bare catch-all with no specific fact stated — needs SME decomposition into the actual Community-Savings-System documentation checklist, same pattern as application-verification's VA disclosure catch-all.
- **SME:** [ ] agree [ ] correct: ______

### G020 — O-FRD-51837 [O-FRD]
- **Q:** Were all Employer Assisted Homeownership (EAH) benefit requirements met?
- **Defect condition:** Employer Assisted Homeownership (EAH) Benefit requirements not met for the type of benefit received
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 150
- **Severity:** Critical
- **Stays human:** 'requirements not met for the type of benefit received' (type-dependent, unstated)
- **Rationale:** Open-ended, benefit-type-dependent catch-all — no single checkable fact until an SME enumerates EAH benefit types and their individual requirements.
- **SME:** [ ] agree [ ] correct: ______

### G023 — O-FRD-50458 [O-FRD]
- **Q:** Were all Individual Development Account (IDA) requirements met?
- **Defect condition:** All requirements not met for use of Individual Development Account (IDA)
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 204
- **Severity:** Critical
- **Stays human:** open-ended 'all requirements not met for use of Individual Development Account (IDA)'
- **Rationale:** Same bare-catch-all pattern as G018.
- **SME:** [ ] agree [ ] correct: ______

### G035 — O-FNM-50265 [O-FNM]
- **Q:** Were all anticipated savings and cash-on-hand asset requirements met?
- **Defect condition:** Anticipated savings considered were unreasonable or calculated incorrectly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 104
- **Severity:** Critical
- **Stays human:** 'unreasonable' savings judgment
- **Rationale:** 'Unreasonable' dominates the compound condition even though 'calculated incorrectly' alone would be crisp math — no anticipated-savings plan data exists to compute against regardless.
- **Guide candidate:** B3-4.3-20 — Anticipated Savings and Cash-on-Hand (PDF p.463)
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **Guide candidate:** B2-1.3-03 — Cash-Out Reﬁnance Transactions (PDF p.197)
- **SME:** [ ] agree [ ] correct: ______

### G053 — O-FNM-52792, O-FRD-00375 [O-FNM/O-FRD]
- **Q:** Were all business account asset requirements met?
- **Defect condition:** File did not document that withdrawal of business assets will not be detrimental to the business
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 326, 327
- **Severity:** Critical
- **Stays human:** 'not detrimental to the business' judgment
- **Rationale:** Classic subjective business-impact judgment — no bright-line test.
- **Guide candidate:** A2-2-03 — Document Warranties (PDF p.36)
- **Guide candidate:** A3-3-04 — Document Custodians (PDF p.133)
- **Guide candidate:** B3-3.4-06 — Employment Related Assets as Qualifying Income (PDF p.358)
- **SME:** [ ] agree [ ] correct: ______

### G055 — O-FHA-02252 [O-FHA]
- **Q:** Were all cash on hand requirements met?
- **Defect condition:** Cash on hand was not reasonable and has not been deposited or held by escrow
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 121
- **Severity:** Critical
- **Stays human:** 'not reasonable' cash-on-hand judgment
- **Rationale:** 'Reasonable' dominates; deposit/escrow half is bundled into the same compound condition rather than checkable standalone.
- **SME:** [ ] agree [ ] correct: ______

### G058 — O-FHA-00771 [O-FHA]
- **Q:** Were all cash to close requirements met?
- **Defect condition:** Fees and charges are not reasonable and customary or evidence of fee markups is identified
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 250
- **Severity:** Critical
- **Stays human:** 'reasonable and customary' fee judgment
- **Rationale:** Fee-reasonableness determination — the same judgment class as application-verification's fee/discrepancy REDs.
- **SME:** [ ] agree [ ] correct: ______

### G098 — O-FRD-00210 [O-FRD]
- **Q:** Were all general asset documentation requirements met?
- **Defect condition:** Asset documents did not meet Streamlined Accept or Standard documentation LPA req's per asset type
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 227
- **Severity:** Critical
- **Stays human:** 'Streamlined Accept or Standard documentation... per asset type' matrix
- **Rationale:** Open-ended compliance check across an entire LPA documentation matrix spanning many asset types — needs SME decomposition before any single fact is checkable, same pattern as application-verification's VA disclosure catch-all.
- **SME:** [ ] agree [ ] correct: ______

### G101 — O-FRD-02031 [O-FRD]
- **Q:** Were all general asset documentation requirements met?
- **Defect condition:** No, third-party verification requirements not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 310
- **Severity:** Critical
- **Stays human:** 'third-party verification requirements' (unspecified)
- **Rationale:** Vague catch-all with zero stated specifics — needs SME decomposition.
- **SME:** [ ] agree [ ] correct: ______

### G157 — O-FNM-00577 [O-FNM]
- **Q:** Were all interested party contributions requirements met?
- **Defect condition:** Interested party contribution does not reflect consistent fees/expenses/resolution of discrepancies
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 211
- **Severity:** Critical
- **Stays human:** 'consistent fees/expenses/resolution of discrepancies'
- **Rationale:** Open-ended cross-file discrepancy sweep — same judgment class as application-verification's file-wide-discrepancies RED.
- **Guide candidate:** B3-4.1-02 — Interested Party Contributions (IPCs) (PDF p.423)
- **Guide candidate:** A2-3.3-01 — Compensatory Fees (PDF p.76)
- **Guide candidate:** A3-3-01 — Outsourcing of Mortgage Processing and Third-Party Originations (PDF p.123)
- **SME:** [ ] agree [ ] correct: ______

### G165 — O-FNM-59271 [O-FNM]
- **Q:** Were all interested party contributions requirements met?
- **Defect condition:** There is evidence of undisclosed IPC's resulting in the loan being ineligible for sale to Fannie Mae
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 325
- **Severity:** Critical
- **Stays human:** 'undisclosed IPC's... ineligible for sale to Fannie Mae' investor-eligibility judgment
- **Rationale:** Holistic GSE-investor-eligibility determination, not a single checkable fact — stays human.
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** B3-4.1-02 — Interested Party Contributions (IPCs) (PDF p.423)
- **Guide candidate:** C3-7-07 — Sale of Fannie Mae Securities to Third Parties (PDF p.1049)
- **SME:** [ ] agree [ ] correct: ______

### G190 — O-RHS-02783 [O-RHS]
- **Q:** Were all other asset requirements met?
- **Defect condition:** Borr disposed of assets in last 2 yrs, did not verify not disposed for less than fair market value
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 145
- **Severity:** Critical
- **Stays human:** 'less than fair market value' determination
- **Rationale:** Fair-market-value judgment without an appraisal-like valuation document; also needs a 2-year asset-disposal history this pilot doesn't track at all.
- **SME:** [ ] agree [ ] correct: ______

### G193 — O-RHS-02782 [O-RHS]
- **Q:** Were all other asset requirements met?
- **Defect condition:** No written explanation for how cash on hand funds were accumulated and length of time saved
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 122
- **Severity:** Critical
- **Stays human:** 'no written explanation... how... accumulated' narrative adequacy
- **Rationale:** Same narrative-adequacy judgment class as G012.
- **SME:** [ ] agree [ ] correct: ______

### G196 — O-FNM-50259 [O-FNM]
- **Q:** Were all other asset type requirements met?
- **Defect condition:** All requirements for a pooled savings were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 243
- **Severity:** Critical
- **Stays human:** open-ended 'all requirements for a pooled savings were not met'
- **Rationale:** Bare catch-all, same pattern as G018/G023.
- **Guide candidate:** B3-4.2-04 — Pooled Savings (Community Savings Funds) (PDF p.438)
- **Guide candidate:** A3-3-03 — Other Servicing Arrangements (PDF p.131)
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **SME:** [ ] agree [ ] correct: ______

### G228 — Asset-1 [GENERIC]
- **Q:** Were all recurring payments reflected on bank statements addressed?
- **Defect condition:** All recurring payments that are reflected on bank statements were not addressed by the underwriter
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 222
- **Severity:** Critical
- **Stays human:** underwriter review-completeness sweep across all recurring bank-statement items
- **Rationale:** An underwriter's own review-completion judgment across every recurring payment — inherently a process/judgment check, not a bright-line fact the file can self-certify.
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** A4-1-02 — Submission of Financial Statements and Reports (PDF p.158)
- **Guide candidate:** B3-3.3-06 — Mortgage Diﬀerential Payments Income (PDF p.343)
- **SME:** [ ] agree [ ] correct: ______

### G265 — O-FNM-50201 [O-FNM]
- **Q:** Were all secondary financing requirements met?
- **Defect condition:** All re-subordination requirements were not met for refinance transactions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 269
- **Severity:** Critical
- **Stays human:** open-ended 'all re-subordination requirements were not met'
- **Rationale:** As worded, a bare catch-all with zero specifics — same pattern as G018/G023/G196, even though 're-subordination' names a definable process an SME could later decompose.
- **Guide candidate:** B5-3.1-02 — Conversion of Construction-to-Permanent Financing: Single-Closing Transactions (PDF p.736)
- **Guide candidate:** B5-3.1-03 — Conversion of Construction-to-Permanent Financing: Two-Closing Transactions (PDF p.743)
- **Guide candidate:** A2-4.1-03 — Electronic Records, Signatures, and Transactions (PDF p.89)
- **SME:** [ ] agree [ ] correct: ______

## NOT_A_CHECK

### G003 —  [O-VA]
- **Q:** Does the file contain sufficient asset documentation for checking/savings?
- **Defect condition:** Yes, all checking/savings asset requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 471
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G006 —  [O-VA]
- **Q:** Does the file contain sufficient asset documentation for net proceeds?
- **Defect condition:** Yes, all net proceeds asset requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 472
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G008 —  [O-VA]
- **Q:** Does the file contain sufficient asset documentation for secondary financing?
- **Defect condition:** Yes, all secondary financing asset requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 473
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G014 —  [O-VA]
- **Q:** Does the file contain sufficient documentation for other assets?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 474, 475
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G019 —  [O-FRD]
- **Q:** Were all Community Savings System funds requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 431, 432
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G021 —  [O-FRD]
- **Q:** Were all Employer Assisted Homeownership (EAH) benefit requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 447, 448
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G024 —  [O-FRD]
- **Q:** Were all Individual Development Account (IDA) requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 437, 438
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G026 —  [O-FRD]
- **Q:** Were all additional general asset documentation requirements met?_x000D_
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 458, 459
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G029 —  [O-FRD]
- **Q:** Were all additional other asset type requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 456, 457
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G032 —  [O-FNM]
- **Q:** Were all anticipated sales proceeds asset requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 398, 399
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G036 —  [O-FNM]
- **Q:** Were all anticipated savings and cash-on-hand asset requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 418, 419
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G041 —  [O-FNM]
- **Q:** Were all asset verification documentation requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 420, 421
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G046 —  [O-FNM]
- **Q:** Were all borrowed funds secured by an asset requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 408, 409
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G048 —  [O-FNM]
- **Q:** Were all bridge/swing loan asset requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 406, 407
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G054 —  [O-FNM/O-FRD/O-RHS]
- **Q:** Were all business account asset requirements met?
- **Defect condition:** Yes, all business account asset requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 425, 455, 466
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G056 —  [O-FHA]
- **Q:** Were all cash on hand requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 363, 364
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G059 —  [O-FHA]
- **Q:** Were all cash to close requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 359, 360
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G063 —  [O-FNM]
- **Q:** Were all cash value of life insurance asset requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 416, 417
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G067 —  [O-FHA]
- **Q:** Were all checking and savings account requirements met?
- **Defect condition:** Yes, all checking and savings account requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 362
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G074 —  [O-RHS]
- **Q:** Were all checking/savings asset requirements met?
- **Defect condition:** Yes, all checking/savings asset requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 460
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G078 —  [O-FNM]
- **Q:** Were all credit card financing and rewards points asset requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 410, 411
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G080 —  [O-FHA]
- **Q:** Were all down payment assistance programs requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 372, 373
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G083 —  [O-FNM/O-RHS]
- **Q:** Were all earnest money deposit asset requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 396, 397, 461, 462
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G085 —  [O-FRD]
- **Q:** Were all earnest money deposit requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 453, 454
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G087 —  [O-FHA]
- **Q:** Were all earnest money deposit requirements met?
- **Defect condition:** Yes, all earnest money deposit requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 358
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G089 —  [O-FNM]
- **Q:** Were all employer assistance asset requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 394, 395
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G091 —  [O-FHA]
- **Q:** Were all employer assistance benefits requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 378, 379
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G093 —  [O-FRD]
- **Q:** Were all foreign fund requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 433, 434
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G106 —  [O-FRD]
- **Q:** Were all general asset documentation requirements met?
- **Defect condition:** Yes, all general asset documentation requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 428
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G118 —  [O-FNM]
- **Q:** Were all gift and/or grant asset requirements met?
- **Defect condition:** Yes, all gift and/or grant asset requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 393
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G129 —  [O-FRD]
- **Q:** Were all gift and/or grant fund requirements met?
- **Defect condition:** Yes, all gift and/or grant fund requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 446
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G136 —  [O-RHS]
- **Q:** Were all gift asset requirements met?
- **Defect condition:** Yes, all gift asset requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 463
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G143 —  [O-FHA]
- **Q:** Were all gifts requirements met?
- **Defect condition:** Yes, all gifts requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 369
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G145 —  [O-FRD]
- **Q:** Were all government bond requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 435, 436
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G147 —  [O-FHA]
- **Q:** Were all grants requirements met?
- **Defect condition:** Yes, all grants requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 377
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G151 —  [O-FRD]
- **Q:** Were all interested party contribution requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 449, 450
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G161 —  [O-FHA/O-FNM]
- **Q:** Were all interested party contributions requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 370, 371, 389, 390
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G168 —  [O-FRD]
- **Q:** Were all life insurance requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 439, 440
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G172 —  [O-FRD]
- **Q:** Were all liquidation or sale of asset requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 441, 442
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G177 —  [O-FHA]
- **Q:** Were all minimum required investment (MRI) requirements met?
- **Defect condition:** Yes, all minimum required investment (MRI) requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 361
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G178 —  [O-FNM]
- **Q:** Were all minimum reserve requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 387, 388
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G184 —  [O-FHA]
- **Q:** Were all net proceeds asset requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 382, 383
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G188 —  [O-RHS]
- **Q:** Were all net proceeds asset requirements met?
- **Defect condition:** Yes, all net proceeds asset requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 467
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G194 —  [O-RHS]
- **Q:** Were all other asset requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 464, 465
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G208 —  [O-FNM/O-FRD]
- **Q:** Were all other asset type requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 422, 423, 451, 452
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G216 —  [O-FHA]
- **Q:** Were all other assets requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 380, 381
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G222 —  [O-FNM]
- **Q:** Were all personal unsecured loans asset requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 412, 413
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G224 —  [O-FHA]
- **Q:** Were all private savings clubs requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 367, 368
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G227 —  [O-FRD]
- **Q:** Were all real estate commission requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 429, 430
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G229 —  [GENERIC]
- **Q:** Were all recurring payments reflected on bank statements addressed?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 336, 337
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G230 —  [O-FNM]
- **Q:** Were all rent credit for option to purchase asset requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 402, 403
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G239 —  [O-FHA]
- **Q:** Were all requirements met for loans obtained to be used as available assets?_x000D_
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 375, 376
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G242 —  [O-FRD]
- **Q:** Were all reserve requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 426, 427
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G245 —  [O-FHA]
- **Q:** Were all reserves/cash to close requirements met?_x000D_
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 384, 385, 386
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G250 —  [O-FNM]
- **Q:** Were all retirement account asset requirements met?
- **Defect condition:** Yes, all retirement account asset requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 392
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G253 —  [O-FHA]
- **Q:** Were all retirement account requirements met?
- **Defect condition:** Yes, all retirement account requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 365
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G258 —  [O-FRD]
- **Q:** Were all retirement fund requirements met?
- **Defect condition:** Yes, all retirement fund requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 443
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G259 —  [O-FNM]
- **Q:** Were all sale of personal assets requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 414, 415
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G264 —  [O-RHS]
- **Q:** Were all secondary financing (bridge loan) asset requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 468, 469
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G272 —  [O-FHA/O-FNM]
- **Q:** Were all secondary financing requirements met?
- **Defect condition:** Yes, all secondary financing requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 374, 424
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G274 —  [O-FHA]
- **Q:** Were all stocks and bonds requirements met?
- **Defect condition:** Yes, all stocks and bonds requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 366
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G276 —  [O-RHS]
- **Q:** Were all stocks/bonds asset requirements met?
- **Defect condition:** Yes, all stocks/bonds  asset requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 470
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G277 —  [O-FNM]
- **Q:** Were all sweat equity asset requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 404, 405
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G280 —  [O-FNM]
- **Q:** Were all trade equity asset requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 400, 401
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G282 —  [O-FRD]
- **Q:** Were all trust fund requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 444, 445
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G290 —  [O-FNM]
- **Q:** Were all verification of deposit assets requirements met?
- **Defect condition:** Yes, all verification of deposit assets requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 391
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G291 —  [GENERIC]
- **Q:** Were assets utilized from any of the following to qualify the loan?
- **Defect condition:** The loan program did not require assets to qualify
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357
- **Rationale:** Screening/applicability answer branch ('the loan program did not require assets to qualify'), not a defect condition — same pattern as application-verification's LEP-applicability screening group.
- **SME:** [ ] agree [ ] correct: ______

### G293 —  [GENERIC]
- **Q:** Were the funds from an acceptable source when a custodial account was utilized?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 338, 339
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G297 —  [O-VA]
- **Q:** Where the transaction allows for gift funds to be used, does the file contain an acceptable gift letter and were the gift funds verified correctly?
- **Defect condition:** Yes, all gift funds asset requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 476
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

