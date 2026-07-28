# Feature Specification: Reconcile Check Engine

**Feature Branch**: `003c-engine-reconcile-checks`
**Created**: 2026-07-16
**Status**: Implemented (2026-07-16, commit `cd545a6` — all 11 proof tests; header corrected from stale "Draft" 2026-07-27, spec adversarial audit)
**Input**: User description: "003c-engine-reconcile-checks — deterministic Step-1 reconcile
execution (agree_categorical/agree_numeric) across the independent doc and system paths, at the
scale of the real reconcile archetypes (INACCURATE 263 + MISMATCH 139 ≈ 402 real conditions; **282 + 165 = 447** in the regenerated, currently-uncommitted post-010a taxonomy — count-basis note as in `003a`, 2026-07-26 audit) —
the next slice in the 003a→003b→003c engine arc, unblocking 004-loan-disposition."

**Governs**: `output/ROADMAP.md` §003c, `.specify/memory/constitution.md` Principle V (source
independence — the three sources are cross-compared, not checked in isolation) and the two-step
RECONCILE/QC model, `output/THESIS.md`'s audit story (a FLAG must never read as a buyback-triggering
failure, and vice versa).
**Depends on**: `001a-field-catalog` (implemented). `001b-source-envelope-and-inbound-contracts`
(implemented — reconcile compares the independent truth/system paths that feature's N-source
envelope generalized). `002b-ruleset-compiler-pipeline` (implemented — this feature evaluates the
checks 002b's pipeline compiles and signs; it does not compile anything itself). Independent of
`003a`/`003b` (both implemented) — all three slice the engine by check-kind, not by dependency.
**Foundation this builds on** (proven, not re-specced): `p0/qc_engine/engine.py`'s `_eval_check`
`agree_categorical`/`agree_numeric` branches and `p0/qc_engine/reconcile.py`'s normalizer table
already implement doc-vs-system reconciliation correctly — proven generically by 001b's own tests
(`test_reconcile_check_compares_independently_populated_sources`,
`test_mismo_only_loan_resolves_system_value_unchanged`, `test_new_named_source_readable_with_zero_engine_changes`)
and exercised at length by `demo_ruleset()`'s 6 hand-authored reconcile checks
(`chk-borrower-name`, `chk-borrower-ssn`, `chk-note-rate`, `chk-principal`, `chk-property-address`,
`chk-flood-zone`) plus, most recently, `000-synthetic-fixture-generation`'s own
`chk-def-fha-case-number` (an `agree_categorical` check against a real extracted field, added
2026-07-16 while wiring known defects into checks). This feature does two things to that existing
mechanism: (1) proves it correct at the scale of the real reconcile archetypes (INACCURATE +
MISMATCH, ~402 conditions) rather than just a handful of hand-authored demo checks, and (2)
documents — rather than silently glossing over — a real structural gap that scale-testing surfaces
(see "What this feature is fixing, precisely" and Edge Cases below).

**What this feature is fixing, precisely:** Unlike `003a`/`003b`, this feature does not close a
vocabulary gap in existing code — `agree_categorical`/`agree_numeric` already work, generically,
for any named source. What's missing is the same thing `003b` supplied for `ratio_threshold`: proof
at real archetype scale, plus an honest accounting of which real conditions that proof actually
covers. Reading `p0/eval_synth/taxonomy.json`'s own MISMATCH examples closely surfaces a structural
finding that changes this feature's honest scope: the real MISMATCH archetype's example conditions
—

- *"The employment dates listed on the 1003 do not match other employment documentation in the file"*
- *"The loan purpose selected on the final 1003 does not match the final 1008 and/or final DU"*
- *"The manner in which title is held on the 1003 does not match the title commitment"*

— are predominantly **doc-vs-doc** comparisons (two independently-extracted *document* values, e.g.
1003 vs VOE, 1003 vs title commitment), **not doc-vs-system**. This is the exact shape
`000-synthetic-fixture-generation` found and explicitly deferred in its own known-defects wiring
(`title_vesting_1003` vs `title_vesting_commitment`, `employment_start_date_1003` vs
`employment_start_date_voe`, `loan_purpose_1003` vs `loan_purpose_cd`, and two others) — not a
one-off synthetic-loan quirk, but the real archetype's dominant real-world shape. The engine's
current `SourceValue` model has exactly **one** `doc` (truth) slot plus named *system* sources
(`los`, `mismo`, ...) — there is no representation for "value from document A" vs "value from
document B" as two independently-named slots. Widening `agree_categorical` to cover this is not a
small vocabulary fix like `003b`'s `ratio="field_value"` addition; it is a data-model question (does
`SourceValue` need multiple named *document* slots, not just one truth + N system slots?) that this
feature does not answer. This feature proves the **doc-vs-system** subset of the reconcile archetype
correct at scale, and explicitly names the doc-vs-doc majority as an uncovered, distinct gap — the
same "prove the clean case, name the rest" discipline `003b` applied to the bundled
`ratio_threshold-01/02/03/04` rows.

Of the two real `agree_categorical`-tagged rows `002a` actually sampled from the real workbook
(`p0/experiment_002a/artifacts/sampled_rows.json`, `row_id="reconcile-00"`/`"reconcile-01"`):
- `reconcile-01` ("SFC 162 not used where there was a discrepancy identified with the Social
  Security number") is a genuine doc-vs-system shape — an SSN discrepancy check, the same
  structural pattern `demo_ruleset()`'s existing `chk-borrower-ssn` already implements
  (`ssn_last4` normalizer, doc vs system). This is this feature's representative real proof case,
  the same role `ratio_threshold-00` (credit-score floor) played for `003b`.
- `reconcile-00` ("credit information material conflict(s) was not investigated and resolved
  appropriately") is ambiguous from the AMQ row text alone — it may not be a clean two-value
  comparison at all (it reads closer to a completeness/procedural condition, arguably `003a`
  predicate territory). Explicitly not resolved here; named as an open compiler-classification
  question for `002b`/Kayla, the same way `003a` left `EXPIRED`'s staleness semantics open and
  `003b` left the bundled multi-condition rows open.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The reconcile mechanism is proven correct across the real reconcile-archetype set, not just the demo's 6 hand-authored checks (Priority: P1)

The demo ruleset carries 6 hand-authored `agree_categorical`/`agree_numeric` checks, all proven
correct individually and generically by `001b`. `003c`'s actual job is the ~402 real conditions
`taxonomy.json` classifies as INACCURATE/MISMATCH, anchored on the one real, structurally-clean,
doc-vs-system sampled row (`reconcile-01`, the SSN-discrepancy condition).

**Why this priority**: This is the actual coverage claim `output/ROADMAP.md` §003c makes
("~402 real conditions") — same discipline `003b` applied: an untested claim about scale isn't a
proven one, and the claim must be scoped to what the mechanism actually covers (see this spec's
preamble on the doc-vs-doc finding).

**Independent Test**: Construct a loan with independently-populated doc (truth) and system (`los`
or `mismo`) values for an SSN-shaped field; build one case where they agree and one where they
genuinely diverge (independence-guard verified, per `001b`'s own `assert_independently_constructed`
discipline — no mutation that "diverges" by leaving `sources` untouched); confirm the engine
produces the correct verdict in both directions, plus a representative categorical (name/address)
and numeric (rate/amount) pair.

**Acceptance Scenarios**:

1. **Given** a loan whose doc (truth) and system values for an SSN-shaped field agree after
   `ssn_last4` normalization, **When** the check runs, **Then** the verdict is `PASS`.
2. **Given** the same field genuinely diverging (independently constructed, not a copy-paste
   "sources left unchanged" mutation), **When** the check runs, **Then** the verdict is `FLAG`
   (informational, `severity=INFO`), **never** `FAIL`.
3. **Given** representative `agree_numeric` conditions (a rate or dollar amount) at, within, and
   outside an authored tolerance, **When** evaluated, **Then** every case produces the correct
   verdict using `Decimal`/`within_tolerance` — no float touches the comparison.
4. **Given** a loan with no doc value, or no system value, for the compared field, **When** the
   check runs, **Then** the verdict is `NEEDS_REVIEW` (existing behavior — one side present, the
   other absent, cannot be reconciled) or `NOT_APPLICABLE` (both absent) — unchanged regression,
   verified explicitly at this feature's own scale rather than only by `001b`'s narrower tests.

---

### User Story 2 - The FLAG-vs-FAIL separation holds safely at scale, in both directions (Priority: P1)

Principle V's two-step model rests on one property: a reconcile disagreement is *informational*
(the closing document is truth; QC runs against it regardless of system sync) and must never block
`auto_cleared` or appear as a QC failure. The inverse must also hold: a genuine QC-phase failure
(predicate/ratio_threshold) must never be misclassified as a reconcile FLAG. Both directions are
proven today only by the demo ruleset's one mixed run — not at real archetype scale, and not as an
explicit adversarial property.

**Why this priority**: This is the single highest-stakes property specific to this check-kind — a
regression here either silently swallows a real defect (a FAIL reclassified as an informational
FLAG, a false-auto-clear) or wrongly blocks a clean loan (a FLAG misread as a failure). Equal
priority to US1 because proving the mechanism *correct* without proving it *safely partitioned* is
an incomplete claim.

**Independent Test**: Build a mixed ruleset spanning `agree_categorical`, `agree_numeric`,
`predicate`, and `ratio_threshold` checks against one loan with both a genuine reconcile divergence
and a genuine QC failure; confirm the divergence surfaces only in `reconcile_results`/`flags` (never
`qc_failures`/`exceptions`) and the failure surfaces only in `qc_results`/`qc_failures` (never
misread as a `flags`-only FLAG), and that `auto_cleared` is `False` (blocked by the real QC failure,
not by the FLAG).

**Acceptance Scenarios**:

1. **Given** a loan with a genuine reconcile divergence and no QC failure, **When** run, **Then**
   `flags` is non-empty, `qc_failures` is empty, and `auto_cleared` is `True` — an informational
   FLAG alone never blocks auto-clear.
2. **Given** a loan with a genuine QC failure and no reconcile divergence, **When** run, **Then**
   `qc_failures` is non-empty, `flags` is empty, and `auto_cleared` is `False`.
3. **Given** a loan with both, **When** run, **Then** both surface in their correct, separate
   buckets simultaneously — `auto_cleared` is `False` (the QC failure alone is sufficient to block
   it; the FLAG is not what blocks it).
4. **Given** the full constructed reconcile-archetype fail-case batch (US1), **When** scored,
   **Then** zero instances of a reconcile FLAG appearing in `qc_failures` or blocking
   `auto_cleared`, and zero instances of a QC failure appearing only as a FLAG — the SAFE gate, at
   archetype scale.

---

### Edge Cases

- What happens to the real MISMATCH examples that are doc-vs-doc, not doc-vs-system (employment
  dates 1003-vs-VOE, loan purpose 1003-vs-1008/DU, title vesting 1003-vs-commitment)? → Explicitly
  out of scope. The current `SourceValue` model has one `doc` slot and named *system* sources; it
  has no way to represent two independently-named *document* values for the same field. Building
  this would require a data-model decision (multiple named document slots? a generalized N-way
  envelope beyond doc/system?) this feature does not make — a genuinely open question for whoever
  specifies that capability next, not a small vocabulary widening like `003b`'s. Named here so it is
  not silently assumed solved by "003c" the way `000-synthetic-fixture-generation`'s own wiring work
  initially (incorrectly) assumed it would be.
- What happens to `reconcile-00` (the credit-conflict-investigation row), whose comparison
  structure is unclear from the AMQ text alone? → Not resolved here. Flagged as an open
  compiler-classification question — it may be closer to a `003a` predicate/completeness condition
  than a genuine two-value comparison. Mirrors `003a`'s own deferred `EXPIRED`-staleness question
  and `003b`'s deferred bundled-condition rows: named, not silently forced into a kind it may not
  fit.
- What happens to the INACCURATE archetype's own examples ("the final 1003 application is
  inaccurate or incomplete," "marital status is incomplete or appears inaccurate")? → These read as
  generic completeness/validity observations, not obviously a two-source comparison either. Treated
  as part of the same open classification question as `reconcile-00` — this feature does not assume
  every INACCURATE-tagged row is a clean `agree_categorical` fit just because `taxonomy.json`
  labels its `engine_kind` that way. `taxonomy.json`'s own coverage note already says classification
  covers ~57% of the 7,398 total conditions; this feature adds a second caveat layer specific to
  reconcile — archetype *label* is not the same claim as *structural fit*.
- What happens when a mixed ruleset's `_phase_for` inference is wrong (e.g. an author sets an
  explicit `phase=""` on an `agree_categorical` check)? → Unchanged existing behavior:
  `_phase_for` infers `RECONCILE` for `agree_categorical`/`agree_numeric` when `phase` is blank,
  same as `003a`/`003b` rely on inference for `QC`. Not a new code path; verified at this feature's
  scale, not reintroduced.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine's existing `agree_categorical`/`agree_numeric` branches MUST correctly
  evaluate representative constructed samples of the real reconcile archetype, anchored on the real
  `reconcile-01` (SSN-discrepancy, doc-vs-system) condition from
  `p0/experiment_002a/artifacts/sampled_rows.json` — not fabricated, drawn from the actual sampled
  workbook rows.
- **FR-002**: A genuine reconcile-phase disagreement MUST produce `FLAG` with `severity="INFO"`,
  never `FAIL`, across the full constructed sample — regression of existing behavior, proven at
  this feature's scale rather than only the demo's 6 checks.
- **FR-003**: A reconcile-phase `FLAG` MUST NOT appear in `RunResult.qc_failures`/`exceptions` and
  MUST NOT cause `auto_cleared` to be `False` on its own, verified across the full constructed
  sample (not just spot-checked).
- **FR-004**: A genuine QC-phase failure (`predicate`/`ratio_threshold`) evaluated alongside
  reconcile checks in the same ruleset MUST NOT be misclassified as a reconcile `FLAG` — the
  `RECONCILE`/`QC` phase partition (`_phase_for`) MUST remain correct under a realistic mixed
  ruleset.
- **FR-005**: This feature MUST NOT introduce a new `Check.kind` or a new data-model capability for
  representing multiple independently-named document sources — the doc-vs-doc majority of real
  MISMATCH conditions (see preamble and Edge Cases) is explicitly out of scope, named as a distinct
  future capability question, not silently assumed solved.
- **FR-006**: This feature MUST NOT attempt to resolve ambiguous real conditions whose comparison
  structure is unclear from the AMQ row text alone (`reconcile-00`; the INACCURATE archetype's
  completeness-flavored examples) — flagged as open compiler-classification questions for `002b`/
  Kayla's rules review, not resolved by this engine spec.
- **FR-007**: This feature MUST NOT build predicate (`003a`, implemented) or ratio_threshold
  (`003b`, implemented) evaluation logic, product/program gating (`010a`/`010b`), the authoring UI
  (`009a`/`009b`/`009c`), or any runtime LLM evaluation path (constitution Principle II).
- **FR-008**: The pre-existing `001b` reconcile tests, `demo_ruleset()`'s 6 reconcile checks, this
  session's `chk-def-fha-case-number`, and the P0 determinism digest MUST be unchanged by this
  feature (regression).

### Key Entities

- **SourceValue** (existing, `p0/qc_engine/model.py`): `doc` (truth) + `sources{}` (named system
  values, resolved via `source_priority`) + `system_value()`. No new fields — this feature proves
  the existing shape correct at scale; it does not extend it to represent multiple named document
  sources (see FR-005).
- **Check** (existing, `p0/qc_engine/ruleset.py`): `kind="agree_categorical"|"agree_numeric"`,
  `normalizer`, `tolerance`, `sources`. No new dataclass fields introduced.
- **ReconcileArchetypeFixture** (new, test-only): constructed pass-case/flag-case loan sets for the
  real `reconcile-01` (SSN) condition plus representative categorical/numeric pairs, and a mixed
  ruleset construction for US2's FLAG-vs-FAIL partition proof — the local eval coverage this
  feature ships with, same precedent `003a`/`003b` established (independent of `005`, which does not
  exist yet).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A constructed loan built on the real `reconcile-01` SSN-discrepancy condition produces
  `PASS` when doc/system agree and `FLAG` (never `FAIL`) when they genuinely diverge — verified by
  test.
- **SC-002**: 100% correct verdicts across constructed representative `agree_categorical` and
  `agree_numeric` cases (agreement, genuine divergence, one-side-absent, both-absent).
- **SC-003**: Zero instances, across the full constructed sample, of a reconcile `FLAG` appearing in
  `qc_failures`/`exceptions` or blocking `auto_cleared` on its own.
- **SC-004**: Zero instances, across a constructed mixed ruleset, of a genuine QC failure being
  misclassified as a reconcile `FLAG`.
- **SC-005**: This feature's own spec text explicitly names the doc-vs-doc majority of real
  MISMATCH conditions and the ambiguous INACCURATE/procedural rows as uncovered — a coverage claim
  that is honest about its boundary, not implicitly total (mirrors `003a`'s "~57% classified"
  caveat).
- **SC-006**: All pre-existing tests (`p0/tests/test_p0.py`, `p0/eval_synth`, and
  `000-synthetic-fixture-generation`'s `test_fixture_generation.py` suite) continue to pass
  unmodified after this feature's change — zero regression, matching the bar every prior spec has
  held (`001a`: 19/19, `001b`: 18/18, `002b`: 31/31, `003a`: 64/64, `003b`: cumulative, `000`: 104
  passed as of this spec's writing — all "zero regression"), and the P0 determinism digest
  (`8510a0a8b4b6996e047fc8534e094394ba72aae396305b0d2ecad3d6924634db`) is unchanged.

## Assumptions

- This feature hardens and proves-at-scale the already-implemented `agree_categorical`/
  `agree_numeric` branches in `p0/qc_engine/engine.py`; it does not invent a new check kind — same
  minimal-change discipline `003a`/`003b` both followed.
- The real `reconcile-01` row (SSN discrepancy) is treated as the representative proof case because
  it is a genuine, structurally-clean doc-vs-system comparison, directly analogous to
  `demo_ruleset()`'s own pre-existing `chk-borrower-ssn` check — unlike `reconcile-00`, whose
  comparison structure is not confirmed from the row text alone (FR-006).
- The doc-vs-doc majority of real MISMATCH conditions (per `taxonomy.json`'s own examples) is a
  genuinely new data-model question, not a small vocabulary widening — explicitly out of scope here
  and not assumed solved by whatever spec eventually addresses it. This corrects an imprecise
  assumption made during `000-synthetic-fixture-generation`'s known-defects wiring, which initially
  described 5 doc-vs-doc defects as "deferred to 003c."
- Per `output/ROADMAP.md`'s inherited coverage caveat (from `003a`/`003b`), taxonomy classification
  covers only ~57% of the 7,398 total real conditions; the INACCURATE/MISMATCH counts this feature
  cites (263/139) are themselves classified estimates, not a confirmed exhaustive count.
- Product/program gating (loan-type applicability) is explicitly out of scope (roadmap `010a`/
  `010b`; Known Blocker #3's sanctioned "assume all rules apply for now" mitigation) — the same
  scoping `000-synthetic-fixture-generation`'s own gating work (T040) narrowly and separately
  addressed for its own 13 predicate checks, not generalized here.
- The authoring UI (`009a`/`009b`/`009c`) does not exist yet; checks evaluated by this feature are
  assumed to arrive via `002b`'s compile-and-sign pipeline or hand-authored fixtures, not through a
  UI this feature builds.
- `005` (the eval-harness CI promotion gate) does not exist yet; this feature ships its own local,
  static eval coverage rather than depending on `005`, consistent with `001a`/`001b`/`002b`/`003a`/
  `003b`.
