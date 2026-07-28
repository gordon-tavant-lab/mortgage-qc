"""
Step 6 of the 002a compile-fidelity spike: apply the LOCKED pre-registered
decision rule (pre-registration.md, locked 2026-06-30) to Kayla's completed
interpretation-fidelity review.

Parses artifacts/sme_review_package.md for filled-in verdict/correction/
reviewer_note fields (the `_[...]` placeholders from build_review_package.py
must be replaced with real values). Refuses to produce a verdict if any row is
still unreviewed -- an honest partial run reports what's missing, it does not
guess or average over gaps.

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import re
import sys
from typing import Any, Dict, List

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from qc_engine.ruleset import _edit_distance  # noqa: E402 -- reused, not reimplemented (FR-005)

HERE = os.path.dirname(os.path.abspath(__file__))
VERDICT_VALUES = {"correct", "incorrect", "ambiguous"}

# Locked thresholds (must match pre-registration.md -- do not edit here without
# re-locking there first).
D1_INTERPRETATION_FIDELITY_THRESHOLD = 0.70


def parse_review_package(path: str) -> List[Dict[str, Any]]:
    with open(path) as fh:
        text = fh.read()
    rows = []
    for block in text.split("## ")[1:]:
        row_id = block.split()[0]
        def _field(name: str) -> str:
            m = re.search(rf"\*\*{name}\*\*:\s*(.+)", block)
            return m.group(1).strip() if m else ""
        verdict = _field("verdict").strip("_[] ").lower()
        correction = _field("correction").strip("_[] ")
        note = _field("reviewer_note").strip("_[] ")
        restatement_m = re.search(r"\*\*plain_english_restatement\*\*[^:]*:\s*(.+)", block)
        restatement = restatement_m.group(1).strip() if restatement_m else ""
        rows.append({
            "row_id": row_id, "verdict": verdict, "correction": correction,
            "reviewer_note": note, "restatement": restatement,
        })
    return rows


def main() -> int:
    pkg_path = os.path.join(HERE, "artifacts", "sme_review_package.md")
    rows = parse_review_package(pkg_path)

    unreviewed = [r["row_id"] for r in rows if r["verdict"] not in VERDICT_VALUES]
    if unreviewed:
        print(f"INCOMPLETE: {len(unreviewed)}/{len(rows)} rows have no valid verdict yet.")
        print(f"Still pending: {unreviewed}")
        print("\nNo PROCEED/RECONSIDER/KILL verdict can be produced until every row "
              "has a verdict in {correct, incorrect, ambiguous}. Have Kayla complete "
              f"{pkg_path} and re-run this script.")
        return 1

    n = len(rows)
    n_correct = sum(1 for r in rows if r["verdict"] == "correct")
    interpretation_fidelity_rate = n_correct / n
    interpretation_error_rate = 1 - interpretation_fidelity_rate

    NO_CORRECTION_SENTINELS = {"", "(none)", "none", "n/a", "na"}
    corrected = [r for r in rows if r["verdict"] != "correct"
                 and r["correction"].strip().lower() not in NO_CORRECTION_SENTINELS]
    edit_distances = [_edit_distance(r["restatement"], r["correction"]) for r in corrected]
    mean_edit_distance = (sum(edit_distances) / len(edit_distances)) if edit_distances else 0.0
    zero_edit_batch = len(corrected) == 0 and n_correct < n  # incorrect/ambiguous but no correction given

    # D1 (primary gate)
    if interpretation_fidelity_rate < D1_INTERPRETATION_FIDELITY_THRESHOLD:
        verdict = "KILL"
        reason = (f"D1 fails: interpretation-fidelity {interpretation_fidelity_rate:.0%} "
                  f"< {D1_INTERPRETATION_FIDELITY_THRESHOLD:.0%} threshold.")
    else:
        # D3 -- qualitative correction-cost check; no hard numeric threshold was
        # pre-registered for "rewriting from scratch" (pre-registration.md states
        # this explicitly), so this stays a flagged judgment call, not an
        # auto-computed downgrade, unless reviewer_notes make it unambiguous.
        high_correction_flag = any(
            "rewrit" in r["reviewer_note"].lower() or "from scratch" in r["reviewer_note"].lower()
            for r in rows if r["reviewer_note"]
        )
        if high_correction_flag:
            verdict = "RECONSIDER"
            reason = (f"D1 passes ({interpretation_fidelity_rate:.0%}) but a reviewer_note "
                      f"flags substantial rewriting -- D3 downgrades to RECONSIDER.")
        else:
            verdict = "PROCEED"
            reason = (f"D1 passes ({interpretation_fidelity_rate:.0%}) and no reviewer_note "
                      f"flags substantial correction cost.")

    with open(os.path.join(HERE, "artifacts", "sampled_rows.json")) as fh:
        archetype_distribution = json.load(fh)["archetype_distribution"]

    finding = {
        "sample_archetype_distribution": archetype_distribution,  # SC-006
        "interpretation_error_rate": round(interpretation_error_rate, 4),
        "interpretation_fidelity_rate": round(interpretation_fidelity_rate, 4),
        "n_correct": n_correct, "n_total": n,
        "mean_edit_distance": round(mean_edit_distance, 2),
        "zero_edit_batch_flag": zero_edit_batch,
        "verdict": verdict,
        "reason": reason,
    }
    out_path = os.path.join(HERE, "artifacts", "spike_finding.json")
    with open(out_path, "w") as fh:
        json.dump(finding, fh, indent=2)

    print(f"Interpretation-fidelity: {n_correct}/{n} = {interpretation_fidelity_rate:.0%}")
    print(f"Mean edit-distance (on corrected rows): {mean_edit_distance:.2f}")
    print(f"\n=== VERDICT: {verdict} ===")
    print(reason)
    print(f"\n-> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
