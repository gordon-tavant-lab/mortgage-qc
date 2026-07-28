# Implementation Plan: Loan Data-Capture & Precondition-Gating Fix (+ FIBO Alignment)

## Sequencing rationale

**Phase 0 (build + run the coverage gate) → Phase A (3 required fixes) → Phase B (informed/expanded
by Phase 0's real output) → Phase C (explicit Layer 1 go/no-go) → spec 014 follow-up.**

Phase 0 goes first so Phase A/B's exact scope is authoritative (the gate's real output), not another
round of manual log-reading. Within Phase A: Issue 3 (one-line config swap) → Issue 2 (`engine.py`,
largest blast radius — every spec, the determinism harness) → Issue 1 (largest diff: new field, new
derivation, new gating logic, fixture regen, test rewrites) — each landed and fully regression-tested
before the next, so any regression is unambiguously attributable to one change.

## Phase 0 — Field & Precondition Coverage Gate

**New artifact**: `p0/compile_runs/run_016_coverage_gate/build_and_run.py` (decide at implementation
time whether the core logic should also live in an importable `p0/qc_engine/coverage_gate.py` if other
specs would want to call it directly).

### Design
1. Call `ontology_pipeline.run_layers(rows)` (or reuse `run_013`'s already-computed `PipelineResult`
   if available) to get every `PreconditionProposal`, including `FLAGGED` ones (`source_layer`,
   `condition.field_name`, `trust_tier`).
2. For every distinct `field_name` referenced: check (a) `field_catalog.json` entry exists directly
   or as a derived-fact target, (b) a `doc_patterns/*.json` pattern or `build_loan_profiles_v3.py`
   derivation function actually produces it, (c) it's non-`None` in at least one of the 5 real
   fixtures (`p0/fixtures/from_docs/loan_0*.json`).
3. Separately, for every distinct `Check.field_name`/`compare_field_name` across the ruleset(s) in
   active use (`comprehensive_e2e_v6_ruleset.json` at minimum), the same three-part check — this is
   the broader net catching non-gating gaps too.
4. Cross-check a small, curated list of FIBO `LOAN`/`RealEstateLoans` concepts (loan program/investor
   type, occupancy, property type, income type — identified manually from FIBO's public schema, not a
   full ontology import) against the catalog, as a third, independent validation source.
5. Output: a structured report, categorized by which check failed (no catalog entry / no
   extraction-or-derivation path / never populated / no FIBO-aligned concept), full list not a sample.

### Verification
Run against the current (pre-fix) repo state first. Confirm it reproduces `loan_program_1003` and
`income_type_used_for_qualification` as real gaps (SC-006) — this is the proof the gate is a faithful
automation, not a weaker approximation, of this session's manual discovery.

### Standing-gate documentation
Add a short section (`CLAUDE.md` or `output/`) declaring this a required pass before signing off any
newly compiled ruleset or demo/production run — same standing as `verify_against_defects.py`'s 25/25.

## Phase A — the three required fixes

### Issue 3 — `run_015`'s applicability-map swap
`p0/compile_runs/run_015_loan_01_comprehensive_qc/build_and_run.py`: `APPLICABILITY_PATH` →
`result/rules/post_closing_only_applicability.json` (verified 100% ID coverage against
`comprehensive_e2e_v6_ruleset.json`, vs. the old file's 61%). Update the docstring's "Inputs" section.
No test regression risk (this script has no dedicated test file).

### Issue 2 — `engine.py`'s `predicate`/`is_true` missing-data fix
`p0/qc_engine/engine.py`, `predicate` branch (~lines 319-335): for `chk.predicate == "is_true"`
specifically, `sv.doc is None` → `status="NEEDS_REVIEW"`, `review_reason="APPLICABILITY_UNKNOWN"`,
early return. `is_present`'s branch is untouched. Update the now-stale comment above the branch.

Test changes (conscious, dated):
- `test_p0.py::test_is_true_missing_doc_fails` → renamed, reasserted to `NEEDS_REVIEW`/
  `APPLICABILITY_UNKNOWN`, comment citing this spec.
- New test: `is_true` + `None` → `NEEDS_REVIEW` (the fix's own positive case).
- New/confirmed test: `is_present` + `None` → `FAIL` unchanged (negative regression pin).

Verification order: `pytest p0/tests -v` → `harness.py` (compare digest to
`82175d076579e31a50971d8b20ea4b63848bea9f9b53c30dd96524071842e5ec`, expected unchanged since no
golden loan/check pair in `demo_ruleset()`/`golden_loans()` exercises this path — confirm by running,
not assuming) → `verify_against_defects.py` (expected unaffected — this gate never calls
`engine.run()`, compares raw `.truth` values directly; re-run as a sanity check regardless).

### Issue 1 — real extraction path for loan program (loans 01 AND 04)

Framing: this `doc_patterns/*.json` addition is a synthetic-fixture stand-in (CLAUDE.md
Non-Negotiable #2 — real extraction is Touchless's job long-term), built now anyway because tonight's
demo accuracy is critical regardless of long-term ownership. Note `loan_program_1003` (here) and
`income_type_used_for_qualification` (Phase B) as data-contract items for Touchless's eventual real
extraction (fold into Phase 0's documentation, not a separate deliverable).

1. `p0/fixtures/from_docs/doc_patterns/urla_1003.json`: add
   `"loan_program_1003": {"regex": "Loan Program\\s+([^\\n*]+)"}`.
2. `p0/qc_engine/field_catalog.json`: add `loan_program_1003` entry (`citation_required: true`,
   `data_type: string`, `expected_sources: ["doc"]`).
3. Regenerate all 5 fixtures (`build_fixtures.py` loops uniformly; regenerating all 5 is less work
   and more consistent than a per-loan carve-out): `python3 build_fixtures.py &&
   python3 verify_against_defects.py` (must be 25/25). Diff-check: only `loan_program_1003` is new
   across all 5 fixtures' `fields{}`; everything else byte-identical.
4. `build_loan_profiles_v3.py::derive_loan_program()`: add a literal GSE-marker check on
   `loan_program_1003` (`"Fannie Mae"`/`"Freddie Mac"` substring), consulted only after the existing
   FHA/VA/USDA presence-field path fails to resolve — preserves loans 02/03/05's exact behavior.
5. Regenerate `storage/loan_profiles/v3/*.json`. Diff-check: only loans 01/04 change.
6. `program_gating.py::applies_to()`: prefer `loan.get("loan_program").doc` over
   `_loan_program(loan.loan_type)`, falling back to the existing path when the fact isn't present.
   Verify `test_program_applicability_gating.py` unchanged for bare loans (no `loan_program` fact
   set); add one new test proving real disambiguation (Fannie-tagged → `True`, Freddie-tagged →
   `False`, not `AMBIGUOUS`, for a loan shaped like post-fix loan 01).
7. Update the 3 tests pinning the old "underivable" outcome
   (`test_loan_profiles_v3.py` ×2, `test_occupancy_applicability_gating.py`'s
   `test_apply_derived_facts_writes_nothing_for_underivable_entries`) — consciously, keeping the
   "writes nothing when genuinely underivable" invariant covered via a still-underivable case.
8. Full verification: `pytest`, `harness.py` (expect unchanged), `verify_against_defects.py` (25/25).
9. `cp p0/fixtures/from_docs/loan_0*.json result/loans/` per that directory's documented procedure.

### Regeneration + spec 014 follow-up
Re-run `run_015`'s script; rewrite its `honest_program_ambiguity_note`; add a `known_caveats`
top-level key (ruleset's real `signoff_summary`, one-line summary of this spec's fixes). After
Phase A/B are fully green, re-run `run_014_decision_narrative_panel/build_and_run.py` and refresh
spec 014's status header with the new real numbers.

## Phase B — ontology-grounded high-leverage fixes

### Step 6 — `income_type_used_for_qualification`
Same shape/process as Issue 1's `loan_program_1003` — new pattern (VOE/1003 employment section, exact
source line confirmed at implementation time), catalog entry, new `derive_income_type()` in
`build_loan_profiles_v3.py`, fixture + profile regeneration for all 5 loans with the same diff-check
discipline. Verify: self-employment-gated checks resolve `NOT_APPLICABLE` for loan 01, not
`APPLICABILITY_UNKNOWN`.

### Step 7 — Question 571085 (loan-product-type taxonomy, ~165+ checks)
Register the 18-answer-value taxonomy through `002g`'s existing `FV.resolve_layer0`/sign-off
mechanism (confirm at implementation time whether this binds to the same `loan_program` fact or a
sibling `loan_product_type` fact). Re-run precondition attachment; confirm the affected checks move
from `FLAGGED` to `applies_if`-gated.

### Step 8 — Question 570606 (asset-type taxonomy split, ~102 checks)
Targeted disambiguation of the shared `Yes - Gift`/`Yes - Checking/Savings`/etc. dropdown into its two
already-known facts (`fact-closing-funds-asset-type`, `fact-gift-funds-used`) — a vocabulary/mapping
task, not new extraction, since standalone `gift_funds_used` rows already resolve correctly elsewhere.

### Phase B verification
Same discipline as Phase A, plus: re-run `run_013`'s precondition-attachment summary and confirm
`attached` rises (from 1,530 toward ~1,700+) and `flagged` falls (from 520 toward ~250 or lower).

## Phase C — Layer 1 (explicit decision, not assumed)

1,153 checks have no dependency Layer 0 can find — Layer 1 (free-text `defect_text` LLM extraction)
has never been run against this ruleset. Cost/yield are both unknown until tried. Phase A's engine
fix already prevents the misleading-FAIL problem regardless of whether Layer 1 runs — skipping it just
means more checks land in `NEEDS_REVIEW` than would with fuller gating. Decision recorded explicitly
once Phase 0's real numbers are in hand, sized to whatever time remains after Phase 0/A/B are green.

## FIBO adoption — documentation deliverables (do regardless of Phase C timing)

1. `CLAUDE.md`: new section near Non-Negotiable #1's grounding discussion, dated, naming this as a
   conscious decision superseding part of `002g`'s "vocabulary not reasoner" framing into "FIBO-aligned
   vocabulary, still not a reasoner" — state the boundary (concept/vocabulary layer only, `engine.py`
   untouched) explicitly.
2. `output/FIBO-ONTOLOGY-ADOPTION-DECISION.md`: what was decided, why (this session's two missed-field
   incidents), the going-forward practice (new fields authored against FIBO first), the explicit
   boundary, and a roadmap pointer.
3. `output/ROADMAP.md`: new entry for the future full-migration spec (not this spec's scope).

## What this plan deliberately does not do

- No OWL/RDF/SPARQL machinery enters `engine.py` or any runtime evaluation path.
- No full migration of the existing ~380 catalog fields / ~4,837 unique checks onto FIBO concepts —
  tracked as a separate, future spec.
- No blind test-patching — every changed assertion gets a dated, explicit comment explaining the
  deliberate behavior change.

## Test plan

- Unit tests for the coverage gate: a constructed `PipelineResult` with a known-missing field
  reproduces a reported gap; a fully-covered fixture reports zero gaps.
- Unit tests for `engine.py`'s `is_true`/`None` path and the `is_present`/`None` regression pin.
- Unit tests for `program_gating.py::applies_to()`'s new fact-preference path, plus the existing
  no-signal-loan `AMBIGUOUS` regression pin.
- Unit tests for `derive_loan_program()`/`derive_income_type()`'s new GSE/income-type branches.
- Integration: full 5-loan fixture regeneration + 25/25 defect gate at every regeneration point;
  `harness.py` digest comparison at every phase boundary; real `run_015` (and `run_016` coverage gate)
  execution against real data, not mocks.
