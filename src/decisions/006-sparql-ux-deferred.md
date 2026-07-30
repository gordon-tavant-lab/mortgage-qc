# 006 — SME-friendly route/block/check editing UX is deferred

**Status:** Accepted 2026-07-29 (Gordon) — "we will work on a user friendly way for
users to edit route/block/check … later (lets prove this first)".

## Decision
The pilot proves the engine (accuracy, determinism, citations, versioning) first.
SPARQL-in-shapes is acknowledged as code — the eventual SME surface will be a
structured editor (or compiler from workbook rows) that *generates* these shapes, at
which point the shapes file becomes a compile target exactly like the p0 ruleset JSON.
Until then, shape authoring is developer work inside the sandbox.

## Non-goal reminder
Do not evaluate the pilot on authorability yet; evaluate it on
detection accuracy (loan 01 gauge + loans 02–05), determinism, and citation fidelity.

## Evidence
- `src/shacl_pilot/blocks/*.ttl` — shapes remain hand-authored SPARQL-in-SHACL (developer work); no editor UI exists in `src/`.
- `src/shacl_pilot/amq_compiler.py` — the Layer-1 compiler that makes shapes a compile target (the path this decision anticipated), with Layer 2 (decision 009) as the eventual SME-facing generation step.
- `src/shacl_pilot/shape_manifest.py` — the versioning/sign-off loop the future editor plugs into (decision 004 workflow step 1 references this decision).
