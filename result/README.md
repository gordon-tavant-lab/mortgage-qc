# `result/` — Central Artifact Store

The single, current location for the three artifacts that used to be scattered across
timestamped `p0/compile_runs/run_NNN_*/` directories and `p0/fixtures/from_docs/`. Each
subdirectory has its own `PROVENANCE.md` naming the exact source run, date, and (for
compiled artifacts) the real Bedrock cost — so nothing here is unlabeled or untraceable
back to how it was produced.

**This is a snapshot store, not a live symlink.** The files here are copies (checksum-
verified against their source at copy time). If a source artifact is regenerated
(re-compiled, re-extracted, re-run), this store does **not** auto-update — see each
subdirectory's `PROVENANCE.md` for the "how to refresh" command.

Lives at the repo root, alongside `p0/` (the engine code) and `output/` (deliverables/reports) —
not nested inside either.

## What's here

| Directory | Contents | Source |
|---|---|---|
| `rules/` | The compiled, engine-loadable ruleset from all 8,442 real AMQ rows (8,399 checks, 4,837 unique after dedup) | `p0/compile_runs/run_008_comprehensive_8442/` |
| `loans/` | The 5 parsed/extracted synthetic loan fixtures (`CanonicalLoan`-shaped JSON, full citations) | `p0/fixtures/from_docs/` |
| `qc_results/` | QA/QC engine output — both the comprehensive-ruleset run and the validated 21-check baseline run, per loan | `p0/compile_runs/run_008_comprehensive_8442/` + `p0/compile_runs/run_007_engine_5loans/` |

## What's deliberately NOT here

- **The validated 21-check baseline ruleset** (`p0/fixtures/ruleset_defects.py`) is Python code, not
  a static file — it builds its `Ruleset` dynamically per loan (program-gated at call time via
  `defects_ruleset_for(loan)`). It's the proven, trusted rule set (100% recall on the 25 known
  planted defects, 0 report drift) — reference it directly in code, don't duplicate it here as a
  stale JSON snapshot that could silently drift from the real logic.
- **Raw source PDFs / MISMO XML** (`demo/syn/loan 0{1-5}/`) — those are inputs to extraction,
  not extracted output; `loans/` already holds what came out of them.

## Known limitations of the rules artifact (read before trusting a result)

Per `output/COMPREHENSIVE-RULESET-OVERNIGHT-REPORT-2026-07-23.md` (full details):
- Only **152 of 4,837** unique checks reference a field these 5 synthetic loans can possibly have
  data for — the other 96.9% reference document types outside this test dataset's scope. Not a
  bug; these two artifacts (a general lender ruleset vs. 5 narrowly-scoped test loans) simply don't
  fully overlap.
- **495 checks** have a threshold/condition intentionally left as the literal string `"UNSPECIFIED"`
  — the source AMQ row implied a limit but didn't state the exact number, and the compiler is
  required to say so honestly rather than invent one (2026-07-22 hallucination-prevention fix,
  `qc_engine/compiler/compile_llm.py`). The engine surfaces these as `NEEDS_REVIEW` /
  `UNSPECIFIED_THRESHOLD`, never a crash, never a silent skip.
- Two specific findings need an SME sanity pass before trusting them as real (not data-population
  artifacts) — see the overnight report's section 5, caveats 1-2.
