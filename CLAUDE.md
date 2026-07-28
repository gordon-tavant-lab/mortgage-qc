# Mortgage QA/QC Tool — Production Build

> A configurable, **deterministic** post-closing QA/QC engine + authoring workbench.
> Lets a non-technical mortgage SME wire up 800+ closed-loan checks as **routes → blocks → checks**,
> run them on demand against **three data sources**, auto-clear what the machine can decide, and
> surface only the true human-judgment exceptions.
>
> **This is a seed to productize, not a one-off prototype.** Full strategy: `output/THESIS.md` (+ one-pager).

---

## What This Is

A closed, funded loan file comes back from the title company as a blob of hundreds of signed, dated PDFs — the **source of truth**. Someone must QC it against the loan data the lender holds. Today that is manual, slow, and judgment-heavy.

The tool's job: **apply the right checks to the right loan, correctly, every time** — auto-clearing the obvious and isolating only what genuinely needs a human. "I'm done with this loan. Next one, next one, next one."

`examples/mortgage-qa_qc-tool` is the AI Studio React prototype that won the client's imagination and **defines the front-end design language**. This `-prod` build hardens that seed toward a real product. `examples/mortgage-qc` is a second reference demo (live at `mortgage-qc.loopinhuman.com`) — see `output/DEMO-UX-LESSONS.md` for what to take from each.

---

## The Non-Negotiables (do not stray from these)

These come straight from the strategy meeting. Treat them as invariants — challenge code that violates them.

### 1 · Determinism above all (the defining bet)
Same loan → **same pass/fail, every time.** No "the LLM may vary," no asterisks. This is what separates the product from Olav's LLM-at-runtime POC.
- **Design pattern: compile, then run.** The LLM works at *configuration time* — it interprets the SME's rule spreadsheet/intent and **generates an intermediate ruleset** (Drools/Groovy-style). The SME validates and signs off on that artifact *before* it runs. The engine then executes the **same compiled artifact** deterministically against every loan.
- On rule change: take it back through the pipeline → regenerate → re-validate → run. **The LLM never freelances at runtime.**
- **Two business drivers, not engineering taste:** (a) *Regulatory audit* — "if they don't understand how you calculated that number, you buy back the loan." (b) *Cost at scale* — per-run LLM inference on 10,000 files could cost $10K/run; compiling once eliminates per-run token cost.
- A runtime-LLM design is permitted **only if** it can prove identical results every time. Burden of proof is on that side; the compiled ruleset is the default.
- **Empirically refined (G3 bake-off, 2026-06-28 — `p0/experiment_g3/RESULTS.md`):** at temp=0 *both* Haiku 4.5 and Sonnet 4.6 were byte-identical across runs, so "the LLM may vary" is **not** the discriminator. The real one is **correctness on boundary math**: Haiku reproducibly cleared a 98%-LTV loan (a buyback); Sonnet caught it. You can't know which model-behavior you have in advance, or show a regulator the derivation — so the load-bearing reasons to compile are now **auditability + guaranteed-correct math**. Cost still favors the engine decisively: the "$10K/run" figure was ~$27–$70 on tiny synthetic payloads, but **real full-extraction payloads (10–50× tokens) push a strong model to ~$700–$3,500/run, per run**, while the engine is **$0 at any scale**. Hold runtime-LLM as a live option only for the *no-deterministic-algorithm* cases (the autonomy story), not the deterministic core.
- **Grounding adds context, never new rule content (hardened 2026-07-22, after a rule-fidelity audit — `output/RULE-FIDELITY-AUDIT-2026-07-22.md`):** research (web lookups, a signed knowledge-base corpus, an agent's own general knowledge) may be used *during compilation* to **interpret or cite** a condition the source AMQ row already states — resolving ambiguous phrasing, attaching the real regulation a defect traces to. It must **never** be the origin of a threshold, date, percentage, or condition that isn't itself present in the source row. A compiled check with a plausible-sounding but untraceable number (e.g. "5-mile" comp-distance, a site-value percentage) is indistinguishable from a correct one until an SME manually re-derives it — which defeats the entire audit-trail premise of Non-Negotiable #1. The compiler's own system prompt (`p0/qc_engine/compiler/compile_llm.py`) and KB-authoring discipline (`p0/qc_engine/compiler/knowledge_base.py`) now say this explicitly: **an honest "UNSPECIFIED, needs SME input" beats a confident invented number, every time.**

### 2 · Build the core, assume the periphery (scope discipline)
**Do not boil the ocean.** Attack the core; assume the edges are solved.
| Area | Decision |
|---|---|
| Rules engine + config workbench + result set | ✅ **This is the product. Build this.** |
| Document data extraction | ❌ Do not build. Upstream contract with the **Touchless** team returns extracted fields **+ document classification**. |
| LOS integration | ❌ Do not build. **Reuse the existing connector.** |

Extraction's data contract may need to widen over time (more data elements to review) — track that as an **interface**, not a build.

### 3 · Three data sources, reconciled (not checked in isolation)
| # | Source | Origin |
|---|---|---|
| 1 | **Closed-loan PDFs** | Title company, post-closing. **Source of truth.** Touchless unpacks → classifies → extracts. |
| 2 | **MISMO 3.4 XML** | Title company *or* LOS export |
| 3 | **LOS export (3.4)** | Loan Origination System, via connector |

The value is **cross-comparing** all three — a check asserts not just "is this value valid?" but "do all three sources tell the same story?" ⚠️ Test data must keep the document path and system path **genuinely independent** — LOS-only data makes the document-vs-system comparison trivially identical and untestable.

### 4 · Configurable by non-technical users (the philosophy that won the room)
**Routes → Blocks → Checks**, wired by hand. Point a route at a target set and **run on demand.** The buyer is a **BA/SME who configures and runs this without going back to IT** — simple or complex, their call. Perfect the **three surfaces**: **Apply** (deterministic engine), **Author** (no-IT config), **Output** (human clears exceptions fast; auto-clear the rest).

---

## Standing Gates (required before sign-off)

Every one of these must be re-run and pass before signing off any newly compiled ruleset or
demo/production run — not optional, not "usually":
- `p0/fixtures/from_docs/verify_against_defects.py` — 25/25 known-defect detection, re-confirmed after
  every fixture regeneration.
- **Field & Precondition Coverage Gate** (added 2026-07-28, spec `015-loan-data-capture-and-gating-fix`
  Phase 0 — `p0/compile_runs/run_016_coverage_gate/build_and_run.py`, same standing as the 25/25 gate
  above): this project has two systems built at different times and never reconciled against each
  other — document extraction (`doc_patterns/*.json` + `field_catalog.json`) and the precondition-
  ontology pipeline (`p0/ontology_extraction/`, spec `002f`). A gap in the second category (a
  contextual/gating fact a check silently depends on, not the field it's checking) is invisible to
  every other review mechanism this project runs, and was only found once, by accident, from a
  screenshot (spec 015's background). This gate makes that discovery repeatable: for every field
  `ontology_extraction`'s real Layer-0 output depends on, every field the currently-vetted ruleset
  references, and a small curated FIBO alignment list (see below), it checks whether a catalog entry
  exists, whether anything actually extracts or derives it, and whether it's ever populated for a real
  loan — reporting the full list of failures, not a sample. Re-run it (`python3 p0/compile_runs/
  run_016_coverage_gate/build_and_run.py`) any time a ruleset is recompiled, a new precondition
  dimension is added, or before a demo run — its own SC-006 self-check fails loudly (non-zero exit)
  if it stops reproducing known gaps, so a silent regression in the gate itself won't go unnoticed.

---

## Front-End Design (from `examples/`)

The prototype establishes the look and the core screens. Preserve this design language.

**Before any front-end/UX work (new screens, authoring surfaces, execution monitors, review queues),
read `output/DEMO-UX-LESSONS.md` first.** It's a source-level review of both reference demos —
`examples/mortgage-qa_qc-tool` (this design language) and `examples/mortgage-qc` (the live
`mortgage-qc.loopinhuman.com` build, Gordon's own forked/extended version of Olav's original) — for
what to reuse vs. avoid: citation-evidence UX (mature, port near-verbatim), DAG visualization (good
as a read-only execution monitor, wrong as the SME-authoring surface — split the two), confidence
scores (unsolved by both demos — design fresh, don't search either for prior art), the compile-log
visualizer (good grammar, currently 100% themed/fake — must wire to real `002b` compiler output), and
the cost/latency dashboard (reusable shape, re-point at this project's own ≥25%-deterministic-
resolution metric, not Olav's ongoing-LLM-spend framing). See also `output/PRIOR-ART-OLAV-MORTGAGE-QC.md`
for the backend/architecture reuse audit (deploy infra, `ConfirmationCard`, session-scoped WebSocket
routing) — that doc and `DEMO-UX-LESSONS.md` are companions, not overlapping.

**Also invoke the design skill family — not just general coding tools — whenever doing frontend,
product-design, or UX/UI work on this project:**
- `frontend-design` and `g-create-design --mode frontend` (Gordon OS's own skill, already wired into
  `/g-dev-build`'s Phase 6 IMPLEMENT for any `has_ui` build per that skill's Dynamic Agent Roster) —
  for building or restyling any screen.
- The `design:*` family, matched to the specific concern: `design:design-system` (component/token
  consistency against the Stack/tokens below), `design:design-critique` (review a new screen before
  calling it done), `design:accessibility-review` (before shipping any reviewer-facing queue, form,
  or citation viewer), `design:user-research` / `design:research-synthesis` (before designing a new
  authoring/review surface — confirm the SME's or reviewer's actual mental model, don't assume it),
  `design:ux-copy` (reviewer-facing microcopy — exception messages, empty states, confirmations),
  `design:design-handoff` (before treating a design as implementation-ready).
- `canvas-design` for static graphics/diagrams (not this app's own live screens).
- **No dedicated frontend/UX/product-design *agent* persona exists in this workspace's roster today**
  (available agents: `architect`, `implementer`, `docs`, `tester`, `reviewer`, `product-manager`,
  etc.) — `product-manager` is the closest agent-level counterpart for product-design concerns
  (problem framing, prioritization, user stories), but actual UI/UX/visual work routes through the
  skills above, invoked explicitly, not assumed to run by default. If a dedicated design agent is
  ever added to the roster, update this instruction to include it.

**Stack:** React 19 · Vite 6 · TypeScript · Tailwind CSS v4 (`@theme` tokens) · `motion` · `lucide-react`. (`@google/genai` + express present from the AI Studio scaffold.)

**Design tokens** (`src/index.css`): fonts — Inter (`font-sans`), Space Grotesk (`font-display`), JetBrains Mono (`font-mono`); slate-50 canvas, blue-600 accent, dark slate-900 chrome.

**Screens / components:**
- `LoanQueue` — pipeline grid; assign route per loan; statuses: Pending · Auto-Cleared · Exception · Resolved.
- `RulesWorkbench` — the SME authoring surface (routes/blocks/checks).
- `InspectSources` — three-point source alignment (DOC vs LOS vs MISMO) before running.
- `RuleCompilerVisualizer` — the "compile, then run" verification gate (deterministic ruleset generated *before* evaluation).
- `ExceptionReview` — human mitigation queue; mitigation types: UNRESOLVED · OVERRIDDEN · ESCALATED · SYSTEM_CORRECTED; "Clear & Next Loan" flow.
- `PdfViewerModal` — citation viewer (doc name + page + highlighted segment) — every doc-sourced value is traceable.

**Core types** (`src/types.ts`): `Check` / `Block` / `Route`, `Loan` + `LoanDataSources` (`documentExtracted` / `losExport` / `mismoXml`), `CheckResult` (with `comparisonValues` + `docCitation`), `AuditRun` (`compiledRulesetSnippet`, auto-cleared/exception counts — the audit trail). The deterministic check logic lives in `src/lib/engine.ts` (`executeCheck`).

---

## Working Conventions

- **`output/` is the deliverables folder** — THESIS, one-pager, PDFs, PORTFOLIO live there. AI-generated artifacts go here, not loose at root.
- **`docs/`** holds source material — `transcript.md` + `summary.md` (the strategy meeting). Ground decisions in these.
- **`examples/mortgage-qa_qc-tool`** is the reference prototype. When building the prod app, match its design language and the routes→blocks→checks model; harden the engine and the data contracts. **`examples/mortgage-qc`** is a second reference demo (the live `mortgage-qc.loopinhuman.com` build) — see `output/DEMO-UX-LESSONS.md` before drawing on either.
- The thesis is the contract. Before a non-trivial change, check it against the four non-negotiables above; if it conflicts, surface the tension rather than silently diverging.
- **Eval is foundational** (Blocker 2): the tool is only as trustworthy as its ground truth. Any rules work needs labeled, expert-validated loans with *known* outcomes to test against — and independent doc/system sources (see #3).

---

## Known Blockers (raised, with sanctioned mitigations)

1. **Extraction accuracy** poisons QC → don't rebuild; lean on Touchless / Kayla's Cloud-processed files.
2. **No labeled test data** (the eval gap) → Kayla provides expert-validated loans with known outcomes *and* validates the 800 check interpretations.
3. **Rule-to-program mapping unknown** (which of the 800 fire for which product?) → for now assume all rules apply; gate by product/program later. Don't block the build on this.

---

## Run the Example Prototype

```bash
cd examples/mortgage-qa_qc-tool
npm install
npm run dev      # vite on :3000
npm run lint     # tsc --noEmit
```

---

## Where This Fits

Gordon prototypes fast → validates with Kayla/client → hands the validated prototype to **Monish's team** for industrial build-out (observability, auditability, security, guardrails) on the Touchless platform. This QA/QC tool is the canonical example of that flywheel — and the **determinism** story for the HousingWire AI Summit (theory → live tool → proof). The October Mortgage AI keynote is the separate *autonomy* story. Nuance: agentic AI belongs **only** where no deterministic algorithm exists; everywhere an algorithm exists, demand utter determinism — the regulator audits the math.

## Active Technologies
- Python 3.9-compatible (project-wide constraint). + `boto3` + Bedrock (reused pattern from `p0/experiment_g3/llm_arm.py`), (main)
- Flat files only (sampled rows, drafts, SME review doc, finding) — no database. (main)
- Python 3.9-compatible (project-wide constraint). + None new — stdlib `json` + `hashlib` only, reusing (main)
- A single JSON file (`p0/qc_engine/field_catalog.json`), co-located with engine code. (main)
- No new storage — a data-model generalization inside `qc_engine`; inbound contracts are (main)
- Python 3.9-compatible (project-wide constraint). + `pdftotext` (poppler-utils, already available in this environment) invoked (000-synthetic-fixture-generation)
- Flat files only — the source PDFs/XML already in `demo/syn/`, and the generated (000-synthetic-fixture-generation)

## Recent Changes
- main: Added Python 3.9-compatible (project-wide constraint). + `boto3` + Bedrock (reused pattern from `p0/experiment_g3/llm_arm.py`),
