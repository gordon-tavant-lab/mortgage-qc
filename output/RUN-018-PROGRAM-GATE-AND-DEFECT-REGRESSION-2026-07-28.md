# run_018 Program Gate Fix + Loan-01-vs-Answer-Key Defect Regression

**Date:** 2026-07-28
**Trigger:** Gordon asked a chain of questions about `run_018_guideline_to_loan01_e2e`'s output ("is loan 01 really Fannie Mae?", "it looks like it's broke again", "run the regression test", "do we need to document #4/#5 before fixing, or can we just fix them?") — each answered by direct code/data inspection, not assumption.

---

## 1. Program-gate bug in run_018 (fixed)

`run_018` ran loan 01 against all 3,203 compiled checks with **no program-applicability scoping** — Fannie Mae, Freddie Mac, FHA, VA, and USDA checks all mixed together, producing an inflated, dishonest picture (85 FAIL, 2,377 NEEDS_REVIEW unscoped). This was a bug in the new demo script, not a regression in spec 015's already-committed program-gating fix (`program_gating.py`'s `applies_to()`/`Applicability`/`AMBIGUOUS`, already proven working in `run_015_loan_01_comprehensive_qc/build_and_run.py`).

**Fix:** `run_018` now reuses run_015's exact classification pattern — post-hoc, per-check-id lookup against `result/rules/post_closing_only_applicability.json` (all 3,203 v8 check IDs covered, zero `NO_TAG_FOUND`) — logged under a new `program_gate` stage tag in `storage/logs/run_018_guideline_to_loan01_e2e.jsonl`.

Properly scoped (Fannie Mae + untagged, 1,076 of 3,203 checks): `NOT_APPLICABLE=290, NEEDS_REVIEW=762, FAIL=20, PASS=4` — far more honest than the unscoped `FAIL=87, NEEDS_REVIEW=2,375`. (The scoped FAIL count of 20, not 18, reflects the two corrections from §2 below now firing correctly within scope.)

## 2. Two of loan 01's 5 known defects were miscompiled (fixed)

A direct regression check of loan 01's QC output against `defect_manifest.json`'s 5 documented defects found only 1 of 5 correctly caught as FAIL. Root-caused and fixed:

| # | Defect | Check | Before | Root cause | After |
|---|---|---|---|---|---|
| 1 | Employment date: 1003 (03/15/2018) vs VOE (05/01/2019) | `employment-dates-1003-vs-docs-agree` | NEEDS_REVIEW | Miscompiled as `agree_categorical` (doc-vs-**system**, compares against `sv.system_value()` which is `None`) instead of `agree_doc_categorical` (doc-vs-**doc**) with `compare_field_name: employment_start_date_voe` | **FAIL** |
| 2 | Title vesting: 1003 ("a married man") vs Title Commitment (TBE) | `title-vesting-1003-vs-commitment` | NEEDS_REVIEW | Same miscompile pattern — needs `compare_field_name: title_vesting_commitment` | **FAIL** |
| 3 | Unsourced $15,000 large deposit | `large-deposit-source-not-acceptable` | FAIL | Already correct | FAIL (unchanged) |

Both `employment_start_date_voe` and `title_vesting_commitment` are real, catalogued, populated fields in `field_catalog.json` and loan 01's fixture — the correction is a deterministic 2-field kind/compare_field_name fix, zero LLM. Applied via a new shared module, `p0/qc_engine/compiler/known_compile_corrections.py`, imported by both `run_018` (so the persisted `comprehensive_e2e_v8_ruleset.json` artifact reflects the fix) and the new regression test (so they can't drift out of sync).

**Follow-up flag, not resolved here:** zero checks in the entire 3,203-check v8 ruleset use `agree_doc_categorical` — this miscompile pattern may be systemic across other doc-vs-doc checks that happen to share a field name pattern with doc-vs-system checks. Worth a dedicated audit.

## 3. Defect #4 (undisclosed liability) — genuinely not a quick patch

The undisclosed $412/mo Ally Bank auto liability (confirmed present on the real credit report PDF via `pdftotext`, not on the 1003's disclosed liability list) is shaped in `defect_manifest.json` exactly like #1/#2 (`doc_1003: null` vs `doc_credit_report: "412.00"`, `expected_relationship: "mismatch"`), so the same fix was checked first — it doesn't work:

- The check's `applies_if` precondition, `credit_report_present_for_all_applicants`, **does not exist in `field_catalog.json` at all** (0 matches) — a genuinely uncatalogued field, unlike #1/#2's compare fields, which were already catalogued and populated. Confirmed live: the check resolves to `NEEDS_REVIEW` / `APPLICABILITY_UNKNOWN` today because the engine can't evaluate a precondition on a field that doesn't exist in `loan.fields`.
- The check (`undisclosed-debt-dti-gap`) is also compiled with `kind: ratio_threshold`, `threshold: "UNSPECIFIED"` — a second, independent reason it can't produce a real verdict, even setting the missing-field issue aside.
- The real defect isn't "does 1003 match credit report on a shared field" (like employment dates/title vesting) — it's "does a trade line on the credit report appear **anywhere** in the 1003's own disclosed liability list." That's set-membership / line-item reconciliation. `engine.py`'s six check kinds (`predicate`, `ratio_threshold`, `agree_categorical`, `agree_numeric`, `agree_doc_categorical`, `agree_doc_numeric`) all compare exactly one value against one reference; none checks list membership.

Building this needs a new check-kind design + engine support — tracked as `output/ROADMAP.md`'s `018-set-membership-check-kind`, not resolved in this change. The new regression test asserts this as `xfail(strict=True)`, so it stays visible in every future `pytest -v` run and fails loudly (not silently green) the moment it's actually fixed.

## 4. Defect #5 (appraisal comp distance) — confirmed source-data absence, not a code gap

Comp #2's 8.5-mile distance exceeding "the Citizens QC checklist" 5-mile guideline has **no corresponding check anywhere in the ruleset**. Searched both sheets of the real AMQ source workbook (`PF and PC Sept 2025 AMQs - Retail.xlsx`) directly: Post-Closing (5,520 rows) and Pre-Funding (4,825 rows, the sheet this project doesn't ingest — checked specifically to rule out "it's in the sheet we skip") — **zero matches in either sheet** for any comp-distance/mileage rule.

This corroborates an independent, earlier finding: `output/RULE-FIDELITY-AUDIT-2026-07-22.md` §3 already flagged `chk-def-appraisal-comp-distance`'s 5-mile threshold as ungrounded, searching a related 8,442-row AMQ dataset and finding no matching row either. Two independent searches, two different (but related) source snapshots, same conclusion.

One superficially similar check exists in the v8 ruleset — `va-appraisal-comp-distance-explanation` — but it's VA-program-tagged (loan 01 is Fannie Mae, out of scope per §1's gate) and is a `predicate` check for "is an explanation present," not a mileage-threshold check. Doesn't change the conclusion.

**This isn't a compile bug, a coverage gap, or an ingestion-scope issue — the rule doesn't exist in the source this project has.** Nothing to fix in this codebase; the honest, complete answer is this documentation entry, not a ROADMAP item (there's no future code work to track).

## 5. AMQ workbook ingestion scope (durable fact)

`run_018` (and every prior comprehensive-ruleset compile run) ingests **Post-Closing only** from `PF and PC Sept 2025 AMQs - Retail.xlsx` (5,520 rows → 944 of the resulting checks). **Pre-Funding (4,825 rows, 856 potential checks) has never been ingested** by this project's compile pipeline. This is a standing scope fact, not a bug — flagged here so it stays visible; see `run_009_prefunding_exclusion/identify_prefunding_checks.py` for the original scoping decision.

## 6. Product/portfolio precondition-completeness gap (carried from a prior session)

Checks gating on loan product (HomeReady) or portfolio/CTP status (Portfolio CTP) can't resolve applicability — the same class of gap spec 015's Field & Precondition Coverage Gate was built to make repeatable, applied to a dimension that gate's first pass didn't fully close. Tracked as `output/ROADMAP.md`'s `017-precondition-completeness-loan-product-portfolio`.

## Net result

Loan 01's 5 documented defects: **1 of 5 correctly caught → 3 of 5** (employment date + title vesting now fire FAIL; large deposit already did). Defect #4 needs a new engine capability (tracked, `xfail`-guarded). Defect #5 is a closed, answered question about source data, not an open gap.
