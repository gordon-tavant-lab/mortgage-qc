# Feature Specification: Ratio/Threshold Check Engine

**Feature Branch**: `003b-engine-ratio-threshold-checks`
**Created**: 2026-07-09
**Status**: Implemented (2026-07-09, commit `b87d987` — all 19 tasks; header corrected from stale "Draft" 2026-07-27, spec adversarial audit)
**Input**: User description: "003b-engine-ratio-threshold-checks — deterministic Step-2 QC
execution of `ratio_threshold` check-kinds against canonical loan truth values, at the scale of
the real THRESHOLD archetype (~853 real conditions) — closing the `ratio` vocabulary gap 002a
found (LTV/DTI-only), not carrying it forward as a dangling note."

**Governs**: `output/ROADMAP.md` §003b, `.specify/memory/constitution.md` Principles I (apply the
right checks correctly) and IV (build the core), `output/THESIS.md` Point 1 (the exact class of
boundary math the G3 bake-off flagged as buyback-risk).
**Depends on**: `001a-field-catalog` (implemented — a `field_value`-mode check's `field_name` must
resolve here). `002b-ruleset-compiler-pipeline` (implemented — this feature evaluates the checks
002b's pipeline compiles and signs; 003b does not compile anything itself). Independent of `003a`
(implemented) — both slice the QC phase by check-kind, not by dependency.
**Foundation this builds on** (proven, not re-specced): `p0/qc_engine/engine.py`'s `_eval_check`
`ratio_threshold` branch and `p0/qc_engine/money.py`'s `ltv_percent`/`dti_percent` already
implement LTV/DTI correctly in Decimal with pinned `ROUND_HALF_EVEN` rounding — proven by
`p0/tests/test_p0.py::test_ltv_boundary_exact` and the demo ruleset's `chk-ltv-max` check. This
feature does three things to that existing branch: (1) closes the vocabulary gap `002a` found (only
`ltv`/`dti` are supported; several real THRESHOLD rows are not ratios at all), (2) removes a
dead/no-op line found while reading the branch closely, and (3) proves the branch correct at the
scale of the real THRESHOLD archetype (853 conditions), not just the one hand-authored demo check.

**What this feature is fixing, precisely:** `p0/experiment_002a/RESULTS.md` ("Discovered engine
findings," #2) found that `engine.py`'s `ratio_threshold` branch only supports `chk.ratio in
("ltv", "dti")` — but real sampled THRESHOLD rows are not always ratios. `ratio_threshold-00`
("Sect 203(h)... minimum credit score of 500") is a single-field numeric floor, not a
loan-amount/property-value or debt/income ratio; the LLM compiler, correctly instructed to use only
`ltv`/`dti`, honestly disclosed in its own `plain_english_restatement` that `ltv` was "the closest
structural analogue," not a real match (`p0/experiment_002a/artifacts/sme_review_package.md`,
`ratio_threshold-00`/`-01`). Forcing every THRESHOLD condition through the ratio vocabulary would
either misclassify real defects or block the compiler from emitting a runnable check for the
non-ratio ones. This spec closes that gap for the clean, single-field-floor case (proven by the
real `ratio_threshold-00` row); the genuinely multi-condition rows (`-01`/`-02`/`-03`/`-04`, each of
which the 002a review found bundles more than one comparison into a single AMQ row) remain an open
compiler-decomposition question, explicitly out of scope here (see Assumptions) — the same
discipline `003a` applied to `EXPIRED`'s staleness semantics.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A single-field numeric floor/ceiling correctly evaluates without forcing an LTV/DTI fit (Priority: P1)

Today, `ratio_threshold`'s `ratio` field only accepts `"ltv"` or `"dti"` — any other value raises
`ValueError("unknown ratio ...")`, and the only way to represent "the borrower's credit score must
be at least 500" is to force it through the LTV/DTI ratio machinery, which computes the wrong
quantity entirely. This is the concrete gap `002a` found and is this feature's primary reason to
exist.

**Why this priority**: Without this fix, no THRESHOLD condition that is a plain numeric floor
(rather than a computed ratio) can be compiled into a runnable, *correct* check — the compiler is
forced to either raise an interpretation error or silently misrepresent the condition as an LTV/DTI
comparison it is not. That is a false-clear vector (a wrong comparison quantity can pass a loan that
should fail) at real archetype scale.

**Independent Test**: Construct a loan whose truth document carries a numeric field (e.g.
`credit_score = 480`) below an authored floor (`threshold = "500"`, `operator = ">="`); confirm a
`ratio_threshold` check with `ratio="field_value"` and `field_name="credit_score"` reports `FAIL`.
Construct the same loan at/above the floor (`credit_score = 620`); confirm it reports `PASS`.

**Acceptance Scenarios**:

1. **Given** a loan whose truth document has a numeric value below an authored floor for a
   `ratio_threshold` check with `ratio="field_value"`, **When** the check runs, **Then** the verdict
   is `FAIL`, comparing the field's own truth value against `threshold` via `operator` — not a
   computed LTV/DTI ratio.
2. **Given** the same field at or clear of the floor, **When** the check runs, **Then** the verdict
   is `PASS`.
3. **Given** a loan whose truth document has no value at all (`doc=None`) for the field a
   `field_value` check references, **When** the check runs, **Then** the verdict is
   `NOT_APPLICABLE` — mirroring the existing LTV/DTI behavior when the underlying facts are absent
   (the comparison cannot be made at all), which is a distinct case from `003a`'s predicate
   `MISSING` fix (see Assumptions for why these two "missing" cases are handled differently on
   purpose).
4. **Given** the pre-existing `ltv`/`dti` cases (`chk.ratio in ("ltv", "dti")`, `field_name=""`),
   **When** either runs, **Then** behavior is byte-for-byte unchanged (regression).

---

### User Story 2 - The engine is proven correct across the real THRESHOLD archetype set, not just the demo's one check (Priority: P1)

The demo ruleset carries exactly one hand-authored `ratio_threshold` check (`chk-ltv-max`, LTV
only). `003b`'s actual job is the 853 real THRESHOLD conditions `p0/eval_synth/taxonomy.json`
(**949** in the regenerated, currently-uncommitted post-010a taxonomy — count-basis note as in `003a`, 2026-07-26 audit)
records, spanning LTV, DTI, and non-ratio numeric floors like the real
`ratio_threshold-00`/`-01`/`-02`/`-03`/`-04` rows `002a` sampled directly from
`demo/rules/*.xlsx`.

**Why this priority**: This is the actual coverage claim `output/ROADMAP.md` §003b makes
("~853 real conditions") — an untested claim about scale isn't a proven one. It is also where the
G3 bake-off's buyback finding lives (boundary math at the LTV/DTI edge), so boundary correctness is
part of this story, not a footnote.

**Independent Test**: For LTV, DTI, and the real `ratio_threshold-00` (credit-score-floor) row,
build a pass-case and fail-case loan (plus an exact-boundary case for LTV/DTI) and confirm the
engine produces the correct verdict in every instance, using Decimal `ROUND_HALF_EVEN` throughout.

**Acceptance Scenarios**:

1. **Given** representative LTV and DTI conditions at, above, and below their authored thresholds,
   **When** evaluated, **Then** every case produces the correct verdict, including the exact-boundary
   case (value equals threshold under a `<=` operator: `PASS`).
2. **Given** the real `ratio_threshold-00` condition (credit score floor) compiled as a
   `field_value`-mode check, **When** evaluated against a below-floor and an at/above-floor loan,
   **Then** both produce the correct verdict.
3. **Given** the full constructed fail-case batch across LTV, DTI, and `field_value`, **When**
   scored, **Then** zero are reported as auto-cleared (zero false-auto-clears — the SAFE gate, at
   archetype scale, not just spot-checked).

---

### User Story 3 - The confidence gate correctly applies to `field_value` checks, closing a gap LTV/DTI checks structurally cannot close (Priority: P2)

The engine's existing confidence gate (`DEFAULT_CONFIDENCE_FLOOR`, ruling #8) downgrades a `PASS` to
`NEEDS_REVIEW` when the truth-document extraction's confidence is below floor. Because `ltv`/`dti`
checks read `loan.facts` (not a catalog `field_name`), they resolve to the model's default empty
`SourceValue` at the confidence-gate check and so **never** carry a real `doc_confidence` —
structurally, the LTV/DTI path cannot exercise this gate today. `field_value` checks, by contrast,
read a real catalog field via `loan.get(chk.field_name)`, so they are the first `ratio_threshold`
checks that actually flow through the confidence gate. This story proves that flow is correct, not
assumed.

**Why this priority**: Lower than US1/US2 because no gate logic changes — this proves an existing
mechanism newly reachable by this feature's own new code path behaves correctly, rather than
introducing a new mechanism.

**Independent Test**: Construct a `field_value` check that would otherwise `PASS`, on a loan whose
`doc_confidence` for that field is below `DEFAULT_CONFIDENCE_FLOOR`; confirm the result is
`NEEDS_REVIEW`. Construct the same case at or above floor; confirm it passes cleanly.

**Acceptance Scenarios**:

1. **Given** a `field_value` check whose truth value would otherwise `PASS`, but whose
   `doc_confidence` is below `DEFAULT_CONFIDENCE_FLOOR`, **When** evaluated, **Then** the result is
   `NEEDS_REVIEW`, not an auto-cleared `PASS`.
2. **Given** the same case with `doc_confidence` at or above floor, **When** evaluated, **Then** the
   result is a clean `PASS` with no review flag.

---

### Edge Cases

- What happens to the dead `res.threshold = chk.threshold if hasattr(res, "threshold") else None`
  line in the existing branch? → `hasattr(res, "threshold")` is always `False` the first time it
  runs (`CheckResult` declares no `threshold` field), so this line always assigns `None` to a
  dynamically-created attribute that `CheckResult.to_dict()` never serializes and no other code
  reads (confirmed by repo-wide search). It is dead, no-op code — removed as part of this feature's
  hardening pass (the audit-relevant value is already carried correctly by the very next line,
  `res.tolerance = chk.threshold`). This is a cleanup, not a behavior change (SC-004).
- Why does a missing `field_value` resolve to `NOT_APPLICABLE` here, when `003a` fixed the exact
  same "missing means NOT_APPLICABLE" pattern to mean `FAIL` for predicate checks? → The two kinds
  answer different questions. A `predicate` `is_present` check's entire job is "does this field
  exist" — for that check, missing *is* the defect. A `ratio_threshold` check's job is "is this
  value's *magnitude* within bounds" — if the value is absent, the magnitude comparison cannot be
  made at all, which is the same "genuinely no data" case the existing LTV/DTI `NOT_APPLICABLE`
  already models when `loan.facts` lacks the inputs. Presence is a separate, `003a`-scoped concern
  (a compiler that cares about both would emit two checks: an `is_present` predicate and a
  `field_value` threshold). This feature does not blur that line.
- What happens to the non-clean real rows (`ratio_threshold-01/02/03/04`) that `002a` found bundle
  more than one comparison into a single AMQ row (e.g. `-01`'s "coverage amount, deductible, AND
  agency rating")? → Explicitly out of scope. Whether these decompose into multiple checks at
  compile time, need a new check kind, or are handled another way is `002b`'s compiler-policy
  question (and eventually Kayla's), not resolved by this engine spec — mirrors how `003a` left
  `EXPIRED`'s staleness semantics for `002b`/Kayla rather than solving it on the spot.
- What if a `field_value` check's `field_name` does not resolve to a catalog entry? → Caught by the
  existing SAFE-gate referential-integrity check (`catalog.py::validate_referential_integrity`),
  unmodified by this feature — unlike `ltv`/`dti` checks (`field_name=""`, deliberately exempted
  because they read `loan.facts`, not a catalog field), a `field_value` check has a real
  `field_name` and is not exempted, so an unresolved reference is caught the same way any other
  check's unresolved reference is (no new exemption logic needed).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine's `ratio_threshold` branch (`kind="ratio_threshold"`) MUST support a new
  `ratio="field_value"` mode that compares the truth (`doc`) value of `chk.field_name` directly
  against `chk.threshold` via `chk.operator`, in Decimal (`qc_engine.money.to_decimal`) — no ratio
  is computed, unlike `ltv`/`dti`.
- **FR-002**: When a `field_value` check's referenced field has no truth value (`sv.doc is None`),
  the engine MUST report `NOT_APPLICABLE` with an explanatory message, mirroring the existing
  `ltv`/`dti` behavior when their underlying `loan.facts` inputs are absent (see Edge Cases for why
  this differs from `003a`'s predicate fix).
- **FR-003**: The existing `ltv`/`dti` code paths and their `NOT_APPLICABLE`-on-missing-facts,
  boundary-comparison, and rounding behavior MUST be unchanged by this feature (regression).
- **FR-004**: The dead `res.threshold = chk.threshold if hasattr(res, "threshold") else None` line
  (confirmed no-op: always assigns `None`, never read elsewhere, not part of `CheckResult`'s
  declared fields or `to_dict()`) MUST be removed. The audit-relevant threshold value continues to
  be carried by the pre-existing `res.tolerance = chk.threshold` assignment — no audit information
  is lost.
- **FR-005**: The engine MUST correctly evaluate representative constructed samples of LTV, DTI, and
  the real `ratio_threshold-00` credit-score-floor condition (drawn from
  `p0/experiment_002a/artifacts/sampled_rows.json`, not fabricated) against both a pass-case and a
  fail-case loan, including an exact-boundary case for LTV/DTI, producing the correct verdict in
  every instance.
- **FR-006**: Zero-false-auto-clear MUST hold across the full constructed fail-case sample from
  FR-005 — no fail-worthy `ratio_threshold` condition may be reported as auto-cleared, verified by
  test.
- **FR-007**: The existing confidence gate (auto-clear withheld when `doc_confidence` is below
  `DEFAULT_CONFIDENCE_FLOOR`) MUST correctly apply to `field_value`-mode `PASS` verdicts, verified by
  test in both directions — the first `ratio_threshold` sub-kind to structurally exercise this gate
  (see US3).
- **FR-008**: This feature MUST NOT introduce a new `Check.kind` (the fix stays within the existing
  `ratio_threshold` kind's `ratio` vocabulary), MUST NOT attempt to decompose the multi-condition
  real rows (`ratio_threshold-01/02/03/04`) into runnable checks, MUST NOT build predicate (`003a`,
  already implemented) or reconcile (`003c`) evaluation logic, product/program gating (`010a/b`),
  the authoring UI (`009a/b/c`), or any runtime LLM evaluation path (constitution Principle II).

### Key Entities

- **Check** (existing, `p0/qc_engine/ruleset.py`): `kind="ratio_threshold"`, `ratio` now accepts
  `"ltv"|"dti"|"field_value"` — no new dataclass field introduced; `field_value` mode is a new
  accepted value for the existing `ratio` string field, and uses the existing `field_name`,
  `threshold`, `operator` fields exactly as `ltv`/`dti` do.
- **CheckResult** (existing, `p0/qc_engine/engine.py`): unchanged shape; the dead `threshold`
  pseudo-attribute (FR-004) is removed, not replaced.
- **ThresholdArchetypeFixture** (new, test-only): constructed pass-case/fail-case/boundary loan
  sets for LTV, DTI, and the real `ratio_threshold-00` row — the local eval coverage this feature
  ships with, independent of `005` (the CI eval-harness promotion gate, which does not exist yet),
  same precedent `003a` established.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A constructed loan with a below-floor numeric field value and a `field_value`-mode
  `ratio_threshold` check produces `FAIL`; the same field at/above floor produces `PASS` — verified
  by test, confirming the new vocabulary works end-to-end.
- **SC-002**: 100% correct verdicts (pass, fail, and exact-boundary directions) across constructed
  representative LTV, DTI, and `field_value` (real `ratio_threshold-00`) cases.
- **SC-003**: Zero false-auto-clears across the full constructed fail-case batch from SC-002.
- **SC-004**: The dead `res.threshold` line is removed with no change to any test's expected output
  and no change to the P0 determinism digest (proving it was truly inert).
- **SC-005**: The confidence gate correctly downgrades a low-confidence `field_value` `PASS` to
  `NEEDS_REVIEW` (and does not downgrade an at-or-above-floor `PASS`), verified by test in both
  directions.
- **SC-006**: All pre-existing `p0/tests/test_p0.py` and `p0/eval_synth` tests continue to pass
  unmodified after this feature's change — zero regression, matching the bar every prior spec's
  implementation has held (`001a`: 19/19, `001b`: 18/18, `002b`: 31/31, `003a`: 64/64 cumulative,
  all "zero regression").

## Assumptions

- This feature hardens the already-implemented `ratio_threshold` branch in
  `p0/qc_engine/engine.py`; it does not invent a new check kind — the vocabulary gap `002a` found is
  closed by widening `ratio`'s accepted values, the minimal change consistent with how `003a`
  resolved its own finding (deleting one early-return, not adding a new kind).
- The real `ratio_threshold-00` row ("minimum credit score of 500") is treated as the representative
  proof case for `field_value` because `002a`'s own review confirmed it is a genuine single-field
  numeric floor with no compound conditions — unlike `-01`/`-02`/`-03`/`-04`, which the review found
  bundle multiple comparisons into one AMQ row and are explicitly out of scope (FR-008).
  Whether `field_value` covers the *rest* of the 853 THRESHOLD conditions once `002b`'s compiler
  reads the real workbook at scale is not confirmed by this feature — it proves the engine
  *mechanism* is correct for the archetype's clean case, the same limited claim `003a` made about
  predicate scale (see `003a` plan.md's Scale/Scope note).
  Per `output/ROADMAP.md` §003b's own coverage caveat inherited from §003a, this is confirmed only
  for the ~57% of the 7,398 total conditions `taxonomy.json` has actually classified.
  `005` (the eval-harness CI promotion gate) does not exist yet; this feature ships its own local,
  static eval coverage rather than depending on `005`, consistent with `001a`/`001b`/`002b`/`003a`.
- Product/program gating (loan-type applicability) is explicitly out of scope (roadmap `010a/b`;
  Known Blocker #3's sanctioned "assume all rules apply for now" mitigation).
- The authoring UI (`009a/b/c`) does not exist yet; checks evaluated by this feature are assumed to
  arrive via `002b`'s compile-and-sign pipeline or hand-authored fixtures, not through a UI this
  feature builds.
