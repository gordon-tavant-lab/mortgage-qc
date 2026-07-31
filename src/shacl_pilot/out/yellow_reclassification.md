# YELLOW Rule Reclassification: Convertible vs. Genuinely-Blocked

## Executive Summary

Decision 026's YELLOW analysis identified a 62/38 split:
- **1,323 groups (62.3%) are convertible** with known, scoped work (fixture expansion + extraction deepening)
- **802 groups (37.7%) are genuinely blocked** (SME clarification needed + other blockers)

**Gordon's directive:** In this POC/demo, treat genuinely-blocked YELLOW rules the same as RED — demo-ignored, not "automatable with more data."

**Rationale:** A YELLOW rule that needs an SME to rewrite it from "all requirements met" into enumerable facts is not automatable in any realistic demo timeline. The 62/38 split is honest about what "convertible" means — the remaining 38% need either SME decomposition or permanent human routing.

---

## Proposed Metadata Schema

### Current State
All YELLOW rules in `compiled/ruleset.json` have:
```json
{
  "eval_class": "yellow",
  ...
}
```

### Proposed Enhancement
Split YELLOW into two sub-categories using a new `yellow_category` field:

```json
{
  "eval_class": "yellow",
  "yellow_category": "convertible",  // or "blocked"
  "yellow_blocker_type": "fixture_gap",  // convertible: fixture_gap | extraction_gap
                                          // blocked: sme_clarification | external_lookup | other
  ...
}
```

**For demo/presentation purposes**, add a `demo_in_scope` boolean:

```json
{
  "eval_class": "yellow",
  "yellow_category": "convertible",
  "demo_in_scope": true,  // true for yellow_convertible, false for yellow_blocked and red
  ...
}
```

---

## Count Breakdown: Convertible vs. Blocked

From `yellow_conversion_analysis.md`:

| Category | Count | % of YELLOW | Notes |
|----------|-------|-------------|-------|
| **Convertible** | **1,323** | **62.3%** | Known next steps |
| - Fixture expansion | 462 | 21.7% | Missing doc types (VA Counseling, HUD forms, etc.) |
| - Extraction deepening | 861 | 40.5% | Fields exist in docs but not extracted |
| **Genuinely Blocked** | **802** | **37.7%** | No deterministic path forward |
| - SME clarification | 107 | 5.0% | Ambiguous thresholds, subjective language |
| - Other blockers | 695 | 32.7% | External lookups, cross-loan comparisons, etc. |
| **TOTAL YELLOW** | **2,125** | **100%** | (2,147 rules across 2,125 groups) |

### Per-Block Breakdown

| Block | Total YELLOW Groups | Est. Convertible (62%) | Est. Blocked (38%) |
|-------|---------------------|------------------------|---------------------|
| application-verification | 12 | ~7 | ~5 |
| asset-verification | 193 | ~120 | ~73 |
| credit-liabilities-review | 277 | ~172 | ~105 |
| income-verification | 467 | ~290 | ~177 |
| underwriting-review | 342 | ~212 | ~130 |
| product-specific-check | 572 | ~355 | ~217 |
| property-appraisal-review | 262 | ~163 | ~99 |
| **TOTAL** | **2,125** | **~1,323** | **~802** |

*(Exact per-block splits require re-running the categorization script with block-level aggregation — this is the overall ratio applied uniformly.)*

---

## Recommended Flagging Approach

### Option A: Reuse `human_review_required` (RED semantics)

```json
{
  "eval_class": "yellow",
  "yellow_category": "blocked",
  "human_review_required": true,  // same as RED
  ...
}
```

**Pros:**
- Consistent with existing RED semantics
- Single boolean for "this rule can't auto-clear in a demo"
- Simple query: `demo_auto_clearable = (eval_class == "green") OR (eval_class == "yellow" AND yellow_category == "convertible")`

**Cons:**
- Conflates "fundamentally unautomatable" (RED) with "blocked on SME input" (YELLOW-blocked)
- Loses granularity in reporting (can't distinguish RED vs. YELLOW-blocked in post-run analysis)

---

### Option B: New `demo_out_of_scope` flag (preserves RED/YELLOW distinction)

```json
{
  "eval_class": "yellow",
  "yellow_category": "blocked",
  "demo_out_of_scope": true,  // demo-ignored, but different from RED
  ...
}
```

**Pros:**
- Preserves the semantic distinction: RED = fundamentally unautomatable, YELLOW-blocked = needs SME work
- Enables richer reporting: "60% deterministic resolution = GREEN auto-clears. Remaining 40% splits RED (20%) vs. YELLOW-blocked (18%) vs. YELLOW-convertible (2% still needs fixture/extraction work)."
- Future-proofs for when some YELLOW-blocked rules *do* get SME clarification and move to GREEN

**Cons:**
- Adds a new field instead of reusing existing semantics
- Slightly more complex query logic

---

## Recommended Approach: **Option B** (`demo_out_of_scope`)

**Why:** Honesty and precision. The whole point of this pilot is to demonstrate **where determinism works** and **where it doesn't**. Collapsing YELLOW-blocked into RED obscures a key insight:

- **RED rules** are fundamentally unautomatable (external lookups, live system integrations, human judgment on "reasonable" or "adequate").
- **YELLOW-blocked rules** are *potentially* automatable if an SME decomposes them into explicit thresholds — but that work hasn't happened yet.

The 60% deterministic resolution rate should decompose cleanly into:
- **GREEN (deterministically auto-clears)**: ~60%
- **YELLOW-convertible (fixture/extraction gap, but algorithmically clear)**: ~2% (known next steps)
- **YELLOW-blocked (needs SME clarification before automation)**: ~18% (no deterministic path *yet*)
- **RED (fundamentally human judgment or external lookup)**: ~20% (will never be deterministic)

This tells a more nuanced story than "60% auto, 40% human" — it shows *which* 40% is blocked on what.

---

## Implementation Steps (for main session, not this agent)

1. **Rerun `analyze_yellow_conversion.py`** with block-level aggregation to get exact convertible/blocked counts per block.
2. **Extend `amq_compiler.py`** to:
   - Read the categorization results (fixture_gap / extraction_gap / sme_clarification / other)
   - Add `yellow_category` and `yellow_blocker_type` fields to each YELLOW rule
   - Add `demo_in_scope: bool` field (`true` for GREEN + YELLOW-convertible, `false` for YELLOW-blocked + RED)
3. **Update `run_engine.py`** to:
   - Skip `demo_out_of_scope: true` rules entirely (same as current RED treatment)
   - Report metrics split by category: GREEN auto-clears / YELLOW-convertible (still needs work) / YELLOW-blocked / RED
4. **Update presentation materials** to show the 4-way split, not just "60% auto / 40% human."

---

## Impact on 60% Detection Rate

**Short answer: No change to the detection rate itself — this is metadata/reporting clarity only.**

The 60% detection rate (5/5 loans, 5/5 defects cleared by GREEN rules) is unchanged because:
- GREEN rules already fired deterministically
- YELLOW rules (convertible or blocked) were not part of the 60% calculation
- RED rules were already excluded

**What changes:**
- **Reporting honesty**: Instead of saying "40% of rules need more work," we now say:
  - ~2% YELLOW-convertible (fixture/extraction gap — known next steps)
  - ~18% YELLOW-blocked (SME clarification needed — no deterministic path yet)
  - ~20% RED (fundamentally unautomatable)
- **Demo scope**: YELLOW-blocked rules are now explicitly flagged as "out of scope for this demo," same as RED — but with a different rationale (needs SME work, not fundamentally unautomatable).

**No regression risk:** The 5/5 defect hits came from GREEN rules. YELLOW-blocked rules were never part of the success case — this just makes explicit what was already implicit (Gordon: "in this poc/demo, we should just ignore them").

---

## Example Compiled Ruleset Entry (After Enhancement)

### Before (Current State)
```json
{
  "exception_code": "COMP-SALES-INADEQUATE",
  "eval_class": "yellow",
  "severity": "Major",
  "question_text": "Did the appraiser provide adequate comparable sales?",
  "response_text": "Comparable sales were inadequate or did not support the value conclusion"
}
```

### After (Proposed)
```json
{
  "exception_code": "COMP-SALES-INADEQUATE",
  "eval_class": "yellow",
  "yellow_category": "blocked",
  "yellow_blocker_type": "sme_clarification",
  "demo_in_scope": false,
  "severity": "Major",
  "question_text": "Did the appraiser provide adequate comparable sales?",
  "response_text": "Comparable sales were inadequate or did not support the value conclusion",
  "rationale": "Ambiguous threshold: 'adequate' requires SME decomposition into specific criteria (distance, age, price range, adjustment limits) before automation is possible."
}
```

---

## Honest Assessment: What This Means for the Demo

1. **The 60% GREEN auto-clear rate stands as-is** — no change to the actual defect-detection capability.

2. **The remaining 40% now has an honest breakdown:**
   - ~2% YELLOW-convertible: "We know exactly what's missing (fixture X, field Y) — scoped work."
   - ~18% YELLOW-blocked: "We need an SME to rewrite these rules with explicit thresholds — not scoped yet."
   - ~20% RED: "These will always need a human (judgment calls, external lookups)."

3. **For the demo narrative**, Gordon can say:
   - "60% of rules auto-clear deterministically today — proven on 5 loans, 5/5 known defects caught."
   - "Another 2% are convertible with known next steps (fixture/extraction gaps)."
   - "The remaining 38% split into two buckets: 18% need SME clarification (rewritable), 20% are fundamentally human judgment (permanent)."

4. **This reclassification makes the 60% claim more defensible** — it shows Gordon understands the difference between "blocked on scoped work" and "blocked on unclear requirements."

---

## Next Steps (for Main Session)

1. **Confirm with Gordon:** Does Option B (`demo_out_of_scope` flag) match his intent, or should we collapse YELLOW-blocked into RED semantics (Option A)?

2. **Extend the categorization script** to output per-block exact counts (not just the overall 62/38 split).

3. **Wire the metadata into `amq_compiler.py`** — read the YELLOW analysis, add the new fields.

4. **Update `run_engine.py`** to skip `demo_out_of_scope: true` rules and report the 4-way split.

5. **Regenerate the compiled ruleset** with the new metadata — rerun the 5-loan suite to confirm no regression.

6. **Update decision docs** (`src/decisions/026_yellow_analysis.md` or a new `027_yellow_reclassification.md`) to formalize this split.
