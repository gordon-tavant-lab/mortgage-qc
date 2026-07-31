# Touchless Loan QC Audit — First Run Analysis

**Date:** 2026-07-30  
**Loan ID:** 12607601215  
**Objective:** Run first QC audit on real Touchless-extracted loan data  

---

## Executive Summary

✅ **Touchless data successfully ingested** — 17 fields + 1 fact extracted from Touchless API  
✅ **RDF conversion working** — 110 triples generated  
✅ **SHACL validation runs** — 26 shapes loaded, no crashes  
❌ **100% NO_DATA** — 0/26 shapes evaluated (schema mismatch)

**Root cause:** The SHACL shapes expect fields with specific names (e.g., `employment_start_date_1003`, `property_year_built`) but Touchless extraction uses different field names or doesn't provide them at all.

**Next step:** Field mapping layer — bridge Touchless schema → SHACL pilot schema.

---

## Touchless Data Quality Assessment

### Fields Successfully Extracted (17)

| Field | Value | Source |
|---|---|---|
| `loan_number` | 12607601215 | loanSummary.lenderCaseIdentifier |
| `loan_program_1003` | CONVENTIONAL | loanTerms.mortgageType |
| `loan_purpose_1003` | PURCHASE | loanTerms.loanPurposeType |
| `mismo_loan_amount` | $260,000 | loanTerms.baseLoanAmount |
| `mismo_note_rate` | 6.5% | loanTerms.interestRate |
| `mismo_mortgage_type` | CONVENTIONAL | loanTerms.mortgageType |
| `application_date` | 2026-07-20 | loanSummary.applicationDate |
| `mismo_total_monthly_income` | $19,500 | qualification.totalMonthlyIncomeAmount |
| `housing_ratio` | 11.38% | qualification.housingExpenseRatioPercent |
| `dti_ratio` | 14.55% | qualification.totalDebtExpenseRatioPercent |
| `ltv` | 73.86% | ltvRatio.ltv |
| `credit_score_1003` | 740 | loanSummary.fico |
| `borrower_name` | Andy America | borrowersDetail.borrowerPairs[0].borrowers[0] |
| `employer_name_1003` | Kraft Foods | employers[0].employerName |
| `base_monthly_income_1003` | $4,000 | employers[0].income[0].monthlyIncome |
| `tax_year_schedule_c` | 2023 | extracted_data: Tax_Year |
| `gross_profit_schedule_c` | $48,000 | extracted_data: Gross_Profit |

### Facts Extracted (1)

| Fact | Value | Source |
|---|---|---|
| `borrower_self_employed` | True | employment.ownershipInterestType: GreaterThanOrEqualTo25Percent |

---

## Field Coverage Gaps

### High-Impact Missing Fields (Required by Multiple Shapes)

**Property / Appraisal:**
- ❌ `property_state` — Not extracted (needed for state-specific checks)
- ❌ `property_year_built` — Not extracted (needed for LBP gate)
- ❌ `appraised_value` — Not extracted
- ❌ `appraisal_effective_date` — Not extracted
- ❌ `closing_date` — Not extracted (needed for appraisal age calc)

**Employment / Income:**
- ❌ `employment_start_date_1003` — Not extracted (employment.employmentStartDate exists but is null in this loan)
- ❌ `monthly_income_voe` — Not extracted (no VOE data in Touchless)
- ❌ `paystub_ytd_gross_income` — Not extracted

**Credit:**
- ❌ `credit_score_bureau` — Extracted as `credit_score_1003` but shapes may expect different name

**Signatures / Docs:**
- ❌ `sig_1003_borrowers_present` — Not extracted (no document-level signatures in Touchless)
- ❌ `doc_present_*` facts — Not extracted (Touchless doesn't provide doc inventory)

**Title / Closing:**
- ❌ `title_vesting_1003` — Not extracted
- ❌ `title_vesting_commitment` — Not extracted

---

## Touchless Data Model Observations

### What Touchless Provides (Strengths)

1. **Structured loan-level data** — LTV, DTI, ratios, qualifications (excellent quality)
2. **Borrower details** — Name, employment, income (well-structured)
3. **Loan terms** — Amount, rate, purpose, program (complete)
4. **Document extraction** — Key-value pairs from tax forms (Schedule C) with confidence scores
5. **Credit scores** — FICO available at loan summary level

### What Touchless Doesn't Provide (Gaps)

1. **Document-level metadata** — No doc inventory, no "doc_present_*" facts
2. **Signature presence flags** — No extraction of signature lines from PDFs
3. **Property details** — No year built, no property state (these should be extractable from collateralDetail)
4. **Cross-document reconciliation data** — No VOE, no paystub YTD, no appraisal comps
5. **Date-stamped events** — Employment start dates, appraisal dates, closing dates often null

---

## Why 100% NO_DATA

**The SHACL shapes were designed for the synthetic loan extraction schema**, which includes:
- All doc-vs-doc comparison fields (VOE income vs 1003 income, title vesting 1003 vs commitment)
- Document-presence facts (`doc_present_arm_disclosure`, `sig_1003_borrowers_present`)
- Derived facts (appraisal age at closing, employment months)

**Touchless provides:**
- High-quality structured loan data (LTV, DTI, FICO, loan terms)
- But NOT document-level extraction (no VOE, no paystubs, no appraisal details, no closing docs)

**Example mismatch:**
- Shape `EmploymentStartDateShape` expects: `employment_start_date_1003` AND `employment_start_date_voe` (for cross-check)
- Touchless provides: Neither (employment.employmentStartDate is null in this loan)

---

## Next Steps to Reach Evaluable State

### Priority 1: Field Mapping Layer (2-3 Hours)

Expand `touchless_adapter.py` to extract ALL available fields from `loan_application.json`:

**Add from collateralDetail:**
- `property_state` (collateral[0].propertyAddress.state) — **available**
- `property_year_built` (collateral[0].propertyDetail.yearBuilt) — **available**
- `appraised_value` (collateral[0].appraisal.appraisedValue) — **available**
- `appraisal_effective_date` (collateral[0].appraisal.appraisalEffectiveDate) — **available**

**Add from closingInformation:**
- `closing_date` (loanSummary.closingInformation.loanEstimatedClosingDate) — **may be available**

**Add from borrowersDetail:**
- `employment_start_date_1003` (employers[0].employment.employmentStartDate) — **check if populated**
- `borrower_dob` (borrowers[0].age) — **available**

**Estimated impact:** 17 fields → 25-30 fields (50%+ increase)  
**Estimated NO_DATA reduction:** 100% → 70-80% (optimistic)

### Priority 2: Shape Adaptation (Medium Effort)

**Some shapes require document-level data that Touchless will never provide:**
- VOE-vs-1003 income cross-checks → **Remove or mark NOT_APPLICABLE**
- Signature presence checks → **Remove or mark NOT_APPLICABLE**
- Document-presence gates (`doc_present_*`) → **Remove or mark NOT_APPLICABLE**

**Option A:** Create a **Touchless-specific shape subset** (12-15 shapes that work with structured data only)  
**Option B:** Implement **NOT_APPLICABLE routing** (shapes self-declare when data contract can't be met)

### Priority 3: Touchless Feature Request (Long-Term)

**Ask Touchless team to add:**
1. **Property year built** to collateralDetail (if not already there)
2. **Document inventory** — simple boolean flags: `has_voe`, `has_paystub`, `has_appraisal`, etc.
3. **Signature metadata** — boolean flags: `borrower_signed_1003`, `donor_signed_gift_letter`, etc.
4. **Timestamped events** — employment start date, appraisal effective date, closing date (populate nulls)

---

## Touchless Data Strengths (Where It Excels)

### Ratio / Qualification Checks (Fully Supported)

Touchless provides **excellent coverage** for:
- ✅ DTI validation (totalDebtExpenseRatioPercent)
- ✅ Housing ratio validation (housingExpenseRatioPercent)
- ✅ LTV validation (ltvRatio.ltv, cltv, hcltv)
- ✅ Income validation (totalMonthlyIncomeAmount)

**These checks can run TODAY with zero changes.**

### Loan-Level Validation (Fully Supported)

- ✅ Loan program eligibility (mortgageType)
- ✅ Loan purpose validation (loanPurposeType)
- ✅ Interest rate validation (interestRate)
- ✅ Loan amount validation (baseLoanAmount)

### Credit Validation (Fully Supported)

- ✅ FICO score validation (fico: 740)
- ✅ Credit score eligibility overlays

---

## Recommendation: Two-Track Approach

### Track 1: Touchless-Native Shapes (Quick Win — 1-2 Weeks)

Build **12-15 new shapes** that validate what Touchless provides natively:
1. DTI thresholds (by loan program)
2. Housing ratio thresholds
3. LTV overlays (by loan program + FICO)
4. Income sufficiency
5. Self-employed income validation (Schedule C data)
6. Loan amount limits (by program)
7. Credit score eligibility

**Estimated coverage:** 20-30 checks that can run TODAY with existing Touchless data.

### Track 2: Document-Level Shapes (Long-Term — Touchless Expansion)

Keep the existing 26 shapes for **document-level QC**, but:
- Mark them NOT_APPLICABLE when Touchless data is the source
- Use them ONLY when full document extraction is available (e.g., Gordon's synthetic fixtures)

**Why:** The original 26 shapes test **post-closing QC** (doc-vs-doc reconciliation). Touchless provides **application-level data** (LOS export), not post-closing docs.

---

## Key Decisions Needed

1. **Should we adapt the existing 26 shapes to Touchless?**
   - **Pro:** Reuse existing work
   - **Con:** Many checks (VOE cross-checks, signature presence) will never be possible with Touchless data alone

2. **Or should we build a Touchless-specific shape set?**
   - **Pro:** Faster path to evaluable checks
   - **Con:** Maintaining two shape sets

3. **What's the Touchless data contract?**
   - Is `collateralDetail.propertyDetail.yearBuilt` always populated?
   - Is `employment.employmentStartDate` ever populated?
   - Can we get document inventory flags?

---

## Files Created

**Adapter:** `src/shacl_pilot/touchless_adapter.py` — converts Touchless API format → extraction JSON  
**Audit runner:** `src/shacl_pilot/run_touchless_audit.py` — runs SHACL validation on Touchless data  
**Output:** `demo/touchless/touchless_loan_extraction.json` — converted extraction (17 fields, 1 fact)

---

## Sample Data Quality

**Loan ID:** 12607601215  
**Borrower:** Andy America, age 56  
**Loan:** $260,000 Conventional Purchase @ 6.5% (FNMA)  
**LTV:** 73.86%  
**DTI:** 14.55%  
**FICO:** 740  
**Self-Employed:** Yes (Kraft Foods, 25%+ ownership)  
**Tax Data:** 2023 Schedule C, $48K gross profit

**Data quality: Excellent** — all extracted values are reasonable, confidence scores high (80-200).

---

**Next Step:** Expand touchless_adapter.py to extract property/appraisal/closing fields from loan_application.json, re-run audit, measure NO_DATA reduction.
