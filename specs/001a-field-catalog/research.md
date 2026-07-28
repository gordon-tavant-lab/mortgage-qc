# Research: Field Catalog

## Unknowns resolved

### 1. Authored-data serialization format: JSON, not YAML

**Decision**: The field catalog is authored and stored as JSON, matching every other authored/
canonical artifact already in this codebase (`p0/eval_synth/taxonomy.json`, the ruleset's
`canonical_content()` in `p0/qc_engine/ruleset.py`, all `eval_synth/artifacts/*.json` outputs).

**Rationale**: External research (web search, 2026-06-30) surfaced a real risk with plain YAML for
this use case: YAML's implicit type coercion (the "Norway problem" — e.g. a two-letter state code
like `"NO"` silently parsing as boolean `false`) is exactly the kind of silent data corruption this
project's SAFE-gate philosophy exists to prevent, and mortgage data is full of ambiguous short
strings (state codes, loan-purpose codes) that could trigger it. `StrictYAML` and JSON-Schema-backed
YAML validators exist to mitigate this, but they add a dependency and a parsing layer this codebase
doesn't otherwise need — every other authored artifact here is already JSON, hashed via
`json.dumps(..., sort_keys=True, separators=(",", ":"))`. Reusing that exact pattern (FR-006) is
simpler and safer than introducing a second serialization format and a new type-coercion risk for a
one-time human-readability gain that matters more once an authoring UI (roadmap `009`) exists to
mediate the editing experience — which is explicitly out of scope for `001a`.

**Alternatives considered**:
- YAML with `StrictYAML` (avoids the Norway problem, still human-friendly) — rejected for now:
  adds a new dependency and parsing path for a benefit (raw-file readability) that matters most once
  a human is hand-editing the raw file directly, which `001a`'s own assumption says is a temporary
  state until `009` ships. Worth revisiting if `009a`'s import surface ends up wanting a YAML
  intermediate — tracked as a note, not a decision reversal here.

Sources:
- [Schema Validation for YAML | JSON Schema Everywhere](https://json-schema-everywhere.github.io/yaml)
- [Validate YAML in Python with Schema](https://www.andrewvillazon.com/validate-yaml-python-schema/)

### 2. Referential-integrity validation: load-time, fail-fast — not a runtime-per-check guard

**Decision**: Referential integrity (every check's `field_name` resolves to a catalog entry) is
validated once, when a `Ruleset` + `FieldCatalog` pair is loaded together — before any loan is
scored — not re-checked inside the per-loan, per-check execution path (`qc_engine/engine.py`'s
`_eval_check`).

**Rationale**: This mirrors both the existing pattern in this codebase (`p0/harness.py` validates
sign-off integrity and computes the ruleset hash once, before the 1000-run determinism loop, not
per-run) and general schema-validation best practice (validate at the boundary, fail fast, don't pay
a validation cost — or risk a silently-skipped check — on every single evaluation). A field
reference that doesn't resolve is a build-time/load-time defect in the ruleset+catalog pairing, not
a per-loan runtime condition; catching it once, loudly, before any loan is scored is both cheaper
and safer than hoping every execution path remembers to re-check it.

**Alternatives considered**:
- Runtime check inside `_eval_check` (raise if `field_name` not in catalog, every single
  evaluation) — rejected: this is exactly the shape of defense-in-depth that sounds safer but
  actually risks becoming a silently-swallowed exception deep in a per-check loop, running 3,000+
  times per eval run for no additional safety once load-time validation already guarantees every
  check in a validated ruleset resolves. Load-time validation is the single point of truth; runtime
  re-validation would be redundant, not defense-in-depth.

## Technical context (no NEEDS CLARIFICATION remaining)

- **Language/Version**: Python 3.9-compatible (project-wide constraint).
- **Primary Dependencies**: None new — reuses stdlib `json` + `hashlib`, exactly as
  `p0/qc_engine/ruleset.py` already does for the signed ruleset artifact.
- **Storage**: A single JSON file (the field catalog), co-located with the engine code, mirroring
  `p0/eval_synth/taxonomy.json`'s code-and-data-together convention.
- **Testing**: Extends the existing `p0/tests/test_p0.py` suite (new tests for referential-integrity
  validation, catalog hashing, and zero-regression against the P0 golden set) — no new test
  framework introduced.
- **Target Platform**: Same as all of `p0/` — local execution, no service.
- **Project Type**: Library extension to the existing `qc_engine` package — a new module, not a new
  service or project.
- **Performance Goals**: N/A — catalog validation happens once at load time, not per-loan; no
  latency-sensitive path is introduced.
- **Constraints**: Zero regression against the P0 golden set (SC-002); the per-field envelope shape
  (`value, source_origin, citation, confidence`) must stay stable even as the field set grows
  (Principle VII).
- **Scale/Scope**: The catalog schema must be able to represent the field vocabulary implied by all
  4,192 classified conditions in `taxonomy.json` (SC-004) without further schema changes — this
  spec does not require authoring all 4,192 entries, only proving the schema scales to them.
