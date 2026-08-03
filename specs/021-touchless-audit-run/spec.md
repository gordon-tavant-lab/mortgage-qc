# Feature Specification: Real-Engine Audit Run (Touchless Fetch → Auto-Run → Pass/Failed)

**Feature Branch**: `021-touchless-audit-run`
**Created**: 2026-08-01
**Status**: Draft
**Input**: User description: "Real-engine audit run for the demo: given a loan already pulled from
Touchless (spec020), automatically compile the gold ruleset into a p0/qc_engine (Pipeline B)
ruleset, adapt the pulled Touchless loan into a CanonicalLoan, run the real deterministic engine
against it, and surface a genuine RUNNING -> PASS/FAILED verdict in the UI (never fabricated).
Also: trim LoanStatus to PASS/FAILED/RESOLVED (plus a transient RUNNING state), split the
Government route into FHA/VA/USDA sub-routes with simulated-but-realistic check counts (reversing
spec019's earlier no-sub-split decision), make the existing 'Restore to Gold' button also clear
any fetched Touchless loan/audit result so the whole demo resets in one click, and update a few
frontend screens (InspectSources, ImportAndSignView) to reflect real facts from a Touchless team
call." Grounded in a transcribed call with Touchless's Shanu (2026-08-01) about their document
extraction API, and in this session's earlier gold-ruleset rework of `019-workbook-first-rule-
authoring`.

**Depends on**: `019-workbook-first-rule-authoring` (the gold-sourced `Check[]` catalog and
`goldCatalog.json` this spec's ruleset compiler consumes), `020-touchless-api-integration` (the
backend proxy and pull-application flow this spec's audit trigger chains off of).

## Clarifications

### Session 2026-08-02

- Q: FR-006's original vocabulary (`PASS`/`FAILED`/`RESOLVED`) has no slot for a loan whose
  evaluation surfaces only non-critical-severity rule failures, or for the manual-review step
  implied by "RESOLVED." What should the outcome model be? → A: `FAILED` is reserved for loans
  with at least one **CRITICAL**-severity rule failure. Loans whose only failures are
  **WARNING**/**INFO**-severity get a new **`NEEDS_REVIEW`** status instead of `FAILED`. `RESOLVED`
  is reached only after a human manually reviews a `NEEDS_REVIEW` loan and clears those flagged
  rules (reusing the existing per-finding mitigation flow in `ExceptionReview` — a finding moving
  off `UNRESOLVED` to `OVERRIDDEN`/`ESCALATED`/`SYSTEM_CORRECTED`) — it is never an automatic engine
  outcome.
- Q: Neither `FAILED`/`NEEDS_REVIEW`/`RESOLVED` covers a run that never produced a real verdict
  (insufficient extracted data, or the engine itself errors) — should this get its own status or
  fold into an existing one? → A: Add a fifth persisted status, `ERROR`, distinct from all four
  outcome states. Scoped for this demo: an `ERROR`-status loan MUST NOT be shown in the Loan Queue
  list view at all (no red/broken tile in front of an audience) — it surfaces only in the loan
  detail view or an inline message at the point of the fetch trigger, never as a queue-grid status
  badge.
- Q: The old status vocabulary (`PENDING`/`AUTO_CLEARED`/`EXCEPTION`) no longer exists on the 4
  other mock loans in the queue, which never go through the new fetch/evaluate flow — what should
  they show, and is the current 5-loan queue sufficient for the demo? → A: Remap all non-demo mock
  loans' status to `PASS`. Separately, expand the Loan Queue to a total of **20** synthetic loans —
  cosmetic content only (realistic borrower/property/loan-type data), none of them wired to a real
  Touchless `applicationId` or requiring real evaluation capability. Only the one existing demo
  loan goes through the actual fetch→run→verdict lifecycle described in User Story 1.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A demo operator fetches a loan and sees a real, computed verdict (Priority: P1)

A demo operator (Gordon, or someone running the demo on his behalf) clicks the existing "Pull
Application" control on a loan already wired to a known Touchless `applicationId`. Once the pull
resolves, the loan's status automatically shows it is being evaluated, then flips to a genuine
pass or fail — computed by actually running the loan through the deterministic rules engine, not
displayed from a canned or hand-picked value.

**Why this priority**: This is the entire point of the feature. Every other story is either
supporting infrastructure for this one or independent polish around it.

**Independent Test**: Trigger the pull for the known demo loan (`applicationId =
0eb57730-6d2e-4a6d-8db3-bc1217c77b90`), and confirm the resulting pass/fail traces to a real
engine run against that loan's actual data — verifiable by comparing the displayed verdict against
a manually-run audit of the same loan through the same ruleset, offline.

**Acceptance Scenarios**:

1. **Given** a loan with a known `applicationId` and no prior fetch this session, **When** the
   operator triggers the fetch, **Then** the loan is retrieved from Touchless (per `020`'s existing
   flow) and, without any further click, the system immediately begins evaluating it.
2. **Given** an evaluation is in progress, **When** the operator views the loan, **Then** its
   status reads as actively running, not as an already-resolved pass/fail/pending state.
3. **Given** an evaluation completes with zero rule failures of any severity, **When** the operator
   views the loan, **Then** its status reads as passed.
4. **Given** an evaluation completes with at least one CRITICAL-severity rule failure, **When** the
   operator views the loan, **Then** its status reads as failed, and the specific failing checks
   are inspectable (reusing the existing Exceptions view).
5. **Given** an evaluation completes with one or more rule failures, none of them CRITICAL
   severity (i.e., only WARNING or INFO), **When** the operator views the loan, **Then** its status
   reads as needing review — distinct from failed — and the flagged checks are inspectable the same
   way.
6. **Given** a loan in needs-review status, **When** a human reviewer resolves every flagged
   finding (via the existing per-finding mitigation flow), **Then** the loan's status updates to
   resolved.
7. **Given** the evaluation cannot complete (the loan's data doesn't resolve enough fields to run
   any checks, or the engine errors), **When** the operator views the loan detail page or the point
   where they triggered the fetch, **Then** this is shown honestly as an error state — never
   silently defaulted to pass, failed, or needs-review.
8. **Given** a loan in error status, **When** the operator views the Loan Queue list, **Then** that
   loan does not appear there with an error badge — the error is visible only in the loan detail
   view or an inline message at the fetch trigger, not in the queue grid.

---

### User Story 2 - One button resets the whole demo, not just the ruleset (Priority: P2)

An operator who has fetched a loan and run an audit wants to reset the entire demo back to its
starting state before a new run-through — without manually clearing multiple things.

**Why this priority**: Directly enables repeated live demos in front of an audience without a
page-reload workaround. Not on the User Story 1 critical path, but needed the first time anyone
demos this twice in a row.

**Independent Test**: Fetch a loan, let it run to a verdict, click the existing "Restore to Gold"
control, and confirm both the authored-ruleset draft (already reset by this control today) and the
fetched loan/verdict are gone — the app looks exactly as it did on a fresh load.

**Acceptance Scenarios**:

1. **Given** a fetched loan with a completed verdict, **When** the operator clicks Restore to
   Gold, **Then** the loan reverts to its un-fetched state and the verdict disappears.
2. **Given** the ruleset draft was also edited this session, **When** Restore to Gold is clicked,
   **Then** both resets happen together, not just one.

---

### User Story 3 - Government loans split into their real sub-programs (Priority: P3)

Someone reviewing the Routes screen sees Government loans broken into FHA, VA, and USDA — the
actual sub-programs — each showing its own check coverage, rather than a single undifferentiated
"Government" bucket.

**Why this priority**: Improves the honesty and specificity of the demo's coverage story, but
doesn't block the core fetch-and-run flow (User Story 1) or the reset flow (User Story 2).

**Independent Test**: Open the Routes screen and confirm three distinct routes (FHA, VA, USDA)
exist in place of the single prior "Government" route, each with a non-zero check count and its
own set of blocks.

**Acceptance Scenarios**:

1. **Given** the Routes list, **When** the operator views it, **Then** FHA, VA, and USDA appear as
   separate routes (not a single "Government" entry), alongside the existing Conventional route.
2. **Given** any of the three new routes, **When** opened, **Then** it shows the same ~16 block
   structure as Conventional, with a check count displayed identically to how Conventional's real
   count is displayed.

---

### User Story 4 - Screens reflect real facts from the Touchless call (Priority: P3)

Someone reviewing the source-inspection and document-import screens sees language and examples
grounded in what Touchless actually confirmed on the call — the real API sequence, real document
type examples, and an honest note about what isn't confirmed yet — rather than generic placeholder
text.

**Why this priority**: Correctness/credibility polish for anyone who reads these screens closely;
doesn't gate the fetch-and-run flow.

**Independent Test**: Open the source-inspection screen and the import screen and confirm the
copy matches the concrete facts below, with no unconfirmed claim stated as settled.

**Acceptance Scenarios**:

1. **Given** the source-inspection screen, **When** viewed, **Then** it describes the real
   Touchless retrieval sequence (get an application's results, then its indexed documents, then
   each document's extracted data) rather than a generic three-source description.
2. **Given** the same screen, **When** it addresses whether a value's exact location on the page
   is traceable, **Then** it states plainly that this is not yet confirmed available from
   Touchless's extraction output — not silently assumed solved.
3. **Given** the import/example-documents screen, **When** viewed, **Then** its example document
   types are drawn from the real list discussed on the call (W-9, 1040 Schedule C, hazard
   insurance, bank statement, credit report, appraisal, application/URLA, gift letter, employment
   verification) rather than a placeholder list.

---

### User Story 5 - A flagged exception's citation opens the real source document (Priority: P1)

A reviewer looking at an exception raised by the real engine run (User Story 1) clicks its
citation and sees the actual Touchless document that check was evaluated against — not a
placeholder or a text-only label — reusing the real document viewer this app already has (from
`020`) for citations elsewhere.

**Why this priority**: Without this, a "real, computed verdict" (User Story 1) still can't be
traced back to real evidence — the exact traceability claim this product's core pitch depends on
("if they don't understand how you calculated that number, you buy back the loan"). This is not
optional polish; it completes User Story 1's own claim.

**Independent Test**: With the demo loan evaluated and at least one exception raised, click that
exception's citation and confirm a real PDF (or the real document viewer already built for `020`'s
citation flow) opens — not a "PDF page render placeholder" text label.

**Acceptance Scenarios**:

1. **Given** an exception whose underlying check resolved against exactly one real document,
   **When** the reviewer clicks its citation, **Then** the real document viewer opens showing that
   actual document.
2. **Given** an exception whose underlying check resolved against more than one real document
   (e.g. a check spanning multiple URLA sub-documents), **When** the reviewer views the citation,
   **Then** each matched document is shown as its own separate, individually clickable link — not
   collapsed into a single link for only the first match.
3. **Given** an exception whose underlying check could not resolve any real document at all,
   **When** the reviewer views the citation, **Then** this is stated honestly (no document to
   open) rather than showing a broken or silently-placeholder link.

### Edge Cases

- **The pulled loan doesn't have enough extracted data to run any checks.** The evaluation must
  complete honestly (an incomplete/no-verdict state), never silently reported as a pass.
- **The engine run itself errors** (e.g. a malformed field). Surfaced as an explicit error status,
  not swallowed into a default status — but, per the queue-suppression rule above, not rendered as
  a badge in the Loan Queue list view.
- **The operator fetches the same loan twice in a row without resetting.** The second run must
  re-evaluate and overwrite the prior verdict, not stack duplicate results.
- **Restore to Gold is clicked with nothing fetched yet.** A no-op on the fetch/verdict side — no
  error, nothing to clear.
- **A route (FHA/VA/USDA) is opened before its simulated count is generated.** Must never render
  as zero/blank in a way that looks like a bug — the simulated count is always present once the
  route exists.
- **A loan re-evaluates while sitting in `NEEDS_REVIEW` with partially-mitigated findings.** A
  second automatic run (see the re-fetch edge case above) MUST NOT silently carry forward or
  discard a human reviewer's prior mitigation work on the old findings — at minimum this must be
  surfaced, not silently overwritten, even if the exact reconciliation behavior is refined during
  planning.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST derive a ruleset the deterministic engine can execute directly from
  the same gold-sourced check catalog already used to drive the rule-authoring screen (`019`'s
  `goldCatalog.json`), so the audit run and the authoring screen agree on what "the ruleset" means.
- **FR-002**: The system MUST convert a loan already retrieved via the existing Touchless pull
  flow (`020`) into the shape the deterministic engine consumes, so the same fetched data both
  displays in the UI and drives the audit.
- **FR-003**: Once a loan fetch completes, the system MUST begin evaluating that loan against the
  ruleset from FR-001 automatically — no separate user action required to start the run.
- **FR-004**: While an evaluation is in progress, the loan's displayed status MUST distinguish
  "running" from any resolved state (passed, failed, resolved, or not-yet-started).
- **FR-005**: Once an evaluation completes, the loan's displayed status MUST reflect the engine's
  actual outcome, tiered by severity: passed (zero rule failures of any severity) / failed (at
  least one CRITICAL-severity rule failure) / needs review (one or more failures, but none
  CRITICAL — i.e., only WARNING or INFO severity). The displayed status MUST NOT be settable
  independently of what the engine actually returned.
- **FR-006**: The loan-status vocabulary MUST be limited to passed / failed / needs-review /
  resolved / error as persisted states, with running modeled as a transient state shown only while
  an evaluation is in flight (not a value stored alongside the other five). Resolved MUST only be
  reachable by a human manually clearing every flagged finding on a needs-review loan (reusing the
  existing per-finding mitigation flow) — never set automatically by an engine run. Error MUST only
  apply when a run never produces a real verdict (insufficient data or an engine failure) — never
  used in place of failed or needs-review when a real verdict *was* produced.
- **FR-006a**: A loan in error status MUST NOT be shown in the Loan Queue list view at all — this
  demo's queue grid never renders an error badge. The error MUST still be visible somewhere
  (the loan detail view or an inline message at the fetch trigger) — never silently swallowed
  entirely.
- **FR-006b**: The Loan Queue MUST display a total of 20 loans. Only the one loan wired to a known
  Touchless `applicationId` participates in the fetch→evaluate→verdict lifecycle (FR-003 through
  FR-006a); the other 19 are cosmetic demo content — realistic-looking borrower/property/loan-type
  data, all shown with `PASS` status, with no real evaluation capability required behind them.
- **FR-007**: The existing "Restore to Gold" control MUST, in addition to its current effect on
  the authored-ruleset draft, also clear any fetched Touchless loan data and any audit verdict
  produced from it.
- **FR-008**: The Routes screen MUST present FHA, VA, and USDA as three separate routes in place
  of the current single "Government" route, each carrying the same block structure as the existing
  routes.
- **FR-009**: Each of the FHA/VA/USDA routes MUST display a non-zero check count, presented with
  the same visual treatment as a real, gold-sourced count — even though today no real FHA/VA/USDA
  rule content exists to back it. This diverges from this project's default practice of never
  presenting an unbacked number as if it were real; that divergence is a deliberate, explicit
  choice for this feature only (see Assumptions), not a precedent for other screens.
- **FR-010**: The source-inspection screen MUST describe the real Touchless retrieval sequence
  (results → indexed documents → extracted data per document) in place of its current generic
  three-source framing.
- **FR-011**: The source-inspection screen MUST state, honestly, that exact in-page/citation
  location for an extracted value is not yet confirmed available from Touchless — not implied as
  already solved.
- **FR-012**: The import/example-documents screen's example document-type list MUST be drawn from
  the real types confirmed on the Touchless call (W-9, 1040 Schedule C, hazard insurance, bank
  statement, credit report, appraisal, application/URLA, gift letter, employment verification).
- **FR-013**: Every exception raised by a real engine run MUST carry a citation identifying the
  real source document(s) it was evaluated against, and clicking that citation MUST open the real
  document — reusing the existing real-document viewer (`020`), not a placeholder or a text-only
  label. When a check resolved against more than one real document, each MUST be shown as its own
  separately clickable link. When no real document could be identified for a check, this MUST be
  stated honestly rather than shown as if a link exists.

### Key Entities

- **Compiled audit ruleset**: The gold-sourced check catalog, re-expressed in the shape the
  deterministic engine executes directly — a second output target from the same source data
  `019`'s `goldCatalog.json` already derives, not a competing or re-derived catalog.
- **Evaluated loan**: A loan fetched via the existing Touchless pull flow, re-expressed in the
  shape the deterministic engine consumes for a run.
- **Audit verdict**: The result of running an evaluated loan against the compiled audit ruleset —
  a pass/fail outcome plus the underlying per-check results, never a value set independently of an
  actual run. Each per-check result's citation identifies the real document(s) it was evaluated
  against (zero, one, or more), not a synthetic/placeholder reference.
- **Loan status (revised)**: `PASS` | `FAILED` | `NEEDS_REVIEW` | `RESOLVED` | `ERROR`, plus a
  transient, non-persisted `RUNNING` display state shown only while an evaluation is executing.
  `FAILED` requires at least one CRITICAL-severity rule failure; `NEEDS_REVIEW` is one or more
  failures with no CRITICAL severity present; `RESOLVED` is reachable only via manual review of a
  `NEEDS_REVIEW` loan, never automatically; `ERROR` means no real verdict was produced at all
  (insufficient data or an engine failure) and, for this demo, is never rendered in the Loan Queue
  list view.
- **Loan Queue (revised)**: 20 loans total. 19 are cosmetic-only (realistic-looking data, `PASS`
  status, no real evaluation behind them); 1 is the real demo loan wired to a known Touchless
  `applicationId`, participating in the full fetch→evaluate→verdict lifecycle.
- **FHA / VA / USDA routes**: Three new routes replacing the single prior Government route, each
  with the existing ~16-block structure and a displayed check count that is simulated (not
  gold-sourced) but shown without a distinguishing visual treatment, per FR-009.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A demo operator can go from "loan not yet fetched" to "a genuine, engine-computed
  verdict displayed" (passed / failed / needs review) in a single triggering click, with no manual
  step in between.
- **SC-002**: The displayed verdict for the demo loan matches, exactly, an independently-run audit
  of that same loan against the same ruleset performed outside the UI.
- **SC-003**: Clicking Restore to Gold after a fetch-and-run cycle returns the app to a state
  indistinguishable from a fresh page load, verified by comparing on-screen state before any fetch
  and after a fetch-then-restore cycle.
- **SC-004**: The Routes screen shows 4 routes total (Conventional, FHA, VA, USDA), each with a
  non-zero displayed check count.
- **SC-005**: The source-inspection and import screens' copy matches the concrete facts in User
  Story 4 with zero remaining generic/placeholder language on the specific points listed.
- **SC-006**: If an evaluation ever produces an error outcome during a demo run, the Loan Queue
  list view shows zero error badges — verified by forcing an error condition and confirming the
  queue grid renders unchanged.
- **SC-007**: The Loan Queue displays 20 loans total; 19 show `PASS` status with realistic-looking
  content and no functional evaluation behind them, and the remaining one is the real demo loan
  reflecting its actual fetch/evaluate lifecycle.
- **SC-008**: Every citation on a real exception opens a real document (not a placeholder), with
  one clickable link per matched document — verified by clicking through every exception on the
  demo loan's actual verdict and confirming each opens genuine Touchless content.

## Assumptions

- **The audit-run engine is `p0/qc_engine` (Pipeline B)**, per explicit instruction — independent
  of the still-unresolved, separately-tracked Pipeline A vs. Pipeline B bake-off happening in
  another worktree. This feature does not wait on that bake-off's outcome.
- **No Touchless-to-engine adapter exists yet for Pipeline B** (Pipeline A has its own, unrelated
  one). Building it is in scope for this feature, not a prerequisite assumed already done.
- **No ready-to-run engine ruleset exists yet that matches the gold-sourced catalog** the
  rule-authoring screen already shows (`019`). The one existing compiled engine ruleset predates
  the gold ruleset entirely and targets a different, now-retired demo loan set. Building a fresh
  compiler from gold data to the engine's ruleset shape is in scope here.
- **FHA/VA/USDA check counts are intentionally simulated, not real**, since the gold ruleset has
  zero actual coverage for any government program today. Shown without a distinguishing visual
  treatment per explicit instruction (FR-009) — an informed, deliberate exception to this
  project's usual anti-false-clean discipline, not an oversight.
- **This supersedes `019`'s prior decision** to keep Government as a single, undifferentiated,
  intentionally-empty route with no Fannie/Freddie-style sub-split. That decision is explicitly
  reversed here for FHA/VA/USDA specifically.
- **Single demo loan in scope for real evaluation.** Only the one loan already wired to a known
  `applicationId` (`020`) is fetchable and evaluable; this feature does not add loan search or a
  multi-loan pull capability (Touchless's API has no search/list endpoint at all, confirmed during
  `020`). The other 19 loans in the expanded queue are cosmetic content only, added purely so the
  queue looks realistically populated for a demo audience — they carry no `applicationId` and no
  functional evaluation requirement.
- **The engine invocation is server-side** (behind the existing `020` backend proxy or a sibling
  process), consistent with `020`'s existing pattern of never running vendor- or engine-adjacent
  logic in the browser.
- **An in-progress evaluation persists across navigation.** If the operator navigates away from
  the loan mid-run and returns, the running/completed state is still accurate — it is not tied to
  a single component staying mounted. This follows the same pattern this app already uses for
  ruleset auto-save/hydration (`019`'s `RoutesFlow`), not a new architectural decision.
- **The engine's citation record gains one small, additive field to carry a real document
  reference** (FR-013). This is the one narrow exception to "the engine stays unmodified" —
  precedented by that same citation record's own history (it was already extended once before,
  additively and backward-compatibly, for `000-synthetic-fixture-generation`'s document-title/
  section/field-label fields) and scoped to metadata only, not new evaluation logic.
