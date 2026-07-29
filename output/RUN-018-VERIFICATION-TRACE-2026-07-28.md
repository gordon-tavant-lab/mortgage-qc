# run_018 — Manual Re-Run Trace & Determinism Verification

**Date:** 2026-07-28 · **Purpose:** Gordon asked for a second, independent run of the guideline-parse → compile → QC pipeline (separate from the file he's showing in tonight's meeting), with every file read, every script executed, and every output written documented step by step — so the process is fully traceable.

**Headline result: the second run produced byte-for-byte identical output to the original.** Same SHA-256 hash on both the QC result and the compiled ruleset. This is the strongest possible evidence for this project's Non-Negotiable #1 (determinism) — not just asserted, empirically reproduced on demand.

---

## What was run

A verification copy of the production script, `p0/compile_runs/run_018_guideline_to_loan01_e2e/build_and_run.py`, was made in the same directory (so its internal relative-path logic — which locates `p0/` and the repo root from its own file location — still resolved correctly), with four output paths redirected so **nothing belonging to tonight's demo file (`loan_01_v8.json`) was touched**:

| Constant | Original (tonight's demo) | This verification run |
|---|---|---|
| `RUN_ID` | `run_018_guideline_to_loan01_e2e` | `run_018_guideline_to_loan01_e2e_verify2` |
| `NEW_RULESET_OUT` | `result/rules/comprehensive_e2e_v8_ruleset.json` | `result/rules/comprehensive_e2e_v8_ruleset-2.json` |
| `RESULTS_OUT` | `result/qc_results/run_018_guideline_to_loan01_e2e_results.json` | `result/qc_results/run_018_guideline_to_loan01_e2e_verify2_results.json` |
| `LOAN01_QC_OUT` | `result/qc_results/loan_01_v8.json` | **`result/qc_results/loan_01_v8-2.json`** |

Command actually run (from the repo root):
```bash
python3 p0/compile_runs/run_018_guideline_to_loan01_e2e/build_and_run_verify2.py
```

The verification copy was deleted immediately after the run completed — it was scaffolding to prove reproducibility, not a permanent addition to the codebase. Only the four output artifacts below (plus this document) are new.

---

## Stage-by-stage trace

### Stage 1 — Parse Guideline (zero LLM)

| | |
|---|---|
| **Script** | `qc_engine/compiler/ingest_selling_guide.py` (`parse_selling_guide()`), called from `stage1_parse_guideline()` in `build_and_run.py` |
| **Input read** | `docs/Selling-Guide_06-03-2026_highlighted.pdf` — the real Fannie Mae Selling Guide |
| **How** | `pdftotext` (poppler-utils) extracts text, deterministically sliced into citable sections |
| **Output** | `storage/knowledge_base/kb.sqlite3` — 416 sections parsed, signed `NOT-A-REAL-SME-pending-kayla-review` (unsigned, pending human review — by design, per this project's grounding discipline) |
| **This run's result** | **416 sections parsed** — identical to the original run |

### Stage 2 — Compile Ruleset (zero fresh LLM calls)

| | |
|---|---|
| **Script** | `stage2_compile_ruleset()` in `build_and_run.py`, using `qc_engine/compiler/{compile_llm, fact_vocabulary, known_compile_corrections}.py` and `ontology_extraction/pipeline.py` |
| **Inputs read** | `p0/compile_runs/run_010_post_closing_only/ruleset.json` (4,506 already-LLM-compiled checks — real Bedrock calls made in a **prior session**, not repeated here) · `.../run_010_post_closing_only/provenance_checkpoint.json` (source-row mapping, for retail-only filtering) · `p0/fixtures/ontology_extraction/retail_post_closing_rows.json` (raw AMQ rows, for precondition derivation) · `storage/fact_vocabulary/v8.json` (signed fact vocabulary — latest as of this run) |
| **Deterministic wiring applied, in order** | 1) **retail-only rebasis** — keep only checks sourced purely from the retail AMQ workbook; 2) **002d operator-consistency gate** — exclude checks with an inverted comparison operator; 3) **002g precondition attachment** — resolve each check's gating condition against the vocabulary; 4) **known compile corrections** (`known_compile_corrections.py`) — fixes 2 checks previously miscompiled as doc-vs-system instead of doc-vs-doc comparisons |
| **Output** | `result/rules/comprehensive_e2e_v8_ruleset-2.json` |
| **This run's result** | 4,506 loaded → 3,330 kept (retail-only) → 127 excluded (operator gate) → 1,701 preconditions attached, 349 flagged, 1,153 unconditional → 2 known corrections applied (`employment-dates-1003-vs-docs-agree`, `title-vesting-1003-vs-commitment`) — **identical counts to the original run**, and **identical SHA-256**: `3ed4fc92...509bf81` |

### Stage 3 — QC Loan 01 (zero LLM calls)

| | |
|---|---|
| **Script** | `stage3_qc_loan01()` in `build_and_run.py`, calling `qc_engine/engine.py`'s `run()` |
| **Inputs read** | `p0/fixtures/from_docs/loan_01.json` (loan 01's real extracted fields — doc/LOS/MISMO source values) · `storage/loan_profiles/v3/loan_01.json` (derived facts layered on top, e.g. `loan_program`, `occupancy_type`) · `result/rules/post_closing_only_applicability.json` (program-tag lookup, for the Fannie-Mae-scoped view) |
| **Output** | `result/qc_results/loan_01_v8-2.json` |
| **This run's result — unscoped (all programs mixed)** | `NOT_APPLICABLE=728, NEEDS_REVIEW=2375, FAIL=87, PASS=13` → disposition **NEEDS_REVIEW** |
| **This run's result — scoped (Fannie Mae + untagged only, 1,076 of 3,203 checks)** | `NOT_APPLICABLE=290, NEEDS_REVIEW=762, FAIL=20, PASS=4` |
| Every count above is **identical** to the original run | |

### Run summary written

`result/qc_results/run_018_guideline_to_loan01_e2e_verify2_results.json` — the same manifest shape as tonight's `run_018_guideline_to_loan01_e2e_results.json`, confirming `cost: {llm_calls: 0, cost_usd: 0.0}`.

### Evidence-chain log

`storage/logs/run_018_guideline_to_loan01_e2e_verify2.jsonl` — one JSON line per event across all three stages (guideline parse → ruleset compile → known-correction application → precondition attachment → program-gate classification → per-check QC verdict). This is the full input → method → verdict trail an auditor would walk, generated fresh by this run, independent of tonight's original log.

---

## Determinism check (the actual proof)

```
$ diff result/qc_results/loan_01_v8.json result/qc_results/loan_01_v8-2.json
(no output — files are identical)

$ shasum -a 256 result/qc_results/loan_01_v8.json result/qc_results/loan_01_v8-2.json
34c71144e97c43cfe68dddf13d54a92ff0301547a3c02f5b4336a33532d60087  loan_01_v8.json
34c71144e97c43cfe68dddf13d54a92ff0301547a3c02f5b4336a33532d60087  loan_01_v8-2.json

$ # compiled ruleset SHA-256, both runs
original: 3ed4fc921877750cd5ec02551c3a38b1bf1cb664ba4367f1e7ddce857509bf81
verify2:  3ed4fc921877750cd5ec02551c3a38b1bf1cb664ba4367f1e7ddce857509bf81
match: True
```

Same loan, same source ruleset inputs, run independently a second time → **byte-identical QC result and byte-identical compiled ruleset.** This is exactly the claim in `CLAUDE.md`'s Non-Negotiable #1 ("Same loan → same pass/fail, every time") demonstrated directly, not just documented.

---

## Files produced by this exercise

| Path | What it is |
|---|---|
| `result/qc_results/loan_01_v8-2.json` | The second run's QC output for loan 01 — confirmed identical to `loan_01_v8.json` |
| `result/rules/comprehensive_e2e_v8_ruleset-2.json` | The second run's compiled ruleset — confirmed identical to `comprehensive_e2e_v8_ruleset.json` |
| `result/qc_results/run_018_guideline_to_loan01_e2e_verify2_results.json` | Run summary/manifest for the second run |
| `storage/logs/run_018_guideline_to_loan01_e2e_verify2.jsonl` | Full evidence-chain log for the second run |
| `output/RUN-018-VERIFICATION-TRACE-2026-07-28.md` | This document |

**Nothing from tonight's demo file (`loan_01_v8.json`) or its associated ruleset/log/summary was modified or overwritten by this exercise.**
