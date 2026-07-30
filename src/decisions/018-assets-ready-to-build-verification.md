# 018 — Assets-triage "ready to build" candidates: verified, 3 of 6 survive

**Status:** Accepted 2026-07-30 (Gordon: "lets test them" / "I just need this working" —
pivoted from comparing rule engines to shipping real coverage on the tool already proven)

## Decision
Of the 6 "ready to build" candidates the Assets-block triage agent flagged
(`compiled/triage_asset-verification.json`), only **3 survive verification against the
actual AMQ row text**. The other 3 sounded plausible in the agent's summary but test a
materially different condition than what our current checks actually verify — wiring
them would have introduced false negatives, not just imprecision.

## Wired (verified correct)
| Exception code | Row | Verification |
|---|---|---|
| O-FNM-00215 | 218 | Already mapped (baseline) |
| O-FRD-50451 | 219 | **Byte-for-byte identical** condition text to O-FNM-00215 |
| O-FHA-50677-1 | 217 | Same failure mode (undocumented deposit >~50% income), FHA wording. Caveat: doesn't separately test "new accounts," and uses `base_monthly_income_1003` as a proxy for "adjusted income" — same core check, not a perfect textual match. |

## Rejected (verified NOT a match, despite the agent's "ready to build" label)
| Exception code | Row | Why it doesn't hold up |
|---|---|---|
| O-FRD-58101 | 102 | Tests whether an already-flagged deposit's source is an **acceptable category** (income/gift/eligible asset) — not merely "was it documented." Our shape only checks presence of documentation. A deposit could be fully documented yet still fail this row's actual test (documented source that isn't an acceptable type). Wiring it would silently pass a real defect. |
| O-VA-00262 | 226 | Needs a "this liability is secured by this specific deposit account" relationship. We extract tradelines and bank transactions as independent entity lists — the *relationship* between a specific liability and a specific deposit isn't captured by any field today. Not a join of existing data; needs new extraction. |
| O-RHS-57768 | 163 | Proposed reusing `cash_out_to_borrower_1003` — but that field is refinance terminology (`extract_loan.py`'s regex is literally `"Cash-Out to Borrower"`, populated only for loan 04's cash-out refi). This AMQ row is about gift-of-equity/sweat-equity cash back on a *purchase* transaction — the proposed field would never populate for the loans this rule targets. |

## Why this matters beyond these 3 rows
This is the second time a background agent's "ready to build" / "byte-for-byte duplicate"
claim needed correction on closer reading (the CIP guide-citation false-positive was the
first, decision 012). Standing lesson: **triage output is a lead to verify, never a
result to wire directly** — same discipline as [[001]]'s original catch of the rigged
NotebookLM script. Confidence language in an agent report ("highest confidence,"
"byte-for-byte duplicate") must still be checked against the actual source text before
any code changes; the two claims here that used exactly that confident language (O-FRD-
58101, O-VA-00262) were the ones that didn't hold up.

## Result
Ruleset recompiled (sha `233c922bb0b6`), audit re-run: 25/25 answer-key defects, 0
unexplained extras, 1 justified extra (loan 05 signature gap, decision 015), fully
deterministic. `LargeDepositShape` now correctly fires for Fannie, Freddie, and FHA
large-deposit variants.
