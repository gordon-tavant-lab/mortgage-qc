# 026 — GREEN/YELLOW/RED audit breakdown: what runs, what converts, what stays human

**Status:** In progress 2026-07-30

## Context
After 7 blocks triaged (Application, Assets, Credit-Liabilities, Property-Appraisal, Income, Underwriting, Product-Specific), Gordon wants three parallel investigations:

1. **GREEN-only audit on loan 01** — what does a "rules that already work" run actually look like?
2. **YELLOW → GREEN conversion feasibility** — how many can fold in with fixture/extraction work vs. genuinely blocked?
3. **RED categorization** — why are they red, how many, what's the honest picture for demo scope?

## Purpose
Establish the honest current-state coverage (not aspirational), understand what "automatable with more fixture work" actually means in practice, and document what RED truly represents (human judgment vs. missing context vs. ambiguous phrasing).

## Tasks dispatched (parallel)
- Agent A: GREEN-only audit (loan 01, current `mapped` + `doc_presence` rules)
- Agent B: YELLOW analysis (conversion feasibility, count convertible vs. blocked, stats)
- Agent C: RED analysis (categorization by root cause, counts, PoC/demo disposition)

All three write to distinct output files under `src/shacl_pilot/out/` to avoid collisions.

## Results summary

### 1. GREEN-only audit (loan 01)
**Report:** `src/shacl_pilot/out/green_only_audit_loan01.md`

- **Defects caught:** 3 of 5 (60% detection rate)
- **Total GREEN rules:** 103 (12 mapped + 91 doc_presence)
- **Rules run on loan 01:** 28 (after O-FNM program filtering)
- **Shapes loaded:** 11 (not 4) — **block loading effect discovered**: mapping one rule from `assets.ttl` loads the entire file, pulling in 7 adjacent shapes. Two of those "bonus" shapes caught answer-key defects.
- **Missed defects:** 2 — both from blocks with zero mapped rules (credit-liabilities, property-appraisal). Mapping just 1 rule per block would light up those entire blocks.
- **Current block coverage:** 3 of 17 AMQ blocks (18%) — asset-verification, application-verification, income-verification.

**Key finding:** The unit of coverage is the **block** (TTL file), not the individual shape. An SME mapping one assets rule effectively maps the entire assets category. This is a velocity multiplier — instead of mapping 4,166 rules one-by-one, map ~17 (one per block) to guarantee at least partial coverage across every AMQ category. The 16% deliberately-mapped count understates actual runtime coverage (44%).

**Path to 100% on loan 01:** Map 1 rule each from credit-liabilities and property-appraisal (< 10 minutes).

**Verdict:** GREEN is more effective than expected due to block loading, but coverage gaps are arbitrary. Not production-ready, but a solid proof-of-concept for deterministic, citation-backed QC.

---

### 2. YELLOW → GREEN conversion feasibility
**Report:** `src/shacl_pilot/out/yellow_conversion_analysis.md`

- **Total YELLOW:** 2,125 groups / 2,147 rules
- **Convertible with known next steps:** 1,323 groups (62.3%)
  - **462 groups** blocked on missing fixtures (legitimate doc types not yet in synthetic loans — Decision 014 validated)
  - **861 groups** blocked on extraction deepening (fields exist in docs but not yet extracted — assumes Touchless can be extended)
- **Genuinely blocked:** 802 groups (37.7%)
  - **107 groups** need SME clarification (ambiguous thresholds, subjective language like "adequate," "reasonable," "appears to need more space")
  - **695 groups** have other blockers (complex cross-file logic, external lookups, program-specific rules without clear data sources)

**Per-block breakdown:**
- application-verification: 12 YELLOW
- asset-verification: 193 YELLOW
- credit-liabilities-review: 277 YELLOW
- income-verification: 467 YELLOW (most extreme YELLOW skew)
- underwriting-review: 342 YELLOW
- product-specific-check: 572 YELLOW (near-zero dedup — agency-fragmented by nature)
- property-appraisal-review: 262 YELLOW

**What "automatable" really means:** 62% are convertible *if* the fixture set expands and Touchless extraction deepens — not convertible today without that upstream investment. The remaining 38% need SME decomposition (turning "all requirements met" into enumerable facts) or stay genuinely blocked (external APIs, cross-loan comparisons).

**Honest assessment:** Fixture-blocked rules are genuinely convertible (Decision 014 is legitimate). Extraction-blocked rules assume Touchless can be extended. SME-blocked rules need human decomposition before any automation is possible.

---

### 3. RED categorization & demo recommendation
**Report:** `src/shacl_pilot/out/red_categorization.md`

- **Total RED:** 409 rules (43% of Post-Closing ruleset) across 397 groups
- **By root cause:**
  - **Narrative judgment** (187 rules, 45.7%) — inherently human decisions ("adequate," "reasonable," "appears") that cannot be automated
  - **External data** (187 rules, 45.7%) — requires APIs/lookups not in closed-loan file (NMLS, appraisal review services)
  - **Ambiguous/vague** (29 rules, 7.1%) — no clear pass/fail threshold; needs SME decomposition
  - **Other** (4 rules, 1.0%) — out-of-scope or system-specific checks
  - **Cross-loan comparison** (2 rules, 0.5%) — portfolio-level data required

**Key finding:** Property-appraisal-review dominates with 317 RED rules (77.5% of all RED) — this block is inherently narrative-heavy. This explains the 0/46/54 GREEN/YELLOW/RED split from Decision 020.

**Demo recommendation: Flag RED as "Human Review Required" (Option A)**
- Rules get `human_review_required: true` flag at compile-time
- Auto-route to Exception Review queue with label **"Requires Expert Judgment"**
- Demo narrative: *"We deterministically clear the objective checks and intelligently route judgment-required cases to expert review with full traceability"*
- Metric focus: resolution rate + exception routing accuracy (not "pass/fail")
- **DO NOT fake automation** (Option C) — violates Non-Negotiable #1 and destroys regulatory audit story

**Three-phase path:**
1. **Phase 1 (Demo):** Implement Option A — honest routing, not fake automation
2. **Phase 2 (Post-demo):** SME decomposition sprints (target ambiguous/vague — 29 rules, high leverage) + external API integration (target external_data — 187 rules)
3. **Phase 3 (Productization):** Accept that 187 narrative judgment rules stay human — build best-in-class reviewer UX

**Key insight:** RED is not failure — it's a feature. A system that explicitly routes subjective cases to human experts while auto-clearing deterministic ones is trustworthy. The demo narrative should frame RED as intelligent routing, not system limitation.

---

## Implications for demo scope & roadmap

### Current state (honest numbers)
- **GREEN (automatable today):** 103 rules (2.5%) — but block loading gives 44% shape coverage
- **YELLOW (automatable with work):** 2,147 rules (51.5%) — 62% convertible with fixture/extraction investment, 38% genuinely blocked
- **RED (stays human or needs major decomposition):** 409 rules (9.8%) — 43% of ingested ruleset
- **Unmapped (not yet triaged):** 4,047 rules (97.2%) — 9 blocks remain untouched

### What the demo can honestly claim today
- **Deterministic auto-clearing:** 103 GREEN rules catch real defects (60% on loan 01) with full citation traceability
- **Intelligent exception routing:** 409 RED rules flagged for expert review (not faked, not hidden)
- **Scalability story:** Block-level loading means mapping 1 rule per category lights up the entire category — velocity multiplier for SME authoring

### What the demo should NOT claim
- Production-grade coverage (3 of 17 blocks mapped is 18%, not comprehensive)
- YELLOW rules are automatable "soon" without acknowledging the upstream fixture/extraction dependency
- RED rules will eventually be automated (187 narrative-judgment rules stay human, period)

### Next steps (prioritized)
1. **Immediate (< 1 hour):** Map 1 rule each from credit-liabilities and property-appraisal → loan 01 hits 5/5
2. **Short-term (< 1 day):** Run GREEN-only audit on all 5 loans → see 25-defect detection rate
3. **Demo prep:** Implement RED → "Human Review Required" UI treatment (Option A from RED report)
4. **Medium-term:** Triage the remaining 9 untouched blocks (insurance, closing-documents, data-validation, loan-documents, information-integrity, appraisal-form-1033, certification-delivery, EPD, compliance)

## Related decisions
- [017](017-assets-block-triage.md) through [023](023-product-specific-block-triage.md) — the 7 block triages establishing GREEN/YELLOW/RED baseline
- [024](024-doc-presence-classifier-fix.md) — classifier fix reducing false GREENs 135→91
- [013](013-poc-no-sme-gate.md) — PoC proceeds without SME sign-off, informs what's acceptable for demo
