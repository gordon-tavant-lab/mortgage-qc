# Frontend Action Items — 2026-07-30

| | |
|---|---|
| **Source** | Meeting transcript review + inline requirements from Gordon |
| **Context** | Kayla-review mockup (PR #2, branch `worktree-kayla-mockup`) — preparing for David demo |
| **Date** | 2026-07-30 |
| **Status** | All items open, #5 blocked on data from Sendhil |

---

## 1. Loan Queue / Loan Screen Updates

### 1a. Remove confidence score from the loan screen

**What:** Strip `confidence` / `docConfidence` display from the Loan Queue master view and Loan Detail's Exception Review dashboard.

**Why:** Confidence is an internal quality metric, not a reviewer-facing signal. The tri-state status (below) replaces it as the primary signal.

**Affected components:**
- `LoanQueue.tsx` — remove confidence column/badge
- `ApplyView.tsx` — remove confidence display from check result rows
- Keep confidence in backend data — just hide from UI

**Estimate:** Small (1 component update)

---

### 1b. Add status tri-state: Running / Failed / Pass / Resolved

**What:** Replace current binary Pass/Fail with four states:

| State | Meaning |
|---|---|
| `Running` | Loan evaluation in progress (engine still executing) |
| `Failed` | Check defects present, not yet resolved |
| `Pass` | All checks passed, no defects |
| `Resolved` | Defects were present but marked resolved by reviewer |

**Why:** Current Pass/Fail doesn't capture in-flight state or post-review resolution — reviewers need to see what's actively running and what's been triaged.

**Affected components:**
- `mockData.ts` — add `status: "running" | "failed" | "pass" | "resolved"` to `Evaluation`
- `LoanQueue.tsx` — update status badge rendering
- `ApplyView.tsx` — add "Mark as Resolved" action for defects

**Estimate:** Medium (3 components, new resolver action)

---

### 1c. Show block-level pass/fail status in queue

**What:** Loan Queue master table should surface which *blocks* passed/failed per loan, not just overall loan status.

**Example:**
```
Loan 001  |  Assets: Pass  |  Application: 2 Failed  |  Income: Pass
```

**Why:** "In your review of the loan, you should say blocks have passed or not" — reviewers need block-level status at a glance without drilling into each loan.

**Affected components:**
- `mockData.ts` — add `blockResults: { blockId: string, status: "pass" | "fail", failedCount: number }[]` to `Evaluation`
- `LoanQueue.tsx` — render block status badges per row

**Estimate:** Medium (data model extension + queue column)

---

## 2. Route Screen — Add DAG Diagram

**What:** Add visual DAG (directed acyclic graph) to Route Detail showing route composition: Checks → Blocks → Route, with parallelism/sequence relationships.

**Why:** "That diagram was for the loan running, but these are running so quick... to showcase the route and what's inside makes sense. Rather than a list, if you have a diagram I can go to and click on a block to fix it."

**Behavior:**
- User can click a block node in the diagram to drill into it (replaces or supplements the existing two-pane block picker)
- Shows cardinality: "these many checks become this many blocks, this becomes this route"
- Indicates parallel vs. sequential execution where applicable

**Affected components:**
- `RouteDetail.tsx` — add new `<RouteDAG>` component above or replacing the two-pane block picker
- Consider using a simple SVG-based layout (no new deps) or React Flow if already in the project

**Estimate:** Large (new component, layout logic, click-to-drill wiring)

**Open question:** Does the DAG show execution order (parallel/sequential blocks) or just containment (blocks in route, checks in block)? Transcript suggests containment + parallelism hint.

---

## 3. Check-Level Document/Page Citations

**What:** Each check result in the Apply screen should show *which document(s)* and *which page(s)* the extraction came from.

**Example:**
```
employment_start_date_1003
  Extracted from: 1003 URLA, page 2
  Confidence: 0.97
```

**Why:** "Closing docs came in. We were able to extract the data... we did the route on it. So you should be able to connect the dots between, hey, closing docs came in, we extracted the data."

**Data model:**
- Extend `CheckResult.citation` from current `{ confidence: number }` to `{ docName: string, pageNumbers: number[], confidence: number }`
- Real schema already exists in engine (`p0/qc_engine/extract.py` — `ExtractionResult` carries `source_doc` + `page`); mockup just needs to mirror it

**Affected components:**
- `mockData.ts` — add `docName` and `pageNumbers` to `MOCK_EVALUATION.auditTrace` citation objects
- `ApplyView.tsx` — update Source Citation column to render doc name + page(s)
- `SourceCitation.tsx` — extend to handle doc/page display (currently only shows grounding/sourceLocator)

**Estimate:** Medium (data model + 2 components)

---

## 4. Multi-Document Field Validation UI

**What:** When a single field (e.g. `purchase_amount`) needs validation against multiple document sources (1003, CD, approval letter), show all extracted values side-by-side with agreement/disagreement status.

**Example layout:**
```
Purchase Amount
  1003:     $450,000  ✓
  CD:       $450,000  ✓ agrees with 1003
  Approval: $450,000  ✓ agrees with 1003
```

**Why:** "Purchase amount - needs to validate against each - 3 documents" — some fields require cross-document reconciliation, not just a single extraction.

**Affected components:**
- New component: `<MultiDocFieldComparison>` (or extend `ApplyView.tsx` with an expanded row view)
- `mockData.ts` — for multi-source fields, add `alternateExtractions: [{ docName, value, pageNumbers }]` alongside the primary `citation`
- Applies to fields with `expected_sources: ["doc"]` AND multiple doc types in the catalog (1003, CD, VOE, etc.)

**Estimate:** Large (new comparison view, data model, agreement logic)

**Open question:** Does the UI auto-flag disagreements, or just display them for manual review? (Likely the former — auto-flag via `agree_doc_*` checks, display here.)

---

## 5. Real Loan Data Integration

**What:** Replace synthetic `MOCK_EVALUATION` data with real loan results from loans 1-5.

**Includes:**
- Real extracted field values
- Real check verdicts (from `defect_manifest.json` and `audit_trace.json`)
- Real document confidence scores
- Real page citations
- Real block/route execution results

**Why:** "Let's just make it real now... have some actual loans in there, have some documents in there... we can connect the dots between, hey, closing docs came in, we extracted the data, that data was this loan MISMO file, we did the route on it."

**Blocked on:** Sendhil providing updated defect keys for loans 2-5 (loan 1 already has full data in `examples/mortgage-qc/run-018-loan-01/`).

**Affected components:**
- `mockData.ts` — replace `MOCK_EVALUATION` with loader function reading real `audit_trace.json` + `defect_manifest.json`
- All screens — no component changes needed, just data source swap

**Estimate:** Medium (data adapter, path wiring) — but blocked on external dependency

---

## 6. Loan Processing Trigger Display

**What:** Loan Queue should indicate whether each loan was triggered manually ("Run on Demand" button) or automatically (milestone event: closing, funding, post-closing).

**Example badge:**
```
Loan 001  |  Manual Run
Loan 002  |  Auto: Post-Closing Milestone
```

**Why:** "I have a list of loans that I want to run routes against... let me run it in front of you on demand, but mostly this will be run by triggers. As a loan achieves a closing/funding/post-closing milestone, we will automatically pick that loan up."

**Data model:**
- Add `trigger: { type: "manual" | "automated", milestone?: "closing" | "funding" | "post_closing" }` to `Evaluation`

**Affected components:**
- `mockData.ts` — add `trigger` field to `MOCK_EVALUATION`
- `LoanQueue.tsx` — render trigger badge per row

**Estimate:** Small (data field + badge rendering)

---

## Summary Table

| # | Action Item | Screen(s) | Estimate | Status |
|---|---|---|---|---|
| 1a | Remove confidence score display | Loan Queue, Apply | Small | Open |
| 1b | Add Running/Failed/Pass/Resolved states | Loan Queue, Apply | Medium | Open |
| 1c | Show block-level pass/fail status in queue | Loan Queue | Medium | Open |
| 2 | Add DAG diagram to Route Detail | Route | Large | Open |
| 3 | Add document + page citations per check | Apply | Medium | Open |
| 4 | Multi-document field comparison UI | Apply (new view) | Large | Open |
| 5 | Wire real loan data (loans 1-5) | All screens | Medium | Blocked on Sendhil |
| 6 | Show loan trigger type (manual/auto) | Loan Queue | Small | Open |

**Total effort estimate:** 1 Small (1a) + 2 Small (6) + 3 Medium (1b, 1c, 3, 5) + 2 Large (2, 4) = **~2-3 days of focused frontend work** (excluding #5's data dependency wait).

---

## Implementation Order (Recommended)

1. **#1a, #1b, #6** — Loan Queue status refinements (quick wins, high visibility)
2. **#1c** — Block-level status (depends on 1b's status model)
3. **#3** — Document/page citations (foundational for #4)
4. **#4** — Multi-document comparison UI (builds on #3)
5. **#2** — DAG diagram (high-impact visual, can work in parallel with above)
6. **#5** — Real data integration (final step, validates all above work)

---

## Open Questions

1. **DAG scope:** Does the route DAG show execution order (parallel/sequential) or just containment hierarchy? (Transcript suggests both: "parallelism... these many checks become this many blocks")
2. **Multi-doc agreement logic:** Should the UI auto-flag disagreements (likely yes, via existing `agree_doc_*` checks) or just display raw values for manual review?
3. **Confidence removal scope:** Strip from all screens, or keep it in a developer/debug view? (Transcript implies full removal from reviewer-facing UI)
4. **Real data path:** Will loans 2-5 come as individual `run-NNN-loan-NN/` directories matching loan 1's structure, or a different format? (Affects #5's data loader implementation)

---

## Related Files

- **Mockup branch:** `worktree-kayla-mockup` (PR #2, `.claude/worktrees/kayla-mockup/`)
- **Real loan data:** `examples/mortgage-qc/run-018-loan-01/` (loan 1 only, as of 2026-07-30)
- **Transcript source:** `src/doc/transcript/meeting.md`
- **Existing action items doc:** `output/CITATION-AND-COMPILER-GAPS-2026-07-29.md` (backend/compiler gaps, not frontend)
