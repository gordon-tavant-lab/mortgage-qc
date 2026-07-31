# Implementation Plan: 019-workbook-first-rule-authoring

**Spec**: `spec.md` (same directory)
**Created**: 2026-07-30
**Status**: Not started

> **Phase 0 gates everything.** Until the audit baseline is restored and its real number recorded, no
> later phase's "did not regress" claim means anything.

---

## Phase 0 · Restore the audit baseline  *(blocks every other phase)*

**Why**: `src/shacl_pilot/out/` holds only `full_5loan_audit_latest.md` and
`green_only_audit_loan01.md`. Every `loan_NN.json` and `loan_NN.ttl` those runs consumed is gone. The
25/25 claim is a report from a past run, not a reproducible fact. If a later change yields 23/25 we
must be able to tell whether we broke two detections or whether it was 23 before we touched anything.

**Steps**

1. For each of `demo/syn/loan 01` … `loan 05`:
   `python3 src/shacl_pilot/extract_loan.py "demo/syn/loan NN" src/shacl_pilot/out/loan_NN.json`
   (the extractor never parses `00_Loan_Summary_And_Answer_Key.pdf` — `ANSWER_KEY_RE` guards it).
2. `python3 src/shacl_pilot/loan_to_rdf.py` for each → `src/shacl_pilot/out/loan_NN.ttl`.
3. `python3 src/shacl_pilot/run_full_ruleset_audit.py <loan_ttl> src/shacl_pilot/compiled/ruleset.json`
   for each loan.
4. **Record the actual detection number** in `specs/019-.../BASELINE.md`, with the per-loan breakdown
   and the shapes-manifest version that produced it.
5. Run twice; confirm byte-identical output (determinism).

**Exit criteria (SC-001)**: `BASELINE.md` exists with a real, dated number. If it is not 25/25, that is
the finding — report it and stop for a scope decision rather than proceeding on a stale premise.

---

## Phase 1 · Ingest the workbook, with authorability verdicts

**New**: `src/shacl_pilot/workbook_ingest.py`

**Reuse (do not reimplement)**: `agency_of()`, `CATEGORY_TO_BLOCK`, and the
`(Question Code, Question Answers Exception Name)` dedup key — all from
`src/shacl_pilot/amq_compiler.py:220-293`. That key is proven: it reproduces 4,167 exactly.

**Steps**

1. Read `demo/rules/PF and PC Sept 2025 AMQs - Retail.xlsx` with `openpyxl`, sheet `Report 1`, header
   on row 4, data from row 5. Keep the real sheet name + row index for `sourceLocator` (FR-001).
2. Filter `Questionnaire Name` contains `Post-Closing` → 5,520 rows.
3. Dedup → 4,546; exclude `Discarded` category → 379; leaving 4,167 rules.
4. Split: blank Exception Code → `affirmative` (797, counted per block); else → `check` (3,370).
5. **Parse `Question Criteria`** → `{program, conditions[]}`. Map `QC_Policy` values:
   `Fannie Mae`→`FNM`, `Freddie Mac`→`FRD`, `FHA`→`FHA`, `VA`→`VA`, `USDA`→`RHS`. Handle the compound
   `AND` forms. Anything else → `gate: null` + `gateRaw`, **listed in full** in the report (FR-004).
6. **Derive the authorability verdict** (FR-005) — the load-bearing step:
   - Load `p0/qc_engine/field_catalog.json` (446 entries) as the extractable-field set.
   - Classify the Exception Description's shape against the six `p0` `Check` kinds.
   - `COMPILABLE` only when a kind is determinable **and** every field it needs is in the catalog.
   - `NEEDS_FIELDS` → record `missingFields[]`. `NEEDS_SME` → judgment language. Otherwise
     `NOT_MECHANIZABLE`.
   - Be conservative: when in doubt, **not** `COMPILABLE`. An over-broad verdict here recreates
     false-clean at the authoring layer.
7. Emit `src/shacl_pilot/compiled/amq_catalog/<block-id>.json` (16 files — `Discarded` excluded) + `index.json` with per-block
   counts, plus a coverage report to `src/shacl_pilot/out/`.
8. Copy the generated catalog to `frontend/src/data/amq_catalog/` (committed — the frontend must not
   depend on gitignored `src/`).

**Do not delete `amq_compiler.py`** until Phase 5 passes the gate.

**Exit criteria**: SC-002 (count assertions), SC-003 (gate-parse report), SC-004 (20 verdicts
hand-checked).

---

## Phase 2 · Frontend types

**Modify**: `frontend/src/lib/types.ts`

1. `Severity` → `"Critical" | "Major" | "Minor"`; add `severityRaw` for the four non-standard values
   (`Material`, `Note`, `Critical-Pending SI`, empty) — FR-006.
2. `CheckStatus`: add `NO_DATA`, `NOT_COMPILED`; **keep `NEEDS_REVIEW`** (real — `run_audit.py:166`
   derives it from `sh:Warning`, and 5 shapes carry `sh:severity sh:Warning`) — FR-007.
3. Extend `Check`: `exceptionCode`, `amqExceptionDescription`, `questionCode`, `questionText`, `aor`,
   `gate`, `gateRaw`, `sourceLocator {sheet, row}`, `authorability`, `authorabilityReason`,
   `missingFields[]`, `compileState`.
4. Update the header comment: these types now mirror the **workbook + SHACL** path, not
   `p0/qc_engine`. (Today lines 1-6 cite `engine.py:46` / `ruleset.py:49` — that provenance is what
   made spec 016's "zero UI changes" claim wrong.)

**Modify**: `frontend/src/data/mockData.ts` — replace `MOCK_CHECKS` / `MOCK_BLOCKS` / `MOCK_ROUTES`
with catalog loaders (lazy, per block). **Keep** `MOCK_LOANS`, `MOCK_EVALUATION`, `MOCK_FINDINGS`,
`MOCK_SOURCE_ALIGNMENT` — loan results are out of scope. Preserving the export names keeps the nine
importing components compiling.

**Exit criteria**: `tsc -b` clean.

---

## Phase 3 · The authoring surface at real scale

**Modify**: `frontend/src/components/BlockDetail.tsx`

The pool filter (`c.category === block.name`, line 44) is correct but yields 714 checks for
Property-Appraisal (704 Product Specific, 616 Income) against 27 mock checks today.

1. **Authorability as the primary axis** (FR-008): default the pool to `COMPILABLE`; show the other
   three bucket counts always. Keep category as the secondary filter.
2. **Collapse `QuestionGroup` only above 50 checks** (FR-009), reusing `groupByQuestion()` (line 190)
   unchanged. Below the threshold keep expanded-by-default and the rationale at lines 50-55 (collapsing
   implies false switch-statement semantics; bulk-activate risks sign-off theatre).
3. Add search over Exception Description / Exception Code / Question Text.
4. Render the parsed gate read-only in the check editor; show `gateRaw` when unparsed.
5. Non-executable checks visually distinct, never green (FR-011). Block header:
   `compilable / total · N affirmative excluded · N need fields`.
6. Empty state for the 7 categories with zero shapes must say *why*, not read as "nothing to configure".
7. Show `amqExceptionDescription` verbatim as the primary label; Question Text as the group caption
   (US2 scenario 4).

**Modify**: `frontend/src/components/RouteDetail.tsx` — Save control (FR-013 / US6).

**Exit criteria**: SC-007 via chrome-devtools MCP against the real screens.

---

## Phase 3b · The Rule Catalog screen (all rules, green/yellow)

**New**: `frontend/src/components/RuleCatalog.tsx` + a `catalog` entry in `lib/nav.ts` and `App.tsx`

Distinct from Phase 3: `BlockDetail` is the *authoring* surface for one block; this is the
*coverage* surface for the whole ruleset — the "what does the tool cover today" screen.

1. Render all **3,369** defect checks with per-block and per-status counts (FR-014). State the counting
   basis: `ruleset.json` reports 3,369 because `amq_compiler.py:301` drops one external-lookup rule that
   a direct workbook read counts as 3,370. One basis, shown once, never two totals on two screens.
2. **Compile state** (FR-015): green `COMPILED` where `eval_class == "mapped"`, yellow `NOT_COMPILED`
   otherwise → **12 / 3,357** today. Green means *the rule has been built* (Gordon, option A), **not**
   that it has fired on a real loan.
3. **Do not reuse the verdict badge** (FR-016). `StatusBadge.tsx` maps emerald to `PASS`/`AUTO_CLEARED`,
   and `RULE-TO-CHECK-UI-MODEL.md:205` mandates `NOT_COMPILED` never be green-as-pass. Use a small
   filled dot on the row **plus the word** `COMPILED` / `NOT COMPILED`. Colour is never the sole carrier
   of meaning — it fails both the false-clean guard and an accessibility review.
4. **Yellow sub-reason from the existing vocabulary** (FR-017): `yellow_blocker_type` — `other` 2,739 ·
   `sme_clarification` 496 · `extraction_gap` 91 · `fixture_gap` 16 · `external_lookup` 15. Where the
   type is `other`, fall back to the authorability reason. No parallel taxonomy.
5. Filters: compile state · authorability · block · severity · program gate. Counts update with the
   filter. Search over Exception Description / Exception Code / Question Text.
6. Surface the **`NOT_COMPILED` + `COMPILABLE`** intersection as its own view — the buildable-but-not-yet
   -built work queue, which is what makes this screen a roadmap tool and not just a status board.
7. Virtualize or group so 3,369 rows stay responsive, loading block files on demand rather than eagerly
   (consistent with FR-012's per-block split).
8. Show the 12 green rules' block concentration honestly (`application-verification` 6,
   `asset-verification` 4, `income-verification` 2) — 13 of 16 blocks have zero, and their empty state
   must read "none compiled yet", not as though the block were empty or done.
9. Note in the UI that 28 shapes are authored but only **4** are reachable via `eval_target`, so
   `COMPILED` is not a claim of end-to-end wiring. Phase 5's reconciliation report closes this gap.

**Exit criteria**: SC-010 (counts match a direct recount), SC-011 (legible in greyscale, no verdict-badge
reuse), SC-012 (yellow reasons reconcile exactly against `ruleset.json`).

---

## Phase 4 · Storage, Save, Export

**New**: `frontend/src/lib/rulesetStore.ts`

Today there is **no persistence at all** — zero matches for `fetch(`, `localStorage`,
`sessionStorage`, `/api` across `frontend/src/`; `RoutesFlow.tsx:24-26` holds everything in `useState`,
so a refresh destroys every edit.

1. Serialize the authored ruleset in the shape of `result/rules/*_ruleset.json`:
   `{content: {checks, engine_version, ruleset_id, version}, sha256, provenance, intent_records,
   signoff_summary}`.
2. Save → `localStorage`, keyed by ruleset id. Handle quota exhaustion with an explicit error directing
   the SME to Export (FR-013).
3. On load, reconcile a stored draft against the current catalog; **report** checks that no longer
   exist rather than failing silently.
4. Export → download the JSON. Document that a human places it at `storage/rules/vN.json` — versioned
   like `storage/fact_vocabulary/v1..v8.json` and `storage/rule_ontology/v1.json`.
5. Label the control a **local draft**. Never imply a server.
6. Wire `RoutesFlow.tsx` to hydrate from the store, and replace `fakeHash()` (line 14) with a real
   digest over the serialized content.

**Note**: `storage/rules/` already exists and is empty. It is **not** `result/rules/` — that holds
compiled/signed engine output; this holds SME-authored input.

**Exit criteria**: SC-009 (activate → Save → reload → persists → Export → compiler accepts).

---

## Phase 5 · The compiler (narrow by design)

**New**: `src/shacl_pilot/ruleset_to_shacl.py`

1. Move the 24 hand-authored shapes to `src/shacl_pilot/blocks/handauthored/` and pass them through
   **untouched**. Their SPARQL is not derivable from a workbook row, and they are what detects real
   defects. Emit a reconciliation report of which now have a workbook row pointing at them (FR-010).
2. Template only the six `p0` `Check` kinds → the plain triple-pattern + `FILTER` form that 20 of the
   28 existing shapes already use. No `UNION` / `BIND` / aggregate generation.
3. Emit `caro:checkId`, `caro:blockRef`, `caro:exceptionRef`, `caro:hasSeverity`,
   `caro:amqQuestionText`, `caro:amqExceptionDescription`, `caro:sourceRow`.
4. **Assert every `caro:exceptionRef` resolves to a real workbook Exception Code** — fail the build
   otherwise. This is the precise defect the 22 broken shapes represent.
5. Fold the parsed gate into the shape's `sh:sparql` as a `FILTER`, so applicability lives *in* the
   compiled artifact rather than being applied outside it.
6. Regenerate `shapes_manifest.json` via the existing `src/shacl_pilot/shape_manifest.py`.
7. Re-run the Phase 0 audit; compare against `BASELINE.md`.

**Exit criteria**: SC-005 (`rdflib` parse + 100% refs resolve), SC-006 (no regression, determinism).

---

## Phase 6 · Correct the misleading docs

Both currently misdirect anyone who reads them as authoritative.

**`docs/frontend/SHACL-UI-COMPATIBILITY-ANALYSIS.md`** — add a superseded-by header, then correct:
"zero UI component changes" (types are p0-shaped, severity enum wrong) · "join key: `exception_code`"
(6 of 28) · "9 blocks" (`routes.json` defines 16; three naming schemes exist) · "1-2 days, risk low".

**`docs/frontend/RULE-TO-CHECK-UI-MODEL.md`** — §7 item 1 claims `NEEDS_REVIEW` does not exist in the
engine; it does (`run_audit.py:166`, from `sh:Warning`, 5 shapes) · §4 lists five verdicts but the
reports use a sixth, `NOT_EVALUATED` · re-point §1's flow to workbook → UI → SHACL · add the
`Question Criteria` finding (resolves §3's `preconditions` TBD and Known Blocker 3) · add the
three-artifact storage model.

**`output/ROADMAP.md`** — add `### 019-workbook-first-rule-authoring` in the house style of the `015`
entry, noting it supersedes `016-shacl-frontend-integration`. Leave the `016`/`017`/`018` reservations
at lines 482/489/498 intact.

**Exit criteria**: `grep -rn "016-shacl-frontend-integration"` returns only intentional
"superseded by" references.

---

## Sequencing

```
Phase 0 (baseline)  ──►  everything
Phase 1 (ingest)    ──►  Phase 2  ──►  Phase 3  (authoring, one block)
                                  ├──►  Phase 3b (catalog, all rules)
                                  └──►  Phase 4  (storage)
Phase 1 ────────────────────────────►  Phase 5  ──►  re-verify vs BASELINE.md
Phase 6  (any time after 1; do last so corrections reflect what was built)
```

Phases 3, 3b, and 4 are independent after Phase 2 and can proceed in parallel. **Phase 3b is the
demo-visible one** — it is the screen that answers "what does this cover today," so if time is short it
outranks Phase 3's per-block refinements.

## Risks

| Risk | Mitigation |
|---|---|
| Phase 0 does not reproduce 25/25 | Record the real number and stop for a scope decision. Do not build on a stale premise. |
| Authorability verdict too permissive | SC-004's 20-item hand check; bias toward not-`COMPILABLE` when uncertain. |
| Catalog bloats the bundle | Per-block split + lazy load (FR-012); SC-008 measures it. |
| Compiler breaks a hand-authored shape | They are passed through untouched, never regenerated (FR-010). |
| `localStorage` quota exceeded | Explicit error + Export path (FR-013). |
| Gate parser silently mis-reads a predicate | Unparsed → `gateRaw`, listed in full (FR-004, SC-003). Never guess. |
