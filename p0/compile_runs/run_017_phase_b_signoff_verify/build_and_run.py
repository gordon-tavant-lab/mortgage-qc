"""
run_017 -- verifies spec 015 Phase B Half 2's (T032-T035) two fact-vocabulary
sign-off registrations by re-running the SAME precondition-attachment logic
run_013 uses (steps 1-4 of its pipeline, replicated read-only here) against
two vocabulary versions, and reporting the real FLAGGED -> applies_if-gated
delta -- not the plan's ~165+/~102 estimates, the actual counts.

Two questions, two different starting states:

1. Question 571085 (loan-product-type taxonomy, proposed fact
   `loan_product_type`) was genuinely unsigned before this spec -- its
   LLM-drafted proposal already existed in
   `storage/fact_vocabulary/candidates/naming_proposals_v1.json` (drafted in
   a prior session), but `promote_naming_proposals.py` had never promoted it
   (it bails whole-batch if ANY of the 24 drafted names already exists in the
   signed vocabulary, and 23 of the other 24 already had been promoted
   2026-07-27 -- see git history for the one-off, scoped re-invocation of
   that script's own functions that produced v8.json). This run compares
   v7 (pre-promotion) against v8 (post-promotion).

2. Question 570606 (asset-type taxonomy, fact `closing_funds_asset_type`)
   turned out to ALREADY be fully signed as of v3 (promoted 2026-07-27,
   one day before this session started) -- tasks.md's framing of it as
   still-needing-registration was stale by the time Phase B ran. This run
   verifies its real, current attachment impact directly against v8 (no
   before/after needed -- it never regressed, it was just never confirmed
   against the compiled ruleset until now).

Read-only: loads the already-compiled run_010 checks + provenance and the
already-extracted ontology rows; does not recompile or write a new ruleset.

Inputs:
- p0/compile_runs/run_010_post_closing_only/{ruleset.json,provenance_checkpoint.json}
- p0/fixtures/ontology_extraction/retail_post_closing_rows.json
- storage/fact_vocabulary/{v7,v8}.json

Output: result/qc_results/run_017_phase_b_signoff_verify_results.json

Run: python3 p0/compile_runs/run_017_phase_b_signoff_verify/build_and_run.py
Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys
from collections import defaultdict

_HERE = os.path.dirname(os.path.abspath(__file__))
_P0 = os.path.dirname(os.path.dirname(_HERE))
_REPO_ROOT = os.path.dirname(_P0)
if _P0 not in sys.path:
    sys.path.insert(0, _P0)

from ontology_extraction import pipeline as ontology_pipeline  # noqa: E402
from qc_engine.compiler import compile_llm  # noqa: E402
from qc_engine.compiler import fact_vocabulary as FV  # noqa: E402
from qc_engine.ruleset import Check  # noqa: E402

RUN010 = os.path.join(_P0, "compile_runs", "run_010_post_closing_only")
FIXTURE_ROWS = os.path.join(_P0, "fixtures", "ontology_extraction",
                            "retail_post_closing_rows.json")
VOCAB_DIR = os.path.join(_REPO_ROOT, "storage", "fact_vocabulary")
RETAIL_FILE = "PF and PC Sept 2025 AMQs - Retail.xlsx"
RESULTS_OUT = os.path.join(_REPO_ROOT, "result", "qc_results",
                           "run_017_phase_b_signoff_verify_results.json")


def _load_kept_checks():
    with open(os.path.join(RUN010, "ruleset.json")) as f:
        run010 = json.load(f)["content"]
    with open(os.path.join(RUN010, "provenance_checkpoint.json")) as f:
        provenance = json.load(f)
    checks_by_id = {c["id"]: c for c in run010["checks"]}

    retail_ids = []
    for check_id, prows in provenance.items():
        if check_id not in checks_by_id:
            continue
        files = {p["source_file"] for p in prows}
        if files == {RETAIL_FILE}:
            retail_ids.append(check_id)

    kept_checks = []
    for cid in sorted(retail_ids):
        chk = Check(**checks_by_id[cid])
        if compile_llm.operator_consistency_check(chk) is None:
            kept_checks.append(chk)
    return kept_checks, provenance


def _row_condition_set(row, vocab, proposals_by_row):
    props = proposals_by_row.get(row["row_id"], [])
    if not props:
        return None
    conds, reasons = [], []
    for prop in props:
        res = FV.resolve_layer0(vocab, prop)
        if res.status == "resolved":
            conds.append(res.condition)
        else:
            reasons.append(res.reason)
    if reasons:
        return "unresolved: " + "; ".join(sorted(set(reasons))[:2])
    return sorted(conds, key=lambda c: (c["field_name"], c["operator"], c["value"]))


def run_attachment(vocab, kept_checks, provenance, proposals_by_row, rows_by_code):
    attached, flagged, unconditional = set(), set(), 0
    conditions_by_check = {}
    for chk in kept_checks:
        codes = {p["exception_code"] for p in provenance[chk.id]}
        candidate_rows = [r for code in codes for r in rows_by_code.get(code, [])]
        if not candidate_rows:
            unconditional += 1
            continue
        outcomes = [_row_condition_set(r, vocab, proposals_by_row) for r in candidate_rows]
        if all(o is None for o in outcomes):
            unconditional += 1
            continue
        str_reasons = [o for o in outcomes if isinstance(o, str)]
        cond_sets = [json.dumps(o) for o in outcomes if isinstance(o, list)]
        if str_reasons or len(set(cond_sets)) != 1 or any(o is None for o in outcomes):
            flagged.add(chk.id)
            continue
        attached.add(chk.id)
        conditions_by_check[chk.id] = json.loads(cond_sets[0])
    return attached, flagged, unconditional, conditions_by_check


def main() -> None:
    kept_checks, provenance = _load_kept_checks()

    with open(FIXTURE_ROWS) as f:
        rows = json.load(f)
    result = ontology_pipeline.run_layers(rows)
    proposals_by_row = defaultdict(list)
    for prop in result.proposals:
        proposals_by_row[prop.row_id].append(prop)
    rows_by_code = defaultdict(list)
    for r in rows:
        if r["exception_code"]:
            rows_by_code[r["exception_code"]].append(r)

    vocab_v7 = FV.load(os.path.join(VOCAB_DIR, "v7.json"))
    vocab_v8 = FV.load(os.path.join(VOCAB_DIR, "v8.json"))

    attached_v7, flagged_v7, unc_v7, _ = run_attachment(
        vocab_v7, kept_checks, provenance, proposals_by_row, rows_by_code)
    attached_v8, flagged_v8, unc_v8, conditions_v8 = run_attachment(
        vocab_v8, kept_checks, provenance, proposals_by_row, rows_by_code)

    newly_attached_571085 = sorted(attached_v8 - attached_v7)
    closing_funds_gated = sorted(
        cid for cid in attached_v8
        if any(c.get("field_name") == "closing_funds_asset_type"
               for c in conditions_v8.get(cid, []))
    )

    out = {
        "run": "run_017_phase_b_signoff_verify",
        "v7_summary": {"attached": len(attached_v7), "flagged": len(flagged_v7),
                       "unconditional": unc_v7},
        "v8_summary": {"attached": len(attached_v8), "flagged": len(flagged_v8),
                       "unconditional": unc_v8},
        "question_571085_loan_product_type": {
            "plan_estimate": "165+",
            "actual_newly_attached_count": len(newly_attached_571085),
            "note": "v8 minus v7 attached-set -- loan_product_type is the only "
                    "difference between these two vocabulary versions (see git "
                    "history: one-off promotion of Question 571085's already-"
                    "drafted naming_proposals_v1.json entry).",
            "sample_check_ids": newly_attached_571085[:15],
        },
        "question_570606_closing_funds_asset_type": {
            "plan_estimate": "102",
            "actual_attached_count": len(closing_funds_gated),
            "note": "closing_funds_asset_type was ALREADY signed as of v3 "
                    "(promoted 2026-07-27, one day before this spec started) -- "
                    "tasks.md's framing of Question 570606 as still-needing-"
                    "registration was stale by the time Phase B ran. This "
                    "count is the real, current, ATTACHED (not FLAGGED) impact "
                    "of that pre-existing sign-off against the compiled "
                    "ruleset, confirmed here for the first time.",
            "sample_check_ids": closing_funds_gated[:15],
        },
    }
    os.makedirs(os.path.dirname(RESULTS_OUT), exist_ok=True)
    with open(RESULTS_OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"v7: attached={len(attached_v7)} flagged={len(flagged_v7)} unconditional={unc_v7}")
    print(f"v8: attached={len(attached_v8)} flagged={len(flagged_v8)} unconditional={unc_v8}")
    print(f"Q571085 (loan_product_type) newly attached: {len(newly_attached_571085)} "
          f"(plan estimate: 165+)")
    print(f"Q570606 (closing_funds_asset_type) attached: {len(closing_funds_gated)} "
          f"(plan estimate: 102)")
    print(f"wrote {RESULTS_OUT}")


if __name__ == "__main__":
    main()
