# GREEN-Only Audit — Artifact Index

**Date:** 2026-07-30  
**Purpose:** QC audit on loan 01 using ONLY GREEN-classified rules (mapped + doc_presence)

---

## Files in This Directory

### Executive Deliverables
1. **GREEN_AUDIT_EXECUTIVE_SUMMARY.md** (4.6 KB) — START HERE
   - 1-page summary for stakeholders
   - Bottom line: 3/5 defects detected (60%)
   - Path to 100%: map 2 more blocks (10 min)
   - Key insight: block loading effect

2. **green_only_audit_loan01.md** (12 KB) — FULL TECHNICAL REPORT
   - Complete findings for all 3 detected defects
   - Citations, shape metadata, reconciliation vs answer key
   - Surprising finding: block loading brought 7 bonus shapes
   - Honest assessment of GREEN's actual capabilities
   - Next steps (immediate / short-term / medium-term)

### Technical Artifacts
3. **green_audit_run.txt** (5.5 KB) — console output from the audit run
4. **loan_01_green_extraction.json** (17 KB) — extraction data for loan 01
5. **run_green_audit.py** (parent dir) — audit runner script (GREEN-filtered, loan 01 only)

---

## Key Findings Summary

### Detection Rate
- **3 of 5** answer-key defects detected (60%)
- Better than expected given only 3 of 17 blocks are mapped

### Detected Defects
1. ✅ Employment dates mismatch (EmploymentStartDateShape)
2. ✅ Title vesting inconsistency (TitleVestingShape)
3. ✅ Unsourced large deposit (LargeDepositShape)

### Missed Defects
4. ❌ Undisclosed liability (UndisclosedLiabilityShape) — credit-liabilities block not loaded
5. ❌ Appraisal comp distance (CompDistanceShape) — property-appraisal block not loaded

### Block Coverage
- **Loaded:** 3 blocks (asset-verification, application-verification, income-verification)
- **Missing:** 14 blocks (including credit-liabilities, property-appraisal)
- **Total:** 3 of 17 blocks (18%)

### Shape Coverage (Due to Block Loading)
- **Deliberately mapped:** 4 shapes (16% of 25 pilot shapes)
- **Actually loaded:** 11 shapes (44% of 25 pilot shapes)
- **Fired (detected issues):** 3 shapes

---

## Surprising Finding: Block Loading Effect

When you map 1 rule from a block, the entire TTL file loads → all shapes in that block become available.

**Example:**
- Map `LargeDepositShape` (1 of 8 shapes in assets.ttl)
- Get all 8 assets shapes for free
- 2 "bonus" shapes caught defects (EmploymentStartDateShape, TitleVestingShape)

**Implication:** Coverage is better than the 12-mapped-rules number suggests, but also unpredictable (depends which blocks got one mapped rule).

**Recommendation:** Surface this in the authoring UX: "Mapping this rule will load the entire ASSETS block (8 shapes)."

---

## Path Forward

### To Hit 5/5 on Loan 01 (10 minutes)
1. Map 1 rule from credit-liabilities → loads UndisclosedLiabilityShape
2. Map 1 rule from property-appraisal → loads CompDistanceShape
3. Re-run audit → should detect all 5 defects

### To Get Production Coverage (~3 hours)
1. Map 1 rule from each of the 14 unmapped blocks
2. All 17 TTL files load → all 25 pilot shapes available
3. Run full 5-loan regression → measure cross-loan performance

---

## How to Run

```bash
cd /Users/gordonchan/Workspace/demo-sites/mortgage-qc-prod/src/shacl_pilot
python3 run_green_audit.py
```

Output goes to:
- Console (also saved to `out/green_audit_run.txt`)
- `out/loan_01_green_extraction.json` (extraction data)

---

## Related Files

- `compiled/ruleset.json` — full 4,166-rule compiled ruleset (GREEN rules are a 103-rule subset)
- `answer_keys/loan_01_answers.md` — ground truth for loan 01's 5 defects
- `blocks/*.ttl` — SHACL shape definitions (one TTL file per AMQ block)
- `run_audit.py` — full audit runner (all 5 loans, all applicable rules)

---

## Questions to Answer Next

1. **Cross-loan performance:** What's GREEN's detection rate on loans 02-05? (25 total defects)
2. **Block priority:** Which 2-3 blocks should we map next based on miss patterns?
3. **Authoring UX:** How do we surface "this rule loads entire X block" to SMEs?
4. **Loader behavior:** Should we keep block-level loading or switch to shape-level?

---

## Contact

- **Audit runner:** SHACL Pilot QC Agent (agent-driven analysis)
- **Project owner:** Gordon Chan (Director of AI, Tavant)
- **Context:** Mortgage QC SHACL pilot (deterministic post-closing QC engine)
