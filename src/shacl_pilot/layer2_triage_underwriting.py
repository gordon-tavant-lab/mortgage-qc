#!/usr/bin/env python3
"""
Layer-2 triage — underwriting-review block (466 rules, 461 unique groups).

Same method and bin definitions as layer2_triage.py (application-verification,
81->54) and layer2_triage_assets.py (asset-verification, 304->297). Read the
module docstring in layer2_triage.py for the GREEN/YELLOW/RED/NOT_A_CHECK
definitions; they are unchanged here.

Why this script looks different from both predecessors: underwriting-review's
461 groups collapse almost not at all from 466 rules (~1.01x, even less than
asset-verification's ~1.02x) AND unlike asset-verification (~87 of 297 groups
mechanically resolved via amq_compiler.py's own eval_class), amq_compiler.py's
MAPPED_SHAPES has literally TWO shapes registered against this block
(ResidualIncomeShape, RatioWaiverShape) but wires ZERO exception codes to
either -- the same "shape exists, never connected" bug already fixed for
GiftEvidenceShape/LargeDepositShape in decisions 017/018. That means only 6 of
461 groups are mechanically GREEN (doc_presence), and hand-classifying the
remaining ~366 one-at-a-time (as layer2_triage.py did for a 54-group block) is
not tractable at this scale. Instead, the ~366 substantive groups are
classified via a FAMILY-regex engine below: every regex was built AFTER
reading the full, untruncated question/response/exception text of all 461
groups (not guessed from truncated previews -- see decision 018's lesson),
grouping them by the real underlying data/document gap they share. A small
OVERRIDES dict hand-corrects the ~14 groups the family engine couldn't cleanly
place (compound conditions, one-off phrasing, a non-breaking-space encoding
quirk in the source CSV). Every family's `needed_data` names the actual
missing form/field/derivation, grounded in what extract_loan.py verifiably
does and does not extract today (checked by grep, not assumed -- see the
credit_score_threshold family's note correcting a claim in this task's own
briefing that turned out to be wrong).

Outputs:
  compiled/triage_underwriting-review.json
  out/TRIAGE-PACKET-underwriting-review.md
"""
import json
import os
import re
from collections import OrderedDict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
RULESET = os.path.join(HERE, "compiled", "ruleset.json")
SG_INDEX = os.path.join(HERE, "compiled", "selling_guide_index.json")
OUT_JSON = os.path.join(HERE, "compiled", "triage_underwriting-review.json")
OUT_MD = os.path.join(HERE, "out", "TRIAGE-PACKET-underwriting-review.md")

BLOCK = "underwriting-review"

PASS_RE = re.compile(r"^(Yes,|Not Applicable)", re.I)

# ---------------------------------------------------------------------------
# Two existing MAPPED_SHAPES entries for this block, both wired to ZERO
# amq_exception_codes today (amq_compiler.py lines 110-111) -- same
# never-connected-shape bug as GiftEvidenceShape/LargeDepositShape before
# decisions 017/018. Investigated as part of this triage (task instruction):
# does ANY of the 461 groups here describe the exact same real-world condition
# these shapes already check? Verified NOT, for both -- see decision 022 for
# the full reasoning. Recorded here so the "0 wired" fact is never silently
# re-derived as a bug when it is actually a verified, deliberate non-wiring.
RESIDUAL_INCOME_REJECTED_CANDIDATES = ["G289 (O-VA-00655)"]
RATIO_WAIVER_REJECTED_CANDIDATES = ["G106 (O-RHS-02848, PITI 34% ceiling)",
                                    "G350 (O-FHA-00606, comp factors not noted on 92900-LT)",
                                    "G343 (O-RHS-02852, manual UW front-ratio 29%)"]

# ---------------------------------------------------------------------------
# Hand overrides for the ~14 groups the family-regex engine below could not
# cleanly place (compound crisp+judgment conditions, one-off phrasing, or a
# non-breaking-space encoding quirk in the source CSV that silently defeated
# a regex until traced down explicitly -- see residency_status_1003's note).
# Fields match the family-tuple shape: (bin, machine, human, needed, rationale).
OVERRIDES = {
    15: ("RED", "-", "open-ended 'guidelines/overlays not met' catch-all", "-",
         "Bare catch-all restating the umbrella question in the negative with zero named "
         "specifics -- same pattern as application-verification's 'all disclosures per "
         "guidelines' RED."),
    23: ("YELLOW", "-", "-",
         "prior-acquisition/resale date fields (seller's acquisition date vs resale date) -- "
         "not modeled; no purchase-contract or prior-deed document exists in the corpus",
         "FHA property-flipping family (91-180-day resale window); same missing-purchase-"
         "contract gap flagged in asset-verification's EMD family (decision 017)."),
    24: ("YELLOW", "-", "-",
         "seller-of-record / property-flipping documentation -- not modeled",
         "Same FHA property-flipping family as G023/G027."),
    27: ("YELLOW", "-", "-",
         "seller's acquisition date vs resale date (90-day window) -- not modeled",
         "Same FHA property-flipping family as G023/G024."),
    35: ("YELLOW", "-", "-",
         "AUS supplemental-decision-screen rationale/timestamp fields -- ties to the AUS-"
         "findings gap (no DU/LPA/GUS export exists in this pilot)",
         "Decision-screen audit-trail fact; same underlying AUS-export gap as the aus_findings "
         "family, just a different named artifact within it."),
    60: ("RED", "-", "fair-lending/discriminatory-intent judgment", "-",
         "Same ECOA discriminatory-intent judgment class as G054/G057/G058/G059 (source text "
         "uses a non-breaking space, 'child\\xa0bearing', which the family regex below "
         "normalizes for)."),
    240: ("YELLOW", "closing-costs-plus-lender-fees vs total-loan-amount comparison (fields "
          "exist: closing_disclosure + loan amount, once loan_amount is extracted)",
          "'unreasonable' fee-amount judgment",
          "loan_amount field (not currently in FIELD_SPECS)",
          "Compound condition ('and/or'): the second half (fees exceed total loan amount) is "
          "crisp math once loan_amount exists; only 'unreasonable' is a judgment call. Kept "
          "YELLOW, not RED, following the assets-triage precedent for compound crisp+judgment "
          "conditions (e.g. decision 017's G007)."),
    248: ("YELLOW", "-", "-", "VA down-payment/percentage-down calculation fields -- loan_amount "
          "and a stated-down-payment field are not currently extracted", "VA fees-and-charges family."),
    250: ("YELLOW", "-", "-", "VA allowable-fee-limit table + loan_amount field -- neither exists today",
          "VA fees-and-charges family."),
    254: ("YELLOW", "-", "-",
          "interest-rate-at-application vs interest-rate-at-closing + re-underwrite tracking -- "
          "mismo_note_rate is extracted but no 'as originally submitted' comparison point exists",
          "VA fees-and-charges family; partial field exists, the comparison logic does not."),
    256: ("YELLOW", "-", "-", "VA down-payment-percentage calculation fields -- same gap as G248",
          "Same VA fees-and-charges family as G248."),
    258: ("YELLOW", "-", "-",
          "NOV reasonable-value field + sales-concessions field (4% threshold) -- va_nov doc "
          "exists (loan 03) with nov_issue_date extracted, but no reasonable-value or "
          "concessions-amount field", "VA fees-and-charges family; crisp threshold math once fields exist."),
    279: ("YELLOW", "-", "-",
          "RHS eligible-income-source classification -- not modeled",
          "Same RHS income-underwriting family as the rhs_income_calc family (income-source "
          "eligibility sub-condition)."),
    337: ("YELLOW", "presence of a documented repayment analysis (RHS)", "'significantly higher' "
          "payment-shock threshold (undefined in the AMQ text)",
          "current-housing-payment field + a repayment-analysis document -- neither modeled",
          "Compound condition: repayment-analysis presence is a crisp doc-presence check once "
          "the doc type exists; 'significantly higher' has no stated numeric threshold in the "
          "AMQ text itself, so that half stays human rather than inventing a cutoff."),
}

# ---------------------------------------------------------------------------
# Family regex engine for the ~366 groups not mechanically resolved by
# amq_compiler.py's own eval_class and not in OVERRIDES above. Each entry:
# (family_name, regex, bin, machine, human, needed_data, rationale). Checked
# in order; first match wins. Built from a full read of every group's
# untruncated question + response + exception text (dumped once to
# /tmp/underwriting_groups.txt during authoring, not re-derived from a
# truncated preview -- the decision-018 discipline this task's briefing
# required).
FAMILIES = [
    ("ecoa_discrim",
     r"discriminat|subjective standards|evaluated by the same standards as married|"
     r"race, ?color|child\s*bearing|national origin or sex",
     "RED", "-", "fair-lending/discriminatory-intent judgment", "-",
     "Fair-lending intent/disparate-treatment determination -- no bright-line fact a document "
     "extractor can settle; matches application-verification's judgment-word RED precedent."),
    ("income_durability",
     r"not likely to be consistently made|discounted or excluded from consideration",
     "RED", "-", "income-continuance/durability judgment", "-",
     "Whether income 'is likely to be consistently made' or was properly weighed is an "
     "underwriter judgment call, not a bright-line fact."),
    ("risk_assessment_adequacy",
     r"did not adequately evaluate|well-reasoned conclusion|not overall complete and accurate|"
     r"did not evaluate all risk factors|excessive layering of risks|"
     r"additional layers of risk not considered|all due diligence not used to evaluate",
     "RED", "-", "holistic risk-adequacy / underwriting-conclusion judgment", "-",
     "Whether an underwriter's overall risk narrative is 'adequate,' 'well-reasoned,' or "
     "'complete' is a holistic judgment call on the underwriter's own written analysis, not a "
     "checkable fact."),
    ("redflag_sweep", r"red flags.{0,60}not (properly )?addressed",
     "RED", "-", "open-ended 'red flags not addressed' sweep", "-",
     "Open-ended file-wide red-flag-resolution sweep -- same class as application-"
     "verification's file-wide discrepancy RED."),
    ("discrepancy_sweep",
     r"material discrepancies|inconsistencies.{0,60}(?:were not addressed|not identified)|"
     r"did not identify.{0,20}resolve inconsistencies|unresolved material discrepancies",
     "RED", "-", "open-ended cross-file discrepancy/inconsistency sweep", "-",
     "Open-ended cross-document discrepancy/inconsistency sweep -- same class as application-"
     "verification's file-wide-discrepancies RED; a specific discrepancy would need its own "
     "check, this row is the general catch-all."),
    ("methodology_review", r"methodology used to review rejected applications",
     "RED", "-", "process/methodology adequacy judgment", "-",
     "Whether a lender's internal review methodology was properly documented and followed is "
     "a process judgment, not a file fact."),
    ("misuse_of_entitlement", r"misuse of the Veteran|indicating possible misuse",
     "RED", "-", "fraud-pattern/investigative judgment", "-",
     "Whether documentation 'indicates possible misuse' is an investigative judgment call, "
     "not a bright-line fact."),
    ("unreasonable_judgment", r"\bunreasonable\b|not reasonable to function",
     "RED", "-", "'(un)reasonable' judgment", "-",
     "'(Un)reasonable' dominates the condition -- same judgment class as asset-verification's "
     "'unreasonable' REDs (decision 017)."),

    # ---------------- AUS / findings-report family (largest single gap) -----
    ("aus_findings",
     r"\bDU\b|Desktop Underwrit|Loan Product Advisor|\bLPA\b|\bGUS\b|TOTAL Scorecard|"
     r"Feedback Certification|Underwriting Findings|Underwriting Analysis|casefile ID|"
     r"DUFindings|Risk Class of Caution|\bAUS\b|automated underwriting|resubmi(t|ssion)|"
     r"feedback messages|key number|second job documentation|complete loan application "
     r"containing the required documentation|abbreviated loan app|"
     r"[Dd]ata element.*chang.*without.*re-underwritten|"
     r"not resubmitted where the data element|"
     r"material change.*without the loan being re-underwritten",
     "YELLOW", "-", "-",
     "DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, "
     "LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 "
     "fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)",
     "Same AUS-submission gap flagged in the asset-verification triage (decision 017, "
     "G037/G039/G095/G179/G243/G244) -- no DU, LPA, or TOTAL Scorecard export exists anywhere "
     "in the 5-loan corpus."),

    # ---------------- CAIVRS / exclusionary / OFAC / GSA family -------------
    ("caivrs_ldp_gsa",
     r"CAIVRS|LDP(/| )GSA|LDP list|GSA list|GSA/SAM|www\.sam\.gov|non-procurement list|"
     r"GSA.{0,5}LDP|LDP.{0,5}GSA",
     "YELLOW", "-", "-",
     "caivrs doc type already exists in DOC_TYPES and is present for loan 02 only "
     "(05_CAIVRS_LDP_GSA.pdf) but has zero FIELD_SPECS/FACT_SPECS entries -- no 'clear'/'hit' "
     "fact is extracted from it, and no loan 01/03/04/05 has this document at all",
     "Per decision 016's own precedent, CAIVRS/LDP/GSA screening is treated as an ordinary "
     "point-in-time screenshot document (not a live-registry Bucket-C lookup like NMLS) -- "
     "ready for Bucket-B-style field extraction once deepened, but genuinely absent as a "
     "fixture for 4 of 5 loans."),
    ("ofac_exclusionary",
     r"OFAC SDN|Exclusionary List|Suspended Counterparty|FHFA SCP|exclusionary list|"
     r"BSA, Money Laundering|USA PATRIOT Act",
     "YELLOW", "-", "-",
     "OFAC SDN list / Freddie Mac Exclusionary List / FHFA Suspended Counterparty Program / "
     "BSA-AML screening record (no such document or fixture exists in any of the 5 synthetic "
     "loans)",
     "Distinct from the CAIVRS/LDP/GSA family above -- no per-loan screenshot document for "
     "these specific lists exists anywhere in the corpus (not even one instance), a genuine "
     "Bucket-A fixture gap, not merely thin extraction."),
    ("de_certification", r"Direct Endorsement.{0,10}certified|DE certified",
     "YELLOW", "-", "underwriter DE-certification currency",
     "underwriter DE-certification roster (staff credential, not a loan fact)",
     "Possible Bucket-C candidate (same kind as the discarded NMLS rule, decision 016) -- "
     "whether an underwriter's DE certification is CURRENTLY valid is an institutional-staff "
     "attribute, not something the loan file can self-certify. Flagged, not unilaterally "
     "classified as Bucket C -- a human should decide, per decision 017's G218 precedent."),
    ("va_uw_credentialing",
     r"VA approved and.or registered as the lender|non-supervised automatic lender",
     "YELLOW", "-", "-", "underwriter VA-approval/registration status (staff credential, not a loan fact)",
     "Same institutional-staff-credential pattern as de_certification -- possible Bucket-C "
     "candidate, flagged not decided."),

    # ---------------- Specific named forms not in corpus (Bucket A) ---------
    ("hud_92900lt", r"92900-LT|HUD-92900-LT",
     "YELLOW", "-", "-",
     "Form HUD-92900-LT, FHA Loan Underwriting and Transmittal Summary (distinct from the "
     "HUD-92900-A Addendum already extracted for loan 02 -- no HUD-92900-LT document exists "
     "in any of the 5 loans)",
     "Same distinct-form nuance decision 014 flagged for HUD-92900-B vs -A: HUD-92900-LT is "
     "FHA's transmittal/underwriting summary, not the borrower-certification Addendum "
     "(hud_92900a) this pilot already parses -- a genuine, separate fixture gap."),
    ("va_26_6393", r"26-6393|VA Form 26-639\b|VA Loan Analysis|income used to qualify was calculated|"
     r"every known debt, judgment, bankruptcy",
     "YELLOW", "-", "-", "VA Form 26-6393 (VA Loan Analysis) -- not in any synthetic loan folder",
     "Niche VA underwriting-analysis form; loan 03 (the pilot's only VA loan) does not contain "
     "this document."),
    ("va_26_1820", r"26-1820", "YELLOW", "-", "-",
     "VA Form 26-1820 (Report and Certification of Loan Disbursement) -- not in corpus",
     "Niche post-closing VA form, absent from loan 03."),
    ("va_26_1817", r"26-1817", "YELLOW", "-", "-",
     "VA Form 26-1817 (Unmarried Surviving Spouse eligibility) -- not in corpus",
     "Niche VA eligibility form, absent from loan 03."),
    ("va_26_8937", r"26-8937", "YELLOW", "-", "-",
     "VA Form 26-8937 (Verification of VA Benefits) -- not in corpus",
     "Niche VA benefits-verification form, absent from loan 03."),
    ("rd_3555_21", r"3555-21|RD 3555", "YELLOW", "-", "-",
     "Form RD 3555-21 (Request for Single Family Housing Loan Guarantee) -- not in corpus",
     "USDA guarantee-request form; loan 05 (the pilot's only USDA loan) does not contain this "
     "document."),
    ("form_1008_1077", r"\b1008\b|\b1077\b", "YELLOW", "-", "-",
     "1008/1077 Uniform Underwriting and Transmittal Summary -- no such document/field exists "
     "for any agency in this pilot",
     "A distinct transmittal-summary form from every doc type this pilot currently parses; "
     "appears across FNM/FRD/RHS variants of the same underlying gap."),
    ("attachment_9b", r"Attachment 9-B", "YELLOW", "-", "-",
     "Attachment 9-B, Uniform Transmittal Summary (RHS income-calculation form) -- not in corpus",
     "Niche RHS income-documentation attachment, absent from loan 05."),
    ("loan_quality_cert", r"Lender.s Loan Quality Certification", "YELLOW", "-", "-",
     "Lender's Loan Quality Certification (VA) -- not in corpus",
     "Post-closing VA certification document, absent from loan 03."),
    ("conditional_commitment", r"Conditional Commitment", "YELLOW", "-", "-",
     "RHS Conditional Commitment -- not in corpus", "USDA/RHS commitment document, absent from loan 05."),
    ("living_trust", r"[Ll]iving [Tt]rust|inter vivos|trustee", "YELLOW", "-", "-",
     "Living Trust Agreement / inter-vivos-revocable-trust documentation -- not in corpus",
     "None of the 5 synthetic loans involves a trust-held title; niche fixture gap."),
    ("hud_92561", r"92561|Hotel and Transient", "YELLOW", "-", "-",
     "Form HUD-92561 (Hotel and Transient Use) -- not in corpus",
     "Niche FHA property-type form, absent from loan 02."),
    ("adverse_action_ecoa_notice",
     r"Notice of Incompleteness|[Nn]otice of [Aa]dverse [Aa]ction|ECOA notice|"
     r"notified of the action taken",
     "YELLOW", "-", "-", "adverse-action/incompleteness notice + its mailing/received dates -- not in corpus",
     "ECOA compliance-letter family; no such correspondence document exists in any of the 5 loans."),
    ("nonborrowing_spouse_ssn",
     r"[Nn]on-borrowing spouse|Form SSA.?89|eCBSV|multiple SSNs|more than one Social Security|"
     r"Social Security|\bSSN\b|\bITIN\b|identity of each borrower",
     "YELLOW", "-", "-",
     "SSN-discrepancy resolution documentation (SSA verification letter, Form SSA-89/eCBSV) or "
     "identity-verification record -- not in corpus",
     "SSN-validation family; no such verification record exists in any of the 5 loans."),
    ("dd214_military", r"DD Form 214|military orders", "YELLOW", "-", "-",
     "DD Form 214 / military orders documentation -- not in corpus",
     "Military-service-verification family, absent from the corpus."),
    ("homeownership_education", r"[Hh]omeownership education|housing counseling",
     "YELLOW", "-", "-", "homeownership-education/housing-counseling completion certificate -- not in corpus",
     "Niche counseling-completion document, absent from the corpus."),
    ("citizenship_residency",
     r"USCIS|refugee or asylee|non-US citizen|qualified alien|permanent resident alien|DACA|"
     r"Micronesia|Marshall Islands|Palau|[Rr]esidency status",
     "YELLOW", "-", "-",
     "citizenship/residency-status documentation (USCIS determination, alien-registration "
     "evidence) -- not in corpus",
     "Citizenship/residency family; not modeled at all in this pilot (same gap flagged for "
     "asset-verification's G284, decision 017)."),
    ("affordable_second_501c", r"Affordable Second|501\(c\)", "YELLOW", "-", "-",
     "Affordable Second program documentation / IRS Section 501(c) determination letter -- not "
     "in corpus",
     "Freddie Mac secondary-financing program family, absent from the corpus (same 501(c) "
     "document family flagged for asset-verification's G440, decision 017)."),
    ("disaster_flex", r"FEMA|disaster (declaration|area)|ACE waiver|ACE\+",
     "YELLOW", "-", "-", "FEMA disaster-declaration date + ACE/ACE+PDR waiver documentation -- not in corpus",
     "Disaster-area documentation-flexibility family, absent from the corpus."),
    ("reo_schedule", r"financed propert|multiple financed", "YELLOW", "-", "-",
     "a parsed real-estate-owned (REO) schedule entity from the 1003 (the extractor does not "
     "yet treat the 1003's REO section as its own entity)",
     "Same gap flagged in the asset-verification triage (decision 017, G240/G241) -- the "
     "count of financed properties isn't derived anywhere today."),
    ("secondary_financing_terms", r"secondary financing|subordinate financing",
     "YELLOW", "-", "-", "secondary/subordinate-financing note + terms documentation -- not in corpus",
     "Same secondary-financing family flagged in asset-verification (decision 017, "
     "G007/G267-271)."),
    ("private_transfer_fee_contract",
     r"private transfer,? reconveyance|resale fee|private transfer fee|shared equity loan",
     "YELLOW", "-", "-",
     "sales contract document (this pilot has NO purchase/sales contract document type in any "
     "of the 5 synthetic loans -- same systemic gap flagged in asset-verification's EMD "
     "family, decision 017)",
     "Same missing-purchase-contract gap as asset-verification's earnest-money-deposit family "
     "(G040/G081/G084/G086, decision 017)."),
    ("tandem_file", r"tandem file", "YELLOW", "-", "-",
     "a 'tandem file' (co-issued/companion loan file) concept -- not modeled; no such document "
     "or cross-loan-file relationship exists in this pilot",
     "Niche cross-file consistency check, absent from the corpus."),
    ("nonprofit_eligibility", r"[Nn]onprofit", "YELLOW", "-", "-",
     "HUD Nonprofit Agency Roster cross-reference -- an external roster lookup, not a "
     "loan-file fact (same kind of gap as CAIVRS/LDP/GSA, though evidenced by a roster "
     "listing rather than a per-loan screenshot)",
     "Nonprofit-borrower-eligibility family; no roster document/fixture exists in this "
     "pilot's corpus."),
    ("hmda_demographic", r"HMDA|demographic information", "YELLOW", "-", "-",
     "HMDA demographic-data entry fact (FHA Connection screen) -- not modeled",
     "Niche FHA Connection data-entry fact, absent from the corpus."),
    ("case_number_transfer", r"[Cc]ase number was transferred", "YELLOW", "-", "-",
     "case-number-transfer documentation between lenders -- not modeled",
     "Niche FHA case-transfer fact, absent from the corpus."),
    ("borrower_authorization_consent", r"consent for use of applicant|authorization",
     "YELLOW", "-", "-", "signed borrower-information-use consent statement -- not in corpus",
     "Niche FHA authorization form, absent from the corpus."),
    ("va_pending_claim_rating",
     r"pre-discharge claim|memorandum rating|proposed rating|National Guard",
     "YELLOW", "-", "-", "VA pending-disability-claim / National-Guard-service-days documentation -- not modeled",
     "Niche VA eligibility sub-conditions, absent from the corpus."),
    ("delinquent_child_support_credit", r"child support|arrear", "YELLOW", "-", "-",
     "delinquent-child-support repayment-history documentation -- not modeled",
     "Niche RHS credit-eligibility sub-condition, absent from the corpus."),
    ("energy_efficient_mortgage", r"[Ee]nergy efficient|[Ee]nergy conservation",
     "YELLOW", "-", "-", "Energy Efficient Mortgage (EEM) program documentation -- not modeled",
     "Niche FHA EEM program family, absent from the corpus."),
    ("rental_tenant_rights", r"tenants rights|rental agreement", "YELLOW", "-", "-",
     "a rental/lease agreement document -- not modeled",
     "Niche landlord-tenant legal family, absent from the corpus."),
    ("mortgage_modification", r"[Mm]odification", "YELLOW", "-", "-",
     "a mortgage-modification agreement document -- not modeled",
     "Niche modified-loan-eligibility family, absent from the corpus."),
    ("nonstandard_payment_option", r"non-monthly payment option|nonstandard payment",
     "YELLOW", "-", "-", "a non-standard-payment-option agreement document -- not modeled",
     "Niche FNM payment-collection family, absent from the corpus."),
    ("va_60day_submission", r"submitted to VA within 60 days", "YELLOW", "-", "-",
     "a VA-submission-date fact -- not modeled (no field captures when the loan was submitted "
     "to VA post-closing)",
     "Niche VA prior-approval timing fact, absent from the corpus."),
    ("identity_of_interest_construction", r"builder, developer or seller|identities of interest",
     "YELLOW", "-", "-", "an identity-of-interest relationship fact (borrower's relationship to "
     "builder/developer/seller) -- not modeled",
     "Niche identity-of-interest family, absent from the corpus."),
    ("foreign_language_docs", r"foreign origin|translated into English", "YELLOW", "-", "-",
     "a translation-attached fact for foreign-language documents -- not modeled",
     "Niche compliance fact, absent from the corpus (no foreign-language document exists in "
     "any of the 5 loans)."),

    # ---------------- Threshold math needing new fields on docs already in corpus (Bucket B) --
    ("ltv_cltv_hcltv", r"\bLTV\b|\bCLTV\b|\bHCLTV\b|\bTLTV\b",
     "YELLOW", "-", "-",
     "loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; "
     "appraised_value already is)",
     "Crisp ratio math once loan_amount is extracted -- appraisal doc already supplies "
     "appraised_value, but no field captures the loan amount itself anywhere in FIELD_SPECS."),
    ("credit_score_threshold",
     r"[Mm]inimum [Dd]ecision [Cc]redit [Ss]core|MDCS|credit score range|"
     r"indicator score of 720|minimum score of 720",
     "YELLOW", "-", "-",
     "a credit_score field on credit_report (credit_report doc exists in every loan; no score "
     "field is extracted today -- only individual tradelines)",
     "Bucket-B-style: the document exists, the specific field does not. (Note: this task's own "
     "briefing claimed borrower_credit_score/coborrower_credit_score are already extracted -- "
     "checked against extract_loan.py directly via grep and found NOT to be true; no such "
     "field or credit-inquiry entity exists anywhere in the extractor today.)"),
    ("funding_fee_mip", r"funding fee|MIP\b|mortgage insurance premium|UFMIP",
     "YELLOW", "-", "-",
     "VA funding-fee / FHA MIP calculation fields (percentage tables, exemption status, loan "
     "amount) -- not extracted",
     "Crisp percentage-table math once the fields exist; no such fields are in FIELD_SPECS "
     "today."),
    ("va_guaranty_calc",
     r"\$144,000|Blue Water Navy|max(?:imum)? guaranty|maximum loan amount|guarantee amt|"
     r"VA maximum loan amount",
     "YELLOW", "-", "-",
     "VA loan-amount/entitlement/guaranty-calculation fields (loan_amount is not currently "
     "extracted at all; entitlement amount is not extracted from va_coe)",
     "Crisp statutory-formula math (all thresholds are stated directly in the AMQ text "
     "itself, not invented) once loan_amount and entitlement fields exist -- neither does "
     "today."),
    ("loan_limit_conforming", r"loan limits based on loan type|conforming loan limit",
     "YELLOW", "-", "-",
     "the applicable conforming loan limit (by county/loan type) + loan_amount field -- "
     "neither is modeled",
     "Crisp comparison once both exist; conforming-loan-limit table is an external reference "
     "table, not derivable from the loan file alone."),
    ("max_loan_amount_mri",
     r"maximum (FHA )?mortgage amount|total amount financed exceeded|"
     r"[Mm]inimum req.d investment|\bMRI\b|adjusted value",
     "YELLOW", "-", "-",
     "loan_amount + adjusted-value fields (appraised_value is extracted; the loan amount "
     "itself and FHA's 'adjusted value' concept are not)",
     "Same loan_amount-field gap as ltv_cltv_hcltv family."),
    ("coe_conditions_entitlement",
     r"Certificate of Eligibility had conditions|Cert of Eligibility is insufficient|entitlement",
     "YELLOW", "-", "-",
     "COE entitlement-amount + guaranty-calculation fields (va_coe doc exists for loan 03 but "
     "only doc-presence is checked today, no entitlement-amount field is extracted)",
     "Bucket-B-style: va_coe doc type exists, but no field captures the entitlement dollar "
     "amount or guaranty percentage this row's math needs."),
    ("title_effective_date_90day", r"90.days of the closing date|title effective date",
     "YELLOW", "-", "-",
     "a title-commitment effective_date field (title_commitment doc exists in loan 01; only "
     "title_vesting_commitment is currently extracted from it)",
     "Crisp date-math once the field exists -- Bucket-B-style, same document, new field."),
    ("first_lien_position", r"first lien position",
     "YELLOW", "-", "-",
     "a first-lien-position fact on title_commitment (doc exists in loan 01 only; no such "
     "field/fact exists today)",
     "Bucket-B-adjacent: title_commitment doc type exists but this specific fact isn't "
     "extracted; absent entirely for the other 4 loans."),
    ("title_waiver_nov_conditions", r"General Waiver|conditions/limitations not on NOV",
     "YELLOW", "-", "-", "title-exception-vs-NOV cross-reference fields -- not modeled",
     "Title/NOV cross-document family, needs new derivation logic on top of two docs that do "
     "exist (title_commitment, va_nov)."),
    ("private_transfer_fee_regulation", r"[Pp]rivate [Tt]ransfer [Ff]ee|shared equity",
     "YELLOW", "-", "-", "private-transfer-fee covenant documentation (title/covenant language) -- not modeled",
     "Niche title-covenant family, absent from the corpus."),
    ("title_general",
     r"[Tt]itle (insurance|commitment|polic|opinion|exceptions|requirements)|"
     r"attorney.s title opinion|[Ee]ncroachment|Schedule B|[Cc]hain of [Tt]itle|"
     r"title lien search|title insurer",
     "YELLOW", "-", "-",
     "specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, "
     "encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these "
     "specific sub-facts are in FIELD_SPECS",
     "Title-family YELLOW: the title_commitment doc type exists but is thin (one field), and "
     "several of these rows describe an attorney's title opinion letter, a distinct document "
     "type not modeled at all."),
    ("special_assessment_lender_contrib",
     r"special assessment|lender (credit|incentive)|premium pricing",
     "YELLOW", "-", "-",
     "special-assessment / lender-incentive fields on closing_disclosure (doc exists in every "
     "loan; these specific line items are not in FIELD_SPECS)",
     "Bucket-B-style, same family flagged in asset-verification's IPC group (decision 017, "
     "G148 etc.) -- doc exists, field doesn't."),
    ("investment_arm_type", r"7/6.month or 10/6.month ARM",
     "YELLOW", "-", "-",
     "mismo_amortization_type value-format comparison (the field IS already extracted from "
     "MISMO XML; the specific '7/6 vs 10/6' ARM-type parsing/comparison logic does not exist "
     "yet)",
     "Bucket-B-style: closest thing to a ready candidate in this batch -- the field already "
     "exists (mismo_amortization_type), but no logic compares its value against the specific "
     "ARM-reset-period strings this row needs; NOT classified GREEN because that comparison "
     "logic has never been verified against a real loan (none of the 5 is an investment-"
     "property ARM) -- exactly the untested-confidence trap decision 018 warned about."),
    ("credit_doc_aging_integrity",
     r"credit document.s. exceed age|faxed credit documentation|"
     r"not delivered directly to.{0,5}returned from source",
     "YELLOW", "-", "-",
     "verification-document source/date-of-receipt fields (VOE/VOD/VOM 'directly from "
     "source' + document date vs Note date) -- not modeled",
     "Freddie Mac credit-document-integrity family; needs new fields on documents that mostly "
     "already exist."),
    ("paystub_date_check", r"YTD paystub|paystub used to verify income was dated",
     "YELLOW", "-", "-",
     "a paystub date field (paystub doc type exists in every loan but extract_loan.py has "
     "ZERO FIELD_SPECS entries for it today -- verified by reading the file directly)",
     "Bucket-B-style: the document exists in every loan folder, but no field is extracted "
     "from it at all -- a genuine and easily-fixed extraction-thinness gap distinct from a "
     "missing fixture."),
    ("repair_cost_appraisal", r"[Rr]epair costs were added to the sales price",
     "YELLOW", "-", "-",
     "a repair-cost dollar-amount field on the appraisal (appraisal doc exists in every loan; "
     "only mpr_repair_required, a boolean, is extracted today -- no dollar figure)",
     "Bucket-B-style: appraisal doc already parsed and even has a related boolean fact "
     "(mpr_repair_required); the specific repair-cost dollar amount this row's math needs is "
     "not extracted."),
    ("debt_paydown_source", r"paid down or paid in full|PIF to qualify",
     "YELLOW", "-", "-",
     "source-of-funds-for-debt-payoff documentation -- ties to the asset-verification "
     "large-deposit/source-of-funds family (decisions 017/018)",
     "Cross-block with asset-verification's sourcing-documentation gap; not a blind reuse of "
     "LargeDepositShape (different condition: paying off a debt vs. an unsourced deposit), "
     "flagged not wired."),
    ("reserves_multiple_props", r"reserve requirement|sufficient assets to meet",
     "YELLOW", "-", "-",
     "a reserves derivation for multiple financed properties -- same reserves-family gap as "
     "asset-verification's G238 (decision 017)",
     "Same reserves-derivation gap already flagged in asset-verification triage."),
    ("compensating_factors_derogatory",
     r"[Cc]ompensating factors were used to compensate|comp factors or ext circumstances|"
     r"comp factors not noted",
     "YELLOW", "-", "-",
     "compensating-factors/extenuating-circumstances documentation on the FHA Transmittal "
     "(HUD-92900-LT) or VA Loan Analysis (26-6393) -- neither form is in corpus",
     "Same hud_92900lt/va_26_6393 fixture family, compensating-factors sub-condition."),
    ("rhs_loan_term",
     r"repayment term of 30 years|rate-terms|interest rate increased prior to closing|"
     r"ineligible for an RHS guaranteed loan",
     "YELLOW", "-", "-",
     "RHS loan-term eligibility fields (note rate at closing vs at commitment, amortization "
     "term) -- mismo_note_rate is extracted but no 'rate at commitment' comparison point "
     "exists",
     "RHS loan-term family; partial field exists (mismo_note_rate) but the comparison point "
     "this row needs does not."),

    # ---------------- RHS/general debt-ratio inclusion rules (entities exist, derivation doesn't) --
    ("debt_ratio_inclusion",
     r"was not included in the (DTI|monthly debt)|DTI debt ratio|debt ratio calculation|"
     r"included in the monthly obligations|omitted from the monthly debt|"
     r"5% of the (balance|payment|outstanding balance)|0\.5% of the (balance|loan balance)|"
     r"balance was not used|alternate (amt|amount) used|"
     r"payment amt used was not the credit report|income tax repayment plan|Judgment pymt|"
     r"more than 10 pymts left",
     "YELLOW", "-", "-",
     "a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities "
     "(both entity types are already extracted for every loan; no logic classifies a specific "
     "liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, "
     "student-loan, etc. -- or aggregates a DTI ratio from them)",
     "Every one of these RHS/FHA/VA 'was a specific debt type included in DTI' rows is "
     "individually crisp math (a rule engine could apply it), but needs a DTI-aggregation + "
     "liability-classification layer that does not exist yet -- no new document required, a "
     "real derivation-logic gap."),
    ("dti_piti_ratio_calc", r"\bDTI\b|debt.to.income|PITIA?\b|\bratio\b",
     "YELLOW", "-", "-",
     "a general DTI/PITI(A) derivation from urla_liabilities/tradelines + income fields "
     "(piti_ratio/dti_ratio today are extracted ONLY from usda_ratio_waiver_doc, present for "
     "loan 05/USDA only)",
     "Distinct from the already-wired RatioWaiverShape (CHK-UND-002), which tests a narrower "
     "USDA-specific condition (ratio exceeds guideline AND no waiver documented); this family "
     "covers general ratio-calculation-accuracy and inclusion-of-specific-debt-type "
     "conditions across other agencies -- entities exist (tradelines, urla_liabilities) but "
     "no general DTI/PITI aggregation derivation exists yet."),

    # ---------------- Occupancy / eligibility narrative presence checks (mostly Bucket A) -----
    ("occupancy_certification", r"[Oo]ccupy|[Oo]ccupancy|primary residence|principal residence",
     "YELLOW", "-", "-",
     "an occupancy-intent certification / military-orders / lease-review fact -- not "
     "currently modeled (no occupancy-related field or fact exists in FIELD_SPECS/FACT_SPECS)",
     "Occupancy-eligibility family; several distinct sub-conditions (military "
     "unable-to-occupy, group-home leased-to-business, second-home suitability) each need "
     "their own new fact, none of which exist today."),
    ("cosigner_guarantor_noncoocc",
     r"co-?signer|guarantor|non-occupying borrower|non-occupant borrower",
     "YELLOW", "-", "-",
     "co-signer/guarantor/non-occupying-borrower structured data (URLA parties exist as free "
     "text; no field distinguishes borrower role/occupancy intent)",
     "Same family as the LTV-for-non-occupying-borrower rules -- needs a borrower-role "
     "classification not modeled today."),
    ("property_investment_niche",
     r"self-sufficiency rental|financial interest in more than|mixed-use|group home",
     "YELLOW", "-", "-",
     "specific property-type/investment-eligibility facts (self-sufficiency rental income "
     "calc, multi-unit financial-interest count, mixed-use square footage) -- none modeled "
     "today",
     "Niche FHA/FNM property-type family, absent from the corpus."),
    ("rhs_refi_eligibility", r"[Ss]treamline|[Rr]efinanc|Statement of Loan Balance",
     "YELLOW", "-", "-",
     "RHS refinance-eligibility facts (existing-loan closing date, borrower-retention, rate "
     "comparison) -- not modeled; loan 04 is the pilot's only refi loan and it's a "
     "conventional cash-out, not an RHS streamline",
     "RHS-refinance family; no RHS refinance fixture exists in the corpus at all."),
    ("rhs_income_calc",
     r"[Aa]nnual income|eligible source|[Ii]ncome calculation|student living away|"
     r"household deductions|adult household members|ensuing 12 months|"
     r"income sources.*qualify.*excluded",
     "YELLOW", "-", "-",
     "RHS annual/household-income calculation derivation (income fields are extracted "
     "per-borrower on the 1003, but no RHS household-income aggregation/eligible-source-"
     "classification logic exists)",
     "RHS income-underwriting family; entities/fields partially exist "
     "(base_monthly_income_1003, co-borrower income) but the RHS-specific household-income "
     "derivation this row needs does not."),
    ("uw_approval_conditions_generic", r"[Aa]ll additional approval condition",
     "YELLOW", "-", "-", "an underwriter approval-conditions checklist -- no such structured list exists today",
     "Generic 'were UW conditions cleared' catch-all; needs the conditions to be enumerated "
     "per loan, which this pilot doesn't capture."),
]


def normalize(text):
    return text.replace(" ", " ")


def combined_text(g):
    return normalize(g["question_text"] + " " + g["response_text"] + " "
                     + " ".join(sorted({m for m in g["exc_descs"]})))


def retrieve_topics(sg, rule_text, k=3):
    stop = set("were all the of and or a an is in to for was not on by with as at have "
               "been requirements met all any".split())
    def tokens(t):
        return {w for w in re.findall(r"[a-z]{3,}", t.lower())} - stop
    rt = tokens(rule_text)
    scored = []
    for t in sg["topics"]:
        overlap = len(rt & tokens(t["title"]))
        if overlap:
            scored.append((overlap, t["code"], t["title"], t["pdf_page"]))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [{"code": c, "title": ti, "pdf_page": p, "score": s}
            for s, c, ti, p in scored[:k]]


def classify(gid, g):
    if PASS_RE.match(g["response_text"].replace(" ", " ").strip()):
        return ("NOT_A_CHECK", "-", "-", "-",
                "Pass/N-A answer option, not a defect condition.", "mechanical")
    if g["ecs"] == ["doc_presence"]:
        targets = sorted({m for m in g["eval_targets"]})
        note = ""
        if gid == 167:
            note = (" CAVEAT (checked, not assumed): amq_compiler.py's own keyword classifier "
                     "mapped this via the 'certificate of eligibility' phrase in the exception "
                     "text to the va_coe doc type -- but VA Form 26-1880 is the REQUEST form "
                     "for a COE, not the COE itself. Same class of keyword-collision latent "
                     "bug decision 014 flagged for 'initial application' -> final_1003. Already "
                     "auto-compiled and working as a doc-presence check either way (va_coe is "
                     "absent for the other 4 loans regardless), so still GREEN, but the target "
                     "document identity is not a perfect fidelity match.")
        if gid == 255:
            note = (" CAVEAT (checked, not assumed): the missing item this row actually names "
                     "is an itemized pest-inspection invoice, not the NOV itself -- "
                     "amq_compiler.py's keyword classifier matched 'NOV' in the exception text "
                     "and pointed the doc-presence check at va_nov. The check will correctly "
                     "report NOT_EVALUATED/present based on va_nov's presence, which is a "
                     "coincidentally-adjacent but not textually-precise target.")
        return ("GREEN", "already-mapped/auto-compiled by amq_compiler.py: doc-presence check "
                "on %s" % ", ".join(targets), "-", "-",
                "Auto-compiled by amq_compiler.py's doc_presence classifier (the exception "
                "text matches 'not in file/missing/not provided' and names a mappable "
                "document type already in the extraction contract) -- already works." + note,
                "mechanical")
    if gid in OVERRIDES:
        bin_, mach, hum, need, rat = OVERRIDES[gid]
        return (bin_, mach, hum, need, rat, "override")
    text = combined_text(g)
    for name, pat, bin_, mach, hum, need, rat in FAMILIES:
        if re.search(pat, text, re.I):
            return (bin_, mach, hum, need, rat, name)
    raise SystemExit("Group %d ('%s' / '%s') matched no family and has no override -- "
                     "triage incomplete." % (gid, g["question_text"], g["response_text"]))


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

    if len(groups) != 461:
        raise SystemExit("Expected 461 unique groups for a fresh compile of %d underwriting-"
                         "review rules; got %d. Ruleset changed -- re-review this triage "
                         "before trusting it." % (len(rules), len(groups)))

    out_groups, group_counter, rule_counter = [], Counter(), Counter()
    family_counter = Counter()
    for gid, ((q, resp), members) in enumerate(groups.items(), 1):
        agencies = sorted({m["agency"] for m in members})
        ecs = sorted({m["eval_class"] for m in members})
        g = {"question_text": q, "response_text": resp,
             "exc_descs": [m["exception_description"] for m in members
                          if m["exception_description"]],
             "ecs": ecs,
             "eval_targets": [m["eval_target"] for m in members if m["eval_target"]]}
        bin_, machine, human, needs, rationale, family = classify(gid, g)
        blocked_on_fixture = any(m["eval_class"] == "blocked_on_missing_fixture"
                                 for m in members)
        source_rows = sorted({n for m in members for n in m.get("source_rows", [])})
        fnm_or_generic = any(a in ("O-FNM", "GENERIC") for a in agencies)
        topics = (retrieve_topics(sg, q + " " + resp)
                  if fnm_or_generic and bin_ != "NOT_A_CHECK" else [])
        rec = {"group": gid, "question": q, "condition": resp,
               "agencies": agencies,
               "severities": sorted({m["severity"] for m in members if m["severity"]}),
               "codes": sorted({m["exception_code"] for m in members if m["exception_code"]}),
               "source_spreadsheet": source_csv,
               "source_rows": source_rows,
               "rule_count": len(members), "bin": bin_,
               "family": family,
               "blocked_on_missing_fixture": blocked_on_fixture,
               "machine_checkable": machine, "stays_human": human,
               "needed_data": needs, "rationale": rationale,
               "guide_candidates": topics,
               "sme_status": "PENDING REVIEW"}
        out_groups.append(rec)
        group_counter[bin_] += 1
        rule_counter[bin_] += len(members)
        family_counter[family] += 1

    result = {"block": BLOCK, "rules_total": len(rules),
              "unique_groups": len(groups),
              "bins_by_group": dict(group_counter),
              "bins_by_rule": dict(rule_counter),
              "family_counts": dict(family_counter),
              "classifier": "Claude (compile-time analyst), session 2026-07-30 -- PENDING SME REVIEW",
              "residual_income_shape_rejected_candidates": RESIDUAL_INCOME_REJECTED_CANDIDATES,
              "ratio_waiver_shape_rejected_candidates": RATIO_WAIVER_REJECTED_CANDIDATES,
              "groups": out_groups}
    with open(OUT_JSON, "w") as f:
        json.dump(result, f, indent=1, sort_keys=True)

    # ------------------------------------------------------------ SME packet
    lines = ["# SME Review Packet — underwriting-review block triage",
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
             "**Note on this block vs the two prior triages:** dedup collapse here is the "
             "smallest of the three (466 rules -> 461 groups, ~1.01x, vs asset-verification's "
             "~1.02x and application-verification's ~1.5x). Two shapes are already registered "
             "against this block in amq_compiler.py's MAPPED_SHAPES (ResidualIncomeShape, "
             "RatioWaiverShape) but both are wired to ZERO exception codes — this triage "
             "explicitly checked whether any of the 461 groups here describe the same real "
             "condition either shape already checks. Neither survived verification — see the "
             "REJECTED candidates note below and decision 022 for the full reasoning. Given "
             "the scale (366 groups not mechanically resolved by amq_compiler.py's own "
             "eval_class), classification below uses a family-regex engine built from a full "
             "read of every group's untruncated text, not a hand-typed dict per group — the "
             "`family` tag on each group names which regex matched, and OVERRIDES groups a "
             "small hand-classified residual.",
             "",
             "## ResidualIncomeShape / RatioWaiverShape — checked, NOT wired (negative result)",
             "",
             "- **ResidualIncomeShape (CHK-UND-001)** checks `doc_present_residual_income_"
             "worksheet == false AND mismo_mortgage_type == \"VA\"`. Closest candidate: **%s** "
             "— tests a materially different, compound condition (DTI>41%% OR residual income "
             "below minimum, AND whether the underwriter separately justified/documented "
             "compensating factors) — not a worksheet-presence fact. REJECTED."
             % ", ".join(RESIDUAL_INCOME_REJECTED_CANDIDATES),
             "- **RatioWaiverShape (CHK-UND-002)** checks `piti_ratio > piti_guideline AND "
             "dti_ratio > dti_guideline AND usda_ratio_waiver_in_file == false`, with both "
             "guideline values sourced only from `usda_ratio_waiver_doc` (loan 05/USDA only). "
             "Closest candidates: **%s** — each tests a different condition (a flat 34%%/29%% "
             "ceiling, or FHA/RHS-specific compensating-factors documentation on a form this "
             "pilot doesn't have) and, structurally, none of them are USDA/RHS loans whose "
             "waiver worksheet would populate `piti_guideline`/`dti_guideline` in the first "
             "place. REJECTED." % ", ".join(RATIO_WAIVER_REJECTED_CANDIDATES),
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
            lines.append("- **Family:** %s" % g["family"])
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
