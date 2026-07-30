# 023 — Layer-2 triage of the product-specific-check block: near-zero duplication, zero GREEN, two orphaned shapes found

**Status:** Accepted 2026-07-30 (Gordon — run the same triage method on "product-specific-check",
704 rules, third-largest block and by nature the most agency/product-fragmented)

## Decision
Triaged all 704 compiled `product-specific-check` rules the same way application-verification and
asset-verification were triaged (`layer2_triage_product_specific.py`, adapted from
`layer2_triage_assets.py` per instruction): dedup by `(question_text, response_text)`, classify
every unique group GREEN/YELLOW/RED/NOT_A_CHECK with real per-group rationale, emit
`compiled/triage_product-specific-check.json` + `out/TRIAGE-PACKET-product-specific-check.md`.
Result:

| Bin | Groups | Rules | % of defect groups | application-verification | asset-verification |
|---|---|---|---|---|---|
| GREEN | 0 | 0 | 0% | 51% | 8% |
| YELLOW | 572 | 572 | 97% | 29% | 85% |
| RED | 17 | 17 | 3% | 20% | 7% |
| NOT_A_CHECK | 114 | 115 | — | — | — |

**Headline finding #1: zero GREEN groups — the lowest automatable-now fraction of the three blocks
triaged so far, and it drops to exactly zero, not just "low."** Both of this block's pre-existing
SHACL shapes (`AmendatoryClauseShape`, `UsdaIncomeLimitShape` — both wired to zero AMQ exception
codes already, the same "built but never connected" bug pattern decisions 017/018 fixed for
`LargeDepositShape`/`GiftEvidenceShape`) were checked against every row in this block. Neither
survives: see the REJECTED section.

**Headline finding #2: dedup is essentially ZERO — 704 rules → 703 unique groups (~1.001x), even
smaller than asset-verification's already-small 304→297 (~1.02x), confirmed empirically rather than
assumed going in.** This is the block's defining character, exactly as anticipated: "Product
Specific" spans FHA/VA/USDA/ARM/refi-program-specific rules — RefiNow, HomeReady, HomeStyle,
CHOICERenovation, Home Possible, Refi Possible, GreenCHOICE, IRRRLs, Texas 50(a)(6), Section
502/RHS refinance variants, and a family of proprietary lender "Portfolio"/CTP internal-overlay
rules coded `GENERIC` — where nearly every agency writes its own program in its own wording. Unlike
application-verification (disclosure/URLA language reused across 5 agencies, 1.5x collapse) or even
asset-verification (some shared asset-type phrasing, 1.02x collapse), this block has almost no
shared phrase pool at all.

**Headline finding #3 (the important methodological one): `eval_class == "doc_presence"` is NOT a
reliable GREEN signal in this block, unlike asset-verification.** All 8 groups amq_compiler.py
mechanically classified `doc_presence` here were individually re-verified against the actual AMQ
row text and found to be **false positives** — the keyword-matching regex hit a generic doc-type
word (`"appraisal"` appearing incidentally in "an inspection... was not in the file", the
pre-existing "initial application"→`final_1003` bug already flagged in decision 014 recurring here,
`"title policy"` matching when the real requirement is a specific clause *within* the title policy)
inside a condition that actually needs a much narrower sub-form or sub-fact the coarse presence
check cannot see. Trusting `eval_class` here the way asset-verification's triage correctly did
would have repeated exactly the mistake decision 018 warns against, one layer down (the mechanical
classifier, not an LLM's summary). All 8 are downgraded to YELLOW with the specific bug named per
group — see the JSON/packet's `G058/G059/G210/G327/G415/G418/G461/G524`.

## Method (disclosed up front, per the scale this block required)
Given ~703 groups and near-zero mechanical dedup, full one-by-one hand-authored prose for every
group (as application-verification's 54 and asset-verification's ~210 substantive groups received)
is not tractable in one sitting. Four-part method, transparent in the script's module docstring and
in each group's `classification_method` field:
1. **NOT_A_CHECK** — `PASS_RE` (`^(Yes,|Not Applicable)`), same convention as both prior scripts,
   PLUS 6 individually-verified overrides (`NOT_A_CHECK_OVERRIDES = {1,2,3,4,5,409}`): G001-G005 are
   a "was this loan originated under a specific product or program?" menu whose answer *names* the
   product (Buydown/ARM/Combination Construction-to-Permanent/...) rather than stating a pass/fail
   condition — a routing branch to this same block's program-specific follow-up questions, the same
   pattern as application-verification's G010 and asset-verification's G291. G409's answer is the
   bare word `"Yes"` with no trailing comma, which `PASS_RE`'s comma-anchored pattern doesn't catch.
   Found by cross-checking every group with a **blank exception_code** (114 such groups exist in
   this block — a strong mechanical signal; 108 already matched `PASS_RE` and needed no override).
2. **The 8 `doc_presence` groups** — hand-verified individually, not trusted from `eval_class` (see
   headline #3).
3. **~90 groups flagged by a RED-signal keyword scan** (`reasonable`, `appropriate`, `acceptable`,
   `sufficient`, bare `"all requirements"`, `"indicators"`-of-fraud language, etc.) were each
   individually read in FULL (question + condition + exception_description) and hand-classified
   RED or YELLOW, applying the same rule asset-verification's triage used: a compound condition
   with ANY crisp, named, checkable component (a document, a number, a date) stays YELLOW even with
   a judgment clause appended; only conditions that are wholly and irreducibly an unqualified
   judgment call — no document, no number, no named comparison basis anywhere in the row — are RED.
4. **The remaining ~500 groups** (crisp-sounding, program-specific presence/threshold conditions
   with no RED-signal keyword) are classified YELLOW by a documented, deterministic heuristic
   (`classify_bulk_yellow`): does the condition reference a document type `extract_loan.py`'s
   `DOC_TYPES` already parses (→ "Bucket-B-style: deepen an existing doc, no new fixture") or a
   document family absent from every synthetic loan (→ "blocked_on_missing_fixture-style,
   decision-014 pattern")? Every group this touches is tagged `classification_method:
   "bulk_heuristic"` in the JSON (498 of 703 groups) so a reviewer can immediately tell hand-read
   rows (97 of 703: 90 RED-signal + 6 NOT_A_CHECK overrides + 1 ready-to-build primary) from
   heuristic ones — this is the disclosed trade-off for triaging a block this size and this
   fragmented in one pass; it never claims GREEN, only distinguishes two flavors of YELLOW, so the
   downside risk of the heuristic being wrong is "a group is filed under the wrong YELLOW flavor,"
   never a false automation claim.

## READY TO BUILD candidates — verified per decision 018's discipline
Only ONE real candidate survived full verification, split across its purchase/refinance transaction
variants:

**G483 (O-RHS-55316) / G491 (O-RHS-02851) — PARTIAL, new shape, no new fixture.** `compensating_factors_documented` is a fact `extract_loan.py` **already extracts**
(`FACT_SPECS`, sourced from `usda_ratio_waiver_doc`'s "Compensating Factors Documented ... NOT IN
FILE" line) and **already correctly populated `False` for loan 05** — verified by re-running
`pdftotext -layout` on loan 05's actual PDF, not assumed. But **no existing shape cites it**:
`RatioWaiverShape` (`CHK-UND-002`, `blocks/underwriting.ttl`) only cites `piti_ratio`/
`piti_guideline`/`dti_ratio`/`dti_guideline`/`usda_ratio_waiver_in_file` — a different clause of the
USDA ratio-waiver rule than the "compensating factors were/weren't documented" clause G483/G491
actually test. G483 ("In a GUS refer or manual underwrite of a **purchase** transaction...") and
G491 ("...in a manual UW of a **refinance**...") are the same underlying fact gated on opposite
transaction types — verified the gating field, `loan_purpose_1003`, already exists before flagging
this, and explicitly named the double-firing risk a naive single-shape wiring would create.
**Needs a NEW shape** (or a purpose-branched one), not a same-shape exception-code-list edit — this
is why it's flagged PARTIAL, not "wire, don't build."

## Rejected after verification (named, per instruction — negative information)
| Candidate | Row(s) | Why it doesn't hold up |
|---|---|---|
| `AmendatoryClauseShape` (CHK-PRD-001) ← **G146** (O-VA-50789) | 3440 | The row (filed under agency O-VA even though the text says "FHA/VA Amendatory Clause") tests THREE things: unsigned, not in file, not included in the sales contract. The shape's SPARQL only checks `doc_present_fha_amendatory_clause` gated on `mismo_mortgage_type=="FHA"`. Two real gaps: (1) `EXPECTED_DOCS_BY_PROGRAM` only computes this fact for FHA loans — a VA loan never populates it at all, so wiring this code would silently never fire for VA loans regardless; (2) no signature sub-check exists. A false "ready to build" of exactly the kind decision 018 warns against — needs real extraction/shape work first. |
| `UsdaIncomeLimitShape` (CHK-PRD-002) | — | **Zero matching rows exist anywhere in the entire 5,520-row Post-Closing workbook** — verified by grepping the raw CSV directly (not just the compiled ruleset, in case discard-filtering hid one), for "USDA" + "income limit"/"adjusted household". The only USDA-income-limit-adjacent row found (`O-RHS-15685`/`O-RHS-56266`, "Streamlined-assist refi max income limit was exceeded due to **not calculating** annual income") is a process/documentation failure, not the shape's actual "adjusted income > limit" numeric comparison — a materially different condition. This shape is a genuinely orphaned pilot check with no AMQ exception code to wire to at all, not merely unwired. |
| `RatioWaiverShape` (CHK-UND-002) ← **G487** (O-RHS-50566, "ratios over 34/41") | 3418 | Textually the closest match of any row in this block to the shape's actual SPARQL logic (ratio > guideline AND no waiver in file). But this pilot's only RHS/USDA fixture (loan 05, a **purchase**) extracts a guideline of **29/41**, not this row's stated **34/41** — and the shape doesn't gate on transaction type at all. Either a different sub-scenario carries 34/41, or this row and the sibling G495 ("Refi ratios over 29/41... **high repayment ratio exception**") are the loan-05-relevant one under different AMQ terminology ("high repayment ratio exception" vs "debt ratio waiver") — an unresolved terminology question an SME needs to settle before wiring ANY specific code here. Confident-sounding on first read, does not survive the actual-number check. |
| `RatioWaiverShape` (CHK-UND-002) ← **G485** (O-RHS-55316, "eligible for a debt ratio waiver") | 3637 | States no numeric guideline at all ("ratio thresholds not met... to be **eligible** for a waiver") — cannot confirm this is the same real-world condition as RatioWaiverShape's "ratios exceed guideline, no waiver in file" test versus a distinct waiver-eligibility-ceiling test, without SME input. |

## What this means for the "unblock which block next" question (cross-link to decision 017)
Asset-verification's ceiling was gated by synthetic-fixture generation breadth (85% YELLOW, mostly
`blocked_on_missing_fixture`-style). Product-specific-check's ceiling is gated by BOTH fixture
breadth AND the sheer number of distinct agency-specific programs (near-zero dedup means each of
~500+ conditions needs its own small, separate piece of logic — there is no "build 5 shapes, cover
25 rules" leverage the way application-verification's disclosure-presence pattern had). This block
is a poor next-unblock candidate on raw ROI grounds compared to application-verification's
remaining Bucket-A fixture gaps, which at least amortize across repeated conditions.

## A discovered idiosyncrasy, distinct from the above
`GENERIC`-agency rows in this block are not uniformly "Fannie Selling Guide relevant" the way
GENERIC rows were in the prior two blocks — a real subset (`PORTAuthority`, `PORTGuides`, `PORTTCL`,
`CTPLand`, `CTPReserves`, `CTPInsure`, `PORTMedical`, `UGV Identifier`, `UGV EPIC`, ...) are
proprietary in-house lender "Portfolio"/CTP overlay-program rules with no Selling Guide grounding at
all, several of which (`G010`, `G347`, `G350`) are checks against the **lender's own internal
authorization/exception-tracking systems**, not any loan document this pilot — or any document-
extraction pilot — could ever model. The deterministic guide-topic retrieval still runs for these
(same `fnm_or_generic` convention as both prior scripts) and returns low-relevance token-overlap
matches rather than nothing (see `G010`'s packet entry) — not a bug in the retrieval, just a
reminder that a nonzero guide-candidate list doesn't mean a meaningful one for this rule family.

## What was NOT done (per instruction)
No `.ttl`, `.py` (other than the new triage script itself), `amq_compiler.py`, `extract_loan.py`,
or `run_audit.py` edit was made. README.md and JOURNAL.md were not touched (per instruction — other
agents are updating those concurrently). No candidate was wired into code; every READY_TO_BUILD
entry is flagged only, exactly like both prior blocks' triage passes.

## Cross-links
[[009]] (full-workbook compile), [[014]]/[[015]]/[[016]] (Bucket A/B/C precedents this triage's
YELLOW/READY-TO-BUILD/internal-lookup-candidate reasoning follows), [[017]] (asset-verification
triage — the dedup-ratio and fixture-breadth comparison this doc builds on), [[018]] (the
verification discipline this triage applied to every candidate before calling anything "ready to
build" — directly responsible for rejecting 3 of the 4 shape-reuse candidates considered here).
