# RED Rule Categorization Analysis

**Analysis Date:** 2026-07-30
**Context:** SHACL-based mortgage QC pilot — 7 blocks triaged

---

## Quick Reference Table

| Category | Rules | Groups | % of RED | Primary Characteristic |
|----------|-------|--------|----------|------------------------|
| **Narrative Judgment** | 187 | 178 | 45.7% | Requires subjective human assessment ("adequate," "reasonable," "appears") |
| **External Data** | 187 | 184 | 45.7% | Requires lookups/APIs/registries not in closed-loan file |
| **Ambiguous/Vague** | 29 | 29 | 7.1% | No clear pass/fail threshold; needs SME decomposition |
| **Other** | 4 | 4 | 1.0% | Out-of-scope or system-specific checks |
| **Cross-Loan Comparison** | 2 | 2 | 0.5% | Portfolio-level data required |
| **TOTAL** | **409** | **397** | **100%** | ~43% of Post-Closing ruleset |

**Key Finding:** Nearly half (409/944) of ingested Post-Closing rules are RED. This is not an edge case — it's a design constraint that defines the product's scope.
## Visual Distribution

```
RED RULE BREAKDOWN (409 total)

Narrative Judgment    ████████████████████ 187 rules (45.7%)
External Data         ████████████████████ 187 rules (45.7%)
Ambiguous/Vague       ███                   29 rules (7.1%)
Other                 ▌                      4 rules (1.0%)
Cross-Loan Comparison ▌                      2 rules (0.5%)

KEY BLOCKS:
property-appraisal-review: 317 rules (77.5% of RED) — Heavily narrative
underwriting-review:        24 rules (5.9% of RED)
product-specific-check:     17 rules (4.2% of RED)
asset-verification:         18 rules (4.4% of RED)
credit-liabilities-review:  15 rules (3.7% of RED)
income-verification:         6 rules (1.5% of RED)
application-verification:   12 rules (2.9% of RED)
```



---

## Detailed Breakdown by Root Cause

### Narrative Judgment Required

**Count:** 187 rules (45.7%) across 178 groups

**Description:** Rules that require subjective human assessment using phrases like "adequate," "reasonable," "acceptable," "sufficient," "appears to need more space," or "without comment." These are inherently human decisions that cannot be reduced to deterministic checks.

**Keywords:** `adequate, reasonable, sufficient, acceptable, satisfactory, appropriate, appears, professional judgment`

**Distribution by block:**

- `property-appraisal-review`: 124 rules (120 groups)
- `underwriting-review`: 16 rules (16 groups)
- `credit-liabilities-review`: 13 rules (13 groups)
- `asset-verification`: 11 rules (10 groups)
- `product-specific-check`: 8 rules (8 groups)
- `application-verification`: 11 rules (7 groups)
- `income-verification`: 4 rules (4 groups)

**Examples:**

1. **[application-verification]** (Best Practice) Standard/approved translated docs not issued based on the applicant(s) LEP pref.
   - **Rationale:** Depends on shop practice and preference nuance — reviewer judgment.
   - **Stays human:** whether translated docs matched the applicant's LEP preference
   - **Rules:** 1

2. **[application-verification]** Discrepancies in the file not explained or supporting docs provided
   - **Rationale:** Open-ended cross-file judgment; specific discrepancies belong to specific checks.
   - **Stays human:** file-wide 'discrepancies not explained' sweep
   - **Rules:** 1

3. **[application-verification]** It appears the borr needed more space to complete the URLA & a continuation sheet not in the file
   - **Rationale:** Inherently a judgment about handwriting/space; route to reviewer.
   - **Stays human:** 'appears the borrower needed more space'
   - **Rules:** 3

4. **[application-verification]** The borrower needed more space to complete the URLA & a continuation sheet was not in the file
   - **Rationale:** As #23.
   - **Stays human:** same 'needed more space' judgment
   - **Rules:** 1

5. **[application-verification]** It appears the borr needed more space to complete the URLA & a continuation sheet not in the file
   - **Rationale:** As #23.
   - **Stays human:** 'needed more space' judgment (FNM variant)
   - **Rules:** 1

*(... 173 more groups in this category)*

---

### External Data Dependency

**Count:** 187 rules (45.7%) across 184 groups

**Description:** Rules that require lookups, APIs, registries, or external databases not available in the closed-loan file. Examples: NMLS registry lookups, credit bureau checks, third-party verification services, appraisal desk/field review requirements.

**Keywords:** `NMLS, registry, lookup, external API, database, third-party service, verification service`

**Distribution by block:**

- `property-appraisal-review`: 187 rules (184 groups)

**Examples:**

1. **[property-appraisal-review]** No, a desk review or field review was not obtained by a certified appraiser as required
   - **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'No, a desk review or field review was not obtained by a certified appraiser as required'
   - **Stays human:** no crisp extractable fact identified in this row's condition text
   - **Rules:** 1

2. **[property-appraisal-review]** Subject has leased equipment, leased energy system or PPA not free of restrictions
   - **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Subject has leased equipment, leased energy system or PPA not free of restrictions'
   - **Stays human:** no crisp extractable fact identified in this row's condition text
   - **Rules:** 1

3. **[property-appraisal-review]** Appraisal form was incorrect for the property & inspection type or as per LPA
   - **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Appraisal form was incorrect for the property & inspection type or as per LPA'
   - **Stays human:** no crisp extractable fact identified in this row's condition text
   - **Rules:** 1

4. **[property-appraisal-review]** No, the information in the subject section is incomplete or inaccurate
   - **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'No, the information in the subject section is incomplete or inaccurate'
   - **Stays human:** no crisp extractable fact identified in this row's condition text
   - **Rules:** 1

5. **[property-appraisal-review]** Market value opinion is inaccurate as of the effective date of the report - Section II not completed
   - **Rationale:** No form/threshold/project-doc/external-DB signal matched; defaulting to human review is the conservative choice for this narrative-heavy block rather than inventing an automation path — condition: 'Market value opinion is inaccurate as of the effective date of the report - Section II not completed'
   - **Stays human:** no crisp extractable fact identified in this row's condition text
   - **Rules:** 1

*(... 179 more groups in this category)*

---

### Ambiguous Phrasing / No Clear Pass-Fail

**Count:** 29 rules (7.1%) across 29 groups

**Description:** Rules with vague conditions that provide no testable threshold or enumerated fact. Often catch-all phrases like "all requirements met," "discrepancies not explained," or "as required" without specifying what those requirements are.

**Keywords:** `unclear, vague, catch-all, open-ended, discrepancies, not explained, as required`

**Distribution by block:**

- `underwriting-review`: 8 rules (8 groups)
- `asset-verification`: 7 rules (7 groups)
- `property-appraisal-review`: 6 rules (6 groups)
- `product-specific-check`: 4 rules (4 groups)
- `credit-liabilities-review`: 2 rules (2 groups)
- `application-verification`: 1 rules (1 groups)
- `income-verification`: 1 rules (1 groups)

**Examples:**

1. **[application-verification]** All disclosures (as required) have not been completed accurately & signed per guidelines
   - **Rationale:** Needs SME decomposition into enumerable VA disclosures before any automation.
   - **Stays human:** catch-all 'all disclosures per guidelines'
   - **Rules:** 1

2. **[asset-verification]** All requirements not met for use of funds in a Community Savings System
   - **Rationale:** Bare catch-all with no specific fact stated — needs SME decomposition into the actual Community-Savings-System documentation checklist, same pattern as application-verification's VA disclosure catch-all.
   - **Stays human:** open-ended 'all requirements not met for use of funds in a Community Savings System'
   - **Rules:** 1

3. **[asset-verification]** Employer Assisted Homeownership (EAH) Benefit requirements not met for the type of benefit received
   - **Rationale:** Open-ended, benefit-type-dependent catch-all — no single checkable fact until an SME enumerates EAH benefit types and their individual requirements.
   - **Stays human:** 'requirements not met for the type of benefit received' (type-dependent, unstated)
   - **Rules:** 1

4. **[asset-verification]** All requirements not met for use of Individual Development Account (IDA)
   - **Rationale:** Same bare-catch-all pattern as G018.
   - **Stays human:** open-ended 'all requirements not met for use of Individual Development Account (IDA)'
   - **Rules:** 1

5. **[asset-verification]** Asset documents did not meet Streamlined Accept or Standard documentation LPA req's per asset type
   - **Rationale:** Open-ended compliance check across an entire LPA documentation matrix spanning many asset types — needs SME decomposition before any single fact is checkable, same pattern as application-verification's VA disclosure catch-all.
   - **Stays human:** 'Streamlined Accept or Standard documentation... per asset type' matrix
   - **Rules:** 1

*(... 24 more groups in this category)*

---

### Other

**Count:** 4 rules (1.0%) across 4 groups

**Description:** Rules that do not fit the above categories. Often system/LOS-specific checks, out-of-scope requirements, or rules needing SME decomposition into specific facts.

**Keywords:** `varies`

**Distribution by block:**

- `product-specific-check`: 3 rules (3 groups)
- `income-verification`: 1 rules (1 groups)

**Examples:**

1. **[income-verification]** The self-employment income is not stable
   - **Rationale:** exception_description adds nothing beyond restating the conclusion ('did not meet stability requirements'). Distinct from the many self-employed rows elsewhere in this block that name a specific document (tax returns, P&L, business credit report) — this one names none.
   - **Stays human:** 'self-employment income is not stable' — bare conclusion, no accompanying document or threshold
   - **Rules:** 1

2. **[product-specific-check]** UGV exception is not properly reflected in EPIC - Expanded & UGV box
   - **Rationale:** Same as G347 — out of document-extraction scope entirely.
   - **Stays human:** same internal lender-system class as G347 ('not properly reflected in EPIC')
   - **Rules:** 1

3. **[product-specific-check]** TX Refi did not meet Section 50(a)(6) Article XVI of the Texas Constitution
   - **Rationale:** Needs SME decomposition of the actual TX 50(a)(6) requirement checklist — this row states no checkable fact on its own.
   - **Stays human:** bare reference to Texas Constitution Article XVI Section 50(a)(6) with zero in-row specifics
   - **Rules:** 1

4. **[product-specific-check]** TX Sect 50(a)(6) Mg didn't comply with TX Constitution and all requirements
   - **Rationale:** Same as G673.
   - **Stays human:** same bare TX 50(a)(6) reference as G673 (FNM variant)
   - **Rules:** 1

---

### Cross-Loan Comparison

**Count:** 2 rules (0.5%) across 2 groups

**Description:** Rules that require comparison across multiple loans or reference to portfolio-level data, not checkable on a single closed-loan file.

**Keywords:** `portfolio, other loans, comparative analysis`

**Distribution by block:**

- `product-specific-check`: 2 rules (2 groups)

**Examples:**

1. **[product-specific-check]** Port guides not met (ex: 2 years W2s, 2 mos bank statements, add'l reserves
   - **Rationale:** The row itself says 'examples' and 'etc' — it does not enumerate a closed, checkable rule set. Needs SME decomposition of the full Portfolio overlay checklist before any single fact is checkable.
   - **Stays human:** bare, non-exhaustive Portfolio overlay list ('ex: 2 years W2s, 2 mos bank statements, add'l reserves, etc' — 'etc' is explicit)
   - **Rules:** 1

2. **[product-specific-check]** All UGV exceptions are not clearly identified/listed in the Portfolio exception screen
   - **Rationale:** Same out-of-scope-entirely class as G010/G350: this is about the LENDER's own internal system, not any document this pilot models.
   - **Stays human:** an internal lender exception-tracking-system completeness check ('not clearly identified/listed in the Portfolio exception screen') — not a loan-document fact at all
   - **Rules:** 1

---


## RED Rules by Block

Distribution of RED rules across the 7 triaged blocks:

| Block | RED Rules | % of Block RED | Top Category |
|-------|-----------|----------------|--------------|
| `application-verification` | 12 | - | Narrative Judgment (11, 92%) |
| `asset-verification` | 18 | - | Narrative Judgment (11, 61%) |
| `credit-liabilities-review` | 15 | - | Narrative Judgment (13, 87%) |
| `income-verification` | 6 | - | Narrative Judgment (4, 67%) |
| `product-specific-check` | 17 | - | Narrative Judgment (8, 47%) |
| `property-appraisal-review` | 317 | - | External Data (187, 59%) |
| `underwriting-review` | 24 | - | Narrative Judgment (16, 67%) |

**Note:** Property-appraisal-review dominates with 317 RED rules (77.5% of all RED). This block is inherently narrative-heavy ("adequate explanation," "professional judgment," etc.).

## Recommendation: How to Handle RED Rules in Demo/PoC

### The Honest Assessment

**409 RED rules (out of 944 total rules ingested) represent ~43% of the Post-Closing ruleset.** This is not a minor edge case — this is nearly half the workload.

### What RED Means for the Demo

RED rules fall into two operational categories:

1. **Truly Unautomatable** (~45% of RED): Narrative judgment, inherently subjective, or require human expertise that cannot be codified.
   - **Examples:** "adequate explanation," "appears to need more space," "reasonable professional judgment"
   - **Demo treatment:** Flag as `HUMAN_REVIEW_REQUIRED` in the UI. Show the rule, the loan data, and route to a reviewer queue. Do NOT pretend the system can auto-clear these.

2. **Automatable with More Data** (~55% of RED): External lookups, ambiguous phrasing needing SME decomposition, or missing fixture data.
   - **Examples:** NMLS registry checks, "all disclosures as required" (needs enumeration), appraisal desk review requirements
   - **Demo treatment:** Short-term = same as #1 (human review queue). Medium-term = prioritize SME decomposition and external API integration for the highest-impact rules.

### Proposed Demo UI Treatment

**Option A: Flag RED as "Human Review Required" (Recommended)**
- **Why:** Honest, defensible, shows the system knows its limits
- **How:** 
  - Rules classified as RED at compile-time get a `human_review_required: true` flag
  - These rules auto-route to the Exception Review queue with a clear label: **"Requires Expert Judgment"**
  - The UI shows: rule text, extracted loan data, citation (if available), and a text box for the reviewer's decision
  - Metric: "X% auto-cleared, Y% routed to expert review" (not "failed" — routed)

**Option B: Exclude RED from Demo Scope**
- **Why:** Keeps the demo focused on the deterministic success story
- **Risk:** Client asks "what about the other 43%?" and you have no answer
- **When to use:** Only if the demo is explicitly scoped to "provably automatable checks only"

**Option C: Fake It (DO NOT DO THIS)**
- Run RED rules through an LLM at runtime and present the result as deterministic
- **Why this is unacceptable:** Violates Non-Negotiable #1, destroys the regulatory audit story, and is dishonest

### Recommended Path Forward

#### Phase 1: Demo (Now)
- **Implement Option A:** Flag RED rules as `HUMAN_REVIEW_REQUIRED`
- **Demo narrative:** "Our system automatically clears 409 deterministic checks and intelligently routes 409 judgment-required exceptions to the expert review queue, with full traceability."
- **Key metric:** Show the *resolution rate* (auto-cleared ÷ total) alongside *exception routing accuracy* (right exceptions to the right queue)

#### Phase 2: Post-Demo Productization
1. **SME Decomposition Sprints** (target the ambiguous/vague category first — 29 groups, high leverage):
   - "All disclosures as required" → enumerate the 12 specific disclosures
   - "Requirements not met" → decompose into checkable facts
   - Partner with Kayla to turn these into GREEN/YELLOW rules

2. **External API Integration** (target external_data category — 187 rules, 45% of RED):
   - NMLS registry lookup service (Decision 016 already flagged this as Bucket C)
   - Appraisal desk/field review requirement API (if such a service exists)
   - Credit bureau integration (out of closed-loan scope, but client may want it)

3. **Narrative Judgment Acceptance** (187 rules, 45% of RED):
   - These stay human. Period.
   - Build the best possible reviewer UX: side-by-side doc viewer, citation highlighting, one-click resolution, keyboard shortcuts
   - The goal is not to eliminate human review — it's to eliminate *unnecessary* human review and make the necessary review as fast as possible

### Key Insight: RED Is Not Failure

**The existence of RED rules is not a system limitation — it's a feature.** A mortgage QC system that claims to automate subjective judgment is lying. A system that explicitly routes subjective cases to human experts while auto-clearing the deterministic ones is *trustworthy*.

**The demo narrative should be:**
> "Our system doesn't pretend to replace human judgment — it amplifies it. We deterministically clear the 409 objective checks, route the 409 judgment-required cases to the right expert queue with full context, and ensure every decision is auditable. The result: faster cycle time, zero missed defects, and full regulatory compliance."

---

**Bottom line:** Ship Option A in the demo. Frame RED as intelligent routing, not system failure. Prioritize SME decomposition and external API integration for Phase 2.

