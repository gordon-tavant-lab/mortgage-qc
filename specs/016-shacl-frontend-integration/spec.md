# Feature Specification: SHACL Shapes → Frontend Integration

**Feature Branch**: `016-shacl-frontend-integration`  
**Created**: 2026-07-30  
**Status**: Draft  
**Input**: Gordon's request after SHACL pilot v3 achieved 100% detection (25/25 defects across 5 loans): "we have now extracted the rules into SHACL shapes, will we still able to support the UI route/blocks/checks?" — compatibility analysis confirmed YES with 1-2 days effort, zero UI changes required.

**Governs**: Frontend Route/Block/Check authoring surface compatibility with the SHACL pilot's artifact structure (`src/shacl_pilot/`). Ensures the Kayla-review mockup (PR #2, branch `worktree-kayla-mockup`) can switch from synthetic `mockData.ts` to real SHACL-derived data without component rewrites.

**Depends on**: 
- SHACL pilot v3 artifacts (`src/shacl_pilot/routes.json`, `blocks/*.ttl`, `compiled/ruleset.json`, `shapes_manifest.json`)
- Frontend mockup (PR #2) — existing Route/Block/Check components in `frontend/src/components/`
- Compatibility analysis (`docs/frontend/SHACL-UI-COMPATIBILITY-ANALYSIS.md`) — confirmed structural match

**Foundation this builds on**: The SHACL pilot already implements Route → Block → Check as:
1. **Routes** (`routes.json`) — 5 program-specific routes (FNM, FHA, VA, FRD, RHS), each containing blocks from a 16-block catalog
2. **Blocks** (`.ttl` files) — 9 block files currently (`application.ttl`, `assets.ttl`, etc.), each a named grouping of SHACL `NodeShape` checks
3. **Checks** (SHACL `NodeShape` definitions inside blocks) — annotated with `caro:checkId`, `caro:blockRef`, `caro:exceptionRef`, `caro:hasSeverity`, `caro:citesFields`

The frontend already has Route/Block/Check components — they just need a data adapter that reads SHACL artifacts instead of `mockData.ts`.

**What this feature is fixing, precisely**: The frontend mockup currently uses synthetic data (`frontend/src/data/mockData.ts`) that manually mirrors what the backend *should* produce. The SHACL pilot's compiler and shapes now produce the real artifacts (4,167 compiled AMQ rules, 12 mapped SHACL shapes, hash-versioned). This feature bridges the gap: a build-time script that parses SHACL artifacts → emits frontend-consumable JSON, plus a frontend data adapter that reads the new JSON files instead of `mockData.ts`. No UI component changes — the Route/Block/Check components already know how to render `Route[]`, `Block[]`, and `Check[]`.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Frontend reads real SHACL-compiled rules instead of synthetic mock data (Priority: P0)

**Why this priority**: This is the feature's entire reason to exist. The frontend mockup was built to demonstrate the Route/Block/Check authoring UX — once the SHACL pilot proved the backend can produce real artifacts at scale (4,167 rules), the frontend must be able to read them.

**Independent Test**: 
1. Run `scripts/compile_shacl_to_json.py` against `src/shacl_pilot/` artifacts
2. Verify it emits `frontend/src/data/shaclRoutes.json`, `shaclBlocks.json`, `shaclChecks.json`
3. Update frontend imports to read from the new files
4. Launch `npm run dev` and navigate through all Route/Block/Check screens
5. Confirm all screens render correctly with SHACL-sourced data (no console errors, no missing fields, correct counts)

**Acceptance Scenarios**:

1. **Given** the SHACL pilot has compiled 4,167 AMQ rules into `compiled/ruleset.json`, **When** `compile_shacl_to_json.py` runs, **Then** `shaclChecks.json` contains 4,167 check objects, each with `id`, `blockId`, `exceptionCode`, `severity`, `questionCode`, `questionText`, `sourceCondition`, `agency`, `evalClass`.

2. **Given** the SHACL pilot has 9 block `.ttl` files (application, assets, credit-liabilities, income, product-specific, property-appraisal, underwriting, certification-delivery, closing), **When** `compile_shacl_to_json.py` runs, **Then** `shaclBlocks.json` contains 9 block objects, each with `id`, `name`, `description`, `checkIds` (array of check IDs belonging to that block).

3. **Given** `routes.json` defines 5 program-specific routes (fnm-post-closing-qc, fha-post-closing-qc, va-post-closing-qc, frd-post-closing-qc, rhs-post-closing-qc), **When** `compile_shacl_to_json.py` runs, **Then** `shaclRoutes.json` contains 5 route objects, each with `id`, `name`, `agency`, `blockIds` (array of block IDs in that route).

4. **Given** the frontend is updated to import from `shaclRoutes.json`/`shaclBlocks.json`/`shaclChecks.json`, **When** the dev server is launched and a user navigates to the Route List screen, **Then** all 5 routes are visible with correct titles and agency labels.

5. **Given** the frontend reads from SHACL-sourced data, **When** a user drills into a route (e.g. "Conventional (Fannie Mae) Post-Closing QC") on the Route Detail screen, **Then** the Available Blocks pool shows 16 catalog blocks, and the Active Blocks pane shows the blocks assigned to that route.

6. **Given** a user drills into a block (e.g. "Application") on the Block Detail screen, **When** the Available Checks pool renders, **Then** checks are grouped by `questionCode` where applicable (e.g. "Final URLA" groups 9 sibling checks), and each check shows its `exceptionCode`, `severity`, and `evalClass` badge (`mapped`, `unmapped`, `doc_presence`).

---

### User Story 2 - SHACL shape metadata enriches frontend check display (Priority: P1)

The SHACL shapes embed metadata (`caro:checkId`, `caro:exceptionRef`, `caro:hasSeverity`, `caro:citesFields`) that the frontend's mock data currently synthesizes. This feature must preserve that metadata through the compile-to-JSON step.

**Why this priority**: Without this metadata, the frontend can't show check severity, field citations, or the compiled-gate summary — all P1 features in the Kayla-review mockup (PR #2).

**Independent Test**: 
1. Pick one mapped SHACL shape (e.g. `EmploymentStartDateShape` from `blocks/application.ttl`)
2. Verify `compile_shacl_to_json.py` extracts its `caro:checkId`, `caro:exceptionRef`, `caro:hasSeverity`, `caro:citesFields` annotations
3. Confirm the resulting `shaclChecks.json` entry contains `id: "CHK-APP-001"`, `exceptionCode: "URLA-Final-9"`, `severity: "Major"`, `fieldId: "employment_start_date_1003"`, `compareFieldId: "employment_start_date_voe"`
4. Launch the frontend, drill into Application block, select that check
5. Confirm the Edit Check panel shows "Employment start date: 1003 vs VOE", severity badge "Major", and the compiled-gate summary "employment_start_date_1003 agrees_with employment_start_date_voe"

**Acceptance Scenarios**:

1. **Given** a SHACL shape has `caro:citesFields "field1", "field2"`, **When** `compile_shacl_to_json.py` parses it, **Then** the resulting check object has `fieldId: "field1"` and `compareFieldId: "field2"`, **AND** `kind: "agree_doc_categorical"` (inferred from 2 fields).

2. **Given** a SHACL shape has `caro:citesFields "field1"` (single field), **When** `compile_shacl_to_json.py` parses it, **Then** the resulting check object has `fieldId: "field1"` and `compareFieldId: null`, **AND** `kind` is inferred based on the check's structure (predicate, ratio, or agree_categorical).

3. **Given** a check in `shaclChecks.json` has `evalClass: "unmapped"`, **When** the frontend renders it in the Available Checks pool, **Then** it displays a `NOT_EVALUATED` badge and the Edit Check panel shows a read-only view with "Not yet implemented" message.

4. **Given** a check in `shaclChecks.json` has `evalClass: "doc_presence"`, **When** the frontend renders it, **Then** it displays a `DOC_PRESENCE_ONLY` badge (auto-compiled inventory check, no field-level logic).

---

### User Story 3 - Question-code grouping works with SHACL-compiled rules (Priority: P1)

The frontend's `BlockDetail.tsx` component already clusters checks by `questionCode` (e.g. "Final URLA" groups 9 sibling checks). The SHACL pilot's `compiled/ruleset.json` already includes `question_code` and `question_text` per rule.

**Why this priority**: Question grouping was identified as a missing field in the citation-gaps doc (`output/CITATION-AND-COMPILER-GAPS-2026-07-29.md`, gap #1) — but the SHACL pilot already fixed this. This feature must preserve it.

**Independent Test**: 
1. Find a multi-sibling question in `compiled/ruleset.json` (e.g. `question_code: "Final URLA"` with 9 exception codes)
2. Verify `compile_shacl_to_json.py` extracts `questionCode` and `questionText` for each check
3. Confirm `shaclChecks.json` has 9 checks all sharing `questionCode: "Final URLA"` and `questionText: "Have all sections of the Final 1003 been completed and accurate?"`
4. Launch the frontend, drill into Application block
5. Confirm the Available Checks pool renders a `QuestionGroup` header "Final URLA — ONE QUESTION, 9 POSSIBLE ANSWERS" with all 9 sibling checks expanded (not collapsed)

**Acceptance Scenarios**:

1. **Given** 9 AMQ rules share `question_code: "Final URLA"`, **When** `compile_shacl_to_json.py` runs, **Then** all 9 resulting check objects have `questionCode: "Final URLA"` and the same `questionText`.

2. **Given** the frontend reads SHACL-sourced checks with `questionCode`, **When** the Block Detail screen renders Available Checks, **Then** checks sharing a `questionCode` are visually clustered under their shared `questionText` header, each check individually visible (expanded by default, not collapsed).

3. **Given** a check has no `questionCode` (null or empty), **When** the Block Detail screen renders it, **Then** it appears as a standalone check outside any question group, not hidden or dropped.

---

### User Story 4 - Versioned shapes manifest is preserved in frontend build artifacts (Priority: P2)

The SHACL pilot's `shapes_manifest.json` hash-versions every .ttl file + `routes.json` change (currently v6, SHA `9a24f2e9b5c0`). The frontend build artifacts should carry this version to trace which ruleset version the UI is displaying.

**Why this priority**: Lower than P0/P1 (the UI works without this), but essential for audit traceability — when a user views the Import & Sign screen, they should see "Data Source: SHACL Pilot v6 (SHA 9a24f2e9b5c0)" to know which ruleset version they're signing.

**Independent Test**: 
1. Run `compile_shacl_to_json.py` against SHACL pilot artifacts
2. Verify it reads `shapes_manifest.json` and embeds the latest version + SHA in `shaclMeta.json`
3. Confirm `frontend/src/data/shaclMeta.json` contains `{ "version": 6, "sha": "9a24f2e9b5c0", "timestamp": "2026-07-29T23:46:28" }`
4. Update `ImportAndSignView.tsx` to display "Data Source: SHACL Pilot v{version} (SHA {sha})" in the file-imported banner
5. Launch the frontend, navigate to Import & Sign screen
6. Confirm the banner shows the correct version + SHA

**Acceptance Scenarios**:

1. **Given** `shapes_manifest.json` has version 6 with SHA `9a24f2e9b5c0`, **When** `compile_shacl_to_json.py` runs, **Then** `shaclMeta.json` contains `version: 6` and `sha: "9a24f2e9b5c0"`.

2. **Given** the frontend imports `shaclMeta.json`, **When** the Import & Sign screen renders, **Then** the file-imported banner displays "Data Source: SHACL Pilot v6 (SHA 9a24f2e9b5c0)".

3. **Given** the SHACL pilot's shapes are updated (new version 7), **When** `compile_shacl_to_json.py` re-runs and the frontend rebuilds, **Then** the Import & Sign banner updates to show "v7" and the new SHA.

---

## Functional Requirements *(mandatory)*

### FR-001: Build-time SHACL → JSON compiler script

**What**: A Python script (`scripts/compile_shacl_to_json.py`) that parses SHACL pilot artifacts → emits frontend-consumable JSON files.

**Inputs**:
- `src/shacl_pilot/routes.json` — route definitions
- `src/shacl_pilot/blocks/*.ttl` — SHACL shape definitions (9 files)
- `src/shacl_pilot/compiled/ruleset.json` — AMQ compiler output (4,167 rules)
- `src/shacl_pilot/shapes_manifest.json` — hash-versioned shape metadata

**Outputs**:
- `frontend/src/data/shaclRoutes.json` — `Route[]` (5 routes)
- `frontend/src/data/shaclBlocks.json` — `Block[]` (9 blocks)
- `frontend/src/data/shaclChecks.json` — `Check[]` (4,167 checks)
- `frontend/src/data/shaclMeta.json` — `{ version, sha, timestamp }` (from shapes_manifest)

**Algorithm**:
1. Parse `routes.json` → extract route definitions, convert to frontend `Route[]` format
2. Parse each `blocks/*.ttl` file via `rdflib` → extract all `sh:NodeShape` subjects
3. For each `NodeShape`, extract `caro:checkId`, `caro:blockRef`, `caro:exceptionRef`, `caro:hasSeverity`, `caro:citesFields`
4. Load `compiled/ruleset.json`, index by `exception_code` (join key)
5. For each SHACL shape, join with the corresponding ruleset entry → enrich with `question_code`, `question_text`, `source_rows`, `agency`, `eval_class`, `response_text` (source condition), `exception_description`
6. Infer `kind` from `citesFields` count: 2 fields → `agree_doc_categorical`, 1 field → context-dependent (check for predicate/ratio/agree patterns in the SPARQL constraint)
7. Group checks by `blockId` → emit `Block[]` with `checkIds` arrays
8. Read `shapes_manifest.json` → extract latest version entry → emit `shaclMeta.json`

**Dependencies**: `rdflib` (Python RDF parser), standard library (`json`, `hashlib`, `os`)

**Exit codes**:
- `0` — success, all 4 JSON files written
- `1` — parse error (malformed .ttl or routes.json)
- `2` — join error (SHACL shape has `caro:exceptionRef` not found in `compiled/ruleset.json`)
- `3` — validation error (missing required fields in output)

**Invocation**: `python3 scripts/compile_shacl_to_json.py` (no arguments, paths hardcoded relative to repo root)

**Runtime**: Expected <5 seconds (9 .ttl files + 1 large JSON file, total ~3.5 MB)

---

### FR-002: Frontend data adapter swap

**What**: Replace `frontend/src/data/mockData.ts` imports with SHACL-sourced JSON files.

**Changes required**:
1. `frontend/src/components/RouteList.tsx` — import `shaclRoutes` from `../data/shaclRoutes.json` instead of `MOCK_ROUTES` from `mockData.ts`
2. `frontend/src/components/RouteDetail.tsx` — same (routes + blocks)
3. `frontend/src/components/BlockDetail.tsx` — import `shaclBlocks` and `shaclChecks` instead of `MOCK_BLOCKS` and `MOCK_CHECKS`
4. `frontend/src/components/ImportAndSignView.tsx` — import `shaclChecks` and `shaclMeta` instead of `MOCK_CHECKS` and `MOCK_SIGNED_RULESET`
5. `frontend/src/components/ApplyView.tsx` — no change (reads loan evaluation results from a separate source, not the ruleset catalog)

**Type safety**: All SHACL-sourced JSON files must match existing TypeScript interfaces (`Route`, `Block`, `Check` from `frontend/src/lib/types.ts`). The `compile_shacl_to_json.py` script's output structure is validated against these types.

**Fallback**: If `shaclChecks.json` does not exist (e.g. user hasn't run the compiler script yet), frontend build should fail with a clear error: `Error: SHACL-sourced data not found. Run 'python3 scripts/compile_shacl_to_json.py' first.`

---

### FR-003: Mark unmapped checks visually in the UI

**What**: The SHACL pilot has only 12 mapped checks (out of 4,167 compiled AMQ rules). The remaining 4,155 are `evalClass: "unmapped"` or `"doc_presence"`. The frontend must show all 4,167 checks but visually distinguish mapped vs. unmapped.

**UI treatment**:
- **Mapped checks** (`evalClass: "mapped"`) — full edit capability, no badge
- **Unmapped checks** (`evalClass: "unmapped"`) — read-only Edit Check panel with amber `NOT_EVALUATED` badge, message: "This check is compiled but not yet mapped to a SHACL shape. Runtime status: NOT_EVALUATED (never a silent pass)."
- **Doc-presence checks** (`evalClass: "doc_presence"`) — read-only Edit Check panel with slate `DOC_PRESENCE` badge, message: "Auto-compiled inventory check: passes if document is present in file, NEEDS_REVIEW if absent."

**Component changes**:
- `BlockDetail.tsx` — add badge rendering per check based on `evalClass`
- `CheckEditor` sub-component — disable form fields when `evalClass !== "mapped"`

**Why this treatment**: Hiding unmapped checks entirely (option B from the compatibility analysis) would prevent SMEs from seeing the full AMQ catalog scope. Showing all checks with clear status badges (option C) informs prioritization: "which of these 4,155 unmapped checks should we map next?"

---

### FR-004: Preserve question-code grouping in Block Detail

**What**: The frontend's `BlockDetail.tsx` already implements `QuestionGroup` clustering (from PR #2's kind-aware edit work). This must continue working with SHACL-sourced data.

**Data requirement**: `shaclChecks.json` must include `questionCode` and `questionText` for every check that has them in `compiled/ruleset.json`.

**UI behavior** (already implemented, no changes):
1. Checks with the same `questionCode` are clustered under a shared `QuestionGroup` header
2. Header shows: `"{questionText}" — ONE QUESTION, {N} POSSIBLE ANSWERS"`
3. All sibling checks are expanded by default (not collapsed) — per the contrarian finding in `output/CITATION-AND-COMPILER-GAPS-2026-07-29.md` §6 (false mutual-exclusivity + sign-off-theater risk)
4. Each sibling check is individually activatable (no bulk "activate all N" gesture)

**Validation**: After FR-002 data adapter swap, verify "Final URLA" question (9 sibling checks) renders correctly with SHACL-sourced data.

---

### FR-005: Display SHACL shapes version in Import & Sign banner

**What**: Add a data-source banner to the Import & Sign screen showing which SHACL shapes version the UI is displaying.

**Component change**: `ImportAndSignView.tsx` — update the file-imported banner to include:
```tsx
<div className="text-xs text-slate-500">
  {MOCK_CHECKS.length} conditions parsed for this route · imported 2026-07-20
  <span className="ml-2 text-slate-400">
    Data Source: SHACL Pilot v{shaclMeta.version} (SHA {shaclMeta.sha.slice(0, 12)})
  </span>
</div>
```

**Data requirement**: `frontend/src/data/shaclMeta.json` must exist with `version`, `sha`, and `timestamp` fields.

**Why this priority (P2)**: Not blocking for UI functionality, but essential for audit traceability — when a user signs a ruleset, they need to know which version they're signing.

---

## Non-Functional Requirements

### NFR-001: Build performance

**Requirement**: `compile_shacl_to_json.py` must complete in <10 seconds on a typical dev machine (M1 Mac, 16 GB RAM).

**Current estimate**: ~5 seconds (9 .ttl files totaling ~50 KB + 1 JSON file ~3.3 MB)

**Rationale**: This script runs at build time, not in the hot path. <10 seconds is acceptable for a pre-frontend-build step.

---

### NFR-002: Frontend bundle size

**Requirement**: Switching from `mockData.ts` (synthetic, ~500 checks) to `shaclChecks.json` (real, 4,167 checks) must not increase the frontend bundle size by >500 KB (gzipped).

**Current mock data size**: ~50 KB (source), ~15 KB (gzipped)  
**Expected SHACL data size**: `shaclChecks.json` ~600 KB (source), ~150 KB (gzipped) — 10x increase in raw size, but only ~135 KB increase gzipped

**Mitigation**: If bundle size becomes an issue, use code-splitting to lazy-load `shaclChecks.json` only when the Route/Block/Check authoring screens are accessed (not on the main Loan Queue screen).

---

### NFR-003: TypeScript type safety

**Requirement**: All SHACL-sourced JSON files must be validated against existing TypeScript interfaces at build time.

**Validation approach**: Add a pre-build step (`scripts/validate_shacl_json_types.ts`) that:
1. Loads `shaclRoutes.json`, `shaclBlocks.json`, `shaclChecks.json`
2. Uses TypeScript's runtime type guards to validate each object matches `Route`, `Block`, `Check` interfaces
3. Fails the build (exit code 1) if any object is malformed

**Rationale**: Catches SHACL-to-JSON compiler bugs at build time, not at runtime in the browser.

---

## Out of Scope

### OOS-001: Real-time SHACL shape editing in the UI

The frontend will display SHACL-sourced checks, but editing them (adding a new check, modifying a SHACL constraint) is out of scope. Checks are authored by editing `.ttl` files directly, re-running `compile_shacl_to_json.py`, and rebuilding the frontend.

**Rationale**: The Import & Sign workflow already assumes checks are authored externally (in the AMQ workbook) and imported. SHACL shapes are the same model — just a different authoring surface (.ttl files instead of .xlsx).

**Future work**: A later feature (not this one) could add a SHACL shape editor in the UI, but that's a P2 or later priority. For now, the Guided Editor surface (Route/Block/Check drill-down) is read-only for SHACL-sourced checks.

---

### OOS-002: Loan evaluation results integration

This feature integrates the **ruleset catalog** (routes/blocks/checks) into the frontend. Integrating **loan evaluation results** (the audit trace from running a loan through the SHACL engine) is a separate feature.

**Current state**: The Apply screen (`ApplyView.tsx`) reads from `MOCK_EVALUATION` (synthetic audit trace). The real SHACL pilot produces audit traces in `src/shacl_pilot/out/loan_NN.json` and markdown reports.

**Future work**: A separate feature (017 or later) will integrate real SHACL audit results into the Apply screen. This feature (016) only handles the ruleset catalog side.

---

### OOS-003: Multi-document field comparison UI (action item #4)

Action item #4 from `docs/frontend/ACTION-ITEMS-2026-07-30.md` (multi-document field validation UI for fields like `purchase_amount` extracted from 3 sources) is out of scope for this feature.

**Rationale**: That's a UX enhancement to the Apply screen, not a SHACL integration task. This feature focuses on making the Route/Block/Check authoring surface work with SHACL-sourced data.

---

### OOS-004: Route DAG diagram (action item #2)

Action item #2 (add a visual DAG diagram to Route Detail) is out of scope for this feature.

**Rationale**: The DAG is a Route Detail screen enhancement, not a SHACL integration dependency. The SHACL pilot's `routes.json` defines blocks as a flat list (no execution-order metadata yet). The DAG can be added later once the SHACL engine gains parallel/sequential execution metadata.

---

## Implementation Plan

### Phase 1: Build-time compiler script (FR-001)

**Owner**: TBD  
**Estimate**: 1 day  
**Deliverables**:
- `scripts/compile_shacl_to_json.py` — Python script, ~200-300 lines
- Unit tests for the script (parse one .ttl file, verify output structure)
- Integration test: run against full SHACL pilot artifacts, verify 4,167 checks emitted
- Documentation: README in `scripts/` directory explaining script usage

**Acceptance**: Script runs successfully on CI, emits valid JSON files, passes TypeScript type validation (NFR-003).

---

### Phase 2: Frontend data adapter swap (FR-002)

**Owner**: TBD  
**Estimate**: 0.5 days  
**Deliverables**:
- Update 5 frontend components to import from `shacl*.json` instead of `mockData.ts`
- Add pre-build validation step (`scripts/validate_shacl_json_types.ts`)
- Update `package.json` scripts: add `"prebuild": "node scripts/validate_shacl_json_types.ts"` before `"build"`

**Acceptance**: `npm run build` succeeds, all Route/Block/Check screens render correctly with SHACL-sourced data, no console errors.

---

### Phase 3: Unmapped check badges (FR-003)

**Owner**: TBD  
**Estimate**: 0.5 days  
**Deliverables**:
- Add `evalClass`-aware badge rendering to `BlockDetail.tsx`
- Disable Edit Check form fields when `evalClass !== "mapped"`
- Add help text explaining each `evalClass` status

**Acceptance**: Navigate to Block Detail, verify unmapped checks show amber `NOT_EVALUATED` badge, Edit Check panel is read-only with explanatory message.

---

### Phase 4: Version banner in Import & Sign (FR-005)

**Owner**: TBD  
**Estimate**: 0.25 days  
**Deliverables**:
- Import `shaclMeta.json` in `ImportAndSignView.tsx`
- Update file-imported banner to display "Data Source: SHACL Pilot v{version} (SHA {sha})"

**Acceptance**: Navigate to Import & Sign, verify banner shows "SHACL Pilot v6 (SHA 9a24f2e9b5c0)" or later.

---

### Phase 5: End-to-end testing

**Owner**: TBD  
**Estimate**: 0.5 days  
**Deliverables**:
- Manual test plan: walk through all Route/Block/Check screens with SHACL-sourced data
- Automated Playwright tests for Route List, Route Detail, Block Detail, Import & Sign screens
- Performance test: measure frontend bundle size increase (verify <500 KB gzipped per NFR-002)

**Acceptance**: All test scenarios from US1-4 pass, no regressions in existing functionality.

---

## Total Estimate

**Total development effort**: 2.75 days (~3 days with buffer)  
**Risk level**: Low (SHACL compatibility already confirmed, no UI component rewrites)

---

## Risks & Mitigations

### Risk 1: SHACL pilot artifacts change structure before this feature ships

**Likelihood**: Medium (SHACL pilot is still experimental, in gitignored `src/`)  
**Impact**: High (would break the compiler script)  
**Mitigation**: 
1. Pin the compiler script to a specific SHACL pilot commit (e.g. "targets SHACL pilot v6, SHA 9a24f2e9b5c0")
2. Add a version check: script reads `shapes_manifest.json`, fails if version < 6
3. If SHACL pilot structure changes significantly, treat it as a new input version (not a bug in this feature)

---

### Risk 2: 4,167 checks cause frontend performance issues

**Likelihood**: Low (React can handle lists of this size with proper virtualization)  
**Impact**: Medium (slow scrolling, high memory usage)  
**Mitigation**: 
1. Use `react-window` or `react-virtualized` for the Available Checks pool in Block Detail (only renders visible checks, not all 4,167 at once)
2. Lazy-load `shaclChecks.json` only when the Block Detail screen is accessed (not on initial page load)
3. If performance is still an issue, add server-side pagination (Block Detail requests checks per block, not all at once)

**Measurement**: Add performance monitoring to Block Detail screen (time-to-interactive, memory usage). If TTI > 2 seconds or memory > 200 MB, implement virtualization.

---

### Risk 3: TypeScript type mismatches between SHACL-sourced data and frontend interfaces

**Likelihood**: Medium (the compiler script is new, might emit wrong types)  
**Impact**: Low (caught at build time by NFR-003 validation step)  
**Mitigation**: 
1. Pre-build type validation (NFR-003) catches mismatches before runtime
2. Add detailed error messages: "shaclChecks.json[42] is missing required field 'severity'" (show which check, which field)
3. Unit tests for the compiler script verify output structure matches TypeScript interfaces

---

## Success Criteria

This feature is successful when:

1. ✅ The frontend can be built and run with SHACL-sourced data instead of `mockData.ts`
2. ✅ All Route/Block/Check screens render correctly with real SHACL-compiled rules (4,167 checks, 9 blocks, 5 routes)
3. ✅ Unmapped checks (4,155 of 4,167) are visually distinguished with `NOT_EVALUATED` or `DOC_PRESENCE` badges
4. ✅ Question-code grouping works (e.g. "Final URLA" groups 9 sibling checks)
5. ✅ The Import & Sign screen displays the SHACL shapes version (e.g. "SHACL Pilot v6, SHA 9a24f2e9b5c0")
6. ✅ Frontend bundle size increase is <500 KB gzipped (NFR-002)
7. ✅ All test scenarios from US1-4 pass

---

## References

- **Compatibility analysis**: `docs/frontend/SHACL-UI-COMPATIBILITY-ANALYSIS.md` (2026-07-30)
- **Frontend action items**: `docs/frontend/ACTION-ITEMS-2026-07-30.md` (meeting transcript review)
- **SHACL pilot audit report**: `src/shacl_pilot/out/full_5loan_audit_latest.md` (100% detection, 25/25 defects)
- **SHACL pilot routes**: `src/shacl_pilot/routes.json`
- **SHACL pilot blocks**: `src/shacl_pilot/blocks/*.ttl` (9 files)
- **SHACL pilot compiled rules**: `src/shacl_pilot/compiled/ruleset.json` (4,167 rules)
- **Frontend mockup**: PR #2, branch `worktree-kayla-mockup`
- **Citation gaps doc**: `output/CITATION-AND-COMPILER-GAPS-2026-07-29.md` (5 backend findings)
