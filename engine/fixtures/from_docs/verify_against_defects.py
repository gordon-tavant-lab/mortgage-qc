"""
verify_against_defects.py — the 25/25 hard gate (FR-005/FR-006, SC-001).

For each of defect_manifest.json's 25 known defects, load the corresponding
generated CanonicalLoan fixture, resolve field_name (and compare_field_name if
present), and assert the extracted values match expected_values exactly — or,
for expected_relationship=missing, that the field genuinely resolves to
absent, never a fabricated placeholder.

Aggregate: 25/25 matched is the only passing state. Anything less is a hard
failure (non-zero exit), never a warning to log and proceed past
(contracts/defect-verification-manifest.md's Verification semantics).

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fixture_loader import load_canonical_loan  # noqa: E402

MANIFEST_PATH = os.path.join(HERE, "defect_manifest.json")


def _field_value_for_check(loan, field_name: str, source_key_hint: str) -> Any:
    """Return the value to compare for one side of a defect: the truth (doc)
    value by default, or the system value under source_key_hint when that key
    is present in the field's sources{} (the doc-vs-system case, e.g.
    fha_case_number_1003's mismo side)."""
    sv = loan.get(field_name)
    if source_key_hint and source_key_hint in sv.sources:
        return sv.sources[source_key_hint]
    return sv.truth


def check_defect(defect: Dict[str, Any], loans_by_id: Dict[str, Any]) -> Tuple[bool, str]:
    loan = loans_by_id.get(defect["loan_id"])
    if loan is None:
        return False, "no fixture loaded for loan_id {0}".format(defect["loan_id"])

    field_name = defect["field_name"]
    compare_field_name = defect.get("compare_field_name")
    expected = defect["expected_values"]
    relationship = defect["expected_relationship"]

    if relationship == "missing":
        # The field must genuinely resolve to absent — never a fabricated
        # placeholder value (spec.md Edge Cases). expected_values holds a
        # single key whose value is either `false` (a document explicitly
        # states the fact is false) or `null` (no document exists at all;
        # absence of `truth` itself is the correct, uncited resolution).
        only_key = next(iter(expected))
        expected_val = expected[only_key]
        actual = loan.get(field_name).truth
        if expected_val is None:
            ok = actual is None
        else:
            # Require a genuine Python/JSON bool `False` — never a string
            # standing in for one. A string is truthy in Python, so silently
            # accepting "false" here would let a real type regression pass
            # (exactly the "scorer that can't fail on a bad label" trap).
            ok = actual is False
        return ok, "expected {0}, got {1!r} (type={2})".format(
            expected_val, actual, type(actual).__name__)

    # mismatch / threshold_breach / stale: compare field_name's value (and
    # compare_field_name's, if present) against the manifest's expected_values,
    # resolving doc-vs-system fields (fha_case_number_1003) via sources{}.
    expected_items = list(expected.items())
    mismatches = []

    # First expected item maps to field_name's value.
    key0, val0 = expected_items[0]
    source_hint = "mismo" if key0 == "mismo" else None
    actual0 = _field_value_for_check(loan, field_name, source_hint)
    if val0 is None:
        if actual0 is not None:
            mismatches.append("{0}: expected None, got {1!r}".format(field_name, actual0))
    elif str(actual0) != str(val0):
        mismatches.append("{0}: expected {1!r}, got {2!r}".format(field_name, val0, actual0))

    if len(expected_items) > 1:
        key1, val1 = expected_items[1]
        if key1 == "mismo":
            actual1 = _field_value_for_check(loan, field_name, "mismo")
            target_field = field_name
        else:
            target_field = compare_field_name
            actual1 = _field_value_for_check(loan, compare_field_name, None) if compare_field_name else None
        if str(actual1) != str(val1):
            mismatches.append("{0}: expected {1!r}, got {2!r}".format(target_field, val1, actual1))

    return (len(mismatches) == 0), "; ".join(mismatches) if mismatches else "matched"


def run_verification(fixtures_dir: str = None) -> Tuple[int, int, List[Dict[str, Any]]]:
    fixtures_dir = fixtures_dir or HERE
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    defects = manifest["defects"]

    loans_by_id = {}
    for fname in os.listdir(fixtures_dir):
        if fname.startswith("loan_") and fname.endswith(".json"):
            loan = load_canonical_loan(os.path.join(fixtures_dir, fname))
            loans_by_id[loan.loan_id] = loan

    results = []
    matched = 0
    for defect in defects:
        ok, detail = check_defect(defect, loans_by_id)
        if ok:
            matched += 1
        results.append({
            "loan_id": defect["loan_id"],
            "defect_number": defect["defect_number"],
            "field_name": defect["field_name"],
            "matched": ok,
            "detail": detail,
        })
    return matched, len(defects), results


def main() -> int:
    fixtures_dir = sys.argv[1] if len(sys.argv) > 1 else HERE
    matched, total, results = run_verification(fixtures_dir)

    for r in results:
        status = "OK  " if r["matched"] else "FAIL"
        print("[{0}] {1} defect#{2} ({3}) — {4}".format(
            status, r["loan_id"], r["defect_number"], r["field_name"], r["detail"]))

    print()
    print("{0}/{1} matched".format(matched, total))

    if matched != total:
        print("FAIL — fixtures are NOT trustworthy. MUST NOT be wired into any "
              "downstream engine or eval test run until this reaches {0}/{0}.".format(total))
        return 1

    print("PASS — 25/25 known defects reproduced exactly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
