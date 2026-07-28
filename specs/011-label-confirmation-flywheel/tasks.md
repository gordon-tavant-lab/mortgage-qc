# Tasks: Label Confirmation Flywheel

**Input**: Design documents from `specs/011-label-confirmation-flywheel/`
**Prerequisites**: plan.md, spec.md

**Tests**: Included — this project's constitution makes eval/audit foundational (Principle III, the
Audit gate), and this feature's entire purpose is proving a set of safety-critical behaviors (tamper
detection, no-silent-corruption of the eval harness) — SC-001 through SC-006 are the deliverable, not
optional polish.

**Organization**: Tasks grouped by user story (spec.md P1/P1/P2/P2/P3), TDD-ordered within each story.

## Phase 1: Setup

- [ ] T001 Create `p0/qc_engine/label_capture.py` module skeleton (imports `GENESIS`/`_digest` from
      `qc_engine.audit`, imports `CheckResult`/`RunResult` from `qc_engine.engine`, imports
      `CanonicalLoan` from `qc_engine.model`; module docstring explicitly distinguishing this
      run-time mechanism from `002a`'s compile-time review-package pattern, per spec.md's "Foundation
      this builds on") — no logic implemented yet
- [ ] T002 [P] Create `p0/label_corpus/__init__.py` + `p0/label_corpus/corpus_io.py` module skeleton
- [ ] T003 [P] Create `p0/eval_synth/label_corpus_ingest.py` module skeleton
- [ ] T004 [P] Create `p0/tests/test_label_capture.py`, `test_label_corpus.py`,
      `test_label_corpus_ingest.py`, `test_promote_to_golden.py` module skeletons

---

## Phase 2: User Story 1 — Capture a single SME confirm/correct action as an audited, immutable event (Priority: P1) 🎯 MVP

**Goal**: `capture_confirmation(...)` produces a `LabelConfirmation`, rejects an invalid `CORRECT`,
and chains into a tamper-evident `ConfirmationLog` (spec.md FR-001/002/003/011/012).

**Independent Test**: Call the capture entry point once with `CONFIRM` and once with `CORRECT` +
`corrected_status` against real `CheckResult`s from a constructed `RunResult`; confirm both records
are captured correctly and the chain verifies.

### Tests for User Story 1 ⚠️ (write first, confirm they FAIL before implementation)

- [ ] T005 [P] [US1] Test in `test_label_capture.py`: capturing a `CONFIRM` action against a real
      `CheckResult` (from a constructed `RunResult`, reusing `p0/fixtures/golden.py`) produces a
      `LabelConfirmation` naming `loan_id`/`ruleset_sha256`/`ruleset_version`/`check_id`/
      `original_status`/`action="CONFIRM"`/`corrected_status=None` (FR-001) (depends on T001)
- [ ] T006 [P] [US1] Test: capturing a `CORRECT` action with a `corrected_status` produces a record
      with `action="CORRECT"` and that exact `corrected_status` (FR-001) (depends on T001)
- [ ] T007 [P] [US1] Test: attempting to capture a `CORRECT` action with an empty/missing
      `corrected_status` raises/returns an explicit rejection — never silently stored (FR-003, SC-004)
      (depends on T001)
- [ ] T008 [P] [US1] Test: capturing a confirmation requires and records a real, verifiable
      `record_hash` from a `007` `AuditLog` entry for the same run — a confirmation constructed
      against a fabricated/nonexistent audit record hash is rejected (FR-011) (depends on T001)
- [ ] T009 [P] [US1] Test in `test_label_capture.py`: two confirmations captured in sequence chain
      correctly (`ConfirmationLog.verify_chain()`-equivalent returns `True`); mutating one historical
      record's stored payload causes verification to fail from that point forward (FR-002, SC-002)
      (depends on T001)
- [ ] T010 [P] [US1] Test: `capture_confirmation`'s injected `confirmed_at` parameter is used
      verbatim (no wall-clock read inside the function) — confirmed by passing two different
      injected timestamps and asserting both are stored exactly, with no live-clock drift (FR-012)
      (depends on T001)

### Implementation for User Story 1

- [ ] T011 [US1] Implement `LabelConfirmation` dataclass (+ `to_dict()`) in `label_capture.py` per
      spec.md's Key Entities field list (depends on T005–T010 existing as red tests)
- [ ] T012 [US1] Implement `LoanSnapshot` helper: serializes a `CanonicalLoan`'s facts into a stable,
      hashable dict at capture time (FR-005) — no dependency on `p0/qc_engine/model.py`'s own
      `to_dict()` shape changing (depends on T011)
- [ ] T013 [US1] Implement `ConfirmationLog` class: own SQLite table, reusing `audit.py`'s
      `GENESIS`/`_digest` imported (not copied) constants; `append()`, `verify_chain()`, `records()`
      methods mirroring `AuditLog`'s own shape (FR-002) (depends on T009 as a red test)
- [ ] T014 [US1] Implement `capture_confirmation(...)`: validates FR-003 (rejects empty
      `corrected_status` on `CORRECT`), validates FR-011 (the referenced `007` `AuditLog` record hash
      is real), constructs `LabelConfirmation` + `LoanSnapshot`, appends to `ConfirmationLog`, returns
      the new record's hash (depends on T011, T012, T013)
- [ ] T015 [US1] Run T005–T010 again; confirm all green

**Checkpoint**: The capture mechanism itself exists and is provably tamper-evident. Independently
valuable even before corpus durability (US2) or 005-feeding (US3) are wired in.

---

## Phase 3: User Story 2 — The corpus grows durably across runs, and disagreement is preserved, not collapsed (Priority: P1)

**Goal**: Every captured confirmation also lands in a durable, append-only, flat-file `LabelCorpus`
(spec.md FR-004/013/014).

**Independent Test**: Capture N confirmations across M loans in one process; read them back from a
fresh process; capture two differing actions against the identical loan/ruleset/check coordinate and
confirm both persist.

### Tests for User Story 2

- [ ] T016 [P] [US2] Test in `test_label_corpus.py`: capturing N confirmations, then reading
      `confirmed_labels.jsonl` from a freshly-imported module/process, returns exactly N records with
      every field intact, in capture order (FR-004, SC-001) (depends on T014)
- [ ] T017 [P] [US2] Test: capturing two different actions (one `CONFIRM`, one `CORRECT`) against the
      identical `(loan_id, ruleset_sha256, check_id)` coordinate persists both as distinct entries —
      neither overwrites the other (FR-014) (depends on T014)
- [ ] T018 [P] [US2] Test: `corpus_io.filter_by(action="CORRECT")` and `filter_by(check_id=...)` each
      return exactly the matching subset of a mixed corpus (FR-013) (depends on T014)

### Implementation for User Story 2

- [ ] T019 [US2] Implement `corpus_io.append_entry()` (one JSON object per line, never truncating/
      rewriting the file) and `corpus_io.read_all()` in `p0/label_corpus/corpus_io.py` (FR-004)
      (depends on T016 as a red test)
- [ ] T020 [US2] Wire `label_capture.capture_confirmation()` (T014) to call `corpus_io.append_entry()`
      atomically alongside the `ConfirmationLog` append (spec.md Assumptions: dual persistence from
      one capture call) (depends on T019)
- [ ] T021 [US2] Implement `corpus_io.filter_by(action=..., check_id=...)` (FR-013) (depends on T018
      as a red test)
- [ ] T022 [US2] Run T016–T018 again; confirm all green

**Checkpoint**: The corpus durably grows and preserves disagreement — the "compounding" the roadmap
names is now real and provable, independent of whether anything downstream consumes it yet.

---

## Phase 4: User Story 3 — A confirmed/corrected label converts into 005's scorer-compatible shape, with zero rework to that scorer (Priority: P2)

**Goal**: `label_corpus_ingest.py` converts a `LabelConfirmation` + `LoanSnapshot` into `005`'s
`(CanonicalLoan, expected_verdicts, provenance)` triple (spec.md FR-006).

**Independent Test**: Convert one captured `CONFIRM` and one captured `CORRECT` record; feed both
through `005`'s actual scorer function with no modification to its signature.

### Tests for User Story 3

- [ ] T023 [P] [US3] Test in `test_label_corpus_ingest.py`: converting a `CONFIRM` record yields
      `expected_verdicts[check_id] == original_status` and `provenance == "sme-confirmed"` (FR-006)
      (depends on T014, T019)
- [ ] T024 [P] [US3] Test: converting a `CORRECT` record yields `expected_verdicts[check_id] ==
      corrected_status` (not the original machine status) and `provenance == "sme-corrected"` (FR-006)
      (depends on T014, T019)
- [ ] T025 [P] [US3] Test: both converted triples are passed to `005`'s actual scorer function
      (imported from `p0.eval_synth`, not reimplemented) and score without error, with zero changes
      required to that function's signature (SC-003) (depends on T023, T024; depends on `005` module
      existing per that feature's own implementation)

### Implementation for User Story 3

- [ ] T026 [US3] Implement the reverse-of-`LoanSnapshot` reconstruction: rebuild a real
      `qc_engine.model.CanonicalLoan` object from a stored `LoanSnapshot` dict (the inverse of T012)
      (depends on T012)
- [ ] T027 [US3] Implement `label_corpus_ingest.to_eval_case(confirmation) ->
      (CanonicalLoan, expected_verdicts, provenance)` in `p0/eval_synth/label_corpus_ingest.py`,
      using T026's reconstruction and branching only on `action` for `expected_verdicts`/`provenance`
      (FR-006) (depends on T023, T024 as red tests, T026)
- [ ] T028 [US3] Run T023–T025 again; confirm all green

**Checkpoint**: A confirmed/corrected label is now a legitimate, zero-rework input to `005`'s scorer
— the flywheel's "feed back into eval" promise is proven, not merely asserted.

---

## Phase 5: User Story 4 — Promotion into 005's permanent GOLDEN panel is a deliberate, curated step (Priority: P2)

**Goal**: `promote_to_golden.py` merges only explicitly-named corpus entries into `005`'s
`golden_panel.py`, never automatically (spec.md FR-007).

**Independent Test**: Confirm capturing confirmations alone changes nothing in `golden_panel.py`;
confirm an explicit promotion call merges only the named entries, tagged with provenance.

### Tests for User Story 4

- [ ] T029 [P] [US4] Test in `test_promote_to_golden.py`: capturing any number of confirmations, with
      no explicit promotion call, leaves `p0/fixtures/golden_panel.py` byte-identical to its
      pre-capture state (FR-007, SC-005) (depends on T027)
- [ ] T030 [P] [US4] Test: calling `promote_to_golden.promote(entry_ids=[...])` with a specific list
      of corpus entry ids merges exactly those entries into the panel, each tagged with its
      confirmation provenance (`reviewer_id`, `confirmed_at`, source `confirmation_id`) — no other
      corpus entries are merged (FR-007) (depends on T027)

### Implementation for User Story 4

- [ ] T031 [US4] Implement `p0/label_corpus/promote_to_golden.py`'s `promote(entry_ids: List[str])`:
      looks up each named entry via `corpus_io`, converts via `label_corpus_ingest.to_eval_case`,
      appends to `005`'s `golden_panel.py` panel structure with provenance tags, and — critically —
      is never called implicitly by `capture_confirmation` (depends on T029, T030 as red tests)
- [ ] T032 [US4] Run T029–T030 again; confirm all green

**Checkpoint**: The flywheel cannot silently corrupt `005`'s permanent regression panel. A curated,
auditable promotion step exists, ready for a future ops process to schedule.

---

## Phase 6: User Story 5 — The mechanism is usable headlessly from day one of pilot, without waiting on 008 (Priority: P3)

**Goal**: Confirm `capture_confirmation` is reachable with no UI and no dependency on code that
doesn't exist yet (spec.md FR-008).

**Independent Test**: Call the capture entry point via a plain function call / minimal CLI script,
with no `008`-shaped mock.

### Tests for User Story 5

- [ ] T033 [US5] Test: `capture_confirmation` is directly callable as a plain function (no class
      instantiation requiring a UI-shaped context object) and, given identical arguments, produces a
      byte-identical `LabelConfirmation` regardless of whether it's invoked from a test, a CLI
      wrapper, or (hypothetically) a future `008` screen (FR-008)

### Implementation for User Story 5

- [ ] T034 [US5] Add a minimal `if __name__ == "__main__":` CLI wrapper to `label_capture.py`
      (argparse: `--loan-id`, `--ruleset-sha256`, `--check-id`, `--action`, `--corrected-status`,
      `--reviewer-id`, `--audit-record-hash`) as the concrete "interim manual review process" example
      the roadmap's "wire it early" mandate calls for (depends on T014)

**Checkpoint**: `008`, when it lands, is a UI calling an already-proven headless entry point — not a
prerequisite this feature waited on.

---

## Phase 7: Polish & Cross-Cutting

- [ ] T035 Run the full existing suite unmodified: `p0/tests/test_p0.py`, `007`'s existing
      `AuditLog` tests, `p0/harness.py` (bit-exact digest) — confirm zero regression (SC-006)
- [ ] T036 [P] Document `label_capture.py`'s CLI usage and `promote_to_golden.py`'s promotion
      contract in module docstrings, mirroring `audit.py`'s and `eval.py`'s existing docstring
      convention
- [ ] T037 Add a post-hoc "Implementation Notes" section to `plan.md` recording: final task count,
      any amendment discovered during implementation, the before/after `harness.py` digest (SC-006,
      expected unchanged since this feature never touches `qc_engine.engine`/`ruleset`), and a real
      end-to-end example (one constructed pilot loan, one CONFIRM, one CORRECT, one promotion call)

## Dependencies & Execution Order

- **Phase 1 (Setup, T001–T004)** blocks all of Phase 2.
- **Phase 2 (US1, T005–T015)** is the foundational MVP slice — every later phase depends on
  `capture_confirmation` (T014) existing.
- **Phase 3 (US2, T016–T022)** depends on Phase 2 (T014) — it extends the same capture call with
  durable flat-file persistence.
- **Phase 4 (US3, T023–T028)** depends on Phase 2 (T012, T014) and Phase 3 (T019, for reading captured
  entries) — conversion needs both a captured record and a durable place to read it from.
- **Phase 5 (US4, T029–T032)** depends on Phase 4 (T027, the conversion function it calls).
- **Phase 6 (US5, T033–T034)** has no hard dependency beyond Phase 2 (T014) — sequenced last as the
  lowest-priority (P3) confirmation that the mechanism needs no UI.
- **T035–T037** run last, after all user stories are complete.

## Parallel Example

```
# T005–T010 (Phase 2, one capture-behavior case each) can run together once T001 exists:
Task: "CONFIRM capture test in test_label_capture.py"
Task: "CORRECT capture test in test_label_capture.py"
Task: "empty corrected_status rejection test in test_label_capture.py"
Task: "fabricated audit-record-hash rejection test in test_label_capture.py"
Task: "chain integrity + tamper detection test in test_label_capture.py"
Task: "injected-timestamp (no wall-clock) test in test_label_capture.py"
```
