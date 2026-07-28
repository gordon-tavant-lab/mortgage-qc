"""
run_014 -- decision-narrative panel (spec 014, T009-T014): reuses run_013's
already-built comprehensive-e2e-v6 ruleset and 5-loan (v2-derived-fields)
panel, generates one real DecisionNarrative per loan via
qc_engine.compiler.decision_narrative.generate(), and logs LLM cost through
qc_engine.eval_log.EvalLog.log_cost (FR-009) -- the one place in this
pipeline that spends real, per-loan-per-run LLM cost, unlike every other
zero-LLM stage the eval log already reports honestly.

Loads the LATEST signed FactVocabulary (storage/fact_vocabulary/ -- v7 as of
2026-07-28, after 010b added occupancy_type/loan_program on top of v6's 16
facts) via FV.load_latest(), the exact read-side convention that module's
own docstring documents; does NOT hardcode a version number.

`decision_narrative.generate()`'s own tested contract returns only a
DecisionNarrative (no usage/cost payload) -- cost accounting is this
driver's concern, not core generation logic, so token usage is captured by
wrapping the real Bedrock client's `.converse()` (`_CostTrackingClient`,
below), not by changing `generate()`'s signature.

Run: python3 p0/compile_runs/run_014_decision_narrative_panel/build_and_run.py
Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys
from decimal import Decimal

_HERE = os.path.dirname(os.path.abspath(__file__))
_P0 = os.path.dirname(os.path.dirname(_HERE))
_REPO_ROOT = os.path.dirname(_P0)
for p in (_P0, os.path.join(_P0, "fixtures", "from_docs")):
    if p not in sys.path:
        sys.path.insert(0, p)

from fixture_loader import load_canonical_loan                # noqa: E402
from qc_engine.compiler import compile_llm                    # noqa: E402
from qc_engine.compiler import decision_narrative as DN        # noqa: E402
from qc_engine.compiler import fact_vocabulary as FV            # noqa: E402
from qc_engine.eval_log import EvalLog                          # noqa: E402
from qc_engine.engine import run                                 # noqa: E402
from qc_engine.model import SourceValue                          # noqa: E402
from qc_engine.ruleset import Check, Ruleset                     # noqa: E402

RUN_ID = "run_014_decision_narrative_panel"
VOCAB_DIR = os.path.join(_REPO_ROOT, "storage", "fact_vocabulary")
LOAN_PROFILES_V2_DIR = os.path.join(_REPO_ROOT, "storage", "loan_profiles", "v2")
FROM_DOCS_DIR = os.path.join(_P0, "fixtures", "from_docs")
RULESET_PATH = os.path.join(_REPO_ROOT, "result", "rules",
                           "comprehensive_e2e_v6_ruleset.json")
RESULTS_OUT = os.path.join(_REPO_ROOT, "result", "qc_results",
                           "{}_results.json".format(RUN_ID))
LOAN_NUMBERS = ("01", "02", "03", "04", "05")

# Sonnet 4.6 on-demand pricing, $/1M tokens -- the same figures already
# locked in p0/experiment_g3/bakeoff.py's D3 cost constants (verified
# 2026-06-28, platform.claude.com/docs/.../pricing). The "us." cross-region
# inference profile carries the same +10% regional premium bakeoff.py
# already accounts for.
_PRICE_INPUT_PER_M = Decimal("3.00")
_PRICE_OUTPUT_PER_M = Decimal("15.00")
_REGIONAL_PREMIUM = Decimal("1.10")


class _CostTrackingClient:
    """Wraps the real Bedrock client's .converse() to record token usage per
    call. decision_narrative.generate() stays cost-agnostic by design (its
    tested contract returns only a DecisionNarrative) -- cost accounting is
    a driver/reporting concern (FR-009), not core generation logic."""

    def __init__(self, real_client):
        self._client = real_client
        self.calls = []

    def converse(self, **kwargs):
        resp = self._client.converse(**kwargs)
        usage = resp.get("usage", {}) or {}
        self.calls.append({
            "input_tokens": usage.get("inputTokens", 0),
            "output_tokens": usage.get("outputTokens", 0),
        })
        return resp


def _cost_usd(calls):
    input_tokens = sum(c["input_tokens"] for c in calls)
    output_tokens = sum(c["output_tokens"] for c in calls)
    cost = (Decimal(input_tokens) / Decimal(1000000) * _PRICE_INPUT_PER_M
            + Decimal(output_tokens) / Decimal(1000000) * _PRICE_OUTPUT_PER_M)
    return cost * _REGIONAL_PREMIUM, input_tokens, output_tokens


def _load_ruleset():
    with open(RULESET_PATH) as f:
        wrapper = json.load(f)
    content = wrapper["content"]
    checks = [Check(**c) for c in content["checks"]]
    return Ruleset(ruleset_id=content["ruleset_id"], version=content["version"],
                   checks=checks)


def _panel():
    """The same 5 real document-extracted loans, with every v2-derived fact
    wired onto loan.fields as a real SourceValue -- run_013's own
    _panel_from_v2_profiles(), minus that run's own evidence-chain logging
    (not this run's concern; run_013 already logged loan-profile derivation
    once, and it is not re-derived here)."""
    loans = []
    for n in LOAN_NUMBERS:
        loan = load_canonical_loan(os.path.join(FROM_DOCS_DIR, "loan_{}.json".format(n)))
        profile_path = os.path.join(LOAN_PROFILES_V2_DIR, "loan_{}.json".format(n))
        with open(profile_path) as f:
            profile = json.load(f)
        for fact_name, entry in profile.get("derived_facts", {}).items():
            loan.fields[fact_name] = SourceValue(doc=entry["value"])
        loans.append(loan)
    return loans


def main():
    log = EvalLog(RUN_ID)
    log.log("setup", "run_started", vocab_dir=VOCAB_DIR, ruleset_path=RULESET_PATH)

    vocab = FV.load_latest(VOCAB_DIR)
    log.log("setup", "vocabulary_loaded", version=vocab.version, fact_count=len(vocab.facts))

    ruleset = _load_ruleset()
    loans = _panel()

    try:
        real_client = compile_llm._client()
    except Exception as e:  # noqa: BLE001 -- no boto3/AWS profile in this env
        real_client = None
        log.log("setup", "bedrock_client_construction_failed",
                error="{}: {}".format(type(e).__name__, e))

    client_available = real_client is not None
    per_loan = []
    total_cost = Decimal("0")
    total_calls = 0

    for loan in loans:
        rr = run(loan, ruleset)
        entry = {
            "loan_id": loan.loan_id, "disposition": rr.disposition,
            "review_reasons": sorted(rr.review_reasons),
            "total_checks": len(rr.results),
            "total_exceptions_and_needs_review": len(rr.exceptions) + len(rr.needs_review),
        }
        if client_available:
            tracked = _CostTrackingClient(real_client)
            try:
                narrative = DN.generate(rr, vocab, tracked, max_retries=2)
            except Exception as e:  # noqa: BLE001 -- e.g. a network/credential
                # failure on the FIRST live call -- stop attempting Bedrock
                # for the remaining loans (spec.md Edge Cases: narrative
                # generation failing must never block the structured
                # result), log it honestly, and fall through.
                client_available = False
                log.log("narrative_generation", "bedrock_call_failed",
                        loan_id=loan.loan_id, error="{}: {}".format(type(e).__name__, e))
                entry["decision_narrative"] = None
                entry["narrative_generation_skipped_reason"] = (
                    "Bedrock call failed: {}: {}".format(type(e).__name__, e))
                per_loan.append(entry)
                print("  {}: {} -- narrative FAILED ({})".format(
                    loan.loan_id, rr.disposition, type(e).__name__))
                continue
            cost_usd, in_tok, out_tok = _cost_usd(tracked.calls)
            total_cost += cost_usd
            total_calls += len(tracked.calls)
            log.log_cost(llm_calls=len(tracked.calls), cost_usd=float(cost_usd),
                        deterministic_resolution_rate=0.0, loan_id=loan.loan_id,
                        input_tokens=in_tok, output_tokens=out_tok,
                        narrative_text_present=narrative.narrative_text is not None,
                        validation_attempts=narrative.validation_attempts,
                        note=("narrative generation only -- the deterministic "
                             "engine run itself is zero-LLM (run_013 precedent)"))
            entry["decision_narrative"] = narrative.to_dict()
            entry["narrative_cost_usd"] = float(cost_usd)
            entry["narrative_tokens"] = {"input": in_tok, "output": out_tok}
        else:
            entry["decision_narrative"] = None
            entry["narrative_generation_skipped_reason"] = (
                "Bedrock client unavailable in this environment")

        per_loan.append(entry)
        print("  {}: {} -- narrative {}".format(
            loan.loan_id, rr.disposition,
            "generated" if entry.get("decision_narrative") else "SKIPPED/FAILED"))

    log.log_cost(llm_calls=total_calls, cost_usd=float(total_cost),
                deterministic_resolution_rate=(1.0 if total_calls == 0 else 0.0),
                note=("run-level total across all {} loans' narrative-generation "
                     "calls only -- the engine's own 16,020-check evaluation "
                     "(run_013 precedent) remains zero-LLM").format(len(loans)))

    out = {
        "run": RUN_ID,
        "built_from": ("run_013's comprehensive_e2e_v6 ruleset + v2 loan profiles "
                      "(zero recompile, zero re-derivation)"),
        "vocabulary_version": vocab.version,
        "vocabulary_fact_count": len(vocab.facts),
        "bedrock_available": client_available,
        "per_loan": per_loan,
        "cost_summary": {"llm_calls": total_calls, "cost_usd": float(total_cost)},
        "eval_log": log.path,
    }
    os.makedirs(os.path.dirname(RESULTS_OUT), exist_ok=True)
    with open(RESULTS_OUT, "w") as f:
        json.dump(out, f, indent=2)

    log.log("setup", "run_finished", results_path=RESULTS_OUT)

    print("vocabulary: v{} ({} facts)".format(vocab.version, len(vocab.facts)))
    print("bedrock available: {}".format(client_available))
    print("total narrative cost: ${:.4f} across {} calls".format(total_cost, total_calls))
    print("wrote {}".format(RESULTS_OUT))
    print("eval log: {}".format(log.path))


if __name__ == "__main__":
    main()
