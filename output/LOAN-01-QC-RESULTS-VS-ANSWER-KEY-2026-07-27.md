# Loan QC Results — Summary & Answer-Key Check

**Run date:** 2026-07-27 · **Source:** `p0/export_qc_results_xlsx.py` against the 5 real synthetic loans in `demo/syn/`, using the known-defects fixture ruleset (`p0/fixtures/ruleset_defects.py`) — the ruleset directly tied to the 25 planted, ground-truth defects across the 5 loan files.

---

## Part 1 — All 5 Loans, at a Glance

| Loan | Type | Disposition | Checks Run | Pass | Fail | Needs Review | N/A |
|---|---|---|---|---|---|---|---|
| 2025-0917-001 | Conventional Purchase | NEEDS_REVIEW | 20 | 7 | **4** | 1 | 8 |
| 2025-1004-FHA-002 | FHA Purchase | NEEDS_REVIEW | 24 | 2 | 5 | 6 | 11 |
| 2025-1108-VA-003 | VA Purchase | NEEDS_REVIEW | 24 | 3 | 6 | 4 | 11 |
| 2025-1215-FRD-004 | Freddie Mac Cash-Out Refi | NEEDS_REVIEW | 22 | 4 | 7 | 2 | 9 |
| 2025-1122-USDA-005 | USDA RHS 502 Guaranteed | NEEDS_REVIEW | 24 | 2 | 8 | 4 | 10 |

Every loan lands on **NEEDS_REVIEW** — none auto-clear yet at this ruleset's scale, because this focused set is deliberately weighted toward the planted defects (a much larger share of real, gated rules pass cleanly in the full 8,442-row rulebook run — see `output/END-TO-END-QC-RESULTS-2026-07-26.md`). This document isolates just **Loan 1**, the one with a published answer key, to prove the engine's verdicts against a known-correct ground truth.

---

## Part 2 — Loan 1 vs. the Answer Key

**Loan #2025-0917-001** — Smith / Charlotte, NC · Conventional Purchase · $340,000 / $425,000 (80% LTV)

The loan package (`demo/syn/loan 01/00_Loan_Summary_And_Answer_Key.pdf`) has **5 intentionally planted defects**, each with a known correct answer. Below: the answer key's claim, side-by-side with what the QC engine actually returned when run against the same documents today.

| # | Planted Defect (Answer Key) | Engine Check | Engine Verdict | Match? |
|---|---|---|---|---|
| 1 | Employment start date on 1003 (03/15/2018) doesn't match VOE/paystub (05/01/2019) | `chk-def-employment-dates-agree` | **FAIL** — "Employment start date on the final 1003 does not match the VOE/paystub." | ✅ Caught |
| 2 | Title vesting on 1003 ("John A. Smith, a married man") doesn't match Title Commitment ("John and Jane Smith, TBE") | `chk-def-title-vesting-agree` | **FAIL** — "Manner in which title is held on the 1003 does not match the title commitment." | ✅ Caught |
| 3 | Unsourced $15,000 large deposit (08/12/2025 bank statement) | `chk-def-large-deposit` | **FAIL** — "Large unexplained deposit lacks source documentation." | ✅ Caught |
| 4 | Ally Bank auto loan ($12,000 / $412 mo) on credit report, not disclosed on 1003 Section 2c | `chk-def-liability-disclosed-agree` | **NEEDS_REVIEW** (`SOURCE_INCOMPLETE`) — "Only one of `liability_disclosed_on_1003` / `liability_amount_credit_report` has a value — cannot compare." | ⚠️ Partial — see note below |
| 5 | Appraisal comp #2 is 8.5 miles from subject, no addenda explanation | `chk-def-appraisal-comp-distance` | **FAIL** — "Comparable sale distance exceeds the 5-mile urban guideline with no addenda explanation." | ✅ Caught |

### Score: 4 of 5 defects caught cleanly as FAIL. The 5th is correctly flagged, not silently missed.

**On #4 — why it's NEEDS_REVIEW, not FAIL, and why that's the engine behaving correctly:**
The credit-report side of this comparison extracted fine — `liability_amount_credit_report` shows the Ally Bank trade line at $12,000/$412mo, cited straight to page 1 of the credit report summary. But `liability_disclosed_on_1003` was never populated during document extraction — there's no automated step yet that scans the 1003's own liabilities section (2c) and asserts "this trade line is absent from it." That's an **upstream extraction gap** (this project's Non-Negotiable #2: extraction is Touchless's contract, not built here), not a rules-engine gap. Given a genuinely one-sided comparison, the engine's honest answer is "cannot compare" — the same discipline used everywhere else in this build (an ambiguous absence routes to a human, it never silently passes or guesses FAIL). The defect is real and currently requires a human reviewer to catch it by reading both documents — exactly the kind of case this tool is built to eventually close as extraction coverage widens.

---

## Part 3 — What This Proves

- The engine's core comparison logic (`agree_doc_categorical` / `agree_doc_numeric` — the doc-vs-doc check kinds added under spec 003d) is **working exactly as designed** against real, known-answer data: 4 of 5 defects fire as clean, auditable FAILs with plain-language explanations and page-cited evidence.
- The one gap is named, understood, and traced to its correct owner (extraction, not the engine) — not swept under a passing test.
- Every verdict above is byte-traceable back to a source document, page, and quoted field label in the full `Check Detail` sheet of `output/QC_Engine_Results_for_Kayla_Review.xlsx`.

---

## Appendix — On the Vocabulary Question (why v2.json still only has one fact)

Separately asked this session: **"are there more vocab than just gift — did we not discover more?"**

Correct observation — `storage/fact_vocabulary/v2.json` (the *signed*, engine-active vocabulary) still has exactly one fact: `gift_funds_used`. This is not a discovery failure. The self-discovery pipeline built earlier this week found **24 candidate questions** (`storage/fact_vocabulary/candidates/v1.json`) and drafted **candidate names for all 24** via a one-time LLM pass (`storage/fact_vocabulary/candidates/naming_proposals_v1.json`, human-readable version: `output/FACT-VOCABULARY-NAMING-PROPOSALS-2026-07-26.md`).

By design, that naming pass is **MEDIUM-tier, review-only** — it is deliberately never auto-promoted into the signed vocabulary the engine reads. Promotion happens only when a human (Kayla, or you) reviews a proposed row in that markdown table and approves it — the same 5-minute review shape already used for the gift fact. Nothing is silently blocked; the 23 remaining questions are drafted, cited, and ready — they're just sitting in the queue, not yet promoted.
