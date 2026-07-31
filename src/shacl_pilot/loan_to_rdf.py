#!/usr/bin/env python3
"""
Loan Instance Ontology converter — extraction JSON -> RDF graph.

Consumes extract_loan.py output (decision 002). Every field/fact becomes a typed
property on the loan node; entity families (bank transactions, tradelines, URLA
liabilities, appraisal comps, VOM rows) become child nodes. Citations become
li:cite_<name> nodes in the graph (decision 003), so provenance travels with the
data, not just the sidecar JSON.

USAGE:
  python3 loan_to_rdf.py <extraction_json> <output_ttl>
"""
import json
import sys

from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

LI = Namespace("http://mortgage.audit.ontology/loan-instance#")

ENTITY_CLASSES = {
    "bank_txns": ("BankTransaction", "hasBankTransaction"),
    "tradelines": ("CreditTradeline", "hasCreditTradeline"),
    "urla_liabilities": ("UrlaLiability", "hasUrlaLiability"),
    "comps": ("AppraisalComparable", "hasAppraisalComparable"),
    "vom_rows": ("VomRow", "hasVomRow"),
}


def typed_literal(value, kind=None):
    if isinstance(value, bool):
        return Literal(value)
    if isinstance(value, (int, float)):
        return Literal(str(value), datatype=XSD.decimal)
    if kind == "date":
        return Literal(value, datatype=XSD.date)
    return Literal(str(value))


def add_citation(g, subject, prop_name, citation):
    node = URIRef(str(subject) + "__cite_" + prop_name)
    g.add((subject, LI["cite_" + prop_name], node))
    g.add((node, RDF.type, LI.Citation))
    g.add((node, LI.doc_name, Literal(citation["doc_name"])))
    g.add((node, LI.page, Literal(citation["page"])))
    g.add((node, LI.snippet, Literal(citation["snippet"])))


def build_graph(extraction_path):
    with open(extraction_path) as f:
        ex = json.load(f)

    g = Graph()
    g.bind("li", LI)

    loan = URIRef(LI["loan_" + ex["loan_id"].replace("-", "_")])
    g.add((loan, RDF.type, LI.LoanInstance))
    g.add((loan, LI.loan_id, Literal(ex["loan_id"])))

    for name in sorted(ex.get("fields", {})):
        item = ex["fields"][name]
        g.add((loan, LI[name], typed_literal(item["value"], item.get("kind"))))
        add_citation(g, loan, name, item["citation"])

    for name in sorted(ex.get("facts", {})):
        item = ex["facts"][name]
        g.add((loan, LI[name], typed_literal(item["value"])))
        add_citation(g, loan, name, item["citation"])

    for family in sorted(ex.get("entities", {})):
        cls, link = ENTITY_CLASSES[family]
        for i, item in enumerate(ex["entities"][family], 1):
            child = URIRef(str(loan) + "_%s_%02d" % (family, i))
            g.add((child, RDF.type, LI[cls]))
            g.add((loan, LI[link], child))
            for attr in sorted(item):
                if attr == "citation":
                    continue
                kind = "date" if attr == "date" else None
                g.add((child, LI[attr], typed_literal(item[attr], kind)))
            if "citation" in item:
                add_citation(g, child, "row", item["citation"])

    return g, loan


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    graph, _ = build_graph(sys.argv[1])
    graph.serialize(destination=sys.argv[2], format="turtle")
    print("Wrote %d triples to %s" % (len(graph), sys.argv[2]))
