# How Rules Are Authored & Run in Olav's Demo (mortgage-qc.loopinhuman.com)

> **Source:** live extraction from `https://mortgage-qc.loopinhuman.com/#/workflow-designer`,
> 2026-07-29, via a headless Playwright script (the shared chrome-devtools MCP profile was
> locked by another concurrent session, so this ran as an independent Chromium instance).
> Password-gated with a single shared password; no data was modified — read-only navigation
> of the Routes / Blocks / Triggers / Tools tabs.
>
> **Raw artifacts:** every block's and route's YAML, extracted byte-for-byte from the app's own
> editor textareas, is checked in alongside this doc under
> [`olav-demo-yaml/`](./olav-demo-yaml/) (20 blocks + 5 routes, ~2.2MB total,
> `blocks_manifest.json` indexes block_id/category/char-count/source-file for each).
>
> **Why this matters:** Gordon had already hand-transcribed one route + one block into
> `docs/authoring-examples.md` (2026-06-30) and flagged the runtime-LLM problem from that single
> sample. This extraction confirms that finding holds **uniformly across all 20 blocks** (not just
> the one sampled), quantifies it, and adds the parts that single sample couldn't show — the tool/
> data-source layer, the routing/classification block, and the report-aggregation block's grading
> logic. Read `docs/authoring-examples.md` first; this is the full-population follow-up.

---

## 1. The three-tab authoring surface

The Workflow Designer (top nav, next to QC Operations / Review Center) has four tabs:

| Tab | What it is |
|---|---|
| **Routes** | A visual DAG editor. Browse existing routes or build a new one by dragging blocks from an "Add Block" palette onto a canvas. A "View YAML" button opens a read-only modal with the compiled `route_id` / `dag.nodes` / `dag.edges` YAML — this is generated from the visual graph, not hand-typed. |
| **Blocks** | A flat sidebar list of 20 blocks, grouped under ~17 category headers (these headers are visibly the same AMQ "Question Category Name" groupings referenced in this project's own `CLAUDE.md` §4). Selecting a block loads its **entire definition as one large, hand-editable YAML text box** (a plain `<textarea>`, not a structured form) plus a "Block Development Assistant" chat panel that can help compose/edit that YAML via natural language. |
| **Triggers** | An operational console for submitting a specific loan (by number, with an optional ULAD XML / PDF upload) against a chosen route, and a static inventory of 20 pre-loaded demo loans. Not an authoring surface. |
| **Tools** | A read-only catalog of the 35 backend data-access functions blocks can call (see §5). |

**Authoring model, in one sentence:** a "block" is authored as **one long free-text YAML document
whose core payload is an LLM system prompt** — there is no structured question/condition/threshold
builder underneath the text box. The chat assistant helps a human *write English*, not compose typed
rule objects. This is the opposite of this project's Non-Negotiable #4 (configurable by non-technical
users via routes → blocks → checks, no YAML).

---

## 2. Route layer: a DAG, and it *is* mechanical

Every route (5 sampled: Application Verification, Demo Route, Conventional Purchase Post-Closing QC,
FHA Purchase Post-Closing QC, Property and Appraisal QC — see `olav-demo-yaml/route_*.yaml`) follows
the same shape, and this part **is** a legitimate compiled/deterministic artifact:

```
loan-intake  →  fan_out_joint  →  [block, block, block, ... one per category]  →  fan_in_joint (merge_strategy: collect)  →  qc-report-generator
```

- `dag.nodes` — each node is either a `block:` reference (with `authority: auto`) or a
  `fan_out_joint` / `fan_in_joint` structural node.
- `dag.edges` — plain `from`/`to` pairs (fan-out edges list multiple targets in one entry).
- The "Conventional Purchase Post-Closing QC" route fans out to all 16 non-intake/non-reporting
  blocks in parallel, then merges and reports — exactly the pattern already captured in
  `docs/authoring-examples.md` Example 1, now confirmed byte-identical against the live app
  (`olav-demo-yaml/route_conventional-purchase-post-closing-qc.yaml`).
- Smaller routes (Application Verification, Property and Appraisal QC) run a single block after
  intake — no fan-out needed for a 1-block route.

**Takeaway for our compiler:** the *routing* layer (which blocks run, in what order, fanned out or
sequential) is genuinely graph data — closer to what "compile, then run" should look like. It is the
**block payload**, not the route DAG, where determinism breaks down.

---

## 3. Block layer: 19 of 20 blocks are a single runtime LLM call, not a compiled ruleset

This is the central finding. Every block was clicked in the live app and its `<textarea>` value was
read directly (with a change-detection retry loop — an earlier naive pass without that safeguard
silently captured 6 blocks' worth of *stale* content left over from the previously-selected block, a
DOM-timing bug worth flagging to anyone else who scrapes this app the same way).

### 3.1 Shape of a "check-catalog" block (17 of 20)

Blocks like `application-verification`, `certification-delivery`, `credit-liabilities-review`, etc.
embed a **question catalog directly in the LLM system prompt**, in this exact recurring grammar:

```yaml
Q<n>:
  CODE: <AMQ-style question code, e.g. O-FHA-15293>
  TEXT: <the question, verbatim from the source workbook>
  SIGNIFICANCE: Critical | Major | Minor
  AOR_PRIMARY: Underwriter | Processor | Closer | Loan Officer
  RESPONSES:
    - "<free-text answer choice>" -> EXCEPTION [<exception-code>] Significance: ... | AOR: ...
      Exception Detail: <description>
      CRITERIA: SELECT DISTINCT Loans.LoanID FROM Loans WHERE (Loans.QC_Policy = 'FHA')
    - "<another answer choice>" -> PASS
    - "Not Applicable" -> NOT_APPLICABLE
```

The block's `step_template.agent.system_prompt` instructs the LLM explicitly:

> *"If a question's criteria field contains a SQL-like filter, evaluate whether the current loan
> matches that criteria. If the loan does NOT match the criteria, mark that question as
> NOT_APPLICABLE."*

**That `CRITERIA:` line is never parsed or executed as SQL.** It is prose the LLM reads and applies
by judgment at inference time, at `temperature: 0.0–0.1`, alongside picking which of the multiple-
choice `RESPONSES` best matches the loan file. Across the 17 catalog-style blocks this happens
**~844 times** (question count per block, see table below) and the literal string `CRITERIA:` appears
**~5,000 times** in the combined YAML — i.e. ~5,000 individual runtime judgment calls of the exact
kind this project's Non-Negotiable #1 was hardened against after the G3 bake-off (Haiku
reproducibly cleared a 98%-LTV loan; Sonnet caught it — model-dependent correctness, not
model-dependent variance, is the risk).

### 3.2 Shape of a "narrative regulation" block

`fha-compliance-check` and `va-eligibility-check` are structurally different: instead of a
multiple-choice catalog, the prompt is a **hand-written narrative summary of the regulation itself**,
with real numeric thresholds inlined as prose for the LLM to apply at runtime, e.g. (from
`block_fha-compliance-check.yaml`):

```
FHA-002: MAXIMUM MORTGAGE CALCULATION
- LTV factor: 96.5% for credit score >= 580; 90% for credit score 500-579.
- Add financed UFMIP (1.75% of base loan amount).
FHA-005: FHA ANTI-FLIPPING REQUIREMENTS
- If seller owned property < 90 days: transaction is INELIGIBLE...
- If seller owned 91-180 days and resale price >= 100% over acquisition cost: second appraisal required.
```

There is no code anywhere computing `96.5% × min(purchase_price, appraised_value)` or comparing a
seller's days-of-ownership to 90/180/365 — the LLM is asked to do this arithmetic itself, from a
prose description, every run. This is a purer, more concentrated version of the exact risk our own
Non-Negotiable #1 names ("boundary math") — narrative-regulation blocks have *no* structured
question/response catalog to fall back on even as a compile target; the regulation text itself would
need to be re-authored into rules, not just re-formatted.

### 3.3 The one exception: `loan-intake` (routing/classification)

`loan-intake` (`block_loan-intake-classification.yaml`) is the only block using
`step_template.prefetch_tools` (a deterministic tool call, `get_loan_summary`, run before the agent
step) — but the classification and, more importantly, the **block-selection decision** are still
LLM-owned prose:

```
STEP 3 - DETERMINE REQUIRED BLOCKS
ALWAYS required: application-verification, income-verification, asset-verification, ...
CONDITIONAL blocks:
  - fha-compliance-check: if Loan Type = FHA
  - va-eligibility-check: if Loan Type = VA
  - epd-review: if loan is flagged for EPD review
```

This "ALWAYS / CONDITIONAL" list is a **deterministic lookup table by loan type** — a 3-line
`if loan_type == 'FHA': add fha-compliance-check` — but it is handed to the LLM as an instruction to
follow, re-decided from scratch on every loan, with no persisted mapping and no audit trail of which
branch fired or why. This is the same category of problem as the AMQ-category "which of the 800 rules
fire for which product" gap called out in this project's own Known Blocker #3 — Olav's demo answers
it with an LLM call per loan rather than a compiled program-to-check mapping.

### 3.4 The report/grading block: even pure count-thresholds are delegated to the LLM

`qc-report-generator` aggregates all upstream blocks' findings and decides the loan's final
disposition. Its grading rule is *literally* a deterministic boolean expression:

```
STEP 3 - DETERMINE OVERALL QC STATUS
- FAILED: Any Critical exception, OR 3+ Major exceptions, OR any compliance exception
  that creates legal/regulatory risk.
- ESCALATED: 1-2 Major exceptions that may be curable, OR any finding requiring
  management judgment.
- PASSED WITH FINDINGS: Minor exceptions only, no Critical or Major.
- PASSED: No exceptions of any significance.
```

`if critical_count > 0 or major_count >= 3: return "FAILED"` is a one-line, zero-ambiguity function.
Instead it is prose in a system prompt, evaluated by an LLM (`temperature: 0.0`) that also has to
correctly *count* the exceptions it just aggregated from up to 13 upstream JSON blobs before applying
the rule. This is the single cleanest example in the whole app of authored logic that has **no reason
to ever touch an LLM** — it should be the first thing compiled to real code in any port of this
model, and it is a useful concrete illustration for explaining Non-Negotiable #1 to a non-technical
stakeholder: *"even counting to 3 is being delegated to inference here."*

---

## 4. Full block inventory (verified against the live app, 2026-07-29)

| Category (sidebar header) | Block (display name) | `block_id` | Questions in catalog | model / temp / max_tokens | authority |
|---|---|---|---|---|---|
| APPLICATION-VERIFICATION | Application Verification | `application-verification` | 19 | sonnet / 0.1 / 8000 | auto |
| APPRAISAL-FORM-1033 | Appraisal Form 1033 Review | `appraisal-form-1033` | 31 | sonnet / 0.1 / 8000 | auto |
| ASSET-VERIFICATION | Asset Verification | `asset-verification` | 75 | sonnet / 0.1 / 12000 | auto |
| CERTIFICATION-DELIVERY | Certification, Endorsement, and Delivery Review | `certification-delivery` | 10 | sonnet / 0.1 / 8000 | auto |
| CLOSING-DOCUMENTS-REVIEW | Closing Documents Review | `closing-documents-review` | 34 | sonnet / 0.1 / 8000 | auto |
| COMPLIANCE-REVIEW | Compliance Review | `compliance-review` | 6 | sonnet / 0.1 / 8000 | auto |
| CREDIT-LIABILITIES-REVIEW | Credit and Liabilities Review | `credit-liabilities-review` | 84 | sonnet / 0.1 / 12000 | auto |
| DATA-VALIDATION-SERVICES | Data Validation Services Review | `data-validation-services` | 20 | sonnet / 0.1 / 8000 | auto |
| EPD-REVIEW | Early Payment Default Review | `epd-review` | 9 | sonnet / 0.1 / 8000 | auto |
| VERIFICATION | FHA Compliance Check | `fha-compliance-check` | 0 (narrative, §3.2) | sonnet / 0.0 / 12288 | **autonomous** |
| VERIFICATION | VA Eligibility Verification | `va-eligibility-check` | 0 (narrative, §3.2) | sonnet / 0.0 / 10240 | **autonomous** |
| INCOME-VERIFICATION | Income Verification | `income-verification` | 111 | sonnet / 0.1 / 16000 | auto |
| INFORMATION-INTEGRITY | Information Integrity Review | `information-integrity` | 16 | sonnet / 0.1 / 8000 | auto |
| INSURANCE-REVIEW | Insurance Review | `insurance-review` | 28 | sonnet / 0.1 / 8000 | auto |
| LOAN-DOCUMENTS-REVIEW | Loan Documents Review | `loan-documents-review` | 33 | sonnet / 0.1 / 8000 | auto |
| INTAKE | Loan Intake & Classification | `loan-intake` | 0 (routing, §3.3) | sonnet / 0.0 / 4096 | **autonomous** |
| PRODUCT-SPECIFIC-CHECK | Product-Specific Check | `product-specific-check` | 119 | sonnet / 0.1 / 16000 | auto |
| PROPERTY-APPRAISAL-REVIEW | Property and Appraisal Review | `property-appraisal-review` | 147 | sonnet / 0.1 / 16000 | auto |
| REPORTING | QC Report Generator | `qc-report-generator` | 0 (aggregation, §3.4) | sonnet / 0.0 / 8000 | **autonomous** |
| UNDERWRITING-REVIEW | Underwriting Review | `underwriting-review` | 102 | sonnet / 0.1 / 16000 | auto |

**Total catalog questions across the 17 catalog-style blocks: 844.** (For comparison: this project's
own AMQ Post-Closing workbook has 5,520 rows / 944 checks across 17 categories — same order of
magnitude and the same category names, suggesting Olav's demo digested a similar or overlapping AMQ
source, just compiled into prompts instead of a rule engine.)

Every block uses `model: sonnet` — no block anywhere uses Haiku or a cheaper tier, and no block runs
at `temperature: 0` except the four structural/aggregation blocks (`fha-compliance-check`,
`va-eligibility-check`, `loan-intake`, `qc-report-generator`); the 17 catalog blocks run at `0.1`.

---

## 5. The tool / data-source layer (35 tools, 10 systems)

The **Tools** tab lists every function a block's agent step can call:

| System | Tool count | Example tools | Method |
|---|---|---|---|
| Loan Origination | 7 | `get_loan_application`, `get_loan_summary`, `get_borrower_data`, `get_aus_findings`, `get_conditions`, `update_qc_status`, `record_exception` | GET / POST / PUT |
| Document Vault | 5 | `get_document_list`, `get_document_data`, `get_income_documents`, `get_asset_documents`, `get_closing_documents` | GET |
| internal-s3 | 5 | `get_extracted_loan_data`, `get_extracted_citations`, `get_ulad_data`, `list_extracted_documents`, `get_document_extraction` | S3_READ |
| Appraisal Service | 3 | `get_appraisal`, `get_comparable_sales`, `get_cu_score` | GET |
| Compliance Engine | 3 | `get_atr_qm_data`, `get_trid_data`, `get_hmda_data` | GET |
| Credit Service | 3 | `get_credit_report`, `get_liabilities`, `get_credit_supplements` | GET |
| Employment Verification | 3 | `get_vvoe`, `get_tax_returns`, `get_employment_history` | GET |
| Investor Guidelines | 3 | `get_investor_requirements`, `get_va_eligibility`, `get_fha_case` | GET |
| Title & Insurance | 2 | `get_title_commitment`, `get_insurance_policies` | GET |
| Flood Determination | 1 | `get_flood_determination` | GET |

Notably, the `internal-s3` group (`get_extracted_loan_data`, `get_extracted_citations`,
`get_ulad_data`) is the closest analog in this demo to **this project's own Touchless extraction
contract** (Non-Negotiable #2) — a pre-extracted-fields-plus-citations interface a block can pull
from rather than parsing documents itself. Unlike our design, though, every block *chooses* which
tools to call and *interprets* the returned JSON itself at runtime — there's no fixed, pre-resolved
field catalog handed to the block up front the way our engine's `field_catalog.json` does.

---

## 6. What this confirms / adds for our own rules-compilation design

1. **Confirms `docs/authoring-examples.md` at full scale, not just on one sample.** Every one of the
   17 catalog-style blocks follows the identical question/response/CRITERIA/significance/AOR grammar
   already flagged there — this isn't one unusual block, it's the uniform pattern across the entire
   demo.
2. **The `CRITERIA:` SQL-like strings are real evidence for our own compiler's condition language.**
   They're unexecuted decoration in Olav's demo, but the shape (`WHERE Loans.QC_Policy = 'FHA'`) is
   exactly a precondition our compiler should parse into an actual gate — reinforcing that this
   project's field/precondition-catalog approach (spec `002f`/`015`) is the right target, not a
   reinvention.
3. **Grading/aggregation logic (qc-report-generator) is the cleanest illustration yet of "this should
   never be an LLM call."** Worth pulling into any internal explainer deck alongside the G3 bake-off
   LTV example — it's a *0/1 boolean threshold*, not a judgment call, and it's still being inferred.
4. **Routing-by-loan-type (loan-intake) should be a compiled lookup table, not a re-decided-every-loan
   LLM classification.** The actual loan classification (type/purpose/occupancy/program from raw
   summary data) is a legitimate extraction/inference task; which *blocks* that classification
   activates should not be.
5. **The authoring surface is AI-assisted YAML editing, not a no-code SME workbench.** A chat panel
   that helps write/edit a giant text blob is a real, useful pattern (worth reusing for our own
   Block/Check editor's "explain this check" or "draft this check from a workbook row" flows) but it
   does **not** satisfy Non-Negotiable #4 on its own — the SME is still one Save-button click away
   from directly editing a 340KB YAML+prompt file by hand.
6. **The tool-call model is a plausible shape for a Touchless/LOS integration surface**, distinct from
   whether the block *logic* itself should run as a runtime agent. A compiled ruleset could still call
   out to equivalent typed data-fetch tools for the fields it needs — the risk this project avoids is
   letting the *decision* logic, not the *data-fetch*, live in an uncompiled prompt.

---

## Appendix: extraction method (for anyone re-running this)

- Playwright (Python) headless Chromium, independent of this machine's shared chrome-devtools-mcp
  profile (which was locked by another concurrent session at the time).
- Login: single password field, value `Tavant!`, submit via "Sign In".
- Blocks: Workflow Designer → **Blocks** tab → click each sidebar item → the block's full YAML lives
  in the *first* `<textarea>` on the page (`el.input_value()`, not `innerText` — it's a real form
  control, not styled text).
- **Known pitfall:** after clicking a new block, the previous block's textarea content can still be
  present for one or more render frames — a fixed `wait_for_timeout` is not reliable. The working
  extractor polls (up to ~6s) until the YAML's `block_id:` line actually changes from the
  previously-recorded value before saving it; six blocks in the first, naive pass captured a stale
  duplicate of the prior block's content and had to be re-run.
- Routes: Workflow Designer → **Routes** tab → **Browse** sub-tab (not **Edit** — the Edit sub-tab's
  sidebar is an "Add Block" palette for building a *new* route and shares block display names with
  the Browse sidebar, which silently added a block into a fresh unsaved route instead of opening the
  named saved route on the first attempt) → click a route → click "View YAML" → read the modal's
  `<textarea>`.
