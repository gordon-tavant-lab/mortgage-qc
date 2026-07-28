# Feature Specification: Field Catalog

**Feature Branch**: `001a-field-catalog`
**Created**: 2026-06-30
**Status**: Implemented (2026-07-01, commit `0fece17` — all 19 tasks, zero regression; header corrected from stale "Draft" 2026-07-26, spec audit)
**Input**: User description: "001a-field-catalog — a schema-driven vocabulary for loan data fields (type, expected sources, citation/confidence requirements), authored as data, that lets the engine scale to hundreds of fields without engine code changes, and that closes the referential-integrity hole where a check's field reference can silently resolve to nothing."

**Governs**: `output/ROADMAP.md` §001a, `.specify/memory/constitution.md` Principle VII, `output/THESIS.md`.
**Foundation this builds on** (proven, not re-specced): `p0/qc_engine/model.py` (the current fixed `{doc, los, mismo}` field slots), `p0/qc_engine/ruleset.py` (the SHA-256 signing pattern this catalog reuses), `p0/eval_synth/taxonomy.json` (7,398 real conditions this catalog must eventually name fields for — 8,442 in the regenerated post-010a taxonomy; count-basis note added 2026-07-26, spec audit).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A check can never silently reference a field that doesn't exist (Priority: P1)

Today, `p0/qc_engine/model.py` uses a fixed Python field map (`CanonicalLoan.fields: Dict[str, SourceValue]`) with no validation that a check's `field_name` actually names something real. A typo, a stale reference after a rename, or a check authored against a field that was never populated all fail the same catastrophic way: the check silently evaluates against `None` / a missing slot and — depending on check logic — may resolve to a false clear. This is the single largest structural safety hole standing between the current 8-field demo and the real 800-check system.

**Why this priority**: This is the safety-critical reason 001a exists at all (constitution Principle VII's SAFE gate: "an unresolved reference is a silent no-op = a false-clear vector"). Every other capability in this feature is in service of making this check possible.

**Independent Test**: Author a check that references a field name not present in the catalog; confirm the system rejects it at validation/load time (not at runtime, not silently) before any loan is scored.

**Acceptance Scenarios**:

1. **Given** a field catalog with entries `note_rate`, `loan_amount`, `property_value`, **When** a check is loaded that references `field_name: "note_rate"`, **Then** the check passes referential-integrity validation and may execute.
2. **Given** the same catalog, **When** a check is loaded that references `field_name: "notee_rate"` (typo), **Then** validation fails with an explicit error naming the unresolved field and the offending check; the check does not execute against any loan.
3. **Given** a catalog entry is renamed or removed, **When** an existing check still references the old name, **Then** the next validation run fails loudly rather than the check silently no-op'ing.

---

### User Story 2 - Adding a new field is an authoring act, not a code change (Priority: P2)

The engine must grow from ~8 demo fields to the vocabulary needed for 4,192+ classified conditions (and eventually the full 7,398) without `p0/qc_engine/model.py` or any engine module being edited per field. A field is declared once — name, type, which sources are expected to carry it, whether a citation is required, whether a confidence value is required — and every downstream check-kind archetype (003a predicate, 003b ratio_threshold, 003c reconcile) consumes that declaration the same way.

**Why this priority**: This is the scaling bet the whole engine-slicing sequence (003a/b/c) depends on. Without it, each new archetype slice would require its own bespoke field-handling code — exactly the "boil the ocean" failure mode Principle IV forbids.

**Independent Test**: Add a new field entry to the catalog (no code change) and confirm a new check referencing it can be authored and validated successfully, and that a regression run against the existing P0 golden set shows zero diffs.

**Acceptance Scenarios**:

1. **Given** the catalog does not yet contain `flood_zone`, **When** an entry for `flood_zone` (type: string, expected sources: doc+los, citation required: true) is added to the catalog file, **Then** no file under `p0/qc_engine/` requires a corresponding code change for the catalog to recognize the field.
2. **Given** a newly added catalog entry, **When** the full P0 test suite and eval_synth property tests are re-run, **Then** all existing tests continue to pass unchanged (zero regression from the catalog's introduction).

---

### User Story 3 - The catalog is authored data an SME can review and sign off on (Priority: P3)

Per Principle VII, the catalog is one of four layers of the Authored Configuration Model: authored → SME-corrected & signed → identified by SHA-256 → executed by a version-pinned interpreter. The authoring **UI** for this (009) does not exist yet — for this feature, the catalog is a hand-authored data file the team edits directly and reviews with Kayla procedurally — but its *shape* must already be the signed, hashed artifact the future UI will read and write, so 009 is additive later, not a rewrite.

**Why this priority**: Lower priority than P1/P2 because the mechanism (hashing, versioning) can be built and proven correct before any human-review workflow exists around it — but it must still exist in 001a so 001b, 003a/b/c, and eventually 009 build on a stable, already-signed artifact shape rather than retrofitting signing later.

**Independent Test**: Hash the same catalog file twice (unchanged) and confirm the SHA-256 digest is identical; edit one entry and confirm the digest changes.

**Acceptance Scenarios**:

1. **Given** an unchanged catalog file, **When** it is hashed on two separate runs (or two machines), **Then** the SHA-256 digest is byte-identical both times.
2. **Given** a catalog file, **When** exactly one field's `type` is changed, **Then** the resulting hash differs from the original.

---

### Edge Cases

- What happens when a check references a field name not in the catalog? → Validation fails explicitly, naming the check and the unresolved field; the check is blocked from ever running against a loan (User Story 1).
- What happens when a catalog entry exists but no check currently uses it? → Visible as an "unused entry" in a validation report; not itself a validation failure (the catalog may legitimately be ahead of the checks that will consume it as archetypes 003a/b/c land).
- What happens when two checks expect different types for the same field name? → Rejected at validation time; the catalog is the single source of truth for a field's type, and a conflicting check reference is itself a referential-integrity failure.
- What happens to a field's `expected_sources` before 001b generalizes the engine to N sources? → Constrained to the existing vocabulary (`doc`, `los`, `mismo`) so 001a ships against the current engine; the catalog schema must not require rework when 001b introduces the generalized `{truth, sources{}}` envelope (forward-compatible naming, not a redesign).
- What happens if the catalog file itself is malformed (unparseable, duplicate field names)? → Fails validation at load time with a specific error; the engine never runs against a loan with a malformed catalog.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST declare every loan data field as a catalog entry with, at minimum: canonical field name, data type, the source(s) expected to carry a value for it, whether a per-field citation is required, and whether a per-field confidence value is required.
- **FR-002**: System MUST define a stable, typed per-field value envelope — `{value, source_origin, citation, confidence}` — that every field value conforms to regardless of which catalog entry it belongs to. This shape is fixed even as the field *set* grows (Principle VII, the fluid-vs-fixed boundary).
- **FR-003**: System MUST validate, before any check executes against a loan, that the check's `field_name` resolves to an existing catalog entry (referential integrity).
- **FR-004**: System MUST treat an unresolved field reference as a hard validation failure at load/compile time — never a silent no-op at runtime.
- **FR-005**: System MUST allow a new field to be added to the vocabulary by editing the catalog (authored data) alone, with zero changes required to engine code (`p0/qc_engine/*.py`).
- **FR-006**: System MUST identify the catalog artifact by a SHA-256 hash over its canonical (sorted-key, whitespace-normalized) serialization, consistent with the existing ruleset-signing pattern in `p0/qc_engine/ruleset.py`.
- **FR-007**: System MUST produce zero regressions against the existing P0 golden set and eval_synth property tests when the fixed field slots in `p0/qc_engine/model.py` are read through the new catalog-validated path instead of directly.
- **FR-008**: System MUST report catalog entries that no existing check references (visibility, not a failure) so unused vocabulary is discoverable during review.
- **FR-009**: Catalog entries MUST NOT allow two entries to share the same canonical field name (uniqueness), and MUST reject a malformed catalog file at load time rather than partially loading it.
- **FR-010**: Catalog entries' `expected_sources` MUST be expressible using the existing `doc`/`los`/`mismo` vocabulary in this feature, structured so that 001b's generalization to a named `sources{}` map requires no change to already-authored catalog entries.

### Key Entities

- **Field Catalog Entry**: A single vocabulary item — canonical field name, data type, expected source(s), citation-required flag, confidence-required flag, human-readable description. The unit of "adding a data element as an authoring act."
- **Field Catalog**: The full, versioned collection of Field Catalog Entries, signed and identified by a single SHA-256 hash — the vocabulary layer of the Authored Configuration Model (constitution Principle VII).
- **Field Envelope**: The stable, typed shape — `{value, source_origin, citation, confidence}` — every field value must conform to. Fixed by design; the thing determinism hashing, the confidence gate, and the audit trail all rest on.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Adding a new field to the vocabulary requires editing exactly one authored-data artifact (the catalog) and zero lines of engine code — verified by adding a synthetic field in a test and confirming no diff outside the catalog file is needed for the field to be recognized.
- **SC-002**: 100% of checks in the existing P0 golden set pass referential-integrity validation against the catalog with zero changes to their expected verdicts (no regression).
- **SC-003**: A deliberately unresolved field reference is caught by validation 100% of the time across a test suite of intentionally-broken references (0 silent no-ops reach loan scoring).
- **SC-004**: The catalog's schema can represent, without further schema changes, the field vocabulary implied by all archetypes already classified in `p0/eval_synth/taxonomy.json` (4,192 conditions across predicate/threshold/reconcile) — verified by a coverage check, not by authoring all 4,192 entries in this feature.
- **SC-005**: Re-hashing an unchanged catalog file yields an identical SHA-256 digest on every run (determinism parity with the existing ruleset-signing mechanism).

## Assumptions

- The authoring **UI** (roadmap feature 009) does not exist yet. For 001a, the catalog is hand-authored as a data file by the engineering team and reviewed procedurally with Kayla; the *artifact shape* (signed, hashed, versioned) must already match what 009's future UI will read/write, so no rework is needed when 009 ships.
- `expected_sources` in this feature is scoped to the existing three-source vocabulary (`doc`, `los`, `mismo`) already present in `p0/qc_engine/model.py`. The N-source generalization (`{truth, sources: {name → value}}`) is explicitly out of scope — that is roadmap feature 001b, which depends on this one.
- Field data types map onto the existing Decimal-safe money/ratio types already used in `p0/qc_engine/money.py` — this feature does not introduce a new type system.
- This is a data-layer/schema feature with no user-facing UI; its consumers are the engine (003a/b/c) and, later, the authoring surfaces (009a/b/c) — not end users directly.
- Out of scope for this feature: the N-source envelope generalization and inbound contracts (001b); any authoring UI (009); building extraction or LOS connectors (Principle IV — assumed periphery).
