# Tasks: Real-Loan Distribution Eval

**Input**: Design documents from `specs/012-real-loan-distribution-eval/` (spec.md, plan.md)
**Prerequisites**: `005-eval-harness-as-promotion-gate` (the scorer/tiers this feature feeds real loans
into), `007-audit-trail-and-citation-of-record` (implemented — the chain this feature proves against
real data), `011-label-confirmation-flywheel` (specced concurrently — the corpus-shape this feature
assumes; reconcile before T020 if `011`'s spec lands with a different shape).

**Tests**: Included per this project's established TDD/zero-regression convention (`000`/`003a`/`003b`/
`003c`/`004`/`005`'s own tasks.md files) — write failing tests first, confirm red, then implement.

**Organization**: Grouped by user story (US1-US4, per spec.md), matching this project's own
`tasks-template.md` convention.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Maps to spec.md's User Story 1-4

---

## Phase 1: Setup (Shared Infrastructure)

- [ ] T001 Create `p0/eval_real/` package (`__init__.py`) as a sibling to `p0/eval_synth/`, per
  plan.md's Project Structure.
  → Done when: `python3 -c "import eval_real"` succeeds from `p0/`.
- [ ] T002 [P] Add `p0/eval_real/local_cache/` to `.gitignore`, with a comment matching the existing
  `demo/` PII-risk convention ("real loan bundles + derived artifacts that may carry PII — kept on
  disk not in git").
  → Done when: `git check-ignore p0/eval_real/local_cache/anything.json` reports ignored.
- [ ] T003 [P] Add `p0/eval_real/s3_client.py` — a thin `boto3` wrapper reusing
  `p0/experiment_g3/llm_arm.py`'s existing `PROFILE='gordon-chan'` session-setup pattern, read-only,
  scoped to `s3://mortgage-qc-extraction/results/`.
  → Done when: a manual, non-CI script using `s3_client.py` lists the 3 real loan prefixes
  (`301224293/`, `301224442/`, `301224735/`) without hardcoding credentials.

**Checkpoint**: Package skeleton + PII-safe storage boundary exist before any real data is touched.

---

## Phase 2: Foundational (Blocking Prerequisites)

**⚠️ CRITICAL**: No user story work may begin until this phase is complete — it establishes the PII
boundary every subsequent task must respect.

- [ ] T004 Write `p0/eval_real/pii_scan.py` — a scan gate over a given set of paths, matching known
  real-loan PII patterns (the specific borrower names / `ssn_last4` values / property address strings
  confirmed present in the 3 real loans' bundles, loaded from a local-only, gitignored reference file —
  never hardcoded into a git-tracked module).
  → Done when: T005 (its test) exists and passes.
- [ ] T005 [P] Write `p0/tests/test_pii_scan_gate.py` — plant a known PII-shaped string in a temp
  fixture file, confirm `pii_scan.py` detects it; confirm a clean fixture passes.
  → Done when: both assertions pass; run this test FIRST (before T004 is complete) to confirm it fails
  red, per this project's TDD convention.
- [ ] T006 Wire `pii_scan.py` as a pre-commit-style manual gate documented in this feature's own
  quickstart note (a script, not a git hook this feature installs unrequested) — run before any commit
  that touches `p0/eval_real/` output paths.
  → Done when: running the gate against a deliberately-planted-PII test commit fails loudly; against a
  clean one, passes.

**Checkpoint**: The PII boundary (FR-012) is provably real before any adapter output exists to test it
against.

---

## Phase 3: User Story 1 - Real loan scores through the existing harness with zero scorer rework (Priority: P1) 🎯 MVP

**Goal**: A real, already-acquired loan converts into a `CanonicalLoan` + `LabeledLoan` tuple and
scores through `p0/eval_synth/test_properties.score()` unmodified (beyond the one disclosed FR-003
hardening).

**Independent Test**: Convert one real loan via the adapter; confirm the resulting tuple scores through
`score()` with no crash and a well-formed report.

### Tests for User Story 1

- [ ] T007 [P] [US1] Write `p0/tests/test_real_loan_adapter.py` — a hand-authored SYNTHETIC stand-in
  bundle mirroring the real S3 shape (`{loan}-ulad.json`, `{loan}-citations.json`,
  `consolidated/*.json`, no live AWS creds needed for CI): asserts the adapter produces a valid
  `CanonicalLoan`, asserts the output tuple matches `LabeledLoan`'s exact shape (FR-002), asserts a
  deliberately-unmapped field name surfaces in `MappingGapReport` (FR-004) rather than being dropped.
  → Done when: written and confirmed RED (adapter doesn't exist yet).
- [ ] T008 [P] [US1] Add a regression test asserting `test_properties.score()` does not raise
  `KeyError` on a tuple whose `prov` dict is exactly `{"mutations": [], "source": "expert-labeled",
  "loan_id": "..."}` (FR-002/003) — write against current (unpatched) `score()` first to confirm it
  currently DOES raise on a mismatching case, proving the gap is real before patching it.
  → Done when: confirmed red against unpatched `score()`, confirmed the exact failure mode (KeyError
  on `prov['mutations']`) matches spec.md's Foundation section finding.

### Implementation for User Story 1

- [ ] T009 [US1] Implement `p0/eval_real/adapter.py`'s `RealLoanAdapter` — reads a bundle (local path
  or `s3_client.py`-fetched), maps ULAD-shaped fields (`borrowers[]`, `property`, `loan_detail`) and
  `{loan}-citations.json`'s discrepancy records onto `CanonicalLoan.fields[name] = SourceValue(truth=...,
  sources={"los": ...}, citation=DocCitation(...), doc_confidence=...)` per `field_catalog.json`'s
  existing canonical names (depends on T007 being red).
  → Done when: T007 passes.
- [ ] T010 [US1] Implement `p0/eval_real/mapping_gaps.py`'s `MappingGapReport` — collects every real
  field name the adapter could not map to a `field_catalog.json` entry (FR-004), as a structured,
  named list (never a silent drop).
  → Done when: T007's mapping-gap assertion passes.
- [ ] T011 [US1] Apply the FR-003 hardening: `p0/eval_synth/test_properties.py`'s mismatch-message
  formatting changes `prov['mutations']` to `prov.get('mutations', [])`, disclosed as the one piece of
  harness rework this feature's own inspection found necessary.
  → Done when: T008 passes; full existing `p0/eval_synth/test_properties.py` suite still passes
  unmodified otherwise (no other behavior change).
- [ ] T012 [US1] Run all 3 real loans (`301224293`, `301224442`, `301224735`, fetched via `s3_client.py`
  into `local_cache/`, never committed) through the adapter; confirm zero crashes (SC-001) and produce
  a local (gitignored) mapping-gap summary per loan.
  → Done when: 3/3 loans produce a valid `CanonicalLoan` and score through `score()` without error;
  results logged to a local, gitignored artifact — never committed raw.
- [ ] T013 [US1] Run `pii_scan.py` (T004) against every git-tracked file this story's implementation
  touches before considering it complete.
  → Done when: scan reports zero PII matches in tracked paths.

**Checkpoint**: US1 fully functional and independently testable — a real loan scores through the
unmodified harness.

---

## Phase 4: User Story 2 - Examiner can trace a real verdict end-to-end (Priority: P1)

**Goal**: `007`'s already-built audit chain and citation trail are proven against real (not synthetic)
citations for the first time.

**Independent Test**: Run the engine against one adapted real loan, append to a real `AuditLog`, call
`verify_chain()`, produce a human-readable trace for one PASS and one FAIL/FLAG verdict.

### Tests for User Story 2

- [ ] T014 [P] [US2] Write `p0/tests/test_real_loan_audit_trace.py` — asserts `verify_chain()` returns
  `True` for an `AuditLog` seeded with a real-adapted loan's `RunResult`; asserts it returns `False`
  after a deliberate tamper simulation (mutate one stored `payload_json` row directly); asserts an
  `ExaminerTraceReport` for at least one PASS and one FAIL/FLAG verdict contains rule id, ruleset
  version + SHA-256, every input `SourceValue`, rounding applied, verdict, and — for doc-sourced values
  — real doc name/page/segment (not a placeholder).
  → Done when: written and confirmed RED (`audit_trace.py` doesn't exist yet).

### Implementation for User Story 2

- [ ] T015 [US2] Implement `p0/eval_real/audit_trace.py` — runs `qc_engine.engine.run` against a US1-
  adapted real loan, appends the `RunResult` to a real `qc_engine.audit.AuditLog` (depends on T009).
  → Done when: T014's `verify_chain()` assertions pass.
- [ ] T016 [US2] Implement the `ExaminerTraceReport` renderer inside `audit_trace.py` — human-readable
  per-verdict trace, sourced from `CheckResult`'s existing intermediates (no new engine fields needed;
  `007`'s existing shape already carries everything FR-008 requires).
  → Done when: T014's report-structure assertions pass for at least one PASS and one FAIL/FLAG verdict
  from a real loan.
- [ ] T017 [US2] Run `pii_scan.py` against any committed examiner-trace report; if a real doc
  name/page/segment snippet contains a PII fragment (e.g. a snippet quoting a borrower's name), redact
  before committing, per FR-012 — never redact the rule id/hash/verdict fields themselves.
  → Done when: any git-tracked example trace report passes the scan gate with the underlying
  audit/citation *mechanism* still fully demonstrated (redaction only touches the PII substring, not
  the report's structural completeness).

**Checkpoint**: US1 + US2 both independently functional — real loans score AND their verdicts are
examiner-traceable.

---

## Phase 5: User Story 3 - G3 bake-off re-runs on real loans; real cost/token measurement (Priority: P2)

**Goal**: Re-run G3's locked methodology against real loans (accuracy half conditional on labels;
cost half unconditional), converting the roadmap's "$700-$3,500/10k-run, reasoned not computed" gap
into a measured number.

**Independent Test**: Measure Arm B's real per-loan token count/cost against a real, full-extraction-
scale payload; if expert labels exist for >=1 check, also report D1/D2 for that labeled subset.

### Tests for User Story 3

- [ ] T018 [P] [US3] Write `p0/tests/test_bakeoff_real.py` — asserts that with zero expert labels
  present, the accuracy/D2 section of the report reads `"status": "BLOCKED"` with a named missing-
  dependency reason (FR-011), never silently omitted; asserts the cost/token (D3) section is populated
  and non-null regardless of label availability.
  → Done when: written and confirmed RED (`bakeoff_real.py` doesn't exist yet).

### Implementation for User Story 3

- [ ] T019 [US3] Implement `p0/eval_real/bakeoff_real.py` — reuses `p0/experiment_g3/llm_arm.py`'s
  Bedrock session pattern and `bakeoff.py`'s locked D1/D2/D3 methodology (`temperature=0`, structured
  JSON, same checks/rules given to both arms) against one US1-adapted real loan's full extraction
  payload; measures real token count, extrapolates cost-at-10k-loans (D3).
  → Done when: T018's D3 assertion passes against at least one real loan.
- [ ] T020 [US3] Add the conditional D1/D2 accuracy path: IF an `ExpertLabelSet` (FR-005's external
  input contract) is available for >=1 check on >=1 real loan, run both arms against that labeled
  subset and report exact-match rate + false-auto-clear count in `RESULTS.md`'s existing table shape;
  ELSE report `"status": "BLOCKED"` naming the missing dependency (FR-011).
  → Done when: T018's BLOCKED-path assertion passes at zero labels; re-run passes the accuracy-reported
  path the moment any labeled fixture is supplied (verified with a test-only synthetic label stand-in,
  since no real label exists at spec-writing time — see spec.md Assumptions).
- [ ] T021 [US3] [P] Implement `p0/eval_real/qc_doc_extraction.py` (FR-006) — label-anchored extraction
  patterns for the real bundles' own already-classified, field-unextracted third-party QC documents
  (Snapdocs Post-Close QC Report, DUAL AUS Audit Report, FraudGuard Variance Summary, Document Package
  Audit Report, Ability-To-Repay Worksheet, per the specific instances named in spec.md's Foundation
  section), mirroring `000`'s `doc_patterns/*.json` label-anchored regex convention — producing a
  structured, per-check-mappable finding set an SME can reconcile against, not reconciling it
  themselves.
  → Done when: at least one real loan's own QC document (e.g. `301224293`'s "Snapdocs Post-Close QC
  Report") yields a non-empty structured finding set where today's `consolidated/qcchecklist.json`
  shows `"fields": {}`.
- [ ] T022 [US3] Run `pii_scan.py` against every git-tracked artifact this story produces (bake-off
  report, extracted QC-document findings) before considering it complete.
  → Done when: scan reports zero PII matches in tracked paths.

**Checkpoint**: US1 + US2 + US3 independently functional — real-loan scoring, audit-trace proof, and
the (partially label-gated) bake-off re-run + unconditional cost measurement all work.

---

## Phase 6: User Story 4 - Shared corpus with 011, not a parallel store (Priority: P3)

**Goal**: This feature's adapter output is structurally identical to `011`'s corpus-entry shape —
integration-boundary correctness, not new capability.

**Independent Test**: Compare this feature's `RealLoanCorpusEntry` shape against `011`'s own
corpus-entry definition once `011`'s spec/plan lands.

- [ ] T023 [US4] Once `011-label-confirmation-flywheel`'s spec.md/plan.md land, diff its corpus-entry
  shape against this feature's `RealLoanCorpusEntry` (spec.md Key Entities); reconcile any mismatch
  before implementation proceeds further, per spec.md's Assumptions/Risks (MEDIUM risk item).
  → Done when: either confirmed identical (no translation layer needed) or a named, resolved
  reconciliation is documented in this file's own follow-up note.
- [ ] T024 [P] [US4] Document the shared shape's contract (loan identity, expected-verdict dict shape,
  `"source": "expert-labeled"` provenance convention) in a short comment block at the top of
  `p0/eval_real/adapter.py`, cross-referencing `011`'s module once it exists.
  → Done when: comment present and accurate against `011`'s actual shipped shape (not its spec-time
  intent, once implementation exists).

**Checkpoint**: All 4 user stories independently functional; no duplicate labeled-loan store exists.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T025 [P] Run the full existing suite (`pytest p0/tests -v`, `p0/eval_synth/test_properties.py`,
  `p0/harness.py`'s 1000-run bit-exact digest) and confirm zero regression (SC-007).
- [ ] T026 [P] Run `pii_scan.py` (T004) one final time against the complete set of files this feature
  added/modified across all phases, as the SC-004 closing gate — not just per-story spot checks.
- [ ] T027 Write a short quickstart note (in this feature's own `specs/012-real-loan-distribution-eval/`
  directory or a `p0/eval_real/README.md`, matching `p0/eval_synth/README.md`'s existing convention)
  documenting: how to fetch real loans locally (`s3_client.py`, profile `gordon-chan`), how to run the
  adapter/audit-trace/bake-off scripts manually, and the PII-handling rule (FR-012) in plain language
  for the next person who touches this package.
- [ ] T028 Update `output/ROADMAP.md` §012's own entry with an "IMPLEMENTED"-style annotation (matching
  `001a`/`006`/`007`'s own precedent) once all phases are green, naming what shipped vs. what remains
  genuinely blocked on G1 (expert labels).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — package skeleton + gitignore entry.
- **Foundational (Phase 2)**: Depends on Setup. **BLOCKS all user stories** — the PII scan gate must
  exist and be proven (T004/T005) before any real data is adapted, traced, or bake-off'd, since every
  subsequent phase produces artifacts the gate must check.
- **User Story 1 (Phase 3)**: Depends on Foundational. No dependency on US2/US3/US4.
- **User Story 2 (Phase 4)**: Depends on Foundational + US1 (needs an adapted `CanonicalLoan` to run
  the engine against and audit-trace).
- **User Story 3 (Phase 5)**: Depends on Foundational + US1 (needs an adapted loan's full extraction
  payload for the cost measurement half; the accuracy half additionally depends on an `ExpertLabelSet`
  existing, external to this feature).
- **User Story 4 (Phase 6)**: Depends on Foundational + US1 (needs `RealLoanCorpusEntry` to exist) +
  `011`'s spec/plan landing (external, sequencing risk named in spec.md Risks).
- **Polish (Phase 7)**: Depends on all desired user stories being complete.

### Within Each User Story

- Tests written and confirmed RED before implementation (T007/T008 before T009-T012; T014 before
  T015-T017; T018 before T019-T022).
- `pii_scan.py` run at the end of every story that produces a committable artifact (T013, T017, T022)
  — not deferred to a single end-of-feature pass alone.

### Parallel Opportunities

- T002/T003 (Setup) can run in parallel.
- T007/T008 (US1 tests) can run in parallel.
- T014 (US2), once Foundational is done, can be drafted in parallel with US1 implementation tasks that
  don't touch `audit_trace.py`.
- T018 (US3 tests) and T021 (QC-document extraction) can run in parallel with each other.
- T024 (US4 documentation) can run in parallel with Phase 7 polish tasks.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup + Foundational (PII boundary must exist first — this is the one phase ordering this
   feature cannot relax, given FR-012's severity).
2. Complete User Story 1 — a real loan scores through the unmodified harness.
3. **STOP and VALIDATE**: confirm SC-001 and the PII scan gate both hold before proceeding.
4. This alone proves the roadmap's own "no harness rework" design claim for the first time against a
   genuine article — independently valuable even before US2/US3 ship.

### Incremental Delivery

1. Setup + Foundational -> PII boundary ready.
2. US1 -> real-loan ingestion proven (MVP).
3. US2 -> audit-trace proof added (the mock-audit exit criterion).
4. US3 -> bake-off re-run + real cost measurement added (may partially degrade to cost-only if G1
   labels aren't ready yet — named explicitly, not a blocking failure).
5. US4 -> corpus-shape reconciliation with `011` (may be revisited once `011` ships, independent of
   this feature's own release).
