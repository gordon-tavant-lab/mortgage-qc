# Feature Specification: Loan Disposition (Composition Layer)

**Feature Branch**: `004-loan-disposition`
**Created**: 2026-07-16
**Status**: Implemented (2026-07-16, commit `2994794` — binary Disposition + open review_reason tags; header corrected from stale "Draft" 2026-07-27, spec adversarial audit)
**Input**: User description: "004-loan-disposition — compose a loan's full set of per-check verdicts
(predicate, ratio_threshold, reconcile) into one deterministic, auditable per-loan disposition:
`AUTO_CLEARED` vs `NEEDS_REVIEW`, with `NEEDS_REVIEW` carrying an open, multi-label set of reason
tags (a genuine QC defect is one such tag among peers, not a separate top-level state) — the
human-in-the-loop intercept, where each tag is a distinct concern/channel to communicate to a human
reviewer. Revised 2026-07-16 from an initial three-state (`AUTO_CLEARED`/`EXCEPTION`/`NEEDS_REVIEW`)
draft per Gordon's explicit design direction (grilled and confirmed, not assumed)."

**Governs**: `output/ROADMAP.md` §004, `.specify/memory/constitution.md` Principle I (determinism),
Principle V (the two-step RECONCILE/QC model — a FLAG is informational, never a failure), Principle
III (eval is foundational), Principle VII (configuration is authored data — the reason-tag vocabulary
is open, not a closed enum baked into control flow).
**Depends on**: `003a-engine-predicate-checks` (implemented), `003b-engine-ratio-threshold-checks`
(implemented), `003c-engine-reconcile-checks` (implemented) — this is the one feature that genuinely
needs the full engine, composing verdicts across all three check-kinds into one decision.
**Foundation this builds on** (proven, not re-specced): `p0/qc_engine/engine.py`'s `RunResult`
already carries `qc_failures`, `needs_review`, `flags`, and a derived `auto_cleared` boolean
(`not qc_failures and not needs_review`) — proven correct by every existing test that asserts against
it, including `003c`'s reconcile tests. The binary split this feature formalizes
(`AUTO_CLEARED`/`NEEDS_REVIEW`) is already exactly what `auto_cleared` computes; this feature does not
change that boundary. What it adds is genuinely new: a small, structural way for a `CheckResult` to
say *why* it needs review, since today that reason lives only in free-text `message` strings.

**What this feature is fixing, precisely:** `RunResult.auto_cleared` is a boolean — it already
answers "can this loan be auto-cleared?" correctly, and this feature does not touch that answer. What
it cannot do today is tell a human reviewer *what kind of attention* a loan needs. `needs_review`
(the property) already conflates at least three structurally distinct concerns: (1) a genuine
QC-phase compliance defect (predicate or ratio_threshold `FAIL`/`WARNING`) — a real exception a human
must judge; (2) the confidence gate withholding a low-confidence `PASS` (ruling #8) — not a defect,
an extraction-trust problem; (3) a reconcile check that could not fully resolve because one side of
the comparison was absent (`NEEDS_REVIEW` status) — not a defect, a data-completeness problem. Today
none of these is distinguishable without parsing each `CheckResult.message`'s free text, which is
fragile and not something a routing/display layer should ever do. Per Gordon's explicit direction,
this feature does three things: (a) keeps the top-level `Disposition` binary
(`AUTO_CLEARED`/`NEEDS_REVIEW`), matching `auto_cleared`'s existing boundary exactly; (b) gives each
contributing `CheckResult` a small, structural `review_reason` tag at the exact code site that
already knows why it isn't clean — no new central dispatch table, so future concerns (a new
archetype, a new gate) are added by tagging their own site, not by editing this feature's logic; (c)
aggregates a loan's full set of tags as `review_reasons` — a loan can carry more than one
simultaneously, since it can genuinely have more than one real concern at once. Tags are DATA the
disposition carries, not a routing mechanism — which team/queue reads a given tag is explicitly out
of scope (see FR-007), reserved for `008` or a later feature.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A loan's disposition is binary, and every reason it needs review is a distinct, inspectable tag (Priority: P1)

Today, telling whether a loan needs review at all requires reading `qc_failures`/`needs_review`
separately; telling *why*, beyond that, requires reading free-text messages. This feature makes
"needs review, and here is the full set of concerns" one deterministic computation.

**Why this priority**: This is `004`'s entire reason to exist (per the contrarian review that found
disposition homeless across 006/007/008) — and per Gordon's direction, the *reason tags* are the
actual product value: they're what will let a future queue route "confidence problem" loans to a
different concern/channel than "genuine underwriting defect" loans, without inventing a second
parallel classification system later.

**Independent Test**: Construct loans covering each individually-known reason a check can require
review today (a QC-phase failure, a confidence-withheld pass, a reconcile one-side-absent), plus a
loan with two of these simultaneously; confirm the disposition is `NEEDS_REVIEW` in every case, and
`review_reasons` contains exactly the expected tag(s) — the correct set, not just a non-empty one.

**Acceptance Scenarios**:

1. **Given** a loan with no QC failures and nothing needing review, **When** its disposition is
   computed, **Then** it is `AUTO_CLEARED` and `review_reasons` is empty.
2. **Given** a loan with one QC-phase failure (predicate or ratio_threshold), **When** its
   disposition is computed, **Then** it is `NEEDS_REVIEW` and `review_reasons` contains `"EXCEPTION"`.
3. **Given** a loan with one confidence-withheld `PASS` (no QC failure), **When** its disposition is
   computed, **Then** it is `NEEDS_REVIEW` and `review_reasons` contains `"LOW_CONFIDENCE"`, not
   `"EXCEPTION"`.
4. **Given** a loan with one reconcile check resolving one-side-absent (no QC failure), **When** its
   disposition is computed, **Then** it is `NEEDS_REVIEW` and `review_reasons` contains
   `"SOURCE_INCOMPLETE"`, not `"EXCEPTION"`.
5. **Given** a loan with both a QC-phase failure AND a confidence-withheld pass, **When** its
   disposition is computed, **Then** it is `NEEDS_REVIEW` and `review_reasons` contains **both**
   `"EXCEPTION"` and `"LOW_CONFIDENCE"` — multi-label, neither reason suppresses the other (per
   Gordon's explicit direction: reasons are peers, not a precedence chain).

---

### User Story 2 - FLAGs never contribute a reason tag, at any combination (Priority: P1)

The two-step model's entire safety promise (Principle V) is that a reconcile `FLAG` is informational
and never blocks auto-clear. This feature must prove that holds through the tag mechanism too — a
`FLAG` must never itself produce a `review_reasons` entry.

**Why this priority**: Equal priority to US1 — a `FLAG` silently producing a reason tag would
systematically route clean loans into the human-review queue the moment this ships, defeating the
entire auto-clear promise.

**Independent Test**: Construct a loan with one or more genuine reconcile divergences (proven-real
per `003c`'s independence-guard discipline) and otherwise clean QC — confirm the disposition is
`AUTO_CLEARED` and `review_reasons` is empty, regardless of how many `FLAG`s are present.

**Acceptance Scenarios**:

1. **Given** a loan with one reconcile `FLAG` and nothing else, **When** its disposition is
   computed, **Then** it is `AUTO_CLEARED` with an empty `review_reasons`.
2. **Given** a loan with multiple reconcile `FLAG`s (`agree_categorical` and `agree_numeric` both)
   and nothing else, **When** its disposition is computed, **Then** it is still `AUTO_CLEARED` with
   an empty `review_reasons`.
3. **Given** a loan with a reconcile `FLAG` **and** a genuine QC failure, **When** its disposition is
   computed, **Then** `review_reasons` contains `"EXCEPTION"` only — never a tag attributable to the
   `FLAG` itself.

---

### User Story 3 - The reason-tag vocabulary is open, not a closed enum the composition logic must know about (Priority: P1)

Per Gordon's direction, tags are authored at the site that already knows the reason (a specific
`_eval_check` branch), not centrally enumerated and dispatched. This story proves the mechanism
supports that — adding a new tag-producing site must not require touching the disposition/aggregation
logic itself.

**Why this priority**: Equal priority to US1/US2, not lower — an implementation that hardcodes "if
message contains X then tag Y" (string-matching) would violate the actual design intent even if every
test in US1/US2 passed; this story is what proves the *mechanism*, not just today's three tag values,
is right.

**Independent Test**: Add a fourth, previously-nonexistent tag value to a test-only check branch (not
touching the aggregation code at all) and confirm it surfaces correctly in `review_reasons` — proving
the aggregation is generic over tag identity, not a hardcoded switch.

**Acceptance Scenarios**:

1. **Given** a `CheckResult` carrying a `review_reason` value the aggregation logic has never seen
   before, **When** the loan's disposition is computed, **Then** that value appears verbatim in
   `review_reasons` — the aggregator does not filter, translate, or reject unrecognized tags.
2. **Given** two checks on the same loan carrying the *same* tag value, **When** the loan's
   disposition is computed, **Then** `review_reasons` contains that value once (a set, not a
   multiset) — repetition across checks is not a distinct concern to surface twice.

### Edge Cases

- What happens to a `qc_failures` entry with `severity="WARNING"` (not `FAIL`)? → Still tagged
  `"EXCEPTION"` — `RunResult.qc_failures` already includes `status in ("FAIL", "WARNING")`; this
  feature does not change that inclusion, only tags it.
- Does 004 build the mechanism for delivering `review_reasons` to a specific human/team/queue? → No.
  Tags are data attached to the disposition; routing (which tag goes to which reviewer, how it's
  queued/notified) is explicitly `008`'s job (FR-007) — building it here would absorb scope the
  roadmap already assigned elsewhere.
- What is the *initial* tag vocabulary, given it's meant to be open? → Three tags this feature
  populates from code paths that already exist and already know their reason: `"EXCEPTION"` (QC-phase
  `FAIL`/`WARNING`), `"LOW_CONFIDENCE"` (confidence-gate downgrade), `"SOURCE_INCOMPLETE"` (reconcile
  one-side-absent). This is a starting vocabulary, not an exhaustive enum — US3 proves new tags don't
  require touching this feature's aggregation logic, only the site that produces them.
- What happens when `RunResult.results` is empty (a ruleset with zero applicable checks — the exact
  shape `000-synthetic-fixture-generation`'s own applicability-gating work produces per loan)? → No
  contributing checks → `AUTO_CLEARED`, `review_reasons` empty. Inherited `auto_cleared` behavior,
  unchanged; an empty result set is not itself a defect.
- Does this require the doc-vs-doc reconcile capability `003c` explicitly did not build
  (`output/ROADMAP.md` Tension #5)? → No. Tag aggregation composes over whatever `CheckResult`s a
  ruleset actually produced; a future doc-vs-doc kind would just tag itself at its own site and flow
  through unchanged.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST compute exactly one binary `Disposition` value per loan:
  `NEEDS_REVIEW` if the loan has any `CheckResult` carrying a `review_reason` tag; else
  `AUTO_CLEARED`.
- **FR-002**: `CheckResult` MUST gain a small, structural way to carry its own reason for needing
  review (a `review_reason` field or equivalent), populated at the existing code site that already
  determines the check's status — not derived after the fact by parsing `message` text.
- **FR-003**: The three code paths that already produce a review-worthy status MUST populate a
  `review_reason`: QC-phase `FAIL`/`WARNING` → `"EXCEPTION"`; the confidence-gate downgrade →
  `"LOW_CONFIDENCE"`; reconcile one-side-absent → `"SOURCE_INCOMPLETE"`. This is the initial
  vocabulary, authored at each site individually — no central enum or dispatch table maps status to
  tag.
- **FR-004**: A loan's `review_reasons` MUST be the set-union (not list, not precedence-ordered) of
  every contributing `CheckResult`'s `review_reason` — a loan may carry multiple tags simultaneously
  when multiple distinct concerns are present (US1 Scenario 5).
- **FR-005**: A reconcile `FLAG` MUST NOT, by itself or in any combination, produce a
  `review_reason`/contribute to `NEEDS_REVIEW` — proven across representative combinations (US2).
- **FR-006**: The binary `Disposition` MUST be provably equivalent to the existing `auto_cleared`
  boolean: `auto_cleared is True` if and only if `disposition == "AUTO_CLEARED"`, for every
  constructed case in this feature's test suite.
- **FR-007**: This feature MUST NOT define routing/delivery logic — which reviewer, team, or queue a
  given `review_reason` maps to is explicitly out of scope, reserved for `008` (the exception-review
  UI) or a later feature.
- **FR-008**: This feature MUST NOT build `008`'s UI itself, the confidence-withhold gate mechanism
  (`006`, already implemented — this feature only tags its existing output), or product/program
  gating (`010a`/`010b`).
- **FR-009**: Tag/disposition computation MUST be a pure function of existing `CheckResult` data — no
  new I/O, network, wall-clock, or LLM call (constitution Principle I).
- **FR-010**: This feature MUST NOT require or depend on the doc-vs-doc reconcile capability `003c`
  explicitly deferred (`output/ROADMAP.md` Tension #5).

### Key Entities

- **Disposition** (new): `"AUTO_CLEARED"` or `"NEEDS_REVIEW"` — a pure derivation from a loan's
  `RunResult`. No new fields on `CanonicalLoan`, `Check`, or `Ruleset`.
- **review_reason** (new, on `CheckResult`): an open-vocabulary string, populated only when the
  check's own status contributes to `NEEDS_REVIEW` (`None`/absent for `PASS`, `NOT_APPLICABLE`, or a
  `FLAG`). Authored per code site, not centrally enumerated.
- **review_reasons** (new, on the loan-level disposition result): the set of all distinct
  `review_reason` values across a loan's contributing checks.
- **RunResult** (existing, `p0/qc_engine/engine.py`): gains the disposition + `review_reasons`
  computation; `qc_failures`, `needs_review`, `flags`, `auto_cleared` are read, not modified.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of constructed representative loans (clean; each of the three known reasons alone;
  two reasons together; FLAG-only; FLAG-plus-a-reason) resolve to the correct `Disposition` AND the
  correct exact `review_reasons` set, per FR-001/003/004.
- **SC-002**: Zero instances, across the full constructed sample, of a reconcile `FLAG` producing a
  `review_reason` or a non-`AUTO_CLEARED` disposition by itself.
- **SC-003**: 100% agreement between the new `Disposition` and the existing `auto_cleared` boolean
  across the full constructed sample (FR-006) — no disagreement in either direction.
- **SC-004**: A tag value never seen by the aggregation logic before surfaces correctly in
  `review_reasons` with zero changes to the aggregation code (US3) — proving the vocabulary is
  genuinely open, not a documentation claim.
- **SC-005**: All pre-existing tests (`p0/tests/test_p0.py`, `p0/eval_synth/test_properties.py`,
  `000-synthetic-fixture-generation`'s `test_fixture_generation.py`, `003a`'s
  `test_predicate_archetypes.py`, `003b`'s `test_threshold_archetypes.py`, `003c`'s
  `test_reconcile_archetypes.py`) continue to pass unmodified — zero regression (000: 115 passed as
  of this spec's writing), and the P0 determinism digest
  (`8510a0a8b4b6996e047fc8534e094394ba72aae396305b0d2ecad3d6924634db`) is unchanged.
  **[Post-hoc correction, 2026-07-26 spec audit — disclosed, not silently rewritten (010a's own
  convention)]**: the digest-unchanged half of this criterion was **violated by design** during
  implementation and never annotated here: adding `review_reason` to `CheckResult` changed the
  serialized shape, so the digest legitimately moved (plan.md's own Implementation Notes: "The
  determinism digest changed — deliberately, for the first time since `001a`" — old baseline kept as
  `PRE_004_BASELINE`, new pinned as `POST_004_BASELINE` in `test_p0.py`, itself since superseded by
  003d and 002e re-baselines; current anchor `82175d07...`). The zero-regression half (all prior
  tests pass unmodified) held. Sibling spec 003d already cites "feature 004's legitimate digest
  bump" as precedent — this note makes 004's own record agree with it.

## Assumptions

- This feature adds one small, structural field to `CheckResult` (`review_reason`) — unlike `003c`
  (zero engine touch), this is a deliberate, minimal exception: making tags genuinely inspectable
  (rather than message-string-dependent) requires it, and Gordon's direction was explicit that the
  open-tag mechanism is the actual point of this feature, not a nice-to-have.
- The three initial tags (`EXCEPTION`/`LOW_CONFIDENCE`/`SOURCE_INCOMPLETE`) are a reasonable starting
  vocabulary derived from the three review-worthy code paths that exist today — not an exhaustive or
  closed set. Future tags (e.g. from a new archetype, or a future compliance/fraud-style check) are
  added by authoring a new tag at their own site, proven possible without touching this feature's
  logic (US3/SC-004).
- Routing `review_reasons` to specific human reviewers/teams/channels is real, intended future work
  per Gordon's own framing ("diff concerns/channels/groups/tags to deliver to the human") — but it is
  explicitly `008`'s (or a later feature's) job, not built here (FR-007). This feature's contract is
  the data those future features will consume, not the delivery mechanism itself.
- Per `output/ROADMAP.md`'s inherited caveat, the underlying check coverage this disposition composes
  over is itself partial (predicate ~57% of real conditions classified; reconcile explicitly excludes
  doc-vs-doc per Tension #5) — this feature's correctness claim is about composing/tagging existing
  verdicts correctly, not about the completeness of the verdicts being composed.
- `006` (confidence-gated auto-clear) and `007` (audit trail) are not built as their own features yet
  in this codebase's spec history, but the confidence gate's *mechanism* (ruling #8,
  `DEFAULT_CONFIDENCE_FLOOR`) already exists in `engine.py` — this feature tags that existing signal
  (`LOW_CONFIDENCE`), it does not build 006/007 themselves.
- `009`'s authoring UI and `010`'s program gating do not exist yet; this feature does not require
  them — it composes whatever `Ruleset` a loan is evaluated against, hand-authored or eventually
  compiled.
