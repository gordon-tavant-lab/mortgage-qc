# SME Review Packet — product-specific-check block triage

**704 rules / 703 unique (question, condition) groups.** Every classification
below is a *proposal* pending your review — mark each check agree / correct.
Bins: GREEN = automatable now (none found here — see the decision doc) · YELLOW = automatable after data/guide work · RED = stays human · NOT_A_CHECK = pass/N-A answer option, not a defect rule.

**Source workbook:** `PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv` — row numbers below are Excel-style
(header = row 1), so you can open the sheet and jump straight to each rule.

**Note on this block vs application-verification / asset-verification:** dedup collapse is essentially zero here (704 rules -> 703 groups, ~1.001x) — this is the most agency/product-fragmented of the three blocks triaged so far, by design (FHA/VA/USDA/ARM/refi-program-specific rules rarely share wording across agencies). Group-by-group hand review (marked `classification_method: "hand_verified"` in the JSON) covers every RED, every doc_presence group, both existing product-specific shapes' candidates, and every READY-TO-BUILD candidate. The remaining groups (`classification_method: "bulk_heuristic"`) are classified YELLOW by a documented, transparent keyword heuristic (see the script's module docstring) rather than individually hand-authored prose — read the condition text yourself before treating any bulk-heuristic rationale as final.

## Headline

| Bin | Groups | Rules | % of defect groups |
|---|---|---|---|
| GREEN | 0 | 0 | 0% |
| YELLOW | 572 | 572 | 97% |
| RED | 17 | 17 | 3% |
| NOT_A_CHECK | 114 | 115 | — |

**Classification method:** 97 hand-verified (RED/doc_presence-downgrade/ready-to-build groups, individually read in full), 108 mechanical pass-answer (NOT_A_CHECK via PASS_RE), 498 bulk-heuristic (of 703 total groups).

## READY TO BUILD candidates (flagged, not implemented)

- **G483** (O-RHS, row 3638): PARTIAL — new shape, no new fixture: `compensating_factors_documented` (FACT_SPECS in extract_loan.py, extracted from usda_ratio_waiver_doc's 'Compensating Factors Documented ... NOT IN FILE' line) is ALREADY extracted and ALREADY correctly populated False for loan 05 — but is cited by ZERO existing SHACL shapes (RatioWaiverShape only cites piti_ratio/piti_guideline/dti_ratio/dti_guideline/usda_ratio_waiver_in_file, never this fact). G483's condition ('the eligible compensating factors supporting the use of the waiver was not supported with documentation' in a PURCHASE GUS-refer/manual-UW) matches this fact directly. Needs a NEW shape (not an extension of RatioWaiverShape, which tests a different clause), gated on loan_purpose_1003 containing 'Purchase' to avoid double-firing against G491's refinance-transaction sibling (same fact, opposite transaction-type gate) — verified the gating field (loan_purpose_1003) already exists before flagging this.
- **G491** (O-RHS, row 3647): PARTIAL, refinance sibling of G483 — same `compensating_factors_documented` fact, gated on loan_purpose_1003 NOT containing 'Purchase' instead. Two separate shapes (or one shape with a purpose branch) needed so the two AMQ exception codes (G483 purchase / G491 refinance) don't collide on the same underlying fact.

## GREEN

## YELLOW

### G006 — PORTExcept [GENERIC]
- **Q:** Are all Portfolio Expanded Authority Guidelines met?
- **Defect condition:** Final terms/tolerances and conditions for Port Exception were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3614
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B3-2-10 — Accuracy of DU Data, DU Tolerances, and Errors in the Credit Report (PDF p.313)
- **Guide candidate:** C2-1.1-03 — Mandatory Commitment Terms, Amounts, Periods and Other Requirements (PDF p.964)
- **Guide candidate:** C2-1.2-03 — Best Eﬀorts Commitment Terms, Amounts, and Other Requirements (PDF p.975)
- **SME:** [ ] agree [ ] correct: ______

### G008 — PORTDTI [GENERIC]
- **Q:** Are all Portfolio Expanded Authority Guidelines met?
- **Defect condition:** The DTI exceeds the maximum 50%
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3612
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '50%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G009 — PORTPolicy [GENERIC]
- **Q:** Are all Portfolio Expanded Authority Guidelines met?
- **Defect condition:** The compensating factors were not met according to credit policy
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3621
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** A3-5-02 — Fidelity Bond Policy Requirements (PDF p.147)
- **Guide candidate:** A3-5-03 — Errors and Omissions Policy Requirements (PDF p.148)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G011 — PORTAssetCalcs [GENERIC]
- **Q:** Are all Portfolio loan overlays met?
- **Defect condition:** Asset dissipation appropriate income calculator was not completed accurately
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3607
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** asset-dissipation income-calculator re-derivation (asset total / dissipation term)
- **Data needed:** asset-dissipation calculator fields (total assets, dissipation period) — not in FIELD_SPECS today
- **Rationale:** 'Accurately' names a specific, re-computable formula (an asset-dissipation calculator), not an open-ended judgment — crisp math once the input fields exist.
- **Guide candidate:** B3-3.1-03 — Income Calculator (PDF p.323)
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **SME:** [ ] agree [ ] correct: ______

### G012 — PORTAssetDispLoan [GENERIC]
- **Q:** Are all Portfolio loan overlays met?
- **Defect condition:** Asset dissipation loan and assets were being counted in DU as both income and reserves
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3608
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B3-3.4-06 — Employment Related Assets as Qualifying Income (PDF p.358)
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **SME:** [ ] agree [ ] correct: ______

### G013 — PORTCapGains [GENERIC]
- **Q:** Are all Portfolio loan overlays met?
- **Defect condition:** Capital losses reflected on tax returns not considered (A/I & manually UW loans)
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3611
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.6-01 — General Information on Analyzing Individual Tax Returns (PDF p.390)
- **Guide candidate:** B4-2.3-04 — Loan Eligibility for Co-op Share Loans (PDF p.712)
- **SME:** [ ] agree [ ] correct: ______

### G014 — PORTLoanAmount [GENERIC]
- **Q:** Are all Portfolio loan overlays met?
- **Defect condition:** Loan amount >$2M and additional appraisal requirements were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3619
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '$2'
- **Data needed:** a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'appraisal', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** A2-4.1-01 — Establishing Loan Files (PDF p.78)
- **SME:** [ ] agree [ ] correct: ______

### G015 — PORTTrade [GENERIC]
- **Q:** Are all Portfolio loan overlays met?
- **Defect condition:** Loan did not meet minimum tradeline requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3626
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** A2-4.1-01 — Establishing Loan Files (PDF p.78)
- **SME:** [ ] agree [ ] correct: ______

### G016 — Port Exception [GENERIC]
- **Q:** Are all Portfolio loan overlays met?
- **Defect condition:** Port exception granted w/o proper docs and/or no approval by Portfolio Dept located
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3615
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** A1-1-01 — Application and Approval of Seller/Servicer (PDF p.20)
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **SME:** [ ] agree [ ] correct: ______

### G019 — PORTSSI [GENERIC]
- **Q:** Are all Portfolio loan overlays met?
- **Defect condition:** The borrower is drawing on SSI and the social security award letter was not located
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3624
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B3-3.4-15 — Social Security Income (PDF p.371)
- **Guide candidate:** B5-3.2-02 — HomeStyle Renovation Mortgages: Loan and Borrower Eligibility (PDF p.747)
- **Guide candidate:** B5-6-01 — HomeReady Mortgage Loan and Borrower Eligibility (PDF p.808)
- **SME:** [ ] agree [ ] correct: ______

### G020 — PORTLLC [GENERIC]
- **Q:** Are all Portfolio loan overlays met?
- **Defect condition:** The loan closed in an LLC or Trust and all conditions weren't met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3618
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** A2-4.1-01 — Establishing Loan Files (PDF p.78)
- **SME:** [ ] agree [ ] correct: ______

### G021 — PORTFootprint [GENERIC]
- **Q:** Are all Portfolio loan overlays met?
- **Defect condition:** The loan outside of bank's footprint and conditions were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3616
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** A2-4.1-01 — Establishing Loan Files (PDF p.78)
- **SME:** [ ] agree [ ] correct: ______

### G022 — PORTSelfEmploy [GENERIC]
- **Q:** Are all Portfolio loan overlays met?
- **Defect condition:** The self employed borrower's YTD P&L's/Balance sheets are not through the most recent quarter
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3623
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-1-01 — High-Balance Mortgage Loan Eligibility and Underwriting (PDF p.715)
- **Guide candidate:** B5-3.2-02 — HomeStyle Renovation Mortgages: Loan and Borrower Eligibility (PDF p.747)
- **Guide candidate:** B5-6-01 — HomeReady Mortgage Loan and Borrower Eligibility (PDF p.808)
- **SME:** [ ] agree [ ] correct: ______

### G023 — PORTArmsLength [GENERIC]
- **Q:** Are all Portfolio loan overlays met?
- **Defect condition:** There is evidence of Non-Arms Length transactions and additional conditions were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3606
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** A2-4.1-01 — Establishing Loan Files (PDF p.78)
- **SME:** [ ] agree [ ] correct: ______

### G024 — PORTBizAssets [GENERIC]
- **Q:** Are all Portfolio loan overlays met?
- **Defect condition:** Using business accounts as assets, and all criteria was not met (see 3.15.4.7 of Port guides)
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3610
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** A2-4.1-01 — Establishing Loan Files (PDF p.78)
- **SME:** [ ] agree [ ] correct: ______

### G026 — CTPCC [GENERIC]
- **Q:** Are all the Portfolio/CTP program guidelines met?
- **Defect condition:** Construction Committee approval was not located or does not match final terms
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3409
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** A1-1-01 — Application and Approval of Seller/Servicer (PDF p.20)
- **Guide candidate:** B3-3.4-14 — Section 8 Housing Choice Voucher Homeownership Program Payments (PDF p.370)
- **Guide candidate:** B4-1.3-06 — Property Condition and Quality of Construction of the Improvements (PDF p.587)
- **SME:** [ ] agree [ ] correct: ______

### G027 — CTPDisclosure [GENERIC]
- **Q:** Are all the Portfolio/CTP program guidelines met?
- **Defect condition:** Missing 1) CTP draw disb notification and/or CTP Indemnity
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3412
- **Severity:** Major
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B3-3.4-14 — Section 8 Housing Choice Voucher Homeownership Program Payments (PDF p.370)
- **Guide candidate:** C3-1-01 — General Information About Fannie Mae’s MBS Program (PDF p.993)
- **SME:** [ ] agree [ ] correct: ______

### G029 — CTPLand [GENERIC]
- **Q:** Are all the Portfolio/CTP program guidelines met?
- **Defect condition:** Property acquired subject/land within 6 months of application & funds not sourced
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3414
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** 6-month acquisition-to-application date comparison + funds-sourcing doc presence
- **Data needed:** land/property acquisition date field + funds-sourcing documentation (not in corpus)
- **Rationale:** Has a genuine crisp threshold (6 months) and a named doc requirement (closing disclosure from the acquisition); 'adequately sourced' is flavor text around an otherwise crisp date/doc test.
- **Guide candidate:** B3-6-03 — Monthly Housing Expense for the Subject Property (PDF p.518)
- **Guide candidate:** A1-1-01 — Application and Approval of Seller/Servicer (PDF p.20)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **SME:** [ ] agree [ ] correct: ______

### G030 — CTPTax [GENERIC]
- **Q:** Are all the Portfolio/CTP program guidelines met?
- **Defect condition:** Qualifying RE taxes not calculated using proposed completed value
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3416
- **Severity:** Major
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **Guide candidate:** B2-1.2-01 — Loan-to-Value (LTV) Ratios (PDF p.179)
- **Guide candidate:** B2-1.2-02 — Combined Loan-to-Value (CLTV) Ratios (PDF p.181)
- **SME:** [ ] agree [ ] correct: ______

### G031 — CTPARB [GENERIC]
- **Q:** Are all the Portfolio/CTP program guidelines met?
- **Defect condition:** The ARB approval was not found
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3408
- **Severity:** Major
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** A1-1-01 — Application and Approval of Seller/Servicer (PDF p.20)
- **Guide candidate:** B3-3.4-14 — Section 8 Housing Choice Voucher Homeownership Program Payments (PDF p.370)
- **Guide candidate:** C3-1-01 — General Information About Fannie Mae’s MBS Program (PDF p.993)
- **SME:** [ ] agree [ ] correct: ______

### G032 — CTPApprove [GENERIC]
- **Q:** Are all the Portfolio/CTP program guidelines met?
- **Defect condition:** The CEC approval conditions were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3407
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** D1-3-02 — Lender Post-Closing Quality Control Review of Approval Conditions, Underwriting Decisions, Data, and Documentation (PDF p.1068)
- **Guide candidate:** A1-1-01 — Application and Approval of Seller/Servicer (PDF p.20)
- **Guide candidate:** B3-3.4-14 — Section 8 Housing Choice Voucher Homeownership Program Payments (PDF p.370)
- **SME:** [ ] agree [ ] correct: ______

### G033 — CTPReserves [GENERIC]
- **Q:** Are all the Portfolio/CTP program guidelines met?
- **Defect condition:** The borrower does not have sufficient contingency reserves in addition to PITI reserves as required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3415
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** contingency-reserves-vs-PITI-reserves math
- **Data needed:** CTP contingency-reserve requirement threshold (an SME-supplied constant, not stated in this row) + reserves fields
- **Rationale:** Has a real comparison basis (PITI reserves) even though the specific required contingency percentage isn't stated in-row — crisp once an SME supplies the threshold and reserves fields exist.
- **Guide candidate:** B2-2-01 — General Borrower Eligibility Requirements (PDF p.241)
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **Guide candidate:** B2-2-03 — Multiple Financed Properties for the Same Borrower (PDF p.244)
- **SME:** [ ] agree [ ] correct: ______

### G034 — CTPContract [GENERIC]
- **Q:** Are all the Portfolio/CTP program guidelines met?
- **Defect condition:** The construction contract does not meet CTP requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3410
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** A2-3.1-01 — Lender Breach of Contract (PDF p.56)
- **Guide candidate:** B2-1.3-05 — Payoﬀ of Installment Land Contract Requirements (PDF p.205)
- **Guide candidate:** B3-3.4-14 — Section 8 Housing Choice Voucher Homeownership Program Payments (PDF p.370)
- **SME:** [ ] agree [ ] correct: ______

### G035 — CTPCost [GENERIC]
- **Q:** Are all the Portfolio/CTP program guidelines met?
- **Defect condition:** The final Detailed Cost Breakdown does not match the final 1003 amount for Cost to Build
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3411
- **Severity:** Major
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'final_1003' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'final_1003', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B3-3.4-14 — Section 8 Housing Choice Voucher Homeownership Program Payments (PDF p.370)
- **Guide candidate:** B4-1.3-10 — Cost and Income Approach to Value (PDF p.604)
- **Guide candidate:** C3-1-01 — General Information About Fannie Mae’s MBS Program (PDF p.993)
- **SME:** [ ] agree [ ] correct: ______

### G036 — CTPInsure [GENERIC]
- **Q:** Are all the Portfolio/CTP program guidelines met?
- **Defect condition:** The insurance policy does not include appropriate builder's risk coverage endorsement/riders
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3413
- **Severity:** Major
- **Classification method:** hand_verified
- **Machine checks:** builder's-risk-coverage-endorsement presence
- **Data needed:** a named insurance endorsement/rider doc (not in corpus)
- **Rationale:** Comparison basis is a specific, named coverage type (builder's risk) — crisp presence check once the document exists; 'appropriate' is describing the pass/fail outcome, not the test itself.
- **Guide candidate:** B7-1-02 — Mortgage Insurance Coverage Requirements (PDF p.852)
- **Guide candidate:** B7-2-03 — General Title Insurance Coverage (PDF p.861)
- **Guide candidate:** B7-2-04 — Special Title Insurance Coverage Considerations (PDF p.863)
- **SME:** [ ] agree [ ] correct: ______

### G037 — UWAuth [GENERIC]
- **Q:** Does the underwriter have the proper lending authority for this loan amount or product and the required second level review was not completed?
- **Defect condition:** No-U/W does not have proper lending auth for this loan amount/product & 2nd level review not found
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3854
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** A2-4.1-01 — Establishing Loan Files (PDF p.78)
- **SME:** [ ] agree [ ] correct: ______

### G039 — PORTMedical [GENERIC]
- **Q:** If the loan is a Medical Professional loan, is all criteria met?
- **Defect condition:** Medical Professional guidelines are not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3620
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** professional-license status/duration evidence
- **Stays human:** 'does not fall within the guidelines of the medical professional program' (unstated criteria)
- **Data needed:** medical-professional license verification doc (not in corpus)
- **Rationale:** Compound: the license-evidence half names a real, checkable document; the 'guidelines' half states no specific criteria and stays human — kept YELLOW per the crisp-half-survives convention (asset-verification G007's pattern).
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** A2-4.1-01 — Establishing Loan Files (PDF p.78)
- **SME:** [ ] agree [ ] correct: ______

### G042 — PORTEmployer [GENERIC]
- **Q:** If this was an Portfolio Employer Guaranteed loan, were all the requirements met?
- **Defect condition:** The employer is not currently on the approved list
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3613
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** A2-4.1-01 — Establishing Loan Files (PDF p.78)
- **SME:** [ ] agree [ ] correct: ______

### G043 — PORTProgram [GENERIC]
- **Q:** If this was an Portfolio Employer Guaranteed loan, were all the requirements met?
- **Defect condition:** The loan did not close under one of the approved programs
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3622
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** A2-4.1-01 — Establishing Loan Files (PDF p.78)
- **SME:** [ ] agree [ ] correct: ______

### G044 — O-FNM-54320 [O-FNM]
- **Q:** In a RefiNow transaction, were all borrower benefit requirements met?
- **Defect condition:** RefiNow did not reduce interest rate by at least 50 basis points & the monthly mtg pymt not reduced
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3659
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.4-04 — Temporary Interest Rate Buydowns (PDF p.219)
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **Guide candidate:** B2-1.4-01 — Fixed-Rate Loans (PDF p.206)
- **SME:** [ ] agree [ ] correct: ______

### G046 — O-FNM-54306 [O-FNM]
- **Q:** In a RefiNow transaction, were all borrower eligibility requirements met?
- **Defect condition:** RefiNow all Note signors whose income is used not considered in determining income limit eligibility
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3668
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-2-01 — General Borrower Eligibility Requirements (PDF p.241)
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **Guide candidate:** B5-3.2-02 — HomeStyle Renovation Mortgages: Loan and Borrower Eligibility (PDF p.747)
- **SME:** [ ] agree [ ] correct: ______

### G047 — O-FNM-54305 [O-FNM]
- **Q:** In a RefiNow transaction, were all borrower eligibility requirements met?
- **Defect condition:** RefiNow total income is not less than or equal to 100% of the AMI limit for the subject's location
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3654
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '100%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-2-01 — General Borrower Eligibility Requirements (PDF p.241)
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **SME:** [ ] agree [ ] correct: ______

### G049 — O-FNM-54310 [O-FNM]
- **Q:** In a RefiNow transaction, were all existing loan eligibility documentation requirements met?
- **Defect condition:** The loan refinanced into a RefiNow was a high LTV refinance, DU Refi Plus loan, or Refi Plus loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3664
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-7-01 — High LTV Reﬁnance Loan and Borrower Eligibility (PDF p.819)
- **Guide candidate:** B5-7-02 — High LTV Reﬁnance Underwriting, Documentation, and Collateral Requirements for the New Loan (PDF p.824)
- **Guide candidate:** B5-1-01 — High-Balance Mortgage Loan Eligibility and Underwriting (PDF p.715)
- **SME:** [ ] agree [ ] correct: ______

### G050 — O-FNM-54307 [O-FNM]
- **Q:** In a RefiNow transaction, were all existing loan eligibility documentation requirements met?
- **Defect condition:** The loan refinanced into a RefiNow was not a conventional mortgage loan owned or securitized by FNMA
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3663
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-1-01 — High-Balance Mortgage Loan Eligibility and Underwriting (PDF p.715)
- **Guide candidate:** B5-6-01 — HomeReady Mortgage Loan and Borrower Eligibility (PDF p.808)
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **SME:** [ ] agree [ ] correct: ______

### G051 — O-FNM-54308 [O-FNM]
- **Q:** In a RefiNow transaction, were all existing loan eligibility documentation requirements met?
- **Defect condition:** The loan refinanced into a RefiNow was not seasoned for at least 12 months
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3665
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '12 months'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.5-02 — Loan Eligibility (PDF p.225)
- **Guide candidate:** B4-2.3-04 — Loan Eligibility for Co-op Share Loans (PDF p.712)
- **Guide candidate:** B5-1-01 — High-Balance Mortgage Loan Eligibility and Underwriting (PDF p.715)
- **SME:** [ ] agree [ ] correct: ______

### G052 — O-FNM-54309 [O-FNM]
- **Q:** In a RefiNow transaction, were all existing loan eligibility documentation requirements met?
- **Defect condition:** The loan refinanced into a RefiNow was subject to recourse, repurchase, indem or credit enhancement
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3666
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.5-02 — Loan Eligibility (PDF p.225)
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **Guide candidate:** B3-5.1-02 — Determining the Credit Score for a Mortgage Loan (PDF p.474)
- **SME:** [ ] agree [ ] correct: ______

### G054 — O-FNM-54331 [O-FNM]
- **Q:** In a RefiNow transaction, were all income documentation requirements met?
- **Defect condition:** In a RefiNow using military income, the military leave and earnings statement not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3677
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.3-05 — Military Income (PDF p.342)
- **Guide candidate:** B3-3.3-09 — Temporary Leave Income (PDF p.347)
- **SME:** [ ] agree [ ] correct: ______

### G055 — O-FNM-54335 [O-FNM]
- **Q:** In a RefiNow transaction, were all income documentation requirements met?
- **Defect condition:** RefiNow alimony/child support debt pymts & amount not documented with a divorce decree or equivalent
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3653
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B3-3.4-02 — Alimony, Child Support, Equalization Payments, or Separate Maintenance (PDF p.352)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-6-02 — Debt-to-Income Ratios (PDF p.514)
- **SME:** [ ] agree [ ] correct: ______

### G056 — O-FNM-54334 [O-FNM]
- **Q:** In a RefiNow transaction, were all income documentation requirements met?
- **Defect condition:** RefiNow file did not contain 1 recent statement showing asset balance verifying funds to close
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3656
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-4.3-15 — Borrowed Funds Secured by an Asset (PDF p.458)
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **SME:** [ ] agree [ ] correct: ______

### G057 — O-FNM-54333 [O-FNM]
- **Q:** In a RefiNow transaction, were all income documentation requirements met?
- **Defect condition:** RefiNow using alimony/child support/maintenance & divorce decree or equiv & 1 mo receipt missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3652
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B3-3.4-02 — Alimony, Child Support, Equalization Payments, or Separate Maintenance (PDF p.352)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **SME:** [ ] agree [ ] correct: ______

### G058 — O-FNM-54329 [O-FNM]
- **Q:** In a RefiNow transaction, were all income documentation requirements met?
- **Defect condition:** RefiNow using base pay only, YTD paystub not provided or date over 30 days prior to application date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3657
- **Severity:** Critical
- **Classification method:** hand_verified
- **Data needed:** a distinct '30-days-old-or-newer' recency fact on paystub (deepen extraction)
- **Rationale:** amq_compiler.py's own eval_class says doc_presence (target: paystub) — but the actual condition is 'not provided OR dated over 30 days prior to application', a compound test. A bare paystub-doc-presence check would FALSE-PASS a loan with a paystub on file that is stale by more than 30 days. Downgraded from the mechanical GREEN: presence alone is not the real test.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.3-01 — Base Income (PDF p.333)
- **Guide candidate:** A1-1-01 — Application and Approval of Seller/Servicer (PDF p.20)
- **SME:** [ ] agree [ ] correct: ______

### G059 — O-FNM-54330 [O-FNM]
- **Q:** In a RefiNow transaction, were all income documentation requirements met?
- **Defect condition:** RefiNow using base pay plus variable income, most recent paystub & last year W2 not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3658
- **Severity:** Critical
- **Classification method:** hand_verified
- **Data needed:** a W2 doc type (not in extract_loan.py's DOC_TYPES at all) + a 'covers the most recent one-year period' recency fact
- **Rationale:** Same false-positive pattern as G058: eval_class=doc_presence targets paystub, but the condition requires BOTH a paystub AND a W2 covering a specific period — the mechanical check only verifies the paystub half, and W2 isn't even a document type this pilot extracts.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.3-01 — Base Income (PDF p.333)
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **SME:** [ ] agree [ ] correct: ______

### G060 — O-FNM-54332 [O-FNM]
- **Q:** In a RefiNow transaction, were all income documentation requirements met?
- **Defect condition:** RefiNow using self-employment, missing 1 yr personal/business tax returns & terms to waive not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3683
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'se_income_index' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'se_income_index', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.1-02 — Tax Return and Transcript Documentation Requirements (PDF p.320)
- **SME:** [ ] agree [ ] correct: ______

### G062 — O-FNM-54323 [O-FNM]
- **Q:** In a RefiNow transaction, were all occupancy and property type documentation requirements met?
- **Defect condition:** RefiNow loan project is a condo or co-op hotel, houseboat, timeshare or segmented ownership project
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3670
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** A2-4.1-02 — Ownership and Retention of Loan Files and Records (PDF p.83)
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **Guide candidate:** B5-7-02 — High LTV Reﬁnance Underwriting, Documentation, and Collateral Requirements for the New Loan (PDF p.824)
- **SME:** [ ] agree [ ] correct: ______

### G063 — O-FNM-54322 [O-FNM]
- **Q:** In a RefiNow transaction, were all occupancy and property type documentation requirements met?
- **Defect condition:** The RefiNow loan is not secured by a one-unit principal residence
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3684
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B7-3-02 — Property Insurance Requirements for One-to Four-Unit Properties (PDF p.875)
- **Guide candidate:** B5-7-02 — High LTV Reﬁnance Underwriting, Documentation, and Collateral Requirements for the New Loan (PDF p.824)
- **Guide candidate:** B7-3-04 — Individual Property Insurance Requirements for a Unit in a Project Development (PDF p.885)
- **SME:** [ ] agree [ ] correct: ______

### G065 — O-FNM-54336 [O-FNM]
- **Q:** In a RefiNow transaction, were all property valuation documentation requirements met?
- **Defect condition:** An appraisal was obtained in a RefiNow without evidence the $500 credit was passed to the borrower
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3655
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '$500'
- **Data needed:** a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'appraisal', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B3-5.4-03 — Documentation and Assessment of a Nontraditional Credit History (PDF p.509)
- **Guide candidate:** B4-1.4-07 — Mixed-Use Property Appraisal Requirements (PDF p.626)
- **Guide candidate:** B7-3-07 — Evidence of Property Insurance (PDF p.897)
- **SME:** [ ] agree [ ] correct: ______

### G067 — O-FNM-54316 [O-FNM]
- **Q:** In a RefiNow transaction, were all subject loan eligibility documentation requirements met?
- **Defect condition:** Borrowers added/removed on RefiNow loan from the original loan without meeting applicable exceptions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3660
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **Guide candidate:** B2-1.5-02 — Loan Eligibility (PDF p.225)
- **Guide candidate:** B4-2.3-04 — Loan Eligibility for Co-op Share Loans (PDF p.712)
- **SME:** [ ] agree [ ] correct: ______

### G068 — O-FNM-54313 [O-FNM]
- **Q:** In a RefiNow transaction, were all subject loan eligibility documentation requirements met?
- **Defect condition:** RefiNow cash out exceeded $250 and/or any excess not applied as a curtailment as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3675
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '$250'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **Guide candidate:** B2-1.3-03 — Cash-Out Reﬁnance Transactions (PDF p.197)
- **Guide candidate:** B2-1.5-02 — Loan Eligibility (PDF p.225)
- **SME:** [ ] agree [ ] correct: ______

### G069 — O-FNM-54676 [O-FNM]
- **Q:** In a RefiNow transaction, were all subject loan eligibility documentation requirements met?
- **Defect condition:** Subject loan closed as a RefiNow where the RefiNow option was previously used in a prior transaction
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3680
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.5-02 — Loan Eligibility (PDF p.225)
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **Guide candidate:** B4-2.3-04 — Loan Eligibility for Co-op Share Loans (PDF p.712)
- **SME:** [ ] agree [ ] correct: ______

### G070 — O-FNM-54317 [O-FNM]
- **Q:** In a RefiNow transaction, were all subject loan eligibility documentation requirements met?
- **Defect condition:** The RefiNow loan is ineligible as a Texas Section 50(a)(6) loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3673
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-4.1-02 — Texas Section 50(a)(6) Loan Eligibility (PDF p.771)
- **Guide candidate:** B5-4.1-03 — Texas Section 50(a)(6) Loan Underwriting, Collateral, and Closing Considerations (PDF p.773)
- **Guide candidate:** B5-4.1-04 — Texas Section 50(a)(6) Loan Delivery and Servicing Considerations (PDF p.775)
- **SME:** [ ] agree [ ] correct: ______

### G071 — O-FNM-54318 [O-FNM]
- **Q:** In a RefiNow transaction, were all subject loan eligibility documentation requirements met?
- **Defect condition:** The RefiNow loan is ineligible being subject to a temporary interest rate buydown
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3672
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.4-04 — Temporary Interest Rate Buydowns (PDF p.219)
- **Guide candidate:** B2-1.5-02 — Loan Eligibility (PDF p.225)
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **SME:** [ ] agree [ ] correct: ______

### G072 — O-FNM-54311 [O-FNM]
- **Q:** In a RefiNow transaction, were all subject loan eligibility documentation requirements met?
- **Defect condition:** The RefiNow loan is not a fixed rate and/or did not meet maximum LTV, CLTV, and HCLTV ratios
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3681
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.2-01 — Loan-to-Value (LTV) Ratios (PDF p.179)
- **Guide candidate:** B2-1.2-02 — Combined Loan-to-Value (CLTV) Ratios (PDF p.181)
- **Guide candidate:** B2-1.2-03 — Home Equity Combined Loan-to-Value (HCLTV) Ratios (PDF p.182)
- **SME:** [ ] agree [ ] correct: ______

### G073 — O-FNM-54315 [O-FNM]
- **Q:** In a RefiNow transaction, were all subject loan eligibility documentation requirements met?
- **Defect condition:** The RefiNow loan is not a limited cash-out refinance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3662
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **Guide candidate:** B5-4.2-02 — Disaster-Related Limited Cash-Out Reﬁnance Flexibilities (PDF p.778)
- **Guide candidate:** B2-1.3-03 — Cash-Out Reﬁnance Transactions (PDF p.197)
- **SME:** [ ] agree [ ] correct: ______

### G074 — O-FNM-54314 [O-FNM]
- **Q:** In a RefiNow transaction, were all subject loan eligibility documentation requirements met?
- **Defect condition:** The RefiNow loan limit does not conform to the general loan limits
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3674
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.5-01 — Loan Limits (PDF p.224)
- **Guide candidate:** B2-1.5-02 — Loan Eligibility (PDF p.225)
- **Guide candidate:** B2-2-01 — General Borrower Eligibility Requirements (PDF p.241)
- **SME:** [ ] agree [ ] correct: ______

### G075 — O-FNM-54319 [O-FNM]
- **Q:** In a RefiNow transaction, were all subject loan eligibility documentation requirements met?
- **Defect condition:** The RefiNow loan was combined with a HomeReady refinance transaction
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3669
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-6-01 — HomeReady Mortgage Loan and Borrower Eligibility (PDF p.808)
- **Guide candidate:** B2-1.2-02 — Combined Loan-to-Value (CLTV) Ratios (PDF p.181)
- **Guide candidate:** B2-1.2-03 — Home Equity Combined Loan-to-Value (HCLTV) Ratios (PDF p.182)
- **SME:** [ ] agree [ ] correct: ______

### G077 — O-FNM-54672 [O-FNM]
- **Q:** In a RefiNow transaction, were all subordinate financing requirements met?
- **Defect condition:** New subordinate P&I increased from the existing subordinated loan in a RefiNow simultaneous refi
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3685
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.2-04 — Subordinate Financing (PDF p.184)
- **Guide candidate:** B5-7-02 — High LTV Reﬁnance Underwriting, Documentation, and Collateral Requirements for the New Loan (PDF p.824)
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **SME:** [ ] agree [ ] correct: ______

### G078 — O-FNM-54673 [O-FNM]
- **Q:** In a RefiNow transaction, were all subordinate financing requirements met?
- **Defect condition:** New subordinate financing permitted in a RefiNow that did not have existing subordinate financing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3671
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.2-04 — Subordinate Financing (PDF p.184)
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **SME:** [ ] agree [ ] correct: ______

### G079 — O-FNM-54671 [O-FNM]
- **Q:** In a RefiNow transaction, were all subordinate financing requirements met?
- **Defect condition:** New subordinate lien UPB is higher than original subordinate lien UPB in RefiNow simultaneous refi
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3686
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'payoff_statement' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'payoff_statement', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.2-04 — Subordinate Financing (PDF p.184)
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **SME:** [ ] agree [ ] correct: ______

### G080 — O-FNM-54321 [O-FNM]
- **Q:** In a RefiNow transaction, were all subordinate financing requirements met?
- **Defect condition:** RefiNow has existing subordinate loan satisfied using loan proceeds &/or was not subordinated
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3667
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.2-04 — Subordinate Financing (PDF p.184)
- **Guide candidate:** C2-2-04 — Timing of Distribution of Whole Loan Purchase Proceeds (PDF p.986)
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **SME:** [ ] agree [ ] correct: ______

### G082 — O-FNM-54324 [O-FNM]
- **Q:** In a RefiNow transaction, were all underwriting requirements met?
- **Defect condition:** A RefiNow was manually underwritten without LTV, DTI ratio and credit score requirements being met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3676
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B3-5.1-02 — Determining the Credit Score for a Mortgage Loan (PDF p.474)
- **Guide candidate:** B5-7-02 — High LTV Reﬁnance Underwriting, Documentation, and Collateral Requirements for the New Loan (PDF p.824)
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **SME:** [ ] agree [ ] correct: ______

### G083 — O-FNM-54675 [O-FNM]
- **Q:** In a RefiNow transaction, were all underwriting requirements met?
- **Defect condition:** No FNMA approval for the variance or exception impactful to underwriting/eligibility in a RefiNow
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3687
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** A2-3.2-02 — Enforcement Relief for Breaches of Certain Representations and Warranties Related to Underwriting and Eligibility (PDF p.65)
- **Guide candidate:** B2-3-02 — Special Property Eligibility and Underwriting Considerations: Factory-Built Housing (PDF p.261)
- **Guide candidate:** B2-3-03 — Special Property Eligibility and Underwriting Considerations: Leasehold Estates (PDF p.268)
- **SME:** [ ] agree [ ] correct: ______

### G084 — O-FNM-54326 [O-FNM]
- **Q:** In a RefiNow transaction, were all underwriting requirements met?
- **Defect condition:** RefiNow original loan had a 30-day late in the last 6 mos &/or more than one 30-day late in mos 7-12
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3679
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '30-day'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-1-01 — High-Balance Mortgage Loan Eligibility and Underwriting (PDF p.715)
- **Guide candidate:** B5-4.1-03 — Texas Section 50(a)(6) Loan Underwriting, Collateral, and Closing Considerations (PDF p.773)
- **Guide candidate:** B5-7-02 — High LTV Reﬁnance Underwriting, Documentation, and Collateral Requirements for the New Loan (PDF p.824)
- **SME:** [ ] agree [ ] correct: ______

### G085 — O-FNM-54328 [O-FNM]
- **Q:** In a RefiNow transaction, were all underwriting requirements met?
- **Defect condition:** RefiNow with a non-occupant borrower did not meet the maximum LTV, CLTV, and HCLTV ratio of 95%
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3678
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '95%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **Guide candidate:** B5-7-01 — High LTV Reﬁnance Loan and Borrower Eligibility (PDF p.819)
- **SME:** [ ] agree [ ] correct: ______

### G086 — O-FNM-54674 [O-FNM]
- **Q:** In a RefiNow transaction, were all underwriting requirements met?
- **Defect condition:** Resolved COVID-19 forbearance missed payments considered delinquencies in RefiNow pay history req's
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3682
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'vom' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'vom', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** A2-3.2-02 — Enforcement Relief for Breaches of Certain Representations and Warranties Related to Underwriting and Eligibility (PDF p.65)
- **SME:** [ ] agree [ ] correct: ______

### G087 — O-FNM-54327 [O-FNM]
- **Q:** In a RefiNow transaction, were all underwriting requirements met?
- **Defect condition:** The RefiNow DTI ratio exceeds 65%
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3661
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '65%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **Guide candidate:** A2-3.2-02 — Enforcement Relief for Breaches of Certain Representations and Warranties Related to Underwriting and Eligibility (PDF p.65)
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **SME:** [ ] agree [ ] correct: ______

### G089 — O-FHA-00599 [O-FHA]
- **Q:** In a Section 251 Adjustable Rate Mortgage (ARM) transaction, were all requirements met?
- **Defect condition:** 1 yr ARM with LTV of 95% or more, does not qualify with initial interest rate plus 1% point
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3269
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '95%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G090 — O-FHA-51054 [O-FHA]
- **Q:** In a Section 251 Adjustable Rate Mortgage (ARM) transaction, were all requirements met?
- **Defect condition:** Incorrect initial interest rate/margin per ARM type &/or initial interest rate adjustment incorrect
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3297
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G092 — O-FNM-00729 [O-FNM]
- **Q:** In a cash-out refinance transaction, were all eligibility requirements  met?
- **Defect condition:** Cash-out loan proceeds allowed to be used for purposes not allowed as per FNMA requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3530
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **Guide candidate:** B2-1.3-03 — Cash-Out Reﬁnance Transactions (PDF p.197)
- **Guide candidate:** B2-1.5-02 — Loan Eligibility (PDF p.225)
- **SME:** [ ] agree [ ] correct: ______

### G093 — O-FNM-55649 [O-FNM]
- **Q:** In a cash-out refinance transaction, were all eligibility requirements  met?
- **Defect condition:** Cash-out refinance with delayed financing did not document the source of funds for the purchase
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3421
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **Guide candidate:** B2-1.3-03 — Cash-Out Reﬁnance Transactions (PDF p.197)
- **Guide candidate:** B5-4.2-02 — Disaster-Related Limited Cash-Out Reﬁnance Flexibilities (PDF p.778)
- **SME:** [ ] agree [ ] correct: ______

### G094 — O-FNM-55648 [O-FNM]
- **Q:** In a cash-out refinance transaction, were all eligibility requirements  met?
- **Defect condition:** Delayed financing cashout refi did not confirm a mtg not used to obtain the subject & no liens exist
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3419
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **Guide candidate:** B2-1.3-03 — Cash-Out Reﬁnance Transactions (PDF p.197)
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **SME:** [ ] agree [ ] correct: ______

### G095 — O-FNM-56146 [O-FNM]
- **Q:** In a cash-out refinance transaction, were all eligibility requirements  met?
- **Defect condition:** First mtg PIF by subject CO refi not at least 12 mos old from prior note date to subject note date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3308
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '12 months'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **Guide candidate:** B2-1.3-03 — Cash-Out Reﬁnance Transactions (PDF p.197)
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **SME:** [ ] agree [ ] correct: ______

### G096 — O-FNM-52249 [O-FNM]
- **Q:** In a cash-out refinance transaction, were all eligibility requirements  met?
- **Defect condition:** In a cash-out refi, no evidence the listed property was taken off the market prior to disbursement
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3310
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **Guide candidate:** B2-1.3-03 — Cash-Out Reﬁnance Transactions (PDF p.197)
- **Guide candidate:** B2-3-01 — General Property Eligibility (PDF p.258)
- **SME:** [ ] agree [ ] correct: ______

### G097 — O-FNM-55650 [O-FNM]
- **Q:** In a cash-out refinance transaction, were all eligibility requirements  met?
- **Defect condition:** Loan amt more than borr's initial purchase plus all costs to close in a CO refi w/ delayed financing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3420
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **Guide candidate:** B2-1.3-03 — Cash-Out Reﬁnance Transactions (PDF p.197)
- **Guide candidate:** B2-1.5-02 — Loan Eligibility (PDF p.225)
- **SME:** [ ] agree [ ] correct: ______

### G098 — O-FNM-52250 [O-FNM]
- **Q:** In a cash-out refinance transaction, were all eligibility requirements  met?
- **Defect condition:** No borrower on title for at least 6 mos prior to disbursement & did not meet ownership exceptions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3313
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '6 months'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **Guide candidate:** B2-1.3-03 — Cash-Out Reﬁnance Transactions (PDF p.197)
- **Guide candidate:** B2-2-01 — General Borrower Eligibility Requirements (PDF p.241)
- **SME:** [ ] agree [ ] correct: ______

### G099 — O-FNM-52251 [O-FNM]
- **Q:** In a cash-out refinance transaction, were all eligibility requirements  met?
- **Defect condition:** Proceeds from the cash-out refinance were used to pay off an installment land contract
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3312
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.3-05 — Payoﬀ of Installment Land Contract Requirements (PDF p.205)
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **Guide candidate:** B2-1.3-03 — Cash-Out Reﬁnance Transactions (PDF p.197)
- **SME:** [ ] agree [ ] correct: ______

### G102 — O-FHA-50024 [O-FHA]
- **Q:** In a cash-out refinance transaction, were all eligibility requirements met?
- **Defect condition:** CO Refi not downgraded to Refer & a mortgage debt has delinquency w/in 12 mos of case# assignment
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3315
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '12 months'
- **Data needed:** a field/fact on the existing 'fhac_case_assignment' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'fhac_case_assignment', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G103 — O-FHA-50724 [O-FHA]
- **Q:** In a cash-out refinance transaction, were all eligibility requirements met?
- **Defect condition:** Product specific pay history req's not met based on the type of refinance and length of time owned
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3314
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'vom' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'vom', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G104 — O-FHA-56216 [O-FHA]
- **Q:** In a cash-out refinance transaction, were all eligibility requirements met?
- **Defect condition:** Subject not owned & occupied by at least 1 borr for the last 12 mos prior to case# assignment date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3311
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '12 months'
- **Data needed:** a field/fact on the existing 'fhac_case_assignment' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'fhac_case_assignment', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G106 — O-FNM-00728 [O-FNM]
- **Q:** In a limited cash-out refinance transaction, were all eligibility requirements  met?
- **Defect condition:** Equity buy out from ex-spouse or other co-borrower without adequate documentation of the equity
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3605
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** equity-buyout supporting-document presence
- **Data needed:** a legally-enforceable-agreement doc type for an ex-spouse/co-owner equity buyout (not in corpus)
- **Rationale:** 'Adequate documentation' names a real, specific document family (the buyout agreement) even though it isn't in the corpus today.
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **Guide candidate:** B5-4.2-02 — Disaster-Related Limited Cash-Out Reﬁnance Flexibilities (PDF p.778)
- **Guide candidate:** B2-1.3-03 — Cash-Out Reﬁnance Transactions (PDF p.197)
- **SME:** [ ] agree [ ] correct: ______

### G107 — O-FNM-50209 [O-FNM]
- **Q:** In a limited cash-out refinance transaction, were all eligibility requirements  met?
- **Defect condition:** Ineligible for LCO as there is not an outstanding lien and not a con-perm
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3555
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **Guide candidate:** B5-4.2-02 — Disaster-Related Limited Cash-Out Reﬁnance Flexibilities (PDF p.778)
- **Guide candidate:** B2-1.3-03 — Cash-Out Reﬁnance Transactions (PDF p.197)
- **SME:** [ ] agree [ ] correct: ______

### G108 — O-FNM-50210 [O-FNM]
- **Q:** In a limited cash-out refinance transaction, were all eligibility requirements  met?
- **Defect condition:** LCO inelig due to short term/consolidated refi to a new 1st mtg < 6 months
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3558
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '6 months'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **Guide candidate:** B5-4.2-02 — Disaster-Related Limited Cash-Out Reﬁnance Flexibilities (PDF p.778)
- **Guide candidate:** B2-1.3-03 — Cash-Out Reﬁnance Transactions (PDF p.197)
- **SME:** [ ] agree [ ] correct: ______

### G109 — O-FNM-50207 [O-FNM]
- **Q:** In a limited cash-out refinance transaction, were all eligibility requirements  met?
- **Defect condition:** LCO refi - All requirements not met for LTV over 95%
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3557
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** LTV > 95% gate (LTV already derivable from appraisal/1003 fields)
- **Stays human:** the specific bundle of 'additional requirements' beyond the LTV gate (unstated in-row)
- **Data needed:** LCO-refi-over-95%-LTV requirement checklist (an SME-defined list)
- **Rationale:** Has an explicit numeric threshold (95% LTV) as a bright-line gate; what else is specifically required beyond that isn't named in-row.
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **Guide candidate:** B5-4.2-02 — Disaster-Related Limited Cash-Out Reﬁnance Flexibilities (PDF p.778)
- **Guide candidate:** B2-1.3-03 — Cash-Out Reﬁnance Transactions (PDF p.197)
- **SME:** [ ] agree [ ] correct: ______

### G110 — O-FNM-50208 [O-FNM]
- **Q:** In a limited cash-out refinance transaction, were all eligibility requirements  met?
- **Defect condition:** Manual UW LCO financed payment of the subject's taxes over 60 days in arrears
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3556
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '60 days'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **Guide candidate:** B5-4.2-02 — Disaster-Related Limited Cash-Out Reﬁnance Flexibilities (PDF p.778)
- **Guide candidate:** B2-1.3-03 — Cash-Out Reﬁnance Transactions (PDF p.197)
- **SME:** [ ] agree [ ] correct: ______

### G111 — O-FNM-56598 [O-FNM]
- **Q:** In a limited cash-out refinance transaction, were all eligibility requirements  met?
- **Defect condition:** No borrower on the LCO was a current owner at the time of the initial app & does not meet exceptions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3563
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '12 months'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **Guide candidate:** B5-4.2-02 — Disaster-Related Limited Cash-Out Reﬁnance Flexibilities (PDF p.778)
- **Guide candidate:** B2-1.3-03 — Cash-Out Reﬁnance Transactions (PDF p.197)
- **SME:** [ ] agree [ ] correct: ______

### G112 — O-FNM-50206 [O-FNM]
- **Q:** In a limited cash-out refinance transaction, were all eligibility requirements  met?
- **Defect condition:** Subject listed for sale w/out evidence it was off the market on/before disbursement of the new loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3559
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **Guide candidate:** B5-4.2-02 — Disaster-Related Limited Cash-Out Reﬁnance Flexibilities (PDF p.778)
- **Guide candidate:** B2-1.3-03 — Cash-Out Reﬁnance Transactions (PDF p.197)
- **SME:** [ ] agree [ ] correct: ______

### G113 — O-FNM-50211 [O-FNM]
- **Q:** In a limited cash-out refinance transaction, were all eligibility requirements  met?
- **Defect condition:** The borrower received loan proceeds exceeding 2% of the subject loan amount or $2,000 in a LCO refi
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3554
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** cash-back-to-borrower vs 2%-of-loan-amount-or-$2,000 threshold
- **Data needed:** an LCO-refi cash-back-to-borrower field (distinct from the refi-specific cash_out_to_borrower_1003, which is populated only for actual cash-out refis, not LCO)
- **Rationale:** Fully crisp numeric threshold with an explicit comparison basis — 'unacceptable' is just naming the outcome, not the test.
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **Guide candidate:** B5-3.2-02 — HomeStyle Renovation Mortgages: Loan and Borrower Eligibility (PDF p.747)
- **Guide candidate:** B5-4.2-02 — Disaster-Related Limited Cash-Out Reﬁnance Flexibilities (PDF p.778)
- **SME:** [ ] agree [ ] correct: ______

### G115 — O-FNM-50205 [O-FNM]
- **Q:** In a limited cash-out refinance transaction, were all eligibility requirements  met?
- **Defect condition:** The subordinate lien paid in LCO refi was not obtained to buy the property
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3560
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **Guide candidate:** B5-4.2-02 — Disaster-Related Limited Cash-Out Reﬁnance Flexibilities (PDF p.778)
- **Guide candidate:** B2-1.3-03 — Cash-Out Reﬁnance Transactions (PDF p.197)
- **SME:** [ ] agree [ ] correct: ______

### G117 — O-FHA-00624 [O-FHA]
- **Q:** In a no cash-out refinance transaction, were all eligibility requirements met?
- **Defect condition:** Acceptable credit history and ability to repay is not documented on credit qualifying streamline
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3406
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** borrower-carryover check: at least 1 original-loan borrower remains on the new mortgage (needs old-loan borrower data)
- **Stays human:** 'acceptable credit history and ability to repay' (unstated criteria)
- **Data needed:** prior-loan borrower-identity data (not currently modeled — this pilot extracts only the CURRENT loan's borrowers)
- **Rationale:** Compound: the borrower-carryover half names a specific, checkable fact; the credit-history-acceptability half is open-ended and stays human.
- **SME:** [ ] agree [ ] correct: ______

### G118 — O-FHA-00617 [O-FHA]
- **Q:** In a no cash-out refinance transaction, were all eligibility requirements met?
- **Defect condition:** Equity buy out from ex-spouse or other co-borrower without adequate documentation of the equity
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3839
- **Severity:** Major
- **Classification method:** hand_verified
- **Machine checks:** equity-buyout supporting-document presence (FHA variant)
- **Data needed:** a legally-enforceable equity agreement doc (not in corpus)
- **Rationale:** Same family as G106 — FHA no-cash-out variant.
- **SME:** [ ] agree [ ] correct: ______

### G119 — O-FHA-50728 [O-FHA]
- **Q:** In a no cash-out refinance transaction, were all eligibility requirements met?
- **Defect condition:** Funds to close exceeded new streamline refi mtg pymt & were not verified
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3824
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G120 — O-FHA-50727 [O-FHA]
- **Q:** In a no cash-out refinance transaction, were all eligibility requirements met?
- **Defect condition:** No credit report or all available credit scores not put in FHA Connection for credit qual STR Refi
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3405
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'credit_report' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'credit_report', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G121 — O-FHA-50729 [O-FHA]
- **Q:** In a no cash-out refinance transaction, were all eligibility requirements met?
- **Defect condition:** STR refi amortization period > than remaining amortization period of existing Mtg +12 yrs or 30 yrs
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3825
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '12 years'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G122 — O-FHA-00618 [O-FHA]
- **Q:** In a no cash-out refinance transaction, were all eligibility requirements met?
- **Defect condition:** Streamline refi transaction includes cash back in excess of minor adjustments exceeding $500
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3433
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '$500'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G123 — O-FHA-00621 [O-FHA]
- **Q:** In a no cash-out refinance transaction, were all eligibility requirements met?
- **Defect condition:** Streamline refi w/out appraisal & new mtg exceeds lower of orig principal balance or existing debt
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3822
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'appraisal', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G124 — O-FHA-00620 [O-FHA]
- **Q:** In a no cash-out refinance transaction, were all eligibility requirements met?
- **Defect condition:** Streamline refinance - borrower did not receive a net tangible benefit
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3823
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G125 — O-FHA-00619 [O-FHA]
- **Q:** In a no cash-out refinance transaction, were all eligibility requirements met?
- **Defect condition:** Streamline refinance - seasoning and payment history requirements not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3827
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'vom' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'vom', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G126 — O-FHA-51754 [O-FHA]
- **Q:** In a no cash-out refinance transaction, were all eligibility requirements met?
- **Defect condition:** The subject streamline refinance PITI exceeds the original PITI by more than $50
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3357
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '$50'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G127 — O-FHA-50726 [O-FHA]
- **Q:** In a no cash-out refinance transaction, were all eligibility requirements met?
- **Defect condition:** The subject streamline refinance was not manually underwritten
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3826
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G129 — O-FNM-50202 [O-FNM]
- **Q:** In a purchase transaction, were all eligibility requirements  met?
- **Defect condition:** All additional requirements not met based on LTV and/or loan type
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3275
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '95%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-7-01 — High LTV Reﬁnance Loan and Borrower Eligibility (PDF p.819)
- **Guide candidate:** B2-1.2-01 — Loan-to-Value (LTV) Ratios (PDF p.179)
- **Guide candidate:** B2-1.5-02 — Loan Eligibility (PDF p.225)
- **SME:** [ ] agree [ ] correct: ______

### G130 — O-FNM-50204 [O-FNM]
- **Q:** In a purchase transaction, were all eligibility requirements  met?
- **Defect condition:** Evidence all parties agreed to the terms of the short sale/pre-foreclosure
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3765, 3766
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** C3-7-07 — Sale of Fannie Mae Securities to Third Parties (PDF p.1049)
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **Guide candidate:** A2-3.2-02 — Enforcement Relief for Breaches of Certain Representations and Warranties Related to Underwriting and Eligibility (PDF p.65)
- **SME:** [ ] agree [ ] correct: ______

### G133 — O-FNM-54035 [O-FNM]
- **Q:** In a purchase transaction, were all eligibility requirements  met?
- **Defect condition:** Seller tax credit included in funds to close that does not meet exception to offset the escrow acct
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3633
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** seller-tax-credit vs escrow-account-offset-exception math
- **Data needed:** real-estate-tax-credit amount + escrow-account-requirement fields (not in corpus)
- **Rationale:** Names a specific, structured exception test (tax credit vs escrow shortage) — crisp once fields exist, not an open-ended judgment.
- **Guide candidate:** A4-1-01 — Maintaining Seller/Servicer Eligibility (PDF p.151)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-5.4-01 — Eligibility Requirements for Loans with Nontraditional Credit (PDF p.504)
- **SME:** [ ] agree [ ] correct: ______

### G134 — O-FNM-00725 [O-FNM]
- **Q:** In a purchase transaction, were all eligibility requirements  met?
- **Defect condition:** Sufficient funds to meet minimum contribution from acceptable source not documented and/or verified
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3576
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** minimum-borrower-contribution threshold + fund-source acceptability
- **Data needed:** minimum-contribution + fund-source fields (deepen 1003/closing_disclosure) — same family as asset-verification's G099
- **Rationale:** Comparison basis (a minimum-contribution percentage the mortgage type defines) is real and crisp; source-acceptability is a bounded, enumerable list, not free-form judgment.
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **Guide candidate:** A2-3.2-02 — Enforcement Relief for Breaches of Certain Representations and Warranties Related to Underwriting and Eligibility (PDF p.65)
- **Guide candidate:** A4-1-01 — Maintaining Seller/Servicer Eligibility (PDF p.151)
- **SME:** [ ] agree [ ] correct: ______

### G135 — O-FNM-00829 [O-FNM]
- **Q:** In a purchase transaction, were all eligibility requirements  met?
- **Defect condition:** The borrower(s) received cash back in an amount exceeding purchase money transaction guidelines
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3639
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-2-01 — General Borrower Eligibility Requirements (PDF p.241)
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **Guide candidate:** B5-3.2-02 — HomeStyle Renovation Mortgages: Loan and Borrower Eligibility (PDF p.747)
- **SME:** [ ] agree [ ] correct: ______

### G136 — UW-Documentation3 [O-FNM]
- **Q:** In a purchase transaction, were all eligibility requirements  met?
- **Defect condition:** The purchase agreement indicates personal property and/or repairs are included in the purchase price
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3855
- **Severity:** Major
- **Classification method:** hand_verified
- **Machine checks:** purchase-agreement clause detection (personal property/repairs bundled into price)
- **Data needed:** a purchase agreement/contract doc type — NOT in this pilot's corpus at all (same systemic gap flagged in decision 017's asset triage: no purchase contract exists in any of loan 01-05)
- **Rationale:** Crisp content check once the document exists; blocked entirely on the missing purchase-contract document family.
- **Guide candidate:** B2-3-01 — General Property Eligibility (PDF p.258)
- **Guide candidate:** B2-3-02 — Special Property Eligibility and Underwriting Considerations: Factory-Built Housing (PDF p.261)
- **Guide candidate:** B2-3-03 — Special Property Eligibility and Underwriting Considerations: Leasehold Estates (PDF p.268)
- **SME:** [ ] agree [ ] correct: ______

### G137 — O-FNM-55679 [O-FNM]
- **Q:** In a purchase transaction, were all eligibility requirements  met?
- **Defect condition:** The purchase price &/or any earnest money deposit was designated in virtual currency
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3635
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B3-4.3-09 — Earnest Money Deposit (PDF p.452)
- **Guide candidate:** B3-4.1-04 — Virtual Currency (PDF p.429)
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **SME:** [ ] agree [ ] correct: ______

### G138 — O-FNM-57531 [O-FNM]
- **Q:** In a purchase transaction, were all payoff of installment land contracts requirements  met?
- **Defect condition:** LTV not calc by dividing the new loan amt by lesser of total acq cost or appraised value at closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3533
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.2-01 — Loan-to-Value (LTV) Ratios (PDF p.179)
- **Guide candidate:** B5-7-02 — High LTV Reﬁnance Underwriting, Documentation, and Collateral Requirements for the New Loan (PDF p.824)
- **Guide candidate:** B2-1.2-02 — Combined Loan-to-Value (CLTV) Ratios (PDF p.181)
- **SME:** [ ] agree [ ] correct: ______

### G140 — O-FNM-50214 [O-FNM]
- **Q:** In a purchase transaction, were all payoff of installment land contracts requirements  met?
- **Defect condition:** Subject not UW as a LCO when p/o of land contract was executed more than 12 mos before application
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3551
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '12 months'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.3-05 — Payoﬀ of Installment Land Contract Requirements (PDF p.205)
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **Guide candidate:** B4-1.3-02 — Subject and Contract Sections of the Appraisal Report (PDF p.570)
- **SME:** [ ] agree [ ] correct: ______

### G141 — O-FNM-50213 [O-FNM]
- **Q:** In a purchase transaction, were all payoff of installment land contracts requirements  met?
- **Defect condition:** Subject not UW as a purchase when p/o of land contract was executed within 12 mos before application
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3552
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '12 months'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.3-05 — Payoﬀ of Installment Land Contract Requirements (PDF p.205)
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **Guide candidate:** B4-1.3-02 — Subject and Contract Sections of the Appraisal Report (PDF p.570)
- **SME:** [ ] agree [ ] correct: ______

### G142 — O-FRD-50384 [O-FRD]
- **Q:** In a purchase transaction, were all payoff of installment land contracts requirements met?
- **Defect condition:** Land contract for deed considered a purchase did not meet all requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3550
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** 3 explicit sub-tests: land-contract execution date within 12 months, loan proceeds fully applied to the contract payoff, no cash disbursed to borrower
- **Data needed:** a land-contract-for-deed document type (not in corpus)
- **Rationale:** All three conjuncts are crisp, named, checkable facts once the document exists — no judgment language in the actual test.
- **SME:** [ ] agree [ ] correct: ______

### G144 — O-VA-00474 [O-VA]
- **Q:** In a purchase transaction, were all requirements met?
- **Defect condition:** File did not evidence the appraiser was provided a copy of the final sales contract & any amendments
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3745
- **Severity:** Major
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G145 — O-VA-50788 [O-VA]
- **Q:** In a purchase transaction, were all requirements met?
- **Defect condition:** Final sales contract and all addendums not in the file &/or is incorrect or unacceptable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3744
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** final-sales-contract-and-addendums presence (same missing-purchase-contract gap as G136)
- **Stays human:** 'is incorrect or unacceptable' (unstated criteria)
- **Data needed:** purchase/sales contract doc type (not in corpus)
- **Rationale:** Presence half is crisp and shares the systemic purchase-contract gap with G136/G486; the 'incorrect or unacceptable' residual stays human.
- **SME:** [ ] agree [ ] correct: ______

### G146 — O-VA-50789 [O-VA]
- **Q:** In a purchase transaction, were all requirements met?
- **Defect condition:** The FHA/VA Amendatory Clause unsigned, not in the file or included in the sales contract
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3440
- **Severity:** Major
- **Classification method:** hand_verified
- **Machine checks:** presence half: doc_present_fha_amendatory_clause (already extracted, FHA only)
- **Stays human:** signature status + 'included in sales contract' location test
- **Data needed:** shape needs widening to VA loans (fact is only computed when mismo_mortgage_type=='FHA' today; a VA loan never populates it) + a signature sub-check
- **Rationale:** CONSIDERED for AmendatoryClauseShape (CHK-PRD-001), REJECTED as-is: this row (O-VA-50789, filed under agency O-VA even though the text says 'FHA/VA Amendatory Clause') tests THREE things — unsigned, not in file, not in the sales contract — while the shape's SPARQL only checks doc_present_fha_amendatory_clause AND mismo_mortgage_type=='FHA'. Two real gaps, not merely imprecision: (1) EXPECTED_DOCS_BY_PROGRAM only computes this fact for FHA loans — a VA loan never gets the fact at all, so the shape would silently never fire for VA loans regardless of wiring; (2) the shape has no signature test. Wiring this code today would be a false 'ready to build' of exactly the kind decision 018 warns against — needs real shape/extraction work first, not just an amq_exception_codes list edit.
- **SME:** [ ] agree [ ] correct: ______

### G148 — O-FHA-50725 [O-FHA]
- **Q:** In a refinance transaction, were all eligibility requirements met?
- **Defect condition:** All max CLTV and mortgage amount limits not met based on the refinance program type
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3574
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G149 — O-FHA-50722 [O-FHA]
- **Q:** In a refinance transaction, were all eligibility requirements met?
- **Defect condition:** Amount of the refund credit to reduce the UFMIP was incorrect for FHA to FHA refi within 3 years
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3846
- **Severity:** Major
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '3 years'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G150 — O-FHA-00080 [O-FHA]
- **Q:** In a refinance transaction, were all eligibility requirements met?
- **Defect condition:** Refinance Authorization number was not obtained for FHA to FHA refinance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3645
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'fhac_case_assignment' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'fhac_case_assignment', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G151 — O-FHA-51753 [O-FHA]
- **Q:** In a refinance transaction, were all eligibility requirements met?
- **Defect condition:** Subject refi is replacing a mtg that has been condemned or seized by a state or municipality
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3649
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G153 — O-FRD-50385 [O-FRD]
- **Q:** In a refinance transaction, were all payoff of installment land contracts requirements met?
- **Defect condition:** Land contract for deed considered no cashout refi but contract dated >12mos
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3549
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '12 months'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G155 — O-FNM-55110 [O-FNM]
- **Q:** In a refinance transaction, were all prohibited practices requirements  met?
- **Defect condition:** A CO refi with a note date 30 days or less before the application date of the subject LCO refi
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3322
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '30 days'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.3-04 — Prohibited Reﬁnancing Practices (PDF p.203)
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **Guide candidate:** A1-1-01 — Application and Approval of Seller/Servicer (PDF p.20)
- **SME:** [ ] agree [ ] correct: ______

### G156 — O-FNM-55627 [O-FNM]
- **Q:** In a refinance transaction, were all prohibited practices requirements  met?
- **Defect condition:** Seller/servicer advanced pymts for the borr to then to refi after agreed pymts were advanced
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3278
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** payment-advance-then-refinance sequence detection
- **Data needed:** servicer payment-advance records + refinance timing (not in corpus)
- **Rationale:** Names a specific, checkable event sequence (advances, then refi) even though establishing 'agreed payments were advanced' as a defect still leans evidentiary.
- **Guide candidate:** A1-1-01 — Application and Approval of Seller/Servicer (PDF p.20)
- **Guide candidate:** A4-1-01 — Maintaining Seller/Servicer Eligibility (PDF p.151)
- **Guide candidate:** A4-1-03 — Report of Changes in the Seller/Servicer’s Organization (PDF p.162)
- **SME:** [ ] agree [ ] correct: ______

### G161 — O-FRD-00693 [O-FRD]
- **Q:** Were all Adjustable Rate (ARM) requirements met?
- **Defect condition:** ARM with a lifetime floor, it does not equal the margin stated in the note
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3565
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G162 — O-FRD-50380 [O-FRD]
- **Q:** Were all Adjustable Rate (ARM) requirements met?
- **Defect condition:** Qualifying rate used not appropriate for the ARM type
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3290
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** ARM-type-to-qualifying-rate rule lookup
- **Data needed:** ARM sub-type + note rate/margin fields (mismo_note_rate already extracted; the specific qualifying-rate-per-ARM-type rule table is not)
- **Rationale:** Comparison basis (a defined correct-rate-per-ARM-type rule) is real and crisp, same family as G194/G195/G164/G196.
- **SME:** [ ] agree [ ] correct: ______

### G163 — O-FRD-52326 [O-FRD]
- **Q:** Were all Adjustable Rate (ARM) requirements met?
- **Defect condition:** Section 4(D) of the ARM Note was incomplete or incorrect
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3529
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G164 — O-FRD-54597 [O-FRD]
- **Q:** Were all Adjustable Rate (ARM) requirements met?
- **Defect condition:** Short term ARM qualifying interest rate not calculated using the required method in ATR covered loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3769
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** short-term-ARM qualifying-rate recompute (FRD variant)
- **Data needed:** the required ATR-covered-ARM qualifying-rate method (an SME-supplied formula) + ARM-type/note-rate fields
- **Rationale:** Same family as G196 (FNM variant) and G194/G195 (explicit-formula variants) — 'required method' names a real, defined calculation.
- **SME:** [ ] agree [ ] correct: ______

### G165 — O-FRD-53028 [O-FRD]
- **Q:** Were all Adjustable Rate (ARM) requirements met?
- **Defect condition:** The Note and Riders did not contain the updated index “fallback” language in a non-SOFR ARM loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3285
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G166 — O-FRD-52327 [O-FRD]
- **Q:** Were all Adjustable Rate (ARM) requirements met?
- **Defect condition:** The lifetime floor was not equal to the margin stated in the Note in an ARM loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3288
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G167 — O-FRD-55095 [O-FRD]
- **Q:** Were all Adjustable Rate (ARM) requirements met?
- **Defect condition:** The subject ARM did not use the 30-day Average SOFR Index
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3852
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '30-day'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G168 — O-FRD-52791 [O-FRD]
- **Q:** Were all Adjustable Rate (ARM) requirements met?
- **Defect condition:** The updated 30 day Average SOFR-index ARM Note and Rider was not used as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3802
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '30 day'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G170 — O-FRD-54602 [O-FRD]
- **Q:** Were all Adjustable Rate (ARM) term requirements met?
- **Defect condition:** 3/6 month SOFR ARM qualifying rate not equal to the Note rate plus Life Cap (5%)
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3270
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '6 month'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G171 — O-FRD-54603 [O-FRD]
- **Q:** Were all Adjustable Rate (ARM) term requirements met?
- **Defect condition:** 5/6 month SOFR ARM qualifying rate not equal to  greater of Note Rate + 2% or fully indexed rate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3272
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '6 month'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G172 — O-FRD-54605 [O-FRD]
- **Q:** Were all Adjustable Rate (ARM) term requirements met?
- **Defect condition:** 7/6 or 10/6 month HPCT/HPML SOFR ARM, qualifying rate not greater of Note Rate or fully indexed rate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3273, 3274
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '6 month'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G173 — O-FRD-55096 [O-FRD]
- **Q:** Were all Adjustable Rate (ARM) term requirements met?
- **Defect condition:** SOFR ARM 3/6, 5/6, 7/6 or 10/6 initial fixed rate period is not 36, 60, 84 or 120 mos as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3801
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '6 month'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G175 — O-VA-50777 [O-VA]
- **Q:** Were all Adjustable Rate Mortgage (ARM) requirements met?
- **Defect condition:** Loan underwritten at the incorrect interest rate based on ARM type
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3296
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G176 — O-VA-52891 [O-VA]
- **Q:** Were all Adjustable Rate Mortgage (ARM) requirements met?
- **Defect condition:** The ARM product index is not a CMT rate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3283
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G178 — O-FNM-52742 [O-FNM]
- **Q:** Were all Adjustable-Rate Mortgages (ARMs) general requirements  met?
- **Defect condition:** A SOFR ARM underwritten by DU was not submitted as a generic ARM
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3800
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.4-02 — Adjustable-Rate Mortgages (ARMs) (PDF p.207)
- **Guide candidate:** B2-1.4-01 — Fixed-Rate Loans (PDF p.206)
- **Guide candidate:** B2-1.4-03 — Convertible ARMs (PDF p.215)
- **SME:** [ ] agree [ ] correct: ______

### G179 — O-FNM-50218 [O-FNM]
- **Q:** Were all Adjustable-Rate Mortgages (ARMs) general requirements  met?
- **Defect condition:** All characteristics in Standard ARM Plan Matrix not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3282
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.4-02 — Adjustable-Rate Mortgages (ARMs) (PDF p.207)
- **Guide candidate:** C2-1.1-07 — Standard ARM and Converted ARM Resale Commitments (PDF p.971)
- **Guide candidate:** B2-1.4-01 — Fixed-Rate Loans (PDF p.206)
- **SME:** [ ] agree [ ] correct: ______

### G180 — O-FNM-55775 [O-FNM]
- **Q:** Were all Adjustable-Rate Mortgages (ARMs) general requirements  met?
- **Defect condition:** Fully indexed rate is not the index value in effect during the 90 days that precede the note date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3446
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '90 days'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.4-02 — Adjustable-Rate Mortgages (ARMs) (PDF p.207)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **Guide candidate:** B2-1.2-01 — Loan-to-Value (LTV) Ratios (PDF p.179)
- **SME:** [ ] agree [ ] correct: ______

### G181 — O-FNM-55774 [O-FNM]
- **Q:** Were all Adjustable-Rate Mortgages (ARMs) general requirements  met?
- **Defect condition:** Fully indexed rate not the sum of the applicable index & the mtg margin rounded to the nearest 1/8%
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3447
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '8%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.4-02 — Adjustable-Rate Mortgages (ARMs) (PDF p.207)
- **Guide candidate:** B2-1.4-01 — Fixed-Rate Loans (PDF p.206)
- **Guide candidate:** B2-1.4-03 — Convertible ARMs (PDF p.215)
- **SME:** [ ] agree [ ] correct: ______

### G182 — O-FNM-50216 [O-FNM]
- **Q:** Were all Adjustable-Rate Mortgages (ARMs) general requirements  met?
- **Defect condition:** One or more standard ARM requirements were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3820
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.4-02 — Adjustable-Rate Mortgages (ARMs) (PDF p.207)
- **Guide candidate:** C2-1.1-07 — Standard ARM and Converted ARM Resale Commitments (PDF p.971)
- **Guide candidate:** B2-1.4-01 — Fixed-Rate Loans (PDF p.206)
- **SME:** [ ] agree [ ] correct: ______

### G183 — O-FNM-50217 [O-FNM]
- **Q:** Were all Adjustable-Rate Mortgages (ARMs) general requirements  met?
- **Defect condition:** The ARM Plan index was unacceptable to FNMA
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3289
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** ARM-Plan-index membership test against FNMA's approved-index list
- **Data needed:** ARM index name field + an FNMA-approved-index reference list (an SME-maintained list, not a document-extraction gap)
- **Rationale:** 'Unacceptable to FNMA' has a real comparison basis — a specific, enumerable list of approved indices — not open-ended judgment.
- **Guide candidate:** B2-1.4-02 — Adjustable-Rate Mortgages (ARMs) (PDF p.207)
- **Guide candidate:** B2-1.4-01 — Fixed-Rate Loans (PDF p.206)
- **Guide candidate:** B2-1.4-03 — Convertible ARMs (PDF p.215)
- **SME:** [ ] agree [ ] correct: ______

### G184 — O-FNM-53027 [O-FNM]
- **Q:** Were all Adjustable-Rate Mortgages (ARMs) general requirements  met?
- **Defect condition:** The Note and Riders did not contain the updated index “fallback” language in a non-SOFR ARM loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3284
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.4-02 — Adjustable-Rate Mortgages (ARMs) (PDF p.207)
- **Guide candidate:** B5-3.2-02 — HomeStyle Renovation Mortgages: Loan and Borrower Eligibility (PDF p.747)
- **Guide candidate:** B6-1-01 — General Government Mortgage Loan Requirements (PDF p.837)
- **SME:** [ ] agree [ ] correct: ______

### G185 — O-FNM-50219 [O-FNM]
- **Q:** Were all Adjustable-Rate Mortgages (ARMs) general requirements  met?
- **Defect condition:** The difference in the initial note rate and the fully indexed rate > 3%
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3286
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** initial-note-rate-vs-fully-indexed-rate > 3% threshold
- **Data needed:** note rate (mismo_note_rate extracted) + index/margin fields for the fully-indexed-rate computation
- **Rationale:** Fully crisp numeric threshold (3%) with a stated comparison basis — 'unacceptable' just names the outcome.
- **Guide candidate:** B2-1.4-02 — Adjustable-Rate Mortgages (ARMs) (PDF p.207)
- **Guide candidate:** B2-1.4-01 — Fixed-Rate Loans (PDF p.206)
- **Guide candidate:** B2-1.4-03 — Convertible ARMs (PDF p.215)
- **SME:** [ ] agree [ ] correct: ______

### G187 — O-FNM-54585 [O-FNM]
- **Q:** Were all Adjustable-Rate Mortgages (ARMs) program requirements  met?
- **Defect condition:** ATR 3-year ARM qualifying rate is not equal to the Note Rate + 5%
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3293
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '3-year'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.4-02 — Adjustable-Rate Mortgages (ARMs) (PDF p.207)
- **Guide candidate:** B2-1.4-01 — Fixed-Rate Loans (PDF p.206)
- **Guide candidate:** B2-1.4-03 — Convertible ARMs (PDF p.215)
- **SME:** [ ] agree [ ] correct: ______

### G188 — O-FNM-54586 [O-FNM]
- **Q:** Were all Adjustable-Rate Mortgages (ARMs) program requirements  met?
- **Defect condition:** ATR 5-year ARM qualifying rate not equal to greater of fully indexed rate or Note Rate + 2%
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3294
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '5-year'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.4-02 — Adjustable-Rate Mortgages (ARMs) (PDF p.207)
- **Guide candidate:** B2-1.4-01 — Fixed-Rate Loans (PDF p.206)
- **Guide candidate:** B2-1.4-03 — Convertible ARMs (PDF p.215)
- **SME:** [ ] agree [ ] correct: ______

### G189 — O-FNM-54587 [O-FNM]
- **Q:** Were all Adjustable-Rate Mortgages (ARMs) program requirements  met?
- **Defect condition:** ATR 7 or 10-year ARM qualifying rate not equal to greater of fully indexed rate or Note Rate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3295
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '10-year'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.4-02 — Adjustable-Rate Mortgages (ARMs) (PDF p.207)
- **Guide candidate:** B2-1.4-01 — Fixed-Rate Loans (PDF p.206)
- **Guide candidate:** B2-1.4-03 — Convertible ARMs (PDF p.215)
- **SME:** [ ] agree [ ] correct: ______

### G190 — O-FNM-54581 [O-FNM]
- **Q:** Were all Adjustable-Rate Mortgages (ARMs) program requirements  met?
- **Defect condition:** ATR covered 3 yr ARM maximum interest rate ceiling exceeds the note rate plus the lifetime cap
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3298
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '3 year'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.4-02 — Adjustable-Rate Mortgages (ARMs) (PDF p.207)
- **Guide candidate:** B2-1.4-04 — Temporary Interest Rate Buydowns (PDF p.219)
- **Guide candidate:** C2-1.1-06 — Accrued Interest Payments for Regularly Amortizing Mortgages (PDF p.970)
- **SME:** [ ] agree [ ] correct: ______

### G191 — O-FNM-54582 [O-FNM]
- **Q:** Were all Adjustable-Rate Mortgages (ARMs) program requirements  met?
- **Defect condition:** ATR covered 5 yr ARM max interest rate ceiling exceeds the note rate plus the first rate change cap
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3299
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '5 year'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.4-02 — Adjustable-Rate Mortgages (ARMs) (PDF p.207)
- **Guide candidate:** B2-1.4-04 — Temporary Interest Rate Buydowns (PDF p.219)
- **Guide candidate:** C2-1.1-06 — Accrued Interest Payments for Regularly Amortizing Mortgages (PDF p.970)
- **SME:** [ ] agree [ ] correct: ______

### G192 — O-FNM-50220 [O-FNM]
- **Q:** Were all Adjustable-Rate Mortgages (ARMs) program requirements  met?
- **Defect condition:** All eligibility requirements not met for Convertible ARM loans
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3404
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.4-02 — Adjustable-Rate Mortgages (ARMs) (PDF p.207)
- **Guide candidate:** B2-1.4-01 — Fixed-Rate Loans (PDF p.206)
- **Guide candidate:** B2-1.4-03 — Convertible ARMs (PDF p.215)
- **SME:** [ ] agree [ ] correct: ______

### G193 — O-FNM-54579 [O-FNM]
- **Q:** Were all Adjustable-Rate Mortgages (ARMs) program requirements  met?
- **Defect condition:** Loan amt over term not used to calculate periodic pymts of P&I for short term ARM ATR covered loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3767
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.4-02 — Adjustable-Rate Mortgages (ARMs) (PDF p.207)
- **Guide candidate:** B5-3.2-02 — HomeStyle Renovation Mortgages: Loan and Borrower Eligibility (PDF p.747)
- **Guide candidate:** C3-4-01 — Term-Related Fixed-Rate Mortgage Pooling Parameters (PDF p.1011)
- **SME:** [ ] agree [ ] correct: ______

### G194 — O-FNM-54583 [O-FNM]
- **Q:** Were all Adjustable-Rate Mortgages (ARMs) program requirements  met?
- **Defect condition:** Qualifying rate used not appropriate for an ATR covered 1 year ARM with a 1% annual cap
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3291
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** qualifying rate == Note rate + 5% for a 1-year 1%-annual-cap ATR ARM
- **Data needed:** 'qualifying rate used' as its own field (mismo_note_rate exists; the rate UNDERWRITING actually qualified against, and the ARM's annual-cap sub-type, are not yet distinct fields)
- **Rationale:** The row states the exact formula inline ('Note rate plus 5%') — this is as close to GREEN as this block gets; only the qualifying-rate and cap-type fields are missing, not the underlying math.
- **Guide candidate:** B2-1.4-02 — Adjustable-Rate Mortgages (ARMs) (PDF p.207)
- **Guide candidate:** B2-1.4-01 — Fixed-Rate Loans (PDF p.206)
- **Guide candidate:** B2-1.4-03 — Convertible ARMs (PDF p.215)
- **SME:** [ ] agree [ ] correct: ______

### G195 — O-FNM-54584 [O-FNM]
- **Q:** Were all Adjustable-Rate Mortgages (ARMs) program requirements  met?
- **Defect condition:** Qualifying rate used not appropriate for an ATR covered 1 year ARM with a 2% annual cap
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3292
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** qualifying rate == Note rate + 6% for a 1-year 2%-annual-cap ATR ARM
- **Data needed:** same fields as G194
- **Rationale:** Same family as G194 — the exact formula is stated in-row.
- **Guide candidate:** B2-1.4-02 — Adjustable-Rate Mortgages (ARMs) (PDF p.207)
- **Guide candidate:** B2-1.4-01 — Fixed-Rate Loans (PDF p.206)
- **Guide candidate:** B2-1.4-03 — Convertible ARMs (PDF p.215)
- **SME:** [ ] agree [ ] correct: ______

### G196 — O-FNM-54580 [O-FNM]
- **Q:** Were all Adjustable-Rate Mortgages (ARMs) program requirements  met?
- **Defect condition:** Short term ARM qualifying interest rate not calculated using the required method in ATR covered loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3768
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** short-term-ARM qualifying-rate recompute (FNM variant)
- **Data needed:** same as G164
- **Rationale:** Same family as G164 (FRD variant) — 'required method' names a real, defined calculation.
- **Guide candidate:** B2-1.4-02 — Adjustable-Rate Mortgages (ARMs) (PDF p.207)
- **Guide candidate:** B2-1.4-04 — Temporary Interest Rate Buydowns (PDF p.219)
- **Guide candidate:** B5-3.2-02 — HomeStyle Renovation Mortgages: Loan and Borrower Eligibility (PDF p.747)
- **SME:** [ ] agree [ ] correct: ______

### G198 — O-VA-50775 [O-VA]
- **Q:** Were all Alternations and Repairs loan requirements met?
- **Defect condition:** Alteration/repair loan, subject not owned & occupied or made to purchase the property
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3279
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G200 — O-FNM-54034 [O-FNM]
- **Q:** Were all Community Seconds and Community Land Trusts requirements met?
- **Defect condition:** Affordable LTV was not calculated appropriately in subject community land trust purchase
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3358
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B4-1.4-06 — Community Land Trust Appraisal Requirements (PDF p.623)
- **Guide candidate:** B5-5.1-01 — Community Seconds Loans (PDF p.783)
- **Guide candidate:** B5-5.1-02 — Community Seconds Loan Eligibility (PDF p.784)
- **SME:** [ ] agree [ ] correct: ______

### G201 — O-FNM-50916 [O-FNM]
- **Q:** Were all Community Seconds and Community Land Trusts requirements met?
- **Defect condition:** Community Second mtg was not obtained from an allowable party and/or all requirements not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3369
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** Community-Second source-party membership test
- **Stays human:** 'all requirements not met' (unstated residual)
- **Data needed:** second-mortgage source-party field + an allowable-party reference list (not in corpus)
- **Rationale:** 'Allowable party' is a real, bounded, enumerable list (nonprofit/government/employer-type sources), same family as G210's CLT check; the appended 'all requirements' clause stays human.
- **Guide candidate:** B4-1.4-06 — Community Land Trust Appraisal Requirements (PDF p.623)
- **Guide candidate:** B5-5.1-01 — Community Seconds Loans (PDF p.783)
- **Guide candidate:** B5-5.1-02 — Community Seconds Loan Eligibility (PDF p.784)
- **SME:** [ ] agree [ ] correct: ______

### G202 — O-FNM-56352 [O-FNM]
- **Q:** Were all Community Seconds and Community Land Trusts requirements met?
- **Defect condition:** Community second shared appreciation transaction did not meet repayment distribution requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3374
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-5.1-03 — Community Seconds: Shared Appreciation Transactions (PDF p.789)
- **Guide candidate:** B4-1.4-06 — Community Land Trust Appraisal Requirements (PDF p.623)
- **Guide candidate:** B5-5.1-01 — Community Seconds Loans (PDF p.783)
- **SME:** [ ] agree [ ] correct: ______

### G203 — O-FNM-56348 [O-FNM]
- **Q:** Were all Community Seconds and Community Land Trusts requirements met?
- **Defect condition:** Minimum borrower contribution requirement was not met for a transaction with a community second loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3370
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-5.1-02 — Community Seconds Loan Eligibility (PDF p.784)
- **Guide candidate:** B4-1.4-06 — Community Land Trust Appraisal Requirements (PDF p.623)
- **Guide candidate:** B5-3.2-02 — HomeStyle Renovation Mortgages: Loan and Borrower Eligibility (PDF p.747)
- **SME:** [ ] agree [ ] correct: ______

### G205 — O-FNM-56347 [O-FNM]
- **Q:** Were all Community Seconds and Community Land Trusts requirements met?
- **Defect condition:** The community second loan proceeds were used toward an unacceptable use of funds
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3375
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-5.1-02 — Community Seconds Loan Eligibility (PDF p.784)
- **Guide candidate:** B3-4.2-04 — Pooled Savings (Community Savings Funds) (PDF p.438)
- **Guide candidate:** B4-1.4-06 — Community Land Trust Appraisal Requirements (PDF p.623)
- **SME:** [ ] agree [ ] correct: ______

### G206 — O-FNM-56349 [O-FNM]
- **Q:** Were all Community Seconds and Community Land Trusts requirements met?
- **Defect condition:** The community second repayment structure is unacceptable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3371
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B4-1.4-06 — Community Land Trust Appraisal Requirements (PDF p.623)
- **Guide candidate:** B5-5.1-01 — Community Seconds Loans (PDF p.783)
- **Guide candidate:** B5-5.1-02 — Community Seconds Loan Eligibility (PDF p.784)
- **SME:** [ ] agree [ ] correct: ______

### G207 — O-FNM-56351 [O-FNM]
- **Q:** Were all Community Seconds and Community Land Trusts requirements met?
- **Defect condition:** The community second shared appreciation transaction did not meet eligibility requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3372
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-5.1-03 — Community Seconds: Shared Appreciation Transactions (PDF p.789)
- **Guide candidate:** B5-5.1-02 — Community Seconds Loan Eligibility (PDF p.784)
- **Guide candidate:** B4-1.4-06 — Community Land Trust Appraisal Requirements (PDF p.623)
- **SME:** [ ] agree [ ] correct: ______

### G208 — O-FNM-56350 [O-FNM]
- **Q:** Were all Community Seconds and Community Land Trusts requirements met?
- **Defect condition:** The community second shared appreciation transaction did not meet provider requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3373
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-5.1-03 — Community Seconds: Shared Appreciation Transactions (PDF p.789)
- **Guide candidate:** B4-1.4-06 — Community Land Trust Appraisal Requirements (PDF p.623)
- **Guide candidate:** B5-5.1-01 — Community Seconds Loans (PDF p.783)
- **SME:** [ ] agree [ ] correct: ______

### G209 — O-FNM-54033 [O-FNM]
- **Q:** Were all Community Seconds and Community Land Trusts requirements met?
- **Defect condition:** The subject's community ground lease is not based upon either the NCLTN or ICE ground lease models
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3364
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B4-1.4-06 — Community Land Trust Appraisal Requirements (PDF p.623)
- **Guide candidate:** B5-5.1-01 — Community Seconds Loans (PDF p.783)
- **Guide candidate:** B5-5.1-02 — Community Seconds Loan Eligibility (PDF p.784)
- **SME:** [ ] agree [ ] correct: ______

### G210 — O-FNM-56359 [O-FNM]
- **Q:** Were all Community Seconds and Community Land Trusts requirements met?
- **Defect condition:** Title policy/endorsement missing specific req's for community land trust/shared equity transactions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3355
- **Severity:** Critical
- **Classification method:** hand_verified
- **Data needed:** a specific CLT/shared-equity clause WITHIN the title policy (deepen title_commitment extraction, not mere presence)
- **Rationale:** eval_class=doc_presence targets title_commitment, but the condition is 'title policy/endorsement MISSING SPECIFIC REQUIREMENTS for community land trust/shared equity' — content-level, not presence-level. Any loan with an ordinary title commitment (every loan in this corpus) would false-PASS a check that only verifies the doc type exists.
- **Guide candidate:** B5-5.1-03 — Community Seconds: Shared Appreciation Transactions (PDF p.789)
- **Guide candidate:** B4-1.4-06 — Community Land Trust Appraisal Requirements (PDF p.623)
- **Guide candidate:** B5-5.3-02 — Shared Equity Transactions: General Requirements (PDF p.798)
- **SME:** [ ] agree [ ] correct: ______

### G211 — O-FHA-02317 [O-FHA]
- **Q:** Were all Energy Efficient Mortgage (EEM) program requirements met?
- **Defect condition:** Energy efficient improvements without 92900-LT demonstrating the mtg and property are FHA compliant
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3431
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'hud_92900a' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'hud_92900a', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G212 — O-FHA-51053 [O-FHA]
- **Q:** Were all Energy Efficient Mortgage (EEM) program requirements met?
- **Defect condition:** Energy efficient loan file did not contain a copy of the home energy report
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3427
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G213 — O-FHA-00608 [O-FHA]
- **Q:** Were all Energy Efficient Mortgage (EEM) program requirements met?
- **Defect condition:** Verification the amount added to the mtg meets HUD energy efficient program requirements not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3430
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G215 — O-VA-00479 [O-VA]
- **Q:** Were all Energy Efficient Mortgages requirements met?
- **Defect condition:** IRRRL w/ energy efficiency improvements missing documentation as required for amounts up to $6,000
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3426
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '$6,000'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G217 — O-VA-00656 [O-VA]
- **Q:** Were all Energy Efficient Mortgages requirements met?
- **Defect condition:** The Cost of Energy efficiency improvements not considered or properly documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3428
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** energy-efficiency-improvement cost documentation presence
- **Data needed:** an energy-improvement cost estimate/documentation type (not in corpus)
- **Rationale:** 'Properly documented' names a real, specific documentation requirement, not an open-ended judgment.
- **SME:** [ ] agree [ ] correct: ______

### G218 — O-VA-50780 [O-VA]
- **Q:** Were all Farm Residence Loan requirements met?
- **Defect condition:** Nonresidential value of farm land ex barn, silo, farm equip or livestock etc included in loan amt
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3438
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** nonresidential (farm) value exclusion from loan amount
- **Data needed:** a farm-value/nonresidential-value breakdown field on the appraisal (appraisal doc exists; this specific breakdown field does not)
- **Rationale:** Crisp dollar-value exclusion test once the appraisal breakdown field exists — not a subjective call.
- **SME:** [ ] agree [ ] correct: ______

### G220 — O-FHA-51137 [O-FHA]
- **Q:** Were all HUD Real Estate Owned (REO) Property requirements met?
- **Defect condition:** All repair completion escrow requirements were not met in this Section 203(b) with repair escrow
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3519
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G221 — O-FHA-51138 [O-FHA]
- **Q:** Were all HUD Real Estate Owned (REO) Property requirements met?
- **Defect condition:** HUD REO 203(k) or 203(b) using Good Neighbor Next Door or $100 Down did not meet all requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3521
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '$100'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G222 — O-FHA-51136 [O-FHA]
- **Q:** Were all HUD Real Estate Owned (REO) Property requirements met?
- **Defect condition:** HUD REO-Form HUD-9548 & addenda setting the sale terms/eligibility not in file or did not meet req's
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3520
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** Form HUD-9548 + addenda presence
- **Stays human:** 'did not meet all requirements' (unstated residual)
- **Data needed:** HUD-9548 (Sales Contract Property Disposition Program) doc type (not in corpus)
- **Rationale:** Presence half is crisp; the appended catch-all clause stays human — same pattern as G145.
- **SME:** [ ] agree [ ] correct: ______

### G224 — O-FHA-59010 [O-FHA]
- **Q:** Were all HUD-92544, Warranty of Completion of Construction, requirements met?
- **Defect condition:** HUD-92544, Warranty of Completion of Construction, missing builder's name, address, and phone number
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3866
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G225 — O-FHA-59003 [O-FHA]
- **Q:** Were all HUD-92544, Warranty of Completion of Construction, requirements met?
- **Defect condition:** HUD-92544, Warranty of Completion of Construction, missing lender's name, address, and phone number
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3870
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G226 — O-FHA-59007 [O-FHA]
- **Q:** Were all HUD-92544, Warranty of Completion of Construction, requirements met?
- **Defect condition:** HUD-92544, Warranty of Completion of Construction, was missing manufacturer's info, as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3871
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G227 — O-FHA-59005 [O-FHA]
- **Q:** Were all HUD-92544, Warranty of Completion of Construction, requirements met?
- **Defect condition:** HUD-92544, Warranty of Completion of Construction, was missing the FHA Case Number
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3867
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G228 — O-FHA-59004 [O-FHA]
- **Q:** Were all HUD-92544, Warranty of Completion of Construction, requirements met?
- **Defect condition:** HUD-92544, Warranty of Completion of Construction, was missing the name of the purchaser/owner
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3872
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G229 — O-FHA-59006 [O-FHA]
- **Q:** Were all HUD-92544, Warranty of Completion of Construction, requirements met?
- **Defect condition:** HUD-92544, Warranty of Completion of Construction, was missing the property address
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3873
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G230 — O-FHA-59009 [O-FHA]
- **Q:** Were all HUD-92544, Warranty of Completion of Construction, requirements met?
- **Defect condition:** HUD-92544, Warranty of Completion of Construction, was missing the purchaser's signature and date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3579
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G231 — O-FHA-59008 [O-FHA]
- **Q:** Were all HUD-92544, Warranty of Completion of Construction, requirements met?
- **Defect condition:** HUD-92544, Warranty of Completion of Construction, was missing warrantor's title, signature, & date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3580
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G232 — O-FHA-50735 [O-FHA]
- **Q:** Were all HUD-92544, Warranty of Completion of Construction, requirements met?
- **Defect condition:** New construction loan file did not contain form HUD-92544, Warranty of Completion of Construction
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3869
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G234 — O-FNM-51185 [O-FNM]
- **Q:** Were all HomeReady requirements met?
- **Defect condition:** A HomeReady and HomeStyle Renovation is combined without all mortgage insurance req's being met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3490
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-6-03 — HomeReady Mortgage Loan Pricing, Mortgage Insurance, and Special Feature Codes (PDF p.818)
- **Guide candidate:** B8-5-03 — HomeStyle Renovation Mortgage Documentation Requirements (PDF p.924)
- **Guide candidate:** B5-1-02 — High-Balance Pricing, Mortgage Insurance, Special Feature Codes, and Delivery Limitations (PDF p.717)
- **SME:** [ ] agree [ ] correct: ______

### G235 — O-FNM-50328 [O-FNM]
- **Q:** Were all HomeReady requirements met?
- **Defect condition:** All HomeReady req's for an LTV, CLTV, or HCLTV Ratio of 95.01 –97% not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3488
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** explicit 95.01-97% LTV/CLTV/HCLTV band gate
- **Stays human:** the specific bundle of 'requirements' beyond the LTV band (unstated in-row)
- **Data needed:** HomeReady 95.01-97% LTV-band requirement checklist (an SME-defined list)
- **Rationale:** Same pattern as G109 — a genuine numeric band as the gate, the full requirement list unstated.
- **Guide candidate:** B2-1.2-01 — Loan-to-Value (LTV) Ratios (PDF p.179)
- **Guide candidate:** B2-1.2-02 — Combined Loan-to-Value (CLTV) Ratios (PDF p.181)
- **Guide candidate:** B2-1.2-03 — Home Equity Combined Loan-to-Value (HCLTV) Ratios (PDF p.182)
- **SME:** [ ] agree [ ] correct: ______

### G236 — O-FNM-00193 [O-FNM]
- **Q:** Were all HomeReady requirements met?
- **Defect condition:** Credit score insufficient and non-traditional credit requirements not met; FNMA HomeReady product
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3500
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B3-5.1-02 — Determining the Credit Score for a Mortgage Loan (PDF p.474)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **SME:** [ ] agree [ ] correct: ______

### G237 — O-FNM-50329 [O-FNM]
- **Q:** Were all HomeReady requirements met?
- **Defect condition:** HomeReady borrower minimum contribution not met with LTV over 80%
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3497
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '80%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-6-01 — HomeReady Mortgage Loan and Borrower Eligibility (PDF p.808)
- **Guide candidate:** B5-7-01 — High LTV Reﬁnance Loan and Borrower Eligibility (PDF p.819)
- **Guide candidate:** B2-1.2-01 — Loan-to-Value (LTV) Ratios (PDF p.179)
- **SME:** [ ] agree [ ] correct: ______

### G238 — O-FNM-55903 [O-FNM]
- **Q:** Were all HomeReady requirements met?
- **Defect condition:** HomeReady lender-funded grant terms & conditions of the grant program is not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3495
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** D1-3-02 — Lender Post-Closing Quality Control Review of Approval Conditions, Underwriting Decisions, Data, and Documentation (PDF p.1068)
- **Guide candidate:** A2-3.1-01 — Lender Breach of Contract (PDF p.56)
- **Guide candidate:** B3-3.4-14 — Section 8 Housing Choice Voucher Homeownership Program Payments (PDF p.370)
- **SME:** [ ] agree [ ] correct: ______

### G239 — O-FNM-55905 [O-FNM]
- **Q:** Were all HomeReady requirements met?
- **Defect condition:** HomeReady lender-funded grant was funded through premium pricing or another way through the loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3493
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-6-03 — HomeReady Mortgage Loan Pricing, Mortgage Insurance, and Special Feature Codes (PDF p.818)
- **Guide candidate:** B5-2-04 — Manufactured Housing Pricing, Mortgage Insurance, and Loan Delivery Requirements (PDF p.727)
- **Guide candidate:** B5-6-01 — HomeReady Mortgage Loan and Borrower Eligibility (PDF p.808)
- **SME:** [ ] agree [ ] correct: ______

### G240 — O-FNM-51184 [O-FNM]
- **Q:** Were all HomeReady requirements met?
- **Defect condition:** HomeReady using boarder income, the boarder is obligated on the mtg or has an ownership interest
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3487
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B3-3.4-04 — Boarder Income (PDF p.356)
- **Guide candidate:** B3-3.4-08 — Interest and Dividend Income (PDF p.363)
- **Guide candidate:** B3-3.4-19 — Schedule K-1 Income <25% Ownership (PDF p.378)
- **SME:** [ ] agree [ ] correct: ______

### G241 — O-FNM-50330 [O-FNM]
- **Q:** Were all HomeReady requirements met?
- **Defect condition:** HomeReady-No homeowner education by 1 borr where all occupying borr's are 1st time homebuyers
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3489
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-2-06 — Homeownership Education and Housing Counseling (PDF p.253)
- **Guide candidate:** B5-6-01 — HomeReady Mortgage Loan and Borrower Eligibility (PDF p.808)
- **Guide candidate:** B5-6-02 — HomeReady Mortgage Underwriting Methods and Requirements (PDF p.813)
- **SME:** [ ] agree [ ] correct: ______

### G242 — O-FNM-55904 [O-FNM]
- **Q:** Were all HomeReady requirements met?
- **Defect condition:** Min 3% contribution from own funds/eligible source not made in a HomeReady w/ a lender-funded grant
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3494
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '3%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** A2-3.1-01 — Lender Breach of Contract (PDF p.56)
- **Guide candidate:** B3-2-05 — Approve/Eligible Recommendations (PDF p.306)
- **Guide candidate:** B3-4.1-03 — Lender Incentives (PDF p.428)
- **SME:** [ ] agree [ ] correct: ______

### G243 — O-FNM-50917 [O-FNM]
- **Q:** Were all HomeReady requirements met?
- **Defect condition:** The mortgage was ineligible under the HomeReady borrower income limits
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3491
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-6-01 — HomeReady Mortgage Loan and Borrower Eligibility (PDF p.808)
- **Guide candidate:** B3-3.3-06 — Mortgage Diﬀerential Payments Income (PDF p.343)
- **Guide candidate:** B5-6-02 — HomeReady Mortgage Underwriting Methods and Requirements (PDF p.813)
- **SME:** [ ] agree [ ] correct: ______

### G245 — O-FNM-00538 [O-FNM]
- **Q:** Were all HomeStyle Energy mortgage requirements met?
- **Defect condition:** Energy-related improvement work not documented in a HomeStyle such as the energy report or similar
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3506
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'appraisal', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B8-5-03 — HomeStyle Renovation Mortgage Documentation Requirements (PDF p.924)
- **Guide candidate:** C3-4-01 — Term-Related Fixed-Rate Mortgage Pooling Parameters (PDF p.1011)
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **SME:** [ ] agree [ ] correct: ______

### G246 — O-FNM-56090 [O-FNM]
- **Q:** Were all HomeStyle Energy mortgage requirements met?
- **Defect condition:** HomeStyle Energy financed improvements that are not on the list of ENERGY STAR Efficient Products
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3509
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-3.3-01 — HomeStyle Refresh for Improvements on Existing Properties (PDF p.760)
- **Guide candidate:** B7-1-04 — Financed Borrower-Purchased Mortgage Insurance (PDF p.855)
- **Guide candidate:** B8-5-03 — HomeStyle Renovation Mortgage Documentation Requirements (PDF p.924)
- **SME:** [ ] agree [ ] correct: ______

### G247 — O-FNM-52894 [O-FNM]
- **Q:** Were all HomeStyle Energy mortgage requirements met?
- **Defect condition:** HomeStyle Energy financing used to pay off energy-related debt did not pay the entire debt in full
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3505
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B8-5-03 — HomeStyle Renovation Mortgage Documentation Requirements (PDF p.924)
- **Guide candidate:** C3-4-01 — Term-Related Fixed-Rate Mortgage Pooling Parameters (PDF p.1011)
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **SME:** [ ] agree [ ] correct: ______

### G248 — O-FNM-58665 [O-FNM]
- **Q:** Were all HomeStyle Energy mortgage requirements met?
- **Defect condition:** HomeStyle alt documentation (besides an energy report) used w/out meeting qualified circumstances
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3507
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B8-5-03 — HomeStyle Renovation Mortgage Documentation Requirements (PDF p.924)
- **Guide candidate:** B8-5-02 — Inter Vivos Revocable Trust Mortgage Documentation and Signature Requirements (PDF p.921)
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **SME:** [ ] agree [ ] correct: ______

### G249 — O-FNM-58663 [O-FNM]
- **Q:** Were all HomeStyle Energy mortgage requirements met?
- **Defect condition:** HomeStyle energy report did not contain savings, recomm improvements, cost-effect &/or est cost
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3528
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B4-1.3-05 — Improvements Section of the Appraisal Report (PDF p.580)
- **Guide candidate:** B5-3.3-01 — HomeStyle Refresh for Improvements on Existing Properties (PDF p.760)
- **Guide candidate:** B8-5-03 — HomeStyle Renovation Mortgage Documentation Requirements (PDF p.924)
- **SME:** [ ] agree [ ] correct: ______

### G250 — O-FNM-58664 [O-FNM]
- **Q:** Were all HomeStyle Energy mortgage requirements met?
- **Defect condition:** HomeStyle energy report did not meet HERS, DOE, or comparable independent and certified standards
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3508
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B8-5-03 — HomeStyle Renovation Mortgage Documentation Requirements (PDF p.924)
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **Guide candidate:** A2-4.1-04 — Notarization Standards (PDF p.99)
- **SME:** [ ] agree [ ] correct: ______

### G251 — O-FNM-58662 [O-FNM]
- **Q:** Were all HomeStyle Energy mortgage requirements met?
- **Defect condition:** HomeStyle loan missing an energy report or report was dated more than 24 mons before the note date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3578
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '24 months'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B3-5.1-02 — Determining the Credit Score for a Mortgage Loan (PDF p.474)
- **Guide candidate:** B5-1-01 — High-Balance Mortgage Loan Eligibility and Underwriting (PDF p.715)
- **Guide candidate:** B5-2-04 — Manufactured Housing Pricing, Mortgage Insurance, and Loan Delivery Requirements (PDF p.727)
- **SME:** [ ] agree [ ] correct: ______

### G253 — O-FNM-50321 [O-FNM]
- **Q:** Were all HomeStyle Renovation mortgage requirements met?
- **Defect condition:** Appraisal did not give "as completed" value for Homestyle Renovation mtg
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3515, 3516
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'appraisal', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B8-5-03 — HomeStyle Renovation Mortgage Documentation Requirements (PDF p.924)
- **Guide candidate:** B5-3.2-01 — HomeStyle Renovation Mortgages (PDF p.744)
- **Guide candidate:** B5-3.2-02 — HomeStyle Renovation Mortgages: Loan and Borrower Eligibility (PDF p.747)
- **SME:** [ ] agree [ ] correct: ______

### G254 — O-FNM-50323 [O-FNM]
- **Q:** Were all HomeStyle Renovation mortgage requirements met?
- **Defect condition:** HomeStyle Construction Contract and Loan Agrmt incomplete or unclear title
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3503
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-3.2-06 — HomeStyle Renovation: Renovation Contract, Renovation Loan Agreement, and Lien Waiver (PDF p.757)
- **Guide candidate:** B5-3.2-02 — HomeStyle Renovation Mortgages: Loan and Borrower Eligibility (PDF p.747)
- **Guide candidate:** B8-5-03 — HomeStyle Renovation Mortgage Documentation Requirements (PDF p.924)
- **SME:** [ ] agree [ ] correct: ______

### G255 — O-FNM-50884 [O-FNM]
- **Q:** Were all HomeStyle Renovation mortgage requirements met?
- **Defect condition:** HomeStyle LCO, funds after reno not a curtailment or reimburse to borr for costs &/or no receipts
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3510
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-3.2-04 — HomeStyle Renovation Mortgages: Costs and Escrow Accounts (PDF p.753)
- **Guide candidate:** B8-5-03 — HomeStyle Renovation Mortgage Documentation Requirements (PDF p.924)
- **Guide candidate:** B5-3.2-01 — HomeStyle Renovation Mortgages (PDF p.744)
- **SME:** [ ] agree [ ] correct: ______

### G256 — O-FNM-50319 [O-FNM]
- **Q:** Were all HomeStyle Renovation mortgage requirements met?
- **Defect condition:** Homestyle LTV not from lesser of "as completed" or sale price + rehab costs
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3513, 3514
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-3.2-04 — HomeStyle Renovation Mortgages: Costs and Escrow Accounts (PDF p.753)
- **Guide candidate:** B8-5-03 — HomeStyle Renovation Mortgage Documentation Requirements (PDF p.924)
- **Guide candidate:** B5-3.2-01 — HomeStyle Renovation Mortgages (PDF p.744)
- **SME:** [ ] agree [ ] correct: ______

### G258 — O-FNM-50882 [O-FNM]
- **Q:** Were all HomeStyle Renovation mortgage requirements met?
- **Defect condition:** The cost of the renovations exceeded the allowable amount as per property and transaction type
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3517
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B8-5-03 — HomeStyle Renovation Mortgage Documentation Requirements (PDF p.924)
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **Guide candidate:** B5-3.2-01 — HomeStyle Renovation Mortgages (PDF p.744)
- **SME:** [ ] agree [ ] correct: ______

### G259 — O-FNM-50951 [O-FNM]
- **Q:** Were all HomeStyle Renovation mortgage requirements met?
- **Defect condition:** The renovation escrow account did not meet all HomeStyle Renovation loan requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3518
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-3.2-02 — HomeStyle Renovation Mortgages: Loan and Borrower Eligibility (PDF p.747)
- **Guide candidate:** B5-3.2-04 — HomeStyle Renovation Mortgages: Costs and Escrow Accounts (PDF p.753)
- **Guide candidate:** B5-3.2-06 — HomeStyle Renovation: Renovation Contract, Renovation Loan Agreement, and Lien Waiver (PDF p.757)
- **SME:** [ ] agree [ ] correct: ______

### G261 — O-VA-57253 [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) borrower requirements met?
- **Defect condition:** IRRRL surviving spouse funding fee exemption without documenting receipt of DIC & VA Form 26-8937
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3833
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G262 — O-VA-50922 [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) borrower requirements met?
- **Defect condition:** In an IRRRL transaction, a final signed Veteran's Statement was not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3861
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G263 — O-VA-57882 [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) borrower requirements met?
- **Defect condition:** Missing Veteran's cert of occupancy 1820 that they previously occupied the property as their home
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3544
- **Severity:** Major
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G264 — O-VA-54254 [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) borrower requirements met?
- **Defect condition:** The IRRRL borrower(s) are not the same as on the original loan & is not an acceptable life event
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3276
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** IRRRL-borrower-vs-original-loan-borrower match (needs prior-loan borrower data)
- **Stays human:** 'acceptable life event' (unstated criteria)
- **Data needed:** prior-loan borrower-identity data (not currently modeled)
- **Rationale:** Compound: the borrower-match half is a crisp fact once prior-loan data exists; the 'acceptable life event' half is a bounded-but-unstated-here judgment, same donor/source-acceptability pattern seen throughout asset-verification.
- **SME:** [ ] agree [ ] correct: ______

### G265 — O-VA-00647 [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) borrower requirements met?
- **Defect condition:** The transaction involves cash proceeds to the borrower or payoff of impermissible debts
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3542
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '$6,000'
- **Data needed:** a field/fact on the existing 'payoff_statement' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'payoff_statement', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G267 — O-VA-52787 [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) closing and delivery requirements met?
- **Defect condition:** IRRRL file did not contain supporting docs of the cure, completion date & already completed actions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3537
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G268 — O-VA-58594 [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) closing and delivery requirements met?
- **Defect condition:** IRRRL replacing the existing VA loan is not the 1st lien on the property w/out a subordination agrmt
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3546
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G269 — O-VA-00795 [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) closing and delivery requirements met?
- **Defect condition:** No, in an IRRRL, the prior VA loan was not current on the day before closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3540
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G270 — O-VA-00864 [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) closing and delivery requirements met?
- **Defect condition:** No, the IRRRL certification of prior VA loan non-delinquency status was not submitted to VA
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3535
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '30 days'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G271 — O-VA-52786 [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) closing and delivery requirements met?
- **Defect condition:** Noncompliant IRRRL has a curative action that resulted in additional costs to the borrower
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3536
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G273 — O-VA-53029 [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) fees requirements met?
- **Defect condition:** Energy Efficient Mortgage dedicated funds not excluded from the statutory fee recoupment calculation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3429
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G274 — O-VA-51740 [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) fees requirements met?
- **Defect condition:** The fee recoupment was not calculated correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3439
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G276 — O-VA-51744 [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) terms requirements met?
- **Defect condition:** Fixed refi to ARM IRRRL and the interest rate was not at least 2% lower than the original rate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3444
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '2%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G277 — O-VA-51743 [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) terms requirements met?
- **Defect condition:** Fixed refi to fixed IRRRL and the interest rate was not at least 0.50% lower than the original rate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3445
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '0.50%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G278 — O-VA-51126 [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) terms requirements met?
- **Defect condition:** IRRRL resulted in lower P&I without certification of recoupment within 36 months from closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3641
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '36 months'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G279 — O-VA-51739 [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) terms requirements met?
- **Defect condition:** IRRRL resulted in same or higher  P&I pymt without certification only customary costs were incurred
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3545
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G280 — O-VA-53030 [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) terms requirements met?
- **Defect condition:** Loan not closed at no cost to the Vet & monthly PI not reduced by the IRRRL from the original ARM PI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3287
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G281 — O-VA-00654 [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) terms requirements met?
- **Defect condition:** New IRRRL PITI increased 20% or more without certifying the Veteran qualifies for the new payment
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3543
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '20%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G282 — O-VA-50773 [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) terms requirements met?
- **Defect condition:** New loan term exceeds the original being refinanced + 10 yrs/exceeded 30 years & 32 days
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3575
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '30 years'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G284 — O-VA-50772 [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) underwriting requirements met?
- **Defect condition:** Completed VA Form 26-8923, IRRRL Worksheet not in file &/or the ln amt calculated incorrectly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3547
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G285 — O-VA-51745 [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) underwriting requirements met?
- **Defect condition:** Discount points added to the loan amount in a fixed refi to ARM IRRRL without meeting all req's
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3538, 3539
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** discount-points-added-to-principal trigger detection
- **Stays human:** 'all requirements being met' (unstated residual)
- **Data needed:** a discount-points-in-IRRRL field (deepen closing_disclosure/1003)
- **Rationale:** The trigger fact (discount points added) is crisp and named; the appended 'all requirements' clause stays human.
- **SME:** [ ] agree [ ] correct: ______

### G286 — O-VA-50961 [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) underwriting requirements met?
- **Defect condition:** Discount points charged in an IRRRL without an appraisal to determine LTV &/or max LTV was exceeded
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3534
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'appraisal', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G287 — O-VA-51746 [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) underwriting requirements met?
- **Defect condition:** File missing Veteran certification that the refi to IRRRL Loan Comparison Statements were received
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3570
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G288 — O-VA-51741 [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) underwriting requirements met?
- **Defect condition:** Final loan disclosure not uploaded during LGC process for recoupment period of 36 months or less
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3643
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '36 months'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G289 — O-VA-54833 [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) underwriting requirements met?
- **Defect condition:** IRRRL seasoning not met at least 210 days since 1st mtg pymt &/or not current last 6 consecutive mos
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3857
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '210 days'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G290 — O-VA-50921 [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) underwriting requirements met?
- **Defect condition:** Lender’s Certification not in the file for IRRRL as req'd if payment increased by 20% or more
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3561
- **Severity:** Major
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '20%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G291 — O-VA-51742 [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) underwriting requirements met?
- **Defect condition:** Recoupment calculation not uploaded during LGC process for recoupment period greater than 36 months
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3642
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '36 months'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G292 — O-VA-54812 [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) underwriting requirements met?
- **Defect condition:** The WebLGY IRRRL Appraisal Case Initiated screen not reviewed to determine funding fee exemption
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3541
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'appraisal', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G295 — O-VA-51645 [O-VA]
- **Q:** Were all Joint Loan requirements met?
- **Defect condition:** Two or more unmarried Veterans each using home entitlement req'd prior VA approval not obtained
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3548
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** prior-VA-approval-record presence for a joint entitlement loan
- **Data needed:** a joint-loan VA prior-approval doc type (not in corpus)
- **Rationale:** Crisp approval-record presence check, not a subjective call.
- **SME:** [ ] agree [ ] correct: ______

### G296 — O-FNM-56354 [O-FNM]
- **Q:** Were all Loans with Resale Restrictions requirements met?
- **Defect condition:** Borrower eligibility requirements not met for a loan with resale restrictions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3734
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-5.2-02 — Loans with Resale Restrictions: Eligibility, Collateral and Delivery Requirements (PDF p.795)
- **Guide candidate:** B4-2.3-04 — Loan Eligibility for Co-op Share Loans (PDF p.712)
- **Guide candidate:** B5-3.2-02 — HomeStyle Renovation Mortgages: Loan and Borrower Eligibility (PDF p.747)
- **SME:** [ ] agree [ ] correct: ______

### G297 — O-FRD-52265 [O-FRD]
- **Q:** Were all Loans with Resale Restrictions requirements met?
- **Defect condition:** Borrower ineligible for property with income-based resale restrictions as per subsidy provider
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3523
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G298 — O-FNM-56358 [O-FNM]
- **Q:** Were all Loans with Resale Restrictions requirements met?
- **Defect condition:** CLT ground lease does not include buyer specific income levels & max sales price limits restrictions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3354
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-5.2-01 — Loans With Resale Restrictions: General Information (PDF p.793)
- **Guide candidate:** B5-5.2-02 — Loans with Resale Restrictions: Eligibility, Collateral and Delivery Requirements (PDF p.795)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G299 — O-FNM-56981 [O-FNM]
- **Q:** Were all Loans with Resale Restrictions requirements met?
- **Defect condition:** Fannie Mae does not have first claim to insurance settlements and condemnation proceeds
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3737
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-5.2-01 — Loans With Resale Restrictions: General Information (PDF p.793)
- **Guide candidate:** B5-5.2-02 — Loans with Resale Restrictions: Eligibility, Collateral and Delivery Requirements (PDF p.795)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **SME:** [ ] agree [ ] correct: ______

### G300 — O-FRD-52268 [O-FRD]
- **Q:** Were all Loans with Resale Restrictions requirements met?
- **Defect condition:** Financial obligation req's not met &/or not subordinate to first mtg subject to resale restrictions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3730
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G301 — O-FRD-52272 [O-FRD]
- **Q:** Were all Loans with Resale Restrictions requirements met?
- **Defect condition:** LTV/TLTV/HTLTV incorrect per resale restrictions that survive or terminate foreclosure as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3731
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G303 — O-FRD-52267 [O-FRD]
- **Q:** Were all Loans with Resale Restrictions requirements met?
- **Defect condition:** Property subject to resale restrictions without any right of first refusal requirements being met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3732
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G304 — O-FNM-50327 [O-FNM]
- **Q:** Were all Loans with Resale Restrictions requirements met?
- **Defect condition:** Resale restrictions loan req's not met, including property type, amortization, &/or loan purpose
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3630
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** 3 named compliance dimensions: property type, amortization type (mismo_amortization_type already extracted), loan purpose (loan_purpose_1003/loan_purpose_cd already extracted)
- **Data needed:** a resale-restriction-program eligibility rule table (SME-defined) + a property-type field (not currently modeled)
- **Rationale:** 2 of the 3 named fields already exist in the extraction contract — a genuine near-term candidate once the resale-restriction program rules and property-type field are added; not claimed ready-to-build here because the actual per-restriction-type rule table isn't sourced anywhere in this row.
- **Guide candidate:** B5-5.2-01 — Loans With Resale Restrictions: General Information (PDF p.793)
- **Guide candidate:** B5-5.2-02 — Loans with Resale Restrictions: Eligibility, Collateral and Delivery Requirements (PDF p.795)
- **Guide candidate:** B4-2.3-04 — Loan Eligibility for Co-op Share Loans (PDF p.712)
- **SME:** [ ] agree [ ] correct: ______

### G305 — O-FRD-52270 [O-FRD]
- **Q:** Were all Loans with Resale Restrictions requirements met?
- **Defect condition:** Resale restrictions survive foreclosure/deed-in-lieu & comps do not have similar resale restrictions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3729
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G306 — O-FRD-52271 [O-FRD]
- **Q:** Were all Loans with Resale Restrictions requirements met?
- **Defect condition:** Resale restrictions terminate & appraisal value did not use comps that are not resale restricted
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3738
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'appraisal', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G307 — O-FNM-56980 [O-FNM]
- **Q:** Were all Loans with Resale Restrictions requirements met?
- **Defect condition:** Source/terms of the resale restrictions not in public land records identifiable in a title search
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3735
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-5.2-01 — Loans With Resale Restrictions: General Information (PDF p.793)
- **Guide candidate:** B5-5.2-02 — Loans with Resale Restrictions: Eligibility, Collateral and Delivery Requirements (PDF p.795)
- **Guide candidate:** A2-4.1-02 — Ownership and Retention of Loan Files and Records (PDF p.83)
- **SME:** [ ] agree [ ] correct: ______

### G308 — O-FRD-57382 [O-FRD]
- **Q:** Were all Loans with Resale Restrictions requirements met?
- **Defect condition:** Terms of the resale restrictions not in public land records discoverable by a routine title search
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3736
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G309 — O-FRD-52269 [O-FRD]
- **Q:** Were all Loans with Resale Restrictions requirements met?
- **Defect condition:** The Appraisal did not include comment on the resale restrictions &/or include an impact analysis
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3728
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'appraisal', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G310 — O-FNM-56353 [O-FNM]
- **Q:** Were all Loans with Resale Restrictions requirements met?
- **Defect condition:** The appraisal did not reflect the market value of the property without resale restrictions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3733
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'appraisal', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-5.2-01 — Loans With Resale Restrictions: General Information (PDF p.793)
- **Guide candidate:** B5-5.2-02 — Loans with Resale Restrictions: Eligibility, Collateral and Delivery Requirements (PDF p.795)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **SME:** [ ] agree [ ] correct: ______

### G311 — O-FNM-54189 [O-FNM]
- **Q:** Were all NY CEMA Agreement requirements met?
- **Defect condition:** NY CEMA missing Form 3172, Consolidation, Extension & Modification Agmt, &/or other req'd exhibits
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3601
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** A3-3-03 — Other Servicing Arrangements (PDF p.131)
- **Guide candidate:** B1-1-02 — Blanket Authorization Form (PDF p.170)
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **SME:** [ ] agree [ ] correct: ______

### G313 — O-RHS-56588 [O-RHS]
- **Q:** Were all Native American restricted land requirements met?_x000D_
- **Defect condition:** A copy of the tribe's lease for use on residential land is not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3584
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G314 — O-RHS-56585 [O-RHS]
- **Q:** Were all Native American restricted land requirements met?_x000D_
- **Defect condition:** Native American restricted land security interest was not approved by the Secretary of the Interior
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3588
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G315 — O-RHS-56584 [O-RHS]
- **Q:** Were all Native American restricted land requirements met?_x000D_
- **Defect condition:** Native American restricted trust or restricted land will not remain in trust or restricted status
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3589
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G316 — O-RHS-56586 [O-RHS]
- **Q:** Were all Native American restricted land requirements met?_x000D_
- **Defect condition:** No evidence the tribe has enacted legally binding and effective foreclosure/eviction procedures
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3840
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G317 — O-RHS-56587 [O-RHS]
- **Q:** Were all Native American restricted land requirements met?_x000D_
- **Defect condition:** No evidence the tribe has procedures ensuring the guaranteed loan will always have 1st lien priority
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3587
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G319 — O-RHS-56591 [O-RHS]
- **Q:** Were all Native American restricted land requirements met?_x000D_
- **Defect condition:** The leasehold estate does not constitute real property and/or is not insured by a title policy
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3585
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'title_commitment' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'title_commitment', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G320 — O-RHS-56590 [O-RHS]
- **Q:** Were all Native American restricted land requirements met?_x000D_
- **Defect condition:** The mortgage does not cover both property improvements and the leasehold interest in the land
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3583
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G321 — O-RHS-56589 [O-RHS]
- **Q:** Were all Native American restricted land requirements met?_x000D_
- **Defect condition:** The tribe's lease does not meet lease requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3586
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G322 — O-VA-51731 [O-VA]
- **Q:** Were all New Construction/Construction Permanent Home Loan requirements met?
- **Defect condition:** An escrow of funds for postponed completion of improvements not established as required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3599
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G323 — O-VA-50774 [O-VA]
- **Q:** Were all New Construction/Construction Permanent Home Loan requirements met?
- **Defect condition:** Constr/constr perm loan- Written approval from the borr prior to each draw pymt not evident
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3391
- **Severity:** Major
- **Classification method:** hand_verified
- **Machine checks:** draw-payment-approval-record presence
- **Data needed:** a construction-draw borrower-approval log (not in corpus)
- **Rationale:** Crisp doc-presence test, not a subjective call — 'not evident' names a specific missing record.
- **SME:** [ ] agree [ ] correct: ______

### G325 — O-VA-00485 [O-VA]
- **Q:** Were all New Construction/Construction Permanent Home Loan requirements met?
- **Defect condition:** Missing Vet acknowledgement that 1 yr builder warranty or 10 yr insured protection plan not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3865
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G326 — O-VA-00470 [O-VA]
- **Q:** Were all New Construction/Construction Permanent Home Loan requirements met?
- **Defect condition:** Missing no construction warranty where Veteran borr is general contractor building subject primary
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3300
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G327 — O-VA-00642 [O-VA]
- **Q:** Were all New Construction/Construction Permanent Home Loan requirements met?
- **Defect condition:** Missing satisfactory inspection for required completion, repairs, alterations or conditions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3441
- **Severity:** Critical
- **Classification method:** hand_verified
- **Data needed:** a distinct 'satisfactory completion inspection' document — NOT the appraisal itself
- **Rationale:** eval_class=doc_presence targets 'appraisal' only because the condition text happens to contain the word 'appraisal' ('The appraisal was made subject to completion... an inspection certifying the repairs have been satisfactorily completed was not in the file') — the actual missing document is the completion INSPECTION, a distinct doc family absent from every synthetic loan. Presence of an ordinary appraisal (which every loan has) would false-PASS this.
- **SME:** [ ] agree [ ] correct: ______

### G328 — O-VA-00480 [O-VA]
- **Q:** Were all New Construction/Construction Permanent Home Loan requirements met?
- **Defect condition:** Model home used to obtain value without stating the model home is the same plan type as the subject
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3582
- **Severity:** Major
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G329 — O-VA-00489 [O-VA]
- **Q:** Were all New Construction/Construction Permanent Home Loan requirements met?
- **Defect condition:** New construction missing exhibits including 1992 CABO Model Energy Code (MEC) as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3306
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** CABO Model Energy Code (MEC) exhibit presence
- **Data needed:** a named specific compliance document (1992 CABO MEC exhibit, not in corpus)
- **Rationale:** Crisp, specific-document presence check.
- **SME:** [ ] agree [ ] correct: ______

### G330 — O-VA-00792 [O-VA]
- **Q:** Were all New Construction/Construction Permanent Home Loan requirements met?
- **Defect condition:** VA LAPP new construction file did not document enrollment in a 10-year insured protection plan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3268
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '10-year'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G331 — O-VA-00481 [O-VA]
- **Q:** Were all New Construction/Construction Permanent Home Loan requirements met?
- **Defect condition:** VA construction compliance inspection req's not met per stage in proposed/under construction
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3402
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G332 — O-VA-51186 [O-VA]
- **Q:** Were all New Construction/Construction Permanent Home Loan requirements met?
- **Defect condition:** Veteran not given Form 26-1859, Warranty of Completion of Construction or 10 yr insurance warranty
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3594
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '1-year'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G334 — O-FRD-50360 [O-FRD]
- **Q:** Were all New York Consolidation, Extension and Modification Agreement (CEMA) requirements met?
- **Defect condition:** A Consolidated Note not in the file for a New York CEMA loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3323
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G335 — O-FRD-50359 [O-FRD]
- **Q:** Were all New York Consolidation, Extension and Modification Agreement (CEMA) requirements met?
- **Defect condition:** All required exhibits (A-D) not provided for New York CEMA
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3324
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G336 — O-FRD-52743 [O-FRD]
- **Q:** Were all New York Consolidation, Extension and Modification Agreement (CEMA) requirements met?
- **Defect condition:** NY CEMA consolidated note, original old & new money note was not a copy of the entire note
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3602
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G338 — O-FHA-50719 [O-FHA]
- **Q:** Were all Section 203(h) Mortgage Insurance for Disaster Victims eligibility requirements met?
- **Defect condition:** Sect 203(h)-Borr did not have a minimum credit score of 500 as required for the program
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3747
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G339 — O-FHA-50717 [O-FHA]
- **Q:** Were all Section 203(h) Mortgage Insurance for Disaster Victims eligibility requirements met?
- **Defect condition:** Sect 203(h)-Case# not assigned within 1 yr of the Presidentially-Declared Major Disaster Area-PDMDA
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3746
- **Severity:** Major
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'fhac_case_assignment' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'fhac_case_assignment', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G340 — O-FHA-50720 [O-FHA]
- **Q:** Were all Section 203(h) Mortgage Insurance for Disaster Victims eligibility requirements met?
- **Defect condition:** Sect 203(h)-No evidence prior home was PDMDA & damaged to req reconstruction/replacement
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3750
- **Severity:** Major
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G341 — O-FHA-50718 [O-FHA]
- **Q:** Were all Section 203(h) Mortgage Insurance for Disaster Victims eligibility requirements met?
- **Defect condition:** Sect 203(h)-The subject property is not the borrower’s principal residence
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3749
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G343 — O-FHA-50721 [O-FHA]
- **Q:** Were all Section 203(h) Mortgage Insurance for Disaster Victims underwriting requirements met?
- **Defect condition:** Sect 203(h)-All additional underwriting and eligibility requirements not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3748
- **Severity:** Major
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G346 — O-VA-50776 [O-VA]
- **Q:** Were all Supplemental Loan requirements met?
- **Defect condition:** Supplemental loan-improvements or repairs not for the purpose of improving basic livability/utility
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3832
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G349 — PrivateBank [GENERIC]
- **Q:** Were all Underwriter Guideline Variances (UGV) procedures met?
- **Defect condition:** Private Bank approved exceptions including all UGV
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3432
- **Severity:** Note
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B4-2.2-05 — FHA-Approved Condo Review Eligibility (PDF p.690)
- **Guide candidate:** B7-2-05 — Title Exceptions and Impediments (PDF p.867)
- **SME:** [ ] agree [ ] correct: ______

### G351 — UGVAPPRVL [GENERIC]
- **Q:** Were all Underwriter Guideline Variances (UGV) procedures met?
- **Defect condition:** Unable to locate approval by Portfolio Rep in Epic and/or Notepad
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3847
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** A1-1-01 — Application and Approval of Seller/Servicer (PDF p.20)
- **Guide candidate:** D1-3-02 — Lender Post-Closing Quality Control Review of Approval Conditions, Underwriting Decisions, Data, and Documentation (PDF p.1068)
- **SME:** [ ] agree [ ] correct: ______

### G352 — UGVLendAuth [GENERIC]
- **Q:** Were all Underwriter Guideline Variances (UGV) procedures met?
- **Defect condition:** Underwriter did not have proper lending authority & loan was not escalated to manager
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3850
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** A2-4.1-01 — Establishing Loan Files (PDF p.78)
- **SME:** [ ] agree [ ] correct: ______

### G353 — O-FNM-56091 [O-FNM]
- **Q:** Were all additional HomeReady requirements met?
- **Defect condition:** Borr did not contribute min of 5% from own funds in HomeReady 2-4 w/ lender-funded grant/LTV over 80
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3492
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '5%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** A2-3.1-01 — Lender Breach of Contract (PDF p.56)
- **Guide candidate:** B2-1.2-01 — Loan-to-Value (LTV) Ratios (PDF p.179)
- **Guide candidate:** B3-4.1-03 — Lender Incentives (PDF p.428)
- **SME:** [ ] agree [ ] correct: ______

### G354 — O-FNM-56234 [O-FNM]
- **Q:** Were all additional HomeReady requirements met?
- **Defect condition:** HomeReady loan with sweat equity exceeded the maximum LTV of 95%
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3499
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '95%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.2-01 — Loan-to-Value (LTV) Ratios (PDF p.179)
- **Guide candidate:** B2-1.2-03 — Home Equity Combined Loan-to-Value (HCLTV) Ratios (PDF p.182)
- **Guide candidate:** B3-4.3-13 — Sweat Equity (PDF p.457)
- **SME:** [ ] agree [ ] correct: ______

### G355 — O-FNM-56233 [O-FNM]
- **Q:** Were all additional HomeReady requirements met?
- **Defect condition:** HomeReady sweat equity exceeded 2% of the lesser of the purchase price/appraised value in a 2-4 unit
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3498
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '2%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.2-03 — Home Equity Combined Loan-to-Value (HCLTV) Ratios (PDF p.182)
- **Guide candidate:** B3-4.3-13 — Sweat Equity (PDF p.457)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **SME:** [ ] agree [ ] correct: ______

### G356 — O-FNM-57898 [O-FNM]
- **Q:** Were all additional HomeReady requirements met?
- **Defect condition:** LLPA applied & counseling not completed w/in 12 mos PTC & not submitted to DU &/or with SFC 184
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3496
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '12 months'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-2-06 — Homeownership Education and Housing Counseling (PDF p.253)
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B5-6-01 — HomeReady Mortgage Loan and Borrower Eligibility (PDF p.808)
- **SME:** [ ] agree [ ] correct: ______

### G357 — O-FNM-57456 [O-FNM]
- **Q:** Were all additional HomeReady requirements met?
- **Defect condition:** Loan closed with the temporary $2,500 LLPA credit & not delivered with the applicable 900 or 884 SFC
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3568
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '$2,500'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B3-5.1-02 — Determining the Credit Score for a Mortgage Loan (PDF p.474)
- **Guide candidate:** B5-6-01 — HomeReady Mortgage Loan and Borrower Eligibility (PDF p.808)
- **Guide candidate:** B5-6-03 — HomeReady Mortgage Loan Pricing, Mortgage Insurance, and Special Feature Codes (PDF p.818)
- **SME:** [ ] agree [ ] correct: ______

### G359 — O-FNM-56235 [O-FNM]
- **Q:** Were all additional HomeReady requirements met?
- **Defect condition:** The HomeReady contributory value of the sweat equity was calculated incorrectly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3501
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.2-03 — Home Equity Combined Loan-to-Value (HCLTV) Ratios (PDF p.182)
- **Guide candidate:** B3-4.3-13 — Sweat Equity (PDF p.457)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **SME:** [ ] agree [ ] correct: ______

### G360 — O-FNM-56236 [O-FNM]
- **Q:** Were all additional HomeReady requirements met?
- **Defect condition:** The file did not contain the HomeReady sweat equity program provider log
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3502
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B3-4.3-13 — Sweat Equity (PDF p.457)
- **Guide candidate:** B2-1.2-03 — Home Equity Combined Loan-to-Value (HCLTV) Ratios (PDF p.182)
- **Guide candidate:** B3-3.4-14 — Section 8 Housing Choice Voucher Homeownership Program Payments (PDF p.370)
- **SME:** [ ] agree [ ] correct: ______

### G361 — O-FNM-57454 [O-FNM]
- **Q:** Were all additional HomeReady requirements met?
- **Defect condition:** The temporary $2,500 LLPA credit was given in a loan that was not an eligible HomeReady purchase
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3567
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '$2,500'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B3-5.1-02 — Determining the Credit Score for a Mortgage Loan (PDF p.474)
- **Guide candidate:** B5-6-01 — HomeReady Mortgage Loan and Borrower Eligibility (PDF p.808)
- **Guide candidate:** B5-6-03 — HomeReady Mortgage Loan Pricing, Mortgage Insurance, and Special Feature Codes (PDF p.818)
- **SME:** [ ] agree [ ] correct: ______

### G362 — O-FNM-57455 [O-FNM]
- **Q:** Were all additional HomeReady requirements met?
- **Defect condition:** The temporary $2,500 LLPA credit was not provided directly to the borrower through the transaction
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3566
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '$2,500'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-6-01 — HomeReady Mortgage Loan and Borrower Eligibility (PDF p.808)
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G363 — O-FNM-55518 [O-FNM]
- **Q:** Were all additional HomeStyle Renovation mortgage requirements met?
- **Defect condition:** HomeStyle loan agreement not executed by the lender & borr at closing on the same date as the note
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3512
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** HomeStyle-loan-agreement-execution-date == note-date match
- **Data needed:** a HomeStyle loan agreement doc + execution date field (not in corpus)
- **Rationale:** Crisp date-match test once the document exists.
- **Guide candidate:** B5-3.2-06 — HomeStyle Renovation: Renovation Contract, Renovation Loan Agreement, and Lien Waiver (PDF p.757)
- **Guide candidate:** B5-3.2-02 — HomeStyle Renovation Mortgages: Loan and Borrower Eligibility (PDF p.747)
- **Guide candidate:** B8-5-03 — HomeStyle Renovation Mortgage Documentation Requirements (PDF p.924)
- **SME:** [ ] agree [ ] correct: ______

### G364 — O-FNM-55517 [O-FNM]
- **Q:** Were all additional HomeStyle Renovation mortgage requirements met?
- **Defect condition:** HomeStyle reno loan agreement not in the file or does not include all req'd elements/provisions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3511
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-3.2-06 — HomeStyle Renovation: Renovation Contract, Renovation Loan Agreement, and Lien Waiver (PDF p.757)
- **Guide candidate:** B5-3.2-02 — HomeStyle Renovation Mortgages: Loan and Borrower Eligibility (PDF p.747)
- **Guide candidate:** B8-5-03 — HomeStyle Renovation Mortgage Documentation Requirements (PDF p.924)
- **SME:** [ ] agree [ ] correct: ______

### G366 — O-FNM-58738 [O-FNM]
- **Q:** Were all additional HomeStyle Renovation mortgage requirements met?
- **Defect condition:** Renovation contract was not fully executed by both the contractor & the borrower prior to closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3435
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** renovation-contract dual-signature + pre-closing-date check
- **Data needed:** a renovation contract doc type (not in corpus)
- **Rationale:** Crisp signature/date test, not a subjective call.
- **Guide candidate:** B5-3.2-02 — HomeStyle Renovation Mortgages: Loan and Borrower Eligibility (PDF p.747)
- **Guide candidate:** B5-3.2-06 — HomeStyle Renovation: Renovation Contract, Renovation Loan Agreement, and Lien Waiver (PDF p.757)
- **Guide candidate:** B8-5-03 — HomeStyle Renovation Mortgage Documentation Requirements (PDF p.924)
- **SME:** [ ] agree [ ] correct: ______

### G367 — O-FRD-52264 [O-FRD]
- **Q:** Were all additional Loans with Resale Restrictions requirements met?
- **Defect condition:** Min down payment req's not met based on resale-restricted price for income-based resale restrictions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3525
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G368 — O-BP-55673 [O-FRD]
- **Q:** Were all additional Loans with Resale Restrictions requirements met?
- **Defect condition:** Model Declaration not used as best practice for the subject income-based resale restricted property
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3581
- **Severity:** Minor
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G370 — O-FRD-52262 [O-FRD]
- **Q:** Were all additional Loans with Resale Restrictions requirements met?
- **Defect condition:** Property type & occupancy requirements not met when subject to income-based resale restrictions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3527
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G371 — O-FRD-52266 [O-FRD]
- **Q:** Were all additional Loans with Resale Restrictions requirements met?
- **Defect condition:** Resale restriction controls not administered by subsidy provider or program administrator as req'd
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3524
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G372 — O-FRD-52263 [O-FRD]
- **Q:** Were all additional Loans with Resale Restrictions requirements met?
- **Defect condition:** The product is ineligible for a property is subject to income-based resale restrictions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3526
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G373 — O-VA-55508 [O-VA]
- **Q:** Were all additional New Construction/Construction Permanent Home Loan requirements met?
- **Defect condition:** All construction exhibits including the survey/plot plan, plans & specs & elevations not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3385
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G374 — O-VA-58001 [O-VA]
- **Q:** Were all additional New Construction/Construction Permanent Home Loan requirements met?
- **Defect condition:** Appraisal wasn't ordered before the completion of the foundation in a one-time construction loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3603
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'appraisal', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G375 — O-VA-58005 [O-VA]
- **Q:** Were all additional New Construction/Construction Permanent Home Loan requirements met?
- **Defect condition:** Documentation not in file supporting acquisition costs included in a 1-time/2-time construction loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3604
- **Severity:** Major
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G376 — O-VA-57999 [O-VA]
- **Q:** Were all additional New Construction/Construction Permanent Home Loan requirements met?
- **Defect condition:** Subject loan is a conversion to another loan type from a VA one-time or two-time construction loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3856
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G377 — O-VA-58003 [O-VA]
- **Q:** Were all additional New Construction/Construction Permanent Home Loan requirements met?
- **Defect condition:** The appraisal was not ordered with the applicable loan use and/or building status
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3280, 3281
- **Severity:** Major
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'appraisal', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G378 — O-VA-58002 [O-VA]
- **Q:** Were all additional New Construction/Construction Permanent Home Loan requirements met?
- **Defect condition:** The appraisal wasn't ordered upon 100% completion of the subject two-time construction loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3842
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '100%'
- **Data needed:** a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'appraisal', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G379 — O-VA-58004 [O-VA]
- **Q:** Were all additional New Construction/Construction Permanent Home Loan requirements met?
- **Defect condition:** The maximum loan amount for the construction one-time or two-time was not calculated correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3389
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G380 — O-VA-58000 [O-VA]
- **Q:** Were all additional New Construction/Construction Permanent Home Loan requirements met?
- **Defect condition:** Veteran chose their own builder & a VA Builder ID was not obtained prior to the issuance of the NOV
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3302
- **Severity:** Major
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'va_nov' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'va_nov', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G382 — O-RHS-50595 [O-RHS]
- **Q:** Were all additional combination construction to permanent (single-close) loan requirements met?
- **Defect condition:** A draw and disbursement ledger was not in the file if applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3424
- **Severity:** Major
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G383 — O-RHS-51849 [O-RHS]
- **Q:** Were all additional combination construction to permanent (single-close) loan requirements met?
- **Defect condition:** A rehab and repair feature without documenting the home has been complete for 12 months or more
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3724
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '12 months'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G384 — O-RHS-50597 [O-RHS]
- **Q:** Were all additional combination construction to permanent (single-close) loan requirements met?
- **Defect condition:** Excess construction proceeds given as cash back and not applied as a principal reduction
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3571
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G385 — O-RHS-02706 [O-RHS]
- **Q:** Were all additional combination construction to permanent (single-close) loan requirements met?
- **Defect condition:** File did not validate construction cost: contracts, loan agreement, plans, receipts, invoices, etc.
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3786
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** construction-cost-documentation-bundle presence (named families: purchase contract, Construction Loan Agreement, plans, receipts, invoices, lien waivers)
- **Data needed:** the named construction-cost document family (none in corpus)
- **Rationale:** Row says 'for example' but DOES name concrete document families, unlike the truly bare catch-alls classified RED elsewhere in this block — crisp presence-bundle check once documents exist.
- **SME:** [ ] agree [ ] correct: ______

### G386 — O-RHS-02708 [O-RHS]
- **Q:** Were all additional combination construction to permanent (single-close) loan requirements met?
- **Defect condition:** No, the guarantee fee was not collected prior to submission of request for guarantee
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3739
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** guarantee-fee-collection-date vs guarantee-request-date order check
- **Data needed:** USDA guarantee-fee collection-date fields (not in corpus — loan 05 doesn't carry this specific fact)
- **Rationale:** Crisp date-order test, not a subjective call.
- **SME:** [ ] agree [ ] correct: ______

### G387 — O-RHS-52818 [O-RHS]
- **Q:** Were all additional combination construction to permanent (single-close) loan requirements met?
- **Defect condition:** Not all of the loan costs were eligible in a rehabilitation & repair loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3425
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G388 — O-RHS-02707 [O-RHS]
- **Q:** Were all additional combination construction to permanent (single-close) loan requirements met?
- **Defect condition:** Single-close credit document(s) exceed age requirements as of the actual/scheduled closing date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3277
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '120 days'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G389 — O-RHS-59184 [O-RHS]
- **Q:** Were all additional combination construction to permanent (single-close) loan requirements met?
- **Defect condition:** Structural repairs over $75,000 did not meet habitable timeline for PITI reserves w/o an extension
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3725
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '$75,000'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G390 — O-RHS-51848 [O-RHS]
- **Q:** Were all additional combination construction to permanent (single-close) loan requirements met?
- **Defect condition:** Subject included rehab & repair feature w/ financed amt for non-structural repairs exceeding $75,000
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3721
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '$75,000'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G391 — O-RHS-59185 [O-RHS]
- **Q:** Were all additional combination construction to permanent (single-close) loan requirements met?
- **Defect condition:** Subject not habitable w/in 30 days of closing w/ a rehab & repair feature for non-structural repairs
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3722
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '30 days'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G392 — O-RHS-50599 [O-RHS]
- **Q:** Were all additional combination construction to permanent (single-close) loan requirements met?
- **Defect condition:** The file did not contain the closing statement and/or it was incorrect
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3353
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G394 — SONYMA Comm Space [GENERIC]
- **Q:** Were all additional project eligibility requirements met for the condo/coop SONYMA project (e.g., commercial space requirements, owner occupancy, litigation, for a co-op share price information, etc.)?
- **Defect condition:** Commercial space exceeds max 20% square footage
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3815
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '20%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B4-2.1-01 — General Information on Project Standards (PDF p.638)
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **SME:** [ ] agree [ ] correct: ______

### G395 — SONYMA HDFC [GENERIC]
- **Q:** Were all additional project eligibility requirements met for the condo/coop SONYMA project (e.g., commercial space requirements, owner occupancy, litigation, for a co-op share price information, etc.)?
- **Defect condition:** Financial statements not obtained for the past 2 years with HDFC approval
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3808
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '2 years'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** A4-1-02 — Submission of Financial Statements and Reports (PDF p.158)
- **Guide candidate:** B4-2.1-01 — General Information on Project Standards (PDF p.638)
- **SME:** [ ] agree [ ] correct: ______

### G396 — SONYMA Flip [GENERIC]
- **Q:** Were all additional project eligibility requirements met for the condo/coop SONYMA project (e.g., commercial space requirements, owner occupancy, litigation, for a co-op share price information, etc.)?
- **Defect condition:** Flip tax exceeds 5% of the appraised value
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3805
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '5%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B3-3.6-01 — General Information on Analyzing Individual Tax Returns (PDF p.390)
- **Guide candidate:** B4-2.1-01 — General Information on Project Standards (PDF p.638)
- **SME:** [ ] agree [ ] correct: ______

### G397 — SONYMA Ground [GENERIC]
- **Q:** Were all additional project eligibility requirements met for the condo/coop SONYMA project (e.g., commercial space requirements, owner occupancy, litigation, for a co-op share price information, etc.)?
- **Defect condition:** Ground lease term expires prior to the 35 year requirement from loan closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3807
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '35 year'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B4-2.3-04 — Loan Eligibility for Co-op Share Loans (PDF p.712)
- **Guide candidate:** B2-1.5-02 — Loan Eligibility (PDF p.225)
- **SME:** [ ] agree [ ] correct: ______

### G398 — SONYMA Units [GENERIC]
- **Q:** Were all additional project eligibility requirements met for the condo/coop SONYMA project (e.g., commercial space requirements, owner occupancy, litigation, for a co-op share price information, etc.)?
- **Defect condition:** Insider Units to existing tenants are ineligible for SONYMA
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3809
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B4-2.1-01 — General Information on Project Standards (PDF p.638)
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **SME:** [ ] agree [ ] correct: ______

### G399 — SONYMA Eviction [GENERIC]
- **Q:** Were all additional project eligibility requirements met for the condo/coop SONYMA project (e.g., commercial space requirements, owner occupancy, litigation, for a co-op share price information, etc.)?
- **Defect condition:** New conversion eviction plans are not eligible
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3804
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B4-2.1-01 — General Information on Project Standards (PDF p.638)
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **SME:** [ ] agree [ ] correct: ______

### G400 — SONYMA Cap Repair [GENERIC]
- **Q:** Were all additional project eligibility requirements met for the condo/coop SONYMA project (e.g., commercial space requirements, owner occupancy, litigation, for a co-op share price information, etc.)?
- **Defect condition:** No reserve limit found for a project with capital repairs
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3814
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B4-2.1-01 — General Information on Project Standards (PDF p.638)
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **SME:** [ ] agree [ ] correct: ______

### G401 — SONYMA Sq Feet [GENERIC]
- **Q:** Were all additional project eligibility requirements met for the condo/coop SONYMA project (e.g., commercial space requirements, owner occupancy, litigation, for a co-op share price information, etc.)?
- **Defect condition:** Project exceeds the minimum 500 square footage
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3806
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B4-2.1-01 — General Information on Project Standards (PDF p.638)
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **SME:** [ ] agree [ ] correct: ______

### G402 — SONYMA Company [GENERIC]
- **Q:** Were all additional project eligibility requirements met for the condo/coop SONYMA project (e.g., commercial space requirements, owner occupancy, litigation, for a co-op share price information, etc.)?
- **Defect condition:** Project is self managed and does not meet investor requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3812
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B4-2.1-01 — General Information on Project Standards (PDF p.638)
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **SME:** [ ] agree [ ] correct: ______

### G403 — SONYMA Lease [GENERIC]
- **Q:** Were all additional project eligibility requirements met for the condo/coop SONYMA project (e.g., commercial space requirements, owner occupancy, litigation, for a co-op share price information, etc.)?
- **Defect condition:** Prop Lease/Occup agreement does not have remaining term at least = the term of the loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3810
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B4-2.3-04 — Loan Eligibility for Co-op Share Loans (PDF p.712)
- **Guide candidate:** B2-1.5-02 — Loan Eligibility (PDF p.225)
- **SME:** [ ] agree [ ] correct: ______

### G404 — SONYMA Tax [GENERIC]
- **Q:** Were all additional project eligibility requirements met for the condo/coop SONYMA project (e.g., commercial space requirements, owner occupancy, litigation, for a co-op share price information, etc.)?
- **Defect condition:** Tax abatement ( if applicable ) not obtained and/or expiration date is not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3816
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B3-3.6-01 — General Information on Analyzing Individual Tax Returns (PDF p.390)
- **Guide candidate:** B4-2.1-01 — General Information on Project Standards (PDF p.638)
- **SME:** [ ] agree [ ] correct: ______

### G405 — SONYMA Ln Term [GENERIC]
- **Q:** Were all additional project eligibility requirements met for the condo/coop SONYMA project (e.g., commercial space requirements, owner occupancy, litigation, for a co-op share price information, etc.)?
- **Defect condition:** Terms of Underlying Mtg not provided and/or does not have at least 3 year remaining on term
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3817
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '3 year'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B4-2.1-01 — General Information on Project Standards (PDF p.638)
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **SME:** [ ] agree [ ] correct: ______

### G406 — SONYMA Maint Pmts [GENERIC]
- **Q:** Were all additional project eligibility requirements met for the condo/coop SONYMA project (e.g., commercial space requirements, owner occupancy, litigation, for a co-op share price information, etc.)?
- **Defect condition:** The owners maintenance payments exceeds the 15% maximum
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3811
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '15%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B3-3.4-02 — Alimony, Child Support, Equalization Payments, or Separate Maintenance (PDF p.352)
- **Guide candidate:** B4-2.1-01 — General Information on Project Standards (PDF p.638)
- **SME:** [ ] agree [ ] correct: ______

### G407 — SONYMA Pro Rata [GENERIC]
- **Q:** Were all additional project eligibility requirements met for the condo/coop SONYMA project (e.g., commercial space requirements, owner occupancy, litigation, for a co-op share price information, etc.)?
- **Defect condition:** The pro rata underlying mtg exceeds 35% of the lower of sales price or appraised value
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3813
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '35%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B4-2.1-01 — General Information on Project Standards (PDF p.638)
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **SME:** [ ] agree [ ] correct: ______

### G408 — SONYMA Min Units [GENERIC]
- **Q:** Were all additional project eligibility requirements met for the condo/coop SONYMA project (e.g., commercial space requirements, owner occupancy, litigation, for a co-op share price information, etc.)?
- **Defect condition:** The project exceeds the 10 Unit minimum
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3818
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B4-2.1-01 — General Information on Project Standards (PDF p.638)
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **SME:** [ ] agree [ ] correct: ______

### G410 — O-FNM-55603 [O-FNM]
- **Q:** Were all additional single closing conversion of construction-to-permanent financing requirements met?
- **Defect condition:** Appraisal effective date is over 4 mos old from the note date of the single-close construction perm
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3778
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'appraisal', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-3.1-02 — Conversion of Construction-to-Permanent Financing: Single-Closing Transactions (PDF p.736)
- **Guide candidate:** B5-3.1-03 — Conversion of Construction-to-Permanent Financing: Two-Closing Transactions (PDF p.743)
- **Guide candidate:** B5-3.1-01 — Conversion of Construction-to-Permanent Financing: Overview (PDF p.735)
- **SME:** [ ] agree [ ] correct: ______

### G412 — O-FNM-55408 [O-FNM]
- **Q:** Were all additional single closing conversion of construction-to-permanent financing requirements met?
- **Defect condition:** Single close construction perm did not use construction rider/modification agmt for perm conversion
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3789
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-3.1-02 — Conversion of Construction-to-Permanent Financing: Single-Closing Transactions (PDF p.736)
- **Guide candidate:** B5-3.1-03 — Conversion of Construction-to-Permanent Financing: Two-Closing Transactions (PDF p.743)
- **Guide candidate:** B5-3.1-01 — Conversion of Construction-to-Permanent Financing: Overview (PDF p.735)
- **SME:** [ ] agree [ ] correct: ______

### G413 — O-FNM-55605 [O-FNM]
- **Q:** Were all additional single closing conversion of construction-to-permanent financing requirements met?
- **Defect condition:** Single-close construction perm Form 1004D indicates decline & new appraisal not obtained/requalified
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3783
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** Form 1004D decline-status + re-qualification-appraisal presence
- **Data needed:** Form 1004D fields (not in corpus — same family as G415)
- **Rationale:** Crisp doc-content + presence test.
- **Guide candidate:** B5-3.1-02 — Conversion of Construction-to-Permanent Financing: Single-Closing Transactions (PDF p.736)
- **Guide candidate:** B5-3.1-03 — Conversion of Construction-to-Permanent Financing: Two-Closing Transactions (PDF p.743)
- **Guide candidate:** B5-3.1-01 — Conversion of Construction-to-Permanent Financing: Overview (PDF p.735)
- **SME:** [ ] agree [ ] correct: ______

### G414 — O-FNM-55407 [O-FNM]
- **Q:** Were all additional single closing conversion of construction-to-permanent financing requirements met?
- **Defect condition:** Single-close construction perm credit docs over 4 months but under 12 months without all cond's met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3774
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '4 months'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-3.1-02 — Conversion of Construction-to-Permanent Financing: Single-Closing Transactions (PDF p.736)
- **Guide candidate:** B5-3.1-03 — Conversion of Construction-to-Permanent Financing: Two-Closing Transactions (PDF p.743)
- **Guide candidate:** B5-3.1-01 — Conversion of Construction-to-Permanent Financing: Overview (PDF p.735)
- **SME:** [ ] agree [ ] correct: ______

### G415 — O-FNM-55604 [O-FNM]
- **Q:** Were all additional single closing conversion of construction-to-permanent financing requirements met?
- **Defect condition:** Single-close construction perm missing completed Form 1004D is not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3781
- **Severity:** Critical
- **Classification method:** hand_verified
- **Data needed:** Form 1004D (Appraisal Update/Completion Report) as its own field/doc-subtype — not the base appraisal doc
- **Rationale:** Same generic-'appraisal'-keyword false-positive as G327: the condition needs a completed Form 1004D specifically, a sub-document type this pilot doesn't distinguish from a plain appraisal.
- **Guide candidate:** B5-3.1-02 — Conversion of Construction-to-Permanent Financing: Single-Closing Transactions (PDF p.736)
- **Guide candidate:** B5-3.1-03 — Conversion of Construction-to-Permanent Financing: Two-Closing Transactions (PDF p.743)
- **Guide candidate:** B5-3.1-01 — Conversion of Construction-to-Permanent Financing: Overview (PDF p.735)
- **SME:** [ ] agree [ ] correct: ______

### G416 — O-VA-51084 [O-VA]
- **Q:** Were all cash-out refinance requirements met?
- **Defect condition:** C/O refi max ln amt incl funding fee &/or energy eff improv up to $6k over 100% of reasonable value
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3845
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** cash-out-refi loan-amount vs 100%-of-reasonable-value + $6k energy-improvement allowance
- **Data needed:** VA 'reasonable value' (the NOV's appraised-value amount) as its own field — va_nov doc exists in the corpus (loan 03) and nov_issue_date is already extracted, but the value amount itself is not yet a field — same VA-reasonable-value gap flagged in the asset-verification triage's G009/G010/G016
- **Rationale:** 'Reasonable value' is VA's defined term of art (the NOV amount), not a subjective judgment — crisp % math once the field exists.
- **SME:** [ ] agree [ ] correct: ______

### G417 — O-VA-58595 [O-VA]
- **Q:** Were all cash-out refinance requirements met?
- **Defect condition:** Cash-out refi not secured by first lien position on the property without a subordination agreement
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3316
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G418 — O-VA-51759 [O-VA]
- **Q:** Were all cash-out refinance requirements met?
- **Defect condition:** Initial and final cash-out Loan Comparison Disclosure was not provided or was not timely
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3569
- **Severity:** Critical
- **Classification method:** hand_verified
- **Data needed:** a VA Loan Comparison Disclosure doc type — NOT the final 1003
- **Rationale:** eval_class=doc_presence targets final_1003 because amq_compiler.py's DOC_KEYWORDS maps the phrase 'initial application' to final_1003 as a same-file shortcut — this is the EXACT latent bug decision 014 already flagged (application-verification groups 35/39/40) recurring here. The condition needs a VA cash-out-refi-specific Loan Comparison Disclosure, a document this pilot doesn't have at all; every loan already has a final 1003, so this would false-PASS on every VA cash-out loan.
- **SME:** [ ] agree [ ] correct: ______

### G419 — O-VA-58593 [O-VA]
- **Q:** Were all cash-out refinance requirements met?
- **Defect condition:** Interest rate reduction req not met in VA-VA Type I refi as per the orig rate type & new rate type
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3860
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G420 — O-VA-58592 [O-VA]
- **Q:** Were all cash-out refinance requirements met?
- **Defect condition:** LTV exceeds 90% of reasonable value in Type I refi of a fixed to ARM & over 1 discount point charged
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3844
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** LTV vs 90%-of-reasonable-value + discount-point-count gate (Type I fixed-to-ARM refi)
- **Data needed:** same VA reasonable-value field gap as G416
- **Rationale:** Same family as G416 — a second variant of the same crisp, term-of-art comparison.
- **SME:** [ ] agree [ ] correct: ______

### G421 — O-VA-51085 [O-VA]
- **Q:** Were all cash-out refinance requirements met?
- **Defect condition:** LTV in a refinance transaction including the financed funding fee if applicable exceeded 100%
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3648
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '100%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G423 — O-VA-51762 [O-VA]
- **Q:** Were all cash-out refinance requirements met?
- **Defect condition:** The fee recoupment was miscalculated in a VA-to-VA TYPE I cash-out refinance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3858
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G424 — O-VA-51763 [O-VA]
- **Q:** Were all cash-out refinance requirements met?
- **Defect condition:** The recoupment period exceeds 36 months in a VA-to-VA TYPE I cash-out refinance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3859
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '36 months'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G425 — O-VA-50960 [O-VA]
- **Q:** Were all cash-out refinance requirements met?
- **Defect condition:** VA refinance seasoning requirement not met as applicable based on refi type and loan terms
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3650
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G426 — O-VA-50920 [O-VA]
- **Q:** Were all cash-out refinance requirements met?
- **Defect condition:** Veteran was not provided a net tangible benefit test (NTB) as required in a refinance transaction
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3590
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G427 — O-RHS-51847 [O-RHS]
- **Q:** Were all combination construction to permanent (single-close) loan requirements met?
- **Defect condition:** A single-close purchase was not coded as Construction Only in GUS/GLS
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3770
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G428 — O-RHS-02698 [O-RHS]
- **Q:** Were all combination construction to permanent (single-close) loan requirements met?
- **Defect condition:** Additional funds disbursed at closing not covering the land cost in a construction single-close mtg
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3775
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G429 — O-RHS-02704 [O-RHS]
- **Q:** Were all combination construction to permanent (single-close) loan requirements met?
- **Defect condition:** Construction Rider/Note Allonge or Construction Loan Agreement not included in a single-close mtg
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3787
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G430 — O-RHS-50596 [O-RHS]
- **Q:** Were all combination construction to permanent (single-close) loan requirements met?
- **Defect condition:** Construction month pymt not paid by borr or an established interest reserve
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3386
- **Severity:** Major
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G431 — O-RHS-57530 [O-RHS]
- **Q:** Were all combination construction to permanent (single-close) loan requirements met?
- **Defect condition:** Current rent excluded w/out verifying it won't have to be paid after the single-close construction
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3777
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'usda_ratio_waiver_doc' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'usda_ratio_waiver_doc', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G432 — O-RHS-02701 [O-RHS]
- **Q:** Were all combination construction to permanent (single-close) loan requirements met?
- **Defect condition:** Ineligible loan costs were included in the amount financed in a single-close mortgage
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3442
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G433 — O-RHS-52817 [O-RHS]
- **Q:** Were all combination construction to permanent (single-close) loan requirements met?
- **Defect condition:** Single-close did not include PITI of subject & pending sale primary & exclusion conditions not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3417
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G434 — O-RHS-02700 [O-RHS]
- **Q:** Were all combination construction to permanent (single-close) loan requirements met?
- **Defect condition:** Single-close mortgage, the construction contractor or builder did not meet RHS builder requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3380
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G435 — O-RHS-02699 [O-RHS]
- **Q:** Were all combination construction to permanent (single-close) loan requirements met?
- **Defect condition:** The file did not contain an acceptable executed construction contract in a single-close mortgage
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3776
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** executed-construction-contract presence
- **Data needed:** a construction contract doc type (not in corpus — same family as G385)
- **Rationale:** 'Acceptable' here means 'executed/signed' — crisp presence test, not a subjective quality call.
- **SME:** [ ] agree [ ] correct: ______

### G436 — O-RHS-51747 [O-RHS]
- **Q:** Were all combination construction to permanent (single-close) loan requirements met?
- **Defect condition:** The property type was ineligible for a combination construction and permanent loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3356
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G437 — O-RHS-59186 [O-RHS]
- **Q:** Were all combination construction to permanent (single-close) loan requirements met?
- **Defect condition:** The subject included a rehab and repair feature for a loan purpose that is prohibited
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3723
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G439 — O-FHA-55974 [O-FHA]
- **Q:** Were all construction to permanent (CP) eligibility requirements met?
- **Defect condition:** Borrowers written authorization not obtained for each draw prior to disbursement to the contractor
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3392
- **Severity:** Major
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G440 — O-FHA-50741 [O-FHA]
- **Q:** Were all construction to permanent (CP) eligibility requirements met?
- **Defect condition:** Constr-Perm-borr owned the land for over 6 months prior to case number assignment
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3394
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '6 months'
- **Data needed:** a field/fact on the existing 'fhac_case_assignment' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'fhac_case_assignment', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G441 — O-FHA-55975 [O-FHA]
- **Q:** Were all construction to permanent (CP) eligibility requirements met?
- **Defect condition:** Construction escrow account not closed & remaining funds not applied as a principal curtailment
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3393
- **Severity:** Major
- **Classification method:** hand_verified
- **Machine checks:** construction-escrow-closure + principal-curtailment-application check
- **Data needed:** construction-escrow-closure fields (not in corpus)
- **Rationale:** Crisp doc/field test, not a subjective call.
- **SME:** [ ] agree [ ] correct: ______

### G442 — O-FHA-55976 [O-FHA]
- **Q:** Were all construction to permanent (CP) eligibility requirements met?
- **Defect condition:** No title update after conversion evidencing property is free & clear of all liens other than the mtg
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3397
- **Severity:** Major
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G444 — O-FNM-55395 [O-FNM]
- **Q:** Were all conversion of construction-to-permanent (CP) mortgage loan financing requirements met?
- **Defect condition:** A CO or equivalent missing in construction perm unimproved lot and the construction of a residence
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3390
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-3.1-01 — Conversion of Construction-to-Permanent Financing: Overview (PDF p.735)
- **Guide candidate:** B5-3.1-02 — Conversion of Construction-to-Permanent Financing: Single-Closing Transactions (PDF p.736)
- **Guide candidate:** B5-3.1-03 — Conversion of Construction-to-Permanent Financing: Two-Closing Transactions (PDF p.743)
- **SME:** [ ] agree [ ] correct: ______

### G445 — O-FNM-55396 [O-FNM]
- **Q:** Were all conversion of construction-to-permanent (CP) mortgage loan financing requirements met?
- **Defect condition:** Construction perm FNMA uniform mtg instruments not used or altered for construction reference
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3398
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-3.1-01 — Conversion of Construction-to-Permanent Financing: Overview (PDF p.735)
- **Guide candidate:** B5-3.1-02 — Conversion of Construction-to-Permanent Financing: Single-Closing Transactions (PDF p.736)
- **Guide candidate:** B5-3.1-03 — Conversion of Construction-to-Permanent Financing: Two-Closing Transactions (PDF p.743)
- **SME:** [ ] agree [ ] correct: ______

### G446 — O-FNM-55394 [O-FNM]
- **Q:** Were all conversion of construction-to-permanent (CP) mortgage loan financing requirements met?
- **Defect condition:** Construction perm work not completed & paid that could result in a mechanic's/materialmen’s lien
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3395
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** unpaid-contractor / lien-risk documentation presence
- **Data needed:** a lien-waiver/payment-completion doc type (not in corpus)
- **Rationale:** 'Could result in a lien' names a specific, checkable documentation gap (unpaid work), not itself a prediction the machine has to make — the file either has lien-waiver/payment evidence or it doesn't.
- **Guide candidate:** B5-3.1-01 — Conversion of Construction-to-Permanent Financing: Overview (PDF p.735)
- **Guide candidate:** B5-3.1-02 — Conversion of Construction-to-Permanent Financing: Single-Closing Transactions (PDF p.736)
- **Guide candidate:** B5-3.1-03 — Conversion of Construction-to-Permanent Financing: Two-Closing Transactions (PDF p.743)
- **SME:** [ ] agree [ ] correct: ______

### G447 — O-FNM-50918 [O-FNM]
- **Q:** Were all conversion of construction-to-permanent (CP) mortgage loan financing requirements met?
- **Defect condition:** Ineligible Conversion of Con-to-Perm Financing, lot not owned or acquired as part of transaction
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3403
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-3.1-01 — Conversion of Construction-to-Permanent Financing: Overview (PDF p.735)
- **Guide candidate:** B5-3.1-02 — Conversion of Construction-to-Permanent Financing: Single-Closing Transactions (PDF p.736)
- **Guide candidate:** B5-3.1-03 — Conversion of Construction-to-Permanent Financing: Two-Closing Transactions (PDF p.743)
- **SME:** [ ] agree [ ] correct: ______

### G449 — O-FNM-51736 [O-FNM]
- **Q:** Were all conversion of construction-to-permanent (CP) mortgage loan financing requirements met?
- **Defect condition:** The subject property type was ineligible for construction to permanent financing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3631
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-3.1-01 — Conversion of Construction-to-Permanent Financing: Overview (PDF p.735)
- **Guide candidate:** B5-3.1-02 — Conversion of Construction-to-Permanent Financing: Single-Closing Transactions (PDF p.736)
- **Guide candidate:** B5-3.1-03 — Conversion of Construction-to-Permanent Financing: Two-Closing Transactions (PDF p.743)
- **SME:** [ ] agree [ ] correct: ______

### G450 — O-FNM-55772 [O-FNM]
- **Q:** Were all conversion of construction-to-permanent (CP) mortgage loan financing requirements met?
- **Defect condition:** Two-closing construction perm w/ cost overruns not paid directly to the builder at closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3384
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-3.1-03 — Conversion of Construction-to-Permanent Financing: Two-Closing Transactions (PDF p.743)
- **Guide candidate:** B5-3.1-02 — Conversion of Construction-to-Permanent Financing: Single-Closing Transactions (PDF p.736)
- **Guide candidate:** B5-3.1-01 — Conversion of Construction-to-Permanent Financing: Overview (PDF p.735)
- **SME:** [ ] agree [ ] correct: ______

### G451 — O-FNM-50318 [O-FNM]
- **Q:** Were all high-balance mortgage loan requirements met?
- **Defect condition:** All requirements not met for high balance mtg and variance not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3458
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** high-balance-mortgage variance-approval presence
- **Stays human:** 'all requirements not met' (unstated residual)
- **Data needed:** a high-balance-mortgage variance-approval doc type (not in corpus)
- **Rationale:** Variance-doc-presence half is crisp; the catch-all clause stays human — same pattern as G145/G222.
- **Guide candidate:** B5-1-01 — High-Balance Mortgage Loan Eligibility and Underwriting (PDF p.715)
- **Guide candidate:** B5-1-02 — High-Balance Pricing, Mortgage Insurance, Special Feature Codes, and Delivery Limitations (PDF p.717)
- **Guide candidate:** B3-5.1-02 — Determining the Credit Score for a Mortgage Loan (PDF p.474)
- **SME:** [ ] agree [ ] correct: ______

### G453 — O-FHA-50739 [O-FHA]
- **Q:** Were all new construction completion requirements met?
- **Defect condition:** 1 comp from outside & inside the subdivision/project not provided for the subject in new subdivision
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3595
- **Severity:** Major
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G454 — O-FHA-51489 [O-FHA]
- **Q:** Were all new construction completion requirements met?
- **Defect condition:** Building On Own Land-file did not document source of borr paid options, itemization & cost per item
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3304
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** owner-builder-paid-options source-documentation + itemization presence
- **Data needed:** an owner-builder cost-itemization doc type (not in corpus)
- **Rationale:** 'Acceptable source' + itemization are named, specific documentation requirements, not open-ended judgment.
- **SME:** [ ] agree [ ] correct: ______

### G455 — O-FHA-51488 [O-FHA]
- **Q:** Were all new construction completion requirements met?
- **Defect condition:** Land purchase not documented with Closing Disclosure or similar legal doc for building on own land
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3387
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'closing_disclosure' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'closing_disclosure', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G456 — O-FHA-50740 [O-FHA]
- **Q:** Were all new construction completion requirements met?
- **Defect condition:** Lender did not certify on HUD-92800.5B, the property is 100% complete and meets HUD’s MPR and MPS
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3377
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '100%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G457 — O-FHA-50735 [O-FHA]
- **Q:** Were all new construction completion requirements met?
- **Defect condition:** New construction loan file did not contain form HUD-92544, Warranty of Completion of Construction
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3868
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G458 — O-FHA-50738 [O-FHA]
- **Q:** Were all new construction completion requirements met?
- **Defect condition:** Safety, structural soundness incl not limited to flood areas, airport hazards not addressed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3799
- **Severity:** Major
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G459 — O-FHA-51490 [O-FHA]
- **Q:** Were all new construction completion requirements met?
- **Defect condition:** The Construction maximum mortgage amount was not calculated correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3388
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G461 — O-FHA-52316 [O-FHA]
- **Q:** Were all new construction documentation requirements met?
- **Defect condition:** Construction 90% or more complete missing components to be installed/completed after appraisal
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3379
- **Severity:** Critical
- **Classification method:** hand_verified
- **Data needed:** a components-to-be-completed list attached to the appraisal for 90%+-complete new construction — not modeled as a distinct fact
- **Rationale:** Same generic-'appraisal'-keyword false positive as G327/G415 — the condition is specific to 90%-or-more-complete new construction, a gating fact this pilot doesn't track, and the missing list is not the appraisal document itself.
- **SME:** [ ] agree [ ] correct: ______

### G462 — O-FHA-52315 [O-FHA]
- **Q:** Were all new construction documentation requirements met?
- **Defect condition:** Construction less than 90% complete, floor plan, plot plan & size/finish exhibits not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3399
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '90%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G463 — O-FHA-50734 [O-FHA]
- **Q:** Were all new construction documentation requirements met?
- **Defect condition:** HUD-92541, Builder’s Certification of Plans, Specifications, and Site was not in the loan file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3303
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G464 — O-FHA-56222 [O-FHA]
- **Q:** Were all new construction documentation requirements met?
- **Defect condition:** HUD-NPMA-99-A is not in the file as required for all new construction
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3829
- **Severity:** Major
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G465 — O-FHA-53912 [O-FHA]
- **Q:** Were all new construction documentation requirements met?
- **Defect condition:** HUD-NPMA-99-B missing in new construction treated w/ termiticide, bait, field wood trtmt or barrier
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3593
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G466 — O-FHA-53910 [O-FHA]
- **Q:** Were all new construction documentation requirements met?
- **Defect condition:** ICC, RCI or CI not available & 2 inspections by a reg architect/structural engineer not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3837
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G467 — O-FHA-53911 [O-FHA]
- **Q:** Were all new construction documentation requirements met?
- **Defect condition:** Missing state/local certs of reg architect/engineer used due to lack of ICC certified RCI or CI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3838
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G468 — O-FHA-53908 [O-FHA]
- **Q:** Were all new construction documentation requirements met?
- **Defect condition:** New construction inspections not by ICC, RCI or CI or registered architect/structural engineer
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3592
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G469 — O-FHA-53909 [O-FHA]
- **Q:** Were all new construction documentation requirements met?
- **Defect condition:** New construction inspections not on form HUD-92051, CI Report or other state sanctioned form
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3591
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** HUD-92051 (or state-sanctioned equivalent) inspection-form presence
- **Data needed:** HUD-92051/Compliance Inspection Report doc type (not in corpus — same new-construction-inspection family as G327/G442)
- **Rationale:** Crisp, specific-form presence check.
- **SME:** [ ] agree [ ] correct: ______

### G470 — O-FHA-53913 [O-FHA]
- **Q:** Were all new construction documentation requirements met?
- **Defect condition:** Termiticide soil treatment applied only around the foundation perimeter post construction
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3627
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G472 — O-FHA-51487 [O-FHA]
- **Q:** Were all new construction eligibility requirements met?
- **Defect condition:** A licensed general contractor builder not hired to construct the dwelling for building on own land
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3305
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G473 — O-FHA-51280 [O-FHA]
- **Q:** Were all new construction eligibility requirements met?
- **Defect condition:** Exist less than 1 year w/out bldg permit & CO or final inspection by local authority, ICC RCI or CI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3436
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '1 year'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G474 — O-FHA-50733 [O-FHA]
- **Q:** Were all new construction eligibility requirements met?
- **Defect condition:** New construction- inspections/warranties as applicable per construction/property type not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3532
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G476 — O-FHA-51278 [O-FHA]
- **Q:** Were all new construction eligibility requirements met?
- **Defect condition:** Proposed construction-missing bldg permit & CO or footing, framing & final inspections by RCI or CI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3632
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G477 — O-FHA-51279 [O-FHA]
- **Q:** Were all new construction eligibility requirements met?
- **Defect condition:** Under construction-missing copies of the building permit and CO or final inspection by a RCI or CI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3853
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G478 — O-RHS-02891 [O-RHS]
- **Q:** Were all prohibited loan purpose requirements met?
- **Defect condition:** Income producing activity exceeds minimal &/or subject does not appear as predominantly residential
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3522
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G479 — O-RHS-02892 [O-RHS]
- **Q:** Were all prohibited loan purpose requirements met?
- **Defect condition:** No, total closing costs including lender fees exceed 3% of the total loan amount
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3572
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '3%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G481 — O-RHS-02886 [O-RHS]
- **Q:** Were all prohibited loan purpose requirements met?
- **Defect condition:** Seller or other interested party contributions exceed 6% of the loan amount
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3756
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '6%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G482 — O-RHS-02885 [O-RHS]
- **Q:** Were all prohibited loan purpose requirements met?
- **Defect condition:** The transaction did not meet the eligibility requirements for loan discount points
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3423
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G483 — O-RHS-55316 [O-RHS]
- **Q:** Were all purchase transaction documentation and/or ratio waiver requirements met?
- **Defect condition:** No supporting documentation of comp factors for debt ratio waiver in a purchase GUS refer/manual UW
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3638
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** compensating_factors_documented (already extracted from usda_ratio_waiver_doc, already populated False for loan 05)
- **Data needed:** loan_purpose_1003 Purchase gate on a new shape (see READY_TO_BUILD)
- **Rationale:** See READY_TO_BUILD — the fact this row needs is already extracted and correctly populated; only a new shape + a purpose-type gate (to avoid colliding with G491's refinance sibling) is missing.
- **READY TO BUILD:** PARTIAL — new shape, no new fixture: `compensating_factors_documented` (FACT_SPECS in extract_loan.py, extracted from usda_ratio_waiver_doc's 'Compensating Factors Documented ... NOT IN FILE' line) is ALREADY extracted and ALREADY correctly populated False for loan 05 — but is cited by ZERO existing SHACL shapes (RatioWaiverShape only cites piti_ratio/piti_guideline/dti_ratio/dti_guideline/usda_ratio_waiver_in_file, never this fact). G483's condition ('the eligible compensating factors supporting the use of the waiver was not supported with documentation' in a PURCHASE GUS-refer/manual-UW) matches this fact directly. Needs a NEW shape (not an extension of RatioWaiverShape, which tests a different clause), gated on loan_purpose_1003 containing 'Purchase' to avoid double-firing against G491's refinance-transaction sibling (same fact, opposite transaction-type gate) — verified the gating field (loan_purpose_1003) already exists before flagging this.
- **SME:** [ ] agree [ ] correct: ______

### G485 — O-RHS-02850 [O-RHS]
- **Q:** Were all purchase transaction documentation and/or ratio waiver requirements met?
- **Defect condition:** Ratio thresholds not met in GUS refer/manual UW of a purchase to be eligible for a debt ratio waiver
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3637
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** PITI/DTI ratio vs guideline comparison (piti_ratio/piti_guideline/dti_ratio/dti_guideline already extracted from usda_ratio_waiver_doc)
- **Data needed:** a purchase-vs-refi transaction-type gate on RatioWaiverShape (CHK-UND-002, currently ungated on transaction type) + confirmation this row's 'eligible for a waiver' test is the same as RatioWaiverShape's 'ratios exceed guideline' test, not a distinct waiver-eligibility-ceiling test
- **Rationale:** CONSIDERED for RatioWaiverShape, NOT wired: this row's exact guideline pair (never stated numerically here) can't be confirmed against RatioWaiverShape's generic ratio>guideline test without an SME confirming 'ratio thresholds not met to be ELIGIBLE for a waiver' is the same real-world condition as 'ratios exceed the guideline and no waiver is on file' rather than a distinct maximum-ratio-ceiling-for-waiver-eligibility test. See G487 for the closer, still-rejected candidate and the decision doc's REJECTED section.
- **SME:** [ ] agree [ ] correct: ______

### G486 — O-RHS-50598 [O-RHS]
- **Q:** Were all purchase transaction documentation and/or ratio waiver requirements met?
- **Defect condition:** Sales contract & all addenda not in the file, is incorrect or not signed by all parties
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3743
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G487 — O-RHS-50566 [O-RHS]
- **Q:** Were all purchase transaction documentation and/or ratio waiver requirements met?
- **Defect condition:** The approved debt ratio waiver is not in the file in a GUS refer/manual UW with ratios over 34/41
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3418
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** PITI/DTI ratio vs guideline comparison + waiver-in-file check (RatioWaiverShape's exact logic, on paper)
- **Data needed:** confirmation this row's stated '34/41' pair is what usda_ratio_waiver_doc's extracted guideline actually contains for the loans this row targets — loan 05 (this pilot's only RHS fixture) extracts 29/41, not 34/41
- **Rationale:** CONSIDERED and REJECTED as ready-to-build: textually the CLOSEST match to RatioWaiverShape (CHK-UND-002) of any row in this block — 'approved debt ratio waiver is not in the file... with ratios over 34/41' maps almost exactly onto piti_ratio>piti_guideline AND dti_ratio>dti_guideline AND usda_ratio_waiver_in_file==false. But the pilot's only RHS/USDA fixture (loan 05) is a PURCHASE with an extracted guideline of 29/41, not this row's stated 34/41 — meaning either a different transaction sub-type carries the 34/41 pair (RatioWaiverShape doesn't gate on transaction type at all today) or this row and G495 ('Refi ratios over 29/41... high repayment ratio exception') are actually the loan-05-relevant one under DIFFERENT AMQ terminology ('high repayment ratio exception' vs 'debt ratio waiver') — an unresolved terminology question an SME needs to settle before wiring ANY specific code here, exactly the kind of confident-sounding-but-unverified match decision 018 warns against.
- **SME:** [ ] agree [ ] correct: ______

### G488 — O-RHS-50927 [O-RHS]
- **Q:** Were all refinance transaction documentation and/or ratio waiver requirements met?
- **Defect condition:** A net tangible benefit was not provided as applicable in a Streamlined-assist Section 502 refinance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3753
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G489 — O-RHS-50923 [O-RHS]
- **Q:** Were all refinance transaction documentation and/or ratio waiver requirements met?
- **Defect condition:** All eligibility req's not met to qualify as a Section 502 refinance of a direct and guaranteed loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3751
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G490 — O-RHS-50924 [O-RHS]
- **Q:** Were all refinance transaction documentation and/or ratio waiver requirements met?
- **Defect condition:** Borr's from original loan, not deceased, was removed in a Section 502 Streamlined-assist refinance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3755
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G491 — O-RHS-02851 [O-RHS]
- **Q:** Were all refinance transaction documentation and/or ratio waiver requirements met?
- **Defect condition:** Comp factors to justify a debt ratio waiver not documented as required in a manual UW of a refinance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3647
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** compensating_factors_documented (already extracted, refi transaction-type variant of G483)
- **Data needed:** loan_purpose_1003 NOT-Purchase gate on a new shape (see READY_TO_BUILD)
- **Rationale:** See READY_TO_BUILD — refinance sibling of G483, same fact, opposite purpose gate.
- **READY TO BUILD:** PARTIAL, refinance sibling of G483 — same `compensating_factors_documented` fact, gated on loan_purpose_1003 NOT containing 'Purchase' instead. Two separate shapes (or one shape with a purpose branch) needed so the two AMQ exception codes (G483 purchase / G491 refinance) don't collide on the same underlying fact.
- **SME:** [ ] agree [ ] correct: ______

### G492 — O-RHS-58661 [O-RHS]
- **Q:** Were all refinance transaction documentation and/or ratio waiver requirements met?
- **Defect condition:** Existing USDA loan being refinanced has a 30 days or more delinquency within previous 180-day period
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3437
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '30 days'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G494 — O-RHS-50925 [O-RHS]
- **Q:** Were all refinance transaction documentation and/or ratio waiver requirements met?
- **Defect condition:** Pay history of loan being refinanced did not meet the req's as per refi type for Sect 502 refinance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3754
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'vom' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'vom', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G495 — O-RHS-50567 [O-RHS]
- **Q:** Were all refinance transaction documentation and/or ratio waiver requirements met?
- **Defect condition:** Refi ratios over 29/41, approved high repayment ratio exception not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3644
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '29/41'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G496 — O-RHS-50926 [O-RHS]
- **Q:** Were all refinance transaction documentation and/or ratio waiver requirements met?
- **Defect condition:** Sect 502 Streamline/Non-streamline refi with GUS Refer missing debt ratio waiver meeting guidelines
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3752
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'gus_findings' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'gus_findings', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G497 — O-RHS-56266 [O-RHS]
- **Q:** Were all refinance transaction documentation and/or ratio waiver requirements met?
- **Defect condition:** Streamlined-assist refi max income limit was exceeded due to not calculating annual income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3821
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G498 — O-FNM-56478 [O-FNM]
- **Q:** Were all shared equity transaction requirements met?
- **Defect condition:** FNMA doesn't have 1st claim to insurance settlements & condemnation proceeds in a shared equity loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3760
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.2-03 — Home Equity Combined Loan-to-Value (HCLTV) Ratios (PDF p.182)
- **Guide candidate:** B5-2-04 — Manufactured Housing Pricing, Mortgage Insurance, and Loan Delivery Requirements (PDF p.727)
- **Guide candidate:** B5-5.3-01 — Shared Equity Overview (PDF p.797)
- **SME:** [ ] agree [ ] correct: ______

### G500 — O-FNM-56472 [O-FNM]
- **Q:** Were all shared equity transaction requirements met?
- **Defect condition:** Private transfer fee doesn't qualify as a excepted transfer fee covenant under 12 C.F.R. § 1228.1(2)
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3762
- **Severity:** Major
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-5.3-01 — Shared Equity Overview (PDF p.797)
- **Guide candidate:** B5-5.3-02 — Shared Equity Transactions: General Requirements (PDF p.798)
- **Guide candidate:** B5-5.3-03 — Shared Equity Transactions: Eligibility, Underwriting and Collateral Requirements (PDF p.802)
- **SME:** [ ] agree [ ] correct: ______

### G501 — O-FNM-56480 [O-FNM]
- **Q:** Were all shared equity transaction requirements met?
- **Defect condition:** The borrower does not meet the specific eligibility criteria set up by the shared equity program
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3757
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-5.3-03 — Shared Equity Transactions: Eligibility, Underwriting and Collateral Requirements (PDF p.802)
- **Guide candidate:** B2-2-01 — General Borrower Eligibility Requirements (PDF p.241)
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **SME:** [ ] agree [ ] correct: ______

### G502 — O-FNM-56479 [O-FNM]
- **Q:** Were all shared equity transaction requirements met?
- **Defect condition:** The file did not evidence the required counseling for a shared equity loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3763
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.2-03 — Home Equity Combined Loan-to-Value (HCLTV) Ratios (PDF p.182)
- **Guide candidate:** B5-5.3-01 — Shared Equity Overview (PDF p.797)
- **Guide candidate:** B5-5.3-02 — Shared Equity Transactions: General Requirements (PDF p.798)
- **SME:** [ ] agree [ ] correct: ______

### G503 — O-FNM-56481 [O-FNM]
- **Q:** Were all shared equity transaction requirements met?
- **Defect condition:** The property, occupancy, or loan type is ineligible for a shared equity loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3764
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B2-1.2-03 — Home Equity Combined Loan-to-Value (HCLTV) Ratios (PDF p.182)
- **Guide candidate:** B5-5.3-01 — Shared Equity Overview (PDF p.797)
- **Guide candidate:** B5-5.3-02 — Shared Equity Transactions: General Requirements (PDF p.798)
- **SME:** [ ] agree [ ] correct: ______

### G504 — O-FNM-56474 [O-FNM]
- **Q:** Were all shared equity transaction requirements met?
- **Defect condition:** The shared equity community land trust did not meet the required legal documentation requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3758
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B4-1.4-06 — Community Land Trust Appraisal Requirements (PDF p.623)
- **Guide candidate:** B5-5.1-03 — Community Seconds: Shared Appreciation Transactions (PDF p.789)
- **Guide candidate:** B5-5.3-01 — Shared Equity Overview (PDF p.797)
- **SME:** [ ] agree [ ] correct: ______

### G505 — O-FNM-56476 [O-FNM]
- **Q:** Were all shared equity transaction requirements met?
- **Defect condition:** The shared equity community land trust is missing Form 2100 signed by the borrower
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3759
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B4-1.4-06 — Community Land Trust Appraisal Requirements (PDF p.623)
- **Guide candidate:** B5-5.1-03 — Community Seconds: Shared Appreciation Transactions (PDF p.789)
- **Guide candidate:** B5-5.3-01 — Shared Equity Overview (PDF p.797)
- **SME:** [ ] agree [ ] correct: ______

### G506 — O-FNM-56475 [O-FNM]
- **Q:** Were all shared equity transaction requirements met?
- **Defect condition:** The shared equity income & price restrictions did not meet required legal documentation req's
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3761
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B5-5.3-01 — Shared Equity Overview (PDF p.797)
- **Guide candidate:** B5-5.3-02 — Shared Equity Transactions: General Requirements (PDF p.798)
- **SME:** [ ] agree [ ] correct: ______

### G507 — O-FNM-56473 [O-FNM]
- **Q:** Were all shared equity transaction requirements met?
- **Defect condition:** The shared equity provider did not meet eligible provider requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3531
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-5.3-01 — Shared Equity Overview (PDF p.797)
- **Guide candidate:** B5-5.3-02 — Shared Equity Transactions: General Requirements (PDF p.798)
- **Guide candidate:** B5-5.3-03 — Shared Equity Transactions: Eligibility, Underwriting and Collateral Requirements (PDF p.802)
- **SME:** [ ] agree [ ] correct: ______

### G508 — O-FNM-55402 [O-FNM]
- **Q:** Were all single closing conversion of construction-to-permanent financing requirements met?
- **Defect condition:** Down payment requirements were not met for the subject single close construction perm purchase
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3780
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-3.1-02 — Conversion of Construction-to-Permanent Financing: Single-Closing Transactions (PDF p.736)
- **Guide candidate:** B5-3.1-03 — Conversion of Construction-to-Permanent Financing: Two-Closing Transactions (PDF p.743)
- **Guide candidate:** B5-3.1-01 — Conversion of Construction-to-Permanent Financing: Overview (PDF p.735)
- **SME:** [ ] agree [ ] correct: ______

### G509 — O-FNM-55400 [O-FNM]
- **Q:** Were all single closing conversion of construction-to-permanent financing requirements met?
- **Defect condition:** Interim funds not used to buy lot/finance construction in single close construction perm purchase
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3785
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-3.1-02 — Conversion of Construction-to-Permanent Financing: Single-Closing Transactions (PDF p.736)
- **Guide candidate:** B5-3.1-03 — Conversion of Construction-to-Permanent Financing: Two-Closing Transactions (PDF p.743)
- **Guide candidate:** B5-3.1-01 — Conversion of Construction-to-Permanent Financing: Overview (PDF p.735)
- **SME:** [ ] agree [ ] correct: ______

### G510 — O-FNM-55399 [O-FNM]
- **Q:** Were all single closing conversion of construction-to-permanent financing requirements met?
- **Defect condition:** Lot not owned by borr at 1st advance of interim financing in single close construction perm purchase
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3782
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-3.1-02 — Conversion of Construction-to-Permanent Financing: Single-Closing Transactions (PDF p.736)
- **Guide candidate:** B5-3.1-03 — Conversion of Construction-to-Permanent Financing: Two-Closing Transactions (PDF p.743)
- **Guide candidate:** B5-3.1-01 — Conversion of Construction-to-Permanent Financing: Overview (PDF p.735)
- **SME:** [ ] agree [ ] correct: ______

### G512 — O-FNM-55401 [O-FNM]
- **Q:** Were all single closing conversion of construction-to-permanent financing requirements met?
- **Defect condition:** Single-close construction perm LTV, CLTV, HCLTV not calculated correctly as per property/loan type
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3794
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-3.1-02 — Conversion of Construction-to-Permanent Financing: Single-Closing Transactions (PDF p.736)
- **Guide candidate:** B5-3.1-03 — Conversion of Construction-to-Permanent Financing: Two-Closing Transactions (PDF p.743)
- **Guide candidate:** B5-3.1-01 — Conversion of Construction-to-Permanent Financing: Overview (PDF p.735)
- **SME:** [ ] agree [ ] correct: ______

### G513 — O-FNM-55406 [O-FNM]
- **Q:** Were all single closing conversion of construction-to-permanent financing requirements met?
- **Defect condition:** Single-close construction perm credit docs older than 4 mos at conversion - permanent financing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3772
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '4 months'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-3.1-02 — Conversion of Construction-to-Permanent Financing: Single-Closing Transactions (PDF p.736)
- **Guide candidate:** B5-3.1-03 — Conversion of Construction-to-Permanent Financing: Two-Closing Transactions (PDF p.743)
- **Guide candidate:** B5-3.1-01 — Conversion of Construction-to-Permanent Financing: Overview (PDF p.735)
- **SME:** [ ] agree [ ] correct: ______

### G514 — O-FNM-55405 [O-FNM]
- **Q:** Were all single closing conversion of construction-to-permanent financing requirements met?
- **Defect condition:** Single-close construction perm not UW based on permanent financing terms or was modified & not re-UW
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3791
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-3.1-02 — Conversion of Construction-to-Permanent Financing: Single-Closing Transactions (PDF p.736)
- **Guide candidate:** B5-3.1-03 — Conversion of Construction-to-Permanent Financing: Two-Closing Transactions (PDF p.743)
- **Guide candidate:** B5-3.1-01 — Conversion of Construction-to-Permanent Financing: Overview (PDF p.735)
- **SME:** [ ] agree [ ] correct: ______

### G515 — O-FNM-55397 [O-FNM]
- **Q:** Were all single closing conversion of construction-to-permanent financing requirements met?
- **Defect condition:** Single-closing construction perm had a single period over 12 mos &/or total period exceeding 18 mos
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3396
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '12 months'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-3.1-02 — Conversion of Construction-to-Permanent Financing: Single-Closing Transactions (PDF p.736)
- **Guide candidate:** B5-3.1-03 — Conversion of Construction-to-Permanent Financing: Two-Closing Transactions (PDF p.743)
- **Guide candidate:** B5-3.1-01 — Conversion of Construction-to-Permanent Financing: Overview (PDF p.735)
- **SME:** [ ] agree [ ] correct: ______

### G516 — O-FNM-55398 [O-FNM]
- **Q:** Were all single closing conversion of construction-to-permanent financing requirements met?
- **Defect condition:** Single-closing construction perm loan term exceeded 30 years after conversion to permanent financing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3792
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '30 years'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-3.1-02 — Conversion of Construction-to-Permanent Financing: Single-Closing Transactions (PDF p.736)
- **Guide candidate:** B5-3.1-03 — Conversion of Construction-to-Permanent Financing: Two-Closing Transactions (PDF p.743)
- **Guide candidate:** B5-3.1-01 — Conversion of Construction-to-Permanent Financing: Overview (PDF p.735)
- **SME:** [ ] agree [ ] correct: ______

### G517 — O-FNM-55404 [O-FNM]
- **Q:** Were all single closing conversion of construction-to-permanent financing requirements met?
- **Defect condition:** The terms of the single-closing construction-to-permanent modified were ineligible for modification
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3796
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-3.1-02 — Conversion of Construction-to-Permanent Financing: Single-Closing Transactions (PDF p.736)
- **Guide candidate:** B5-3.1-03 — Conversion of Construction-to-Permanent Financing: Two-Closing Transactions (PDF p.743)
- **Guide candidate:** B5-3.1-01 — Conversion of Construction-to-Permanent Financing: Overview (PDF p.735)
- **SME:** [ ] agree [ ] correct: ______

### G518 — O-FNM-55403 [O-FNM]
- **Q:** Were all single closing conversion of construction-to-permanent financing requirements met?
- **Defect condition:** The terms of the single-closing construction-to-permanent were modified after the time of conversion
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3798
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-3.1-02 — Conversion of Construction-to-Permanent Financing: Single-Closing Transactions (PDF p.736)
- **Guide candidate:** B5-3.1-03 — Conversion of Construction-to-Permanent Financing: Two-Closing Transactions (PDF p.743)
- **Guide candidate:** B5-3.1-01 — Conversion of Construction-to-Permanent Financing: Overview (PDF p.735)
- **SME:** [ ] agree [ ] correct: ______

### G519 — O-FHA-50744 [O-FHA]
- **Q:** Were all solar and wind technologies product requirements met?
- **Defect condition:** Solar & wind technologies policy used to increase base loan amt w/out meeting all eligibility req's
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3803
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G521 — O-FHA-50743 [O-FHA]
- **Q:** Were all weatherization product requirements met?
- **Defect condition:** Weatherization product eligibility requirements not met for eligible energy related improvements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3874
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G524 — O-VA-50787 [O-VA]
- **Q:** Where the Veteran obtained a second mortgage simultaneously with a VA-guaranteed first mortgage, were all secondary borrowing requirements met?
- **Defect condition:** Subordination Agreement not in file or title policy does not reflect the 2nd mtg is in Jr position
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3828
- **Severity:** Critical
- **Classification method:** hand_verified
- **Data needed:** a Subordination Agreement doc type + a junior-lien-position clause within the title policy
- **Rationale:** eval_class=doc_presence targets title_commitment (matched on 'title policy'), but the condition is compound: EITHER no Subordination Agreement OR the title policy doesn't reflect junior-lien position. Mere presence of an ordinary title commitment (ungated on the second-mortgage-position clause) would false-PASS this.
- **SME:** [ ] agree [ ] correct: ______

### G525 — O-FRD-51679 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all additional renovation requirements met?
- **Defect condition:** All renovation funds &/or contingency reserve acct requirements not met in a CHOICERenovation loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3349
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G526 — O-FRD-55326 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all additional renovation requirements met?
- **Defect condition:** CHOICEReno home improvement store completing the renovation do not have licensed/insured contractors
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3329
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** contractor licensing/insurance-verification presence
- **Data needed:** a contractor-licensing-verification doc type (not in corpus)
- **Rationale:** Crisp doc-presence test.
- **SME:** [ ] agree [ ] correct: ______

### G527 — O-FRD-55329 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all additional renovation requirements met?
- **Defect condition:** CHOICEReno loan borrower is the general contractor & a plan detailing the work items not submitted
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3332
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G528 — O-FRD-55327 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all additional renovation requirements met?
- **Defect condition:** CHOICEReno missing contract between borr & home improvement store doing renos w/in reasonable time
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3339
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** renovation-contract execution date vs 180/365-day threshold
- **Data needed:** a CHOICERenovation contract doc type + date field (not in corpus)
- **Rationale:** Explicit numeric day-thresholds are stated in-row ('not to exceed 180 days or 365 days') despite the 'reasonable time' phrase — crisp math once the document exists.
- **SME:** [ ] agree [ ] correct: ______

### G529 — O-FRD-55325 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all additional renovation requirements met?
- **Defect condition:** CHOICEReno, home improvement store doing reno does not have a managed contractor approval process
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3328
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** contractor-approval-process documentation presence
- **Data needed:** a contractor-approval-process doc/attestation (not in corpus)
- **Rationale:** Crisp presence test, not a subjective call.
- **SME:** [ ] agree [ ] correct: ______

### G530 — O-FRD-55330 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all additional renovation requirements met?
- **Defect condition:** CHOICERenovation borr is the general contractor & loan proceeds reimbursed the borrower for labor
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3333
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G531 — O-FRD-51678 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all additional renovation requirements met?
- **Defect condition:** CHOICERenovation-Change order not agreed to by all parties &/or all applicable docs not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3335
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G532 — O-FRD-55324 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all additional renovation requirements met?
- **Defect condition:** In a CHOICEReno, no evidence the home improvement store doing the renovation is financially able
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3340
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G533 — O-FRD-55328 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all additional renovation requirements met?
- **Defect condition:** The borrower is the general contractor in a CHOICERenovation loan and is not licensed/qualified
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3334
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G534 — O-FRD-51680 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all additional renovation requirements met?
- **Defect condition:** Unused CHOICERenovation funds not applied to UPB, addt'l reno, or disbursed to borr as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3352
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G536 — O-FRD-55322 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all eligibility requirements met?
- **Defect condition:** All renovations not completed within 180 days of Note date in a CHOICEReno eXPress CHOICERenovation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3327
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '180 days'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G537 — O-FRD-55334 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all eligibility requirements met?
- **Defect condition:** CHOICERenovation did not document the borrower will occupy w/in 60 days of last reno disbursement
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3345
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** occupancy-within-60-days-of-disbursement date check
- **Data needed:** occupancy-certification + disbursement-date fields (not in corpus)
- **Rationale:** Explicit numeric threshold (60 days) stated in-row.
- **SME:** [ ] agree [ ] correct: ______

### G538 — O-FRD-51671 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all eligibility requirements met?
- **Defect condition:** CHOICERenovation post-closing renovations were not completed within 450 days of the Note date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3346
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '450 days'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G539 — O-FRD-51669 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all eligibility requirements met?
- **Defect condition:** CHOICERenovation-prior written approval not obtained if renovations not completed prior to closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3336
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G540 — O-FRD-58289 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all eligibility requirements met?
- **Defect condition:** Reno extension not sent to Loan Status Hub w/ delay reason & Loan Status Hub granted ext not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3726
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G541 — O-FRD-51670 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all eligibility requirements met?
- **Defect condition:** The property type is ineligible for CHOICERenovation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3348
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G543 — O-FRD-55323 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all renovation requirements met?
- **Defect condition:** CHOICEReno eXPress max financed renovation costs were exceeded for loan type && Duty to Serve area
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3326
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G544 — O-FRD-55331 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all renovation requirements met?
- **Defect condition:** CHOICEReno proceeds PIF short-term reno financing for repairs not done prior to the appraisal/Note
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3350
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'appraisal', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G545 — O-FRD-51677 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all renovation requirements met?
- **Defect condition:** CHOICERenovation appraisal did not include as completed value based on final plans & specs
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3331
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'appraisal', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G546 — O-FRD-55332 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all renovation requirements met?
- **Defect condition:** CHOICERenovation proceeds PIF short-term financing for reno & validation of the cost not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3351
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G547 — O-FRD-56143 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all renovation requirements met?
- **Defect condition:** GreenCHOICE fee credit applied for renovations not related to energy/water efficiency
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3338
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G548 — O-FRD-55333 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all renovation requirements met?
- **Defect condition:** Loan proceeds paid off short-term financing used for renovation in a CHOICEReno eXPress loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3325
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G549 — O-FRD-51675 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all renovation requirements met?
- **Defect condition:** Over 50% of cost of materials advanced & borrower not acting as own contractor in CHOICERenovation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3344
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '50%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G550 — O-FRD-51674 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all renovation requirements met?
- **Defect condition:** The CHOICERenovation proceeds were used for an ineligible purpose
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3347
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G551 — O-FRD-51676 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all renovation requirements met?
- **Defect condition:** The total cost of financed renovations exceeded the applicable limit for a CHOICERenovation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3337
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G553 — O-FRD-58288 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all underwriting requirements met?
- **Defect condition:** CHOICEReno In Progress/CHOICEReno eXPress missing lease &/or temporary rent not in DTI if applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3330
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G554 — O-FRD-51672 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all underwriting requirements met?
- **Defect condition:** CHOICERenovation mtg purpose is Construction or Construction-Perm in lieu of a purchase or refinance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3342
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G555 — O-FRD-58287 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all underwriting requirements met?
- **Defect condition:** Outstanding reno liens after completion of renovations not subordinate to subject CHOICERenovation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3341
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G556 — O-FRD-51673 [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all underwriting requirements met?
- **Defect condition:** The CHOICERenovation proceeds were used for an inelligible purpose
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3343
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G558 — O-FRD-51008 [O-FRD]
- **Q:** Where the loan is a Community Land Trust, were all requirements met?
- **Defect condition:** Borrower eligibility & property improvements resale restrictions not met for a Community Land Trust
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3363
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G559 — O-FRD-56014 [O-FRD]
- **Q:** Where the loan is a Community Land Trust, were all requirements met?
- **Defect condition:** Community Land Trust 2 unit without borrower landlord education or 1 yr prior landlord experience
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3361, 3362
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '1-year'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G560 — O-FRD-56013 [O-FRD]
- **Q:** Where the loan is a Community Land Trust, were all requirements met?
- **Defect condition:** Community Land Trust mtg is not secured by a 1 or 2 unit primary that is not a manufactured home
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3368
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G562 — O-FRD-56015 [O-FRD]
- **Q:** Where the loan is a Community Land Trust, were all requirements met?
- **Defect condition:** The Community Land Trust 2 unit property missing applicable landlord education certificate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3359, 3360
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G563 — O-FRD-56010 [O-FRD]
- **Q:** Where the loan is a Community Land Trust, were all requirements met?
- **Defect condition:** The completed, executed, recorded Community Land Trust Ground Lease is not in the loan file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3365
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G564 — O-FRD-56012 [O-FRD]
- **Q:** Where the loan is a Community Land Trust, were all requirements met?
- **Defect condition:** The loan purpose did not meet Community Land Trust mortgage eligibility requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3366
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G565 — O-FRD-56011 [O-FRD]
- **Q:** Where the loan is a Community Land Trust, were all requirements met?
- **Defect condition:** The loan type did not meet Community Land Trust mortgage eligibility requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3367
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G566 — O-FRD-50408 [O-FRD]
- **Q:** Where the loan is a Construction Conversion and Renovation Mortgage, were all requirements met?
- **Defect condition:** Construction Conversion & Renovation LTV not calculated correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3401
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G567 — O-FRD-50407 [O-FRD]
- **Q:** Where the loan is a Construction Conversion and Renovation Mortgage, were all requirements met?
- **Defect condition:** Int/ext didn't include as completed value for Construction Conv and Reno Mtg
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3400
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'appraisal', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G568 — O-FRD-50403 [O-FRD]
- **Q:** Where the loan is a Construction Conversion and Renovation Mortgage, were all requirements met?
- **Defect condition:** Land ownership & disbursement req's not met for Construction Conv or Reno
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3382
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G569 — O-FRD-00518 [O-FRD]
- **Q:** Where the loan is a Construction Conversion and Renovation Mortgage, were all requirements met?
- **Defect condition:** No classification as construction conv or renovation mtg &/or no verification of completion costs
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3381
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G571 — O-FRD-50405 [O-FRD]
- **Q:** Where the loan is a Construction Conversion and Renovation Mortgage, were all requirements met?
- **Defect condition:** The subject was not an existing 1-4 unit site built home for this Renovation Mortgage
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3727
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G572 — O-FRD-50406 [O-FRD]
- **Q:** Where the loan is a Construction Conversion and Renovation Mortgage, were all requirements met?
- **Defect condition:** Tolerances were exceeded without resubmission on a Construction Conversion/Renovation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3383
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G573 — O-FRD-54870 [O-FRD]
- **Q:** Where the loan is a GreenCHOICE® Mortgage, were all requirements met?
- **Defect condition:** GreenCHOICE NCO energy improvements debt not PIF, balance re-amortized w/out Note & new pymt in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3453
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G574 — O-FRD-52230 [O-FRD]
- **Q:** Where the loan is a GreenCHOICE® Mortgage, were all requirements met?
- **Defect condition:** GreenCHOICE NCO proceeds paid existing debt that financed efficiency improvements & all reqs not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3454
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** GreenCHOICE-proceeds-paid-existing-efficiency-debt trigger detection
- **Stays human:** 'all requirements not met' (unstated residual)
- **Data needed:** a GreenCHOICE-proceeds-use field (deepen closing_disclosure)
- **Rationale:** Trigger fact is named and crisp; catch-all residual stays human.
- **SME:** [ ] agree [ ] correct: ______

### G575 — O-FRD-54868 [O-FRD]
- **Q:** Where the loan is a GreenCHOICE® Mortgage, were all requirements met?
- **Defect condition:** GreenCHOICE energy report alt is missing invoices/receipts or other allowable alt documentation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3450
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G576 — O-FRD-54869 [O-FRD]
- **Q:** Where the loan is a GreenCHOICE® Mortgage, were all requirements met?
- **Defect condition:** GreenCHOICE no cashout financed energy improvements partially paid off, remaining debt not in DTI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3452
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G577 — O-FRD-51183 [O-FRD]
- **Q:** Where the loan is a GreenCHOICE® Mortgage, were all requirements met?
- **Defect condition:** GreenCHOICE no energy report missing, ineligible source, incomplete &/or not w/in 24 mos of closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3449
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '24 months'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G578 — O-FRD-51182 [O-FRD]
- **Q:** Where the loan is a GreenCHOICE® Mortgage, were all requirements met?
- **Defect condition:** GreenCHOICE not interior/exterior w/ as completed value for energy efficiency improvements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3448
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'appraisal', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G579 — O-FRD-51181 [O-FRD]
- **Q:** Where the loan is a GreenCHOICE® Mortgage, were all requirements met?
- **Defect condition:** GreenCHOICE proceeds for efficiency improvements not deposited into a completion escrow account
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3451
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G580 — O-FRD-51180 [O-FRD]
- **Q:** Where the loan is a GreenCHOICE® Mortgage, were all requirements met?
- **Defect condition:** GreenCHOICE proceeds used to finance energy efficient improvements over 15% of as completed value
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3455
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '15%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G581 — O-FRD-51178 [O-FRD]
- **Q:** Where the loan is a GreenCHOICE® Mortgage, were all requirements met?
- **Defect condition:** GreenCHOICE value used in a purchase not lesser of the as completed value & total acquisition cost
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3456
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G582 — O-FRD-51179 [O-FRD]
- **Q:** Where the loan is a GreenCHOICE® Mortgage, were all requirements met?
- **Defect condition:** The as completed value was not used in a GreenCHOICE no cash-out refinance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3457
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G584 — O-FRD-50400 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all LTV/TLTV/HTLTV ratios, borrower contribution, reserves, and sources of funds requirements met?
- **Defect condition:** 2 months reserves not documented for a 2-4 unit Home Possible mortgage
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3483
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '2 months'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G585 — O-FRD-50399 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all LTV/TLTV/HTLTV ratios, borrower contribution, reserves, and sources of funds requirements met?
- **Defect condition:** Borr contribution req't not met as per property type & LTV, TLTV or HTLTV for Home Possible purchase
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3467
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G586 — O-FRD-55319 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all LTV/TLTV/HTLTV ratios, borrower contribution, reserves, and sources of funds requirements met?
- **Defect condition:** Home Possible 3% borr contribution not met & LTV, TLTV or HTLTV over 95% Home Possible 2-4 purchase
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3464
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '3%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G587 — O-FRD-50810 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all LTV/TLTV/HTLTV ratios, borrower contribution, reserves, and sources of funds requirements met?
- **Defect condition:** Home Possible borr did not have 3% own funds & a gift from seller who is the orig lender was rec'd
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3473
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '3%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G588 — O-FRD-00274 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all LTV/TLTV/HTLTV ratios, borrower contribution, reserves, and sources of funds requirements met?
- **Defect condition:** Home Possible sweat equity not documented and certified by the appraiser
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3485
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** sweat-equity appraiser-certification presence
- **Data needed:** an appraiser sweat-equity-certification field (appraisal doc exists; this specific field does not) — same family as asset-verification's G219/G278
- **Rationale:** Crisp attestation-presence test.
- **SME:** [ ] agree [ ] correct: ______

### G589 — O-FRD-00213 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all LTV/TLTV/HTLTV ratios, borrower contribution, reserves, and sources of funds requirements met?
- **Defect condition:** HomePossible-Cash on hand appears borrowed &/or residual income for savings not a positive number
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3469
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** residual-income-for-savings sign test (positive/negative number)
- **Stays human:** 'cash on hand appears borrowed' (evidentiary judgment)
- **Data needed:** a residual-income-for-savings computation field (not in corpus)
- **Rationale:** Compound: the residual-income-sign half is crisp math; the 'appears borrowed' half is evidentiary and stays human — kept YELLOW per the crisp-half-survives convention.
- **SME:** [ ] agree [ ] correct: ______

### G590 — O-FRD-02620 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all LTV/TLTV/HTLTV ratios, borrower contribution, reserves, and sources of funds requirements met?
- **Defect condition:** Source of funds for a Home Possible is an unsecured loan that did not meet all requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3486
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** unsecured-loan-as-funds-source detection (cross-referenced against tradelines/urla_liabilities entities ALREADY extracted)
- **Stays human:** 'all conditions being met' + 'monthly payment... where applicable' (partially unstated)
- **Data needed:** an unsecured-loan-type flag on tradelines/urla_liabilities (both entities already extracted; the loan-type-is-unsecured classification is not)
- **Rationale:** Worth a second look before ruling out entirely: BOTH entity types this needs already exist for every loan (same 'reuse existing entities' pattern as asset-verification's G011 VA-secured-loan candidate) — not claimed ready-to-build here because the 'all conditions'/monthly-payment-inclusion residual isn't fully named in-row.
- **SME:** [ ] agree [ ] correct: ______

### G591 — O-FRD-50398 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all LTV/TLTV/HTLTV ratios, borrower contribution, reserves, and sources of funds requirements met?
- **Defect condition:** The Home Possible max LTV limits were exceeded as per applicable property type and loan purpose
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3477
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G592 — O-FRD-55317 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all LTV/TLTV/HTLTV ratios, borrower contribution, reserves, and sources of funds requirements met?
- **Defect condition:** The TLTV exceeded 105% in a Home Possible that included an Affordable Second
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3434
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '105%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G594 — O-FRD-57505 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all borrower income requirements met?
- **Defect condition:** 2,500 VLIP credit given & borr income converted to an annual basis exceeds 50% of area median income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3863
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '50%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G595 — O-FRD-51681 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all borrower income requirements met?
- **Defect condition:** Home Possible 1 unit primary rental, the renter is a spouse/partner &/or has ownership interest
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3481
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G596 — O-FRD-50396 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all borrower income requirements met?
- **Defect condition:** Home Possible 1 unit rental income did not meet 12 mos history or continuance requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3482
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** 12-month rental-history-duration threshold
- **Stays human:** 'will continue to reside together for the foreseeable future' (unstated criteria)
- **Data needed:** rental-history-duration + lease/continuance documentation (not in corpus)
- **Rationale:** Explicit numeric threshold (12 months) stated in-row; the continuance-affirmation half is softer but still names a specific certification, not open-ended judgment — kept YELLOW.
- **SME:** [ ] agree [ ] correct: ______

### G598 — O-FRD-50392 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all eligibility requirements met?
- **Defect condition:** Borr has ownership in another property, guidelines for HomePossible not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3480
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** other-real-estate-owned/property-ownership fact
- **Data needed:** a financed/owned-properties schedule entity (not modeled — same systemic gap flagged in asset-verification's G240/G241)
- **Rationale:** 'Ownership interest in other residential property' is a crisp, named fact once an REO/owned-property schedule entity exists.
- **SME:** [ ] agree [ ] correct: ______

### G599 — O-FRD-50393 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all eligibility requirements met?
- **Defect condition:** Confirmation borr's will occupy as required for Home Possible not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3479
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G600 — O-FRD-56145 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all eligibility requirements met?
- **Defect condition:** Desktop appraisal used in a Home Possible purchase that did not meet desktop eligibility req's
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3471
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'appraisal', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G601 — O-FRD-50390 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all eligibility requirements met?
- **Defect condition:** Full appraisal not obtained in Home Possible loan & Feedback Cert did not offer an appraisal waiver
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3466
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'appraisal', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G602 — O-FRD-50388 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all eligibility requirements met?
- **Defect condition:** Home Possible Mtg w/temp subsidy buydown plan has 2nd loan not a fixed rate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3468
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G603 — O-FRD-50391 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all eligibility requirements met?
- **Defect condition:** Income used for this Home Possible loan exceeded 80% of area median income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3478
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '80%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G604 — O-FRD-50387 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all eligibility requirements met?
- **Defect condition:** The loan is not an eligible conventional product for the Home Possible program
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3472
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G605 — O-FRD-54537 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all eligibility requirements met?
- **Defect condition:** The mortgage was ineligible under the Home Possible area median income limits
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3465
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G607 — O-FRD-50985 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all homeownership education and landlord education requirements met?
- **Defect condition:** Evidence of landlord education &/or a cert of completion not in file for 2-4 Home Possible purchase
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3553
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G608 — O-FRD-00041 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all homeownership education and landlord education requirements met?
- **Defect condition:** No evidence of homeownership education in a Home Possible using only noncredit payment references
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3475
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G609 — O-FRD-54538 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all homeownership education and landlord education requirements met?
- **Defect condition:** No homeownership education in a Home Possible purchase where all occupying are first time homebuyers
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3474
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G612 — O-FRD-57504 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all underwriting requirements met?
- **Defect condition:** The temporary $2,500 VLIP credit was not provided directly to the borrower through the transaction
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3862
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '$2,500'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G613 — O-FRD-57506 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all underwriting requirements met?
- **Defect condition:** The temporary VLIP $2,500 credit was applied to a loan that was not manually UW or an LPA Accept
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3864
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '$2,500'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G615 — O-FRD-50984 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgages with an RHS Leveraged Second, were all requirements met?
- **Defect condition:** Home Possible w/ RHS Leveraged Second Borr Cert of Eligibility, Form RD 1944.59 not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3740
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G616 — O-FRD-50374 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgages with an RHS Leveraged Second, were all requirements met?
- **Defect condition:** Home Possible w/RHS Leveraged Second is not a 1st lien purchase of 1 unit primary w/ 30 year rate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3484
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '30 year'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G617 — O-FRD-50983 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgages with an RHS Leveraged Second, were all requirements met?
- **Defect condition:** Home Possible with RHS Leveraged Second did not meet LTV limits and/or all RHS requirements not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3741
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G619 — O-FRD-55318 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgages with an RHS Leveraged Second, were all requirements met?
- **Defect condition:** The initial fixed-rate period was under 5 years in a Home-Possible ARM with an Affordable Second
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3476
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '5 years'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G620 — O-FRD-50954 [O-FRD]
- **Q:** Where the loan is a HomeOne Mortgage, were all requirements met?
- **Defect condition:** All  HomeOne property and borrower eligibility requirements were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3460
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G621 — O-FRD-50956 [O-FRD]
- **Q:** Where the loan is a HomeOne Mortgage, were all requirements met?
- **Defect condition:** Confirmation that all borrowers will occupy as primary residence not in the file for a HomeOne mtg
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3463
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G622 — O-FRD-58601 [O-FRD]
- **Q:** Where the loan is a HomeOne Mortgage, were all requirements met?
- **Defect condition:** No evidence at least 1 borr took homeownership education where all borr's are first-time homebuyers
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3461
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G623 — O-FRD-50955 [O-FRD]
- **Q:** Where the loan is a HomeOne Mortgage, were all requirements met?
- **Defect condition:** The maximum HomeOne LTV limit was exceeded as per transaction type
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3462
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G624 — O-FRD-50953 [O-FRD]
- **Q:** Where the loan is a HomeOne Mortgage, were all requirements met?
- **Defect condition:** The subject HomeOne was not underwritten by LPA or did not receive a risk class of Accept
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3459
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G626 — O-FRD-54847 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage on a condo or co-op, were all general eligibility and underwriting requirements met?
- **Defect condition:** Refi Possible condo or co-op appears to be a condotel or insurance requirements were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3694
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G628 — O-FRD-54839 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all borrower eligibility requirements met?
- **Defect condition:** <1/1/22 Qualifying income converted to an annual basis exceeds 80% of the AMI for subject property
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3691
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '80%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G629 — O-FRD-54841 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all borrower eligibility requirements met?
- **Defect condition:** Borr on Note being refinanced is not on Refi Possible w/out req's met & at least 1 borr not retained
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3692
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G630 — O-FRD-54840 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all borrower eligibility requirements met?
- **Defect condition:** Borr(s) on the Refi Possible Note are not the same as is on the Note being refinanced
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3693
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G632 — O-FRD-54851 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all closing requirements met?
- **Defect condition:** Excess Refi Possible proceeds not a principal curtailment &/or not on the Closing Disclosure Stmt
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3698
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** principal-curtailment line-item presence on the Closing Disclosure
- **Data needed:** a principal-curtailment field on closing_disclosure (doc exists; field does not)
- **Rationale:** Crisp field-presence test, not a subjective call.
- **SME:** [ ] agree [ ] correct: ______

### G633 — O-FRD-54864 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all closing requirements met?
- **Defect condition:** Funds for closing are more than $500 in a Refi Possible without sufficient funds being documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3689
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** $500 cash-to-close threshold + funds-documentation presence
- **Data needed:** cash-to-close + funds-documentation fields (not in corpus)
- **Rationale:** Explicit numeric threshold ($500) stated in-row.
- **SME:** [ ] agree [ ] correct: ______

### G634 — O-FRD-54850 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all closing requirements met?
- **Defect condition:** Refi Possible proceeds not used only to PIF the first mtg, closing costs &/or cash back over $250
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3719
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '$250'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G635 — O-FRD-54865 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all closing requirements met?
- **Defect condition:** The appraisal cost offset credit was not passed to the borrower
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3688
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'appraisal', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G637 — O-FRD-54860 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all income and asset documentation requirements met?
- **Defect condition:** Missing individual & business tax returns for last year in Refi Possible using self-employed income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3717
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '1 year'
- **Data needed:** a field/fact on the existing 'se_income_index' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'se_income_index', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G638 — O-FRD-54862 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all income and asset documentation requirements met?
- **Defect condition:** Missing last 1 month receipt of alimony, child support &/or maintenance pymts in a Refi Possible
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3704
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '1 month'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G639 — O-FRD-54861 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all income and asset documentation requirements met?
- **Defect condition:** No 3rd party business exists verif 120 days prior to Note in Refi Possible using SE income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3716
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '120 days'
- **Data needed:** a field/fact on the existing 'se_income_index' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'se_income_index', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G640 — O-FRD-54859 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all income and asset documentation requirements met?
- **Defect condition:** No YTD military leave and earnings statement in a Refi Possible using military income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3707
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G641 — O-FRD-54858 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all income and asset documentation requirements met?
- **Defect condition:** No YTD paystub & W2 or VOE & 10 day PCVVOE in Refi Possible using tip, bonus, OT &/or commission
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3713
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '10 day'
- **Data needed:** a field/fact on the existing 'voe' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'voe', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G642 — O-FRD-54857 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all income and asset documentation requirements met?
- **Defect condition:** No YTD paystub or VOE & 10 day PCVVOE in Refi Possible using base non-fluctuating primary employment
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3712
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '10 day'
- **Data needed:** a field/fact on the existing 'voe' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'voe', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G643 — O-FRD-54863 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all income and asset documentation requirements met?
- **Defect condition:** Refi Possible using alimony, child support &/or maintenance missing legal agmnt w/ amount & duration
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3705
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G645 — O-FRD-54844 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all product eligibility requirements met?
- **Defect condition:** Existing 2nd did not meet secondary financing req's &/or not subordinated to the Refi Possible mtg
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3714
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G646 — O-FRD-54866 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all product eligibility requirements met?
- **Defect condition:** Mtg refinanced to a Refi Possible has recourse/indemnification without meeting eligibility req's
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3720
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G647 — O-FRD-54843 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all product eligibility requirements met?
- **Defect condition:** Refi Possible is super-conforming, temporary interest buydown or TX Equity Section 50(a)(6)
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3703
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G648 — O-FRD-54842 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all product eligibility requirements met?
- **Defect condition:** The Refi Possible is not a fixed-rate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3702
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G649 — O-FRD-54846 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all product eligibility requirements met?
- **Defect condition:** The Refi Possible is not secured by a one-unit primary residence
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3711
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G650 — O-FRD-54845 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all product eligibility requirements met?
- **Defect condition:** The new jr lien UPB is more than the UPB of jr lien being refinanced w/ the 1st to the Refi Possible
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3715
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G652 — O-FRD-54835 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all refinance eligibility requirements met?
- **Defect condition:** <1/1/22 Refi Possible mtg being refinanced not seasoned between 12 mos & 120 mos prior to Note
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3710
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '12 months'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G653 — O-FRD-54836 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all refinance eligibility requirements met?
- **Defect condition:** Ineligible Refi Possible, refinanced mtg is Relief/Enhanced, Refi Possible, subject to repurch/indem
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3700
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G654 — O-FRD-54838 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all refinance eligibility requirements met?
- **Defect condition:** Mtg being refinanced to Refi Possible has 30 delinquent more than once &/or over 60 in last year
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3699
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '30 days'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G655 — O-FRD-54837 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all refinance eligibility requirements met?
- **Defect condition:** Mtg being refinanced to a Refi Possible has been 30 days delinquent in the most recent six months
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3701
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '30 days'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G656 — O-FRD-54834 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all refinance eligibility requirements met?
- **Defect condition:** Refi Possible mtg being refinanced is not a 1st lien conventional owned/securitized by Freddie Mac
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3709
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G658 — O-FRD-54854 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all underwriting requirements met?
- **Defect condition:** No credit assessment in Refi Possible manual UW & credit reestablish req not met after derog credit
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3696
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G659 — O-FRD-54853 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all underwriting requirements met?
- **Defect condition:** No credit assessment in Refi Possible manual UW & pay history req's not met for mtg being refinanced
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3695
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'vom' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'vom', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G660 — O-FRD-54849 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all underwriting requirements met?
- **Defect condition:** Refi Possible interest rate reduction is not at least 50 bps & no reduction to the mtg payment
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3690
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G661 — O-FRD-54848 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all underwriting requirements met?
- **Defect condition:** Refi Possible maximum LTV, TLTV & HTLTV requirements were not met as per property/transaction type
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3706
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G662 — O-FRD-54855 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all underwriting requirements met?
- **Defect condition:** Refi Possible significant derogatory event not documented the cause was beyond the borr’s control
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3718
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G663 — O-FRD-54856 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all underwriting requirements met?
- **Defect condition:** The Refi Possible has a non-occupying borrower and the total DTI ratio exceeded 65%
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3697
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '65%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G664 — O-FRD-54852 [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all underwriting requirements met?
- **Defect condition:** The minimum indicator score is not at least 620 in the subject Refi Possible
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3708
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** 620 minimum-credit-score threshold
- **Data needed:** a credit-score field on credit_report (the doc type exists generically but is absent from loan 05, this pilot's only RHS loan — needs BOTH a new field AND a new RHS-specific fixture)
- **Rationale:** Explicit numeric threshold (620) stated in-row — as crisp as this block gets; blocked purely on missing fixture/field, not on any ambiguity in the rule.
- **SME:** [ ] agree [ ] correct: ______

### G666 — O-FRD-50373 [O-FRD]
- **Q:** Where the loan is a Section 502 GRH Mortgage, were all requirements met?
- **Defect condition:** All requirements not complied with for a Section 502 GRH Mortgage
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3271
- **Severity:** Critical
- **Classification method:** hand_verified
- **Machine checks:** RHS-waiver-approval-letter presence
- **Stays human:** 'did not comply with all of the requirements' (unstated residual)
- **Data needed:** an RHS modification/waiver-approval doc type (not in corpus)
- **Rationale:** Waiver-approval-doc-presence half is crisp; the broad opening clause stays human.
- **SME:** [ ] agree [ ] correct: ______

### G668 — O-FRD-50409 [O-FRD]
- **Q:** Where the loan is a Super Conforming Mortgage, were all requirements met?
- **Defect condition:** Loan amt did not comply with min & max loan amts for Super Conforming mtg
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3830
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G670 — O-FRD-50410 [O-FRD]
- **Q:** Where the loan is a Super Conforming Mortgage, were all requirements met?
- **Defect condition:** Super Conforming was manually UW without a caution, invalid, ineligible or incomplete status by LPA
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3831
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G672 — O-FRD-54543 [O-FRD]
- **Q:** Where the loan is a Texas Equity Section 50(a)(6) loan, were all refinance requirements met?
- **Defect condition:** Remote ink-signed notarization (RIN) was utilized in a Texas Equity Section 50(a)(6) mortgage
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3834
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G674 — O-FNM-52716 [O-FNM]
- **Q:** Where the loan is a Texas Equity Section 50(a)(6) loan, were all requirements met?
- **Defect condition:** Remote online notarization, (RON), was used in a Texas Equity Section 50(a)(6) Mortgage
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3742
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-4.1-02 — Texas Section 50(a)(6) Loan Eligibility (PDF p.771)
- **Guide candidate:** B5-4.1-03 — Texas Section 50(a)(6) Loan Underwriting, Collateral, and Closing Considerations (PDF p.773)
- **Guide candidate:** B5-4.1-04 — Texas Section 50(a)(6) Loan Delivery and Servicing Considerations (PDF p.775)
- **SME:** [ ] agree [ ] correct: ______

### G676 — O-FNM-51479 [O-FNM]
- **Q:** Where the loan is a Texas Equity Section 50(a)(6) loan, were all requirements met?
- **Defect condition:** The subject is an eMortgage which is not eligible for a Texas Section 50(a)(6)
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3836
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **Guide candidate:** B5-4.1-02 — Texas Section 50(a)(6) Loan Eligibility (PDF p.771)
- **Guide candidate:** B5-4.1-03 — Texas Section 50(a)(6) Loan Underwriting, Collateral, and Closing Considerations (PDF p.773)
- **Guide candidate:** B5-4.1-04 — Texas Section 50(a)(6) Loan Delivery and Servicing Considerations (PDF p.775)
- **SME:** [ ] agree [ ] correct: ______

### G678 — O-FRD-50376 [O-FRD]
- **Q:** Where the loan is a cash-out refinance transaction, were all requirements met?
- **Defect condition:** Borr's not on title 6mos prior & did not meet requirements for cashout refi
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3321
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G679 — O-FRD-53317 [O-FRD]
- **Q:** Where the loan is a cash-out refinance transaction, were all requirements met?
- **Defect condition:** Cash-out cooperative unit without at least 1 borr having held cooperative shares for at least 6 mos
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3307
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G680 — O-FRD-53316 [O-FRD]
- **Q:** Where the loan is a cash-out refinance transaction, were all requirements met?
- **Defect condition:** Cash-out leasehold and at least 1 borrower not a lessee on ground/lease agmnt for at least 6 mos
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3309
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G681 — O-FRD-56133 [O-FRD]
- **Q:** Where the loan is a cash-out refinance transaction, were all requirements met?
- **Defect condition:** Cash-out proceeds paid a 1st lien mtg seasoned less than 12 mos & didn't meet standards to not apply
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3317
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '12 months'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G682 — O-FRD-55102 [O-FRD]
- **Q:** Where the loan is a cash-out refinance transaction, were all requirements met?
- **Defect condition:** Delayed financing cash-out refi & borrowed funds to buy the subject not paid down/PIF as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3422
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G683 — O-FRD-54696 [O-FRD]
- **Q:** Where the loan is a cash-out refinance transaction, were all requirements met?
- **Defect condition:** LLC/LP holds title & borr not majority owner & not put in borr's name prior to Note in a CO refi
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3319
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '6 months'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G684 — O-FRD-00691 [O-FRD]
- **Q:** Where the loan is a cash-out refinance transaction, were all requirements met?
- **Defect condition:** Special purpose cash-out doesn't meet limitations on the use of proceeds & ownership of the property
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3819
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G685 — O-FRD-54695 [O-FRD]
- **Q:** Where the loan is a cash-out refinance transaction, were all requirements met?
- **Defect condition:** Title in LLC/LP not borr & did not meet the CO refi 6 mos on title req to qualify for an exception
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3318
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '6 months'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G687 — O-FRD-50375 [O-FRD]
- **Q:** Where the loan is a no cash-out refinance transaction, were all requirements met?
- **Defect condition:** Cash-out exceeded 1% or $2,000 and/or any excess not applied as a principal curtailment
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3596
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '1%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G688 — O-FRD-55902 [O-FRD]
- **Q:** Where the loan is a no cash-out refinance transaction, were all requirements met?
- **Defect condition:** NCO proceeds over the greater of 1% or $2,000 were used to pay past due &/or delinquent taxes
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3443
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '1%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G690 — O-FRD-54694 [O-FRD]
- **Q:** Where the loan is a no cash-out refinance transaction, were all requirements met?
- **Defect condition:** Note date of the refi being PIF not at least 30 days prior to the Note date of the no cash-out refi
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3597
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '30 days'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G691 — O-FRD-56264 [O-FRD]
- **Q:** Where the loan is a no cash-out refinance transaction, were all requirements met?
- **Defect condition:** Proceeds from the no cash-out transaction were used to pay off or pay down an unallowable debt/lien
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3598
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G692 — O-FRD-51841 [O-FRD]
- **Q:** Where the loan is a purchase transaction, were all requirements met?
- **Defect condition:** Cash back or a principal curtailment in a purchase not on the Settlement/Closing Disclosure
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3628
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'closing_disclosure' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'closing_disclosure', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G693 — O-FRD-51839 [O-FRD]
- **Q:** Where the loan is a purchase transaction, were all requirements met?
- **Defect condition:** Cash back or principal curtailment in a purchase transaction w/out meeting conditions to allow it
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3636
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G695 — O-FRD-55672 [O-FRD]
- **Q:** Where the loan is a purchase transaction, were all requirements met?
- **Defect condition:** Prorated property tax credit not used to offset charge to establish the escrow account as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3634
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G696 — O-FRD-54340 [O-FRD]
- **Q:** Where the loan is a purchase transaction, were all requirements met?
- **Defect condition:** Purchase VOD current balance exceeds avg balance over 50% qualifying income w/out supporting doc
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3640
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '50%'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G697 — O-FRD-51840 [O-FRD]
- **Q:** Where the loan is a purchase transaction, were all requirements met?
- **Defect condition:** Purchase cashback results in min contribution not met & principal curtailment not applied for excess
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3577
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G698 — O-FRD-50001 [O-FRD]
- **Q:** Where the loan is a purchase transaction, were all requirements met?
- **Defect condition:** The UW did not ensure the original loan amount does not exceed the maximum loan limit for the area
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3573
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G699 — O-FRD-00684 [O-FRD]
- **Q:** Where the loan is a refinance transaction, were all requirements met?
- **Defect condition:** At least 1 borr not on new loan, or title past year or legally awarded the subject being refinanced
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3301
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G700 — O-FRD-55901 [O-FRD]
- **Q:** Where the loan is a refinance transaction, were all requirements met?
- **Defect condition:** Borr's not on loan being refinanced & no evidence they made pymts on the subject for last 12 mos
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3646
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Machine checks:** explicit numeric/date threshold detected: '12 months'
- **Data needed:** a document/data type not in extract_loan.py's DOC_TYPES at all
- **Rationale:** Bucket-A-style (decision 014 pattern): no keyword in this condition matches any document type extract_loan.py already parses — likely needs a genuinely new synthetic fixture, not just a new field. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

### G702 — O-FRD-54688 [O-FRD]
- **Q:** Where the loan is a refinance transaction, were all requirements met?
- **Defect condition:** Value used was not the value reported as of the appraisal effective date as required in a refinance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3651
- **Severity:** Critical
- **Classification method:** bulk_heuristic
- **Data needed:** a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- **Rationale:** Bucket-B-style (decision 015 pattern): condition references 'appraisal', a document type extract_loan.py already parses for at least one synthetic loan — likely a new-field addition, not a new fixture. NOT hand-verified individually; classified by the bulk keyword heuristic (see module docstring point d) — read the condition text before building.
- **SME:** [ ] agree [ ] correct: ______

## RED

### G010 — PORTAuthority [GENERIC]
- **Q:** Are all Portfolio Expanded Authority Guidelines met?
- **Defect condition:** The underwriter that approved the loan did not have expanded loan authority
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3609
- **Severity:** Critical
- **Classification method:** hand_verified
- **Stays human:** 'did not have sufficient authority' — an internal lender underwriting-authorization-level judgment
- **Rationale:** No document, number, or named comparison basis anywhere in the row — an internal lender authority-matrix determination, not something any loan document states. Also out of this pilot's document-extraction scope entirely (an internal process fact, not borrower/loan data).
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** A2-4.1-01 — Establishing Loan Files (PDF p.78)
- **SME:** [ ] agree [ ] correct: ______

### G017 — PORTGuides [GENERIC]
- **Q:** Are all Portfolio loan overlays met?
- **Defect condition:** Port guides not met (ex: 2 years W2s, 2 mos bank statements, add'l reserves
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3617
- **Severity:** Critical
- **Classification method:** hand_verified
- **Stays human:** bare, non-exhaustive Portfolio overlay list ('ex: 2 years W2s, 2 mos bank statements, add'l reserves, etc' — 'etc' is explicit)
- **Rationale:** The row itself says 'examples' and 'etc' — it does not enumerate a closed, checkable rule set. Needs SME decomposition of the full Portfolio overlay checklist before any single fact is checkable.
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** A2-4.1-01 — Establishing Loan Files (PDF p.78)
- **SME:** [ ] agree [ ] correct: ______

### G018 — PORTTCL [GENERIC]
- **Q:** Are all Portfolio loan overlays met?
- **Defect condition:** TCL (Total Credit Limit) guidelines were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3625
- **Severity:** Critical
- **Classification method:** hand_verified
- **Stays human:** 'TCL (Total Credit Limit) guidelines were not met' — no threshold number stated anywhere in the row
- **Rationale:** Bare reference to an internal Portfolio policy limit with no number given — same pattern as the bare 'all requirements' catch-alls found in the asset-verification triage (decision 017's G018/G023/G196).
- **Guide candidate:** B3-5.1-02 — Determining the Credit Score for a Mortgage Loan (PDF p.474)
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **SME:** [ ] agree [ ] correct: ______

### G100 — O-FNM-52252 [O-FNM]
- **Q:** In a cash-out refinance transaction, were all eligibility requirements  met?
- **Defect condition:** The subject has a student loan cash-out refinance feature without all requirements being met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3320
- **Severity:** Critical
- **Classification method:** hand_verified
- **Stays human:** 'without all requirements being met' — zero specific requirements named in this row for the student-loan cash-out feature
- **Rationale:** Bare catch-all; FNMA's actual student-loan-cash-out-refi rule set is not enumerated anywhere in this row — needs SME decomposition.
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **Guide candidate:** B2-1.3-03 — Cash-Out Reﬁnance Transactions (PDF p.197)
- **Guide candidate:** B2-1.5-02 — Loan Eligibility (PDF p.225)
- **SME:** [ ] agree [ ] correct: ______

### G114 — O-FNM-56579 [O-FNM]
- **Q:** In a limited cash-out refinance transaction, were all eligibility requirements  met?
- **Defect condition:** The limited cash-out refinance was obtained for an unacceptable use
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3564
- **Severity:** Critical
- **Classification method:** hand_verified
- **Stays human:** 'obtained for an unacceptable use' — no specific banned uses named in this row
- **Rationale:** Bare catch-all; FNMA's actual allowable-use list for LCO refis is not stated here — needs SME decomposition before any fact is checkable.
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **Guide candidate:** B5-4.2-02 — Disaster-Related Limited Cash-Out Reﬁnance Flexibilities (PDF p.778)
- **Guide candidate:** B2-1.3-03 — Cash-Out Reﬁnance Transactions (PDF p.197)
- **SME:** [ ] agree [ ] correct: ______

### G132 — O-FNM-50203 [O-FNM]
- **Q:** In a purchase transaction, were all eligibility requirements  met?
- **Defect condition:** Not all Non-Arm's length requirements were met for existing or new homes
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3600
- **Severity:** Critical
- **Classification method:** hand_verified
- **Stays human:** 'not all Non-Arm's Length requirements were met' — zero specific requirements named
- **Rationale:** Bare catch-all; FNMA's non-arm's-length checklist isn't enumerated in this row — needs SME decomposition.
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **SME:** [ ] agree [ ] correct: ______

### G157 — O-FNM-55109 [O-FNM]
- **Q:** In a refinance transaction, were all prohibited practices requirements  met?
- **Defect condition:** There are indicators in the file that the subject refinance is a prearranged refinancing agreement
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3629
- **Severity:** Critical
- **Classification method:** hand_verified
- **Stays human:** 'indicators in the file that the subject refinance is a prearranged refinancing agreement' — a fraud-pattern judgment call with no defined bright-line test
- **Rationale:** 'Indicators' is inherently evidentiary/subjective — same class as G158/G159/G701.
- **Guide candidate:** B2-1.3-04 — Prohibited Reﬁnancing Practices (PDF p.203)
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **SME:** [ ] agree [ ] correct: ______

### G158 — O-FNM-55628 [O-FNM]
- **Q:** In a refinance transaction, were all prohibited practices requirements  met?
- **Defect condition:** There are indicators that the refinance was the result of a conditional tender of payment procedure
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3378
- **Severity:** Critical
- **Classification method:** hand_verified
- **Stays human:** 'indicators that the refinance was the result of a conditional tender of payment procedure' — fraud-pattern judgment
- **Rationale:** Same class as G157/G159/G701 — no stated bright-line test.
- **Guide candidate:** B2-1.3-04 — Prohibited Reﬁnancing Practices (PDF p.203)
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **Guide candidate:** A3-2-02 — Responsible Lending Practices (PDF p.119)
- **SME:** [ ] agree [ ] correct: ______

### G159 — O-FNM-55626 [O-FNM]
- **Q:** In a refinance transaction, were all prohibited practices requirements  met?
- **Defect condition:** There are indicators the lender specifically targeted the Fannie Mae borrower to offer a refinance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3562
- **Severity:** Critical
- **Classification method:** hand_verified
- **Stays human:** 'indicators the lender specifically targeted the Fannie Mae borrower to offer a refinance' — fraud-pattern judgment
- **Rationale:** Same class as G157/G158/G701 — no stated bright-line test.
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** A2-5-01 — Fannie Mae Trade Name and Trademarks (PDF p.102)
- **Guide candidate:** A3-1-01 — Fannie Mae’s Technology Products (PDF p.106)
- **SME:** [ ] agree [ ] correct: ______

### G257 — O-FNM-50883 [O-FNM]
- **Q:** Were all HomeStyle Renovation mortgage requirements met?
- **Defect condition:** The borrower has opted for the HomeStyle "Do It Yourself" option without all requirements being met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3504
- **Severity:** Critical
- **Classification method:** hand_verified
- **Stays human:** 'without all requirements being met' for the HomeStyle 'Do It Yourself' option — zero specific requirements named
- **Rationale:** Bare catch-all; needs SME decomposition of the DIY-option checklist.
- **Guide candidate:** B5-3.2-02 — HomeStyle Renovation Mortgages: Loan and Borrower Eligibility (PDF p.747)
- **Guide candidate:** B8-5-03 — HomeStyle Renovation Mortgage Documentation Requirements (PDF p.924)
- **Guide candidate:** B5-3.2-01 — HomeStyle Renovation Mortgages (PDF p.744)
- **SME:** [ ] agree [ ] correct: ______

### G324 — O-VA-51064 [O-VA]
- **Q:** Were all New Construction/Construction Permanent Home Loan requirements met?
- **Defect condition:** Escrow of completion holdback was inappropriate &/or the home not suitable for immediate occupancy
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3376
- **Severity:** Critical
- **Classification method:** hand_verified
- **Stays human:** BOTH conjuncts are judgment calls: 'escrow holdback amount was not appropriate' (no formula stated) AND 'dwelling not suitable for immediate occupancy' (an inspector's judgment)
- **Rationale:** Unlike most compound rows here, NEITHER half of this one names a crisp fact or number — kept RED rather than defaulting to the crisp-half-survives convention.
- **SME:** [ ] agree [ ] correct: ______

### G347 — UGV Identifier [GENERIC]
- **Q:** Were all Underwriter Guideline Variances (UGV) procedures met?
- **Defect condition:** All UGV exceptions are not clearly identified/listed in the Portfolio exception screen
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3849
- **Severity:** Critical
- **Classification method:** hand_verified
- **Stays human:** an internal lender exception-tracking-system completeness check ('not clearly identified/listed in the Portfolio exception screen') — not a loan-document fact at all
- **Rationale:** Same out-of-scope-entirely class as G010/G350: this is about the LENDER's own internal system, not any document this pilot models.
- **Guide candidate:** B7-2-05 — Title Exceptions and Impediments (PDF p.867)
- **SME:** [ ] agree [ ] correct: ______

### G350 — UGV EPIC [GENERIC]
- **Q:** Were all Underwriter Guideline Variances (UGV) procedures met?
- **Defect condition:** UGV exception is not properly reflected in EPIC - Expanded & UGV box
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3848
- **Severity:** Critical
- **Classification method:** hand_verified
- **Stays human:** same internal lender-system class as G347 ('not properly reflected in EPIC')
- **Rationale:** Same as G347 — out of document-extraction scope entirely.
- **SME:** [ ] agree [ ] correct: ______

### G611 — O-FRD-50395 [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all underwriting requirements met?
- **Defect condition:** Sufficient credit history for min of 1 borr for Home Possible mtg manual UW
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3470
- **Severity:** Critical
- **Classification method:** hand_verified
- **Stays human:** 'sufficient'/'acceptable'/'free of derogatory credit' credit-history-adequacy judgment — no quantified threshold anywhere in the row
- **Rationale:** Unlike most 'sufficient'/'acceptable' rows in this block, this one names NO comparison basis at all (no score, no ratio, no specific document) — a genuine open-ended credit-quality judgment call.
- **SME:** [ ] agree [ ] correct: ______

### G673 — O-FRD-50377 [O-FRD]
- **Q:** Where the loan is a Texas Equity Section 50(a)(6) loan, were all refinance requirements met?
- **Defect condition:** TX Refi did not meet Section 50(a)(6) Article XVI of the Texas Constitution
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3843
- **Severity:** Critical
- **Classification method:** hand_verified
- **Stays human:** bare reference to Texas Constitution Article XVI Section 50(a)(6) with zero in-row specifics
- **Rationale:** Needs SME decomposition of the actual TX 50(a)(6) requirement checklist — this row states no checkable fact on its own.
- **SME:** [ ] agree [ ] correct: ______

### G675 — O-FNM-50324 [O-FNM]
- **Q:** Where the loan is a Texas Equity Section 50(a)(6) loan, were all requirements met?
- **Defect condition:** TX Sect 50(a)(6) Mg didn't comply with TX Constitution and all requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3835
- **Severity:** Critical
- **Classification method:** hand_verified
- **Stays human:** same bare TX 50(a)(6) reference as G673 (FNM variant)
- **Rationale:** Same as G673.
- **Guide candidate:** B5-4.1-02 — Texas Section 50(a)(6) Loan Eligibility (PDF p.771)
- **Guide candidate:** B5-4.1-03 — Texas Section 50(a)(6) Loan Underwriting, Collateral, and Closing Considerations (PDF p.773)
- **Guide candidate:** B5-4.1-04 — Texas Section 50(a)(6) Loan Delivery and Servicing Considerations (PDF p.775)
- **SME:** [ ] agree [ ] correct: ______

### G701 — O-FRD-00692 [O-FRD]
- **Q:** Where the loan is a refinance transaction, were all requirements met?
- **Defect condition:** Loan approved despite indications that the borrower had a prearrangement to refinance the new loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3851
- **Severity:** Critical
- **Classification method:** hand_verified
- **Stays human:** 'appears to have been obtained with unacceptable refinance practices' — a fraud-pattern judgment with 'appears' and 'indications' as its only stated test
- **Rationale:** Same evidentiary-judgment class as G157/G158/G159 — no bright-line test stated.
- **SME:** [ ] agree [ ] correct: ______

## NOT_A_CHECK

### G001 —  [O-FHA]
- **Q:** (FHA) Was this loan originated under a specific product or program?
- **Defect condition:** Buydown
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3878, 3879, 3880, 3881, 3882, 3883, 3884, 3885, 3886, 3887, 3888, 3889, 3890, 3891, 3892
- **Classification method:** hand_verified
- **Rationale:** Screening/routing answer option (product-type selector or a bare 'Yes' PASS_RE's comma-anchored regex doesn't catch), not a defect condition — verified individually, see NOT_A_CHECK_OVERRIDES.
- **SME:** [ ] agree [ ] correct: ______

### G002 —  [O-FNM]
- **Q:** (Fannie Mae) Was this loan originated under a specific product or program?
- **Defect condition:** Adjustable Rate Mortgage (ARM)
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3942, 3943, 3944, 3945, 3946, 3947, 3948, 3949, 3950, 3951, 3952, 3953, 3954, 3955, 3956, 3957, 3958, 3959, 3960, 3961, 3962
- **Classification method:** hand_verified
- **Rationale:** Screening/routing answer option (product-type selector or a bare 'Yes' PASS_RE's comma-anchored regex doesn't catch), not a defect condition — verified individually, see NOT_A_CHECK_OVERRIDES.
- **SME:** [ ] agree [ ] correct: ______

### G003 —  [O-FRD]
- **Q:** (Freddie Mac) Was this loan originated under a specific product or program?
- **Defect condition:** Adjustable Rate (ARM)
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4020, 4021, 4022, 4023, 4024, 4025, 4026, 4027, 4028, 4029, 4030, 4031, 4032, 4033, 4034, 4035, 4036, 4037, 4038, 4039
- **Classification method:** hand_verified
- **Rationale:** Screening/routing answer option (product-type selector or a bare 'Yes' PASS_RE's comma-anchored regex doesn't catch), not a defect condition — verified individually, see NOT_A_CHECK_OVERRIDES.
- **SME:** [ ] agree [ ] correct: ______

### G004 —  [O-RHS]
- **Q:** (RHS) Was this loan originated under a specific product or program?
- **Defect condition:** Combination Construction to Permanent (CP)
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4051, 4052, 4053, 4054, 4055
- **Classification method:** hand_verified
- **Rationale:** Screening/routing answer option (product-type selector or a bare 'Yes' PASS_RE's comma-anchored regex doesn't catch), not a defect condition — verified individually, see NOT_A_CHECK_OVERRIDES.
- **SME:** [ ] agree [ ] correct: ______

### G005 —  [O-VA]
- **Q:** (VA) Was this loan originated under a specific product or program?
- **Defect condition:** Adjustable Rate Mortgage (ARM)
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4058, 4059, 4060, 4061, 4062, 4063, 4064, 4065, 4066, 4067, 4068, 4069, 4070
- **Classification method:** hand_verified
- **Rationale:** Screening/routing answer option (product-type selector or a bare 'Yes' PASS_RE's comma-anchored regex doesn't catch), not a defect condition — verified individually, see NOT_A_CHECK_OVERRIDES.
- **SME:** [ ] agree [ ] correct: ______

### G007 —  [GENERIC]
- **Q:** Are all Portfolio Expanded Authority Guidelines met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4098, 4099
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G025 —  [GENERIC]
- **Q:** Are all Portfolio loan overlays met?
- **Defect condition:** Yes, all Portfolio loan overlays were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4093
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G028 —  [GENERIC]
- **Q:** Are all the Portfolio/CTP program guidelines met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4094, 4095
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G038 —  [GENERIC]
- **Q:** Does the underwriter have the proper lending authority for this loan amount or product and the required second level review was not completed?
- **Defect condition:** Yes, the underwriter has proper lending authority
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3875
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G040 —  [GENERIC]
- **Q:** If the loan is a Medical Professional loan, is all criteria met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3876, 3877
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G041 —  [GENERIC]
- **Q:** If this was an Portfolio Employer Guaranteed loan, were all the requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4096, 4097
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G045 —  [O-FNM]
- **Q:** In a RefiNow transaction, were all borrower benefit requirements met?
- **Defect condition:** Yes, all RefiNow borrower benefit requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3921
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G048 —  [O-FNM]
- **Q:** In a RefiNow transaction, were all borrower eligibility requirements met?
- **Defect condition:** Yes, all RefiNow borrower eligibility requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3913
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G053 —  [O-FNM]
- **Q:** In a RefiNow transaction, were all existing loan eligibility documentation requirements met?
- **Defect condition:** Yes, all RefiNow existing loan eligibility requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3916
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G061 —  [O-FNM]
- **Q:** In a RefiNow transaction, were all income documentation requirements met?
- **Defect condition:** Yes, all RefiNow income requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3914
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G064 —  [O-FNM]
- **Q:** In a RefiNow transaction, were all occupancy and property type documentation requirements met?
- **Defect condition:** Yes, all RefiNow occupancy and property type requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3915
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G066 —  [O-FNM]
- **Q:** In a RefiNow transaction, were all property valuation documentation requirements met?
- **Defect condition:** Yes, all RefiNow property valuation requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3919
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G076 —  [O-FNM]
- **Q:** In a RefiNow transaction, were all subject loan eligibility documentation requirements met?
- **Defect condition:** Yes, all RefiNow subject loan eligibility requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3917
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G081 —  [O-FNM]
- **Q:** In a RefiNow transaction, were all subordinate financing requirements met?
- **Defect condition:** Yes, all RefiNow subordinate financing requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3918
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G088 —  [O-FNM]
- **Q:** In a RefiNow transaction, were all underwriting requirements met?
- **Defect condition:** Yes, all RefiNow underwriting requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3920
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G091 —  [O-FHA]
- **Q:** In a Section 251 Adjustable Rate Mortgage (ARM) transaction, were all requirements met?
- **Defect condition:** Yes, all Section 251 Adjustable Rate Mortgage (ARM) requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3899
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G101 —  [O-FNM]
- **Q:** In a cash-out refinance transaction, were all eligibility requirements  met?
- **Defect condition:** Yes, all cash-out refinance transaction eligibility requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3912
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G105 —  [O-FHA]
- **Q:** In a cash-out refinance transaction, were all eligibility requirements met?
- **Defect condition:** Yes, all cash-out refinance eligibility requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3894
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G116 —  [O-FNM]
- **Q:** In a limited cash-out refinance transaction, were all eligibility requirements  met?
- **Defect condition:** Yes, all limited cash-out refinance transaction eligibility requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3911
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G128 —  [O-FHA]
- **Q:** In a no cash-out refinance transaction, were all eligibility requirements met?
- **Defect condition:** Yes, all no cash-out refinance eligibility requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3895
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G131 —  [O-FNM]
- **Q:** In a purchase transaction, were all eligibility requirements  met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3909, 3910
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G139 —  [O-FNM]
- **Q:** In a purchase transaction, were all payoff of installment land contracts requirements  met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3923, 3924
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G143 —  [O-FRD]
- **Q:** In a purchase transaction, were all payoff of installment land contracts requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3996, 3997
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G147 —  [O-VA]
- **Q:** In a purchase transaction, were all requirements met?
- **Defect condition:** Yes, all purchase transaction requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4071
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G152 —  [O-FHA]
- **Q:** In a refinance transaction, were all eligibility requirements met?
- **Defect condition:** Yes, all refinance eligibility requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3893
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G154 —  [O-FRD]
- **Q:** In a refinance transaction, were all payoff of installment land contracts requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3998, 3999
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G160 —  [O-FNM]
- **Q:** In a refinance transaction, were all prohibited practices requirements  met?
- **Defect condition:** Yes, all refinance transaction prohibited practices requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3922
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G169 —  [O-FRD]
- **Q:** Were all Adjustable Rate (ARM) requirements met?
- **Defect condition:** Yes, all Adjustable Rate (ARM) requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3976
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G174 —  [O-FRD]
- **Q:** Were all Adjustable Rate (ARM) term requirements met?
- **Defect condition:** Yes, all Adjustable Rate (ARM) term requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3977
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G177 —  [O-VA]
- **Q:** Were all Adjustable Rate Mortgage (ARM) requirements met?
- **Defect condition:** Yes, all Adjustable Rate Mortgage (ARM) requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4090
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G186 —  [O-FNM]
- **Q:** Were all Adjustable-Rate Mortgages (ARMs) general requirements  met?
- **Defect condition:** Yes, all Adjustable-Rate Mortgages (ARMs) general requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3925
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G197 —  [O-FNM]
- **Q:** Were all Adjustable-Rate Mortgages (ARMs) program requirements  met?
- **Defect condition:** Yes, all Adjustable-Rate Mortgages (ARMs) program requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3926
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G199 —  [O-VA]
- **Q:** Were all Alternations and Repairs loan requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4086, 4087
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G204 —  [O-FNM]
- **Q:** Were all Community Seconds and Community Land Trusts requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3935, 3936
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G214 —  [O-FHA]
- **Q:** Were all Energy Efficient Mortgage (EEM) program requirements met?
- **Defect condition:** Yes, all EEM requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3898
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G216 —  [O-VA]
- **Q:** Were all Energy Efficient Mortgages requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4084, 4085
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G219 —  [O-VA]
- **Q:** Were all Farm Residence Loan requirements met?
- **Defect condition:** Yes, all Farm Residence Loan requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4091
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G223 —  [O-FHA]
- **Q:** Were all HUD Real Estate Owned (REO) Property requirements met?
- **Defect condition:** Yes, all HUD Real Estate Owned (REO) Property requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3907
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G233 —  [O-FHA]
- **Q:** Were all HUD-92544, Warranty of Completion of Construction, requirements met?
- **Defect condition:** Yes, all HUD-92544, Warranty of Completion of Construction, requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3908
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G244 —  [O-FNM]
- **Q:** Were all HomeReady requirements met?
- **Defect condition:** Yes, all HomeReady requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3939
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G252 —  [O-FNM]
- **Q:** Were all HomeStyle Energy mortgage requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3932, 3933
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G260 —  [O-FNM]
- **Q:** Were all HomeStyle Renovation mortgage requirements met?
- **Defect condition:** Yes, all HomeStyle Renovation mortgage requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3931
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G266 —  [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) borrower requirements met?
- **Defect condition:** Yes, all Interest Rate Reduction Refinancing Loans (IRRRLs) borrower requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4074
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G272 —  [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) closing and delivery requirements met?
- **Defect condition:** Yes, all Interest Rate Reduction Refinancing Loans (IRRRLs) closing/delivery requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4078
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G275 —  [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) fees requirements met?
- **Defect condition:** Yes, all Interest Rate Reduction Refinancing Loans (IRRRLs) fees requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4075
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G283 —  [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) terms requirements met?
- **Defect condition:** Yes, all Interest Rate Reduction Refinancing Loans (IRRRLs) terms requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4076
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G293 —  [O-VA]
- **Q:** Were all Interest Rate Reduction Refinancing Loans (IRRRLs) underwriting requirements met?
- **Defect condition:** Yes, all Interest Rate Reduction Refinancing Loans (IRRRLs) underwriting requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4077
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G294 —  [O-VA]
- **Q:** Were all Joint Loan requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4081, 4082
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G302 —  [O-FNM/O-FRD]
- **Q:** Were all Loans with Resale Restrictions requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3937, 3938, 4000, 4001
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G312 —  [O-FNM]
- **Q:** Were all NY CEMA Agreement requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3940, 3941
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G318 —  [O-RHS]
- **Q:** Were all Native American restricted land requirements met?_x000D_
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4056, 4057
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G333 —  [O-VA]
- **Q:** Were all New Construction/Construction Permanent Home Loan requirements met?
- **Defect condition:** Yes, all New Construction/Permanent Home Loan requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4083
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G337 —  [O-FRD]
- **Q:** Were all New York Consolidation, Extension and Modification Agreement (CEMA) requirements met?
- **Defect condition:** Yes, all New York Consolidation, Extension and Modification Agreement (CEMA) requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3975
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G342 —  [O-FHA]
- **Q:** Were all Section 203(h) Mortgage Insurance for Disaster Victims eligibility requirements met?
- **Defect condition:** Yes, all Section 203(h) eligibility requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3896
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G344 —  [O-FHA]
- **Q:** Were all Section 203(h) Mortgage Insurance for Disaster Victims underwriting requirements met?
- **Defect condition:** Yes, all Section 203(h) underwriting requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3897
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G345 —  [O-VA]
- **Q:** Were all Supplemental Loan requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4088, 4089
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G348 —  [GENERIC]
- **Q:** Were all Underwriter Guideline Variances (UGV) procedures met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4101, 4102
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G358 —  [O-FNM]
- **Q:** Were all additional HomeReady requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3971, 3972
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G365 —  [O-FNM]
- **Q:** Were all additional HomeStyle Renovation mortgage requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3965, 3966
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G369 —  [O-FRD]
- **Q:** Were all additional Loans with Resale Restrictions requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4040, 4041
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G381 —  [O-VA]
- **Q:** Were all additional New Construction/Construction Permanent Home Loan requirements met?
- **Defect condition:** Yes, all additional New Construction/Construction Permanent Home Loan requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4092
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G393 —  [O-RHS]
- **Q:** Were all additional combination construction to permanent (single-close) loan requirements met?
- **Defect condition:** Yes, all additional combination construction to permanent (single-close) requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4050
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G409 —  [GENERIC]
- **Q:** Were all additional project eligibility requirements met for the condo/coop SONYMA project (e.g., commercial space requirements, owner occupancy, litigation, for a co-op share price information, etc.)?
- **Defect condition:** Yes
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4100
- **Classification method:** hand_verified
- **Rationale:** Screening/routing answer option (product-type selector or a bare 'Yes' PASS_RE's comma-anchored regex doesn't catch), not a defect condition — verified individually, see NOT_A_CHECK_OVERRIDES.
- **SME:** [ ] agree [ ] correct: ______

### G411 —  [O-FNM]
- **Q:** Were all additional single closing conversion of construction-to-permanent financing requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3969, 3970
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G422 —  [O-VA]
- **Q:** Were all cash-out refinance requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4079, 4080
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G438 —  [O-RHS]
- **Q:** Were all combination construction to permanent (single-close) loan requirements met?
- **Defect condition:** Yes, all combination construction to permanent (single-close) requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4049
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G443 —  [O-FHA]
- **Q:** Were all construction to permanent (CP) eligibility requirements met?
- **Defect condition:** Yes, all construction to permanent (CP) eligibility requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3904
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G448 —  [O-FNM]
- **Q:** Were all conversion of construction-to-permanent (CP) mortgage loan financing requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3929, 3930
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G452 —  [O-FNM]
- **Q:** Were all high-balance mortgage loan requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3927, 3928
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G460 —  [O-FHA]
- **Q:** Were all new construction completion requirements met?
- **Defect condition:** Yes, all new construction completion requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3903
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G471 —  [O-FHA]
- **Q:** Were all new construction documentation requirements met?
- **Defect condition:** Yes, all new construction documentation requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3902
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G475 —  [O-FHA]
- **Q:** Were all new construction eligibility requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3900, 3901
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G480 —  [O-RHS]
- **Q:** Were all prohibited loan purpose requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4042, 4043, 4044
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G484 —  [O-RHS]
- **Q:** Were all purchase transaction documentation and/or ratio waiver requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4045, 4046
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G493 —  [O-RHS]
- **Q:** Were all refinance transaction documentation and/or ratio waiver requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4047, 4048
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G499 —  [O-FNM]
- **Q:** Were all shared equity transaction requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3973, 3974
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G511 —  [O-FNM]
- **Q:** Were all single closing conversion of construction-to-permanent financing requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3967, 3968
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G520 —  [O-FHA]
- **Q:** Were all solar and wind technologies product requirements met?
- **Defect condition:** Yes, all solar and wind technologies product requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3906
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G522 —  [O-FHA]
- **Q:** Were all weatherization product requirements met?
- **Defect condition:** Yes, all weatherization product requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3905
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G523 —  [O-VA]
- **Q:** Where the Veteran obtained a second mortgage simultaneously with a VA-guaranteed first mortgage, were all secondary borrowing requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4072, 4073
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G535 —  [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all additional renovation requirements met?
- **Defect condition:** Yes, all additional CHOICERenovation® Mortgages renovation requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4019
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G542 —  [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all eligibility requirements met?
- **Defect condition:** Yes, all CHOICERenovation® Mortgages eligibility requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4016
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G552 —  [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all renovation requirements met?
- **Defect condition:** Yes, all CHOICERenovation® Mortgages renovation requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4018
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G557 —  [O-FRD]
- **Q:** Where the loan is a CHOICERenovation® Mortgages, were all underwriting requirements met?
- **Defect condition:** Yes, all CHOICERenovation® Mortgages underwriting requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4017
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G561 —  [O-FRD]
- **Q:** Where the loan is a Community Land Trust, were all requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4008, 4009
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G570 —  [O-FRD]
- **Q:** Where the loan is a Construction Conversion and Renovation Mortgage, were all requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4010, 4011
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G583 —  [O-FRD]
- **Q:** Where the loan is a GreenCHOICE® Mortgage, were all requirements met?
- **Defect condition:** Yes, all GreenCHOICE® Mortgage requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4015
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G593 —  [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all LTV/TLTV/HTLTV ratios, borrower contribution, reserves, and sources of funds requirements met?
- **Defect condition:** Yes, all Home Possible® LTV/TLTV/HTLTV, contribution, reserves, funds source requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4005
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G597 —  [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all borrower income requirements met?
- **Defect condition:** Yes, all Home Possible® borrower income requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4004
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G606 —  [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all eligibility requirements met?
- **Defect condition:** Yes, all Home Possible® eligibility requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4002
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G610 —  [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all homeownership education and landlord education requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4006, 4007
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G614 —  [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgage, were all underwriting requirements met?
- **Defect condition:** Yes, all Home Possible® underwriting requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4003
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G618 —  [O-FRD]
- **Q:** Where the loan is a Home Possible® Mortgages with an RHS Leveraged Second, were all requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3979, 3980
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G625 —  [O-FRD]
- **Q:** Where the loan is a HomeOne Mortgage, were all requirements met?
- **Defect condition:** Yes, all HomeOne Mortgage requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4014
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G627 —  [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage on a condo or co-op, were all general eligibility and underwriting requirements met?
- **Defect condition:** Yes, all Refi Possible condo or co-op general eligibility and underwriting requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3991
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G631 —  [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all borrower eligibility requirements met?
- **Defect condition:** Yes, all Refi Possible borrower eligibility requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3986
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G636 —  [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all closing requirements met?
- **Defect condition:** Yes, all Refi Possible closing requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3990
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G644 —  [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all income and asset documentation requirements met?
- **Defect condition:** Yes, all Refi Possible income and asset documentation requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3989
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G651 —  [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all product eligibility requirements met?
- **Defect condition:** Yes, all Refi Possible product eligibility requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3987
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G657 —  [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all refinance eligibility requirements met?
- **Defect condition:** Yes, all Refi Possible refinance eligibility requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3985
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G665 —  [O-FRD]
- **Q:** Where the loan is a Refi Possible mortgage, were all underwriting requirements met?
- **Defect condition:** Yes, all Refi Possible underwriting requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3988
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G667 —  [O-FRD]
- **Q:** Where the loan is a Section 502 GRH Mortgage, were all requirements met?
- **Defect condition:** Yes, all Section 502 GRH requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3978
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G669 —  [O-FRD]
- **Q:** Where the loan is a Super Conforming Mortgage, were all requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4012, 4013
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G671 —  [O-FRD]
- **Q:** Where the loan is a Texas Equity Section 50(a)(6) loan, were all refinance requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3992, 3993
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G677 —  [O-FNM]
- **Q:** Where the loan is a Texas Equity Section 50(a)(6) loan, were all requirements met?
- **Defect condition:** Yes, all Texas Section 50(a)(6) loan requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3934
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G686 —  [O-FRD]
- **Q:** Where the loan is a cash-out refinance transaction, were all requirements met?
- **Defect condition:** Yes, all cash-out refinance transaction requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3984
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G689 —  [O-FRD]
- **Q:** Where the loan is a no cash-out refinance transaction, were all requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3982, 3983
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G694 —  [O-FRD]
- **Q:** Where the loan is a purchase transaction, were all requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 3994, 3995
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G703 —  [O-FRD]
- **Q:** Where the loan is a refinance transaction, were all requirements met?
- **Defect condition:** Yes, all refinance transaction requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 3981
- **Classification method:** mechanical_pass_answer
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

