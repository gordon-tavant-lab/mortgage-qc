# 002a Compile-Fidelity Spike — SME Review Package

**⚠️ PROVISIONAL — AI SELF-REVIEW, NOT KAYLA-VALIDATED.** Kayla is unavailable; per project direction
(2026-07-01), this review was completed by Claude (the same model family that compiled the rules, via
Sonnet 4.6) as a stopgap so the roadmap isn't blocked indefinitely on an external dependency. This is
**not** an independent domain-expert judgment and carries a real correlation risk (a model reviewing
another model's output may share its blind spots rather than catching them). Reviewed adversarially
— skeptical by default, not rubber-stamping — but this verdict must be re-confirmed by Kayla (or
another qualified SME) before being treated as final. Flagged explicitly in `RESULTS.md`.

**For: Kayla (when available) or the reviewer of record.** For each row, read `source_question` +
`source_response` (the real AMQ workbook text) and judge whether `plain_english_restatement` correctly
captures what that response means -- **not** whether the `constructed_label_score` passed (that only
tests internal consistency, not whether the rule reads the row correctly; a rule can pass that and
still misread the row's intent).

## predicate-00  (POLICY / predicate)

- **source_response**: Product specific pay history req's not met based on the type of refinance and length of time owned
- **plain_english_restatement**: This check flags when the borrower's payment history does not satisfy FHA's product-specific requirements given the particular type of refinance transaction (e.g., rate/term, cash-out, streamline) and the length of time the borrower has owned the property — the check fails when the field indicating those requirements are met evaluates to false.
- **verdict**: correct
- **correction**: (none)
- **reviewer_note**: Restatement is faithful. The parenthetical refinance-type examples are illustrative additions not present in the source text but are generically accurate and don't change the check's meaning.

## predicate-01  (MISSING / predicate)

- **source_response**: Certificate of Completion after Homestyle Renovations not in the file
- **plain_english_restatement**: This check verifies that a Certificate of Completion document exists in the loan file for loans that underwent HomeStyle Renovation; it flags as CRITICAL when that certificate is absent.
- **verdict**: correct
- **correction**: (none)
- **reviewer_note**:

## predicate-02  (MISSING / predicate)

- **source_response**: A disclosure outlining the ROV process at the time of loan application was not provided
- **plain_english_restatement**: This check flags as CRITICAL when there is no evidence in the loan file that a disclosure outlining the Reconsideration of Value (ROV) process was provided to the borrower at the time of loan application, as required under Fannie Mae guideline O-FNM-16691.
- **verdict**: correct
- **correction**: (none)
- **reviewer_note**:

## predicate-03  (MISSING / predicate)

- **source_response**: No invoice for Vet paid fees on the State Fees & Charges Deviations list without a max dollar amt
- **plain_english_restatement**: This check fails when a VA loan file contains vet-paid fees listed on the State Fees & Charges Deviations list that have no maximum dollar amount specified, and no supporting invoice document is present in the file to substantiate those fees.
- **verdict**: correct
- **correction**: (none)
- **reviewer_note**: The source sentence is a genuinely awkward compound condition (fees-without-a-cap AND no invoice). The restatement correctly untangles it — a good sign for compound-condition handling, worth noting positively.

## predicate-04  (MISSING / predicate)

- **source_response**: Due diligence not documented to ensure continuity of employment/income
- **plain_english_restatement**: This check fails when the loan file does not contain documented evidence that the lender performed due diligence to verify the continuity of the borrower's employment and/or income in accordance with COVID-19 temporary guidance (FRD-14443), flagging any file where that documentation field is absent or unpopulated.
- **verdict**: correct
- **correction**: (none)
- **reviewer_note**:

## predicate-05  (POLICY / predicate)

- **source_response**: The file does not support that all data submitted to DU is reliable information
- **plain_english_restatement**: This check fails when the loan file does not contain sufficient documentation or evidence to confirm that all data entered into Desktop Underwriter (DU) is accurate and reliable — i.e., the field 'du_data_reliability_supported' must be true (affirmatively supported by the file) or the check flags as CRITICAL.
- **verdict**: correct
- **correction**: (none)
- **reviewer_note**:

## predicate-06  (MISSING / predicate)

- **source_response**: IRS installment agreement verifying the payment terms, monthly payment & balance was not in the file
- **plain_english_restatement**: This check verifies that an IRS installment agreement document — one that confirms the payment terms, monthly payment amount, and outstanding balance — is present in the loan file; it flags as CRITICAL when that document is absent.
- **verdict**: correct
- **correction**: (none)
- **reviewer_note**:

## predicate-07  (MISSING / predicate)

- **source_response**: No, loan approved where property is in a CBRS/OPA and not covered by private flood insurance
- **plain_english_restatement**: This check flags as CRITICAL when a loan has been approved on a property located within a Coastal Barrier Resources System (CBRS) or Otherwise Protected Area (OPA) but the loan file does not evidence coverage by private flood insurance, which is required for such properties.
- **verdict**: correct
- **correction**: (none)
- **reviewer_note**:

## predicate-08  (ATR-QM / predicate)

- **source_response**: No, the payment calculation did not use the greater of fully indexed rate/introductory interest rate
- **plain_english_restatement**: This check fails when the loan's payment calculation does not use the greater of the fully indexed rate or the introductory interest rate — meaning the payment was computed using a rate that is not the higher of these two values, violating the federal requirement that the more conservative (higher) rate be used for qualification/payment purposes.
- **verdict**: ambiguous
- **correction**: (none)
- **reviewer_note**: **Flag for Kayla.** The restatement is textually faithful, but the compiled rule (`kind=predicate`, `predicate=is_true` on a single field) reduces an inherently *computational* check — compare two actual rate values, use the greater — into an opaque boolean the engine just reads. This is not a misreading of the source text, but it may be an *incomplete* compile: the rule as compiled doesn't encode the comparison logic itself, it assumes some upstream process already computed the boolean correctly. Whether that's acceptable (a pre-computed field is legitimate input) or a gap (the engine should derive the comparison itself, the way `003b`'s ratio_threshold checks derive LTV/DTI) is a judgment call for whoever designs the predicate-vs-computed-comparison boundary — flagging, not resolving.

## predicate-09  (POLICY / predicate)

- **source_response**: Sect 8 Housing Vouchers were not used as repayment income
- **plain_english_restatement**: This check fails when a borrower has Section 8 Housing Voucher income that was not included/counted as qualifying repayment income in the loan file; the field 'sect8_voucher_income_included_as_repayment' must be true (i.e., the voucher income was properly applied) for the check to pass.
- **verdict**: correct
- **correction**: (none)
- **reviewer_note**:

## predicate-10  (MISSING / predicate)

- **source_response**: File did not document that the terms of a family loan as source of funds met HUD's criteria
- **plain_english_restatement**: This check fails when the loan file lacks documentation confirming that the terms of a family loan used as a source of funds satisfy HUD's eligibility criteria — specifically, the file must contain evidence (e.g., a signed agreement, gift/loan letter, or underwriter notation) demonstrating compliance with HUD requirements for family loans as an acceptable funds source.
- **verdict**: correct
- **correction**: (none)
- **reviewer_note**:

## predicate-11  (POLICY / predicate)

- **source_response**: Community Second mtg was not obtained from an allowable party and/or all requirements not met
- **plain_english_restatement**: This check flags as CRITICAL when a loan includes a Community Second mortgage that was either sourced from a party not permitted under Fannie Mae guidelines and/or failed to satisfy all applicable Community Second program requirements — the check passes only when both the originating party is allowable AND all requirements are confirmed met.
- **verdict**: correct
- **correction**: (none)
- **reviewer_note**: Source is an "and/or" defect condition (fails on either sub-condition); restatement correctly converts this to "passes only when both hold" — logically equivalent (De Morgan's), correctly handled compound logic.

## predicate-12  (POLICY / predicate)

- **source_response**: A copy of the military leave and earnings statement was not provided
- **plain_english_restatement**: This check flags as CRITICAL when a copy of the borrower's military leave and earnings statement has not been provided in the FHA loan file — it verifies that the document is present and fails if it is absent.
- **verdict**: correct
- **correction**: (none)
- **reviewer_note**:

## predicate-13  (POLICY / predicate)

- **source_response**: The flood insurance deductible requirements as per property type were not met
- **plain_english_restatement**: This check flags as CRITICAL when the flood insurance deductible on the loan file does not satisfy Fannie Mae's required deductible limits for the specific property type (e.g., 1-4 unit, condo, co-op), meaning the boolean field 'flood_insurance_deductible_requirements_met' must be true to pass.
- **verdict**: correct
- **correction**: (none)
- **reviewer_note**:

## predicate-14  (MISSING / predicate)

- **source_response**: Boarders-Documentation verifying history of shared residency/rent payment for 12 mos not provided
- **plain_english_restatement**: This check fails when a loan file includes boarder income but does not contain documentation verifying at least 12 months of shared residency and rent payment history between the borrower and the boarder, as required by Fannie Mae guidelines.
- **verdict**: correct
- **correction**: (none)
- **reviewer_note**:

## predicate-15  (MISSING / predicate)

- **source_response**: No, documentation of manufacturer and contractor warranties for manufactured home is missing
- **plain_english_restatement**: This check flags when the loan file for a manufactured home is missing the required documentation evidencing both the manufacturer warranty and the contractor warranty; it fails/flags whenever that warranty documentation field is not present.
- **verdict**: correct
- **correction**: (none)
- **reviewer_note**:

## predicate-16  (EXPIRED / predicate)

- **source_response**: No, projected income was used  without validating income would begin within 60 days of closing
- **plain_english_restatement**: This check fails when projected (not yet received) income was used in qualifying the borrower but the file lacks documentation or validation confirming that the income would commence within 60 days of the loan closing date.
- **verdict**: correct
- **correction**: (none)
- **reviewer_note**:

## ratio_threshold-00  (THRESHOLD / ratio_threshold)

- **source_response**: Sect 203(h)-Borr did not have a minimum credit score of 500 as required for the program
- **plain_english_restatement**: This check flags when the borrower's credit score falls below 500, which is the minimum required for the FHA Section 203(h) program. NOTE: The underlying metric is a credit score (not LTV or DTI); the ratio_threshold engine kind was assigned upstream and 'ltv' is used here only as the closest structural analogue for a numeric floor threshold.
- **verdict**: correct
- **correction**: (none)
- **reviewer_note**: Restatement correctly identifies the *intent* (credit score >= 500) and honestly discloses the engine_kind force-fit rather than silently misrepresenting it. This is a known, already-logged engine-taxonomy gap (`RESULTS.md`), not a new interpretation failure — `ratio_threshold` currently only models `ltv`/`dti`; a credit-score floor needs its own comparison mechanism, a finding for `003b`, not a compile defect.

## ratio_threshold-01  (THRESHOLD / ratio_threshold)

- **source_response**: Minimum Coverage; deductible; and/ or minimum agency ratings not met
- **plain_english_restatement**: This check flags when the insurance policy on the subject property fails to meet one or more of the required minimums: the coverage amount is insufficient, the deductible exceeds the allowable limit, or the insurer does not meet the minimum agency (e.g., AM Best) rating threshold. Because the engine_kind is ratio_threshold but the underlying condition is not a true LTV or DTI ratio, the LTV ratio mechanism is used as the closest structural analogue — in practice this check should be implemented as a direct comparison of the insurance coverage amount, deductible level, or carrier rating against their respective program-defined minimums.
- **verdict**: correct
- **correction**: (none)
- **reviewer_note**: Same engine-gap disclosure pattern as ratio_threshold-00 — correctly identifies this is actually THREE separate minimums, not one ratio, and says so plainly instead of forcing a false single-number fit.

## ratio_threshold-02  (THRESHOLD / ratio_threshold)

- **source_response**: Lesser of monthly op income or 75% of fair market rent not used for subj rent with limited history
- **plain_english_restatement**: This check flags when, for a subject property with limited rental history, the rental income amount used for qualifying is NOT the lesser of (a) monthly net operating income or (b) 75% of fair market rent — i.e., the qualifying rental income figure on the file exceeds the FHA-required cap of the lower of those two values.
- **verdict**: correct
- **correction**: (none)
- **reviewer_note**: "Lesser-of-X-or-Y not used" correctly restated as "figure exceeds the cap of the lower value" — correct logical inversion, not a misread.

## ratio_threshold-03  (THRESHOLD / ratio_threshold)

- **source_response**: Credit report did not report a payment on a revolving account and 5% of the balance was not used
- **plain_english_restatement**: This check flags when a revolving account on the credit report has no reported payment AND the lender failed to impute a payment equal to at least 5% of the outstanding balance for DTI qualification purposes.
- **verdict**: correct
- **correction**: (none)
- **reviewer_note**: Correctly handled as a compound AND condition (no payment reported AND no 5% imputation), not simplified to one clause.

## ratio_threshold-04  (THRESHOLD / ratio_threshold)

- **source_response**: Auth user act considered w/out evidence co-borr/spouse owns it or borr paid last 12 mos & is in DTI
- **plain_english_restatement**: This check flags when an authorized user account has been counted in the borrower's DTI calculation but the file lacks required supporting evidence — specifically, either proof that a co-borrower or spouse owns the account, or documentation that the borrower personally made the payments on that account for the most recent 12 months.
- **verdict**: correct
- **correction**: (none)
- **reviewer_note**: Dense, abbreviation-heavy source sentence; restatement correctly untangles the OR-condition on evidence types. Same engine-gap disclosure as the other ratio_threshold rows.

## reconcile-00  (MISMATCH / agree_categorical)

- **source_response**: Yes, credit information material conflict(s) was not investigated and resolved appropriately
- **plain_english_restatement**: This check flags as a CRITICAL defect when the loan file contains material conflicts in credit information that were not properly investigated and resolved, as indicated by the field 'credit_material_conflict_investigated_resolved' reflecting a 'Yes' (conflict exists and was not appropriately handled) response on the AMQ.
- **verdict**: ambiguous
- **correction**: (none)
- **reviewer_note**: **Flag for Kayla — the most important finding in this review.** The restatement's *plain-English content* is accurate, but the `engine_kind=agree_categorical` (a doc-vs-system comparison) doesn't match what this condition actually is: a single process/compliance question ("was a conflict investigated and resolved?"), not a two-independent-source agreement test. There is no second source to reconcile against here. This looks like a `taxonomy.py` classification issue — the word "conflict" pattern-matched the MISMATCH archetype's regex, but the underlying condition is closer to a POLICY predicate. Same concern as `reconcile-01` below (2 of 2 reconcile-kind samples show this pattern) — worth a taxonomy.py regex review, separate from the LLM compiler's own performance.

## reconcile-01  (MISMATCH / agree_categorical)

- **source_response**: SFC 162 not used where there was a discrepancy identified with the Social Security number
- **plain_english_restatement**: This check fails when a Social Security number discrepancy has been identified on the loan but Special Feature Code 162 was not applied — it compares the expected categorical value (SFC 162 present/used) against the actual coded value on the loan record, flagging any case where the code is absent despite a documented SSN discrepancy.
- **verdict**: ambiguous
- **correction**: (none)
- **reviewer_note**: Same concern as `reconcile-00`. This reads as a conditional compliance rule ("if an SSN discrepancy was found, SFC 162 must be applied"), not a doc-vs-system reconciliation — there's no second independent source being compared. `taxonomy.py`'s "discrepancy" keyword match likely misclassified this into the MISMATCH archetype. Both reconcile-kind rows in this sample show the same issue — small N (2), but 2-for-2 is a real signal, not noise.
