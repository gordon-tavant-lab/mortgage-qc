#!/usr/bin/env python3
"""
AMQ workbook compiler — Layer 1 (mechanical, deterministic, no LLM).

Compiles the full Post-Closing AMQ CSV (5,520 rows) into a program-filterable
ruleset of (question_code, exception_name) rules:

  * agency classification from the Question Code prefix:
      O-FNM- / O-FHA- / O-VA- / O-FRD- / O-RHS-  -> agency-specific
      anything else (O-CFPB-, O-CNTL-, URLA, DVS codes, ...) -> GENERIC
      (GENERIC rules run for every program; agency rules run only for their program)
  * block assignment: AMQ "Question Category Name" -> Olav block_id, validated
    against docs/research/olav-demo-yaml/blocks_manifest.json
  * evaluability class (the honest part):
      mapped        -> a hand-mapped SHACL shape exists (field-level check)
      doc_presence  -> exception text says a mappable document is "not in file /
                       missing / not provided" -> auto-compiled inventory check
      unmapped      -> applicable but NO data contract yet; runtime reports
                       NOT_EVALUATED, never a silent pass
  * "Discarded" category rules are excluded (workbook-retired), counted.

Layer 2 (future, decision 006/008): an LLM-assisted compile pass maps each
unmapped rule's text -> required docs/fields -> generated SHACL, SME signs off,
hash-versioned. LLM at CONFIG time only — runtime stays deterministic.

USAGE:  python3 amq_compiler.py          (writes compiled/ruleset.json)
"""
import csv
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
CSV_PATH = os.path.join(REPO, "src", "doc",
                        "PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv")
BLOCKS_MANIFEST = os.path.join(REPO, "docs", "research", "olav-demo-yaml",
                               "blocks_manifest.json")
OUT_DIR = os.path.join(HERE, "compiled")

AGENCIES = ["O-FNM", "O-FHA", "O-VA", "O-FRD", "O-RHS"]

# AMQ "Question Category Name" -> Olav block_id (Image #2 / blocks_manifest.json)
CATEGORY_TO_BLOCK = {
    "Application": "application-verification",
    "Fannie Mae Form 1033": "appraisal-form-1033",
    "Assets": "asset-verification",
    "Certification, Endorsement, and Delivery": "certification-delivery",
    "Closing": "closing-documents-review",
    "ATR-QM": "compliance-review",
    "Credit - Liabilities": "credit-liabilities-review",
    "Data Validation Svc-DVS": "data-validation-services",
    "EPD": "epd-review",
    "Income": "income-verification",
    "Information Integrity": "information-integrity",
    "Insurance": "insurance-review",
    "Loan Documents": "loan-documents-review",
    "Product Specific": "product-specific-check",
    "Property - Appraisal": "property-appraisal-review",
    "Underwriting": "underwriting-review",
}

# hand-mapped field-level shapes (the 25 pilot checks + Bucket-B additions),
# keyed by EXCEPTION CODE (not question code — question codes collide: e.g.
# O-FHA-15293 is shared by two different (question,exception) rules, rows 20
# and 29 of the AMQ CSV; exception codes are unique per row).
MAPPED_SHAPES = {
    "EmploymentStartDateShape": {"block": "application-verification", "amq_exception_codes": []},
    "TitleVestingShape": {"block": "application-verification", "amq_exception_codes": []},
    "FhaCaseNumberShape": {"block": "application-verification", "amq_exception_codes": []},
    "Hud92900aBorrowerSigShape": {"block": "application-verification", "amq_exception_codes": []},
    "LoanPurposeMismatchShape": {"block": "application-verification", "amq_exception_codes": []},
    "LbpDisclosureShape": {"block": "application-verification", "amq_exception_codes": []},
    "ArmDisclosureShape": {"block": "application-verification", "amq_exception_codes": []},
    # decision 015 (Bucket B): co-borrower/Additional-Borrower section
    # completeness — 5 agency variants of "Additional Borrower form not fully
    # completed" (rows 20/21/22/23/24) + FHA's "sections... not signed by all
    # parties" (row 29), all resolved by the same real-data check.
    "CoBorrowerSectionCompleteShape": {"block": "application-verification",
        "amq_exception_codes": ["O-FHA-58072", "O-FNM-58197", "O-FRD-58201",
                                "O-RHS-58247", "O-VA-58305", "O-FHA-54281"]},
    # decision 018 (Assets-triage follow-up): O-FRD-50451 verified byte-for-byte
    # identical condition text to O-FNM-00215 (row 218 vs 219) — safe to wire.
    # O-FHA-50677-1 tests the same failure mode (undocumented large deposit
    # over ~50% of income) worded for FHA ("adjusted income", "new accounts");
    # wired with the caveat that our check doesn't separately test new-account
    # deposits or distinguish "adjusted" vs "qualifying" income bases.
    # REJECTED after verification (see decision 018): O-FRD-58101 tests source-
    # ACCEPTABILITY (income/gift/eligible-asset category), a materially
    # different question than mere presence of documentation — wiring it here
    # would risk false negatives, not just imprecision.
    "LargeDepositShape": {"block": "asset-verification",
        "amq_exception_codes": ["O-FNM-00215", "O-FRD-50451", "O-FHA-50677-1"]},
    # decision 017 (Assets-block triage, G135): row 177, "No, proof of transfer
    # not provided" — the same fact (gift_transfer_evidence_in_file) already
    # extracted and checked for the FHA gift-letter rule now also covers RHS.
    "GiftEvidenceShape": {"block": "asset-verification",
        "amq_exception_codes": ["O-RHS-02772"]},
    "UndisclosedLiabilityShape": {"block": "credit-liabilities-review", "amq_exception_codes": []},
    "CashoutMortgageLateShape": {"block": "credit-liabilities-review", "amq_exception_codes": []},
    "CompDistanceShape": {"block": "property-appraisal-review", "amq_exception_codes": []},
    "MprCompletionCertShape": {"block": "property-appraisal-review", "amq_exception_codes": []},
    "TermiteInspectionShape": {"block": "property-appraisal-review", "amq_exception_codes": []},
    "StaleAppraisalShape": {"block": "property-appraisal-review", "amq_exception_codes": []},
    "WellSepticShape": {"block": "property-appraisal-review", "amq_exception_codes": []},
    "SiteValueJustificationShape": {"block": "property-appraisal-review", "amq_exception_codes": []},
    "UsdaEligibilityDocShape": {"block": "property-appraisal-review", "amq_exception_codes": []},
    "ResidualIncomeShape": {"block": "underwriting-review", "amq_exception_codes": []},
    "RatioWaiverShape": {"block": "underwriting-review", "amq_exception_codes": []},
    # decision 025 (income-verification triage follow-up): O-VA-00364 (row 2487)
    # and O-FHA-02293 (row 2410) both verified as the same real condition —
    # missing YTD P&L / balance sheet for a self-employed borrower.
    "SelfEmployedDocsShape": {"block": "income-verification",
        "amq_exception_codes": ["O-VA-00364", "O-FHA-02293"]},
    "PayoffDiscrepancyShape": {"block": "closing-documents-review", "amq_exception_codes": []},
    "NovAfterClosingShape": {"block": "certification-delivery", "amq_exception_codes": []},
    "AmendatoryClauseShape": {"block": "product-specific-check", "amq_exception_codes": []},
    "UsdaIncomeLimitShape": {"block": "product-specific-check", "amq_exception_codes": []},
}

# decision 016 (Bucket C): rules requiring an external live-lookup data
# source (not derivable from any loan document) are excluded from this
# document-extraction PoC entirely — not compiled, not counted as YELLOW/RED.
# Keyed by exception_code. Revisit as a distinct integration decision later.
DISCARDED_EXTERNAL_LOOKUP_EXCEPTION_CODES = {
    "O-FHA-00030",  # NMLS originator-license registry check (AMQ row 68)
}

# decision 024 (doc_presence classifier fix, after independent discovery in
# three parallel block triages — decisions 019/020/023): the ORIGINAL
# NOT_IN_FILE_RE/DOC_KEYWORDS classifier had two real bugs, both proven
# against actual AMQ rows, not hypothetical:
#   1. No word boundaries: r"credit report" matched inside "credit reporTED"
#      (a completely different word) — O-FNM-00200's exc_desc "written
#      explanation... were NOT PROVIDED" false-matched via this, while its
#      byte-for-byte twin O-VA-00143 (no "not provided"/"missing" at all)
#      correctly stayed unmapped. Fixed below with \b boundaries.
#   2. No proximity requirement: "not provided"/"missing" anywhere in a long
#      compound sentence matched a doc-type keyword anywhere else in that same
#      sentence, even when the absence being described was a specific
#      exhibit/comment/analysis WITHIN a document that verifiably exists, not
#      the whole document (property-appraisal-review: 33 of 35 auto-tagged
#      rows were this pattern — "appraisal" appears somewhere, an absence-word
#      appears somewhere else, entirely unrelated to each other). Fixed below
#      by requiring the absence-phrase and the doc-keyword to occur within a
#      bounded character window of each other, AND by excluding matches whose
#      surrounding text contains narrative/judgment qualifiers (adequate,
#      sufficient, acceptable, analysis, comment, support, correctly,
#      properly, satisfactory) — those signal a commentary/adequacy condition,
#      not a plain document-presence one.
PROXIMITY_WINDOW = 50
NARRATIVE_QUALIFIER_RE = re.compile(
    r"adequate|sufficient|acceptable|analy[sz]|comment|support|correctly|"
    r"properly|satisfactory|reasonable|appropriate|justif", re.I)
NOT_IN_FILE_RE = re.compile(
    r"not in\s.{0,20}\bfile\b|not\s(?:be\s)?provided|missing|not\sin\sfile",
    re.I)

# exception-text keyword -> extractor doc_type (order matters; first match wins)
# every pattern is boundary-safe (\b or an inherent word break) so it cannot
# match as a substring of an unrelated word.
DOC_KEYWORDS = [
    (r"\bfinal\b.{0,10}\bapplication\b|\bfinal URLA\b", "final_1003"),
    (r"\binitial\b.{0,10}\bapplication\b", "final_1003"),
    (r"\bappraisal\b", "appraisal"),
    (r"\bcredit report\b", "credit_report"),
    (r"\bbank statement\b|\bdepository\b", "bank_statement"),
    (r"\bverification of employment\b|\bVOE\b", "voe"),
    (r"\bpaystub\b|\bpay stub\b", "paystub"),
    (r"\btitle (commitment|policy|binder)\b", "title_commitment"),
    (r"\bclosing disclosure\b|\bCD\b", "closing_disclosure"),
    (r"\bgift letter\b", "gift_letter"),
    (r"\bnotice of value\b|\bNOV\b", "va_nov"),
    (r"\bcertificate of eligibility\b|\bCOE\b", "va_coe"),
    (r"\bpayoff\b", "payoff_statement"),
]


# YELLOW classification keywords (decision 026 → yellow_reclassification logic)
SME_CLARIFICATION_KEYWORDS = re.compile(
    r"\badequate\b|\bsufficient\b|\bacceptable\b|\breasonable\b|\bappropriate\b|"
    r"\bjustif(?:y|ied|ication)\b|\bsatisfactory\b|\bsubstantial\b|\bcomplete(?:d)?\b|"
    r"\baccura(?:te|cy)\b|\bcorrect\b|\bproperly\b|\btimely\b", re.I)
EXTERNAL_LOOKUP_KEYWORDS = re.compile(
    r"\bexternal\b|\blookup\b|\bAPI\b|\bregistry\b|\bNMLS\b|\bMERS\b|\bHUD\b.*\blist\b|"
    r"\bapproved\b.*\blist\b|\blive\b.*\bdata\b", re.I)


def classify_yellow_unmapped(rule):
    """
    Classify unmapped rules into YELLOW sub-categories based on decision 026's
    convertible vs. genuinely-blocked analysis.

    Returns: (yellow_category, yellow_blocker_type)
      - ("convertible", "extraction_gap") if fields exist in docs but not extracted
      - ("blocked", "sme_clarification") if ambiguous threshold/subjective language
      - ("blocked", "external_lookup") if requires external data source
      - ("blocked", "other") otherwise
    """
    text = "%s %s %s" % (rule["question_text"], rule["response_text"],
                         rule["exception_description"])

    # Check for SME clarification needed (ambiguous/subjective language)
    if SME_CLARIFICATION_KEYWORDS.search(text):
        return "blocked", "sme_clarification"

    # Check for external lookup requirement
    if EXTERNAL_LOOKUP_KEYWORDS.search(text):
        return "blocked", "external_lookup"

    # Default: blocked on "other" (needs deeper analysis to determine convertibility)
    # In the real implementation, this would cross-reference against the full
    # yellow_conversion_analysis.md categorization, but for this POC we use
    # keyword heuristics as a proxy.
    return "blocked", "other"


def agency_of(code):
    c = code.upper()
    for a in AGENCIES:
        if c.startswith(a):
            return a
    return "GENERIC"


# decision 014 (Bucket A): rules needing a document type genuinely absent
# from every synthetic test loan (demo/syn/loan 01-05), verified by folder-
# inventory search against the AMQ CSV's exact rows — NOT a rule-clarity
# problem, just a missing fixture. Kept as fully legitimate/valid rules
# (never discarded or downgraded); tagged distinctly so they're never
# confused with genuinely-unclear (RED) rules. 16 exception codes across the
# 12 triaged groups (some groups span >1 code: LEP x2, Additional-Borrower-
# form x4, initial-URLA x1-shared, SCIF x2, ROV x2).
BLOCKED_ON_MISSING_FIXTURE_EXCEPTION_CODES = {
    "O-CFPB-54136", "O-CFPB-54137",                    # LEP preference/disclosure
    "O-FHA-00079",                                      # HUD-92564-CN
    "O-VA-00071",                                       # VA Counseling Checklist
    "O-FHA-00067",                                       # Informed Consumer Choice
    "O-FHA-00066",                                       # HUD-92900-B
    "O-FHA-54162", "O-FRD-54159", "O-RHS-54165", "O-VA-54168",  # Additional Borrower form (initial)
    "O-VA-50003", "O-FHA-54040",                        # initial URLA incomplete/not in file
    "O-FRD-56131", "O-FNM-56132",                       # Form 1103 / SCIF
    "O-FNM-59136", "O-FRD-59137",                       # ROV-process disclosure
}


def classify_eval(rule, mapped_codes):
    exc = rule["exception_code"]
    if exc in mapped_codes:
        return "mapped", mapped_codes[exc], None, None
    if exc in BLOCKED_ON_MISSING_FIXTURE_EXCEPTION_CODES:
        return "blocked_on_missing_fixture", None, "convertible", "fixture_gap"
    text = "%s %s" % (rule["response_text"], rule["exception_description"])
    for absence_m in NOT_IN_FILE_RE.finditer(text):
        for kw, doc_type in DOC_KEYWORDS:
            for kw_m in re.finditer(kw, text, re.I):
                gap_start = min(absence_m.end(), kw_m.end())
                gap_end = max(absence_m.start(), kw_m.start())
                if gap_end - gap_start > PROXIMITY_WINDOW:
                    continue  # too far apart to plausibly describe each other
                span_lo = min(absence_m.start(), kw_m.start())
                span_hi = max(absence_m.end(), kw_m.end())
                if NARRATIVE_QUALIFIER_RE.search(text[span_lo:span_hi]):
                    continue  # commentary/adequacy condition, not plain presence
                return "doc_presence", doc_type, "convertible", "extraction_gap"
    # unmapped rules need further classification logic
    yellow_cat, yellow_blocker = classify_yellow_unmapped(rule)
    return "unmapped", None, yellow_cat, yellow_blocker


def compile_ruleset():
    with open(BLOCKS_MANIFEST) as f:
        valid_blocks = {b["block_id"] for b in json.load(f)}
    unknown = set(CATEGORY_TO_BLOCK.values()) - valid_blocks
    if unknown:
        raise SystemExit("Block ids not in blocks_manifest.json: %s" % unknown)

    mapped_codes = {code: name for name, m in MAPPED_SHAPES.items()
                    for code in m["amq_exception_codes"]}

    rules, seen = [], {}
    discarded = 0
    discarded_external_lookup = 0
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        # spreadsheet row numbers are Excel-style: header = row 1, data starts at 2
        for row_num, row in enumerate(csv.DictReader(f), start=2):
            code = row["Question Code"].strip()
            exc_name = row["Question Answers Exception Name"].strip()
            category = row["Question Category Name"].strip()
            exc_code = row["Exception Code"].strip()
            key = (code, exc_name)
            if key in seen:
                seen[key]["source_rows"].append(row_num)
                continue
            if category == "Discarded":
                seen[key] = {"source_rows": [row_num]}
                discarded += 1
                continue
            if exc_code in DISCARDED_EXTERNAL_LOOKUP_EXCEPTION_CODES:
                # decision 016 (Bucket C): excluded from this PoC entirely —
                # requires a live external registry lookup, not derivable
                # from any loan document.
                seen[key] = {"source_rows": [row_num]}
                discarded_external_lookup += 1
                continue
            block = CATEGORY_TO_BLOCK.get(category)
            if block is None:
                raise SystemExit("Unmapped category: %r" % category)
            rule = {
                "question_code": code,
                "exception_name": exc_name,
                "exception_code": exc_code,
                "agency": agency_of(code),
                "category": category,
                "block": block,
                "severity": row["Default Significance"].strip(),
                "aor": row["Default AOR 1"].strip(),
                "question_text": row["Question Text"].strip(),
                "response_text": (row["Question Response"] or "").strip(),
                "exception_description": (row["Exception Description"] or "").strip(),
                "source_rows": [row_num],
            }
            eval_class, eval_target, yellow_cat, yellow_blocker = classify_eval(rule, mapped_codes)
            rule["eval_class"] = eval_class
            rule["eval_target"] = eval_target

            # Add YELLOW reclassification metadata (decision 026 → yellow_reclassification)
            if yellow_cat is not None:
                rule["yellow_category"] = yellow_cat
                rule["yellow_blocker_type"] = yellow_blocker
            else:
                rule["yellow_category"] = None
                rule["yellow_blocker_type"] = None

            # demo_in_scope: true for GREEN + YELLOW-convertible, false otherwise
            rule["demo_in_scope"] = (
                eval_class == "mapped" or
                (eval_class == "doc_presence" and yellow_cat == "convertible") or
                (eval_class == "blocked_on_missing_fixture" and yellow_cat == "convertible") or
                (eval_class == "unmapped" and yellow_cat == "convertible")
            )

            rules.append(rule)
            seen[key] = rule

    payload = json.dumps(rules, sort_keys=True).encode()
    ruleset = {
        "source_csv": os.path.basename(CSV_PATH),
        "source_rows": 5520,
        "rules_total": len(rules),
        "discarded_excluded": discarded,
        "discarded_external_lookup_excluded": discarded_external_lookup,
        "ruleset_sha256": hashlib.sha256(payload).hexdigest(),
        "rules": rules,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "ruleset.json")
    with open(out_path, "w") as f:
        json.dump(ruleset, f, indent=1, sort_keys=True)

    from collections import Counter
    by_agency = Counter(r["agency"] for r in rules)
    by_eval = Counter(r["eval_class"] for r in rules)
    by_block = Counter(r["block"] for r in rules)
    print("Compiled %d rules (excluded %d discarded, %d external-lookup [Bucket C]) -> %s"
          % (len(rules), discarded, discarded_external_lookup,
             os.path.relpath(out_path, HERE)))
    print("ruleset sha256: %s" % ruleset["ruleset_sha256"][:16])
    print("by agency: %s" % dict(by_agency.most_common()))
    print("by eval class: %s" % dict(by_eval.most_common()))
    print("by block:")
    for b, n in by_block.most_common():
        print("  %-36s %d" % (b, n))
    return ruleset


if __name__ == "__main__":
    compile_ruleset()
