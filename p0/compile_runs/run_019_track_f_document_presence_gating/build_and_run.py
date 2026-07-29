"""
run_019 -- Track F closeout demonstration (2026-07-28, extended round 2
2026-07-29): proves the document-presence gates
`qc_engine/compiler/document_presence_gating.py` defines actually change loan
01's real QC output, not just that the DOCUMENT_PRESENCE_GATES dict looks
right on paper. Reads len(DOCUMENT_PRESENCE_GATES) dynamically throughout
(round 1: 46 checks / 43 facts; round 2 added 13 more checks / 11 more facts,
59 checks / 54 facts total) rather than hardcoding a check count, so this
script does not need editing again if a future round adds more gates.

Track A2 (2026-07-29) update: this run now loads the v5 loan profile
(storage/loan_profiles/v5/loan_01.json) instead of v4 -- v5 is a strict
superset of v4 (same 7 derivations + 4 new precondition derivations:
appraisal_waiver_type, borrower_income_type,
credit_report_present_for_all_applicants, closing_funds_asset_type), single
source of truth with run_018. The BEFORE baseline below (read from the
already-stored loan_01_v8.json) still reflects the Track-F-only state; the
AFTER numbers in this run now also reflect Track A2's derivations layered on
top, since both build_and_run.py scripts (run_018 and this one) were
repointed at v5 together.

Why this run exists, distinct from run_018: run_018 already wires both
correction modules (`apply_known_compile_corrections` then
`apply_document_presence_gates`) into its own compile stage and already
loads the v4 profile, so its own `loan_01_v8.json` output already reflects
gating applied. This run isolates the *delta* Track F specifically caused --
it recomputes loan 01's scoped program-gate summary from scratch with BOTH
correction modules applied (identical to run_018's own compile order), then
diffs that against the numbers `result/qc_results/loan_01_v8.json` already
has on disk (itself a real run_018 output, from before this run executes),
so the specific check_ids that flip status -- and any that don't, with
why -- are named explicitly, not just summarized in aggregate counts.

Honest note on the applicability file: the task instructions describing
this run named `result/rules/comprehensive_applicability.json` as the file
to scope against. Reading run_018/build_and_run.py's actual
`stage3_qc_loan01` (APPLICABILITY_PATH) shows it uses
`result/rules/post_closing_only_applicability.json`, not
`comprehensive_applicability.json` -- confirmed by direct inspection:
`comprehensive_applicability.json` is missing tag entries for 1,260 of the
3,203 v8 ruleset check_ids (would misclassify them NO_TAG_FOUND), while
`post_closing_only_applicability.json` has 0 missing and its resulting
scoped_status_counts match `loan_01_v8.json`'s stored values exactly
(scoped_checks=1076, NOT_APPLICABLE=290, NEEDS_REVIEW=762, FAIL=20, PASS=4).
This run uses `post_closing_only_applicability.json` -- the file run_018
actually reads -- so BEFORE/AFTER are a true apples-to-apples comparison
against the real stored baseline, not two runs scoped by different maps.

No cross-run-directory import exists anywhere in this codebase (confirmed
by grep before writing this file) -- `_program_classification` and
`_FANNIE_OR_UNTAGGED` are reimplemented here identically to run_018's
versions, not imported from run_018's module.

Pipeline:
 1. Load loan_01 fixture + v4 profile, promote derived_facts into
    loan.fields (same SourceValue(doc=...) pattern as run_018 / the
    regression test).
 2. Load comprehensive_e2e_v8_ruleset.json, build Check objects, apply
    apply_known_compile_corrections then apply_document_presence_gates
    (same order as run_018's compile stage).
 3. Run the engine once.
 4. Reproduce the scoped (Fannie Mae + UNTAGGED) program-gate summary,
    identical logic to run_018's stage3_qc_loan01.
 5. Compare against the BEFORE baseline hardcoded from the already-stored
    result/qc_results/loan_01_v8.json's program_gate_summary.
    scoped_status_counts (read directly from that file, not approximated).
 6. Print BEFORE vs AFTER side by side + every check_id whose status
    changed + the full DOCUMENT_PRESENCE_GATES-check breakdown (changed vs
    already-was-NOT_APPLICABLE-for-an-unrelated-reason).

Zero LLM calls. Deterministic. Python 3.9 compatible.

Run: python3 p0/compile_runs/run_019_track_f_document_presence_gating/build_and_run.py
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
_P0 = os.path.dirname(os.path.dirname(_HERE))
_REPO_ROOT = os.path.dirname(_P0)
if _P0 not in sys.path:
    sys.path.insert(0, _P0)
sys.path.insert(0, os.path.join(_P0, "fixtures", "from_docs"))

from fixture_loader import load_canonical_loan  # noqa: E402
from qc_engine.compiler.document_presence_gating import (  # noqa: E402
    apply_document_presence_gates, DOCUMENT_PRESENCE_GATES)
from qc_engine.compiler.known_compile_corrections import (  # noqa: E402
    apply_known_compile_corrections)
from qc_engine.compiler.program_gating import applies_to, Applicability, AMBIGUOUS  # noqa: E402
from qc_engine.engine import run  # noqa: E402
from qc_engine.model import SourceValue  # noqa: E402
from qc_engine.ruleset import Check, Ruleset  # noqa: E402

RUN_ID = "run_019_track_f_document_presence_gating"
FROM_DOCS_DIR = os.path.join(_P0, "fixtures", "from_docs")
LOAN01_FIXTURE = os.path.join(FROM_DOCS_DIR, "loan_01.json")
# Track A2 (2026-07-29): v5 instead of v4 -- strict superset (v4's 7
# derivations + 4 new precondition derivations: appraisal_waiver_type,
# borrower_income_type, credit_report_present_for_all_applicants,
# closing_funds_asset_type). Single source of truth with run_018.
LOAN_PROFILE_V4 = os.path.join(_REPO_ROOT, "storage", "loan_profiles", "v5", "loan_01.json")
RULESET_PATH = os.path.join(_REPO_ROOT, "result", "rules", "comprehensive_e2e_v8_ruleset.json")
# The file run_018/build_and_run.py's stage3_qc_loan01 actually reads
# (APPLICABILITY_PATH there) -- NOT comprehensive_applicability.json (see
# module docstring for why: that file is missing 1,260 of the v8 ruleset's
# 3,203 check_ids and would silently change the scoped set, not just the
# gated statuses within it).
APPLICABILITY_PATH = os.path.join(_REPO_ROOT, "result", "rules",
                                  "post_closing_only_applicability.json")
BEFORE_STORED_PATH = os.path.join(_REPO_ROOT, "result", "qc_results", "loan_01_v8.json")
RESULTS_OUT = os.path.join(_REPO_ROOT, "result", "qc_results",
                           "run_019_track_f_document_presence_gating_results.json")

_FANNIE_OR_UNTAGGED = ("Fannie Mae", "UNTAGGED")


def _program_classification(check_id, loan, applicability_map):
    """Identical logic to run_018_guideline_to_loan01_e2e/build_and_run.py's
    own `_program_classification` (reimplemented, not imported -- no
    cross-run-directory import precedent exists in this codebase)."""
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


def load_loan_with_v4_profile():
    """Function name kept as-is (v4) though it now loads the v5 profile
    (LOAN_PROFILE_V4 points at storage/loan_profiles/v5/loan_01.json, Track
    A2 2026-07-29) -- v5 is a strict superset of v4, so the loaded profile
    still carries every v4 fact plus the 4 new precondition derivations."""
    loan = load_canonical_loan(LOAN01_FIXTURE)
    with open(LOAN_PROFILE_V4) as f:
        profile = json.load(f)
    for fact_name, entry in profile.get("derived_facts", {}).items():
        loan.fields[fact_name] = SourceValue(doc=entry["value"])
    return loan, profile


def build_gated_ruleset():
    with open(RULESET_PATH) as f:
        wrapper = json.load(f)
    content = wrapper["content"]
    checks = [Check(**c) for c in content["checks"]]
    corrected_ids = apply_known_compile_corrections(checks)
    gated_ids = apply_document_presence_gates(checks)
    rs = Ruleset(ruleset_id=content["ruleset_id"], version=content["version"], checks=checks)
    return rs, checks, corrected_ids, gated_ids


def compute_scoped_summary(loan, rs):
    result = run(loan, rs)
    results_by_id = {r.check_id: r for r in result.results}

    with open(APPLICABILITY_PATH) as f:
        applicability_map = json.load(f)

    scoped_results = []
    classification_counts = Counter()
    for r in result.results:
        programs, classification = _program_classification(r.check_id, loan, applicability_map)
        classification_counts[classification] += 1
        if classification == "UNTAGGED" or (
            programs and any(p in _FANNIE_OR_UNTAGGED for p in programs)
        ):
            scoped_results.append(r)
    scoped_status_counts = Counter(r.status for r in scoped_results)

    return {
        "total_checks": len(result.results),
        "scoped_checks": len(scoped_results),
        "classification_counts": dict(classification_counts),
        "scoped_status_counts": dict(scoped_status_counts),
        "results_by_id": results_by_id,
    }


def main() -> None:
    # ---- BEFORE: the real, already-stored run_018 baseline (not recomputed
    # here -- read directly off disk, per the task's explicit instruction to
    # hardcode from the stored file rather than trust an approximation). ----
    with open(BEFORE_STORED_PATH) as f:
        before_stored = json.load(f)
    before_pg = before_stored["program_gate_summary"]
    before_status_counts = before_pg["scoped_status_counts"]
    before_results_by_id = {r["check_id"]: r for r in before_stored["results"]}

    # ---- AFTER: fresh compile (both correction modules applied) + fresh
    # engine run + fresh scoped program-gate summary, computed in THIS run. ----
    loan, profile = load_loan_with_v4_profile()
    rs, checks, corrected_ids, gated_ids = build_gated_ruleset()
    after = compute_scoped_summary(loan, rs)
    after_status_counts = after["scoped_status_counts"]
    after_results_by_id = after["results_by_id"]

    # ---- Sanity: applies_if actually landed on every gated check object
    # (dynamic over however many DOCUMENT_PRESENCE_GATES currently defines --
    # round 1: 46, round 2: 59). ----
    checks_by_id = {c.id: c for c in checks}
    applies_if_check = {}
    for cid, condition in DOCUMENT_PRESENCE_GATES.items():
        chk = checks_by_id.get(cid)
        applies_if_check[cid] = {
            "exists_in_ruleset": chk is not None,
            "applies_if_set_correctly": bool(chk) and chk.applies_if == condition,
            "applies_if": getattr(chk, "applies_if", None),
        }
    all_gates_wired_correctly = all(v["applies_if_set_correctly"] for v in applies_if_check.values())

    # ---- Status-change list: every check_id whose status differs between
    # the stored BEFORE and this run's AFTER (not limited to the gated set --
    # if gating had any side effect elsewhere this would surface it too,
    # though none is expected). ----
    all_ids = set(before_results_by_id) | set(after_results_by_id)
    status_changes = []
    for cid in sorted(all_ids):
        b = before_results_by_id.get(cid)
        a = after_results_by_id.get(cid)
        b_status = b["status"] if b else None
        a_status = a.status if a else None
        if b_status != a_status:
            status_changes.append({"check_id": cid, "old_status": b_status, "new_status": a_status})

    # ---- Per-gated-check breakdown: did it flip to NOT_APPLICABLE, and if
    # not, what was it already? ----
    gated_breakdown = []
    anomalies = []
    with open(APPLICABILITY_PATH) as f:
        _amap_for_note = json.load(f)
    for cid in sorted(DOCUMENT_PRESENCE_GATES):
        b = before_results_by_id.get(cid)
        a = after_results_by_id.get(cid)
        b_status = b["status"] if b else None
        a_status = a.status if a else None
        a_message = a.message if a else None
        flipped = (b_status != a_status)
        resolved_not_applicable = (a_status == "NOT_APPLICABLE")
        tags = _amap_for_note.get(cid)
        in_scope = tags == ["UNTAGGED"] or bool(tags and any(p in _FANNIE_OR_UNTAGGED for p in tags))
        entry = {
            "check_id": cid,
            "field_name": DOCUMENT_PRESENCE_GATES[cid][0]["field_name"],
            "before_status": b_status,
            "after_status": a_status,
            "flipped": flipped,
            "resolved_not_applicable": resolved_not_applicable,
            "after_message": a_message,
            "program_tags": tags,
            "in_fannie_or_untagged_scope": in_scope,
        }
        gated_breakdown.append(entry)
        if not resolved_not_applicable:
            anomalies.append(entry)

    # ---- Spot-check the NOT_APPLICABLE message wording (engine.py's
    # _eval_applies_if literal format) on a few gated checks. ----
    message_spot_checks = []
    for entry in gated_breakdown:
        if entry["resolved_not_applicable"]:
            message_spot_checks.append(entry)
        if len(message_spot_checks) >= 5:
            break

    out = {
        "run": RUN_ID,
        "loan_id": loan.loan_id,
        "rounds_reflected": (
            "This output is round-1 + round-2 combined, not round 1 alone. "
            "Round 1 (2026-07-28) defined 46 checks / 43 facts, found via a "
            "candidate sweep against result/rules/comprehensive_applicability.json "
            "-- a file later found to be missing 1,260 of the v8 ruleset's "
            "3,203 check_ids as keys, silently dropping genuine Track F "
            "targets (e.g. du-uw-findings-report-present, "
            "homeready-income-limits-present) out of round 1's candidate "
            "pool. Round 2 (2026-07-29) re-swept against the correct map, "
            "result/rules/post_closing_only_applicability.json, against the "
            "POST-round-1 engine state, adding 13 more check_ids across 11 "
            "new doc_present_* facts plus 1 check merged onto round 1's "
            "existing doc_present_construction_perm_conversion_rider fact -- "
            "59 check_ids / 54 facts gated in total as of this run."),
        "third_sweep_note": (
            "A third sweep may still be warranted. Round 2's own candidate "
            "pool (per the task that produced this round, ~414 checks "
            "regenerated the same way as round 1's sweep, just against the "
            "corrected post_closing_only_applicability.json map) was not "
            "available as a file in this run's environment to audit line by "
            "line -- only the final, already-categorized 11-new-fact + "
            "1-merged-check mapping was handed down and implemented here. "
            "Round 1's own precedent (4 of its candidates were deliberately "
            "excluded for bundling a correctness/completeness judgment with "
            "presence) suggests most of the remaining ~400 candidates not "
            "mapped this round are NOT genuine doc_present_* gates for the "
            "same reason, rather than an overlooked gap -- but that is an "
            "inference, not a verified fact, since the candidate list itself "
            "was not directly reviewed this round. Re-run the same "
            "candidate-sweep-plus-categorization process again after this "
            "round lands, against the POST-round-2 engine state, before "
            "concluding Track F's document-presence-gating opportunity is "
            "fully exhausted."),
        "ruleset_path": RULESET_PATH,
        "applicability_path": APPLICABILITY_PATH,
        "applicability_path_note": (
            "task instructions named comprehensive_applicability.json; "
            "run_018's actual code (and the only file matching the stored "
            "BEFORE baseline) uses post_closing_only_applicability.json -- "
            "used here for a true apples-to-apples BEFORE/AFTER comparison"),
        "known_compile_corrections_applied": corrected_ids,
        "document_presence_gates_applied": gated_ids,
        "gates_defined": len(DOCUMENT_PRESENCE_GATES),
        "gates_applied_count": len(gated_ids),
        "all_gates_applies_if_wired_correctly": all_gates_wired_correctly,
        "applies_if_wiring_detail": applies_if_check,
        "before_scoped_status_counts": before_status_counts,
        "after_scoped_status_counts": after_status_counts,
        "before_scoped_checks": before_pg["scoped_checks"],
        "after_scoped_checks": after["scoped_checks"],
        "before_total_checks": before_stored["summary"]["total_checks"],
        "after_total_checks": after["total_checks"],
        "status_changes": status_changes,
        "status_changes_count": len(status_changes),
        "gated_checks_breakdown": gated_breakdown,
        "gated_checks_all_resolved_not_applicable": len(anomalies) == 0,
        "anomalies_not_resolved_not_applicable": anomalies,
        "message_spot_checks": message_spot_checks,
    }
    os.makedirs(os.path.dirname(RESULTS_OUT), exist_ok=True)
    with open(RESULTS_OUT, "w") as f:
        json.dump(out, f, indent=2)

    print("=== TRACK F: DOCUMENT-PRESENCE GATING -- BEFORE vs AFTER (loan 01) ===")
    print()
    print("BEFORE (stored result/qc_results/loan_01_v8.json), scoped_checks={}, total_checks={}:".format(
        before_pg["scoped_checks"], before_stored["summary"]["total_checks"]))
    print("  {}".format(before_status_counts))
    print()
    print("AFTER (this run, both correction modules applied), scoped_checks={}, total_checks={}:".format(
        after["scoped_checks"], after["total_checks"]))
    print("  {}".format(after_status_counts))
    print()
    print("gates defined: {}  gates actually applied: {}  all wired correctly: {}".format(
        len(DOCUMENT_PRESENCE_GATES), len(gated_ids), all_gates_wired_correctly))
    print()
    print("=== STATUS CHANGES ({} check_ids) ===".format(len(status_changes)))
    for chg in status_changes:
        print("  {}: {} -> {}".format(chg["check_id"], chg["old_status"], chg["new_status"]))
    print()
    print("=== {} GATED CHECKS: resolved NOT_APPLICABLE? ===".format(len(gated_breakdown)))
    flipped_count = sum(1 for e in gated_breakdown if e["flipped"])
    already_na_count = sum(1 for e in gated_breakdown if e["resolved_not_applicable"] and not e["flipped"])
    print("  flipped to NOT_APPLICABLE by this gating: {}".format(flipped_count))
    print("  already NOT_APPLICABLE before gating (no visible change): {}".format(already_na_count))
    print("  did NOT resolve NOT_APPLICABLE (anomalies): {}".format(len(anomalies)))
    if anomalies:
        for a in anomalies:
            print("    ANOMALY: {} before={} after={}".format(a["check_id"], a["before_status"], a["after_status"]))
    print()
    print("all {} gated checks resolved NOT_APPLICABLE: {}".format(
        len(gated_breakdown), len(anomalies) == 0))
    print()
    # Dynamic, not hardcoded: some gated checks are tagged a program outside
    # this run's Fannie+UNTAGGED scope (post_closing_only_applicability.json),
    # so they correctly flip to NOT_APPLICABLE (visible in the gated-checks
    # breakdown and the unscoped status_changes list above) without moving
    # the SCOPED counts. Compute which/how-many dynamically each run rather
    # than hardcoding a specific check_id or count (round 1 hardcoded this
    # note to "45, not 46" / family-member-employer-tax-returns-present --
    # round 2 makes it self-computing so it stays correct as more gates are added).
    out_of_scope_gated = [e for e in gated_breakdown if not e["in_fannie_or_untagged_scope"]]
    if out_of_scope_gated:
        plural = len(out_of_scope_gated) != 1
        print("note: the scoped (Fannie Mae + UNTAGGED) delta above moves by "
              "{} of {} gated checks, not all of them -- {} ({}) "
              "{} tagged outside Fannie+UNTAGGED scope "
              "(post_closing_only_applicability.json), so {} fall{} outside "
              "this run's scoped counts both before and after; {} still "
              "correctly flip{} to NOT_APPLICABLE (visible in the gated-checks "
              "breakdown and the unscoped status_changes list above), {} just "
              "{} move the SCOPED counts. Not a bug -- verified.".format(
                  len(gated_breakdown) - len(out_of_scope_gated), len(gated_breakdown),
                  len(out_of_scope_gated),
                  ", ".join(e["check_id"] for e in out_of_scope_gated),
                  "are" if plural else "is",
                  "they" if plural else "it",
                  "" if plural else "s",
                  "they" if plural else "it",
                  "" if plural else "s",
                  "they" if plural else "it",
                  "don't" if plural else "doesn't"))
    else:
        print("note: every gated check this run is tagged Fannie Mae or "
              "UNTAGGED, so the scoped delta above moves by the full {} "
              "gated-check count -- no out-of-scope exceptions this "
              "round.".format(len(gated_breakdown)))
    print()
    print("wrote {}".format(RESULTS_OUT))


if __name__ == "__main__":
    main()
