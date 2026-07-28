# Feature Specification: Predicate Check Engine

**Feature Branch**: `003a-engine-predicate-checks`
**Created**: 2026-07-08
**Status**: Implemented (2026-07-08, commit `dd94e4b` — all 17 tasks; header corrected from stale "Draft" 2026-07-27, spec adversarial audit)
**Input**: User description: "003a-engine-predicate-checks — deterministic Step-2 QC execution of predicate check-kinds (is_present/is_true) against canonical loan truth values, at the scale of the real MISSING/UNSIGNED/EXPIRED/INCOMPLETE/POLICY archetypes (~2,937 real conditions) — folding in the doc=None short-circuit bug 002a found, not carrying it forward as a dangling note."

**Governs**: `output/ROADMAP.md` §003a, `.specify/memory/constitution.md` Principles I (apply the right checks correctly) and IV (build the core), `output/THESIS.md` Point 1.
**Depends on**: `001a-field-catalog` (implemented — every predicate check's `field_name` must resolve here). `002b-ruleset-compiler-pipeline` (implemented — this feature evaluates the checks 002b's pipeline compiles and signs; 003a does not compile anything itself).
**Foundation this builds on** (proven, not re-specced): `p0/qc_engine/engine.py`'s `_eval_check` predicate branch already implements `is_true`/`is_present` correctly **for non-missing values** — this is proven by `p0/tests/test_p0.py` and the demo ruleset's `note_signed` check. This feature does two things to that existing branch: (1) fixes the one concrete defect `002a` found in it, and (2) proves it correct at the scale of the real archetype set (2,937 conditions across 5 archetypes), not just the one hand-authored demo check.

**What this feature is fixing, precisely:** `p0/experiment_002a/RESULTS.md` ("Discovered engine findings," #1) found that `engine.py`'s predicate branch returns `NOT_APPLICABLE` whenever the truth-document value (`sv.doc`) is `None`, **before** `is_present`'s own logic ever runs — but `p0/eval_synth/taxonomy.json`'s `MISSING` archetype (1,807 of the 2,937 predicate conditions — the single largest archetype in the whole 7,398-condition taxonomy) declares `expected_verdict: FAIL` for exactly this case: a truly-missing document value. Today, `is_present` can **never** produce `FAIL` for the condition it exists to detect. `p0/experiment_002a/score_drafts.py`'s own `_score_predicate` function documents working around this bug rather than exercising it (`NOTE: doc=None short-circuits to NOT_APPLICABLE in the current engine ... that is itself a spike finding, not something this test should paper over`). This spec is where that finding gets fixed instead of worked around again.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A genuinely-missing truth value correctly FAILs a predicate check (Priority: P1)

Today, if the closing-document extraction found no value at all for a field (`sv.doc is None`), the engine reports `NOT_APPLICABLE` for any predicate check on that field — even though "the document is missing entirely" is the literal defect the `MISSING` archetype (and, by the same logic, `UNSIGNED`/`INCOMPLETE`/`POLICY`, which also assert a boolean condition was satisfied) exists to catch. This is the concrete bug `002a` found and is this feature's primary reason to exist.

**Why this priority**: Without this fix, the single largest predicate archetype (1,807 conditions) can never legitimately fail via `is_present` — every genuinely-missing document silently reports as "not applicable" instead of the defect it is. That is a false-clear vector at the largest possible scale, directly violating the SAFE gate.

**Independent Test**: Construct a loan whose truth document has no extracted value (`doc=None`) for a field carrying an `is_present` check; confirm the engine reports `FAIL`, not `NOT_APPLICABLE`. Repeat for an `is_true` check on a `doc=None` field.

**Acceptance Scenarios**:

1. **Given** a loan whose truth document has no extracted value (`doc=None`) for a field, **When** an `is_present`-kind predicate check for that field runs, **Then** the verdict is `FAIL` — not `NOT_APPLICABLE` — with an audit message explaining the field is absent from the document.
2. **Given** the same missing-value case, **When** an `is_true`-kind predicate check for that field runs, **Then** the verdict is `FAIL` for the same reason.
3. **Given** a loan whose truth document has a present-but-failing value (`doc=""` for `is_present`, `doc=False` for `is_true` — the pre-existing, already-correct case), **When** either check runs, **Then** it still correctly `FAIL`s (regression: behavior for non-`None`-but-failing values is unchanged by this fix).

---

### User Story 2 - The engine is proven correct across the real predicate archetype set, not just the demo's one check (Priority: P1)

The demo ruleset carries exactly one hand-authored predicate check (`note_signed`, `is_true`). `003a`'s actual job is the 2,937 real conditions across 5 archetypes — `MISSING` (1,807), `POLICY` (836), `UNSIGNED` (106), `EXPIRED` (98), `INCOMPLETE` (90), per `p0/eval_synth/taxonomy.json` — that `002b`'s compiler will produce as `is_present`/`is_true` checks. The engine must be proven correct against a representative constructed sample of each archetype, not asserted correct by analogy from one check.

> **[Count-basis note, 2026-07-26 spec audit]**: archetype/total counts in this spec were computed
> from the `taxonomy.json` committed at authoring time (7,398 total / 4,192 classified). The
> regenerated taxonomy (010a's all-sheets + column-shift fix, currently an uncommitted working-tree
> change) reports 8,442 total / 4,651 classified, with every archetype count shifted accordingly —
> and ROADMAP Tension 9's Retail-only re-basis (5,520 rows) will shift them again when executed.
> Counts here are kept as-authored: correct against their own era's data, superseded since.


**Why this priority**: This is the actual coverage claim `output/ROADMAP.md` §003a makes ("largest coverage: ~2,937 real conditions") — an untested claim about scale isn't a proven one.

**Independent Test**: For a representative constructed sample of each of the 5 predicate archetypes, build a pass-case and fail-case loan and confirm the engine produces the taxonomy's declared `expected_verdict` (always `FAIL` on the defect case, `PASS` on the clean case) in every instance.

**Acceptance Scenarios**:

1. **Given** a representative constructed sample of `MISSING`/`UNSIGNED`/`INCOMPLETE`/`POLICY`-archetype conditions compiled as `is_present` or `is_true` checks, **When** each is evaluated against its constructed pass-case and fail-case loan, **Then** every check produces the taxonomy-declared `expected_verdict` correctly, in both directions.
2. **Given** a representative constructed sample of the `EXPIRED` archetype, **When** these are compiled today as `is_present`/`is_true` against a pre-computed staleness boolean (not raw dates — see Assumptions for why the engine does no date arithmetic itself), **Then** they evaluate correctly under the same predicate semantics as any other boolean-condition check.
3. **Given** the full constructed fail-case batch across all 5 archetypes, **When** scored, **Then** zero are reported as auto-cleared (zero false-auto-clears — the SAFE gate, at archetype scale, not just spot-checked).

---

### User Story 3 - The confidence gate still correctly withholds auto-clear at archetype scale (Priority: P2)

The engine's existing confidence gate (`DEFAULT_CONFIDENCE_FLOOR`, ruling #8) downgrades a `PASS` to `NEEDS_REVIEW` when the truth-document extraction's confidence is below floor. This mechanism is proven today against one demo check; this feature confirms it continues to hold once the predicate branch is exercised across the real archetype set, rather than assuming it generalizes untested.

**Why this priority**: Lower than US1/US2 because no new logic is introduced — this is regression coverage confirming an existing gate still works once the branch it gates is exercised at real scale, not a new mechanism.

**Independent Test**: For a representative predicate check, construct a `PASS`-worthy loan with `doc_confidence` below `DEFAULT_CONFIDENCE_FLOOR`; confirm the result is `NEEDS_REVIEW`, not an auto-cleared `PASS`. Construct the same case at or above floor; confirm it passes cleanly.

**Acceptance Scenarios**:

1. **Given** a predicate check whose truth value would otherwise `PASS`, but whose `doc_confidence` is below `DEFAULT_CONFIDENCE_FLOOR`, **When** evaluated, **Then** the result is `NEEDS_REVIEW`, not an auto-cleared `PASS`.
2. **Given** the same case with `doc_confidence` at or above floor, **When** evaluated, **Then** the result is a clean `PASS` with no review flag.

---

### Edge Cases

- What happens to `NOT_APPLICABLE` as a status for predicate checks now that the `doc=None` short-circuit is removed? → It is no longer produced by the predicate branch at all in this feature's scope. That status remains legitimate elsewhere (e.g. `agree_categorical`/`agree_numeric` when *both* doc and system are `None` — genuinely no data on either side of a reconciliation), but the predicate/QC phase's "truth document has no value" case is, per the taxonomy, a defect (`FAIL`), not a non-case.
- What happens to a `FAIL` verdict produced from a missing (`None`) doc value with no `doc_confidence` score at all? → The confidence gate only downgrades `PASS` → `NEEDS_REVIEW` (ruling #8); it does not apply to `FAIL`. A `FAIL` is already the conservative outcome — there is no "confident FAIL" ambiguity to resolve.
- What happens to the `EXPIRED` archetype's staleness semantics (e.g. "not provided within 3 days")? → Explicitly out of scope for this feature; see Assumptions. This mirrors how `002a` flagged the `ratio_threshold` vocabulary gap as "a finding for that spec" (003b) rather than solving it on the spot — the same discipline applies here to `EXPIRED`'s date-arithmetic question.
- What happens when a doc value is present but an unexpected type (e.g. a non-boolean truthy string where `is_true` expects a strict boolean)? → `sv.doc is True` already handles this correctly today (identity check, not truthiness) — no change needed; covered by regression tests, not new logic.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine's predicate branch (`kind="predicate"`) MUST evaluate `is_present` checks against a `None` truth-document value as `FAIL`, using `is_present`'s existing logic (`sv.doc is not None and str(sv.doc).strip() != ""`) rather than short-circuiting to `NOT_APPLICABLE` before that logic runs.
- **FR-002**: The engine's predicate branch MUST evaluate `is_true` checks against a `None` truth-document value as `FAIL`, using `is_true`'s existing logic (`sv.doc is True`) rather than short-circuiting to `NOT_APPLICABLE`.
- **FR-003**: The predicate branch's blanket early-return on `sv.doc is None` MUST be removed. `NOT_APPLICABLE` is no longer a producible status for `kind="predicate"` checks in this feature's scope. Loan-type/product applicability gating remains deferred to roadmap `010a/b`, per the project's existing "assume all rules apply for now" mitigation (Known Blocker #3) — this feature does not invent a substitute not-applicable mechanism to compensate for that deferral.
- **FR-004**: The engine MUST correctly evaluate a representative constructed sample of each of the 5 real predicate archetypes (`MISSING`, `UNSIGNED`, `EXPIRED`, `INCOMPLETE`, `POLICY` — `p0/eval_synth/taxonomy.json`) against both a constructed pass-case and fail-case loan, producing the taxonomy's declared `expected_verdict` in every instance.
- **FR-005**: Zero-false-auto-clear MUST hold across the full constructed fail-case sample from FR-004 — no fail-worthy predicate condition may be reported as auto-cleared, verified by test.
- **FR-006**: The existing confidence gate (auto-clear withheld when `doc_confidence` is below `DEFAULT_CONFIDENCE_FLOOR`) MUST continue to apply correctly to predicate-kind `PASS` verdicts at archetype scale — verified by test, not assumed to generalize from the single demo check it's proven against today.
- **FR-007**: This feature MUST NOT introduce a new predicate vocabulary, check kind, or date-arithmetic logic to resolve the `EXPIRED` archetype's staleness semantics. Whether `EXPIRED` conditions can be safely modeled as compiler-precomputed booleans (mirroring `002a`'s `predicate-08` finding about opaque pre-computed comparisons) or need a new predicate/check kind is an open question for `002b`'s compiler policy and Kayla's eventual review — not resolved by this engine spec.
- **FR-008**: This feature MUST NOT build `ratio_threshold` (`003b`) or reconcile (`003c`) evaluation logic, product/program gating (`010a/b`), the authoring UI (`009a/b/c`), or any runtime LLM evaluation path (constitution Principle II). Its surface is the predicate branch of `qc_engine.engine.py` only.

### Key Entities

- **Check** (existing, `p0/qc_engine/ruleset.py`): `kind="predicate"`, `predicate="is_true"|"is_present"` — no new fields introduced by this feature.
- **CheckResult** (existing, `p0/qc_engine/engine.py`): `status` now correctly includes `FAIL` for missing-doc predicate cases; `NOT_APPLICABLE` is removed from this kind's producible statuses (FR-003).
- **PredicateArchetypeFixture** (new, test-only): constructed pass-case/fail-case loan pairs per archetype (`MISSING`/`UNSIGNED`/`EXPIRED`/`INCOMPLETE`/`POLICY`) — the local eval coverage this feature ships with, independent of `005` (the CI eval-harness promotion gate), which does not exist yet and which `003a` explicitly does not depend on.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A constructed loan with `doc=None` on a field carrying an `is_present` or `is_true` check produces `FAIL`, not `NOT_APPLICABLE` — verified by test, confirming the exact behavior change from today's engine.
- **SC-002**: 100% correct verdicts (both pass-case and fail-case directions) across a constructed representative sample of all 5 predicate archetypes (`MISSING`/`UNSIGNED`/`EXPIRED`/`INCOMPLETE`/`POLICY`), drawn from real conditions in `p0/eval_synth/taxonomy.json`.
- **SC-003**: Zero false-auto-clears across the full constructed fail-case batch from SC-002.
- **SC-004**: The confidence gate correctly downgrades a low-confidence predicate `PASS` to `NEEDS_REVIEW` (and does not downgrade an at-or-above-floor `PASS`), verified by test in both directions, at archetype scale.
- **SC-005**: All pre-existing `p0/tests/test_p0.py` and `p0/eval_synth` tests continue to pass unmodified after this feature's change — zero regression, matching the bar every prior spec's implementation has held (`001a`: 19/19, `001b`: 18/18, `002b`: 31/31, all "zero regression").

## Assumptions

- This feature hardens the already-implemented predicate branch in `p0/qc_engine/engine.py` (`is_true`/`is_present`); it does not invent a new check kind or predicate vocabulary.
- The 5 predicate archetypes (`MISSING`, `UNSIGNED`, `EXPIRED`, `INCOMPLETE`, `POLICY` — 2,937 real conditions per `taxonomy.json`) are assumed to map onto today's `is_true`/`is_present` vocabulary. Per `output/ROADMAP.md` §003a's own coverage caveat, this is confirmed only for the 56.7% of conditions `taxonomy.json` has actually classified; the remaining ~43% are *believed*, pending Kayla's rules review, to be the same kinds — not yet confirmed.
- `EXPIRED`'s staleness conditions (e.g. "not provided within 3 days") are assumed, for this feature's scope, to arrive at the engine as an already-computed boolean (produced upstream by `002b`'s compiler or a future extraction step) — the engine itself does no date arithmetic here. Whether that assumption holds is an open question for `002b`/Kayla, not resolved by this spec (see FR-007).
- Product/program gating (loan-type applicability) is explicitly out of scope (roadmap `010a/b`; Known Blocker #3's sanctioned "assume all rules apply for now" mitigation) — this feature does not introduce a not-applicable concept to compensate for ungated checks.
- `005` (the eval-harness CI promotion gate) does not exist yet; this feature ships its own local, static eval coverage (constructed pass/fail fixtures per archetype) rather than depending on `005`, consistent with how `001a`/`001b`/`002b` each shipped independent of it.
- The authoring UI (`009a/b/c`) does not exist yet; checks evaluated by this feature are assumed to arrive via `002b`'s compile-and-sign pipeline or hand-authored fixtures, not through a UI this feature builds.
