"""
build_loan_profiles_v2.py -- adds two more loan-side derivations on top of
v1's `gift_funds_used`, writing storage/loan_profiles/v2/ (v1 stays untouched
-- one file per version, 002c precedent; this is a NEW script rather than an
edit to build_loan_profiles.py for the same reason promote_naming_proposals.py
was a new script rather than an edit to build_seed_fact_vocabulary.py: v1's
generator behavior is pinned by committed tests and artifacts).

2026-07-27, after Gordon asked for a genuine (not just compile-time) 5-loan
end-to-end run against the expanded 16-fact vocabulary: an explicit
feasibility check against all 5 real loan fixtures found these are the ONLY
two additional facts (of 16) with a direct, already-extracted signal to
derive from -- not an inferential guess:

  - `loan_transaction_type` <- `loan_purpose_general_1003` (the 1003 field IS
    the answer to this question, present on every loan; a small, disclosed,
    literal string->token map, never a partial/fuzzy match)
  - `appraisal_in_file` <- true if ANY of `doc_present_va_appraisal`,
    `doc_present_usda_appraisal`, or a populated `appraised_value` field is
    present. NEVER derived false from absence: 4 of 5 loan fixtures are
    deliberately narrow (built to extract only the fields their own planted
    defects need -- loan_05 has 28 total fields vs loan_01's 216), so a
    missing field means "this fixture wasn't built to extract it," not "this
    document doesn't exist." Confirmed empirically (checked `k in fields`,
    not `fields.get(k)`, for every candidate field across all 5 loans)
    before writing any derivation logic -- loan_02 (FHA) has no positive
    signal at all and is honestly `underivable`, not defaulted to false.

The other 13 facts in the vocabulary (income type, credit report presence,
DU components, LEP, etc.) were evaluated and found to have NO direct signal
in these fixtures -- deriving them would mean inventing an inference rule
from adjacent-but-not-equivalent raw fields (e.g. an asset account's type is
NOT the same claim as "which asset type funded closing"), the same category
of mistake the citation-mismatch fix (fact_vocabulary v5) just corrected.
Not attempted here; tracked as a real extraction-coverage gap (Non-Negotiable
#2 -- Touchless's contract, not built in this engine).

Run: python3 p0/qc_engine/build_loan_profiles_v2.py
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
from qc_engine.build_loan_profiles import derive_gift_funds_used  # noqa: E402 (v1, reused unchanged)
from qc_engine.model import CanonicalLoan  # noqa: E402

LOAN_NUMBERS = ("01", "02", "03", "04", "05")
FIXTURE_DIR = os.path.join(_P0, "fixtures", "from_docs")
PROFILE_VERSION = 2
OUT_DIR = os.path.join(_REPO_ROOT, "storage", "loan_profiles", "v{}".format(PROFILE_VERSION))


def _underivable(fact_name: str, reason: str, attempted_from: Dict[str, Any]) -> Dict[str, Any]:
    return {"underivable": {fact_name: {"reason": reason, "attempted_from": attempted_from}}}


def _derived(fact_name: str, value: str, derived_from: Dict[str, Any], rule: str) -> Dict[str, Any]:
    return {"derived_facts": {fact_name: {
        "value": value, "derived_from": derived_from,
        "derivation_rule": rule, "derivation_kind": "computed",
    }}}


# --- loan_transaction_type ---------------------------------------------------

# Literal 1003 loan-purpose text -> the SAME canonical_value tokens
# storage/fact_vocabulary's loan_transaction_type fact already uses (v6.json).
# Deliberately conservative: "Refinance -- Rate/Term" maps to the generic
# "refinance" bucket (571086's answer set), NOT the more specific
# "limited_cash_out_refinance" (571083) -- industry usage treats "rate/term"
# as synonymous with "no cash out", but that's an additional inferential
# claim the 1003 field text doesn't itself assert. Under-mapping is the safe
# failure mode (same discipline as draft_fact_names_llm.py's naming pass).
# Any 1003 text not listed here is honestly underivable, never fuzzy-matched.
LOAN_PURPOSE_MAP = {
    "Purchase": "purchase",
    "Refinance — Rate/Term": "refinance",
    "Refinance - Rate/Term": "refinance",  # ASCII-hyphen variant, same claim
}
LOAN_PURPOSE_FIELD = "loan_purpose_general_1003"


def derive_loan_transaction_type(loan: CanonicalLoan) -> Dict[str, Any]:
    fact_name = "loan_transaction_type"
    raw = loan.get(LOAN_PURPOSE_FIELD).doc
    if raw is None:
        return _underivable(fact_name, "source field '{}' is missing from loan.fields".format(
            LOAN_PURPOSE_FIELD), {"field": LOAN_PURPOSE_FIELD, "value": None})
    canonical = LOAN_PURPOSE_MAP.get(raw)
    if canonical is None:
        return _underivable(
            fact_name,
            "source field '{}' has value {!r}, not in the recognized 1003-text->canonical-token "
            "map -- refusing to guess".format(LOAN_PURPOSE_FIELD, raw),
            {"field": LOAN_PURPOSE_FIELD, "value": raw})
    return _derived(
        fact_name, canonical, {"field": LOAN_PURPOSE_FIELD, "value": raw},
        "1003's own loan-purpose text maps literally to the fact vocabulary's canonical "
        "token (storage/fact_vocabulary/v6.json question_bindings) -- conservative mapping, "
        "never inferring cash-out status beyond what the document states")


# --- appraisal_in_file --------------------------------------------------------

APPRAISAL_PRESENCE_FACTS = ("doc_present_va_appraisal", "doc_present_usda_appraisal")
APPRAISAL_VALUE_FIELD = "appraised_value"


def derive_appraisal_in_file(loan: CanonicalLoan) -> Dict[str, Any]:
    """True only from a POSITIVE signal (a program-specific appraisal-presence
    fact reading 'true', or a populated appraised_value field) -- a 'false'
    reading on doc_present_va_appraisal/doc_present_usda_appraisal is NOT
    treated as a negative signal, since that fact is a generic default on
    every non-VA/non-USDA loan, not a real "no appraisal" assertion. Absence
    of all three signals (loan_02/FHA in this fixture set) is honestly
    underivable, never defaulted to false."""
    fact_name = "appraisal_in_file"
    positive_facts = [f for f in APPRAISAL_PRESENCE_FACTS if loan.facts.get(f) == "true"]
    appraised_value = loan.get(APPRAISAL_VALUE_FIELD).doc
    if positive_facts or appraised_value is not None:
        evidence = {"facts_true": positive_facts, "appraised_value": appraised_value}
        return _derived(
            fact_name, "true", evidence,
            "a positive appraisal-presence signal exists (a program-specific "
            "doc_present_*_appraisal fact reading true, or a populated appraised_value "
            "field) -- never derived false from absence, since 4 of 5 fixtures only "
            "extract fields their own planted defects need")
    return _underivable(
        fact_name,
        "no positive appraisal signal found (checked {} and {}); absence in a narrow, "
        "defect-targeted fixture does not mean no appraisal exists in the real "
        "file".format(APPRAISAL_PRESENCE_FACTS, APPRAISAL_VALUE_FIELD),
        {"facts_checked": list(APPRAISAL_PRESENCE_FACTS), "appraised_value": None})


DERIVATIONS = (derive_gift_funds_used, derive_loan_transaction_type, derive_appraisal_in_file)


def build_profile(loan: CanonicalLoan) -> Dict[str, Any]:
    """Unlike v1's build_profile (exactly-one-fact, either/or), v2 profiles
    can carry BOTH derived_facts and underivable simultaneously, per-fact --
    e.g. loan_02 derives gift_funds_used and loan_transaction_type but is
    underivable for appraisal_in_file."""
    profile: Dict[str, Any] = {"loan_id": loan.loan_id, "profile_version": PROFILE_VERSION}
    derived_facts: Dict[str, Any] = {}
    underivable: Dict[str, Any] = {}
    for derive_fn in DERIVATIONS:
        result = derive_fn(loan)
        derived_facts.update(result.get("derived_facts", {}))
        underivable.update(result.get("underivable", {}))
    if derived_facts:
        profile["derived_facts"] = derived_facts
    if underivable:
        profile["underivable"] = underivable
    return profile


def build_all_profiles() -> List[str]:
    os.makedirs(OUT_DIR, exist_ok=True)
    written = []
    for n in LOAN_NUMBERS:
        fixture_path = os.path.join(FIXTURE_DIR, "loan_{}.json".format(n))
        if not os.path.isfile(fixture_path):
            raise SystemExit(
                "missing fixture {} -- refusing to write a loan profile not "
                "derived from real data".format(fixture_path))
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
        derived = profile.get("derived_facts", {})
        underivable = profile.get("underivable", {})
        parts = ["{}={}".format(k, v["value"]) for k, v in sorted(derived.items())]
        parts += ["{}=UNDERIVABLE".format(k) for k in sorted(underivable)]
        print("  {} ({}): {}".format(os.path.basename(path), loan_id, ", ".join(parts)))


if __name__ == "__main__":
    main()
