# Specification Quality Checklist: Real-Loan Distribution Eval

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-07-27
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs) — *note: class/function/file references
  (`score()`, `LabeledLoan`, `field_catalog.json`, `AuditLog.verify_chain()`, `{loan}-citations.json`)
  are cited, matching this project's established house convention already used in
  `000`/`003a`-`003c`/`004`/`005`'s own spec.md files — these are internal engineering artifacts
  governed by a technical constitution, not generic stakeholder documents. Treated as consistent with
  precedent, not a defect.*
- [x] Focused on user value and business needs — the "user" here is the constitution's own Principle
  III (eval decomposition's third, real-loan-only question) and the pilot exit criterion; every FR is
  framed around what the roadmap's own accuracy/audit claims cannot honestly assert without this
  feature (a directional 6-synthetic-loan accuracy number, an audit chain proven only against
  synthetic citations, a reasoned-not-measured cost figure).
- [x] Written for non-technical stakeholders — *within this project's own convention, see note above*
- [x] All mandatory sections completed (User Scenarios, Requirements, Key Entities, Success Criteria,
  Assumptions, Risks)

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain — every open question found during research (whether
  loan acquisition is genuinely still external, whether the field-mapping shape will diverge, what
  happens if zero expert labels ever arrive) is resolved as an explicit Assumption, Edge Case, or Risk
  with a stated rationale, not left as an unresolved marker.
- [x] Requirements are testable and unambiguous — FR-001-004 name the exact bundle files and mapping
  behavior; FR-009-011 specify the exact conditional (labeled vs. `BLOCKED`) behavior; FR-012 specifies
  the exact PII-exclusion mechanism (gitignore-excluded local path OR redaction before any git-tracked
  write).
- [x] Success criteria are measurable — SC-001-007 each name a specific, verifiable check (3/3 loans
  convert with zero crashes; `verify_chain()` True then False under tamper; ≥2 examiner-trace reports;
  a zero-PII scan result; a `BLOCKED`-or-real-numbers report; a measured, not reasoned, cost figure;
  zero test-suite regression) — none is a vague "works correctly."
- [x] Success criteria are technology-agnostic (no implementation details) — *same house-convention
  note as above applies to entity/field-name references*
- [x] All acceptance scenarios are defined — every user story (US1-US4) carries Given/When/Then
  scenarios directly traceable to at least one FR.
- [x] Edge cases are identified — 6 edge cases cover unresolved field-mapping references, partial-label
  scoring, third-party QC-document disagreement, PII-touching artifacts, zero-label G3 rerun, and
  document-set mismatch between real bundles and the synthetic-derived field catalog.
- [x] Scope is clearly bounded — FR-013/014 explicitly name what this feature does not do (real-loan
  acquisition — confirmed already done by direct S3 inspection, not merely deferred; expert-label
  authoring, G1; modifying `generator.py`/`engine.py`/`audit.py`'s own logic).
- [x] Dependencies and assumptions identified — depends-on (`005`, `007`, `011`) is stated with each
  dependency's exact role (additional scorer source; already-proven-mechanism-to-validate;
  concurrently-specced corpus-shape peer); 6 Assumptions each name what's deliberately left open and
  why, including the corrected "loans are already acquired, only labels are external" framing.

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria — every FR maps to at least one
  Acceptance Scenario and at least one Success Criterion.
- [x] User scenarios cover primary flows — the ingestion adapter (US1), the mock-audit exit criterion
  (US2), the G3 bake-off re-run + real cost measurement (US3), and the shared-corpus integration
  boundary with `011` (US4) — matching all three of the roadmap's named scope items plus the one
  cross-feature integrity concern this session's concurrent specs (`005`/`011`) introduce.
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification — *see house-convention note above*

## Notes

- This spec's single largest departure from a literal reading of `output/ROADMAP.md` §012 is also its
  most load-bearing finding: direct S3 inspection this session (`aws s3 ls
  s3://mortgage-qc-extraction/results/ --profile gordon-chan`) confirmed the 3 real loans are **already
  acquired**, with full Touchless-shaped extraction bundles already in hand — contradicting the
  roadmap's implicit "G1 real labeled loans" framing that reads as if the loans themselves are the
  external blocker. The spec corrects this precisely rather than silently inheriting the coarser
  framing: acquisition is done; expert-adjudicated verdict *labels* are the genuinely remaining
  external dependency. This distinction changes what this feature can ship independent of Kayla/SME
  availability (the adapter, the audit-trace proof, the cost measurement — all label-independent) vs.
  what stays genuinely gated (the accuracy/false-auto-clear comparison, US3's D2 axis).
- The PII risk (FR-012, SC-004) is flagged as this spec's highest-severity risk because it is a new
  class of exposure no prior spec in this repository had to handle — confirmed directly (not assumed)
  by inspecting real field values in `301224293-ulad.json`/`301224293-citations.json` during this
  session's own research, and cross-checked against a sibling project's (`demo-sites/
  dynamic-mortgage-qc`) own documented precedent of building a synthetic stand-in specifically to avoid
  committing the same class of real PII. Reviewers should treat FR-012/SC-004 as non-negotiable gates,
  not nice-to-haves, before this feature's plan proceeds to implementation.
- A secondary, non-obvious finding worth flagging for planning: each real loan's closed-file bundle
  already contains a real third-party post-closing QC/audit report (Snapdocs, DUAL AUS, FraudGuard,
  etc.), classified but not yet field-extracted (`consolidated/qcchecklist.json`'s `"fields": {}`
  instances). FR-006 scopes building the extraction pattern for these documents as a `SHOULD`, not a
  `MUST` — reviewers should confirm this priority level is right given it materially cheapens the G1
  labeling ask, rather than assuming it's a nice-to-have that can slip indefinitely.
