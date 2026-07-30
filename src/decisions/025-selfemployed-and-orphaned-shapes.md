# 025 — SelfEmployedDocsShape wired; 4 pilot shapes confirmed orphaned from the real workbook

**Status:** Accepted 2026-07-30

## Wired (verified)
`SelfEmployedDocsShape` (income-verification block) was wired to zero exception codes.
The income-verification triage found `O-VA-00364` (row 2487) and `O-FHA-02293` (row
2410) — both independently verified (full row text pulled directly, not trusted from
the agent summary) to describe the same real condition the shape already checks:
self-employed borrower, missing YTD P&L and/or balance sheet. Wired; ruleset recompiled
(sha `b9afbf4f23b6`); full audit re-run, still 25/25, 0 unexplained extras, deterministic.

## Orphaned shapes — a pattern worth naming honestly
Across this round's 5 block triages, agents checking whether ANY workbook row matches
an existing hand-built shape found that **4 of the original 25 pilot shapes have zero
matching rows anywhere in the actual 5,520-row AMQ workbook**, confirmed by direct CSV
search, not assumption:

- `CompDistanceShape` (property-appraisal) — no comp-distance row exists; this shape's
  5.0-mile threshold was already flagged `SME-PLACEHOLDER-UNSPECIFIED` (decision-era
  rule-fidelity discipline) — now confirmed doubly unfounded: not just an unsourced
  number, but not backed by any real AMQ question at all.
- `SiteValueJustificationShape` (property-appraisal)
- `UsdaEligibilityDocShape` (property-appraisal)
- `UsdaIncomeLimitShape` (product-specific) — searched across the ENTIRE workbook per
  the product-specific-check triage, zero matches.

## What this means
These 4 shapes were built during the original loan-01/loan-05 pilot (this session's
early turns) directly from the synthetic loan documents and Gordon's hand-authored
`Answers.md`/`defect_manifest.json`, **not from an AMQ workbook row** — they encode real
defects the demo loans contain, but the actual Post-Closing AMQ questionnaire (5,520
rows) apparently doesn't ask the exact question they answer, at least not in a form our
text search can find. They still function correctly for the loan-01/05 gauge
reconciliation (decision 007) — that reconciliation was never routed through
`amq_compiler.py`'s `MAPPED_SHAPES` mechanism, so this doesn't break anything running
today. But it means these 4 shapes will **never** show as "mapped" in any full-workbook
compile, and their `caro:checkId`s are decorative from the compiler's point of view.

## Recommendation (not yet actioned — flagged for a decision)
Before assuming the demo's headline "5/5 defects × 5 loans = 25/25" answer-key
reconciliation generalizes to real QC coverage, confirm whether these 4 conditions
really have no AMQ counterpart (possible: different wording our search missed; the
Pre-Funding sheet, never ingested, per CLAUDE.md; or a genuinely demo-only scenario) —
this is a fact-finding item, not a code change, and belongs in a future session.
