"""
G3 Bake-Off Runner — Arm A (compiled engine) vs Arm B (governed runtime-LLM).

Executes the PRE-REGISTERED experiment (see PRE-REGISTRATION.md). The decision
rules D1/D2/D3 and their verdict mapping were LOCKED before this ran; this file
only *measures* and *applies* them — it must not introduce a new rule.

What it does, per the pre-registration:
  - Arm A: qc_engine.run(loan, signed_ruleset). Pure Decimal, no model.
  - Arm B: llm_arm.evaluate_llm(...) at temperature=0, N=5 times per loan.
  - D1 (determinism): are Arm B's 5 verdict sets byte-identical, every loan?
  - D2 (accuracy / safety): does either arm produce a FALSE-AUTO-CLEAR
        (says PASS where the labeled truth is a defect)? Per-arm count.
  - D3 (cost): real Bedrock tokens/loan for Arm B -> extrapolate to 10,000.
        Haiku 4.5 on-demand: $1.00/MTok input, $5.00/MTok output (verified
        2026-06-28, platform.claude.com/docs/.../pricing). The "us." cross-
        region inference profile carries a +10% regional premium on Bedrock;
        we report both the global-rate and regional-rate extrapolations.

Honesty: the accuracy axis is DIRECTIONAL on synthetic loans (see caveats in
the pre-registration). Determinism and cost generalize. Labels are loud.

Run:  python bakeoff.py            # full run (calls Bedrock)
      python bakeoff.py --arm-a    # Arm A only, no network (sanity)
Writes: artifacts/g3_bakeoff_<runtag>.json   (runtag passed in, never wall-clock)

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

# Allow running from experiment_g3/ against the parent p0 package.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qc_engine import run as engine_run                       # noqa: E402
from fixtures.golden import golden_loans                      # noqa: E402
from fixtures.ruleset_demo import demo_ruleset                # noqa: E402

# ---- D3 cost constants (LOCKED inputs; pricing verified, not guessed) -------
# On-demand $/1M tokens, verified 2026-06-28 (platform.claude.com/docs/.../pricing).
PRICING = {
    "haiku":  {"input": Decimal("1.00"), "output": Decimal("5.00"),
               "model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
               "label": "claude-haiku-4-5"},
    "sonnet": {"input": Decimal("3.00"), "output": Decimal("15.00"),
               "model_id": "us.anthropic.claude-sonnet-4-6",
               "label": "claude-sonnet-4-6"},
}
REGIONAL_PREMIUM = Decimal("1.10")        # "us." cross-region profile = +10%
SCALE_LOANS = 10_000                       # the thesis's stated scale
N_RUNS = 5                                  # determinism repetitions per loan

# D3 thresholds (from the pre-registration, evaluated on the regional rate that
# this experiment actually pays — the "us." profile).
D3_COST_CONCERN_CONFIRMED = Decimal("2000")   # > this  -> compiled wins on cost
D3_COST_SCAR_STALE = Decimal("200")           # < this  -> cost is not a reason


# A labeled "defect" is any check whose ground-truth status is a hard QC
# failure. FLAG (reconcile/system-out-of-sync) is informational, NOT a defect:
# it does not block auto-clear, so clearing past a FLAG is not a false-clear.
DEFECT_TRUTH = {"FAIL"}


def _dollars(x: Decimal) -> str:
    return f"${x.quantize(Decimal('0.01'))}"


# --------------------------------------------------------------------------- #
# Arm A — the compiled, deterministic engine
# --------------------------------------------------------------------------- #
def run_arm_a() -> Dict[str, Dict[str, str]]:
    """{loan_id: {check_id: status}} from the pure engine (one run is enough —
    determinism is already proven bit-exact by harness.py)."""
    rs = demo_ruleset()
    out: Dict[str, Dict[str, str]] = {}
    for loan, _expected in golden_loans():
        res = engine_run(loan, rs)
        out[loan.loan_id] = {r.check_id: r.status for r in res.results}
    return out


# --------------------------------------------------------------------------- #
# Arm B — the governed runtime-LLM, run N times for determinism
# --------------------------------------------------------------------------- #
def run_arm_b(model_id: str, n_runs: int = N_RUNS
              ) -> Tuple[Dict[str, List[Dict[str, str]]],
                         Dict[str, List[Dict[str, int]]]]:
    """Returns:
      verdicts[loan_id] = [ {check_id: status}, ... ]   (n_runs entries)
      tokens[loan_id]   = [ {input_tokens, output_tokens}, ... ]
    Imported lazily so --arm-a works with no boto3/credentials."""
    from llm_arm import evaluate_llm

    rs = demo_ruleset()
    verdicts: Dict[str, List[Dict[str, str]]] = {}
    tokens: Dict[str, List[Dict[str, int]]] = {}
    for loan, _expected in golden_loans():
        v_runs: List[Dict[str, str]] = []
        t_runs: List[Dict[str, int]] = []
        for _ in range(n_runs):
            verdict, tok = evaluate_llm(loan, rs, model_id=model_id)
            v_runs.append(verdict)
            t_runs.append(tok)
        verdicts[loan.loan_id] = v_runs
        tokens[loan.loan_id] = t_runs
    return verdicts, tokens


# --------------------------------------------------------------------------- #
# D1 — determinism gate
# --------------------------------------------------------------------------- #
def evaluate_d1(arm_b_verdicts: Dict[str, List[Dict[str, str]]]) -> Dict[str, Any]:
    """Are Arm B's N verdict sets byte-identical for EVERY loan? A single
    non-identical loan fails D1 outright (pre-reg D1)."""
    per_loan: Dict[str, bool] = {}
    offenders: List[Dict[str, Any]] = []
    for loan_id, runs in arm_b_verdicts.items():
        canon = [json.dumps(v, sort_keys=True, separators=(",", ":")) for v in runs]
        identical = len(set(canon)) == 1
        per_loan[loan_id] = identical
        if not identical:
            # Surface which checks flickered, for the writeup.
            flicker = {}
            for cid in {c for v in runs for c in v}:
                seen = Counter(v.get(cid) for v in runs)
                if len(seen) > 1:
                    flicker[cid] = dict(seen)
            offenders.append({"loan_id": loan_id, "flicker": flicker})
    passed = all(per_loan.values())
    return {"passed": passed, "per_loan_identical": per_loan,
            "offenders": offenders}


# --------------------------------------------------------------------------- #
# D2 — accuracy / safety gate (the catastrophic error: false-auto-clear)
# --------------------------------------------------------------------------- #
def _false_auto_clears(verdicts: Dict[str, str],
                       expected: Dict[str, str]) -> List[str]:
    """check_ids where an arm said PASS but the labeled truth is a defect."""
    out = []
    for cid, exp in expected.items():
        if exp in DEFECT_TRUTH and verdicts.get(cid) == "PASS":
            out.append(cid)
    return out


def evaluate_d2(arm_a: Dict[str, Dict[str, str]],
                arm_b_verdicts: Optional[Dict[str, List[Dict[str, str]]]]
                ) -> Dict[str, Any]:
    """Per-arm exact-match accuracy + false-auto-clear count vs ground truth.
    For Arm B we use run #1's verdicts (D1 already reports if runs differ)."""
    labels = {loan.loan_id: exp for loan, exp in golden_loans()}

    def score(verdict_by_loan: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
        total = match = 0
        false_clears: List[str] = []
        mismatches: List[str] = []
        for loan_id, expected in labels.items():
            got = verdict_by_loan.get(loan_id, {})
            for cid, exp in expected.items():
                total += 1
                g = got.get(cid, "MISSING")
                if g == exp:
                    match += 1
                else:
                    mismatches.append(f"{loan_id}/{cid}: expected {exp}, got {g}")
            for cid in _false_auto_clears(got, expected):
                false_clears.append(f"{loan_id}/{cid}")
        return {
            "checks_scored": total,
            "exact_match": match,
            "exact_match_rate": round(match / total, 4) if total else 1.0,
            "false_auto_clears": false_clears,
            "false_auto_clear_count": len(false_clears),
            "mismatches": mismatches,
        }

    arm_a_score = score(arm_a)
    arm_b_score = None
    if arm_b_verdicts is not None:
        arm_b_first = {lid: runs[0] for lid, runs in arm_b_verdicts.items()}
        arm_b_score = score(arm_b_first)

    # Gate: Arm B disqualified if it introduces a false-auto-clear Arm A doesn't.
    passed = True
    reason = "Arm B not run (Arm A only)."
    if arm_b_score is not None:
        extra = set(arm_b_score["false_auto_clears"]) - set(
            arm_a_score["false_auto_clears"])
        passed = len(extra) == 0
        reason = ("Arm B has no false-auto-clear beyond Arm A."
                  if passed else
                  f"Arm B false-auto-clears Arm A does not: {sorted(extra)}")
    return {"passed": passed, "reason": reason,
            "arm_a": arm_a_score, "arm_b": arm_b_score}


# --------------------------------------------------------------------------- #
# D3 — cost test
# --------------------------------------------------------------------------- #
def evaluate_d3(arm_b_tokens: Optional[Dict[str, List[Dict[str, int]]]],
                pricing: Dict[str, Any]) -> Dict[str, Any]:
    """Real per-loan tokens -> $/10,000-loan run for Arm B. Arm A is ~$0."""
    if not arm_b_tokens:
        return {"ran": False,
                "note": "Arm B not run; cost axis not measured this pass."}
    in_per_mtok = pricing["input"]
    out_per_mtok = pricing["output"]

    # Average a single inference per loan (one run's tokens; N runs are for D1).
    in_toks: List[int] = []
    out_toks: List[int] = []
    per_loan: Dict[str, Dict[str, float]] = {}
    for loan_id, runs in arm_b_tokens.items():
        li = sum(r["input_tokens"] for r in runs) / len(runs)
        lo = sum(r["output_tokens"] for r in runs) / len(runs)
        in_toks.append(li)
        out_toks.append(lo)
        per_loan[loan_id] = {"avg_input_tokens": round(li, 1),
                             "avg_output_tokens": round(lo, 1)}

    avg_in = Decimal(sum(in_toks)) / Decimal(len(in_toks))
    avg_out = Decimal(sum(out_toks)) / Decimal(len(out_toks))

    def run_cost(scale: int, premium: Decimal = Decimal("1.0")) -> Decimal:
        cin = avg_in * scale / Decimal(1_000_000) * in_per_mtok
        cout = avg_out * scale / Decimal(1_000_000) * out_per_mtok
        return (cin + cout) * premium

    cost_global = run_cost(SCALE_LOANS)
    cost_regional = run_cost(SCALE_LOANS, REGIONAL_PREMIUM)

    # Verdict on the rate this experiment actually paid (the "us." profile).
    paid = cost_regional
    if paid > D3_COST_CONCERN_CONFIRMED:
        finding = "CONFIRMED"  # cost-at-scale concern real; compiled wins cost
    elif paid < D3_COST_SCAR_STALE:
        finding = "STALE"      # cost not a valid reason to prefer compiled
    else:
        finding = "SOFT"       # decide on D1/D2

    return {
        "ran": True,
        "model": f"{pricing['label']} (us. cross-region profile)",
        "pricing_per_mtok": {"input": str(in_per_mtok),
                             "output": str(out_per_mtok),
                             "verified": "2026-06-28 platform.claude.com"},
        "avg_input_tokens_per_loan": round(float(avg_in), 1),
        "avg_output_tokens_per_loan": round(float(avg_out), 1),
        "per_loan": per_loan,
        "scale_loans": SCALE_LOANS,
        "cost_10k_global_rate": _dollars(cost_global),
        "cost_10k_regional_rate": _dollars(cost_regional),
        "arm_a_cost": "$0.00 (CPU only, no tokens)",
        "thresholds": {"confirmed_above": _dollars(D3_COST_CONCERN_CONFIRMED),
                       "stale_below": _dollars(D3_COST_SCAR_STALE)},
        "finding": finding,
    }


# --------------------------------------------------------------------------- #
# Verdict mapping (LOCKED in the pre-registration)
# --------------------------------------------------------------------------- #
def map_verdict(d1: Dict[str, Any], d2: Dict[str, Any],
                d3: Dict[str, Any]) -> Dict[str, Any]:
    arm_b_ran = d2.get("arm_b") is not None
    if not arm_b_ran:
        return {"verdict": "INCOMPLETE",
                "rationale": "Arm B did not run; D1/D2/D3 need both arms."}

    # D1 fail OR D2 fail -> PROCEED with compiled-then-run (determinism/safety
    # justify the architecture regardless of cost).
    if not d1["passed"] or not d2["passed"]:
        drivers = []
        if not d1["passed"]:
            drivers.append("D1: Arm B verdicts were not reproducible (temp=0 "
                           "did not yield byte-identical runs).")
        if not d2["passed"]:
            drivers.append(f"D2: {d2['reason']}")
        return {"verdict": "PROCEED with compiled-then-run architecture",
                "rationale": " ".join(drivers)}

    # Arm B passed D1 AND D2. Cost becomes the tie-breaker per the pre-reg.
    if d3.get("ran") and d3.get("finding") == "STALE":
        return {"verdict": "RECONSIDER — run a larger governed-LLM trial",
                "rationale": ("Arm B was reproducible (D1) and made no false-"
                              "auto-clear (D2), and cost is below the stale "
                              "threshold (D3). The compiled bet must then win "
                              "on D1/D2 at larger N before locking architecture.")}
    return {"verdict": "PROCEED with compiled-then-run architecture",
            "rationale": ("Arm B passed D1/D2 but cost is not cheap (D3 = "
                          f"{d3.get('finding')}); compiled remains the default.")}


# --------------------------------------------------------------------------- #
def main() -> int:
    arm_a_only = "--arm-a" in sys.argv
    # runtag must be injected (determinism contract: no wall-clock in artifacts)
    runtag = "manual"
    model_key = "haiku"   # the cheap/fast steelman by default
    for a in sys.argv[1:]:
        if a.startswith("--runtag="):
            runtag = a.split("=", 1)[1]
        elif a.startswith("--model="):
            model_key = a.split("=", 1)[1]
    if model_key not in PRICING:
        print(f"  unknown --model={model_key}; choose from {list(PRICING)}")
        return 2
    pricing = PRICING[model_key]

    print("\n=== G3 BAKE-OFF — Compiled Engine (A) vs Governed Runtime-LLM (B) ===")
    print("    (decision rules D1/D2/D3 locked in PRE-REGISTRATION.md)\n")

    arm_a = run_arm_a()
    print(f"  Arm A (engine): evaluated {len(arm_a)} golden loans, "
          f"deterministic by construction.")

    arm_b_verdicts = None
    arm_b_tokens = None
    if not arm_a_only:
        try:
            print(f"  Arm B ({pricing['label']}, temp=0): {N_RUNS} runs/loan over "
                  f"{len(arm_a)} loans -> {N_RUNS * len(arm_a)} Bedrock calls ...")
            arm_b_verdicts, arm_b_tokens = run_arm_b(pricing["model_id"], N_RUNS)
            print("  Arm B: complete.")
        except Exception as exc:  # credentials / network / Bedrock access
            print(f"  Arm B: COULD NOT RUN ({type(exc).__name__}: {exc}).")
            print("         Re-run with AWS profile 'gordon-chan' reachable, "
                  "or use --arm-a for the engine-only sanity pass.")

    d1 = evaluate_d1(arm_b_verdicts) if arm_b_verdicts else {
        "passed": None, "note": "Arm B not run."}
    d2 = evaluate_d2(arm_a, arm_b_verdicts)
    d3 = evaluate_d3(arm_b_tokens, pricing)
    verdict = map_verdict(d1, d2, d3)

    # ---- console report ----
    print("\n--- D1 · DETERMINISM GATE ---")
    if arm_b_verdicts:
        print(f"  Arm B byte-identical across {N_RUNS} runs, every loan: "
              f"{'YES ✓' if d1['passed'] else 'NO ✗'}")
        for off in d1.get("offenders", []):
            print(f"    ✗ {off['loan_id']} flickered: {off['flicker']}")
    else:
        print("  (Arm B not run)")

    print("\n--- D2 · ACCURACY / SAFETY GATE (false-auto-clear) ---")
    a = d2["arm_a"]
    print(f"  Arm A: exact-match {a['exact_match']}/{a['checks_scored']} "
          f"({a['exact_match_rate']}), false-auto-clears={a['false_auto_clear_count']}")
    if d2["arm_b"]:
        b = d2["arm_b"]
        print(f"  Arm B: exact-match {b['exact_match']}/{b['checks_scored']} "
              f"({b['exact_match_rate']}), false-auto-clears={b['false_auto_clear_count']}")
        if b["false_auto_clears"]:
            print(f"    ⚠ Arm B false-auto-clears: {b['false_auto_clears']}")
    print(f"  gate: {'PASS ✓' if d2['passed'] else 'FAIL ✗'} — {d2['reason']}")
    print("  NOTE: accuracy is DIRECTIONAL on synthetic loans (pre-reg caveat).")

    print("\n--- D3 · COST TEST (extrapolated to 10,000 loans) ---")
    if d3.get("ran"):
        print(f"  Arm B tokens/loan: in={d3['avg_input_tokens_per_loan']} "
              f"out={d3['avg_output_tokens_per_loan']}")
        print(f"  10k-run cost  global rate : {d3['cost_10k_global_rate']}")
        print(f"  10k-run cost  regional(+10%): {d3['cost_10k_regional_rate']}  "
              f"<- the rate this profile pays")
        print(f"  Arm A cost: {d3['arm_a_cost']}")
        print(f"  finding: {d3['finding']}  (confirmed>"
              f"{d3['thresholds']['confirmed_above']}, stale<"
              f"{d3['thresholds']['stale_below']})")
    else:
        print(f"  {d3.get('note')}")

    print("\n=== VERDICT (locked mapping) ===")
    print(f"  {verdict['verdict']}")
    print(f"  {verdict['rationale']}\n")

    # ---- persist artifact ----
    artifact = {
        "experiment": "G3 bake-off",
        "runtag": runtag,
        "arm_b_model": pricing["label"],
        "n_runs": N_RUNS,
        "ruleset_sha256": demo_ruleset().sha256(),
        "arm_b_ran": arm_b_verdicts is not None,
        "D1_determinism": d1,
        "D2_accuracy": d2,
        "D3_cost": d3,
        "verdict": verdict,
        "caveats": [
            "Synthetic golden loans: accuracy DIRECTIONAL until Kayla's real, "
            "independent-path loans land (1-2 weeks out).",
            "Small N (~6 loans): decisive for determinism + real per-loan cost; "
            "not a population false-clear rate.",
            "One model (Haiku 4.5): the cheap/fast steelman; a larger model "
            "might pass D1/D2 but worsens D3.",
        ],
    }
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "artifacts")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"g3_bakeoff_{runtag}.json")
    with open(out_path, "w") as fh:
        json.dump(artifact, fh, indent=2, sort_keys=True)
    print(f"  artifact -> {out_path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
