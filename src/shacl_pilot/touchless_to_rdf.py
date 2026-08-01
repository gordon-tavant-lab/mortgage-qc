#!/usr/bin/env python3
"""
Touchless JSON → RDF converter.

Converts Touchless API loan_application.json format into RDF (Turtle).
Direct property mapping (flat structure) + nested entities as child nodes.

USAGE:
  python3 touchless_to_rdf.py <loan_application.json> [extracted_data.json] <output.ttl>

EXAMPLE:
  python3 touchless_to_rdf.py demo/touchless/loan_application.json demo/touchless/loan_12607601215.ttl
"""
import json
import sys
from datetime import datetime, timezone
from typing import Any, Optional

from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

# Namespace
TL = Namespace("http://touchless.audit/loan#")

# High-priority fields that should warn if null
HIGH_PRIORITY_FIELDS = {
    "propertyState",
    "baseLoanAmount",
    "loanPurposeType",
    "lenderCaseIdentifier",
    "borrowerFirstName",
    "borrowerLastName",
}


def milliseconds_to_date(ms: Optional[int]) -> Optional[str]:
    """Convert milliseconds timestamp to YYYY-MM-DD date string."""
    if ms is None:
        return None
    try:
        dt = datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d")
    except (ValueError, OSError):
        return None


def typed_literal(value: Any, datatype: Optional[str] = None) -> Literal:
    """Convert Python value to RDF Literal with appropriate XSD type."""
    if value is None:
        return None

    if isinstance(value, bool):
        return Literal(value, datatype=XSD.boolean)

    if isinstance(value, int):
        return Literal(value, datatype=XSD.integer)

    if isinstance(value, float):
        return Literal(value, datatype=XSD.decimal)

    if datatype == "date":
        return Literal(value, datatype=XSD.date)

    return Literal(str(value), datatype=XSD.string)


def safe_add_triple(g: Graph, subject: URIRef, predicate: URIRef, value: Any,
                   datatype: Optional[str] = None, field_name: Optional[str] = None):
    """Add triple to graph, skipping null values and warning on high-priority nulls."""
    if value is None:
        if field_name and field_name in HIGH_PRIORITY_FIELDS:
            print(f"WARNING: High-priority field '{field_name}' is null", file=sys.stderr)
        return

    lit = typed_literal(value, datatype)
    if lit is not None:
        g.add((subject, predicate, lit))


def add_flat_properties(g: Graph, loan_node: URIRef, data: dict, prefix: str = ""):
    """Add flat properties from a dict to the loan node."""
    for key, value in data.items():
        if value is None:
            continue

        if isinstance(value, dict):
            # Skip nested dicts here; handle separately
            continue

        if isinstance(value, list):
            # Skip lists here; handle separately
            continue

        # Property name with optional prefix
        prop_name = f"{prefix}{key}" if prefix else key

        # Handle timestamp → date conversion
        if key.endswith("Date") or key.endswith("Datetime") or key == "timestamp":
            date_str = milliseconds_to_date(value)
            if date_str:
                safe_add_triple(g, loan_node, TL[prop_name], date_str, datatype="date", field_name=prop_name)
        else:
            safe_add_triple(g, loan_node, TL[prop_name], value, field_name=prop_name)


def add_borrower(g: Graph, loan_node: URIRef, borrower: dict, borrower_num: int):
    """Add borrower as a child node."""
    borrower_id = borrower.get("borrowerId", f"borrower_{borrower_num}")
    borrower_node = URIRef(f"{loan_node}_borrower_{borrower_num}")

    g.add((borrower_node, RDF.type, TL.Borrower))
    g.add((loan_node, TL.hasBorrower, borrower_node))

    # Basic borrower fields
    safe_add_triple(g, borrower_node, TL.borrowerId, borrower_id)
    safe_add_triple(g, borrower_node, TL.firstName, borrower.get("firstName"))
    safe_add_triple(g, borrower_node, TL.lastName, borrower.get("lastName"))
    safe_add_triple(g, borrower_node, TL.middleName, borrower.get("middleName"))
    safe_add_triple(g, borrower_node, TL.ssn, borrower.get("ssn"))
    safe_add_triple(g, borrower_node, TL.isPrimary, borrower.get("isPrimary"))
    safe_add_triple(g, borrower_node, TL.age, borrower.get("age"))

    # Birth date
    birth_date_ms = borrower.get("birthDate")
    if birth_date_ms:
        birth_date = milliseconds_to_date(birth_date_ms)
        if birth_date:
            safe_add_triple(g, borrower_node, TL.birthDate, birth_date, datatype="date")

    # Contact info
    contact = borrower.get("contact", {})
    if contact:
        safe_add_triple(g, borrower_node, TL.email, contact.get("email"))
        safe_add_triple(g, borrower_node, TL.cellPhone, contact.get("cellPhone"))
        safe_add_triple(g, borrower_node, TL.homePhone, contact.get("homePhone"))
        safe_add_triple(g, borrower_node, TL.workPhone, contact.get("workPhone"))

    # Borrower detail
    detail = borrower.get("borrowerDetail", {})
    if detail:
        safe_add_triple(g, borrower_node, TL.maritalStatusType, detail.get("maritalStatusType"))
        safe_add_triple(g, borrower_node, TL.dependentCount, detail.get("dependentCount"))

    # Credit scores
    scores = borrower.get("creditScores", {})
    if scores:
        for bureau, score_data in scores.items():
            if score_data and isinstance(score_data, dict):
                score_val = score_data.get("creditScoreValue")
                if score_val:
                    safe_add_triple(g, borrower_node, TL[f"creditScore{bureau.capitalize()}"], score_val)

    # Income analysis
    income_analysis = borrower.get("incomeAnalysis", {})
    if income_analysis:
        safe_add_triple(g, borrower_node, TL.qualifyingIncome, income_analysis.get("qualifyingIncome"))

    # Employers (embedded in borrower, not separate nodes for now)
    employers = borrower.get("employers", [])
    if employers:
        for idx, emp in enumerate(employers, 1):
            emp_name = emp.get("employerName")
            if emp_name:
                safe_add_triple(g, borrower_node, TL[f"employer{idx}Name"], emp_name)

            employment = emp.get("employment", {})
            if employment:
                safe_add_triple(g, borrower_node, TL[f"employer{idx}IsSelfEmployed"],
                              employment.get("isSelfEmployed"))
                safe_add_triple(g, borrower_node, TL[f"employer{idx}PositionDescription"],
                              employment.get("employmentPositionDescription"))


def add_property(g: Graph, loan_node: URIRef, prop_data: dict):
    """Add property as a child node."""
    property_node = URIRef(f"{loan_node}_property")

    g.add((property_node, RDF.type, TL.Property))
    g.add((loan_node, TL.hasProperty, property_node))

    # Property address
    address = prop_data.get("propertyAddress", {})
    if address:
        safe_add_triple(g, property_node, TL.propertyAddress, address.get("address"))
        safe_add_triple(g, property_node, TL.propertyCity, address.get("city"))
        safe_add_triple(g, property_node, TL.propertyStateCode, address.get("stateCode"))
        safe_add_triple(g, property_node, TL.propertyPostalCode, address.get("postalCode"))

    # Property fields
    safe_add_triple(g, property_node, TL.propertyUsageType, prop_data.get("propertyUsageType"))
    safe_add_triple(g, property_node, TL.propertyValuationAmount, prop_data.get("propertyValuationAmount"))
    safe_add_triple(g, property_node, TL.propertyAppraisedValueAmount, prop_data.get("propertyAppraisedValueAmount"))
    safe_add_triple(g, property_node, TL.propertyEstimatedValueAmount, prop_data.get("propertyEstimatedValueAmount"))
    safe_add_triple(g, property_node, TL.purchasePriceAmount, prop_data.get("purchasePriceAmount"))
    safe_add_triple(g, property_node, TL.propertyStructureBuiltYear, prop_data.get("propertyStructureBuiltYear"))


def build_graph(loan_app_path: str, extracted_data_path: Optional[str] = None) -> tuple[Graph, URIRef]:
    """Build RDF graph from Touchless loan_application.json."""
    with open(loan_app_path) as f:
        loan_app = json.load(f)

    g = Graph()
    g.bind("tl", TL)
    g.bind("rdf", RDF)
    g.bind("xsd", XSD)

    # Main loan node
    loan_id = loan_app.get("loanId", loan_app.get("applicationId", "unknown"))
    loan_id_clean = loan_id.replace("{", "").replace("}", "").replace("-", "_")
    loan_node = URIRef(TL[f"loan_{loan_id_clean}"])

    g.add((loan_node, RDF.type, TL.LoanApplication))

    # Provenance
    safe_add_triple(g, loan_node, TL.dataSource, "Touchless API")
    timestamp_ms = loan_app.get("timestamp")
    if timestamp_ms:
        timestamp_date = milliseconds_to_date(timestamp_ms)
        if timestamp_date:
            safe_add_triple(g, loan_node, TL.extractionTimestamp, timestamp_date, datatype="date")

    # Top-level identifiers
    safe_add_triple(g, loan_node, TL.loanId, loan_id)
    safe_add_triple(g, loan_node, TL.applicationId, loan_app.get("applicationId"))

    loan_summary = loan_app.get("loanSummary", {})

    # Lender case identifier
    safe_add_triple(g, loan_node, TL.lenderCaseIdentifier,
                   loan_summary.get("lenderCaseIdentifier"), field_name="lenderCaseIdentifier")

    # Loan terms (flat)
    loan_terms = loan_summary.get("loanTerms", {})
    if loan_terms:
        safe_add_triple(g, loan_node, TL.baseLoanAmount, loan_terms.get("baseLoanAmount"),
                       field_name="baseLoanAmount")
        safe_add_triple(g, loan_node, TL.noteAmount, loan_terms.get("noteAmount"))
        safe_add_triple(g, loan_node, TL.loanPurposeType, loan_terms.get("loanPurposeType"),
                       field_name="loanPurposeType")
        safe_add_triple(g, loan_node, TL.mortgageType, loan_terms.get("mortgageType"))
        safe_add_triple(g, loan_node, TL.interestRate, loan_terms.get("interestRate"))
        safe_add_triple(g, loan_node, TL.lienPriorityType, loan_terms.get("lienPriorityType"))

    # Amortization (flat)
    amortization = loan_summary.get("amortization", {})
    if amortization:
        safe_add_triple(g, loan_node, TL.amortizationType, amortization.get("amortizationType"))
        safe_add_triple(g, loan_node, TL.loanAmortizationPeriodCount, amortization.get("loanAmortizationPeriodCount"))

    # Down payment
    down_payment = loan_summary.get("downPayment", {})
    if down_payment:
        safe_add_triple(g, loan_node, TL.downPaymentAmount, down_payment.get("downPaymentAmount"))
        safe_add_triple(g, loan_node, TL.downPaymentType, down_payment.get("downPaymentType"))

    # Qualification (flat)
    qualification = loan_summary.get("qualification", {})
    if qualification:
        safe_add_triple(g, loan_node, TL.housingExpenseRatioPercent,
                       qualification.get("housingExpenseRatioPercent"))
        safe_add_triple(g, loan_node, TL.totalDebtExpenseRatioPercent,
                       qualification.get("totalDebtExpenseRatioPercent"))
        safe_add_triple(g, loan_node, TL.totalMonthlyIncomeAmount,
                       qualification.get("totalMonthlyIncomeAmount"))
        safe_add_triple(g, loan_node, TL.totalLiabilitiesMonthlyPaymentAmount,
                       qualification.get("totalLiabilitiesMonthlyPaymentAmount"))

    # LTV ratios (flat)
    ltv_ratio = loan_summary.get("ltvRatio", {})
    if ltv_ratio:
        safe_add_triple(g, loan_node, TL.baseLtv, ltv_ratio.get("baseLtv"))
        safe_add_triple(g, loan_node, TL.ltv, ltv_ratio.get("ltv"))
        safe_add_triple(g, loan_node, TL.cltv, ltv_ratio.get("cltv"))
        safe_add_triple(g, loan_node, TL.hcltv, ltv_ratio.get("hcltv"))

    # FICO
    safe_add_triple(g, loan_node, TL.fico, loan_summary.get("fico"))

    # Dates
    app_date_ms = loan_summary.get("applicationDate")
    if app_date_ms:
        app_date = milliseconds_to_date(app_date_ms)
        if app_date:
            safe_add_triple(g, loan_node, TL.applicationDate, app_date, datatype="date")

    app_recv_date_ms = loan_summary.get("applicationReceivedDate")
    if app_recv_date_ms:
        app_recv_date = milliseconds_to_date(app_recv_date_ms)
        if app_recv_date:
            safe_add_triple(g, loan_node, TL.applicationReceivedDate, app_recv_date, datatype="date")

    # Loan product
    loan_product = loan_summary.get("loanProduct", {})
    if loan_product:
        safe_add_triple(g, loan_node, TL.productName, loan_product.get("productName"))
        safe_add_triple(g, loan_node, TL.productPortfolioName, loan_product.get("productPortfolioName"))

    # Borrowers (nested)
    borrowers_detail = loan_app.get("borrowersDetail", {})
    borrower_pairs = borrowers_detail.get("borrowerPairs", [])
    borrower_num = 1
    for pair in borrower_pairs:
        borrowers = pair.get("borrowers", [])
        for borrower in borrowers:
            add_borrower(g, loan_node, borrower, borrower_num)
            borrower_num += 1

    # Property (nested) - find in assets
    asset_detail = loan_app.get("assetDetail", {})
    assets = asset_detail.get("assets", [])
    for asset in assets:
        owned_property = asset.get("ownedProperty", {})
        if owned_property:
            prop_data = owned_property.get("property", {})
            if prop_data:
                add_property(g, loan_node, prop_data)
                break  # Just take the first property for now

    return g, loan_node


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    loan_app_path = sys.argv[1]

    # Check if extracted_data_path is provided (optional)
    if len(sys.argv) == 4:
        extracted_data_path = sys.argv[2]
        output_path = sys.argv[3]
    else:
        extracted_data_path = None
        output_path = sys.argv[2]

    print(f"Converting {loan_app_path} → {output_path}")

    graph, loan_node = build_graph(loan_app_path, extracted_data_path)

    # Serialize to Turtle
    graph.serialize(destination=output_path, format="turtle")

    print(f"✓ Wrote {len(graph)} triples to {output_path}")
    print(f"✓ Loan node: {loan_node}")

    # Print sample (first 20 lines)
    print("\n--- Sample (first 20 lines) ---")
    with open(output_path) as f:
        for i, line in enumerate(f, 1):
            if i > 20:
                break
            print(line.rstrip())


if __name__ == "__main__":
    main()
