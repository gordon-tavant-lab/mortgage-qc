# Feature Specification: Source Envelope and Inbound Contracts

**Feature Branch**: `001b-source-envelope-and-inbound-contracts`
**Created**: 2026-06-30
**Status**: Implemented (2026-07-01, commit `1cec012` — all 18 tasks; header corrected from stale "Draft" 2026-07-26, spec audit)
**Input**: User description: "001b-source-envelope-and-inbound-contracts — generalize the engine's fixed {doc, los, mismo} field shape to a source-agnostic {truth, sources: {name → value}} envelope (N sources, no code change per source), and pin the Touchless and LOS/MISMO inbound contracts as consumed interface schemas — the scaling bet and source-independence guarantee (Principle V) that 001a's field catalog was built to anchor."

**Governs**: `output/ROADMAP.md` §001b, `.specify/memory/constitution.md` Principle V (source independence) and Principle VII (authored data), `output/THESIS.md` Point 2.
**Depends on**: `001a-field-catalog` (this feature generalizes the runtime shape whose vocabulary 001a already declares).
**Foundation this builds on** (proven, not re-specced): `p0/qc_engine/model.py` (`SourceValue.system_value()` — the existing LOS-else-MISMO fallback this feature generalizes), `p0/qc_engine/mismo.py` (the existing MISMO 3.4 adapter), `p0/qc_engine/engine.py` (the Step-1 FLAG-only comparison this feature must keep source-independent — `reconcile.py` holds normalize/compare helpers, but the actual FLAG-status assignment lives in `engine.py`'s `_eval_check`, e.g. lines 199 and 447; corrected 2026-07-27, constitution-alignment audit).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reconcile checks compare genuinely independent sources, not the same data twice (Priority: P1)

THESIS.md Point 2 names the exact trap this feature exists to close: "all the data she's going to provide is from the LOS, so that will be totally accurate — I can't compare the document to the system" → "No, we need to consider all three." Today, `SourceValue` hardcodes `doc` (truth) against `los`/`mismo` (system) as fixed attributes. The generalization must preserve that the document side is always `truth` and the system side is always a genuinely separate origin — never let a check compare a value against a re-serialization of itself.

**Why this priority**: This is Principle V, and it's the safety property the entire reconcile archetype (003c, FLAG-only) depends on. Getting the envelope shape wrong here silently defeats source-independence for every reconcile check built on top of it.

**Independent Test**: Construct a test loan where the `sources` map contains two entries fed from the *same* origin under different names; confirm the system rejects this configuration rather than allowing a reconcile check to "pass" a comparison against itself.

**Acceptance Scenarios**:

1. **Given** a field with `truth` populated from the closing-document extraction and a `sources` map containing `{"los": <value>}`, **When** a reconcile check compares `truth` against `sources.los`, **Then** the comparison runs against two independently-populated values (document-path vs. system-path), per Principle V.
2. **Given** a test fixture that (incorrectly) derives `sources.los` from the same origin as `truth` (e.g., both populated by re-serializing the same extracted value), **When** the source-independence guard runs, **Then** the configuration is rejected before any loan is scored under it.
3. **Given** only a MISMO 3.4/ULAD-DU export is available (no direct LOS export), **When** the loan is loaded, **Then** the MISMO value populates the system side (a named entry in `sources`) exactly as `SourceValue.system_value()` does today — behavior is preserved, not changed.

---

### User Story 2 - A new system source can be added without touching engine code (Priority: P1)

The fixed `{doc, los, mismo}` shape means adding a fourth source today requires a new dataclass attribute and code changes everywhere `SourceValue` is read. The generalized `{truth, sources: {name → value}}` shape must let a new named source (a fourth LOS, or eventually a settlement-agent/title feed) be added as configuration/authored data, consistent with 001a's "add a field without a code change" guarantee applied to sources instead of fields.

**Why this priority**: This is the literal scaling bet named in the roadmap ("the system must accept N independent sources... without a code change per source") and the reason 001b exists as a distinct feature from 001a.

**Independent Test**: Add a synthetic named source (e.g., `"settlement_agent"`) to a test loan's `sources` map and confirm an existing check can read it through the generalized accessor with zero changes to `p0/qc_engine/*.py`.

**Acceptance Scenarios**:

1. **Given** the generalized envelope, **When** a new named source key is added to a test loan's `sources` map, **Then** no engine module requires a code change for that source to be readable by existing check logic.
2. **Given** the same test loan, **When** the full P0 golden-set regression suite is re-run, **Then** all existing verdicts are byte-identical to the pre-generalization baseline (zero regression from the shape change itself).

---

### User Story 3 - The Touchless and LOS/MISMO inbound contracts are pinned schemas, not prose (Priority: P2)

`output/FOUNDATION-READINESS.md` GAP 1 flags that the Touchless extraction contract and the LOS/MISMO contract are currently described in prose (THESIS.md, CLAUDE.md) but not pinned as reviewable schemas. This feature closes that gap: document, as a schema, exactly what Touchless must return (extracted fields, document classification, per-field citation, per-field confidence) and what a LOS export / MISMO 3.4 XML must supply, each mapped onto 001a's catalog entries.

**Why this priority**: Lower than P1 because the engine-side generalization (User Stories 1-2) is the load-bearing safety/scaling work; this is the interface documentation that makes the *already-assumed* Touchless/LOS contracts (Principle IV — periphery, not a build) auditable and reviewable rather than tribal knowledge.

**Independent Test**: Hand the Touchless inbound schema and the LOS/MISMO inbound schema to someone unfamiliar with the codebase and confirm they can identify, for any given catalog field (001a), which inbound contract is responsible for supplying it and what confidence/citation metadata accompanies it.

**Acceptance Scenarios**:

1. **Given** a catalog entry from 001a with `expected_sources` including `doc`, **When** the Touchless inbound contract schema is consulted, **Then** it specifies the extracted-field shape (value, document classification, citation, confidence) that populates that entry's `truth` slot.
2. **Given** a catalog entry with `expected_sources` including `los`, **When** the LOS/MISMO inbound contract schema is consulted, **Then** it specifies how both a native LOS export field and a MISMO 3.4/ULAD-DU XML field populate that entry's system-side value under the same named-source key.

---

### Edge Cases

- What happens when a field has zero populated sources (missing everywhere)? → Resolves to an empty/missing state consistent with today's `SourceValue()` default — the MISSING archetype (predicate check-kind) must continue to fire correctly after generalization.
- What happens when only a MISMO file is present and no direct LOS export exists? → MISMO populates the system side exactly as today's fallback (`los if los is not None else mismo`), now expressed as a named entry in the generalized `sources` map rather than a hardcoded attribute.
- What happens when two or more system sources disagree with each other (not with truth)? → Explicitly out of scope for this feature (multi-source reconciliation across 2+ system sources is roadmap feature 013, demoted to a v3 interface note — the envelope must be *ready* for this, not implement it).
- What happens when a reconcile check's fixture accidentally derives the system value from the same origin as the truth value? → Rejected by the source-independence guard (User Story 1, Scenario 2) — this is the exact CLAUDE.md #3 test-data trap the guard exists to catch.
- What happens to existing engine code that reads `.doc`, `.los`, `.mismo` attributes directly? → Must be migrated to the generalized accessor with identical behavior; zero regression against the P0 golden set is a hard gate (Success Criteria).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST represent each field's value as a generalized envelope containing exactly one `truth` slot and a named map (`sources`) of zero-or-more system-side values, replacing the fixed `{doc, los, mismo}` attributes.
- **FR-002**: The `truth` slot MUST always represent the closing-document side of the loan (Principle V) — the system MUST NOT allow a system-side value to populate `truth`.
- **FR-003**: System MUST preserve the existing LOS-else-MISMO fallback behavior (`SourceValue.system_value()`) as a specific, named case of the generalized `sources` map, with zero change to any existing check's verdict.
- **FR-004**: System MUST allow a new named source to be added to the `sources` map via configuration/authored data only, with zero changes required to engine code (`p0/qc_engine/*.py`).
- **FR-005**: System MUST reject any configuration where a reconcile-kind check's comparison value is derived from the same origin as its truth value (the source-independence guard), before that configuration is used to score any loan.
- **FR-006**: System MUST document the Touchless inbound contract as a schema — extracted field value, document classification, per-field citation, per-field confidence — mapped onto 001a catalog entries.
- **FR-007**: System MUST document the LOS/MISMO inbound contract as a schema showing how both a native LOS export field and a MISMO 3.4/ULAD-DU XML field populate the same named system-side source key.
- **FR-008**: System MUST NOT implement reconciliation logic across two or more system-side sources (that comparison is out of scope — roadmap feature 013 / v3 interface note); the envelope must merely be structurally ready for it.
- **FR-009**: System MUST produce zero regressions — byte-identical verdicts — against the existing P0 golden set when engine code is migrated from the fixed `{doc, los, mismo}` attributes to the generalized envelope.
- **FR-010**: System MUST NOT require building the Touchless extractor or the LOS connector themselves (Principle IV) — only the contract/schema they must conform to, and the engine-side generalization to consume what they supply.

### Key Entities

- **Source Envelope**: The generalized per-field value container — `{truth, sources: {name → value}}` — replacing the fixed `SourceValue` dataclass. `truth` is always document-sourced; `sources` is an open, named map of system-side origins (today: `los`, `mismo`; extensible without code change).
- **Touchless Inbound Contract**: The consumed-interface schema describing what document extraction must return per field: extracted value, document classification, citation (doc name/page/segment), and confidence — mapping onto 001a's field catalog entries.
- **LOS/MISMO Inbound Contract**: The consumed-interface schema describing how a native LOS export field and a MISMO 3.4/ULAD-DU XML field both populate a named entry in the `sources` map, preserving today's fallback semantics.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of loans in the existing P0 golden set produce byte-identical verdicts before and after migrating from the fixed `{doc, los, mismo}` shape to the generalized `{truth, sources{}}` envelope (zero regression, the determinism gate).
- **SC-002**: A new named source can be added to a test loan and read by an existing check with zero lines of engine code changed — verified by an integration test that adds a synthetic source and reruns the existing check suite unmodified.
- **SC-003**: 100% of reconcile-check test fixtures where `truth` and a `sources` entry are (deliberately, for the test) derived from the same origin are rejected by the source-independence guard before scoring — 0 self-validating comparisons reach a verdict.
- **SC-004**: The Touchless inbound contract and the LOS/MISMO inbound contract each exist as a versioned schema document reviewable independently of code, each explicitly mapped to 001a catalog entries (closing `output/FOUNDATION-READINESS.md` GAP 1 for this feature's scope).
- **SC-005**: A loan with only a MISMO 3.4/ULAD-DU export (no native LOS export) produces identical verdicts to today's fallback behavior on every existing check that reads the system-side value.

## Assumptions

- Multi-source reconciliation — comparing two or more *system*-side sources against each other (e.g., two LOS exports after an M&A) — is explicitly out of scope. Per the roadmap, this was roadmap feature 013, demoted to a v3 interface note: the envelope must be structurally ready for it, but it is not built here, and is funded only if/when a real multi-LOS pilot exists.
- Building the Touchless extractor and the LOS connector is explicitly out of scope (Principle IV, assumed periphery) — this feature only pins the schema those upstream systems must conform to, and generalizes the engine's data model to consume it.
- A future independent title/settlement-agent feed (UCD / Closing Disclosure) becoming a *second truth-side* source is a distinct future interface (roadmap's "Future truth-side widening (A3)" note), not in scope for this feature — today, `truth` remains singular and document-sourced.
- This feature depends on 001a's field catalog for the vocabulary of field names and their expected-sources declarations; it does not redefine what fields exist, only how their values are structurally represented across N sources.
- Out of scope for this feature: the authoring UI (009); product/program gating (010a/b); the compiler/ruleset pipeline (002a/002b) — this is purely the data-ingest and source-representation layer.
