# 019 — Layer-2 triage of the credit-liabilities-review block: heaviest YELLOW skew yet, zero safe ready-to-build candidates, and a false-GREEN bug found in amq_compiler.py itself

**Status:** Accepted 2026-07-30 (Gordon — run the same triage method on credit-liabilities-review
as a third data point after application-verification and asset-verification)

## Decision
Triaged all 386 compiled `credit-liabilities-review` rules the same way as the prior two blocks
(`layer2_triage_credit_liabilities.py`, modeled on `layer2_triage.py`/`layer2_triage_assets.py`):
dedup by `(question_text, response_text)` → 382 unique groups, classify every group GREEN/YELLOW/
RED/NOT_A_CHECK with real per-group rationale, emit `compiled/triage_credit-liabilities-review.json`
+ `out/TRIAGE-PACKET-credit-liabilities-review.md`. Result:

| Bin | Groups | Rules | % of defect groups | application-verification | asset-verification |
|---|---|---|---|---|---|
| GREEN | 10 | 10 | 3% | 51% | 8% |
| YELLOW | 277 | 277 | 92% | 29% | 85% |
| RED | 15 | 15 | 5% | 20% | 7% |
| NOT_A_CHECK | 80 | 84 | — | — | — |

**Headline: the YELLOW skew gets worse, not better, and for the same root cause as asset-
verification.** Dedup barely collapses (386→382, ~1.01x — even less than asset-verification's
304→297, ~1.02x): the 5 AMQ agencies write almost entirely independent condition text per credit/
liability sub-topic. The 5-loan synthetic corpus (`demo/syn/loan 01`..`loan 05`) contains exactly
**one** credit report at all (loan 01), and it shows clean current tradelines with "None reported"
under Public Records / Collections / Derogatory. Every AMQ row in this block asking about
bankruptcy, foreclosure, short sale, judgments, collections, disputed accounts, tax liens, IRS
installment agreements, consumer credit counseling, non-traditional credit/VOR, mortgage
forbearance, or RMCR-format compliance is fixture-blocked for that one reason — the synthetic
corpus never modeled adverse credit or these document families — not because the condition is
unclear. RED stayed small (5%) for the same reason it did in asset-verification: most of this
block's math (percentage-of-balance thresholds, DTI inclusion, dollar thresholds) is crisp once
the data exists; genuine judgment calls ("significant," "reasonable," "satisfactory," "extenuating
circumstances," open-ended catch-alls) are a real minority, not the dominant failure mode.

## Method notes (both deliberate, both verified before assuming them)
1. **Dedup**: 386 rules → 382 groups, ~1.01x — verified, not assumed, same discipline as the prior
   two triages.
2. **Mechanical resolution**: `PASS_RE` (Yes/Not Applicable) plus 3 explicit screening/
   applicability overrides (2x "the loan program did not require a credit report to qualify" +
   1x a special-credit-considerations routing answer, all with an *empty* `exception_code` in the
   source row — the same signal application-verification's group 10 and asset-verification's
   group 291 used) account for 80 NOT_A_CHECK groups / 84 rules. The remaining ~302 substantive
   groups were individually read and classified by family (RED families for irreducible judgment
   calls; ~35 YELLOW families for fixture/derivation gaps), at the same rigor as the prior two
   scripts' hand-authored `C` dicts.

## The zero-exception-code shapes: searched, found no safe match (the decision-018 discipline applied one block earlier than expected)
`amq_compiler.py`'s `MAPPED_SHAPES` has **two** shapes already keyed to `credit-liabilities-review`
— `UndisclosedLiabilityShape` and `CashoutMortgageLateShape` — but **both are wired to zero
`amq_exception_codes`**, the identical bug pattern decisions 017/018 found and partly fixed for
`LargeDepositShape`/`GiftEvidenceShape`. Per this session's instructions, every AMQ row in this
block was searched for a real match to each shape's actual SPARQL logic (read from
`blocks/credit_liabilities.ttl`, not guessed from the shape's name) before calling anything ready:

- **`UndisclosedLiabilityShape`** (credit-report tradeline with no matching 1003 Section 2c
  liability, by amount): the closest textual matches are a family of "undisclosed debt" AMQ rows
  (`O-RHS-57144`/G118, `O-VA-00133`/G176, `O-FHA-02234`/G169+G256, `O-FHA-02232`/G381,
  `O-FHA-02233`/G382, `O-RHS-50563`, `O-RHS-02826`) — **every one of them bundles an additional
  requirement our shape doesn't test**: a borrower explanation obtained (G176), the payment amount
  verified and included in DTI (G169/G256), or resubmission to GUS/TOTAL (G118/G381/G382). Wiring
  any of these as a direct extension would risk **false negatives** — a loan could have the
  undisclosed debt our shape flags AND satisfy the AMQ row's real (compound) condition via a
  properly-documented explanation our shape can't see, or vice versa. None survive verification.
  Kept YELLOW, flagged in the packet (`F_UNDISCLOSED_DEBT` family), not wired.
- **`CashoutMortgageLateShape`** (`mortgage_late30_count_12mo > 0` AND `purpose_cashout_cd`, a
  Freddie Mac cash-out-refinance-seasoning check): searched the full ingested Post-Closing sheet,
  not just this block, for any row stating this exact condition for Freddie Mac. **None exists.**
  The nearest analogues are FHA-specific (`O-FHA-50024`, filed under the **Discarded** category and
  already excluded from compilation) and generic housing-payment-history rows with no cash-out
  gating at all (`O-FHA-02230`/G222). This shape appears to have been authored directly from
  general Selling Guide knowledge of the cash-out-refinance seasoning requirement (its own `.ttl`
  comment already says "SME to attach exact Guide section citation before production use") rather
  than from a specific AMQ row — it may simply have no AMQ-row counterpart in this ingested sheet.
  Flagged for a human to decide (attach a citation and leave unwired, or determine whether the
  Pre-Funding sheet — never ingested, see the CLAUDE.md program-gate note — has the matching row).

**Net: zero "ready to build" candidates this round**, in contrast to both prior triages (2/8 and
3/6 candidates respectively). This is itself the honest finding, not a gap in the triage — per the
task's explicit instruction to under-claim rather than repeat the Assets-round mistake.

## A second, more consequential finding: amq_compiler.py's OWN mechanical doc_presence classifier has a false-GREEN bug in this block
The prior two triages both deferred to `amq_compiler.py`'s `eval_class == "doc_presence"` as an
automatic GREEN (asset-verification's script says so explicitly: "already-mapped SHACL shape... /
auto-compiled doc-presence check... already works"). Applying the decision-018 discipline **one
level deeper** — verifying the mechanical classifier's own output against the full
`exception_description` text, not just trusting it — found that of the **24** rules this block's
`classify_eval()` tags `doc_presence`, only **5** are genuine "is a credit report present for this
applicant" checks. **The other 19 are compound conditions** (an undocumented business debt, an
unresolved DU-disputed-account message, a missing 12-month mortgage-payment history, a missing
24-month RMCR residency history, an undocumented significant-derogatory-reporting error, ...) that
got mechanically mis-routed to `doc_presence` purely because their `exception_description` text
happens to contain both a `NOT_IN_FILE_RE` trigger word ("missing," "not documented," "not
provided," ...) **and** the substring "credit report" somewhere in the sentence — not because "does
a credit_report document exist in the folder" is actually what the row is asking.

**Concrete proof this is a real bug, not a stylistic quibble**: `O-FNM-00200` ("Loan approval does
not evidence satisfactory credit risk for serious adverse credit reported") is the **byte-for-byte
identical FNM wording variant** of `O-VA-00143` (this triage's group 201) — this triage
independently classified the VA row **RED** ("satisfactory credit risk" is a holistic underwriter
judgment call, no bright-line test) purely from reading its text. The FNM twin got mechanically
auto-classified `doc_presence` → GREEN by `amq_compiler.py`, for the same real-world condition. If
wired as-is, this and the other 18 miscategorized rows would **silently PASS any loan that merely
has a credit_report document in its folder**, regardless of whether the loan's actual defect
(undocumented business debt, unresolved dispute, missing payment history, ...) is present — a
false-clear on a genuine defect, exactly what Non-Negotiable #1 (determinism + correctness) warns
against, and worse in kind than a coverage gap because it looks like automation that works.

All 24 were individually re-verified against their full `exception_description` text and
reclassified by hand in the triage script (`DOC_PRESENCE_VERIFIED_GREEN` / `DOC_PRESENCE_MISCLASSIFIED`
dicts) — 5 kept GREEN, 18 moved to YELLOW (their real condition needs a fixture/derivation this
corpus doesn't have), 1 (`O-FNM-00200`) moved to RED. **`amq_compiler.py` itself was NOT modified**
(off-limits for this exercise, same as decisions 017/018's regex-gap findings) — this is flagged
here for a human to patch: `classify_eval()`'s `doc_presence` branch needs the "is this literally a
document-presence check" test to require the NOT_IN_FILE_RE match to apply to the DOCUMENT NAME
itself, not merely co-occur anywhere in the same sentence as a document-type keyword.

## Rejected after verification (per the decision-018 self-check discipline)
- **`UndisclosedLiabilityShape` extension to any of G118/G169/G176/G256/G381/G382/`O-RHS-50563`/
  `O-RHS-02826`** — rejected; every candidate bundles a compound requirement (explanation obtained,
  DTI inclusion, GUS/TOTAL resubmission) the shape doesn't test. See above.
- **`CashoutMortgageLateShape` extension to any AMQ row** — rejected; no matching row found in the
  ingested Post-Closing sheet for Freddie Mac's exact condition. See above.
- **`O-FNM-00195`/"Previous Mortgage Payment History" as a `mortgage_late30_count_12mo` reuse** —
  considered and rejected: that fact is derived from the VOM (loan 04 only, one specific mortgage
  being refinanced), a 12-month **month-by-month** payment-history document; this row is about the
  **credit report's** own (different, shallower) mortgage-history field, which this pilot's
  `extract_tradelines()` doesn't parse at all. Reusing the VOM-derived fact here would be wrong —
  different document, different depth of history. Kept YELLOW as its own gap.

## What was NOT done (per instruction)
No `.ttl`, `extract_loan.py`, `amq_compiler.py`, or `run_audit.py` edit was made. `README.md`/
`JOURNAL.md` were not touched (other parallel sessions own those). This is triage + documentation
only, identical scope to the two prior rounds.

## Cross-links
[[009]] (full-workbook compile), [[012]] (Selling Guide grounding corpus — B3-5.x "Credit Score"/
"Credit Reports" and B3-6.x "Liabilities" chapters, confirmed present in `compiled/
selling_guide_index.json` before citing anything, same as the other two triages), [[014]]/[[015]]/
[[016]] (Bucket A/B/C precedents this triage's YELLOW/rejected-candidate reasoning follows),
[[017]]/[[018]] (the asset-verification triage and its ready-to-build verification discipline,
applied here one level deeper — to `amq_compiler.py`'s own mechanical classifier, not just this
triage's hand judgment — and finding a real bug as a result).
