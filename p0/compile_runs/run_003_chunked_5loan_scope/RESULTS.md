# Compile Run 003 — Full 5-Loan Scope (Chunked)

**Status: real, unsigned, referential-integrity-screened candidate checks covering the entire 5,365-row scope.** Compiled in chunks of 500 rows to avoid AWS credential expiration during the ~40-minute run. Real Bedrock calls (Sonnet 4.6, temperature=0), real measured cost.

## Result

- Total rows in scope: 5,365
- Compiled successfully: 5,310
- Parse failures: 55 (1.0%)
- Referential integrity: **PASSED** (after field deduplication)
- New fields proposed: 47
- Chunks completed: 11/11

## Real cost (measured across all chunks)

- Real spend: **$242.14**
- Cost per row: $0.0451

## Chunk summary

- Chunk 1: 500 rows → 494 compiled, cost $22.73
- Chunk 2: 500 rows → 496 compiled, cost $22.74
- Chunk 3: 500 rows → 495 compiled, cost $22.73
- Chunk 4: 500 rows → 493 compiled, cost $22.72
- Chunk 5: 500 rows → 496 compiled, cost $22.73
- Chunk 6: 500 rows → 497 compiled, cost $22.70
- Chunk 7: 500 rows → 494 compiled, cost $22.75
- Chunk 8: 500 rows → 493 compiled, cost $22.71
- Chunk 9: 500 rows → 495 compiled, cost $22.71
- Chunk 10: 500 rows → 498 compiled, cost $22.72
- Chunk 11: 365 rows → 359 compiled, cost $16.61

## Compiled by program

- FHA: 1,210
- VA: 948
- USDA: 872
- Fannie Mae: 2,280

## Next step

This is a full, unsigned candidate ruleset. SME review and sign-off required before this can be run against real loans, per the existing `002b`/`002c` provenance discipline.
