# 001 — SHACL-as-engine experiment sandbox in src/

**Status:** Accepted 2026-07-29 (Gordon)

## Decision
Try the SHACL/semantic-validation approach as a QC engine inside `src/`, which is
gitignored (`.gitignore:8`) and treated as a low-risk sandbox. For work inside `src/`,
the project-level "no OWL/RDF reasoner in the runtime path" decision (FIBO adoption
decision, spec 015) is deliberately set aside.

## Context
Gordon judged that prior decisions/work had not produced the results he wanted and
explicitly chose to test the SHACL approach empirically rather than re-litigate the
documented boundary. This matches the project's empirical culture (G3 bake-off).

## Constraints that still hold
- `p0/`, the compiled ruleset, and the standing gates remain governed by CLAUDE.md.
- Determinism is still required: same loan → same result, every run (verified by
  double-run comparison in the pilot runner).
- Rule-fidelity discipline still applies: any threshold not traceable to a source
  (AMQ row or the loan documents themselves) is marked `SME-PLACEHOLDER-UNSPECIFIED`.
- If the experiment graduates out of `src/`, a real ADR reversing/scoping the FIBO
  boundary decision must be written first.

## Evidence
- `src/shacl_pilot/` — the sandboxed pilot implementation this decision authorized (extractor, shapes, runners, compiled artifacts).
- `src/shacl_pilot/run_shacl_audit.py` — v1 runner: double-run determinism check on independently constructed graphs, per the constraint above.
- `src/shacl_pilot/run_audit.py` — v3 runner: SHACL validation runs twice per loan; run output stamps ruleset sha + shapes version.
- `src/shacl_pilot/blocks/property_appraisal.ttl` (line 16) and `blocks/closing.ttl` (line 16) — untraceable thresholds explicitly marked `SME-PLACEHOLDER-*`, per the rule-fidelity constraint.
- `p0/` untouched by the pilot — no pilot script imports from or writes to it (v3 removed even read-only p0 fixture use; see decision 011).
