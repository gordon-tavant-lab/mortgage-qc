# Feature Specification: Compile-Fidelity Spike

**Feature Branch**: `002a-compile-fidelity-spike`
**Created**: 2026-06-30
**Status**: Spike complete (2026-07-01 — `p0/experiment_002a/RESULTS.md`: PROVISIONAL VERDICT: PROCEED, D1 87.5% ≥ 70%; header corrected from stale "Draft" 2026-07-26, spec audit)
**Input**: User description: "002a-compile-fidelity-spike — a throwaway de-risking spike (the highest-risk irreversible item in the roadmap) that tests whether an LLM can turn a real slice of the AMQ workbook into a correct, signed ruleset at config time, measuring not just runnability but interpretation fidelity (did it read the row the way the lender means it) and required SME correction — before the production compiler (002b) is specced or built."

**Governs**: `output/ROADMAP.md` §002a and Tension 6, `.specify/memory/constitution.md` Principle II (compile, then run) and Principle III (eval is foundational), `output/THESIS.md` Point 3.
**Depends on**: `001a-field-catalog` (the catalog vocabulary generated rules will reference). Does **not** depend on `001b` or the later CI-productionized eval gate (roadmap feature `005`) — this spike uses the already-built `p0/eval_synth` scorer directly, per the roadmap's explicit fix of an earlier dependency-numbering error.
**Foundation this builds on** (proven, not re-specced): `p0/eval_synth/taxonomy.py` (classifies, does not compile, the real AMQ conditions), `p0/eval_synth/eval.py` (the scorer this spike reuses), `p0/qc_engine/ruleset.py` (the `Check` schema generated rules must produce, and the edit-distance measurement this spike reuses), `p0/experiment_g3/` (the pre-registered-decision-rule discipline this spike explicitly mirrors, and the Bedrock/temperature=0 LLM-invocation harness in `llm_arm.py`).

**This is a spike, not a durable feature.** Its deliverable is a **finding** — a go/no-go verdict with calibrated metrics — not a shipped capability. Its code is explicitly throwaway (Out of Scope, below); if the finding is PROCEED, the production compiler (`002b`) is specced and built fresh, informed by but not extending this spike's code.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Know whether the compile bet is real before building on it (Priority: P1)

"Compile, then run" (constitution Principle II) is the product's central architectural bet — the reason the entire engine-slicing sequence (`003a/b/c`), the compiler pipeline (`002b`), and the authoring surfaces (`009a/b/c`) are all designed around a signed, LLM-drafted ruleset. The G3 bake-off (`p0/experiment_g3/`) already tested this bet's *runtime* half (a governed LLM evaluating loans at runtime) and found the compiled engine wins on auditability and cost. It never tested the *other* half: can an LLM, at config time, correctly turn the **real** AMQ workbook — not a synthetic or invented rule — into a signed ruleset at all? `taxonomy.py` only classifies conditions into archetypes; it has never been asked to compile one into an executable rule. This is the single largest unproven assumption standing between the current 2-feature foundation and the 17+ features that assume the compile approach works.

**Why this priority**: If this spike finds the compiler cannot reliably interpret the real workbook, the product's central differentiation needs rethinking **before** `002b`, `003a/b/c`, and `009a/b` are specced and built on top of an unproven assumption — this is exactly the "de-risk the irreversible thing first" principle the constitution names.

**Independent Test**: Take a representative sample of real AMQ workbook rows, run each through an LLM compiler at temperature=0, and score the output against the existing `p0/eval_synth` scorer — without touching any other feature's code.

**Acceptance Scenarios**:

1. **Given** a representative sample of real rows from `demo/rules/*.xlsx`, **When** each row is compiled by the LLM into a rule conforming to `p0/qc_engine/ruleset.py`'s `Check` schema, **Then** each generated rule is scored for runnability and constructed-label correctness using the existing `p0/eval_synth` scorer.
2. **Given** the scored results, **When** the spike concludes, **Then** it reports one of three pre-registered verdicts — PROCEED / RECONSIDER / KILL — never an unscored qualitative impression.

---

### User Story 2 - Catch the failure mode construction can't see: misreading intent (Priority: P1)

A generated rule can be perfectly runnable and score 100% correct against constructed-label mutations while still misreading what the lender's workbook row actually means — because `eval_synth`'s labels are generated *by construction* from the same taxonomy the LLM is also compiling against; a rule that's internally consistent with a wrong interpretation can still pass. This is eval_synth's own documented blind spot ("Question 2" — interpretation correctness), and it's the actual compile risk this spike exists to catch, not incidental to it.

**Why this priority**: The roadmap is explicit that runnability alone is insufficient: "(a) alone would pass while missing the thing the spike exists to catch." Skipping this half of the spike would produce a false PROCEED verdict on the exact failure mode most likely to occur.

**Independent Test**: For the same sample of generated rules, have an SME (Kayla) independently judge — against the original workbook row, not against the generated rule's own internal logic — whether the compiled rule captures the lender's intent.

**Acceptance Scenarios**:

1. **Given** a sample of LLM-generated rules that passed the constructed-label scorer, **When** an SME reviews each rule against its source workbook row, **Then** the SME records an independent interpretation-fidelity judgment (correct / incorrect / ambiguous) for each rule.
2. **Given** a rule that passes the constructed-label scorer but is judged by the SME to misread the workbook row's intent, **Then** the spike counts it as an interpretation failure — the constructed-label pass does **not** override or suppress the SME's judgment.

---

### User Story 3 - Calibrate how much correction the SME actually does (Priority: P2)

If the SME must substantially rewrite most LLM-drafted rules, the LLM isn't compiling the workbook — the SME is, with extra steps. This changes the economics of the entire "compile, then run" value proposition (the LLM was supposed to do the interpretation work, not just generate a first draft the SME redoes from scratch). The existing edit-distance / sign-off-theater machinery already built for the ruleset-signing pattern (`p0/qc_engine/ruleset.py`) measures exactly this; the spike reuses it rather than inventing a new metric.

**Why this priority**: Lower than User Stories 1-2 because it's a calibration output, not a pass/fail gate by itself — but it's a required input to the go/no-go decision (a high correction rate combined with a high interpretation-error rate is a much stronger KILL signal than either alone).

**Independent Test**: Measure the edit-distance between each LLM-drafted rule and its SME-corrected version, using the existing edit-distance function already implemented for ruleset signing.

**Acceptance Scenarios**:

1. **Given** an LLM-drafted rule that the SME corrects during review, **When** the edit-distance is computed between the draft and the corrected version, **Then** the spike records this per-rule and reports a mean/distribution across the sample.
2. **Given** a batch of generated rules signed with zero edits, **When** the spike reports its findings, **Then** a zero-edit batch is flagged explicitly as a possible sign-off-theater signal (constitution Principle II), not silently reported as a win.

---

### Edge Cases

- What happens if a generated rule is runnable and scores correctly on constructed labels, but the SME judges the underlying interpretation wrong (the exact case User Story 2 exists to catch)? → Counted as an interpretation failure regardless of the constructed-label score; this is the decisive test the spike is built around.
- What happens if the sampled workbook rows happen to be unusually easy or hard (e.g., all from one AMQ category)? → Out of scope for a valid result — the sample must be drawn across all classified check-kind archetypes (predicate, ratio_threshold, reconcile) in rough proportion to their real prevalence per `taxonomy.json`, not a convenience sample.
- What happens if results are ambiguous — neither a clear PROCEED nor a clear KILL against the pre-registered thresholds? → The pre-registered decision rule must define an explicit RECONSIDER band (mirroring G3's D1/D2/D3 structure), so the spike is never forced into a binary call the evidence doesn't support.
- What happens to the spike's code after the finding is reported? → It is explicitly throwaway (per roadmap and Out of Scope below); a PROCEED verdict authorizes speccing `002b` fresh, not extending this spike's code into production.
- What happens if no SME reviewer is available for the interpretation-fidelity step? → The spike cannot produce its User Story 2 finding and cannot conclude with a valid verdict — this is a hard external dependency, not a step that can be skipped or approximated.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The spike MUST draw its compile input from a real, representative sample of rows in the AMQ workbook (`demo/rules/*.xlsx`) — never synthetic or invented rule text.
- **FR-002**: The spike MUST use an LLM, invoked only at config/compile time (never at runtime), to draft a rule from each sampled workbook row, conforming to the existing `Check` schema in `p0/qc_engine/ruleset.py`.
- **FR-003** *(execution deviated, disclosed in `p0/experiment_002a/RESULTS.md`: scoring ran per-check rather than via `eval_synth`'s pre-built archetype generator; deviation noted here 2026-07-26, spec audit)*: The spike MUST score each generated rule's runnability and constructed-label correctness using the existing `p0/eval_synth` scorer, without modifying that scorer's mechanism.
- **FR-004**: The spike MUST include an SME (Kayla) rules-review step that independently judges, for each sampled generated rule, whether it captures the source workbook row's intent — a judgment made against the original row, not against the generated rule's own internal logic, and not overridden by a passing constructed-label score.
- **FR-005**: The spike MUST measure the edit-distance between each LLM-drafted rule and its SME-corrected version, reusing the edit-distance function already implemented in `p0/qc_engine/ruleset.py` rather than introducing a new metric.
- **FR-006**: The spike MUST pre-register its go/no-go decision rule — explicit thresholds for the interpretation-fidelity rate and the required-SME-correction rate, and the resulting PROCEED / RECONSIDER / KILL mapping — in a timestamped document *before* any generated rule is scored, mirroring the discipline already used in `p0/experiment_g3/PRE-REGISTRATION.md`.
- **FR-007**: The spike MUST sample workbook rows across all classified check-kind archetypes (predicate, ratio_threshold, reconcile) in rough proportion to their real prevalence in `p0/eval_synth/taxonomy.json`, not a convenience sample concentrated in one archetype.
- **FR-008**: The spike's code and any generated ruleset artifacts MUST be treated as throwaway — its deliverable is the finding (the pre-registered verdict + calibrated metrics), not a production compiler artifact.
- **FR-009**: The spike MUST NOT introduce any LLM call into the QC engine's runtime evaluation path — every LLM invocation happens at config/compile time only, consistent with constitution Principle II.
- **FR-010**: The spike MUST report the interpretation-error rate (from FR-004) as a metric distinct from, and never substitutable by, the constructed-label runnability score (from FR-003) — the roadmap's explicit warning that runnability alone would pass while missing the actual compile risk.

### Key Entities

- **Sampled Workbook Row**: A single real AMQ defect condition (question → response → exception code → significance) drawn from `demo/rules/*.xlsx`, the unit of compile input.
- **Compiled Rule Draft**: The LLM's config-time output for one sampled row — a candidate `Check` (per `p0/qc_engine/ruleset.py`'s schema) before SME review.
- **Interpretation-Fidelity Judgment**: The SME's independent verdict (correct / incorrect / ambiguous) on whether a Compiled Rule Draft captures its source row's intent — the finding User Story 2 exists to produce.
- **Pre-Registered Decision Rule**: The locked, timestamped thresholds and PROCEED/RECONSIDER/KILL mapping, written before any rule is scored — the artifact that makes the spike's conclusion evidence-based rather than post-hoc.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A pre-registered decision-rule document exists with a timestamp predating the first scored rule — verifying the decision thresholds were locked before results could influence them.
- **SC-002**: 100% of sampled workbook rows receive a runnability/constructed-label verdict from the `p0/eval_synth` scorer — no sampled row is left unscored.
- **SC-003**: 100% of sampled generated rules receive an independent SME interpretation-fidelity judgment, distinct from and not derived from the constructed-label score.
- **SC-004**: The spike reports exactly one interpretation-error rate and one required-SME-correction (edit-distance) rate, each computed identically across every sampled rule — comparable numbers, not a narrative.
- **SC-005**: The spike concludes with exactly one of three pre-registered verdicts — PROCEED / RECONSIDER / KILL — evaluated against the thresholds from SC-001, never an unscored qualitative impression.
- **SC-006**: The sample's archetype distribution (predicate / ratio_threshold / reconcile) is reported alongside the findings, verifying the sample was representative per FR-007 rather than a convenience sample.

## Assumptions

- Kayla (or an equivalent SME) is available for the interpretation-fidelity review (User Story 2). Without this reviewer slot, the spike cannot produce a valid verdict — this is an external dependency the spike depends on, consistent with how the roadmap already names Kayla as the check-interpretation reviewer elsewhere (Blocker 2/3).
- The sample size is small by design — this is a throwaway spike testing a mechanism, not a population study — mirroring the G3 bake-off's explicit "honesty caveat" that small-N findings are directional/decisive-if-clear, not exhaustive.
- The LLM invocation reuses the existing Bedrock harness pattern already proven in `p0/experiment_g3/llm_arm.py` (temperature=0, AWS profile `gordon-chan`, cross-region inference profile) rather than standing up new infrastructure.
- A PROCEED verdict authorizes specifying the production compiler (`002b`) next; it does not pre-build any part of `002b`, and `002b`'s implementation does not extend this spike's throwaway code.
- Out of scope: production compiler hardening (`002b`); the authoring UI (`009a/b/c`); any runtime LLM evaluation path; the CI-productionized eval gate (`005` — this spike uses `p0/eval_synth` directly).
