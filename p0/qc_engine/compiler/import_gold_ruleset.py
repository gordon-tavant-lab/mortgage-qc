"""
Gold rule set -> p0 Ruleset converter (bake-off, 2026-07-31).

Deterministic, NO LLM calls -- this is a pure data-shape conversion, consistent
with this project's "LLM at compile time only, never twice" discipline (see
CLAUDE.md's LLM Guardrails section: an LLM already ran once, at gold-set
*compile* time, to assign check_type/citations/applicability to each of these
266 cards -- this script does not re-derive any of that judgment, it only
re-shapes the already-compiled result into `p0/qc_engine/ruleset.py`'s
dataclasses).

Input:  storage/rules/gold/data/rules_compiled.json (266 cards, ~1105
        defect_options -- see storage/rules/gold/README.md SS3 and
        storage/rules/gold/schema/rule.schema.json for the ground-truth shape)
Output: a `Ruleset` (p0/qc_engine/ruleset.py's existing dataclasses -- no new
        shapes defined here) plus a sidecar mapping file joining each
        generated Check back to its gold (card_id, exception_code) origin.

Context: this is Pipeline B's half of the p0-vs-src_shacl_pilot bake-off --
see /Users/gordonchan/.claude/plans/1-no-no-this-iridescent-brooks.md for the
full experiment design and the mapping table this module implements.

------------------------------------------------------------------------------
MAPPING DECISIONS (read this before trusting any converted Check)
------------------------------------------------------------------------------

One gold "defect option" (an entry in card['defect_options']) becomes one
`Check`, except where noted. `Check.question_code` carries the parent
`card_id` (e.g. "PC::O-FNM-15320"); `Check.id` is `"{card_id}::{exception_code}"`
(de-duplicated with a numeric suffix on the rare within-card collision --
verified 2 of 266 cards repeat an exception_code across sibling
defect_options). `Check.message_fail` is always the gold `finding.description`
VERBATIM -- this project's established rule (see AMQ-verbatim-message
convention): never paraphrase the workbook's exception text.

check_type -> Check.kind:

  doc_presence / doc_completeness
      -> Check(kind="predicate", predicate="is_present", field_name=<placeholder>).
      AMENDED 2026-07-31 (see output/BAKEOFF-P0-VS-SRC-GOLD-TOUCHLESS-2026-07-
      31.md): the loan fixture's `documents[]`-derived inventory (62 real
      entries, previously discarded by touchless_adapter.py) is now used for
      a small, individually hand-verified allowlist -- CURATED_DOC_MATCHES
      below, same 5 entries as the src/shacl_pilot side's
      CURATED_DOC_MATCHES in ruleset_to_shacl.py, same discipline (a naive
      keyword sweep over all 253 doc_presence descriptions produced false
      matches -- verified, not attempted here). For those 5, field_name
      points at a real `doc_present_<slug>` boolean the adapter now
      populates. Every other doc_presence/doc_completeness card still gets
      the placeholder field_name (derived deterministically from the
      exception text) that no fixture populates -- honestly resolves FAIL
      (is_present treats an absent field as "provably not there", per
      engine.py's documented 015-Issue-2 semantics), an expected, symmetric
      limitation, not a bug in this converter.

  threshold_eligibility
      -> Check(kind="ratio_threshold", ratio="field_value", ...). field_name
      is matched to one of the ~4 relevant real fields this loan's fixture
      populates (ltv, dti_ratio, housing_ratio, credit_score_1003) by keyword
      search over finding.description; otherwise a placeholder. Threshold and
      operator are parsed from the description text ONLY when a single,
      unambiguous numeric bound is stated next to the matched keyword and a
      directional verb (exceed(s|ed)/over/above/greater than/more than for an
      upper bound -> PASS operator "<="; below/less than/under/fell below for
      a lower bound -> PASS operator ">="). Deliberately excluded from
      auto-parsing: "did not meet"/"not met"/"insufficient" -- these phrases
      are directionally AMBIGUOUS on their own ("the MAXIMUM ratio was not
      met" means the value is too HIGH; "the MINIMUM score was not met" means
      the value is too LOW; same three words, opposite meaning) and an early
      version of this parser got exactly this wrong on a real card
      (O-FNM-54328, "the maximum LTV ... ratio of 95% was not met") before
      being restricted to unambiguous verbs only. Where no numeric bound can
      be safely parsed, `threshold="UNSPECIFIED"` -- engine.py's existing,
      established honesty guard (same one agree_numeric/agree_doc_numeric use
      for an unstated tolerance): resolves NEEDS_REVIEW, never a fabricated
      number, never a crash. mismo_loan_amount was deliberately EXCLUDED from
      the known-field keyword list: most "loan amount" mentions in this
      corpus are a denominator inside an unrelated fee-percentage rule (e.g.
      "financing concessions ... 2% of the loan amount"), not a threshold ON
      the loan amount field itself -- mapping those would silently compare
      the wrong quantity (a fee percentage) against the raw loan-amount
      field. A placeholder (safe, honest abstention) beats that.

  computation
      -> converted ONLY when the description's PRIMARY subject is clearly an
      LTV or DTI (re)calculation (contains "was/were not calculated
      correctly/appropriately", "not recalculated", "not included in the ...
      calculation", or a direct "DTI ... exceed/increase" statement) --
      Check(kind="ratio_threshold", ratio="ltv"/"dti", field_name="ltv"/
      "dti_ratio", threshold=<parsed as above, else "UNSPECIFIED">). Cards
      where LTV/DTI is only INCIDENTAL CONTEXT for a different subject (e.g.
      O-FNM-50329 "In a HomeReady Mortgage with an LTV over 80%, the
      borrower's minimum CONTRIBUTION AMOUNT was not met" -- the defect is
      about the contribution amount, not the LTV) are explicitly excluded via
      a small hand-reviewed exclusion set (see _LTV_DTI_INCIDENTAL_CONTEXT
      below, 3 exception_codes, hand-checked against the real card text) and
      logged unsupported with reason "computation_incidental_ltv_dti_context"
      rather than silently miscompiled as an LTV/DTI check.

      IMPORTANT ENGINE-BEHAVIOR CAVEAT (a real deviation worth flagging, not
      silently absorbed): ratio="ltv"/"dti" reads `loan.facts["loan_amount"]`/
      `["property_value"]` / `["monthly_debts"]`/`["monthly_income"]` (see
      engine.py's `_eval_check`, ratio_threshold branch) -- NOT the
      pre-computed `ltv`/`dti_ratio` fields this experiment's touchless
      fixture actually carries. `p0/qc_engine/adapters/touchless_adapter.py`
      (already built, not touched by this script) does not populate those
      four facts, only the already-computed ltv/dti_ratio field values, so
      EVERY computation-kind LTV/DTI Check this converter emits will resolve
      NOT_APPLICABLE ("LTV/DTI facts not present for this loan") on this
      loan, regardless of whether a threshold was parsed. This was a
      deliberate choice to follow the task's literal instruction (map
      computation-kind LTV/DTI cards to ratio="ltv"/"dti", the facts-based
      path) rather than silently substituting ratio="field_value" against the
      pre-computed field (which threshold_eligibility uses and which WOULD
      produce a real PASS/FAIL on this loan) -- see the run summary printed
      by this script's __main__ block, and the final report, for the actual
      observed effect. This is flagged as a documented judgment call, not
      hidden inside the mapping.

      Any other computation subject (fees, sweat equity, insurance
      deductibles, reserves, ARM index math, points-and-fees caps, etc.) is
      NOT converted -- logged unsupported, matching src/shacl_pilot's
      symmetric treatment per the bake-off plan (neither engine has these
      formulas built; building throwaway infra for one side would not change
      which engine looks stronger, since neither has it).

  cross_doc_consistency
      -> Check(kind="agree_categorical") or "agree_numeric" (by a keyword
      heuristic over the description: $/amount/ratio/percent/score/rate
      implies numeric, else categorical), field_name=<placeholder, since this
      loan's fixture has none of the 5 entity-family record types
      cross_doc_consistency checks actually need>. tolerance left at the
      Check dataclass default ("0") rather than "UNSPECIFIED" for the numeric
      case: since the placeholder field is never populated on this loan
      either way, the doc-vs-system both-None branch fires first and resolves
      NOT_APPLICABLE (the semantically correct "no data" verdict) rather than
      NEEDS_REVIEW's "we don't know the tolerance" (a different, less
      accurate claim given we genuinely have no data to compare, not merely
      an unstated tolerance).

  scripted_review
      -> Check(kind="predicate", predicate="is_true", field_name=<a checklist
      fact name deliberately never set in any loan fixture>). Per engine.py's
      existing, unmodified predicate/is_true branch, a None doc value on
      is_true resolves NEEDS_REVIEW/APPLICABILITY_UNKNOWN (confirmed by
      reading engine.py before relying on it, as instructed) -- no engine
      change needed.

  routing_context
      -> not a Check; skipped (this gold set carries zero defect_options
      under routing_context cards, confirmed empirically -- consistent with
      the taxonomy's "raises zero findings itself" definition).

  date_window, list_screening, reverification
      -> NOT converted at all. Logged unsupported, symmetric with
      src/shacl_pilot's treatment of the same three types per the plan.

applicability.always -> Check.applies_if = None (unconditional).

applicability.all_of -> each condition becomes one applies_if entry
(AND-combined, matching gold's own semantics exactly).

applicability.any_of -> gold's OR is translated to p0's AND-only applies_if
grammar as a SINGLE condition using the "in" operator with the any_of values
pipe-joined, PROVIDED every condition in the any_of block shares the same
field (verified: 4 of the 5 any_of cards in this data set do). The one
exception, PC::O-FNM-15437, ORs across TWO different fields (Loans.LoanType
and Loans.PropertyType) -- p0's applies_if has no way to express a cross-field
OR (each condition targets exactly one field, and the list is AND-only), so
that one card's any_of gate is DROPPED (only its all_of condition is kept),
documented explicitly in gold_to_check_mapping.json's
"any_of_dropped_heterogeneous_fields" flag and in the run summary. This is a
one-directional widening (the check will fire on more loans than gold
intends) -- flagged loudly rather than silently approximated, per this
project's guardrail discipline of never letting an abstention/approximation
pass as a full result.

Field-name vocabulary for applicability conditions (Loans.QC_Policy,
Loans.LoanPurposeType, Loans.PropertyType, Loans.Underwriting_Type,
Loans.LoanType, Loans.AddressState) is used VERBATIM as Check.applies_if
field_name -- these are exactly the keys
`p0/qc_engine/adapters/touchless_adapter.py` already emits under.

gold's condition "value" is real JSON (list or scalar) in this file (verified
by direct inspection, not the Python-list-repr STRING format the task brief
flagged as a possible hazard) -- `ast.literal_eval` is still applied
defensively if a string starting with "[" is ever encountered, so this
converter does not regress if a future re-export changes that.

Python 3.9 compatible.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import sys
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
_P0 = os.path.dirname(os.path.dirname(_HERE))
_REPO_ROOT = os.path.dirname(_P0)
if _P0 not in sys.path:
    sys.path.insert(0, _P0)

from qc_engine.ruleset import Check, Ruleset  # noqa: E402

GOLD_RULES_PATH = os.path.join(
    _REPO_ROOT, "storage", "rules", "gold", "data", "rules_compiled.json")
DEMO_EXCLUSIONS_PATH = os.path.join(
    _REPO_ROOT, "storage", "rules", "gold", "data", "demo_exclusions.json")
AUTOPASS_PATH = os.path.join(
    _REPO_ROOT, "storage", "rules", "gold", "data", "autopass_no_system_access.json")
AUTOPASS_SENTINEL_FIELD = "_demo_autopass_sentinel_true"
SCENARIO_APPLICABILITY_PATH = os.path.join(
    _REPO_ROOT, "storage", "rules", "gold", "data",
    "scenario_applicability_loan12607601215.json")
SCENARIO_GATE_SENTINEL_FIELD = "_demo_scenario_gate_always_false"
DOC_DECIDABILITY_PATH = os.path.join(
    _REPO_ROOT, "storage", "rules", "gold", "data", "doc_decidability_classification.json")
RUN_DIR = os.path.join(_P0, "compile_runs", "bakeoff_gold_touchless_2026-07-31")
TOUCHLESS_FIXTURE_PATH = os.path.join(RUN_DIR, "touchless_loan_fixture.json")
MAPPING_OUT_PATH = os.path.join(RUN_DIR, "gold_to_check_mapping.json")
RESULTS_OUT_PATH = os.path.join(RUN_DIR, "p0_results.json")

RULESET_ID = "gold-bakeoff-2026-07-31"
RULESET_VERSION = 1

# --- check_type dispositions ------------------------------------------------
NOT_CONVERTED_TYPES = {"date_window", "list_screening", "reverification"}
SKIPPED_TYPES = {"routing_context"}  # zero defect_options, nothing to do

GOLD_SEVERITY_MAP = {
    "Critical": "CRITICAL",
    "Critical-Pending SI": "CRITICAL",
    "Major": "WARNING",
    "Minor": "INFO",
    "Note": "INFO",
}

# Hand-verified, individually reviewed (card_id, exception_code) -> the real
# `doc_present_<slug>` field name p0/qc_engine/adapters/touchless_adapter.py
# now populates from this loan's real documents[] inventory. Mirrors
# src/shacl_pilot/ruleset_to_shacl.py's CURATED_DOC_MATCHES exactly (same 5
# checks, same underlying Touchless documentType, same verification -- see
# that file's comment for why each one is safe: every description is
# fundamentally an ABSENCE check, not a completeness/quality check, and each
# was read individually against this loan's real 62-document inventory, not
# derived from a keyword sweep (which produced false matches on this same
# 253-card set -- verified before choosing this approach).
CURATED_DOC_MATCHES = {
    ("PC::O-FNM-15336", "O-FNM-00234"): "doc_present_gift_letter",
    ("PC::O-FNM-14152", "O-FNM-58076"): "doc_present_credit_report",
    ("PC::O-FNM-15436", "FAMCO-FNM-00825"): "doc_present_hazard_insurance",
    ("PC::PropFlip", "FlipGuide-1"): "doc_present_title_commitment",
    ("PC::O-FNM-15438", "O-FNM-00533"): "doc_present_flood_hazard_determination",
    # 3 additions from the 2026-07-31 NO_DATA root-cause pass: every uncurated
    # doc check was classified by a guardrailed config-time review (closed
    # vocabulary, verbatim-evidence requirement); of 9 PURE_PRESENCE candidates
    # only these 3 survived hand-verification as bare-absence defects whose
    # named document maps unambiguously to a Touchless documentType. Rejected
    # at the same review, deliberately: "appraisal"->Form 1004 (would false-FAIL
    # loans appraised on 1073/1025), Escrow Waiver O-FNM-50230 (conjunctive
    # defect -- absence alone is not the defect on escrowed loans), and
    # credit-report-per-applicant O-FNM-00179 (needs doc-level borrower tags,
    # null in the real payload).
    ("PC::ICPL", "ICPL"): "doc_present_closing_protection_letter",
    ("PC::O-BP-14663", "O-BP-54652"): "doc_present_borrowers_authorization",
    ("PC::O-FNM-15436", "HOICoverage"): "doc_present_hazard_insurance",
}

# --- known real fields this loan's touchless fixture actually populates ----
# (see p0/qc_engine/adapters/touchless_adapter.py)
THRESHOLD_FIELD_PATTERNS: List[Tuple[str, "re.Pattern"]] = [
    ("ltv", re.compile(r"\bloan-to-value\b|\bltv\b", re.I)),
    ("dti_ratio", re.compile(r"\bdebt-to-income\b|\bdti\b", re.I)),
    ("housing_ratio", re.compile(r"\bhousing (?:expense )?ratio\b", re.I)),
    ("credit_score_1003", re.compile(r"\bcredit score\b|\bfico\b", re.I)),
]
COMPUTATION_FIELD_PATTERNS: List[Tuple[str, "re.Pattern"]] = [
    ("ltv", re.compile(r"\bloan-to-value\b|\bltv\b", re.I)),
    ("dti_ratio", re.compile(r"\bdebt-to-income\b|\bdti\b", re.I)),
]

# computation cards where LTV/DTI is mentioned only as incidental context for
# a different real subject (contribution amount / down payment), hand-checked
# against the real card text -- see the module docstring's "computation"
# section. Keyed by exception_code (unique enough within this small set).
_LTV_DTI_INCIDENTAL_CONTEXT = {
    "O-FNM-50329",  # HomeReady LTV>80% -- defect is the CONTRIBUTION amount
    "O-FNM-56091",  # HomeReady LTV>80% -- defect is the 5% contribution
    "O-FNM-55631",  # co-signer LTV>80% -- defect is the down payment source
}

# "was/were not calculated correctly/appropriately", "not recalculated",
# "not included in the ... calculation" -- the genuine "recompute this ratio"
# signal that distinguishes a real computation-LTV/DTI card from one that
# merely mentions LTV/DTI as context for a different subject.
_COMPUTATION_VERB_RE = re.compile(
    r"not (?:be )?(?:re)?calculat|not recalculat|not included in the .{0,30}calculation"
    r"|increase(?:d)? beyond|exceed(?:s|ed)? without",
    re.I,
)

_UPPER_BOUND_RE = re.compile(
    r"\b(?:exceed(?:s|ed)?|over|greater than|more than|above)\b", re.I)
_LOWER_BOUND_RE = re.compile(r"\b(?:below|less than|under|fell below)\b", re.I)
_NUM_RE = re.compile(r"(\d+(?:\.\d+)?)\s*%?")
_SENT_SPLIT_RE = re.compile(r"(?<=[.;])\s+")

_APPLIES_IF_OP_MAP = {
    "eq": "==",
    "ne": "!=",
    "in": "in",
    "gte": ">=",
    "lte": "<=",
    "gt": ">",
    "lt": "<",
}


# --- small deterministic helpers --------------------------------------------

def _slug(text: str, maxlen: int = 50) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", (text or "").lower()).strip("_")
    s = re.sub(r"_+", "_", s)
    return (s[:maxlen].strip("_")) or "x"


def _stable_suffix(*parts: str) -> str:
    h = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()
    return h[:8]


def _placeholder_field_name(prefix: str, card_id: str, exception_code: str,
                            description: str) -> str:
    return "{}__{}__{}".format(
        prefix, _slug(description), _stable_suffix(card_id, exception_code))


def _sentence_containing(desc: str, match: "re.Match") -> str:
    sentences = []
    start = 0
    for sm in _SENT_SPLIT_RE.finditer(desc):
        sentences.append(desc[start:sm.start() + 1])
        start = sm.end()
    sentences.append(desc[start:])
    pos = match.start()
    off = 0
    for s in sentences:
        if off <= pos < off + len(s):
            return s
        off += len(s)
    return desc


def _match_known_field(desc: str, patterns: List[Tuple[str, "re.Pattern"]]
                       ) -> Optional[Tuple[str, "re.Match"]]:
    for field_name, pat in patterns:
        m = pat.search(desc)
        if m:
            return field_name, m
    return None


def _parse_threshold(desc: str, match: "re.Match") -> Optional[Tuple[str, str]]:
    """Best-effort (operator, threshold) parse from the sentence containing
    `match` (a known-field keyword hit). Returns None (-> caller uses
    "UNSPECIFIED") unless exactly one number and exactly one unambiguous
    directional keyword co-occur in that sentence. See module docstring for
    why "not met"/"did not meet"/"insufficient" are deliberately excluded."""
    sent = _sentence_containing(desc, match)
    nums = list(_NUM_RE.finditer(sent))
    if len(nums) != 1:
        return None
    ups = list(_UPPER_BOUND_RE.finditer(sent))
    lows = list(_LOWER_BOUND_RE.finditer(sent))
    if len(ups) == 1 and len(lows) == 0:
        return "<=", nums[0].group(1)
    if len(lows) == 1 and len(ups) == 0:
        return ">=", nums[0].group(1)
    return None


def _coerce_in_values(raw_value: Any) -> List[str]:
    if isinstance(raw_value, list):
        return [str(v) for v in raw_value]
    if isinstance(raw_value, str) and raw_value.strip().startswith("["):
        try:
            parsed = ast.literal_eval(raw_value)
            if isinstance(parsed, list):
                return [str(v) for v in parsed]
        except (ValueError, SyntaxError):
            pass
    return [str(raw_value)]


def _condition_to_applies_if(cond: Dict[str, Any]) -> Optional[Dict[str, str]]:
    op = cond.get("op")
    mapped_op = _APPLIES_IF_OP_MAP.get(op)
    if mapped_op is None:
        return None  # unmapped op (never observed in this data set; dropped defensively)
    if mapped_op == "in":
        value = "|".join(_coerce_in_values(cond["value"]))
    else:
        value = str(cond["value"])
    return {"field_name": cond["field"], "operator": mapped_op, "value": value}


# 2026-08-02: cards whose any_of mixes more than one field -- p0's
# applies_if is AND-only, can't express a cross-field OR natively. Curated,
# individually verified allowlist (same discipline as CURATED_DOC_MATCHES):
# (card_id) -> a real derived Loans.ContextFlag_<name> field that resolves
# the same OR one-directionally (True when a real branch confirms it, else
# left unset/undetermined -- never a guessed False). Everything not in this
# dict keeps the previous drop-the-any_of behavior, which is still the
# honest floor for cards not yet reviewed -- scanned ruleset-wide, this is
# the only card with a heterogeneous any_of today (compile-time stat
# any_of_dropped_heterogeneous_fields_cards would show any others).
_MULTI_FIELD_OR_CARDS = {
    "PC::O-FNM-15437": "Loans.ContextFlag_property_condo_pud_coop",
}


def build_applies_if(applicability: Dict[str, Any], card_id: str = ""
                     ) -> Tuple[Optional[List[Dict[str, str]]], bool]:
    """Returns (applies_if, any_of_dropped_heterogeneous_fields)."""
    if applicability.get("always"):
        return None, False

    conditions: List[Dict[str, str]] = []
    for cond in applicability.get("all_of") or []:
        c = _condition_to_applies_if(cond)
        if c is not None:
            conditions.append(c)

    any_of = applicability.get("any_of") or []
    dropped = False
    if any_of:
        fields = {c["field"] for c in any_of}
        if len(fields) == 1 and all(c.get("op") == "eq" for c in any_of):
            field_name = next(iter(fields))
            values = [str(c["value"]) for c in any_of]
            conditions.append({
                "field_name": field_name, "operator": "in",
                "value": "|".join(values),
            })
        else:
            or_field = _MULTI_FIELD_OR_CARDS.get(card_id)
            if or_field is not None:
                conditions.append({"field_name": or_field, "operator": "==", "value": "True"})
            else:
                # heterogeneous OR (or a non-"eq" any_of, never observed) --
                # p0's applies_if grammar can't express a cross-field OR;
                # drop the any_of gate and keep only all_of. Flagged to the
                # caller.
                dropped = True

    return (conditions or None), dropped


# --- per check_type converters ----------------------------------------------

def _base_check_kwargs(card: Dict[str, Any], option: Dict[str, Any],
                       check_id: str, applies_if: Optional[List[Dict[str, str]]]
                      ) -> Dict[str, Any]:
    finding = option["finding"]
    return dict(
        id=check_id,
        name=option.get("response") or finding["description"],
        severity=GOLD_SEVERITY_MAP.get(finding["severity"], "WARNING"),
        message_fail=finding["description"],
        applies_if=applies_if,
        question_code=card["card_id"],
    )


def _convert_doc_presence_or_completeness(card, option, check_id, applies_if,
                                          prefix: str) -> Check:
    finding = option["finding"]
    curated_field = CURATED_DOC_MATCHES.get((card["card_id"], finding["exception_code"]))
    field_name = curated_field or _placeholder_field_name(
        prefix, card["card_id"], finding["exception_code"], finding["description"])
    kw = _base_check_kwargs(card, option, check_id, applies_if)
    return Check(kind="predicate", predicate="is_present", field_name=field_name, **kw)


def _convert_threshold_eligibility(card, option, check_id, applies_if) -> Optional[Check]:
    # 2026-07-31: previously fell back to a placeholder field_name +
    # threshold="UNSPECIFIED" whenever no known field matched or the numeric
    # bound couldn't be parsed -- that Check would then report NEEDS_REVIEW
    # for every loan, forever, which is a compile-time defect (the rule text
    # was never actually turned into a real check) wearing a runtime status.
    # Same disease as the doc_presence FAIL bug fixed earlier this session;
    # same cure -- don't construct a Check at all, let the caller mark it
    # unsupported (NOT_COMPILED) instead. Returns None on failure.
    finding = option["finding"]
    desc = finding["description"]
    matched = _match_known_field(desc, THRESHOLD_FIELD_PATTERNS)
    parsed = _parse_threshold(desc, matched[1]) if matched else None
    if parsed is None:
        return None
    field_name = matched[0]
    operator, threshold = parsed
    kw = _base_check_kwargs(card, option, check_id, applies_if)
    return Check(kind="ratio_threshold", ratio="field_value", field_name=field_name,
                operator=operator, threshold=threshold, **kw)


def _computation_disposition(desc: str) -> str:
    """Returns 'ltv', 'dti_ratio', or '' (not a computation this converter handles)."""
    matched = _match_known_field(desc, COMPUTATION_FIELD_PATTERNS)
    if not matched:
        return ""
    field_name, _m = matched
    if not _COMPUTATION_VERB_RE.search(desc):
        return ""
    return field_name  # "ltv" or "dti_ratio"


def _convert_computation_ltv_dti(card, option, check_id, applies_if,
                                 field_name: str) -> Optional[Check]:
    # Same fix as _convert_threshold_eligibility above: a field-matched-but-
    # unparseable threshold is a compile-time defect, not a per-loan gap --
    # don't emit a Check that would say NEEDS_REVIEW for every loan forever.
    finding = option["finding"]
    desc = finding["description"]
    matched = _match_known_field(desc, COMPUTATION_FIELD_PATTERNS)
    parsed = _parse_threshold(desc, matched[1]) if matched else None
    if parsed is None:
        return None
    operator, threshold = parsed
    ratio = "ltv" if field_name == "ltv" else "dti"
    kw = _base_check_kwargs(card, option, check_id, applies_if)
    return Check(kind="ratio_threshold", ratio=ratio, field_name=field_name,
                operator=operator, threshold=threshold, **kw)


# 2026-08-01: scripted_review checks gold itself marked as requiring a
# human -- but a content read of all 147 defect_options
# (output/NEEDS-REVIEW-REMEDIATION-RESEARCH-2026-08-01.md) found some are
# genuinely deterministic field checks once the right fact exists, not
# open-ended judgment. Curated, individually hand-verified allowlist --
# same discipline as CURATED_DOC_MATCHES -- (card_id, exception_code) ->
# real is_true field_name. Everything not in this dict keeps the placeholder
# behavior (always NEEDS_REVIEW/APPLICABILITY_UNKNOWN, since no fixture
# populates a placeholder), which is still the honest floor for the ~138
# checks not yet reviewed.
CURATED_SCRIPTED_REVIEW_FIELDS = {
    ("PC::O-EPD-14457", "O-EPD-52921"): "employer_address_not_po_box_only",
    # 2026-08-02: 3 more, each a real derived fact, each one-directional
    # (only ever asserts True/confirmed-no-defect, never a confident False)
    # -- see touchless_adapter.py for the full reasoning. Correctly inert
    # today (all 3 underlying fields are null for the current bake-off
    # loan); wired ahead of data landing so a future loan resolves them on
    # the next compile with no further engineering.
    ("PC::O-FNM-50297", "O-FNM-50297"): "appraised_value_within_comp_range",
    ("PC::O-FNM-54534", "O-FNM-54534"): "zoning_legal_or_unknown",
    ("PC::O-EPD-14455", "O-EPD-52936"): "no_adverse_credit_public_records",
}


def _convert_scripted_review(card, option, check_id, applies_if) -> Check:
    finding = option["finding"]
    curated_field = CURATED_SCRIPTED_REVIEW_FIELDS.get((card["card_id"], finding["exception_code"]))
    field_name = curated_field or _placeholder_field_name(
        "scripted_review_checklist", card["card_id"], finding["exception_code"],
        finding["description"])
    kw = _base_check_kwargs(card, option, check_id, applies_if)
    return Check(kind="predicate", predicate="is_true", field_name=field_name, **kw)


# --- top-level build ---------------------------------------------------------

def load_demo_exclusions(path: str = DEMO_EXCLUSIONS_PATH) -> Dict[Tuple[str, str], str]:
    """(card_id, exception_code) -> reason, for checks this DEMO build should
    not compile (deployment-scope decision -- see demo_exclusions.json's
    _meta and A0 in the plan). Never mutates rules_compiled.json; a future
    non-demo build should not consult this file."""
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {
        (e["card_id"], e["exception_code"]): e["reason"]
        for e in data.get("exclusions", [])
    }


def load_scenario_na(path: str = SCENARIO_APPLICABILITY_PATH) -> Dict[Tuple[str, str], str]:
    """(card_id, exception_code) -> cited fact, for checks whose gold-defined
    scenario trigger was determined provably FALSE for the specific loan
    this scenario table was built against (see the file's own _meta for the
    experiment methodology, the disjunction-safety rule applied, and the
    2026-07-31 spot-check corrections). PROVISIONAL -- see _meta.
    spot_check_status. Only NA-verdict rows are returned; APPLIES/UNKNOWN/
    NOT_CONDITIONAL rows don't change conversion behavior and are skipped."""
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {
        (r["card_id"], r["exception_code"]): r["cited_fact"]
        for r in data.get("rows", [])
        if r["verdict"] == "NA"
    }


# 2026-08-01: maps doc_decidability_classification.json's `category` to a
# precise unsupported reason naming the ORIGINAL RULE issue, not just the
# engine-level fact "no curated document match" -- see that file's own
# _meta for what each category means and Gordon's explicit ask ("that
# should have a category, name this to point to the original rule issue").
_DOC_DECIDABILITY_REASON = {
    "PURE_PRESENCE": "doc_type_not_curated:pure_presence_reviewed_rejected",
    "PRESENCE_GATE": "doc_type_not_curated:presence_gate_needs_conditional_logic",
    "COMPOUND_DOCS": "doc_type_not_curated:compound_docs_needs_multi_doc_logic",
    "TRIGGER_GATED": "doc_type_not_curated:trigger_gated_needs_fact_machinery",
    "NOT_DOC_DECIDABLE": "doc_type_not_curated:not_doc_decidable_likely_misclassified",
}


def load_doc_decidability(path: str = DOC_DECIDABILITY_PATH) -> Dict[Tuple[str, str], str]:
    """(card_id, exception_code) -> unsupported reason string, precise about
    WHY a doc_presence/doc_completeness check isn't curated (see
    _DOC_DECIDABILITY_REASON). A key absent here (not yet triaged) falls
    back to the generic 'doc_type_not_curated' reason -- same honest floor
    as before this classification existed."""
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    out = {}
    for r in data.get("rows", []):
        reason = _DOC_DECIDABILITY_REASON.get(r["category"])
        if reason:
            out[(r["card_id"], r["exception_code"])] = reason
    return out


def _inject_scenario_gate(applies_if: Optional[List[Dict[str, str]]]
                          ) -> List[Dict[str, str]]:
    """Appends the scenario-gate sentinel condition (always False -> forces
    NOT_APPLICABLE via the existing applies_if mechanism, engine.py
    untouched) onto whatever applies_if the card already computed."""
    extra = {"field_name": SCENARIO_GATE_SENTINEL_FIELD, "operator": "==", "value": "True"}
    return (list(applies_if) if applies_if else []) + [extra]


# 2026-08-01: context_flags -> the real Loans.ContextFlag_<name> field
# touchless_adapter.py populates for it, see that module's "context_flags
# gating fields" comment for the full trace (the RefiNow-DTI false-PASS this
# fixes) and CLAUDE.md's per-loan applicability-is-loan-agnostic-at-compile-
# time architecture note. Only flags with a real, closed-world-or-
# structurally-derivable fact are here; every other flag (28 of 29
# ruleset-wide) is left unhandled -- same honest floor as every other
# not-yet-converted piece of this ruleset.
CONTEXT_FLAG_APPLIES_IF_FIELD = {
    "income_type_self_employment": None,  # src-only today, not p0 -- deliberately not wired here yet
    "appraisal_in_file": "Loans.ContextFlag_appraisal_in_file",
    "credit_report_presence_determined": "Loans.ContextFlag_credit_report_presence_determined",
    "loan_product_purchase": "Loans.ContextFlag_loan_product_purchase",
    "loan_product_refinow": "Loans.ContextFlag_loan_product_refinow",
    "loan_product_limited_cash_out_refinance": "Loans.ContextFlag_loan_product_limited_cash_out_refinance",
    "loan_product_cash_out_refinance": "Loans.ContextFlag_loan_product_cash_out_refinance",
    "loan_product_arm": "Loans.ContextFlag_loan_product_arm",
}

# The one card ruleset-wide whose context_flags combine multiple of the
# flags above (refinow / cash_out_refinance / limited_cash_out_refinance) --
# verified by scanning every card before writing this fix. p0's applies_if
# is AND-only (confirmed by reading engine.py's _eval_applies_if), so a true
# OR across these three needs a precomputed combined field
# (Loans.ContextFlag_any_refinance_type, set in touchless_adapter.py) rather
# than three separate AND conditions, which would incorrectly require ALL
# three simultaneously (impossible -- a loan can't be all three refinance
# subtypes at once).
_MULTI_FLAG_OR_CARDS = {
    "PC::O-FNM-15422": "Loans.ContextFlag_any_refinance_type",
}


def _inject_context_flags(applies_if: Optional[List[Dict[str, str]]],
                          card_id: str, context_flags: List[str]
                          ) -> List[Dict[str, str]]:
    """Appends an AND condition per handled context_flags entry. A card
    with an unhandled flag (not in CONTEXT_FLAG_APPLIES_IF_FIELD) is left
    exactly as today -- no condition injected for that flag, preserving
    current behavior rather than guessing."""
    conditions = list(applies_if) if applies_if else []
    if not context_flags:
        return conditions
    or_field = _MULTI_FLAG_OR_CARDS.get(card_id)
    if or_field is not None:
        conditions.append({"field_name": or_field, "operator": "==", "value": "True"})
        return conditions
    for flag in context_flags:
        field_name = CONTEXT_FLAG_APPLIES_IF_FIELD.get(flag)
        if field_name is not None:
            conditions.append({"field_name": field_name, "operator": "==", "value": "True"})
    return conditions


def load_autopass(path: str = AUTOPASS_PATH) -> Dict[Tuple[str, str], str]:
    """(card_id, exception_code) -> reason, for checks this DEMO build
    auto-passes because they require verifying something inside DU/EPIC/Loan
    Delivery -- a system this project has no connection to. Unlike
    demo_exclusions, these ARE compiled and produce a real PASS verdict.
    See autopass_no_system_access.json's _meta for the full decision record
    and the acknowledged 'never show a false clean' tradeoff."""
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {
        (e["card_id"], e["exception_code"]): e["reason"]
        for e in data.get("autopass", [])
    }


def _make_autopass_check(card: Dict[str, Any], option: Dict[str, Any],
                          check_id: str, applies_if: Optional[List[Dict[str, str]]],
                          reason: str) -> Check:
    kw = _base_check_kwargs(card, option, check_id, applies_if)
    kw["message_pass"] = (
        "auto-pass: requires verification inside %s, which this project has "
        "no connection to (demo-scoped decision, see "
        "autopass_no_system_access.json)" % reason)
    return Check(field_name=AUTOPASS_SENTINEL_FIELD, kind="predicate",
                 predicate="is_true", **kw)


def build_ruleset(gold_path: str = GOLD_RULES_PATH,
                   demo_exclusions_path: str = DEMO_EXCLUSIONS_PATH,
                   autopass_path: str = AUTOPASS_PATH,
                   scenario_na_path: str = SCENARIO_APPLICABILITY_PATH,
                   doc_decidability_path: str = DOC_DECIDABILITY_PATH,
                  ) -> Tuple[Ruleset, Dict[str, Any], Dict[str, Any]]:
    """Returns (ruleset, gold_to_check_mapping, stats)."""
    with open(gold_path, "r", encoding="utf-8") as f:
        gold = json.load(f)
    demo_exclusions = load_demo_exclusions(demo_exclusions_path)
    autopass = load_autopass(autopass_path)
    scenario_na = load_scenario_na(scenario_na_path)
    doc_decidability = load_doc_decidability(doc_decidability_path)

    checks: List[Check] = []
    mapping: Dict[str, Any] = {}
    seen_ids: set = set()
    converted_by_type: Counter = Counter()
    unsupported: List[Dict[str, str]] = []
    any_of_dropped_cards: List[str] = []

    for card in gold["cards"]:
        card_id = card["card_id"]
        applies_if, any_of_dropped = build_applies_if(card["applicability"], card_id)
        if any_of_dropped:
            any_of_dropped_cards.append(card_id)
        context_flags = (card["applicability"] or {}).get("context_flags") or []
        applies_if = _inject_context_flags(applies_if, card_id, context_flags)

        for option in card["defect_options"]:
            check_type = option["check_type"]
            finding = option["finding"]
            exception_code = finding["exception_code"]

            # A2: per-OPTION override, not per-card -- the scenario table is
            # keyed at (card_id, exception_code) granularity, so a sibling
            # defect_option on the same card that's still APPLIES/UNKNOWN
            # must not inherit this card's scenario-gated sibling's extra
            # condition. `applies_if` itself (card-level) stays untouched.
            option_applies_if = applies_if
            if (card_id, exception_code) in scenario_na:
                option_applies_if = _inject_scenario_gate(applies_if)

            base_id = "{}::{}".format(card_id, exception_code)
            check_id = base_id
            n = 2
            while check_id in seen_ids:
                check_id = "{}#{}".format(base_id, n)
                n += 1
            seen_ids.add(check_id)

            check: Optional[Check] = None
            disposition_note = ""

            demo_excl_reason = demo_exclusions.get((card_id, exception_code))
            autopass_reason = autopass.get((card_id, exception_code))
            if demo_excl_reason is not None:
                unsupported.append({
                    "card_id": card_id, "exception_code": exception_code,
                    "check_type": check_type,
                    "reason": "demo_excluded:{}".format(demo_excl_reason),
                })
            elif autopass_reason is not None:
                check = _make_autopass_check(card, option, check_id, option_applies_if, autopass_reason)
            elif check_type in ("doc_presence", "doc_completeness"):
                # 2026-07-31: an uncurated doc_presence/doc_completeness check
                # has no real Touchless documentType behind it -- the old
                # behavior wired an is_present Check against an
                # auto-generated placeholder field name that no fixture ever
                # populates, which engine.py's documented 015-Issue-2
                # semantics ("absent field = provably not there") then
                # resolved to a confident FAIL. Traced end-to-end
                # (output/BAKEOFF-P0-VS-SRC-GOLD-RULESET-2026-07-31.md
                # Addendum 5): 204/204 of this run's p0 FAILs were exactly
                # this pattern -- zero were on a real, populated field. src's
                # run_gold_ruleset_audit.py already floors the identical
                # situation to NO_DATA (see its "no reliable document-type
                # match... not individually curated" branch); p0 has no
                # NO_DATA status, so the symmetric honest floor here is
                # NOT_COMPILED, same bucket as every other not-yet-converted
                # check -- not a confident, evidence-free FAIL.
                if (card_id, exception_code) not in CURATED_DOC_MATCHES:
                    # 2026-08-01: sub-categorize by doc_decidability_
                    # classification.json's category when known -- names the
                    # ORIGINAL RULE issue (needs trigger-fact machinery /
                    # conditional-presence logic / multi-doc comparison /
                    # likely a check_type mislabel / already individually
                    # reviewed and rejected) instead of a flat, engine-level
                    # "not curated" label that erases why. Falls back to the
                    # generic reason for the handful of rows not yet triaged.
                    reason = doc_decidability.get(
                        (card_id, exception_code), "doc_type_not_curated")
                    unsupported.append({
                        "card_id": card_id, "exception_code": exception_code,
                        "check_type": check_type,
                        "reason": reason,
                    })
                else:
                    check = _convert_doc_presence_or_completeness(
                        card, option, check_id, option_applies_if, check_type)
            elif check_type == "threshold_eligibility":
                check = _convert_threshold_eligibility(card, option, check_id, option_applies_if)
                if check is None:
                    unsupported.append({
                        "card_id": card_id, "exception_code": exception_code,
                        "check_type": check_type, "reason": "threshold_not_parseable",
                    })
            elif check_type == "computation":
                field_name = _computation_disposition(finding["description"])
                if field_name and exception_code in _LTV_DTI_INCIDENTAL_CONTEXT:
                    disposition_note = "computation_incidental_ltv_dti_context"
                    field_name = ""
                if field_name:
                    check = _convert_computation_ltv_dti(
                        card, option, check_id, option_applies_if, field_name)
                    if check is None:
                        unsupported.append({
                            "card_id": card_id, "exception_code": exception_code,
                            "check_type": check_type, "reason": "threshold_not_parseable",
                        })
                else:
                    unsupported.append({
                        "card_id": card_id, "exception_code": exception_code,
                        "check_type": check_type,
                        "reason": disposition_note or "computation_not_ltv_dti",
                    })
            elif check_type == "cross_doc_consistency":
                # 2026-07-31: this converter never had real per-check
                # comparison logic -- field_name was always an
                # auto-generated placeholder unique to this
                # (card_id, exception_code), which no fixture has ever
                # populated (no CURATED_CROSS_DOC_MATCHES equivalent to
                # CURATED_DOC_MATCHES exists). Checked what that produced at
                # runtime before this fix: 87 of the 100 converted checks
                # silently resolved NOT_APPLICABLE ("No data present for
                # cross_doc__...") -- worse than the doc_presence FAIL bug,
                # because NOT_APPLICABLE reads as "confirmed this doesn't
                # apply, safe to skip" when the truth is "never had real
                # logic to test it." (11 more resolved NEEDS_REVIEW for a
                # genuine reason -- Loans.Underwriting_Type is null -- and 2
                # resolved a genuine NOT_APPLICABLE via real applies_if
                # preconditions; both small, legitimate signals are accepted
                # as lost here, same trade-off already made for
                # doc_presence/doc_completeness above.) src/shacl_pilot's
                # mirror-image "entity-family existence probe" has the
                # identical root cause and gets the identical fix in
                # ruleset_to_shacl.py.
                unsupported.append({
                    "card_id": card_id, "exception_code": exception_code,
                    "check_type": check_type, "reason": "cross_doc_no_curated_comparison",
                })
            elif check_type == "scripted_review":
                check = _convert_scripted_review(card, option, check_id, option_applies_if)
            elif check_type in SKIPPED_TYPES:
                pass  # zero defect_options expected; nothing to do
            elif check_type in NOT_CONVERTED_TYPES:
                unsupported.append({
                    "card_id": card_id, "exception_code": exception_code,
                    "check_type": check_type, "reason": "not_converted_by_design",
                })
            else:
                unsupported.append({
                    "card_id": card_id, "exception_code": exception_code,
                    "check_type": check_type, "reason": "unrecognized_check_type",
                })

            if check is not None:
                checks.append(check)
                converted_by_type[check_type] += 1
                mapping[check_id] = {
                    "card_id": card_id,
                    "exception_code": exception_code,
                    "check_type": check_type,
                    "gold_severity": finding["severity"],
                    "defect_description": finding["description"],
                    "kind": check.kind,
                    "field_name": check.field_name,
                    "scenario_gate_na_reason": scenario_na.get((card_id, exception_code)),
                }

    ruleset = Ruleset(ruleset_id=RULESET_ID, version=RULESET_VERSION, checks=checks)

    stats = {
        "total_defect_options": sum(len(c["defect_options"]) for c in gold["cards"]),
        "converted_by_check_type": dict(converted_by_type),
        "converted_total": len(checks),
        "unsupported_total": len(unsupported),
        "unsupported_by_reason": dict(Counter(u["reason"] for u in unsupported)),
        "unsupported_by_check_type": dict(Counter(u["check_type"] for u in unsupported)),
        "any_of_dropped_heterogeneous_fields_cards": any_of_dropped_cards,
        "unsupported_detail": unsupported,
    }
    return ruleset, mapping, stats


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gold-path", default=GOLD_RULES_PATH)
    parser.add_argument("--loan-fixture", default=TOUCHLESS_FIXTURE_PATH)
    parser.add_argument("--mapping-out", default=MAPPING_OUT_PATH)
    parser.add_argument("--results-out", default=RESULTS_OUT_PATH)
    args = parser.parse_args()

    sys.path.insert(0, os.path.join(_P0, "fixtures", "from_docs"))
    from fixture_loader import load_canonical_loan  # noqa: E402
    from qc_engine.engine import run  # noqa: E402

    ruleset, mapping, stats = build_ruleset(args.gold_path)
    loan = load_canonical_loan(args.loan_fixture)
    result = run(loan, ruleset)

    os.makedirs(os.path.dirname(args.mapping_out), exist_ok=True)
    with open(args.mapping_out, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=1, sort_keys=True)
    with open(args.results_out, "w", encoding="utf-8") as f:
        json.dump(result.to_dict(), f, indent=1, sort_keys=True)

    verdicts = Counter(r.status for r in result.results)

    print("=== import_gold_ruleset.py: gold -> p0 conversion summary ===")
    print("Total gold defect_options: {}".format(stats["total_defect_options"]))
    print("\nConverted, by gold check_type:")
    for k, v in sorted(stats["converted_by_check_type"].items()):
        print("  {:24s} {}".format(k, v))
    print("Converted total: {}".format(stats["converted_total"]))
    print("\nUnsupported (not converted), by reason:")
    for k, v in sorted(stats["unsupported_by_reason"].items()):
        print("  {:38s} {}".format(k, v))
    print("Unsupported total: {}".format(stats["unsupported_total"]))
    if stats["any_of_dropped_heterogeneous_fields_cards"]:
        print("\nany_of gate DROPPED (heterogeneous fields, see docstring): {}".format(
            stats["any_of_dropped_heterogeneous_fields_cards"]))
    print("\n=== Run against loan {} ===".format(loan.loan_id))
    print("Ruleset sha256: {}".format(ruleset.sha256()))
    print("Verdict distribution:")
    for k, v in sorted(verdicts.items()):
        print("  {:14s} {}".format(k, v))
    print("\nWrote: {}".format(args.mapping_out))
    print("Wrote: {}".format(args.results_out))


if __name__ == "__main__":
    main()
