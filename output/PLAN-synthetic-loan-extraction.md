# Plan: Convert `demo/syn` loan files into field-extracted fixtures

| | |
|---|---|
| **Date** | 2026-07-14 |
| **Trigger** | Convert the 5 synthetic loans in `demo/syn/loan 0{1-5}/` into the "post-extraction" field format the QC engine consumes, generated once (dev-mode), not at runtime. Must be accurate — downstream trust depends on it. |
| **Scope** | Planning only. No code written yet. |

---

## 0. The tension this plan has to resolve first

CLAUDE.md Non-Negotiable #2 says: **"Document data extraction ❌ Do not build. Upstream contract with Touchless."** A literal reading would block this whole task.

The resolution: what's needed here is **not** the Touchless extractor. It's a **throwaway, dev-only fixture generator** — a one-time script that turns 5 already-known synthetic loans into `CanonicalLoan` JSON, so the engine has *document-derived* test fixtures instead of only hand-authored ones (today's `p0/fixtures/golden.py` and `p0/eval_synth/generator.py` — both 100% hand-typed Python, confirmed by reading them; **nothing in this codebase has ever parsed a real document**). This is the same category of thing as `p0/eval_synth` itself — eval infrastructure, not the product. It does not compete with or preempt Touchless; it unblocks testing while Touchless doesn't exist yet. Frame it that way in any commit/doc, per Principle IV.

---

## 1. What "field extracted files format" already means here (nothing new to design)

The target shape is **already pinned**, not something to invent:

- **Runtime shape**: `p0/qc_engine/model.py` — `CanonicalLoan{loan_id, loan_type, fields: Dict[str, SourceValue], facts}`, where `SourceValue{truth, sources: {los, mismo, ...}, citation: DocCitation{doc_name, page_num, segment_snippet}, doc_confidence}`.
- **Wire/inbound shape**: `specs/001b-source-envelope-and-inbound-contracts/contracts/inbound-contracts.md` — the Touchless inbound contract is exactly:
  ```json
  {"field_name": "note_rate", "value": "6.125", "document_classification": "Promissory_Note",
   "citation": {"doc_name": "...", "page_num": 3, "segment_snippet": "..."}, "confidence": 0.97}
  ```
  and the LOS/MISMO inbound contract is `{"field_name": ..., "value": ..., "source_name": "los|mismo"}`.

**Decision: output must conform to this contract exactly** (field-name-keyed JSON that a small adapter turns into `CanonicalLoan`/`SourceValue`), not a new ad hoc schema. This makes the fixture generator double as a first real-world exercise of the contract itself.

---

## 2. Field scope — the fork that needs your call

`p0/qc_engine/field_catalog.json` today has **7 fields** (borrower_name, borrower_ssn, note_rate, loan_amount, property_address, flood_zone, note_signed) — a P0 seed catalog, not the full 800-check vocabulary.

I checked what the 5 synthetic loans actually test. **Every MISMO XML has 5 `<!-- DEFECT -->` comments (25 total) — a complete, mechanically-checkable answer key already built into the fixtures**, e.g.:

- Loan 01: employment start date mismatch (1003 vs VOE/paystub), title vesting mismatch (1003 vs title commitment), unsourced $15K deposit, undisclosed $412/mo liability, appraisal comp 8.5mi over guideline.
- Loan 02 (FHA): FHA case number mismatch, unsigned HUD cert, missing gift-fund paper trail, missing lead-paint cert, missing amendatory clause.
- Loan 03 (VA): NOV dated after closing, missing ARM disclosure/termite/lead-paint, undocumented residual income.
- Loan 04 (Freddie cash-out refi): loan purpose mismatch, payoff amount mismatch, mortgage-history delinquency, stale appraisal, missing YTD P&L.
- Loan 05 (USDA): income-limit breach, missing property-eligibility screen-print, DTI ratio breach, missing well/septic docs, site-value % over guideline.

**None of these 25 defects are covered by the current 7-field catalog.** They map mostly to `003c-engine-reconcile-checks` (doc-vs-system mismatches) and document-presence predicates — both real roadmap features, **003c isn't spec'd yet** (only 001a/001b/002a/002b/003a/003b exist).

**Decision (Gordon, 2026-07-14): extend the catalog, be thorough, and don't guess the field list from the 5 loans alone — diff it against what the real rules actually check for**, using `p0/eval_synth/taxonomy.json` (already-classified vocabulary from the real 7,398-condition AMQ workbook, not invented) as the ground truth for "what do rules look for." Every proposed field below is tied to a specific taxonomy archetype/category — several by **exact-text match** to a real rule example, not analogy.

### 2.1 Rule-grounded field catalog extension (proposed)

| Field | Archetype (taxonomy.json) | Real-rule evidence | Loan(s) it unblocks | `expected_sources` |
|---|---|---|---|---|
| `employment_start_date` (+ supporting-doc value) | MISMATCH | *"The employment dates listed on the 1003 do not match other employment documentation in the file"* — exact text match | 01 | doc, doc (see §2.2) |
| `title_vesting` | MISMATCH | *"The manner in which title is held on the 1003 does not match the title commitment"* — exact text match | 01 | doc, doc |
| `large_deposit_source_documented` | POLICY / MISSING | *"Large deposit not from the borr's income, acceptable funds awarded to the borr, or eligible asset"* — exact text match (unclassified list, but literal) | 01 | doc |
| `liability_disclosed_on_1003` | MISMATCH | Same family as loan-purpose/title-vesting MISMATCH rows (Credit - Liabilities category, 109 THRESHOLD + part of 139 MISMATCH conditions) | 01 | doc, doc |
| `appraisal_comp_max_distance_miles` | THRESHOLD | Property - Appraisal category (58 THRESHOLD conditions); Form 1004/1033 comp-selection rules | 01 | doc |
| `fha_case_number` | MISMATCH | 1003 vs. FHA Connection (FHAC) — this one **is** genuinely doc-vs-system (FHAC is an external HUD system, not a closing doc) | 02 | doc, sources.fhac |
| `hud_certification_signed` | UNSIGNED | Loan Documents/Certification category (106 UNSIGNED conditions) | 02 | doc |
| `gift_funds_documentation_complete` | MISSING | Assets category (176 of 1,807 MISSING conditions) | 02 | doc |
| `lead_paint_cert_present` / `property_year_built` | MISSING | Property - Appraisal category (274 of 1,807 MISSING) | 02, 03 | doc |
| `fha_amendatory_clause_present` | MISSING | Loan Documents category | 02 | doc |
| `nov_issue_date` / `closing_date` | EXPIRED (date-order variant) | Income/date-validity-window category | 03 | doc, doc |
| `arm_preloan_disclosure_present` | MISSING | **Exact text match**: *"No, the ARM pre-loan disclosure is missing or was not provided timely"* | 03 | doc |
| `termite_inspection_present` | MISSING | Property - Appraisal category | 03 | doc |
| `va_residual_income_documented` | POLICY / MISSING | Underwriting category | 03 | doc |
| `loan_purpose` | MISMATCH | **Near-exact match**: *"The loan purpose selected on the final 1003 does not match the final 1008 and/or final DU"* | 04 | doc, doc |
| `existing_loan_payoff_amount` | MISMATCH / THRESHOLD | Underwriting/reconciliation category | 04 | doc (payoff stmt), doc (CD) |
| `mortgage_late_payment_count_12mo` | THRESHOLD / POLICY | Credit - Liabilities category (109 THRESHOLD) | 04 | doc |
| `appraisal_effective_date` | EXPIRED | **Direct fit** — "stale, aged, out of validity window" is EXPIRED's literal definition; Property-Appraisal is EXPIRED's top-5 category | 04 | doc |
| `self_employed_ytd_pl_present` / `self_employed_balance_sheet_present` | MISSING | Income category (345 of 1,807 MISSING — the single largest MISSING bucket) | 04 | doc |
| `household_income` / `usda_income_limit_moderate` | THRESHOLD | Income category (98 of 853 THRESHOLD) | 05 | doc, doc (program limit table) |
| `usda_property_eligibility_screenshot_present` | MISSING | Property - Appraisal category | 05 | doc |
| `piti_ratio` / `total_dti_ratio` | THRESHOLD | Underwriting category (156 of 853 THRESHOLD — 2nd largest bucket) | 05 | doc |
| `usda_ratio_waiver_documented` | POLICY | Underwriting category | 05 | doc |
| `well_water_test_present` / `septic_evaluation_present` | MISSING | Property - Appraisal category | 05 | doc |
| `site_value_pct_of_appraised` / `site_value_analysis_documented` | THRESHOLD + POLICY | Property - Appraisal category | 05 | doc |

That's ~26 new fields (some paired), each traceable to a real rule condition — not a guess from "what's convenient in these 5 files." Combined with the existing 7, this covers all 25 built-in defects with room to spare (several fields, e.g. `appraisal_effective_date` and `self_employed_ytd_pl_present`, generalize beyond the specific loan that surfaced them).

### 2.2 A real architecture gap this surfaced — needs your call before catalog work starts

Several rows above (`employment_start_date`, `title_vesting`, `liability_disclosed_on_1003`, `loan_purpose`, `existing_loan_payoff_amount`) are **doc-vs-doc** mismatches (e.g., the 1003 vs. the VOE, or the 1003 vs. the title commitment) — **not doc-vs-system**. But `SourceValue` (`model.py`) and 001b's source-independence guard are built for exactly one shape: `truth` (document side, singular) vs. `sources{los, mismo, ...}` (system side). There's no first-class way today to say "these two *document-side* values must agree with each other," and FR-005's guard would (correctly) reject a fixture that tried to fake this by putting one doc value in `sources`.

Real rules clearly need this — the MISMATCH archetype's own top real-rule examples are mostly doc-internal cross-checks (1003 vs. VOE, 1003 vs. title, 1003 vs. 1008/DU), and this is presumably most of `003c`'s eventual real scope, not an edge case.

**Recommended default (flagging, not silently deciding): model each side as its own catalog field with its own `truth`+`citation`** (e.g. `employment_start_date_1003` and `employment_start_date_supporting_docs` as two separate fields), and let a **new, distinct check kind** (`agree_doc_internal` or similar — explicitly NOT reusing `agree_categorical`'s source-independence-guarded path) compare truth-to-truth. This keeps 001b's guard meaningful (it still only ever fires on true doc-vs-system comparisons) while giving doc-vs-doc consistency its own honest lane. This is a call for whoever specs `003c` — flagging here so the field-catalog extension doesn't quietly bake in an assumption that feature hasn't made yet.

### 2.3 Citation-link design (per your ask — "build in citation links to the original source")

Every extracted field must carry enough to answer "where did this come from, exactly" — already the model's `DocCitation{doc_name, page_num, segment_snippet}`, but today it's a single citation hanging off `truth`. Two refinements needed for this batch:

1. **Every doc-sourced value (both `truth` and any doc-internal "second side" field per §2.2) gets its own citation** — not just the primary `truth` slot. In practice: each of the ~26 new fields resolves to its own catalog entry with `citation_required: true`, so a doc-vs-doc pair is two catalog entries, each independently cited — no schema change needed, this falls out of §2.2's design for free.
2. **System-side values** (`fha_case_number`'s `sources.fhac`) don't get a `DocCitation` (there's no PDF page to cite) — instead they should carry a lightweight provenance string (source system name + record identifier, e.g. `"FHA Connection, case lookup 2026-07-22"`), which `SourceValue` doesn't currently have a slot for either. Minor, additive schema note for whoever builds this — not a blocker.

Every one of the 25 DEFECT-comment answer-key entries can now be traced to a specific citation-bearing field pair, which is what makes the accuracy gate (§3, step 4) actually mean something: it's not just "the right value came out," it's "the right value came out **and** we can point at the exact page it came from."

---

## 3. Extraction mechanism — audited `examples/mortgage-qc`, verdict: reuse the idea, not the code

Dispatched a full audit of Olav's live extraction pipeline (`examples/mortgage-qc/agent-gateway/src/{extraction_handler,pdf_processor,xml_extractor,cross_validator}.py` + its issue log). Findings:

- **XML parsing is already deterministic and reusable as-is** — `p0/qc_engine/mismo.py` already does this for our MISMO files; no need to touch Olav's `xml_extractor.py`.
- **PDF extraction is Claude Vision/Sonnet at `temperature=0.0`**, not Textract (Textract was only ever a "future fast path" in the design doc, never built). Temp=0 reduces but doesn't guarantee bit-identical output, and the pipeline's **own issue log documents live inaccuracy**: issue 006 (LoanEstimate fields return `null`/confidence-0.0 for present data, unfixed), issue 010 (a mock fixture silently disagreeing with the real PDF — exactly the "fake mismatch" failure THESIS.md already cites as corroborating evidence for source independence), issue 014 (citations pointed at the wrong page until fixed 2026-06-11).
- **Confidence scores are frequently a hardcoded fallback** (`0.8` / `0.5` defaults), not a calibrated signal — unusable as-is for `006-confidence-gated-auto-clear`'s eventual gate.
- **Document-type coverage is narrower than what these 5 loans need**: 12 schemas exist (w2, paystub, bank statement, closing disclosure, credit report, appraisal, loan estimate, title, 1003, VOE, note, insurance) — **no VA Notice of Value, no VA Certificate of Eligibility, no USDA docs, no FHA-specific docs, no gift letter schema** (despite being listed as classifiable).
- **Not runnable in isolation** — only exposed via a FastAPI endpoint requiring live AWS Bedrock, S3 (no local-storage fallback despite doc claims), Redis, and mock LOS/DocVault services. No standalone CLI exists.

**Verdict: do not point this pipeline at `demo/syn`.** It would import a real non-determinism/accuracy risk into the one artifact that has to be more trustworthy than the thing it's meant to validate, and it can't run without infra this project doesn't want to stand up for a one-time job.

**What to build instead**, in order of preference (all deterministic, all offline):

1. **MISMO XML → reuse `p0/qc_engine/mismo.py` directly.** Already handles our exact file shape; extend its field list to match whatever field catalog (§2) lands on.
2. **PDFs → deterministic text extraction + per-document-type field patterns.** Every PDF in `demo/syn` is a born-digital synthetic document with a clean, regular "Label — spaces — Value" layout (confirmed by reading all 38 files with `pdftotext -layout` — zero OCR noise, no scanned images). A small `pdftotext -layout` + label-anchored regex per document type (one spec per doc type, similar in spirit to Olav's `schemas/extraction/*.yaml` but standalone, no runtime deps) will extract every field **byte-deterministically** — same input, same output, forever. This is strictly easier than what Olav's pipeline solves (his has to handle scanned/real lender PDFs; ours only has to handle its own synthetic generator's fixed layout).
3. **LLM assist, only if #2 can't confidently resolve a field** — a single offline (dev-mode) Sonnet call at `temperature=0`, required to emit `{value, citation, confidence}` in the exact contract shape, used as a fallback with the extraction still gated on step 4.
4. **Mandatory accuracy gate before any output is trusted** (this is the "must be accurate" bar, made mechanical): for every one of the 25 `<!-- DEFECT -->` comments, assert the extracted `truth` and `sources.mismo` values reproduce the documented discrepancy exactly (e.g., loan 01's liability defect: extracted truth must show the Ally Bank $412/mo liability present on the credit report doc-side and absent from the 1003/MISMO system-side, with the amounts matching to the cent). **25/25 exact matches, zero tolerance** — this is the same "false-auto-clears = 0" discipline `g-learn-ground-truth-by-construction` already established for the engine, applied one layer earlier, to extraction itself.

---

## 4. Where this lives / how it's built

- **Decision (2026-07-14): lightweight script, not a formal spec-kit feature** — mirrors `p0/eval_synth`'s existing convention (hand-built, documented, tested Python module, no formal spec cycle) rather than the 001a/001b/003a/003b governed-feature pattern. `p0/fixtures/from_docs/` — `extract_pdf.py` (per-doc-type patterns), `extract_xml.py` (thin wrapper over `qc_engine/mismo.py`), `build_fixtures.py` (assembles `CanonicalLoan` JSON per loan), `verify_against_defects.py` (the 25/25 gate), plus a README stating explicitly: *dev-only, throwaway, not the Touchless extractor, not a claim about real-document extraction accuracy* (per `g-learn-ground-truth-by-construction` Step 6 and `g-learn-synthetic-ulad-loan`'s self-documentation convention).
  - **Caveat**: the field_catalog.json extension itself (§2.1) still touches a governed artifact (001a's zero-regression gate). Since the script is lightweight, keep the catalog change small and reviewable — a plain JSON diff plus a rerun of 001a's existing referential-integrity/zero-regression tests — rather than skipping that gate. "Lightweight build process" applies to the *extraction script*, not license to bypass 001a's own gate on its own artifact.
  - **§2.2's doc-internal check-kind question is out of scope for this script** — the extractor just needs to produce two independently-cited fields per doc-vs-doc pair; deciding the actual comparison mechanism (`agree_doc_internal` or otherwise) is `003c`'s call when it's spec'd, not something this fixture-generation work should preempt.
- **Output** lands as JSON fixtures (one per loan) that a thin adapter loads into `CanonicalLoan`/`SourceValue` — pluggable into `p0/eval_synth`'s scorer and any future 003c reconcile-check tests with zero rework, per the "same `score()`, swap the source" principle.

---

## 5. Phased plan

| Phase | What | Gate before proceeding |
|---|---|---|
| **1. Scope lock** | Decide §2 (7 fields vs. extend catalog) and §4 (throwaway script vs. formal spec) | Your sign-off — these are the two forks in this plan |
| **2. XML adapter** | Extend `mismo.py` (or a thin wrapper) to emit every in-scope field for all 5 MISMO files | Field-for-field diff against what I already hand-read from each XML in this session |
| **3. PDF adapter** | Per-document-type `pdftotext`+regex extractors for the ~10 doc types across the 38 PDFs | Same — diff against hand-read values |
| **4. Fixture assembly** | Merge doc-side (`truth`) + MISMO-side (`sources.mismo`) into 5 `CanonicalLoan` JSON files, contract-shaped per §1 | Schema validates against `field-catalog-schema.md` / `inbound-contracts.md` |
| **5. Accuracy gate** | Automated check: all 25 DEFECT comments reproduce as expected mismatches; zero silent nulls (issue-006-style failure) | **25/25 exact — hard stop if not** |
| **6. Wire to downstream** | Point `p0/eval_synth`/engine tests at the new fixtures alongside (not replacing) the hand-authored golden set | Zero regression on existing golden-set verdicts |

---

## 6. What this does *not* claim

Per `g-learn-ground-truth-by-construction` Step 6 — label the residual loudly: this proves the extraction *mechanism* is accurate against **known, constructed** documents. It does **not** prove accuracy against real lenders' scanned/messy PDFs, real OCR noise, or real Touchless output — that remains Blocker 1/2 territory, gated on Kayla's real loans, same as everywhere else in this project.
