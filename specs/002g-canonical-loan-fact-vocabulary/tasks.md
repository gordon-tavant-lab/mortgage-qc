# Tasks: Canonical Loan-Fact Vocabulary + Compile-Time Precondition Wiring

**Plan**: `plan.md` · **Created**: 2026-07-26

## Phase 1 — Vocabulary module

- [X] T001 `knowledge_base.py`: refactor `sign()` to `dataclasses.replace()` (generic, same
      semantics). Done when: existing KB tests pass unchanged.
- [X] T002 `p0/qc_engine/compiler/fact_vocabulary.py`: `QuestionBinding`, `CanonicalFact`,
      `FactVocabulary`, `save`/`load` (`storage/fact_vocabulary/v<N>.json`),
      `VocabularyNotSignedError`. Done when: roundtrip save/load preserves all fields.
- [X] T003 `resolve_layer0()` + `resolve_field_name()` per plan §1 (signed-gate, `|`-join `in`
      encoding, unresolved/novel refusal paths). Done when: test_fact_vocabulary.py resolution
      tests pass.
- [X] T004 `attach_guide_citations()` (concept index — citation strings only, via `KB.retrieve`).
      Done when: signed-corpus attach + unsigned-corpus refusal tests pass.

## Phase 2 — Compile wiring

- [X] T005 `CompiledCheckDraft` += `applies_if_provenance`/`applies_if_review`;
      `attach_preconditions()` + `PreconditionAttachReport` per plan §2 (HIGH-tier-only attach).
      Done when: wiring tests pass against the real gift rows with zero LLM calls.
- [X] T006 `field_catalog.json` += `gift_funds_used` (rule-grounded description citing question
      570606). Done when: taxonomy-grounding + masquerade tests still pass.

## Phase 3 — Replay + seed artifact

- [X] T007 `p0/qc_engine/replay.py`: `replay()` + `ReplayReport`. Done when: test_replay_panel.py
      passes on the 5 real from_docs loans.
- [X] T008 `build_seed_fact_vocabulary.py` → `storage/fact_vocabulary/v1.json` (honest placeholder
      signature) + Layer-0 full-sheet coverage printout. Done when: script runs, artifact loads and
      resolves the real gift proposals.

## Phase 4 — Proof

- [X] T009 `test_compile_precondition_wiring.py` SC-001 end-to-end: real rows → Layer 0 → resolve →
      `applies_if` → real loan 01 fixture → `NOT_APPLICABLE`. FR-005 identical-eval test.
- [X] T010 Full suite + `python3 p0/harness.py` green; pinned digest tests untouched (SC-003).
