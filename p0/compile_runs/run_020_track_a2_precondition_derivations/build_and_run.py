"""
run_020 -- Track A2 closeout demonstration (2026-07-29): proves the 5 new
precondition derivations in build_loan_profiles_v5.py actually change loan
01's real QC output, not just that the derivations look right on paper.

Why this run exists, and why it does NOT reuse run_019's own BEFORE/AFTER
diff: run_019's BEFORE_STORED_PATH reads result/qc_results/loan_01_v8.json
directly off disk, on the documented assumption that file is a static,
already-stored Track-F-only snapshot. Track A2 repoints BOTH run_018 and
run_019 at the v5 profile (a strict superset of v4), so running run_018 even
once after this change overwrites that very file with POST-Track-A2 numbers
-- there is no longer a static pre-Track-A2 snapshot on disk to diff against.
Rather than special-case that file (which would mean either freezing a copy
before repointing run_018, or re-deriving a v4-only run some other way, both
one-off and not reproducible on a later re-run), this script computes BOTH
sides itself, fresh, in one execution: BEFORE = loan 01 + v4 profile (the
Track-F-only state), AFTER = loan 01 + v5 profile (Track-F + Track A2) --
same ruleset, same correction modules, same program-gate scoping logic for
both, so the diff isolates Track A2's marginal effect cleanly regardless of
what any other file on disk currently holds. This reproduces the specific
baseline the Track A2 investigation was run against (NOT_APPLICABLE=348,
NEEDS_REVIEW=718, FAIL=6, PASS=4 of 1076 scoped) exactly, confirmed by this
script computing that value itself rather than trusting a hardcoded number.

No cross-run-directory import exists anywhere in this codebase (same
precedent run_019 already established) -- `_program_classification` and
`_FANNIE_OR_UNTAGGED` are reimplemented here identically, not imported.

Pipeline:
 1. Load loan_01 fixture twice: once with v4 derived_facts promoted into
    loan.fields (BEFORE), once with v5 (AFTER).
 2. Load comprehensive_e2e_v8_ruleset.json, build Check objects, apply
    apply_known_compile_corrections then apply_document_presence_gates
    (identical for both sides -- only the loan profile differs).
 3. Run the engine once per side.
 4. Reproduce the scoped (Fannie Mae + UNTAGGED) program-gate summary for
    both sides.
 5. Diff: every check_id whose status differs, which of the 5 Track A2
    target fields (if any) explains each change (read directly off each
    check's own compiled `applies_if`, not assumed), and a per-field
    breakdown of how many of the checks blocked on that field at BEFORE
    resolved, and to what.

Zero LLM calls. Deterministic. Python 3.9 compatible.

Run: python3 p0/compile_runs/run_020_track_a2_precondition_derivations/build_and_run.py
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
    apply_document_presence_gates)
from qc_engine.compiler.known_compile_corrections import (  # noqa: E402
    apply_known_compile_corrections)
from qc_engine.compiler.program_gating import applies_to, Applicability, AMBIGUOUS  # noqa: E402
from qc_engine.engine import run  # noqa: E402
from qc_engine.model import SourceValue  # noqa: E402
from qc_engine.ruleset import Check, Ruleset  # noqa: E402

RUN_ID = "run_020_track_a2_precondition_derivations"
FROM_DOCS_DIR = os.path.join(_P0, "fixtures", "from_docs")
LOAN01_FIXTURE = os.path.join(FROM_DOCS_DIR, "loan_01.json")
LOAN_PROFILE_V4 = os.path.join(_REPO_ROOT, "storage", "loan_profiles", "v4", "loan_01.json")
LOAN_PROFILE_V5 = os.path.join(_REPO_ROOT, "storage", "loan_profiles", "v5", "loan_01.json")
RULESET_PATH = os.path.join(_REPO_ROOT, "result", "rules", "comprehensive_e2e_v8_ruleset.json")
APPLICABILITY_PATH = os.path.join(_REPO_ROOT, "result", "rules",
                                  "post_closing_only_applicability.json")
RESULTS_OUT = os.path.join(_REPO_ROOT, "result", "qc_results",
                           "run_020_track_a2_precondition_derivations_results.json")

_FANNIE_OR_UNTAGGED = ("Fannie Mae", "UNTAGGED")
TARGET_FIELDS = (
    "appraisal_waiver_type", "borrower_income_type",
    "du_validation_service_components_received",
    "credit_report_present_for_all_applicants", "closing_funds_asset_type",
)


def _program_classification(check_id, loan, applicability_map):
    """Identical logic to run_018/run_019's own `_program_classification`
    (reimplemented, not imported -- no cross-run-directory import precedent
    exists in this codebase)."""
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


def _load_loan_with_profile(profile_path):
    loan = load_canonical_loan(LOAN01_FIXTURE)
    with open(profile_path) as f:
        profile = json.load(f)
    for fact_name, entry in profile.get("derived_facts", {}).items():
        loan.fields[fact_name] = SourceValue(doc=entry["value"])
    return loan, profile


def _build_gated_checks():
    with open(RULESET_PATH) as f:
        wrapper = json.load(f)
    content = wrapper["content"]
    checks = [Check(**c) for c in content["checks"]]
    apply_known_compile_corrections(checks)
    apply_document_presence_gates(checks)
    return checks, {c.id: c for c in checks}


def _compute_side(profile_path, checks, applicability_map):
    loan, profile = _load_loan_with_profile(profile_path)
    rs = Ruleset(ruleset_id="track-a2-diff", version=1, checks=checks)
    result = run(loan, rs)
    results_by_id = {r.check_id: r for r in result.results}
    scoped_ids = set()
    for r in result.results:
        programs, classification = _program_classification(r.check_id, loan, applicability_map)
        if classification == "UNTAGGED" or (
            programs and any(p in _FANNIE_OR_UNTAGGED for p in programs)
        ):
            scoped_ids.add(r.check_id)
    scoped_status_counts = Counter(results_by_id[cid].status for cid in scoped_ids)
    return {
        "profile": profile,
        "results_by_id": results_by_id,
        "scoped_ids": scoped_ids,
        "scoped_status_counts": scoped_status_counts,
    }


def main() -> None:
    checks, checks_by_id = _build_gated_checks()
    with open(APPLICABILITY_PATH) as f:
        applicability_map = json.load(f)

    before = _compute_side(LOAN_PROFILE_V4, checks, applicability_map)
    after = _compute_side(LOAN_PROFILE_V5, checks, applicability_map)

    assert before["scoped_ids"] == after["scoped_ids"], (
        "scoped-check membership differs between v4 and v5 profiles -- Track A2's "
        "derivations should never change which checks are program-scoped, only "
        "whether precondition-gated checks within that scope resolve")
    scope = before["scoped_ids"]

    before_counts = dict(before["scoped_status_counts"])
    after_counts = dict(after["scoped_status_counts"])

    # ---- per-check status changes within the 1076 scoped checks ----
    status_changes = []
    for cid in sorted(scope):
        b = before["results_by_id"][cid].status
        a = after["results_by_id"][cid].status
        if b != a:
            chk = checks_by_id.get(cid)
            fields_in_applies_if = (
                {c["field_name"] for c in chk.applies_if} if chk and chk.applies_if else set())
            matched_target_fields = sorted(fields_in_applies_if & set(TARGET_FIELDS))
            status_changes.append({
                "check_id": cid, "old_status": b, "new_status": a,
                "explained_by_target_field(s)": matched_target_fields,
            })

    # ---- per-target-field breakdown: how many scoped checks were blocked
    # (NEEDS_REVIEW / APPLICABILITY_UNKNOWN) on this field at BEFORE, and
    # what they resolved to at AFTER ----
    per_field_blocked = {f: [] for f in TARGET_FIELDS}
    for cid in scope:
        chk = checks_by_id.get(cid)
        if not chk or not chk.applies_if:
            continue
        fields = {c["field_name"] for c in chk.applies_if}
        matched = fields & set(TARGET_FIELDS)
        if not matched:
            continue
        r = before["results_by_id"][cid]
        if r.status == "NEEDS_REVIEW" and getattr(r, "review_reason", None) == "APPLICABILITY_UNKNOWN":
            for f in matched:
                per_field_blocked[f].append(cid)

    per_field_summary = {}
    for field, ids in per_field_blocked.items():
        outcome_tally = Counter(after["results_by_id"][cid].status for cid in ids)
        per_field_summary[field] = {
            "blocked_at_before": len(ids),
            "after_outcomes": dict(outcome_tally),
            "still_blocked_at_after": outcome_tally.get("NEEDS_REVIEW", 0),
        }

    out = {
        "run": RUN_ID,
        "loan_id": "2025-0917-001",
        "note": (
            "BEFORE = loan 01 + storage/loan_profiles/v4 (Track-F-only). "
            "AFTER = loan 01 + storage/loan_profiles/v5 (Track-F + Track A2's 5 new "
            "precondition derivations: appraisal_waiver_type, borrower_income_type, "
            "du_validation_service_components_received (no derivation added -- stays "
            "underivable for all 5 loans), credit_report_present_for_all_applicants, "
            "closing_funds_asset_type (stays underivable for loan 01 itself -- two "
            "distinct asset types disclosed, no field says which funds closing). Both "
            "sides use the identical ruleset + correction modules + program-gate "
            "scoping logic; only the loan profile differs."),
        "scoped_checks": len(scope),
        "before_scoped_status_counts": before_counts,
        "after_scoped_status_counts": after_counts,
        "status_changes_count": len(status_changes),
        "status_changes": status_changes,
        "per_target_field_summary": per_field_summary,
    }
    os.makedirs(os.path.dirname(RESULTS_OUT), exist_ok=True)
    with open(RESULTS_OUT, "w") as f:
        json.dump(out, f, indent=2)

    print("=== TRACK A2: PRECONDITION DERIVATIONS -- BEFORE (v4) vs AFTER (v5), loan 01 ===")
    print()
    print("BEFORE (v4 profile), scoped_checks={}:".format(len(scope)))
    print("  {}".format(before_counts))
    print()
    print("AFTER (v5 profile), scoped_checks={}:".format(len(scope)))
    print("  {}".format(after_counts))
    print()
    print("=== STATUS CHANGES ({} check_ids) ===".format(len(status_changes)))
    for chg in status_changes:
        print("  {}: {} -> {}  [{}]".format(
            chg["check_id"], chg["old_status"], chg["new_status"],
            ", ".join(chg["explained_by_target_field(s)"]) or "unexplained!"))
    print()
    print("=== PER-TARGET-FIELD SUMMARY (of checks blocked at BEFORE) ===")
    for field, summary in sorted(per_field_summary.items()):
        print("  {}: blocked_at_before={}  after_outcomes={}".format(
            field, summary["blocked_at_before"], summary["after_outcomes"]))
    print()
    print("wrote {}".format(RESULTS_OUT))


if __name__ == "__main__":
    main()
