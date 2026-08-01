#!/usr/bin/env python3
"""
Touchless -> AMQ RDF, using the document inventory as a CLOSED-WORLD source.

Key insight (Gordon, 2026-07-30): documents[] is a COMPLETE classified inventory of
the closing package. So a documentType that is ABSENT is positive evidence of absence,
not unknown data. That converts doc_present_* from NO_DATA into a real false verdict.

Citation granularity is DOCUMENT-level (documentName + documentId), not page-level.
Every emitted fact carries its citation.
"""
import json, sys
from datetime import datetime
from rdflib import Graph, Literal, Namespace, RDF, URIRef, BNode
from rdflib.namespace import XSD

LI = Namespace("http://mortgage.audit.ontology/loan-instance#")

# doc_present_* fact  ->  (matcher on documentType/Subcategory, human label)
# Matching is explicit and auditable: exact documentType strings only.
DOC_RULES = {
    "doc_present_1003":                     ["URLA - Borrower Information"],
    "doc_present_1003_continuation":        ["URLA - Continuation Sheet"],
    "doc_present_credit_report":            ["Credit Report"],
    "doc_present_paystub":                  ["Paystub"],
    "doc_present_w2":                       ["W2"],
    "doc_present_1040":                     ["Form 1040"],
    "doc_present_schedule_c":               ["Form 1040 - Schedule C"],
    "doc_present_k1":                       ["Schedule K-1 - Form 1065"],
    "doc_present_voe":                      ["Work Number Verification"],
    "doc_present_bank_statement":           ["Bank Statement"],
    "doc_present_gift_letter":              ["Gift Letter"],
    "doc_present_voa":                      ["Verification Of Assets"],
    "doc_present_appraisal":                ["Form 1004 Uniform Residential Appraisal"],
    "doc_present_purchase_agreement":       ["Purchase Agreement"],
    "doc_present_title_commitment":         ["Title Commitment"],
    "doc_present_title_policy":             ["Title Policy"],
    "doc_present_closing_disclosure":       ["Closing Disclosure"],
    "doc_present_note":                     ["Note"],
    "doc_present_security_instrument":      ["Security Instrument"],
    "doc_present_hazard_insurance":         ["Hazard Insurance"],
    "doc_present_flood_determination":      ["Flood Hazard Determination", "Standard Flood Hazard Determination"],
    "doc_present_loan_estimate":            ["Loan Estimate"],
    "doc_present_escrow_waiver":            ["Escrow Waiver"],
    "doc_present_occupancy_affidavit":      ["Occupancy Affidavit"],
    "doc_present_pud_rider":                ["PUD Rider"],
    # --- the five the AMQ shapes actually ask for ---
    "doc_present_lbp_disclosure":           ["Lead Based Paint Disclosure"],
    "doc_present_arm_program_disclosure":   ["ARM Program Disclosure", "CHARM Booklet"],
    "doc_present_fha_amendatory_clause":    ["FHA Amendatory Clause"],
    "doc_present_fha_form_442":             ["FHA Form 442", "Compliance Inspection Report"],
    "doc_present_residual_income_worksheet":["Residual Income Worksheet", "VA Loan Analysis"],
    # --- *_in_file variants the shapes use ---
    "ytd_pnl_in_file":                      ["Profit And Loss Statement", "YTD Profit And Loss"],
    "ytd_balance_sheet_in_file":            ["Balance Sheet", "YTD Balance Sheet"],
    "termite_inspection_in_file":           ["Termite Inspection", "NPMA-33"],
    "well_septic_inspection_in_file":       ["Well Septic Inspection", "Water Test"],
    "recert_of_value_in_file":              ["Recertification Of Value"],
    "usda_eligibility_screenprint_in_file": ["USDA Eligibility"],
    "usda_ratio_waiver_in_file":            ["USDA Ratio Waiver"],
    "gift_transfer_evidence_in_file":       ["Gift Transfer Evidence", "Gift Donor Bank Statement"],
}

def ts_to_date(ms):
    return datetime.fromtimestamp(ms/1000).strftime("%Y-%m-%d") if ms else None

def dec(v): return Literal(str(v), datatype=XSD.decimal)

class Builder:
    def __init__(self, g, loan):
        self.g, self.loan = g, loan
        self.n = 0
    def emit(self, pred, value, doc_name=None, doc_id=None, json_path=None, kind=None):
        """Emit a fact plus its citation."""
        if value is None: return
        if isinstance(value, bool):   lit = Literal(value)
        elif kind == "date":          lit = Literal(value, datatype=XSD.date)
        elif isinstance(value,(int,float)): lit = dec(value)
        else:                         lit = Literal(str(value))
        self.g.add((self.loan, LI[pred], lit))
        c = BNode()
        self.g.add((self.loan, LI["cite_"+pred], c))
        self.g.add((c, RDF.type, LI.Citation))
        self.g.add((c, LI.doc_name, Literal(doc_name or "Touchless loan_application.json")))
        if doc_id:    self.g.add((c, LI.document_id, Literal(doc_id)))
        if json_path: self.g.add((c, LI.snippet, Literal(json_path[:160])))
        self.n += 1

def build(path):
    d = json.load(open(path))
    g = Graph(); g.bind("li", LI)
    ls = d.get("loanSummary", {})
    loan_id = str(ls.get("lenderCaseIdentifier","UNKNOWN"))
    loan = URIRef(LI["loan_"+loan_id])
    g.add((loan, RDF.type, LI.LoanInstance))
    b = Builder(g, loan)
    b.emit("loan_id", loan_id, json_path="loanSummary.lenderCaseIdentifier")

    # ---------- document inventory (CLOSED WORLD) ----------
    docs = d.get("documents", [])
    by_type = {}
    for x in docs:
        for key in (x.get("documentType"), x.get("documentSubcategory")):
            if key: by_type.setdefault(key, x)
    for fact, names in DOC_RULES.items():
        hit = next((by_type[n] for n in names if n in by_type), None)
        if hit:
            b.emit(fact, True, hit.get("documentName"), hit.get("documentId"),
                   "documents[].documentType=%s" % hit.get("documentType"))
        else:
            # ABSENT from a complete inventory == positive evidence of absence
            b.emit(fact, False, "Touchless document inventory (%d docs, complete)" % len(docs),
                   None, "no documentType in %s" % (names,))

    # ---------- loan terms ----------
    lt = ls.get("loanTerms", {})
    b.emit("loan_amount", lt.get("baseLoanAmount"), json_path="loanSummary.loanTerms.baseLoanAmount")
    b.emit("mismo_loan_amount", lt.get("baseLoanAmount"), json_path="loanSummary.loanTerms.baseLoanAmount")
    b.emit("mismo_mortgage_type", lt.get("mortgageType"), json_path="loanSummary.loanTerms.mortgageType")
    b.emit("loan_program_1003", lt.get("mortgageType"), json_path="loanSummary.loanTerms.mortgageType")
    b.emit("mismo_note_rate", lt.get("interestRate"), json_path="loanSummary.loanTerms.interestRate")
    purpose = lt.get("loanPurposeType")
    b.emit("loan_purpose_1003", purpose, json_path="loanSummary.loanTerms.loanPurposeType")
    # derived boolean the shapes actually test
    if purpose:
        cash = "CASH" in purpose.upper() and "REFIN" in purpose.upper()
        b.emit("purpose_cashout_1003", cash, json_path="derived from loanPurposeType=%s" % purpose)
    b.emit("mismo_amortization_type",
           {"FIXED":"Fixed","ADJUSTABLE":"AdjustableRate"}.get(str(ls.get("amortization",{}).get("amortizationType")).upper(),
                                                               ls.get("amortization",{}).get("amortizationType")),
           json_path="loanSummary.amortization.amortizationType")

    # ---------- ratios ----------
    q = ls.get("qualification", {})
    b.emit("dti_ratio", q.get("totalDebtExpenseRatioPercent"), json_path="loanSummary.qualification.totalDebtExpenseRatioPercent")
    b.emit("housing_ratio", q.get("housingExpenseRatioPercent"), json_path="loanSummary.qualification.housingExpenseRatioPercent")
    b.emit("piti_ratio", q.get("housingExpenseRatioPercent"), json_path="loanSummary.qualification.housingExpenseRatioPercent")
    ltv = ls.get("ltvRatio", {})
    b.emit("ltv", ltv.get("ltv"), json_path="loanSummary.ltvRatio.ltv")
    b.emit("cltv", ltv.get("cltv"), json_path="loanSummary.ltvRatio.cltv")
    if ls.get("fico"): b.emit("credit_score_1003", str(int(ls["fico"])), json_path="loanSummary.fico")
    b.emit("application_date", ts_to_date(ls.get("applicationDate")), kind="date", json_path="loanSummary.applicationDate")

    # ---------- borrower / self-employment ----------
    bp = d.get("borrowersDetail",{}).get("borrowerPairs",[])
    if bp and bp[0].get("borrowers"):
        br = bp[0]["borrowers"][0]
        b.emit("borrower_name", " ".join(filter(None,[br.get("firstName"),br.get("lastName")])),
               json_path="borrowersDetail.borrowerPairs[0].borrowers[0]")
        emps = br.get("employers",[])
        flagged = [e for e in emps if e.get("employment",{}).get("isSelfEmployed") is True]
        owned   = [e for e in emps if "25Percent" in str(e.get("employment",{}).get("ownershipInterestType"))
                   and e.get("employment",{}).get("isSelfEmployed") is not True]
        se = flagged + owned
        b.emit("borrower_self_employed", bool(se),
               json_path="%d employer(s) flagged isSelfEmployed=true; %d more with ownership>=25%% "
                         "(Fannie B3-3.2-01 treats >=25%% ownership as self-employed)" % (len(flagged), len(owned)))
        # surface the vendor's own internal contradiction rather than silently resolving it
        for e in owned:
            n = BNode(); g.add((loan, LI.hasSourceConflict, n))
            g.add((n, LI.field, Literal("borrower_self_employed")))
            g.add((n, LI.value_a, Literal("false (employment.isSelfEmployed)")))
            g.add((n, LI.value_b, Literal("true (ownershipInterestType >= 25%)")))
            g.add((n, LI.subject_ref, Literal(str(e.get("employerName")))))
        if emps:
            e0=emps[0]
            b.emit("employer_name_1003", e0.get("employerName"), json_path="employers[0].employerName")
            inc=e0.get("income",[])
            if inc: b.emit("base_monthly_income_1003", inc[0].get("monthlyIncome"), json_path="employers[0].income[0].monthlyIncome")
        # co-borrower presence
        nco = len(bp[0]["borrowers"]) - 1
        if nco>0:
            co=bp[0]["borrowers"][1]
            b.emit("co_borrower_name"," ".join(filter(None,[co.get("firstName"),co.get("lastName")])),json_path="borrowers[1]")

    # ---------- property ----------
    col = d.get("collateralDetail",{}).get("collateral",[])
    if col:
        p=col[0]
        b.emit("property_state", p.get("propertyAddress",{}).get("state"), json_path="collateral[0].propertyAddress.state")
        pd=p.get("propertyDetail",{})
        b.emit("property_year_built", pd.get("propertyStructureBuiltYear"), json_path="collateral[0].propertyDetail.propertyStructureBuiltYear")
        vs=d["collateralDetail"].get("collateralService",{}).get("valuationServices",[])
        if vs:
            vr=vs[0].get("valuationReport",{})
            appr_doc=by_type.get("Form 1004 Uniform Residential Appraisal",{})
            b.emit("appraisal_effective_date", ts_to_date(vr.get("appraisalReportEffectiveDate")) if isinstance(vr.get("appraisalReportEffectiveDate"),int) else vr.get("appraisalReportEffectiveDate"),
                   appr_doc.get("documentName"), appr_doc.get("documentId"), "valuationReport.appraisalReportEffectiveDate", kind="date")
            b.emit("appraised_value", pd.get("propertyValuationAmount") or pd.get("propertyEstimatedValueAmount"),
                   appr_doc.get("documentName"), appr_doc.get("documentId"), "propertyDetail.propertyValuationAmount")

    # ---------- liabilities (URLA side, real data) ----------
    for L in d.get("liabilityDetail",{}).get("liabilities",[]):
        n=BNode(); g.add((loan, LI.hasUrlaLiability, n))
        g.add((n, LI.creditor, Literal(L.get("holder",{}).get("fullName","?"))))
        if L.get("monthlyPaymentAmount") is not None:
            g.add((n, LI.monthly_payment, dec(L["monthlyPaymentAmount"])))
        if L.get("unpaidBalanceAmount") is not None:
            g.add((n, LI.unpaid_balance, dec(L["unpaidBalanceAmount"])))
        c=BNode(); g.add((n, LI.cite_row, c))
        urla=by_type.get("URLA - Borrower Information",{})
        g.add((c, LI.doc_name, Literal(urla.get("documentName","URLA"))))
        g.add((c, LI.page, Literal(0)))
        b.n+=1
    return g, loan, b.n

if __name__=="__main__":
    g,loan,n=build(sys.argv[1])
    g.serialize(destination=sys.argv[2], format="turtle")
    print("facts emitted: %d | triples: %d" % (n, len(g)))
    print("loan node:", loan)
