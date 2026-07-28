# G3 Bake-Off — Results

> Companion to `PRE-REGISTRATION.md`. The decision rules D1/D2/D3 and the verdict
> mapping were **locked before this ran** — this file reports what the evidence
> said, including the parts that *contradict* the thesis we walked in with.
>
> Date: 2026-06-28 · Data: synthetic golden loans (6, 26 checks) ·
> `temperature=0` · N=5 runs/loan · Two Arm-B models tested.
> Artifacts: `artifacts/g3_bakeoff_g3run1.json` (Haiku),
> `artifacts/g3_bakeoff_g3run2_sonnet.json` (Sonnet).

## Headline

**The verdict depends on the model — and that is the finding.** Run on the cheap
steelman (Haiku 4.5), the runtime-LLM committed the catastrophic error and the
locked rules said *proceed with compiling*. Run on Sonnet 4.6, the runtime-LLM
passed both safety gates and the locked rules said *reconsider*. The
architecture choice is therefore **not** settled by determinism or cost — it
turns entirely on **whether the runtime model is accurate enough on boundary
QC**, and that is exactly what we don't yet know on real loans.

| Axis | Arm A — engine | Arm B · **Haiku 4.5** | Arm B · **Sonnet 4.6** | Pre-reg expectation |
|---|---|---|---|---|
| **D1 · Determinism** | bit-exact | identical ×5, every loan ✓ | identical ×5, every loan ✓ | open question |
| **D2 · Accuracy / safety** | 26/26, **0 false-clears** | 19/26 (0.73), **1 false-clear** ✗ | 25/26 (0.96), **0 false-clears** ✓ | the catastrophic class |
| **D3 · Cost @ 10k loans** | **$0.00** | ~$26.69 (regional) | ~$69.62 (regional) | "$10K/run" scar |
| **Locked verdict** | — | **PROCEED (compile)** | **RECONSIDER (larger trial)** | — |

The one Sonnet miss was **non-catastrophic**: `LN-95301/chk-borrower-name`
expected PASS, returned FLAG (over-cautious on a name-normalization match). It
flagged a clean loan for a human — annoying, not dangerous. Crucially, Sonnet
**caught the 98%-LTV loan that Haiku cleared.** The catastrophic error was a
*small-model* artifact, not an intrinsic runtime-LLM property.

## What each gate actually found

### D1 — determinism: both models passed (this surprised us the *other* way)
At `temperature=0`, **both Haiku 4.5 and Sonnet 4.6** returned byte-identical
verdict sets across all 5 runs, on every loan. The reflexive argument "the LLM
may vary at runtime" did **not** hold at this scale, for either model. We cannot
lean the architecture case on per-run flakiness alone — it didn't appear here.

### D2 — accuracy / safety: model-dependent (the whole ballgame)
This is where the two models diverged, and it is the crux of the decision.

**Haiku 4.5 — 19/26 (0.73), one false-auto-clear (DISQUALIFYING):**
- **`LN-QCFAIL / chk-ltv-max` — expected FAIL, got PASS.** LTV = 343,000 /
  350,000 = **98.0%** against a **95%** program max. Haiku cleared it, and per D1
  cleared it *reproducibly every time.* This is the catastrophic error (PRD §6):
  a **stable wrong answer** is worse than a flaky one — it survives a "show me
  the same number twice" audit while still buying back the loan.
- Plus semantic drift: 4× reconcile checks → `FLAG` where truth is `PASS`; 2×
  `chk-note-signed` → `FAIL` where truth is `PASS`.

**Sonnet 4.6 — 25/26 (0.96), zero false-auto-clears (PASSED):**
- **Caught the 98%-LTV loan** Haiku cleared. No catastrophic error.
- One non-catastrophic miss: `LN-95301/chk-borrower-name` expected PASS, got
  `FLAG` — over-cautious on a name-normalization match. It routed a clean loan
  to a human. Annoying, fail-safe, not dangerous.

**The lesson: the catastrophic error was a *small-model* artifact, not an
intrinsic property of running an LLM at runtime.** A capable model, given the
rules and low temperature, did the boundary arithmetic correctly and
reproducibly.

### D3 — cost: the "$10K/run" scar is stale for both models
Real Bedrock usage, extrapolated to 10,000 loans (on-demand rates verified
2026-06-28; regional = `us.` cross-region profile, +10%):

| Model | tokens/loan (in/out) | global rate | regional rate |
|---|---|---|---|
| Haiku 4.5 ($1/$5 per MTok) | ~1,130 / ~259 | $24.26 | **$26.69** |
| Sonnet 4.6 ($3/$15 per MTok) | ~1,131 / ~196 | $63.29 | **$69.62** |
| Arm A (engine) | 0 / 0 | — | **$0.00** |

The thesis's "per-run inference on 10,000 files could cost $10K/run" is **off by
~150–400×.** Even the more expensive, more accurate model is **~$70 per 10k-run.**
Cost is **not** a valid reason to prefer compiling. (Arm A is still free, so
compiling wins the cost axis — but the magnitude is trivial, not the
order-of-magnitude story the thesis told.)

## What this means for the product architecture

The decision under test: **does the QA/QC product compile a signed ruleset and
run it deterministically, or run a governed LLM at evaluation time?** The original
case for compiling rested on two pillars (CLAUDE.md non-negotiable #1):
(a) *regulatory audit* — same loan, same math, every time; (b) *cost at scale*.

The evidence reshapes the case:
- **Pillar (b) cost is dead** — ~$27–70/10k-run, not $10K. Drop it as a reason.
- **Pillar (a)'s "the LLM varies" sub-claim is dead** — both models were
  byte-identical at temp=0. Drop it too.
- **What's left and is real:** the runtime-LLM's *correctness* is **not
  guaranteed and is model-dependent.** Haiku silently bought back a loan; Sonnet
  didn't. The compiled engine is correct *by construction* and **shows the
  Decimal math + rounding policy** an auditor can re-derive — a property no
  runtime model offers regardless of accuracy.

**Recommendation (unchanged conclusion, honest rationale): keep the compiled
engine as the default** — but justify it on **auditability + guaranteed
correctness on the math**, not on variance or cost. The defensible one-liner:

> A runtime LLM *can* be reproducible and cheap, and a strong model *can* get the
> arithmetic right — but you cannot know in advance that it did, and you cannot
> hand a regulator the derivation. The compiled engine gives you both, for free.

**The open risk this surfaces:** if a capable model (Sonnet) is in fact accurate
enough on *real* loans, the compiled-vs-runtime choice becomes a governance/audit
preference, not a correctness necessity. That is precisely what the real-loan
re-run (below) must resolve.

## Caveats (pre-committed, still binding)

- **Accuracy is DIRECTIONAL.** Synthetic, hand-authored loans under-represent OCR
  noise/ambiguity. The D2 number is not a population false-clear rate. The real
  number waits on **Kayla's expert-labeled, independent-path loans** (1–2 weeks
  out). D1 and D3 generalize; D2 does not yet.
- **Small N** (6 loans, 26 checks). Decisive for determinism (one non-identical
  run would have been fatal) and for a real per-loan token cost; **not** a
  statistical accuracy claim. Sonnet's 25/26 is *not* "96% accurate on real
  loans" — it's 25/26 on six hand-authored ones.
- **Two models tested** (Haiku 4.5, Sonnet 4.6). The model-dependence of D2 is
  itself the headline. We did not test Opus; a still-larger model is unlikely to
  change the architecture conclusion (it would only widen the cost gap while the
  audit argument stays the same).

## Follow-ups

1. ✅ **DONE** — Sonnet 4.6 re-run. The Haiku false-clear was a small-model
   artifact: Sonnet caught the 98%-LTV loan, 0 false-clears, at ~$70/10k-run.
2. Re-run the whole bake-off on Kayla's real labeled loans when they land →
   convert the D2 accuracy number from *directional* to *load-bearing*. This is
   the experiment that actually decides whether runtime-LLM correctness is
   trustworthy enough to make compiling a *preference* rather than a *necessity*.
