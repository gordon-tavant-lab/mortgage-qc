# FIBO Ontology Adoption Decision

| | |
|---|---|
| **Date** | 2026-07-28 |
| **Status** | Accepted |
| **Spec** | `specs/015-loan-data-capture-and-gating-fix/spec.md` |
| **Supersedes (in part)** | `002g-canonical-loan-fact-vocabulary`'s original "borrow the vocabulary discipline, not the reasoner" framing — same principle, now made a permanent, named policy instead of a one-off borrowing |
| **Governs** | `CLAUDE.md` (Non-Negotiable #1), `output/ROADMAP.md` (`016-fibo-ontology-alignment`) |

## Context

FIBO (the Financial Industry Business Ontology) is a public, standards-body-maintained
ontology for financial concepts, including a `LOAN`/`RealEstateLoans` module covering
things like loan program, investor type, occupancy, property type, and income
classification — the same kind of gating dimensions this project's field catalog and
precondition-ontology pipeline (`p0/ontology_extraction/`, spec `002f`) already work with.

FIBO came up mid-investigation of spec `015`, not as a planned research task. That spec's
Phase 0 built a Field & Precondition Coverage Gate to find gaps the size of
`loan_program_1003` (a fact the loan's own 1003 states plainly, but that was never
extracted) before they surface by accident in a demo. Gordon asked to evaluate FIBO as a
third, independent cross-check for that gate — first as a one-off "first pass," then,
after discussion, as the **permanent** framework this project authors new
fields/concepts against going forward. This project has already been informally
gesturing at FIBO-like naming (`loan_program`, `occupancy_type`) without ever deciding so
explicitly; this spec is that decision, made on the record.

## Decision

Adopt FIBO as a **naming/vocabulary-alignment reference, not a runtime dependency**:

- When authoring a new field in `field_catalog.json` or a new fact in the canonical
  loan-fact vocabulary (`002g`), check whether an existing FIBO `LOAN`/`RealEstateLoans`
  concept already names the thing being added, and prefer that name (or a clear,
  documented adaptation of it) over inventing a fresh one.
- FIBO is consulted as a **public schema reference at authoring time** — there is no
  ontology import, no ontology file checked into the repo, no library dependency added.
  Spec `015`'s coverage gate curates a small, hand-picked list of relevant FIBO concepts
  (loan program/investor type, occupancy, property type, income type) as a third
  validation cross-check, alongside catalog-entry and extraction/derivation-path checks —
  not a full ontology import.
- **Explicit, permanent boundary:** no OWL/RDF reasoner, no SPARQL, no ontology-inference
  machinery of any kind enters `engine.py` or any part of the runtime evaluation path.
  `engine.py` stays flat, deterministic Python, exactly as Non-Negotiable #1 requires.
  This decision governs *naming*, never *evaluation*.

## Consequences

**What this means going forward:** anyone adding a new field to `field_catalog.json` (or a
new fact to the `002g` canonical-fact registry) should check FIBO's public schema for an
existing, analogous concept name before inventing one from scratch. Where a recognized
FIBO name exists, use it (or a documented, minimal adaptation); where it doesn't, name the
field on the project's own existing conventions as before — FIBO is a cross-check, not a
gate that blocks authoring.

**What this explicitly does NOT mean:**
- No obligation to model every existing or new field as a FIBO concept — most of this
  project's fields (extraction metadata, citation shapes, internal derived flags) have no
  FIBO analogue and aren't expected to.
- No new tooling, library, or runtime dependency. Nothing changes in `engine.py`,
  `requirements.txt`, or the deploy/runtime path.
- No obligation to migrate the existing ~380-field catalog or ~4,837 compiled checks onto
  FIBO concepts now — that is explicitly out of scope for spec `015` and is tracked as a
  separate, future, not-yet-specced effort (`output/ROADMAP.md`, `016-fibo-ontology-alignment`).

## Alternatives Considered

- **Full ontology import + OWL/RDF reasoner wired into `engine.py`.** Rejected. This would
  turn the engine from a simple, auditable, deterministic evaluator into a semantic-web
  inference engine — a direct violation of Non-Negotiable #1 (determinism, "same loan →
  same verdict," a regulator must be able to follow the exact calculation) and Non-Negotiable
  #2 (build the core, don't boil the ocean). `002g` already declined this path once, for the
  same reason; this decision reaffirms it rather than revisiting it.
- **No formal framework at all — keep naming ad hoc.** Rejected. This project's own naming
  had already drifted informally toward FIBO-like terms without anyone deciding so, and this
  same session's investigation surfaced two real fields (`loan_program`, and the gap that
  became `income_type_used_for_qualification`) whose ambiguity was a direct product of no
  shared naming discipline. Ad hoc naming is what let a real, documented loan fact
  (loan 01's own "Loan Program: Conventional — Fannie Mae") go unextracted long enough to
  surface by accident during demo prep, not by design.
