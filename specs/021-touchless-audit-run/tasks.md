# Tasks: 021-touchless-audit-run

**Input**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/audit-run.md`,
`quickstart.md` (same directory)
**Prerequisites**: plan.md (required); `019`/`020` already merged into this worktree (done, prior
session commits)

**Tests**: Included per `plan.md`'s Testing section (`pytest` for Python, `vitest` for
backend/frontend) — this project's own constitution requires labeled-case coverage for any new
check-adjacent logic (Eval gate), so test tasks are not optional here.

## Phase 1: Setup

- [X] T001 Port `demo/touchless/{original,extracted}` from
      `/Users/gordonchan/Workspace/demo-sites/mortgage-qc-prod/demo/touchless/` into this
      worktree's `demo/touchless/` (research.md Item 4) — source data only, no code
- [X] T002 Confirm `p0/tests/` suite, `backend/` vitest suite, and `frontend/` vitest suite are all
      currently green before adding anything (re-baseline; these were last verified in the prior
      `656d440` port commit, confirm nothing drifted) — p0: 318 passed, 3 skipped, 26 pre-existing
      failures unrelated to this feature (other specs' TDD scaffolding: `eval_real`,
      `promotion_gate`, `scenario_construction` modules don't exist yet — confirmed via
      `git log` these predate this worktree's spec021 work); backend: 42/42; frontend: 21/21

## Phase 2: Foundational (blocking — required by User Story 1 and User Story 5)

**Purpose**: The compiled ruleset, adapter, loan-status derivation, and the backend route that ties
them together. Nothing in Phase 3+ can be verified end-to-end until this phase is done.

- [X] T003 [P] Add `document_ids: Optional[List[str]] = None` to `DocCitation` in
      `p0/qc_engine/model.py` (additive field; `to_dict()` emits `documentIds` only when populated,
      matching the existing `document_title`/`section`/`field_label` convention) — data-model.md's
      "`DocCitation` (revised)" section
- [X] T004 [P] Write `p0/tests/test_model_doc_citation_document_ids.py`: confirm existing
      `DocCitation` construction/`to_dict()` call sites (e.g. `golden.py`'s hand-authored
      citations) are byte-identical when `document_ids` is left unset — the additive-field
      backward-compatibility guarantee this change depends on
- [X] T005 Create `p0/qc_engine/touchless_document_map.py`: the confidently-resolvable
      canonical-field → Touchless-`documentType` lookup table (research.md Item 2 / data-model.md's
      "Document-Type Mapping Table") — `bank_statement`, `paystub`, `W2`, `gift_letter`,
      `schedule_k1`, `tax_return`→`"Form 1040"`, `sales_contract`→`"Purchase Agreement"`,
      `URLA_1003_final`→ the 4 real `URLA - *` document types (list-valued)
- [X] T006 Create `p0/qc_engine/compiler/build_p0_ruleset_from_gold.py`: reads
      `storage/rules/gold/data/{rules_compiled.json,rules_atomic.json}` (same source
      `frontend/scripts/build_gold_catalog.py` reads), filters gold's `COMPILABLE` checks to only
      those whose `fieldId` appears in T005's mapping table, emits a `p0/qc_engine/ruleset.py`
      `Ruleset` (data-model.md's "Compiled Audit Ruleset") — depends on T005. Returns
      `(ruleset, total_compilable_count)`; `total_compilable_count` mirrors
      `build_gold_catalog.py`'s exact NEEDS_FIELDS-eligible check-type set, verified == 208
      (the authoring UI's own COMPILABLE count)
- [X] T007 [P] Write `p0/tests/test_build_p0_ruleset_from_gold.py`: assert the compiled `Ruleset`'s
      check count matches the T005 mapping table's coverage exactly (no check outside the mapped
      set slips in), and spot-check 2-3 real checks' `severity`/`field_name` mapping correctness —
      37 checks compiled, 208 total_compilable (9/9 passed)
- [X] T008 Create `p0/qc_engine/touchless_to_canonical_loan.py`: converts a pulled
      `loan_application.json` payload into a `CanonicalLoan` — for each T005 mapping-table entry,
      sets `truth=True` if a matching `documentType` exists in `documents[]` (else leaves the field
      unset), and populates the matched document(s)' real `documentId`(s) into
      `DocCitation.document_ids` (T003) for each such field; `doc_confidence` is never set (per
      Gordon's explicit instruction — confidence scoring is out of scope) — depends on T003, T005
- [X] T009 [P] Write `p0/tests/test_touchless_to_canonical_loan.py`: using the real ported
      `demo/touchless/extracted/loan_application.json` (T001), assert the adapter correctly
      resolves presence for at least one known-present field (e.g. `bank_statement`) and
      known-absent field (once T005's map is extended per `022`'s research — for `021` alone,
      assert absence is `None`/unresolved, not silently `True`), and that `document_ids` is
      populated with the real `documentId`(s) for present fields — 6/6 passed, all 8 confidently-
      resolvable fields confirmed present in the real demo loan
- [X] T010 [P] Create `p0/qc_engine/loan_status.py`: the severity-tiered status derivation
      (research.md Item 1) — `PASS` (zero `qc_failures`) / `FAILED` (any CRITICAL-severity
      `qc_failures`) / `NEEDS_REVIEW` (non-empty `qc_failures`/`needs_review`, no CRITICAL present),
      operating on an existing `RunResult` — no dependency on T005-T009
- [X] T011 [P] Write `p0/tests/test_loan_status.py`: one labeled case per outcome (`PASS`,
      `FAILED`, `NEEDS_REVIEW`), constructed via hand-built `RunResult`/`CheckResult` fixtures (per
      this project's Eval gate — labeled cases, not just an empty-input smoke test) — 4/4 passed
- [X] T012 Create `p0/qc_engine/run_touchless_audit_for_demo.py`: single entry-point — takes a
      loan-application JSON path (or stdin) as input, runs T006's compiler, T008's adapter, then
      `engine.run()`, then T010's status derivation, and prints one JSON object
      (`{loanStatus, compiledCheckCount, excludedCheckCount, runResult}`, per contracts/audit-run.md)
      to stdout — depends on T006, T008, T010. Verified against the real demo loan: `PASS`,
      37 compiled, 171 excluded, byte-identical across repeated runs (determinism confirmed);
      stdin path also verified
- [X] T013 Create `backend/src/routes/audit.ts`: `POST /api/audit/:applicationId/run` (validates
      `applicationId` via `020`'s existing `isValidUuid()`, looks up the already-pulled application
      payload, invokes T012 via `child_process.execFile`, parses stdout, returns the response shape
      from contracts/audit-run.md; maps subprocess failure/timeout/malformed-stdout to
      `ErrorCode.PROXY_ERROR` reusing `020`'s existing `ErrorEnvelope`) — depends on T012.
      Required a small new addition beyond the original task text: `020`'s pull route never
      cached the pulled payload anywhere, so a new `backend/src/applicationStore.ts` (in-memory
      Map, session-lifetime) was added and wired into `applications.ts`'s pull route so this
      route has something real to read from (contract's "already pulled this session" NOT_FOUND
      case depends on this existing)
- [X] T014 [P] Write `backend/src/__tests__/audit.route.test.ts`: mock the subprocess call, assert
      the 200 success shape, the `NOT_FOUND` case (unpulled `applicationId`), the `PROXY_ERROR` case
      (subprocess failure), and the `INVALID_INPUT` case (malformed UUID) per contracts/audit-run.md
      — 6/6 passed (also covers unparseable stdout and unexpected-shape stdout)
- [X] T015 Mount the new `auditRouter` in `backend/src/server.ts` alongside `applicationsRouter`/
      `documentsRouter` — depends on T013

**Checkpoint**: `python3 p0/qc_engine/run_touchless_audit_for_demo.py` runs standalone against the
ported demo loan and prints a real, non-empty verdict; `POST /api/audit/:applicationId/run`
returns that same verdict over HTTP. This is the foundation every user story below builds on.

## Phase 3: User Story 1 - A demo operator fetches a loan and sees a real, computed verdict (Priority: P1) 🎯 MVP

**Goal**: Click "Pull Application" → loan fetches → audit runs automatically → status flips
`RUNNING` → a genuine `PASS`/`FAILED`/`NEEDS_REVIEW`, traceable to the real engine (spec.md
Acceptance Scenarios 1-8).

**Independent Test**: Per spec.md — trigger the pull for `applicationId =
0eb57730-6d2e-4a6d-8db3-bc1217c77b90`, confirm the resulting status traces to a real engine run
(matches T012's standalone CLI output exactly, SC-002).

- [X] T016 [P] [US1] Revise `LoanStatus` in `frontend/src/lib/types.ts`: persisted union becomes
      `"PASS" | "FAILED" | "NEEDS_REVIEW" | "RESOLVED" | "ERROR"`; model `RUNNING` as a separate,
      non-persisted display-state type (data-model.md's `LoanDisplayState`), not a `LoanStatus`
      member — added a 4th kind beyond data-model.md's original 3 (`not_fetched`), for the
      never-fetched-this-session demo loan: since the persisted union has no "not yet run" value,
      showing any of PASS/FAILED/NEEDS_REVIEW before a real run would be fabrication (violates
      FR-003/"never a guess"); `not_fetched` is the honest default until a real pull+run happens
- [X] T017 [P] [US1] Expand `frontend/src/data/mockData.ts`'s `MOCK_LOANS` to 20 total: remap the 4
      existing non-demo loans' status to `"PASS"`, add 15 more cosmetic loans (realistic
      borrower/property/loan-type text, `status: "PASS"`, no `applicationId`) — the existing real
      demo loan (`applicationId` present) is unchanged
- [X] T018 [US1] Extend `frontend/src/lib/dataSourceContext.tsx`: add audit-run state (per
      `applicationId`: `idle | running | { status: LoanStatus } | { error: string }`), a
      `runAudit(applicationId)` action calling `POST /api/audit/:applicationId/run` (T013), and
      auto-invoke `runAudit` immediately when a pull-application fetch resolves successfully (no
      separate user action, per FR-003) — depends on T013, T016. Also added `deriveLoanDisplayState()`
      / `useLoanDisplayState()` as the single source of truth for what a loan's badge shows; new
      `frontend/src/lib/auditApi.ts` fetch wrapper (mirrors `touchlessApi.ts`'s own pattern)
- [X] T019 [US1] Update `frontend/src/components/LoanDetail.tsx`: render the transient `RUNNING`
      state while `runAudit` is in flight, then the resolved `PASS`/`FAILED`/`NEEDS_REVIEW` badge
      once it completes, sourced only from `dataSourceContext`'s state (never a locally-set value)
      — depends on T018. `LoanStatusBadge` (StatusBadge.tsx) now takes a `LoanDisplayState`, not a
      bare `LoanStatus`, so it can render running/not_fetched/error too
- [X] T020 [US1] Update `frontend/src/components/LoanQueue.tsx`: render the new 20-loan set (T017);
      never render an `ERROR`-status/state loan with a badge in the grid (FR-006a) — surfacing that
      state is out of scope for the grid entirely, per spec.md Acceptance Scenario 8 — extracted a
      `LoanQueueRow` subcomponent (a hook can't be called per-iteration inside `.map()`); clamps
      `error` down to the same neutral look as `not_fetched` in the grid specifically
- [X] T021 [US1] Verify end-to-end (quickstart.md steps 1-5): fetch the real demo loan, confirm
      `RUNNING` then a real resolved status; compare against T012's standalone CLI output for exact
      match (SC-002) — verified via real backend (`npm run dev`) + real Touchless credentials:
      `POST /api/touchless/applications/.../pull` (62 real documents) then
      `POST /api/audit/.../run` both succeeded live; HTTP response `loanStatus`/counts/
      `ruleset_sha256`/full `results[]` are byte-identical to the standalone CLI run (SC-002
      confirmed); also fixed 2 pre-existing spec020 tests (`dataSourceContext.test.tsx`) whose
      `mockResolvedValue` reused one `Response` instance across calls -- broke once a pull started
      triggering a second (audit) fetch, since a `Response` body can only be read once; switched to
      `mockImplementation` for a fresh `Response` per call. tsc/build/vitest (21/21) all clean

**Checkpoint**: User Story 1 fully functional and independently demoable/testable.

## Phase 4: User Story 5 - A flagged exception's citation opens the real source document (Priority: P1)

**Goal**: Every exception from User Story 1's real run has a citation that opens the actual
Touchless document — not a placeholder (spec.md Acceptance Scenarios 1-3).

**Depends on**: User Story 1 (Phase 3) — there must be a real exception to click before this can be
demonstrated; not parallelizable with Phase 3 for that reason, despite the same priority (P1).

**Independent Test**: Per spec.md — with the demo loan evaluated and at least one exception raised,
click its citation and confirm a real document opens.

- [X] T022 [US5] Add `documentIds?: string[]` to `Finding["citation"]` in
      `frontend/src/lib/types.ts` (mirrors T003's backend `document_ids`, passed through unmodified
      by `RunResult.to_dict()` per contracts/audit-run.md)
- [X] T023 [US5] Rewire `frontend/src/components/ExceptionReview.tsx`'s citation-click flow: for a
      real (Touchless-sourced) exception, render one clickable link per `citation.documentIds`
      entry (not collapsed to the first match, per spec.md Acceptance Scenario 2), each opening
      `020`'s existing `RetrievedDocumentViewer` (reused, not rebuilt); if `documentIds` is empty,
      state this honestly (no document to open) rather than showing a dead link — replaces the
      existing "PDF page render placeholder" modal for this feature's real exceptions only (mock
      findings elsewhere are unaffected) — depends on T022. Required more than a citation-modal
      rewire: `ExceptionReview.tsx` previously only ever read `MOCK_FINDINGS`, with no wiring to a
      real audit run's `RunResult` at all — added `frontend/src/lib/auditFindings.ts`
      (`findingsFromRunResult()`, mirrors `engine.py`'s own `qc_failures` definition: `phase ===
      "QC" && status in (FAIL, WARNING)`) and wired the component to prefer real findings once
      the loan's real audit run has resolved, falling back to `MOCK_FINDINGS` otherwise
- [X] T024 [US5] Verify (quickstart.md step 6a): click through every exception on the demo loan's
      real verdict; confirm each opens genuine Touchless content, and multi-document checks (e.g.
      `URLA_1003_final`) show all matched documents as separate links (SC-008) — **the real demo
      loan's real audit run currently resolves to PASS with ZERO exceptions** (all 8 confidently-
      resolvable fields are present on this loan, confirmed live against real Touchless
      credentials in Phase 3/T021's verification) — there is nothing to literally click through on
      today's real data. Verified the wiring instead via `ExceptionReview.test.tsx` (7 new tests,
      controlled synthetic "resolved" audit states): single-documentId citation opens the real
      `RetrievedDocumentViewer` (not the placeholder), a 4-document citation renders all 4 as
      separate links and each opens the SPECIFIC clicked document (`getOrFetchDocument` called with
      that exact id, not always the first), an empty-`documentIds` citation shows the honest
      "no source document identified" message, a RECONCILE-phase FLAG never counts as an exception,
      and pre-existing mock-finding placeholder-modal behavior is unaffected. This real-data gap is
      exactly what motivates `022`'s existence — noted, not silently worked around.

**Checkpoint**: User Stories 1 and 5 together deliver the full "real verdict, real evidence" story.

## Phase 5: User Story 2 - One button resets the whole demo, not just the ruleset (Priority: P2)

**Goal**: "Restore to Gold" also clears the fetched loan and its verdict (spec.md Acceptance
Scenarios 1-2).

**Depends on**: User Story 1 (there must be fetched/run state for this to demonstrably clear).

**Independent Test**: Per spec.md — fetch a loan, run it to a verdict, click Restore to Gold,
confirm both the ruleset draft and the fetched loan/verdict are gone.

- [X] T025 [US2] Add a `resetFetchedApplications()` action to `frontend/src/lib/dataSourceContext.tsx`
      clearing all per-`applicationId` fetch/audit-run state — also clears
      `retrievedDocuments`/`documentErrors` (citation-viewed documents), since a genuinely
      fresh page load would have none of those either
- [X] T026 [US2] Wire `frontend/src/components/RoutesFlow.tsx`'s existing `restoreToGold()` (from
      `019`'s Phase 5) to also call T025's new action — depends on T025
- [X] T027 [US2] Verify (quickstart.md step 7): fetch + run the demo loan, click Restore to Gold,
      confirm the app matches a fresh page load exactly (SC-003, same bar as `019`'s own SC-003)
      — verified via 2 new `dataSourceContext.test.tsx` tests: a real pull+run (mocked fetch)
      followed by `resetFetchedApplications()` leaves `pulledApplications`/`auditRuns` empty and
      `applicationError`/`isPullingApplication` back to their fresh-mount values; a separate test
      confirms `retrievedDocuments`/`documentError` are cleared too. tsc/build/vitest (30/30) clean

**Checkpoint**: The demo can be reset and re-run repeatedly without a page reload.

## Phase 6: User Story 3 - Government loans split into their real sub-programs (Priority: P3)

**Goal**: FHA/VA/USDA replace the single Government route, each with a non-zero check count.

**Independent of** every other phase — touches only `019`'s existing gold-catalog generator script
and its output; can be done in parallel with Phases 2-5.

**Independent Test**: Per spec.md — open the Routes screen, confirm FHA/VA/USDA appear as separate
routes with non-zero counts and the same block structure as Conventional.

- [X] T028 [P] [US3] Modify `frontend/scripts/build_gold_catalog.py`: replace the single
      `government`/`gov-*` route/blocks with three routes (`fha`, `va`, `usda`, id-prefixed
      `fha-`/`va-`/`usda-`), each with the same 16 blocks; generate a simulated non-zero check
      count per block, scaled proportionally to Conventional's real per-block count (data-model.md
      "FHA / VA / USDA Routes"), with an explicit, dated code comment marking these as simulated —
      per FR-009, the UI itself shows them identically to real counts, no distinguishing badge —
      `build_simulated_program_blocks()`; count formula `max(3, round(real_count * 0.20))`;
      deliberately does NOT set `placeholder: true` (confirmed that field renders a distinguishing
      `PlaceholderBadge` elsewhere, which would violate FR-009's "no distinguishing badge")
- [X] T029 [US3] Regenerate `frontend/src/data/goldCatalog.json` by rerunning the modified script
      (T028) — depends on T028. 1768 total checks (1105 real conv + 3×~221 simulated); FHA/VA/USDA
      block counts range 3-39, zero zero-count blocks, zero id collisions with real conv checks
- [X] T030 [US3] Verify (quickstart.md step 8): Routes screen shows 4 routes total (Conventional,
      FHA, VA, USDA), each with a non-zero check count (SC-004) — verified in goldCatalog.json
      directly; `tsc -b`/`npm run build`/`npm test -- --run` (21/21) all clean

**Checkpoint**: The Routes screen shows the full 4-route program breakdown.

## Phase 7: User Story 4 - Screens reflect real facts from the Touchless call (Priority: P3)

**Goal**: `InspectSources`/`ImportAndSignView` copy matches concrete, real facts from the Touchless
call, with no unconfirmed claim stated as settled.

**Independent of** every other phase — pure content edits on two existing components; can be done
in parallel with everything else.

**Independent Test**: Per spec.md — open both screens, confirm the copy matches the concrete facts,
zero placeholder language remaining.

- [X] T031 [P] [US4] Update `frontend/src/components/InspectSources.tsx`: replace the generic
      three-source framing with the real Touchless retrieval sequence (application results →
      indexed documents → per-document extracted data), and add an honest note that exact
      in-page/citation location is not yet confirmed available from Touchless's extraction output
      — intro paragraph + 3-card row re-pointed at the real retrieval sequence (kept the same
      icon+label+sub card pattern), added a slate-toned honest-uncertainty note (Info icon) plus a
      short separating paragraph so the still-valid DOC/LOS/MISMO reconciliation table below isn't
      conflated with Touchless's own retrieval steps
- [X] T032 [P] [US4] Update `frontend/src/components/ImportAndSignView.tsx`: replace the example
      document-type list with the real types from the call (W-9, 1040 Schedule C, hazard insurance,
      bank statement, credit report, appraisal, application/URLA, gift letter, employment
      verification) — no prior list existed (confirmed via grep), so added a new
      `EXAMPLE_DOCUMENT_TYPES` const + a labeled pill-list card placed right after the existing AMQ
      workbook import-summary card, matching existing Tailwind/lucide-react patterns already used
      in this file
- [X] T033 [US4] Verify (quickstart.md, spec.md Acceptance Scenarios 1-3): re-read both screens
      against the concrete facts list, confirm zero remaining generic/placeholder language on the
      specific points (SC-005) — confirmed via grep (old three-source phrase gone, all 9 real
      document types present); `npx tsc -b` clean, `npm run build` clean, frontend vitest 21/21
      passed, zero regressions

**Checkpoint**: Both screens are grounded in real, confirmed facts, not generic placeholder text.

## Phase 8: Polish & Cross-Cutting Concerns

- [X] T034 Run the full regression sweep: `p0/tests/` (`python -m pytest tests/ -v`), `backend`
      vitest, `frontend` vitest, `npx tsc -b`, `npm run build` — all green, matching the bar every
      prior phase in this session's work has held to — p0: 341 passed (26 pre-existing, unrelated
      failures); backend: 48/48; frontend: tsc clean, 33/33, build clean
- [X] T035 Force an error path (per quickstart.md's SC-006 verification — e.g. an unreachable
      `TOUCHLESS_BASE_URL` or a killed backend mid-run) and confirm the Loan Queue grid shows zero
      error badges while the loan detail view/fetch-trigger does show the error (SC-006) —
      verified BOTH ways: (1) live against the real backend — temporarily moved
      `run_touchless_audit_for_demo.py` aside mid-session, confirmed the real HTTP response is
      `500 PROXY_ERROR` (restored the file immediately after, re-verified the standalone CLI still
      works); (2) new `LoanQueue.test.tsx` (3 tests) proving the grid renders zero error badges
      (falls back to "Not Yet Evaluated") while `LoanDetail` DOES show "Error" for the identical
      mocked error state. Caught and fixed a real pre-existing bug while writing this test: the
      `useLoanDisplayState()` hook (added in Phase 3) called `useDataSource()` internally, which
      bypasses `vi.spyOn(dataSourceContext, "useDataSource")` (an ES-module same-file call doesn't
      route through the exported binding) — this codebase's own established component-test
      convention depends on that spy working. Removed the hook; `LoanDetail.tsx`/`LoanQueue.tsx`
      now call `useDataSource()` themselves and pass the result to `deriveLoanDisplayState(loan,
      ctx)` directly, matching `RetrievedDocumentViewer.test.tsx`/`ExceptionReview.test.tsx`'s own
      pattern. Full suite re-verified green after the fix (33/33)
- [ ] T036 Run `/speckit-analyze` against `spec.md`/`plan.md`/`tasks.md` and resolve any findings
      before considering this feature done

## Dependencies

```
T001-T002 (Setup)
  └──► T003-T015 (Foundational — blocks US1 and US5)
         └──► T016-T021 (US1, P1 — MVP)
                └──► T022-T024 (US5, P1 — depends on US1's real exceptions)
                └──► T025-T027 (US2, P2 — depends on US1's fetch/run state existing)
T028-T030 (US3, P3) — independent, parallel to everything above
T031-T033 (US4, P3) — independent, parallel to everything above
T034-T036 (Polish) — after all preceding phases
```

Within Phase 2: T003→T004; T005→T006→T007; T005+T003→T008→T009; T010→T011 (parallel to T005-T009);
T006+T008+T010→T012→T013→T014; T013→T015.

## Parallel Execution Examples

**Phase 2 (Foundational)**, after T005 lands:
```
T003 [P], T007 [P] (once T006 exists), T009 [P] (once T008 exists), T010 [P], T011 [P]
```

**Across user-story phases**, once Phase 2 is done:
```
Phase 6 (T028-T030) and Phase 7 (T031-T033) can run entirely in parallel with Phase 3 (T016-T021)
— neither touches the audit-run pipeline or LoanQueue/LoanDetail/dataSourceContext.
```

## Implementation Strategy

**MVP = Phase 1 + Phase 2 + Phase 3 (User Story 1)**. This alone delivers the feature's entire
stated purpose — a real, computed verdict from a real engine run — and is independently demoable.

**Recommended incremental order**: Setup → Foundational → US1 (MVP checkpoint) → US5 (completes the
traceability claim US1 makes) → US2 (repeat-demo convenience) → US3 + US4 (can slot in anytime
after Setup, in parallel with the above, since they're fully independent).
