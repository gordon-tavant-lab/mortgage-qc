# Mortgage QA/QC Engine — Architecture & Design Rationale

> Audience: a peer technical architect evaluating this system's design.
> Scope: the deterministic engine core (`p0/qc_engine/`) — not the extraction
> or LOS-connector layers, which are treated as upstream contracts, not builds.

---

## TL;DR

A closed loan file is QC'd by comparing three independent data sources
(closing documents, LOS export, MISMO XML) against 800+ lender-authored rules.
The system splits cleanly into two phases with a hard boundary between them:

- **Compile time** — an LLM interprets a human-authored rule (an AMQ workbook
  row) and drafts a structured, typed `Check`. A deterministic referential-
  integrity screen and a human SME sign-off gate every draft before it becomes
  live. The signed output is content-addressed (SHA-256).
- **Run time** — a pure function `f(signed_ruleset, loan) -> verdicts`. No
  network call, no model inference, no floating-point money math, no
  wall-clock. Same inputs, same hash in, same verdicts out, forever.

The interesting engineering decision isn't "use an LLM" or "don't" — it's
**where the non-determinism is allowed to live**, and proving that boundary
holds under audit. That's the rest of this document.

---

## 1. The problem shape

A funded loan comes back from the title company as hundreds of signed PDFs —
the source of truth. The lender's own systems (LOS, and often a MISMO 3.4
export of the same data) may or may not agree with what's actually on the
documents. QC today means a human manually cross-checking hundreds of data
points against hundreds of pages, per loan, at scale.

Two things make this a distinctive architecture problem rather than a
generic "LLM does QC" problem:

1. **It's a three-way reconciliation, not a single-source validation.** A
   check isn't "is this value valid" — it's "does the document (truth) agree
   with what the lender's system of record says." Two independent test data
   paths (document extraction vs. LOS/MISMO) have to stay genuinely
   independent, or the comparison is trivially self-confirming.
2. **It's regulator-facing.** If a lender can't reproduce and explain exactly
   why a loan cleared, they buy it back. "The model said so" is not an
   acceptable audit answer at any accuracy level — the requirement is
   *reproducible derivation*, not just a correct answer.

---

## 2. Architecture: compile, then run

```
                         COMPILE TIME (per rule, once)
 ┌──────────────┐   ┌────────────────┐   ┌───────────────────┐   ┌────────────┐
 │ AMQ workbook  │──▶│ LLM compile step│──▶│ Referential-       │──▶│ SME sign-  │
 │ row (defect   │   │ (Bedrock,       │   │ integrity screen   │   │ off gate   │
 │ text, human-  │   │ Sonnet 4.6,     │   │ (field must exist  │   │ (edit-     │
 │ authored)     │   │ temp=0)         │   │ in catalog, or be  │   │ distance   │
 │               │   │                 │   │ a signable new     │   │ measured)  │
 │               │   │ → CompiledCheck │   │ catalog proposal)  │   │            │
 │               │   │   Draft         │   │                    │   │            │
 └──────────────┘   └────────────────┘   └───────────────────┘   └─────┬──────┘
                                                                        │
                                                                        ▼
                                                        ┌───────────────────────────┐
                                                        │ Signed Ruleset             │
                                                        │ (SHA-256 over canonical    │
                                                        │  JSON; RuleProvenance +    │
                                                        │  RuleIntentRecord per rule)│
                                                        └─────────────┬─────────────┘
                                                                      │
                         RUN TIME (per loan, every run)               │
 ┌──────────────┐   ┌──────────────────┐   ┌──────────────────────┐  │
 │ CanonicalLoan │──▶│ engine.run(ruleset,│──▶│ CheckResult per rule │◀─┘
 │ (doc/truth +  │   │ loan) — pure       │   │ (audit-grade: inputs,│
 │  los/mismo    │   │ function, no I/O,  │   │  normalized values,  │
 │  system data) │   │ no float, no LLM   │   │  rounding, citation) │
 └──────────────┘   └──────────────────┘   └──────────────────────┘
```

### Compile time: where the LLM is allowed to be uncertain

`compiler/compile_llm.py` sends one Bedrock call per AMQ row — the lender's
own defect-text description of a rule — and gets back a `CompiledCheckDraft`:
a structured `Check` (one of four kinds: `predicate`, `ratio_threshold`,
`agree_categorical`, `agree_numeric`) plus a `plain_english_restatement` —
the LLM's own account of what it thinks the rule means, **retained
permanently** as part of the audit trail, not discarded after compilation.

Before a draft is signable, `catalog_screen.py` runs the same referential-
integrity validator the engine itself will later trust, one draft at a time,
so a batch of dozens of compiled rules gets per-draft PASS/BLOCKED reporting
instead of the whole batch dying on the first bad row. A malformed proposed
catalog field degrades that one draft to "blocked," it doesn't discard an
otherwise-valid compiled check — a failure mode this caught in a real 30-row
production batch (3 valid checks would have been silently lost under a
naive implementation).

**The sign-off gate is not theater by construction.** `RuleProvenance`
computes a Levenshtein edit-distance between what the LLM drafted and what
the SME actually signed. A ruleset where every edit distance is 0 is a visible
red flag in `signoff_summary()` — evidence the human rubber-stamped rather
than reviewed. This was a specific design correction from an internal review:
"compile once, SME signs off" only means something if you can prove signing
happened, not just that a click occurred.

### The signed artifact

`Ruleset.sha256()` hashes the canonical, sorted JSON of `{ruleset_id,
version, engine_version, checks}` — the LLM draft text and provenance are
*not* part of the hash (they're audit context, not executable content). The
runtime loads a ruleset **by hash**. Given the hash, the exact rules that
judged any loan are forever recoverable, and two rulesets with the same hash
are provably identical rule-for-rule.

### Run time: the determinism proof

`engine.run()` is deliberately boring: `[_eval_check(loan, c) for c in
ruleset.checks]`. Every check kind is a closed-form comparison against typed,
pre-extracted fields — nothing here calls out, retries, or branches on
anything but the data in front of it. Two properties make the determinism
claim provable rather than asserted:

- **No floats touch a money/ratio decision.** `money.py` converts everything
  to `Decimal` via string representation (never through a float literal, to
  avoid inheriting binary-float noise), pins `ROUND_HALF_EVEN` explicitly
  rather than relying on a platform default, and quantizes to a fixed,
  documented scale per value class (cents, rate-percent, ratio-percent).
  LTV/DTI boundary checks are exactly where float drift would silently flip
  a pass/fail — this is the mechanism, not just a policy statement.
- **Reconciliation logic is signed data, not code.** Which normalizer applies
  to which field, and what tolerance is acceptable, lives in the signed
  ruleset (`reconcile.py`'s `NORMALIZERS` map is a fixed, version-pinned
  *interpreter* of named transforms — `norm_name`, `norm_address`, etc. — not
  a place where per-field judgment gets hand-coded outside the audit trail).
  This was also a direct response to internal review: judgment-heavy logic
  living in unaudited Python, rather than in the signed artifact, would have
  quietly broken the "SME owns the judgment" story.

One more determinism-adjacent gate worth calling out: **auto-clear is
confidence-gated**, not verdict-gated. A `PASS` that depended on a
low-confidence document extraction is downgraded to `NEEDS_REVIEW` rather
than auto-cleared — a confident-but-wrong OCR read is the dominant residual
risk once the engine itself is provably correct, so the system routes around
it rather than assuming extraction accuracy.

---

## 3. Architecture decision: compile-then-run vs. runtime LLM

This is the load-bearing decision in the system, so it's worth walking
through as an ADR rather than a stated conclusion — including the part where
the evidence didn't say what we expected going in.

**Context.** The alternative to compiling is simpler to build: run a
governed LLM against the loan at evaluation time, every time. The original
case against that (documented in the project thesis) rested on two claims:
(a) LLM output varies run to run, which is unauditable, and (b) per-run
inference at scale (~10,000 loans) would cost roughly $10K/run.

**What we did before committing:** a pre-registered bake-off (`p0/experiment_g3/`)
— the decision rule (D1 determinism, D2 accuracy/safety, D3 cost) was locked
*before* running it, specifically so the result couldn't be rationalized
after the fact.

**What the evidence actually said (2026-06-28, `RESULTS.md`):**

| Axis | Compiled engine | Runtime LLM — Haiku 4.5 | Runtime LLM — Sonnet 4.6 |
|---|---|---|---|
| Determinism (temp=0, N=5 runs × 6 loans) | bit-exact | identical every run | identical every run |
| Accuracy (26 checks) | 26/26, 0 false-clears | 19/26, **1 false auto-clear** | 25/26, 0 false-clears |
| Cost @ 10k loans | $0.00 | ~$27 | ~$70 |

Two of the three original arguments turned out to be **wrong**, not just
weak:
- **"The LLM varies" — false at temp=0.** Both models were byte-identical
  across every run on every loan. The reflexive non-determinism argument did
  not hold at this scale, for either model.
- **"$10K/run" — off by 150–400×.** Real Bedrock token usage on the same
  synthetic payloads put the expensive model at ~$70 per 10,000-loan run, not
  $10,000. Cost does not favor compiling by an order of magnitude — it favors
  it by a rounding error (engine is $0, but the delta is trivial, not decisive).

**What actually decided it: accuracy was model-dependent, and that's
disqualifying on its own.** Haiku 4.5 reproducibly (not randomly — the *same
wrong answer* every time) cleared a loan at 98.0% LTV against a 95% program
max — a buyback-grade error, and one that would pass a "run it twice, get the
same number" audit while still being catastrophically wrong. Sonnet 4.6
caught the same loan. So the catastrophic failure mode was a *small-model*
artifact, not an intrinsic property of running an LLM at runtime — but you
cannot know in advance, on a given real loan, which regime you're in, and you
cannot hand a regulator "trust me, we used the good model."

**Decision (kept, rationale revised):** compile-then-run stays the default —
but the honest justification is **auditability + guaranteed correctness on
the arithmetic**, not variance or cost. A capable runtime model *can* be
reproducible and *can* get the boundary math right; the compiled engine
*guarantees* both, and shows the Decimal derivation an auditor can re-check
by hand. That's a property no runtime model offers regardless of how accurate
it turns out to be.

**Open risk, stated plainly:** this bake-off ran on six hand-authored
synthetic loans — decisive for proving determinism (one non-identical run
would have killed the compile thesis outright) but explicitly *not* a
population accuracy claim. The real test is the same bake-off re-run against
expert-labeled, independently-sourced real loans. If a capable model turns
out to be accurate enough on real loans, the compile-vs-runtime choice
becomes a *governance preference*, not a *correctness necessity* — worth
knowing honestly rather than assuming away.

---

## 4. External validation: what the published literature says

The G3 bake-off (§3) is an internal, six-loan experiment. A broader literature sweep
(`output/RULE-COMPILATION-RESEARCH.md` — 108 agents, 25 primary sources fetched,
110 claims extracted, adversarially 3-vote-verified) checked whether that internal
result generalizes, and surfaced one verification technique the pipeline doesn't
have yet.

**Two independent 2025 benchmarks confirm the same failure shape G3 found
internally.** RuleArena (ACL 2025, peer-reviewed — airline-fee, NBA-transaction, and
tax-regulation rules, not toy logic problems) finds state-of-the-art LLMs fail via
two separable modes: misselecting the applicable rule among similar-but-distinct
regulations, and computing incorrectly even *after* correctly selecting the right
one. A legal-text-to-DMN decision-model generation study found LLM-compiled models
matched gold standards only **51–53%** of the time even under best-of-5 sampling,
with full outcome equivalence in just 33% of models. Both land on the same
structural finding the G3 bake-off found with Haiku's 98%-LTV false-clear: LLM
rule-compilation is not reliably correct, and its errors take a small number of
well-documented shapes — which is exactly why this architecture keeps the LLM at
compile time (drafting, under a screen and a human sign-off) and never at runtime
(arithmetic).

**An unrelated domain independently confirms the cost argument.** A 2026
healthcare-coding study (Portland State + Optum AI) found an
LLM-compiled-rules-plus-deterministic-engine architecture processed 11,000 CPT
billing codes for ≈$22, versus $4,840–$38,720 for LLM-at-runtime approaches on the
same volume — **200×–1,700× cheaper**. Different domain, identical architecture
shape, same order-of-magnitude conclusion as G3's own cost finding — two unrelated
measurements agreeing is stronger evidence than either alone.

**The literature validates the human-sign-off gate as load-bearing, not
ceremonial.** A foundational 1992 survey (Preece, Shinghal & Batarekh, *Knowledge
Engineering Review*) establishes that automated anomaly detection in a rule base is
*diagnostic, not dispositive* — a flagged issue is evidence of a likely error, never
proof of one (some flagged redundancy is intentional). That is precisely why
`catalog_screen.py`'s referential-integrity screen feeds a **required** SME sign-off
(`RuleProvenance`, edit-distance measured) rather than auto-approving a clean screen
result.

**The one real gap: the screen catches structural errors, not logical ones.**
Referential integrity confirms every field a compiled check references actually
exists in the catalog. It cannot catch two checks that can never both pass (a
genuine logical conflict) or a check whose guard condition can never be satisfied (a
dead, unreachable rule). Formal model-checking is an established, tractable
technique for exactly this class of error: model the rule base as a finite-state
transition system, express "confliction" and "unreachability" as CTL formulas, and
check automatically via a model checker (e.g., UPPAAL) — with total state space
**provably polynomial** (O(m²) for m rules), not the exponential blow-up earlier
verification approaches suffered from. At the scale this pipeline compiles at
(hundreds of checks, not millions), this is computationally cheap and currently
absent from `catalog_screen.py`.

**Two smaller, concrete additions worth making:**
- **Prompt-stability testing.** Neural semantic-parsing approaches are documented
  to be fragile to small input perturbation — a single word or comma change in the
  source text can flip the extracted structure. Re-compiling the same (or a
  near-duplicate) AMQ row and diffing the resulting `Check` spec is a cheap,
  testable addition to the sign-off review, not a one-shot compile-and-trust step.
- **Unify the hash and the sign-off.** The signed ruleset's SHA-256 hash and its
  SME sign-off provenance are currently related-but-separate artifacts. A 2026
  audit-trail pattern (technical provenance + governance approval merged into one
  chronological, tamper-evident ledger) argues for formalizing them into a single
  ledger entry per ruleset version, rather than two records a reader has to
  correlate by hand.

What did *not* survive adversarial verification and should not be treated as
established: a specific "73.5% attribute-omission" LLM failure-mode breakdown, a
"37–54% structural-similarity improvement" from a specific prompting technique, and
the claim that model-checking is the "de facto dominant" rule-verification technique
industry-wide. The full source list, confirmed/refuted claim ledger, and open
questions live in `output/RULE-COMPILATION-RESEARCH.md`.

## 5. Data model: keeping DOC and SYSTEM genuinely independent

`SourceValue` holds `truth` (the document/closing-file side — always the
title company's PDFs, extracted upstream) and a named `sources` map (`los`,
`mismo`, extensible to more without a code change). `system_value()` resolves
through a configurable `source_priority` (default: LOS, else MISMO) —
deliberately **not** an LOS-vs-MISMO comparison, because both are the same
lender data in different file formats; comparing a system against its own
re-serialization proves nothing. The actual comparison is always DOC (truth)
vs. resolved SYSTEM value.

This matters architecturally because it's easy to accidentally build test
fixtures where the "independent" system-side source is just a re-export of
the document data — at which point every reconciliation check trivially
passes and the three-source design stops being tested at all. The data model
enforces the distinction at the type level (`truth` vs. `sources`), but
maintaining genuine independence in test data is an ongoing discipline, not a
one-time fix.

---

## 6. What's actually built vs. what this describes in aspiration

Delivered, on `main`, each shipped as a TDD spec → plan → tasks → zero-
regression commit (5 specs so far):

| Spec | What it added |
|---|---|
| `001a` field-catalog | The typed field catalog + referential-integrity validator |
| `001b` source-envelope | The `truth`/`sources` generalized N-source data model |
| `002b` ruleset-compiler | The LLM compile step, catalog screen, sign-off provenance |
| `003a` predicate checks | `is_true` / `is_present` check kind |
| `003b` ratio-threshold checks | LTV/DTI/field-floor-ceiling check kind, the Decimal math path |

Not yet built (explicitly out of scope per the project's non-negotiables,
not an oversight): document extraction (upstream Touchless contract) and LOS
integration (existing connector, reused not rebuilt). `agree_categorical` /
`agree_numeric` (the reconciliation-phase checks) exist in the schema and
`engine.py`, exercised by the money/reconcile primitives above; the compiler
pipeline for authoring them at scale from the AMQ workbook is the same
`002b` pipeline already shipped.

---

## 7. The one-sentence version for a peer architect

Push all interpretive uncertainty (what does this rule mean, does the data
model support it) into a compile step that is slow, reviewed, and signed;
leave zero interpretive uncertainty in the run step that executes 10,000
times per batch. The interesting part isn't banning the LLM — it's proving,
with a pre-registered experiment rather than an assumption, exactly which
claims about "why compile" were true and which weren't.
