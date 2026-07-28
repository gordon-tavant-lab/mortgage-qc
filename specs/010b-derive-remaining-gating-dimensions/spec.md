# Feature Specification: Derive the Remaining Gating Dimensions (Occupancy + Loan Program)

**Feature Branch**: `010b-derive-remaining-gating-dimensions`
**Created**: 2026-07-27
**Status**: Draft
**Input**: Continuing the `010a`/`002g` thread — `output/ROADMAP.md`'s own 010b entry ("derive `QC_Policy`
/ occupancy / income-bucket gating attributes from loan data where no SQL clause encodes them"),
narrowed to the two dimensions this increment can actually ground in real, already-extracted data:
**occupancy** (owner-occupied / second-home / investment) and a clean **loan program** fact, distinct
from loan purpose — the two the roadmap itself names as still-derived, not already-SQL-encoded.

**Governs**: `output/ROADMAP.md`'s 010b entry, and the residual line in `010a`'s own spec: *"Occupancy/
Underwriting_Type/LoanType/LoanPurposeType narrowing (found, not yet gated on)... deriving gates
neither mechanism encodes (`010b`)."* Occupancy is `010a`'s **own named original motivating example**
for why program/loan-fact gating matters at all (`010a` spec.md preamble: *"Occupancy (owner-occupied
vs. investment) — the roadmap's own original motivating example, already encoded not derived"* at the
per-row SQL-clause layer — this spec derives it at the **canonical-loan-fact** layer instead, per-loan,
not per-row).

**Depends on**: `010a-program-applicability-gating` (implemented — establishes the program-tag token
set this spec's `loan_program` fact reuses, and the `applies_to()` gate this spec's `applies_if` gate
sits alongside, not instead of), `001b-source-envelope-and-inbound-contracts` (implemented — this
spec's derived facts are consumed as ordinary `SourceValue` entries in the same field envelope),
`002e-conditional-applicability-gating` (implemented — `Check.applies_if` is the mechanism this spec
finally exercises with a real, wired derived fact, not a hand-injected test-only field), `002g-
canonical-loan-fact-vocabulary` (implemented — this spec extends its 16-fact `FactVocabulary` and its
`build_loan_profiles_v2.py` derivation layer, following the same `derivation_kind`/`derivation_rule`/
`derived_from` shape verbatim).

---

## Why this feature exists

Two real, confirmed gaps — found by direct inspection of the code and the real fixtures, not assumed:

**Gap 1 — the two facts this spec adds do not exist anywhere.** `grep -rn "occupancy_type\|loan_program"
p0/ storage/` (excluding raw `occupancy_1003`/`loan_type`/`loan_type_cd` extraction fields and the
per-row `program_gating.py` used by `010a`) returns zero hits. The only program-mapping that exists
today is `program_gating.py`'s `_loan_program(loan_type)` (`p0/qc_engine/compiler/program_gating.py:146-
156`), which reads the single, conflated `CanonicalLoan.loan_type` string (e.g. `"Conventional
Purchase"`, `"Freddie Mac Cash-Out Refi"`) — a **bare Python attribute with no `SourceValue`, no
citation, no per-field envelope at all** (`model.py:186`: `loan_type: str = ""`) — purely to decide
`010a`'s own compiled-check filtering (`applies_to()`, `program_gating.py:167-193`). It is never written
to a loan profile, never a citable derived fact, and conflates *program* with *purpose* in one string
("Purchase"/"Cash-Out Refi" is baked into the same token `010a` reads for program). A client-facing
"Loan Program: Conventional — Fannie Mae" display, or an `applies_if` gate that needs occupancy alone,
has nothing to read.

**Gap 2 — the mechanism that WOULD carry these facts into a real check exists, is tested, and is
completely unread by the engine.** `p0/qc_engine/build_loan_profiles_v2.py` computes `derived_facts`
(shape: `{"derived_facts": {"<fact_name>": {"value", "derived_from", "derivation_rule",
"derivation_kind": "computed"}}}`) for 3 of the 16 facts in `storage/fact_vocabulary/v6.json`
(`gift_funds_used`, `loan_transaction_type`, `appraisal_in_file` — confirmed by reading
`build_loan_profiles_v2.py:149`'s `DERIVATIONS` tuple and the module's own docstring, which explains why
the other 13 have no direct signal in these 5 fixtures and are correctly left `underivable`, not
guessed). It writes `storage/loan_profiles/v2/loan_0{1..5}.json`. **`grep -rn "loan_profiles"
p0/qc_engine --include="*.py" | grep -v test` returns zero hits inside the production `qc_engine`
package** — the mechanism is a side-channel nobody in the real pipeline reads. The one place this was
ever actually wired into `loan.fields` and evaluated is a **one-off proof script**,
`p0/compile_runs/run_013_comprehensive_e2e_v6/build_and_run.py`'s `_panel_from_v2_profiles()`
(lines 81-105) — real, working, but untested, uncommitted-as-reusable-code, and living outside
`qc_engine` entirely. It also confirms (by direct code read) the honest boundary this spec inherits
from `002g`'s own recorded Assumption: a derived fact is written as `SourceValue(doc=entry["value"])`
with **no citation** (`run_013` line 93) — `SourceValue.citation` stays `None` — because a derived
fact was never extracted from a document page/segment; `002g`'s spec explicitly flagged this "third
provenance kind" gap and deferred it ("`001a`/`001b` are flagged for that revisit then, not now"). This
spec does not re-open that revisit either (Assumptions, below) — it reuses the same, already-proven
`doc`-with-no-citation pattern `run_013` established, promoted from a throwaway script into tested,
reusable `qc_engine` code.

**The concrete, real anchor case this spec proves against**: the real, already-compiled check
`insurance-docs-support-owner-occupancy` (`result/rules/post_closing_only_ruleset.json`, `field_name:
insurance_docs_support_owner_occupancy`, `kind: predicate`, `predicate: is_true`) traces to a family of
5 real AMQ rows sharing the identical defect text **"QC review of insurance & other documents do not
support owner occupancy"** — `pc-retail-02837` (`O-FHA-50893`), `pc-retail-02838` (`O-FNM-50343`),
`pc-retail-02839` (`O-FRD-50355`), `pc-retail-02840` (`O-RHS-50530`), `pc-retail-02841` (`O-VA-50894`) —
confirmed directly in `p0/fixtures/ontology_extraction/retail_post_closing_rows.json`. The check's own
purpose (does the file's insurance/other paperwork corroborate the *claimed* owner-occupancy — a
misrepresentation check) is only meaningful when the loan **claims** owner-occupancy in the first
place; a loan honestly originated as an investment property claims no owner-occupancy benefit, so
there is nothing for this check to corroborate. Today it runs unconditionally on every loan regardless
of occupancy — the same class of false-positive-shaped result `002e`'s own gift-funds case (Kayla's
SME finding) already fixed for a different fact. This spec closes the identical gap for occupancy.

**A second, equally real, disclosed limitation found while scoping `loan_program`** (the honest-
residual discipline `build_loan_profiles_v2.py`'s own docstring already established for the other 13
underivable facts, applied here to a 14th case found mid-scoping): unlike `occupancy_1003` (one
field, present with a real `DocCitation` on all 5 fixtures), a **citable** per-loan program signal is
scattered and incomplete. Confirmed by direct inspection of all 5 fixtures' `fields`:

| Loan | Real program (fixture label) | Citable doc signal found |
|---|---|---|
| loan_01 | Conventional | `loan_type_cd = "Conventional"` (cited) — but "Conventional" alone cannot distinguish Fannie Mae vs. Freddie Mac, the identical ambiguity `program_gating.py`'s `AMBIGUOUS` sentinel already exists to surface at the SQL-clause layer (`program_gating.py:118-141`) |
| loan_02 | FHA | `fha_case_number_1003` (cited) — unambiguous |
| loan_03 | VA | `va_lgy_case_number` (cited) — unambiguous |
| loan_04 | Freddie Mac | **zero** program-identifying field of any kind in `fields` |
| loan_05 | USDA | `usda_gus_id` (cited) — unambiguous |

loan_04's own top-level `loan_type` label ("Freddie Mac Cash-Out Refi") is fixture-authoring metadata —
a bare string with no `SourceValue`, no citation — not a citable doc-extracted signal a real pipeline
could ever produce. Per this project's own hardened grounding discipline (`CLAUDE.md` Non-Negotiable
#1: *"an honest 'UNSPECIFIED, needs SME input' beats a confident invented number, every time"*),
`loan_program` is therefore **honestly `underivable`** for loan_01 and loan_04 in these fixtures — not
guessed from the uncited label — mirroring exactly the posture `build_loan_profiles_v2.py` already
established for `appraisal_in_file` on loan_02. This is disclosed here, not smoothed over.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Occupancy is derived once, centrally, from the 1003, and is citable (Priority: P1)

Today, no canonical fact expresses a loan's occupancy in the fact-vocabulary/derived-facts sense — only
the raw, uncanonicalized `occupancy_1003` doc field (free text: `"Primary Residence"`, `"Primary
Residence (First-Time Homebuyer)"`, etc.) exists. After this feature, `occupancy_type` is a signed
`FactVocabulary` entry (`owner_occupied` / `second_home` / `investment`) with a `build_loan_profiles_v2`-
style derivation function that conservatively maps the known 1003 literal-text variants to the
canonical token, and honestly returns `underivable` for any text it does not recognize — never a fuzzy
match.

**Why this priority**: This is `010a`'s own named original motivating example (occupancy, owner-
occupied vs. investment) — the concrete case that justified building program/loan-fact gating in the
first place. Deriving it is the demonstrably real, already-extractable half of this spec's scope.

**Independent Test**: Run the derivation against all 5 real loan fixtures; confirm each resolves
`owner_occupied` (all 5 real fixtures are, in fact, owner-occupied — a real, disclosed data-diversity
limit, see Edge Cases) from a real, cited `occupancy_1003` value, traceable via `derived_from`.

**Acceptance Scenarios**:

1. **Given** loan_02's real fixture (`occupancy_1003 = "Primary Residence (First-Time Homebuyer)"`),
   **When** `derive_occupancy_type` runs, **Then** it returns `derived_facts.occupancy_type.value ==
   "owner_occupied"`, with `derived_from` naming the source field and its literal text.
2. **Given** a constructed loan whose `occupancy_1003` reads `"Investment Property"` (the real ULAD/
   URLA occupancy checkbox option — no fixture carries this text today), **When** derived, **Then** it
   resolves `"investment"` — proving the map recognizes the industry-standard token set, not only the
   5 fixtures' own narrow text.
3. **Given** a loan whose `occupancy_1003` is missing or reads text outside the recognized literal-
   variant map, **When** derived, **Then** the result is `underivable`, never a guessed default.

---

### User Story 2 - A real, already-compiled check gates on occupancy and stops running unconditionally (Priority: P1)

The real compiled check `insurance-docs-support-owner-occupancy` (Why This Feature Exists) runs on every
loan today, regardless of occupancy. After this feature, it carries `applies_if=[{"field_name":
"occupancy_type", "operator": "==", "value": "owner_occupied"}]`; on a loan whose occupancy resolves to
anything else, it resolves `NOT_APPLICABLE` — the derived fact actually gates a real check, closing the
"computed and ignored" gap the other 3 derived facts are still in (Why This Feature Exists, Gap 2).

**Why this priority**: This is the entire point of the feature (per the task scope) — proving the
derived-facts mechanism is load-bearing, not a side-channel nobody reads. Occupancy alone, without this
story, would just be a 4th unread fact.

**Independent Test**: Build the real check's `Check` object with the new `applies_if`; evaluate it
against (a) loan_02's real fixture (occupancy resolves `owner_occupied`) and confirm it evaluates its
own `predicate`/`is_true` logic normally (unaffected by the gate, same non-regression discipline
`002e`'s own Acceptance Scenario 2 established); (b) a constructed comparison loan whose occupancy
resolves `investment` and confirm `NOT_APPLICABLE`.

**Acceptance Scenarios**:

1. **Given** the real `insurance-docs-support-owner-occupancy` check with `applies_if` gating on
   `occupancy_type == owner_occupied`, and loan_02's real fixture (occupancy derives `owner_occupied`),
   **When** the check runs, **Then** it evaluates its own `predicate: is_true` logic exactly as it
   would have before this feature — the gate does not change behavior once it passes.
2. **Given** the same check and a constructed loan whose derived `occupancy_type == "investment"`,
   **When** the check runs, **Then** the verdict is `NOT_APPLICABLE`, computed before any kind-specific
   dispatch (`002e`'s existing `_eval_applies_if` ordering, unmodified).
3. **Given** a loan where `occupancy_type` was never derivable (User Story 1, Acceptance Scenario 3),
   **When** the same check runs, **Then** the verdict is `NEEDS_REVIEW` with `review_reason ==
   "APPLICABILITY_UNKNOWN"` — `002e`'s existing FR-003 behavior, unmodified, now exercised by a real
   derived fact instead of only a hand-authored test fixture.

---

### User Story 3 - `loan_program` is derived where a citable signal exists, and honestly `underivable` where it does not (Priority: P2)

A clean `loan_program` fact (Conventional/FHA/VA/USDA/Freddie/Fannie/SONYMA — `010a`'s own confirmed
token set, `program_gating.py:_PREFIX_TO_PROGRAM`), distinct from loan purpose, is derived from
per-program citable presence markers (`fha_case_number_1003`, `va_lgy_case_number`, `usda_gus_id`) where
they exist, and is honestly `underivable` — never guessed from the uncited `loan_type` label — where a
loan's only "signal" is that fixture-authoring string (Why This Feature Exists, loan_01/loan_04).

**Why this priority**: Lower priority than occupancy because two of five real loans are honestly
`underivable` today (a genuine, disclosed data-coverage gap, not a derivation-logic gap) — the fact is
real and correctly conservative, but proves the mechanism on 3 of 5 loans, not all 5, unlike occupancy's
5-of-5 coverage.

**Independent Test**: Run the derivation against all 5 real fixtures; confirm loan_02/03/05 resolve
FHA/VA/USDA respectively with citable `derived_from`; confirm loan_01/04 resolve `underivable` with an
honest reason naming the ambiguity (loan_01) or total absence of a citable field (loan_04) — never a
program guessed from `loan.loan_type`.

**Acceptance Scenarios**:

1. **Given** loan_02's real fixture (`fha_case_number_1003` present, cited), **When**
   `derive_loan_program` runs, **Then** it returns `derived_facts.loan_program.value == "FHA"`.
2. **Given** loan_01's real fixture (`loan_type_cd = "Conventional"`, cited, but no GSE-specific citable
   field), **When** derived, **Then** the result is `underivable`, with a reason naming the Fannie/
   Freddie ambiguity explicitly — never a silent guess in either direction.
3. **Given** loan_04's real fixture (no program-identifying field of any kind in `fields`), **When**
   derived, **Then** the result is `underivable`, with a reason distinguishing "no citable signal
   found" from loan_01's "signal found but ambiguous" — the two are different failure reasons and must
   not be conflated in the derivation's own reporting.

### Edge Cases

- All 5 real loan fixtures are, in fact, owner-occupied (Why This Feature Exists) — `occupancy_type`'s
  derivation logic is proven correct on the *owner-occupied* path against all 5 real loans, but the
  *second_home*/*investment* paths (User Story 1, Acceptance Scenario 2; User Story 2, Acceptance
  Scenario 2) are proven only against **constructed** `CanonicalLoan` fixtures, not a real extracted
  loan — the same "untested against a real fixture, but verified not to silently misfire" posture
  `010a` already disclosed for SONYMA (`program_gating.py`'s own comment, line ~32-34). Not fabricated
  as tested-on-real-data; disclosed as constructed-fixture-only.
- What happens if a future real extraction populates `occupancy_1003` with unanticipated text (a
  regional/product-specific occupancy label neither "Primary Residence," "Second Home," nor
  "Investment Property")? → `underivable`, per FR-002 — never a fuzzy/substring match beyond the
  explicitly enumerated literal variants (mirrors `derive_loan_transaction_type`'s existing
  `LOAN_PURPOSE_MAP` discipline in `build_loan_profiles_v2.py`).
- What happens if a derived fact's name collides with a field a real extraction pass *does* populate
  for the same loan (e.g., a future Touchless contract widening to extract a real `occupancy_type`
  field directly)? → The wiring step (FR-006) MUST NOT overwrite an existing `loan.fields` entry — a
  derived fact only fills a gap, never shadows a genuinely extracted one (Non-Negotiable #1: the
  document is the source of truth).
- What happens to `gift_funds_used`'s existing `field_catalog.json` entry, which declares
  `citation_required: true` even though its own real wiring (`run_013`) has never attached a citation
  and never will (Why This Feature Exists, Gap 2)? → A pre-existing inconsistency this spec did not
  create; **not fixed here** (out of scope — a `002g`-owned correction), but this spec's own two new
  catalog entries (FR-005) are declared honestly (`citation_required: false`) rather than repeating the
  same undisclosed mismatch.
- What happens when `occupancy_type` or `loan_program` is referenced by an `applies_if` condition but
  the referenced `CanonicalLoan` was loaded WITHOUT the wiring step (FR-006) ever running (e.g., a
  caller that builds a `CanonicalLoan` directly, bypassing the new wiring function)? → The field is
  simply absent from `loan.fields`, and `002e`'s existing FR-003 behavior applies unchanged:
  `NEEDS_REVIEW` / `APPLICABILITY_UNKNOWN`, never a silent unconditional pass-through.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `storage/fact_vocabulary` MUST gain a new signed version (v7, 18 facts) adding
  `occupancy_type` (enum: `owner_occupied` / `second_home` / `investment`) and `loan_program` (enum:
  `Conventional` / `FHA` / `VA` / `USDA` / `Freddie Mac` / `Fannie Mae` / `SONYMA` — `010a`'s existing
  token set, reused verbatim, not reinvented), each a `CanonicalFact` entry per `002g`'s existing shape,
  each with real `source_citations` (occupancy: the `pc-retail-0283{7,8,9}`/`02840`/`02841` "owner
  occupancy" row family plus the URLA/1003 "Occupancy" question itself; loan_program: the Exception
  Code prefix family `010a` already established at scale). Signed with the same honest placeholder
  every prior vocabulary version uses (`signed_by="NOT-A-REAL-SME-pending-kayla-review"`) until a real
  SME reviews it — unchanged posture, not a new gap.
- **FR-002**: A new derivation module (`build_loan_profiles_v3.py`, new script per version — the same
  "v1's/v2's generator behavior is pinned by committed tests and artifacts" precedent that produced
  `build_loan_profiles_v2.py` as a new script rather than an edit to v1) MUST implement
  `derive_occupancy_type(loan) -> Dict[str, Any]`, mapping a small, explicit, literal set of known
  `occupancy_1003` text variants to the canonical token (User Story 1) — never a fuzzy/substring match
  beyond the enumerated variants — and MUST honestly report `underivable` for any other text or a
  missing field, never guessed.
- **FR-003**: The same module MUST implement `derive_loan_program(loan) -> Dict[str, Any]`, resolving
  a citable program signal from per-program presence markers (`fha_case_number_1003`,
  `va_lgy_case_number`, `usda_gus_id`, and `loan_type_cd`'s literal `"Conventional"` value where
  present) — and MUST report `underivable` (never a guessed program) whenever (a) the only signal is a
  generically-"Conventional" `loan_type_cd` with no further GSE-specific citable field (the Fannie/
  Freddie ambiguity, mirroring `program_gating.py`'s own `AMBIGUOUS` sentinel at a different layer), or
  (b) no program-identifying field of any kind is present (loan_04's honest case).
- **FR-004**: `build_loan_profiles_v3.py` MUST reuse `build_loan_profiles_v2.py`'s three existing
  derivations (`derive_gift_funds_used`, `derive_loan_transaction_type`, `derive_appraisal_in_file`)
  unchanged, exactly as v2 reused v1's `derive_gift_funds_used` — a v3 profile carries all 5
  derivations' output, never a partial regression of v2's 3.
- **FR-005**: `p0/qc_engine/field_catalog.json` MUST gain two new entries, `occupancy_type` and
  `loan_program` (`data_type: "enum"`, `enum_values` per FR-001's token sets, `citation_required:
  false`, `confidence_required: false` — declared honestly, since neither fact's wiring path (FR-006)
  ever attaches a real `DocCitation`; see Edge Cases re: `gift_funds_used`'s inconsistent existing
  entry, not repeated here) — required so `validate_referential_integrity()` resolves them when
  referenced by a compiled check's `field_name` or `applies_if.field_name` (`catalog.py:155-197`),
  rather than raising `ReferentialIntegrityError` the moment either fact is actually used.
- **FR-006**: A new, reusable, tested function (promoting `run_013`'s one-off
  `_panel_from_v2_profiles()` pattern out of a throwaway proof script and into `qc_engine` itself) MUST
  take a `CanonicalLoan` and a loan-profile dict (`build_loan_profiles_v3.py`'s output) and write each
  `derived_facts` entry into `loan.fields[fact_name] = SourceValue(doc=value)` — **only** when
  `fact_name` is not already present in `loan.fields` (Edge Cases: never shadow a genuinely extracted
  field of the same name) — and MUST leave `underivable` entries alone (no field written; the existing
  `002e`/`NEEDS_REVIEW` path handles absence correctly already).
- **FR-007**: The real, already-compiled check `insurance-docs-support-owner-occupancy`
  (`field_name: insurance_docs_support_owner_occupancy`) MUST be given `applies_if=[{"field_name":
  "occupancy_type", "operator": "==", "value": "owner_occupied"}]` — proving User Story 2 against a
  real compiled check traced to 5 real AMQ rows, not a hand-authored test-only check.
- **FR-008**: This feature MUST NOT re-derive any gate `010a` already honors (program-prefix or
  SQL-clause applicability) or any income-bucket/`QC_Policy` dimension `output/ROADMAP.md`'s 010b entry
  also names — those remain out of scope for this increment (Out of Scope, below); this spec is
  occupancy + loan_program only, per the task's explicit scope narrowing.
- **FR-009**: This feature MUST NOT introduce any runtime LLM call. Both derivations are pure,
  deterministic string/dict logic over already-extracted fields, at profile-build time — consistent
  with every prior spec in the `002`/`010` families and Non-Negotiable #1.
- **FR-010**: The `applies_if` gate on `insurance-docs-support-owner-occupancy` (FR-007) MUST NOT
  change `010a`'s own, separate program-applicability tag on the same check (`applicability.json`'s
  `["Fannie Mae"]` entry) — the two gating layers compose (`002e` FR-009's existing invariant), neither
  supersedes the other.

### Key Entities

- **`occupancy_type`** (new `CanonicalFact`, `FactVocabulary` v7): `owner_occupied` / `second_home` /
  `investment`, derived from `occupancy_1003`.
- **`loan_program`** (new `CanonicalFact`, `FactVocabulary` v7): `Conventional` / `FHA` / `VA` / `USDA`
  / `Freddie Mac` / `Fannie Mae` / `SONYMA`, derived from per-program citable presence markers; distinct
  from `loan_purpose_general_1003`/`loan_transaction_type` (loan purpose) and from `010a`'s own
  uncitable `CanonicalLoan.loan_type` string.
- **`LoanProfile` v3** (extends `002g`'s existing shape, `build_loan_profiles_v3.py`): 5 derivations
  (3 reused from v2 + these 2 new), same `derived_facts`/`underivable` dual-map shape.
- **`Check.applies_if`** (existing, `002e`): consumed, not modified in shape — this spec is its first
  real, non-test-fixture producer/consumer pairing exercised end-to-end against a compiled check.
- **`FieldCatalogEntry`** (existing, `001a`/`catalog.py`): gains 2 new entries (FR-005).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `derive_occupancy_type` run against all 5 real loan fixtures resolves
  `occupancy_type=owner_occupied` for all 5, each with a real, cited `derived_from` — matching the
  actual, disclosed data-diversity limit (Edge Cases), not claimed beyond it.
- **SC-002**: The real compiled check `insurance-docs-support-owner-occupancy`, with `applies_if` set
  per FR-007, evaluates normally (its own `predicate: is_true` logic, unaffected) against loan_02's real
  fixture (occupancy resolves `owner_occupied`), and resolves `NOT_APPLICABLE` against a constructed
  loan whose `occupancy_type` resolves `investment` — proving User Story 2 end-to-end against a real
  compiled artifact, not only a hand-authored test check.
- **SC-003**: `derive_loan_program` resolves `FHA`/`VA`/`USDA` (loan_02/03/05) with citable
  `derived_from`, and honestly `underivable` (loan_01/04) with distinct, correct reasons — never a
  program silently guessed from `loan.loan_type`.
- **SC-004**: `validate_referential_integrity()` resolves both new fields without raising, for a
  ruleset whose checks reference `occupancy_type`/`loan_program` (FR-005 confirmed load-bearing, not
  just declared).
- **SC-005**: Full existing test suite (`python3 -m pytest p0/ -q`, 325 passing at this spec's writing)
  passes with zero regressions after this feature's additions; `python3 harness.py`'s 1,000-run digest
  (`82175d076579e31a50971d8b20ea4b63848bea9f9b53c30dd96524071842e5ec` at this spec's writing) is
  unchanged, since this feature touches no `engine.py`/`model.py`/`ruleset.py` evaluation logic — only
  adds data (a new profile version, 2 catalog entries, 1 compiled check's `applies_if`) and one small,
  new, additive wiring function.

---

## Assumptions

- **Inherits, does not re-open, `002g`'s own recorded "third provenance kind" gap**: a derived fact is
  written as `SourceValue(doc=value)` with `citation=None` — the same posture `run_013` already
  established in practice and `002g`'s spec already flagged as a future `001a`/`001b` revisit ("not
  now"). This spec promotes that pattern into tested, reusable code; it does not solve the underlying
  citation-provenance gap. A reviewer viewing `insurance-docs-support-owner-occupancy`'s citation in
  `ExceptionReview`'s `PdfViewerModal` for a loan gated by `occupancy_type` will see no citation on the
  gating fact itself — a named, disclosed limitation, not silently smoothed over. Output-surface
  rendering of derivation provenance (vs. a doc citation) is explicitly out of scope (below).
- `income-bucket` and `QC_Policy` — the other two dimensions `output/ROADMAP.md`'s 010b entry names —
  are out of scope for this increment (Out of Scope, below), per the task's explicit narrowing to
  occupancy + loan_program; tracked as a residual, not silently dropped from the roadmap entry.
- `loan_program`'s honest `underivable` result for 2 of 5 real loans (loan_01, loan_04) is treated as a
  real, disclosed data-coverage finding, not a defect in this spec's derivation logic — the same
  "narrow, defect-targeted fixture ≠ absence in the real file" discipline `appraisal_in_file`'s own
  docstring already established.
- Kayla (or another real SME) has not yet reviewed `FactVocabulary` v7 — same honest-placeholder
  posture (`signed_by="NOT-A-REAL-SME-pending-kayla-review"`) every prior vocabulary version carries.

## Out of Scope

- Re-deriving any gate `010a` already honors (Exception Code prefix, SQL-clause narrowing) — unchanged.
- `income-bucket` and `QC_Policy` derivation — `output/ROADMAP.md`'s 010b entry names these alongside
  occupancy; this increment narrows to occupancy + loan_program only, per explicit task scope. A future
  `010b`-family increment, not blocked by anything in this spec.
- Pulling Fannie/Freddie Selling Guides beyond the client spreadsheet to resolve loan_01/loan_04's
  Fannie-vs-Freddie ambiguity — resolved-in-part already (`output/SME-REVIEW-FINDINGS-2026-07-24.md`):
  the real gap is loan-fact conditional-applicability gating (what this spec builds), not deeper
  Selling-Guide program research; a Selling Guide may only gate whether an existing rule applies, never
  originate new rule content (`010a`'s own boundary, unchanged).
- Resolving `002g`'s deferred "third provenance kind" (derived-fact citation story) in `SourceValue`/
  `001b`'s envelope — inherited, not re-opened (Assumptions).
- Correcting `gift_funds_used`'s pre-existing, inconsistent `citation_required: true` catalog
  declaration (Edge Cases) — a `002g`-owned cleanup, not this spec's.
- Any Output-surface (`ExceptionReview`, xlsx/PDF export) rendering of a derived fact's provenance —
  Author + Apply only, per this spec's Surface.
