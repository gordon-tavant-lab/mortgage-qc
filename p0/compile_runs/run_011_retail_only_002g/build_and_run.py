"""
run_011 -- the END-TO-END proof run Kayla reviews RESULTS from, not mechanisms.

Builds the Retail-only, 002g-wired ruleset at ZERO LLM cost by reusing
run_010's already-compiled checks (per-row LLM compilation is row-specific
content; excluding Private Bank rows and attaching deterministically-derived
preconditions requires no recompile), then runs all 5 real document-extracted
loans through the old (deployed) and new rulesets and reports exactly what
changed.

Pipeline (every step deterministic, no network):
 1. Load run_010's compiled ruleset + its check->source-row provenance.
 2. RETAIL-ONLY RE-BASIS (ROADMAP Tension 9's pending housekeeping): keep only
    checks whose every source row came from the Retail workbook; drop Private
    Bank / mixed checks, counted and reported.
 3. 002d OPERATOR GATE: run operator_consistency_check() over the kept checks
    (the deployed ruleset predates 002d and still contains the known inverted
    checks) -- flagged checks are EXCLUDED from the new signed set, listed.
 4. 002g PRECONDITIONS: run 002f Layer 0 over the real 5,520 Retail rows,
    resolve every proposal through the signed v1 fact vocabulary, and attach
    `applies_if` to a check only when EVERY candidate source row (exception-
    code join; duplicated codes handled conservatively) resolves to the
    IDENTICAL condition set -- anything else is flagged for review, never
    guessed.
 5. Run all 5 loans against old + new rulesets; replay.py reports every
    status flip; per-loan dispositions saved.

Outputs:
  result/rules/retail_only_002g_ruleset.json
  result/qc_results/run_011_retail_only_002g_results.json
  (human-readable summary written separately to output/)

Run: python3 p0/compile_runs/run_011_retail_only_002g/build_and_run.py
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

from fixture_loader import load_canonical_loan  # noqa: E402
from ontology_extraction import pipeline as ontology_pipeline  # noqa: E402
from qc_engine.compiler import compile_llm  # noqa: E402
from qc_engine.compiler import fact_vocabulary as FV  # noqa: E402
from qc_engine.engine import run  # noqa: E402
from qc_engine.model import SourceValue  # noqa: E402
from qc_engine.replay import replay  # noqa: E402
from qc_engine.ruleset import Check, Ruleset  # noqa: E402

RUN010 = os.path.join(_P0, "compile_runs", "run_010_post_closing_only")
FIXTURE_ROWS = os.path.join(_P0, "fixtures", "ontology_extraction",
                            "retail_post_closing_rows.json")
VOCAB_PATH = os.path.join(_REPO_ROOT, "storage", "fact_vocabulary", "v1.json")
OLD_RULESET = os.path.join(_REPO_ROOT, "result", "rules", "post_closing_only_ruleset.json")
NEW_RULESET_OUT = os.path.join(_REPO_ROOT, "result", "rules", "retail_only_002g_ruleset.json")
RESULTS_OUT = os.path.join(_REPO_ROOT, "result", "qc_results",
                           "run_011_retail_only_002g_results.json")
RETAIL_FILE = "PF and PC Sept 2025 AMQs - Retail.xlsx"


def _load_checks(ruleset_json_path):
    with open(ruleset_json_path) as f:
        wrapper = json.load(f)
    content = wrapper["content"]
    return [Check(**c) for c in content["checks"]], content


def _panel():
    """The 5 real document-extracted loans. `gift_funds_used` is DERIVED from
    each loan's real extracted `doc_present_gift_letter` fact (present in all
    5 fixtures; loan 02 is the real gift loan with full donor documentation)
    -- a disclosed derivation from real extraction, not an injected answer."""
    loans = []
    for n in ("01", "02", "03", "04", "05"):
        loan = load_canonical_loan(
            os.path.join(_P0, "fixtures", "from_docs", f"loan_{n}.json"))
        letter = loan.facts.get("doc_present_gift_letter")
        if letter in ("true", "false"):
            loan.fields["gift_funds_used"] = SourceValue(doc=letter)
        loans.append(loan)
    return loans


def main() -> None:
    # -- 1. run_010 compiled material ----------------------------------------
    with open(os.path.join(RUN010, "ruleset.json")) as f:
        run010 = json.load(f)["content"]
    with open(os.path.join(RUN010, "provenance_checkpoint.json")) as f:
        provenance = json.load(f)
    checks_by_id = {c["id"]: c for c in run010["checks"]}
    print(f"run_010 compiled checks: {len(checks_by_id)}; provenance rows for "
          f"{len(provenance)} check ids")

    # -- 2. Retail-only re-basis ---------------------------------------------
    retail_ids, dropped_mixed, dropped_pb = [], [], []
    for check_id, prows in provenance.items():
        if check_id not in checks_by_id:
            continue
        files = {p["source_file"] for p in prows}
        if files == {RETAIL_FILE}:
            retail_ids.append(check_id)
        elif RETAIL_FILE in files:
            dropped_mixed.append(check_id)
        else:
            dropped_pb.append(check_id)
    print(f"retail-only checks kept: {len(retail_ids)}; dropped: "
          f"{len(dropped_pb)} Private-Bank-only, {len(dropped_mixed)} mixed-source")

    # -- 3. 002d operator gate on the kept checks ----------------------------
    kept_checks, operator_excluded = [], []
    for cid in sorted(retail_ids):
        chk = Check(**checks_by_id[cid])
        flag = compile_llm.operator_consistency_check(chk)
        if flag is not None:
            operator_excluded.append({"check_id": cid, "flag": flag})
        else:
            kept_checks.append(chk)
    print(f"002d operator gate: {len(operator_excluded)} checks excluded "
          f"(known-inverted family), {len(kept_checks)} remain")

    # -- 4. 002g preconditions (Layer 0 + signed vocabulary, zero LLM) -------
    with open(FIXTURE_ROWS) as f:
        rows = json.load(f)
    vocab = FV.load(VOCAB_PATH)
    result = ontology_pipeline.run_layers(rows)  # Layer-0 only
    proposals_by_row = defaultdict(list)
    for prop in result.proposals:
        proposals_by_row[prop.row_id].append(prop)

    rows_by_code = defaultdict(list)
    for r in rows:
        if r["exception_code"]:
            rows_by_code[r["exception_code"]].append(r)

    def _row_condition_set(row):
        """Resolved applies_if condition list for one fixture row, or a
        string describing why it can't be resolved. None = unconditional."""
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
            flagged.append({"check_id": chk.id,
                            "reason": (str_reasons[0] if str_reasons
                                       else "candidate rows disagree on condition")})
            continue
        chk.applies_if = json.loads(cond_sets[0])
        attached.append(chk.id)
    print(f"002g preconditions: {len(attached)} checks gated, "
          f"{len(flagged)} flagged for SME review, {unconditional} unconditional")

    # -- 5. old vs new on the real 5-loan panel ------------------------------
    old_checks, old_content = _load_checks(OLD_RULESET)
    old_rs = Ruleset(ruleset_id=old_content["ruleset_id"],
                     version=old_content["version"], checks=old_checks)
    new_rs = Ruleset(ruleset_id="retail-only-002g", version=1, checks=kept_checks)
    loans = _panel()

    rep = replay(loans, old_rs, new_rs)
    per_loan = []
    for loan in loans:
        rr = run(loan, new_rs)
        by_status = defaultdict(int)
        for r in rr.results:
            by_status[r.status] += 1
        gift = [
            {"check_id": r.check_id, "status": r.status, "message": r.message}
            for r in rr.results
            if r.check_id in attached and "gift" in (r.message or "").lower()
        ]
        per_loan.append({
            "loan_id": loan.loan_id,
            "gift_funds_used": (loan.fields.get("gift_funds_used").doc
                                 if "gift_funds_used" in loan.fields else None),
            "disposition": rr.disposition,
            "status_counts": dict(sorted(by_status.items())),
            "gated_gift_checks": gift,
        })

    flips_by_status = defaultdict(int)
    for fl in rep.flips:
        flips_by_status[f"{fl.old_status} -> {fl.new_status}"] += 1

    out = {
        "run": "run_011_retail_only_002g",
        "built_from": "run_010 compiled checks (zero recompile, zero LLM calls)",
        "rebasis": {"kept_retail_only": len(retail_ids),
                     "dropped_private_bank_only": len(dropped_pb),
                     "dropped_mixed_source": len(dropped_mixed)},
        "operator_gate_excluded": operator_excluded,
        "preconditions": {"attached": len(attached), "attached_check_ids": sorted(attached),
                           "flagged_for_review": flagged,
                           "unconditional": unconditional,
                           "layer0_coverage": {
                               "total_rows": result.coverage.total_rows,
                               "resolved_rows": result.coverage.resolved_rows}},
        "replay_vs_deployed": {
            "loans": rep.loans_replayed,
            "checks_only_in_old": len(rep.only_in_old),
            "checks_only_in_new": len(rep.only_in_new),
            "flips_total": len(rep.flips),
            "flips_by_transition": dict(sorted(flips_by_status.items())),
            "flips": [{"loan_id": f.loan_id, "check_id": f.check_id,
                        "old": f.old_status, "new": f.new_status}
                       for f in rep.flips],
        },
        "per_loan": per_loan,
    }
    os.makedirs(os.path.dirname(RESULTS_OUT), exist_ok=True)
    with open(RESULTS_OUT, "w") as f:
        json.dump(out, f, indent=2)

    wrapper = {
        "content": {"ruleset_id": new_rs.ruleset_id, "version": new_rs.version,
                     "engine_version": new_rs.engine_version,
                     "checks": [c.to_dict() for c in new_rs.checks]},
        "sha256": new_rs.sha256(),
        "signoff_summary": ("NOT SIGNED -- built deterministically from run_010's "
                             "compiled checks; pending SME (Kayla) review of results"),
    }
    with open(NEW_RULESET_OUT, "w") as f:
        json.dump(wrapper, f, indent=2)

    print(f"\nwrote {NEW_RULESET_OUT} ({len(kept_checks)} checks, sha {new_rs.sha256()[:12]}...)")
    print(f"wrote {RESULTS_OUT}")
    print(f"replay: {len(rep.flips)} flips vs deployed; per-loan dispositions: "
          + ", ".join(f"{p['loan_id']}={p['disposition']}" for p in per_loan))


if __name__ == "__main__":
    main()
