#!/usr/bin/env python3
"""
Layer-2 triage — product-specific-check block (704 rules, 703 unique groups).

Same method as layer2_triage.py (application-verification, reference) and
layer2_triage_assets.py (asset-verification, second generation) — read those
docstrings for the GREEN/YELLOW/RED/NOT_A_CHECK definitions; unchanged here.

THREE structural differences from both prior blocks, all deliberate and all
verified empirically before assuming them (decision 018's standing lesson:
confidence language must survive a full-row-text check, not just a summary):

1. Dedup is essentially ZERO here: 704 rules -> 703 unique groups (~1.001x),
   even smaller than asset-verification's already-small 304->297 (~1.02x).
   This is the block's defining character — "Product Specific" spans FHA/VA/
   USDA/ARM/refi-program-specific rules (RefiNow, HomeReady, HomeStyle,
   CHOICERenovation, Home Possible, Refi Possible, GreenCHOICE, IRRRL, Texas
   50(a)(6), Section 502/RHS refi variants, Portfolio/CTP internal overlays,
   ...) where nearly every agency writes its own program with its own wording
   — there is almost no shared phrase pool to collapse against, unlike
   application-verification's disclosure/URLA rules.

2. UNLIKE asset-verification, `eval_class == "doc_presence"` does NOT mean
   "already correctly auto-compiled" in this block. All 8 doc_presence groups
   here were individually re-verified against amq_compiler.py's own
   DOC_KEYWORDS matching logic and found to be FALSE POSITIVES: the keyword
   regex matched a generic doc-type word ("appraisal", "title policy", the
   pre-existing "initial application" -> final_1003 bug already flagged in
   decision 014) inside a condition that actually requires a much more
   specific sub-form or sub-fact (Form 1004D, HUD-92544, a VA Loan Comparison
   Disclosure, a Subordination Agreement's junior-lien-position clause, a
   CLT/shared-equity title-policy clause) that the coarse doc-type-presence
   check cannot detect. Auto-trusting eval_class here would have repeated
   exactly the mistake decision 018 warns against, at the mechanical-
   classification layer instead of the LLM-summary layer — see the GREEN
   section below for the full per-group verification.

3. Two SHACL shapes already exist in `blocks/product_specific.ttl`
   (AmendatoryClauseShape, UsdaIncomeLimitShape) wired to ZERO AMQ exception
   codes (same "built but never connected" bug pattern decisions 017/018
   fixed for LargeDepositShape/GiftEvidenceShape). Both were checked against
   every row in this block:
     - AmendatoryClauseShape: ONE candidate row exists (G146, O-VA-50789) but
       does NOT survive verification — see the REJECTED section.
     - UsdaIncomeLimitShape: ZERO matching rows exist ANYWHERE in the entire
       5,520-row Post-Closing workbook (verified by grep across the raw CSV,
       not just the compiled ruleset) — this shape is a genuinely orphaned
       pilot check with no AMQ exception code to wire to at all.
   One NEW candidate was found instead: `compensating_factors_documented`, a
   fact extract_loan.py already extracts (from usda_ratio_waiver_doc) but
   that NO existing shape cites — see READY_TO_BUILD.

Given ~703 groups and near-zero mechanical dedup, full one-by-one hand prose
for every group (as application-verification's 54 and asset-verification's
~210 substantive groups received) is not tractable at this scale. Method used
here, disclosed for auditability:
  a. NOT_A_CHECK: identical PASS_RE convention as both prior scripts (^(Yes,|
     Not Applicable)). Verified no G291-style screening-branch override is
     needed in this block (checked every non-PASS_RE-matching short/negative-
     sounding response by hand; both candidates found — G050, G336 — are
     real defect conditions, not applicability screens).
  b. The 8 doc_presence groups: HAND-VERIFIED individually (not trusted from
     eval_class) — see point 2 above.
  c. ~90 groups flagged by a RED-signal keyword scan (reasonable/appropriate/
     acceptable/sufficient/"all requirements"/indicators-of/etc.) were EACH
     individually read in full (question + condition + exception_description)
     and hand-classified RED or YELLOW below in `C`, applying the same rule
     asset-verification's script used: a compound condition with ANY crisp,
     named, checkable component (a document, a number, a date) stays YELLOW
     even if a judgment clause is appended; only conditions that are WHOLLY
     and irreducibly an unqualified judgment call (no document, no number, no
     named comparison basis anywhere in the row) are RED.
  d. The remaining ~520 groups (crisp, program-specific presence/threshold
     conditions with no RED-signal keyword) are classified YELLOW by a
     documented, deterministic text heuristic (`classify_bulk_yellow`): does
     the condition reference a document type extract_loan.py's DOC_TYPES
     already parses (-> "Bucket-B-style: deepen an existing doc, no new
     fixture") or a document family absent from every synthetic loan (->
     "blocked_on_missing_fixture-style, decision-014 pattern: legitimate
     rule, corpus gap")? This is the same kind of mechanical derivation
     decision 017 used for asset-verification's ~87 GREEN/NOT_A_CHECK groups,
     scaled up and applied to YELLOW here because this block's own mechanical
     signal (eval_class) turned out to be unusable (see point 2) — read the
     heuristic function; it is intentionally conservative (never claims
     GREEN, only distinguishes two flavors of YELLOW) and every group it
     touches is tagged `"classification_method": "bulk_heuristic"` in the
     JSON output so a human reviewer can immediately tell hand-verified rows
     from heuristic ones and re-check the heuristic ones at whatever pace
     they choose.

Outputs:
  compiled/triage_product-specific-check.json
  out/TRIAGE-PACKET-product-specific-check.md
"""
import json
import os
import re
from collections import OrderedDict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
RULESET = os.path.join(HERE, "compiled", "ruleset.json")
SG_INDEX = os.path.join(HERE, "compiled", "selling_guide_index.json")
OUT_JSON = os.path.join(HERE, "compiled", "triage_product-specific-check.json")
OUT_MD = os.path.join(HERE, "out", "TRIAGE-PACKET-product-specific-check.md")

BLOCK = "product-specific-check"

PASS_RE = re.compile(r"^(Yes,|Not Applicable)", re.I)

# NOT_A_CHECK overrides — verified individually (same discipline as asset-
# verification's G291, application-verification's G10): a row that does NOT
# match PASS_RE's "Yes,"/"Not Applicable" wording but is still a screening/
# categorical-menu answer, not a defect condition. Found by cross-checking
# EVERY group with a blank exception_code (a strong mechanical signal — 114
# groups in this block have one; 108 of those already match PASS_RE and need
# no override) against its actual condition text:
#   G001-G005: "Was this loan originated under a specific product or program?"
#     -> the response NAMES the product (Buydown/ARM/Combination CP/...), a
#     routing/menu selector to the program-specific follow-up questions
#     elsewhere in this same block (e.g. G169 "Were all Adjustable Rate (ARM)
#     requirements met?") — not itself a pass/fail defect statement.
#   G409: response is the bare word "Yes" (no trailing comma/text) — a pass
#     answer PASS_RE's "^Yes," pattern doesn't catch because of the missing
#     comma; verified by reading the row, not assumed from the word alone.
NOT_A_CHECK_OVERRIDES = {1, 2, 3, 4, 5, 409}

# ---------------------------------------------------------------------------
# READY TO BUILD candidates (task C): flagged, NOT implemented. Every one
# individually verified against the actual AMQ row text and the actual real-
# data check it would reuse or extend (decision-018 discipline), not taken on
# a summary's word.
READY_TO_BUILD = {
    483: ("PARTIAL — new shape, no new fixture: `compensating_factors_documented` "
          "(FACT_SPECS in extract_loan.py, extracted from usda_ratio_waiver_doc's "
          "'Compensating Factors Documented ... NOT IN FILE' line) is ALREADY "
          "extracted and ALREADY correctly populated False for loan 05 — but is "
          "cited by ZERO existing SHACL shapes (RatioWaiverShape only cites "
          "piti_ratio/piti_guideline/dti_ratio/dti_guideline/usda_ratio_waiver_in_file, "
          "never this fact). G483's condition ('the eligible compensating factors "
          "supporting the use of the waiver was not supported with documentation' "
          "in a PURCHASE GUS-refer/manual-UW) matches this fact directly. Needs a "
          "NEW shape (not an extension of RatioWaiverShape, which tests a "
          "different clause), gated on loan_purpose_1003 containing 'Purchase' "
          "to avoid double-firing against G491's refinance-transaction sibling "
          "(same fact, opposite transaction-type gate) — verified the gating "
          "field (loan_purpose_1003) already exists before flagging this."),
    491: ("PARTIAL, refinance sibling of G483 — same `compensating_factors_documented` "
          "fact, gated on loan_purpose_1003 NOT containing 'Purchase' instead. Two "
          "separate shapes (or one shape with a purpose branch) needed so the two "
          "AMQ exception codes (G483 purchase / G491 refinance) don't collide on "
          "the same underlying fact."),
}

# ---------------------------------------------------------------------------
# Hand-verified classifications. Two kinds of entries:
#  (a) the 8 doc_presence eval_class groups (mechanically flagged GREEN by
#      amq_compiler.py, individually re-verified here and downgraded — see
#      module docstring point 2)
#  (b) the ~90 RED-signal-keyword groups, individually read in full and
#      classified RED or YELLOW by hand (module docstring point c)
# Fields: bin, machine, human, needs, rationale. "-" = empty (reference
# scripts' convention).
C = {
    483: ("YELLOW", "compensating_factors_documented (already extracted from "
          "usda_ratio_waiver_doc, already populated False for loan 05)", "-",
          "loan_purpose_1003 Purchase gate on a new shape (see READY_TO_BUILD)",
          "See READY_TO_BUILD — the fact this row needs is already extracted "
          "and correctly populated; only a new shape + a purpose-type gate "
          "(to avoid colliding with G491's refinance sibling) is missing."),
    # --- (a) doc_presence eval_class groups, individually re-verified false ---
    58: ("YELLOW", "-", "-",
         "a distinct '30-days-old-or-newer' recency fact on paystub (deepen extraction)",
         "amq_compiler.py's own eval_class says doc_presence (target: paystub) — but "
         "the actual condition is 'not provided OR dated over 30 days prior to "
         "application', a compound test. A bare paystub-doc-presence check would "
         "FALSE-PASS a loan with a paystub on file that is stale by more than 30 "
         "days. Downgraded from the mechanical GREEN: presence alone is not the "
         "real test."),
    59: ("YELLOW", "-", "-",
         "a W2 doc type (not in extract_loan.py's DOC_TYPES at all) + a "
         "'covers the most recent one-year period' recency fact",
         "Same false-positive pattern as G058: eval_class=doc_presence targets "
         "paystub, but the condition requires BOTH a paystub AND a W2 covering a "
         "specific period — the mechanical check only verifies the paystub half, "
         "and W2 isn't even a document type this pilot extracts."),
    210: ("YELLOW", "-", "-",
          "a specific CLT/shared-equity clause WITHIN the title policy (deepen "
          "title_commitment extraction, not mere presence)",
          "eval_class=doc_presence targets title_commitment, but the condition is "
          "'title policy/endorsement MISSING SPECIFIC REQUIREMENTS for community "
          "land trust/shared equity' — content-level, not presence-level. Any "
          "loan with an ordinary title commitment (every loan in this corpus) "
          "would false-PASS a check that only verifies the doc type exists."),
    327: ("YELLOW", "-", "-",
          "a distinct 'satisfactory completion inspection' document — NOT the "
          "appraisal itself",
          "eval_class=doc_presence targets 'appraisal' only because the condition "
          "text happens to contain the word 'appraisal' ('The appraisal was made "
          "subject to completion... an inspection certifying the repairs have "
          "been satisfactorily completed was not in the file') — the actual "
          "missing document is the completion INSPECTION, a distinct doc family "
          "absent from every synthetic loan. Presence of an ordinary appraisal "
          "(which every loan has) would false-PASS this."),
    415: ("YELLOW", "-", "-",
          "Form 1004D (Appraisal Update/Completion Report) as its own field/doc-"
          "subtype — not the base appraisal doc",
          "Same generic-'appraisal'-keyword false-positive as G327: the condition "
          "needs a completed Form 1004D specifically, a sub-document type this "
          "pilot doesn't distinguish from a plain appraisal."),
    418: ("YELLOW", "-", "-",
          "a VA Loan Comparison Disclosure doc type — NOT the final 1003",
          "eval_class=doc_presence targets final_1003 because amq_compiler.py's "
          "DOC_KEYWORDS maps the phrase 'initial application' to final_1003 as a "
          "same-file shortcut — this is the EXACT latent bug decision 014 already "
          "flagged (application-verification groups 35/39/40) recurring here. The "
          "condition needs a VA cash-out-refi-specific Loan Comparison Disclosure, "
          "a document this pilot doesn't have at all; every loan already has a "
          "final 1003, so this would false-PASS on every VA cash-out loan."),
    461: ("YELLOW", "-", "-",
          "a components-to-be-completed list attached to the appraisal for 90%+-"
          "complete new construction — not modeled as a distinct fact",
          "Same generic-'appraisal'-keyword false positive as G327/G415 — the "
          "condition is specific to 90%-or-more-complete new construction, a "
          "gating fact this pilot doesn't track, and the missing list is not the "
          "appraisal document itself."),
    524: ("YELLOW", "-", "-",
          "a Subordination Agreement doc type + a junior-lien-position clause "
          "within the title policy",
          "eval_class=doc_presence targets title_commitment (matched on 'title "
          "policy'), but the condition is compound: EITHER no Subordination "
          "Agreement OR the title policy doesn't reflect junior-lien position. "
          "Mere presence of an ordinary title commitment (ungated on the second-"
          "mortgage-position clause) would false-PASS this."),
    # --- G146: AmendatoryClauseShape candidate, verified NOT ready to build ---
    146: ("YELLOW", "presence half: doc_present_fha_amendatory_clause (already "
          "extracted, FHA only)", "signature status + 'included in sales contract' "
          "location test",
          "shape needs widening to VA loans (fact is only computed when "
          "mismo_mortgage_type=='FHA' today; a VA loan never populates it) + a "
          "signature sub-check",
          "CONSIDERED for AmendatoryClauseShape (CHK-PRD-001), REJECTED as-is: "
          "this row (O-VA-50789, filed under agency O-VA even though the text "
          "says 'FHA/VA Amendatory Clause') tests THREE things — unsigned, not "
          "in file, not in the sales contract — while the shape's SPARQL only "
          "checks doc_present_fha_amendatory_clause AND mismo_mortgage_type=='FHA'. "
          "Two real gaps, not merely imprecision: (1) EXPECTED_DOCS_BY_PROGRAM only "
          "computes this fact for FHA loans — a VA loan never gets the fact at "
          "all, so the shape would silently never fire for VA loans regardless of "
          "wiring; (2) the shape has no signature test. Wiring this code today "
          "would be a false 'ready to build' of exactly the kind decision 018 "
          "warns against — needs real shape/extraction work first, not just an "
          "amq_exception_codes list edit."),
    # --- (c) RED-signal-keyword groups, hand-read and classified ---
    10: ("RED", "-", "'did not have sufficient authority' — an internal lender "
         "underwriting-authorization-level judgment", "-",
         "No document, number, or named comparison basis anywhere in the row — "
         "an internal lender authority-matrix determination, not something any "
         "loan document states. Also out of this pilot's document-extraction "
         "scope entirely (an internal process fact, not borrower/loan data)."),
    11: ("YELLOW", "asset-dissipation income-calculator re-derivation (asset "
         "total / dissipation term)", "-",
         "asset-dissipation calculator fields (total assets, dissipation period) "
         "— not in FIELD_SPECS today",
         "'Accurately' names a specific, re-computable formula (an asset-"
         "dissipation calculator), not an open-ended judgment — crisp math once "
         "the input fields exist."),
    17: ("RED", "-", "bare, non-exhaustive Portfolio overlay list ('ex: 2 years "
         "W2s, 2 mos bank statements, add'l reserves, etc' — 'etc' is explicit)",
         "-", "The row itself says 'examples' and 'etc' — it does not enumerate "
              "a closed, checkable rule set. Needs SME decomposition of the full "
              "Portfolio overlay checklist before any single fact is checkable."),
    18: ("RED", "-", "'TCL (Total Credit Limit) guidelines were not met' — no "
         "threshold number stated anywhere in the row", "-",
         "Bare reference to an internal Portfolio policy limit with no number "
         "given — same pattern as the bare 'all requirements' catch-alls found "
         "in the asset-verification triage (decision 017's G018/G023/G196)."),
    29: ("YELLOW", "6-month acquisition-to-application date comparison + funds-"
         "sourcing doc presence", "-",
         "land/property acquisition date field + funds-sourcing documentation "
         "(not in corpus)",
         "Has a genuine crisp threshold (6 months) and a named doc requirement "
         "(closing disclosure from the acquisition); 'adequately sourced' is "
         "flavor text around an otherwise crisp date/doc test."),
    33: ("YELLOW", "contingency-reserves-vs-PITI-reserves math", "-",
         "CTP contingency-reserve requirement threshold (an SME-supplied constant, "
         "not stated in this row) + reserves fields",
         "Has a real comparison basis (PITI reserves) even though the specific "
         "required contingency percentage isn't stated in-row — crisp once an "
         "SME supplies the threshold and reserves fields exist."),
    36: ("YELLOW", "builder's-risk-coverage-endorsement presence", "-",
         "a named insurance endorsement/rider doc (not in corpus)",
         "Comparison basis is a specific, named coverage type (builder's risk) — "
         "crisp presence check once the document exists; 'appropriate' is "
         "describing the pass/fail outcome, not the test itself."),
    39: ("YELLOW", "professional-license status/duration evidence", "'does not "
         "fall within the guidelines of the medical professional program' "
         "(unstated criteria)",
         "medical-professional license verification doc (not in corpus)",
         "Compound: the license-evidence half names a real, checkable document; "
         "the 'guidelines' half states no specific criteria and stays human — "
         "kept YELLOW per the crisp-half-survives convention (asset-verification "
         "G007's pattern)."),
    100: ("RED", "-", "'without all requirements being met' — zero specific "
          "requirements named in this row for the student-loan cash-out feature",
          "-", "Bare catch-all; FNMA's actual student-loan-cash-out-refi rule set "
               "is not enumerated anywhere in this row — needs SME decomposition."),
    106: ("YELLOW", "equity-buyout supporting-document presence", "-",
          "a legally-enforceable-agreement doc type for an ex-spouse/co-owner "
          "equity buyout (not in corpus)",
          "'Adequate documentation' names a real, specific document family (the "
          "buyout agreement) even though it isn't in the corpus today."),
    109: ("YELLOW", "LTV > 95% gate (LTV already derivable from appraisal/1003 "
          "fields)", "the specific bundle of 'additional requirements' beyond "
          "the LTV gate (unstated in-row)",
          "LCO-refi-over-95%-LTV requirement checklist (an SME-defined list)",
          "Has an explicit numeric threshold (95% LTV) as a bright-line gate; "
          "what else is specifically required beyond that isn't named in-row."),
    113: ("YELLOW", "cash-back-to-borrower vs 2%-of-loan-amount-or-$2,000 "
          "threshold", "-",
          "an LCO-refi cash-back-to-borrower field (distinct from the refi-"
          "specific cash_out_to_borrower_1003, which is populated only for "
          "actual cash-out refis, not LCO)",
          "Fully crisp numeric threshold with an explicit comparison basis — "
          "'unacceptable' is just naming the outcome, not the test."),
    114: ("RED", "-", "'obtained for an unacceptable use' — no specific banned "
          "uses named in this row", "-",
          "Bare catch-all; FNMA's actual allowable-use list for LCO refis is not "
          "stated here — needs SME decomposition before any fact is checkable."),
    117: ("YELLOW", "borrower-carryover check: at least 1 original-loan borrower "
          "remains on the new mortgage (needs old-loan borrower data)",
          "'acceptable credit history and ability to repay' (unstated criteria)",
          "prior-loan borrower-identity data (not currently modeled — this pilot "
          "extracts only the CURRENT loan's borrowers)",
          "Compound: the borrower-carryover half names a specific, checkable "
          "fact; the credit-history-acceptability half is open-ended and stays "
          "human."),
    118: ("YELLOW", "equity-buyout supporting-document presence (FHA variant)", "-",
          "a legally-enforceable equity agreement doc (not in corpus)",
          "Same family as G106 — FHA no-cash-out variant."),
    132: ("RED", "-", "'not all Non-Arm's Length requirements were met' — zero "
          "specific requirements named", "-",
          "Bare catch-all; FNMA's non-arm's-length checklist isn't enumerated "
          "in this row — needs SME decomposition."),
    133: ("YELLOW", "seller-tax-credit vs escrow-account-offset-exception math", "-",
          "real-estate-tax-credit amount + escrow-account-requirement fields "
          "(not in corpus)",
          "Names a specific, structured exception test (tax credit vs escrow "
          "shortage) — crisp once fields exist, not an open-ended judgment."),
    134: ("YELLOW", "minimum-borrower-contribution threshold + fund-source "
          "acceptability", "-",
          "minimum-contribution + fund-source fields (deepen 1003/closing_"
          "disclosure) — same family as asset-verification's G099",
          "Comparison basis (a minimum-contribution percentage the mortgage "
          "type defines) is real and crisp; source-acceptability is a bounded, "
          "enumerable list, not free-form judgment."),
    136: ("YELLOW", "purchase-agreement clause detection (personal property/"
          "repairs bundled into price)", "-",
          "a purchase agreement/contract doc type — NOT in this pilot's corpus "
          "at all (same systemic gap flagged in decision 017's asset triage: no "
          "purchase contract exists in any of loan 01-05)",
          "Crisp content check once the document exists; blocked entirely on "
          "the missing purchase-contract document family."),
    142: ("YELLOW", "3 explicit sub-tests: land-contract execution date within "
          "12 months, loan proceeds fully applied to the contract payoff, no "
          "cash disbursed to borrower", "-",
          "a land-contract-for-deed document type (not in corpus)",
          "All three conjuncts are crisp, named, checkable facts once the "
          "document exists — no judgment language in the actual test."),
    145: ("YELLOW", "final-sales-contract-and-addendums presence (same missing-"
          "purchase-contract gap as G136)", "'is incorrect or unacceptable' "
          "(unstated criteria)",
          "purchase/sales contract doc type (not in corpus)",
          "Presence half is crisp and shares the systemic purchase-contract gap "
          "with G136/G486; the 'incorrect or unacceptable' residual stays "
          "human."),
    156: ("YELLOW", "payment-advance-then-refinance sequence detection", "-",
          "servicer payment-advance records + refinance timing (not in corpus)",
          "Names a specific, checkable event sequence (advances, then refi) "
          "even though establishing 'agreed payments were advanced' as a defect "
          "still leans evidentiary."),
    157: ("RED", "-", "'indicators in the file that the subject refinance is a "
          "prearranged refinancing agreement' — a fraud-pattern judgment call "
          "with no defined bright-line test", "-",
          "'Indicators' is inherently evidentiary/subjective — same class as "
          "G158/G159/G701."),
    158: ("RED", "-", "'indicators that the refinance was the result of a "
          "conditional tender of payment procedure' — fraud-pattern judgment",
          "-", "Same class as G157/G159/G701 — no stated bright-line test."),
    159: ("RED", "-", "'indicators the lender specifically targeted the Fannie "
          "Mae borrower to offer a refinance' — fraud-pattern judgment", "-",
          "Same class as G157/G158/G701 — no stated bright-line test."),
    162: ("YELLOW", "ARM-type-to-qualifying-rate rule lookup", "-",
          "ARM sub-type + note rate/margin fields (mismo_note_rate already "
          "extracted; the specific qualifying-rate-per-ARM-type rule table is "
          "not)", "Comparison basis (a defined correct-rate-per-ARM-type rule) "
          "is real and crisp, same family as G194/G195/G164/G196."),
    164: ("YELLOW", "short-term-ARM qualifying-rate recompute (FRD variant)", "-",
          "the required ATR-covered-ARM qualifying-rate method (an SME-"
          "supplied formula) + ARM-type/note-rate fields",
          "Same family as G196 (FNM variant) and G194/G195 (explicit-formula "
          "variants) — 'required method' names a real, defined calculation."),
    183: ("YELLOW", "ARM-Plan-index membership test against FNMA's approved-"
          "index list", "-",
          "ARM index name field + an FNMA-approved-index reference list (an "
          "SME-maintained list, not a document-extraction gap)",
          "'Unacceptable to FNMA' has a real comparison basis — a specific, "
          "enumerable list of approved indices — not open-ended judgment."),
    185: ("YELLOW", "initial-note-rate-vs-fully-indexed-rate > 3% threshold", "-",
          "note rate (mismo_note_rate extracted) + index/margin fields for the "
          "fully-indexed-rate computation",
          "Fully crisp numeric threshold (3%) with a stated comparison basis — "
          "'unacceptable' just names the outcome."),
    194: ("YELLOW", "qualifying rate == Note rate + 5% for a 1-year 1%-annual-"
          "cap ATR ARM", "-",
          "'qualifying rate used' as its own field (mismo_note_rate exists; "
          "the rate UNDERWRITING actually qualified against, and the ARM's "
          "annual-cap sub-type, are not yet distinct fields)",
          "The row states the exact formula inline ('Note rate plus 5%') — this "
          "is as close to GREEN as this block gets; only the qualifying-rate "
          "and cap-type fields are missing, not the underlying math."),
    195: ("YELLOW", "qualifying rate == Note rate + 6% for a 1-year 2%-annual-"
          "cap ATR ARM", "-", "same fields as G194",
          "Same family as G194 — the exact formula is stated in-row."),
    196: ("YELLOW", "short-term-ARM qualifying-rate recompute (FNM variant)", "-",
          "same as G164", "Same family as G164 (FRD variant) — 'required "
          "method' names a real, defined calculation."),
    201: ("YELLOW", "Community-Second source-party membership test", "'all "
          "requirements not met' (unstated residual)",
          "second-mortgage source-party field + an allowable-party reference "
          "list (not in corpus)",
          "'Allowable party' is a real, bounded, enumerable list (nonprofit/"
          "government/employer-type sources), same family as G210's CLT check; "
          "the appended 'all requirements' clause stays human."),
    217: ("YELLOW", "energy-efficiency-improvement cost documentation presence", "-",
          "an energy-improvement cost estimate/documentation type (not in corpus)",
          "'Properly documented' names a real, specific documentation "
          "requirement, not an open-ended judgment."),
    218: ("YELLOW", "nonresidential (farm) value exclusion from loan amount", "-",
          "a farm-value/nonresidential-value breakdown field on the appraisal "
          "(appraisal doc exists; this specific breakdown field does not)",
          "Crisp dollar-value exclusion test once the appraisal breakdown field "
          "exists — not a subjective call."),
    222: ("YELLOW", "Form HUD-9548 + addenda presence", "'did not meet all "
          "requirements' (unstated residual)",
          "HUD-9548 (Sales Contract Property Disposition Program) doc type "
          "(not in corpus)",
          "Presence half is crisp; the appended catch-all clause stays human — "
          "same pattern as G145."),
    235: ("YELLOW", "explicit 95.01-97% LTV/CLTV/HCLTV band gate", "the specific "
          "bundle of 'requirements' beyond the LTV band (unstated in-row)",
          "HomeReady 95.01-97% LTV-band requirement checklist (an SME-defined "
          "list)", "Same pattern as G109 — a genuine numeric band as the gate, "
          "the full requirement list unstated."),
    257: ("RED", "-", "'without all requirements being met' for the HomeStyle "
          "'Do It Yourself' option — zero specific requirements named", "-",
          "Bare catch-all; needs SME decomposition of the DIY-option checklist."),
    264: ("YELLOW", "IRRRL-borrower-vs-original-loan-borrower match (needs prior-"
          "loan borrower data)", "'acceptable life event' (unstated criteria)",
          "prior-loan borrower-identity data (not currently modeled)",
          "Compound: the borrower-match half is a crisp fact once prior-loan "
          "data exists; the 'acceptable life event' half is a bounded-but-"
          "unstated-here judgment, same donor/source-acceptability pattern seen "
          "throughout asset-verification."),
    285: ("YELLOW", "discount-points-added-to-principal trigger detection", "'all "
          "requirements being met' (unstated residual)",
          "a discount-points-in-IRRRL field (deepen closing_disclosure/1003)",
          "The trigger fact (discount points added) is crisp and named; the "
          "appended 'all requirements' clause stays human."),
    295: ("YELLOW", "prior-VA-approval-record presence for a joint entitlement "
          "loan", "-",
          "a joint-loan VA prior-approval doc type (not in corpus)",
          "Crisp approval-record presence check, not a subjective call."),
    304: ("YELLOW", "3 named compliance dimensions: property type, amortization "
          "type (mismo_amortization_type already extracted), loan purpose "
          "(loan_purpose_1003/loan_purpose_cd already extracted)", "-",
          "a resale-restriction-program eligibility rule table (SME-defined) + "
          "a property-type field (not currently modeled)",
          "2 of the 3 named fields already exist in the extraction contract — "
          "a genuine near-term candidate once the resale-restriction program "
          "rules and property-type field are added; not claimed ready-to-build "
          "here because the actual per-restriction-type rule table isn't "
          "sourced anywhere in this row."),
    323: ("YELLOW", "draw-payment-approval-record presence", "-",
          "a construction-draw borrower-approval log (not in corpus)",
          "Crisp doc-presence test, not a subjective call — 'not evident' names "
          "a specific missing record."),
    324: ("RED", "-", "BOTH conjuncts are judgment calls: 'escrow holdback "
          "amount was not appropriate' (no formula stated) AND 'dwelling not "
          "suitable for immediate occupancy' (an inspector's judgment)", "-",
          "Unlike most compound rows here, NEITHER half of this one names a "
          "crisp fact or number — kept RED rather than defaulting to the "
          "crisp-half-survives convention."),
    329: ("YELLOW", "CABO Model Energy Code (MEC) exhibit presence", "-",
          "a named specific compliance document (1992 CABO MEC exhibit, not in "
          "corpus)", "Crisp, specific-document presence check."),
    347: ("RED", "-", "an internal lender exception-tracking-system completeness "
          "check ('not clearly identified/listed in the Portfolio exception "
          "screen') — not a loan-document fact at all", "-",
          "Same out-of-scope-entirely class as G010/G350: this is about the "
          "LENDER's own internal system, not any document this pilot models."),
    350: ("RED", "-", "same internal lender-system class as G347 ('not properly "
          "reflected in EPIC')", "-", "Same as G347 — out of document-extraction "
          "scope entirely."),
    363: ("YELLOW", "HomeStyle-loan-agreement-execution-date == note-date match", "-",
          "a HomeStyle loan agreement doc + execution date field (not in "
          "corpus)", "Crisp date-match test once the document exists."),
    366: ("YELLOW", "renovation-contract dual-signature + pre-closing-date check", "-",
          "a renovation contract doc type (not in corpus)",
          "Crisp signature/date test, not a subjective call."),
    385: ("YELLOW", "construction-cost-documentation-bundle presence (named "
          "families: purchase contract, Construction Loan Agreement, plans, "
          "receipts, invoices, lien waivers)", "-",
          "the named construction-cost document family (none in corpus)",
          "Row says 'for example' but DOES name concrete document families, "
          "unlike the truly bare catch-alls classified RED elsewhere in this "
          "block — crisp presence-bundle check once documents exist."),
    386: ("YELLOW", "guarantee-fee-collection-date vs guarantee-request-date "
          "order check", "-",
          "USDA guarantee-fee collection-date fields (not in corpus — loan 05 "
          "doesn't carry this specific fact)",
          "Crisp date-order test, not a subjective call."),
    413: ("YELLOW", "Form 1004D decline-status + re-qualification-appraisal "
          "presence", "-",
          "Form 1004D fields (not in corpus — same family as G415)",
          "Crisp doc-content + presence test."),
    416: ("YELLOW", "cash-out-refi loan-amount vs 100%-of-reasonable-value + $6k "
          "energy-improvement allowance", "-",
          "VA 'reasonable value' (the NOV's appraised-value amount) as its own "
          "field — va_nov doc exists in the corpus (loan 03) and nov_issue_date "
          "is already extracted, but the value amount itself is not yet a field "
          "— same VA-reasonable-value gap flagged in the asset-verification "
          "triage's G009/G010/G016",
          "'Reasonable value' is VA's defined term of art (the NOV amount), not "
          "a subjective judgment — crisp % math once the field exists."),
    420: ("YELLOW", "LTV vs 90%-of-reasonable-value + discount-point-count gate "
          "(Type I fixed-to-ARM refi)", "-",
          "same VA reasonable-value field gap as G416",
          "Same family as G416 — a second variant of the same crisp, "
          "term-of-art comparison."),
    435: ("YELLOW", "executed-construction-contract presence", "-",
          "a construction contract doc type (not in corpus — same family as "
          "G385)", "'Acceptable' here means 'executed/signed' — crisp presence "
              "test, not a subjective quality call."),
    441: ("YELLOW", "construction-escrow-closure + principal-curtailment-"
          "application check", "-",
          "construction-escrow-closure fields (not in corpus)",
          "Crisp doc/field test, not a subjective call."),
    446: ("YELLOW", "unpaid-contractor / lien-risk documentation presence", "-",
          "a lien-waiver/payment-completion doc type (not in corpus)",
          "'Could result in a lien' names a specific, checkable documentation "
          "gap (unpaid work), not itself a prediction the machine has to make — "
          "the file either has lien-waiver/payment evidence or it doesn't."),
    451: ("YELLOW", "high-balance-mortgage variance-approval presence", "'all "
          "requirements not met' (unstated residual)",
          "a high-balance-mortgage variance-approval doc type (not in corpus)",
          "Variance-doc-presence half is crisp; the catch-all clause stays "
          "human — same pattern as G145/G222."),
    454: ("YELLOW", "owner-builder-paid-options source-documentation + "
          "itemization presence", "-",
          "an owner-builder cost-itemization doc type (not in corpus)",
          "'Acceptable source' + itemization are named, specific documentation "
          "requirements, not open-ended judgment."),
    469: ("YELLOW", "HUD-92051 (or state-sanctioned equivalent) inspection-form "
          "presence", "-",
          "HUD-92051/Compliance Inspection Report doc type (not in corpus — "
          "same new-construction-inspection family as G327/G442)",
          "Crisp, specific-form presence check."),
    485: ("YELLOW", "PITI/DTI ratio vs guideline comparison (piti_ratio/"
          "piti_guideline/dti_ratio/dti_guideline already extracted from "
          "usda_ratio_waiver_doc)", "-",
          "a purchase-vs-refi transaction-type gate on RatioWaiverShape (CHK-"
          "UND-002, currently ungated on transaction type) + confirmation this "
          "row's 'eligible for a waiver' test is the same as RatioWaiverShape's "
          "'ratios exceed guideline' test, not a distinct waiver-eligibility-"
          "ceiling test",
          "CONSIDERED for RatioWaiverShape, NOT wired: this row's exact "
          "guideline pair (never stated numerically here) can't be confirmed "
          "against RatioWaiverShape's generic ratio>guideline test without an "
          "SME confirming 'ratio thresholds not met to be ELIGIBLE for a "
          "waiver' is the same real-world condition as 'ratios exceed the "
          "guideline and no waiver is on file' rather than a distinct maximum-"
          "ratio-ceiling-for-waiver-eligibility test. See G487 for the closer, "
          "still-rejected candidate and the decision doc's REJECTED section."),
    487: ("YELLOW", "PITI/DTI ratio vs guideline comparison + waiver-in-file "
          "check (RatioWaiverShape's exact logic, on paper)", "-",
          "confirmation this row's stated '34/41' pair is what "
          "usda_ratio_waiver_doc's extracted guideline actually contains for "
          "the loans this row targets — loan 05 (this pilot's only RHS fixture) "
          "extracts 29/41, not 34/41",
          "CONSIDERED and REJECTED as ready-to-build: textually the CLOSEST "
          "match to RatioWaiverShape (CHK-UND-002) of any row in this block — "
          "'approved debt ratio waiver is not in the file... with ratios over "
          "34/41' maps almost exactly onto piti_ratio>piti_guideline AND "
          "dti_ratio>dti_guideline AND usda_ratio_waiver_in_file==false. But "
          "the pilot's only RHS/USDA fixture (loan 05) is a PURCHASE with an "
          "extracted guideline of 29/41, not this row's stated 34/41 — meaning "
          "either a different transaction sub-type carries the 34/41 pair (RatioWaiverShape "
          "doesn't gate on transaction type at all today) or this row and G495 "
          "('Refi ratios over 29/41... high repayment ratio exception') are "
          "actually the loan-05-relevant one under DIFFERENT AMQ terminology "
          "('high repayment ratio exception' vs 'debt ratio waiver') — an "
          "unresolved terminology question an SME needs to settle before "
          "wiring ANY specific code here, exactly the kind of confident-"
          "sounding-but-unverified match decision 018 warns against."),
    491: ("YELLOW", "compensating_factors_documented (already extracted, refi "
         "transaction-type variant of G483)", "-",
         "loan_purpose_1003 NOT-Purchase gate on a new shape (see READY_TO_BUILD)",
         "See READY_TO_BUILD — refinance sibling of G483, same fact, opposite "
         "purpose gate."),
    526: ("YELLOW", "contractor licensing/insurance-verification presence", "-",
          "a contractor-licensing-verification doc type (not in corpus)",
          "Crisp doc-presence test."),
    528: ("YELLOW", "renovation-contract execution date vs 180/365-day "
          "threshold", "-",
          "a CHOICERenovation contract doc type + date field (not in corpus)",
          "Explicit numeric day-thresholds are stated in-row ('not to exceed "
          "180 days or 365 days') despite the 'reasonable time' phrase — crisp "
          "math once the document exists."),
    529: ("YELLOW", "contractor-approval-process documentation presence", "-",
          "a contractor-approval-process doc/attestation (not in corpus)",
          "Crisp presence test, not a subjective call."),
    537: ("YELLOW", "occupancy-within-60-days-of-disbursement date check", "-",
          "occupancy-certification + disbursement-date fields (not in corpus)",
          "Explicit numeric threshold (60 days) stated in-row."),
    574: ("YELLOW", "GreenCHOICE-proceeds-paid-existing-efficiency-debt trigger "
          "detection", "'all requirements not met' (unstated residual)",
          "a GreenCHOICE-proceeds-use field (deepen closing_disclosure)",
          "Trigger fact is named and crisp; catch-all residual stays human."),
    588: ("YELLOW", "sweat-equity appraiser-certification presence", "-",
          "an appraiser sweat-equity-certification field (appraisal doc exists; "
          "this specific field does not) — same family as asset-verification's "
          "G219/G278", "Crisp attestation-presence test."),
    589: ("YELLOW", "residual-income-for-savings sign test (positive/negative "
          "number)", "'cash on hand appears borrowed' (evidentiary judgment)",
          "a residual-income-for-savings computation field (not in corpus)",
          "Compound: the residual-income-sign half is crisp math; the "
          "'appears borrowed' half is evidentiary and stays human — kept "
          "YELLOW per the crisp-half-survives convention."),
    590: ("YELLOW", "unsecured-loan-as-funds-source detection (cross-referenced "
          "against tradelines/urla_liabilities entities ALREADY extracted)", "'all "
          "conditions being met' + 'monthly payment... where applicable' "
          "(partially unstated)",
          "an unsecured-loan-type flag on tradelines/urla_liabilities (both "
          "entities already extracted; the loan-type-is-unsecured "
          "classification is not)",
          "Worth a second look before ruling out entirely: BOTH entity types "
          "this needs already exist for every loan (same 'reuse existing "
          "entities' pattern as asset-verification's G011 VA-secured-loan "
          "candidate) — not claimed ready-to-build here because the 'all "
          "conditions'/monthly-payment-inclusion residual isn't fully named "
          "in-row."),
    596: ("YELLOW", "12-month rental-history-duration threshold", "'will "
          "continue to reside together for the foreseeable future' (unstated "
          "criteria)",
          "rental-history-duration + lease/continuance documentation (not in "
          "corpus)",
          "Explicit numeric threshold (12 months) stated in-row; the "
          "continuance-affirmation half is softer but still names a specific "
          "certification, not open-ended judgment — kept YELLOW."),
    598: ("YELLOW", "other-real-estate-owned/property-ownership fact", "-",
          "a financed/owned-properties schedule entity (not modeled — same "
          "systemic gap flagged in asset-verification's G240/G241)",
          "'Ownership interest in other residential property' is a crisp, "
          "named fact once an REO/owned-property schedule entity exists."),
    611: ("RED", "-", "'sufficient'/'acceptable'/'free of derogatory credit' "
          "credit-history-adequacy judgment — no quantified threshold anywhere "
          "in the row", "-",
          "Unlike most 'sufficient'/'acceptable' rows in this block, this one "
          "names NO comparison basis at all (no score, no ratio, no specific "
          "document) — a genuine open-ended credit-quality judgment call."),
    632: ("YELLOW", "principal-curtailment line-item presence on the Closing "
          "Disclosure", "-",
          "a principal-curtailment field on closing_disclosure (doc exists; "
          "field does not)", "Crisp field-presence test, not a subjective call."),
    633: ("YELLOW", "$500 cash-to-close threshold + funds-documentation "
          "presence", "-",
          "cash-to-close + funds-documentation fields (not in corpus)",
          "Explicit numeric threshold ($500) stated in-row."),
    664: ("YELLOW", "620 minimum-credit-score threshold", "-",
          "a credit-score field on credit_report (the doc type exists generically "
          "but is absent from loan 05, this pilot's only RHS loan — needs BOTH "
          "a new field AND a new RHS-specific fixture)",
          "Explicit numeric threshold (620) stated in-row — as crisp as this "
          "block gets; blocked purely on missing fixture/field, not on any "
          "ambiguity in the rule."),
    666: ("YELLOW", "RHS-waiver-approval-letter presence", "'did not comply "
          "with all of the requirements' (unstated residual)",
          "an RHS modification/waiver-approval doc type (not in corpus)",
          "Waiver-approval-doc-presence half is crisp; the broad opening "
          "clause stays human."),
    673: ("RED", "-", "bare reference to Texas Constitution Article XVI Section "
          "50(a)(6) with zero in-row specifics", "-",
          "Needs SME decomposition of the actual TX 50(a)(6) requirement "
          "checklist — this row states no checkable fact on its own."),
    675: ("RED", "-", "same bare TX 50(a)(6) reference as G673 (FNM variant)",
          "-", "Same as G673."),
    701: ("RED", "-", "'appears to have been obtained with unacceptable "
          "refinance practices' — a fraud-pattern judgment with 'appears' and "
          "'indications' as its only stated test", "-",
          "Same evidentiary-judgment class as G157/G158/G159 — no bright-line "
          "test stated."),
}

# ---------------------------------------------------------------------------
# Bulk YELLOW heuristic for the ~520 remaining substantive groups (module
# docstring point d). Deliberately conservative: never emits GREEN or RED,
# only names which flavor of YELLOW (existing-doc-deepen vs missing-fixture)
# applies, grounded in a real keyword match against extract_loan.py's own
# DOC_TYPES list. Every group this touches is tagged in the JSON output so a
# human reviewer knows it wasn't individually hand-read like the groups in
# `C` above.
EXISTING_DOC_HINTS = [
    (r"final .{0,15}(application|1003|urla)|\b1003\b|\bURLA\b", "final_1003"),
    (r"verification of employment|\bVOE\b", "voe"),
    (r"pay ?stub", "paystub"),
    (r"credit report", "credit_report"),
    (r"bank statement", "bank_statement"),
    (r"title (commitment|policy|binder)", "title_commitment"),
    (r"closing disclosure|\bCD\b", "closing_disclosure"),
    (r"HUD-?92900", "hud_92900a"),
    (r"FHA Connection|case number assignment", "fhac_case_assignment"),
    (r"gift letter", "gift_letter"),
    (r"CAIVRS", "caivrs"),
    (r"certificate of eligibility|\bCOE\b", "va_coe"),
    (r"notice of value|\bNOV\b|reasonable value", "va_nov"),
    (r"payoff", "payoff_statement"),
    (r"mortgage payment history|\bVOM\b|pay history", "vom"),
    (r"self-employ", "se_income_index"),
    (r"GUS [Ff]indings|GUS refer", "gus_findings"),
    (r"property eligibility", "usda_property_elig"),
    (r"debt ratio|ratio waiver", "usda_ratio_waiver_doc"),
    (r"\bappraisal\b", "appraisal"),
]

CRISP_SIGNAL_RE = re.compile(
    r"(\d+(\.\d+)?\s*%|\$[\d,]+|\b\d+[\s-]*(day|month|year)s?\b|\b\d{2,3}/\d{2,3}\b)",
    re.I)


def detect_doc_hint(text):
    for rx, doc_type in EXISTING_DOC_HINTS:
        if re.search(rx, text, re.I):
            return doc_type
    return None


def classify_bulk_yellow(g):
    text = g["condition"] + " " + g["exc_desc"]
    doc_type = detect_doc_hint(text)
    crisp = CRISP_SIGNAL_RE.search(text)
    machine = ("explicit numeric/date threshold detected: '%s'" % crisp.group(0)
               if crisp else "-")
    if doc_type:
        needs = ("a field/fact on the existing '%s' doc type not yet in "
                 "FIELD_SPECS/FACT_SPECS" % doc_type)
        rationale = ("Bucket-B-style (decision 015 pattern): condition references "
                     "'%s', a document type extract_loan.py already parses for at "
                     "least one synthetic loan — likely a new-field addition, not "
                     "a new fixture. NOT hand-verified individually; classified by "
                     "the bulk keyword heuristic (see module docstring point d) — "
                     "read the condition text before building." % doc_type)
    else:
        needs = "a document/data type not in extract_loan.py's DOC_TYPES at all"
        rationale = ("Bucket-A-style (decision 014 pattern): no keyword in this "
                     "condition matches any document type extract_loan.py already "
                     "parses — likely needs a genuinely new synthetic fixture, not "
                     "just a new field. NOT hand-verified individually; classified "
                     "by the bulk keyword heuristic (see module docstring point d) "
                     "— read the condition text before building.")
    return "YELLOW", machine, "-", needs, rationale, bool(doc_type)


STOP = set("were all the of and or a an is in to for was not on by with as at have "
           "been requirements met all any".split())


def tokens(text):
    return {w for w in re.findall(r"[a-z]{3,}", text.lower())} - STOP


def retrieve_topics(sg, rule_text, k=3):
    rt = tokens(rule_text)
    scored = []
    for t in sg["topics"]:
        overlap = len(rt & tokens(t["title"]))
        if overlap:
            scored.append((overlap, t["code"], t["title"], t["pdf_page"]))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [{"code": c, "title": ti, "pdf_page": p, "score": s}
            for s, c, ti, p in scored[:k]]


def main():
    with open(RULESET) as f:
        ruleset = json.load(f)
    rules = [r for r in ruleset["rules"] if r["block"] == BLOCK]
    source_csv = ruleset["source_csv"]
    with open(SG_INDEX) as f:
        sg = json.load(f)

    groups = OrderedDict()
    for r in sorted(rules, key=lambda x: (x["question_text"], x["response_text"])):
        groups.setdefault((r["question_text"], r["response_text"]), []).append(r)

    if len(groups) != 703:
        raise SystemExit("Expected 703 unique groups for a fresh compile of %d "
                         "rules; got %d. Ruleset changed — re-review before "
                         "trusting this triage." % (len(rules), len(groups)))

    out_groups, group_counter, rule_counter = [], Counter(), Counter()
    method_counter = Counter()
    for gid, ((q, resp), members) in enumerate(groups.items(), 1):
        agencies = sorted({m["agency"] for m in members})
        codes = sorted({m["exception_code"] for m in members})
        exc_desc = members[0].get("exception_description", "")
        g_partial = {"gid": gid, "question": q, "condition": resp,
                     "exc_desc": exc_desc}
        blocked_on_missing_fixture = False

        if gid in NOT_A_CHECK_OVERRIDES:
            bin_, machine, human, needs, rationale = (
                "NOT_A_CHECK", "-", "-", "-",
                "Screening/routing answer option (product-type selector or a "
                "bare 'Yes' PASS_RE's comma-anchored regex doesn't catch), not "
                "a defect condition — verified individually, see "
                "NOT_A_CHECK_OVERRIDES.")
            method = "hand_verified"
        elif PASS_RE.match(resp.strip()):
            bin_, machine, human, needs, rationale = (
                "NOT_A_CHECK", "-", "-", "-",
                "Pass/N-A answer option, not a defect condition.")
            method = "mechanical_pass_answer"
        elif gid in C:
            bin_, machine, human, needs, rationale = C[gid]
            method = "hand_verified"
        else:
            bin_, machine, human, needs, rationale, has_existing_doc = \
                classify_bulk_yellow(g_partial)
            blocked_on_missing_fixture = not has_existing_doc
            method = "bulk_heuristic"

        fnm_or_generic = any(a in ("O-FNM", "GENERIC") for a in agencies)
        topics = (retrieve_topics(sg, q + " " + resp)
                  if fnm_or_generic and bin_ != "NOT_A_CHECK" else [])
        source_rows = sorted({n for m in members for n in m.get("source_rows", [])})

        g = {"group": gid, "question": q, "condition": resp,
             "agencies": agencies,
             "severities": sorted({m["severity"] for m in members if m["severity"]}),
             "codes": codes,
             "source_spreadsheet": source_csv,
             "source_rows": source_rows,
             "rule_count": len(members), "bin": bin_,
             "blocked_on_missing_fixture": blocked_on_missing_fixture,
             "classification_method": method,
             "machine_checkable": machine, "stays_human": human,
             "needed_data": needs, "rationale": rationale,
             "ready_to_build": READY_TO_BUILD.get(gid),
             "guide_candidates": topics,
             "sme_status": "PENDING REVIEW"}
        out_groups.append(g)
        group_counter[bin_] += 1
        rule_counter[bin_] += len(members)
        method_counter[method] += 1

    result = {"block": BLOCK, "rules_total": len(rules),
              "unique_groups": len(groups),
              "bins_by_group": dict(group_counter),
              "bins_by_rule": dict(rule_counter),
              "classification_method_counts": dict(method_counter),
              "classifier": "Claude (compile-time analyst), session 2026-07-30 — "
                            "PENDING SME REVIEW",
              "groups": out_groups}
    with open(OUT_JSON, "w") as f:
        json.dump(result, f, indent=1, sort_keys=True)

    # ------------------------------------------------------------ SME packet
    lines = ["# SME Review Packet — product-specific-check block triage",
             "",
             "**%d rules / %d unique (question, condition) groups.** Every "
             "classification" % (len(rules), len(groups)),
             "below is a *proposal* pending your review — mark each check agree / "
             "correct.",
             "Bins: GREEN = automatable now (none found here — see the decision "
             "doc) · YELLOW = automatable after data/guide work · RED = stays "
             "human · NOT_A_CHECK = pass/N-A answer option, not a defect rule.",
             "",
             "**Source workbook:** `%s` — row numbers below are Excel-style"
             % source_csv,
             "(header = row 1), so you can open the sheet and jump straight to "
             "each rule.",
             "",
             "**Note on this block vs application-verification / asset-"
             "verification:** dedup collapse is essentially zero here (704 "
             "rules -> 703 groups, ~1.001x) — this is the most agency/product-"
             "fragmented of the three blocks triaged so far, by design (FHA/VA/"
             "USDA/ARM/refi-program-specific rules rarely share wording across "
             "agencies). Group-by-group hand review (marked "
             "`classification_method: \"hand_verified\"` in the JSON) covers "
             "every RED, every doc_presence group, both existing product-"
             "specific shapes' candidates, and every READY-TO-BUILD candidate. "
             "The remaining groups (`classification_method: \"bulk_heuristic\"`) "
             "are classified YELLOW by a documented, transparent keyword "
             "heuristic (see the script's module docstring) rather than "
             "individually hand-authored prose — read the condition text "
             "yourself before treating any bulk-heuristic rationale as final.",
             ""]
    defect_groups = [g for g in out_groups if g["bin"] != "NOT_A_CHECK"]
    ng = len(defect_groups)
    lines.append("## Headline")
    lines.append("")
    lines.append("| Bin | Groups | Rules | % of defect groups |")
    lines.append("|---|---|---|---|")
    for b in ("GREEN", "YELLOW", "RED"):
        gc = group_counter[b]
        pct = round(100.0 * gc / ng) if ng else 0
        lines.append("| %s | %d | %d | %d%% |" % (b, gc, rule_counter[b], pct))
    lines.append("| NOT_A_CHECK | %d | %d | — |"
                 % (group_counter["NOT_A_CHECK"], rule_counter["NOT_A_CHECK"]))
    lines.append("")
    lines.append("**Classification method:** %d hand-verified (RED/doc_presence-"
                 "downgrade/ready-to-build groups, individually read in full), "
                 "%d mechanical pass-answer (NOT_A_CHECK via PASS_RE), %d bulk-"
                 "heuristic (of %d total groups)."
                 % (method_counter["hand_verified"],
                    method_counter["mechanical_pass_answer"],
                    method_counter["bulk_heuristic"], len(groups)))
    lines.append("")
    lines.append("## READY TO BUILD candidates (flagged, not implemented)")
    lines.append("")
    for gid, note in sorted(READY_TO_BUILD.items()):
        g = next(x for x in out_groups if x["group"] == gid)
        lines.append("- **G%03d** (%s, row%s %s): %s"
                     % (gid, "/".join(g["agencies"]),
                        "s" if len(g["source_rows"]) > 1 else "",
                        ", ".join(str(n) for n in g["source_rows"]), note))
    lines.append("")
    for b in ("GREEN", "YELLOW", "RED", "NOT_A_CHECK"):
        lines.append("## %s" % b)
        lines.append("")
        for g in out_groups:
            if g["bin"] != b:
                continue
            lines.append("### G%03d — %s [%s]" % (g["group"],
                         ", ".join(g["codes"][:4]) + ("…" if len(g["codes"]) > 4 else ""),
                         "/".join(g["agencies"])))
            lines.append("- **Q:** %s" % g["question"])
            lines.append("- **Defect condition:** %s" % (g["condition"] or "(none)"))
            lines.append("- **Source:** %s, row%s %s"
                         % (g["source_spreadsheet"],
                            "s" if len(g["source_rows"]) > 1 else "",
                            ", ".join(str(n) for n in g["source_rows"])))
            if g["severities"]:
                lines.append("- **Severity:** %s" % "/".join(g["severities"]))
            lines.append("- **Classification method:** %s" % g["classification_method"])
            if g["machine_checkable"] != "-":
                lines.append("- **Machine checks:** %s" % g["machine_checkable"])
            if g["stays_human"] != "-":
                lines.append("- **Stays human:** %s" % g["stays_human"])
            if g["needed_data"] != "-":
                lines.append("- **Data needed:** %s" % g["needed_data"])
            lines.append("- **Rationale:** %s" % g["rationale"])
            if g["ready_to_build"]:
                lines.append("- **READY TO BUILD:** %s" % g["ready_to_build"])
            for t in g["guide_candidates"]:
                lines.append("- **Guide candidate:** %s — %s (PDF p.%d)"
                             % (t["code"], t["title"], t["pdf_page"]))
            lines.append("- **SME:** [ ] agree [ ] correct: ______")
            lines.append("")
    with open(OUT_MD, "w") as f:
        f.write("\n".join(lines) + "\n")

    print("Triage: %d rules -> %d groups | by group: %s | by rule: %s"
          % (len(rules), len(groups), dict(group_counter), dict(rule_counter)))
    print("Method: %s" % dict(method_counter))
    print("Packet: %s" % os.path.relpath(OUT_MD, HERE))


if __name__ == "__main__":
    main()
