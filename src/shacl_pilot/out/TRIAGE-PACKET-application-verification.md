# SME Review Packet — application-verification block triage

**80 rules / 54 unique (question, condition) groups.** Every classification
below is a *proposal* pending your review — mark each ✅ agree / ✏️ correct.
Bins: GREEN = automatable now · YELLOW = automatable after data/guide work ·
RED = stays human · NOT_A_CHECK = pass/N-A answer option, not a defect rule.

**Source workbook:** `PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv` — row numbers below are Excel-style
(header = row 1), so you can open the sheet and jump straight to each rule.

## Headline

| Bin | Groups | Rules | % of defect groups |
|---|---|---|---|
| GREEN | 21 | 33 | 51% |
| YELLOW | 12 | 16 | 29% |
| RED | 8 | 12 | 20% |
| NOT_A_CHECK | 13 | 19 | — |

## GREEN

### G05 — CIP DATA POINTS [GENERIC]
- **Q:** Are the 4 Customer Identification Program (CIP) data points provided in file:  Name, Physical property address, DOB, SS#/Tax ID?
- **Defect condition:** No, one or more of the CIP data points was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 13
- **Severity:** Major
- **Machine checks:** all 4 CIP fields (name, address, DOB, SSN) present on 1003/file
- **Rationale:** Pure field-presence test; fields already in the extraction contract.
- **Guide candidate:** B4-1.4-11 — Value Acceptance + Property Data (PDF p.634)
- **Guide candidate:** B7-3-02 — Property Insurance Requirements for One-to Four-Unit Properties (PDF p.875)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **SME:** ☐ agree ☐ correct: ______

### G08 — Final URLA [GENERIC]
- **Q:** Have all sections of the Final 1003 been completed and accurate?
- **Defect condition:** The employment dates listed on the 1003 do not match other employment documentation in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 2, 3, 4, 5, 6, 7, 8, 9
- **Severity:** Major
- **Machine checks:** 1003 employment dates vs VOE/paystub dates
- **Rationale:** ALREADY BUILT: EmploymentStartDateShape (CHK-APP-001), proven on loan 01.
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** A3-3-03 — Other Servicing Arrangements (PDF p.131)
- **Guide candidate:** B3-2-04 — DU Documentation Requirements (PDF p.305)
- **SME:** ☐ agree ☐ correct: ______

### G12 — O-FHA-15140 [O-FHA]
- **Q:** Were all application disclosure requirements met?
- **Defect condition:** HUD's Lead Based Paint Notice is missing or was not provided timely, where required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 64
- **Severity:** Critical
- **Machine checks:** LBP notice presence gated on year_built < 1978
- **Stays human:** 'timely' timing
- **Data needed:** LBP notice doc type
- **Rationale:** Same pattern as built LbpDisclosureShape; FHA variant.
- **SME:** ☐ agree ☐ correct: ______

### G14 — O-VA-15711 [O-VA]
- **Q:** Were all application disclosure requirements met?
- **Defect condition:** No, the ARM pre-loan disclosure is missing or was not provided timely
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 11
- **Severity:** Critical
- **Machine checks:** ARM pre-loan disclosure presence gated on AdjustableRate
- **Stays human:** 'timely'
- **Rationale:** ALREADY BUILT: ArmDisclosureShape (CHK-APP-007), proven on loan 03.
- **SME:** ☐ agree ☐ correct: ______

### G17 — O-VA-15711 [O-VA]
- **Q:** Were all application disclosure requirements met?
- **Defect condition:** The LE was not provided within 3 days
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 63
- **Severity:** Major
- **Machine checks:** LE provided-date within 3 business days of application date
- **Data needed:** LE date + application date fields
- **Rationale:** Crisp TRID rule; business-day math is deterministic.
- **SME:** ☐ agree ☐ correct: ______

### G21 — O-FHA-15293, O-FRD-14083, O-RHS-15627, O-VA-14259 [O-FHA/O-FRD/O-RHS/O-VA]
- **Q:** Were all final Uniform Residential Loan Application requirements met?
- **Defect condition:** All sections of URLA Additional Borrower form not fully completed, correct &/or signed as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 20, 22, 23, 24
- **Severity:** Critical/Major
- **Machine checks:** co-borrower employer + income presence + co-borrower signature (final 1003)
- **Stays human:** 'fully completed, correct'
- **Rationale:** BUILT 2026-07-29 (decision 015): CoBorrowerSectionCompleteShape (CHK-APP-008). Was miscategorized as needing a separate 'Additional Borrower form' document — verified via pdftotext that the co-borrower's data is inline in the same final 1003 every loan already has; extract_loan.py's own 'first occurrence wins' logic was silently discarding it. Fixed by extract_coborrower_fields().
- **SME:** ☐ agree ☐ correct: ______

### G22 — O-FRD-14083, O-RHS-15627, O-VA-14259 [O-FRD/O-RHS/O-VA]
- **Q:** Were all final Uniform Residential Loan Application requirements met?
- **Defect condition:** Final application not in the file or is incomplete, incorrect or not dated & signed by all parties
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 16, 17, 18
- **Severity:** Critical/Major
- **Machine checks:** final 1003 presence + signed + dated by all parties
- **Stays human:** 'incomplete, incorrect'
- **Rationale:** Presence/signature/date already extractable; content-accuracy stays human.
- **SME:** ☐ agree ☐ correct: ______

### G24 — O-FHA-15293 [O-FHA]
- **Q:** Were all final Uniform Residential Loan Application requirements met?
- **Defect condition:** Sections of the final URLA were incomplete, inaccurate &/or not signed by all parties
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 29
- **Severity:** Critical
- **Machine checks:** co-borrower employer + income presence + co-borrower signature (final 1003)
- **Stays human:** 'inaccurate'
- **Rationale:** BUILT 2026-07-29 (decision 015): same shape as #21 (CoBorrowerSectionCompleteShape, CHK-APP-008) — this row's condition text ('sections... not signed by all parties') and #21's ('Additional Borrower form... not signed') describe the same underlying gap; one check covers both AMQ exception codes.
- **SME:** ☐ agree ☐ correct: ______

### G26 — O-FHA-15293 [O-FHA]
- **Q:** Were all final Uniform Residential Loan Application requirements met?
- **Defect condition:** The final HUD-92900-A is missing, incomplete, incorrect &/or is not signed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 19
- **Severity:** Major
- **Machine checks:** HUD-92900-A presence + signatures by section
- **Stays human:** 'incomplete, incorrect'
- **Rationale:** ALREADY BUILT (signature core): Hud92900aBorrowerSigShape, proven on loan 02.
- **SME:** ☐ agree ☐ correct: ______

### G27 — O-FHA-15293 [O-FHA]
- **Q:** Were all final Uniform Residential Loan Application requirements met?
- **Defect condition:** The final application is not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 14
- **Severity:** Critical
- **Machine checks:** final application presence in file
- **Rationale:** Pure doc presence; already inventoried.
- **SME:** ☐ agree ☐ correct: ______

### G28 — O-FHA-15293, O-FRD-14083, O-RHS-15627, O-VA-14259 [O-FHA/O-FRD/O-RHS/O-VA]
- **Q:** Were all final Uniform Residential Loan Application requirements met?
- **Defect condition:** Unmarried Addendum not completed as applicable when borrower selects "unmarried" in section 1
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 30, 32, 33, 34
- **Severity:** Major
- **Machine checks:** Unmarried Addendum presence gated on marital_status = Unmarried
- **Data needed:** marital status field (extractable) + addendum doc type
- **Rationale:** Well-defined conditional presence.
- **SME:** ☐ agree ☐ correct: ______

### G30 — O-FNM-15304 [O-FNM]
- **Q:** Were all final Uniform Residential Loan Application requirements met?
- **Defect condition:** All sections of URLA Additional Borrower form not fully completed, correct &/or signed as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 21
- **Severity:** Major
- **Machine checks:** as #21 (FNM variant)
- **Stays human:** 'fully completed, correct'
- **Rationale:** BUILT 2026-07-29: same CoBorrowerSectionCompleteShape as #21.
- **Guide candidate:** B5-3.2-02 — HomeStyle Renovation Mortgages: Loan and Borrower Eligibility (PDF p.747)
- **Guide candidate:** B5-6-01 — HomeReady Mortgage Loan and Borrower Eligibility (PDF p.808)
- **Guide candidate:** B5-7-01 — High LTV Reﬁnance Loan and Borrower Eligibility (PDF p.819)
- **SME:** ☐ agree ☐ correct: ______

### G31 — O-FNM-15304 [O-FNM]
- **Q:** Were all final Uniform Residential Loan Application requirements met?
- **Defect condition:** Final application not in the file or is incomplete, incorrect or not dated & signed by all parties
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 15
- **Severity:** Critical
- **Machine checks:** as #22 (FNM variant)
- **Stays human:** 'incomplete, incorrect'
- **Rationale:** Same as #22.
- **Guide candidate:** A1-1-01 — Application and Approval of Seller/Servicer (PDF p.20)
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **SME:** ☐ agree ☐ correct: ______

### G33 — O-FNM-15304 [O-FNM]
- **Q:** Were all final Uniform Residential Loan Application requirements met?
- **Defect condition:** Unmarried Addendum not completed as applicable when borrower selects "unmarried" in section 1
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 31
- **Severity:** Major
- **Machine checks:** as #28 (FNM variant)
- **Data needed:** same as #28
- **Rationale:** Same as #28.
- **Guide candidate:** B5-3.2-02 — HomeStyle Renovation Mortgages: Loan and Borrower Eligibility (PDF p.747)
- **Guide candidate:** B5-4.1-02 — Texas Section 50(a)(6) Loan Eligibility (PDF p.771)
- **Guide candidate:** B5-4.1-03 — Texas Section 50(a)(6) Loan Underwriting, Collateral, and Closing Considerations (PDF p.773)
- **SME:** ☐ agree ☐ correct: ______

### G36 — O-FHA-15141, O-RHS-15626 [O-FHA/O-RHS]
- **Q:** Were all initial Uniform Residential Loan Application requirements met?
- **Defect condition:** Initial application not in the file or is incomplete, incorrect or not dated & signed by all parties
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 39, 40, 42
- **Severity:** Critical
- **Machine checks:** initial application presence + signed + dated
- **Stays human:** 'incomplete, incorrect'
- **Data needed:** initial-1003 doc type distinct from final
- **Rationale:** Same pattern as #22 for the initial URLA.
- **SME:** ☐ agree ☐ correct: ______

### G43 — O-FHA-15141 [O-FHA]
- **Q:** Were all initial Uniform Residential Loan Application requirements met?
- **Defect condition:** The initial HUD-92900-A is missing, incomplete, incorrect &/or is not signed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 45
- **Severity:** Critical
- **Machine checks:** initial HUD-92900-A presence + signatures
- **Stays human:** 'incomplete, incorrect'
- **Rationale:** Initial-doc variant of #26; same machinery.
- **SME:** ☐ agree ☐ correct: ______

### G44 — O-FRD-14076 [O-FRD]
- **Q:** Were all initial Uniform Residential Loan Application requirements met?
- **Defect condition:** The initial application is not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 41
- **Severity:** Minor
- **Machine checks:** initial application presence in file
- **Data needed:** initial-1003 doc type
- **Rationale:** Pure presence (FRD, Minor severity).
- **SME:** ☐ agree ☐ correct: ______

### G45 — O-FHA-15141, O-FRD-14076, O-RHS-15626, O-VA-14253 [O-FHA/O-FRD/O-RHS/O-VA]
- **Q:** Were all initial Uniform Residential Loan Application requirements met?
- **Defect condition:** Unmarried Addendum not completed as applicable when borrower selects "unmarried" in section 1
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 58, 59, 60, 61
- **Severity:** Critical/Major
- **Machine checks:** as #28 (initial URLA variant)
- **Data needed:** as #28
- **Rationale:** Same as #28.
- **SME:** ☐ agree ☐ correct: ______

### G51 — O-BP-14663 [GENERIC]
- **Q:** Were the following non-regulatory customary disclosures provided to the applicant in the initial disclosure package?_x000D_
- **Defect condition:** Borrower Certification and Authorization to Release Information was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 12
- **Severity:** Major
- **Machine checks:** Borrower Certification & Authorization presence
- **Rationale:** Doc presence; loan 01's disclosure-package index already lists this doc family.
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **Guide candidate:** B4-1.1-05 — Disclosure of Information to Appraisers (PDF p.543)
- **Guide candidate:** A2-2-02 — Delivery Information and Delivery-Option Speciﬁc Representations and Warranties (PDF p.34)
- **SME:** ☐ agree ☐ correct: ______

### G52 — O-BP-14663 [GENERIC]
- **Q:** Were the following non-regulatory customary disclosures provided to the applicant in the initial disclosure package?_x000D_
- **Defect condition:** Flood Insurance Coverage Disclosure was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 35
- **Severity:** Major
- **Machine checks:** Flood Insurance Coverage Disclosure presence
- **Data needed:** doc type (index row exists in disclosure package)
- **Rationale:** Doc presence via disclosure index.
- **Guide candidate:** B7-1-02 — Mortgage Insurance Coverage Requirements (PDF p.852)
- **Guide candidate:** B7-2-03 — General Title Insurance Coverage (PDF p.861)
- **Guide candidate:** B7-2-04 — Special Title Insurance Coverage Considerations (PDF p.863)
- **SME:** ☐ agree ☐ correct: ______

### G53 — O-BP-14663 [GENERIC]
- **Q:** Were the following non-regulatory customary disclosures provided to the applicant in the initial disclosure package?_x000D_
- **Defect condition:** Intent to Proceed with Application was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 62
- **Severity:** Major
- **Machine checks:** Intent to Proceed presence (+ signed date)
- **Rationale:** Field intent_to_proceed_signed_date ALREADY extracted on loan 01.
- **Guide candidate:** B1-1-01 — Contents of the Application Package (PDF p.167)
- **Guide candidate:** A1-1-01 — Application and Approval of Seller/Servicer (PDF p.20)
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **SME:** ☐ agree ☐ correct: ______

## YELLOW

### G01 — O-CFPB-14500 [GENERIC]
- **Q:** (Best Practice) Were all Limited English Proficiency (LEP) requirements met?_x000D_
- **Defect condition:** (Best Practice) Documented and verifiable LEP preferences were not obtained from the applicant(s)
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 66
- **Severity:** Minor
- **Machine checks:** presence of documented LEP preference record
- **Stays human:** adequacy of the record
- **Data needed:** LEP preference form/doc type in extraction contract
- **Rationale:** BLOCKED ON MISSING FIXTURE (decision 014), not a rule-clarity problem: Best-practice; presence checkable once doc type is captured.
- **Guide candidate:** A2-2-04 — Limited Waiver and Enforcement Relief of Representations and Warranties (PDF p.38)
- **Guide candidate:** A2-2-05 — Invalidation of Limited Waiver of Representations and Warranties (PDF p.44)
- **Guide candidate:** A4-1-04 — Submission of Irrevocable Limited Powers of Attorney (PDF p.164)
- **SME:** ☐ agree ☐ correct: ______

### G02 — O-CFPB-14500 [GENERIC]
- **Q:** (Best Practice) Were all Limited English Proficiency (LEP) requirements met?_x000D_
- **Defect condition:** (Best Practice) Limited English Proficiency (LEP) disclosure not provided at the time of application
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 65
- **Severity:** Minor
- **Machine checks:** LEP disclosure presence + provided-date vs application-date
- **Data needed:** LEP disclosure doc type + its date field
- **Rationale:** BLOCKED ON MISSING FIXTURE (decision 014), not a rule-clarity problem: Presence crisp; 'timely' needs both dates.
- **Guide candidate:** A1-1-01 — Application and Approval of Seller/Servicer (PDF p.20)
- **Guide candidate:** A2-2-04 — Limited Waiver and Enforcement Relief of Representations and Warranties (PDF p.38)
- **Guide candidate:** A2-2-05 — Invalidation of Limited Waiver of Representations and Warranties (PDF p.44)
- **SME:** ☐ agree ☐ correct: ______

### G13 — O-FHA-15140 [O-FHA]
- **Q:** Were all application disclosure requirements met?
- **Defect condition:** It was not evident HUD-92564-CN, For Your Protection: Get a Home Inspection, was provided timely
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 36
- **Severity:** Major
- **Machine checks:** HUD-92564-CN presence
- **Stays human:** 'timely'
- **Data needed:** doc type + provided date
- **Rationale:** BLOCKED ON MISSING FIXTURE (decision 014), not a rule-clarity problem: Presence easy; timing needs dates.
- **SME:** ☐ agree ☐ correct: ______

### G15 — O-VA-15711 [O-VA]
- **Q:** Were all application disclosure requirements met?
- **Defect condition:** No, the executed VA Counseling Checklist is missing or was not provided timely
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 71, 72
- **Severity:** Major
- **Machine checks:** VA Counseling Checklist presence + signature
- **Data needed:** doc type in inventory
- **Rationale:** BLOCKED ON MISSING FIXTURE (decision 014), not a rule-clarity problem: Signature detection exists; needs the doc type added.
- **SME:** ☐ agree ☐ correct: ______

### G16 — O-FHA-15140 [O-FHA]
- **Q:** Were all application disclosure requirements met?
- **Defect condition:** The Informed Consumer Choice Disclosure Notice is missing or was not provided timely
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 38
- **Severity:** Critical
- **Machine checks:** Informed Consumer Choice Disclosure presence
- **Data needed:** doc type
- **Rationale:** BLOCKED ON MISSING FIXTURE (decision 014), not a rule-clarity problem: Straight presence once doc type captured.
- **SME:** ☐ agree ☐ correct: ______

### G18 — O-FHA-15140 [O-FHA]
- **Q:** Were all application disclosure requirements met?
- **Defect condition:** The executed Important Notice to Homebuyers, HUD-92900-B is missing or was not provided timely
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 37
- **Severity:** Critical
- **Machine checks:** HUD-92900-B presence + signature
- **Data needed:** doc type
- **Rationale:** BLOCKED ON MISSING FIXTURE (decision 014), not a rule-clarity problem: Presence + signature pattern, doc type not yet in contract.
- **SME:** ☐ agree ☐ correct: ______

### G35 — O-FHA-15141, O-FRD-14076, O-RHS-15626, O-VA-14253 [O-FHA/O-FRD/O-RHS/O-VA]
- **Q:** Were all initial Uniform Residential Loan Application requirements met?
- **Defect condition:** All sections of URLA Additional Borrower form not fully completed, correct &/or signed as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 48, 49, 50, 51
- **Severity:** Critical/Major
- **Machine checks:** initial-URLA Additional Borrower form presence + signature
- **Stays human:** completeness/correctness
- **Data needed:** doc type + fields
- **Rationale:** BLOCKED ON MISSING FIXTURE (decision 014), not a rule-clarity problem: Initial-application variant of #21.
- **SME:** ☐ agree ☐ correct: ______

### G39 — O-VA-14253 [O-VA]
- **Q:** Were all initial Uniform Residential Loan Application requirements met?
- **Defect condition:** Sections of the initial URLA were incomplete and/or were inaccurate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 43, 44
- **Severity:** Critical
- **Machine checks:** initial URLA per-section completeness + signatures
- **Stays human:** 'inaccurate'
- **Data needed:** section-level fields
- **Rationale:** BLOCKED ON MISSING FIXTURE (decision 014), not a rule-clarity problem: As #24 for initial URLA.
- **SME:** ☐ agree ☐ correct: ______

### G40 — O-FHA-15141 [O-FHA]
- **Q:** Were all initial Uniform Residential Loan Application requirements met?
- **Defect condition:** Sections of the initial URLA were incomplete, inaccurate and/or was not signed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 57
- **Severity:** Critical
- **Machine checks:** as #39 (FHA wording variant)
- **Stays human:** 'inaccurate'
- **Data needed:** as #39
- **Rationale:** BLOCKED ON MISSING FIXTURE (decision 014), not a rule-clarity problem: Same as #39.
- **SME:** ☐ agree ☐ correct: ______

### G42 — O-FRD-14076 [O-FRD]
- **Q:** Were all initial Uniform Residential Loan Application requirements met?
- **Defect condition:** The file did not include a fully completed Supplemental Consumer Information Form (Form 1103)
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 70
- **Severity:** Critical
- **Machine checks:** Form 1103 (SCIF) presence
- **Stays human:** 'fully completed'
- **Data needed:** doc type + its fields
- **Rationale:** BLOCKED ON MISSING FIXTURE (decision 014), not a rule-clarity problem: Presence easy; completeness needs field list.
- **SME:** ☐ agree ☐ correct: ______

### G47 — O-FNM-15303 [O-FNM]
- **Q:** Were all initial Uniform Residential Loan Application requirements met?
- **Defect condition:** The file did not include a fully completed Supplemental Consumer Information Form (Form 1103)
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 69, 1709
- **Severity:** Major
- **Machine checks:** as #42 (FNM variant)
- **Stays human:** 'fully completed'
- **Data needed:** as #42
- **Rationale:** BLOCKED ON MISSING FIXTURE (decision 014), not a rule-clarity problem: Same as #42.
- **Guide candidate:** C1-2-01 — General Information on Delivering Loan Data and Documents (PDF p.947)
- **Guide candidate:** C2-2-03 — General Information on Whole Loan Purchasing Policies (PDF p.984)
- **Guide candidate:** A1-1-01 — Application and Approval of Seller/Servicer (PDF p.20)
- **SME:** ☐ agree ☐ correct: ______

### G49 — O-FNM-16691, O-FRD-16692 [O-FNM/O-FRD]
- **Q:** Were application disclosure requirements met?
- **Defect condition:** A disclosure outlining the ROV process at the time of loan application was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 46, 47
- **Severity:** Critical
- **Machine checks:** ROV-process disclosure presence at application
- **Data needed:** ROV disclosure doc type + date
- **Rationale:** BLOCKED ON MISSING FIXTURE (decision 014), not a rule-clarity problem: New requirement; guide topic retrievable for citation.
- **Guide candidate:** C2-2-05 — Whole Loan Purchasing Process (PDF p.987)
- **Guide candidate:** A1-1-01 — Application and Approval of Seller/Servicer (PDF p.20)
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **SME:** ☐ agree ☐ correct: ______

## RED

### G03 — O-CFPB-14500 [GENERIC]
- **Q:** (Best Practice) Were all Limited English Proficiency (LEP) requirements met?_x000D_
- **Defect condition:** (Best Practice) Standard/approved translated docs not issued based on the applicant(s) LEP pref.
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 67
- **Severity:** Minor
- **Stays human:** whether translated docs matched the applicant's LEP preference
- **Rationale:** Depends on shop practice and preference nuance — reviewer judgment.
- **Guide candidate:** A2-2-04 — Limited Waiver and Enforcement Relief of Representations and Warranties (PDF p.38)
- **Guide candidate:** A2-2-05 — Invalidation of Limited Waiver of Representations and Warranties (PDF p.44)
- **Guide candidate:** A4-1-04 — Submission of Irrevocable Limited Powers of Attorney (PDF p.164)
- **SME:** ☐ agree ☐ correct: ______

### G07 — Final URLA [GENERIC]
- **Q:** Have all sections of the Final 1003 been completed and accurate?
- **Defect condition:** Discrepancies in the file not explained or supporting docs provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 10
- **Severity:** Major
- **Stays human:** file-wide 'discrepancies not explained' sweep
- **Rationale:** Open-ended cross-file judgment; specific discrepancies belong to specific checks.
- **Guide candidate:** B4-1.3-02 — Subject and Contract Sections of the Appraisal Report (PDF p.570)
- **Guide candidate:** D2-1-02 — Fannie Mae QC File Request and Submission Requirements (PDF p.1078)
- **SME:** ☐ agree ☐ correct: ______

### G11 — O-VA-15711 [O-VA]
- **Q:** Were all application disclosure requirements met?
- **Defect condition:** All disclosures (as required) have not been completed accurately & signed per guidelines
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 73, 74
- **Severity:** Major
- **Stays human:** catch-all 'all disclosures per guidelines'
- **Rationale:** Needs SME decomposition into enumerable VA disclosures before any automation.
- **SME:** ☐ agree ☐ correct: ______

### G23 — O-FHA-15293, O-RHS-15627, O-VA-14259 [O-FHA/O-RHS/O-VA]
- **Q:** Were all final Uniform Residential Loan Application requirements met?
- **Defect condition:** It appears the borr needed more space to complete the URLA & a continuation sheet not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 25, 27, 28
- **Severity:** Critical/Major
- **Stays human:** 'appears the borrower needed more space'
- **Rationale:** Inherently a judgment about handwriting/space; route to reviewer.
- **SME:** ☐ agree ☐ correct: ______

### G25 — O-FRD-14083 [O-FRD]
- **Q:** Were all final Uniform Residential Loan Application requirements met?
- **Defect condition:** The borrower needed more space to complete the URLA & a continuation sheet was not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 54
- **Severity:** Major
- **Stays human:** same 'needed more space' judgment
- **Rationale:** As #23.
- **SME:** ☐ agree ☐ correct: ______

### G32 — O-FNM-15304 [O-FNM]
- **Q:** Were all final Uniform Residential Loan Application requirements met?
- **Defect condition:** It appears the borr needed more space to complete the URLA & a continuation sheet not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 26
- **Severity:** Major
- **Stays human:** 'needed more space' judgment (FNM variant)
- **Rationale:** As #23.
- **Guide candidate:** A1-1-01 — Application and Approval of Seller/Servicer (PDF p.20)
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **SME:** ☐ agree ☐ correct: ______

### G37 — O-FHA-15141, O-RHS-15626, O-VA-14253 [O-FHA/O-RHS/O-VA]
- **Q:** Were all initial Uniform Residential Loan Application requirements met?
- **Defect condition:** It appears the borr needed more space to complete the URLA & a continuation sheet not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 52, 55, 56
- **Severity:** Critical/Major
- **Stays human:** 'needed more space' judgment (initial)
- **Rationale:** As #23.
- **SME:** ☐ agree ☐ correct: ______

### G41 — O-FRD-14076 [O-FRD]
- **Q:** Were all initial Uniform Residential Loan Application requirements met?
- **Defect condition:** The borrower needed more space to complete the URLA & a continuation sheet was not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 53
- **Severity:** Major
- **Stays human:** 'needed more space' judgment (FRD initial)
- **Rationale:** As #23.
- **SME:** ☐ agree ☐ correct: ______

## NOT_A_CHECK

### G04 — O-CFPB-14500 [GENERIC]
- **Q:** (Best Practice) Were all Limited English Proficiency (LEP) requirements met?_x000D_
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 81, 82
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** ☐ agree ☐ correct: ______

### G06 — CIP DATA POINTS [GENERIC]
- **Q:** Are the 4 Customer Identification Program (CIP) data points provided in file:  Name, Physical property address, DOB, SS#/Tax ID?
- **Defect condition:** Yes, all CIP data points have been provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 75
- **Rationale:** Pass answer option.
- **SME:** ☐ agree ☐ correct: ______

### G09 — Final URLA [GENERIC]
- **Q:** Have all sections of the Final 1003 been completed and accurate?
- **Defect condition:** Yes, all sections of the final 1003 are complete and accurate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 76
- **Rationale:** Pass answer option.
- **SME:** ☐ agree ☐ correct: ______

### G10 — O-CFPB-14499 [GENERIC]
- **Q:** Is one or more consumers in the transaction a Limited English Proficient (LEP) individual, meaning an individual who does not speak English as their primary language and has a limited ability to read, speak, write, or understand English?_x000D_
- **Defect condition:** No
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 79, 80
- **Rationale:** Screening answer option (LEP applicability), not a defect.
- **SME:** ☐ agree ☐ correct: ______

### G19 — O-FHA-15140 [O-FHA]
- **Q:** Were all application disclosure requirements met?
- **Defect condition:** Yes, all application disclosure  requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 83
- **Rationale:** Pass answer option.
- **SME:** ☐ agree ☐ correct: ______

### G20 — O-VA-15711 [O-VA]
- **Q:** Were all application disclosure requirements met?
- **Defect condition:** Yes, all application disclosure requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 99
- **Rationale:** Pass answer option.
- **SME:** ☐ agree ☐ correct: ______

### G29 — O-FHA-15293, O-FRD-14083, O-RHS-15627, O-VA-14259 [O-FHA/O-FRD/O-RHS/O-VA]
- **Q:** Were all final Uniform Residential Loan Application requirements met?
- **Defect condition:** Yes, all final Uniform Residential Loan Application requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 86, 92, 96, 98
- **Rationale:** Pass answer option.
- **SME:** ☐ agree ☐ correct: ______

### G34 — O-FNM-15304 [O-FNM]
- **Q:** Were all final Uniform Residential Loan Application requirements met?
- **Defect condition:** Yes, all final Uniform Residential Loan Application requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 88
- **Rationale:** Pass answer option.
- **SME:** ☐ agree ☐ correct: ______

### G38 — O-FHA-15141 [O-FHA]
- **Q:** Were all initial Uniform Residential Loan Application requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 84, 85
- **Rationale:** N-A answer option.
- **SME:** ☐ agree ☐ correct: ______

### G46 — O-FRD-14076, O-RHS-15626, O-VA-14253 [O-FRD/O-RHS/O-VA]
- **Q:** Were all initial Uniform Residential Loan Application requirements met?
- **Defect condition:** Yes, all initial Uniform Residential Loan Application requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 91, 95, 97
- **Rationale:** Pass answer option.
- **SME:** ☐ agree ☐ correct: ______

### G48 — O-FNM-15303 [O-FNM]
- **Q:** Were all initial Uniform Residential Loan Application requirements met?
- **Defect condition:** Yes, all initial Uniform Residential Loan Application requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 87, 1816
- **Rationale:** Pass answer option.
- **SME:** ☐ agree ☐ correct: ______

### G50 — O-FNM-16691, O-FRD-16692 [O-FNM/O-FRD]
- **Q:** Were application disclosure requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 89, 90, 93, 94
- **Rationale:** N-A answer option.
- **SME:** ☐ agree ☐ correct: ______

### G54 — O-BP-14663 [GENERIC]
- **Q:** Were the following non-regulatory customary disclosures provided to the applicant in the initial disclosure package?_x000D_
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 77, 78
- **Rationale:** N-A answer option.
- **SME:** ☐ agree ☐ correct: ______

