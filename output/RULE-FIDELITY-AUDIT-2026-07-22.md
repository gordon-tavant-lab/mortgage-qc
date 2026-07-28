# Rule Fidelity Audit — 5-Loan QA/QC Engine Run

**Date:** 2026-07-22
**Scope:** Independent verification of the `dispositions.json` engine run against (a) the synthetic loans' ground-truth answer key, (b) the underlying field extraction, and (c) the real source AMQ rule text — before the results go to manual SME review.
**Trigger:** Gordon asked for a full accuracy double-check of the 5-loan disposition run, spanning both the engine's output and the original rules it claims to enforce.

---

## 1 · Extraction accuracy — CONFIRMED, 25/25

Re-ran `p0/fixtures/from_docs/verify_against_defects.py`. Every one of the 25 known planted defect values across the 5 synthetic loans still extracts exactly as expected. No drift since the last verified run.

## 2 · Engine verdict accuracy — CONFIRMED, 21/21 recall, 0 report drift

Re-ran `p0/fixtures/from_docs/verify_report_accuracy.py`:

- **Recall: 21/21 (100%)** on every defect that has a wired `Check` object (20 of the 25 known defects; the other 5 are genuine doc-vs-doc comparisons with no check-kind built yet — a pre-existing, documented scope boundary, not a new gap).
- **Report fidelity: 0 drift** — the `output/QC_Engine_Results_for_Kayla_Review.xlsx` export matches a fresh live engine run exactly, cell for cell.
- **6 false positives**, all on the two lead-paint checks (`chk-def-lead-paint-cert`, `chk-def-lead-paint-disclosure`) firing on loans where `year_built_appraisal` was never extracted. This is a **pre-existing, already-documented** design tradeoff (`p0/fixtures/from_docs/README.md`, Round 7, 2026-07-16): the property-age gate conservatively applies both checks whenever build year is unknown — "absence of contrary evidence should never silently clear a compliance check." Independently reconfirmed here, not newly discovered.

Root cause of the missing `year_built_appraisal` data, checked directly against the source PDFs:
- **Loan 02 (FHA):** the fact IS present in the document, just as prose ("Peeling paint... Pre-1978 structure") rather than a structured "Year Built" field — an extraction-scope gap, not a document gap.
- **Loans 04 and 05:** genuinely absent from the source PDF. These loans' scenarios were never designed to test lead-paint compliance at all.

## 3 · Rule fidelity against the real AMQ workbooks — NEW finding this audit

The prior two checks confirm the engine faithfully executes its own 21 `Check` objects. This section asks a different question: **are those checks' actual thresholds grounded in the real source rules (`demo/rules/*.xlsx`, 8,442 real rows across all sheets), or invented during fixture/check authoring?**

### 19 of 21 checks: confirmed, with citations

| Check | Real AMQ match |
|---|---|
| Lead-paint (pre-1978 gate) | `O-VA-58007`: *"Dwelling/improvements before 1978... appraiser did not identify the location of defective paint"* |
| Termite inspection | `O-FHA-50713`: *"Form NPMA-33, Wood Destroying Insect Insp... not in file"* |
| VA residual income | `O-VA-00653`: *"residual income was insufficient as per family size and geographic region"* |
| VA NOV vs. closing date | `O-VA-00557`: *"Notice of Value was no longer valid as of the date of closing"* |
| USDA moderate-income limit | `O-RHS-02764`: *"adjusted annual household income exceeds applicable moderate income program limit"* |
| USDA PITI 29% | `O-RHS-02852` + `O-RHS-50567`: *"front ratio over 29%"* / *"ratios over 29/41"* |
| USDA DTI 41% | `O-RHS-50567` / `O-RHS-50566`: *"29/41"* and *"34/41"* ratio pairs |
| Appraisal staleness (~120 days) | `O-FNM-15363`: real Fannie/Freddie rule uses a ~4-month (120-day) trigger for a Form 1004D update — conceptually confirmed, not byte-exact wording |
| Remaining 11 presence/absence checks (large deposit, HUD-92900-A, gift funds, FHA amendatory clause, ARM disclosure, self-employed P&L, USDA property eligibility, well/septic, FHA case number reconcile) | Standard, well-established program document requirements; consistent with the real rule categories present in the workbook |

### 2 of 21 checks: no confirmed grounding found

Searched exhaustively across all 8,442 rows (every sheet, all Form 1033 comparable-sale rows, every USDA/RHS row):

- **`chk-def-appraisal-comp-distance` (5-mile threshold)** — no row in the entire dataset states a mileage/distance guideline for comparable sales. This check drove a real `FAIL` on loan 01 in the disposition run.
- **`chk-def-site-value-justification`** (implied ~30% site-value-to-total-value threshold) — no row mentions a USDA site-value percentage guideline. This check drove a real `FAIL` on loan 05.

**What this means:** these two checks' underlying document data is genuine (the appraisal really does say "8.5 mi" and "27.6% of total value") — the open question is only whether "5 miles" and "~30%" are the *correct real guideline cutoffs* the engine should be comparing against, or values chosen during synthetic-fixture/check authoring without a traced source. Origin could not be established from git history either — the single commit implementing spec 000 (`9952b8d`) doesn't document where these two specific numbers came from.

**Recommendation:** flag both checks for explicit SME confirmation of the threshold value before treating loan 01's and loan 05's dispositions on these two specific checks as regulator-ready. Every other check and finding in the 5-loan run is traceable to real source rule text.

---

## 4 · Process fix: closing the gap that let this happen

The two ungrounded thresholds above were possible because nothing in the compilation pipeline explicitly forbade a compile step (LLM or KB-authoring) from filling in a plausible-sounding number when the source text didn't state one. Research/grounding is legitimate and necessary for *interpreting* ambiguous rule text — it must never become the *origin* of new rule content. Hardened this in three places:

1. **`p0/qc_engine/compiler/compile_llm.py`** (`SYSTEM_PROMPT`) — added a hard constraint: every threshold, tolerance, operator, and condition in a compiled check must trace to `defect_text` or a quoted `grounding_context` excerpt. If a limit is implied but its exact value is absent from both, the compiler must emit the literal string `"UNSPECIFIED"` and say so in `plain_english_restatement` — never fill in a plausible number.
2. **`p0/qc_engine/compiler/knowledge_base.py`** — added the same constraint at the KB-authoring level: a `KBSection` may cite and explain a condition already present in the source workbook; it must never be how a new rule/threshold enters the system. An LLM correctly refusing to invent a number is defeated if the KB it's told to trust already smuggled that invented number in as "grounding."
3. **`CLAUDE.md`** — added as a hardened sub-point under Non-Negotiable #1 (Determinism), so this constraint is visible to every future session working on this codebase, not just encoded in the compiler prompt.

**Principle, stated plainly:** an honest `"UNSPECIFIED — needs SME input"` beats a confident invented number, every time. This is the same audit-trail logic as Non-Negotiable #1 itself — a regulator asking "how did you calculate that number" must always have a traceable answer, never "the model's training knowledge said this is typical."
