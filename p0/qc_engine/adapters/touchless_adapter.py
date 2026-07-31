"""
Touchless loan payload -> qc_engine fixture JSON (the shape
`p0/fixtures/from_docs/fixture_loader.py::load_canonical_loan()` reads).

Bake-off counterpart to `src/shacl_pilot/touchless_adapter.py` (Pipeline A's
adapter for the same input). Field-for-field mirrors that adapter's coverage
so both engines see identical input data from `demo/touchless/extracted/` --
that symmetry is the fairness requirement for the p0-vs-src bake-off
(see the plan at `/Users/gordonchan/.claude/plans/1-no-no-this-iridescent-brooks.md`).

Adds six applicability-gating fields (`Loans.QC_Policy` etc.) the gold
ruleset's `applicability.all_of`/`any_of` conditions read, which the SHACL
adapter has no equivalent of (that pipeline gates applicability outside the
adapter, in `run_full_ruleset_audit.py`'s Python layer).

`QC_Policy` is set to the literal "Fannie Mae" rather than left unknown: the
Touchless payload's `investor` field is null for this loan, but the gold
ruleset itself is scoped to Fannie Mae conventional only (the SME would only
ever assign this ruleset's route to a loan already known to be on that
program) -- this is a documented experiment assumption, not a guess made to
force checks to fire. `Underwriting_Type` is left genuinely unknown (the
payload's `duStatus`/`underwriting`/`lpaApproved` are all null) so
`applies_if` resolves it as `NEEDS_REVIEW` (APPLICABILITY_UNKNOWN), never a
silent guess -- matching this project's "never gate on a null field"
discipline.

Python 3.9 compatible.
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, Optional


def _ts_to_date(ts_ms: Optional[float]) -> Optional[str]:
    if not ts_ms:
        return None
    return datetime.fromtimestamp(ts_ms / 1000).strftime("%Y-%m-%d")


def _citation(source: str, confidence: Optional[float] = None) -> Dict[str, Any]:
    """Mirrors src/shacl_pilot/touchless_adapter.py::cite_touchless() --
    same honesty limits: this payload carries no PDF, no page, no bounding
    box (`documentLocation` is null throughout), so the citation is a
    JSON-path breadcrumb into the Touchless payload itself, not a real
    document/page. Never claim a page number that doesn't exist."""
    snippet = f"Touchless extraction: {source}"
    if confidence is not None:
        snippet += f" (confidence: {confidence})"
    return {
        "doc_name": "Touchless API",
        "page_num": 0,
        "segment_snippet": snippet[:200],
    }


def _field(value: Any, citation_source: str, confidence: Optional[float] = None) -> Dict[str, Any]:
    return {"truth": value, "sources": {}, "citation": _citation(citation_source, confidence)}


def adapt_touchless_to_fixture(loan_app_path: str, extracted_data_path: str) -> Dict[str, Any]:
    with open(loan_app_path, "r", encoding="utf-8") as f:
        loan_app = json.load(f)
    with open(extracted_data_path, "r", encoding="utf-8") as f:
        extracted_data = json.load(f)

    fields: Dict[str, Any] = {}
    facts: Dict[str, Any] = {}

    loan_summary = loan_app.get("loanSummary", {}) or {}
    loan_terms = loan_summary.get("loanTerms", {}) or {}
    loan_id = loan_summary.get("lenderCaseIdentifier") or loan_app.get("loanId") or "UNKNOWN"

    # --- loan terms ---------------------------------------------------
    if loan_terms.get("loanPurposeType"):
        fields["loan_purpose_1003"] = _field(loan_terms["loanPurposeType"], "loanTerms.loanPurposeType")
        # Loans.LoanPurposeType condition values are title-cased ("Purchase");
        # the payload's are upper-cased ("PURCHASE") -- normalize for the
        # applies_if gate, keep the raw value for the display field above.
        fields["Loans.LoanPurposeType"] = _field(
            str(loan_terms["loanPurposeType"]).title(), "loanTerms.loanPurposeType (normalized)")

    if loan_terms.get("mortgageType"):
        fields["loan_program_1003"] = _field(loan_terms["mortgageType"], "loanTerms.mortgageType")
        fields["mismo_mortgage_type"] = _field(loan_terms["mortgageType"], "loanTerms.mortgageType")
        fields["Loans.LoanType"] = _field(
            str(loan_terms["mortgageType"]).title(), "loanTerms.mortgageType (normalized)")

    if loan_terms.get("baseLoanAmount"):
        fields["mismo_loan_amount"] = _field(float(loan_terms["baseLoanAmount"]), "loanTerms.baseLoanAmount")

    if loan_terms.get("interestRate"):
        fields["mismo_note_rate"] = _field(float(loan_terms["interestRate"]), "loanTerms.interestRate")

    app_date_ts = loan_summary.get("applicationDate")
    if app_date_ts:
        fields["application_date"] = _field(_ts_to_date(app_date_ts), "loanSummary.applicationDate")

    # --- qualification / ratios ----------------------------------------
    qual = loan_summary.get("qualification", {}) or {}
    if qual.get("totalMonthlyIncomeAmount"):
        fields["mismo_total_monthly_income"] = _field(
            float(qual["totalMonthlyIncomeAmount"]), "qualification.totalMonthlyIncomeAmount")
    if qual.get("housingExpenseRatioPercent"):
        fields["housing_ratio"] = _field(
            float(qual["housingExpenseRatioPercent"]), "qualification.housingExpenseRatioPercent")
    if qual.get("totalDebtExpenseRatioPercent"):
        fields["dti_ratio"] = _field(
            float(qual["totalDebtExpenseRatioPercent"]), "qualification.totalDebtExpenseRatioPercent")

    ltv_ratio = loan_summary.get("ltvRatio", {}) or {}
    if ltv_ratio.get("ltv"):
        fields["ltv"] = _field(float(ltv_ratio["ltv"]), "ltvRatio.ltv")

    if loan_summary.get("fico"):
        fields["credit_score_1003"] = _field(str(int(loan_summary["fico"])), "loanSummary.fico")

    # --- borrower / employment ------------------------------------------
    borrower_pairs = (loan_app.get("borrowersDetail", {}) or {}).get("borrowerPairs", []) or []
    if borrower_pairs:
        borrowers_list = borrower_pairs[0].get("borrowers", []) or []
        if borrowers_list:
            borrower = borrowers_list[0]
            name_parts = [borrower.get(k) for k in ("firstName", "middleName", "lastName") if borrower.get(k)]
            if name_parts:
                fields["borrower_name"] = _field(" ".join(name_parts), "borrowersDetail.borrowerPairs[0].borrowers[0]")

            employers = borrower.get("employers", []) or []
            if employers:
                emp = employers[0]
                if emp.get("employerName"):
                    fields["employer_name_1003"] = _field(emp["employerName"], "employers[0].employerName")

                employment = emp.get("employment", {}) or {}
                if employment.get("employmentStartDate"):
                    fields["employment_start_date_1003"] = _field(
                        _ts_to_date(employment["employmentStartDate"]),
                        "employers[0].employment.employmentStartDate")

                income_list = emp.get("income", []) or []
                if income_list and income_list[0].get("monthlyIncome"):
                    fields["base_monthly_income_1003"] = _field(
                        float(income_list[0]["monthlyIncome"]), "employers[0].income[0].monthlyIncome")

                ownership = employment.get("ownershipInterestType", "") or ""
                is_se = employment.get("isSelfEmployed")
                if is_se or "25Percent" in ownership:
                    facts["borrower_self_employed"] = True

    # --- property / collateral ------------------------------------------
    collateral = (loan_app.get("collateralDetail", {}) or {}).get("collateral", []) or []
    if collateral:
        prop = collateral[0]
        prop_detail = prop.get("propertyDetail", {}) or {}
        addr = prop_detail.get("propertyAddress", {}) or {}

        if addr.get("stateCode"):
            fields["property_state"] = _field(addr["stateCode"], "propertyDetail.propertyAddress.stateCode")
            fields["Loans.AddressState"] = _field(addr["stateCode"], "propertyDetail.propertyAddress.stateCode")

        if prop_detail.get("attachmentType"):
            # Not a direct match to gold's PropertyType vocabulary (Condo/PUD/
            # Co-op/2-4 unit) -- "Detached"/"Attached" describes a different
            # axis (single-family structure type). Carried through honestly;
            # PropertyType-gated cards correctly resolve NOT_APPLICABLE for a
            # loan whose only signal is "Detached", rather than a guess.
            fields["Loans.PropertyType"] = _field(
                prop_detail["attachmentType"], "propertyDetail.attachmentType")

        appraisal = prop.get("appraisal", {}) or {}
        if appraisal.get("appraisedValue"):
            fields["appraised_value"] = _field(float(appraisal["appraisedValue"]), "appraisal.appraisedValue")
        if appraisal.get("appraisalEffectiveDate"):
            fields["appraisal_effective_date"] = _field(
                _ts_to_date(appraisal["appraisalEffectiveDate"]), "appraisal.appraisalEffectiveDate")

        if prop_detail.get("yearBuilt"):
            fields["property_year_built"] = _field(str(prop_detail["yearBuilt"]), "propertyDetail.yearBuilt")

    # --- extracted document data (Schedule C) ---------------------------
    extracted_by_field: Dict[str, Dict[str, Any]] = {}
    for item in extracted_data:
        name, value, confidence = item.get("name"), item.get("value"), item.get("confidence")
        if name and value:
            extracted_by_field[name] = {"value": value, "confidence": confidence}

    if "Tax_Year" in extracted_by_field:
        fields["tax_year_schedule_c"] = _field(
            extracted_by_field["Tax_Year"]["value"], "Schedule C: Tax_Year",
            extracted_by_field["Tax_Year"]["confidence"])
    if "Gross_Profit" in extracted_by_field:
        fields["gross_profit_schedule_c"] = _field(
            float(extracted_by_field["Gross_Profit"]["value"]), "Schedule C: Gross_Profit",
            extracted_by_field["Gross_Profit"]["confidence"])
    if "Net_Profit" in extracted_by_field:
        fields["net_profit_schedule_c"] = _field(
            float(extracted_by_field["Net_Profit"]["value"]), "Schedule C: Net_Profit",
            extracted_by_field["Net_Profit"]["confidence"])

    # --- credit -----------------------------------------------------------
    credit = loan_app.get("creditDetail", {}) or {}
    credit_score_data = credit.get("creditScore", []) or []
    scores = [s.get("creditRepositorySourceScore") for s in credit_score_data if s.get("creditRepositorySourceScore")]
    if len(scores) >= 2:
        scores_sorted = sorted(int(s) for s in scores)
        middle_score = scores_sorted[len(scores_sorted) // 2]
        fields["credit_score_bureau"] = _field(str(middle_score), f"creditDetail.creditScore middle of {len(scores)} scores")

    # --- applicability-gating fields not covered above ------------------
    # QC_Policy: documented experiment assumption, see module docstring.
    fields["Loans.QC_Policy"] = _field("Fannie Mae", "experiment assumption: gold ruleset is FNM-conventional-only")
    # Underwriting_Type: genuinely unknown on this payload (duStatus/
    # underwriting/lpaApproved are all null) -- deliberately NOT set, so
    # applies_if resolves APPLICABILITY_UNKNOWN rather than a guess.

    # --- curated document-presence fields (added 2026-07-31) ------------
    # Mirrors src/shacl_pilot/touchless_adapter.py's docs_present population
    # from the real documents[] inventory (62 entries, previously discarded
    # here too -- same finding, see output/BAKEOFF-P0-VS-SRC-GOLD-TOUCHLESS-
    # 2026-07-31.md). Only the 5 individually hand-verified matches in
    # p0/qc_engine/compiler/import_gold_ruleset.py's CURATED_DOC_MATCHES are
    # wired to a Check -- populate all 5 as real boolean-ish presence fields
    # here (`truth` = the real documentId when present, so is_present's
    # `sv.doc is not None` check resolves PASS; simply never set the field
    # for a document confirmed absent, so is_present's None-check correctly
    # resolves FAIL -- never set truth=False, since str(False) is a
    # non-empty string and would incorrectly resolve PASS under is_present's
    # actual semantics, engine.py line ~347).
    _CURATED_DOC_TYPES = {
        "doc_present_gift_letter": "Gift Letter",
        "doc_present_credit_report": "Credit Report",
        "doc_present_hazard_insurance": "Hazard Insurance",
        "doc_present_title_commitment": "Title Commitment",
        "doc_present_flood_hazard_determination": "Flood Hazard Determination",
    }
    docs_by_type = {}
    for doc in loan_app.get("documents", []) or []:
        dtype = doc.get("documentType")
        if dtype:
            docs_by_type.setdefault(dtype, doc.get("documentId"))
    for field_name, doc_type in _CURATED_DOC_TYPES.items():
        if doc_type in docs_by_type:
            fields[field_name] = _field(
                docs_by_type[doc_type] or "present",
                "documents[] entry with documentType=%s" % doc_type)
        # else: deliberately not set -- is_present resolves FAIL, honestly.

    return {
        "loan_id": str(loan_id),
        "loan_type": "CONVENTIONAL",
        "fields": fields,
        "facts": facts,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print(__doc__)
        print("\nUsage: python3 touchless_adapter.py <loan_application.json> <extracted_data.json> <output.json>")
        sys.exit(1)

    result = adapt_touchless_to_fixture(sys.argv[1], sys.argv[2])
    with open(sys.argv[3], "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1, sort_keys=True)

    print("Converted Touchless data to qc_engine fixture format:")
    print(f"  Loan ID: {result['loan_id']}")
    print(f"  Fields:  {len(result['fields'])}")
    print(f"  Facts:   {len(result['facts'])}")
    print(f"  Output:  {sys.argv[3]}")
