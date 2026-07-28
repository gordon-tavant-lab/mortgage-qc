"""
Step 3 of the 002a compile-fidelity spike: runnability + constructed-label
scoring (FR-003).

Reuses the EXISTING deterministic engine (qc_engine.engine.run) directly and
applies the SAME ground-truth-by-construction philosophy p0/eval_synth already
uses (inject a known condition, check the engine's verdict matches) -- adapted
per-drafted-check rather than via eval_synth's pre-built archetype generator,
because each compiled rule names a field/threshold the generator has never seen
(there is no field catalog yet -- 001a/001b -- so the generator's fixed demo
fields cannot stand in for an arbitrary real workbook row).

This is the SAME scoring paradigm p0/eval_synth uses (construct a labeled loan,
run the engine, compare verdict to the constructed label), not eval.py's
score() function verbatim -- that function is hardwired to the 8 fixed demo
ruleset check IDs. Documented explicitly, per the constitution's honest-residual
principle: this is an adaptation, not a silent reuse claim.

For each compiled Check, build a synthetic PASS-case loan and a synthetic
FAIL/FLAG-case loan tailored to its kind, run the real engine, and check the
verdict matches the constructed label. A rule that errors (unknown predicate,
unsupported ratio, etc.) is scored as a runnability failure, not silently
dropped.

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys
from decimal import Decimal
from typing import Any, Dict, Optional, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from qc_engine.model import CanonicalLoan, SourceValue  # noqa: E402
from qc_engine.ruleset import Check, Ruleset  # noqa: E402
from qc_engine.engine import run  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def _check_from_draft(draft: Dict[str, Any]) -> Optional[Check]:
    c = draft.get("check")
    if not c:
        return None
    try:
        return Check(
            id=c.get("id", draft["row_id"]),
            name=c.get("name", ""),
            field_name=c["field_name"],
            kind=c["kind"],
            severity=c.get("severity", "CRITICAL"),
            phase=c.get("phase", ""),
            sources=c.get("sources", []),
            normalizer=c.get("normalizer", "identity"),
            tolerance=c.get("tolerance", "0"),
            predicate=c.get("predicate", ""),
            ratio=c.get("ratio", ""),
            threshold=c.get("threshold", ""),
            operator=c.get("operator", "<="),
            message_pass=c.get("message_pass", ""),
            message_fail=c.get("message_fail", ""),
        )
    except KeyError as e:
        raise ValueError(f"Malformed check draft, missing {e}")


def _run_one(chk: Check, loan: CanonicalLoan) -> str:
    ruleset = Ruleset(ruleset_id="spike-002a", version=1, checks=[chk])
    result = run(loan, ruleset)
    return result.results[0].status


def _score_predicate(chk: Check) -> Tuple[bool, bool, str]:
    """Returns (pass_case_ok, fail_case_ok, error)."""
    if chk.predicate == "is_true":
        pass_loan = CanonicalLoan(loan_id="pass", fields={
            chk.field_name: SourceValue(doc=True, doc_confidence=0.99)})
        fail_loan = CanonicalLoan(loan_id="fail", fields={
            chk.field_name: SourceValue(doc=False, doc_confidence=0.99)})
    elif chk.predicate == "is_present":
        pass_loan = CanonicalLoan(loan_id="pass", fields={
            chk.field_name: SourceValue(doc="present-value", doc_confidence=0.99)})
        # NOTE: doc=None short-circuits to NOT_APPLICABLE in the current engine
        # (engine.py's predicate branch returns before is_present ever runs) --
        # that is itself a spike finding (see RESULTS.md), not something this
        # test should paper over by avoiding it. Use "" (non-None, but empty)
        # so the fail case actually exercises is_present's own logic.
        fail_loan = CanonicalLoan(loan_id="fail", fields={
            chk.field_name: SourceValue(doc="", doc_confidence=0.99)})
    else:
        return False, False, f"unknown predicate '{chk.predicate}'"

    p_status = _run_one(chk, pass_loan)
    f_status = _run_one(chk, fail_loan)
    return (p_status == "PASS"), (f_status == "FAIL"), ""


def _score_ratio_threshold(chk: Check) -> Tuple[bool, bool, str]:
    thr = Decimal(chk.threshold) if chk.threshold else Decimal("0")
    op = chk.operator
    # Construct a passing value and a failing value straddling the threshold,
    # respecting the drafted operator's direction.
    if op in ("<=", "<"):
        pass_val, fail_val = thr - Decimal("5"), thr + Decimal("5")
    else:  # >=, >
        pass_val, fail_val = thr + Decimal("5"), thr - Decimal("5")
    # No positive-only clamp: Decimal math tolerates negative facts fine, and a
    # low/zero threshold (e.g. a credit-score-style floor forced into the ltv/
    # dti mechanism -- see RESULTS.md) needs both sides distinguishable even
    # when that pushes a "fact" negative. This isn't a realistic loan value;
    # it's a synthetic probe of the comparison operator's arithmetic only.

    def _loan_for(ratio_pct: Decimal, loan_id: str) -> CanonicalLoan:
        loan = CanonicalLoan(loan_id=loan_id)
        if chk.ratio == "ltv":
            # LTV% = loan_amount / property_value * 100 -> pick property_value=100
            loan.facts = {"property_value": "100.00",
                          "loan_amount": str(ratio_pct)}
        elif chk.ratio == "dti":
            loan.facts = {"monthly_income": "100.00",
                          "monthly_debts": str(ratio_pct)}
        else:
            raise ValueError(f"unknown ratio '{chk.ratio}'")
        return loan

    try:
        p_status = _run_one(chk, _loan_for(pass_val, "pass"))
        f_status = _run_one(chk, _loan_for(fail_val, "fail"))
    except ValueError as e:
        return False, False, str(e)
    return (p_status == "PASS"), (f_status == "FAIL"), ""


def _score_agree_categorical(chk: Check) -> Tuple[bool, bool, str]:
    pass_loan = CanonicalLoan(loan_id="pass", fields={
        chk.field_name: SourceValue(doc="VALUE_A", los="VALUE_A", doc_confidence=0.99)})
    fail_loan = CanonicalLoan(loan_id="fail", fields={
        chk.field_name: SourceValue(doc="VALUE_A", los="VALUE_B", doc_confidence=0.99)})
    p_status = _run_one(chk, pass_loan)
    f_status = _run_one(chk, fail_loan)
    return (p_status == "PASS"), (f_status == "FLAG"), ""


def _score_agree_numeric(chk: Check) -> Tuple[bool, bool, str]:
    tol = Decimal(chk.tolerance) if chk.tolerance else Decimal("0")
    pass_loan = CanonicalLoan(loan_id="pass", fields={
        chk.field_name: SourceValue(doc="100.00", los="100.00", doc_confidence=0.99)})
    fail_val = str(Decimal("100.00") + tol + Decimal("5"))
    fail_loan = CanonicalLoan(loan_id="fail", fields={
        chk.field_name: SourceValue(doc="100.00", los=fail_val, doc_confidence=0.99)})
    p_status = _run_one(chk, pass_loan)
    f_status = _run_one(chk, fail_loan)
    return (p_status == "PASS"), (f_status == "FLAG"), ""


SCORERS = {
    "predicate": _score_predicate,
    "ratio_threshold": _score_ratio_threshold,
    "agree_categorical": _score_agree_categorical,
    "agree_numeric": _score_agree_numeric,
}


def score_draft(draft: Dict[str, Any]) -> Dict[str, Any]:
    row_id = draft["row_id"]
    if draft.get("_parse_error"):
        return {"row_id": row_id, "runnable": False,
                "constructed_label_score": "fail",
                "error": f"LLM output did not parse: {draft['_parse_error']}"}
    try:
        chk = _check_from_draft(draft)
    except ValueError as e:
        return {"row_id": row_id, "runnable": False,
                "constructed_label_score": "fail", "error": str(e)}

    scorer = SCORERS.get(chk.kind)
    if scorer is None:
        return {"row_id": row_id, "runnable": False,
                "constructed_label_score": "fail",
                "error": f"unsupported kind '{chk.kind}'"}

    try:
        pass_ok, fail_ok, err = scorer(chk)
    except Exception as e:  # noqa: BLE001 -- record as a runnability failure
        return {"row_id": row_id, "runnable": False,
                "constructed_label_score": "fail", "error": str(e)}

    if err:
        return {"row_id": row_id, "runnable": False,
                "constructed_label_score": "fail", "error": err}

    exact_match = pass_ok and fail_ok
    return {
        "row_id": row_id,
        "runnable": True,
        "constructed_label_score": "pass" if exact_match else "fail",
        "pass_case_correct": pass_ok,
        "fail_case_correct": fail_ok,
        "error": "" if exact_match else "constructed pass/fail case mismatch",
    }


def main() -> int:
    with open(os.path.join(HERE, "artifacts", "compiled_drafts.json")) as fh:
        compiled = json.load(fh)

    scores = [score_draft(d) for d in compiled["drafts"]]
    n_runnable = sum(1 for s in scores if s["runnable"])
    n_pass = sum(1 for s in scores if s["constructed_label_score"] == "pass")

    out_path = os.path.join(HERE, "artifacts", "scored_drafts.json")
    with open(out_path, "w") as fh:
        json.dump({"scores": scores}, fh, indent=2, sort_keys=False)

    print(f"Runnable: {n_runnable}/{len(scores)}")
    print(f"Constructed-label PASS: {n_pass}/{len(scores)}")
    for s in scores:
        if s["constructed_label_score"] != "pass":
            print(f"  FAIL {s['row_id']}: {s.get('error', '')}")
    print(f"\n-> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
