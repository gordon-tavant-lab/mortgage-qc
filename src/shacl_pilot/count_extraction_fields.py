#!/usr/bin/env python3
"""
Count extracted fields across all 5 loans to measure coverage improvement.
"""
import json
import os
import sys
from extract_loan import LoanExtractor

HERE = os.path.dirname(os.path.abspath(__file__))
SYN = os.path.join(HERE, "../../demo/syn")

LOANS = [
    ("loan 01", "2025-0917-001"),
    ("loan 02", "2025-1004-FHA-002"),
    ("loan 03", "2025-1108-VA-003"),
    ("loan 04", "2025-1215-FRD-004"),
    ("loan 05", "2025-1122-USDA-005"),
]

# Fields we just added
NEW_FIELDS = [
    "property_state",
    "property_year_built",
    "loan_purpose_1003",  # already existed, verify it works
]

NEW_FACTS = [
    "borrower_self_employed",  # already existed, verify it works
]

def main():
    print("\n" + "="*70)
    print("CONTEXTUAL FACT EXTRACTION TEST")
    print("="*70)

    results = []

    for loan_dir, loan_id in LOANS:
        loan_path = os.path.join(SYN, loan_dir)
        extraction = LoanExtractor(loan_path).run()

        fields = extraction["fields"]
        facts = extraction["facts"]

        # Check new fields
        new_field_status = {}
        for f in NEW_FIELDS:
            new_field_status[f] = f in fields and fields[f]["value"] is not None

        # Check new facts
        new_fact_status = {}
        for f in NEW_FACTS:
            new_fact_status[f] = f in facts

        results.append({
            "loan": loan_dir,
            "loan_id": loan_id,
            "total_fields": len(fields),
            "total_facts": len(facts),
            "new_fields": new_field_status,
            "new_facts": new_fact_status,
        })

        print(f"\n{loan_dir} ({loan_id})")
        print(f"  Total fields:  {len(fields)}")
        print(f"  Total facts:   {len(facts)}")
        print(f"  New fields:")
        for f, present in new_field_status.items():
            status = "✅" if present else "❌"
            value = fields[f]["value"] if present else "NOT EXTRACTED"
            print(f"    {status} {f:30s} = {value}")
        print(f"  New facts:")
        for f, present in new_fact_status.items():
            status = "✅" if present else "❌"
            value = facts[f]["value"] if present else "NOT PRESENT"
            print(f"    {status} {f:30s} = {value}")

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")

    for field in NEW_FIELDS:
        count = sum(1 for r in results if r["new_fields"][field])
        print(f"{field:30s}: {count}/5 loans ({100*count/5:.0f}%)")

    for fact in NEW_FACTS:
        count = sum(1 for r in results if r["new_facts"][fact])
        print(f"{fact:30s}: {count}/5 loans ({100*count/5:.0f}%) - expected sparse (only SE loans)")

    avg_fields = sum(r["total_fields"] for r in results) / len(results)
    avg_facts = sum(r["total_facts"] for r in results) / len(results)

    print(f"\nAverage fields per loan: {avg_fields:.1f}")
    print(f"Average facts per loan:  {avg_facts:.1f}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
