# SME Review Packet — property-appraisal-review block triage

**714 rules / 696 unique (question, condition) groups.** Every classification
below is a *proposal* pending your review — mark each check agree / correct.
Bins: GREEN = automatable now · YELLOW = automatable after data/guide work ·
RED = stays human · NOT_A_CHECK = pass/N-A answer option, not a defect rule.

**Source workbook:** `PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv` — row numbers below are Excel-style
(header = row 1), so you can open the sheet and jump straight to each rule.

**Note on this block vs the prior two:** dedup collapse is minimal (714 rules -> 696 groups, ~1.03x, matching asset-verification's ~1.02x, not application-verification's ~1.5x). Unlike either prior block, **zero** groups mechanically resolve to an already-`mapped` SHACL shape — all 7 existing property-appraisal shapes are wired to zero AMQ exception codes today (same latent bug already fixed for LargeDepositShape/GiftEvidenceShape in decisions 017/018) — and an explicit, row-by-row search for safe direct wires against all 7 found **none** (see decision 020: 3 of the 7 shapes have no matching AMQ row in this workbook at all; the other 4 have near-miss candidates that each test a materially different condition on close reading — flagged as YELLOW/worth-SME-review in this packet, not proposed as ready-to-build). Given the scale (526 groups needed individual classification), most are classified by a documented, auditable regex-family classifier (see `layer2_triage_property_appraisal.py`'s module docstring and `classify_family()`) rather than hand-typed one at a time — every row's rationale below still cites its own actual condition text, and the highest-value candidates (existing-shape near-misses, external-registry Bucket-C flags, and the appraisal-presence regex-widening gap) are individually hand-verified overrides, not classifier output.

## Headline

| Bin | Groups | Rules | % of defect groups |
|---|---|---|---|
| GREEN | 2 | 2 | 0% |
| YELLOW | 262 | 263 | 46% |
| RED | 310 | 317 | 54% |
| NOT_A_CHECK | 122 | 132 | — |

## Existing-shape near-miss candidates (verified, NOT ready to build)

- **G151** (O-VA, row 4520): NEAR-MISS vs TermiteInspectionShape (CHK-PRP-003) — checked and REJECTED as a blind wire: our termite_inspection_in_file fact is a single boolean derived from one 'Termite ... NOT IN FILE' phrase in the appraisal summary; this VA row names THREE specific form numbers (NPMA-99-A/99-B/33) AND adds a 'not signed' clause our fact cannot distinguish. Wiring it would risk a false negative on the signature half — same class of mistake the assets triage's O-FRD-58101 rejection was.
- **G279** (O-FHA, row 4640): Topically near TermiteInspectionShape (mentions 'termites') but tests a DIFFERENT fact — whether soil-poisoning treatment was shown not to endanger water quality — not termite-inspection-report presence. Not a match; kept as its own YELLOW group.
- **G375** (O-RHS, row 4609): NEAR-MISS vs TermiteInspectionShape (CHK-PRP-003) — closest of the four termite candidates (same real fact: termite/pest inspection report presence), but the existing shape's message hardcodes 'VA loans in NC' while this row is RHS and conditioned on an unmodeled applicability test ('where required'). The shape's SPARQL itself doesn't actually gate on state or program (a pre-existing gap, not introduced by this row) — extending amq_exception_codes here would make the shape fire for RHS loans too without ever checking RHS applicability. Flagged as WORTH SME REVIEW, not classified as ready-to-build — same caution as assets' G108/G127/G131/G296 gift-transfer near-misses.
- **G511** (O-FHA, row 4397): Topically overlaps termite/well/LBP families but the actual condition is 'no commentary given' — a narrative-adequacy judgment on the appraiser's write-up, not a document-presence test. Not a match to any existing shape.
- **G275** (O-FHA, row 4629): Topically near WellSepticShape but stated as a bare, unenumerated catch-all with no single fact named — needs SME decomposition before any automation, same pattern as application-verification's VA-disclosure catch-all.
- **G276** (O-FHA, row 4463): Same bare-catch-all pattern as G275 (well, not septic, variant).
- **G281** (O-FHA, row 4702): NEAR-MISS vs WellSepticShape (CHK-PRP-005) — checked and REJECTED as a blind wire: this row tests WHO conducted the test (a disinterested third party), a source-authority condition our presence-only fact cannot verify — same trap as the assets triage's O-FRD-58101 rejection (acceptability of source vs. mere presence).
- **G282** (O-FHA, row 4701): NEAR-MISS vs WellSepticShape — closest of the well/septic candidates (presence OR staleness), but REJECTED as a blind wire: our well_septic_inspection_in_file fact is presence-only; this row's real, and arguably primary, condition is a 180-day AGE test our fact cannot evaluate. Wiring it would silently pass a stale-but-present test result, a genuine false-negative risk.
- **G283** (O-FHA, row 4681): NEAR-MISS vs WellSepticShape — REJECTED: tests source ACCEPTABILITY (qualified lab or local health authority performed the test), not presence. Same acceptability-vs-presence trap as G281/G283 and the assets triage's O-FRD-58101 rejection.
- **G423** (O-VA, rows 4699, 4700): Distinguishable from WellSepticShape by subject matter alone: WellSepticShape is USDA RD's PRIVATE well & septic check; this VA row is about a COMMUNITY water/sewage system's documented adequacy — a different real-world system, plus an 'adequately maintained' judgment word. Not a match.
- **G485** (O-RHS, row 4696): Presence is the crisp half; 'acceptable' is the same acceptability-judgment trap as G281/G283 — kept YELLOW since documentation presence is still checkable once the doc exists, but flagged, not treated as a WellSepticShape extension.
- **G493** (O-RHS, row 4695): Same staleness-not-presence gap as G282 (RHS site-requirements wording variant).
- **G040** (O-FRD, row 4253): NEAR-MISS vs MprCompletionCertShape (CHK-PRP-002) — REJECTED: our doc_present_fha_form_442 fact is computed ONLY for mortgage_type == 'FHA' (extract_loan.py's EXPECTED_DOCS_BY_PROGRAM is keyed 'FHA'/'VA' only) and this row is Freddie Mac — the fact would never even be populated for an FRD loan, so wiring this exception code to MprCompletionCertShape would never fire, a 'field that would never populate for the loans this rule targets' trap identical to the assets triage's O-RHS-57768 rejection (cash_out_to_borrower_1003 being refi-only terminology). Also a different real-world form USE (appraisal update/revalidation vs. MPR-repair completion), not just a different program.
- **G676** (O-FRD, row 4254): Same program-mismatch rejection as G040.
- **G677** (O-FRD, row 4525): Same program-mismatch rejection as G040.
- **G037** (O-FRD, row 4107): NEAR-MISS vs StaleAppraisalShape (CHK-PRP-004) — REJECTED: '120 days' here gates an AUS PIW (Property Inspection Waiver) OFFER's validity, not the appraisal report's own age. Different real-world clock, different document (LPA findings, not the appraisal), not a match.
- **G039** (O-FRD, row 4610): NEAR-MISS vs StaleAppraisalShape — related family (a REUSED PRIOR appraisal over 120 days), but the row targets appraisal REUSE specifically (our fact only measures this loan's own appraisal's age at closing, not whether it was carried over from a prior transaction) plus a vague catch-all suffix — not a safe direct wire.
- **G041** (O-FRD, row 4133): NEAR-MISS vs StaleAppraisalShape — related (appraisal validity gap) but keyed to DISBURSEMENT date, which can post-date closing for construction/escrow loans; our appraisal_age_days_at_closing derivation is closing-date-based. Not a safe direct wire without a new disbursement_date field.
- **G096** (O-FNM, row 4157): WORTH SME REVIEW, not ready-to-build: a genuine two-part condition — (a) comp not closed within 12 months (needs a new comp-closing-date field) AND (b) no explanation provided, which reuses the SAME comp_explanation_present boolean CompDistanceShape already checks. Flagged, not proposed as a blind wire: comp_explanation_present is a single generic 'is there ANY addenda/explanation text' flag, not specific to WHICH condition it explains (comp distance vs comp age) — reusing it here risks the same over-general-fact trap as the assets triage's gift-transfer-evidence near-misses (G108/G127/G131/G296).
- **G270** (O-RHS, row 4134): WORTH SME REVIEW, closest near-miss in this entire block to an existing shape: RHS's 180-day appraisal-age rule tests the EXACT SAME fact StaleAppraisalShape already computes (appraisal_age_days_at_closing), just a different threshold (180, not 120) and — unlike StaleAppraisalShape — this RHS row states no recertification-of-value exception that would cure it. NOT proposed as a blind extension of StaleAppraisalShape (different threshold + different cure condition would change the shape's actual logic, not just its exception-code list) — flagged as the strongest build candidate in the block for a NEW, RHS-specific check reusing the same already-extracted field.
- **G204** (O-VA, row 4603): amq_compiler.py's DOC_KEYWORDS matched 'NOV' and pointed this at the va_nov doc type, but the ACTUAL missing thing per the full exception_description is evidence of the SAR's market-data research and recommendation to the RLC — the NOV itself already exists in this row's premise. Reclassified from the mechanical GREEN this eval_target would otherwise produce: a real compiler mis-mapping, not a genuine va_nov-presence check — same class of finding as the 'appraisal' generic-target issue this triage's module docstring documents at length.

## GREEN

### G141 — O-VA-50799 [O-VA]
- **Q:** Were all Lender Appraisal Processing Program (LAPP) requirements met?
- **Defect condition:** The LAPP NOV was not in the file and/or all conditions not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4537
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: va_nov
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier against a genuinely distinct, already-modeled document type (not the generic 'appraisal' catch-all — see module docstring) — already works.
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G203 — O-VA-58667 [O-VA]
- **Q:** Were all additional general appraisal requirements met?
- **Defect condition:** Updated NOV not in file after ROV request where VA determined an increase in value was appropriate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4604
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: va_nov
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier against a genuinely distinct, already-modeled document type (not the generic 'appraisal' catch-all — see module docstring) — already works.
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

## YELLOW

### G002 — O-FHA-50904 [O-FHA]
- **Q:** (FHA) Is there an appraisal in the file?
- **Defect condition:** No, the loan file did not contain an appraisal report as required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4149
- **Severity:** Critical
- **Machine checks:** appraisal document presence (doc type already in the extraction contract)
- **Data needed:** amq_compiler.py's NOT_IN_FILE_RE regex needs widening to also match 'did not contain ... as required' phrasing
- **Rationale:** Same real check amq_compiler.py already auto-compiles as doc_presence for other rows in this block (appraisal doc type is already extracted) — this row's exact wording ('did not contain an appraisal report as required') just evades the compiler's NOT_IN_FILE_RE regex. A compiler regex-widening fix, not a data/fixture gap — kept YELLOW rather than blindly called GREEN, since the mechanism that would make it GREEN doesn't actually fire for this row today.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G004 — O-FNM-50902 [O-FNM]
- **Q:** (Fannie Mae) Is there an appraisal in the file?
- **Defect condition:** No, the loan file did not contain an appraisal report as required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4508
- **Severity:** Critical
- **Machine checks:** as G002 (FNM variant)
- **Data needed:** same regex-widening gap as G002
- **Rationale:** Same as G002 (FNM wording).
- **Classified by:** hand_override
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** D2-1-02 — Fannie Mae QC File Request and Submission Requirements (PDF p.1078)
- **Guide candidate:** A2-5-01 — Fannie Mae Trade Name and Trademarks (PDF p.102)
- **SME:** [ ] agree [ ] correct: ______

### G006 — O-FRD-50472 [O-FRD]
- **Q:** (Freddie Mac) Is there an appraisal in the file?
- **Defect condition:** No, the loan file did not contain an appraisal report as required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4150
- **Severity:** Critical
- **Machine checks:** as G002 (FRD variant)
- **Data needed:** same regex-widening gap as G002
- **Rationale:** Same as G002 (FRD wording).
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G008 — O-RHS-50575 [O-RHS]
- **Q:** (RHS) Is there an appraisal in the file?
- **Defect condition:** No, the loan file did not contain an appraisal report as required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4151
- **Severity:** Critical
- **Machine checks:** as G002 (RHS variant)
- **Data needed:** same regex-widening gap as G002
- **Rationale:** Same as G002 (RHS wording).
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G010 — O-VA-50906 [O-VA]
- **Q:** (VA) Is there an appraisal in the file?
- **Defect condition:** No, the loan file did not contain an appraisal report as required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4152
- **Severity:** Critical
- **Machine checks:** as G002 (VA variant)
- **Data needed:** same regex-widening gap as G002
- **Rationale:** Same as G002 (VA wording).
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G022 — O-FNM-50280 [O-FNM]
- **Q:** Did the appraiser address external influences impacting value or marketability, and did the comparables provided have similar external influences as per aerial image(s)?
- **Defect condition:** No comments found for existing adverse site conditions or external factors
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4425
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'Form 1033' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'Form 1033' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'No comments found for existing adverse site conditions or external factors'
- **Classified by:** family_classifier
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **Guide candidate:** B2-1.2-01 — Loan-to-Value (LTV) Ratios (PDF p.179)
- **Guide candidate:** B2-1.2-02 — Combined Loan-to-Value (CLTV) Ratios (PDF p.181)
- **SME:** [ ] agree [ ] correct: ______

### G026 — O-FNM-57786, O-FRD-57792 [O-FNM/O-FRD]
- **Q:** Does the appraisal evidence unacceptable appraisal practices?_x000D_
- **Defect condition:** A disclosure outlining the ROV process not provided at the time the appraisal report was provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4418, 4419
- **Severity:** Critical
- **Machine checks:** presence of a ROV-process disclosure at the time the appraisal was provided
- **Data needed:** ROV-process disclosure doc type (not in corpus)
- **Rationale:** SAME missing-fixture family as application-verification's decision-014 Bucket-A ROV-disclosure groups (O-FNM-59136/O-FRD-59137, that block's application-stage variant) — this is the appraisal-stage ROV-disclosure-presence variant, same underlying document family, still absent from all 5 synthetic loans.
- **Classified by:** hand_override
- **Guide candidate:** B4-1.1-04 — Unacceptable Appraisal Practices (PDF p.541)
- **Guide candidate:** B4-1.2-01 — Appraisal Report Forms and Exhibits (PDF p.547)
- **Guide candidate:** B4-1.3-01 — Review of the Appraisal Report (PDF p.569)
- **SME:** [ ] agree [ ] correct: ______

### G037 — O-FRD-50473 [O-FRD]
- **Q:** Does the appraisal report meet all requirements?
- **Defect condition:** LPA over 120 days, not resubmitted to confirm PIW offer still valid
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4107
- **Severity:** Critical
- **Data needed:** LPA/PIW offer-validity date field (not modeled) — a different real-world expiration than appraisal-effective-date staleness
- **Rationale:** NEAR-MISS vs StaleAppraisalShape (CHK-PRP-004) — REJECTED: '120 days' here gates an AUS PIW (Property Inspection Waiver) OFFER's validity, not the appraisal report's own age. Different real-world clock, different document (LPA findings, not the appraisal), not a match.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G039 — O-FRD-00517 [O-FRD]
- **Q:** Does the appraisal report meet all requirements?
- **Defect condition:** Prior appraisal was re-used dated over 120 days of the Note date &/or all other req's not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4610
- **Severity:** Critical
- **Stays human:** bare 'all other req's not met' catch-all appended to the reuse condition
- **Data needed:** prior-appraisal-reuse date field + explicit reuse flag (not modeled)
- **Rationale:** NEAR-MISS vs StaleAppraisalShape — related family (a REUSED PRIOR appraisal over 120 days), but the row targets appraisal REUSE specifically (our fact only measures this loan's own appraisal's age at closing, not whether it was carried over from a prior transaction) plus a vague catch-all suffix — not a safe direct wire.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G040 — O-FRD-54687 [O-FRD]
- **Q:** Does the appraisal report meet all requirements?
- **Defect condition:** Required appraisal update was not reported on Form 442, Appraisal Update and/or Completion Report
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4253
- **Severity:** Critical
- **Data needed:** Form 442 (Freddie Mac 'Appraisal Update and/or Completion Report') doc type — NOT the FHA MPR-completion-cert fact our extractor models
- **Rationale:** NEAR-MISS vs MprCompletionCertShape (CHK-PRP-002) — REJECTED: our doc_present_fha_form_442 fact is computed ONLY for mortgage_type == 'FHA' (extract_loan.py's EXPECTED_DOCS_BY_PROGRAM is keyed 'FHA'/'VA' only) and this row is Freddie Mac — the fact would never even be populated for an FRD loan, so wiring this exception code to MprCompletionCertShape would never fire, a 'field that would never populate for the loans this rule targets' trap identical to the assets triage's O-RHS-57768 rejection (cash_out_to_borrower_1003 being refi-only terminology). Also a different real-world form USE (appraisal update/revalidation vs. MPR-repair completion), not just a different program.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G041 — O-FRD-00564 [O-FRD]
- **Q:** Does the appraisal report meet all requirements?
- **Defect condition:** The appraisal was no longer valid as of the disbursement date without an updated or new appraisal
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4133
- **Severity:** Critical
- **Data needed:** disbursement-date field (not modeled — our fact measures age at CLOSING, not at disbursement) + 'updated or new appraisal' fact
- **Rationale:** NEAR-MISS vs StaleAppraisalShape — related (appraisal validity gap) but keyed to DISBURSEMENT date, which can post-date closing for construction/escrow loans; our appraisal_age_days_at_closing derivation is closing-date-based. Not a safe direct wire without a new disbursement_date field.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G057 — O-FNM-50295 [O-FRD]
- **Q:** Form F1033-1, Section I, 6. Are the comparable sales selected locationally, physically, and functionally the most similar to the subject property?
- **Defect condition:** Comparable sales do not have similar physical/legal characteristics when compared to subject
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4426
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'Form 1033' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'Form 1033' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Comparable sales do not have similar physical/legal characteristics when compared to subject'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G065 — O-FRD-58099 [O-FRD]
- **Q:** If the subject is in a federally declared disaster area, were all requirements met?
- **Defect condition:** Condo disaster impact assessment did not include damage to common elements, separate from unit
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4388
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('Condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Condo disaster impact assessment did not include damage to common elements, separate from unit'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G072 — Appraisal-Score=<2.5 [GENERIC]
- **Q:** Was the appropriate level of appraisal review completed based on the CU score?
- **Defect condition:** CU score is =<2.5; prop is one unit detach, attach, condo & "data integrity" concerns not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4227, 4228
- **Severity:** Critical
- **Data needed:** live lookup against an external system/database this pilot has no integration with ('CU')
- **Rationale:** Bucket-C-style candidate (decision 016 precedent): references 'CU', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- **Classified by:** family_classifier
- **Guide candidate:** A3-4-02 — Data Quality and Integrity (PDF p.141)
- **Guide candidate:** B4-1.1-06 — Uniform Appraisal Dataset (UAD) and the Uniform Collateral Data Portal (UCDP) (PDF p.545)
- **Guide candidate:** B4-1.3-01 — Review of the Appraisal Report (PDF p.569)
- **SME:** [ ] agree [ ] correct: ______

### G074 — O-FRD-51640 [O-FRD]
- **Q:** Were additional general condo project eligibility requirements met?_x000D_
- **Defect condition:** Condo HOA receives income from leasing commercial parking that exceed 10% of its budgeted income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4296
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Condo HOA receives income from leasing commercial parking that exceed 10% of its budgeted income'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G075 — O-FRD-50504 [O-FRD]
- **Q:** Were additional general condo project eligibility requirements met?_x000D_
- **Defect condition:** Condo is a timeshare, tenancy in common or unit ownership is identified as an investment opportunity
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4467
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Condo is a timeshare, tenancy in common or unit ownership is identified as an investment opportunity'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G077 — O-FRD-54177 [O-FRD]
- **Q:** Were additional general condo project eligibility requirements met?_x000D_
- **Defect condition:** Condo review revealed characteristics that would be considered a condotel or transient housing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4327
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Condo review revealed characteristics that would be considered a condotel or transient housing'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G078 — O-FRD-54178 [O-FRD]
- **Q:** Were additional general condo project eligibility requirements met?_x000D_
- **Defect condition:** Documentation supporting project is not a condotel or similar transient housing not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4326
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Documentation supporting project is not a condotel or similar transient housing not in the file'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G079 — O-FRD-00516 [O-FRD]
- **Q:** Were additional general condo project eligibility requirements met?_x000D_
- **Defect condition:** Missing documentation to determine project is not a condotel
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4325
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Missing documentation to determine project is not a condotel'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G080 — O-FRD-50507 [O-FRD]
- **Q:** Were additional general condo project eligibility requirements met?_x000D_
- **Defect condition:** Project req/LTV limits not met to allow for streamlined project review
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4646
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Project req/LTV limits not met to allow for streamlined project review'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G081 — O-FRD-59351 [O-FRD]
- **Q:** Were additional general condo project eligibility requirements met?_x000D_
- **Defect condition:** Subject of action causing project to not exist/termination/deconversion/legal structure dissolution
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4571
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Subject of action causing project to not exist/termination/deconversion/legal structure dissolution'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G082 — O-FRD-54176 [O-FRD]
- **Q:** Were additional general condo project eligibility requirements met?_x000D_
- **Defect condition:** The condo HOA or mgt company/agent receives revenue or pays expenses for hotel type services
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4329
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The condo HOA or mgt company/agent receives revenue or pays expenses for hotel type services'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G083 — O-FRD-54678 [O-FRD]
- **Q:** Were additional general condo project eligibility requirements met?_x000D_
- **Defect condition:** The condominium HOA TIN was not obtained
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4304
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The condominium HOA TIN was not obtained'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G084 — O-FRD-53790 [O-FRD]
- **Q:** Were additional general condo project eligibility requirements met?_x000D_
- **Defect condition:** The project did not meet single entity ownership limits
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4569
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The project did not meet single entity ownership limits'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G085 — Approval [O-FRD]
- **Q:** Were additional general condo project eligibility requirements met?_x000D_
- **Defect condition:** Unable to locate the project approval certificate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4292
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'project approval certificate' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'project approval certificate' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Unable to locate the project approval certificate'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G090 — O-FNM-54349 [O-FNM]
- **Q:** Were all Collateral Risk Assessment requirements met?_x000D_
- **Defect condition:** CU comps tab messages & data alerts review reveal quality & condition ratings inconsistent to market
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4594
- **Severity:** Critical
- **Data needed:** live lookup against an external system/database this pilot has no integration with ('CU')
- **Rationale:** Bucket-C-style candidate (decision 016 precedent): references 'CU', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- **Classified by:** family_classifier
- **Guide candidate:** D1-3-02 — Lender Post-Closing Quality Control Review of Approval Conditions, Underwriting Decisions, Data, and Documentation (PDF p.1068)
- **Guide candidate:** A3-4-02 — Data Quality and Integrity (PDF p.141)
- **Guide candidate:** B3-1-01 — Comprehensive Risk Assessment (PDF p.285)
- **SME:** [ ] agree [ ] correct: ______

### G091 — O-FNM-54352 [O-FNM]
- **Q:** Were all Collateral Risk Assessment requirements met?_x000D_
- **Defect condition:** Information provided in CU or other sources did not confirm the sales provided were appropriate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4268
- **Severity:** Critical
- **Data needed:** live lookup against an external system/database this pilot has no integration with ('CU')
- **Rationale:** Bucket-C-style candidate (decision 016 precedent): references 'CU', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- **Classified by:** family_classifier
- **Guide candidate:** B3-1-01 — Comprehensive Risk Assessment (PDF p.285)
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **Guide candidate:** A2-2-02 — Delivery Information and Delivery-Option Speciﬁc Representations and Warranties (PDF p.34)
- **SME:** [ ] agree [ ] correct: ______

### G092 — O-FNM-54344 [O-FNM]
- **Q:** Were all Collateral Risk Assessment requirements met?_x000D_
- **Defect condition:** No extra steps taken ensuring property characteristics reported correct regardless of CU risk score
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4112
- **Severity:** Critical
- **Data needed:** live lookup against an external system/database this pilot has no integration with ('CU')
- **Rationale:** Bucket-C-style candidate (decision 016 precedent): references 'CU', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- **Classified by:** family_classifier
- **Guide candidate:** B3-1-01 — Comprehensive Risk Assessment (PDF p.285)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **Guide candidate:** B2-3-01 — General Property Eligibility (PDF p.258)
- **SME:** [ ] agree [ ] correct: ______

### G094 — O-FNM-54119 [O-FNM]
- **Q:** Were all Comparable sales requirements met?
- **Defect condition:** CU 2.6 + without ensuring comps appropriate, physically similar in site, GLA, & proper adjustments
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4180
- **Severity:** Critical
- **Data needed:** live lookup against an external system/database this pilot has no integration with ('CU')
- **Rationale:** Bucket-C-style candidate (decision 016 precedent): references 'CU', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-09 — Adjustments to Comparable Sales (PDF p.601)
- **Guide candidate:** B4-1.3-08 — Comparable Sales (PDF p.597)
- **Guide candidate:** B3-4.3-10 — Anticipated Sales Proceeds (PDF p.453)
- **SME:** [ ] agree [ ] correct: ______

### G096 — O-FNM-00535 [O-FNM]
- **Q:** Were all Comparable sales requirements met?
- **Defect condition:** Comparable sales were not closed within the last 12 months and no explanation provided for their use
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4157
- **Severity:** Critical
- **Machine checks:** comp_explanation_present (ALREADY extracted) for the explanation half
- **Data needed:** comp sale-closing-date field (not currently extracted — comps entity has comp_num/address/distance_miles/sale_price/gla/adjusted_sale_price, no closing date) for the '12 months' half
- **Rationale:** WORTH SME REVIEW, not ready-to-build: a genuine two-part condition — (a) comp not closed within 12 months (needs a new comp-closing-date field) AND (b) no explanation provided, which reuses the SAME comp_explanation_present boolean CompDistanceShape already checks. Flagged, not proposed as a blind wire: comp_explanation_present is a single generic 'is there ANY addenda/explanation text' flag, not specific to WHICH condition it explains (comp distance vs comp age) — reusing it here risks the same over-general-fact trap as the assets triage's gift-transfer-evidence near-misses (G108/G127/G131/G296).
- **Classified by:** hand_override
- **Guide candidate:** B4-1.3-08 — Comparable Sales (PDF p.597)
- **Guide candidate:** B4-1.3-09 — Adjustments to Comparable Sales (PDF p.601)
- **Guide candidate:** B3-4.3-10 — Anticipated Sales Proceeds (PDF p.453)
- **SME:** [ ] agree [ ] correct: ______

### G107 — O-FNM-55515 [O-FNM]
- **Q:** Were all Condominium Project Questionnaire appraisal requirements met?
- **Defect condition:** (Best Practice) Form 1076A not used to ensure project meets temp req's for condo & co-op projects
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4272
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'Project Questionnaire' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'Project Questionnaire' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: "(Best Practice) Form 1076A not used to ensure project meets temp req's for condo & co-op projects"
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-03 — Condo Appraisal Requirements (PDF p.618)
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **SME:** [ ] agree [ ] correct: ______

### G108 — O-FNM-59131 [O-FNM]
- **Q:** Were all Condominium Project Questionnaire appraisal requirements met?
- **Defect condition:** CPM Approved by FNMA in DU lost status due to credit report exp or changes to CPM ID/project/address
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4390
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'Project Questionnaire' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'Project Questionnaire' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'CPM Approved by FNMA in DU lost status due to credit report exp or changes to CPM ID/project/address'
- **Classified by:** family_classifier
- **Guide candidate:** A4-1-03 — Report of Changes in the Seller/Servicer’s Organization (PDF p.162)
- **Guide candidate:** B3-2-09 — Erroneous Credit Report Data (PDF p.311)
- **Guide candidate:** B3-2-10 — Accuracy of DU Data, DU Tolerances, and Errors in the Credit Report (PDF p.313)
- **SME:** [ ] agree [ ] correct: ______

### G109 — O-FNM-59132 [O-FNM]
- **Q:** Were all Condominium Project Questionnaire appraisal requirements met?
- **Defect condition:** CPM has a delivery restriction with a CPM Approved by FNMA msg in DU without evidence of compliance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4359
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'Project Questionnaire' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'Project Questionnaire' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'CPM has a delivery restriction with a CPM Approved by FNMA msg in DU without evidence of compliance'
- **Classified by:** family_classifier
- **Guide candidate:** A2-2-02 — Delivery Information and Delivery-Option Speciﬁc Representations and Warranties (PDF p.34)
- **Guide candidate:** A3-2-01 — Compliance With Laws (PDF p.107)
- **Guide candidate:** B4-1.1-04 — Unacceptable Appraisal Practices (PDF p.541)
- **SME:** [ ] agree [ ] correct: ______

### G110 — O-FNM-59133 [O-FNM]
- **Q:** Were all Condominium Project Questionnaire appraisal requirements met?
- **Defect condition:** CPM project approved status not retained as of note date & CPM Approved by FNMA DU msg not received
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4360
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'Project Questionnaire' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'Project Questionnaire' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'CPM project approved status not retained as of note date & CPM Approved by FNMA DU msg not received'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.1-04 — Unacceptable Appraisal Practices (PDF p.541)
- **Guide candidate:** B4-1.1-06 — Uniform Appraisal Dataset (UAD) and the Uniform Collateral Data Portal (UCDP) (PDF p.545)
- **Guide candidate:** B4-1.2-01 — Appraisal Report Forms and Exhibits (PDF p.547)
- **SME:** [ ] agree [ ] correct: ______

### G111 — O-FNM-50876 [O-FNM]
- **Q:** Were all Condominium Project Questionnaire appraisal requirements met?
- **Defect condition:** Detached condo did not meet property/appraisal standards, insurance, &/or priority lien requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4374
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'Project Questionnaire' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'Project Questionnaire' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Detached condo did not meet property/appraisal standards, insurance, &/or priority lien requirements'
- **Classified by:** family_classifier
- **Guide candidate:** B7-3-03 — Master Property Insurance Requirements for Project Developments (PDF p.879)
- **Guide candidate:** B7-3-04 — Individual Property Insurance Requirements for a Unit in a Project Development (PDF p.885)
- **Guide candidate:** B4-1.4-03 — Condo Appraisal Requirements (PDF p.618)
- **SME:** [ ] agree [ ] correct: ______

### G112 — O-FNM-53853 [O-FNM]
- **Q:** Were all Condominium Project Questionnaire appraisal requirements met?
- **Defect condition:** Missing Condo Project Questionnaire, Form 1076, with deferred maintenance addendum as recommended
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4307
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'Project Questionnaire' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'Project Questionnaire' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Missing Condo Project Questionnaire, Form 1076, with deferred maintenance addendum as recommended'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-03 — Condo Appraisal Requirements (PDF p.618)
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **Guide candidate:** B1-1-02 — Blanket Authorization Form (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G114 — O-FNM-51046 [O-FNM]
- **Q:** Were all Condominium Project Questionnaire appraisal requirements met?
- **Defect condition:** Project review is waived without meeting all property eligibility requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4694
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'Project Questionnaire' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'Project Questionnaire' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Project review is waived without meeting all property eligibility requirements'
- **Classified by:** family_classifier
- **Guide candidate:** B4-2.2-06 — Project Eligibility Review Service (PERS) (PDF p.691)
- **Guide candidate:** B2-3-01 — General Property Eligibility (PDF p.258)
- **Guide candidate:** B2-3-02 — Special Property Eligibility and Underwriting Considerations: Factory-Built Housing (PDF p.261)
- **SME:** [ ] agree [ ] correct: ______

### G115 — O-FNM-59348 [O-FNM]
- **Q:** Were all Condominium Project Questionnaire appraisal requirements met?
- **Defect condition:** Project review waiver exercised where project is terminating or involved in insolvency proceedings
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4662
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'Project Questionnaire' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'Project Questionnaire' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Project review waiver exercised where project is terminating or involved in insolvency proceedings'
- **Classified by:** family_classifier
- **Guide candidate:** B4-2.1-02 — Waiver of Project Review (PDF p.649)
- **Guide candidate:** B4-1.3-01 — Review of the Appraisal Report (PDF p.569)
- **Guide candidate:** B4-2.2-06 — Project Eligibility Review Service (PERS) (PDF p.691)
- **SME:** [ ] agree [ ] correct: ______

### G116 — O-FNM-55420 [O-FNM]
- **Q:** Were all Condominium Project Questionnaire appraisal requirements met?
- **Defect condition:** The status of the subject condo or co-op project is “Unavailable” in Condo Project Manager, CPM
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4320
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'Project Questionnaire' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'Project Questionnaire' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'The status of the subject condo or co-op project is “Unavailable” in Condo Project Manager, CPM'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-02 — Subject and Contract Sections of the Appraisal Report (PDF p.570)
- **Guide candidate:** B4-1.4-03 — Condo Appraisal Requirements (PDF p.618)
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **SME:** [ ] agree [ ] correct: ______

### G120 — O-FHA-50750 [O-FHA]
- **Q:** Were all Gross Living Area (GLA) appraisal requirements met?
- **Defect condition:** The appraiser reports the property has non-residential use that exceeds 49% of the total floor area
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4535
- **Severity:** Major
- **Machine checks:** threshold math once the underlying date/percent field exists
- **Data needed:** a specific date/percentage field ('49%') not currently in FIELD_SPECS/FACT_SPECS for any appraisal-adjacent document
- **Rationale:** Crisp threshold math ('49%') once the field exists — not a judgment call, just an unbuilt field; condition: 'The appraiser reports the property has non-residential use that exceeds 49% of the total floor area'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G151 — O-VA-54301 [O-VA]
- **Q:** Were all Notice of Value (NOV) requirements met?
- **Defect condition:** Applicable termite form, NPMA-99-A, NPMA-99-B or NPMA-33 missing &/or not signed as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4520
- **Severity:** Critical
- **Data needed:** NPMA-99-A/99-B/33 form-specific doc type + a signature fact (neither modeled today)
- **Rationale:** NEAR-MISS vs TermiteInspectionShape (CHK-PRP-003) — checked and REJECTED as a blind wire: our termite_inspection_in_file fact is a single boolean derived from one 'Termite ... NOT IN FILE' phrase in the appraisal summary; this VA row names THREE specific form numbers (NPMA-99-A/99-B/33) AND adds a 'not signed' clause our fact cannot distinguish. Wiring it would risk a false negative on the signature half — same class of mistake the assets triage's O-FRD-58101 rejection was.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G153 — O-VA-50800 [O-VA]
- **Q:** Were all Notice of Value (NOV) requirements met?
- **Defect condition:** Compliance Inspection Report, VA Form 26-1839, including photographs not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4289
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'Compliance Inspection Report' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'Compliance Inspection Report' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Compliance Inspection Report, VA Form 26-1839, including photographs not in file'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G154 — O-VA-50798 [O-VA]
- **Q:** Were all Notice of Value (NOV) requirements met?
- **Defect condition:** Correction in writing signed, dated w/ supporting docs if applicable by appraiser not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4252
- **Severity:** Major
- **Machine checks:** presence of a signed/dated written correction by the appraiser
- **Data needed:** appraisal-correction-letter doc type (not in corpus)
- **Rationale:** Crisp presence check once the correction letter exists as a document; niche, absent from all 5 synthetic loans' single Appraisal Summary PDF.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G164 — O-FNM-50294 [O-FNM]
- **Q:** Were all Sales Comparison Approach section of the appraisal requirements met?_x000D_
- **Defect condition:** Subject's 3 year sales history & comps sales history for last 12 months not reported
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4234
- **Severity:** Critical
- **Machine checks:** threshold math once the underlying date/percent field exists
- **Data needed:** a specific date/percentage field ('12 months') not currently in FIELD_SPECS/FACT_SPECS for any appraisal-adjacent document
- **Rationale:** Crisp threshold math ('12 months') once the field exists — not a judgment call, just an unbuilt field; condition: "Subject's 3 year sales history & comps sales history for last 12 months not reported"
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-07 — Sales Comparison Approach Section of the Appraisal Report (PDF p.595)
- **Guide candidate:** B4-1.3-02 — Subject and Contract Sections of the Appraisal Report (PDF p.570)
- **Guide candidate:** B4-1.3-03 — Neighborhood Section of the Appraisal Report (PDF p.572)
- **SME:** [ ] agree [ ] correct: ______

### G179 — O-RHS-50578 [O-RHS]
- **Q:** Were all additional appraisal report requirements met?
- **Defect condition:** Appraisal transfer letter from original lender not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4249
- **Severity:** Critical
- **Machine checks:** presence of an appraisal-transfer letter from the original lender
- **Data needed:** appraisal-transfer-letter doc type (not in corpus)
- **Rationale:** Crisp presence check once the transfer letter exists as a document.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G184 — O-RHS-50577 [O-RHS]
- **Q:** Were all additional appraisal report requirements met?
- **Defect condition:** The location map, building sketch, subject &/or comp photos not included
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4176
- **Severity:** Critical
- **Machine checks:** presence of the named exhibit (photos/sketch/map/invoice)
- **Data needed:** appraisal exhibit fields (photos, sketch, location map, invoice) — not modeled; the appraisal summary PDF used in this pilot's synthetic loans does not include exhibit pages
- **Rationale:** Crisp presence check once appraisal exhibits are captured as their own fields/attachments — condition: 'The location map, building sketch, subject &/or comp photos not included'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G194 — O-FHA-50684 [O-FHA]
- **Q:** Were all additional appraisal underwriting requirements met?
- **Defect condition:** Conditional Commitment DE Statement of Appraised Value, form HUD-92800.5B, not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4290
- **Severity:** Major
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'HUD-92800.5B' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'HUD-92800.5B' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Conditional Commitment DE Statement of Appraised Value, form HUD-92800.5B, not in the file'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G196 — O-FHA-51857 [O-FHA]
- **Q:** Were all additional condo appraisal requirements met?
- **Defect condition:** A fully completed Form HUD-9992 signed & dated by an eligible submission source is not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4438
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'HUD-9992' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'HUD-9992' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'A fully completed Form HUD-9992 signed & dated by an eligible submission source is not in the file'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G197 — O-FHA-00634 [O-FHA]
- **Q:** Were all additional condo appraisal requirements met?
- **Defect condition:** Condo project percent individual own concentration & units in arrears for assoc fees req's not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4303
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: "Condo project percent individual own concentration & units in arrears for assoc fees req's not met"
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G199 — O-FHA-54045 [O-FHA]
- **Q:** Were all additional condo appraisal requirements met?
- **Defect condition:** Supporting documentation the condo project is not a condotel or other transient housing not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4305
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Supporting documentation the condo project is not a condotel or other transient housing not in file'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G200 — O-VA-51733 [O-VA]
- **Q:** Were all additional general appraisal requirements met?
- **Defect condition:** A cursory or comprehensive review of the appraisal & VeroSCORE not conducted as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4143
- **Severity:** Critical
- **Data needed:** live lookup against an external system/database this pilot has no integration with ('VeroSCORE')
- **Rationale:** Bucket-C-style candidate (decision 016 precedent): references 'VeroSCORE', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G202 — O-VA-51732 [O-VA]
- **Q:** Were all additional general appraisal requirements met?
- **Defect condition:** The AMS had a critical, severe or high alert that was not addressed in WebLGY notes
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4144
- **Severity:** Critical
- **Data needed:** live lookup against an external system/database this pilot has no integration with ('AMS')
- **Rationale:** Bucket-C-style candidate (decision 016 precedent): references 'AMS', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G204 — O-VA-58666 [O-VA]
- **Q:** Were all additional general appraisal requirements met?
- **Defect condition:** Vet req'd ROV after NOV was issued & submitted to RLC without market data research/recommendation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4603
- **Severity:** Critical
- **Data needed:** a distinct 'SAR researched market data and provided a recommendation' evidence fact (not modeled — different from mere va_nov/NOV presence, which already exists)
- **Rationale:** amq_compiler.py's DOC_KEYWORDS matched 'NOV' and pointed this at the va_nov doc type, but the ACTUAL missing thing per the full exception_description is evidence of the SAR's market-data research and recommendation to the RLC — the NOV itself already exists in this row's premise. Reclassified from the mechanical GREEN this eval_target would otherwise produce: a real compiler mis-mapping, not a genuine va_nov-presence check — same class of finding as the 'appraisal' generic-target issue this triage's module docstring documents at length.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G206 — O-FNM-58735 [O-FNM]
- **Q:** Were all additional leasehold estate appraisal requirements met?
- **Defect condition:** All leasehold lease requirements were not met where the HOA or Co-op Corporation is the lessee
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4448
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'All leasehold lease requirements were not met where the HOA or Co-op Corporation is the lessee'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-05 — Leasehold Interests Appraisal Requirements (PDF p.622)
- **Guide candidate:** B2-3-03 — Special Property Eligibility and Underwriting Considerations: Leasehold Estates (PDF p.268)
- **Guide candidate:** B3-3.7-02 — Analyzing Returns for an S Corporation (PDF p.402)
- **SME:** [ ] agree [ ] correct: ______

### G207 — O-FNM-58736 [O-FNM]
- **Q:** Were all additional leasehold estate appraisal requirements met?
- **Defect condition:** All leasehold lease requirements were not met where the borrower is the lessee
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4494
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'All leasehold lease requirements were not met where the borrower is the lessee'
- **Classified by:** family_classifier
- **Guide candidate:** B3-4.3-21 — Borrower's Earned Real Estate Commission (PDF p.464)
- **Guide candidate:** B4-1.4-05 — Leasehold Interests Appraisal Requirements (PDF p.622)
- **Guide candidate:** B2-2-01 — General Borrower Eligibility Requirements (PDF p.241)
- **SME:** [ ] agree [ ] correct: ______

### G209 — O-FNM-58737 [O-FNM]
- **Q:** Were all additional leasehold estate appraisal requirements met?
- **Defect condition:** Lease includes borr option to purchase & req's not met to establish the purchase price of the land
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4277
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: "Lease includes borr option to purchase & req's not met to establish the purchase price of the land"
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-05 — Leasehold Interests Appraisal Requirements (PDF p.622)
- **Guide candidate:** B4-1.4-06 — Community Land Trust Appraisal Requirements (PDF p.623)
- **Guide candidate:** A2-2-02 — Delivery Information and Delivery-Option Speciﬁc Representations and Warranties (PDF p.34)
- **SME:** [ ] agree [ ] correct: ______

### G210 — O-FNM-58734 [O-FNM]
- **Q:** Were all additional leasehold estate appraisal requirements met?
- **Defect condition:** Loan not 1st lien in property improvements & the borrower's rights in leasehold interest in the land
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4420
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: "Loan not 1st lien in property improvements & the borrower's rights in leasehold interest in the land"
- **Classified by:** family_classifier
- **Guide candidate:** B2-3-03 — Special Property Eligibility and Underwriting Considerations: Leasehold Estates (PDF p.268)
- **Guide candidate:** B3-4.3-21 — Borrower's Earned Real Estate Commission (PDF p.464)
- **Guide candidate:** B4-1.3-05 — Improvements Section of the Appraisal Report (PDF p.580)
- **SME:** [ ] agree [ ] correct: ______

### G222 — O-FHA-56219 [O-FHA]
- **Q:** Were all additional specific appraisal requirements met?
- **Defect condition:** Cost, income, &/or sales comparison approaches not used to determine the ADU contributory value
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4121
- **Severity:** Major
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('ADU') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Cost, income, &/or sales comparison approaches not used to determine the ADU contributory value'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G228 — O-FHA-57797 [O-FHA]
- **Q:** Were all additional valuation, reporting, and fair lending appraisal protocol requirements met?_x000D_
- **Defect condition:** Appraiser’s response to the ROV not included in a revised version of the appraisal & logged in FHAC
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4598
- **Severity:** Major
- **Data needed:** live lookup against an external system/database this pilot has no integration with ('FHAC')
- **Rationale:** Bucket-C-style candidate (decision 016 precedent): references 'FHAC', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G229 — O-FHA-57795 [O-FHA]
- **Q:** Were all additional valuation, reporting, and fair lending appraisal protocol requirements met?_x000D_
- **Defect condition:** Disclosure of the ROV process not given to the borr at application & when the appraisal was provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4599
- **Severity:** Major
- **Machine checks:** presence of a ROV-process disclosure given at application and at appraisal delivery
- **Data needed:** ROV-process disclosure doc type (not in corpus)
- **Rationale:** FHA variant of the same ROV-disclosure family as G026 — same missing-fixture gap.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G231 — O-FNM-00542 [O-FNM]
- **Q:** Were all appraisal delivery requirements met?
- **Defect condition:** A copy of the appraisal report was not provided at least 3 days prior to the closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4276
- **Severity:** Critical
- **Machine checks:** threshold math once the underlying date/percent field exists
- **Data needed:** a specific date/percentage field ('3 days') not currently in FIELD_SPECS/FACT_SPECS for any appraisal-adjacent document
- **Rationale:** Crisp threshold math ('3 days') once the field exists — not a judgment call, just an unbuilt field; condition: 'A copy of the appraisal report was not provided at least 3 days prior to the closing'
- **Classified by:** family_classifier
- **Guide candidate:** B3-6-07 — Debts Paid Oﬀ At or Prior to Closing (PDF p.531)
- **Guide candidate:** B4-1.2-01 — Appraisal Report Forms and Exhibits (PDF p.547)
- **Guide candidate:** B4-1.3-01 — Review of the Appraisal Report (PDF p.569)
- **SME:** [ ] agree [ ] correct: ______

### G236 — O-FHA-51086 [O-FHA]
- **Q:** Were all appraisal effective date requirements met?
- **Defect condition:** The Appraisal Logging Results is not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4200
- **Severity:** Critical
- **Machine checks:** presence of the FHA Appraisal Logging Results screen-print
- **Data needed:** FHA Connection Appraisal Logging Results doc type (not in corpus)
- **Rationale:** Crisp presence check once this specific FHAC screen-print exists as a captured document; distinct from the whole appraisal report itself.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G240 — O-FRD-50474 [O-FRD]
- **Q:** Were all appraisal exhibit and addenda requirements met?
- **Defect condition:** Subject photos missing front/rear view, street, kitchen, all baths, living & extra photos as needed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4650
- **Severity:** Major
- **Machine checks:** presence of the named exhibit (photos/sketch/map/invoice)
- **Data needed:** appraisal exhibit fields (photos, sketch, location map, invoice) — not modeled; the appraisal summary PDF used in this pilot's synthetic loans does not include exhibit pages
- **Rationale:** Crisp presence check once appraisal exhibits are captured as their own fields/attachments — condition: 'Subject photos missing front/rear view, street, kitchen, all baths, living & extra photos as needed'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G241 — O-FRD-00508 [O-FRD]
- **Q:** Were all appraisal exhibit and addenda requirements met?
- **Defect condition:** The subject/comp photos, building sketch &/or location map not included in appraisal exhibits
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4175
- **Severity:** Critical
- **Machine checks:** presence of the named exhibit (photos/sketch/map/invoice)
- **Data needed:** appraisal exhibit fields (photos, sketch, location map, invoice) — not modeled; the appraisal summary PDF used in this pilot's synthetic loans does not include exhibit pages
- **Rationale:** Crisp presence check once appraisal exhibits are captured as their own fields/attachments — condition: 'The subject/comp photos, building sketch &/or location map not included in appraisal exhibits'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G247 — O-FHA-00441 [O-FHA]
- **Q:** Were all appraisal ordering requirements met?
- **Defect condition:** The appraisal was not performed by an appraiser on the HUD roster
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4264
- **Severity:** Critical
- **Data needed:** live lookup against an external system/database this pilot has no integration with ('HUD roster')
- **Rationale:** Bucket-C-style candidate (decision 016 precedent): references 'HUD roster', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G253 — O-FNM-55654 [O-FNM]
- **Q:** Were all appraisal report form, age, and use requirements met?
- **Defect condition:** 2-4 rental income property missing Form 1025, Small Residential Income Property Appraisal Report
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4639
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'Form 1025' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'Form 1025' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: '2-4 rental income property missing Form 1025, Small Residential Income Property Appraisal Report'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.2-04 — Appraisal Age and Use Requirements (PDF p.559)
- **Guide candidate:** B4-1.4-07 — Mixed-Use Property Appraisal Requirements (PDF p.626)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G255 — O-FNM-58350 [O-FNM]
- **Q:** Were all appraisal report form, age, and use requirements met?
- **Defect condition:** A hybrid appraisal was used in an ineligible transaction type
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4453
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('hybrid appraisal') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'A hybrid appraisal was used in an ineligible transaction type'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.2-04 — Appraisal Age and Use Requirements (PDF p.559)
- **Guide candidate:** B4-1.2-01 — Appraisal Report Forms and Exhibits (PDF p.547)
- **Guide candidate:** B4-1.3-01 — Review of the Appraisal Report (PDF p.569)
- **SME:** [ ] agree [ ] correct: ______

### G256 — O-FNM-58351 [O-FNM]
- **Q:** Were all appraisal report form, age, and use requirements met?
- **Defect condition:** A hybrid appraisal was used that did not meet all of the required preconditions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4454
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('hybrid appraisal') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'A hybrid appraisal was used that did not meet all of the required preconditions'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.2-04 — Appraisal Age and Use Requirements (PDF p.559)
- **Guide candidate:** B4-1.2-01 — Appraisal Report Forms and Exhibits (PDF p.547)
- **Guide candidate:** B4-1.3-01 — Review of the Appraisal Report (PDF p.569)
- **SME:** [ ] agree [ ] correct: ______

### G257 — O-FNM-00528 [O-FNM]
- **Q:** Were all appraisal report form, age, and use requirements met?
- **Defect condition:** Appraisal is missing the appraiser’s certification, statement of assumptions & limiting conditions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4258
- **Severity:** Critical
- **Machine checks:** presence of the appraiser's certification / statement of assumptions section
- **Data needed:** appraiser-certification exhibit flag (deepen appraisal extraction — not modeled; the doc always exists, but this specific section/exhibit within it isn't checked)
- **Rationale:** Exhibit-level presence check, same family as G263/G421/G531 (already YELLOW) — reclassified from the conservative-default RED, since this is a specific-component-missing fact, not a narrative-adequacy judgment.
- **Classified by:** hand_override
- **Guide candidate:** B4-1.2-04 — Appraisal Age and Use Requirements (PDF p.559)
- **Guide candidate:** B4-1.2-01 — Appraisal Report Forms and Exhibits (PDF p.547)
- **Guide candidate:** B4-1.3-01 — Review of the Appraisal Report (PDF p.569)
- **SME:** [ ] agree [ ] correct: ______

### G258 — O-FNM-00576 [O-FNM]
- **Q:** Were all appraisal report form, age, and use requirements met?
- **Defect condition:** Appraisal is over 4 mos but under 12 mos on the date of closing without reinspection on Form 1004D
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4250
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'Form 1004D' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'Form 1004D' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Appraisal is over 4 mos but under 12 mos on the date of closing without reinspection on Form 1004D'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.2-04 — Appraisal Age and Use Requirements (PDF p.559)
- **Guide candidate:** B4-1.2-01 — Appraisal Report Forms and Exhibits (PDF p.547)
- **Guide candidate:** B4-1.3-01 — Review of the Appraisal Report (PDF p.569)
- **SME:** [ ] agree [ ] correct: ______

### G260 — O-FNM-55729 [O-FNM]
- **Q:** Were all appraisal report form, age, and use requirements met?
- **Defect condition:** Desktop appraisal used in a loan that was not a primary SFR purchase with an LTV of 90% or less
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4370
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('Desktop appraisal') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Desktop appraisal used in a loan that was not a primary SFR purchase with an LTV of 90% or less'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.2-04 — Appraisal Age and Use Requirements (PDF p.559)
- **Guide candidate:** B2-1.2-01 — Loan-to-Value (LTV) Ratios (PDF p.179)
- **Guide candidate:** B4-1.2-01 — Appraisal Report Forms and Exhibits (PDF p.547)
- **SME:** [ ] agree [ ] correct: ______

### G261 — O-FNM-51045 [O-FNM]
- **Q:** Were all appraisal report form, age, and use requirements met?
- **Defect condition:** Form 1007, comparable rent schedule not in file for 1 unit investment property
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4634
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'Form 1007' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'Form 1007' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Form 1007, comparable rent schedule not in file for 1 unit investment property'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.2-04 — Appraisal Age and Use Requirements (PDF p.559)
- **Guide candidate:** B4-1.4-07 — Mixed-Use Property Appraisal Requirements (PDF p.626)
- **Guide candidate:** B3-3.6-03 — Income or Loss Reported on IRS Form 1040, Schedule C (PDF p.393)
- **SME:** [ ] agree [ ] correct: ______

### G263 — O-FNM-50271 [O-FNM]
- **Q:** Were all appraisal report form, age, and use requirements met?
- **Defect condition:** The exterior only appraisal did not include street map &/or subject photos
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4412
- **Severity:** Critical
- **Machine checks:** presence of the named exhibit (photos/sketch/map/invoice)
- **Data needed:** appraisal exhibit fields (photos, sketch, location map, invoice) — not modeled; the appraisal summary PDF used in this pilot's synthetic loans does not include exhibit pages
- **Rationale:** Crisp presence check once appraisal exhibits are captured as their own fields/attachments — condition: 'The exterior only appraisal did not include street map &/or subject photos'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.2-04 — Appraisal Age and Use Requirements (PDF p.559)
- **Guide candidate:** B4-1.3-02 — Subject and Contract Sections of the Appraisal Report (PDF p.570)
- **Guide candidate:** B4-1.2-01 — Appraisal Report Forms and Exhibits (PDF p.547)
- **SME:** [ ] agree [ ] correct: ______

### G267 — O-RHS-52790 [O-RHS]
- **Q:** Were all appraisal report requirements met?
- **Defect condition:** Appraisal subject to completion or repairs is missing an inspection by a qualified professional
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4624
- **Severity:** Critical
- **Machine checks:** presence of a qualified-professional inspection for a repairs-conditioned appraisal
- **Data needed:** post-repair inspection-report doc type (not in corpus)
- **Rationale:** Crisp presence check once the inspection report exists as a document.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G268 — O-RHS-02685 [O-RHS]
- **Q:** Were all appraisal report requirements met?
- **Defect condition:** Appraisal transfer approval letter from the original lender was not provided, where required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4248
- **Severity:** Major
- **Machine checks:** presence of an appraisal-transfer approval letter from the original lender
- **Data needed:** transfer-approval-letter doc type (not in corpus)
- **Rationale:** Same transfer-letter family as G179 (approval variant).
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G270 — O-RHS-02855 [O-RHS]
- **Q:** Were all appraisal report requirements met?
- **Defect condition:** The appraisal was not completed within 180 days of loan closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4134
- **Severity:** Critical
- **Machine checks:** appraisal_age_days_at_closing (ALREADY extracted and used by StaleAppraisalShape)
- **Data needed:** none for the age math itself — only the 180-vs-120-day threshold and the missing recertification-cures-it exception need SME confirmation before wiring
- **Rationale:** WORTH SME REVIEW, closest near-miss in this entire block to an existing shape: RHS's 180-day appraisal-age rule tests the EXACT SAME fact StaleAppraisalShape already computes (appraisal_age_days_at_closing), just a different threshold (180, not 120) and — unlike StaleAppraisalShape — this RHS row states no recertification-of-value exception that would cure it. NOT proposed as a blind extension of StaleAppraisalShape (different threshold + different cure condition would change the shape's actual logic, not just its exception-code list) — flagged as the strongest build candidate in the block for a NEW, RHS-specific check reusing the same already-extracted field.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G277 — O-FHA-51721 [O-FHA]
- **Q:** Were all appraisal underwriting requirements met?
- **Defect condition:** No water purification system with maintenance contract & escrow acct for water deemed unsafe
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4698
- **Severity:** Critical
- **Data needed:** water-purification maintenance-contract + escrow-account doc/field (not modeled)
- **Rationale:** Reclassified from the family classifier's default RED match (incidental word 'deemed'): the actual checkable condition is presence of a maintenance contract and escrow account for a water-purification system, once the antecedent ('water deemed unsafe') holds — a crisp presence check, not a narrative judgment.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G278 — O-FHA-51717 [O-FHA]
- **Q:** Were all appraisal underwriting requirements met?
- **Defect condition:** Public water supply unsafe per appraiser/health auth & evidence it's safe prior to close not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4109
- **Severity:** Critical
- **Data needed:** safety-evidence documentation for a public water supply deemed unsafe (not modeled)
- **Rationale:** Reclassified from the family classifier's default RED match (incidental word 'deemed'): the checkable condition is presence of evidence the water supply was made safe prior to closing — a crisp presence check once the doc type exists.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G279 — O-FHA-51723 [O-FHA]
- **Q:** Were all appraisal underwriting requirements met?
- **Defect condition:** Soil poisoning used to treat termites without documentation it will not endanger water quality
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4640
- **Severity:** Critical
- **Data needed:** post-treatment water-safety documentation (not modeled; distinct from inspection presence)
- **Rationale:** Topically near TermiteInspectionShape (mentions 'termites') but tests a DIFFERENT fact — whether soil-poisoning treatment was shown not to endanger water quality — not termite-inspection-report presence. Not a match; kept as its own YELLOW group.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G281 — O-FHA-51718 [O-FHA]
- **Q:** Were all appraisal underwriting requirements met?
- **Defect condition:** The required well water test was not conducted and handled by a disinterested third-party
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4702
- **Severity:** Critical
- **Data needed:** well-water-test doc type + a 'disinterested third-party' source-authority fact (not modeled)
- **Rationale:** NEAR-MISS vs WellSepticShape (CHK-PRP-005) — checked and REJECTED as a blind wire: this row tests WHO conducted the test (a disinterested third party), a source-authority condition our presence-only fact cannot verify — same trap as the assets triage's O-FRD-58101 rejection (acceptability of source vs. mere presence).
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G282 — O-FHA-51719 [O-FHA]
- **Q:** Were all appraisal underwriting requirements met?
- **Defect condition:** The required well water test was not in the file or was older than 180 days from disbursement date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4701
- **Severity:** Critical
- **Data needed:** well-water-test date field (180-day staleness, not modeled — presence-only fact today)
- **Rationale:** NEAR-MISS vs WellSepticShape — closest of the well/septic candidates (presence OR staleness), but REJECTED as a blind wire: our well_septic_inspection_in_file fact is presence-only; this row's real, and arguably primary, condition is a 180-day AGE test our fact cannot evaluate. Wiring it would silently pass a stale-but-present test result, a genuine false-negative risk.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G283 — O-FHA-51720 [O-FHA]
- **Q:** Were all appraisal underwriting requirements met?
- **Defect condition:** Well water test was not from the local health authority or a lab qualified to conduct water testing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4681
- **Severity:** Critical
- **Data needed:** well-water-test source-authority field (lab/health-authority qualification, not modeled)
- **Rationale:** NEAR-MISS vs WellSepticShape — REJECTED: tests source ACCEPTABILITY (qualified lab or local health authority performed the test), not presence. Same acceptability-vs-presence trap as G281/G283 and the assets triage's O-FRD-58101 rejection.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G289 — O-FNM-50312 [O-FNM]
- **Q:** Were all community land trust appraisal requirements met?_x000D_
- **Defect condition:** Income not converted from ground lease to leased fee value correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4154
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('community land trust') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Income not converted from ground lease to leased fee value correctly'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-06 — Community Land Trust Appraisal Requirements (PDF p.623)
- **Guide candidate:** B3-3.4-16 — Trust Income (PDF p.374)
- **Guide candidate:** B4-1.3-10 — Cost and Income Approach to Value (PDF p.604)
- **SME:** [ ] agree [ ] correct: ______

### G291 — O-FHA-51856 [O-FHA]
- **Q:** Were all condo appraisal requirements met?
- **Defect condition:** A completed, signed, and dated form HUD-9991, Condo Questionnaire,  is not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4437
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'HUD-9991' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'HUD-9991' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'A completed, signed, and dated form HUD-9991, Condo Questionnaire,  is not in the file'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G292 — O-FNM-50304 [O-FNM]
- **Q:** Were all condo appraisal requirements met?
- **Defect condition:** Analysis of the unit, project amenities & HOA purpose not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4161
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Analysis of the unit, project amenities & HOA purpose not provided'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-03 — Condo Appraisal Requirements (PDF p.618)
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **Guide candidate:** B7-3-04 — Individual Property Insurance Requirements for a Unit in a Project Development (PDF p.885)
- **SME:** [ ] agree [ ] correct: ______

### G293 — O-FHA-51772 [O-FHA]
- **Q:** Were all condo appraisal requirements met?
- **Defect condition:** Condo project not on list of FHA Approved Condominium Projects at time of case number assignment
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4416
- **Severity:** Critical
- **Data needed:** live lookup against an external system/database this pilot has no integration with ('FHA Approved Condominium')
- **Rationale:** Bucket-C-style candidate (decision 016 precedent): references 'FHA Approved Condominium', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G295 — O-RHS-50588 [O-RHS]
- **Q:** Were all condo appraisal requirements met?
- **Defect condition:** Monthly PITIA not calculated correctly &/or did not include all housing components
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4551
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Monthly PITIA not calculated correctly &/or did not include all housing components'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G296 — O-RHS-56101 [O-RHS]
- **Q:** Were all condo appraisal requirements met?
- **Defect condition:** No condo documentation supporting project approval or acceptance by HUD, VA, FNMA or FHLMC
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4452
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'No condo documentation supporting project approval or acceptance by HUD, VA, FNMA or FHLMC'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G298 — O-RHS-50591 [O-RHS]
- **Q:** Were all condo appraisal requirements met?
- **Defect condition:** Project approval not done for site condo, waiver/exception not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4635
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Project approval not done for site condo, waiver/exception not in the file'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G299 — O-RHS-50589 [O-RHS]
- **Q:** Were all condo appraisal requirements met?
- **Defect condition:** Security Instrument did not include the required PUD/Condominium rider or the rider was not signed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4590
- **Severity:** Major
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Security Instrument did not include the required PUD/Condominium rider or the rider was not signed'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G300 — O-FHA-51773 [O-FHA]
- **Q:** Were all condo appraisal requirements met?
- **Defect condition:** The FHA Condo ID was not entered in the FHA Connection (FHAC) Case Assignment screen
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4417
- **Severity:** Critical
- **Data needed:** live lookup against an external system/database this pilot has no integration with ('FHA Connection')
- **Rationale:** Bucket-C-style candidate (decision 016 precedent): references 'FHA Connection', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G301 — O-FHA-51824 [O-FHA]
- **Q:** Were all condo appraisal requirements met?
- **Defect condition:** The condo project was not approved under HRAP or DELRAP approval process
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4449
- **Severity:** Critical
- **Data needed:** live lookup against an external system/database this pilot has no integration with ('HRAP')
- **Rationale:** Bucket-C-style candidate (decision 016 precedent): references 'HRAP', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G302 — O-FHA-51825 [O-FHA]
- **Q:** Were all condo appraisal requirements met?
- **Defect condition:** The file did not document that the subject condo unit met the definition for a site condominium
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4636
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The file did not document that the subject condo unit met the definition for a site condominium'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G303 — O-FHA-00033 [O-FHA]
- **Q:** Were all condo appraisal requirements met?
- **Defect condition:** The percentage of owner-occupied units in the subject condominium project did not meet requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4321
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The percentage of owner-occupied units in the subject condominium project did not meet requirements'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G304 — O-RHS-02697 [O-RHS]
- **Q:** Were all condo appraisal requirements met?
- **Defect condition:** The subject condominium is in an ineligible project
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4466
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The subject condominium is in an ineligible project'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G305 — O-RHS-50590 [O-RHS]
- **Q:** Were all condo appraisal requirements met?
- **Defect condition:** The subject property is in an ineligible condominium project type
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4469
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The subject property is in an ineligible condominium project type'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G306 — O-FHA-00032 [O-FHA]
- **Q:** Were all condo appraisal requirements met?
- **Defect condition:** The subject's condominium project was not approved as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4316
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: "The subject's condominium project was not approved as applicable"
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G307 — O-RHS-50592 [O-RHS]
- **Q:** Were all condo appraisal requirements met?
- **Defect condition:** Underwriting review of the condominium project not conducted as required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4564
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Underwriting review of the condominium project not conducted as required'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G308 — O-FNM-55418 [O-FNM]
- **Q:** Were all condo or co-op project deferred maintenance requirements met?
- **Defect condition:** Condo/co-op financial documents not obtained to confirm the association has ability to fund repairs
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4299
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Condo/co-op financial documents not obtained to confirm the association has ability to fund repairs'
- **Classified by:** family_classifier
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **Guide candidate:** A3-3-05 — Custody of Mortgage Documents (PDF p.136)
- **Guide candidate:** A4-1-02 — Submission of Financial Statements and Reports (PDF p.158)
- **SME:** [ ] agree [ ] correct: ______

### G309 — O-FNM-55414 [O-FNM]
- **Q:** Were all condo or co-op project deferred maintenance requirements met?
- **Defect condition:** Condo/co-op project has deferred maintenance or has regulatory directive to repair unsafe conditions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4302
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Condo/co-op project has deferred maintenance or has regulatory directive to repair unsafe conditions'
- **Classified by:** family_classifier
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **Guide candidate:** B3-3.4-02 — Alimony, Child Support, Equalization Payments, or Separate Maintenance (PDF p.352)
- **Guide candidate:** B4-1.4-03 — Condo Appraisal Requirements (PDF p.618)
- **SME:** [ ] agree [ ] correct: ______

### G312 — O-FNM-55415 [O-FNM]
- **Q:** Were all condo or co-op project deferred maintenance requirements met?
- **Defect condition:** Project missing engineer/inspection report, COO, or other evidence of completed repairs/maintenance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4298
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Project missing engineer/inspection report, COO, or other evidence of completed repairs/maintenance'
- **Classified by:** family_classifier
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **Guide candidate:** A3-3-03 — Other Servicing Arrangements (PDF p.131)
- **Guide candidate:** A4-1-03 — Report of Changes in the Seller/Servicer’s Organization (PDF p.162)
- **SME:** [ ] agree [ ] correct: ______

### G314 — O-FNM-55419 [O-FNM]
- **Q:** Were all condo or co-op project deferred maintenance requirements met?
- **Defect condition:** Special assessment is safety/sound/structural or livability & repairs incomplete or adverse impact
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4301
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Special assessment is safety/sound/structural or livability & repairs incomplete or adverse impact'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-09 — Special Assessment or Community Facilities Districts Appraisal Requirements (PDF p.629)
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **Guide candidate:** B2-3-02 — Special Property Eligibility and Underwriting Considerations: Factory-Built Housing (PDF p.261)
- **SME:** [ ] agree [ ] correct: ______

### G315 — O-FNM-55423 [O-FNM]
- **Q:** Were all condo or co-op project deferred maintenance requirements met?
- **Defect condition:** [Best Practice] Last 5 yrs project inspections/certifications not reviewed for deferred maintenance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4273
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: '[Best Practice] Last 5 yrs project inspections/certifications not reviewed for deferred maintenance'
- **Classified by:** family_classifier
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **Guide candidate:** B3-3.4-02 — Alimony, Child Support, Equalization Payments, or Separate Maintenance (PDF p.352)
- **Guide candidate:** B4-1.4-03 — Condo Appraisal Requirements (PDF p.618)
- **SME:** [ ] agree [ ] correct: ______

### G316 — O-FNM-55422 [O-FNM]
- **Q:** Were all condo or co-op project deferred maintenance requirements met?
- **Defect condition:** [Best Practice] The past 6 months of a condo/co-op project’s HOA meeting minutes were not reviewed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4274
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: '[Best Practice] The past 6 months of a condo/co-op project’s HOA meeting minutes were not reviewed'
- **Classified by:** family_classifier
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **Guide candidate:** B3-3.4-02 — Alimony, Child Support, Equalization Payments, or Separate Maintenance (PDF p.352)
- **Guide candidate:** B4-1.4-03 — Condo Appraisal Requirements (PDF p.618)
- **SME:** [ ] agree [ ] correct: ______

### G317 — O-FNM-53863 [O-FNM]
- **Q:** Were all condo or co-op ineligible projects appraisal requirements met?
- **Defect condition:** Condo or co-op project has recreational leases or mandatory memberships that require paying dues
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4565
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Condo or co-op project has recreational leases or mandatory memberships that require paying dues'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-03 — Condo Appraisal Requirements (PDF p.618)
- **Guide candidate:** B4-2.1-03 — Ineligible Projects (PDF p.652)
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **SME:** [ ] agree [ ] correct: ______

### G320 — CoopDoc [O-FNM]
- **Q:** Were all condo or co-op ineligible projects appraisal requirements met?
- **Defect condition:** Sponsor ownership/Coop shares not documented or outside of allotted %.  20%  Portfolio - 40% Agency
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4338
- **Severity:** Major
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Sponsor ownership/Coop shares not documented or outside of allotted %.  20%  Portfolio - 40% Agency'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-03 — Condo Appraisal Requirements (PDF p.618)
- **Guide candidate:** B4-2.1-03 — Ineligible Projects (PDF p.652)
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **SME:** [ ] agree [ ] correct: ______

### G321 — O-FNM-50877 [O-FNM]
- **Q:** Were all condo or co-op ineligible projects appraisal requirements met?
- **Defect condition:** The condo/co-op project is subject of litigation without all eligible minor litigation criteria met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4222
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The condo/co-op project is subject of litigation without all eligible minor litigation criteria met'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-02 — Subject and Contract Sections of the Appraisal Report (PDF p.570)
- **Guide candidate:** B4-1.4-03 — Condo Appraisal Requirements (PDF p.618)
- **Guide candidate:** B4-2.1-03 — Ineligible Projects (PDF p.652)
- **SME:** [ ] agree [ ] correct: ______

### G322 — O-FNM-53789 [O-FNM]
- **Q:** Were all condo or co-op ineligible projects appraisal requirements met?
- **Defect condition:** The project did not meet single entity ownership limits
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4568
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The project did not meet single entity ownership limits'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-03 — Condo Appraisal Requirements (PDF p.618)
- **Guide candidate:** B4-2.1-03 — Ineligible Projects (PDF p.652)
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **SME:** [ ] agree [ ] correct: ______

### G323 — O-FNM-53854 [O-FNM]
- **Q:** Were all condo or co-op ineligible projects appraisal requirements met?
- **Defect condition:** Total nonresidential or commercial space exceeds 35% in a condo or cooperative
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4533
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Total nonresidential or commercial space exceeds 35% in a condo or cooperative'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-03 — Condo Appraisal Requirements (PDF p.618)
- **Guide candidate:** B4-2.1-03 — Ineligible Projects (PDF p.652)
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **SME:** [ ] agree [ ] correct: ______

### G324 — CondoQuestionnaire [O-FNM]
- **Q:** Were all condo or co-op project review requirements met?
- **Defect condition:** A Questionnaire/Approval worksheet is not found in the file and is required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4324
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'condo questionnaire' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'condo questionnaire' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'A Questionnaire/Approval worksheet is not found in the file and is required'
- **Classified by:** family_classifier
- **Guide candidate:** B4-2.1-02 — Waiver of Project Review (PDF p.649)
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **SME:** [ ] agree [ ] correct: ______

### G325 — O-FNM-56482 [O-FNM]
- **Q:** Were all condo or co-op project review requirements met?
- **Defect condition:** CPM was not used to conduct the condo project full review without being exempt or receiving a waiver
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4319
- **Severity:** Critical
- **Data needed:** live lookup against an external system/database this pilot has no integration with ('CPM')
- **Rationale:** Bucket-C-style candidate (decision 016 precedent): references 'CPM', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- **Classified by:** family_classifier
- **Guide candidate:** B4-2.1-02 — Waiver of Project Review (PDF p.649)
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B4-2.2-02 — Full Review Process (PDF p.675)
- **SME:** [ ] agree [ ] correct: ______

### G326 — O-FNM-50315 [O-FNM]
- **Q:** Were all condo or co-op project review requirements met?
- **Defect condition:** Limited or full condo project review not conducted as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4567
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Limited or full condo project review not conducted as applicable'
- **Classified by:** family_classifier
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B4-2.1-02 — Waiver of Project Review (PDF p.649)
- **Guide candidate:** B4-2.2-01 — Limited Review Process (PDF p.673)
- **SME:** [ ] agree [ ] correct: ______

### G327 — O-FNM-56978 [O-FNM]
- **Q:** Were all condo or co-op project review requirements met?
- **Defect condition:** More than 15% of the total units in a project are 60 days or more past due on HOA fees
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4402
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'More than 15% of the total units in a project are 60 days or more past due on HOA fees'
- **Classified by:** family_classifier
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B4-2.1-02 — Waiver of Project Review (PDF p.649)
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **SME:** [ ] agree [ ] correct: ______

### G328 — O-FNM-53788 [O-FNM]
- **Q:** Were all condo or co-op project review requirements met?
- **Defect condition:** No evidence the project  assoc has a minimum annual budgeted replacement reserve allocation of 10%
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4566
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'No evidence the project  assoc has a minimum annual budgeted replacement reserve allocation of 10%'
- **Classified by:** family_classifier
- **Guide candidate:** B3-4.1-01 — Minimum Reserve Requirements (PDF p.418)
- **Guide candidate:** B4-2.1-02 — Waiver of Project Review (PDF p.649)
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **SME:** [ ] agree [ ] correct: ______

### G330 — O-FNM-56979 [O-FNM]
- **Q:** Were all condo or co-op project review requirements met?
- **Defect condition:** Over 15% of total units in a project are 60 days or more past due in pymts of special assessments
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4403
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Over 15% of total units in a project are 60 days or more past due in pymts of special assessments'
- **Classified by:** family_classifier
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B4-2.1-02 — Waiver of Project Review (PDF p.649)
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **SME:** [ ] agree [ ] correct: ______

### G331 — O-FNM-58745 [O-FNM]
- **Q:** Were all condo or co-op project review requirements met?
- **Defect condition:** Project subject to ground lease w/out protected lender financial interest in a condemnation/similar
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4337
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Project subject to ground lease w/out protected lender financial interest in a condemnation/similar'
- **Classified by:** family_classifier
- **Guide candidate:** B4-2.1-02 — Waiver of Project Review (PDF p.649)
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **SME:** [ ] agree [ ] correct: ______

### G332 — CondoAUS [O-FNM]
- **Q:** Were all condo or co-op project review requirements met?
- **Defect condition:** The Condo, CO-OP, or PUD does not meet the AUS project requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4294
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The Condo, CO-OP, or PUD does not meet the AUS project requirements'
- **Classified by:** family_classifier
- **Guide candidate:** B4-2.1-02 — Waiver of Project Review (PDF p.649)
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **SME:** [ ] agree [ ] correct: ______

### G333 — ProRata [O-FNM]
- **Q:** Were all condo or co-op project review requirements met?
- **Defect condition:** The Pro Rata form is missing or is incomplete/inaccurate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4588
- **Severity:** Major
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'Pro Rata form' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'Pro Rata form' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'The Pro Rata form is missing or is incomplete/inaccurate'
- **Classified by:** family_classifier
- **Guide candidate:** B4-2.1-02 — Waiver of Project Review (PDF p.649)
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **SME:** [ ] agree [ ] correct: ______

### G334 — COOPPSA [O-FNM]
- **Q:** Were all condo or co-op project review requirements met?
- **Defect condition:** The co-op sellers affidavit was not located and/or properly executed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4355
- **Severity:** Major
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'sellers affidavit' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'sellers affidavit' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'The co-op sellers affidavit was not located and/or properly executed'
- **Classified by:** family_classifier
- **Guide candidate:** B4-2.1-02 — Waiver of Project Review (PDF p.649)
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **SME:** [ ] agree [ ] correct: ______

### G335 — O-FNM-53024 [O-FNM]
- **Q:** Were all condo or co-op project review requirements met?
- **Defect condition:** The file did not contain a Co-op Corporation’s Recognition Agreement
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4356
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'Recognition Agreement' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'Recognition Agreement' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'The file did not contain a Co-op Corporation’s Recognition Agreement'
- **Classified by:** family_classifier
- **Guide candidate:** B4-2.1-02 — Waiver of Project Review (PDF p.649)
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **SME:** [ ] agree [ ] correct: ______

### G336 — O-FNM-58744 [O-FNM]
- **Q:** Were all condo or co-op project review requirements met?
- **Defect condition:** The file did not include the CPM decision and unexpired CPM Certification
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4358
- **Severity:** Critical
- **Data needed:** live lookup against an external system/database this pilot has no integration with ('CPM')
- **Rationale:** Bucket-C-style candidate (decision 016 precedent): references 'CPM', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- **Classified by:** family_classifier
- **Guide candidate:** B4-2.1-02 — Waiver of Project Review (PDF p.649)
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **SME:** [ ] agree [ ] correct: ______

### G337 — COOPStkCert [O-FNM]
- **Q:** Were all condo or co-op project review requirements met?
- **Defect condition:** The stock cert is not found and/or does not match the # of shares on the loan security agreement
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4357
- **Severity:** Major
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'stock cert' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'stock cert' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'The stock cert is not found and/or does not match the # of shares on the loan security agreement'
- **Classified by:** family_classifier
- **Guide candidate:** B4-2.1-02 — Waiver of Project Review (PDF p.649)
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **SME:** [ ] agree [ ] correct: ______

### G339 — O-FNM-56977 [O-FNM]
- **Q:** Were all condo or co-op project review requirements met?
- **Defect condition:** Unit is not on a separate meter, no evidence this is common & project budget includes utility funds
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4573
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Unit is not on a separate meter, no evidence this is common & project budget includes utility funds'
- **Classified by:** family_classifier
- **Guide candidate:** B4-2.1-02 — Waiver of Project Review (PDF p.649)
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **SME:** [ ] agree [ ] correct: ______

### G340 — O-FRD-54179 [O-FRD]
- **Q:** Were all condominium exempt from review requirements met?_x000D_
- **Defect condition:** Condo exempt from review without being a 2-4, detached, Freddie owned NCO refi, or Refi Possible
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4404
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Condo exempt from review without being a 2-4, detached, Freddie owned NCO refi, or Refi Possible'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G341 — O-FRD-54180 [O-FRD]
- **Q:** Were all condominium exempt from review requirements met?_x000D_
- **Defect condition:** Exempt from review & is a condotel, houseboat, timeshare, manufactured or segmented owner project
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4405
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Exempt from review & is a condotel, houseboat, timeshare, manufactured or segmented owner project'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G343 — O-FRD-51006 [O-FRD]
- **Q:** Were all condominium exempt from review requirements met?_x000D_
- **Defect condition:** The condominium unit did not meet the glossary definition of a detached condominium unit
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4375
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The condominium unit did not meet the glossary definition of a detached condominium unit'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G344 — O-FRD-59116 [O-FRD]
- **Q:** Were all contract, neighborhood, site, and improvement section requirements met?
- **Defect condition:** Appraisal or PDR review required an inspection, an inspection report or repair invoices not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4219
- **Severity:** Critical
- **Machine checks:** presence of an inspection report or repair invoices
- **Data needed:** post-repair inspection/invoice doc type (not in corpus)
- **Rationale:** Crisp presence check once the inspection report or invoices exist as documents.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G359 — O-FRD-55600 [O-FRD]
- **Q:** Were all desktop appraisal requirements met?
- **Defect condition:** A desktop appraisal was used in a loan that had an ineligible property or mortgage type
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4369
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('desktop appraisal') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'A desktop appraisal was used in a loan that had an ineligible property or mortgage type'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G360 — O-FRD-55601 [O-FRD]
- **Q:** Were all desktop appraisal requirements met?
- **Defect condition:** A desktop appraisal was used in a loan with an LTV over 90%
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4371
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('desktop appraisal') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'A desktop appraisal was used in a loan with an LTV over 90%'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G361 — O-FRD-55598 [O-FRD]
- **Q:** Were all desktop appraisal requirements met?
- **Defect condition:** A floor plan and a building sketch not provided as required for the use of desktop Guide Form 70D
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4373
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'Form 70D' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'Form 70D' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'A floor plan and a building sketch not provided as required for the use of desktop Guide Form 70D'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G362 — O-FRD-55597 [O-FRD]
- **Q:** Were all desktop appraisal requirements met?
- **Defect condition:** Desktop appraisal Guide Form 70D was not fully completed and/or was not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4368
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'Form 70D' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'Form 70D' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Desktop appraisal Guide Form 70D was not fully completed and/or was not in the file'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G363 — O-FRD-55602 [O-FRD]
- **Q:** Were all desktop appraisal requirements met?
- **Defect condition:** Desktop not upgraded to an interior/exterior where an adequate appraisal could not be developed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4372
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('desktop appraisal') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Desktop not upgraded to an interior/exterior where an adequate appraisal could not be developed'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G371 — O-RHS-56099 [O-RHS]
- **Q:** Were all existing dwelling requirements met?
- **Defect condition:** Form HUD-92564-CN not provided to the applicant with evidence maintained in the permanent loan file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4439
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'HUD-92564' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'HUD-92564' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Form HUD-92564-CN not provided to the applicant with evidence maintained in the permanent loan file'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G375 — O-RHS-57526 [O-RHS]
- **Q:** Were all existing dwelling requirements met?
- **Defect condition:** Termite/pest inspection not in file where req'd by the lender, appraiser, inspector, or State law
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4609
- **Severity:** Critical
- **Data needed:** termite_inspection_in_file (fact already extracted) — but shape has no RHS/state-law conditionality to gate on, and the AMQ row's own trigger is conditional ('where req'd by the lender, appraiser, inspector, or State law')
- **Rationale:** NEAR-MISS vs TermiteInspectionShape (CHK-PRP-003) — closest of the four termite candidates (same real fact: termite/pest inspection report presence), but the existing shape's message hardcodes 'VA loans in NC' while this row is RHS and conditioned on an unmodeled applicability test ('where required'). The shape's SPARQL itself doesn't actually gate on state or program (a pre-existing gap, not introduced by this row) — extending amq_exception_codes here would make the shape fire for RHS loans too without ever checking RHS applicability. Flagged as WORTH SME REVIEW, not classified as ready-to-build — same caution as assets' G108/G127/G131/G296 gift-transfer near-misses.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G379 — O-VA-50791 [O-VA]
- **Q:** Were all general appraisal requirements met?
- **Defect condition:** Appraisal did not include all exhibits including a location map, floor plan sketch &/or all photos
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4179
- **Severity:** Major
- **Machine checks:** presence of the named exhibit (photos/sketch/map/invoice)
- **Data needed:** appraisal exhibit fields (photos, sketch, location map, invoice) — not modeled; the appraisal summary PDF used in this pilot's synthetic loans does not include exhibit pages
- **Rationale:** Crisp presence check once appraisal exhibits are captured as their own fields/attachments — condition: 'Appraisal did not include all exhibits including a location map, floor plan sketch &/or all photos'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G381 — O-FRD-00506 [O-FRD]
- **Q:** Were all general appraisal requirements met?
- **Defect condition:** Appraisal is missing the appraiser’s certification, statement of assumptions & limiting conditions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4501
- **Severity:** Critical
- **Machine checks:** presence of the appraiser's certification / statement of assumptions section
- **Data needed:** appraiser-certification exhibit flag (deepen appraisal extraction — not modeled)
- **Rationale:** Same exhibit-level family as G257 (Freddie Mac wording variant).
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G385 — O-VA-00473 [O-VA]
- **Q:** Were all general appraisal requirements met?
- **Defect condition:** Appraiser not given Form 26-1805 & all other req'd documents on the same day the assignment was made
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4379
- **Severity:** Major
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'Form 26' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'Form 26' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: "Appraiser not given Form 26-1805 & all other req'd documents on the same day the assignment was made"
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G391 — O-VA-50792 [O-VA]
- **Q:** Were all general appraisal requirements met?
- **Defect condition:** The appraisal did not include a copy of the appraisal invoice
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4198
- **Severity:** Major
- **Machine checks:** presence of the named exhibit (photos/sketch/map/invoice)
- **Data needed:** appraisal exhibit fields (photos, sketch, location map, invoice) — not modeled; the appraisal summary PDF used in this pilot's synthetic loans does not include exhibit pages
- **Rationale:** Crisp presence check once appraisal exhibits are captured as their own fields/attachments — condition: 'The appraisal did not include a copy of the appraisal invoice'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G398 — O-FNM-55643 [O-FNM]
- **Q:** Were all leasehold estate appraisal requirements met?
- **Defect condition:** A default under the leasehold estate will terminate the sublease securing the mortgage
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4492
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'A default under the leasehold estate will terminate the sublease securing the mortgage'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-05 — Leasehold Interests Appraisal Requirements (PDF p.622)
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **Guide candidate:** A3-3-01 — Outsourcing of Mortgage Processing and Third-Party Originations (PDF p.123)
- **SME:** [ ] agree [ ] correct: ______

### G399 — O-FNM-50310 [O-FNM]
- **Q:** Were all leasehold estate appraisal requirements met?
- **Defect condition:** Lease agreement or ground lease terms, restrictions & conditions not provided for leasehold property
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4199
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Lease agreement or ground lease terms, restrictions & conditions not provided for leasehold property'
- **Classified by:** family_classifier
- **Guide candidate:** B2-3-03 — Special Property Eligibility and Underwriting Considerations: Leasehold Estates (PDF p.268)
- **Guide candidate:** B4-1.4-05 — Leasehold Interests Appraisal Requirements (PDF p.622)
- **Guide candidate:** B4-1.4-07 — Mixed-Use Property Appraisal Requirements (PDF p.626)
- **SME:** [ ] agree [ ] correct: ______

### G400 — O-FNM-55644 [O-FNM]
- **Q:** Were all leasehold estate appraisal requirements met?
- **Defect condition:** Leasehold term not at least 5 yrs past maturity date & fee simple title not vested to borr earlier
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4493
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Leasehold term not at least 5 yrs past maturity date & fee simple title not vested to borr earlier'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-05 — Leasehold Interests Appraisal Requirements (PDF p.622)
- **Guide candidate:** B2-3-03 — Special Property Eligibility and Underwriting Considerations: Leasehold Estates (PDF p.268)
- **Guide candidate:** B3-3.4-09 — Long-term Disability Income (PDF p.364)
- **SME:** [ ] agree [ ] correct: ______

### G401 — O-RHS-50601 [O-RHS]
- **Q:** Were all leasehold estate appraisal requirements met?
- **Defect condition:** Mtg subject to leasehold estate, conditions and lease requirements not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4485
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Mtg subject to leasehold estate, conditions and lease requirements not met'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G403 — O-FNM-55647 [O-FNM]
- **Q:** Were all leasehold estate appraisal requirements met?
- **Defect condition:** Req's not met for establishing the purchase price of the land in leasehold with option to purchase
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4490
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: "Req's not met for establishing the purchase price of the land in leasehold with option to purchase"
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-05 — Leasehold Interests Appraisal Requirements (PDF p.622)
- **Guide candidate:** B4-1.4-06 — Community Land Trust Appraisal Requirements (PDF p.623)
- **Guide candidate:** A2-2-02 — Delivery Information and Delivery-Option Speciﬁc Representations and Warranties (PDF p.34)
- **SME:** [ ] agree [ ] correct: ______

### G404 — O-FNM-55642 [O-FNM]
- **Q:** Were all leasehold estate appraisal requirements met?
- **Defect condition:** The leasehold estate & improvements did not constitute real property subject to the mortgage lien
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4488
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The leasehold estate & improvements did not constitute real property subject to the mortgage lien'
- **Classified by:** family_classifier
- **Guide candidate:** B2-3-03 — Special Property Eligibility and Underwriting Considerations: Leasehold Estates (PDF p.268)
- **Guide candidate:** B3-4.3-21 — Borrower's Earned Real Estate Commission (PDF p.464)
- **Guide candidate:** B3-6-03 — Monthly Housing Expense for the Subject Property (PDF p.518)
- **SME:** [ ] agree [ ] correct: ______

### G405 — O-FNM-55641 [O-FNM]
- **Q:** Were all leasehold estate appraisal requirements met?
- **Defect condition:** The leasehold estate & mortgage will be impaired by a merger of title between the lessor and lessee
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4491
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The leasehold estate & mortgage will be impaired by a merger of title between the lessor and lessee'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-05 — Leasehold Interests Appraisal Requirements (PDF p.622)
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **Guide candidate:** A3-3-01 — Outsourcing of Mortgage Processing and Third-Party Originations (PDF p.123)
- **SME:** [ ] agree [ ] correct: ______

### G406 — O-FNM-55646 [O-FNM]
- **Q:** Were all leasehold estate appraisal requirements met?
- **Defect condition:** The leasehold estate lease payments/assessments were unpaid or were in default
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4363
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The leasehold estate lease payments/assessments were unpaid or were in default'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-05 — Leasehold Interests Appraisal Requirements (PDF p.622)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** B2-3-03 — Special Property Eligibility and Underwriting Considerations: Leasehold Estates (PDF p.268)
- **SME:** [ ] agree [ ] correct: ______

### G407 — O-FNM-58730 [O-FNM]
- **Q:** Were all leasehold estate appraisal requirements met?
- **Defect condition:** The property is subject to a leasehold estate and is an ineligible property type
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4486
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The property is subject to a leasehold estate and is an ineligible property type'
- **Classified by:** family_classifier
- **Guide candidate:** B2-3-03 — Special Property Eligibility and Underwriting Considerations: Leasehold Estates (PDF p.268)
- **Guide candidate:** B3-6-03 — Monthly Housing Expense for the Subject Property (PDF p.518)
- **Guide candidate:** B4-1.3-02 — Subject and Contract Sections of the Appraisal Report (PDF p.570)
- **SME:** [ ] agree [ ] correct: ______

### G408 — O-FNM-55645 [O-FNM]
- **Q:** Were all leasehold estate appraisal requirements met?
- **Defect condition:** The provisions of the lease associated with the leasehold estate did not meet requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4487
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The provisions of the lease associated with the leasehold estate did not meet requirements'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-05 — Leasehold Interests Appraisal Requirements (PDF p.622)
- **Guide candidate:** B2-3-03 — Special Property Eligibility and Underwriting Considerations: Leasehold Estates (PDF p.268)
- **Guide candidate:** B3-4.3-21 — Borrower's Earned Real Estate Commission (PDF p.464)
- **SME:** [ ] agree [ ] correct: ______

### G410 — O-FNM-55730 [O-FNM]
- **Q:** Were all lender responsibilities requirements met?
- **Defect condition:** Appraiser indicated on Form 1004D that the property value has declined without a new appraisal
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4366
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'Form 1004D' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'Form 1004D' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Appraiser indicated on Form 1004D that the property value has declined without a new appraisal'
- **Classified by:** family_classifier
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **Guide candidate:** B4-1.1-02 — Lender Responsibilities (PDF p.535)
- **Guide candidate:** B4-1.4-07 — Mixed-Use Property Appraisal Requirements (PDF p.626)
- **SME:** [ ] agree [ ] correct: ______

### G411 — O-FNM-00530 [O-FNM]
- **Q:** Were all lender responsibilities requirements met?
- **Defect condition:** Appraiser not provided sales contract, known property info &/or contract updates if applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4474
- **Severity:** Critical
- **Machine checks:** presence of appraiser-input documentation (sales contract, known property info)
- **Data needed:** appraiser-input-package doc/field (not modeled — this is about what the LENDER gave the appraiser, not what the appraiser reported)
- **Rationale:** Reclassified from the conservative-default RED: this is a presence check on the lender's input package to the appraiser, a crisp (if currently unmodeled) fact, not a narrative-adequacy judgment.
- **Classified by:** hand_override
- **Guide candidate:** A2-3.1-01 — Lender Breach of Contract (PDF p.56)
- **Guide candidate:** B4-1.1-02 — Lender Responsibilities (PDF p.535)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **SME:** [ ] agree [ ] correct: ______

### G417 — O-FHA-50748 [O-FHA]
- **Q:** Were all minimum property appraisal requirements met?
- **Defect condition:** The appraiser reported defective conditions without photos of those conditions being provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4367
- **Severity:** Major
- **Machine checks:** presence of the named exhibit (photos/sketch/map/invoice)
- **Data needed:** appraisal exhibit fields (photos, sketch, location map, invoice) — not modeled; the appraisal summary PDF used in this pilot's synthetic loans does not include exhibit pages
- **Rationale:** Crisp presence check once appraisal exhibits are captured as their own fields/attachments — condition: 'The appraiser reported defective conditions without photos of those conditions being provided'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G421 — O-FHA-55571 [O-FHA]
- **Q:** Were all minimum property appraisal requirements met?
- **Defect condition:** The subject section of the appraisal was missing components and/or contained incorrect information
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4245
- **Severity:** Major
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('parcel') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The subject section of the appraisal was missing components and/or contained incorrect information'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G423 — O-VA-50796 [O-VA]
- **Q:** Were all minimum property requirements met?
- **Defect condition:** Community water/sewage system not documented to be sufficient in size, properly operated/maintained
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4699, 4700
- **Severity:** Major
- **Stays human:** adequacy of community water/sewage system operation & maintenance
- **Data needed:** community (not private) water/sewage system documentation (not modeled)
- **Rationale:** Distinguishable from WellSepticShape by subject matter alone: WellSepticShape is USDA RD's PRIVATE well & septic check; this VA row is about a COMMUNITY water/sewage system's documented adequacy — a different real-world system, plus an 'adequately maintained' judgment word. Not a match.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G426 — O-VA-50794 [O-VA]
- **Q:** Were all minimum property requirements met?
- **Defect condition:** Nonresidential use impairs residential character of the subject or exceeded 25% of total floor area
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4534
- **Severity:** Major
- **Machine checks:** threshold math once the underlying date/percent field exists
- **Data needed:** a specific date/percentage field ('25%') not currently in FIELD_SPECS/FACT_SPECS for any appraisal-adjacent document
- **Rationale:** Crisp threshold math ('25%') once the field exists — not a judgment call, just an unbuilt field; condition: 'Nonresidential use impairs residential character of the subject or exceeded 25% of total floor area'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G431 — O-VA-51852 [O-VA]
- **Q:** Were all minimum property requirements met?
- **Defect condition:** Subject has multiple parcels and appraisal not subject to all of the parcels being on one deed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4519
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('parcel') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Subject has multiple parcels and appraisal not subject to all of the parcels being on one deed'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G452 — O-FRD-55783 [O-FRD]
- **Q:** Were all requirements met for a property with an accessory dwelling unit?
- **Defect condition:** Appraiser did not include a description, general condition & room count for the ADU
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4117
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('ADU') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Appraiser did not include a description, general condition & room count for the ADU'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G453 — O-FRD-55785 [O-FRD]
- **Q:** Were all requirements met for a property with an accessory dwelling unit?
- **Defect condition:** Comparable requirements not met for an ADU that is illegal & does not comply with zoning & land use
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4127
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('ADU') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Comparable requirements not met for an ADU that is illegal & does not comply with zoning & land use'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G455 — O-FRD-55784 [O-FRD]
- **Q:** Were all requirements met for a property with an accessory dwelling unit?
- **Defect condition:** The subject is an ineligible property type to have an ADU
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4129
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('ADU') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The subject is an ineligible property type to have an ADU'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G456 — O-FNM-57980 [O-FNM]
- **Q:** Were all requirements met for a property with an accessory dwelling unit?_x000D_
- **Defect condition:** ADU does not comply with zoning requirements or meet the additional conditions to be eligible
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4126
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('ADU') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'ADU does not comply with zoning requirements or meet the additional conditions to be eligible'
- **Classified by:** family_classifier
- **Guide candidate:** B7-3-02 — Property Insurance Requirements for One-to Four-Unit Properties (PDF p.875)
- **Guide candidate:** B7-3-04 — Individual Property Insurance Requirements for a Unit in a Project Development (PDF p.885)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **SME:** [ ] agree [ ] correct: ______

### G457 — O-FNM-57982 [O-FNM]
- **Q:** Were all requirements met for a property with an accessory dwelling unit?_x000D_
- **Defect condition:** ADU not subordinate in size to the primary dwelling &/or did not have the req'd separate features
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4131
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('ADU') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: "ADU not subordinate in size to the primary dwelling &/or did not have the req'd separate features"
- **Classified by:** family_classifier
- **Guide candidate:** B7-3-02 — Property Insurance Requirements for One-to Four-Unit Properties (PDF p.875)
- **Guide candidate:** B7-3-04 — Individual Property Insurance Requirements for a Unit in a Project Development (PDF p.885)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **SME:** [ ] agree [ ] correct: ______

### G462 — O-FNM-57981 [O-FNM]
- **Q:** Were all requirements met for a property with an accessory dwelling unit?_x000D_
- **Defect condition:** The ADU is a HUD Code manufactured home and the additional requirements applicable were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4125
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('ADU') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The ADU is a HUD Code manufactured home and the additional requirements applicable were not met'
- **Classified by:** family_classifier
- **Guide candidate:** B7-3-02 — Property Insurance Requirements for One-to Four-Unit Properties (PDF p.875)
- **Guide candidate:** B7-3-04 — Individual Property Insurance Requirements for a Unit in a Project Development (PDF p.885)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **SME:** [ ] agree [ ] correct: ______

### G463 — O-FNM-57983 [O-FNM]
- **Q:** Were all requirements met for a property with an accessory dwelling unit?_x000D_
- **Defect condition:** The ADU was included with the Gross Living Area calculation of the primary dwelling
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4123
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('ADU') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The ADU was included with the Gross Living Area calculation of the primary dwelling'
- **Classified by:** family_classifier
- **Guide candidate:** B7-3-02 — Property Insurance Requirements for One-to Four-Unit Properties (PDF p.875)
- **Guide candidate:** B7-3-04 — Individual Property Insurance Requirements for a Unit in a Project Development (PDF p.885)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **SME:** [ ] agree [ ] correct: ______

### G464 — O-FNM-57979 [O-FNM]
- **Q:** Were all requirements met for a property with an accessory dwelling unit?_x000D_
- **Defect condition:** The subject is an ineligible property type to have an ADU
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4128
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('ADU') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The subject is an ineligible property type to have an ADU'
- **Classified by:** family_classifier
- **Guide candidate:** B3-6-03 — Monthly Housing Expense for the Subject Property (PDF p.518)
- **Guide candidate:** B7-3-02 — Property Insurance Requirements for One-to Four-Unit Properties (PDF p.875)
- **Guide candidate:** B7-3-04 — Individual Property Insurance Requirements for a Unit in a Project Development (PDF p.885)
- **SME:** [ ] agree [ ] correct: ______

### G465 — O-VA-55910 [O-VA]
- **Q:** Were all requirements met for the use of an exterior-only or desktop appraisal?
- **Defect condition:** Ext-only/desktop with down pymt less than 20% & case unassigned by VA for less than 7 business days
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4407
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('desktop appraisal') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Ext-only/desktop with down pymt less than 20% & case unassigned by VA for less than 7 business days'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G466 — O-VA-55911 [O-VA]
- **Q:** Were all requirements met for the use of an exterior-only or desktop appraisal?
- **Defect condition:** Exterior-only or desktop appraisal used in a purchase where the lender is not LAPP approved
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4408
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('desktop appraisal') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Exterior-only or desktop appraisal used in a purchase where the lender is not LAPP approved'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G467 — O-VA-55912 [O-VA]
- **Q:** Were all requirements met for the use of an exterior-only or desktop appraisal?
- **Defect condition:** Exterior-only or desktop appraisal used where the purchase price exceeds the conforming loan limit
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4409
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('desktop appraisal') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Exterior-only or desktop appraisal used where the purchase price exceeds the conforming loan limit'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G468 — O-VA-55913 [O-VA]
- **Q:** Were all requirements met for the use of an exterior-only or desktop appraisal?
- **Defect condition:** Exterior-only/desktop use in a condo, leasehold, or a SFR undergoing renovation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4410, 4411
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('desktop appraisal') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Exterior-only/desktop use in a condo, leasehold, or a SFR undergoing renovation'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G471 — O-RHS-50571 [O-RHS]
- **Q:** Were all rural area designation requirements met?_x000D_
- **Defect condition:** Rural designation changed to non-rural without meeting all criteria to be approved and guaranteed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4278
- **Severity:** Major
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('rural area designat') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Rural designation changed to non-rural without meeting all criteria to be approved and guaranteed'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G472 — O-RHS-02679 [O-RHS]
- **Q:** Were all rural area designation requirements met?_x000D_
- **Defect condition:** The subject property is not in an area designated as rural by RHS
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4614
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('rural area designat') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The subject property is not in an area designated as rural by RHS'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G475 — O-FRD-50491 [O-FRD]
- **Q:** Were all sales comparison approach requirements met?_x000D_
- **Defect condition:** Comparable selection requirements not met for new PUD or new or recently converted Condo projects
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4526
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('PUD') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Comparable selection requirements not met for new PUD or new or recently converted Condo projects'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G476 — O-FRD-50490 [O-FRD]
- **Q:** Were all sales comparison approach requirements met?_x000D_
- **Defect condition:** Comps not within subjects established PUD/Condo project when they are the best indicators of value
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4400
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('PUD') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Comps not within subjects established PUD/Condo project when they are the best indicators of value'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G478 — O-FRD-00511 [O-FRD]
- **Q:** Were all sales comparison approach requirements met?_x000D_
- **Defect condition:** Subject prior sales/Xfers in last 3 yrs or last 1 yr for the comps &/or verification source missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4617
- **Severity:** Critical
- **Machine checks:** presence of a prior-sales/transfer-history field + verification source
- **Data needed:** subject/comp 3-year sales-history + verification-source fields (not modeled)
- **Rationale:** Crisp presence/completeness check on a specific data point once the field is added; reclassified from the conservative-default RED.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G485 — O-RHS-02688 [O-RHS]
- **Q:** Were all site requirements met?
- **Defect condition:** No documentation that the site has acceptable water and waste water disposal systems
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4696
- **Severity:** Critical
- **Stays human:** 'acceptable' water/wastewater system judgment
- **Data needed:** site water/wastewater documentation (not modeled)
- **Rationale:** Presence is the crisp half; 'acceptable' is the same acceptability-judgment trap as G281/G283 — kept YELLOW since documentation presence is still checkable once the doc exists, but flagged, not treated as a WellSepticShape extension.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G490 — O-RHS-56098 [O-RHS]
- **Q:** Were all site requirements met?
- **Defect condition:** The subject accessory dwelling unit (ADU) is ineligible due to potentially creating rental income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4465
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('ADU') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The subject accessory dwelling unit (ADU) is ineligible due to potentially creating rental income'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G491 — O-RHS-52815 [O-RHS]
- **Q:** Were all site requirements met?
- **Defect condition:** The subject property has multiple parcels without all requirements being met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4518
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('parcel') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The subject property has multiple parcels without all requirements being met'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G493 — O-RHS-57529 [O-RHS]
- **Q:** Were all site requirements met?
- **Defect condition:** The water analysis report is older than 180 days at the time of the loan closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4695
- **Severity:** Critical
- **Data needed:** water-analysis-report date field (180-day staleness, not modeled)
- **Rationale:** Same staleness-not-presence gap as G282 (RHS site-requirements wording variant).
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G498 — O-FNM-54684 [O-FNM]
- **Q:** Were all special property appraisal requirements met?_x000D_
- **Defect condition:** Each of the multiple parcels not conveyed in entirety with the mortgage being the first lien on each
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4113
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('parcel') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Each of the multiple parcels not conveyed in entirety with the mortgage being the first lien on each'
- **Classified by:** family_classifier
- **Guide candidate:** B2-3-02 — Special Property Eligibility and Underwriting Considerations: Factory-Built Housing (PDF p.261)
- **Guide candidate:** B2-3-03 — Special Property Eligibility and Underwriting Considerations: Leasehold Estates (PDF p.268)
- **Guide candidate:** B2-3-04 — Special Property Eligibility Considerations (PDF p.274)
- **SME:** [ ] agree [ ] correct: ______

### G499 — O-FNM-54686 [O-FNM]
- **Q:** Were all special property appraisal requirements met?_x000D_
- **Defect condition:** No documentation non-adjoining parcels without the residence cannot be improved with a dwelling
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4527
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('parcel') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'No documentation non-adjoining parcels without the residence cannot be improved with a dwelling'
- **Classified by:** family_classifier
- **Guide candidate:** B2-3-02 — Special Property Eligibility and Underwriting Considerations: Factory-Built Housing (PDF p.261)
- **Guide candidate:** B2-3-03 — Special Property Eligibility and Underwriting Considerations: Leasehold Estates (PDF p.268)
- **Guide candidate:** B2-3-04 — Special Property Eligibility Considerations (PDF p.274)
- **SME:** [ ] agree [ ] correct: ______

### G500 — O-FNM-54685 [O-FNM]
- **Q:** Were all special property appraisal requirements met?_x000D_
- **Defect condition:** Non-adjoining parcels are not separated due to a road, waterfront access or similar as allowable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4529
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('parcel') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Non-adjoining parcels are not separated due to a road, waterfront access or similar as allowable'
- **Classified by:** family_classifier
- **Guide candidate:** B2-3-02 — Special Property Eligibility and Underwriting Considerations: Factory-Built Housing (PDF p.261)
- **Guide candidate:** B2-3-03 — Special Property Eligibility and Underwriting Considerations: Leasehold Estates (PDF p.268)
- **Guide candidate:** B2-3-04 — Special Property Eligibility Considerations (PDF p.274)
- **SME:** [ ] agree [ ] correct: ______

### G503 — O-FNM-54683 [O-FNM]
- **Q:** Were all special property appraisal requirements met?_x000D_
- **Defect condition:** The subject's additional parcels were not adjoining and/or did not have the same basic zoning
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4115
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('parcel') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: "The subject's additional parcels were not adjoining and/or did not have the same basic zoning"
- **Classified by:** family_classifier
- **Guide candidate:** B2-3-02 — Special Property Eligibility and Underwriting Considerations: Factory-Built Housing (PDF p.261)
- **Guide candidate:** B2-3-03 — Special Property Eligibility and Underwriting Considerations: Leasehold Estates (PDF p.268)
- **Guide candidate:** B2-3-04 — Special Property Eligibility Considerations (PDF p.274)
- **SME:** [ ] agree [ ] correct: ______

### G507 — O-FHA-56219 [O-FHA]
- **Q:** Were all specific appraisal requirements met?
- **Defect condition:** Cost, income, &/or sales comparison approaches not used to determine the ADU contributory value
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4120
- **Severity:** Major
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('ADU') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Cost, income, &/or sales comparison approaches not used to determine the ADU contributory value'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G516 — O-FRD-50479 [O-FRD]
- **Q:** Were all subject section requirements met?
- **Defect condition:** The appraisal did not report the property rights as fee simple or leasehold
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4587
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The appraisal did not report the property rights as fee simple or leasehold'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G531 — O-FHA-50946 [O-FHA]
- **Q:** Were all valuation, reporting, and fair lending appraisal protocols requirements met?
- **Defect condition:** Building sketch, required photographs and/or a legible street map not included
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4174
- **Severity:** Critical
- **Machine checks:** presence of the named exhibit (photos/sketch/map/invoice)
- **Data needed:** appraisal exhibit fields (photos, sketch, location map, invoice) — not modeled; the appraisal summary PDF used in this pilot's synthetic loans does not include exhibit pages
- **Rationale:** Crisp presence check once appraisal exhibits are captured as their own fields/attachments — condition: 'Building sketch, required photographs and/or a legible street map not included'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G534 — O-FHA-56218 [O-FHA]
- **Q:** Were all valuation, reporting, and fair lending appraisal protocols requirements met?
- **Defect condition:** The appraiser did not identify the name of the PUD and/or check the PUD box on the appraisal form
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4224
- **Severity:** Major
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('PUD') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The appraiser did not identify the name of the PUD and/or check the PUD box on the appraisal form'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G537 — O-FNM-56088 [O-FNM]
- **Q:** Were all value acceptance (appraisal waiver) requirements met?
- **Defect condition:** Special feature code 801 was not included at delivery where value acceptance was exercised
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4685
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('value acceptance') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Special feature code 801 was not included at delivery where value acceptance was exercised'
- **Classified by:** family_classifier
- **Guide candidate:** B5-1-02 — High-Balance Pricing, Mortgage Insurance, Special Feature Codes, and Delivery Limitations (PDF p.717)
- **Guide candidate:** B4-1.4-09 — Special Assessment or Community Facilities Districts Appraisal Requirements (PDF p.629)
- **Guide candidate:** B4-1.4-10 — Value Acceptance (PDF p.631)
- **SME:** [ ] agree [ ] correct: ______

### G538 — O-FNM-56089 [O-FNM]
- **Q:** Were all value acceptance (appraisal waiver) requirements met?
- **Defect condition:** The loan had a characteristic that was not eligible for value acceptance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4686
- **Severity:** Major
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('value acceptance') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The loan had a characteristic that was not eligible for value acceptance'
- **Classified by:** family_classifier
- **Guide candidate:** B2-1.2-01 — Loan-to-Value (LTV) Ratios (PDF p.179)
- **Guide candidate:** B2-1.2-02 — Combined Loan-to-Value (CLTV) Ratios (PDF p.181)
- **Guide candidate:** B2-1.2-03 — Home Equity Combined Loan-to-Value (HCLTV) Ratios (PDF p.182)
- **SME:** [ ] agree [ ] correct: ______

### G539 — O-FNM-56087 [O-FNM]
- **Q:** Were all value acceptance (appraisal waiver) requirements met?
- **Defect condition:** The value acceptance offer is over 4 months old on the Note date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4682
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('value acceptance') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The value acceptance offer is over 4 months old on the Note date'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-10 — Value Acceptance (PDF p.631)
- **Guide candidate:** B4-1.4-11 — Value Acceptance + Property Data (PDF p.634)
- **Guide candidate:** A2-2-04 — Limited Waiver and Enforcement Relief of Representations and Warranties (PDF p.38)
- **SME:** [ ] agree [ ] correct: ______

### G540 — O-FNM-54132 [O-FNM]
- **Q:** Were all value acceptance (appraisal waiver) requirements met?
- **Defect condition:** Value acceptance was exercised when rental income from the subject property is used
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4684
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('value acceptance') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Value acceptance was exercised when rental income from the subject property is used'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-11 — Value Acceptance + Property Data (PDF p.634)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **Guide candidate:** B3-3.8-01 — Rental Income (PDF p.406)
- **SME:** [ ] agree [ ] correct: ______

### G541 — O-FNM-56086 [O-FNM]
- **Q:** Were all value acceptance (appraisal waiver) requirements met?
- **Defect condition:** Value acceptance was exercised where an appraisal was obtained for the transaction
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4471
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('value acceptance') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Value acceptance was exercised where an appraisal was obtained for the transaction'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-10 — Value Acceptance (PDF p.631)
- **Guide candidate:** B4-1.4-11 — Value Acceptance + Property Data (PDF p.634)
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **SME:** [ ] agree [ ] correct: ______

### G542 — O-FNM-54874 [O-FNM]
- **Q:** Were all value acceptance (appraisal waiver) requirements met?
- **Defect condition:** Value acceptance was exercised where it would have been prudent or required to obtain an appraisal
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4683
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('value acceptance') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Value acceptance was exercised where it would have been prudent or required to obtain an appraisal'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-10 — Value Acceptance (PDF p.631)
- **Guide candidate:** B4-1.4-11 — Value Acceptance + Property Data (PDF p.634)
- **Guide candidate:** A2-2-04 — Limited Waiver and Enforcement Relief of Representations and Warranties (PDF p.38)
- **SME:** [ ] agree [ ] correct: ______

### G543 — O-FNM-56231 [O-FNM]
- **Q:** Were all value acceptance + property data requirements met?
- **Defect condition:** Data collection items fail eligibility & a professional report confirming eligibility not obtained
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4577
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('value acceptance') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Data collection items fail eligibility & a professional report confirming eligibility not obtained'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-11 — Value Acceptance + Property Data (PDF p.634)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **Guide candidate:** B2-3-01 — General Property Eligibility (PDF p.258)
- **SME:** [ ] agree [ ] correct: ______

### G544 — O-FNM-56232 [O-FNM]
- **Q:** Were all value acceptance + property data requirements met?
- **Defect condition:** Form 1004D and Completion Alternatives is not in the file as applicable for repairs or alterations
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4692
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'Form 1004D' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'Form 1004D' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Form 1004D and Completion Alternatives is not in the file as applicable for repairs or alterations'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-11 — Value Acceptance + Property Data (PDF p.634)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **Guide candidate:** B4-1.4-10 — Value Acceptance (PDF p.631)
- **SME:** [ ] agree [ ] correct: ______

### G545 — O-FNM-56228 [O-FNM]
- **Q:** Were all value acceptance + property data requirements met?
- **Defect condition:** Property data collection was not obtained after the initial DU offer and prior to the note date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4406
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('value acceptance') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Property data collection was not obtained after the initial DU offer and prior to the note date'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-11 — Value Acceptance + Property Data (PDF p.634)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **Guide candidate:** B4-1.4-10 — Value Acceptance (PDF p.631)
- **SME:** [ ] agree [ ] correct: ______

### G546 — O-FNM-57149 [O-FNM]
- **Q:** Were all value acceptance + property data requirements met?
- **Defect condition:** Property data collection was not submitted to the Property Data API prior to the note date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4687
- **Severity:** Critical
- **Data needed:** live lookup against an external system/database this pilot has no integration with ('Property Data API')
- **Rationale:** Bucket-C-style candidate (decision 016 precedent): references 'Property Data API', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-11 — Value Acceptance + Property Data (PDF p.634)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **Guide candidate:** B4-1.4-10 — Value Acceptance (PDF p.631)
- **SME:** [ ] agree [ ] correct: ______

### G547 — O-FNM-56225 [O-FNM]
- **Q:** Were all value acceptance + property data requirements met?
- **Defect condition:** Property data collector not trained with competent knowledge or vetted by an annual background check
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4688
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('value acceptance') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Property data collector not trained with competent knowledge or vetted by an annual background check'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-11 — Value Acceptance + Property Data (PDF p.634)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **Guide candidate:** B4-1.4-10 — Value Acceptance (PDF p.631)
- **SME:** [ ] agree [ ] correct: ______

### G548 — O-FNM-56230 [O-FNM]
- **Q:** Were all value acceptance + property data requirements met?
- **Defect condition:** Rep & warrant property conditions not met for property data collection needing repairs/completion
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4578
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('value acceptance') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Rep & warrant property conditions not met for property data collection needing repairs/completion'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-11 — Value Acceptance + Property Data (PDF p.634)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **Guide candidate:** B4-1.4-10 — Value Acceptance (PDF p.631)
- **SME:** [ ] agree [ ] correct: ______

### G549 — O-FNM-56227 [O-FNM]
- **Q:** Were all value acceptance + property data requirements met?
- **Defect condition:** SFC 774 was not included at delivery where value acceptance + property data was exercised
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4693
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('value acceptance') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'SFC 774 was not included at delivery where value acceptance + property data was exercised'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-11 — Value Acceptance + Property Data (PDF p.634)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **Guide candidate:** B4-1.4-10 — Value Acceptance (PDF p.631)
- **SME:** [ ] agree [ ] correct: ______

### G550 — O-FNM-56224 [O-FNM]
- **Q:** Were all value acceptance + property data requirements met?
- **Defect condition:** The loan had a characteristic that was not eligible for value acceptance + property data
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4690
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('value acceptance') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The loan had a characteristic that was not eligible for value acceptance + property data'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-11 — Value Acceptance + Property Data (PDF p.634)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **Guide candidate:** B2-1.2-01 — Loan-to-Value (LTV) Ratios (PDF p.179)
- **SME:** [ ] agree [ ] correct: ______

### G551 — O-FNM-56226 [O-FNM]
- **Q:** Were all value acceptance + property data requirements met?
- **Defect condition:** The property data collection did not meet FNMA's Property Data Standard minimum requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4689
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('value acceptance') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: "The property data collection did not meet FNMA's Property Data Standard minimum requirements"
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-11 — Value Acceptance + Property Data (PDF p.634)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **Guide candidate:** B4-1.4-10 — Value Acceptance (PDF p.631)
- **SME:** [ ] agree [ ] correct: ______

### G552 — O-FNM-56229 [O-FNM]
- **Q:** Were all value acceptance + property data requirements met?
- **Defect condition:** The value acceptance + property data offer is over 4 months old on the Note date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4691
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('value acceptance') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The value acceptance + property data offer is over 4 months old on the Note date'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-11 — Value Acceptance + Property Data (PDF p.634)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **Guide candidate:** B4-1.4-10 — Value Acceptance (PDF p.631)
- **SME:** [ ] agree [ ] correct: ______

### G555 — O-FRD-51190 [O-FRD]
- **Q:** Were appraisal delivery requirements met?
- **Defect condition:** The appraisal report was not submitted to the UCDP or did not receive a “successful” status
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4672
- **Severity:** Critical
- **Data needed:** live lookup against an external system/database this pilot has no integration with ('UCDP')
- **Rationale:** Bucket-C-style candidate (decision 016 precedent): references 'UCDP', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G557 — O-FRD-57314 [O-FRD]
- **Q:** Were co-op appraisal requirements met?_x000D_
- **Defect condition:** Co-op comps outside the subject project not from projects with similar common elements/recreation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4545
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Co-op comps outside the subject project not from projects with similar common elements/recreation'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G559 — O-FRD-57313 [O-FRD]
- **Q:** Were co-op appraisal requirements met?_x000D_
- **Defect condition:** Cooperative interest not reported on the appraisal and/or FNMA Form 1074 not attached as an addendum
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4344
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'Form 1074' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'Form 1074' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Cooperative interest not reported on the appraisal and/or FNMA Form 1074 not attached as an addendum'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G561 — O-FRD-57312 [O-FRD]
- **Q:** Were co-op appraisal requirements met?_x000D_
- **Defect condition:** The interior and exterior appraisal of the cooperative unit was not reported on Fannie Mae Form 2090
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4339
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'Form 2090' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'Form 2090' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'The interior and exterior appraisal of the\xa0cooperative unit\xa0was not reported on\xa0Fannie Mae Form 2090'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G563 — O-FRD-50508 [O-FRD]
- **Q:** Were established condo project requirements met?
- **Defect condition:** Applicable occupancy requirements for an established condo project were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4399
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Applicable occupancy requirements for an established condo project were not met'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G564 — O-FRD-55989 [O-FRD]
- **Q:** Were established condo project requirements met?
- **Defect condition:** CPA Feedback Cert or last Feedback Cert, whichever contains the last PAR findings is not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4313
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'CPA Feedback Cert or last Feedback Cert, whichever contains the last PAR findings is not in the file'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G565 — O-FRD-55734 [O-FRD]
- **Q:** Were established condo project requirements met?
- **Defect condition:** Eligibility requirements were not met for an established manufactured home condo project review
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4503
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Eligibility requirements were not met for an established manufactured home condo project review'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G567 — O-FRD-55991 [O-FRD]
- **Q:** Were established condo project requirements met?
- **Defect condition:** Note date not w/in 120 days of CPA Feedback Cert/last Feedback Cert whichever has last PAR findings
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4314
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Note date not w/in 120 days of CPA Feedback Cert/last Feedback Cert whichever has last PAR findings'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G568 — O-FRD-55990 [O-FRD]
- **Q:** Were established condo project requirements met?
- **Defect condition:** Project review/eligibility req's not met where Condo Project Advisor has yellow or incomplete status
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4312
- **Severity:** Critical
- **Data needed:** live lookup against an external system/database this pilot has no integration with ('Condo Project Advisor')
- **Rationale:** Bucket-C-style candidate (decision 016 precedent): references 'Condo Project Advisor', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G569 — O-FRD-57380 [O-FRD]
- **Q:** Were established condo project requirements met?
- **Defect condition:** The condo Project Assessment Request (PAR) received a Not Eligible status without evidence of appeal
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4315
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The condo Project Assessment Request (PAR) received a Not Eligible status without evidence of appeal'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G570 — O-FRD-51838 [O-FRD]
- **Q:** Were established condo project requirements met?
- **Defect condition:** The condo project budget requirements were not met and/or it was not for the current fiscal year
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4317
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The condo project budget requirements were not met and/or it was not for the current fiscal year'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G571 — O-FRD-58957 [O-FRD]
- **Q:** Were established condo project requirements met?
- **Defect condition:** The full review questionnaire was not dated within 180 days of the PCS request date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4550
- **Severity:** Major
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The full review questionnaire was not dated within 180 days of the PCS request date'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G572 — O-VA-50802 [O-VA]
- **Q:** Were general condo project eligibility requirements met?
- **Defect condition:** Condo or PUD-not ensured that mandatory HOA assessment is subordinate to the VA-guaranteed mtg
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4447
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Condo or PUD-not ensured that mandatory HOA assessment is subordinate to the VA-guaranteed mtg'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G573 — O-VA-50803 [O-VA]
- **Q:** Were general condo project eligibility requirements met?
- **Defect condition:** Condominium project not VA approved
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4291
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Condominium project not VA approved'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G574 — O-FNM-50877 [O-VA]
- **Q:** Were general condo project eligibility requirements met?
- **Defect condition:** Litigation without meeting the eligible minor litigation criteria
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4223
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Litigation without meeting the eligible minor litigation criteria'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G578 — Approval [O-VA]
- **Q:** Were general condo project eligibility requirements met?
- **Defect condition:** Unable to locate the project approval certificate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4293
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'project approval certificate' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'project approval certificate' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Unable to locate the project approval certificate'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G579 — O-FRD-51013 [O-FRD]
- **Q:** Were general condo project eligibility requirements met?_x000D_
- **Defect condition:** 2-4 unit condo review waived, not all cond met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4105
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: '2-4 unit condo review waived, not all cond met'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G580 — O-FRD-55389 [O-FRD]
- **Q:** Were general condo project eligibility requirements met?_x000D_
- **Defect condition:** Condo HOA litigation amt to exceed 10% of project funded reserves or is unallowable by laws and regs
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4306
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Condo HOA litigation amt to exceed 10% of project funded reserves or is unallowable by laws and regs'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G581 — O-FRD-51836 [O-FRD]
- **Q:** Were general condo project eligibility requirements met?_x000D_
- **Defect condition:** Condo Project Advisor used to obtain a PWR without all project eligibility requirements being met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4574
- **Severity:** Critical
- **Data needed:** live lookup against an external system/database this pilot has no integration with ('Condo Project Advisor')
- **Rationale:** Bucket-C-style candidate (decision 016 precedent): references 'Condo Project Advisor', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G582 — O-FRD-50505 [O-FRD]
- **Q:** Were general condo project eligibility requirements met?_x000D_
- **Defect condition:** Condo project litigation impacts safety, structural or function of subject
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4323
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Condo project litigation impacts safety, structural or function of subject'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G583 — O-FRD-56268 [O-FRD]
- **Q:** Were general condo project eligibility requirements met?_x000D_
- **Defect condition:** File did not document project meets FNMA’s full review req's where CPM status is Certified by Lender
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4597
- **Severity:** Critical
- **Data needed:** live lookup against an external system/database this pilot has no integration with ('CPM')
- **Rationale:** Bucket-C-style candidate (decision 016 precedent): references 'CPM', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G585 — O-FNM-53853 [O-FRD]
- **Q:** Were general condo project eligibility requirements met?_x000D_
- **Defect condition:** Project Questionnaire not found (when required)
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4308
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'Project Questionnaire' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'Project Questionnaire' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Project Questionnaire not found (when required)'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G586 — O-FRD-50503 [O-FRD]
- **Q:** Were general condo project eligibility requirements met?_x000D_
- **Defect condition:** Required condo project review not conducted or was incomplete
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4322
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Required condo project review not conducted or was incomplete'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G587 — O-FRD-54181 [O-FRD]
- **Q:** Were general condo project eligibility requirements met?_x000D_
- **Defect condition:** Subject 2-4 unit condominium project had over 4 units and/or more than 1 commercial unit
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4104
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Subject 2-4 unit condominium project had over 4 units and/or more than 1 commercial unit'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G589 — O-FRD-52172 [O-FRD]
- **Q:** Were general condo project eligibility requirements met?_x000D_
- **Defect condition:** The condominium project commercial or non-residential space was not calculated correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4295
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The condominium project commercial or non-residential space was not calculated correctly'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G590 — O-FRD-50509 [O-FRD]
- **Q:** Were general condo project eligibility requirements met?_x000D_
- **Defect condition:** The project has over 35% commercial or non-residential space which is ineligible
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4318
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The project has over 35% commercial or non-residential space which is ineligible'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G591 — O-FRD-50506 [O-FRD]
- **Q:** Were general condo project eligibility requirements met?_x000D_
- **Defect condition:** Total number of condo units owned by same person/entity exceeds limits
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4401
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Total number of condo units owned by same person/entity exceeds limits'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G592 — HOAMinutes [O-FRD]
- **Q:** Were general condo project eligibility requirements met?_x000D_
- **Defect condition:** Unable to locate the projects HOA meeting minutes
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4311
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Unable to locate the projects HOA meeting minutes'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G594 — O-FRD-59356 [O-FRD]
- **Q:** Were general co-op eligibility requirements met?
- **Defect condition:** Project review waiver exercised where project is terminating or involved in insolvency proceedings
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4663
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Project review waiver exercised where project is terminating or involved in insolvency proceedings'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G595 — O-FRD-52745 [O-FRD]
- **Q:** Were general co-op eligibility requirements met?
- **Defect condition:** The cooperative project does not meet eligibility requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4349
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The cooperative project does not meet eligibility requirements'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G596 — O-FRD-52744 [O-FRD]
- **Q:** Were general co-op eligibility requirements met?
- **Defect condition:** The cooperative project review as applicable per project type is not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4350
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The cooperative project review as applicable per project type is not in the file'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G597 — O-FRD-52746 [O-FRD]
- **Q:** Were general co-op eligibility requirements met?
- **Defect condition:** The subject is a cooperative hotel or similar type of transient housing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4342
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The subject is a cooperative hotel or similar type of transient housing'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G600 — O-FRD-50520 [O-FRD]
- **Q:** Were leasehold estate requirements met?
- **Defect condition:** Security Instrument legal desc leasehold did not refer to recorded lease
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4496
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Security Instrument legal desc leasehold did not refer to recorded lease'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G602 — O-FRD-52750 [O-FRD]
- **Q:** Were co-op project eligibility requirements met?_x000D_
- **Defect condition:** Co-op has been 30+ days delinq in last yr blanket mtg pymts, taxes, insurance &/or other obligations
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4341
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Co-op has been 30+ days delinq in last yr blanket mtg pymts, taxes, insurance &/or other obligations'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G604 — O-FRD-52751 [O-FRD]
- **Q:** Were co-op project eligibility requirements met?_x000D_
- **Defect condition:** Over 15% of co-op shareholders are over 60 days delinq in maintenance fees/assessments
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4351
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Over 15% of co-op shareholders are over 60 days delinq in maintenance fees/assessments'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G605 — O-FRD-59354 [O-FRD]
- **Q:** Were co-op project eligibility requirements met?_x000D_
- **Defect condition:** Subject of action causing project to not exist/termination/deconversion/legal structure dissolution
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4572
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Subject of action causing project to not exist/termination/deconversion/legal structure dissolution'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G606 — O-FRD-59355 [O-FRD]
- **Q:** Were co-op project eligibility requirements met?_x000D_
- **Defect condition:** Subject of voluntary-invol bankruptcy/insolvency/liquidation/receivership proceeding or similar
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4570
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Subject of voluntary-invol bankruptcy/insolvency/liquidation/receivership proceeding or similar'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G607 — O-FRD-52747 [O-FRD]
- **Q:** Were co-op project eligibility requirements met?_x000D_
- **Defect condition:** The co-op units & common areas are incomplete &/or are subject to addt'l phasing or annexation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4459
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: "The co-op units & common areas are incomplete &/or are subject to addt'l phasing or annexation"
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G608 — O-FRD-52752 [O-FRD]
- **Q:** Were co-op project eligibility requirements met?_x000D_
- **Defect condition:** The cooperative project does not consist of two or more 1-unit dwellings
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4347
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The cooperative project does not consist of two or more 1-unit dwellings'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G609 — O-FRD-52749 [O-FRD]
- **Q:** Were co-op project eligibility requirements met?_x000D_
- **Defect condition:** The cooperative project's budget did not meet requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4340
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: "The cooperative project's budget did not meet requirements"
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G610 — O-FRD-54677 [O-FRD]
- **Q:** Were co-op project eligibility requirements met?_x000D_
- **Defect condition:** The maximum single-investor concentration limit for the cooperative projects was exceeded
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4353
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The maximum single-investor concentration limit for\xa0the cooperative projects was exceeded'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G612 — O-FRD-53876 [O-FRD]
- **Q:** Were co-op share loan eligibility requirements met?
- **Defect condition:** Co-op share loan did not meet IRS section 216 req's for co-op housing in effect as of delivery date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4343
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: "Co-op share loan did not meet IRS section 216 req's for co-op housing in effect as of delivery date"
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G614 — O-FRD-52753 [O-FRD]
- **Q:** Were co-op share loan eligibility requirements met?
- **Defect condition:** The cooperative share loan did not comply with all eligibility requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4352
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The cooperative share loan did not comply with all eligibility requirements'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G615 — O-FRD-53877 [O-FRD]
- **Q:** Were co-op share loan eligibility requirements met?
- **Defect condition:** The pro rata cooperative share of the cooperative corporation's debt was not calculated correctly
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4589
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: "The pro rata cooperative share of the cooperative corporation's debt was not calculated correctly"
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G641 — O-RHS-58082 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were all subject, neighborhood, site and improvements sections of the appraisal complete and accurate?
- **Defect condition:** Address,owner,county,legal, parcel ID,neighborhood &\or occupant et al is missing/incomplete
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4246
- **Severity:** Major
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('parcel') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Address,owner,county,legal, parcel ID,neighborhood &\\or occupant et al is missing/incomplete'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G644 — O-RHS-50577 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were all the required exhibits provided and acceptable?
- **Defect condition:** No, all the required exhibits were not provided and/or acceptable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4177, 4178
- **Severity:** Critical
- **Machine checks:** presence of the named exhibit (photos/sketch/map/invoice)
- **Data needed:** appraisal exhibit fields (photos, sketch, location map, invoice) — not modeled; the appraisal summary PDF used in this pilot's synthetic loans does not include exhibit pages
- **Rationale:** Crisp presence check once appraisal exhibits are captured as their own fields/attachments — condition: 'No, all the required exhibits were not provided and/or acceptable'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G659 — O-VA-00806 [O-VA]
- **Q:** Where a property has been affected by a disaster, were all appraisal requirements met?
- **Defect condition:** Appraisal pre-dates disaster and borrower certification of property condition is missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4382
- **Severity:** Critical
- **Machine checks:** presence of borrower certification of pre-disaster property condition
- **Data needed:** disaster borrower-certification doc type (not in corpus)
- **Rationale:** Crisp presence check, same disaster-documentation family as G660/G661.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G660 — O-VA-00493 [O-VA]
- **Q:** Where a property has been affected by a disaster, were all appraisal requirements met?
- **Defect condition:** Appraisal pre-dates disaster and inspection evidencing property is pre-disaster condition is missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4553
- **Severity:** Critical
- **Machine checks:** presence of an inspection evidencing pre-disaster property condition
- **Data needed:** disaster pre-condition inspection doc type (not in corpus)
- **Rationale:** Same disaster-documentation family as G659/G661.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G661 — O-VA-00805 [O-VA]
- **Q:** Where a property has been affected by a disaster, were all appraisal requirements met?
- **Defect condition:** Appraisal pre-dates disaster and lender certification property is pre-disaster condition is missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4384
- **Severity:** Critical
- **Machine checks:** presence of lender certification of pre-disaster property condition
- **Data needed:** disaster lender-certification doc type (not in corpus)
- **Rationale:** Same disaster-documentation family as G659/G660.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G667 — O-FNM-55653 [O-FNM]
- **Q:** Where a property has been affected by a disaster, were all appraisal requirements met?
- **Defect condition:** The appraisal was dated over 180 days before the note date in a property affected by a disaster
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4136
- **Severity:** Critical
- **Machine checks:** threshold math once the underlying date/percent field exists
- **Data needed:** a specific date/percentage field ('180 days') not currently in FIELD_SPECS/FACT_SPECS for any appraisal-adjacent document
- **Rationale:** Crisp threshold math ('180 days') once the field exists — not a judgment call, just an unbuilt field; condition: 'The appraisal was dated over 180 days before the note date in a property affected by a disaster'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-07 — Mixed-Use Property Appraisal Requirements (PDF p.626)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **Guide candidate:** B2-3-01 — General Property Eligibility (PDF p.258)
- **SME:** [ ] agree [ ] correct: ______

### G668 — O-FNM-55652 [O-FNM]
- **Q:** Where a property has been affected by a disaster, were all appraisal requirements met?
- **Defect condition:** UW docs, credit reports, income/asset verifications over 180 days prior to note in disaster area
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4139
- **Severity:** Critical
- **Machine checks:** threshold math once the underlying date/percent field exists
- **Data needed:** a specific date/percentage field ('180 days') not currently in FIELD_SPECS/FACT_SPECS for any appraisal-adjacent document
- **Rationale:** Crisp threshold math ('180 days') once the field exists — not a judgment call, just an unbuilt field; condition: 'UW docs, credit reports, income/asset verifications over 180 days prior to note in disaster area'
- **Classified by:** family_classifier
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-5.2-01 — Requirements for Credit Reports (PDF p.476)
- **Guide candidate:** B3-5.2-02 — Types of Credit Reports (PDF p.480)
- **SME:** [ ] agree [ ] correct: ______

### G671 — O-VA-00490 [O-VA]
- **Q:** Where the appraisal was completed subject to completion, repairs, or alterations, were all requirements met?
- **Defect condition:** Appraisal subject to repairs is missing the appraiser's itemized list of repairs/other action needed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4204
- **Severity:** Critical
- **Machine checks:** presence of the appraiser's itemized list of repairs/required actions
- **Data needed:** repair-itemization exhibit (not modeled)
- **Rationale:** Crisp presence check once this specific exhibit is captured; reclassified from the conservative-default RED.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G673 — O-FRD-56572 [O-FRD]
- **Q:** Where the appraisal was completed subject to completion, repairs, or alterations, were all requirements met?
- **Defect condition:** Form 400, Warranty of Completion of Construction, used but not signed/dated by borr & builder's rep
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4676
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'Form 400' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'Form 400' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: "Form 400, Warranty of Completion of Construction, used but not signed/dated by borr & builder's rep"
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G674 — O-FRD-00664 [O-FRD]
- **Q:** Where the appraisal was completed subject to completion, repairs, or alterations, were all requirements met?
- **Defect condition:** No repair final inspection/completion report dated prior to closing &/or no photos as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4247
- **Severity:** Critical
- **Machine checks:** presence of the named exhibit (photos/sketch/map/invoice)
- **Data needed:** appraisal exhibit fields (photos, sketch, location map, invoice) — not modeled; the appraisal summary PDF used in this pilot's synthetic loans does not include exhibit pages
- **Rationale:** Crisp presence check once appraisal exhibits are captured as their own fields/attachments — condition: 'No repair final inspection/completion report dated prior to closing &/or no photos as applicable'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G676 — O-FRD-54687 [O-FRD]
- **Q:** Where the appraisal was completed subject to completion, repairs, or alterations, were all requirements met?
- **Defect condition:** The file did not contain Form 442 where the appraisal was made subject to repairs or alterations
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4254
- **Severity:** Critical
- **Data needed:** as G040 — Freddie Form 442, not FHA MPR completion cert
- **Rationale:** Same program-mismatch rejection as G040.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G677 — O-FRD-56267 [O-FRD]
- **Q:** Where the appraisal was completed subject to completion, repairs, or alterations, were all requirements met?
- **Defect condition:** The file did not contain Form 442, Form 400, or other similar form in a new or proposed construction
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4525
- **Severity:** Critical
- **Data needed:** as G040 — Freddie Form 442/400, not FHA MPR completion cert
- **Rationale:** Same program-mismatch rejection as G040.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G678 — O-FRD-52231 [O-FRD]
- **Q:** Where the property has energy-efficient improvements, were all requirements met?
- **Defect condition:** Appraiser did not use additional due diligence or Form 820.05 for lack of energy efficient comps
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4396
- **Severity:** Critical
- **Machine checks:** presence of the named form/document once its doc type exists
- **Data needed:** 'Form 820' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)
- **Rationale:** Crisp presence check once 'Form 820' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Appraiser did not use additional due diligence or Form 820.05 for lack of energy efficient comps'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G689 — O-FRD-54680 [O-FRD]
- **Q:** Where the subject has multiple parcels, were all requirements met?
- **Defect condition:** Each of the multiple parcels not conveyed in entirety with the being the first lien on each
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4114
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('parcel') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Each of the multiple parcels not conveyed in entirety with the being the first lien on each'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G690 — O-FRD-54682 [O-FRD]
- **Q:** Where the subject has multiple parcels, were all requirements met?
- **Defect condition:** No documentation non-adjoining parcels without the residence cannot be improved with a dwelling
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4528
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('parcel') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'No documentation non-adjoining parcels without the residence cannot be improved with a dwelling'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G691 — O-FRD-54681 [O-FRD]
- **Q:** Where the subject has multiple parcels, were all requirements met?
- **Defect condition:** Non-adjoining parcels are not separated due to a road, waterfront access or similar as allowable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4530
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('parcel') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Non-adjoining parcels are not separated due to a road, waterfront access or similar as allowable'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G693 — O-FRD-50486 [O-FRD]
- **Q:** Where the subject has multiple parcels, were all requirements met?
- **Defect condition:** Subject w/ more than 1 adjoining parcel file did not confirm parcels had no additional residence
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4517
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('parcel') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Subject w/ more than 1 adjoining parcel file did not confirm parcels had no additional residence'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G694 — O-FRD-54679 [O-FRD]
- **Q:** Where the subject has multiple parcels, were all requirements met?
- **Defect condition:** The subject's additional parcels were not adjoining and/or did not have the same basic zoning
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4116
- **Severity:** Critical
- **Data needed:** condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans
- **Rationale:** Matched project-documentation vocabulary ('parcel') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: "The subject's additional parcels were not adjoining and/or did not have the same basic zoning"
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

## RED

### G011 — O-FRD-55346 [O-FRD]
- **Q:** Appraisal Review FAQ, Q5: If the desk review determined that the value of the property is supported, was it still ensured that the condition and marketability of the subject property are acceptable and that the mortgaged premises is adequate collateral?
- **Defect condition:** No, the condition & marketability and that the premises are deemed acceptable was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4230
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('marketability') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'No, the condition & marketability and that the premises are deemed acceptable was not provided'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G013 — O-FRD-55347 [O-FRD]
- **Q:** Appraisal Review FAQ, Q6: If the desk review performed by a qualified reviewer was not able to determine the accuracy of the appraisal or the adequacy of the collateral, was a desk review or field review by a certified appraiser obtained?
- **Defect condition:** No, a desk review or field review was not obtained by a certified appraiser as required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4232
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'No, a desk review or field review was not obtained by a certified appraiser as required'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G015 — O-FRD-55348 [O-FRD]
- **Q:** Appraisal Review FAQ, Q6: If the internal desk review prompted a desk review or field review by a certified appraiser, was the original market value supported?
- **Defect condition:** No, the original value was not supported
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4231
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('not supported') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'No, the original value was not supported'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G017 — O-FRD-55349 [O-FRD]
- **Q:** Appraisal Review FAQ, Q8: When an analyst or appraiser performs a desk review to satisfy the QC reverification requirement, was Form F1033-1 used or another appropriate form?
- **Defect condition:** No, form F1033-1 or another appropriate form was not utilized
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4233
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('appropriate') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'No, form F1033-1 or another appropriate form was not utilized'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G019 — FlipGuide-2 [GENERIC]
- **Q:** Are all requirements met when the seller acquired the property within 180 days of the contract ( including Full Appraisal regardless of DU)?
- **Defect condition:** Assignments of contract sale and not a resale under employee relocation program so is not acceptable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4583, 4584
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('acceptable') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Assignments of contract sale and not a resale under employee relocation program so is not acceptable'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-02 — Subject and Contract Sections of the Appraisal Report (PDF p.570)
- **Guide candidate:** B4-1.4-07 — Mixed-Use Property Appraisal Requirements (PDF p.626)
- **Guide candidate:** A1-1-01 — Application and Approval of Seller/Servicer (PDF p.20)
- **SME:** [ ] agree [ ] correct: ______

### G020 — FlipGuide [GENERIC]
- **Q:** Are all requirements met when the seller acquired the property within 180 days of the contract ( including Full Appraisal regardless of DU)?
- **Defect condition:** No, all requirements have not been met to satisfy potential property flip
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4421
- **Severity:** Critical
- **Stays human:** bare 'all requirements... not met' catch-all bundling several distinct property-flip sub-rules (180-day window, resale-price-increase %, etc.)
- **Rationale:** Reclassified from the family classifier's numeric-threshold match (it picked up '180 days' from the QUESTION text, not the response): the actual defect condition is a bare 'all requirements have not been met' catch-all bundling several distinct property-flip sub-tests, not a single checkable fact — same pattern as application-verification's VA-disclosure catch-all; needs SME decomposition first.
- **Classified by:** hand_override
- **Guide candidate:** B4-1.3-02 — Subject and Contract Sections of the Appraisal Report (PDF p.570)
- **Guide candidate:** B4-1.4-07 — Mixed-Use Property Appraisal Requirements (PDF p.626)
- **Guide candidate:** A1-1-01 — Application and Approval of Seller/Servicer (PDF p.20)
- **SME:** [ ] agree [ ] correct: ______

### G025 — O-FHA-50661 [O-FHA]
- **Q:** Does any identified legal restriction on conveyance conform with the requirements?
- **Defect condition:** Subject has leased equipment, leased energy system or PPA not free of restrictions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4554
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Subject has leased equipment, leased energy system or PPA not free of restrictions'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G027 — O-FNM-57787, O-FRD-57793 [O-FNM/O-FRD]
- **Q:** Does the appraisal evidence unacceptable appraisal practices?_x000D_
- **Defect condition:** All documentation & communications related to the initiation & outcome of the ROV not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4601, 4602
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('unacceptable') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'All documentation & communications related to the initiation & outcome of the ROV not in the file'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.1-04 — Unacceptable Appraisal Practices (PDF p.541)
- **Guide candidate:** A2-3.2-02 — Enforcement Relief for Breaches of Certain Representations and Warranties Related to Underwriting and Eligibility (PDF p.65)
- **Guide candidate:** A3-2-02 — Responsible Lending Practices (PDF p.119)
- **SME:** [ ] agree [ ] correct: ______

### G028 — O-FRD-57996 [O-FRD]
- **Q:** Does the appraisal evidence unacceptable appraisal practices?_x000D_
- **Defect condition:** Appraiser didn't address concerns adequately & appraisal wasn't rejected & replaced w/ a new one
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4544
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('unacceptable') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: "Appraiser didn't address concerns adequately & appraisal wasn't rejected & replaced w/ a new one"
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G029 — O-FRD-02577 [O-FRD]
- **Q:** Does the appraisal evidence unacceptable appraisal practices?_x000D_
- **Defect condition:** Evidence an unacceptable practice was used in establishing the value of the property
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4667
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('unacceptable') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Evidence an unacceptable practice was used in establishing the value of the property'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G031 — O-FNM-57523 [O-FNM]
- **Q:** Does the appraisal evidence unacceptable appraisal practices?_x000D_
- **Defect condition:** Review of the appraisal revealed unacceptable appraisal practices were used in the report
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4666
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('unacceptable') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Review of the appraisal revealed unacceptable appraisal practices were used in the report'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.1-04 — Unacceptable Appraisal Practices (PDF p.541)
- **Guide candidate:** B4-1.3-01 — Review of the Appraisal Report (PDF p.569)
- **Guide candidate:** B4-1.2-01 — Appraisal Report Forms and Exhibits (PDF p.547)
- **SME:** [ ] agree [ ] correct: ______

### G032 — O-FNM-57524, O-FRD-55992 [O-FNM/O-FRD]
- **Q:** Does the appraisal evidence unacceptable appraisal practices?_x000D_
- **Defect condition:** The appraisal report contains unacceptable terms and phrases identified as prohibited language
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4562, 4563
- **Severity:** Critical/Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('unacceptable') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'The appraisal report contains unacceptable terms and phrases identified as prohibited language'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.1-04 — Unacceptable Appraisal Practices (PDF p.541)
- **Guide candidate:** B2-1.3-04 — Prohibited Reﬁnancing Practices (PDF p.203)
- **Guide candidate:** B4-1.2-01 — Appraisal Report Forms and Exhibits (PDF p.547)
- **SME:** [ ] agree [ ] correct: ______

### G033 — O-FRD-57998 [O-FRD]
- **Q:** Does the appraisal evidence unacceptable appraisal practices?_x000D_
- **Defect condition:** Turn-time expectations for communicating the results of the ROV to the borrower were not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4613
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('unacceptable') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Turn-time expectations for communicating the results of the ROV to the borrower were not documented'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G034 — O-FRD-57997 [O-FRD]
- **Q:** Does the appraisal evidence unacceptable appraisal practices?_x000D_
- **Defect condition:** Unacceptable appraisal practice/unresolved material deficiencies & appraisal/findings not reported
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4668
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('unacceptable') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Unacceptable appraisal practice/unresolved material deficiencies & appraisal/findings not reported'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G035 — O-FRD-00497 [O-FRD]
- **Q:** Does the appraisal report meet all requirements?
- **Defect condition:** Appraisal form was incorrect for the property & inspection type or as per LPA
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4225
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Appraisal form was incorrect for the property & inspection type or as per LPA'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G036 — O-FRD-00505 [O-FRD]
- **Q:** Does the appraisal report meet all requirements?
- **Defect condition:** Exterior only not upgraded where sufficient Interior/exterior characteristics can not be obtained
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4413
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Exterior only not upgraded where sufficient Interior/exterior characteristics can not be obtained'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G038 — O-FRD-57381 [O-FRD]
- **Q:** Does the appraisal report meet all requirements?
- **Defect condition:** No market area analysis/market condition adj using a min of 12 mos data from acceptable data sources
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4504
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('acceptable') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'No market area analysis/market condition adj using a min of 12 mos data from acceptable data sources'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G043 — O-FRD-55335 [O-FRD]
- **Q:** Form F1033-1, Section I, 1. Is the information in the subject section complete and accurate?
- **Defect condition:** No, the information in the subject section is incomplete or inaccurate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4429
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'No, the information in the subject section is incomplete or inaccurate'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G045 — O-FRD-55345 [O-FRD]
- **Q:** Form F1033-1, Section I, 10. If the opinion of market value in the appraisal report under review is inaccurate as of the effective date of the appraisal report, was Section II completed to substantiate and provide a new opinion of value?
- **Defect condition:** Market value opinion is inaccurate as of the effective date of the report - Section II not completed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4428
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Market value opinion is inaccurate as of the effective date of the report - Section II not completed'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G048 — O-FRD-55344 [O-FRD]
- **Q:** Form F1033-1, Section I, 10. Is the opinion of market value in the appraisal under review accurate as of the effective date of the appraisal report?
- **Defect condition:** The market value opinion is not accurate as of the effective date of the appraisal
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4427
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The market value opinion is not accurate as of the effective date of the appraisal'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G049 — O-FRD-55336 [O-FRD]
- **Q:** Form F1033-1, Section I, 2. Is the information in the contract section complete and accurate?
- **Defect condition:** No, information in the contract section is incomplete or inaccurate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4430
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'No, information in the contract section is incomplete or inaccurate'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G051 — O-FRD-55337 [O-FRD]
- **Q:** Form F1033-1, Section I, 3. Is the information in the neighborhood section complete and accurate?
- **Defect condition:** No, the information in the neighborhood section is incomplete or inaccurate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4431
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'No, the information in the neighborhood section is incomplete or inaccurate'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G053 — O-FRD-55338 [O-FRD]
- **Q:** Form F1033-1, Section I, 4. Is the information in the site section complete and accurate?
- **Defect condition:** No, information in the site section is incomplete or inaccurate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4432
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'No, information in the site section is incomplete or inaccurate'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G055 — O-FRD-55339 [O-FRD]
- **Q:** Form F1033-1, Section I, 5. Is the data in the improvements section complete and accurate?
- **Defect condition:** No, the data in the improvements section is incomplete or inaccurate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4433
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'No, the data in the improvements section is incomplete or inaccurate'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G059 — O-FRD-55341 [O-FRD]
- **Q:** Form F1033-1, Section I, 7. Are the data and analysis (including the individual adjustments) presented in the sales comparison approach complete and accurate?
- **Defect condition:** Data and analysis (including the individual adjustments) in the are incomplete/inaccurate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4434
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Data and analysis (including the individual adjustments) in the are incomplete/inaccurate'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G062 — O-FRD-55342 [O-FRD]
- **Q:** Form F1033-1, Section I, 8. Are the data and analysis presented in the income and cost approaches complete and accurate if developed?
- **Defect condition:** The data and analysis presented in the income and cost approaches are incomplete or inaccurate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4435
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The data and analysis presented in the income and cost approaches are incomplete or inaccurate'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G063 — O-FRD-55343 [O-FRD]
- **Q:** Form F1033-1, Section I, 9. Is the sale or transfer history reported for the subject property and each of the comparable sales complete and accurate?
- **Defect condition:** No, the sale or transfer history does not appear to be complete and/or accurate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4436
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('appear') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'No, the sale or transfer history does not appear to be complete and/or accurate'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G066 — O-FRD-58096 [O-FRD]
- **Q:** If the subject is in a federally declared disaster area, were all requirements met?
- **Defect condition:** File did not document if there were adverse effects on the subject property impacted by a disaster
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4381
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'File did not document if there were adverse effects on the subject property impacted by a disaster'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G067 — O-FRD-58100 [O-FRD]
- **Q:** If the subject is in a federally declared disaster area, were all requirements met?
- **Defect condition:** It was not ensured that all damage was documented and covered by insurance as required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4389
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'It was not ensured that all damage was documented and covered by insurance as required'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G069 — O-FRD-58097 [O-FRD]
- **Q:** If the subject is in a federally declared disaster area, were all requirements met?
- **Defect condition:** Subject with an appraisal & disaster impact did not document damage was not safety/structural
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4387
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Subject with an appraisal & disaster impact did not document damage was not safety/structural'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G071 — CRMReview [GENERIC]
- **Q:** Was the GAAR worksheet completed in the file and all applicable conditions met?
- **Defect condition:** Unable to locate the GAAR worksheet or confirm the conditions listed are met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4362
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Unable to locate the GAAR worksheet or confirm the conditions listed are met'
- **Classified by:** family_classifier
- **Guide candidate:** D1-3-02 — Lender Post-Closing Quality Control Review of Approval Conditions, Underwriting Decisions, Data, and Documentation (PDF p.1068)
- **Guide candidate:** D2-1-02 — Fannie Mae QC File Request and Submission Requirements (PDF p.1078)
- **SME:** [ ] agree [ ] correct: ______

### G076 — O-FRD-55735 [O-FRD]
- **Q:** Were additional general condo project eligibility requirements met?_x000D_
- **Defect condition:** Condo personalized services/centralized systems red flags not analyzed ensuring its not a condotel
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4328
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('not analyzed') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Condo personalized services/centralized systems red flags not analyzed ensuring its not a condotel'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G087 — O-FRD-50495 [O-FRD]
- **Q:** Were all 2- to 4-unit property requirements met?
- **Defect condition:** 3 rental comps not provided &/or no current rent information or units dissimilar or distant in a 2-4
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4286
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: '3 rental comps not provided &/or no current rent information or units dissimilar or distant in a 2-4'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G088 — O-FRD-50496 [O-FRD]
- **Q:** Were all 2- to 4-unit property requirements met?
- **Defect condition:** For a 2-4, appraisal did not include the rent schedule with current actual & estimated market rent
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4652
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'For a 2-4, appraisal did not include the rent schedule with current actual & estimated market rent'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G095 — O-FNM-58598 [O-FNM]
- **Q:** Were all Comparable sales requirements met?
- **Defect condition:** Comp time adj w/out explanation or analysis of market cond changes from their contract date-eff date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4365
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('without explanation') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Comp time adj w/out explanation or analysis of market cond changes from their contract date-eff date'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-08 — Comparable Sales (PDF p.597)
- **Guide candidate:** B4-1.3-09 — Adjustments to Comparable Sales (PDF p.601)
- **Guide candidate:** A2-3.1-01 — Lender Breach of Contract (PDF p.56)
- **SME:** [ ] agree [ ] correct: ______

### G097 — O-FNM-58600 [O-FNM]
- **Q:** Were all Comparable sales requirements met?
- **Defect condition:** Comps do not have similar physical/legal characteristics as the subject without appraiser commentary
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4631
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('without comment') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Comps do not have similar physical/legal characteristics as the subject without appraiser commentary'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-08 — Comparable Sales (PDF p.597)
- **Guide candidate:** B4-1.3-09 — Adjustments to Comparable Sales (PDF p.601)
- **Guide candidate:** B2-1.5-03 — Legal Requirements (PDF p.236)
- **SME:** [ ] agree [ ] correct: ______

### G098 — O-VA-00477 [O-VA]
- **Q:** Were all Comparable sales requirements met?
- **Defect condition:** Comps further from the subject than similar recent comps or outside of market without explanation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4502
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('without explanation') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Comps further from the subject than similar recent comps or outside of market without explanation'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G099 — O-FNM-50296 [O-FNM]
- **Q:** Were all Comparable sales requirements met?
- **Defect condition:** Comps provided not from within & outside of the new condo, subdivision or PUD without explanation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4205
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('without explanation') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Comps provided not from within & outside of the new condo, subdivision or PUD without explanation'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-08 — Comparable Sales (PDF p.597)
- **Guide candidate:** B4-1.3-09 — Adjustments to Comparable Sales (PDF p.601)
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **SME:** [ ] agree [ ] correct: ______

### G100 — O-VA-00478 [O-VA]
- **Q:** Were all Comparable sales requirements met?
- **Defect condition:** Neighborhood section/addendum did not state competitive listings/contract offerings were considered
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4287
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Neighborhood section/addendum did not state competitive listings/contract offerings were considered'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G101 — O-FNM-00536 [O-FNM]
- **Q:** Were all Comparable sales requirements met?
- **Defect condition:** No dollar amount given for comparables concessions &/or no adjustments made & explanation not given
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4622
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'No dollar amount given for comparables concessions &/or no adjustments made & explanation not given'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-09 — Adjustments to Comparable Sales (PDF p.601)
- **Guide candidate:** B4-1.3-08 — Comparable Sales (PDF p.597)
- **Guide candidate:** B3-4.3-10 — Anticipated Sales Proceeds (PDF p.453)
- **SME:** [ ] agree [ ] correct: ______

### G103 — O-FNM-54816 [O-FNM]
- **Q:** Were all Comparable sales requirements met?
- **Defect condition:** The comps do not reflect the same positive & negative location characteristics as the subject
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4285
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The comps do not reflect the same positive & negative location characteristics as the subject'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-08 — Comparable Sales (PDF p.597)
- **Guide candidate:** B4-1.3-09 — Adjustments to Comparable Sales (PDF p.601)
- **Guide candidate:** B2-2-03 — Multiple Financed Properties for the Same Borrower (PDF p.244)
- **SME:** [ ] agree [ ] correct: ______

### G104 — O-VA-00476 [O-VA]
- **Q:** Were all Comparable sales requirements met?
- **Defect condition:** The use of comps with a sale date over 12 months was not adequately explained by the appraiser
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4138
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('not adequately') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'The use of comps with a sale date over 12 months was not adequately explained by the appraiser'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G105 — O-VA-50793 [O-VA]
- **Q:** Were all Comparable sales requirements met?
- **Defect condition:** Value not from sales comparison approach or if another approach not justified by the appraiser
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4267
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Value not from sales comparison approach or if another approach not justified by the appraiser'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G117 — O-FHA-51473 [O-FHA]
- **Q:** Were all Gross Living Area (GLA) appraisal requirements met?
- **Defect condition:** An encroachment was identified on the subject or neighboring property without an easement
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4579
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'An encroachment was identified on the subject or neighboring property without an easement'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G118 — O-FHA-54018 [O-FHA]
- **Q:** Were all Gross Living Area (GLA) appraisal requirements met?
- **Defect condition:** Externalities not reported &/or marketability & positive or negative value effects not addressed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4414
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('marketability') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Externalities not reported &/or marketability & positive or negative value effects not addressed'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G119 — O-FHA-50749 [O-FHA]
- **Q:** Were all Gross Living Area (GLA) appraisal requirements met?
- **Defect condition:** The appraiser did not report if the subject is Fee Simple or Leasehold
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4586
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('did not report if') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'The appraiser did not report if the subject is Fee Simple or Leasehold'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G121 — O-FHA-50751 [O-FHA]
- **Q:** Were all Gross Living Area (GLA) appraisal requirements met?
- **Defect condition:** The property does not comply with zoning ordinances and is not “Legal Non-Conforming”
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4531
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The property does not comply with zoning ordinances and is not “Legal Non-Conforming”'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G123 — O-FNM-55586 [O-FNM]
- **Q:** Were all Gross Living Area (GLA) appraisal requirements met?_x000D_
- **Defect condition:** ANSI Z765-2021 standard not adhered to & explanation of non-compliance was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4507
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'ANSI Z765-2021 standard not adhered to & explanation of non-compliance was not provided'
- **Classified by:** family_classifier
- **Guide candidate:** A3-2-01 — Compliance With Laws (PDF p.107)
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **SME:** [ ] agree [ ] correct: ______

### G124 — O-FNM-55583 [O-FNM]
- **Q:** Were all Gross Living Area (GLA) appraisal requirements met?_x000D_
- **Defect condition:** ANSI min ceiling height not met & addt'l sq ft not on addt'l line &/or appropriate adj not applied
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4147, 4148
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('appropriate') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: "ANSI min ceiling height not met & addt'l sq ft not on addt'l line &/or appropriate adj not applied"
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.1-04 — Unacceptable Appraisal Practices (PDF p.541)
- **Guide candidate:** B4-1.1-06 — Uniform Appraisal Dataset (UAD) and the Uniform Collateral Data Portal (UCDP) (PDF p.545)
- **Guide candidate:** B4-1.2-01 — Appraisal Report Forms and Exhibits (PDF p.547)
- **SME:** [ ] agree [ ] correct: ______

### G125 — O-FNM-55584 [O-FNM]
- **Q:** Were all Gross Living Area (GLA) appraisal requirements met?_x000D_
- **Defect condition:** ANSI min ceiling height not met w/out explaining how ANSI standard was met & use of addt'l sq ft
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4145, 4146
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: "ANSI min ceiling height not met w/out explaining how ANSI standard was met & use of addt'l sq ft"
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.2-04 — Appraisal Age and Use Requirements (PDF p.559)
- **Guide candidate:** B4-1.4-07 — Mixed-Use Property Appraisal Requirements (PDF p.626)
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **SME:** [ ] agree [ ] correct: ______

### G126 — O-FNM-55582 [O-FNM]
- **Q:** Were all Gross Living Area (GLA) appraisal requirements met?_x000D_
- **Defect condition:** Detached structures finished square feet not put on a different line &/or not in reported GLA
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4377, 4378
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Detached structures finished square feet not put on a different line &/or not in reported GLA'
- **Classified by:** family_classifier
- **Guide candidate:** B3-3.5-02 — Business Structures (PDF p.384)
- **Guide candidate:** B3-3.6-02 — Income Reported on IRS Form 1040 (PDF p.391)
- **Guide candidate:** B3-3.6-03 — Income or Loss Reported on IRS Form 1040, Schedule C (PDF p.393)
- **SME:** [ ] agree [ ] correct: ______

### G128 — O-FNM-55579 [O-FNM]
- **Q:** Were all Gross Living Area (GLA) appraisal requirements met?_x000D_
- **Defect condition:** Square Footage Method: ANSI Z765-2021 not used to measure, calculate & report GLA /Non-GLA
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4441
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Square Footage Method: ANSI Z765-2021 not used to measure, calculate & report GLA /Non-GLA'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.2-01 — Appraisal Report Forms and Exhibits (PDF p.547)
- **Guide candidate:** B4-1.3-01 — Review of the Appraisal Report (PDF p.569)
- **Guide candidate:** B4-1.3-02 — Subject and Contract Sections of the Appraisal Report (PDF p.570)
- **SME:** [ ] agree [ ] correct: ______

### G129 — O-FNM-55581 [O-FNM]
- **Q:** Were all Gross Living Area (GLA) appraisal requirements met?_x000D_
- **Defect condition:** The appraiser's sketching or 3D scanning software output did not conform to ANSI Z765-2021 standards
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4637, 4638
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: "The appraiser's sketching or 3D scanning software output did not conform to ANSI Z765-2021 standards"
- **Classified by:** family_classifier
- **Guide candidate:** A2-4.1-04 — Notarization Standards (PDF p.99)
- **Guide candidate:** B3-3.2-01 — Standards for Employment and Income Documentation (PDF p.327)
- **Guide candidate:** B3-3.2-02 — Standards for Employment-Related Income (PDF p.330)
- **SME:** [ ] agree [ ] correct: ______

### G130 — O-FNM-55580 [O-FNM]
- **Q:** Were all Gross Living Area (GLA) appraisal requirements met?_x000D_
- **Defect condition:** The finished above-grade GLA, below-grade square footage, &/or room count was inconsistent
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4460, 4461
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('inconsistent') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'The finished above-grade GLA, below-grade square footage, &/or room count was inconsistent'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.1-04 — Unacceptable Appraisal Practices (PDF p.541)
- **Guide candidate:** B4-1.1-06 — Uniform Appraisal Dataset (UAD) and the Uniform Collateral Data Portal (UCDP) (PDF p.545)
- **Guide candidate:** B4-1.2-01 — Appraisal Report Forms and Exhibits (PDF p.547)
- **SME:** [ ] agree [ ] correct: ______

### G132 — O-FNM-50291 [O-FNM]
- **Q:** Were all Improvements section of the appraisal requirements met?
- **Defect condition:** A description and impact of an outbuilding on the property not given
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4193
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'A description and impact of an outbuilding on the property not given'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-05 — Improvements Section of the Appraisal Report (PDF p.580)
- **Guide candidate:** B4-1.3-03 — Neighborhood Section of the Appraisal Report (PDF p.572)
- **Guide candidate:** B4-1.3-04 — Site Section of the Appraisal Report (PDF p.577)
- **SME:** [ ] agree [ ] correct: ______

### G133 — O-FNM-50286 [O-FNM]
- **Q:** Were all Improvements section of the appraisal requirements met?
- **Defect condition:** Effective age is higher than the actual age indicating poor subject condition without comment
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4188
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('without comment') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Effective age is higher than the actual age indicating poor subject condition without comment'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-05 — Improvements Section of the Appraisal Report (PDF p.580)
- **Guide candidate:** B4-1.2-04 — Appraisal Age and Use Requirements (PDF p.559)
- **Guide candidate:** B4-1.3-02 — Subject and Contract Sections of the Appraisal Report (PDF p.570)
- **SME:** [ ] agree [ ] correct: ______

### G135 — FNM-Private Rd [O-FNM]
- **Q:** Were all Improvements section of the appraisal requirements met?
- **Defect condition:** Private road noted without condition of the road noted and/or a maintenance agreement was not found
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4558
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Private road noted without condition of the road noted and/or a maintenance agreement was not found'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-05 — Improvements Section of the Appraisal Report (PDF p.580)
- **Guide candidate:** B4-1.3-03 — Neighborhood Section of the Appraisal Report (PDF p.572)
- **Guide candidate:** B4-1.3-04 — Site Section of the Appraisal Report (PDF p.577)
- **SME:** [ ] agree [ ] correct: ______

### G136 — O-FNM-50287 [O-FNM]
- **Q:** Were all Improvements section of the appraisal requirements met?
- **Defect condition:** Special energy saving items not noted on energy efficient property
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4190
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Special energy saving items not noted on energy efficient property'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-05 — Improvements Section of the Appraisal Report (PDF p.580)
- **Guide candidate:** B2-3-02 — Special Property Eligibility and Underwriting Considerations: Factory-Built Housing (PDF p.261)
- **Guide candidate:** B2-3-03 — Special Property Eligibility and Underwriting Considerations: Leasehold Estates (PDF p.268)
- **SME:** [ ] agree [ ] correct: ______

### G137 — O-FNM-50290 [O-FNM]
- **Q:** Were all Improvements section of the appraisal requirements met?
- **Defect condition:** The impact &/or commentary of an unpermitted addition was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4185
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The impact &/or commentary of an unpermitted addition was not provided'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-05 — Improvements Section of the Appraisal Report (PDF p.580)
- **Guide candidate:** B4-1.3-03 — Neighborhood Section of the Appraisal Report (PDF p.572)
- **Guide candidate:** B4-1.3-04 — Site Section of the Appraisal Report (PDF p.577)
- **SME:** [ ] agree [ ] correct: ______

### G138 — O-FNM-58599 [O-FNM]
- **Q:** Were all Improvements section of the appraisal requirements met?
- **Defect condition:** Unique property w/out recent similar comps, sound adj for differences, or demonstrated marketability
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4674
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('marketability') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Unique property w/out recent similar comps, sound adj for differences, or demonstrated marketability'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-05 — Improvements Section of the Appraisal Report (PDF p.580)
- **Guide candidate:** B4-1.3-03 — Neighborhood Section of the Appraisal Report (PDF p.572)
- **Guide candidate:** B4-1.3-04 — Site Section of the Appraisal Report (PDF p.577)
- **SME:** [ ] agree [ ] correct: ______

### G139 — O-VA-50801 [O-VA]
- **Q:** Were all Lender Appraisal Processing Program (LAPP) requirements met?
- **Defect condition:** Due diligence not exercised in the processing/uw of the subject LAPP case as per VA
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4391
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Due diligence not exercised in the processing/uw of the subject LAPP case as per VA'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G140 — O-VA-00472 [O-VA]
- **Q:** Were all Lender Appraisal Processing Program (LAPP) requirements met?
- **Defect condition:** LAPP used in an entity owned by or has financial interest in or is affiliated with the lender
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4478
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'LAPP used in an entity owned by or has financial interest in or is affiliated with the lender'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G143 — O-FNM-50279 [O-FNM]
- **Q:** Were all Neighborhood section of the appraisal requirements met?_x000D_
- **Defect condition:** Age range & predominant age of the properties in the neighborhood not provided by the appraiser
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4213
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Age range & predominant age of the properties in the neighborhood not provided by the appraiser'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-03 — Neighborhood Section of the Appraisal Report (PDF p.572)
- **Guide candidate:** B4-1.2-04 — Appraisal Age and Use Requirements (PDF p.559)
- **Guide candidate:** B4-1.3-04 — Site Section of the Appraisal Report (PDF p.577)
- **SME:** [ ] agree [ ] correct: ______

### G144 — O-FNM-50276 [O-FNM]
- **Q:** Were all Neighborhood section of the appraisal requirements met?_x000D_
- **Defect condition:** Available land/degree of development, zoning/present land use not reported ensuring residential area
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4207
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Available land/degree of development, zoning/present land use not reported ensuring residential area'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-03 — Neighborhood Section of the Appraisal Report (PDF p.572)
- **Guide candidate:** B4-1.2-04 — Appraisal Age and Use Requirements (PDF p.559)
- **Guide candidate:** B4-1.3-04 — Site Section of the Appraisal Report (PDF p.577)
- **SME:** [ ] agree [ ] correct: ______

### G145 — O-FNM-59374 [O-FNM]
- **Q:** Were all Neighborhood section of the appraisal requirements met?_x000D_
- **Defect condition:** Indicators of market conditions including trend of values, supply & marketing time not reported
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4665
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Indicators of market conditions including trend of values, supply & marketing time not reported'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-03 — Neighborhood Section of the Appraisal Report (PDF p.572)
- **Guide candidate:** B4-1.3-04 — Site Section of the Appraisal Report (PDF p.577)
- **Guide candidate:** B4-1.3-05 — Improvements Section of the Appraisal Report (PDF p.580)
- **SME:** [ ] agree [ ] correct: ______

### G146 — O-FNM-50275 [O-FNM]
- **Q:** Were all Neighborhood section of the appraisal requirements met?_x000D_
- **Defect condition:** Neighborhood boundaries, characteristics & marketability factors not reported on the appraisal
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4209
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('marketability') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Neighborhood boundaries, characteristics & marketability factors not reported on the appraisal'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-03 — Neighborhood Section of the Appraisal Report (PDF p.572)
- **Guide candidate:** B4-1.3-04 — Site Section of the Appraisal Report (PDF p.577)
- **Guide candidate:** B4-1.3-05 — Improvements Section of the Appraisal Report (PDF p.580)
- **SME:** [ ] agree [ ] correct: ______

### G147 — O-FNM-50277 [O-FNM]
- **Q:** Were all Neighborhood section of the appraisal requirements met?_x000D_
- **Defect condition:** Price range/predominant price & area high/low prevailing price of same property type not reported
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4215
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Price range/predominant price & area high/low prevailing price of same property type not reported'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-03 — Neighborhood Section of the Appraisal Report (PDF p.572)
- **Guide candidate:** B4-1.3-04 — Site Section of the Appraisal Report (PDF p.577)
- **Guide candidate:** B4-1.3-05 — Improvements Section of the Appraisal Report (PDF p.580)
- **SME:** [ ] agree [ ] correct: ______

### G148 — O-FNM-50278 [O-FNM]
- **Q:** Were all Neighborhood section of the appraisal requirements met?_x000D_
- **Defect condition:** Subject appears to be an over-improvement &/or is not in the comps adjustment grid without comment
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4211
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('appears') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Subject appears to be an over-improvement &/or is not in the comps adjustment grid without comment'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-03 — Neighborhood Section of the Appraisal Report (PDF p.572)
- **Guide candidate:** B4-1.3-02 — Subject and Contract Sections of the Appraisal Report (PDF p.570)
- **Guide candidate:** B4-1.3-04 — Site Section of the Appraisal Report (PDF p.577)
- **SME:** [ ] agree [ ] correct: ______

### G149 — O-FNM-52895 [O-FNM]
- **Q:** Were all Neighborhood section of the appraisal requirements met?_x000D_
- **Defect condition:** The predominant age and predominant price were not given in whole numbers
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4555
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The predominant age and predominant price were not given in whole numbers'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-03 — Neighborhood Section of the Appraisal Report (PDF p.572)
- **Guide candidate:** B4-1.2-04 — Appraisal Age and Use Requirements (PDF p.559)
- **Guide candidate:** B4-1.3-04 — Site Section of the Appraisal Report (PDF p.577)
- **SME:** [ ] agree [ ] correct: ______

### G152 — O-VA-00638 [O-VA]
- **Q:** Were all Notice of Value (NOV) requirements met?
- **Defect condition:** Appraisal incomplete, unclear &/or not prepared as per industry accepted techniques/VA instructions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4182
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Appraisal incomplete, unclear &/or not prepared as per industry accepted techniques/VA instructions'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G155 — O-VA-00471 [O-VA]
- **Q:** Were all Notice of Value (NOV) requirements met?
- **Defect condition:** LAPP eligible property not processed under LAPP & NOV request did not include a detailed explanation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4477
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'LAPP eligible property not processed under LAPP & NOV request did not include a detailed explanation'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G156 — O-VA-51734 [O-VA]
- **Q:** Were all Notice of Value (NOV) requirements met?
- **Defect condition:** Lender overlays, items that are not required by VA, were included on the NOV
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4499
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Lender overlays, items that are not required by VA, were included on the NOV'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G157 — O-VA-00492 [O-VA]
- **Q:** Were all Notice of Value (NOV) requirements met?
- **Defect condition:** Letter of reasonable value & appraisal copy not provided within 5 business days of appraisal receipt
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4538
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('reasonable') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Letter of reasonable value & appraisal copy not provided within 5 business days of appraisal receipt'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G158 — O-VA-00557 [O-VA]
- **Q:** Were all Notice of Value (NOV) requirements met?
- **Defect condition:** No, the Notice of Value was no longer valid as of the date of closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4680
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'No, the Notice of Value was no longer valid as of the date of closing'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G159 — O-VA-58293 [O-VA]
- **Q:** Were all Notice of Value (NOV) requirements met?
- **Defect condition:** Repairs needed to meet VA's MPR as listed on the NOV were satisfactorily completed not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4516
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: "Repairs needed to meet VA's MPR as listed on the NOV were satisfactorily completed not documented"
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G160 — O-VA-00486 [O-VA]
- **Q:** Were all Notice of Value (NOV) requirements met?
- **Defect condition:** The appraisal was no longer valid as of the disbursement date without an updated or new appraisal
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4135
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The appraisal was no longer valid as of the disbursement date without an updated or new appraisal'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G161 — O-VA-00639 [O-VA]
- **Q:** Were all Notice of Value (NOV) requirements met?
- **Defect condition:** The appraiser methodology was not appropriate, consistent, sound, supportable or logical
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4202
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('appropriate') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'The appraiser methodology was not appropriate, consistent, sound, supportable or logical'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G165 — O-FNM-50293 [O-FNM]
- **Q:** Were all Sales Comparison Approach section of the appraisal requirements met?_x000D_
- **Defect condition:** The specific data and verification source for each comparable not given
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4236
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The specific data and verification source for each comparable not given'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-07 — Sales Comparison Approach Section of the Appraisal Report (PDF p.595)
- **Guide candidate:** B4-1.1-06 — Uniform Appraisal Dataset (UAD) and the Uniform Collateral Data Portal (UCDP) (PDF p.545)
- **Guide candidate:** B4-1.3-03 — Neighborhood Section of the Appraisal Report (PDF p.572)
- **SME:** [ ] agree [ ] correct: ______

### G166 — O-FNM-51474 [O-FNM]
- **Q:** Were all Site sections of the appraisal requirements met?_x000D_
- **Defect condition:** An encroachment was identified on the subject or neighboring property without an easement
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4580
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'An encroachment was identified on the subject or neighboring property without an easement'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-02 — Subject and Contract Sections of the Appraisal Report (PDF p.570)
- **Guide candidate:** B3-6-03 — Monthly Housing Expense for the Subject Property (PDF p.518)
- **Guide candidate:** B4-1.3-04 — Site Section of the Appraisal Report (PDF p.577)
- **SME:** [ ] agree [ ] correct: ______

### G167 — O-FNM-50283 [O-FNM]
- **Q:** Were all Site sections of the appraisal requirements met?_x000D_
- **Defect condition:** Legally enforceable maintenance agreement/covenant of community or private owned street as required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4280
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Legally enforceable maintenance agreement/covenant of community or private owned street as required'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-02 — Subject and Contract Sections of the Appraisal Report (PDF p.570)
- **Guide candidate:** B4-1.3-04 — Site Section of the Appraisal Report (PDF p.577)
- **Guide candidate:** B4-1.4-06 — Community Land Trust Appraisal Requirements (PDF p.623)
- **SME:** [ ] agree [ ] correct: ______

### G168 — O-FNM-54817 [O-FNM]
- **Q:** Were all Site sections of the appraisal requirements met?_x000D_
- **Defect condition:** No comment on adverse conds affecting the subject &/or adj properties impact to value/marketability
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4132
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('No comment') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'No comment on adverse conds affecting the subject &/or adj properties impact to value/marketability'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-02 — Subject and Contract Sections of the Appraisal Report (PDF p.570)
- **Guide candidate:** B4-1.3-04 — Site Section of the Appraisal Report (PDF p.577)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **SME:** [ ] agree [ ] correct: ______

### G170 — O-FNM-50281 [O-FNM]
- **Q:** Were all Site sections of the appraisal requirements met?_x000D_
- **Defect condition:** Specific zoning class & a general statement to what the zoning permits not reported in the appraisal
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4243
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Specific zoning class & a general statement to what the zoning permits not reported in the appraisal'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-02 — Subject and Contract Sections of the Appraisal Report (PDF p.570)
- **Guide candidate:** B4-1.3-04 — Site Section of the Appraisal Report (PDF p.577)
- **Guide candidate:** B2-2-01 — General Borrower Eligibility Requirements (PDF p.241)
- **SME:** [ ] agree [ ] correct: ______

### G171 — O-FNM-50282 [O-FNM]
- **Q:** Were all Site sections of the appraisal requirements met?_x000D_
- **Defect condition:** The subject improvements are not considered the highest and best use of the site
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4445
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('highest and best use') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'The subject improvements are not considered the highest and best use of the site'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-02 — Subject and Contract Sections of the Appraisal Report (PDF p.570)
- **Guide candidate:** B4-1.2-04 — Appraisal Age and Use Requirements (PDF p.559)
- **Guide candidate:** B4-1.3-04 — Site Section of the Appraisal Report (PDF p.577)
- **SME:** [ ] agree [ ] correct: ______

### G172 — O-FNM-53023 [O-FNM]
- **Q:** Were all Subject and Contract sections of the appraisal requirements met?
- **Defect condition:** Appraisal did not note of monetary and non-monetary items paid by any party on behalf of the borr
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4334
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('did not indicate if') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Appraisal did not note of monetary and non-monetary items paid by any party on behalf of the borr'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-02 — Subject and Contract Sections of the Appraisal Report (PDF p.570)
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **Guide candidate:** A2-3.1-01 — Lender Breach of Contract (PDF p.56)
- **SME:** [ ] agree [ ] correct: ______

### G173 — O-FNM-50274 [O-FNM]
- **Q:** Were all Subject and Contract sections of the appraisal requirements met?
- **Defect condition:** Contract not analyzed &/or analysis not provided in the contract section of the appraisal
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4164
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('not analyzed') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Contract not analyzed &/or analysis not provided in the contract section of the appraisal'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-02 — Subject and Contract Sections of the Appraisal Report (PDF p.570)
- **Guide candidate:** B4-1.3-03 — Neighborhood Section of the Appraisal Report (PDF p.572)
- **Guide candidate:** B4-1.3-04 — Site Section of the Appraisal Report (PDF p.577)
- **SME:** [ ] agree [ ] correct: ______

### G174 — O-FNM-53020 [O-FNM]
- **Q:** Were all Subject and Contract sections of the appraisal requirements met?
- **Defect condition:** Contract price in the contract section did not match the contract/sales comparison approach section
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4169
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Contract price in the contract section did not match the contract/sales comparison approach section'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-07 — Sales Comparison Approach Section of the Appraisal Report (PDF p.595)
- **Guide candidate:** B4-1.3-02 — Subject and Contract Sections of the Appraisal Report (PDF p.570)
- **Guide candidate:** B4-1.3-03 — Neighborhood Section of the Appraisal Report (PDF p.572)
- **SME:** [ ] agree [ ] correct: ______

### G176 — O-FNM-53021 [O-FNM]
- **Q:** Were all Subject and Contract sections of the appraisal requirements met?
- **Defect condition:** The appraiser did not enter the contract date for the subject purchase transaction
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4162
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The appraiser did not enter the contract date for the subject purchase transaction'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-02 — Subject and Contract Sections of the Appraisal Report (PDF p.570)
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **Guide candidate:** A2-1-02 — Nature of Mortgage Transaction (PDF p.25)
- **SME:** [ ] agree [ ] correct: ______

### G177 — O-FNM-53022 [O-FNM]
- **Q:** Were all Subject and Contract sections of the appraisal requirements met?
- **Defect condition:** The appraiser did not indicate if the property seller is the owner of record
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4166
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('did not indicate if') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'The appraiser did not indicate if the property seller is the owner of record'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-02 — Subject and Contract Sections of the Appraisal Report (PDF p.570)
- **Guide candidate:** B3-6-03 — Monthly Housing Expense for the Subject Property (PDF p.518)
- **Guide candidate:** B4-1.4-07 — Mixed-Use Property Appraisal Requirements (PDF p.626)
- **SME:** [ ] agree [ ] correct: ______

### G180 — O-RHS-50579 [O-RHS]
- **Q:** Were all additional appraisal report requirements met?
- **Defect condition:** Appraisal update report was provided, however, all req's not met to extend the validity period
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4251
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: "Appraisal update report was provided, however, all req's not met to extend the validity period"
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G181 — O-RHS-50580 [O-RHS]
- **Q:** Were all additional appraisal report requirements met?
- **Defect condition:** Current value is significantly higher than prior sales & no extra steps taken to support the value
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4582
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Current value is significantly higher than prior sales & no extra steps taken to support the value'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G182 — O-RHS-50581 [O-RHS]
- **Q:** Were all additional appraisal report requirements met?
- **Defect condition:** Sales comparison approach not used without comment for rural, Tribal, or low market subject area
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4605
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('without comment') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Sales comparison approach not used without comment for rural, Tribal, or low market subject area'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G183 — O-RHS-50576 [O-RHS]
- **Q:** Were all additional appraisal report requirements met?
- **Defect condition:** The appraisal is not on the correct form for the property type being appraised
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4181
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The appraisal is not on the correct form for the property type being appraised'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G186 — O-FHA-51757 [O-FHA]
- **Q:** Were all additional appraisal requirements met?
- **Defect condition:** Appraiser included business value, personal property or business fixtures in the mixed-use appraisal
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4513
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Appraiser included business value, personal property or business fixtures in the mixed-use appraisal'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G187 — O-FHA-56986 [O-FHA]
- **Q:** Were all additional appraisal requirements met?
- **Defect condition:** FHA and the Mortgagee are not listed as the intended users of the appraisal report
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4415
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'FHA and the Mortgagee are not listed as the intended users of the appraisal report'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G188 — O-FHA-51756 [O-FHA]
- **Q:** Were all additional appraisal requirements met?
- **Defect condition:** No appraiser stmt of insurability if insurable, insurable w/ repair or uninsurable < or > $10,000
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4265
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'No appraiser stmt of insurability if insurable, insurable w/ repair or uninsurable < or > $10,000'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G189 — O-FHA-00442 [O-FHA]
- **Q:** Were all additional appraisal requirements met?
- **Defect condition:** The appraisal was not reported on the URAR or other appropriate form
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4108
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('appropriate') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'The appraisal was not reported on the URAR or other appropriate form'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G191 — O-FHA-50667 [O-FHA]
- **Q:** Were all additional appraisal underwriting requirements met?
- **Defect condition:** Appraisal did not report 12 mo sale history to ensure no undisclosed identity-of-interest trans
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4103
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('not analyzed') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Appraisal did not report 12 mo sale history to ensure no undisclosed identity-of-interest trans'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G192 — O-FHA-00590 [O-FHA]
- **Q:** Were all additional appraisal underwriting requirements met?
- **Defect condition:** Appraised value used to determine the loan amount is inaccurate and is not adequately supported
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4229
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('not adequately') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Appraised value used to determine the loan amount is inaccurate and is not adequately supported'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G193 — O-FHA-50668 [O-FHA]
- **Q:** Were all additional appraisal underwriting requirements met?
- **Defect condition:** Completion of addt'l inspects/repair/certs noted to meet Property Acceptability Criteria not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4476
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: "Completion of addt'l inspects/repair/certs noted to meet Property Acceptability Criteria not in file"
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G201 — O-VA-00555 [O-VA]
- **Q:** Were all additional general appraisal requirements met?
- **Defect condition:** Loan approved with property in area of the Coastal Barrier Resource System
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4279
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Loan approved with property in area of the Coastal Barrier Resource System'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G208 — O-FNM-58732 [O-FNM]
- **Q:** Were all additional leasehold estate appraisal requirements met?
- **Defect condition:** Appraiser did not comment on effects the lease agreement/ground lease has on value & marketability
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4489
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('did not comment') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Appraiser did not comment on effects the lease agreement/ground lease has on value & marketability'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-05 — Leasehold Interests Appraisal Requirements (PDF p.622)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **Guide candidate:** B2-1.2-01 — Loan-to-Value (LTV) Ratios (PDF p.179)
- **SME:** [ ] agree [ ] correct: ______

### G211 — O-FNM-58733 [O-FNM]
- **Q:** Were all additional leasehold estate appraisal requirements met?
- **Defect condition:** New leasehold on or after 9/1/2025, subject to prior liens & no agreement to not disturb the lease
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4524
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('appropriate') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'New leasehold on or after 9/1/2025, subject to prior liens & no agreement to not disturb the lease'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-02 — Subject and Contract Sections of the Appraisal Report (PDF p.570)
- **Guide candidate:** B4-1.4-05 — Leasehold Interests Appraisal Requirements (PDF p.622)
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **SME:** [ ] agree [ ] correct: ______

### G213 — O-VA-58011 [O-VA]
- **Q:** Were all additional minimum property requirements met?_x000D_
- **Defect condition:** Appraiser did not provide a market analysis of solar, high-energy, geothermal & wind-powered equipt
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4141
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Appraiser did not provide a market analysis of solar, high-energy, geothermal & wind-powered equipt'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G214 — O-VA-58009 [O-VA]
- **Q:** Were all additional minimum property requirements met?_x000D_
- **Defect condition:** Completion of repairs involving defective lead-based paint not certified by VA-assigned appraiser
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4481
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Completion of repairs involving defective lead-based paint not certified by VA-assigned appraiser'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G215 — O-VA-58006 [O-VA]
- **Q:** Were all additional minimum property requirements met?_x000D_
- **Defect condition:** Dwelling/improv in 1978 or later, appraiser did not report exterior defective paint & require repair
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4480
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Dwelling/improv in 1978 or later, appraiser did not report exterior defective paint & require repair'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G216 — O-VA-58007 [O-VA]
- **Q:** Were all additional minimum property requirements met?_x000D_
- **Defect condition:** Dwelling/improvements before 1978 and the appraiser did not identify the location of defective paint
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4479
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Dwelling/improvements before 1978 and the appraiser did not identify the location of defective paint'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G217 — O-VA-58008 [O-VA]
- **Q:** Were all additional minimum property requirements met?_x000D_
- **Defect condition:** Evidence defective lead-based paint rec'd adequate treatment to prevent ingestion not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4482
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: "Evidence defective lead-based paint rec'd adequate treatment to prevent ingestion not in the file"
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G218 — O-VA-58012 [O-VA]
- **Q:** Were all additional minimum property requirements met?_x000D_
- **Defect condition:** Leased alternative energy equipment was given value in the appraisal
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4142
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Leased alternative energy equipment was given value in the appraisal'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G220 — O-FHA-50646 [O-FHA]
- **Q:** Were all additional specific appraisal requirements met?
- **Defect condition:** A second appraisal was ordered, and the loan file did not contain the original appraisal report
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4628
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'A second appraisal was ordered, and the loan file did not contain the original appraisal report'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G221 — O-FHA-57260 [O-FHA]
- **Q:** Were all additional specific appraisal requirements met?
- **Defect condition:** Appraiser did not include sufficient eligible comparable rents for a credible ADU market estimate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4118
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('credible') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Appraiser did not include sufficient eligible comparable rents for a credible ADU market estimate'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G223 — O-FHA-57259 [O-FHA]
- **Q:** Were all additional specific appraisal requirements met?
- **Defect condition:** Highest & best use analysis show the subject has an ADU & appraiser didn't provide req'd addt'l info
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4124
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('highest and best use') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: "Highest & best use analysis show the subject has an ADU & appraiser didn't provide req'd addt'l info"
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G225 — O-FHA-56220 [O-FHA]
- **Q:** Were all additional specific appraisal requirements met?
- **Defect condition:** The community water system does not comply with local jurisdiction requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4282
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The community water system does not comply with local jurisdiction requirements'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G226 — O-FHA-57258 [O-FHA]
- **Q:** Were all additional specific appraisal requirements met?
- **Defect condition:** The subject has an accessory dwelling unit that did not meet all eligibility requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4110
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The subject has an accessory dwelling unit that did not meet all eligibility requirements'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G227 — O-FHA-57796 [O-FHA]
- **Q:** Were all additional valuation, reporting, and fair lending appraisal protocol requirements met?_x000D_
- **Defect condition:** All documentation & communications related to the initiation & outcome of the ROV not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4600
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'All documentation & communications related to the initiation & outcome of the ROV not in the file'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G233 — O-FHA-50644 [O-FHA]
- **Q:** Were all appraisal effective date requirements met?
- **Defect condition:** A transferred appraisal was used without all requirements being met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4664
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'A transferred appraisal was used without all requirements being met'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G234 — O-FHA-56211 [O-FHA]
- **Q:** Were all appraisal effective date requirements met?
- **Defect condition:** An appraisal update was ordered and used without meeting all appraisal update use requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4255
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'An appraisal update was ordered and used without meeting all appraisal update use requirements'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G235 — O-FHA-50643 [O-FHA]
- **Q:** Were all appraisal effective date requirements met?
- **Defect condition:** Eff appraisal date prior to case# assignment date w/out lender cert in the Appraisal Logging Screen
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4392
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Eff appraisal date prior to case# assignment date w/out lender cert in the Appraisal Logging Screen'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G238 — O-FRD-57135 [O-FRD]
- **Q:** Were all appraisal exhibit and addenda requirements met?
- **Defect condition:** ANSI Standard current as of appraisal date not used in measuring/calculating/reporting if applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4153
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'ANSI Standard current as of appraisal date not used in measuring/calculating/reporting if applicable'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G242 — O-FHA-00462 [O-FHA]
- **Q:** Were all appraisal ordering requirements met?
- **Defect condition:** An appraisal completed under another case# was re-used in a transaction with a new case#
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4536
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'An appraisal completed under another case# was re-used in a transaction with a new case#'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G243 — O-FHA-00592 [O-FHA]
- **Q:** Were all appraisal ordering requirements met?
- **Defect condition:** Appraiser did not provide commentary or sufficient description on dissimilar comps &/or adjustments
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4618
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Appraiser did not provide commentary or sufficient description on dissimilar comps &/or adjustments'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G244 — O-FHA-00447 [O-FHA]
- **Q:** Were all appraisal ordering requirements met?
- **Defect condition:** Appraiser not provided FHA case#, sales contract, PACE, related legal documents &/or known hazards
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4472
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Appraiser not provided FHA case#, sales contract, PACE, related legal documents &/or known hazards'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G245 — O-FHA-51271 [O-FHA]
- **Q:** Were all appraisal ordering requirements met?
- **Defect condition:** Appraiser was not notified the PACE obligation will be paid off &/or this was not an UW condition
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4549
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Appraiser was not notified the PACE obligation will be paid off &/or this was not an UW condition'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G246 — O-FHA-00445 [O-FHA]
- **Q:** Were all appraisal ordering requirements met?
- **Defect condition:** Fees/charges for the AMC and/or appraiser did not comply with HUD requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4201
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('reasonable') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Fees/charges for the AMC and/or appraiser did not comply with HUD requirements'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G249 — O-FHA-59118 [O-FHA]
- **Q:** Were all appraisal property acceptability criteria requirements met?
- **Defect condition:** Appraiser was not provided all relevant data when the underwriter requested reconsideration of value
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4670
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Appraiser was not provided all relevant data when the underwriter requested reconsideration of value'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G250 — O-FHA-59119 [O-FHA]
- **Q:** Were all appraisal property acceptability criteria requirements met?
- **Defect condition:** Borr was charged for reconsideration of value, despite not being responsible for unavailable data
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4275
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Borr was charged for reconsideration of value, despite not being responsible for unavailable data'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G251 — O-FHA-00455 [O-FHA]
- **Q:** Were all appraisal property acceptability criteria requirements met?
- **Defect condition:** Noncompliance of MPR or MPS without appraiser comment or cost to cure for the property to comply
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4451
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('without comment') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Noncompliance of MPR or MPS without appraiser comment or cost to cure for the property to comply'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G254 — O-FNM-50878 [O-FNM]
- **Q:** Were all appraisal report form, age, and use requirements met?
- **Defect condition:** A 2nd appraisal obtained w/out basis deficiencies noted &/or most reliable appraisal not used
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4625
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'A 2nd appraisal obtained w/out basis deficiencies noted &/or most reliable appraisal not used'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.2-04 — Appraisal Age and Use Requirements (PDF p.559)
- **Guide candidate:** B4-1.2-01 — Appraisal Report Forms and Exhibits (PDF p.547)
- **Guide candidate:** B4-1.3-01 — Review of the Appraisal Report (PDF p.569)
- **SME:** [ ] agree [ ] correct: ______

### G259 — O-FNM-54356 [O-FNM]
- **Q:** Were all appraisal report form, age, and use requirements met?
- **Defect condition:** Appraiser certification &/or statement of assumptions & limiting conditions conflict w/ FNMA policy
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4257
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Appraiser certification &/or statement of assumptions & limiting conditions conflict w/ FNMA policy'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.2-04 — Appraisal Age and Use Requirements (PDF p.559)
- **Guide candidate:** B4-1.2-01 — Appraisal Report Forms and Exhibits (PDF p.547)
- **Guide candidate:** B4-1.3-01 — Review of the Appraisal Report (PDF p.569)
- **SME:** [ ] agree [ ] correct: ______

### G264 — O-RHS-02686 [O-RHS]
- **Q:** Were all appraisal report requirements met?
- **Defect condition:** An appraisal update was obtained for an unallowable purpose and not to extend the validity period
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4669
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'An appraisal update was obtained for an unallowable purpose and not to extend the validity period'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G265 — O-RHS-02683 [O-RHS]
- **Q:** Were all appraisal report requirements met?
- **Defect condition:** Appraisal does not use the market/sales comparison approach to arrive at the value of the property
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4266
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Appraisal does not use the market/sales comparison approach to arrive at the value of the property'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G266 — O-RHS-02682 [O-RHS]
- **Q:** Were all appraisal report requirements met?
- **Defect condition:** Appraisal is not reported on the uniform residential appraisal report form or other appropriate form
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4226
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('appropriate') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Appraisal is not reported on the uniform residential appraisal report form or other appropriate form'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G269 — O-RHS-02684 [O-RHS]
- **Q:** Were all appraisal report requirements met?
- **Defect condition:** Photographs are not clear and descriptive to identify the property’s condition and quality
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4220
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Photographs are not clear and descriptive to identify the property’s condition and quality'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G271 — O-RHS-57525 [O-RHS]
- **Q:** Were all appraisal report requirements met?
- **Defect condition:** The interior and exterior appraisal report did not include all required photographs
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4607
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The interior and exterior appraisal report did not include all required photographs'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G272 — O-RHS-02687 [O-RHS]
- **Q:** Were all appraisal report requirements met?
- **Defect condition:** Value not strongly supported or evidence of property flips due to large increases of recent sales
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4581
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Value not strongly supported or evidence of property flips due to large increases of recent sales'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G274 — O-FHA-51722 [O-FHA]
- **Q:** Were all appraisal underwriting requirements met?
- **Defect condition:** A Water Purification Equipment Rider is not in the file and a water purification system is required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4697
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'A Water Purification Equipment Rider is not in the file and a water purification system is required'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G275 — O-FHA-50666 [O-FHA]
- **Q:** Were all appraisal underwriting requirements met?
- **Defect condition:** All on-site sewage system/septic tank requirements not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4629
- **Severity:** Major
- **Stays human:** bare 'all on-site sewage system/septic tank requirements not met' catch-all
- **Rationale:** Topically near WellSepticShape but stated as a bare, unenumerated catch-all with no single fact named — needs SME decomposition before any automation, same pattern as application-verification's VA-disclosure catch-all.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G276 — O-FHA-50665 [O-FHA]
- **Q:** Were all appraisal underwriting requirements met?
- **Defect condition:** All subject well requirements not met for an individual water supply system
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4463
- **Severity:** Major
- **Stays human:** bare 'all subject well requirements not met' catch-all
- **Rationale:** Same bare-catch-all pattern as G275 (well, not septic, variant).
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G280 — O-FHA-54087 [O-FHA]
- **Q:** Were all appraisal underwriting requirements met?
- **Defect condition:** Subject is within a runway clear zone and a written acknowledgment from the borrower not obtained
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4140
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Subject is within a runway clear zone and a written acknowledgment from the borrower not obtained'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G285 — O-FNM-51044 [O-FNM]
- **Q:** Were all appraiser selection criteria and information disclosure requirements met?
- **Defect condition:** Appraisal completed by trainee, unlicensed/uncertified appraiser w/out supervisory appraiser signing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4660
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Appraisal completed by trainee, unlicensed/uncertified appraiser w/out supervisory appraiser signing'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.1-03 — Appraiser Selection Criteria (PDF p.538)
- **Guide candidate:** B4-1.1-05 — Disclosure of Information to Appraisers (PDF p.543)
- **Guide candidate:** A2-2-02 — Delivery Information and Delivery-Option Speciﬁc Representations and Warranties (PDF p.34)
- **SME:** [ ] agree [ ] correct: ______

### G286 — O-FNM-00523 [O-FNM]
- **Q:** Were all appraiser selection criteria and information disclosure requirements met?
- **Defect condition:** The appraiser's active state license as of the effective date of the appraisal was not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4261
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: "The appraiser's active state license as of the effective date of the appraisal was not documented"
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.1-03 — Appraiser Selection Criteria (PDF p.538)
- **Guide candidate:** B4-1.1-05 — Disclosure of Information to Appraisers (PDF p.543)
- **Guide candidate:** A2-2-02 — Delivery Information and Delivery-Option Speciﬁc Representations and Warranties (PDF p.34)
- **SME:** [ ] agree [ ] correct: ______

### G288 — O-FNM-50311 [O-FNM]
- **Q:** Were all community land trust appraisal requirements met?_x000D_
- **Defect condition:** Ground lease leasehold interest held by community land trust not analyzed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4155
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('not analyzed') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Ground lease leasehold interest held by community land trust not analyzed'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-06 — Community Land Trust Appraisal Requirements (PDF p.623)
- **Guide candidate:** B4-1.4-05 — Leasehold Interests Appraisal Requirements (PDF p.622)
- **Guide candidate:** B4-1.4-09 — Special Assessment or Community Facilities Districts Appraisal Requirements (PDF p.629)
- **SME:** [ ] agree [ ] correct: ______

### G294 — O-RHS-02696 [O-RHS]
- **Q:** Were all condo appraisal requirements met?
- **Defect condition:** Lender certification that the condo project is acceptable to rural development is not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4615
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('acceptable') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Lender certification that the condo project is acceptable to rural development is not in the file'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G310 — O-FNM-55416 [O-FNM]
- **Q:** Were all condo or co-op project deferred maintenance requirements met?
- **Defect condition:** Condo/co-op project missing acceptable COO or failed local regulatory inspections or recertification
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4297
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('acceptable') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Condo/co-op project missing acceptable COO or failed local regulatory inspections or recertification'
- **Classified by:** family_classifier
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **Guide candidate:** B3-3.4-02 — Alimony, Child Support, Equalization Payments, or Separate Maintenance (PDF p.352)
- **Guide candidate:** B4-1.4-03 — Condo Appraisal Requirements (PDF p.618)
- **SME:** [ ] agree [ ] correct: ______

### G313 — O-FNM-55417 [O-FNM]
- **Q:** Were all condo or co-op project deferred maintenance requirements met?
- **Defect condition:** Project reason/term of current or planned special assessments not documented to determine acceptable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4300
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('acceptable') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Project reason/term of current or planned special assessments not documented to determine acceptable'
- **Classified by:** family_classifier
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **Guide candidate:** B2-3-02 — Special Property Eligibility and Underwriting Considerations: Factory-Built Housing (PDF p.261)
- **Guide candidate:** B2-3-03 — Special Property Eligibility and Underwriting Considerations: Leasehold Estates (PDF p.268)
- **SME:** [ ] agree [ ] correct: ______

### G318 — O-FNM-00541 [O-FNM]
- **Q:** Were all condo or co-op ineligible projects appraisal requirements met?
- **Defect condition:** Indicators exist that the individually owned unit condo/co-op project operates as a condotel
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4468
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('indication') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Indicators exist that the individually owned unit condo/co-op project operates as a condotel'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-03 — Condo Appraisal Requirements (PDF p.618)
- **Guide candidate:** B4-2.1-03 — Ineligible Projects (PDF p.652)
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **SME:** [ ] agree [ ] correct: ______

### G338 — O-FNM-50317 [O-FNM]
- **Q:** Were all condo or co-op project review requirements met?
- **Defect condition:** The subject co-op occupancy intent is for investment purposes which is prohibited
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4354
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('prohibited') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'The subject co-op occupancy intent is for investment purposes which is prohibited'
- **Classified by:** family_classifier
- **Guide candidate:** B4-2.1-02 — Waiver of Project Review (PDF p.649)
- **Guide candidate:** B4-2.2-03 — Full Review: Additional Eligibility Requirements for Units in New and Newly Converted Condo Projects (PDF p.684)
- **Guide candidate:** B4-2.2-04 — Geographic-Speciﬁc Condo Project Considerations (PDF p.688)
- **SME:** [ ] agree [ ] correct: ______

### G345 — O-FRD-53865 [O-FRD]
- **Q:** Were all contract, neighborhood, site, and improvement section requirements met?
- **Defect condition:** Missing explanation of market area analysis used to determine the subject is adequate collateral
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4521
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('marketability') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Missing explanation of market area analysis used to determine the subject is adequate collateral'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G346 — O-FRD-53032 [O-FRD]
- **Q:** Were all contract, neighborhood, site, and improvement section requirements met?
- **Defect condition:** No commentary &/or comps to support value or marketability for unusual floor plan obsolescence
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4677
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('No comment') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'No commentary &/or comps to support value or marketability for unusual floor plan obsolescence'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G348 — O-FRD-53926 [O-FRD]
- **Q:** Were all contract, neighborhood, site, and improvement section requirements met?
- **Defect condition:** Overall rating of Q6, C5 or C6 without all reasons for the rating being cured prior to delivery
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4470
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Overall rating of Q6, C5 or C6 without all reasons for the rating being cured prior to delivery'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G349 — O-FRD-58586 [O-FRD]
- **Q:** Were all contract, neighborhood, site, and improvement section requirements met?
- **Defect condition:** Subject nonconforms to its neighborhood in type/design/age/constr without marketability evaluation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4522
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('marketability') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Subject nonconforms to its\xa0neighborhood\xa0in type/design/age/constr without marketability evaluation'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G350 — O-FRD-50488 [O-FRD]
- **Q:** Were all contract, neighborhood, site, and improvement section requirements met?
- **Defect condition:** The comps were older than 12 months without comment by the appraiser
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4137
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('without comment') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'The comps were older than 12 months without comment by the appraiser'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G351 — O-FRD-50482 [O-FRD]
- **Q:** Were all contract, neighborhood, site, and improvement section requirements met?
- **Defect condition:** The contract section of the appraisal not completed or was inaccurate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4335
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The contract section of the appraisal not completed or was inaccurate'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G352 — O-FRD-50487 [O-FRD]
- **Q:** Were all contract, neighborhood, site, and improvement section requirements met?
- **Defect condition:** The improvements section is incomplete/inaccurate or missing factors impacting marketability
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4455
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('marketability') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'The improvements section is incomplete/inaccurate or missing factors impacting marketability'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G353 — O-FRD-50483 [O-FRD]
- **Q:** Were all contract, neighborhood, site, and improvement section requirements met?
- **Defect condition:** The neighborhood boundaries and characteristics etc not completed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4649
- **Severity:** Critical
- **Stays human:** neighborhood-section narrative completeness/accuracy judgment
- **Rationale:** Reclassified from the family classifier's numeric-threshold match (picked up a stray digit from exception_description, not a real threshold in this row's own condition): same 'Section ... not completed/incomplete/inaccurate' narrative-completeness family as G043/G049/G051/G059/G062 (all already RED) — this is the neighborhood-section sibling, no different in kind.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G354 — O-FRD-50484 [O-FRD]
- **Q:** Were all contract, neighborhood, site, and improvement section requirements met?
- **Defect condition:** The site section not fully completed or was incorrect
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4654
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The site section not fully completed or was incorrect'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G355 — O-FRD-50485 [O-FRD]
- **Q:** Were all contract, neighborhood, site, and improvement section requirements met?
- **Defect condition:** The subject property present use not reported as the highest and best use
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4446
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('highest and best use') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'The subject property present use not reported as the highest and best use'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G356 — O-FNM-50299 [O-FNM]
- **Q:** Were all cost and income approach to value requirements met?
- **Defect condition:** Analysis in the cost approach is inconsistent to other areas of the report
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4170
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('inconsistent') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Analysis in the cost approach is inconsistent to other areas of the report'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-10 — Cost and Income Approach to Value (PDF p.604)
- **Guide candidate:** B3-3.4-01 — General Requirements for Other Sources of Income (PDF p.351)
- **Guide candidate:** B3-5.3-09 — DU Credit Report Analysis (PDF p.495)
- **SME:** [ ] agree [ ] correct: ______

### G357 — O-FNM-50300 [O-FNM]
- **Q:** Were all cost and income approach to value requirements met?
- **Defect condition:** Income approach used without supporting comp rental/sales data & gross rent multiplier calculations
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4196
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('without support') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Income approach used without supporting comp rental/sales data & gross rent multiplier calculations'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-10 — Cost and Income Approach to Value (PDF p.604)
- **Guide candidate:** B3-3.8-01 — Rental Income (PDF p.406)
- **Guide candidate:** B4-1.3-07 — Sales Comparison Approach Section of the Appraisal Report (PDF p.595)
- **SME:** [ ] agree [ ] correct: ______

### G365 — O-FNM-50314 [O-FNM]
- **Q:** Were all environmental hazards appraisal requirements met?
- **Defect condition:** Hazardous condition noted without additional commentary
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4172
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('appropriate') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Hazardous condition noted without additional commentary'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-08 — Environmental Hazards Appraisal Requirements (PDF p.627)
- **Guide candidate:** B4-2.1-05 — Unacceptable Environmental Hazards (PDF p.668)
- **Guide candidate:** B4-1.1-04 — Unacceptable Appraisal Practices (PDF p.541)
- **SME:** [ ] agree [ ] correct: ______

### G366 — HealthSafe [O-FNM]
- **Q:** Were all environmental hazards appraisal requirements met?
- **Defect condition:** Health & safety issues have been identified without being addressed and/or corrected
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4444
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('not addressed') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Health & safety issues have been identified without being addressed and/or corrected'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-08 — Environmental Hazards Appraisal Requirements (PDF p.627)
- **Guide candidate:** B4-2.1-05 — Unacceptable Environmental Hazards (PDF p.668)
- **Guide candidate:** B4-1.1-04 — Unacceptable Appraisal Practices (PDF p.541)
- **SME:** [ ] agree [ ] correct: ______

### G367 — O-FNM-00540 [O-FNM]
- **Q:** Were all environmental hazards appraisal requirements met?
- **Defect condition:** Known environment hazard not disclosed to the borr & addt'l inspections not conducted as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4173
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('appropriate') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: "Known environment hazard not disclosed to the borr & addt'l inspections not conducted as applicable"
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-08 — Environmental Hazards Appraisal Requirements (PDF p.627)
- **Guide candidate:** B4-2.1-04 — Environmental Hazard Assessments (PDF p.665)
- **Guide candidate:** B4-2.1-05 — Unacceptable Environmental Hazards (PDF p.668)
- **SME:** [ ] agree [ ] correct: ______

### G369 — O-RHS-02693 [O-RHS]
- **Q:** Were all environmental hazards appraisal requirements met?
- **Defect condition:** Potential environmental hazard was not mitigated before requesting the loan guarantee
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4398
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Potential environmental hazard was not mitigated before requesting the loan guarantee'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G370 — O-RHS-50587 [O-RHS]
- **Q:** Were all environmental hazards appraisal requirements met?
- **Defect condition:** Subject has known hazards that may have adverse effects on the health & safety of the occupants
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4585
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Subject has known hazards that may have adverse effects on the health & safety of the occupants'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G372 — O-RHS-02690 [O-RHS]
- **Q:** Were all existing dwelling requirements met?
- **Defect condition:** No appraiser cert/report from a qualified home inspector evidencing HUD property standards are met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4450
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'No appraiser cert/report from a qualified home inspector evidencing HUD property standards are met'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G373 — O-RHS-57527 [O-RHS]
- **Q:** Were all existing dwelling requirements met?
- **Defect condition:** No evidence the lender encouraged the applicants to get an independent/detailed home inspection
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4462
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'No evidence the lender encouraged the applicants to get an independent/detailed home inspection'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G376 — O-FRD-51683 [O-FRD]
- **Q:** Were all general appraisal requirements met?
- **Defect condition:** A contaminated site or hazardous substance known by the seller was not disclosed to the borrower
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4333
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'A contaminated site or hazardous substance known by the seller was not disclosed to the borrower'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G377 — O-FRD-00495 [O-FRD]
- **Q:** Were all general appraisal requirements met?
- **Defect condition:** All appraiser independence requirements were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4260
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'All appraiser independence requirements were not met'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G378 — O-FRD-00498 [O-FRD]
- **Q:** Were all general appraisal requirements met?
- **Defect condition:** Appraisal completed by an unlicensed or trainee appraiser without a supervisory appraiser signature
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4675
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Appraisal completed by an unlicensed or trainee appraiser without a supervisory appraiser signature'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G380 — O-VA-50790 [O-VA]
- **Q:** Were all general appraisal requirements met?
- **Defect condition:** Appraisal did not meet all USPAP requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4678
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Appraisal did not meet all USPAP requirements'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G382 — O-FRD-59115 [O-FRD]
- **Q:** Were all general appraisal requirements met?
- **Defect condition:** Appraisal subject to inspection due to a detrimental condition, no evidence of repair/reinspection
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4648
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Appraisal subject to inspection due to a detrimental condition, no evidence of repair/reinspection'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G383 — O-FRD-00512 [O-FRD]
- **Q:** Were all general appraisal requirements met?
- **Defect condition:** Appraiser did not make adjustments to the comps for special/creative financing or sales concessions
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4283
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Appraiser did not make adjustments to the comps for special/creative financing or sales concessions'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G384 — O-FRD-00496 [O-FRD]
- **Q:** Were all general appraisal requirements met?
- **Defect condition:** Appraiser is not state-licensed or state-certified in the state the subject property is located
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4263
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Appraiser is not state-licensed or state-certified in the state the subject property is located'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G386 — O-FRD-00507 [O-FRD]
- **Q:** Were all general appraisal requirements met?
- **Defect condition:** Appraiser not provided information known to likely affect market value/marketability of the property
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4473
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('marketability') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Appraiser not provided information known to likely affect market value/marketability of the property'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G387 — O-VA-51638 [O-VA]
- **Q:** Were all general appraisal requirements met?
- **Defect condition:** COE confirming eligibility not obtained prior to ordering the appraisal and a waiver was not granted
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4543
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'COE confirming eligibility not obtained prior to ordering the appraisal and a waiver was not granted'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G388 — O-FRD-00665 [O-FRD]
- **Q:** Were all general appraisal requirements met?
- **Defect condition:** Detrimental conditions at the property or subject neighborhood not considered in the value estimate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4380
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Detrimental conditions at the property or subject neighborhood not considered in the value estimate'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G389 — O-VA-00469 [O-VA]
- **Q:** Were all general appraisal requirements met?
- **Defect condition:** Property ineligible for appraisal & appraisal request req not cleared prior to ordering an appraisal
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4394
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Property ineligible for appraisal\xa0& appraisal request req not cleared prior to ordering an appraisal'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G390 — O-FRD-59114 [O-FRD]
- **Q:** Were all general appraisal requirements met?
- **Defect condition:** Subject detrimental conditions on report & not made "subject to" inspection for repair determination
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4656
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Subject detrimental conditions on report & not made "subject to" inspection for repair determination'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G392 — O-FRD-00667 [O-FRD]
- **Q:** Were all general appraisal requirements met?
- **Defect condition:** The file does not contain documentation verifying the seller is the owner of record
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4547
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The file does not contain documentation verifying the seller is the owner of record'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G394 — O-FRD-00808 [O-FRD]
- **Q:** Were all general property eligibility requirements met?
- **Defect condition:** A satisfactory escrow was not established at closing for repairs or completion after closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4288
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'A satisfactory escrow was not established at closing for repairs or completion after closing'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G395 — O-FRD-54131 [O-FRD]
- **Q:** Were all general property eligibility requirements met?
- **Defect condition:** Appraisal did not include the owned free & clear solar panels in the value
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4546
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Appraisal did not include the owned free & clear solar panels in the value'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G396 — O-FRD-55107 [O-FRD]
- **Q:** Were all general property eligibility requirements met?
- **Defect condition:** Subject is a group home for individuals with disabilities & residential & occupancy req's not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4442
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: "Subject is a group home for individuals with disabilities & residential & occupancy req's not met"
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G409 — O-FNM-00537 [O-FNM]
- **Q:** Were all lender responsibilities requirements met?
- **Defect condition:** Appraiser comments indicate value may be based on discriminatory assumptions of subject/neighborhood
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4539
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('indicate') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Appraiser comments indicate value may be based on discriminatory assumptions of subject/neighborhood'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.1-02 — Lender Responsibilities (PDF p.535)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **Guide candidate:** A2-3.1-01 — Lender Breach of Contract (PDF p.56)
- **SME:** [ ] agree [ ] correct: ______

### G413 — O-FNM-00703 [O-FNM]
- **Q:** Were all lender responsibilities requirements met?
- **Defect condition:** The file does not contain documentation verifying the property seller is the owner of the property
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4364
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The file does not contain documentation verifying the property seller is the owner of the property'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.1-02 — Lender Responsibilities (PDF p.535)
- **Guide candidate:** D1-3-02 — Lender Post-Closing Quality Control Review of Approval Conditions, Underwriting Decisions, Data, and Documentation (PDF p.1068)
- **Guide candidate:** A1-1-01 — Application and Approval of Seller/Servicer (PDF p.20)
- **SME:** [ ] agree [ ] correct: ______

### G414 — O-FNM-00539 [O-FNM]
- **Q:** Were all lender responsibilities requirements met?
- **Defect condition:** Unfavorable environment or economic factors noted without comment &/or no comps with same condition
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4671
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('without comment') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Unfavorable environment or economic factors noted without comment &/or no comps with same condition'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.1-02 — Lender Responsibilities (PDF p.535)
- **Guide candidate:** A2-3.1-01 — Lender Breach of Contract (PDF p.56)
- **Guide candidate:** B2-2-03 — Multiple Financed Properties for the Same Borrower (PDF p.244)
- **SME:** [ ] agree [ ] correct: ______

### G415 — O-FHA-55572 [O-FHA]
- **Q:** Were all minimum property appraisal requirements met?
- **Defect condition:** Contract section is incomplete or inaccurate &/or did not match sales comparison approach section
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4163
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Contract section is incomplete or inaccurate &/or did not match sales comparison approach section'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G416 — O-FHA-52797 [O-FHA]
- **Q:** Were all minimum property appraisal requirements met?
- **Defect condition:** Subject's private road condition not noted and/or a maintenance agreement not in place
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4557
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: "Subject's private road condition not noted and/or a maintenance agreement not in place"
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G418 — O-FHA-55575 [O-FHA]
- **Q:** Were all minimum property appraisal requirements met?
- **Defect condition:** The information in the improvements section are incomplete and/or inaccurate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4240
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The information in the improvements section are incomplete and/or inaccurate'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G419 — O-FHA-55573 [O-FHA]
- **Q:** Were all minimum property appraisal requirements met?
- **Defect condition:** The information in the neighborhood section is incomplete and/or inaccurate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4217
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The information in the neighborhood section is incomplete and/or inaccurate'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G420 — O-FHA-55574 [O-FHA]
- **Q:** Were all minimum property appraisal requirements met?
- **Defect condition:** The information in the site section is incomplete and/or inaccurate
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4241
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The information in the site section is incomplete and/or inaccurate'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G424 — O-VA-51851 [O-VA]
- **Q:** Were all minimum property requirements met?
- **Defect condition:** Detached site improvement was included that did not meet MPRs &/or posed a health or safety hazard
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4376
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Detached site improvement was included that did not meet MPRs &/or posed a health or safety hazard'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G425 — O-VA-56067 [O-VA]
- **Q:** Were all minimum property requirements met?
- **Defect condition:** No recorded permanent easement or right-of-way to a public road for private road or shared driveway
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4559
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'No recorded permanent easement or right-of-way to a public road for private road or shared driveway'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G428 — O-VA-51853 [O-VA]
- **Q:** Were all minimum property requirements met?
- **Defect condition:** Per appraiser's market knowledge, subject is prone to regular flooding regardless of flood zone
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4464
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: "Per appraiser's market knowledge, subject is prone to regular flooding regardless of flood zone"
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G429 — O-VA-58954 [O-VA]
- **Q:** Were all minimum property requirements met?
- **Defect condition:** Property hazard impacting health/safety, structural soundness or impairs customary use not addressed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4515
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('not addressed') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Property hazard impacting health/safety, structural soundness or impairs customary use not addressed'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G430 — O-VA-51854 [O-VA]
- **Q:** Were all minimum property requirements met?
- **Defect condition:** Radon resistant construction not used in a proposed/new construction located in Radon Zone 1
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4596
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Radon resistant construction not used in a proposed/new construction located in Radon Zone 1'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G433 — O-FNM-50313 [O-FNM]
- **Q:** Were all mixed-use properties appraisal requirements met?
- **Defect condition:** One or more of the requirements for a mixed-use property appraisal was not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4203
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'One or more of the requirements for a mixed-use property appraisal was not met'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-07 — Mixed-Use Property Appraisal Requirements (PDF p.626)
- **Guide candidate:** B7-3-02 — Property Insurance Requirements for One-to Four-Unit Properties (PDF p.875)
- **Guide candidate:** B4-1.2-04 — Appraisal Age and Use Requirements (PDF p.559)
- **SME:** [ ] agree [ ] correct: ______

### G434 — O-FRD-50500 [O-FRD]
- **Q:** Were all mixed-use property requirements met?
- **Defect condition:** Current use of the mixed-use property is not legal & permissible under the local zoning requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4497
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Current use of the mixed-use property is not legal & permissible under the local zoning requirements'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G435 — O-FRD-50501 [O-FRD]
- **Q:** Were all mixed-use property requirements met?
- **Defect condition:** Mixed-use borr not owner of the business &/or business has adverse impact on the habitability/safety
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4510
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Mixed-use borr not owner of the business &/or business has adverse impact on the habitability/safety'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G436 — O-FRD-50498 [O-FRD]
- **Q:** Were all mixed-use property requirements met?
- **Defect condition:** Mixed-use missing commercial use description, residential value, market reaction &/or adjustments
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4511
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Mixed-use missing commercial use description, residential value, market reaction &/or adjustments'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G437 — O-FRD-50499 [O-FRD]
- **Q:** Were all mixed-use property requirements met?
- **Defect condition:** Mixed-use property not a 1 unit primary or neighborhood not primarily residential &/or is atypical
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4512
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Mixed-use property not a 1 unit primary or neighborhood not primarily residential &/or is atypical'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G439 — O-RHS-59183 [O-RHS]
- **Q:** Were all new construction requirements met?
- **Defect condition:** Contruction change orders affect the project scope or appraised value &/or were not lender approved
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4330
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Contruction change orders affect the project scope or appraised value &/or were not lender approved'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G440 — O-RHS-02691 [O-RHS]
- **Q:** Were all new construction requirements met?
- **Defect condition:** New dwelling not designed & constructed as per acceptable certified plans and specification
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4523
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('acceptable') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'New dwelling not designed & constructed as per acceptable certified plans and specification'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G442 — O-RHS-59181 [O-RHS]
- **Q:** Were all new construction requirements met?
- **Defect condition:** One-year builder warranty missing or incomplete: date, owner, warrantor, location, signatures, info
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4541
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'One-year builder warranty missing or incomplete: date, owner, warrantor, location, signatures, info'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G443 — O-RHS-02703 [O-RHS]
- **Q:** Were all new construction requirements met?
- **Defect condition:** Plans & specs do not comply with all development standards applicable for a new construction
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4332
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Plans & specs do not comply with all development standards applicable for a new construction'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G444 — O-RHS-02702 [O-RHS]
- **Q:** Were all new construction requirements met?
- **Defect condition:** The file did not contain evidence of new construction inspections that meet the 3 options RHS allows
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4331
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The file did not contain evidence of new construction inspections that meet the 3 options RHS allows'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G445 — O-RHS-56100 [O-RHS]
- **Q:** Were all new construction requirements met?
- **Defect condition:** The file did not contain plans and specifications, construction inspections, and thermal standards
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4552
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The file did not contain plans and specifications, construction inspections, and thermal standards'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G446 — O-RHS-50574 [O-RHS]
- **Q:** Were all qualified appraiser requirements met?_x000D_
- **Defect condition:** Appraiser not qualified, competent &/or properly licensed or certified in the subject property state
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4591, 4592, 4593
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('appropriate') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Appraiser not qualified, competent &/or properly licensed or certified in the subject property state'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G448 — O-FRD-50494 [O-FRD]
- **Q:** Were all reconciliation, cost approach, and income approach requirements met?_x000D_
- **Defect condition:** An income approach was not provided as required for a 2-4 unit
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4457
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'An income approach was not provided as required for a 2-4 unit'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G449 — O-FRD-00663 [O-FRD]
- **Q:** Were all reconciliation, cost approach, and income approach requirements met?_x000D_
- **Defect condition:** No appraiser commentary on value conclusion or comments were inconsistent with areas of the report
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4256
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('inconsistent') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'No appraiser commentary on value conclusion or comments were inconsistent with areas of the report'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G451 — O-FRD-55782 [O-FRD]
- **Q:** Were all requirements met for a property with an accessory dwelling unit?
- **Defect condition:** Appraiser did not identify & use the appropriate appraisal form for a subject property with an ADU
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4130
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('appropriate') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Appraiser did not identify & use the appropriate appraisal form for a subject property with an\xa0ADU'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G458 — O-FNM-50289 [O-FNM]
- **Q:** Were all requirements met for a property with an accessory dwelling unit?_x000D_
- **Defect condition:** All requirements for a property with an accessory unit not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4183
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'All requirements for a property with an accessory unit not met'
- **Classified by:** family_classifier
- **Guide candidate:** B7-3-02 — Property Insurance Requirements for One-to Four-Unit Properties (PDF p.875)
- **Guide candidate:** B7-3-04 — Individual Property Insurance Requirements for a Unit in a Project Development (PDF p.885)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **SME:** [ ] agree [ ] correct: ______

### G459 — O-FNM-57985 [O-FNM]
- **Q:** Were all requirements met for a property with an accessory dwelling unit?_x000D_
- **Defect condition:** An aged settled sale & an active listing/under contract sale not provided as a supplemental exhibit
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4119
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('marketability') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'An aged settled sale & an active listing/under contract sale not provided as a supplemental exhibit'
- **Classified by:** family_classifier
- **Guide candidate:** B7-3-02 — Property Insurance Requirements for One-to Four-Unit Properties (PDF p.875)
- **Guide candidate:** B7-3-04 — Individual Property Insurance Requirements for a Unit in a Project Development (PDF p.885)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **SME:** [ ] agree [ ] correct: ______

### G460 — O-FNM-57984 [O-FNM]
- **Q:** Were all requirements met for a property with an accessory dwelling unit?_x000D_
- **Defect condition:** Appraisal did not include a description of the ADU & effect on value or marketability of the subject
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4122
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('marketability') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Appraisal did not include a description of the ADU & effect on value or marketability of the subject'
- **Classified by:** family_classifier
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **Guide candidate:** B3-6-03 — Monthly Housing Expense for the Subject Property (PDF p.518)
- **Guide candidate:** B4-1.3-02 — Subject and Contract Sections of the Appraisal Report (PDF p.570)
- **SME:** [ ] agree [ ] correct: ______

### G473 — O-FRD-50492 [O-FRD]
- **Q:** Were all sales comparison approach requirements met?_x000D_
- **Defect condition:** A comp w/ an accessory unit like the subject not provided without comment/support by the appraiser
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4111
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('without comment') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'A comp w/ an accessory unit like the subject not provided without comment/support by the appraiser'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G474 — O-FRD-00662 [O-FRD]
- **Q:** Were all sales comparison approach requirements met?_x000D_
- **Defect condition:** Appraiser's estimate of market value using the sales comparison approach to value is not supported
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4620
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('not supported') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: "Appraiser's estimate of market value using the sales comparison approach to value is not supported"
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G479 — O-FRD-50489 [O-FRD]
- **Q:** Were all sales comparison approach requirements met?_x000D_
- **Defect condition:** The appraiser didn't adjust appropriately for differences in subject & comps
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4284
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('not analyzed') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: "The appraiser didn't adjust appropriately for differences in subject & comps"
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G480 — O-FHA-50645 [O-FHA]
- **Q:** Were all second order appraisal requirements met?_x000D_
- **Defect condition:** 2nd URAR ordered w/out DE UW determining 1st materially deficient or appraiser didn't resolve issue
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4626
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: "2nd URAR ordered w/out DE UW determining 1st materially deficient or appraiser didn't resolve issue"
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G481 — O-FHA-50646 [O-FHA]
- **Q:** Were all second order appraisal requirements met?_x000D_
- **Defect condition:** A second appraisal was ordered, and the loan file did not contain the original appraisal report
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4627
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'A second appraisal was ordered, and the loan file did not contain the original appraisal report'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G482 — O-FHA-57794 [O-FHA]
- **Q:** Were all second order appraisal requirements met?_x000D_
- **Defect condition:** No evidence that the appraisal that was replaced due to material deficiencies was reported
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4506
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'No evidence that the appraisal that was replaced due to material deficiencies was reported'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G484 — O-RHS-51477 [O-RHS]
- **Q:** Were all site requirements met?
- **Defect condition:** An encroachment was identified on the subject or neighboring property without an easement
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4395
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'An encroachment was identified on the subject or neighboring property without an easement'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G486 — O-RHS-02689 [O-RHS]
- **Q:** Were all site requirements met?
- **Defect condition:** No documentation the site is contiguous to/has direct access to a maintained street/road/driveway
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4647
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'No documentation the site is contiguous to/has direct access to a maintained street/road/driveway'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G487 — O-RHS-52816 [O-RHS]
- **Q:** Were all site requirements met?
- **Defect condition:** Solar panels subject to a lease agreement, PPA or similar agreement without meeting all requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4642
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Solar panels subject to a lease agreement, PPA or similar agreement without meeting all requirements'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G488 — O-RHS-50573 [O-RHS]
- **Q:** Were all site requirements met?
- **Defect condition:** Subject appears to have income-producing land or income-producing buildings which are ineligible
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4458
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('appears') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Subject appears to have income-producing land or income-producing buildings which are ineligible'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G489 — O-RHS-02680 [O-RHS]
- **Q:** Were all site requirements met?
- **Defect condition:** Subject site did not meet the size, income production, site specifications &/or utilities req's
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4655
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: "Subject site did not meet the size, income production, site specifications &/or utilities req's"
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G492 — O-RHS-50572 [O-RHS]
- **Q:** Were all site requirements met?
- **Defect condition:** The subject site size was not typical for the area as required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4657
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The subject site size was not typical for the area as required'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G495 — O-FNM-50240 [O-FNM]
- **Q:** Were all special property appraisal requirements met?_x000D_
- **Defect condition:** All requirements for a mixed-use property were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4509
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'All requirements for a mixed-use property were not met'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-07 — Mixed-Use Property Appraisal Requirements (PDF p.626)
- **Guide candidate:** B2-3-02 — Special Property Eligibility and Underwriting Considerations: Factory-Built Housing (PDF p.261)
- **Guide candidate:** B2-3-03 — Special Property Eligibility and Underwriting Considerations: Leasehold Estates (PDF p.268)
- **SME:** [ ] agree [ ] correct: ______

### G496 — O-FNM-50242 [O-FNM]
- **Q:** Were all special property appraisal requirements met?_x000D_
- **Defect condition:** All requirements for non-owned solar panels were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4641
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'All requirements for non-owned solar panels were not met'
- **Classified by:** family_classifier
- **Guide candidate:** B2-3-02 — Special Property Eligibility and Underwriting Considerations: Factory-Built Housing (PDF p.261)
- **Guide candidate:** B2-3-03 — Special Property Eligibility and Underwriting Considerations: Leasehold Estates (PDF p.268)
- **Guide candidate:** B2-3-04 — Special Property Eligibility Considerations (PDF p.274)
- **SME:** [ ] agree [ ] correct: ______

### G497 — O-FNM-57136 [O-FNM]
- **Q:** Were all special property appraisal requirements met?_x000D_
- **Defect condition:** Appraiser did not enter "3D Printed Home" in the description field of the Sales Comp Approach grid
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4106
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Appraiser did not enter "3D Printed Home" in the description field of the Sales Comp Approach grid'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.3-07 — Sales Comparison Approach Section of the Appraisal Report (PDF p.595)
- **Guide candidate:** B2-3-02 — Special Property Eligibility and Underwriting Considerations: Factory-Built Housing (PDF p.261)
- **Guide candidate:** B2-3-03 — Special Property Eligibility and Underwriting Considerations: Leasehold Estates (PDF p.268)
- **SME:** [ ] agree [ ] correct: ______

### G502 — O-FNM-50241 [O-FNM]
- **Q:** Were all special property appraisal requirements met?_x000D_
- **Defect condition:** The subject property is in Hawaiian Lava Zone 1 or 2 which is not eligible for delivery to FNMA
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4443
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The subject property is in Hawaiian Lava Zone 1 or 2 which is not eligible for delivery to FNMA'
- **Classified by:** family_classifier
- **Guide candidate:** B2-3-02 — Special Property Eligibility and Underwriting Considerations: Factory-Built Housing (PDF p.261)
- **Guide candidate:** B2-3-03 — Special Property Eligibility and Underwriting Considerations: Leasehold Estates (PDF p.268)
- **Guide candidate:** B2-3-04 — Special Property Eligibility Considerations (PDF p.274)
- **SME:** [ ] agree [ ] correct: ______

### G504 — O-FHA-52319 [O-FHA]
- **Q:** Were all specific appraisal requirements met?
- **Defect condition:** Appraiser did not comment on the physical condition of the plumbing, heating and electrical systems
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4679
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('did not comment') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Appraiser did not comment on the physical condition of the plumbing, heating and electrical systems'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G505 — O-FHA-52277 [O-FHA]
- **Q:** Were all specific appraisal requirements met?
- **Defect condition:** Appraiser did not observe the crawl space or comment there is a lack of accessibility
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4361
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Appraiser did not observe the crawl space or comment there is a lack of accessibility'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G506 — O-FHA-52276 [O-FHA]
- **Q:** Were all specific appraisal requirements met?
- **Defect condition:** Appraiser did not observe the interior of all attic spaces or comment a lack of accessibility
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4269
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Appraiser did not observe the interior of all attic spaces or comment a lack of accessibility'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G508 — O-FHA-52322 [O-FHA]
- **Q:** Were all specific appraisal requirements met?
- **Defect condition:** Evidence the basement or sump pump were observed for deficiency was not present
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4270
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Evidence the basement or sump pump were observed for deficiency was not present'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G509 — O-FHA-55625 [O-FHA]
- **Q:** Were all specific appraisal requirements met?
- **Defect condition:** Evidence the onsite sewage disposal system was observed for deficiency was not present
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4542
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Evidence the onsite sewage disposal system was observed for deficiency was not present'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G510 — O-FHA-52318 [O-FHA]
- **Q:** Were all specific appraisal requirements met?
- **Defect condition:** No comment of appliances present and operational and/or if considered real or personal property
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4456
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('No comment') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'No comment of appliances present and operational and/or if considered real or personal property'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G511 — O-FHA-52323 [O-FHA]
- **Q:** Were all specific appraisal requirements met?
- **Defect condition:** No commentary given for lead-based paint, methamphetamine contamination &/or wood destroying pests
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4397
- **Severity:** Critical
- **Stays human:** narrative commentary presence/adequacy for lead paint, meth contamination, wood-destroying pests
- **Rationale:** Topically overlaps termite/well/LBP families but the actual condition is 'no commentary given' — a narrative-adequacy judgment on the appraiser's write-up, not a document-presence test. Not a match to any existing shape.
- **Classified by:** hand_override
- **SME:** [ ] agree [ ] correct: ______

### G512 — O-FHA-52320 [O-FHA]
- **Q:** Were all specific appraisal requirements met?
- **Defect condition:** No evidence the roof was observed for health/safety deficiencies or reasonable future utility
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4612
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('reasonable') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'No evidence the roof was observed for health/safety deficiencies or reasonable future utility'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G513 — O-FHA-52321 [O-FHA]
- **Q:** Were all specific appraisal requirements met?
- **Defect condition:** No visual observation/commentary about the foundation & structure of improvements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4440
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'No visual observation/commentary about the foundation & structure of improvements'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G515 — O-FRD-50481 [O-FRD]
- **Q:** Were all subject section requirements met?
- **Defect condition:** Lender/client line blank or if applicable, AMC not reported in the appraiser certification section
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4498
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Lender/client line blank or if applicable, AMC not reported in the appraiser certification section'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G517 — O-FRD-50480 [O-FRD]
- **Q:** Were all subject section requirements met?
- **Defect condition:** The appraiser did not provide subject sale, offer history for last 12mos & data sources used
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4651
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('did not indicate whether') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'The appraiser did not provide subject sale, offer history for last 12mos & data sources used'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G518 — O-FRD-50478 [O-FRD]
- **Q:** Were all subject section requirements met?
- **Defect condition:** The occupancy status of the property not noted as owner, tenant or vacant
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4540
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The occupancy status of the property not noted as owner, tenant or vacant'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G519 — O-FRD-50477 [O-FRD]
- **Q:** Were all subject section requirements met?
- **Defect condition:** The owner of public record was not provided and/or was incorrect
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4548
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The owner of public record was not provided and/or was incorrect'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G520 — O-FRD-50476 [O-FRD]
- **Q:** Were all subject section requirements met?
- **Defect condition:** The subject section, address and/or legal description was incomplete/incorrect
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4653
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The subject section, address and/or legal description was incomplete/incorrect'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G522 — O-FHA-55623 [O-FHA]
- **Q:** Were all swimming pool requirements met?
- **Defect condition:** Appraisal not conditioned for pool with structure issues be fixed or permanently filled in
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4661
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Appraisal not conditioned for pool with structure issues be fixed or permanently filled in'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G524 — O-FHA-55624 [O-FHA]
- **Q:** Were all swimming pool requirements met?
- **Defect condition:** Not assumed the pool & equipment can be restored to operation if winterized/undeterminable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4703
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Not assumed the pool & equipment can be restored to operation if winterized/undeterminable'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G525 — O-FHA-55622 [O-FHA]
- **Q:** Were all swimming pool requirements met?
- **Defect condition:** Observable defects in a noncovered pool not reported rendering the pool inoperable or unusable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4475
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Observable defects in a noncovered pool not reported rendering the pool inoperable or unusable'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G526 — O-FHA-55411 [O-FHA]
- **Q:** Were all valuation, reporting, and fair lending appraisal protocols requirements met?
- **Defect condition:** Appraisal evidences bias of buyers, owners or subject area occupants or other prohibited basis
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4532
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('bias') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Appraisal evidences bias of buyers, owners or subject area occupants or other prohibited basis'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G527 — O-FHA-55410 [O-FHA]
- **Q:** Were all valuation, reporting, and fair lending appraisal protocols requirements met?
- **Defect condition:** Appraisal non-compliant with applicable laws, the Fair Housing Act &/or local antidiscrimination law
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4595
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('discriminat') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Appraisal non-compliant with applicable laws, the Fair Housing Act &/or local antidiscrimination law'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G528 — O-FHA-00450 [O-FHA]
- **Q:** Were all valuation, reporting, and fair lending appraisal protocols requirements met?
- **Defect condition:** Appraiser did not identify/adjust for sales concessions that affect the sales price of the comps
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4621
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Appraiser did not identify/adjust for sales concessions that affect the sales price of the comps'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G529 — O-FHA-00592 [O-FHA]
- **Q:** Were all valuation, reporting, and fair lending appraisal protocols requirements met?
- **Defect condition:** Appraiser did not provide commentary or sufficient description on dissimilar comps &/or adjustments
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4619
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Appraiser did not provide commentary or sufficient description on dissimilar comps &/or adjustments'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G530 — O-FHA-55413 [O-FHA]
- **Q:** Were all valuation, reporting, and fair lending appraisal protocols requirements met?
- **Defect condition:** Appraiser misrepresented scope of work providing a knowing misleading or fraudulent appraisal report
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4262
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('misrepresent') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Appraiser misrepresented scope of work providing a knowing misleading or fraudulent appraisal report'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G532 — O-FHA-55412 [O-FHA]
- **Q:** Were all valuation, reporting, and fair lending appraisal protocols requirements met?
- **Defect condition:** Discrimination used in developing part of the appraisal/value conclusion that are protected by laws
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4259
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('Discriminat') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Discrimination used in developing part of the appraisal/value conclusion that are protected by laws'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G535 — O-FNM-55740 [O-FNM]
- **Q:** Were all value acceptance (appraisal waiver) requirements met?
- **Defect condition:** No acceptable home inspection in the file where a rural high-needs value acceptance was exercised
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4616
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('acceptable') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'No acceptable home inspection in the file where a rural high-needs value acceptance was exercised'
- **Classified by:** family_classifier
- **Guide candidate:** B2-1.2-03 — Home Equity Combined Loan-to-Value (HCLTV) Ratios (PDF p.182)
- **Guide candidate:** B4-1.4-10 — Value Acceptance (PDF p.631)
- **Guide candidate:** B4-1.4-11 — Value Acceptance + Property Data (PDF p.634)
- **SME:** [ ] agree [ ] correct: ______

### G554 — O-FRD-00500 [O-FRD]
- **Q:** Were appraisal delivery requirements met?
- **Defect condition:** Appraisal is an electronic record that does not meet Freddie Mac original document requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4393
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Appraisal is an electronic record that does not meet Freddie Mac original document requirements'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G558 — O-FRD-57315 [O-FRD]
- **Q:** Were co-op appraisal requirements met?_x000D_
- **Defect condition:** Condominium unit comparables were used without an acceptable explanation and adjustments
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4310
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('acceptable') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Condominium unit comparables were used without an acceptable explanation and adjustments'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G560 — O-FRD-57311 [O-FRD]
- **Q:** Were co-op appraisal requirements met?_x000D_
- **Defect condition:** The appraiser did not comment on the acceptance of housing cooperatives in the market area
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4345
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('did not comment') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'The appraiser did not comment on the acceptance of housing cooperatives in the market area'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G575 — VA Master [O-VA]
- **Q:** Were general condo project eligibility requirements met?
- **Defect condition:** Master Insurance requirements were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4505
- **Severity:** Critical
- **Stays human:** open-ended catch-all with no single stated fact
- **Rationale:** Bare 'requirements not met' catch-all, same pattern as application-verification's VA-disclosure catch-all and assets' Community-Savings-System/IDA catch-alls — needs SME decomposition before any automation; condition: 'Master Insurance requirements were not met'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G577 — ReplacementCost [O-VA]
- **Q:** Were general condo project eligibility requirements met?
- **Defect condition:** Replacement cost coverage not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4606
- **Severity:** Critical
- **Stays human:** open-ended catch-all with no single stated fact
- **Rationale:** Bare 'requirements not met' catch-all, same pattern as application-verification's VA-disclosure catch-all and assets' Community-Savings-System/IDA catch-alls — needs SME decomposition before any automation; condition: 'Replacement cost coverage not met'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G588 — O-FRD-51014 [O-FRD]
- **Q:** Were general condo project eligibility requirements met?_x000D_
- **Defect condition:** The appropriate condominium project review was not conducted as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4309
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('appropriate') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'The appropriate condominium project review was not conducted as applicable'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G598 — O-FRD-50517 [O-FRD]
- **Q:** Were leasehold estate requirements met?
- **Defect condition:** Leasehold property  terms/conditions/restrictions of ground lease not given
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4495
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('marketability') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Leasehold property  terms/conditions/restrictions of ground lease not given'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G601 — O-FRD-50518 [O-FRD]
- **Q:** Were leasehold estate requirements met?
- **Defect condition:** Similar leasehold sales with the same lease terms not used without comment
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4484
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('without comment') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Similar leasehold sales with the same lease terms not used without comment'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G603 — O-FRD-52748 [O-FRD]
- **Q:** Were co-op project eligibility requirements met?_x000D_
- **Defect condition:** Cooperative owner-occupancy requirements were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4348
- **Severity:** Critical
- **Stays human:** open-ended catch-all with no single stated fact
- **Rationale:** Bare 'requirements not met' catch-all, same pattern as application-verification's VA-disclosure catch-all and assets' Community-Savings-System/IDA catch-alls — needs SME decomposition before any automation; condition: 'Cooperative owner-occupancy requirements were not met'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G617 — O-RHS-58086 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, was the Contract section of the appraisal complete and accurate?_x000D_
- **Defect condition:** The specific data and verification source for each comparable not given
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4165
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('did not indicate whether') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'The specific data and verification source for each comparable not given'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G618 — O-RHS-58193 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, was the final value supported and concluded using appropriate methods?
- **Defect condition:** Analysis in the cost approach is inconsistent to other areas of the report
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4171
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('appropriate') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Analysis in the cost approach is inconsistent to other areas of the report'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G619 — O-RHS-58194 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, was the final value supported and concluded using appropriate methods?
- **Defect condition:** Income approach did not include comparable rental/sales, & calc used for gross rent multiplier
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4197
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('appropriate') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Income approach did not include comparable rental/sales, & calc used for gross rent multiplier'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G621 — O-RHS-58174 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were all other property conditions and requirements met?
- **Defect condition:** Age range & predominant age of the properties in the neighborhood not provided by the appraiser
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4214
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Age range & predominant age of the properties in the neighborhood not provided by the appraiser'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G622 — O-RHS-58087 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were all other property conditions and requirements met?
- **Defect condition:** Available land/degree of development, zoning/present land use not reported ensuring residential area
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4208
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Available land/degree of development, zoning/present land use not reported ensuring residential area'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G623 — O-RHS-58178 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were all other property conditions and requirements met?
- **Defect condition:** Legally enforceable maintenance agreement/covenant of community or private owned street as required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4281
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Legally enforceable maintenance agreement/covenant of community or private owned street as required'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G624 — O-RHS-58085 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were all other property conditions and requirements met?
- **Defect condition:** Neighborhood boundaries, characteristics & marketability factors not reported on the appraisal
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4210
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('marketability') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Neighborhood boundaries, characteristics & marketability factors not reported on the appraisal'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G626 — O-RHS-58088 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were all other property conditions and requirements met?
- **Defect condition:** Price range/predominant price & area high/low prevailing price of same property type not reported
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4216
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Price range/predominant price & area high/low prevailing price of same property type not reported'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G627 — O-RHS-58176 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were all other property conditions and requirements met?
- **Defect condition:** Specific zoning class & a general statement to what the zoning permits not reported in the appraisal
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4244
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Specific zoning class & a general statement to what the zoning permits not reported in the appraisal'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G628 — O-RHS-58186 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were all other property conditions and requirements met?
- **Defect condition:** Standard conditions/quality construction ratings not assigned on a UAD appraisal
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4576
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Standard conditions/quality construction ratings not assigned on a UAD appraisal'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G629 — O-RHS-58089 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were all other property conditions and requirements met?
- **Defect condition:** Subject appears to be an over-improvement &/or is not in the comps adjustment grid without comment
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4212
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('appears') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Subject appears to be an over-improvement &/or is not in the comps adjustment grid without comment'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G630 — O-RHS-58175 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were all other property conditions and requirements met?
- **Defect condition:** The appraiser did not comment if any adverse site conditions or external factors existed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4239
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('did not comment') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'The appraiser did not comment if any adverse site conditions or external factors existed'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G631 — O-RHS-58177 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were all other property conditions and requirements met?
- **Defect condition:** The subject improvements are not considered the highest and best use of the site
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4242
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('highest and best use') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'The subject improvements are not considered the highest and best use of the site'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G632 — O-RHS-58185 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were all specific dwelling requirements met?
- **Defect condition:** A description and impact of an outbuilding on the property not given
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4194
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'A description and impact of an outbuilding on the property not given'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G633 — O-RHS-58179 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were all specific dwelling requirements met?
- **Defect condition:** Aerial images show subject does not conform to the neighborhood w/out explanation from the appraiser
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4187
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Aerial images show subject does not conform to the neighborhood w/out explanation from the appraiser'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G634 — O-FNM-50289 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were all specific dwelling requirements met?
- **Defect condition:** All requirements for a property with an accessory unit not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4184
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'All requirements for a property with an accessory unit not met'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G635 — O-RHS-58181 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were all specific dwelling requirements met?
- **Defect condition:** Effective age is higher than the actual age indicating poor subject condition without comment
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4189
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('without comment') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Effective age is higher than the actual age indicating poor subject condition without comment'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G637 — O-RHS-58182 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were all specific dwelling requirements met?
- **Defect condition:** Special energy saving items not noted on energy efficient property
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4191
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Special energy saving items not noted on energy efficient property'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G638 — O-RHS-58183 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were all specific dwelling requirements met?
- **Defect condition:** The GLA was calculated incorrectly or not consistently applied
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4192
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The GLA was calculated incorrectly or not consistently applied'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G639 — O-RHS-58184 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were all specific dwelling requirements met?
- **Defect condition:** The impact &/or commentary of an unpermitted addition was not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4186
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The impact &/or commentary of an unpermitted addition was not provided'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G640 — O-RHS-58180 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were all specific dwelling requirements met?
- **Defect condition:** Unique property without recent similar comps, adjustments or ability to demonstrate marketability
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4195
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('marketability') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Unique property without recent similar comps, adjustments or ability to demonstrate marketability'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G645 — O-RHS-02684 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were all the required exhibits provided and acceptable?
- **Defect condition:** Photographs are not clear and descriptive to identify the property’s condition and quality
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4221
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('acceptable') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Photographs are not clear and descriptive to identify the property’s condition and quality'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G646 — O-RHS-57525 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were all the required exhibits provided and acceptable?
- **Defect condition:** The interior and exterior appraisal report did not include all required photographs
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4608
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('acceptable') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'The interior and exterior appraisal report did not include all required photographs'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G647 — O-RHS-58187 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were the comparables used the best and most appropriate and were all requirements met?
- **Defect condition:** Appraiser didn’t select within and outside of subject subdivision/project or provide comment
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4237, 4238
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('appropriate') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Appraiser didn’t select within and outside of subject subdivision/project or provide comment'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G648 — O-RHS-58192 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were the comparables used the best and most appropriate and were all requirements met?
- **Defect condition:** Comp time adj w/out explanation or analysis of market cond changes from their contract date-eff date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4159
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('appropriate') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Comp time adj w/out explanation or analysis of market cond changes from their contract date-eff date'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G649 — O-RHS-58078 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were the comparables used the best and most appropriate and were all requirements met?
- **Defect condition:** Comparable sales were not closed within the last 12 months and no explanation provided for their use
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4158
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('appropriate') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Comparable sales were not closed within the last 12 months and no explanation provided for their use'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G650 — O-RHS-58189 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were the comparables used the best and most appropriate and were all requirements met?
- **Defect condition:** Comps are not similar in physical/legal characteristics, room count, GLA, style, and condition etc
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4632, 4633
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('appropriate') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Comps are not similar in physical/legal characteristics, room count, GLA, style, and condition etc'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G651 — O-RHS-58190 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were the comparables used the best and most appropriate and were all requirements met?
- **Defect condition:** Comps provided not from within & outside of the new condo, subdivision or PUD without explanation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4206
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('appropriate') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Comps provided not from within & outside of the new condo, subdivision or PUD without explanation'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G652 — O-RHS-58195 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were the comparables used the best and most appropriate and were all requirements met?
- **Defect condition:** Condo comparable was used instead of a co-op comparable without comment
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4160
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('appropriate') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Condo comparable was used instead of a co-op comparable without comment'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G653 — O-RHS-58081 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were the comparables used the best and most appropriate and were all requirements met?
- **Defect condition:** Dollar amount of concessions in comps/adjustments reflecting the market's reaction is not noted
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4623
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('appropriate') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: "Dollar amount of concessions in comps/adjustments reflecting the market's reaction is not noted"
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G655 — O-RHS-58188 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were the comparables used the best and most appropriate and were all requirements met?
- **Defect condition:** Subject's 3 year sales history & comps sales history for last 12 months not reported
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4235
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('appropriate') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: "Subject's 3 year sales history & comps sales history for last 12 months not reported"
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G656 — O-RHS-58191 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were the comparables used the best and most appropriate and were all requirements met?
- **Defect condition:** The adj to the comps indicate the subject may not conform to the area
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4156
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('appropriate') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'The adj to the comps indicate the subject may not conform to the area'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G657 — O-RHS-58077 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were the comparables used the best and most appropriate and were all requirements met?
- **Defect condition:** The primary indicators of market conditions was not reported using trends in property values
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4218
- **Severity:** Major
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('appropriate') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'The primary indicators of market conditions was not reported using trends in property values'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G658 — O-RHS-50616 [O-RHS]
- **Q:** Where a property has been affected by a disaster, were all appraisal requirements met?
- **Defect condition:** An inspection of the property was not performed to assess the degree of any damage
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4385
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'An inspection of the property was not performed to assess the degree of any damage'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G662 — O-RHS-50618 [O-RHS]
- **Q:** Where a property has been affected by a disaster, were all appraisal requirements met?
- **Defect condition:** Did not consult the appraiser for any impact of any revision to the contract of sale for the subject
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4383
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Did not consult the appraiser for any impact of any revision to the contract of sale for the subject'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G663 — O-RHS-50617 [O-RHS]
- **Q:** Where a property has been affected by a disaster, were all appraisal requirements met?
- **Defect condition:** Did not re-verify property insurance coverage for adequacy to protect against future losses
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4386
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Did not re-verify property insurance coverage for adequacy to protect against future losses'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G664 — O-FNM-00544 [O-FNM]
- **Q:** Where a property has been affected by a disaster, were all appraisal requirements met?
- **Defect condition:** No safety/soundness disaster impact but repair estimates & insurance proceeds not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4575
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'No safety/soundness disaster impact but repair estimates & insurance proceeds not documented'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-07 — Mixed-Use Property Appraisal Requirements (PDF p.626)
- **Guide candidate:** B7-3-01 — General Property Insurance Requirements for All Property Types (PDF p.872)
- **Guide candidate:** B7-3-02 — Property Insurance Requirements for One-to Four-Unit Properties (PDF p.875)
- **SME:** [ ] agree [ ] correct: ______

### G666 — O-FNM-55651 [O-FNM]
- **Q:** Where a property has been affected by a disaster, were all appraisal requirements met?
- **Defect condition:** Property not repaired after disaster w/ uninsured damage affecting safety, soundness, or structure
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4673
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Property not repaired after disaster w/ uninsured damage affecting safety, soundness, or structure'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-07 — Mixed-Use Property Appraisal Requirements (PDF p.626)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **Guide candidate:** B2-3-01 — General Property Eligibility (PDF p.258)
- **SME:** [ ] agree [ ] correct: ______

### G670 — O-FRD-53033 [O-FRD]
- **Q:** Where a second appraisal was obtained, were all requirements met?_x000D_
- **Defect condition:** Second appraisal ordered without explanation and/or all appraisals are not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4658, 4659
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('without explanation') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: 'Second appraisal ordered without explanation and/or all appraisals are not in the file'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G672 — O-FRD-50475 [O-FRD]
- **Q:** Where the appraisal was completed subject to completion, repairs, or alterations, were all requirements met?
- **Defect condition:** Final inspection/licensed professional report not in the file if applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4500
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Final inspection/licensed professional report not in the file if applicable'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G680 — O-FRD-54129 [O-FRD]
- **Q:** Where the property has energy-efficient improvements, were all requirements met?
- **Defect condition:** Solar panels UCC-1/lease not used to determine liens against the subject or solar panels themselves
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4644
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Solar panels UCC-1/lease not used to determine liens against the subject or solar panels themselves'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G681 — O-FRD-50497 [O-FRD]
- **Q:** Where the property has energy-efficient improvements, were all requirements met?
- **Defect condition:** Solar panels subject to lease agmt, PPA or similar that was not excluded from the appraised value
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4483
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Solar panels subject to lease agmt, PPA or similar that was not excluded from the appraised value'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G682 — O-FNM-55388 [O-FNM]
- **Q:** Where the property has energy-efficient improvements, were all requirements met?
- **Defect condition:** Subject not built under the IRC as req'd for modular, prefabricated, panelized, or sectional housing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4514
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: "Subject not built under the IRC as req'd for modular, prefabricated, panelized, or sectional housing"
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.4-02 — Factory-Built Housing: Modular, Prefabricated, Panelized, or Sectional Housing (PDF p.616)
- **Guide candidate:** B2-3-02 — Special Property Eligibility and Underwriting Considerations: Factory-Built Housing (PDF p.261)
- **Guide candidate:** B3-6-03 — Monthly Housing Expense for the Subject Property (PDF p.518)
- **SME:** [ ] agree [ ] correct: ______

### G683 — O-FRD-54130 [O-FRD]
- **Q:** Where the property has energy-efficient improvements, were all requirements met?
- **Defect condition:** The solar panels lease agreement, PPA or similar agreement was not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4643
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'The solar panels lease agreement, PPA or similar agreement was not in the file'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G684 — O-FNM-53034 [O-FNM]
- **Q:** Where the property has energy-efficient improvements, were all requirements met?
- **Defect condition:** The subject's solar panels were not valued properly based on the ownership structure of the panels
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4645
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: "The subject's solar panels were not valued properly based on the ownership structure of the panels"
- **Classified by:** family_classifier
- **Guide candidate:** B3-6-03 — Monthly Housing Expense for the Subject Property (PDF p.518)
- **Guide candidate:** B4-1.3-06 — Property Condition and Quality of Construction of the Improvements (PDF p.587)
- **Guide candidate:** B5-3.4-01 — Property Assessed Clean Energy Loans (PDF p.766)
- **SME:** [ ] agree [ ] correct: ______

### G686 — O-FRD-56484 [O-FRD]
- **Q:** Where the property is encumbered by private transfer fee covenants, were all requirements met?
- **Defect condition:** Private transfer fee does not meet Duty to Serve shared equity criteria in 12 CFR 1282.34(d)(4)
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4561
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Private transfer fee does not meet Duty to Serve shared equity criteria in 12 CFR 1282.34(d)(4)'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G687 — O-FRD-56483 [O-FRD]
- **Q:** Where the property is encumbered by private transfer fee covenants, were all requirements met?
- **Defect condition:** Subject has a private transfer fee & is not a shared equity loan with a Note date on or after 7/1/23
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4630
- **Severity:** Major
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Subject has a private transfer fee & is not a shared equity loan with a Note date on or after 7/1/23'
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G688 — O-FRD-00880 [O-FRD]
- **Q:** Where the property is encumbered by private transfer fee covenants, were all requirements met?
- **Defect condition:** The subject's private transfer fee covenants were created on or after 2/8/11, which are ineligible
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4560
- **Severity:** Critical
- **Stays human:** no crisp extractable fact identified in this row's condition text
- **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: "The subject's private transfer fee covenants were created on or after 2/8/11, which are ineligible"
- **Classified by:** family_classifier
- **SME:** [ ] agree [ ] correct: ______

### G696 — O-BP-FED-59094 [GENERIC]
- **Q:** Where there was an appraisal and AVM in the file, and the AVM value was used, was the AVM value based on appropriate valuation methods?
- **Defect condition:** (Best Practice) The use of the AVM value was based on inappropriate valuation methods
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4271
- **Severity:** Critical
- **Stays human:** narrative-adequacy judgment on the appraiser's written commentary/analysis
- **Rationale:** Matched narrative-judgment vocabulary ('appropriate') — requires reading and judging free-text commentary in the appraisal report body, which this pilot's regex-based field extractor does not capture and could not capture without full semantic parsing of the narrative sections; condition: '(Best Practice) The use of the AVM value was based on inappropriate valuation methods'
- **Classified by:** family_classifier
- **Guide candidate:** B4-1.2-04 — Appraisal Age and Use Requirements (PDF p.559)
- **Guide candidate:** B4-1.4-07 — Mixed-Use Property Appraisal Requirements (PDF p.626)
- **Guide candidate:** A2-2-06 — Representations and Warranties on Property Value (PDF p.46)
- **SME:** [ ] agree [ ] correct: ______

## NOT_A_CHECK

### G001 —  [O-FHA]
- **Q:** (FHA) Is there an appraisal in the file?
- **Defect condition:** No, an appraisal is not required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4710, 4711
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G003 —  [O-FNM]
- **Q:** (Fannie Mae) Is there an appraisal in the file?
- **Defect condition:** No, an appraisal is not required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4738, 4739, 4740, 4741
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G005 —  [O-FRD]
- **Q:** (Freddie Mac) Is there an appraisal in the file?
- **Defect condition:** No, an appraisal is not required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4808, 4809
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G007 —  [O-RHS]
- **Q:** (RHS) Is there an appraisal in the file?
- **Defect condition:** No, an appraisal is not required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4894, 4895
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G009 —  [O-VA]
- **Q:** (VA) Is there an appraisal in the file?
- **Defect condition:** No, an appraisal is not required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4928, 4929
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G012 —  [O-FRD]
- **Q:** Appraisal Review FAQ, Q5: If the desk review determined that the value of the property is supported, was it still ensured that the condition and marketability of the subject property are acceptable and that the mortgaged premises is adequate collateral?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4886, 4887
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G014 —  [O-FRD]
- **Q:** Appraisal Review FAQ, Q6: If the desk review performed by a qualified reviewer was not able to determine the accuracy of the appraisal or the adequacy of the collateral, was a desk review or field review by a certified appraiser obtained?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4888, 4889
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G016 —  [O-FRD]
- **Q:** Appraisal Review FAQ, Q6: If the internal desk review prompted a desk review or field review by a certified appraiser, was the original market value supported?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4890, 4891
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G018 —  [O-FRD]
- **Q:** Appraisal Review FAQ, Q8: When an analyst or appraiser performs a desk review to satisfy the QC reverification requirement, was Form F1033-1 used or another appropriate form?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4892, 4893
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G021 —  [GENERIC]
- **Q:** Are all requirements met when the seller acquired the property within 180 days of the contract ( including Full Appraisal regardless of DU)?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4947, 4948
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G023 —  [O-FNM]
- **Q:** Did the appraiser address external influences impacting value or marketability, and did the comparables provided have similar external influences as per aerial image(s)?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4797, 4798
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G024 —  [O-FHA]
- **Q:** Does any identified legal restriction on conveyance conform with the requirements?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4717, 4718
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G030 —  [O-FNM/O-FRD]
- **Q:** Does the appraisal evidence unacceptable appraisal practices?_x000D_
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4791, 4792, 4814, 4815
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G042 —  [O-FRD]
- **Q:** Does the appraisal report meet all requirements?
- **Defect condition:** Yes, the appraisal report meets all requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4816
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G044 —  [O-FRD]
- **Q:** Form F1033-1, Section I, 1. Is the information in the subject section complete and accurate?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4864, 4865
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G046 —  [O-FRD]
- **Q:** Form F1033-1, Section I, 10. If the opinion of market value in the appraisal report under review is inaccurate as of the effective date of the appraisal report, was Section II completed to substantiate and provide a new opinion of value?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4884, 4885
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G047 —  [O-FRD]
- **Q:** Form F1033-1, Section I, 10. Is the opinion of market value in the appraisal under review accurate as of the effective date of the appraisal report?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4882, 4883
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G050 —  [O-FRD]
- **Q:** Form F1033-1, Section I, 2. Is the information in the contract section complete and accurate?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4866, 4867
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G052 —  [O-FRD]
- **Q:** Form F1033-1, Section I, 3. Is the information in the neighborhood section complete and accurate?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4868, 4869
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G054 —  [O-FRD]
- **Q:** Form F1033-1, Section I, 4. Is the information in the site section complete and accurate?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4870, 4871
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G056 —  [O-FRD]
- **Q:** Form F1033-1, Section I, 5. Is the data in the improvements section complete and accurate?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4872, 4873
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G058 —  [O-FRD]
- **Q:** Form F1033-1, Section I, 6. Are the comparable sales selected locationally, physically, and functionally the most similar to the subject property?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4874, 4875
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G060 —  [O-FRD]
- **Q:** Form F1033-1, Section I, 7. Are the data and analysis (including the individual adjustments) presented in the sales comparison approach complete and accurate?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4876, 4877
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G061 —  [O-FRD]
- **Q:** Form F1033-1, Section I, 8. Are the data and analysis presented in the income and cost approaches complete and accurate if developed?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4878, 4879
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G064 —  [O-FRD]
- **Q:** Form F1033-1, Section I, 9. Is the sale or transfer history reported for the subject property and each of the comparable sales complete and accurate?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4880, 4881
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G068 —  [O-FRD]
- **Q:** If the subject is in a federally declared disaster area, were all requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4811, 4812
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G070 —  [GENERIC]
- **Q:** Was the GAAR worksheet completed in the file and all applicable conditions met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4706, 4707
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G073 —  [GENERIC]
- **Q:** Was the appropriate level of appraisal review completed based on the CU score?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4704, 4705
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G086 —  [O-FRD]
- **Q:** Were additional general condo project eligibility requirements met?_x000D_
- **Defect condition:** Yes
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4845
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G089 —  [O-FRD]
- **Q:** Were all 2- to 4-unit property requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4833, 4834
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G093 —  [O-FNM]
- **Q:** Were all Collateral Risk Assessment requirements met?_x000D_
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4752, 4753
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G102 —  [O-FNM]
- **Q:** Were all Comparable sales requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4765, 4766
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G106 —  [O-VA]
- **Q:** Were all Comparable sales requirements met?
- **Defect condition:** Yes, all Comparable sales requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4932
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G113 —  [O-FNM]
- **Q:** Were all Condominium Project Questionnaire appraisal requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4778, 4779
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G122 —  [O-FHA]
- **Q:** Were all Gross Living Area (GLA) appraisal requirements met?
- **Defect condition:** Yes, all Gross Living Area (GLA) appraisal requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4726
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G127 —  [O-FNM]
- **Q:** Were all Gross Living Area (GLA) appraisal requirements met?_x000D_
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4788, 4789
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G131 —  [O-FNM]
- **Q:** Were all Gross Living Area (GLA) appraisal requirements met?_x000D_
- **Defect condition:** Yes, all GLA appraisal requirements have been met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4807
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G134 —  [O-FNM]
- **Q:** Were all Improvements section of the appraisal requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4761, 4762
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G142 —  [O-VA]
- **Q:** Were all Lender Appraisal Processing Program (LAPP) requirements met?
- **Defect condition:** Yes, all Lender Appraisal Processing Program (LAPP) requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4942
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G150 —  [O-FNM]
- **Q:** Were all Neighborhood section of the appraisal requirements met?_x000D_
- **Defect condition:** Yes, all Neighborhood section of the appraisal requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4758
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G162 —  [O-VA]
- **Q:** Were all Notice of Value (NOV) requirements met?
- **Defect condition:** Yes, all Notice of Value (NOV) requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4939
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G163 —  [O-FNM]
- **Q:** Were all Sales Comparison Approach section of the appraisal requirements met?_x000D_
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4763, 4764
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G169 —  [O-FNM]
- **Q:** Were all Site sections of the appraisal requirements met?_x000D_
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4759, 4760
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G175 —  [O-FNM]
- **Q:** Were all Subject and Contract sections of the appraisal requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4756, 4757
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G178 — O-FNM-50273 [O-FNM]
- **Q:** Were all Subject and Contract sections of the appraisal requirements met?
- **Defect condition:** Yes or No box not checked if subject listed in last year &/or no data source, offering price & date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4167
- **Severity:** Critical
- **Rationale:** Pass/N-A/screening answer option, not a defect condition.
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G185 —  [O-RHS]
- **Q:** Were all additional appraisal report requirements met?
- **Defect condition:** Yes, all additional appraisal report requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4901
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G190 —  [O-FHA]
- **Q:** Were all additional appraisal requirements met?
- **Defect condition:** Yes, all additional appraisal requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4731
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G195 —  [O-FHA]
- **Q:** Were all additional appraisal underwriting requirements met?
- **Defect condition:** Yes, all additional appraisal underwriting requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4720
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G198 —  [O-FHA]
- **Q:** Were all additional condo appraisal requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4723, 4724
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G205 —  [O-VA]
- **Q:** Were all additional general appraisal requirements met?
- **Defect condition:** Yes, all additional general appraisal requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4931
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G212 —  [O-FNM]
- **Q:** Were all additional leasehold estate appraisal requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4795, 4796
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G219 —  [O-VA]
- **Q:** Were all additional minimum property requirements met?_x000D_
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4945, 4946
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G224 —  [O-FHA]
- **Q:** Were all additional specific appraisal requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4734, 4735
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G230 —  [O-FHA]
- **Q:** Were all additional valuation, reporting, and fair lending appraisal protocol requirements met?_x000D_
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4736, 4737
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G232 —  [O-FNM]
- **Q:** Were all appraisal delivery requirements met?
- **Defect condition:** Yes, all appraisal delivery requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4742
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G237 —  [O-FHA]
- **Q:** Were all appraisal effective date requirements met?
- **Defect condition:** Yes, all appraisal effective date requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4713
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G239 —  [O-FRD]
- **Q:** Were all appraisal exhibit and addenda requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4817, 4818
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G248 —  [O-FHA]
- **Q:** Were all appraisal ordering requirements met?
- **Defect condition:** Yes, all appraisal ordering requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4712
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G252 —  [O-FHA]
- **Q:** Were all appraisal property acceptability criteria requirements met?
- **Defect condition:** Yes, all appraisal property acceptability criteria requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4716
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G262 —  [O-FNM]
- **Q:** Were all appraisal report form, age, and use requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4754, 4755
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G273 —  [O-RHS]
- **Q:** Were all appraisal report requirements met?
- **Defect condition:** Yes, all appraisal report requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4900
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G284 —  [O-FHA]
- **Q:** Were all appraisal underwriting requirements met?
- **Defect condition:** Yes, all appraisal underwriting requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4719
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G287 —  [O-FNM]
- **Q:** Were all appraiser selection criteria and information disclosure requirements met?
- **Defect condition:** Yes, all appraiser selection criteria and information disclosure requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4751
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G290 —  [O-FNM]
- **Q:** Were all community land trust appraisal requirements met?_x000D_
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4770, 4771
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G297 —  [O-FHA/O-FNM/O-RHS]
- **Q:** Were all condo appraisal requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4721, 4722, 4768, 4769, 4908, 4909
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G311 —  [O-FNM]
- **Q:** Were all condo or co-op project deferred maintenance requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4784, 4785
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G319 —  [O-FNM]
- **Q:** Were all condo or co-op ineligible projects appraisal requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4780, 4781
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G329 —  [O-FNM]
- **Q:** Were all condo or co-op project review requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4782, 4783
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G342 —  [O-FRD]
- **Q:** Were all condominium exempt from review requirements met?_x000D_
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4848, 4849
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G347 —  [O-FRD]
- **Q:** Were all contract, neighborhood, site, and improvement section requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4822, 4823
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G358 —  [O-FNM]
- **Q:** Were all cost and income approach to value requirements met?
- **Defect condition:** Yes, all cost and income approach to value requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4767
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G364 —  [O-FRD]
- **Q:** Were all desktop appraisal requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4860, 4861
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G368 —  [O-FNM/O-RHS]
- **Q:** Were all environmental hazards appraisal requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4774, 4775, 4906, 4907
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G374 —  [O-RHS]
- **Q:** Were all existing dwelling requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4902, 4903
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G393 —  [O-FRD/O-VA]
- **Q:** Were all general appraisal requirements met?
- **Defect condition:** Yes, all general appraisal requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4813, 4930
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G397 —  [O-FRD]
- **Q:** Were all general property eligibility requirements met?
- **Defect condition:** Yes, all general property eligibility requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4810
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G402 —  [O-FNM/O-RHS]
- **Q:** Were all leasehold estate appraisal requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4743, 4744, 4910, 4911
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G412 —  [O-FNM]
- **Q:** Were all lender responsibilities requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4749, 4750
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G422 —  [O-FHA]
- **Q:** Were all minimum property appraisal requirements met?
- **Defect condition:** Yes, all minimum property appraisal requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4725
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G427 —  [O-VA]
- **Q:** Were all minimum property requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4935, 4936
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G432 —  [O-FNM]
- **Q:** Were all mixed-use properties appraisal requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4772, 4773
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G438 —  [O-FRD]
- **Q:** Were all mixed-use property requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4837, 4838
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G441 —  [O-RHS]
- **Q:** Were all new construction requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4904, 4905
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G447 —  [O-RHS]
- **Q:** Were all qualified appraiser requirements met?_x000D_
- **Defect condition:** Yes, all qualified appraiser requirements have been met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4899
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G450 —  [O-FRD]
- **Q:** Were all reconciliation, cost approach, and income approach requirements met?_x000D_
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4830, 4831, 4832
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G454 —  [O-FRD]
- **Q:** Were all requirements met for a property with an accessory dwelling unit?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4862, 4863
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G461 —  [O-FNM]
- **Q:** Were all requirements met for a property with an accessory dwelling unit?_x000D_
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4793, 4794
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G469 —  [O-VA]
- **Q:** Were all requirements met for the use of an exterior-only or desktop appraisal?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4943, 4944
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G470 —  [O-RHS]
- **Q:** Were all rural area designation requirements met?_x000D_
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4896, 4897
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G477 —  [O-FRD]
- **Q:** Were all sales comparison approach requirements met?_x000D_
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4828, 4829
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G483 —  [O-FHA]
- **Q:** Were all second order appraisal requirements met?_x000D_
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4714, 4715
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G494 —  [O-RHS]
- **Q:** Were all site requirements met?
- **Defect condition:** Yes, all site requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4898
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G501 —  [O-FNM]
- **Q:** Were all special property appraisal requirements met?_x000D_
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4745, 4746
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G514 —  [O-FHA]
- **Q:** Were all specific appraisal requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4727, 4728
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G521 —  [O-FRD]
- **Q:** Were all subject section requirements met?
- **Defect condition:** Yes, all subject section requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4821
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G523 —  [O-FHA]
- **Q:** Were all swimming pool requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4732, 4733
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G533 —  [O-FHA]
- **Q:** Were all valuation, reporting, and fair lending appraisal protocols requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4729, 4730
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G536 —  [O-FNM]
- **Q:** Were all value acceptance (appraisal waiver) requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4776, 4777
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G553 —  [O-FNM]
- **Q:** Were all value acceptance + property data requirements met?
- **Defect condition:** Yes, all value acceptance + property data requirements are met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4790
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G556 —  [O-FRD]
- **Q:** Were appraisal delivery requirements met?
- **Defect condition:** Yes, all appraisal delivery requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4842
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G562 —  [O-FRD]
- **Q:** Were co-op appraisal requirements met?_x000D_
- **Defect condition:** Yes, all co-op appraisal requirements have been met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4857
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G566 —  [O-FRD]
- **Q:** Were established condo project requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4846, 4847
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G576 —  [O-VA]
- **Q:** Were general condo project eligibility requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4937, 4938
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G584 —  [O-FRD]
- **Q:** Were general condo project eligibility requirements met?_x000D_
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4843, 4844
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G593 —  [O-FRD]
- **Q:** Were general co-op eligibility requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4852, 4853
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G599 —  [O-FRD]
- **Q:** Were leasehold estate requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4850, 4851
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G611 —  [O-FRD]
- **Q:** Were co-op project eligibility requirements met?_x000D_
- **Defect condition:** Yes
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4854
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G613 —  [O-FRD]
- **Q:** Were co-op share loan eligibility requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4855, 4856
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G616 —  [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, was the Contract section of the appraisal complete and accurate?_x000D_
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4924, 4925
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G620 —  [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, was the final value supported and concluded using appropriate methods?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4922, 4923
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G625 —  [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were all other property conditions and requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4926, 4927
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G636 —  [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were all specific dwelling requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4914, 4915
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G642 —  [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were all subject, neighborhood, site and improvements sections of the appraisal complete and accurate?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4916, 4917
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G643 — O-RHS-58083 [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were all subject, neighborhood, site and improvements sections of the appraisal complete and accurate?
- **Defect condition:** Yes or No box not checked if subject listed in last year &/or no data source, offering price & date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 4168
- **Severity:** Major
- **Rationale:** Pass/N-A/screening answer option, not a defect condition.
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G654 —  [O-RHS]
- **Q:** Where RHS defers to Fannie Mae requirements, were the comparables used the best and most appropriate and were all requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4918, 4919
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G665 —  [O-FNM/O-RHS/O-VA]
- **Q:** Where a property has been affected by a disaster, were all appraisal requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4747, 4748, 4912, 4913, 4940, 4941
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G669 —  [O-FRD]
- **Q:** Where a second appraisal was obtained, were all requirements met?_x000D_
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4839, 4840, 4841
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G675 —  [O-FRD/O-VA]
- **Q:** Where the appraisal was completed subject to completion, repairs, or alterations, were all requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4819, 4820, 4933, 4934
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G679 —  [O-FNM/O-FRD]
- **Q:** Where the property has energy-efficient improvements, were all requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4786, 4787, 4835, 4836
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G685 —  [O-FRD]
- **Q:** Where the property is encumbered by private transfer fee covenants, were all requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4824, 4825
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G692 —  [O-FRD]
- **Q:** Where the subject has multiple parcels, were all requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4826, 4827
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

### G695 —  [GENERIC]
- **Q:** Where there was an appraisal and AVM in the file, and the AVM value was used, was the AVM value based on appropriate valuation methods?
- **Defect condition:** (Best Practice) The use of the AVM value was based on appropriate valuation methods
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 4708, 4709
- **Rationale:** Pass/N-A/screening answer option, not a defect condition (blank Exception Code in source CSV confirms this is a screening/applicability branch, not a scoreable defect).
- **Classified by:** mechanical
- **SME:** [ ] agree [ ] correct: ______

