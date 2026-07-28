# Feature Specification: Doc-vs-Doc Reconcile Check Engine

**Feature Branch**: `003d-engine-doc-vs-doc-reconcile-checks`
**Created**: 2026-07-23
**Status**: Implemented (2026-07-26, commit `41b8499` — all 19 tasks; header corrected from stale "Draft" 2026-07-27, spec adversarial audit)
**Input**: User description: "here is an engine gap we need to address, Real engine gap:
agree_categorical compares one field's doc-value vs. system-value, not two different document
field against each other. research and give me a plan to fix this" — surfaced while verifying
loan 01's post-closing-only QC results against its known planted-defect answer key.

**Governs**: `output/ROADMAP.md` Tension #5, `.specify/memory/constitution.md` Principle V (source
independence) and the RECONCILE/QC two-step model, `output/THESIS.md`'s audit story.
**Depends on**: `003c-engine-reconcile-checks` (implemented — this feature builds the capability
`003c`'s own FR-005 explicitly declined to build). `001b-source-envelope-and-inbound-contracts`
(implemented — this feature deliberately does NOT touch `SourceValue`/the source-independence
guard `001b` built; it adds a new, separate comparison path instead). `002b-ruleset-compiler-
pipeline` (implemented — this feature extends its compiler, not its architecture).
**Foundation this builds on**: `p0/qc_engine/engine.py`'s `_eval_check` dispatch, `p0/qc_engine/
ruleset.py`'s `Check` dataclass, `p0/qc_engine/catalog.py`'s referential-integrity gate, and
`p0/qc_engine/compiler/compile_llm.py`'s compile-time field-reuse discipline — all proven, reused
as-is; this feature adds two new dispatch branches and one new optional `Check` field, nothing else.

**What this feature is fixing, precisely:** `003c` proved `agree_categorical`/`agree_numeric`
correct for doc-vs-**system** reconciliation — one named field, comparing its document-extracted
`truth` value against its `system_value()` (LOS/MISMO). `003c`'s own FR-005 explicitly declined to
build the other real shape found in the same archetype data: **doc-vs-doc** comparisons, where two
*independently-extracted document* values must agree with each other and neither side has a system
source at all (e.g. the 1003's stated employment start date vs. the VOE's; the 1003's stated title
vesting vs. the Title Commitment's). `research.md` (`000-synthetic-fixture-generation`, decision #4)
named the reason this wasn't just bolted onto `agree_categorical`: `SourceValue`'s independence
guard is built for exactly one shape (`truth` vs `sources{}`), and forcing a second *document* value
into the `sources{}` slot would defeat that guard's whole purpose. `output/ROADMAP.md` Tension #5
has tracked this as a confirmed, real, unscheduled gap since `003c` shipped.

This was rediscovered directly, not assumed, while auditing loan 01's real QC results against its
planted-defect answer key: `title-vesting-1003-vs-commitment` and `employment-dates-1003-vs-docs-
agree` are both real, correctly-compiled checks against the client's actual rulebook — both landing
on `NEEDS_REVIEW: "No system value to check against the document"` because `agree_categorical`
structurally cannot reach a second, independently-named document field. Two more known defects
(`liability_disclosed_on_1003` vs `liability_amount_credit_report`; `cd_payoff_amount` vs
`payoff_statement_amount`) have no compiled check at all for the same underlying reason.

Confirmed by direct inspection of `p0/fixtures/from_docs/loan_01.json`/`loan_04.json`: all 5 known
field pairs carry `"sources": {}` (empty) on *both* sides — there is no system value to fall back
to; this is genuinely doc-vs-doc, not "doc-vs-system where the system side happens to be null."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A doc-vs-doc mismatch is caught as a real, deterministic defect (Priority: P1)

Today, a genuine disagreement between two documents in the closing package (e.g. title vesting on
the 1003 vs. the Title Commitment) either silently produces `NEEDS_REVIEW` with a message that
doesn't name the real problem, or has no check at all. After this feature, the same condition
produces a real `PASS`/`FAIL` verdict, citing both documents' values.

**Why this priority**: This is the actual defect this feature exists to close — without it, a
category of real, planted, catchable errors is silently invisible to the QC process.

**Independent Test**: Build a loan with independently-populated doc values for two named fields
(e.g. `title_vesting_1003`, `title_vesting_commitment`); construct one case where they agree
(after normalization) and one where they genuinely diverge; confirm the engine produces the
correct verdict in both directions, for both a categorical and a numeric comparison pair.

**Acceptance Scenarios**:

1. **Given** a loan whose two named document fields agree after normalization, **When** the
   `agree_doc_categorical` check runs, **Then** the verdict is `PASS`.
2. **Given** the same two fields genuinely diverging (independently constructed, not a copy-paste
   "one side left unchanged" mutation), **When** the check runs, **Then** the verdict is `FAIL`
   with `review_reason="EXCEPTION"` — **never** an informational `FLAG` (see User Story 2).
3. **Given** representative `agree_doc_numeric` conditions (two independently-stated dollar
   amounts) at, within, and outside an authored tolerance, **When** evaluated, **Then** every case
   produces the correct verdict using `Decimal`/`within_tolerance` — no float touches the
   comparison, and an `UNSPECIFIED` tolerance produces the same honest `NEEDS_REVIEW` guard
   `agree_numeric`/`ratio_threshold` already use.
4. **Given** a loan with a value present on only one of the two compared fields, **When** the check
   runs, **Then** the verdict is `NEEDS_REVIEW` with `review_reason="SOURCE_INCOMPLETE"` (set
   explicitly — see Edge Cases) — the same honest "ambiguous absence → human" semantics every other
   kind uses, not a special-cased `FAIL`.
5. **Given** a loan with both compared fields absent, **When** the check runs, **Then** the verdict
   is `NOT_APPLICABLE`.

---

### User Story 2 - A doc-vs-doc mismatch is a real defect, not an informational FLAG (Priority: P1)

`003c`'s FLAG-vs-FAIL partition exists because doc-vs-*system* disagreement is asymmetric: the
document is truth, the system is a possibly-stale copy, so disagreement is informational. That
asymmetry does not exist for doc-vs-doc — both sides are independently-extracted documents from the
same closing package; a mismatch is a genuine defect in the file itself, the same severity class as
a predicate/ratio_threshold failure.

**Why this priority**: Getting this wrong in either direction is a real, silent-failure-shaped bug —
treating a genuine doc-vs-doc defect as an informational `FLAG` would mean it never blocks
`auto_cleared` and never appears as a QC failure, silently under-reporting real defects exactly the
way `title-vesting-1003-vs-commitment` is under-reported today.

**Independent Test**: Run a loan with a genuine doc-vs-doc mismatch and no other QC failure; confirm
it surfaces in `qc_failures`/`exceptions` (not `flags`) and blocks `auto_cleared`.

**Acceptance Scenarios**:

1. **Given** a loan with a genuine doc-vs-doc mismatch and no other QC failure, **When** run,
   **Then** `qc_failures` is non-empty, `disposition` is `NEEDS_REVIEW`, and `review_reasons`
   contains `EXCEPTION` — not the reconcile-`FLAG` path `agree_categorical` uses.
2. **Given** the new kinds' phase, **When** inspected, **Then** `_phase_for()` resolves them to
   `QC` (they are simply not added to the `RECONCILE`-inference tuple) — verified directly, not
   assumed, since this is the mechanism that makes Scenario 1 correct with zero extra dispatch code.

---

### Edge Cases

- What happens on the one-side-absent case, given the new kinds default to `QC` phase? →
  `engine.py`'s generic review-reason auto-tagging block only fires `SOURCE_INCOMPLETE` for
  `RECONCILE`-phase `NEEDS_REVIEW` (mirroring `agree_categorical`'s one-side-absent case) — a
  `QC`-phase `NEEDS_REVIEW` gets **no** automatic `review_reason`. The new branches MUST set
  `review_reason="SOURCE_INCOMPLETE"` explicitly (mirroring how `ratio_threshold`'s
  `UNSPECIFIED_THRESHOLD` case already sets its own reason before an early return) — otherwise
  `RunResult.disposition` silently disagrees with the loan's actual status, the same invariant
  `test_loan_disposition.py` already pins for the analogous doc-vs-system case.
- What happens to the ~14-26 additional doc-vs-doc conditions estimated to exist across the full
  8,442-row rulebook, beyond the 5 known synthetic-loan defects? → Explicitly out of scope for this
  feature (Phase 2, a separate future spend decision — see plan.md). This feature proves the engine
  capability and wires the 5 known cases by hand, at zero LLM cost; it does not recompile the
  rulebook.
- What happens when AUS/DU/LPA output (not a raw document, not literally MISMO) is one side of a
  comparison? → Not a new judgment call — `model.py`'s own docstring already establishes AUS/DU/LPA
  output as SYSTEM-side ("a MISMO/ULAD/DU file is just the same lender data in another file format,
  so it feeds SYSTEM too"). These remain ordinary `agree_categorical`/`agree_numeric` checks; the
  compiler applies existing precedent, not a new rule.
- What happens to `Check.to_dict()`/`Ruleset.sha256()` for ruleset content that never uses the new
  kinds (e.g. `demo_ruleset()`)? → The digest changes anyway, because `asdict()` emits every
  dataclass field for every check regardless of kind. This is a real, unavoidable digest bump —
  handled the same way feature `004`'s legitimate digest bump was (new pinned baseline, old baseline
  kept as a historical constant), not worked around by hiding the new field from serialization.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST support two new check kinds, `agree_doc_categorical` and
  `agree_doc_numeric`, each comparing two independently-named fields' document (`truth`) values
  directly — never a `system_value()` on either side.
- **FR-002**: `Check` MUST gain exactly one new field, `compare_field_name: Optional[str] = None`,
  naming the second field for the two new kinds. No other new `Check` fields.
- **FR-003**: A genuine doc-vs-doc mismatch MUST produce `FAIL` (not `FLAG`), tagged
  `review_reason="EXCEPTION"` via the existing generic QC-phase auto-tagging rule — the new kinds
  MUST NOT be added to `_phase_for`'s `RECONCILE`-inference tuple.
- **FR-004**: The one-side-absent case MUST produce `NEEDS_REVIEW` with `review_reason=
  "SOURCE_INCOMPLETE"`, set explicitly by the new branches (not automatic for `QC` phase — see Edge
  Cases). The both-absent case MUST produce `NOT_APPLICABLE`.
- **FR-005**: `agree_doc_categorical` MUST reuse the existing normalizer registry (`name`,
  `address`, `ssn_last4`, `identity`) exactly as `agree_categorical` does — no new normalizer logic.
- **FR-006**: `agree_doc_numeric` MUST reuse the existing `Decimal`/`within_tolerance` comparison
  and the existing `UNSPECIFIED`-tolerance honesty guard exactly as `agree_numeric` does.
- **FR-007**: `p0/qc_engine/catalog.py`'s `validate_referential_integrity()` MUST also resolve
  `compare_field_name` when present, using the same fail-fast pattern as `field_name` — an
  unresolvable `compare_field_name` MUST be caught at load time, not at evaluation time.
- **FR-008**: The compiler (`compile_llm.py`) MUST decide doc-vs-system vs. doc-vs-doc *at compile
  time*, using `expected_sources` (newly added to its `existing_catalog_fields` payload) as the
  load-bearing signal — MUST NOT push this decision upstream into `taxonomy.py`'s blind regex
  classifier, which has no access to that signal.
- **FR-009**: This feature MUST NOT modify `agree_categorical`/`agree_numeric`'s existing semantics,
  `SourceValue`/`model.py`, or the source-independence guard `001b` built — the new kinds are
  additive and never touch `sources{}`.
- **FR-010**: This feature's Phase 1 scope MUST hand-author all 5 known doc-vs-doc defects directly
  in `p0/fixtures/ruleset_defects.py` (zero LLM cost) as its proof; a full/partial recompile of the
  8,442-row rulebook to find additional real-world doc-vs-doc conditions is explicitly Phase 2, a
  separate future decision, not built by this feature.
- **FR-011**: The pre-existing `003c` reconcile tests, `demo_ruleset()`'s checks, and the P0
  determinism digest's *shape-correctness* (a new, re-baselined digest is expected and required —
  see Edge Cases) MUST otherwise be unchanged by this feature.

### Key Entities

- **Check** (existing, `p0/qc_engine/ruleset.py`): gains `compare_field_name: Optional[str] = None`.
  `kind` gains two new legal values, `agree_doc_categorical`/`agree_doc_numeric`.
- **SourceValue**/`CanonicalLoan` (existing, `p0/qc_engine/model.py`): **unchanged** — this feature's
  central design constraint (FR-009).
- 5 known doc-vs-doc defect fixtures (existing test data, `p0/fixtures/from_docs/loan_01.json`,
  `loan_04.json`, `p0/fixtures/from_docs/defect_manifest.json`) — this feature's Phase 1 proof
  target, not new test data to construct.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 5 known doc-vs-doc defects (`employment_start_date_1003`/`_voe`,
  `title_vesting_1003`/`_commitment`, `liability_disclosed_on_1003`/`liability_amount_credit_
  report`, `loan_purpose_1003`/`_cd`, `cd_payoff_amount`/`payoff_statement_amount`) resolve to their
  correct expected status (`FAIL`/`PASS` for the three categorical/complete-data cases,
  `NEEDS_REVIEW` for the liability case where source data is genuinely absent on some loans) —
  verified by test, not just by the loan_01/loan_04 spot-checks that surfaced this gap.
- **SC-002**: Zero instances, across the new test suite, of a doc-vs-doc mismatch appearing as a
  `FLAG` instead of a `FAIL`, or blocking `auto_cleared` incorrectly.
- **SC-003**: `pytest p0/tests -v` passes in full after the digest re-baseline (a new, documented
  `POST_003D_BASELINE`, following the `004` precedent exactly) — zero *unrelated* regressions.
- **SC-004**: `run_010_post_closing_only/run_against_loans.py` (or its updated equivalent) shows
  `title-vesting-1003-vs-commitment` and `employment-dates-1003-vs-docs-agree` resolving `FAIL`/
  `PASS` instead of `NEEDS_REVIEW: "No system value..."`, and loan 04 gets real checks for the
  previously-uncompiled `cd_payoff_amount`/`loan_purpose_1003` defects.

## Assumptions

- This feature is a direct sibling of `003a`/`003b`/`003c` in the reconcile-engine arc — numbered
  `003d` rather than the next open top-level slot, since `005` through `012` are already reserved
  for other planned features (`output/ROADMAP.md`) and this is a continuation of `003c`'s own
  explicitly-declined scope, not a new independent workstream.
- The 5 known synthetic-loan defects are treated as this feature's representative, sufficient proof
  set for Phase 1 — the same "prove the clean case at hand" discipline `003a`/`003b`/`003c` each
  applied to their own representative samples before any real-corpus recompile.
- Phase 2 (recompiling the full 8,442-row rulebook to find the estimated 14-26 additional real
  doc-vs-doc conditions) is explicitly not this feature's scope or cost commitment.
- `005` (the eval-harness CI promotion gate) does not exist yet; this feature ships its own local,
  static eval coverage, consistent with every prior spec in this arc.
