# Feature Specification: Real-Loan Distribution Eval

**Feature Branch**: `012-real-loan-distribution-eval`
**Created**: 2026-07-27
**Status**: Implemented -- Phase 1 (2026-07-28, all 4 committed test files green -- `test_real_loan_adapter.py`,
`test_real_loan_audit_trace.py`, `test_pii_scan_gate.py`, `test_bakeoff_real.py` -- 26 new tests, zero
regression against the pre-existing suite, 389 passed/0 failed/3 skipped total). US1/US2 are fully
proven, against a hand-authored synthetic stand-in bundle mirroring the real S3 shape (per plan.md's own
design -- CI needs no live AWS creds): `p0/eval_real/adapter.py` (`RealLoanAdapter`, FR-001/002),
`mapping_gaps.py` (FR-004), the FR-003 `test_properties.py` hardening (`prov.get('mutations', [])`), and
`audit_trace.py` (`run_and_append`/`build_examiner_trace`, FR-007/008, `verify_chain()` True/False
including tamper simulation) all pass. US3's mechanism (`bakeoff_real.py`, reusing
`experiment_g3/bakeoff.py`'s own locked `PRICING`/`REGIONAL_PREMIUM`/`SCALE_LOANS` constants unmodified)
is built and tested: the D2/BLOCKED path (FR-011) and the D3 cost/token path (FR-010) both pass against
a synthetic stand-in + a fake, offline `evaluate_fn`. `s3_client.py` (T003) is built and AWS-reachable
(`sts get-caller-identity` verified against profile `gordon-chan` this session) but its live 3-loan
fetch was not exercised this session -- see below. **Genuinely gated on external state, not fabricated:**
(a) **expert-adjudicated verdict labels (G1)** do not exist for any real loan -- US3's real D1/D2 re-run
(FR-009) and SC-005 stay `BLOCKED`, exactly as FR-011 requires; only the label-independent D3 cost
mechanism is proven (against a synthetic stand-in, not yet a real full-extraction payload); (b) **the
live 3-real-loan run itself (T012, SC-001's live variant)** -- converting the actual `301224293`/
`301224442`/`301224735` S3 extraction bundles through the adapter -- was not executed this session;
`p0/eval_real/local_cache/` and `s3_client.py` exist and AWS access was verified, but the bundles were
not fetched/adapted this pass, so SC-001's "all 3 real loans, zero crashes" and SC-006's real-payload
token/cost figure remain the honest residual, not claimed. FR-006's `qc_doc_extraction.py` (the
third-party QC-document extraction shortcut) and US4's `011` corpus-shape reconciliation (011 itself is
`DEFERRED`, per its own spec Status) are out of scope for this pass -- no committed test requires them,
and building them speculatively against a not-yet-built consumer would risk exactly the kind of
un-grounded work this project's non-negotiables warn against.
**Input**: `output/ROADMAP.md` §012: "Ingest real expert-labeled loans as just another source into 005's
`score()`; the synthetic eval becomes the regression floor, real loans the distribution check. Run the
mock-audit exit criterion (an examiner can trace any number to inputs/rounding/rule-version/citation).
Re-run the G3 bake-off on real loans."

**Governs**: `output/ROADMAP.md` §012, `.specify/memory/constitution.md` Principle III (Eval is
foundational — item 3 of its own three-question decomposition: "defect distribution +
extraction/OCR realism... the honest residual; it is the only piece that genuinely needs real
files"), Principle I (the G3 bake-off's own stated remaining gate: "the real-loan re-run is the one
remaining gate," `p0/experiment_g3/RESULTS.md`), the Audit quality gate (every doc-sourced value
traceable; every verdict carries field-level intermediates).

**Depends on**: `005-eval-harness-as-promotion-gate` (this feature's real loans are ingested as an
*additional* GOLDEN/VOLUME source into 005's tiered gate, per 005's own FR-010/US5 — 012 does not
build a second scorer). `007-audit-trail-and-citation-of-record` (IMPLEMENTED — this feature proves
`p0/qc_engine/audit.py`'s already-built hash chain and citation trail against a real loan; it does not
build new traceability machinery). `011-label-confirmation-flywheel` (specced concurrently this
session — 012's real-loan corpus is read/grown by the *same* confirm/correct mechanism 011 builds,
not a parallel store; see Assumptions).

**Foundation this builds on** (confirmed by direct inspection this session, not assumed):

- `p0/eval_synth/README.md` lines 86-92 ("When real loans arrive") and `p0/eval_synth/eval.py`'s own
  module docstring (line 7) both describe real-loan ingestion as pure future work — **no real
  (non-synthetic) loan has ever been ingested through this harness.**
- `p0/eval_synth/test_properties.py`'s `score()` function (line 54) takes `loans: List[G.LabeledLoan]`,
  where `LabeledLoan = Tuple[CanonicalLoan, Dict[str, str], Dict[str, Any]]` (`generator.py:43`) — a
  **plain tuple**, not a class bound to synthetic generation. This is the literal seam this feature
  targets: anything that produces this exact 3-tuple shape scores identically, per 005's own FR-010
  design commitment.
- **A gap this feature's own inspection found, not previously documented anywhere:** `score()`'s
  mismatch-message formatting (`test_properties.py`, inside the per-check loop) does
  `'; '.join(prov['mutations']) or 'clean'` unconditionally on every mismatch — a `prov` dict lacking
  a `"mutations"` key raises `KeyError` the instant any newly-scored tuple mismatches. The "harness
  absorbs real loans with no rework" claim (`p0/eval_synth/README.md`'s own words, repeated in
  `output/ROADMAP.md`'s Sequencing Rationale §5 and §8) is **true for the scoring logic itself**, but
  has one previously-unstated shape requirement — a real-loan `prov` dict must carry `"mutations": []`
  (empty, not absent) — and one previously-unstated fragility (the unconditional dict access) this
  feature must either satisfy by convention (FR-002) or harden directly (FR-003), named honestly
  rather than discovered as a crash the first time a real loan produces a mismatch.
- `p0/qc_engine/audit.py` — `AuditLog.append` (lines 58-77) and `verify_chain()` (lines 79-93) are
  fully implemented and already proven end-to-end against **synthetic** artifacts
  (`p0/eval_synth/artifacts/synth_eval_audit_verify.json`, per `007`'s roadmap entry). This feature is
  the first time that chain is exercised against a **real** loan's actual citations — genuinely
  different risk, since real `DocCitation` page numbers/snippets come from messy real PDFs (348+ pages
  per loan below), not hand-authored synthetic ones.
- **Real ground-truth loans are already acquired — this materially refines the roadmap's own "G1 real
  labeled loans (Kayla)" framing, confirmed by direct inspection this session, not assumed from prior
  memory.** `aws s3 ls s3://mortgage-qc-extraction/results/ --profile gordon-chan` lists 3 real closed
  loans, each with a full extraction bundle in the exact shape this project's own inbound contract
  expects (extracted fields + document classification + per-field citation, `CLAUDE.md`'s Touchless
  contract, `001b`'s consumed interface):

  | Loan | Total docs | Fields extracted | Doc-vs-system discrepancies logged |
  |---|---|---|---|
  | `301224293` | 348 | 67 | 11 |
  | `301224442` | 213 | 65 | 16 |
  | `301224735` | 343 | 53 | 12 |

  Each loan folder carries `{loan}-ulad.json` (a structured ULAD-shaped summary: borrowers, employment,
  income, property, loan detail), `{loan}-citations.json` (per-field doc-vs-XML **discrepancy** records,
  each with `text_snippet`, `page`, `confidence`, `document`, `document_type` — directly analogous in
  shape to this project's own `DocCitation`/`doc_confidence`), `classification.json`, `{loan}-
  documents.json`, `extraction-summary.json`, and 18-24 `consolidated/{doctype}.json` files (appraisal,
  assets, closing, compliance, credit, income, insurance, paystub, promissorynote, title, urla1003,
  etc.). **This means the "acquire real loans" half of G1 is done** — what remains genuinely external
  and ungated is narrower: **expert-adjudicated per-check verdict labels**, not the loan files or their
  machine extraction. This spec states that distinction precisely rather than inheriting the coarser
  "real loans haven't arrived" framing uncorrected.
- **A further, more specific finding: each real loan's own closed-file bundle already contains a real
  third-party post-closing QC/audit document, classified but not yet field-extracted** —
  `consolidated/qcchecklist.json` (`document_type: "qcchecklist"`) lists, per loan:
  - `301224293`: "Report Card - Omissions, Discrepancies, 1004MC, Public Records" (PDF page 79),
    "Snapdocs Post-Close QC Report" (pages 1146-1148).
  - `301224442`: "Document Package Audit Report" (505-506), "DUAL AUS Audit Report - Fannie Mae and
    Freddie Mac" (x2, pages 576 and 602), "FraudGuard Variance Summary and Findings" (1068-1074),
    "Ability-To-Repay Worksheet" (1142-1145), "Debt/Obligation Information Worksheet" (1147).
  - `301224735`: "Underwriting Conditions" (138-139), "DUAL AUS Audit Report - Fannie Mae and Freddie
    Mac" (659), "Loan Notes and Activity Log" (x2, 1089 and 1096), "Snapdocs Post-Close QC Report"
    (1133-1134).

  Every one of these instances carries `"fields": {}` — the current extraction pipeline classifies
  these documents by type but has **no field-extraction pattern for their content yet.** This is a
  real, not-yet-exploited shortcut: extracting and reconciling *these* documents' own findings against
  this project's AMQ check taxonomy is a materially cheaper path to expert-adjudicated labels than
  asking an SME to QC 3 loans against ~800 checks from a blank page. It does not eliminate the G1
  dependency (reconciling a third-party vendor's own finding taxonomy onto this project's specific
  check IDs is still genuine SME judgment, not automatable) — it substantially cheapens it, and this
  spec scopes the extraction half of that shortcut in (FR-006).
- **PII risk, confirmed directly, not assumed:** `301224293-ulad.json` and `301224293-citations.json`
  both carry real values in plain text — real borrower names ("Jose Alejandro Oviedo Sanchez", "Sydney
  Morgan Ansley"), `ssn_last4` fragments, and a real property address ("11774 SW 133rd Court, Miami, FL
  33186"). A sibling demo project (`demo-sites/dynamic-mortgage-qc`, drawing on what its own memory
  describes as the same S3 bucket) explicitly built a synthetic stand-in loan specifically because its
  "3 real loan files carry PII (13 SSNs, real names/addresses) and can't go in shared/committed
  artifacts." **This repository (`mortgage-qc-prod`) has no equivalent established redaction/exclusion
  discipline today** — `.gitignore` excludes `demo/` with the comment "may carry PII" but nothing
  currently governs a *new* real-loan ingestion path this feature introduces. This is a named, HIGH
  risk this spec's own requirements must close structurally (FR-012), not discover after a commit.
- `field_catalog.json` carries 379 entries (per `005`'s own count) derived from the **5 synthetic**
  `demo/syn/loan 0{1-5}` document sets — not from the real loans' own ~18-24 document types. The
  mapping between the real bundles' extraction shape and this project's canonical field vocabulary is
  real, non-trivial adapter work (FR-001/004), not a drop-in format conversion.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A real, already-acquired loan scores through the existing harness with zero scorer rework (Priority: P1)

Today, `p0/eval_synth`'s scorer has never seen a real loan. This feature proves the roadmap's own
design claim — "the harness is built to absorb real loans with no rework" — against a genuine article,
not a constructed stand-in (which is all `005`'s own US5 could do, since `012` didn't exist yet when
`005` shipped).

**Why this priority**: This is the literal first scope item from `output/ROADMAP.md` §012 ("ingest real
expert-labeled loans as just another source into 005's `score()`") and the precondition for both other
user stories — without a working adapter, there is no real loan to audit-trace or bake off against.

**Independent Test**: Convert one of the 3 already-acquired real loans (`301224293`, `301224442`, or
`301224735`) into a `CanonicalLoan` via the adapter, pair it with a placeholder or partial
expert-verdict set, and feed the resulting `(loan, expected, prov)` tuple through the existing,
byte-for-byte unmodified `score()` function; confirm it returns a well-formed report with no code
change to `score()`'s signature.

**Acceptance Scenarios**:

1. **Given** one real loan's extraction bundle (`{loan}-ulad.json` + `{loan}-citations.json` +
   `consolidated/*.json`), **When** the adapter runs, **Then** it produces a `CanonicalLoan` whose
   `fields` are populated from the bundle, using `field_catalog.json`'s existing canonical names where
   a mapping exists.
2. **Given** the adapter's output paired with any `Dict[str, str]` expected-verdict set (even a
   partial one covering only checks with known labels), **When** the tuple is passed to
   `test_properties.score()` unmodified, **Then** it scores without a `KeyError` or any other crash,
   producing `checks_scored`/`exact_match`/`false_auto_clear_count` fields in the same shape as a
   synthetic tuple would.
3. **Given** a real extracted field whose name resolves to no `field_catalog.json` entry, **When** the
   adapter runs, **Then** the gap is recorded as an explicit, named mapping-gap entry in the adapter's
   own report — never silently dropped and never silently coerced into a null `SourceValue`.
4. **Given** all 3 already-acquired real loans, **When** each is run through the adapter, **Then** all
   3 produce valid `CanonicalLoan` objects with zero adapter crashes.

---

### User Story 2 - An examiner can trace any real loan's verdict back to its inputs, rounding, rule version, and citation (Priority: P1)

"If they don't understand how you calculated that number, you buy back the loan" (`CLAUDE.md`'s
non-negotiable #1). `007` already built the mechanism (the hash chain, `verify_chain()`, the
`DocCitation` -> `CheckResult` -> `RunResult.to_dict()` -> audit-payload flow) and already proved it once
— against synthetic data. This feature proves the mechanism holds up against the genuinely messier
case: a real loan's real citations (a 348-page real PDF, a real page number, a real extracted snippet),
not a hand-authored synthetic one.

**Why this priority**: Equal to US1 — this is the roadmap's second named scope item ("run the mock-audit
exit criterion... using a REAL loan as the test case") and the pilot exit criterion's audit-defensibility
half.

**Independent Test**: Run the existing, unmodified `qc_engine.engine.run` against one adapted real
loan, append the resulting `RunResult` to a real `p0/qc_engine/audit.AuditLog`, call `verify_chain()`,
and produce a human-readable trace for one `PASS` verdict and one `FAIL`/`FLAG` verdict that an
examiner could follow start to finish without reading engine source code.

**Acceptance Scenarios**:

1. **Given** a real, adapted loan run through the unmodified engine, **When** its `RunResult` is
   appended to a real `AuditLog`, **Then** `verify_chain()` returns `True`.
2. **Given** that same `AuditLog`, **When** any single historical record's payload is deliberately
   altered (a tamper simulation), **Then** `verify_chain()` returns `False` — proving the chain's
   tamper-detection holds for a real-loan-seeded log exactly as it already does for a synthetic one.
3. **Given** one real `PASS` verdict and one real `FAIL`/`FLAG` verdict from the same run, **When** an
   examiner-trace report is generated for each, **Then** it names: the rule id, the signed ruleset's
   version and SHA-256 hash, every input `SourceValue` (truth and system-side), any normalization/
   rounding applied, the resulting verdict, and — for any doc-sourced value — the real source document
   name, page number, and extracted segment (not a synthetic placeholder).

---

### User Story 3 - The G3 bake-off re-runs on real loans, converting the accuracy claim from directional to load-bearing (Priority: P2)

The G3 bake-off (`p0/experiment_g3/RESULTS.md`) ran on 6 **synthetic** golden loans and 26 checks —
decisive for determinism, but its own Limitations section names its accuracy finding as directional
("small N... 25/26 on six hand-authored [loans]... [decisive] on-the-boundary accuracy on *real* loans
is exactly what we don't yet know"). This feature re-runs the same locked methodology
(`p0/experiment_g3/bakeoff.py`/`llm_arm.py`) against the 3 real loans, and separately closes a second,
smaller gap this project's own memory already flagged: the "$700-$3,500/10k-run" real-extraction-scale
cost figure was reasoned, not measured — G3's own `$27-$70/10k-run` number came from a ~1.1K-token
synthetic payload, an order of magnitude or more smaller than a real loan's extraction payload.

**Why this priority**: Lower than US1/US2 because it is gated on expert-adjudicated labels (a real,
still-open external dependency, G1) existing for at least some checks — this story is the roadmap's
third scope item, but the *cost* half (FR-010) can and should ship even before any label exists.

**Independent Test**: Once expert-adjudicated verdict labels exist for at least one check on at least
one real loan, re-run Arm A (compiled engine) vs. Arm B (governed runtime-LLM, `temperature=0`) against
that labeled subset and report the same D1 (determinism)/D2 (accuracy/false-auto-clear) axes
`RESULTS.md` reported for the synthetic 6-loan sample. Independent of labels: measure Arm B's real
per-loan token count/cost against a real, full-extraction-scale payload and report an actual D3 number.

**Acceptance Scenarios**:

1. **Given** expert-adjudicated labels exist for >=1 check on >=1 real loan, **When** the bake-off
   re-runs, **Then** it reports D1 (byte-identical across N runs, per model) and D2 (exact-match rate,
   false-auto-clear count) for the real-loan labeled subset, in the same report shape as
   `RESULTS.md`'s existing table.
2. **Given** no expert-adjudicated labels exist yet for any real loan, **When** the bake-off is asked to
   run, **Then** the accuracy/D2 comparison is reported as explicitly `BLOCKED` (naming the missing
   dependency), never silently skipped or omitted from the report.
3. **Given** at least one real loan's full extraction-scale payload (not the ~1.1K-token synthetic one),
   **When** Arm B is run against it, **Then** the system reports a real, measured token count and an
   extrapolated cost-at-10k-loans figure — replacing the "reasoned, not computed" $700-$3,500 range
   with an actual number, whatever that number turns out to be.

---

### User Story 4 - The real-loan corpus is the same corpus 011 grows, not a parallel one (Priority: P3)

`011-label-confirmation-flywheel` is specced concurrently with this feature and is explicitly the
mechanism that captures SME confirm/correct on cited engine outputs to grow the labeled corpus over
time. This feature must consume/validate against that corpus at a point in time — it must not stand up
a second, competing labeled-loan store.

**Why this priority**: Lowest, because it is an integration-boundary correctness concern, not new
end-user-visible capability — but still worth stating explicitly given both features are being
specced in the same session and could otherwise drift into overlapping stores.

**Independent Test**: Confirm the real-loan `(loan, expected, prov)` tuples this feature's adapter
produces are structurally identical to whatever `011`'s own corpus-entry shape defines (once `011`'s
spec lands) — same loan identity, same expected-verdict dict shape, same provenance-tagging
convention (`"source": "expert-labeled"`).

**Acceptance Scenarios**:

1. **Given** `011`'s labeled-corpus entry shape (once specced/built), **When** this feature's adapter
   output is compared against it, **Then** no field-shape translation layer is required to move an
   entry from one to the other — they are the same shape, read by two different consumers (the
   promotion gate here vs. the confirm/correct UI in `011`).

---

### Edge Cases

- A real loan's extracted field name has no `field_catalog.json` counterpart at all -> recorded as a
  named mapping gap (FR-004; US1 Acceptance Scenario 3), mirroring `005`'s own precedent that an
  unresolved reference is a dependency failure to surface loudly, not a construction-strategy gap to
  paper over.
- Only some of a real loan's ~800 potential checks have expert labels, not all -> the adapter and
  scorer must score only the labeled subset; an unlabeled check is excluded from `checks_scored`, never
  treated as an automatic pass, fail, or false-auto-clear (FR-005/FR-009).
- A real loan's own pre-existing third-party QC document (Snapdocs report, DUAL AUS audit, FraudGuard
  summary) disagrees with this project's AMQ-derived verdict for an overlapping concern -> this is not,
  by itself, a false-auto-clear against *this project's* ground truth (a different vendor's taxonomy is
  not automatically this project's own check-by-check ground truth) — it is surfaced as a named
  discrepancy requiring SME reconciliation (G1), never silently auto-resolved in either direction
  (FR-006).
- Any artifact this feature would otherwise write touches a real PII value (name, address, SSN
  fragment) -> MUST NOT be committed to this git-tracked repository in raw form (FR-012); see Risks.
- Expert-adjudicated labels do not exist for any check on any real loan by the time this feature ships
  -> US3's accuracy re-run is explicitly `BLOCKED` in its own report (FR-011), while the cost/token
  measurement (FR-010) still ships independently, since it needs no labels at all.
- A real loan's extraction bundle's document set (18-24 `consolidated/{doctype}.json` types) does not
  correspond 1:1 to the 5 synthetic loans' document set the field catalog was built against -> treated
  as an expected, real adapter-engineering finding (not a design flaw), tracked via the same
  mapping-gap mechanism as FR-004, not solved by inventing new catalog fields speculatively.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system SHALL provide an adapter that converts one already-acquired real loan's
  extraction bundle (`{loan}-ulad.json`, `{loan}-citations.json`, `consolidated/*.json`, per the S3
  layout confirmed in this spec's Foundation section) into a `CanonicalLoan`, mapping each real
  extracted value onto an existing `field_catalog.json` canonical field name where a mapping exists,
  and populating `SourceValue.truth`/`sources`/`citation`/`doc_confidence` from the bundle's own
  discrepancy/confidence records.
- **FR-002**: The adapter SHALL emit output in the exact existing `LabeledLoan` tuple shape
  (`Tuple[CanonicalLoan, Dict[str, str], Dict[str, Any]]`, `generator.py:43`) — no new type, no scorer
  signature change — with the provenance dict carrying at minimum `{"mutations": [], "source":
  "expert-labeled", "loan_id": <real loan id>}`.
- **FR-003**: `test_properties.score()`'s existing mismatch-message formatting MUST NOT raise a
  `KeyError` when scoring a real-loan tuple whose provenance is shaped per FR-002 — the system SHALL
  harden that one call site (e.g. `prov.get("mutations", [])`) as a minimal, explicitly-scoped patch,
  named honestly as the one piece of "harness rework" this feature's own inspection found necessary
  against the "no rework" claim, rather than silently patched without disclosure.
- **FR-004**: IF a real loan's extracted field name does not resolve to any `field_catalog.json` entry
  THEN the adapter SHALL record it as an explicit, named mapping-gap entry in its own report — never
  silently dropped, never silently coerced into an absent/null `SourceValue`.
- **FR-005**: Expected-verdict labels (the `Dict[str, str]` half of the `LabeledLoan` tuple) MUST come
  from an expert-adjudicated source — the adapter is a pure format-conversion layer over already-
  extracted field data; it MUST NOT itself infer or derive what a real loan's correct QC verdict is.
  Interpreting a real loan's correct verdict remains the explicitly out-of-scope G1 dependency.
- **FR-006**: WHERE a real loan's own closed-file bundle already contains a classified-but-
  field-unextracted third-party post-closing QC/audit document (a `consolidated/qcchecklist.json`
  instance with `"fields": {}` — e.g. "Snapdocs Post-Close QC Report," "DUAL AUS Audit Report - Fannie
  Mae and Freddie Mac," "FraudGuard Variance Summary and Findings," per the specific instances named in
  this spec's Foundation section) THE system SHOULD provide the extraction pattern needed to pull that
  document's own findings into a structured, per-check-mappable form — cheapening the SME labeling
  task from de novo adjudication to reconciliation against an existing third-party finding set, without
  itself performing that reconciliation (which remains G1, human judgment).
- **FR-007**: The system MUST run the existing, unmodified engine evaluation path
  (`qc_engine.engine.run`) against at least one real, adapted loan and append the resulting
  `RunResult` to a real `p0/qc_engine/audit.AuditLog`, then call `verify_chain()` and confirm it
  returns `True`.
- **FR-008**: For at least one real `PASS` verdict and at least one real `FAIL`/`FLAG` verdict from the
  same run, the system SHALL produce a human-readable examiner-trace report naming: the rule id, the
  signed ruleset's version and SHA-256 hash, every input `SourceValue` (truth and system-side), any
  normalization/rounding applied, the resulting verdict, and — for any doc-sourced value — the real
  source document name, page number, and extracted segment.
- **FR-009**: WHEN expert-adjudicated labels exist for at least one check on at least one real loan
  THE system SHALL re-run the locked G3 bake-off methodology (`p0/experiment_g3/bakeoff.py`/
  `llm_arm.py`, `temperature=0`, Arm A compiled engine vs. Arm B governed runtime-LLM) against that
  labeled subset, reporting D1 (determinism) and D2 (exact-match rate, false-auto-clear count) in the
  same shape as `RESULTS.md`'s existing table.
- **FR-010**: The system SHALL separately measure and report Arm B's real per-loan token count and an
  extrapolated cost-at-10k-loans figure using a real, full-extraction-scale payload from at least one
  already-acquired real loan (not the ~1.1K-token synthetic payload G3's original run used) —
  independent of whether any expert label yet exists.
- **FR-011**: IF expert-adjudicated labels do not exist for any check on any real loan at the time this
  feature ships THEN the accuracy/D2 re-run (FR-009) SHALL be reported as explicitly `BLOCKED` (naming
  the missing dependency) rather than silently omitted, and the cost measurement (FR-010) SHALL still
  be produced and reported independently.
- **FR-012**: This feature MUST NOT commit any raw real-loan field value, borrower name, address, or
  SSN fragment to any git-tracked file in this repository. Every artifact this feature produces that
  would otherwise carry a real value MUST be either (a) written only to a `.gitignore`-excluded,
  local-only, regenerable location, or (b) redacted (real values replaced with a stable, non-reversible
  placeholder) before being written to any git-tracked path.
  - **Known limitation, documented not fixed (2026-07-27, constitution-alignment audit) — not urgent,
    address before real loan data is actually ingested, not blocking this spec:** a "stable" placeholder
    (the same real SSN always redacting to the same placeholder value) closes the *reversibility* risk
    (nobody can recover the real SSN from it) but not a *correlation* risk — the same stable placeholder
    appearing on two different loan records would still reveal that they belong to the same real person,
    without ever exposing the actual SSN. This wasn't in scope for this pass; whoever implements FR-012
    should decide then whether cross-loan linkability is an acceptable risk for this feature's specific
    use (internal eval corpus, not a public artifact) or whether the placeholder needs to be salted
    per-loan (trading away the ability to notice legitimate same-borrower cases across loans).
- **FR-013**: This feature MUST NOT build real-loan acquisition (already done, confirmed via direct S3
  inspection in this spec's Foundation section) or expert-label authoring itself (G1, the SME/Kayla
  dependency) — only the ingestion adapter, the audit-trace proof, and the bake-off re-run mechanics.
- **FR-014**: This feature MUST NOT modify `p0/eval_synth/generator.py`'s existing synthetic mutation
  operators, `p0/qc_engine/engine.py`'s evaluation logic, or `p0/qc_engine/audit.py`'s chain mechanism
  — all three are consumed unmodified, matching `005`'s and `007`'s own "promote/prove, don't rewrite"
  precedent.
- **FR-015**: After this feature ships, the synthetic eval (`p0/eval_synth`, `005`'s GOLDEN/COVERAGE/
  VOLUME tiers) MUST continue to serve as the regression floor — real loans are an *additional*
  GOLDEN/VOLUME source per `005` FR-010, never a replacement for the constructed-label suite
  (constitution Principle III).

### Key Entities

- **RealLoanAdapter** (new): converts one real loan's S3 extraction bundle into a `CanonicalLoan` +
  `LabeledLoan`-shaped tuple (FR-001/002), also producing a `MappingGapReport` (FR-004).
- **MappingGapReport** (new): the named list of real extracted fields with no `field_catalog.json`
  counterpart, produced per adaptation run.
- **ExpertLabelSet** (new, external-input contract, not authored by this feature): the `Dict[str, str]`
  of check-id -> expected-verdict this feature's adapter consumes but does not produce (FR-005) — the
  shape Kayla's/the SME's G1 sign-off must eventually fill.
- **ExaminerTraceReport** (new): the human-readable, per-verdict audit walk (rule id, ruleset version/
  hash, input `SourceValue`s, rounding, verdict, real `DocCitation`) produced against a real loan
  (FR-008).
- **RealLoanCorpusEntry** (new, shared shape with `011`): one real loan's adapted-loan identity + its
  currently-available label coverage — the record both this feature and `011`'s flywheel read/write
  against (User Story 4).
- **G3RealRerunResult** (new): the real-loan re-run's D1/D2/D3 report, extending
  `p0/experiment_g3/RESULTS.md`'s existing table shape with a real-payload-measured D3 cost figure
  (FR-009/010).
- **CanonicalLoan / SourceValue / DocCitation / LabeledLoan / RunResult / AuditLog** (existing,
  `p0/qc_engine/model.py`, `p0/eval_synth/generator.py`, `p0/qc_engine/engine.py`,
  `p0/qc_engine/audit.py`): all consumed unmodified except the one narrow hardening in FR-003.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 3 already-acquired real loans (`301224293`, `301224442`, `301224735`) convert through
  the adapter into valid `CanonicalLoan` objects with zero adapter crashes, and each resulting `(loan,
  expected, prov)` tuple scores through the existing, byte-for-byte unmodified `score()` function
  without error.
- **SC-002**: `verify_chain()` returns `True` for a real `AuditLog` seeded with all 3 real loans'
  `RunResult`s, and returns `False` when a deliberate tamper simulation alters one historical record —
  proving the chain's real-loan behavior matches its already-proven synthetic behavior in both
  directions.
- **SC-003**: At least 2 examiner-trace reports (one `PASS`, one `FAIL`/`FLAG`) are produced against
  real loan data, each independently walkable start-to-finish by a reader without needing to read
  `qc_engine` source code.
- **SC-004**: Zero real PII values (borrower name, address, SSN fragment) appear in any file committed
  to this repository as a result of this feature's work — verified by an explicit scan/grep gate run
  against the feature's own commits, not merely asserted by description.
- **SC-005**: If expert-adjudicated labels exist for >=1 check on >=1 real loan by ship time, the G3
  bake-off re-run reports real D1/D2 axes for that labeled subset; if no label exists yet, the report
  states `BLOCKED` explicitly rather than omitting the section.
- **SC-006**: A real, full-extraction-scale payload's token count and cost-at-10k-loans figure is
  measured and reported for at least one real loan — replacing the "$700-$3,500/10k-run, reasoned but
  not computed" gap (this session's own memory finding, itself grounded in `p0/experiment_g3/
  RESULTS.md`'s 1.1K-token synthetic-payload D3 measurement) with an actual number.
- **SC-007**: Full existing test suite (`p0/tests`, `p0/eval_synth/test_properties.py`) and
  `p0/harness.py`'s bit-exact determinism digest pass with zero regression after this feature ships.

## Assumptions

- The 3 real loans confirmed in this spec's Foundation section (`301224293`, `301224442`,
  `301224735`, `s3://mortgage-qc-extraction/results/`, profile `gordon-chan`) are the sample this
  feature ingests. This supersedes the roadmap's implicit framing that real loans are not yet in hand
  — they are; what remains external is the expert-adjudicated label, not the file.
- Expert-adjudicated verdict labels are the genuine, still-open G1 dependency. This feature is designed
  to ship real, independently-useful value (the adapter, the audit-trace proof, the cost measurement)
  even at zero labels — the accuracy/false-auto-clear comparison (US3/FR-009) is the one piece
  genuinely gated on Kayla's/the SME's timeline, named honestly rather than silently blocking the whole
  feature on it.
- `011-label-confirmation-flywheel` (specced concurrently this session) is assumed to own the
  *growing, ongoing* labeled corpus over time; this feature is a consumer/validator against that corpus
  at a point in time, not a duplicate store (User Story 4). If `011`'s eventual spec defines a
  materially different corpus-entry shape than this feature assumes, that is a real integration
  finding to reconcile before implementation, not something to silently paper over.
- This repository has no pre-existing PII-handling discipline for real loan data (unlike
  `demo-sites/dynamic-mortgage-qc`'s own synthetic-standin precedent for the same class of risk) —
  this feature is the first to establish one here (FR-012), not inherit an existing pattern.
- The real loans' own document sets (18-24 `consolidated/{doctype}.json` types per loan) do not
  necessarily align 1:1 with the 5 synthetic loans' document set the 379-entry `field_catalog.json` was
  built against — some mapping-gap volume (FR-004) is expected and is itself a useful finding about
  catalog completeness, not treated as a defect in this feature.
- Building the extraction pattern for the real loans' own pre-existing third-party QC documents
  (FR-006) is scoped as "provide the extraction capability," not "perform the SME reconciliation
  against this project's AMQ check IDs" — the latter remains G1, genuine human judgment.

## Risks

- **HIGH — PII leak into git history.** The real loan bundles carry real borrower names, SSN
  fragments, and property addresses (confirmed directly in this spec's Foundation section). Any
  artifact this feature writes that touches a real per-field value (an adapted-loan dump, an
  eval-report JSON, a printed mismatch message, an examiner-trace report) is a potential leak the
  moment it lands in a git-tracked path. **Mitigation:** FR-012 makes redaction/exclusion a hard
  requirement, not an implementation detail; SC-004 makes it independently verified, not merely
  asserted.
- **HIGH — the real bundles' field-mapping shape may diverge substantially from `field_catalog.json`.**
  The catalog's 379 entries were built against 5 *synthetic* loans' document set; the 3 real loans'
  document sets are real, larger (213-348 total documents each), and may classify differently.
  **Mitigation:** FR-004's mapping-gap reporting turns an unknown-sized gap into a named, measured one
  rather than a silent drop; this feature does not block on closing every gap, only on reporting them
  honestly.
- **MEDIUM — `011` is specced concurrently, not yet built.** This feature's User Story 4 / corpus-shape
  assumption could shift once `011`'s own spec/plan lands. **Mitigation:** named explicitly as an
  Assumption with an explicit reconciliation trigger, rather than silently building toward a shape that
  might not match.
- **MEDIUM — the G3 real-loan re-run (US3) may ship with zero labels and thus report `BLOCKED`
  indefinitely**, since expert adjudication timing is outside this feature's control. **Mitigation:**
  FR-010/FR-011 make the cost/token measurement ship independently of labels, so this feature still
  delivers a real, load-bearing number (the corrected D3 cost figure) even if the accuracy half stays
  blocked for a while.
