# Research: Real-Engine Audit Run

> **Addendum (live-demo-engine-wiring, 2026-08-02)**: this spec's implementation
> originally ran against `p0/qc_engine` (the pipeline this document describes below), ported
> into this repo from a disconnected worktree. It has since been **rewired to run against
> `engine/`** — the standalone, definitive QC audit engine extracted in `023-standalone-qc-engine`
> (see `engine/README.md`) — because `engine/` is the actively-maintained, more complete pipeline
> (broader field extraction, a fixed predicate-evaluation bug `p0/qc_engine` still carries). The
> design decisions and research below are still accurate in substance; every `p0/qc_engine`
> reference in this document describes the pipeline this feature *originally* targeted, not the
> one the live demo runs today. The live entry point is now
> `engine/qc_engine/run_touchless_audit_for_demo.py`, invoked from
> `backend/src/routes/audit.ts`, with the same input/output contract described here.

Every item below traces to a genuine unknown found while reading the actual code this feature
touches — not a generic survey. Sources are cited inline (file:line where useful).

## 1. The engine's own outcome model does NOT match spec021's severity-tiered status

**Finding**: `p0/qc_engine/engine.py`'s `RunResult.disposition` is binary —
`"NEEDS_REVIEW" if self.review_reasons else "AUTO_CLEARED"` (engine.py:481-490) — driven by
`review_reasons`, a flat set unioned from every `CheckResult.review_reason` regardless of
severity. There is no severity-tiered (CRITICAL vs. WARNING/INFO) split anywhere in the engine's
own disposition logic.

**Decision**: Build a small, new mapping function *outside* `engine.py` (not a change to the
engine itself — Non-Negotiable #1/#2 forbid touching the pure, signed-artifact-driven engine to
special-case one demo's status vocabulary) that derives spec021's loan-level status from a
completed `RunResult`:

```
qc_failures = run_result.qc_failures  # existing property: status in (FAIL, WARNING)
if any(r.severity == "CRITICAL" for r in qc_failures):
    loan_status = "FAILED"
elif qc_failures or run_result.needs_review:
    loan_status = "NEEDS_REVIEW"
else:
    loan_status = "PASS"
```

This reuses `RunResult`'s existing `qc_failures`/`needs_review` properties unchanged — it's a
read-only derivation layer, not new engine logic. Note the terminology collision: the engine's own
per-*check* `CheckResult.status == "NEEDS_REVIEW"` is a different axis from spec021's per-*loan*
`NEEDS_REVIEW` (a severity-tier concept) — but per Item 3 below (confidence scoring is out of scope
entirely for this feature), the per-check path is moot here: every check in this feature's compiled
ruleset is `predicate`/`is_present` kind, whose own evaluation logic (engine.py:319-334) only ever
produces `PASS` or `FAIL`, never `NEEDS_REVIEW` — and the confidence-gate downgrade that could turn
a `PASS` into `NEEDS_REVIEW` never fires either, since `doc_confidence` is never populated (Item
3). So `run_result.needs_review` will always be empty for this feature's runs; the mapping's
`elif` branch above is defensive/future-proofing (e.g. if a later phase adds non-predicate checks
to the compiled set), not something the current check set can actually trigger. Loan-level
`NEEDS_REVIEW` today is reached purely via one or more non-CRITICAL-severity `FAIL` results.

**Alternatives considered**: Modifying `engine.py`'s `disposition` property directly — rejected,
it's a shared, tested, hash-relevant artifact used by other specs (004, 005); special-casing one
demo's vocabulary into it violates the "engine is a pure function" non-negotiable and risks
regressing its existing consumers.

## 2. Gold's 208 `COMPILABLE` checks resolve to only ~30 unique fields, and those fields are document-TYPE identifiers, not fine-grained data points

**Finding**: `python3 -c "..."` against `frontend/src/data/goldCatalog.json` shows the 208
`COMPILABLE` checks resolve to only 30 unique `fieldId` values (`bank_statement`, `paystub`,
`W2`, `tax_return`, `gift_letter`, `schedule_k1`, `URLA_1003_final`, `settlement_statement`, …).
These are **document-type identifiers** — the checks are overwhelmingly `doc_presence`/
`doc_completeness` kind ("is a bank statement present in the file"), inherited from Assets/Income
being the only two gold blocks decomposed to atomic-rule granularity today (per `019`'s own
findings). This is a materially simpler adapter target than deep field-value extraction
(`note_rate`, `loan_amount`-style values) would have been.

**Cross-checked against the real Touchless loan's actual document set**
(`demo/touchless/extracted/loan_application.json`, `applicationId =
0eb57730-6d2e-4a6d-8db3-bc1217c77b90`, from the other repo — not yet ported into this worktree,
see Item 4): its `documents[]` array has **62 real entries** with a `documentType` string per
document (e.g. `"Bank Statement"`, `"Paystub"`, `"W2"`, `"Form 1040"`, `"Schedule K-1 - Form
1065"`, `"Gift Letter"`, `"Purchase Agreement"`). A direct comparison against gold's 30 field
identifiers found:

- **Confidently resolvable** (a real document of that type exists, name is an unambiguous match):
  `bank_statement`, `paystub`, `W2`, `gift_letter`, `schedule_k1`, `tax_return` (→ `Form 1040`),
  `sales_contract` (→ `Purchase Agreement`), `URLA_1003_final` (→ the four `URLA - *` documents,
  combined).
- **Not present in this loan's document set at all** (the loan genuinely lacks that document
  type — a real, honest signal, not a mapping gap): `tax_return_schedule_e`,
  `appraisal_rental_schedule`, `brokerage_rsu_statement`, `credit_card_statement`,
  `earnest_money_deposit_record`, `foreign_asset_documentation`, `lease_agreement`,
  `life_insurance_cash_value_statement`, `military_LES`, `retirement_account_statement`,
  `ssa_award_letter`, `trust_account_statement`, `virtual_currency_exchange_record`.
- **Genuinely ambiguous** (no confident document-type match exists in the 62-document list, and
  it's not clear the concept applies at all to a document-presence check) — `AUS_findings`,
  `DU_findings`, `VOE_form_1005`, `VVOE_record`, `employer_documentation`,
  `income_calculator_findings_report`, `irs_tax_transcript_4506c`, `loan_file_documentation`,
  `settlement_statement` (`Closing Disclosure` is the modern equivalent but not an exact-name
  match — a judgment call, not a certainty).

**Decision**: The compiled P0 ruleset for this feature's audit run MUST be scoped to only the
checks whose evidence field has a **confidently-resolvable** document-type mapping — not all 208.
This is directly backed by the constitution's own Safety Gate: *"a check whose field reference
does not resolve to a catalog entry is a silent no-op (a false-clear vector) and must fail
validation"* — running a check whose field mapping is a guess risks the same failure mode in
reverse (a false *FAIL* from an unmapped document, presented as if it were a genuine missing-
document finding). Phase 2 (adapter) builds the mapping table and empirically measures the
resolvable count; Phase 1 (compiler) filters gold's `COMPILABLE` set down to that measured,
honestly-resolvable subset. The unresolved checks remain visible as `COMPILABLE` in `019`'s
authoring screen (that's a different, correct claim — "a real evidence field resolves against the
canonical field catalog") but are out of scope for *this specific demo loan's audit run* — stated
honestly in the plan, not silently included and pre-emptively fudged.

**Alternatives considered**: Running all 208 anyway and accepting some will show `FAIL` for
missing-mapping reasons — rejected per the Safety Gate above. Building a full NLP/fuzzy-matcher
for perfect document-type mapping — rejected as over-engineering for a single demo loan; a hand-
built lookup table for ~10-15 document types is simpler, auditable, and sufficient.

## 3. Confidence scoring is deliberately out of scope — the adapter never populates it

**Gordon's explicit instruction**: remove confidence scoring from this feature entirely. The
engine is deterministic; a probabilistic per-field confidence score doesn't belong in that story
for this demo, regardless of what Touchless's real API returns.

**Consequence**: `Item 3` originally researched here — Touchless's real OCR confidence values are
on a 0-100 scale, with unexplained values above 100 (`output/TOUCHLESS-API-LIVE-TEST-2026-08-01.md`
Finding 3), which would have needed normalizing against `engine.py`'s `DEFAULT_CONFIDENCE_FLOOR =
0.80` (a 0.0-1.0 scale) — is now moot. The adapter (Item 2's `touchless_to_canonical_loan.py`)
simply never sets `SourceValue.doc_confidence` (leaves it at its default, `None`). `engine.py`'s
existing confidence-gate branch (`if res.status == "PASS" and sv.doc_confidence is not None and
...`) is unmodified and structurally cannot fire when `doc_confidence` is always `None` — this
disables the gate for this feature's runs without touching `engine.py` itself, consistent with the
"the pure engine stays unmodified" constraint elsewhere in this plan. The vendor's own open
confidence-scale question (Tier-2 Q E) remains open and is simply irrelevant to this feature now.

**Alternatives considered**: Normalizing and passing the real confidence value through (the
original plan) — superseded by explicit instruction. Removing the confidence *concept* from
`engine.py`/`model.py` globally — rejected; those are shared, tested primitives other specs may
still use `doc_confidence` for (e.g. reconcile-phase checks elsewhere in the project); this
feature simply doesn't feed it a value, it doesn't delete the capability.

## 4. The real Touchless loan's cached JSON snapshot is not yet in this worktree

**Finding**: `demo/touchless/extracted/{loan_application.json, extracted_data_*.json}` exist in
the other (standalone) repo this session already ported `020`'s work from, but were not part of
that port (only `backend/`, `frontend/`, `specs/020-*`, and two `output/` docs were copied —
`demo/` was out of scope for that commit). They don't exist in this worktree yet.

**Decision**: Port `demo/touchless/` (both `original/` and `extracted/` subdirectories) into this
worktree as a Phase 0 implementation step, same pattern already used for `020`'s port. This is
real, already-fetched Touchless data — not something to re-derive or re-fetch. Directly relevant:
this data is what the adapter's document-type mapping table (Item 2) is measured against.

## 5. Server-side Python invocation from the Node backend has no existing precedent to reuse

**Finding**: `backend/src/` (spec020) is entirely TypeScript/Express; nothing there spawns a
Python process today. `p0/qc_engine/` is Python 3.9-compatible per project convention
(`CLAUDE.md`, constitution Development Workflow) — this feature's compiler/adapter/engine
invocation stays Python, not a rewrite into TypeScript (that would fork the engine into two
maintained implementations, a much larger and unrequested undertaking).

**Decision**: A single new Python entry-point script (e.g.
`p0/qc_engine/run_touchless_audit_for_demo.py`) takes a loan-application JSON payload (stdin or a
temp file path) and the compiled ruleset path as arguments, runs Phase 1's compiler +Phase 2's
adapter + `engine.run()` inline, and prints one JSON object (the `RunResult.to_dict()` plus the
derived loan-status from Item 1) to stdout. The new backend route spawns this via Node's
`child_process.execFile` (not `exec`, to avoid shell-injection surface — the applicationId is
already UUID-validated upstream by `020`'s existing `isValidUuid()` guard, reused here), captures
stdout, and parses it as the API response body.

**Alternatives considered**: A long-running Python service the Node backend calls over HTTP —
rejected as unnecessary operational complexity (a second process to manage, health-check, restart)
for a single-shot, sub-second computation with no need for persistent state between calls.

## 6. `AuditLog` (hash-chained SQLite audit trail) exists but is out of scope

**Finding**: `p0/qc_engine/audit.py` provides a tamper-evident, hash-chained audit log — a real,
tested capability. Nothing in spec021 requests persisted audit-trail storage across demo runs.

**Decision**: Not used for this feature. `RunResult` is returned directly to the frontend and
displayed; nothing is persisted to `AuditLog`'s SQLite store. Revisit only if a future spec
explicitly asks for cross-session audit-trail durability.

## 7. Existing frontend context/state pattern to reuse for cross-navigation persistence

**Finding**: `frontend/src/lib/dataSourceContext.tsx` (from `020`) already provides a React
context wrapping the whole app (`DataSourceProvider` in `App.tsx`) holding fetched-application
state above any single view. `frontend/src/lib/rulesetStore.ts` (from `019`'s Phase 5) already
demonstrates the auto-persist/hydrate pattern this feature's `RUNNING`→verdict state needs.

**Decision**: The audit-run state (which loan is running, its last verdict) lives in
`dataSourceContext.tsx` (extending it) rather than component-local state in `LoanDetail.tsx` — so
navigating away and back reflects the true current state, per the spec's documented Assumption.
This also gives `RESTORE_TO_GOLD` (FR-007) a single place to clear from.

## 8. A real exception's citation has no way to open the real source document — a genuine gap, not covered by the original plan

**Finding** (raised directly by Gordon, verified before responding): `p0/qc_engine/model.py`'s
`DocCitation` carries only human-readable text (`doc_name`/`page_num`/`segment_snippet`/
`document_title`/`section`/`field_label`) — no Touchless `documentId`. `020` already built a real
"fetch and view the actual PDF by `documentId`" capability (`RetrievedDocumentViewer.tsx` + the
backend's document-read route), but today it's wired only from `LiveApplicationPanel.tsx`
(browsing the loan's raw document list) — never from a check, citation, or exception.
`ExceptionReview.tsx`'s existing citation-click modal is explicitly a **placeholder**: its own copy
reads *"PDF page render placeholder — deep-links to {doc}#page={page}"*. Without a fix, this
feature's real, engine-computed exceptions (User Story 1) would still show only a text label on
click — the product's own core traceability claim ("if they don't understand how you calculated
that number, you buy back the loan") would not actually hold for this feature's output.

**Decision**:
1. Extend `DocCitation` with one new optional field, `document_ids: Optional[List[str]] = None`
   (plural/list-shaped, not a single string — Item below explains why) — additive and
   backward-compatible, following the exact same precedent already set when `document_title`/
   `section`/`field_label` were added (`model.py`'s own docstring documents that precedent
   directly). `to_dict()` emits `documentIds` only when populated, same convention as the other
   optional fields. This is the one narrow, precedented exception to "the engine's data model
   stays unmodified" elsewhere in this plan — metadata only, no new evaluation logic, no change to
   any `engine.py` dispatch behavior.
2. The Touchless adapter (Item 2) captures the real `documentId`(s) of whichever document(s) in
   `documents[]` matched a given `doc_presence` check's document-type mapping, and populates
   `document_ids` with all of them — **not** just the first match. Confirmed with Gordon: a check
   like `URLA_1003_final`, which maps to a set of 4 real document types, must show **all 4** as
   separately clickable links, not collapse to one.
3. `ExceptionReview.tsx`'s citation-click flow is rewired to render one clickable link per
   `documentIds` entry, each opening `020`'s existing `RetrievedDocumentViewer` (reused verbatim,
   not rebuilt) — replacing the current placeholder modal entirely for this feature's real
   exceptions. A check whose evidence field had no confidently-resolvable document (excluded from
   the compiled ruleset per Item 2, so this shouldn't arise for anything actually run — but stated
   for completeness) would show zero links with an honest "no document identified" note, never a
   dead/broken link.

**Alternatives considered**: A single scalar `document_id` field, using only the first match for
multi-document checks — rejected per Gordon's explicit instruction (all matches must be individually
clickable, not collapsed). Building a new document viewer specific to this feature — rejected;
`020`'s `RetrievedDocumentViewer` already does exactly this job and reusing it avoids a second,
divergent implementation of the same PDF-fetch-and-render behavior.

## Summary of resolved unknowns

| Unknown | Resolution |
|---|---|
| Loan-status derivation from engine output | New pure mapping function over `RunResult.qc_failures`/`needs_review`, severity-tiered |
| Which of gold's 208 checks can honestly run against real Touchless data | Empirically measured via a document-type mapping table; only the confidently-resolvable subset is compiled in |
| Confidence scoring | Out of scope entirely (Gordon's explicit call) — adapter never populates `doc_confidence`; the engine's confidence gate is structurally never triggered, unmodified |
| Missing `demo/touchless/` data in this worktree | Port from the other repo as a Phase 0 step |
| Python↔Node bridge | `child_process.execFile` calling a new single-purpose Python entry-point script, stdin/stdout JSON |
| Audit-trail persistence | Out of scope; not requested |
| Cross-navigation state | Extend `dataSourceContext.tsx`, matching `019`/`020`'s existing patterns |
| Citation → real document link-through | New `document_ids: List[str]` field on `DocCitation` (additive, precedented); adapter populates all matched documents; `ExceptionReview.tsx` reuses `020`'s `RetrievedDocumentViewer`, one link per document |
