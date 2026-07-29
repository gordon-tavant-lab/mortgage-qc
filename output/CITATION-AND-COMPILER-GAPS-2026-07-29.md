# Compiler & Citation Gaps — Flagged Follow-Up (2026-07-29)

| | |
|---|---|
| **Trigger** | A frontend redesign session for the Route/Block/Check authoring surface (Kayla-review mockup) surfaced five real backend/compiler findings while verifying what the UI should actually represent. Each was confirmed by reading the real code and/or querying a real compiled ruleset — none is speculative. |
| **Scope decision** | This session's build work stayed scoped to the frontend mockup (Option A). These five findings are **not fixed** — they are documented here for the real dev team to act on. The mockup demonstrates each gap explicitly (via `PlaceholderBadge`/`FlaskConical` treatment) rather than hiding it. |
| **Status** | All 5 findings below are open. None has a tracking spec yet. |

---

## 1. Question-code grouping data is read, then discarded, at compile time

**What's confirmed:** `p0/eval_synth/taxonomy.py`'s `load_rows()` (line 226) already extracts the AMQ workbook's **Question Code** column per row into a `qcode` field. `p0/qc_engine/compiler/compile_llm.py` (line 386) already reads that value — but only to build the LLM prompt's `question_text` input. It is never written onto the resulting `Check` object. `ruleset.py`'s `Check` dataclass has no `question_code` field at all.

**Why it matters:** Real AMQ rows share Question Codes in groups (confirmed directly against the raw workbook: the question "Have all sections of the Final 1003 been completed and accurate?" has **9 separate rows** under one Question Code, each its own answer/exception/severity). Without this field surviving compilation, the frontend has no reliable way to cluster sibling checks under their shared question — it would have to reconstruct this via fragile name-matching heuristics instead of reading real data.

**Fix (small, additive, zero risk):** add `question_code: Optional[str] = None` to `Check` (`ruleset.py`), and set it from `row.get("qcode")` in `compile_row()` (`compile_llm.py`) alongside the existing `field_name`/`kind` assignment. No extraction-unit change — the compiler already reads this value per row; it's a one-line addition to what gets persisted.

**Frontend demonstration:** `src/data/mockData.ts`'s `chk-urla-final-1..4` (4 of the real 9 "Final URLA" siblings), grouped in `BlockDetail.tsx`'s Available Checks pool via the new `questionCode`/`questionText` fields — expanded by default, not collapsed (see §6 for why).

---

## 2. Doc-vs-doc miscompile: 35 suspects, 2 fixed, 33 unaudited

**What's confirmed:** `p0/qc_engine/compiler/known_compile_corrections.py` is a **hardcoded 2-item allowlist** (keyed by exact check ID: `employment-dates-1003-vs-docs-agree`, `title-vesting-1003-vs-commitment`), not a general detector. It was written on 2026-07-28 after both checks were found miscompiled as `agree_categorical` (doc-vs-**system**) when they should be `agree_doc_categorical` (doc-vs-**doc**) — comparing against `sv.system_value()`, which is `None` for a field with no system source, silently producing a wrong verdict.

The same finding flagged "zero checks in the entire 3,203-check v8 ruleset use `agree_doc_categorical`... worth a dedicated audit" as an **unresolved follow-up**. That audit was never done.

**We ran it.** Cross-referencing `field_catalog.json`'s `expected_sources` against the real 8,399-check `run_008_comprehensive_8442/ruleset.json`: any check compiled as `agree_categorical` whose field has `expected_sources: ["doc"]` (no `los`/`mismo`) is **structurally impossible** to be a real doc-vs-system comparison. Result: **35 suspects**, not 2. Sample:

```
cash-to-borrower-cd-vs-approval-consistent | cash_to_borrower_cd
gla-sqft-consistency                        | gla_sqft
1008-appraiser-name-license-agree           | appraiser_name
1008-loan-purpose-agree                     | loan_purpose_1003
urla-marital-status-agree                   | marital_status_1003
loan-purpose-1003-vs-1008-du-agree          | loan_purpose_1003
... (29 more)
```

**Fix (real, not a patch):** the hardcoded allowlist doesn't scale and won't catch new instances on the next compile run. The real fix is upstream in the compiler's kind-selection logic: when a candidate check's field has no system source in the catalog, either (a) auto-resolve to `agree_doc_categorical` with a compiler-proposed `compare_field_name` for SME confirmation, or (b) flag `NEEDS_REVIEW` rather than silently defaulting to `agree_categorical`. Re-run the 35-suspect detection query as a **standing gate** (same tier as the existing 25/25 defect gate) on every recompile, not a one-time find.

**Frontend demonstration:** `chk-employment-dates-1003-vs-voe` in `src/data/mockData.ts` — shown in its intended-correct `agree_doc_categorical` shape (two field selectors, Field A + Field B) in `BlockDetail.tsx`'s kind-aware Edit Check form, with an inline warning banner noting the near-zero real usage.

---

## 3. `GroundingRecord` is computed at compile time, then discarded before signing

**What's confirmed:** `compile_llm.py` defines `GroundingRecord{kb_program, kb_version, section_ids}` (line 277) — a real, populated link from a compiled check back to the specific Selling Guide section(s) that informed its interpretation (built from real `KB.retrieve()` results, lines 374–391). But `assemble_ruleset()` (lines 618–657) never reads `d.grounding` when building the final signed `Ruleset` — only `check`, `source_text`, and `extracted_intent` survive. The citation is real and correctly computed, then silently dropped before it reaches the artifact anyone can audit.

**Why it matters:** an internal architecture doc (`output/scratch/architecture-doc.html:310`, duplicated in `architecture-doc-v2.html:310`) states the compiler "attaches Guide citations" as part of its audit trail. That claim is only half true — the citation is attached in memory during compilation and vanishes before the signed artifact is produced. This undercuts a stated differentiator of the product (traceable, non-invented thresholds — the "grounding adds context, never new rule content" principle from `RULE-FIDELITY-AUDIT-2026-07-22.md`).

**Fix (low-risk — restore, don't build):** persist `GroundingRecord` (or an equivalent citation list) onto the signed `Ruleset`/`Check` in `assemble_ruleset()`. The data already exists at the point it's discarded; this is a wiring fix, not new retrieval logic.

**Frontend demonstration:** `chk-gift-funds-source` in `src/data/mockData.ts` carries a `grounding: [{ source: "Fannie Mae Selling Guide", sectionId: "B3-4.3-04", ... }]` field, rendered via the shared `SourceCitation` component in both `BlockDetail.tsx`'s Edit Check panel and `ImportAndSignView.tsx`'s diff-and-sign review — shown as it **should** look once this fix lands.

---

## 4. No row/sheet/cell locator ever exists for the raw AMQ source

**What's confirmed:** `taxonomy.py`'s `load_rows()` reads the workbook via `openpyxl.iter_rows(values_only=True)`, which discards each row's own index and sheet name entirely — the returned dict carries only `category, qcode, defect_text, sql_criteria, exception_code, significance`. `p0/qc_engine/compiler/sample.py` later synthesizes a `row_id` (e.g. `"predicate-014"`), but this is a **synthetic index**, not a pointer back into the real `.xlsx` file. `RuleIntentRecord` (`ruleset.py:122-136`) keeps only `check_id, source_text, extracted_intent` — the raw row text is embedded as a string with zero locator, and even the transient synthetic `row_id`/`source_file` don't survive to this permanent record.

**Why it matters:** even after fixing #3 above, a check with no grounding (most of them — grounding only applies where the compiler actually retrieved a relevant Guide section) would have **no way to show an SME which row of which sheet it came from**. That's a real gap in the audit trail's completeness, separate from the grounding-citation gap.

**Fix:** capture `openpyxl`'s row index and the active sheet name in `load_rows()`, and thread it through to a persisted field on `Check` (e.g. `source_locator: {workbook, sheet, row}`).

**Frontend demonstration:** most checks in `src/data/mockData.ts` carry a `sourceLocator` field (e.g. `{ workbook: "PF and PC Sept 2025 AMQs - Retail.xlsx", sheet: "Post-Closing", row: 1142 }`) as the fallback citation when no grounding applies — rendered by the same `SourceCitation` component.

---

## 5. `citation_required` exists on 380/385 catalog fields; nothing enforces it

**What's confirmed:** `p0/qc_engine/catalog.py:43` defines `citation_required: bool = False` on `FieldCatalogEntry`. Of the 385 real entries in `field_catalog.json`, **380 have `citation_required: true`**. Grepping every non-test `.py` file under `p0/` for `citation_required` finds only the dataclass definition, its `to_dict()` serialization, and one mention in the compiler's LLM prompt text (informational only, not enforced). `engine.py` never reads this flag — there is no code path that blocks a PASS/auto-clear when a citation-required field's resolved `citation` is `None`.

**Why it matters:** this is a real, confirmed violation of this project's own stated Audit gate principle (`.specify/memory/constitution.md`'s Quality Gates section: *"every doc-sourced value is traceable... not an opaque trace"*). It sits right next to the confidence gate that **does** exist (spec `006-confidence-gated-auto-clear`, shipped — a sub-floor-confidence PASS is correctly withheld to `NEEDS_REVIEW`) — the same pattern was never built for the missing-citation case.

**Fix:** add a citation gate to `engine.py`'s post-dispatch logic (same shape as spec 006's confidence gate): when `field_catalog[field_name].citation_required` is true and the resolved `CheckResult.citation` is `None` on a would-be PASS, downgrade to `NEEDS_REVIEW` with `review_reason = "MISSING_CITATION"`, never silently auto-clear.

**Frontend demonstration:** `MOCK_EVALUATION`'s audit trace in `src/data/mockData.ts` includes `chk-borrower-cert-auth-release-present` — a real `PASS` with `citationRequired: true` on its field and **no citation**, shown exactly as the system behaves today (not as it should). `ApplyView.tsx` renders this as a distinct "Missing required citation" flag in the Source Citation column, not a silent dash.

---

## 6. Adjacent design finding: question-grouping must not collapse by default

Not a backend gap, but worth recording alongside these so the rationale isn't lost: an earlier draft of the frontend grouping feature defaulted grouped sibling checks to a collapsed accordion. A contrarian pass against that design found two real problems, both now reflected in `BlockDetail.tsx`'s `QuestionGroup` component:

- **False mutual-exclusivity.** The engine runs every active check independently, every time — there is no "pick one answer" resolution step. A collapsed group implying "9 possible outcomes, pick one" misrepresents actual runtime semantics.
- **Sign-off-theater risk.** If "activate this group" becomes a single click that activates all N sibling checks at once, that's structurally the same red flag Principle II already warns about for zero-edit bulk sign-offs — just moved one level down, from rulesets to check-groups.

Resolution: sibling checks are visually clustered under their shared question text but **expanded by default**, every check individually visible and individually activatable — no click-to-reveal, no implied bulk-approve gesture.

---

## Summary table

| # | Gap | Type | Fix size | Status |
|---|---|---|---|---|
| 1 | `question_code` computed, not persisted | Compiler (small addition) | Small | Open |
| 2 | Doc-vs-doc miscompile, 35 suspects | Compiler (logic fix) | Medium | 2/35 patched, 33 open |
| 3 | `GroundingRecord` computed, discarded | Compiler (wiring bug) | Small | Open |
| 4 | No AMQ row/sheet locator ever captured | Compiler (small addition) | Small | Open |
| 5 | `citation_required` never enforced | Engine (new gate, same shape as spec 006) | Small–Medium | Open |

None of these blocks the current frontend mockup — all five are demonstrated in it deliberately, so reviewers see the real state of the system rather than a UI that quietly implies these problems don't exist.
