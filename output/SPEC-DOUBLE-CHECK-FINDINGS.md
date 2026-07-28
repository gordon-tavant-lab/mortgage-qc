# Spec Adversarial Double-Check Findings

---

## CLOSING SUMMARY — GO / NO-GO

**Date closed**: 2026-07-27
**Iterations**: 2 (Iteration 1: full adversarial read of all 21 in-scope specs; Iteration 2: evidence-groundedness verification, code-level finding confirmation, direct fixes)

### Counts

| Category | Count |
|---|---|
| In-scope specs reviewed | 21 |
| Auto-fixed (clearly-correct, directly in spec files) | **8** |
| Flagged for human judgment (cannot be auto-resolved) | **20** |
| New findings added in Iteration 2 (none — all confirmed from Iteration 1) | 0 |

**Auto-fixes applied across both iterations:**
- 6 stale "Draft" status headers corrected to "Implemented (date, commit)" (003a, 003b, 003c, 003d, 004, 010a) — Iteration 1
- 1 missing FR added to 002c (citation error repair) — prior constitution-alignment pass
- 1 Edge Cases stale "21%" figure corrected to "~13.9%" in 010a — Iteration 2

### Evidence-groundedness verdict (Iteration 2 spot-check)

Specs 005, 010b, 011, and 012 — the four flagged for verification — are **exceptionally well evidence-grounded**. Each cites real file paths, line numbers, grep results, and direct code inspection. No fabricated claims found. The "gaps confirmed by direct inspection, not assumed" sections in 005, 010b, 011, and 012 explicitly trace every baseline claim to a file:line anchor. This is the strongest evidence-groundedness discipline in the spec corpus.

### Code-level finding verification (Iteration 2)

| Finding | Claim verified? | Evidence |
|---|---|---|
| #3 — zero `applies_if` in real compiled ruleset | ✅ **CONFIRMED** | `run_010_post_closing_only/ruleset.json` → 5,093 checks, 0 with `applies_if` |
| #11 — ROADMAP MISMATCH metric not overclaiming | ✅ **NOT an issue** | ROADMAP §003c headline is taxonomy count (~402), and line 502 explicitly calls out Phase 2 (doc-vs-doc recompile) as unscheduled — the metric is correctly framed, not overclaiming coverage |
| #12 — `Ruleset.version` hardcoded to 1 | ✅ **CONFIRMED** | `run_010_post_closing_only/ruleset.json: "version": 1`; all construction sites in `p0/fixtures/`, `p0/compile_runs/`, `p0/experiment_002a/002c` hardcode `version=1`; contrast: `FactVocabulary.version` genuinely increments (`promote_naming_proposals.py:189`) — the pattern exists in this codebase, just not for `Ruleset` |
| #14 — Edge Cases 21% stale | ✅ **FIXED** | Corrected to ~13.9% (1,171/8,442) with pre-correction historical note inline |

### GO / NO-GO: **CONDITIONAL GO**

The spec set is ready for implementation to begin **on the specs with no blocking human-judgment findings** — primarily the engine slices (003a through 003d, all already implemented), field catalog and source envelope specs (001a, 001b, 002a through 002g), and the engine architecture (004, 005 pending its version-bump wiring).

**Three findings should be resolved or formally accepted before the first production run on real loans:**

1. **Finding #1** (Kayla SME sign-off on 002a's 87.5% fidelity baseline) — the downstream compiler specs treat this as settled; it is not formally validated.
2. **Finding #17** (PII guardrails at repo level before any real-loan work) — 3 real loans with PII are in S3; no pre-commit hook or CI check exists today.
3. **Finding #18** (014 LLM cost circuit-breaker or explicit "unbounded by design" decision) — 014 is the first feature to introduce per-loan-run LLM cost with no cap.

The remaining 17 findings are real design tensions worth tracking but do not block initial implementation. They are predominantly integration-gap, deferred-work, and "confirm-with-Kayla" items that will surface naturally during first real-loan exercise.

---

**Iteration**: 2 of 3 (complete — evidence verification pass, code confirmation, closing summary written)
**Iteration 1 date**: 2026-07-27 — full adversarial read of all 21 in-scope specs
**Iteration 2 date**: 2026-07-27 — code-level confirmation + direct fixes + closing summary
**Reviewer**: Contrarian/steelman + g-os-judge evidence-groundedness. Small clearly-correct fixes applied directly. Human-judgment findings surfaced below.
**Out of scope**: specs 008, 009a/b/c; no code implementation; no silent design-disagreement resolution.

---

## Coverage

| Spec | Passed adversarial read | Notes |
|------|------------------------|-------|
| 000-synthetic-fixture-generation | ✅ | Clean — no human-judgment findings |
| 001a-field-catalog | ✅ | Clean |
| 001b-source-envelope-and-inbound-contracts | ✅ | Clean |
| 002a-compiler-spike-and-eval | ✅ | Findings #1, #2 |
| 002b-ruleset-compiler-pipeline | ✅ | Finding #5 |
| 002c-domain-knowledge-grounded-compilation | ✅ | Findings #4, #7 |
| 002d-operator-consistency-gate | ✅ | Clean |
| 002e-applies-if-conditional-gating | ✅ | Finding #3 |
| 002f-precondition-ontology-layer | ✅ | Finding #3 (shared) |
| 002g-canonical-loan-fact-vocabulary | ✅ | Finding #6 |
| 003a-engine-predicate-checks | ✅ | Finding #8 |
| 003b-engine-ratio-threshold-checks | ✅ | Findings #9, #10 |
| 003c-engine-reconcile-checks | ✅ | Finding #11 |
| 003d-engine-doc-vs-doc-reconcile-checks | ✅ | Finding #11 (shared) |
| 004-loan-disposition | ✅ | Clean |
| 005-eval-harness-as-promotion-gate | ✅ | Findings #12, #13 |
| 010a-program-applicability-gating | ✅ | Finding #14 |
| 010b-derive-remaining-gating-dimensions | ✅ | Finding #15 |
| 011-label-confirmation-flywheel | ✅ | Finding #16 |
| 012-real-loan-distribution-eval | ✅ | Findings #17, #19, #20 |
| 014-decision-narrative | ✅ | Findings #18 |

---

## Human-Judgment Findings

Each finding states: the strongest contrarian case, why it is not auto-fixable (requires human judgment), and a recommendation.

---

### #1 · 002a PROCEED is provisional — no SME sign-off on the 87.5% fidelity spike result

**Spec**: `002a-compiler-spike-and-eval`

**Contrarian case**: The PROCEED gate in 002a rests on an AI self-review of the spike's fidelity score. Kayla — the required domain SME — has never seen, reviewed, or signed off on the 87.5% result or the 16 sample interpretations it is based on. Every downstream spec (002b through 002g) treats this as settled foundation. If Kayla reviews the 16-check sample and disagrees with even a few of the SME-graded judgments that generated the 87.5% number, the compiler arc's foundational score changes, possibly below a real go/no-go threshold.

**Why not auto-fixed**: This is a process/governance gap, not a spec-text error. Fixing it requires a real human action (SME validation session), not a text edit.

**Recommendation**: Before 002b→002g are implemented in production, schedule a Kayla review of the 16-sample set (ideally the full 002a eval output). This is already named as a blocker in CLAUDE.md ("Kayla provides expert-validated loans with known outcomes and validates the 800 check interpretations") — the finding is that no spec currently tracks when this sign-off actually happened or is scheduled.

---

### #2 · FR-003 deviation in 002a invalidates pre-registration discipline for one eval dimension

**Spec**: `002a-compiler-spike-and-eval`

**Contrarian case**: The pre-registered experimental plan specified scoring via `eval_synth`'s pre-built archetype generator. The actual spike scored per-check rather than via that generator — a deviation from the pre-registered protocol on the most important dimension (compiler fidelity). The scientific-rigor claim that 002a is a "pre-registered experiment" is therefore only partially true.

**Why not auto-fixed**: Whether the deviation is material depends on whether per-check and archetype-generator scoring produce meaningfully different results. That is an empirical question, not a text-editing question.

**Recommendation**: Document the deviation explicitly in 002a's spec header or plan.md (similar to how 003c and 003d document their deviations), so future auditors don't interpret the pre-registration claim as covering a dimension it doesn't. Alternatively, retroactively run the archetype-generator scoring path on the same sample and confirm the numbers agree.

---

### #3 · applies_if conditional gating (002e/002f/002g) has never been exercised against real compiled rulesets — zero wiring

**Specs**: `002e-applies-if-conditional-gating`, `002f-precondition-ontology-layer`, `002g-canonical-loan-fact-vocabulary`

**Contrarian case**: The entire three-spec conditional gating arc has been implemented and tested exclusively against hand-authored test fixtures. Not a single compiled check in the real `post_closing_only_ruleset.json` contains an `applies_if` entry (010b's wiring is the first planned real exercise). This means the engine path that handles `applies_if` at runtime may carry subtle semantics bugs that only appear when compiled data is fed through it — bugs that 3 complete spec+implementation cycles have had no opportunity to surface.

**Why not auto-fixed**: The resolution is an integration test run (feed real compiled ruleset through the applies_if engine path), not a spec text change.

**Recommendation**: Before shipping 010b, write one integration test that takes an actual compiled check from `post_closing_only_ruleset.json` (with a hand-added `applies_if` field for the test), runs it through the engine, and verifies the expected applies/skips behavior. This is the minimal real-data exercise that would catch a lurking parsing or evaluation bug before 010b relies on it at scale.

---

### #4 · 002c storage layer was superseded — but the spec body still describes the old design

**Spec**: `002c-domain-knowledge-grounded-compilation`

**Contrarian case**: The spec's status header says "Storage layer since superseded — see plan.md's 2026-07-26 post-hoc note." The spec body, however, still describes the superseded storage design in detail. A reader following only the spec body (rather than plan.md) will build against the wrong architecture. The spec-as-spec is now misleading.

**Why not auto-fixed**: The correct fix depends on what the superseding design is — that is described in plan.md's 2026-07-26 note, not here. The right action is to update the spec body to reflect the current design, which requires reading plan.md first and then editing the spec — more than a one-line correction.

**Recommendation**: Inline the plan.md post-hoc note into the spec body under a `## Amendments` section (or directly update the relevant storage architecture section). The spec should be the single source of truth for what was built, not "read the spec plus a sibling file's footnote."

---

### #5 · Batch compile strategy unresolved — 5,520+ rows at production scale

**Spec**: `002b-ruleset-compiler-pipeline`

**Contrarian case**: 002b explicitly defers the single-pass vs. chunked vs. hierarchical compile decision to plan.md. At 5,520 real AMQ rows (8,442 post-010a), this is not a hypothetical edge case. Chunked compile creates ordering dependencies; hierarchical compile creates semantic dependencies between passes; single-pass at this scale risks exceeding context windows and has cost implications. None of these trade-offs are resolved anywhere in the spec arc.

**Why not auto-fixed**: The choice between strategies depends on empirical data (what context window fits how many rows, what chunking does to inter-row consistency) plus product requirements (how often SMEs re-run the full compile). This is a research question, not a text edit.

**Recommendation**: Before the first production full-compile run, this decision needs an explicit resolution — even a temporary "single-pass on 500-row batches for now" with documented rationale. Currently there is no spec that owns this decision. Assign it explicitly to 002b's plan.md (or open a new 002b-followup spec entry).

---

### #6 · Derived fact provenance gap — is_jumbo, QM status, and computed derived facts cannot use doc-provenance

**Spec**: `002g-canonical-loan-fact-vocabulary`

**Contrarian case**: 002g names this as a "future data-model touch," but the gap is load-bearing for Non-Negotiable #1. An auditor checking a FAIL verdict that was driven by `is_jumbo=True` cannot trace that fact to a document citation — because `is_jumbo` was derived algorithmically from `loan_amount` and `conforming_limit`, not extracted from a document. If the QC product's audit trail story requires every check input to be doc-traceable, derived facts represent an architectural hole in that story.

**Why not auto-fixed**: This requires a deliberate design decision: either (a) derived facts get a distinct provenance type (`"computed from: [loan_amount, conforming_limit], rule: conforming_limit_for_year()"`) in the audit trail, or (b) derived facts are excluded from audit-trail traceability with an explicit documented justification. Neither option is a spec text fix.

**Recommendation**: Resolve this in 002g or 010b: define explicitly what provenance looks like for a derived fact (computation formula + input field names + source rules), versus what provenance looks like for an extracted fact (doc + page + segment). The audit-trail story needs both shapes to be specified before Non-Negotiable #1 can be considered fully addressed.

---

### #7 · 002c FR-010 auto-approve rate never measured on real data

**Spec**: `002c-domain-knowledge-grounded-compilation`

**Contrarian case**: The spec explicitly says "do NOT assume from literature" for the auto-approve rate, but there is no indication the real split has been measured on even a pilot batch of real compiled checks. If the auto-approve rate is materially lower than assumed (e.g., 40% rather than 70%), the human-review queue design is under-resourced; if it is materially higher, the auto-approve confidence threshold may be set too conservatively.

**Why not auto-fixed**: Measuring the real auto-approve rate requires running a batch compile and applying the confidence gate — an empirical action, not a spec text edit.

**Recommendation**: Before 002c's confidence gate design is treated as production-ready, measure the split on a real representative batch (even 50–100 rows) and document the observed rate in plan.md. If the real rate diverges significantly from the gate's design assumptions, adjust the threshold.

---

### #8 · EXPIRED staleness semantics unresolved — assumed pre-computed booleans, never confirmed

**Spec**: `003a-engine-predicate-checks`

**Contrarian case**: 003a defers the EXPIRED condition's semantics to 002b/Kayla, under the assumption that EXPIRED conditions arrive as pre-computed boolean flags in the extracted data (i.e., the field already says "expired=True"). This assumption has not been confirmed with Kayla. The real AMQ condition "document is past its acceptable date window" requires date arithmetic — if EXPIRED conditions arrive as raw dates, not pre-computed booleans, the predicate engine as built does not handle them.

**Why not auto-fixed**: Confirming whether EXPIRED conditions arrive as pre-computed flags or raw dates requires asking Kayla or inspecting real Touchless extraction output.

**Recommendation**: Resolve this before any real loan file with date-sensitive checks (e.g., appraisal date, title insurance date) is processed. If EXPIRED conditions come as raw dates, 003a needs a date-comparison code path, which is a feature addition, not a spec clarification.

---

### #9 · Bundled multi-condition THRESHOLD rows — field_value vocabulary cannot represent them

**Spec**: `003b-engine-ratio-threshold-checks`

**Contrarian case**: The AMQ workbook contains `ratio_threshold` rows that bundle multiple comparisons (e.g., "credit score ≥ 500 AND DTI ≤ 45%" in one row). The current `ratio="field_value"` vocabulary handles single-field numeric floors only. The spec does not address how multi-condition THRESHOLD rows are classified or compiled — they would either compile incorrectly (mapping to a single-field check that misrepresents the rule) or fail to compile (becoming false `parse_error`s).

**Why not auto-fixed**: The resolution depends on whether multi-condition rows should be split into separate checks at compile time, or whether a new `multi_condition` check kind is needed. That is a product decision.

**Recommendation**: Identify the real count of multi-condition THRESHOLD rows in `PF and PC Sept 2025 AMQs - Retail.xlsx` (a single `grep` over the AMQ spreadsheet or a compile-run analysis would reveal this). If the count is non-trivial, spec a handling strategy before the production compile run.

---

### #10 · reconcile-00 classification ambiguous — may be predicate, not reconcile

**Spec**: `003b-engine-ratio-threshold-checks` (also touches 003c)

**Contrarian case**: The example row `reconcile-00` (described in 003c as a two-value comparison) may actually be a single-value predicate check rather than a genuine two-source reconcile. If it is predicate territory, classifying it as reconcile inflates the RECONCILE archetype's proven coverage with a test case that doesn't actually exercise the reconcile engine path.

**Why not auto-fixed**: Resolving this requires reviewing the actual AMQ source row with Kayla to confirm the intended comparison structure (one-source vs. two-source).

**Recommendation**: Add this to the Kayla rules-review agenda. If reconcile-00 is reclassified as predicate, move its test fixture to 003a and update 003c's coverage count. Low priority — the test still passes either way — but wrong classification pollutes coverage metrics.

---

### #11 · Doc-vs-doc is the dominant real MISMATCH shape, but Phase 2 (full recompile) is deferred

**Specs**: `003c-engine-reconcile-checks`, `003d-engine-doc-vs-doc-reconcile-checks`

**Contrarian case**: 003c proves only the doc-vs-system subset of MISMATCH conditions. 003d addresses the doc-vs-doc subset but defers Phase 2 (full rulebook recompile incorporating the new `agree_doc_categorical`/`agree_doc_numeric` kinds) explicitly. The "~402 conditions" MISMATCH coverage headline cited in 003c is therefore not the effective coverage number — a significant fraction of real MISMATCH conditions are doc-vs-doc shapes that are not yet wired into the production ruleset.

**Why not auto-fixed**: The Phase 2 deference in 003d is a deliberate product decision. "Don't cover this yet" is not a spec error; it is a prioritization call.

**Recommendation**: The ROADMAP.md coverage metric for MISMATCH should reflect effective current coverage (doc-vs-system subset only), not the total addressable ~402. If the ROADMAP currently reports ~402 as covered, correct it. The correct number is the count of `agree_categorical` + `agree_numeric` checks in the current production ruleset, not the full MISMATCH row count.

---

### #12 · 005 has no real promotion trigger — Ruleset.version hardcoded to 1 everywhere

**Spec**: `005-eval-harness-as-promotion-gate`

**Contrarian case**: The eval harness spec is built around the premise that a version bump triggers the gate, and a zero-false-auto-clear rule is a hard block. But `Ruleset.version` is hardcoded to `1` in every location it appears in the codebase. Nothing in the spec or the codebase causes this version to increment on any real event (e.g., a new compile run, a new sign-off, a new SME edit). The gate is real code but is structurally disconnected from the production workflow — it is a "run it manually when you remember" tool, not an actual gate.

**Why not auto-fixed**: Wiring the version bump to a real event (e.g., `assemble_ruleset` increments the version before writing the signed artifact) is a code change, not a spec text edit. The decision of what event constitutes a "new version" is a product call.

**Recommendation**: Decide: what event should cause `Ruleset.version` to increment? The most natural answer is "a new `assemble_ruleset` run that produces a signed artifact" — this is already the compile-then-run checkpoint. Spec this explicitly in 005 or 002b (which owns `assemble_ruleset`). Until this is wired, the promotion gate will never run automatically regardless of how correct its logic is.

---

### #13 · agree_doc_categorical/agree_doc_numeric have no scenario construction strategy in 005

**Spec**: `005-eval-harness-as-promotion-gate`

**Contrarian case**: `score_drafts.py`'s `SCORERS` covers 4 of the 6 live check kinds (`predicate`, `ratio_threshold`, `agree_categorical`, `agree_numeric`). The two kinds added by 003d (`agree_doc_categorical`, `agree_doc_numeric`) have no generalized `ScenarioConstructionStrategy` in 005's design. The COVERAGE tier therefore has zero automated coverage for the check kinds that handle the doc-vs-doc majority of real MISMATCH conditions. An eval harness that cannot construct scenarios for the dominant check kind is structurally incomplete.

**Why not auto-fixed**: Designing the construction strategy for `agree_doc_categorical`/`agree_doc_numeric` requires understanding the fixture shape for doc-vs-doc comparisons (both `truth` and a named `sources` entry carry doc-side values, unlike the doc-vs-system case). This is a non-trivial design task.

**Recommendation**: Add a FR to 005 (or 003d, as a follow-on) to specify the `ScenarioConstructionStrategy` for these two kinds. This is a blocker for the 005 COVERAGE tier being meaningful once Phase 2 of 003d ships.

---

### #14 · 010a's "21% fail-open" framing stale after post-hoc column-shift correction

**Spec**: `010a-program-applicability-gating`

**Contrarian case**: The spec's preamble documents the post-hoc correction: after the column-shift fix, 86.1% of rows are tagged (7,271/8,442), not 79%. But the Edge Cases section still says "21% of rows with no program-prefixed Exception Code" — internally consistent with the old pre-correction count, but inconsistent with the preamble's corrected 86.1% figure. A reader reading Edge Cases without reading the preamble gets a materially wrong picture of the fail-open exposure.

**Why not auto-fixed**: The Edge Cases paragraph needs to be updated to use the post-correction numbers — straightforward text fix, but requires reading the preamble carefully to get the right numbers (the 13.9% unresolved fraction after correction, not the old 21%).

**Recommendation**: Update the Edge Cases section to say "~13.9% (1,171/8,442 rows) remain unresolved by program-prefix parsing" and footnote the pre-correction 21% figure as the historical baseline.

---

### #15 · 010b proven on 5/5 owner-occupied loans only — investment/second-home path unverified on real data

**Spec**: `010b-derive-remaining-gating-dimensions`

**Contrarian case**: All 5 real loan fixtures (loan_01 through loan_05) are owner-occupied. The investment property and second-home derivation paths in `build_loan_profiles_v3.py` have been proven only against hand-constructed `CanonicalLoan` fixtures. If real extracted data encodes occupancy indicators differently than the construction strategy assumes (e.g., different field names, different coded values), the non-owner-occupied paths will silently misfired. Since real non-owner-occupied loans are not in the fixture set, this will not be caught by any existing test.

**Why not auto-fixed**: Getting at least one real non-owner-occupied loan into the fixture set requires a real data acquisition action (sourcing from S3 or requesting from Kayla), not a spec edit.

**Recommendation**: Track this as an explicit known gap in 010b's spec/plan. Add a requirement that before production use on mixed-occupancy portfolios, at least one investment-property and one second-home real loan is processed through the `occupancy_type` derivation path and its result validated against the known loan facts. The 012 real-loan eval work is the natural venue for this.

---

### #16 · 011 GOLDEN panel promotion has no defined cadence — flywheel may spin without ever landing

**Spec**: `011-label-confirmation-flywheel`

**Contrarian case**: The label-confirmation flywheel's end-to-end value proposition depends on confirmations eventually landing in the GOLDEN eval panel (FR-007), which in turn gates ruleset promotion (005). But FR-007 says GOLDEN-panel promotion is "a separately-invoked human-curated step" with no defined cadence, trigger, or responsible party. A flywheel that collects confirmations but has no defined moment when they enter the eval gate is functionally the same as no flywheel at all — the confirmations accumulate in `ConfirmationLog` without producing the ruleset-quality feedback loop the spec promises.

**Why not auto-fixed**: Defining the cadence (e.g., "after N confirmations on the same check, a Kayla/SME review session promotes the top candidates to GOLDEN") is a process/product decision.

**Recommendation**: Add a FR or process note to 011 specifying: what quantity of confirmations triggers a GOLDEN-panel review session, who conducts it, and how the output feeds back into 005's promotion gate. Even a draft process ("every 50 confirmations, Gordon + Kayla review the candidates") would close the structural gap.

---

### #17 · 012 introduces a PII risk category this repo has no established guardrails for

**Spec**: `012-real-loan-distribution-eval`

**Contrarian case**: Three real loans with confirmed PII (real borrower names, SSN last4 fragments, real property addresses) are already in S3. This repo's `.gitignore` provides only light coverage (`demo/` directory exclusion). The `demo-sites/dynamic-mortgage-qc` project handled this explicitly by building synthetic stand-ins; this repo has no equivalent discipline. FR-012 in the spec names and addresses the git-exclusion requirement, but it is a feature requirement in a spec — not a repo-level policy that applies before and after this feature ships.

**Why not auto-fixed**: The right fix is a repo-level policy decision (`.gitignore` additions, a pre-commit hook or CI check for PII patterns, clear documentation of what lives in S3 vs. git), not a feature requirement in one spec.

**Recommendation**: Before any real-loan data work starts, establish repo-level PII guardrails: (a) explicit `.gitignore` entries for any path pattern that could carry real loan data (not just `demo/`), (b) a brief README note or CLAUDE.md entry documenting the boundary ("real loan data lives in S3 only, never committed"), (c) the PII scan gate from 012 SC-004 run against the repo's current state to confirm no PII has already leaked.

---

### #18 · 014 introduces per-loan LLM cost with no budget threshold or blocking mechanism

**Spec**: `014-decision-narrative`

**Contrarian case**: 014 is the first feature that introduces per-loan-per-run LLM cost — deliberately breaking the zero-LLM-at-runtime discipline. Cost is logged (FR-009) but there is no mechanism to block generation if cumulative cost exceeds a threshold, no alert when a single run produces unexpectedly high spend, and no way to disable narrative generation for a run batch without a code change. On a 10,000-loan portfolio run with 3 exceptions per loan, 30,000 LLM calls at current Sonnet pricing is a non-trivial bill, with no circuit breaker.

**Why not auto-fixed**: Whether a cost threshold/circuit-breaker is appropriate is a product call — it depends on the deployment model (per-loan fees passed to customer vs. Tavant-absorbed cost).

**Recommendation**: Add to 014 a FR specifying either: (a) a configurable `max_narrative_cost_per_run` threshold that disables narrative generation if exceeded (with a logged warning), or (b) a clear documented decision that cost is unbounded by design (e.g., "customer billed per exception reviewed"). At minimum, document the expected cost range per run in the spec so operators know what they're signing up for.

---

### #19 · 011+012 corpus shape alignment unverified — concurrent specs may diverge at first wiring

**Specs**: `011-label-confirmation-flywheel`, `012-real-loan-distribution-eval`

**Contrarian case**: Both specs were written on 2026-07-27 and define corpus entry shapes independently. 012's User Story 4 names the alignment requirement ("RealLoanCorpusEntry shares shape with 011's LabelCorpus entries") but this is unverified since neither is implemented. If 011's `LabelCorpus` entry shape diverges from 012's `RealLoanCorpusEntry` (different field names, different nullable treatment, different provenance fields), the first attempt to wire them together will fail with a data-model incompatibility that was avoidable.

**Why not auto-fixed**: The fix is to explicitly cross-spec the two shapes now, before implementation — a spec review action, not a text error correction.

**Recommendation**: Before implementing either spec, produce a single canonical `CorpusEntry` type definition (possibly in a shared `types.py` or in the 011 spec as the authoritative shape) and have 012 reference it explicitly rather than saying "shares shape." This is a one-session task that prevents a two-session integration debugging session later.

---

### #20 · 012 G3 real-loan re-run may report BLOCKED indefinitely — expert-adjudicated labels on Kayla's timeline

**Spec**: `012-real-loan-distribution-eval`

**Contrarian case**: The spec's primary eval goal — comparing real-loan engine output against expert-adjudicated labels — depends on Kayla completing label review for the 3 acquired loans. This is outside the feature's control. The spec handles this with FR-011 (explicit BLOCKED report when labels not yet available), which is correct, but it means the spec's most important deliverable (the "$700–$3,500/run" figure's empirical replacement with a reasoned, calculated number) may remain undelivered for the feature's entire initial shipping lifetime.

**Why not auto-fixed**: This is a people/dependency management concern, not a spec text error.

**Recommendation**: Document the label-review ask to Kayla explicitly — not just as a feature requirement in this spec, but as a named action item on the engagement calendar. The 012 spec's value proposition is substantially weaker without at least one expert-labeled real loan to compare against. Consider whether the 3 S3 loans already acquired include any that have already been through a manual QC review (i.e., existing Kayla review notes that could serve as ground truth without a new review cycle).

---

## Small Direct Fixes Applied

The following were clearly-correct corrections made directly to spec files:

| Spec | Fix applied |
|------|-------------|
| 003a-engine-predicate-checks | Status header: "Draft" → "Implemented (2026-07-08, commit `dd94e4b`)" |
| 003b-engine-ratio-threshold-checks | Status header: "Draft" → "Implemented (2026-07-09, commit `b87d987`)" |
| 003c-engine-reconcile-checks | Status header: "Draft" → "Implemented (2026-07-16, commit `cd545a6`)" |
| 003d-engine-doc-vs-doc-reconcile-checks | Status header: "Draft" → "Implemented (2026-07-26, commit `41b8499`)" |
| 004-loan-disposition | Status header: "Draft" → "Implemented (2026-07-16, commit `2994794`)" |
| 010a-program-applicability-gating | Status header: "Draft" → "Implemented (2026-07-26, commit `0741905`)" |

---

## Iteration 2 — Completed 2026-07-27

Iteration 2 completed:
1. Read this findings file in full (all 21 specs already covered — no re-read of spec bodies needed except targeted sections)
2. Verified findings #3, #11, #12, #14 by direct code inspection (see Closing Summary table)
3. Confirmed #11 is NOT a ROADMAP overclaiming issue — ROADMAP already correctly scopes Phase 2 as unscheduled
4. Fixed finding #14's Edge Cases text directly in 010a spec (21% → ~13.9%)
5. Evidence-groundedness spot-check on 005, 010b, 011, 012 — all four pass with high confidence
6. Wrote closing summary at top of this file with go/no-go verdict

**No new findings added in Iteration 2.** All 20 human-judgment findings from Iteration 1 stand. See Closing Summary for the CONDITIONAL GO recommendation and 3 pre-production blockers.
