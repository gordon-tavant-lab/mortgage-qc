# Feature Specification: Canonical Loan-Fact Vocabulary + Compile-Time Precondition Wiring

**Feature Branch**: `002g-canonical-loan-fact-vocabulary`
**Created**: 2026-07-26
**Status**: Implemented — Phase 1 (2026-07-26; T001–T010, 24 new tests, 242 total passing, zero digest movement; SC-001 proven on real data with zero LLM calls)
**Input**: Continuing session thread (grill-me on loan-nature classification, then `/g-os-orchestrate`
"should we also include the ontology layer to the QC process... understand the nature of the loan
application... so we don't need to run thru all 5000+ rules"), refined across several turns to: (1)
loan-nature facts must be computed once, centrally, not re-derived per check ("B" — centralized, user-
confirmed); (2) the vocabulary of facts must be *discovered* from the real guide/rulebook, not hand-
picked; (3) every fact still requires a citation, no exception. Final direction: **"yes, we should
turn this into spec and make sure all prior specs align with this new concept."**

**Governs**: `output/ROADMAP.md` Tension 9's own explicitly-named, deliberately-deferred **Phase 2**
("a full/partial recompile of the 5,520-row Retail workbook through all three `002f` layers at scale
... a separate, later, real-Bedrock-spend decision") — this spec is that Phase 2, scoped and specced
with the research this session gathered, not a new problem.

**Depends on**: `002c-domain-knowledge-grounded-compilation` (implemented — reused for KB sign-off
shape), `002e-conditional-applicability-gating` (implemented — `Check.applies_if` is the consumer this
spec finally populates from real data), `002f-precondition-ontology-layer` (implemented — this spec
wires its already-built, already-tested `run_layers()` into the actual compiler for the first time),
`010a-program-applicability-gating` (implemented — this spec's Guide-citation boundary is bound by
010a's own already-signed constraint, not a new one).

**Research this spec is built on** (verified directly, not taken from search snippets alone):
1. [DMN (Decision Model and Notation)](https://docs.drools.org/latest/drools-docs/drools/DMN/index.html)
   — OMG standard for explainable, auditable decision logic with native decision-trace output;
   preferred here over SBVR as the precedent to anchor on because DMN has live production execution
   engines (Drools, Camunda) while SBVR is a modeling/vocabulary standard without a comparable
   execution ecosystem. **Correction (2026-07-26, adversarial audit)**: an earlier revision justified
   this preference with "SBVR's last formal version shipped January 2008... dormant," labeled
   "checked directly." Both parts were wrong: the check was a Wikipedia fetch (which mentions only
   v1.0), and [OMG's own spec page](https://www.omg.org/spec/SBVR/) lists SBVR 1.1 (2013) through
   **1.5 (December 2019)**. The DMN preference stands, on the honest ground (execution tooling and
   decision-trace output), not the false one (dormancy).
2. [MISMO Logical Data Dictionary](https://www.mismo.org/standards-resources/mismo-product/logical-data-model-3.5)
   — the mortgage industry's own standard business vocabulary; this project already touches MISMO XML
   as a data source (Non-Negotiable #3), so a canonical fact's name should be checked against the LDD
   where a matching term exists, not invented independently.
3. LoanOnt (Jain & Sharma, 2016, [doi.org/10.5121/ijwest.2016.7402](https://doi.org/10.5121/ijwest.2016.7402))
   — direct academic precedent for a TBox (general loan-eligibility structure)/ABox (one applicant's
   facts) split in this exact domain, confirming the layer split isn't a stretch for loan QC.
4. [PostgreSQL vs Pinecone vs OWL Ontology](https://pub.towardsai.net/postgresql-vs-pinecone-vs-owl-ontology-i-tested-all-three-as-ai-agent-backends-none-of-them-won-f5c03b321cb0)
   — a real, tested comparison using mortgage underwriting (CFPB QM rules, Fannie Mae Selling Guide)
   as the test domain; ontology-with-formal-constraints beat a vector DB and a SQL agent specifically
   on deterministic, auditable threshold checks, and — the disclosed limitation worth keeping — it
   correctly returned "no rule covers this" on a case with no defined shape, rather than guessing.
5. [Sanctioned](https://github.com/Devanshjoshi2804/Sanctioned) (verified directly — repo exists,
   not archived, README content matches: "Deterministic & explainable — pure typed rules, no ML,"
   "each lender is a versioned, declarative YAML," a "line-by-line reason trace for every verdict") —
   a real open-source lending-decision engine with the same policy-as-code, always-cite-a-reason shape
   this project already follows; its golden-persona replay-on-policy-change pattern (replay 360 fixed
   test borrowers through old vs. new policy, report who flips) is adopted here (Edge Cases, FR-008).
   **Correction (2026-07-26, direct WebFetch + `gh api` verification pass)**: an earlier draft of this
   spec also cited a second repo, "LendFlow" (`github.com/SidharthKriplani/lendflow`), sourced from an
   Exa search result that included specific, plausible-sounding architecture details (a 7-node
   pipeline, named FOIR/PII-redaction components, eval numbers). Direct verification found no such
   repository exists — `gh api repos/SidharthKriplani/lendflow` returns 404, and the account's real,
   complete repo list (92 public repos, checked directly) contains neither it nor the two other
   projects the same search result cross-referenced under that name. Removed rather than left
   standing; nothing in this spec's actual requirements depended on the removed citation, only on
   Sanctioned, which independently supports the same points and is now the only source cited here.
6. [Fannie Mae Lender Letter LL-2026-04](https://www.deepinspect.ai/blog/fannie-mae-ll-2026-04)
   (verified directly, effective **2026-08-08**) — requires lenders to "maintain records sufficient to
   support quality control review and Fannie Mae audit... which AI tool influenced which loan
   decision," explicitly naming quality control in scope. Not a new design driver — reinforces
   Non-Negotiable #1's existing audit-trail requirement with a real, dated regulatory deadline.

**Retraction (2026-07-26, same day — kept as the honest record)**: an earlier revision of this
paragraph declared `002f`'s "94.2% → 86.7%" ablation citation (ComplianceNLP, arXiv:2604.23585)
fabricated. **That declaration was itself the error.** It rested on a check of the paper's abstract
only; the full text contains the figure verbatim (§6, Ablation: "MiniCheck removal has minimal F1
impact but degrades grounding accuracy from 94.2% to 86.7%"). A same-day adversarial audit caught
the false correction; direct fetch of the full body confirmed it. `002f`'s original citation was
accurate all along and has been restored there with its own audit-trail note. Rule this project now
follows for citation disputes: fetch the full text — an abstract-only check can neither confirm nor
condemn a citation.

---

## Why this feature exists

Two real gaps, found by direct inspection, not assumption:

**Gap 1 — the wiring `002f`/`002e`'s own specs already named as Phase 2 was never built.** Confirmed
by grep: `grep -rn "run_layers" p0/ --include="*.py" | grep -v test` returns only
`p0/ontology_extraction/__init__.py` and `p0/ontology_extraction/pipeline.py` itself — the real
compiler, `p0/qc_engine/compiler/compile_llm.py`, has zero references to `ontology_extraction`,
`run_layers`, or `PreconditionProposal`. **Corrected 2026-07-26 (adversarial audit)**: an earlier
revision of this paragraph said `applies_if` values ship today via hand-authored fixtures in
`p0/fixtures/ruleset_defects.py` — also wrong, in the honest direction: that file contains **zero**
`applies_if` (verified by grep). The truth is starker: outside `ruleset.py`/`engine.py`/`catalog.py`
and their tests, **no `applies_if` exists anywhere** — not in any compiled ruleset, not in any
fixture. `002f`'s tested extraction pipeline has never populated one for a real rule row.

**Gap 2 — nothing stops two extracted preconditions from silently disagreeing about the same fact.**
`p0/ontology_extraction/layer1_extraction.py:55` prompts the LLM to invent `field_name` fresh, per
row: `"<snake_case name for the referenced loan fact>"` — there is no registry, no dedup, no check
against `field_catalog.json`'s existing names. Two AMQ rows about the same real-world fact ("gift
funds were used") worded differently could extract as `gift_funds_used` and
`gift_proceeds_present` — two different `Check.applies_if` conditions that could, in principle, ever
disagree about the same loan. This is the exact accuracy risk this session's design discussion
converged on: a loan-nature fact must be computed once, centrally, and referenced everywhere, not
re-derived per check.

**The boundary this spec does not get to redraw**: `010a-program-applicability-gating`'s own spec
already states, and this spec must keep honoring verbatim: *"a Selling Guide may only gate whether an
existing rule applies, never originate new rule content or trigger additional questions."* A canonical
fact's *name* may be enriched with a MISMO or Guide citation; its *existence* must always trace back to
a real AMQ row `002f` already extracted a precondition from. This spec adds a naming/dedup layer on
top of `002f`'s output — it does not change what `002f` is allowed to originate.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A compiled check's `applies_if` is populated from a real extraction, not a hand-authored fixture (Priority: P1)

A rule row whose `defect_text` reads "Were all gift and/or grant fund requirements met?" compiles
through `compile_llm.py`. Instead of the current behavior (no `applies_if` at all — nothing outside
the engine's own tests populates it today), the compiler calls `002f`'s `run_layers()` against
the row, gets back a `PreconditionProposal` (Layer 0 or Layer 1 resolves this specific row — it's a
row that states its own precondition in `defect_text`), and sets the compiled `Check.applies_if`
accordingly.

**Why this priority**: This is the entire point of the feature — without it, `002f`'s three layers are
tested, correct, and unused in production.

**Independent Test**: Run the wiring against a known gift-funds row from the real Retail AMQ sheet;
confirm the resulting compiled check's `applies_if` references the canonical `gift_funds_used` field
(not a re-derived ad hoc string), and that evaluating it against loan 01's fixture (documented
SC-001 case in `002e`, `gift_funds_used=false`) resolves `NOT_APPLICABLE`.

**Acceptance Scenarios**:

1. **Given** a real AMQ row whose `defect_text` self-states a precondition, **When** it compiles,
   **Then** the resulting `Check.applies_if` is non-empty and traces to a specific `002f` layer/
   proposal, visible in the compile log.
2. **Given** a row where all three `002f` layers fail to resolve a precondition (a genuinely
   unconditional check), **When** it compiles, **Then** `applies_if` remains `None` — never a guessed
   condition (mirrors `002f` FR-004/FR-011's existing never-invent discipline; this wiring must not
   weaken it).

### User Story 2 - Two checks about the same real-world fact reference one canonical field, not two that could drift apart (Priority: P1)

Two different AMQ rows, worded differently, both really mean "gift funds were used." Today's `002f`
Layer 1 would extract two independent `field_name` strings. This feature adds a resolution step: a
newly-extracted `field_name` is checked against a signed canonical-fact registry; an exact or
recognized-synonym match reuses the existing canonical name; a genuinely new fact is flagged for human
review before being added, never silently created as a duplicate.

**Why this priority**: This is the specific accuracy failure mode named earlier in this session's
design discussion — checks disagreeing about a loan's own nature is worse than a missing check,
because it looks correct until an auditor cross-checks two results against each other.

**Independent Test**: Feed two constructed rows with synonymous gift-related preconditions through the
pipeline; confirm both resolve to the same canonical `field_name`, and that a genuinely novel
precondition (no existing canonical match) is flagged for review rather than silently added.

**Acceptance Scenarios**:

1. **Given** an extracted `field_name` that exact-matches an existing canonical fact, **When**
   resolution runs, **Then** the existing canonical name is reused, no new entry is created.
2. **Given** an extracted `field_name` that is a recognized synonym (SME-confirmed mapping) of an
   existing canonical fact, **When** resolution runs, **Then** it resolves to the same canonical name.
3. **Given** an extracted `field_name` with no existing match, **When** resolution runs, **Then** it
   is surfaced as a candidate new canonical fact requiring sign-off — **never** auto-added.

### User Story 3 - The canonical fact vocabulary is itself signed before it can gate anything (Priority: P1)

Mirrors `002c`'s `KnowledgeBaseCorpus`: a vocabulary of canonical facts is real data the moment it's
built, but unusable for compilation until an SME signs it.

**Why this priority**: Everything else in this project's grounding chain (`002c`'s KB corpus, every
`002f` Layer-2 proposal) already enforces "no sign-off, no use." A canonical fact used to gate real
checks across the whole rulebook is at least as load-bearing as a single KB section — it must not be
the one place this discipline quietly lapses.

**Independent Test**: Attempt to resolve a `field_name` against an unsigned vocabulary; confirm it
raises the same class of error `knowledge_base.py`'s `CorpusNotSignedError` already establishes as
precedent, not a silent pass-through.

**Acceptance Scenarios**:

1. **Given** an unsigned canonical-fact vocabulary, **When** `compile_llm.py` attempts to resolve a
   `field_name` against it, **Then** compilation fails loudly (fail-fast, matching `catalog.py`'s
   existing referential-integrity pattern) rather than silently compiling without gating.

### Edge Cases

- Two Layer 1 extractions produce genuinely synonymous field names with no prior SME-confirmed
  mapping between them → both surface as separate candidates for the same review queue; the SME
  merges them at sign-off time, not the pipeline guessing they're the same.
- An extracted `field_name` collides in spelling with an *existing* `field_catalog.json` entry that
  means something unrelated → resolution MUST treat this as a real name collision requiring explicit
  human disambiguation, never a silent alias.
- A canonical fact's definition needs to change after a later Fannie Mae Selling Guide revision (the
  ingested corpus is already versioned, `storage/knowledge_base/kb.sqlite3`) → the fact vocabulary
  MUST itself be versioned the same way, so a check compiled against v1's definition doesn't silently
  start meaning something different when v2 ships (same principle as `002c`'s `update_corpus`
  section-level diffing).
- A rule-set change is proposed after the vocabulary is signed → adopting `Sanctioned`'s researched
  pattern (Research, source 5): replay a fixed panel of already-known loan fixtures through old vs.
  new vocabulary/ruleset and report exactly which checks flip, before the change ships (FR-008).
- Running the wiring at full 5,520-row scale is a real Bedrock cost, same as `002f`'s own already-
  established Phase 2 framing (`output/ROADMAP.md` Tension 9) — this spec's default scope is a bounded
  sample, not the full sheet (FR-007, Assumptions).

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `compile_llm.py` MUST call `ontology_extraction.pipeline.run_layers()` against a row's
  `defect_text` (and Layer 0's clustering input, where applicable) before finalizing a
  `CompiledCheckDraft`, and MUST set `applies_if` from any resolved `PreconditionProposal` — closing
  the gap where `run_layers()` is currently invoked only by its own package and its own tests.
- **FR-002**: Before a `PreconditionProposal`'s `field_name` is used in a compiled check, it MUST be
  resolved against a canonical fact registry. An exact match reuses the canonical name. A near-
  duplicate/synonym MUST be flagged for human merge-or-reject — never silently treated as identical or
  silently treated as new.
- **FR-003**: The canonical fact registry MUST be a versioned, signed artifact mirroring `002c`'s
  `KnowledgeBaseCorpus` shape (`signed_by`/`signed_at` gate usability) — unusable for compilation until
  an SME signs it (User Story 3).
- **FR-004**: A canonical fact entry MAY carry an optional citation to a MISMO Logical Data Dictionary
  term where a real match exists, attached as reference only. It MUST NOT be used to originate a fact
  that doesn't already trace to a real AMQ row `002f` extracted a precondition from — `010a`'s existing
  boundary (Why This Feature Exists) is unchanged, not loosened, by adding this citation.
- **FR-005**: Two checks whose `applies_if` conditions reference the same canonical `field_name` MUST
  evaluate identically at runtime for the same loan. (`engine.py`'s existing `_eval_applies_if`
  already satisfies this by construction — it reads `loan.get(field_name)` once per named field; this
  FR makes the invariant explicit and gives it a dedicated regression test, since FR-002's dedup step
  is what actually guarantees two *different* rows converge onto that same field name in the first
  place.)
- **FR-006**: The wiring MUST preserve `002f`'s existing FR-008 (strict layer sequencing) and FR-011
  (bounded-retry-then-explicit-`parse_failed`, never a guessed default) — this feature adds a
  consumer of `002f`'s output, not a second extraction path with looser discipline.
- **FR-007**: The default execution mode MUST run against a bounded, explicitly-chosen sample of rows
  (not the full 5,520-row Retail sheet). A full-rulebook run remains a separate, explicit, costed
  decision — the same posture `002f`/`002e`'s own specs already established for their Phase 2 and not
  re-opened here.
- **FR-008**: Before a canonical-fact-vocabulary or ruleset change ships, the pipeline MUST support
  replaying a fixed panel of already-known loan fixtures through the old vs. new version and reporting
  which compiled checks' resolutions change — adopted from the `Sanctioned` precedent (Research,
  source 5), not previously required by any prior spec in this project.
- **FR-009**: This feature MUST NOT introduce any runtime LLM call — extraction and canonicalization
  happen entirely at compile time, consistent with Non-Negotiable #1 and every prior spec in the
  `002` family.

### Key Entities

- **CanonicalFact** (new): `id`, `canonical_field_name`, `synonyms: List[str]`, `mismo_ldd_reference:
  Optional[str]`, `source_citations: List[str]` (which AMQ row(s)/Guide sections it traces to),
  `signed_by: Optional[str]`, `signed_at: Optional[str]`.
- **FactVocabulary** (new): a versioned collection of `CanonicalFact` entries, mirroring
  `KnowledgeBaseCorpus`'s shape (`p0/qc_engine/compiler/knowledge_base.py`) closely enough to reuse its
  `sign()`/`is_usable()` functions directly rather than re-implementing sign-off logic a second time.
- **CompiledCheckDraft** (existing, `compile_llm.py`): gains a populated `applies_if`, resolved through
  `FactVocabulary`, wherever `002f`'s `run_layers()` returns a usable `PreconditionProposal`.
- **PreconditionProposal** (existing, `p0/ontology_extraction/pipeline.py`): consumed, not modified in
  shape — this spec adds a consumer and a resolution step downstream of it, not a change to `002f`
  itself.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running the wiring against the real Retail AMQ sheet's known gift-funds row(s) produces
  a compiled check whose `applies_if` references the canonical `gift_funds_used` field; evaluating it
  against loan 01's fixture resolves `NOT_APPLICABLE` (the same SME-confirmed case `002e`'s SC-001
  already established, now reached via the real pipeline instead of a hand-authored fixture).
- **SC-002**: A constructed test with two rows carrying synonymous gift-related preconditions
  resolves both to the identical canonical field name; a constructed test with a genuinely novel
  precondition is flagged for review, not silently added.
- **SC-003**: Full existing test suite (`pytest p0/tests -v`) passes with zero regressions.
- **SC-004**: A bounded-sample run (FR-007) completes and reports honest coverage numbers (rows
  attempted / rows resolved by layer / rows flagged for vocabulary review), mirroring `002f`'s FR-012
  coverage-reporting pattern rather than inventing a new one.

---

## Assumptions

- The full 5,520-row recompile remains a separate, later, real-Bedrock-spend decision, unchanged from
  `002f`/`002e`'s own existing Phase 2 framing (`output/ROADMAP.md` Tension 9) — this spec scopes and
  builds the *mechanism*, not the full-scale run.
- Loan-nature facts requiring new external reference data to compute (e.g. a jumbo-loan conforming-
  limit table, CFPB Qualified-Mortgage test thresholds) are explicitly **out of scope** here — this
  spec only handles facts already derivable from fields `001a`'s field catalog already extracts (this
  session's own turn-3 scoping decision: prove the mechanism on the cheap, already-available case
  first).
- **Known data-model touch when that Phase 2 lands (recorded 2026-07-26, direction review)**: a
  *derived* fact (computed, not extracted — `is_jumbo`, QM status) fits neither of `SourceValue`'s
  two provenance kinds (document truth / named system source), and `_eval_applies_if` reads
  `loan.get(field_name).doc` directly (`engine.py:142`). Derived facts will need a third,
  explicit "computed from these inputs by this rule" provenance kind in `001b`'s envelope — never
  fake doc-provenance — so the citation story survives. `001a`/`001b` are flagged for that revisit
  then, not now.
- **Concept-index decision (2026-07-26, direction review)**: FR-002's synonym resolution is expected
  to be implemented with a citation-only concept index over `002c`'s existing KB (concept name →
  the Guide sections that define it, every entry a pointer to verbatim text) — satisfying the
  "understand the Guide's meanings" step *inside* this spec rather than via a separate Guide-ontology
  spec, because a pointer-only index organizes citations without ever originating content, staying on
  the right side of `010a`'s Guide-gates-never-originates boundary.
- Kayla (or another real SME) has not yet reviewed a canonical fact vocabulary produced by this
  pipeline — same honest-placeholder posture as the real Fannie Mae KB corpus
  (`signed_by="NOT-A-REAL-SME-pending-kayla-review"`) until real review happens.

## Out of Scope

- Jumbo/QM (or any other externally-referenced) fact computation — a separate, later spec, once the
  reference data itself (FHFA conforming limits, CFPB QM tests) is actually sourced.
- Re-litigating `010a`'s program-gating scope or mechanism.
- Any runtime LLM call of any kind (FR-009).
- The full-rulebook recompile at scale — tracked, explicitly deferred, per existing `002f`/`002e`
  Phase 2 precedent, not re-opened by this spec.
- Replacing `engine.py`'s flat deterministic evaluation with any form of formal ontology reasoner
  (OWL/DL, SHACL engine, or otherwise) — this session's own research surfaced that tooling and
  explicitly recommends against adopting it here (Research, source 4's real limitations plus this
  project's own audit-trail requirement); the vocabulary/canonicalization concept is borrowed, the
  reasoner machinery is not.
