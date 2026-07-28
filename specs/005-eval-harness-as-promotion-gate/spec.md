# Feature Specification: Eval Harness as Promotion Gate

**Feature Branch**: `005-eval-harness-as-promotion-gate`
**Created**: 2026-07-27
**Status**: Implemented (2026-07-27 — all 44 tasks, zero regression; `p0/eval_synth/scenario_construction.py`/`golden_set.py`/`coverage_set.py`/`promotion_gate.py` new, `test_properties.py` generalized to an explicit `ruleset` param (FR-008), `p0/fixtures/golden_panel.py` new; harness.py bit-exact digest unchanged, 96.5% real-ruleset coverage per plan.md's Implementation Notes)
**Input**: `output/ROADMAP.md` §005 (v0.6, amended after a metacognition pass found the scenario-
generation gap by reading the actual code rather than trusting the roadmap's own prior framing).

**Governs**: `output/ROADMAP.md` §005, `.specify/memory/constitution.md` Principle III (Eval is
foundational — NON-NEGOTIABLE) and its Quality Gates (Safety gate: zero false-auto-clears; Eval
gate: constructed-label scorer + label-free metamorphic invariants), `output/THESIS.md` Blocker 2
(the eval gap).

**Depends on**: `001a-field-catalog` (implemented — the `field_catalog.json` vocabulary this
feature's generalized scenario construction reads `data_type`/`expected_sources` from, instead of
hand-picking fields). `003a-engine-predicate-checks` (implemented — this feature scores real
engine output; it evolves alongside `003b`/`003c`/`003d` as they land new check `kind`s). **Does
not gate `002a`** — the compile-fidelity spike already depends on and uses the pre-existing
`p0/eval_synth` scorer directly, independent of this feature's CI productionization (the
dependency-knot fix recorded in the roadmap's v0.3→v0.4 changelog).

**Foundation this builds on** (proven, not re-specced):
- `p0/eval_synth/eval.py` — the existing scorer. Generates N synthetic loans (`generator.generate`),
  scores them (`test_properties.score`), enforces `false_auto_clear_count == 0`, and writes a JSON
  artifact to `p0/eval_synth/artifacts/synth_eval_<runtag>.json` with exit code `0` on pass / `1` on
  fail (`eval.py:107`). This is what `002a` uses directly. It is **not wired to anything that blocks
  a ruleset from being promoted** — nothing in the repository consumes its exit code as a gate.
- `p0/eval_synth/generator.py` — ground-truth-by-construction mutation operators, but **hand-written
  per specific demo field**: `mut_mismatch_categorical` hardcodes `property_address`
  (`generator.py:147-156`), `mut_unsigned` hardcodes `note_signed` (`generator.py:185-190`),
  `mut_threshold_over` hardcodes `loan_amount`/`property_value` LTV math (`generator.py:193-202`).
  The `MUTATIONS` registry (`generator.py:230-238`) covers exactly 7 archetypes tied to 7 specific
  fields on one fixed demo ruleset (`CLEAN_EXPECTED`, `generator.py:101-106`) — there is no
  mechanism to construct a labeled scenario for a field `002b`'s compiler produces that nobody has
  hand-authored a mutation for.
- `p0/experiment_002a/score_drafts.py` — the **generic, kind-based** pattern this feature promotes.
  `SCORERS = {"predicate": _score_predicate, "ratio_threshold": _score_ratio_threshold,
  "agree_categorical": _score_agree_categorical, "agree_numeric": _score_agree_numeric}`
  (`score_drafts.py:159-164`), dispatched off `chk.kind`, each building a synthetic
  `CanonicalLoan`/`SourceValue` pass-case and fail-case **from the `Check` object alone** — no
  hand-picked field name required. Proven at n=24 during `002a`. Never promoted past that spike;
  the file's own docstring (`score_drafts.py:1-25`) explicitly documents it as an adaptation, not a
  production component.
- `p0/eval_synth/test_properties.py` — the label-free metamorphic invariants (monotonicity,
  reconcile soundness, self-consistency, confidence gate; `test_properties.py:1-24`), but hardcoded
  against one fixed ruleset: `RULESET = demo_ruleset()` (`test_properties.py:32`) — not
  parameterized over an arbitrary candidate `Ruleset`.

**Gaps confirmed by direct inspection, not assumed**:
1. **No CI/promotion-gate wiring exists anywhere in the repository.** `find .` for `.github/`,
   any `*.yml` workflow, or any script that treats `eval.py`'s exit code as a merge/deploy gate
   returns nothing. `output/ROADMAP.md` §005's "run on every ruleset version bump" has no trigger
   mechanism today.
2. **No GOLDEN / COVERAGE / VOLUME tiered sets exist anywhere.** `eval.py` runs one undifferentiated
   population (`generate(n)`, default `n=5000`) mixing clean/single/multi-defect loans
   (`generator.py:274-290`) — there is no separate fixed-regression panel, no per-compiled-check
   coverage set, and no named volume/auto-clear-rate estimate as distinct, separately-reportable
   artifacts.
3. **`Ruleset.version` is not a real promotion signal today.** Every `Ruleset(...)` construction site
   across `p0/fixtures/`, `p0/compile_runs/*/`, and `p0/experiment_002a`/`002c` hardcodes
   `version=1` (or `version=0` for `catalog_screen.py`'s throwaway screen) — grep confirms zero
   call sites that increment `Ruleset.version` on a real promotion event. (Contrast:
   `FactVocabulary.version` genuinely increments — `promote_naming_proposals.py:189`,
   `build_vocabulary_guide_citations.py:239` — proving the pattern exists elsewhere in this codebase,
   just not yet for `Ruleset`.) This feature must define what a "candidate ruleset" and a
   "promotion event" concretely are before it can gate one.
4. **`score_drafts.py`'s `SCORERS` covers 4 of the engine's 6 live check kinds.** `p0/qc_engine/engine.py`
   dispatches on `chk.kind` for `agree_categorical` (`engine.py:174`), `agree_numeric`
   (`engine.py:205`), `agree_doc_categorical` (`engine.py:247`), `agree_doc_numeric`
   (`engine.py:285`), `predicate` (`engine.py:319`), `ratio_threshold` (`engine.py:337`) — six
   kinds. `agree_doc_categorical`/`agree_doc_numeric` (added by `003d`, after `002a`'s spike was
   written) have no generalized scenario-construction strategy at all today.
5. **`field_catalog.json` carries 379 entries across 4 `data_type`s** (`string`: 243, `decimal`: 114,
   `boolean`: 17, `date`: 5 — counted directly from the committed catalog) — the vocabulary a
   data-driven scenario constructor must key off, not a hand-picked field list.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Any compiled check gets an automatic constructed pass/fail scenario (Priority: P1)

A rule compiled by `002b` against a field nobody has hand-authored a mutation for (e.g. a new
`002b`-compiled `ratio_threshold` check on a field `generator.py`'s `MUTATIONS` registry has never
heard of) must still get a labeled test scenario — constructed automatically from the `Check`'s
`kind` and its `field_name`'s `field_catalog.json` entry, the way `002a`'s `score_drafts.py` already
proved possible at small scale, generalized to the full check-kind and precondition surface the real
compiler produces today (six kinds, `applies_if` preconditions, two-field doc-vs-doc checks).

**Why this priority**: This is the literal v0.6 amendment and the precondition for everything else
in this feature — without it, the COVERAGE tier (User Story 3) has no way to build a scenario for
any check `002b` compiles beyond the ~7 the demo generator hand-authored, and the whole "eval keeps
pace with the engine slices" mandate (roadmap §005's own "Why") is unmet.

**Independent Test**: Feed a `Check` of each of the 6 live kinds (`predicate`, `ratio_threshold`,
`agree_categorical`, `agree_numeric`, `agree_doc_categorical`, `agree_doc_numeric`) — including one
carrying an `applies_if` precondition — through the generalized constructor with no per-field
mutation code written for that specific field; confirm a pass-case and fail-case loan are produced
and the real engine (`qc_engine.engine.run`) returns the expected verdict for both.

**Acceptance Scenarios**:

1. **Given** a compiled `Check` of any of the 6 live kinds, referencing a field present in
   `field_catalog.json`, **When** the generalized scenario constructor runs, **Then** it returns a
   pass-case loan and a fail/flag-case loan without consulting any field-specific mutation function,
   and running both through `qc_engine.engine.run` produces the kind's expected verdict pair (e.g.
   `PASS`/`FAIL` for `predicate`, `PASS`/`FLAG` for `agree_categorical`).
2. **Given** a compiled `Check` carrying one or more `applies_if` preconditions, **When** the
   constructor builds its pass/fail scenario, **Then** the constructed loan's facts also satisfy
   every precondition — so the check is genuinely reached and evaluated, not silently resolved
   `NOT_APPLICABLE` by an unset precondition fact.
3. **Given** a compiled `Check` of kind `agree_doc_categorical` or `agree_doc_numeric`
   (`compare_field_name` set), **When** the constructor builds its scenario, **Then** it populates
   both `field_name` and `compare_field_name` as independent document-extracted values (mirroring
   `003d`'s doc-vs-doc semantics, never touching `SourceValue.sources{}`).
4. **Given** a compiled `Check` whose `kind` has no registered construction strategy, **When** the
   constructor runs, **Then** it is recorded as an explicit construction failure (surfaced in the
   gate's report) — never silently skipped from coverage.

---

### User Story 2 - Zero false-auto-clear is a hard block, not an advisory report (Priority: P1)

Today, `eval.py` computes `false_auto_clear_count` and prints "SAFETY FAILURE," but nothing consumes
its exit code as a gate — a candidate ruleset with a genuine false-auto-clear defect can be promoted
today with no mechanism stopping it. This feature makes that block real and enforceable.

**Why this priority**: This is the Safety quality gate from the constitution verbatim ("a single
false-clear blocks the change") — the single most safety-critical behavior this feature exists to
guarantee, and currently the codebase only *reports* the number, it does not *act* on it.

**Independent Test**: Construct a candidate ruleset with a deliberately injected false-auto-clear
defect (a check that should `FAIL` a known-bad loan but is miswired to `PASS` it); run the
promotion-gate entry point against it; confirm the gate's process exit code is non-zero and its
JSON artifact's top-level decision field reads `BLOCK`, not merely a printed warning.

**Acceptance Scenarios**:

1. **Given** a candidate ruleset that produces zero false-auto-clears across GOLDEN, COVERAGE, and
   VOLUME tiers, **When** the promotion gate runs, **Then** it exits `0` and its artifact records
   `promotion_decision: "PROMOTE"`.
2. **Given** a candidate ruleset that produces even one false-auto-clear in any tier, **When** the
   promotion gate runs, **Then** it exits non-zero, its artifact records `promotion_decision:
   "BLOCK"`, and the specific false-auto-cleared case (check id, loan, expected vs. actual verdict)
   is named in the artifact — not aggregated away into a count alone.
3. **Given** a `BLOCK` result, **When** the same candidate ruleset is re-run unchanged, **Then** the
   gate produces the identical `BLOCK` decision and the identical named cases (deterministic gate,
   consistent with Principle I — the gate itself must not be a source of flakiness).

---

### User Story 3 - GOLDEN, COVERAGE, and VOLUME each answer a distinct question, separately (Priority: P2)

Today's `eval.py` runs one undifferentiated population and reports one blended set of numbers. This
feature separates that into three named tiers, each answering a different question the constitution's
eval decomposition (Principle III, items 1-3) already implies should be distinct: **GOLDEN** — "did a
known-correct case regress?" (a fixed, versioned panel, replayed old-vs-new ruleset); **COVERAGE** —
"does every compiled check have at least one proven pass/fail scenario?" (one constructed scenario
per compiled `Check`, from User Story 1); **VOLUME** — "at realistic population scale, what fraction
auto-clears, and does zero-false-auto-clear still hold?" (a large generated population, reusing
`generator.py`'s existing clean/single/multi-defect composition).

**Why this priority**: Lower than US1/US2 because it is a reporting/organization layer over
mechanisms US1 and the existing scorer already provide — valuable and explicitly named in the
roadmap, but not the safety-critical mechanism itself.

**Independent Test**: Run the gate against a candidate ruleset; confirm the artifact reports three
distinct, separately-computed metrics (`golden.regressions`, `coverage.checks_covered /
checks_total`, `volume.auto_clear_rate`) rather than one blended number.

**Acceptance Scenarios**:

1. **Given** a candidate ruleset identical to the previously-promoted one, **When** GOLDEN replays
   its fixed panel, **Then** it reports zero regressions and the artifact names the panel version it
   replayed against.
2. **Given** a candidate ruleset compiling N checks, **When** COVERAGE runs, **Then** it reports
   exactly how many of the N checks got a constructed scenario (User Story 1) versus how many failed
   construction (User Story 1, Acceptance Scenario 4) — a coverage fraction, not a pass/fail count
   alone.
3. **Given** a candidate ruleset, **When** VOLUME generates its population (default N matching
   `eval.py`'s existing `5000`), **Then** it reports an auto-clear-rate estimate alongside the
   existing `false_auto_clear_count` check.

---

### User Story 4 - Label-free metamorphic invariants run against any candidate ruleset, not just the demo (Priority: P2)

`p0/eval_synth/test_properties.py` proves genuinely useful, label-free invariants (monotonicity,
reconcile soundness, self-consistency, confidence gate) — but only against `demo_ruleset()`
hardcoded at import time (`test_properties.py:32`). This feature generalizes those invariants to run
against whatever `Ruleset` the gate is asked to evaluate.

**Why this priority**: Necessary for the gate to be genuinely reusable across every ruleset version
the engine slices (`003a`/`b`/`c`/`d`) produce, not a second hardcoded artifact alongside the one
`eval.py` already has.

**Independent Test**: Run the metamorphic invariant suite against two different compiled rulesets
(the existing `demo_ruleset()` and a second, differently-shaped ruleset containing an
`agree_doc_categorical` check); confirm each invariant evaluates against the ruleset it was actually
given, not a module-level constant.

**Acceptance Scenarios**:

1. **Given** a ruleset containing an LTV `ratio_threshold` check, **When** the monotonicity invariant
   runs, **Then** it confirms raising `loan_amount` only ever moves that specific check's verdict
   `PASS → FAIL`, never the reverse, for the ruleset under test — not a hardcoded reference to
   `demo_ruleset()`'s own check ids.
2. **Given** a ruleset with no `ratio_threshold` check at all, **When** the invariant suite runs,
   **Then** the monotonicity invariant is skipped for that ruleset (reported as not-applicable, not
   silently passed or errored) rather than assuming the demo ruleset's shape.

---

### User Story 5 - The harness absorbs real loans with no rework when they arrive (Priority: P3)

Per Principle III and the roadmap's explicit design intent ("built to absorb real loans with no
rework"), once expert-labeled real loans (feature `012`) exist, they become another labeled-scenario
source feeding the same GOLDEN/COVERAGE/VOLUME scorer — not a second harness.

**Why this priority**: Lowest priority because `012` (real-loan acquisition) does not exist yet and
is explicitly out of scope for this feature to build — this user story only requires that this
feature's own interfaces don't have to change shape when `012` lands.

**Independent Test**: Construct a fake "real-loan" input matching the shape `012` is expected to
produce (a loan + an expert-assigned expected verdict per check, no injected-mutation provenance);
confirm it can be scored by the same scorer function used for synthetic loans, with no code change
to the scorer's signature.

**Acceptance Scenarios**:

1. **Given** a `(loan, expected_verdicts)` pair whose provenance is `"expert-labeled"` rather than
   `"constructed-by-mutation"`, **When** it is passed to the scorer, **Then** it scores identically
   to a synthetic labeled loan — the scorer's interface does not distinguish loan origin.

---

### Edge Cases

- A compiled check's `field_name` does not resolve to any `field_catalog.json` entry at all → this
  is already a SAFE-gate referential-integrity failure the catalog layer (`catalog.py`) is
  responsible for catching upstream of this feature (Principle VII); this feature's scenario
  constructor assumes a resolvable `field_name` as a precondition and does not re-implement that
  check — an unresolved reference is a dependency failure, not a construction-strategy gap.
- A field's `data_type` is `date` (5 of 379 catalog entries) → no generalized construction strategy
  is defined for date arithmetic in this feature's scope, mirroring `003a`'s own precedent of
  **naming, not solving**, the `EXPIRED` archetype's date-arithmetic gap (`003a` spec.md FR-007) —
  carried forward as the same open question for `002b`'s compiler policy, not re-solved here as a
  side effect.
- Two archetypes' constructed scenarios could compose ambiguously if run together (the same trap
  `generator.py`'s `make_multi` already solved by choosing archetypes that touch *distinct* checks,
  `generator.py:270-271`) → the generalized COVERAGE constructor builds one isolated scenario per
  check (never composes multiple checks' mutations into one loan), sidestepping the ambiguity
  entirely rather than re-solving it.
- A GOLDEN-tier case flips verdict between the previously-promoted ruleset and the candidate — is
  a flip always a regression? → No: a flip can be an *intended* correction (e.g. `003a`'s own
  `doc=None` predicate fix intentionally flipped `NOT_APPLICABLE → FAIL`). The gate reports every
  flip and requires an explicit human acknowledgment before promotion proceeds (mirrors `002g`
  FR-008's replay-and-report pattern) — it does not assume every flip is bad, but it never lets one
  pass silently either.
- What triggers "a ruleset version bump" concretely, given `Ruleset.version` is hardcoded to `1`
  everywhere today (Gap 3 above)? → Out of scope for this feature to solve generally; this feature
  defines the gate as a callable entry point taking two `Ruleset` objects (candidate + previously-
  promoted baseline, or a single candidate against GOLDEN/COVERAGE/VOLUME alone if no baseline
  exists yet) and leaves *what event calls it* (a real versioning/promotion workflow) to whichever
  feature or ops process first wires actual CI infrastructure — named as a real, unresolved gap
  rather than assumed solved.
- No CI infrastructure (`.github/workflows` or equivalent) exists in this repository today → this
  feature ships the gate as a script with a documented, stable exit-code and artifact contract,
  runnable by any CI vendor's runner; it does not itself add a specific vendor's workflow file (see
  Assumptions).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system SHALL construct, for any compiled `Check` of a kind already live in
  `qc_engine.engine` (`predicate`, `ratio_threshold`, `agree_categorical`, `agree_numeric`,
  `agree_doc_categorical`, `agree_doc_numeric`), a synthetic pass-case loan and a synthetic
  fail/flag-case loan, derived from the `Check`'s `kind`, `field_name` (and `compare_field_name`
  where applicable), and that field's `field_catalog.json` entry — with no hand-written per-field
  mutation function required.
- **FR-002**: IF a compiled `Check`'s `kind` has no registered scenario-construction strategy THEN
  THE system SHALL record an explicit construction failure for that check (named in the gate's
  artifact) rather than silently omitting it from the coverage count.
- **FR-003**: WHEN a `Check` carries one or more `applies_if` preconditions THE system SHALL set the
  constructed loan's facts to satisfy every precondition before evaluating the check's own pass/fail
  logic, so the constructed scenario is genuinely reached by the engine rather than short-circuited
  to `NOT_APPLICABLE`.
- **FR-004**: The system SHALL construct two-field scenarios for `agree_doc_categorical` /
  `agree_doc_numeric` kinds, populating both `field_name` and `compare_field_name` as independent
  document-extracted values and never populating `SourceValue.sources{}` for either (preserving
  `003d`'s doc-vs-doc vs. doc-vs-system distinction).
- **FR-005**: The system SHALL maintain three named, separately-reportable test tiers:
  - **GOLDEN** — a fixed, versioned regression panel of previously-known `(loan, expected_verdicts)`
    pairs, replayed against both the previously-promoted ruleset and the candidate ruleset, reporting
    any verdict that flips between the two.
  - **COVERAGE** — exactly one constructed pass/fail scenario (FR-001) per compiled `Check` present
    in the candidate ruleset, reporting the fraction of checks successfully covered.
  - **VOLUME** — a large generated population (reusing `generator.py`'s existing clean/single/multi-
    defect composition; default N matching `eval.py`'s current default of 5000), reporting an
    auto-clear-rate estimate and the existing `false_auto_clear_count` check at that scale.
- **FR-006**: IF any constructed fail-case scenario, in any of the three tiers, resolves to an
  auto-cleared `PASS` THEN THE promotion gate SHALL block promotion of the candidate ruleset — a
  non-zero process exit code and a `promotion_decision: "BLOCK"` artifact field, naming the specific
  check id, loan, and expected-vs-actual verdict — not merely an advisory count a caller may choose
  to ignore.
- **FR-007**: WHEN a GOLDEN-tier case's verdict changes between the previously-promoted ruleset and
  the candidate ruleset THE system SHALL report every such flip explicitly and SHALL require an
  explicit human acknowledgment field in the promotion record before promotion proceeds — an
  unacknowledged flip blocks promotion, whether or not it also produces a false-auto-clear.
- **FR-008**: The system SHALL run the existing label-free metamorphic invariants (monotonicity,
  reconcile soundness, self-consistency, confidence gate — `p0/eval_synth/test_properties.py`)
  parameterized against the candidate `Ruleset` under test, not a module-level hardcoded ruleset —
  an invariant whose precondition check kind is absent from the ruleset under test MUST be reported
  as not-applicable for that run, never silently passed.
- **FR-009**: The promotion gate SHALL be invocable as a single script/entry point with a documented,
  stable exit-code contract (`0` = promote, non-zero = block) and a JSON artifact (extending
  `eval.py`'s existing artifact shape with per-tier metrics and a top-level `promotion_decision`
  field) — runnable by any CI system's runner without this feature building or assuming a specific
  CI vendor's workflow configuration.
- **FR-010**: The scorer's `(loan, expected_verdicts)` input contract MUST NOT distinguish a
  synthetically-constructed scenario from an expert-labeled real loan (feature `012`, not yet built)
  — both score through the identical function, so real loans can be added as an additional GOLDEN/
  VOLUME source with no scorer-interface rework when `012` lands.
- **FR-011**: This feature MUST NOT introduce any runtime LLM call. Scenario construction and scoring
  are pure deterministic code operating on the compiled `Ruleset` (`p0/qc_engine/ruleset.py`) and
  `field_catalog.json` — consistent with Principle II; the LLM's only role anywhere in this project's
  pipeline is at `002b`'s compile time, never here.
- **FR-012**: This feature MUST NOT build real-loan acquisition (`012`) or extraction/OCR-noise
  realism modeling — both remain the honest, explicitly named residual per Principle III, not
  silently folded into a correctness claim this feature's synthetic tiers cannot actually support.
- **FR-013**: This feature MUST NOT modify `p0/experiment_002a/score_drafts.py` itself — that file
  remains the throwaway spike record of what `002a` proved at n=24 (matching the precedent
  `002b`'s own plan.md already set: prior spike code is left untouched, not extended in place). The
  generalized construction strategies this feature ships are a fresh, production-scoped
  implementation in `p0/eval_synth/`, informed by (not built inside) that file.

### Key Entities

- **ScenarioConstructionStrategy** (new): a function keyed by `Check.kind` — the promoted,
  generalized successor to `score_drafts.py`'s `SCORERS` dict (FR-001), extended to all 6 live
  kinds and to `applies_if`-precondition-setting and two-field construction (FR-003/004).
- **ConstructedScenario** (new): the `(pass_loan, fail_loan, expected_pass_status,
  expected_fail_status, provenance)` tuple a strategy produces — the generalized, per-check
  successor to `generator.py`'s fixed-ruleset `LabeledLoan` shape.
- **GoldenSet / CoverageSet / VolumeSet** (new): the three named tiers (FR-005), each with its own
  metric and its own artifact section.
- **PromotionGateResult** (new): the gate's output artifact — extends `eval.py`'s existing JSON
  shape (`eval.py:72-100`) with per-tier metrics, the list of any GOLDEN flips, and a top-level
  `promotion_decision: "PROMOTE" | "BLOCK"` field (FR-006/007/009).
- **Check / Ruleset** (existing, `p0/qc_engine/ruleset.py`): the candidate artifact under test;
  unmodified by this feature.
- **field_catalog.json entries** (existing, `p0/qc_engine/field_catalog.json`, 379 entries across
  `string`/`decimal`/`boolean`/`date`): the vocabulary the generalized constructor reads `data_type`
  from, in place of a hand-picked field list.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A registered scenario-construction strategy exists for all 6 check kinds live in
  `qc_engine.engine` today (`predicate`, `ratio_threshold`, `agree_categorical`, `agree_numeric`,
  `agree_doc_categorical`, `agree_doc_numeric`) — up from the 4 kinds `score_drafts.py`'s `SCORERS`
  covers today, verified by test against one representative `Check` of each kind.
- **SC-002**: Running the generalized COVERAGE builder against an existing compiled ruleset (e.g.
  `p0/compile_runs/run_013_comprehensive_e2e_v6`'s output, or `run_011_retail_only_002g`'s) produces
  a constructed pass/fail scenario for every check whose kind is covered by SC-001, with zero
  hand-written per-field mutation code added to reach that coverage — verified by a coverage-fraction
  report in the gate's artifact.
- **SC-003**: A deliberately-injected false-auto-clear defect in a constructed candidate ruleset
  causes the gate to exit non-zero and report `promotion_decision: "BLOCK"`, naming the specific
  offending check — proven by a dedicated test constructing exactly this case, not merely asserted
  by description.
- **SC-004**: A constructed before/after ruleset pair with one deliberately flipped verdict causes
  GOLDEN-tier replay to report exactly that one flip, no more and no fewer — proven by test.
- **SC-005**: VOLUME tier at the existing default N (5000) reports an auto-clear-rate estimate
  alongside a `false_auto_clear_count` of zero on a known-clean candidate ruleset, and non-zero
  (triggering `BLOCK`) on a ruleset with an injected false-auto-clear defect.
- **SC-006**: Full existing test suite (`pytest p0/tests -v`, `p0/eval_synth/test_properties.py`,
  `p0/harness.py`'s bit-exact digest) passes with zero regressions after this feature ships.

## Assumptions

- `Ruleset.version`'s current hardcoded-`1` state (Gap 3) is not fixed by this feature — this
  feature defines the gate as a callable entry point over two `Ruleset` objects (or one, if no
  prior-promoted baseline exists), and leaves the question of what real event calls it (an actual
  versioning/promotion workflow) to whichever future process wires real CI/ops infrastructure. Named
  explicitly so it is not mistaken for solved.
- No `.github/workflows` or equivalent CI infrastructure exists in this repository today, and this
  feature does not add a specific CI vendor's configuration — it ships a script with a stable
  exit-code and JSON-artifact contract that any CI runner can invoke, consistent with this project's
  cloud-agnostic-deployment default. Actual CI wiring is assumed to be a later, separate task (likely
  part of the prototype→validate→handoff flywheel's industrial build-out, `CLAUDE.md`'s "Where This
  Fits").
- The `date` `data_type` (5 of 379 `field_catalog.json` entries) has no generalized construction
  strategy in this feature's scope, mirroring `003a`'s own precedent of naming rather than solving
  the `EXPIRED` archetype's date-arithmetic gap — carried forward as the same open item.
- `p0/eval_synth/generator.py`'s existing 7 hand-written mutation operators are not deleted by this
  feature — they remain valid, proven VOLUME-tier population generators (FR-005); this feature adds
  the generalized per-check constructor for COVERAGE alongside them, it does not replace working
  code that isn't broken.
- Feature `012` (real-loan acquisition) does not exist yet; User Story 5's interface contract (FR-010)
  is verified against a constructed stand-in for real-loan shape, not an actual real loan, consistent
  with how `003a`/`003b`/`003c` each shipped their own local eval coverage independent of this
  feature (`003a` spec.md's own Assumptions: "`005` does not exist yet; this feature ships its own
  local, static eval coverage... rather than depending on `005`").
- The GOLDEN panel's initial contents (what counts as "previously known") are assumed to be seeded
  from this project's own existing known-defect fixtures (`p0/fixtures/ruleset_defects.py`'s 25
  planted defects across 5 synthetic loans, `p0/eval_synth/generator.py`'s constructed archetypes) —
  not real expert-labeled loans, which don't exist yet (see `012`).

## Risks

- **HIGH — a hard block with no real trigger event is inert.** Per Gap 3 and the Edge Cases note,
  nothing today actually bumps `Ruleset.version` on a real promotion. Mitigation: this feature ships
  the gate as a directly-callable script (FR-009) that any future promotion workflow can invoke
  immediately, rather than waiting for that workflow to be designed first — the gate itself is
  useful run manually or via a Makefile/pre-commit hook even before real CI exists.
- **MEDIUM — generalized construction could silently under-cover a kind it claims to support.** A
  strategy that "constructs a scenario" but constructs one that doesn't actually exercise the
  check's real logic (e.g. a precondition silently unmet) would look green while proving nothing —
  the same failure mode `generator.py`'s own `assert_independently_constructed` guard exists to
  catch for reconcile mutations (`generator.py:120-140`). Mitigation: FR-003's precondition-setting
  requirement and SC-002's coverage-fraction report against a real compiled ruleset (not just
  synthetic unit tests of the constructor itself) are both explicit line items, not left implicit.
- **LOW — VOLUME's default N=5000 may not be the right scale once `002b` compiles the full ~8,442-row
  rulebook.** Mitigation: N is a named, documented parameter (mirrors `eval.py`'s existing CLI
  arg), not hardcoded logic — raising it is a config change, not a rebuild.
