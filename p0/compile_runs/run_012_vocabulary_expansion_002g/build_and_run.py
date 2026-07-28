"""
run_012 -- measures the COMPILE-TIME impact of expanding the fact vocabulary
from 1 fact (gift only, v1) to the latest promoted vocabulary
(promote_naming_proposals.py + build_vocabulary_guide_citations.py +
remove_out_of_scope_fact.py, 2026-07-27): how many more of the Retail-only,
operator-gated checks (run_011's own kept_checks) now get a real `applies_if`
attached at compile time, versus flagged for review or left unconditional,
with ZERO recompile and ZERO new LLM calls -- this reruns only the
deterministic Layer-0 precondition-attachment step (run_011 step 4) twice,
once per vocabulary version, and diffs the outcome. Always resolves "latest"
dynamically (FV.load_latest) rather than hardcoding a version, so this stays
accurate as the vocabulary evolves (e.g. v6 dropped loan_product_type --
Freddie Mac fact, no Freddie Mac corpus to cite it from -- reducing coverage
from v4/v5's 1,701 attached to v6's 1,530; still zero regressions vs v1).

This is deliberately a COMPILE-TIME comparison, not a new 5-loan disposition
run: the newly-promoted facts (income type, appraisal-in-file, credit
report presence, etc.) have no corresponding extracted loan-side data yet in
`p0/fixtures/from_docs/loan_0N.json` (only `gift_funds_used` has a real
per-loan derivation, per `build_loan_profiles.py`) -- so checks newly gated on
them would show real coverage gains at compile time but NEEDS_REVIEW at
runtime for lack of loan data, which would muddy the actual finding here
(vocabulary coverage, not extraction coverage). The 5-loan disposition run
(run_011) and the extraction-coverage gap are both already tracked
separately; this run isolates one variable.

Run: python3 p0/compile_runs/run_012_vocabulary_expansion_002g/build_and_run.py
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
for p in (_P0, os.path.join(_P0, "fixtures", "from_docs")):
    if p not in sys.path:
        sys.path.insert(0, p)

from ontology_extraction import pipeline as ontology_pipeline  # noqa: E402
from qc_engine.compiler import compile_llm  # noqa: E402
from qc_engine.compiler import fact_vocabulary as FV  # noqa: E402
from qc_engine.ruleset import Check  # noqa: E402

RUN010 = os.path.join(_P0, "compile_runs", "run_010_post_closing_only")
FIXTURE_ROWS = os.path.join(_P0, "fixtures", "ontology_extraction",
                            "retail_post_closing_rows.json")
VOCAB_DIR = os.path.join(_REPO_ROOT, "storage", "fact_vocabulary")
VOCAB_V1 = os.path.join(VOCAB_DIR, "v1.json")
RESULTS_OUT = os.path.join(_REPO_ROOT, "result", "qc_results",
                           "run_012_vocabulary_expansion_002g_results.json")
RETAIL_FILE = "PF and PC Sept 2025 AMQs - Retail.xlsx"


def _kept_checks_and_provenance():
    """Exactly run_011 steps 1-3 (compiled checks -> Retail-only re-basis ->
    002d operator gate) -- unchanged inputs, so the ONLY variable in this run
    is which fact vocabulary resolves preconditions."""
    with open(os.path.join(RUN010, "ruleset.json")) as f:
        run010 = json.load(f)["content"]
    with open(os.path.join(RUN010, "provenance_checkpoint.json")) as f:
        provenance = json.load(f)
    checks_by_id = {c["id"]: c for c in run010["checks"]}

    retail_ids = []
    for check_id, prows in provenance.items():
        if check_id not in checks_by_id:
            continue
        if {p["source_file"] for p in prows} == {RETAIL_FILE}:
            retail_ids.append(check_id)

    kept_checks = []
    for cid in sorted(retail_ids):
        chk = Check(**checks_by_id[cid])
        if compile_llm.operator_consistency_check(chk) is None:
            kept_checks.append(chk)
    return kept_checks, provenance


def _attach_preconditions(kept_checks, provenance, rows, vocab):
    """run_011 step 4, factored out so it can run once per vocabulary."""
    result = ontology_pipeline.run_layers(rows)
    proposals_by_row = defaultdict(list)
    for prop in result.proposals:
        proposals_by_row[prop.row_id].append(prop)
    rows_by_code = defaultdict(list)
    for r in rows:
        if r["exception_code"]:
            rows_by_code[r["exception_code"]].append(r)

    def _row_condition_set(row):
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

    attached, flagged, unconditional = [], [], 0
    for chk in kept_checks:
        codes = {p["exception_code"] for p in provenance[chk.id]}
        candidate_rows = [r for code in codes for r in rows_by_code.get(code, [])]
        if not candidate_rows:
            unconditional += 1
            continue
        outcomes = [_row_condition_set(r) for r in candidate_rows]
        if all(o is None for o in outcomes):
            unconditional += 1
            continue
        str_reasons = [o for o in outcomes if isinstance(o, str)]
        cond_sets = [json.dumps(o) for o in outcomes if isinstance(o, list)]
        if str_reasons or len(set(cond_sets)) != 1 or any(o is None for o in outcomes):
            flagged.append(chk.id)
            continue
        attached.append(chk.id)
    return {"attached": sorted(attached), "flagged": sorted(flagged),
            "unconditional": unconditional, "total": len(kept_checks)}


def main() -> None:
    kept_checks, provenance = _kept_checks_and_provenance()
    with open(FIXTURE_ROWS) as f:
        rows = json.load(f)

    vocab_v1 = FV.load(VOCAB_V1)
    vocab_latest = FV.load_latest(VOCAB_DIR)
    assert vocab_latest.version >= 4, "expected the expanded vocabulary to be latest"

    before = _attach_preconditions(kept_checks, provenance, rows, vocab_v1)
    after = _attach_preconditions(kept_checks, provenance, rows, vocab_latest)

    newly_attached = sorted(set(after["attached"]) - set(before["attached"]))
    still_flagged = sorted(set(after["flagged"]) & set(before["flagged"]))
    newly_flagged = sorted(set(after["flagged"]) - set(before["flagged"]))  # should be empty

    out = {
        "run": "run_012_vocabulary_expansion_002g",
        "compares": f"precondition attachment against v1 (1 fact) vs latest "
                    f"(v{vocab_latest.version}, {len(vocab_latest.facts)} facts) "
                    f"of the fact vocabulary -- same checks, same rows, zero recompile",
        "kept_checks_total": len(kept_checks),
        "before_v1": {"attached": len(before["attached"]), "flagged": len(before["flagged"]),
                      "unconditional": before["unconditional"]},
        "after_latest": {"version": vocab_latest.version, "fact_count": len(vocab_latest.facts),
                     "attached": len(after["attached"]), "flagged": len(after["flagged"]),
                     "unconditional": after["unconditional"]},
        "newly_attached_check_ids": newly_attached,
        "newly_attached_count": len(newly_attached),
        "still_flagged_check_ids": still_flagged,
        "regressions_newly_flagged": newly_flagged,  # non-empty would be a real bug
    }
    os.makedirs(os.path.dirname(RESULTS_OUT), exist_ok=True)
    with open(RESULTS_OUT, "w") as f:
        json.dump(out, f, indent=2)

    print(f"kept checks (Retail-only, operator-gated): {len(kept_checks)}")
    print(f"v1 (gift only):        {len(before['attached'])} attached, "
          f"{len(before['flagged'])} flagged, {before['unconditional']} unconditional")
    print(f"latest (v{vocab_latest.version}, {len(vocab_latest.facts)} facts): "
          f"{len(after['attached'])} attached, {len(after['flagged'])} flagged, "
          f"{after['unconditional']} unconditional")
    print(f"newly attached by vocabulary expansion: {len(newly_attached)}")
    if newly_flagged:
        print(f"WARNING: {len(newly_flagged)} checks newly flagged that weren't before "
              f"-- investigate before trusting this run")
    print(f"wrote {RESULTS_OUT}")


if __name__ == "__main__":
    main()
