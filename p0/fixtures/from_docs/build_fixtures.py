"""
build_fixtures.py — merges extract_pdf.py's truth+citation output and
extract_xml.py's sources.mismo output into 5 CanonicalLoan JSON fixtures,
one per synthetic loan, populated only from that loan's own folder (no
cross-loan data leakage). Deterministic: same source documents -> same
output JSON, every run (plan.md Constraints).

Output shape mirrors qc_engine/model.py's CanonicalLoan/SourceValue/DocCitation
directly (fields[name] = {truth, sources, citation, doc_confidence}), so
loading a fixture back into CanonicalLoan requires zero changes to model.py —
see fixture_loader.py for the loader that does that reconstruction.

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from extract_pdf import extract_pdf_fields  # noqa: E402
from extract_xml import extract_mismo_fields  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
DEMO_SYN_DIR = os.path.join(REPO_ROOT, "demo", "syn")

# folder name -> (mismo filename, loan_type) — the only per-loan metadata not
# derivable purely from extraction; loan_type is descriptive only, never used
# by verify_against_defects.py's field-level checks.
#
# NOTE (2026-07-20, see output/RULE-PROGRAM-GATING-FINDINGS.md §8): loan 01's and
# loan 04's real MISMO <MortgageType> is just "Conventional" -- neither carries a
# GSE-investor field. Loan 04's "Freddie Mac" label below is this fixture's own
# descriptive choice, not derived from the loan's actual data; program_gating.py
# correctly returns AMBIGUOUS for both. For a bounded LLM-compile pre-test, both
# are being assumed Fannie Mae (documented, not silently baked in) -- 010b is
# where a real investor/AUS field would make this derivable instead of assumed.
LOAN_PACKAGES = {
    "loan 01": ("09_Loan_Data_MISMO.xml", "Conventional Purchase"),
    "loan 02": ("09_Loan_Data_MISMO.xml", "FHA Purchase"),
    "loan 03": ("07_Loan_Data_MISMO.xml", "VA Purchase"),
    "loan 04": ("07_Loan_Data_MISMO.xml", "Freddie Mac Cash-Out Refi"),
    "loan 05": ("06_Loan_Data_MISMO.xml", "USDA RHS 502 Guaranteed"),
}


def build_loan_fixture(loan_folder_name: str) -> Dict[str, Any]:
    """Build one loan's CanonicalLoan-shaped fixture dict, from that loan's
    own folder only (no cross-loan leakage — every value below comes from
    files under demo/syn/<loan_folder_name>/)."""
    mismo_filename, loan_type = LOAN_PACKAGES[loan_folder_name]
    loan_folder = os.path.join(DEMO_SYN_DIR, loan_folder_name)
    mismo_path = os.path.join(loan_folder, mismo_filename)

    doc_fields = extract_pdf_fields(loan_folder)
    mismo_fields = extract_mismo_fields(mismo_path)

    loan_id = mismo_fields.get("loan_id")

    all_field_names = set(doc_fields) | set(mismo_fields) - {"loan_id"}
    fields: Dict[str, Any] = {}
    for name in sorted(all_field_names):
        doc_entry = doc_fields.get(name)
        sources: Dict[str, Any] = {}
        if name in mismo_fields:
            sources["mismo"] = mismo_fields[name]
        fields[name] = {
            "truth": doc_entry["value"] if doc_entry else None,
            "sources": sources,
            "citation": doc_entry["citation"] if doc_entry else None,
            "doc_confidence": doc_entry["doc_confidence"] if doc_entry else None,
        }
    fields.update(_derive_date_diff_fields(fields))

    facts = _derive_facts(fields)
    facts.update(_derive_document_presence_facts(loan_folder))

    return {
        "loan_id": loan_id,
        "loan_type": loan_type,
        "fields": fields,
        "facts": facts,
    }


# filename substring -> fact name. Each names ONE specific physical document,
# not a bundled doc_patterns/*.json file (fha_docs.json alone bundles 5
# distinct documents under one pattern) -- ruleset_defects.py's per-loan
# gating needs to know whether THAT SPECIFIC supporting document exists in
# this loan's own package, the real precondition for "is a missing-document
# predicate check even meaningful here" (as opposed to loan_type/program,
# which is wrong for borrower/transaction-level conditions like self-employed
# income or an unexplained large deposit -- those can occur under any
# program, not just the one loan in this 5-loan set that happens to have it).
_DOCUMENT_PRESENCE_SUBSTRINGS = {
    "doc_present_bank_statement": ["Bank_Statement"],
    "doc_present_hud92900a": ["HUD_92900A"],
    "doc_present_gift_letter": ["Gift_Letter"],
    "doc_present_va_appraisal": ["VA_Appraisal"],
    "doc_present_self_employed_income": ["Self_Employed"],
    "doc_present_usda_appraisal": ["Appraisal_Summary_USDA"],
    "doc_present_usda_property_eligibility": ["USDA_Property_Eligibility"],

    # Track F (2026-07-28): 43 more document types, one per specialty document
    # a real AMQ-derived check asserts must be present. UNLIKE the 7 facts
    # above, NONE of these documents exists anywhere across the 5 synthetic
    # loans (confirmed directly -- a full `git ls-tree`/directory listing of
    # every real file under demo/syn/loan 0{1-5}/ after the corpus was
    # restored this session shows only the 28 already-known real document
    # types; none of these 43 is among them). So every substring below is a
    # best-guess, never-yet-verified-against-a-real-filename pattern --
    # correctness is checked pairwise against every existing substring (no
    # collisions, e.g. "Form_1076_" vs "Form_1076A" cannot cross-match) and
    # against all 28 real filenames (spot-checked, no accidental true), but
    # NOT against a real document of this type, because none exists in this
    # project's corpus. If a document of one of these types is ever added to
    # demo/syn/ in the future, re-verify its real filename against the
    # substring here before trusting a "true" result from it.
    "doc_present_asset_verification_report": ["Asset_Verification_Report"],
    "doc_present_appraiser_contract": ["Appraiser_Contract"],
    "doc_present_business_tax_returns": ["Business_Tax_Returns"],
    "doc_present_blanket_credit_reverify_authorization": ["Blanket_Auth_Credit_Reverify"],
    "doc_present_boarder_shared_residency_rent_documentation": ["Boarder_Shared_Residency_Rent"],
    "doc_present_signed_tax_returns_2yr": ["Signed_Tax_Returns_2yr"],
    "doc_present_condo_coop_financial_docs": ["Condo_Coop_Financial"],
    "doc_present_form_1076": ["Form_1076_"],
    "doc_present_appraisal_amended_cert_scope": ["Appraisal_Amended_Cert_Scope"],
    "doc_present_vvoe": ["VVOE_"],
    "doc_present_covid19_income_break_doc": ["Covid19_Income_Break_Documentation"],
    "doc_present_builders_risk_coverage_endorsement": ["Builders_Risk_Coverage_Endorsement"],
    "doc_present_draw_disbursement_notification_indemnity": ["Draw_Disbursement_Notification_Indemnity"],
    "doc_present_esign_notice_of_completion": ["eSign_Notice_of_Completion"],
    "doc_present_exterior_only_appraisal_personal_inspection_cert": ["Exterior_Only_Appraisal_Personal_Inspection_Cert"],
    "doc_present_family_member_employer_tax_returns": ["Family_Member_Employer_Tax_Returns"],
    "doc_present_federal_tax_payment_proof": ["Federal_Tax_Payment_Proof"],
    "doc_present_flood_cert_life_of_loan": ["Life_of_Loan_Flood_Cert"],
    "doc_present_form_1076a": ["Form_1076A"],
    "doc_present_questionnaire_approval_worksheet": ["Questionnaire_Approval_Worksheet"],
    "doc_present_hoa_meeting_minutes": ["HOA_Meeting_Minutes"],
    "doc_present_icpl": ["ICPL"],
    "doc_present_grant_funds_award_letter": ["Grant_Funds_Award_Letter"],
    "doc_present_interest_dividend_income_documentation": ["Interest_Dividend_Income_Documentation"],
    "doc_present_irs_4506c_response": ["IRS_4506C_Response"],
    "doc_present_non_monthly_payment_agreement": ["Non_Monthly_Payment_Agreement"],
    "doc_present_nonprofit_ida_documentation": ["Nonprofit_IDA_Documentation"],
    "doc_present_ny_cema_form_3172": ["NY_CEMA_Form_3172"],
    "doc_present_arb_approval": ["ARB_Approval"],
    "doc_present_project_approval_certificate": ["General_Project_Approval_Certificate"],
    "doc_present_public_assistance_agency_letter": ["Public_Assistance_Agency_Letter"],
    "doc_present_rent_credit_option_purchase_receipts": ["Rent_Credit_Option_Purchase_Receipts"],
    "doc_present_rent_credit_option_purchase_lease_docs": ["Rent_Credit_Option_Purchase_Lease"],
    "doc_present_rin_av_recording": ["RIN_AV_Recording"],
    "doc_present_rov_disclosure_at_application": ["ROV_Disclosure_At_Application"],
    "doc_present_signature_name_affidavit": ["Signature_Name_Affidavit"],
    "doc_present_construction_perm_conversion_rider": ["Construction_Perm_Conversion_Rider"],
    "doc_present_tax_return_or_4868": ["Tax_Return_Or_4868"],
    "doc_present_tax_returns_foreign_income": ["Foreign_Income_Tax_Returns"],
    "doc_present_private_bank_exception_approval": ["Private_Bank_Exception_Approval"],
    "doc_present_dd214": ["DD214"],
    "doc_present_note_allonge": ["Note_Allonge"],
    "doc_present_va_project_approval_certificate": ["VA_Project_Approval_Certificate"],

    # Track F round 2 (2026-07-29): 11 more document types, discovered by
    # re-running the same candidate sweep against the CORRECT applicability
    # map (result/rules/post_closing_only_applicability.json) instead of the
    # incomplete comprehensive_applicability.json round 1's sweep mistakenly
    # used (that file silently drops 1,260 of 3,203 v8 check_ids as keys,
    # which is how du-uw-findings-report-present and
    # homeready-income-limits-present -- both explicitly named in the
    # original Track F plan -- fell out of round 1's candidate pool
    # entirely). Same caveat as the 43 above: none of these 11 documents
    # exists anywhere across the 5 synthetic loans (re-confirmed against the
    # real demo/syn/ corpus this round, same 28 real filenames as round 1),
    # and every substring below was checked pairwise against all 43 round-1
    # substrings, the 7 pre-existing substrings, each other, and all 28 real
    # filenames for accidental containment -- no collisions found. Still a
    # best-guess, never-yet-verified-against-a-real-filename pattern for the
    # same reason as round 1: no example of the real document exists in this
    # project's corpus to check the guess against.
    "doc_present_business_open_confirmation": ["Business_Open_Confirmation"],
    "doc_present_gaar_worksheet": ["GAAR_Worksheet"],
    "doc_present_disaster_repair_documentation": ["Disaster_Repair_Documentation"],
    "doc_present_du_uw_findings_report": ["DU_UW_Findings_Report"],
    "doc_present_appraisal_subject_to_completion_docs": ["Appraisal_Subject_To_Completion"],
    "doc_present_fha_late_endorsement_request": ["FHA_Late_Endorsement_Request"],
    "doc_present_cohabitation_certification": ["Cohabitation_Certification"],
    "doc_present_homeready_income_limits": ["HomeReady_Income_Limits"],
    "doc_present_nat_uw_mgr_approval_email": ["Nat_UW_Mgr_Approval_Email"],
    "doc_present_sales_contract": ["Sales_Contract"],
    "doc_present_portfolio_rep_exception_approval": ["Portfolio_Rep_Exception_Approval"],
}


def _derive_document_presence_facts(loan_folder: str) -> Dict[str, str]:
    filenames = os.listdir(loan_folder)
    facts: Dict[str, str] = {}
    for fact_name, substrings in _DOCUMENT_PRESENCE_SUBSTRINGS.items():
        present = any(sub in fn for fn in filenames for sub in substrings)
        facts[fact_name] = "true" if present else "false"
    return facts


# Field names _derive_date_diff_fields() computes (not doc-extracted -- no
# citation applies). test_fixture_generation.py's citation-completeness
# invariants exclude these by name rather than relaxing "truth implies
# citation" for every field.
DERIVED_FIELD_NAMES = frozenset({
    "appraisal_staleness_days",
    "nov_days_after_closing",
})


def _parse_mmddyyyy(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%m/%d/%Y")
    except ValueError:
        return None


def _derive_date_diff_fields(fields: Dict[str, Any]) -> Dict[str, Any]:
    """Two engine check-kinds already built (003a predicate, 003b
    ratio_threshold field_value) can only compare a field's own truth value
    against a threshold -- neither computes a date difference between TWO
    doc-sourced date fields. Rather than add a new engine ratio mode for what
    is genuinely a fixture-side derivation (both inputs are already-resolved
    doc truth, no new extraction or engine logic needed), compute the day-gap
    as its own numeric field here -- same precedent as _derive_facts(), just
    landing in fields{} (not facts{}) so ratio_threshold's existing
    ratio="field_value" mode (which reads loan.get(field_name), i.e. fields,
    not facts) can check it with zero engine changes.

    No citation is attached: the value is computed from two documents, not
    read from one, so there is no single page/segment to cite (mirrors the
    DocCitation contract -- one citation, one source document)."""
    derived: Dict[str, Any] = {}

    appraisal_dt = _parse_mmddyyyy(
        (fields.get("appraisal_effective_date") or {}).get("truth"))
    closing_dt = _parse_mmddyyyy((fields.get("closing_date") or {}).get("truth"))
    if appraisal_dt is not None and closing_dt is not None:
        derived["appraisal_staleness_days"] = {
            "truth": str((closing_dt - appraisal_dt).days),
            "sources": {}, "citation": None, "doc_confidence": None,
        }

    nov_dt = _parse_mmddyyyy((fields.get("notice_of_value_date") or {}).get("truth"))
    if nov_dt is not None and closing_dt is not None:
        derived["nov_days_after_closing"] = {
            "truth": str((nov_dt - closing_dt).days),
            "sources": {}, "citation": None, "doc_confidence": None,
        }

    return derived


def _derive_facts(fields: Dict[str, Any]) -> Dict[str, Any]:
    """qc_engine/engine.py's ratio_threshold="ltv" check reads loan.facts, not
    loan.fields -- a distinct data path build_fixtures.py had always left
    empty, so chk-ltv-max resolved NOT_APPLICABLE for every document-derived
    loan regardless of how complete fields{} was. Derives the two facts keys
    golden.py's own boundary-loan fixtures use ("loan_amount", "property_value")
    from the already-resolved fields, preferring the document truth (Principle
    V) and falling back to the system side only if no doc value exists -- never
    fabricated, just resolved from data already extracted above."""
    facts: Dict[str, Any] = {}
    for fact_name, field_name in (("loan_amount", "loan_amount"),
                                   ("property_value", "property_value")):
        entry = fields.get(field_name)
        if not entry:
            continue
        value = entry["truth"] if entry["truth"] is not None else entry["sources"].get("mismo")
        if value is not None:
            facts[fact_name] = str(value)
    return facts


def build_all_fixtures() -> Dict[str, str]:
    """Build and write all 5 fixtures. Returns {loan_folder_name: output_path}."""
    written = {}
    for loan_folder_name in sorted(LOAN_PACKAGES):
        fixture = build_loan_fixture(loan_folder_name)
        out_name = "loan_{0}.json".format(loan_folder_name.split(" ")[1])
        out_path = os.path.join(HERE, out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(fixture, f, indent=2, sort_keys=True)
            f.write("\n")
        written[loan_folder_name] = out_path
    return written


if __name__ == "__main__":
    for name, path in build_all_fixtures().items():
        print("{0} -> {1}".format(name, path))
