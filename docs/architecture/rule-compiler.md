# Architecture: LLM Rule-Compilation Pipeline

| | |
|---|---|
| **Date** | 2026-07-24 |
| **Covers** | `p0/eval_synth/taxonomy.py` (classify) → `p0/qc_engine/compiler/compile_llm.py` (compile) → `p0/qc_engine/ruleset.py` (assemble/sign) |
| **Why this exists** | This pipeline is the load-bearing "compile, then run" mechanism the whole product's determinism claim rests on (`CLAUDE.md` Non-Negotiable #1), but it had no single documentation artifact describing how it actually works — only scattered spec-kit docs (`specs/002a/002b/002c`) and the code itself. Written directly from the current code, not from memory or the specs (specs describe intent; this describes what runs). |
| **Companion** | `output/SME-REVIEW-FINDINGS-2026-07-24.md` — the two open issues this pipeline currently has, which this doc's "Known limitations" section explains at the architecture level. |

---

## 1. What this is, in one sentence

One real workbook row (a lender's AMQ post-closing QC question + defect condition) goes into **exactly
one LLM call** (Claude Sonnet, temperature=0) and comes out as a structured `Check` object — a
deterministic, engine-executable specification (field, comparison, threshold, messages) that an SME
signs off on **before** it ever evaluates a real loan. The LLM never runs again at evaluation time —
`p0/qc_engine/engine.py` evaluates the signed artifact with plain Decimal arithmetic, zero model calls.
This is Principle II ("compile, then run") made concrete.

---

## 2. The pipeline, stage by stage

```
AMQ workbook row (demo/rules/*.xlsx)
        │
        ▼
┌─────────────────────────────────────────────┐
│ 1. CLASSIFY (deterministic, no LLM)          │  p0/eval_synth/taxonomy.py :: classify()
│    defect_text → engine_kind                 │  regex/keyword classifier over defect_text
│    (predicate | ratio_threshold |            │  → one of 5 archetype buckets (MISSING,
│     agree_categorical | agree_numeric)       │  POLICY, THRESHOLD, INACCURATE, MISMATCH)
└─────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────┐
│ 2. GROUND (deterministic retrieval, no LLM)  │  compile_llm.py :: _load_signed_kb_for_program()
│    program (from Exception Code prefix)      │  + knowledge_base.py :: retrieve()
│    → signed, version-pinned KB corpus        │  in-memory keyword match against a pre-signed,
│    → top-3 sections as grounding_context     │  SME-reviewed corpus — NEVER a live web/agent
│                                               │  call at compile time (spec 002c FR-005/FR-006)
└─────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────┐
│ 3. COMPILE (the one LLM call)                │  compile_llm.py :: compile_row()
│    {question_text, defect_text, engine_kind, │  bedrock.converse(), Sonnet 4.6, temp=0,
│     significance, existing_catalog_fields,   │  maxTokens=700, one row per call — NOT
│     grounding_context} → structured JSON     │  native tool-use/function-calling; a prompted
│                                               │  JSON shape parsed via regex (_extract_json)
└─────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────┐
│ 4. PARSE + CLEAN (deterministic)             │  compile_row(): _extract_json, _clean_check_kwargs,
│    JSON → Check(**kwargs); malformed          │  Check(**check_kwargs) — dataclass field
│    proposed_field_entry degrades gracefully   │  validation is the only "schema enforcement"
│    (doesn't discard an otherwise-valid check) │  layer; a parse exception → parse_error,
│                                               │  excluded from assembly, never crashes the batch
└─────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────┐
│ 5. PROGRAM-GATE (deterministic, no LLM)      │  program_gating.py :: parse_exception_code_prefix,
│    row's own Exception Code prefix +          │  parse_sql_gating_clause — parsed directly from
│    (if present) SQL gating clause             │  the row's real text, same discipline as step 1;
│    → Applicability(program, sql_filters)      │  AMBIGUOUS sentinel for GSE-ambiguous rows
└─────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────┐
│ 6. ASSEMBLE + SIGN (batch, human-gated)      │  compile_llm.py :: assemble_ruleset()
│    drafts → Ruleset + RuleProvenance          │  SME reviews/corrects; edit-distance measured
│    (llm_draft vs signed_text) + intent record │  (sign-off-theater detection); SHA-256 identifies
│    (source_text, plain-English restatement)   │  the final signed artifact — THIS is what
│                                               │  engine.py runs, forever after, unchanged
└─────────────────────────────────────────────┘
```

**What is and isn't an LLM decision**, precisely — this is the detail most worth getting right, since
it's the crux of the "compile, then run" claim:

| Decision | Who makes it | Mechanism |
|---|---|---|
| Which check-kind family (predicate vs ratio_threshold vs agree_*) | **Deterministic** | `taxonomy.classify()`, regex/keyword over `defect_text` |
| doc-vs-system vs doc-vs-doc (within the `agree_*` family only) | **LLM** | Prompted decision rule in `SYSTEM_PROMPT`, using `expected_sources` as the load-bearing signal |
| The actual field(s), operator, threshold, tolerance, messages | **LLM** | Extracted from `defect_text` + `grounding_context`, single-shot |
| Which program(s) a check belongs to | **Deterministic** | `program_gating.py`, parsed from the row's own Exception Code / SQL clause text |
| What regulatory/guide context grounds the compile | **Deterministic retrieval** | Keyword match against a pre-signed KB; the LLM never searches live |
| Final sign-off | **Human (SME)** | `assemble_ruleset()`'s `corrections` dict; edit-distance measured |

---

## 3. The structured-output contract

`compile_row()` sends one JSON user message and expects one JSON object back (see `SYSTEM_PROMPT` in
full, `p0/qc_engine/compiler/compile_llm.py:51-209`). Key discipline already enforced in the prompt:

- **Never invent a number.** If `defect_text` implies a threshold exists but doesn't state it (and
  `grounding_context` doesn't supply it), the LLM must emit the literal string `"UNSPECIFIED"`, not a
  plausible-sounding guess — an honest gap beats a confident fabrication (hardened 2026-07-22 after a
  rule-fidelity audit found the model being too eager to invent values, and separately, too eager to
  mark things UNSPECIFIED when a value like "less than 2 yrs" was actually present in prose).
- **Grounding never originates content.** `grounding_context` may only interpret/cite what `defect_text`
  already says; it must never be the source of a threshold/condition the row itself doesn't state.
- **Kind-family is fixed upstream**, except within `agree_*`, where the LLM is trusted to pick
  doc-vs-system vs doc-vs-doc using `expected_sources` as evidence, defaulting to the existing/proven
  doc-vs-system path when genuinely ambiguous.

**What the contract does NOT yet cover** (see §5, below) is any notion of conditional applicability —
there is no output key for "only evaluate this if some other field has some other value." Every
compiled check is unconditional by construction today.

---

## 4. Verification posture today

- **No retry-on-parse-failure.** A malformed JSON response produces a `CompiledCheckDraft` with
  `parse_error` set and `check=None` — excluded from `assemble_ruleset()` silently (never crashes the
  batch), but also never retried.
- **No multi-model / judge-panel cross-check in this file.** Spec `002c` (`specs/002c-domain-knowledge-grounded-compilation/spec.md`,
  US5) describes a full 10-step intake workflow that includes a multi-model judge panel (2+ models,
  different family than the compiler, any disagreement escalates to SME review) — but that panel is
  **not present in `compile_llm.py` today**. What IS implemented and live is the grounding-retrieval
  half (step 2 above); the judge-panel half of `002c` remains specced, not built. Worth knowing before
  assuming the compiler already has a self-check step — it doesn't, beyond dataclass field validation.
- **Single-shot temperature=0 is the only reproducibility guarantee**, not a correctness guarantee —
  the G3 bake-off (`p0/experiment_g3/RESULTS.md`) already established that byte-identical-across-runs
  and factually-correct are separate properties; this pipeline inherits that same distinction.

---

## 5. Known limitations (as of 2026-07-24 — see `output/SME-REVIEW-FINDINGS-2026-07-24.md` for full detail)

1. **No conditional-applicability output.** The JSON contract above has no field for "this check only
   applies if `<precondition>`." Every compiled check runs unconditionally on every program-eligible
   loan; a loan-fact precondition (gift used, condo, co-borrower, etc.) that the source row's own text
   implies has nowhere to go in the compiled artifact today. This is the systemic gap surfaced on the
   2026-07-24 SME review call.
2. **`operator`'s PASS-condition convention is unstated in `SYSTEM_PROMPT`.** The engine evaluates
   `ok = value <operator> threshold; PASS iff ok`, but the prompt (`compile_llm.py:100`) just says
   `"operator": "<= | < | >= | > (ONLY if kind=ratio_threshold)"` with no explanation of which
   direction is expected. Where `defect_text` phrases a FAIL-trigger comparison ("if LTV **exceeds**
   80%..."), the model has transcribed that comparison word literally instead of inverting it — a
   confirmed defect (45/495 compiled `ratio_threshold` checks show the signature; 2 confirmed by manual
   SME review on loan 01).

Both are prompt/schema gaps in this same file, not engine bugs — `engine.py`'s evaluation logic for
both `ratio_threshold` and (once it exists) any applicability gate is straightforward and correct;
the compiler simply isn't yet telling the LLM the full contract it needs to fill in correctly.

---

## 6. Comparison: how the sibling `examples/mortgage-qc` app handles the same question

`examples/mortgage-qc` (Olav's original runtime-LLM POC, Gordon's own forked/extended build, live at
`mortgage-qc.loopinhuman.com`) is architecturally the opposite bet — no compile step at all. Its ~20
`blocks/*.block.yaml` files are **hand-authored**, not LLM-extracted from the workbook, and QC
evaluation happens via a **live Claude call per block at loan-review time** (`agent-gateway/src/agent_invoker.py`),
with the model given tool access to mock lending systems and told to reason over the full loan file —
already audited in `output/PRIOR-ART-OLAV-MORTGAGE-QC.md` as **not reusable** for our engine (it's the
literal architecture Principle I/II reject).

**But it's directly informative on the conditional-applicability question**, because it turns out to
have the *same* gap, solved the *opposite* way. Inspecting a real block
(`examples/mortgage-qc/blocks/asset-verification.block.yaml`, Q2, `O-FRD-15499` — "Were all gift
and/or grant fund requirements met?"): its `CRITERIA` field is **program-level only**
(`WHERE Loans.QC_Policy = 'Freddie Mac'`) — identical in kind to our own `program_gating.py`, nothing
more. There is no data-driven "does this loan actually have a gift" predicate anywhere in the YAML.
Instead, the block's own system prompt hands that decision to the LLM at runtime, verbatim:

> *"If a question's criteria field contains a SQL-like filter, evaluate whether the current loan
> matches that criteria... If the check does not apply to this loan type or scenario, select
> NOT_APPLICABLE."*

I.e. Olav's system never solved loan-fact conditional applicability as structured data either — it
papered over the exact gap we're now trying to close by asking a model to re-derive it, fresh, from
the whole loan file, on every single evaluation. That's workable for a live per-loan agent call; it's
precisely the non-determinism this project's compiled-engine bet exists to avoid (same loan, same
facts, must produce the same NOT_APPLICABLE verdict every time, auditable without re-running a model).

**The one useful, adoptable idea**: their schema treats `NOT_APPLICABLE` as a first-class response
value sitting alongside PASS/EXCEPTION for every question — not a fallback state discovered after the
fact. Our own `Check`/`CheckResult` model already has an equivalent `NOT_APPLICABLE` status, so this
confirms (rather than changes) the target resolution shape for a conditionally-gated check; it does
not supply the missing mechanism. **No architecture or code from this app is being adopted for the
gating fix** — its relevance here is confirmation of the problem shape, not a solution to borrow.
