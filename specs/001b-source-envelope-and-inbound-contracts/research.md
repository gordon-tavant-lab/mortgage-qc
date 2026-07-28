# Research: Source Envelope and Inbound Contracts

## Unknowns resolved

### 1. The generalized envelope shape: a named dict, priority-ordered fallback

**Decision**: `{truth: <value>, sources: {name: <value>}}`, exactly as the roadmap specifies — a
plain string-keyed map, not a more elaborate structure. Backward-compatible system-value resolution
(today's `los`-else-`mismo` fallback in `SourceValue.system_value()`) becomes a priority-ordered
lookup over `sources` keys, with a default priority list `["los", "mismo"]` that a catalog entry
(001a) may override per field once a real second/third system source exists.

**Rationale**: The roadmap's own target shape (`output/ROADMAP.md` §001b) already specifies
`{truth, sources{}}` — there is no genuine ambiguity to resolve on the container shape itself. The
one real design choice is how `system_value()`'s existing fallback *order* generalizes: a fixed
default priority list preserves today's exact behavior (SC-001, SC-005) while remaining data-driven
(a new source can be inserted into the priority list via catalog metadata, not code, per FR-004).

**Alternatives considered**: A more structured per-source object (e.g. `{name, value, priority,
timestamp}`) instead of a plain map — rejected as premature structure for this feature; `001a`'s
catalog already carries `expected_sources` metadata, and duplicating priority/ordering concerns into
the envelope itself would create two places that could disagree. Keep the envelope simple; let the
catalog own source metadata.

### 2. The source-independence guard is a test-construction discipline, not a runtime data check

**Decision**: FR-005's "reject any configuration where a reconcile check's comparison value is
derived from the same origin as its truth value" is enforced as a **test-fixture-construction
convention** (a reusable assertion helper that test/synthetic loan builders must use), not as a
runtime check on production data.

**Rationale**: External research (web search, 2026-06-30) on data-provenance/independent-source
validation confirms the standard pattern is provenance *metadata* attached at construction time
(timestamped source logs, explicit lineage tags) — there is no way to detect "derived from the same
origin" by inspecting two already-populated values alone; by the time a doc value and a system value
exist as data, they're just data. The real risk this guard exists to catch is exactly the one
CLAUDE.md #3 already names: **test/synthetic data** where a lazy fixture builder derives the
"system" value directly from the "doc" value (making the comparison trivially, uselessly pass).
**Real production data does not have this problem** — Touchless extraction and the LOS export are
genuinely different upstream systems; independence is structural, not something that needs runtime
verification on live data. So the guard belongs where the risk actually lives: as a construction-time
discipline for test fixtures (mirroring `p0/eval_synth/generator.py`'s existing practice of building
`doc` and `los`/`mismo` values from *separate* random draws), not as a new runtime validator that
would have nothing meaningful to check against real inbound data.

**Alternatives considered**: A runtime "same-value" heuristic (flag if `truth == sources['los']`
exactly) — rejected: a genuinely independent doc and system value legitimately agreeing (the common,
correct case — most fields match!) would trigger constant false positives; equality is not evidence
of derivation, and the two are supposed to agree most of the time. The risk is in *how test data is
built*, not in what a comparison of already-built values shows.

**Empirical corroboration, added 2026-07-01** (`output/PRIOR-ART-OLAV-MORTGAGE-QC.md`): a prior-art
audit of `examples/mortgage-qc/` — Olav's real, deployed runtime-LLM mortgage QC system — found this
exact failure mode occurred in production, independently of this project. Its mock system services
(appraisal, credit, etc.) returned data conflicting with the actual extracted PDF (issue
`013-appraisal-false-positives-human-review.md`: mock GLA = 2,400 sf vs. extracted PDF = 3,639 sf).
The LLM correctly flagged the mismatch, but the mismatch was an artifact of badly-independent test/mock
data, not a real defect. The team tried fixing it with prompt engineering and it failed — LLM
non-determinism meant the same loan produced different findings across runs; the fix had to be
structural (seed mocks from extraction data so the conflict can't arise). This is independent, real-
world confirmation of this decision's core claim: **prompting cannot substitute for a construction-time
guarantee, and the risk genuinely lives in how test/mock data is built, not in runtime data itself.**

Sources:
- [Data Provenance: Importance, Challenges and 8 Best Practices](https://www.astera.com/type/blog/data-provenance)
- [Security Approaches for Data Provenance in the Internet of Things: A Systematic Literature Review](https://arxiv.org/pdf/2407.03466)

### 3. Inbound contracts are pinned as consumed-interface schemas, reusing 001a's catalog vocabulary

**Decision**: The Touchless inbound contract and the LOS/MISMO inbound contract are each documented
as a schema (per `contracts/`) mapping onto `001a`'s `FieldCatalogEntry` vocabulary — not
independently invented field lists.

**Rationale**: `001a` already declares, per field, which sources are expected and what
citation/confidence requirements apply. Re-describing that from scratch in the inbound contracts
would create two sources of truth that could drift. The inbound contracts describe *what an upstream
system must supply*; the catalog describes *what the engine expects to receive* — the same
vocabulary, described from two directions.

## Technical context (no NEEDS CLARIFICATION remaining)

- **Language/Version**: Python 3.9-compatible (project-wide constraint).
- **Primary Dependencies**: None new.
- **Storage**: No new storage — this is a data-model generalization inside the existing
  `qc_engine` package; inbound contracts are documentation (`contracts/`), not a new integration.
- **Testing**: Extends `p0/tests/test_p0.py` — zero-regression against the P0 golden set is the
  primary gate (SC-001); a new test-fixture helper enforces independent construction for reconcile
  test cases (decision #2).
- **Target Platform**: Same as all of `p0/` — no service, no network call introduced.
- **Project Type**: Library extension to `qc_engine`, depends on `001a`.
- **Performance Goals**: N/A.
- **Constraints**: Zero regression against the P0 golden set; `truth` always represents the
  document/closing-file side (Principle V) — never a system-derived value.
- **Scale/Scope**: The `sources` map must accept a new named source via configuration only (FR-004)
  — this feature does not build multi-LOS reconciliation logic itself (that's the demoted v3
  interface, roadmap feature 013).
