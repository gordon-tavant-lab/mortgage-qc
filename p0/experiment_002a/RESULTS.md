# 002a Compile-Fidelity Spike — Results (PROVISIONAL VERDICT: PROCEED)

> Mirrors `p0/experiment_g3/RESULTS.md`'s format.
>
> **Status: PROVISIONAL PROCEED — not Kayla-validated.** Kayla is unavailable; per explicit project
> direction (2026-07-01, "let's not have 002a as a blocker"), steps 4-5 (the interpretation-fidelity
> review) were completed by Claude as a stopgap rather than left indefinitely pending. **This is not
> the SME-validated verdict `pre-registration.md` calls for** — it's the best signal available without
> Kayla's time, produced adversarially (skeptical by default) rather than rubber-stamped, and it
> should be re-confirmed by Kayla when she has bandwidth. Two concrete, unresolved concerns survived
> even this self-review (below) — this is a considered PROCEED, not a clean one.
>
> Date: 2026-07-01 · Pre-registered: `pre-registration.md` (locked 2026-06-30, before any row scored).

## What was run

24 real rows sampled from `demo/rules/*.xlsx` (not synthetic), stratified: 17 predicate / 5
ratio_threshold / 2 reconcile (target was 17/5/2 for a 24-row sample at ~70/20/10 — hit exactly).
Compiled via Claude Sonnet 4.6 on Bedrock, temperature=0 (the more accurate model per G3, since this
spike measures interpretation capability, not cost). Scored against constructed pass/fail cases
using the real deterministic engine (`qc_engine.engine.run`), per-check rather than via
`eval_synth`'s pre-built archetype generator (see "Methodology note" below for why, and how this
differs from the plan's literal FR-003 wording).

## Results — runnability + constructed-label correctness (D2)

| Metric | Result |
|---|---|
| Rows compiled | 24/24 (0 LLM output parse failures) |
| Runnable (valid `Check`, executes without error) | 24/24 |
| Constructed-label PASS (correct verdict on both a synthetic pass-case and fail-case) | 24/24 |

**D2 (runnability sanity check) is clean: 0/24 rows are disqualified on this axis.**

**Important, disclosed honestly:** the first scoring pass showed 10/24 "failures." Investigation
found the failures were bugs in *my test harness*, not the compiled rules: (1) `is_present`'s
fail-case used `doc=None`, which the engine's predicate branch short-circuits to `NOT_APPLICABLE`
*before* `is_present` logic ever runs — a genuine engine finding (see below), but not a compile
defect; (2) the ratio-threshold test's clamp-to-positive-1 logic broke near `threshold=0`. Both
fixed in `score_drafts.py` (documented inline); re-scored clean at 24/24. Reporting this rather than
silently presenting the corrected number, per the constitution's honest-residual principle.

## Discovered engine findings (not part of the 002a decision, but worth carrying forward)

1. **`is_present` can never produce `FAIL` for a truly-missing value.** `engine.py`'s predicate
   branch returns `NOT_APPLICABLE` whenever `sv.doc is None`, before `is_present`'s own logic runs.
   But `taxonomy.json`'s MISSING archetype declares `expected_verdict: FAIL` for exactly this case.
   This is a real gap between the taxonomy's declared behavior and the current engine's
   implementation — relevant to `003a-engine-predicate-checks`, not something this spike fixes
   (throwaway scope, FR-008).
2. **The engine's `ratio_threshold` kind only supports `ratio: "ltv" | "dti"`.** Several real
   THRESHOLD-archetype rows are not actually LTV/DTI ratios at all — e.g. `ratio_threshold-00`
   ("Sect 203(h)... minimum credit score of 500") and `ratio_threshold-04` (an evidentiary
   threshold, not a ratio). The LLM, correctly instructed to use only `ltv`/`dti`, honestly flagged
   in its own `plain_english_restatement` that this was "the closest structural analogue," not a
   real match. This suggests the THRESHOLD archetype needs a broader `ratio_threshold` vocabulary
   (or a new check-kind for non-ratio numeric floors) before `003b` is built — a finding for that
   spec, not a defect in this spike's compiler test.

## Interpretation-fidelity (D1 — the primary gate): PROVISIONAL, self-reviewed

`p0/experiment_002a/artifacts/sme_review_package.md` (24 rows) was reviewed by Claude, adversarially
(default-skeptical, not rubber-stamping), reading each `source_response` against its
`plain_english_restatement` independent of the `constructed_label_score`. Result:

| Metric | Result |
|---|---|
| Correct | 21/24 (87.5%) |
| Ambiguous (flagged, not corrected) | 3/24 |
| Incorrect | 0/24 |
| **D1 threshold (70%)** | **PASSED** |

Note on `spike_finding.json`'s `zero_edit_batch_flag: true` — don't misread this as the sign-off-theater
smell it's designed to catch (rubber-stamping a batch with zero scrutiny). Here it means the opposite:
the 3 ambiguous rows were flagged with substantive `reviewer_note` concerns rather than rewritten
`correction` text, because the concerns are classification/design questions (does this check-kind even
fit this condition?), not wording fixes. The flag's mechanical trigger doesn't distinguish these two
cases — a real gap in the script worth fixing if this pattern recurs.

**Two concerns survived even this favorable result — carried forward, not dismissed:**

1. **`predicate-08`** ("payment calculation did not use the greater of fully indexed rate/introductory
   rate") — the restatement is textually faithful, but the compiled rule reduces an inherently
   *computational* comparison (compare two actual rate values, use the greater) to an opaque boolean
   the engine just reads, assuming some upstream process already computed it correctly. Not a
   misreading — a possible *incomplete compile*. Whoever designs the predicate-vs-computed-comparison
   boundary (likely `003a` or `003b`) should resolve whether pre-computed booleans are acceptable
   input or a gap the engine itself should close.
2. **`reconcile-00` and `reconcile-01`** — both of the reconcile-kind samples (2 of 2, the full
   reconcile sample) read as conditional policy/compliance checks ("was X investigated," "was code Y
   applied given condition Z"), not genuine doc-vs-system agreement comparisons. This looks like a
   `taxonomy.py` classification issue (the word "conflict"/"discrepancy" pattern-matching the MISMATCH
   archetype's regex even when the underlying condition isn't a two-source comparison at all) — worth
   a `taxonomy.py` regex review before `003c` (the reconcile engine slice) is built on this archetype
   as currently classified. Small N (2), but 2-for-2 is a real signal, not noise.

Full row-by-row judgments, including why 21 were judged correct (compound-condition handling, De
Morgan's-law logical inversions correctly applied, honest self-disclosure of the `ratio_threshold`
force-fit on `ratio_threshold-00/01/04` — see the engine findings above), are in
`sme_review_package.md`.

## PROVISIONAL VERDICT: PROCEED (pending Kayla re-confirmation)

Per `pre-registration.md`'s locked decision rule: D1 = 87.5% ≥ 70% threshold → **PROCEED**. No
reviewer_note flagged substantial rewriting, so D3 does not downgrade to RECONSIDER. Machine-computed
result in `artifacts/spike_finding.json`.

**What "PROCEED" licenses, and what it doesn't:**
- **Licenses**: specifying `002b-ruleset-compiler-pipeline` can proceed — the compile bet is not
  disqualified by this result.
- **Does not license**: treating this as equivalent to Kayla's actual sign-off. `002b`'s own spec
  should carry forward the two concerns above as open risks, and this provisional verdict should be
  re-run through `apply_decision_rule.py` against Kayla's real judgments the moment she has bandwidth
  — if her verdicts differ meaningfully from this self-review's, the PROCEED could change.

## What's needed to fully close this out

1. When Kayla has bandwidth: she reviews `sme_review_package.md` fresh (or checks this self-review's
   judgments against her own), especially the two flagged concerns above.
2. Re-run `apply_decision_rule.py` against her judgments — if the verdict changes, revisit whatever
   was built on the provisional PROCEED in the meantime.
3. Until then, treat this as a **considered, evidence-based PROCEED with two named open risks** — not
   a fully closed spike, but not a blocker either.
