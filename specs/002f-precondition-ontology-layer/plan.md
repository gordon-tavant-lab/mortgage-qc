# Implementation Plan: Precondition Ontology Layer (modular, reusable)

**Branch**: `002f-precondition-ontology-layer` | **Date**: 2026-07-24 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/002f-precondition-ontology-layer/spec.md`

## Summary

A new, standalone package (`p0/ontology_extraction/`) implementing the three-layer precondition-
sourcing sequence found and validated this session: Layer 0 (deterministic cross-reference-column
clustering — zero LLM), Layer 1 (source-text extraction with explicit deontic-modality + cross-
reference-target classification, extending `compile_llm.py`'s existing never-invent discipline),
Layer 2 (KB-retrieval + automated grounding-verification + mandatory-human-review, reusing `002c`'s
already-implemented `knowledge_base.py`/`judge_panel.py` rather than re-building grounding/judging
infrastructure). The package has zero dependency on mortgage-qc-specific types — `002e` is the sole
consumer that translates its output into `Check.applies_if`.

Two additional mechanisms adopted from `project/Onity`'s independently-built, real "Ontology Graph
Mapping" pipeline (a different problem, same architecture shape — see spec.md's cited prior art):
a bounded-retry-then-explicit-abstain pattern for any Layer 1/2 LLM call (FR-011), and a
coverage-based circuit breaker on Layer 0 (FR-012) — the concrete mechanism that makes this package
safely reusable against a rule source this project has never seen, not just structurally decoupled
from `qc_engine` by import discipline alone.

This is explicitly a capability-extraction spec, not a UI or workflow spec: the deliverable is a
Python package with a clean, tested, documented interface, proven against this project's own real
data (the Retail AMQ workbook), and structured so another project could depend on it directly.

## Technical Context

**Language/Version**: Python 3.9-compatible (project-wide constraint).
**Primary Dependencies**: None new for Layer 0/1 (stdlib `re`/`json` + the existing Bedrock harness
pattern `compile_llm.py` already uses for Layer 1's LLM call). Layer 2 imports `002c`'s
`knowledge_base.py`/`judge_panel.py` directly — no new grounding/judging code.
**Storage**: Layer 0's ontology output is a plain JSON-serializable structure — callers decide
where/whether to persist it (mortgage-qc-prod's own compile-run scripts already have this pattern).
No new storage mechanism owned by this package itself.
**Testing**: New `p0/tests/test_ontology_extraction.py` (Layer 0 clustering — deterministic, no
mocks needed, run directly against a fixture derived from the real Retail workbook's structure;
Layer 1's extraction logic tested the same way `compile_llm.py`'s existing tests are — synthetic
fixtures for structure, a separate real-Bedrock-call script for the live path) plus
`p0/tests/test_ontology_reusability.py` (the static import-check enforcing spec FR-009/SC-005 — a
simple `ast`-based scan or import-time check confirming zero `qc_engine.*` imports in
`p0/ontology_extraction/`).
**Target Platform**: Local execution; Layer 1/2's live paths call Bedrock, same precedent as every
other LLM-calling module in this project (kept outside the fast pytest suite).
**Project Type**: New standalone package + one integration point in `002e`'s consumption of it.
**Performance Goals**: Layer 0 is O(rows) clustering, negligible cost. Layer 1/2 costs scale with
however many rows reach each layer — by design, Layer 0's coverage (measured, SC-002) determines how
much of the more expensive Layer 1/2 work is actually needed; this is the point of the sequencing.
**Constraints**: Zero imports from `p0/qc_engine/` inside `p0/ontology_extraction/` (FR-009) — with FR-010's one sanctioned exception: `layer2_grounded.py` imports `002c`'s `knowledge_base`/`judge_panel`, statically enforced in exactly that shape by `test_ontology_reusability.py` *(precision note added 2026-07-26, spec audit)*. Layer 2
MUST NOT re-implement KB storage/retrieval/judging — reuse `002c`'s modules directly (FR-010).
**Scale/Scope**: Proven against the real Retail Post-Closing sheet (5,520 rows, 24 decoded ontology
entries, 3,255 rows resolved by Layer 0 alone). Full end-to-end recompile of the entire workbook
through all three layers is Phase 2 (a separate, larger, real-Bedrock-cost decision), mirroring
`003d`'s and `002e`'s own Phase 1/Phase 2 precedent — this spec's Phase 1 proves the mechanism.

## Constitution Check

*GATE: evaluated against `.specify/memory/constitution.md` v1.1.1.*

| Principle | Status | Note |
|---|---|---|
| I — Determinism of the correct computation | ✅ PASS | Layer 0 is a pure function, no LLM. Layer 1/2's LLM calls happen at compile time only (Principle II); the engine that ultimately evaluates `applies_if` (via `002e`) is unchanged, deterministic. |
| II — Compile, then run | ✅ PASS | All three layers run at compile time; nothing here introduces a runtime model call. Layer 2's KB retrieval is the same frozen-corpus pattern `002c` already established, not live search. |
| III — Eval is foundational | ✅ PASS | SC-001-003 make Layer 0's real coverage and Layer 2's grounding-verification behavior explicit, measured gates. |
| IV — Build the core, assume the periphery | ✅ PASS | This is compiler-spine infrastructure, core to the audit/determinism story, not an extraction/LOS concern. |
| V — Source independence | N/A | Not touched. |
| VII — Configuration is authored data | ✅ PASS | The decoded ontology and precondition proposals are data artifacts a human ultimately signs off on (via `002e`/`002c`'s existing sign-off mechanisms), not new runtime logic. |

**No unjustified violations. Complexity Tracking is empty.**

## Project Structure

### Documentation (this feature)

```text
specs/002f-precondition-ontology-layer/
├── spec.md
├── plan.md                  # This file
├── tasks.md
└── criteria.md
```

### Source Code (repository root)

```text
p0/ontology_extraction/                 # NEW standalone package — zero qc_engine imports
├── __init__.py
├── layer0_clustering.py                # Dependency-key clustering — pure, deterministic
├── layer1_extraction.py                # Deontic-modality + cross-ref-target classification,
│                                        # then precondition extraction from row text (LLM, compile-
│                                        # time only)
├── layer2_grounded.py                  # KB retrieval (via 002c's knowledge_base.retrieve) +
│                                        # automated grounding-verification + judge-panel wiring
│                                        # (via 002c's judge_panel.escalate_or_approve, overridden to
│                                        # never auto-approve for this use case)
└── pipeline.py                         # run_layers(rows, kb, ...) -> List[PreconditionProposal],
                                         # sequencing 0 -> 1 -> 2 per FR-008

p0/qc_engine/compiler/                  # UNCHANGED, imported by layer2_grounded.py
├── knowledge_base.py                   # existing, implemented (002c)
└── judge_panel.py                      # existing, implemented (002c)

p0/tests/
├── test_ontology_extraction.py         # NEW — Layer 0/1/2 behavior
└── test_ontology_reusability.py        # NEW — the zero-qc_engine-imports static check
```

## Complexity Tracking

*(empty — no constitution violations to justify)*
