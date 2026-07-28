"""
run_013 -- the genuine, comprehensive END-TO-END proof against the expanded
(16-fact) vocabulary, requested explicitly after run_012 showed compile-time
coverage only. Unlike run_012, this ACTUALLY RUNS the 5 real loans through
the engine with real derived loan-side fields (storage/loan_profiles/v2/:
gift_funds_used, loan_transaction_type, appraisal_in_file -- the only 3 of
16 vocabulary facts with an honest, already-extracted derivation; see
build_loan_profiles_v2.py's docstring for why the other 13 aren't attempted).

Every stage is logged to storage/logs/run_013_comprehensive_e2e_v6.jsonl via
qc_engine.eval_log.EvalLog (CLAUDE.md's Evidence Chain + Cost Transparency
requirements): loan-profile derivation, precondition attachment (per check),
engine execution (per check, per loan -- input/method/verdict, "no black
boxes"), the replay comparison against the deployed baseline, and an explicit
cost summary (this entire pipeline is zero-LLM; the log says so, not just
implies it by omission).

Pipeline (identical to run_011/012's proven steps 1-4, then genuinely new):
 1. Load run_010's compiled checks + provenance (zero recompile).
 2. Retail-only re-basis (ROADMAP Tension 9).
 3. 002d operator gate.
 4. 002g preconditions, resolved against the LATEST (v6, 16-fact) vocabulary
    instead of v1's gift-only vocabulary.
 5. NEW: run all 5 loans (with their real v2-derived fields) through the
    resulting ruleset; replay against the deployed baseline; log everything.

Outputs:
  result/qc_results/run_013_comprehensive_e2e_v6_results.json
  storage/logs/run_013_comprehensive_e2e_v6.jsonl

Run: python3 p0/compile_runs/run_013_comprehensive_e2e_v6/build_and_run.py
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
from qc_engine.eval_log import EvalLog  # noqa: E402
from qc_engine.engine import run  # noqa: E402
from qc_engine.model import SourceValue  # noqa: E402
from qc_engine.replay import replay  # noqa: E402
from qc_engine.ruleset import Check, Ruleset  # noqa: E402

RUN_ID = "run_013_comprehensive_e2e_v6"
RUN010 = os.path.join(_P0, "compile_runs", "run_010_post_closing_only")
FIXTURE_ROWS = os.path.join(_P0, "fixtures", "ontology_extraction",
                            "retail_post_closing_rows.json")
VOCAB_DIR = os.path.join(_REPO_ROOT, "storage", "fact_vocabulary")
LOAN_PROFILES_V2_DIR = os.path.join(_REPO_ROOT, "storage", "loan_profiles", "v2")
FROM_DOCS_DIR = os.path.join(_P0, "fixtures", "from_docs")
OLD_RULESET = os.path.join(_REPO_ROOT, "result", "rules", "post_closing_only_ruleset.json")
NEW_RULESET_OUT = os.path.join(_REPO_ROOT, "result", "rules",
                               "comprehensive_e2e_v6_ruleset.json")
RESULTS_OUT = os.path.join(_REPO_ROOT, "result", "qc_results",
                           "{}_results.json".format(RUN_ID))
RETAIL_FILE = "PF and PC Sept 2025 AMQs - Retail.xlsx"
LOAN_NUMBERS = ("01", "02", "03", "04", "05")


def _load_checks(ruleset_json_path):
    with open(ruleset_json_path) as f:
        wrapper = json.load(f)
    content = wrapper["content"]
    return [Check(**c) for c in content["checks"]], content


def _panel_from_v2_profiles(log: EvalLog):
    """The 5 real document-extracted loans, with EVERY v2-derived fact wired
    onto loan.fields as a real SourceValue -- not just gift_funds_used
    (run_011's scope). Logs each loan's derivation evidence chain."""
    loans = []
    for n in LOAN_NUMBERS:
        loan = load_canonical_loan(os.path.join(FROM_DOCS_DIR, "loan_{}.json".format(n)))
        profile_path = os.path.join(LOAN_PROFILES_V2_DIR, "loan_{}.json".format(n))
        with open(profile_path) as f:
            profile = json.load(f)

        for fact_name, entry in profile.get("derived_facts", {}).items():
            loan.fields[fact_name] = SourceValue(doc=entry["value"])
            log.log_evidence_chain(
                entity_id="{}::{}".format(loan.loan_id, fact_name),
                input_=entry["derived_from"], method=entry["derivation_rule"],
                verdict=entry["value"], stage="loan_profile_derivation")
        for fact_name, entry in profile.get("underivable", {}).items():
            log.log_evidence_chain(
                entity_id="{}::{}".format(loan.loan_id, fact_name),
                input_=entry["attempted_from"], method="derivation_attempted",
                verdict="UNDERIVABLE", reason=entry["reason"],
                stage="loan_profile_derivation")
        loans.append(loan)
    return loans


def main() -> None:
    log = EvalLog(RUN_ID)
    log.log("setup", "run_started",
             vocab_dir=VOCAB_DIR, loan_profiles_dir=LOAN_PROFILES_V2_DIR)

    # -- 1. run_010 compiled material ----------------------------------------
    with open(os.path.join(RUN010, "ruleset.json")) as f:
        run010 = json.load(f)["content"]
    with open(os.path.join(RUN010, "provenance_checkpoint.json")) as f:
        provenance = json.load(f)
    checks_by_id = {c["id"]: c for c in run010["checks"]}
    log.log("setup", "run010_checks_loaded", total_checks=len(checks_by_id))

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
    log.log("rebasis", "retail_only_filter_applied", kept=len(retail_ids),
            dropped_private_bank_only=len(dropped_pb), dropped_mixed_source=len(dropped_mixed))

    # -- 3. 002d operator gate ------------------------------------------------
    kept_checks, operator_excluded = [], []
    for cid in sorted(retail_ids):
        chk = Check(**checks_by_id[cid])
        flag = compile_llm.operator_consistency_check(chk)
        if flag is not None:
            operator_excluded.append({"check_id": cid, "flag": flag})
        else:
            kept_checks.append(chk)
    log.log("operator_gate", "excluded_known_inverted_family",
            excluded=len(operator_excluded), remaining=len(kept_checks))

    # -- 4. 002g preconditions against the LATEST (v6) vocabulary -----------
    with open(FIXTURE_ROWS) as f:
        rows = json.load(f)
    vocab = FV.load_latest(VOCAB_DIR)
    log.log("precondition_attachment", "vocabulary_loaded",
            version=vocab.version, fact_count=len(vocab.facts))
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
            reason = str_reasons[0] if str_reasons else "candidate rows disagree on condition"
            flagged.append(chk.id)
            log.log_evidence_chain(entity_id=chk.id, input_={"codes": sorted(codes)},
                                   method="resolve_layer0", verdict="FLAGGED", reason=reason,
                                   stage="precondition_attachment")
            continue
        condition = json.loads(cond_sets[0])
        chk.applies_if = condition
        attached.append(chk.id)
        log.log_evidence_chain(entity_id=chk.id, input_={"codes": sorted(codes)},
                               method="resolve_layer0", verdict="ATTACHED",
                               applies_if=condition, stage="precondition_attachment")
    log.log("precondition_attachment", "summary", attached=len(attached),
            flagged=len(flagged), unconditional=unconditional, total=len(kept_checks))

    # -- 5. NEW: run all 5 loans (real v2-derived fields) + replay -----------
    loans = _panel_from_v2_profiles(log)
    old_checks, old_content = _load_checks(OLD_RULESET)
    old_rs = Ruleset(ruleset_id=old_content["ruleset_id"],
                     version=old_content["version"], checks=old_checks)
    new_rs = Ruleset(ruleset_id="comprehensive-e2e-v6", version=1, checks=kept_checks)

    rep = replay(loans, old_rs, new_rs)
    log.log("replay", "summary", loans_replayed=rep.loans_replayed,
            flips_total=len(rep.flips), only_in_old=len(rep.only_in_old),
            only_in_new=len(rep.only_in_new))
    for fl in rep.flips:
        log.log_evidence_chain(entity_id="{}::{}".format(fl.loan_id, fl.check_id),
                               input_={"old_status": fl.old_status}, method="replay_diff",
                               verdict=fl.new_status, stage="replay")

    per_loan = []
    for loan in loans:
        rr = run(loan, new_rs)
        by_status = defaultdict(int)
        for r in rr.results:
            by_status[r.status] += 1
            # Full evidence chain, every check, every loan -- "no black boxes."
            # `citation` is the audit anchor (model.py's own DocCitation
            # docstring) -- doc name, page, and the exact snippet the
            # extracted value came from. Without it this log can show a
            # verdict but not let a human trace it back to the source
            # document, which defeats the point of an evidence-chain log.
            log.log_evidence_chain(
                entity_id=r.check_id, input_=r.inputs, method=r.phase or "unphased",
                verdict=r.status, loan_id=loan.loan_id, field_name=r.field_name,
                message=r.message, review_reason=r.review_reason,
                citation=r.citation, doc_confidence=r.doc_confidence,
                stage="engine_execution")
        per_loan.append({
            "loan_id": loan.loan_id,
            "derived_fields": {k: v.doc for k, v in loan.fields.items()
                               if k in ("gift_funds_used", "loan_transaction_type",
                                        "appraisal_in_file")},
            "disposition": rr.disposition,
            "status_counts": dict(sorted(by_status.items())),
        })
        log.log("engine_execution", "loan_summary", loan_id=loan.loan_id,
                disposition=rr.disposition, status_counts=dict(sorted(by_status.items())))

    # -- cost transparency (CLAUDE.md requirement) ---------------------------
    log.log_cost(llm_calls=0, cost_usd=0.0, deterministic_resolution_rate=1.0,
                 note="entire pipeline (rebasis, operator gate, precondition "
                      "attachment, engine execution) is zero-LLM; only the "
                      "one-time naming-proposal draft (already logged separately, "
                      "2026-07-26) used a model call, and is not re-run here")

    flips_by_status = defaultdict(int)
    for fl in rep.flips:
        flips_by_status["{} -> {}".format(fl.old_status, fl.new_status)] += 1

    out = {
        "run": RUN_ID,
        "built_from": "run_010 compiled checks (zero recompile, zero LLM calls)",
        "vocabulary_version": vocab.version,
        "vocabulary_fact_count": len(vocab.facts),
        "loan_profiles_version": 2,
        "rebasis": {"kept_retail_only": len(retail_ids),
                    "dropped_private_bank_only": len(dropped_pb),
                    "dropped_mixed_source": len(dropped_mixed)},
        "operator_gate_excluded": operator_excluded,
        "preconditions": {"attached": len(attached), "flagged_for_review": len(flagged),
                          "unconditional": unconditional},
        "replay_vs_deployed": {
            "loans": rep.loans_replayed,
            "checks_only_in_old": len(rep.only_in_old),
            "checks_only_in_new": len(rep.only_in_new),
            "flips_total": len(rep.flips),
            "flips_by_transition": dict(sorted(flips_by_status.items())),
            "flips": [{"loan_id": f.loan_id, "check_id": f.check_id,
                       "old": f.old_status, "new": f.new_status} for f in rep.flips],
        },
        "per_loan": per_loan,
        "eval_log": log.path,
        "cost": {"llm_calls": 0, "cost_usd": 0.0, "deterministic_resolution_rate": 1.0},
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
                            "compiled checks + the v6 fact vocabulary; pending SME "
                            "(Kayla) review of results"),
    }
    with open(NEW_RULESET_OUT, "w") as f:
        json.dump(wrapper, f, indent=2)

    log.log("setup", "run_finished", results_path=RESULTS_OUT, ruleset_path=NEW_RULESET_OUT)

    print("vocabulary: v{} ({} facts)".format(vocab.version, len(vocab.facts)))
    print("preconditions: {} attached, {} flagged, {} unconditional".format(
        len(attached), len(flagged), unconditional))
    print("replay: {} flips vs deployed baseline".format(len(rep.flips)))
    for p in per_loan:
        print("  {}: {} -- {}".format(p["loan_id"], p["disposition"], p["status_counts"]))
    print("wrote {}".format(RESULTS_OUT))
    print("wrote {}".format(NEW_RULESET_OUT))
    print("eval log: {}".format(log.path))


if __name__ == "__main__":
    main()
