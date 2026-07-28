# Implementation Plan: Canonical Loan-Fact Vocabulary + Compile-Time Precondition Wiring

**Spec**: `spec.md` (this directory) · **Created**: 2026-07-26 · **Python 3.9 compatible**

## Load-bearing discovery that shapes this plan (verified against real data, 2026-07-26)

The real gift rows are **Layer 0 rows**: `pc-retail-00099`/`00146`/`00161` (and 38 more mentioning
gift) all carry `question_criteria_by_q` referencing **QuestionID 570606** — the AMQ's own "which
asset types does this loan use?" question, whose full decoded answer vocabulary (17 answers,
`"Yes - Gift"`, `"Yes - Grant"`, `"Yes - Checking/Savings"`, ... 362 dependent rows) Layer 0
reconstructs deterministically. Consequence: **SC-001's entire path runs on real data with zero LLM
calls.** Phase 1 wiring adds no new LLM behavior anywhere — the vocabulary is a pure, signed,
deterministic bridge from Layer 0's opaque `question_570606` proposals onto real catalog fields.
Layer 1/2 proposals (LLM-sourced, `MEDIUM`/`MANDATORY` trust tiers) are **never auto-attached** in
Phase 1 — they surface as review-flagged drafts, honoring 002f's trust-tier discipline.

## Design

### 1. `p0/qc_engine/compiler/fact_vocabulary.py` (new)

- `QuestionBinding`: `{question_key, answers: [str], canonical_value: str}` — maps a Layer-0
  `(question, answer)` pair onto a canonical field value. The gift binding:
  `{question_key: "570606", answers: ["Yes - Gift"], canonical_value: "true"}`.
- `CanonicalFact`: `{id, canonical_field_name, data_type, description, name_synonyms: [str],
  question_bindings: [QuestionBinding], mismo_ldd_reference: Optional[str],
  source_citations: [str], guide_citations: [str]}`.
- `FactVocabulary`: `{version, facts, signed_by, signed_at}` — mirrors `KnowledgeBaseCorpus`'s
  sign-off shape. `knowledge_base.sign()` is refactored to `dataclasses.replace()` (same semantics,
  now generic) so vocabulary sign-off **reuses** `KB.sign`/`KB.is_usable` — no second sign-off
  implementation (spec Key Entities).
- `resolve_layer0(vocab, proposal) -> Resolution`: unsigned vocab → `VocabularyNotSignedError`
  (US3, mirroring `CorpusNotSignedError`). All proposal answers map through one fact's bindings →
  resolved condition on the canonical field (`==` single value; `in` with `|`-joined values —
  engine.py:109's exact encoding). Any unmapped answer / answers spanning multiple facts →
  `unresolved` with a reason (never guessed, FR-002).
- `resolve_field_name(vocab, name) -> Resolution`: exact `canonical_field_name` → resolved;
  `name_synonyms` hit → resolved to canonical; else `novel_candidate` (surfaced, never auto-added).
- `attach_guide_citations(vocab, corpus, top_n)`: the concept-index decision (spec Assumptions) —
  per fact, `KB.retrieve()` over the signed Selling Guide corpus; stores **citation strings only**
  (pointers to verbatim sections). Never content. Unsigned corpus → the existing
  `CorpusNotSignedError` propagates.
- `save`/`load` at `storage/fact_vocabulary/v<N>.json` (central-storage convention, one file per
  version, never overwritten — 002c's precedent).

### 2. Compile wiring (`compile_llm.py`)

- `CompiledCheckDraft` gains `applies_if_provenance: Optional[str]` and
  `applies_if_review: Optional[str]` (the `operator_consistency_flag` precedent — draft-level
  metadata, not `Check` schema, so **no digest impact**; `Check.applies_if` already exists since
  002e).
- New `attach_preconditions(drafts, rows, vocabulary, layer1_client=None, ...) ->
  PreconditionAttachReport`: runs `ontology_extraction.pipeline.run_layers()` once over the batch
  (Layer-0-only by default — zero cost), then per draft: HIGH-tier resolved → sets
  `draft.check.applies_if` + provenance; HIGH-tier unresolved → `applies_if_review` set, no
  `applies_if` (a check gates on a vocabularied fact or not at all); MEDIUM/MANDATORY tier →
  `applies_if_review` set regardless of resolvability (human path). Report carries honest counts:
  rows attempted / proposals by layer / attached / flagged / novel candidates (SC-004, mirroring
  002f FR-012).
- Deliberately **not** wired inside `compile_batch()` — callers invoke it explicitly after
  compilation, keeping 002b's compile step untouched and the wiring auditable as its own step.

### 3. Catalog + fixtures

- `field_catalog.json` += `gift_funds_used` (boolean, `expected_sources: ["doc"]`), description
  grounded in the real AMQ question 570606 rows (taxonomy-grounding test gate compliance —
  rule-grounded style, not "Comprehensive-coverage field"). Referential integrity then accepts
  `applies_if` on it (catalog.py's existing 002e extension).

### 4. `p0/qc_engine/replay.py` (new — FR-008, Sanctioned's golden-persona pattern)

`replay(loans, old_ruleset, new_ruleset) -> ReplayReport`: runs the engine over the fixed panel
under both rulesets, reports every `(loan_id, check_id)` whose status flips, plus summary counts.
Pure function over `engine.run()` — no LLM, no network.

### 5. Seed artifact (`build_seed_fact_vocabulary.py`, new)

Deterministically derives the gift binding from the real Retail rows (re-clusters, extracts
570606's real answer vocabulary, binds only `"Yes - Gift"` → `gift_funds_used=true`), writes
`storage/fact_vocabulary/v1.json` signed `NOT-A-REAL-SME-pending-kayla-review` (the KB corpus's
exact honest-placeholder precedent) and prints the Layer-0 full-sheet coverage report (FR-007's
bounded default: full Layer 0 is free; any Layer 1/2 spend stays a separate explicit decision).

## Constitution Check

*GATE: evaluated against `.specify/memory/constitution.md` v1.1.1. Added 2026-07-27,
constitution-alignment audit — every sibling spec in the `002` family (002c/002d/002e/002f) has this
section; this plan.md was missing it, a process gap, not a substantive one (the spec.md itself already
argues each principle correctly in prose).*

| Principle | Status | Note |
|---|---|---|
| I — Determinism of the correct computation | ✅ PASS | Resolution against `FactVocabulary` is a pure lookup — zero LLM at the compile-decision point beyond what `002f`'s `run_layers()` already runs. |
| II — Compile, then run | ✅ PASS | Wiring happens entirely at compile time (`compile_llm.py`); no runtime model call is introduced. |
| III — Eval is foundational | ✅ PASS | SC-001 through SC-004 are measured against the real Retail sheet's known gift-funds row(s), not assumed. |
| IV — Build the core, assume the periphery | ✅ PASS | Compiler-spine infrastructure; no new UI surface (reuses `002c`'s existing SME-review-queue shape). |
| V — Source independence | N/A | Not touched — this feature resolves fact names, it doesn't compare doc-vs-system values. |
| VI — Configurable by non-technical users | N/A | No Author/Output surface added; canonical-fact sign-off reuses the existing SME-exception-queue mechanism unchanged. |
| VII — Configuration is authored data | ✅ PASS | `FactVocabulary`/`CanonicalFact` is signed, versioned, and hashed exactly like the field catalog and KB corpus — one more instance of the same four-layer model, not a new mechanic. |

**No unjustified violations. Complexity Tracking: one new package (`fact_vocabulary.py`), reusing `002c`'s sign()/is_usable() functions directly rather than re-implementing sign-off logic.**

## What this plan deliberately does not do

- No prompt/SYSTEM_PROMPT changes; no new LLM calls in any test or default path (FR-009).
- No auto-attach for Layer 1/2 proposals (trust tiers).
- No `Check`/`Ruleset` schema change → no digest re-baseline expected (verified at the end by the
  harness + pinned digest tests).
- No full-sheet Layer 1/2 run; no jumbo/QM facts; no `010a` changes (spec Out of Scope).

## Test plan

- `test_fact_vocabulary.py`: sign-gating raises; exact/synonym/novel name resolution; Layer-0
  binding resolution happy path + unmapped-answer refusal; save/load roundtrip; guide-citation
  attachment (tiny signed corpus) + unsigned-corpus refusal.
- `test_compile_precondition_wiring.py`: real gift rows through real Layer 0 → attached
  `applies_if` on `gift_funds_used`; SC-001 end-to-end (real loan 01 fixture → `NOT_APPLICABLE`);
  FR-005 two-checks-same-field identical evaluation; unmapped answer → flagged, no `applies_if`;
  MEDIUM-tier proposal → flagged, never auto-attached.
- `test_replay_panel.py`: 5 real from_docs loans, ruleset with vs. without the gift `applies_if` →
  report names exactly the expected flips.
- Full suite + `p0/harness.py` green, digests unchanged (SC-003).
