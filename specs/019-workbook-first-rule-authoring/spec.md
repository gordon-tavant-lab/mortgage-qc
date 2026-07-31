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

## The storage model — three artifacts, three jobs

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

1. **Given** the Assets block (304 workbook rows), **When** the SME opens it, **Then** the pool shows
   only `COMPILABLE` checks by default, and the header shows counts for `NEEDS_FIELDS`, `NEEDS_SME`,
   and `NOT_MECHANIZABLE` alongside the affirmative-rows-excluded count.
2. **Given** a check whose fields are not extracted (e.g. `CHK-AST-003`, needing `hasBankDebit`,
   `payee`, `debit_amount`, `recurring_count`), **When** the SME inspects it, **Then** it is labelled
   `NEEDS_FIELDS` and lists exactly which fields are missing.
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

1. **Given** any check, **When** the SME opens its detail view, **Then** category, Question Code,
   Question Text, Exception Code, Exception Description, Default Significance, and Default AOR 1 are
   all shown, sourced from the workbook.
2. **Given** a check's Exception Description, **When** displayed, **Then** it appears **verbatim** —
   no paraphrase, no truncation in the detail view.
3. **Given** any check, **When** inspected, **Then** its `sourceLocator` shows the real sheet name and
   row number from the `.xlsx`.
4. **Given** the Exception Description and the Question Text, **When** both are shown, **Then** the
   Exception Description is the primary label and the Question Text the grouping caption — never the
   reverse (a Question Text like "Were all self-employed requirements met?" is a vague header shared by
   dozens of distinct tests).

---

### User Story 3 — A signed check compiles to a valid shape, and detection does not regress (Priority: P1)

The SME signs a set of checks; the compiler emits SHACL; the audit still catches the known defects.

**Why this priority**: this closes the loop. Without it the UI is a viewer, not an authoring tool.

**Acceptance Scenarios**

1. **Given** a signed `COMPILABLE` check, **When** `ruleset_to_shacl.py` runs, **Then** it emits a
   `sh:NodeShape` whose `caro:exceptionRef` is a real workbook Exception Code.
2. **Given** any emitted shape, **When** the compiler validates its own output, **Then** an
   unresolvable `caro:exceptionRef` fails the build loudly — the exact defect the 22 broken shapes
   represent.
3. **Given** the 24 hand-authored shapes, **When** the compiler runs, **Then** they pass through
   untouched and a reconciliation report states which now have a workbook row pointing at them.
4. **Given** the recompiled ruleset, **When** the 5-loan audit runs, **Then** detection does not
   regress from the number Phase 0 recorded, and determinism passes.

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
3. **Given** that exported file placed at `storage/rules/v1.json`, **When** `ruleset_to_shacl.py` runs
   against it, **Then** it is accepted and compiles to valid `.ttl`.
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

Gordon (or a client in a demo) opens a catalog-wide Rule Catalog screen and sees **all 3,369** post-close
rules at once — not just the ones scoped to a single Block. Each row carries a green or yellow indicator:
green where executable SHACL logic exists, yellow where it does not yet. Headline counts sit at the top,
and yellow rows can be grouped by *why* they are not built.

**Why this priority**: this is the coverage story. It answers "what does the tool cover today, and what
is left?" in one screen — the question a client asks first. It is also the honest counterweight to a
padded "3,369 rules configured" claim.

**Acceptance Scenarios**

1. **Given** the compiled ruleset, **When** the SME opens the Rule Catalog, **Then** the header shows
   **12 compiled / 3,357 not compiled** out of 3,369 total, with the counting basis stated.
2. **Given** any rule row, **When** rendered, **Then** its compile state is shown as a distinct visual
   indicator **plus the word** `COMPILED` or `NOT COMPILED` — never colour alone, and never the same
   pill-shaped badge used for loan verdicts.
3. **Given** a `NOT_COMPILED` rule, **When** the SME inspects it, **Then** the reason is shown from the
   existing `yellow_blocker_type` vocabulary (`sme_clarification`, `extraction_gap`, `fixture_gap`,
   `external_lookup`, `other`), falling back to the authorability reason where the type is `other`.
4. **Given** the catalog, **When** the SME filters, **Then** compile state, authorability, block,
   severity, and program gate all work as filters, and counts update to match the filtered set.
5. **Given** the 12 compiled rules, **When** grouped by block, **Then** they show as
   `application-verification` 6, `asset-verification` 4, `income-verification` 2 — making the
   concentration visible rather than implying even coverage.
6. **Given** 3,369 rows, **When** the screen renders and is scrolled, **Then** it stays responsive
   (virtualized or grouped) and does not eagerly load all 16 block files.

---

### Edge Cases

- **A block with more checks than fit on screen.** Property-Appraisal has **714** checks (Product
  Specific 704, Income 616) against 27 in today's mock data. Question-code grouping collapses 714 into
  131 groups.
- **A block with zero `COMPILABLE` checks.** Seven categories have no hand-authored shape at all
  (Data Validation Svc-DVS 137 · Insurance 133 · Loan Documents 109 · Information Integrity 84 ·
  EPD 34 · Fannie Mae Form 1033 30 · ATR-QM 14). The empty state must say why, not read as "nothing to
  configure".
- **Affirmative rows.** 797 deduped rows carry blank Exception Code, blank severity, and blank
  description; 769 begin "Yes…" or "Not Applicable". They are the questionnaire's compliant branch, not
  defect rules, and must not appear as gateless checks.
- **Non-standard severities.** Beyond `Critical`/`Major`/`Minor` the data contains `Material` (1),
  `Note` (4), `Critical-Pending SI` (6), and empty (797).
- **Duplicate Exception Codes.** 3,250 distinct codes across 3,370 checks — the code alone is not a
  unique key.
- **A `localStorage` draft written against a stale catalog.** Checks referenced by a saved draft may no
  longer exist after the workbook is re-ingested.
- **`localStorage` quota.** A large authored ruleset may exceed the ~5 MB browser limit.
- **A green rule that has never been run.** `COMPILED` means logic exists, not that it has fired on any
  loan. All 12 are in this state until an audit runs, so the label must not read as a verdict.
- **A green rule the engine cannot actually reach.** 28 shapes are authored in `.ttl` but only **4** are
  reachable via `eval_target` — so 8 of the 12 green rules point at logic the runner does not currently
  invoke. The catalog must not present "compiled" as "wired end-to-end"; Phase 5's reconciliation report
  is what closes this.
- **The 3,369 vs 3,370 discrepancy.** `amq_compiler.py:301` drops one external-lookup rule that a direct
  workbook read counts. State the basis; never show two different totals on different screens.
- **A whole block with zero green rules.** 13 of 16 blocks have none. The empty state must say "none
  compiled yet" rather than rendering as though the block is empty or complete.
- **Colour-blind and greyscale viewing.** Green/yellow are indistinguishable to some viewers and in
  printed demo handouts, which is why FR-016 requires the word alongside the colour.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `src/shacl_pilot/workbook_ingest.py` MUST read
  `demo/rules/PF and PC Sept 2025 AMQs - Retail.xlsx` directly via `openpyxl` (not the derived CSV),
  preserving the real sheet name and row number that `frontend/src/lib/types.ts:45-49` already declares
  as `SourceLocator` and that the CSV path discards.
- **FR-002**: It MUST filter on `Questionnaire Name` containing `Post-Closing`, and MUST reproduce the
  verified counts exactly, reusing `agency_of()`, `CATEGORY_TO_BLOCK`, and the
  `(Question Code, Question Answers Exception Name)` dedup key from `amq_compiler.py:289-293`.
- **FR-003**: The 797 affirmative rows (blank Exception Code) MUST be excluded from the Check universe
  and **counted per block**, never rendered as checks with no gate.
- **FR-004**: `Question Criteria` MUST be parsed into a structured gate
  (`{program, conditions[]}`). A predicate that does not parse MUST yield `gate: null` plus
  `gateRaw` (the original SQL) and MUST be **listed in full** in the ingest report — never guessed,
  never silently dropped.
- **FR-005**: Every check MUST carry a derived **authorability verdict** with its reason:
  `COMPILABLE` (maps to one of the six `p0/qc_engine/ruleset.py` `Check` kinds **and** every field it
  needs exists in `field_catalog.json`) · `NEEDS_FIELDS` (kind clear, fields absent — MUST list
  `missingFields[]`) · `NEEDS_SME` (judgment language; cannot be pass/fail) · `NOT_MECHANIZABLE`
  (compound multi-entity predicate). The verdict MUST be derived and displayed with its reason, never
  inferred silently.
- **FR-006**: `types.ts` `Severity` MUST become `"Critical" | "Major" | "Minor"`, normalizing the four
  non-standard values found in the data (`Material`, `Note`, `Critical-Pending SI`, empty) to `Minor`
  while retaining the original in `severityRaw`.
- **FR-007**: `CheckStatus` MUST add `NO_DATA` and `NOT_COMPILED`, and MUST **keep** `NEEDS_REVIEW` —
  it exists in the SHACL engine, derived from `sh:Warning` at `src/shacl_pilot/run_audit.py:166`, with
  five shapes carrying `sh:severity sh:Warning`.
- **FR-008**: `BlockDetail.tsx`'s available-checks pool MUST default its primary axis to
  **authorability**, not category, with the counts of the other three buckets always visible. Category
  scoping (`c.category === block.name`, line 44) MUST remain as the secondary filter.
- **FR-009**: `QuestionGroup` MUST collapse by default **only** when a block exceeds 50 checks,
  reusing `groupByQuestion()` (`BlockDetail.tsx:190`) unchanged. Below that threshold, today's
  expanded-by-default behaviour and its documented rationale (lines 50-55: collapsing implies false
  switch-statement semantics and risks sign-off theatre) MUST hold. A search control over Exception
  Description, Exception Code, and Question Text MUST be present.
- **FR-010**: `src/shacl_pilot/ruleset_to_shacl.py` MUST template only the six `p0` `Check` kinds
  (the plain triple-pattern + `FILTER` form that 20 of the 28 existing shapes already use), MUST assert
  every emitted `caro:exceptionRef` resolves to a real workbook Exception Code, and MUST pass the 24
  hand-authored shapes through untouched from `src/shacl_pilot/blocks/handauthored/` while emitting a
  reconciliation report — never regenerating their SPARQL logic.
- **FR-011**: `NOT_COMPILED` and `NO_DATA` MUST be visually distinct from `PASS` and never green;
  block headers MUST show `compilable / total · N affirmative excluded · N need fields`.
- **FR-012**: The **three-artifact separation MUST hold**: the UI loads `amq_catalog.json` (read-only
  catalog), Save persists to `storage/rules/vN.json` (SME decisions), and `ruleset_to_shacl.py` emits
  `blocks/*.ttl` (compiled). **The UI MUST NOT read `.ttl`.** The catalog MUST be split per block and
  lazy-loaded — `result/rules/post_closing_only_ruleset.json` is 3.7 MB for 5,093 checks, so a single
  eagerly-imported catalog would bloat the bundle.
- **FR-013**: Save MUST persist to `localStorage` so a refresh does not destroy work, and MUST offer
  **Export** of a ruleset JSON shaped like `result/rules/*_ruleset.json`
  (`{content, sha256, provenance, signoff_summary}`), destined for `storage/rules/vN.json` — versioned
  `vN.json` exactly as `storage/fact_vocabulary/v1..v8.json` and `storage/rule_ontology/v1.json` do.
  Writing the file there is a deliberate human step. The UI MUST label this a local draft and MUST NOT
  imply a server. A draft referencing checks absent from the current catalog MUST report them rather
  than fail silently, and exceeding the `localStorage` quota MUST surface an explicit error directing
  the SME to Export.
- **FR-014**: **Every rule MUST be visible on a catalog-wide screen**, not only the checks scoped to one
  Block. All **3,369** defect checks MUST be reachable and countable in one place, with per-block and
  per-status totals. (3,369 in `ruleset.json` vs 3,370 workbook-direct: `amq_compiler.py:301` excludes
  one external-lookup rule via `DISCARDED_EXTERNAL_LOOKUP_EXCEPTION_CODES`. The catalog MUST state which
  basis it counts on rather than leaving a silent off-by-one.)
- **FR-015**: Each rule MUST carry a **compile state** — `COMPILED` (green) when executable SHACL logic
  exists and is vetted, `NOT_COMPILED` (yellow) otherwise. Against today's artifact that is **12 green /
  3,357 yellow**, green being `eval_class == "mapped"` (6 `application-verification`, 4
  `asset-verification`, 2 `income-verification`). Definition (Gordon's call, 2026-07-30, option A):
  green asserts **"the rule has been built,"** *not* "the rule has been proven to fire on a real loan"
  — a stricter reading that would make the count **4**, since only 4 of the 28 authored shapes are
  reachable via `eval_target`. The screen MUST NOT imply the stronger claim.
- **FR-016**: **Compile state MUST NOT reuse the verdict colour language.** `StatusBadge.tsx` already
  maps emerald to `PASS` and `AUTO_CLEARED` — a loan *passed*. Compile state is a different axis
  entirely (is the rule built), and `docs/frontend/RULE-TO-CHECK-UI-MODEL.md:205` mandates that
  `NOT_COMPILED` be *"visually distinct from `PASS` — never green."* Therefore: render compile state in
  a **distinct visual form** (e.g. a small filled dot on the rule row) rather than the pill-shaped
  verdict badge, and **always pair the colour with the word** `COMPILED` / `NOT COMPILED`. Colour alone
  MUST NOT be the only carrier of meaning — reading "12 green" as "12 passed" is the false-clean bug in
  a new place, and it also fails the non-colour-dependence requirement of an accessibility review.
- **FR-017**: The yellow sub-reason MUST reuse the **existing** `yellow_blocker_type` vocabulary already
  present on every rule in `ruleset.json` — `other` (2,739), `sme_clarification` (496),
  `extraction_gap` (91), `fixture_gap` (16), `external_lookup` (15) — rather than inventing a parallel
  taxonomy. Where `yellow_blocker_type` is `other`, the authorability verdict (FR-005) supplies the
  more specific reason. The relationship MUST be documented: compile state answers *"is it built?"*;
  authorability answers *"can it be built?"* — a rule can be `NOT_COMPILED` **and** `COMPILABLE`
  (buildable, not yet built: the actual work queue), which is the intersection the roadmap needs.

### Key Entities

- **`amq_catalog.json`** (new; generated, committed, split per block): the read-only authoring catalog
  — 16 blocks, 3,370 checks, each with workbook provenance, parsed gate, and authorability verdict.
- **`storage/rules/vN.json`** (new; SME-written, versioned): activations per block/route, per-check
  edits, and sign-off. The compiler's only input. Lives in the existing empty `storage/rules/`.
- **Authorability verdict** (new; derived): one of `COMPILABLE` / `NEEDS_FIELDS` / `NEEDS_SME` /
  `NOT_MECHANIZABLE`, plus a human-readable reason and `missingFields[]` where applicable. Answers
  *"can this be built?"*
- **Compile state** (new; derived from `eval_class`): `COMPILED` / `NOT_COMPILED`. Answers *"is this
  built?"* — a **separate axis** from authorability. The two intersect: `NOT_COMPILED` + `COMPILABLE`
  is the buildable-but-not-yet-built work queue.
- **Rule Catalog screen** (new): the catalog-wide view of all 3,369 defect checks with green/yellow
  compile state, per-block and per-status counts, search, and filters on compile state, authorability,
  block, severity, and program gate.
- **Parsed gate** (new; derived from `Question Criteria`): `{program, conditions[]}`, or `null` with
  `gateRaw` when unparsed.
- **`blocks/handauthored/*.ttl`** (new location for existing files): the 24 hand-authored shapes the
  compiler passes through untouched.

---

## Success Criteria *(mandatory)*

- **SC-001**: Baseline restored **before any change**: the 5 loan fixtures regenerated from
  `demo/syn/loan 01..05` via `extract_loan.py` → `loan_to_rdf.py`, `run_full_ruleset_audit.py` re-run,
  and the **actual** detection number recorded. (`src/shacl_pilot/out/` currently holds only two `.md`
  files — every `loan_NN.json`/`loan_NN.ttl` the 25/25 report consumed is gone, so 25/25 is a claim
  from a past run, not a reproducible fact today.)
- **SC-002**: `workbook_ingest.py` asserts, and fails loudly on drift from: 5,520 post-close rows →
  4,546 deduped → 379 Discarded → 4,167 rules → 797 affirmative → **3,370 defect checks**, across
  **16** categories and **787** distinct Question Codes in the check set. (The workbook has **17**
  Question Category Names; `Discarded` is the 17th and is excluded, so the *check* set spans 16.)
- **SC-003**: Gate-parse coverage is reported over the 5,201 populated `Question Criteria` cells, with
  every unparsed predicate listed in full — not sampled.
- **SC-004**: The `COMPILABLE` set is independently re-derivable from `field_catalog.json`, and 20
  verdicts are hand-spot-checked. (An over-broad verdict here is the false-clean bug in a new place.)
- **SC-005**: Emitted `.ttl` parses under `rdflib`, and **100%** of emitted `caro:exceptionRef` values
  resolve to real workbook Exception Codes.
- **SC-006**: The post-compilation 5-loan audit does not regress from SC-001's recorded number, and
  determinism passes (two runs byte-identical).
- **SC-007**: `npm run build` (`tsc -b`) and `npm run lint` are clean, and chrome-devtools MCP confirms
  on the real screens: Property-Appraisal's 714 checks render, groups collapse, search filters, no
  non-executable check is green, gates are visible, and Save is present.
- **SC-008**: Bundle size is measured with the catalog loaded, and per-block lazy-loading is verified —
  opening one block fetches one block's data, not all 16.
- **SC-010**: The Rule Catalog screen renders **all 3,369** defect checks and reports
  **12 compiled / 3,357 not compiled**, matching a direct recount of `ruleset.json` `eval_class` values.
  Green rules group as `application-verification` 6, `asset-verification` 4, `income-verification` 2.
- **SC-011**: Compile state is legible **without colour**: greyscale screenshot review (chrome-devtools
  MCP) confirms `COMPILED` / `NOT COMPILED` is readable from the text alone, and no compile indicator
  reuses the pill-shaped verdict badge from `StatusBadge.tsx`.
- **SC-012**: Yellow sub-reasons reconcile exactly against `ruleset.json`'s existing
  `yellow_blocker_type` counts — `other` 2,739 · `sme_clarification` 496 · `extraction_gap` 91 ·
  `fixture_gap` 16 · `external_lookup` 15 — with no invented categories.
- **SC-009**: Refresh durability is proven end-to-end via chrome-devtools MCP: activate checks → Save →
  reload → activations persist → Export → the downloaded file, placed at `storage/rules/v1.json`, is
  accepted by `ruleset_to_shacl.py` and compiles to valid `.ttl`.

---

## Assumptions

- `src/shacl_pilot/` remains a gitignored experimental sandbox (per memory
  `shacl-experiment-src-sandbox`). Promoting it to `p0/` is a separate decision. The frontend therefore
  reads a **committed copy** of the generated catalog under `frontend/src/data/`, never the gitignored
  source directory.
- The 25/25 figure in `src/shacl_pilot/out/full_5loan_audit_latest.md` is treated as **unverified**
  until SC-001 re-runs it. Every later gate compares against the number SC-001 records, not against 25.
- The six `p0/qc_engine/ruleset.py` `Check` kinds are sufficient for the `COMPILABLE` subset. Checks
  needing a genuinely new kind are `NOT_MECHANIZABLE` for now; `018-set-membership-check-kind` is the
  reserved slot for expanding the vocabulary.
- Extraction breadth is fixed for this spec. Growing `field_catalog.json` moves checks from
  `NEEDS_FIELDS` to `COMPILABLE`, but that work belongs to the Touchless contract (Non-Negotiable #2),
  not here.
- Single-user authoring. No concurrent-edit or merge semantics.
- The 50-check collapse threshold in FR-009 is a starting value, tunable after the first real SME
  session — not a load-bearing constant.

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
