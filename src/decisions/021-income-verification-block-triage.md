# 021 — Layer-2 triage of the income-verification block: YELLOW dominance goes even further than assets

**Status:** Accepted 2026-07-30 (Gordon — run the same triage method on income-verification, the
second-largest block after assets, as a third data point on how the 51/29/20 application-
verification ratio generalizes)

## Decision
Triaged all 616 compiled `income-verification` rules (`layer2_triage_income.py`, modeled on
`layer2_triage.py`/`layer2_triage_assets.py`): dedup by `(question_text, response_text)` to 580
unique groups, classify every group GREEN/YELLOW/RED/NOT_A_CHECK with real per-group rationale,
emit `compiled/triage_income-verification.json` + `out/TRIAGE-PACKET-income-verification.md`.
Result:

| Bin | Groups | Rules | % of defect groups | application-verification | asset-verification |
|---|---|---|---|---|---|
| GREEN | 28 | 28 | 6% | 51% | 8% |
| YELLOW | 467 | 482 | 93% | 29% | 85% |
| RED | 6 | 6 | 1% | 20% | 7% |
| NOT_A_CHECK | 79 | 100 | — | — | — |

**Headline finding: income-verification is even more lopsided toward YELLOW than assets was, and
RED nearly vanishes.** 93% YELLOW / 6% GREEN / 1% RED, versus assets' 85%/8%/7% and application-
verification's 29%/51%/20%. Two things drive this, both confirmed by reading the actual rows, not
inferred from a keyword count:

1. **Document-type breadth is even wider than assets.** The AMQ "Income" category spans 20+
   effectively-independent income sub-types (W-2 wage, self-employed/business, military, alimony/
   child support, rental — including ADU/boarder variants, trust, RSU/restricted stock, retirement/
   Social Security/disability, foster care, Section 8/MCC/housing-assistance, 1099/K-1, capital
   gains, virtual currency, ...), each with its own required document family per agency guide. The
   5-loan synthetic corpus was built to cover one wage-earner profile (loan 01), one self-employed
   profile with only YTD-P&L/balance-sheet presence tracked (loan 04), and one USDA income-limit
   profile (loan 05) — it was never meant to, and does not, cover the other ~18 income types this
   category checks.
2. **RED all but disappears because the math genuinely is well-defined, not because the block is
   less rigorous.** Every agency's Selling/AMQ guide specifies exact history-and-continuance periods
   (2 years, 3 years, 12 months...), exact percentage thresholds (10%/20%/30% fluctuation bands, 50%
   grossed-up caps, 30% boarder-income caps), and exact required-document lists per income type —
   almost none of it is left to underwriter discretion the way "reasonable"/"appropriate" catch-alls
   are in the other two blocks. Six genuinely bare judgment calls survived a full read of all 474
   substantive groups (see RED below); everything else that LOOKED judgment-flavored on a keyword
   scan (a stated 20% threshold attached to "not supported and logical," a presence-of-analysis fact
   attached to "unreasonable") turned out, on reading the full condition text, to have a crisp,
   checkable component and was classified YELLOW instead — see "Keyword false positives caught"
   below.

## Method differences from the first two blocks (both deliberate, both stated up front in the script)
1. **Dedup collapse (616→580, ~1.06x)** sits between application-verification's ~1.5x and asset-
   verification's ~1.02x — the 5 agencies mostly write independent text per income sub-type, but a
   real set of condition texts recurs **verbatim across many different AMQ question categories**
   (not just within one), a pattern asset-verification's G040/G081/G102 triage first noticed at small
   scale (2-3 repeats). Here it is much larger: **19 groups** share the literal text "Income
   submitted to AUS is not accurate - broken out and/or categorized correctly" across 19 different
   income-type question categories (automobile allowance, alimony, disability, employment, general
   income, housing assistance, military, other income, retirement, self-employed, trust income, ...).
   Six such recurring code families exist total (Income Breakdown x19, VVOE Inactive x7, 3rdParty x5,
   IncomeWork x5, plus smaller ones) — each was read in full once and the same classification applied
   everywhere that exact code recurs, rather than re-deriving it 19 times.
2. **GREEN is 100% mechanical `doc_presence` — zero `mapped`.** `amq_compiler.py`'s `MAPPED_SHAPES`
   lists `SelfEmployedDocsShape` for this block, but wires it to `amq_exception_codes: []` — the same
   "shape exists, never fires" bug already found and fixed for `GiftEvidenceShape`/`LargeDepositShape`
   in decisions 017/018. This triage is the first time anyone checked whether *other* income-block AMQ
   rows describe the same condition `SelfEmployedDocsShape` already tests (see READY TO BUILD below).
3. **Scale forced a different classification technique for the ~474 groups requiring real judgment**
   (more than double asset-verification's ~210): six recurring code families classified once each
   (above); six individually hand-verified RED calls (below); two verified READY_TO_BUILD candidates
   (below); and — for the remainder — a deterministic keyword scan of each row's own text against a
   curated list of ~35 income-document families, stating per group which specific document/fact
   family the row is missing, grounded in that row's own text (never inventing a family the text
   doesn't itself name — the grounding rule from the rule-fidelity audit). This is a documented,
   reproducible technique (`layer2_triage_income.py`'s `classify_fallback`), not a giant hand-typed
   dict — necessary at this scale, but disclosed as such rather than presented as uniformly
   hand-authored like the first two blocks' `C` dicts.

## READY TO BUILD candidates — verified per decision-018 discipline
Two candidates, both wiring `SelfEmployedDocsShape` (`CHK-INC-001`) to real AMQ exception codes for
the first time since it was built:

| Exception code | Row | Verification |
|---|---|---|
| O-VA-00364 | 2487 | Response: "File missing a YTD P&L and current balance sheet as applicable or as per AUS for self-employed." exception_description: "the file did not contain a YTD profit and loss statement and current balance sheet as applicable or as per AUS." Read against the shape's actual SPARQL (`blocks/income.ttl`): `borrower_self_employed=true` AND (`ytd_pnl_in_file=false` OR `ytd_balance_sheet_in_file=false`) — an either-missing test. The natural reading of "the file did not contain [P&L] and [balance sheet]" applied to a required document PAIR is that the pair is incomplete if either is absent — the same real-world condition, not just similar-sounding text. Loan 04's own Self-Employed Income Documentation Index (the only synthetic fixture exercising this shape) marks BOTH docs "NOT IN FILE," so this row and the shape would agree on that loan today. |
| O-FHA-02293 | 2410 | Response: "A YTD profit and loss statement and balance sheet were not provided." exception_description: "A YTD P&L and balance sheet was required but not in the file where more than a calendar quarter has elapsed since the date of most recent calendar or fiscal year-end tax return was filed by the borrower." Same either-missing-from-the-required-pair reading as O-VA-00364, FHA wording variant. |

**Self-check performed (decision-018 discipline):** a full-text keyword sweep of every one of the
~40 self-employed/business-income groups in this block for "profit and loss," "balance sheet," and
"P&L" together found **no other agency row** naming both documents as a pair — these two are the
only matches, not an assumption. Other self-employed rows name a different, non-overlapping
condition (business tax returns, K-1 documentation, business-existence verification, Schedule C
deductions, the Freddie Mac Income Analysis Form) and were correctly kept as separate YELLOW groups,
not folded into this candidate.

**Not** classified as GREEN — matches asset-verification's own precedent (its G135/G102 READY_TO_BUILD
candidates stayed YELLOW too): wiring is a proposed `amq_compiler.py` change a human has not yet made.

## RED — six candidates, individually verified (no bulk judgment-keyword bucketing)
Every group whose condition text contained a judgment-flavored word ("reasonable," "unreasonable,"
"logical," "appropriate," "adequate," "stable") was read in full — question, response, AND
exception_description — before being called RED. Six survived that read with genuinely no crisp,
checkable component:

- **G025 (O-VA-00406)** — "Income used not addressed by VA... continuance was unreasonable." Income
  source not enumerated by VA guidance at all; nothing to check against until an SME names what
  documentation would even apply.
- **G122 (O-RHS-02785)** — "UW analysis does not support stability and continuance." The analysis
  EXISTS (unlike most "analysis not documented" rows elsewhere in this block, which are presence
  checks and stayed YELLOW) — this judges whether its content is adequate, with no bright-line test.
- **G168 (O-RHS-02829)** — "Noted income discrepancies were not resolved." Open-ended cross-file
  discrepancy sweep, same class as application-verification's file-wide-discrepancies RED.
- **G180 (O-FRD-50420)** — "Assets used as income not reasonable/stable," no document or threshold
  named anywhere in the row, same class as asset-verification's G035.
- **G310 (O-FRD-55384)** — "Necessary additional documentation... to evaluate, justify and explain
  the qualification," a fully open catch-all naming nothing specific.
- **G538 (O-FHA-02289)** — "The self-employment income is not stable," bare conclusion; every other
  self-employed row in the block names a specific document, this one names none.

## Keyword false positives caught (would have been mis-classified RED on a naive scan)
Read in full and reclassified YELLOW because a genuinely checkable fact survived the judgment word:
- **G041 (O-VA-00310)**: "continued employment is unreasonable & analysis not documented" — the
  analysis-presence half is crisp; only the reasonableness judgment on top stays human (kept YELLOW,
  same compound-condition precedent as asset-verification's G007/G225).
- **G127 (O-RHS-51844)**: "sharp increase/decrease of 20% or more that was not supported and
  logical" — the 20% swing itself is a crisp, computable threshold; only "supported and logical"
  stays human.
- **G304 (O-FRD-50421)** / **G435 (O-FNM-55655)**: both evaluate whether the CORRECT guide-defined
  methodology was used for a given income-type/time-in-service fact pattern — the methodology itself
  is guide-defined (B3-3.4-01, B3-3.8-01), not left to discretion, so kept YELLOW (blocked on missing
  classification fields) rather than RED.
- **G383 (O-FHA-02311)**: response text says "not adequately documented & supported" (sounds RED),
  but exception_description is far more concrete: "not from a non-taxable source and/or was
  calculated incorrectly" — two crisp, checkable facts. Classified from the fuller description, not
  the terser response gloss, per the same discipline that surfaced the P&L/balance-sheet READY_TO_
  BUILD match above.
- **G348 (O-FRD-50432)**: "all req's not met" reads like a bare catch-all, but the description
  narrows it to a specific comparable date fact (income start date vs. Note date) with an appended
  open "all requirements" tail — crisp presence half kept YELLOW, tail noted as stays_human, same
  precedent as asset-verification's G007.

## What was NOT done (per instruction)
No `.ttl`, `amq_compiler.py`, `extract_loan.py`, or `run_audit.py` edit was made. `README.md` and
`JOURNAL.md` were not touched (other parallel agents were mid-edit on those files). No candidate was
unilaterally wired — both READY_TO_BUILD candidates and all RED calls are flagged for a human
decision, exactly like the two prior block triages.

## Cross-links
[[009]] (two-layer compile pattern this triage executes for a third block), [[012]] (Selling Guide
grounding corpus — B3-3.x "Income Assessment" chapters, e.g. B3-3.1-01 through B3-3.8-01, confirmed
present in `compiled/selling_guide_index.json` before citing anything), [[014]]/[[015]]/[[016]]
(Bucket A/B/C precedents this triage's YELLOW/READY-TO-BUILD reasoning follows), [[017]]/[[018]]
(asset-verification triage + its ready-to-build verification discipline — the direct model for this
block's method and the source of the "confidence language must still be checked against actual text"
lesson applied throughout, including the G383/G348 "read the fuller description, not the response
gloss" catches above).
