# src/ Pilot — Decision Records

Decisions made by Gordon for the SHACL pilot experiment (sandboxed in gitignored `src/`).
These override project-level CLAUDE.md decisions **inside `src/` only**; `p0/` and the
standing gates remain governed by CLAUDE.md.

**Chronological experiment record:** [JOURNAL.md](JOURNAL.md) — what was done, in what order, with verified evidence paths per step (2026-07-29).

| # | Decision | Status |
|---|---|---|
| [001](001-shacl-sandbox-override.md) | SHACL-as-engine experiment sandbox in `src/` | Accepted 2026-07-29 |
| [002](002-extraction-from-syn-pdfs.md) | Loan data extracted from `demo/syn` PDFs + MISMO XML, incl. signatures | Accepted 2026-07-29 |
| [003](003-citations-non-negotiable.md) | Citations are non-negotiable on every extracted value | Accepted 2026-07-29 |
| [004](004-shape-versioning.md) | SHACL shapes are versioned by content hash | Accepted 2026-07-29 |
| [005](005-routes-blocks-checks.md) | Shapes organized as routes → blocks → checks | Accepted 2026-07-29 |
| [006](006-sparql-ux-deferred.md) | SME-friendly editing UX deferred until engine proven | Accepted 2026-07-29 |
| [007](007-loan01-gauge-answers-key.md) | Loan 01 = accuracy gauge; loans 02–05 = generalization vs Answers.md | Accepted 2026-07-29 |
| [008](008-needs-review-tri-state.md) | Tri-state results via SHACL severity (proposed) | Proposed — awaiting Gordon |
| [009](009-full-workbook-compile.md) | Compile the FULL AMQ workbook (4,167 rules); two-layer compile | Accepted 2026-07-29 |
| [010](010-program-filter-question-code.md) | Program filter by Question Code agency prefix (O-FNM/O-FHA/O-VA/O-FRD/O-RHS + generic) | Accepted 2026-07-29 |
| [011](011-olav-blocks-routes-isolation.md) | Olav block taxonomy, per-program routes, full src/ isolation from p0 | Accepted 2026-07-29 |
| [012](012-selling-guide-grounding-corpus.md) | Selling Guide topic-index ontology as Layer-B grounding corpus | Accepted 2026-07-29 |
| [013](013-poc-no-sme-gate.md) | src/ PoC proceeds without SME sign-off gating progress | Accepted 2026-07-29 |
| [014](014-bucket-a-legitimate-fixture-gap.md) | Bucket A: 12 YELLOW groups blocked on missing synthetic fixtures remain legitimate/YELLOW | Accepted 2026-07-29 |
| [015](015-bucket-b-deepen-1003-extraction.md) | Bucket B: 3 YELLOW groups (final-URLA Additional Borrower + section completeness) deepen existing `final_1003` extraction, zero new fixtures | Accepted 2026-07-29 |
| [016](016-bucket-c-discard-external-lookup-rules.md) | Bucket C: NMLS-registry-lookup rule (group 45) discarded from PoC/demo scope | Accepted 2026-07-29 |
| [017](017-assets-block-triage.md) | Asset-verification block triage (304 rules/297 groups): 8/85/7 GREEN/YELLOW/RED — the 51/29/20 application-verification ratio does NOT generalize | Accepted 2026-07-30 |
| [018](018-assets-ready-to-build-verification.md) | Assets "ready to build" candidates: 3 of 6 survive verification | Accepted 2026-07-30 |
| [019](019-credit-liabilities-block-triage.md) | Credit-liabilities-review triage (386/382): 3/92/5 GREEN/YELLOW/RED — zero ready-to-build survives, found the doc_presence classifier bug | Accepted 2026-07-30 |
| [020](020-property-appraisal-block-triage.md) | Property-appraisal-review triage (714/696): 0/46/54 — first block where RED dominates (narrative-adequacy language, not fixture gaps); 3 shapes confirmed orphaned | Accepted 2026-07-30 |
| [021](021-income-verification-block-triage.md) | Income-verification triage (616/580): 6/93/1 — most extreme YELLOW skew yet; 2 verified ready-to-build wins | Accepted 2026-07-30 |
| [022](022-underwriting-block-triage.md) | Underwriting-review triage (466/461): 2/92/6 — least automatable block, zero ready-to-build survives (honest negative) | Accepted 2026-07-30 |
| [023](023-product-specific-block-triage.md) | Product-specific-check triage (704/703): 0/97/3 — near-zero dedup (agency-fragmented by nature); UsdaIncomeLimitShape confirmed orphaned | Accepted 2026-07-30 |
| [024](024-doc-presence-classifier-fix.md) | Fixed the doc_presence auto-classifier's two root-cause bugs (found independently 3×); 135→91 ruleset-wide, partial not complete fix | Accepted 2026-07-30 |
| [025](025-selfemployed-and-orphaned-shapes.md) | SelfEmployedDocsShape wired (2 codes); 4 pilot shapes confirmed to have zero matching AMQ workbook rows | Accepted 2026-07-30 |
| [026](026-green-yellow-red-audit-breakdown.md) | GREEN/YELLOW/RED audit breakdown: what runs (60% on loan 01 via block loading), what converts (62% YELLOW convertible with fixture/extraction work), what stays human (409 RED = 43% of ruleset, route to expert review) | Accepted 2026-07-30 |
