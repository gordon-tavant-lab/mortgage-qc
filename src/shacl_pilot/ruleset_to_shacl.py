#!/usr/bin/env python3
"""
ruleset_to_shacl.py — deterministic (NO LLM) compiler: gold rule set
(storage/rules/gold/data/rules_compiled.json, 266 cards / ~1,105 defect_options)
-> SHACL shapes (src/shacl_pilot/blocks/gold/*.ttl) + a linkage table
(src/shacl_pilot/blocks/gold/gold_shape_mapping.json).

Built for the p0/qc_engine-vs-src/shacl_pilot bake-off
(.claude/plans/1-no-no-this-iridescent-brooks.md, 2026-07-31). This is the
src/shacl_pilot side of the gold-ruleset converter; `p0/qc_engine/compiler/
import_gold_ruleset.py` is the symmetric p0-side converter, built with the
SAME judgment calls (see the mapping table in the plan §2 and the docstring
of each `build_*_shape` function below for the exact rationale per
check_type).

Per check_type (mirrors the plan's mapping table exactly):
  doc_presence / doc_completeness  -> sh:select testing `?this li:docs_present
                                       ?d . FILTER(?d = "<exception_code>")`.
                                       li:docs_present is never populated by
                                       loan_to_rdf.py for ANY loan today (grep
                                       confirmed) and Touchless gives no doc
                                       inventory for this loan either -- these
                                       shapes are honest, permanent NO_DATA on
                                       this data source. Not a bug.
  threshold_eligibility / computation (LTV/DTI subset ONLY) -> a numeric
                                       FILTER against li:ltv / li:dti_ratio.
                                       See LTV_DTI_THRESHOLDS below: this is a
                                       small, HAND-CURATED allowlist, not a
                                       regex parser. 31 of 266 cards' defect
                                       descriptions mention LTV/DTI; on manual
                                       read, 28 of the 31 bundle the ratio
                                       into a compound, multi-condition, or
                                       true-recomputation finding (program
                                       eligibility like RefiNow/HomeReady,
                                       co-signer rules, "or" between two
                                       numbers, or genuine "recompute LTV from
                                       loan amount / appraised value" formulas
                                       we don't have the inputs for) -- reducing
                                       those to a single FILTER would silently
                                       misrepresent the rule (CLAUDE.md's
                                       grounding-never-invents-content rule).
                                       Only the 3 with one clean, unambiguous
                                       number and a plain "exceeds" comparator
                                       were converted. All other LTV/DTI-
                                       keyword and non-LTV/DTI-keyword
                                       threshold_eligibility/computation cards
                                       are logged unsupported, not fabricated.
  cross_doc_consistency            -> sh:select over the closest-matching
                                       entity family (keyword heuristic, see
                                       ENTITY_FAMILY_KEYWORDS) -- all 5 entity
                                       families are empty for this loan
                                       (Touchless doesn't populate them), so
                                       every one of these honestly resolves
                                       NO_DATA. Which family is picked doesn't
                                       change that outcome; it's chosen for
                                       shape-name traceability only.
  scripted_review                  -> a shape whose sh:select ALWAYS returns
                                       exactly one row for $this (no
                                       data-dependent FILTER -- it's inherently
                                       "needs a human"), with sh:severity
                                       sh:Warning set AT THE NODESHAPE LEVEL.
                                       Verified empirically (see below) that
                                       pyshacl only surfaces sh:resultSeverity
                                       when sh:severity sits on the NodeShape
                                       itself, NOT inside the sh:sparql blank
                                       node (the latter silently defaults back
                                       to Violation) -- do not move it back.
  routing_context                  -> no shape (0 defect_options carry this
                                       type in the gold set; nothing to skip).
  date_window / list_screening /
  reverification                   -> NOT converted. Logged unsupported.
                                       Deliberate shared scope limit with the
                                       p0/qc_engine side (plan §"Important
                                       scope-setting"), not a gap to fill.

Applicability (Loans.QC_Policy / LoanPurposeType / PropertyType /
Underwriting_Type / LoanType / AddressState) is NOT baked into these shapes.
Per the plan's option (b), it's evaluated in Python by run_gold_ruleset_audit.py
directly off the raw Touchless payload, before pyshacl ever runs -- exactly
the pattern run_full_ruleset_audit.py already uses for program gating. That
keeps this file a pure check_type -> shape converter and avoids extending the
shared touchless_adapter.py / loan_to_rdf.py files.

USAGE:  python3 ruleset_to_shacl.py     (writes blocks/gold/*.ttl + gold_shape_mapping.json)
"""
import collections
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
GOLD_RULES_PATH = os.path.join(REPO_ROOT, "storage", "rules", "gold", "data", "rules_compiled.json")
OUT_DIR = os.path.join(HERE, "blocks", "gold")
MAPPING_PATH = os.path.join(OUT_DIR, "gold_shape_mapping.json")

TURTLE_PREFIX_BLOCK = """# AUTOGENERATED by ruleset_to_shacl.py -- do not hand-edit, regenerate instead.
@prefix sh:   <http://www.w3.org/ns/shacl#> .
@prefix li:   <http://mortgage.audit.ontology/loan-instance#> .
@prefix caro: <http://mortgage.audit.ontology/caro#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .

li:PilotPrefixesGold a owl:Ontology ;
    sh:declare [ sh:prefix "li" ;
                 sh:namespace "http://mortgage.audit.ontology/loan-instance#"^^xsd:anyURI ] ,
               [ sh:prefix "xsd" ;
                 sh:namespace "http://www.w3.org/2001/XMLSchema#"^^xsd:anyURI ] .
"""

# ---------------------------------------------------------------------------
# Hand-curated LTV/DTI threshold allowlist. See the module docstring: this is
# NOT a regex parser over free text -- every gold threshold_eligibility /
# computation defect_option whose description mentions LTV or DTI (31 of 266
# cards) was read by hand; only these 3 reduce to one clean number with an
# unambiguous "exceeds" comparator and no other unverifiable precondition
# folded into the same sentence.
# ---------------------------------------------------------------------------
LTV_DTI_THRESHOLDS = {
    ("PC::O-FNM-15420", "O-FNM-54327"): {
        "field": "dti_ratio", "op": ">", "threshold": 65.0,
        "note": "RefiNow DTI ratio cap (65%). RefiNow-program membership is not "
                "independently verified on this loan -- applied as a general DTI "
                "threshold; a false positive is possible on a non-RefiNow loan "
                "whose DTI happens to exceed 65%.",
    },
    ("PC::O-FNM-15420", "O-FNM-54328"): {
        "field": "ltv", "op": ">", "threshold": 95.0,
        "note": "Maximum LTV/CLTV/HCLTV ratio of 95% for a RefiNow with a "
                "non-occupant borrower. Only base LTV is checked -- CLTV/HCLTV "
                "are not populated by touchless_adapter.py. RefiNow/non-occupant "
                "preconditions not independently verified.",
    },
    ("PC::O-FNM-16190", "O-FNM-56234"): {
        "field": "ltv", "op": ">", "threshold": 95.0,
        "note": "Maximum LTV of 95% for a HomeReady loan using sweat equity. "
                "HomeReady/sweat-equity preconditions not independently verified "
                "-- applied as a general LTV threshold.",
    },
}
FIELD_PREDICATE = {"ltv": "li:ltv", "dti_ratio": "li:dti_ratio"}
LTV_DTI_KEYWORD_RE = re.compile(r"loan-to-value|\bltv\b|debt-to-income|\bdti\b", re.IGNORECASE)

# ---------------------------------------------------------------------------
# cross_doc_consistency -> nearest entity family, by keyword. All 5 families
# are empty on this loan regardless, so this only affects shape-name
# traceability, never the verdict.
# ---------------------------------------------------------------------------
ENTITY_FAMILY_KEYWORDS = [
    (("bank statement", "deposit", "large deposit", "reserve", "asset"), ("bank_txns", "li:hasBankTransaction")),
    (("credit report", "tradeline", "liability", "debt", "undisclosed"), ("urla_liabilities", "li:hasUrlaLiability")),
    (("appraisal", "comparable", "comp report", "adjustment"), ("comps", "li:hasAppraisalComparable")),
    (("verification of mortgage", "vom", "mortgage rating", "payment history"), ("vom_rows", "li:hasVomRow")),
]
DEFAULT_ENTITY_FAMILY = ("bank_txns", "li:hasBankTransaction")

UNSUPPORTED_ALWAYS = {
    "date_window": "out of scope for this experiment (shared scope limit with p0/qc_engine side, per bake-off plan)",
    "list_screening": "needs a reference-list dataset (e.g. OFAC/GSA) neither engine has for this experiment",
    "reverification": "needs third-party re-pull data absent from the Touchless payload",
}


def slugify(s):
    return re.sub(r"[^A-Za-z0-9_]", "_", str(s))


def tesc(s):
    """Turtle string literal escape."""
    return str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").replace("\r", " ")


def entity_family_for(description):
    d = (description or "").lower()
    for keywords, family in ENTITY_FAMILY_KEYWORDS:
        if any(k in d for k in keywords):
            return family
    return DEFAULT_ENTITY_FAMILY


def build_doc_shape(shape_name, card_id, category, exc, check_type, finding):
    sev = finding.get("severity", "")
    desc = finding.get("description", "") or ""
    slug = exc  # deterministic; never present in li:docs_present (see docstring)
    msg = "[%s / %s / %s] %s" % (card_id, exc, check_type, desc)
    return """### %s -- %s -- %s / %s
li:%s a sh:NodeShape ;
    sh:targetClass li:LoanInstance ;
    caro:goldCardId "%s" ; caro:goldExceptionCode "%s" ;
    caro:goldCheckType "%s" ; caro:blockRef "%s" ; caro:hasSeverity "%s" ;
    sh:sparql [ a sh:SPARQLConstraint ; sh:prefixes li:PilotPrefixesGold ;
        sh:message "%s" ;
        sh:select \"\"\"SELECT $this WHERE {
            $this li:docs_present ?__doc .
            FILTER(?__doc = "%s") }\"\"\" ] .
""" % (shape_name, check_type, card_id, exc, shape_name, tesc(card_id), tesc(exc),
       check_type, tesc(slugify(category).lower()), tesc(sev), tesc(msg), tesc(slug))


def build_threshold_shape(shape_name, card_id, category, exc, check_type, finding, curated):
    field = curated["field"]
    op = curated["op"]
    thr = curated["threshold"]
    pred = FIELD_PREDICATE[field]
    sev = finding.get("severity", "")
    desc = finding.get("description", "") or ""
    msg = "[%s / %s / %s] %s (this loan's %s = ${?__val})" % (card_id, exc, check_type, desc, field)
    return """### %s -- %s -- %s / %s
# curation note: %s
li:%s a sh:NodeShape ;
    sh:targetClass li:LoanInstance ;
    caro:goldCardId "%s" ; caro:goldExceptionCode "%s" ;
    caro:goldCheckType "%s" ; caro:blockRef "%s" ; caro:hasSeverity "%s" ;
    caro:goldNote "%s" ;
    sh:sparql [ a sh:SPARQLConstraint ; sh:prefixes li:PilotPrefixesGold ;
        sh:message "%s" ;
        sh:select \"\"\"SELECT $this ?__val WHERE {
            $this %s ?__val .
            FILTER(?__val %s %s) }\"\"\" ] .
""" % (shape_name, check_type, card_id, exc, tesc(curated["note"]), shape_name,
       tesc(card_id), tesc(exc), check_type, tesc(slugify(category).lower()), tesc(sev),
       tesc(curated["note"]), tesc(msg), pred, op, thr)


def build_cross_doc_shape(shape_name, card_id, category, exc, check_type, finding, family, pred):
    sev = finding.get("severity", "")
    desc = finding.get("description", "") or ""
    msg = "[%s / %s / %s] %s (entity family: %s)" % (card_id, exc, check_type, desc, family)
    return """### %s -- %s -- %s / %s -- entity family: %s
li:%s a sh:NodeShape ;
    sh:targetClass li:LoanInstance ;
    caro:goldCardId "%s" ; caro:goldExceptionCode "%s" ;
    caro:goldCheckType "%s" ; caro:blockRef "%s" ; caro:hasSeverity "%s" ;
    sh:sparql [ a sh:SPARQLConstraint ; sh:prefixes li:PilotPrefixesGold ;
        sh:message "%s" ;
        sh:select \"\"\"SELECT $this WHERE {
            $this %s ?__row . }\"\"\" ] .
""" % (shape_name, check_type, card_id, exc, family, shape_name, tesc(card_id), tesc(exc),
       check_type, tesc(slugify(category).lower()), tesc(sev), tesc(msg), pred)


def build_scripted_review_shape(shape_name, card_id, category, exc, check_type, finding):
    sev = finding.get("severity", "")
    desc = finding.get("description", "") or ""
    msg = "[%s / %s / %s] REQUIRES_HUMAN_REVIEW -- %s" % (card_id, exc, check_type, desc)
    # sh:severity MUST be on the NodeShape itself, not inside the sh:sparql
    # blank node -- verified empirically against pyshacl 0.40.1 (a copy set
    # only inside the blank node silently reports Violation instead).
    return """### %s -- %s -- %s / %s
li:%s a sh:NodeShape ;
    sh:targetClass li:LoanInstance ;
    sh:severity sh:Warning ;
    caro:goldCardId "%s" ; caro:goldExceptionCode "%s" ;
    caro:goldCheckType "%s" ; caro:blockRef "%s" ; caro:hasSeverity "%s" ;
    sh:sparql [ a sh:SPARQLConstraint ; sh:prefixes li:PilotPrefixesGold ;
        sh:message "%s" ;
        sh:select \"\"\"SELECT $this WHERE { }\"\"\" ] .
""" % (shape_name, check_type, card_id, exc, shape_name, tesc(card_id), tesc(exc),
       check_type, tesc(slugify(category).lower()), tesc(sev), tesc(msg))


def main():
    with open(GOLD_RULES_PATH) as f:
        gold = json.load(f)
    cards = gold["cards"]

    os.makedirs(OUT_DIR, exist_ok=True)

    mapping = {}
    counts = collections.Counter()
    shape_seq = 0

    doc_bodies = []
    threshold_bodies = []
    cross_doc_bodies = []
    scripted_bodies = []

    for card in cards:
        card_id = card["card_id"]
        category = card["category"]
        for opt in card["defect_options"]:
            ct = opt["check_type"]
            finding = opt["finding"]
            exc = finding["exception_code"]
            key = "%s||%s" % (card_id, exc)
            counts[(ct, "total")] += 1

            if ct in ("doc_presence", "doc_completeness"):
                shape_seq += 1
                shape_name = "GoldDoc_%04d_%s" % (shape_seq, slugify(exc)[:44])
                doc_bodies.append(build_doc_shape(shape_name, card_id, category, exc, ct, finding))
                mapping[key] = {
                    "card_id": card_id, "exception_code": exc, "check_type": ct,
                    "unsupported": False, "shape_name": shape_name, "file": "gold_doc_presence.ttl",
                }
                counts[(ct, "converted")] += 1

            elif ct in ("threshold_eligibility", "computation"):
                desc = finding.get("description", "") or ""
                has_kw = bool(LTV_DTI_KEYWORD_RE.search(desc))
                curated = LTV_DTI_THRESHOLDS.get((card_id, exc))
                if has_kw and curated:
                    shape_seq += 1
                    shape_name = "GoldThresh_%04d_%s" % (shape_seq, slugify(exc)[:44])
                    threshold_bodies.append(build_threshold_shape(shape_name, card_id, category, exc, ct, finding, curated))
                    mapping[key] = {
                        "card_id": card_id, "exception_code": exc, "check_type": ct,
                        "unsupported": False, "shape_name": shape_name, "file": "gold_threshold.ttl",
                        "field": curated["field"], "op": curated["op"], "threshold": curated["threshold"],
                        "note": curated["note"],
                    }
                    counts[(ct, "converted")] += 1
                else:
                    if not has_kw:
                        reason = "check_type is %s but description does not mention LTV or DTI -- out of scope for this experiment's LTV/DTI-only slice" % ct
                    else:
                        reason = ("description mentions LTV/DTI but does not reduce to one clean, unambiguous "
                                  "numeric threshold -- compound/multi-condition wording (program eligibility, "
                                  "co-signer rules, an 'or' between two numbers, or a genuine multi-input "
                                  "recomputation formula) that a single FILTER would misrepresent; hand-reviewed "
                                  "and deliberately left unconverted rather than fabricated (see module docstring)")
                    mapping[key] = {
                        "card_id": card_id, "exception_code": exc, "check_type": ct,
                        "unsupported": True, "shape_name": None, "unsupported_reason": reason,
                    }
                    counts[(ct, "unsupported")] += 1

            elif ct == "cross_doc_consistency":
                shape_seq += 1
                family, pred = entity_family_for(finding.get("description", ""))
                shape_name = "GoldCross_%04d_%s" % (shape_seq, slugify(exc)[:44])
                cross_doc_bodies.append(build_cross_doc_shape(shape_name, card_id, category, exc, ct, finding, family, pred))
                mapping[key] = {
                    "card_id": card_id, "exception_code": exc, "check_type": ct,
                    "unsupported": False, "shape_name": shape_name, "file": "gold_cross_doc.ttl",
                    "entity_family": family,
                }
                counts[(ct, "converted")] += 1

            elif ct == "scripted_review":
                shape_seq += 1
                shape_name = "GoldReview_%04d_%s" % (shape_seq, slugify(exc)[:44])
                scripted_bodies.append(build_scripted_review_shape(shape_name, card_id, category, exc, ct, finding))
                mapping[key] = {
                    "card_id": card_id, "exception_code": exc, "check_type": ct,
                    "unsupported": False, "shape_name": shape_name, "file": "gold_scripted_review.ttl",
                }
                counts[(ct, "converted")] += 1

            elif ct == "routing_context":
                mapping[key] = {
                    "card_id": card_id, "exception_code": exc, "check_type": ct,
                    "unsupported": True, "shape_name": None,
                    "unsupported_reason": "routing_context sets a context flag and raises no findings itself -- no shape by design",
                }
                counts[(ct, "unsupported")] += 1

            elif ct in UNSUPPORTED_ALWAYS:
                mapping[key] = {
                    "card_id": card_id, "exception_code": exc, "check_type": ct,
                    "unsupported": True, "shape_name": None,
                    "unsupported_reason": UNSUPPORTED_ALWAYS[ct],
                }
                counts[(ct, "unsupported")] += 1

            else:
                mapping[key] = {
                    "card_id": card_id, "exception_code": exc, "check_type": ct,
                    "unsupported": True, "shape_name": None,
                    "unsupported_reason": "unrecognized check_type %r" % ct,
                }
                counts[(ct, "unsupported")] += 1

    def write_file(name, header_comment, bodies):
        path = os.path.join(OUT_DIR, name)
        with open(path, "w") as f:
            f.write("# %s\n" % header_comment)
            f.write(TURTLE_PREFIX_BLOCK)
            f.write("\n")
            f.write("\n".join(bodies))
            f.write("\n")
        return path

    written = []
    written.append(write_file("gold_doc_presence.ttl",
        "Block: GOLD doc_presence/doc_completeness shapes (autogenerated)", doc_bodies))
    written.append(write_file("gold_threshold.ttl",
        "Block: GOLD threshold_eligibility/computation (LTV/DTI subset) shapes (autogenerated)", threshold_bodies))
    written.append(write_file("gold_cross_doc.ttl",
        "Block: GOLD cross_doc_consistency shapes (autogenerated)", cross_doc_bodies))
    written.append(write_file("gold_scripted_review.ttl",
        "Block: GOLD scripted_review shapes (autogenerated, sh:severity sh:Warning)", scripted_bodies))

    with open(MAPPING_PATH, "w") as f:
        json.dump(mapping, f, indent=1, sort_keys=True)

    # --- summary ---
    total = sum(v for (ct, kind), v in counts.items() if kind == "total")
    converted = sum(v for (ct, kind), v in counts.items() if kind == "converted")
    unsupported = sum(v for (ct, kind), v in counts.items() if kind == "unsupported")
    print("=" * 78)
    print("ruleset_to_shacl.py -- gold rule set -> SHACL shapes")
    print("=" * 78)
    print("cards: %d   defect_options: %d" % (len(cards), total))
    print("shapes written: %d  (%d converted, %d logged unsupported)" % (shape_seq, converted, unsupported))
    print()
    by_ct = collections.defaultdict(lambda: [0, 0])
    for (ct, kind), v in counts.items():
        idx = 0 if kind == "converted" else (1 if kind == "unsupported" else None)
        if idx is not None:
            by_ct[ct][idx] += v
    print("%-24s %10s %12s" % ("check_type", "converted", "unsupported"))
    for ct in sorted(by_ct):
        c, u = by_ct[ct]
        print("%-24s %10d %12d" % (ct, c, u))
    print()
    print("files written:")
    for p in written:
        print("  " + p)
    print("  " + MAPPING_PATH)
    return mapping, counts


if __name__ == "__main__":
    main()
