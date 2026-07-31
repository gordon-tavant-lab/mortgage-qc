#!/usr/bin/env python3
"""
Layer-2 triage — asset-verification block (304 rules, 297 unique groups).

Same method as layer2_triage.py (application-verification, 81->54), extended to a
much larger, much less textually-duplicative block. Read the module docstring
there for the GREEN/YELLOW/RED/NOT_A_CHECK definitions; they are unchanged here.

Two structural differences from the reference script, both deliberate:

1. Dedup collapse is far smaller here: 304 rules -> 297 unique (question,
   condition) groups (a ~1.02x collapse), vs application-verification's 81->54
   (~1.5x). Verified empirically (decision 017), not assumed going in — the 5
   AMQ agencies write almost entirely independent condition text per asset
   sub-type instead of reusing a small shared phrase set.

2. Given ~297 groups, GREEN/NOT_A_CHECK are derived DETERMINISTICALLY from data
   already computed by amq_compiler.py and a pass/N-A regex, rather than hand-
   authored per group in a giant dict:
     - NOT_A_CHECK: condition text matches ^(Yes,|Not Applicable) (identical
       policy to the reference script's manual G04/G06/G09/... calls), plus one
       explicit override (group 291 — a screening/applicability answer branch,
       "The loan program did not require assets to qualify", not itself a
       defect condition; same pattern as application-verification's group 10).
     - GREEN: every rule in the group already has eval_class in
       {"mapped", "doc_presence"} — i.e. amq_compiler.py's own mechanical
       classification already auto-compiles it (a hand-built SHACL shape, or
       the "not in file/missing/not provided" doc-presence auto-compile).
       This mirrors the reference script's own `blocked_on_missing_fixture`
       override, which already deferred to amq_compiler.py's eval_class at
       runtime instead of re-deriving that judgment by hand per group.
   The REMAINING ~210 groups — the ones that actually require reading the
   AMQ condition text and exercising judgment — are hand-classified in the `C`
   dict below, exactly as in the reference script.

Outputs:
  compiled/triage_asset-verification.json
  out/TRIAGE-PACKET-asset-verification.md
"""
import json
import os
import re
from collections import OrderedDict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
RULESET = os.path.join(HERE, "compiled", "ruleset.json")
SG_INDEX = os.path.join(HERE, "compiled", "selling_guide_index.json")
OUT_JSON = os.path.join(HERE, "compiled", "triage_asset-verification.json")
OUT_MD = os.path.join(HERE, "out", "TRIAGE-PACKET-asset-verification.md")

BLOCK = "asset-verification"

PASS_RE = re.compile(r"^(Yes,|Not Applicable)", re.I)

# Group 291 ("The loan program did not require assets to qualify", answering
# "Were assets utilized from any of the following to qualify the loan?") is a
# screening/applicability answer branch, not a defect condition — the same
# pattern as application-verification's group 10 ("Is one or more consumers...
# LEP? No" -> NOT_A_CHECK, a screening answer, not "Yes all requirements met").
NOT_A_CHECK_OVERRIDES = {291}

# ---------------------------------------------------------------------------
# READY TO BUILD candidates (task C): flagged here, NOT implemented. Every one
# is either (a) a straight extension of an EXISTING mapped shape's exception-
# code list — zero new code, zero new fixture — or (b) a new derived fact
# computable entirely from fields/entities extract_loan.py ALREADY captures.
# Surfaced in the SME packet and the final report; a human decides whether to
# build them next.
READY_TO_BUILD = {
    135: ("WIRE, don't build — GiftEvidenceShape (CHK-AST-002) already checks "
          "exactly this fact (gift_transfer_evidence_in_file), but "
          "MAPPED_SHAPES wires it to ZERO amq_exception_codes today "
          "(amq_compiler.py: \"GiftEvidenceShape\": {...\"amq_exception_codes\": []}). "
          "O-RHS-02772 (\"No, proof of transfer not provided\") is a clean "
          "1-line addition to that list — no new code, no new fixture."),
    25:  ("Extend LargeDepositShape (CHK-AST-001)'s amq_exception_codes to "
          "O-FRD-58101 — same unsourced-large-deposit defect the shape "
          "already encodes for O-FNM-00215, FRD wording variant. Verify "
          "wording match before wiring."),
    64:  ("Extend LargeDepositShape (CHK-AST-001)'s amq_exception_codes to "
          "O-FHA-50677-1 — same defect, FHA wording variant ('new accounts & "
          "recent deposits over 50% of adjusted income'). Verify wording match."),
    102: ("Extend LargeDepositShape (CHK-AST-001)'s amq_exception_codes to "
          "O-FRD-50451 — condition text is a BYTE-FOR-BYTE duplicate of the "
          "already-mapped O-FNM-00215 row (group 287), just filed under a "
          "different AMQ question category ('general asset documentation' "
          "vs 'verification of deposit assets'). Highest-confidence candidate "
          "in this batch."),
    11:  ("New derivation, no new fixture: 'Borrower has a loan outstanding "
          "secured by funds on deposit and these funds were treated as an "
          "asset' (O-VA-00262) is checkable by cross-referencing entities "
          "extract_loan.py ALREADY extracts — tradelines/urla_liabilities "
          "(for the secured loan) against bank_txns (for the deposit treated "
          "as an asset) — no new document type needed, just new join logic."),
    130: ("Partial win now: 'Borrower received cash back at closing due to a "
          "gift of equity, sweat equity, or rent credits' (O-RHS-57768) can "
          "be cross-referenced today against cash_out_to_borrower_1003 "
          "(already extracted) + gift_transfer_evidence_in_file/gift_letter "
          "presence; a full sweat-equity/rent-credit fact still needs new "
          "fixtures, but the gift-fund half is buildable now."),
}

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


# ---------------------------------------------------------------------------
# Hand-authored classifications for the ~210 groups that are NOT mechanically
# resolvable (not a Yes/N-A pass answer, not already mapped/doc_presence).
# Fields: bin, machine (what automates), human (what stays human), needs (data
# to add), rationale. "-" = empty, matching the reference script's convention.
C = {
    1: ("YELLOW", "-", "-",
        "VOD doc type (not in any synthetic loan) or a bank_statement "
        "balance-vs-claimed-funds derivation",
        "VA AUS-track funds-on-deposit verification; bank_statement exists in the corpus "
        "(loan 01) but a distinct VOD form does not, and no field compares statement "
        "balance to a claimed asset amount yet."),
    2: ("YELLOW", "-", "-", "same as G001",
        "Same defect as G001, Manual-UW track (2 months, not 1)."),
    4: ("YELLOW", "-", "-",
        "prior-home-sale settlement statement + net-proceeds field (deepen closing_disclosure)",
        "Crisp documentation-presence check; closing_disclosure doc type exists in every "
        "loan but a distinct prior-sale settlement statement / net-proceeds field is not "
        "yet in FIELD_SPECS."),
    5: ("YELLOW", "-", "-", "sale-proceeds equity-accumulation field, same doc gap as G004",
        "Same net-sale-proceeds family as G004."),
    7: ("YELLOW", "second-mortgage/subordinate-loan note presence", "catch-all 'and/or all requirements not met'",
        "secondary financing note doc type (not in corpus)",
        "Presence half is crisp; the appended open-ended 'all requirements' clause stays human."),
    9: ("YELLOW", "-", "-", "VA NOV reasonable-value + sales-price + down-payment fields (deepen va_nov/1003)",
        "va_nov doc exists (loan 03) with nov_issue_date extracted, but not a 'reasonable "
        "value' amount field; sales-price/down-payment comparison needs new fields, not a "
        "new document."),
    10: ("YELLOW", "-", "-", "same fields as G009 (VA NOV reasonable value vs sales price)",
         "Same VA reasonable-value family as G009 (AUS-Refer variant)."),
    11: ("YELLOW", "-", "-",
         "cross-reference of tradelines/urla_liabilities against bank_txns (new derivation, no new fixture)",
         "READY TO BUILD candidate — see READY_TO_BUILD; both entity types this needs "
         "(tradelines, bank_txns) are already extracted for every loan."),
    12: ("RED", "-", "'reasonable explanation... how money was saved'",
         "-", "Narrative/judgment call on the borrower's own explanation — same class as "
              "application-verification's judgment-word REDs."),
    13: ("YELLOW", "HAP fee > $250 threshold (once HAP data exists)",
         "catch-all 'all VA, property & occupancy standards were not met'",
         "VA Homebuyer Assistance Program (HAP) fee/agreement doc (not in corpus)",
         "The $250 threshold is crisp math once the HAP fee is captured; the appended "
         "open-ended standards clause stays human."),
    15: ("YELLOW", "-", "-", "VA residual-income/reserves worksheet (EXPECTED_DOCS_BY_PROGRAM's "
         "residual_income_worksheet entry exists for VA but is not yet a reserves fact)",
         "Reserves-for-rental-income is a well-defined number once the worksheet exists; "
         "no such document in any of the 5 synthetic loans today."),
    16: ("YELLOW", "-", "-", "same VA-reasonable-value fields as G009/G010, plus a HAP-grant field",
         "Same reasonable-value family as G009/G010."),
    17: ("YELLOW", "-", "-",
         "closing-cost + down-payment + total-available-assets derivation (deepen 1003/closing_disclosure)",
         "Generic cash-to-close sufficiency; both source docs already exist in the corpus, "
         "the derived comparison does not."),
    18: ("RED", "-", "open-ended 'all requirements not met for use of funds in a Community Savings System'",
         "-", "Bare catch-all with no specific fact stated — needs SME decomposition into "
              "the actual Community-Savings-System documentation checklist, same pattern as "
              "application-verification's VA disclosure catch-all."),
    20: ("RED", "-", "'requirements not met for the type of benefit received' (type-dependent, unstated)",
         "-", "Open-ended, benefit-type-dependent catch-all — no single checkable fact until "
              "an SME enumerates EAH benefit types and their individual requirements."),
    22: ("YELLOW", "EAH benefit terms doc presence", "-",
         "Employer Assisted Homeownership benefit agreement doc type (not in corpus)",
         "Unlike G020, this row IS a crisp presence check ('terms... not in file') — same "
         "topic, very different condition, classified independently per instructions."),
    23: ("RED", "-", "open-ended 'all requirements not met for use of Individual Development Account (IDA)'",
         "-", "Same bare-catch-all pattern as G018."),
    25: ("YELLOW", "unsourced-large-deposit comparison (bank_txns credit_amount vs base_monthly_income_1003)",
         "-", "none if wired — see READY_TO_BUILD",
         "READY TO BUILD candidate: same defect family as the already-mapped "
         "LargeDepositShape (O-FNM-00215) — FRD wording variant."),
    27: ("YELLOW", "-", "-", "credit-card-rewards statement (ownership + cash value), not in corpus",
         "Crisp presence/valuation check; no such document exists in any synthetic loan."),
    28: ("YELLOW", "-", "-", "same credit-card-rewards doc gap as G027",
         "Same family as G027 (redemption-timing variant)."),
    30: ("YELLOW", "-", "-", "home-sale listing/contract doc (not in corpus)",
         "Sale-proceeds calculation is deterministic math once the listing/contract exists; "
         "it doesn't today."),
    31: ("YELLOW", "-", "IRC Section 1031 compliance determination",
         "1031-exchange documentation (not in corpus)",
         "Presence is checkable once the doc exists; full IRC compliance stays a judgment "
         "call layered on top."),
    33: ("YELLOW", "-", "-", "prior-sale settlement statement (distinct from this loan's closing_disclosure)",
         "Same net-cash-proceeds-from-a-prior-sale family as G004/G033."),
    34: ("YELLOW", "-", "-", "employee relocation buy-out agreement (not in corpus)",
         "Crisp doc-presence check; niche document, absent from all 5 synthetic loans."),
    35: ("RED", "-", "'unreasonable' savings judgment", "-",
         "'Unreasonable' dominates the compound condition even though 'calculated "
         "incorrectly' alone would be crisp math — no anticipated-savings plan data exists "
         "to compute against regardless."),
    37: ("YELLOW", "-", "-", "DU (Fannie Mae AUS) findings report, not in corpus",
         "This pilot has no AUS-submission export at all for FNM (the RHS-equivalent, GUS "
         "findings, IS already partially extracted for loan 05 — a natural next fixture, "
         "not built here)."),
    38: ("YELLOW", "-", "-", "realtor-commission-as-credit field on closing_disclosure (deepen extraction)",
         "closing_disclosure exists in every loan; the specific credit-line field does not "
         "yet — Bucket-B-style (no new fixture)."),
    39: ("YELLOW", "-", "-", "same DU-findings gap as G037",
         "Same DU-submission family as G037."),
    40: ("YELLOW", "-", "-",
         "EMD amount field (1003/purchase contract) cross-referenced against bank_txns debit — same as G081",
         "Duplicate condition text to G081 filed under a different AMQ question category "
         "(same pattern as G102/G287); both need a new EMD-amount field, not a new fixture."),
    43: ("YELLOW", "-", "-", "total-closing-funds-needed vs total-assets-available derivation",
         "Generic sufficiency check, same family as G073/G103."),
    44: ("YELLOW", "-", "-", "cryptocurrency-to-USD exchange confirmation (not in corpus)",
         "Same virtual-currency family as G174/G200/G201/G205/G213."),
    45: ("YELLOW", "-", "-", "personal/secured loan note (not in corpus)",
         "Crisp doc-presence check once the note exists; no such document in any loan today."),
    47: ("YELLOW", "-", "-", "bridge/swing loan payment-ability worksheet (not in corpus)",
         "Same bridge-loan family as G049/G198/G263."),
    49: ("YELLOW", "-", "-", "bridge loan security instrument (not in corpus)",
         "Same bridge-loan family as G047."),
    50: ("YELLOW", "-", "-",
         "business-account-type flag + 2-month-average-balance derivation (deepen bank_statement)",
         "bank_statement doc exists generically, but neither business-vs-personal account "
         "classification nor a multi-month average is modeled today."),
    51: ("YELLOW", "-", "-", "account-ownership field on bank_statement (not currently captured)",
         "Same business-account family as G050/G052/G053."),
    52: ("YELLOW", "-", "-", "cash-flow-analysis worksheet (not in corpus)",
         "Same business-account family as G050/G051."),
    53: ("RED", "-", "'not detrimental to the business' judgment", "-",
         "Classic subjective business-impact judgment — no bright-line test."),
    55: ("RED", "-", "'not reasonable' cash-on-hand judgment", "-",
         "'Reasonable' dominates; deposit/escrow half is bundled into the same compound "
         "condition rather than checkable standalone."),
    57: ("YELLOW", "-", "-",
         "MRI + closing-costs/prepaids + seller-tax-credit fields (deepen 1003/closing_disclosure)",
         "Compound cash-to-close math; every source doc exists in the corpus, the specific "
         "derived comparison does not."),
    58: ("RED", "-", "'reasonable and customary' fee judgment", "-",
         "Fee-reasonableness determination — the same judgment class as application-"
         "verification's fee/discrepancy REDs."),
    60: ("YELLOW", "-", "-", "landlord education certificate / experience documentation (not in corpus)",
         "Crisp presence/duration check once the document exists."),
    61: ("YELLOW", "-", "-", "premium-pricing-credit-application field (deepen closing_disclosure)",
         "closing_disclosure exists in every loan; the specific credit-application field "
         "does not yet — related to G162."),
    62: ("YELLOW", "-", "-", "life insurance policy/surrender statement (not in corpus)",
         "Same life-insurance family as G167."),
    64: ("YELLOW", "unsourced-large-deposit comparison (same logic as G025/G102)", "-",
         "none if wired — see READY_TO_BUILD",
         "READY TO BUILD candidate: FHA wording variant of the already-mapped "
         "LargeDepositShape defect."),
    65: ("YELLOW", "-", "-", "Third Party Verification (TPV) report doc (not in corpus)",
         "Crisp 30-day-currency check once the TPV report exists as a document type."),
    66: ("YELLOW", "-", "-", "aggregate 'current balance' fact derived from bank_txns (deepen extraction)",
         "bank_statement/bank_txns already extract a running balance column; a simple "
         "most-recent-balance derivation would make this near-ready — flagged as a "
         "secondary READY-TO-BUILD-adjacent candidate, not implemented here."),
    69: ("YELLOW", "-", "-",
         "reserves field on gus_findings (deepen extraction — doc exists for loan 05, field does not)",
         "GUS findings doc type is already parsed for USDA loans (usda_income_limit, "
         "usda_adjusted_household_income); a post-closing-reserves field is not yet in "
         "FIELD_SPECS['gus_findings'] — Bucket-B-style, no new fixture."),
    70: ("YELLOW", "-", "-", "multi-statement balance comparison (deepen bank_statement, or a 2nd month's fixture)",
         "Needs either a second month's bank statement (each loan currently has one) or a "
         "running-balance derivation from the one statement in hand."),
    71: ("YELLOW", "-", "-", "lender-review-completed flag (not currently modeled)",
         "Related to, but not identical to, the large-deposit family (G025/G064/G102/G287) "
         "— this asks whether the LENDER reviewed for large/unusual deposits (a process "
         "fact), not a specific dollar threshold, so it is not a blind extension of "
         "LargeDepositShape."),
    72: ("YELLOW", "-", "-", "payroll-vs-non-payroll deposit classification (deepen bank_txns)",
         "bank_txns already extracts each transaction; a payroll/non-payroll categorization "
         "does not exist yet."),
    73: ("YELLOW", "-", "-", "same sufficiency derivation as G043/G103",
         "Same generic-sufficiency family as G043."),
    75: ("YELLOW", "-", "-",
         "credit-card-paid-costs field + loan-amount comparison (2% threshold; deepen closing_disclosure/1003)",
         "Crisp 2% threshold math once the specific field exists; not modeled today."),
    76: ("YELLOW", "-", "-", "credit-card-reward-conversion sourcing doc (not in corpus)",
         "Related to the large-deposit family but needs a credit-card-specific sourcing "
         "document, not present."),
    79: ("YELLOW", "-", "'is a 501c' determination",
         "charitable-org / DPA-program documentation (IRS determination letter; not in corpus)",
         "Usually evidenced by a document (not a live registry, unlike NMLS) — kept YELLOW, "
         "but flagged as a borderline candidate worth a second look before ruling out "
         "Bucket C entirely if no such letter is ever produced in practice."),
    81: ("YELLOW", "-", "-", "same as G040 (duplicate condition, different AMQ question category)",
         "Duplicate condition text to G040."),
    82: ("YELLOW", "-", "-", "purchase/sales contract document (not present as a doc type in any synthetic loan)",
         "Notable systemic gap: NO purchase contract document exists in any of the 5 "
         "synthetic loans — several EMD-family rules (G040/G081/G084/G086) trace back to "
         "this same missing document."),
    84: ("YELLOW", "-", "-", "EMD amount field cross-referenced against bank_txns debit (deepen extraction)",
         "Same EMD-clearing family as G040/G081; bank_statement doc exists, EMD-amount "
         "field does not."),
    86: ("YELLOW", "-", "-", "EMD amount + sales price fields (1% threshold; deepen 1003/contract)",
         "Crisp 1% threshold math once fields exist; same EMD family as G084."),
    88: ("YELLOW", "-", "'meets FNMA req's' guideline-compliance judgment",
         "employer-financing agreement doc (not in corpus)",
         "Presence is crisp; full guideline-compliance determination stays partly human."),
    90: ("YELLOW", "-", "-", "employer-assistance award/receipt doc (not in corpus)",
         "Crisp presence/receipt check once the document exists."),
    92: ("YELLOW", "-", "-", "foreign-currency exchange confirmation (not in corpus)",
         "Same foreign-funds family as G191/G192/G200/G201/G205."),
    95: ("YELLOW", "-", "-", "LPA (Freddie Mac AUS) findings report, not in corpus",
         "Same AUS-submission gap as G037/G039 (Fannie's DU) — neither AUS export exists "
         "in this pilot; RHS's GUS is the only AUS output currently parsed."),
    96: ("YELLOW", "-", "-", "asset-internet-printout document (distinct alt-doc type, not in corpus)",
         "Crisp completeness check once the specific alt-document format exists."),
    97: ("YELLOW", "-", "-", "VOD form (distinct from bank_statement; not in corpus)",
        "Same VOD-family gap as G001/G002/G105/G256/G257/G286."),
    98: ("RED", "-", "'Streamlined Accept or Standard documentation... per asset type' matrix",
         "-", "Open-ended compliance check across an entire LPA documentation matrix spanning "
              "many asset types — needs SME decomposition before any single fact is "
              "checkable, same pattern as application-verification's VA disclosure catch-all."),
    99: ("YELLOW", "-", "-", "minimum-contribution + fund-source fields (deepen 1003/closing_disclosure)",
         "Crisp comparison once fields exist; doc already in the corpus."),
    100: ("YELLOW", "-", "-", "account-open-date field (deepen bank_statement)",
          "bank_statement exists; a distinct account-open-date fact (for the 90-day test) "
          "does not."),
    101: ("RED", "-", "'third-party verification requirements' (unspecified)", "-",
          "Vague catch-all with zero stated specifics — needs SME decomposition."),
    102: ("YELLOW", "unsourced-large-deposit comparison (identical text to the mapped O-FNM-00215 row)",
          "-", "none if wired — see READY_TO_BUILD",
          "READY TO BUILD candidate — highest confidence: condition text is a byte-for-byte "
          "duplicate of group 287 (already mapped to LargeDepositShape), just filed under a "
          "different AMQ question category."),
    103: ("YELLOW", "-", "-", "same sufficiency derivation as G043/G073",
          "Same generic-sufficiency family as G043."),
    104: ("YELLOW", "-", "-", "underwriter asset-analysis worksheet (not in corpus)",
          "Crisp presence check once the document exists."),
    105: ("YELLOW", "-", "-", "same VOD-format detail gap as G097",
          "Same VOD family as G097."),
    107: ("YELLOW", "-", "-", "gift-of-equity/reserves designation field (deepen gift_letter)",
          "gift_letter doc exists (loan 02); a distinct equity-vs-cash + reserves-use field "
          "does not yet — Bucket-B-style, no new fixture."),
    108: ("YELLOW", "-", "-", "donor-ability + transfer-method fields (deepen gift_letter)",
          "Plausible near-relative of the gift_transfer_evidence_in_file fact GiftEvidenceShape "
          "already checks, but bundles an extra 'donor ability' clause the existing boolean "
          "may not cover — worth SME review before wiring, not a blind copy of G135's fix."),
    109: ("YELLOW", "-", "-", "same DU-submission gap as G037, plus a gift-identification flag",
          "DU-family gap, same as G037/G039."),
    110: ("YELLOW", "-", "donor-acceptability guideline judgment",
          "donor-relationship field (deepen gift_letter)",
          "Presence of a stated donor/relationship is crisp; whether that relationship "
          "is 'acceptable' per guide stays partly human."),
    111: ("YELLOW", "-", "-", "equity amount cross-check against closing_disclosure (deepen extraction)",
          "Both docs (gift_letter, closing_disclosure) exist in the corpus; the cross-"
          "reference field does not."),
    112: ("YELLOW", "-", "-", "co-residency/occupancy certification doc (not in corpus)",
          "Crisp presence check once the document exists; niche, absent from all 5 loans."),
    113: ("YELLOW", "-", "-", "same co-residency certification gap as G112",
          "Same family as G112 (pooled-gift-funds variant)."),
    115: ("YELLOW", "-", "-", "DU borrower-number submission detail (AUS-family, not in corpus)",
          "Same AUS-submission gap as G037/G039/G095."),
    116: ("YELLOW", "-", "-", "grant award letter / legal agreement (not in corpus)",
          "Crisp presence check once the document exists."),
    117: ("YELLOW", "-", "grant-entity acceptability judgment",
          "grant award letter (not in corpus, same as G116)",
          "Presence of a stated entity is crisp; guide-based acceptability stays human."),
    119: ("YELLOW", "-", "donor-acceptability guideline judgment", "donor-relationship field (deepen gift_letter)",
          "Same donor-acceptability family as G110 (FRD wording variant)."),
    120: ("YELLOW", "-", "-", "equity amount cross-check (deepen gift_letter + closing_disclosure)",
          "Same family as G111 (FRD variant)."),
    121: ("YELLOW", "-", "-", "diploma/transcript documentation (niche, not in corpus)",
          "Crisp presence check; graduation-gift program docs don't exist in any synthetic loan."),
    122: ("YELLOW", "-", "-", "graduation-date evidence + gift_letter/bank_statement date fields",
          "Same graduation-gift family as G121; also needs a graduation-date fact no "
          "current document supplies."),
    124: ("YELLOW", "-", "-", "agency-eligibility documentation (deepen gift_letter or a new doc, unclear which)",
          "Crisp presence check once whatever 'eligible agency' documentation is defined "
          "exists."),
    125: ("YELLOW", "-", "-", "gift-amount-stated field (deepen gift_letter FIELD_SPECS)",
          "gift_letter doc exists in the corpus (loan 02); extracting a gift-amount field "
          "is a plausible near-term Bucket-B win, though not implemented here."),
    126: ("YELLOW", "-", "-", "same DU/LPA borrower-number gap as G115",
          "Same family as G115 (FRD variant)."),
    127: ("YELLOW", "-", "-", "transfer-method field (deepen gift_letter)",
          "Related to the gift_transfer_evidence_in_file family (see G135's READY-TO-BUILD "
          "note) but bundles multiple named-recipient variants (donor acct/borr acct/"
          "closing agent/realtor/builder) the existing boolean fact likely doesn't "
          "distinguish — needs SME review before wiring."),
    128: ("YELLOW", "-", "-", "marriage license document (niche, not in corpus)",
          "Crisp presence/timing check once the document exists."),
    130: ("YELLOW", "-", "-",
          "cross-reference of cash_out_to_borrower_1003 (already extracted) against gift/"
          "sweat-equity/rent-credit facts (partial fixture gap for the latter)",
          "READY TO BUILD candidate (partial) — see READY_TO_BUILD."),
    131: ("YELLOW", "-", "-", "transfer-method field, same gift-transfer family as G108/G127",
          "Worth SME review before wiring to the existing gift_transfer_evidence_in_file "
          "fact (same caution as G108/G127)."),
    132: ("YELLOW", "-", "-", "sale-price-reduction field cross-check (deepen closing_disclosure)",
          "closing_disclosure exists in every loan; the specific reduction-applied field "
          "does not."),
    133: ("YELLOW", "-", "donor-acceptability guideline judgment", "donor-relationship field (deepen gift_letter)",
          "Same donor-acceptability family as G110/G119/G142 (RHS wording variant)."),
    135: ("YELLOW", "gift_transfer_evidence_in_file (fact ALREADY extracted and checked by GiftEvidenceShape)",
          "-", "none — wire this exception code into MAPPED_SHAPES; see READY_TO_BUILD",
          "READY TO BUILD candidate — top pick: the check this row needs already exists "
          "in code (GiftEvidenceShape/CHK-AST-002) but is wired to zero AMQ exception "
          "codes today."),
    137: ("YELLOW", "-", "-", "land-gift title-transfer documentation (niche, not in corpus)",
          "Crisp presence check once the document exists."),
    138: ("YELLOW", "-", "-", "payment-method field (deepen gift_letter/closing_disclosure)",
          "Both docs exist in the corpus; the specific EFT/cashier's-check-method field "
          "does not."),
    141: ("YELLOW", "-", "donor-family-member determination", "donor-relationship field (deepen gift_letter)",
          "Same donor-relationship family as G110/G119/G133 (FHA gift-of-equity wording)."),
    142: ("YELLOW", "-", "donor-acceptability guideline judgment", "donor-relationship field (deepen gift_letter)",
          "Same donor-acceptability family as G110/G119/G133 (FHA wording variant)."),
    144: ("YELLOW", "-", "-", "government bond certificate/statement (not in corpus)",
          "Crisp ownership/valuation check once the document exists."),
    146: ("YELLOW", "-", "'terms of use' compliance judgment", "grant award/terms documentation (not in corpus)",
          "Receipt-verification is crisp once the doc exists; terms-of-use compliance "
          "stays partly human."),
    148: ("YELLOW", "-", "-", "IPC amount/source field (deepen closing_disclosure)",
          "closing_disclosure exists in every loan; no interested-party-contribution line "
          "item is in FIELD_SPECS yet — Bucket-B-style for the whole IPC family "
          "(G148-166), no new fixture needed, just new fields on an existing document."),
    149: ("YELLOW", "-", "-", "IPC-use classification field (deepen closing_disclosure)",
          "Same IPC family as G148."),
    150: ("YELLOW", "-", "-", "IPC amount + applicable-limit fields (deepen closing_disclosure)",
          "Crisp limit-comparison math once fields exist; same IPC family as G148."),
    152: ("YELLOW", "-", "-", "sale-price + IPC + LTV recalculation fields (deepen closing_disclosure/1003)",
          "Same IPC family as G148."),
    153: ("YELLOW", "-", "-", "cross-document IPC reconciliation (contract vs CD vs appraisal)",
          "Harder than a simple presence check (detecting an UNDISCLOSED item by definition "
          "requires comparing multiple documents for inconsistency), but still a factual "
          "cross-document comparison, not subjective judgment — kept YELLOW, not RED."),
    154: ("YELLOW", "-", "-", "same IPC-limit fields as G150", "Same IPC family (FNM wording variant)."),
    155: ("YELLOW", "-", "-", "same IPC-use fields as G149", "Same IPC family (FNM wording variant)."),
    156: ("YELLOW", "-", "-", "same IPC-use fields as G149", "Same IPC family (FNM wording variant)."),
    157: ("RED", "-", "'consistent fees/expenses/resolution of discrepancies'", "-",
          "Open-ended cross-file discrepancy sweep — same judgment class as application-"
          "verification's file-wide-discrepancies RED."),
    158: ("YELLOW", "-", "-", "'legal document in lieu of contract' (niche IPC doc, not in corpus)",
          "Crisp presence check once the document exists; touches appraisal workflow too."),
    159: ("YELLOW", "-", "'did not document no repayment is req'd' compliance judgment",
          "lender-incentive agreement (not in corpus)",
          "Presence is crisp; full requirement-compliance stays partly human."),
    160: ("YELLOW", "-", "-", "lender-incentive + LTV/refi-type fields (deepen closing_disclosure)",
          "Same IPC/lender-incentive family as G159."),
    162: ("YELLOW", "-", "-", "premium-pricing-credit field (deepen closing_disclosure)",
          "Same premium-pricing family as G061."),
    163: ("YELLOW", "-", "-", "same IPC-limit fields as G150 (6% threshold)",
          "Same IPC family as G148/G150, crisp threshold math once fields exist."),
    164: ("YELLOW", "-", "-", "IPC-abatement field (deepen closing_disclosure)",
          "Same IPC family as G148."),
    165: ("RED", "-", "'undisclosed IPC's... ineligible for sale to Fannie Mae' investor-eligibility judgment",
          "-", "Holistic GSE-investor-eligibility determination, not a single checkable fact "
               "— stays human."),
    166: ("YELLOW", "-", "-", "cross-doc IPC total reconciliation (contract/92900-LT/CD)",
          "hud_92900a doc type exists (loan 02) though the specific 92900-LT (loan-estimate "
          "side) form is distinct; same IPC family as G148."),
    167: ("YELLOW", "-", "'liquidation if applicable' judgment", "life insurance statement (not in corpus)",
          "Same life-insurance family as G062."),
    169: ("YELLOW", "-", "-", "cryptocurrency documentation (not in corpus)",
          "Same virtual-currency family as G044/G174/G200/G201/G205/G213."),
    171: ("YELLOW", "-", "-",
          "'amount needed to close' + liquidation-evidence fields (20% threshold; deepen extraction)",
          "Crisp threshold math once fields exist; bank_statement/1003 exist, specific "
          "liquidation-evidence doc likely separate and absent."),
    173: ("YELLOW", "-", "-", "bill-of-sale document (not in corpus)",
          "Same personal-property-sale family as G185/G186/G195/G261."),
    174: ("YELLOW", "-", "-", "same cryptocurrency gap as G169",
          "Same virtual-currency family as G169."),
    175: ("YELLOW", "-", "-", "brokerage/stock statement (not in corpus)",
          "Same stocks/bonds family as G144/G214/G262/G273/G275/G281/G283."),
    176: ("YELLOW", "-", "'permissible source that meets req's' guideline judgment",
          "MRI-source field + SME-defined permissible-source list",
          "Source-name presence is crisp; full permissibility determination stays partly "
          "human."),
    179: ("YELLOW", "-", "-", "DU reserve-requirement field (AUS-family, not in corpus)",
          "Same AUS-submission gap as G037/G039/G095/G243/G244."),
    180: ("YELLOW", "-", "'unacceptable source' guideline judgment", "reserve-source field",
          "Same source-acceptability pattern as the donor-acceptability family."),
    182: ("YELLOW", "-", "-", "prior-sale entitlement field (deepen closing_disclosure)",
          "Same net-proceeds-entitlement family as G183/G187."),
    183: ("YELLOW", "-", "-", "net-proceeds cross-check field (deepen closing_disclosure)",
          "closing_disclosure exists in the corpus; the specific net-proceeds-verified "
          "field does not — same family as G182."),
    185: ("YELLOW", "-", "-", "bill-of-sale / personal-property-sale doc (not in corpus)",
          "Same family as G173/G186/G195."),
    186: ("YELLOW", "-", "-", "same bill-of-sale gap as G185",
          "Same personal-property-sale family as G185."),
    187: ("YELLOW", "-", "-", "arm's-length-transaction affidavit (not in corpus)",
          "'Arm's length' is normally evidenced by a specific affidavit/settlement doc, not "
          "inherently a subjective call once that doc exists — kept YELLOW, not RED."),
    190: ("RED", "-", "'less than fair market value' determination", "-",
          "Fair-market-value judgment without an appraisal-like valuation document; also "
          "needs a 2-year asset-disposal history this pilot doesn't track at all."),
    191: ("YELLOW", "-", "-", "foreign asset statement + translation (not in corpus)",
          "Same foreign-asset family as G092/G200/G201/G205."),
    192: ("YELLOW", "-", "-", "same foreign-asset gap as G191",
          "Same foreign-asset family as G191."),
    193: ("RED", "-", "'no written explanation... how... accumulated' narrative adequacy", "-",
          "Same narrative-adequacy judgment class as G012."),
    195: ("YELLOW", "-", "-", "personal-property valuation doc (not in corpus)",
          "Same family as G185/G186."),
    196: ("RED", "-", "open-ended 'all requirements for a pooled savings were not met'", "-",
          "Bare catch-all, same pattern as G018/G023."),
    197: ("YELLOW", "-", "-", "trust agreement / trustee statement (not in corpus)",
          "Same trust family as G214/G281/G283."),
    198: ("YELLOW", "-", "-", "bridge loan security/receipt doc (not in corpus)",
          "Same bridge-loan family as G047/G049/G263."),
    199: ("YELLOW", "-", "-", "same relocation buy-out agreement gap as G034",
          "Same family as G034."),
    200: ("YELLOW", "-", "-", "foreign-asset translation doc (not in corpus)",
          "Same foreign-asset family as G191/G201/G205."),
    201: ("YELLOW", "-", "-", "same foreign-currency exchange gap as G092",
          "Same foreign-funds family as G092/G200/G205."),
    202: ("YELLOW", "-", "-", "credit-card/cash-advance/LOC documentation (not in corpus)",
          "Related to G027/G223 (unallowable-funds family)."),
    203: ("YELLOW", "-", "-", "HELOC agreement + proceeds doc (not in corpus)",
          "Crisp presence/security check once the document exists."),
    204: ("YELLOW", "-", "-", "trade-in contract doc (not in corpus)",
          "Same trade-equity family as G220/G221/G279."),
    205: ("YELLOW", "-", "-", "same foreign-currency exchange gap as G092/G201",
          "Same foreign-funds family as G092/G201."),
    206: ("YELLOW", "-", "-", "secured-loan documentation (not in corpus)",
          "Related to G045 (personal/secured loan family)."),
    207: ("YELLOW", "-", "-", "IDA program documentation (not in corpus)",
          "Related to G023 (Individual Development Account family)."),
    209: ("YELLOW", "-", "'participants... eligible' determination", "pooled-funds agreement (not in corpus)",
          "Related to G196 (pooled-savings family); presence is crisp, eligibility "
          "determination stays partly human."),
    210: ("YELLOW", "-", "-", "same 1031-exchange documentation gap as G031",
          "Same family as G031."),
    211: ("YELLOW", "-", "-", "tax-proration-credit field (deepen closing_disclosure)",
          "closing_disclosure exists in every loan; the specific proration-credit field "
          "does not."),
    212: ("YELLOW", "-", "-", "rent-to-own agreement (not in corpus)",
          "Same rent-credit family as G217/G231-235."),
    213: ("YELLOW", "-", "-", "same virtual-currency exchange gap as G044",
          "Same virtual-currency family as G044/G169/G174."),
    214: ("YELLOW", "-", "-", "trust manager statement (not in corpus)",
          "Same trust family as G197/G281/G283."),
    215: ("YELLOW", "-", "-", "inducement-to-purchase field (deepen closing_disclosure)",
          "Related to the IPC family (G148); doc exists, field does not."),
    217: ("YELLOW", "-", "-", "rent credit agreement (not in corpus)",
          "Same rent-credit family as G212/G231-235."),
    218: ("YELLOW", "-", "RE license 'entitlement' verification",
          "RE agent license copy (not in corpus) — possible Bucket-C candidate",
          "Borderline: a license copy in the file might suffice, but genuinely current "
          "license STATUS verification could require a state licensing-board lookup, "
          "similar in kind to the discarded NMLS rule (decision 016). Flagged, not "
          "unilaterally discarded — a human should decide."),
    219: ("YELLOW", "-", "-", "sweat-equity labor/materials documentation (not in corpus)",
          "Same family as G278."),
    220: ("YELLOW", "-", "-", "trade-in contract/appraisal doc (not in corpus)",
          "Same trade-equity family as G204/G221/G279."),
    221: ("YELLOW", "-", "-", "same trade-equity documentation gap as G220",
          "Same family as G220."),
    223: ("YELLOW", "-", "-", "personal-loan/credit documentation (not in corpus)",
          "Related to G045/G202 (unallowable-funds family)."),
    225: ("YELLOW", "-", "'reasonability' clause (one of three possible defects in this row)",
          "private-savings-club statement (not in corpus)",
          "Two of the three listed conditions (club duration, receipt of funds) are crisp "
          "facts; only the appended 'reasonability' clause stays human — kept YELLOW, not "
          "RED, since it isn't the row's sole condition."),
    228: ("RED", "-", "underwriter review-completeness sweep across all recurring bank-statement items",
         "-", "An underwriter's own review-completion judgment across every recurring "
              "payment — inherently a process/judgment check, not a bright-line fact the "
              "file can self-certify."),
    231: ("YELLOW", "-", "-", "lease/option-to-purchase agreement (not in corpus)",
          "Same rent-credit family as G212/G217/G233-235."),
    233: ("YELLOW", "-", "-", "market-rent determination field (deepen appraisal, or a rent-schedule addendum)",
          "appraisal doc exists in the corpus but doesn't normally capture a market-rent "
          "determination — likely needs a distinct rent-schedule addendum."),
    234: ("YELLOW", "-", "-", "market-rent + actual-rent fields (deepen appraisal/lease)",
          "Crisp math once fields exist; same rent-credit family as G233."),
    235: ("YELLOW", "-", "-", "rent-back-credit field (deepen closing_disclosure)",
          "closing_disclosure exists; the specific rent-back-credit-as-source-of-funds "
          "field does not."),
    236: ("YELLOW", "-", "-", "collateralized-loan note (not in corpus)",
          "Related to G045/G206 (secured-loan family)."),
    237: ("YELLOW", "-", "-", "disaster-relief promissory note (niche, not in corpus)",
          "Crisp presence check once the document exists."),
    238: ("YELLOW", "-", "-", "retirement account statement (not in corpus)",
          "Same retirement family as G249/G251/G252/G254-257."),
    240: ("YELLOW", "-", "-",
          "financed-property count + reserve-months fields (not modeled — no REO-schedule entity today)",
          "Crisp math once a financed-properties schedule is parsed from the 1003; this "
          "pilot's extractor doesn't yet treat the 1003's REO section as its own entity."),
    241: ("YELLOW", "-", "-", "same financed-property-schedule gap as G240",
          "Same family as G240 (7-10 property tier)."),
    243: ("YELLOW", "-", "-", "LPA reserve-requirement field (AUS-family, not in corpus)",
          "Same AUS-submission gap as G179 (Freddie's LPA, not Fannie's DU)."),
    244: ("YELLOW", "-", "-", "AUS/TOTAL Scorecard findings (FHA's AUS, not in corpus)",
          "Same AUS-submission gap as G037/G039/G095/G179/G243."),
    246: ("YELLOW", "-", "-", "PITI + reserve-months fields (deepen extraction)",
          "Same reserves family as G057/G247/G248; crisp math once fields exist."),
    247: ("YELLOW", "-", "-", "same PITI-reserves gap as G246",
          "Same family as G246 (ADU-rental-income variant)."),
    248: ("YELLOW", "-", "-", "same PITI-reserves gap as G246",
          "Same family as G246 (3-4 unit variant)."),
    249: ("YELLOW", "-", "-", "retirement-plan vesting-schedule doc (not in corpus)",
          "Same retirement family as G238."),
    251: ("YELLOW", "-", "-", "same retirement-account-statement gap as G238",
          "Same family as G238."),
    252: ("YELLOW", "-", "-", "retirement-account value + outstanding-loan fields (60% threshold)",
          "Crisp threshold math once fields exist; same retirement family as G238."),
    254: ("YELLOW", "-", "-", "same retirement-account gap as G238 (20% threshold)",
          "Same family as G238."),
    255: ("YELLOW", "-", "-", "retirement vesting/withdrawal-evidence field",
          "Same retirement family as G238/G249."),
    256: ("YELLOW", "-", "-", "retirement-account VOD (doc-presence-style, doc type absent from corpus)",
          "Same VOD family as G097/G105/G286, retirement-specific."),
    257: ("YELLOW", "-", "-", "same retirement-VOD gap as G256",
          "Same family as G256 (2-month standard-doc variant)."),
    260: ("YELLOW", "-", "-", "independent valuation doc for a sold personal asset (not in corpus)",
          "The 50%-of-income comparison reuses base_monthly_income_1003 (already "
          "extracted), but the independent-valuation requirement is a genuinely separate, "
          "absent fixture — not a blind extension of LargeDepositShape."),
    261: ("YELLOW", "-", "-", "title/ownership + bill-of-sale doc (not in corpus)",
          "Same personal-property-sale family as G173/G185/G186/G195."),
    262: ("YELLOW", "-", "-", "brokerage/trust statement (not in corpus)",
          "Same stocks/bonds/trust family as G144/G175/G214/G273/G275/G281/G283."),
    263: ("YELLOW", "-", "-", "bridge loan documentation (not in corpus)",
          "Same bridge-loan family as G047/G049/G198."),
    265: ("RED", "-", "open-ended 'all re-subordination requirements were not met'", "-",
          "As worded, a bare catch-all with zero specifics — same pattern as G018/G023/G196, "
          "even though 're-subordination' names a definable process an SME could later "
          "decompose."),
    266: ("YELLOW", "-", "'met HUD's criteria' compliance judgment", "family loan note (not in corpus)",
          "Presence is crisp; full HUD-criteria compliance stays partly human."),
    267: ("YELLOW", "-", "-", "nonprofit second-mortgage note (not in corpus)",
          "Same secondary-financing family as G007/G198/G236/G268-271."),
    268: ("YELLOW", "-", "-", "same nonprofit secondary-financing gap as G267",
          "Same family as G267."),
    269: ("YELLOW", "-", "'policy exception' approval judgment", "policy-exception approval doc (not in corpus)",
          "Presence of an approval record is crisp; whether an exception was properly "
          "granted stays partly human."),
    270: ("YELLOW", "-", "-", "subordination agreement / recorded mortgage doc (not in corpus)",
          "Same secondary-financing family as G267/G269/G271."),
    271: ("YELLOW", "-", "'unacceptable' terms determination", "subordinate-financing terms field",
          "Terms-presence is crisp; acceptability against guide stays human."),
    273: ("YELLOW", "-", "-", "stock/bond certificate (not in corpus)",
          "Same stocks/bonds family as G144/G175/G262/G275/G281/G283."),
    275: ("YELLOW", "-", "-", "same stock/bond statement gap as G273",
          "Same family as G273."),
    278: ("YELLOW", "-", "'unallowable transaction' / 'eligibility requirements' judgment",
          "sweat-equity documentation (not in corpus)",
          "Same family as G219; documentation presence is crisp, transaction-type "
          "eligibility stays partly human."),
    279: ("YELLOW", "-", "-", "same trade-equity documentation gap as G204/G220/G221",
          "Same family as G220."),
    281: ("YELLOW", "-", "-", "trust fund receipt evidence (not in corpus)",
          "Same trust family as G197/G214/G283."),
    283: ("YELLOW", "-", "-", "trust agreement/trustee statement (not in corpus)",
          "Same trust family as G197/G214/G281."),
    284: ("YELLOW", "-", "-", "citizenship/foreign-national documentation (not in corpus)",
          "Related to the large-deposit family, but citizenship data isn't modeled at "
          "all — a genuinely separate, absent fixture."),
    286: ("YELLOW", "-", "-", "VOD form (not in corpus)",
          "Same VOD family as G001/G002/G097/G105/G256/G257."),
    289: ("YELLOW", "-", "-", "account-identifying-information field (deepen bank_statement FIELD_SPECS)",
          "bank_statement doc is already parsed for every loan that has one; a distinct "
          "account-number/identifying-info field is a plausible near-term Bucket-B win, "
          "not implemented here."),
    292: ("YELLOW", "-", "-", "custodial account (UTMA/UGMA) statement (not in corpus)",
          "Crisp eligibility check once the document exists."),
    295: ("YELLOW", "-", "donor-acceptability guideline judgment", "donor-relationship field (deepen gift_letter)",
          "Same donor-acceptability family as G110/G119/G133/G142 (VA wording variant)."),
    296: ("YELLOW", "-", "-", "transfer-method field, same gift-transfer family as G108/G127/G131",
          "Worth SME review before wiring to gift_transfer_evidence_in_file (same caution "
          "as G108/G127/G131)."),
}


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

    # Fresh block, no prior discard/remap has happened (unlike application-
    # verification's decision-016 NMLS removal) — group count must equal rule
    # count exactly minus nothing.
    if len(groups) != 297:
        raise SystemExit("Expected 297 unique groups for a fresh compile of %d rules; "
                         "got %d. Ruleset changed — re-review before trusting this "
                         "triage." % (len(rules), len(groups)))

    out_groups, group_counter, rule_counter = [], Counter(), Counter()
    for gid, ((q, resp), members) in enumerate(groups.items(), 1):
        agencies = sorted({m["agency"] for m in members})
        ecs = sorted({m["eval_class"] for m in members})
        blocked_on_fixture = any(m["eval_class"] == "blocked_on_missing_fixture"
                                for m in members)

        if gid in NOT_A_CHECK_OVERRIDES:
            bin_, machine, human, needs, rationale = (
                "NOT_A_CHECK", "-", "-", "-",
                "Screening/applicability answer branch ('the loan program did not "
                "require assets to qualify'), not a defect condition — same pattern "
                "as application-verification's LEP-applicability screening group.")
        elif PASS_RE.match(resp.strip()):
            bin_, machine, human, needs, rationale = (
                "NOT_A_CHECK", "-", "-", "-",
                "Pass/N-A answer option, not a defect condition.")
        elif ecs == ["mapped"]:
            names = sorted({m["eval_target"] for m in members})
            bin_, machine, human, needs, rationale = (
                "GREEN", "already-mapped SHACL shape: %s" % ", ".join(names), "-", "-",
                "ALREADY BUILT: %s (see blocks/assets.ttl)." % ", ".join(names))
        elif ecs == ["doc_presence"]:
            targets = sorted({m["eval_target"] for m in members})
            bin_, machine, human, needs, rationale = (
                "GREEN", "auto-compiled doc-presence check on: %s" % ", ".join(targets),
                "-", "-",
                "Auto-compiled by amq_compiler.py's doc_presence classifier (the exception "
                "text matches 'not in file/missing/not provided' and names a mappable "
                "document type already in the extraction contract) — already works.")
        else:
            if gid not in C:
                raise SystemExit("Group %d has no classification in C and is not "
                                 "mechanically resolvable — triage incomplete." % gid)
            bin_, machine, human, needs, rationale = C[gid]

        if blocked_on_fixture and bin_ not in ("NOT_A_CHECK", "GREEN"):
            bin_ = "YELLOW"
            rationale = ("BLOCKED ON MISSING FIXTURE (decision 014 principle), not a "
                        "rule-clarity problem: " + rationale)

        fnm_or_generic = any(a in ("O-FNM", "GENERIC") for a in agencies)
        topics = (retrieve_topics(sg, q + " " + resp)
                  if fnm_or_generic and bin_ != "NOT_A_CHECK" else [])
        source_rows = sorted({n for m in members for n in m.get("source_rows", [])})

        g = {"group": gid, "question": q, "condition": resp,
             "agencies": agencies,
             "severities": sorted({m["severity"] for m in members if m["severity"]}),
             "codes": sorted({m["exception_code"] for m in members}),
             "source_spreadsheet": source_csv,
             "source_rows": source_rows,
             "rule_count": len(members), "bin": bin_,
             "blocked_on_missing_fixture": blocked_on_fixture,
             "machine_checkable": machine, "stays_human": human,
             "needed_data": needs, "rationale": rationale,
             "ready_to_build": READY_TO_BUILD.get(gid),
             "guide_candidates": topics,
             "sme_status": "PENDING REVIEW"}
        out_groups.append(g)
        group_counter[bin_] += 1
        rule_counter[bin_] += len(members)

    result = {"block": BLOCK, "rules_total": len(rules),
              "unique_groups": len(groups),
              "bins_by_group": dict(group_counter),
              "bins_by_rule": dict(rule_counter),
              "classifier": "Claude (compile-time analyst), session 2026-07-30 — PENDING SME REVIEW",
              "groups": out_groups}
    with open(OUT_JSON, "w") as f:
        json.dump(result, f, indent=1, sort_keys=True)

    # ------------------------------------------------------------ SME packet
    lines = ["# SME Review Packet — asset-verification block triage",
             "",
             "**%d rules / %d unique (question, condition) groups.** Every classification"
             % (len(rules), len(groups)),
             "below is a *proposal* pending your review — mark each check agree / correct.",
             "Bins: GREEN = automatable now · YELLOW = automatable after data/guide work ·",
             "RED = stays human · NOT_A_CHECK = pass/N-A answer option, not a defect rule.",
             "",
             "**Source workbook:** `%s` — row numbers below are Excel-style" % source_csv,
             "(header = row 1), so you can open the sheet and jump straight to each rule.",
             "",
             "**Note on this block vs application-verification:** dedup collapse here is "
             "far smaller (304 rules -> 297 groups, ~1.02x, vs 81->54, ~1.5x) — the 5 AMQ "
             "agencies write almost entirely independent condition text per asset sub-type. "
             "GREEN/NOT_A_CHECK for the ~87 mechanically-resolvable groups are derived "
             "directly from amq_compiler.py's own eval_class and a pass/N-A regex, not "
             "hand-typed; the ~210 substantive groups below are individually read and "
             "classified.",
             ""]
    defect_groups = [g for g in out_groups if g["bin"] != "NOT_A_CHECK"]
    ng = len(defect_groups)
    lines.append("## Headline")
    lines.append("")
    lines.append("| Bin | Groups | Rules | % of defect groups |")
    lines.append("|---|---|---|---|")
    for b in ("GREEN", "YELLOW", "RED"):
        gc = group_counter[b]
        lines.append("| %s | %d | %d | %d%% |" % (b, gc, rule_counter[b],
                                                  round(100.0 * gc / ng)))
    lines.append("| NOT_A_CHECK | %d | %d | — |"
                 % (group_counter["NOT_A_CHECK"], rule_counter["NOT_A_CHECK"]))
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
    print("Packet: %s" % os.path.relpath(OUT_MD, HERE))


if __name__ == "__main__":
    main()
