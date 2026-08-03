# Implementation Plan: 021-touchless-audit-run

> **Addendum (live-demo-engine-wiring, 2026-08-02)**: this spec's implementation
> originally ran against `p0/qc_engine` (the pipeline this document describes below), ported
> into this repo from a disconnected worktree. It has since been **rewired to run against
> `engine/`** — the standalone, definitive QC audit engine extracted in `023-standalone-qc-engine`
> (see `engine/README.md`) — because `engine/` is the actively-maintained, more complete pipeline
> (broader field extraction, a fixed predicate-evaluation bug `p0/qc_engine` still carries). The
> design decisions and research below are still accurate in substance; every `p0/qc_engine`
> reference in this document describes the pipeline this feature *originally* targeted, not the
> one the live demo runs today. The live entry point is now
> `engine/qc_engine/run_touchless_audit_for_demo.py`, invoked from
> `backend/src/routes/audit.ts`, with the same input/output contract described here.

**Branch**: `021-touchless-audit-run` | **Date**: 2026-08-02 | **Spec**: `spec.md` (same directory)
**Input**: Feature specification from `specs/021-touchless-audit-run/spec.md`

## Summary

Given a loan already pulled from Touchless via `020`'s existing proxy, automatically compile the
gold ruleset (`019`) into a real `p0/qc_engine` (Pipeline B) ruleset, adapt the pulled loan into a
`CanonicalLoan`, run the actual deterministic engine, and derive a severity-tiered loan status
(`PASS`/`FAILED`/`NEEDS_REVIEW`, plus transient `RUNNING`/`ERROR`) — never fabricated. Also: expand
the Loan Queue to 20 loans (1 real, 19 cosmetic), split the Government route into FHA/VA/USDA with
simulated counts, wire "Restore to Gold" to also clear a fetched loan/verdict, and update
`InspectSources`/`ImportAndSignView` copy to real facts from the Touchless call.

**Technical approach** (from research.md): gold's 208 `COMPILABLE` checks resolve to only ~30
unique document-type fields; cross-referenced against the real demo loan's actual 62-document set,
only a subset (research.md Item 2 lists ~8) has a confident document-type mapping. The compiled
ruleset for this feature is scoped to that confidently-resolvable subset only — a small,
hand-authored lookup table, not a blind "compile all 208." A new Python entry-point script runs the
compiler + adapter + `engine.run()` inline and is invoked from a new backend route via
`child_process.execFile`; the loan-status derivation is a new, pure mapping function reading the
engine's existing `RunResult.qc_failures`/`needs_review`, not a change to `engine.py` itself.

## Technical Context

**Language/Version**: Python 3.9-compatible (new compiler/adapter/entry-point scripts, matching
`p0/qc_engine`'s existing constraint) + TypeScript/Node (new backend route, matching `020`'s
existing `backend/`) + TypeScript/React 19 (frontend changes, matching the existing app)
**Primary Dependencies**: `p0/qc_engine` (existing — `ruleset.py`/`engine.py` unmodified;
`model.py`'s `DocCitation` gets one small, additive `document_ids` field, see research.md Item 8),
Express (existing, `020`'s backend), React 19/Vite 6 (existing frontend) — no new third-party
dependency added by this feature
**Storage**: Flat files only — the new compiled ruleset is a `Ruleset.to_json()` artifact on disk
(same convention as `storage/rules/gold/`, `result/rules/*`); no database
**Testing**: `pytest` (Python: compiler, adapter, loan-status mapping — matching `p0/tests/`'s
existing convention, `python -m pytest tests/ -v`), `vitest` (backend/frontend — matching `020`'s
existing setup)
**Target Platform**: Web app (existing) — Node backend + Vite/React frontend, engine/adapter
invoked server-side only, never in the browser
**Project Type**: Web application (frontend + backend), extending both existing halves plus one
new Python subpackage addition under the existing `p0/qc_engine/`
**Performance Goals**: Single-loan, single-run, sub-second (no load/throughput target — this is a
live demo trigger, not a batch/service endpoint)
**Constraints**: Server-side-only engine invocation (constitution Principle II — the engine never
runs in the browser); `engine.py`/`ruleset.py` MUST remain unmodified (Non-Negotiable #1's "pure
function of (ruleset, loan)" — all new logic is additive, in new files); `model.py`'s one narrow
exception (the `document_ids` citation field, FR-013) is additive metadata only, following that
same file's own established precedent, and changes zero evaluation behavior; the compiled
ruleset MUST NOT include a check whose field mapping isn't confidently resolvable (constitution
Safety Gate — referential integrity)
**Scale/Scope**: One real evaluable loan; ~8-12 checks in the compiled ruleset (not all 208); 20
loans in the queue (19 cosmetic); 3 new routes (FHA/VA/USDA) replacing 1

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Result |
|---|---|---|
| I. Determinism of the correct computation | Engine invocation is `engine.run(loan, ruleset)`, unmodified, over Decimal math already proven bit-exact. New code (compiler, adapter, status mapper) is read/derive-only over existing, tested primitives. | PASS |
| II. Compile, then run | The gold ruleset is compiled to a `Ruleset` artifact *before* any run — same "compile once, run deterministically" shape as `019`'s `build_gold_catalog.py`, just a second output target. No runtime-LLM step anywhere in this feature. | PASS |
| III. Eval is foundational | No new check *kinds* are introduced — reusing `predicate`/`is_present`, already covered by the engine's existing test suite. SC-002 requires the UI's displayed verdict to match an independently-run audit exactly — a labeled, checkable claim. | PASS |
| IV. Build the core, assume the periphery | Reuses `020`'s existing Touchless proxy and pull flow entirely; adds only the audit-run bridge. Does not rebuild extraction or the LOS connector. | PASS |
| V. Source independence | Not applicable to this feature's checks — all in scope are `predicate`/`is_present` (QC-phase, doc-only), not RECONCILE-phase doc-vs-system comparisons; no new source-independence claim is made. | N/A |
| VI. Configurable by non-technical users | Not applicable — this feature is a demo-trigger/audit-run wire-up, not a new authoring surface. `019`'s existing authoring screen is untouched. | N/A |
| VII. Configuration is authored data | The compiled ruleset is authored data (from the gold ruleset) interpreted by the version-pinned `engine.py`/`ENGINE_VERSION` — same one-model shape. Referential integrity (every check's field resolves to a real, adapter-populated field) is enforced by construction (research.md Item 2's filtering), not left to the engine to silently no-op. | PASS |
| Safety Gate (zero false-auto-clears, referential integrity) | Directly drives the Item 2 scoping decision: checks whose field mapping isn't confidently resolvable are excluded from the compiled ruleset entirely, rather than risking a false-FAIL-from-missing-mapping or (worse) a false-clear from a silently-unresolved reference. | PASS (by design) |
| Confidence Gate | N/A for this feature by explicit instruction — confidence scoring is out of scope entirely; the adapter never populates `doc_confidence`, so `engine.py`'s existing gate structurally never fires (unmodified, simply unexercised). | N/A |
| Audit Gate | `RunResult`'s existing per-check field-level intermediates and citation shape are passed through unmodified to the frontend response (contracts/audit-run.md). `DocCitation`'s one new field (`document_ids`) makes citations genuinely clickable to real source documents (FR-013) rather than a text-only trace — strengthens this gate's traceability claim, doesn't weaken it. | PASS |

No violations requiring Complexity Tracking justification.

## Project Structure

### Documentation (this feature)

```text
specs/021-touchless-audit-run/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── audit-run.md     # Phase 1 output — new backend endpoint contract
└── tasks.md             # Phase 2 output (/speckit-tasks — not created by this command)
```

### Source Code (repository root)

```text
p0/qc_engine/
├── model.py                              # MODIFIED — one additive field: DocCitation.document_ids (research.md Item 8)
├── ruleset.py                             # existing, unmodified
├── engine.py                              # existing, unmodified
├── compiler/
│   └── build_p0_ruleset_from_gold.py      # NEW — gold -> Ruleset compiler (research.md Item 2)
├── touchless_document_map.py              # NEW — the ~10-entry document-type mapping table
├── touchless_to_canonical_loan.py         # NEW — Touchless loan_application.json -> CanonicalLoan, populates document_ids
├── loan_status.py                         # NEW — severity-tiered status derivation (research.md Item 1)
└── run_touchless_audit_for_demo.py        # NEW — single entry-point: compile + adapt + run + print JSON

p0/tests/
├── test_model_doc_citation_document_ids.py  # NEW — additive-field backward-compat test (existing citations unaffected)
├── test_build_p0_ruleset_from_gold.py     # NEW
├── test_touchless_to_canonical_loan.py    # NEW
└── test_loan_status.py                    # NEW

backend/src/
├── routes/
│   └── audit.ts                           # NEW — POST /api/audit/:applicationId/run (contracts/audit-run.md)
├── applicationStore.ts                    # NEW — in-memory cache of pulled applications (020's pull route
│                                           # never persisted one; audit.ts needs something to read from)
└── __tests__/
    └── audit.route.test.ts                # NEW

frontend/src/
├── lib/
│   ├── types.ts                           # MODIFIED — LoanStatus revised, Finding.citation gains documentIds?: string[] (FR-013), Loan.applicationId already present (020)
│   └── dataSourceContext.tsx              # MODIFIED (020's existing file) — audit-run state, error state
├── data/
│   └── mockData.ts                        # MODIFIED — 20 loans, 19 cosmetic + status remap
├── scripts/
│   └── build_gold_catalog.py              # MODIFIED (019's existing file) — FHA/VA/USDA routes, simulated counts
├── components/
│   ├── LoanQueue.tsx                       # MODIFIED — hide ERROR-status loans from the grid (FR-006a)
│   ├── LoanDetail.tsx                      # MODIFIED — RUNNING/status display, auto-trigger on fetch resolve
│   ├── RoutesFlow.tsx                      # MODIFIED (019's existing file) — restoreToGold() also clears fetched loan/verdict
│   ├── ExceptionReview.tsx                 # MODIFIED — real citation links (FR-013, research.md Item 8), replaces the placeholder PDF-page modal for this feature's exceptions, reuses RetrievedDocumentViewer (020)
│   ├── InspectSources.tsx                  # MODIFIED — real Touchless retrieval sequence + honest citation-gap note
│   └── ImportAndSignView.tsx               # MODIFIED — real document-type example list
└── data/
    └── goldCatalog.json                    # REGENERATED (from build_gold_catalog.py's route changes)

demo/touchless/                             # PORTED from the other repo (Phase 0 of implementation)
├── original/
└── extracted/
```

**Structure Decision**: Web application (frontend + backend), same two halves `020` already
established, plus one new Python subpackage inside the existing `p0/qc_engine/` (not a new
top-level directory — this is an extension of the existing engine's ecosystem, matching how `019`'s
`build_gold_catalog.py` already lives inside `frontend/scripts/` rather than inventing a new
location). No new services, no new databases, no new frontend routes/screens (the audit-run UI
lives inside the existing `LoanDetail`/`LoanQueue` components, per spec021's User Story 1 — no new
top-level nav entry).

## Complexity Tracking

*No entries — Constitution Check found no violations requiring justification.*
