# 027 — Option A + Three Design Decisions

**Status:** In progress 2026-07-30

## Context
After the GREEN/YELLOW/RED audit breakdown (decision 026), Gordon clarified three design decisions and requested Option A execution (map 2 rules to hit 5/5 on loan 01).

## Three Design Decisions

### Decision 1: NOT_APPLICABLE Status for Fixture-Gap Rules
**Problem:** "Check for the gift letter — we just don't have a gift letter in the synthetic loan yet." If the loan doesn't need a gift letter (no gift transaction), the rule should return NOT_APPLICABLE, not FAIL.

**Decision:** Implement NOT_APPLICABLE as a fourth result state alongside PASS/FAIL/NEEDS_REVIEW. Rules evaluate NOT_APPLICABLE when:
- The loan characteristics indicate the rule's precondition isn't met (e.g., no gift, so gift-letter check doesn't apply)
- Distinct from FAIL (document missing when required) and distinct from NEEDS_REVIEW (document present but ambiguous)

**Implementation:** Agent B designing the detection logic and engine changes.

---

### Decision 2: Genuinely-Blocked YELLOW = Ignore in Demo
**Problem:** 802 YELLOW rules (38% of YELLOW) can't convert to GREEN without SME decomposition or external APIs. These aren't "automatable with more data" — they're blocked on human work or outside dependencies.

**Decision:** Treat genuinely-blocked YELLOW the same as RED for demo/PoC purposes:
- 1,323 convertible YELLOW (fixture-gap + extraction-gap) stay YELLOW
- 802 genuinely-blocked YELLOW reclassified as demo-ignored (metadata flag, not run in demo scope)
- Rationale: A "YELLOW" that needs an SME to rewrite it from "all requirements met" into enumerable facts is not automatable in any realistic demo timeline

**Implementation:** Agent C updating the ruleset metadata and decision docs.

---

### Decision 3: RED = "Requires Expert Judgment" (Confirmed)
**Problem:** 409 RED rules (43% of ruleset) — how to handle in demo?

**Decision:** Implement Option A from decision 026's RED report:
- Compile-time flag: `human_review_required: true`
- Auto-route to Exception Review queue with label **"Requires Expert Judgment"**
- Demo narrative: *"We deterministically clear objective checks and intelligently route judgment-required cases to expert review"*
- Do NOT fake automation, do NOT hide RED rules from the demo

**Implementation:** This is a UI/UX task (separate from this session's engine work), but the decision is locked in.

---

## Option A: Map 2 Rules to Hit 5/5 on Loan 01

**Task:** Map 1 rule from credit-liabilities block and 1 rule from property-appraisal block. Recompile, re-run loan 01, confirm 5/5 detection.

**Expected outcome:**
- `UndisclosedLiabilityShape` fires (currently missed defect #4)
- `CompDistanceShape` fires (currently missed defect #5)
- Detection rate: 5/5 (100%)

**Implementation:** Agent A executing in parallel.

---

## Tasks Dispatched (Parallel)
- Agent A: Map 2 rules, recompile, re-run loan 01, report results → `out/option_a_results.md`
- Agent B: Design NOT_APPLICABLE status logic → `out/not_applicable_design.md`
- Agent C: Reclassify genuinely-blocked YELLOW → `out/yellow_reclassification.md`
