# 022 — Layer-2 triage of the underwriting-review block: heaviest YELLOW skew yet, two shape-wiring candidates both REJECTED

**Status:** Accepted 2026-07-30 (Gordon — run the same triage method on underwriting-review, the
fourth block triaged, as a fourth data point on how the 51/29/20 application-verification ratio
generalizes, and to specifically check whether the two never-wired shapes already registered
against this block — `ResidualIncomeShape`, `RatioWaiverShape` — should be connected to real AMQ
rows)

## Decision
Triaged all 466 compiled `underwriting-review` rules (`layer2_triage_underwriting.py`, modeled on
`layer2_triage.py`/`layer2_triage_assets.py`/`layer2_triage_income.py`): dedup by `(question_text,
response_text)` to 461 unique groups, classify every group GREEN/YELLOW/RED/NOT_A_CHECK with real
per-group rationale, emit `compiled/triage_underwriting-review.json` +
`out/TRIAGE-PACKET-underwriting-review.md`. Result:

| Bin | Groups | Rules | % of defect groups | application-verification | asset-verification | income-verification |
|---|---|---|---|---|---|---|
| GREEN | 6 | 6 | 2% | 51% | 8% | 6% |
| YELLOW | 342 | 344 | 92% | 29% | 85% | 93% |
| RED | 24 | 24 | 6% | 20% | 7% | 1% |
| NOT_A_CHECK | 89 | 92 | — | — | — | — |

**Headline finding: underwriting-review is the least automatable block triaged so far, and for a
different reason than assets/income.** 92% YELLOW / 2% GREEN / 6% RED — GREEN is now the lowest of
any block (only 6 of 461 groups, all mechanical `doc_presence` auto-compiles amq_compiler.py already
does; zero `mapped` groups, because the two shapes registered against this block fire for zero AMQ
codes — see below). Two things drive the YELLOW dominance, both confirmed by reading every group's
full text, not inferred from a keyword count:

1. **This is the compliance/AUS-findings/legal-form block, not a math-heavy or document-breadth
   block.** Where assets/income needed dozens of asset- or income-*type* documents this pilot never
   built fixtures for, underwriting-review needs entire *categories of infrastructure* this pilot has
   never built at all: no DU, LPA, or TOTAL Scorecard AUS export exists anywhere in the corpus (GUS is
   the only AUS output even partially parsed, 2 fields, loan 05/USDA only) — **58 of the 342 YELLOW
   groups** trace to this single gap. A second large cluster (27 groups) needs title-insurance/
   attorney-title-opinion-letter facts beyond the one field (`title_vesting_commitment`) this pilot
   extracts from `title_commitment`. A third (19 groups) needs a DTI-aggregation + liability-type-
   classification derivation layer on top of entities (`tradelines`, `urla_liabilities`) that already
   exist — crisp math, real derivation-logic gap, no new document needed. A fourth (14 groups) needs a
   `loan_amount` field that, checked directly, **does not exist anywhere in `FIELD_SPECS` today** —
   every LTV/CLTV/HCLTV/TLTV check in this block is blocked on a field this pilot has simply never
   extracted, even though `appraised_value` (the other half of every LTV ratio) already is.
2. **RED is genuinely rarer here than in assets (7%) and closer to income's near-vanishing 1%** — most
   of this block's underwriter-judgment language ("did not adequately evaluate," "well-reasoned
   conclusion," fair-lending ECOA rows) clusters into a small number of real judgment calls (24 of
   461), not spread thin across many groups. Two compound conditions that read RED on a keyword scan
   (G240's "unreasonable... and/or exceeded the total loan amount"; G337's "significantly higher...
   without a repayment analysis") were, on reading the full text, split — the crisp half classified
   YELLOW with the judgment half noted under `stays_human`, same precedent as asset-verification's
   G007/G225 and income-verification's G041/G127.

## Method differences from the first three blocks (stated up front in the script, same discipline)
1. **Dedup barely collapses (466→461, ~1.01x)** — the smallest collapse of any block triaged so far
   (application-verification ~1.5x, income ~1.06x, assets ~1.02x). Verified empirically, not assumed.
2. **GREEN is 100% mechanical, and lower than any prior block.** `amq_compiler.py`'s `MAPPED_SHAPES`
   registers TWO shapes against this block — `ResidualIncomeShape` (`CHK-UND-001`) and
   `RatioWaiverShape` (`CHK-UND-002`) — but both are wired to `amq_exception_codes: []`, the same
   never-fires bug already found and fixed for `GiftEvidenceShape`/`LargeDepositShape` (decisions
   017/018) and found-but-not-yet-fixed for `SelfEmployedDocsShape` (decision 021). This triage is the
   first time anyone checked whether any of underwriting-review's 461 groups describe the same
   condition either shape already tests. **Neither survived verification — see below.** Combined with
   zero pre-existing `mapped` eval_class rules, this makes underwriting-review the first block where
   GREEN is *entirely* auto-compiled doc-presence checks and *zero* hand-built shapes actually fire.
3. **Scale (366 groups needing real judgment, more than any prior block) forced a family-regex
   classification engine, not a hand-typed dict.** ~70 named families, each built from a full read of
   every group's untruncated question/response/exception text (dumped once to a scratch file during
   authoring, never classified off a truncated preview), plus a small 14-group `OVERRIDES` dict for
   compound conditions and one-off phrasing the regex engine couldn't cleanly place. One override
   (`G060`) exists purely because the source CSV encodes "child bearing" with a non-breaking space
   (`\xa0`) that silently defeated the first version of the family regex until traced down explicitly —
   a small but real reminder that "no match" can mean an encoding quirk, not "genuinely unclassifiable."

## ResidualIncomeShape / RatioWaiverShape — checked, NOT wired (the negative result this task asked for)
Per the task briefing's explicit instruction to check whether other AMQ rows across agencies
describe the same real conditions these two shapes already test, before assuming the "0 wired" state
is a bug rather than a verified fact:

**ResidualIncomeShape** (`sh:sparql`: `doc_present_residual_income_worksheet false ; mismo_mortgage_type
"VA"` — i.e., is the VA residual-income worksheet simply absent from the file). Full-text search of
all 461 groups for "residual" found exactly one hit:
- **G289 (O-VA-00655)**, "DTI exceeds 41% or residual income is below VA's minimum and the UW did not
  justify the approval." Read in full against the shape's actual SPARQL: this tests a **materially
  different, compound condition** — a DTI/residual-income *threshold breach* combined with whether the
  underwriter *separately documented compensating factors/justification* for a manual-underwrite
  approval. `ResidualIncomeShape` tests only whether the worksheet document itself is present at all,
  for any VA loan, full stop. A loan could have the worksheet in file (satisfying the shape) yet still
  fail G289 (ratios breached, no justification documented), or vice versa. Wiring G289's exception
  code to this shape would silently mis-evaluate real loans in both directions — the exact false-
  negative risk decision 018 warned about. **REJECTED.**

**RatioWaiverShape** (`sh:sparql`: `piti_ratio > piti_guideline AND dti_ratio > dti_guideline AND
usda_ratio_waiver_in_file false`, with `piti_guideline`/`dti_guideline` populated ONLY from
`usda_ratio_waiver_doc`, present only for loan 05/USDA). Three candidates considered:
- **G106 (O-RHS-02848)**, "PITIA housing ratio... exceeded 34% of the repayment income." A flat,
  hardcoded 34% ceiling — not the shape's "exceeds the loan's OWN extracted guideline, without a
  documented waiver" logic. Different condition (absolute threshold vs. guideline-relative-with-
  waiver-exception).
- **G350 (O-FHA-00606)**, "ratio's exceeding guidelines & compensating factors not noted on the
  [HUD-]92900-LT." FHA's own compensating-factors-documentation pattern, tied to a form
  (HUD-92900-LT) this pilot doesn't have at all — a different agency, different form, different
  documentation target than `usda_ratio_waiver_doc`.
- **G343 (O-RHS-02852)**, "manual UW front ratio over 29% & 100% housing payment increase w/ risk
  layers & no strong comp factors." A compound payment-shock/risk-layering condition, not the same
  shape as guideline-vs-waiver.
- **Structural rejection, independent of textual similarity**: none of these three groups is a
  USDA/RHS loan whose `usda_ratio_waiver_doc` would ever populate `piti_guideline`/`dti_guideline` in
  the first place (G350/G106/G343 span FHA and two different RHS question categories) — even a
  perfect textual match would be structurally unwireable without a new guideline-source field per
  agency. **All three REJECTED.**

Both shapes remain correctly wired to zero exception codes — not a latent bug, a verified fact.

## RED — 24 groups, individually verified (no bulk judgment-keyword bucketing)
Every group whose condition text contained a judgment-flavored word ("(un)reasonable," "adequately,"
"well-reasoned," "discriminat-," "overall complete," "misuse") was read in full before being called
RED. Two compound conditions were caught and reclassified YELLOW instead (see above: G240, G337).
Notable RED families: 6 ECOA fair-lending rows (G051/G054/G057/G058/G059/G060 — discriminatory-intent
or disparate-treatment judgment, no bright-line fact), 5 open-ended discrepancy/red-flag sweeps
(G017/G031/G186/G229/G231/G264/G355 — same class as application-verification's file-wide-discrepancy
RED), 6 holistic risk/underwriting-conclusion-adequacy judgments (G046/G223/G303/G304/G347/G431), plus
one bare catch-all (G015, "No, all program guidelines/overlays have not been met" — same pattern as
application-verification's "all disclosures per guidelines"), one methodology-adequacy call (G025),
one fraud-pattern/investigative judgment (G288), and one pure "(un)reasonable"-dominated condition
with no crisp half (G460).

## What was considered and REJECTED beyond the two shapes above
- **G167 (O-VA-56141, VA Form 26-1880)** — already auto-compiled GREEN by `amq_compiler.py`'s own
  `doc_presence` keyword classifier (matched "Certificate of Eligibility" in the exception text and
  pointed it at the `va_coe` doc type). Verified this is a **keyword-collision false-positive-adjacent**
  case, same class as decision 014's "initial application" → `final_1003` bug: VA Form 26-1880 is the
  *request* form for a COE, not the COE itself. Left GREEN (it's amq_compiler.py's own classification,
  not something newly discovered to fix here, and `va_coe`'s absence for 4 of 5 loans makes the check
  still resolve correctly either way) but flagged with the caveat inline in the packet rather than
  silently presented as a clean fidelity match.
- **G255 (O-VA-55826, itemized pest-inspection invoice)** — same pattern: auto-compiled GREEN against
  `va_nov` because "NOV" appears in the text, but the actual missing item is the itemized invoice, not
  the NOV itself. Flagged with the same caveat, not corrected (no `.py`/`.ttl` edit permitted here).
- **G370 (O-FHA, MIP calculated incorrectly based on LTV/term/product)** — considered for the
  `funding_fee_mip` family (same document/data gap in spirit) but classified under `ltv_cltv_hcltv`
  instead since the blocking field (`loan_amount`) is identical; noted here so the family tag isn't
  read as a coding error.
- **`investment_arm_type` (G453, O-FRD)** — the single closest thing to a "wire existing code" candidate
  in this entire block: `mismo_amortization_type` IS already extracted from every loan's MISMO XML.
  **Not** classified GREEN or flagged READY TO BUILD: no comparison logic exists to parse "7/6-month vs
  10/6-month ARM" out of that field's actual string values, and none of the 5 synthetic loans is an
  investment-property ARM to verify the comparison against — exactly the untested-confidence trap
  decision 018 warned about (a plausible-sounding candidate with no fixture to prove it against).
  Correctly left YELLOW.
- **`de_certification` (G006) and `va_uw_credentialing` (G430)** — underwriter DE-certification
  currency and non-supervised-automatic-lender VA registration are staff/institutional credentials, not
  loan-file facts — same kind of live-registry dependency as the discarded NMLS rule (decision 016).
  Flagged as possible Bucket-C candidates, **not** unilaterally reclassified — a human should decide,
  per decision 017's G218 precedent.
- **`paystub_date_check` (G305)** — a genuine, verified extraction-thinness finding: the `paystub`
  document type exists in every loan folder, but `extract_loan.py` has **zero** `FIELD_SPECS` entries
  for it today (checked directly, not assumed). Kept YELLOW, not elevated to a Bucket-B "ready" claim,
  since no field extraction exists yet to wire — same discipline as income-verification's decision to
  keep its own near-miss candidates YELLOW rather than GREEN.
- **The task briefing's own claim that `borrower_credit_score`/`coborrower_credit_score` and a
  credit-inquiry entity are already extracted** — checked directly against `extract_loan.py` via
  `grep -n "credit_score\|inquiry"` and found **zero matches**. No such field or entity exists anywhere
  in the extractor. All `credit_score_threshold`-family groups (MDCS ≥500/580, credit-score-range
  manual-UW-review-level checks) are classified YELLOW needing a new field on the already-present
  `credit_report` document, not treated as already-solved. Recorded here because trusting an unverified
  claim in a task briefing is exactly the failure mode decision 018 exists to prevent.

## What was NOT done (per instruction)
No `.ttl`, `amq_compiler.py`, `extract_loan.py`, or `run_audit.py` edit was made. `README.md` and
`JOURNAL.md` were not touched (other parallel agents were mid-edit on those files, per the task
briefing). No candidate was unilaterally wired — the zero-survivor ResidualIncomeShape/RatioWaiverShape
result, all RED calls, and all flagged-but-undecided Bucket-C-style candidates are left for a human
decision, exactly like the three prior block triages.

## Cross-links
[[009]] (two-layer compile pattern this triage executes for a fourth block), [[012]] (Selling Guide
grounding corpus — B3-2.x "Automated Underwriting" and B3-5.x/B3-6.x "Credit"/"Liabilities" chapters
are the natural citations for this block, confirmed present in `compiled/selling_guide_index.json`
before citing anything), [[014]]/[[015]]/[[016]] (Bucket A/B/C precedents this triage's YELLOW/
Bucket-C-flag reasoning follows), [[017]]/[[018]] (asset-verification triage + its ready-to-build
verification discipline — the direct model for this block's zero-survivor shape-wiring check), [[021]]
(income-verification triage — the immediately preceding block, whose `SelfEmployedDocsShape`
never-wired finding is the same bug pattern this triage checked for and, this time, found no valid fix
for).
