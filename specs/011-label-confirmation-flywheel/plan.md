# Implementation Plan: Label Confirmation Flywheel

**Branch**: `011-label-confirmation-flywheel` | **Date**: 2026-07-27 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/011-label-confirmation-flywheel/spec.md`

## Summary

Build the mechanism that turns a live, cited engine verdict (`p0/qc_engine/engine.py`'s
`CheckResult`) into human-ratified, structured training/eval data: an SME's confirm/correct action is
captured as an immutable, hash-chained `LabelConfirmation`, persisted into a durable, append-only,
flat-file `LabelCorpus`, and made convertible — with zero rework to that scorer's signature — into
`005-eval-harness-as-promotion-gate`'s scorer-compatible `(CanonicalLoan, expected_verdicts,
provenance)` triple. This is deliberately a **data-capture-and-storage feature, not a UI feature**:
`008` (the review queue) does not exist and is not built here; this feature ships its own minimal,
headless calling convention so the flywheel can be wired starting with the very first pilot loan, per
the roadmap's explicit "wire it early" mandate. The core engineering acts are: (1) a sibling to the
already-implemented `007` `AuditLog` that reuses its proven hash-chain primitives without modifying
it; (2) a pinned, immutable loan-fact snapshot so a later re-extraction can't retroactively change
what a human actually judged; (3) a pure conversion function targeting the exact seam `005`'s own
`FR-010` already designed to receive; and (4) an explicit, non-automatic curation step for promoting
corpus entries into `005`'s permanent GOLDEN panel, so the flywheel cannot silently corrupt the eval
harness it feeds.

## Technical Context

**Language/Version**: Python 3.9-compatible (project-wide constraint).
**Primary Dependencies**: None new. Reuses `qc_engine.model` (`CanonicalLoan`/`SourceValue`),
`qc_engine.engine` (`CheckResult`/`RunResult` — read-only), `qc_engine.audit` (`GENESIS`/`_digest`
constants, imported not modified), and `005`'s `p0/eval_synth` scorer contract (consumed, not
modified) — all existing. `hashlib`/`json`/`sqlite3` from stdlib, mirroring `audit.py`'s own imports.
**Storage**: Dual, deliberate (spec.md Assumptions): a small SQLite hash-chain (`ConfirmationLog`,
mirrors `audit.py`'s own `sqlite3` table pattern) for tamper-evidence of the *event*, plus a
version-control-friendly, append-only flat file (`p0/label_corpus/confirmed_labels.jsonl`) as the
durable, human-inspectable, growing `LabelCorpus` a curation pass actually reads. No new database
technology introduced — same `sqlite3` stdlib module `audit.py` already uses, plus flat JSONL
consistent with the rest of `p0/`'s flat-file convention (`002a`'s `sme_review_package.md`,
`p0/fixtures/*.py`).
**Testing**: `pytest p0/tests -v` (existing suite, zero-regression bar) plus new test modules
covering capture + chain integrity (SC-001/002/004), corpus durability + disagreement preservation
(SC-001), conversion to `005`'s scorer triple (SC-003), and no-auto-promotion (SC-005).
**Target Platform**: Local execution / any process that can import `p0.qc_engine.label_capture` and
call a plain function — no service, no UI, consistent with `008` being explicitly out of scope here.
**Project Type**: Library extension to the existing `p0/qc_engine` + `p0/eval_synth` packages — no new
project, no UI.
**Performance Goals**: Capture is a single in-memory dataclass construction + one SQLite insert + one
JSONL append per confirmation — negligible cost, no batch/throughput requirement at pilot scale (tens
to low hundreds of confirmations, not the 5,000-loan VOLUME-tier scale `005` already handles).
**Constraints**: Zero regression against the existing suite, `007`'s `AuditLog` behavior, and
`p0/harness.py`'s bit-exact digest (SC-006) — this feature adds a new, separate mechanism; it must
not touch the engine's own evaluation behavior or `audit.py`'s existing schema. No runtime LLM call
anywhere in this feature (FR-012, Principle I) — capture is pure bookkeeping over already-computed
data plus a human's explicit input. Python 3.9 syntax only (`Optional[...]`, not `X | None`).
**Scale/Scope**: One new capture module, one new corpus/query module, one new conversion module
targeting `005`, one new (separately-invoked) promotion-to-GOLDEN script. Does not include building
`008` (the review UI) or any cross-customer aggregation (out of scope, spec.md FR-009/FR-010).

## Constitution Check

*GATE: evaluated against `.specify/memory/constitution.md` v1.1.1.*

| Principle | Status | Note |
|---|---|---|
| I — Determinism of the *correct* computation | PASS | Capture is a pure function of already-computed `CheckResult`/`RunResult` data plus the human's explicit input; the record's timestamp is injected by the caller, never wall-clock (FR-012). This feature never re-runs the engine and never mutates a `RunResult`/`CheckResult` it references — same "read-only, one-way, downstream-of-the-verdict" discipline `014`'s narrative established. |
| II — Compile, then run | PASS | Zero LLM calls anywhere in this feature. It captures a human's reaction to an already-compiled, already-signed `Ruleset`'s output; it does not compile, interpret, or re-evaluate anything. |
| III — Eval is foundational | PASS (this feature *is* the flywheel) | Directly implements the constitution's own "ground truth before trust" mandate at the one point the synthetic eval (`005`) cannot reach by construction: a machine verdict a human has actually looked at and ratified or corrected. Feeds `005`'s tiers without requiring any change to `005`'s scorer interface (FR-006, `005` FR-010). |
| IV — Build the core, assume the periphery | PASS | No document extraction, no LOS integration touched. This is an internal data-capture/audit mechanism over the engine's own already-computed output. |
| V — Source independence | N/A this feature | This feature does not construct or compare DOC-vs-SYSTEM values; it captures a human's reaction to a verdict the engine already reconciled under `003c`'s discipline. Nothing here re-derives a comparison value. |
| VI — Configurable by non-technical users | N/A this feature | No authoring-surface change. The eventual human-facing action ("click confirm/correct") belongs to `008`, not built here; this feature is the plumbing underneath it. |
| VII — Configuration is authored data | PASS (referenced, not extended) | This feature does not add a new authored-configuration layer (no new field/check/block/route). `LabelConfirmation`'s `check_id` reference is expected to resolve to a real check in the ruleset that produced the `RunResult` it cites — this feature assumes that referential integrity already holds (guaranteed upstream by the SAFE gate, per `005`'s own Edge Cases precedent), it does not re-validate it. |

**No unjustified violations. Complexity Tracking is empty.**

## Project Structure

### Documentation (this feature)

```text
specs/011-label-confirmation-flywheel/
├── spec.md
├── plan.md                  # This file
├── tasks.md                 # Phase 2 output (/speckit-tasks)
└── checklists/
    └── requirements.md
```

No `research.md`/`data-model.md`/`contracts/` — deliberately omitted, following `005`'s own precedent:
this feature reuses two already-proven, already-designed patterns (`audit.py`'s hash chain; `005`'s
own `FR-010` provenance-tagged scorer contract) rather than researching new mechanisms from scratch.
The "research" this plan would otherwise capture is the direct code-reading already recorded in
spec.md's "Foundation this builds on" / "Gaps confirmed by direct inspection" sections.

### Source Code (repository root)

```text
p0/qc_engine/
└── label_capture.py            # NEW — LabelConfirmation dataclass (+ to_dict()), LoanSnapshot
                                 #   helper (serializes + hashes a CanonicalLoan's facts at capture
                                 #   time, FR-005), ConfirmationLog class (own SQLite table, imports
                                 #   GENESIS/_digest from qc_engine.audit — does not modify audit.py,
                                 #   FR-002), and capture_confirmation(...) — the headless entry
                                 #   point (FR-008) validating FR-003 before appending to both the
                                 #   ConfirmationLog and the flat-file corpus (FR-004)

p0/label_corpus/                # NEW package — the durable, human-inspectable, growing artifact
├── __init__.py
├── confirmed_labels.jsonl      # NEW — the flat, append-only corpus file itself (one JSON object
                                 #   per LabelConfirmation + its LoanSnapshot, per line); grows as
                                 #   capture_confirmation() is called; never truncated/rewritten
├── corpus_io.py                 # NEW — append/read/filter functions over confirmed_labels.jsonl:
                                 #   read_all(), filter_by(action=..., check_id=...) (FR-013),
                                 #   append_entry() (called by label_capture.capture_confirmation)
└── promote_to_golden.py         # NEW — the explicit, separately-invoked curation step (FR-007):
                                 #   takes a named list of corpus entry ids, merges only those into
                                 #   005's p0/fixtures/golden_panel.py, tagging each promoted entry
                                 #   with its confirmation provenance (reviewer_id, confirmed_at,
                                 #   source LabelConfirmation id) so a panel case is traceable back
                                 #   to the human decision that produced it

p0/eval_synth/
└── label_corpus_ingest.py       # NEW — the pure conversion function (FR-006): reads a
                                 #   LabelConfirmation + LoanSnapshot (via p0.label_corpus.corpus_io)
                                 #   and returns 005's scorer-compatible (CanonicalLoan,
                                 #   expected_verdicts, provenance) triple, provenance in
                                 #   {"sme-confirmed", "sme-corrected"} — imported by
                                 #   promote_to_golden.py and by any ad-hoc VOLUME-tier ingestion,
                                 #   never duplicating 005's own scorer logic

p0/qc_engine/audit.py            # UNMODIFIED — GENESIS/_digest imported by label_capture.py;
                                  # AuditLog's own schema/behavior untouched (spec.md FR-002, SC-006)

p0/experiment_002a/
├── build_review_package.py      # UNMODIFIED — the different, compile-time artifact this feature's
└── apply_decision_rule.py       #   spec.md explicitly distinguishes itself from; not imported by
                                  #   label_capture.py, informs its shape only

p0/tests/
├── test_label_capture.py        # NEW — US1: capture CONFIRM/CORRECT, FR-003 rejection, chain
│                                 #   integrity + tamper detection (SC-002, SC-004)
├── test_label_corpus.py         # NEW — US2: durability across process restarts, disagreement
│                                 #   preservation, action/check_id filtering (SC-001)
├── test_label_corpus_ingest.py  # NEW — US3: conversion to 005's scorer triple, scored via 005's
│                                 #   actual scorer function with zero signature changes (SC-003)
└── test_promote_to_golden.py    # NEW — US4: zero unintended promotion; explicit promotion merges
                                  #   only named entries, tagged with provenance (SC-005)
```

**Structure Decision**: New capability lands as one new module in the existing `p0/qc_engine/` package
(the natural home for the capture mechanism, since it must import `qc_engine.audit`'s primitives and
reference `qc_engine.engine`'s `CheckResult`/`RunResult` types), one new `p0/label_corpus/` package
(the growing, human-inspectable artifact and its curation step — parallel to how `p0/fixtures/`
already hosts version-controlled panels), and one new conversion module inside `p0/eval_synth/` (the
natural home for anything targeting `005`'s scorer contract, matching where `005`'s own
`scenario_construction.py` lives). `audit.py` and `experiment_002a`'s two files are left in place
unmodified — this is an additive, sibling feature, not a rewrite or extension of already-working,
already-implemented code.

## Complexity Tracking

*No entries — no Constitution Check violations require justification.*
