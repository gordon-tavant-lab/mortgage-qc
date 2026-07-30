# 024 — Fixed the doc_presence auto-classifier's two root-cause bugs

**Status:** Accepted 2026-07-30 — found independently by 3 of 5 parallel block-triage
agents (credit-liabilities, property-appraisal, product-specific), each following the
decision-018 "verify before trusting" discipline against a different block, without
knowledge of each other's work. That independent triangulation is itself the evidence
this was a real, systemic bug — not a one-block quirk.

## The two bugs (both proven against actual AMQ rows)
1. **No word boundaries.** `DOC_KEYWORDS`' `r"credit report"` matched as a bare
   substring inside "credit **report**ed" — a different word entirely. Proof:
   `O-FNM-00200`'s exception description ("a written explanation... were **not
   provided**") false-matched via this, auto-tagged `doc_presence` → GREEN, while its
   byte-for-byte-identical-condition twin `O-VA-00143` correctly stayed unmapped (no
   "not provided"/"missing" text at all) — the two AMQ rows describe the identical
   real-world defect, one degraded through the bug, the other exposed it.
2. **No proximity requirement.** `NOT_IN_FILE_RE`'s bare `"not provided"` / `"missing"`
   alternatives fired anywhere in a compound sentence, regardless of distance from the
   document-type keyword. property-appraisal-review was hit hardest: 33 of 35
   auto-tagged rows were narrative-commentary-adequacy language ("without comment,"
   "not adequately supported," "not analyzed") — the word "appraisal" appearing
   somewhere in the sentence, an unrelated absence-word appearing somewhere else.

## The fix
- Added `\b` boundaries to every `DOC_KEYWORDS` pattern (root-caused bug 1).
- Added a `PROXIMITY_WINDOW` (50 chars) requiring the absence-phrase and the doc-type
  keyword to occur near each other, not just co-occur anywhere in the text.
- Added a `NARRATIVE_QUALIFIER_RE` exclusion (adequate/sufficient/acceptable/analysis/
  comment/support/correctly/properly/satisfactory/reasonable/appropriate/justif*) —
  if any of these appear in the span between the two matches, the classification is
  rejected as a commentary/adequacy condition, not plain document presence.

## Result — real improvement, NOT full precision
`doc_presence`-classified rules dropped **135 → 91** ruleset-wide (33% reduction) after
recompile. Per block: property-appraisal 36→25, credit-liabilities 24→14,
product-specific 8→6. **This is honestly a partial fix, not a complete one** — the
agents' full manual reads found even fewer true positives than the mechanical fix now
leaves (e.g. property-appraisal's hand-verified count was 2, not 25). A regex-based
proximity/exclusion heuristic cannot fully replace a human or LLM reading each row's
actual meaning. **The authoritative classification for any block that has been through
Layer-2 hand triage is that block's own `triage_*.json`/packet, not the mechanical
`eval_class` alone** — this fix reduces the blast radius for blocks NOT yet hand-triaged
(the other 9), it does not retroactively certify the 7 blocks already triaged (their
hand classifications already superseded the mechanical tag).

## Verification
Full audit re-run after the fix: 25/25 answer-key defects, 0 unexplained extras, 1
justified extra (unchanged), fully deterministic. Ruleset sha stamped
(`fc829b39c857` after the classifier fix alone, `b9afbf4f23b6` after also wiring
decision 025's SelfEmployedDocsShape codes).
