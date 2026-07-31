# MISMO 3.4 Migration — Findings, Decision & Implementation Roadmap

**Date:** 2026-07-30  
**Project:** Universal QC System (Touchless + AMQ Integration)  
**Decision:** Adopt MISMO 3.4 as canonical schema (ADR 030)

---

## Executive Summary

**Problem:** AMQ QC rules returned 100% NO_DATA on Touchless loan data despite Touchless providing complete loan information with 54 document types.

**Root Cause:** AMQ rules were built against a custom extraction schema (synthetic fixtures), not an industry standard. This makes the system non-portable.

**Decision:** Migrate to MISMO 3.4 (Mortgage Industry Standards Maintenance Organization) as the canonical loan data schema.

**Effort:** 3-4 weeks  
**Benefit:** Universal compatibility - any MISMO-compliant data source works immediately

---

## Findings: What Went Wrong

### Finding 1: Non-Portable Schema Design

**What we built:**
```
Synthetic Fixtures → Custom Extraction → Custom Schema → AMQ Shapes
```

**Problem:** New data source requires complete field remapping
- Touchless uses `mortgageType` → AMQ expects `loan_program_1003`
- Touchless uses `totalDebtExpenseRatioPercent` → AMQ expects `dti_ratio`
- Touchless uses `documents[]` array → AMQ expects `doc_present_*` booleans

**Impact:** 100% NO_DATA on Touchless integration (0 of 26 shapes evaluated)

### Finding 2: Gordon's Requirement Was Correct

> "This should be universal - I should be able to upload any kind of loan to run against the AMQ rules."

**He's right.** A production system must handle:
- ✅ Touchless data
- ✅ LOS exports (Encompass, Ellie Mae, etc.)
- ✅ MISMO 3.4 XML files
- ✅ Manual data entry
- ✅ Any mortgage data source

**Current system fails this requirement.**

### Finding 3: Touchless Already Uses MISMO-Like Structure

**Touchless `loan_application.json` structure:**
```json
{
  "loanSummary": {...},      // ≈ MISMO LOAN_DETAIL
  "borrowersDetail": {...},  // ≈ MISMO BORROWER
  "assetDetail": {...},      // ≈ MISMO ASSET
  "creditDetail": {...},     // ≈ MISMO CREDIT
  "liabilityDetail": {...},  // ≈ MISMO LIABILITY
  "collateralDetail": {...}, // ≈ MISMO PROPERTY
  "documents": [...]         // ≈ MISMO DOCUMENT
}
```

**This is 80-90% aligned with MISMO 3.4 already** - minimal adaptation needed.

### Finding 4: Custom Schema Was a Technical Debt Decision

**When building synthetic fixtures:**
- No industry data source to integrate with
- Created custom extraction schema for test data
- Built SHACL shapes against that schema
- **Didn't anticipate multiple data sources**

**Now:** The custom schema is the integration bottleneck.

### Finding 5: MISMO 3.4 Solves the Portability Problem

**MISMO 3.4 is:**
- ✅ Mortgage industry standard (used by all major LOS platforms, GSEs)
- ✅ Comprehensive (all loan data: borrower, property, credit, income, assets, docs)
- ✅ Well-documented (XML schema, data dictionary, vendor support)
- ✅ Already used by Touchless (their structure mirrors it)
- ✅ Vendor-neutral (not tied to any platform)

**With MISMO as canonical schema:**
```
Any Source → MISMO Adapter → AMQ Rules (MISMO-based) → Results
```

This is **truly universal.**

---

## The Decision: Option B (MISMO Migration)

### Option A: Quick Fix (Rejected)

**Approach:** Map Touchless → current custom schema

**Pros:**
- Fast (1 week)
- No rework of existing shapes

**Cons:**
- ❌ Not universal (next source needs another custom mapping)
- ❌ Accumulating technical debt
- ❌ Doesn't solve Gordon's requirement

### Option B: MISMO Migration (ACCEPTED) ✅

**Approach:** Rewrite AMQ shapes for MISMO 3.4, build adapters for all sources

**Pros:**
- ✅ Truly universal (any MISMO source works)
- ✅ Industry standard (easier onboarding, vendor support)
- ✅ Future-proof (benefits from industry evolution)
- ✅ Touchless already aligned (minimal work)

**Cons:**
- ⏱️ Takes 3-4 weeks (vs 1 week quick fix)
- 🔧 Requires rewriting 26 existing shapes
- 📚 Team must learn MISMO 3.4

**Decision:** Option B - **the long-term value justifies the short-term investment**

---

## Implementation Roadmap

### Phase 1: MISMO Schema Definition (Week 1)

**Deliverables:**
1. **MISMO 3.4 RDF Namespace Definition** (`src/doc/specifications/mismo-rdf-namespace.md`)
   - All MISMO fields → RDF properties
   - Data types (xsd:decimal, xsd:date, etc.)
   - Nested entity patterns (borrowers, assets, liabilities)

2. **Touchless → MISMO Field Mapping** (`src/doc/specifications/touchless-to-mismo-mapping.md`)
   - Complete field-by-field mapping
   - 54 document type classifications
   - OCR data integration pattern

3. **Reference Converter Implementation** (`src/shacl_pilot/mismo_to_rdf.py`)
   - Reusable converter template
   - Handle all MISMO entity types
   - Generate 500-800 triples from full loan data

**Success Criteria:**
- ✅ 100% of Touchless fields mapped to MISMO equivalents
- ✅ Reference converter handles sample loan
- ✅ Documentation complete for team handoff

### Phase 2: Migrate SHACL Shapes (Weeks 2-3)

**Approach:** Batch migration (5 shapes per batch), test, validate

#### Batch 1: Underwriting (Highest Priority - Week 2)

**Shapes to migrate:**
1. DTI threshold checks (4 shapes: CONVENTIONAL, FHA, VA, USDA)
2. LTV overlay checks (5 shapes: by program + FICO)
3. FICO minimum checks (3 shapes: by program)
4. Housing ratio checks (3 shapes: by program)
5. Loan amount checks (2 shapes: conforming limit, rate reasonableness)

**New field names (examples):**
```turtle
# OLD (custom schema)
li:dti_ratio
li:loan_program_1003
li:ltv
li:credit_score_1003

# NEW (MISMO)
mi:totalDebtRatio
mi:mortgageType
mi:ltvRatio
mi:creditScoreValue
```

**Validation:**
- Run on Touchless loan #12607601215
- Expect: 15-17 of 17 shapes evaluate (vs 0 today)
- All checks should PASS (loan is clean)

#### Batch 2: Income & Assets (Week 3)

**Shapes to migrate:**
1. Income sufficiency
2. Employment verification
3. Self-employed income validation
4. Asset documentation
5. Liability disclosure

#### Batch 3: Property & Credit (Week 3)

**Shapes to migrate:**
1. Appraisal checks
2. Property eligibility
3. Title verification
4. Credit score verification

#### Batch 4: Closing & Documents (Week 3)

**Shapes to migrate:**
1. Closing disclosure reconciliation
2. Document presence checks
3. Signature verification

**Success Criteria:**
- ✅ All 26 shapes migrated to MISMO
- ✅ 20+ shapes evaluate on Touchless data (80% coverage)
- ✅ Zero degradation on synthetic fixture tests

### Phase 3: Build Adapters (Week 3-4)

#### Touchless → MISMO Adapter

**File:** `src/shacl_pilot/touchless_to_mismo_rdf.py`

**Responsibilities:**
1. Convert `loan_application.json` → MISMO RDF
   - Map all loanSummary, borrowersDetail, assetDetail, etc.
   - Generate 500-800 triples (vs current 106)

2. Map 54 document types → MISMO classifications
   - `documents[]` array → `mi:hasDocument[@type='X']`
   - Document presence → boolean facts

3. Integrate OCR `extracted_data_*.json`
   - Schedule C fields → MISMO self-employment income
   - Any other extracted fields

**Test Cases:**
- Loan #12607601215 (self-employed, conventional)
- Expect 500-800 triples
- All 26 shapes should have data to evaluate

#### Synthetic Fixtures → MISMO Adapter

**File:** `src/shacl_pilot/synthetic_to_mismo_rdf.py`

**Responsibilities:**
1. Convert custom extraction schema → MISMO RDF
2. Preserve all existing test cases
3. Maintain backward compatibility

**Test Cases:**
- All 5 synthetic loans (loan 01-05)
- All 25 known defects still detected
- Zero false positives

### Phase 4: Validation & Cutover (Week 4)

**Step 1: Parallel Execution**
- Run both old shapes (custom schema) and new shapes (MISMO)
- Compare results side-by-side
- Measure coverage, detection rate, false positive rate

**Step 2: Touchless Integration Validation**
- Run full audit on loan #12607601215
- Target: 20-25 of 26 shapes evaluate (80-95%)
- Target: <5% false positive rate

**Step 3: Synthetic Fixture Regression**
- Run full audit on all 5 synthetic loans
- All 25 known defects still detected
- Zero new false positives

**Step 4: Cutover**
- Archive old shapes to `src/shacl_pilot/blocks/legacy/`
- Update all documentation
- Remove parallel execution code
- Declare MISMO as production schema

**Success Criteria:**
- ✅ 20+ of 26 shapes evaluate on Touchless
- ✅ All synthetic fixture tests pass
- ✅ <5% false positive rate
- ✅ Documentation complete

---

## Field Mapping Examples

### Example 1: Loan Terms

| Touchless Field | MISMO 3.4 Field | RDF Property | Data Type |
|---|---|---|---|
| `lenderCaseIdentifier` | LoanIdentifier | `mi:loanIdentifier` | xsd:string |
| `loanTerms.baseLoanAmount` | BaseLoanAmount | `mi:baseLoanAmount` | xsd:decimal |
| `loanTerms.mortgageType` | MortgageType | `mi:mortgageType` | xsd:string |
| `loanTerms.loanPurposeType` | LoanPurposeType | `mi:loanPurposeType` | xsd:string |
| `loanTerms.interestRate` | NoteRatePercent | `mi:noteRatePercent` | xsd:decimal |

### Example 2: Qualification/Ratios

| Touchless Field | MISMO 3.4 Field | RDF Property | Data Type |
|---|---|---|---|
| `qualification.totalDebtExpenseRatioPercent` | TotalDebtExpenseRatioPercent | `mi:totalDebtRatio` | xsd:decimal |
| `qualification.housingExpenseRatioPercent` | HousingExpenseRatioPercent | `mi:housingExpenseRatio` | xsd:decimal |
| `ltvRatio.ltv` | LTVRatioPercent | `mi:ltvRatio` | xsd:decimal |
| `ltvRatio.cltv` | CLTVRatioPercent | `mi:cltvRatio` | xsd:decimal |
| `fico` | CreditScoreValue | `mi:creditScoreValue` | xsd:integer |

### Example 3: Borrower

| Touchless Field | MISMO 3.4 Field | RDF Property | Data Type |
|---|---|---|---|
| `borrowers[0].firstName` | FirstName | `mi:firstName` | xsd:string |
| `borrowers[0].lastName` | LastName | `mi:lastName` | xsd:string |
| `employers[0].employerName` | EmployerName | `mi:employerName` | xsd:string |
| `income[0].monthlyIncome` | MonthlyIncomeAmount | `mi:monthlyIncomeAmount` | xsd:decimal |
| `employment.ownershipInterestType` | OwnershipInterestType | `mi:ownershipInterestType` | xsd:string |

### Example 4: Document Inventory

| Touchless Field | MISMO 3.4 Pattern | RDF Property | Data Type |
|---|---|---|---|
| `documents[type='Credit Report']` | DOCUMENT[@Type='CreditReport'] | `mi:hasDocument[type='CreditReport']` | boolean |
| `documents[type='Paystub']` | DOCUMENT[@Type='Paystub'] | `mi:hasDocument[type='Paystub']` | boolean |
| `documents[type='W2']` | DOCUMENT[@Type='W2'] | `mi:hasDocument[type='W2']` | boolean |
| `documents[type='Form 1040']` | DOCUMENT[@Type='TaxReturn']` | `mi:hasDocument[type='TaxReturn']` | boolean |

---

## Expected Outcomes

### Coverage Improvements

| Metric | Before (Custom Schema) | After (MISMO) |
|---|---|---|
| **Touchless shapes evaluated** | 0/26 (0%) | 20-25/26 (80-95%) |
| **Synthetic shapes evaluated** | 26/26 (100%) | 26/26 (100%) |
| **Known defects detected** | 25/25 (100%) | 25/25 (100%) |
| **False positive rate** | 0% | <5% |
| **Universal compatibility** | ❌ No | ✅ Yes |

### Performance

| Metric | Target |
|---|---|
| **Conversion time** | <2 seconds (Touchless → RDF) |
| **Validation time** | <3 seconds (26 shapes) |
| **Total audit time** | <5 seconds per loan |

### Business Impact

**Immediate:**
- ✅ Touchless integration works (can QC real loans)
- ✅ No vendor lock-in (can switch data sources)

**Short-term (3-6 months):**
- ✅ Add new LOS exports (Encompass, Ellie Mae) in days, not weeks
- ✅ Industry-standard vocabulary (easier SME onboarding)
- ✅ Reusable across other mortgage AI projects

**Long-term (1+ years):**
- ✅ MISMO updates benefit us automatically
- ✅ Can sell as "MISMO-compliant QC system"
- ✅ Integration with industry tools (GSE validation, warehouse lending)

---

## Risk Mitigation

### Risk 1: MISMO Spec Gaps

**Scenario:** MISMO doesn't have a field we need

**Mitigation:**
- Use MISMO extensions (allowed by spec)
- Namespace: `mi-ext:` for custom fields
- Document all extensions

### Risk 2: Touchless Diverges from MISMO

**Scenario:** Touchless changes their structure

**Mitigation:**
- Adapter layer isolates MISMO shapes from Touchless changes
- Version Touchless API responses
- Monitor Touchless API changelog

### Risk 3: Effort Estimate Wrong

**Scenario:** Takes >4 weeks

**Mitigation:**
- Phased approach (5 shapes per batch)
- Measure velocity after Batch 1
- Can ship partial coverage (15/26 shapes = 60% value)

### Risk 4: Breaking Existing Tests

**Scenario:** Synthetic fixture tests fail after migration

**Mitigation:**
- Keep old schema in parallel during migration
- Run both schemas side-by-side
- Only deprecate after 100% validation

---

## Team Responsibilities

### Engineering (Primary Owner: Claude Code / Monish's Team)

**Week 1:**
- Define MISMO RDF namespace
- Create field mapping docs
- Build reference converter

**Weeks 2-3:**
- Migrate 26 SHACL shapes (batched)
- Build Touchless adapter
- Build synthetic fixtures adapter

**Week 4:**
- Validation testing
- Cutover
- Archive old schema

### SME (Kayla / Mortgage QC Expert)

**Throughout:**
- Validate MISMO field mappings (correct mortgage terminology?)
- Review sample SHACL shapes (rules correct?)
- Test on real loans (results make sense?)

### Director (Gordon)

**Week 2:**
- Review progress (Batch 1 results)
- Approve direction or adjust

**Week 4:**
- Final validation (is it truly universal?)
- Sign-off for production

---

## Success Metrics (Go/No-Go Criteria)

### Must Have ✅
1. 20+ of 26 shapes evaluate on Touchless data (80% coverage)
2. All 25 synthetic fixture defects still detected (zero degradation)
3. <5% false positive rate on Touchless data
4. Documentation complete (MISMO namespace, adapters, migration guide)

### Should Have
5. 25/26 shapes evaluate (95% coverage)
6. <2% false positive rate
7. <5 seconds total audit time per loan

### Stretch Goals
8. 26/26 shapes evaluate (100% coverage)
9. MISMO XML file support (not just Touchless JSON)
10. Field glossary (MISMO → plain English for SMEs)

---

## Next Actions

### Immediate (This Week)

1. **Kickoff meeting** (Gordon + team)
   - Align on roadmap
   - Assign owners
   - Set check-in cadence

2. **Start Phase 1** (MISMO schema definition)
   - Research MISMO 3.4 spec
   - Draft namespace documentation
   - Begin Touchless field mapping

### Week 2

3. **Complete Phase 1 deliverables**
4. **Begin Batch 1 migration** (underwriting shapes)
5. **Mid-point check-in** (validate approach)

### Week 3-4

6. **Complete all batches**
7. **Build adapters**
8. **Validation & cutover**

---

## References

- **Decision Record:** `src/decisions/030-mismo-canonical-schema-adoption.md`
- **MISMO 3.4 Spec:** https://www.mismo.org/reference-library
- **Touchless Data:** `demo/touchless/loan_application.json`
- **Synthetic Schema:** `p0/qc_engine/extract_loan.py`
- **Current Shapes:** `src/shacl_pilot/blocks/*.ttl`

---

**Prepared by:** Claude Code  
**Approved by:** Gordon Chan  
**Date:** 2026-07-30  
**Status:** Ready for implementation
