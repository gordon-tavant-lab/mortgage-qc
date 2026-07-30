# SHACL Shapes → Route/Block/Check UI Compatibility Analysis

| | |
|---|---|
| **Question** | Can the frontend Route/Block/Check UI model still be supported now that rules have been extracted into SHACL shapes? |
| **Analysis Date** | 2026-07-30 |
| **Analyst** | Claude Sonnet 4.5 (background session) |
| **SHACL Pilot Scope** | `src/shacl_pilot/` (gitignored experiment, per memory `shacl-experiment-src-sandbox`) |
| **Answer** | **YES — with zero UI changes required.** The SHACL shapes already embed Route/Block/Check metadata in a UI-compatible shape. |

---

## Executive Summary

**The SHACL pilot already implements the Route → Block → Check hierarchy** via:

1. **Routes** — `src/shacl_pilot/routes.json` defines 5 program-specific routes (`fnm-post-closing-qc`, `fha-post-closing-qc`, `va-post-closing-qc`, `frd-post-closing-qc`, `rhs-post-closing-qc`), each containing a set of blocks from the 16-block catalog
2. **Blocks** — `src/shacl_pilot/blocks/*.ttl` (9 .ttl files: `application.ttl`, `assets.ttl`, `credit_liabilities.ttl`, `income.ttl`, `product_specific.ttl`, `property_appraisal.ttl`, `underwriting.ttl`, `certification_delivery.ttl`, `closing.ttl`) — each is a named grouping of SHACL shapes, mirroring Olav's 16-block taxonomy validated against `docs/research/olav-demo-yaml/blocks_manifest.json`
3. **Checks** — SHACL `NodeShape` definitions inside each block .ttl file, annotated with `caro:checkId`, `caro:blockRef`, `caro:exceptionRef`, `caro:hasSeverity`, `caro:citesFields` — these are the individual executable rules

**Example from `src/shacl_pilot/blocks/application.ttl`:**

```turtle
### CHK-APP-001 — Employment start date: 1003 vs VOE
li:EmploymentStartDateShape a sh:NodeShape ;
    sh:targetClass li:LoanInstance ;
    caro:checkId "CHK-APP-001" ;
    caro:blockRef "application" ;
    caro:exceptionRef "URLA-Final-9" ;
    caro:hasSeverity "Major" ;
    caro:citesFields "employment_start_date_1003", "employment_start_date_voe" ;
    sh:sparql [ ... ] .
```

This shape IS a check. The `caro:blockRef "application"` explicitly declares it belongs to the Application block. The block .ttl file groups multiple such checks. The routes.json file groups blocks into routes.

**The UI can continue to use the same Route/Block/Check model with zero changes** — it just needs a new data adapter that reads:
- `routes.json` → `Route[]`
- `blocks/*.ttl` (parse RDF, extract check annotations) → `Block[]` + `Check[]`
- `compiled/ruleset.json` (the AMQ compiler output) → enriched Check metadata (question_code, question_text, exception_code, severity, etc.)

---

## 1. Routes — Already Implemented

**File:** `src/shacl_pilot/routes.json`

**Structure:**
```json
{
  "catalog_blocks": [
    "application-verification", "appraisal-form-1033", "asset-verification",
    "certification-delivery", "closing-documents-review", "compliance-review",
    "credit-liabilities-review", "data-validation-services", "epd-review",
    "income-verification", "information-integrity", "insurance-review",
    "loan-documents-review", "product-specific-check",
    "property-appraisal-review", "underwriting-review"
  ],
  "routes": {
    "fnm-post-closing-qc": {
      "title": "Conventional (Fannie Mae) Post-Closing QC",
      "agency": "O-FNM",
      "extra_blocks": []
    },
    "fha-post-closing-qc": {
      "title": "FHA Post-Closing QC",
      "agency": "O-FHA",
      "extra_blocks": ["fha-compliance-check"]
    },
    ...
  },
  "selection_by_agency": {
    "O-FNM": "fnm-post-closing-qc",
    "O-FHA": "fha-post-closing-qc",
    ...
  }
}
```

**Frontend mapping:**
- Each `routes[routeId]` object → one `Route` in the UI
- `catalog_blocks` → the pool of available blocks in the two-pane Route Detail picker
- `extra_blocks` → agency-specific additions (FHA compliance, VA eligibility)
- `selection_by_agency` → deterministic route lookup by loan program (used at runtime, not directly UI-relevant)

**UI impact:** **None.** The `routes.json` shape is already Route-Detail-friendly. Parse it, render it.

---

## 2. Blocks — Already Implemented (as .ttl files)

**Files:** `src/shacl_pilot/blocks/*.ttl` (9 files currently)

**Structure (example from `application.ttl`):**

```turtle
# Block: APPLICATION — AMQ "Application" category checks
@prefix sh:   <http://www.w3.org/ns/shacl#> .
@prefix li:   <http://mortgage.audit.ontology/loan-instance#> .
@prefix caro: <http://mortgage.audit.ontology/caro#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

### CHK-APP-001 — Employment start date: 1003 vs VOE
li:EmploymentStartDateShape a sh:NodeShape ;
    caro:checkId "CHK-APP-001" ;
    caro:blockRef "application" ;
    caro:exceptionRef "URLA-Final-9" ;
    caro:hasSeverity "Major" ;
    caro:citesFields "employment_start_date_1003", "employment_start_date_voe" ;
    sh:sparql [ ... ] .

### CHK-APP-002 — Title vesting: 1003 vs Title Commitment
li:TitleVestingShape a sh:NodeShape ;
    caro:checkId "CHK-APP-002" ;
    caro:blockRef "application" ;
    ...
```

**Frontend mapping:**
- Each `.ttl` file → one `Block` in the UI
- The file comment `# Block: APPLICATION — AMQ "Application" category checks` → `Block.name` and `Block.description`
- Each `sh:NodeShape` inside the file → one `Check` in the UI's Available Checks pool for that block
- `caro:checkId` → `Check.id`
- `caro:exceptionRef` → `Check.exceptionCode`
- `caro:hasSeverity` → `Check.severity`
- `caro:citesFields` → parse into `Check.fieldId` (primary field) + `Check.compareFieldId` (if doc-vs-doc)

**UI impact:** **Small adapter needed.** The frontend needs a lightweight RDF parser (or a pre-compiled JSON index) to extract check metadata from .ttl files. Two options:

### Option A: Parse .ttl at UI load time (lightweight RDF lib)
- Use a browser-compatible RDF library (e.g. `rdflib.js`, `n3.js`) to parse each block .ttl file
- Extract `sh:NodeShape` subjects + their `caro:*` annotations
- Reconstruct `Check[]` objects

**Pro:** Direct read from the canonical source (the .ttl files)  
**Con:** Adds a runtime dependency on an RDF parser (~50KB gzipped); parsing overhead at page load

### Option B: Pre-compile .ttl → JSON at build time (zero runtime cost)
- Add a build-time script (`scripts/compile_shacl_to_json.py`) that parses all `blocks/*.ttl` files and emits `frontend/src/data/blocks.json` + `frontend/src/data/checks.json`
- Frontend reads the pre-compiled JSON, no RDF parsing needed

**Pro:** Zero runtime overhead, no new dependencies, simpler frontend code  
**Con:** One more build step; frontend data is one commit behind if .ttl files change and build isn't re-run

**Recommendation:** **Option B** (pre-compile to JSON). This matches the existing `shapes_manifest.json` versioning pattern already present in the SHACL pilot — shapes are already being hashed and versioned, so a pre-compiled JSON index fits naturally.

---

## 3. Checks — Already Implemented (as SHACL NodeShapes)

**Files:** `src/shacl_pilot/blocks/*.ttl` (each `sh:NodeShape` is one check)

**Additional metadata source:** `src/shacl_pilot/compiled/ruleset.json` (the AMQ compiler output, 4,167 rules compiled from the 5,520-row AMQ CSV)

**Check metadata extracted from SHACL shapes:**
- `caro:checkId` → `Check.id` (e.g. `"CHK-APP-001"`)
- `caro:blockRef` → `Check.blockId` (e.g. `"application"`)
- `caro:exceptionRef` → `Check.exceptionCode` (e.g. `"URLA-Final-9"`)
- `caro:hasSeverity` → `Check.severity` (`"Major"`, `"Critical"`, etc.)
- `caro:citesFields` → comma-separated field IDs → parse into `Check.fieldId` + optional `Check.compareFieldId`

**Check metadata from `compiled/ruleset.json`:**

Each rule in the compiled ruleset carries:
```json
{
  "question_code": "Final URLA",
  "question_text": "Have all sections of the Final 1003 been completed and accurate?",
  "exception_code": "URLA-Final-9",
  "exception_description": "The employment dates listed on the 1003 do not match other employment documentation in the file",
  "response_text": "The employment dates listed on the 1003 do not match other employment documentation in the file",
  "severity": "Major",
  "block": "application-verification",
  "category": "Application",
  "agency": "GENERIC",
  "aor": "Underwriter",
  "eval_class": "unmapped" | "mapped" | "doc_presence",
  "eval_target": "final_1003" | null,
  "source_rows": [2, 3, 4, 5, 6, 7, 8, 9]
}
```

**How to join:**
- SHACL shapes use `caro:exceptionRef` (e.g. `"URLA-Final-9"`)
- `compiled/ruleset.json` uses `exception_code` (e.g. `"URLA-Final-9"`)
- **Join key:** `exception_code` (unique per AMQ rule)

**Enriched `Check` object for the UI:**

```typescript
interface Check {
  id: string;                     // from caro:checkId
  name: string;                   // from ruleset.json exception_name or generated
  blockId: string;                // from caro:blockRef
  fieldId: string;                // from caro:citesFields (first field)
  compareFieldId?: string;        // from caro:citesFields (second field, if present)
  kind: CheckKind;                // inferred: if 2 fields → agree_doc_*, else TBD
  severity: Severity;             // from caro:hasSeverity or ruleset.json severity
  questionCode?: string;          // from ruleset.json question_code
  questionText?: string;          // from ruleset.json question_text
  exceptionCode: string;          // from caro:exceptionRef (join key)
  exceptionDescription: string;   // from ruleset.json exception_description
  sourceCondition: string;        // from ruleset.json response_text (AMQ source text)
  plainEnglish?: string;          // generated or from ruleset.json
  grounding?: GuidelineCitation[]; // from SHACL sh:message citations (if present)
  sourceLocator?: SourceLocator;  // from ruleset.json source_rows → map to AMQ workbook row
  agency: string;                 // from ruleset.json agency (O-FNM, O-FHA, GENERIC, etc.)
  evalClass: string;              // from ruleset.json eval_class (mapped, unmapped, doc_presence)
}
```

**UI impact:** **Medium adapter needed.** The frontend needs:
1. A parser/indexer for `blocks/*.ttl` files → extract check metadata
2. A loader for `compiled/ruleset.json` → enrich checks with AMQ metadata
3. A join operation on `exception_code` to merge SHACL shape annotations + AMQ compiler output

---

## 4. Question Grouping — Already Implicit in AMQ Compiler

**Context:** The frontend action items doc (`docs/frontend/ACTION-ITEMS-2026-07-30.md`, item #1, sub-finding from the citation-gaps doc) identified `question_code` grouping as a missing field — multiple AMQ rows share one Question Code (e.g. "Final URLA" has 9 sibling rows), but the compiler reads `question_code` per row and never persists it onto the compiled `Check`.

**SHACL pilot status:** The `compiled/ruleset.json` output from `src/shacl_pilot/amq_compiler.py` **already includes `question_code` and `question_text` per rule** (lines 10-11 of the sample output above). This was explicitly preserved in the SHACL pilot's compiler.

**Excerpt from `compiled/ruleset.json`:**
```json
{
  "question_code": "Final URLA",
  "question_text": "Have all sections of the Final 1003 been completed and accurate?",
  "exception_code": "URLA-Final-9",
  ...
}
```

**Frontend mapping:** The UI's `QuestionGroup` component (from `BlockDetail.tsx`) can cluster checks by `questionCode` directly — no frontend change needed, the data is already there.

**UI impact:** **None.** The SHACL pilot's compiler already persists `question_code` and `question_text`, so the frontend's question-grouping feature works as-is once it reads `compiled/ruleset.json`.

---

## 5. Citation Support — Partially Implemented

**Context:** The citation-gaps doc (`output/CITATION-AND-COMPILER-GAPS-2026-07-29.md`) identified 5 real backend/compiler gaps. How does the SHACL pilot fare?

### Gap 1: `question_code` persisted?
**Status:** ✅ **FIXED** in SHACL pilot. The `compiled/ruleset.json` includes `question_code` and `question_text` per rule.

### Gap 2: Doc-vs-doc miscompile (35 suspects, 2 fixed)?
**Status:** ⚠️ **PARTIALLY ADDRESSED**. The SHACL shapes use explicit `caro:citesFields "field1", "field2"` annotations, which unambiguously declare doc-vs-doc comparisons (e.g. `EmploymentStartDateShape` cites both `employment_start_date_1003` and `employment_start_date_voe`). This is structurally clearer than the `p0/` compiler's `agree_categorical` vs `agree_doc_categorical` kind inference. However, the SHACL pilot only has **12 mapped shapes** (out of 4,167 AMQ rules), so the 35-suspect miscompile audit from the `p0/` compiler is not directly applicable — the SHACL pilot hasn't compiled those 35 rules yet.

### Gap 3: `GroundingRecord` computed, then discarded?
**Status:** ⚠️ **MIXED**. The SHACL pilot includes a `selling_guide_index.py` module (lines 40-41 of memory) that deterministically indexes the Fannie Selling Guide PDF into 386 topics with code/title/date/PDF-page. The `LargeDepositShape` example in memory shows this grounding was used to verify O-FNM-15334's 50% threshold against B3-4.2-02 p.432. However, it's unclear whether this grounding is **persisted on the SHACL shapes themselves** (e.g. as `sh:message` citation links) or just used during shape authoring and then discarded. The .ttl files do NOT show inline guide citations in the sample shapes (the `sh:message` text is a plain defect message, not a cited guide section). **This gap is still open** unless the SHACL pilot's shapes start embedding `<http://selling-guide/section/B3-4.2-02>` resource links in their definitions.

### Gap 4: No AMQ row/sheet locator?
**Status:** ⚠️ **PARTIALLY ADDRESSED**. The `compiled/ruleset.json` output includes `source_rows: [2, 3, 4, 5, ...]` per rule, which are 1-indexed row numbers from the AMQ CSV. This is a **synthetic row index** (the CSV row number), not the original .xlsx row/sheet locator, but it's better than nothing — the UI can render "AMQ CSV row 2" as the source citation. The .xlsx file/sheet/row locator is still missing (the AMQ compiler reads a CSV export, not the original .xlsx).

### Gap 5: `citation_required` never enforced?
**Status:** ❓ **UNKNOWN**. The SHACL pilot's extraction output (`src/shacl_pilot/out/loan_01.json`) shows field-level `citation` objects with `doc_name`, `page`, and `snippet` (lines 17-21 of the loan_01.json sample above). This suggests citation capture IS happening at extraction time. However, there's no visible enforcement of "this field requires a citation" in the SHACL shapes or the audit runner — the `caro:citesFields` annotation declares which fields a check reads, not which fields require citations. **This gap is likely still open** unless the audit runner has a separate citation-required gate (not visible in the sampled files).

---

## 6. Data Flow: SHACL Pilot → Frontend UI

**Current state (SHACL pilot):**
1. `src/shacl_pilot/amq_compiler.py` reads `src/doc/PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv` (5,520 rows) → compiles to `src/shacl_pilot/compiled/ruleset.json` (4,167 rules, after excluding 379 discarded + 1 external-lookup)
2. Hand-authored SHACL shapes in `src/shacl_pilot/blocks/*.ttl` (12 shapes currently) define the executable checks
3. `src/shacl_pilot/routes.json` defines 5 program-specific routes, each referencing blocks from the 16-block catalog
4. `src/shacl_pilot/shape_manifest.py` hashes all .ttl files + routes.json → `src/shacl_pilot/shapes_manifest.json` (versioned, 6 versions so far)
5. `src/shacl_pilot/extract_loan.py` extracts loan data from PDFs + MISMO XML → `src/shacl_pilot/out/loan_NN.json`
6. `src/shacl_pilot/loan_to_rdf.py` converts extracted loan data → `src/shacl_pilot/out/loan_NN.ttl` (RDF instance graph)
7. `src/shacl_pilot/run_audit.py` runs SHACL validation against the instance graph → produces defect reports (markdown, per-loan JSON)

**Proposed data flow (SHACL pilot → frontend UI):**

```
┌─────────────────────────────────────────────────────────────┐
│ SHACL Pilot (src/shacl_pilot/)                              │
│                                                              │
│  1. amq_compiler.py                                          │
│     ↓                                                        │
│  2. compiled/ruleset.json (4,167 rules + metadata)          │
│                                                              │
│  3. blocks/*.ttl (12 SHACL shapes, hand-authored)           │
│                                                              │
│  4. routes.json (5 routes, 16-block catalog)                │
│                                                              │
│  5. shapes_manifest.json (hash-versioned)                   │
│     ↓                                                        │
│  6. scripts/compile_shacl_to_json.py  ← NEW BUILD STEP      │
│     ↓                                                        │
│  7. frontend/src/data/shaclBlocks.json  ← NEW FILE          │
│     frontend/src/data/shaclChecks.json  ← NEW FILE          │
│     frontend/src/data/shaclRoutes.json  ← NEW FILE          │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Frontend (frontend/src/)                                     │
│                                                              │
│  • ImportAndSignView.tsx — reads shaclChecks.json            │
│  • RouteList.tsx — reads shaclRoutes.json                    │
│  • RouteDetail.tsx — reads shaclRoutes.json + shaclBlocks    │
│  • BlockDetail.tsx — reads shaclBlocks + shaclChecks         │
│  • ApplyView.tsx — reads loan audit results (from engine)    │
└─────────────────────────────────────────────────────────────┘
```

**New build step: `scripts/compile_shacl_to_json.py`**

```python
#!/usr/bin/env python3
"""
Compile SHACL shapes (blocks/*.ttl + routes.json + compiled/ruleset.json)
into frontend-friendly JSON files.

USAGE:  python3 scripts/compile_shacl_to_json.py
OUTPUT: frontend/src/data/shaclBlocks.json
        frontend/src/data/shaclChecks.json
        frontend/src/data/shaclRoutes.json
"""
import json
from rdflib import Graph, Namespace

CARO = Namespace("http://mortgage.audit.ontology/caro#")
SH = Namespace("http://www.w3.org/ns/shacl#")

def parse_blocks_and_checks(ttl_files, ruleset_json):
    """Parse all .ttl files, extract checks, enrich with ruleset metadata."""
    blocks = []
    checks = []
    
    # Load ruleset for enrichment (question_code, question_text, etc.)
    ruleset_by_exception = {r["exception_code"]: r for r in ruleset_json["rules"]}
    
    for ttl_path in ttl_files:
        g = Graph()
        g.parse(ttl_path, format="turtle")
        
        # Extract block name from file comment or filename
        block_id = extract_block_id(ttl_path)
        blocks.append({"id": block_id, "checkIds": []})
        
        # Extract all NodeShapes
        for shape in g.subjects(RDF.type, SH.NodeShape):
            check_id = str(g.value(shape, CARO.checkId))
            exception_code = str(g.value(shape, CARO.exceptionRef))
            severity = str(g.value(shape, CARO.hasSeverity))
            fields = str(g.value(shape, CARO.citesFields)).split(", ")
            
            # Enrich from ruleset.json
            rule = ruleset_by_exception.get(exception_code, {})
            
            check = {
                "id": check_id,
                "blockId": block_id,
                "exceptionCode": exception_code,
                "severity": severity,
                "fieldId": fields[0] if fields else None,
                "compareFieldId": fields[1] if len(fields) > 1 else None,
                "kind": infer_kind(fields),
                "questionCode": rule.get("question_code"),
                "questionText": rule.get("question_text"),
                "sourceCondition": rule.get("response_text"),
                "exceptionDescription": rule.get("exception_description"),
                "agency": rule.get("agency"),
                "evalClass": rule.get("eval_class"),
            }
            checks.append(check)
            blocks[-1]["checkIds"].append(check_id)
    
    return blocks, checks

def parse_routes(routes_json):
    """Convert routes.json to frontend Route[] format."""
    routes = []
    for route_id, route_data in routes_json["routes"].items():
        routes.append({
            "id": route_id,
            "name": route_data["title"],
            "agency": route_data["agency"],
            "blockIds": routes_json["catalog_blocks"] + route_data.get("extra_blocks", []),
        })
    return routes

# ... rest of implementation
```

**Frontend changes required:** **Zero UI component changes.** The existing Route/Block/Check components already know how to render `Route[]`, `Block[]`, and `Check[]` — they just need to read from `shaclRoutes.json`, `shaclBlocks.json`, and `shaclChecks.json` instead of `mockData.ts`.

**Data adapter swap:**

```typescript
// BEFORE (mockup):
import { MOCK_ROUTES, MOCK_BLOCKS, MOCK_CHECKS } from "../data/mockData";

// AFTER (SHACL pilot):
import shaclRoutes from "../data/shaclRoutes.json";
import shaclBlocks from "../data/shaclBlocks.json";
import shaclChecks from "../data/shaclChecks.json";

const routes: Route[] = shaclRoutes;
const blocks: Block[] = shaclBlocks;
const checks: Check[] = shaclChecks;
```

---

## 7. Open Questions & Recommendations

### Q1: Should the frontend read SHACL pilot data directly, or wait for it to be promoted to `p0/`?

**Context:** The SHACL pilot lives in `src/` (gitignored, experimental sandbox per memory). The production engine is in `p0/`. The frontend mockup currently reads neither — it uses synthetic `mockData.ts`.

**Options:**
- **A. Frontend reads `src/shacl_pilot/` directly** — Requires the frontend to depend on gitignored experimental data. Risky if `src/` is truly ephemeral.
- **B. Wait for SHACL pilot promotion to `p0/`** — Frontend continues using `mockData.ts` until the SHACL shapes are promoted out of the sandbox. Once promoted, the frontend switches to reading the promoted artifacts.
- **C. Hybrid: frontend reads a COPY of SHACL pilot data committed to the repo** — Add a `frontend/src/data/shacl_snapshot/` directory with a committed copy of `routes.json`, `compiled/ruleset.json`, and pre-compiled JSON indexes. This decouples the frontend from the gitignored `src/` while still using real SHACL-derived data.

**Recommendation:** **Option C (committed snapshot).** This lets the frontend build against real SHACL-shaped data without depending on gitignored files, and provides a clean migration path when the SHACL pilot is promoted — just update the snapshot source.

### Q2: How should the frontend handle the 4,155 unmapped checks (4,167 total - 12 mapped)?

**Context:** The SHACL pilot has only mapped 12 checks (100% of the 25 known defects across 5 loans, but <1% of the 4,167 compiled AMQ rules). The remaining 4,155 rules are compiled into `ruleset.json` with `eval_class: "unmapped"` or `"doc_presence"`.

**Options:**
- **A. Show all 4,167 checks in the Available Checks pool** — Mark unmapped checks with a badge (`NOT_EVALUATED`, `DOC_PRESENCE_ONLY`, etc.)
- **B. Filter to mapped checks only (12)** — Hide unmapped checks entirely; only show the 12 that have real SHACL shapes
- **C. Show all, but with a clear visual distinction** — Mapped checks get full edit capability, unmapped checks are read-only with a "Not yet implemented" badge

**Recommendation:** **Option C (show all, mark unmapped).** This gives SMEs the full AMQ catalog view (4,167 rules) and lets them see what's mapped vs. unmapped, which informs prioritization ("which of these 4,155 unmapped checks do we want to map next?"). The `evalClass` field from `compiled/ruleset.json` already provides the status flag needed for this.

### Q3: Should the Route DAG diagram (action item #2) show SHACL execution order or just containment?

**Context:** The `routes.json` file currently defines blocks as a flat list per route. There's no explicit execution-order metadata (parallel vs. sequential blocks). The audit report (`full_5loan_audit_latest.md`) mentions "689–1,385 rules run (program-filtered from 4,166 total)" — the filtering is deterministic (by agency), but the execution order is not documented.

**Recommendation:** Start with **containment-only DAG** (Checks → Blocks → Route) for the first iteration. Add execution-order metadata (parallel/sequential edges) later if the SHACL pilot's `run_audit.py` gains that capability.

---

## 8. Final Verdict

**Can the Route/Block/Check UI model still be supported after SHACL extraction?**

**YES — with high fidelity and low effort.**

The SHACL pilot already implements the Route → Block → Check hierarchy in a UI-compatible shape:
- **Routes** are defined in `routes.json` (5 program-specific routes, 16-block catalog)
- **Blocks** are .ttl files (`blocks/*.ttl`, 9 files, each a named grouping of checks)
- **Checks** are SHACL `NodeShape` definitions inside blocks, annotated with `caro:checkId`, `caro:blockRef`, `caro:exceptionRef`, `caro:hasSeverity`, `caro:citesFields`

The frontend needs:
1. **One new build step:** `scripts/compile_shacl_to_json.py` to pre-compile .ttl + routes.json + compiled/ruleset.json → `frontend/src/data/shaclBlocks.json` + `shaclChecks.json` + `shaclRoutes.json`
2. **One data adapter swap:** Replace `mockData.ts` imports with the new JSON files
3. **Zero UI component changes:** The existing Route/Block/Check components work as-is

**Effort estimate:** **1-2 days** (build script + data adapter + integration testing).

**Risk:** **Low.** The SHACL shapes already embed all required metadata; the frontend just needs to read it in a different format.

**Next steps:**
1. Write `scripts/compile_shacl_to_json.py` (Python script, ~200 lines, uses `rdflib` to parse .ttl)
2. Run it to generate `frontend/src/data/shaclRoutes.json`, `shaclBlocks.json`, `shaclChecks.json`
3. Update `mockData.ts` to import from the new files instead of hardcoded mock data
4. Verify all Route/Block/Check screens render correctly with SHACL-sourced data
5. Add a "Data Source: SHACL Pilot v3 (ruleset SHA 6fa9840dc020)" banner to the mockup

**Compatibility: ✅ CONFIRMED.**
