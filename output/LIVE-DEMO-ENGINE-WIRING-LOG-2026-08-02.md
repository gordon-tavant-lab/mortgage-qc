# Live Demo / Engine-Wiring Session Log — 2026-08-02

Working log of everything requested and done on the `feature/live-demo-engine-wiring`
branch (PR #9), in request order. Each entry: what Gordon asked, what was actually
changed, and any judgment call made along the way (with the reasoning, so it can be
revisited later without re-deriving it).

## 1. Repo/worktree reconciliation (prerequisite)

**Finding, not a request**: this session's spec019/020/021 demo-app work had been
happening in a git worktree that was never properly connected to the real
`gordon-tavant-lab/mortgage-qc` repo — it was tracked as plain files inside the
unrelated `gordon-os-marketplace` mono-repo instead. Meanwhile the real repo's own
`main` had independently built a standalone `engine/` pipeline (`023-standalone-qc-engine`,
resolve6/7/8 passes) with no knowledge of the demo-app work.

**Done**: created a proper `git worktree` of the real repo at
`demo-sites/mortgage-qc-prod/.claude/worktrees/live-demo-engine-wiring`, branch
`feature/live-demo-engine-wiring`, off real `main`. Ported the entire demo app
(frontend/src, backend/src, frontend/scripts, the untracked `demo/touchless/` fixture,
specs/019 + specs/021) wholesale — verified the real repo had no independent frontend/
backend changes to lose first.

## 2. "Wire the live demo to `engine/` instead of `p0/qc_engine`"

**Request**: rewire the live demo's audit engine from `p0/qc_engine` (the earlier
bake-off copy) to `engine/` (the repo's own standalone, actively-maintained pipeline),
update docs, run a real test and report the result.

**Done**:
- New `engine/qc_engine/run_touchless_audit_for_demo.py` entry point (ported from
  `p0`'s version, adapted to `engine/`'s own adapter + compiler).
- Ported two small pieces `engine/` was missing, so the "click a citation to open the
  real document" feature kept working: `DocCitation.document_ids` (`model.py`,
  `fixture_loader.py`) and curated `doc_present_*` fields now carrying real Touchless
  `documentId`s (`adapters/touchless_adapter.py`).
- `backend/src/routes/audit.ts` now calls the `engine/` script instead of the `p0`
  one.
- Docs: addendum notes in `specs/021-touchless-audit-run/{plan,research}.md` pointing
  at the switch (kept the original design docs intact rather than rewriting history),
  plus a new "Live demo wiring" section in `engine/README.md`.

**Verified live** (not just unit tests): ran the new script against the real demo
loan. Result: `loanStatus=NEEDS_REVIEW`, 668 checks compiled / 437 excluded, 133 PASS /
92 NEEDS_REVIEW / 443 NOT_APPLICABLE / 0 FAIL, 12 checks carrying real Touchless
document citations. Backend 49/49 tests, frontend `tsc -b` clean + 35/35 tests + build
clean.

Shipped as **PR #9**: https://github.com/gordon-tavant-lab/mortgage-qc/pull/9

## 3. "Remove the sample-data banner / where's the button to trigger a live fetch / loan detail looks broken, add filter+sort" *(from earlier in the session, spec021 itself — not this branch, listed for continuity)*

Already resolved before this branch existed — see `specs/021-touchless-audit-run/`
commit history (`ecef6ef`, `4de06b4`) for that round.

## 4. "Hide the Touchless loan from the queue until fetched; add an Activate Live Demo button; show it appear with a real-time RUNNING → verdict transition"

**Request**: the one real Touchless-backed loan shouldn't sit in the queue showing
"Not Yet Evaluated" before anything happens — it should not exist in the list at all
until actually fetched, then appear live going RUNNING → a real verdict. Trigger this
from the Settings menu instead of requiring the user to already be on that loan's
detail page.

**Done**:
- `LoanQueue.tsx`: filters `MOCK_LOANS` down to `visibleLoans`, excluding the
  Touchless-backed loan while its display state is `"not_fetched"`.
- New `ActivateLiveDemoButton.tsx` in the Settings menu (`SettingsMenu.tsx`): one
  click switches the data source to Live and fires the real pull + audit run, then
  closes the settings panel.
- The RUNNING → resolved transition itself was **already wired** (`LoanStatusBadge`'s
  pulsing "Running…" badge + `deriveLoanDisplayState`) — this request's actual gap was
  that there was no way to trigger the *first* fetch once the loan was hidden from the
  queue; the Settings button closes that gap.

## 5. "Remove the Open Exceptions header; rephrase the Loan Queue subtitle to be marketing-facing"

**Done**: removed the "Open Exceptions" red panel and its now-dead
`unresolved`/`criticalUnresolved` computations/imports from `LoanQueue.tsx`. Subtitle
changed from *"Point a route at a target set of loans and run on demand. 'I'm done
with this loan. Next one, next one, next one.'"* to *"Every loan runs the full gold
ruleset automatically — real, citation-backed verdicts the moment a loan lands in the
queue."*

## 6. "Make the 4 status boxes clickable filters; paginate the loan list at 20/page; add ~50 synthetic loans"

**Done**:
- Stat boxes (Pass/Failed/Needs Review/Resolved) are now toggleable filter buttons
  (click again to clear), filtering by each loan's **actual displayed status**
  (`deriveLoanDisplayState`), not its static seed — so this correctly reflects the one
  real loan's real verdict once it resolves.
- Pagination at 20/page (Previous/Next, "Showing X–Y of Z", "Page N of M" — same
  pattern already used in the Apply tab's table).
- Grew `MOCK_LOANS` from 20 to 50 (1 real + 49 cosmetic), giving 3 pages at 20/page.

**Decision (flagged, not silently made)**: all 49 new cosmetic loans are seeded
`status: "PASS"`, matching the existing 19 — never fabricating a FAIL/NEEDS_REVIEW for
a loan that was never actually evaluated (this project's standing anti-fabrication
rule). Net effect: clicking Failed/Resolved currently shows an honest empty state;
Needs Review shows the one real loan once its real verdict resolves (it resolved
NEEDS_REVIEW in the test run above). If varied cosmetic statuses are wanted purely for
filter-demo variety, that's a separate, explicit ask — not done here without checking
first.

## 7. "NOT_APPLICABLE isn't Failed — don't show it in the list"

**Finding**: this was a real bug, not just a display preference. `ApplyView.tsx`'s
`bucketFor()` was bucketing by **severity** for any non-PASS row, so a CRITICAL-severity
`NOT_APPLICABLE` check (precondition not met — never actually ran) was counting as
"Failed Defective." That's why the demo showed 506 "Failed Defective" against 0 real
engine FAILs.

**Done**: `bucketFor()` now buckets by the check's real `status` (`PASS`→passed,
`FAIL`→failed, everything else terminal-but-non-pass→needsReview). `NOT_APPLICABLE`
returns `null` and is excluded from every bucket and the table entirely, per Gordon's
explicit call. Verified against the real cached audit result: 133 Passed / 0 Failed /
92 Needs Review, 443 `NOT_APPLICABLE` correctly hidden (previously misreported as 506
Failed / 29 Needs Review).

## 8. "Make sure the Inspect Sources page's numbers are real and live; remove the Exceptions tab"

**Finding**: the "reconciliation" table (Closing Doc / LOS Export / MISMO XML,
"2 fields disagree") on the Inspect Sources tab was **100% static mock data**
(`MOCK_SOURCE_ALIGNMENT`), entirely disconnected from the real pulled loan — it even
showed a fabricated credit score of 665 while the real loan's actual FICO (shown
correctly elsewhere on the same page) is 740. Traced further: this demo genuinely has
no second or third live data source wired in — Touchless is the only real feed (the
engine's own `SourceValue.sources` map for LOS/MISMO is always empty in the current
adapter, and the real audit run produced zero `RECONCILE`-phase results) — so there is
no real 3-way comparison this page could honestly show today.

**Done**: removed the fabricated table and its supporting `MOCK_SOURCE_ALIGNMENT`
data/`SourceAlignmentRow` type entirely, replacing it with a plain statement of the
actual gap (matching the "known limitation, not silently solved" framing already used
elsewhere on that same page for the citation-location question). The "Live Touchless
Application" panel above it was already genuinely real/live — separately fixed it to
format raw epoch-millisecond `*Date` fields (e.g. `1784592000000`) as readable dates
instead of a bare number, since that read as broken/fake data even though it wasn't.

Also removed the **Exceptions tab** from the loan detail view (`LoanDetail.tsx` +
`nav.ts`'s `LoanDetailTab` type) — Inspect Sources / Apply only now.

**Open item, not yet decided**: if a real cross-source reconciliation story matters
for the pitch, it needs an actual second data feed (LOS export or MISMO XML) wired in
— flagged to Gordon, not started.

## 9. "Push the DU auto-pass rules to the last pages, not the top of page 1"

**Finding**: ~111 of the 133 real "Passed Assertions" are DU (Desktop Underwriter)
checks that auto-pass only because this project has no live DU connection
(`autopass_no_system_access.json`'s demo-scoped decision) — their message reads
`"auto-pass: requires verification inside du_not_accessible..."`. These were
interleaved with the 22 genuinely-evaluated PASS rows (`"Predicate satisfied."`) in
whatever order the engine happened to return them, so the first page often opened on
an auto-pass caveat instead of a real evaluation.

**Done**: `visibleRows` now stable-sorts real evaluations before auto-pass rows within
whichever bucket is selected — never reordered out of the list, just deprioritized so
genuine results lead. Verified against the cached real result: the first 5 rows are
now all `"Predicate satisfied."`, the auto-pass rows all land on later pages.

## Status (as of item 9)

All of the above: TypeScript clean, backend 49/49 + frontend 35/35 tests passing after
every change, verified live in the browser (http://localhost:3001) via hot-reload
throughout. Items 4–9 are committed to `feature/live-demo-engine-wiring` (PR #9) as of
this log; item 2's initial commit (`b308456`) was pushed earlier in the session.

## 10. "Add the QC audit (LLM) narrative here at the bottom of the page (spec014)"

**Request**: bring back spec014's decision-narrative feature (an LLM-authored, read-
only prose explanation of a loan's already-computed result), at the bottom of the
Inspect Sources tab.

**Real gap found before building anything**: `decision_narrative.py`
(`p0/qc_engine/compiler/`) requires a **signed FactVocabulary** to ground its claims
and reject fabricated citations — that vocabulary belongs to a separate ontology-
extraction pipeline (`fact_vocabulary.py`, `build_loan_profiles*.py`) that was never
built for the Touchless-fetched loan, and was explicitly excluded from `engine/`'s
scope during the `023-standalone-qc-engine` extraction. Presented this to Gordon
directly rather than either skipping the grounding requirement or guessing at scope;
his call: build a real vocabulary, don't skip the safety net.

**Done**:
- Ported `fact_vocabulary.py`, `knowledge_base.py`, `decision_narrative.py` into
  `engine/qc_engine/compiler/` (the AMQ-specific `compile_llm.py` was NOT ported —
  replaced with a minimal `bedrock_client.py` carrying only what `decision_narrative.py`
  actually needs: `MODEL_SONNET` + a Bedrock client factory).
- New `gold_fact_vocabulary.py`: builds a real, signed FactVocabulary directly from
  the gold ruleset's own already-compiled `citations` field
  (`storage/rules/gold/data/rules_compiled.json`'s `cards[].citations` — real Fannie
  Mae Selling Guide section references, e.g. `B3-3.1-02`) — no fabrication, no
  separate Selling Guide corpus/RAG step. Signed immediately since it's deterministically
  derived from already-reviewed, already-compiled data, not new unreviewed content.
- New `engine/qc_engine/run_decision_narrative_for_demo.py` entry point (re-runs the
  same real audit to get a live `RunResult`, builds the vocabulary, calls
  `decision_narrative.generate()` against a real Bedrock Sonnet call).
- New backend route `POST /api/audit/:applicationId/narrative` and frontend
  `DecisionNarrativePanel.tsx` — **on-demand only** (a button), never fired
  automatically alongside the deterministic audit run, since this is a real, billed
  LLM call.

**Two real bugs found and fixed in the ported `decision_narrative.py` itself**,
surfaced by one real end-to-end test (not caught by unit tests, which only mock the
LLM response): its `_CHECK_ID_RE` check-id grounding regex assumed every real
check_id is a clean hyphenated kebab-case token (true for the old p0/AMQ-workbook
ruleset it was built against) — verified 0/668 of this pipeline's real gold-ruleset
check_ids match that shape (they're `"{card_id}::{exception_code}"`, routinely
containing spaces and uppercase words, e.g. `"PC::Closing Conditions::UW
Condition-A"`). The regex silently found zero matches instead of validating the
narrative's real, hand-verified-accurate check citations — never a false accept, but
an unexercised safety check. Fixed by switching check-id grounding from regex-
extraction to **closed-set membership matching** (for each of the loan's real
check_ids, does `"check <id>"` appear in the text, any case) — correct regardless of
the id's internal shape, and structurally can never mark a fabricated id as
"referenced" since it only ever matches against the real set. Guide-citation grounding
(a separate, narrower regex for clean `[A-Z]{1,2}[\d.\-]*\d`-shaped codes) was
already correct and needed no change.

**Verified live** (one real, billed Bedrock call): generated a real narrative for the
real demo loan (NEEDS_REVIEW, 92 real needs_review checks) — correctly explained the
disposition, named 3 real checks by their real (irregular-shaped) check_id, cited 5
real Fannie Mae Selling Guide sections pulled straight from the gold ruleset's own
citation data, and correctly stated the exact remainder count (89) for the checks not
individually detailed. `validation_attempts: 1` (passed grounding on the first try).

## 11. "Add to the far right a measure of how fast this QC audit process took, in milliseconds"

**Done**: backend now measures real wall-clock time around the audit-run subprocess
(`Date.now()` before/after the same `execFile` call the rest of the response is built
from — never estimated) and returns `durationMs`. Frontend shows "QC audit completed
in Xms" on the far right of the "Live Touchless Application" panel's header, once the
audit has actually resolved.

**Live-testing catch**: the first version crashed the running demo — a stale, already-
cached audit result from before this field existed had `durationMs: undefined`, and
`undefined.toLocaleString()` threw. Fixed by guarding on `typeof durationMs ===
"number"` before rendering; told Gordon a one-time refresh would clear the stale
cached state.

## 12. "Make this an infographic showing the QC audit process"

**Done**: replaced the 3 plain, unconnected white cards (Application Results /
Indexed Documents / Extracted Data) on Inspect Sources with a connected flow diagram
(`QcAuditProcessFlow.tsx`) — Touchless API source node -> the same 3 real GET calls,
now visually chained with arrows -> a "Deterministic Engine" sink node. Same real
content as before (no new claims), presented as a process rather than 3 isolated
facts. In-app, not a standalone asset, per Gordon's call.

## Status (as of item 12)

All of the above: TypeScript clean, backend 55/55 + frontend 35/35 tests passing,
`npm run build` clean, every change verified live via hot-reload — including one real
Bedrock LLM call (not mocked) to prove the decision-narrative pipeline actually works
end-to-end, not just structurally.

## 13. "Auto-kick off the narrative generation as soon as the audit is complete"

**Request**: stop gating narrative generation behind a manual button — fire it
automatically the instant a real audit run resolves.

**Decision**: this is a real, billed Bedrock call on every audit run now, not an
occasional on-demand action — flagged plainly, but Gordon's explicit call, not a
default I chose. Reversing the earlier "on-demand only, never automatic" design
decision from item 10.

**Done**: `dataSourceContext.tsx`'s `runAudit` now calls `generateNarrative`
immediately after `setAuditRuns` resolves, in the same "no second click" spirit
FR-003 already used for pull -> run. Reordered the two `useCallback`s
(`generateNarrative` now defined before `runAudit`, which references it) since
`runAudit` needs a stable reference to call it.

**Test fallout, expected and fixed**: two pre-existing `dataSourceContext.test.tsx`
tests asserted exact `fetch` call counts (2 and 4, for pull+audit chains) — updated to
3 and 6 to account for the new auto-triggered narrative fetch in each chain.

## 14. "Remove the info boxes"

**Done**: removed both static "Not yet confirmed: whether Touchless's extraction
output can identify a value's exact in-page location..." and "This demo's live pull
has one real data source..." info boxes from Inspect Sources. (The underlying facts
they stated are still true and still relevant if this ever needs re-explaining to
someone new — just no longer surfaced as permanent on-page callouts.)

## 15. "The LLM narrative should have at least 2 sections: what kind of loan this is (type, program, scenario, full picture), then the audit result explained for a loan officer/auditor"

**Done**: this required real new data plumbing, not just a prompt tweak — the
narrative previously only ever saw `RunResult` content (disposition, checks,
citations), never the loan's own characteristics.
- New `_loan_overview()` in `run_decision_narrative_for_demo.py`: reads real values
  straight off the same adapted `CanonicalLoan` the engine itself runs against
  (program, purpose, amount, note rate, term, LTV/DTI/housing ratio, credit score,
  borrower name, property state/type, application date, underwriting type) — omits
  any field the loan's own data didn't populate, never fills a gap with a guess.
- `decision_narrative.py`: `generate()`/`_build_user_message()` now take an optional
  `loan_overview` dict, included in the prompt payload. Rewrote `SYSTEM_PROMPT` to
  require exactly two sections, "Loan Overview" (grounded ONLY in `loan_overview`,
  explicitly forbidden from inventing a missing field) and "Audit Findings" (the
  original disposition/citation-grounded explanation, refocused on what's actually
  actionable for a loan officer or auditor, not just an enumeration).
- `DecisionNarrativePanel.tsx`: splits the returned text on the two real section
  headings and renders them as two visually distinct, labeled blocks instead of one
  paragraph (falls back to one plain block if a future model response doesn't match
  the expected shape — never crashes on it).

**Verified live** (one real Bedrock call against the real demo loan): Loan Overview
correctly stated Conventional / Purchase / $260,000 / 30-year / 6.50% note rate /
73.86% LTV / 740 credit score / 14.55% DTI / PUD Detached in Hawaii / Desktop
Underwriter / application date 2026-07-20 — every one of those a real value read off
the loan's own extracted data, not invented. Audit Findings section followed with the
disposition explanation, correctly grounded (3/3 real check citations, 5 real Guide
citations, `validation_attempts: 1`).

## Status (as of item 15)

All of the above: TypeScript clean, backend 55/55 + frontend 35/35 tests passing,
`npm run build` clean, verified live via hot-reload throughout, including two
separate real (billed) Bedrock calls to prove the narrative pipeline end-to-end, not
just structurally.

At this point the branch was still "not organized under a formal spec number" —
everything above was ad-hoc commits on `feature/live-demo-engine-wiring`. That
changed with item 16.

## 16. "Let's create a new spec" — the rule-author page upgrade (spec024)

**Request** (7 items, verbatim intent): a live read-only DAG view of a route's active
blocks, positioned between the route header and the two list boxes; convert the
inline "Edit Check" panel into a popup modal (dimmed background); add pagination
(25/page) to the Available/Active Blocks and Available/Active Checks lists; hide
not-yet-buildable ("NOT_COMPILED") checks by default with a "Show not built" toggle;
allow adding/removing blocks from a route via a modal (matching the check-edit
modal's pattern); show real, as-close-to-true FHA/VA/USDA check counts derived from
the AMQ rule workbook, replacing the existing simulated placeholder; allow
adding/removing checks from a block the same way.

**Done**: ran the formal spec-kit process for the first time on this branch —
`specs/024-route-dag-editor/spec.md` (5 user stories, 16 functional requirements, 5
success criteria), `plan.md`, `tasks.md` (27 tasks), committed and pushed as their own
commits, all still on `feature/live-demo-engine-wiring`/PR #9 (not a new branch —
recorded as an explicit Assumption in the spec itself, consistent with items 1-15).

**Judgment call made before implementation, not after**: before writing the plan, a
`g-os-contrarian` check surfaced that the 7th item's literal ask (real FHA/VA/USDA
counts "derived from the AMQ workbook") would still be a fabrication — the gold
ruleset is compiled from the Fannie Mae Selling Guide and covers Conventional only;
no AMQ-workbook data is compiled into anything the demo actually runs checks against.
Confirmed with Gordon this correction before proceeding: User Story 5 became "FHA/VA/
USDA keep the same 16 blocks as Conventional but show an honest 0 checks," not an
AMQ-derived number. This is the same anti-fabrication discipline this project has
applied consistently since spec019 (see e.g. item 7's NOT_APPLICABLE fix) — caught
*before* code was written this time, not after.

**Implemented** (full 5-user-story scope):
- `Modal.tsx` (new) — shared scrim+centered-panel component, extracted from the
  markup already duplicated in `ExceptionReview.tsx`/`RetrievedDocumentViewer.tsx`.
- `RouteDagView.tsx` (new) — live DAG of a route's active blocks, a pure function of
  `route.blockIds` so it re-renders with zero extra wiring whenever a block is
  activated/deactivated.
- `BlockMembershipModal.tsx` (new) — wraps the *already-working* block
  activate/deactivate action in an explicit confirm modal (the action itself wasn't
  new; only its modal presentation was).
- `BlockDetail.tsx`'s inline "Edit Check" panel moved into `Modal.tsx`, with a
  field-value snapshot taken on open so Cancel/Escape/scrim-click reverts in-progress
  edits and only an explicit "Done" keeps them.
- 25/page pagination on all four Available/Active lists (route and block level).
- A "Show not built" checkbox, scoped correctly to the Available Checks list only —
  caught and fixed a real regression during manual testing where the first pass had
  also hidden NOT_COMPILED checks from the *Active* list (which must always stay
  visible, badged "wired, not yet buildable").
- `build_gold_catalog.py`: replaced `build_simulated_program_blocks()` (the FHA/VA/
  USDA non-zero placeholder) with `build_empty_program_blocks()` — same 16-block
  structure, `checkIds: []`. Also fixed two related stale bugs: `RouteDetail.tsx`'s
  `ROUTE_BLOCK_PREFIX` and `BlockDetail.tsx`'s real-coverage guard both still checked
  for a `"gov-"` prefix that no longer matches any real block id since spec021's
  four-route split (fha-/va-/usda- prefixed blocks were silently falling through the
  wrong code path).

**Verified**: 62/62 tests, `tsc -b` and `npm run build` clean, then manually verified
live at `localhost:3001` — deactivated and reactivated a block via the modal and
watched the DAG lose/regain its node with no reload; opened the 195-check "Product
Specific" block and confirmed "Showing 1–25 of 195" / "Page 1 of 8"; opened the Edit
Check modal and confirmed Cancel reverts an in-progress field edit; confirmed FHA/VA/
USDA show 16 blocks / 0 checks each.

**Then ran the full spec-kit quality loop**: `/speckit-analyze` found 0 critical/high
issues but 2 doc-consistency findings — the Edge Cases and requirements-checklist
Notes sections still described the *original* (pre-correction) AMQ-derived US5 ask,
stale after the contrarian correction above. Fixed both. `/speckit-converge` then
reported clean (0 actionable gaps) against the corrected spec/plan/tasks.

## 17. "Make the DAG show the process running in parallel, not sequential" (reference:
a fan-out/fan-in diagram — intake → fan-out joint → N parallel steps → fan-in joint →
report)

**Request**: the DAG built in item 16 read left-to-right as one long sequential
chain; Gordon wanted it to instead show the real shape of how the engine evaluates a
route — every active block run independently, then aggregated into one verdict — a
fan-out/fan-in topology, not a pipeline.

**Done**: reworked `RouteDagView.tsx` entirely. New shape: Route entry → Fan-Out
joint → every active block rendered as a parallel row (elbow-connected off two shared
vertical trunk lines) → Fan-In joint → "QC Report Generator". The trunk-line
positions are computed in pure CSS from a fixed row height — no DOM measurement, no
refs, no `ResizeObserver` — since every block row is the same height. Still a pure
function of `route.blockIds`, so live updates on block add/remove kept working
unchanged (same tests, all still green).

**Verified**: 62/62 tests unchanged, `tsc -b`/`npm run build` clean, then a live
screenshot at a narrower viewport specifically to inspect the elbow-connector lines
clearly — confirmed correct fan-out on the left (Fan-Out joint → each block) and
fan-in on the right (each block → Fan-In joint).

## 18. "Hide the two list boxes on initial load; add an Edit button to the DAG's
top-right corner; clicking it opens the list boxes as a popup modal"

**Request**: the route page still showed the DAG *and* the full Available/Active
Blocks lists below it at all times. Gordon wanted the page to open DAG-only, with an
explicit Edit action revealing the lists in a modal — "document this to the spec
before we proceed."

**Done, spec-first per the explicit instruction**: added User Story 6 to
`specs/024-route-dag-editor/spec.md` (FR-017/018/019, SC-006, plus an Assumptions
note on the resulting nested-modal pattern), and a Phase 8 to `tasks.md` — committed
and pushed *before* any code changed.

**Implemented**:
- `RouteDagView.tsx` gained an optional `onEdit` prop, rendering a small Edit
  button in the panel's top-right corner only when a handler is provided.
- `RouteDetail.tsx`: the entire Available/Active Blocks two-column grid (pagination
  included) now lives inside a new `<Modal title="Edit Blocks" widthClassName=
  "max-w-5xl">` (added the `widthClassName` override to `Modal.tsx` itself, since the
  default `max-w-2xl` would have cramped two side-by-side lists), toggled by the new
  Edit button. The existing per-block membership modal (item 16) nests inside this
  one unchanged when a row is clicked.
- Updated `RouteDetail.test.tsx` (list-box assertions now open the Edit modal first)
  and `RouteDagView.test.tsx` (new Edit-button coverage): 66/66 tests pass.

**Verified live**: fresh route-page load shows DAG-only (no "Available Blocks"/
"Active Blocks" text anywhere in the DOM); Edit reveals both lists dimmed-backdrop;
clicking a block row opens the membership modal nested on top (confirmed the click
correctly closed only the *inner* modal, leaving the outer one open — proving the
two-modal z-order/dismiss behavior works as intended, not just "looks right");
dismissing either modal, in either order, leaves state exactly as it was before —
zero mutation from browsing alone.

## Status (final, this session)

All of items 1-18: TypeScript clean, `npm run build` clean, 66/66 frontend tests
passing (backend unchanged since item 15, still 55/55). Every UI change in items
16-18 was verified live in the browser at `localhost:3001`, not just via the test
suite — including two real, intentional bugs caught and fixed during that live
verification (the not-built toggle leaking into the Active list in item 16; the
nested-modal dismiss behavior double-checked in item 18) before being called done.

Current repo state (2026-08-03): all work is committed and pushed to
`feature/live-demo-engine-wiring`. **Not yet merged to `main`** — open as
[PR #9](https://github.com/gordon-tavant-lab/mortgage-qc/pull/9), still in **draft**
status. As of item 16, this branch's rule-author-page work *is* organized under a
formal spec — `specs/024-route-dag-editor/` — with a completed spec → plan → tasks →
implement → analyze → converge cycle; items 17-18 extended that same spec
(topology rework, then a new User Story 6) rather than starting a new one, each
documented in the spec before the corresponding code was written.
