# Feature Specification: Precondition Ontology Layer (modular, reusable)

**Feature Branch**: `002f-precondition-ontology-layer`
**Created**: 2026-07-24
**Status**: Implemented — Phase 1 (2026-07-25; standalone package proven, but `run_layers()` uncalled by the real compiler until `002g`; header corrected from stale "Draft" 2026-07-26, spec audit)
**Input**: User direction, continuing the SME-call/grill-me thread: "lets document the ontology way
layer0/1/2 and we will start specing this... we should spec a ontology layer to extract that can be
modular that can be reuse with other project." Supersedes `002e`'s original single-layer design
(`applies_if` extracted from `defect_text` only) with the full three-layer sequencing discovered and
validated against the real Retail AMQ workbook this session — see `g-learn-hidden-precondition-
extraction` and `output/RULE-COMPILER-FIX-PLAN-2026-07-24.md`.

**Governs**: `output/ROADMAP.md` Tension 9. Feeds `002e-conditional-applicability-gating` (the
mortgage-qc-prod-specific consumer — `Check.applies_if`) as its primary caller, but is scoped and
built as a **standalone capability**, not mortgage-specific logic, per explicit user direction that
it be reusable by other projects. **Update 2026-07-26**: `run_layers()` is called only by this
package's own tests as of this date — `002g-canonical-loan-fact-vocabulary` is the spec that
actually wires it into `compile_llm.py` for the first time, plus adds a canonical-fact registry so
independently-extracted `field_name`s for the same real fact converge instead of silently diverging.
**Depends on**: `002c-domain-knowledge-grounded-compilation` (**implemented** — `002f`'s Layer 2
reuses `knowledge_base.py`'s `retrieve()` and `judge_panel.py`'s `escalate_or_approve()` directly,
rather than re-specifying grounding/judging infrastructure that already exists, tested, and proven
against a real Bedrock run).

**Research this spec is built on** (cited inline below):
1. [ComplianceNLP: Knowledge-Graph-Augmented RAG for Multi-Framework Regulatory Gap Detection](https://arxiv.org/html/2604.23585)
2. [Transfer Learning for Deontic Rule Classification: The Case Study of the GDPR](https://doi.org/10.3233/FAIA220467) (Liga et al., JURIX 2022 — link corrected 2026-07-26 to the verified DOI; the original ResearchGate URL's numeric ID looked mistyped and RG blocks verification)
3. [Detecting Hallucinations in RAG through Grounding-Aware Sensitivity by Perturbation (GASP)](https://arxiv.org/pdf/2607.04223)
4. [An Automated Framework for the Extraction of Semantic Legal Metadata from Legal Texts](https://arxiv.org/pdf/2001.11245)
5. **In-portfolio prior art**: `project/Onity`'s "Ontology Graph Mapping" pipeline
   (`specs/ontology-graph-mapping-research-v2.md`) — a real, actively-specced system solving a
   *different* problem (LOS-export-to-boarding-template schema matching, not rule applicability) with
   the *same underlying shape*: deterministic structural clustering first (its Stage 1 entity
   clustering, regex prefix/suffix patterns, zero LLM), an LLM invoked only as a tiebreaker on
   genuinely ambiguous cases (its Stage 7, gated to ≤30 calls per run), and certain categories
   permanently floored at mandatory-human-review regardless of confidence (its `always_review`
   category, Stage 8 Rule 3 — "tier = MED, never auto-approve"). Independently arrived at, not
   borrowed from the research above — real, additional validation that this exact architecture shape
   (cheap-deterministic → targeted-LLM-tiebreak → hard-floored trust tiers) recurs across unrelated
   problem domains.

---

## Why this feature exists, and why it is a separate spec from `002e`

`002e` asks "how does a compiled check express a loan-fact precondition." This spec answers a
narrower, harder, and more general question: **where does that precondition's *content* come from,
and how do we know it's trustworthy** — and does so as a domain-agnostic layer, not mortgage-specific
code, because the underlying problem (a rule whose applicability depends on an upstream answer that
may or may not be stated explicitly in the same document) recurs in any rules-from-a-workbook
compilation problem, not just AMQ rows.

Real evidence, gathered directly against the one workbook this project now exclusively compiles
(`demo/rules/PF and PC Sept 2025 AMQs - Retail.xlsx`), shows the problem has **three distinct shapes**,
requiring three different sourcing strategies, not one:

- **3,255 of 5,520** Post-Closing rows carry a `Question Criteria by Questions` expression of the form
  `QuestionID == N && AnswerText == "..."` — structured, but only decodable by clustering across every
  row that references the same `N` (a single row's `N` looks like meaningless bookkeeping; the
  aggregate answer-vocabulary across all rows sharing it is not). Confirmed: **24 distinct IDs**,
  each with a small, coherent answer vocabulary, covering 3,255 rows — reconstructed entirely from
  the data, zero LLM, zero external knowledge.
- A further subset of rows (not yet exhaustively counted) state or clearly imply their own
  precondition directly in `defect_text` (the gift-letter row's own question text, "Were all gift
  and/or grant fund requirements met?", already self-signals its topic).
- A residual (**253 rows** in the Post-Closing sheet carry neither gating column at all) — spot-
  checked and found to be **mostly genuinely unconditional**, not disguised hidden-precondition cases;
  the true "needs external domain knowledge" residual is smaller than the SME call's original worry
  assumed.

Published research on the identical underlying problem (regulatory-gap detection with implicit
obligations and multi-hop cross-references, source 1) reports **extraction accuracy falling from
97.1% at 0 cross-reference hops to 84.6% at 3+ hops** — a direct, numeric argument for exhausting the
cheapest, most verifiable layer first, not reaching for external knowledge by default.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Layer 0: an opaque cross-reference column is decoded by clustering, not assumed undecodable (Priority: P1)

Given a tabular rule source with a column expressing a dependency on another row/question (any
syntactic form — not hardcoded to the `QuestionID == N && AnswerText == "..."` shape found in this
project's own data), the ontology layer clusters every row referencing the same dependency key and
reconstructs the key's full, real answer vocabulary and dependent-row set — a decoded "ontology" —
using zero LLM calls and zero external knowledge.

**Why this priority**: This is the highest-yield, zero-risk, zero-cost layer — it should always run
first and its coverage should be measured before any LLM/external-knowledge layer is invoked.

**Independent Test**: Feed the real Retail Post-Closing rows through the clustering step; confirm it
reproduces the 24-ID, 3,255-row result independently (not by re-reading the number from this spec).

**Acceptance Scenarios**:

1. **Given** a set of rows where multiple rows share the same dependency-key value, **When** Layer 0
   runs, **Then** it produces one ontology entry per distinct key, listing every answer value and
   every dependent row seen for that key anywhere in the input set.
2. **Given** a dependency-key expression syntax the layer has not been told about in advance (e.g. a
   different delimiter or field order than this project's own data), **When** Layer 0 encounters a
   row it cannot parse against its configured pattern(s), **Then** it reports that row as unparsed —
   never silently drops it or guesses a partial match.
3. **Given** the same input run twice, **When** Layer 0 executes, **Then** the resulting ontology is
   byte-for-byte identical both times — Layer 0 is a pure function of its input rows, no
   nondeterminism.

---

### User Story 2 - Layer 1: a row's own text states its precondition, extracted with multi-task classification (Priority: P1)

For a row with no Layer-0 ontology match, the compiler extracts a precondition **only** when the
row's own `defect_text` states or clearly implies it — using the same never-invent, traceable-span
discipline already governing threshold extraction (`compile_llm.py`'s existing `SYSTEM_PROMPT` rule),
strengthened by **explicit multi-task classification** rather than one flat "find the condition"
prompt: classify the row's **deontic modality** (Obligation / Permission / Prohibition /
Recommendation — an established NLP task, source 2) and the cross-reference target *as separate
signals* before extracting the applicability condition itself.

**Why this priority**: Sequencing this before any external-knowledge layer matters because it is
still fully traceable to the row's own text — no citation-trust question, no grounding-verification
overhead needed.

**Independent Test**: Compile a representative sample including (a) a row with an explicit stated
precondition, (b) a row with none, (c) a row where a precondition is implied but not clearly stated;
confirm (a) extracts correctly with a traceable span, (b)/(c) default to no precondition rather than
guessing.

**Acceptance Scenarios**:

1. **Given** a row whose `defect_text` names its own topic clearly (e.g. "Were all gift and/or grant
   fund requirements met?"), **When** Layer 1 runs, **Then** it extracts the implied precondition,
   citing the specific phrase.
2. **Given** a row with no stated or implied precondition, **When** Layer 1 runs, **Then** no
   precondition is extracted — unchanged from unconditional compilation.
3. **Given** genuine ambiguity, **When** Layer 1 is uncertain, **Then** it defaults to no precondition
   (never a guess) — per the researched failure-mode asymmetry (under-extraction, not hallucination,
   is the dominant real-world risk for this extraction class).

---

### User Story 3 - Layer 2: external-knowledge-derived preconditions retrieve and cite, verify automatically, then escalate to a human (Priority: P1)

For the genuine residual — no Layer-0 match, no Layer-1 signal — the layer may consult a signed
knowledge base (reusing `002c`'s existing `knowledge_base.py`) to propose a precondition, but the
proposal must be **retrieval-only** (never synthesized), pass an **automated grounding-verification
check** before any human sees it, and then go through `002c`'s existing judge panel
(`judge_panel.py`) — with a **stricter escalation policy than `002c`'s default** (see Edge Cases).

**Why this priority**: This is the layer research shows is least reliable and highest-stakes to get
wrong (a false precondition silently suppresses a real defect) — it exists, but every other layer
must be exhausted first, and it carries the heaviest trust machinery of the three.

**Independent Test**: Construct a case where a KB section supports a precondition claim; confirm the
grounding-verification check passes and it proceeds to judging. Construct a case where the LLM's
claimed citation does NOT actually support the claim; confirm the grounding-verification check
catches it before judging/human review ever sees it.

**Acceptance Scenarios**:

1. **Given** a genuinely residual row and a signed KB section that supports a real precondition,
   **When** Layer 2 runs, **Then** the proposed precondition is traceable to a specific KB section/
   version, and passes automated grounding verification.
2. **Given** the same setup but the LLM's proposed citation does not actually support the claimed
   precondition, **When** Layer 2's automated grounding-verification step runs, **Then** the proposal
   is rejected (not passed to judging or a human) — mirroring source 1's ablation finding that
   removing its grounding-verification component degrades grounding accuracy from 94.2% to 86.7%
   (§6, Ablation: "MiniCheck removal has minimal F1 impact but degrades grounding accuracy from
   94.2% to 86.7%").
   **Verification history (2026-07-26, kept as a record, not erased)**: earlier the same day, this
   citation was wrongly branded fabricated and removed, based on a re-check against the paper's
   *abstract only* — the abstract genuinely lacks the figure, but the full text contains it verbatim.
   A same-day adversarial audit caught the false correction by fetching the paper's full body; the
   citation is restored with this note as the audit trail. Lesson, binding on future citation checks
   in this project: **an abstract-only or summary-page check is not verification** — fetch the full
   text before declaring a citation fabricated, with the same rigor demanded before trusting it.
3. **Given** a proposal that passes grounding verification, **When** it reaches `002c`'s judge panel,
   **Then** it is **never auto-approved regardless of judge unanimity** — every Layer-2 proposal
   requires human sign-off before it can gate a real check, a deliberate, stricter override of
   `002c`'s default unanimous-and-confident auto-approve path (Edge Cases).

### Edge Cases

- **Why does Layer 2 override `002c`'s default auto-approve path?** `002c`'s judge panel exists to
  triage *interpretation* of a check's own already-scoped content (e.g. clarifying what a vague
  defect_text phrase means) — a wrong interpretation there produces a wrong threshold on a check that
  still fires and gets reviewed. A wrong Layer-2 precondition produces a check that **silently never
  fires at all** on loans where it should — the exact failure mode `002e`'s own Edge Cases already
  named as the one to guard hardest against. This asymmetry justifies a stricter bar for this one use
  case; it does not change `002c`'s default behavior for anything else.
- **What if Layer 0's clustering finds a dependency key but the loan-level canonical field needed to
  resolve it doesn't exist yet in the field catalog?** Not Layer 0's problem to solve — it produces
  the decoded ontology; whether/how a canonical field gets proposed for it is `002e`'s
  `proposed_field_entry` mechanism, unchanged.
- **What happens to the unresolved 253-row residual if Layer 2 still can't resolve some of them (no
  KB section covers the topic at all)?** They compile unconditionally (today's status quo) — the safe
  default per the researched under-extraction-is-the-dominant-risk finding, not a blocker.
- **Reusability**: this layer MUST NOT import anything from `p0/qc_engine/`'s mortgage-specific
  modules (`ruleset.py`, `engine.py`, `catalog.py`) — its public interface takes plain rows/dicts in
  and returns plain ontology/precondition-proposal data out; `002e` is the one place mortgage-specific
  wiring happens (translating a Layer-0/1/2 output into a `Check.applies_if`).
- **What if a Layer 1/2 LLM call returns malformed output?** Per Onity's own working pattern (retry,
  then an explicit abstain state — never silently coerced into a guessed answer): retry the call a
  bounded number of times; if still malformed, return an explicit `parse_failed` proposal state
  (mirroring `compile_llm.py`'s existing `parse_error` handling), not a fabricated "no precondition"
  or "precondition found" default.
- **What if this layer is pointed at a *different* project's rule source entirely, and Layer 0's
  clustering finds almost no dependency-key structure at all** (e.g. a workbook with no cross-
  reference column, or one whose syntax doesn't match any configured pattern)? Per Onity's own
  circuit-breaker precedent ("if fewer than 30% of source fields can be assigned an entity cluster...
  halt pipeline and return a structured error... do not produce a misleading low-quality mapping"):
  Layer 0 MUST report its real coverage percentage, and the pipeline MUST surface a structured
  low-structure signal (not silently fall through to running every row through expensive Layer 1/2)
  when coverage falls below a configurable floor — this is the concrete mechanism that makes "modular,
  reusable with other projects" true in practice, not just true by not importing `qc_engine`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Layer 0 MUST cluster rows by a configurable dependency-key pattern and produce a
  decoded ontology (key → {answer vocabulary, dependent rows}) as a pure, deterministic function of
  its input rows — zero LLM calls, zero network calls.
- **FR-002**: Layer 0 MUST report (not silently drop or guess) any row whose dependency expression
  doesn't match a configured pattern.
- **FR-003**: Layer 1 MUST classify a row's deontic modality and cross-reference target as explicit,
  separate extraction signals before deriving an applicability condition — not one flat prompt.
- **FR-004**: Layer 1 MUST default to no precondition when uncertain, per the same never-invent
  discipline already governing threshold extraction — extending it, not creating a new rule.
- **FR-005**: Layer 2 MUST source a proposed precondition only via retrieval against a signed KB
  (`002c`'s `knowledge_base.retrieve()`) — MUST NOT synthesize a precondition from general model
  knowledge.
- **FR-006**: Layer 2 MUST run an automated grounding-verification check (confirming the LLM's
  claimed citation actually supports the claim) BEFORE any judge-panel or human-review step —
  rejecting proposals that fail this check outright.
- **FR-007**: Layer 2 proposals that pass grounding verification MUST still route through `002c`'s
  judge panel, but MUST NEVER auto-approve regardless of judge unanimity/confidence — mandatory human
  sign-off for every Layer-2-sourced precondition, a stricter override of `002c`'s default policy for
  this specific use case only.
- **FR-008**: The three layers MUST run in strict sequence — Layer 1 only attempts rows Layer 0 didn't
  resolve; Layer 2 only attempts rows neither Layer 0 nor Layer 1 resolved. A row resolved by an
  earlier layer MUST NOT be re-processed by a later one.
- **FR-009**: This entire module MUST be importable and usable with no dependency on mortgage-qc-
  specific types (`Check`, `CanonicalLoan`, etc.) — its interface is plain data in, plain data out.
- **FR-010**: `002c`'s existing `knowledge_base.py`/`judge_panel.py` MUST be reused as-is (imported,
  not re-implemented) for Layer 2's KB-retrieval and judging steps.
- **FR-011**: Any Layer 1/2 LLM call that returns malformed/unparseable output MUST retry a bounded
  number of times, then fall back to an explicit `parse_failed` proposal state — never silently
  coerced into a guessed "no precondition" or "precondition found" default (Onity precedent, Edge
  Cases).
- **FR-012**: Layer 0 MUST report its real coverage (rows resolved / total input rows) for every run,
  and the pipeline MUST expose a configurable minimum-coverage floor below which it surfaces a
  structured low-structure signal rather than silently proceeding into Layer 1/2 at full scale
  (Onity's circuit-breaker precedent, Edge Cases) — this is the concrete, testable mechanism behind
  the "reusable with other projects" claim.

### Key Entities

- **OntologyEntry** (new): one decoded dependency key — `key`, `answer_vocabulary: List[str]`,
  `dependent_row_ids: List[str]`.
- **PreconditionProposal** (new): one candidate precondition for one row — `row_id`, `condition`
  (field/operator/value shape, matching `002e`'s `applies_if` condition shape), `source_layer` (0, 1,
  or 2), `provenance` (a quoted span for Layer 1, a KB section/version + grounding-verification result
  for Layer 2), `trust_tier` (derived from `source_layer` — used by `002e` to decide auto-sign vs.
  mandatory review), `parse_failed: bool` (Onity-precedent explicit abstain state, FR-011 — distinct
  from "no precondition found").
- **CoverageReport** (new): one run's Layer 0 statistics — `total_rows`, `resolved_rows`,
  `coverage_pct`, `below_floor: bool` (FR-012's circuit-breaker signal).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Layer 0, run against the real Retail Post-Closing rows, reproduces the 24-ontology-
  entry, 3,255-row result independently.
- **SC-002**: Layer 0's real *structural* coverage (rows resolved / total gated rows, computed
  directly from the raw workbook) is measured and reported before Layer 1/2 scope is finalized — not
  assumed from this spec's own preliminary numbers. **Explicitly NOT claimed by this criterion**
  (corrected 2026-07-24, see Assumptions): how many of those resolved rows are *currently producing a
  wrong verdict on a real loan* — that is a different measurement, requires a trustworthy compiled
  ruleset to test against, and is out of reach until the prerequisites named in Assumptions are met.
- **SC-003**: Layer 2's automated grounding-verification step, tested against a constructed
  unsupported-citation case, rejects it before judging — verified by test, not by inspection.
- **SC-004**: Zero Layer-2-sourced precondition reaches a real compiled `Check` without a recorded
  human sign-off, verified by test.
- **SC-005**: The module has zero imports from `p0/qc_engine/`'s mortgage-specific modules —
  verified by a static import-check test, not just code review.
- **SC-006**: `pytest p0/tests -v` passes in full — zero regressions to `002c`'s existing 164 tests.
- **SC-007**: A constructed malformed-LLM-output case (Layer 1 or 2) retries the configured number of
  times, then produces an explicit `parse_failed` proposal — never a silently-guessed default,
  verified by test (FR-011).
- **SC-008**: A constructed low-structure input set (below the configured coverage floor) produces a
  reported `CoverageReport.below_floor = True` and the pipeline halts Layer 1/2 expansion for that run
  rather than silently proceeding — verified by test (FR-012).

## Assumptions

- This spec builds the ontology layer as a new top-level package (`p0/ontology_extraction/`, see
  plan.md) rather than moving `002c`'s existing `knowledge_base.py`/`judge_panel.py` out of
  `p0/qc_engine/compiler/` — those modules are already implementation-generic (their own retrieval
  logic has no mortgage-specific content), so a future physical relocation is a low-risk refactor if
  ever wanted, not blocking this spec.
- Layer 0's dependency-key pattern is configurable (regex/parser passed in), not hardcoded to this
  project's specific `QuestionID == N && AnswerText == "..."` syntax — proven reusable by construction,
  not just by intent.
- This spec does not build a UI or authoring surface for reviewing Layer-2 proposals — FR-007's
  mandatory human sign-off reuses `002c`'s existing SME-exception-queue mechanism, unchanged.
- **Added 2026-07-24, from a `g-os-judge` review of this session's work**: measuring the *real-world
  defect impact* of Layer 0's coverage (how many of the 3,255 structurally-resolvable rows are
  currently producing a wrong verdict on a real loan, not just how many are structurally gateable) is
  explicitly **not attempted against the current compiled ruleset**, and MUST NOT be — that artifact
  mixes the now-excluded Private Bank workbook and carries the known, unfixed operator-inversion bug
  (`002d`, 45+ suspects). Testing against it would tangle three unrelated bugs together and produce
  confounded, untrustworthy evidence either way. This measurement is a **later, explicitly gated
  step** — valid only once (a) `002d`'s fix lands and (b) the ruleset is recompiled Retail-only (the
  still-pending housekeeping decision tracked in `output/ROADMAP.md` Tension 9) — not part of this
  spec's own Phase 1 criteria, and not to be attempted early as a shortcut.
- Numbered `002f`, a sibling of `002b`/`002c`/`002d`/`002e` in the compiler-family arc — depends on
  `002c` (implemented) directly; `002e` depends on `002f`, not the reverse.
