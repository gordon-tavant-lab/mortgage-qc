# Specification Quality Checklist: Eval Harness as Promotion Gate

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-07-27
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs) — *note: class/function/file
  references (`Check.kind`, `SCORERS`, `generator.py`, `field_catalog.json`) are cited, matching
  this project's established house convention already used in `000`/`003a`/`003b`/`003c`/`004`'s own
  spec.md files — these specs are internal engineering artifacts governed by a technical
  constitution, not generic stakeholder documents. Treated as consistent with precedent, not a
  defect.*
- [x] Focused on user value and business needs — the "user" here is the constitution's own eval
  discipline (Principle III) and the engine slices (`003a`/`b`/`c`/`d`) it must keep pace with; the
  spec frames every FR around what breaks (a false-auto-clear promoted, a check with no proof) if
  the feature doesn't exist.
- [x] Written for non-technical stakeholders — *within this project's own convention, see note above*
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain — every open question found during research (what
  triggers a "ruleset version bump," what CI vendor to target) is resolved as an explicit Assumption
  or Edge Case with a stated rationale, not left as an unresolved marker.
- [x] Requirements are testable and unambiguous — FR-001–004 name the exact 6 check kinds and the
  exact precondition/two-field mechanics; FR-006's hard-block behavior specifies the exact exit-code
  and artifact-field contract.
- [x] Success criteria are measurable — SC-001–006 each name a specific, verifiable number or
  test-constructed scenario (6 kinds covered, a named injected-defect test, a named injected-flip
  test), not a vague "works correctly."
- [x] Success criteria are technology-agnostic (no implementation details) — *same house-convention
  note as above applies to entity/field-name references*
- [x] All acceptance scenarios are defined — every user story (US1–US5) carries Given/When/Then
  scenarios directly traceable to at least one FR.
- [x] Edge cases are identified — 6 edge cases cover referential-integrity boundaries, the `date`
  data-type gap, multi-check composition ambiguity, GOLDEN-flip-is-not-always-regression, the
  undefined version-bump trigger, and absent CI infrastructure.
- [x] Scope is clearly bounded — FR-011/012/013 explicitly name what this feature does not do
  (runtime LLM calls, real-loan acquisition/extraction realism, modifying the `002a` spike file).
- [x] Dependencies and assumptions identified — depends-on (`001a`, `003a`) and does-not-gate
  (`002a`) are both stated with the roadmap's own dependency-knot-fix rationale; 6 Assumptions each
  name what's deliberately left unsolved and why.

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria — every FR maps to at least one
  Acceptance Scenario and at least one Success Criterion.
- [x] User scenarios cover primary flows — generalized construction (US1), the hard safety block
  (US2), the three-tier reporting split (US3), invariant generalization (US4), and real-loan
  readiness (US5) — matching the roadmap's own three named scope items plus the v0.6 amendment.
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification — *see house-convention note above*

## Notes

- This spec's single largest risk (see spec.md's own Risks section, HIGH severity) is that the hard
  block it builds has no real trigger event yet, since `Ruleset.version` is hardcoded to `1`
  everywhere in the codebase today (confirmed by direct grep, not assumed). This is surfaced
  explicitly rather than papered over — the mitigation (ship the gate as a directly-callable script
  now, let a future promotion workflow invoke it later) is a deliberate, named scope boundary, not an
  oversight.
- Confirmed by direct code reading before this checklist was written: `score_drafts.py`'s `SCORERS`
  dict covers 4 of the engine's 6 live check kinds (`agree_doc_categorical`/`agree_doc_numeric`,
  added by `003d`, are not covered) — this gap is what FR-001/004 and SC-001 explicitly close, not a
  gap discovered after the fact during implementation.
- Ready for `/speckit.plan` (already produced, `plan.md`) and `/speckit.tasks` (already produced,
  `tasks.md`) — per this project's established `speckit-*` workflow convention, all three artifacts
  were authored together in this session against the same direct code-reading pass.
