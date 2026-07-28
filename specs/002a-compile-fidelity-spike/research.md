# Research: Compile-Fidelity Spike

## Unknowns resolved

### 1. What sample size for the spike?

**Decision**: ~20-30 sampled workbook rows, stratified across the three classified archetypes
(predicate / ratio_threshold / reconcile) in rough proportion to their real prevalence in
`taxonomy.json` (predicate 2,937 → threshold 853 → reconcile 402, i.e. roughly 70% / 20% / 10%).

**Rationale**: External research on pilot/feasibility study sample sizing (web search, 2026-06-30)
places qualitative-calibration pilots at 7-29 samples as "exploratory calibration," with 30 as the
median target across pilot/feasibility studies generally (IQR 20-50). This spike is explicitly a
throwaway mechanism test, not a population-accuracy study — it sits deliberately at the low end of
that calibration band, matching the honesty discipline already established by the G3 bake-off
(`p0/experiment_g3/PRE-REGISTRATION.md`), which used ~6 loans and stated plainly that determinism
findings generalize but accuracy findings are directional-only at that N. The same posture applies
here: large enough to catch a systematic interpretation failure across archetypes, small enough to
respect Kayla's scarce review time and the spike's throwaway nature.

**Alternatives considered**:
- A larger sample (50+) for statistical confidence — rejected: the spike's answer (PROCEED /
  RECONSIDER / KILL) is a mechanism test, not a rate estimate; a clearer signal at low N (e.g. 30%+
  interpretation-error rate) is decisive regardless of sample size, and the roadmap explicitly frames
  this as a throwaway spike, not the population-level accuracy study (that's roadmap feature `012`,
  gated on Kayla's real labeled loans separately).
- Stratification by AMQ category (17 categories) instead of by check-kind archetype — rejected:
  research explicitly cautions against stratification in small pilots (fragments already-small N
  further); the check-kind archetype (predicate/threshold/reconcile) is the dimension the engine and
  eval_synth already speak in, so stratifying along it keeps the sample legible to the existing
  scoring mechanism without fragmenting it into 17 tiny buckets.

Sources:
- [Guidelines for Designing and Evaluating Feasibility Pilot Studies (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8849521/)
- [A review of sample sizes for UK pilot and feasibility studies on the ISRCTN registry from 2013 to 2020](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10662929/)
- [Pilot Study Sample Size Rules of Thumb (NCSS)](https://www.ncss.com/wp-content/themes/ncss/pdf/Procedures/PASS/Pilot_Study_Sample_Size_Rules_of_Thumb.pdf)

### 2. What structured-output approach for LLM rule compilation?

**Decision**: Reuse the existing structured-JSON, temperature=0 pattern already proven in
`p0/experiment_g3/llm_arm.py` (Bedrock, AWS profile `gordon-chan`, cross-region inference profile),
targeting `p0/qc_engine/ruleset.py`'s existing `Check` schema as the LLM's required output shape,
rather than inventing a new prompting or schema-validation approach for this spike.

**Rationale**: External research (web search, 2026-06-30) on LLM-based structured extraction from
spreadsheets confirms the current best-practice pattern is: combine prompt engineering with a fixed
target schema and a validation/scoring layer downstream — exactly the shape this project already
has (`Check` dataclass + `p0/eval_synth`'s scorer). No new infrastructure is justified when a proven,
already-validated harness exists for LLM-to-structured-output compilation in this exact codebase.

**Alternatives considered**:
- A new few-shot prompting framework or RAG layer over the workbook — rejected: over-engineering
  for a throwaway spike; the question is whether a *direct* compile (row → `Check`) works at all,
  not whether an elaborate prompting pipeline can be made to work. If the direct approach fails,
  that itself is spike-worthy information (a stronger KILL/RECONSIDER signal), not a reason to reach
  for more machinery before testing the simple case.

Sources:
- [Automating Document Validation Using LLMs: Building a Smart Rule Engine with RAG and Prompt Engineering](https://medium.com/@alysameh2002/automating-document-validation-using-llms-building-a-smart-rule-engine-with-rag-and-prompt-4aa679907812)
- [Agent-Based LLM System for Extracting Structured Data: A Dual-Validation Study (medRxiv)](https://www.medrxiv.org/content/10.1101/2025.11.25.25340989.full.pdf)

### 3. How should the SME (interpretation-fidelity) review be structured?

**Decision**: A dual-column review artifact — source workbook row (question/response/exception
code/significance, verbatim) next to the LLM-drafted `Check`, restated in plain English — with a
single per-row judgment column (correct / incorrect / ambiguous) and a free-text correction field,
handed to Kayla as a reviewable document (not a live UI — no authoring surface exists yet, per
`001a`'s assumption that 001a-era authoring is hand-done, procedurally reviewed).

**Rationale**: The "dual-validation" pattern in the medRxiv structured-extraction study (source
alongside LLM output, single human judgment per item) is the same shape already proven useful in
this project's own G3 bake-off methodology (steelmanned comparison, explicit per-item labeling) and
matches the roadmap's explicit language: "did the LLM read the workbook row the way the lender
*means* it" — a judgment made by reading the row, not by trusting the rule's internal logic.

**Alternatives considered**:
- Two independent SME reviewers with inter-rater agreement scoring (the "2+ annotator gold standard"
  pattern found in research) — rejected for this spike: only one SME (Kayla) is available per the
  project's established external-dependency constraint (CLAUDE.md Blocker 2/3); noted as a future
  strengthening if a second reviewer becomes available before `002b` is committed.

Sources:
- [Agent-Based LLM System for Extracting Structured Data from Breast Cancer Synoptic Reports: A Dual-Validation Study](https://www.medrxiv.org/content/10.1101/2025.11.25.25340989.full.pdf)

## Technical context (no NEEDS CLARIFICATION remaining)

- **Language/Version**: Python 3.9-compatible (project-wide constraint; matches `p0/` throughout).
- **Primary Dependencies**: `boto3` + Bedrock (reused from `p0/experiment_g3/llm_arm.py`); `openpyxl`
  (reused from `p0/eval_synth/taxonomy.py` for reading `demo/rules/*.xlsx`); no new dependencies.
- **Storage**: Flat files only — sampled rows, generated rule drafts, SME review artifact, and the
  pre-registration document are all files under `specs/002a-compile-fidelity-spike/` and a throwaway
  scratch directory; no database, consistent with the spike being explicitly non-durable.
- **Testing**: Reuses `p0/eval_synth`'s existing scorer directly (per roadmap: "uses the already-built
  `p0/eval_synth` scorer... not the later 005 CI productionization"). No new test framework.
- **Target Platform**: Local execution (same as all of `p0/`) plus one Bedrock API call per sampled
  row at compile time.
- **Project Type**: Throwaway experiment / spike script, not a service or library.
- **Performance Goals**: N/A — this is a one-time compile-and-score run over ~20-30 rows, not a
  performance-sensitive path.
- **Constraints**: Every LLM call happens at config/compile time only (Principle II); zero LLM calls
  may enter the QC engine's runtime evaluation path.
- **Scale/Scope**: ~20-30 sampled rows this spike; full-workbook compilation (7,398 conditions) is
  explicitly out of scope — that's `002b`, gated on this spike's verdict.
