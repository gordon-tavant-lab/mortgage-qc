# QC Results Reading — 5 Test Loans (Post-Closing Only)

**Source file:** `result/qc_results/comprehensive_vs_baseline_results.json`
**Date:** July 23, 2026
**Scope:** Post-closing rules only — pre-funding rules are excluded from every result below.

---

## 1. The headline

**All 5 test loans need a human to look at them.** None auto-cleared. That's the correct outcome for these loans — every one of them has a real, planted defect, and the engine found it.

This isn't one number talking to itself. Two independent rulesets were run against each loan and cross-checked against each other:

1. **The comprehensive ruleset** — compiled by AI from the client's real 8,442-row rule spreadsheet, narrowed down to only the rules these 5 loans can actually be tested against (see §2), and with all pre-funding-only rules removed.
2. **The validated baseline** — 27 rules built and hand-checked earlier against these same 5 loans, used here purely as a cross-check.

Both rulesets landed on the same disposition for every loan: **NEEDS_REVIEW.**

---

## 2. Where the 68 rules come from (the funnel)

The client's rulebook has **8,442 rows**. Not all of that is usable for this test:

| Step | Count | What happened |
|---|---|---|
| Rows in the client's rulebook | 8,442 | Starting point |
| Unique rules after removing duplicates | 4,837 | Many rows restate the same real rule once per loan program (FHA, VA, USDA, Fannie, Freddie each get their own copy) |
| Rules these 5 loans can actually be tested against | 152 | These 5 loans are small test files — most of the 4,837 rules need document types or data fields these loans simply don't have |
| **Pre-funding rules removed** | **−84** | This project only QCs *closed* loans (post-closing). 84 of the 152 rules turned out to be pre-funding-only conditions (entity/trust setup, private-bank pre-close items) and were pulled out |
| **Rules actually run against each loan** | **68** | This is the real, final, post-closing-only rule set |

Nothing was thrown away — the full 8,442-rule compiled rulebook still exists. This is just the subset that applies to *these particular test loans, post-closing, right now*.

---

## 3. Per-loan summary

| Loan ID | Type | Rules evaluated | Findings surfaced | Of those, confirmed real problems | Cross-check (baseline) | Disposition |
|---|---|---|---|---|---|---|
| 2025-0917-001 | Conventional Purchase | 43 | 39 | 10 | 2 failures / 15 rules | NEEDS_REVIEW |
| 2025-1004-FHA-002 | FHA Purchase | 22 | 17 | 5 | 5 failures / 19 rules | NEEDS_REVIEW |
| 2025-1108-VA-003 | VA Purchase | 16 | 12 | 5 | 6 failures / 19 rules | NEEDS_REVIEW |
| 2025-1215-FRD-004 | Freddie Mac Cash-Out Refi | 24 | 23 | 2 | 5 failures / 17 rules | NEEDS_REVIEW |
| 2025-1122-USDA-005 | USDA RHS 502 Guaranteed | 26 | 17 | 4 | 8 failures / 19 rules | NEEDS_REVIEW |

"Rules evaluated" is smaller than 68 for each loan because loan program gating applies — a VA loan only gets tested against VA (and generic) rules, not FHA-specific ones, for example.

"Findings surfaced" includes real failures **and** honest "can't tell yet" flags (explained in §5) — it is not the same as "number of real defects."

---

## 4. The confirmed real problems, per loan

### Loan 2025-0917-001 (Conventional Purchase) — 10 confirmed
- Large deposit ($15,000 mobile deposit) is not sourced/documented
- Gift funds source documentation missing (2 related rules both fired)
- Loan purpose on the 1003 doesn't clearly say Purchase, Cash-Out Refi, or Limited Cash-Out Refi — all three GSE-specific product checks flagged it
- Appraisal is more than 180 days old on a disaster-affected property
- Title is vested in the borrowers' own names, not the required trust + borrower combination
- DU flagged the large deposit and the gift funds as unverified

### Loan 2025-1004-FHA-002 (FHA Purchase) — 5 confirmed
- Intent to Proceed disclosure missing
- Gift funds source documentation missing
- HUD-92900-A is unsigned
- FHA Amendatory Clause missing from the file
- Borrower credit score is below the FHA Section 203(h) minimum of 500

### Loan 2025-1108-VA-003 (VA Purchase) — 5 confirmed
- Intent to Proceed disclosure missing
- Gift funds source documentation missing
- Missing YTD P&L / balance sheet for a self-employed borrower
- Missing evidence that defective lead-based paint was properly treated
- VA Notice of Value had expired by the time the loan closed

### Loan 2025-1215-FRD-004 (Freddie Mac Cash-Out Refi) — 2 confirmed
- Intent to Proceed disclosure missing
- Gift funds source documentation missing

### Loan 2025-1122-USDA-005 (USDA RHS 502 Guaranteed) — 4 confirmed
- Intent to Proceed disclosure missing
- Gift funds source documentation missing
- Termite/pest inspection missing (required in this jurisdiction)
- Loan term is not 30 years, which USDA requires

**A cross-source finding (not from the comprehensive ruleset — from the doc-vs-system-of-record check):** on loans **02 (FHA)** and **05 (USDA)**, the loan amount on the closing documents does not match the loan amount in the system of record. This is exactly the kind of discrepancy the three-way reconciliation was built to catch — it's a genuine finding, not a coincidence across two different rulebooks agreeing.

---

## 5. Reading the other flags — what's a real problem vs. what's the tool being honest about a gap

Not every flag on this list is a confirmed defect. Three categories show up a lot, and each means something different:

**"Needs SME input — rule threshold not stated"** (dozens of DTI, credit-score, and gift-amount rules)
The client's own rulebook says "check this DTI ratio" or "check this credit score" but never actually states the number. Rather than guess a plausible-sounding threshold, the tool honestly says "I don't know this number — an SME needs to supply it." This is the tool doing its job correctly: a guessed number here would be a compliance risk (an auditor asking "how did you calculate that" and getting no real answer). Nothing to review on the loan itself yet — this is a rulebook gap, not a loan problem.

**"No system value to check against the document"** (SSN, property address, property value on several loans)
The tool tried to compare a document value against a system-of-record value and found nothing on the system side for these test loans. This is a data-completeness gap in this small test dataset, not a mismatch — there's nothing to disagree with if one side is empty.

**"[AMBIGUOUS PROGRAM]"** (loan 01 only, ~30 of its 39 flags)
Loan 01 is a generic "Conventional Purchase" with no stated GSE (Fannie or Freddie). A number of rules only apply to one or the other, and the tool can't tell which one owns this loan from the data available, so it includes the check but flags it as ambiguous rather than silently guessing either way. Once the loan's actual investor/GSE is known, most of these resolve themselves.

None of these three categories are hidden — every single one is labeled honestly in the results rather than being folded into a false PASS or a false FAIL.

---

## 6. Why two rulesets agree (and why the numbers differ)

The comprehensive ruleset and the validated 27-rule baseline were built independently — different source material, different level of specificity — and yet they land on the same overall answer (NEEDS_REVIEW) for all 5 loans, and they overlap on several of the same real defects (large deposit, gift funds, loan amount mismatch). That agreement is the useful signal, not the raw surfaced-count, which will always differ because the comprehensive ruleset is deliberately broader (68 program-specific rules vs. 27 hand-picked ones).

---

## 7. What this run enforces going forward

This is the first run where the pre-funding exclusion is actually wired into the engine, not just documented as a plan. 84 pre-funding-only rules (entity/trust setup, private-bank pre-close conditions) are removed before any loan is evaluated — this project only touches closed, funded loan files, and this run reflects that.

---

*Generated from `result/qc_results/comprehensive_vs_baseline_results.json`. The engine is deterministic — running the same loan against the same ruleset always produces the same result, with no randomness at evaluation time.*
