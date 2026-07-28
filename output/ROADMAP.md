# Mortgage QA/QC Tool — Product Roadmap (Feature Arc)

| | |
|---|---|
| **Version** | 0.6 |
| **Date** | 2026-07-02 |
| **Author** | Product Manager |
| **Status** | DRAFT — feature arc, dependency-ordered, spec-ready |
| **Governs** | `.specify/memory/constitution.md` (v1.1.0). Inputs: `output/THESIS.md`, `output/PRD.md`, `output/AUTHORING-UX-DECISION.md`, `p0/`. |

> **Changelog v0.5 → v0.6** (metacognition pass — scenario-generation gap found, not invented):
> - **Amended 005's scope**: found, by reading the actual code rather than trusting the roadmap's own
>   framing, that `p0/eval_synth/generator.py`'s mutation operators are hand-written against 7 specific
>   demo fields (`mut_mismatch_categorical` hardcodes `property_address`, `mut_unsigned` hardcodes
>   `note_signed`, etc.) — there is no generic mechanism to synthesize a labeled test scenario for an
>   *arbitrary* compiled `Check` the way `002b` will produce hundreds of. The fix already exists as
>   unpromoted throwaway code: `p0/experiment_002a/score_drafts.py`'s `_score_predicate`/
>   `_score_ratio_threshold`/`_score_agree_categorical`/`_score_agree_numeric` construct a synthetic
>   pass/fail case **generically, from a `Check`'s `kind` and `field_name`** — proven at n=24 during
>   `002a`, never promoted into the reusable foundation. **005's scope now explicitly includes
>   generalizing scenario construction to any compiled check** (not just productionizing the scoring
>   of hand-written ones) — see the amended entry below. Not spun out as a new feature number:
>   consistent with this roadmap's own discipline against proliferation (see `013`'s demotion below) —
>   005 already owns "eval keeps pace with the engine slices," and this is that same mandate, made
>   explicit rather than left implicit until someone specs 005 and misses it.

> **Changelog v0.4 → v0.5** (authoring-UX decision — see `output/AUTHORING-UX-DECISION.md`):
> - **Split 009 into 009a/009b/009c** because "authoring" is four tasks with opposite UX needs and risk profiles, not one workbench:
>   - **009a-import-and-diff-sign** — the **MVP authoring experience**: import the AMQ workbook (the SME's existing structured source), review the compiled artifact in a **diff-and-sign surface** (the real centerpiece), sign with measured edit-distance. No free-text needed for the pilot.
>   - **009b-guided-structured-editor** — catalog-constrained UI for net-new/edits; **owns the criteria gate so NL never does**.
>   - **009c-nl-drafting-assistant (v2)** — NL drafts *into* the guided UI at config time; **conditional on 002a** proving interpretation fidelity. If 002a fails, 009c does not ship.
> - **Resolved "no YAML for non-technical users":** the SME never touches YAML — import (their spreadsheet) + guided UI + (v2) NL. YAML is an internal artifact, not the authoring surface.
> - **Reframed the runtime-LLM block** (the `temperature:0.1` agent in the example): it is *authored data* compiled once into a signed ruleset (Principle II), not a runtime evaluator. The agent disappears.
> - **Phased the G4 tension:** MVP (009a/009b) is customer-facing but Tavant-shaped (import + guided, no DSL) — needs only the cheap, reversible half of G4. The expensive full customer-authored model is deferred to 009c. **G4 must lock before 009c, not before 009a** — this unblocks MVP authoring.
> - **Added Tension 8 (NL-on-the-gate):** NL may *propose* the criteria gate into a structured control, never *be* it — the gate is the one field a non-technical SME can't fluently read = the sign-off-theater hole.

> **Changelog v0.3 → v0.4** (adversarial review — metacognition / judge / contrarian):
> - **Fixed the dependency knot (RED):** 002a (the first spec a builder picks up) no longer "depends on feature 005." It depends on the **already-built foundation** `p0/eval_synth` scorer. Feature 005 is the *productionized CI gate* — a later, different thing. Numbering now matches the real dependency order (constitution: "NNN- encodes dependency order").
> - **Tightened 002a's success metric (RED):** the spike previously tested only whether the LLM emits a *runnable* rule. The real compile risk is *interpretation* fidelity — did the LLM read AMQ row #347 the way the lender means it? (eval_synth's "Question 2"). 002a now requires an SME rules-review component in its go/no-go, not just constructed-label runnability.
> - **Added 004-loan-disposition (composition gap, contrarian):** "compose all verdicts on one loan into one auto-clear/exception disposition" was homeless — smeared across 006/007/008. Now an explicit feature, slotting into the previously-empty `004`. This is the loan-centric integration the archetype slices don't cover.
> - **Split overloaded features (AMBER):** 001 → **001a** (field catalog + typed envelope, what the engine needs) and **001b** (source-agnostic N-source generalization + inbound contracts, the scaling bet). 010 → **010a** (honor the 615 existing SQL gates) and **010b** (derive remaining dimensions).
> - **Demoted 013 multi-LOS to an interface note (contrarian — most-likely-wasted):** gated on a partner who doesn't exist, serves an unconfirmed ICP assumption, depends on positioning the PRD says the MVP can't cash. Tracked as a v3 interface, removed from the build arc.
> - **Marked Principle VII as a new bet, not external validation (metacognition):** the constitution was amended to contain VII the same day this roadmap introduced the Authored Configuration Model — co-authored, not a pre-existing test the design passed. Language corrected throughout.
> - **Fixed the coverage denominator (metacognition):** the 2,937/853/402 archetype counts are **57% of the 7,398 conditions**; the remaining 43% are *believed* (not confirmed) to be the same kinds, pending Kayla's rules review. No longer presented as the whole population.
> - **Added Tension 7 (trust-ordering vs demo-ordering):** the feature that *won the room* (self-service authoring, 009) is sequenced ninth; engine-first is the right trust order but it is in tension with what converts the demo. Surfaced, not silently resolved. **Declined** the contrarian "compile spine is over-built" framing — in regulated QC, auditability alone (not variance/cost) justifies compiling; the 002a-gates-002b discipline already prevents over-building.

> **Changelog v0.2 → v0.3** (unify config as authored data):
> - **Added the "Authored Configuration Model" section** below. Routes → Blocks → Checks and the **field catalog** are one family at four layers, sharing the same mechanics: authored → SME-signed → SHA-256 hashed → version-pinned interpreter → DET/AUDIT/SAFE gates. This makes the constitution's "judgment lives as authored data, not code" pattern (Principle II / `reconcile.py` ruling #3) apply *uniformly*, not just to normalizers.
> - **Rescoped 001** from a fixed `{doc, los, mismo}` shape to a **schema-driven field catalog** (the *vocabulary* layer) + a **source-agnostic `{truth, sources{}}` envelope** (N sources, no code change). The per-field envelope (`value, source_origin, citation, confidence`) stays typed — determinism hashing, the confidence gate, and source-independence all rest on it. Field *set* becomes fluid; per-field *structure* stays stable.
> - **Added referential integrity as a SAFE-gate rule:** every check's `field_name` must resolve to a catalog entry — an unresolved reference is a silent no-op, i.e. a false-clear vector.
> - Constitution bumped to v1.1.0 (new Principle VII: Configuration is Authored Data).

> **Changelog v0.1 → v0.2** (metacognitive review):
> - **Sliced 003 by check-kind archetype** (003a predicate / 003b ratio_threshold / 003c reconcile). The single "widen to the real 800" feature spanned 17 AMQ categories and was the largest body of work in the arc — lumping it violated Principle IV (build core, don't boil the ocean). Each slice now ships with its own eval coverage + zero-false-clear gate, ordered by real-condition coverage measured from `taxonomy.json` (predicate 2,937 conditions → threshold 853 → reconcile 402).
> - **Inserted 002a-compile-fidelity-spike** before the full compiler (now 002b). G3 spiked the *runtime-LLM* question; it never spiked the *config-time compile* question — whether the LLM can turn the real AMQ workbook into a correct signed ruleset at scale is still unproven. Throwaway spike de-risks before the full compiler is specced. Now flagged the highest-risk irreversible item.
> - **Rescoped 009** (program gating) to cite existing evidence: the AMQ workbooks already carry **615 machine-readable SQL gating rows** (`taxonomy.json` `sql_gating_rows_excluded` = 615). Honor what the sheet already encodes; derive dimensions only where it doesn't. Not a from-scratch "profile-derivation layer."
> - Renumbering: 002→002b; old 003 split into 003a/b/c; old 004–012 shift to 005–013.

> **What this is:** the full feature arc as **numbered, dependency-ordered features**, each
> ready to become a GitHub Spec Kit spec via `/speckit-specify`. It does NOT contain code,
> data models, APIs, or EARS criteria — the architect owns those. It organizes and sequences
> what the PRD already articulated; it does not contradict it.
>
> **The frame:** three surfaces the constitution names — **Apply** (deterministic engine),
> **Author** (no-IT config), **Output** (clear exceptions fast) — plus the cross-cutting spine
> (signed-ruleset compiler, the authored configuration model, audit/citation trail). Sequencing
> de-risks the compile bet with a throwaway spike first, then widens the engine toward the
> real 800 checks **one archetype slice at a time**, hardening the compiler **before** the
> authoring UI; the eval harness keeps pace with every rules-touching feature.

---

## The Authored Configuration Model (one model, four layers)

Everything the SME configures is **authored data**, not code — the constitution's
defining pattern (Principle II; `reconcile.py` ruling #3: judgment lives as data
referenced by name, interpreted by version-pinned engine code). **Principle VII is a
*new bet* introduced alongside this roadmap (constitution v1.1.0, amended the same
day), not a pre-existing constraint this design was tested against** — we are
asserting the field catalog and Routes → Blocks → Checks *should* be one family, and
committing to find out. They share one set of mechanics:

> **authored → SME-corrected & signed → identified by SHA-256 → executed by a
> version-pinned interpreter → gated by DET (determinism) + AUDIT + SAFE.**

| Layer | What it is | Maps to | Feature |
|---|---|---|---|
| **Field catalog** | the *vocabulary* — which data elements exist (`note_rate`, `flood_zone`…), each with type, the sources expected to carry it, and citation/confidence requirements | the canonical loan's field set | **001a** |
| **Checks** | assertions *over fields* — each references a `field_name` from the catalog (kind: predicate / ratio_threshold / agree_*) | the 7,398 real AMQ conditions | 002b, 003a/b/c |
| **Blocks** | named groupings of checks | the **17 real AMQ categories** (Income, Property-Appraisal…) | 009a/b |
| **Routes** | compositions of blocks + applicability gating (which fire for which product) | program/product gating | 009b, 010a/b |

> **Scope note (review AMBER):** only the **field-catalog + checks** layers have a
> consumer before a pilot converts — the engine (003a/b/c) needs them. The
> **blocks/routes** layers have *no authoring consumer until 009/v2* (the MVP
> hand-authors). We build the catalog the engine needs now; the four-layer unified
> model is the *target*, not all built up front. Fluid-vs-fixed and referential
> integrity (below) still apply to what we build.

**Unify the mechanics; keep the layers distinct.** Fields are *vocabulary*; checks/
blocks/routes are *logic over that vocabulary*. The dependency direction is one-way
(a check references a field; the catalog declares the field exists), and that buys a
safety property the SAFE gate enforces: **every check's `field_name` must resolve to
a catalog entry — an unresolved reference is a silent no-op, i.e. a false-clear
vector.** This referential-integrity check is why we do *not* flatten everything into
one undifferentiated blob.

**What stays fluid vs. fixed.** The field *set* and the source *list* are
data-driven and scale without engine changes (add a field or a settlement-agent feed
by authoring, not coding). The per-field *envelope* is a stable typed shape —
`{value, source_origin, citation, confidence}` — because canonical hashing
(determinism + audit) and the confidence gate both depend on it. Fluid where
flexibility scales; fixed where the non-negotiables rest.

---

## Foundation (DONE — do not re-spec)

These three are proven base. Everything below builds on them. They are cited, not re-built.

**P0 — the determinism proof (`p0/`).** Proves the engine is a pure function of
`(signed_ruleset, loan)`: Decimal money/ratio math with pinned `ROUND_HALF_EVEN`, bit-exact
across 1000 runs, the two-step model (Step 1 reconcile = FLAG/info, Step 2 QC = the only
pass/fail), signed ruleset by SHA-256 with measured SME edit-distance, hash-chained
tamper-evident audit log, confidence-gated auto-clear, and a real MISMO 3.4 adapter on the
system side. **Guarantees:** same loan → same verdict, every machine; show-me-the-math audit;
zero marginal runtime cost. This is the embodiment of NON-NEGOTIABLES I, II, V.

**Synthetic eval — ground truth by construction (`p0/eval_synth/`).** Decomposes "we need real
loans" into three questions and solves the two that don't need them: engine correctness (the
mutation *is* the label — 40,000/40,000 checks exact, **0 false-auto-clears** on 5,000 loans)
and interpretation correctness (a rules review of mutation→verdict, decoupled from loan hunting).
Archetypes derive from the **real** AMQ workbooks (7,398 conditions, 0 uncovered check-kinds).
**Guarantees:** a zero-false-auto-clear regression floor that absorbs real loans with no harness
rework. This is the embodiment of NON-NEGOTIABLE III and the Eval/Safety quality gates.

**G3 bake-off — the architecture decision, on evidence (`p0/experiment_g3/`).** A pre-registered
head-to-head (compiled engine vs governed runtime-LLM, temp=0, two models) that *refined the bet*:
reproducibility is NOT the discriminator (both models byte-identical), and cost is ~$27–$70/10k-run,
not $10K. What survived: runtime-LLM correctness is **model-dependent and unknowable in advance**
(Haiku reproducibly cleared a 98%-LTV loan; Sonnet caught it), and only the compiled engine can hand
a regulator the derivation. **Guarantees:** the load-bearing reason to compile is **auditability +
guaranteed-correct math**, not variance or cost — and that the real-loan re-run is the one remaining
gate. This is the empirical basis for Principle I.

---

## The Feature Arc

Each feature: **Why · Scope (in) · Out of scope · Depends on · Surface · Constitution gates.**
Gate shorthand: **DET** (determinism), **SAFE** (zero-false-auto-clear), **EVAL**, **AUDIT**, **CONF** (confidence).

---

### 001a-field-catalog  *(IMPLEMENTED 2026-07-01 — annotation added 2026-07-26, spec audit)*
- **Why:** The engine needs a *scalable, maintainable* vocabulary for loan data — the **field-catalog layer** of the Authored Configuration Model. This is the real prerequisite the engine slices (003a/b/c) consume, and it must grow to hundreds of fields (the 800 checks) *without engine changes*. (Split from old 001 per review: the catalog is the engine's dependency; the N-source generalization is a separate bet — 001b.)
- **Scope:**
  - **A schema-driven field catalog** — fields declared as **authored data** (type, expected sources, citation/confidence requirements), not hardcoded attributes. Adding a data element is an authoring act, not a code change. This is the layer that scales to the 800 checks.
  - **The stable typed per-field envelope** — `{value, source_origin, citation, confidence}`. This shape is *fixed* (determinism hashing, the confidence gate, and audit all rest on it), even as the field *set* is fluid.
  - **Referential integrity** — a validation (SAFE gate) that every check's `field_name` resolves to a catalog entry; an unresolved reference is a silent no-op = false-clear vector.
- **Out of scope:** The N-source envelope generalization + inbound contracts (001b); the routes/blocks **authoring UI** (009). 
- **Depends on:** P0 (generalizes `model.py`'s field map from fixed slots to a signed catalog).
- **Surface:** Cross-cutting (the vocabulary layer of the Authored Configuration Model).
- **Gates:** SAFE (referential integrity; confidence present on every truth value), CONF, AUDIT (catalog is part of the canonical hash), DET (the catalog is signed/hashed like any authored artifact).

### 001b-source-envelope-and-inbound-contracts  *(IMPLEMENTED 2026-07-01 — annotation added 2026-07-26, spec audit)*
- **Why:** Source independence (Principle V) plus the *scaling bet* — the system must accept N independent sources (doc, LOS, MISMO, a future settlement-agent feed) without a code change per source. Separated from 001a because the catalog is needed first and certainly; the source-agnostic generalization is a distinct, slightly more speculative design move.
- **Scope:**
  - **A source-agnostic per-field structure** — replace the fixed `{doc, los, mismo}` attributes with `{truth, sources: {name → value}}`. N sources, no new attributes; `truth` is always the document side (Principle V).
  - The **Touchless inbound contract** (extracted fields + classification + citation + confidence) and the **LOS/MISMO inbound contract** as *consumed interfaces* mapping onto the catalog. MISMO 3.4 / ULAD-DU accepted as a same-data system source.
- **Out of scope:** Building extraction (Touchless owns it); building the LOS connector (reuse existing); multi-LOS reconciliation logic (was 013, now a v3 interface note). These are **interface contracts that may widen**, not builds.
- **Depends on:** 001a.
- **Surface:** Cross-cutting (the data-ingest layer of the Authored Configuration Model).
- **Gates:** SAFE, CONF, AUDIT, Source-independence.

### 002a-compile-fidelity-spike  *(throwaway de-risking spike — highest-risk irreversible item; COMPLETE 2026-07-01, verdict PROVISIONAL PROCEED — annotation added 2026-07-26, spec audit)*
- **Why:** "Compile, then run" is the architectural bet (Principle II), but G3 only spiked the *runtime-LLM* side. The *config-time compile* question — can an LLM turn the **real** AMQ workbook (800+ rows, `demo/rules/*.xlsx`) into a **correct** signed ruleset at scale? — is **unproven**. `taxonomy.py` only *classifies* conditions; spreadsheet-intent → compiled DRL/JSON is untested. Per the constitution's "de-risk the irreversible thing first / throwaway spike before full specs," prove the mechanism cheaply before committing the full compiler spec.
- **Scope:** A G4-style bake-off: take a real slice of the AMQ workbook through the LLM compiler, measure **three** things, not two:
  - (a) **ruleset runnability + correctness** — does the generated rule evaluate to the right verdict on constructed-label cases (using the existing `p0/eval_synth` scorer)?
  - (b) **interpretation fidelity (the actual compile risk)** — did the LLM read the workbook row the way the lender *means* it? This is eval_synth's "Question 2," which construction can't answer: requires an **SME (Kayla) rules-review** of a sample of generated rules against the source conditions. A rule can be perfectly runnable and still misread the intent — (a) alone would pass while missing the thing the spike exists to catch.
  - (c) **required SME correction** — tie to the existing edit-distance / sign-off-theater machinery; high correction = the LLM isn't compiling, the SME is.
  - Output: a go/no-go on the compile approach + calibrated SME-effort-per-rule + an interpretation-error rate.
- **Out of scope:** Production compiler hardening; the authoring UI; any runtime LLM. **This is a spike — its code is throwaway; its finding is the deliverable.**
- **Depends on:** 001a; uses the **already-built `p0/eval_synth` scorer** (not the later 005 CI productionization) to score generated rules; needs an SME review slot for (b).
- **Surface:** Cross-cutting (compiler spine, de-risking).
- **Gates:** DET (generated rules must be deterministic), EVAL (scored against constructed labels), AUDIT (edit-distance measured). **Pre-registers its decision rule before running, per the G3 discipline — including the interpretation-fidelity threshold.**

### 002b-ruleset-compiler-pipeline  *(IMPLEMENTED — all 31 tasks, see plan.md Implementation Notes; annotation added 2026-07-26, spec audit)*
- **Why:** "Compile, then run" is the architectural bet (Principle II, G3). The LLM interprets SME intent at *config time* and emits a signed artifact; the engine never sees a model at runtime. **Only specced once 002a de-risks the compile approach.** *(That gate was satisfied — 002a returned PROCEED 2026-07-01 and this feature shipped; sentence kept as the original sequencing rule, tense corrected by the annotation above. 2026-07-26 audit.)*
- **Scope:** The compile→correct→sign loop at production scale: LLM drafts a ruleset from rule intent; SME corrects and **signs**; artifact identified by SHA-256; per-rule provenance (draft vs signed) and measured edit-distance with sign-off-theater detection. Reconciliation/normalization logic lives **inside** the signed artifact as named, authored data.
- **Out of scope:** The authoring *UI* (that's 009); product/program gating (that's 010). Runtime LLM calls of any kind.
- **Depends on:** 001a, 002a (the spike gates this spec).
- **Surface:** Cross-cutting (compiler spine) → feeds Apply.
- **Gates:** DET, AUDIT (the signed artifact is the audit anchor). Tension watch: zero-edit sign-off must surface loudly, not pass silently.

### 002c-domain-knowledge-grounded-compilation  *(IMPLEMENTED 2026-07-20 — two research passes, see spec.md; corrected here 2026-07-24, plan.md's own Implementation Notes already showed T001-T036 complete/164 tests passing/real Bedrock proof run, but this roadmap entry had drifted stale at "specced")*
- **Why:** `002a`'s spike found 3 of 24 real rows ambiguous from row text alone — grounding the compile step in real regulatory/guide context (not just the bare row) is the fix. The originally-proposed design (live multi-agent web research per row) was evaluated against Principle II's reproducibility/auditability bar and found unsupported by any published prior art in a regulated industry, and expensive (~3–15x cost multiplier at ~7,000-row scale, research-cited). Revised to: a static, versioned, per-program knowledge base (segmented by `010a`'s 6 confirmed programs), built once by research agents, SME-signed before use, incrementally updatable — the pattern research confirmed is actually used in regulated-industry RAG systems.
- **Scope:** KB build (SME-signed, program-scoped, content-fingerprinted, versioned) → grounded per-row compilation (extends `002b`'s `compile_llm.py`, standard retrieval against the frozen KB, never a live agent call) → multi-model judge panel (2+ models, different family than the compiler, ANY disagreement escalates — no majority-vote auto-approve, given researched correlated-error risk) → SME review of the exception queue only → sign-off & version-lock, every compiled check provenance-anchored to its exact KB version. Full 10-step intake workflow (upload → fingerprint → classify/gate-on-novelty → KB build/update → extract → judge → integrity screen → SME exceptions → sign-off → deploy) specced in `spec.md` US5.
- **Out of scope:** Replacing `005`'s eventual eval-CI-gate (judge panel is triage, not a correctness proof); an automated "grounding went stale" re-review trigger when KB material changes after a rule is signed; the authoring/import UI surface (`009a/b/c`) — this feature specs the backend workflow, not its UI.
- **Depends on:** 001a, 002b, 010a (all implemented).
- **Surface:** Cross-cutting (compiler spine, extends `002b`) → feeds Apply.
- **Gates:** DET (grounding uses frozen, versioned retrieval only — SC-003 requires zero live-search calls in the compile path), AUDIT (every compiled check's provenance chain: source doc → KB version → judge verdicts → SME sign-off), EVAL (judge-panel auto-approve/escalate split must be measured on a real pilot batch, not assumed from literature — FR-010).

### 002d-operator-consistency-gate  *(IMPLEMENTED 2026-07-25 — Phase 1 shipped, see spec.md)*
- **Why:** SME review call (2026-07-24) found `compile_llm.py`'s `SYSTEM_PROMPT` never states that
  `ratio_threshold`'s `operator` must express the PASS condition — so a FAIL-framed source sentence
  ("if LTV exceeds 80%...") gets transcribed literally instead of inverted, producing a confirmed
  false positive at loan 01's exact 80% LTV boundary. A heuristic re-scan found the same signature in
  45/495 compiled `ratio_threshold` checks. External research confirmed this is a documented, named
  LLM failure class ("Conditional Misalignment Error"), not a one-off prompt defect.
- **Scope:** (1) Prevention — state the PASS-condition convention explicitly in `SYSTEM_PROMPT` with
  inversion few-shot examples. (2) Detection — formalize the manual heuristic scan into a permanent,
  deterministic `operator_consistency_check()` run on every compile batch, comparing structured
  `operator`/`threshold` against the LLM's own `message_pass`/`message_fail` text (no new LLM call —
  both already exist from one compile call); a flagged check is excluded from auto-sign.
- **Out of scope:** Re-signing or regenerating the currently-shipped `post_closing_only_ruleset.json`
  or its downstream reports — separate housekeeping, tracked in `output/SME-REVIEW-FINDINGS-2026-07-24.md` §4.
- **Depends on:** 002b (implemented).
- **Surface:** Cross-cutting (compiler spine, extends `002b`).
- **Gates:** DET (no new LLM call in the detection gate), EVAL (SC-001/002: true-positive floor of 45
  known suspects, measured false-positive rate against correct checks).

### 002e-conditional-applicability-gating  *(IMPLEMENTED 2026-07-25 — Phase 1 shipped, see spec.md)*
- **Why:** Same SME call found the tool has no mechanism for loan-fact conditional applicability —
  every compiled check runs unconditionally, so a gift-fund-related check surfaced as an unresolved
  gap on loan 01 (which used no gift funds) instead of resolving `NOT_APPLICABLE`. `010a`'s program
  gating is orthogonal (which product a rule belongs to, not whether a loan's own facts satisfy a
  precondition). External research (XACML `Target`/`Condition`/`Effect`, DMN condition-columns) both
  independently converge on a gate evaluated first, resolving to a distinct not-applicable outcome —
  exactly what this engine's `NOT_APPLICABLE` status already is.
- **Scope:** One new optional `Check` field (`applies_if: List[{field_name, operator, value}]`,
  AND-combined, `operator` including `in`/`between` — revised 2026-07-24 from a single-condition
  design after reviewing Olav's live "Ratio-Space Console" demo, `output/AGENT-LAB-SCENARIO-CONSOLE-FINDINGS-2026-07-24.md`,
  a sibling Tavant system solving the identical guideline-compilation problem whose real compiled
  output confirmed compound conditions are the norm); one new deterministic gate in `engine.py`,
  evaluated before kind-dispatch; `catalog.py` referential-integrity extended. **Sourcing mechanism
  revised again, 2026-07-24, superseding the paragraph below**: `applies_if` is no longer populated by
  a bespoke defect_text-only extraction step this spec owns — it's sourced through
  `002f-precondition-ontology-layer`'s three-layer sequence (deterministic cross-reference clustering
  → source-text extraction → KB-grounded/mandatory-human-reviewed extraction), a standalone, reusable
  capability this spec consumes. Phase 1 proves the mechanism against loan 01's real gift-fund case; a
  full rulebook recompile is explicit Phase 2, unscheduled. **Update 2026-07-26:** the actual wiring
  from `002f`'s extraction into a real compiled `applies_if` was never built even after Phase 1 shipped
  — and (corrected 2026-07-26, adversarial audit) no `applies_if` exists anywhere outside the
  engine/schema and its tests: `ruleset_defects.py` contains zero, and no compiled ruleset carries
  one. Nothing has ever populated it in production. Closing that, plus a canonical-fact dedup layer this spec's own design didn't
  anticipate (two rows about the same real fact could extract two different field names with nothing
  to reconcile them), is now scoped as `002g-canonical-loan-fact-vocabulary`.
- **Out of scope:** The extraction mechanism itself (owned by `002f`); any general cross-row
  dependency-graph inference beyond what `002f`'s Layer 0 clustering already covers; changing `010a`'s
  program gating; the compile-time wiring and canonical-fact dedup (now `002g`).
- **Depends on:** 001a (implemented), 002b (implemented), 010a (implemented — complementary, not
  modified), **002f (implemented — this spec's sourcing mechanism)**.
- **Surface:** **Author** (configured) + **Apply** (executed) + compiler spine.
- **Gates:** DET (the gate is a pure data comparison, zero LLM at evaluation time — this is the direct
  compiled-engine fix for the exact gap `examples/mortgage-qc` instead papers over with a live
  per-loan LLM call, per `docs/architecture/rule-compiler.md` §6), SAFE (a false `NOT_APPLICABLE` — a
  real defect silently resolving as not-applicable — is the failure mode guarded hardest against),
  EVAL, AUDIT (`applies_if` extraction traceable to a quoted source span, same discipline as
  thresholds).

### 002f-precondition-ontology-layer  *(IMPLEMENTED 2026-07-25 — Phase 1 shipped, see spec.md; modular, reusable capability)*
- **Why:** `002e`'s original design (extract `applies_if` from `defect_text` alone) proved too narrow
  the moment it was tested against real data: the AMQ workbook's "Question Criteria by Questions"
  column — assumed undecodable on the SME call — turned out to be a structured
  `QuestionID == N && AnswerText == "..."` expression, decodable by clustering across every row
  sharing the same `N` (24 distinct IDs found, covering 3,255 of 5,520 real Post-Closing rows, zero
  LLM). External research (ComplianceNLP, arXiv:2604.23585) confirms extraction reliability falls
  sharply with cross-reference hop-distance (97.1% at 0 hops → 84.6% at 3+), which sets this feature's
  core design principle: exhaust the cheapest, most verifiable layer first.
- **Scope:** A standalone package (`p0/ontology_extraction/`, zero imports from `qc_engine`) — Layer 0
  (deterministic cross-reference clustering), Layer 1 (source-text extraction with explicit deontic-
  modality classification, per arXiv:2001.11245/GDPR-deontic-classification precedent), Layer 2
  (KB-grounded extraction reusing `002c`'s implemented `knowledge_base.py`/`judge_panel.py`, gated by
  an automated grounding-verification check and **mandatory human sign-off, never auto-approved**, a
  deliberate stricter override of `002c`'s default). Two mechanisms adopted from `project/Onity`'s
  independently-built, real "Ontology Graph Mapping" pipeline (same architecture shape, different
  problem): bounded-retry-then-explicit-abstain for malformed LLM output, and a coverage-based
  circuit breaker so the package fails loudly (not silently) against a rule source with no matching
  structure — the concrete mechanism behind "reusable with other projects."
- **Out of scope:** A full recompile of the Retail workbook through all three layers (Phase 2, a
  separate real-spend decision); any UI for reviewing Layer-2 proposals (reuses `002c`'s existing
  SME-exception-queue mechanism). **Update 2026-07-26:** Phase 2 is now scoped as
  `002g-canonical-loan-fact-vocabulary` — which also closed a real gap this spec left open:
  `run_layers()` was never actually called by `compile_llm.py` (verified by grep, zero references
  outside this package's own tests), so no compiled check's `applies_if` has come from this pipeline
  in production yet — in fact (corrected 2026-07-26) none exists anywhere outside the engine's own
  tests.
- **Depends on:** `002c` (implemented — Layer 2 reuses it directly).
- **Surface:** Cross-cutting (compiler spine) — `002e` is its sole mortgage-qc-prod consumer;
  `002g` is now its compile-time caller.
- **Gates:** DET (Layer 0 is a pure function), EVAL (SC-001/002/007/008 measured, not assumed), AUDIT
  (every `PreconditionProposal` traceable to its source layer + provenance).

### 002g-canonical-loan-fact-vocabulary  *(IMPLEMENTED 2026-07-26 — same day as spec; Phase 1, see spec.md)*
- **Why:** `002f`'s Phase 1 shipped tested, working extraction — but `compile_llm.py` never actually
  calls it (verified by grep, zero references outside the package's own tests), so no compiled check
  in production has ever gotten its `applies_if` from `002f`. Separately, `002f`'s Layer 1 lets the
  LLM invent a fresh `field_name` per row with no dedup — two rows about the same real fact ("gift
  funds used") could extract as two different field names, letting two checks disagree about the same
  loan's own nature. Session design work (loan-nature-classification grill-me,
  `output/ROADMAP.md` Tension 9) converged on: compute a loan-nature fact once, centrally, signed
  before use — this spec is that mechanism, plus the wiring `002f`/`002e` left unbuilt.
- **Scope:** Wires `ontology_extraction.pipeline.run_layers()` into `compile_llm.py` for the first
  time; adds a versioned, signed `FactVocabulary`/`CanonicalFact` registry (mirrors `002c`'s KB corpus
  sign-off shape) that a `PreconditionProposal`'s `field_name` must resolve against before gating a
  real check — exact match reuses, synonym flags for human merge, novel fact flags for sign-off,
  never silently duplicated. Default execution mode is a bounded sample, not the full 5,520-row sheet.
- **Out of scope:** Jumbo/QM or any fact requiring new external reference data (a later, separate
  spec, once that reference data is sourced); re-litigating `010a`'s program gating; any runtime LLM
  call; adopting a formal OWL/DL or SHACL reasoner (researched directly this session, deliberately
  not adopted — `engine.py` stays flat, deterministic Python; only the naming/dedup discipline is
  borrowed).
- **Depends on:** `002c`, `002e`, `002f`, `010a` (all implemented).
- **Surface:** Compiler spine only — no new UI surface; reuses `002c`'s existing SME-review queue
  shape for canonical-fact sign-off.
- **Gates:** DET (resolution is a pure lookup against a signed registry, zero LLM at compile-decision
  time beyond what `002f` already runs), AUDIT (every canonical fact traceable to the AMQ row(s) it
  originated from, same discipline `002f` already enforces), EVAL (SC-001 through SC-004, measured
  against the real Retail sheet's known gift-funds row(s), not assumed).

### 003a-engine-predicate-checks  *(largest coverage: ~2,937 real conditions)*
- **Why:** The product is "apply the right checks correctly, every time" (Principle I, IV). Predicate checks are the bulk of the real rule set — MISSING (1,807), POLICY (836), UNSIGNED (106), EXPIRED (98), INCOMPLETE (90) per `taxonomy.json`, all `engine_kind=predicate → is_present/is_true`, QC phase, FAIL on defect. Slicing by archetype (the unit the engine and taxonomy already speak in) keeps each spec shippable, not an ocean-boil.
- **Scope:** Deterministic Step-2 QC execution of predicate check-kinds (is_present / is_true) against canonical loan truth values. Decimal where applicable; pure function — no network, model, wall-clock.
- **Out of scope:** Ratio/threshold math (003b); reconcile (003c); any check-kind Kayla hasn't validated; product/program gating; runtime LLM.
- **Depends on:** 001a, 002b. (001b only where multi-source values are read.)
- **Surface:** **Apply.**
- **Gates:** DET, SAFE, EVAL, AUDIT, CONF. Ships with its own predicate-archetype eval coverage + zero-false-clear gate. **Coverage caveat:** the predicate archetypes account for the bulk of the *classified* conditions; classification covers **~57% of the 7,398 total** — the remaining ~43% are *believed* (pending Kayla's rules review) to be the same kinds, not confirmed.

### 003b-engine-ratio-threshold-checks  *(~853 real conditions)*
- **Why:** THRESHOLD checks (853 conditions: LTV/DTI/%/max-min) are where boundary arithmetic decides pass/fail — the exact class where Haiku reproducibly bought back a 98%-LTV loan (G3). This is the math the regulator audits; Decimal + pinned rounding is load-bearing here.
- **Scope:** Deterministic Step-2 QC execution of `ratio_threshold` check-kinds against truth values, with Decimal money/ratio math and pinned `ROUND_HALF_EVEN` at tolerance boundaries.
- **Out of scope:** Predicate (003a); reconcile (003c); product/program gating; runtime LLM.
- **Depends on:** 001a, 002b. (Independent of 003a — can ship in parallel.)
- **Surface:** **Apply.**
- **Gates:** DET, SAFE, EVAL, AUDIT, CONF. Ships with its own threshold-archetype eval coverage; boundary cases (the buyback class) get explicit golden labels.

### 003c-engine-reconcile-checks  *(~402 real conditions, FLAG-only)*
- **Why:** Reconcile is Step 1 — doc-vs-system comparison that **FLAGs** (informational), never fails QC (Principle V; the two-step model). INACCURATE (263) + MISMATCH (139) per `taxonomy.json`, `engine_kind=agree_categorical/agree_numeric`, RECONCILE phase, FLAG verdict. Keeping this a separate slice protects the flag-vs-fail separation the whole product rests on.
- **Scope:** Deterministic Step-1 reconcile execution (agree_categorical / agree_numeric) across the **independent** doc and system paths; emit FLAGs that do **not** block auto-clear.
- **Out of scope:** Any pass/fail semantics (FLAG-only by construction); predicate (003a); threshold (003b); deriving the comparison value from the same source (source-independence violation).
- **Depends on:** 001a, 001b (reconcile compares the independent truth/system paths — needs the N-source envelope), 002b. (Independent of 003a/003b.)
- **Surface:** **Apply.**
- **Gates:** SAFE (a FLAG must never read as or become a QC fail), EVAL, AUDIT, Source-independence. Ships with its own reconcile-archetype eval coverage.

### 004-loan-disposition  *(the composition layer — added per contrarian review)*
- **Why:** The archetype slices (003a/b/c) each produce *per-check* verdicts, but the **product** speaks in *per-loan dispositions* — "auto-clear vs exception, on THIS loan." The contrarian review caught that "compose all verdicts on one loan into one disposition" was homeless, smeared across 006/007/008. The engine is sliced by its *internal* vocabulary (check-kind); this feature is the *user-visible* unit (a dispositioned loan) that the slices don't individually cover. It de-risks the actual integration: predicate + threshold + reconcile verdicts must compose correctly into one decision.
- **Scope:** The disposition rule over a loan's full result set: QC failures → exception; FLAGs are informational and do **not** block auto-clear (Principle V two-step); nothing needing review + no QC failure → auto-clear. One disposition per loan, deterministic, auditable. This is the seam the confidence gate (006), audit record (007), and queue (008) all attach to.
- **Out of scope:** The exception-review UI (008); the confidence-withhold logic itself (006, which this composes in); product/program gating (010).
- **Depends on:** 003a, 003b, 003c (composes all three kinds — this is the one feature that genuinely needs the full engine).
- **Surface:** **Apply** (the disposition seam) → feeds Output.
- **Gates:** DET, SAFE (the auto-clear/exception split is the safety-critical composition; a FLAG leaking into "fail" or a defect leaking into "auto-clear" both blocked), EVAL, AUDIT.

### 005-eval-harness-as-promotion-gate
- **Why:** Eval is foundational (Principle III); no ruleset promotes without passing the constructed-label scorer and the false-auto-clear gate. This must keep pace with the engine slices (003a/b/c), not trail them. **Amended (v0.6):** "keep pace" now explicitly includes the scenario-*generation* mechanism, not just the scoring/gating mechanism — the current generator only knows how to construct scenarios for 7 hand-picked fields, and `002b` will compile checks against fields nobody has hand-written a mutation for.
- **Scope:** **Productionize** the already-built `p0/eval_synth` (which 002a uses directly) into a **CI promotion gate**: constructed-label scoring + label-free metamorphic invariants, run on every ruleset version bump. **Zero-false-auto-clear is a hard block.** Tiered sets (GOLDEN regression / COVERAGE defect-diversity / VOLUME auto-clear estimate) wired in. Built to absorb real loans with no rework. *(Distinction: `p0/eval_synth` is the existing scorer — 002a depends on that, not on this. 005 is the CI productionization, which lands alongside the engine slices.)* **Added (v0.6):** generalize scenario *construction* — today `generator.py`'s mutation operators are hand-written per specific demo field (`property_address`, `note_rate`, `note_signed`, ...); this must become data-driven off the field catalog (`001a`) and a compiled `Check`'s `kind`, so a synthetic pass/fail scenario can be constructed for *any* compiled check, not just the ones someone happened to hand-author a mutation for. Promote the pattern already proven in `p0/experiment_002a/score_drafts.py` (`_score_predicate`/`_score_ratio_threshold`/`_score_agree_categorical`/`_score_agree_numeric` — generic, kind-based construction, not field-specific) from throwaway spike code into the reusable foundation.
- **Out of scope:** Real-loan acquisition (that's G1, an external dependency — see Interfaces); extraction/OCR-noise realism (the honest residual, labeled loudly).
- **Depends on:** 001a, 003a (scores real engine output; evolves alongside 003b/c). Does **not** gate 002a — the spike uses the pre-existing `eval_synth` scorer.
- **Surface:** Cross-cutting (eval spine).
- **Gates:** EVAL, SAFE, DET (bit-exact harness stays green).

### 006-confidence-gated-auto-clear  *(IMPLEMENTED — confirmed 2026-07-27 by direct code inspection, never previously annotated)*
- **Why:** A confident-but-wrong extraction must never silently clear a defective loan (Confidence gate; Blocker 1 boundary). This is the seam between assumed-periphery (extraction) and the core's safety promise.
- **Scope:** Auto-clear gated on per-field extraction confidence: a PASS that relied on a sub-floor extracted truth value is withheld to `NEEDS_REVIEW`. Make the floor calibratable (not a magic 0.80) once Touchless confidence is characterized.
- **Out of scope:** Calibrating Touchless confidence itself (upstream, gate G2); rebuilding extraction.
- **Depends on:** 001a, 003a (applies once predicate QC produces PASS verdicts; extends across 003b/c); composed into the disposition by 004.
- **Surface:** **Apply** (safety seam) → surfaces into Output.
- **Gates:** CONF, SAFE, EVAL.
- **Confirmed built (2026-07-27):** `p0/qc_engine/engine.py:412-418` — a real PASS→`NEEDS_REVIEW` gate: `if res.status == "PASS" and sv.doc is not None and sv.doc_confidence is not None and sv.doc_confidence < confidence_floor: res.status = "NEEDS_REVIEW"`. `confidence_floor` is a real parameter threaded through `run()`/`_eval_check` (engine.py:29,514-515,522), not a hardcoded literal — `DEFAULT_CONFIDENCE_FLOOR = 0.80` is only the *default*, structurally calibratable the moment Touchless confidence is characterized. The one open item (external calibration data) is exactly the out-of-scope item this entry already named — nothing left to spec or build here.

### 007-audit-trail-and-citation-of-record  *(IMPLEMENTED — confirmed 2026-07-27 by direct code inspection, never previously annotated)*
- **Why:** "If they don't understand how you calculated that number, you buy back the loan." Defensibility is one of the two business hires (Audit gate; Principle I).
- **Scope:** Hash-chained, tamper-evident decision log; each record carries field-level intermediates (the three inputs, normalized/derived value, rounding, rule version + hash, verdict, citation). Chain-verification surface. Every doc-sourced value traceable to doc name + page + segment.
- **Out of scope:** WORM storage infra / Object-Lock anchoring (industrial build-out — Monish's team); examiner-facing reporting UI beyond traceability.
- **Depends on:** 003a (audit records the first verdicts; extends across 003b/c); records the 004 disposition as the loan-level audit anchor.
- **Surface:** Cross-cutting (audit spine) → backs Output.
- **Gates:** AUDIT, DET.
- **Confirmed built (2026-07-27):** `p0/qc_engine/audit.py` implements the full hash chain (`_digest` line 28, `AuditLog.append` lines 58-77) and a real `verify_chain()` (79-93) that walks every record and recomputes hashes to detect tampering. Every citation flows end-to-end: `DocCitation` (model.py:40-73) → `sv.citation.to_dict()` (engine.py:164) → `CheckResult.citation` (engine.py:59,81) → `RunResult.to_dict()` (engine.py:499) → the audit payload — verified against a real artifact, `p0/eval_synth/artifacts/synth_eval_audit_verify.json`. This was built as part of the P0 determinism proof (2026-06-26), before this feature was ever named/numbered on the roadmap — it was simply never annotated. Nothing left to spec here beyond the already-named, already-out-of-scope WORM/Object-Lock anchoring.

### 008-exception-queue-and-clear-next
- **Why:** "I'm done with this loan. Next one, next one, next one." Throughput is the other business hire; this is the Output surface that won the room's daily use (Principle VI).
- **Scope:** Harden the prototype's `LoanQueue` + `ExceptionReview` + `PdfViewerModal`: result set with **flags vs QC-failures shown separately**, citation viewer (doc/page/highlighted segment), clear-&-next-loan flow, mitigation types (UNRESOLVED/OVERRIDDEN/ESCALATED/SYSTEM_CORRECTED), statuses (Pending/Auto-Cleared/Exception/Resolved). Match the existing design language (Inter/Space Grotesk/JetBrains Mono, slate canvas, blue accent). UI tone: informational, never alarming.
- **Out of scope:** Authoring of rules (009); workflow/sampling/defect-tracking/GSE reporting (legacy-platform turf, partner/defer).
- **Depends on:** 004 (displays the per-loan disposition), 006, 007.
- **Surface:** **Output.**
- **Gates:** AUDIT (citation traceability), SAFE (flags must not read as failures; auto-clear separation honored).

### 009a-import-and-diff-sign  *(the MVP authoring experience — see `output/AUTHORING-UX-DECISION.md`)*
- **Why:** "Authoring" for the pilot is not free-text — it is **get your existing rules in, see what the compiler made of them, and sign.** The AMQ workbook already *is* a structured authoring source (7,398 conditions, 615 SQL gates); the SME "authors" by importing what they already maintain, not re-entering thousands of rows. The **diff-and-sign review surface** is the real centerpiece and the real engineering risk (Principle II sign-off; Principle VI no-IT).
- **Scope:** Ingest the AMQ workbook (bulk path); render **source-condition ↔ compiled-gate ↔ plain-English restatement** side by side per rule; capture SME sign-off bound to the human-corrected artifact (SHA-256); **measure + surface edit-distance** (a batch signed with zero edits is flagged as sign-off theater, not celebrated — Principle II). Hardens the prototype's `RuleCompilerVisualizer` into a *real* compiled-artifact review (the prototype currently only *simulates* compilation — design language, not behavior contract).
- **Out of scope:** Free-form NL authoring (009c); net-new visual authoring (009b); extraction/LOS config.
- **Depends on:** 002b (the compiler), 010a (honor the 615 SQL gates on import), 005 (no imported rule runs without passing the eval gate).
- **Surface:** **Author** (the bulk + trust-anchor surface).
- **Gates:** DET, EVAL, AUDIT (sign-off binds to human-corrected text; edit-distance measured).

### 009b-guided-structured-editor
- **Why:** Net-new and edit authoring needs a **catalog-constrained structured surface** — and crucially, this surface **owns the criteria gate** so natural language never does (the gate is the one field a non-technical SME can't fluently read = the false-clear sign-off-theater hole, Tension 8).
- **Scope:** A guided editor for a single check (gate via **catalog-constrained controls** — field picked from the catalog, operator from a list, value from known values; significance; AOR), block grouping, field-catalog entry (typed, sources, confidence), and a **visual route-DAG builder** (over the Example-1 structure). **Referential integrity enforced at author time**, not caught later by the SAFE gate.
- **Out of scope:** NL drafting (009c); the compiler internals (002b).
- **Depends on:** 001a (the catalog it edits/constrains against), 002b.
- **Surface:** **Author** (the safe surface for dense logic).
- **Gates:** SAFE (referential integrity by construction; the gate is structured, never free text), DET, AUDIT.

### 009c-nl-drafting-assistant  *(v2 — conditional on 002a)*
- **Why:** NL authoring is the magic that won the room (Principle VI) — but it is *conditional*: the user gated it on "if dependable and accurate," and 002a is the experiment that answers that. NL works at **config time only**, drafting *into* the guided UI.
- **Scope:** SME types intent in prose → the LLM (config time) pre-fills the **prose fields** (question text, description, suggested significance) and **proposes a structured gate into 009b's catalog-constrained control for field-by-field confirmation.** NL **never** emits free-text logic that bypasses the structured surface or reaches runtime (Principle I/II).
- **Out of scope:** NL authoring the criteria gate as free text (Tension 8 — forbidden); any runtime LLM.
- **Depends on:** 009b (writes into its control), **002a's go-decision** — if config-time interpretation fidelity is poor, **009c does not ship**; the product stays import + guided.
- **Surface:** **Author** (the v2 drafting layer).
- **Gates:** DET, EVAL, AUDIT. **Conditional feature** — gated on 002a + G4 + Tension 8 sign-off.

### 010a-program-applicability-gating  *(renamed from "010a-honor-encoded-sql-gating"; corrected twice 2026-07-20 — see `output/RULE-PROGRAM-GATING-FINDINGS.md`; IMPLEMENTED)*
- **Why:** "We don't want to run all 800 for every loan" — an FHA rule must not fire on a VA loan, etc. (Blocker 3). **Final corrected finding (2026-07-20, after a full column/sheet audit + domain research):** the primary, machine-readable program signal is the **Exception Code prefix** carried on every real rule row — `O-FHA-`, `O-VA-`, `O-RHS-` (USDA), `O-FRD-` (Freddie), `O-FNM-` (Fannie), `SONYMA` (NY state housing program, space-delimited format) — covering **7,241 of 8,442 real rows (85.8%)**, mapping directly onto the 5 synthetic loans' own programs (SONYMA added per explicit direction though untested — no synthetic loan carries it yet). The per-row SQL gating clause (secondary) narrows further and agrees with the prefix on `QC_Policy`, but also carries `PropertyType`, `Occupancy` (owner-occupied vs. investment — the roadmap's own original motivating example, already encoded not derived), `Underwriting_Type` (AUS), `LoanType`, `LoanPurposeType`, `AddressState`. One entire questionnaire ("Post-Closing Private Bank Oct 2025," 802 rows) exports its columns one position shifted from the other 3 sources — found, and corrected in `taxonomy.py`. Full evidence and the two self-corrections made getting here: `output/RULE-PROGRAM-GATING-FINDINGS.md`.
- **Scope:** Parse **both** real mechanisms — (1) the Exception Code prefix → program (6 confirmed), the primary signal; (2) the per-row SQL gating clause, PropertyType narrowing implemented, Occupancy/Underwriting_Type/LoanType/LoanPurposeType found-but-deferred to a future increment of this same feature (not `010b` — they're already encoded, not derived). Also fixed: `taxonomy.py` now reads every sheet (not just the first) and corrects the one shifted questionnaire's column layout. Executed by 003a/b/c, surfaced on import (009a).
- **Out of scope (this increment):** Occupancy/Underwriting_Type/LoanType/LoanPurposeType narrowing (found, not yet gated on); deriving gates neither mechanism encodes (`010b` — may need less new work than assumed, now that more is confirmed already-encoded); AOR-based finding routing (confirmed real, feeds `008` later, not this); severity-taxonomy alignment (this workbook's Critical/Major/Minor vs. `engine.py`'s CRITICAL/WARNING/INFO — feeds `006`/`008`, not this); the unrelated `Question Criteria by Questions` column (questionnaire branching logic, not program gating).
- **Depends on:** 003a/b/c (implemented), 002b (implemented). 009a (import surfaces the gates for sign-off) is a future consumer, not a build dependency.
- **Surface:** **Author** (configured) + **Apply** (executed).
- **Gates:** EVAL (gating must not silently skip a check that should fire — a new false-clear vector), SAFE, AUDIT (which rules fired, under which gate, is part of the trace). All green: 144/144 tests, zero-regression digest unchanged, 25/25 known defects.

### 010b-derive-remaining-gating-dimensions
- **Why:** Where the sheet does *not* already gate, QC dimensions must be derived (Blocker 3 residual; ULAD fields gate on derived attributes — `QC_Policy` from AUS type, occupancy, income bucket). Sequenced after 010a so we only build derivation for the gates the SQL doesn't already cover.
- **Scope:** A profile-derivation layer for the *remaining* dimensions only: derive `QC_Policy` / occupancy / income-bucket gating attributes from loan data where no SQL clause encodes them.
- **Out of scope:** Re-deriving gates 010a already honors; pulling Fannie/Freddie selling guides beyond the client spreadsheet (resolved-in-part 2026-07-24 — see Tension 9 and `output/SME-REVIEW-FINDINGS-2026-07-24.md`: the real gap is loan-fact conditional-applicability gating, not program gating; a Selling Guide may only gate whether an existing rule applies, never originate new rule content or trigger additional questions).
- **Depends on:** 010a (knows what's already gated), 001b (consumes the gating attributes).
- **Surface:** **Author** + **Apply.**
- **Gates:** EVAL, SAFE, AUDIT.

### 011-label-confirmation-flywheel  *(DEFERRED 2026-07-27, same day as spec.md was written — Gordon's explicit scope call: adds complexity not needed this round. Spec is complete, evidence-grounded, and ready to build whenever it's picked back up — this is a scheduling decision, not a quality or design problem found with it. Left out of `output/scratch/architecture-doc-v2.html`'s current picture for the same reason 013 doesn't appear in the mega-flow diagram: deferred work isn't part of "how it works right now.")*
- **Why:** The primary moat is the eval/labeled-outcome flywheel (PRD §9). The engine's cited outputs become draft labels the SME confirms — compounding the corpus. Wire from the first pilot loan.
- **Scope:** Capture SME confirm/correct on cited engine outputs → grow the labeled corpus → feed back into 005's tiered sets. Instrument from day 1 of pilot.
- **Out of scope:** Cross-customer learning (requires the data-rights clause — Q2, a contract dependency, see Interfaces); not a build to over-engineer before a partner signs.
- **Depends on:** 005, 007, 008.
- **Surface:** Cross-cutting (eval spine, moat).
- **Gates:** EVAL, AUDIT (confirmed labels are auditable provenance).

### 012-real-loan-distribution-eval  *(Implemented -- Phase 1, 2026-07-28 -- `p0/eval_real/` adapter + audit-trace + bake-off-mechanism all built and tested against a synthetic S3-shaped stand-in bundle, zero regression; see spec.md's own Status header for exactly what's proven vs. still gated on G1 expert labels + the live 3-real-loan run)*
- **Why:** The G3 accuracy number is *directional* (6 synthetic loans). The one experiment that converts it to load-bearing is the re-run on Kayla's expert-labeled, independent-path loans (G1, the real-data gate). This is the pilot exit criterion's backbone.
- **Scope:** Ingest real expert-labeled loans as just another source into 005's `score()`; the synthetic eval becomes the regression floor, real loans the distribution check. Run the mock-audit exit criterion (an examiner can trace any number to inputs/rounding/rule-version/citation). Re-run the G3 bake-off on real loans.
- **Out of scope:** Acquiring the loans (external SME dependency, G1 — gate, not build); changing the harness (built to absorb with no rework).
- **Depends on:** 005, 007, 011.
- **Surface:** Cross-cutting (eval spine) → pilot exit.
- **Gates:** EVAL, SAFE, AUDIT. This is where the false-auto-clear ≈ 0 claim becomes real-world, not synthetic.

### ~~013-multi-los-reconciliation~~ → DEMOTED to a v3 interface note (per contrarian review)
- **Why demoted:** This was the feature most likely to be wasted effort. It is gated on a design partner who does not yet exist, serves an *unconfirmed* ICP assumption (multi-LOS / recent-M&A lenders), depends on multi-LOS positioning the PRD itself flags as a check the MVP can't cash, and would likely be partially built for positioning then stranded when the actual pilot turns out single-LOS. **Removed from the build arc.**
- **What survives as an interface note:** the **001b** source-agnostic `{truth, sources{}}` envelope is *already* N-source by design — so when a funded multi-LOS need is real, reconciliation resolves the system value across multiple LOS sources without re-architecting. Track multi-LOS as a **v3 interface** the data model is *ready for*, not a feature we build speculatively. Decision owed only if/when a multi-LOS pilot is funded (Tension 2).

### 014-decision-narrative  *(added 2026-07-27, spec.md written same day)*
- **Why:** A run's structured output (disposition, review_reasons, raw `CheckResult` rows) tells a reviewer *how many* checks landed where, not *what actually happened with this loan* in one readable paragraph — `run_013`'s 16,020-verdict comprehensive run made this gap concrete. `ExceptionReview`'s own design (`CLAUDE.md`) assumes a reviewer works loan-by-loan toward "I'm done with this loan, next one," which needs a synthesized summary, not a spreadsheet.
- **Scope:** A per-loan, LLM-authored prose narrative generated exactly once per `RunResult` (never regenerated live), validated closed-set against that loan's own real check_ids/citations/review_reasons before being accepted (same discipline as `002g`'s naming-proposal validation) — grounds every claim in already-computed, already-deterministic data; never influences the verdict itself (read-only, one-way, never parsed back into routing/gating logic).
- **Out of scope:** Rendering/UI placement (`ExceptionReview`, xlsx/PDF export) — a later, separate feature. A run-level (all-loans) narrative. Any change to `004`'s disposition/review_reasons computation.
- **Depends on:** 004 (disposition/review_reasons — the narrative's primary input), 003a/b/c (citations/exceptions).
- **Surface:** Output (loan-level review experience).
- **Gates:** none new — this is presentation-only and cannot fail a loan; DET is unaffected because the verdict it describes is already fixed before this feature ever runs. New, disclosed cost: unlike every other spec in `002`/`003`/`004`, this is a genuine per-loan-per-run LLM call (Gordon's explicit choice over a deterministic-template alternative, 2026-07-27) — tracked honestly via `eval_log.py`'s cost summary, never folded into the pipeline's otherwise-real "$0" claim.

---

## What stays an interface, not a build

Per Principle IV (build the core, assume the periphery), these are **consumed contracts that may widen** — never builds:

- **Touchless extraction contract (inbound):** document blob → extracted fields + document classification + per-field citation + **per-field confidence**. The confidence field is load-bearing for the auto-clear gate (006). The contract widens as more data elements come under review — tracked as an interface in 001.
- **LOS connector (inbound):** reuse the existing connector for system-of-record loan data; MISMO 3.4 / ULAD-DU accepted as a same-data fallback format. Per-LOS connectors are reused, not built.
- **Multi-LOS reconciliation (v3, deferred — was 013):** the 001b N-source envelope is *ready* for multiple system sources, but reconciling across N LOSs is **not** built speculatively. Track as a v3 interface; build only when a multi-LOS pilot is funded (Tension 2).
- **AMQ workbook gating (inbound, partly machine-readable):** the client rule workbook already encodes **615 SQL gating rows** that say which checks fire for which program/policy. 010 *consumes and honors* these clauses rather than re-deriving them — track the gating column structure as an interface that may evolve as the workbook does.
- **Future truth-side widening (A3):** an independent title/settlement feed (UCD / Closing Disclosure) would become a *second* truth-side source. Not present today — track as a future interface, not a build.
- **External non-engineering gates (not features, but blockers):** G1 real labeled loans (Kayla), G2 calibrated extraction confidence (Touchless), G6 design partner + cross-customer data-rights clause (Q2). These gate 006, 012, and the moat — they are dependencies to track, not things this team builds.

---

## Sequencing rationale

The order de-risks the **irreversible thing first** and refuses to let the hard-but-external block the solvable-and-internal.

1. **The compile-fidelity spike (002a) is now the single highest-risk irreversible item — and it comes before the full compiler is specced.** G3 proved the *runtime-LLM* side; it never tested whether an LLM can turn the **real** AMQ workbook into a *correct* signed ruleset at scale, which is the whole premise of "compile, then run." A throwaway spike that takes a real workbook slice through the compiler and measures correctness + SME-correction effort de-risks the architecture before we commit the production compiler (002b). If the spike fails, the entire compile-then-run bet — and the product's differentiation — is in question; better to learn that for the cost of a spike than after building 002b.
2. **The data spine (001a field catalog, then 001b source envelope) anchors everything**, because the canonical contract is what every feature binds to. Getting its shape wrong is an expensive reversal. Split so the engine's true prerequisite (the catalog) lands first; the N-source generalization (001b) is a distinct, slightly more speculative bet.
3. **The engine is sliced by archetype (003a→003b→003c) and ordered by real coverage** — predicate (~2,937 conditions) first, then ratio_threshold (~853), then reconcile (~402, FLAG-only). Each slice is independently spec-able and ships with its own eval coverage + zero-false-clear gate. This is the direct fix for the boil-the-ocean risk: we never try to "do the 800" in one move. 003b/003c can run in parallel with 003a once 002b lands. **Honest note (review):** slicing reduces *spec size and enables parallelism* — it does not reduce total work; the genuine de-risking is 002a (throwaway, gates an irreversible commit), not the 003 split.
3.5. **The disposition layer (004) composes the slices into the user-visible unit.** The slices produce per-check verdicts; 004 composes them into one per-loan auto-clear/exception decision — the integration the archetype slicing does *not* cover. It sits right after the engine slices and before the safety/audit/output features that all attach to a loan-level disposition.
4. **The engine slices come before the authoring UI (009).** The constitution and G3 say the engine earning trust is the prerequisite — a beautiful Author surface over an untrusted engine is theater. The PRD defers Author to v2 for exactly this reason; we hand-author with the SME until the engine is proven.
5. **Eval is sequenced *alongside* the engine, not after it.** The **already-built `p0/eval_synth` scorer** is what 002a uses (the spike does NOT wait on a later feature — the v0.3 numbering knot is fixed). Feature 005 is the *CI productionization* of that scorer, landing with the engine slices. Principle III makes eval a gate, not a phase. Every rules-touching feature (003a/b/c, 004, 009, 010a/b) promotes only through the zero-false-auto-clear gate. This is the single most important ordering invariant.
6. **Safety and audit (006–007) land before the Output surface (008)**, because the queue's entire value is that a human can *trust* an auto-clear and *trace* an exception. Output without the confidence gate and the audit chain underneath it would violate the two gates that protect the buyback number.
7. **Author and gating (009–010a/b) follow once the engine, eval, and audit are load-bearing** — the riskiest reversal (G4: customer-authored model vs Tavant-internal pipeline) is held until its prerequisites are green. Gating is cheaper than first thought: 615 SQL clauses already encode most of "which checks fire for which loan," so **010a honors the sheet** and **010b derives only the remainder.**
8. **The flywheel and real-loan eval (011–012) convert the directional accuracy story into the load-bearing one** — the pilot exit criterion. They depend on the audit/citation trail (cited outputs become draft labels) and on the external G1 gate, so they sit late.
9. **Multi-LOS is removed from the build arc** (was 013) — demoted to a v3 interface the 001b envelope is *ready for*, built only when a multi-LOS pilot is funded. We do not build it speculatively.

The throughline: **de-risk the compile bet with a throwaway spike, prove correct-by-construction determinism on the core one archetype slice at a time, compose into a per-loan disposition, gate every slice with eval, make it auditable, only then expand the surface area** — never let the periphery (extraction, LOS, multi-LOS, real-loan acquisition) hold the core hostage.

**Acknowledged tension the sequence does not fully resolve (review):** this is *trust-ordering* (engine earns trust before the Author surface is real). The thing that *won the room* was the **self-service authoring magic** (009), now ninth. A *demo-ordering* arc would front-load author-magic to convert the deal. We chose trust-ordering deliberately — a beautiful Author surface over an untrusted engine is theater, and the constitution backs engine-first — but the conflict is real and named in Tension 7. The mitigation is that the existing `example/` prototype already *shows* the authoring magic for demo purposes while the trustworthy engine is built underneath.

---

## Tensions flagged (per the constitution's "surface, don't silently diverge" mandate)

1. **009 / G4 — Author in the model or not (AMBER → now phased; see `output/AUTHORING-UX-DECISION.md`).** The authoring-UX decision splits the binary into a phase: **MVP (009a import + 009b guided) is customer-facing but Tavant-shaped** — the SME authors via their own spreadsheet + a guided UI, never a DSL or the compiler — which needs only the *cheap, reversible* half of G4 and **unblocks MVP authoring now.** The *expensive* full customer-authored model is deferred to **009c/v2**. **G4 must lock before 009c, not before 009a.** Principle VI satisfied without the irreversible commitment.

2. **Multi-LOS / G5 — positioning vs scope discipline (AMBER; feature demoted).** The positioning headlines "any LOS, independent referee," but Principle IV says assume the periphery and the PRD defers multi-LOS to v3. Per the contrarian review, the *feature* (was 013) is **removed from the build arc** — the 001b envelope stays N-source-ready, but reconciliation is built only when funded. **Decision still owed: is the pilot single-LOS (almost certainly yes)?** The positioning must not write a check the MVP can't cash.

3. **006 / G2 — the confidence floor is a magic number until calibrated (RED).** The 0.80 floor cannot catch *confidently-wrong* extractions until Touchless confidence is characterized on real docs. 006 ships the *mechanism*; the *calibration* is gated on an external dependency. Scope determinism honestly as "deterministic given the extracted inputs" until then (Blocker 1).

4. **012 / G1 — the false-auto-clear ≈ 0 claim is synthetic until real loans land (RED).** The eval is correct *by construction*, but the population false-clear rate waits on Kayla's expert-labeled, independent-path loans. The harness absorbs them with no rework — but until 012 runs, the safety claim is the regression floor, not the real-world number. Do not over-claim. Principle III's honest-residual mandate.

5. **003c / doc-vs-doc reconciliation — CLOSED by `003d` (2026-07-23, GREEN).** `003c`'s own spec found that `taxonomy.json`'s real MISMATCH examples — 1003-vs-VOE employment dates, 1003-vs-title-commitment vesting, 1003-vs-1008/DU loan purpose — are predominantly **doc-vs-doc** comparisons (two independently-extracted document values), not doc-vs-system, and explicitly declined to build it (its own FR-005). `specs/003d-engine-doc-vs-doc-reconcile-checks/` built the real fix: two new check kinds, `agree_doc_categorical`/`agree_doc_numeric`, that compare two independently-named document fields directly — never touching `SourceValue.sources{}`, so `001b`'s source-independence guard for the pre-existing doc-vs-system kinds is untouched. `QC` phase (not `RECONCILE`): a doc-vs-doc mismatch is a genuine defect in the closing package itself, resolving `FAIL`/`EXCEPTION`, not the informational `FLAG` doc-vs-system disagreement produces. Phase 1 (shipped) hand-authored all 5 known doc-vs-doc defects in `ruleset_defects.py` at zero LLM cost — all 25 known planted defects across the 5 synthetic loans now resolve correctly (`test_wired_checks_catch_all_25_known_defects`), up from 20/25. Phase 2 (recompiling the full 8,442-row rulebook to find the estimated 14-26 additional real doc-vs-doc conditions at scale) remains a separate, unscheduled, future spend decision — the engine capability now exists; applying it broadly to the real rulebook is not yet done.

5b. *(renumbered from a duplicate "5." 2026-07-26, spec audit — specs citing "Tension #5" mean the doc-vs-doc tension above)* **011 / Q2 — the moat is contingent on a data-rights clause lenders resist (RED).** The label-confirmation flywheel compounds across customers only with a contractual right to learn from anonymized cross-customer outcomes. Without it, 011 is single-customer and the primary moat changes shape. A contract term, not a build — but it gates the moat thesis (PRD §9).

6. **002a / the compile bet itself is unproven at scale (RED — highest-risk item).** The entire "compile, then run" differentiation assumes an LLM can turn the real AMQ workbook into a *correct* signed ruleset — and read each row the way the lender *means* it. G3 only tested the runtime-LLM side. If 002a finds the compiler is wrong often, misreads intent, or needs near-total SME rewriting (sign-off theater inverted — the human compiles, not the LLM), the product's central premise needs rethinking. This is why 002a is a throwaway spike sequenced *before* the full compiler (002b), and why its metric now includes **interpretation fidelity** (an SME rules review), not just runnability — fail cheap, before building on the assumption. Principle II.

7. **Trust-ordering vs demo-ordering (AMBER — new, from contrarian review).** The roadmap sequences the engine to *earn trust* before the Author surface (009) is real — engine-first, constitution-backed. But the feature that *won the room* (self-service authoring) is therefore ninth. A demo-driven arc would front-load the authoring magic to convert the design partner. **The conflict:** what makes the product *trustworthy* (engine-first) is not what makes the demo *seductive* (author-first). We chose trust-ordering deliberately, with the `example/` prototype carrying the demo magic in the interim — but if a pilot hinges on the live authoring experience sooner, the sequence may need to bring a thin slice of 009 forward. Named, not silently resolved.

8. **Tension 8 — NL-on-the-gate vs the sign-off-theater hole (AMBER → RED on the criteria layer; from the authoring-UX decision).** The feature most likely to *delight* (type-it-in-English authoring, 009c) targets the exact field — the **criteria gate** — where a wrong-but-plausible artifact most easily survives SME sign-off, because the SME cannot fluently read the gate they are signing. An authoring-time LLM error is *not* the G3 runtime horror (it faces three catch points: sign-off, the eval gate, 002a's review) — but the gate is the one task that defeats all three. **Decision owed:** does NL ever emit the gate as free text, or is it permanently confined to *proposing into* a catalog-constrained control the SME confirms value-by-value? **Recommendation: the latter, hard** — a signed-off product boundary before 009c is specced, not discovered in build. Distinct from Tension 1 (*whether* customer-facing) and Tension 7 (*ordering*).

9. **Conditional-applicability gating + operator-direction bug (Phase 1 IMPLEMENTED 2026-07-25 —
   see below; specced 2026-07-24, revised 2026-07-24 after real-data testing, from SME review call, see
   `output/SME-REVIEW-FINDINGS-2026-07-24.md`, `output/RULE-COMPILER-FIX-PLAN-2026-07-24.md`, and
   `g-learn-hidden-precondition-extraction`).** `010a`'s program gate (Fannie/Freddie/VA/etc.) is
   coarse; it does not gate by *loan-specific facts* (gift used, condo, co-borrower...). **Reversed,
   not merely revised**: the AMQ sheet's own "Question Criteria by Questions" column, first assumed
   undecodable live on the call, turned out to be a structured `QuestionID == N && AnswerText == "..."`
   expression — clustering every row sharing the same `N` reconstructs the real answer vocabulary
   with zero client-supplied key, zero LLM (24 distinct IDs, 3,255 of 5,520 real Post-Closing rows).
   This became `002f-precondition-ontology-layer`'s Layer 0, the majority-case, zero-risk path; a
   defect_text-based Layer 1 and a Guide-grounded, mandatory-human-reviewed Layer 2 handle the
   genuine residual. **`002e-conditional-applicability-gating`** is now the mortgage-qc-prod-specific
   consumer of `002f`'s output (`Check.applies_if`), not the extraction mechanism itself.
   A separate, mechanical compiler bug (operator-direction inversion in `ratio_threshold` checks,
   45/495 suspects) was found in the same review and specced as **`002d-operator-consistency-gate`**
   (cross-validated against the same Layer-2 grounding-verification research, no design change).
   Domain knowledge (a Fannie Selling Guide) may only decide **whether an existing rule applies**,
   never originate new rule content or cause additional questions/rules to fire — enforced not by
   forbidding Guide use outright, but by `002f`'s Layer 2 requiring mandatory human sign-off on every
   single Guide-derived proposal, regardless of confidence.
   **Phase 1 shipped 2026-07-25**: all three specs (`002d`/`002e`/`002f`) are implemented — `211`
   tests passing at ship time (218 as of 2026-07-26 — the KB-store/Selling-Guide-ingestion tests
   added later; count moves, all green), zero regressions (`pytest p0/tests -v`). `002d`: `SYSTEM_PROMPT` PASS-condition
   convention + `operator_consistency_check()`, validated against the real ruleset (all 45 known
   suspects reproduced, 3 additional same-pattern catches, wired into `assemble_ruleset` to exclude
   flagged checks from auto-sign). `002f`: `p0/ontology_extraction/` standalone package — Layer 0
   reproduces the real 24-entry/3,255-row Retail Post-Closing result exactly; Layer 1/Layer 2 (KB
   grounding-verification + mandatory-human-review override + Onity-adopted retry/coverage-floor
   mechanisms) proven against constructed cases; zero `qc_engine` imports outside the one
   FR-010-sanctioned exception (`layer2_grounded.py`, statically enforced). `002e`: `Check.applies_if`
   + `engine.py`'s new pre-kind-dispatch gate + `catalog.py` referential-integrity extension, proven
   against all 6 Acceptance Scenarios (compound AND, `in`, `between`, unknown-field→`NEEDS_REVIEW`,
   definite-fail-priority-over-unknown) AND against the real loan 01 fixture — SC-001's exact
   SME-confirmed case (`gift_funds_used=false` → the gift-fund check now resolves `NOT_APPLICABLE`
   instead of an unresolved gap). **Still open, each spec's own explicit Phase 2, not part of Phase 1's
   scope**: a full/partial recompile of the 5,520-row Retail workbook through all three `002f` layers
   at scale (currently proven on the real fixture + constructed cases, not yet run end-to-end against
   the whole sheet) — a separate, later, real-Bedrock-spend decision. **Also decided 2026-07-24, not
   yet executed**: this project now compiles exclusively from `PF and PC Sept 2025 AMQs - Retail.xlsx`;
   the `Private Bank Oct 2025 PC and Nov 2025 PF.xlsx` workbook and all previously-compiled artifacts
   mixing both workbooks are to be excluded/discarded — tracked as a pending housekeeping action, not
   yet performed.
   **Phase 2 now scoped (2026-07-26): `002g-canonical-loan-fact-vocabulary`.** Two real gaps found by
   direct code inspection, not assumption: (1) `compile_llm.py` has zero references to
   `ontology_extraction`/`run_layers` — `002f`'s tested pipeline has never actually populated a real
   compiled check's `applies_if`; no `applies_if` exists anywhere outside the engine/schema and its
   tests (corrected 2026-07-26 — an earlier revision wrongly said `ruleset_defects.py` carries
   hand-authored ones; it carries zero). (2) `layer1_extraction.py` lets the LLM invent a fresh `field_name` per row
   with no registry or dedup — two rows about the same real fact ("gift funds used") could extract as
   two different field names, so two checks could, in principle, disagree about the same loan's own
   nature. `002g` closes both: wires `run_layers()` into the real compiler, and adds a signed,
   versioned canonical-fact vocabulary (mirroring `002c`'s KB corpus sign-off shape) that a
   `field_name` must resolve against before it can gate a real check. Scoped narrowly and
   deliberately: facts derivable from fields the catalog already extracts only (gift-funds-shaped
   facts); facts needing new external reference data (jumbo conforming-limit tables, CFPB QM tests)
   are explicitly out of scope, tracked as a later, separate spec once that reference data is actually
   sourced. Research grounding: DMN (not SBVR — checked directly, SBVR has shipped no update since
   2008) as the "vocabulary → auditable decision" precedent; MISMO's own Logical Data Dictionary as
   the vocabulary-alignment source; a real, directly-tested mortgage-domain comparison
   ([PostgreSQL vs Pinecone vs OWL Ontology](https://pub.towardsai.net/postgresql-vs-pinecone-vs-owl-ontology-i-tested-all-three-as-ai-agent-backends-none-of-them-won-f5c03b321cb0))
   showing ontology-with-formal-constraints beating a vector DB and a SQL agent on deterministic,
   auditable threshold checks; and Fannie Mae Lender Letter LL-2026-04 (verified directly, effective
   **2026-08-08**), which explicitly names quality control in its AI-audit-trail mandate — a real,
   dated deadline, not just supporting theory. Explicitly does **not** adopt a formal OWL/DL or SHACL
   reasoner — `engine.py` stays the same flat, deterministic Python it already is; only the
   vocabulary/naming discipline is borrowed from that research, not the reasoner machinery (same
   veto reasoning as `002f`'s own audit-trail-over-opacity stance).
   **Sequencing note (added 2026-07-24, `g-os-judge` review; status updated 2026-07-25)**: measuring
   `002f` Layer 0's real-world defect impact (not just structural coverage) requires a trustworthy
   *recompiled* ruleset to test against — `002d` shipping is necessary but not sufficient; the
   currently-*deployed* `post_closing_only_ruleset.json` was compiled before `002d`/`002e` existed and
   still mixes Private Bank data, so it remains an invalid test instrument until the Retail-only
   recompile (above) actually runs with the new compiler in place.

> **Declined from the review (recorded for honesty):** the contrarian argued the compile-then-run spine is "over-protected past what G3 justifies" since Sonnet passed D1/D2. We decline this framing: in *regulated* mortgage QC, **auditability alone** — handing an examiner the exact Decimal derivation — justifies compiling, independent of variance or cost (THESIS Point 3; "if they don't understand how you calculated that number, you buy back the loan"). The 002a-gates-002b discipline already prevents over-building on an unproven bet; we do not need to also defer the spine behind the real-loan eval (012), which is itself gated on loans that may never arrive.

---

*End of ROADMAP v0.5 (DRAFT). Each entry is ready for `/speckit-specify`. The architect
translates the in-scope items into EARS technical criteria and the data-contract interface specs
for Touchless and the LOS connector. Constitution v1.1.0 governs; tensions above require human
decision before the affected features (002a spike, 009c NL authoring, multi-LOS) are committed.*
