# NOT_APPLICABLE Status Design

**Date:** 2026-07-30  
**Context:** SHACL pilot — decision 008 result states (PASS / FAIL / NEEDS_REVIEW) + this new state  
**Problem:** "Check for gift letter" fails when the loan has no gift transaction. If there's no gift, the rule shouldn't apply at all — returning NOT_APPLICABLE, not FAIL.

---

## 1. Detection Logic: How Does the Engine Know a Rule Doesn't Apply?

Three detection approaches, in order of specificity:

### 1.1 Precondition Check (Runtime, SPARQL-level)
**Pattern:** The SHACL shape includes an applicability guard in the SPARQL query itself.

**Example — GiftEvidenceShape (loan 02 defect #3):**
```sparql
SELECT $this WHERE {
    $this li:gift_transfer_evidence_in_file false .
}
```

**Current behavior:** If `gift_transfer_evidence_in_file` is not in the graph (i.e., there's no gift transaction), the query returns no results → shape passes → **PASSED**.

**Problem:** A loan with no gift transaction shouldn't "pass" the gift-evidence check — it should return **NOT_APPLICABLE** (the check didn't run because the precondition wasn't met).

**Solution:** Add an explicit precondition filter, and distinguish "no match" from "precondition not met":
```sparql
SELECT $this WHERE {
    # Precondition: a gift transaction exists
    FILTER EXISTS { $this li:gift_transfer_evidence_in_file ?any }
    # Then check the actual condition
    $this li:gift_transfer_evidence_in_file false .
}
```

If the `FILTER EXISTS` fails, the query returns **no results** → the shape doesn't fire → **NOT_APPLICABLE**.  
If the filter passes but the condition fails, the query returns a violation → **FAIL**.  
If the filter passes and the condition passes, the query returns no violation → **PASSED**.

**BUT:** This still conflates "no violation" with "didn't check" — SHACL returns the same empty result set for both. We need post-processing.

---

### 1.2 Metadata-Driven Applicability (Compile-Time Declaration)
**Pattern:** The shape declares its preconditions in `caro:` metadata, and the engine checks them before running the shape.

**Example:**
```turtle
li:GiftEvidenceShape a sh:NodeShape ;
    sh:targetClass li:LoanInstance ;
    caro:checkId "CHK-AST-002" ;
    caro:requiresField "gift_transfer_evidence_in_file" ;  # NEW metadata
    caro:citesFields "gift_transfer_evidence_in_file" ;
    sh:sparql [ ... ] .
```

**Engine logic (Python, in `run_audit.py`):**
```python
def check_applicability(shape_name, meta, extraction):
    """Returns: 'applicable' | 'not_applicable' | 'no_data'"""
    required = meta.get("requiresField", [])
    for field in required:
        if field not in extraction["fields"] and field not in extraction["facts"]:
            return "not_applicable"  # precondition field doesn't exist
    # Now check if data for the actual check is present
    if not data_present(shape_name, meta, extraction):
        return "no_data"  # fields exist but values are missing
    return "applicable"
```

**Before running the shape:**
```python
applicability = check_applicability(shape_name, meta, extraction)
if applicability == "not_applicable":
    mapped_status[name] = "NOT_APPLICABLE"
    continue  # skip SHACL validation for this shape
elif applicability == "no_data":
    mapped_status[name] = "NO_DATA"
    continue
else:
    # run the shape, interpret results as PASS/FAIL/NEEDS_REVIEW
```

**Advantage:** Explicit, auditable preconditions in the shape definition (not buried in SPARQL). SME can see at a glance: "This check only applies if `gift_transfer_evidence_in_file` exists."

**Disadvantage:** Requires annotating every shape with `caro:requiresField` — a compile-time/authoring burden.

---

### 1.3 Data-Driven Heuristics (Runtime, Inferred from Loan Data)
**Pattern:** The engine infers applicability from the loan's data profile, using domain knowledge.

**Examples:**
- **Gift checks:** Only apply if `gift_transfer_evidence_in_file` exists OR `mismo_gift_amount > 0` OR the 1003 mentions a gift in Section 3.
- **FHA-specific checks:** Only apply if `mismo_mortgage_type == "FHA"` (already done — decision 010).
- **VA ARM disclosure:** Only apply if `mismo_amortization_type == "AdjustableRate"` (see ArmDisclosureShape, loan 03 defect #2).
- **Self-employed docs:** Only apply if the borrower is self-employed (detected from `employment_status` or employer name patterns).

**Engine logic:**
```python
def infer_applicability(shape_name, extraction):
    """Domain-specific heuristics for applicability."""
    if shape_name == "GiftEvidenceShape":
        # Only applies if there's evidence of a gift transaction
        gift_field = extraction["facts"].get("gift_transfer_evidence_in_file")
        mismo_gift = extraction["fields"].get("mismo_gift_amount", {}).get("value", 0)
        return gift_field is not None or mismo_gift > 0
    if shape_name == "ArmDisclosureShape":
        amort = extraction["fields"].get("mismo_amortization_type", {}).get("value", "")
        return amort == "AdjustableRate"
    if shape_name == "SelfEmployedDocsShape":
        # Heuristic: employer name contains "LLC", "Consulting", or self-employment flag
        employer = str(extraction["fields"].get("employer_name_1003", {}).get("value", ""))
        return "self-employed" in employer.lower() or "LLC" in employer or "Consulting" in employer
    # Default: always applicable
    return True
```

**Advantage:** No shape authoring changes required. Works for existing shapes.

**Disadvantage:** Implicit, hard to audit. "Why didn't this check run?" → "Because the heuristic said so" is not a satisfying answer for a regulator.

---

## 2. Engine Implementation: Where Does NOT_APPLICABLE Get Evaluated?

Three integration points:

### 2.1 Pre-Validation Filter (Runtime, Before SHACL)
**Location:** `run_audit.py`, in the main loop before calling `run_validation()`.

**Current logic (lines 250-260):**
```python
fired = {name: status for name, status, _ in run1}
mapped_status = {}
for name, meta in catalog.items():
    if name in fired:
        status = fired[name]
    elif data_present(name, meta, extraction):
        status = "PASSED"
    else:
        status = "NO_DATA"
    mapped_status[name] = status if status != "PASSED" else "PASS"
```

**Proposed change (insert before `if name in fired`):**
```python
for name, meta in catalog.items():
    # NEW: check applicability first
    applicability = check_applicability(name, meta, extraction)
    if applicability == "not_applicable":
        mapped_status[name] = "NOT_APPLICABLE"
        continue
    elif applicability == "no_data":
        mapped_status[name] = "NO_DATA"
        continue
    # Then proceed with existing logic
    if name in fired:
        status = fired[name]
    elif data_present(name, meta, extraction):
        status = "PASSED"
    else:
        status = "NO_DATA"
    mapped_status[name] = status if status != "PASSED" else "PASS"
```

**Advantage:** Minimal disruption. NOT_APPLICABLE is evaluated before SHACL runs, so inapplicable shapes never execute (performance win).

**Disadvantage:** Separates applicability logic from the shape definition itself (harder to audit the full check in one place).

---

### 2.2 Post-Validation Classification (Runtime, After SHACL)
**Location:** Same place as above, but after `run_validation()`.

**Logic:** If a shape didn't fire (no violation) AND its precondition field doesn't exist, classify as NOT_APPLICABLE instead of PASSED.

```python
for name, meta in catalog.items():
    if name in fired:
        status = fired[name]
    elif not data_present(name, meta, extraction):
        status = "NO_DATA"
    else:
        # NEW: distinguish PASSED from NOT_APPLICABLE
        required = meta.get("requiresField", [])
        missing_precondition = any(
            f not in extraction["fields"] and f not in extraction["facts"]
            for f in required
        )
        status = "NOT_APPLICABLE" if missing_precondition else "PASSED"
    mapped_status[name] = status if status != "PASSED" else "PASS"
```

**Advantage:** Shape still runs (so you can inspect the SPARQL query for debugging), but the result is re-classified based on preconditions.

**Disadvantage:** Shapes run even when they shouldn't apply (performance hit). Also, SHACL might return a false-positive violation if the SPARQL doesn't guard against missing preconditions.

---

### 2.3 Compile-Time (AMQ → SHACL Translation)
**Location:** `amq_compiler.py` or the layer2_triage_* scripts.

**Pattern:** When generating a SHACL shape from an AMQ row, the compiler infers preconditions from the row's text and embeds them in the shape's SPARQL.

**Example — O-FHA-54280 (loan 02 defect #1):**
AMQ row: "HUD-92900-A Section III (Borrower Certification) is not signed."

**Compiler infers:**
- Precondition: `doc_present_hud_92900a == true` (the document must exist)
- Condition: `sig_hud92900a_borrower_present == false` (the signature is absent)

**Generated SPARQL:**
```sparql
SELECT $this WHERE {
    # Precondition: HUD-92900-A must be in the file
    ?doc li:doc_present_hud_92900a true .
    # Condition: Section III unsigned
    $this li:sig_hud92900a_borrower_present false .
}
```

If `doc_present_hud_92900a` is not in the graph, the query returns no results → NOT_APPLICABLE.

**Advantage:** Preconditions are baked into the SHACL artifact at compile time — fully deterministic, auditable. No runtime heuristics.

**Disadvantage:** Requires LLM-driven inference at compile time (risk of misinterpreting the AMQ row). Also, same conflation problem as 1.1 (empty SPARQL result = both "passed" and "didn't apply").

---

## 3. Rule Categories Most Affected

### 3.1 Document-Presence Checks (`doc_presence` eval_class) — **BIGGEST IMPACT**
**Count:** 91 rules (from `grep '"eval_class": "doc_presence"'`).

**Current behavior (line 201-202 of `run_audit.py`):**
```python
if rule["eval_class"] == "doc_presence":
    status = "PASS" if rule["eval_target"] in docs else "NEEDS_REVIEW"
```

**Problem:** If a document isn't required for this loan, "NEEDS_REVIEW" is wrong — it should be "NOT_APPLICABLE".

**Example:** `arm_program_disclosure` (VA ARM disclosure) should only be checked for VA ARM loans, not all VA loans. Current logic: if it's a VA loan but not an ARM, the rule fires → doc is absent → NEEDS_REVIEW. **Wrong.** Should be NOT_APPLICABLE.

**Proposed fix:**
```python
if rule["eval_class"] == "doc_presence":
    if rule_applies(rule, extraction):  # NEW helper function
        status = "PASS" if rule["eval_target"] in docs else "NEEDS_REVIEW"
    else:
        status = "NOT_APPLICABLE"
```

**`rule_applies()` logic:**
- Check the rule's `eval_target` (doc name) against the loan's profile.
- Example: `arm_program_disclosure` applies only if `mismo_amortization_type == "AdjustableRate"`.
- This requires a **precondition map** (doc name → applicability condition), either:
  - Embedded in `ruleset.json` (compiled from AMQ), OR
  - Hardcoded in `run_audit.py` (domain knowledge), OR
  - Inferred at runtime from the doc's own context (e.g., "FHA" in the doc name → only applies to FHA loans).

---

### 3.2 Program-Specific Checks (Already Partially Gated by Agency)
**Current gate (line 198):**
```python
if rule["agency"] not in (agency, "GENERIC"):
    counts["EXCLUDED_PROGRAM"] += 1
    continue
```

**This handles coarse-grained filtering (FHA vs VA vs Conventional).**

**Gap:** Sub-program filtering isn't done. Examples:
- **VA ARM checks** should only apply to VA ARMs, not all VA loans.
- **Cash-out refi checks** should only apply to cash-out loans, not all refis.
- **Self-employed checks** should only apply to self-employed borrowers.

**Proposed enhancement:** Add a `rule_preconditions` field to each rule in `ruleset.json`:
```json
{
  "eval_class": "doc_presence",
  "eval_target": "arm_program_disclosure",
  "agency": "O-VA",
  "rule_preconditions": {
    "mismo_amortization_type": "AdjustableRate"
  }
}
```

**Engine checks preconditions before running the rule:**
```python
if not check_preconditions(rule["rule_preconditions"], extraction):
    counts["NOT_APPLICABLE"] += 1
    continue
```

**Advantage:** Explicit, auditable preconditions in the ruleset artifact (SME can review them before deployment).

---

### 3.3 Specific Data Checks (Mapped SHACL Shapes)
**Count:** 12 mapped shapes (from `grep '"eval_class": "mapped"'`).

**Examples from loan 01:**
- **LargeDepositShape:** Only applies if there are bank transactions in the extraction (`bank_txns` entity family is non-empty).
- **GiftEvidenceShape:** Only applies if there's a gift transaction (precondition field exists).
- **SelfEmployedDocsShape:** Only applies if the borrower is self-employed.

**Current NO_DATA logic (line 171-178) handles missing data**, but **doesn't distinguish "data missing" from "check doesn't apply".**

**Example — LargeDepositShape on a loan with no bank statement:**
- Current: `bank_txns` is empty → `data_present()` returns False → NO_DATA.
- Proposed: If the loan is a refinance (where large-deposit docs aren't required per B3-4.2-02), return NOT_APPLICABLE instead of NO_DATA.

**Challenge:** The Selling Guide nuance ("for refinance, large deposits don't need docs") isn't in the AMQ row — it was found by looking up B3-4.2-02 in the topic index (see GiftEvidenceShape's `GUIDE NUANCE` comment, `blocks/assets.ttl` line 22). **How do we know this at runtime?**

**Options:**
1. **Compile-time annotation:** The compiler (or an SME) adds `"rule_preconditions": {"loan_purpose": "Purchase"}` to LargeDepositShape's rule entry.
2. **Runtime heuristic:** The engine infers from `loan_purpose_1003` or `loan_purpose_cd`. **Risky** (what if the value is ambiguous?).
3. **SME declaration:** The shape author adds `caro:appliesToPurpose "Purchase"` in the TTL file. **Best option** (explicit, auditable).

---

## 4. Honest Boundary: Automatic vs. SME Annotation

### 4.1 What Can Be Detected Automatically?

| Precondition Type | Auto-Detectable? | Example |
|---|---|---|
| **No gift transaction** | ✅ Yes | Check if `gift_transfer_evidence_in_file` exists in the extraction. If not, GiftEvidenceShape → NOT_APPLICABLE. |
| **No ARM loan** | ✅ Yes | Check `mismo_amortization_type`. If not "AdjustableRate", ArmDisclosureShape → NOT_APPLICABLE. |
| **No bank transactions in file** | ✅ Yes | Check if `bank_txns` entity family is empty. If so, LargeDepositShape → NO_DATA (not NOT_APPLICABLE — the check would apply if data were present). |
| **Loan purpose is refinance** | ⚠️ Maybe | `loan_purpose_1003` or `loan_purpose_cd` exists, but what if they conflict? What if it's cash-out vs rate-term? Needs disambiguation logic. |
| **Borrower is self-employed** | ⚠️ Maybe | Heuristic from employer name / employment status. **Risky** (could misclassify). Better: require an explicit `self_employed` fact in the extraction. |
| **Property is pre-1978** | ✅ Yes | Check `year_built_1003` or `year_built_appraisal`. If < 1978, LBP checks apply. |
| **Property is in NC** | ✅ Yes | Check property state. If NC, termite inspection is required (VA-specific). |
| **Manufactured housing** | ❌ No | AMQ rows mention "manufactured housing" as a precondition, but there's no `property_type` field in the extraction today. **Needs data contract expansion.** |
| **4-unit property** | ❌ No | Similar — no `unit_count` field. **Needs data contract expansion.** |

**Automatic detection works for preconditions that are already in the extraction data model.** Anything else requires either:
- **Data contract expansion** (add new fields to `extract_loan.py`), OR
- **SME annotation** (manual declaration in the shape or ruleset).

---

### 4.2 What Needs SME Annotation?

**Preconditions that aren't in the data today:**
- **Property type** (manufactured, condo, 2-4 unit, etc.) — mentioned in 100+ AMQ rows, but not extracted.
- **Occupancy type** (primary residence, investment, second home) — same.
- **Loan purpose subtype** (cash-out vs rate-term refi) — partially extractable but ambiguous.
- **Selling Guide nuances** (e.g., "large deposits don't need docs on refi") — not in AMQ, found only by looking up the guide.

**Honest assessment:** Automatic detection can handle **~70% of doc-presence checks** (agency-specific docs, ARM-specific docs, pre-1978 docs) and **~40% of data checks** (those with clear precondition fields). The rest need either **data expansion** or **SME declaration**.

**Proposed SME workflow (for the 30% that can't be auto-detected):**
1. Compiler generates a draft shape with `caro:requiresField` metadata, but leaves `caro:appliesToPurpose` / `caro:appliesToPropertyType` blank.
2. SME reviews the shape, consults the Selling Guide, and fills in the blanks.
3. Engine uses the filled-in metadata to determine applicability at runtime.

---

## 5. Implementation Complexity

### 5.1 Minimal Implementation (Demo-Ready, 2-3 days)
**Scope:** Handle the **5 loan 02 defects that currently fire on loans without the precondition.**

**Changes:**
1. **Engine enhancement (2 hours):** Add `check_applicability()` function to `run_audit.py` that checks if a shape's `caro:requiresField` metadata fields exist in the extraction. If not → NOT_APPLICABLE.
2. **Shape annotation (4 hours):** Add `caro:requiresField` to the 5 loan 02 shapes:
   - `GiftEvidenceShape`: `caro:requiresField "gift_transfer_evidence_in_file"`
   - `ArmDisclosureShape`: `caro:requiresField "mismo_amortization_type"`
   - `SelfEmployedDocsShape`: (requires new `self_employed` fact in extraction — 1 hour to add)
   - `AmendatoryClauseShape`: Already program-gated (FHA only), no additional precondition needed.
   - `MprCompletionCertShape`: `caro:requiresField "mpr_repair_required"`
3. **Test (2 hours):** Run loan 01 (conventional, no gift) through the engine. GiftEvidenceShape should now return NOT_APPLICABLE instead of PASSED. **This is the demo proof point.**

**Total: ~8 hours** (1 day of focused work).

**Risk:** Low. Only touches 5 shapes. If it breaks, revert the `caro:requiresField` annotations and fall back to current behavior.

---

### 5.2 Full Implementation (Production-Ready, 2-3 weeks)
**Scope:** Handle **all 91 doc-presence checks + all 12 mapped shapes + the 4,047 unmapped rules** (eventually).

**Phases:**
1. **Data contract expansion (1 week):**
   - Add `property_type`, `unit_count`, `occupancy_type`, `self_employed` to `extract_loan.py`.
   - Update `field_catalog.json` with these new fields.
   - Add extraction logic to `extract_loan.py` for each (regex patterns, MISMO fallbacks).
   - Regenerate all 5 loan extraction JSONs.
   - Update answer keys if any defects now become detectable.

2. **Ruleset precondition annotation (3-5 days):**
   - For each of the 91 doc-presence rules in `ruleset.json`, add `rule_preconditions` (agency, loan purpose, property type, etc.).
   - Start with the high-impact ones (FHA/VA/USDA program-specific docs, ARM docs, pre-1978 docs).
   - Use a mix of automatic inference (from doc name patterns) and SME review.

3. **Shape precondition annotation (2-3 days):**
   - For each of the 12 mapped shapes, add `caro:requiresField` / `caro:appliesToPurpose` / `caro:appliesToPropertyType` metadata.
   - Document the Selling Guide reference for each precondition (audit trail).

4. **Engine enhancement (2-3 days):**
   - Generalize `check_applicability()` to handle `rule_preconditions` (not just `requiresField`).
   - Add `check_preconditions()` helper for doc-presence rules.
   - Update `workbook_stats()` to count NOT_APPLICABLE separately from PASS.
   - Update output format to show NOT_APPLICABLE in the per-block breakdown.

5. **Testing & validation (3-5 days):**
   - Run all 5 loans through the enhanced engine.
   - Verify no regressions (25/25 defects still detected, no new false positives).
   - Spot-check 10-20 NOT_APPLICABLE results to confirm they're correct.
   - Update `run_audit.py` docstring and decision log.

**Total: ~15-20 days** (3-4 weeks of calendar time with review rounds).

**Risk:** Medium. Touches the entire ruleset + all shapes + extraction logic. Needs thorough testing to avoid false negatives (a real defect misclassified as NOT_APPLICABLE is a **silent miss**, worse than a false positive).

---

## 6. Demo-Blocker Assessment

### Is this a demo-blocker?
**No.** Here's why:

**Current state (without NOT_APPLICABLE):**
- The 5/5 loan 01 defects are detected (FAIL).
- The 5/5 loan 02 defects are detected (FAIL).
- Extra shapes that don't apply (e.g., GiftEvidenceShape on loan 01) return **PASSED** (because the precondition field doesn't exist → SPARQL query returns no violation).
- This is **correct enough for a demo** — no false positives (extra FAILs), no missed defects.

**What NOT_APPLICABLE adds:**
- **Transparency:** "This check didn't run because the precondition wasn't met" vs. "This check ran and passed."
- **Audit trail clarity:** Regulators want to know *why* a check didn't fire, not just that it didn't fire.
- **Workbook stats accuracy:** The "PASS" count today includes both "passed" and "didn't apply" — NOT_APPLICABLE separates them.

**Demo story without NOT_APPLICABLE:**
> "We run 959 checks on an FHA loan. 10 pass, 9 need review, 936 aren't implemented yet. Of the 10 that pass, some genuinely passed (e.g., appraisal age is OK), and some didn't apply (e.g., no gift transaction, so the gift check was skipped)."

**Demo story with NOT_APPLICABLE:**
> "We run 959 checks. 5 pass, 5 fail, 4 need review, 100 don't apply (no gift, not an ARM, etc.), 845 aren't implemented yet. **The engine knows what to check and what to skip.**"

**Which story is stronger?** The second one — it shows **intelligent applicability gating**, not just blind execution. But the first one is **sufficient to prove determinism + defect detection**, which is the core demo thesis.

**Verdict:** NOT_APPLICABLE is a **post-demo enhancement**, not a pre-demo blocker. Implement the **minimal version (5 shapes, 1 day)** if time allows before the demo; otherwise defer to the production build phase.

---

## 7. Recommended Approach

### Phase 0 (Pre-Demo, Optional, 1 day)
**Goal:** Prove NOT_APPLICABLE works on 1 shape (GiftEvidenceShape).

**Steps:**
1. Add `caro:requiresField "gift_transfer_evidence_in_file"` to `GiftEvidenceShape`.
2. Implement `check_applicability()` in `run_audit.py` (10 lines of code).
3. Run loan 01 (no gift) and loan 02 (gift with missing evidence).
4. **Expected results:**
   - Loan 01: GiftEvidenceShape → NOT_APPLICABLE (field doesn't exist).
   - Loan 02: GiftEvidenceShape → FAIL (field exists, value is false).
5. If it works, commit. If not, revert and defer.

**Risk:** Minimal. Only touches 1 shape + 10 lines of engine code. Revertible in 5 minutes.

---

### Phase 1 (Post-Demo, Production Build, 3 weeks)
**Goal:** Full NOT_APPLICABLE support for all 91 doc-presence checks + 12 mapped shapes.

**Steps:**
1. Data contract expansion (new fields: property_type, unit_count, occupancy_type, self_employed).
2. Ruleset precondition annotation (91 doc-presence rules).
3. Shape precondition annotation (12 mapped shapes).
4. Engine generalization (handle `rule_preconditions` + `caro:appliesToX` metadata).
5. Testing & validation (all 5 loans, spot-check 20 NOT_APPLICABLE results).

**Gate:** Before this goes to production, an **SME must review** the precondition annotations (compare against the Selling Guide and AMQ source rows). This is the same review gate as the ruleset itself (decision 001's "SME validates the compiled artifact").

---

## 8. Open Questions for SME / Gordon

1. **Is the "didn't apply" distinction load-bearing for the October demo?** Or can it wait until the production build?
2. **Who defines preconditions for the 91 doc-presence rules?** The compiler (automatic inference from doc name) or an SME (manual review)?
3. **Should NOT_APPLICABLE count as a "good" outcome (like PASS) or neutral?** For workbook stats: is "900 didn't apply" reassuring (efficient gating) or concerning (too many exclusions)?
4. **How does Kayla's QC workflow treat "didn't apply"?** Does she want to see them in the UI, or are they hidden (only FAIL / NEEDS_REVIEW shown)?

---

## 9. Summary

| Aspect | Design Choice |
|---|---|
| **Detection logic** | Metadata-driven (`caro:requiresField` + `rule_preconditions`), with runtime check before SHACL runs. |
| **Engine integration** | Pre-validation filter (line 250 of `run_audit.py`). Inapplicable shapes never execute. |
| **Most affected rules** | 91 doc-presence checks (biggest impact), 12 mapped shapes (needs annotation), 4,047 unmapped (future work). |
| **Auto vs. SME** | ~70% auto-detectable (if precondition field exists in extraction); 30% need SME annotation or data expansion. |
| **Complexity** | Minimal (1 day, 5 shapes) or Full (3 weeks, all rules). |
| **Demo-blocker?** | No. Sufficient without it; stronger with it. Recommend Phase 0 (1 shape proof) if time allows. |
| **Production gate** | SME review of all precondition annotations before deployment (same as ruleset review gate). |

**Next step:** Gordon / Kayla decide: (1) defer entirely to post-demo, (2) do Phase 0 (1 shape proof), or (3) do full implementation now (3 weeks).
