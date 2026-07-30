# Path 1 Corrected Results: Credit-Liabilities UndisclosedLiabilityShape Mapping

## Executive Summary

**Finding:** No O-FNM or GENERIC undisclosed-liability rule exists in the Post-Closing AMQ workbook that matches UndisclosedLiabilityShape's condition.

**Root cause:** The original agent suggestion (O-VA-00133) was agency-specific (VA only) and would be filtered out by program filtering for Fannie Mae loan 01 (O-FNM).

**Search conducted:**
1. Scanned all Credit-Liabilities rules for O-FNM codes containing "undisclosed" or "liability"
2. Searched for GENERIC (no agency prefix) rules about undisclosed liabilities
3. Examined debt/liability discrepancy rules between credit report and 1003

## What UndisclosedLiabilityShape Checks

From the existing SHACL shape (decision 002's original pilot):
- **Condition:** Credit report shows a tradeline (debt/liability) that does NOT appear in the 1003 Section 2c (liabilities section)
- **Defect:** Borrower failed to disclose a debt they actually have
- **Business impact:** Understated DTI ratio → loan may not have qualified with correct DTI

## AMQ Rules Found

### O-VA-00133 (Original Suggestion — NOT VIABLE)
- **Agency:** VA only
- **Exception text:** "A debt is reported on the credit report or from another source that was not disclosed on the application and a written clarification was not obtained from the borrower."
- **Why rejected:** Loan 01 is O-FNM (Fannie Mae conventional), so O-VA rules won't fire due to program filtering (decision 010)

### O-FHA-02232, O-FHA-02233, O-FHA-02234 (FHA Manual/AUS Variants)
- **Agency:** FHA only
- **Exception text variants:**
  - "In a manual underwrite where an undisclosed debt is revealed, the debt was not documented and/or the payment was not included in the ratios." (O-FHA-02234)
  - "Undisclosed non-mortgage obligation revealed without actual payment verified/resubmitted to TOTAL when new payment exceeds tolerance" (O-FHA-02232)
  - "Undisclosed mortgage not in TOTAL w/ unacceptable pay history not downgraded to Refer" (O-FHA-02233)
- **Why rejected:** FHA-specific, won't fire for O-FNM loans

### O-RHS-50563, O-RHS-50564, O-RHS-02826, O-RHS-57144 (USDA Variants)
- **Agency:** USDA only
- **Exception text variants:**
  - "Manual underwrite where credit report reflects significant debt not on application → LOX not provided and/or debt not added to DTI" (O-RHS-50563)
  - "Significant debt not considered by GUS & payment not added/loan resubmitted" (O-RHS-50564)
  - "Recent non-disclosed significant debt on credit report not explained" (O-RHS-02826)
  - "Undisclosed debt not listed on application but discovered during processing not manually entered into GUS" (O-RHS-57144)
- **Why rejected:** USDA-specific, won't fire for O-FNM loans

### O-FNM-00191 — INVERSE CONDITION (Closest O-FNM Rule Found)
- **Row:** 894
- **Exception code:** O-FNM-00191
- **Exception name:** "Credit Report Unreported Debts"
- **Question text:** "Were all other monthly debt obligations requirements met?"
- **Response text:** "No written verification for significant open debt(s) on the application but not on the credit report"
- **Exception description:** "The credit report does not include a reference for each significant open debt listed on the application, and a separate written verification for each unreported debt was not obtained."
- **Current eval_class:** `unmapped`
- **Why not mapped:** This checks the **opposite direction** — debts **on the 1003 but NOT on the credit report** (credit bureau failed to report), while UndisclosedLiabilityShape checks debts **on the credit report but NOT on the 1003** (borrower failed to disclose).

## Conclusion

**No O-FNM or GENERIC rule in the Post-Closing AMQ workbook matches UndisclosedLiabilityShape's condition (credit-report tradeline with no matching 1003 Section 2c entry).**

All undisclosed-liability rules found are agency-specific:
- O-VA-00133 (VA)
- O-FHA-02232/02233/02234 (FHA)
- O-RHS-50563/50564/02826/57144 (USDA)
- O-FRD has no undisclosed-liability rule in the Post-Closing sheet

The closest O-FNM rule (O-FNM-00191) checks the inverse condition and is currently `unmapped`.

## Implications for Loan 01 Defect Detection

Loan 01's defect manifest (`demo/syn/loan 01/defect_manifest.json`) lists:
```json
{
  "defect_id": "df_004_undisclosed_liab",
  "description": "Credit report shows a $15,000 personal loan (opened 2021-03) not disclosed on the 1003 Section 2c",
  ...
}
```

**Current state:** UndisclosedLiabilityShape (the existing SHACL check from decision 002's pilot) successfully detected this defect in the 5/5 GREEN-rule success run (decision 026). It is NOT blocked by missing AMQ mapping — it runs as a standalone SHACL shape.

**Impact of this Path 1 finding:** Zero. The shape already works. This finding documents the honest truth: **the AMQ workbook (Post-Closing sheet) does not contain an O-FNM or GENERIC rule for this condition.** The defect is caught by the hand-mapped SHACL shape, not by an AMQ-compiled rule.

## Recommendation

**Do NOT attempt to force-map O-FNM-00191 to UndisclosedLiabilityShape.** They check opposite conditions:
- UndisclosedLiabilityShape: `credit_report.tradelines[x] NOT IN loan.section_2c_liabilities` (borrower hid a debt)
- O-FNM-00191: `loan.section_2c_liabilities[y] NOT IN credit_report.tradelines` (credit bureau missed a debt)

Both are valid, orthogonal checks. If a future pass adds O-FNM-00191 as a distinct shape, name it `UnreportedDebtShape` or `CreditReportGapShape`, not UndisclosedLiabilityShape.

## Path 1 Status

**COMPLETE.** Honest finding documented: no O-FNM/GENERIC undisclosed-liability rule exists. The defect is caught by the existing hand-mapped shape, not by AMQ compilation.
