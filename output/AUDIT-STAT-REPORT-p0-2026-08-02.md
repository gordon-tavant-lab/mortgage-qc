# p0 Engine Audit Stat Report — Loan 12607601215

**Date:** 2026-08-02
**Purpose:** a complete, citable explanation of why every one of the 1,105 compiled gold-ruleset
checks is in the status it's in for this loan — suitable to hand to Kayla or any other reviewer
without further context from this session. Companion file:
`output/AUDIT-STAT-REPORT-p0-2026-08-02.xlsx` (3 sheets: Summary, Reason Categories + real example
citations, and the full 1,105-row detail with question text/response/citation for every check).

---

## 1. The raw AMQ workbook — what actually exists, verified directly

Source: `demo/rules/PF and PC Sept 2025 AMQs - Retail.xlsx` ("Report 1" sheet, header on row 4).

| Questionnaire | Rows | Unique Question Codes ("cards") |
|---|---:|---:|
| Post-Closing AMQ Sept 2025 audits | 5,520 | 889 |
| Pre-Funding AMQ Sept 2025 audits | 4,825 | 813 |
| *(blank spacer rows in the Excel export)* | 1,671 | — |
| **Total** | **12,016** | **1,702** |

This project has **only ever ingested Post-Closing.** Pre-Funding (4,825 rows, 813 cards) has never
been touched — not reviewed, not scoped, not started. That's a real, sizeable, separate body of work
sitting untouched, not a gap in what's been built so far.

## 2. Why 889 Post-Closing cards became 266 — the scope funnel, verified against the actual extraction pipeline

`storage/rules/gold/pipeline/extract_cards.py` classifies every card by scope before anything else
happens. This is a deterministic, no-LLM step — every card gets bucketed by a simple rule (category
name, or a prefix on its question code):

| Scope bucket | Cards | What it means |
|---|---:|---|
| **base** (Fannie Mae, live, in scope) | **266** | **This is the entire gold ruleset — everything downstream starts here** |
| excluded_government | 338 | FHA / VA / RHS federal loan programs — different rule sets entirely |
| excluded_freddie | 201 | Freddie Mac-specific cards — this project is Fannie Mae only |
| discarded | 77 | The source workbook's own "Discarded" category — already marked unused before this project touched it |
| excluded_program | 7 | Niche program overlays (SONYMA, Portfolio, state programs, Medical Professional) |
| **Total** | **889** | |

**Plain-English summary:** of every Post-Closing question in the source workbook, roughly 3 in 10
are in scope for this build (Fannie Mae, conventional, not a discarded/niche category). The other 7
in 10 were never candidates for this build — they belong to a different investor, a different
government program, or were already marked unused in the source data. This is a scope decision made
before any compilation started, not something lost along the way.

*(The same math applies to Pre-Funding's 813 cards: 247 would be "base"/in-scope by the identical
rule, but none of it — base or otherwise — has been ingested.)*

## 3. From 266 cards to a real, runnable engine — the compile funnel

| Stage | Cards | Exception codes ("individual checks") |
|---|---:|---:|
| 266 base cards, raw extraction from the workbook | 266 | 1,111 |
| Gold ruleset, after SME/LLM-assisted compilation + citation-grounding + schema/fidelity validation | 266 | 1,105 |
| → **p0 compiled into a real, runnable check** | | **256** |
| → **p0 NOT_COMPILED** (no runnable logic exists yet, for any loan) | | **849** |

The 266→1,105 stage is a **prior, separate body of work** (documented in
`storage/rules/gold/reports/compile-stats.md`, generated 2026-07-31) — 264 of 266 cards compiled
successfully (2 failures, both a Freddie-vs-Fannie routing conflict already covered by a live
Fannie-side twin, zero coverage lost). **This session's work starts at the next stage down**: taking
those 1,105 gold-ruleset checks and determining, for one real loan, which ones can actually run.

## 4. p0 verdict distribution — this loan, right now

| Status | Count | % of 1,105 | Plain-English meaning |
|---|---:|---:|---|
| **PASS** | 121 | 11.0% | A real verified pass — either matched real loan data, or an acknowledged, documented demo-scoped auto-pass (see §6) |
| **NEEDS_REVIEW** | 92 | 8.3% | Sent to a human — 7 different reasons, broken down in §7 |
| **NOT_APPLICABLE** | 43 | 3.9% | This check's own trigger condition is provably false for this loan |
| **NOT_COMPILED** | 849 | 76.8% | No runnable check exists yet for *any* loan — a compile-time gap, not something specific to this loan |
| **Total** | 1,105 | 100% | |

**The single most important thing to understand about this table:** `NOT_COMPILED` is not "this loan
failed to produce an answer" — it's "the engineering to answer this question doesn't exist yet,
for any loan, ever, until someone builds it." Distinguishing "we don't have an answer for this loan"
from "we can't answer this question at all yet" is the entire point of this report.

## 5. Cross-engine verification — why these numbers can be trusted

Every fix this session was checked against a second, independently-built engine
(`src/shacl_pilot`, SHACL/RDF-based — architecturally unrelated to `p0`'s Python dataclass engine).

| Metric | Value |
|---|---|
| Checks both engines evaluate and agree on | 120 |
| Disagreements, ever, across the entire session (dozens of runs) | **0** |
| Independent ground-truth gate (25 seeded defects across 5 synthetic loan fixtures) | **25/25 PASS** |
| Automated regression tests (p0) | 449 tests across 45 files, all passing |

Two independently-built engines agreeing on every overlapping check, plus a separate ground-truth
gate that doesn't depend on either engine agreeing with itself, is the strongest evidence available
that today's numbers are real rather than an artifact of one engine's own blind spots.

---

## 6. PASS (121) — what's real vs. what's an acknowledged simulation

| Sub-category | Count | What it is |
|---|---:|---|
| Real data match | 11 | Genuinely resolved from real, populated loan data |
| Auto-pass: DU (Desktop Underwriter) not accessible | 73 | Can only be verified inside Fannie Mae's DU system — this project has no connection to it |
| Auto-pass: DU-relief precondition not accessible | 27 | Applies only if DU granted a specific relief — that fact is just as unverifiable as the checks above |
| Auto-pass: CU (Collateral Underwriter) not accessible | 4 | Same pattern, Fannie Mae's automated collateral-risk system |
| Auto-pass: Loan Delivery/ULDD not accessible | 4 | Same pattern, Fannie Mae's delivery system |
| Auto-pass: EPIC not accessible | 1 | Same pattern, an internal lender system |
| Auto-pass: UCD not accessible | 1 | Same pattern, the Uniform Closing Dataset collection system |

**This is the single most important thing in this whole report to communicate accurately: 110 of
121 PASSes (91%) are a deliberate, documented simulation, not a verified fact.** The decision (made
explicitly, by Gordon, mid-session, with the tradeoff stated before deciding): *"we cannot call into
the DU system to verify, we will simulate they pass"* — and the output is intentionally
**indistinguishable from a real, independently-verified PASS.** This is a real, acknowledged
departure from this project's own "never show a false clean" discipline, scoped explicitly to this
demo build. It is documented in full, with the exact decision quote, in
`storage/rules/gold/data/autopass_no_system_access.json`'s `_meta` block. **Anyone reviewing PASS
counts as a headline metric should know 91% of them are a policy decision, not a verified outcome.**

---

## 7. NEEDS_REVIEW (92) — the full breakdown, why a human is needed for each

| Category | Count | Real example (from the full detail sheet) |
|---|---:|---|
| **Genuine judgment** — no field can ever answer this | 39 | *Form 1033 #26:* "Comparable property characteristics were reported inaccurately... CU comparables tab was not reviewed" — requires reading appraiser narrative and photos |
| **Extraction gap** — document exists, fields unread | 28 | The Form 1004 appraisal is in this loan's file; every structured field inside it (comps, GLA, zoning, condition) is still null — Touchless hasn't extracted them |
| **Data never captured** — no field exists in the vendor contract at all | 18 | 13 of these 18 hang on ONE missing fact: was this closed as an electronic transaction? |
| **Confirmed red flag** — the review queue working correctly | 3 | Subject property is in Hawaii; all 5 of the borrower's employer records are in Colorado, on a loan claiming primary-residence occupancy |
| **Vendor data trust** — a field exists but can't be trusted either direction | 2 | 3 underwriting conditions all show "OPEN" on a loan that's already closed and funded — looks like stale, pre-closing data |
| **Needs real logic built** | 2 | A commute-distance check needs geocoding + distance math — a small build, not a data problem |

**Full explanation of every category, with real question-code/question-text/response citations, is
in the "Reason Categories + Examples" sheet of the companion Excel file** — this table is the
summary; the spreadsheet has the receipts.

**Root-cause note worth flagging directly:** only 39 of 92 (42%) is the true irreducible-judgment
floor. The rest is addressable — mostly by getting more data from the vendor (extraction gaps,
never-captured data), not by writing more code.

---

## 8. NOT_APPLICABLE (43) — every one cites a specific, checkable fact

Every NOT_APPLICABLE verdict in this system carries a cited fact — a real field, from the real loan
payload, that proves the trigger condition false. None are guesses. Representative examples (full
list in the companion sheet):

- *Leasehold-estate appraisal requirements* — this loan's `propertyEstateType = "FeeSimple"`, so a
  leasehold-only requirement cannot apply
- *Condo/co-op project review requirements* — this loan is confirmed a PUD (`pudIndicator = "Y"`),
  not a condo or co-op
- *RefiNow QM/LTV requirements* — this loan's `loanPurposeType = "PURCHASE"`, confirmed not RefiNow
- *AVM-value-appropriateness check* — this loan has a full traditional appraisal and zero AVM data
  anywhere in the file; the check's own trigger requires both to be present

Three of the 43 (a solar-panel valuation check, two ADU checks) rest on an **explicit, demo-scoped
assumption** — "assume this loan has no solar panels / no ADU" — made deliberately for this demo,
not derived from real data (the vendor payload has no field for either concept at all). Marked as
such in the source file (`scenario_applicability_loan12607601215.json`), same standing as the DU
auto-pass decision above.

---

## 9. NOT_COMPILED (849) — the honest majority, broken down by what's actually missing

| Reason | Count | What's needed to fix it |
|---|---:|---|
| Trigger-gated, needs fact machinery | 229 | Document not vendor-matched AND the check only applies under an unresolvable scenario |
| Threshold not parseable | 175 | Rule cites a number but the direction is ambiguous in the source text — the compiler correctly refuses to guess |
| Presence-gate, needs conditional logic | 102 | One document's presence should gate a different requirement — logic not built yet |
| Computation not LTV/DTI | 102 | Needs a recomputation this project has only built for LTV/DTI so far |
| Not converted by design | 101 | Check type (e.g. reverification, list screening) outside this build's current scope |
| Cross-doc, no curated comparison | 96 | Needs comparing two documents against each other — not built yet |
| Compound docs, needs multi-doc logic | 12 | Needs two-or-more documents considered together |
| Demo-excluded | 20 | Deliberately dropped from this demo's scope (documented, reversible) |
| Pure-presence, reviewed and rejected | 6 | Individually reviewed; no safe vendor-document match exists |
| Likely misclassified | 5 | Probably not really a document question — a data-labeling issue in the source |

**The single highest-leverage fact in this entire report:** 340 of the ~365 uncurated document
checks were investigated and found to need fundamentally different machinery (conditional logic,
multi-document comparison, trigger-fact resolution) — **not more document-name matching**, which is
already exhausted (9 total candidates ruleset-wide, 3 wired, 6 reviewed and correctly rejected).

---

## 10. Additional context worth having on hand

**A. The core architectural promise, in one sentence.** Every verdict above was produced by
*compiling* the rule once into a deterministic check, then *running* that same compiled artifact
against the loan — no LLM runs at check-time, ever. Same loan in → same verdict out, every time,
provably (verified via literal byte-identical reruns this session).

**B. What "loan 12607601215" is, and the single-loan caveat.** This is one real Touchless
production loan — not a synthetic fixture. Every number in this report reflects that one loan's
data. **No number here has been validated against a second real loan.** A loan-fetching API is
reportedly becoming available; the natural next step once it lands is rerunning this entire report
against a structurally different loan (a refinance, an ARM, a loan with different documents) to see
which of today's numbers hold and which were specific to this one loan's shape.

**C. The vendor-question trail.** Every "needs more data" finding in this report has already been
turned into a specific, evidence-grounded question filed with the Touchless vendor team —
`output/TOUCHLESS-API-QUESTIONS-2026-07-30.md` (21 questions as of this report, each citing the
exact field/gap it unblocks and how many checks it would resolve). The single highest-leverage open
question: one boolean (was this an electronic closing?) would resolve 13 checks at once.

**D. What changed this session, in order, if a reviewer wants the full history.**
`output/BAKEOFF-P0-VS-SRC-GOLD-RULESET-2026-07-31.md` — 12 addenda, each with before/after stats,
gate verification, and the reasoning for every decision (including ones later corrected, e.g. an
overstated "tested against 25 loans" claim that was found and corrected to "1 loan, honestly
documented as a gap").

**E. Known, accepted risks — stated plainly, not buried:**
- Single-loan validation only (see B).
- 91% of PASS is a documented simulation, not a verified fact (see §6).
- 3 checks rest on an explicit "assume no solar/ADU" demo decision, not real data (see §8).
- `Loans.Underwriting_Type` (whether this loan is DU-underwritten at all) is also an assumed fact,
  not derived — a different, smaller-blast-radius decision than the DU-content auto-passes.

**F. What this is NOT yet.** This entire pipeline exists only on a feature branch/PR
(`worktree-gold-ruleset-plan`, PR #7 against `main`), not merged. `main` still only has the older,
AMQ-workbook-direct compilation path. Nothing in this report is visible to a fresh session working
from `main` until that PR is reviewed and merged.

**G. Suggested audiences for each artifact:**
- **This markdown file** — anyone needing the narrative and the "why," including non-technical stakeholders.
- **Excel Sheet 1 (Summary)** — a one-screen leadership view.
- **Excel Sheet 2 (Reason Categories + Examples)** — Kayla or any SME reviewer wanting to spot-check
  the reasoning category by category with real citations, without opening 1,105 rows.
- **Excel Sheet 3 (Full Detail)** — anyone needing to audit or search a specific question code,
  exception code, or category — filterable, sortable, every row cited back to its real AMQ text.
