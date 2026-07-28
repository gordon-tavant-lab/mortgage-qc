# Provenance — `qc_results/`

| File | What it is | Ruleset used |
|---|---|---|
| `baseline_only_dispositions.json` | Per-loan engine results (all 5 loans, full audit trail: inputs, citations, review reasons) | The **validated** baseline (`fixtures/ruleset_defects.py`) — 100% recall on the 25 known planted defects, 0 report drift. **27 checks as of 2026-07-23** (21 original + 6 new doc-vs-MISMO reconciliation checks — see below). |
| `comprehensive_vs_baseline_results.json` | Per-loan results from **both** rulesets side by side — the comprehensive 8,399-check ruleset (deduplicated, program-gated, catalog-scope-filtered to the 152 checks these loans can speak to, **and now pre-funding-excluded — post-closing only**) AND the same validated 27-check baseline, for direct comparison | Both. Regenerated 2026-07-23 (post pre-funding exclusion wiring) — baseline side reflects the full 27 checks. |

## 2026-07-23 update: pre-funding exclusion wired into the actual QC run (not just built as a side file)

This project is post-closing QC only (CLAUDE.md). The original comprehensive compile (before this
distinction was caught) mixed pre-funding rows into the same source workbooks alongside post-closing
rows — so the raw 8,399-check `comprehensive_ruleset.json` still contains checks derived from
pre-funding content. `run_009_prefunding_exclusion/identify_prefunding_checks.py` (see
`rules/prefunding_check_ids.json`) determined which check IDs those are by re-compiling the 3,344
known pre-funding rows in isolation and cross-referencing against the main ruleset (2,490 confirmed
overlap). That list existed as data only until this update — `run_against_loans.py` now actually
filters `exclude_from_qc_runs` out of the catalog-in-scope set before running against loans: of the
152 in-catalog-scope checks, **84 were pre-funding-derived and are now excluded**, leaving **68
checks** as the final post-closing-only ruleset evaluated against the 5 loans. All 5 loans still
resolve to `NEEDS_REVIEW`; the surfaced-defect set changed only in that pre-funding-only checks (e.g.
entity/trust-formation, private-bank pre-close conditions) no longer appear.

## 2026-07-23 update: doc-vs-MISMO reconciliation extended to all comparable fields (Bucket E)

Prior to this, only 1 field (`fha_case_number_1003`, FHA-only) had a check comparing the closing-doc
PDF value against the MISMO XML value. Direct inspection of all 5 loan fixtures found 6 fields total
carry both a `doc` value and a `sources.mismo` value — extended to all of them
(`fixtures/ruleset_defects.py`, Bucket E, `chk-reconcile-*`):

| Field | Kind | Normalizer / tolerance | Result across 5 loans |
|---|---|---|---|
| `borrower_name` | agree_categorical | `name` (drops middle-initial noise) | PASS on all 5 |
| `note_rate` | agree_numeric | tolerance `0` | PASS on all 5 |
| `loan_amount` | agree_numeric | tolerance `0` | PASS on 3; **FLAG on loans 02 and 05 — genuine $3,350 and $2,460 discrepancies, new findings** |
| `property_value` | agree_numeric | tolerance `0` | PASS where MISMO data exists (01, 04); `NEEDS_REVIEW` elsewhere (no MISMO value to check against, not a false pass) |
| `borrower_ssn` | agree_categorical | `ssn_last4` | `NEEDS_REVIEW` on loans 02-05 (no MISMO value for this field on those loans) |
| `property_address` | agree_categorical | `address` | `NEEDS_REVIEW` on loans 02-05 (same reason) |

Adding `chk-reconcile-property-value` surfaced a real pre-existing gap: the field `property_value`
was extracted and used (`loan.facts.property_value` for LTV; `fields.property_value` with real
citations) since spec 000, but was never registered in `field_catalog.json` — fixed by adding a
proper catalog entry (378 fields total now, up from 377), not by working around the referential-
integrity test that caught it.

Normalizer/tolerance choices are grounded in the actual doc-vs-mismo value pairs observed across all
5 loans (not invented) — see `fixtures/ruleset_defects.py`'s own module docstring for the full
evidence behind each choice. Zero regression: `harness.py`'s 1000-run digest unchanged, all 157 tests
pass.

## Source

- **`baseline_only_dispositions.json`:** 2026-07-23 (refreshed for the Bucket E extension; originally
  2026-07-22), `compile_runs/run_007_engine_5loans/` — direct `qc_engine.run()` calls, no LLM
  involved at evaluation time (pure function of loan + ruleset).
- **`comprehensive_vs_baseline_results.json`:** 2026-07-23, `compile_runs/run_008_comprehensive_8442/run_against_loans.py`
  — see that script's own docstring for the two honesty notes baked into how it filters:
  (1) deduplication by check ID, (2) catalog-scope filter (only 152 of 4,837 unique checks reference
  a field these 5 loans can possibly have) plus real per-loan program gating via
  `program_gating.applies_to()`.

## Headline result (both files agree)

All 5 loans resolve to **NEEDS_REVIEW** on both rulesets — cross-validated: several checks the
comprehensive ruleset compiled *independently* (from different source rows than the baseline's
hand-authored checks) correctly rediscovered the same real planted defects the baseline already
found.

## Known caveats (do not treat every "FAIL" here as a confirmed real finding without reading this)

1. **Loan 01** (generic "Conventional Purchase", no named GSE) has ~48-52 results flagged
   `"ambiguous_program": true` — checks compiled specifically for Fannie Mae *or* Freddie Mac that
   can't be resolved without knowing which GSE actually owns this loan. A real, pre-existing
   data-modeling gap (`program_gating.py`'s own FR-005), not a new bug.
2. **`gift-funds-source-documented`** and **`intent-to-proceed-provided`/`-present`** fire as `FAIL`
   identically across most or all 5 loans, even though only specific loans have a genuine planted
   defect for that condition. Most likely a field-population artifact (the underlying field was
   only ever filled in for the one loan designed to test it) rather than a real cross-loan finding
   — needs a quick SME check against the actual loan data before trusting these specific rows.

Full detail on both: `output/COMPREHENSIVE-RULESET-OVERNIGHT-REPORT-2026-07-23.md` §5.

## How to refresh

```bash
# from the repo root
python3 p0/compile_runs/run_007_engine_5loans/<script>              # baseline-only run
python3 p0/compile_runs/run_008_comprehensive_8442/run_against_loans.py  # comprehensive + baseline
cp p0/compile_runs/run_007_engine_5loans/dispositions.json result/qc_results/baseline_only_dispositions.json
cp p0/compile_runs/run_008_comprehensive_8442/combined_results.json result/qc_results/comprehensive_vs_baseline_results.json
```
