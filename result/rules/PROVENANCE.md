# Provenance — `rules/`

| File | What it is |
|---|---|
| `comprehensive_ruleset.json` | The compiled, engine-loadable `Ruleset` (real `Check` objects, `Ruleset.to_json()` format — loadable via `Ruleset.from_dict()`) |
| `comprehensive_applicability.json` | `check_id -> [program, ...]` map. `"UNTAGGED"` means the source row had no program-prefixed Exception Code and fails open (applies to every loan), per `qc_engine/compiler/program_gating.py`'s existing design. |

## Source

- **Compiled:** 2026-07-23, `p0/compile_runs/run_008_comprehensive_8442/run_comprehensive.py`
- **Source data:** all 8,442 real rows across every sheet of every workbook in `demo/rules/*.xlsx` — all 6 real programs (FHA, VA, USDA, Freddie Mac, Fannie Mae, SONYMA) plus 1,171 untagged/universal rows. No program filter at compile time (unlike the earlier 5,365-row runs, which were restricted to 4 programs).
- **Model:** Bedrock Claude Sonnet 4.6, temperature=0, one row per call, 20 parallel workers.
- **Cost:** $394.30 for this final, successful compile pass. (Two earlier attempts tonight cost an additional $394.28 + $283.44 and were discarded/superseded — see `output/COMPREHENSIVE-RULESET-OVERNIGHT-REPORT-2026-07-23.md` §1 for the full accounting and why.)
- **Result:** 8,399 checks compiled (99.5% of 8,442), 43 failed to parse, 495 checks with an honestly-`UNSPECIFIED` threshold (2026-07-22 hallucination-prevention fix — see `qc_engine/compiler/compile_llm.py`'s `SYSTEM_PROMPT`).
- **Ruleset content SHA-256:** `5cb467ee07a87572f995aaa7e35cd99e6335682640ba1f9e2b540a5a49dcbcc9` (verify with `Ruleset.from_dict(json.load(open(...))).sha256()`)
- **Unsigned.** No SME has reviewed or signed off on this ruleset yet — per this project's "compile once, SME sign-off" discipline (`CLAUDE.md` Non-Negotiable #1), this is a real, unsigned candidate artifact, not yet cleared to run in place of the validated baseline.

## Deduplication note

8,399 check *instances* collapse to **4,837 unique check IDs** — the real AMQ workbooks restate
the same underlying condition across each program's own sheet. Anything consuming this ruleset for
a single loan should deduplicate by `id` first (keep one representative), matching what
`compile_runs/run_008_comprehensive_8442/run_against_loans.py` already does — otherwise the same
real-world check appears to fire dozens of times for one condition.

## How to refresh

```bash
# from the repo root
python3 p0/compile_runs/run_008_comprehensive_8442/run_comprehensive.py   # resumable — see its own docstring
cp p0/compile_runs/run_008_comprehensive_8442/ruleset.json result/rules/comprehensive_ruleset.json
cp p0/compile_runs/run_008_comprehensive_8442/applicability.json result/rules/comprehensive_applicability.json
```

Update this file's cost/date/SHA-256 after any refresh.
