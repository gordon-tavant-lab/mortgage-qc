"""
build_loan_profiles_v5.py -- adds 5 more derivations on top of v4's 7
(occupancy_type, loan_program, income_type_used_for_qualification,
gift_funds_used, loan_transaction_type, appraisal_in_file,
doc_present_* passthrough), writing storage/loan_profiles/v5/ (v1/v2/v3/v4
stay untouched -- one file per version, same precedent that made each prior
version a NEW script rather than an edit to the one before it: a prior
version's generator behavior is pinned by committed tests and artifacts).

Track A2 (2026-07-29): an investigation into the 718 checks still
NEEDS_REVIEW on loan 01 (Fannie Mae + UNTAGGED scoped, out of the 1,076-check
comprehensive ruleset) after Track F found 271 of them are blocked not by
their own missing data, but by an EXISTING `applies_if` precondition on some
OTHER field that was never derived/populated in loan.fields at all. Of those
271, 5 precondition fields account for the large majority and are plausibly
derivable from data already extracted, with zero new document extraction:
`appraisal_waiver_type` (90 checks), `borrower_income_type` (45),
`du_validation_service_components_received` (45),
`credit_report_present_for_all_applicants` (41), `closing_funds_asset_type`
(29). Full writeup: output/TRACK-A2-PRECONDITION-DERIVATIONS-2026-07-29.md.

Each of the 5 below was independently re-verified against the real fixtures
(p0/fixtures/from_docs/loan_0{1-5}.json) before being written, not copied
blind from the investigation -- see each function's own docstring for what
was confirmed and any correction made:

  - `appraisal_waiver_type` <- presence of a named, licensed appraiser field
    (`appraiser_name` / `fha_appraiser_name` / `va_appraiser_name`) ->
    'full_appraisal'. The 'value_acceptance_plus_property_data' branch is
    never exercised against real fixture data today (no waiver/PDC document
    pattern exists in any of the 5 fixtures) -- same disclosed-but-accepted
    gap as v3's OCCUPANCY_MAP untested second_home/investment tokens.
    Loan 05 stays underivable (no appraiser-name field extracted there).

  - `borrower_income_type` <- reuses v3's derive_income_type's own two
    presence signals (self-employment marker -> self_employment; VOE
    employer name -> wage_earner) plus one new signal specific to the
    richer vocabulary (`va_branch_of_service` present -> military). Loans
    02/05 stay underivable -- neither carries any of the three signals.

  - `du_validation_service_components_received` -- NOT derived for any loan.
    No DU/AUS/relief-related field exists anywhere across all 5 fixtures'
    `fields` (confirmed by direct grep of every field key); the only related
    datum, `doc_present_du_uw_findings_report`, reads "false" for all 5 loans
    and -- per this project's own derive_appraisal_in_file precedent -- an
    absence-only signal in a narrow, defect-targeted fixture is never turned
    into a derived negative claim. No function is added for this field; it
    remains a disclosed, real extraction-coverage gap.

  - `credit_report_present_for_all_applicants` <- applicant count from
    presence of `co_borrower_name_1003` (present => 2 applicants, absent =>
    1 -- no co_borrower_2 field exists anywhere in the catalog), then "true"
    only if every applicant slot has a citable credit-report-sourced score
    (`borrower_credit_score` alone for 1 applicant; both
    `borrower_credit_score` AND `coborrower_credit_score` for 2). Absence is
    NEVER turned into "false" (mirrors derive_appraisal_in_file's discipline
    exactly) -- loans 02/03/04/05 stay underivable, not defaulted false.

  - `closing_funds_asset_type` <- collects every `asset_NN_account_type`
    field present, maps each through an explicit, literal ASSET_TYPE_MAP
    (sourced from storage/fact_vocabulary/v8.json's own question_bindings
    for this fact), and derives a single value only if exactly one distinct
    canonical token results. Loan 01 itself discloses TWO distinct asset
    types (checking_savings AND retirement) with no field saying which
    specifically funds closing -- so loan 01, like all 5 loans, comes out
    underivable under this conservative design. This is the one field in
    the batch where the conservative design yields zero clearances on loan
    01 -- disclosed here, not hidden.

Run: python3 p0/qc_engine/build_loan_profiles_v5.py
Python 3.9 compatible. Deterministic -- no network, no LLM calls (FR-009).
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
_P0 = os.path.dirname(_HERE)
_REPO_ROOT = os.path.dirname(_P0)
_FROM_DOCS = os.path.join(_P0, "fixtures", "from_docs")
for _p in (_P0, _FROM_DOCS):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fixture_loader import load_canonical_loan  # noqa: E402
from qc_engine.build_loan_profiles_v4 import DERIVATIONS as V4_DERIVATIONS  # noqa: E402
from qc_engine.model import CanonicalLoan  # noqa: E402

LOAN_NUMBERS = ("01", "02", "03", "04", "05")
FIXTURE_DIR = os.path.join(_P0, "fixtures", "from_docs")
PROFILE_VERSION = 5
OUT_DIR = os.path.join(_REPO_ROOT, "storage", "loan_profiles", "v{}".format(PROFILE_VERSION))


def _underivable(fact_name: str, reason: str, attempted_from: Dict[str, Any]) -> Dict[str, Any]:
    return {"underivable": {fact_name: {"reason": reason, "attempted_from": attempted_from}}}


def _derived(fact_name: str, value: str, derived_from: Dict[str, Any], rule: str) -> Dict[str, Any]:
    return {"derived_facts": {fact_name: {
        "value": value, "derived_from": derived_from,
        "derivation_rule": rule, "derivation_kind": "computed",
    }}}


# --- appraisal_waiver_type -----------------------------------------------------

# A real named-and-licensed "Appraiser" line on an Appraisal Summary/URAR is
# direct, citable evidence a licensed appraiser performed a traditional
# inspection-based appraisal, as opposed to a value-acceptance waiver (no
# appraisal at all) or a value-acceptance-plus-property-data hybrid (a
# non-appraiser property-data collector visits, never a licensed "Appraiser"
# of record). Checked in a fixed order across all 3 program-specific
# appraiser-name fields the catalog defines -- confirmed by direct
# inspection, no real fixture carries more than one of these simultaneously,
# so ordering is not load-bearing on real data today.
#
# The 'value_acceptance_plus_property_data' token is never actually
# producible from current fixture data (confirmed: no waiver/value_acceptance/
# PDR/PIW document-presence pattern exists anywhere in build_fixtures.py's
# _DOCUMENT_PRESENCE_SUBSTRINGS, and none of the 5 fixtures' fields carry any
# such marker) -- that branch stays unexercised and honestly disclosed, the
# same posture v3's OCCUPANCY_MAP already discloses for its own never-hit
# second_home/investment tokens.
#
# Never inferred from a bare doc_present_*_appraisal fact alone -- that fact
# only proves an appraisal-related document exists, not which of the two
# enum values applies (a document-presence fact cannot distinguish a full
# appraisal from a hybrid property-data-collection visit).
_APPRAISER_NAME_FIELDS = ("appraiser_name", "fha_appraiser_name", "va_appraiser_name")
_FULL_APPRAISAL_TOKEN = "full_appraisal"


def derive_appraisal_waiver_type(loan: CanonicalLoan) -> Dict[str, Any]:
    """Verified directly against all 5 real fixtures (2026-07-29): loan 01
    has appraiser_name, loan 02 has fha_appraiser_name, loan 03 has
    va_appraiser_name, loan 04 has appraiser_name -- all real named/licensed
    appraiser signatures. Loan 05 has none of the three (only
    usda_ratio_waiver_required exists among appraisal-adjacent fields) --
    stays underivable, per this project's derive_appraisal_in_file precedent
    ("absence in a narrow, defect-targeted fixture does not mean no
    appraisal exists in the real file")."""
    fact_name = "appraisal_waiver_type"
    for field_name in _APPRAISER_NAME_FIELDS:
        raw = loan.get(field_name).doc
        if raw is not None:
            return _derived(
                fact_name, _FULL_APPRAISAL_TOKEN, {"field": field_name, "value": raw},
                "presence of a named, licensed appraiser field ({}) is direct, citable "
                "evidence a licensed appraiser performed a traditional inspection-based "
                "appraisal (as opposed to a value-acceptance waiver with no appraisal at "
                "all, or a value-acceptance-plus-property-data hybrid where a non-appraiser "
                "property-data collector visits instead) -- value is the canonical '{}' "
                "token the compiled ruleset's own applies_if conditions already use".format(
                    field_name, _FULL_APPRAISAL_TOKEN))
    return _underivable(
        fact_name,
        "none of {} is present in loan.fields -- a bare doc_present_*_appraisal fact alone "
        "(if present) only proves an appraisal-related document exists, not which of "
        "'full_appraisal' or 'value_acceptance_plus_property_data' applies, so it is not "
        "used as a substitute signal here; absence in a narrow, defect-targeted fixture "
        "does not mean no appraisal exists in the real file".format(
            list(_APPRAISER_NAME_FIELDS)),
        {"fields_checked": list(_APPRAISER_NAME_FIELDS)})


# --- borrower_income_type -------------------------------------------------------

# Reuses v3's derive_income_type's own two presence signals verbatim (a
# self-employment marker and a VOE-sourced employer field), and adds one new
# signal specific to this field's richer 10-token vocabulary: a populated
# va_branch_of_service field (extant only via the VA Certificate of
# Eligibility, whose own field label is literally "Branch of Service") ->
# 'military'. Verified directly against all 5 real fixtures (2026-07-29):
# loan 01 has voe_employer_name -> wage_earner; loan 03 has
# va_branch_of_service -> military (corroborated, not contradicted, by
# employer_name_1003='U.S. Army — 82nd Airborne' in the same fixture);
# loan 04 has years_self_employed_1003 -> self_employment; loans 02/05 have
# none of the three signals -- stay underivable, refusing to guess among the
# remaining 7 tokens (rental, trust, alimony_child_support_maintenance,
# overtime_bonus_commission, social_security_retirement_disability,
# part_time_second_job_seasonal_unemployment, other) since none of the 5
# real fixtures carries any citable signal for them. Order matters only in
# that a self-employment marker is checked first (strongest, most specific
# signal), matching v3's own precedence.
_SELF_EMPLOYED_FIELD = "years_self_employed_1003"
_VOE_SIGNAL_FIELD = "voe_employer_name"
_VA_BRANCH_FIELD = "va_branch_of_service"
_SELF_EMPLOYMENT_TOKEN = "self_employment"
_WAGE_EARNER_TOKEN = "wage_earner"
_MILITARY_TOKEN = "military"


def derive_borrower_income_type(loan: CanonicalLoan) -> Dict[str, Any]:
    fact_name = "borrower_income_type"
    self_employed_raw = loan.get(_SELF_EMPLOYED_FIELD).doc
    if self_employed_raw is not None:
        return _derived(
            fact_name, _SELF_EMPLOYMENT_TOKEN,
            {"field": _SELF_EMPLOYED_FIELD, "value": self_employed_raw},
            "presence of a citable self-employment marker ({}, the 1003's own 'Years "
            "Self-Employed' line) unambiguously identifies self-employment income -- "
            "value is the canonical '{}' token the compiled ruleset's own applies_if "
            "conditions already use".format(_SELF_EMPLOYED_FIELD, _SELF_EMPLOYMENT_TOKEN))

    voe_raw = loan.get(_VOE_SIGNAL_FIELD).doc
    if voe_raw is not None:
        return _derived(
            fact_name, _WAGE_EARNER_TOKEN, {"field": _VOE_SIGNAL_FIELD, "value": voe_raw},
            "presence of a VOE-sourced field ({}) indicates a written Verification of "
            "Employment exists for this borrower -- a document (Fannie Mae Form 1005 / "
            "Freddie Mac Form 90) that specifically verifies traditional W-2/salaried "
            "employment -- value is the canonical '{}' token the compiled ruleset's own "
            "applies_if conditions already use".format(_VOE_SIGNAL_FIELD, _WAGE_EARNER_TOKEN))

    va_branch_raw = loan.get(_VA_BRANCH_FIELD).doc
    if va_branch_raw is not None:
        return _derived(
            fact_name, _MILITARY_TOKEN, {"field": _VA_BRANCH_FIELD, "value": va_branch_raw},
            "presence of a VA Certificate of Eligibility-sourced field ({}, field_label "
            "'Branch of Service') unambiguously identifies military income -- value is "
            "the canonical '{}' token the compiled ruleset's own applies_if conditions "
            "already use".format(_VA_BRANCH_FIELD, _MILITARY_TOKEN))

    attempted_from = {"fields_checked": [_SELF_EMPLOYED_FIELD, _VOE_SIGNAL_FIELD, _VA_BRANCH_FIELD]}
    return _underivable(
        fact_name,
        "none of a self-employment marker ({}), a VOE-sourced field ({}), or a VA "
        "branch-of-service field ({}) is present in loan.fields -- refusing to guess "
        "among the remaining income-type tokens (rental, trust, "
        "alimony_child_support_maintenance, overtime_bonus_commission, "
        "social_security_retirement_disability, "
        "part_time_second_job_seasonal_unemployment, other) with no citable signal for "
        "any of them".format(_SELF_EMPLOYED_FIELD, _VOE_SIGNAL_FIELD, _VA_BRANCH_FIELD),
        attempted_from)


# --- du_validation_service_components_received ----------------------------------
#
# No derivation is added for this field. Independently re-confirmed
# (2026-07-29) by grepping every field key across all 5 real fixtures for
# anything DU/AUS/relief/validation-related: zero hits. The only related
# datum anywhere is the fact `doc_present_du_uw_findings_report`, which reads
# "false" for all 5 loans -- per this project's own established precedent in
# derive_appraisal_in_file ("NEVER derived false from absence ... absence in
# a narrow, defect-targeted fixture does not mean no appraisal exists in the
# real file"), a "false" presence fact cannot be used to manufacture a
# substantive negative value here either. Separately, even a confirmed
# absence would at most support "this loan wasn't processed through DU
# Validation Service at all" -- a different claim from "zero relief
# components were received" -- and the fact vocabulary defines no token for
# either "not applicable" or "none received" (storage/fact_vocabulary/v8.json
# lists only 5 positive relief tokens), so there is no vocabulary-sanctioned
# value to assign even if the absence were confirmed real. Tracked as a real
# extraction-coverage gap, not attempted here.


# --- credit_report_present_for_all_applicants -----------------------------------
#
# Applicant count from presence of co_borrower_name_1003 (no co_borrower_2
# field exists anywhere in the catalog -- confirmed by grep -- so this field
# models exactly two shapes: 1 or 2 applicants). "true" only when EVERY
# applicant slot has a citable credit-report-sourced score; absence is NEVER
# treated as a negative "false" signal, mirroring derive_appraisal_in_file's
# explicit discipline exactly, since these loans' sparse field counts
# (56/43/111/29 vs loan 01's 217) are the identical narrow-fixture pattern
# that discipline was written for.
#
# Verified directly against all 5 real fixtures (2026-07-29): loan 01 has
# co_borrower_name_1003 (2 applicants) AND both borrower_credit_score (742)
# and coborrower_credit_score (758), both from the SAME Tri-Merge Credit
# Report Summary document -- unambiguous positive evidence. Loans 02-05 have
# no co_borrower_name_1003 (1 applicant each) and none carries
# borrower_credit_score at all -- stay underivable.
_COBORROWER_NAME_FIELD = "co_borrower_name_1003"
_BORROWER_SCORE_FIELD = "borrower_credit_score"
_COBORROWER_SCORE_FIELD = "coborrower_credit_score"


def derive_credit_report_present_for_all_applicants(loan: CanonicalLoan) -> Dict[str, Any]:
    fact_name = "credit_report_present_for_all_applicants"
    coborrower_name = loan.get(_COBORROWER_NAME_FIELD).doc
    two_applicants = coborrower_name is not None
    borrower_score = loan.get(_BORROWER_SCORE_FIELD).doc
    coborrower_score = loan.get(_COBORROWER_SCORE_FIELD).doc

    if not two_applicants:
        if borrower_score is not None:
            return _derived(
                fact_name, "true",
                {"applicants": 1, "field": _BORROWER_SCORE_FIELD, "value": borrower_score},
                "single-applicant loan (no {} present); a citable credit-report-sourced "
                "score ({}) exists for the sole applicant -- 'true' satisfies this field's "
                "'in false|true' applies_if gate, letting gated checks proceed to their "
                "own real pass/fail logic".format(_COBORROWER_NAME_FIELD, _BORROWER_SCORE_FIELD))
        return _underivable(
            fact_name,
            "single-applicant loan (no {} present), but no {} field is present either -- "
            "absence is NEVER treated as a negative 'false' signal (mirrors "
            "derive_appraisal_in_file's discipline: a narrow, defect-targeted fixture not "
            "extracting this field does not mean no credit report exists in the real "
            "file)".format(_COBORROWER_NAME_FIELD, _BORROWER_SCORE_FIELD),
            {"applicants": 1, "fields_checked": [_BORROWER_SCORE_FIELD]})

    if borrower_score is not None and coborrower_score is not None:
        return _derived(
            fact_name, "true",
            {"applicants": 2, "co_borrower_name": coborrower_name,
             "borrower_credit_score": borrower_score, "coborrower_credit_score": coborrower_score},
            "two-applicant loan ({} present); citable credit-report-sourced scores exist "
            "for BOTH applicants ({} and {}), the same tri-merge document scoring both "
            "named roles -- 'true' satisfies this field's 'in false|true' applies_if gate, "
            "letting gated checks proceed to their own real pass/fail logic".format(
                _COBORROWER_NAME_FIELD, _BORROWER_SCORE_FIELD, _COBORROWER_SCORE_FIELD))
    return _underivable(
        fact_name,
        "two-applicant loan ({} present), but at least one of {} / {} is missing -- "
        "refusing to derive 'true' without a citable score for every applicant, and "
        "never deriving 'false' from absence (narrow-fixture precedent)".format(
            _COBORROWER_NAME_FIELD, _BORROWER_SCORE_FIELD, _COBORROWER_SCORE_FIELD),
        {"applicants": 2, "co_borrower_name": coborrower_name,
         "borrower_credit_score": borrower_score, "coborrower_credit_score": coborrower_score})


# --- closing_funds_asset_type ----------------------------------------------------

# Literal 1003 asset-account-type text -> the SAME canonical_value tokens
# storage/fact_vocabulary/v8.json's closing_funds_asset_type question_bindings
# already use (question_key 570606). Deliberately conservative: any text not
# listed here is honestly underivable, never fuzzy/substring-matched (same
# discipline as v3's OCCUPANCY_MAP). "Gift" is deliberately NOT mapped to any
# token -- it is absent from the vocabulary's 16-token answer set, and
# forcing it to 'other' would be an interpretive relabeling not grounded in
# any document's literal text.
ASSET_TYPE_MAP = {
    "Checking": "checking_savings",
    "Savings": "checking_savings",
    "401(k)": "retirement",
    "IRA": "retirement",
    "403(b)": "retirement",
}
_ASSET_ACCOUNT_TYPE_SUFFIX = "_account_type"


def _asset_account_type_fields(loan: CanonicalLoan) -> List[str]:
    """Every asset_NN_account_type field present in loan.fields, sorted for
    determinism. loan.fields is a plain dict of SourceValue -- iterating its
    keys (not a fixed NN range) is required since the NN range/count differs
    per loan and no catalog enumerates them by a shared prefix pattern other
    than the literal suffix itself."""
    return sorted(
        name for name in loan.fields
        if name.startswith("asset_") and name.endswith(_ASSET_ACCOUNT_TYPE_SUFFIX)
    )


def derive_closing_funds_asset_type(loan: CanonicalLoan) -> Dict[str, Any]:
    """Verified directly against all 5 real fixtures (2026-07-29): loan 01
    discloses TWO distinct canonical asset types (asset_01/asset_02 ->
    checking_savings, asset_03 '401(k)' -> retirement) with no field saying
    which specifically funds closing -- ambiguous, not single-valued, so
    loan 01 itself comes out underivable under this design (mirrors
    derive_loan_program's "multiple candidate signals, no field says which
    one" precedent). Loans 02-05 have zero asset_NN_account_type fields at
    all -- also underivable. Every one of the 5 real fixtures is underivable
    for this field; disclosed here, not hidden."""
    fact_name = "closing_funds_asset_type"
    asset_fields = _asset_account_type_fields(loan)
    if not asset_fields:
        return _underivable(
            fact_name,
            "no asset_NN_account_type field is present in loan.fields -- no source-of-funds "
            "signal of any kind exists for this loan",
            {"fields_checked": []})

    resolved: Dict[str, Optional[str]] = {}
    unrecognized: Dict[str, str] = {}
    for field_name in asset_fields:
        raw = loan.get(field_name).doc
        canonical = ASSET_TYPE_MAP.get(raw)
        resolved[field_name] = canonical
        if canonical is None:
            unrecognized[field_name] = raw

    distinct_tokens = sorted({v for v in resolved.values() if v is not None})
    if len(distinct_tokens) == 1 and not unrecognized:
        only_field = [f for f, v in resolved.items() if v == distinct_tokens[0]][0]
        return _derived(
            fact_name, distinct_tokens[0],
            {"fields": {f: loan.get(f).doc for f in asset_fields}},
            "every present asset_NN_account_type field maps to the SAME canonical token "
            "({}) via the fact vocabulary's own literal text map -- unambiguous single "
            "closing-funds asset source".format(distinct_tokens[0]))

    return _underivable(
        fact_name,
        "asset_NN_account_type fields present ({}) resolve to {} distinct canonical "
        "token(s){} -- no field designates which specific asset source funds closing "
        "costs, so this is honestly ambiguous, not single-valued (mirrors "
        "derive_loan_program's 'multiple candidate signals, no field says which one' "
        "precedent); unrecognized text is never fuzzy-matched or guessed".format(
            asset_fields, len(distinct_tokens),
            " (plus {} unrecognized text value(s))".format(len(unrecognized)) if unrecognized else ""),
        {"fields": {f: loan.get(f).doc for f in asset_fields}, "resolved": resolved})


DERIVATIONS = tuple(V4_DERIVATIONS) + (
    derive_appraisal_waiver_type,
    derive_borrower_income_type,
    derive_credit_report_present_for_all_applicants,
    derive_closing_funds_asset_type,
)


def build_profile(loan: CanonicalLoan) -> Dict[str, Any]:
    """Same per-fact both/either shape v2-v4 introduced: a v5 profile can
    carry BOTH derived_facts and underivable simultaneously, per-fact."""
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
        doc_presence_true = [k for k, v in derived.items()
                              if k.startswith("doc_present_") and v["value"] == "true"]
        non_doc_presence = {k: v["value"] for k, v in sorted(derived.items())
                             if not k.startswith("doc_present_")}
        parts = ["{}={}".format(k, v) for k, v in non_doc_presence.items()]
        parts += ["{}=UNDERIVABLE".format(k) for k in sorted(underivable)]
        parts.append("doc_present_* true-for-this-loan: {}".format(sorted(doc_presence_true) or "none"))
        print("  {} ({}): {}".format(os.path.basename(path), loan_id, ", ".join(parts)))


if __name__ == "__main__":
    main()
