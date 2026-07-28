# Quickstart: Running the Compile-Fidelity Spike

This is a one-time, throwaway experiment run — not a service to stand up. Steps, in order:

## 1. Sample rows (FR-001, FR-007)

Using `p0/eval_synth/taxonomy.py`'s existing classification of `demo/rules/*.xlsx`, draw ~20-30
rows stratified by archetype (≈70% predicate / 20% ratio_threshold / 10% reconcile, per
`research.md`). Record each as a `SampledWorkbookRow` (`data-model.md`).

## 2. Compile each row (FR-002)

For each sampled row, call the LLM at temperature=0 (reusing the Bedrock harness pattern in
`p0/experiment_g3/llm_arm.py`: profile `gordon-chan`, cross-region inference profile), requesting
output conforming to `contracts/compiled-rule-schema.md`. Record each result as a
`CompiledRuleDraft`.

## 3. Score runnability + constructed-label correctness (FR-003)

Feed each `CompiledRuleDraft`'s `check` object into the existing `p0/eval_synth` scorer, exactly as
it already scores checks today — no modification to the scorer itself. Record `runnable` and
`constructed_label_score`.

## 4. Build the SME review package (FR-004)

Assemble the dual-column document per `contracts/sme-review-package.md` — source row text next to
the `plain_english_restatement` — and hand it to Kayla. **This step has a human dependency; the
spike cannot conclude without it** (spec.md Edge Cases, Assumptions).

## 5. Collect judgments + compute correction cost (FR-004, FR-005)

For each row Kayla reviews, record the `InterpretationFidelityJudgment` (verdict + correction +
`reviewer_note`). Compute `edit_distance` between the LLM draft and Kayla's correction using the
existing edit-distance function in `p0/qc_engine/ruleset.py` (do not reimplement it).

## 6. Apply the pre-registered decision rule (FR-006)

Evaluate the collected results against `pre-registration.md`'s locked D1 → D2 → D3 sequence.
Produce the `SpikeFinding` (`data-model.md`): archetype distribution, interpretation-error rate,
mean edit-distance, zero-edit-batch flag, and the final PROCEED / RECONSIDER / KILL verdict.

## 7. Report and discard (FR-008)

Write the finding to `specs/002a-compile-fidelity-spike/RESULTS.md` (mirroring
`p0/experiment_g3/RESULTS.md`'s format). Delete or archive the throwaway compile/scoring scripts —
they are not a production artifact. If the verdict is PROCEED, the next action is
`/speckit-specify 002b-ruleset-compiler-pipeline`, specced fresh, not built by extending this
spike's code.

## What this quickstart deliberately does not include

- No CI wiring, no service deployment, no scaffold (Phase 4) — this is a spike, not a shipped
  feature; Phase 4/SCAFFOLD does not apply.
- No production compiler code — that is `002b`'s scope entirely, gated on this spike's verdict.
