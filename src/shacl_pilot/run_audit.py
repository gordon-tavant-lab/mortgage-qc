#!/usr/bin/env python3
"""
SHACL pilot audit runner v3 — full-workbook, program-filtered (decisions 009-011).

Per loan:
  1. extract from demo/syn PDFs + MISMO XML (citations + signatures, decision 002)
  2. detect agency from the loan's own documents (1003 Loan Program line, MISMO
     MortgageType fallback) -> deterministic route lookup (decision 010/011)
  3. run the loan's FULL applicable workbook rule population (agency + generic,
     689-1,385 rules) from compiled/ruleset.json:
        mapped        -> pilot SHACL shapes (PASS / FAIL / NEEDS_REVIEW / NO_DATA)
        doc_presence  -> inventory check (doc present -> PASS; absent -> NEEDS_REVIEW)
        unmapped      -> NOT_EVALUATED (no data contract yet — never a silent pass)
  4. SHACL validation runs TWICE (determinism) on the pilot shapes
  5. reconcile FAIL/NEEDS_REVIEW findings against the answer keys — all inside
     src/ (answer_keys/loan_01_answers.md) or Gordon-authored data
     (demo/syn/Answers.md). NOTHING is read from p0/ (decision 011).

Exit 0 only if: 25/25 answer-key defects detected, no unexpected extra FAILs,
deterministic, shapes manifest verified.
"""
import glob
import json
import os
import re
import sys

from pyshacl import validate
from rdflib import Graph, Namespace

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from extract_loan import LoanExtractor          # noqa: E402
from loan_to_rdf import build_graph             # noqa: E402
from shape_manifest import current_version      # noqa: E402

SH = Namespace("http://www.w3.org/ns/shacl#")
CARO = Namespace("http://mortgage.audit.ontology/caro#")

REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
SYN = os.path.join(REPO, "demo", "syn")
ANSWERS_2_5 = os.path.join(SYN, "Answers.md")
ANSWERS_1 = os.path.join(HERE, "answer_keys", "loan_01_answers.md")
RULESET = os.path.join(HERE, "compiled", "ruleset.json")
OUT = os.path.join(HERE, "out")

LOANS = [("loan 01", "2025-0917-001"), ("loan 02", "2025-1004-FHA-002"),
         ("loan 03", "2025-1108-VA-003"), ("loan 04", "2025-1215-FRD-004"),
         ("loan 05", "2025-1122-USDA-005")]

# extras beyond the hand-authored answer key that were investigated and
# confirmed to be REAL, defensible findings (decision 007: "or each extra
# individually justified") — never add an entry here to silence a check;
# only after verifying the underlying document genuinely supports it.
JUSTIFIED_EXTRAS = {
    ("2025-1122-USDA-005", "CoBorrowerSectionCompleteShape"):
        "Verified 2026-07-29: loan 05's final 1003 has no signature line "
        "anywhere (grep confirms zero matches for 'Signat' in the document) "
        "— a real, undocumented gap the original 5-defect answer key never "
        "captured. Not a false positive; decision 015.",
}

# 1003 "Loan Program" keywords -> agency prefix (decision 010); MISMO fallback
PROGRAM_KEYWORDS = [("fannie", "O-FNM"), ("freddie", "O-FRD"), ("fha", "O-FHA"),
                    ("usda", "O-RHS"), ("rhs", "O-RHS"), ("va", "O-VA")]
MISMO_TYPE_TO_AGENCY = {"FHA": "O-FHA", "VA": "O-VA",
                        "USDARuralDevelopment": "O-RHS"}

# answer-key defect -> pilot shape mapping, in answer-key line order
EXPECTED_SHAPES = {
    "2025-0917-001": ["EmploymentStartDateShape", "TitleVestingShape",
                      "LargeDepositShape", "UndisclosedLiabilityShape",
                      "CompDistanceShape"],
    "2025-1004-FHA-002": ["Hud92900aBorrowerSigShape", "FhaCaseNumberShape",
                          "GiftEvidenceShape", "MprCompletionCertShape",
                          "AmendatoryClauseShape"],
    "2025-1108-VA-003": ["NovAfterClosingShape", "ArmDisclosureShape",
                         "TermiteInspectionShape", "LbpDisclosureShape",
                         "ResidualIncomeShape"],
    "2025-1215-FRD-004": ["LoanPurposeMismatchShape", "PayoffDiscrepancyShape",
                          "CashoutMortgageLateShape", "StaleAppraisalShape",
                          "SelfEmployedDocsShape"],
    "2025-1122-USDA-005": ["UsdaIncomeLimitShape", "UsdaEligibilityDocShape",
                           "RatioWaiverShape", "WellSepticShape",
                           "SiteValueJustificationShape"],
}

ENTITY_NEEDS = {
    "LargeDepositShape": ["bank_txns"],
    "UndisclosedLiabilityShape": ["tradelines", "urla_liabilities"],
    "CompDistanceShape": ["comps"],
}


def parse_answer_file(path):
    out, current = {}, None
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        header = re.match(r"Loan \d+ — .*\(#([\w-]+)", line)
        if header:
            current = header.group(1)
            out[current] = []
        elif current:
            out[current].append(line)
    return out


def expected_defects():
    answers = parse_answer_file(ANSWERS_1)
    answers.update(parse_answer_file(ANSWERS_2_5))
    result = {}
    for loan_id, shapes in EXPECTED_SHAPES.items():
        descs = answers.get(loan_id, [])
        if len(descs) != len(shapes):
            raise SystemExit("Answer key lists %d defects for %s; mapping has %d"
                             % (len(descs), loan_id, len(shapes)))
        result[loan_id] = list(zip(descs, shapes))
    return result


def detect_agency(extraction):
    """Agency from the loan's own documents; the audit trail records the source."""
    program = str(extraction["fields"].get("loan_program_1003", {}).get("value", ""))
    for kw, agency in PROGRAM_KEYWORDS:
        if re.search(r"\b" + kw, program, re.I):
            return agency, "1003 Loan Program: %r" % program
    mt = str(extraction["fields"].get("mismo_mortgage_type", {}).get("value", ""))
    if mt in MISMO_TYPE_TO_AGENCY:
        return MISMO_TYPE_TO_AGENCY[mt], "MISMO MortgageType: %r" % mt
    raise SystemExit("Cannot determine agency for loan %s" % extraction["loan_id"])


def shapes_graph_all():
    g = Graph()
    for path in sorted(glob.glob(os.path.join(HERE, "blocks", "*.ttl"))):
        g.parse(path, format="turtle")
    return g


def shape_metadata(shapes_graph):
    meta = {}
    for shape in shapes_graph.subjects(CARO.checkId, None):
        name = str(shape).rsplit("#", 1)[-1]
        meta[name] = {
            "check_id": str(shapes_graph.value(shape, CARO.checkId)),
            "exception": str(shapes_graph.value(shape, CARO.exceptionRef)),
            "severity": str(shapes_graph.value(shape, CARO.hasSeverity)),
            "cites": sorted(str(v) for v in shapes_graph.objects(shape, CARO.citesFields) if str(v)),
        }
    return meta


def run_validation(extraction_json):
    data, _ = build_graph(extraction_json)
    shapes = shapes_graph_all()
    _, report, _ = validate(data_graph=data, shacl_graph=shapes,
                            inference="none", advanced=True)
    findings = []
    for result in report.subjects(SH.resultSeverity, None):
        sev = report.value(result, SH.resultSeverity)
        shape = report.value(result, SH.sourceShape)
        msg = str(report.value(result, SH.resultMessage))
        name = str(shape).rsplit("#", 1)[-1]
        status = "NEEDS_REVIEW" if sev == SH.Warning else "FAIL"
        findings.append((name, status, msg))
    return sorted(findings)


def data_present(shape_name, meta, extraction):
    for fam in ENTITY_NEEDS.get(shape_name, []):
        if not extraction["entities"].get(fam):
            return False
    for fname in meta.get("cites", []):
        if fname and fname not in extraction["fields"] and fname not in extraction["facts"]:
            return False
    return True


def citations_for(extraction, field_names):
    cites = []
    for fname in field_names:
        item = extraction["fields"].get(fname) or extraction["facts"].get(fname)
        if item:
            c = item["citation"]
            cites.append("%s p.%s: \"%s\"" % (c["doc_name"], c["page"], c["snippet"][:90]))
    return cites


def workbook_stats(rules, agency, extraction, mapped_status):
    """Run the applicable workbook population; returns (counts, per_block)."""
    from collections import Counter, defaultdict
    counts = Counter()
    per_block = defaultdict(Counter)
    docs = set(extraction["docs_present"])
    for rule in rules:
        if rule["agency"] not in (agency, "GENERIC"):
            counts["EXCLUDED_PROGRAM"] += 1
            continue
        if rule["eval_class"] == "doc_presence":
            status = "PASS" if rule["eval_target"] in docs else "NEEDS_REVIEW"
        elif rule["eval_class"] == "mapped":
            status = mapped_status.get(rule["eval_target"], "NOT_EVALUATED")
        else:
            status = "NOT_EVALUATED"
        counts[status] += 1
        per_block[rule["block"]][status] += 1
    return counts, per_block


def main():
    version, combo = current_version()
    with open(RULESET) as f:
        ruleset = json.load(f)
    rules = ruleset["rules"]
    with open(os.path.join(HERE, "routes.json")) as f:
        routes = json.load(f)

    print("=" * 78)
    print("SHACL PILOT AUDIT v3 — full workbook, program-filtered")
    print("shapes version %d (%s) | ruleset %d rules (sha %s) | %d discarded excluded"
          % (version, combo[:12], ruleset["rules_total"],
             ruleset["ruleset_sha256"][:12], ruleset["discarded_excluded"]))
    print("=" * 78)

    expected = expected_defects()
    catalog = shape_metadata(shapes_graph_all())
    total_expected = total_detected = 0
    all_extras, justified_extras, nondeterministic = [], [], []

    for folder_name, loan_id in LOANS:
        extraction = LoanExtractor(os.path.join(SYN, folder_name)).run()
        assert extraction["loan_id"] == loan_id
        ex_path = os.path.join(OUT, "loan_%s_extraction.json" % folder_name[-2:])
        with open(ex_path, "w") as f:
            json.dump(extraction, f, indent=1, sort_keys=True)

        agency, agency_evidence = detect_agency(extraction)
        route_id = routes["selection_by_agency"][agency]
        route = routes["routes"][route_id]

        run1 = run_validation(ex_path)
        run2 = run_validation(ex_path)
        if run1 != run2:
            nondeterministic.append(loan_id)
        fired = {name: status for name, status, _ in run1}

        # pilot-check statuses (also feeds mapped workbook rules)
        mapped_status = {}
        pilot_counts = {"FAIL": 0, "NEEDS_REVIEW": 0, "PASSED": 0, "NO_DATA": 0}
        for name, meta in catalog.items():
            if name in fired:
                status = fired[name]
            elif data_present(name, meta, extraction):
                status = "PASSED"
            else:
                status = "NO_DATA"
            mapped_status[name] = status if status != "PASSED" else "PASS"
            pilot_counts[status if status != "PASS" else "PASSED"] += 1

        wb_counts, per_block = workbook_stats(rules, agency, extraction, mapped_status)
        applicable = sum(v for k, v in wb_counts.items() if k != "EXCLUDED_PROGRAM")

        print("\n" + "-" * 70)
        print("LOAN %s  (%s)" % (loan_id, folder_name))
        print("  agency: %s  [%s]" % (agency, agency_evidence))
        print("  route: %s (%s)  determinism: %s"
              % (route_id, route["title"],
                 "PASS" if loan_id not in nondeterministic else "FAIL"))
        print("  WORKBOOK RULES: %d total | %d excluded (other program) | %d RUN"
              % (len(rules), wb_counts["EXCLUDED_PROGRAM"], applicable))
        print("    PASS: %d | FAIL: %d | NEEDS_REVIEW: %d | NOT_EVALUATED: %d"
              % (wb_counts["PASS"], wb_counts["FAIL"],
                 wb_counts["NEEDS_REVIEW"], wb_counts["NOT_EVALUATED"]))
        print("    per block (run/pass/fail/needs_review/not_evaluated):")
        for block in sorted(per_block):
            c = per_block[block]
            run_n = sum(c.values())
            print("      %-34s %4d / %3d / %2d / %3d / %4d"
                  % (block, run_n, c["PASS"], c["FAIL"],
                     c["NEEDS_REVIEW"], c["NOT_EVALUATED"]))
        print("  PILOT FIELD-MAPPED CHECKS (25): PASSED %d | FAIL %d | NEEDS_REVIEW %d | NO_DATA %d"
              % (pilot_counts["PASSED"], pilot_counts["FAIL"],
                 pilot_counts["NEEDS_REVIEW"], pilot_counts["NO_DATA"]))
        for name, status, msg in run1:
            meta = catalog.get(name, {})
            print("   [%s] %s (%s, %s)" % (status, name, meta.get("check_id"),
                                           meta.get("exception")))
            print("      %s" % msg)
            for cite_line in citations_for(extraction, meta.get("cites", [])):
                print("      cite: %s" % cite_line)

        print("  reconciliation vs answer key:")
        missed = []
        for desc, shape_name in expected[loan_id]:
            ok = shape_name in fired
            total_expected += 1
            total_detected += 1 if ok else 0
            if not ok:
                missed.append(shape_name)
            print("   %s %s -> %s" % ("DETECTED" if ok else "MISSED  ",
                                      desc[:58], shape_name))
        extras = sorted(n for n, s in fired.items()
                        if s == "FAIL" and n not in {s2 for _, s2 in expected[loan_id]})
        for e in extras:
            justification = JUSTIFIED_EXTRAS.get((loan_id, e))
            if justification:
                justified_extras.append((loan_id, e))
                print("   EXTRA(justified) %s -- %s" % (e, justification))
            else:
                all_extras.append((loan_id, e))
                print("   EXTRA    unexplained FAIL from %s" % e)

    print("\n" + "=" * 78)
    ok = (total_detected == total_expected and not all_extras and not nondeterministic)
    print("SUMMARY: %d/%d answer-key defects detected | unexplained extra FAILs: %d "
          "| justified extra FAILs: %d | non-deterministic: %d"
          % (total_detected, total_expected, len(all_extras),
             len(justified_extras), len(nondeterministic)))
    print("Ruleset sha %s + shapes version %d (%s) recorded for audit trail."
          % (ruleset["ruleset_sha256"][:12], version, combo[:12]))
    print("OVERALL: %s" % ("PASS" if ok else "FAIL"))
    print("=" * 78)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
