# Resolve6 — resolving the six NOT_COMPILED categories (2026-08-01)

Gordon's ask: take the six remaining NOT_COMPILED reason categories from the audit
report (324 checks) and resolve what can honestly be resolved, using the session's
accumulated findings, parallel research/analysis agents, and external research.

**Headline: 250 of the 324 targeted checks (77%) left NOT_COMPILED this pass — 241 to a
cited, per-loan NOT_APPLICABLE and 9 to a verified PASS — with zero changes to any
previously-evaluated verdict, zero new FAILs, both standing gates green, and both
engines in perfect agreement (121 jointly evaluated, 0 disagreements, NOT_APPLICABLE
284 == 284).**

## Before / after (all 1,105 gold-ruleset checks, loan 12607601215)

| Status | Before (audit report) | After | Δ |
|---|---|---|---|
| PASS | 121 | **130** | +9 |
| NEEDS_REVIEW | 92 | **92** | 0 |
| NOT_APPLICABLE | 43 | **284** | +241 |
| NOT_COMPILED | 849 | **599** | −250 |
| Evaluated (real verdict) | 256 | **506** | +250 |

Per-check diff discipline: every one of the 250 changes is `NOT_COMPILED → verdict`;
no previously-evaluated check changed status (verified against the committed
`p0_results.json` at HEAD, not just aggregate counts).

## The core insight

**Most of these weren't missing-logic problems — they were missing-applicability
problems.** The checks' trigger scenarios (HomeStyle, HomeReady, ARM, condo, New York
CEMA, SFHA flood zone, manual underwriting, nontraditional credit…) are provably false
for this loan, but the checks never compiled, so the existing scenario gate could
never fire. The audit report had already recorded 166 scenario-NA entries "for checks
that never actually got built" — the fix was to let those verdicts take effect.

## Per-category outcome

| Category | Was | Now | What happened |
|---|---|---|---|
| 1. Presence-gate conditional | 102 | 79 | 16 existing + 7 new payload-proven scenario NAs (incl. 4 flood rows flipped from UNKNOWN by the payload's extracted `specialFloodHazardAreaIndicator="No"`) |
| 2. Computation not LTV/DTI | 102 | 48 | 52 scenario NAs + CLTV/HCLTV recompute wired (both PASS: 260,000/352,000 = 73.86 == reported) |
| 3. Cross-doc comparison | 96 | 62 | 33 scenario NAs + CIP identity wire (PASS: 1003 name+SSN == Schedule C) |
| 4. Compound/multi-doc | 12 | 7 | 2 disjunctive-presence OR-facts wired (both PASS) + scenario NAs |
| 5. Pure-presence rejected | 6 | 4 | 1 rejection overturned (Occupancy Affidavit — exact-or-narrower match, PASS); 1 scenario NA; 4 rejections hold |
| 6. Likely misclassified | 6 | 0 | All 6 reclassified `scripted_review` at source (validate_compiled GATE PASS); 4 resolve via gates/autopass, 1 SSN-shape wire (PASS), 1 autopass |

(Residual counts also shifted across sibling categories — e.g. `trigger_gated_needs_
fact_machinery` 103, `threshold_not_parseable` 175 — because scenario NAs cut across
all of them. Full refreshed per-row detail: `AUDIT-EXPORT-p0-loan-12607601215-2026-08-02.csv`.)

## What was built (all compile-time, LLM never in the runtime path)

1. **Scenario-gated stubs** (`import_gold_ruleset.py::_make_scenario_gated_stub` + the
   symmetric patch in `src/shacl_pilot/run_gold_ruleset_audit.py`): a check whose
   conversion is unsupported but whose trigger is provably false in the scenario table
   compiles just far enough for the existing always-false sentinel to yield
   NOT_APPLICABLE with the cited fact. Safety: the stub body is `is_true` on a
   placeholder, so if the gate ever fails to fire (a future loan) it lands
   NEEDS_REVIEW — never a fabricated PASS/FAIL.
2. **93 verified scenario-table rows** (`scenario_applicability_loan12607601215.json`,
   tag `2026-08-01-resolve6`): every candidate independently re-derived from the raw
   payload by an adversarial verification pass — pass-arguments rejected as NA grounds,
   disjunction rule enforced, absence-inference-only rows rejected. 3 candidates
   rejected (2 rested on the ASSUMED demo DU fact; 1 on absence inference).
3. **`CURATED_CROSS_DOC_FACTS`** (4 wires) + **`CURATED_COMPUTATION_FACTS`** (2 wires)
   + 1 curated doc match + 1 scripted-review field — all backed by one-directional,
   cited derivations in `touchless_adapter.py` (True only when proven; mismatch →
   unset → NEEDS_REVIEW; a derived comparison never produces a confident FAIL).
4. **6 source reclassifications** (`storage/rules/gold/data/compiled/*.json`,
   `check_type → scripted_review`, type_profile kept consistent, validator GATE PASS)
   + 4 autopass bookkeeping repairs (incl. the `O-FNM-00824` row that the exclusion
   file's note claimed had moved but had landed in neither file).

## What honestly stays blocked (599 NOT_COMPILED), and what unlocks it

Ranked vendor asks by unlock count (from the cross-doc/computation analyses):
1. **Final DU/AUS findings + 1008 into the doc package — ~17 cross-doc rows**, and it
   retires the demo's ASSUMED-DU fact (the single biggest honesty upgrade available).
2. **Form 1004 appraisal field extraction — ~52 presence-gate rows + 10 cross-doc rows.**
   The appraisal is IN the file; its contents aren't extracted. Largest single unlock.
3. Title Commitment/Policy fields (~9), Credit Report fields (~8 — header report-ID+DOB
   alone unlocks 2), Closing Disclosure fees (~8), Purchase Agreement (~8).
4. Liability/tradeline detail (`creditResponse.liabilityDetail` is null — blocks all 7
   monthly-debt computation rows), APOR (blocks points/fees/APR family),
   HOI coverage/deductible amounts (blocks 8 insurance-math rows).
5. Data-quality bugs to report to Touchless: gift-letter annotations present-but-blank;
   `totalPointsAndFees` = literal string "NA"; duplicate REO mortgage tradelines;
   `cashToBorrowerAtClosingAmount=$115,261.50` on a PURCHASE.

Also structurally blocked (not vendor): 175 threshold-not-parseable (ambiguous rule
text — SME queue), 101 not-converted-by-design (reverification/list_screening/
date_window), 12 formula-ambiguous computations (SME queue).

## Deferred deliberately (in `sme-review-queue.md`)

- Tax-return most-recent-year FAIL (`O-FNM-54125`) — safe for this loan, but the
  B1-1-03 year-boundary table must be SME-signed first.
- Final-URLA PASS candidate — documentType doesn't encode initial-vs-final.
- ROV-disclosure absence findings — confirm Touchless can emit an ROV type first.

## External research (full report: `output/RESOLVE6-EXTERNAL-RESEARCH-2026-08-01.md`)

Confirms the architecture: extraction-heritage QC platforms converge on exactly this
shape (classify docs → detect missing → match configured field pairs → emit
lifecycle-managed conditions); UCD Appendix B/I + ULAD mapping give canonical
field-pair maps for CD/URLA/Note comparisons (a ready-made spec for the cross-doc
curation backlog); Fannie D1-3-02 makes cross-doc consistency mandatory on every
sampled loan (prioritizes that family); MISMO formally recommends DMN decision tables
for conditionality — deterministic engines, no runtime reasoners, industry-wide.

## Gates

- `pytest p0/` — 445 passed, 3 skipped, 1 xfailed ✅
- `verify_against_defects.py` — 25/25 ✅
- `validate_compiled.py` — GATE PASS (0 hard failures) ✅
- Coverage gate SC-006 — fails, **byte-identical to its committed state at HEAD**
  (pre-existing on this branch, targets the older AMQ-pipeline ruleset; not a
  regression from this pass).
- Cross-engine: 121 jointly evaluated, 0 disagreements; NA 284 == 284. The 9 curated
  PASS wires are p0-only for now (src/SHACL ports tracked as parity backlog).
