# Phase 0 Research: Ruleset Compiler Pipeline

**Feature**: `002b-ruleset-compiler-pipeline` | **Date**: 2026-07-02

Four decisions were open at spec time (spec.md's Edge Cases + Assumptions explicitly deferred them
to this planning phase). Each is resolved below with external evidence, per the project's research
discipline ("never make an architecture decision without external research").

---

## Decision 1 — Batch compile strategy: chunked map-reduce, not single-pass or recursive

**Question** (spec.md Edge Cases): "What happens when the batch is large enough that compiling it
in a single LLM context risks losing cross-row consistency? ... single-pass vs. chunked vs. a
hierarchical/recursive orchestration pattern for very large batches."

**Research** (Tavily, pro-depth synthesis across 23 sources, 2026-07-02): for production batch jobs
in the hundreds-of-rows range that must produce strict, schema-conforming records, three
architectures are viable — (A) single large-context pass, (B) chunked/map-reduce with a
canonicalizing reduce step, (C) recursive/hierarchical orchestration. The synthesis's own decision
checklist: *"If cost, parallelism, and robustness are primary and rows are mostly independent:
prefer chunked/map-reduce with a strong validator + merge step."* Recursive/hierarchical
orchestration is recommended specifically *"when records have hierarchical relationships that are
hard to capture per row"* — and even then, purely recursive passes "may produce unreasonable trees
and underperform level-wise pipelines unless carefully constrained."

**Decision: chunked map-reduce.**
- **Map**: each of the ~4,192 real workbook rows (roadmap `output/ROADMAP.md` §003a/b/c) is an
  independent policy/comparison assertion — not a parent/child hierarchical structure. The
  recursive-orchestration case for handling cross-row dependency (the reason an RLM-style approach
  was raised in an earlier discussion of this feature) doesn't apply here: rows don't reference each
  other's compiled output. Recursive orchestration's downside (more calls, more complexity) would be
  paid for no benefit.
- **Reduce**: FR-003's consistency report (duplicate-vocabulary detection across the batch) **is**
  the research-recommended "canonicalizing reduce step" — this spec already required exactly the
  component the evidence says a chunked design needs, it just hadn't been named as the reduce phase
  until now.
- Chunk size: bounded by the same per-call token budget already proven in
  `p0/experiment_002a/compile_llm.py` (`maxTokens=700` per row response, one row per call) — this
  spec keeps that proven one-row-per-call shape rather than batching multiple rows into a single
  prompt, since the research flags per-row independent calls plus a shared canonical instruction
  (the existing `SYSTEM_PROMPT`) as the validated pattern for cross-item consistency, and
  `compile_llm.py`'s harness already implements exactly that shape at n=24.
- This also directly answers the earlier open question about Recursive Language Models (RLM,
  MIT CSAIL) as a candidate orchestration pattern for this feature: RLM-style recursive
  decomposition is a solution to a *long-context* problem (a single task too large for one context
  window). This pipeline's rows are independent and already fit one-row-per-call; there is no long
  context to decompose. RLM is not the right tool for this batch shape — chunked map-reduce is.

## Decision 2 — Field catalog growth during compile: propose-then-sign, not pre-population or silent creation

**Question** (not explicit in spec.md, but load-bearing for FR-002): the `001a` field catalog
currently has 7 entries (`p0/qc_engine/field_catalog.json`); a production batch of dozens-to-hundreds
of real rows will reference field names far beyond those 7 (`compile_llm.py`'s own system prompt
already tells the LLM to invent a `field_name` "if no catalog exists yet"). If FR-002's rule
("unresolved reference blocks sign-off") is applied naively, nearly every drafted check in a real
batch would be blocked on day one — starving the feature of the very batch scale it exists to prove.

**Research** (Tavily search, schema-registry evolution patterns, 2026): the established pattern for
progressively growing a shared vocabulary under validation (Confluent/Avro schema registries) is
*"centralize validation and governance... establish ownership and approval processes for schema
modifications"* — new fields are **proposed**, validated for compatibility, and registered under
an approval step, never silently auto-created and never blocked pending an out-of-band manual
pre-population pass.

**Decision: the compiler proposes new `FieldCatalogEntry` drafts, not just `Check` drafts.** When a
drafted check's `field_name` doesn't resolve against `001a`'s catalog, the pipeline drafts a
candidate `FieldCatalogEntry` (inferring `data_type`/`expected_sources` from the source row context)
alongside the check, and routes *both* through the same authored → SME-corrected → signed workflow
(constitution Principle VII already establishes this is one model across all four authored layers —
the field catalog is one of those four layers, not a separate concern). This is additive to `001a`'s
existing `FieldCatalogEntry` dataclass (no schema change) and keeps the "unresolved reference blocks
sign-off" rule intact — a proposed-but-unsigned entry is, correctly, still unresolved until the SME
signs it, at which point it is added to the catalog and the checks that reference it become eligible.

## Decision 3 — Duplicate-vocabulary detection (FR-003): reuse the existing edit-distance helper, no new dependency

**Question**: FR-003 requires detecting when two drafted checks reference the same underlying
concept under different field names — needs some form of fuzzy string comparison across the batch's
candidate field names.

**Decision**: reuse `p0/qc_engine/ruleset.py`'s existing `_edit_distance` (Levenshtein) helper —
already proven (`RuleProvenance.__post_init__`, `test_signoff_tracks_edits`) — for fuzzy clustering
of candidate field names, rather than adding a new fuzzy-matching dependency. This keeps the
project's "no new dependencies" posture (this feature's Technical Context, below) intact and is a
second, independent use of a mechanism the codebase already trusts. A pair of candidate field names
below a small edit-distance threshold (or containing a shared/normalized token stem) is reported as
a possible duplicate — advisory (FR-003 doesn't gate sign-off; it reports a consistency risk), same
non-blocking posture as FR-006/007/008.

## Decision 4 — Per-check referential-integrity screening at batch scale: wrap, don't modify, the existing validator

**Question**: `001a`'s `validate_referential_integrity(ruleset, catalog)` (`p0/qc_engine/catalog.py`)
raises `ReferentialIntegrityError` on the *first* unresolved check in a `Ruleset` and stops — correct
for its proven use (`p0/harness.py`'s one-shot load-time SAFE gate on an already-signed ruleset), but
insufficient for this feature's User Story 3, which needs to know *which* of potentially dozens of
drafted checks in one batch are blocked, not just the first one.

**Decision**: do not modify `validate_referential_integrity` (spec.md explicitly requires reusing it
"unmodified" / "verbatim" — FR-002, User Story 3). Instead, the pipeline calls it once per candidate
check (constructing a throwaway single-check `Ruleset` per call) and collects the pass/fail result
per check into a batch-level report. This is a wrapping pattern, not a modification — the existing
function's contract (raise-on-first-error, for a whole signed ruleset at final load time) is
completely untouched and continues to run exactly as `001a`/`p0/harness.py` already prove; the
pipeline simply invokes it at a finer grain than its original caller does. Reusing a proven function
in a new calling pattern is not the same claim as reusing it in a new *shape* — this preserves the
"verbatim" commitment while meeting FR-002's per-check reporting need.

## Summary: Technical Context inputs this research resolves

| Open question | Resolution |
|---|---|
| Compile orchestration strategy | Chunked map-reduce; one-row-per-call (proven shape), FR-003's consistency report is the reduce step |
| RLM / recursive orchestration | Not applicable — rows are independent, not hierarchical; no long-context problem exists to decompose |
| Field catalog growth at batch scale | Propose-then-sign new `FieldCatalogEntry` drafts alongside `Check` drafts, same authored/signed workflow |
| Duplicate-vocabulary detection (FR-003) | Reuse `ruleset.py`'s existing `_edit_distance`; no new dependency |
| Per-check referential-integrity screening (FR-002/US3) | Wrap `validate_referential_integrity` per-candidate-check (unmodified), don't change its contract |
