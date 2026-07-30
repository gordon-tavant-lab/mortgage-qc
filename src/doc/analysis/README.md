# Analysis Directory — SHACL Pilot Audit Reports

This directory contains formal analysis documents for the SHACL QC pilot, capturing key findings, production projections, and decision rationale.

---

## Documents

### 2026-07-30: Production Audit Analysis
**File:** `2026-07-30_production_audit_analysis.md`  
**Question:** "How can we make this more production-like and not tailored to those 25 defects?"

**Key Findings:**
- **0% false positive rate** (0/26 findings)
- **100% detection rate** (25/25 answer-key defects + 1 justified extra)
- **20.8% coverage** (26/125 checks had data to evaluate)
- **79.2% NO_DATA** (pilot scope, not system failure)

**Conclusion:** The audit is NOT tailored to the 25 defects. The 12 shapes are general-purpose checks (doc-vs-doc, threshold math, presence) that work on any loan. The limitation is **coverage breadth** (20%), not precision or tailoring.

**Recommendation:** Deploy the 12 shapes as-is (production-ready), expand to 50 shapes (40 more from YELLOW-convertible set), validate on 20 real loans.

---

## Purpose

These analyses answer stakeholder questions about:
- **Production readiness** — Can we deploy this today?
- **False positive risk** — Will we flood SMEs with incorrect findings?
- **Coverage gaps** — What % of real defects would we miss?
- **Scale projections** — What does 100-loan or 1,000-loan volume look like?

---

## Document Naming Convention

`YYYY-MM-DD_topic_analysis.md`

Example: `2026-07-30_production_audit_analysis.md`

---

## Related Documentation

- **Audit reports:** `../../shacl_pilot/out/` (raw audit outputs)
- **Decisions:** `../../decisions/` (architectural decisions with rationale)
- **Research:** `../../../output/` (strategy docs, theses, one-pagers)
- **Architecture diagrams:** `../../../output/scratch/` (HTML visualization)

---

**Maintained by:** Gordon Chan (Director of AI, Tavant)  
**Last updated:** 2026-07-30
