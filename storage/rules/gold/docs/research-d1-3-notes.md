# Verified research notes — Fannie post-closing QC (run wf_bc23911d-efb, 2026-07-30 night)

Status: partial. 6 claims CONFIRMED (3-0 adversarial votes, official selling-guide.fanniemae.com).
~19 further claims drafted but unverified (session limit hit; verification resumes after 3:30am CT).

## Confirmed (safe to build on)

1. **Chapter D1-3 has exactly THREE sections** (older D1-3-04/-05/-06 are RETIRED — any rule citing
   them is a citation-drift compile failure):
   - D1-3-01, Lender Post-Closing Quality Control Review Process
   - D1-3-02, Lender Post-Closing Quality Control Review of Approval Conditions, Underwriting
     Decisions, Data, and Documentation (04/01/2026)
   - D1-3-03, Lender Post-Closing Quality Control Reverifications
2. **D1-3-02 minimum review scope** — canonical topic skeleton for check categories: application
   accuracy/completeness; underwriting docs supporting credit/income/assets incl. reverifications +
   data integrity review; support for underwriting decision; DU data entry; appraisal/collateral;
   property + project eligibility; property/flood insurance; MI coverage; legal/transaction/closing
   docs; compliance with laws.
3. **DU-underwritten loans**: QC must confirm every DU Verification Message/Approval Condition in
   the DU Findings report was resolved + documented — itemizable per-message deterministic checks.
4. **Deterministic discrepancy workflow** keyed to DU tolerances (B3-2-10): beyond-tolerance data
   -> resubmit to DU (or manual re-risk for non-DU), eligibility determination, self-report
   ineligible via Loan Quality Connect; failure to resubmit invalidates the DU limited waiver.

## Verified LOCALLY from guide/sections/D1-3-01.txt (2026-07-31, deterministic grep — stronger than web)

5. **Selection cadence**: loans selected for post-closing QC "on at least a monthly basis"; the
   entire QC cycle (selection, review, rebuttal, reporting) completes "within 90 days from the month
   of the disbursement date".
6. **Random sample sizing**: minimum 10% of monthly production, OR a statistically valid sample at
   95% confidence / 2% precision with a six-month statistical statement; if 10% < 1 loan, at least
   one loan. Component reviews vs full-file reviews distinguished in the same section.
7. D1-3-02 subsection taxonomy (web-confirmed 3-0): Overview; Review of Underwriting Decision and
   Approval Conditions; Review of DU Findings and Conditions; Verification of Data; Review of
   Potential Red Flag and Alert Messages; Review of Social Security Numbers; Review of Transaction
   and Closing Documents.

## Still unverified (web run limit-killed twice; NOT blocking — local guide text is the primary source now)

- Form 1032/1033 official item structures (we have the ACES Form 1033 card battery as ground truth anyway)
- Forms 1084/1088/1038/1039 worksheet encodings (needed for Income decomposition depth, fetch as needed)
- D1-3-03 reverification enumeration — read guide/sections/D1-3-03.txt directly instead.
