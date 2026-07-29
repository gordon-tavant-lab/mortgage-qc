"""
Track F (2026-07-28, extended 2026-07-29): document-presence gating for
specialty-document predicate checks -- deterministic, zero-LLM, applied at
compile time (Non-Negotiable #1: compile, then run). Mirrors
known_compile_corrections.py's structure exactly.

Round 1 (2026-07-28): 46 checks in the comprehensive ruleset assert a
specific, named document is present/found/located in the file (e.g. "ICPL is
not located in the file", "ARB approval was not found in the loan file") but
ran unconditionally against every loan regardless of whether that loan's
transaction would ever produce such a document -- resolving NEEDS_REVIEW or
FAIL even on loans where the document genuinely doesn't apply. Each is gated
here on the matching doc_present_* fact (promoted into loan.fields by
qc_engine/build_loan_profiles_v4.py) so an absent document resolves
NOT_APPLICABLE instead.

Round 1's mapping was produced by an 8-reviewer categorization pass over the
287 candidate unconditional is_present/is_true checks in the 1,076 Fannie-
scoped ruleset, followed by a normalization/dedup pass -- 43 canonical
doc_present_* facts, 46 check_ids (fan-in only for
doc_present_federal_tax_payment_proof, 3 checks, and doc_present_form_1076,
2 checks). 4 borderline candidates were deliberately excluded during
normalization for bundling a content-completeness/correctness judgment with
presence (e.g. hoi_worksheet_complete, security-instrument-present-correct) --
a doc_present_* boolean can only assert existence, never correctness, so
gating those would risk a false auto-clear.

Round 2 (2026-07-29): round 1's candidate sweep used
result/rules/comprehensive_applicability.json to decide which checks were
"Fannie Mae or UNTAGGED scoped" -- that file is missing 1,260 of the v8
ruleset's 3,203 check_ids as keys entirely, so every genuinely-applicable
check missing from it (including checks the ORIGINAL Track F plan explicitly
named as targets, e.g. du-uw-findings-report-present,
homeready-income-limits-present) silently fell out of round 1's pool. Round 2
re-swept candidates against the CORRECT map,
result/rules/post_closing_only_applicability.json (0 missing check_ids, the
file run_018/run_019 actually use for their real scoped program-gate
summary), against the POST-round-1 engine state -- so there is zero overlap
with round 1's 46 already-gated checks by construction. That re-sweep adds
11 new canonical doc_present_* facts, 12 new check_ids (one new check_id per
new fact, except doc_present_du_uw_findings_report which fans in 2:
du-uw-findings-report-present and fnm-du-final-report-present -- the same
underlying document under two different check_ids in the ruleset), plus 1
more check_id merged onto round 1's existing
doc_present_construction_perm_conversion_rider fact
(single-close-construction-rider-present, a near-duplicate check_id of
round 1's single-close-construction-perm-rider-present, both genuinely
asserting the same document) -- 54 canonical doc_present_* facts, 59
check_ids total after round 2.

Python 3.9 compatible.
"""
from __future__ import annotations

from typing import Dict, List

DOCUMENT_PRESENCE_GATES: Dict[str, List[Dict[str, str]]] = {
    "covid19-fha-exterior-appraisal-amended-cert-scope": [{"field_name": "doc_present_appraisal_amended_cert_scope", "operator": "==", "value": "true"}],
    "appraiser-full-contract-provided": [{"field_name": "doc_present_appraiser_contract", "operator": "==", "value": "true"}],
    "portfolio-ctp-arb-approval-present": [{"field_name": "doc_present_arb_approval", "operator": "==", "value": "true"}],
    "asset-verification-report-present": [{"field_name": "doc_present_asset_verification_report", "operator": "==", "value": "true"}],
    "blanket-auth-credit-reverify-present": [{"field_name": "doc_present_blanket_credit_reverify_authorization", "operator": "==", "value": "true"}],
    "boarder-shared-residency-rent-doc-present": [{"field_name": "doc_present_boarder_shared_residency_rent_documentation", "operator": "==", "value": "true"}],
    "ctp-builders-risk-endorsement-present": [{"field_name": "doc_present_builders_risk_coverage_endorsement", "operator": "==", "value": "true"}],
    "biz-tax-returns-2yr-present": [{"field_name": "doc_present_business_tax_returns", "operator": "==", "value": "true"}],
    "condo-coop-financial-docs-present": [{"field_name": "doc_present_condo_coop_financial_docs", "operator": "==", "value": "true"}],
    "single-close-construction-perm-rider-present": [{"field_name": "doc_present_construction_perm_conversion_rider", "operator": "==", "value": "true"}],
    "covid19-va-income-break-doc-present": [{"field_name": "doc_present_covid19_income_break_doc", "operator": "==", "value": "true"}],
    "va-dd214-present": [{"field_name": "doc_present_dd214", "operator": "==", "value": "true"}],
    "ctp-draw-disb-notification-indemnity-present": [{"field_name": "doc_present_draw_disbursement_notification_indemnity", "operator": "==", "value": "true"}],
    "esign-notice-of-completion-present": [{"field_name": "doc_present_esign_notice_of_completion", "operator": "==", "value": "true"}],
    "exterior-only-appraisal-personal-inspection-cert": [{"field_name": "doc_present_exterior_only_appraisal_personal_inspection_cert", "operator": "==", "value": "true"}],
    "family-member-employer-tax-returns-present": [{"field_name": "doc_present_family_member_employer_tax_returns", "operator": "==", "value": "true"}],
    "fed-tax-due-proof-paid-present": [{"field_name": "doc_present_federal_tax_payment_proof", "operator": "==", "value": "true"}],
    "fha-federal-tax-due-proof-paid": [{"field_name": "doc_present_federal_tax_payment_proof", "operator": "==", "value": "true"}],
    "va-federal-tax-due-proof-paid-present": [{"field_name": "doc_present_federal_tax_payment_proof", "operator": "==", "value": "true"}],
    "flood-cert-life-of-loan-present": [{"field_name": "doc_present_flood_cert_life_of_loan", "operator": "==", "value": "true"}],
    "condo-project-questionnaire-form-1076-present": [{"field_name": "doc_present_form_1076", "operator": "==", "value": "true"}],
    "project-questionnaire-present": [{"field_name": "doc_present_form_1076", "operator": "==", "value": "true"}],
    "fnm-15381-form-1076a-present": [{"field_name": "doc_present_form_1076a", "operator": "==", "value": "true"}],
    "grant-funds-award-letter-transfer-present": [{"field_name": "doc_present_grant_funds_award_letter", "operator": "==", "value": "true"}],
    "hoa-meeting-minutes-present": [{"field_name": "doc_present_hoa_meeting_minutes", "operator": "==", "value": "true"}],
    "icpl-present": [{"field_name": "doc_present_icpl", "operator": "==", "value": "true"}],
    "interest-dividend-2yr-receipt-docs-present": [{"field_name": "doc_present_interest_dividend_income_documentation", "operator": "==", "value": "true"}],
    "irs-4506c-response-in-file": [{"field_name": "doc_present_irs_4506c_response", "operator": "==", "value": "true"}],
    "non-monthly-payment-agreement-missing": [{"field_name": "doc_present_non_monthly_payment_agreement", "operator": "==", "value": "true"}],
    "nonprofit-ida-documentation-present": [{"field_name": "doc_present_nonprofit_ida_documentation", "operator": "==", "value": "true"}],
    "va-eclosing-note-allonge-present": [{"field_name": "doc_present_note_allonge", "operator": "==", "value": "true"}],
    "ny-cema-form-3172-present": [{"field_name": "doc_present_ny_cema_form_3172", "operator": "==", "value": "true"}],
    "ugv-exception-private-bank-approved": [{"field_name": "doc_present_private_bank_exception_approval", "operator": "==", "value": "true"}],
    "project-approval-cert-present": [{"field_name": "doc_present_project_approval_certificate", "operator": "==", "value": "true"}],
    "public-assistance-agency-letter-present": [{"field_name": "doc_present_public_assistance_agency_letter", "operator": "==", "value": "true"}],
    "fnm-15384-questionnaire-approval-worksheet-present": [{"field_name": "doc_present_questionnaire_approval_worksheet", "operator": "==", "value": "true"}],
    "rent-credit-option-purchase-lease-docs-present": [{"field_name": "doc_present_rent_credit_option_purchase_lease_docs", "operator": "==", "value": "true"}],
    "rent-credit-option-purchase-checks-present": [{"field_name": "doc_present_rent_credit_option_purchase_receipts", "operator": "==", "value": "true"}],
    "rin-av-recording-present": [{"field_name": "doc_present_rin_av_recording", "operator": "==", "value": "true"}],
    "rov-disclosure-at-application-present": [{"field_name": "doc_present_rov_disclosure_at_application", "operator": "==", "value": "true"}],
    "sig-name-affidavit-aka-present": [{"field_name": "doc_present_signature_name_affidavit", "operator": "==", "value": "true"}],
    "capital-gains-signed-tax-returns-2yr": [{"field_name": "doc_present_signed_tax_returns_2yr", "operator": "==", "value": "true"}],
    "tax-return-or-4868-present": [{"field_name": "doc_present_tax_return_or_4868", "operator": "==", "value": "true"}],
    "tax-returns-foreign-income-present": [{"field_name": "doc_present_tax_returns_foreign_income", "operator": "==", "value": "true"}],
    "va-project-approval-cert-present": [{"field_name": "doc_present_va_project_approval_certificate", "operator": "==", "value": "true"}],
    "covid19-fnm-14442-vvoe-present": [{"field_name": "doc_present_vvoe", "operator": "==", "value": "true"}],

    # Track F round 2 (2026-07-29): 11 new-fact checks + 1 check merged onto
    # round 1's existing doc_present_construction_perm_conversion_rider fact.
    "covid19-fha-business-open-confirmation": [{"field_name": "doc_present_business_open_confirmation", "operator": "==", "value": "true"}],
    "cu-score-gaar-worksheet-present": [{"field_name": "doc_present_gaar_worksheet", "operator": "==", "value": "true"}],
    "disaster-repair-docs-present": [{"field_name": "doc_present_disaster_repair_documentation", "operator": "==", "value": "true"}],
    "du-uw-findings-report-present": [{"field_name": "doc_present_du_uw_findings_report", "operator": "==", "value": "true"}],
    "fnm-du-final-report-present": [{"field_name": "doc_present_du_uw_findings_report", "operator": "==", "value": "true"}],
    "fha-appraisal-subject-to-completion-docs-present": [{"field_name": "doc_present_appraisal_subject_to_completion_docs", "operator": "==", "value": "true"}],
    "fha-late-endorsement-request-missing": [{"field_name": "doc_present_fha_late_endorsement_request", "operator": "==", "value": "true"}],
    "gift-pooled-donor-cohabitation-cert-present": [{"field_name": "doc_present_cohabitation_certification", "operator": "==", "value": "true"}],
    "homeready-income-limits-present": [{"field_name": "doc_present_homeready_income_limits", "operator": "==", "value": "true"}],
    "overlay-exception-nat-uw-mgr-approval-email-present": [{"field_name": "doc_present_nat_uw_mgr_approval_email", "operator": "==", "value": "true"}],
    "sales-contract-present": [{"field_name": "doc_present_sales_contract", "operator": "==", "value": "true"}],
    "ugv-exception-portfolio-rep-approval-present": [{"field_name": "doc_present_portfolio_rep_exception_approval", "operator": "==", "value": "true"}],
    "single-close-construction-rider-present": [{"field_name": "doc_present_construction_perm_conversion_rider", "operator": "==", "value": "true"}],
}


def apply_document_presence_gates(checks) -> List[str]:
    """Mutates matching Check objects' applies_if in place. Returns the ids of
    checks actually gated (order-preserving, only ids present in both `checks`
    and DOCUMENT_PRESENCE_GATES). Skips -- never silently overwrites -- any
    check that already carries a non-null applies_if (a compile-time
    precondition already wired some other way should win; verified directly
    against the live ruleset that none of these 59 (round 1's 46 + round 2's
    13 new check_ids) currently do, so this is a defensive no-op today, not
    an active branch)."""
    gated = []
    for chk in checks:
        condition = DOCUMENT_PRESENCE_GATES.get(chk.id)
        if condition is None:
            continue
        if chk.applies_if:
            continue
        chk.applies_if = condition
        gated.append(chk.id)
    return gated
