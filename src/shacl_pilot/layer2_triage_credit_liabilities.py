#!/usr/bin/env python3
"""
Layer-2 triage — credit-liabilities-review block (386 rules, 382 unique groups).

Same method and GREEN/YELLOW/RED/NOT_A_CHECK definitions as layer2_triage.py
(application-verification) and layer2_triage_assets.py (asset-verification) —
read those module docstrings first. This is the third block triaged this way.

Structural notes, all verified empirically before assuming them (same discipline
as the asset-verification script):

1. Dedup barely collapses: 386 rules -> 382 unique (question, condition) groups
   (~1.01x) — even less collapse than asset-verification's 304->297 (~1.02x).
   The 5 AMQ agencies write almost entirely independent condition text per
   credit/liability sub-topic (AUS-specific variants, RMCR-specific variants,
   manual-UW variants, ...).

2. Unlike asset-verification, `amq_compiler.py`'s MAPPED_SHAPES has TWO shapes
   already wired to this block (`UndisclosedLiabilityShape`, `CashoutMortgageLateShape`)
   but BOTH are wired to zero `amq_exception_codes` (the same bug pattern
   decisions 017/018 found and partly fixed for LargeDepositShape/GiftEvidenceShape)
   -- so `ruleset.json` shows literally zero rules with eval_class "mapped" for
   this block; every rule is "unmapped" or "doc_presence". This triage
   deliberately went looking for an AMQ row each shape could be wired to (the
   decision-018 discipline) -- see decision 019 for the verdict: NEITHER
   shape found a safe match. Every textually-close "undisclosed debt" row
   bundles an extra requirement (borrower explanation obtained, DTI
   resubmission, GUS re-entry) our shape doesn't test, and no row anywhere in
   the ingested Post-Closing sheet states CashoutMortgageLateShape's exact
   "cash-out refi + 0x30 late in mortgage payment history, prior 12 months"
   condition for Freddie Mac. Flagged, not force-wired.

3. Given ~382 groups, NOT_A_CHECK/GREEN for the mechanically-resolvable slice
   are derived from data amq_compiler.py already computes (pass/N-A regex,
   `eval_class == "doc_presence"`), plus two explicit overrides this triage
   found by hand:
     - 3 screening/applicability answer branches (empty exception_code,
       "the loan program did not require a credit report to qualify" x2 +
       one special-credit-considerations routing answer) -- same pattern as
       application-verification's group 10 and asset-verification's group 291.
     - 5 "There are no credit report(s) in the file" rows that are functionally
       identical to amq_compiler.py's own doc_presence auto-compile logic but
       are NOT caught by its `NOT_IN_FILE_RE` regex (which requires the literal
       substring "not in file"/"not provided"/"missing" -- "there ARE NO
       credit report(s) in the file" doesn't match that pattern). Classified
       GREEN here (the underlying fact, docs_present.get("credit_report"), is
       already extractable) with the regex gap flagged as a finding for a
       human to patch in amq_compiler.py -- NOT patched here (out of scope:
       don't touch amq_compiler.py).
   The remaining ~273 substantive groups are read individually and classified
   by family below, in the same rigor as the reference scripts' `C` dicts.

4. Headline finding (see decision 019 for the full writeup): this block skews
   even more heavily YELLOW than asset-verification, and for a similar root
   cause -- the "Credit - Liabilities" AMQ category spans dozens of
   sub-topics (RMCR-format compliance, AUS/DU/LPA/TOTAL/GUS feedback-
   certificate specifics, IRS installment agreements, consumer credit
   counseling, non-traditional credit/VOR, mortgage forbearance/modification,
   federal debt, community-property non-borrowing-spouse credit, bankruptcy/
   foreclosure/short-sale/judgment/collections/disputed-account history) and
   the 5-loan synthetic corpus contains exactly ONE credit report (loan 01),
   showing clean current tradelines and "None reported" for Public Records /
   Collections / Derogatory. Every "adverse/derogatory credit" AMQ row in this
   block is fixture-blocked not because the condition is unclear, but because
   no synthetic loan in this corpus HAS derogatory credit to check against.
"""
import json
import os
import re
from collections import OrderedDict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
RULESET = os.path.join(HERE, "compiled", "ruleset.json")
SG_INDEX = os.path.join(HERE, "compiled", "selling_guide_index.json")
OUT_JSON = os.path.join(HERE, "compiled", "triage_credit-liabilities-review.json")
OUT_MD = os.path.join(HERE, "out", "TRIAGE-PACKET-credit-liabilities-review.md")

BLOCK = "credit-liabilities-review"

PASS_RE = re.compile(r"^(Yes,|Not Applicable)", re.I)

# Screening/applicability answer branches with an EMPTY exception_code (same
# signal application-verification's group 10 and asset-verification's group
# 291 used) -- not a defect condition, a routing/screening answer.
NOT_A_CHECK_OVERRIDE_RESPONSES = {
    "the loan program did not require a credit report to qualify",
    "alimony, child support, and maintenance debt",
}

# "There are no credit report(s) in the file" / "No, there are no credit
# report(s) in the file" -- functionally identical to amq_compiler.py's own
# doc_presence auto-compile (checkable via docs_present.get("credit_report")),
# but NOT caught by its NOT_IN_FILE_RE regex (needs literal "not in file" /
# "not provided" / "missing"; "there ARE NO ... in the file" doesn't match).
# Flagged as a regex-coverage gap for amq_compiler.py -- not patched here.
GREEN_CREDIT_REPORT_PRESENCE_RE = re.compile(r"no credit report\(s\) in the file", re.I)

# ---------------------------------------------------------------------------
# CRITICAL FINDING (decision 019): amq_compiler.py's mechanical doc_presence
# classifier (NOT_IN_FILE_RE match + a DOC_KEYWORDS "credit report" hit) is a
# FALSE-POSITIVE trap for this block. Of the 24 rules its own `classify_eval`
# tags eval_class=="doc_presence" here, only 5 are genuinely "is a credit
# report present for this applicant" checks. The other 19 are compound
# conditions where "credit report" appears merely as the SOURCE the defect
# is read off of (a business debt, a disputed account, a payment-history
# depth, a 24-month residency history, ...) -- NOT a presence fact at all.
# Verified against the full exception_description text for every one of the
# 24 (not assumed from the response_text alone), per the decision-018
# discipline: an agent's/script's confident-looking mechanical classification
# is a lead to verify, never a result to wire directly. Wiring these 19 as
# auto-GREEN "already works" would silently PASS any loan that merely HAS a
# credit_report document in its folder, regardless of whether the loan's
# real defect (undocumented business debt, unresolved disputed account,
# missing 12-month payment history, ...) is present -- a false-clear on a
# genuine defect, exactly what Non-Negotiable #1 (determinism + correctness)
# warns against. NOT fixed in amq_compiler.py (off-limits for this exercise)
# -- this triage instead re-derives the correct bin for all 24 by hand and
# flags the bug prominently in decision 019 for a human to patch.
DOC_PRESENCE_VERIFIED_GREEN = {
    "O-FHA-02220", "O-FNM-00179", "O-FRD-00144", "O-RHS-02788", "O-VA-00118",
}
DOC_PRESENCE_MISCLASSIFIED = {
    "O-FNM-50004": ("YELLOW",
        "MISCLASSIFIED by amq_compiler.py's mechanical doc_presence rule (matched 'in "
        "excess' + 'credit report' keyword) -- the real condition is asset-sufficiency "
        "to cover a flagged 30-day account beyond reserves/closing funds, not credit-"
        "report presence. Needs a cross-reference of the flagged tradeline balance "
        "against total available assets (bank_txns) and reserve/closing-cost fields -- "
        "not yet derived anywhere in extract_loan.py."),
    "O-FNM-50006": ("YELLOW",
        "MISCLASSIFIED (matched 'not included'/'not documented' + 'credit report' "
        "keyword) -- the real condition is whether a business debt on the personal "
        "credit report is documented as company-paid and excluded from DTI accordingly. "
        "Needs a business-debt-payment documentation type this corpus doesn't have, plus "
        "DTI-inclusion logic not yet built."),
    "O-FRD-50021": ("YELLOW",
        "Same business-debt-in-DTI family as O-FNM-50006 (FRD wording variant) -- "
        "MISCLASSIFIED by the same mechanical doc_presence false-positive."),
    "O-FHA-02242": ("YELLOW",
        "Same business-debt-in-DTI family as O-FNM-50006 (FHA wording variant, adds a "
        "self-employment/cash-flow-analysis angle) -- MISCLASSIFIED by the same "
        "mechanical doc_presence false-positive."),
    "O-FRD-00149": ("YELLOW",
        "MISCLASSIFIED (matched 'did not confirm' + 'credit report' keyword) -- the real "
        "condition is whether the credit report documents that the reporting agency "
        "attempted employment/income verification, an RMCR-format field this pilot's "
        "synthetic credit report doesn't model at all."),
    "O-FRD-00155": ("YELLOW",
        "MISCLASSIFIED (matched 'not reflected' + 'credit report' keyword) -- same RMCR-"
        "format-field family as O-FRD-00149; 'responsive verification statements' aren't "
        "modeled in this corpus's credit report."),
    "O-FNM-00200": ("RED",
        "MISCLASSIFIED (matched 'not provided' + 'credit report' keyword). Verified: this "
        "is the byte-for-byte-identical FNM wording variant of O-VA-00143 (group 201 "
        "below), which this triage independently classified RED for 'satisfactory credit "
        "risk' being a holistic underwriter judgment -- a clean demonstration of the bug: "
        "the exact same real-world condition got auto-GREENed here purely because "
        "amq_compiler.py's regex happened to fire, and correctly hand-classified RED "
        "there because it didn't."),
    "O-FNM-50010": ("YELLOW",
        "MISCLASSIFIED (matched 'not documented' + 'credit report' keyword) -- the real "
        "condition needs DU's own disputed-account message/resolution record, part of the "
        "same AUS-feedback-certificate gap as the F_AUS_EXPORT family (no DU export doc "
        "exists in this corpus)."),
    "O-FNM-00182": ("YELLOW",
        "MISCLASSIFIED (matched 'not in the file' + 'credit report' keyword) -- Bucket-B-"
        "close, not a bare presence check: loan 01's synthetic credit report IS explicitly "
        "titled 'Tri-Merge Credit Report Summary — Bureaus: Equifax / Experian / "
        "TransUnion,' so the underlying fact may already be true in text, but no "
        "is_tri_merge / bureau-count field is parsed by FIELD_SPECS today -- needs "
        "extraction, not just a presence flag."),
    "O-FNM-50245": ("YELLOW",
        "MISCLASSIFIED (matched 'not supported' + 'credit report' keyword) -- the real "
        "condition needs a credit-supplement/dispute-resolution document family, same as "
        "the F_DEROG_HISTORY YELLOW family elsewhere in this block, not in this corpus."),
    "O-FRD-50023": ("YELLOW",
        "MISCLASSIFIED (matched 'not report' + 'credit report' keyword) -- needs a "
        "deferred/forbearance status flag per tradeline and a separate payment-"
        "verification document; `extract_tradelines()` doesn't model either today."),
    "O-FHA-50015": ("YELLOW",
        "MISCLASSIFIED (matched 'not adequately document' + 'credit report' keyword) -- "
        "the real condition needs an explanation-of-delinquency document establishing "
        "extenuating circumstances, a doc type this corpus doesn't have; presence of such "
        "a letter would be crisp once it exists, 'adequately' stays a partial human check."),
    "O-FHA-02222": ("YELLOW",
        "MISCLASSIFIED (matched 'did not meet' + 'credit report' keyword) -- same non-"
        "traditional-credit-report family as F_NONTRAD_VOR elsewhere in this block, not a "
        "bare presence check."),
    "O-FRD-00174": ("YELLOW",
        "MISCLASSIFIED (matched 'is missing' + 'credit report' keyword) -- the real "
        "condition is the REVERSE direction of UndisclosedLiabilityShape (a 1003 debt "
        "missing from the credit report, needing a separate written verification "
        "document), same family as F_APPLICATION_DEBT_NOT_ON_CREDIT elsewhere in this "
        "block -- not itself a credit-report-presence fact."),
    "O-RHS-50563": ("YELLOW",
        "MISCLASSIFIED (matched 'was not provided'/'not added' + 'credit report' keyword) "
        "-- same direction as UndisclosedLiabilityShape's real condition (credit report "
        "shows a debt the 1003 doesn't), but bundles an extra explanation/DTI-inclusion "
        "requirement our shape doesn't test -- same caution as the F_UNDISCLOSED_DEBT "
        "family and decision 019's verdict on that shape."),
    "O-FNM-00195": ("YELLOW",
        "MISCLASSIFIED (matched 'does not provide' + 'credit report' keyword) -- needs "
        "12 months of month-by-month mortgage payment history; `extract_tradelines()` "
        "captures only a single current-status snapshot, same gap as F_PAYMENT_HISTORY_DEPTH."),
    "O-RHS-02826": ("YELLOW",
        "MISCLASSIFIED (matched 'was not' + 'credit report' keyword) -- same direction as "
        "UndisclosedLiabilityShape's real condition plus a borrower-explanation "
        "requirement, same family/caution as O-RHS-50563 above."),
    "O-VA-00124": ("YELLOW",
        "MISCLASSIFIED (matched 'was not provided' + 'credit report' keyword) -- needs an "
        "RMCR-specific 24-month residency-history field, same F_RMCR_FORMAT family "
        "elsewhere in this block, not a bare presence check."),
    "O-VA-00131": ("YELLOW",
        "MISCLASSIFIED (matched 'is not reported' + 'credit report' keyword) -- same "
        "reverse-direction family as O-FRD-00174 (F_APPLICATION_DEBT_NOT_ON_CREDIT), not "
        "a credit-report-presence fact."),
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
# RED: irreducible human-judgment conditions (true regardless of whether more
# fixtures existed -- "reasonable"/"significant"/"satisfactory"/open-ended
# catch-all wording dominates the condition, same standard applied throughout
# application-verification's and asset-verification's RED calls).
RED_FAMILIES = [
    (r"reasonable steps|reasonably confirm",
     "FCRA identity-theft/active-duty/fraud-alert phone verification ('reasonable steps') "
     "has no bright-line test, and no alert flag exists anywhere in this corpus's one "
     "credit report (loan 01) regardless."),
    (r"perform(ed)? an analysis and determin|analysis determining (the )?significance|"
     r"determine.{0,15}significan|significance of (the )?(adverse|derogatory)",
     "Whether a derogatory/adverse event is 'significant' is an underwriter judgment call, "
     "not a bright-line test -- same class as prior REDs on significance/reasonableness "
     "determinations (application-verification G7/G11/G23, asset-verification G012/G053)."),
    (r"not due to extenuating circumstances|explanation of extenuating circumstances",
     "'Extenuating circumstances' is inherently a narrative/judgment determination, same "
     "class as asset-verification's narrative-adequacy REDs (G012/G193)."),
    (r"unacceptable payment history as per review|satisfactory credit risk",
     "Holistic 'satisfactory credit risk'/'acceptable payment history' determination -- an "
     "underwriter judgment call across the whole file, not a single checkable fact."),
    (r"all debts required to be paid.{0,10}were not satisfied|"
     r"all debts were not (paid off|paid of) at or prior to closing",
     "Open-ended sweep across whatever debts were separately flagged 'required to be paid "
     "at closing' -- no single named debt or threshold stated; needs SME decomposition into "
     "the specific debts before any one fact is checkable, same pattern as application-"
     "verification's 'all disclosures per guidelines' and asset-verification's bare "
     "'all requirements ... not met' catch-alls (G018/G023/G196/G265)."),
]

# ---------------------------------------------------------------------------
# YELLOW families: crisp-once-the-data-exists conditions, blocked on fixtures
# genuinely absent from demo/syn/loan 01..05 (this corpus's ONE credit report,
# loan 01, shows clean current tradelines and "None reported" derogatory/
# public-records -- every adverse-credit family below is blocked for that
# reason, not because the condition is unclear), or needing derived facts
# (PITIA/DTI) this pilot doesn't yet compute. (regex, needed_data, rationale)
YELLOW_FAMILIES = [
    ("F_AUS_EXPORT",
     r"loan product advisor|feedback certificate|\blpa\b|desktop underwrit|entered into gus|"
     r"not resubmitted|not re-?submitted|1008/1077|rescored in total|"
     r"not manually downgraded|not downgraded to a refer|not downgraded to refer|"
     r"caution range|pattern of high balance|reason codes|data entered into du|"
     r"resubmission requirements|not in total w/|days of the aus report|aus refer",
     "DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log "
     "export -- no such document exists as a doc type in this pilot for any agency; RHS's "
     "GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a "
     "downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-"
     "verification triage (decision 017, G037/G039/G095/G179/G243/G244)."),
    ("F_DEROG_HISTORY",
     r"bankrupt|foreclosure|deed[- ]in[- ]lieu|short sale|pre-?foreclosure|collection|"
     r"judg[e]?ment|disputed (derogatory|account)|tax lien|charge[- ]off|"
     r"mitigating circumstances|credit exception|usda loss|derogatory credit|"
     r"derogatory accounts|adverse.{0,3}or.{0,3}derogatory",
     "Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/"
     "judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's "
     "ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/"
     "Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity "
     "problem; the synthetic fixtures simply never modeled adverse credit."),
    ("F_RMCR_FORMAT",
     r"repositor|rmcr|residential mortgage credit report|altered|not an original|"
     r"erasures|whiteouts|reporting status|checked with the creditor within|public record|"
     r"identifying info|manual credit report did not meet|updated with the creditor within|"
     r"required credit information for each debt",
     "Needs RMCR-specific compliance fields (repository count, per-account 'last updated' "
     "aging, original-vs-altered flag, identifying-info accuracy, public-records "
     "completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/"
     "balance/monthly_payment/status; none of these format/compliance attributes are "
     "parsed, and the synthetic credit report's own text doesn't model them either."),
    ("F_IRS_INSTALLMENT",
     r"irs installment|notice of federal tax lien|internal revenue service",
     "IRS installment-agreement document (payment terms/balance/lien notice) -- not a doc "
     "type in this corpus."),
    ("F_CREDIT_COUNSELING",
     r"credit counseling",
     "Consumer credit counseling program enrollment/payout/agency-approval document -- not "
     "a doc type in this corpus."),
    ("F_NONTRAD_VOR",
     r"non-?traditional|nontraditional|verification of rent|\bvor\b|rental payment history|"
     r"rent(al)? pay(ment)? histor|housing pay history|housing payment history|"
     r"noncredit|allowable documentation to verify pay history|"
     r"minimum trad/non trad credit|acceptable documentation|prior housing history|"
     r"verifications were not obtained for rental",
     "Non-traditional credit report / Verification of Rent (VOR) / noncredit payment "
     "reference documentation -- no such doc type exists in this corpus; every loan's "
     "housing-payment history today comes only from the VOM (loan 04, mortgage-specific, "
     "not rental) or the one credit report's tradelines (loan 01)."),
    ("F_FORBEARANCE",
     r"forbearance|modification plan",
     "Mortgage forbearance/modification-plan document (terms, consecutive-payment count "
     "since granted) -- not a doc type in this corpus."),
    ("F_FEDERAL_DEBT",
     r"federal (non-?tax )?debt|delinquent federal|debt collection improvement act|"
     r"disability benefits.{0,20}search req",
     "Federal debt / delinquent federal (tax or non-tax) obligation documentation "
     "(repayment status, CAIVRS-adjacent) -- not modeled beyond loan 02's CAIVRS/LDP/GSA "
     "screenprint (a different, narrower fact)."),
    ("F_COMMUNITY_PROPERTY",
     r"community property|non-?borrowing spouse|non-purchasing spouse|non-borrowing veteran",
     "A second credit report (the non-borrowing/non-purchasing spouse's) plus the "
     "applicable state's community-property statute reference -- neither exists in this "
     "corpus; every loan extracts exactly one applicant-side credit report at most."),
    ("F_STUDENT_LOAN",
     r"student loan",
     "Student-loan payment-substitution math (0.5%/1% of balance when the credit report "
     "shows a $0 or missing payment) is crisp arithmetic, and `extract_tradelines()` "
     "already captures tradeline type/balance/monthly_payment (loan 01 has one Student "
     "tradeline) -- but verifying which qualifying-payment value the lender ACTUALLY used "
     "needs a DTI/qualifying-payment worksheet this pilot doesn't extract or derive from "
     "any document today. Trigger-detection is Bucket-B-close; the verification half is not."),
    ("F_CONTINGENT_COSIGN_AUTHUSER",
     r"contingent liabilit|co-?signed|authorized user",
     "Needs a 12-month third-party-payment history (contingent-liability co-obligor, "
     "cosigner, or authorized-user account owner) -- `urla_liabilities`/`tradelines` "
     "capture the liability itself but not who else has been paying it or for how long; "
     "no such payment-history document exists in this corpus."),
    ("F_LEASE_HELOC_MISC",
     r"\blease\b|heloc|timeshare|secured by a financial asset|solar panel|virtual currency|"
     r"cryptocurrency",
     "Needs a lease/HELOC/timeshare/solar-panel-agreement/virtual-currency-secured-loan "
     "document -- none of these niche liability-collateral document types exist in this "
     "corpus (same 'document family the synthetic corpus never modeled' pattern as several "
     "asset-verification YELLOW groups)."),
    ("F_PITIA_DTI_REO",
     r"pitia|housing (expense|ratio)|debt-to-income|dti ratio|real estate tax|"
     r"other propert(y|ies) owned|rent.{0,15}(document|includ)|tax abatement|"
     r"special assessment|energy efficien|monthly dti",
     "PITIA/DTI/housing-ratio computation from components already partly extracted "
     "(base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in "
     "extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted "
     "dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a "
     "financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- "
     "same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity)."),
    ("F_ALIMONY",
     r"alimony|child support|maintenance payment|divorce decree",
     "Divorce decree / court order / separation agreement documenting alimony, child "
     "support, or maintenance payment terms -- not a doc type in this corpus."),
    ("F_TAX_LIABILITY",
     r"federal income taxes due on the current year tax return",
     "Current-year tax return + proof-of-payment documentation -- not a doc type in this "
     "corpus (identical condition text recurs across FHA/FRD/RHS/VA/FNM -- a single fixture "
     "gap, not five separate ones)."),
    ("F_PAYSTUB_DEDUCTION",
     r"loan(s)?/?deductions listed on the paystubs|has an allotment without documenting",
     "Verified against the actual synthetic paystub (loan 01, `03_Paystub_Most_Recent.pdf`): "
     "its Deductions section lists only standard tax withholdings (Federal Withholding, "
     "Social Security, Medicare, NC State Tax) -- no loan-type deduction or military "
     "allotment line appears in any paystub in this corpus. Genuine Bucket-A-style fixture "
     "gap (the paystub doc type exists; the specific line item this rule needs does not), "
     "not a Bucket-B extraction-deepening candidate -- there is nothing yet to extract."),
    ("F_HAWK_ALERT",
     r"hawk alert|credit alert",
     "Hawk Alert / Other Credit Alert flag -- this attribute doesn't appear anywhere in the "
     "one synthetic credit report's text; not modeled, not merely unextracted."),
    ("F_CREDIT_SCORE",
     r"credit score|fico score",
     "Deepen `credit_report` FIELD_SPECS: the doc's own text already shows 'Middle Score — "
     "Borrower 742' / 'Middle Score — Co-Borrower 758' (loan 01) but no score field is "
     "parsed today. Even once parsed, applying these rules needs a per-program minimum-"
     "score / representative-score-selection table that is a Selling-Guide business rule, "
     "not a fact derivable from any loan document -- Bucket-B on the extraction side, still "
     "needs an SME-sourced threshold table beyond that."),
    ("F_UNDISCLOSED_DEBT",
     r"undisclosed (debt|mortgage)",
     "Closest textual match to the already-mapped (but zero-exception-code) "
     "`UndisclosedLiabilityShape` (credit-report tradeline with no matching 1003 Section 2c "
     "liability) -- verified NOT a safe direct wire (decision 019): this row bundles an "
     "additional requirement (borrower explanation obtained, and/or the payment verified "
     "and included in DTI) our shape doesn't test. Wiring it as-is would risk false "
     "negatives on loans where the undisclosed debt is present but the compound condition "
     "isn't met, or false positives once the explanation-documentation piece is added and "
     "our shape can't see it. Kept YELLOW pending that extra logic being built."),
    ("F_FROZEN_CREDIT",
     r"frozen credit",
     "Credit-freeze status is not modeled anywhere in this corpus's credit report."),
    ("F_INQUIRIES",
     r"inquir",
     "Needs a parsed Inquiries table (already visible in the loan 01 credit report's text -- "
     "'Inquiries (last 120 days)' with Date/Bureau/Requesting Party -- but not yet in "
     "FIELD_SPECS/entities) cross-referenced against whether new debt was opened; Bucket-B-"
     "style (deepen extraction of a section already present in the one document we have), "
     "not a missing document."),
    ("F_ERRONEOUS_DU",
     r"erroneous credit|reconcile discrepancies",
     "DU-specific credit-data reconciliation record -- part of the same AUS-export-document "
     "gap as F_AUS_EXPORT (no DU feedback certificate/resubmission log in this corpus)."),
    ("F_TRADELINE_MATH",
     r"revolving (charge )?account|installment (loan|debt)|deferred (obligation|installment)|"
     r"of the balance|charge off|5% of|1\.5%|0\.5%",
     "The percentage-of-balance math (5%/1.5%/0.5% thresholds) is crisp arithmetic once the "
     "relevant balance is in hand, and `extract_tradelines()` already captures type/balance/"
     "monthly_payment per tradeline -- but confirming whether the LENDER actually included "
     "the computed amount in the final DTI needs a DTI worksheet this pilot doesn't derive "
     "(same gap as F_PITIA_DTI_REO); and month-by-month late-payment-in-12-months detection "
     "needs payment-history depth the tradeline snapshot (a single current 'Status' value) "
     "doesn't carry. Trigger data partly in hand; verification math not yet built."),
    ("F_REUNDERWRITE",
     r"updated credit report|re-?underwritten|rescored",
     "Needs a second (updated) credit-report pull to compare against the original, plus a "
     "resubmission/rescoring record -- neither exists for any loan in this corpus (each "
     "loan has at most one credit report snapshot)."),
    ("F_CREDIT_REPORT_AGE",
     r"credit report was expired|credit report was over 120 days old|credit report was more "
     r"than 120 days old",
     "Bucket-B-close: the synthetic credit report's own text already shows 'Report Date "
     "07/29/2025' (loan 01) and `closing_date` is already extracted from the closing "
     "disclosure -- a days-elapsed comparison is crisp arithmetic once `report_date` joins "
     "FIELD_SPECS['credit_report']. Not fully ready: the expiration threshold itself is "
     "agency-specific (RHS states 120 days explicitly; VA's 'expired' needs its own Guide-"
     "cited day count) and needs an SME/guide citation before hardcoding, not just a new field."),
    ("F_MAIL_ONLY_VERIFICATION",
     r"rate by mail only|need written authorization",
     "'Will rate by mail only'/'need written authorization' accounts need a separate written-"
     "verification document per account -- not a doc type this corpus models (the one "
     "credit report's tradelines don't carry a rate-by-mail flag either)."),
    ("F_LATE_PAYMENT_GUIDELINE",
     r"late rental or mortgage payment reported|late rental and/or (mortgage )?payment "
     r"reported|payment history for the most recent 12 months",
     "'Does not meet guidelines' bundles a specific late-payment-count/severity threshold "
     "(defined per agency Selling Guide, not stated in the row itself) with the housing-"
     "payment-history depth this pilot's VOM only captures for one mortgage on one loan "
     "(loan 04) -- needs both a guide-sourced threshold and broader payment-history "
     "extraction; genuinely blocked on both counts, not a rule-clarity problem."),
    ("F_EAH",
     r"employee relocation program|eah benefit",
     "Employer Assisted Homeownership (EAH) benefit agreement -- same document family "
     "asset-verification's triage already flagged as absent from this corpus (G020/G022)."),
    ("F_CREDIT_ASSESSMENT_MISC",
     r"recent, significant increase in open accounts|significant increase in open accounts",
     "Needs tradeline open-date history (to detect a 'recent, significant increase in open "
     "accounts') this pilot doesn't parse, plus an undefined 'significant' threshold -- "
     "kept YELLOW rather than RED because a specific new-account count could ground it "
     "once an SME supplies the number; not purely a judgment call by wording alone."),
    ("F_ADDRESS_ELIGIBILITY",
     r"present address not within the u\.s\.",
     "Needs a borrower current-address country/military-address classification -- "
     "`final_1003` extraction captures identity/employment/loan fields today, not a "
     "structured current-address country flag."),
    ("F_VA_EMPLOYMENT_COSTS",
     r"child care.{0,10}to age 12|significant commutes",
     "VA job-related-expense debt (child care, commute costs) documentation -- not a doc "
     "type or field this corpus's single VA loan (03) models."),
    ("F_PAYOFF_SOURCE_ASSETS",
     r"source/sufficient assets remain for the loan not provided|debt paid off or paid down "
     r"to qualify",
     "Needs a source-of-funds-for-payoff cross-reference against remaining total assets -- "
     "`payoff_amount_1003`/`cash_out_to_borrower_1003` and `bank_txns` exist independently, "
     "but the specific 'paid down solely to qualify, sufficient assets remain' derivation "
     "isn't built; related to asset-verification's net-sale-proceeds family (G004/G005)."),
    ("F_PENDING_SALE",
     r"pending sale after note date|executed sale contract",
     "Executed sales contract for a pending sale of the borrower's current residence -- not "
     "a doc type in this corpus; related to asset-verification's prior-home-sale settlement-"
     "statement family (G004/G005/G033)."),
    ("F_POOLED_SAVINGS_DTI",
     r"private or pooled savings",
     "Pooled/private-savings-plan agreement -- same document family asset-verification's "
     "triage flagged as absent from this corpus (G196/G209 there)."),
    ("F_PAYMENT_HISTORY_DEPTH",
     r"outstanding balance is paid in full for the past 12 months on a 30-day account",
     "Needs 12 months of month-by-month payment history for a specific tradeline -- "
     "`extract_tradelines()` captures only a single current-status snapshot per tradeline "
     "(creditor/type/balance/monthly_payment/status), not a payment-history timeline; only "
     "the VOM (loan 04, one specific mortgage) has that depth in this corpus."),
    ("F_APPLICATION_DEBT_NOT_ON_CREDIT",
     r"debt on the application is not on the credit report|significant open debt\(s\) on the "
     r"application but not on the credit report",
     "The REVERSE direction of `UndisclosedLiabilityShape`'s condition (that shape flags a "
     "credit-report tradeline missing from the 1003; this row flags a 1003 liability "
     "missing from the credit report) -- needs a separate written-verification document per "
     "unreported debt that isn't modeled in this corpus. Noted as textually adjacent to, but "
     "NOT the same real-world check as, the mapped shape -- do not conflate the two "
     "directions when this is eventually built."),
]


def classify_group(q, resp, exc_desc_list):
    resp_l = resp.strip().lower()
    if resp_l in NOT_A_CHECK_OVERRIDE_RESPONSES:
        return ("NOT_A_CHECK", "-", "-", "-",
                "Screening/applicability answer branch (empty exception_code in the source "
                "row), not a defect condition -- same pattern as application-verification's "
                "LEP-applicability group and asset-verification's group 291.")
    if GREEN_CREDIT_REPORT_PRESENCE_RE.search(resp):
        return ("GREEN", "credit_report doc presence via docs_present inventory", "-", "-",
                "Trivially checkable (docs_present.get('credit_report')) -- functionally "
                "identical to amq_compiler.py's own doc_presence auto-compile, but this "
                "exact phrasing ('There are no credit report(s) in the file') isn't caught "
                "by its NOT_IN_FILE_RE regex (requires literal 'not in file'/'not provided'/"
                "'missing'). Flagged as a regex-coverage gap in amq_compiler.py for a human "
                "to patch -- not itself a triage-judgment problem, and not patched here "
                "(amq_compiler.py is off-limits for this exercise).")
    text_qr = (q + " " + resp).lower()
    full = (q + " " + resp + " " + " ".join(exc_desc_list)).lower()
    for pat, rationale in RED_FAMILIES:
        if re.search(pat, resp.lower() + " " + " ".join(exc_desc_list).lower()):
            return ("RED", "-", resp, "-", rationale)
    for _name, pat, rationale in YELLOW_FAMILIES:
        if re.search(pat, full):
            return ("YELLOW", "-", "-", "-", rationale)
    return None


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

    if len(groups) != 382:
        raise SystemExit("Expected 382 unique groups for a fresh compile of %d rules; "
                         "got %d. Ruleset changed -- re-review before trusting this "
                         "triage." % (len(rules), len(groups)))

    out_groups, group_counter, rule_counter = [], Counter(), Counter()
    unclassified = []
    for gid, ((q, resp), members) in enumerate(groups.items(), 1):
        agencies = sorted({m["agency"] for m in members})
        ecs = sorted({m["eval_class"] for m in members})
        exc_desc_list = sorted({m["exception_description"] for m in members if m["exception_description"]})

        codes_here = {m["exception_code"] for m in members}

        if PASS_RE.match(resp.strip()):
            bin_, machine, human, needs, rationale = (
                "NOT_A_CHECK", "-", "-", "-",
                "Pass/N-A answer option, not a defect condition.")
        elif ecs == ["doc_presence"] and codes_here <= DOC_PRESENCE_VERIFIED_GREEN:
            targets = sorted({m["eval_target"] for m in members})
            bin_, machine, human, needs, rationale = (
                "GREEN", "auto-compiled doc-presence check on: %s" % ", ".join(targets),
                "-", "-",
                "Auto-compiled by amq_compiler.py's doc_presence classifier (the exception "
                "text matches 'not in file/missing/not provided' and names a mappable "
                "document type already in the extraction contract) -- already works. "
                "Verified against the full exception_description text (decision-018 "
                "discipline): this IS a genuine 'credit report present for this "
                "applicant' presence fact, unlike 19 of its 24 doc_presence siblings in "
                "this block -- see decision 019's false-GREEN finding.")
        elif ecs == ["doc_presence"] and codes_here & set(DOC_PRESENCE_MISCLASSIFIED):
            code = next(iter(codes_here & set(DOC_PRESENCE_MISCLASSIFIED)))
            bin_override, rationale = DOC_PRESENCE_MISCLASSIFIED[code]
            bin_, machine, human, needs = bin_override, "-", "-", "-"
        else:
            result = classify_group(q, resp, exc_desc_list)
            if result is None:
                unclassified.append(gid)
                continue
            bin_, machine, human, needs, rationale = result

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
             "machine_checkable": machine, "stays_human": human,
             "needed_data": needs, "rationale": rationale,
             "guide_candidates": topics,
             "sme_status": "PENDING REVIEW"}
        out_groups.append(g)
        group_counter[bin_] += 1
        rule_counter[bin_] += len(members)

    if unclassified:
        raise SystemExit("%d groups have no classification: %s -- triage incomplete."
                         % (len(unclassified), unclassified))

    result = {"block": BLOCK, "rules_total": len(rules),
              "unique_groups": len(groups),
              "bins_by_group": dict(group_counter),
              "bins_by_rule": dict(rule_counter),
              "classifier": "Claude (compile-time analyst), session 2026-07-30 -- PENDING SME REVIEW",
              "groups": out_groups}
    with open(OUT_JSON, "w") as f:
        json.dump(result, f, indent=1, sort_keys=True)

    # ------------------------------------------------------------ SME packet
    lines = ["# SME Review Packet — credit-liabilities-review block triage",
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
             "**Note on this block vs the other two:** dedup collapse is even smaller here "
             "(386 rules -> 382 groups, ~1.01x) than asset-verification's 304->297 (~1.02x) "
             "or application-verification's 81->54 (~1.5x). Two shapes are already mapped to "
             "this block (`UndisclosedLiabilityShape`, `CashoutMortgageLateShape`) but BOTH "
             "are wired to zero AMQ exception codes — this triage went looking for a real "
             "row each could safely extend (the decision-018 discipline) and found none that "
             "survives verification; see decision 019 for the full writeup of what was "
             "checked and rejected, and why.",
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
