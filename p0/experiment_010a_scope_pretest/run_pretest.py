"""
Pre-test: does program_gating.py's mechanism, run against real compiled
checks and the 5 real synthetic loans, actually narrow to the "5 loans'
scope" decided in output/RULE-PROGRAM-GATING-FINDINGS.md SS8?

Zero new Bedrock spend -- reuses the 24 real, already-compiled checks from
experiment_002a/artifacts/compiled_drafts.json (a real compile-fidelity spike
run 2026-07-01), which already spans FHA/VA/USDA/Fannie Mae/Freddie Mac.
This is a real proof of the gating mechanism against real compiled output and
real loan fixtures, not a new synthetic exercise.

Applies the SS8 pre-test override explicitly (loan 01 and loan 04 both
resolved to Fannie Mae) rather than relying on program_gating._loan_program's
natural resolution -- which this run discovered treats loan 04 as
unambiguously Freddie Mac purely because build_fixtures.py's descriptive
loan_type label happens to contain the substring "Freddie Mac". That's a
real, separate finding (flagged in RESULTS.md), not fixed here.

Usage (from p0/):
    python3 experiment_010a_scope_pretest/run_pretest.py
Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
P0 = os.path.dirname(HERE)
sys.path.insert(0, P0)

from qc_engine.compiler import program_gating as PG
from fixtures.from_docs import fixture_loader

COMPILED_DRAFTS_PATH = os.path.join(P0, "experiment_002a", "artifacts", "compiled_drafts.json")
LOAN_FIXTURE_DIR = os.path.join(P0, "fixtures", "from_docs")

# SS8 pre-test override (output/RULE-PROGRAM-GATING-FINDINGS.md): neither loan
# 01 nor loan 04's real MISMO data carries a GSE-investor field: both are
# genuinely ambiguous Fannie/Freddie. Assumed Fannie Mae for this pre-test
# only -- applied explicitly here, NOT read off build_fixtures.py's
# descriptive loan_type label (which resolves loan 04 to Freddie Mac today,
# a separate finding -- see RESULTS.md).
LOAN_PROGRAM_OVERRIDE = {
    "loan_01": "Fannie Mae",
    "loan_02": None,  # real signal, no override needed
    "loan_03": None,
    "loan_04": "Fannie Mae",
    "loan_05": None,
}


def _effective_loan_program(loan_key: str, loan) -> str:
    override = LOAN_PROGRAM_OVERRIDE.get(loan_key)
    if override is not None:
        return override
    return PG._loan_program(loan.loan_type)


def run_pretest() -> Dict[str, Any]:
    drafts = json.load(open(COMPILED_DRAFTS_PATH))["drafts"]
    loans = {
        key: fixture_loader.load_canonical_loan(os.path.join(LOAN_FIXTURE_DIR, f"{key}.json"))
        for key in ["loan_01", "loan_02", "loan_03", "loan_04", "loan_05"]
    }

    # What each loan's effective program is under the SS8 pre-test scope.
    loan_programs = {k: _effective_loan_program(k, v) for k, v in loans.items()}

    # For each of the 24 real compiled checks: which program does its source
    # row's Exception Code carry, and which of the 5 loans would it apply to
    # under the pre-test's effective programs?
    check_rows: List[Dict[str, Any]] = []
    for d in drafts:
        code = d["_source_row"].get("exception_code")
        check_program = PG.parse_exception_code_prefix(code)
        applicable_loans = [
            k for k, prog in loan_programs.items()
            if check_program is not None and check_program == prog
        ]
        check_rows.append({
            "row_id": d["row_id"],
            "check_id": d["check"]["id"],
            "exception_code": code,
            "check_program": check_program,
            "applicable_loans": applicable_loans,
        })

    relevant = [c for c in check_rows if c["applicable_loans"]]
    untagged_or_out_of_scope = [c for c in check_rows if not c["applicable_loans"]]

    per_loan_counts = {k: 0 for k in loans}
    for c in relevant:
        for k in c["applicable_loans"]:
            per_loan_counts[k] += 1

    return {
        "loan_programs_effective": loan_programs,
        "total_real_compiled_checks": len(check_rows),
        "relevant_to_5_loans": len(relevant),
        "dropped_untagged_or_out_of_scope": len(untagged_or_out_of_scope),
        "per_loan_check_counts": per_loan_counts,
        "relevant_checks": relevant,
        "dropped_checks": untagged_or_out_of_scope,
    }


def _write_results_md(result: Dict[str, Any], path: str) -> None:
    lines = [
        "# 010a Scope Pre-Test — Results",
        "",
        "Real proof, zero new Bedrock spend: reuses the 24 already-compiled real",
        "checks from `experiment_002a` (2026-07-01 compile-fidelity spike) and",
        "runs `program_gating.py`'s real applicability mechanism against the 5",
        "real synthetic loan fixtures, under the `RULE-PROGRAM-GATING-FINDINGS.md`",
        "§8 pre-test assumption (loan 01 + loan 04 assumed Fannie Mae).",
        "",
        "## Finding: a real fixture-label bug, surfaced by this pre-test",
        "",
        "`program_gating._loan_program()` reads `CanonicalLoan.loan_type` — a",
        "hand-typed descriptive string, not a value derived from the loan's real",
        "MISMO data. Loan 04's label (`\"Freddie Mac Cash-Out Refi\"`, set in",
        "`build_fixtures.py`'s `LOAN_PACKAGES`) happens to contain the substring",
        "`\"Freddie Mac\"`, so **the code today resolves loan 04 to Freddie Mac",
        "unambiguously — not `AMBIGUOUS`** — purely because of that label, even",
        "though loan 04's real MISMO `<MortgageType>` is just `\"Conventional\"`,",
        "identical in kind to loan 01's genuinely-ambiguous case. Loan 01's label",
        "(`\"Conventional Purchase\"`) carries no GSE marker, so it correctly",
        "resolves to `None`/ambiguous. The two loans are equally undetermined by",
        "real data; only one of their fixture labels happens to leak an answer.",
        "",
        "This pre-test does NOT fix that — it applies the §8 assumption via an",
        "explicit override (`LOAN_PROGRAM_OVERRIDE` in this script) instead of",
        "trusting the label, so the pre-test's own scope decision is honored",
        "consistently for both loans. The underlying fixture-label bug is a",
        "separate, real finding for `build_fixtures.py` — flagged, not fixed",
        "here, since `010a`'s own test (`test_program_applicability_gating.py`)",
        "explicitly mirrors this exact label as its Freddie-tagged test case and",
        "a fix needs to account for that.",
        "",
        "## Effective program per loan (this pre-test)",
        "",
    ]
    for k, v in result["loan_programs_effective"].items():
        lines.append(f"- `{k}`: **{v}**")
    lines += [
        "",
        "## Result",
        "",
        f"- Real compiled checks available (from `002a`): {result['total_real_compiled_checks']}",
        f"- Relevant to the 5 loans under this scope: **{result['relevant_to_5_loans']}**",
        f"- Dropped (untagged prefix, e.g. TILA/COVID19-FRD/FAMCO, or Freddie Mac "
        f"now out of scope): {result['dropped_untagged_or_out_of_scope']}",
        "",
        "## Per-loan applicable-check counts (of the 24)",
        "",
    ]
    for k, c in result["per_loan_check_counts"].items():
        lines.append(f"- `{k}`: {c} checks")
    lines += [
        "",
        "## Relevant checks (real compiled Check IDs, tied to real loans)",
        "",
    ]
    for c in result["relevant_checks"]:
        lines.append(
            f"- `{c['check_id']}` ({c['exception_code']}, {c['check_program']}) "
            f"-> applies to: {', '.join(c['applicable_loans'])}"
        )
    lines += [
        "",
        "## Dropped checks (untagged prefix or out of pre-test scope)",
        "",
    ]
    for c in result["dropped_checks"]:
        lines.append(f"- `{c['check_id']}` ({c['exception_code']}, program={c['check_program']})")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main() -> None:
    result = run_pretest()
    print(json.dumps(
        {k: v for k, v in result.items() if k not in ("relevant_checks", "dropped_checks")},
        indent=2,
    ))
    results_path = os.path.join(HERE, "RESULTS.md")
    _write_results_md(result, results_path)
    print(f"\n[written] {results_path}")


if __name__ == "__main__":
    main()
