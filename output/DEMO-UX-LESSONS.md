# UX Lessons from the Two Reference Demos

| | |
|---|---|
| **Subject** | `examples/mortgage-qc/cockpit/frontend/` (the live demo at `mortgage-qc.loopinhuman.com` — Gordon's forked/extended build of Olav's original, 77 of 79 commits are Gordon's) and `examples/mortgage-qa_qc-tool/` (the AI-Studio React prototype `CLAUDE.md` names as this project's front-end design-language reference) |
| **Lens** | Interaction/UX patterns specifically — citation evidence, DAG visualization, confidence scores, and other reusable patterns — not architecture (see `PRIOR-ART-OLAV-MORTGAGE-QC.md` for the backend/reuse audit) |
| **Method** | Direct source read of both repos' actual components (not just the deployed JS bundle) |
| **Verdict shape** | Per pattern: what it does, is it worth keeping, what to change for `-prod` |

---

## 1. Citation evidence — the strongest pattern in either demo, worth carrying forward almost as-is

Both demos treat "click to see the exact source" as a first-class interaction, and the loopinhuman.com
build has iterated on it twice (see specs `004-citation-dedup`, `005-review-center-ux`) — this is
mature, battle-tested UX, not a first draft.

**What's good:**
- **Deep-link to the exact page**: citation buttons link straight to `pdfUrl#page=N`, opening the
  source PDF at the cited page in a new tab (`ExecutionDetailPage.jsx`). `mortgage-qa_qc-tool`'s
  `ExceptionReview.tsx` does the same via `onOpenPdfCitation(docName, pageNum, segmentSnippet)` →
  `PdfViewerModal`. Both land the reviewer on the exact page, not just "here's a PDF, good luck."
- **Citation dedup by logical document identity** (spec `004-citation-dedup`, shipped): if a finding
  cites 3 paystubs for the same borrower, show **one** citation link, not three identical-looking
  buttons. Identity = same document type + same borrower (inferred from title); different borrowers
  or different types stay separate. This is a real, hard-won lesson — the naive "one button per
  matching document" approach was tried first and explicitly walked back.
- **Collapsed by default, count visible**: "▼ Show N citations" toggle — citations don't clutter the
  finding by default, but the count is always visible so the reviewer knows evidence exists
  (`ExecutionDetailPage.jsx`).
- **"No fallback" discipline**: citation links only render `if (pageRefs && pageRefs.length > 0)` —
  there's an explicit code comment "*No fallback — only show citations when evidence.page_references
  exists*." No citation is fabricated or approximated when the real one isn't available. This is
  exactly this project's own FR-002/SC-002 discipline (000-synthetic-fixture-generation), independently
  arrived at in production.
- **Discrepancy table, not just per-field citations**: a dedicated "Discrepancies" section shows
  Field / XML Value / PDF Value / Page side-by-side when doc and system disagree — the reconciliation
  story made visible, not just implied.
- **`InspectSources.tsx`'s pre-flight alignment matrix** (mortgage-qa_qc-tool): before checks even
  run, a 3-column table (Doc / MISMO / LOS) with a pulsing amber dot per misaligned row and a static
  green dot per aligned row. This is a genuinely nice "sanity check before you trust the run" screen
  that loopinhuman.com doesn't have an equivalent of — worth keeping from the AI-Studio side.

**What to change for `-prod`:**
- Citation dedup logic (spec 004) is currently ~implicit in how the frontend groups by document
  title string-matching — worth formalizing as a first-class property on `DocCitation` (e.g. a
  `logical_document_key` derived at extraction time from `{doc_type, borrower}`) rather than
  re-deriving it client-side from title strings each render. Cleaner and matches this project's
  "citation is data, not UI-inferred" bias.
- Both demos only show citations for **document**-sourced values. Neither demo has a UI pattern for
  citing a genuinely **system**-sourced value (e.g. an FHA-case-number system-of-record lookup) —
  this project's own spec `000-synthetic-fixture-generation` (US4) already had to invent that
  "lightweight provenance note, not a fabricated page citation" pattern fresh, because neither
  reference demo solved it. Don't go looking for prior art here — there isn't any; design it new.

---

## 2. DAG/route visualization — powerful, and yes, too much for the SME persona as-is

Your instinct is confirmed by reading `NodeDetailPanel.jsx` directly: clicking a node in the
Route Builder's canvas surfaces the block's **raw system prompt** (rendered as a monospace text box),
**model name** and **max_tokens**, the **tool list**, typed **input/output** ports, and a **merge
strategy** dropdown (`collect`/`merge`) for fan-in joints. This is IT/engineer-grade configuration
surface — appropriate for the person who wrote the block, wrong for the non-technical SME persona
this project's Principle VI ("configurable by non-technical users") targets.

**What's good and worth keeping (the visualization, not the editing surface):**
- **Execution-time DAG as a status board**: `ExecutionDAG.jsx` colors nodes/edges by live status
  (`COMPLETED` green, `RUNNING` blue-pulsing, `FAILED` red; edges tinted by the upstream node's
  status) — this is exactly the "live execution monitor" pattern you said to carry forward. As a
  **read-only, post-hoc "here's what ran and in what order" view**, a DAG is genuinely the right
  shape — Routes are literally DAGs (fan-out/fan-in), and a linear list would hide that structure.
  Fan-out/fan-in nodes render as distinct joint shapes, which is a nice, legible convention.
  `BlockNode.jsx`'s category-color-coding (income/assets/credit/property/compliance/etc.) gives an
  at-a-glance sense of what kind of check each node is without reading labels.
- **The DAG as a topology reference in Execution Detail** (a "topology" tab alongside the flat
  results list, `ExecutionDetailPage.jsx`) — letting an ops reviewer toggle between "just the
  findings" and "show me the graph" is a good affordance, not a forced default.

**What to change for `-prod`:**
- **Split the two jobs the DAG currently does into two different surfaces at two different altitudes.**
  Today one component (`DAGCanvas`/`NodeDetailPanel`) does both **authoring** (an SME or engineer
  wires the graph, edits prompts/params) and **observing** (an ops reviewer watches a run). Per this
  project's own CLAUDE.md ("Perfect the three surfaces: Apply / Author / Output"), these should be
  different screens with different information density:
  - **Author** (the SME-facing Routes→Blocks→Checks workbench, `example/`'s `RulesWorkbench`
    design language): keep the graph shape if you want the DAG's structural clarity, but hide
    system-prompt/model/token internals behind a clearly-labeled "Advanced" disclosure a non-SME
    would never need to open. The SME's unit of work is a **check** (field, threshold, comparison),
    not a system prompt.
  - **Apply/Output** (execution monitoring, ops/reviewer-facing): the live-colored DAG is genuinely
    good here and needs no dumbing-down — this audience already understands "this step ran, this one
    is running, this one failed."
- Don't inherit loopinhuman.com's implicit assumption that one canvas serves both audiences — that's
  the root cause of "too much for non-technical folks," not the DAG shape itself.

---

## 3. Confidence scores — the real finding: **neither demo actually solved this**

This is worth stating plainly rather than papering over: I looked for a UI pattern to reuse and found
none worth reusing.

- **`examples/mortgage-qa_qc-tool` (the AI-Studio prototype):** `grep confidence` across
  `types.ts`/`engine.ts`/every component returns **zero matches**. Confidence isn't modeled at all in
  this prototype — despite this project's own `p0/qc_engine/model.py` already treating
  `doc_confidence` as a first-class field with a real confidence gate (a PASS on sub-floor confidence
  downgrades to `NEEDS_REVIEW`, per the constitution's Confidence gate). The design-language reference
  this project is meant to extend has no answer for how to *show* the thing the engine already
  computes.
- **loopinhuman.com (`agent-gateway/src/extraction_handler.py`):** confidence exists, but only as a
  **backend field-consolidation tiebreaker** ("higher confidence wins" when merging duplicate
  extractions) — and its values are near-universally **hardcoded fallback defaults**, not calibrated
  signals: `confidence.setdefault("confidence", 0.8)`, `"confidence": 0.9` (used whenever a field
  lacks its own citation-embedded score), `"confidence": 0.5` as the last-resort default, `"confidence":
  0.95` for a different code path. This is the exact anti-pattern this project's own `research.md`
  (000-synthetic-fixture-generation, decision #6) already flagged from bundle-level analysis — now
  confirmed at the source-code level, not inferred. **It is never surfaced to the reviewer at all** —
  I read through the entire exception-rendering path in `ExecutionDetailPage.jsx` and found no
  confidence badge, percentage, or indicator anywhere in the findings UI.

**What this means for `-prod`:** don't search either demo for "how should confidence look in the UI" —
there's no prior art to adapt, only an anti-pattern to avoid (hardcoded fallback values masquerading as
calibrated confidence). This needs fresh design, grounded in what the engine actually knows:
- Since `doc_confidence` already gates PASS→NEEDS_REVIEW in the engine, the Output/Exception-review
  surface needs *some* visible signal for "this was auto-cleared with high confidence" vs "this is
  in front of you because confidence was borderline" — otherwise a reviewer can't tell the difference
  between "the engine is certain" and "the engine wasn't sure and this is a courtesy flag." A simple
  visual affordance (not a hardcoded default): show the confidence value only when it's the *reason*
  a finding needed a human, not as decoration on every row.
- Whatever you design, hold it to research.md decision #6's standard: a confidence value is only ever
  shown if it's honestly method-derived — never a flat default dressed up as a number.

---

## 4. Progressive disclosure / information density — the most mature, least glamorous lesson

Specs `004-citation-dedup` and `005-review-center-ux` exist specifically because the first version of
this UI was too dense for a real reviewer working a real loan (260+ documents, 77+ extraction sources).
The fixes are worth adopting as defaults from day one, not rediscovering the hard way:

- **Collapse by default, show counts**: the Extraction Sources section defaults to collapsed with a
  count + discrepancy badge in the header ("Extraction Sources (77 documents) — 4 discrepancies");
  expand on click. Same pattern for citation lists ("Show N citations").
- **Group findings by severity, collapsed per group**: Critical → Major → Minor → Passed, in that
  order, each sub-group collapsed by default showing only a label + count. A reviewer scans severities
  top-to-bottom instead of hunting through a flat list.
- **Show Passed, not just exceptions** (spec 005 US3): a QC section with zero exceptions still shows
  a "Passed" group listing what was verified — explicitly framed as building reviewer trust and
  supporting the audit trail, not just exception-hunting. This is directly relevant to this project's
  own auto-clear framing (CLAUDE.md's ExceptionReview: "auto-clear the rest") — the auto-cleared set
  needs to be inspectable, not just implied by absence from the exception list.

**Carry forward as defaults**, not options to consider later — this project's Output surface will hit
the same document-count/finding-count scale (800+ checks) that forced these fixes in loopinhuman.com.

---

## 5. Honesty-in-the-UI patterns — small, easy to copy, easy to forget

- **`KPICard.jsx`'s "sim" badge**: any KPI card sourced from simulated/mock data carries a small
  amber "sim" badge next to its label. This is a one-line, cheap pattern with an outsized payoff: it
  keeps demo-mode metrics from being mistaken for real ones, in the same UI, without a separate
  demo-vs-prod build. Worth adopting verbatim for `-prod`'s dev/demo fixtures (including the
  document-derived synthetic fixtures from `000-synthetic-fixture-generation` itself — if those ever
  render in a UI, they should carry an equivalent "synthetic" badge per this project's own
  [[feedback_synthetic_vs_real_test_data]] discipline).
- **Human mitigation log trail** (`mortgage-qa_qc-tool`'s `ExceptionReview.tsx`): every resolved
  exception shows who cleared it, when, and their literal comment ("Cleared by: Gordon Chan (Auditor)
  on 06/20/2026"). Combined with typed mitigation actions (Overrule / Force-Align-LOS /
  Escalate) each requiring a mandatory audit-trail comment before submission — this is a strong,
  reusable "human judgment is itself an audited event" pattern, consistent with this project's
  determinism-and-audit thesis (a human override is exactly the kind of event that must be traceable
  too, not just the machine's verdicts).

---

## 6. The "compile, then run" verification gate — good visual grammar, currently 100% theater

`RuleCompilerVisualizer.tsx` (mortgage-qa_qc-tool) is a terminal-styled compile log with a progress
bar, color-coded log lines (`[PARSE]`, `[AST]`, `[COMPILER]`, `[HARDEN]`, `[SUCCESS]`), and a green
"Deterministic Audit Complete" success state. It's a genuinely good visual grammar for *this project's
own* non-negotiable #1 ("compile, then run" — the SME validates the compiled artifact before it runs).

**The catch, worth being direct about**: every log line is a hardcoded string on a `setTimeout`/
`setInterval` — there is no real compiler behind it. Lines like *"Bypassing O(n) security gaps"* or
*"0 AST syntax flaws found"* are flavor text, not real compiler output. This is fine as a prototype
placeholder but must not ship into `-prod` as-is — the equivalent screen needs to show the **real**
`002b` compiler's actual output: real referential-integrity checks, the real SHA-256 ruleset hash,
real edit-distance-from-LLM-draft signal, wired to `p0/qc_engine/ruleset.py`'s actual
`CompiledRuleset` — not a themed loading animation. Keep the visual pacing/log-line aesthetic
(it's good storytelling for a non-technical SME watching their config get "locked in"); replace 100%
of the log content with real compiler output.

---

## 7. Ops/cost dashboard — good shape, wrong metric to optimize

loopinhuman.com's Terminal/Ops Analyst surface (`KPICard.jsx`, `TrendCharts.jsx`,
`PerformanceTables.jsx`, sparklines, cost/latency/token breakdowns "By Model"/"By Route"/"By Method")
is the "cost/latency dashboard" you said to carry forward, and structurally it's a good ops surface —
sparkline KPI cards, drill-down tables, an on-demand AI-generated briefing.

**What to change conceptually, not just visually**: loopinhuman.com's dashboard exists because its
architecture runs an LLM on every step of every loan — cost/latency tracking is there to manage an
inherent, ongoing spend. This project's constitution flips that: cost visibility exists to **prove
the primary path costs ~$0** (the compiled engine, no LLM at runtime) and to make the **rare, gated
exception** (an LLM fallback for a field pattern-matching couldn't resolve) visible precisely because
it's supposed to be rare. Reuse the visual components (KPI cards, sparklines, by-model/by-route
tables), but point them at this project's own Cost Transparency Requirement metric: tokens/cost per
decision **and the deterministic-resolution rate** (target ≥25% resolved without any LLM call,
ideally near-100% on the compiled primary path) — a dashboard that would look *wrong* to Olav's
architecture (near-zero LLM spend) is exactly the success state for this one.

---

## Bottom line

Both demos are strong, real prior art for **interaction patterns**, not architecture (architecture
prior art is `PRIOR-ART-OLAV-MORTGAGE-QC.md`'s job). Citation evidence and progressive-disclosure/
severity-grouping are mature enough to port with only light adaptation. The live execution DAG,
trigger console, and cost dashboard are good shapes that need re-pointing at a compiled-deterministic
backend instead of a live-agent one. Confidence-score UX and system-sourced-value citations are
**not** solved by either demo — design those fresh, and hold them to this project's own honesty
standards (research.md decision #6, FR-002) rather than assuming a reference exists. The DAG-as-editor
surface is the one pattern to actively *not* copy for the SME-facing Author screen — split it from
the DAG-as-monitor surface, which is worth keeping as-is.

**Related**: [[project_mortgage_qc_prod]] (memory), `PRIOR-ART-OLAV-MORTGAGE-QC.md` (architecture/reuse
audit), `THESIS.md` (non-negotiables these lessons are checked against).
