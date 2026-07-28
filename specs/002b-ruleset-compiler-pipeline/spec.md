# Feature Specification: Ruleset Compiler Pipeline

**Feature Branch**: `002b-ruleset-compiler-pipeline`
**Created**: 2026-07-01
**Status**: Implemented (2026-07 — all 31 tasks, see plan.md Implementation Notes; header corrected from stale "Draft" 2026-07-26, spec audit)
**Input**: User description: "002b-ruleset-compiler-pipeline — the compile→correct→sign loop at production scale: an LLM drafts a ruleset from real AMQ rule intent at config time, an SME corrects and signs it, the artifact is identified by SHA-256 with per-rule provenance and measured edit-distance, and sign-off-theater is surfaced loudly rather than passed silently."

**Governs**: `output/ROADMAP.md` §002b, `.specify/memory/constitution.md` Principle II (compile, then run), `output/THESIS.md` Point 3.
**Depends on**: `001a-field-catalog` (implemented — every drafted check's `field_name` must resolve here before sign-off). `002a-compile-fidelity-spike` (provisional PROCEED, 2026-07-01, AI self-review pending Kayla's confirmation — the spike that de-risked this spec being written at all; see below for what "provisional" means for this feature's scope).
**Foundation this builds on** (proven, not re-specced): `p0/qc_engine/ruleset.py`'s `Check`, `Ruleset`, and `RuleProvenance` dataclasses — the signed-artifact shape, the canonical SHA-256 hashing, and the edit-distance/sign-off-integrity mechanism **already exist and are proven** (`p0/tests/test_p0.py`'s `test_signoff_tracks_edits`, `test_ruleset_hash_stable`). This feature scales that mechanism from a hand-authored 8-check demo ruleset to a real, LLM-compiled batch — it does **not** invent a new artifact format. `p0/experiment_002a/compile_llm.py` proved the LLM-compile mechanism works at n=24; this feature is that mechanism at production batch scale.

**What "provisional" means for this feature's scope:** `002a`'s PROCEED verdict was produced by AI
self-review (Kayla unavailable), not by Kayla herself, and it surfaced two concrete failure patterns
even in a favorable result. This spec treats those two patterns as **scope, not footnotes** — FR-007
and FR-008 exist specifically because `002a` found them. If Kayla's eventual review substantially
disagrees with the self-review, this spec's automated-flagging requirements (FR-007/008) become more
load-bearing, not less — they're the mechanism that would have caught what a rushed sign-off might miss.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Compile a real batch into the same signed-artifact shape already proven (Priority: P1)

`002a` proved, at n=24, that an LLM can draft a `Check` conforming to `p0/qc_engine/ruleset.py`'s
existing schema from a real AMQ workbook row. This feature scales that to a production batch — dozens
to hundreds of rows in one compile run — producing draft `Check` objects ready for SME review, without
inventing any new artifact shape. The compiled batch becomes a `Ruleset`, identified by the same
SHA-256 canonicalization already proven for the demo ruleset.

**Why this priority**: This is the mechanism itself — everything else in this feature (consistency
checking, pattern flagging, sign-off tracking) operates on the output of this step.

**Independent Test**: Compile a batch of N real workbook rows (N > 24); confirm N `Check` drafts are
produced, each conforming to the existing `Check` schema, with zero new fields introduced.

**Acceptance Scenarios**:

1. **Given** a batch of real AMQ workbook rows, **When** the compiler runs, **Then** it produces one
   `Check` draft per row, each a valid instance of the existing `p0/qc_engine/ruleset.py` `Check`
   dataclass — no new schema, no new artifact format.
2. **Given** a compiled batch, **When** it is assembled into a `Ruleset`, **Then** `Ruleset.sha256()`
   (the existing, unmodified method) produces a stable, reproducible digest over the batch.

---

### User Story 2 - Zero-edit sign-off is surfaced loudly, never passed as a quiet win (Priority: P1)

Constitution Principle II is explicit: "zero edits across many rules is the sign-off-theater smell,
surfaced loudly, not a win." `p0/qc_engine/ruleset.py` already implements `unedited_rules()` and
`signoff_summary()` for this at the demo-ruleset scale (8 checks); this feature extends that same
mechanism to report at batch scale (dozens to hundreds of checks), so a production compile run can't
quietly slip past this signal the way a small demo batch might.

**Why this priority**: This is the constitution's own non-negotiable language, applied at the scale
where it actually matters — a large batch is exactly where a rushed, low-scrutiny sign-off is most
likely and least visible without an explicit report.

**Independent Test**: Sign a batch with zero edits; confirm the sign-off-theater flag fires. Sign the
same batch with a realistic edit-distance distribution; confirm it does not.

**Acceptance Scenarios**:

1. **Given** a compiled batch signed with zero edits across every rule, **When** the batch's
   sign-off summary is generated, **Then** it is flagged explicitly as a sign-off-theater risk — not
   silently reported as a clean pass.
2. **Given** a compiled batch with a normal, non-zero edit-distance distribution, **When** the summary
   is generated, **Then** no sign-off-theater flag fires.

---

### User Story 3 - No compiled check can be signed with an unresolved field reference (Priority: P1)

`001a-field-catalog`'s SAFE gate (`validate_referential_integrity`) already blocks a check whose
`field_name` doesn't resolve to a catalog entry — but that's currently checked at engine load time,
after a rule may already be signed. This feature moves that same check earlier: into the compile
pipeline, before a drafted rule is eligible for SME sign-off at all, using the existing validator
unmodified.

**Why this priority**: Catching an unresolved reference before signing is strictly better than
catching it at load time — it's the difference between "this can't be signed" and "this was signed
but silently never runs." Reuses `001a`'s exact mechanism; does not reimplement it.

**Independent Test**: Compile a batch where the LLM drafts a check against a field name not present in
the `001a` catalog; confirm the pipeline blocks that check from being marked sign-off-ready.

**Acceptance Scenarios**:

1. **Given** a drafted check whose `field_name` does not resolve to any `001a` `FieldCatalogEntry`,
   **When** the compile pipeline runs its pre-signing validation, **Then** that check is blocked from
   sign-off, naming the check and the missing field (reusing `validate_referential_integrity` verbatim).
2. **Given** a drafted check whose `field_name` does resolve, **When** the same validation runs,
   **Then** the check proceeds to the sign-off stage normally.

---

### User Story 4 - The two patterns `002a` found are caught automatically at scale, not by luck (Priority: P2)

`002a`'s self-review found two concrete failure patterns even in a small (n=24), favorable sample:
(a) a computational comparison (e.g. "use the greater of two rates") compiled into an opaque
pre-computed boolean the engine just reads, rather than deriving the comparison itself
(`predicate-08`); (b) a check classified as a doc-vs-system reconciliation (`agree_categorical`) when
the source condition is actually a policy/compliance question with no second independent source at all
(`reconcile-00`, `reconcile-01` — 2 of 2 in that sample). At production batch scale, a human can't
re-discover these row-by-row the way the `002a` review did by hand — the pipeline must flag them
automatically.

**Why this priority**: Lower than US1-3 because it's a quality-assurance layer on top of the core
mechanism, not the mechanism itself — but it's the direct, concrete legacy of what `002a` actually
found, not a generic "add more validation" instinct.

**Independent Test**: Feed the compiler a synthetic row shaped like `predicate-08` (a two-value
comparison condition) and one shaped like `reconcile-00`/`reconcile-01` (a policy condition containing
words like "conflict" or "discrepancy" but no real second source); confirm both are flagged for human
attention rather than silently compiled and passed through.

**Acceptance Scenarios**:

1. **Given** a drafted `predicate`-kind check whose underlying source condition describes comparing
   two values (not a simple presence/truth check), **When** the pipeline runs its pattern flags,
   **Then** it is flagged for human attention as a possible opaque-boolean/incomplete-compile risk.
2. **Given** a drafted `agree_categorical`/`agree_numeric`-kind check whose source condition text does
   not describe an actual doc-vs-system comparison (no second independent source is implied),
   **When** the pipeline runs its pattern flags, **Then** it is flagged for human attention as a
   possible archetype-classification mismatch.

---

### User Story 5 - The extracted intent is permanently registered, not just used to draft the check and discarded (Priority: P1)

The whole point of "compile, then run" (Principle II) is that the LLM **interprets the SME's rule
intent** — the compiled `Check` is not the source of truth on its own, it is a deterministic
*encoding* of an intent that came from somewhere (a real guideline, policy, or workbook row). Today,
`002a`'s `plain_english_restatement` field is framed only as something the SME reads *during* review
(`contracts/compiled-rule-schema.md`: "used ONLY by the SME reviewer to judge intent; never used by
the engine"). That framing is correct for the *engine* (it must never read this field at runtime,
per Principle II) — but it leaves open whether the restatement survives sign-off as a permanent
record, or is discarded once review is done. This feature makes the requirement explicit: **the
source rule/guidance text, the LLM's extracted intent, and the resulting deterministic check are
retained together as one registered triple, for the life of the signed artifact** — not just during
compile-time review. This is what lets someone, six months later, ask "what guideline was this check
for, and what did we understand it to mean?" and get a real, cited answer — not just the compiled
logic with no explanation of where it came from.

**Why this priority**: This is the audit half of the two business drivers named in `output/THESIS.md`
Point 3 ("if they don't understand how you calculated that number, you buy back the loan") applied to
*interpretation*, not just arithmetic. A regulator or an SME revisiting a rule a year from now needs
to see not just *what* the check does, but *what guidance it was compiled from* and *what we
understood that guidance to mean* — the same three-part chain `002a`'s spike proved is compileable at
all. Losing the intent after sign-off would mean the audit trail explains the math but not the
judgment behind it.

**Independent Test**: Take a signed `Check` from a compiled `Ruleset`; confirm its original source
rule/guidance text and its extracted plain-English intent can both be retrieved alongside the
deterministic logic — not just the logic on its own.

**Acceptance Scenarios**:

1. **Given** a `Check` that has been compiled, corrected, and signed, **When** its record is
   retrieved at any later point, **Then** it includes the original source rule/guidance text, the
   LLM's extracted plain-English intent, and the deterministic logic itself, together — none of the
   three is discarded once the others exist.
2. **Given** the same signed `Check`, **When** the engine evaluates it against a loan
   (`qc_engine.engine.run`), **Then** only the deterministic logic is read at evaluation time — the
   source text and extracted intent are retained for audit/review, never consulted by the engine at
   runtime (this does not reopen Principle II; it is the *audit* record, evaluated by humans, not a
   second code path the engine reads).

---

### Edge Cases

- What happens when the batch is large enough that compiling it in a single LLM context risks losing
  cross-row consistency (e.g., two checks about the same underlying concept drafted under different
  field names)? → Out of scope for *this spec* to resolve mechanically (FR-003 requires detecting it;
  the compile *strategy* — single-pass vs. chunked vs. a hierarchical/recursive orchestration pattern
  for very large batches — is a `/speckit-plan` architecture decision, not resolved here).
- What happens when a `predicate-08`-style or `reconcile-00/01`-style flag fires but the SME reviews
  it and confirms the compile is actually fine? → The flag is advisory, not a hard block — it routes
  to human attention, per User Story 4; it does not prevent sign-off on its own (only an unresolved
  field reference, User Story 3, is a hard block).
- What happens if the same batch is recompiled after a rule intent changes? → Out of scope for this
  spec (the re-validate/re-sign loop on rule change is Principle II's stated workflow, but this
  feature's scope is the compile→sign loop itself, not change management around it).
- What happens to `002a`'s own throwaway experiment code? → Untouched; this feature is a fresh,
  production-scoped implementation, not an extension of `p0/experiment_002a/`'s throwaway scripts
  (per `002a`'s own FR-008 — spike code is not extended into production).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The pipeline MUST compile a batch of real AMQ workbook rows into draft `Check` objects
  conforming exactly to the existing `p0/qc_engine/ruleset.py` schema — no new fields, no new artifact
  format.
- **FR-002**: Every drafted `Check`'s `field_name` MUST be validated against the `001a` `FieldCatalog`
  (reusing `validate_referential_integrity` unmodified) before that check is eligible for SME sign-off
  — an unresolved reference blocks sign-off, it is never silently signable.
- **FR-003**: The pipeline MUST detect and report likely duplicate vocabulary within a batch — two or
  more drafted checks that appear to reference the same underlying real-world concept under different
  `field_name`s — as a consistency risk, distinct from and in addition to `001a`'s referential-integrity
  check (which only catches *unresolved* references, not *duplicate* ones).
- **FR-004**: Every drafted `Check` MUST carry a `RuleProvenance` record (`llm_draft`, `signed_text`,
  `signed_by`, `signed_at`, `edit_distance`) using the existing mechanism in `p0/qc_engine/ruleset.py`
  verbatim — not reimplemented.
- **FR-005**: The compiled batch, once assembled into a `Ruleset`, MUST be identified by the existing
  `Ruleset.sha256()` canonical-hashing method, unmodified.
- **FR-006**: A batch signed with zero or near-zero total edit-distance across all rules MUST be
  flagged explicitly as a sign-off-theater risk (extending `Ruleset.unedited_rules()` /
  `signoff_summary()` to batch-scale reporting) — never silently reported as a clean pass (constitution
  Principle II).
- **FR-007**: The pipeline MUST flag, for human attention, any drafted `predicate`-kind check whose
  underlying source condition describes comparing two or more values rather than a simple
  presence/truth check — the `predicate-08` pattern `002a` found.
- **FR-008**: The pipeline MUST flag, for human attention, any drafted `agree_categorical`/
  `agree_numeric`-kind check whose source condition text does not describe a genuine two-independent-
  source comparison — the `reconcile-00`/`reconcile-01` pattern `002a` found (2 of 2 in that sample).
- **FR-009**: No LLM call may occur outside the compile step — the signed artifact, once produced, is
  consumed by the existing `qc_engine.engine.run` with zero model calls at evaluation time, exactly as
  today (constitution Principle II, non-negotiable).
- **FR-010**: This feature MUST NOT build the authoring UI (roadmap `009a/b/c`) or product/program
  gating (`010a/b`) — its surface is the compile mechanism only.
- **FR-011**: Every compiled `Check` MUST retain, as a permanent part of its record — not a value
  discarded once SME review is complete — three linked pieces: (a) the original source rule/guidance
  text it was compiled from, (b) the LLM's extracted plain-English statement of that rule's intent,
  and (c) the resulting deterministic logic. This registers the transformation itself (source →
  extracted intent → deterministic check) as an auditable, retrievable record — not merely a
  transient step in producing the check. The engine (`qc_engine.engine.run`) MUST continue to read
  only (c) at evaluation time; (a) and (b) are audit-record fields, never a runtime input (Principle
  II is unchanged — this is documentation of what was compiled, not a second execution path).

### Key Entities

- **CompiledCheckDraft**: An LLM-drafted `Check` (existing schema, `p0/qc_engine/ruleset.py`) plus its
  source workbook row reference **and its extracted plain-English intent** (FR-011) — the unit User
  Story 1 produces. The intent field is not discarded after sign-off; it persists as part of the
  signed record alongside the source reference and the compiled logic.
- **ConsistencyReport**: The cross-batch duplicate-vocabulary finding (FR-003) — new to this feature,
  since `002a`'s n=24 sample was too small to exercise this risk meaningfully.
- **PatternFlag**: A `predicate-08`-style or `reconcile-00/01`-style advisory flag (FR-007/008) —
  attaches to a `CompiledCheckDraft`, routes to human attention, does not block sign-off on its own
  (only an unresolved field reference does, per User Story 3).
- **CompiledRuleset**: Reuses the existing `Ruleset` + `RuleProvenance` dataclasses verbatim — extended
  only by FR-011's requirement that intent is retained, not by any new dataclass.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Compiling a batch of N real workbook rows (N > 24, beyond `002a`'s spike scale) produces
  N `Check` drafts, each passing `001a`'s referential-integrity validator before sign-off is possible
  for any of them.
- **SC-002**: A synthetic test batch containing two checks that reference the same underlying concept
  under different field names is caught by the consistency report 100% of the time.
- **SC-003**: A synthetic test batch containing one `predicate-08`-style check and one
  `reconcile-00/01`-style check are both automatically flagged for human attention — 0 silent
  pass-throughs of either known pattern.
- **SC-004**: A batch signed with zero SME edits triggers the sign-off-theater flag; a batch with a
  realistic non-zero edit-distance distribution does not — verified by test, both directions.
- **SC-005**: Zero LLM/network calls occur during `qc_engine.engine.run` execution of any compiled
  ruleset produced by this pipeline — confirmed by test (no model access needed or possible at
  runtime).
- **SC-006**: For every `Check` in a signed `Ruleset` produced by this pipeline, its source
  rule/guidance text and extracted plain-English intent (FR-011) can be retrieved alongside its
  deterministic logic — verified by a test that queries a signed `Ruleset` for this full triple
  (source, intent, logic) for every check, with 0 checks missing any of the three.

## Assumptions

- This feature scales the already-proven compile/sign/hash mechanism (`p0/qc_engine/ruleset.py`) and
  the compile pattern already validated at small scale by `002a` (`p0/experiment_002a/compile_llm.py`)
  — it does not invent a new artifact format or a new signing mechanism.
- `002a`'s PROCEED verdict is provisional (AI self-review, not Kayla-validated) — FR-007 and FR-008
  exist as direct, concrete carry-forward of what that provisional review found, not as generic
  additional validation; if Kayla's eventual review differs, these become more load-bearing, not less.
- The authoring UI (`009a/b/c`) does not exist yet — sign-off in this feature is a procedural,
  non-UI review step (direct data inspection), consistent with `001a`'s and `002a`'s own assumptions.
- Batch size and the corresponding compile strategy for very large batches (single-pass vs. chunked
  vs. a hierarchical/recursive LLM orchestration pattern) is explicitly **not** decided in this spec —
  it's a `/speckit-plan` architecture question, to be resolved with research at that stage.
- Out of scope: the authoring UI (`009a/b/c`); product/program gating (`010a/b`); any runtime LLM
  evaluation path (Principle II); change-management for re-compiling after a rule intent changes.
