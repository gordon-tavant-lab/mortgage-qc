#!/usr/bin/env python3
"""
Touchless → AMQ RDF Converter

Converts Touchless API JSON to AMQ-compatible RDF format (li: namespace).
Uses AMQ field naming conventions so existing SHACL shapes can validate.
"""
import json
import sys
from datetime import datetime
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

# AMQ namespace (matches existing shapes)
LI = Namespace("http://mortgage.audit.ontology/loan-instance#")

def ts_to_date(ts_ms):
    """Convert timestamp in milliseconds to ISO date."""
    if not ts_ms:
        return None
    return datetime.fromtimestamp(ts_ms / 1000).strftime("%Y-%m-%d")

def typed_literal(value, kind=None):
    """Convert value to typed literal."""
    if isinstance(value, bool):
        return Literal(value)
    if isinstance(value, (int, float)):
        return Literal(str(value), datatype=XSD.decimal)
    if kind == "date":
        return Literal(value, datatype=XSD.date)
    return Literal(str(value))

def add_citation(g, subject, prop_name, source):
    """Add Touchless API citation."""
    node = URIRef(str(subject) + "__cite_" + prop_name)
    g.add((subject, LI["cite_" + prop_name], node))
    g.add((node, RDF.type, LI.Citation))
    g.add((node, LI.doc_name, Literal("Touchless API")))
    g.add((node, LI.page, Literal(0)))
    g.add((node, LI.snippet, Literal(f"Touchless: {source}"[:160])))

def convert_touchless_to_amq_rdf(loan_app_path, extracted_data_path=None):
    """Convert Touchless JSON → AMQ-compatible RDF."""

    with open(loan_app_path) as f:
        loan_app = json.load(f)

    # Optional document extraction data
    extracted_data = []
    if extracted_data_path:
        with open(extracted_data_path) as f:
            extracted_data = json.load(f)

    g = Graph()
    g.bind("li", LI)

    # Loan ID
    loan_summary = loan_app.get("loanSummary", {})
    loan_id = loan_summary.get("lenderCaseIdentifier", loan_app.get("loanId", "UNKNOWN"))
    loan_node = URIRef(LI["loan_" + loan_id.replace("-", "_").replace("{", "").replace("}", "")])

    g.add((loan_node, RDF.type, LI.LoanInstance))
    g.add((loan_node, LI.loan_id, Literal(loan_id)))
    add_citation(g, loan_node, "loan_id", "loanSummary.lenderCaseIdentifier")

    # --- LOAN TERMS ---
    loan_terms = loan_summary.get("loanTerms", {})

    # Loan amount
    if loan_terms.get("baseLoanAmount"):
        g.add((loan_node, LI.loan_amount, typed_literal(loan_terms["baseLoanAmount"])))
        g.add((loan_node, LI.mismo_loan_amount, typed_literal(loan_terms["baseLoanAmount"])))
        add_citation(g, loan_node, "loan_amount", "loanTerms.baseLoanAmount")

    # Loan program
    if loan_terms.get("mortgageType"):
        g.add((loan_node, LI.loan_program_1003, Literal(loan_terms["mortgageType"])))
        g.add((loan_node, LI.mismo_mortgage_type, Literal(loan_terms["mortgageType"])))
        add_citation(g, loan_node, "loan_program_1003", "loanTerms.mortgageType")

    # Loan purpose
    if loan_terms.get("loanPurposeType"):
        g.add((loan_node, LI.loan_purpose_1003, Literal(loan_terms["loanPurposeType"])))
        g.add((loan_node, LI.mismo_loan_purpose, Literal(loan_terms["loanPurposeType"])))
        add_citation(g, loan_node, "loan_purpose_1003", "loanTerms.loanPurposeType")

    # Interest rate
    if loan_terms.get("interestRate"):
        g.add((loan_node, LI.mismo_note_rate, typed_literal(loan_terms["interestRate"])))
        add_citation(g, loan_node, "mismo_note_rate", "loanTerms.interestRate")

    # --- QUALIFICATION / RATIOS ---
    qual = loan_summary.get("qualification", {})

    if qual.get("totalDebtExpenseRatioPercent"):
        g.add((loan_node, LI.dti_ratio, typed_literal(qual["totalDebtExpenseRatioPercent"])))
        add_citation(g, loan_node, "dti_ratio", "qualification.totalDebtExpenseRatioPercent")

    if qual.get("housingExpenseRatioPercent"):
        g.add((loan_node, LI.housing_ratio, typed_literal(qual["housingExpenseRatioPercent"])))
        add_citation(g, loan_node, "housing_ratio", "qualification.housingExpenseRatioPercent")

    if qual.get("totalMonthlyIncomeAmount"):
        g.add((loan_node, LI.mismo_total_monthly_income, typed_literal(qual["totalMonthlyIncomeAmount"])))
        add_citation(g, loan_node, "mismo_total_monthly_income", "qualification.totalMonthlyIncomeAmount")

    if qual.get("totalLiabilitiesMonthlyPaymentAmount"):
        g.add((loan_node, LI.mismo_total_liabilities_pmt, typed_literal(qual["totalLiabilitiesMonthlyPaymentAmount"])))
        add_citation(g, loan_node, "mismo_total_liabilities_pmt", "qualification.totalLiabilitiesMonthlyPaymentAmount")

    # --- LTV RATIOS ---
    ltv_ratio = loan_summary.get("ltvRatio", {})

    if ltv_ratio.get("ltv"):
        g.add((loan_node, LI.ltv, typed_literal(ltv_ratio["ltv"])))
        add_citation(g, loan_node, "ltv", "ltvRatio.ltv")

    if ltv_ratio.get("cltv"):
        g.add((loan_node, LI.cltv, typed_literal(ltv_ratio["cltv"])))
        add_citation(g, loan_node, "cltv", "ltvRatio.cltv")

    # --- FICO ---
    if loan_summary.get("fico"):
        g.add((loan_node, LI.credit_score_1003, Literal(str(int(loan_summary["fico"])))))
        add_citation(g, loan_node, "credit_score_1003", "loanSummary.fico")

    # --- DATES ---
    if loan_summary.get("applicationDate"):
        app_date = ts_to_date(loan_summary["applicationDate"])
        if app_date:
            g.add((loan_node, LI.application_date, typed_literal(app_date, "date")))
            add_citation(g, loan_node, "application_date", "loanSummary.applicationDate")

    closing_info = loan_summary.get("closingInformation", {})
    if closing_info.get("loanEstimatedClosingDate"):
        close_date = ts_to_date(closing_info["loanEstimatedClosingDate"])
        if close_date:
            g.add((loan_node, LI.closing_date, typed_literal(close_date, "date")))
            add_citation(g, loan_node, "closing_date", "closingInformation.loanEstimatedClosingDate")

    # --- BORROWER ---
    borrower_pairs = loan_app.get("borrowersDetail", {}).get("borrowerPairs", [])
    if borrower_pairs:
        borrowers_list = borrower_pairs[0].get("borrowers", [])
        if borrowers_list:
            borrower = borrowers_list[0]

            # Name
            name_parts = []
            if borrower.get("firstName"):
                name_parts.append(borrower["firstName"])
            if borrower.get("lastName"):
                name_parts.append(borrower["lastName"])
            if name_parts:
                g.add((loan_node, LI.borrower_name, Literal(" ".join(name_parts))))
                add_citation(g, loan_node, "borrower_name", "borrowersDetail.borrowerPairs[0].borrowers[0]")

            # Employment
            employers = borrower.get("employers", [])
            if employers:
                emp = employers[0]

                if emp.get("employerName"):
                    g.add((loan_node, LI.employer_name_1003, Literal(emp["employerName"])))
                    add_citation(g, loan_node, "employer_name_1003", "employers[0].employerName")

                employment = emp.get("employment", {})
                if employment.get("employmentStartDate"):
                    start_date = ts_to_date(employment["employmentStartDate"])
                    if start_date:
                        g.add((loan_node, LI.employment_start_date_1003, typed_literal(start_date, "date")))
                        add_citation(g, loan_node, "employment_start_date_1003", "employers[0].employment.employmentStartDate")

                # Income
                income_list = emp.get("income", [])
                if income_list and income_list[0].get("monthlyIncome"):
                    g.add((loan_node, LI.base_monthly_income_1003, typed_literal(income_list[0]["monthlyIncome"])))
                    add_citation(g, loan_node, "base_monthly_income_1003", "employers[0].income[0].monthlyIncome")

                # Self-employed
                ownership = employment.get("ownershipInterestType", "")
                is_se = employment.get("isSelfEmployed")
                if is_se or "25Percent" in ownership:
                    g.add((loan_node, LI.borrower_self_employed, Literal(True)))
                    add_citation(g, loan_node, "borrower_self_employed", f"employment.ownershipInterestType: {ownership}")

    # --- PROPERTY / COLLATERAL ---
    collateral = loan_app.get("collateralDetail", {}).get("collateral", [])
    if collateral:
        prop = collateral[0]

        # Address
        addr = prop.get("propertyAddress", {})
        if addr.get("state"):
            g.add((loan_node, LI.property_state, Literal(addr["state"])))
            add_citation(g, loan_node, "property_state", "collateralDetail.collateral[0].propertyAddress.state")

        # Appraisal
        appraisal = prop.get("appraisal", {})
        if appraisal.get("appraisedValue"):
            g.add((loan_node, LI.appraised_value, typed_literal(appraisal["appraisedValue"])))
            add_citation(g, loan_node, "appraised_value", "appraisal.appraisedValue")

        if appraisal.get("appraisalEffectiveDate"):
            appr_date = ts_to_date(appraisal["appraisalEffectiveDate"])
            if appr_date:
                g.add((loan_node, LI.appraisal_effective_date, typed_literal(appr_date, "date")))
                add_citation(g, loan_node, "appraisal_effective_date", "appraisal.appraisalEffectiveDate")

        # Property details
        prop_detail = prop.get("propertyDetail", {})
        if prop_detail.get("yearBuilt"):
            g.add((loan_node, LI.property_year_built, Literal(str(prop_detail["yearBuilt"]))))
            add_citation(g, loan_node, "property_year_built", "propertyDetail.yearBuilt")

    return g, loan_node

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        print("\nUsage: python3 touchless_to_amq_rdf.py <loan_application.json> <output.ttl> [extracted_data.json]")
        sys.exit(1)

    extracted_path = sys.argv[3] if len(sys.argv) > 3 else None
    graph, loan = convert_touchless_to_amq_rdf(sys.argv[1], extracted_path)

    graph.serialize(destination=sys.argv[2], format="turtle")
    print(f"✓ Wrote {len(graph)} triples to {sys.argv[2]}")
    print(f"✓ Loan node: {loan}")
    print(f"\n--- Sample (first 20 lines) ---")
    with open(sys.argv[2]) as f:
        for i, line in enumerate(f):
            if i >= 20:
                break
            print(line.rstrip())
