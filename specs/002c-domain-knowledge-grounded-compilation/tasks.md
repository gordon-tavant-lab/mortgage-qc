# Tasks: Domain-Knowledge-Grounded Rule Compilation & Intake Workflow

**Input**: Design documents from `specs/002c-domain-knowledge-grounded-compilation/`
**Prerequisites**: plan.md, spec.md

**Tests**: Included — this project's constitution makes eval/regression-proof foundational
(Principle III). Deterministic logic (versioning, diffing, retrieval ranking, escalation rules) gets
fast unit tests, written red-first. Live-API-calling code (real KB-build research, real judge model
calls) is proven via a standalone script outside the pytest suite, matching `002b`'s own precedent
for `compile_row`/`compile_batch`.

**Organization**: Tasks grouped by user story (spec.md P1×4, P2×1).

## Phase 1: Setup

- [x] T001 Create `p0/qc_engine/compiler/knowledge_base.py` and `judge_panel.py` module skeletons
      (docstrings per the existing `compiler/*.py` style; imports only)
- [x] T002 Create `p0/tests/test_knowledge_base.py` and `p0/tests/test_judge_panel.py` module
      skeletons — no test bodies yet
- [x] T003 Create `p0/qc_engine/compiler/knowledge_base/` data directory **[path since migrated to `storage/knowledge_base/` + SQLite primary — see plan.md's 2026-07-26 post-hoc note]** (empty; corpus files land
      here per-program)

---

## Phase 2: User Story 1 — A versioned, per-program KB exists before any rule grounds against it (Priority: P1)

### Tests ⚠️ (write first, confirm red)

- [x] T004 [P] [US1] Test: building a corpus for one program from a set of documents produces a
      `KnowledgeBaseCorpus` with every section content-fingerprinted (SHA-256) and a version
      identifier; confirm red
- [x] T005 [P] [US1] Test: an unsigned corpus's `is_usable()` returns `False`; `retrieve()` against
      an unsigned corpus raises rather than silently returning content
- [x] T006 [US1] Test: `sign(corpus, signed_by, signed_at)` makes `is_usable()` return `True`,
      mirroring `RuleProvenance`'s existing sign-off shape

### Implementation

- [x] T007 [US1] In `knowledge_base.py`, implement `KBSection` (id, program, content, source_document,
      citation, content_fingerprint) and `KnowledgeBaseCorpus` (program, version, sections, signed_by,
      signed_at) dataclasses
- [x] T008 [US1] Implement `build_corpus(program, documents, version=1) -> KnowledgeBaseCorpus`
      (fingerprints each document's content into one or more `KBSection`s)
- [x] T009 [US1] Implement `sign(corpus, signed_by, signed_at) -> KnowledgeBaseCorpus` and
      `is_usable(corpus) -> bool`
- [x] T010 [US1] Implement `save(corpus, path)`/`load(path)` (JSON, one file per version, never
      overwritten in place)
- [x] T011 [US1] Run T004–T006 again; confirm green

**Checkpoint**: A signed, versioned, fingerprinted KB exists and can be persisted/loaded.

---

## Phase 3: User Story 2 — Incremental updates never break past compiled rules (Priority: P1)

### Tests

- [x] T012 [P] [US2] Test: updating a corpus where only some source documents changed produces a new
      version where unchanged sections keep their original fingerprint and unchanged sections'
      `KBSection` objects are the *same* content, not re-derived; confirm red
- [x] T013 [P] [US2] Test: a `GroundingRecord` created against corpus version N still resolves to
      version N's exact section content after the corpus advances to version N+1 (load `v1.json`
      explicitly still works after `v2.json` is written)

### Implementation

- [x] T014 [US2] Implement `update_corpus(prior_corpus, documents, new_version) ->
      KnowledgeBaseCorpus` — diffs incoming documents against `prior_corpus`'s sections by content
      fingerprint; unchanged sections carry forward unmodified; changed/new documents produce new
      `KBSection`s
- [x] T015 [US2] Run T012–T013 again; confirm green

**Checkpoint**: KB updates are incremental and non-destructive to prior versions' provenance.

---

## Phase 4: User Story 3 — Each compiled rule grounds against its own program's frozen KB (Priority: P1)

### Tests

- [x] T016 [P] [US3] Test: `retrieve(corpus, query_text, top_n=3)` ranks sections by keyword overlap
      with `query_text`, returns at most `top_n`; confirm red
- [x] T017 [P] [US3] Test: `compile_llm.CompiledCheckDraft` gains a `grounding` field
      (`Optional[GroundingRecord]`), default `None` — existing construction sites unaffected
- [x] T018 [US3] Test: `compile_row()` populates `grounding` when a signed KB exists for the row's
      program (via `program_gating.parse_exception_code_prefix`); leaves it `None` when no KB exists
      yet for that program (FR-006 fallback) — using a stubbed Bedrock client, no live call

### Implementation

- [x] T019 [US3] In `knowledge_base.py`, implement `retrieve(corpus, query_text, top_n=3) ->
      List[KBSection]` (pure keyword-overlap ranking — no embeddings, no network)
- [x] T020 [US3] In `compile_llm.py`, add `GroundingRecord` (kb_program, kb_version, section_ids) and
      the `grounding` field on `CompiledCheckDraft`
- [x] T021 [US3] In `compile_row()`, before building the compile prompt: resolve the row's program
      (`program_gating`), look up a signed KB for it (if one exists on disk), call `retrieve()`, and
      include the retrieved section text in the prompt alongside the existing field-catalog context;
      populate `grounding` on the returned draft
- [x] T022 [US3] Run T016–T018 again; confirm green

**Checkpoint**: Compilation is grounded when a KB exists, ungrounded (unchanged `002b` behavior)
otherwise — zero live search/research calls anywhere in this path (SC-003).

---

## Phase 5: User Story 4 — A multi-model judge panel triages which compiled rules need SME review (Priority: P1)

### Tests

- [x] T023 [P] [US4] Test: `escalate_or_approve([verdict_agree, verdict_agree]) ->
      "AUTO_APPROVED"` when all judge verdicts agree; confirm red
- [x] T024 [P] [US4] Test: `escalate_or_approve([verdict_agree, verdict_disagree]) ->
      "ESCALATED"` on ANY disagreement — never a majority-vote auto-approve (FR-008); confirm red
- [x] T025 [US4] Test: an escalated result preserves every individual `JudgeVerdict`'s reasoning,
      not just the aggregate flag (FR-009)
- [x] T026 [US4] Test: a judge verdict below the configured confidence threshold escalates even if
      all verdicts nominally "agree" (FR-008's second clause)

### Implementation

- [x] T027 [US4] In `judge_panel.py`, implement `JudgeVerdict` (judge_model, agrees, confidence,
      reasoning) dataclass
- [x] T028 [US4] Implement `escalate_or_approve(verdicts, confidence_threshold=0.8) -> str` (pure
      logic: unanimous agreement AND all confidences >= threshold -> `"AUTO_APPROVED"`; otherwise
      `"ESCALATED"`) — no N-of-M parameter, matching the conservative posture (plan.md Constraints)
- [x] T029 [US4] Implement `judge_check(client, check, source_text, grounding, judge_model_id) ->
      JudgeVerdict` (one real Bedrock `converse()` call per judge — kept out of the fast test suite
      per T023–T026 using stubbed verdicts instead)
- [x] T030 [US4] Run T023–T026 again; confirm green

**Checkpoint**: The escalation rule is proven correct and conservative by construction — auto-approve
requires unanimous, confident agreement; anything else escalates with full reasoning preserved.

---

## Phase 6: User Story 5 — The full intake workflow (Priority: P2)

- [x] T031 [P] [US5] Test: a document type never seen before halts before any extraction — a
      constructed "unknown type" input raises/returns a halt signal, not a silent pass-through
      (FR-011); confirm red
- [x] T032 [US5] Implement a reusable orchestration function, `run_intake_demo()` in
      `p0/experiment_002c/build_fha_kb.py` (real script — not a pytest-covered module) demonstrating
      the 10-step sequence end to end against one small, real, hand-curated FHA knowledge base:
      fingerprint → segment → classify/gate → build/update KB → extract (grounded) → judge →
      integrity screen (existing `002b` mechanism) → exception queue → sign-off & version-lock →
      deploy-ready signed ruleset. **Self-correction (same day, caught by a direct code-vs-spec
      check, not a second self-review pass)**: the first version of this task's implementation
      stopped after the judge panel (steps 1–6) and was marked `[x]` complete without actually
      reaching the integrity screen, exception-queue routing, or real `Ruleset` sign-off (steps
      7–10) — closed by rewriting `main()`'s inline script into the real `run_intake_demo()`
      function this task always described, and by actually calling
      `catalog.validate_referential_integrity` and `compile_llm.assemble_ruleset`. Persisted output
      as `p0/experiment_002c/RESULTS.md` (was missing entirely — 002a's own precedent has one,
      002c's first pass didn't).
- [x] T033 Run T031 again; confirm green. Also re-ran the full corrected `run_intake_demo()` for
      real (real Bedrock calls, real HUD Handbook text, real judge panel) — outcome
      `SIGNED_RULESET_READY`, `signed_ruleset_sha256` verified reproducible by local reconstruction.

**Checkpoint**: The mechanism (US1–4) composes into the FULL sequence spec.md describes, proven
end-to-end against a small real KB, including the steps a same-day self-correction found missing —
not yet the full 6-program corpus (explicitly deferred, plan.md Scale/Scope; requires separate
go-ahead given real research-agent cost).

---

## Phase 7: Polish & Cross-Cutting

- [x] T034 [P] Test (FR-005/SC-003, zero live calls in the compile path): grep-verify
      `knowledge_base.py`'s `retrieve()` and `compile_llm.py`'s grounding call site make no
      `boto3`/network calls — pure function over already-loaded corpus data
- [x] T035 Run the full existing suite unmodified: `python3 -m pytest p0/ -q` and `python3
      p0/harness.py`, confirm zero regression — digest unchanged, since this feature touches no
      `engine.py`/`model.py`/`ruleset.py` code
- [x] T036 Add a post-hoc "Implementation Notes" section to `plan.md` recording final task/test
      counts and confirming the digest is unchanged

## Dependencies & Execution Order

- **T001–T003** (setup) block all of Phase 2.
- **Phase 2 (US1)** is the MVP slice — KB versioning/sign-off exists before anything else can use it.
- **Phase 3 (US2)** depends on Phase 2 (updates a corpus that must first exist).
- **Phase 4 (US3)** depends on Phase 2 (retrieval needs a signed corpus) — independent of Phase 3.
- **Phase 5 (US4)** is independent of Phases 2–4 (pure escalation logic + judge-call wiring) — can
  build in parallel with either.
- **Phase 6 (US5)** depends on Phases 2–5 all existing (orchestrates all of them).
- **T034–T036** run last.
