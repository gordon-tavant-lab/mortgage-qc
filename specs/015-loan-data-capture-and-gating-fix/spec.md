# Feature Specification: Loan Data-Capture & Precondition-Gating Fix (+ FIBO Alignment)

**Feature Branch**: `015-loan-data-capture-and-gating-fix`
**Created**: 2026-07-28
**Status**: Draft — approved for implementation, not yet built

**Input**: Gordon ran a real, comprehensive-rulebook QC pass for loan 01
(`result/qc_results/loan_01_all.json`, via `p0/compile_runs/run_015_loan_01_comprehensive_qc/build_and_run.py`)
to prep for a same-day demo. He caught, from a screenshot of loan 01's own 1003 form, that it
explicitly states **"Loan Program: Conventional — Fannie Mae"** — yet the QC result treated loan 01's
program as `AMBIGUOUS` for every Fannie/Freddie-tagged check. He also flagged the previously-documented
"predicate checks fire FAIL on missing data" caveat as something needing a real fix, not just a verbal
caveat, "for a realistic run." Rather than patch the one instance, Gordon asked to (1) use the
project's own existing rule-ontology-parsing logic (`p0/ontology_extraction/`, spec `002f`) to
systematically discover what else is missing, (2) confirm whether the loan-context precondition system
he remembered ("we ran a quick LLM context check on the loan before running the rules") actually
exists and is wired in, and (3) address the root cause so this class of gap stops being discovered by
accident. Mid-investigation he also asked to evaluate and adopt FIBO (Financial Industry Business
Ontology) as a third, independent reference — first as a "first pass" cross-check, then, after
discussion, as the **permanent** framework this project authors new fields/concepts against going
forward.

**Governs**: `output/ROADMAP.md` (new entry), `CLAUDE.md` (new architecture-decision section on FIBO,
superseding part of `002g`'s original "vocabulary not reasoner" framing).
**Depends on**: `002f-precondition-ontology-layer` (the `ontology_extraction` pipeline this spec
discovers is only partially invoked), `002g-canonical-loan-fact-vocabulary` (the fact-vocabulary
sign-off mechanism Phase B's taxonomy registrations use), `003a-engine-predicate-checks` (the
`engine.py` predicate branch this spec fixes), `010a`/`010b` (`program_gating.py`, `build_loan_profiles_v3.py`
— both touched here), `000-synthetic-fixture-generation` (the fixture-regeneration + 25/25 defect gate
this spec's fixes must keep passing).

---

## Why this feature exists

A demo-prep QC run for loan 01 surfaced two real, user-visible correctness problems, and investigating
them surfaced a third, systemic one:

1. **Loan 01's own document plainly states its GSE ("Fannie Mae"), but the QC result couldn't use
   that fact** — `program_gating.py` reported `AMBIGUOUS` for every Fannie/Freddie-tagged check
   because that fact was never extracted into structured data, and (a deeper wiring gap found during
   investigation) even if it had been, `program_gating.py::applies_to()` never reads the derived fact
   at all — only an informal, hardcoded `loan_type` string.
2. **The engine's `predicate`/`is_true` check kind treats "we have no data" the same as "confirmed
   false,"** producing a FAIL. Measured directly against loan 01's real comprehensive-ruleset run:
   **82% of all 1,643 FAILs are this exact artifact** — not real defects, a labeling bug. This is the
   dominant reason a raw run looks "confidently wrong" rather than realistically informative.
3. **The root cause is systemic, not two isolated bugs**: this project has two systems — document
   extraction (`doc_patterns/*.json`+`field_catalog.json`) and the precondition-ontology pipeline
   (`p0/ontology_extraction/`, spec `002f`) — built at different times, never reconciled against each
   other. A gap in the second category (a contextual/gating fact, not a check-subject field) is
   invisible to every existing review mechanism this project already runs (`g-os-judge`, `g-core-eval`,
   `g-os-contrarian` included), because none of those tools know this specific cross-reference needs
   to hold. Direct investigation also confirmed the "loan context LLM check" Gordon remembered is real
   (`ontology_extraction`'s Layer 1/2) — but was never actually invoked for the rulebook used in
   today's run; only the free, structural Layer 0 pass was (confirmed at
   `p0/compile_runs/run_013_comprehensive_e2e_v6/build_and_run.py:154`).

Fixing today's two instances without fixing the reconciliation gap that let them hide guarantees a
fourth, fifth, and sixth instance surface the same way — by luck, one screenshot at a time. This spec
fixes the two immediate issues **and** builds the durable cross-reference check (Phase 0) that
prevents recurrence, plus documents FIBO's adoption as a permanent, independent reference for that
check going forward.

### Why an ontology/vocabulary change doesn't violate Non-Negotiable #1

Everything in this spec operates at compile-time or extraction-time, never at runtime evaluation:
- The extraction fixes (Phase A Issue 1, Phase B Step 6) add new *inputs* to the deterministic engine;
  they don't change how `engine.py::run()` evaluates a given input.
- The `engine.py` fix (Phase A Issue 2) changes *evaluation semantics* for one specific case
  (`predicate`/`is_true` + missing data) — this is the one genuine behavior change in this spec, and
  it is treated with the blast-radius care Non-Negotiable #1 demands (full regression, digest
  re-verification, 25/25 gate re-confirmation, conscious/documented test updates — never a blind
  patch).
- The FIBO adoption is explicitly scoped to the *vocabulary/concept-alignment* layer (what facts
  exist, what they're called) — not the runtime reasoner. `engine.py` stays the same flat,
  deterministic Python; no OWL/RDF/SPARQL machinery enters the evaluation path. This mirrors and
  extends `002g`'s already-accepted "borrow the vocabulary discipline, not the reasoner" precedent.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — A demo-ready QC run for loan 01 reflects reality, not a labeling bug (Priority: P1)

**Independent Test**: Run `p0/compile_runs/run_015_loan_01_comprehensive_qc/build_and_run.py` against
loan 01 after all Phase A fixes land. Confirm the result no longer reports `AMBIGUOUS` for
Fannie/Freddie-tagged checks (it should resolve to a definite Fannie Mae classification, citably
traced to the 1003's own "Loan Program" line), and confirm the FAIL count no longer includes checks
that were never given data to evaluate (those now resolve `NEEDS_REVIEW`/`APPLICABILITY_UNKNOWN`).

**Acceptance Scenarios**:
1. **Given** loan 01's real 1003 document states "Loan Program: Conventional — Fannie Mae", **When**
   fixtures are regenerated and the comprehensive QC run is re-executed, **Then** every
   Fannie-Mae-tagged check resolves a definite applicability verdict (not `AMBIGUOUS`), citably traced
   to the extracted `loan_program_1003` field.
2. **Given** a `predicate`/`is_true` check whose field was never populated for a loan (e.g. no
   accessory unit exists), **When** the engine evaluates it, **Then** the result is `NEEDS_REVIEW`/
   `APPLICABILITY_UNKNOWN`, never `FAIL` — while a `predicate`/`is_present` check on a genuinely
   missing required document still correctly resolves `FAIL` (unchanged).
3. **Given** loan 04's 1003 states "Freddie Mac Conventional Cash-Out Refi", **When** the same fixes
   are applied, **Then** loan 04 resolves a definite Freddie Mac classification, not `AMBIGUOUS`.

### User Story 2 — A durable gate catches this class of gap automatically, going forward (Priority: P1)

**Independent Test**: Run the new Field & Precondition Coverage Gate (Phase 0) against the current
repo state. Confirm it reports every field/dimension `ontology_extraction`'s real output says the
rulebook depends on, cross-referenced against catalog/extraction/population status and (for the
curated FIBO concept list) FIBO alignment — and that re-running it after Phase A/B's fixes land shows
the previously-reported gaps resolved.

**Acceptance Scenarios**:
1. **Given** the pre-fix repo state, **When** the coverage gate runs, **Then** it reports
   `loan_program_1003` and `income_type_used_for_qualification` (among others) as real gaps — the same
   ones found by hand this session — proving the gate is a faithful, automatable version of the manual
   process, not a weaker approximation.
2. **Given** the gate's report, **When** a future spec compiles a new ruleset or adds a new
   precondition dimension, **Then** running the gate again is the documented, required step before
   declaring that ruleset/ demo run ready — same standing as `verify_against_defects.py`'s 25/25 gate.

### User Story 3 — The loan-context/"LLM check" system Gordon remembered is confirmed, measured, and its gaps are made an explicit decision (Priority: P2)

**Independent Test**: Confirm directly (not assumed) which layers of `ontology_extraction` actually
ran for the rulebook in use, get the real attached/flagged/unconditional counts, and identify the
concrete, named taxonomies behind the largest flagged clusters.

**Acceptance Scenarios**:
1. **Given** `run_013`'s precondition-attachment log, **When** read directly, **Then** it shows the
   real counts (1,530 attached / 520 flagged / 1,153 unconditional out of 3,203) — not an estimate.
2. **Given** the flagged-reason clusters, **When** the two largest (Question 571085's loan-product
   taxonomy, ~165+ checks; Question 570606's asset-type taxonomy, ~102 checks) are traced to their
   real source rows, **Then** each has a concrete, actionable fix path (vocabulary sign-off vs. new
   extraction) — not left as an unexplained 520-item pile.
3. **Given** the remaining 1,153 fully-unconditional checks (Layer 1 candidates, never run), **When**
   this spec ships, **Then** the decision to run or defer Layer 1 is recorded explicitly (Phase C),
   not silently assumed either way.

### Edge Cases

- A loan whose 1003 states a GSE `program_gating.py` doesn't recognize (a new marker string) must fall
  back honestly to `AMBIGUOUS`, not silently misclassify — the fix is additive, not a replacement of
  the ambiguity semantics for genuinely no-signal loans.
- Regenerating fixtures must be provably additive-only (diffed field-by-field) — a fixture regeneration
  that changes any existing, already-verified field's value is a regression, not this spec's intent.
- The `engine.py` fix must not change `is_present`'s behavior in any way — that FAIL-on-missing is
  correct, intentional design (`p0/experiment_002a/RESULTS.md`) and must be regression-pinned, not just
  left untested.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A new, real `loan_program_1003` field MUST be extracted from the 1003's own "Loan
  Program" line for all 5 loans (uniform pipeline pass, not a per-loan carve-out), with a proper
  `field_catalog.json` entry (citation-required).
- **FR-002**: `build_loan_profiles_v3.py::derive_loan_program()` MUST use `loan_program_1003` to
  resolve loans 01 and 04 to their real GSE, without changing loans 02/03/05's existing (already
  correct) resolution path.
- **FR-003**: `program_gating.py::applies_to()` MUST prefer a loan's real derived `loan_program` fact
  over the informal `loan_type` string, falling back to the existing string-matching path only when
  the fact isn't present — additive, no signature change, no caller update required.
- **FR-004**: `engine.py`'s `predicate`/`is_true` branch MUST resolve `NEEDS_REVIEW`/
  `APPLICABILITY_UNKNOWN` (not `FAIL`) when the underlying field is `None`. `is_present`'s behavior
  MUST NOT change.
- **FR-005**: `run_015`'s applicability map MUST be swapped to a generation-matched file (0 `NO_TAG_FOUND`
  against the ruleset actually in use).
- **FR-006**: A new Field & Precondition Coverage Gate MUST exist as a re-runnable script/library,
  checking, for every dimension `ontology_extraction` structurally depends on (plus a curated FIBO
  concept list): catalog entry exists, extraction/derivation path exists, is actually populated for at
  least one real loan.
- **FR-007**: `income_type_used_for_qualification` MUST be extracted and derived (same shape as
  `loan_program_1003`), resolving self-employment-gated checks to `NOT_APPLICABLE` for W-2 borrowers
  instead of `APPLICABILITY_UNKNOWN`.
- **FR-008**: Question 571085's and 570606's flagged shared-answer-taxonomies MUST be registered
  through the existing `002g` fact-vocabulary sign-off mechanism, moving the affected checks from
  `FLAGGED` to properly `applies_if`-gated.
- **FR-009**: The FIBO adoption decision (permanent, going-forward framework for new fields/concepts;
  vocabulary/concept layer only, no reasoner machinery in `engine.py`) MUST be documented in `CLAUDE.md`
  and a new `output/FIBO-ONTOLOGY-ADOPTION-DECISION.md`, with a `ROADMAP.md` pointer to the separate,
  future full-migration spec.
- **FR-010**: `result/qc_results/loan_01_all.json` (and `loan_04_all.json` if produced) MUST carry an
  explicit `known_caveats` block surfacing the ruleset's real unsigned status and a summary of which
  fixes this run reflects — never left implicit.
- **FR-011**: Every test assertion changed by this spec MUST be a conscious, dated, documented change
  (explaining the deliberate behavior shift), never a blind "make it pass" edit.

### Key Entities

- **`loan_program_1003` / `income_type_used_for_qualification`** (new, raw, doc-extracted fields):
  citation-required, `expected_sources: ["doc"]`.
- **Field & Precondition Coverage Gate** (new): consumes `ontology_extraction.PipelineResult.proposals`
  + `field_catalog.json` + the 5 real fixtures + a curated FIBO concept list; produces a categorized
  gap report.
- **FIBO concept alignment list** (new, curated, not a full ontology import): the subset of FIBO
  `LOAN`/`RealEstateLoans` concepts relevant to this project's gating dimensions.

---

## Success Criteria *(mandatory)*

- **SC-001**: `pytest p0/tests -v` — zero unexpected failures at every phase boundary; every changed
  assertion has an explicit, dated comment.
- **SC-002**: `harness.py`'s digest is explicitly compared to the pre-fix baseline
  (`82175d076579e31a50971d8b20ea4b63848bea9f9b53c30dd96524071842e5ec`) after every phase — any change
  stated honestly, never silently absorbed.
- **SC-003**: `verify_against_defects.py` reports 25/25 after every fixture regeneration.
- **SC-004**: Loan 01 and loan 04 resolve a definite GSE classification (not `AMBIGUOUS`) for
  GSE-tagged checks in a real, regenerated `loan_01_all.json`/`loan_04_all.json`.
- **SC-005**: The ~1,351 ungated-predicate-missing-data FAILs no longer appear as FAILs in loan 01's
  regenerated result.
- **SC-006**: The coverage gate (Phase 0), run against the pre-fix state, reproduces
  `loan_program_1003` and `income_type_used_for_qualification` as real gaps — proving it's a faithful
  automation of the manual discovery process this spec started from.
- **SC-007**: `run_013`'s precondition-attachment summary shows `attached` rising and `flagged` falling
  by the amounts Phase B's Steps 7-8 predict.
- **SC-008**: `CLAUDE.md`, `output/FIBO-ONTOLOGY-ADOPTION-DECISION.md`, and `ROADMAP.md` all reflect
  the FIBO decision, dated and explicit about scope (vocabulary layer only).

---

## Assumptions

- Phase C (running Layer 1 against the remaining 1,153 fully-unconditional checks) is an explicit,
  separate go/no-go decision made once Phase 0's real numbers are in hand — not assumed either way by
  this spec.
- The full FIBO-to-catalog migration (all ~380 fields, ~4,837 unique checks) is out of scope for this
  spec — tracked as a separate, future spec per the `ROADMAP.md` entry this spec adds.
- Spec 014's committed decision-narrative numbers become stale once the `engine.py` fix lands; refreshing
  them is a follow-up step in this spec's plan, not a separate spec.

## Out of Scope

- Full FIBO ontology migration of the existing field catalog and compiled rulebook (future spec).
- Building a real OWL/RDF reasoner into `engine.py` (explicitly declined, per `002g`'s precedent).
- UI/export changes reflecting any of the above (unrelated surfaces).
