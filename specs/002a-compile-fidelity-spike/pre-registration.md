# 002a Compile-Fidelity Spike — Pre-Registration

> **Locked before running.** Per the discipline already established in
> `p0/experiment_g3/PRE-REGISTRATION.md`: decision rules are fixed *now*, before any row is
> compiled or scored, so results cannot move the goalposts after the fact.
>
> **Locked at**: 2026-06-30 (this document's creation — must predate the first `constructed_label_score`, per SC-001).
> **Status**: PRE-REGISTERED · Data: a real, stratified sample of `demo/rules/*.xlsx` rows (not synthetic).

## The question

G3 (`p0/experiment_g3/`) tested whether a *runtime*-LLM should evaluate loans. It never tested
whether an LLM can, at *config time*, correctly compile the **real** AMQ workbook into a signed,
executable rule. This spike answers that question directly: can an LLM turn a real workbook row
into a rule that (a) runs correctly and (b) captures what the lender's row actually means — cheaply
enough, and with little enough SME correction, to justify specifying the production compiler (`002b`)?

## The sample

~20-30 rows from `demo/rules/*.xlsx`, stratified by check-kind archetype in rough proportion to real
prevalence (per `taxonomy.json`): roughly 70% predicate, 20% ratio_threshold, 10% reconcile.
Archetype distribution is reported alongside the finding (SC-006) so the sample's representativeness
is auditable, not asserted.

## Metrics (measured for every sampled row)

1. **Runnability + constructed-label correctness** — scored by the existing `p0/eval_synth` scorer.
   Reported as a pass rate, for context only (see D1 below for why this is not the deciding metric).
2. **Interpretation-fidelity rate** — the % of sampled rules Kayla judges `correct` against the
   source workbook row (not against the rule's own internal logic or its constructed-label score).
   **This is the primary metric.**
3. **Required SME correction** — mean edit-distance between LLM draft and Kayla-corrected rule,
   computed via the existing edit-distance function in `p0/qc_engine/ruleset.py`.
4. **Zero-edit-batch flag** — if the entire sample is signed with zero SME edits, flagged explicitly
   as a possible sign-off-theater signal (constitution Principle II), not silently reported as a win.

## Decision rules (LOCKED — evaluated in this order)

- **D1 (interpretation-fidelity gate — the primary gate).** If the interpretation-fidelity rate is
  **below 70%**, the compiler is misreading the workbook too often to trust at scale → **KILL** the
  compile-then-run approach for `002b` as currently conceived; the product's central differentiation
  needs rethinking (roadmap Tension 6).
- **D2 (runnability sanity check).** A rule that fails `p0/eval_synth`'s constructed-label scorer
  (not runnable, or runs but produces the wrong verdict on constructed labels) is **always** counted
  as an interpretation failure for D1, regardless of what the SME thinks of its prose restatement —
  a rule that doesn't run is disqualifying on its own, not something D1 can override in the other
  direction.
- **D3 (correction-cost check).** If the mean edit-distance is high enough that Kayla is, in
  substance, rewriting most rules from scratch (a qualitative judgment she records via
  `reviewer_note`, since there is no pre-existing numeric threshold for "rewriting from scratch" in
  this codebase) — treat this as evidence the LLM isn't compiling, the SME is, **even if D1 passes**.
  This downgrades a D1-pass toward **RECONSIDER** rather than a clean PROCEED.
- **VERDICT mapping:**
  - D1 fails (interpretation-fidelity < 70%) → **KILL**.
  - D1 passes (≥ 70%) and D3 shows low correction cost → **PROCEED** to specifying `002b`.
  - D1 passes but D3 shows high correction cost, or the sample is too ambiguous to call cleanly →
    **RECONSIDER** — run a second, larger spike round before committing to `002b`, rather than
    forcing a binary call the evidence doesn't support (spec.md Edge Cases).

**Why 70% and not some other number**: there is no pre-existing internal benchmark for this specific
metric (this is the first time it's been measured). 70% is chosen as the threshold below which more
than 1 in 4 compiled rules would misread the lender's intent — a rate high enough that per-rule SME
review (which `002b` and `009a`'s diff-and-sign surface both assume will remain lightweight) would
become, in practice, a full re-derivation of every rule. This is a judgment call, stated plainly as
one, not derived from an external benchmark — flagged here for the same reason G3 flagged its own
assumptions rather than presenting them as more rigorous than they are.

## Honesty caveats (pre-committed)

- **Small N, by design.** ~20-30 rows is a calibration-pilot sample (per `research.md`'s external
  research), not a population study. A clear signal (e.g., an interpretation-fidelity rate near 0%
  or near 100%) is decisive regardless of N; a borderline result (near the 70% line) is genuinely
  ambiguous at this sample size and should route to RECONSIDER rather than being forced to PROCEED
  or KILL.
- **One SME reviewer.** Kayla alone provides the interpretation-fidelity judgment. No inter-rater
  reliability check is possible at this stage (`research.md` decision #3) — a second reviewer would
  strengthen this finding before `002b` is committed, but is not available now.
- **One model, one temperature.** Consistent with the G3 precedent: if the model used here fails
  D1, a stronger model might do better — but a stronger model also costs more, so (per G3's D3) that
  trade is itself informative, not evaded by testing every model available.
- **This is not the production compiler.** A PROCEED verdict authorizes speccing `002b` next. It
  does not mean `002b` is pre-built, and `002b`'s implementation must not extend this spike's
  throwaway code (FR-008, spec.md Assumptions).
