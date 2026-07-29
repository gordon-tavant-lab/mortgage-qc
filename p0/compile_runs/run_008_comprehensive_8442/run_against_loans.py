"""
Runs the comprehensive compiled ruleset against all 5 parsed loan fixtures,
program-gated per loan, alongside the existing validated 21-check baseline
(ruleset_defects.py), and writes a combined report.

Two honesty notes, surfaced in the output rather than hidden:

1. DEDUPLICATION: the compiled ruleset has far more check INSTANCES than
   unique check IDS -- the real AMQ workbooks restate the same condition
   across each program's own sheet (FHA/VA/USDA/Freddie/Fannie each have
   their own row for e.g. "AUS income categorization matches"). Running
   every instance would show the same real-world check firing dozens of
   times per loan for one condition. Deduplicated to one representative per
   id (first occurrence) before running -- unique-id count is the honest
   "how many different rules exist" number.

2. PROGRAM GATING: the first comprehensive-compile attempt did not persist
   which program each compiled check belongs to, discovered when running
   it unfiltered produced hundreds of false "FAIL"s (predicate checks
   correctly treat a missing field as FAIL when pre-gated -- but flood a
   report with irrelevant defects when run ungated against checks that
   were never in scope for a given loan's program). Fixed by recompiling
   with per-check-id -> program set persisted (applicability.json), then
   filtering here using the EXISTING, already-tested program_gating.py
   (program_gating.applies_to()) -- the same gate ruleset_defects.py's own
   defects_ruleset_for() already uses for the validated 21-check baseline,
   not a new/reinvented gating mechanism.

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
P0 = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, P0)
sys.path.insert(0, os.path.join(P0, "fixtures", "from_docs"))

from qc_engine.ruleset import Ruleset, Check
from qc_engine.catalog import load_catalog
from qc_engine import engine as ENGINE
from qc_engine.compiler import program_gating as PG
from fixture_loader import load_canonical_loan
from fixtures.ruleset_defects import defects_ruleset_for

FIXTURES_DIR = os.path.join(P0, "fixtures", "from_docs")
COMPREHENSIVE_RULESET_PATH = os.path.join(HERE, "ruleset.json")
APPLICABILITY_PATH = os.path.join(HERE, "applicability.json")
CATALOG_PATH = os.path.join(P0, "qc_engine", "field_catalog.json")
RESULT_DIR = os.path.normpath(os.path.join(P0, "..", "result"))
PREFUNDING_IDS_PATH = os.path.join(RESULT_DIR, "rules", "prefunding_check_ids.json")


def load_deduplicated_comprehensive_ruleset():
    raw = json.load(open(COMPREHENSIVE_RULESET_PATH))
    full_ruleset = Ruleset.from_dict(raw)
    applicable_programs: Dict[str, List[str]] = json.load(open(APPLICABILITY_PATH))

    seen_ids = set()
    deduped: List[Check] = []
    for c in full_ruleset.checks:
        if c.id in seen_ids:
            continue
        seen_ids.add(c.id)
        deduped.append(c)

    # SCOPE-MISMATCH FILTER: these 5 synthetic loans were built to test 25
    # specific planted defects and carry ~377 known fields total
    # (field_catalog.json) -- nowhere near the breadth of document types a
    # truly comprehensive lender AMQ checklist references (asset types,
    # entity/trust structures, LEP, private-bank guidelines, etc. this
    # dataset never modeled at all). Confirmed by direct count: only 150 of
    # 4,616 unique compiled checks (3.2%) reference a field_name that
    # exists anywhere in the catalog -- the other 96.8% reference fields
    # these loans could NEVER have data for, so predicate.is_true/is_present
    # (which treats a missing field as FAIL, correctly, when pre-gated)
    # would flood every loan with false "defects" that are really just
    # "this loan's fixture was never built to answer this question," not a
    # real finding. Restricting to catalog-known fields is what makes the
    # comprehensive ruleset's *actual applicable subset* to these loans
    # meaningfully reviewable, rather than 96.8% guaranteed noise.
    catalog = load_catalog(CATALOG_PATH)
    catalog_fields = set(e.field_name for e in catalog.entries)
    in_scope = [c for c in deduped if c.field_name in catalog_fields]

    # PRE-FUNDING EXCLUSION: this project is post-closing QC only (CLAUDE.md).
    # The original comprehensive compile (before this distinction was caught)
    # mixed ~3,344 pre-funding-derived rows in with the 5,098 post-closing
    # rows across the same source workbooks. run_009_prefunding_exclusion/
    # identified which resulting check IDs came from pre-funding rows by
    # re-compiling those rows in isolation (relying on confirmed temp=0
    # determinism) and cross-referencing against this ruleset -- exclude
    # those here so no pre-funding-derived check is ever evaluated against
    # a loan, even though the underlying compiled artifact still contains them.
    prefunding_data = json.load(open(PREFUNDING_IDS_PATH))
    prefunding_exclude_ids = set(prefunding_data["exclude_from_qc_runs"])
    post_closing_only = [c for c in in_scope if c.id not in prefunding_exclude_ids]

    dedup_stats = {
        "total_compiled": len(full_ruleset.checks),
        "unique_ids": len(deduped),
        "in_catalog_scope": len(in_scope),
        "out_of_scope_no_field_data_possible": len(deduped) - len(in_scope),
        "excluded_prefunding_derived": len(in_scope) - len(post_closing_only),
        "post_closing_only_final": len(post_closing_only),
    }
    ruleset = Ruleset(ruleset_id="rs-comprehensive-post-closing-only", version=1, checks=post_closing_only)
    return ruleset, applicable_programs, dedup_stats, catalog


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


def run_comprehensive_for_loan(ruleset: Ruleset, applicable_programs: Dict[str, List[str]], loan,
                                catalog=None) -> Dict[str, Any]:
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

    gated_ruleset = Ruleset(ruleset_id="rs-comprehensive-gated", version=1, checks=gated_checks)
    result = ENGINE.run(loan, gated_ruleset, catalog=catalog)
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


def run_baseline_for_loan(loan, catalog=None) -> Dict[str, Any]:
    rs = defects_ruleset_for(loan)
    result = ENGINE.run(loan, rs, catalog=catalog)
    return result.to_dict()


def main() -> None:
    ruleset, applicable_programs, dedup_stats, catalog = load_deduplicated_comprehensive_ruleset()
    print(f"Deduplicated comprehensive ruleset: {dedup_stats['total_compiled']} compiled -> "
          f"{dedup_stats['unique_ids']} unique checks", flush=True)
    print(f"Scope filter: {dedup_stats['in_catalog_scope']} checks reference a field this dataset "
          f"could possibly have ({dedup_stats['out_of_scope_no_field_data_possible']} excluded -- "
          f"no field data possible for these 5 loans)", flush=True)
    print(f"Pre-funding exclusion: {dedup_stats['excluded_prefunding_derived']} checks excluded "
          f"(post-closing only, per project scope) -> {dedup_stats['post_closing_only_final']} "
          f"checks in the final ruleset run against loans", flush=True)

    loan_files = sorted(f for f in os.listdir(FIXTURES_DIR) if f.startswith("loan_") and f.endswith(".json"))

    combined = {"dedup_stats": dedup_stats, "loans": {}}
    for lf in loan_files:
        loan = load_canonical_loan(os.path.join(FIXTURES_DIR, lf))
        print(f"\n=== {loan.loan_id} ({lf}, loan_type={loan.loan_type!r}) ===", flush=True)

        comprehensive = run_comprehensive_for_loan(ruleset, applicable_programs, loan, catalog=catalog)
        print(f"  Program gate: {comprehensive['skipped_by_program_gate']} skipped, "
              f"{comprehensive['gated_in_count']} gated in ({comprehensive['ambiguous_program_count']} ambiguous)", flush=True)
        print(f"  Comprehensive ruleset: {comprehensive['evaluated_count']} evaluated, "
              f"{comprehensive['not_applicable_count']} NOT_APPLICABLE (hidden), "
              f"{comprehensive['surfaced_count']} surfaced", flush=True)
        for r in comprehensive["surfaced_results"]:
            flag = " [AMBIGUOUS PROGRAM]" if r.get("ambiguous_program") else ""
            print(f"    [{r['status']}]{flag} {r['check_id']}: {r['message']}", flush=True)

        baseline = run_baseline_for_loan(loan, catalog=catalog)
        print(f"  Validated baseline (21-check): disposition={baseline['disposition']}, "
              f"{baseline['summary']['qc_failures']} qc_failures", flush=True)

        combined["loans"][loan.loan_id] = {
            "comprehensive": comprehensive,
            "baseline": baseline,
        }

    out_path = os.path.join(HERE, "combined_results.json")
    with open(out_path, "w") as f:
        json.dump(combined, f, indent=2)
    print(f"\n[written] {out_path}")


if __name__ == "__main__":
    main()
