# Implementation Plan: Standalone `engine/` — the definitive official QC audit engine

**Branch**: `worktree-gold-ruleset-plan` (see spec.md's Assumptions for why this plan lands on
the existing PR #7 branch rather than a new `021-*` branch) | **Date**: 2026-08-02 | **Spec**:
[spec.md](./spec.md)
**Input**: Feature specification from `specs/021-standalone-qc-engine/spec.md`

## Summary

Extract exactly the files the gold-ruleset QC pipeline actually imports at runtime — traced by
reading every file's own `import`/`from` statements, not by copying `p0/qc_engine/` wholesale —
into a new, standalone `engine/` folder that mirrors `p0/`'s internal directory depth exactly (so
existing `_REPO_ROOT`-relative path logic keeps resolving `storage/rules/gold/data/*.json`
correctly with zero code changes). This is a pure file-reorganization feature: no new product
logic, no new algorithm, no design unknowns — the technical approach is "trace, copy, verify,"
not research. `p0/` is untouched (copy, not move); `engine/` becomes the mergeable, minimal
artifact this branch's PR carries into `main`.

## Technical Context

**Language/Version**: Python 3.9-compatible (project-wide constraint, confirmed by
`import_gold_ruleset.py`'s own docstring: "Python 3.9 compatible.")
**Primary Dependencies**: None — every file in the copy set is confirmed Python-stdlib-only
(`decimal`, `json`, `re`, `hashlib`, `sqlite3`, `dataclasses`, `typing`, `datetime`, `argparse`,
`ast`, `collections`, `xml.etree.ElementTree`, `os`, `sys`). Zero third-party packages introduced.
**Storage**: Flat JSON files only — no database. `engine/` reads `storage/rules/gold/data/*.json`
(the compiled gold ruleset) by relative path; it does not duplicate that data.
**Testing**: The copied `verify_against_defects.py` (25/25 known-defect detection against 5
labeled synthetic loans) is the standalone correctness gate for this feature. No new test
framework introduced.
**Target Platform**: Local/CI Python execution (matches `p0/`'s existing runtime — no server, no
network, no model calls at runtime, per Constitution Principle I).
**Project Type**: Library/CLI — a deterministic evaluation engine plus two CLI entry points
(the Touchless adapter, the gold-ruleset compiler-and-runner), not a service.
**Performance Goals**: N/A — this feature doesn't change engine performance, only its packaging.
**Constraints**: `p0/` MUST remain byte-for-byte unmodified (FR-008); the copy MUST NOT
reintroduce any of the superseded/experimental code paths (FR-003, FR-006).
**Scale/Scope**: ~15 files copied (`engine/qc_engine/` core: 8 files + `field_catalog.json`;
`compiler/`: 2 files; `adapters/`: 2 files; `fixtures/from_docs/`: 7 files) + 1 new file
(`README.md`) + 1 one-line constant edit in the copied `import_gold_ruleset.py`. No unknowns —
every inclusion/exclusion decision was already resolved by direct import-trace investigation
during specification (see spec.md's Requirements section and the file-by-file rationale below).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Applies? | Assessment |
|---|---|---|
| I. Determinism of the correct computation | Yes | Unaffected — this feature copies the deterministic engine files verbatim (`money.py`, `engine.py`, `ruleset.py`, etc.); no algorithm, rounding policy, or evaluation logic changes. The one code edit (FR-007, `RUN_DIR` constant) is an output-path label, not computation logic. |
| II. Compile, then run | Yes | Unaffected — `import_gold_ruleset.py` is copied verbatim (minus the one path constant); the LLM-never-at-runtime boundary is untouched. |
| III. Eval is foundational | Yes | Directly served — FR-004 explicitly requires the 25/25 standing-gate harness travel with the copy, so `engine/` can prove ground-truth correctness standalone (SC-003), not weaken eval coverage. |
| IV. Build the core, assume the periphery | Yes | This feature *is* an act of scope discipline — deliberately excluding the superseded AMQ-direct compiler, the ontology-extraction pipeline, and ~20 experiment directories (FR-003) so the shipped artifact is exactly the core, nothing else. |
| V. Source independence | No | Not implicated — this feature doesn't touch source reconciliation logic (`reconcile.py` is copied verbatim, unmodified). |
| VI. Configurable by non-technical users | No | Not implicated — no Route/Block/Check authoring surface is touched by this feature. |
| VII. Configuration is authored data | Yes | Unaffected — the gold ruleset itself (`storage/rules/gold/data/`) stays exactly where it is, read by relative path, not duplicated or altered; the authored-data/signed-artifact model is untouched. |

**Result: PASS, no violations.** No entry needed in Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/021-standalone-qc-engine/
├── plan.md              # This file
├── checklists/
│   └── requirements.md  # Spec quality checklist (completed during /speckit.specify)
└── tasks.md             # Phase 2 output (/speckit.tasks — next step)
```

No `research.md`, `data-model.md`, or `contracts/` — this feature has zero unresolved unknowns
(every technical question was answered by direct source inspection before the spec was written;
see spec.md) and no external interface contract is being introduced (the two CLI entry points
already exist verbatim in `p0/`; this feature relocates them, it doesn't design a new one).

### Source Code (repository root)

```text
engine/                                  # NEW — this feature's entire deliverable
├── README.md                            # NEW, authored (FR-009) — the only new content
├── qc_engine/
│   ├── __init__.py                      # copied verbatim from p0/qc_engine/
│   ├── money.py                         # copied verbatim
│   ├── model.py                         # copied verbatim
│   ├── reconcile.py                     # copied verbatim
│   ├── ruleset.py                       # copied verbatim
│   ├── catalog.py                       # copied verbatim
│   ├── engine.py                        # copied verbatim
│   ├── audit.py                         # copied verbatim
│   ├── mismo.py                         # copied verbatim (FR-005)
│   ├── field_catalog.json               # copied verbatim (FR-004)
│   ├── compiler/
│   │   ├── __init__.py                  # copied verbatim
│   │   └── import_gold_ruleset.py       # copied, ONE constant edited (FR-007: RUN_DIR)
│   └── adapters/
│       ├── __init__.py                  # copied verbatim (empty file)
│       └── touchless_adapter.py         # copied verbatim
└── fixtures/
    └── from_docs/
        ├── fixture_loader.py            # copied verbatim
        ├── verify_against_defects.py    # copied verbatim (FR-004)
        ├── defect_manifest.json         # copied verbatim
        ├── loan_01.json                 # copied verbatim
        ├── loan_02.json                 # copied verbatim (post pre-existing-drift revert)
        ├── loan_03.json                 # copied verbatim (post pre-existing-drift revert)
        ├── loan_04.json                 # copied verbatim
        └── loan_05.json                 # copied verbatim (post pre-existing-drift revert)

p0/                                      # UNCHANGED (FR-008) — remains the experimental/
                                          # historical workspace; every file above has an
                                          # untouched original still living here
```

**Structure Decision**: Single-project layout (Option 1 from the template, without the `src/`/
`tests/` split, since it mirrors `p0/`'s own existing convention exactly — `qc_engine/` as the
library, `fixtures/from_docs/` as the test/validation data, no separate `tests/` directory
because `verify_against_defects.py` *is* the test). `engine/` sits as a sibling of `p0/` at the
repo root, at the same directory depth `p0/` occupies, which is what makes the `_REPO_ROOT`-
relative path logic in `import_gold_ruleset.py`/`fixture_loader.py` continue to work unmodified
(see spec.md FR-002 and the Edge Cases section).

### Why each exclusion is safe (traced, not assumed)

| Excluded | Why |
|---|---|
| `apply_loan_profile.py`, `build_loan_profiles*.py` (v2–v5), `eval_log.py`, `replay.py`, `yaml_executor.py` | `qc_engine/__init__.py` does not import any of these; confirmed by reading its own import list. Belong to the superseded ontology-extraction pipeline (spec 002f/002g). |
| ~25 other `compiler/*.py` files (`compile_llm.py`, `knowledge_base*.py`, `fact_vocabulary.py`, `judge_panel.py`, `decision_narrative.py`, `program_gating.py`, `document_presence_gating.py`, etc.) | `import_gold_ruleset.py` imports exactly `from qc_engine.ruleset import Check, Ruleset` — nothing else from `compiler/`. These belong to the AMQ-workbook-direct compiler CLAUDE.md documents as what `main` currently has (the *older* pipeline, not this one). |
| `p0/compile_runs/run_016_coverage_gate/build_and_run.py` (the *other* CLAUDE.md standing gate) | Imports `ontology_extraction`, `qc_engine.build_loan_profiles_v3`, `qc_engine.compiler.fact_vocabulary`, `qc_engine.eval_log` — pulling it in would drag the entire superseded pipeline back in. Stays running against `p0/` only (FR-006). |
| `doc_patterns/`, `extract_pdf.py`, `extract_xml.py`, `build_fixtures.py` | One-time fixture-*generation* tooling; `verify_against_defects.py` only needs the already-built `loan_*.json` files + `fixture_loader.py` + `defect_manifest.json`, confirmed by its own import list. |
| `p0/ontology_extraction/`, `p0/eval_synth/`, `p0/eval_real/`, `p0/experiment_*/`, 20 dated `p0/compile_runs/run_NNN_*/` | Unrelated experiment/history directories, zero imports from the traced runtime path. |
| `p0/README.md`, `harness.py`, `prove.py`, `run_demo.py`, `export_qc_results_xlsx.py` | Describe/exercise an earlier, smaller synthetic-only P0 shape (single `test_p0.py`, `fixtures/golden.py`) that predates the gold-ruleset work — copying verbatim would mislead readers of "the definitive official engine." Replaced by the new, accurate `engine/README.md` (FR-009). |

## Complexity Tracking

*(Empty — Constitution Check passed with no violations to justify.)*
