# Feature Specification: Domain-Knowledge-Grounded Rule Compilation & Intake Workflow

**Feature Branch**: `002c-domain-knowledge-grounded-compilation`
**Created**: 2026-07-20
**Status**: Implemented (2026-07-20 — T001–T036, real Bedrock proof run; header corrected from stale "Draft" 2026-07-26, spec audit. Storage layer since superseded — see plan.md's 2026-07-26 post-hoc note)
**Input**: User description (across two turns, 2026-07-20): "during the llm parsing of the rules
into rule engine, the llm must do its own research and analysis to these mortgage terms, rules,
regulations and mortgage qa/qc process to enrich and add context to the meaning... we need an
agentic system with agents that can research, analysis and fetch these into context, and spawn
other agents arming with the research and understanding to parse the rules individually" —
subsequently refined after research to: a one-time, versioned, per-program-type (VA/FHA/USDA/
Conventional/Jumbo/etc.) knowledge base, appendable when new rules/guidance arrive; multi-model
"agent judges" validating compiled rules so only exceptions/disagreements need SME review; plus a
researched, designed end-to-end intake workflow for first-time parsing of an uploaded ruleset/
guidance/policy document set.

**Governs**: `output/ROADMAP.md` (new entry, sequenced alongside `002b`), `.specify/memory/
constitution.md` Principle II (compile, then run — this feature extends the compile step with a
grounding sub-stage, still entirely config-time, never runtime), Principle III (eval is
foundational — the judge panel is a triage mechanism, not a substitute for real-outcome eval).
Consumes `010a-program-applicability-gating`'s 6 confirmed programs (FHA/VA/USDA/Freddie Mac/
Fannie Mae/SONYMA) as the knowledge base's category segmentation.

**Depends on**: `001a-field-catalog` (implemented), `002b-ruleset-compiler-pipeline` (implemented —
this feature grounds, does not replace, `compile_llm.py`'s per-row compile call), `010a-program-
applicability-gating` (implemented — supplies the per-program category boundaries the KB is
segmented by).

**Consumed by (2026-07-24)**: `002f-precondition-ontology-layer`'s Layer 2 reuses this feature's
`knowledge_base.py`/`judge_panel.py` directly (imported, not re-implemented) for the narrower use
case of proposing a loan-fact *applicability* condition a rulebook row doesn't itself state — with
one deliberate, explicit override of this spec's own FR-008/US4 default: a Layer-2 proposal is
**never** auto-approved regardless of judge unanimity/confidence, unlike this spec's standard
unanimous-and-confident auto-approve path. The asymmetry: a wrong grounded *interpretation* here
(this spec's normal case) still produces a check that fires and gets reviewed; a wrong grounded
*applicability* condition (`002f`'s Layer 2) produces a check that silently never fires at all — the
stricter failure mode justifies the stricter override, for that one consumer only. This spec's own
default policy is unchanged for every other caller.

**Research this spec is built on** (two rounds, both cited inline below, full reports not
separately filed — see this spec's own citations): (1) RAG-for-rule-extraction literature,
multi-agent research-architecture cost/failure-mode data, static-vs-live-RAG reproducibility
guidance; (2) multi-model LLM-judge reliability data, versioned/incremental RAG architecture, and
a concrete reference intake pipeline (De Jure, arXiv 2604.02276).

---

## Why this feature exists, and why the originally-proposed architecture was revised

The original ask — spawn research agents that fetch live web context per rule row, then hand off to
parsing agents "armed with" that research — was evaluated against this project's own non-negotiable
(Principle II, THESIS.md): the compiled ruleset's derivation must be reproducible and auditable
enough that a regulator can be shown exactly how a rule was derived. Research found:

- **No published architecture, in mortgage or any other regulated industry, documents a live
  multi-agent-research-per-item pipeline feeding a compile-time rule generator with audit
  requirements.** This would be a genuinely novel, unproven design.
- **Live web retrieval breaks reproducibility by construction** — the same query against a live
  source can return different content over time, before the LLM's own stochasticity is even
  considered (UCSC OSPO; FlowHunt's non-determinism analysis: "you cannot trace a specific output
  back to its causes with certainty" under non-determinism).
- **Cost**: agentic RAG runs ~3–10x the cost of single-shot RAG per item (Tensoria); Anthropic's own
  published multi-agent-system figures show ~15x token usage vs. a single call. At this project's
  real scale (~7,000+ real rule rows, `output/RULE-PROGRAM-GATING-FINDINGS.md`), a fresh-research-
  agent-per-row design plausibly costs tens of thousands of dollars — against this project's own
  THESIS.md figure of $700–$3,500 for a *single* full-scale LLM run today.

**What research supports instead, and what this spec builds**: a **static, versioned, per-program-
category knowledge base**, built once (and later updated incrementally, never rebuilt from scratch)
by research agents whose output is **SME-reviewed and signed off before any rule ever compiles
against it** — the same sign-off discipline the ruleset itself already gets. Every compiled rule is
then grounded against this **frozen, version-anchored** corpus, not live search. This is confirmed,
by direct research, to be the design pattern used in every regulated-industry RAG system found
(Atlan's "governed retrieval pipeline," VersionRAG's version-anchored graph) — not a compromise, the
established answer.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A versioned, per-program knowledge base exists before any rule compiles against it (Priority: P1)

Research agents build a knowledge base — regulation summaries (TILA/ECOA/HMDA/FCRA/ESIGN/ATR-QM),
Fannie Mae/Freddie Mac Selling Guide excerpts, HUD Handbook 4000.1 sections, USDA/RHS and VA
guaranty guidance, a QC glossary — segmented by the 6 confirmed programs (`010a`). An SME reviews
and signs off the corpus, exactly as an SME signs off a compiled ruleset today, before any rule ever
retrieves from it.

**Why this priority**: This is the foundation everything else in this spec depends on — grounding,
judging, and the intake workflow all assume a signed, versioned KB already exists.

**Independent Test**: Build a KB for one program (e.g. FHA) from a small, real set of source
documents; confirm every stored section carries a content fingerprint (SHA-256) and a KB version
identifier; confirm the KB cannot be marked "usable" without a recorded SME sign-off, mirroring
`Ruleset`'s existing `RuleProvenance` mechanism.

**Acceptance Scenarios**:

1. **Given** a set of source documents for one program, **When** the KB-build step runs, **Then**
   it produces a versioned, content-fingerprinted, program-scoped corpus — not a single monolithic
   store spanning all programs.
2. **Given** an unsigned KB build, **When** a compile step attempts to ground against it, **Then**
   it is rejected — the same "no sign-off, no use" discipline `002b`'s `Ruleset` already enforces.

---

### User Story 2 - The knowledge base updates incrementally, without breaking past compiled rules (Priority: P1)

When new source documents arrive, or an existing document is revised, the KB updates at the
**section level** (VersionRAG-style version-sequence graph, not a flat overwrite) — unchanged
sections keep their existing version anchor; changed/new sections get a new one. A rule compiled
against KB version N continues to correctly cite version N even after the KB advances to version
N+1.

**Why this priority**: Without this, every KB update would force re-deriving (and re-signing) every
previously-compiled rule that touched the changed material — unworkable at real scale, and directly
threatens the audit story (a rule's derivation must remain stable once signed).

**Independent Test**: Build a KB version N; compile a rule grounded against a specific section;
update that section's source document (producing version N+1); confirm the already-compiled rule's
recorded grounding still resolves to version N's content, byte-for-byte, not N+1's.

**Acceptance Scenarios**:

1. **Given** a KB update where only some sections changed, **When** the update runs, **Then** only
   the changed/new sections are re-fingerprinted and re-embedded — unchanged sections are untouched.
2. **Given** a rule compiled and signed against KB version N, **When** the KB later advances to
   version N+1, **Then** the signed rule's recorded provenance still resolves to version N's exact
   content.

---

### User Story 3 - Each compiled rule is grounded against its own program's frozen KB (Priority: P1)

`002b`'s `compile_llm.py` gains a grounding sub-step: before the Bedrock compile call, retrieve the
relevant KB section(s) for the row's program (from `010a`'s Exception Code prefix) and topic, and
include them in the compile prompt alongside the existing field-catalog context — using **standard
retrieval against the frozen corpus, never a live agent call**.

**Why this priority**: This is the actual grounding capability the original request was about —
resolving the kind of ambiguity `002a`'s spike already found (3 of 24 rows flagged ambiguous), now
with real regulatory/guide context instead of the row's bare text alone.

**Independent Test**: Compile a real row known to reference a specific regulatory concept (e.g. an
ATR-QM row); confirm the compile prompt includes the retrieved KB excerpt; confirm the resulting
`CompiledCheckDraft` records which KB version/section grounded it.

**Acceptance Scenarios**:

1. **Given** a row tagged for a program with an existing signed KB, **When** it compiles, **Then**
   the retrieved KB context is included in the prompt and recorded on the resulting draft.
2. **Given** a row tagged for a program with no KB yet built, **When** it compiles, **Then** it
   falls back to `002b`'s existing ungrounded behavior — never blocks the batch.

---

### User Story 4 - A multi-model judge panel triages which compiled rules need SME review (Priority: P1)

Each compiled rule is scored by 2+ judge models from a **different model family than the compiler**
against the source text and its KB grounding. Judges agreeing with each other and the compile
auto-approve; **any disagreement, or a judge's own confidence below a tunable threshold, escalates**
to a human SME — never auto-approved on a majority/plurality basis.

**Why this priority**: This is the mechanism that makes real-scale (~7,000-row) review feasible —
but research found real limits on how much to trust it (CompliBench: even strong models hit only
77.7% compliance-violation-detection accuracy; "Nine Judges, Two Effective Votes": a large judge
panel yields only ~2.2 truly independent votes, so more judges ≠ proportionally more confidence).

**Why "any disagreement escalates," not majority vote**: given the correlated-error finding above, a
majority-rules scheme risks auto-approving a rule two correlated models are both wrong about. The
conservative default matches this project's own SAFE-gate posture (a false auto-clear is worse than
an unnecessary human review) — escalate more, not less, until real numbers exist.

**Independent Test**: Construct a compiled rule with two judge models agreeing → confirm
auto-approve. Construct one with judges disagreeing → confirm escalation to the SME queue, with the
disagreement itself recorded (not silently resolved either direction).

**Acceptance Scenarios**:

1. **Given** unanimous judge agreement with the compile, **When** the panel runs, **Then** the rule
   auto-approves — no SME review required.
2. **Given** any judge disagreement, or any judge's confidence below the configured threshold,
   **When** the panel runs, **Then** the rule routes to the SME exception queue, with every judge's
   individual verdict and reasoning preserved (not just a pass/fail flag).
3. **Given** the full compiled batch, **When** scored, **Then** the fraction auto-approved vs.
   escalated is measured and reported — **not assumed from literature** (no source found a real
   auto-approve percentage for this exact task shape; treat the first real pilot batch as the
   measurement, not a validation of a pre-assumed number).

---

### User Story 5 - The full intake workflow orchestrates all of the above, end to end (Priority: P2)

From a user uploading a new document set (an AMQ workbook, or a new investor guideline) through to a
signed, versioned, deployable ruleset, the system runs: upload & fingerprint → normalize & segment →
classify & gate on novelty → build/update the relevant program-scoped KB → extract (US3) → judge
(US4) → referential-integrity/conflict screen (existing `002b` mechanism) → SME review of the
exception queue only → sign-off & version-lock → deploy.

**Why this priority**: Lower priority than US1–4 because it's an orchestration of already-specified
mechanisms, not new decision logic — but it's the actual user-facing shape of "first-time parsing,"
and unsequenced work here risks each mechanism being built without a coherent handoff between them.

**Independent Test**: Walk a small, real document set through every stage; confirm a document type
never seen before halts at the classify-and-gate stage (not silently processed); confirm the final
artifact is a signed ruleset with every compiled check version-anchored to the exact KB version(s)
that grounded it.

**Acceptance Scenarios**:

1. **Given** a document type never seen before, **When** intake runs, **Then** it halts for
   mandatory human triage before any extraction happens — never auto-processed.
2. **Given** a known document type and an existing signed KB for its program, **When** intake runs
   end to end, **Then** the output is a signed, version-locked ruleset with full provenance from
   source document through KB grounding through judge verdicts to SME sign-off.

---

### Edge Cases

- **Judges from "different model families" still share correlated blind spots** (research finding,
  not resolved by this feature): the judge panel is explicitly a **cost/triage mechanism**, not a
  substitute for real-outcome evaluation. `005`'s eventual eval-harness-as-CI-gate remains the
  authority on actual correctness; a judge-panel auto-approval is not itself proof of correctness.
- **No literature-standard confidence threshold or voting scheme exists** for this exact task shape
  — the threshold MUST be a tunable, empirically-set parameter, not a hardcoded "industry standard"
  number (none was found; explicitly flagged as an open question by the research itself).
- **A KB section update that changes a definition an already-signed rule depended on**: the signed
  rule's provenance still resolves to the old version (US2) — this feature does NOT auto-flag
  downstream rules for re-review when their grounding material changes; that's a distinct future
  capability (a "grounding went stale" detector), named here as out of scope, not silently assumed
  solved.
- **What happens if two research agents building the KB disagree on a regulatory interpretation
  during the one-time build?** Not resolved by this feature — the SME sign-off step (US1) is the
  backstop; this feature does not attempt automated conflict-resolution during KB construction
  itself.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST build the knowledge base as a versioned, content-fingerprinted,
  per-program-category corpus (segmented by `010a`'s 6 confirmed programs), not a single monolithic
  store.
- **FR-002**: The system MUST require SME sign-off on a KB version before any compile step may
  ground against it.
- **FR-003**: The system MUST support incremental KB updates at the section level — unchanged
  sections retain their version anchor; only changed/new sections are re-processed.
- **FR-004**: The system MUST version-anchor every compiled rule to the exact KB version(s) that
  grounded it, such that a later KB update never retroactively changes an already-signed rule's
  recorded derivation.
- **FR-005**: The system MUST ground each row's compile call using standard retrieval against the
  frozen, signed KB — MUST NOT invoke a live web-search or research agent in the per-row compile
  path.
- **FR-006**: The system MUST fall back to `002b`'s existing ungrounded compile behavior when no
  signed KB exists yet for a row's program — grounding is additive, never a hard blocker.
- **FR-007**: The system MUST score each compiled rule with 2+ judge models from a different model
  family than the compiling model.
- **FR-008**: The system MUST escalate to human SME review on ANY judge disagreement or any judge's
  confidence below a configured threshold — MUST NOT auto-approve on a simple majority/plurality
  basis, given the correlated-error risk research found.
- **FR-009**: The system MUST preserve every individual judge's verdict and reasoning on an
  escalated rule, not just an aggregate pass/fail flag.
- **FR-010**: The system MUST measure (not assume) the real auto-approve/escalate split on its first
  pilot batch, and MUST NOT present a literature-derived percentage as a validated production number.
- **FR-011**: The intake workflow MUST halt for mandatory human triage on any document type not
  previously seen — MUST NOT silently auto-process an unfamiliar document type.
- **FR-012**: The final output of a full intake run MUST be a signed, version-locked ruleset whose
  every compiled check carries full provenance: source document → KB grounding version → judge
  verdicts → SME sign-off.
- **FR-013**: This feature MUST NOT replace `005`'s eventual eval-harness-as-CI-gate — judge-panel
  auto-approval is triage for human-review load, not a correctness proof.
- **FR-014**: This feature MUST NOT invent an automated "grounding went stale" re-review trigger for
  rules whose source KB material later changes — named as a distinct, unbuilt future capability.
- **FR-015**: This feature's grounding retrieval (FR-005) MUST NEVER be the origin of a threshold,
  date, percentage, or condition that is not itself already present in the source AMQ row it grounds
  — grounding may only clarify or cite the regulation an existing row-stated condition traces to, per
  Principle II's "never freelances" boundary and this codebase's own `compile_llm.py` `SYSTEM_PROMPT`
  discipline ("NEVER INVENT A NUMBER, DATE, OR CONDITION"). This is stated here as a first-class,
  testable requirement — added 2026-07-27, constitution-alignment audit — because `002e`/`002f` both
  already cite "the never-invent discipline" as an established rule, but this spec (the one KB-grounded
  compile path they're citing it from) never previously wrote it down as its own FR.

### Key Entities

- **KnowledgeBaseCorpus** (new): program-scoped (one of the 6 confirmed programs), versioned,
  content-fingerprinted (SHA-256 per section), SME-signed before use — mirrors `Ruleset`'s existing
  `RuleProvenance`/sign-off shape.
- **KBSection** (new): one fingerprinted unit within a corpus version; a KB update only re-fingerprints
  changed/new sections, per US2.
- **GroundingRecord** (new): attached to a `CompiledCheckDraft` (extends `002b`'s existing entity) —
  records which KB version/section(s) grounded a given compile.
- **JudgeVerdict** (new): one judge model's score/reasoning on one compiled rule; a rule carries one
  `JudgeVerdict` per judge, not a single aggregate.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A KB version cannot be used for grounding without a recorded SME sign-off — verified
  by test.
- **SC-002**: An incremental KB update re-processes only changed/new sections; a rule signed against
  a prior KB version continues to resolve to that exact prior content after the update.
- **SC-003**: Zero live web-search or research-agent calls occur in the per-row compile path — the
  compile step's only external calls are the single compiling LLM call plus judge-panel calls,
  matching `002b`'s existing "compile-time-only" cost/latency profile, not the ~3–15x agentic-RAG
  multiplier research found for live-research-per-item designs.
- **SC-004**: Every escalation to the SME queue carries the specific disagreement or low-confidence
  signal that triggered it — zero instances of an opaque "needs review" with no reasoning attached.
- **SC-005**: A document type never seen before halts intake for human triage in 100% of constructed
  test cases — zero silent auto-processing of an unfamiliar type.
- **SC-006**: This spec's own text names the judge panel as triage (not correctness proof), the
  unvalidated auto-approve percentage, and the "no stale-grounding re-review" gap as explicit,
  inspectable scope boundaries.

## Assumptions

- The KB-first architecture (vs. the alternative De Jure-style interleaved, no-separate-KB design
  found by research) is the explicit, informed choice for this feature — chosen for stronger
  per-rule auditability (a regulator can be shown the exact pinned KB version behind any rule),
  accepting a slower stand-up cost (KB must exist before compiling starts) as the tradeoff. No
  source directly compares the two approaches; this is a judgment call, not a literature-settled one.
- The judge-panel confidence threshold and escalation scheme are explicitly NOT fixed by this spec —
  they are tunable parameters to be set from a real pilot batch's measured results (FR-010), not a
  literature-derived constant.
- This feature does not build the KB-build research-agent orchestration's own implementation detail
  (which agent framework, how many parallel research agents, etc.) — that is a `plan.md`-level
  design decision, informed by, but not fixed in, this spec.
- `005` (eval-harness-as-CI-gate) does not exist yet; this feature's judge panel is a real, useful
  triage mechanism in the meantime, but explicitly not a replacement for `005` once it exists
  (FR-013).
- `009a`/`009b`/`009c` (authoring/import UI) do not exist yet; the intake workflow (US5) is specified
  as a backend process — its user-facing surface is a future UI feature, not built here.
