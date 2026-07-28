# Synthetic Eval — Pressing On Without Real Loans

> **The constraint:** real expert-labeled loans (Blocker 2) may be the *last*
> thing we get, if ever. **The response:** stop treating "we need real loans" as
> one blocker. It's three — and only one of them actually needs real files.
>
> Status: operational · Date: 2026-06-28 · `p0/eval_synth/`

## The decomposition that unblocks us

"Ground truth" bundles three separate questions. Only #3 truly needs real loans:

| What we need to know | Needs real loans? | How we get it here |
|---|---|---|
| **1. Engine correctness** — given the data, does the engine compute the right verdict per the signed spec? | **No** | Ground truth **by construction** (below). |
| **2. Interpretation correctness** — did we read check #347 the way the lender means it? | **No** | An expert reviews the **rule→mutation mapping** — a *rules review*, not a loan hunt. |
| **3. Defect distribution + extraction/OCR realism** — what actually goes wrong in the wild | **Partly** | The honest residual. Approximated, labeled loudly, deferred. |

The trap was letting #3 (hard) block #1 and #2 (solvable). This package solves
1 and 2 now.

## The core idea: ground truth *by construction*

The old fear — "synthetic data is untrustworthy because we made up the answer."
The inversion: **if WE inject the defect, we KNOW the answer. The mutation IS the
label.** No human adjudication required.

```
clean loan (all PASS)  --mutation(archetype)-->  (mutated loan, {check: expected})
                                                          └── the label, exact by construction
```

This also solves the **source-independence trap** (CLAUDE.md #3) better than real
loans do: we *control* the document path and the system path as separate
structures, so reconcile checks get genuinely independent inputs — instead of the
LOS-only collapse where doc-vs-system is trivially identical.

## The files

| File | What it does |
|---|---|
| `taxonomy.py` | Parses the **real** AMQ workbooks (`demo/rules/*.xlsx`), classifies **7,398 real defect conditions** into 8 generatable archetypes, maps each to an engine check-kind + expected verdict. → `taxonomy.json` |
| `generator.py` | Clean-loan builder (independent doc/system paths) + one mutation operator per archetype. Deterministic (seeded). → labeled loans |
| `test_properties.py` | (1) constructed-label scoring; (2) label-free **metamorphic invariants** (monotonicity, reconcile soundness, independent-Decimal self-consistency, confidence gate, generator determinism). |
| `eval.py` | Generates N loans, scores the engine, emits a report + artifact with per-archetype coverage. |

## What it proves (current results)

- **Taxonomy grounding:** 8 archetypes derived from real workbooks; 56.7% of
  defect conditions classified, **0 uncovered engine check-kinds** (the rest are
  residual phrasings of covered archetypes; SQL program-gating rows excluded).
- **Engine correctness at scale:** **40,000 / 40,000** checks exact-match vs
  by-construction labels on 5,000 loans; **0 false-auto-clears** (the
  catastrophic metric — engine never clears an injected defect).
- **Label-free invariants:** 7/7 property tests pass (`pytest test_properties.py`).
- **It catches its own bugs:** the scorer flagged an early generator bug (an SSN
  mutation that didn't actually change the normalized last-4) — i.e. it
  distinguishes *engine-correct* from *label-wrong*, which is the whole point.

```bash
python3 taxonomy.py                       # rebuild taxonomy.json
python3 -m pytest test_properties.py -q   # invariants
python3 eval.py 5000 --runtag=run1        # scored eval + artifact
```

## The honest residual (do not oversell)

This proves the engine is **correct given the data**. It does **not** prove:

1. **Real-world defect distribution.** We only catch failure modes we inject.
   *Mitigation:* archetypes are derived from the real 800+ check workbook, so
   coverage tracks the actual rule set — not our imagination.
2. **Extraction / OCR realism.** Generated values are clean; real Touchless
   output carries noise and confidence variance. *This is the one piece that
   still wants real files* — tracked as a separate gap, not silently folded in.
   (An OCR-noise layer is the natural next addition; the confidence gate is
   already tested.)
3. **Interpretation correctness.** That each mutation→verdict mapping matches the
   lender's intent needs **Kayla's sign-off on the mapping** — a rules review we
   *can* obtain, decoupled from the loan-file dependency.

**This is not "pretend synthetic is real."** It is: make synthetic's ground truth
trustworthy *by construction*, tie coverage to the real rule set, validate
interpretations against the spec, and label the distribution gap loudly.

## When real loans arrive

The harness is built to absorb them with **no rework**: real loans are just
another loan source feeding the same `score()` in `test_properties.py`. Swap the
source, keep the scorer; the synthetic eval becomes the regression floor and the
real loans become the distribution check (#3 above). That converts the accuracy
story from *directional* to *load-bearing* — see `p0/experiment_g3/RESULTS.md`.
