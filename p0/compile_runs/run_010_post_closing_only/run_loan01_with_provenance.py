"""
QC's loan 01 (demo/syn/loan 01, extracted to fixtures/from_docs/loan_01.json)
against ONLY the three named result/rules/ artifacts:
  - post_closing_only_ruleset.json      (the compiled checks)
  - post_closing_only_applicability.json (check_id -> program, for gating)
  - post_closing_only_provenance.json    (check_id -> real source row(s))

Same dedup / catalog-scope-filter / program-gating pipeline as
run_against_loans.py -- this script's only addition is actually USING
provenance.json, which was written during the compile but never read by
anything since. Every surfaced finding here is enriched with the real
source_file/sheet_name/source_row/exception_code the check was compiled
from, so "where did this rule come from" is answerable by lookup, not
re-investigation.

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
P0 = os.path.dirname(os.path.dirname(HERE))
RESULT_DIR = os.path.normpath(os.path.join(P0, "..", "result"))
sys.path.insert(0, P0)
sys.path.insert(0, os.path.join(P0, "fixtures", "from_docs"))

from qc_engine.ruleset import Ruleset, Check
from qc_engine.catalog import load_catalog
from qc_engine import engine as ENGINE
from qc_engine.compiler import program_gating as PG
from fixture_loader import load_canonical_loan

RULESET_PATH = os.path.join(RESULT_DIR, "rules", "post_closing_only_ruleset.json")
APPLICABILITY_PATH = os.path.join(RESULT_DIR, "rules", "post_closing_only_applicability.json")
PROVENANCE_PATH = os.path.join(RESULT_DIR, "rules", "post_closing_only_provenance.json")
CATALOG_PATH = os.path.join(P0, "qc_engine", "field_catalog.json")
LOAN_01_FIXTURE = os.path.join(P0, "fixtures", "from_docs", "loan_01.json")


def load_deduplicated_in_scope_ruleset():
    raw = json.load(open(RULESET_PATH))
    full_ruleset = Ruleset.from_dict(raw)
    applicable_programs: Dict[str, List[str]] = json.load(open(APPLICABILITY_PATH))
    provenance: Dict[str, List[Dict[str, Any]]] = json.load(open(PROVENANCE_PATH))

    seen_ids = set()
    deduped: List[Check] = []
    for c in full_ruleset.checks:
        if c.id in seen_ids:
            continue
        seen_ids.add(c.id)
        deduped.append(c)

    catalog = load_catalog(CATALOG_PATH)
    catalog_fields = set(e.field_name for e in catalog.entries)
    in_scope = [c for c in deduped if c.field_name in catalog_fields]

    ruleset = Ruleset(ruleset_id="rs-loan01-post-closing-only", version=1, checks=in_scope)
    return ruleset, applicable_programs, provenance, catalog


def _check_applies_to_loan(check: Check, programs: List[str], loan) -> str:
    if "UNTAGGED" in programs:
        return "APPLIES"
    saw_ambiguous = False
    for prog in programs:
        applicability = PG.Applicability(program=prog)
        result = PG.applies_to(loan, applicability)
        if result is PG.AMBIGUOUS:
            saw_ambiguous = True
            continue
        if result:
            return "APPLIES"
    return "AMBIGUOUS" if saw_ambiguous else "SKIPPED"


def main() -> None:
    ruleset, applicable_programs, provenance, catalog = load_deduplicated_in_scope_ruleset()
    loan = load_canonical_loan(LOAN_01_FIXTURE)
    print(f"Loan: {loan.loan_id} (from demo/syn/loan 01, via fixtures/from_docs/loan_01.json)")
    print(f"Ruleset: {len(ruleset.checks)} in-catalog-scope checks (deduplicated)\n")

    gated_checks, skipped, ambiguous = [], 0, []
    for c in ruleset.checks:
        programs = applicable_programs.get(c.id, ["UNTAGGED"])
        verdict = _check_applies_to_loan(c, programs, loan)
        if verdict == "APPLIES":
            gated_checks.append(c)
        elif verdict == "AMBIGUOUS":
            ambiguous.append(c.id)
            gated_checks.append(c)
        else:
            skipped += 1

    result = ENGINE.run(loan, Ruleset(ruleset_id="rs-loan01-gated", version=1, checks=gated_checks),
                        catalog=catalog)
    surfaced = [r for r in result.results if r.status != "NOT_APPLICABLE"]
    print(f"Program gate: {skipped} skipped, {len(gated_checks)} gated in ({len(ambiguous)} ambiguous)")
    print(f"Evaluated: {len(result.results)}, surfaced: {len(surfaced)}, disposition: {result.disposition}\n")

    out_rows = []
    for r in sorted(surfaced, key=lambda r: (r.status != "FAIL", r.check_id)):
        prov_entries = provenance.get(r.check_id, [])
        prov_summary = "; ".join(
            f"{p['source_file']} / {p['sheet_name']} row {p['source_row']} ({p['exception_code']})"
            for p in prov_entries[:2]
        ) or "(no provenance recorded)"
        flag = " [AMBIGUOUS PROGRAM]" if r.check_id in ambiguous else ""
        # Document citation: WHERE in the actual loan PDF this value came
        # from (doc name, page, exact text snippet) -- distinct from
        # `provenance` above (which client-rulebook ROW compiled this RULE).
        # Both were already computed (citation by the engine, provenance by
        # the compiler) but this script previously only surfaced the rule
        # side -- adding the document side closes that gap.
        doc_citation = r.citation  # already a dict via CheckResult.to_dict()'s shape, or None
        doc_summary = "(no document citation -- field not doc-sourced, or absent on this loan)"
        if doc_citation:
            loc = f"{doc_citation['docName']}, p.{doc_citation['pageNum']}"
            if doc_citation.get("section"):
                loc += f" ({doc_citation['section']})"
            doc_summary = f"{loc}: “{doc_citation['segmentSnippet']}”"
        print(f"[{r.status}]{flag} {r.check_id}")
        print(f"    {r.message}")
        print(f"    rule source: {prov_summary}"
              + (f" (+{len(prov_entries)-2} more)" if len(prov_entries) > 2 else ""))
        print(f"    document citation: {doc_summary}")
        out_rows.append({
            "check_id": r.check_id, "status": r.status, "severity": r.severity,
            "message": r.message, "review_reason": r.review_reason,
            "provenance": prov_entries,
            "document_citation": doc_citation,
            "doc_confidence": r.doc_confidence,
        })

    out_path = os.path.join(HERE, "loan01_with_provenance.json")
    with open(out_path, "w") as f:
        json.dump({"loan_id": loan.loan_id, "disposition": result.disposition,
                   "surfaced_results": out_rows}, f, indent=2)
    print(f"\n[written] {out_path}")


if __name__ == "__main__":
    main()
