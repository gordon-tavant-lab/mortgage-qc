# Resolve7 — round 2 on the remaining NOT_COMPILED (2026-08-01)

Gordon's ask: "are there more NOT_COMPILED we can compile? can we run another round."
Round 2 targeted the three buckets round 1 (resolve6) never examined row-by-row:
`threshold_not_parseable` (175), `trigger_gated_needs_fact_machinery` (103), and
`date_window` (56) — 334 rows total.

**Headline: 161 more checks resolved — NOT_COMPILED 599 → 439, NOT_APPLICABLE
284 → 443, PASS 130 → 131 — plus one honest retraction: an existing NOT_APPLICABLE
was corrected back to NOT_COMPILED after the verifier found the payload contradicts
its cited fact. Zero previously-evaluated verdicts changed otherwise; all gates
green; both engines agree (121 jointly evaluated, 0 disagreements; NA 443 == 443).**

## Cumulative (all 1,105 gold-ruleset checks, loan 12607601215)

| Status | Audit report | After resolve6 | After resolve7 |
|---|---|---|---|
| PASS | 121 | 130 | **131** |
| NEEDS_REVIEW | 92 | 92 | **92** |
| NOT_APPLICABLE | 43 | 284 | **443** |
| NOT_COMPILED | 849 | 599 | **439** |
| Evaluated | 256 | 506 | **666 (60%)** |

## What round 2 found

1. **The three buckets had zero scenario-table coverage.** Round 1's table extension
   covered the computation/cross-doc/presence buckets; none of these 334 keys were
   in it. Analysis found 168 rows whose trigger scenario is provably false for this
   loan; the adversarial verifier accepted 151 new + 9 UNKNOWN→NA flips and
   **rejected 8** (5 absence-inference-only including the ADU trio, 1 HomeReady-LLPA
   inversion trap — "not HomeReady" doesn't preclude the erroneous-LLPA defect the
   check exists to catch, 1 unprovable disjunct, 1 circular trigger conjunct).
2. **Three more compiler dispatch bugs, same disease as round 1**: the
   `date_window`/`NOT_CONVERTED_TYPES`, `threshold_eligibility`-parse-failure, and
   computation-parse-failure branches all dropped to NOT_COMPILED *before* the
   scenario gate could fire. Fixed identically (scenario-gated-stub fallback). src
   needed no change — its runtime overlay already covers every unsupported type.
3. **New payload-fact discoveries** (SFHA-style — facts previously marked
   "unknowable" that are actually extracted): `amortizationType=FIXED` (kills the
   ARM gate), `citizenshipResidencyType=USCitizen` (2 non-US-citizen gates),
   `propertyEstateType=FeeSimple` (leasehold), the SFHA indicator (3 more rows),
   `assetType=GIFT_OF_CASH`+`fundSourceType=RELATIVE` (gift-of-equity, flagged),
   income enumeration living at `currentIncome[0..4].basePay` summing exactly to
   the 19,500 qualifying income.
4. **One real PASS wire**: ATR-QM `O-FRD-54594` "loan term exceeded 30 years" —
   the only unambiguously parseable threshold in all 175 rows (regex missed it
   because the bound is in years, the field in months). 360 ≤ 360 → PASS, backed by
   `loanSummary.amortization.loanAmortizationPeriodCount`.
5. **One honest retraction (self-correction)**: existing NA row
   `PC::O-FNM-15358/O-FNM-00544` cited "no disaster impact evidenced anywhere" —
   but the payload carries `disasterSummary[0]` = FEMA **DR-4909-HI** (Flood,
   declared 2026-04-07) for the subject's own county, predating the 2026-07-21
   application. Flipped NA → UNKNOWN (an area declaration isn't proof of
   property-level impact either); the check honestly returns to NOT_COMPILED.
   This is the adversarial-verification discipline catching a round-1-era error.

## What honestly remains (439 NOT_COMPILED)

| Bucket | Count | Real blocker |
|---|---|---|
| trigger_gated | 95 | facts genuinely absent (LEP/language, alimony, military, DU/AUS relief, APOR) |
| presence_gate | 79 | 52 appraisal-content rows blocked on Form 1004 field extraction |
| by-design | 72 | 24 reverification + 21 list_screening (out of scope) + 27 date_window blocked on dates |
| cross-doc | 62 | second comparison side unextracted |
| threshold | 52 | 39 genuinely-ambiguous texts (SME) + 7 field-not-populated + 6 rejected-NA |
| computation | 48 | inputs null (liabilities, APOR, HOI amounts) + 12 SME-ambiguous |
| demo_excluded / compound / rejected-presence | 31 | deliberate scope + no safe mapping |

**Date starvation is the date_window story**: the payload carries only 3 substantive
loan-level dates; the note date and closing date — anchors for most windows — exist
nowhere (all 62 `documents[].documentDate` are null). The populated dates are also
mutually inconsistent (originator signed 19 months before application; 2023 bank
statements on a 2026 loan) — worth adding to the Touchless data-quality bug list.
Top vendor asks by unlock count, updated: Form 1004 extraction, DU/AUS findings,
note/closing dates + documentDate, APOR join (APR 7.401 already extracted — the
FFIEC table alone decides both HPML rows), LEP `language` field, liability detail.

## SME queue additions (in `sme-review-queue.md`)

- 6 new spot-check-flagged NA rows (gift-of-equity pair, EPD Freddie-sale, UGV
  portfolio-gate, ECOA consummation inference, eMortgage conjunct).
- Verifier flags on two *existing* rows: the trust-account NA shares the
  Custodial-Acct doc-granularity weakness; the two ADU NAs rest on the demo-scoped
  ASSUMED fact rather than payload proof.
- 39 genuinely-ambiguous thresholds + 4 ambiguous date windows ("timely",
  "immediately") — resolvable only by Kayla; the compiler refusing to guess here is
  the product's core discipline, not a gap.
- Negative-control follow-up (silent-false-negative discipline): the 9 UNKNOWN→NA
  flips should each get a mutation fixture (flip the deciding fact, assert the
  check un-gates) before the stubs are trusted beyond the demo.

## Gates

- `pytest p0/` 445 passed · `verify_against_defects.py` 25/25 · cross-engine 121
  agree / 0 disagree, NA parity 443 == 443.
- Per-check diff vs HEAD: 160 × NOT_COMPILED→NOT_APPLICABLE, 1 × NOT_COMPILED→PASS,
  1 × NOT_APPLICABLE→NOT_COMPILED (the disaster retraction), zero other flips.
- Deliverables refreshed: audit CSV + 3-sheet xlsx (both copies).

## Is there a round 3?

Diminishing returns from here without new inputs. The remaining 439 split into:
SME-answerable (~55 ambiguous texts — cheapest next unlock, needs Kayla not code),
vendor-answerable (~250 blocked on extraction/data), by-design out of scope (~65),
and deliberate demo scope (~31). A round 3 worth running would be *after* either
Kayla's first SME-queue session or a vendor extraction widening — not before.
