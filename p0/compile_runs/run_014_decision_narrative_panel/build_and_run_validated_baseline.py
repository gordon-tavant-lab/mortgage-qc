"""
run_014 -- decision-narrative panel, VALIDATED-BASELINE variant (spec 014
correction, 2026-07-28): the original `build_and_run.py` grounds its 5-loan
proof in `run_013`'s comprehensive_e2e_v6 ruleset (3,203 checks/loan, ~97%
of which reference document types this 5-loan synthetic corpus doesn't even
have) -- a deliberate SC-001 stress test of the sampling/aggregation logic
at real scale (spec.md's own "hundreds of exceptions" edge case), but a
poor demonstration of the feature's actual reviewer-facing value, since the
real signal (this project's 25 known planted defects,
`p0/fixtures/from_docs/defect_manifest.json`) gets buried in noise from
checks that were never going to fire on this test data.

This script generates the SAME narrative artifact against the repo's own
documented "proven, trusted rule set -- 100% recall on the 25 known planted
defects, 0 report drift" (`result/README.md`, `p0/fixtures/ruleset_defects.py`
:`defects_ruleset_for`), run against the canonical, fully-cited loan facts
at `result/loans/loan_0N.json` (confirmed byte-identical to
`p0/fixtures/from_docs/loan_0N.json` -- same extraction, just the
`result/`-store copy Gordon pointed at directly). This is the narrative a
human reviewer should actually see for these 5 demo loans; the original
comprehensive-ruleset run remains valid as its own separate real-scale
sampling proof and is not deleted.

Run: python3 p0/compile_runs/run_014_decision_narrative_panel/build_and_run_validated_baseline.py
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
from fixtures.ruleset_defects import defects_ruleset_for       # noqa: E402
from qc_engine.compiler import compile_llm                    # noqa: E402
from qc_engine.compiler import decision_narrative as DN        # noqa: E402
from qc_engine.compiler import fact_vocabulary as FV            # noqa: E402
from qc_engine.eval_log import EvalLog                          # noqa: E402
from qc_engine.engine import run                                 # noqa: E402

RUN_ID = "run_014_decision_narrative_panel_validated_baseline"
VOCAB_DIR = os.path.join(_REPO_ROOT, "storage", "fact_vocabulary")
LOANS_DIR = os.path.join(_REPO_ROOT, "result", "loans")
RESULTS_OUT = os.path.join(_REPO_ROOT, "result", "qc_results",
                           "{}_results.json".format(RUN_ID))
LOAN_NUMBERS = ("01", "02", "03", "04", "05")

# Sonnet 4.6 on-demand pricing, $/1M tokens -- same figures as the original
# build_and_run.py (verified 2026-06-28, platform.claude.com pricing).
_PRICE_INPUT_PER_M = Decimal("3.00")
_PRICE_OUTPUT_PER_M = Decimal("15.00")
_REGIONAL_PREMIUM = Decimal("1.10")


class _CostTrackingClient:
    """Wraps the real Bedrock client's .converse() to record token usage per
    call -- identical to the original build_and_run.py's helper."""

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


def _panel():
    """The 5 real document-extracted loans, read directly from `result/loans/`
    -- the canonical, fully-cited CanonicalLoan JSON (confirmed byte-identical
    to `p0/fixtures/from_docs/loan_0N.json`). No loan_profiles/v2 derived-fact
    overlay here -- the validated baseline ruleset only ever references
    fields this extraction already populates."""
    loans = []
    for n in LOAN_NUMBERS:
        loan = load_canonical_loan(os.path.join(LOANS_DIR, "loan_{}.json".format(n)))
        loans.append(loan)
    return loans


def main():
    log = EvalLog(RUN_ID)
    log.log("setup", "run_started", vocab_dir=VOCAB_DIR, loans_dir=LOANS_DIR,
             ruleset="fixtures.ruleset_defects.defects_ruleset_for (validated baseline, "
                     "100% recall on 25 known planted defects per result/README.md)")

    vocab = FV.load_latest(VOCAB_DIR)
    log.log("setup", "vocabulary_loaded", version=vocab.version, fact_count=len(vocab.facts))

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
        ruleset = defects_ruleset_for(loan)
        rr = run(loan, ruleset)
        entry = {
            "loan_id": loan.loan_id, "disposition": rr.disposition,
            "review_reasons": sorted(rr.review_reasons),
            "total_checks": len(rr.results),
            "total_exceptions_and_needs_review": len(rr.exceptions) + len(rr.needs_review),
            "ruleset_checks_applicable_to_this_loan": len(ruleset.checks),
        }
        if client_available:
            tracked = _CostTrackingClient(real_client)
            try:
                narrative = DN.generate(rr, vocab, tracked, max_retries=2)
            except Exception as e:  # noqa: BLE001
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
                             "engine run itself is zero-LLM"))
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
                     "calls only").format(len(loans)))

    out = {
        "run": RUN_ID,
        "built_from": ("result/loans/loan_0N.json (canonical, fully-cited extraction) run "
                      "through fixtures.ruleset_defects.defects_ruleset_for -- the repo's "
                      "documented validated baseline, 100% recall on the 25 known planted "
                      "defects (result/README.md), NOT run_013's comprehensive_e2e_v6 "
                      "ruleset (see build_and_run.py for that separate real-scale "
                      "sampling stress test, kept as its own SC-001 proof)."),
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
