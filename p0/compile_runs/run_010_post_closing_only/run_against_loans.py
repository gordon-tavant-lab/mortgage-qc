"""
Runs the NEW post-closing-only compiled ruleset (result/rules/
post_closing_only_ruleset.json -- compiled directly from the confirmed 5,098
post-closing rows, pre-funding rows never touched at all) against all 5
parsed loan fixtures, program-gated per loan, alongside the existing
validated 32-check baseline (ruleset_defects.py).

This is the live QC-running script going forward -- supersedes run_008's
run_against_loans.py, which loaded the mixed-scope comprehensive_ruleset.json
and applied a since-confirmed-buggy pre-funding exclusion filter on top (that
filter dropped legitimate post-closing checks like
`title-vesting-1003-vs-commitment` whenever the SAME check ID also happened
to be producible from a pre-funding row -- content-deterministic IDs don't
distinguish "exclusively pre-funding" from "also pre-funding"). Compiling the
true post-closing-only row set directly (run_010/run_compile.py) avoids that
whole class of bug -- there is no exclusion step here at all, because nothing
pre-funding was ever compiled into this ruleset in the first place.

run_008's comprehensive_ruleset.json / run_009's prefunding_check_ids.json
are left on disk untouched (kept per explicit instruction) but are no longer
read by this script or any live QC run.

Honesty notes carried over from run_008 (still apply):

1. DEDUPLICATION: the compiled ruleset has far more check INSTANCES than
   unique check IDs -- the real AMQ workbooks restate the same condition
   across each program's own sheet. Deduplicated to one representative per
   id (first occurrence) before running.

2. SCOPE-MISMATCH FILTER: these 5 synthetic loans carry ~378 known fields
   total (field_catalog.json) -- nowhere near the breadth of a full AMQ
   checklist. Restricted to catalog-known fields so the ruleset's applicable
   subset to these loans is meaningfully reviewable, not mostly guaranteed
   "field never populated for this loan" noise.

3. PROGRAM GATING: via the existing, already-tested program_gating.py
   (program_gating.applies_to()) -- same gate ruleset_defects.py's own
   defects_ruleset_for() uses for the baseline.

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
from fixtures.ruleset_defects import defects_ruleset_for

FIXTURES_DIR = os.path.join(P0, "fixtures", "from_docs")
POST_CLOSING_RULESET_PATH = os.path.join(RESULT_DIR, "rules", "post_closing_only_ruleset.json")
APPLICABILITY_PATH = os.path.join(RESULT_DIR, "rules", "post_closing_only_applicability.json")
CATALOG_PATH = os.path.join(P0, "qc_engine", "field_catalog.json")


def load_deduplicated_post_closing_ruleset():
    raw = json.load(open(POST_CLOSING_RULESET_PATH))
    full_ruleset = Ruleset.from_dict(raw)
    applicable_programs: Dict[str, List[str]] = json.load(open(APPLICABILITY_PATH))

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

    dedup_stats = {
        "total_compiled": len(full_ruleset.checks),
        "unique_ids": len(deduped),
        "in_catalog_scope": len(in_scope),
        "out_of_scope_no_field_data_possible": len(deduped) - len(in_scope),
    }
    ruleset = Ruleset(ruleset_id="rs-post-closing-only-in-scope", version=1, checks=in_scope)
    return ruleset, applicable_programs, dedup_stats


def _check_applies_to_loan(check: Check, programs: List[str], loan) -> str:
    """Returns 'APPLIES', 'SKIPPED', or 'AMBIGUOUS' -- using the existing,
    already-tested program_gating.applies_to() per associated program,
    never a new/reinvented gating rule."""
    if "UNTAGGED" in programs:
        return "APPLIES"  # fails open -- same semantics as program_gating's own None case
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


def run_post_closing_for_loan(ruleset: Ruleset, applicable_programs: Dict[str, List[str]], loan) -> Dict[str, Any]:
    gated_checks = []
    skipped_count = 0
    ambiguous_checks = []
    for c in ruleset.checks:
        programs = applicable_programs.get(c.id, ["UNTAGGED"])
        verdict = _check_applies_to_loan(c, programs, loan)
        if verdict == "APPLIES":
            gated_checks.append(c)
        elif verdict == "AMBIGUOUS":
            ambiguous_checks.append(c)
            gated_checks.append(c)  # include but flagged -- never silently resolved either way
        else:
            skipped_count += 1

    gated_ruleset = Ruleset(ruleset_id="rs-post-closing-gated", version=1, checks=gated_checks)
    result = ENGINE.run(loan, gated_ruleset)
    surfaced = [r for r in result.results if r.status != "NOT_APPLICABLE"]
    ambiguous_ids = {c.id for c in ambiguous_checks}

    surfaced_dicts = []
    for r in surfaced:
        d = r.to_dict()
        d["ambiguous_program"] = r.check_id in ambiguous_ids
        surfaced_dicts.append(d)

    return {
        "loan_id": loan.loan_id,
        "total_checks_in_ruleset": len(ruleset.checks),
        "skipped_by_program_gate": skipped_count,
        "gated_in_count": len(gated_checks),
        "ambiguous_program_count": len(ambiguous_checks),
        "evaluated_count": len(result.results),
        "not_applicable_count": len(result.results) - len(surfaced),
        "surfaced_count": len(surfaced),
        "surfaced_results": surfaced_dicts,
        "disposition": result.disposition,
    }


def run_baseline_for_loan(loan) -> Dict[str, Any]:
    rs = defects_ruleset_for(loan)
    result = ENGINE.run(loan, rs)
    return result.to_dict()


def main() -> None:
    ruleset, applicable_programs, dedup_stats = load_deduplicated_post_closing_ruleset()
    print(f"Deduplicated post-closing-only ruleset: {dedup_stats['total_compiled']} compiled -> "
          f"{dedup_stats['unique_ids']} unique checks", flush=True)
    print(f"Scope filter: {dedup_stats['in_catalog_scope']} checks reference a field this dataset "
          f"could possibly have ({dedup_stats['out_of_scope_no_field_data_possible']} excluded -- "
          f"no field data possible for these 5 loans)", flush=True)

    loan_files = sorted(f for f in os.listdir(FIXTURES_DIR) if f.startswith("loan_") and f.endswith(".json"))

    combined = {"dedup_stats": dedup_stats, "loans": {}}
    for lf in loan_files:
        loan = load_canonical_loan(os.path.join(FIXTURES_DIR, lf))
        print(f"\n=== {loan.loan_id} ({lf}, loan_type={loan.loan_type!r}) ===", flush=True)

        post_closing = run_post_closing_for_loan(ruleset, applicable_programs, loan)
        print(f"  Program gate: {post_closing['skipped_by_program_gate']} skipped, "
              f"{post_closing['gated_in_count']} gated in ({post_closing['ambiguous_program_count']} ambiguous)", flush=True)
        print(f"  Post-closing ruleset: {post_closing['evaluated_count']} evaluated, "
              f"{post_closing['not_applicable_count']} NOT_APPLICABLE (hidden), "
              f"{post_closing['surfaced_count']} surfaced", flush=True)
        for r in post_closing["surfaced_results"]:
            flag = " [AMBIGUOUS PROGRAM]" if r.get("ambiguous_program") else ""
            print(f"    [{r['status']}]{flag} {r['check_id']}: {r['message']}", flush=True)

        baseline = run_baseline_for_loan(loan)
        print(f"  Validated baseline (32-check): disposition={baseline['disposition']}, "
              f"{baseline['summary']['qc_failures']} qc_failures", flush=True)

        combined["loans"][loan.loan_id] = {
            "post_closing": post_closing,
            "baseline": baseline,
        }

    out_path = os.path.join(HERE, "combined_results.json")
    with open(out_path, "w") as f:
        json.dump(combined, f, indent=2)
    print(f"\n[written] {out_path}")


if __name__ == "__main__":
    main()
