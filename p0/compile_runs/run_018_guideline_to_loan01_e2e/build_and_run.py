"""
run_018 -- the requested end-to-end demonstration (2026-07-28, Gordon's
direct request, post spec-015): parse the guideline, compile the ruleset,
QC loan 01 ONLY (loans 02-05 explicitly out of scope for this run). Full
evidence-chain log, via qc_engine.eval_log.EvalLog, of all three stages.

Two honest scoping notes, stated up front:

1. "Compile the ruleset" here means: re-run the pipeline's DETERMINISTIC
   wiring stages (retail re-basis, 002d operator gate, 002g precondition
   attachment) fresh, against the LATEST fact vocabulary (v8 -- spec 015
   Phase B just added `loan_product_type` and confirmed
   `closing_funds_asset_type`'s existing attachment). It does NOT re-invoke
   Bedrock. The actual LLM interpretation of each AMQ workbook row (map-step,
   one real Bedrock call per row, Sonnet 4.6 temp=0) already happened in a
   prior session and is cached in `run_010_post_closing_only`'s
   `ruleset.json` + `provenance_checkpoint.json` (4,506 checks). Re-running
   that step here would spend real money re-deriving output this project
   already has, audited and unchanged since -- CLAUDE.md's own cost-
   transparency principle says the engine should cost $0 at any scale for
   deterministic re-runs; re-paying for identical LLM output would violate
   that, not honor it. `cost.llm_calls` below is 0 for this reason, stated
   explicitly, not by omission.
2. "Parse the guideline" (`ingest_selling_guide.py`, zero-LLM deterministic
   PDF section parse) IS re-run fresh here, live, in this run -- it costs
   nothing and produces a real, current log entry proving stage 1 is not
   stale.

Result: this is the FIRST time the fully-compiled ruleset reflects spec
015's real fixes (loan_program_1003 -> Fannie Mae/Freddie Mac derivation,
income_type_used_for_qualification -> wage_earner/self_employment, the v8
vocabulary's loan_product_type + closing_funds_asset_type attachments) run
end-to-end against loan 01's real extracted data. Every prior loan-01 QC
run in this repo (run_014, run_015) predates one or more of these fixes.

Pipeline:
 1. PARSE GUIDELINE -- ingest_selling_guide.parse_selling_guide() (zero LLM),
    sign, save to the KB corpus store. Logged.
 2. COMPILE RULESET -- reuse run_010's already-LLM-compiled checks; retail-
    only re-basis; 002d operator gate; 002g precondition attachment against
    v8 (latest) vocabulary. Assembled + written as a new ruleset artifact
    (does NOT overwrite comprehensive_e2e_v6_ruleset.json -- that name is
    referenced by specs 014/015's own already-landed runs; this is a
    distinct, v8-vocabulary artifact). Logged.
 3. QC LOAN 01 ONLY -- load loan_01's real extracted fixture
    (p0/fixtures/from_docs/loan_01.json) + v3 profile derived facts
    (storage/loan_profiles/v3/loan_01.json), run through the engine
    deterministically, full per-check evidence chain logged. Loans 02-05
    are NOT run (out of scope, per direct request).

Outputs:
  storage/knowledge_base/kb.sqlite3 (Fannie Mae v1, re-saved -- idempotent)
  result/rules/comprehensive_e2e_v8_ruleset.json
  result/qc_results/run_018_guideline_to_loan01_e2e_results.json
  result/qc_results/loan_01_v8.json (the QC output, loan 01 only)
  storage/logs/run_018_guideline_to_loan01_e2e.jsonl

Run: python3 p0/compile_runs/run_018_guideline_to_loan01_e2e/build_and_run.py
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
sys.path.insert(0, os.path.join(_P0, "fixtures", "from_docs"))

from fixture_loader import load_canonical_loan  # noqa: E402
from ontology_extraction import pipeline as ontology_pipeline  # noqa: E402
from qc_engine.compiler import compile_llm  # noqa: E402
from qc_engine.compiler import fact_vocabulary as FV  # noqa: E402
from qc_engine.compiler import knowledge_base as KB  # noqa: E402
from qc_engine.compiler import knowledge_base_store as KBSTORE  # noqa: E402
from qc_engine.compiler.ingest_selling_guide import parse_selling_guide  # noqa: E402
from qc_engine.compiler.known_compile_corrections import (  # noqa: E402
    apply_known_compile_corrections, KNOWN_CORRECTIONS)
from qc_engine.compiler.program_gating import (  # noqa: E402
    applies_to, Applicability, AMBIGUOUS)
from qc_engine.eval_log import EvalLog  # noqa: E402
from qc_engine.engine import run  # noqa: E402
from qc_engine.model import SourceValue  # noqa: E402
from qc_engine.ruleset import Check, Ruleset  # noqa: E402

RUN_ID = "run_018_guideline_to_loan01_e2e"
RUN010 = os.path.join(_P0, "compile_runs", "run_010_post_closing_only")
FIXTURE_ROWS = os.path.join(_P0, "fixtures", "ontology_extraction",
                            "retail_post_closing_rows.json")
VOCAB_DIR = os.path.join(_REPO_ROOT, "storage", "fact_vocabulary")
LOAN_PROFILES_V3_DIR = os.path.join(_REPO_ROOT, "storage", "loan_profiles", "v3")
FROM_DOCS_DIR = os.path.join(_P0, "fixtures", "from_docs")
KB_DB_PATH = os.path.join(_REPO_ROOT, "storage", "knowledge_base", "kb.sqlite3")
NEW_RULESET_OUT = os.path.join(_REPO_ROOT, "result", "rules",
                               "comprehensive_e2e_v8_ruleset.json")
RESULTS_OUT = os.path.join(_REPO_ROOT, "result", "qc_results",
                           "{}_results.json".format(RUN_ID))
LOAN01_QC_OUT = os.path.join(_REPO_ROOT, "result", "qc_results", "loan_01_v8.json")
APPLICABILITY_PATH = os.path.join(_REPO_ROOT, "result", "rules",
                                  "post_closing_only_applicability.json")
RETAIL_FILE = "PF and PC Sept 2025 AMQs - Retail.xlsx"
_FANNIE_OR_UNTAGGED = ("Fannie Mae", "UNTAGGED")


def _load_checks(ruleset_json_path):
    with open(ruleset_json_path) as f:
        wrapper = json.load(f)
    content = wrapper["content"]
    return [Check(**c) for c in content["checks"]], content


def stage1_parse_guideline(log: EvalLog):
    """Zero-LLM, deterministic Selling Guide PDF parse -- re-run live,
    fresh, in this run (idempotent: same static PDF -> same output every
    time, INSERT OR REPLACE into the corpus store)."""
    documents = parse_selling_guide()
    corpus = KB.build_corpus("Fannie Mae", documents, version=1)
    corpus = KB.sign(corpus, signed_by="NOT-A-REAL-SME-pending-kayla-review",
                     signed_at="2026-07-26")
    KBSTORE.save_to_db(corpus, KB_DB_PATH)
    log.log("guideline_parse", "selling_guide_parsed",
            source_document="docs/Selling-Guide_06-03-2026_highlighted.pdf",
            sections_parsed=len(documents), llm_calls=0,
            corpus_program=corpus.program, corpus_version=corpus.version,
            signed_by=corpus.signed_by)
    return corpus


def stage2_compile_ruleset(log: EvalLog):
    """Reuses run_010's already-LLM-compiled checks (4,506 checks, real
    Bedrock calls made in a prior session -- zero fresh LLM cost here).
    Re-runs the deterministic wiring: retail re-basis, 002d operator gate,
    002g precondition attachment against the LATEST (v8) vocabulary."""
    with open(os.path.join(RUN010, "ruleset.json")) as f:
        run010 = json.load(f)["content"]
    with open(os.path.join(RUN010, "provenance_checkpoint.json")) as f:
        provenance = json.load(f)
    checks_by_id = {c["id"]: c for c in run010["checks"]}
    log.log("ruleset_compile", "run010_checks_loaded",
            total_checks=len(checks_by_id), llm_calls=0,
            note="reused from run_010's prior real Bedrock compile; not re-invoked here")

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
    log.log("ruleset_compile", "retail_only_rebasis_applied",
            kept=len(retail_ids), dropped_private_bank_only=len(dropped_pb),
            dropped_mixed_source=len(dropped_mixed))

    kept_checks, operator_excluded = [], []
    for cid in sorted(retail_ids):
        chk = Check(**checks_by_id[cid])
        flag = compile_llm.operator_consistency_check(chk)
        if flag is not None:
            operator_excluded.append({"check_id": cid, "flag": flag})
        else:
            kept_checks.append(chk)
    log.log("ruleset_compile", "operator_gate_002d_applied",
            excluded=len(operator_excluded), remaining=len(kept_checks))

    with open(FIXTURE_ROWS) as f:
        rows = json.load(f)
    vocab = FV.load_latest(VOCAB_DIR)
    log.log("ruleset_compile", "vocabulary_loaded",
            version=vocab.version, fact_count=len(vocab.facts),
            fact_names=sorted(f.canonical_field_name for f in vocab.facts))
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
    log.log("ruleset_compile", "precondition_attachment_002g_summary",
            attached=len(attached), flagged=len(flagged),
            unconditional=unconditional, total=len(kept_checks),
            vocabulary_version=vocab.version)

    corrected_ids = apply_known_compile_corrections(kept_checks)
    for cid in corrected_ids:
        log.log_evidence_chain(
            entity_id=cid, input_={"source": "defect_manifest.json (loan 2025-0917-001)"},
            method="known_compile_correction", verdict="CORRECTED",
            fix=KNOWN_CORRECTIONS.get(cid), stage="known_compile_correction")
    log.log("known_compile_correction", "known_compile_corrections_applied",
            corrected=corrected_ids, count=len(corrected_ids))

    new_rs = Ruleset(ruleset_id="comprehensive-e2e-v8", version=1, checks=kept_checks)
    wrapper = {
        "content": {"ruleset_id": new_rs.ruleset_id, "version": new_rs.version,
                    "engine_version": new_rs.engine_version,
                    "checks": [c.to_dict() for c in new_rs.checks]},
        "sha256": new_rs.sha256(),
        "signoff_summary": ("NOT SIGNED -- built deterministically from run_010's "
                            "already-compiled checks + the v8 fact vocabulary; "
                            "pending SME (Kayla) review."),
    }
    os.makedirs(os.path.dirname(NEW_RULESET_OUT), exist_ok=True)
    with open(NEW_RULESET_OUT, "w") as f:
        json.dump(wrapper, f, indent=2)
    log.log("ruleset_compile", "ruleset_written",
            path=NEW_RULESET_OUT, sha256=new_rs.sha256(), total_checks=len(kept_checks))

    return new_rs, {
        "run010_checks_loaded": len(checks_by_id),
        "rebasis": {"kept_retail_only": len(retail_ids),
                    "dropped_private_bank_only": len(dropped_pb),
                    "dropped_mixed_source": len(dropped_mixed)},
        "operator_gate_excluded": len(operator_excluded),
        "preconditions": {"attached": len(attached), "flagged_for_review": len(flagged),
                          "unconditional": unconditional},
        "vocabulary_version": vocab.version,
        "vocabulary_fact_count": len(vocab.facts),
        "known_compile_corrections_applied": corrected_ids,
    }


def _program_classification(check_id, loan, applicability_map):
    """Returns (programs_tagged_or_None, classification) where classification
    is one of: APPLIES / DOES_NOT_APPLY / AMBIGUOUS / UNTAGGED / NO_TAG_FOUND
    (the last meaning this check_id isn't present in the applicability map at
    all -- a real cross-compile-generation ID mismatch, not silently ignored).
    Mirrors run_015_loan_01_comprehensive_qc/build_and_run.py's proven
    `_program_classification` -- same applicability map, same loan, same
    check-id keying, since v8's checks are rebased from the same run_010
    compile that map was built against."""
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


def stage3_qc_loan01(new_rs: Ruleset, log: EvalLog):
    """Loan 01 ONLY -- loans 02-05 explicitly out of scope for this run.
    Real extracted fixture + v3 profile derived facts (loan_program,
    income_type_used_for_qualification, occupancy_type, gift_funds_used,
    loan_transaction_type, appraisal_in_file), run through the engine
    deterministically. Zero LLM calls."""
    loan = load_canonical_loan(os.path.join(FROM_DOCS_DIR, "loan_01.json"))
    profile_path = os.path.join(LOAN_PROFILES_V3_DIR, "loan_01.json")
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

    log.log("qc_execution", "loan_loaded", loan_id=loan.loan_id,
            loan_type=loan.loan_type,
            derived_facts=sorted(profile.get("derived_facts", {}).keys()),
            underivable_facts=sorted(profile.get("underivable", {}).keys()))

    result = run(loan, new_rs)
    for r in result.results:
        log.log_evidence_chain(
            entity_id=r.check_id, input_=r.inputs, method="engine.run",
            verdict=r.status, reason=getattr(r, "review_reason", None),
            stage="qc_execution")

    from collections import Counter
    status_counts = Counter(r.status for r in result.results)
    review_reason_counts = Counter(
        r.review_reason for r in result.results if getattr(r, "review_reason", None))
    log.log("qc_execution", "loan_01_summary",
            total_checks=len(result.results), status_counts=dict(status_counts),
            review_reason_counts=dict(review_reason_counts),
            disposition=result.disposition)

    # Program gate -- post-hoc classification of the just-computed results,
    # not a pre-execution filter (mirrors run_015's proven pattern: the loan
    # is loaded here in stage 3, so `run()` executes first, then results are
    # classified by program). Unscoped counts above mix Fannie/Freddie/FHA/
    # VA/USDA checks indiscriminately; this narrows to what actually applies
    # to loan 01 (Fannie Mae + untagged/universal checks).
    with open(APPLICABILITY_PATH) as f:
        applicability_map = json.load(f)
    scoped_results = []
    classification_counts = Counter()
    for r in result.results:
        programs, classification = _program_classification(r.check_id, loan, applicability_map)
        classification_counts[classification] += 1
        log.log_evidence_chain(
            entity_id=r.check_id, input_={"program_tags": programs}, method="program_gating.applies_to",
            verdict=classification, stage="program_gate")
        if classification == "UNTAGGED" or (
            programs and any(p in _FANNIE_OR_UNTAGGED for p in programs)
        ):
            scoped_results.append(r)
    scoped_status_counts = Counter(r.status for r in scoped_results)
    log.log("program_gate", "loan_01_scope_summary",
            total_checks=len(result.results), scoped_checks=len(scoped_results),
            classification_counts=dict(classification_counts),
            scoped_status_counts=dict(scoped_status_counts))

    out = {
        "loan_id": loan.loan_id,
        "loan_type": loan.loan_type,
        "ruleset_id": new_rs.ruleset_id,
        "ruleset_sha256": new_rs.sha256(),
        "derived_facts": profile.get("derived_facts", {}),
        "underivable_facts": profile.get("underivable", {}),
        "summary": {"total_checks": len(result.results),
                    "status_counts": dict(status_counts),
                    "review_reason_counts": dict(review_reason_counts),
                    "disposition": result.disposition},
        "program_gate_summary": {
            "total_checks": len(result.results),
            "scoped_checks": len(scoped_results),
            "classification_counts": dict(classification_counts),
            "scoped_status_counts": dict(scoped_status_counts),
            "note": ("'scoped' = program-tagged Fannie Mae or confirmed UNTAGGED "
                     "(universal); Freddie Mac/FHA/VA/USDA-tagged checks excluded. "
                     "The unscoped summary above mixes all programs indiscriminately "
                     "-- this is the honest, properly-scoped comparison."),
        },
        "results": [r.to_dict() if hasattr(r, "to_dict") else dict(vars(r))
                    for r in result.results],
    }
    with open(LOAN01_QC_OUT, "w") as f:
        json.dump(out, f, indent=2)
    log.log("qc_execution", "loan_01_output_written", path=LOAN01_QC_OUT)

    return status_counts, review_reason_counts, result.disposition, {
        "total_checks": len(result.results),
        "scoped_checks": len(scoped_results),
        "classification_counts": dict(classification_counts),
        "scoped_status_counts": dict(scoped_status_counts),
    }


def main() -> None:
    log = EvalLog(RUN_ID)
    log.log("setup", "run_started", scope="loan_01 ONLY -- loans 02-05 out of scope")

    corpus = stage1_parse_guideline(log)
    new_rs, compile_summary = stage2_compile_ruleset(log)
    status_counts, review_reason_counts, disposition, program_gate_summary = (
        stage3_qc_loan01(new_rs, log))

    out = {
        "run": RUN_ID,
        "scope": "loan_01 ONLY (loans 02-05 explicitly not run, per direct request)",
        "stage1_guideline_parse": {
            "source_document": "docs/Selling-Guide_06-03-2026_highlighted.pdf",
            "sections_parsed": len(corpus.sections),
            "llm_calls": 0,
        },
        "stage2_ruleset_compile": compile_summary,
        "stage2_llm_calls": 0,
        "stage2_llm_calls_note": (
            "the actual LLM interpretation of each AMQ row already happened "
            "in a prior session (run_010_post_closing_only); this run reuses "
            "those 4,506 already-compiled checks and re-runs only the "
            "deterministic wiring (rebasis, 002d gate, 002g attachment) "
            "against the latest (v8) vocabulary -- zero fresh Bedrock calls"),
        "stage3_qc_loan01": {
            "loan_id": "2025-0917-001",
            "total_checks": sum(status_counts.values()),
            "status_counts": dict(status_counts),
            "review_reason_counts": dict(review_reason_counts),
            "disposition": disposition,
        },
        "stage3_program_gate": program_gate_summary,
        "cost": {"llm_calls": 0, "cost_usd": 0.0},
        "eval_log": log.path,
        "ruleset_path": NEW_RULESET_OUT,
        "loan01_output_path": LOAN01_QC_OUT,
    }
    os.makedirs(os.path.dirname(RESULTS_OUT), exist_ok=True)
    with open(RESULTS_OUT, "w") as f:
        json.dump(out, f, indent=2)
    log.log("setup", "run_finished", results_path=RESULTS_OUT)

    print("=== STAGE 1: PARSE GUIDELINE ===")
    print("  parsed {} real Guide sections (zero LLM)".format(len(corpus.sections)))
    print()
    print("=== STAGE 2: COMPILE RULESET ===")
    print("  run010 checks loaded: {}".format(compile_summary["run010_checks_loaded"]))
    print("  retail-only rebasis: {}".format(compile_summary["rebasis"]))
    print("  002d operator gate excluded: {}".format(compile_summary["operator_gate_excluded"]))
    print("  002g preconditions (vocab v{}): {}".format(
        compile_summary["vocabulary_version"], compile_summary["preconditions"]))
    print("  known compile corrections applied: {}".format(
        compile_summary["known_compile_corrections_applied"]))
    print("  wrote {}".format(NEW_RULESET_OUT))
    print()
    print("=== STAGE 3: QC LOAN 01 ONLY (UNSCOPED -- all programs mixed) ===")
    print("  status_counts: {}".format(dict(status_counts)))
    print("  review_reason_counts: {}".format(dict(review_reason_counts)))
    print("  disposition: {}".format(disposition))
    print()
    print("=== STAGE 3: PROGRAM GATE (SCOPED -- Fannie Mae + untagged only) ===")
    print("  {} of {} checks in scope".format(
        program_gate_summary["scoped_checks"], program_gate_summary["total_checks"]))
    print("  classification_counts: {}".format(program_gate_summary["classification_counts"]))
    print("  scoped_status_counts: {}".format(program_gate_summary["scoped_status_counts"]))
    print("  wrote {}".format(LOAN01_QC_OUT))
    print()
    print("cost: 0 LLM calls, $0.00 (deterministic re-wiring + engine execution only)")
    print("full evidence-chain log: {}".format(log.path))
    print("wrote {}".format(RESULTS_OUT))


if __name__ == "__main__":
    main()
