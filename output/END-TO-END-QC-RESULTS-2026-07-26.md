# End-to-End QC Results — Gift-Letter Fix Proven on Real Loans

**Run**: `run_011_retail_only_002g` · 2026-07-26 · fully deterministic (zero LLM calls, zero cost)
**For**: Kayla — this is the *results* review, not a mechanism review. Every number below comes from
`result/qc_results/run_011_retail_only_002g_results.json`, reproducible by running
`python3 p0/compile_runs/run_011_retail_only_002g/build_and_run.py`.

---

## The headline, in one paragraph

On the July 24 review call you found the tool raising gift-letter exceptions on a loan that never
used gift funds, and said: *"we would want a result of an NA, not applicable."* That is now what
happens, proven on the real loan files: **60 false exceptions cleared** — 15 gift-related checks ×
the 4 loans that genuinely used no gift funds each flipped from FAIL to NOT_APPLICABLE — while on
the one loan that **did** use gift funds (loan 02, the FHA loan with the donor letter), **all 15
checks stayed active and still caught its real planted defect** (the missing gift-funds paper
trail). Nothing was suppressed; only the noise went away.

| | Before (deployed ruleset) | After (this run) |
|---|---|---|
| Loans 01/03/04/05 (no gift funds) | 15 gift checks **FAIL** each — 60 false exceptions a reviewer must clear by hand | 15 × **NOT_APPLICABLE** each — zero touches |
| Loan 02 (real gift loan) | gift checks evaluated | gift checks **still evaluated — real defect still caught** |
| Every flip, accounted for | — | **All 60 flips are FAIL → NOT_APPLICABLE. No other status moved.** |

The 15 gated checks are the genuinely gift-specific ones (`fha-gift-letter-complete`,
`fha-gift-source-acceptable`, `cash-back-gift-equity-sweat-rent`, ...) — full list in the results
JSON.

## How the gate decides (and why you can audit it)

The gate is not a model's opinion. Your own rule spreadsheet already encodes it: 362 rows are gated
by the workbook's asset-type question (QuestionID 570606), and the rows behind these 15 checks fire
only when the answer is **"Yes - Gift"**. We decoded that structure directly from the spreadsheet
(deterministic clustering — no AI at any point in this chain), mapped "Yes - Gift" onto one named
loan fact (`gift_funds_used`), and the engine checks that fact per loan before running the check.
Same loan in, same answer out, every time — and every gate traces to the exact spreadsheet rows it
came from.

Where the loan's gift status comes from in this run: each loan file's own extracted
`doc_present_gift_letter` fact (loan 02 = true — it has the real donor letter, name, address,
signature date; the other four = false). That derivation is disclosed, not hidden.

## What else this run cleaned up (same run, same determinism)

1. **Retail-only re-basis** (the decision from July 24, now executed): of run_010's 4,506 compiled
   checks, **3,330 kept** (every source row from the Retail workbook), **923 dropped**
   (Private-Bank-only), **253 dropped** (mixed-source). The deployed ruleset still mixes those in.
2. **Operator-direction gate**: **127 checks excluded** from the new ruleset because their compiled
   operator contradicts their own pass-message (the family of the LTV-inversion bug you saw — the
   kind that would clear a 98%-LTV loan). They are listed by id in the results JSON for review,
   never silently signed.
3. Net new ruleset: **3,203 checks**, `result/rules/retail_only_002g_ruleset.json` — explicitly
   marked NOT SIGNED, pending your review.

## Your review agenda, ranked by impact (this is the ask)

The gift fact is deliberately the only one wired so far — every other gated rule refuses to guess
and is flagged instead (2,035 checks flagged; 1,153 genuinely unconditional). The flags are not a
backlog of errors; they are the **vocabulary waiting to be confirmed**, and the run counted exactly
which confirmations buy the most:

| Spreadsheet question | Unbound answers seen | Checks waiting on it |
|---|---|---|
| 570906 — alimony / child support / separate maintenance | "Alimony, Child Support..." | 152 |
| 571199 / 571198 / 571197 — "Yes, there is..." family | various | 295 |
| 570606 — the other 16 asset types (Business Assets, Retirement, Grant, ...) | 16 answers | ~93+ |

Confirming one question's mapping (this answer means this loan fact, true/false) immediately gates
every check behind it — the same 5-minute review shape as the gift fact, repeated. **"Yes - Grant"
is a ready-made first case**: two real gift rows gate on Gift OR Grant, and the system refused to
treat a grant as a gift without your say-so — those two rows are flagged, waiting.

## Honest caveats (so nothing here oversells)

- The fact vocabulary and the ingested Selling Guide corpus are both signed with an explicit
  placeholder (`NOT-A-REAL-SME-pending-kayla-review`) — the machinery enforces sign-off; the
  sign-off itself is what your review provides.
- All 5 loans still land NEEDS_REVIEW overall — expected: 3,203 checks against ~70 extracted fields
  per loan means most checks lack their field and honestly say so. The win measured here is the
  **delta** (60 false exceptions eliminated, zero real detections lost), not a finished green
  dashboard.
- `gift_funds_used` is derived from `doc_present_gift_letter` in this run; the extraction contract
  should eventually deliver it directly (tracked as an interface note, 002e/002g).
