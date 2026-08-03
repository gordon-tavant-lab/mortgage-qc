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

## Status (final, this session)

All of the above: TypeScript clean, backend 55/55 + frontend 35/35 tests passing,
`npm run build` clean, every change verified live via hot-reload — including one real
Bedrock LLM call (not mocked) to prove the decision-narrative pipeline actually works
end-to-end, not just structurally.
