# Requirements Checklist: Derive the Remaining Gating Dimensions (Occupancy + Loan Program)

**Purpose**: Validate `spec.md`'s requirements are complete, unambiguous, testable, and honestly
scoped before `/speckit.plan`/`/speckit.tasks` work is trusted — mirrors the rigor `002g`/`010a` both
applied to their own requirements before implementation began.
**Created**: 2026-07-27
**Feature**: [spec.md](../spec.md)

## Grounding & Evidence

- [ ] CHK001 Every claim in "Why this feature exists" traces to a specific file:line or a direct
      `grep`/inspection result, not an assumption (spec.md Gap 1, Gap 2)
- [ ] CHK002 The real anchor check (`insurance-docs-support-owner-occupancy`) is confirmed to exist,
      by its real `field_name`, in the actual compiled ruleset artifact — not a hypothetical/invented
      check id
- [ ] CHK003 The 5 real AMQ rows cited for the anchor check's family (`pc-retail-02837`–`02841`) are
      confirmed to exist, with the exact defect text quoted, in the real extraction fixture
- [ ] CHK004 The `loan_program` citability table (loan_01–05, Why This Feature Exists) is confirmed
      against each real fixture's actual `fields` dict, not inferred from the fixture's `loan_type`
      label alone

## Requirement Completeness

- [ ] CHK005 Every FR (FR-001–FR-010) states a single, unambiguous, testable behavior — no FR bundles
      two independently-verifiable claims under one ID
- [ ] CHK006 Every FR that introduces a new artifact (vocabulary version, catalog entry, derived-fact
      module, wiring function) names the exact file path it lands in
- [ ] CHK007 The "never guess" discipline (FR-002, FR-003) is stated with the same rigor as
      `build_loan_profiles_v2.py`'s existing `derive_loan_transaction_type`/`derive_appraisal_in_file`
      precedent — an explicit, enumerated map, not an open-ended fuzzy match
- [ ] CHK008 FR-006's "never overwrite an existing `loan.fields` entry" guarantee is stated as a MUST,
      not a SHOULD, given the Non-Negotiable #1 (document-is-truth) risk a violation would create
- [ ] CHK009 FR-010's non-interference with `010a`'s existing program-applicability tag on the same
      compiled check is explicit, not left to be assumed compatible

## Coverage Against the Task's Explicit Scope

- [ ] CHK010 `occupancy_type` derivation (User Story 1) is present and grounded in a real, already-
      extracted field (`occupancy_1003`)
- [ ] CHK011 `loan_program` derivation (User Story 3) is present and correctly reuses `010a`'s existing
      program token set rather than inventing a new one
- [ ] CHK012 At least one real, already-compiled check is wired end-to-end to gate on the new fact via
      `002e`'s `applies_if` mechanism (User Story 2) — not merely computed and left unconsumed, the
      exact "computed-and-ignored" failure mode named for the other 3 derived facts (`gift_funds_used`,
      `loan_transaction_type`, `appraisal_in_file`)
- [ ] CHK013 The 13 other 16-fact-vocabulary facts (income type, credit-report presence, DU components,
      LEP, etc.) are explicitly named as out of scope, with the reason (no direct extractable signal)
      pointing back to `build_loan_profiles_v2.py`'s own existing finding, not re-litigated here
- [ ] CHK014 `income-bucket` and `QC_Policy` — the two other dimensions `output/ROADMAP.md`'s 010b
      entry names — are explicitly acknowledged as a residual, not silently dropped from the roadmap
      entry's original scope

## Honesty of Disclosed Limitations

- [ ] CHK015 The fact that all 5 real fixtures are owner-occupied (no real second-home/investment
      fixture exists) is disclosed as a real data-diversity limit, not hidden behind a passing test
      suite that only exercises the owner-occupied path against real data
- [ ] CHK016 `loan_program`'s honest `underivable` result for loan_01 (ambiguity) and loan_04 (no
      signal) is disclosed as a genuine finding, with the two failure reasons kept distinct — not
      collapsed into one generic "unknown" bucket that would obscure which failure mode occurred
- [ ] CHK017 The inherited "third provenance kind" gap (a derived fact's `SourceValue.citation` stays
      `None`) is disclosed as inherited from `002g`, not silently resolved nor silently ignored
- [ ] CHK018 The pre-existing `gift_funds_used` catalog-entry inconsistency
      (`citation_required: true` never actually honored) is named as a pre-existing, undisclosed-until-
      now gap this spec does not fix, rather than either (a) silently repeating it in the 2 new entries
      or (b) silently fixing it as an unplanned scope-creep change

## Success Criteria Quality

- [ ] CHK019 Every SC (SC-001–SC-005) is measurable without subjective judgment (a specific value, a
      specific digest, a specific pass/fail count) — no SC relies on "looks correct" or "reasonable"
- [ ] CHK020 SC-005's cited baseline numbers (325 tests passing, harness digest
      `82175d076579e31a50971d8b20ea4b63848bea9f9b53c30dd96524071842e5ec`) are confirmed current as of
      this spec's writing (2026-07-27), not stale figures carried over from an earlier feature's spec

## Dependency & Sequencing Sanity

- [ ] CHK021 Every "Depends on" entry (010a, 001b, 002e, 002g) is confirmed already implemented, per
      `output/ROADMAP.md`'s own status markers, before this spec assumes their mechanisms are available
      to build on
- [ ] CHK022 No requirement in this spec asks `002e`'s engine-side `_eval_applies_if` or `catalog.py`'s
      `validate_referential_integrity()` to change shape — this spec is purely a new producer/consumer
      of those already-implemented mechanisms, confirmed by re-reading FR-006/FR-007/SC-004 against
      `002e`'s own spec

## Notes

- Check items off as completed: `[x]`
- Any item left unchecked at plan/tasks review time should be resolved — either the spec is amended,
  or the gap is explicitly re-confirmed as an accepted, disclosed limitation (matching this project's
  own "surface the tension, don't silently diverge" constitution mandate) before implementation starts.
