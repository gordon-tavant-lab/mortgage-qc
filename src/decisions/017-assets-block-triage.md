# 017 — Layer-2 triage of the asset-verification block: the 51/29/20 ratio does NOT generalize

**Status:** Accepted 2026-07-30 (Gordon — run the application-verification triage method on
asset-verification as a test of whether its bin ratios hold on a larger, math-heavier block)

## Decision
Triaged all 304 compiled `asset-verification` rules the same way application-verification was
triaged (`layer2_triage_assets.py`, modeled directly on `layer2_triage.py`): dedup by
`(question_text, response_text)`, classify every unique group GREEN/YELLOW/RED/NOT_A_CHECK with
real per-group rationale, emit `compiled/triage_asset-verification.json` +
`out/TRIAGE-PACKET-asset-verification.md`. Result:

| Bin | Groups | Rules | % of defect groups | application-verification (for comparison) |
|---|---|---|---|---|
| GREEN | 18 | 18 | 8% | 51% |
| YELLOW | 193 | 193 | 85% | 29% |
| RED | 17 | 18 | 7% | 20% |
| NOT_A_CHECK | 69 | 75 | — | — |

**Headline finding: the 51/29/20 ratio does not generalize — it inverts.** Asset-verification is
~8% GREEN / ~85% YELLOW / ~7% RED, versus application-verification's ~51% GREEN / ~29% YELLOW /
~20% RED. Both the qualitative RED share and the GREEN share moved in the opposite direction from
what "more math-heavy" might suggest: RED did not grow (asset math is mostly crisp threshold
comparisons — 50%, 1%, 60%, 20%, $250, 2%, 6% — not judgment calls), but YELLOW absorbed almost
everything, because the AMQ "Assets" category spans **dozens of distinct asset-type document
families** (VOD forms, retirement/brokerage/trust statements, bridge-loan notes, subordination
agreements, DU/LPA/TOTAL AUS findings, foreign-asset/cryptocurrency confirmations, sweat-equity and
trade-equity documentation, custodial-account statements, EAH/IDA/pooled-savings program
agreements, rent-to-own leases, ...) — and the 5-loan synthetic corpus (`demo/syn/loan 01`..`loan
05`) was built to cover one document set per program, not this asset-type breadth. Unlike
application-verification (where only 12 of 16 YELLOW groups were fixture-blocked, ~75%), here the
overwhelming majority of the 193 YELLOW groups are fixture-blocked in the same decision-014 sense —
this is a genuine qualitative difference in kind, not a sign the block was triaged less carefully.

## Method differences from application-verification (both deliberate, both stated up front)
1. **Dedup barely collapses here**: 304 rules → 297 unique groups (~1.02x), versus 81→54 (~1.5x)
   for application-verification. Verified empirically before assuming otherwise — the 5 AMQ
   agencies write almost entirely independent condition text per asset sub-type instead of reusing
   a small shared phrase set the way application-verification's disclosure/URLA rules did.
2. Given ~297 groups, **GREEN and NOT_A_CHECK for the ~87 mechanically-resolvable groups are
   derived from data amq_compiler.py already computes** (`eval_class` in `{mapped, doc_presence}`,
   and a pass/N-A regex on the condition text) rather than hand-typed one at a time — this mirrors
   the reference script's own `blocked_on_missing_fixture` override, which already deferred to
   `eval_class` at runtime instead of re-deriving that judgment by hand per group. The remaining
   ~210 groups that actually require reading AMQ text and exercising judgment were individually
   classified by hand in `layer2_triage_assets.py`'s `C` dict, at the same rigor as the reference
   script. One group (291, "The loan program did not require assets to qualify") was a screening/
   applicability answer branch that didn't match the Yes/N-A regex verbatim and was reclassified
   NOT_A_CHECK by explicit override — the same pattern as application-verification's group 10
   (LEP-applicability screening question).

## READY TO BUILD candidates found (flagged only — not implemented, per instruction)
Six candidates, ranked by confidence, all cited with exact locations in the packet's "READY TO
BUILD" section:

1. **G135 (O-RHS-02772, "No, proof of transfer not provided") — WIRE, don't build.**
   `GiftEvidenceShape` (`CHK-AST-002`, `blocks/assets.ttl`) already implements exactly this fact
   (`gift_transfer_evidence_in_file`), but `amq_compiler.py`'s `MAPPED_SHAPES` wires it to **zero**
   `amq_exception_codes` (`"GiftEvidenceShape": {..., "amq_exception_codes": []}`) — the shape has
   never fired for any real AMQ rule. Adding `O-RHS-02772` to that list is a genuine 1-line change,
   cheaper than the co-borrower fix (decision 015) that started this whole triage exercise. G108,
   G127, G131, G296 are plausible near-relatives of the same fact but bundle extra clauses (donor
   ability, named-recipient variants) — flagged as "worth SME review before wiring," not blind
   copies of this fix.
2. **G102 (O-FRD-50451)** — condition text is a **byte-for-byte duplicate** of the already-mapped
   O-FNM-00215 row (group 287, `LargeDepositShape`/`CHK-AST-001`), filed under a different AMQ
   question category ("general asset documentation" vs "verification of deposit assets"). Highest-
   confidence large-deposit extension candidate.
3. **G025 (O-FRD-58101)** and **G064 (O-FHA-50677-1)** — same unsourced-large-deposit defect
   `LargeDepositShape` already encodes for FNM, FRD/FHA wording variants. Extend the shape's
   `amq_exception_codes` list; verify wording match before wiring (per instruction — not done here).
4. **G011 (O-VA-00262, "loan outstanding secured by funds on deposit... treated as an asset")** —
   new derivation, zero new fixture: checkable by cross-referencing `tradelines`/
   `urla_liabilities` against `bank_txns`, all three of which `extract_loan.py` already extracts.
5. **G130 (O-RHS-57768, cash back at closing from gift/sweat-equity/rent credits)** — partial win:
   the gift-fund half is cross-referenceable today against `cash_out_to_borrower_1003` (already
   extracted) + `gift_transfer_evidence_in_file`; the sweat-equity/rent-credit half still needs new
   fixtures.

Two more Bucket-B-adjacent (not top-tier, mentioned in the packet, not the headline list): G289
(FNM bank-statement account-identifying-info field) and G066/G125 (bank-statement balance
aggregation / gift-letter amount field) — small, plausible field additions to documents already in
the corpus.

## Bucket-C-style external-lookup candidate flagged (not discarded — human decides, per decision 016's precedent)
**G218 (O-FHA-02269, "commission for cash to close without verifying borr RE license/commission
entitlement")** — borderline. A license copy in the file might suffice for a file-level check, but
genuinely *current* license status could require a state real-estate-licensing-board lookup, the
same kind of live-registry dependency that got the NMLS rule (decision 016) discarded from PoC
scope. Flagged in the packet, **not** unilaterally classified as Bucket C or removed from
`amq_compiler.py` — a human should decide, exactly as instructed. (G079's 501(c)(3) charitable-
status check was considered and rejected as a Bucket-C candidate — unlike an RE license or NMLS ID,
nonprofit status is normally evidenced by a document already in a shop's file, an IRS determination
letter, not a live lookup — kept as an ordinary blocked-on-missing-fixture YELLOW.)

## A second systemic gap, distinct from the fixture gap above
No purchase/sales contract document exists as a doc type anywhere in `demo/syn/loan 01`..`loan 05`
— several earnest-money-deposit rules (G040, G081, G084, G086, G082) all trace back to this single
missing document family. Worth flagging alongside the DU/LPA/TOTAL AUS-findings gap (present for
RHS via `gus_findings`, absent for FNM/FRD/FHA) as a natural next-fixture-generation priority if
this block's YELLOW rate is ever to move.

## What was NOT done (per instruction)
No `.ttl`, `.py` (other than the new triage script itself), or `amq_compiler.py` edit was made.
`extract_loan.py` and `run_audit.py` were not touched. No Bucket-C candidate was discarded
unilaterally. This is triage + documentation only, exactly like application-verification's triage
before any code was built from it (decisions 014-016).

## Cross-links
[[009]] (full-workbook compile; two-layer compile pattern this triage executes for a second block),
[[012]] (Selling Guide grounding corpus — B3-4.x "Verification of Deposits and Assets" is the
natural chapter for this block's guide citations, confirmed present in `compiled/
selling_guide_index.json` before citing anything), [[014]]/[[015]]/[[016]] (the application-
verification Bucket A/B/C precedents this triage's YELLOW/READY-TO-BUILD/Bucket-C-candidate
reasoning follows).
