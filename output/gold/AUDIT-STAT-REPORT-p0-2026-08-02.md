# p0 Engine Audit Stat Report — Loan 12607601215

**Date:** 2026-08-02 (narrative refreshed 2026-08-01 after the resolve6 + resolve7 passes)
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
| → **p0 compiled into a real, runnable check** | | **668** |
| → **p0 NOT_COMPILED** (no runnable logic exists yet, for any loan) | | **437** |

The 266→1,105 stage is a **prior, separate body of work** (documented in
`storage/rules/gold/reports/compile-stats.md`, generated 2026-07-31) — 264 of 266 cards compiled
successfully (2 failures, both a Freddie-vs-Fannie routing conflict already covered by a live
Fannie-side twin, zero coverage lost). The next stage — taking those 1,105 gold-ruleset checks and
determining, for one real loan, which ones can actually run — is where this report's numbers come
from, and it has moved through three systematic resolution passes since the report was first
written: **resolve6** (2026-08-01, `output/RESOLVE6-NOT-COMPILED-RESOLUTION-2026-08-01.md`),
**resolve7** (2026-08-01, `output/RESOLVE7-ROUND-2-2026-08-01.md`), and **resolve8** (2026-08-02,
`output/RESOLVE8-ROUND-3-2026-08-02.md`, a small closing pass — 2 checks — that wired candidates
already identified but never acted on, and confirmed the honest floor had been reached). Evaluated
coverage moved from 256/1,105 (23%) → 506/1,105 (46%) → 666/1,105 (60%) → **668/1,105 (60%)**
across those three passes, with zero regressions to any previously-evaluated verdict at any step
(verified per-check, not just by aggregate count).

## 4. p0 verdict distribution — this loan, right now

| Status | Count | % of 1,105 | Plain-English meaning |
|---|---:|---:|---|
| **PASS** | 133 | 12.0% | A real verified pass — either matched real loan data, or an acknowledged, documented demo-scoped auto-pass (see §6) |
| **NEEDS_REVIEW** | 92 | 8.3% | Sent to a human — 6 different reasons, broken down in §7 |
| **NOT_APPLICABLE** | 443 | 40.1% | This check's own trigger condition is provably false for this loan — every one cites a specific payload fact (see §8) |
| **NOT_COMPILED** | 437 | 39.5% | No runnable check exists yet for *any* loan — a compile-time gap, not something specific to this loan |
| **Total** | 1,105 | 100% | |

**The single most important thing to understand about this table:** `NOT_COMPILED` is not "this loan
failed to produce an answer" — it's "the engineering to answer this question doesn't exist yet,
for any loan, ever, until someone builds it." Distinguishing "we don't have an answer for this loan"
from "we can't answer this question at all yet" is the entire point of this report.

**What moved NOT_APPLICABLE from 43 (the original report) to 443, and what that means.** The single
biggest driver across both resolution passes was a compiler bug, not new domain logic: a check whose
document/computation/comparison logic was never built would drop straight to `NOT_COMPILED` even when
its own trigger scenario was already provable false from this loan's real data — the "this doesn't
apply" verdict never got a chance to fire. Fixing that dispatch bug (in five separate places across
the converter) and then adversarially re-deriving 244 trigger-scenario facts directly against the raw
Touchless payload (rejecting 11 candidates that didn't hold up — see §8) is what did it. This is not
253 new NOT_APPLICABLE checks meaning "253 things got easier" — it's 253 checks correctly recognizing
they were never relevant to this specific loan in the first place, now that the engine is allowed to
say so.

## 5. Cross-engine verification — why these numbers can be trusted

Every fix across both resolution passes was checked against a second, independently-built engine
(`src/shacl_pilot`, SHACL/RDF-based — architecturally unrelated to `p0`'s Python dataclass engine).

| Metric | Value |
|---|---|
| Checks both engines evaluate and agree on | 124 |
| Disagreements, ever, across the entire session (dozens of runs) | **0** |
| NOT_APPLICABLE parity between engines after all three resolution passes | **443 == 443** |
| Independent ground-truth gate (25 seeded defects across 5 synthetic loan fixtures) | **25/25 PASS** |
| Automated regression tests (p0) | 445 passed, 3 skipped, 1 xfailed |

Two independently-built engines agreeing on every overlapping check, plus a separate ground-truth
gate that doesn't depend on either engine agreeing with itself, is the strongest evidence available
that today's numbers are real rather than an artifact of one engine's own blind spots. 3 of the 11
curated PASS wires added across the resolution passes (all 3 document-match checks — occupancy
affidavit, URLA continuation sheet, escrow instructions) are ported to the SHACL engine too,
which is what moved joint agreement 121→124. The remaining 8 (identity cross-checks, disjunctive
presence facts, the CLTV/HCLTV recompute, the ATR-QM threshold) are p0-only for now — porting them
needs new SHACL shape/predicate wiring, not a dict addition, and is tracked as parity backlog, not
a disagreement (src has no logic yet to evaluate those specific checks either way).

---

## 6. PASS (133) — what's real vs. what's an acknowledged simulation

| Sub-category | Count | What it is |
|---|---:|---|
| Real data match | 22 | Genuinely resolved from real, populated loan data — includes 11 checks newly wired during the resolution passes (identity cross-checks, disjunctive-document-presence facts, a CLTV/HCLTV recompute, a loan-term threshold, 2 pure-absence document matches) |
| Auto-pass: DU (Desktop Underwriter) not accessible | 74 | Can only be verified inside Fannie Mae's DU system — this project has no connection to it |
| Auto-pass: DU-relief precondition not accessible | 27 | Applies only if DU granted a specific relief — that fact is just as unverifiable as the checks above |
| Auto-pass: CU (Collateral Underwriter) not accessible | 4 | Same pattern, Fannie Mae's automated collateral-risk system |
| Auto-pass: Loan Delivery/ULDD not accessible | 4 | Same pattern, Fannie Mae's delivery system |
| Auto-pass: UCD not accessible | 1 | Same pattern, the Uniform Closing Dataset collection system |
| Auto-pass: EPIC not accessible | 1 | Same pattern, an internal lender system |

**This is the single most important thing in this whole report to communicate accurately: 111 of
133 PASSes (83%) are a deliberate, documented simulation, not a verified fact.** The decision (made
explicitly, by Gordon, mid-session, with the tradeoff stated before deciding): *"we cannot call into
the DU system to verify, we will simulate they pass"* — and the output is intentionally
**indistinguishable from a real, independently-verified PASS.** This is a real, acknowledged
departure from this project's own "never show a false clean" discipline, scoped explicitly to this
demo build. It is documented in full, with the exact decision quote, in
`storage/rules/gold/data/autopass_no_system_access.json`'s `_meta` block. **Anyone reviewing PASS
counts as a headline metric should know 83% of them are a policy decision, not a verified outcome** —
down from 91% at the original report, because newly-wired real-data checks kept diluting the ratio
across three rounds, not because any auto-pass was reclassified.

The 9 newly-wired real checks, for anyone spot-checking: 1003-vs-Schedule-C identity agreement,
bank-statement account-holder-vs-borrower agreement, two disjunctive document-presence checks (VOD-
or-statement; signature/name affidavit-or-AKA), an occupancy-affidavit document match, a CLTV
recompute, an HCLTV recompute, a per-borrower SSN-shape check, and the ATR-QM 30-year loan-term
threshold. Every one is a **one-directional derived fact** — it asserts PASS only when every input is
proven from cited payload data; any mismatch or missing input leaves the fact unset, which routes to
NEEDS_REVIEW, never a false FAIL or a guessed PASS. Full citations for each in the companion Excel's
Sheet 3.

---

## 7. NEEDS_REVIEW (92) — the full breakdown, why a human is needed for each

**Unchanged by both resolution passes** — neither pass touched a NEEDS_REVIEW verdict; both were
scoped entirely to converting NOT_COMPILED checks, and every check that was already sending a human
a real, evidenced question keeps doing exactly that.

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

## 8. NOT_APPLICABLE (443) — every one cites a specific, checkable fact

Every NOT_APPLICABLE verdict in this system carries a cited fact — a real field, from the real loan
payload, that proves the trigger condition false. None are guesses, and every one was independently
re-derived by an adversarial verification pass before being trusted (see the rejection counts below).

| Sub-category | Count | What it means |
|---|---:|---|
| Precondition not applicable (scenario-gated) | 418 | The check's own trigger scenario is provably false for this loan, cited to a specific payload fact |
| Structural applicability | 19 | The card-level applicability rule (from the original AMQ source) resolved false for this loan |
| Auto-pass system-check, also structurally not applicable | 6 | Would have been a DU/EPIC-inaccessible auto-pass, but the card doesn't even apply to this loan's structure |

Representative examples, spanning both the original report and the two resolution passes:

- *Leasehold-estate appraisal requirements* — this loan's `propertyEstateType = "FeeSimple"`, so a
  leasehold-only requirement cannot apply
- *Condo/co-op project review requirements* — this loan is confirmed a PUD (`pudIndicator = "Y"`,
  `attachmentType = "Detached"`), not a condo or co-op
- *RefiNow QM/LTV requirements* — this loan's `loanPurposeType = "PURCHASE"`, confirmed not RefiNow
- *Non-US-citizen borrower deposit review* — the sole borrower's URLA declaration is extracted:
  `citizenshipResidencyType = "USCitizen"`
- *SFHA flood-insurance escrow requirement* — extracted flood determination is
  `specialFloodHazardAreaIndicator = "No"`, `nfipFloodZoneIdentifier = "X"`
- *ATR-exempt (HELOC/investment-property) carve-out* — both disjuncts of the exemption trigger are
  provably false (`propertyUsageType = "PrimaryResidence"`, closed-end fixed first lien)

**Adversarial verification, not a one-pass table build.** Every candidate NA fact across both
resolution passes was independently re-derived — not copied — against `demo/touchless/
loan_application.json` by a separate verification step before being added, with a strict rule:
citing that a check *would pass* is not the same as proving its *trigger doesn't apply*, and only
the latter is a valid NA ground. That discipline rejected 11 candidates across both passes (3 in the
first pass, 8 in the second) — including a case where "not HomeReady" looked like an exemption but
was actually the check's own trigger condition (inverted from what it first appeared), and a case
where the only supporting evidence was an absent field rather than a positive fact. It also **caught
and corrected an error already sitting in the table**: an existing NA claiming "no disaster impact
evidenced" was found to be contradicted by the payload's own data (`disasterSummary` records a FEMA
disaster declaration, DR-4909-HI, for the subject property's county, predating this loan's
application date) — that row was flipped back to unresolved rather than left standing.

5 of the 443 (a solar-panel valuation check, two ADU checks, and two others) rest on an **explicit,
demo-scoped assumption** — made deliberately for this demo, not derived from real data (the vendor
payload has no field for either concept at all). Marked as such in the source file
(`scenario_applicability_loan12607601215.json`), same standing as the DU auto-pass decision above,
and flagged in that file's own metadata for anyone reviewing this beyond the demo.

---

## 9. NOT_COMPILED (437) — the honest remainder, broken down by what's actually missing

| Reason | Count | What's needed to fix it |
|---|---:|---|
| Trigger-gated, needs fact machinery | 93 | Document not vendor-matched AND the check only applies under a scenario/fact this project still can't resolve |
| Presence-gate, needs conditional logic | 79 | One document's presence should gate a different requirement — logic not built yet (52 of these are appraisal-content checks: the Form 1004 is in the file, its fields aren't extracted) |
| Not converted by design | 72 | Check type (reverification, list screening) outside this build's scope, or a date-window check blocked on missing anchor dates (all 62 documents in this loan's file have a null `documentDate`) |
| Cross-doc, no curated comparison | 62 | Needs comparing two documents against each other — the second comparison side isn't extracted for most of these |
| Threshold not parseable | 52 | Rule cites a number but the direction is ambiguous in the source text — the compiler correctly refuses to guess (39 of these are a genuinely ambiguous rule text, the cheapest remaining unlock via an SME, not more engineering) |
| Computation not LTV/DTI | 48 | Needs a recomputation this project has only built for a couple of ratio types so far; most are blocked on missing inputs (liability detail, APOR, insurance coverage amounts) |
| Demo-excluded | 20 | Deliberately dropped from this demo's scope (documented, reversible) |
| Compound docs, needs multi-doc logic | 7 | Needs two-or-more documents considered together |
| Pure-presence, reviewed and rejected | 4 | Individually reviewed; no safe vendor-document match exists |

**What changed since the original report (849 → 437):** three systematic passes
(`output/RESOLVE6-NOT-COMPILED-RESOLUTION-2026-08-01.md`,
`output/RESOLVE7-ROUND-2-2026-08-01.md`, `output/RESOLVE8-ROUND-3-2026-08-02.md`) worked through
every reason category above, row by row, no sampling. The core discovery: **most of the reduction
wasn't new engineering — it was fixing a compiler bug that prevented a check's own "this doesn't
apply" logic from ever running.** 11 checks were genuinely wired with new logic (curated document
matches, cross-document comparisons, a ratio recompute, a threshold). Everything else moved to
NOT_APPLICABLE (§8) once the scenario gate was allowed to fire, or stayed in NOT_COMPILED because
it's honestly still blocked — mostly on vendor data (Form 1004 appraisal fields, DU/AUS findings,
note and closing dates, credit-report detail) or on SME judgment (ambiguous rule text). The reports
name a ranked list of vendor asks by how many checks each would unlock; the single largest is
Form 1004 field extraction.

**On a fourth round:** the third round (resolve8) deliberately closed out the last bucket of
already-identified-but-unwired candidates — reviewing 23 checks whose trigger was provably *true*
(the mirror case to rounds 1–2's provably-false triggers) and finding only 2 were safe to wire
(the rest had compound defect conditions, wildcard-disjunction rule text, or an explicit domain
false-positive risk that presence alone can't resolve). That confirms the honest floor: the 437
remaining split into vendor-blocked (~250), SME-answerable (~55), by-design out of scope (~65), and
deliberate demo exclusions (~31), plus the newly-flagged reclassification/ambiguity items in the SME
queue. The next productive round should follow either a Kayla SME-queue session or a vendor
extraction widening — not another pass over this session's own already-mined inputs.

---

## 10. Additional context worth having on hand

**A. The core architectural promise, in one sentence.** Every verdict above was produced by
*compiling* the rule once into a deterministic check, then *running* that same compiled artifact
against the loan — no LLM runs at check-time, ever. Same loan in → same verdict out, every time,
provably (verified via literal byte-identical reruns this session, and via a per-check diff against
the prior commit at all three resolution passes — confirming zero previously-evaluated verdicts
changed except the one deliberate correction noted in §8).

**B. What "loan 12607601215" is, and the single-loan caveat.** This is one real Touchless
production loan — not a synthetic fixture. Every number in this report reflects that one loan's
data. **No number here has been validated against a second real loan.** A loan-fetching API is
reportedly becoming available; the natural next step once it lands is rerunning this entire report
against a structurally different loan (a refinance, an ARM, a loan with different documents) to see
which of today's numbers hold and which were specific to this one loan's shape. This caveat matters
more now than at the original report: the scenario-applicability table that now drives 418 of the
443 NOT_APPLICABLE verdicts is explicitly per-loan (`scenario_applicability_loan12607601215.json`) —
none of it transfers automatically to a second loan without rebuilding the profile and re-verifying.

**C. The vendor-question trail.** Every "needs more data" finding in this report has already been
turned into a specific, evidence-grounded question filed with the Touchless vendor team —
`output/TOUCHLESS-API-QUESTIONS-2026-07-30.md` (21 questions as of the original report, each citing
the exact field/gap it unblocks). The resolution-pass reports add updated, re-ranked vendor asks on
top of that list reflecting what's still blocking the current 437 NOT_COMPILED checks — Form 1004
appraisal field extraction and DU/AUS findings are now the two largest single unlocks.

**D. What changed this session, in order, if a reviewer wants the full history.**
`output/BAKEOFF-P0-VS-SRC-GOLD-RULESET-2026-07-31.md` (12 addenda, the original engine bake-off),
then `output/RESOLVE6-NOT-COMPILED-RESOLUTION-2026-08-01.md` (six NOT_COMPILED categories, 250
checks resolved), then `output/RESOLVE7-ROUND-2-2026-08-01.md` (the remaining three categories, 161
more checks resolved, plus the one deliberate NA-to-unresolved correction), then
`output/RESOLVE8-ROUND-3-2026-08-02.md` (a small closing pass, 2 checks, that confirmed the honest
floor had been reached). Each carries before/after stats, gate verification, and the reasoning for
every decision.

**E. Known, accepted risks — stated plainly, not buried:**
- Single-loan validation only (see B), now load-bearing for a much larger share of the ruleset (60%
  evaluated vs. 23% at the original report).
- 83% of PASS is a documented simulation, not a verified fact (see §6) — down from 91%, diluted by
  new real-data wires across three rounds, not by any auto-pass being reclassified.
- 5 NOT_APPLICABLE verdicts rest on an explicit "assume no solar/ADU"-style demo decision, not real
  data (see §8).
- `Loans.Underwriting_Type` (whether this loan is DU-underwritten at all) is also an assumed fact,
  not derived — a different, smaller-blast-radius decision than the DU-content auto-passes, but one
  that several of the newly-added NOT_APPLICABLE verdicts in §8 now depend on transitively.
- The scenario-applicability table driving most of §8 is per-loan and provisional by design — see B.

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
- **`storage/rules/gold/reports/sme-review-queue.md`** — the specific, itemized list of what Kayla or
  another SME should look at first (spot-check-flagged verdicts, the ambiguous-threshold queue, new
  curated wires needing sign-off before production use).
