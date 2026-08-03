# Feature Specification: Workbook-First Rule Authoring (AMQ Post-Closing → UI → SHACL)

**Feature Branch**: `019-workbook-first-rule-authoring`
**Created**: 2026-07-30
**Status**: Draft — approved for implementation, not yet built

**Input**: Gordon reviewed the frontend work queued by `docs/frontend/ACTION-ITEMS-2026-07-30.md` and
`docs/frontend/SHACL-UI-COMPATIBILITY-ANALYSIS.md`, then proposed inverting the data flow: *"we should
tailor the screen to just accommodate the rules from `demo/rules/PF and PC Sept 2025 AMQs -
Retail.xlsx` (only the post-close rules) in the ui, and the ui rules will compile into the SHACL."* He
asked for a researched, definitive answer before implementing. Investigation confirmed the direction
is correct **and** found that the previously-specced direction (`016-shacl-frontend-integration`) rests
on a join that does not work. Gordon then asked the question that exposed a real hole in the first
draft of this spec — *"where do we store the rules to load on to the screen, are we loading the screen
from the SHACL? or do we need another storage for them?"* — resolved here as an explicit three-artifact
model, with the SME-authored ruleset stored at **`storage/rules/vN.json`** (his call, 2026-07-30).

**Governs**: `output/ROADMAP.md` (new entry), `docs/frontend/RULE-TO-CHECK-UI-MODEL.md`,
`docs/frontend/SHACL-UI-COMPATIBILITY-ANALYSIS.md` (both corrected by this spec).
**Depends on**: `010a-program-applicability-gating` (the program-gating this spec's `Question Criteria`
parse feeds — and whose Known Blocker 3 it resolves), `009b-guided-structured-editor` (the authoring
surface this extends), `000-synthetic-fixture-generation` (the fixtures + 25/25 defect gate Phase 0
must restore and every later phase must keep passing).
**Supersedes**: `016-shacl-frontend-integration` (removed by this spec — see *Why spec 016 is retired*).

---

## Why this feature exists

Three real problems, one of which is a live correctness defect.

### 1 · The previously-specced data direction does not work

`016-shacl-frontend-integration` had the frontend **read** hand-authored `.ttl` shapes and back-fill
AMQ metadata onto them, joining on `exception_code`. Measured against the actual artifacts:

- Of the **28** shapes carrying `caro:checkId`, only **6** have a `caro:exceptionRef` that resolves to
  a real `exception_code` in `ruleset.json`. The other 22 carry invented slugs —
  `"FHA-Case-Number-Mismatch"`, `"CD-Payoff-Reconciliation"`, `"USDA-Well-Septic"` — that exist in no
  workbook. The engine's own link (`eval_target` → shape name) reaches only **4**.
- Two shapes claim the same code (`CHK-AST-003` and `CHK-AST-004` both assert `Asset-1`), so the join
  is not 1:1 even where it resolves.
- **24 of 28 shapes have no AMQ rule pointing at them at all.**

Reading `.ttl` as the spine makes a hand-authored engineering artifact authoritative and the SME a
spectator over it — the opposite of Non-Negotiable #4 ("configurable by non-technical users"). Compiling
**to** `.ttl` makes the workbook authoritative and the SME the author, which is precisely the
"compile, then run" pattern of Non-Negotiable #1 with the UI as the sign-off gate.

### 2 · The workbook already contains the program gate this project calls an open blocker

`Question Criteria` (column 8 of the AMQ workbook) holds machine-readable SQL applicability gates:

```sql
SELECT DISTINCT Loans.LoanID FROM Loans WHERE (Loans.QC_Policy = 'Fannie Mae')
SELECT DISTINCT Loans.LoanID FROM Loans WHERE Loans.QC_Policy = 'FHA'
    AND Loans.Underwriting_Type = 'Manually Underwritten'
SELECT DISTINCT Loans.LoanID FROM Loans WHERE Loans.QC_Policy = 'Freddie Mac'
    AND Loans.PropertyType = 'Condominium'
```

Populated on **5,201 of 5,520** post-close rows (94%), with only **80 distinct predicates** over a
closed 8-field vocabulary: `QC_Policy` (5,064) · `PropertyType` (372) · `Underwriting_Type` (247) ·
`ARMCO_OriginalLoanNumber`/`LoanNumber` (97) · `LoanType` (97) · `LoanPurposeType` (85) · `Occupancy`
(52) · `OriginalLTVRatioPercent` (11) · `AddressState` (3).

`src/shacl_pilot/amq_compiler.py` reads nine columns (lines 289-322) and **this is not among them** —
even though the column *is* present in the CSV it reads (column 8 of 14). A dropped field, not a
missing export.

This is the applicability data `RULE-TO-CHECK-UI-MODEL.md` §3 specifies as `program` / `loanType` /
`preconditions`, and that **Known Blocker 3** ("rule-to-program mapping unknown — for now assume all
rules apply, gate by product/program later") treats as unsolved. Because every gate traces to a
workbook cell, using it satisfies the grounding discipline in Non-Negotiable #1: no threshold,
percentage, or condition originates anywhere but the source row.

### 3 · The authoring UI can reproduce the false-clean bug one layer upstream

This project has already been bitten once by false-clean at the *results* layer: SHACL
`conforms=True` was reported as a pass when checks had in fact not evaluated, which is why the
four-verdict split (`PASS` / `FAIL` / `NOT_APPLICABLE` / `NO_DATA`) exists.

The same defect can reappear at the *authoring* layer, and today's UI would not prevent it. The
available-checks pool (`frontend/src/components/BlockDetail.tsx:44`) filters only on
`c.category === block.name`. Nothing distinguishes a check that can execute from one that cannot. An
SME could activate 40 checks, see "40 wired", and sign off believing they have 40 checks of coverage —
when most resolve `NO_DATA` on every loan forever because the fields they read are not extracted.
`CHK-AST-003` is exactly this case: `RULE-TO-CHECK-UI-MODEL.md` §6 documents it returning `NO_DATA` on
loan 12607601215 because two bank statements are classified but no transactions are extracted from
them.

The binding constraint is the field vocabulary, and it is roughly **50× smaller** than the rule
catalog:

| Artifact | Size |
|---|---|
| Defect checks in the post-close workbook | **3,370** |
| `p0/qc_engine/field_catalog.json` entries | **446** |
| `li:` predicates used by all 28 SHACL shapes | **67** |

No UI improvement closes that gap — extraction is explicitly not ours to build (Non-Negotiable #2,
Touchless owns the contract). What the UI *can* do is refuse to hide it.

### Why spec 016 is retired rather than amended

Beyond the broken join, `016`'s stated conclusions are wrong in four independently-verifiable ways:

| 016 claim | Reality |
|---|---|
| "zero UI component changes required" | `frontend/src/lib/types.ts:1-6` explicitly mirrors `p0/qc_engine/engine.py:46` and declares `Severity = "CRITICAL"｜"WARNING"｜"INFO"`. AMQ emits `Critical`/`Major`/`Minor` — every severity badge is wrong. |
| "join key: `exception_code`" | Resolves for 6 of 28 shapes. |
| "9 .ttl files → 9 blocks" | `routes.json` defines **16** catalog blocks; the `.ttl` files use a third naming scheme (`application` vs `application-verification` vs the UI's `Application`). |
| "1-2 days, risk low" | Understated: the type model, the severity enum, the status vocabulary, the pool scale, and the storage layer all need work. |

It also occupies a reserved number: `output/ROADMAP.md:482` already reserves
`016-fibo-ontology-alignment`, `:489` reserves `017-precondition-completeness-loan-product-portfolio`,
and `:498` reserves `018-set-membership-check-kind`. Spec 016 was written into an occupied slot. This
spec takes **019**, the next free number. Spec 016 was never merged to `main`, so retiring it reverts
nothing.

---

## 2026-08-01 Rework: retarget onto the gold ruleset (Pipeline B), not Pipeline A

This spec's original Phase 1 (`src/shacl_pilot/workbook_ingest.py`) and Phase 5
(`src/shacl_pilot/ruleset_to_shacl.py`, as originally scoped — a workbook-row →
hand-templated-`.ttl` compiler) are **retired**, same rigor as spec 016's retirement above — a table
of premise vs. verified reality, not a vibe:

| Original premise | Reality, verified 2026-07-31/08-01 |
|---|---|
| The frontend needs to move onto Pipeline A / SHACL because it currently mirrors Pipeline B | `grep -rn "shacl_pilot" frontend/src` → **0 hits, ever.** The frontend was never wired to Pipeline A at any point in its history. The premise that it *needs to move* rests on nothing the frontend actually does. |
| `frontend/src/lib/types.ts` "now mirror the workbook + SHACL path, not `p0/qc_engine`" (original Phase 2) | `types.ts` lines 1-6 **still** say "mirrors p0/qc_engine's real classes," unchanged, correctly. This spec's own Phase 2 plan was written to invert a provenance that was never actually pointed at Pipeline A. |
| Re-ingest the workbook ourselves (`workbook_ingest.py`) to build an authoring catalog | `storage/rules/gold/` already did this job, from the same source workbook (`amqs-sept-2025-retail.xlsx`), at materially higher fidelity: 266 cards / 1,111 defect options / 221 atomic rules, each Selling-Guide-cited against a 390-section validated index, LLM-compiled then deterministically gated — not a second, parallel, hand-derived-verdict pipeline. Constitution v1.2.0 Principle VII (ratified 2026-07-31) already states this: checks/blocks/routes are authored against the gold ruleset, not re-derived ad hoc by a parallel pipeline. |
| Compile to `.ttl` via a new narrow `ruleset_to_shacl.py`, asserting every `caro:exceptionRef` resolves | Gordon's engine decision (2026-08-01): the rule-author page needs no engine decision at all — `Check`'s fields (`kind`/`operator`/`threshold`/`ratio`/`severity`/`appliesIf`/`grounding`) describe rule logic in the abstract; a `frontend/scripts/build_gold_catalog.py` mapper produces a real `Check[]` directly from gold's own schema, independent of whether Pipeline A or Pipeline B (still an open, separately-tracked bake-off) ends up executing audits later. |
| Phase 0's baseline (4/20,830 rule-loan pairs on `demo/syn/loan 01-05`) is the regression floor future phases compare against | Decision 031 (2026-07-31) already supersedes this — the demo/audit target moved to the Touchless loan. `BASELINE.md` stands as historical rationale for why Pipeline A's synthetic-fixture pipeline doesn't generalize, not a floor this spec's phases build against. |

**Not retired**: this spec's actual problem statements — the broken 016 join (§1 above), the
program-gate finding (§2 above), and the false-clean-at-authoring-layer risk (§3 above) — and the
authorability concept (`COMPILABLE`/`NEEDS_FIELDS`/`NEEDS_SME`/`NOT_MECHANIZABLE`, FR-005) and the
Rule Catalog screen concept (User Story 7). These are **re-platformed onto the gold ruleset**, not
dropped — see the revised Phase plan in `plan.md` and decision
[032](../../src/decisions/032-spec019-rework-onto-gold-ruleset.md).

**Program scope, decided 2026-08-01**: gold's checks are all sourced from Fannie Mae (FNM)
specifically (`storage/rules/gold/README.md`: "Only the FNM route is populated"). Gordon's call: the
UI does not differentiate Fannie vs. Freddie at all. Routes map to `CLAUDE.md`'s two-way AMQ program
grouping only — **Conventional** (FNM + FRD combined, no sub-split, shows the real gold-sourced
checks) and **Government** (FHA + VA + RHS combined, no sub-split, same block structure, genuinely
zero checks). This supersedes this spec's original assumption of a single implicit program scope.

This spec keeps its number (019) — this is a rework, not a new spec, same convention 019 itself used
against 016.

---

## The storage model — three artifacts, three jobs

> ⚠️ **Superseded 2026-08-01** (see rework section above): this section describes Pipeline A's
> workbook→catalog→`storage/rules/vN.json`→`.ttl` flow, which is retired for the authoring UI's
> catalog source. `storage/rules/gold/` + `frontend/scripts/build_gold_catalog.py` replace Phase 1's
> role; a signed `storage/rules/vN.json` (Phase 7/rulesetStore.ts) and the gold-isolation guard
> remain valid and unchanged — those parts of this section still apply.

**The screen does not load from SHACL.** SHACL is a *compiled output*, downstream of authoring; loading
the UI from `.ttl` is the inverted direction §1 rejects. Conflating any two of these artifacts is a
design error:

| # | Artifact | Written by | Read by | Role |
|---|---|---|---|---|
| 1 | `amq_catalog.json` (per-block split) | `workbook_ingest.py` | **the UI, at load** | **The catalog.** All 3,370 post-close checks + 16 blocks + parsed gates + authorability verdicts. Read-only; regenerated from the workbook. (16, not 17: `Discarded` is a real Question Category Name but is excluded.) |
| 2 | `storage/rules/vN.json` | the SME, via Save/Export | `ruleset_to_shacl.py` | **The SME's decisions.** Which checks are active in which block/route, plus edits and sign-off. |
| 3 | `src/shacl_pilot/blocks/*.ttl` | `ruleset_to_shacl.py` | the SHACL engine | **The compiled artifact.** A build output. Never read by the UI. |

**Flow:** workbook → catalog → UI authoring → `storage/rules/vN.json` → compile → `.ttl` → engine.

`storage/rules/` (Gordon's call, 2026-07-30) already exists and is empty. It sits beside
`storage/fact_vocabulary/`, `storage/rule_ontology/`, `storage/loan_profiles/`, and
`storage/knowledge_base/`, so the authored ruleset joins the project's existing versioned-artifact
convention — `v1.json`, `v2.json`, … exactly as `fact_vocabulary/v1..v8.json` and
`rule_ontology/v1.json` already do. It is **distinct from `result/rules/`**, which holds
compiled/signed *engine* rulesets; `storage/rules/` holds the SME-authored *input* that produces them.

**`storage/rules/gold/` is a separate, read-only sibling — never a Save/Export target (added
2026-07-31, one day after this spec was written).** It holds a separately-sourced, pre-compiled
FNM-conventional reference ruleset (266 cards / 1,106 checks, Selling-Guide-cited), relocated there
by Gordon *specifically* to keep the `storage/rules/` root free for this spec's `vN.json` output
(see `GOLD-RULESET-INTEGRATION-PLAN-2026-07-31.md`). It is reference/ground-truth material, not an
SME draft. **Save/Export logic (Phase 4) MUST NOT read from, write to, or delete anything under
`storage/rules/gold/`** — it is scoped to the `storage/rules/` root only.

### What Save can honestly do today

The frontend has **no persistence whatsoever**: `fetch(`, `localStorage`, `sessionStorage`, `axios`,
and `/api` all return zero matches across `frontend/src/`, and `vite.config.ts` is a static dev server
with no proxy. All editable state is in-memory React state — `RoutesFlow.tsx:24-26` does
`useState(() => structuredClone(MOCK_ROUTES))` for routes, blocks, and checks. **A browser refresh
destroys every edit.** That is a real defect in the current mockup, not merely a missing feature.

Building a backend is out of scope. So Save is `localStorage` (draft durability) plus an explicit
**Export** of the ruleset JSON, which a human places at `storage/rules/vN.json`. The UI must label this
a local draft and never imply a server exists.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — An SME sees only checks that can actually run, and an honest count of what cannot (Priority: P1)

A QC analyst opens the **Assets** block to configure it. The available-checks pool defaults to checks
that are genuinely executable. Alongside it, the header states how many checks in this block are *not*
executable and why — so coverage is never overstated.

**Why this priority**: this is the false-clean guard. Without it the authoring surface can manufacture
the exact defect the four-verdict results model was built to eliminate.

**Acceptance Scenarios**

1. **Given** the Assets block (**81 gold-sourced checks**, updated 2026-08-01 — was "304 workbook
   rows" under the retired workbook-ingestion plan), **When** the SME opens it, **Then** the pool
   shows only `COMPILABLE` checks by default (80 of 81 — Assets is one of only two blocks with any
   decomposed, field-resolved checks today, the other being Income), and the header shows counts for
   `NEEDS_FIELDS`, `NEEDS_SME`, and `NOT_MECHANIZABLE`.
2. **Given** a check whose evidence field hasn't resolved (i.e. its parent gold card hasn't been
   decomposed to atomic-rule granularity — true for 14 of 16 blocks today), **When** the SME inspects
   it, **Then** it is labelled `NEEDS_FIELDS` with that reason stated.
3. **Given** a check with judgment language ("acceptable", "as required"), **When** displayed,
   **Then** it is labelled `NEEDS_SME` with that reason stated — not offered as a pass/fail gate.
4. **Given** any non-`COMPILABLE` check, **When** rendered anywhere, **Then** it is visually distinct
   from a passing/active check and never green.

---

### User Story 2 — Every check traces to its workbook row (Priority: P1)

A reviewer (or auditor) inspects any check and can see exactly which AMQ row it came from, with the
rule text verbatim.

**Why this priority**: the audit trail is the product's core claim ("if they don't understand how you
calculated that number, you buy back the loan").

**Acceptance Scenarios**

1. **Given** any check, **When** the SME opens its detail view, **Then** category, Exception Code
   (`name`), description, and AOR are all shown, sourced from the gold ruleset.
2. **Given** a check's description, **When** displayed, **Then** it appears **verbatim** — no
   paraphrase, no truncation in the detail view.
3. **Given** any check, **When** inspected, **Then** its `sourceLocator` shows `{ruleId, cardId}` —
   **updated 2026-08-01**: gold has no workbook sheet/row to show; `ruleId`/`cardId` are its stable,
   traceable IDs instead (an atomic rule ID like `FNM-AST-0001` when decomposed, else a synthesized
   `${cardId}#${index}`).
4. **Given** the Exception Description and the Question Text, **When** both are shown, **Then** the
   Exception Description is the primary label and the Question Text the grouping caption — never the
   reverse (a Question Text like "Were all self-employed requirements met?" is a vague header shared by
   dozens of distinct tests).

---

### User Story 3 — RETIRED 2026-08-01, see rework section

*Original: "A signed check compiles to a valid shape, and detection does not regress" — assumed a
custom `ruleset_to_shacl.py` compile step in the authoring UI's own path. No such compiler exists
here; gold's checks are already compiled (LLM-compiled + deterministically gated, upstream of this
UI). Whether a signed export later "compiles to a valid shape" for some runtime engine is a Phase
6-8 concern (deferred, not blocking), not something the rule-author page itself does or needs to
prove.*

---

### User Story 4 — An SME's work survives a refresh and exports as the compiler's input (Priority: P1)

The SME activates checks across several blocks, saves, accidentally reloads the browser, and finds the
work intact. When ready, they export the ruleset file.

**Why this priority**: today a refresh silently destroys everything
(`RoutesFlow.tsx:24-26`). An authoring tool that loses work is not usable for the 800+-check
configuration job this product exists to do.

**Acceptance Scenarios**

1. **Given** activated checks and edits, **When** the SME clicks Save and reloads the page, **Then**
   every activation and edit is restored.
2. **Given** saved work, **When** the SME clicks Export, **Then** a ruleset JSON downloads shaped like
   `result/rules/*_ruleset.json` (`{content, sha256, provenance, signoff_summary}`).
3. **Given** that exported file, **When** placed at `storage/rules/v1.json`, **Then** it is a valid,
   parseable ruleset JSON. *(Updated 2026-08-01: "accepted by `ruleset_to_shacl.py`, compiles to
   `.ttl`" is dropped — no compiler in this spec's path consumes the export; see US3.)*
4. **Given** the Save affordance, **When** displayed, **Then** it is labelled a local draft — the UI
   never implies a server-side save.

---

### User Story 5 — Applicability comes from the workbook, and unparsed gates are shown as unparsed (Priority: P2)

**Acceptance Scenarios**

1. **Given** a check whose `Question Criteria` is `WHERE (Loans.QC_Policy = 'Fannie Mae')`, **When**
   inspected, **Then** its gate displays as program FNM, read-only.
2. **Given** a compound criterion (`QC_Policy = 'FHA' AND Underwriting_Type = 'Manually
   Underwritten'`), **When** inspected, **Then** both conditions are shown.
3. **Given** a criterion the parser cannot interpret, **When** inspected, **Then** the raw SQL is shown
   as unparsed — never silently dropped and never guessed at.

---

### User Story 6 — Save is reachable from the screens where work happens (Priority: P2)

**Acceptance Scenarios**

1. **Given** the Route Detail screen, **When** the SME changes block membership, **Then** a Save
   control is present and reflects unsaved state.
2. **Given** the Block Detail screen, **When** the SME activates or edits a check, **Then** the same
   holds.

---

### User Story 7 — Every rule is on screen, with green/yellow showing what is built (Priority: P1)

Gordon (or a client in a demo) opens a catalog-wide Rule Catalog screen and sees **all 1,105**
gold-sourced checks at once (**updated 2026-08-01** — was "3,369 post-close rules" under the retired
workbook-ingestion plan) — not just the ones scoped to a single Block. Each row carries a green or
yellow indicator: green where a real evidence field resolved, yellow where it hasn't yet. Headline
counts sit at the top, and yellow rows can be grouped by *why* they are not built.

**Why this priority**: this is the coverage story — unchanged. It answers "what does the tool cover
today, and what is left?" in one screen, and is the honest counterweight to a padded coverage claim.

**Acceptance Scenarios**

1. **Given** `goldCatalog.json`, **When** the SME opens the Rule Catalog, **Then** the header shows
   **208 compiled / 897 not compiled** out of 1,105 total, with the counting basis stated.
2. **Given** any rule row, **When** rendered, **Then** its compile state is shown as a distinct visual
   indicator **plus the word** `COMPILED` or `NOT COMPILED` — never colour alone, and never the same
   pill-shaped badge used for loan verdicts.
3. **Given** a `NOT_COMPILED` rule, **When** the SME inspects it, **Then** the reason is shown from
   `authorabilityReason` (**updated 2026-08-01** — not `yellow_blocker_type`, which has no equivalent
   on gold cards): 642 `NEEDS_FIELDS`, 108 `NOT_MECHANIZABLE`, 147 `NEEDS_SME`.
4. **Given** the catalog, **When** the SME filters, **Then** compile state, authorability, block,
   severity, and Route all work as filters, and counts update to match the filtered set.
5. **Given** the 208 compiled rules, **When** grouped by block, **Then** they concentrate almost
   entirely in **Assets** (80) and **Income** (128) — the only two categories decomposed to
   atomic-rule granularity so far — making the concentration visible rather than implying even
   coverage across all 16 blocks.
6. **Given** 1,105 rows, **When** the screen renders and is scrolled, **Then** it stays responsive —
   **re-verify whether virtualization is still needed** at this smaller scale (was sized against the
   old 3,369-row catalog) before building it.

---

### Edge Cases

> ⚠️ **Updated 2026-08-01**: counts below are gold-derived (`goldCatalog.json`), replacing the retired
> workbook-derived numbers. Two edge cases below were found only after implementation began — see the
> last two entries.

- **A block with more checks than fit on screen.** Product Specific has **195** checks (the largest
  block; Property-Appraisal 184, Income 140) — small enough that question-code grouping / 50-check
  collapse (FR-009) may not even be needed in practice; re-verify against the real UI before assuming
  it's load-bearing (was sized against a 714-check block under the retired plan).
- **A block with zero `COMPILABLE` checks.** **14 of 16** blocks have zero decomposed (field-resolved)
  checks today — only **Assets** (80/81) and **Income** (128/140) have been decomposed to atomic-rule
  granularity. The empty/near-empty state must say why (not yet decomposed), not read as "nothing to
  configure".
- **Non-standard severities.** Gold's `severity` enum includes `Critical`, `Critical-Pending SI`,
  `Major`, `Minor`, `Note` — mapped to the frontend's `CRITICAL`/`WARNING`/`INFO` inside the mapper
  (`Critical`/`Critical-Pending SI`→`CRITICAL`, `Major`→`WARNING`, `Minor`/`Note`→`INFO`).
- **A `localStorage` draft written against a stale catalog.** Checks referenced by a saved draft may no
  longer exist after `goldCatalog.json` is regenerated (e.g. more cards decomposed, gold ruleset
  updated).
- **`localStorage` quota.** A large authored ruleset may exceed the ~5 MB browser limit.
- **A green rule that has never been run.** `COMPILED` means a real evidence field resolved, not that
  it has fired on any loan or been proven correct against real data. All 208 are in this state.
- **A whole block with zero green rules.** 14 of 16 blocks have none, as above. The empty state must
  say "not yet decomposed" rather than rendering as though the block is empty or complete.
- **Colour-blind and greyscale viewing.** Green/yellow are indistinguishable to some viewers and in
  printed demo handouts, which is why FR-016 requires the word alongside the colour.
- **Government blocks share a category name with their Conventional counterpart, but must show zero
  available checks** *(found during implementation, 2026-08-01)*: `Check.category` is plain AMQ
  category text, not Route-scoped, so a naive filter would let an SME wire a Fannie-sourced check into
  a Government block. Fixed with an explicit `block.id` prefix guard (`conv-`/`gov-`) in
  `BlockDetail.tsx`.
- **A Route's "available blocks" pool must not include the other Route's same-category block**
  *(found during implementation, 2026-08-01, via Gordon's own review of the running app)*: the same
  root cause one level up — `RouteDetail.tsx`'s available/active block pools must be scoped to the
  current Route's own id prefix, or Government's blocks appear as confusing "available" duplicates on
  Conventional's screen and vice versa.

---

## Requirements *(mandatory)*

### Functional Requirements

> ⚠️ **2026-08-01**: FR-001, FR-002, FR-003, FR-006, and FR-010 below are **RETIRED** — they describe
> the workbook-re-ingestion pipeline and custom SHACL compiler this spec's rework section retires.
> FR-007, FR-012, FR-014, FR-015, FR-016, FR-017 are **updated in place** below to reflect what was
> actually built (`frontend/scripts/build_gold_catalog.py` → `goldCatalog.json`). FR-004, FR-005,
> FR-008, FR-009, FR-011, FR-013 are **unchanged in substance** — their concept survives, only their
> data source moved from a workbook re-parse to the gold ruleset.

- **FR-001** *(RETIRED — see rework)*: ~~`src/shacl_pilot/workbook_ingest.py` reads the workbook
  directly via `openpyxl`~~. No workbook-re-ingestion script exists or is planned; the catalog comes
  from `storage/rules/gold/` via `build_gold_catalog.py`.
- **FR-002** *(RETIRED — see rework)*: ~~filter on `Questionnaire Name` containing `Post-Closing`,
  reproduce workbook-derived counts~~. Gold's own build already scoped to Post-Closing, Fannie-cut
  (`storage/rules/gold/README.md`); this spec does not re-derive that scoping.
- **FR-003** *(RETIRED — see rework)*: ~~797 affirmative rows (blank Exception Code) excluded and
  counted per block~~. Gold's schema requires every `defect_option`/`atomicRule` to carry a
  `finding.exception_code` — there is no blank-Exception-Code "affirmative" row concept in gold's data
  model to exclude.
- **FR-004**: `appliesIf` (the precondition gate) MUST come from a structured source, never guessed.
  **Source changed**: gold's own `applicability` field (`{always, all_of[], any_of[], source_sql}`,
  structurally equivalent to the original `{program, conditions[]}` target) is already
  machine-readable — `build_gold_catalog.py`'s `map_applies_if()` maps it directly. An unparseable or
  absent applicability MUST NOT be guessed at.
- **FR-005**: Every check MUST carry a derived **authorability verdict** with its reason: `COMPILABLE`
  (a real evidence field resolved — an atomic rule's `evidence[0].field`/`.name`) · `NEEDS_FIELDS`
  (kind clear, no evidence resolved yet — the card hasn't been decomposed to atomic-rule granularity) ·
  `NEEDS_SME` (`scripted_review` check_type, judgment language by design) · `NOT_MECHANIZABLE`
  (`date_window`/`list_screening`/`reverification`/`routing_context`, or an unrecognized check_type).
  **Source changed**: derived from gold's own `check_type` + evidence resolution
  (`build_gold_catalog.py`), not from re-parsing AMQ rows against `field_catalog.json` from scratch —
  conservative by design either way; caught and fixed one false-clean bug during implementation (see
  `plan.md` Phase 1).
- **FR-006** *(RETIRED — see rework)*: ~~`Severity` becomes `"Critical" | "Major" | "Minor"` with a
  `severityRaw` field~~. Not built — Phase 2 kept `Severity = "CRITICAL" | "WARNING" | "INFO"`
  unchanged (it already matched `p0/qc_engine`, which was never actually wrong) and maps gold's raw
  severity strings (`Critical`/`Major`/`Minor`/etc.) to it inside the mapper, at build time, not as a
  frontend type field.
- **FR-007** *(updated)*: `CheckStatus` MUST add `NOT_COMPILED` and MUST **keep** `NEEDS_REVIEW`. **Do
  NOT add `NO_DATA`** — that is a Pipeline-A-specific (pyshacl) concept the frontend's actual data
  model (Pipeline B-shaped, unrelated to which engine ultimately executes audits) does not produce;
  adding it would reintroduce a status the real `CheckResult` never emits. *(Original FR-007 required
  both `NO_DATA` and `NOT_COMPILED` — corrected here to match what Phase 2 actually built and why.)*
- **FR-008**: `BlockDetail.tsx`'s available-checks pool MUST default its primary axis to
  **authorability**, not category, with the counts of the other three buckets always visible. Category
  scoping (`c.category === block.name`) MUST remain as the secondary filter. **Also required, found
  during implementation, not in the original FR text**: this scoping MUST additionally respect which
  Route the block belongs to (Conventional vs. Government) — category name alone is not sufficient,
  since both Routes share category names but only Conventional has real checks (see Edge Cases).
- **FR-009**: `QuestionGroup` MUST collapse by default **only** when a block exceeds 50 checks,
  reusing `groupByQuestion()` unchanged. Below that threshold, expanded-by-default behaviour holds
  (collapsing implies false switch-statement semantics and risks sign-off theatre). A search control
  over check name, description, and question text MUST be present.
- **FR-010** *(RETIRED — see rework)*: ~~`src/shacl_pilot/ruleset_to_shacl.py` templates the six `p0`
  `Check` kinds and asserts every emitted `caro:exceptionRef` resolves~~. No custom SHACL compiler is
  in the authoring UI's path. The UI needs a `Check[]`, not `.ttl` — `build_gold_catalog.py` produces
  that directly.
- **FR-011**: `NOT_COMPILED` MUST be visually distinct from `PASS` and never green; block headers MUST
  show `compilable / total` plus how many checks are not yet buildable, per `authorabilityReason`.
- **FR-012** *(updated)*: The UI loads `goldCatalog.json` (read-only, generated by
  `build_gold_catalog.py` from `storage/rules/gold/`, committed under `frontend/src/data/`) — **not**
  `amq_catalog.json`, and **not** by reading `.ttl`. Save (Phase 5) persists to `storage/rules/vN.json`
  (SME decisions), kept separate from the read-only catalog and from `storage/rules/gold/` itself
  (gold-isolation guard, unchanged — see FR-013).
- **FR-013**: Save MUST persist to `localStorage` so a refresh does not destroy work, and MUST offer
  **Export** of a ruleset JSON (`{content, sha256, provenance, signoff_summary}`), destined for
  `storage/rules/vN.json` — versioned `vN.json` exactly as `storage/fact_vocabulary/v1..v8.json` does.
  The UI MUST label this a local draft and MUST NOT imply a server. A draft referencing checks absent
  from the current catalog MUST report them rather than fail silently, and exceeding the `localStorage`
  quota MUST surface an explicit error directing the SME to Export. **Export MUST target only
  `storage/rules/vN.json` at the `storage/rules/` root and MUST NOT read, write, or delete anything
  under `storage/rules/gold/`.**
- **FR-014** *(updated)*: **Every rule MUST be visible on a catalog-wide screen**, not only the checks
  scoped to one Block. All **1,105** checks (from `goldCatalog.json`, not the retired `ruleset.json`'s
  3,369) MUST be reachable and countable in one place, with per-block, per-status, and per-Route
  totals. The catalog MUST state which basis it counts on.
- **FR-015** *(updated)*: Each rule MUST carry a **compile state** — `COMPILED` (green, 208 checks
  today) when `authorability === "COMPILABLE"`, `NOT_COMPILED` (yellow, 897) otherwise. Green asserts
  *"a real evidence field resolved,"* not *"proven to fire on a real loan."* The screen MUST NOT imply
  the stronger claim.
- **FR-016**: **Compile state MUST NOT reuse the verdict colour language.** `StatusBadge.tsx` maps
  emerald to `PASS`/`AUTO_CLEARED` — a loan *passed*. Compile state is a different axis (is the rule
  built), styled distinctly (dashed border, muted color, never green — built in Phase 2/3) and always
  paired with the word `COMPILED`/`NOT COMPILED`, never colour alone.
- **FR-017** *(updated)*: The yellow sub-reason MUST come from `authorabilityReason` (derived from
  gold's own `check_type` and `compile.failure_category`), **not** `yellow_blocker_type` — that
  vocabulary lives on the retired `ruleset.json` and has no equivalent on gold cards. Compile state
  answers *"is it built?"*; authorability answers *"can it be built?"* — a rule can be `NOT_COMPILED`
  **and** `COMPILABLE` isn't possible under the new derivation (compile state now equals authorability
  directly — see Key Entities), which simplifies the original FR-017's two-axis framing; the
  buildable-but-not-yet-built work queue is now just `NEEDS_FIELDS` filtered to check_types with a
  plausible near-term fix.

### Key Entities

- **`goldCatalog.json`** (new; generated by `frontend/scripts/build_gold_catalog.py`, committed under
  `frontend/src/data/`): the read-only authoring catalog — 16 blocks × two Routes (Conventional real,
  Government empty), 1,105 checks, each with gold provenance (`ruleId`/`cardId`), applicability, and
  authorability verdict. **Replaces** the originally-planned `amq_catalog.json`.
- **`storage/rules/vN.json`** (new; SME-written, versioned, not yet built — Phase 5): activations per
  block/route, per-check edits, and sign-off. Lives at the `storage/rules/` root — **not** in
  `storage/rules/gold/`, a sibling subdirectory holding a separate, read-only reference ruleset that
  is out of scope for this entity and must never be written to or deleted.
- **Authorability verdict** (derived): one of `COMPILABLE` / `NEEDS_FIELDS` / `NEEDS_SME` /
  `NOT_MECHANIZABLE`, plus a human-readable reason. Answers *"can this be built?"* — and, under the
  gold-derived model, also serves as compile state directly (see FR-017).
- **Compile state** (derived): `COMPILED` (= `authorability === "COMPILABLE"`) / `NOT_COMPILED`.
  Answers *"is this built?"*
- **Rule Catalog screen** (new, not yet built — Phase 4): the catalog-wide view of all 1,105 checks
  with green/yellow compile state, per-block/per-Route/per-status counts, search, and filters on
  compile state, authorability, block, severity, and Route.
- **`appliesIf` / applicability** (derived from gold's `applicability` field): `{always}` or
  `{all_of[], any_of[]}` conditions, mapped 1:1 into the frontend's existing precondition-gate shape.
- ~~**`blocks/handauthored/*.ttl`**~~ *(RETIRED — see rework)*: no SHACL compiler is in this spec's
  path; nothing passes through it.

---

## Success Criteria *(mandatory)*

> ⚠️ **2026-08-01**: SC-002, SC-003, SC-004, SC-005, SC-006 (as originally worded), SC-010, and SC-012
> below are **retired or updated** — same reasoning as the FR section above. SC-001 is done (see its
> own result below); SC-007/008/009/011 are unchanged in substance, pending Phases 4-5.

- **SC-001** *(done)*: Baseline restored before any change — result: **4/20,830** rule-loan pairs
  reach a verdict on `demo/syn/loan 01-05` (`BASELINE.md`), not 25/25. Decision 031 then moved the
  demo/regression target to the Touchless loan; this baseline stands as historical rationale only.
- **SC-002** *(RETIRED — see rework)*: ~~`workbook_ingest.py` asserts 5,520→4,167→3,370 row counts~~.
  No such ingestion script exists. Gold's own build (`storage/rules/gold/reports/compile-stats.md`)
  is the authoritative record of its 266 cards / 1,111 defect options / 221 atomic rules.
- **SC-003** *(RETIRED — see rework)*: ~~gate-parse coverage over 5,201 `Question Criteria` cells~~.
  Gold's `applicability` field is already structured; `build_gold_catalog.py`'s `map_applies_if()` is
  a direct mapping, not a parse-and-report step.
- **SC-004** *(updated)*: The `COMPILABLE` set is independently re-derivable from
  `goldCatalog.json`'s own `authorability`/`sourceLocator` fields (not `field_catalog.json` re-parsed
  from scratch), and was spot-checked during Phase 1 — catching and fixing one false-clean bug
  (doc_presence/doc_completeness marked `COMPILABLE` without a resolved evidence field).
- **SC-005** *(RETIRED — see rework)*: ~~emitted `.ttl` parses under `rdflib`, 100% of
  `caro:exceptionRef` resolves~~. No `.ttl` is emitted in this spec's path.
- **SC-006** *(updated)*: Any future regression check for the *authoring UI's data* compares against
  `goldCatalog.json`'s own recorded totals (1,105 checks, 208 `COMPILABLE`), not SC-001's retired
  4/20,830 SHACL-audit number — those measure different things (rule catalog completeness vs. a
  specific engine's audit-time behavior) and must not be conflated.
- **SC-007**: `npm run build` (`tsc -b`) is clean — **confirmed** (2,206 modules, no errors) — and
  chrome-devtools MCP confirms on the real screens: checks render, groups collapse, search filters, no
  non-executable check is green, gates are visible, and Save is present. *(Screenshot verification via
  chrome-devtools MCP was not completed this session — shared browser profile conflict; Gordon's own
  manual review of the running app substituted, and found two real bugs — see Phase 3 in plan.md.)*
- **SC-008**: Bundle size measured with the catalog loaded (gold's ~1,105 checks is far smaller than
  the old 3,370-check target this criterion was originally sized against — re-verify whether
  per-block lazy-loading is still necessary before building it, per plan.md Phase 4).
- **SC-009**: Refresh durability proven end-to-end: activate checks → Save → reload → activations
  persist → Export → the downloaded file, placed at `storage/rules/v1.json`. *(Not yet built — Phase
  5. "Accepted by `ruleset_to_shacl.py` and compiles to `.ttl`" from the original wording is dropped —
  no compiler in this spec's path consumes the export.)*
- **SC-010** *(updated)*: The Rule Catalog screen renders **all 1,105** checks and reports **208
  compiled / 897 not compiled**, matching a direct recount of `goldCatalog.json`.
- **SC-011**: Compile state is legible **without colour**: greyscale screenshot review confirms
  `COMPILED` / `NOT COMPILED` is readable from the text alone, and no compile indicator reuses the
  pill-shaped verdict badge from `StatusBadge.tsx` — **built in Phase 2/3** (dashed border + text
  label, never green).
- **SC-012** *(updated)*: Yellow sub-reasons reconcile exactly against `goldCatalog.json`'s own
  `authorabilityReason` values (642 `NEEDS_FIELDS`, 108 `NOT_MECHANIZABLE`, 147 `NEEDS_SME`) — **not**
  `yellow_blocker_type`, which has no equivalent on gold cards.

---

## Assumptions

- ~~`src/shacl_pilot/` remains a gitignored experimental sandbox~~ **Corrected 2026-08-01**: a bare
  `src/` gitignore rule was accidentally hiding both `frontend/src/` and `src/shacl_pilot/` from git
  entirely — fixed, and both trees committed as a first-time baseline. The frontend still reads a
  **committed copy** of its catalog (now `frontend/src/data/goldCatalog.json`), but the reason is no
  longer "the source directory is gitignored" — it's simply the established generated-artifact
  convention (spec019's original Phase 1 step 8).
- The 25/25 figure in `src/shacl_pilot/out/full_5loan_audit_latest.md` is treated as **unverified**
  until SC-001 re-runs it — **done 2026-07-31**: the real number is 4/20,830 (`BASELINE.md`), and per
  decision 031, no future phase measures against it or against `demo/syn/loan 01-05` generally.
- The six `p0/qc_engine/ruleset.py` `Check` kinds are sufficient for the `COMPILABLE` subset. Checks
  needing a genuinely new kind are `NOT_MECHANIZABLE` for now; `018-set-membership-check-kind` is the
  reserved slot for expanding the vocabulary.
- Extraction breadth is fixed for this spec. Growing `field_catalog.json` moves checks from
  `NEEDS_FIELDS` to `COMPILABLE`, but that work belongs to the Touchless contract (Non-Negotiable #2),
  not here.
- Single-user authoring. No concurrent-edit or merge semantics.
- The 50-check collapse threshold in FR-009 is a starting value, tunable after the first real SME
  session — not a load-bearing constant.
- **Added 2026-08-01**: `fieldId` validity (for the authorability verdict) is checked against
  `p0/qc_engine/field_catalog.json`, since the frontend has always assumed that catalog. This is a
  simplification, not resolved: if Pipeline A ends up the audit engine (the live bake-off is
  unresolved), some `NOT_MECHANIZABLE`/`NEEDS_FIELDS` verdicts may need re-deriving against Pipeline
  A's own fact vocabulary (`storage/fact_vocabulary/vN.json`). Not blocking for the authoring UI.
- **Added 2026-08-01**: Routes map to the two-way AMQ program grouping (Conventional, Government),
  not the five granular AMQ programs (FNM/FRD/FHA/VA/RHS) — Gordon's explicit call, no Fannie/Freddie
  or FHA/VA/USDA sub-split anywhere in the UI.

## Out of Scope

- **A write API or real backend** for Save (the `localStorage` + Export path is deliberate; naming this
  out of scope so nobody assumes durability that does not exist).
- Loan-evaluation results wiring — `MOCK_EVALUATION` stays; per-loan verdict rendering is separate.
- The Route DAG diagram (`ACTION-ITEMS-2026-07-30.md` item #2) and the multi-document field comparison
  view (item #4).
- Pre-Funding's 4,825 rows. Post-close only, per Gordon's explicit scope.
- Regenerating the 24 hand-authored shapes' SPARQL logic; they are passed through untouched.
- Any extraction work — new fields, new document types, per-page citation granularity.
- Promoting `src/shacl_pilot/` out of its gitignored sandbox into `p0/`.
- Multi-user concurrent authoring, edit merging, and role-based permissions.
