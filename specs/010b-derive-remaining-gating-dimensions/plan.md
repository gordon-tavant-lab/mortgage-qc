# Implementation Plan: Derive the Remaining Gating Dimensions (Occupancy + Loan Program)

**Branch**: `010b-derive-remaining-gating-dimensions` | **Date**: 2026-07-27 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/010b-derive-remaining-gating-dimensions/spec.md`

## Summary

Two additive changes, no evaluation-engine logic touched. **(1) Derive:** a new
`build_loan_profiles_v3.py` (new script per version, same precedent that produced v2 from v1) adds
`derive_occupancy_type` and `derive_loan_program` to the 3 derivations `build_loan_profiles_v2.py`
already has, plus a new `storage/fact_vocabulary` v7 registering both facts, plus 2 new
`field_catalog.json` entries so `applies_if`/`field_name` references to them resolve at load time.
**(2) Wire:** a new, small, tested `qc_engine` module promotes `run_013`'s one-off
`_panel_from_v2_profiles()` pattern (`SourceValue(doc=value)`, never overwriting a real extracted
field) into reusable code, and the real, already-compiled check `insurance-docs-support-owner-
occupancy` gains an `applies_if` gate on `occupancy_type == owner_occupied` — the first derived fact
in this project actually consumed by a real compiled check, not computed and ignored.

## Technical Context

**Language/Version**: Python 3.9-compatible (project-wide constraint).
**Primary Dependencies**: None new. Touches `p0/qc_engine/field_catalog.json` (2 new entries),
`storage/fact_vocabulary/` (new v7 file), `p0/qc_engine/build_loan_profiles_v3.py` (new script),
a new `p0/qc_engine/apply_loan_profile.py` module (new — the promoted wiring function), and one
compiled-check artifact (`result/rules/post_closing_only_ruleset.json`'s
`insurance-docs-support-owner-occupancy` entry gains `applies_if`). No changes to `engine.py`,
`model.py`, `ruleset.py`, or `reconcile.py` — this feature adds data (a profile version, 2 catalog
entries, 1 check's `applies_if`) and one small, additive wiring function; it does not change how the
engine evaluates any check once gating is resolved (the same "adds a gate, does not change kind-
dispatch logic" boundary `002e`'s own plan already established).
**Storage**: Flat files only, consistent with the rest of this project — `storage/fact_vocabulary/
v7.json` (new), `storage/loan_profiles/v3/loan_0{1..5}.json` (new, one per real fixture). No database.
**Testing**: New `p0/tests/test_loan_profiles_v3.py` (US1/US3: derivation correctness, mirroring
`test_loan_profiles_v2.py`'s existing shape — shipped-artifact assertions + rebuild-is-byte-identical)
and a new `p0/tests/test_occupancy_applicability_gating.py` (US2: the real compiled check's `applies_if`
gate, mirroring `test_conditional_applicability.py`'s existing constructed-`CanonicalLoan` pattern).
Extends `p0/qc_engine/catalog.py`'s existing test coverage implicitly (SC-004 exercises
`validate_referential_integrity()`, already tested generically by `002e`'s own suite — no new
referential-integrity *mechanism*, just 2 new resolvable field names to prove it against).
**Target Platform**: Local execution only, same as all of `p0/` — zero network calls, zero LLM calls
(FR-009); this is pure Python derivation logic run at profile-build time, same posture as
`build_loan_profiles_v2.py`.
**Project Type**: Small, additive derivation + wiring feature — two new small modules, one new data
file, two new catalog entries, one existing compiled-check artifact edited in place.
**Performance Goals**: N/A — derivation runs once per loan at profile-build time (5 real loans today);
the wiring function runs once per loan at loan-load time, O(facts) per loan, the same shape
`_panel_from_v2_profiles()` already proved acceptable in `run_013`.
**Constraints**: FR-002/FR-003's "never guess" discipline is the one safety-shaped constraint —
getting it wrong in the unsafe direction (inventing an occupancy or program value the fixture doesn't
literally state) reintroduces exactly the invented-number risk `CLAUDE.md` Non-Negotiable #1 (grounding
hardening) already named as the worst failure mode. FR-006's "never overwrite an existing `loan.fields`
entry" is the second safety-shaped constraint — a derived fact silently shadowing a genuinely extracted
field of the same name would collapse the document-is-truth invariant (Non-Negotiable/Principle V).
**Scale/Scope**: 5 real synthetic loan fixtures (unchanged scope from `002g`/`build_loan_profiles_v2`),
2 new facts (not the other 13/16 already found infeasible, and not `income-bucket`/`QC_Policy` —
spec.md Out of Scope), 1 real compiled check wired end-to-end. Not a full-rulebook occupancy-gating
sweep — that would require finding every real AMQ row referencing occupancy (43 rows found by grep,
spec.md Why This Feature Exists) and compiling `applies_if` for each; this spec proves the mechanism on
one, real, representative check, the same "prove the mechanism, not the full-rulebook sweep" scope
discipline `002g`/`002e` both already established for their own Phase 1s.

## Constitution Check

*GATE: evaluated against `.specify/memory/constitution.md` v1.1.1.*

| Principle | Status | Note |
|---|---|---|
| I — Determinism of the correct computation | PASS | Both derivations are pure string/dict lookups over already-extracted fields, at profile-build time — no float, no wall-clock, no network, no LLM. The wiring function (`apply_loan_profile.py`) is a pure dict-merge, O(facts) per loan. |
| II — Compile, then run | PASS | `applies_if` is set on the compiled check artifact once (FR-007), not re-derived per loan at evaluation time; the engine's existing `_eval_applies_if` (unmodified) evaluates it deterministically per loan, same as every other `applies_if` gate `002e` already established. |
| III — Eval is foundational | PASS | SC-001 through SC-005 make derivation correctness, the real-check gating proof, and the honest `underivable` cases all measurable, testable gates — not asserted by inspection. The `loan_program` honest-`underivable` finding (spec.md Why This Feature Exists) is itself a Principle III-aligned outcome: ground truth disclosed, not smoothed into a false 5-of-5 claim. |
| IV — Build the core, assume the periphery | PASS | This closes a real, named residual of `010a`'s own scope boundary (occupancy — "found, not yet gated on") and `output/ROADMAP.md`'s 010b entry — core rules-engine/gating work, not a periphery build. |
| V — Source independence | N/A this feature | This feature derives loan-side facts from the DOC-truth side only (`occupancy_1003`, `fha_case_number_1003`, etc. — all `truth`/doc-cited fields); it does not touch the doc-vs-system reconciliation mechanism at all. |
| VI — Configurable by non-technical users | PASS, with a named limitation | `FactVocabulary` v7's 2 new entries are signed, versioned data (same as v6's 16), inspectable by an SME the same way `002g`'s registry already is — but, same honest boundary `010a`'s own Constitution Check named for its lookup tables, the derivation *logic* (the literal-text maps in `build_loan_profiles_v3.py`) is Python code, not yet SME-editable config. Named here, not smoothed over — a future `009a`-family surfacing, not built in this spec. |
| VII — Configuration is authored data | PASS, with the same inherited, disclosed gap `002g` already named | The 2 new facts are versioned, signed vocabulary entries — consistent with the rest of the fact model. The one honest gap: a derived fact's *value* on a specific loan is written via `SourceValue(doc=value)` with `citation=None` (no real per-field citation), the exact "third provenance kind" gap `002g`'s own spec already flagged and deferred. This spec inherits, and does not resolve, that gap (spec.md Assumptions) — disclosed, not new. |

**Two named limitations (Principles VI, VII), not violations** — both mirror precedent this project's
own specs already established for the identical class of gap (`010a`'s lookup-table editability limit;
`002g`'s citation-provenance limit) rather than smoothing either over as resolved.

## Project Structure

### Documentation (this feature)

```text
specs/010b-derive-remaining-gating-dimensions/
├── spec.md
├── plan.md                  # This file
├── tasks.md                 # Phase 2 output
└── checklists/
    └── requirements.md
```

No `data-model.md` — the two new entities (`occupancy_type`/`loan_program` `CanonicalFact` rows) are
each a small, few-field addition to `002g`'s already-documented `FactVocabulary` shape, not a new
schema warranting a separate design document; documented directly in spec.md's Key Entities, per the
same precedent `010a`'s plan.md already set for its own small, additive entity.

### Source Code (repository root)

```text
storage/fact_vocabulary/
└── v7.json                     # NEW: v6's 16 facts + occupancy_type + loan_program (18 total),
                                # signed with the same honest placeholder every prior version uses.

storage/loan_profiles/v3/
├── loan_01.json                # NEW: 5 derivations (3 reused from v2 + 2 new); loan_program
├── loan_02.json                #   underivable for loan_01/loan_04 (spec.md Why This Feature
├── loan_03.json                #   Exists), occupancy_type=owner_occupied for all 5.
├── loan_04.json
└── loan_05.json

p0/qc_engine/
├── build_loan_profiles_v3.py    # NEW: derive_occupancy_type, derive_loan_program, reusing v2's
│                                #   3 existing derivations unchanged (imported, not copied — same
│                                #   "v2 reused v1's derive_gift_funds_used unchanged" precedent).
├── apply_loan_profile.py        # NEW: apply_derived_facts(loan, profile) -> CanonicalLoan --
│                                #   promotes run_013's one-off _panel_from_v2_profiles() pattern
│                                #   into tested, reusable qc_engine code (FR-006). Writes
│                                #   SourceValue(doc=value) into loan.fields ONLY when the field
│                                #   name is not already present (never shadows a real extracted
│                                #   field of the same name).
└── field_catalog.json           # MODIFIED: +2 entries (occupancy_type, loan_program;
                                 #   citation_required=False, confidence_required=False --
                                 #   declared honestly, FR-005).

result/rules/
└── post_closing_only_ruleset.json   # MODIFIED: insurance-docs-support-owner-occupancy's
                                     #   Check gains applies_if=[{"field_name": "occupancy_type",
                                     #   "operator": "==", "value": "owner_occupied"}] (FR-007).
                                     #   applicability.json's existing ["Fannie Mae"] program tag
                                     #   on the same check is left untouched (FR-010).

p0/tests/
├── test_loan_profiles_v3.py                     # NEW -- US1/US3 derivation coverage, mirroring
│                                                #   test_loan_profiles_v2.py's existing shape.
└── test_occupancy_applicability_gating.py        # NEW -- US2: the real compiled check's applies_if
                                                #   gate, mirroring test_conditional_applicability.py's
                                                #   constructed-CanonicalLoan pattern, plus a
                                                #   validate_referential_integrity() proof (SC-004).
```

**Structure Decision**: A new `build_loan_profiles_v3.py` (not an edit to v2) — the same "prior
version's generator behavior is pinned by committed tests and artifacts" precedent that made v2 a new
script rather than an edit to v1 (`build_loan_profiles_v2.py`'s own docstring). A new, separate
`apply_loan_profile.py` module (not folded into `build_loan_profiles_v3.py`) because it is a distinct
concern — *deriving* a fact's value (a batch, profile-build-time operation) versus *wiring* an already-
derived value onto a specific `CanonicalLoan` instance for evaluation (a per-loan-load-time operation,
the gap `run_013` proved ad hoc and this spec promotes into real code) — mirroring the same
single-purpose-module discipline `010a`'s own plan.md cited for keeping `program_gating.py` separate
from `compile_llm.py`.

## Complexity Tracking

*No entries — the two named limitations (Constitution Check, Principles VI/VII) are inherited, already-
disclosed scope boundaries from `010a` and `002g` respectively, not new violations requiring
justification.*


## Implementation Notes (2026-07-28)

All 37 tasks complete (Phases 1-6). Summary, for anyone reconciling this plan against what
actually shipped:

- **Files added**: `p0/qc_engine/build_loan_profiles_v3.py` (`derive_occupancy_type`,
  `derive_loan_program`, reusing v1's `derive_gift_funds_used` and v2's
  `derive_loan_transaction_type`/`derive_appraisal_in_file` unchanged), `p0/qc_engine/
  apply_loan_profile.py` (`apply_derived_facts`), `p0/tests/test_loan_profiles_v3.py` (11
  tests), `p0/tests/test_occupancy_applicability_gating.py` (10 tests) -- 21 new tests total,
  all green.
- **Files modified**: `storage/fact_vocabulary/v7.json` (new, 18 facts -- v6's 16 unchanged +
  `occupancy_type` + `loan_program`), `p0/qc_engine/field_catalog.json` (+3 entries:
  `occupancy_type`, `loan_program`, and `insurance_docs_support_owner_occupancy` -- the last
  one a necessary addition beyond FR-005's original 2, found while proving SC-004 against the
  REAL check: the check's own `field_name` needed to resolve too, not only its new
  `applies_if` condition, for `validate_referential_integrity()` to pass end-to-end against a
  real `Ruleset`, not a hand-authored look-alike), `result/rules/post_closing_only_ruleset.json`
  (FR-007: `applies_if` added to `insurance-docs-support-owner-occupancy`; `010a`'s
  `post_closing_only_applicability.json` `["Fannie Mae"]` tag for the same check confirmed
  untouched, FR-010), `storage/loan_profiles/v3/loan_0{1..5}.json` (new, generated).
- **Two small, honest scope extensions beyond the original FR list, both required to keep
  this project's own pre-existing test gates green (not scope creep -- necessary consequences
  of adding real catalog entries)**:
  1. `insurance_docs_support_owner_occupancy`'s new catalog entry needed its own taxonomy
     grounding (`test_fixture_generation.py::test_every_new_catalog_field_has_taxonomy_grounding_citation`)
     -- grounded in `taxonomy.json` archetype MISMATCH, category Underwriting (the real AMQ row
     family, `pc-retail-02837/02838/02839/02840/02841`). `occupancy_type` is grounded the same
     way (it is the canonical claimed-occupancy value that check corroborates against).
     `loan_program` is not itself a QC-finding subject -- it categorizes the loan, it does not
     assert a defect -- so forcing a taxonomy citation on it would have been dishonest; instead,
     `test_fixture_generation.py`'s grounding test gained a third, explicit, equally-strict
     category ("derived-fact grounded": names its own deriving function + owning spec, never a
     fabricated archetype citation) and `loan_program`'s description uses it.
  2. `storage/fact_vocabulary/candidates/v1.json` (a downstream generated artifact, `002f`'s
     `discover_fact_candidates.py`) is derived FROM `field_catalog.json`; adding 3 new catalog
     entries changed its own regenerated output (24 candidates unchanged, one new
     `catalog_field_suggestions` fuzzy-token-overlap entry for `insurance_docs_support_owner_occupancy`,
     `field_catalog_entries: 379 -> 382`). Regenerated and re-committed to keep
     `test_fact_candidates.py::test_rebuild_is_byte_identical` green -- the same "downstream
     generated artifact must be rebuilt when its own input changes" discipline this project
     already applies to loan profiles.
  3. `test_occupancy_applicability_gating.py`'s own T017 test (`test_real_check_currently_has_no_applies_if_before_this_feature`)
     had a docstring that explicitly anticipated flipping once FR-007 landed ("this test's job
     is only to pin down the starting point, not to remain true forever"). Renamed to
     `test_real_check_now_carries_applies_if_after_fr007_lands` and its assertion flipped to
     confirm the after-state, rather than left stale and failing.
- **`derive_loan_program`'s two shipped `underivable` reason strings** (SC-003, exact text on
  the real fixtures):
  - loan_01: "loan_type_cd reads 'Conventional' (cited), but no GSE-specific citable field
    (fha_case_number_1003 / va_lgy_case_number / usda_gus_id) is present -- 'Conventional' alone
    cannot distinguish Fannie Mae vs. Freddie Mac (the same ambiguity program_gating.py's own
    AMBIGUOUS sentinel already surfaces at the SQL-clause layer) -- refusing to guess in either
    direction"
  - loan_04: "no program-identifying field of any kind is present in loan.fields (checked
    ['fha_case_number_1003', 'va_lgy_case_number', 'usda_gus_id', 'loan_type_cd']) -- the loan's
    top-level loan_type label, if any, is uncited fixture-authoring metadata, not a citable
    doc-extracted signal -- refusing to guess"
- **Confirmed untouched**: `engine.py`, `model.py`, `ruleset.py`, `reconcile.py` -- `git diff`
  against this feature's own start point shows zero changes to any of the four; this feature
  is additive data (a new profile version, 3 catalog entries, 1 check's `applies_if`, 1 new
  vocabulary version) plus one small, new, additive wiring module, exactly as planned above.
- **Test results**: `p0/qc_engine/build_loan_profiles_v3.py` + `apply_loan_profile.py`'s own 21
  new tests: 21/21 green. Full suite (`cd p0 && python3 -m pytest tests -q`, excluding
  `test_decision_narrative.py` -- `014`'s file, out of this spec's scope, mid-flight in a
  concurrent session against this same worktree): 343 passed, 46 failed, 3 skipped -- the 46
  failures are 100% pre-existing environment gaps (`ModuleNotFoundError: No module named
  'eval_real'`, missing `demo/syn/`/`demo/rules/` source files not present in this worktree
  checkout) confirmed unrelated to this feature by direct inspection of every failure's
  traceback; zero of the 46 reference `occupancy_type`, `loan_program`, `build_loan_profiles_v3`,
  `apply_loan_profile`, or `field_catalog`. `python3 harness.py`'s 1,000-run digest
  (`82175d076579e31a50971d8b20ea4b63848bea9f9b53c30dd96524071842e5ec`) is confirmed byte-identical
  to the value recorded in this spec's own SC-005 at time of writing.
