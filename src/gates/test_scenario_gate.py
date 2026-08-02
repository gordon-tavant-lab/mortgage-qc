"""
Standing negative-control tests for the scenario applicability gate.

WHY THESE EXIST — READ BEFORE CHANGING THE GATE
A wrongly-excluded rule is a SILENT FALSE NEGATIVE: it yields a clean audit with no
artifact for anyone to review. It is invisible to
  * the 25/25 defect gate  (tests defects that ARE present, not rules that should fire)
  * the field Coverage Gate (checks fields, not scenario triggers)
  * the SME                (a suppressed rule produces nothing to review)
Worse, the symptom LOOKS LIKE SUCCESS — fewer findings reads as progress.

So the gate's correctness cannot be established by observing its output. It has to be
pinned by controls that fail loudly:

  H2  scenario PRESENT  -> the exclusion must vanish            (too-loose failure)
  H2b proving field NULL -> NO_DATA, never NOT_APPLICABLE       (unknowable failure)
  H3  disjunctive rule with a live alternative -> NO_DATA       (the 2026-07-30 bug)
  H3b intra-trigger "or" (subtypes/verbs) -> still excluded     (over-correction failure)

H3 and H3b are deliberately opposed. The disjunction guard has two ways to fail: too
loose suppresses real rules, too tight makes the gate useless. Both directions are tested.

METHOD NOTE (2026-07-30): the original H3 assertion was itself WRONG in the same
direction as the code — both assumed "keyword present => that is the rule's trigger".
6 of 8 apparent failures were correct exclusions. Hand-adjudication, not the test,
separated them. Tests bound behaviour; they do not establish correctness.
"""
import copy
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scenario_gate import (DO_NOT_GATE, SCENARIOS, _is_disjunctive,  # noqa: E402
                           _undisprovable_alternatives, classify)

REPO = "/Users/gordonchan/Workspace/demo-sites/mortgage-qc-prod/"
LOAN = REPO + "demo/touchless/loan_application.json"
RULESET = REPO + "src/shacl_pilot/compiled/ruleset.json"


@pytest.fixture(scope="module")
def loan():
    return json.load(open(LOAN))


@pytest.fixture(scope="module")
def rules():
    return json.load(open(RULESET))["rules"]


# ---------------------------------------------------------------- helpers
def mutate(base, **kw):
    """Return a copy of the loan with one scenario field changed."""
    L = copy.deepcopy(base)
    pd = L["collateralDetail"]["collateral"][0]["propertyDetail"]
    if "purpose" in kw:
        L["loanSummary"]["loanTerms"]["loanPurposeType"] = kw["purpose"]
    if "amort" in kw:
        L["loanSummary"]["amortization"]["amortizationType"] = kw["amort"]
    if "usage" in kw:
        pd["propertyUsageType"] = kw["usage"]
    if "units" in kw:
        pd["financedUnitCount"] = kw["units"]
    if "method" in kw:
        pd["constructionMethodType"] = kw["method"]
    if kw.get("addco"):
        bp = L["borrowersDetail"]["borrowerPairs"][0]
        bp["borrowers"].append(copy.deepcopy(bp["borrowers"][0]))
    return L


def excluded_count(rules, loan, scenario):
    return sum(1 for r in rules
               if classify(r, loan)[1] == scenario
               and classify(r, loan)[0] == "NOT_APPLICABLE")


def nodata_count(rules, loan, scenario):
    return sum(1 for r in rules
               if classify(r, loan)[1] == scenario
               and classify(r, loan)[0] == "NO_DATA")


def find(rules, fragment):
    return [r for r in rules
            if fragment in str(r.get("exception_description") or "")]


# ---------------------------------------------------------------- H1
def test_h1_baseline_exclusions_exist(rules, loan):
    """Sanity floor: the gate must actually be doing something."""
    total = sum(excluded_count(rules, loan, s) for s in SCENARIOS)
    assert total > 100, "gate excluded only %d rules — is it wired up?" % total


def test_h1_every_exclusion_cites_its_evidence(rules, loan):
    """Q7b — a verdict with no grounding statement is not auditable."""
    missing = [r.get("question_code") for r in rules
               if classify(r, loan)[0] == "NOT_APPLICABLE"
               and not classify(r, loan)[2]]
    assert not missing, "exclusions with no evidence field: %s" % missing[:5]


# ---------------------------------------------------------------- H2
H2_CASES = [
    ("refinance / cash-out", {"purpose": "CASHOUT_REFINANCE"}),
    ("refinance / cash-out", {"purpose": "NO_CASH_OUT_REFINANCE"}),
    ("ARM / adjustable", {"amort": "ADJUSTABLE"}),
    ("2nd home / investment", {"usage": "SecondHome"}),
    ("2nd home / investment", {"usage": "Investment"}),
    ("2-4 unit / multi-unit", {"units": 3}),
    ("co-borrower / non-occupant", {"addco": True}),
    ("manufactured / mobile", {"method": "Manufactured"}),
]


@pytest.mark.parametrize("scenario,mutation", H2_CASES)
def test_h2_present_scenario_is_never_suppressed(rules, loan, scenario, mutation):
    """THE FALSIFIER. If the scenario is present, no rule may be excluded for it."""
    base = excluded_count(rules, loan, scenario)
    assert base > 0, "precondition: %s should be excluded on the base loan" % scenario
    after = excluded_count(rules, mutate(loan, **mutation), scenario)
    assert after == 0, (
        "SILENT FALSE NEGATIVE: %d rule(s) still excluded for '%s' after making the "
        "scenario present via %s" % (after, scenario, mutation))


# ---------------------------------------------------------------- H2b
H2B_CASES = [
    ("refinance / cash-out", ["loanSummary", "loanTerms", "loanPurposeType"]),
    ("ARM / adjustable", ["loanSummary", "amortization", "amortizationType"]),
]


@pytest.mark.parametrize("scenario,path", H2B_CASES)
def test_h2b_null_proving_field_yields_nodata(rules, loan, scenario, path):
    """An unknowable scenario is NO_DATA — never NOT_APPLICABLE."""
    L = copy.deepcopy(loan)
    node = L
    for k in path[:-1]:
        node = node[k]
    node[path[-1]] = None
    assert excluded_count(rules, L, scenario) == 0, \
        "null %s must not produce NOT_APPLICABLE" % ".".join(path)
    assert nodata_count(rules, L, scenario) > 0, \
        "null %s should produce NO_DATA" % ".".join(path)


def test_h2b_null_property_usage_yields_nodata(rules, loan):
    L = copy.deepcopy(loan)
    L["collateralDetail"]["collateral"][0]["propertyDetail"]["propertyUsageType"] = None
    s = "2nd home / investment"
    assert excluded_count(rules, L, s) == 0
    assert nodata_count(rules, L, s) > 0


# ---------------------------------------------------------------- H3 (the bug)
H3_REGRESSIONS = [
    ("An exterior-only or desktop appraisal was used in a purchase transaction for a "
     "manufactured home",
     "matched 'manufactured home' but condo / leasehold / renovation remain live"),
    ("The condo was exempt from review without meeting the criteria of being a 2- to "
     "4-unit project",
     "matched refinance but 'detached unit' is a live alternative — this loan IS detached"),
]


@pytest.mark.parametrize("fragment,why", H3_REGRESSIONS)
def test_h3_disjunctive_rule_with_live_alternative_is_not_excluded(
        rules, loan, fragment, why):
    """The 2026-07-30 disjunction bug. Must never regress."""
    hits = find(rules, fragment[:60])
    assert hits, "fixture rule not found — did the ruleset change? (%s)" % fragment[:40]
    for r in hits:
        verdict, scenario, evidence = classify(r, loan)
        if verdict == "NOT_APPLICABLE":
            pytest.fail("DISJUNCTION BUG REGRESSED (%s): excluded on '%s' / %s\n  %s"
                        % (why, scenario, evidence,
                           str(r.get("exception_description"))[:140]))


# ---------------------------------------------------------------- H3b (over-correction)
H3B_INTRA_TRIGGER = [
    ("The borrower sold or traded in a manufactured home",
     "'sold or traded' = two verbs, one manufactured home — trigger is still MH"),
    ("The subject limited or cash-out refinance transaction",
     "'limited or cash-out' = two refi subtypes — trigger is still refi"),
    ("When making the ability to repay determination, the fully indexed rate or any "
     "introductory",
     "two rate types on an ARM — trigger is still ARM"),
]


@pytest.mark.parametrize("fragment,why", H3B_INTRA_TRIGGER)
def test_h3b_intra_trigger_or_still_excludes(rules, loan, fragment, why):
    """Guard must not over-correct: an 'or' joining SUBTYPES of one scenario is not
    a disjunction of alternative triggers."""
    hits = find(rules, fragment[:50])
    assert hits, "fixture rule not found (%s)" % fragment[:40]
    verdicts = {classify(r, loan)[0] for r in hits}
    assert "NOT_APPLICABLE" in verdicts, (
        "OVER-CORRECTION: %s — expected still excluded, got %s" % (why, verdicts))


def test_h3_disjunction_detector_is_neither_dead_nor_universal(rules, loan):
    """If it fires on ~0% it is dead code; on ~100% the guard is meaningless."""
    gated = [r for r in rules
             if classify(r, loan)[0] in ("NOT_APPLICABLE", "NO_DATA")]
    assert gated, "no gated rules to measure"
    fires = sum(1 for r in gated
                if _is_disjunctive(str(r.get("exception_description") or "")))
    pct = 100.0 * fires / len(gated)
    assert 5 < pct < 95, "disjunction detector fires on %.0f%% of gated rules" % pct


def test_h3_detached_is_a_live_alternative_for_this_loan(rules, loan):
    """This loan is attachmentType=Detached, so any rule offering 'detached' as an
    alternative trigger must not be excluded."""
    det = [r for r in rules
           if "detached" in str(r.get("exception_description") or "").lower()]
    leaks = [r.get("question_code") for r in det
             if classify(r, loan)[0] == "NOT_APPLICABLE"
             and "detached" in _undisprovable_alternatives(
                 str(r.get("exception_description")), loan, classify(r, loan)[1])]
    assert not leaks, "rules excluded despite a live 'detached' alternative: %s" % leaks[:5]


# ---------------------------------------------------------------- guard rails on the gate itself
def test_do_not_gate_scenarios_are_never_added_to_scenarios(loan):
    """condominium / construction / HomeReady must stay OUT of the gate until a field
    proves absence or an SME rules. Adding them is the change these tests exist to catch."""
    forbidden = {"condominium", "condo", "construction", "renovation",
                 "homeready", "home possible"}
    for name in SCENARIOS:
        low = name.lower()
        assert not any(f in low for f in forbidden), (
            "'%s' was added to SCENARIOS but is listed in DO_NOT_GATE (%s). A field must "
            "prove absence first — see docs/SCENARIO-GATE-EXPERIMENT-2026-07-30.md"
            % (name, DO_NOT_GATE))


def test_do_not_gate_list_is_documented():
    assert len(DO_NOT_GATE) >= 3, "DO_NOT_GATE lost entries — why?"
    for k, v in DO_NOT_GATE.items():
        assert v and len(v) > 20, "DO_NOT_GATE['%s'] needs a stated reason" % k
