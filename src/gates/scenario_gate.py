#!/usr/bin/env python3
"""
SCENARIO APPLICABILITY GATE — excludes a rule ONLY when a loan field proves the
scenario is absent.

Distinct from the program gate (docs/AMQ-PROGRAM-TAXONOMY.md), which only knows
FHA/VA/USDA. This catches a second layer: a refinance rule cannot apply to a purchase.

THE DESIGN CONSTRAINT THAT MATTERS (docs/LOAN-SCENARIO-APPLICABILITY.md):
A wrongly-excluded rule is a SILENT FALSE NEGATIVE — it produces a clean audit with no
artifact for anyone to review. That is strictly worse than a false positive. Therefore:

  * exclude ONLY on an explicit non-null field value that PROVES absence
  * a null field is `unknowable` -> NO_DATA, never NOT_APPLICABLE
  * every exclusion records the field and value it was derived from (grounding statement)
  * pudIndicator=Y means a PROJECT EXISTS -> project/condo rules stay ACTIVE

Verified counter-example: keyword matching alone flagged 93 condo/project rules as
inapplicable on a loan whose pudIndicator is "Y". That would have suppressed real rules.
"""
import json, re

# scenario -> (rule-text pattern, prover(loan)->(absent: bool|None, evidence: str))
# prover returns None for "unknowable" — NEVER exclude on unknowable.

def _pd(loan):
    col = loan.get("collateralDetail", {}).get("collateral", [{}])
    return (col[0] if col else {}).get("propertyDetail", {}) or {}

def _borrower_count(loan):
    return sum(len(p.get("borrowers", []))
               for p in loan.get("borrowersDetail", {}).get("borrowerPairs", []))

def p_purpose(loan):
    v = loan.get("loanSummary", {}).get("loanTerms", {}).get("loanPurposeType")
    if not v: return None, "loanPurposeType is null"
    return ("PURCHASE" in v.upper() and "REFIN" not in v.upper()), "loanPurposeType=%s" % v

def p_amortization(loan):
    v = loan.get("loanSummary", {}).get("amortization", {}).get("amortizationType")
    if not v: return None, "amortizationType is null"
    return (v.upper() == "FIXED"), "amortizationType=%s" % v

def p_coborrower(loan):
    n = _borrower_count(loan)
    if not n: return None, "no borrowers parsed"
    return (n == 1), "borrower count=%d" % n

def p_occupancy(loan):
    v = _pd(loan).get("propertyUsageType")
    if not v: return None, "propertyUsageType is null"
    return ("PRIMARY" in v.upper()), "propertyUsageType=%s" % v

def p_units(loan):
    pd = _pd(loan)
    v = pd.get("financedUnitCount") or pd.get("unitCount")
    if v is None: return None, "financedUnitCount is null"
    return (int(v) == 1), "financedUnitCount=%s" % v

def p_manufactured(loan):
    pd = _pd(loan)
    est, att = pd.get("propertyEstateType"), pd.get("attachmentType")
    if not est and not att: return None, "propertyEstateType/attachmentType null"
    mh = pd.get("constructionMethodType")
    if mh and "MANUFACT" in str(mh).upper():
        return False, "constructionMethodType=%s" % mh
    return (str(est).upper() == "FEESIMPLE"), "propertyEstateType=%s, attachmentType=%s" % (est, att)

SCENARIOS = {
    "refinance / cash-out": (
        r"\b(refinanc\w*|cash[- ]?out|no cash[- ]out|\bLCO\b|RefiNow|Refi Possible|rate/term)\b",
        p_purpose),
    "ARM / adjustable": (
        r"\b(ARM\b|adjustable[- ]rate|SOFR|fully indexed|interest rate cap|convertible)\b",
        p_amortization),
    "co-borrower / non-occupant": (
        r"\b(co[- ]?borrower|coborrower|non[- ]occupan\w+|non[- ]occupying|co[- ]signer|cosigner)\b",
        p_coborrower),
    "2nd home / investment": (
        r"\b(2nd home|second home|investment propert\w+|rental propert\w+|non[- ]owner occupied)\b",
        p_occupancy),
    "2-4 unit / multi-unit": (
        r"\b(2-4 unit|two[- ]to[- ]four|multi[- ]unit|duplex|triplex|fourplex)\b",
        p_units),
    "manufactured / mobile": (
        r"\b(manufactured home|mobile home|MH Advantage)\b",
        p_manufactured),
}

# Scenarios we deliberately DO NOT gate on — the proving field is null, or the scenario
# is active. Kept explicit so nobody "helpfully" adds them later.
DO_NOT_GATE = {
    "condominium / project": "projectType null AND pudIndicator=Y means a project EXISTS",
    "construction / renovation": "constructionMethodType null — unknowable",
    "HomeReady / affordable": "productName is suggestive, not proof — needs SME",
}


# --- DISJUNCTION GUARD (bug found + fixed 2026-07-30) ------------------------
# BUG: a rule listing ALTERNATIVE triggers was excluded after disproving only ONE.
#   "An exterior-only appraisal was used ... for a manufactured home, condo,
#    leasehold, or a SFR undergoing renovation."
# The gate matched "manufactured home", proved not-manufactured, and excluded the rule
# while condo / leasehold / renovation remained live doors into it. Silent false negative.
#
# FIX: if the matched keyword sits inside a disjunctive list, the rule may be excluded
# ONLY IF every alternative is independently disproven. Undecidable -> NO_DATA.

# Other scenario vocabulary that can appear as an alternative in a list.
ALT_TRIGGER_TERMS = {
    "condo":        r"\b(condominium|condo\b|co[- ]op\b|cooperative|condotel)\b",
    "leasehold":    r"\bleasehold\b",
    "renovation":   r"\b(renovation|rehab\w*|HomeStyle|undergoing construction)\b",
    "manufactured": r"\b(manufactured home|mobile home|MH Advantage)\b",
    "detached":     r"\bdetached\b",
    "multi_unit":   r"\b(2-4 unit|two[- ]to[- ]four|multi[- ]unit|duplex|triplex|fourplex)\b",
    "refinance":    r"\b(refinanc\w*|cash[- ]?out|RefiNow|Refi ?Possible)\b",
    "second_home":  r"\b(2nd home|second home|investment propert\w+)\b",
}

# Which alternatives can we DISPROVE for a given loan? Returns the set we cannot.
def _undisprovable_alternatives(text, loan, matched_scenario):
    """Alternatives present in the text that we cannot rule out for this loan."""
    pd = _pd(loan)
    live = set()
    for term, pat in ALT_TRIGGER_TERMS.items():
        if not re.search(pat, text, re.I):
            continue
        if term == "condo":
            # projectType null AND pudIndicator=Y -> a project exists. Cannot disprove.
            if not pd.get("projectType") or str(pd.get("pudIndicator") or "").upper() == "Y":
                live.add("condo")
        elif term == "leasehold":
            est = str(pd.get("propertyEstateType") or "")
            if not est:
                live.add("leasehold")
            elif "LEASEHOLD" in est.upper():
                live.add("leasehold")
        elif term == "renovation":
            if not pd.get("constructionMethodType"):
                live.add("renovation")          # unknowable
        elif term == "manufactured":
            absent, _ = p_manufactured(loan)
            if absent is not True:
                live.add("manufactured")
        elif term == "detached":
            if str(pd.get("attachmentType") or "").upper() == "DETACHED":
                live.add("detached")            # this loan IS detached -> alternative is LIVE
        elif term == "multi_unit":
            absent, _ = p_units(loan)
            if absent is not True:
                live.add("multi_unit")
        elif term == "refinance":
            absent, _ = p_purpose(loan)
            if absent is not True:
                live.add("refinance")
        elif term == "second_home":
            absent, _ = p_occupancy(loan)
            if absent is not True:
                live.add("second_home")
    return live


DISJUNCTION_RE = re.compile(r",\s*[^,.;]{1,60}\s*,?\s*\bor\b|\bor\b\s+(?:a|an|the)?\s*\w", re.I)


def _is_disjunctive(text):
    """Does the text enumerate alternatives (A, B, C, or D)?"""
    return bool(DISJUNCTION_RE.search(text))


def classify(rule, loan):
    """-> (verdict, scenario, evidence) ; verdict in {NOT_APPLICABLE, NO_DATA, None}"""
    text = rule.get("exception_description") or ""
    if not text:
        return None, None, None
    for name, (pattern, prover) in SCENARIOS.items():
        if not re.search(pattern, text, re.I):
            continue
        absent, evidence = prover(loan)
        if absent is None:
            return "NO_DATA", name, evidence      # unknowable — never exclude
        if absent is not True:
            return None, name, evidence           # scenario ACTIVE — rule must run

        # absent is True — but check for undisprovable ALTERNATIVE triggers first.
        if _is_disjunctive(text):
            live = _undisprovable_alternatives(text, loan, name)
            live.discard({"refinance": "refinance", "manufactured": "manufactured",
                          "2-4 unit / multi-unit": "multi_unit",
                          "2nd home / investment": "second_home"}.get(name, ""))
            if live:
                return ("NO_DATA", name,
                        "%s, BUT disjunctive rule has undisprovable alternative trigger(s): %s"
                        % (evidence, ", ".join(sorted(live))))
        return "NOT_APPLICABLE", name, evidence
    return None, None, None


def run(ruleset_path, loan_path):
    rules = json.load(open(ruleset_path))["rules"]
    loan = json.load(open(loan_path))
    out = {"NOT_APPLICABLE": [], "NO_DATA": [], "ACTIVE": []}
    for r in rules:
        v, s, e = classify(r, loan)
        if v == "NOT_APPLICABLE": out["NOT_APPLICABLE"].append((r, s, e))
        elif v == "NO_DATA":      out["NO_DATA"].append((r, s, e))
        elif s:                   out["ACTIVE"].append((r, s, e))
    return out
