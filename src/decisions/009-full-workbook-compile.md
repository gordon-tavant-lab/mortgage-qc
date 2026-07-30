# 009 — Compile the FULL AMQ workbook; hand-authored checks are only the field-mapped subset

**Status:** Accepted 2026-07-29 (Gordon — "there are supposed 5000+ post-fund rules total,
the total rules run should be at least 500+")

## Decision
The unit of scale is the full Post-Closing AMQ workbook (5,520 rows), not a hand-picked
demo subset. `amq_compiler.py` (Layer 1, mechanical, no LLM) compiles it into 4,167
active rules — one rule per unique (Question Code, Exception Name) pair — after
excluding the 379 "Discarded"-category pairs. Every audited loan runs its full
applicable rule population (689–1,385 rules depending on program; see decision 010),
satisfying the ≥500 bar with real workbook rules, not padding.

## Honest evaluability classes (no fake passes)
- `mapped` — a hand-mapped field-level SHACL shape exists (the 25 pilot checks).
- `doc_presence` — exception text says a recognizable document is "not in file /
  missing / not provided" (134 rules auto-compiled to inventory checks). Document
  present → PASS; absent → NEEDS_REVIEW (synthetic folders are partial by
  construction, so absence goes to a human, not auto-FAIL).
- `unmapped` (4,026) — applicable but no data contract yet → runtime status
  NOT_EVALUATED, reported loudly. **Never a silent pass.**

## The two-layer compile (Gordon's LLM question)
Layer 1 (this, today): deterministic parse/classify/filter/organize.
Layer 2 (next): an LLM-assisted compile pass reads each unmapped rule's text and
proposes {required docs, required fields, comparison logic} → generates the SHACL
shape → SME validates → hash-versioned (decision 004). The LLM works at
CONFIGURATION time only; runtime stays a deterministic validator — the project's
compile-then-run doctrine, now with an empirical harness to measure it.
