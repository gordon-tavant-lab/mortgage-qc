"""
run_015 -- the real comprehensive-rulebook QC run for loan 01 Gordon asked
for directly (2026-07-28): "run a QC process for loan 01 with the
comprehensive Fannie Mae's rulebook, not the 32-check hand-authored test
harness... create a new result called loan_01_all.json."

Two honest scoping notes, stated up front rather than buried in the output:

1. "The comprehensive rulebook" here is `comprehensive_e2e_v6_ruleset.json`
   (3,203 checks), not the raw `post_closing_only_ruleset.json` (5,093
   checks) -- the former has already been through the 002d
   operator-consistency gate (excludes the known 45+3 operator-direction-
   inverted checks) and 002g precondition/applies_if wiring; the latter has
   neither applied wholesale (only one hand-added applies_if entry from
   010b's session today). Running the *unvetted* raw compile as "the real
   test" would silently include checks already known to be buggy.

2. Loan 01's own `loan_type` is "Conventional Purchase" -- it names no
   specific GSE. `qc_engine.compiler.program_gating.applies_to()` returns
   its explicit `AMBIGUOUS` sentinel (not True or False) for any
   Fannie-Mae- or Freddie-Mac-tagged check against a loan like this, by
   design (spec `010a`'s FR-005) -- it is genuinely unknown whether this
   loan is a Fannie Mae loan or a Freddie Mac loan from the data alone.
   Per Gordon's explicit request to scope to "Fannie Mae's rulebook," this
   run treats every Fannie-Mae-tagged (or untagged/universal) check as
   in-scope and every Freddie-Mac/FHA/VA/USDA-tagged check as out-of-scope
   for the `fannie_mae_scope` view below -- but the full, unfiltered,
   all-3,203-check run is ALSO written to the same output file, so nothing
   is silently dropped and the Fannie/Freddie ambiguity stays visible
   rather than quietly resolved in one direction.

Inputs:
- `result/loans/loan_01.json` -- canonical, fully-cited extraction (same
  file used by the corrected 014 decision-narrative run).
- `storage/loan_profiles/v3/loan_01.json` -- 010b's latest derived facts
  (occupancy_type, gift_funds_used, loan_transaction_type,
  appraisal_in_file) layered on top, same pattern every other driver in
  this project uses.
- `result/rules/comprehensive_e2e_v6_ruleset.json` -- the vetted
  comprehensive ruleset (see note 1).
- `result/rules/post_closing_only_applicability.json` -- check_id -> [program]
  tags, used only for the Fannie-Mae-scope slice and reporting; never
  changes which checks the engine itself runs (that's the full 3,203).
  (spec 015 Issue 3: switched from `comprehensive_applicability.json`, which
  only tagged 61% of `comprehensive_e2e_v6_ruleset.json`'s check IDs -- this
  file has verified 100% ID coverage, so Fannie/Freddie scoping no longer
  silently falls back to "untagged" for checks that actually have a tag.)

Output: `result/qc_results/loan_01_all.json`

Run: python3 p0/compile_runs/run_015_loan_01_comprehensive_qc/build_and_run.py
Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_P0 = os.path.dirname(os.path.dirname(_HERE))
_REPO_ROOT = os.path.dirname(_P0)
for p in (_P0, os.path.join(_P0, "fixtures", "from_docs")):
    if p not in sys.path:
        sys.path.insert(0, p)

from fixture_loader import load_canonical_loan                          # noqa: E402
from qc_engine.compiler.program_gating import applies_to, Applicability, AMBIGUOUS  # noqa: E402
from qc_engine.engine import run                                        # noqa: E402
from qc_engine.eval_log import EvalLog                                  # noqa: E402
from qc_engine.model import SourceValue                                 # noqa: E402
from qc_engine.ruleset import Check, Ruleset                            # noqa: E402

RUN_ID = "run_015_loan_01_comprehensive_qc"
LOAN_ID = "loan_01"
LOAN_FACTS_PATH = os.path.join(_REPO_ROOT, "result", "loans", "loan_01.json")
LOAN_PROFILE_V3_PATH = os.path.join(_REPO_ROOT, "storage", "loan_profiles", "v3", "loan_01.json")
RULESET_PATH = os.path.join(_REPO_ROOT, "result", "rules", "comprehensive_e2e_v6_ruleset.json")
APPLICABILITY_PATH = os.path.join(_REPO_ROOT, "result", "rules", "post_closing_only_applicability.json")
RESULT_OUT = os.path.join(_REPO_ROOT, "result", "qc_results", "loan_01_all.json")

_FANNIE_OR_UNTAGGED = ("Fannie Mae", "UNTAGGED")


def _load_ruleset():
    with open(RULESET_PATH) as f:
        wrapper = json.load(f)
    content = wrapper["content"]
    checks = [Check(**c) for c in content["checks"]]
    return Ruleset(ruleset_id=content["ruleset_id"], version=content["version"], checks=checks), wrapper


def _load_loan():
    loan = load_canonical_loan(LOAN_FACTS_PATH)
    with open(LOAN_PROFILE_V3_PATH) as f:
        profile = json.load(f)
    for fact_name, entry in profile.get("derived_facts", {}).items():
        loan.fields[fact_name] = SourceValue(doc=entry["value"])
    return loan


def _program_classification(check_id, loan, applicability_map):
    """Returns (programs_tagged_or_None, classification) where classification
    is one of: APPLIES / DOES_NOT_APPLY / AMBIGUOUS / UNTAGGED / NO_TAG_FOUND
    (the last meaning this check_id isn't present in the applicability map at
    all -- a real cross-compile-generation ID mismatch, not silently ignored)."""
    programs = applicability_map.get(check_id)
    if programs is None:
        return None, "NO_TAG_FOUND"
    if programs == ["UNTAGGED"]:
        return programs, "UNTAGGED"
    results = set()
    for p in programs:
        a = Applicability(program=p)
        r = applies_to(loan, a)
        results.add("AMBIGUOUS" if r is AMBIGUOUS else r)
    if "AMBIGUOUS" in results:
        return programs, "AMBIGUOUS"
    if True in results:
        return programs, "APPLIES"
    return programs, "DOES_NOT_APPLY"


def main():
    log = EvalLog(RUN_ID)
    log.log("setup", "run_started",
            purpose="run the comprehensive rulebook against loan 01 (Gordon's direct "
                    "request), full run + Fannie-Mae-scoped view")

    loan = _load_loan()
    ruleset, ruleset_wrapper = _load_ruleset()
    print("Loan {}: loan_type={!r}".format(loan.loan_id, loan.loan_type))
    print("Ruleset: {} checks ({})".format(len(ruleset.checks), RULESET_PATH))
    log.log("setup", "loan_and_ruleset_loaded", loan_id=loan.loan_id,
            loan_type=loan.loan_type, ruleset_id=ruleset.ruleset_id,
            total_checks=len(ruleset.checks))

    result = run(loan, ruleset)
    log.log("qc_execution", "engine_run_complete", disposition=result.disposition,
            total_results=len(result.results))

    with open(APPLICABILITY_PATH) as f:
        applicability_map = json.load(f)

    full_results = []
    fannie_scope_results = []
    program_tag_counts = {}
    classification_counts = {}

    for r in result.results:
        programs, classification = _program_classification(r.check_id, loan, applicability_map)
        entry = r.to_dict() if hasattr(r, "to_dict") else dict(vars(r))
        entry["program_tags"] = programs
        entry["program_classification"] = classification
        full_results.append(entry)
        classification_counts[classification] = classification_counts.get(classification, 0) + 1
        for p in (programs or []):
            program_tag_counts[p] = program_tag_counts.get(p, 0) + 1
        log.log_evidence_chain(
            entity_id=r.check_id, input_={"programs_tagged": programs, "status": r.status},
            method="_program_classification", verdict=classification,
            stage="program_classification")
        # NO_TAG_FOUND is deliberately excluded here -- it means this check_id
        # isn't in post_closing_only_applicability.json at all (a real cross-compile
        # ID mismatch), i.e. its program is UNKNOWN, not confirmed universal.
        # Silently folding "unknown" into "Fannie Mae scope" would be exactly
        # the kind of quiet ambiguity-resolution program_gating.py's own
        # AMBIGUOUS sentinel exists to prevent -- report it separately instead
        # (see "no_program_tag_found" below), never as if it were in-scope.
        if classification == "UNTAGGED" or (
            programs and any(p in _FANNIE_OR_UNTAGGED for p in programs)
        ):
            fannie_scope_results.append(entry)

    log.log("program_classification", "summary",
            classification_counts=classification_counts,
            program_tag_counts=program_tag_counts,
            fannie_scope_size=len(fannie_scope_results))

    def _summarize(entries):
        from collections import Counter
        status_counts = Counter(e["status"] for e in entries)
        review_reason_counts = Counter(e.get("review_reason") for e in entries if e.get("review_reason"))
        fails = [e for e in entries if e["status"] == "FAIL"]
        needs_review = [e for e in entries if e["status"] == "NEEDS_REVIEW"]
        return {
            "total_checks": len(entries),
            "status_counts": dict(status_counts),
            "review_reason_counts": dict(review_reason_counts),
            "fail_count": len(fails),
            "needs_review_count": len(needs_review),
        }

    out = {
        "run": "run_015_loan_01_comprehensive_qc",
        "loan_id": loan.loan_id,
        "loan_type": loan.loan_type,
        "ruleset_source": "result/rules/comprehensive_e2e_v6_ruleset.json (3,203 checks -- "
                          "already 002d operator-gated + 002g precondition-wired; NOT the "
                          "32-check fixtures/ruleset_defects.py validated baseline)",
        "ruleset_id": ruleset.ruleset_id,
        "ruleset_version": ruleset.version,
        "ruleset_sha256": result.ruleset_sha256,
        "disposition_full_run": result.disposition,
        "review_reasons_full_run": sorted(result.review_reasons),
        "honest_program_ambiguity_note": (
            "loan_01.loan_type is 'Conventional Purchase' -- it names no specific GSE. Every "
            "check tagged 'Fannie Mae' or 'Freddie Mac' in post_closing_only_applicability.json "
            "resolves to program_gating.py's explicit AMBIGUOUS sentinel for this loan, by "
            "design (it is genuinely unknown from the loan's own data whether Fannie or "
            "Freddie owns it). 'fannie_mae_scope' below includes every Fannie-Mae-tagged "
            "check (ambiguous-but-Fannie-eligible) plus every confirmed-UNTAGGED (fails-open, "
            "universal) check -- it does NOT confirm this loan actually is a Fannie Mae loan, "
            "only that it's in-scope under a Fannie Mae reading, per Gordon's explicit request "
            "to scope this way. Freddie-Mac/FHA/VA/USDA-tagged checks are excluded from this "
            "scope. Checks with NO_TAG_FOUND classification (this ruleset's check_id isn't "
            "present at all in post_closing_only_applicability.json -- a real cross-compile-"
            "generation ID mismatch, see full_run.program_classification_counts) are ALSO "
            "excluded from fannie_mae_scope, deliberately -- their real program is unknown, not "
            "confirmed universal, so folding them in would silently resolve an ambiguity this "
            "note exists to keep visible. Every individual check's classification (including "
            "NO_TAG_FOUND ones) is still inspectable per-entry in full_run.results."
        ),
        "full_run": {
            "summary": _summarize(full_results),
            "program_tag_counts": program_tag_counts,
            "program_classification_counts": classification_counts,
            "results": full_results,
        },
        "fannie_mae_scope": {
            "summary": _summarize(fannie_scope_results),
            "results": fannie_scope_results,
        },
    }

    os.makedirs(os.path.dirname(RESULT_OUT), exist_ok=True)
    with open(RESULT_OUT, "w") as f:
        json.dump(out, f, indent=2, default=str)
    log.log("setup", "run_finished", results_path=RESULT_OUT,
            full_run_summary=out["full_run"]["summary"],
            fannie_scope_summary=out["fannie_mae_scope"]["summary"],
            cost={"llm_calls": 0, "cost_usd": 0.0})

    print()
    print("=== FULL RUN (all {} checks, all programs) ===".format(len(full_results)))
    print("disposition:", result.disposition)
    print("status_counts:", out["full_run"]["summary"]["status_counts"])
    print("program_classification_counts:", classification_counts)
    print()
    print("=== FANNIE MAE SCOPE ({} checks: Fannie-tagged + untagged/universal) ===".format(
        len(fannie_scope_results)))
    print("status_counts:", out["fannie_mae_scope"]["summary"]["status_counts"])
    print()
    print("wrote", RESULT_OUT)
    print("full structured audit trail:", log.path)


if __name__ == "__main__":
    main()
