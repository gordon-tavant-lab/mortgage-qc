# Compiling Natural-Language Rules into a Deterministic Engine — Research Findings

> Deep-research pass (108 agents, 25 primary sources fetched, 110 claims extracted,
> adversarially 3-vote-verified — 17 confirmed / 8 refuted). Question: what does the
> academic/industry literature say is the scientifically grounded approach to parsing
> human-authored business rules into a deterministic rules engine, and where does
> `p0/qc_engine`'s existing compile-then-run design sit relative to it?

---

## Headline

**The literature validates the architecture, doesn't replace it, and points at one
real gap.** Two independent 2025–2026 benchmarks show LLM-compiled rules hit only
~50–53% outcome-equivalence against gold standards, via two separable failure modes
(wrong rule selected; right rule, wrong math) — which is exactly the risk profile
`compile_llm.py` → SME sign-off → pure-function `engine.py` is built to contain. The
older formal-grammar alternative (Controlled Natural Language → SBVR) is a real,
established lineage, not a strawman — but no evidence surfaced that it's *more
accurate* than LLM-based compilation, just differently-shaped (less flexible
authoring, more built-in formal guarantee). Where the codebase is genuinely
under-built relative to the literature: **the referential-integrity screen catches
structural errors, not logical ones** — a rule base can be internally
self-referentially valid and still contain two checks that can never both pass, or a
check whose guard can never be satisfied. Formal model-checking for exactly this
(CTL-based confliction/unreachability detection, provably polynomial in rule count)
is an established, tractable technique this pipeline doesn't yet have.

---

## 1. LLM rule-compilation accuracy: the evidence is not flattering, and that's the point

Two methodologically independent studies converge on the same structural finding:

- **Legal→DMN decision-model generation** (arXiv 2604.17153): even under the best
  input condition and best-of-5 sampling, LLM-generated executable decision models
  matched gold-standard test scenarios only **51–53%** of the time on average, with
  full outcome equivalence in just **33%** of generated models.
- **RuleArena** (ACL 2025, peer-reviewed — airline-fee, NBA-transaction, and tax
  rules, not toy logic puzzles): state-of-the-art LLMs "perform poorly" overall, and
  fail via **two separable modes**: (1) misselecting the applicable rule among
  similar-but-distinct regulations, and (2) computing incorrectly even *after*
  correctly identifying the right rule.

**Why this matters for `p0/qc_engine`:** these are exactly the two failure modes the
existing design already defends against structurally, not incidentally.
`compile_llm.py` never lets the LLM's draft go live without passing the
referential-integrity screen (`catalog_screen.py`) and a human SME sign-off
(`RuleProvenance`, edit-distance measured) — a defense against failure mode (1).
`engine.py` never lets the LLM touch arithmetic at runtime — Decimal-only,
pure-function evaluation — a defense against failure mode (2). The literature
independently confirms both failure modes are real and current (2025 benchmarks,
not stale priors); the architecture already routes around both. This is the
strongest finding of the pass: **the design isn't a hedge against a hypothetical
risk, it's a direct response to a measured one.**

A related, weaker-but-real finding: augmenting an LLM with an *external deterministic
tool* for math (rather than having it compute in-context) produces a real accuracy
improvement (RuleArena, confirmed 3-0) — the same underlying fact THESIS.md's
"compile, then run" pattern already exploits, though the paper itself doesn't claim
to be validating architectures like this one (that inference is ours, not theirs —
flagged during verification and excluded from the strong-claim set).

## 2. Controlled Natural Language: the pre-LLM alternative, not a superior one

**RuleCNL** (arXiv 1406.2096) is the closest pre-LLM analog to the compile step:
a purpose-built grammar (EBNF, actual parser — no statistical component) that maps
rule statements deterministically into **SBVR**, the OMG standard grounded in
first-order-logic-style formal semantics. This is the "fully-formal-grammar" branch
of the lineage — Attempto Controlled English is the other well-known member of this
family.

The trade-off is real and worth stating plainly: CNL buys a **formal semantic
guarantee at parse time** — if the text is grammatical CNL, the mapping to logic is
provably correct, no accuracy benchmark needed. What it costs is **authoring
flexibility** — an SME must write in the constrained grammar, not their own AMQ
defect-text prose. No source in this research pass showed CNL beating LLM-based
compilation on accuracy for genuinely free-text input; it's a different point on the
flexibility/guarantee curve, not a demonstrated winner. Given `p0/qc_engine`'s
input is real lender AMQ workbook rows (existing, unconstrained prose, hundreds of
them, not authored fresh in a constrained grammar), the LLM-compile approach is the
practically available one — CNL would require re-authoring the source rules, not
just re-architecting the compiler.

One caution that *does* transfer from the broader NLP literature: neural
semantic-parsing approaches (Semantic Role Labeling included) are documented to be
**fragile to small input perturbation** — a single word or comma change can flip the
extracted structure (arXiv 2309.13272, confirmed 3-0, consistent with the broader
adversarial-NLP literature: Jia & Liang 2017, Ribeiro et al. 2020 CheckList). This
argues for a concrete, cheap addition to the compile pipeline's own validation: **run
the same or near-duplicate rule text through the compiler twice and diff the
resulting `Check` spec** as part of the sign-off review, not just a one-shot compile.

## 3. Cost economics: independently corroborated, by an unrelated domain

A 2026 healthcare-coding analog (arXiv 2601.01266, AAAI preprint, Portland State +
Optum AI) found an LLM-compiled-symbolic-rules-plus-deterministic-engine
architecture processed 11,000 CPT codes for **~$22**, versus **$4,840–$38,720** for
various LLM-at-runtime approaches on the same volume — roughly **200×–1,700×
cheaper**. Different domain (healthcare, not mortgage), but architecturally
identical to `p0/qc_engine`'s pattern (LLM drafts symbolic rules once; a
deterministic engine executes without further LLM calls), and it independently
confirms the order-of-magnitude direction of `THESIS.md`'s own cost argument (and of
the G3 bake-off's ~$700–$3,500/run LLM-at-runtime estimate on real payloads vs. $0
for the engine) from a completely unrelated dataset. Two unrelated empirical
measurements landing on the same order-of-magnitude conclusion is meaningfully more
convincing than either alone.

## 4. Verification depth: the one real gap

This is the most actionable finding. Two things are true simultaneously:

- **The existing referential-integrity screen is necessary but was never claimed to
  be sufficient.** A foundational, highly-cited 1992 survey (Preece, Shinghal &
  Batarekh, *Knowledge Engineering Review*) establishes a stable methodological
  point that still holds: automated anomaly detection is *diagnostic, not
  dispositive* — a flagged issue is "highly indicative of an error" but not proof of
  one (some flagged redundancy is intentional). This validates the codebase's
  existing choice to pair an automated screen with **mandatory** SME sign-off rather
  than auto-approving on a clean screen result.
- **But the screen only catches structural errors — undefined field references —
  not logical ones.** A rule base can pass referential integrity perfectly and still
  contain two checks that can never both pass (a genuine logical conflict) or a
  check whose guard condition can never be satisfied (a dead, unreachable rule).
  **Formal model-checking is an established, tractable technique for exactly this**
  (arXiv 1404.2768): model the rule base as a finite-state transition system,
  express "confliction" and "unreachability" as CTL formulas, check automatically
  via a model checker (e.g., UPPAAL) — with total state space **provably polynomial**
  (O(m²) for m rules), not the exponential blow-up earlier verification approaches
  suffered from. At the scale this pipeline compiles at (hundreds of checks, not
  millions), this is computationally cheap and currently absent.

**Concrete recommendation:** add a conflict/unreachability check as a second
compile-time gate, after the referential-integrity screen and before SME sign-off —
same "diagnostic signal a human confirms" pattern already in place, just extended to
catch logical contradictions the current screen structurally cannot see.

## 5. Architectural pattern worth adopting: unify the hash and the sign-off

A January 2026 audit-trail paper (Brown University, arXiv 2601.20727) proposes
linking technical provenance (models, data, deployments, monitoring) with governance
records (approvals, attestations) into **one chronological, tamper-evident ledger**,
so an organization can reconstruct what changed, when, and who authorized it, from a
single artifact. The paper's own subject is LLM accountability broadly, not rules
engines — so this is a reasonable architectural analogy, not a literature claim
specifically about this codebase. But it's a good one: `p0/qc_engine` currently
produces the SHA-256-hashed ruleset and the SME sign-off (`RuleProvenance`,
edit-distance) as related-but-separate artifacts. Formalizing them into a single
append-only, tamper-evident ledger entry per ruleset version — rather than "the hash
proves the content, the provenance record proves the review, trust that they're
talking about the same version" — is a small, concrete hardening a regulator-facing
system should consider.

---

## What did NOT survive verification (excluded from findings above — do not cite)

Adversarial verification (3-vote, need 2/3 refutes to kill) rejected 8 of 25
top-priority claims. Notably:

- A specific "**37–54% structural-similarity improvement** from interface-constraint
  prompting" — refuted 1-2. Don't use this as a specific prompt-design lever.
- A "**73.5% attribute-omission**" LLM failure-mode breakdown — refuted 0-3. The
  general finding (LLM rule-compilation fails in structured ways) stands; this
  specific percentage does not.
- A four-anomaly taxonomy (redundancy/ambivalence/circularity/deficiency) claimed to
  be "the basis of RETE-based BRMS tooling" — refuted 1-2 on the causal linkage,
  though the taxonomy itself is real.
- "Model checking is the **de facto dominant** verification technique across 46
  studies, 1981–2018" — refuted 0-3. Don't overstate model-checking's industry
  adoption; treat it as an available, tractable technique, not an established
  default.

## Open questions this pass did not resolve

- Whether RETE and its successors (RETE-NT, TREAT, LEAPS) remain the state-of-the-art
  *execution* strategy for production rule engines in 2025–2026 — relevant to
  whether `engine.py`'s flat `[eval_check(c) for c in ruleset.checks]` loop should
  ever evolve toward incremental/indexed matching as check count grows into the
  thousands. Not confirmed either way; would need a dedicated follow-up.
- How DMN and RuleML's decision-table semantics compare directly to the `Check`
  spec's JSON schema — worth a targeted comparison if the team wants to benchmark
  the schema against an established notation rather than continue evolving it
  ad hoc.
- Whether SMT/constraint-solver verification (distinct from CTL model-checking) has
  been applied to business-rule engines specifically — unexplored in this pass.
- **What this codebase's own LLM compile step actually gets wrong** — omitted
  fields, hallucinated field names, misassigned check `kind` — is not answered by
  external literature and shouldn't be assumed from the healthcare-domain
  73.5%-omission figure (which was refuted). This is a question for `p0/qc_engine`'s
  own eval harness, not further web research.

---

## Bottom line for the team

Don't second-guess compile-then-run — two independent 2025 benchmarks just
confirmed the failure modes it was built to contain, and an unrelated domain just
confirmed the cost argument by 2–3 orders of magnitude. Do add a model-checking
pass (conflict + unreachability detection) to the compile gate — it's cheap,
established, and catches a class of error the current referential-integrity screen
structurally cannot see. And treat prompt-stability (same rule text twice → same
compiled `Check`) as a testable property worth adding to the compile pipeline's own
validation, not just an assumption.

**Sources (primary, verified by direct fetch):** RuleCNL (arXiv 1406.2096) ·
Legal-DMN generation (arXiv 2604.17153) · RuleArena, ACL 2025
(aclanthology.org/2025.acl-long.27) · SRL fragility (arXiv 2309.13272) · CPT-coding
cost analog (arXiv 2601.01266) · UPPAAL/CTL model-checking (arXiv 1404.2768) ·
Preece, Shinghal & Batarekh 1992 (Cambridge, *Knowledge Engineering Review*) ·
Audit-trail ledger pattern (arXiv 2601.20727).
