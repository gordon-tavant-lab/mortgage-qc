# NEEDS_REVIEW remediation: research findings and decision record

**Date:** 2026-08-01
**Scope:** the 140-check `scripted_review` population (Category D per
`output/BAKEOFF-P0-VS-SRC-GOLD-RULESET-2026-07-31.md` Addendum 6) — checks both engines currently
report as needing a human, no compiled logic behind them.

## Why this doc exists

Gordon asked to tackle `NEEDS_REVIEW` before `NOT_COMPILED`, explicitly requesting research (web
search) into whether real prior art exists to resolve some of these before assuming they're all
irreducibly human — and asked that the resulting decision be documented, same convention as the
other addenda in this project.

**Headline finding: the premise that all 140 are "no amount of compiler sophistication or loan
data would ever make them machine-decidable" (Addendum 6's Category D definition) does not survive
contact with the actual check text.** A content read of all 147 `scripted_review` defect_options
(147 options across the 140 checks — some cards have multiple options) found large, coherent
clusters that are not open-ended human judgment at all — they're **vendor/system data-contract
gaps**, structurally identical to the DU/EPIC/Loan-Delivery gap this project already has a
sanctioned pattern for (`autopass_no_system_access.json`), not a new problem class.

## Categorization (first pass, content-grounded, not final)

| Cluster | Approx. count | What it actually is |
|---|---:|---|
| Form 1033 / Collateral Underwriter (CU) | ~25-36 | Fannie Mae's own Post-Closing QC Collateral Risk Assessment worksheet, built explicitly around CU output (see research below) |
| RON/RIN e-notary / eNote compliance | ~13 | Remote notarization and E-SIGN Act compliance checks |
| Fraud / red-flag / EPD indicators | ~15-20 | "Indications of," "evidence of" pattern-matching checks, several of which are trivially deterministic |
| Program-eligibility / compound conditions | ~11 | LTV/CLTV thresholds, refinance-program eligibility, title-timing rules — likely *misclassified* `scripted_review`, not genuine judgment (see below) |
| Appraisal judgment (non-1033-numbered) | ~11 | Comp selection, adjustment reasonableness, unique-property judgment |
| Fair lending / ECOA / discriminatory-effects | ~5 | Genuinely irreducible — flagged separately, see below |
| Contact verification (FCRA active-duty/fraud alerts) | ~4 | Needs a call log Touchless doesn't extract |
| Everything else (property/project eligibility checklists, title exceptions, closing-document review, misc.) | ~40 | Heterogeneous; needs the manual pass Gordon offered to do |

This table is a first-pass content read, not a final, individually-hand-verified classification —
consistent with this project's standing discipline (Non-Negotiable #1's grounding rule: a category
assignment is a claim, and claims get verified before anything is wired, the same bar applied to
every curated document match and scenario-gate row so far).

## Research findings, by cluster

### 1. Form 1033 / Collateral Underwriter — the biggest, most actionable finding

**Form 1033 is not an independent checklist we're interpreting — it's Fannie Mae's own document,
explicitly built around Collateral Underwriter (CU) output.** CU is Fannie Mae's automated
appraisal-review engine: it scores UAD-formatted appraisals (Forms 1004/1073) across four
categories (Data Integrity, Comparable Selection, Adjustments, Reconciliation) plus
overvaluation/property-eligibility flags, producing a 1.0-5.0 risk score and itemized messages.

**Critically: CU output is retained, not ephemeral.** Every Uniform Collateral Data Portal (UCDP)
submission produces a **Submission Summary Report (SSR)** tied to a Doc File ID. Fannie Mae's own
Selling Guide requires lenders to keep the final SSR in the loan file. Form 1033 itself requires a
**CU Risk Score ≤ 2.5** as one of four satisfactory-assessment criteria, and requires the assessor
to "reconcile flags and messages identified in Collateral Underwriter."

**What this means for us:** if the SSR (or equivalent DU/EarlyCheck CU feedback) is added to the
extraction contract, a real subset of these checks become **deterministic threshold/field
comparisons** (CU Risk Score ≤ 2.5, flag/message counts by category) — not narrative judgment.
Items requiring qualitative judgment beyond what CU's own messages state remain genuine
`scripted_review`, but that's a much smaller residual than "all Form-1033-numbered items."

This is structurally the same shape as the DU/EPIC/Loan-Delivery gap — **an external system's
retained output that this project's current extraction contract doesn't capture** — not a new kind
of problem. Freddie Mac's parallel tool is **Loan Collateral Advisor (LCA)**.

Sources: Fannie Mae Collateral Underwriter & UCDP pages (singlefamily.fanniemae.com), Form 1033 /
Enhanced Collateral Risk Assessment guidance (fanniemae.com media library, corroborated via
PennyMac correspondent bulletin and SingleSource Property Solutions FAQ since direct PDF fetch was
blocked), Fannie Mae Developer Portal APIs.

### 2. RON/RIN e-notary compliance — a hybrid gap

A structured record exists, but fragmented across systems, and only partially covers what the
checks ask:

- **Already likely available without a new contract:** ULDD Phase 5 "Remote Online Notarization
  Indicator" (Sort ID 398.2), GSE delivery Special Feature Codes **861** (RON) and **920** (RIN) —
  binary flags that may already be in the LOS export our connector touches. Worth confirming with
  the Touchless/LOS team before assuming a gap.
- **MERS eRegistry** gives eNote controller/location/active-status — a real proxy for "the eNote is
  a validly registered transferable record," but narrower than "the platform met legal/technical/
  operational requirements" as the check text demands.
- **Not currently structured, a genuine document-extraction gap:** notary license number/state,
  physical location at signing, RON platform name — these live in the vendor's own **Certificate of
  Completion** (Proof/Notarize, Pavaso, SIGNiX, DocVerify, NotaryCam all produce one; several are
  MISMO-RON-V2-certified against a standard schema). This would need to become a new Touchless
  document type to classify/extract — same pattern as the CU/SSR ask above, not a new category.

Sources: MISMO eMortgage & RON Standards V2, MERS eRegistry FAQ, Fannie Mae Selling Guide
Notarization Standards (A2-4.1-04), ALTA RON conforming-laws checklist, Proof.com documentation.

### 3. Fraud / red-flag indicators — a genuine mixed bag, some solvable today with zero new contracts

- **Deterministic today, no vendor contract needed:** "PO Box is the only address listed for an
  employer" is a solved problem via USPS CASS certification (DPV footnote `PB`, or a commercial
  address-validation API's `record_type` field) — a real field check, not judgment.
  "Excessive AUS resubmissions" is a **pass-through, not re-derivation** — DU's own "Potential Red
  Flag Messages" already flags this natively in the DU Underwriting Findings Report, *if* DU
  findings text is captured (which ties back to the same Underwriting_Type/DU-access gap already
  tracked as Category C in the root-cause doc).
- **Buildable but not a packaged vendor field:** employer-to-property commute distance (geocode +
  distance calc) is technically deterministic but nobody ships it as a named product field — would
  be a build-it-ourselves calculation, not an extraction ask.
- **Genuinely a new vendor contract:** compromised-transaction/flip/straw-buyer/condotel-operation
  pattern indicators need a real fraud-detection product (CoreLogic LoanSafe Fraud Manager, First
  American FraudGuard) — these are subscribed, per-pull services, not something in a standard
  closing package. Consuming their alert codes is the same shape as the DU/EPIC ask, not a
  different kind of gap.

Sources: USPS Postal Explorer Pub 28, PostalPro CASS certification, Smarty US Street API reference,
Fannie Mae Selling Guide B3-2-11 (DU Underwriting Findings Report / Potential Red Flag Messages),
CoreLogic and First American fraud-product documentation, HousingWire coverage of FraudGuard.

### 4. Program-eligibility / compound-condition cluster — likely a *classification* bug, not a research gap

Checks like "at least one borrower on title 6 months prior to disbursement," "LTV/CLTV/HCLTV
exceeds 95% but requirements not met," "borrowers added/removed on RefiNow loan without meeting
exceptions" read as multi-condition eligibility rules, not open-ended judgment — the same shape as
`PC::CIP DATA POINTS`, which this project already reclassified out of a wrong check_type earlier
(Addendum to `NODATA-ROOT-CAUSE-ANALYSIS-2026-07-31.md`). These deserve the same treatment: hand
review for a `check_type` correction (likely toward `cross_doc_consistency` or a compound
`threshold_eligibility`), not vendor research. Flagged here, not yet acted on.

### 5. Fair lending / ECOA — recommend leaving alone

"Evidence of discriminatory effects," "unmarried vs. married applicants evaluated differently,"
"race/color/national origin/... considered" — these are genuinely the closest thing to irreducible
human judgment in the entire set, both technically (no field-level proxy is safe to build) and by
policy (automating fair-lending determination carries real regulatory risk beyond this project's
scope). Recommend these stay `scripted_review` permanently, not a target for future automation.

## Decision

Given the research, Gordon's stated willingness to go through the residual manually, and this
project's standing discipline of "compile, then run" (LLM/vendor integration decisions happen at
configuration time, verified, never as a runtime guess):

1. **Do not treat the 140 as a uniform Category D population going forward.** The real shape is:
   a genuinely small irreducible residual (fair lending, ~5; open-ended "investigate and resolve"
   items; qualitative appraiser judgment beyond CU's own flags) alongside a much larger set that is
   Category A/C in disguise — a data-contract gap this project already has a proven pattern for
   (document it as a vendor/extraction ask, same as `TOUCHLESS-API-QUESTIONS-2026-07-30.md`).
2. **Two sub-items are actionable immediately, with zero new vendor contract:** the PO Box
   deterministic check and the AUS-resubmission DU-findings pass-through (the latter gated on the
   same DU-findings-text availability already tracked in Category C).
3. **The CU/SSR, RON-certificate, and fraud-vendor asks get written up as new, specific questions**
   in the Touchless/vendor-extraction-contract document — not built speculatively, since this
   project's scope discipline is explicit: "Document data extraction ❌ Do not build. Upstream
   contract with the Touchless team returns extracted fields."
4. **The program-eligibility cluster (~11) gets a `check_type` hand-review pass**, same discipline
   as the earlier CIP DATA POINTS reclassification — a classification-accuracy question, not a
   research question.
5. **The remaining ~40 unclassified + appraisal-judgment-other (~11) go to Gordon's manual,
   one-by-one review**, the same rigor already applied to the 9 PURE_PRESENCE and 37
   NOT_DOC_DECIDABLE candidates earlier in this project.

Not yet decided: exact sequencing of steps 2-5, and who does the manual pass in step 5 first. That's
the next conversation, not assumed here.

## What this does NOT change

- No code has been touched. `NEEDS_REVIEW` counts in both engines are unchanged (140/140).
- No new field extraction, vendor contract, or `check_type` reclassification has been implemented —
  this is a research/decision record only, per Gordon's explicit request to document the decision
  before acting on it.
