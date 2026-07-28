# Implementation Complete When

## Overall Exit Condition

- All tasks in `tasks.md` are marked `[X]`
- `python3 -m pytest p0/tests/ p0/eval_synth/test_properties.py -q` exits 0 (no test framework/lint
  command exists beyond pytest in this project — see plan.md Technical Context)
- `python3 p0/harness.py` (bit-exact determinism digest) exits 0 with an unchanged digest from its
  pre-feature baseline
- `python3 p0/fixtures/from_docs/verify_against_defects.py` reports exactly `25/25 matched`

## Phase Gates (must pass before next phase starts)

### Phase 1 — Setup
Done when: `p0/fixtures/from_docs/` exists with the `doc_patterns/` subdirectory and a `README.md`
carrying all three required disclaimers (not-Touchless, no real-document accuracy claim, doc-vs-doc
deferred to `003c`); `python3 -m pytest p0/tests/test_fixture_generation.py --collect-only` exits 0.

### Phase 2 — Foundational
Done when: `p0/fixtures/from_docs/defect_manifest.json` has exactly 25 entries matching the 25
`<!-- DEFECT ... -->` comments across the 5 loans' MISMO XML files; every `field_name`/
`compare_field_name` it references resolves to a `p0/qc_engine/field_catalog.json` entry; the
catalog's existing referential-integrity validator and the full existing engine test suite
(`test_p0.py`, `test_predicate_archetypes.py`, `test_threshold_archetypes.py`) pass unmodified
against the extended catalog; `qc_engine/mismo.py` returns a value for every new mismo-sourced field
on the loans that carry it, with zero change to its original 7-field output.

### Phase 3 — User Story 1 (fixtures load cleanly, no cross-loan leakage)
Done when: exactly 5 fixture JSON files exist under `p0/fixtures/from_docs/`; each loads into
`CanonicalLoan` via `p0/qc_engine/model.py` with zero code changes to that file; each scores through
`p0/eval_synth`'s existing scorer with zero changes to the scorer; no field or citation in any
fixture is traceable to a different loan's documents.

### Phase 4 — User Story 2 (25/25 known-defect gate)
Done when: `verify_against_defects.py` reports `25/25 matched` against the 5 real generated
fixtures; a deliberately-broken fixture (one defect patched to not-reproduce) is reported as `24/25`
with a non-zero exit — proving no partial-credit path exists. Fixtures MUST NOT be described as
wired into any downstream engine/eval test run until this gate is green.

### Phase 5 — User Story 3 (catalog grounded in real rules)
Done when: every new `field_catalog.json` entry has a non-empty, reviewable `taxonomy.json`
archetype citation in its description; the catalog's referential-integrity/zero-regression
validation passes as this feature's own named acceptance run (not just Phase 2's initial pass).

### Phase 6 — User Story 4 (full audit trail)
Done when: 100% of document-sourced field values across all 5 fixtures carry a non-empty
`{doc_name, page_num, segment_snippet}` citation; any genuinely system-of-record-sourced field
(e.g. an FHA-case-number system side) carries a lightweight provenance note instead of a fabricated
document/page citation.

### Phase 7 — Polish
Done when: the full existing suite plus the new `test_fixture_generation.py` pass with zero
regression; `harness.py`'s digest is unchanged; `README.md`'s disclaimers match what was actually
built; `plan.md` has a post-hoc "Implementation Notes" section recording the final task count and
the `25/25` verification result.

## Must Not Regress

- The existing 7 seed `field_catalog.json` entries and their behavior (FR-009, `001a` governance)
- `qc_engine/mismo.py`'s existing return values (labeled "7-field" here but enumerating ~10 names — self-inconsistent as written; live `parse_mismo()` on loan 01 returns 8 keys. Noted 2026-07-26, spec audit) for `borrower_name`, `borrower_ssn`,
  `note_rate`, `loan_amount`, `property_address`, `flood_zone`, `note_signed`/`term_months`,
  `property_value`, `purchase_price`, `loan_id`
- `p0/fixtures/golden.py`'s existing hand-authored fixtures — unchanged, not replaced (plan.md
  Project Structure)
- `p0/eval_synth`'s existing scorer and golden-fixture test suite — must pass unmodified after the
  new fixtures are introduced (SC-004)
- The engine's existing test suites (`test_p0.py`, `test_predicate_archetypes.py`,
  `test_threshold_archetypes.py`) and `harness.py`'s bit-exact determinism digest
- Determinism: same source documents → same output JSON, every run, every machine (plan.md
  Constraints) — no wall-clock, no non-`temperature=0` LLM call, on the primary extraction path
- Source independence: no doc-vs-doc comparison is ever silently modeled as doc-vs-system (FR-007,
  SC-005) — genuine doc-vs-doc pairs stay as two independently-cited catalog fields, comparison
  logic explicitly deferred to `003c`
- Scope: this feature never claims to be, replace, or preempt the Touchless production extractor or
  the LOS/MISMO connector (Principle IV, FR-003/FR-010)
