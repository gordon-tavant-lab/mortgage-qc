# 008 — Tri-state results (PASS / FAIL / NEEDS_REVIEW) via SHACL severity

**Status:** Proposed 2026-07-29 — awaiting Gordon's decision (explained in
non-technical terms in the session summary).

## The idea, plainly
Not every rule can end in a clean yes/no. Three honest outcomes exist:
1. **PASS** — the machine checked and it's fine.
2. **FAIL** — the machine checked and it's definitively wrong (citable proof).
3. **NEEDS_REVIEW** — the machine either (a) couldn't get the data it needed, or
   (b) the rule itself requires human judgment. Silence here would be dangerous:
   a check that quietly passes because its data was missing looks identical to a
   check that genuinely passed.

## Mapping onto SHACL (zero new machinery)
SHACL has three built-in severity levels; we map them:
- `sh:Violation` → **FAIL** (defect, blocks the loan)
- `sh:Warning` → **NEEDS_REVIEW** (goes to the human exception queue)
- `sh:Info` → informational only

Two Warning patterns implemented in the pilot:
- **Data-missing guard**: if a check's required field wasn't extracted, a Warning fires
  ("could not verify X — data not extracted") instead of silent pass.
- **Judgment rule**: a rule whose threshold is inherently judgment-based (e.g. loan 05's
  site-value justification) fires as Warning — routed to a human, never auto-failed.

## Recommendation (pending Gordon)
Adopt the mapping above. It reproduces the prod design's PASS/FAIL/NEEDS_REVIEW
tri-state and the ExceptionReview queue semantics with standard SHACL, no custom
result model.

## Evidence
- `src/shacl_pilot/blocks/property_appraisal.ttl` — judgment rule fires as `sh:Warning` (site-value/outbuildings justification, lines 85–89), per the mapping above.
- `src/shacl_pilot/run_audit.py` — tri-state-plus statuses live in the runner: pilot checks report PASS / FAIL / NEEDS_REVIEW / NO_DATA (lines 239–248); workbook rules additionally report NOT_EVALUATED, never a silent pass.
- The motivating honest stats (PASSED=0, NO_DATA=57 across loans 01–05) came from the v2 session run; that console output was not persisted, but the accounting that produced it is in `run_audit.py` (per-loan status counters, lines 271–273).
- `src/shacl_pilot/compiled/ruleset.json` — `doc_presence` rules (134) resolve to PASS or NEEDS_REVIEW (absence goes to a human, decision 009), the data-missing-guard pattern at workbook scale.
