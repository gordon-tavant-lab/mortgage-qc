# Feature Specification: Standalone `engine/` — the definitive official QC audit engine

**Feature Branch**: `worktree-gold-ruleset-plan` (this spec lands on the existing branch/PR #7,
not a new one — see Assumptions)
**Created**: 2026-08-02
**Status**: Draft
**Input**: User description: "Extract the currently-exercised p0 QC pipeline (the gold-ruleset
compiler, the Touchless adapter, the core deterministic engine, and the 25/25 standing-gate
validation harness) into a new, minimal, standalone `engine/` folder at the repo root — a copy,
not a move, so `p0/` remains fully intact and functional — establishing `engine/` as the
definitive official QC audit engine ahead of merging this branch's gold-ruleset work into
`main`. The copy must exclude `p0/`'s experimental/superseded code (the ~20 experiment/eval
directories, the older AMQ-workbook-direct compiler files, the ontology-extraction pipeline) and
only include what the actually-exercised runtime path imports."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run the QC engine without any experimental baggage (Priority: P1)

An engineer (or a CI job, or a future backend integration) needs to compile the gold ruleset,
adapt a real Touchless loan payload, evaluate it, and trust the result — without wading through
or accidentally depending on any of `p0/`'s ~20 experiment directories, the superseded
AMQ-workbook-direct compiler, or the ontology-extraction pipeline that CLAUDE.md already
documents as legacy.

**Why this priority**: This is the entire point of the feature — everything else is in service
of this. Without it, there is no "definitive official engine," just another copy of `p0/`.

**Independent Test**: From a clean checkout, run only the three commands in `engine/README.md`
(adapt → compile+evaluate → verify) using nothing outside `engine/` except the existing
`storage/rules/gold/data/` ruleset and `demo/touchless/` sample payload (both already shared,
external inputs — not part of this copy). Confirm the verdict distribution matches `p0/`'s
current run exactly.

**Acceptance Scenarios**:

1. **Given** a fresh checkout of this branch, **When** `engine/qc_engine/adapters/
   touchless_adapter.py` is run against a real Touchless loan payload, **Then** it produces the
   same fixture JSON `p0/qc_engine/adapters/touchless_adapter.py` would produce for the same
   input.
2. **Given** that fixture, **When** `engine/qc_engine/compiler/import_gold_ruleset.py` compiles
   the gold ruleset and evaluates it, **Then** the resulting verdict distribution (PASS /
   NEEDS_REVIEW / NOT_APPLICABLE / NOT_COMPILED counts) is identical to `p0/`'s current run.
3. **Given** the engine's own README instructions alone (no reference back into `p0/`), **When**
   someone unfamiliar with this session's history follows them, **Then** they can run the full
   pipeline end to end.

---

### User Story 2 - Prove the engine's own correctness claim standalone (Priority: P2)

The same engineer/CI job needs to verify the copied engine actually works correctly — not just
that it runs, but that it produces correct verdicts — without depending on `p0/`'s test
infrastructure.

**Why this priority**: A "definitive official engine" that can't prove its own headline claim
(deterministic, correct defect detection) independently isn't yet trustworthy as *the* official
artifact — it's still leaning on `p0/` for credibility.

**Independent Test**: Run `engine/fixtures/from_docs/verify_against_defects.py` with no `p0/`
files on the path. It must report 25/25 known-defect detection, matching the standing gate
CLAUDE.md already requires of `p0/`.

**Acceptance Scenarios**:

1. **Given** the 5 labeled synthetic loan fixtures copied into `engine/fixtures/from_docs/`,
   **When** `verify_against_defects.py` runs from inside `engine/`, **Then** it reports 25/25
   without importing anything from `p0/`.

---

### User Story 3 - `p0/` remains fully intact after the extraction (Priority: P1)

Whoever continues working in `p0/` (running resolve6/7/8-style passes, the coverage gate, the
pytest suite) needs everything there to keep working exactly as it does today — this is a copy
operation, and nothing about `p0/`'s own behavior should change.

**Why this priority**: Explicitly non-negotiable per the feature description ("a copy, not a
move, so `p0/` remains fully intact and functional"). A regression here would mean the extraction
did net harm even if `engine/` itself works.

**Independent Test**: Diff `p0/` before and after the extraction — zero content changes (except
resolving one pre-existing, unrelated loose end — see Assumptions). Re-run `p0/`'s own gates
(`pytest p0/`, `p0/fixtures/from_docs/verify_against_defects.py`) and confirm identical results
to before the extraction.

**Acceptance Scenarios**:

1. **Given** `p0/` before this feature is implemented, **When** the extraction is complete,
   **Then** `git diff` shows zero modifications under `p0/` (beyond the pre-existing loose-end
   fixture-edit resolution called out in Assumptions).
2. **Given** `p0/`'s existing standing gates, **When** run after the extraction, **Then** they
   report the same results as before (445 passed / 3 skipped / 1 xfailed; 25/25 defects).

---

### Edge Cases

- What happens if a future change to `p0/qc_engine/`'s core files (`money.py`, `engine.py`, etc.)
  needs to reach `engine/` too? Out of scope for this feature — this is a one-time extraction, not
  an ongoing sync mechanism. Whoever maintains `engine/` going forward owns keeping it current;
  not addressed here.
- What happens if `engine/`'s copy of `import_gold_ruleset.py` is run before `storage/rules/gold/
  data/rules_compiled.json` exists (e.g., a checkout that never ran the gold-ruleset pipeline)?
  Same behavior as `p0/`'s original — the file-not-found error is unchanged by this copy, since
  the compiler's `_REPO_ROOT`-relative paths point at the same shared `storage/` tree either way.
- What happens to the output directory naming (`RUN_DIR`) that's currently a literal, dated
  bake-off name in `p0/`'s copy? Addressed directly — the `engine/` copy renames this one constant
  so it doesn't read as tied to one specific historical bake-off run.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a standalone `engine/` folder, at the repo root, containing
  only the files the actually-exercised runtime path (Touchless adapter → gold-ruleset compiler →
  deterministic engine → standing-gate verification) imports, confirmed by direct inspection of
  each file's own `import`/`from` statements — not a directory-level copy of `p0/qc_engine/`.
- **FR-002**: `engine/` MUST reproduce `p0/`'s internal folder depth exactly
  (`engine/qc_engine/compiler/...`, `engine/qc_engine/adapters/...`,
  `engine/fixtures/from_docs/...`) so the existing `_REPO_ROOT`-relative path logic in
  `import_gold_ruleset.py` and `fixture_loader.py` continues to resolve `storage/rules/gold/
  data/*.json` correctly with zero code changes to that logic.
- **FR-003**: `engine/` MUST exclude every file confirmed (by import trace, not assumption) to
  belong to a different, superseded pipeline: the six `qc_engine/`-top-level ontology-extraction
  files (`apply_loan_profile.py`, `build_loan_profiles*.py` v2–v5, `eval_log.py`, `replay.py`,
  `yaml_executor.py`), the ~25 AMQ-workbook-direct `compiler/*.py` files other than
  `import_gold_ruleset.py`, and everything under `p0/ontology_extraction/`,
  `p0/eval_synth/`, `p0/eval_real/`, `p0/experiment_*/`, and the 20 dated
  `p0/compile_runs/run_NNN_*/` directories.
- **FR-004**: `engine/` MUST include the standing-gate validation harness
  (`verify_against_defects.py`, `defect_manifest.json`, the 5 labeled loan fixtures
  `loan_01.json`–`loan_05.json`, `fixture_loader.py`, `field_catalog.json`) so it can prove its
  own 25/25 defect-detection claim without depending on `p0/`.
- **FR-005**: `engine/` MUST include `mismo.py` (the MISMO 3.4 XML parser) even though today's
  Touchless-only bake-off doesn't exercise it, because it is a small, self-contained (stdlib-only),
  documented capability of the engine's three-source-of-truth model.
- **FR-006**: `engine/` MUST NOT include the Field & Precondition Coverage Gate
  (`p0/compile_runs/run_016_coverage_gate/build_and_run.py`) or its transitive dependencies
  (`ontology_extraction`, `build_loan_profiles_v3`, `fact_vocabulary`, `eval_log`) — confirmed
  entangled with the superseded pipeline this extraction is explicitly leaving behind. This gate
  continues to run against `p0/` only.
- **FR-007**: The one constant in the copied `import_gold_ruleset.py` that names a specific,
  dated bake-off run (`RUN_DIR = "compile_runs/bakeoff_gold_touchless_2026-07-31"`) MUST be
  renamed in the `engine/` copy to something that doesn't read as tied to one historical run
  (e.g. `compile_runs/default`) — this is the one deliberate code edit distinguishing the copy
  from `p0/`'s original.
- **FR-008**: `p0/`'s original files MUST remain byte-for-byte unmodified by this feature (this
  is a copy, never a move) — verified via `git diff` showing zero changes under `p0/` after the
  extraction.
- **FR-009**: `engine/` MUST include a new `README.md` (the one genuinely new authored file in
  this feature) documenting the actual three-command flow (adapt → compile+evaluate → verify),
  since `p0/README.md` describes an earlier, smaller, now-inaccurate shape of the project and
  copying it verbatim would mislead anyone using `engine/` as "the definitive official engine."

### Key Entities

- **`engine/qc_engine/`**: the core deterministic evaluator package — money/ratio math, the
  canonical loan model, the check/ruleset dataclasses, the field catalog, the hash-chained audit
  log, and the MISMO XML parser. Zero third-party dependencies (Python stdlib only).
- **`engine/qc_engine/compiler/import_gold_ruleset.py`**: the single compiler this copy carries —
  converts the gold ruleset (`storage/rules/gold/data/rules_compiled.json`, outside this copy,
  read by relative path) into runnable `Check`/`Ruleset` objects, and runs them against a loan
  fixture, producing verdict output.
- **`engine/qc_engine/adapters/touchless_adapter.py`**: converts a raw Touchless loan payload
  (`loan_application.json` + `extracted_data*.json`) into the canonical fixture format the
  compiler's `main()` consumes.
- **`engine/fixtures/from_docs/`**: the 5 labeled synthetic loans + the 25-defect manifest +
  the verification script that proves the engine's defect-detection claim standalone.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `find engine -type f` matches the planned copy-set file list exactly — no
  unplanned extra files, none missing.
- **SC-002**: Running the three-command flow documented in `engine/README.md` end to end against
  the same real loan (`demo/touchless/loan_application.json` /
  `extracted_data_e59d57a9-...json`) produces the exact same verdict distribution as `p0/`'s
  current run: PASS 133, NEEDS_REVIEW 92, NOT_APPLICABLE 443, NOT_COMPILED 437.
- **SC-003**: `engine/fixtures/from_docs/verify_against_defects.py` reports 25/25 when run
  standalone, with no import path reaching into `p0/`.
- **SC-004**: `git status`/`git diff` after the extraction shows only new, untracked files under
  `engine/` — zero modifications under `p0/` (beyond the pre-existing loose-end resolution noted
  in Assumptions, which happens before the copy, not as part of it).
- **SC-005**: `p0/`'s own standing gates (`pytest p0/`; `p0/fixtures/from_docs/
  verify_against_defects.py`) report identical results after the extraction as before it (445
  passed / 3 skipped / 1 xfailed; 25/25) — proving this was genuinely additive, not disruptive.

## Assumptions

- This spec is tracked under `specs/021-standalone-qc-engine/` but implemented **on the existing
  `worktree-gold-ruleset-plan` branch (PR #7)**, not a new feature branch — Gordon's own framing
  ("before we merge *this* to main") places the engine extraction inside the same PR already in
  flight, not a separate one. The spec-directory number (`021`) was computed the normal Spec-Kit
  way (next available after scanning local `specs/` and remote branch refs, which already
  correctly detected `main`'s merged `020-touchless-api-integration` and skipped past it) — only
  the *branch-creation* side effect of the standard `/speckit.specify` flow was skipped, to avoid
  fragmenting this work across two branches/PRs.
- `p0/fixtures/from_docs/loan_02.json`, `loan_03.json`, and `loan_05.json` had pre-existing,
  unrelated uncommitted edits (accidental citation-text truncation, unrelated to this feature)
  sitting in the working tree before this feature started. These were reverted to their
  last-committed state *before* the copy, so `engine/` inherits clean, correct fixture data and
  `p0/`'s own working tree returns to its last-known-good committed state.
- `storage/rules/gold/data/*.json` (the compiled gold ruleset) and `demo/touchless/*.json` (the
  sample loan payload) are existing, shared inputs this feature reads by relative path — they are
  explicitly *not* duplicated into `engine/`, consistent with "only extract the required files."
- No third-party/PyPI dependencies are introduced — every file in the copy set is already
  confirmed stdlib-only.
- Maintaining `engine/` and `p0/` in sync going forward (if `p0/`'s core files change later) is
  out of scope for this feature — a one-time extraction, not an ongoing sync mechanism.
