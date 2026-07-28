"""
build_loan_profiles_v3.py -- adds two more loan-side derivations on top of
v2's 3 (gift_funds_used, loan_transaction_type, appraisal_in_file), writing
storage/loan_profiles/v3/ (v2 stays untouched -- one file per version, same
precedent that made build_loan_profiles_v2.py a NEW script rather than an
edit to build_loan_profiles.py: a prior version's generator behavior is
pinned by committed tests and artifacts).

specs/010b-derive-remaining-gating-dimensions adds:

  - `occupancy_type` <- `occupancy_1003` (the 1003's own occupancy question).
    A small, explicit, literal text->token map (OCCUPANCY_MAP) -- never a
    fuzzy/substring match. All 5 real loan fixtures resolve `owner_occupied`
    (a real, disclosed data-diversity limit: no real fixture carries
    "Second Home" or "Investment Property" text today -- those two paths are
    proven only against constructed CanonicalLoan fixtures in
    test_loan_profiles_v3.py, mirroring the same "untested against a real
    fixture, but verified not to silently misfire" posture program_gating.py
    already disclosed for SONYMA).

  - `loan_program` <- per-program citable presence markers
    (`fha_case_number_1003`, `va_lgy_case_number`, `usda_gus_id`), reusing
    program_gating.py's own `_PREFIX_TO_PROGRAM` token set verbatim. Honestly
    `underivable` -- never guessed from the uncited `loan.loan_type` string --
    in two distinct cases, found by direct inspection of all 5 real fixtures:
      (a) loan_01: `loan_type_cd == "Conventional"`, cited, but no GSE-
          specific citable field -- "Conventional" alone cannot distinguish
          Fannie Mae vs. Freddie Mac (the same ambiguity program_gating.py's
          own AMBIGUOUS sentinel already exists to surface at the
          SQL-clause layer).
      (b) loan_04: zero program-identifying field of any kind in `fields` --
          a different failure mode ("no citable signal found") from (a)'s
          ("signal found but ambiguous"); the two reasons are deliberately
          distinct strings, never conflated.

Run: python3 p0/qc_engine/build_loan_profiles_v3.py
Python 3.9 compatible. Deterministic -- no network, no LLM calls (FR-009).
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
from qc_engine.build_loan_profiles_v2 import (  # noqa: E402 (v2, reused unchanged)
    derive_appraisal_in_file,
    derive_loan_transaction_type,
)
from qc_engine.model import CanonicalLoan  # noqa: E402

LOAN_NUMBERS = ("01", "02", "03", "04", "05")
FIXTURE_DIR = os.path.join(_P0, "fixtures", "from_docs")
PROFILE_VERSION = 3
OUT_DIR = os.path.join(_REPO_ROOT, "storage", "loan_profiles", "v{}".format(PROFILE_VERSION))


def _underivable(fact_name: str, reason: str, attempted_from: Dict[str, Any]) -> Dict[str, Any]:
    return {"underivable": {fact_name: {"reason": reason, "attempted_from": attempted_from}}}


def _derived(fact_name: str, value: str, derived_from: Dict[str, Any], rule: str) -> Dict[str, Any]:
    return {"derived_facts": {fact_name: {
        "value": value, "derived_from": derived_from,
        "derivation_rule": rule, "derivation_kind": "computed",
    }}}


# --- occupancy_type -----------------------------------------------------------

# Literal 1003 occupancy-question text -> the SAME canonical_value tokens
# storage/fact_vocabulary's occupancy_type fact already uses (v7.json).
# Deliberately conservative: any text not listed here is honestly
# underivable, never fuzzy/substring-matched (mirrors
# derive_loan_transaction_type's existing LOAN_PURPOSE_MAP discipline,
# build_loan_profiles_v2.py). "Second Home" and "Investment Property" are
# the real ULAD/URLA occupancy checkbox options -- no real fixture carries
# either text today (all 5 read a "Primary Residence" variant), so those two
# paths are proven only against constructed fixtures (spec.md Edge Cases).
OCCUPANCY_MAP = {
    "Primary Residence": "owner_occupied",
    "Primary Residence (First-Time Homebuyer)": "owner_occupied",
    "Second Home": "second_home",
    "Investment Property": "investment",
}
OCCUPANCY_FIELD = "occupancy_1003"


def derive_occupancy_type(loan: CanonicalLoan) -> Dict[str, Any]:
    fact_name = "occupancy_type"
    raw = loan.get(OCCUPANCY_FIELD).doc
    if raw is None:
        return _underivable(fact_name, "source field '{}' is missing from loan.fields".format(
            OCCUPANCY_FIELD), {"field": OCCUPANCY_FIELD, "value": None})
    canonical = OCCUPANCY_MAP.get(raw)
    if canonical is None:
        return _underivable(
            fact_name,
            "source field '{}' has value {!r}, not in the recognized 1003-text->canonical-token "
            "map -- refusing to guess".format(OCCUPANCY_FIELD, raw),
            {"field": OCCUPANCY_FIELD, "value": raw})
    return _derived(
        fact_name, canonical, {"field": OCCUPANCY_FIELD, "value": raw},
        "1003's own occupancy question text maps literally to the fact vocabulary's canonical "
        "token (storage/fact_vocabulary/v7.json question_bindings) -- conservative mapping, "
        "never inferring occupancy beyond what the document states")


# --- loan_program --------------------------------------------------------------

# Per-program citable presence markers -> program_gating.py's own
# _PREFIX_TO_PROGRAM token set, reused verbatim (010a). Checked in a fixed
# order (FHA, then VA, then USDA) -- none of the 5 real fixtures carries
# more than one of these simultaneously, so ordering is not load-bearing on
# real data today, but a deterministic, explicit order is still the correct
# discipline (Non-Negotiable #1: same loan -> same result, every time).
_PROGRAM_PRESENCE_FIELDS = (
    ("fha_case_number_1003", "FHA"),
    ("va_lgy_case_number", "VA"),
    ("usda_gus_id", "USDA"),
)
_LOAN_TYPE_CD_FIELD = "loan_type_cd"

# spec 015 Issue 1 (2026-07-28): a fourth signal, consulted after the FHA/
# VA/USDA presence markers but before the "Conventional" ambiguity fallback
# below. The final 1003's own "Loan Program" line already states the GSE
# outright for Fannie/Freddie Conventional loans (e.g. loan 01: "Conventional
# — Fannie Mae"; loan 04: "Freddie Mac Conventional Cash-Out Refi") -- no
# FHA/VA/USDA presence field exists for these loans (they aren't government
# programs), so without this branch they fall through to the honestly-
# underivable "Conventional alone can't distinguish Fannie/Freddie" and
# "no program-identifying field at all" cases below, even though the source
# document actually names the GSE. A literal substring check against the
# doc's own text -- not an inference beyond what the 1003 states (CLAUDE.md's
# "grounding adds context, never new rule content" rule) -- for loans 02/03/05
# neither substring is present, so they fall through to the unchanged
# existing paths exactly as before this fix.
_LOAN_PROGRAM_1003_FIELD = "loan_program_1003"


def derive_loan_program(loan: CanonicalLoan) -> Dict[str, Any]:
    fact_name = "loan_program"
    for field_name, program in _PROGRAM_PRESENCE_FIELDS:
        raw = loan.get(field_name).doc
        if raw is not None:
            return _derived(
                fact_name, program, {"field": field_name, "value": raw},
                "presence of a program-specific citable field ({}) unambiguously identifies "
                "the loan program -- program_gating.py's own _PREFIX_TO_PROGRAM token set, "
                "reused verbatim (010a)".format(field_name))

    loan_program_1003 = loan.get(_LOAN_PROGRAM_1003_FIELD).doc
    if loan_program_1003 is not None:
        if "Fannie Mae" in loan_program_1003:
            return _derived(
                fact_name, "Fannie Mae",
                {"field": _LOAN_PROGRAM_1003_FIELD, "value": loan_program_1003},
                "the final 1003's own 'Loan Program' line names the GSE directly ({!r} contains "
                "'Fannie Mae') -- a literal substring read off the source document's own text, "
                "not an inference beyond what the 1003 states (spec 015 Issue 1)".format(
                    loan_program_1003))
        if "Freddie Mac" in loan_program_1003:
            return _derived(
                fact_name, "Freddie Mac",
                {"field": _LOAN_PROGRAM_1003_FIELD, "value": loan_program_1003},
                "the final 1003's own 'Loan Program' line names the GSE directly ({!r} contains "
                "'Freddie Mac') -- a literal substring read off the source document's own text, "
                "not an inference beyond what the 1003 states (spec 015 Issue 1)".format(
                    loan_program_1003))

    loan_type_cd = loan.get(_LOAN_TYPE_CD_FIELD).doc
    attempted_from = {
        "fields_checked": [f for f, _ in _PROGRAM_PRESENCE_FIELDS]
        + [_LOAN_PROGRAM_1003_FIELD, _LOAN_TYPE_CD_FIELD],
        "loan_type_cd": loan_type_cd,
    }
    if loan_type_cd == "Conventional":
        return _underivable(
            fact_name,
            "loan_type_cd reads 'Conventional' (cited), but no GSE-specific citable field "
            "(fha_case_number_1003 / va_lgy_case_number / usda_gus_id) is present -- "
            "'Conventional' alone cannot distinguish Fannie Mae vs. Freddie Mac (the same "
            "ambiguity program_gating.py's own AMBIGUOUS sentinel already surfaces at the "
            "SQL-clause layer) -- refusing to guess in either direction",
            attempted_from)
    return _underivable(
        fact_name,
        "no program-identifying field of any kind is present in loan.fields (checked {}) -- "
        "the loan's top-level loan_type label, if any, is uncited fixture-authoring metadata, "
        "not a citable doc-extracted signal -- refusing to guess".format(
            attempted_from["fields_checked"]),
        attempted_from)


# --- income_type_used_for_qualification -----------------------------------

# Presence-based, same shape as derive_loan_program: prefer the strongest
# direct signal (a citable self-employment marker), fall back to the next
# strongest (a VOE-sourced field -- Fannie Mae Form 1005 / Freddie Mac Form 90
# exists specifically to verify traditional salaried employment; self-employed
# borrowers don't get one), and refuse to guess when neither is present
# (specs/015-loan-data-capture-and-gating-fix FR-007). Verified directly
# against all 5 real fixtures: only loan 04 carries years_self_employed_1003
# (its 1003's own "Years Self-Employed" line); only loan 01 carries a VOE doc
# (voe_employer_name populated); loans 02/03/05 carry neither -- honestly
# underivable for those three, not forced to a guess.
#
# Output values MUST match the canonical income-type vocabulary the
# comprehensive ruleset's own applies_if conditions already use verbatim
# (result/rules/comprehensive_e2e_v6_ruleset.json: 'self_employment',
# 'wage_earner', 'military', 'rental', ... -- confirmed by direct inspection,
# 2026-07-28) -- NOT a fresh, human-readable label. engine.py's
# _normalize_for_applies_if lowercases and strips but does not otherwise
# reformat, so "Self-Employed"/"W-2" would silently fail to match
# "self_employment"/"wage_earner" and every self-employment-gated check
# would stay ungated (spec 015 FR-007's whole point, undone).
_SELF_EMPLOYED_FIELD = "years_self_employed_1003"
_VOE_SIGNAL_FIELD = "voe_employer_name"
_SELF_EMPLOYMENT_TOKEN = "self_employment"
_WAGE_EARNER_TOKEN = "wage_earner"


def derive_income_type(loan: CanonicalLoan) -> Dict[str, Any]:
    fact_name = "income_type_used_for_qualification"
    self_employed_raw = loan.get(_SELF_EMPLOYED_FIELD).doc
    if self_employed_raw is not None:
        return _derived(
            fact_name, _SELF_EMPLOYMENT_TOKEN,
            {"field": _SELF_EMPLOYED_FIELD, "value": self_employed_raw},
            "presence of a citable self-employment marker ({}, the 1003's own 'Years "
            "Self-Employed' line) unambiguously identifies self-employment income as the "
            "basis for qualification -- value is the canonical '{}' token the compiled "
            "ruleset's own applies_if conditions already use".format(
                _SELF_EMPLOYED_FIELD, _SELF_EMPLOYMENT_TOKEN))

    voe_raw = loan.get(_VOE_SIGNAL_FIELD).doc
    if voe_raw is not None:
        return _derived(
            fact_name, _WAGE_EARNER_TOKEN,
            {"field": _VOE_SIGNAL_FIELD, "value": voe_raw},
            "presence of a VOE-sourced field ({}) indicates a written Verification of "
            "Employment exists for this borrower -- a document (Fannie Mae Form 1005 / "
            "Freddie Mac Form 90) that specifically verifies traditional W-2/salaried "
            "employment; self-employed borrowers are documented via the P&L/4506-C route "
            "instead, not a VOE -- value is the canonical '{}' token the compiled ruleset's "
            "own applies_if conditions already use".format(_VOE_SIGNAL_FIELD, _WAGE_EARNER_TOKEN))

    attempted_from = {"fields_checked": [_SELF_EMPLOYED_FIELD, _VOE_SIGNAL_FIELD]}
    return _underivable(
        fact_name,
        "neither a self-employment marker ({}) nor a VOE-sourced field ({}) is present in "
        "loan.fields -- refusing to guess whether qualifying income is W-2 or "
        "self-employed".format(_SELF_EMPLOYED_FIELD, _VOE_SIGNAL_FIELD),
        attempted_from)


DERIVATIONS = (
    derive_gift_funds_used,
    derive_loan_transaction_type,
    derive_appraisal_in_file,
    derive_occupancy_type,
    derive_loan_program,
    derive_income_type,
)


def build_profile(loan: CanonicalLoan) -> Dict[str, Any]:
    """Same per-fact both/either shape v2 introduced: a v3 profile can carry
    BOTH derived_facts and underivable simultaneously, per-fact."""
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
