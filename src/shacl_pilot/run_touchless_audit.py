#!/usr/bin/env python3
"""
Run SHACL QC audit on Touchless loan data.

Converts Touchless API format → extraction JSON → RDF → SHACL validation → findings report.
"""
import json
import os
import sys
import tempfile
from pyshacl import validate
from rdflib import Graph, Namespace, RDF

from touchless_adapter import adapt_touchless_to_extraction
from loan_to_rdf import build_graph

HERE = os.path.dirname(os.path.abspath(__file__))

def load_shapes():
    """Load all SHACL shapes from blocks/ directory."""
    shapes_g = Graph()
    blocks_dir = os.path.join(HERE, "blocks")

    if not os.path.exists(blocks_dir):
        print(f"ERROR: shapes directory not found: {blocks_dir}")
        sys.exit(1)

    ttl_files = [f for f in os.listdir(blocks_dir) if f.endswith(".ttl")]
    if not ttl_files:
        print(f"ERROR: no .ttl files found in {blocks_dir}")
        sys.exit(1)

    for ttl_file in ttl_files:
        path = os.path.join(blocks_dir, ttl_file)
        shapes_g.parse(path, format="turtle")
        print(f"  Loaded {ttl_file}")

    return shapes_g

def run_audit(loan_app_path, extracted_data_path):
    """Run SHACL audit on Touchless data."""

    print("\n" + "="*70)
    print("TOUCHLESS LOAN QC AUDIT")
    print("="*70)

    # Step 1: Convert Touchless data to extraction format
    print("\n[1/4] Converting Touchless data to extraction format...")
    extraction = adapt_touchless_to_extraction(loan_app_path, extracted_data_path)

    loan_id = extraction["loan_id"]
    print(f"  Loan ID: {loan_id}")
    print(f"  Fields extracted: {len(extraction['fields'])}")
    print(f"  Facts extracted: {len(extraction['facts'])}")

    # Step 2: Convert extraction to RDF
    print("\n[2/4] Converting extraction to RDF...")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        json.dump(extraction, tmp, indent=1)
        tmp_path = tmp.name

    data_g, loan_node = build_graph(tmp_path)
    os.unlink(tmp_path)

    print(f"  RDF triples: {len(data_g)}")

    # Step 3: Load SHACL shapes
    print("\n[3/4] Loading SHACL shapes...")
    shapes_g = load_shapes()

    # Count shapes
    SH = Namespace("http://www.w3.org/ns/shacl#")
    from rdflib.term import URIRef
    node_shapes = list(shapes_g.subjects(RDF.type, URIRef("http://www.w3.org/ns/shacl#NodeShape")))
    print(f"  Total shapes loaded: {len(node_shapes)}")

    # Step 4: Run SHACL validation
    print("\n[4/4] Running SHACL validation...")
    conforms, results_graph, results_text = validate(
        data_graph=data_g,
        shacl_graph=shapes_g,
        inference='rdfs',
        abort_on_first=False,
        allow_infos=False,
        allow_warnings=False,
    )

    # Parse results
    validation_results = list(results_graph.subjects(RDF.type, SH.ValidationResult))

    findings = {"FAIL": [], "NEEDS_REVIEW": [], "PASS": []}

    for vr in validation_results:
        severity = results_graph.value(vr, SH.resultSeverity)
        source_shape = results_graph.value(vr, SH.sourceShape)
        result_message = results_graph.value(vr, SH.resultMessage)
        focus_node = results_graph.value(vr, SH.focusNode)

        shape_name = str(source_shape).split("#")[-1] if source_shape else "UnknownShape"
        message = str(result_message) if result_message else "No message"

        if severity == SH.Violation:
            findings["FAIL"].append({"shape": shape_name, "message": message})
        elif severity == SH.Warning:
            findings["NEEDS_REVIEW"].append({"shape": shape_name, "message": message})

    # Calculate NO_DATA
    evaluated_shapes = len(set(results_graph.objects(None, SH.sourceShape)))
    total_shapes = len(node_shapes)
    no_data_count = total_shapes - evaluated_shapes

    # Report
    print("\n" + "="*70)
    print("AUDIT RESULTS")
    print("="*70)

    print(f"\nLoan: {loan_id}")
    print(f"  Total shapes:     {total_shapes}")
    print(f"  Evaluated:        {evaluated_shapes} ({100*evaluated_shapes/total_shapes:.1f}%)")
    print(f"  NO_DATA:          {no_data_count} ({100*no_data_count/total_shapes:.1f}%)")

    print(f"\nFindings:")
    print(f"  FAIL:             {len(findings['FAIL'])}")
    print(f"  NEEDS_REVIEW:     {len(findings['NEEDS_REVIEW'])}")

    if findings["FAIL"]:
        print(f"\nFAIL findings:")
        for i, finding in enumerate(findings["FAIL"][:10], 1):
            print(f"  {i}. {finding['shape']}")
            print(f"     {finding['message'][:100]}")

    if findings["NEEDS_REVIEW"]:
        print(f"\nNEEDS_REVIEW findings:")
        for i, finding in enumerate(findings["NEEDS_REVIEW"][:5], 1):
            print(f"  {i}. {finding['shape']}")
            print(f"     {finding['message'][:100]}")

    if no_data_count > 0:
        print(f"\nNO_DATA: {no_data_count} shapes did not have sufficient data to evaluate")
        print(f"  This means {100*no_data_count/total_shapes:.1f}% of checks could not run due to missing fields")

    # Field coverage analysis
    print(f"\n" + "="*70)
    print("FIELD COVERAGE ANALYSIS")
    print("="*70)

    print(f"\nFields extracted from Touchless ({len(extraction['fields'])}):")
    for field_name in sorted(extraction["fields"].keys())[:20]:
        value = extraction["fields"][field_name]["value"]
        if isinstance(value, float):
            print(f"  ✅ {field_name:35s} = ${value:,.2f}" if field_name.endswith("_amount") or "income" in field_name or "ratio" not in field_name else f"  ✅ {field_name:35s} = {value:.2f}%")
        else:
            print(f"  ✅ {field_name:35s} = {value}")

    if len(extraction["fields"]) > 20:
        print(f"  ... and {len(extraction['fields']) - 20} more")

    print(f"\nFacts extracted ({len(extraction['facts'])}):")
    for fact_name, fact_data in extraction["facts"].items():
        print(f"  ✅ {fact_name:35s} = {fact_data['value']}")

    return {
        "loan_id": loan_id,
        "total_shapes": total_shapes,
        "evaluated": evaluated_shapes,
        "no_data": no_data_count,
        "fail": len(findings["FAIL"]),
        "needs_review": len(findings["NEEDS_REVIEW"]),
        "findings": findings,
        "fields_extracted": len(extraction["fields"]),
        "facts_extracted": len(extraction["facts"]),
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        print("\nUsage: python3 run_touchless_audit.py <loan_application.json> <extracted_data.json>")
        sys.exit(1)

    result = run_audit(sys.argv[1], sys.argv[2])
    sys.exit(0)
