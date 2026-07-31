# Representing an AMQ Rule as a Check in the Route → Block → Check UI

> **Purpose:** the field-level contract for turning one compiled AMQ rule into one
> `Check` the SME sees, configures, and reviews results from.
> **Companion docs:** `SHACL-UI-COMPATIBILITY-ANALYSIS.md` (⚠️ **superseded** — see its header),
> `ACTION-ITEMS-2026-07-30.md` (open frontend work), `../AMQ-PROGRAM-TAXONOMY.md`
> (program gating — **read before implementing applicability**).

> ## Amended 2026-07-30 by `specs/019-workbook-first-rule-authoring/spec.md`
>
> **This document's field-level contract is sound and remains authoritative.** Four amendments follow
> from spec 019's research. Read them before implementing §3, §4, or §7.
>
> **1 · The flow in §1 is inverted.** It reads
> `AMQ row → compiled rule → SHACL NodeShape → Check (UI)`, implying the UI reads `.ttl`. The
> established direction is the reverse: **workbook → catalog → UI authoring → SHACL**. The `.ttl` is a
> *compiled output* the UI never reads. §1's other claims (one `NodeShape` = one `Check`; the Block is
> the AMQ Question Category Name; "do not invent a Check that has no NodeShape") all still hold —
> the UI remains a view over a compiled artifact, never a second source of truth.
>
> **2 · §7 item 1 is wrong: `NEEDS_REVIEW` does exist in the engine.** It asserts *"`NEEDS_REVIEW` does
> not exist in the engine. Every check is binary today."* In the SHACL engine it is real and produced:
> `src/shacl_pilot/run_audit.py:166` resolves `status = "NEEDS_REVIEW" if sev == SH.Warning else
> "FAIL"`, and **5 shapes carry `sh:severity sh:Warning`** (vs 19 `sh:Violation`). It is also emitted
> for document-presence checks (`run_audit.py:202`) and appears in every per-loan report in
> `full_5loan_audit_latest.md` (counts 1 / 9 / 5 / 12 / 7 across the five loans). The *underlying*
> concern is still valid — 166 AMQ rules use judgment language that cannot be pass/fail, and spec 019
> routes those to a `NEEDS_SME` authorability verdict so they are never offered as a binary gate.
>
> **3 · §4 lists five verdicts; the reports use a sixth.** `run_full_ruleset_audit.py` emits
> `FAIL` / `PASS` / `NOT_APPLICABLE` / `NO_DATA` / `NOT_COMPILED`, but the audit reports also carry
> **`NOT_EVALUATED`** (e.g. "PASS: 26 | FAIL: 1 | NEEDS_REVIEW: 1 | NOT_EVALUATED: 1,324"). Any results
> header claiming to show "all five counts" must reconcile against the vocabulary the runner actually
> produces, or it reintroduces the false-clean bug at the UI layer in a new place.
>
> **4 · §3's `preconditions` / `program` / `loanType` fields have a real, machine-readable source —
> and it resolves Known Blocker 3.** The AMQ workbook's **`Question Criteria`** column (column 8) holds
> SQL applicability gates, populated on **5,201 of 5,520** post-close rows (94%), with only **80
> distinct predicates** over a closed 8-field vocabulary (`QC_Policy` 5,064 · `PropertyType` 372 ·
> `Underwriting_Type` 247 · `LoanType` 97 · `LoanPurposeType` 85 · `Occupancy` 52 ·
> `OriginalLTVRatioPercent` 11 · `AddressState` 3):
>
> ```sql
> WHERE Loans.QC_Policy = 'FHA' AND Loans.Underwriting_Type = 'Manually Underwritten'
> WHERE Loans.QC_Policy = 'Freddie Mac' AND Loans.PropertyType = 'Condominium'
> ```
>
> `src/shacl_pilot/amq_compiler.py` reads nine columns (lines 289-322) and **this is not among them**,
> though the column *is* present in the CSV it reads (column 8 of 14) — a dropped field, not a missing
> export. Because every gate traces to a workbook cell, using it satisfies the grounding rule in
> Non-Negotiable #1. This is also the data CLAUDE.md's **Known Blocker 3** ("rule-to-program mapping
> unknown… gate by product/program later") treats as unavailable.
>
> ### Storage — what this document does not cover
>
> It specifies the `Check` *shape* but not where authored rules live. Spec 019 defines three artifacts,
> and conflating any two is a design error:
>
> | # | Artifact | Written by | Read by | Role |
> |---|---|---|---|---|
> | 1 | `amq_catalog.json` (per-block split) | `workbook_ingest.py` | **the UI, at load** | Read-only catalog: 3,370 checks, 16 blocks, parsed gates, authorability verdicts |
> | 2 | `storage/rules/vN.json` | the SME, via Save/Export | `ruleset_to_shacl.py` | The SME's decisions — activations, edits, sign-off |
> | 3 | `src/shacl_pilot/blocks/*.ttl` | `ruleset_to_shacl.py` | the SHACL engine | Compiled build output — **never read by the UI** |
>
> `storage/rules/` is versioned `vN.json` like `storage/fact_vocabulary/v1..v8.json`, and is **distinct
> from `result/rules/`** (which holds compiled/signed *engine* rulesets). Note the frontend has no
> persistence today — `RoutesFlow.tsx:24-26` holds all editable state in `useState`, so a refresh
> destroys every edit.
>
> ### The scale constraint this contract should be read against
>
> The post-close workbook yields **3,370 defect checks** (5,520 rows → 4,546 deduped → −379 Discarded
> = 4,167 rules → −797 affirmative "Yes / Not Applicable" rows). Against that: **446**
> `field_catalog.json` entries and **67** `li:` predicates used by all 28 shapes. A check whose fields
> aren't extracted resolves `NO_DATA` forever — which is why spec 019 makes the authorability verdict
> the authoring pool's primary axis rather than category.

---

## 1 · The mapping in one line

```
AMQ workbook row  →  compiled rule (ruleset.json)  →  SHACL NodeShape (.ttl)  →  Check (UI)
```

One `sh:NodeShape` = one `Check`. The Block is the AMQ **Question Category Name**
(17 real categories). The Route is an SME-assembled set of Blocks.

**Do not invent a Check that has no NodeShape.** The UI is a view over the compiled
artifact, never a second source of truth — that is what makes the run auditable.

---

## 2 · What already exists vs. what must be added

The prototype's `Check` (`examples/mortgage-qa_qc-tool/src/types.ts`) is a good start but
is missing every field needed for traceability and honest verdicts:

```ts
// EXISTING — prototype
export interface Check {
  id: string;  name: string;  description: string;
  severity: Severity;                      // "CRITICAL" | "WARNING" | "INFO"
  sourceTypes: ("DOC" | "LOS" | "MISMO")[];
  isActive: boolean;
  formula: string;                         // human-readable
  category: string;
  compiledSnippet?: string;
}
```

Three structural problems:
1. **No citation.** A finding must point at the evidence — the document it came from.
   Nothing in the current `Check` carries that.
2. **`Severity` enum is wrong.** AMQ emits `Critical` / `Major` / `Minor`, not
   `CRITICAL` / `WARNING` / `INFO`.
3. **No applicability, no compile state.** The UI cannot distinguish "passed" from
   "never ran" — the exact false-clean bug that made a real audit report 0 defects.

**Scope decision (Gordon, 2026-07-30): citation, not link-back.** The UI does not need to
navigate a reviewer back to the AMQ workbook row. What it needs is the **evidence
citation** — which document, and where in it, the finding came from. So
`exceptionCode` / `severity` / `aor` stay (they are the rule's identity and are shown as
text), but the UI is not required to deep-link into the source workbook, and
`sourceRows` is informational only — no navigation affordance is owed to it.

---

## 3 · The target `Check` shape

```ts
export type AmqSeverity = "Critical" | "Major" | "Minor";

export type CompileState =
  | "COMPILED"        // a NodeShape exists and is vetted
  | "NOT_COMPILED"    // AMQ row ingested, no executable logic yet  (2,442 of 4,166)
  | "DRAFT";          // authored, not yet signed off by the SME

export interface Check {
  // ── identity ────────────────────────────────────────────────
  id: string;                    // "CHK-AST-003"      caro:checkId
  shapeName: string;             // "RecurringPaymentNotInDtiShape"
  blockId: string;               // "assets"           caro:blockRef

  // ── rule identity (shown as text; no workbook deep-link needed) ──
  questionCode: string;          // "Asset"  | "O-FNM-15311"
  exceptionCode: string;         // "Asset-1"          caro:exceptionRef
  amqQuestionText: string;       // the category header, verbatim
  amqExceptionDescription: string; // THE RULE, verbatim — never paraphrase
  severity: AmqSeverity;
  aor: string;                   // "Underwriter" — accountable role
  sourceRows?: number[];         // informational only — no navigation owed

  // ── applicability (see ../AMQ-PROGRAM-TAXONOMY.md) ──────────
  program: "FNM" | "FRD" | "FHA" | "VA" | "RHS" | null;  // null = applies to ALL
  loanType: "CONVENTIONAL" | "GOVERNMENT" | "ALL";
  preconditions: string[];       // ["property_year_built < 1978"]

  // ── execution ───────────────────────────────────────────────
  compileState: CompileState;
  requiredFields: string[];      // parsed from the sh:select body
  sourceTypes: ("DOC" | "LOS" | "MISMO")[];
  compiledSnippet?: string;      // the SPARQL, shown read-only
  formula: string;               // plain-English restatement for the SME

  isActive: boolean;             // SME toggle
}
```

**`amqExceptionDescription` is the field that carries the rule.** `amqQuestionText` is a
vague header ("Were all self-employed requirements met?") shared by dozens of distinct
tests. Build the UI to show the Exception Description as the primary label and the
Question Text as the grouping caption — never the reverse.

### Field provenance

| Check field | Comes from |
|---|---|
| `id`, `blockId` | `caro:checkId`, `caro:blockRef` |
| `exceptionCode` | `caro:exceptionRef` |
| `amqQuestionText`, `amqExceptionDescription` | `caro:amqQuestionText`, `caro:amqExceptionDescription` |
| `severity`, `aor`, `sourceRows` | `ruleset.json` (`severity`, `aor`, `source_rows`) |
| `program`, `loanType` | `question_code` prefix — `O-<TOKEN>-` only |
| `requiredFields` | regex `li:([A-Za-z_][A-Za-z_0-9]*)` over `sh:select` |
| `compiledSnippet` | the `sh:select` string |

⚠ **Never populate `requiredFields` from `caro:citesFields`.** It is unreliable — 2 shapes
have empty values, 2 more name different fields than their own SPARQL, several omit the
program gate. Parse the SPARQL body.

---

## 4 · `CheckResult` — five verdicts, not three

The prototype's `CheckStatus = "PASS" | "FAIL" | "WARNING"` cannot express "did not run",
which is how a loan with 0 evaluated checks displayed as clean.

```ts
export type CheckStatus =
  | "FAIL"            // fired; defect found
  | "PASS"            // all required fields present; did not fire
  | "NOT_APPLICABLE"  // program/precondition excludes it        → collapsed by default
  | "NO_DATA"         // compiled, but a required field is missing → NEVER render as a pass
  | "NOT_COMPILED"    // no executable logic yet
  | "NEEDS_REVIEW";   // ⚠ NOT YET IMPLEMENTED IN THE ENGINE — see §7

export interface CheckResult {
  checkId: string;
  status: CheckStatus;
  message: string;              // Exception Description verbatim + specifics + citation
  // why it landed in this bucket — drives the UI explanation, no guessing
  reason?: {
    missingFields?: string[];   // NO_DATA
    excludedBy?: string;        // NOT_APPLICABLE: "FHA-only (loan is CONVENTIONAL)"
    blocker?: string;           // NOT_COMPILED: "sme_clarification"
  };
  comparisonValues: {
    doc?: any; los?: any; mismo?: any;
    citation?: Citation;         // see §4a — two kinds, rendered differently
  };
  mitigationStatus: MitigationType;
  mitigationComment?: string; mitigatedBy?: string; mitigatedAt?: string;
}
```

---

## 4a · Citation — the UI's primary traceability obligation

Per the scope decision in §2, **citation is what the UI owes a reviewer**, not workbook
navigation. Every document-sourced value carries one. The engine emits **two distinct
kinds**, and the UI must render them differently — conflating them is a correctness bug,
not a cosmetic one.

```ts
export type Citation =
  | {  // (a) POSITIVE — a document was found; this value came from it
      kind: "document";
      docName: string;      // "Loan_URLA - Continuation Sheet_1784635687082.pdf"
      documentId: string;   // "35622b20-78d4-4d93-af3a-0729fca2b074"
      snippet?: string;     // "documents[].documentType=URLA - Continuation Sheet"
      pageNum?: number;     // present ONLY where per-document extraction has run
    }
  | {  // (b) NEGATIVE — absence proven against a complete inventory
      kind: "inventory";
      docName: string;      // "Touchless document inventory (62 docs, complete)"
      snippet: string;      // "no documentType in ['FHA Form 442', 'Compliance Inspection Report']"
      searchedFor: string[];
    };
```

**Why the second kind exists.** Touchless's `documents[]` is a *complete* classified
inventory of the closing package, so a document type absent from it is **positive evidence
of absence**, not missing data. That is what lets document-presence checks reach a real
verdict without reading any PDF. The citation must show *what was searched for*, so a
reviewer can judge whether the search terms were right — this is the only defence against
a false "missing document" finding caused by a naming mismatch.

Rendering requirements:

- **Kind (a)** → clickable; opens the named document. Show `pageNum` when present.
- **Kind (b)** → **not clickable** (there is no document to open). Render as an evidence
  statement: *"Not found in the 62-document inventory. Searched for: FHA Form 442,
  Compliance Inspection Report."*
- `pageNum` is **optional and usually absent** — today's granularity is document-level
  (`docName` + `documentId`). Page numbers exist only where per-document extraction has
  run (**1 of 62 documents**). The viewer must open a named document with no page anchor
  and degrade gracefully; never render "p. 0" as if it were a real page.
- A `FAIL` with no citation of either kind is a defect in the check, not a display edge
  case. Surface it as such rather than showing an unattributed finding.

### Rendering rules (non-negotiable)

- `NO_DATA` and `NOT_COMPILED` must be **visually distinct from `PASS`** — never green,
  never folded into an "auto-cleared" count. A run that evaluates 47 of 4,166 rules must
  not read as "4,166 clean."
- Every results header shows all five counts. An `AuditRun` reporting only
  cleared/exception is the false-clean bug re-introduced at the UI layer.
- `NOT_APPLICABLE` is collapsed by default but always expandable with its `excludedBy`
  reason — an auditor will ask why a rule didn't run.

```ts
export interface AuditRun {
  runId: string; loanId: string; routeId: string; timestamp: string;
  rulesetSha256: string;         // which compiled artifact ran — required for audit
  compiledRulesetSnippet: string;
  counts: {                      // replaces autoClearedCount/exceptionCount
    total: number; fail: number; pass: number;
    notApplicable: number; noData: number; notCompiled: number;
  };
  results: CheckResult[];
}
```

---

## 5 · Block and Route

```ts
export interface Block {
  id: string;                    // "assets"
  name: string;                  // "Assets" — the AMQ Question Category Name
  amqCategory: string;           // authoritative key
  description: string;
  checks: Check[];
  isActive: boolean;
  counts: { compiled: number; notCompiled: number };  // honest coverage per block
}

export interface Route {
  id: string; name: string; description: string;
  blockIds: string[];
  appliesTo?: { loanType?: "CONVENTIONAL" | "GOVERNMENT"; program?: string };
  isCustom?: boolean;
}
```

The 17 real AMQ categories (Post-Closing) already give the SME a natural grouping — no
manual re-organization of 4,166 rules is required. Surface `counts` on every Block so the
SME sees that "Property - Appraisal" has 418 uncompiled rules rather than assuming full
coverage.

---

## 6 · Worked example — `CHK-AST-003`

```jsonc
{
  "id": "CHK-AST-003",
  "shapeName": "RecurringPaymentNotInDtiShape",
  "blockId": "assets",
  "questionCode": "Asset",
  "exceptionCode": "Asset-1",
  "amqQuestionText": "Were all recurring payments reflected on bank statements addressed?",
  "amqExceptionDescription": "All recurring payments that are reflected on bank statements were not addressed by the underwriter and included in DTI",
  "severity": "Critical",
  "aor": "Underwriter",
  "program": null,              // question code is "Asset" — not O-*, so applies to ALL
  "loanType": "ALL",
  "compileState": "COMPILED",
  "requiredFields": ["hasBankDebit","payee","debit_amount","recurring_count","hasUrlaLiability"],
  "sourceTypes": ["DOC","LOS"],
  "formula": "For each payee debited in >1 statement period, a liability for that payee must exist on the 1003.",
  "isActive": true
}
```

Result today, on loan 12607601215:

```jsonc
{ "checkId": "CHK-AST-003", "status": "NO_DATA",
  "reason": { "missingFields": ["hasBankDebit","payee","debit_amount","recurring_count"] },
  "message": "All recurring payments that are reflected on bank statements were not addressed by the underwriter and included in DTI [Asset-1]" }
```

Two bank statements are classified and present, but no transactions are extracted from
them — so the honest verdict is `NO_DATA`. Rendering this as a pass would be a lie.

---

## 7 · Open items the UI depends on

| # | Item | Impact |
|---|---|---|
| 1 | **`NEEDS_REVIEW` does not exist in the engine.** Every check is binary today; 166 AMQ rules use judgment language ("reasonable", "adequate") that cannot be pass/fail. | Build the verdict **before** the ExceptionReview queue, or the queue models a state the engine can't produce. |
| 2 | **Document-name crosswalk unbuilt.** AMQ names documents ("Occupancy Statement") that Touchless does not classify — 9 of 10 sampled had no counterpart. | Presence checks must return `NO_DATA` for unmapped documents, not `FAIL`. Without the crosswalk the UI shows false positives on Major findings. |
| 3 | **`caro:amqQuestionText` / `amqExceptionDescription` exist on only 2 shapes.** | Backfill during compilation, or the UI cannot show provenance for most checks. |
| 4 | Page-level citations exist for 1 of 62 documents. | Citation viewer must handle document-only citations. |

---

## 8 · Checklist before calling a Check UI-ready

- [ ] `amqExceptionDescription` shown verbatim — no paraphrase, no truncation in the detail view
- [ ] `exceptionCode` + `severity` + `aor` shown as text (no workbook deep-link required)
- [ ] **Every `FAIL` carries a citation**; `kind: "document"` is clickable, `kind: "inventory"` is not
- [ ] Inventory citations list what was searched for
- [ ] No "p. 0" rendered — omit the page when absent
- [ ] `severity` uses `Critical`/`Major`/`Minor`
- [ ] All five statuses rendered distinctly; `NO_DATA` is not green
- [ ] `NO_DATA` lists its `missingFields`
- [ ] `NOT_APPLICABLE` states `excludedBy`
- [ ] `compileState: NOT_COMPILED` visibly distinct from an active check
- [ ] Block header shows `compiled / notCompiled`
- [ ] `rulesetSha256` shown on the run — which artifact produced this result
- [ ] Citation opens the named document; tolerates a missing page number
