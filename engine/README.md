# QC Audit Engine

The definitive, standalone Mortgage QA/QC audit engine — a deterministic evaluator that
compiles a signed gold ruleset and runs it against a loan, producing an auditable verdict for
every check. Zero third-party dependencies (Python 3.9-compatible stdlib only).

This is a **copy** of the pipeline proven out and validated across the `resolve6`/`resolve7`/
`resolve8` passes in `p0/` — `p0/` remains the experimental/historical workspace where that work
happened; this folder is the clean, minimal artifact meant to be the official engine going
forward. It does not depend on anything else in `p0/`.

## Run it

Two inputs, three commands, from the repo root:

```bash
# 1. Adapt a real Touchless loan payload into the engine's canonical fixture format
python3 engine/qc_engine/adapters/touchless_adapter.py \
    <loan_application.json> <extracted_data.json> <fixture_out.json>

# 2. Compile the gold ruleset and evaluate it against that fixture
python3 engine/qc_engine/compiler/import_gold_ruleset.py --loan-fixture <fixture_out.json>

# 3. Standing gate: verify the engine against 25 known, labeled defects
python3 engine/fixtures/from_docs/verify_against_defects.py
```

Step 2 writes its output (`p0_results.json`, `gold_to_check_mapping.json`, and the fixture copy)
under `engine/compile_runs/default/` by default — override with `--mapping-out` /
`--results-out` / `--loan-fixture` if needed.

## Where the ruleset comes from

The compiled gold ruleset (`storage/rules/gold/data/rules_compiled.json` and its companion
sidecar files — `demo_exclusions.json`, `autopass_no_system_access.json`,
`scenario_applicability_loan12607601215.json`, `doc_decidability_classification.json`) lives
outside this folder, in the repo's shared `storage/` tree, and is read by relative path — it is
**not** duplicated here. `engine/`'s directory depth deliberately mirrors `p0/`'s exactly
(`engine/qc_engine/compiler/import_gold_ruleset.py`) so the existing path-resolution logic in
that file finds the shared ruleset data with zero code changes.

## What's in here

```
qc_engine/
  money.py, model.py, reconcile.py, ruleset.py, catalog.py, engine.py, audit.py, mismo.py
                        the core deterministic evaluator (Decimal math, canonical loan model,
                        check/ruleset dataclasses, field catalog, hash-chained audit log,
                        MISMO 3.4 XML parser)
  field_catalog.json    the field vocabulary the catalog module validates against
  compiler/
    import_gold_ruleset.py   compiles storage/rules/gold/data/rules_compiled.json into
                              runnable Check/Ruleset objects and evaluates them
  adapters/
    touchless_adapter.py     converts a raw Touchless loan payload into the engine's
                              canonical fixture format
fixtures/from_docs/
  fixture_loader.py, verify_against_defects.py, defect_manifest.json, loan_01.json..loan_05.json
                        the standing-gate harness: 5 labeled synthetic loans with 25 known,
                        seeded defects, used to prove the engine's own correctness
```

## What's deliberately not here

This engine carries only what the currently-exercised runtime path actually imports — traced by
reading each file's own `import` statements, not copied by directory. Left behind in `p0/`, on
purpose: the earlier AMQ-workbook-direct compiler (`compile_llm.py` and ~25 related files), the
ontology-extraction pipeline (`build_loan_profiles*.py`, `fact_vocabulary.py`, and friends), the
Field & Precondition Coverage Gate (entangled with that older pipeline), and ~20 experiment/eval
directories that were exploratory dead ends or one-off bake-off runs, not part of the pipeline
itself. See `specs/023-standalone-qc-engine/plan.md` for the full file-by-file rationale.
