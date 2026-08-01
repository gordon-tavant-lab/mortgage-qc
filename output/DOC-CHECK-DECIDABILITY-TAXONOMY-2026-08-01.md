# Doc-check decidability taxonomy: finding, decision, and resolution plan

**Date:** 2026-08-01
**Scope:** the 365 `doc_type_not_curated` checks (part of `NOT_COMPILED`) surfaced in Addendum 6's
"converted total dropped 872 → 224" finding.

## Gordon's question

> 1. I thought we built the document mapping, we should be able to fix "wrong document lookup"
> 2. That should have a category, name this to point to the original rule issue, and not bring
>    this in the rule engine for audit
> 3. This is important and we need to fix this.

## Finding 1: the document-mapping tool can't fix most of these — verified, not assumed

Cross-referenced all 365 `doc_type_not_curated` checks against `doc_all_classified.json` (the
5-way decidability classification built during the original A-category root-cause pass:
`PURE_PRESENCE` / `PRESENCE_GATE` / `COMPOUND_DOCS` / `TRIGGER_GATED` / `NOT_DOC_DECIDABLE`).
**Document-name matching (`llm_doc_mapper.py`) only ever helps `PURE_PRESENCE`-shaped checks** —
ones decidable purely by whether one named document exists, no compound or conditional
qualifiers. That population is exactly 9 checks ruleset-wide, and it's already exhausted: 3 wired
to a real curated match, 6 individually reviewed and rejected for a specific, documented reason
(no matching Touchless vocabulary entry, or a compound per-applicant requirement the payload can't
satisfy — see `output/BAKEOFF-P0-VS-SRC-GOLD-RULESET-2026-07-31.md` Addendum 5). Re-verified: the 6
rejected rows found in the 365 today are the exact same 6 already reviewed, not new candidates.

**Real breakdown of the 365, by the actual rule-level reason:**

| Category | Count | What it needs |
|---|---:|---|
| `TRIGGER_GATED` | 230 | The check only applies under a scenario/fact trigger (e.g. "if rental income was used") — needs trigger-fact resolution machinery (same category of work as `context_flags`/A2 scenario-gating), not document matching |
| `PRESENCE_GATE` | 99 | One document's presence/absence gates whether a *different* requirement applies — needs real conditional-check logic |
| `COMPOUND_DOCS` | 11 | Needs two or more documents compared/considered together — needs real multi-document comparison logic |
| `PURE_PRESENCE` (reviewed, rejected) | 6 | Already individually reviewed; correctly stays unwired, not a gap |
| `NOT_DOC_DECIDABLE` | 3 | Not really a document question — likely a `check_type` misclassification (same pattern as the earlier `CIP DATA POINTS` fix) |
| Unclassified (before today) | 16 | Never triaged in the original classification pass |

**None of the top three (340 of 365) are document-lookup problems at all.** They need
genuinely different, larger machinery than what the document-mapping tool does. That's the honest
answer to point 1: the tool was never going to touch this population, not because it wasn't run
hard enough, but because it solves a different problem than what's actually blocking these checks.

## Finding 2: investigating this surfaced a real, fixable bug

Of the 16 never-classified rows, checking each individually found **9 that explicitly reference DU
or EPIC** and match the exact same `\bDU\b`/`\bEPIC\b` word-boundary regex already used to build
`autopass_no_system_access.json`'s 66-entry list — but were absent from it. Confirmed by literally
re-running that regex against their verbatim text: 9 of 11 candidates matched. This is a real
execution gap in the original scan (the regex was correct; the scan simply didn't catch these 9),
not a design flaw.

**Fixed:** added all 9 to `autopass_no_system_access.json` (7 `du_not_accessible`, 2
`epic_not_accessible`), individually verified against their actual description text first (see that
file's own `correction_2026-08-01` meta field for the full verification trail). Re-ran both engines:

- 2 (`PC::UGV Exception`'s `UGVAPPRVL`/`UGV EPIC`) correctly resolve `NOT_APPLICABLE` — they're
  gated on `Loans.LoanType == Portfolio`, and this loan is Conventional/FNMA, not Portfolio.
- 7 (`PC::DUValid`'s cluster) correctly resolve `NEEDS_REVIEW`/`NO_DATA` — blocked on the
  already-known, already-tracked Category C gap (`Loans.Underwriting_Type` is null in the payload).

Neither outcome is a bug — it confirms the autopass mechanism still respects genuine applicability
facts first, rather than blindly passing everything that mentions DU/EPIC.

**Left as still-unclassified (2 of the original 16 that don't match DU/EPIC, plus 5 more the
9-check investigation surfaced along the way — 7 total):** `PC::UGV Exception`/`PrivateBank`,
`PC::UGV Exception`/`UGV Identifier`, and 5 others (`O-FNM-15381`/`O-FNM-55515`,
`O-FNM-15374`/`O-FNM-50304`, `O-FNM-15381`/`O-FNM-53853`, `O-FNM-15381`/`O-FNM-59132`,
`O-FNM-15446`/`O-FNM-54189`). Genuinely need a fresh triage pass — not done today, tracked here so
it isn't silently dropped.

## Finding/decision 2: real categorization, not a flat engine label

Gordon's ask: "that should have a category, name this to point to the original rule issue, and not
bring this in the rule engine for audit." Implemented directly:

- Relocated the classification data from a gitignored, session-dated `src/shacl_pilot/.../
  nodata_research/doc_all_classified.json` to a permanent, shared location both engines read:
  `storage/rules/gold/data/doc_decidability_classification.json` (matching where
  `demo_exclusions.json`/`autopass_no_system_access.json`/`scenario_applicability_*.json` already
  live), with a proper `_meta` block explaining provenance and what each category means.
- Both converters (`import_gold_ruleset.py`, `ruleset_to_shacl.py`) now load this file and, for any
  uncurated `doc_presence`/`doc_completeness` check, emit a precise `unsupported` reason naming the
  real cause (`doc_type_not_curated:trigger_gated_needs_fact_machinery`,
  `...presence_gate_needs_conditional_logic`, `...compound_docs_needs_multi_doc_logic`,
  `...pure_presence_reviewed_rejected`, `...not_doc_decidable_likely_misclassified`) instead of the
  single flat `doc_type_not_curated` label. The 7 rows still genuinely unclassified keep the
  generic reason — an honest gap, not hidden behind a fake category.

This means a future audit of `NOT_COMPILED` reasons can now see *why* a doc check is stuck without
re-deriving it by hand every time — the category travels with the compiled ruleset's own stats
output.

## Decision on point 3: what "fixing this" actually means going forward

Given the real sizing (340 of 365 need new machinery, not a quick fix), the honest plan is staged,
not a single "fix it" pass:

1. **Done today:** the 9-row autopass gap (mechanical, verified, shipped), and the categorization
   fix (mechanical, shipped) — both real, both small, both immediately verifiable.
2. **Next, bounded:** triage the remaining 7 unclassified rows — small, contained, no new machinery
   needed, just individual review (same discipline as the original 9/37 candidate reviews).
3. **`NOT_DOC_DECIDABLE`'s 3 rows:** a `check_type` reclassification review, same pattern as
   `CIP DATA POINTS` — small, mechanical once reviewed.
4. **The real work, not started, explicitly sized so it isn't confused with a quick fix:**
   - `PRESENCE_GATE` (99 rows) — needs a real conditional-document-logic mechanism.
   - `COMPOUND_DOCS` (11 rows) — needs real multi-document comparison logic.
   - `TRIGGER_GATED` (230 rows) — needs trigger-fact resolution machinery; the biggest bucket by
     far, and the same category of work as the `context_flags` generalization
     (`output/BAKEOFF-P0-VS-SRC-GOLD-RULESET-2026-07-31.md` Addendum 8) — likely the highest-leverage
     next investment, since the same machinery pattern (a curated flag → derivable-fact lookup)
     already proved out this session.

Not yet decided: which of the three "real work" buckets to tackle first, or how to resource it.
That's the next conversation.

## Verified

`pytest p0/` 445 passed/3 skipped/1 xfailed; 25/25 known-defect gate PASS; bake-off agreement
unchanged at 75/0 (this pass is a labeling + autopass-list correction, not a verdict-generating
fix beyond the 9 rows already accounted for in Addendum 8's own before/after table).
