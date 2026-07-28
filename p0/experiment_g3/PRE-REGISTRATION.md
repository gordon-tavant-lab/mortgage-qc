# G3 Bake-Off — Pre-Registration

> **Locked before running.** The thesis required a per-file cost estimate "before
> committing to any runtime-LLM path." It was never produced. This experiment
> produces it — and tests determinism + accuracy head-to-head — on evidence, not
> assertion. Decision rules are fixed *now* so we can't move the goalposts after
> seeing results.
>
> Date: 2026-06-27 · Status: PRE-REGISTERED · Data: synthetic golden loans (real
> Kayla loans pending, 1–2 weeks out — see caveat).

## The question
Does the **compiled, deterministic engine** (P0) beat a **governed runtime-LLM**
(Olav's approach, steelmanned) on the three axes that actually matter for this
product — **determinism, accuracy, cost** — enough to justify building the
compile-then-run architecture instead of a governed runtime-LLM?

## The two arms (same inputs, same golden loans, same checks)
- **Arm A — Compiled engine (P0):** `qc_engine.run(loan, signed_ruleset)`. Pure
  Decimal, no model at runtime. Already proven bit-exact across 1000 runs.
- **Arm B — Governed runtime-LLM (steelmanned):** Claude Haiku 4.5 on Bedrock,
  **temperature=0**, structured JSON output, given the SAME rule definitions and
  the SAME canonical loan data, asked to return PASS/FAIL/FLAG per check. All
  arithmetic asked of it is simple (rate compare, LTV threshold) — we give the
  LLM its best, fair shot (clean prompt, low temp, structured schema). We do NOT
  hand it a deliberately bad prompt.

## Metrics (measured identically for both arms)
1. **Determinism** — run each loan **N=5 times**. Are the per-check verdicts
   **byte-identical** across all 5? (Arm A: expected YES by construction. Arm B:
   the open question — does temp=0 actually yield identical verdicts every time?)
2. **Accuracy** — per-check verdict vs the **labeled ground truth** in the golden
   fixtures. Report exact-match rate, and the **false-auto-clear count** (the
   catastrophic error: engine says PASS where truth says a defect exists).
3. **Cost** — Arm B: real input+output **tokens per loan** from Bedrock usage →
   extrapolate to **10,000 loans** (the thesis's scale). Arm A: ~$0 tokens
   (CPU only). Tests the "$10K/run" claim directly.
4. **Latency** — wall-clock per loan per arm (informational).

## Decision rules (LOCKED — evaluated in this order)
- **D1 (determinism gate).** If Arm B is **not** byte-identical across the N runs
  on **even one loan**, the compiled engine wins the determinism axis outright —
  a non-reproducible verdict cannot pass a "show the same math every time" audit.
- **D2 (accuracy gate).** If Arm B produces **any false-auto-clear** that Arm A
  does not, that is a disqualifying safety failure for the runtime-LLM at current
  maturity (the catastrophic error, §6 of the PRD).
- **D3 (cost test).** Record Arm B's extrapolated 10k-loan cost.
  - If **> ~$2,000/run** → the thesis "cost at scale" concern is **CONFIRMED**;
    compiled engine wins on cost.
  - If **< ~$200/run** → the cost scar is **STALE**; cost is NOT a valid reason
    to prefer compiled (must then win on D1/D2 alone). *(This is the outcome that
    would most challenge our bet — we pre-commit to reporting it honestly.)*
  - Between → cost is a soft factor, decide on D1/D2.
- **VERDICT mapping:**
  - Arm B fails D1 **or** D2 → **PROCEED with compiled-then-run architecture**
    (determinism/safety justify it regardless of cost).
  - Arm B passes D1 **and** D2 **and** D3 shows cheap → **RECONSIDER**: the
    governed-LLM may be viable; run a larger trial before locking architecture.

## Honesty caveats (pre-committed)
- **Synthetic data limit.** These loans are hand-authored; they under-represent
  the OCR noise / ambiguity of real extracted docs. Determinism and cost results
  generalize; **accuracy results are directional only** until Kayla's real,
  independent-path loans land. We will label the accuracy numbers accordingly.
- **Small N.** ~6 loans × small check set. Enough to test determinism (a single
  non-identical run is decisive) and to get a real per-loan token cost; **not**
  enough to claim a population false-clear rate. Stated as such.
- **One model.** Haiku 4.5 is the cheap/fast steelman. If it fails D1/D2, a
  larger model might pass — but a larger model worsens the cost axis, so the
  trade is itself informative. We note this rather than testing every model.
