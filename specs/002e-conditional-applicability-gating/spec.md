# Feature Specification: Conditional-Applicability Gating

**Feature Branch**: `002e-conditional-applicability-gating`
**Created**: 2026-07-24
**Status**: Implemented — Phase 1, engine side only (2026-07-25; compile-side sourcing never wired — that is `002g`'s scope; header corrected from stale "Draft" 2026-07-26, spec audit)
**Input**: Surfaced on a live SME review call (Kayla + Gordon) of loan 01's QC output. Kayla, checking
the actual closing package by hand, found the tool surfacing gift-fund-related checks as an
unresolved gap/exception on a loan that never used gift funds — her verdict: *"we would want... a
result of an NA, not applicable, because there is no gift letter... there are going to be a lot of
these things that are just not applicable to each loan situation."* Formalized as the systemic issue
in `output/SME-REVIEW-FINDINGS-2026-07-24.md` §1, designed against external research and prior art
(XACML `Target`/`Condition`/`Effect`, DMN condition-columns, Drools inferred-fact idiom, LLM
precondition-extraction literature) in `output/RULE-COMPILER-FIX-PLAN-2026-07-24.md` §1.

**Governs**: `output/ROADMAP.md` Tension 9 (the conditional-applicability half; the operator-direction
half is `002d`), and the still-open note on `010b`'s out-of-scope line ("pulling Fannie/Freddie
selling guides beyond the client spreadsheet"). `.specify/memory/constitution.md` Principle II
(compile, then run — the gating decision is authored at compile time, evaluated deterministically at
run time, never re-derived by a model per loan) and Principle VII (configuration is authored data).

**Revised 2026-07-24** after reviewing Olav's live "Ratio-Space Console" (`scenario.agent-lab.io`,
full findings in `output/AGENT-LAB-SCENARIO-CONSOLE-FINDINGS-2026-07-24.md`) — a sibling Tavant system
solving the identical guideline-to-constraint compilation problem for the same Citizens engagement.
It independently confirmed the two-layer design (a coarse `applies_to[]` program gate, separate from a
finer loan-fact `scope:` gate) this spec already proposed — but its real compiled output
(`(scope: occupancy == primary_residence; units between [3, 4]; loan_purpose in ['purchase',
'rate_term_refinance'])`) showed the gate is normally **compound** (multiple AND-combined conditions)
and uses operators beyond simple equality (`in` for set membership, `between` for ranges). The
original single-triple `applies_if` design below could not express this without artificially
splitting one real precondition across multiple checks. **`applies_if` is revised from a single dict
to a list of conditions** (FR-001, below) as a direct result.
**Depends on**: `001a-field-catalog` (implemented — `applies_if.field_name` must resolve to a real
catalog entry, same discipline as `field_name`/`compare_field_name`). `002b-ruleset-compiler-pipeline`
(implemented — this feature extends its compiler, not its architecture). `010a-program-applicability-
gating` (implemented — this feature is explicitly a *different, complementary* gating layer: `010a`
gates by program/investor; this feature gates by loan-specific fact, and the two compose, not
conflict). **`002f-precondition-ontology-layer`** (implemented 2026-07-25 — **this feature's
sourcing mechanism**: `applies_if` is no longer populated by a single bespoke defect_text-only
extraction step; it's populated by `002f`'s three-layer sequence — Layer 0 deterministic
cross-reference-column clustering, Layer 1 source-text extraction, Layer 2 KB-grounded extraction
with mandatory human review. This spec owns the mortgage-qc-specific consumption of `002f`'s output
— translating a `PreconditionProposal` into `Check.applies_if` — not the extraction mechanism
itself, which `002f` owns as a standalone, reusable capability). **Correction (2026-07-26,
`002g` alignment pass)**: that consumption was, in practice, never wired to `002f`'s real output —
`compile_llm.py` never called it — and (corrected 2026-07-26, adversarial audit) nothing else
populates `applies_if` either: it exists nowhere outside the engine/schema and its tests, in no
compiled ruleset and no fixture. `002g-canonical-loan-fact-vocabulary` builds the actual wiring, plus a canonical-
fact registry this spec's own design didn't anticipate needing (two independently-extracted
`field_name`s for the same real fact had no reconciliation step).
**Foundation this builds on**: `p0/qc_engine/ruleset.py`'s `Check` dataclass (gains one new optional
field, same pattern `003d`'s `compare_field_name` already established), `p0/qc_engine/engine.py`'s
`_eval_check` (gains one new deterministic step, evaluated before the existing kind-dispatch chain —
confirmed by direct code read: `sv = loan.get(chk.field_name)` at line 90 is the first line of the
function, before the `if chk.kind ==` chain begins at line 98; the new step slots in at that same
point, iterating `chk.applies_if`'s condition list and reading each condition's own `field_name` —
before any kind-specific logic runs), and `p0/qc_engine/catalog.py`'s `validate_referential_integrity()` (extended the same way
`003d` extended it for `compare_field_name`).

**What this feature is fixing, precisely:** No check kind today has any way to express "only evaluate
this if some other field on the loan has some other value." Every compiled check runs unconditionally
on every program-eligible loan (program-level gating, `010a`, is orthogonal — it decides which
*product* a rule belongs to, never whether a loan's own *facts* satisfy a rule's implicit
precondition). Confirmed concretely on loan 01 (no gift funds used): gift-fund-related checks
surfaced as an unresolved gap instead of resolving `NOT_APPLICABLE` cleanly, because nothing in the
compiled ruleset or the engine has a mechanism to make that determination from the loan's own data.

The AMQ workbook's own "Question ID"/"Question Criteria by Questions" column appears to encode this
branching. **[SUPERSEDED SAME-DAY — this paragraph preserved as the original assumption, flagged
stale by the 2026-07-26 spec audit]** It was believed **undecodable** without a client-supplied key
neither Gordon nor Kayla has. That was **reversed later the same day** (see the Edge Case below and
FR-008): clustering rows sharing the same Question ID reconstructs the real answer vocabulary with
zero client key and zero LLM — it became `002f`'s Layer 0, the majority-case source (3,255 of 5,520
rows). Instead, this feature extracts the precondition **directly from each row's own
`defect_text`** at compile time — the same "traceable to source text" discipline `compile_llm.py`
already enforces for thresholds, extended to a new field.

**Kayla's hard constraint, directly satisfied by this design:** on the same call, Kayla was explicit
that domain knowledge (a candidate Fannie Selling Guide, `docs/Selling-Guide_06-03-2026_highlighted.pdf`)
must never cause additional rules/questions to fire or originate content the spreadsheet didn't
already state — *"if it's not going to interject and cause other rules to run or questions to run,
then we're fine."* **Revised 2026-07-24**: rather than a single blanket rule ("grounding_context may
only interpret, never originate"), `002f`'s three-layer sequencing satisfies this constraint
precisely, tier by tier: Layer 0 uses zero external knowledge at all (pure data clustering — the
majority case, confirmed to cover 3,255 of 5,520 real rows); Layer 1 stays scoped to each row's own
text, unchanged from the original design; Layer 2 (the only tier where the Selling Guide may propose
a precondition the row's own text doesn't state) is real, but gated by an automated grounding-
verification check plus **mandatory human sign-off on every single proposal, regardless of model
confidence** — Kayla's constraint is honored not by forbidding this tier outright, but by never
letting it act alone.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A conditionally-scoped check resolves NOT_APPLICABLE cleanly when its precondition doesn't hold (Priority: P1)

Today, a check whose real-world applicability depends on a loan fact (gift funds used, property is a
condo, etc.) evaluates unconditionally — producing a false-positive-shaped surfaced result on loans
where the precondition doesn't hold. After this feature, such a check's compiled artifact carries an
explicit `applies_if` gate; when the loan's own data doesn't satisfy it, the check resolves
`NOT_APPLICABLE`, with zero LLM involvement at evaluation time.

**Why this priority**: This is the actual defect this feature exists to close — a real, SME-confirmed
false-positive-shaped result on a real loan, discovered by an actual human review, not a hypothetical.

**Independent Test**: Build a loan whose data doesn't satisfy a check's `applies_if` precondition;
confirm the check resolves `NOT_APPLICABLE`. Build a loan whose data does satisfy it; confirm the
check evaluates its own `kind` logic normally, unaffected by this feature.

**Acceptance Scenarios**:

1. **Given** a check with `applies_if=[{"field_name": "gift_funds_used", "operator": "==",
   "value": "true"}]` (a single-condition list) and a loan where `gift_funds_used` is `false`,
   **When** the check runs, **Then** the verdict is `NOT_APPLICABLE`, computed before any
   kind-specific evaluation logic runs.
2. **Given** the same check and a loan where `gift_funds_used` is `true`, **When** the check runs,
   **Then** it evaluates its own `kind` logic exactly as it would have before this feature — this
   feature adds a gate, it does not change what happens once the gate passes.
3. **Given** a check with `applies_if=None` (the default — the overwhelming majority of checks,
   unconditional), **When** the check runs, **Then** behavior is byte-for-byte identical to today —
   this feature must not change the evaluation of any existing unconditional check.
4. **Given** a check with an `applies_if` gate whose precondition *field* is itself absent on the loan
   (not `false` — genuinely unknown), **When** the check runs, **Then** the verdict is `NEEDS_REVIEW`
   with an explicit `review_reason` (not silently `NOT_APPLICABLE`, which would read as "confirmed no
   gift" when the true state is "we don't know") — the same "ambiguous absence → human" discipline
   `003d` already established for its one-side-absent case.
5. **Given** a check with a **compound** `applies_if` (2+ conditions, e.g. gating on both
   `occupancy == "primary_residence"` AND `property_type == "manufactured"` — the real shape
   confirmed by `output/AGENT-LAB-SCENARIO-CONSOLE-FINDINGS-2026-07-24.md`'s live prior art), **When**
   the check runs, **Then** all conditions are AND-combined — the check applies only if every
   condition holds; any single condition failing (and known) resolves `NOT_APPLICABLE` the same as
   Scenario 1.
6. **Given** an `applies_if` condition using the `in` operator (set membership, e.g. `property_type
   in ["condo", "co_op", "pud"]`) or the `between` operator (range, e.g. `units between [3, 4]`),
   **When** the check runs, **Then** the condition evaluates correctly for both — not just simple
   equality/inequality.

---

### User Story 2 - `applies_if` is sourced through `002f`'s three-layer sequence, never invents or over-triggers (Priority: P1)

**Revised 2026-07-24** — this story originally described a single, bespoke defect_text-only
extraction step. It's now sourced through `002f-precondition-ontology-layer`'s three-layer sequence
(Layer 0 deterministic clustering → Layer 1 source-text extraction → Layer 2 KB-grounded, mandatory-
human-reviewed extraction), each layer only attempting rows the prior layer didn't resolve. The
never-invent discipline and the under-extraction-is-safer-than-over-extraction default (per the
researched failure-mode asymmetry) still hold throughout — `002f` owns enforcing them; this spec owns
translating whatever `002f` resolves into `Check.applies_if`.

**Why this priority**: Getting this wrong in the unsafe direction (inventing preconditions that
aren't there) would cause the opposite failure — real defects silently resolving `NOT_APPLICABLE`
when they should fire — which is worse than today's status quo, not better. This is the load-bearing
safety property of the whole feature.

**Independent Test**: Compile a representative sample of rows including (a) rows with an explicit,
extractable precondition ("if gift funds were used..."), (b) rows with no precondition at all
(today's unconditional majority), and (c) rows where a precondition is implied but not explicitly
named. Confirm (a) extracts correctly, (b) stays `applies_if=None`, and (c) defaults to `None` rather
than guessing.

**Acceptance Scenarios**:

1. **Given** a row whose `defect_text` explicitly states a precondition ("Were all gift and/or grant
   fund requirements met?" — implying the check only concerns gift/grant scenarios), **When**
   compiled, **Then** `applies_if` is set, with the precondition traceable to a quoted span of
   `defect_text`.
2. **Given** a row with no stated or implied precondition, **When** compiled, **Then**
   `applies_if` is `None` — unchanged from today.
3. **Given** a row where the compiler is uncertain whether a precondition exists, **When** compiled,
   **Then** `applies_if` defaults to `None` (unconditional) — never a guessed gate.
4. **Given** a row a Layer-0 ontology entry resolves (a decoded cross-reference cluster), **When**
   compiled, **Then** `applies_if` is set directly from the ontology entry — no LLM call, no
   `grounding_context` involved at all for this row.
5. **Given** a row only Layer 2 can resolve (no Layer 0/1 signal), **When** it produces a proposal,
   **Then** that proposal reaches `Check.applies_if` ONLY after `002f`'s mandatory human sign-off —
   never auto-signed, regardless of grounding-verification or judge-panel confidence.

### Edge Cases

- What happens when `applies_if.field_name` doesn't resolve to a real catalog entry? → Caught at load
  time by `validate_referential_integrity()` (extended the same way as `compare_field_name`), never
  silently ignored at evaluation time.
- **What happens to the "Question ID" cross-reference column?** → **Revised 2026-07-24 — reversed
  from this spec's original assumption.** It is NOT unresolvable. Confirmed against the real,
  now-exclusive `PF and PC Sept 2025 AMQs - Retail.xlsx` workbook: the column (`Question Criteria by
  Questions`) is a structured `QuestionID == N && AnswerText == "..."` expression, and clustering
  every row that shares the same `N` reconstructs the full answer vocabulary and dependent-row set —
  entirely from the data, no client-supplied key needed. This is exactly `002f`'s Layer 0, and it
  resolves the majority of gated rows (3,255 of 5,520 Post-Closing rows, 24 distinct decoded
  questions) with zero LLM involvement. See `g-learn-hidden-precondition-extraction`.
- What happens on a recompile of the full rulebook — does `applies_if` retroactively change behavior
  for checks that already work correctly today (the unconditional majority)? → No: the safe-default
  discipline (User Story 2) means `applies_if` is only set when a layer has a real, traceable/
  verified signal; the vast unconditional majority is expected to compile with `applies_if=None`,
  identical to today.
- What happens to `Check.to_dict()`/`Ruleset.sha256()` for rulesets that never use `applies_if`? →
  Same as `003d`: the digest changes anyway (`asdict()` emits every field), a required re-baseline,
  not a regression — confirmed unavoidable by the same mechanism `003d` already documented.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `Check` MUST gain exactly one new optional field, `applies_if: Optional[List[Dict[str,
  str]]] = None` — a list of conditions (keys per condition: `field_name`, `operator`, `value`; for
  `in`, `value` is a delimited list e.g. `"condo|co_op|pud"`; for `between`, `value` is a delimited
  pair e.g. `"3|4"`), defaulting to `None` (unconditional, today's universal behavior). **Revised
  2026-07-24** from a single-dict design to a list — real prior art
  (`output/AGENT-LAB-SCENARIO-CONSOLE-FINDINGS-2026-07-24.md`) confirmed compound, multi-condition
  gates are the norm, not the exception, in this exact problem class.
- **FR-002**: `engine.py`'s `_eval_check` MUST evaluate every condition in `applies_if` (when
  present) before any kind-specific dispatch logic runs, AND-combined: for each condition, read
  `loan.get(condition["field_name"])` and compare against `value` using `operator`
  (`==`/`!=`/`<=`/`>=`/`<`/`>`/`in`/`between`); if any condition definitively does not hold, resolve
  `NOT_APPLICABLE` immediately — short-circuit on the first definite non-match.
- **FR-003**: If any condition's precondition field is present but its value is absent/unknown on the
  loan (not a definite non-match), and no other condition has already definitively failed, the check
  MUST resolve `NEEDS_REVIEW` with an explicit `review_reason` (name TBD in planning — e.g.
  `APPLICABILITY_UNKNOWN`), never a silent `NOT_APPLICABLE` (which would misrepresent "unknown" as
  "confirmed does not apply") and never a silent unconditional evaluation (which would reproduce
  today's bug).
- **FR-004**: `catalog.py`'s `validate_referential_integrity()` MUST also resolve every condition's
  `field_name` within `applies_if` when present, using the same fail-fast pattern as `field_name`/
  `compare_field_name`.
- **FR-005**: `applies_if` MUST be sourced exclusively through `002f`'s three-layer sequence (Layer 0
  deterministic clustering, Layer 1 source-text extraction, Layer 2 KB-grounded extraction) — this
  spec MUST NOT implement a separate, parallel extraction path of its own. **Revised 2026-07-24**
  (was: "the compiler MUST extract `applies_if` only from `defect_text`") — superseded now that
  `002f` exists as the dedicated, reusable sourcing mechanism; the never-invent/traceability
  discipline this FR originally stated is now `002f`'s FR-004/FR-005, enforced there.
- **FR-006**: When no layer of `002f` resolves a row with sufficient confidence/verification, this
  feature MUST default to `applies_if=None` (unconditional) — per the researched failure-mode
  asymmetry (under-extraction is the dominant risk; the safe default trades a few reviewable false
  positives against the worse failure of a check silently never firing).
- **FR-007**: *(superseded — closed checklist is `002f`'s Layer 1 concern, not this spec's; see
  `002f` FR-003.)*
- **FR-008**: *(superseded 2026-07-24 — reversed, not merely revised.)* The AMQ workbook's "Question
  ID"/"Question Criteria by Questions" column is confirmed decodable by clustering (`002f`'s Layer 0)
  and MUST be attempted before any LLM-based extraction — this feature does not skip it; `002f` owns
  the decoding, this spec consumes its output.
- **FR-009**: This feature MUST NOT change program-level gating (`010a`, `program_gating.py`) — the
  two gating layers (program vs. loan-fact) are complementary and compose (a check may be gated by
  both), neither supersedes the other.
- **FR-010**: Any canonical loan field needed as an `applies_if.field_name` target that doesn't
  already exist in the field catalog MUST be proposed via the existing `proposed_field_entry`
  mechanism (`compile_llm.py`, unchanged) — no new field-catalog mechanism.

### Key Entities

- **Check** (existing, `p0/qc_engine/ruleset.py`): gains `applies_if: Optional[List[Dict[str, str]]]
  = None` (AND-combined condition list).
- **CanonicalLoan** / field catalog (existing, `001a`): consumed, not modified in shape — precondition
  target fields are ordinary catalog entries, proposed via the existing mechanism if new.
- **AMQ workbook rows** (existing, `demo/rules/*.xlsx`): the sole source of truth for `applies_if`
  extraction — never `grounding_context` alone. (An earlier revision of this line also called the
  Question-ID column "unresolvable" — stale after the same-day reversal; its decoded output, via
  `002f` Layer 0, is in fact the primary source. Corrected 2026-07-26, spec audit.)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A loan reconstructed to match loan 01's real facts (no gift funds used) produces
  `NOT_APPLICABLE` for the gift-fund-related check(s) that previously surfaced as an unresolved
  gap/exception — the concrete, SME-confirmed case this feature exists to fix.
- **SC-002**: A loan with gift funds used produces the same evaluation behavior for those checks as
  today (this feature adds a gate, not new evaluation logic) — zero behavioral change on the
  gate-passes path.
- **SC-003**: A representative recompile sample shows the unconditional majority of checks compiling
  with `applies_if=None`, unchanged from today — confirming FR-006's safe default holds in practice,
  not just in prompt wording.
- **SC-004**: `validate_referential_integrity()` rejects a check with an unresolvable
  `applies_if.field_name` at load time.
- **SC-005**: `pytest p0/tests -v` passes in full after the digest re-baseline (following the `003d`/
  `004` precedent) — zero *unrelated* regressions.

## Assumptions

- **Superseded 2026-07-24**: this feature does not decode the AMQ workbook's Question-ID column
  itself — that decoding is `002f`'s Layer 0, a dependency, not something this spec re-does.
- This feature does not recompile the full Retail workbook's 5,520 Post-Closing rows as part of its
  own scope — Phase 1 (this spec) proves the mechanism against a representative sample including
  loan 01's real gift-fund case; a full/partial recompile to find additional real-world conditionally-
  gated checks at scale is a separate, later, real-spend decision (mirroring `003d`'s own Phase 1/
  Phase 2 split). **Note**: this project now compiles exclusively from `PF and PC Sept 2025 AMQs -
  Retail.xlsx` (5,520 Post-Closing rows) — the `Private Bank Oct 2025 PC and Nov 2025 PF.xlsx`
  workbook and all previously-compiled artifacts mixing both workbooks are excluded/superseded per
  explicit user direction; a full re-scope of already-compiled outputs is tracked separately (not
  this spec's scope).
- The Fannie Selling Guide (`docs/Selling-Guide_06-03-2026_highlighted.pdf`) is available as a
  candidate `grounding_context` source for *interpreting* an already-stated precondition (e.g.
  resolving what "condo project requirements" specifically means), consistent with `002c`'s existing
  grounding discipline — but is never required for this feature's core mechanism to work, and never
  permitted to originate a precondition on its own (FR-005).
- This is numbered `002e`, a sibling of `002b`/`002c`/`002d` in the compiler-family spec arc, per
  `output/RULE-COMPILER-FIX-PLAN-2026-07-24.md`'s suggested sequencing — larger and depending on more
  (field-catalog additions likely needed for some gating dimensions) than `002d`, so it may ship after
  it, not necessarily blocked by it.
