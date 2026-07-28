"""
build_loan_profiles.py -- closes the "extracted loan ontology" gap: derived
loan facts were computed in-memory (run_011's `_panel()`) and never
persisted. This script writes one profile artifact per loan under
`storage/loan_profiles/v1/`, with the derivation made explicit and
provenance recorded, instead of re-deriving it silently on every run.

The one derivation this project has today -- `gift_funds_used` from the real
extracted `doc_present_gift_letter` fact -- is documented verbatim in
`p0/compile_runs/run_011_retail_only_002g/build_and_run.py`'s `_panel()`:
"true"/"false" -> the same "true"/"false". No new content is invented here;
this only persists what run_011 already computes in memory, with provenance.

If a loan's source fact is missing or not a recognized "true"/"false" value,
NO derived fact is written for it -- the profile records the gap honestly
under `underivable` instead of guessing (this project's grounding rule:
an honest "can't derive" beats an invented value, every time).

Run: python3 p0/qc_engine/build_loan_profiles.py
Python 3.9 compatible. Deterministic -- no network, no LLM calls.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List

_HERE = os.path.dirname(os.path.abspath(__file__))
_P0 = os.path.dirname(_HERE)
_REPO_ROOT = os.path.dirname(_P0)
_FROM_DOCS = os.path.join(_P0, "fixtures", "from_docs")
for _p in (_P0, _FROM_DOCS):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fixture_loader import load_canonical_loan  # noqa: E402
from qc_engine.model import CanonicalLoan  # noqa: E402

LOAN_NUMBERS = ("01", "02", "03", "04", "05")
FIXTURE_DIR = os.path.join(_P0, "fixtures", "from_docs")
OUT_DIR = os.path.join(_REPO_ROOT, "storage", "loan_profiles", "v1")
PROFILE_VERSION = 1

# The single derivation rule this project currently has (run_011 `_panel()`):
# doc_present_gift_letter "true"/"false" -> gift_funds_used, same value.
SOURCE_FACT = "doc_present_gift_letter"
DERIVED_FACT = "gift_funds_used"
VALID_SOURCE_VALUES = ("true", "false")
DERIVATION_RULE = (
    "gift letter present in file <=> gift funds used (fixture-set invariant; "
    "extraction contract should eventually deliver gift_funds_used directly - "
    "002e/002g interface note)"
)


def derive_gift_funds_used(loan: CanonicalLoan) -> Dict[str, Any]:
    """Compute the derived_facts / underivable payload for one loan, straight
    from its real extracted facts. Never guesses: if the source fact is
    missing or not a recognized boolean-string value, the derived fact is
    omitted and an `underivable` entry is returned instead.

    Returns a dict shaped like:
      {"derived_facts": {...}} or {"underivable": {...}} (never both, never
      neither -- exactly one key is present).
    """
    source_value = loan.facts.get(SOURCE_FACT)

    if source_value not in VALID_SOURCE_VALUES:
        reason = (
            "source fact '{}' is missing from loan.facts".format(SOURCE_FACT)
            if source_value is None
            else "source fact '{}' has unrecognized value {!r} (expected 'true' or 'false')".format(
                SOURCE_FACT, source_value
            )
        )
        return {
            "underivable": {
                DERIVED_FACT: {
                    "reason": reason,
                    "attempted_from": {"fact": SOURCE_FACT, "value": source_value},
                }
            }
        }

    return {
        "derived_facts": {
            DERIVED_FACT: {
                "value": source_value,
                "derived_from": {"fact": SOURCE_FACT, "value": source_value},
                "derivation_rule": DERIVATION_RULE,
                "derivation_kind": "computed",
            }
        }
    }


def build_profile(loan: CanonicalLoan) -> Dict[str, Any]:
    profile: Dict[str, Any] = {
        "loan_id": loan.loan_id,
        "profile_version": PROFILE_VERSION,
    }
    profile.update(derive_gift_funds_used(loan))
    return profile


def build_all_profiles() -> List[str]:
    """Loads each of the 5 real document-extracted loan fixtures, derives its
    profile, and writes it to storage/loan_profiles/v1/loan_<NN>.json.
    Returns the list of paths written (deterministic order)."""
    os.makedirs(OUT_DIR, exist_ok=True)
    written = []
    for n in LOAN_NUMBERS:
        fixture_path = os.path.join(FIXTURE_DIR, "loan_{}.json".format(n))
        if not os.path.isfile(fixture_path):
            raise SystemExit(
                "missing fixture {} -- refusing to write a loan profile not "
                "derived from real data".format(fixture_path)
            )
        loan = load_canonical_loan(fixture_path)
        profile = build_profile(loan)
        out_path = os.path.join(OUT_DIR, "loan_{}.json".format(n))
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2, sort_keys=True)
            f.write("\n")
        written.append(out_path)
    return written


def main() -> None:
    written = build_all_profiles()
    print("wrote {} loan profile(s) to {}".format(len(written), OUT_DIR))
    for path in written:
        with open(path, "r", encoding="utf-8") as f:
            profile = json.load(f)
        loan_id = profile["loan_id"]
        if "derived_facts" in profile:
            value = profile["derived_facts"][DERIVED_FACT]["value"]
            print("  {} ({}): {} = {}".format(
                os.path.basename(path), loan_id, DERIVED_FACT, value))
        else:
            reason = profile["underivable"][DERIVED_FACT]["reason"]
            print("  {} ({}): UNDERIVABLE -- {}".format(
                os.path.basename(path), loan_id, reason))


if __name__ == "__main__":
    main()
