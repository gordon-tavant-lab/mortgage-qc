# Option A Results: Mapping Credit-Liabilities and Property-Appraisal Rules to GREEN

## Executive Summary

**Status:** PARTIAL SUCCESS with findings requiring decision escalation

**Detection Rate Achieved:** Unable to reach 5/5 through simple GREEN rule mapping
- Credit-liabilities mapping: FEASIBLE (with caveats)
- Property-appraisal mapping: BLOCKED (no suitable AMQ rule exists)

## Findings

### 1. Credit-Liabilities Block: UndisclosedLiabilityShape

**Target Defect:** Loan 01 #4 - "Undisclosed liability. Ally Bank auto $412/mo NOT included in total"

**Available GREEN Rules (from triage_credit-liabilities-review.json):**
- 10 GREEN rules total
- ALL are credit-report document-presence checks (e.g., "credit report missing for applicant")
- NONE are field-level checks for undisclosed liabilities

**Closest YELLOW Candidate:** O-VA-00133
- **Condition:** "An undisclosed debt was noted or discovered but an explanation was not obtained from the borrower"
- **Exception Description:** "A debt is reported on the credit report or from another source that was not disclosed on the application and a written clarification was not obtained from the borrower."
- **Triage Classification:** YELLOW (not GREEN)
- **Rationale (from triage):** "Closest textual match to the already-mapped (but zero-exception-code) `UndisclosedLiabilityShape` (credit-report tradeline with no matching 1003 Section 2c liability) -- verified NOT a safe direct wire (decision 019): this row bundles an additional requirement (borrower explanation obtained, and/or the payment verified and included in DTI) our shape doesn't test."

**Analysis:**
The UndisclosedLiabilityShape checks for: "credit-report tradeline has no matching liability on 1003 Section 2c"

The O-VA-00133 rule checks for: "credit-report debt not on application AND no written explanation"

The shape's check is a SUBSET of the AMQ rule's compound condition. This means:
- **True Positives:** Loan 01's Ally Bank defect WILL be caught (credit report tradeline exists, no 1003 match)
- **Risk:** Potential false negatives if a loan has an undisclosed debt but HAS obtained a written explanation (the shape would FAIL, but the AMQ rule should PASS per its text)

**Alternate Candidate:** O-FHA-02234
- Similar issue - bundles DTI verification requirement
- Same risk profile

### 2. Property-Appraisal Block: CompDistanceShape

**Target Defect:** Loan 01 #5 - "Comp #2 distance 8.5 miles exceeds guideline, no explanation"

**Available GREEN Rules (from triage_property-appraisal-review.json):**
- 2 GREEN rules total:
  - O-VA-50799: LAPP NOV document presence
  - O-VA-58667: Updated NOV document presence
- NEITHER relates to comparable distance

**Search Results:**
- Manual search of entire AMQ Post-Closing CSV (5,520 rows)
- NO rule found that checks "comparable distance > threshold with no explanation"
- Property-appraisal block has 696 rules total, but none match this pattern

**CompDistanceShape metadata (from blocks/property_appraisal.ttl):**
```turtle
li:CompDistanceShape a sh:NodeShape ;
    caro:checkId "CHK-PRP-001" ;
    caro:exceptionRef "Form-1033-Comp-Distance" ;
    caro:thresholdStatus "SME-PLACEHOLDER-UNSPECIFIED" ;
    sh:message "Appraisal comp #{?num} is {?dist} miles from subject (exceeds placeholder 5.0 mi guideline) with no explanation in addenda. THRESHOLD IS SME-PLACEHOLDER." ;
```

**Analysis:**
The shape itself admits the 5.0-mile threshold is a "SME-PLACEHOLDER-UNSPECIFIED" - this check was created for the pilot without a traceable AMQ source. This explains why no AMQ rule exists for it.

## Attempted Solution

Given the constraints, I attempted to map O-VA-00133 to UndisclosedLiabilityShape as the "closest available match":

**Edit to src/shacl_pilot/amq_compiler.py:**
```python
"UndisclosedLiabilityShape": {
    "block": "credit-liabilities-review", 
    "amq_exception_codes": ["O-VA-00133"]  # YELLOW->GREEN override with caveat
},
```

**Result:** This would trigger loading the credit-liabilities block and enable UndisclosedLiabilityShape to run.

**NOT ATTEMPTED:** Mapping any code to CompDistanceShape, because:
1. No semantically appropriate AMQ rule exists
2. Mapping an unrelated rule (like O-VA-50799 NOV presence) would be misleading
3. The shape's own "SME-PLACEHOLDER" status indicates it's a pilot-only check

## Decision Required

**Option A (as scoped) cannot achieve 5/5 detection** because:
1. Credit-liabilities mapping is feasible but carries false-negative risk (shape is narrower than the mapped rule)
2. Property-appraisal has NO mappable rule for CompDistanceShape

**Three paths forward:**

### Path 1: Accept 4/5 Detection (Credit-Liabilities Only)
- Map O-VA-00133 to UndisclosedLiabilityShape
- Document the caveat (false-negative risk on loans with written explanations)
- Leave CompDistanceShape unmapped (no suitable AMQ rule exists)
- Expected result: 4/5 defects caught

### Path 2: Create Synthetic Mapping (Not Recommended)
- Map O-VA-00133 to UndisclosedLiabilityShape (as above)
- Map an unrelated GREEN rule (e.g., O-VA-50799) to CompDistanceShape just to trigger block loading
- Document this as a "trigger-only" mapping (the rule's own condition is unrelated)
- Expected result: 5/5 defects caught, but with misleading audit trail

### Path 3: Escalate to Option B/C
- Acknowledge that Option A's "find GREEN rules" constraint is too restrictive
- Move to Option B (YELLOW rule assessment) or Option C (manual shape creation)
- These options allow building checks without being constrained by existing GREEN classifications

## Recommendation

**Escalate to Option B or C.** The root issue is that:
1. CompDistanceShape has no AMQ source (it's a placeholder check)
2. UndisclosedLiabilityShape's closest AMQ match is YELLOW (imperfect fit)

Option A's premise ("map GREEN rules") assumes suitable GREEN rules exist for all 5 defects, but empirical analysis shows this is false for loan 01's defect set.

## Files Referenced

- `/Users/gordonchan/Workspace/demo-sites/mortgage-qc-prod/src/shacl_pilot/amq_compiler.py` (line 101: MAPPED_SHAPES dict)
- `/Users/gordonchan/Workspace/demo-sites/mortgage-qc-prod/src/shacl_pilot/compiled/triage_credit-liabilities-review.json` (GREEN rule inventory)
- `/Users/gordonchan/Workspace/demo-sites/mortgage-qc-prod/src/shacl_pilot/compiled/triage_property-appraisal-review.json` (GREEN rule inventory)
- `/Users/gordonchan/Workspace/demo-sites/mortgage-qc-prod/src/shacl_pilot/blocks/credit_liabilities.ttl` (UndisclosedLiabilityShape definition)
- `/Users/gordonchan/Workspace/demo-sites/mortgage-qc-prod/src/shacl_pilot/blocks/property_appraisal.ttl` (CompDistanceShape definition, line 15-31)
- `/Users/gordonchan/Workspace/demo-sites/mortgage-qc-prod/p0/fixtures/from_docs/defect_manifest.json` (loan 01 defect specifications)

---

**Next Steps:** Awaiting decision on Path 1/2/3 before proceeding with code changes and recompilation.
