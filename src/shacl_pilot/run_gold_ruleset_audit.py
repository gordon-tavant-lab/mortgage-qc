#!/usr/bin/env python3
"""
run_gold_ruleset_audit.py — run the gold rule set's SHACL conversion
(blocks/gold/*.ttl, from ruleset_to_shacl.py) against one Touchless loan.

src/shacl_pilot side of the p0/qc_engine-vs-src/shacl_pilot bake-off
(.claude/plans/1-no-no-this-iridescent-brooks.md, 2026-07-31). Mirrors
run_full_ruleset_audit.py's classification pattern (NOT_APPLICABLE resolved
in Python BEFORE touching pyshacl; FAIL/PASS/NO_DATA/NEEDS_REVIEW come from
actually running pyshacl.validate(..., advanced=True) and cross-referencing
fired-shape names + severities against required-predicate presence in the
loan's facts) but points at the gold-derived shapes/linkage instead of
compiled/ruleset.json / MAPPED_SHAPES, and — unlike run_full_ruleset_audit.py
— actually writes a JSON results file (no script in src/shacl_pilot did this
before).

Six-verdict scheme (five standard + NEEDS_REVIEW, the SHACL-side surface for
scripted_review's "genuine judgment" checks):
  FAIL            shape fired, sh:resultSeverity absent or Violation
  NEEDS_REVIEW    shape fired, sh:resultSeverity = Warning (scripted_review by design)
  NOT_APPLICABLE  card-level applicability gate excludes this loan
  NO_DATA         shape exists but a required li: predicate is absent from
                   this loan's graph, OR applicability itself can't be
                   determined (Underwriting_Type unknown) -- see
                   docs/LOAN-SCENARIO-APPLICABILITY.md's "cannot tell whether
                   the scenario applies -> NO_DATA" convention, which this
                   script follows for consistency with the rest of the
                   project rather than inventing a 7th verdict.
  PASS            shape ran, required data present, did not fire
  NOT_COMPILED    card/defect_option marked unsupported in gold_shape_mapping.json

Applicability (option (b) from the plan): computed directly off the raw
Touchless loan_application.json in Python, NOT round-tripped through the RDF
graph -- loan_to_rdf.py is reused completely unmodified, and
touchless_adapter.py's own field/fact-extraction logic is unmodified by this
script (this script only reads its output, e.g. `borrower_self_employed`).
See compute_applicability_facts() below. Card-level applicability also
respects a narrow, curated set of `context_flags` (currently just
self-employment) alongside the structural all_of/any_of/always conditions --
see evaluate_applicability() and SELF_EMPLOYMENT_CONTEXT_FLAG below.

USAGE:
  python3 run_gold_ruleset_audit.py \
      <loan_application.json> <extracted_data.json> [out_dir]
"""
import ast
import collections
import json
import os
import re
import sys

from rdflib import Graph, Namespace
from pyshacl import validate

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from touchless_adapter import adapt_touchless_to_extraction  # noqa: E402
from loan_to_rdf import build_graph  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
GOLD_RULES_PATH = os.path.join(REPO_ROOT, "storage", "rules", "gold", "data", "rules_compiled.json")
SCENARIO_APPLICABILITY_PATH = os.path.join(
    REPO_ROOT, "storage", "rules", "gold", "data",
    "scenario_applicability_loan12607601215.json")


def load_scenario_na(path=SCENARIO_APPLICABILITY_PATH):
    """(card_id, exception_code) -> cited fact, for checks whose gold-defined
    scenario trigger was determined provably FALSE for the specific loan
    this table was built against. PROVISIONAL -- see the file's own _meta
    (spot_check_status) for the experiment methodology and known limits.
    Only NA-verdict rows are returned."""
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        data = json.load(f)
    return {
        (r["card_id"], r["exception_code"]): r["cited_fact"]
        for r in data.get("rows", [])
        if r["verdict"] == "NA"
    }
GOLD_BLOCKS_DIR = os.path.join(HERE, "blocks", "gold")
MAPPING_PATH = os.path.join(GOLD_BLOCKS_DIR, "gold_shape_mapping.json")
DEFAULT_OUT_DIR = os.path.join(HERE, "bakeoff_gold_touchless_2026-07-31")

LI = Namespace("http://mortgage.audit.ontology/loan-instance#")
SH = Namespace("http://www.w3.org/ns/shacl#")

NON_LI_PREDICATES = {"cite_row", "doc_name", "page", "snippet", "loan_id"}


# ---------------------------------------------------------------------------
# Applicability -- computed straight off the raw Touchless payload (option
# (b) from the plan), independent of the RDF graph / touchless_adapter.py.
# QC_Policy is a documented experiment assumption (gold is FNM-conventional-
# only); the other 5 fields are read from the real payload.
# ---------------------------------------------------------------------------
def compute_applicability_facts(loan_app, borrower_self_employed=None):
    ls = loan_app.get("loanSummary", {}) or {}
    lt = ls.get("loanTerms", {}) or {}
    coll = (loan_app.get("collateralDetail", {}) or {}).get("collateral", []) or []
    pd = (coll[0].get("propertyDetail", {}) if coll else {}) or {}

    facts = {"Loans.QC_Policy": "Fannie Mae"}  # experiment assumption; gold is FNM-conventional-only

    # borrower_self_employed: passed in from touchless_adapter.py's own,
    # already-verified detection (employers[0].employment.isSelfEmployed /
    # ownershipInterestType) rather than re-derived here -- single source of
    # truth, see main() below. touchless_adapter.py only ever sets this key
    # when it can positively confirm self-employment; it never asserts a
    # definite "not self-employed", so the only two states this can be here
    # are True or None (unknown) -- never a guessed False. Consumed by
    # evaluate_applicability()'s context_flags handling, below.
    facts["borrower_self_employed"] = borrower_self_employed

    purpose = lt.get("loanPurposeType")
    facts["Loans.LoanPurposeType"] = purpose.replace("_", " ").title() if purpose else None

    mtype = lt.get("mortgageType")
    facts["Loans.LoanType"] = mtype.replace("_", " ").title() if mtype else None

    # PropertyType: derived from the propertyDetail flags actually present
    # in the payload (no direct enum field is populated -- propertyType is
    # null throughout). A determinate "not one of the special categories"
    # answer (e.g. plain detached SFR) is still a KNOWN value -- it must
    # resolve to a concrete string, not None/unknown, so eq/in comparisons
    # against it correctly return False (NOT_APPLICABLE), never "can't tell".
    pud = str(pd.get("pudIndicator") or "").upper() == "Y"
    attached = str(pd.get("attachmentType") or "").lower() == "attached"
    condo = bool(pd.get("condominiumIndicator"))
    coop = bool(pd.get("cooperativeIndicator"))
    units = pd.get("financedUnitCount")
    if condo:
        prop_type = "Condominium"
    elif coop:
        prop_type = "Cooperative"
    elif pud:
        prop_type = "PUD Attached" if attached else "PUD Detached"
    elif units and units in (2, 3, 4):
        prop_type = "2-4 unit"
    else:
        prop_type = "Single Family Detached"  # known, just not one of gold's special-case values
    facts["Loans.PropertyType"] = prop_type

    addr = pd.get("propertyAddress", {}) or {}
    facts["Loans.AddressState"] = addr.get("stateCode")

    # Genuinely absent from this payload (loanSummary.underwriting == None,
    # confirmed by direct inspection) -- must resolve unknown, not a guess.
    facts["Loans.Underwriting_Type"] = None

    return facts


def _parse_condition_value(v):
    if isinstance(v, str) and v.strip().startswith("["):
        try:
            return ast.literal_eval(v)
        except (ValueError, SyntaxError):
            return v
    return v


def _eval_condition(cond, facts):
    """True / False / None (unknown -- field has no determinable value)."""
    field = cond["field"]
    op = cond["op"]
    value = _parse_condition_value(cond["value"])
    have = facts.get(field)
    if have is None:
        return None
    if op == "eq":
        return have == value
    if op == "ne":
        return have != value
    if op == "in":
        return have in value
    if op == "not_in":
        return have not in value
    if op in ("gte", "lte", "gt", "lt"):
        try:
            have_n, value_n = float(have), float(value)
        except (TypeError, ValueError):
            return None
        return {"gte": have_n >= value_n, "lte": have_n <= value_n,
                "gt": have_n > value_n, "lt": have_n < value_n}[op]
    if op == "exists":
        return have is not None
    if op == "not_exists":
        return have is None
    return None


# context_flags this evaluator can resolve against a concrete loan fact --
# a narrow, curated overlay (2026-07-31, Workstream B of
# .claude/plans/1-no-no-this-iridescent-brooks.md). Gold cards carry
# `applicability.context_flags` (a list of string trigger flags, e.g.
# "income_type_self_employment", "DU_INCOME_RELIEF_RECEIVED",
# "loan_product_refinow") ADDITIONAL to (AND-ed onto) any all_of/any_of
# conditions -- confirmed by inspecting storage/rules/gold/data/
# rules_compiled.json: every card carrying a context_flags list also carries
# an all_of Loans.QC_Policy condition. Only self-employment is wired here
# because it's the one context_flags value this project can currently
# resolve with a real, hand-verified fact (`borrower_self_employed`). Every
# OTHER context_flags value is deliberately left unevaluated -- unchanged
# from this function's pre-existing behavior, not a regression -- per the
# disjunction-safety discipline (docs/SCENARIO-GATE-EXPERIMENT-2026-07-30.md
# / src/gates/scenario_gate.py): an undecidable condition must never be
# silently treated as satisfied or excluded, so this project only wires the
# specific narrow cases it can actually decide.
SELF_EMPLOYMENT_CONTEXT_FLAG = "income_type_self_employment"


def _evaluate_structural_applicability(applicability, facts):
    """The all_of/any_of/always evaluator -- unchanged logic, factored out
    so evaluate_applicability() can layer the context_flags check (below) on
    top without touching it."""
    if applicability.get("always"):
        return "APPLICABLE", "always: true"

    all_of = applicability.get("all_of") or []
    any_of = applicability.get("any_of") or []

    if all_of:
        results = [(c, _eval_condition(c, facts)) for c in all_of]
        false_hit = next((c for c, r in results if r is False), None)
        if false_hit:
            return "NOT_APPLICABLE", "all_of condition failed: %s %s %s" % (
                false_hit["field"], false_hit["op"], false_hit["value"])
        unknown_hit = next((c for c, r in results if r is None), None)
        if unknown_hit:
            return "UNKNOWN", "all_of condition undeterminable: %s (loan value unknown)" % unknown_hit["field"]
        return "APPLICABLE", "all_of: all conditions matched"

    if any_of:
        results = [(c, _eval_condition(c, facts)) for c in any_of]
        true_hit = next((c for c, r in results if r is True), None)
        if true_hit:
            return "APPLICABLE", "any_of condition matched: %s %s %s" % (
                true_hit["field"], true_hit["op"], true_hit["value"])
        unknown_hit = next((c for c, r in results if r is None), None)
        if unknown_hit:
            return "UNKNOWN", "any_of condition undeterminable: %s (loan value unknown)" % unknown_hit["field"]
        return "NOT_APPLICABLE", "any_of: no condition matched"

    return "APPLICABLE", "no conditions declared"


def evaluate_applicability(applicability, facts):
    """Returns ('APPLICABLE'|'NOT_APPLICABLE'|'UNKNOWN', reason:str).

    Structural (all_of/any_of/always) verdict first; if that resolves
    APPLICABLE, additionally checks the one context_flags value this
    project can currently resolve (self-employment -- see
    SELF_EMPLOYMENT_CONTEXT_FLAG above). If the structural verdict is
    already NOT_APPLICABLE/UNKNOWN, context_flags are not consulted -- that
    verdict already stands regardless.
    """
    verdict, reason = _evaluate_structural_applicability(applicability, facts)
    if verdict != "APPLICABLE":
        return verdict, reason

    context_flags = applicability.get("context_flags") or []
    if SELF_EMPLOYMENT_CONTEXT_FLAG in context_flags:
        se = facts.get("borrower_self_employed")
        if se is True:
            return "APPLICABLE", reason + "; context_flag %s matched: borrower_self_employed=True" % (
                SELF_EMPLOYMENT_CONTEXT_FLAG)
        if se is False:
            return "NOT_APPLICABLE", "context_flag %s not met: borrower_self_employed=False" % (
                SELF_EMPLOYMENT_CONTEXT_FLAG)
        return "UNKNOWN", "context_flag %s undeterminable: borrower_self_employed unknown" % (
            SELF_EMPLOYMENT_CONTEXT_FLAG)

    return verdict, reason


# ---------------------------------------------------------------------------
# pyshacl run + required-predicate extraction (mirrors run_full_ruleset_audit.py)
# ---------------------------------------------------------------------------
def load_shapes_graph():
    shapes = Graph()
    for fn in sorted(os.listdir(GOLD_BLOCKS_DIR)):
        if fn.endswith(".ttl"):
            shapes.parse(os.path.join(GOLD_BLOCKS_DIR, fn), format="turtle")
    return shapes


def required_predicates_by_shape(shapes_graph):
    """shape local-name -> set of li:<pred> tokens referenced in its sh:select body."""
    need = {}
    for s in shapes_graph.subjects(SH.targetClass, None):
        body = "".join(str(shapes_graph.value(c, SH.select) or "") for c in shapes_graph.objects(s, SH.sparql))
        preds = set(re.findall(r"li:([A-Za-z_][A-Za-z_0-9]*)", body))
        preds -= NON_LI_PREDICATES
        need[str(s).split("#")[-1]] = preds
    return need


def run_shapes(data_graph, shapes_graph):
    conforms, report, _ = validate(data_graph=data_graph, shacl_graph=shapes_graph, inference="none", advanced=True)
    fired = collections.defaultdict(list)  # shape_name -> [(message, severity_local_name)]
    for r in report.subjects(SH.resultSeverity, None):
        shape_name = str(report.value(r, SH.sourceShape)).split("#")[-1]
        severity = str(report.value(r, SH.resultSeverity)).split("#")[-1]
        message = str(report.value(r, SH.resultMessage))
        fired[shape_name].append((message, severity))
    return conforms, fired


def facts_from_graph(data_graph, loan_uri):
    facts = set()
    for _, p, _ in data_graph.triples((loan_uri, None, None)):
        name = str(p).split("#")[-1]
        if name.startswith("cite_"):
            continue
        facts.add(name)
    return facts


def main(loan_app_path, extracted_data_path, out_dir=None):
    out_dir = out_dir or DEFAULT_OUT_DIR
    os.makedirs(out_dir, exist_ok=True)

    with open(loan_app_path) as f:
        loan_app = json.load(f)
    with open(GOLD_RULES_PATH) as f:
        gold = json.load(f)
    with open(MAPPING_PATH) as f:
        mapping = json.load(f)

    # -- loan graph, via the existing, UNMODIFIED touchless_adapter.py / loan_to_rdf.py --
    extraction = adapt_touchless_to_extraction(loan_app_path, extracted_data_path)
    tmp_extraction_path = os.path.join(out_dir, "_extraction.json")
    with open(tmp_extraction_path, "w") as f:
        json.dump(extraction, f, indent=1, sort_keys=True)
    data_graph, loan_uri = build_graph(tmp_extraction_path)
    loan_facts = facts_from_graph(data_graph, loan_uri)

    # -- applicability facts, straight off the raw payload (option b) --
    # borrower_self_employed is threaded through from the already-computed
    # `extraction["facts"]` (touchless_adapter.py's own detection) rather
    # than re-derived here -- single source of truth, see
    # compute_applicability_facts()'s docstring/comment.
    borrower_se = (extraction.get("facts", {}).get("borrower_self_employed") or {}).get("value")
    appl_facts = compute_applicability_facts(loan_app, borrower_self_employed=borrower_se)
    scenario_na = load_scenario_na()

    # -- shapes + required predicates --
    shapes_graph = load_shapes_graph()
    need = required_predicates_by_shape(shapes_graph)
    conforms, fired = run_shapes(data_graph, shapes_graph)

    results = []
    status_counts = collections.Counter()
    coverage = collections.defaultdict(lambda: collections.Counter())

    for card in gold["cards"]:
        card_id = card["card_id"]
        question_code = card_id.split("::", 1)[-1] if "::" in card_id else card_id
        appl_verdict, appl_reason = evaluate_applicability(card["applicability"], appl_facts)

        for opt in card["defect_options"]:
            ct = opt["check_type"]
            exc = opt["finding"]["exception_code"]
            key = "%s||%s" % (card_id, exc)
            link = mapping.get(key)
            coverage[ct]["total"] += 1

            record = {
                "card_id": card_id, "question_code": question_code, "exception_code": exc,
                "check_type": ct, "severity": opt["finding"].get("severity"),
            }

            if link is None:
                record["status"] = "NOT_COMPILED"
                record["message"] = "no linkage entry (should not happen)"
                results.append(record)
                status_counts["NOT_COMPILED"] += 1
                coverage[ct]["unsupported"] += 1
                continue

            if link.get("unsupported"):
                record["status"] = "NOT_COMPILED"
                record["message"] = link.get("unsupported_reason", "unsupported")
                results.append(record)
                status_counts["NOT_COMPILED"] += 1
                coverage[ct]["unsupported"] += 1
                continue

            coverage[ct]["converted"] += 1

            # 2026-07-31, workstream A2: per-OPTION scenario-gate override --
            # the card-level appl_verdict below is computed once per card and
            # doesn't see individual defect_option triggers; this table is
            # keyed at (card_id, exception_code) granularity specifically to
            # catch cases where one sibling option's trigger is provably
            # false for this loan even though the card overall still applies.
            # PROVISIONAL -- see scenario_applicability_loan12607601215.json's
            # _meta.spot_check_status before trusting this beyond the demo.
            scenario_reason = scenario_na.get((card_id, exc))
            if scenario_reason is not None:
                record["status"] = "NOT_APPLICABLE"
                record["message"] = "scenario-gated (this loan): %s" % scenario_reason
                results.append(record)
                status_counts["NOT_APPLICABLE"] += 1
                continue

            if appl_verdict == "NOT_APPLICABLE":
                record["status"] = "NOT_APPLICABLE"
                record["message"] = appl_reason
                results.append(record)
                status_counts["NOT_APPLICABLE"] += 1
                continue

            if appl_verdict == "UNKNOWN":
                record["status"] = "NO_DATA"
                record["message"] = "applicability undetermined: %s" % appl_reason
                results.append(record)
                status_counts["NO_DATA"] += 1
                continue

            # 2026-07-31, workstream A0b: this check genuinely applies to the
            # loan (applicability already resolved above, not overridden
            # here), but its outcome can only be verified inside DU/EPIC/Loan
            # Delivery -- a system this project has no connection to. Gordon:
            # "we cannot call into the DU system to verify, we will simulate
            # they pass." Deliberately, acknowledged departure from "never
            # show a false clean" -- see autopass_no_system_access.json's
            # _meta for the full decision record and its explicit scope
            # limits (does NOT extend to category C's Underwriting_Type-null
            # checks -- those stay NO_DATA).
            # (Reconciled into Workstream B's copy 2026-07-31: this block
            # landed in the shared checkout concurrently with Workstream B's
            # own edits below/above it; pulled in verbatim so this file
            # doesn't regress A0b's already-landed change. No interaction
            # with Workstream B's own edits -- disjoint code paths.)
            if link.get("autopass"):
                record["status"] = "PASS"
                record["message"] = ("auto-pass: requires verification inside %s, which this "
                                      "project has no connection to (demo-scoped decision, see "
                                      "autopass_no_system_access.json)" % link.get("autopass_reason"))
                results.append(record)
                status_counts["PASS"] += 1
                continue

            # 2026-08-01: the two branches that used to live here (force
            # NO_DATA on uncurated doc_presence/doc_completeness, and on
            # every cross_doc_consistency check) are gone -- both were a
            # compile-time defect (no curated documentType / no real
            # per-check comparison logic, true for every loan) papered over
            # with a runtime-looking status. ruleset_to_shacl.py now marks
            # both cases `unsupported` at compile time instead of emitting a
            # meaningless shape, so they're already caught by the
            # `link.get("unsupported")` branch above and never reach this
            # point. See output/BAKEOFF-P0-VS-SRC-GOLD-RULESET-2026-07-31.md
            # Addendum 6.

            shape_name = link["shape_name"]
            required = need.get(shape_name, set())
            missing = required - loan_facts

            if shape_name in fired:
                messages, severities = zip(*fired[shape_name])
                if "Warning" in severities:
                    record["status"] = "NEEDS_REVIEW"
                else:
                    record["status"] = "FAIL"
                record["message"] = messages[0]
                record["fired_severity"] = severities[0]
            elif missing:
                record["status"] = "NO_DATA"
                record["message"] = "missing required field(s): %s" % ", ".join(sorted(missing))
            else:
                record["status"] = "PASS"
                record["message"] = "%s did not fire (all required data present)" % shape_name

            results.append(record)
            status_counts[record["status"]] += 1

    out = {
        "summary": {
            "loan_id": extraction["loan_id"],
            "loan_application_path": loan_app_path,
            "extracted_data_path": extracted_data_path,
            "applicability_facts": appl_facts,
            "total_checks": len(results),
            "status_counts": dict(status_counts),
            "coverage_by_check_type": {ct: dict(c) for ct, c in coverage.items()},
            "pyshacl_conforms_raw": conforms,
        },
        "results": results,
    }

    out_path = os.path.join(out_dir, "shacl_results.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)

    print("=" * 78)
    print("GOLD RULESET AUDIT (SHACL / src/shacl_pilot) -- loan %s" % extraction["loan_id"])
    print("=" * 78)
    print("checks: %d" % len(results))
    print()
    print("verdict distribution:")
    for k in ["FAIL", "NEEDS_REVIEW", "PASS", "NOT_APPLICABLE", "NO_DATA", "NOT_COMPILED"]:
        n = status_counts.get(k, 0)
        print("  %-16s %5d  (%.1f%%)" % (k, n, 100.0 * n / len(results)))
    print()
    print("coverage by check_type (converted vs unsupported):")
    for ct in sorted(coverage):
        c = coverage[ct]
        print("  %-24s converted=%-5d unsupported=%-5d" % (ct, c.get("converted", 0), c.get("unsupported", 0)))
    print()
    print("wrote: %s" % out_path)
    return out


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    out_dir_arg = sys.argv[3] if len(sys.argv) > 3 else None
    main(sys.argv[1], sys.argv[2], out_dir_arg)
