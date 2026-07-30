#!/usr/bin/env python3
"""
SHACL pilot runner — loan 01.

Honest-by-construction, unlike the earlier qc-loan-audit-engine.py demo:
  * Loan data comes from the REAL p0 fixture (loan_01.json), via loan_to_rdf.
  * Ground truth comes from the REAL p0 defect_manifest.json, loaded at runtime.
  * Validation runs TWICE on independently constructed graphs; the two reports
    must agree (determinism check).
  * Reconciliation reports misses and unexpected extras — it cannot print
    SUCCESS unless every manifest defect is actually detected.

Exit codes: 0 = all manifest defects detected AND deterministic; 1 otherwise.
"""
import json
import os
import sys

from pyshacl import validate
from rdflib import Graph, Namespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from loan_to_rdf import build_graph  # noqa: E402

SH = Namespace("http://www.w3.org/ns/shacl#")

REPO = "/Users/gordonchan/Workspace/demo-sites/mortgage-qc-prod"
FIXTURE = os.path.join(REPO, "p0/fixtures/from_docs/loan_01.json")
MANIFEST = os.path.join(REPO, "p0/fixtures/from_docs/defect_manifest.json")
SHAPES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shapes_loan01.ttl")
LOAN_ID = "2025-0917-001"

# manifest defect_number -> shape local name expected to catch it
DEFECT_TO_SHAPE = {
    1: "EmploymentStartDateShape",
    2: "TitleVestingShape",
    3: "LargeDepositShape",
    4: "UndisclosedLiabilityShape",
    5: "CompDistanceShape",
}


def run_validation():
    """Build fresh graphs and validate. Returns sorted (shape, message) tuples."""
    data = build_graph(FIXTURE)
    shapes = Graph().parse(SHAPES, format="turtle")
    conforms, report_graph, _ = validate(
        data_graph=data,
        shacl_graph=shapes,
        inference="none",
        advanced=True,
    )
    results = []
    for result in report_graph.subjects(SH.resultSeverity, None):
        shape = report_graph.value(result, SH.sourceShape)
        message = report_graph.value(result, SH.resultMessage)
        shape_name = str(shape).rsplit("#", 1)[-1] if shape else "?"
        results.append((shape_name, str(message)))
    return conforms, sorted(results)


def main():
    print("=" * 72)
    print("SHACL PILOT — loan %s (real fixture, real manifest)" % LOAN_ID)
    print("=" * 72)

    # --- determinism: two independent runs must produce identical results ---
    conforms1, run1 = run_validation()
    conforms2, run2 = run_validation()
    deterministic = (run1 == run2) and (conforms1 == conforms2)

    print("\nRun 1: conforms=%s, %d violation(s)" % (conforms1, len(run1)))
    print("Run 2: conforms=%s, %d violation(s)" % (conforms2, len(run2)))
    print("Determinism (identical result sets): %s" % ("PASS" if deterministic else "FAIL"))

    print("\n--- Violations (run 1) ---")
    for shape_name, message in run1:
        print("  [%s]\n    %s" % (shape_name, message))

    # --- reconcile against the real defect manifest ---
    with open(MANIFEST) as f:
        manifest = json.load(f)
    expected = [d for d in manifest["defects"] if d["loan_id"] == LOAN_ID]

    print("\n--- Reconciliation vs p0 defect_manifest.json (%d expected) ---" % len(expected))
    fired_shapes = {shape_name for shape_name, _ in run1}
    missed = []
    for defect in expected:
        shape_name = DEFECT_TO_SHAPE.get(defect["defect_number"])
        caught = shape_name in fired_shapes
        status = "DETECTED" if caught else "MISSED"
        if not caught:
            missed.append(defect)
        print("  defect %d [%s] %s -> %s" % (
            defect["defect_number"], status, defect["description"][:60], shape_name))

    extras = fired_shapes - {DEFECT_TO_SHAPE[d["defect_number"]] for d in expected
                             if d["defect_number"] in DEFECT_TO_SHAPE}
    if extras:
        print("  UNEXPECTED extra violations from: %s" % ", ".join(sorted(extras)))

    print("\n" + "=" * 72)
    ok = deterministic and not missed
    if ok:
        print("RESULT: %d/%d manifest defects detected; deterministic across runs."
              % (len(expected), len(expected)))
    else:
        if missed:
            print("RESULT: FAIL — %d manifest defect(s) NOT detected." % len(missed))
        if not deterministic:
            print("RESULT: FAIL — runs disagreed (non-deterministic).")
    print("=" * 72)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
