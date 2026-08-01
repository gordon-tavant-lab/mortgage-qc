#!/usr/bin/env python3
"""
Quick adapter: Touchless → AMQ (current custom schema)
Goal: Get audit running TODAY, optimize later
"""
import json
import sys
from datetime import datetime
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

LI = Namespace("http://mortgage.audit.ontology/loan-instance#")

def ts_to_date(ts_ms):
    if not ts_ms:
        return None
    return datetime.fromtimestamp(ts_ms / 1000).strftime("%Y-%m-%d")

def typed_literal(value, kind=None):
    if isinstance(value, bool):
        return Literal(value)
    if isinstance(value, (int, float)):
        return Literal(str(value), datatype=XSD.decimal)
    if kind == "date":
        return Literal(value, datatype=XSD.date)
    return Literal(str(value))

def convert_touchless_to_amq(loan_app_path):
    with open(loan_app_path) as f:
        loan_app = json.load(f)

    g = Graph()
    g.bind("li", LI)

    loan_summary = loan_app.get("loanSummary", {})
    loan_id = loan_summary.get("lenderCaseIdentifier", "UNKNOWN")
    loan_node = URIRef(LI["loan_" + loan_id.replace("-", "_")])

    g.add((loan_node, RDF.type, LI.LoanInstance))
    g.add((loan_node, LI.loan_id, Literal(loan_id)))

    # Loan terms
    loan_terms = loan_summary.get("loanTerms", {})
    if loan_terms.get("baseLoanAmount"):
        g.add((loan_node, LI.loan_amount, typed_literal(loan_terms["baseLoanAmount"])))
        g.add((loan_node, LI.mismo_loan_amount, typed_literal(loan_terms["baseLoanAmount"])))
    
    if loan_terms.get("mortgageType"):
        g.add((loan_node, LI.loan_program_1003, Literal(loan_terms["mortgageType"])))
        g.add((loan_node, LI.mismo_mortgage_type, Literal(loan_terms["mortgageType"])))
    
    if loan_terms.get("loanPurposeType"):
        g.add((loan_node, LI.loan_purpose_1003, Literal(loan_terms["loanPurposeType"])))
        g.add((loan_node, LI.mismo_loan_purpose, Literal(loan_terms["loanPurposeType"])))
    
    if loan_terms.get("interestRate"):
        g.add((loan_node, LI.mismo_note_rate, typed_literal(loan_terms["interestRate"])))

    # Qualification/ratios
    qual = loan_summary.get("qualification", {})
    if qual.get("totalDebtExpenseRatioPercent"):
        g.add((loan_node, LI.dti_ratio, typed_literal(qual["totalDebtExpenseRatioPercent"])))
    
    if qual.get("housingExpenseRatioPercent"):
        g.add((loan_node, LI.housing_ratio, typed_literal(qual["housingExpenseRatioPercent"])))
    
    if qual.get("totalMonthlyIncomeAmount"):
        g.add((loan_node, LI.mismo_total_monthly_income, typed_literal(qual["totalMonthlyIncomeAmount"])))
    
    if qual.get("totalLiabilitiesMonthlyPaymentAmount"):
        g.add((loan_node, LI.mismo_total_liabilities_pmt, typed_literal(qual["totalLiabilitiesMonthlyPaymentAmount"])))

    # LTV
    ltv_ratio = loan_summary.get("ltvRatio", {})
    if ltv_ratio.get("ltv"):
        g.add((loan_node, LI.ltv, typed_literal(ltv_ratio["ltv"])))
    if ltv_ratio.get("cltv"):
        g.add((loan_node, LI.cltv, typed_literal(ltv_ratio["cltv"])))

    # FICO
    if loan_summary.get("fico"):
        g.add((loan_node, LI.credit_score_1003, Literal(str(int(loan_summary["fico"])))))

    # Dates
    if loan_summary.get("applicationDate"):
        app_date = ts_to_date(loan_summary["applicationDate"])
        if app_date:
            g.add((loan_node, LI.application_date, typed_literal(app_date, "date")))

    closing_info = loan_summary.get("closingInformation", {})
    if closing_info.get("loanEstimatedClosingDate"):
        close_date = ts_to_date(closing_info["loanEstimatedClosingDate"])
        if close_date:
            g.add((loan_node, LI.closing_date, typed_literal(close_date, "date")))

    # Borrower
    borrower_pairs = loan_app.get("borrowersDetail", {}).get("borrowerPairs", [])
    if borrower_pairs and borrower_pairs[0].get("borrowers"):
        borrower = borrower_pairs[0]["borrowers"][0]
        
        name_parts = []
        if borrower.get("firstName"):
            name_parts.append(borrower["firstName"])
        if borrower.get("lastName"):
            name_parts.append(borrower["lastName"])
        if name_parts:
            g.add((loan_node, LI.borrower_name, Literal(" ".join(name_parts))))

        employers = borrower.get("employers", [])
        if employers:
            emp = employers[0]
            if emp.get("employerName"):
                g.add((loan_node, LI.employer_name_1003, Literal(emp["employerName"])))
            
            employment = emp.get("employment", {})
            if employment.get("employmentStartDate"):
                start_date = ts_to_date(employment["employmentStartDate"])
                if start_date:
                    g.add((loan_node, LI.employment_start_date_1003, typed_literal(start_date, "date")))
            
            income_list = emp.get("income", [])
            if income_list and income_list[0].get("monthlyIncome"):
                g.add((loan_node, LI.base_monthly_income_1003, typed_literal(income_list[0]["monthlyIncome"])))
            
            ownership = employment.get("ownershipInterestType", "")
            is_se = employment.get("isSelfEmployed")
            if is_se or "25Percent" in ownership:
                g.add((loan_node, LI.borrower_self_employed, Literal(True)))

    # Property
    collateral = loan_app.get("collateralDetail", {}).get("collateral", [])
    if collateral:
        prop = collateral[0]
        addr = prop.get("propertyAddress", {})
        if addr.get("state"):
            g.add((loan_node, LI.property_state, Literal(addr["state"])))
        
        appraisal = prop.get("appraisal", {})
        if appraisal.get("appraisedValue"):
            g.add((loan_node, LI.appraised_value, typed_literal(appraisal["appraisedValue"])))
        
        if appraisal.get("appraisalEffectiveDate"):
            appr_date = ts_to_date(appraisal["appraisalEffectiveDate"])
            if appr_date:
                g.add((loan_node, LI.appraisal_effective_date, typed_literal(appr_date, "date")))
        
        prop_detail = prop.get("propertyDetail", {})
        if prop_detail.get("yearBuilt"):
            g.add((loan_node, LI.property_year_built, Literal(str(prop_detail["yearBuilt"]))))

    # Documents - map to doc_present_* facts
    documents = loan_app.get("documents", [])
    doc_types = set(doc.get("documentType") for doc in documents if doc.get("documentType"))
    
    # Map common document types
    doc_mapping = {
        "Credit Report": "doc_present_credit_report",
        "Paystub": "doc_present_paystub",
        "W2": "doc_present_w2",
        "Form 1040": "doc_present_1040",
        "Form 1040 - Schedule C": "doc_present_schedule_c",
        "Form 1004 Uniform Residential Appraisal": "doc_present_appraisal",
        "URLA - Borrower Information": "doc_present_1003",
        "Closing Disclosure": "doc_present_closing_disclosure",
        "Title Commitment": "doc_present_title_commitment",
        "Gift Letter": "doc_present_gift_letter",
        "Hazard Insurance": "doc_present_hazard_insurance",
        "Bank Statement": "doc_present_bank_statement",
    }
    
    for doc_type, field_name in doc_mapping.items():
        g.add((loan_node, LI[field_name], Literal(doc_type in doc_types)))

    return g, loan_node

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 touchless_to_amq_quick.py <loan_application.json> <output.ttl>")
        sys.exit(1)

    graph, loan = convert_touchless_to_amq(sys.argv[1])
    graph.serialize(destination=sys.argv[2], format="turtle")
    print(f"✓ Wrote {len(graph)} triples to {sys.argv[2]}")
    print(f"✓ Loan: {loan}")
