# The Complete Fact Vocabulary — Guideline-Derived, All 24 Questions

**Built:** 2026-07-27 · **Vocabulary:** `storage/fact_vocabulary/v6.json` (16 facts) · **Status:** still `NOT-A-REAL-SME-pending-kayla-review` — nothing below is a substitute for real sign-off.

> **Two corrections, same day:**
> 1. **(caught by a `/g-os-judge` review of v4)** `loan_product_type`'s own description correctly identified it as a **Freddie Mac** fact (real programs: CHOICERenovation®, GreenCHOICE® Mortgage) — but v4 shipped it with 3 citations from the Fannie Mae Selling Guide, the only corpus ingested. No Freddie Mac Guide exists in this system, so those citations could not have been correct regardless of how well-ranked they looked. v5 added a hard pre-retrieval guard so a fact can never cite an investor's Guide the system hasn't ingested.
> 2. **(Gordon's call, after reviewing the v5 fix)** rather than carry `loan_product_type` indefinitely with no citation, it's been **removed from the vocabulary entirely** (`remove_out_of_scope_fact.py` → `v6.json`) — it can be re-added, correctly cited, if a Freddie Mac Selling Guide is ever ingested. Every other fact is untouched; question 571085 (239 AMQ rows) is unbound again until then. This document reflects the current, 16-fact state.

---

## What changed

A week ago this vocabulary had exactly one fact: `gift_funds_used`. You asked why — the answer was never "we didn't find the rest," it was that the rest was drafted but sitting in a review queue, waiting for someone to say "go." This document is that promotion, done: **23 of the 24 questions this project has decoded from the client's own rule workbook now have a canonical fact**, deduplicated, cited back to the real Selling Guide, and disclosed as pending human review exactly like gift always was. (The 24th, a Freddie Mac product-type question, was promoted and then deliberately removed the same day — see the correction above.)

| | Before | After |
|---|---|---|
| Canonical facts | 1 (`gift_funds_used`) | **16** |
| AMQ questions covered | 1 of 24 | **23 of 24** (the 24th, loan product type, was removed — see correction above) |
| Checks with a real, auto-attached precondition (out of 3,203 gated checks) | 15 (0.5%) | **1,530 (47.8%)** |
| Checks flagged, still needing SME review | 2,035 | **520** |
| Regressions (checks that got *worse*) | — | **0** |

That last row is the load-bearing one: expanding the vocabulary made **zero** checks worse. Every check that used to resolve cleanly still does; 1,515 more now resolve cleanly too. (Full numbers: `result/qc_results/run_012_vocabulary_expansion_002g_results.json`.)

---

## Part 1 — Where the 24 questions went

Every proposal came from the same one-time, MEDIUM-tier LLM naming pass already reviewed with you (`output/FACT-VOCABULARY-NAMING-PROPOSALS-2026-07-26.md`). Promoting them surfaced a genuinely useful finding on its own: **the client's own AMQ workbook asks the same real question under multiple different keys.** Three of the 16 facts merge answers from more than one question key — verified, not assumed, that no answer disagrees about its meaning across the merged questions before combining them:

| Fact | AMQ question keys | Why merged |
|---|---|---|
| `loan_transaction_type` | 571083, 571086, 571087 | Same "what kind of transaction is this" question, asked once per loan program (Fannie/VA/general) — no answer contradicts another across the three |
| `appraisal_in_file` | 571197, 571199, 571200, 571202 | Identical question, identical single answer ("Yes, there is an appraisal in the file"), asked under 4 different keys |
| `credit_report_present_for_all_applicants` | 570729–570733 (5 keys) | Same question, minor answer-text punctuation variance only, asked under 5 different keys |

The other 14 facts are one-question-one-fact, no merge needed.

---

## Part 2 — All 16 Facts

| Canonical Fact | Type | AMQ Rows Gated | Top Guide Citation | Review Status |
|---|---|---|---|---|
| `gift_funds_used` | boolean | 362 | B3-4.3-04, Personal Gifts | ✅ Reviewed pattern (original seed) |
| `income_type_used_for_qualification` | enum | 683 | B5-7-03, High LTV Refinance Alt. Qualification Path | Drafted, pending review |
| `closing_funds_asset_type` | enum | 362 (shared w/ gift) | B3-4.1-01, Minimum Reserve Requirements | Drafted, pending review |
| `appraisal_in_file` | boolean | 483 (4 questions) | B4-1.3-05, Improvements Section of the Appraisal Report | Drafted, pending review |
| `loan_transaction_type` | enum | 424 (3 questions) | B4-2.1-03, Ineligible Projects | Drafted, pending review |
| `appraisal_waiver_type` | enum | 283 | B4-1.3-05, Improvements Section of the Appraisal Report | Drafted, pending review |
| `credit_report_present_for_all_applicants` | boolean | 329 (5 questions) | B3-5.3-09, DU Credit Report Analysis | Drafted, pending review |
| `loan_collateral_advisor_relief_type` | enum | 109 | D1-3-03, Lender Post-Closing QC Reverifications | Drafted, pending review |
| `automated_assessment_type` | enum | 109 | D1-3-03, Lender Post-Closing QC Reverifications | Drafted, pending review |
| `fha_loan_purpose_type` | enum | 99 | E-3-03, Acronyms and Glossary of Defined Terms | Drafted, pending review |
| `derogatory_credit_item_type` | enum | 67 | B3-5.3-09, DU Credit Report Analysis | Drafted, pending review |
| `borrower_income_type` | enum | 64 | B5-7-03, High LTV Refinance Alt. Qualification Path | Drafted, pending review |
| `du_validation_service_components_received` | enum | 57 | A2-2-03, Document Warranties | Drafted, pending review |
| `hpml_atr_qm_review_required` | boolean | 55 | B2-1.5-02, Loan Eligibility | Drafted, pending review |
| `electronic_closing_used` | boolean | 16 | A2-4.1-03, Electronic Records, Signatures, and Transactions | Drafted, pending review |
| `lep_requirements_met` | boolean | 5 | ⚠️ **None** — see below | Drafted, pending review |

`loan_product_type` (239 rows, question 571085) was promoted, found to be mis-cited, fixed, and then removed the same day — see the correction at the top of this document. It's not a row in this table because it's not in the vocabulary; the 239 rows it would have gated go back to unbound (question 571085 shows as `NEEDS_NAMING` again in `storage/fact_vocabulary/candidates/v1.json`).

Every fact's full detail — every question key, every answer string, every canonical value, every citation, and the exact confidence/rationale the drafting model gave — lives in `storage/fact_vocabulary/v6.json` and its evidence trail `storage/fact_vocabulary/candidates/naming_proposals_v1.json`.

### The one honest gap: `lep_requirements_met`

The 416-section indexed Fannie Mae Selling Guide corpus has no section on Limited English Proficiency requirements — checked directly, not assumed. Rather than attach a plausible-looking wrong citation (three candidate sections were tried; none were actually about LEP), this fact ships with **zero** Guide citations and an explicit note: likely lives in CFPB/fair-lending guidance outside this corpus, flagged for you or Kayla to source manually. The fact itself is still real and usable — only its Guide citation is missing.

---

## Part 3 — What this unlocks right now

With 23/24 questions covered, **1,530 of the 3,203 Retail-only checks** (47.8%) now compile with a real, auto-attached precondition — up from 15. That means well over a thousand checks that used to compile *unconditionally* (running on every loan regardless of program/situation) or sat *flagged* for manual review now correctly gate themselves — e.g., an appraisal-waiver-specific check only fires when `appraisal_waiver_type` says a waiver was actually used, an FHA-purpose check only fires when `fha_loan_purpose_type` says this is that kind of loan.

The remaining **520 flagged checks** are the honest leftovers — cases where either an answer was deliberately abstained during naming (never guessed), a check's source rows disagree on which condition applies, or (171 of them) depend on the now-removed `loan_product_type` question. Those need a human, same as before; they're just far fewer of them now.

---

## Part 4 — Still true, unchanged

- **Nothing here is signed.** `signed_by` on `v6.json` is still the same placeholder — `NOT-A-REAL-SME-pending-kayla-review` — as it always was. Promoting facts is a mechanical, disclosed, code-reviewed step; it is not Kayla's review.
- **Every promoted fact carries a `promotion_note`** disclosing it was LLM-drafted (Sonnet, temp 0) and has not been reviewed by a domain SME — visible on every fact in `v6.json`, not just described here.
- **This does not change any loan's actual QC result yet.** The 5 real synthetic loans (`demo/syn/`) don't have extracted values for most of these 15 new facts — only `gift_funds_used` has a real per-loan derivation today (`storage/loan_profiles/`). This document proves *compile-time coverage*, not *runtime disposition* — extending extraction to populate the other 15 facts is the natural next step, tracked separately from this vocabulary work.

---

## Where everything lives

| Artifact | Path |
|---|---|
| Signed vocabulary (16 facts, latest) | `storage/fact_vocabulary/v6.json` |
| Promotion script (deterministic, no LLM) | `p0/qc_engine/compiler/promote_naming_proposals.py` |
| Citation enrichment script (incl. investor-mismatch guard) | `p0/qc_engine/compiler/build_vocabulary_guide_citations.py` |
| Out-of-scope removal script | `p0/qc_engine/compiler/remove_out_of_scope_fact.py` |
| Full evidence trail per fact (LLM proposals) | `storage/fact_vocabulary/candidates/naming_proposals_v1.json` |
| Coverage-impact proof (this doc's Part 3 numbers) | `result/qc_results/run_012_vocabulary_expansion_002g_results.json` |
| Tests | `p0/tests/test_fact_vocabulary.py`, `test_promote_naming_proposals.py`, `test_build_vocabulary_guide_citations.py`, `test_remove_out_of_scope_fact.py`, `test_fact_candidates.py`, `test_naming_proposals.py` |
