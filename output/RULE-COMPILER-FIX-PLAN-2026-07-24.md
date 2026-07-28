# Rule-Compiler Fix Plan — Conditional-Applicability Gating + Operator-Inversion Prevention

| | |
|---|---|
| **Date** | 2026-07-24 |
| **Status** | **Plan for review — no code changed, no spec opened yet.** |
| **Answers** | `output/SME-REVIEW-FINDINGS-2026-07-24.md`'s two open issues, using: (1) our own compiler's documented current approach (`docs/architecture/rule-compiler.md`), (2) a targeted architecture comparison against the sibling `examples/mortgage-qc` app, (3) external research (context7/Tavily/Exa/WebFetch) on precondition extraction, sign/direction-error prevention, and rules-engine applicability schemas. |
| **Governs** | Feeds a future spec-kit spec (numbering suggested below) — not a substitute for one. Per this project's spec-before-build convention, no implementation starts until that spec is written and reviewed. |

---

## 0. What grounds this plan

- **Our own compiler, documented for the first time**: `docs/architecture/rule-compiler.md` — the exact pipeline (classify → ground → compile → parse → program-gate → sign), and precisely which decisions are deterministic vs. LLM-made today. It has no conditional-applicability output field at all, and its `operator` convention is unstated in the prompt — the two root causes.
- **The sibling app, checked directly, not assumed**: `examples/mortgage-qc`'s `blocks/asset-verification.block.yaml` (the real gift-fund question, `O-FRD-15499`) confirmed it has the *same* gap, solved the *opposite*, non-adoptable way — a live LLM call re-derives "does this loan have a gift" fresh on every evaluation. Useful as confirmation the gap is real and non-trivial; not a source of a mechanism to borrow. Full comparison in `docs/architecture/rule-compiler.md` §6.
- **External research**, three independent tracks, converging findings summarized in each section below.

---

## 1. Fix: conditional-applicability gating (the systemic issue)

### 1.1 What the research confirms

Two independent research tracks (precondition-extraction literature, and rules-engine prior art)
converged on the same shape without being told to:

- **XACML** (OASIS access-control standard) separates every rule into **`Target`** (a boolean match
  that gates whether the rule is even in scope — no match → the standardized outcome
  **`NotApplicable`**, computed with zero further logic) from **`Condition`** (further refinement) and
  **`Effect`** (the actual decision). This is a name-for-name match to what we need: a gate, evaluated
  first, that resolves cleanly to `NOT_APPLICABLE` — a state our own `CheckResult` already has.
- **DMN** (the OMG business-rule/decision-table standard, implemented by Drools/Camunda) structures
  every rule row as **condition columns** (including a `-` cell meaning "this input doesn't apply to
  this rule") separate from **output/conclusion columns**. Condition-column = our proposed
  applicability gate; output-column = our existing `kind`/`operator`/`threshold` logic.
- By contrast, Drools DRL's `when`/`then`, OPA/Rego's `deny if {...}`, and `json-rules-engine`'s single
  `conditions` block all **conflate** applicability and pass/fail into one clause, with no distinct
  "not applicable" outcome. These are the patterns we're deliberately *not* copying — they'd reproduce
  the same blended-condition ambiguity that's the actual source of this gap in our own AMQ rows.
- Separately, **Drools' own idiom** for exactly this situation — "compile a gating condition into a
  named, inferred intermediate fact once, then have downstream rules match on that fact" (their
  canonical example: `IsAdult(age>=18)` inferred once, reused everywhere) — maps directly onto our
  existing field-catalog model: a loan-fact precondition like "gift funds were used" is just another
  **canonical field** (`gift_funds_used: boolean`), no new machinery required to *represent* it, only
  to *reference* it from a check.
- On the extraction side: **Policy-to-Tests (P2T)** and **De Jure** (both 2025-2026 LLM rule-extraction
  papers) already extract regulatory clauses into separate typed fields — `scope`/`conditions` distinct
  from `requirement` — each carrying its own source-span citation, judged for verbatim traceability
  before acceptance. This is the same discipline `compile_llm.py`'s existing `UNSPECIFIED`/never-invent
  rule already enforces for thresholds — we'd be extending a pattern we already trust, not adopting a
  new one.
- **Real failure-mode data** (arXiv:2607.03325, legal-clause extraction against expert ground truth):
  precision ~93%, recall 60–82% — **under-extraction, not hallucination, is the dominant error.**
  Translated to our case: the more likely failure is the compiler *missing* a real precondition (a
  check wrongly always-fires) rather than inventing one (a check wrongly always-skips). This directly
  determines the safe default (below).

### 1.2 Proposed design (for the eventual spec, not committed here)

**Schema**: add one new field to `Check` (`p0/qc_engine/ruleset.py`), mirroring the XACML/DMN shape and
reusing the exact same operator vocabulary the ratio-threshold kind already has, for consistency:

```python
applies_if: Optional[Dict[str, str]] = None
# e.g. {"field_name": "gift_funds_used", "operator": "==", "value": "true"}
# None = unconditional (today's universal behavior, unchanged) — the safe default.
```

**Engine**: one new deterministic step in `engine.py`, evaluated *before* the check's own `kind` logic
— read `loan.get(applies_if.field_name)`, compare against `value`, and resolve `NOT_APPLICABLE`
immediately (with an explicit, honest `review_reason` when the precondition field itself is absent —
same "ambiguous absence → human" discipline `003d` already established) if it doesn't hold. Zero LLM
involvement at runtime — this is a plain data comparison, identical in kind to every other deterministic
step already in this engine. No new evaluation *mechanism*, only a new evaluated field.

**Compiler**: extend `SYSTEM_PROMPT` to extract `applies_if` using the sequential technique the
extraction research recommends — first locate and quote verbatim any conditional-trigger clause in
`defect_text` ("if gift funds were used...", "for a condo transaction...") *before* extracting the
check's own pass/fail condition, rather than one flat pass that risks blending the two. Apply the same
`NEVER INVENT` discipline already governing thresholds: `applies_if` is set **only** when `defect_text`
itself states or clearly implies the precondition, with the precondition string traceable to a quoted
span — never inferred from `grounding_context` (the Selling Guide) and never from general model
knowledge. **This directly satisfies Kayla's hard constraint** from the SME call (domain knowledge may
interpret an existing condition, never originate one) — `applies_if` extraction is scoped to the row's
own text by the same rule that already governs thresholds, so the Selling Guide's role stays exactly
where she drew the line: none, for originating a new gate.

**Safe default, per the failure-mode data above**: when the compiler is uncertain whether a
precondition exists, `applies_if` stays `None` (unconditional — today's behavior). This trades a few
reviewable false-positive exceptions against the far worse failure of a check silently never firing —
the same asymmetry `compile_llm.py` already applies to `UNSPECIFIED` thresholds.

**Recall aid**: prompt the compiler with a closed checklist of the gating dimensions we already know
recur across the AMQ workbook (gift/grant funds used, property type = condo/co-op/PUD, VA/USDA/FHA-specific
scenarios, co-borrower present, self-employment income used, etc.) and ask it to check each explicitly
against `defect_text`, rather than open-ended "find a precondition if one exists" — closed-checklist
prompting measurably improved recall over open extraction in the cited legal-extraction studies.

**Field-catalog implication**: `applies_if.field_name` must resolve to a real canonical field the same
way `field_name`/`compare_field_name` already must (extend `catalog.py`'s `validate_referential_integrity`
the same way `003d` did). Some gating dimensions (gift funds used, property type) likely already exist
or are trivial catalog additions (`001a`); this plan does not audit that gap — the eventual spec should.

### 1.3 Explicitly out of scope for this fix

The unresolvable "Question ID"/ACES cross-reference column stays excluded, per the call — this design
does not attempt to decode it. This fix only extracts preconditions a row's **own** `defect_text`
already states or clearly implies — it does not build general-purpose dependency-graph inference across
rows.

---

## 2. Fix: operator-inversion prevention (the mechanical bug)

### 2.1 What the research confirms

- The failure class is **documented and named** in the LLM code-generation literature — "Conditional
  Misalignment Error" (~15.65% of all generation errors in one 2025 taxonomy, arXiv:2411.01414),
  attributed partly to training-data confusion around negation/inversion. Our finding (a FAIL-framed
  source sentence producing a non-inverted operator) is a consistent instance of this broader, evidenced
  weakness, not an anomaly specific to our prompt.
- **Roundtrip/back-translation consistency checking** (arXiv:2604.25031, "Faithful Autoformalization via
  Roundtrip Verification and Repair") is a close, validated analog: formalize NL → structured logic →
  back-translate → re-check semantic equivalence, raising accuracy from 45–61% to 83–85% on a comparable
  rules-extraction task. **We are structurally ahead of that paper's starting position**: `compile_row()`
  already generates `message_pass`/`message_fail` (natural language) in the **same call** as
  `operator`/`threshold` (structured) — no second LLM call is needed to get both sides of the
  consistency check; we already have both, we just aren't comparing them.

### 2.2 Proposed design (for the eventual spec, not committed here)

**(a) Prompt-level prevention** — cheapest, addresses the actual root cause: add an explicit rule to
`SYSTEM_PROMPT` stating the convention `engine.py` already relies on ("`operator`/`threshold` must
always express the condition under which the loan PASSES — invert the source text's comparison
direction when `defect_text` is phrased as a FAIL-trigger condition, e.g. 'if LTV exceeds 80%'
compiles to `operator: "<="`, not `">"`"), plus 2-3 few-shot examples specifically demonstrating the
inversion. This alone is expected to prevent most new instances.

**(b) Compile-time consistency gate** — the higher-value, permanent fix: formalize the heuristic scan
that already found 45/495 suspects (`output/operator_inversion_suspects_2026-07-24.json`) into a
mandatory, automatic validation step that runs on every compiled batch, comparing the structured
`operator`/`threshold` against the LLM's own `message_pass`/`message_fail` text for the same check. Any
check that fails this consistency check is **held out of auto-sign** and routed to the SME exception
queue (the same pattern `002c`'s spec already establishes for its judge-panel disagreements) — never
silently signed. This needs no new LLM call (unlike the roundtrip paper's design) since both sides
already exist from the same compile call — it's a deterministic post-check, cheap to run on every batch
forever, not a one-time scan.

**(c) Lower-priority supporting technique, worth naming**: boundary-value probing — synthetically
evaluate each compiled `ratio_threshold` check at `threshold−ε`/`threshold`/`threshold+ε` and confirm
the result direction matches the stated NL intent. This overlaps with what `005`'s eventual eval-CI-gate
is already meant to do generically; likely belongs there rather than as bespoke compiler logic.

### 2.3 Immediate housekeeping this implies (not decided here, just named)

Once (b) exists and is re-run against the current `post_closing_only_ruleset.json`, the 45 suspect
checks need SME review before re-signing, and `LOAN-01-QC-RESULT-WITH-PROVENANCE-2026-07-24.pdf` /
`loan01_with_provenance.json` need regenerating so the 2 confirmed false positives no longer read as
real defects — already flagged in `output/SME-REVIEW-FINDINGS-2026-07-24.md` §4.

---

## 3. Sequencing recommendation

The operator-inversion fix (§2) is small, well-scoped, low-risk, and already blocking correction of a
shipped artifact — it could reasonably move first and fast. The conditional-applicability fix (§1) is a
real schema change touching `Check`, `engine.py`, `catalog.py`, and the compiler prompt — comparable in
size to `003d` (doc-vs-doc), and should get the same spec-kit treatment (spec → plan → tasks → criteria)
before any code is written, consistent with how every other engine-schema change in this project has
been handled. Suggested spec numbering, both siblings of the existing `002b`/`002c` compiler-family
specs (not committed — the architect should confirm on formal specing):

- **`002d-operator-consistency-gate`** — §2, small.
- **`002e-conditional-applicability-gating`** — §1, larger; depends on `001a` (field-catalog additions)
  and `002b` (existing compiler), same as `002c` did.

---

## 4. What this plan does not decide

No code has been changed. No spec has been opened. This is the research + design synthesis the prior
"agree on the problem space first" consensus called for, now extended to a concrete, externally-grounded
fix shape for both issues — the next step is your review, then (if it holds up) formal spec-kit specs
before implementation begins.
