# SME Review Packet — underwriting-review block triage

**466 rules / 461 unique (question, condition) groups.** Every classification
below is a *proposal* pending your review — mark each check agree / correct.
Bins: GREEN = automatable now · YELLOW = automatable after data/guide work ·
RED = stays human · NOT_A_CHECK = pass/N-A answer option, not a defect rule.

**Source workbook:** `PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv` — row numbers below are Excel-style
(header = row 1), so you can open the sheet and jump straight to each rule.

**Note on this block vs the two prior triages:** dedup collapse here is the smallest of the three (466 rules -> 461 groups, ~1.01x, vs asset-verification's ~1.02x and application-verification's ~1.5x). Two shapes are already registered against this block in amq_compiler.py's MAPPED_SHAPES (ResidualIncomeShape, RatioWaiverShape) but both are wired to ZERO exception codes — this triage explicitly checked whether any of the 461 groups here describe the same real condition either shape already checks. Neither survived verification — see the REJECTED candidates note below and decision 022 for the full reasoning. Given the scale (366 groups not mechanically resolved by amq_compiler.py's own eval_class), classification below uses a family-regex engine built from a full read of every group's untruncated text, not a hand-typed dict per group — the `family` tag on each group names which regex matched, and OVERRIDES groups a small hand-classified residual.

## ResidualIncomeShape / RatioWaiverShape — checked, NOT wired (negative result)

- **ResidualIncomeShape (CHK-UND-001)** checks `doc_present_residual_income_worksheet == false AND mismo_mortgage_type == "VA"`. Closest candidate: **G289 (O-VA-00655)** — tests a materially different, compound condition (DTI>41% OR residual income below minimum, AND whether the underwriter separately justified/documented compensating factors) — not a worksheet-presence fact. REJECTED.
- **RatioWaiverShape (CHK-UND-002)** checks `piti_ratio > piti_guideline AND dti_ratio > dti_guideline AND usda_ratio_waiver_in_file == false`, with both guideline values sourced only from `usda_ratio_waiver_doc` (loan 05/USDA only). Closest candidates: **G106 (O-RHS-02848, PITI 34% ceiling), G350 (O-FHA-00606, comp factors not noted on 92900-LT), G343 (O-RHS-02852, manual UW front-ratio 29%)** — each tests a different condition (a flat 34%/29% ceiling, or FHA/RHS-specific compensating-factors documentation on a form this pilot doesn't have) and, structurally, none of them are USDA/RHS loans whose waiver worksheet would populate `piti_guideline`/`dti_guideline` in the first place. REJECTED.

## Headline

| Bin | Groups | Rules | % of defect groups |
|---|---|---|---|
| GREEN | 6 | 6 | 2% |
| YELLOW | 342 | 344 | 92% |
| RED | 24 | 24 | 6% |
| NOT_A_CHECK | 89 | 92 | — |

## GREEN

### G113 — O-FHA-50703 [O-FHA]
- **Q:** Were all Title Insurance and title requirements met including company ratings?
- **Defect condition:** A final title policy, attorney’s title opinion or cert meeting FHA’s requirements not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5069
- **Severity:** Major
- **Machine checks:** already-mapped/auto-compiled by amq_compiler.py: doc-presence check on title_commitment
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier (the exception text matches 'not in file/missing/not provided' and names a mappable document type already in the extraction contract) -- already works.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G123 — O-FHA-50642 [O-FHA]
- **Q:** Were all Title Insurance and title requirements met including company ratings?
- **Defect condition:** Title commitment not in the file or does not meet FHA requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5310
- **Severity:** Critical
- **Machine checks:** already-mapped/auto-compiled by amq_compiler.py: doc-presence check on title_commitment
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier (the exception text matches 'not in file/missing/not provided' and names a mappable document type already in the extraction contract) -- already works.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G139 — O-FRD-55390 [O-FRD]
- **Q:** Were all Title Insurance requirements met including company ratings?
- **Defect condition:** Title lien search not in file for co-op recognized as personal property not requiring a title policy
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5006
- **Severity:** Critical
- **Machine checks:** already-mapped/auto-compiled by amq_compiler.py: doc-presence check on title_commitment
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier (the exception text matches 'not in file/missing/not provided' and names a mappable document type already in the extraction contract) -- already works.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G167 — O-VA-56141 [O-VA]
- **Q:** Were all Veteran's eligibility requirements met?
- **Defect condition:** Most up-to-date version of Form 26-1880, is not in the file or is incomplete, incorrect or unsigned
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5376
- **Severity:** Critical
- **Machine checks:** already-mapped/auto-compiled by amq_compiler.py: doc-presence check on va_coe
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier (the exception text matches 'not in file/missing/not provided' and names a mappable document type already in the extraction contract) -- already works. CAVEAT (checked, not assumed): amq_compiler.py's own keyword classifier mapped this via the 'certificate of eligibility' phrase in the exception text to the va_coe doc type -- but VA Form 26-1880 is the REQUEST form for a COE, not the COE itself. Same class of keyword-collision latent bug decision 014 flagged for 'initial application' -> final_1003. Already auto-compiled and working as a doc-presence check either way (va_coe is absent for the other 4 loans regardless), so still GREEN, but the target document identity is not a perfect fidelity match.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G169 — O-VA-00081 [O-VA]
- **Q:** Were all Veteran's eligibility requirements met?
- **Defect condition:** The Certificate of Eligibility is not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4995
- **Severity:** Critical
- **Machine checks:** already-mapped/auto-compiled by amq_compiler.py: doc-presence check on va_coe
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier (the exception text matches 'not in file/missing/not provided' and names a mappable document type already in the extraction contract) -- already works.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G255 — O-VA-55826 [O-VA]
- **Q:** Were all fees and charges requirements met?
- **Defect condition:** No itemized invoice for Vet paid wood destroying pest inspection fees &/or repairs as per the NOV
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5228
- **Severity:** Critical
- **Machine checks:** already-mapped/auto-compiled by amq_compiler.py: doc-presence check on va_nov
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier (the exception text matches 'not in file/missing/not provided' and names a mappable document type already in the extraction contract) -- already works. CAVEAT (checked, not assumed): the missing item this row actually names is an itemized pest-inspection invoice, not the NOV itself -- amq_compiler.py's keyword classifier matched 'NOV' in the exception text and pointed the doc-presence check at va_nov. The check will correctly report NOT_EVALUATED/present based on va_nov's presence, which is a coincidentally-adjacent but not textually-precise target.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

## YELLOW

### G001 — O-FHA-00077 [O-FHA]
- **Q:** Did the CAIVRS and/or LDP/GSA documentation meet all requirements?
- **Defect condition:** LDP/GSA lists and SAM were not checked and/or determination not noted on form HUD-92900-LT
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5121
- **Severity:** Critical
- **Data needed:** caivrs doc type already exists in DOC_TYPES and is present for loan 02 only (05_CAIVRS_LDP_GSA.pdf) but has zero FIELD_SPECS/FACT_SPECS entries -- no 'clear'/'hit' fact is extracted from it, and no loan 01/03/04/05 has this document at all
- **Rationale:** Per decision 016's own precedent, CAIVRS/LDP/GSA screening is treated as an ordinary point-in-time screenshot document (not a live-registry Bucket-C lookup like NMLS) -- ready for Bucket-B-style field extraction once deepened, but genuinely absent as a fixture for 4 of 5 loans.
- **Family:** caivrs_ldp_gsa
- **SME:** [ ] agree [ ] correct: ______

### G002 — O-FHA-50002 [O-FHA]
- **Q:** Did the CAIVRS and/or LDP/GSA documentation meet all requirements?
- **Defect condition:** One or more of the interested parties appeared on the GSA list
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5077
- **Severity:** Critical
- **Data needed:** caivrs doc type already exists in DOC_TYPES and is present for loan 02 only (05_CAIVRS_LDP_GSA.pdf) but has zero FIELD_SPECS/FACT_SPECS entries -- no 'clear'/'hit' fact is extracted from it, and no loan 01/03/04/05 has this document at all
- **Rationale:** Per decision 016's own precedent, CAIVRS/LDP/GSA screening is treated as an ordinary point-in-time screenshot document (not a live-registry Bucket-C lookup like NMLS) -- ready for Bucket-B-style field extraction once deepened, but genuinely absent as a fixture for 4 of 5 loans.
- **Family:** caivrs_ldp_gsa
- **SME:** [ ] agree [ ] correct: ______

### G003 — O-FHA-50001 [O-FHA]
- **Q:** Did the CAIVRS and/or LDP/GSA documentation meet all requirements?
- **Defect condition:** One or more of the interested parties appeared on the LDP list
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5136
- **Severity:** Critical
- **Data needed:** caivrs doc type already exists in DOC_TYPES and is present for loan 02 only (05_CAIVRS_LDP_GSA.pdf) but has zero FIELD_SPECS/FACT_SPECS entries -- no 'clear'/'hit' fact is extracted from it, and no loan 01/03/04/05 has this document at all
- **Rationale:** Per decision 016's own precedent, CAIVRS/LDP/GSA screening is treated as an ordinary point-in-time screenshot document (not a live-registry Bucket-C lookup like NMLS) -- ready for Bucket-B-style field extraction once deepened, but genuinely absent as a fixture for 4 of 5 loans.
- **Family:** caivrs_ldp_gsa
- **SME:** [ ] agree [ ] correct: ______

### G004 — O-FRD-02575 [O-FHA]
- **Q:** Did the CAIVRS and/or LDP/GSA documentation meet all requirements?
- **Defect condition:** Required parties per their specific role in the loan not checked against the FHLMC Exclusionary List
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5071
- **Severity:** Major
- **Data needed:** caivrs doc type already exists in DOC_TYPES and is present for loan 02 only (05_CAIVRS_LDP_GSA.pdf) but has zero FIELD_SPECS/FACT_SPECS entries -- no 'clear'/'hit' fact is extracted from it, and no loan 01/03/04/05 has this document at all
- **Rationale:** Per decision 016's own precedent, CAIVRS/LDP/GSA screening is treated as an ordinary point-in-time screenshot document (not a live-registry Bucket-C lookup like NMLS) -- ready for Bucket-B-style field extraction once deepened, but genuinely absent as a fixture for 4 of 5 loans.
- **Family:** caivrs_ldp_gsa
- **SME:** [ ] agree [ ] correct: ______

### G005 — O-FHA-00076 [O-FHA]
- **Q:** Did the CAIVRS and/or LDP/GSA documentation meet all requirements?
- **Defect condition:** The CAIVRS was not examined to determine whether any party to the transaction appears on either list
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4989
- **Severity:** Critical
- **Data needed:** caivrs doc type already exists in DOC_TYPES and is present for loan 02 only (05_CAIVRS_LDP_GSA.pdf) but has zero FIELD_SPECS/FACT_SPECS entries -- no 'clear'/'hit' fact is extracted from it, and no loan 01/03/04/05 has this document at all
- **Rationale:** Per decision 016's own precedent, CAIVRS/LDP/GSA screening is treated as an ordinary point-in-time screenshot document (not a live-registry Bucket-C lookup like NMLS) -- ready for Bucket-B-style field extraction once deepened, but genuinely absent as a fixture for 4 of 5 loans.
- **Family:** caivrs_ldp_gsa
- **SME:** [ ] agree [ ] correct: ______

### G006 — O-FHA-52872 [O-FHA]
- **Q:** Did the CAIVRS and/or LDP/GSA documentation meet all requirements?
- **Defect condition:** The approving underwriter was not Direct Endorsement (DE) certified
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5059
- **Severity:** Critical
- **Data needed:** caivrs doc type already exists in DOC_TYPES and is present for loan 02 only (05_CAIVRS_LDP_GSA.pdf) but has zero FIELD_SPECS/FACT_SPECS entries -- no 'clear'/'hit' fact is extracted from it, and no loan 01/03/04/05 has this document at all
- **Rationale:** Per decision 016's own precedent, CAIVRS/LDP/GSA screening is treated as an ordinary point-in-time screenshot document (not a live-registry Bucket-C lookup like NMLS) -- ready for Bucket-B-style field extraction once deepened, but genuinely absent as a fixture for 4 of 5 loans.
- **Family:** caivrs_ldp_gsa
- **SME:** [ ] agree [ ] correct: ______

### G008 — DUFindings-A [GENERIC]
- **Q:** Do the final AUS findings match all other documentation in the file?
- **Defect condition:** Cash to close on the final AUS doesn't match final 1003 or 1008
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5344, 5345, 5346, 5347, 5348, 5349, 5350
- **Severity:** Major
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **Guide candidate:** A3-3-03 — Other Servicing Arrangements (PDF p.131)
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **Guide candidate:** B2-1.3-03 — Cash-Out Reﬁnance Transactions (PDF p.197)
- **SME:** [ ] agree [ ] correct: ______

### G010 — Property Type/Appr [GENERIC]
- **Q:** Do the final AUS findings match all other documentation in the file?
- **Defect condition:** The property type on the final AUS does not match the property type listed on the appraisal
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5245
- **Severity:** Major
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **Guide candidate:** B4-1.4-07 — Mixed-Use Property Appraisal Requirements (PDF p.626)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **Guide candidate:** A3-3-03 — Other Servicing Arrangements (PDF p.131)
- **SME:** [ ] agree [ ] correct: ______

### G011 — Sales Con-TransFees [GENERIC]
- **Q:** Does the sales contract makes reference to a private transfer, reconveyance, recovery, capital recovery or resale fees?
- **Defect condition:** Contract shows a private transfer, reconveyance, recovery/capital, or resale fee & is not cleared
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5276
- **Severity:** Major
- **Data needed:** sales contract document (this pilot has NO purchase/sales contract document type in any of the 5 synthetic loans -- same systemic gap flagged in asset-verification's EMD family, decision 017)
- **Rationale:** Same missing-purchase-contract gap as asset-verification's earnest-money-deposit family (G040/G081/G084/G086, decision 017).
- **Family:** private_transfer_fee_contract
- **Guide candidate:** A2-3.1-01 — Lender Breach of Contract (PDF p.56)
- **Guide candidate:** A2-3.3-01 — Compensatory Fees (PDF p.76)
- **Guide candidate:** B2-1.3-05 — Payoﬀ of Installment Land Contract Requirements (PDF p.205)
- **SME:** [ ] agree [ ] correct: ______

### G013 — CompFactors [GENERIC]
- **Q:** Have all program guidelines/overlays been met?
- **Defect condition:** Citizens FHA/VA overlay exception appr’d is missing commentary on FHA transmittal/VA loan analysis
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5062, 5063
- **Severity:** Critical
- **Data needed:** VA Form 26-6393 (VA Loan Analysis) -- not in any synthetic loan folder
- **Rationale:** Niche VA underwriting-analysis form; loan 03 (the pilot's only VA loan) does not contain this document.
- **Family:** va_26_6393
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** A2-4.1-01 — Establishing Loan Files (PDF p.78)
- **SME:** [ ] agree [ ] correct: ______

### G014 — QC Exclusionary List [GENERIC]
- **Q:** Have all program guidelines/overlays been met?
- **Defect condition:** No, all parties were not checked against the exclusionary list or other applicable lists
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5251
- **Severity:** Major
- **Data needed:** OFAC SDN list / Freddie Mac Exclusionary List / FHFA Suspended Counterparty Program / BSA-AML screening record (no such document or fixture exists in any of the 5 synthetic loans)
- **Rationale:** Distinct from the CAIVRS/LDP/GSA family above -- no per-loan screenshot document for these specific lists exists anywhere in the corpus (not even one instance), a genuine Bucket-A fixture gap, not merely thin extraction.
- **Family:** ofac_exclusionary
- **Guide candidate:** A3-3-03 — Other Servicing Arrangements (PDF p.131)
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **Guide candidate:** B3-3.4-14 — Section 8 Housing Choice Voucher Homeownership Program Payments (PDF p.370)
- **SME:** [ ] agree [ ] correct: ______

### G018 — Tandem [GENERIC]
- **Q:** Have all program guidelines/overlays been met?
- **Defect condition:** The documentation in the tandem file does not match and/or is missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5306
- **Severity:** Critical
- **Data needed:** a 'tandem file' (co-issued/companion loan file) concept -- not modeled; no such document or cross-loan-file relationship exists in this pilot
- **Rationale:** Niche cross-file consistency check, absent from the corpus.
- **Family:** tandem_file
- **Guide candidate:** B3-2-04 — DU Documentation Requirements (PDF p.305)
- **Guide candidate:** B3-3.1-02 — Tax Return and Transcript Documentation Requirements (PDF p.320)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **SME:** [ ] agree [ ] correct: ______

### G019 — DUValid-A [GENERIC]
- **Q:** Have conditions required by DU been met?
- **Defect condition:** Condition for second job documentation when no second job applicable was not cleared
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5036, 5037, 5038, 5039, 5040, 5041, 5042
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **Guide candidate:** D1-3-02 — Lender Post-Closing Quality Control Review of Approval Conditions, Underwriting Decisions, Data, and Documentation (PDF p.1068)
- **Guide candidate:** B3-2-04 — DU Documentation Requirements (PDF p.305)
- **Guide candidate:** B3-3.1-02 — Tax Return and Transcript Documentation Requirements (PDF p.320)
- **SME:** [ ] agree [ ] correct: ______

### G020 — DU Secured Funds [GENERIC]
- **Q:** Have conditions required by DU been met?
- **Defect condition:** Secured funds were not entered correctly into DU and/or they were not identified separately
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5282
- **Severity:** Major
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **Guide candidate:** B3-4.3-15 — Borrowed Funds Secured by an Asset (PDF p.458)
- **Guide candidate:** B3-4.2-04 — Pooled Savings (Community Savings Funds) (PDF p.438)
- **Guide candidate:** B3-4.3-01 — Stocks, Stock Options, Bonds, and Mutual Funds (PDF p.439)
- **SME:** [ ] agree [ ] correct: ______

### G021 — CoSignDebt [GENERIC]
- **Q:** Have conditions required by DU been met?
- **Defect condition:** The declarations indicate borrower is a co-signor on a debt and unable to confirm this was addressed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5080
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **Guide candidate:** B2-2-01 — General Borrower Eligibility Requirements (PDF p.241)
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **Guide candidate:** B2-2-03 — Multiple Financed Properties for the Same Borrower (PDF p.244)
- **SME:** [ ] agree [ ] correct: ______

### G023 — O-FHA-50655 [O-FHA]
- **Q:** In a purchase transaction, were all requirements met?
- **Defect condition:** All req's where the subject is being resold between 91 -180 days after the last acquisition not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5265
- **Severity:** Critical
- **Data needed:** prior-acquisition/resale date fields (seller's acquisition date vs resale date) -- not modeled; no purchase-contract or prior-deed document exists in the corpus
- **Rationale:** FHA property-flipping family (91-180-day resale window); same missing-purchase-contract gap flagged in asset-verification's EMD family (decision 017).
- **Family:** override
- **SME:** [ ] agree [ ] correct: ______

### G024 — O-FHA-00596 [O-FHA]
- **Q:** In a purchase transaction, were all requirements met?
- **Defect condition:** Documentation the transaction does not violate HUD's rule against property flipping was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5223
- **Severity:** Critical
- **Data needed:** seller-of-record / property-flipping documentation -- not modeled
- **Rationale:** Same FHA property-flipping family as G023/G027.
- **Family:** override
- **SME:** [ ] agree [ ] correct: ______

### G027 — O-FHA-50654 [O-FHA]
- **Q:** In a purchase transaction, were all requirements met?
- **Defect condition:** The subject property is being resold within 90 days of the seller's acquisition
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4954
- **Severity:** Critical
- **Data needed:** seller's acquisition date vs resale date (90-day window) -- not modeled
- **Rationale:** Same FHA property-flipping family as G023/G024.
- **Family:** override
- **SME:** [ ] agree [ ] correct: ______

### G029 — O-FNM-00715-C [GENERIC]
- **Q:** Is the final 1008 Transmittal Summary accurate & complete?
- **Defect condition:** The appraiser name and/or license # field is incomplete or incorrect
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5352, 5353, 5354, 5355, 5356
- **Severity:** Major
- **Data needed:** 1008/1077 Uniform Underwriting and Transmittal Summary -- no such document/field exists for any agency in this pilot
- **Rationale:** A distinct transmittal-summary form from every doc type this pilot currently parses; appears across FNM/FRD/RHS variants of the same underlying gap.
- **Family:** form_1008_1077
- **Guide candidate:** A2-5-01 — Fannie Mae Trade Name and Trademarks (PDF p.102)
- **Guide candidate:** B4-1.1-03 — Appraiser Selection Criteria (PDF p.538)
- **SME:** [ ] agree [ ] correct: ______

### G030 — O-FNM-00715 [GENERIC]
- **Q:** Is the final 1008 Transmittal Summary accurate & complete?
- **Defect condition:** The final 1008 is incorrect or incomplete
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5357, 5358
- **Severity:** Major
- **Data needed:** 1008/1077 Uniform Underwriting and Transmittal Summary -- no such document/field exists for any agency in this pilot
- **Rationale:** A distinct transmittal-summary form from every doc type this pilot currently parses; appears across FNM/FRD/RHS variants of the same underlying gap.
- **Family:** form_1008_1077
- **SME:** [ ] agree [ ] correct: ______

### G034 — Adverse Action [GENERIC]
- **Q:** Was a counter-offer made (final terms were less favorable based on initial loan application & price/lock history screen)?
- **Defect condition:** Notice of adverse action/commitment with new terms not found or incorrect
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4961
- **Severity:** Critical
- **Data needed:** adverse-action/incompleteness notice + its mailing/received dates -- not in corpus
- **Rationale:** ECOA compliance-letter family; no such correspondence document exists in any of the 5 loans.
- **Family:** adverse_action_ecoa_notice
- **Guide candidate:** B5-7-02 — High LTV Reﬁnance Underwriting, Documentation, and Collateral Requirements for the New Loan (PDF p.824)
- **Guide candidate:** C2-1.1-03 — Mandatory Commitment Terms, Amounts, Periods and Other Requirements (PDF p.964)
- **Guide candidate:** C2-1.2-03 — Best Eﬀorts Commitment Terms, Amounts, and Other Requirements (PDF p.975)
- **SME:** [ ] agree [ ] correct: ______

### G035 — Dec Screen [GENERIC]
- **Q:** Was a counter-offer made (final terms were less favorable based on initial loan application & price/lock history screen)?
- **Defect condition:** Supplemental decision screen is missing rationale, discussion details and/or date/time stamps
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5022
- **Severity:** Major
- **Data needed:** AUS supplemental-decision-screen rationale/timestamp fields -- ties to the AUS-findings gap (no DU/LPA/GUS export exists in this pilot)
- **Rationale:** Decision-screen audit-trail fact; same underlying AUS-export gap as the aus_findings family, just a different named artifact within it.
- **Family:** override
- **Guide candidate:** A1-1-01 — Application and Approval of Seller/Servicer (PDF p.20)
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **SME:** [ ] agree [ ] correct: ______

### G036 — O-FNM-00184 [O-FNM]
- **Q:** Were DU documentation requirements met?
- **Defect condition:** DU Verifications/Conditions not met for income, assets, credit, &/or level of property fieldwork
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5043
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.4-06 — Employment Related Assets as Qualifying Income (PDF p.358)
- **SME:** [ ] agree [ ] correct: ______

### G037 — O-FNM-50243 [O-FNM]
- **Q:** Were DU documentation requirements met?
- **Defect condition:** Final complete DU UW Findings report &/or final UW Analysis report produced by DU not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5035
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **Guide candidate:** B3-2-11 — DU Underwriting Findings Report (PDF p.316)
- **Guide candidate:** B3-5.3-09 — DU Credit Report Analysis (PDF p.495)
- **Guide candidate:** A4-1-03 — Report of Changes in the Seller/Servicer’s Organization (PDF p.162)
- **SME:** [ ] agree [ ] correct: ______

### G039 — O-FHA-00613 [O-FHA]
- **Q:** Were all AUS specific underwriting requirements met?
- **Defect condition:** Accept/Ineligible-loan approved without clearing ineligibility issues or document the approval basis
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4957
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G040 — O-FHA-00554 [O-FHA]
- **Q:** Were all AUS specific underwriting requirements met?
- **Defect condition:** All of the data elements entered in the AUS were not correct
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4974
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G041 — O-FHA-02324 [O-FHA]
- **Q:** Were all AUS specific underwriting requirements met?
- **Defect condition:** DU Accept however, conditions exist for a downgrade but the loan was not manually underwritten
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4956
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G043 — O-FHA-56983 [O-FHA]
- **Q:** Were all AUS specific underwriting requirements met?
- **Defect condition:** The Section 8 Housing Choice Voucher amount was deducted and is not paid directly to the servicer
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4977
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G044 — O-FHA-56984 [O-FHA]
- **Q:** Were all AUS specific underwriting requirements met?
- **Defect condition:** The abated real estate tax amount was used without meeting documentation & continuance requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4973
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G045 — O-FHA-58946 [O-FHA]
- **Q:** Were all AUS specific underwriting requirements met?
- **Defect condition:** The monthly PITIA did not include all of the applicable housing components
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4976
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G047 — O-FNM-00721 [O-FNM]
- **Q:** Were all Approve/Ineligible, Refer with Caution, or Out of Scope recommendations requirements met?
- **Defect condition:** In a Refer w/ Caution the UW did not follow suggested steps to resubmit or manually UW the loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5258
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **Guide candidate:** B3-2-06 — Approve/Ineligible Recommendations (PDF p.307)
- **Guide candidate:** B3-2-07 — Refer with Caution Recommendations (PDF p.309)
- **Guide candidate:** B3-2-08 — Out of Scope Recommendations (PDF p.311)
- **SME:** [ ] agree [ ] correct: ______

### G049 — O-FNM-50244 [O-FNM]
- **Q:** Were all Approve/Ineligible, Refer with Caution, or Out of Scope recommendations requirements met?
- **Defect condition:** The loan was not manually UW when DU recommendation was "out of scope"
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5220
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **Guide candidate:** B3-2-06 — Approve/Ineligible Recommendations (PDF p.307)
- **Guide candidate:** B3-2-07 — Refer with Caution Recommendations (PDF p.309)
- **Guide candidate:** B3-2-08 — Out of Scope Recommendations (PDF p.311)
- **SME:** [ ] agree [ ] correct: ______

### G050 — O-ECOA-51104 [GENERIC]
- **Q:** Were all ECOA requirements met (part 1)?
- **Defect condition:** A Notice of Incompleteness (NOI) was not mailed within 30 days of the application date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5203
- **Severity:** Critical
- **Data needed:** adverse-action/incompleteness notice + its mailing/received dates -- not in corpus
- **Rationale:** ECOA compliance-letter family; no such correspondence document exists in any of the 5 loans.
- **Family:** adverse_action_ecoa_notice
- **Guide candidate:** A1-1-01 — Application and Approval of Seller/Servicer (PDF p.20)
- **Guide candidate:** B1-1-01 — Contents of the Application Package (PDF p.167)
- **Guide candidate:** B7-3-08 — Mortgagee Clause, Named Insured, and Notice of Cancellation Requirements (PDF p.899)
- **SME:** [ ] agree [ ] correct: ______

### G052 — O-ECOA-00582 [GENERIC]
- **Q:** Were all ECOA requirements met (part 1)?
- **Defect condition:** Applicant was not notified of action taken within 30 days after receiving a completed application
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5201, 5202
- **Severity:** Critical
- **Data needed:** adverse-action/incompleteness notice + its mailing/received dates -- not in corpus
- **Rationale:** ECOA compliance-letter family; no such correspondence document exists in any of the 5 loans.
- **Family:** adverse_action_ecoa_notice
- **Guide candidate:** A1-1-01 — Application and Approval of Seller/Servicer (PDF p.20)
- **Guide candidate:** B1-1-01 — Contents of the Application Package (PDF p.167)
- **SME:** [ ] agree [ ] correct: ______

### G053 — O-ECOA-02035 [GENERIC]
- **Q:** Were all ECOA requirements met (part 1)?
- **Defect condition:** ECOA notice missing reasons for action or disclosure of right to specific reasons within 30 days
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5200
- **Severity:** Critical
- **Data needed:** adverse-action/incompleteness notice + its mailing/received dates -- not in corpus
- **Rationale:** ECOA compliance-letter family; no such correspondence document exists in any of the 5 loans.
- **Family:** adverse_action_ecoa_notice
- **Guide candidate:** B4-1.1-05 — Disclosure of Information to Appraisers (PDF p.543)
- **Guide candidate:** B7-3-08 — Mortgagee Clause, Named Insured, and Notice of Cancellation Requirements (PDF p.899)
- **SME:** [ ] agree [ ] correct: ______

### G062 — O-FNM-54259 [O-FNM]
- **Q:** Were all Fannie Mae AUS requirements met?
- **Defect condition:** 2nd home or investment property not underwritten with DU &/or not an Approve/Eligible recommendation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5280
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** A2-5-01 — Fannie Mae Trade Name and Trademarks (PDF p.102)
- **Guide candidate:** A3-1-01 — Fannie Mae’s Technology Products (PDF p.106)
- **SME:** [ ] agree [ ] correct: ______

### G063 — O-FNM-54260 [O-FNM]
- **Q:** Were all Fannie Mae AUS requirements met?
- **Defect condition:** 2nd home/investment not DU UW & not a high LTV refi w/ SFC 840 manual UW Alt Qualification Path
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5281
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **Guide candidate:** B5-7-03 — High LTV Reﬁnance Alternative Qualiﬁcation Path (PDF p.828)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** A2-5-01 — Fannie Mae Trade Name and Trademarks (PDF p.102)
- **SME:** [ ] agree [ ] correct: ______

### G064 — O-FNM-54338 [O-FNM]
- **Q:** Were all Fannie Mae AUS requirements met?
- **Defect condition:** Automated UW case identifier did not include DU casefile ID in a second home or investment property
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5278
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** A2-5-01 — Fannie Mae Trade Name and Trademarks (PDF p.102)
- **Guide candidate:** A3-1-01 — Fannie Mae’s Technology Products (PDF p.106)
- **SME:** [ ] agree [ ] correct: ______

### G066 — O-RHS-02857 [O-RHS]
- **Q:** Were all Form RD 3555-21 requirements met?
- **Defect condition:** Form RD 3555-21 (Rev. 03-21) is missing, not fully completed &/or not signed by all required parties
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5263
- **Severity:** Critical
- **Data needed:** Form RD 3555-21 (Request for Single Family Housing Loan Guarantee) -- not in corpus
- **Rationale:** USDA guarantee-request form; loan 05 (the pilot's only USDA loan) does not contain this document.
- **Family:** rd_3555_21
- **SME:** [ ] agree [ ] correct: ______

### G068 — O-FRD-58172 [O-FRD]
- **Q:** Were all Freddie Mac Exclusionary List and FHFA Suspended Counterparty Program requirements met?
- **Defect condition:** BSA, Money Laundering Control Act, USA PATRIOT Act & Anti-Money Laundering Act not complied with
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4987
- **Severity:** Critical
- **Data needed:** OFAC SDN list / Freddie Mac Exclusionary List / FHFA Suspended Counterparty Program / BSA-AML screening record (no such document or fixture exists in any of the 5 synthetic loans)
- **Rationale:** Distinct from the CAIVRS/LDP/GSA family above -- no per-loan screenshot document for these specific lists exists anywhere in the corpus (not even one instance), a genuine Bucket-A fixture gap, not merely thin extraction.
- **Family:** ofac_exclusionary
- **SME:** [ ] agree [ ] correct: ______

### G069 — O-FRD-51689 [O-FRD]
- **Q:** Were all Freddie Mac Exclusionary List and FHFA Suspended Counterparty Program requirements met?
- **Defect condition:** Match on the OFAC SDN list, FHLMC not notified w/in 24 hrs & funds not blocked & segregated
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5215
- **Severity:** Critical
- **Data needed:** OFAC SDN list / Freddie Mac Exclusionary List / FHFA Suspended Counterparty Program / BSA-AML screening record (no such document or fixture exists in any of the 5 synthetic loans)
- **Rationale:** Distinct from the CAIVRS/LDP/GSA family above -- no per-loan screenshot document for these specific lists exists anywhere in the corpus (not even one instance), a genuine Bucket-A fixture gap, not merely thin extraction.
- **Family:** ofac_exclusionary
- **SME:** [ ] agree [ ] correct: ______

### G070 — O-FRD-52796 [O-FRD]
- **Q:** Were all Freddie Mac Exclusionary List and FHFA Suspended Counterparty Program requirements met?
- **Defect condition:** No evidence all participants were checked against the FHFA Suspended Counterparty Program list
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5065
- **Severity:** Critical
- **Data needed:** OFAC SDN list / Freddie Mac Exclusionary List / FHFA Suspended Counterparty Program / BSA-AML screening record (no such document or fixture exists in any of the 5 synthetic loans)
- **Rationale:** Distinct from the CAIVRS/LDP/GSA family above -- no per-loan screenshot document for these specific lists exists anywhere in the corpus (not even one instance), a genuine Bucket-A fixture gap, not merely thin extraction.
- **Family:** ofac_exclusionary
- **SME:** [ ] agree [ ] correct: ______

### G071 — O-FRD-02575 [O-FRD]
- **Q:** Were all Freddie Mac Exclusionary List and FHFA Suspended Counterparty Program requirements met?
- **Defect condition:** Required parties per their specific role in the loan not checked against the FHLMC Exclusionary List
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5073
- **Severity:** Major
- **Data needed:** OFAC SDN list / Freddie Mac Exclusionary List / FHFA Suspended Counterparty Program / BSA-AML screening record (no such document or fixture exists in any of the 5 synthetic loans)
- **Rationale:** Distinct from the CAIVRS/LDP/GSA family above -- no per-loan screenshot document for these specific lists exists anywhere in the corpus (not even one instance), a genuine Bucket-A fixture gap, not merely thin extraction.
- **Family:** ofac_exclusionary
- **SME:** [ ] agree [ ] correct: ______

### G073 — O-RHS-02862 [O-RHS]
- **Q:** Were all Guaranteed Underwriting System (GUS) requirements met?
- **Defect condition:** Accept/Eligible status but the loan did not meet all RHS-guarantee requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5083
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G074 — O-RHS-02863 [O-RHS]
- **Q:** Were all Guaranteed Underwriting System (GUS) requirements met?
- **Defect condition:** Accept/Ineligible decision approved without resolving the ineligibility issue & resubmitting to GUS
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5084
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G075 — O-RHS-50533 [O-RHS]
- **Q:** Were all Guaranteed Underwriting System (GUS) requirements met?
- **Defect condition:** Adverse credit omitted rec'd Accept w/out explanation to support omission
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5216
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G076 — O-RHS-57401 [O-RHS]
- **Q:** Were all Guaranteed Underwriting System (GUS) requirements met?
- **Defect condition:** Obligations disclosed by the borr not considered in DTI not listed in GUS & "omitted" as permitted
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5205
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G077 — O-RHS-02864 [O-RHS]
- **Q:** Were all Guaranteed Underwriting System (GUS) requirements met?
- **Defect condition:** Refer w/ Caution was not manually UW &/or no approval compensating factors noted
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5086
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G078 — O-RHS-50534 [O-RHS]
- **Q:** Were all Guaranteed Underwriting System (GUS) requirements met?
- **Defect condition:** The final GUS submission is not in the loan file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5067
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G079 — O-RHS-02865 [O-RHS]
- **Q:** Were all Guaranteed Underwriting System (GUS) requirements met?
- **Defect condition:** There was a material change in data & the loan was not resubmitted for an updated evaluation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5087
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G081 — O-FHA-57396 [O-FHA]
- **Q:** Were all LTV limitations requirements met?_x000D_
- **Defect condition:** LTV limit exceeded in a loan with a non-occupying co-borrower as per relationship &/or property type
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5155
- **Severity:** Critical
- **Data needed:** loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; appraised_value already is)
- **Rationale:** Crisp ratio math once loan_amount is extracted -- appraisal doc already supplies appraised_value, but no field captures the loan amount itself anywhere in FIELD_SPECS.
- **Family:** ltv_cltv_hcltv
- **SME:** [ ] agree [ ] correct: ______

### G082 — O-FHA-53933 [O-FHA]
- **Q:** Were all LTV limitations requirements met?_x000D_
- **Defect condition:** LTV limit exceeded without meeting requirements based on identities of interest relationship type
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5096
- **Severity:** Critical
- **Data needed:** an identity-of-interest relationship fact (borrower's relationship to builder/developer/seller) -- not modeled
- **Rationale:** Niche identity-of-interest family, absent from the corpus.
- **Family:** identity_of_interest_construction
- **SME:** [ ] agree [ ] correct: ______

### G083 — O-FHA-02323 [O-FHA]
- **Q:** Were all LTV limitations requirements met?_x000D_
- **Defect condition:** LTV ratio exceeds the maximum FHA mortgage amount that the applicant is eligible for
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5170
- **Severity:** Critical
- **Data needed:** loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; appraised_value already is)
- **Rationale:** Crisp ratio math once loan_amount is extracted -- appraisal doc already supplies appraised_value, but no field captures the loan amount itself anywhere in FIELD_SPECS.
- **Family:** ltv_cltv_hcltv
- **SME:** [ ] agree [ ] correct: ______

### G085 — O-FHA-57395 [O-FHA]
- **Q:** Were all LTV limitations requirements met?_x000D_
- **Defect condition:** The LTV limitation was exceeded based on the borrower's credit score
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5154
- **Severity:** Critical
- **Data needed:** loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; appraised_value already is)
- **Rationale:** Crisp ratio math once loan_amount is extracted -- appraisal doc already supplies appraised_value, but no field captures the loan amount itself anywhere in FIELD_SPECS.
- **Family:** ltv_cltv_hcltv
- **SME:** [ ] agree [ ] correct: ______

### G086 — O-FRD-50369 [O-FRD]
- **Q:** Were all LTV, TLTV and HTLTV Ratio requirements met?
- **Defect condition:** LTV/TLTV/HTLTV calculated incorrect or info in LPA to calculate is wrong
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5152
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G087 — O-FRD-00683 [O-FRD]
- **Q:** Were all LTV, TLTV and HTLTV Ratio requirements met?
- **Defect condition:** The UW allowed the LTV ratio and total LTV ratio to be higher than Freddie Mac’s maximum
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5171
- **Severity:** Critical
- **Data needed:** loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; appraised_value already is)
- **Rationale:** Crisp ratio math once loan_amount is extracted -- appraisal doc already supplies appraised_value, but no field captures the loan amount itself anywhere in FIELD_SPECS.
- **Family:** ltv_cltv_hcltv
- **SME:** [ ] agree [ ] correct: ______

### G089 — O-VA-00659 [O-VA]
- **Q:** Were all Lender’s Loan Quality Certification requirements met?
- **Defect condition:** Lender’s Loan Quality Certification not in the file or not signed by an appropriate lender official
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5130
- **Severity:** Critical
- **Data needed:** Lender's Loan Quality Certification (VA) -- not in corpus
- **Rationale:** Post-closing VA certification document, absent from loan 03.
- **Family:** loan_quality_cert
- **SME:** [ ] agree [ ] correct: ______

### G091 — O-FRD-50349 [O-FRD]
- **Q:** Were all Loan Product Advisor® use requirements met?
- **Defect condition:** All LPA Feedback messages were not resolved and/or documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4975
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G092 — FRD-Data Integrity [O-FRD]
- **Q:** Were all Loan Product Advisor® use requirements met?
- **Defect condition:** All of the data elements entered in the AUS were not correct
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5147
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G093 — O-FRD-57885 [O-FRD]
- **Q:** Were all Loan Product Advisor® use requirements met?
- **Defect condition:** Borr has multiple loans in process & each doesn't have a separate application & different key number
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5148
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G094 — O-FRD-00048 [O-FRD]
- **Q:** Were all Loan Product Advisor® use requirements met?
- **Defect condition:** Homeownership education req's not met for non-traditional credit borr's or purchase w/ LTV above 95%
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5091
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G095 — O-FRD-00145 [O-FRD]
- **Q:** Were all Loan Product Advisor® use requirements met?
- **Defect condition:** Identifying info not entered in LPA correctly such as name, addresses, SS#, subject property, etc
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5142
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G096 — O-FRD-00573 [O-FRD]
- **Q:** Were all Loan Product Advisor® use requirements met?
- **Defect condition:** Income, assets, debts, or loan amount changed beyond LPA allowable tolerances without resubmission
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5149
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G097 — O-FRD-54819 [O-FRD]
- **Q:** Were all Loan Product Advisor® use requirements met?
- **Defect condition:** The 1008/1077 or similar document was incomplete, incorrect or not in the LPA underwritten file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5150
- **Severity:** Major
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G098 — O-FRD-57883 [O-FRD]
- **Q:** Were all Loan Product Advisor® use requirements met?
- **Defect condition:** The loan was resubmitted to LPA with the original key number that was removed by Freddie Mac
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5269
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G099 — O-FRD-57884 [O-FRD]
- **Q:** Were all Loan Product Advisor® use requirements met?
- **Defect condition:** The key number from a previously closed loan was re-used to process or originate another mortgage
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5271
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G101 — O-FHA-00610 [O-FHA]
- **Q:** Were all Minimum Decision Credit Score (MDCS) requirements met?
- **Defect condition:** The minimum decision credit score (MDCS) utilized was incorrect and/or was less than 500
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5174
- **Severity:** Critical
- **Data needed:** a credit_score field on credit_report (credit_report doc exists in every loan; no score field is extracted today -- only individual tradelines)
- **Rationale:** Bucket-B-style: the document exists, the specific field does not. (Note: this task's own briefing claimed borrower_credit_score/coborrower_credit_score are already extracted -- checked against extract_loan.py directly via grep and found NOT to be true; no such field or credit-inquiry entity exists anywhere in the extractor today.)
- **Family:** credit_score_threshold
- **SME:** [ ] agree [ ] correct: ______

### G102 — O-FHA-00114 [O-FHA]
- **Q:** Were all Minimum Decision Credit Score (MDCS) requirements met?
- **Defect condition:** The minimum decision credit score was not at least 580 to be eligible for maximum financing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5175
- **Severity:** Critical
- **Data needed:** a credit_score field on credit_report (credit_report doc exists in every loan; no score field is extracted today -- only individual tradelines)
- **Rationale:** Bucket-B-style: the document exists, the specific field does not. (Note: this task's own briefing claimed borrower_credit_score/coborrower_credit_score are already extracted -- checked against extract_loan.py directly via grep and found NOT to be true; no such field or credit-inquiry entity exists anywhere in the extractor today.)
- **Family:** credit_score_threshold
- **SME:** [ ] agree [ ] correct: ______

### G104 — O-FHA-50651 [O-FHA]
- **Q:** Were all Nonprofit organizations requirements met?
- **Defect condition:** Borr is a nonprofit not on approved HUD Nonprofit Agency Roster
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5194
- **Severity:** Critical
- **Data needed:** HUD Nonprofit Agency Roster cross-reference -- an external roster lookup, not a loan-file fact (same kind of gap as CAIVRS/LDP/GSA, though evidenced by a roster listing rather than a per-loan screenshot)
- **Rationale:** Nonprofit-borrower-eligibility family; no roster document/fixture exists in this pilot's corpus.
- **Family:** nonprofit_eligibility
- **SME:** [ ] agree [ ] correct: ______

### G106 — O-RHS-02848 [O-RHS]
- **Q:** Were all PITI ratio calculation requirements met?
- **Defect condition:** The PITIA housing ratio was calculated incorrectly and/or exceeded 34% of the repayment income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5232
- **Severity:** Critical
- **Data needed:** a general DTI/PITI(A) derivation from urla_liabilities/tradelines + income fields (piti_ratio/dti_ratio today are extracted ONLY from usda_ratio_waiver_doc, present for loan 05/USDA only)
- **Rationale:** Distinct from the already-wired RatioWaiverShape (CHK-UND-002), which tests a narrower USDA-specific condition (ratio exceeds guideline AND no waiver documented); this family covers general ratio-calculation-accuracy and inclusion-of-specific-debt-type conditions across other agencies -- entities exist (tradelines, urla_liabilities) but no general DTI/PITI aggregation derivation exists yet.
- **Family:** dti_piti_ratio_calc
- **SME:** [ ] agree [ ] correct: ______

### G109 — O-FNM-57897 [O-FNM]
- **Q:** Were all Private Transfer Fee Covenants eligibility requirements met?
- **Defect condition:** Subject has a private transfer fee & is not a shared equity loan with a Note date on or after 7/1/23
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5285
- **Severity:** Critical
- **Data needed:** sales contract document (this pilot has NO purchase/sales contract document type in any of the 5 synthetic loans -- same systemic gap flagged in asset-verification's EMD family, decision 017)
- **Rationale:** Same missing-purchase-contract gap as asset-verification's earnest-money-deposit family (G040/G081/G084/G086, decision 017).
- **Family:** private_transfer_fee_contract
- **Guide candidate:** B5-5.3-03 — Shared Equity Transactions: Eligibility, Underwriting and Collateral Requirements (PDF p.802)
- **Guide candidate:** B2-1.2-03 — Home Equity Combined Loan-to-Value (HCLTV) Ratios (PDF p.182)
- **Guide candidate:** B2-1.5-02 — Loan Eligibility (PDF p.225)
- **SME:** [ ] agree [ ] correct: ______

### G110 — O-FNM-00881 [O-FNM]
- **Q:** Were all Private Transfer Fee Covenants eligibility requirements met?
- **Defect condition:** The subject's private transfer fee is unacceptable under the Private Transfer Fee Regulation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5341
- **Severity:** Critical
- **Data needed:** sales contract document (this pilot has NO purchase/sales contract document type in any of the 5 synthetic loans -- same systemic gap flagged in asset-verification's EMD family, decision 017)
- **Rationale:** Same missing-purchase-contract gap as asset-verification's earnest-money-deposit family (G040/G081/G084/G086, decision 017).
- **Family:** private_transfer_fee_contract
- **Guide candidate:** A2-3.2-02 — Enforcement Relief for Breaches of Certain Representations and Warranties Related to Underwriting and Eligibility (PDF p.65)
- **Guide candidate:** A4-1-01 — Maintaining Seller/Servicer Eligibility (PDF p.151)
- **Guide candidate:** B2-1.5-02 — Loan Eligibility (PDF p.225)
- **SME:** [ ] agree [ ] correct: ______

### G111 — O-FHA-50647 [O-FHA]
- **Q:** Were all SSN validation requirements met?
- **Defect condition:** A service provider not used to verify with the SSA where inconsistencies/multiple SSNs were noted
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5288, 5289
- **Severity:** Critical
- **Data needed:** SSN-discrepancy resolution documentation (SSA verification letter, Form SSA-89/eCBSV) or identity-verification record -- not in corpus
- **Rationale:** SSN-validation family; no such verification record exists in any of the 5 loans.
- **Family:** nonborrowing_spouse_ssn
- **SME:** [ ] agree [ ] correct: ______

### G114 — O-VA-51729 [O-VA]
- **Q:** Were all Title Insurance and title requirements met including company ratings?
- **Defect condition:** All req's not met for a loan that includes a beneficial interest in a revocable Family Living Trust
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5272
- **Severity:** Critical
- **Data needed:** Living Trust Agreement / inter-vivos-revocable-trust documentation -- not in corpus
- **Rationale:** None of the 5 synthetic loans involves a trust-held title; niche fixture gap.
- **Family:** living_trust
- **SME:** [ ] agree [ ] correct: ______

### G115 — O-VA-51476 [O-VA]
- **Q:** Were all Title Insurance and title requirements met including company ratings?
- **Defect condition:** An encroachment was identified on the subject or neighboring property without an easement
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5244
- **Severity:** Critical
- **Data needed:** specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- **Rationale:** Title-family YELLOW: the title_commitment doc type exists but is thin (one field), and several of these rows describe an attorney's title opinion letter, a distinct document type not modeled at all.
- **Family:** title_general
- **SME:** [ ] agree [ ] correct: ______

### G116 — O-FHA-54829 [O-FHA]
- **Q:** Were all Title Insurance and title requirements met including company ratings?
- **Defect condition:** At least one borrower obligated on the Note was not on the title
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4986
- **Severity:** Critical
- **Data needed:** specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- **Rationale:** Title-family YELLOW: the title_commitment doc type exists but is thin (one field), and several of these rows describe an attorney's title opinion letter, a distinct document type not modeled at all.
- **Family:** title_general
- **SME:** [ ] agree [ ] correct: ______

### G117 — O-FHA-50704 [O-FHA]
- **Q:** Were all Title Insurance and title requirements met including company ratings?
- **Defect condition:** Exceptions were discovered during the title search not covered by the General Waiver
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5319
- **Severity:** Critical
- **Data needed:** title-exception-vs-NOV cross-reference fields -- not modeled
- **Rationale:** Title/NOV cross-document family, needs new derivation logic on top of two docs that do exist (title_commitment, va_nov).
- **Family:** title_waiver_nov_conditions
- **SME:** [ ] agree [ ] correct: ______

### G118 — O-FHA-50648 [O-FHA]
- **Q:** Were all Title Insurance and title requirements met including company ratings?
- **Defect condition:** Not all occupying/non-occupying borrowers took title in their name or a Living Trust
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5323
- **Severity:** Critical
- **Data needed:** Living Trust Agreement / inter-vivos-revocable-trust documentation -- not in corpus
- **Rationale:** None of the 5 synthetic loans involves a trust-held title; niche fixture gap.
- **Family:** living_trust
- **SME:** [ ] agree [ ] correct: ______

### G119 — O-FHA-50650 [O-FHA]
- **Q:** Were all Title Insurance and title requirements met including company ratings?
- **Defect condition:** Per title, property not free of all liens other than the subject & 2nd liens permitted by FHA
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5131
- **Severity:** Critical
- **Data needed:** specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- **Rationale:** Title-family YELLOW: the title_commitment doc type exists but is thin (one field), and several of these rows describe an attorney's title opinion letter, a distinct document type not modeled at all.
- **Family:** title_general
- **SME:** [ ] agree [ ] correct: ______

### G120 — O-VA-50785 [O-VA]
- **Q:** Were all Title Insurance and title requirements met including company ratings?
- **Defect condition:** The lender required title insurance, however, all applicable requirements not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5334
- **Severity:** Major
- **Data needed:** specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- **Rationale:** Title-family YELLOW: the title_commitment doc type exists but is thin (one field), and several of these rows describe an attorney's title opinion letter, a distinct document type not modeled at all.
- **Family:** title_general
- **SME:** [ ] agree [ ] correct: ______

### G121 — TitleRedFlags [O-FHA/O-VA]
- **Q:** Were all Title Insurance and title requirements met including company ratings?
- **Defect condition:** The loan amount, vesting, proposed insured or other "Red Flags" have not been addressed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5329, 5333
- **Severity:** Major
- **Data needed:** specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- **Rationale:** Title-family YELLOW: the title_commitment doc type exists but is thin (one field), and several of these rows describe an attorney's title opinion letter, a distinct document type not modeled at all.
- **Family:** title_general
- **SME:** [ ] agree [ ] correct: ______

### G122 — Title 90Days [O-FHA/O-VA]
- **Q:** Were all Title Insurance and title requirements met including company ratings?
- **Defect condition:** The title effective date is not within 90-days of the closing date or 180 days for new construction
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5312, 5316
- **Severity:** Critical
- **Data needed:** a title-commitment effective_date field (title_commitment doc exists in loan 01; only title_vesting_commitment is currently extracted from it)
- **Rationale:** Crisp date-math once the field exists -- Bucket-B-style, same document, new field.
- **Family:** title_effective_date_90day
- **SME:** [ ] agree [ ] correct: ______

### G124 — O-VA-50786 [O-VA]
- **Q:** Were all Title Insurance and title requirements met including company ratings?
- **Defect condition:** Title has conditions/limitations not on NOV or considered by the appraiser or VA if prior to closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5311
- **Severity:** Critical
- **Data needed:** title-exception-vs-NOV cross-reference fields -- not modeled
- **Rationale:** Title/NOV cross-document family, needs new derivation logic on top of two docs that do exist (title_commitment, va_nov).
- **Family:** title_waiver_nov_conditions
- **SME:** [ ] agree [ ] correct: ______

### G126 — O-RHS-51713 [O-RHS]
- **Q:** Were all Title Insurance and title requirements met?
- **Defect condition:** All Title insurance and title requirements have not been met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5325, 5326
- **Severity:** Critical
- **Data needed:** specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- **Rationale:** Title-family YELLOW: the title_commitment doc type exists but is thin (one field), and several of these rows describe an attorney's title opinion letter, a distinct document type not modeled at all.
- **Family:** title_general
- **SME:** [ ] agree [ ] correct: ______

### G127 — O-RHS-59425 [O-RHS]
- **Q:** Were all Title Insurance and title requirements met?
- **Defect condition:** Attny Opinion Letter not prepared by acceptable attny &/or had exceptions not reviewed and resolved
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5162
- **Severity:** Critical
- **Data needed:** specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- **Rationale:** Title-family YELLOW: the title_commitment doc type exists but is thin (one field), and several of these rows describe an attorney's title opinion letter, a distinct document type not modeled at all.
- **Family:** title_general
- **SME:** [ ] agree [ ] correct: ______

### G128 — O-RHS-50609 [O-RHS]
- **Q:** Were all Title Insurance and title requirements met?
- **Defect condition:** Lender not in 1st lien position or Jr lien exists w/out all req's being met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5135
- **Severity:** Critical
- **Data needed:** a first-lien-position fact on title_commitment (doc exists in loan 01 only; no such field/fact exists today)
- **Rationale:** Bucket-B-adjacent: title_commitment doc type exists but this specific fact isn't extracted; absent entirely for the other 4 loans.
- **Family:** first_lien_position
- **SME:** [ ] agree [ ] correct: ______

### G129 — TitleRedFlags [O-RHS]
- **Q:** Were all Title Insurance and title requirements met?
- **Defect condition:** The loan amount, vesting, proposed insured or other "Red Flags" have not been addressed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5332
- **Severity:** Major
- **Data needed:** specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- **Rationale:** Title-family YELLOW: the title_commitment doc type exists but is thin (one field), and several of these rows describe an attorney's title opinion letter, a distinct document type not modeled at all.
- **Family:** title_general
- **SME:** [ ] agree [ ] correct: ______

### G130 — Title 90Days [O-RHS]
- **Q:** Were all Title Insurance and title requirements met?
- **Defect condition:** The title effective date is not within 90-days of the closing date or 180 days for new construction
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5315
- **Severity:** Critical
- **Data needed:** a title-commitment effective_date field (title_commitment doc exists in loan 01; only title_vesting_commitment is currently extracted from it)
- **Rationale:** Crisp date-math once the field exists -- Bucket-B-style, same document, new field.
- **Family:** title_effective_date_90day
- **SME:** [ ] agree [ ] correct: ______

### G131 — O-RHS-51714 [O-RHS]
- **Q:** Were all Title Insurance and title requirements met?
- **Defect condition:** Title policy amount of protection, insured party is incorrect &/or was written on an incorrect form
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5327
- **Severity:** Critical
- **Data needed:** specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- **Rationale:** Title-family YELLOW: the title_commitment doc type exists but is thin (one field), and several of these rows describe an attorney's title opinion letter, a distinct document type not modeled at all.
- **Family:** title_general
- **SME:** [ ] agree [ ] correct: ______

### G132 — O-RHS-59424 [O-RHS]
- **Q:** Were all Title Insurance and title requirements met?
- **Defect condition:** Title policy did not provide marketable title &/or had title exceptions not reviewed and resolved
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5164
- **Severity:** Critical
- **Data needed:** specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- **Rationale:** Title-family YELLOW: the title_commitment doc type exists but is thin (one field), and several of these rows describe an attorney's title opinion letter, a distinct document type not modeled at all.
- **Family:** title_general
- **SME:** [ ] agree [ ] correct: ______

### G134 — O-FRD-51475 [O-FRD]
- **Q:** Were all Title Insurance requirements met including company ratings?
- **Defect condition:** An encroachment was identified on the subject or neighboring property without an easement
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5243
- **Severity:** Critical
- **Data needed:** specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- **Rationale:** Title-family YELLOW: the title_commitment doc type exists but is thin (one field), and several of these rows describe an attorney's title opinion letter, a distinct document type not modeled at all.
- **Family:** title_general
- **SME:** [ ] agree [ ] correct: ______

### G135 — O-FRD-00811 [O-FRD]
- **Q:** Were all Title Insurance requirements met including company ratings?
- **Defect condition:** Final TP, applicable endorsements or an attny's title opinion/certificate meeting req's not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5328
- **Severity:** Critical
- **Data needed:** specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- **Rationale:** Title-family YELLOW: the title_commitment doc type exists but is thin (one field), and several of these rows describe an attorney's title opinion letter, a distinct document type not modeled at all.
- **Family:** title_general
- **SME:** [ ] agree [ ] correct: ______

### G136 — TitleRedFlags [O-FRD]
- **Q:** Were all Title Insurance requirements met including company ratings?
- **Defect condition:** The loan amount, vesting, proposed insured or other "Red Flags" have not been addressed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5331
- **Severity:** Major
- **Data needed:** specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- **Rationale:** Title-family YELLOW: the title_commitment doc type exists but is thin (one field), and several of these rows describe an attorney's title opinion letter, a distinct document type not modeled at all.
- **Family:** title_general
- **SME:** [ ] agree [ ] correct: ______

### G137 — Title 90Days [O-FRD]
- **Q:** Were all Title Insurance requirements met including company ratings?
- **Defect condition:** The title effective date is not within 90-days of the closing date or 180 days for new construction
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5314
- **Severity:** Critical
- **Data needed:** a title-commitment effective_date field (title_commitment doc exists in loan 01; only title_vesting_commitment is currently extracted from it)
- **Rationale:** Crisp date-math once the field exists -- Bucket-B-style, same document, new field.
- **Family:** title_effective_date_90day
- **SME:** [ ] agree [ ] correct: ______

### G138 — Title-TransofTitle [O-FRD]
- **Q:** Were all Title Insurance requirements met including company ratings?
- **Defect condition:** The transfer of title is outside of company guidelines and not properly explained
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5337
- **Severity:** Major
- **Data needed:** specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- **Rationale:** Title-family YELLOW: the title_commitment doc type exists but is thin (one field), and several of these rows describe an attorney's title opinion letter, a distinct document type not modeled at all.
- **Family:** title_general
- **SME:** [ ] agree [ ] correct: ______

### G140 — O-FRD-51049 [O-FRD]
- **Q:** Were all Title Insurance requirements met including company ratings?
- **Defect condition:** Title policy amount of protection, insured party is incorrect &/or was written on an incorrect form
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5324
- **Severity:** Critical
- **Data needed:** specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- **Rationale:** Title-family YELLOW: the title_commitment doc type exists but is thin (one field), and several of these rows describe an attorney's title opinion letter, a distinct document type not modeled at all.
- **Family:** title_general
- **SME:** [ ] agree [ ] correct: ______

### G142 — O-FNM-55724 [O-FNM]
- **Q:** Were all Title Insurance requirements met?
- **Defect condition:** Attorney not insured against malpractice in giving opinions of title in an amt common for the area
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5320
- **Severity:** Critical
- **Data needed:** specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- **Rationale:** Title-family YELLOW: the title_commitment doc type exists but is thin (one field), and several of these rows describe an attorney's title opinion letter, a distinct document type not modeled at all.
- **Family:** title_general
- **Guide candidate:** B7-2-01 — Provision of Title Insurance (PDF p.860)
- **Guide candidate:** B7-2-03 — General Title Insurance Coverage (PDF p.861)
- **Guide candidate:** B7-2-04 — Special Title Insurance Coverage Considerations (PDF p.863)
- **SME:** [ ] agree [ ] correct: ______

### G143 — O-FNM-55726 [O-FNM]
- **Q:** Were all Title Insurance requirements met?
- **Defect condition:** Attorney title opinion letter did not provide gap coverage between closing & recordation of the mtg
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4970
- **Severity:** Critical
- **Data needed:** specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- **Rationale:** Title-family YELLOW: the title_commitment doc type exists but is thin (one field), and several of these rows describe an attorney's title opinion letter, a distinct document type not modeled at all.
- **Family:** title_general
- **Guide candidate:** B7-2-06 — Attorney Title Opinion Letter Requirements (PDF p.870)
- **Guide candidate:** B7-2-03 — General Title Insurance Coverage (PDF p.861)
- **Guide candidate:** B7-2-04 — Special Title Insurance Coverage Considerations (PDF p.863)
- **SME:** [ ] agree [ ] correct: ______

### G144 — O-FNM-55728 [O-FNM]
- **Q:** Were all Title Insurance requirements met?
- **Defect condition:** Attorney title opinion letter did not state property is acceptable & mtg is a fee simple 1st lien
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4969
- **Severity:** Critical
- **Data needed:** specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- **Rationale:** Title-family YELLOW: the title_commitment doc type exists but is thin (one field), and several of these rows describe an attorney's title opinion letter, a distinct document type not modeled at all.
- **Family:** title_general
- **Guide candidate:** B7-2-06 — Attorney Title Opinion Letter Requirements (PDF p.870)
- **Guide candidate:** B7-2-01 — Provision of Title Insurance (PDF p.860)
- **Guide candidate:** B7-2-03 — General Title Insurance Coverage (PDF p.861)
- **SME:** [ ] agree [ ] correct: ______

### G145 — O-FNM-55725 [O-FNM]
- **Q:** Were all Title Insurance requirements met?
- **Defect condition:** Attorney title opinion letter was not addressed to the lender and all successors
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4972
- **Severity:** Critical
- **Data needed:** specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- **Rationale:** Title-family YELLOW: the title_commitment doc type exists but is thin (one field), and several of these rows describe an attorney's title opinion letter, a distinct document type not modeled at all.
- **Family:** title_general
- **Guide candidate:** B7-2-06 — Attorney Title Opinion Letter Requirements (PDF p.870)
- **Guide candidate:** B7-1-03 — Lender-Purchased Mortgage Insurance (PDF p.854)
- **Guide candidate:** B7-2-01 — Provision of Title Insurance (PDF p.860)
- **SME:** [ ] agree [ ] correct: ______

### G146 — O-FNM-00830 [O-FNM]
- **Q:** Were all Title Insurance requirements met?
- **Defect condition:** No, the file does not reflect evidence of acceptable title insurance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5318
- **Severity:** Critical
- **Data needed:** specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- **Rationale:** Title-family YELLOW: the title_commitment doc type exists but is thin (one field), and several of these rows describe an attorney's title opinion letter, a distinct document type not modeled at all.
- **Family:** title_general
- **Guide candidate:** B7-2-01 — Provision of Title Insurance (PDF p.860)
- **Guide candidate:** B7-2-03 — General Title Insurance Coverage (PDF p.861)
- **Guide candidate:** B7-2-04 — Special Title Insurance Coverage Considerations (PDF p.863)
- **SME:** [ ] agree [ ] correct: ______

### G148 — Title-TitleReqmts [O-FNM]
- **Q:** Were all Title Insurance requirements met?
- **Defect condition:** Schedule B -  title requirements found that have not been appropriately addressed and/or cleared
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5335
- **Severity:** Major
- **Data needed:** specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- **Rationale:** Title-family YELLOW: the title_commitment doc type exists but is thin (one field), and several of these rows describe an attorney's title opinion letter, a distinct document type not modeled at all.
- **Family:** title_general
- **Guide candidate:** B7-2-01 — Provision of Title Insurance (PDF p.860)
- **Guide candidate:** B7-2-03 — General Title Insurance Coverage (PDF p.861)
- **Guide candidate:** B7-2-04 — Special Title Insurance Coverage Considerations (PDF p.863)
- **SME:** [ ] agree [ ] correct: ______

### G149 — O-FNM-55723 [O-FNM]
- **Q:** Were all Title Insurance requirements met?
- **Defect condition:** The attorney issuing the title opinion letter was not licensed where the subject property is located
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5321
- **Severity:** Critical
- **Data needed:** specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- **Rationale:** Title-family YELLOW: the title_commitment doc type exists but is thin (one field), and several of these rows describe an attorney's title opinion letter, a distinct document type not modeled at all.
- **Family:** title_general
- **Guide candidate:** B7-2-06 — Attorney Title Opinion Letter Requirements (PDF p.870)
- **Guide candidate:** B3-6-03 — Monthly Housing Expense for the Subject Property (PDF p.518)
- **Guide candidate:** B7-2-01 — Provision of Title Insurance (PDF p.860)
- **SME:** [ ] agree [ ] correct: ______

### G150 — O-FNM-55727 [O-FNM]
- **Q:** Were all Title Insurance requirements met?
- **Defect condition:** The attorney title opinion letter did not list all other liens and state they are subordinate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4971
- **Severity:** Critical
- **Data needed:** specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- **Rationale:** Title-family YELLOW: the title_commitment doc type exists but is thin (one field), and several of these rows describe an attorney's title opinion letter, a distinct document type not modeled at all.
- **Family:** title_general
- **Guide candidate:** B7-2-06 — Attorney Title Opinion Letter Requirements (PDF p.870)
- **Guide candidate:** B7-2-01 — Provision of Title Insurance (PDF p.860)
- **Guide candidate:** B7-2-03 — General Title Insurance Coverage (PDF p.861)
- **SME:** [ ] agree [ ] correct: ______

### G151 — TitleRedFlags [O-FNM]
- **Q:** Were all Title Insurance requirements met?
- **Defect condition:** The loan amount, vesting, proposed insured or other "Red Flags" have not been addressed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5330
- **Severity:** Major
- **Data needed:** specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- **Rationale:** Title-family YELLOW: the title_commitment doc type exists but is thin (one field), and several of these rows describe an attorney's title opinion letter, a distinct document type not modeled at all.
- **Family:** title_general
- **Guide candidate:** B5-2-04 — Manufactured Housing Pricing, Mortgage Insurance, and Loan Delivery Requirements (PDF p.727)
- **Guide candidate:** B5-6-03 — HomeReady Mortgage Loan Pricing, Mortgage Insurance, and Special Feature Codes (PDF p.818)
- **Guide candidate:** B7-1-05 — Government Mortgage Loan Guaranty or Insurance (PDF p.857)
- **SME:** [ ] agree [ ] correct: ______

### G152 — Title 90Days [O-FNM]
- **Q:** Were all Title Insurance requirements met?
- **Defect condition:** The title effective date is not within 90-days of the closing date or 180 days for new construction
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5313
- **Severity:** Critical
- **Data needed:** a title-commitment effective_date field (title_commitment doc exists in loan 01; only title_vesting_commitment is currently extracted from it)
- **Rationale:** Crisp date-math once the field exists -- Bucket-B-style, same document, new field.
- **Family:** title_effective_date_90day
- **Guide candidate:** B5-3.1-02 — Conversion of Construction-to-Permanent Financing: Single-Closing Transactions (PDF p.736)
- **Guide candidate:** B5-3.1-03 — Conversion of Construction-to-Permanent Financing: Two-Closing Transactions (PDF p.743)
- **Guide candidate:** B7-2-01 — Provision of Title Insurance (PDF p.860)
- **SME:** [ ] agree [ ] correct: ______

### G153 — Title-TransofTitle [O-FNM]
- **Q:** Were all Title Insurance requirements met?
- **Defect condition:** The transfer of title is outside of company guidelines and not properly explained
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5336
- **Severity:** Major
- **Data needed:** specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- **Rationale:** Title-family YELLOW: the title_commitment doc type exists but is thin (one field), and several of these rows describe an attorney's title opinion letter, a distinct document type not modeled at all.
- **Family:** title_general
- **Guide candidate:** B7-2-01 — Provision of Title Insurance (PDF p.860)
- **Guide candidate:** B7-2-03 — General Title Insurance Coverage (PDF p.861)
- **Guide candidate:** B7-2-04 — Special Title Insurance Coverage Considerations (PDF p.863)
- **SME:** [ ] agree [ ] correct: ______

### G154 — O-FNM-51712 [O-FNM]
- **Q:** Were all Title Insurance requirements met?
- **Defect condition:** Title insurer/reinsurer not approved &/or licensed to issue insurance in the subject property state
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4979
- **Severity:** Critical
- **Data needed:** specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- **Rationale:** Title-family YELLOW: the title_commitment doc type exists but is thin (one field), and several of these rows describe an attorney's title opinion letter, a distinct document type not modeled at all.
- **Family:** title_general
- **Guide candidate:** B3-6-03 — Monthly Housing Expense for the Subject Property (PDF p.518)
- **Guide candidate:** B7-2-01 — Provision of Title Insurance (PDF p.860)
- **Guide candidate:** B7-2-02 — Title Insurer Requirements (PDF p.860)
- **SME:** [ ] agree [ ] correct: ______

### G155 — O-FNM-51047 [O-FNM]
- **Q:** Were all Title Insurance requirements met?
- **Defect condition:** Title revealed exceptions or impediments without all specific eligibility requirements being met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5317
- **Severity:** Critical
- **Data needed:** specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- **Rationale:** Title-family YELLOW: the title_commitment doc type exists but is thin (one field), and several of these rows describe an attorney's title opinion letter, a distinct document type not modeled at all.
- **Family:** title_general
- **Guide candidate:** B7-2-05 — Title Exceptions and Impediments (PDF p.867)
- **Guide candidate:** B7-2-01 — Provision of Title Insurance (PDF p.860)
- **Guide candidate:** B7-2-03 — General Title Insurance Coverage (PDF p.861)
- **SME:** [ ] agree [ ] correct: ______

### G156 — O-VA-56209 [O-VA]
- **Q:** Were all VA Form 26-6393 Loan Analysis requirements met?
- **Defect condition:** Manual VA UW did not sign Form 26-6393 (Aug. 2022), which closed on a non-supervised automatic basis
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5363
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G157 — O-VA-53785 [O-VA]
- **Q:** Were all VA Form 26-6393 Loan Analysis requirements met?
- **Defect condition:** Monthly PITIA not calculated correctly &/or did not include all housing components
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5231
- **Severity:** Critical
- **Data needed:** VA Form 26-6393 (VA Loan Analysis) -- not in any synthetic loan folder
- **Rationale:** Niche VA underwriting-analysis form; loan 03 (the pilot's only VA loan) does not contain this document.
- **Family:** va_26_6393
- **SME:** [ ] agree [ ] correct: ______

### G158 — O-VA-00035 [O-VA]
- **Q:** Were all VA Form 26-6393 Loan Analysis requirements met?
- **Defect condition:** More than one Social Security# was noted without explanation &/or validation from SSA
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5184
- **Severity:** Critical
- **Data needed:** VA Form 26-6393 (VA Loan Analysis) -- not in any synthetic loan folder
- **Rationale:** Niche VA underwriting-analysis form; loan 03 (the pilot's only VA loan) does not contain this document.
- **Family:** va_26_6393
- **SME:** [ ] agree [ ] correct: ______

### G159 — O-VA-56075 [O-VA]
- **Q:** Were all VA Form 26-6393 Loan Analysis requirements met?
- **Defect condition:** PITIA of other properties owned by the borrower were not included in DTI as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5219
- **Severity:** Critical
- **Data needed:** VA Form 26-6393 (VA Loan Analysis) -- not in any synthetic loan folder
- **Rationale:** Niche VA underwriting-analysis form; loan 03 (the pilot's only VA loan) does not contain this document.
- **Family:** va_26_6393
- **SME:** [ ] agree [ ] correct: ______

### G160 — O-VA-55973 [O-VA]
- **Q:** Were all VA Form 26-6393 Loan Analysis requirements met?
- **Defect condition:** The VA Loan Analysis, VA Form 26-6393 (Aug. 2022), was not fully completed or was incorrect
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5103, 5104
- **Severity:** Critical
- **Data needed:** VA Form 26-6393 (VA Loan Analysis) -- not in any synthetic loan folder
- **Rationale:** Niche VA underwriting-analysis form; loan 03 (the pilot's only VA loan) does not contain this document.
- **Family:** va_26_6393
- **SME:** [ ] agree [ ] correct: ______

### G161 — O-VA-50762 [O-VA]
- **Q:** Were all VA Form 26-6393 Loan Analysis requirements met?
- **Defect condition:** The file did not contain a completed Loan Analysis, VA Form 26-639
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5177, 5178
- **Severity:** Critical
- **Data needed:** VA Form 26-6393 (VA Loan Analysis) -- not in any synthetic loan folder
- **Rationale:** Niche VA underwriting-analysis form; loan 03 (the pilot's only VA loan) does not contain this document.
- **Family:** va_26_6393
- **SME:** [ ] agree [ ] correct: ______

### G162 — O-VA-50771 [O-VA]
- **Q:** Were all VA Form 26-6393 Loan Analysis requirements met?
- **Defect condition:** The income used to qualify was calculated incorrectly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5099
- **Severity:** Critical
- **Data needed:** VA Form 26-6393 (VA Loan Analysis) -- not in any synthetic loan folder
- **Rationale:** Niche VA underwriting-analysis form; loan 03 (the pilot's only VA loan) does not contain this document.
- **Family:** va_26_6393
- **SME:** [ ] agree [ ] correct: ______

### G163 — O-VA-00139 [O-VA]
- **Q:** Were all VA Form 26-6393 Loan Analysis requirements met?
- **Defect condition:** UW failed to include every known debt, judgment, bankruptcy, alimony or child support obligation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5021
- **Severity:** Critical
- **Data needed:** VA Form 26-6393 (VA Loan Analysis) -- not in any synthetic loan folder
- **Rationale:** Niche VA underwriting-analysis form; loan 03 (the pilot's only VA loan) does not contain this document.
- **Family:** va_26_6393
- **SME:** [ ] agree [ ] correct: ______

### G164 — O-VA-56208 [O-VA]
- **Q:** Were all VA Form 26-6393 Loan Analysis requirements met?
- **Defect condition:** VA underwriter ID number was not entered in box 52 on the Loan Analysis, VA Form 26-6393 (Aug. 2022)
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5377
- **Severity:** Critical
- **Data needed:** VA Form 26-6393 (VA Loan Analysis) -- not in any synthetic loan folder
- **Rationale:** Niche VA underwriting-analysis form; loan 03 (the pilot's only VA loan) does not contain this document.
- **Family:** va_26_6393
- **SME:** [ ] agree [ ] correct: ______

### G166 — O-VA-56142 [O-VA]
- **Q:** Were all Veteran's eligibility requirements met?
- **Defect condition:** Most up-to-date version of Form 26-1817, is not in the file or is incomplete, incorrect or unsigned
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5374
- **Severity:** Critical
- **Data needed:** VA Form 26-1817 (Unmarried Surviving Spouse eligibility) -- not in corpus
- **Rationale:** Niche VA eligibility form, absent from loan 03.
- **Family:** va_26_1817
- **SME:** [ ] agree [ ] correct: ______

### G168 — O-VA-51187 [O-VA]
- **Q:** Were all Veteran's eligibility requirements met?
- **Defect condition:** The Certificate of Eligibility had conditions to receive a guaranty that were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4996
- **Severity:** Critical
- **Data needed:** COE entitlement-amount + guaranty-calculation fields (va_coe doc exists for loan 03 but only doc-presence is checked today, no entitlement-amount field is extracted)
- **Rationale:** Bucket-B-style: va_coe doc type exists, but no field captures the entitlement dollar amount or guaranty percentage this row's math needs.
- **Family:** coe_conditions_entitlement
- **SME:** [ ] agree [ ] correct: ______

### G170 — O-VA-50000 [O-VA]
- **Q:** Were all Veteran's eligibility requirements met?
- **Defect condition:** The current Cert of Eligibility is insufficient to allow for max 25% guaranty
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5372
- **Severity:** Critical
- **Data needed:** COE entitlement-amount + guaranty-calculation fields (va_coe doc exists for loan 03 but only doc-presence is checked today, no entitlement-amount field is extracted)
- **Rationale:** Bucket-B-style: va_coe doc type exists, but no field captures the entitlement dollar amount or guaranty percentage this row's math needs.
- **Family:** coe_conditions_entitlement
- **SME:** [ ] agree [ ] correct: ______

### G171 — O-BP-57801 [O-VA]
- **Q:** Were all Veteran's eligibility requirements met?
- **Defect condition:** Veteran discharged from service & a copy of DD Form 214 not provided as  proof of military service
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5019
- **Severity:** Minor
- **Data needed:** DD Form 214 / military orders documentation -- not in corpus
- **Rationale:** Military-service-verification family, absent from the corpus.
- **Family:** dd214_military
- **SME:** [ ] agree [ ] correct: ______

### G173 — O-RHS-50006 [O-RHS]
- **Q:** Were all additional total debt ratio calculation requirements met?
- **Defect condition:** Account with 30 day late payment in 12 months evident; 5% of the balance not included in DTI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4953
- **Severity:** Critical
- **Data needed:** a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- **Rationale:** Every one of these RHS/FHA/VA 'was a specific debt type included in DTI' rows is individually crisp math (a rule engine could apply it), but needs a DTI-aggregation + liability-classification layer that does not exist yet -- no new document required, a real derivation-logic gap.
- **Family:** debt_ratio_inclusion
- **SME:** [ ] agree [ ] correct: ______

### G174 — O-RHS-50008 [O-RHS]
- **Q:** Were all additional total debt ratio calculation requirements met?
- **Defect condition:** Business debt on personal credit report omitted w/out evidence debt is paid through a business acct
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4988
- **Severity:** Critical
- **Data needed:** a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- **Rationale:** Every one of these RHS/FHA/VA 'was a specific debt type included in DTI' rows is individually crisp math (a rule engine could apply it), but needs a DTI-aggregation + liability-classification layer that does not exist yet -- no new document required, a real derivation-logic gap.
- **Family:** debt_ratio_inclusion
- **SME:** [ ] agree [ ] correct: ______

### G175 — O-RHS-02843 [O-RHS]
- **Q:** Were all additional total debt ratio calculation requirements met?
- **Defect condition:** Contingent liability without evidence another obligor has made payments for the last 12 months
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5005
- **Severity:** Critical
- **Data needed:** a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- **Rationale:** Every one of these RHS/FHA/VA 'was a specific debt type included in DTI' rows is individually crisp math (a rule engine could apply it), but needs a DTI-aggregation + liability-classification layer that does not exist yet -- no new document required, a real derivation-logic gap.
- **Family:** debt_ratio_inclusion
- **SME:** [ ] agree [ ] correct: ______

### G176 — O-RHS-52813 [O-RHS]
- **Q:** Were all additional total debt ratio calculation requirements met?
- **Defect condition:** Federal and/or State income tax repayment plan payments were not included in the monthly debt
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5308
- **Severity:** Critical
- **Data needed:** a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- **Rationale:** Every one of these RHS/FHA/VA 'was a specific debt type included in DTI' rows is individually crisp math (a rule engine could apply it), but needs a DTI-aggregation + liability-classification layer that does not exist yet -- no new document required, a real derivation-logic gap.
- **Family:** debt_ratio_inclusion
- **SME:** [ ] agree [ ] correct: ______

### G177 — O-RHS-50565 [O-RHS]
- **Q:** Were all additional total debt ratio calculation requirements met?
- **Defect condition:** Installment accounts with more than 10 months remaining was not included in the DTI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5146
- **Severity:** Critical
- **Data needed:** a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- **Rationale:** Every one of these RHS/FHA/VA 'was a specific debt type included in DTI' rows is individually crisp math (a rule engine could apply it), but needs a DTI-aggregation + liability-classification layer that does not exist yet -- no new document required, a real derivation-logic gap.
- **Family:** debt_ratio_inclusion
- **SME:** [ ] agree [ ] correct: ______

### G178 — O-RHS-02844 [O-RHS]
- **Q:** Were all additional total debt ratio calculation requirements met?
- **Defect condition:** Judgment pymt w/ more than 10 pymts left not included with significant impact on mtg repayment
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5120
- **Severity:** Critical
- **Data needed:** a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- **Rationale:** Every one of these RHS/FHA/VA 'was a specific debt type included in DTI' rows is individually crisp math (a rule engine could apply it), but needs a DTI-aggregation + liability-classification layer that does not exist yet -- no new document required, a real derivation-logic gap.
- **Family:** debt_ratio_inclusion
- **SME:** [ ] agree [ ] correct: ______

### G179 — O-RHS-52814 [O-RHS]
- **Q:** Were all additional total debt ratio calculation requirements met?
- **Defect condition:** Lease payments not included in the DTI regardless of months remaining to pay on the contract
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5124
- **Severity:** Critical
- **Data needed:** a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- **Rationale:** Every one of these RHS/FHA/VA 'was a specific debt type included in DTI' rows is individually crisp math (a rule engine could apply it), but needs a DTI-aggregation + liability-classification layer that does not exist yet -- no new document required, a real derivation-logic gap.
- **Family:** debt_ratio_inclusion
- **SME:** [ ] agree [ ] correct: ______

### G180 — O-RHS-02846 [O-RHS]
- **Q:** Were all additional total debt ratio calculation requirements met?
- **Defect condition:** Short-term obligation was not included in DTI that will have a significant impact ability to repay
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5286
- **Severity:** Critical
- **Data needed:** a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- **Rationale:** Every one of these RHS/FHA/VA 'was a specific debt type included in DTI' rows is individually crisp math (a rule engine could apply it), but needs a DTI-aggregation + liability-classification layer that does not exist yet -- no new document required, a real derivation-logic gap.
- **Family:** debt_ratio_inclusion
- **SME:** [ ] agree [ ] correct: ______

### G181 — O-RHS-02845 [O-RHS]
- **Q:** Were all additional total debt ratio calculation requirements met?
- **Defect condition:** The full monthly debt of the automobile or expense allowance was not included in the DTI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4980
- **Severity:** Critical
- **Data needed:** a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- **Rationale:** Every one of these RHS/FHA/VA 'was a specific debt type included in DTI' rows is individually crisp math (a rule engine could apply it), but needs a DTI-aggregation + liability-classification layer that does not exist yet -- no new document required, a real derivation-logic gap.
- **Family:** debt_ratio_inclusion
- **SME:** [ ] agree [ ] correct: ______

### G182 — O-RHS-02847 [O-RHS]
- **Q:** Were all additional total debt ratio calculation requirements met?
- **Defect condition:** There is a balloon/deferred payment due in the next 24 mos. that was not included in the DTI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4981
- **Severity:** Critical
- **Data needed:** a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- **Rationale:** Every one of these RHS/FHA/VA 'was a specific debt type included in DTI' rows is individually crisp math (a rule engine could apply it), but needs a DTI-aggregation + liability-classification layer that does not exist yet -- no new document required, a real derivation-logic gap.
- **Family:** debt_ratio_inclusion
- **SME:** [ ] agree [ ] correct: ______

### G184 — O-FHA-00616 [O-FHA]
- **Q:** Were all additional underwriting requirements met?
- **Defect condition:** A material change occurred or was discovered and the loan was not resubmitted to the AUS
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5143
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G185 — O-FHA-54122 [O-FHA]
- **Q:** Were all additional underwriting requirements met?
- **Defect condition:** Expanded borrower demographic information not entered in FHA Connection as per HMDA regulations
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5057
- **Severity:** Critical
- **Data needed:** HMDA demographic-data entry fact (FHA Connection screen) -- not modeled
- **Rationale:** Niche FHA Connection data-entry fact, absent from the corpus.
- **Family:** hmda_demographic
- **SME:** [ ] agree [ ] correct: ______

### G188 — O-FHA-50641 [O-FHA]
- **Q:** Were all application document processing requirements met?
- **Defect condition:** Case number was transferred from another lender without meeting all requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4992
- **Severity:** Critical
- **Data needed:** case-number-transfer documentation between lenders -- not modeled
- **Rationale:** Niche FHA case-transfer fact, absent from the corpus.
- **Family:** case_number_transfer
- **SME:** [ ] agree [ ] correct: ______

### G189 — O-FHA-50639 [O-FHA]
- **Q:** Were all application document processing requirements met?
- **Defect condition:** The borr's receipt of counseling by HUD-approved housing counseling agencies not evident
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5095
- **Severity:** Major
- **Data needed:** homeownership-education/housing-counseling completion certificate -- not in corpus
- **Rationale:** Niche counseling-completion document, absent from the corpus.
- **Family:** homeownership_education
- **SME:** [ ] agree [ ] correct: ______

### G191 — O-RHS-02895 [O-RHS]
- **Q:** Were all application package requirements met?
- **Defect condition:** Accept decision but lender did not submit the abbreviated loan app with the required documentation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5085
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G192 — O-RHS-50594 [O-RHS]
- **Q:** Were all application package requirements met?
- **Defect condition:** Conditional Commitment not in the loan file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5002
- **Severity:** Critical
- **Data needed:** RHS Conditional Commitment -- not in corpus
- **Rationale:** USDA/RHS commitment document, absent from loan 05.
- **Family:** conditional_commitment
- **SME:** [ ] agree [ ] correct: ______

### G193 — O-RHS-02870 [O-RHS]
- **Q:** Were all application package requirements met?
- **Defect condition:** Manual UW approval or final GUS Underwriting Analysis is not in the file as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5068
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G194 — O-RHS-55739 [O-RHS]
- **Q:** Were all application package requirements met?
- **Defect condition:** The Conditional Commitment was not issued prior to the loan closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5003
- **Severity:** Critical
- **Data needed:** RHS Conditional Commitment -- not in corpus
- **Rationale:** USDA/RHS commitment document, absent from loan 05.
- **Family:** conditional_commitment
- **SME:** [ ] agree [ ] correct: ______

### G195 — O-RHS-02894 [O-RHS]
- **Q:** Were all application package requirements met?
- **Defect condition:** The lender did not submit a complete loan application containing the required documentation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5157
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G197 — O-FHA-02219 [O-FHA]
- **Q:** Were all borrower authorization  requirements met?
- **Defect condition:** An executed statement clearly expressing consent for use of applicant's information is missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4978
- **Severity:** Major
- **Data needed:** signed borrower-information-use consent statement -- not in corpus
- **Rationale:** Niche FHA authorization form, absent from the corpus.
- **Family:** borrower_authorization_consent
- **SME:** [ ] agree [ ] correct: ______

### G198 — O-FHA-51135 [O-FHA]
- **Q:** Were all borrower authorization  requirements met?
- **Defect condition:** Non-borrowing spouse's social security number &/or consent to verify with the SSA not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5185
- **Severity:** Critical
- **Data needed:** SSN-discrepancy resolution documentation (SSA verification letter, Form SSA-89/eCBSV) or identity-verification record -- not in corpus
- **Rationale:** SSN-validation family; no such verification record exists in any of the 5 loans.
- **Family:** nonborrowing_spouse_ssn
- **SME:** [ ] agree [ ] correct: ______

### G200 — O-VA-54810 [O-VA]
- **Q:** Were all borrower eligibility requirements met?
- **Defect condition:** Active duty borr provided receipt of Purple Heart prior to/at closing & stat funding fee not waived
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5249
- **Severity:** Critical
- **Data needed:** VA funding-fee / FHA MIP calculation fields (percentage tables, exemption status, loan amount) -- not extracted
- **Rationale:** Crisp percentage-table math once the fields exist; no such fields are in FIELD_SPECS today.
- **Family:** funding_fee_mip
- **SME:** [ ] agree [ ] correct: ______

### G201 — O-VA-54814 [O-VA]
- **Q:** Were all borrower eligibility requirements met?
- **Defect condition:** Active duty svc member has pre-discharge claim pending & proposed or memorandum rating not obtained
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5233
- **Severity:** Critical
- **Data needed:** VA pending-disability-claim / National-Guard-service-days documentation -- not modeled
- **Rationale:** Niche VA eligibility sub-conditions, absent from the corpus.
- **Family:** va_pending_claim_rating
- **SME:** [ ] agree [ ] correct: ______

### G202 — O-VA-54337 [O-VA]
- **Q:** Were all borrower eligibility requirements met?
- **Defect condition:** Army or Air National Guard member does not have 90 cumulative &  30 consecutive days active duty
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4968
- **Severity:** Critical
- **Data needed:** VA pending-disability-claim / National-Guard-service-days documentation -- not modeled
- **Rationale:** Niche VA eligibility sub-conditions, absent from the corpus.
- **Family:** va_pending_claim_rating
- **SME:** [ ] agree [ ] correct: ______

### G203 — O-VA-54808 [O-VA]
- **Q:** Were all borrower eligibility requirements met?
- **Defect condition:** Borr is surviving spouse of Vet who died from a service disability & stat funding fee not waived
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5305
- **Severity:** Critical
- **Data needed:** VA funding-fee / FHA MIP calculation fields (percentage tables, exemption status, loan amount) -- not extracted
- **Rationale:** Crisp percentage-table math once the fields exist; no such fields are in FIELD_SPECS today.
- **Family:** funding_fee_mip
- **SME:** [ ] agree [ ] correct: ______

### G204 — O-RHS-50539 [O-RHS]
- **Q:** Were all borrower eligibility requirements met?
- **Defect condition:** Borr owns another property without validating RHS loan will be primary
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5097
- **Severity:** Critical
- **Data needed:** an occupancy-intent certification / military-orders / lease-review fact -- not currently modeled (no occupancy-related field or fact exists in FIELD_SPECS/FACT_SPECS)
- **Rationale:** Occupancy-eligibility family; several distinct sub-conditions (military unable-to-occupy, group-home leased-to-business, second-home suitability) each need their own new fact, none of which exist today.
- **Family:** occupancy_certification
- **SME:** [ ] agree [ ] correct: ______

### G205 — O-RHS-02858 [O-RHS]
- **Q:** Were all borrower eligibility requirements met?
- **Defect condition:** Borrower is not a US citizen & documentation verifying qualified alien status not obtained
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5198
- **Severity:** Critical
- **Data needed:** citizenship/residency-status documentation (USCIS determination, alien-registration evidence) -- not in corpus
- **Rationale:** Citizenship/residency family; not modeled at all in this pilot (same gap flagged for asset-verification's G284, decision 017).
- **Family:** citizenship_residency
- **SME:** [ ] agree [ ] correct: ______

### G206 — O-RHS-02856 [O-RHS]
- **Q:** Were all borrower eligibility requirements met?
- **Defect condition:** No GSA/SAM check evidence or GUS date found before commitment or 30 days pre-closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5078
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G208 — O-VA-54809 [O-VA]
- **Q:** Were all borrower eligibility requirements met?
- **Defect condition:** Pre-discharge disability exam w/ memorandum rating pay eligibility & the stat funding fee not waived
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5235
- **Severity:** Critical
- **Data needed:** VA pending-disability-claim / National-Guard-service-days documentation -- not modeled
- **Rationale:** Niche VA eligibility sub-conditions, absent from the corpus.
- **Family:** va_pending_claim_rating
- **SME:** [ ] agree [ ] correct: ______

### G209 — O-VA-54813 [O-VA]
- **Q:** Were all borrower eligibility requirements met?
- **Defect condition:** The active duty service member has a pending pre-discharge claim & VA Form 26-8937 was not submitted
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5234
- **Severity:** Critical
- **Data needed:** VA Form 26-8937 (Verification of VA Benefits) -- not in corpus
- **Rationale:** Niche VA benefits-verification form, absent from loan 03.
- **Family:** va_26_8937
- **SME:** [ ] agree [ ] correct: ______

### G210 — O-RHS-02859 [O-RHS]
- **Q:** Were all borrower eligibility requirements met?
- **Defect condition:** The file does not document that the applicant intends to occupy the subject as their primary home
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5211
- **Severity:** Critical
- **Data needed:** an occupancy-intent certification / military-orders / lease-review fact -- not currently modeled (no occupancy-related field or fact exists in FIELD_SPECS/FACT_SPECS)
- **Rationale:** Occupancy-eligibility family; several distinct sub-conditions (military unable-to-occupy, group-home leased-to-business, second-home suitability) each need their own new fact, none of which exist today.
- **Family:** occupancy_certification
- **SME:** [ ] agree [ ] correct: ______

### G211 — O-RHS-59423 [O-RHS]
- **Q:** Were all borrower eligibility requirements met?
- **Defect condition:** The number of household members was not certified by entering the number in GUS
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4997
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G212 — O-VA-54811 [O-VA]
- **Q:** Were all borrower eligibility requirements met?
- **Defect condition:** The potentially exempt Vet was advised to finance the funding fee resulting in cashback
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5055
- **Severity:** Critical
- **Data needed:** VA funding-fee / FHA MIP calculation fields (percentage tables, exemption status, loan amount) -- not extracted
- **Rationale:** Crisp percentage-table math once the fields exist; no such fields are in FIELD_SPECS today.
- **Family:** funding_fee_mip
- **SME:** [ ] agree [ ] correct: ______

### G213 — O-RHS-02893 [O-RHS]
- **Q:** Were all borrower eligibility requirements met?
- **Defect condition:** The social security number for each applicant was not documented and/or verified
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5290
- **Severity:** Critical
- **Data needed:** SSN-discrepancy resolution documentation (SSA verification letter, Form SSA-89/eCBSV) or identity-verification record -- not in corpus
- **Rationale:** SSN-validation family; no such verification record exists in any of the 5 loans.
- **Family:** nonborrowing_spouse_ssn
- **SME:** [ ] agree [ ] correct: ______

### G214 — O-VA-54807 [O-VA]
- **Q:** Were all borrower eligibility requirements met?
- **Defect condition:** Vet gets disability or would be entitled retirement/active svc pay & stat funding fee not waived
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5024
- **Severity:** Critical
- **Data needed:** VA funding-fee / FHA MIP calculation fields (percentage tables, exemption status, loan amount) -- not extracted
- **Rationale:** Crisp percentage-table math once the fields exist; no such fields are in FIELD_SPECS today.
- **Family:** funding_fee_mip
- **SME:** [ ] agree [ ] correct: ______

### G216 — O-FHA-54123 [O-FHA]
- **Q:** Were all citizenship and residency status requirements met?
- **Defect condition:** All eligibility req's not met for  non-U.S. citizen borrower including DACA status recipients
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5199
- **Severity:** Critical
- **Data needed:** citizenship/residency-status documentation (USCIS determination, alien-registration evidence) -- not in corpus
- **Rationale:** Citizenship/residency family; not modeled at all in this pilot (same gap flagged for asset-verification's G284, decision 017).
- **Family:** citizenship_residency
- **SME:** [ ] agree [ ] correct: ______

### G217 — O-FHA-59123 [O-FHA]
- **Q:** Were all citizenship and residency status requirements met?
- **Defect condition:** Citizenship evidence for borrowers from Micronesia, Marshall Islands, or Palau not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4998
- **Severity:** Critical
- **Data needed:** citizenship/residency-status documentation (USCIS determination, alien-registration evidence) -- not in corpus
- **Rationale:** Citizenship/residency family; not modeled at all in this pilot (same gap flagged for asset-verification's G284, decision 017).
- **Family:** citizenship_residency
- **SME:** [ ] agree [ ] correct: ______

### G218 — O-FHA-54124 [O-FHA]
- **Q:** Were all citizenship and residency status requirements met?
- **Defect condition:** Documentation substantiating the refugee or asylee status granted by the USCIS was not obtained
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5365
- **Severity:** Critical
- **Data needed:** citizenship/residency-status documentation (USCIS determination, alien-registration evidence) -- not in corpus
- **Rationale:** Citizenship/residency family; not modeled at all in this pilot (same gap flagged for asset-verification's G284, decision 017).
- **Family:** citizenship_residency
- **SME:** [ ] agree [ ] correct: ______

### G221 — O-FHA-50649 [O-FHA]
- **Q:** Were all co-signer requirements met?
- **Defect condition:** The cosigner on the transaction did not sign the Note
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5007
- **Severity:** Critical
- **Data needed:** co-signer/guarantor/non-occupying-borrower structured data (URLA parties exist as free text; no field distinguishes borrower role/occupancy intent)
- **Rationale:** Same family as the LTV-for-non-occupying-borrower rules -- needs a borrower-role classification not modeled today.
- **Family:** cosigner_guarantor_noncoocc
- **SME:** [ ] agree [ ] correct: ______

### G224 — O-RHS-52641 [O-RHS]
- **Q:** Were all credit eligibility requirements met?
- **Defect condition:** Delinq court order child support w/out admin offset & arrear not PIF, released or 3 timely repaymts
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5023
- **Severity:** Critical
- **Data needed:** delinquent-child-support repayment-history documentation -- not modeled
- **Rationale:** Niche RHS credit-eligibility sub-condition, absent from the corpus.
- **Family:** delinquent_child_support_credit
- **SME:** [ ] agree [ ] correct: ______

### G225 — O-RHS-02833 [O-RHS]
- **Q:** Were all credit eligibility requirements met?
- **Defect condition:** GSA List & CAIVRS not checked to determine applicant & other req'd parties eligibility
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4990
- **Severity:** Critical
- **Data needed:** caivrs doc type already exists in DOC_TYPES and is present for loan 02 only (05_CAIVRS_LDP_GSA.pdf) but has zero FIELD_SPECS/FACT_SPECS entries -- no 'clear'/'hit' fact is extracted from it, and no loan 01/03/04/05 has this document at all
- **Rationale:** Per decision 016's own precedent, CAIVRS/LDP/GSA screening is treated as an ordinary point-in-time screenshot document (not a live-registry Bucket-C lookup like NMLS) -- ready for Bucket-B-style field extraction once deepened, but genuinely absent as a fixture for 4 of 5 loans.
- **Family:** caivrs_ldp_gsa
- **SME:** [ ] agree [ ] correct: ______

### G227 — O-FNM-52794 [O-FNM]
- **Q:** Were all data quality, integrity, and fraud requirements met?
- **Defect condition:** All employees involved in the origination of the loan were not checked against the FHFA SCP list
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5064
- **Severity:** Critical
- **Data needed:** OFAC SDN list / Freddie Mac Exclusionary List / FHFA Suspended Counterparty Program / BSA-AML screening record (no such document or fixture exists in any of the 5 synthetic loans)
- **Rationale:** Distinct from the CAIVRS/LDP/GSA family above -- no per-loan screenshot document for these specific lists exists anywhere in the corpus (not even one instance), a genuine Bucket-A fixture gap, not merely thin extraction.
- **Family:** ofac_exclusionary
- **Guide candidate:** A3-4-02 — Data Quality and Integrity (PDF p.141)
- **Guide candidate:** C1-2-01 — General Information on Delivering Loan Data and Documents (PDF p.947)
- **Guide candidate:** C1-2-02 — Loan Data and Documentation Delivery Requirements (PDF p.948)
- **SME:** [ ] agree [ ] correct: ______

### G228 — Credit Rept ID Match [O-FNM]
- **Q:** Were all data quality, integrity, and fraud requirements met?
- **Defect condition:** ID # on the Credit report does not match the AUS report or EPIC screen
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5014
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **Guide candidate:** A3-4-02 — Data Quality and Integrity (PDF p.141)
- **Guide candidate:** B3-2-09 — Erroneous Credit Report Data (PDF p.311)
- **Guide candidate:** B3-2-10 — Accuracy of DU Data, DU Tolerances, and Errors in the Credit Report (PDF p.313)
- **SME:** [ ] agree [ ] correct: ______

### G230 — O-FNM-51688 [O-FNM]
- **Q:** Were all data quality, integrity, and fraud requirements met?
- **Defect condition:** Match on the OFAC SDN list, FNMA not notified w/in 24 hrs & funds not blocked & segregated
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5214
- **Severity:** Critical
- **Data needed:** OFAC SDN list / Freddie Mac Exclusionary List / FHFA Suspended Counterparty Program / BSA-AML screening record (no such document or fixture exists in any of the 5 synthetic loans)
- **Rationale:** Distinct from the CAIVRS/LDP/GSA family above -- no per-loan screenshot document for these specific lists exists anywhere in the corpus (not even one instance), a genuine Bucket-A fixture gap, not merely thin extraction.
- **Family:** ofac_exclusionary
- **Guide candidate:** A3-4-02 — Data Quality and Integrity (PDF p.141)
- **Guide candidate:** D1-3-02 — Lender Post-Closing Quality Control Review of Approval Conditions, Underwriting Decisions, Data, and Documentation (PDF p.1068)
- **Guide candidate:** A3-4-03 — Preventing, Detecting, and Reporting Mortgage Fraud (PDF p.142)
- **SME:** [ ] agree [ ] correct: ______

### G232 — O-FNM-52795 [O-FNM]
- **Q:** Were all data quality, integrity, and fraud requirements met?
- **Defect condition:** No evidence all internal participants involved in the mtg were checked against the GSA and LDP lists
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5122
- **Severity:** Critical
- **Data needed:** caivrs doc type already exists in DOC_TYPES and is present for loan 02 only (05_CAIVRS_LDP_GSA.pdf) but has zero FIELD_SPECS/FACT_SPECS entries -- no 'clear'/'hit' fact is extracted from it, and no loan 01/03/04/05 has this document at all
- **Rationale:** Per decision 016's own precedent, CAIVRS/LDP/GSA screening is treated as an ordinary point-in-time screenshot document (not a live-registry Bucket-C lookup like NMLS) -- ready for Bucket-B-style field extraction once deepened, but genuinely absent as a fixture for 4 of 5 loans.
- **Family:** caivrs_ldp_gsa
- **Guide candidate:** A3-4-02 — Data Quality and Integrity (PDF p.141)
- **Guide candidate:** D1-3-02 — Lender Post-Closing Quality Control Review of Approval Conditions, Underwriting Decisions, Data, and Documentation (PDF p.1068)
- **Guide candidate:** A3-4-03 — Preventing, Detecting, and Reporting Mortgage Fraud (PDF p.142)
- **SME:** [ ] agree [ ] correct: ______

### G233 — BorrowerAddress [O-FNM]
- **Q:** Were all data quality, integrity, and fraud requirements met?
- **Defect condition:** Property address submitted to DU does not match other documentation in the loan file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4983
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **Guide candidate:** A3-4-02 — Data Quality and Integrity (PDF p.141)
- **Guide candidate:** C1-2-02 — Loan Data and Documentation Delivery Requirements (PDF p.948)
- **Guide candidate:** D1-3-02 — Lender Post-Closing Quality Control Review of Approval Conditions, Underwriting Decisions, Data, and Documentation (PDF p.1068)
- **SME:** [ ] agree [ ] correct: ______

### G234 — O-FRD-02575 [O-FNM]
- **Q:** Were all data quality, integrity, and fraud requirements met?
- **Defect condition:** Required parties per their specific role in the loan not checked against the FHLMC Exclusionary List
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5072
- **Severity:** Major
- **Data needed:** OFAC SDN list / Freddie Mac Exclusionary List / FHFA Suspended Counterparty Program / BSA-AML screening record (no such document or fixture exists in any of the 5 synthetic loans)
- **Rationale:** Distinct from the CAIVRS/LDP/GSA family above -- no per-loan screenshot document for these specific lists exists anywhere in the corpus (not even one instance), a genuine Bucket-A fixture gap, not merely thin extraction.
- **Family:** ofac_exclusionary
- **Guide candidate:** A3-4-02 — Data Quality and Integrity (PDF p.141)
- **Guide candidate:** C1-2-01 — General Information on Delivering Loan Data and Documents (PDF p.947)
- **Guide candidate:** C1-2-02 — Loan Data and Documentation Delivery Requirements (PDF p.948)
- **SME:** [ ] agree [ ] correct: ______

### G236 — O-RHS-02882 [O-RHS]
- **Q:** Were all eligible loan purpose requirements met?
- **Defect condition:** All eligibility requirements were not met for a non-streamlined refinance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5196
- **Severity:** Critical
- **Data needed:** RHS refinance-eligibility facts (existing-loan closing date, borrower-retention, rate comparison) -- not modeled; loan 04 is the pilot's only refi loan and it's a conventional cash-out, not an RHS streamline
- **Rationale:** RHS-refinance family; no RHS refinance fixture exists in the corpus at all.
- **Family:** rhs_refi_eligibility
- **SME:** [ ] agree [ ] correct: ______

### G237 — O-RHS-02883 [O-RHS]
- **Q:** Were all eligible loan purpose requirements met?
- **Defect condition:** All eligibility requirements were not met for a streamlined refinance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5300
- **Severity:** Critical
- **Data needed:** RHS refinance-eligibility facts (existing-loan closing date, borrower-retention, rate comparison) -- not modeled; loan 04 is the pilot's only refi loan and it's a conventional cash-out, not an RHS streamline
- **Rationale:** RHS-refinance family; no RHS refinance fixture exists in the corpus at all.
- **Family:** rhs_refi_eligibility
- **SME:** [ ] agree [ ] correct: ______

### G238 — O-RHS-50017 [O-RHS]
- **Q:** Were all eligible loan purpose requirements met?
- **Defect condition:** All the borrowers on the RHS refi of an RD Guaranteed loan to a Streamline-Assist were not retained
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5366
- **Severity:** Critical
- **Data needed:** RHS refinance-eligibility facts (existing-loan closing date, borrower-retention, rate comparison) -- not modeled; loan 04 is the pilot's only refi loan and it's a conventional cash-out, not an RHS streamline
- **Rationale:** RHS-refinance family; no RHS refinance fixture exists in the corpus at all.
- **Family:** rhs_refi_eligibility
- **SME:** [ ] agree [ ] correct: ______

### G239 — O-RHS-50535 [O-RHS]
- **Q:** Were all eligible loan purpose requirements met?
- **Defect condition:** Borr has a direct USDA loan, Statement of Loan Balance letter not obtained
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5298
- **Severity:** Critical
- **Data needed:** RHS refinance-eligibility facts (existing-loan closing date, borrower-retention, rate comparison) -- not modeled; loan 04 is the pilot's only refi loan and it's a conventional cash-out, not an RHS streamline
- **Rationale:** RHS-refinance family; no RHS refinance fixture exists in the corpus at all.
- **Family:** rhs_refi_eligibility
- **SME:** [ ] agree [ ] correct: ______

### G240 — O-RHS-51842 [O-RHS]
- **Q:** Were all eligible loan purpose requirements met?
- **Defect condition:** Closing costs and lender fees were unreasonable and/or they exceeded the total loan amount
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5362
- **Severity:** Critical
- **Machine checks:** closing-costs-plus-lender-fees vs total-loan-amount comparison (fields exist: closing_disclosure + loan amount, once loan_amount is extracted)
- **Stays human:** 'unreasonable' fee-amount judgment
- **Data needed:** loan_amount field (not currently in FIELD_SPECS)
- **Rationale:** Compound condition ('and/or'): the second half (fees exceed total loan amount) is crisp math once loan_amount exists; only 'unreasonable' is a judgment call. Kept YELLOW, not RED, following the assets-triage precedent for compound crisp+judgment conditions (e.g. decision 017's G007).
- **Family:** override
- **SME:** [ ] agree [ ] correct: ______

### G241 — O-RHS-50016 [O-RHS]
- **Q:** Were all eligible loan purpose requirements met?
- **Defect condition:** Existing USDA loan being refinanced did not close at least 180 days before the req for Cond Commit
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5368
- **Severity:** Critical
- **Data needed:** RHS Conditional Commitment -- not in corpus
- **Rationale:** USDA/RHS commitment document, absent from loan 05.
- **Family:** conditional_commitment
- **SME:** [ ] agree [ ] correct: ______

### G242 — O-RHS-50536 [O-RHS]
- **Q:** Were all eligible loan purpose requirements met?
- **Defect condition:** Interest rate not fixed and/or is higher than rate of loan being refinanced
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5111
- **Severity:** Critical
- **Data needed:** RHS refinance-eligibility facts (existing-loan closing date, borrower-retention, rate comparison) -- not modeled; loan 04 is the pilot's only refi loan and it's a conventional cash-out, not an RHS streamline
- **Rationale:** RHS-refinance family; no RHS refinance fixture exists in the corpus at all.
- **Family:** rhs_refi_eligibility
- **SME:** [ ] agree [ ] correct: ______

### G243 — O-RHS-50015 [O-RHS]
- **Q:** Were all eligible loan purpose requirements met?
- **Defect condition:** RHS refi of an RD Guaranteed loan-at least 1 of the borr's is not on the RD loan being refinanced
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5367
- **Severity:** Critical
- **Data needed:** RHS refinance-eligibility facts (existing-loan closing date, borrower-retention, rate comparison) -- not modeled; loan 04 is the pilot's only refi loan and it's a conventional cash-out, not an RHS streamline
- **Rationale:** RHS-refinance family; no RHS refinance fixture exists in the corpus at all.
- **Family:** rhs_refi_eligibility
- **SME:** [ ] agree [ ] correct: ______

### G244 — O-RHS-02884 [O-RHS]
- **Q:** Were all eligible loan purpose requirements met?
- **Defect condition:** Streamlined-Assist Refi - the transaction does not meet the eligibility requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5299
- **Severity:** Critical
- **Data needed:** RHS refinance-eligibility facts (existing-loan closing date, borrower-retention, rate comparison) -- not modeled; loan 04 is the pilot's only refi loan and it's a conventional cash-out, not an RHS streamline
- **Rationale:** RHS-refinance family; no RHS refinance fixture exists in the corpus at all.
- **Family:** rhs_refi_eligibility
- **SME:** [ ] agree [ ] correct: ______

### G245 — O-RHS-02881 [O-RHS]
- **Q:** Were all eligible loan purpose requirements met?
- **Defect condition:** The refinance did not have a permissible purpose
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5250
- **Severity:** Critical
- **Data needed:** RHS refinance-eligibility facts (existing-loan closing date, borrower-retention, rate comparison) -- not modeled; loan 04 is the pilot's only refi loan and it's a conventional cash-out, not an RHS streamline
- **Rationale:** RHS-refinance family; no RHS refinance fixture exists in the corpus at all.
- **Family:** rhs_refi_eligibility
- **SME:** [ ] agree [ ] correct: ______

### G246 — O-RHS-53928 [O-RHS]
- **Q:** Were all eligible loan purpose requirements met?
- **Defect condition:** Unpaid fees, past-due interest & late fees/penalties included in new streamlined refi loan amount
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5107
- **Severity:** Critical
- **Data needed:** RHS refinance-eligibility facts (existing-loan closing date, borrower-retention, rate comparison) -- not modeled; loan 04 is the pilot's only refi loan and it's a conventional cash-out, not an RHS streamline
- **Rationale:** RHS-refinance family; no RHS refinance fixture exists in the corpus at all.
- **Family:** rhs_refi_eligibility
- **SME:** [ ] agree [ ] correct: ______

### G248 — O-VA-55437 [O-VA]
- **Q:** Were all fees and charges requirements met?
- **Defect condition:** Borr down pymts, even if sales price exceeds reasonable value, not included in percentage down calc
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5031
- **Severity:** Critical
- **Data needed:** VA down-payment/percentage-down calculation fields -- loan_amount and a stated-down-payment field are not currently extracted
- **Rationale:** VA fees-and-charges family.
- **Family:** override
- **SME:** [ ] agree [ ] correct: ______

### G249 — O-VA-55438 [O-VA]
- **Q:** Were all fees and charges requirements met?
- **Defect condition:** Construction loan equity in the property not used as a down payment for calculating the funding fee
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5004
- **Severity:** Critical
- **Data needed:** VA funding-fee / FHA MIP calculation fields (percentage tables, exemption status, loan amount) -- not extracted
- **Rationale:** Crisp percentage-table math once the fields exist; no such fields are in FIELD_SPECS today.
- **Family:** funding_fee_mip
- **SME:** [ ] agree [ ] correct: ______

### G250 — O-VA-50782 [O-VA]
- **Q:** Were all fees and charges requirements met?
- **Defect condition:** Fees, charges or discount pts included in loan amount unallowable or not w/in limits per loan type
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4965
- **Severity:** Critical
- **Data needed:** VA allowable-fee-limit table + loan_amount field -- neither exists today
- **Rationale:** VA fees-and-charges family.
- **Family:** override
- **SME:** [ ] agree [ ] correct: ______

### G251 — O-VA-51682 [O-VA]
- **Q:** Were all fees and charges requirements met?
- **Defect condition:** Funding fee exemption status was not established prior to closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5075
- **Severity:** Critical
- **Data needed:** VA funding-fee / FHA MIP calculation fields (percentage tables, exemption status, loan amount) -- not extracted
- **Rationale:** Crisp percentage-table math once the fields exist; no such fields are in FIELD_SPECS today.
- **Family:** funding_fee_mip
- **SME:** [ ] agree [ ] correct: ______

### G252 — O-VA-50018 [O-VA]
- **Q:** Were all fees and charges requirements met?
- **Defect condition:** Funding fee incorrect due to the wrong percentage selected from the funding fee percentage table
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5380
- **Severity:** Critical
- **Data needed:** VA funding-fee / FHA MIP calculation fields (percentage tables, exemption status, loan amount) -- not extracted
- **Rationale:** Crisp percentage-table math once the fields exist; no such fields are in FIELD_SPECS today.
- **Family:** funding_fee_mip
- **SME:** [ ] agree [ ] correct: ______

### G253 — O-VA-50783 [O-VA]
- **Q:** Were all fees and charges requirements met?
- **Defect condition:** Funding fee was not charged without verifying exempt status
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5056
- **Severity:** Critical
- **Data needed:** VA funding-fee / FHA MIP calculation fields (percentage tables, exemption status, loan amount) -- not extracted
- **Rationale:** Crisp percentage-table math once the fields exist; no such fields are in FIELD_SPECS today.
- **Family:** funding_fee_mip
- **SME:** [ ] agree [ ] correct: ______

### G254 — O-VA-00797 [O-VA]
- **Q:** Were all fees and charges requirements met?
- **Defect condition:** Int rate increase over 1% & not re-uw &/or a new or corrected 1003 not completed, initialed & dated
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5106
- **Severity:** Critical
- **Data needed:** interest-rate-at-application vs interest-rate-at-closing + re-underwrite tracking -- mismo_note_rate is extracted but no 'as originally submitted' comparison point exists
- **Rationale:** VA fees-and-charges family; partial field exists, the comparison logic does not.
- **Family:** override
- **SME:** [ ] agree [ ] correct: ______

### G256 — O-VA-55436 [O-VA]
- **Q:** Were all fees and charges requirements met?
- **Defect condition:** Purchase/construction at least 5% down & percentage not included in total price or construction cost
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5248
- **Severity:** Critical
- **Data needed:** VA down-payment-percentage calculation fields -- same gap as G248
- **Rationale:** Same VA fees-and-charges family as G248.
- **Family:** override
- **SME:** [ ] agree [ ] correct: ______

### G257 — O-VA-50784 [O-VA]
- **Q:** Were all fees and charges requirements met?
- **Defect condition:** The funding fee was calculated incorrectly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5379
- **Severity:** Critical
- **Data needed:** VA funding-fee / FHA MIP calculation fields (percentage tables, exemption status, loan amount) -- not extracted
- **Rationale:** Crisp percentage-table math once the fields exist; no such fields are in FIELD_SPECS today.
- **Family:** funding_fee_mip
- **SME:** [ ] agree [ ] correct: ______

### G258 — O-VA-00643 [O-VA]
- **Q:** Were all fees and charges requirements met?
- **Defect condition:** The sales concessions exceeded 4% of the established reasonable value of the property
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5275
- **Severity:** Critical
- **Data needed:** NOV reasonable-value field + sales-concessions field (4% threshold) -- va_nov doc exists (loan 03) with nov_issue_date extracted, but no reasonable-value or concessions-amount field
- **Rationale:** VA fees-and-charges family; crisp threshold math once fields exist.
- **Family:** override
- **SME:** [ ] agree [ ] correct: ______

### G260 — O-FHA-50701 [O-FHA]
- **Q:** Were all final underwriting decision requirements met?
- **Defect condition:** All eligibility and underwriting requirements not met for nonprofit borrower
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5191, 5192, 5193
- **Severity:** Major
- **Data needed:** HUD Nonprofit Agency Roster cross-reference -- an external roster lookup, not a loan-file fact (same kind of gap as CAIVRS/LDP/GSA, though evidenced by a roster listing rather than a per-loan screenshot)
- **Rationale:** Nonprofit-borrower-eligibility family; no roster document/fixture exists in this pilot's corpus.
- **Family:** nonprofit_eligibility
- **SME:** [ ] agree [ ] correct: ______

### G261 — O-FHA-00859 [O-FHA]
- **Q:** Were all final underwriting decision requirements met?
- **Defect condition:** MI ineligibility was not corrected to clear FHAC case warning/resubmission of file did not occur
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5060
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G262 — O-FHA-02312 [O-FHA]
- **Q:** Were all final underwriting decision requirements met?
- **Defect condition:** The file does not contain the required evidence of the final underwriting decision
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5066
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G263 — O-FHA-50683 [O-FHA]
- **Q:** Were all final underwriting decision requirements met?
- **Defect condition:** The final Form HUD-92900-LT, FHA Loan Underwriting and Transmittal Summary not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5351
- **Severity:** Major
- **Data needed:** Form HUD-92900-LT, FHA Loan Underwriting and Transmittal Summary (distinct from the HUD-92900-A Addendum already extracted for loan 02 -- no HUD-92900-LT document exists in any of the 5 loans)
- **Rationale:** Same distinct-form nuance decision 014 flagged for HUD-92900-B vs -A: HUD-92900-LT is FHA's transmittal/underwriting summary, not the borrower-certification Addendum (hud_92900a) this pilot already parses -- a genuine, separate fixture gap.
- **Family:** hud_92900lt
- **SME:** [ ] agree [ ] correct: ______

### G267 — O-FNM-00048 [O-FNM]
- **Q:** Were all general borrower eligibility requirements met?
- **Defect condition:** Homeownership education req's not met for non-traditional credit borr's or purchase w/ LTV above 95%
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5090
- **Severity:** Critical
- **Data needed:** homeownership-education/housing-counseling completion certificate -- not in corpus
- **Rationale:** Niche counseling-completion document, absent from the corpus.
- **Family:** homeownership_education
- **Guide candidate:** B2-2-01 — General Borrower Eligibility Requirements (PDF p.241)
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **Guide candidate:** B5-7-01 — High LTV Reﬁnance Loan and Borrower Eligibility (PDF p.819)
- **SME:** [ ] agree [ ] correct: ______

### G269 — O-FNM-56092 [O-FNM]
- **Q:** Were all general borrower eligibility requirements met?
- **Defect condition:** SFC 162 not used where there was a discrepancy identified with the Social Security number
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5291
- **Severity:** Critical
- **Data needed:** SSN-discrepancy resolution documentation (SSA verification letter, Form SSA-89/eCBSV) or identity-verification record -- not in corpus
- **Rationale:** SSN-validation family; no such verification record exists in any of the 5 loans.
- **Family:** nonborrowing_spouse_ssn
- **Guide candidate:** B2-2-01 — General Borrower Eligibility Requirements (PDF p.241)
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **Guide candidate:** B2-3-01 — General Property Eligibility (PDF p.258)
- **SME:** [ ] agree [ ] correct: ______

### G270 — O-FNM-50233 [O-FNM]
- **Q:** Were all general borrower eligibility requirements met?
- **Defect condition:** SSN/ITIN discrepancy not resolved & documented using Form SSA–89, eCBSV or 3rd party vendor from SSA
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5287
- **Severity:** Critical
- **Data needed:** SSN-discrepancy resolution documentation (SSA verification letter, Form SSA-89/eCBSV) or identity-verification record -- not in corpus
- **Rationale:** SSN-validation family; no such verification record exists in any of the 5 loans.
- **Family:** nonborrowing_spouse_ssn
- **Guide candidate:** B2-2-01 — General Borrower Eligibility Requirements (PDF p.241)
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **Guide candidate:** B2-3-01 — General Property Eligibility (PDF p.258)
- **SME:** [ ] agree [ ] correct: ______

### G271 — O-FNM-58597 [O-FNM]
- **Q:** Were all general borrower eligibility requirements met?
- **Defect condition:** The file did not document that each borrower has a valid SS number or ITIN
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5307
- **Severity:** Critical
- **Data needed:** SSN-discrepancy resolution documentation (SSA verification letter, Form SSA-89/eCBSV) or identity-verification record -- not in corpus
- **Rationale:** SSN-validation family; no such verification record exists in any of the 5 loans.
- **Family:** nonborrowing_spouse_ssn
- **Guide candidate:** B2-2-01 — General Borrower Eligibility Requirements (PDF p.241)
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **Guide candidate:** B2-3-01 — General Property Eligibility (PDF p.258)
- **SME:** [ ] agree [ ] correct: ______

### G272 — O-FNM-00043 [O-FNM]
- **Q:** Were all general borrower eligibility requirements met?
- **Defect condition:** The identity of each borrower was not confirmed prior to the extension of credit
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4985
- **Severity:** Critical
- **Data needed:** SSN-discrepancy resolution documentation (SSA verification letter, Form SSA-89/eCBSV) or identity-verification record -- not in corpus
- **Rationale:** SSN-validation family; no such verification record exists in any of the 5 loans.
- **Family:** nonborrowing_spouse_ssn
- **Guide candidate:** B2-2-01 — General Borrower Eligibility Requirements (PDF p.241)
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **Guide candidate:** B2-3-01 — General Property Eligibility (PDF p.258)
- **SME:** [ ] agree [ ] correct: ______

### G273 — O-FNM-55425 [O-FNM]
- **Q:** Were all general borrower eligibility requirements met?
- **Defect condition:** Third-party homeownership education content not aligned w/ NIS or HUD's Housing Counseling Program
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5092
- **Severity:** Critical
- **Data needed:** homeownership-education/housing-counseling completion certificate -- not in corpus
- **Rationale:** Niche counseling-completion document, absent from the corpus.
- **Family:** homeownership_education
- **Guide candidate:** B2-2-06 — Homeownership Education and Housing Counseling (PDF p.253)
- **Guide candidate:** B2-2-01 — General Borrower Eligibility Requirements (PDF p.241)
- **Guide candidate:** B3-3.4-14 — Section 8 Housing Choice Voucher Homeownership Program Payments (PDF p.370)
- **SME:** [ ] agree [ ] correct: ______

### G274 — O-RHS-50542 [O-RHS]
- **Q:** Were all general income underwriting requirements met?
- **Defect condition:** Annual income calculated incorrectly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5098
- **Severity:** Critical
- **Data needed:** RHS annual/household-income calculation derivation (income fields are extracted per-borrower on the 1003, but no RHS household-income aggregation/eligible-source-classification logic exists)
- **Rationale:** RHS income-underwriting family; entities/fields partially exist (base_monthly_income_1003, co-borrower income) but the RHS-specific household-income derivation this row needs does not.
- **Family:** rhs_income_calc
- **SME:** [ ] agree [ ] correct: ______

### G275 — O-RHS-50541 [O-RHS]
- **Q:** Were all general income underwriting requirements met?
- **Defect condition:** Annual income used to qualify not from an eligible source
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5048
- **Severity:** Critical
- **Data needed:** RHS annual/household-income calculation derivation (income fields are extracted per-borrower on the 1003, but no RHS household-income aggregation/eligible-source-classification logic exists)
- **Rationale:** RHS income-underwriting family; entities/fields partially exist (base_monthly_income_1003, co-borrower income) but the RHS-specific household-income derivation this row needs does not.
- **Family:** rhs_income_calc
- **SME:** [ ] agree [ ] correct: ______

### G276 — O-RHS-50818 [O-RHS]
- **Q:** Were all general income underwriting requirements met?
- **Defect condition:** Income calculation requirements were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5100
- **Severity:** Critical
- **Data needed:** RHS annual/household-income calculation derivation (income fields are extracted per-borrower on the 1003, but no RHS household-income aggregation/eligible-source-classification logic exists)
- **Rationale:** RHS income-underwriting family; entities/fields partially exist (base_monthly_income_1003, co-borrower income) but the RHS-specific household-income derivation this row needs does not.
- **Family:** rhs_income_calc
- **SME:** [ ] agree [ ] correct: ______

### G277 — O-RHS-54269 [O-RHS]
- **Q:** Were all general income underwriting requirements met?
- **Defect condition:** Income calculations not provided on Attachment 9-B, Uniform Transmittal Summary or equivalent form
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5028
- **Severity:** Critical
- **Data needed:** Attachment 9-B, Uniform Transmittal Summary (RHS income-calculation form) -- not in corpus
- **Rationale:** Niche RHS income-documentation attachment, absent from loan 05.
- **Family:** attachment_9b
- **SME:** [ ] agree [ ] correct: ______

### G278 — O-RHS-50543 [O-RHS]
- **Q:** Were all general income underwriting requirements met?
- **Defect condition:** Income considered for student living away, all req's not met or income used exceeded the first $480
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4955
- **Severity:** Critical
- **Data needed:** RHS annual/household-income calculation derivation (income fields are extracted per-borrower on the 1003, but no RHS household-income aggregation/eligible-source-classification logic exists)
- **Rationale:** RHS income-underwriting family; entities/fields partially exist (base_monthly_income_1003, co-borrower income) but the RHS-specific household-income derivation this row needs does not.
- **Family:** rhs_income_calc
- **SME:** [ ] agree [ ] correct: ______

### G279 — O-RHS-02787 [O-RHS]
- **Q:** Were all general income underwriting requirements met?
- **Defect condition:** One or more income sources were used to qualify that are to be excluded as per RHS guidelines
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5054
- **Severity:** Critical
- **Data needed:** RHS eligible-income-source classification -- not modeled
- **Rationale:** Same RHS income-underwriting family as the rhs_income_calc family (income-source eligibility sub-condition).
- **Family:** override
- **SME:** [ ] agree [ ] correct: ______

### G280 — O-RHS-02757 [O-RHS]
- **Q:** Were all general income underwriting requirements met?
- **Defect condition:** Projected household annual income calculation did not exclude qualified household deductions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5241
- **Severity:** Critical
- **Data needed:** RHS annual/household-income calculation derivation (income fields are extracted per-borrower on the 1003, but no RHS household-income aggregation/eligible-source-classification logic exists)
- **Rationale:** RHS income-underwriting family; entities/fields partially exist (base_monthly_income_1003, co-borrower income) but the RHS-specific household-income derivation this row needs does not.
- **Family:** rhs_income_calc
- **SME:** [ ] agree [ ] correct: ______

### G281 — O-RHS-02861 [O-RHS]
- **Q:** Were all general income underwriting requirements met?
- **Defect condition:** Tax and insurance estimate used as part of the monthly mortgage payment is not accurate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5053
- **Severity:** Critical
- **Data needed:** a general DTI/PITI(A) derivation from urla_liabilities/tradelines + income fields (piti_ratio/dti_ratio today are extracted ONLY from usda_ratio_waiver_doc, present for loan 05/USDA only)
- **Rationale:** Distinct from the already-wired RatioWaiverShape (CHK-UND-002), which tests a narrower USDA-specific condition (ratio exceeds guideline AND no waiver documented); this family covers general ratio-calculation-accuracy and inclusion-of-specific-debt-type conditions across other agencies -- entities exist (tradelines, urla_liabilities) but no general DTI/PITI aggregation derivation exists yet.
- **Family:** dti_piti_ratio_calc
- **SME:** [ ] agree [ ] correct: ______

### G282 — O-RHS-50901 [O-RHS]
- **Q:** Were all general income underwriting requirements met?
- **Defect condition:** The 1008/1077 or other similar document was incomplete, incorrect or not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5361
- **Severity:** Major
- **Data needed:** 1008/1077 Uniform Underwriting and Transmittal Summary -- no such document/field exists for any agency in this pilot
- **Rationale:** A distinct transmittal-summary form from every doc type this pilot currently parses; appears across FNM/FRD/RHS variants of the same underlying gap.
- **Family:** form_1008_1077
- **SME:** [ ] agree [ ] correct: ______

### G283 — O-RHS-02756 [O-RHS]
- **Q:** Were all general income underwriting requirements met?
- **Defect condition:** The underwriter did not include the eligible income of all adult household members
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5242
- **Severity:** Critical
- **Data needed:** RHS annual/household-income calculation derivation (income fields are extracted per-borrower on the 1003, but no RHS household-income aggregation/eligible-source-classification logic exists)
- **Rationale:** RHS income-underwriting family; entities/fields partially exist (base_monthly_income_1003, co-borrower income) but the RHS-specific household-income derivation this row needs does not.
- **Family:** rhs_income_calc
- **SME:** [ ] agree [ ] correct: ______

### G284 — O-RHS-51843 [O-RHS]
- **Q:** Were all general income underwriting requirements met?
- **Defect condition:** Verified changes of income amounts or sources in the ensuing 12 months was not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5101
- **Severity:** Critical
- **Data needed:** RHS annual/household-income calculation derivation (income fields are extracted per-borrower on the 1003, but no RHS household-income aggregation/eligible-source-classification logic exists)
- **Rationale:** RHS income-underwriting family; entities/fields partially exist (base_monthly_income_1003, co-borrower income) but the RHS-specific household-income derivation this row needs does not.
- **Family:** rhs_income_calc
- **SME:** [ ] agree [ ] correct: ______

### G286 — O-VA-00082 [O-VA]
- **Q:** Were all general underwriting requirements met?
- **Defect condition:** A CAIVRS screening was not conducted on all obligors on the loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4991
- **Severity:** Critical
- **Data needed:** caivrs doc type already exists in DOC_TYPES and is present for loan 02 only (05_CAIVRS_LDP_GSA.pdf) but has zero FIELD_SPECS/FACT_SPECS entries -- no 'clear'/'hit' fact is extracted from it, and no loan 01/03/04/05 has this document at all
- **Rationale:** Per decision 016's own precedent, CAIVRS/LDP/GSA screening is treated as an ordinary point-in-time screenshot document (not a live-registry Bucket-C lookup like NMLS) -- ready for Bucket-B-style field extraction once deepened, but genuinely absent as a fixture for 4 of 5 loans.
- **Family:** caivrs_ldp_gsa
- **SME:** [ ] agree [ ] correct: ______

### G287 — O-FRD-50348 [O-FRD]
- **Q:** Were all general underwriting requirements met?
- **Defect condition:** All additional approval condition by the UW were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5342, 5343
- **Severity:** Critical
- **Data needed:** an underwriter approval-conditions checklist -- no such structured list exists today
- **Rationale:** Generic 'were UW conditions cleared' catch-all; needs the conditions to be enumerated per loan, which this pilot doesn't capture.
- **Family:** uw_approval_conditions_generic
- **SME:** [ ] agree [ ] correct: ______

### G289 — O-VA-00655 [O-VA]
- **Q:** Were all general underwriting requirements met?
- **Defect condition:** DTI exceeds 41% or residual income is below VA's minimum and the UW did not justify the approval
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5033
- **Severity:** Critical
- **Data needed:** a general DTI/PITI(A) derivation from urla_liabilities/tradelines + income fields (piti_ratio/dti_ratio today are extracted ONLY from usda_ratio_waiver_doc, present for loan 05/USDA only)
- **Rationale:** Distinct from the already-wired RatioWaiverShape (CHK-UND-002), which tests a narrower USDA-specific condition (ratio exceeds guideline AND no waiver documented); this family covers general ratio-calculation-accuracy and inclusion-of-specific-debt-type conditions across other agencies -- entities exist (tradelines, urla_liabilities) but no general DTI/PITI aggregation derivation exists yet.
- **Family:** dti_piti_ratio_calc
- **SME:** [ ] agree [ ] correct: ______

### G290 — O-FRD-00015 [O-FRD]
- **Q:** Were all general underwriting requirements met?
- **Defect condition:** Foreign origin documents were not filled out in English & were not translated into English
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5030
- **Severity:** Critical
- **Data needed:** a translation-attached fact for foreign-language documents -- not modeled
- **Rationale:** Niche compliance fact, absent from the corpus (no foreign-language document exists in any of the 5 loans).
- **Family:** foreign_language_docs
- **SME:** [ ] agree [ ] correct: ______

### G291 — O-VA-55741 [O-VA]
- **Q:** Were all general underwriting requirements met?
- **Defect condition:** GSA/LDP/VA non-procurement list not checked for excluded program participants
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5079
- **Severity:** Critical
- **Data needed:** caivrs doc type already exists in DOC_TYPES and is present for loan 02 only (05_CAIVRS_LDP_GSA.pdf) but has zero FIELD_SPECS/FACT_SPECS entries -- no 'clear'/'hit' fact is extracted from it, and no loan 01/03/04/05 has this document at all
- **Rationale:** Per decision 016's own precedent, CAIVRS/LDP/GSA screening is treated as an ordinary point-in-time screenshot document (not a live-registry Bucket-C lookup like NMLS) -- ready for Bucket-B-style field extraction once deepened, but genuinely absent as a fixture for 4 of 5 loans.
- **Family:** caivrs_ldp_gsa
- **SME:** [ ] agree [ ] correct: ______

### G292 — O-VA-57890 [O-VA]
- **Q:** Were all general underwriting requirements met?
- **Defect condition:** Loan $144,000 or less w/ partial entitlement & guaranty not $36,000 minus the unrestored entitlement
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5224
- **Severity:** Critical
- **Data needed:** VA loan-amount/entitlement/guaranty-calculation fields (loan_amount is not currently extracted at all; entitlement amount is not extracted from va_coe)
- **Rationale:** Crisp statutory-formula math (all thresholds are stated directly in the AMQ text itself, not invented) once loan_amount and entitlement fields exist -- neither does today.
- **Family:** va_guaranty_calc
- **SME:** [ ] agree [ ] correct: ______

### G293 — O-FRD-55104 [O-FRD]
- **Q:** Were all general underwriting requirements met?
- **Defect condition:** Loan not identified as a caution at delivery via the key# for manual UW after an LPA caution
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4993
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G294 — O-VA-57889 [O-VA]
- **Q:** Were all general underwriting requirements met?
- **Defect condition:** Loan over $144,000 & max guarantee amt was incorrect per the Blue Water Navy Vietnam Veterans Act
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4982
- **Severity:** Critical
- **Data needed:** VA loan-amount/entitlement/guaranty-calculation fields (loan_amount is not currently extracted at all; entitlement amount is not extracted from va_coe)
- **Rationale:** Crisp statutory-formula math (all thresholds are stated directly in the AMQ text itself, not invented) once loan_amount and entitlement fields exist -- neither does today.
- **Family:** va_guaranty_calc
- **SME:** [ ] agree [ ] correct: ______

### G295 — O-VA-52168 [O-VA]
- **Q:** Were all general underwriting requirements met?
- **Defect condition:** Loan over $144,000, married or joint Vets & max guaranty incorrect based on full/partial entitlement
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5119
- **Severity:** Critical
- **Data needed:** VA loan-amount/entitlement/guaranty-calculation fields (loan_amount is not currently extracted at all; entitlement amount is not extracted from va_coe)
- **Rationale:** Crisp statutory-formula math (all thresholds are stated directly in the AMQ text itself, not invented) once loan_amount and entitlement fields exist -- neither does today.
- **Family:** va_guaranty_calc
- **SME:** [ ] agree [ ] correct: ______

### G296 — O-VA-52166 [O-VA]
- **Q:** Were all general underwriting requirements met?
- **Defect condition:** Loan over $144,000, w/ full entitlement & max amt of guaranty was not 25% of the loan amount
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5074
- **Severity:** Critical
- **Data needed:** VA loan-amount/entitlement/guaranty-calculation fields (loan_amount is not currently extracted at all; entitlement amount is not extracted from va_coe)
- **Rationale:** Crisp statutory-formula math (all thresholds are stated directly in the AMQ text itself, not invented) once loan_amount and entitlement fields exist -- neither does today.
- **Family:** va_guaranty_calc
- **SME:** [ ] agree [ ] correct: ______

### G297 — O-VA-52167 [O-VA]
- **Q:** Were all general underwriting requirements met?
- **Defect condition:** Loan over $144,000, w/ partial entitlement & guaranty not 25% of CLL reduced by used entitlement
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5225
- **Severity:** Critical
- **Data needed:** VA loan-amount/entitlement/guaranty-calculation fields (loan_amount is not currently extracted at all; entitlement amount is not extracted from va_coe)
- **Rationale:** Crisp statutory-formula math (all thresholds are stated directly in the AMQ text itself, not invented) once loan_amount and entitlement fields exist -- neither does today.
- **Family:** va_guaranty_calc
- **SME:** [ ] agree [ ] correct: ______

### G298 — O-FRD-00563 [O-FRD]
- **Q:** Were all general underwriting requirements met?
- **Defect condition:** No, credit document(s) exceed age requirements as of the actual/scheduled closing date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4963
- **Severity:** Critical
- **Data needed:** verification-document source/date-of-receipt fields (VOE/VOD/VOM 'directly from source' + document date vs Note date) -- not modeled
- **Rationale:** Freddie Mac credit-document-integrity family; needs new fields on documents that mostly already exist.
- **Family:** credit_doc_aging_integrity
- **SME:** [ ] agree [ ] correct: ______

### G299 — O-FRD-00012 [O-FRD]
- **Q:** Were all general underwriting requirements met?
- **Defect condition:** No, source is not clearly identified for faxed credit documentation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5295
- **Severity:** Critical
- **Data needed:** verification-document source/date-of-receipt fields (VOE/VOD/VOM 'directly from source' + document date vs Note date) -- not modeled
- **Rationale:** Freddie Mac credit-document-integrity family; needs new fields on documents that mostly already exist.
- **Family:** credit_doc_aging_integrity
- **SME:** [ ] agree [ ] correct: ______

### G300 — O-FRD-00011 [O-FRD]
- **Q:** Were all general underwriting requirements met?
- **Defect condition:** No, verification document(s) were not delivered directly to/returned from source of verification
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5296
- **Severity:** Critical
- **Data needed:** verification-document source/date-of-receipt fields (VOE/VOD/VOM 'directly from source' + document date vs Note date) -- not modeled
- **Rationale:** Freddie Mac credit-document-integrity family; needs new fields on documents that mostly already exist.
- **Family:** credit_doc_aging_integrity
- **SME:** [ ] agree [ ] correct: ______

### G301 — O-FRD-55103 [O-FRD]
- **Q:** Were all general underwriting requirements met?
- **Defect condition:** Not manually UW as per req's for caution loans after being submitted & receiving a Caution from LPA
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4994
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G302 — O-VA-51758 [O-VA]
- **Q:** Were all general underwriting requirements met?
- **Defect condition:** The LTV was calculated incorrectly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5153
- **Severity:** Critical
- **Data needed:** loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; appraised_value already is)
- **Rationale:** Crisp ratio math once loan_amount is extracted -- appraisal doc already supplies appraised_value, but no field captures the loan amount itself anywhere in FIELD_SPECS.
- **Family:** ltv_cltv_hcltv
- **SME:** [ ] agree [ ] correct: ______

### G305 — O-FRD-55383 [O-FRD]
- **Q:** Were all general underwriting requirements met?
- **Defect condition:** YTD paystub used to verify income was dated over 30 days before the application received date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5381
- **Severity:** Critical
- **Data needed:** a paystub date field (paystub doc type exists in every loan but extract_loan.py has ZERO FIELD_SPECS entries for it today -- verified by reading the file directly)
- **Rationale:** Bucket-B-style: the document exists in every loan folder, but no field is extracted from it at all -- a genuine and easily-fixed extraction-thinness gap distinct from a missing fixture.
- **Family:** paystub_date_check
- **SME:** [ ] agree [ ] correct: ______

### G307 — O-FNM-55631 [O-FNM]
- **Q:** Were all guarantors, co-signers, or non-occupant borrowers eligibility requirements met?
- **Defect condition:** Manual UW non-occupant & occupying borr 5% down not own funds & LTV >80%/donated funds ineligible
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5186
- **Severity:** Critical
- **Data needed:** loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; appraised_value already is)
- **Rationale:** Crisp ratio math once loan_amount is extracted -- appraisal doc already supplies appraised_value, but no field captures the loan amount itself anywhere in FIELD_SPECS.
- **Family:** ltv_cltv_hcltv
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **Guide candidate:** B5-7-01 — High LTV Reﬁnance Loan and Borrower Eligibility (PDF p.819)
- **SME:** [ ] agree [ ] correct: ______

### G308 — O-FNM-55632 [O-FNM]
- **Q:** Were all guarantors, co-signers, or non-occupant borrowers eligibility requirements met?
- **Defect condition:** Max LTV, CLTV, HCLTV ratio not met as applicable in a loan with a co-signer or non-occupant borrower
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5187
- **Severity:** Critical
- **Data needed:** loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; appraised_value already is)
- **Rationale:** Crisp ratio math once loan_amount is extracted -- appraisal doc already supplies appraised_value, but no field captures the loan amount itself anywhere in FIELD_SPECS.
- **Family:** ltv_cltv_hcltv
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **Guide candidate:** B5-7-01 — High LTV Reﬁnance Loan and Borrower Eligibility (PDF p.819)
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **SME:** [ ] agree [ ] correct: ______

### G310 — O-FNM-57446 [O-FNM]
- **Q:** Were all guarantors, co-signers, or non-occupant borrowers eligibility requirements met?
- **Defect condition:** The guarantor or co-signer did not sign the mortgage or deed of trust note
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5081
- **Severity:** Critical
- **Data needed:** co-signer/guarantor/non-occupying-borrower structured data (URLA parties exist as free text; no field distinguishes borrower role/occupancy intent)
- **Rationale:** Same family as the LTV-for-non-occupying-borrower rules -- needs a borrower-role classification not modeled today.
- **Family:** cosigner_guarantor_noncoocc
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **Guide candidate:** B5-1-01 — High-Balance Mortgage Loan Eligibility and Underwriting (PDF p.715)
- **SME:** [ ] agree [ ] correct: ______

### G311 — O-FNM-55635 [O-FNM]
- **Q:** Were all inter vivos revocable trusts requirements met?
- **Defect condition:** At least 1 inter vivos revocable trustee did not sign the loan documents in a primary residence
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5114
- **Severity:** Critical
- **Data needed:** Living Trust Agreement / inter-vivos-revocable-trust documentation -- not in corpus
- **Rationale:** None of the 5 synthetic loans involves a trust-held title; niche fixture gap.
- **Family:** living_trust
- **Guide candidate:** B2-2-05 — Inter Vivos Revocable Trusts (PDF p.250)
- **Guide candidate:** B8-5-02 — Inter Vivos Revocable Trust Mortgage Documentation and Signature Requirements (PDF p.921)
- **Guide candidate:** C1-2-01 — General Information on Delivering Loan Data and Documents (PDF p.947)
- **SME:** [ ] agree [ ] correct: ______

### G312 — O-FNM-55636 [O-FNM]
- **Q:** Were all inter vivos revocable trusts requirements met?
- **Defect condition:** In a primary residence at least 1 inter vivos revocable trustee will not occupy the subject property
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5113
- **Severity:** Critical
- **Data needed:** Living Trust Agreement / inter-vivos-revocable-trust documentation -- not in corpus
- **Rationale:** None of the 5 synthetic loans involves a trust-held title; niche fixture gap.
- **Family:** living_trust
- **Guide candidate:** B2-2-05 — Inter Vivos Revocable Trusts (PDF p.250)
- **Guide candidate:** B8-5-02 — Inter Vivos Revocable Trust Mortgage Documentation and Signature Requirements (PDF p.921)
- **Guide candidate:** B3-6-03 — Monthly Housing Expense for the Subject Property (PDF p.518)
- **SME:** [ ] agree [ ] correct: ______

### G313 — O-FNM-55634 [O-FNM]
- **Q:** Were all inter vivos revocable trusts requirements met?
- **Defect condition:** Income/assets of at least 1 person forming the inter vivos revocable trust was not used to qualify
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5112
- **Severity:** Critical
- **Data needed:** Living Trust Agreement / inter-vivos-revocable-trust documentation -- not in corpus
- **Rationale:** None of the 5 synthetic loans involves a trust-held title; niche fixture gap.
- **Family:** living_trust
- **Guide candidate:** B2-2-05 — Inter Vivos Revocable Trusts (PDF p.250)
- **Guide candidate:** B8-5-02 — Inter Vivos Revocable Trust Mortgage Documentation and Signature Requirements (PDF p.921)
- **Guide candidate:** B3-3.4-06 — Employment Related Assets as Qualifying Income (PDF p.358)
- **SME:** [ ] agree [ ] correct: ______

### G315 — O-FNM-55633 [O-FNM]
- **Q:** Were all inter vivos revocable trusts requirements met?
- **Defect condition:** Title insurance coverage contained exceptions for the inter vivos revocable trust or the trustees
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5115
- **Severity:** Critical
- **Data needed:** Living Trust Agreement / inter-vivos-revocable-trust documentation -- not in corpus
- **Rationale:** None of the 5 synthetic loans involves a trust-held title; niche fixture gap.
- **Family:** living_trust
- **Guide candidate:** B2-2-05 — Inter Vivos Revocable Trusts (PDF p.250)
- **Guide candidate:** B8-5-02 — Inter Vivos Revocable Trust Mortgage Documentation and Signature Requirements (PDF p.921)
- **Guide candidate:** B7-2-03 — General Title Insurance Coverage (PDF p.861)
- **SME:** [ ] agree [ ] correct: ______

### G316 — O-FNM-55637 [O-FNM]
- **Q:** Were all inter vivos revocable trusts requirements met?
- **Defect condition:** Title is not vested in the inter vivos revocable trustee(s) and the individual borrower(s) names
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5116
- **Severity:** Critical
- **Data needed:** Living Trust Agreement / inter-vivos-revocable-trust documentation -- not in corpus
- **Rationale:** None of the 5 synthetic loans involves a trust-held title; niche fixture gap.
- **Family:** living_trust
- **Guide candidate:** B2-2-05 — Inter Vivos Revocable Trusts (PDF p.250)
- **Guide candidate:** B8-5-02 — Inter Vivos Revocable Trust Mortgage Documentation and Signature Requirements (PDF p.921)
- **Guide candidate:** B2-2-01 — General Borrower Eligibility Requirements (PDF p.241)
- **SME:** [ ] agree [ ] correct: ______

### G318 — O-FNM-50229 [O-FNM]
- **Q:** Were all legal requirements met?
- **Defect condition:** Subject is rented & tenants rights could affect FNMA's interest
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5259
- **Severity:** Critical
- **Data needed:** a rental/lease agreement document -- not modeled
- **Rationale:** Niche landlord-tenant legal family, absent from the corpus.
- **Family:** rental_tenant_rights
- **Guide candidate:** B2-1.4-04 — Temporary Interest Rate Buydowns (PDF p.219)
- **Guide candidate:** B2-1.5-03 — Legal Requirements (PDF p.236)
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **SME:** [ ] agree [ ] correct: ______

### G319 — O-FNM-50228 [O-FNM]
- **Q:** Were all legal requirements met?
- **Defect condition:** The subject's first lien position was not confirmed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5132
- **Severity:** Critical
- **Data needed:** a first-lien-position fact on title_commitment (doc exists in loan 01 only; no such field/fact exists today)
- **Rationale:** Bucket-B-adjacent: title_commitment doc type exists but this specific fact isn't extracted; absent entirely for the other 4 loans.
- **Family:** first_lien_position
- **Guide candidate:** B2-1.5-03 — Legal Requirements (PDF p.236)
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **Guide candidate:** B2-2-07 — First-Generation Homebuyer Loans (PDF p.256)
- **SME:** [ ] agree [ ] correct: ______

### G320 — O-FRD-59238 [O-FRD]
- **Q:** Were all lender contribution requirements met?
- **Defect condition:** Lender credit was not derived from an increase in the interest rate, or was not funded by the lender
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5126
- **Severity:** Critical
- **Data needed:** special-assessment / lender-incentive fields on closing_disclosure (doc exists in every loan; these specific line items are not in FIELD_SPECS)
- **Rationale:** Bucket-B-style, same family flagged in asset-verification's IPC group (decision 017, G148 etc.) -- doc exists, field doesn't.
- **Family:** special_assessment_lender_contrib
- **SME:** [ ] agree [ ] correct: ______

### G321 — O-FRD-59237 [O-FRD]
- **Q:** Were all lender contribution requirements met?
- **Defect condition:** Lender incentive not treated as a sales concession & lender is/affiliated with an interested party
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5128
- **Severity:** Critical
- **Data needed:** special-assessment / lender-incentive fields on closing_disclosure (doc exists in every loan; these specific line items are not in FIELD_SPECS)
- **Rationale:** Bucket-B-style, same family flagged in asset-verification's IPC group (decision 017, G148 etc.) -- doc exists, field doesn't.
- **Family:** special_assessment_lender_contrib
- **SME:** [ ] agree [ ] correct: ______

### G323 — O-FRD-59240 [O-FRD]
- **Q:** Were all lender contribution requirements met?
- **Defect condition:** The lender credit was used for a purpose other than as a credit towards the borrower's closing costs
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5127
- **Severity:** Critical
- **Data needed:** special-assessment / lender-incentive fields on closing_disclosure (doc exists in every loan; these specific line items are not in FIELD_SPECS)
- **Rationale:** Bucket-B-style, same family flagged in asset-verification's IPC group (decision 017, G148 etc.) -- doc exists, field doesn't.
- **Family:** special_assessment_lender_contrib
- **SME:** [ ] agree [ ] correct: ______

### G324 — O-FRD-59235 [O-FRD]
- **Q:** Were all lender contribution requirements met?
- **Defect condition:** The lender incentive cost or value was funded through the mtg transaction (e.g., premium pricing)
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5182
- **Severity:** Critical
- **Data needed:** special-assessment / lender-incentive fields on closing_disclosure (doc exists in every loan; these specific line items are not in FIELD_SPECS)
- **Rationale:** Bucket-B-style, same family flagged in asset-verification's IPC group (decision 017, G148 etc.) -- doc exists, field doesn't.
- **Family:** special_assessment_lender_contrib
- **SME:** [ ] agree [ ] correct: ______

### G325 — O-FRD-59236 [O-FRD]
- **Q:** Were all lender contribution requirements met?
- **Defect condition:** The lender incentive was considered in qualifying (e.g., as a source of funds for closing/reserves)
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5129
- **Severity:** Critical
- **Data needed:** special-assessment / lender-incentive fields on closing_disclosure (doc exists in every loan; these specific line items are not in FIELD_SPECS)
- **Rationale:** Bucket-B-style, same family flagged in asset-verification's IPC group (decision 017, G148 etc.) -- doc exists, field doesn't.
- **Family:** special_assessment_lender_contrib
- **SME:** [ ] agree [ ] correct: ______

### G326 — O-FRD-59234 [O-FRD]
- **Q:** Were all lender contribution requirements met?
- **Defect condition:** The mortgage loan included a lender incentive or lender credit that required repayment
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5262
- **Severity:** Critical
- **Data needed:** special-assessment / lender-incentive fields on closing_disclosure (doc exists in every loan; these specific line items are not in FIELD_SPECS)
- **Rationale:** Bucket-B-style, same family flagged in asset-verification's IPC group (decision 017, G148 etc.) -- doc exists, field doesn't.
- **Family:** special_assessment_lender_contrib
- **SME:** [ ] agree [ ] correct: ______

### G327 — O-FRD-59239 [O-FRD]
- **Q:** Were all lender contribution requirements met?
- **Defect condition:** Third party funds were used to provide a lender credit
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5125
- **Severity:** Critical
- **Data needed:** special-assessment / lender-incentive fields on closing_disclosure (doc exists in every loan; these specific line items are not in FIELD_SPECS)
- **Rationale:** Bucket-B-style, same family flagged in asset-verification's IPC group (decision 017, G148 etc.) -- doc exists, field doesn't.
- **Family:** special_assessment_lender_contrib
- **SME:** [ ] agree [ ] correct: ______

### G329 — O-FHA-50652 [O-FHA]
- **Q:** Were all living trust requirements met?
- **Defect condition:** Property will be held in a living trust without all documentation requirements being met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5137
- **Severity:** Critical
- **Data needed:** Living Trust Agreement / inter-vivos-revocable-trust documentation -- not in corpus
- **Rationale:** None of the 5 synthetic loans involves a trust-held title; niche fixture gap.
- **Family:** living_trust
- **SME:** [ ] agree [ ] correct: ______

### G330 — O-VA-57887 [O-VA]
- **Q:** Were all loan eligibility requirements met?
- **Defect condition:** The VA maximum loan amount was exceeded for the loan type
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5168
- **Severity:** Critical
- **Data needed:** VA loan-amount/entitlement/guaranty-calculation fields (loan_amount is not currently extracted at all; entitlement amount is not extracted from va_coe)
- **Rationale:** Crisp statutory-formula math (all thresholds are stated directly in the AMQ text itself, not invented) once loan_amount and entitlement fields exist -- neither does today.
- **Family:** va_guaranty_calc
- **SME:** [ ] agree [ ] correct: ______

### G331 — O-VA-00658 [O-VA]
- **Q:** Were all loan eligibility requirements met?
- **Defect condition:** The maximum loan amount was not calculated correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5169
- **Severity:** Critical
- **Data needed:** VA loan-amount/entitlement/guaranty-calculation fields (loan_amount is not currently extracted at all; entitlement amount is not extracted from va_coe)
- **Rationale:** Crisp statutory-formula math (all thresholds are stated directly in the AMQ text itself, not invented) once loan_amount and entitlement fields exist -- neither does today.
- **Family:** va_guaranty_calc
- **SME:** [ ] agree [ ] correct: ______

### G332 — O-VA-50761 [O-VA]
- **Q:** Were all loan eligibility requirements met?
- **Defect condition:** Veteran certification that the subject property will be used as their primary residence not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5212
- **Severity:** Critical
- **Data needed:** an occupancy-intent certification / military-orders / lease-review fact -- not currently modeled (no occupancy-related field or fact exists in FIELD_SPECS/FACT_SPECS)
- **Rationale:** Occupancy-eligibility family; several distinct sub-conditions (military unable-to-occupy, group-home leased-to-business, second-home suitability) each need their own new fact, none of which exist today.
- **Family:** occupancy_certification
- **SME:** [ ] agree [ ] correct: ______

### G334 — O-FNM-50223 [O-FNM]
- **Q:** Were all loan limit requirements  met?
- **Defect condition:** The mtg did not meet the loan limits based on loan type as outlined by FNMA
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5070
- **Severity:** Critical
- **Data needed:** the applicable conforming loan limit (by county/loan type) + loan_amount field -- neither is modeled
- **Rationale:** Crisp comparison once both exist; conforming-loan-limit table is an external reference table, not derivable from the loan file alone.
- **Family:** loan_limit_conforming
- **Guide candidate:** B2-1.5-01 — Loan Limits (PDF p.224)
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **SME:** [ ] agree [ ] correct: ______

### G336 — O-RHS-50537 [O-RHS]
- **Q:** Were all loan term requirements met?
- **Defect condition:** Loan would have been granted w/out the RHS guarantee at the same rate-terms
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5141
- **Severity:** Critical
- **Data needed:** RHS loan-term eligibility fields (note rate at closing vs at commitment, amortization term) -- mismo_note_rate is extracted but no 'rate at commitment' comparison point exists
- **Rationale:** RHS loan-term family; partial field exists (mismo_note_rate) but the comparison point this row needs does not.
- **Family:** rhs_loan_term
- **SME:** [ ] agree [ ] correct: ______

### G337 — O-RHS-57147 [O-RHS]
- **Q:** Were all loan term requirements met?
- **Defect condition:** Proposed payment is significantly higher than current housing payment without a repayment analysis
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5246
- **Severity:** Critical
- **Machine checks:** presence of a documented repayment analysis (RHS)
- **Stays human:** 'significantly higher' payment-shock threshold (undefined in the AMQ text)
- **Data needed:** current-housing-payment field + a repayment-analysis document -- neither modeled
- **Rationale:** Compound condition: repayment-analysis presence is a crisp doc-presence check once the doc type exists; 'significantly higher' has no stated numeric threshold in the AMQ text itself, so that half stays human rather than inventing a cutoff.
- **Family:** override
- **SME:** [ ] agree [ ] correct: ______

### G338 — O-RHS-02889 [O-RHS]
- **Q:** Were all loan term requirements met?
- **Defect condition:** The interest rate increased prior to closing rendering the loan ineligible
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5105
- **Severity:** Critical
- **Data needed:** RHS loan-term eligibility fields (note rate at closing vs at commitment, amortization term) -- mismo_note_rate is extracted but no 'rate at commitment' comparison point exists
- **Rationale:** RHS loan-term family; partial field exists (mismo_note_rate) but the comparison point this row needs does not.
- **Family:** rhs_loan_term
- **SME:** [ ] agree [ ] correct: ______

### G339 — O-RHS-50538 [O-RHS]
- **Q:** Were all loan term requirements met?
- **Defect condition:** The loan does not have a term of 30 years
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5145
- **Severity:** Critical
- **Data needed:** RHS loan-term eligibility fields (note rate at closing vs at commitment, amortization term) -- mismo_note_rate is extracted but no 'rate at commitment' comparison point exists
- **Rationale:** RHS loan-term family; partial field exists (mismo_note_rate) but the comparison point this row needs does not.
- **Family:** rhs_loan_term
- **SME:** [ ] agree [ ] correct: ______

### G340 — O-RHS-02890 [O-RHS]
- **Q:** Were all loan term requirements met?
- **Defect condition:** The terms of the loan were ineligible for an RHS guaranteed loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5108
- **Severity:** Critical
- **Data needed:** RHS loan-term eligibility fields (note rate at closing vs at commitment, amortization term) -- mismo_note_rate is extracted but no 'rate at commitment' comparison point exists
- **Rationale:** RHS loan-term family; partial field exists (mismo_note_rate) but the comparison point this row needs does not.
- **Family:** rhs_loan_term
- **SME:** [ ] agree [ ] correct: ______

### G342 — O-RHS-02853 [O-RHS]
- **Q:** Were all manual underwriting requirements met?
- **Defect condition:** Lender did not perform the level of underwriting review appropriate based on the credit score range
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5156
- **Severity:** Critical
- **Data needed:** a credit_score field on credit_report (credit_report doc exists in every loan; no score field is extracted today -- only individual tradelines)
- **Rationale:** Bucket-B-style: the document exists, the specific field does not. (Note: this task's own briefing claimed borrower_credit_score/coborrower_credit_score are already extracted -- checked against extract_loan.py directly via grep and found NOT to be true; no such field or credit-inquiry entity exists anywhere in the extractor today.)
- **Family:** credit_score_threshold
- **SME:** [ ] agree [ ] correct: ______

### G343 — O-RHS-02852 [O-RHS]
- **Q:** Were all manual underwriting requirements met?
- **Defect condition:** Manual UW front ratio over 29% & 100% housing pymt increase w/ risk layers & no strong comp factors
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5226
- **Severity:** Critical
- **Data needed:** a general DTI/PITI(A) derivation from urla_liabilities/tradelines + income fields (piti_ratio/dti_ratio today are extracted ONLY from usda_ratio_waiver_doc, present for loan 05/USDA only)
- **Rationale:** Distinct from the already-wired RatioWaiverShape (CHK-UND-002), which tests a narrower USDA-specific condition (ratio exceeds guideline AND no waiver documented); this family covers general ratio-calculation-accuracy and inclusion-of-specific-debt-type conditions across other agencies -- entities exist (tradelines, urla_liabilities) but no general DTI/PITI aggregation derivation exists yet.
- **Family:** dti_piti_ratio_calc
- **SME:** [ ] agree [ ] correct: ______

### G344 — O-RHS-59421 [O-RHS]
- **Q:** Were all manual underwriting requirements met?
- **Defect condition:** Manually underwritten and submitted loan without the associated documents being uploaded via GUS
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5160
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G345 — O-FRD-50900 [O-FRD]
- **Q:** Were all manual underwriting requirements met?
- **Defect condition:** The 1008/1077 or similar document was incomplete, incorrect or not in the manually underwritten file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5159
- **Severity:** Major
- **Data needed:** 1008/1077 Uniform Underwriting and Transmittal Summary -- no such document/field exists for any agency in this pilot
- **Rationale:** A distinct transmittal-summary form from every doc type this pilot currently parses; appears across FNM/FRD/RHS variants of the same underlying gap.
- **Family:** form_1008_1077
- **SME:** [ ] agree [ ] correct: ______

### G348 — O-FHA-50696 [O-FHA]
- **Q:** Were all manually underwritten final underwriting decision requirements met?
- **Defect condition:** Compensating factors were used to compensate for derogatory credit
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5000
- **Severity:** Critical
- **Data needed:** compensating-factors/extenuating-circumstances documentation on the FHA Transmittal (HUD-92900-LT) or VA Loan Analysis (26-6393) -- neither form is in corpus
- **Rationale:** Same hud_92900lt/va_26_6393 fixture family, compensating-factors sub-condition.
- **Family:** compensating_factors_derogatory
- **SME:** [ ] agree [ ] correct: ______

### G349 — O-FHA-00607 [O-FHA]
- **Q:** Were all manually underwritten final underwriting decision requirements met?
- **Defect condition:** Energy efficient stretch ratios used exceed limits &/or subject did not meet energy efficient req's
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5050
- **Severity:** Critical
- **Data needed:** Energy Efficient Mortgage (EEM) program documentation -- not modeled
- **Rationale:** Niche FHA EEM program family, absent from the corpus.
- **Family:** energy_efficient_mortgage
- **SME:** [ ] agree [ ] correct: ______

### G350 — O-FHA-00606 [O-FHA]
- **Q:** Were all manually underwritten final underwriting decision requirements met?
- **Defect condition:** Loan approved with ratio's exceeding guidelines & compensating factors not noted on the 92900-LT
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5158
- **Severity:** Critical
- **Data needed:** Form HUD-92900-LT, FHA Loan Underwriting and Transmittal Summary (distinct from the HUD-92900-A Addendum already extracted for loan 02 -- no HUD-92900-LT document exists in any of the 5 loans)
- **Rationale:** Same distinct-form nuance decision 014 flagged for HUD-92900-B vs -A: HUD-92900-LT is FHA's transmittal/underwriting summary, not the borrower-certification Addendum (hud_92900a) this pilot already parses -- a genuine, separate fixture gap.
- **Family:** hud_92900lt
- **SME:** [ ] agree [ ] correct: ______

### G351 — O-FHA-50698 [O-FHA]
- **Q:** Were all manually underwritten final underwriting decision requirements met?
- **Defect condition:** Loan or Borrower data elements changed without the loan being re-underwritten
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5270
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G352 — ManualCF [O-FHA]
- **Q:** Were all manually underwritten final underwriting decision requirements met?
- **Defect condition:** Manual UW & no comp factors or ext circumstances (if applic) required by FHA on the FHA Transmittal
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5061
- **Severity:** Critical
- **Data needed:** compensating-factors/extenuating-circumstances documentation on the FHA Transmittal (HUD-92900-LT) or VA Loan Analysis (26-6393) -- neither form is in corpus
- **Rationale:** Same hud_92900lt/va_26_6393 fixture family, compensating-factors sub-condition.
- **Family:** compensating_factors_derogatory
- **SME:** [ ] agree [ ] correct: ______

### G354 — O-FHA-50697 [O-FHA]
- **Q:** Were all manually underwritten final underwriting decision requirements met?
- **Defect condition:** The total PITIA/DTI ratios were not calculated correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5229
- **Severity:** Critical
- **Data needed:** a general DTI/PITI(A) derivation from urla_liabilities/tradelines + income fields (piti_ratio/dti_ratio today are extracted ONLY from usda_ratio_waiver_doc, present for loan 05/USDA only)
- **Rationale:** Distinct from the already-wired RatioWaiverShape (CHK-UND-002), which tests a narrower USDA-specific condition (ratio exceeds guideline AND no waiver documented); this family covers general ratio-calculation-accuracy and inclusion-of-specific-debt-type conditions across other agencies -- entities exist (tradelines, urla_liabilities) but no general DTI/PITI aggregation derivation exists yet.
- **Family:** dti_piti_ratio_calc
- **SME:** [ ] agree [ ] correct: ______

### G357 — O-RHS-02887 [O-RHS]
- **Q:** Were all maximum loan amount requirements met?
- **Defect condition:** The total amount financed exceeded the maximum loan amount limit
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5167
- **Severity:** Critical
- **Data needed:** VA loan-amount/entitlement/guaranty-calculation fields (loan_amount is not currently extracted at all; entitlement amount is not extracted from va_coe)
- **Rationale:** Crisp statutory-formula math (all thresholds are stated directly in the AMQ text itself, not invented) once loan_amount and entitlement fields exist -- neither does today.
- **Family:** va_guaranty_calc
- **SME:** [ ] agree [ ] correct: ______

### G359 — O-FHA-50662 [O-FHA]
- **Q:** Were all maximum mortgage amount requirements met?
- **Defect condition:** The base and/or total loan amount was not calculated correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5140
- **Severity:** Critical
- **Data needed:** loan_amount + adjusted-value fields (appraised_value is extracted; the loan amount itself and FHA's 'adjusted value' concept are not)
- **Rationale:** Same loan_amount-field gap as ltv_cltv_hcltv family.
- **Family:** max_loan_amount_mri
- **SME:** [ ] agree [ ] correct: ______

### G360 — O-FHA-00611 [O-FHA]
- **Q:** Were all maximum mortgage amount requirements met?
- **Defect condition:** The loan amount exceeds the maximum FHA mortgage amount
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5166
- **Severity:** Critical
- **Data needed:** VA loan-amount/entitlement/guaranty-calculation fields (loan_amount is not currently extracted at all; entitlement amount is not extracted from va_coe)
- **Rationale:** Crisp statutory-formula math (all thresholds are stated directly in the AMQ text itself, not invented) once loan_amount and entitlement fields exist -- neither does today.
- **Family:** va_guaranty_calc
- **SME:** [ ] agree [ ] correct: ______

### G362 — O-FHA-00609 [O-FHA]
- **Q:** Were all maximum mortgage amount requirements on a purchase transaction met?
- **Defect condition:** Minimum req'd investment (MRI) was not at least 3.5% of the adjusted value in a purchase
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5176
- **Severity:** Critical
- **Data needed:** loan_amount + adjusted-value fields (appraised_value is extracted; the loan amount itself and FHA's 'adjusted value' concept are not)
- **Rationale:** Same loan_amount-field gap as ltv_cltv_hcltv family.
- **Family:** max_loan_amount_mri
- **SME:** [ ] agree [ ] correct: ______

### G364 — O-FNM-50226 [O-FNM]
- **Q:** Were all modified loan eligibility requirements met?
- **Defect condition:** Mtg Modification changed the loan terms of original Note
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5181
- **Severity:** Critical
- **Data needed:** a mortgage-modification agreement document -- not modeled
- **Rationale:** Niche modified-loan-eligibility family, absent from the corpus.
- **Family:** mortgage_modification
- **Guide candidate:** B2-1.5-02 — Loan Eligibility (PDF p.225)
- **Guide candidate:** B4-2.3-04 — Loan Eligibility for Co-op Share Loans (PDF p.712)
- **Guide candidate:** B5-1-01 — High-Balance Mortgage Loan Eligibility and Underwriting (PDF p.715)
- **SME:** [ ] agree [ ] correct: ______

### G366 — O-FRD-55527 [O-FRD]
- **Q:** Were all monthly debt payment-to-income ratio liability evaluation requirements met?
- **Defect condition:** Debt paid down or PIF to qualify without the source of funds used being eligible and documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5256
- **Severity:** Critical
- **Data needed:** source-of-funds-for-debt-payoff documentation -- ties to the asset-verification large-deposit/source-of-funds family (decisions 017/018)
- **Rationale:** Cross-block with asset-verification's sourcing-documentation gap; not a blind reuse of LargeDepositShape (different condition: paying off a debt vs. an unsourced deposit), flagged not wired.
- **Family:** debt_paydown_source
- **SME:** [ ] agree [ ] correct: ______

### G367 — O-FNM-50196 [O-FNM]
- **Q:** Were all mortgage eligibility requirements  met?
- **Defect condition:** CLTV calculated incorrectly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4999
- **Severity:** Critical
- **Data needed:** loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; appraised_value already is)
- **Rationale:** Crisp ratio math once loan_amount is extracted -- appraisal doc already supplies appraised_value, but no field captures the loan amount itself anywhere in FIELD_SPECS.
- **Family:** ltv_cltv_hcltv
- **Guide candidate:** B5-1-01 — High-Balance Mortgage Loan Eligibility and Underwriting (PDF p.715)
- **Guide candidate:** B5-6-01 — HomeReady Mortgage Loan and Borrower Eligibility (PDF p.808)
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **SME:** [ ] agree [ ] correct: ______

### G368 — O-FNM-50197 [O-FNM]
- **Q:** Were all mortgage eligibility requirements  met?
- **Defect condition:** HCLTV calculated incorrectly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5088
- **Severity:** Critical
- **Data needed:** loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; appraised_value already is)
- **Rationale:** Crisp ratio math once loan_amount is extracted -- appraisal doc already supplies appraised_value, but no field captures the loan amount itself anywhere in FIELD_SPECS.
- **Family:** ltv_cltv_hcltv
- **Guide candidate:** B5-1-01 — High-Balance Mortgage Loan Eligibility and Underwriting (PDF p.715)
- **Guide candidate:** B5-6-01 — HomeReady Mortgage Loan and Borrower Eligibility (PDF p.808)
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **SME:** [ ] agree [ ] correct: ______

### G370 — O-FHA-50755 [O-FHA]
- **Q:** Were all mortgage insurance premium requirements met?
- **Defect condition:** The annual MIP was incorrect based on the LTV, term and product type
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4966
- **Severity:** Critical
- **Data needed:** loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; appraised_value already is)
- **Rationale:** Crisp ratio math once loan_amount is extracted -- appraisal doc already supplies appraised_value, but no field captures the loan amount itself anywhere in FIELD_SPECS.
- **Family:** ltv_cltv_hcltv
- **SME:** [ ] agree [ ] correct: ______

### G371 — O-FHA-00632 [O-FHA]
- **Q:** Were all mortgage insurance premium requirements met?
- **Defect condition:** The upfront mortgage insurance premium (UFMIP) charged was incorrect
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5364
- **Severity:** Critical
- **Data needed:** VA funding-fee / FHA MIP calculation fields (percentage tables, exemption status, loan amount) -- not extracted
- **Rationale:** Crisp percentage-table math once the fields exist; no such fields are in FIELD_SPECS today.
- **Family:** funding_fee_mip
- **SME:** [ ] agree [ ] correct: ______

### G374 — O-FNM-51486 [O-FNM]
- **Q:** Were all multiple financed properties eligibility requirements met?
- **Defect condition:** The borrower exceeded the max limit of 2 financed properties including the subject in a HomeReady
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5093
- **Severity:** Critical
- **Data needed:** a parsed real-estate-owned (REO) schedule entity from the 1003 (the extractor does not yet treat the 1003's REO section as its own entity)
- **Rationale:** Same gap flagged in the asset-verification triage (decision 017, G240/G241) -- the count of financed properties isn't derived anywhere today.
- **Family:** reo_schedule
- **Guide candidate:** B2-2-03 — Multiple Financed Properties for the Same Borrower (PDF p.244)
- **Guide candidate:** B5-6-01 — HomeReady Mortgage Loan and Borrower Eligibility (PDF p.808)
- **Guide candidate:** B2-2-01 — General Borrower Eligibility Requirements (PDF p.241)
- **SME:** [ ] agree [ ] correct: ______

### G375 — O-FNM-50235 [O-FNM]
- **Q:** Were all multiple financed properties eligibility requirements met?
- **Defect condition:** The file did not document sufficient assets to meet the reserve requirement
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5266
- **Severity:** Critical
- **Data needed:** a parsed real-estate-owned (REO) schedule entity from the 1003 (the extractor does not yet treat the 1003's REO section as its own entity)
- **Rationale:** Same gap flagged in the asset-verification triage (decision 017, G240/G241) -- the count of financed properties isn't derived anywhere today.
- **Family:** reo_schedule
- **Guide candidate:** B2-2-03 — Multiple Financed Properties for the Same Borrower (PDF p.244)
- **Guide candidate:** A2-2-03 — Document Warranties (PDF p.36)
- **Guide candidate:** A2-3.2-02 — Enforcement Relief for Breaches of Certain Representations and Warranties Related to Underwriting and Eligibility (PDF p.65)
- **SME:** [ ] agree [ ] correct: ______

### G376 — O-FNM-50234 [O-FNM]
- **Q:** Were all multiple financed properties eligibility requirements met?
- **Defect condition:** The number of financed properties exceeded guidelines
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5183
- **Severity:** Critical
- **Data needed:** a parsed real-estate-owned (REO) schedule entity from the 1003 (the extractor does not yet treat the 1003's REO section as its own entity)
- **Rationale:** Same gap flagged in the asset-verification triage (decision 017, G240/G241) -- the count of financed properties isn't derived anywhere today.
- **Family:** reo_schedule
- **Guide candidate:** B2-2-03 — Multiple Financed Properties for the Same Borrower (PDF p.244)
- **Guide candidate:** A2-3.2-02 — Enforcement Relief for Breaches of Certain Representations and Warranties Related to Underwriting and Eligibility (PDF p.65)
- **Guide candidate:** A4-1-01 — Maintaining Seller/Servicer Eligibility (PDF p.151)
- **SME:** [ ] agree [ ] correct: ______

### G377 — O-FNM-54873 [O-FNM]
- **Q:** Were all multiple financed properties eligibility requirements met?
- **Defect condition:** The subject loan is a second home or investment property & the loan was not DU underwritten
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5189
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **Guide candidate:** B2-2-03 — Multiple Financed Properties for the Same Borrower (PDF p.244)
- **Guide candidate:** B2-1.2-03 — Home Equity Combined Loan-to-Value (HCLTV) Ratios (PDF p.182)
- **Guide candidate:** B2-1.5-02 — Loan Eligibility (PDF p.225)
- **SME:** [ ] agree [ ] correct: ______

### G378 — O-FNM-50227 [O-FNM]
- **Q:** Were all nonstandard payment collection options eligibility requirements met?
- **Defect condition:** A non-monthly payment option offered without a separate agreement
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5340
- **Severity:** Critical
- **Data needed:** a non-standard-payment-option agreement document -- not modeled
- **Rationale:** Niche FNM payment-collection family, absent from the corpus.
- **Family:** nonstandard_payment_option
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **Guide candidate:** A2-2-02 — Delivery Information and Delivery-Option Speciﬁc Representations and Warranties (PDF p.34)
- **Guide candidate:** A2-3.2-02 — Enforcement Relief for Breaches of Certain Representations and Warranties Related to Underwriting and Eligibility (PDF p.65)
- **SME:** [ ] agree [ ] correct: ______

### G381 — O-FNM-00046 [O-FNM]
- **Q:** Were all non–U.S. citizen borrower eligibility requirements met?
- **Defect condition:** The applicant is a non-US citizen not legally present in the United States
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5197
- **Severity:** Critical
- **Data needed:** citizenship/residency-status documentation (USCIS determination, alien-registration evidence) -- not in corpus
- **Rationale:** Citizenship/residency family; not modeled at all in this pilot (same gap flagged for asset-verification's G284, decision 017).
- **Family:** citizenship_residency
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **Guide candidate:** B2-2-01 — General Borrower Eligibility Requirements (PDF p.241)
- **Guide candidate:** B5-3.2-02 — HomeStyle Renovation Mortgages: Loan and Borrower Eligibility (PDF p.747)
- **SME:** [ ] agree [ ] correct: ______

### G382 — O-FNM-55773 [O-FNM]
- **Q:** Were all occupancy type requirements  met?
- **Defect condition:** All borrowers were not individuals for a group home investment property leased to business entities
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5076
- **Severity:** Critical
- **Data needed:** an occupancy-intent certification / military-orders / lease-review fact -- not currently modeled (no occupancy-related field or fact exists in FIELD_SPECS/FACT_SPECS)
- **Rationale:** Occupancy-eligibility family; several distinct sub-conditions (military unable-to-occupy, group-home leased-to-business, second-home suitability) each need their own new fact, none of which exist today.
- **Family:** occupancy_certification
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **Guide candidate:** B2-1.1-01 — Occupancy Types (PDF p.175)
- **Guide candidate:** B2-1.2-03 — Home Equity Combined Loan-to-Value (HCLTV) Ratios (PDF p.182)
- **SME:** [ ] agree [ ] correct: ______

### G383 — O-FNM-50194 [O-FNM]
- **Q:** Were all occupancy type requirements  met?
- **Defect condition:** All occupancy eligibility requirements were not met for the occupancy type
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5213
- **Severity:** Critical
- **Data needed:** an occupancy-intent certification / military-orders / lease-review fact -- not currently modeled (no occupancy-related field or fact exists in FIELD_SPECS/FACT_SPECS)
- **Rationale:** Occupancy-eligibility family; several distinct sub-conditions (military unable-to-occupy, group-home leased-to-business, second-home suitability) each need their own new fact, none of which exist today.
- **Family:** occupancy_certification
- **Guide candidate:** A2-3.2-02 — Enforcement Relief for Breaches of Certain Representations and Warranties Related to Underwriting and Eligibility (PDF p.65)
- **Guide candidate:** A4-1-01 — Maintaining Seller/Servicer Eligibility (PDF p.151)
- **Guide candidate:** B2-1.1-01 — Occupancy Types (PDF p.175)
- **SME:** [ ] agree [ ] correct: ______

### G384 — O-FNM-50195 [O-FNM]
- **Q:** Were all occupancy type requirements  met?
- **Defect condition:** LTV calculated incorrectly or info put in AUS to calculate LTV incorrect
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5151
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **Guide candidate:** B2-1.1-01 — Occupancy Types (PDF p.175)
- **Guide candidate:** B2-1.2-01 — Loan-to-Value (LTV) Ratios (PDF p.179)
- **Guide candidate:** B5-7-01 — High LTV Reﬁnance Loan and Borrower Eligibility (PDF p.819)
- **SME:** [ ] agree [ ] correct: ______

### G385 — O-FNM-55439 [O-FNM]
- **Q:** Were all occupancy type requirements  met?
- **Defect condition:** Military orders not obtained evidencing active duty as reason borr unable to occupy as per the mtg
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4960
- **Severity:** Critical
- **Data needed:** DD Form 214 / military orders documentation -- not in corpus
- **Rationale:** Military-service-verification family, absent from the corpus.
- **Family:** dd214_military
- **Guide candidate:** B2-1.1-01 — Occupancy Types (PDF p.175)
- **Guide candidate:** B3-3.3-05 — Military Income (PDF p.342)
- **Guide candidate:** C3-2-03 — MBS Remittance Type and Selecting a Remittance Cycle (PDF p.1003)
- **SME:** [ ] agree [ ] correct: ______

### G386 — O-FNM-00726 [O-FNM]
- **Q:** Were all occupancy type requirements  met?
- **Defect condition:** The LTV ratio is higher than Fannie Mae’s maximum allowable ratio
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5172
- **Severity:** Critical
- **Data needed:** loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; appraised_value already is)
- **Rationale:** Crisp ratio math once loan_amount is extracted -- appraisal doc already supplies appraised_value, but no field captures the loan amount itself anywhere in FIELD_SPECS.
- **Family:** ltv_cltv_hcltv
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** A2-5-01 — Fannie Mae Trade Name and Trademarks (PDF p.102)
- **Guide candidate:** A3-1-01 — Fannie Mae’s Technology Products (PDF p.106)
- **SME:** [ ] agree [ ] correct: ______

### G388 — O-FHA-55900 [O-FHA]
- **Q:** Were all principal residence occupancy requirements met?
- **Defect condition:** Employment, utilities, direct TPV docs do not evidence the subject as the primary in streamline refi
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5301
- **Severity:** Critical
- **Data needed:** an occupancy-intent certification / military-orders / lease-review fact -- not currently modeled (no occupancy-related field or fact exists in FIELD_SPECS/FACT_SPECS)
- **Rationale:** Occupancy-eligibility family; several distinct sub-conditions (military unable-to-occupy, group-home leased-to-business, second-home suitability) each need their own new fact, none of which exist today.
- **Family:** occupancy_certification
- **SME:** [ ] agree [ ] correct: ______

### G389 — O-FHA-00552 [O-FHA]
- **Q:** Were all principal residence occupancy requirements met?
- **Defect condition:** Evidence at least 1 borrower intends to occupy the subject as their primary home was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5238
- **Severity:** Critical
- **Data needed:** an occupancy-intent certification / military-orders / lease-review fact -- not currently modeled (no occupancy-related field or fact exists in FIELD_SPECS/FACT_SPECS)
- **Rationale:** Occupancy-eligibility family; several distinct sub-conditions (military unable-to-occupy, group-home leased-to-business, second-home suitability) each need their own new fact, none of which exist today.
- **Family:** occupancy_certification
- **SME:** [ ] agree [ ] correct: ______

### G392 — O-VA-00865 [O-VA]
- **Q:** Were all prior approval lending requirements met?
- **Defect condition:** The loan was not submitted to VA within 60 days of closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5082
- **Severity:** Critical
- **Data needed:** a VA-submission-date fact -- not modeled (no field captures when the loan was submitted to VA post-closing)
- **Rationale:** Niche VA prior-approval timing fact, absent from the corpus.
- **Family:** va_60day_submission
- **SME:** [ ] agree [ ] correct: ______

### G393 — O-VA-56207 [O-VA]
- **Q:** Were all prior approval lending requirements met?
- **Defect condition:** VA Form 26-1820 was not fully completed, executed, and dated by all applicable parties
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5102
- **Severity:** Critical
- **Data needed:** VA Form 26-1820 (Report and Certification of Loan Disbursement) -- not in corpus
- **Rationale:** Niche post-closing VA form, absent from loan 03.
- **Family:** va_26_1820
- **SME:** [ ] agree [ ] correct: ______

### G394 — O-VA-50008 [O-VA]
- **Q:** Were all prior approval lending requirements met?
- **Defect condition:** VA Form 26-1820, Report and Certification of Loan Disbursement is not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5375
- **Severity:** Critical
- **Data needed:** VA Form 26-1820 (Report and Certification of Loan Disbursement) -- not in corpus
- **Rationale:** Niche post-closing VA form, absent from loan 03.
- **Family:** va_26_1820
- **SME:** [ ] agree [ ] correct: ______

### G395 — O-FHA-50658 [O-FHA]
- **Q:** Were all property type and/or investment property requirements met?
- **Defect condition:** Form HUD-92561, Contract with Respect to Hotel and Transient Use, is req'd & not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5094
- **Severity:** Major
- **Data needed:** Form HUD-92561 (Hotel and Transient Use) -- not in corpus
- **Rationale:** Niche FHA property-type form, absent from loan 02.
- **Family:** hud_92561
- **SME:** [ ] agree [ ] correct: ______

### G396 — O-FHA-50659 [O-FHA]
- **Q:** Were all property type and/or investment property requirements met?
- **Defect condition:** Mixed-use -Less than 51%  sq ft residential &/or possible health/safety concerns
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5180
- **Severity:** Critical
- **Data needed:** specific property-type/investment-eligibility facts (self-sufficiency rental income calc, multi-unit financial-interest count, mixed-use square footage) -- none modeled today
- **Rationale:** Niche FHA/FNM property-type family, absent from the corpus.
- **Family:** property_investment_niche
- **SME:** [ ] agree [ ] correct: ______

### G397 — O-FHA-50660 [O-FHA]
- **Q:** Were all property type and/or investment property requirements met?
- **Defect condition:** Net self-sufficiency rental Income was calculated incorrectly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5283
- **Severity:** Critical
- **Data needed:** specific property-type/investment-eligibility facts (self-sufficiency rental income calc, multi-unit financial-interest count, mixed-use square footage) -- none modeled today
- **Rationale:** Niche FHA/FNM property-type family, absent from the corpus.
- **Family:** property_investment_niche
- **SME:** [ ] agree [ ] correct: ______

### G399 — O-FHA-51051 [O-FHA]
- **Q:** Were all property type and/or investment property requirements met?
- **Defect condition:** The borr has a financial interest in more than 7 units w/in 2 blocks in an investment transaction
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5044
- **Severity:** Critical
- **Data needed:** specific property-type/investment-eligibility facts (self-sufficiency rental income calc, multi-unit financial-interest count, mixed-use square footage) -- none modeled today
- **Rationale:** Niche FHA/FNM property-type family, absent from the corpus.
- **Family:** property_investment_niche
- **SME:** [ ] agree [ ] correct: ______

### G401 — O-FHA-52903 [O-FHA]
- **Q:** Were all resident alien status requirements met?
- **Defect condition:** Residency status of the borrower was not determined using the 1003 & other applicable documentation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5369
- **Severity:** Critical
- **Data needed:** citizenship/residency-status documentation (USCIS determination, alien-registration evidence) -- not in corpus
- **Rationale:** Citizenship/residency family; not modeled at all in this pilot (same gap flagged for asset-verification's G284, decision 017).
- **Family:** citizenship_residency
- **SME:** [ ] agree [ ] correct: ______

### G402 — O-FHA-00078 [O-FHA]
- **Q:** Were all resident alien status requirements met?
- **Defect condition:** The borrower(s) is a permanent resident alien, but permanent residency is not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5267
- **Severity:** Critical
- **Data needed:** citizenship/residency-status documentation (USCIS determination, alien-registration evidence) -- not in corpus
- **Rationale:** Citizenship/residency family; not modeled at all in this pilot (same gap flagged for asset-verification's G284, decision 017).
- **Family:** citizenship_residency
- **SME:** [ ] agree [ ] correct: ______

### G403 — O-FHA-50653 [O-FHA]
- **Q:** Were all secondary residence occupancy requirements met?
- **Defect condition:** For a second home, all requirements not met and all required documentation not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5277
- **Severity:** Critical
- **Data needed:** an occupancy-intent certification / military-orders / lease-review fact -- not currently modeled (no occupancy-related field or fact exists in FIELD_SPECS/FACT_SPECS)
- **Rationale:** Occupancy-eligibility family; several distinct sub-conditions (military unable-to-occupy, group-home leased-to-business, second-home suitability) each need their own new fact, none of which exist today.
- **Family:** occupancy_certification
- **SME:** [ ] agree [ ] correct: ______

### G406 — O-FNM-50225 [O-FNM]
- **Q:** Were all special assessment eligibility requirements met?
- **Defect condition:** Special assessments not PIF & mtg not reduced by amt of unpaid assessments
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5292
- **Severity:** Critical
- **Data needed:** loan_amount + adjusted-value fields (appraised_value is extracted; the loan amount itself and FHA's 'adjusted value' concept are not)
- **Rationale:** Same loan_amount-field gap as ltv_cltv_hcltv family.
- **Family:** max_loan_amount_mri
- **Guide candidate:** B2-3-02 — Special Property Eligibility and Underwriting Considerations: Factory-Built Housing (PDF p.261)
- **Guide candidate:** B2-3-03 — Special Property Eligibility and Underwriting Considerations: Leasehold Estates (PDF p.268)
- **Guide candidate:** B2-3-04 — Special Property Eligibility Considerations (PDF p.274)
- **SME:** [ ] agree [ ] correct: ______

### G407 — O-FNM-55629 [O-FNM]
- **Q:** Were all special assessment eligibility requirements met?
- **Defect condition:** The file did not document the current/future installments of taxes and special assessments
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5294
- **Severity:** Critical
- **Data needed:** special-assessment / lender-incentive fields on closing_disclosure (doc exists in every loan; these specific line items are not in FIELD_SPECS)
- **Rationale:** Bucket-B-style, same family flagged in asset-verification's IPC group (decision 017, G148 etc.) -- doc exists, field doesn't.
- **Family:** special_assessment_lender_contrib
- **Guide candidate:** B2-3-02 — Special Property Eligibility and Underwriting Considerations: Factory-Built Housing (PDF p.261)
- **Guide candidate:** B2-3-03 — Special Property Eligibility and Underwriting Considerations: Leasehold Estates (PDF p.268)
- **Guide candidate:** B2-3-04 — Special Property Eligibility Considerations (PDF p.274)
- **SME:** [ ] agree [ ] correct: ______

### G408 — O-FRD-50412 [O-FRD]
- **Q:** Were all special borrower eligibility requirements met?
- **Defect condition:** All title requirements not met when the borrower is a Living Trust
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5139
- **Severity:** Critical
- **Data needed:** Living Trust Agreement / inter-vivos-revocable-trust documentation -- not in corpus
- **Rationale:** None of the 5 synthetic loans involves a trust-held title; niche fixture gap.
- **Family:** living_trust
- **SME:** [ ] agree [ ] correct: ______

### G409 — O-FRD-50411 [O-FRD]
- **Q:** Were all special borrower eligibility requirements met?
- **Defect condition:** LTV/or ratios calculated incorrect based on UW type with a non-occ borrower
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5188
- **Severity:** Critical
- **Data needed:** loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; appraised_value already is)
- **Rationale:** Crisp ratio math once loan_amount is extracted -- appraisal doc already supplies appraised_value, but no field captures the loan amount itself anywhere in FIELD_SPECS.
- **Family:** ltv_cltv_hcltv
- **SME:** [ ] agree [ ] correct: ______

### G411 — O-FRD-00040 [O-FRD]
- **Q:** Were all special borrower eligibility requirements met?
- **Defect condition:** The applicant is a non-US citizen and does not have lawful residency status in the United States
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5227
- **Severity:** Critical
- **Data needed:** citizenship/residency-status documentation (USCIS determination, alien-registration evidence) -- not in corpus
- **Rationale:** Citizenship/residency family; not modeled at all in this pilot (same gap flagged for asset-verification's G284, decision 017).
- **Family:** citizenship_residency
- **SME:** [ ] agree [ ] correct: ______

### G412 — O-FRD-56486 [O-FRD]
- **Q:** Were all special borrower eligibility requirements met?
- **Defect condition:** The maximum LTV ratio for a manually underwritten loan with a non-occupying borrower exceeds 90%
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5161
- **Severity:** Critical
- **Data needed:** loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; appraised_value already is)
- **Rationale:** Crisp ratio math once loan_amount is extracted -- appraisal doc already supplies appraised_value, but no field captures the loan amount itself anywhere in FIELD_SPECS.
- **Family:** ltv_cltv_hcltv
- **SME:** [ ] agree [ ] correct: ______

### G413 — O-FRD-56485 [O-FRD]
- **Q:** Were all special borrower eligibility requirements met?
- **Defect condition:** The maximum LTV ratio for an Accept Mortgage with a non-occupying borrower exceeds 95%
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4958
- **Severity:** Critical
- **Data needed:** loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; appraised_value already is)
- **Rationale:** Crisp ratio math once loan_amount is extracted -- appraisal doc already supplies appraised_value, but no field captures the loan amount itself anywhere in FIELD_SPECS.
- **Family:** ltv_cltv_hcltv
- **SME:** [ ] agree [ ] correct: ______

### G414 — O-FRD-56487 [O-FRD]
- **Q:** Were all special borrower eligibility requirements met?
- **Defect condition:** The non-occupying borrower is an interested party, such as the builder, seller, realtor or broker
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5109
- **Severity:** Critical
- **Data needed:** an occupancy-intent certification / military-orders / lease-review fact -- not currently modeled (no occupancy-related field or fact exists in FIELD_SPECS/FACT_SPECS)
- **Rationale:** Occupancy-eligibility family; several distinct sub-conditions (military unable-to-occupy, group-home leased-to-business, second-home suitability) each need their own new fact, none of which exist today.
- **Family:** occupancy_certification
- **SME:** [ ] agree [ ] correct: ______

### G415 — O-FRD-50413 [O-FRD]
- **Q:** Were all special borrower eligibility requirements met?
- **Defect condition:** Trust Agreement not in the file where the borrower is a Living Trust
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5138
- **Severity:** Critical
- **Data needed:** Living Trust Agreement / inter-vivos-revocable-trust documentation -- not in corpus
- **Rationale:** None of the 5 synthetic loans involves a trust-held title; niche fixture gap.
- **Family:** living_trust
- **SME:** [ ] agree [ ] correct: ______

### G416 — O-RHS-02839 [O-RHS]
- **Q:** Were all total debt ratio calculation requirements met?
- **Defect condition:** A 30-day account balance with late payment > 12 months; 5% of the payment is not included in DTI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4951
- **Severity:** Critical
- **Data needed:** a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- **Rationale:** Every one of these RHS/FHA/VA 'was a specific debt type included in DTI' rows is individually crisp math (a rule engine could apply it), but needs a DTI-aggregation + liability-classification layer that does not exist yet -- no new document required, a real derivation-logic gap.
- **Family:** debt_ratio_inclusion
- **SME:** [ ] agree [ ] correct: ______

### G417 — O-RHS-02840 [O-RHS]
- **Q:** Were all total debt ratio calculation requirements met?
- **Defect condition:** Alimony/child support/garnishments/other court ordered debts were excluded from DTI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5008
- **Severity:** Critical
- **Data needed:** delinquent-child-support repayment-history documentation -- not modeled
- **Rationale:** Niche RHS credit-eligibility sub-condition, absent from the corpus.
- **Family:** delinquent_child_support_credit
- **SME:** [ ] agree [ ] correct: ______

### G418 — O-RHS-55313 [O-RHS]
- **Q:** Were all total debt ratio calculation requirements met?
- **Defect condition:** Borr is in a debt management plan & the monthly counseling plan payment was not included in the DTI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5020
- **Severity:** Critical
- **Data needed:** a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- **Rationale:** Every one of these RHS/FHA/VA 'was a specific debt type included in DTI' rows is individually crisp math (a rule engine could apply it), but needs a DTI-aggregation + liability-classification layer that does not exist yet -- no new document required, a real derivation-logic gap.
- **Family:** debt_ratio_inclusion
- **SME:** [ ] agree [ ] correct: ______

### G419 — O-RHS-02838 [O-RHS]
- **Q:** Were all total debt ratio calculation requirements met?
- **Defect condition:** Credit report did not report a payment on a revolving account and 5% of the balance was not used
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5273
- **Severity:** Critical
- **Data needed:** a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- **Rationale:** Every one of these RHS/FHA/VA 'was a specific debt type included in DTI' rows is individually crisp math (a rule engine could apply it), but needs a DTI-aggregation + liability-classification layer that does not exist yet -- no new document required, a real derivation-logic gap.
- **Family:** debt_ratio_inclusion
- **SME:** [ ] agree [ ] correct: ______

### G420 — O-RHS-55312 [O-RHS]
- **Q:** Were all total debt ratio calculation requirements met?
- **Defect condition:** Late mtg pymts on borr's rental property within 12 mos prior to app & the  full PITIA not in DTI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5260
- **Severity:** Critical
- **Data needed:** a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- **Rationale:** Every one of these RHS/FHA/VA 'was a specific debt type included in DTI' rows is individually crisp math (a rule engine could apply it), but needs a DTI-aggregation + liability-classification layer that does not exist yet -- no new document required, a real derivation-logic gap.
- **Family:** debt_ratio_inclusion
- **SME:** [ ] agree [ ] correct: ______

### G421 — O-RHS-55994 [O-RHS]
- **Q:** Were all total debt ratio calculation requirements met?
- **Defect condition:** Outstanding student loan credit report/actual documented pymt not used or 0.5% of the balance if $0
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5303
- **Severity:** Critical
- **Data needed:** a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- **Rationale:** Every one of these RHS/FHA/VA 'was a specific debt type included in DTI' rows is individually crisp math (a rule engine could apply it), but needs a DTI-aggregation + liability-classification layer that does not exist yet -- no new document required, a real derivation-logic gap.
- **Family:** debt_ratio_inclusion
- **SME:** [ ] agree [ ] correct: ______

### G422 — O-RHS-55993 [O-RHS]
- **Q:** Were all total debt ratio calculation requirements met?
- **Defect condition:** Payment amt used was not the credit report amt & no documentation to support the alternate amt used
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5217
- **Severity:** Critical
- **Data needed:** a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- **Rationale:** Every one of these RHS/FHA/VA 'was a specific debt type included in DTI' rows is individually crisp math (a rule engine could apply it), but needs a DTI-aggregation + liability-classification layer that does not exist yet -- no new document required, a real derivation-logic gap.
- **Family:** debt_ratio_inclusion
- **SME:** [ ] agree [ ] correct: ______

### G423 — O-RHS-55315 [O-RHS]
- **Q:** Were all total debt ratio calculation requirements met?
- **Defect condition:** Student loan pymt not in DTI as req'd even if paid by another party or in a forgiveness loan program
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5302
- **Severity:** Critical
- **Data needed:** a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- **Rationale:** Every one of these RHS/FHA/VA 'was a specific debt type included in DTI' rows is individually crisp math (a rule engine could apply it), but needs a DTI-aggregation + liability-classification layer that does not exist yet -- no new document required, a real derivation-logic gap.
- **Family:** debt_ratio_inclusion
- **SME:** [ ] agree [ ] correct: ______

### G424 — O-RHS-02849 [O-RHS]
- **Q:** Were all total debt ratio calculation requirements met?
- **Defect condition:** The DTI debt ratio was calculated incorrectly and/or the ratio did not meet requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5032
- **Severity:** Critical
- **Data needed:** a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- **Rationale:** Every one of these RHS/FHA/VA 'was a specific debt type included in DTI' rows is individually crisp math (a rule engine could apply it), but needs a DTI-aggregation + liability-classification layer that does not exist yet -- no new document required, a real derivation-logic gap.
- **Family:** debt_ratio_inclusion
- **SME:** [ ] agree [ ] correct: ______

### G425 — O-RHS-02842 [O-RHS]
- **Q:** Were all total debt ratio calculation requirements met?
- **Defect condition:** Unsatisfied prior mortgage not in DTI; evidence another obligor has made payments 12 months missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5236
- **Severity:** Critical
- **Data needed:** a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- **Rationale:** Every one of these RHS/FHA/VA 'was a specific debt type included in DTI' rows is individually crisp math (a rule engine could apply it), but needs a DTI-aggregation + liability-classification layer that does not exist yet -- no new document required, a real derivation-logic gap.
- **Family:** debt_ratio_inclusion
- **SME:** [ ] agree [ ] correct: ______

### G427 — O-VA-57254 [O-VA]
- **Q:** Were all underwriting documentation requirements met?
- **Defect condition:** COE non-exempt & non-active duty borr w/ a pre-discharge claim pending & updated COE not obtained
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5247
- **Severity:** Critical
- **Data needed:** VA pending-disability-claim / National-Guard-service-days documentation -- not modeled
- **Rationale:** Niche VA eligibility sub-conditions, absent from the corpus.
- **Family:** va_pending_claim_rating
- **SME:** [ ] agree [ ] correct: ______

### G428 — ManualCF-2 [O-VA]
- **Q:** Were all underwriting documentation requirements met?
- **Defect condition:** Manual UW & no comp factors or ext circumstances (if applic) required by VA on the VA Loan analysis
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5373
- **Severity:** Critical
- **Data needed:** VA Form 26-6393 (VA Loan Analysis) -- not in any synthetic loan folder
- **Rationale:** Niche VA underwriting-analysis form; loan 03 (the pilot's only VA loan) does not contain this document.
- **Family:** va_26_6393
- **SME:** [ ] agree [ ] correct: ______

### G429 — O-VA-54815 [O-VA]
- **Q:** Were all underwriting documentation requirements met?
- **Defect condition:** No verif active duty funding fee exempt w/pend pre-discharge claim & no proposed/memorandum rating
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4959
- **Severity:** Critical
- **Data needed:** VA pending-disability-claim / National-Guard-service-days documentation -- not modeled
- **Rationale:** Niche VA eligibility sub-conditions, absent from the corpus.
- **Family:** va_pending_claim_rating
- **SME:** [ ] agree [ ] correct: ______

### G430 — O-VA-52871 [O-VA]
- **Q:** Were all underwriting documentation requirements met?
- **Defect condition:** Non-supervised automatic lender & UW is not VA approved and/or registered as the lender's employee
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5371
- **Severity:** Critical
- **Data needed:** underwriter VA-approval/registration status (staff credential, not a loan fact)
- **Rationale:** Same institutional-staff-credential pattern as de_certification -- possible Bucket-C candidate, flagged not decided.
- **Family:** va_uw_credentialing
- **SME:** [ ] agree [ ] correct: ______

### G432 — O-VA-54171 [O-VA]
- **Q:** Were all underwriting documentation requirements met?
- **Defect condition:** VA Form 26-8937 was submitted to VA for information already listed on the COE
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5378
- **Severity:** Critical
- **Data needed:** VA Form 26-8937 (Verification of VA Benefits) -- not in corpus
- **Rationale:** Niche VA benefits-verification form, absent from loan 03.
- **Family:** va_26_8937
- **SME:** [ ] agree [ ] correct: ______

### G434 — O-FHA-00612 [O-FHA]
- **Q:** Were all underwriting requirements met?
- **Defect condition:** Approve/Accept - FHA TOTAL feedback cert was not included in the documentation in the FHA binder
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5338, 5339
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G435 — O-FHA-00614 [O-FHA]
- **Q:** Were all underwriting requirements met?
- **Defect condition:** Refer - DU underwriter did not underwrite the loan and sign the underwriter's certificate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5257
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G436 — O-FHA-50670 [O-FHA]
- **Q:** Were all underwriting requirements met?
- **Defect condition:** Reserves, income and/or PITIA amounts changed and exceeded tolerance levels without resubmission
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5268
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G439 — O-FHA-50663 [O-FHA]
- **Q:** Where the appraisal reflects required repairs, were all maximum mortgage amount requirements met?
- **Defect condition:** Repair costs were added to the sales price before calculating the mortgage without meeting all req's
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5264
- **Severity:** Critical
- **Data needed:** loan_amount + adjusted-value fields (appraised_value is extracted; the loan amount itself and FHA's 'adjusted value' concept are not)
- **Rationale:** Same loan_amount-field gap as ltv_cltv_hcltv family.
- **Family:** max_loan_amount_mri
- **SME:** [ ] agree [ ] correct: ______

### G440 — O-FRD-55520 [O-FRD]
- **Q:** Where the borrower has secondary financing or other financing arrangements, were all requirements met?
- **Defect condition:** Non-profit entity funding the Affordable Second Section 501(c) determination not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5190
- **Severity:** Critical
- **Data needed:** Affordable Second program documentation / IRS Section 501(c) determination letter -- not in corpus
- **Rationale:** Freddie Mac secondary-financing program family, absent from the corpus (same 501(c) document family flagged for asset-verification's G440, decision 017).
- **Family:** affordable_second_501c
- **SME:** [ ] agree [ ] correct: ______

### G442 — O-FRD-50371 [O-FRD]
- **Q:** Where the borrower has secondary financing or other financing arrangements, were all requirements met?
- **Defect condition:** The Affordable Second was provided by an unallowable agency
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5195
- **Severity:** Critical
- **Data needed:** Affordable Second program documentation / IRS Section 501(c) determination letter -- not in corpus
- **Rationale:** Freddie Mac secondary-financing program family, absent from the corpus (same 501(c) document family flagged for asset-verification's G440, decision 017).
- **Family:** affordable_second_501c
- **SME:** [ ] agree [ ] correct: ______

### G443 — O-FRD-55320 [O-FRD]
- **Q:** Where the borrower has secondary financing or other financing arrangements, were all requirements met?
- **Defect condition:** The source of the Affordable Second is the property seller or another interested party
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4962
- **Severity:** Critical
- **Data needed:** Affordable Second program documentation / IRS Section 501(c) determination letter -- not in corpus
- **Rationale:** Freddie Mac secondary-financing program family, absent from the corpus (same 501(c) document family flagged for asset-verification's G440, decision 017).
- **Family:** affordable_second_501c
- **SME:** [ ] agree [ ] correct: ______

### G444 — O-FRD-50363 [O-FRD]
- **Q:** Where the borrower has secondary financing or other financing arrangements, were all requirements met?
- **Defect condition:** The subject does not appear to be held in first lien position as required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5133
- **Severity:** Critical
- **Data needed:** secondary/subordinate-financing note + terms documentation -- not in corpus
- **Rationale:** Same secondary-financing family flagged in asset-verification (decision 017, G007/G267-271).
- **Family:** secondary_financing_terms
- **SME:** [ ] agree [ ] correct: ______

### G445 — O-FRD-52260 [O-FRD]
- **Q:** Where the borrower has secondary financing or other financing arrangements, were all requirements met?
- **Defect condition:** The subject has a seller funded affordable second without all eligibility requirements being met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5284
- **Severity:** Critical
- **Data needed:** Affordable Second program documentation / IRS Section 501(c) determination letter -- not in corpus
- **Rationale:** Freddie Mac secondary-financing program family, absent from the corpus (same 501(c) document family flagged for asset-verification's G440, decision 017).
- **Family:** affordable_second_501c
- **SME:** [ ] agree [ ] correct: ______

### G446 — O-FRD-50370 [O-FRD]
- **Q:** Where the borrower has secondary financing or other financing arrangements, were all requirements met?
- **Defect condition:** The terms of the secondary financing were not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5309
- **Severity:** Critical
- **Data needed:** secondary/subordinate-financing note + terms documentation -- not in corpus
- **Rationale:** Same secondary-financing family flagged in asset-verification (decision 017, G007/G267-271).
- **Family:** secondary_financing_terms
- **SME:** [ ] agree [ ] correct: ______

### G447 — O-FRD-51015 [O-FRD]
- **Q:** Where the loan is secured by a property located in an eligible disaster area, were all documentation flexibilities met?
- **Defect condition:** Disaster documentation age flexibilities used exceeding 6 mos from FEMA disaster declaration date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5026
- **Severity:** Critical
- **Data needed:** FEMA disaster-declaration date + ACE/ACE+PDR waiver documentation -- not in corpus
- **Rationale:** Disaster-area documentation-flexibility family, absent from the corpus.
- **Family:** disaster_flex
- **SME:** [ ] agree [ ] correct: ______

### G449 — O-FRD-58098 [O-FRD]
- **Q:** Where the loan is secured by a property located in an eligible disaster area, were all documentation flexibilities met?
- **Defect condition:** Subject w/ ACE waiver or ACE+PDR & disaster impact did not document damage was not safety/structural
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5025
- **Severity:** Critical
- **Data needed:** FEMA disaster-declaration date + ACE/ACE+PDR waiver documentation -- not in corpus
- **Rationale:** Disaster-area documentation-flexibility family, absent from the corpus.
- **Family:** disaster_flex
- **SME:** [ ] agree [ ] correct: ______

### G450 — O-FRD-51124 [O-FRD]
- **Q:** Where the mortgage is secured by a investment property, were all eligibility requirements met?
- **Defect condition:** Borr has an interest or employment w/ the builder, developer or seller in new construction purchase
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4984
- **Severity:** Critical
- **Data needed:** an identity-of-interest relationship fact (borrower's relationship to builder/developer/seller) -- not modeled
- **Rationale:** Niche identity-of-interest family, absent from the corpus.
- **Family:** identity_of_interest_construction
- **SME:** [ ] agree [ ] correct: ______

### G451 — O-FRD-50366 [O-FRD]
- **Q:** Where the mortgage is secured by a investment property, were all eligibility requirements met?
- **Defect condition:** Exceeded max number of 10 financed properties or was over 6 without min score of 720 or LPA Accept
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5204
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G453 — O-FRD-53800 [O-FRD]
- **Q:** Where the mortgage is secured by a investment property, were all eligibility requirements met?
- **Defect condition:** The subject investment property ARM was ineligible as it was not a 7/6-month or 10/6-month ARM
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5117
- **Severity:** Critical
- **Data needed:** mismo_amortization_type value-format comparison (the field IS already extracted from MISMO XML; the specific '7/6 vs 10/6' ARM-type parsing/comparison logic does not exist yet)
- **Rationale:** Bucket-B-style: closest thing to a ready candidate in this batch -- the field already exists (mismo_amortization_type), but no logic compares its value against the specific ARM-reset-period strings this row needs; NOT classified GREEN because that comparison logic has never been verified against a real loan (none of the 5 is an investment-property ARM) -- exactly the untested-confidence trap decision 018 warned about.
- **Family:** investment_arm_type
- **SME:** [ ] agree [ ] correct: ______

### G454 — O-FRD-58223 [O-FRD]
- **Q:** Where the mortgage is secured by a investment property, were all eligibility requirements met?
- **Defect condition:** The subject is an investment property that was not underwritten with Loan Product Advisor
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5118
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

### G455 — O-FRD-00569 [O-FRD]
- **Q:** Where the mortgage is secured by a primary residence, were all eligibility requirements met?
- **Defect condition:** Evidence at least 1 borrower intends to occupy the subject as their primary home was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5237
- **Severity:** Critical
- **Data needed:** an occupancy-intent certification / military-orders / lease-review fact -- not currently modeled (no occupancy-related field or fact exists in FIELD_SPECS/FACT_SPECS)
- **Rationale:** Occupancy-eligibility family; several distinct sub-conditions (military unable-to-occupy, group-home leased-to-business, second-home suitability) each need their own new fact, none of which exist today.
- **Family:** occupancy_certification
- **SME:** [ ] agree [ ] correct: ______

### G456 — O-FRD-55731 [O-FRD]
- **Q:** Where the mortgage is secured by a primary residence, were all eligibility requirements met?
- **Defect condition:** Military borrower unable to occupy prior to delivery & military orders not in the file to verify
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5173
- **Severity:** Critical
- **Data needed:** DD Form 214 / military orders documentation -- not in corpus
- **Rationale:** Military-service-verification family, absent from the corpus.
- **Family:** dd214_military
- **SME:** [ ] agree [ ] correct: ______

### G458 — O-FRD-50365 [O-FRD]
- **Q:** Where the mortgage is secured by a second home, were all eligibility requirements met?
- **Defect condition:** 2nd home unfit for full time occ &/or unavailable for borr's exclusive use
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4950
- **Severity:** Critical
- **Data needed:** an occupancy-intent certification / military-orders / lease-review fact -- not currently modeled (no occupancy-related field or fact exists in FIELD_SPECS/FACT_SPECS)
- **Rationale:** Occupancy-eligibility family; several distinct sub-conditions (military unable-to-occupy, group-home leased-to-business, second-home suitability) each need their own new fact, none of which exist today.
- **Family:** occupancy_certification
- **SME:** [ ] agree [ ] correct: ______

### G461 — O-FRD-58203 [O-FRD]
- **Q:** Where the mortgage is secured by a second home, were all eligibility requirements met?
- **Defect condition:** The subject is a second home that was not underwritten with Loan Product Advisor
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5279
- **Severity:** Critical
- **Data needed:** DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- **Rationale:** Same AUS-submission gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere in the 5-loan corpus.
- **Family:** aus_findings
- **SME:** [ ] agree [ ] correct: ______

## RED

### G015 — Overlay [GENERIC]
- **Q:** Have all program guidelines/overlays been met?
- **Defect condition:** No, all program guidelines/overlays have not been met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5221, 5222
- **Severity:** Critical
- **Stays human:** open-ended 'guidelines/overlays not met' catch-all
- **Rationale:** Bare catch-all restating the umbrella question in the negative with zero named specifics -- same pattern as application-verification's 'all disclosures per guidelines' RED.
- **Family:** override
- **Guide candidate:** B3-3.4-14 — Section 8 Housing Choice Voucher Homeownership Program Payments (PDF p.370)
- **Guide candidate:** C3-1-01 — General Information About Fannie Mae’s MBS Program (PDF p.993)
- **SME:** [ ] agree [ ] correct: ______

### G017 — RedFlags [GENERIC]
- **Q:** Have all program guidelines/overlays been met?
- **Defect condition:** Red flags appearing on the data verify report were not properly addressed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5017, 5018
- **Severity:** Critical
- **Stays human:** open-ended 'red flags not addressed' sweep
- **Rationale:** Open-ended file-wide red-flag-resolution sweep -- same class as application-verification's file-wide discrepancy RED.
- **Family:** redflag_sweep
- **Guide candidate:** B3-2-09 — Erroneous Credit Report Data (PDF p.311)
- **Guide candidate:** B3-2-10 — Accuracy of DU Data, DU Tolerances, and Errors in the Credit Report (PDF p.313)
- **Guide candidate:** A3-4-02 — Data Quality and Integrity (PDF p.141)
- **SME:** [ ] agree [ ] correct: ______

### G025 — O-FHA-00635 [O-FHA]
- **Q:** In a purchase transaction, were all requirements met?
- **Defect condition:** Loan was disapproved & a officer of the company or Sr staff did not agree with the disapproval
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5058
- **Severity:** Critical
- **Stays human:** process/methodology adequacy judgment
- **Rationale:** Whether a lender's internal review methodology was properly documented and followed is a process judgment, not a file fact.
- **Family:** methodology_review
- **SME:** [ ] agree [ ] correct: ______

### G031 — Appr Red Flags [GENERIC]
- **Q:** Is the occupancy type supported (primary, 2nd, investment) by all documentation in the loan file?
- **Defect condition:** Appraisal red flags present and were not addressed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5206, 5207, 5208, 5209, 5210
- **Severity:** Critical
- **Stays human:** open-ended 'red flags not addressed' sweep
- **Rationale:** Open-ended file-wide red-flag-resolution sweep -- same class as application-verification's file-wide discrepancy RED.
- **Family:** redflag_sweep
- **Guide candidate:** B5-7-02 — High LTV Reﬁnance Underwriting, Documentation, and Collateral Requirements for the New Loan (PDF p.824)
- **Guide candidate:** C1-2-02 — Loan Data and Documentation Delivery Requirements (PDF p.948)
- **Guide candidate:** C2-2-02 — Documentation Requirements for Whole Loan Deliveries (PDF p.982)
- **SME:** [ ] agree [ ] correct: ______

### G046 — O-FNM-00720 [O-FNM]
- **Q:** Were all Approve/Ineligible, Refer with Caution, or Out of Scope recommendations requirements met?
- **Defect condition:** Approve/Ineligible decision & additional layers of risk not considered in the approval
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4967
- **Severity:** Critical
- **Stays human:** holistic risk-adequacy / underwriting-conclusion judgment
- **Rationale:** Whether an underwriter's overall risk narrative is 'adequate,' 'well-reasoned,' or 'complete' is a holistic judgment call on the underwriter's own written analysis, not a checkable fact.
- **Family:** risk_assessment_adequacy
- **Guide candidate:** B3-2-06 — Approve/Ineligible Recommendations (PDF p.307)
- **Guide candidate:** B3-2-07 — Refer with Caution Recommendations (PDF p.309)
- **Guide candidate:** B3-2-08 — Out of Scope Recommendations (PDF p.311)
- **SME:** [ ] agree [ ] correct: ______

### G051 — O-ECOA-53164 [GENERIC]
- **Q:** Were all ECOA requirements met (part 1)?
- **Defect condition:** Alimony/child support/maintenance payments were included where not likely to be consistently made
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5045
- **Severity:** Critical
- **Stays human:** income-continuance/durability judgment
- **Rationale:** Whether income 'is likely to be consistently made' or was properly weighed is an underwriter judgment call, not a bright-line fact.
- **Family:** income_durability
- **Guide candidate:** B3-3.4-02 — Alimony, Child Support, Equalization Payments, or Separate Maintenance (PDF p.352)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** B3-3.3-06 — Mortgage Diﬀerential Payments Income (PDF p.343)
- **SME:** [ ] agree [ ] correct: ______

### G054 — O-ECOA-00584 [GENERIC]
- **Q:** Were all ECOA requirements met (part 1)?
- **Defect condition:** Exceptions of creditworthiness that the UW used may constitute a discriminatory practice or effect
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5239
- **Severity:** Critical
- **Stays human:** fair-lending/discriminatory-intent judgment
- **Rationale:** Fair-lending intent/disparate-treatment determination -- no bright-line fact a document extractor can settle; matches application-verification's judgment-word RED precedent.
- **Family:** ecoa_discrim
- **Guide candidate:** B7-2-05 — Title Exceptions and Impediments (PDF p.867)
- **SME:** [ ] agree [ ] correct: ______

### G055 — O-ECOA-53163 [GENERIC]
- **Q:** Were all ECOA requirements met (part 1)?
- **Defect condition:** Part time income/pension/annuity/retirement income was discounted or excluded from consideration
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5047
- **Severity:** Critical
- **Stays human:** income-continuance/durability judgment
- **Rationale:** Whether income 'is likely to be consistently made' or was properly weighed is an underwriter judgment call, not a bright-line fact.
- **Family:** income_durability
- **Guide candidate:** B3-3.4-03 — Annuity, Pension, or Retirement Income (PDF p.354)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.1-01 — General Income Information (PDF p.318)
- **SME:** [ ] agree [ ] correct: ______

### G057 — O-ECOA-00583 [GENERIC]
- **Q:** Were all ECOA requirements met (part 2)?
- **Defect condition:** The UW decision was based on subjective standards that can result in discriminatory effects
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5027
- **Severity:** Critical
- **Stays human:** fair-lending/discriminatory-intent judgment
- **Rationale:** Fair-lending intent/disparate-treatment determination -- no bright-line fact a document extractor can settle; matches application-verification's judgment-word RED precedent.
- **Family:** ecoa_discrim
- **Guide candidate:** A2-4.1-04 — Notarization Standards (PDF p.99)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.2-02 — Standards for Employment-Related Income (PDF p.330)
- **SME:** [ ] agree [ ] correct: ______

### G058 — O-ECOA-00585 [GENERIC]
- **Q:** Were all ECOA requirements met (part 2)?
- **Defect condition:** The UW evaluated married and unmarried applicants by different standards
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5163
- **Severity:** Critical
- **Stays human:** fair-lending/discriminatory-intent judgment
- **Rationale:** Fair-lending intent/disparate-treatment determination -- no bright-line fact a document extractor can settle; matches application-verification's judgment-word RED precedent.
- **Family:** ecoa_discrim
- **Guide candidate:** A2-4.1-04 — Notarization Standards (PDF p.99)
- **Guide candidate:** B3-2-03 — Risk Factors Evaluated by DU (PDF p.299)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **SME:** [ ] agree [ ] correct: ______

### G059 — O-ECOA-00586 [GENERIC]
- **Q:** Were all ECOA requirements met (part 2)?
- **Defect condition:** The UW may have considered race, color, religion, national origin or sex in evaluating an applicant
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5240
- **Severity:** Critical
- **Stays human:** fair-lending/discriminatory-intent judgment
- **Rationale:** Fair-lending intent/disparate-treatment determination -- no bright-line fact a document extractor can settle; matches application-verification's judgment-word RED precedent.
- **Family:** ecoa_discrim
- **SME:** [ ] agree [ ] correct: ______

### G060 — O-ECOA-53162 [GENERIC]
- **Q:** Were all ECOA requirements met (part 2)?
- **Defect condition:** Use of assumptions or aggregate statistics relating to child bearing was part of the evaluation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5046
- **Severity:** Critical
- **Stays human:** fair-lending/discriminatory-intent judgment
- **Rationale:** Same ECOA discriminatory-intent judgment class as G054/G057/G058/G059 (source text uses a non-breaking space, 'child\xa0bearing', which the family regex below normalizes for).
- **Family:** override
- **Guide candidate:** B3-3.4-02 — Alimony, Child Support, Equalization Payments, or Separate Maintenance (PDF p.352)
- **Guide candidate:** B4-1.2-04 — Appraisal Age and Use Requirements (PDF p.559)
- **Guide candidate:** B4-1.4-07 — Mixed-Use Property Appraisal Requirements (PDF p.626)
- **SME:** [ ] agree [ ] correct: ______

### G186 — O-FHA-00549 [O-FHA]
- **Q:** Were all additional underwriting requirements met?
- **Defect condition:** There are unresolved material discrepancies in the credit information without evidence of resolution
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5165
- **Severity:** Critical
- **Stays human:** open-ended cross-file discrepancy/inconsistency sweep
- **Rationale:** Open-ended cross-document discrepancy/inconsistency sweep -- same class as application-verification's file-wide-discrepancies RED; a specific discrepancy would need its own check, this row is the general catch-all.
- **Family:** discrepancy_sweep
- **SME:** [ ] agree [ ] correct: ______

### G223 — O-FNM-00713 [O-FNM]
- **Q:** Were all comprehensive risk assessment requirements met?
- **Defect condition:** UW did not adequately evaluate the layers of risk, significance of risk factors and overall risks
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5001
- **Severity:** Critical
- **Stays human:** holistic risk-adequacy / underwriting-conclusion judgment
- **Rationale:** Whether an underwriter's overall risk narrative is 'adequate,' 'well-reasoned,' or 'complete' is a holistic judgment call on the underwriter's own written analysis, not a checkable fact.
- **Family:** risk_assessment_adequacy
- **Guide candidate:** B3-1-01 — Comprehensive Risk Assessment (PDF p.285)
- **Guide candidate:** B3-2-03 — Risk Factors Evaluated by DU (PDF p.299)
- **Guide candidate:** B3-5.4-03 — Documentation and Assessment of a Nontraditional Credit History (PDF p.509)
- **SME:** [ ] agree [ ] correct: ______

### G229 — O-FNM-00578 [O-FNM]
- **Q:** Were all data quality, integrity, and fraud requirements met?
- **Defect condition:** Inconsistencies in the Income, asset, liability &/or credit documents were not addressed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5009
- **Severity:** Critical
- **Stays human:** open-ended cross-file discrepancy/inconsistency sweep
- **Rationale:** Open-ended cross-document discrepancy/inconsistency sweep -- same class as application-verification's file-wide-discrepancies RED; a specific discrepancy would need its own check, this row is the general catch-all.
- **Family:** discrepancy_sweep
- **Guide candidate:** A3-4-02 — Data Quality and Integrity (PDF p.141)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-2-09 — Erroneous Credit Report Data (PDF p.311)
- **SME:** [ ] agree [ ] correct: ______

### G231 — O-FNM-00016 [O-FNM]
- **Q:** Were all data quality, integrity, and fraud requirements met?
- **Defect condition:** Material discrepancies noted in the credit information without documenting the resolution
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5010
- **Severity:** Critical
- **Stays human:** open-ended cross-file discrepancy/inconsistency sweep
- **Rationale:** Open-ended cross-document discrepancy/inconsistency sweep -- same class as application-verification's file-wide-discrepancies RED; a specific discrepancy would need its own check, this row is the general catch-all.
- **Family:** discrepancy_sweep
- **Guide candidate:** A3-4-02 — Data Quality and Integrity (PDF p.141)
- **Guide candidate:** B3-2-09 — Erroneous Credit Report Data (PDF p.311)
- **Guide candidate:** B3-2-10 — Accuracy of DU Data, DU Tolerances, and Errors in the Credit Report (PDF p.313)
- **SME:** [ ] agree [ ] correct: ______

### G264 — O-FHA-50695 [O-FHA]
- **Q:** Were all final underwriting decision requirements met?
- **Defect condition:** UW did not identify/resolve inconsistencies in information between the 1003 & other file documents
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5011
- **Severity:** Critical
- **Stays human:** open-ended cross-file discrepancy/inconsistency sweep
- **Rationale:** Open-ended cross-document discrepancy/inconsistency sweep -- same class as application-verification's file-wide-discrepancies RED; a specific discrepancy would need its own check, this row is the general catch-all.
- **Family:** discrepancy_sweep
- **SME:** [ ] agree [ ] correct: ______

### G288 — O-VA-58955 [O-VA]
- **Q:** Were all general underwriting requirements met?
- **Defect condition:** Borr arranged to sell/convey property prior to closing indicating misuse of Veteran's entitlement
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5179
- **Severity:** Critical
- **Stays human:** fraud-pattern/investigative judgment
- **Rationale:** Whether documentation 'indicates possible misuse' is an investigative judgment call, not a bright-line fact.
- **Family:** misuse_of_entitlement
- **SME:** [ ] agree [ ] correct: ______

### G303 — O-FRD-00675 [O-FRD]
- **Q:** Were all general underwriting requirements met?
- **Defect condition:** The UW conclusion that the applicant has adequate capacity to make timely payments is not supported
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5015
- **Severity:** Critical
- **Stays human:** holistic risk-adequacy / underwriting-conclusion judgment
- **Rationale:** Whether an underwriter's overall risk narrative is 'adequate,' 'well-reasoned,' or 'complete' is a holistic judgment call on the underwriter's own written analysis, not a checkable fact.
- **Family:** risk_assessment_adequacy
- **SME:** [ ] agree [ ] correct: ______

### G304 — O-FRD-00681 [O-FRD]
- **Q:** Were all general underwriting requirements met?
- **Defect condition:** The UW did not evaluate all risk factors or document offsetting factors to conclude acceptability
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5274
- **Severity:** Critical
- **Stays human:** holistic risk-adequacy / underwriting-conclusion judgment
- **Rationale:** Whether an underwriter's overall risk narrative is 'adequate,' 'well-reasoned,' or 'complete' is a holistic judgment call on the underwriter's own written analysis, not a checkable fact.
- **Family:** risk_assessment_adequacy
- **SME:** [ ] agree [ ] correct: ______

### G347 — O-FHA-50694 [O-FHA]
- **Q:** Were all manually underwritten final underwriting decision requirements met?
- **Defect condition:** All due diligence not used to evaluate circumstances, risk layers to probability of mtg repay
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5034
- **Severity:** Critical
- **Stays human:** holistic risk-adequacy / underwriting-conclusion judgment
- **Rationale:** Whether an underwriter's overall risk narrative is 'adequate,' 'well-reasoned,' or 'complete' is a holistic judgment call on the underwriter's own written analysis, not a checkable fact.
- **Family:** risk_assessment_adequacy
- **SME:** [ ] agree [ ] correct: ______

### G355 — UW-MatDiscrep/Other [GENERIC]
- **Q:** Were all material discrepancies identified and the required documentation or commentary provided to address?
- **Defect condition:** Missing the required documentation or commentary addressing the material discrepancies identified
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5370
- **Severity:** Critical
- **Stays human:** open-ended cross-file discrepancy/inconsistency sweep
- **Rationale:** Open-ended cross-document discrepancy/inconsistency sweep -- same class as application-verification's file-wide-discrepancies RED; a specific discrepancy would need its own check, this row is the general catch-all.
- **Family:** discrepancy_sweep
- **Guide candidate:** B3-2-04 — DU Documentation Requirements (PDF p.305)
- **Guide candidate:** B3-3.1-02 — Tax Return and Transcript Documentation Requirements (PDF p.320)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **SME:** [ ] agree [ ] correct: ______

### G431 — O-VA-50756 [O-VA]
- **Q:** Were all underwriting documentation requirements met?
- **Defect condition:** The underwriting conclusions and lender documentation was not overall complete and accurate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5359
- **Severity:** Critical
- **Stays human:** holistic risk-adequacy / underwriting-conclusion judgment
- **Rationale:** Whether an underwriter's overall risk narrative is 'adequate,' 'well-reasoned,' or 'complete' is a holistic judgment call on the underwriter's own written analysis, not a checkable fact.
- **Family:** risk_assessment_adequacy
- **SME:** [ ] agree [ ] correct: ______

### G460 — O-FRD-50364 [O-FRD]
- **Q:** Where the mortgage is secured by a second home, were all eligibility requirements met?
- **Defect condition:** The location of the subject is unreasonable to function as a 2nd home
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4949
- **Severity:** Critical
- **Stays human:** '(un)reasonable' judgment
- **Rationale:** '(Un)reasonable' dominates the condition -- same judgment class as asset-verification's 'unreasonable' REDs (decision 017).
- **Family:** unreasonable_judgment
- **SME:** [ ] agree [ ] correct: ______

## NOT_A_CHECK

### G007 —  [O-FHA]
- **Q:** Did the CAIVRS and/or LDP/GSA documentation meet all requirements?
- **Defect condition:** Yes, the CAIVRS and/or LDP/GSA documentation meets all requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5395
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G009 —  [GENERIC]
- **Q:** Do the final AUS findings match all other documentation in the file?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5382, 5383
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G012 —  [GENERIC]
- **Q:** Does the sales contract makes reference to a private transfer, reconveyance, recovery, capital recovery or resale fees?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5521
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G016 —  [GENERIC]
- **Q:** Have all program guidelines/overlays been met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5519, 5520
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G022 —  [GENERIC]
- **Q:** Have conditions required by DU been met?
- **Defect condition:** Yes, conditions required by DU have been met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5387
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G026 —  [O-FHA]
- **Q:** In a purchase transaction, were all requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5417, 5418
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G028 —  [GENERIC]
- **Q:** Is the final 1008 Transmittal Summary accurate & complete?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5388, 5389
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G032 —  [GENERIC]
- **Q:** Is the occupancy type supported (primary, 2nd, investment) by all documentation in the loan file?
- **Defect condition:** Yes, all documentation supports occupancy type and no red flags present
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5392
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G033 —  [GENERIC]
- **Q:** Was a counter-offer made (final terms were less favorable based on initial loan application & price/lock history screen)?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5384, 5385
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G038 —  [O-FNM]
- **Q:** Were DU documentation requirements met?
- **Defect condition:** Yes,  DU documentation requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5460
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G042 —  [O-FHA]
- **Q:** Were all AUS specific underwriting requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5429, 5430
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G048 —  [O-FNM]
- **Q:** Were all Approve/Ineligible, Refer with Caution, or Out of Scope recommendations requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5461, 5462
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G056 —  [GENERIC]
- **Q:** Were all ECOA requirements met (part 1)?
- **Defect condition:** Yes, all ECOA requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5393
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G061 —  [GENERIC]
- **Q:** Were all ECOA requirements met (part 2)?
- **Defect condition:** Yes, all ECOA requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5394
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G065 —  [O-FNM]
- **Q:** Were all Fannie Mae AUS requirements met?
- **Defect condition:** Yes, all Fannie Mae AUS requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5434
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G067 —  [O-RHS]
- **Q:** Were all Form RD 3555-21 requirements met?
- **Defect condition:** Yes, all Form RD 3555-21 requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5491
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G072 —  [O-FRD]
- **Q:** Were all Freddie Mac Exclusionary List and FHFA Suspended Counterparty Program requirements met?
- **Defect condition:** Yes, all Freddie Mac Exclusionary List and FHFA Suspended Counterparty Program requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5467
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G080 —  [O-RHS]
- **Q:** Were all Guaranteed Underwriting System (GUS) requirements met?
- **Defect condition:** Yes, all Guaranteed Underwriting System (GUS) requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5492
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G084 —  [O-FHA]
- **Q:** Were all LTV limitations requirements met?_x000D_
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5425, 5426
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G088 —  [O-FRD]
- **Q:** Were all LTV, TLTV and HTLTV Ratio requirements met?
- **Defect condition:** Yes, all LTV, TLTV and HTLTV Ratio requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5474
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G090 —  [O-VA]
- **Q:** Were all Lender’s Loan Quality Certification requirements met?
- **Defect condition:** Yes, all VA Lender’s Loan Quality Certification requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5512
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G100 —  [O-FRD]
- **Q:** Were all Loan Product Advisor® use requirements met?
- **Defect condition:** Yes, all Loan Product Advisor® use requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5480
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G103 —  [O-FHA]
- **Q:** Were all Minimum Decision Credit Score (MDCS) requirements met?
- **Defect condition:** Yes, all Minimum Decision Credit Score (MDCS) requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5405
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G105 —  [O-FHA]
- **Q:** Were all Nonprofit organizations requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5411, 5412
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G107 —  [O-RHS]
- **Q:** Were all PITI ratio calculation requirements met?
- **Defect condition:** Yes, all PITI ratio calculation requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5500
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G108 —  [O-FNM]
- **Q:** Were all Private Transfer Fee Covenants eligibility requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5438, 5439
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G112 —  [O-FHA]
- **Q:** Were all SSN validation requirements met?
- **Defect condition:** Yes, all SSN validation requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5404
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G125 —  [O-FHA/O-VA]
- **Q:** Were all Title Insurance and title requirements met including company ratings?
- **Defect condition:** Yes, all Title Insurance and title requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5432, 5516
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G133 —  [O-RHS]
- **Q:** Were all Title Insurance and title requirements met?
- **Defect condition:** Yes, all Title Insurance and title requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5505
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G141 —  [O-FRD]
- **Q:** Were all Title Insurance requirements met including company ratings?
- **Defect condition:** Yes, all Title Insurance requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5479
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G147 —  [O-FNM]
- **Q:** Were all Title Insurance requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5465, 5466
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G165 —  [O-VA]
- **Q:** Were all VA Form 26-6393 Loan Analysis requirements met?
- **Defect condition:** Yes, all VA Form 26-6393 Loan Analysis requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5506
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G172 —  [O-VA]
- **Q:** Were all Veteran's eligibility requirements met?
- **Defect condition:** Yes, all Veteran's eligibility requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5507
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G183 —  [O-RHS]
- **Q:** Were all additional total debt ratio calculation requirements met?
- **Defect condition:** Yes, all additional total debt ratio calculation requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5502
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G187 —  [O-FHA]
- **Q:** Were all additional underwriting requirements met?
- **Defect condition:** Yes, all additional requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5396
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G190 —  [O-FHA]
- **Q:** Were all application document processing requirements met?
- **Defect condition:** Yes, all application document processing requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5403
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G196 —  [O-RHS]
- **Q:** Were all application package requirements met?
- **Defect condition:** Yes, all application package requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5503
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G199 —  [O-FHA]
- **Q:** Were all borrower authorization  requirements met?
- **Defect condition:** Yes, all borrower authorization requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5402
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G207 —  [O-RHS]
- **Q:** Were all borrower eligibility requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5497, 5498
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G215 —  [O-VA]
- **Q:** Were all borrower eligibility requirements met?
- **Defect condition:** Yes, all borrower eligibility requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5509
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G219 —  [O-FHA]
- **Q:** Were all citizenship and residency status requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5397, 5398
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G220 —  [O-FHA]
- **Q:** Were all co-signer requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5407, 5408
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G222 —  [O-FNM]
- **Q:** Were all comprehensive risk assessment requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5458, 5459
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G226 —  [O-RHS]
- **Q:** Were all credit eligibility requirements met?
- **Defect condition:** Yes, all credit eligibility requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5499
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G235 —  [O-FNM]
- **Q:** Were all data quality, integrity, and fraud requirements met?
- **Defect condition:** Yes, all data quality, integrity, and fraud requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5433
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G247 —  [O-RHS]
- **Q:** Were all eligible loan purpose requirements met?
- **Defect condition:** Yes, all eligible loan purpose requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5494
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G259 —  [O-VA]
- **Q:** Were all fees and charges requirements met?
- **Defect condition:** Yes, all fees and charges requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5515
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G265 —  [O-FHA]
- **Q:** Were all final underwriting decision requirements met?
- **Defect condition:** Yes, all   final underwriting decision requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5428
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G266 —  [O-FHA]
- **Q:** Were all final underwriting decision requirements met?
- **Defect condition:** Yes, all final underwriting decision requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5431
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G268 —  [O-FNM]
- **Q:** Were all general borrower eligibility requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5448, 5449
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G285 —  [O-RHS]
- **Q:** Were all general income underwriting requirements met?
- **Defect condition:** Yes, all general income underwriting requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5490
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G306 —  [O-FRD/O-VA]
- **Q:** Were all general underwriting requirements met?
- **Defect condition:** Yes, all general underwriting requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5481, 5510
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G309 —  [O-FNM]
- **Q:** Were all guarantors, co-signers, or non-occupant borrowers eligibility requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5454, 5455
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G314 —  [O-FNM]
- **Q:** Were all inter vivos revocable trusts requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5456, 5457
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G317 —  [O-FNM]
- **Q:** Were all legal requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5446, 5447
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G322 —  [O-FRD]
- **Q:** Were all lender contribution requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5487, 5488
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G328 —  [O-FHA]
- **Q:** Were all living trust requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5413, 5414
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G333 —  [O-VA]
- **Q:** Were all loan eligibility requirements met?
- **Defect condition:** Yes, all loan eligibility requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5508
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G335 —  [O-FNM]
- **Q:** Were all loan limit requirements  met?
- **Defect condition:** Yes, all loan limit requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5437
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G341 —  [O-RHS]
- **Q:** Were all loan term requirements met?
- **Defect condition:** Yes, all loan term requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5496
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G346 —  [O-FRD/O-RHS]
- **Q:** Were all manual underwriting requirements met?
- **Defect condition:** Yes, all manual underwriting requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5489, 5493
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G353 —  [O-FHA]
- **Q:** Were all manually underwritten final underwriting decision requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5400, 5401
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G356 —  [GENERIC]
- **Q:** Were all material discrepancies identified and the required documentation or commentary provided to address?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5390, 5391
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G358 —  [O-RHS]
- **Q:** Were all maximum loan amount requirements met?
- **Defect condition:** Yes, all maximum loan amount requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5495
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G361 —  [O-FHA]
- **Q:** Were all maximum mortgage amount requirements met?
- **Defect condition:** Yes, all maximum mortgage amount requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5421
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G363 —  [O-FHA]
- **Q:** Were all maximum mortgage amount requirements on a purchase transaction met?
- **Defect condition:** Yes, all maximum mortgage amount requirements on a purchase transaction were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5422
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G365 —  [O-FNM]
- **Q:** Were all modified loan eligibility requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5442, 5443
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G369 —  [O-FNM]
- **Q:** Were all mortgage eligibility requirements  met?
- **Defect condition:** Yes, all mortgage eligibility requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5436
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G372 —  [O-FHA]
- **Q:** Were all mortgage insurance premium requirements met?
- **Defect condition:** Yes, all mortgage insurance premium requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5427
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G373 —  [O-FNM]
- **Q:** Were all multiple financed properties eligibility requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5452, 5453
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G379 —  [O-FNM]
- **Q:** Were all nonstandard payment collection options eligibility requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5444, 5445
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G380 —  [O-FNM]
- **Q:** Were all non–U.S. citizen borrower eligibility requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5450, 5451
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G387 —  [O-FNM]
- **Q:** Were all occupancy type requirements  met?
- **Defect condition:** Yes, all occupancy type requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5435
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G390 —  [O-FHA]
- **Q:** Were all principal residence occupancy requirements met?
- **Defect condition:** Yes, all principal residence occupancy requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5415
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G391 —  [O-VA]
- **Q:** Were all prior approval lending requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5513, 5514
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G398 —  [O-FHA]
- **Q:** Were all property type and/or investment property requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5419, 5420
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G400 —  [O-FHA]
- **Q:** Were all resident alien status requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5409, 5410
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G404 —  [O-FHA]
- **Q:** Were all secondary residence occupancy requirements met?
- **Defect condition:** Yes, all secondary residence occupany requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5416
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G405 —  [O-FNM]
- **Q:** Were all special assessment eligibility requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5440, 5441
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G410 —  [O-FRD]
- **Q:** Were all special borrower eligibility requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5482, 5483
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G426 —  [O-RHS]
- **Q:** Were all total debt ratio calculation requirements met?
- **Defect condition:** Yes, all total debt ratio calculation requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5501
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G433 —  [O-VA]
- **Q:** Were all underwriting documentation requirements met?
- **Defect condition:** Yes, all underwriting documentation requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5511
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G437 —  [O-FHA]
- **Q:** Were all underwriting requirements met?
- **Defect condition:** Yes, all   underwriting requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 5399
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G438 —  [O-FHA]
- **Q:** Where the appraisal reflects required repairs, were all maximum mortgage amount requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5423, 5424
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G441 —  [O-FRD]
- **Q:** Where the borrower has secondary financing or other financing arrangements, were all requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5475, 5476
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G448 —  [O-FRD]
- **Q:** Where the loan is secured by a property located in an eligible disaster area, were all documentation flexibilities met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5477, 5478
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G452 —  [O-FRD]
- **Q:** Where the mortgage is secured by a investment property, were all eligibility requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5472, 5473
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G457 —  [O-FRD]
- **Q:** Where the mortgage is secured by a primary residence, were all eligibility requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5468, 5469
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G459 —  [O-FRD]
- **Q:** Where the mortgage is secured by a second home, were all eligibility requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 5470, 5471
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **Family:** mechanical
- **SME:** [ ] agree [ ] correct: ______

