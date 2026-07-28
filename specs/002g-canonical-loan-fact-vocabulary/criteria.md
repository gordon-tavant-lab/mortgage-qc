# Criteria: 002g Canonical Loan-Fact Vocabulary

Exit conditions (all must hold; each verified by running, not asserting):

1. `pytest p0/tests -q` exits 0 — including the three new test files — with **zero** changes to any
   pinned digest constant (`Check` schema untouched; SC-003).
2. `python3 p0/harness.py` exits 0 against the current pinned baseline (`82175d07...`).
3. SC-001 proven on real data with zero LLM calls: real Retail gift rows → Layer 0 → signed
   vocabulary → compiled `applies_if` referencing `gift_funds_used` → real loan 01 fixture →
   `NOT_APPLICABLE`.
4. SC-002: synonym resolution converges two names onto one canonical field; a novel name is
   surfaced as a candidate, never auto-added; an unmapped Layer-0 answer refuses resolution.
5. US3: any resolution attempt against an unsigned vocabulary fails loudly
   (`VocabularyNotSignedError`), matching the KB's `CorpusNotSignedError` discipline.
6. FR-008: the replay report over the 5 real from_docs loans names exactly the checks whose status
   flips between a ruleset without and with the gift `applies_if` — no more, no fewer.
7. `storage/fact_vocabulary/v1.json` exists, loads, carries the honest placeholder signature
   (`NOT-A-REAL-SME-pending-kayla-review`), and its gift binding derives from the real 570606
   cluster (not hand-typed answer strings).
8. No new LLM call in any default path or test (FR-009) — `attach_preconditions` default is
   Layer-0-only.
