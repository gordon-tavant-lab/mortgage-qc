# Tasks: Precondition Ontology Layer (modular, reusable)

**Input**: Design documents from `specs/002f-precondition-ontology-layer/`
**Prerequisites**: plan.md, spec.md

**Tests**: Included — SC-001/002/003/004/005 are the correctness/safety/reusability proof this
feature exists to produce.

**Organization**: Tasks grouped by user story (= by layer), per this project's convention.

## Phase 1: Setup

- [ ] T001 Create `p0/ontology_extraction/` package skeleton (`__init__.py`, empty
      `layer0_clustering.py`/`layer1_extraction.py`/`layer2_grounded.py`/`pipeline.py`) — no logic
      yet
      → Done when: `python3 -c "import ontology_extraction"` succeeds from `p0/` with no
      `qc_engine` import anywhere in the package
- [ ] T002 Build the real fixture: extract the Retail Post-Closing sheet's raw rows (questionnaire,
      qcode, question_text, response, question_criteria_by_q) into a checked-in test fixture — the
      same real data this session's scan already touched, persisted so tests don't re-read the live
      `.xlsx` (mirrors how other specs' fixtures are derived from `demo/rules/*.xlsx` once, not
      re-parsed per test run)
- [ ] T003 Create `p0/tests/test_ontology_extraction.py` and `p0/tests/test_ontology_reusability.py`
      module skeletons — no test bodies yet

---

## Phase 2: User Story 1 — Layer 0 clustering (Priority: P1) 🎯 MVP

**Done when:** Layer 0 reproduces the real 24-ontology-entry, 3,255-row result against the fixture;
unparseable rows are reported, not dropped; output is deterministic across repeated runs.

**Independent Test**: Run Layer 0 against the T002 fixture twice; confirm byte-identical output both
times and confirm it matches the 24/3,255 numbers independently.

- [ ] T004 [US1] Implement `layer0_clustering.py`: a configurable dependency-key pattern (default:
      the `QuestionID == N && AnswerText == "..."` regex confirmed against the real data), clustering
      by key across all input rows into `OntologyEntry` objects (depends on T001)
- [ ] T005 [US1] In `test_ontology_extraction.py`: run Layer 0 against the T002 fixture; assert
      exactly 24 distinct ontology entries and 3,255 total resolved rows (SC-001) (depends on T002,
      T004)
- [ ] T006 [US1] In `test_ontology_extraction.py`: construct a row with a dependency expression that
      doesn't match the configured pattern; assert it's reported as unparsed, not silently dropped or
      partially matched (FR-002) (depends on T004)
- [ ] T007 [US1] In `test_ontology_extraction.py`: run Layer 0 twice against the same input; assert
      byte-identical output (determinism proof) (depends on T004)

---

## Phase 3: User Story 2 — Layer 1 extraction (Priority: P1)

**Done when:** Layer 1's compile prompt classifies deontic modality + cross-reference target as
explicit, separate signals before extracting a precondition; defaults to none when uncertain.

**Independent Test**: Compile the explicit/none/ambiguous row trio from spec.md's Acceptance
Scenarios; confirm the three expected outcomes.

- [ ] T008 [US2] Implement `layer1_extraction.py`: a `SYSTEM_PROMPT` extension (or new prompt,
      reusing `compile_llm.py`'s existing Bedrock-call harness) that classifies deontic modality
      (Obligation/Permission/Prohibition/Recommendation) and any cross-reference target as separate
      output fields before the precondition itself — never one flat "find the condition" ask
      (depends on T001)
- [ ] T009 [US2] Recompile the real gift-fund row and 2+ representative unconditional rows through
      Layer 1 with the updated prompt; confirm the gift-fund row extracts correctly with a traceable
      quoted span, and unconditional rows stay precondition-free (depends on T008)
- [ ] T010 [US2] Recompile a genuinely ambiguous row; confirm Layer 1 defaults to no precondition
      rather than guessing (FR-004) (depends on T008)

---

## Phase 4: User Story 3 — Layer 2 grounded extraction (Priority: P1)

**Done when:** Layer 2 retrieves from `002c`'s signed KB, runs automated grounding verification
before judging, and never auto-approves regardless of judge unanimity.

**Independent Test**: Construct a supported-citation case (passes verification, proceeds to judging)
and an unsupported-citation case (rejected before judging).

- [ ] T011 [US3] Implement `layer2_grounded.py`: call `002c`'s `knowledge_base.retrieve()` for the
      row's program-scoped signed KB (reuse, not reimplement) (depends on T001)
- [ ] T012 [US3] Implement the automated grounding-verification check — an NLI/fact-check-style pass
      (per GASP/MiniCheck precedent) confirming the LLM's claimed citation actually supports the
      proposed precondition; a proposal failing this check is rejected before reaching judging
      (depends on T011)
- [ ] T013 [US3] In `test_ontology_extraction.py`: construct a supported-citation case; assert it
      passes grounding verification and proceeds (SC-003 positive case) (depends on T012)
- [ ] T014 [US3] In `test_ontology_extraction.py`: construct an unsupported-citation case (LLM claims
      a citation that doesn't actually say what's claimed); assert grounding verification rejects it
      before judging ever runs (SC-003) (depends on T012)
- [ ] T015 [US3] Wire `002c`'s `judge_panel.escalate_or_approve()` into `layer2_grounded.py`, but
      override its outcome: regardless of the panel's verdict, a Layer-2 proposal is always routed to
      mandatory human review, never auto-approved (FR-007) (depends on T011)
- [ ] T016 [US3] In `test_ontology_extraction.py`: construct a case where the judge panel would
      normally auto-approve (unanimous, high confidence); assert the Layer-2 override still routes it
      to human review, not auto-sign (SC-004) (depends on T015)

---

## Phase 5: Polish & Cross-Cutting

- [ ] T017 Implement `pipeline.py`'s `run_layers()`: sequences Layer 0 → 1 → 2 per FR-008 — a row
      resolved by an earlier layer is never reprocessed by a later one (depends on T004, T008, T011)
- [ ] T017a [Onity-adopted] Add bounded-retry-then-explicit-`parse_failed` handling to Layer 1's and
      Layer 2's LLM-calling code (FR-011); in `test_ontology_extraction.py`, construct a malformed-
      output case and confirm it produces `parse_failed=True` after retries exhaust, never a guessed
      default (SC-007) (depends on T008, T012)
- [ ] T017b [Onity-adopted] Add `CoverageReport` computation to Layer 0 (rows resolved / total input,
      `below_floor` against a configurable threshold) and wire `pipeline.py` to halt Layer 1/2
      expansion when `below_floor` (FR-012); in `test_ontology_extraction.py`, construct a
      low-structure input set and confirm the halt behavior (SC-008) (depends on T004, T017)
- [ ] T018 In `test_ontology_reusability.py`: a static check (AST scan or import-time assertion) that
      zero files under `p0/ontology_extraction/` import anything from `p0.qc_engine` (SC-005, FR-009) *(overstated as written — FR-010 sanctions exactly one exception: `layer2_grounded.py` imports `002c`'s `knowledge_base`/`judge_panel`, and `test_ontology_reusability.py` enforces that precise shape. Corrected 2026-07-26, spec audit)*
- [ ] T019 Run `pytest p0/tests -v` in full; confirm zero regressions to `002c`'s existing 164 tests
- [ ] T020 Measure and report Layer 0's real coverage (resolved rows / total gated rows) against the
      full Retail Post-Closing sheet, not just the sample — feeds `002e`'s eventual Layer 1/2 scope
      decision (SC-002)
- [ ] T021 Update `output/ROADMAP.md` to register `002f` and cross-reference it from `002e`'s entry

## Dependencies & Execution Order

- Phase 1 (T001-T003) blocks everything.
- Phase 2 (Layer 0), Phase 3 (Layer 1), and Phase 4 (Layer 2) are independent of each other —
  different files, no shared state — and can proceed in parallel once Phase 1 lands.
- T017 (pipeline sequencing) depends on all three layers existing.
- T018-T021 are the closing verification sequence.

## Parallel Example

```
# Phases 2/3/4 touch different files and can run together once T001-T003 exist:
Task: "Implement and test Layer 0 clustering"
Task: "Implement and test Layer 1 multi-task extraction"
Task: "Implement and test Layer 2 grounded extraction + verification"
```
