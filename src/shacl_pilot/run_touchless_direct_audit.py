#!/usr/bin/env python3
"""
Touchless → RDF → SHACL integrated audit runner.

Pipeline:
  1. Load Touchless JSON (loan_application.json)
  2. Convert → RDF (touchless_to_rdf.py)
  3. Load Touchless-native shapes (blocks/touchless_*.ttl)
  4. Run SHACL validation
  5. Report findings + metrics

USAGE:
  python3 run_touchless_direct_audit.py <loan_application.json>

EXAMPLE:
  python3 run_touchless_direct_audit.py demo/touchless/loan_application.json
"""
import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, Namespace

# Import touchless_to_rdf converter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from touchless_to_rdf import build_graph  # noqa: E402

SH = Namespace("http://www.w3.org/ns/shacl#")
TL = Namespace("http://touchless.audit/loan#")


def load_touchless_shapes(blocks_dir: Path) -> Graph:
    """Load all touchless_*.ttl shape files from blocks/ directory."""
    shapes = Graph()
    shapes.bind("sh", SH)
    shapes.bind("tl", TL)

    touchless_shapes = sorted(blocks_dir.glob("touchless_*.ttl"))
    if not touchless_shapes:
        raise FileNotFoundError(f"No touchless_*.ttl files found in {blocks_dir}")

    for shape_file in touchless_shapes:
        print(f"Loading shape file: {shape_file.name}", file=sys.stderr)
        shapes.parse(shape_file, format="turtle")

    return shapes


def extract_shape_names(shapes_graph: Graph) -> set:
    """Extract all shape names from the shapes graph."""
    shape_names = set()
    for shape in shapes_graph.subjects(predicate=None, object=SH.NodeShape):
        shape_name = str(shape).rsplit("#", 1)[-1] if "#" in str(shape) else str(shape).rsplit("/", 1)[-1]
        shape_names.add(shape_name)
    return shape_names


def categorize_findings(report_graph: Graph, all_shapes: set, conforms: bool) -> dict:
    """
    Categorize findings by severity.

    Returns dict with:
      - FAIL: list of (shape_name, message) tuples for Violations
      - NEEDS_REVIEW: list of (shape_name, message) tuples for Warnings/Info
      - PASS: set of shape names that evaluated without violations
      - EVALUATED: set of ALL shape names that were checked (FAIL + NEEDS_REVIEW + PASS)
      - NO_DATA: set of shape names that couldn't evaluate (lack of required data)

    Note: If conforms=True and no violations, we assume all shapes were evaluated and passed.
    If conforms=False, only shapes with explicit violations in the report are marked as evaluated.
    """
    findings = {
        "FAIL": [],
        "NEEDS_REVIEW": [],
        "PASS": set(),
        "EVALUATED": set(),
        "NO_DATA": set()
    }

    # Extract violations from report
    shapes_with_findings = set()
    for result in report_graph.subjects(predicate=SH.resultSeverity, object=None):
        severity = report_graph.value(result, SH.resultSeverity)
        shape = report_graph.value(result, SH.sourceShape)
        message = report_graph.value(result, SH.resultMessage)

        shape_name = str(shape).rsplit("#", 1)[-1] if shape else "?"
        shapes_with_findings.add(shape_name)

        severity_str = str(severity).rsplit("#", 1)[-1] if severity else "?"

        if severity_str == "Violation":
            findings["FAIL"].append((shape_name, str(message)))
        elif severity_str in ["Warning", "Info"]:
            findings["NEEDS_REVIEW"].append((shape_name, str(message)))

    # If conforms=True, all shapes evaluated and passed (except those with findings)
    # If conforms=False, only shapes with findings were evaluated
    if conforms:
        # All shapes evaluated, only those with findings have violations/warnings
        findings["EVALUATED"] = all_shapes
        findings["PASS"] = all_shapes - shapes_with_findings
        findings["NO_DATA"] = set()
    else:
        # Only shapes with findings are confirmed evaluated
        findings["EVALUATED"] = shapes_with_findings
        findings["NO_DATA"] = all_shapes - shapes_with_findings

    return findings


def run_audit(loan_app_path: str) -> dict:
    """
    Run full Touchless → RDF → SHACL audit pipeline.

    Returns dict with:
      - loan_id: str
      - triple_count: int
      - shape_count: int
      - evaluated_count: int
      - no_data_count: int
      - findings: dict with FAIL/NEEDS_REVIEW lists
      - processing_time_ms: float
      - conforms: bool
    """
    start_time = time.time()

    # Step 1: Load Touchless JSON and extract loan ID
    print(f"\n[1/5] Loading Touchless JSON: {loan_app_path}", file=sys.stderr)
    with open(loan_app_path) as f:
        loan_app = json.load(f)
    loan_id = loan_app.get("loanId", loan_app.get("applicationId", "unknown"))
    loan_id_clean = loan_id.replace("{", "").replace("}", "").replace("-", "_")
    print(f"        Loan ID: {loan_id}", file=sys.stderr)

    # Step 2: Convert to RDF
    print("\n[2/5] Converting to RDF...", file=sys.stderr)
    data_graph, loan_node = build_graph(loan_app_path)
    triple_count = len(data_graph)
    print(f"        Triples: {triple_count}", file=sys.stderr)
    print(f"        Loan node: {loan_node}", file=sys.stderr)

    # Step 3: Load Touchless-native shapes
    print("\n[3/5] Loading Touchless-native shapes...", file=sys.stderr)
    script_dir = Path(__file__).parent
    blocks_dir = script_dir / "blocks"
    shapes_graph = load_touchless_shapes(blocks_dir)
    all_shapes = extract_shape_names(shapes_graph)
    shape_count = len(all_shapes)
    print(f"        Total shapes: {shape_count}", file=sys.stderr)

    # Step 4: Run SHACL validation
    print("\n[4/5] Running SHACL validation...", file=sys.stderr)
    conforms, report_graph, _ = validate(
        data_graph=data_graph,
        shacl_graph=shapes_graph,
        inference="none",
        advanced=True,
    )
    print(f"        Conforms: {conforms}", file=sys.stderr)

    # Step 5: Categorize findings
    print("\n[5/5] Categorizing findings...", file=sys.stderr)
    findings = categorize_findings(report_graph, all_shapes, conforms)

    processing_time_ms = (time.time() - start_time) * 1000

    return {
        "loan_id": loan_id,
        "triple_count": triple_count,
        "shape_count": shape_count,
        "evaluated_count": len(findings["EVALUATED"]),
        "pass_count": len(findings["PASS"]),
        "no_data_count": len(findings["NO_DATA"]),
        "findings": findings,
        "processing_time_ms": processing_time_ms,
        "conforms": conforms,
    }


def print_report(results: dict):
    """Print formatted audit report."""
    print("\n" + "=" * 72)
    print("TOUCHLESS → RDF → SHACL AUDIT REPORT")
    print("=" * 72)

    print(f"\nLoan ID: {results['loan_id']}")
    print(f"Processing time: {results['processing_time_ms']:.1f}ms")
    print(f"Conforms: {results['conforms']}")

    print("\n--- RDF Metrics ---")
    print(f"Triple count: {results['triple_count']}")

    print("\n--- Shape Metrics ---")
    print(f"Total shapes: {results['shape_count']}")
    print(f"Evaluated: {results['evaluated_count']} ({100 * results['evaluated_count'] / results['shape_count']:.1f}%)")
    print(f"  - PASS: {results['pass_count']} ({100 * results['pass_count'] / results['shape_count']:.1f}%)")
    print(f"NO_DATA: {results['no_data_count']} ({100 * results['no_data_count'] / results['shape_count']:.1f}%)")

    findings = results['findings']
    fail_count = len(findings['FAIL'])
    needs_review_count = len(findings['NEEDS_REVIEW'])

    print("\n--- Findings ---")
    print(f"FAIL: {fail_count}")
    print(f"NEEDS_REVIEW: {needs_review_count}")

    if fail_count > 0:
        print("\n--- FAIL Details ---")
        for shape_name, message in findings['FAIL']:
            print(f"  [{shape_name}]")
            print(f"    {message}")

    if needs_review_count > 0:
        print("\n--- NEEDS_REVIEW Details ---")
        for shape_name, message in findings['NEEDS_REVIEW']:
            print(f"  [{shape_name}]")
            print(f"    {message}")

    if results['pass_count'] > 0 and results['pass_count'] <= 10:
        print("\n--- PASS Shapes (sample) ---")
        for shape_name in sorted(list(findings['PASS'])[:10]):
            print(f"  {shape_name}")
    elif results['pass_count'] > 10:
        print(f"\n--- PASS Shapes ---")
        print(f"  {results['pass_count']} shapes passed (too many to list)")

    if results['no_data_count'] > 0:
        print("\n--- NO_DATA Shapes ---")
        for shape_name in sorted(findings['NO_DATA']):
            print(f"  {shape_name}")

    print("\n" + "=" * 72)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    loan_app_path = sys.argv[1]

    if not os.path.exists(loan_app_path):
        print(f"ERROR: File not found: {loan_app_path}", file=sys.stderr)
        sys.exit(1)

    try:
        results = run_audit(loan_app_path)
        print_report(results)

        # Exit code: 0 if conforms, 1 if violations found
        sys.exit(0 if results['conforms'] else 1)

    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
