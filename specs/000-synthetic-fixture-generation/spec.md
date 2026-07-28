# Feature Specification: Synthetic Loan Fixture Generation (Document-Derived, Dev-Mode)

**Feature Branch**: `000-synthetic-fixture-generation`
**Created**: 2026-07-15
**Status**: Implemented (2026-07-15–16 — all 40 tasks; 25/25 defect gate passes; header corrected from stale "Draft" 2026-07-26, spec audit)
**Input**: User description: "Convert the 5 synthetic loans in demo/syn/loan 0{1-5}/ into the field-extracted fixture format the QC engine consumes — generated once, offline, dev-mode only, accurate enough that downstream engine/eval work can trust it. See output/PLAN-synthetic-loan-extraction.md and output/architecture-diagram.html for the working plan and diagram this formalizes."

**Governs**: `output/PLAN-synthetic-loan-extraction.md` (the working plan this spec formalizes), `output/architecture-diagram.html` (the accompanying diagram).
**Depends on**: `001a-field-catalog` (this feature extends its catalog), `001b-source-envelope-and-inbound-contracts` (output conforms to the pinned `SourceEnvelope`/Touchless-inbound-contract shape — nothing new invented).
**Foundation this builds on** (proven, not re-specced): `p0/qc_engine/mismo.py` (existing deterministic MISMO 3.4 parser), `p0/eval_synth/taxonomy.json` (existing real-rule archetype classification, derived from the actual 7,398-condition AMQ workbook), `p0/fixtures/golden.py` + `p0/eval_synth/generator.py` (existing hand-authored fixture convention this extends alongside, not replaces).

**Numbering note**: assigned `000` rather than the next sequential slot (`004`) deliberately — `004` is already reserved on `output/ROADMAP.md` for `004-loan-disposition`, an unrelated, already-planned feature. This work is dev/test tooling outside the roadmap's dependency-ordered numbered arc (see Assumptions), not a roadmap feature competing for that slot.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Engine and eval tests run against document-derived fixtures, not only hand-typed ones (Priority: P1)

Today, every test fixture in the engine (`p0/fixtures/golden.py`, `p0/eval_synth/generator.py`) is a hand-authored Python object — nothing in the codebase has ever turned a real document into the engine's input shape. The 5 synthetic loans sitting in `demo/syn/` were purpose-built with known defects and are unused. This story delivers document-derived fixtures for all 5 loans so the engine and eval harness can be exercised against something closer to what production extraction will actually hand it, not just what a person happened to imagine.

**Why this priority**: Everything else in this feature (accuracy verification, catalog grounding, citations) only matters once real fixtures exist to apply it to.

**Independent Test**: Can be fully tested by loading each of the 5 generated fixtures through the existing `CanonicalLoan`/`SourceValue` model with zero code changes, and confirming all 5 load without error.

**Acceptance Scenarios**:

1. **Given** the 5 synthetic loan folders (documents + MISMO XML), **When** fixture generation runs, **Then** exactly 5 `CanonicalLoan`-shaped fixtures are produced, each populated only from its own loan's documents (no cross-loan data leakage).
2. **Given** a generated fixture, **When** it is loaded by the existing eval scorer, **Then** it loads and scores with no changes to the scorer itself.

---

### User Story 2 - A fixture is never trusted until it proves itself against known answers (Priority: P1)

Each synthetic loan's MISMO export carries 5 embedded, precisely-documented defects (25 total across all 5 loans) — a ground-truth answer key built into the fixtures themselves, not something a human has to adjudicate. This story makes that answer key a hard, mechanical gate: extraction is not considered trustworthy, and is not wired to anything downstream, until it reproduces every one of the 25 documented defects exactly.

**Why this priority**: This is the actual "must be accurate or downstream cannot be trusted" requirement — without it, this feature just produces plausible-looking data with no more credibility than the hand-authored fixtures it's meant to improve on.

**Independent Test**: Can be fully tested by running the verification step against the 5 generated fixtures and confirming it reports all 25 known defects reproduced, with a non-zero/incomplete result treated as a failure, not a warning.

**Acceptance Scenarios**:

1. **Given** a generated fixture for a loan with a documented defect (e.g., an undisclosed liability amount), **When** the verification step runs, **Then** the fixture's extracted values reproduce that exact documented discrepancy between the document side and the system side.
2. **Given** any fixture where even one of its loan's 5 documented defects fails to reproduce exactly, **When** verification completes, **Then** that fixture is flagged as not trustworthy and MUST NOT be wired into downstream engine or eval tests.

---

### User Story 3 - The field vocabulary is grounded in real rules, not invented from convenience (Priority: P2)

The existing 7-field seed catalog covers none of the 25 known defects. Rather than adding whatever fields happen to make these 5 files work, each candidate field is checked against the real rule taxonomy (`p0/eval_synth/taxonomy.json`, derived from the actual AMQ rule workbook) so the catalog's growth has value beyond this one batch of loans.

**Why this priority**: Lower than US1/US2 because the fixtures can exist and be verified against the current catalog fields already; this story is about the catalog's long-term integrity, not this batch's immediate function.

**Independent Test**: Can be fully tested by reviewing the new catalog entries and confirming each cites the specific real-rule archetype/condition that justifies its existence.

**Acceptance Scenarios**:

1. **Given** a candidate new field, **When** it is proposed for the catalog, **Then** it is traceable to a specific archetype/category in the real-rule taxonomy, not only to a document in these 5 loans.
2. **Given** the extended catalog, **When** it is loaded by the engine's existing referential-integrity validator, **Then** it passes with zero regressions against prior verdicts.

---

### User Story 4 - Every extracted value is traceable to exactly where it came from (Priority: P3)

Every document-sourced field value carries a citation (document name, page, exact text) — the same audit standard the eventual Touchless contract must meet, so a human (or a future confidence-gated check) can always answer "why does the engine believe this."

**Why this priority**: Important for audit credibility, but the fixtures are still usable for correctness testing (US1/US2) even before every citation is polished.

**Independent Test**: Can be fully tested by sampling generated fixtures and confirming every document-sourced field has a non-empty citation with document name, page number, and source text.

**Acceptance Scenarios**:

1. **Given** a field extracted from a document, **When** the fixture is generated, **Then** its citation identifies the exact source document, page, and text segment.
2. **Given** a field sourced from a system-of-record (e.g., an external case-number lookup) rather than a document, **When** the fixture is generated, **Then** it carries a lightweight source-provenance note appropriate to a non-document origin, not a fabricated page citation.

---

### Edge Cases

- What happens when a rule condition requires comparing two *document-side* values against each other (e.g., the loan application vs. the employment verification), rather than document-vs-system? Today's model only supports document-vs-system comparison. This is **out of scope for this feature** — it is surfaced explicitly as an open question for whoever specifies the reconcile check-kind feature, not silently forced into the existing shape.
- What happens when a document doesn't contain a field the catalog expects? The field resolves to a missing/absent state consistent with the engine's existing behavior — it is never fabricated or defaulted to a plausible-looking value.
- What happens if a fixture reproduces 24 of 25 known defects but not the 25th? The whole fixture set for that batch is treated as not yet trustworthy; partial credit does not unlock downstream use.
- What happens when a field could plausibly be extracted by more than one method with different results? The discrepancy must surface as a build-time failure to resolve, not a silent pick of one value.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST produce one `CanonicalLoan`-shaped fixture per synthetic loan (5 total), each populated only from that loan's own documents and MISMO export.
- **FR-002**: Every document-sourced field value MUST carry a citation identifying the source document, page, and the exact text it was read from.
- **FR-003**: Outputs MUST be presented and used strictly as dev/test fixtures — never described, documented, or wired as the Touchless production extractor (Principle IV — extraction remains assumed periphery, not built here).
- **FR-004**: Every new field-catalog entry introduced by this feature MUST be traceable to a specific condition/archetype in the real rule taxonomy — fields justified only by convenience for these 5 loans MUST NOT be added.
- **FR-005**: System MUST verify, for all 5 loans, that all 25 embedded known defects are reproduced exactly by the generated fixtures — 100% required, zero tolerance for a silent miss.
- **FR-006**: A fixture set that fails FR-005's verification MUST NOT be wired into any downstream engine or eval test run.
- **FR-007**: System MUST NOT model a document-vs-document comparison as if it were a document-vs-system comparison; any case requiring this MUST be surfaced as an explicit open question rather than resolved silently.
- **FR-008**: Generated fixtures MUST be consumable by the existing eval scorer (`p0/eval_synth`) without modification to the scorer itself.
- **FR-009**: Extending the field catalog MUST pass the catalog's own existing validation (field-name uniqueness, referential integrity, zero regression against prior engine verdicts) — this feature receives no governance exemption because its own build process is lightweight.
- **FR-010**: System MUST NOT require building the Touchless extractor or the LOS/MISMO connector themselves — only the one-time, offline generation of fixtures from the 5 already-available synthetic loans.

### Key Entities

- **Synthetic Loan Package**: one of 5 folders of synthetic closing documents plus one MISMO export, each carrying 5 known, pre-documented defects (25 total).
- **Extracted Field Fixture**: a document-and-system-derived value for one canonical field on one loan, carrying its source citation and confidence.
- **Known Defect**: a pre-documented, constructed mismatch or missing-item condition embedded in a loan package, used as the ground-truth check for extraction accuracy.
- **Rule-Grounded Catalog Entry**: a field-catalog entry whose existence is justified by a specific real rule condition/archetype, not by convenience.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% (25 of 25) of the known, embedded defects across the 5 synthetic loans are reproduced exactly by the generated fixtures.
- **SC-002**: 100% of document-sourced field values in the output carry a non-empty citation (document name, page, text segment).
- **SC-003**: 100% of newly added field-catalog entries are documented with the specific real-rule archetype/condition that justifies them.
- **SC-004**: The existing eval scorer and golden-fixture test suite continue to pass unmodified after the new fixtures are introduced — zero regression.
- **SC-005**: Zero instances, in the shipped output, of a document-vs-document comparison silently modeled as document-vs-system.

## Assumptions

- The 5 synthetic loan packages in `demo/syn/` are the entire input population for this feature; broader or real-loan extraction remains out of scope (Blockers 1/2, Principle IV).
- This is dev/test tooling, not a roadmap-numbered product feature — it does not claim to be, replace, or preempt the eventual Touchless extraction contract, and is intentionally numbered `000` rather than consuming the roadmap's next sequential slot.
- The document-vs-document comparison question raised in Edge Cases is explicitly deferred to whichever feature specifies the reconcile check-kind (`003c`); this feature only surfaces it, it does not resolve it. *(Since resolved: `003c` declined it (its FR-005); **`003d` built it** — `agree_doc_categorical`/`agree_doc_numeric`, all 25 known defects now wired, `test_wired_checks_catch_all_25_known_defects`. Note added 2026-07-26, spec audit.)*
- Field-catalog changes ride on the existing `001a` governance (referential integrity + zero-regression); no new gate is invented here.
- No git feature branch is created for this spec, consistent with how `001a`/`001b`/`002a`/`002b`/`003a`/`003b` were built in this shared workspace repository (this repo is a subdirectory of a much larger mono-repo with unrelated concurrent work; a dedicated feature branch per spec is not this project's established convention).
