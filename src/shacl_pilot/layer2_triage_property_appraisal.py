#!/usr/bin/env python3
"""
Layer-2 triage — property-appraisal-review block (714 rules, 696 unique groups).

Same GREEN/YELLOW/RED/NOT_A_CHECK method as layer2_triage.py (application-
verification) and layer2_triage_assets.py (asset-verification); read the
module docstring in layer2_triage.py for the bin definitions, they are
unchanged here.

THIS BLOCK IS QUALITATIVELY DIFFERENT FROM THE PRIOR TWO, AND THE METHOD SAYS
SO UP FRONT (verified empirically, not assumed):

1. Almost no dedup collapse: 714 rules -> 696 unique (question, condition)
   groups (~1.03x) — the 5 AMQ agencies write almost entirely independent
   condition text per appraisal sub-topic, same pattern as asset-verification
   (~1.02x), unlike application-verification (~1.5x).
2. eval_class distribution is stark: of 714 rules, 0 are "mapped" (all 7
   existing property-appraisal SHACL shapes — CompDistanceShape,
   MprCompletionCertShape, TermiteInspectionShape, StaleAppraisalShape,
   WellSepticShape, SiteValueJustificationShape, UsdaEligibilityDocShape —
   are wired to ZERO amq_exception_codes, same bug pattern already fixed
   for LargeDepositShape/GiftEvidenceShape in decisions 017/018), 36 are
   "doc_presence" (auto-compiled), 678 are "unmapped".
3. Two mechanical passes, same spirit as the asset-verification script's
   GREEN/NOT_A_CHECK derivation from amq_compiler.py's own eval_class:
     - NOT_A_CHECK: EITHER the condition text matches ^(Yes\\b|Not Applicable)
       (same PASS_RE family as the other two scripts, widened to bare "Yes"
       without a trailing comma — verified two real rows, G086 and G611, are
       bare "Yes" and would otherwise slip through) OR every rule sharing
       that (question, condition) has a BLANK Exception Code in the source
       CSV — verified this is a reliable second signal distinct from the
       PASS_RE text match: the "(FHA/FNM/FRD/RHS/VA) Is there an appraisal in
       the file? -> No, an appraisal is not required" rows (G001/G003/G005/
       G007/G009) are a screening/applicability branch (loans exempt from an
       appraisal, e.g. value-acceptance waivers) with blank Exception Code
       and blank Severity — the real defect is the SIBLING row ("No, the
       loan file did not contain an appraisal report as required", non-blank
       Exception Code) — same screening-vs-defect pattern as application-
       verification's LEP-applicability group 10 and asset-verification's
       group 291.
     - GREEN: eval_class doc_presence for every rule in the group (36 groups)
       — amq_compiler.py's own mechanical classifier already auto-compiles
       these; unchanged from the reference pattern.
4. NO group in this block mechanically resolves to "mapped" (eval_class),
   because MAPPED_SHAPES lists these 7 shapes with an EMPTY amq_exception_
   codes list today. Task instruction: check whether any of the 696 groups'
   real condition text is the SAME real-world fact one of those 7 shapes
   already checks (an agency-wording variant), the way decision 018 found
   for LargeDepositShape/GiftEvidenceShape. Searched explicitly (see decision
   020's writeup) for comp-distance, MPR/Form-442, termite, stale-appraisal/
   recert, well/septic, site-value, and USDA-property-eligibility language
   across all 696 groups AND the raw source CSV directly. Result: ZERO safe
   direct wires. Three of the seven shapes (CompDistanceShape,
   SiteValueJustificationShape, UsdaEligibilityDocShape) have NO matching AMQ
   row in this workbook AT ALL — confirmed by grepping the raw CSV for
   "mile"/"site value"/"rural eligib" within the Property - Appraisal
   category and getting zero hits — these three shapes predate the full-
   workbook compile (decision 009) and were authored directly against the
   loan-01 demo scenario, not derived from any AMQ row; the CompDistanceShape
   SPARQL comment already says as much ("SME-PLACEHOLDER... NOT traceable to
   a source AMQ row"). The other four (MPR/442, termite, stale-appraisal/
   recert, well/septic) DO have topically-related AMQ rows in this block, but
   every single one verified tests a MATERIALLY DIFFERENT condition than the
   existing shape's SPARQL (an added source-authority requirement, an added
   staleness/date clause, a different real-world form purpose, a different
   loan-program applicability) — see decision 020 for the row-by-row
   verification. This is the decision-018 self-check discipline applied
   BEFORE any candidate is proposed, not after — the honest result is that
   this search came up empty, and that negative result is reported as a
   finding, not papered over.
5. Given the remaining ~539 groups (696 - 122 NOT_A_CHECK - 35 doc_presence)
   are overwhelmingly dominated by appraisal-REPORT narrative-content
   adequacy language ("did not comment", "no commentary", "not adequately
   supported", "not analyzed", "not consistent", "not addressed") that our
   field-level regex extractor (extract_loan.py) does not capture today and
   could not capture without full free-text semantic parsing of the
   appraisal narrative sections — a fundamentally different, much harder
   problem than presence/threshold checks — individually hand-authoring
   539 entries at the same prose depth as the ~210-entry asset-verification
   C dict was not achievable at reviewable quality in the time available.
   Instead: a small, explicit OVERRIDES dict below hand-classifies every
   group that is either (a) a genuine near-miss candidate against one of the
   7 existing shapes (individually verified, see decision 020), (b) an
   external-registry/Bucket-C candidate, or (c) otherwise notable/singular;
   everything else is classified by a documented, auditable FAMILY
   classifier (regex-pattern rules applied in a fixed priority order, listed
   below) that assigns bin + a rationale citing the ACTUAL matched condition
   text for that row (not a generic canned string) — reviewable in the SME
   packet exactly like a hand-typed entry, just generated systematically
   given the scale. This is a deliberate, disclosed method difference from
   the prior two scripts, not a shortcut hidden from the SME.

Outputs:
  compiled/triage_property-appraisal-review.json
  out/TRIAGE-PACKET-property-appraisal-review.md
"""
import json
import os
import re
from collections import OrderedDict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
RULESET = os.path.join(HERE, "compiled", "ruleset.json")
SG_INDEX = os.path.join(HERE, "compiled", "selling_guide_index.json")
OUT_JSON = os.path.join(HERE, "compiled", "triage_property-appraisal-review.json")
OUT_MD = os.path.join(HERE, "out", "TRIAGE-PACKET-property-appraisal-review.md")

BLOCK = "property-appraisal-review"
EXPECTED_GROUPS = 696

PASS_RE = re.compile(r"^(Yes\b|Not Applicable)", re.I)

STOP = set("were all the of and or a an is in to for was not on by with as at have "
           "been requirements met all any".split())


def tokens(text):
    return {w for w in re.findall(r"[a-z]{3,}", text.lower())} - STOP


def retrieve_topics(sg, rule_text, k=3):
    rt = tokens(rule_text)
    scored = []
    for t in sg["topics"]:
        overlap = len(rt & tokens(t["title"]))
        if overlap:
            scored.append((overlap, t["code"], t["title"], t["pdf_page"]))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [{"code": c, "title": ti, "pdf_page": p, "score": s}
            for s, c, ti, p in scored[:k]]


# ---------------------------------------------------------------------------
# Hand-verified overrides (task C's decision-018 discipline applied BEFORE
# proposing anything). Every one below was checked against the full
# question_text + response_text + exception_description for that row AND
# the exact SPARQL/fact the candidate shape uses, per the required self-check.
# Keyed by gid (1-indexed position in the sorted-groups OrderedDict).
OVERRIDES = {
    # ----- "Is there an appraisal in the file?" — the real doc_presence defect
    # rows, worded differently from amq_compiler.py's NOT_IN_FILE_RE regex
    # ("did not contain ... as required" doesn't match "not in .{0,20}file|
    # not provided|missing"), so these did NOT auto-classify as doc_presence
    # even though they are, conceptually, the exact same check amq_compiler.py
    # already auto-compiles elsewhere in this block (the appraisal doc type
    # is already in DOC_KEYWORDS/extract_loan.py's DOC_TYPES).
    2: ("YELLOW", "appraisal document presence (doc type already in the extraction contract)", "-",
        "amq_compiler.py's NOT_IN_FILE_RE regex needs widening to also match "
        "'did not contain ... as required' phrasing",
        "Same real check amq_compiler.py already auto-compiles as doc_presence for "
        "other rows in this block (appraisal doc type is already extracted) — this "
        "row's exact wording ('did not contain an appraisal report as required') just "
        "evades the compiler's NOT_IN_FILE_RE regex. A compiler regex-widening fix, "
        "not a data/fixture gap — kept YELLOW rather than blindly called GREEN, since "
        "the mechanism that would make it GREEN doesn't actually fire for this row today."),
    4: ("YELLOW", "as G002 (FNM variant)", "-", "same regex-widening gap as G002", "Same as G002 (FNM wording)."),
    6: ("YELLOW", "as G002 (FRD variant)", "-", "same regex-widening gap as G002", "Same as G002 (FRD wording)."),
    8: ("YELLOW", "as G002 (RHS variant)", "-", "same regex-widening gap as G002", "Same as G002 (RHS wording)."),
    10: ("YELLOW", "as G002 (VA variant)", "-", "same regex-widening gap as G002", "Same as G002 (VA wording)."),

    # ----- Existing-shape near-miss candidates: verified NOT safe to wire
    # (decision-018 discipline) — every one tests a materially different
    # real-world condition than the shape's actual SPARQL, despite sharing
    # a topic keyword (termite / well-septic / Form-442-MPR / stale-appraisal).
    151: ("YELLOW", "-", "-",
          "NPMA-99-A/99-B/33 form-specific doc type + a signature fact (neither modeled today)",
          "NEAR-MISS vs TermiteInspectionShape (CHK-PRP-003) — checked and REJECTED as a "
          "blind wire: our termite_inspection_in_file fact is a single boolean derived from "
          "one 'Termite ... NOT IN FILE' phrase in the appraisal summary; this VA row names "
          "THREE specific form numbers (NPMA-99-A/99-B/33) AND adds a 'not signed' clause our "
          "fact cannot distinguish. Wiring it would risk a false negative on the signature "
          "half — same class of mistake the assets triage's O-FRD-58101 rejection was."),
    279: ("YELLOW", "-", "-", "post-treatment water-safety documentation (not modeled; distinct from inspection presence)",
          "Topically near TermiteInspectionShape (mentions 'termites') but tests a DIFFERENT "
          "fact — whether soil-poisoning treatment was shown not to endanger water quality — "
          "not termite-inspection-report presence. Not a match; kept as its own YELLOW group."),
    375: ("YELLOW", "-", "-",
          "termite_inspection_in_file (fact already extracted) — but shape has no RHS/state-law "
          "conditionality to gate on, and the AMQ row's own trigger is conditional ('where req'd "
          "by the lender, appraiser, inspector, or State law')",
          "NEAR-MISS vs TermiteInspectionShape (CHK-PRP-003) — closest of the four termite "
          "candidates (same real fact: termite/pest inspection report presence), but the "
          "existing shape's message hardcodes 'VA loans in NC' while this row is RHS and "
          "conditioned on an unmodeled applicability test ('where required'). The shape's "
          "SPARQL itself doesn't actually gate on state or program (a pre-existing gap, not "
          "introduced by this row) — extending amq_exception_codes here would make the shape "
          "fire for RHS loans too without ever checking RHS applicability. Flagged as WORTH "
          "SME REVIEW, not classified as ready-to-build — same caution as assets' G108/G127/"
          "G131/G296 gift-transfer near-misses."),
    511: ("RED", "-", "narrative commentary presence/adequacy for lead paint, meth contamination, wood-destroying pests",
          "-",
          "Topically overlaps termite/well/LBP families but the actual condition is 'no "
          "commentary given' — a narrative-adequacy judgment on the appraiser's write-up, not "
          "a document-presence test. Not a match to any existing shape."),
    275: ("RED", "-", "bare 'all on-site sewage system/septic tank requirements not met' catch-all", "-",
          "Topically near WellSepticShape but stated as a bare, unenumerated catch-all with no "
          "single fact named — needs SME decomposition before any automation, same pattern as "
          "application-verification's VA-disclosure catch-all."),
    276: ("RED", "-", "bare 'all subject well requirements not met' catch-all", "-",
          "Same bare-catch-all pattern as G275 (well, not septic, variant)."),
    281: ("YELLOW", "-", "-", "well-water-test doc type + a 'disinterested third-party' source-authority fact (not modeled)",
          "NEAR-MISS vs WellSepticShape (CHK-PRP-005) — checked and REJECTED as a blind wire: "
          "this row tests WHO conducted the test (a disinterested third party), a source-"
          "authority condition our presence-only fact cannot verify — same trap as the assets "
          "triage's O-FRD-58101 rejection (acceptability of source vs. mere presence)."),
    282: ("YELLOW", "-", "-", "well-water-test date field (180-day staleness, not modeled — presence-only fact today)",
          "NEAR-MISS vs WellSepticShape — closest of the well/septic candidates (presence OR "
          "staleness), but REJECTED as a blind wire: our well_septic_inspection_in_file fact "
          "is presence-only; this row's real, and arguably primary, condition is a 180-day "
          "AGE test our fact cannot evaluate. Wiring it would silently pass a stale-but-"
          "present test result, a genuine false-negative risk."),
    283: ("YELLOW", "-", "-", "well-water-test source-authority field (lab/health-authority qualification, not modeled)",
          "NEAR-MISS vs WellSepticShape — REJECTED: tests source ACCEPTABILITY (qualified lab "
          "or local health authority performed the test), not presence. Same acceptability-"
          "vs-presence trap as G281/G283 and the assets triage's O-FRD-58101 rejection."),
    423: ("YELLOW", "-", "adequacy of community water/sewage system operation & maintenance",
          "community (not private) water/sewage system documentation (not modeled)",
          "Distinguishable from WellSepticShape by subject matter alone: WellSepticShape is "
          "USDA RD's PRIVATE well & septic check; this VA row is about a COMMUNITY water/"
          "sewage system's documented adequacy — a different real-world system, plus an "
          "'adequately maintained' judgment word. Not a match."),
    485: ("YELLOW", "-", "'acceptable' water/wastewater system judgment", "site water/wastewater documentation (not modeled)",
          "Presence is the crisp half; 'acceptable' is the same acceptability-judgment trap as "
          "G281/G283 — kept YELLOW since documentation presence is still checkable once the "
          "doc exists, but flagged, not treated as a WellSepticShape extension."),
    493: ("YELLOW", "-", "-", "water-analysis-report date field (180-day staleness, not modeled)",
          "Same staleness-not-presence gap as G282 (RHS site-requirements wording variant)."),
    40: ("YELLOW", "-", "-", "Form 442 (Freddie Mac 'Appraisal Update and/or Completion Report') doc type — "
         "NOT the FHA MPR-completion-cert fact our extractor models",
         "NEAR-MISS vs MprCompletionCertShape (CHK-PRP-002) — REJECTED: our "
         "doc_present_fha_form_442 fact is computed ONLY for mortgage_type == 'FHA' "
         "(extract_loan.py's EXPECTED_DOCS_BY_PROGRAM is keyed 'FHA'/'VA' only) and this row "
         "is Freddie Mac — the fact would never even be populated for an FRD loan, so wiring "
         "this exception code to MprCompletionCertShape would never fire, a 'field that would "
         "never populate for the loans this rule targets' trap identical to the assets "
         "triage's O-RHS-57768 rejection (cash_out_to_borrower_1003 being refi-only "
         "terminology). Also a different real-world form USE (appraisal update/revalidation "
         "vs. MPR-repair completion), not just a different program."),
    676: ("YELLOW", "-", "-", "as G040 — Freddie Form 442, not FHA MPR completion cert",
          "Same program-mismatch rejection as G040."),
    677: ("YELLOW", "-", "-", "as G040 — Freddie Form 442/400, not FHA MPR completion cert",
          "Same program-mismatch rejection as G040."),
    37: ("YELLOW", "-", "-", "LPA/PIW offer-validity date field (not modeled) — a different real-world "
         "expiration than appraisal-effective-date staleness",
         "NEAR-MISS vs StaleAppraisalShape (CHK-PRP-004) — REJECTED: '120 days' here gates an "
         "AUS PIW (Property Inspection Waiver) OFFER's validity, not the appraisal report's "
         "own age. Different real-world clock, different document (LPA findings, not the "
         "appraisal), not a match."),
    39: ("YELLOW", "-", "bare 'all other req's not met' catch-all appended to the reuse condition",
         "prior-appraisal-reuse date field + explicit reuse flag (not modeled)",
         "NEAR-MISS vs StaleAppraisalShape — related family (a REUSED PRIOR appraisal over 120 "
         "days), but the row targets appraisal REUSE specifically (our fact only measures this "
         "loan's own appraisal's age at closing, not whether it was carried over from a prior "
         "transaction) plus a vague catch-all suffix — not a safe direct wire."),
    41: ("YELLOW", "-", "-", "disbursement-date field (not modeled — our fact measures age at CLOSING, "
         "not at disbursement) + 'updated or new appraisal' fact",
         "NEAR-MISS vs StaleAppraisalShape — related (appraisal validity gap) but keyed to "
         "DISBURSEMENT date, which can post-date closing for construction/escrow loans; our "
         "appraisal_age_days_at_closing derivation is closing-date-based. Not a safe direct "
         "wire without a new disbursement_date field."),

    # ----- The 17 (of 33) "appraisal"-target doc_presence rows that, once
    # re-routed out of the mechanical-GREEN path (see the eval_target fix
    # above), the generic FORM_RE/PHOTO_RE regexes still didn't catch —
    # manually reviewed instead of left to the conservative-default-RED
    # fallback, since every one of these is a genuine presence check for a
    # SPECIFIC missing letter/certification/report/evidence, not a narrative-
    # adequacy judgment call. (The ones the fallback correctly left as RED —
    # G011, G173, G345 narrative-analysis; G670's compound "without
    # explanation" catch-all — were left alone.)
    26: ("YELLOW", "presence of a ROV-process disclosure at the time the appraisal was provided", "-",
         "ROV-process disclosure doc type (not in corpus)",
         "SAME missing-fixture family as application-verification's decision-014 Bucket-A "
         "ROV-disclosure groups (O-FNM-59136/O-FRD-59137, that block's application-stage "
         "variant) — this is the appraisal-stage ROV-disclosure-presence variant, same "
         "underlying document family, still absent from all 5 synthetic loans."),
    154: ("YELLOW", "presence of a signed/dated written correction by the appraiser", "-",
          "appraisal-correction-letter doc type (not in corpus)",
          "Crisp presence check once the correction letter exists as a document; niche, "
          "absent from all 5 synthetic loans' single Appraisal Summary PDF."),
    179: ("YELLOW", "presence of an appraisal-transfer letter from the original lender", "-",
          "appraisal-transfer-letter doc type (not in corpus)",
          "Crisp presence check once the transfer letter exists as a document."),
    204: ("YELLOW", "-", "-",
          "a distinct 'SAR researched market data and provided a recommendation' evidence "
          "fact (not modeled — different from mere va_nov/NOV presence, which already exists)",
          "amq_compiler.py's DOC_KEYWORDS matched 'NOV' and pointed this at the va_nov doc "
          "type, but the ACTUAL missing thing per the full exception_description is evidence "
          "of the SAR's market-data research and recommendation to the RLC — the NOV itself "
          "already exists in this row's premise. Reclassified from the mechanical GREEN this "
          "eval_target would otherwise produce: a real compiler mis-mapping, not a genuine "
          "va_nov-presence check — same class of finding as the 'appraisal' generic-target "
          "issue this triage's module docstring documents at length."),
    229: ("YELLOW", "presence of a ROV-process disclosure given at application and at appraisal delivery", "-",
          "ROV-process disclosure doc type (not in corpus)",
          "FHA variant of the same ROV-disclosure family as G026 — same missing-fixture gap."),
    236: ("YELLOW", "presence of the FHA Appraisal Logging Results screen-print", "-",
          "FHA Connection Appraisal Logging Results doc type (not in corpus)",
          "Crisp presence check once this specific FHAC screen-print exists as a captured "
          "document; distinct from the whole appraisal report itself."),
    257: ("YELLOW", "presence of the appraiser's certification / statement of assumptions section", "-",
          "appraiser-certification exhibit flag (deepen appraisal extraction — not modeled; "
          "the doc always exists, but this specific section/exhibit within it isn't checked)",
          "Exhibit-level presence check, same family as G263/G421/G531 (already YELLOW) — "
          "reclassified from the conservative-default RED, since this is a specific-"
          "component-missing fact, not a narrative-adequacy judgment."),
    267: ("YELLOW", "presence of a qualified-professional inspection for a repairs-conditioned appraisal", "-",
          "post-repair inspection-report doc type (not in corpus)",
          "Crisp presence check once the inspection report exists as a document."),
    268: ("YELLOW", "presence of an appraisal-transfer approval letter from the original lender", "-",
          "transfer-approval-letter doc type (not in corpus)",
          "Same transfer-letter family as G179 (approval variant)."),
    344: ("YELLOW", "presence of an inspection report or repair invoices", "-",
          "post-repair inspection/invoice doc type (not in corpus)",
          "Crisp presence check once the inspection report or invoices exist as documents."),
    381: ("YELLOW", "presence of the appraiser's certification / statement of assumptions section", "-",
          "appraiser-certification exhibit flag (deepen appraisal extraction — not modeled)",
          "Same exhibit-level family as G257 (Freddie Mac wording variant)."),
    411: ("YELLOW", "presence of appraiser-input documentation (sales contract, known property info)", "-",
          "appraiser-input-package doc/field (not modeled — this is about what the LENDER gave "
          "the appraiser, not what the appraiser reported)",
          "Reclassified from the conservative-default RED: this is a presence check on the "
          "lender's input package to the appraiser, a crisp (if currently unmodeled) fact, "
          "not a narrative-adequacy judgment."),
    478: ("YELLOW", "presence of a prior-sales/transfer-history field + verification source", "-",
          "subject/comp 3-year sales-history + verification-source fields (not modeled)",
          "Crisp presence/completeness check on a specific data point once the field is added; "
          "reclassified from the conservative-default RED."),
    659: ("YELLOW", "presence of borrower certification of pre-disaster property condition", "-",
          "disaster borrower-certification doc type (not in corpus)",
          "Crisp presence check, same disaster-documentation family as G660/G661."),
    660: ("YELLOW", "presence of an inspection evidencing pre-disaster property condition", "-",
          "disaster pre-condition inspection doc type (not in corpus)",
          "Same disaster-documentation family as G659/G661."),
    661: ("YELLOW", "presence of lender certification of pre-disaster property condition", "-",
          "disaster lender-certification doc type (not in corpus)",
          "Same disaster-documentation family as G659/G660."),
    671: ("YELLOW", "presence of the appraiser's itemized list of repairs/required actions", "-",
          "repair-itemization exhibit (not modeled)",
          "Crisp presence check once this specific exhibit is captured; reclassified from the "
          "conservative-default RED."),

    # ----- Four more rows corrected by manual spot-check of the "numeric
    # threshold" YELLOW bucket (only 9 groups total — small enough to review
    # every one by hand once the classifier's headline counts were sane).
    20: ("RED", "-", "bare 'all requirements... not met' catch-all bundling several distinct "
         "property-flip sub-rules (180-day window, resale-price-increase %, etc.)", "-",
         "Reclassified from the family classifier's numeric-threshold match (it picked up "
         "'180 days' from the QUESTION text, not the response): the actual defect condition "
         "is a bare 'all requirements have not been met' catch-all bundling several distinct "
         "property-flip sub-tests, not a single checkable fact — same pattern as application-"
         "verification's VA-disclosure catch-all; needs SME decomposition first."),
    353: ("RED", "-", "neighborhood-section narrative completeness/accuracy judgment", "-",
          "Reclassified from the family classifier's numeric-threshold match (picked up a "
          "stray digit from exception_description, not a real threshold in this row's own "
          "condition): same 'Section ... not completed/incomplete/inaccurate' narrative-"
          "completeness family as G043/G049/G051/G059/G062 (all already RED) — this is the "
          "neighborhood-section sibling, no different in kind."),
    96: ("YELLOW", "comp_explanation_present (ALREADY extracted) for the explanation half", "-",
         "comp sale-closing-date field (not currently extracted — comps entity has "
         "comp_num/address/distance_miles/sale_price/gla/adjusted_sale_price, no closing date) "
         "for the '12 months' half",
         "WORTH SME REVIEW, not ready-to-build: a genuine two-part condition — (a) comp not "
         "closed within 12 months (needs a new comp-closing-date field) AND (b) no explanation "
         "provided, which reuses the SAME comp_explanation_present boolean CompDistanceShape "
         "already checks. Flagged, not proposed as a blind wire: comp_explanation_present is a "
         "single generic 'is there ANY addenda/explanation text' flag, not specific to WHICH "
         "condition it explains (comp distance vs comp age) — reusing it here risks the same "
         "over-general-fact trap as the assets triage's gift-transfer-evidence near-misses "
         "(G108/G127/G131/G296)."),
    270: ("YELLOW", "appraisal_age_days_at_closing (ALREADY extracted and used by StaleAppraisalShape)", "-",
          "none for the age math itself — only the 180-vs-120-day threshold and the "
          "missing recertification-cures-it exception need SME confirmation before wiring",
          "WORTH SME REVIEW, closest near-miss in this entire block to an existing shape: "
          "RHS's 180-day appraisal-age rule tests the EXACT SAME fact StaleAppraisalShape "
          "already computes (appraisal_age_days_at_closing), just a different threshold (180, "
          "not 120) and — unlike StaleAppraisalShape — this RHS row states no recertification-"
          "of-value exception that would cure it. NOT proposed as a blind extension of "
          "StaleAppraisalShape (different threshold + different cure condition would change "
          "the shape's actual logic, not just its exception-code list) — flagged as the "
          "strongest build candidate in the block for a NEW, RHS-specific check reusing the "
          "same already-extracted field."),

    # ----- Two rows the family classifier over-matched on incidental words
    # ("deemed") inside the narrative-judgment regex; found by manual spot-
    # check of a random RED sample, not the classifier's own logic. Both are
    # genuinely doc-presence/evidence checks once the antecedent ("water
    # deemed unsafe") is true — the word "deemed" was describing the
    # antecedent trigger, not the checkable condition itself.
    277: ("YELLOW", "-", "-", "water-purification maintenance-contract + escrow-account doc/field (not modeled)",
          "Reclassified from the family classifier's default RED match (incidental word "
          "'deemed'): the actual checkable condition is presence of a maintenance contract "
          "and escrow account for a water-purification system, once the antecedent ('water "
          "deemed unsafe') holds — a crisp presence check, not a narrative judgment."),
    278: ("YELLOW", "-", "-", "safety-evidence documentation for a public water supply deemed unsafe (not modeled)",
          "Reclassified from the family classifier's default RED match (incidental word "
          "'deemed'): the checkable condition is presence of evidence the water supply was "
          "made safe prior to closing — a crisp presence check once the doc type exists."),

    # ----- The screening/applicability "not required" branches (mechanical
    # NOT_A_CHECK already handles these via the blank-Exception-Code rule;
    # listed here only for narrative completeness in the packet's Bucket-C/
    # near-miss discussion — no override tuple needed, they're already
    # correctly binned before OVERRIDES is even consulted).
}

# Bucket-C-style external-registry/database candidates (decision 016
# precedent) — flagged in the packet, NOT unilaterally discarded from the
# compiled ruleset (a human decides, per that decision's own instruction).
EXTERNAL_DB_RE = re.compile(
    r"\bCPM\b|Condo Project Manager|FHA Connection|\bFHAC\b|\bUCDP\b|VeroSCORE|"
    r"WebLGY|\bAMS\b|DELRAP|HRAP|Property Data API|Condo Project Advisor|"
    r"\bCU\b(?!STOM)|Collateral Underwriter|HUD roster|FHA Approved Condominium",
    re.I)

FORM_RE = re.compile(
    r"\bForm\s?\d{2,4}[A-Z]?\b|HUD-\d{3,5}(?:\.\d+)?[A-Z]?|VA Form\s?26-\d{3,4}|"
    r"\b26-1839\b|\b26-1805\b|\b1076A?\b|\b1074\b|\b1007\b|\b9991\b|\b9992\b|"
    r"\b92800\.5B\b|\b820\.05\b|\b2090\b|\b1004D\b|Pro Rata form|"
    r"Compliance Inspection Report|Condo Questionnaire|Project Questionnaire|"
    r"project approval certificate|Recognition Agreement|sellers affidavit|"
    r"stock cert(?:ificate)?",
    re.I)

PHOTO_RE = re.compile(
    r"\bphotos?\b|\bsketch\b|location map|building sketch|appraisal invoice",
    re.I)

NUMERIC_THRESHOLD_RE = re.compile(
    r"\b\d{1,3}\s*(?:days?|months?|mos\b)\b|\b\d{1,3}%|\bLTV\b.{0,10}\b\d{1,3}%?",
    re.I)

# Narrative/judgment vocabulary this pilot's field-level extractor cannot
# resolve now (or via any near-term field addition) without full free-text
# semantic parsing of the appraisal narrative — this IS the human-judgment
# core of appraisal review.
NARRATIVE_JUDGMENT_RE = re.compile(
    r"without (?:comment|explanation|comment\w*|adequate|sufficient|support)|"
    r"no comment|not commented|did not comment|no commentary|not addressed|"
    r"did not address|not adequately|did not adequately|not analy[sz]ed|"
    r"did not analy[sz]e|not (?:adequately )?supported|did not support|"
    r"\breasonabl[ey]\b|\bunreasonable\b|\bacceptable\b|\bunacceptable\b|"
    r"\bappropriate\b|\binappropriate\b|\bcredible\b|\bmarketability\b|"
    r"highest and best use|\binconsistent\b|\bconsistent\b|\bappears?\b|"
    r"misrepresent|prohibited|discriminat|\bbias\b|not (?:properly|adequately)|"
    r"did not (?:report|note|indicate) (?:if|whether)|adequately explained|"
    r"not adequately explained|without (?:being )?cured|deemed|indicat(?:e|es|ion)",
    re.I)

BARE_CATCHALL_RE = re.compile(
    r"^(?:all|.{0,15})?requirements? (?:for|of|not met|were not met)\.?$", re.I)

CONDO_COOP_PROJECT_RE = re.compile(
    r"condo|co-?op\b|\bPUD\b|leasehold|\bADU\b|manufactured home|timeshare|"
    r"condotel|\bHOA\b|budget|litigation|reserve allocation|special assessment|"
    r"delinquen|ownership concentration|single entity|parcel|community land trust|"
    r"desktop appraisal|hybrid appraisal|value acceptance|rural (?:area )?designat",
    re.I)


def classify_family(q, resp, exc_desc, agencies):
    """Documented, auditable fallback classifier — see module docstring
    point 5. Priority order matters; each branch returns a rationale that
    cites the actual matched text, not a canned string."""
    text = "%s %s %s" % (q, resp, exc_desc)
    resp_short = resp.strip()
    # form-number/doc-presence signal checked ahead of the external-DB signal:
    # a row whose PRIMARY, actionable condition is "Form NNNN ... not in the
    # file" is a crisp presence check even if its exception_description also
    # happens to name the submission channel (e.g. "... or a DELRAP Mortgagee
    # is not in the file" — DELRAP names WHO may submit the form, it is not
    # itself a live-lookup requirement). Only treat a row as Bucket-C when the
    # external-system reference appears in the actual condition (question or
    # response text), not merely in the fuller exception_description.
    qresp_text = "%s %s" % (q, resp)

    m = FORM_RE.search(text)
    if m:
        pass  # handled below, after the external-DB check on qresp_text only
    m_extdb_primary = EXTERNAL_DB_RE.search(qresp_text)
    if m_extdb_primary and not m:
        return ("YELLOW", "-", "-",
                "live lookup against an external system/database this pilot has no "
                "integration with (%r)" % m_extdb_primary.group(0),
                "Bucket-C-style candidate (decision 016 precedent): references %r, an "
                "external system this pilot cannot query from a static loan document. "
                "Flagged, not unilaterally discarded from the compiled ruleset — a human "
                "should decide, same as the RE-license and NMLS precedents."
                % m_extdb_primary.group(0))

    if m:
        return ("YELLOW", "presence of the named form/document once its doc type exists", "-",
                "%r as a distinct document type — not in any of the 5 synthetic loans "
                "(each has one 'Appraisal Summary' PDF only, no separate project/form "
                "documentation)" % m.group(0),
                "Crisp presence check once %r exists as its own document type; a real "
                "fixture gap, not a rule-clarity problem — condition: %r"
                % (m.group(0), resp_short[:140]))

    m = PHOTO_RE.search(text)
    if m:
        return ("YELLOW", "presence of the named exhibit (photos/sketch/map/invoice)", "-",
                "appraisal exhibit fields (photos, sketch, location map, invoice) — not "
                "modeled; the appraisal summary PDF used in this pilot's synthetic loans "
                "does not include exhibit pages",
                "Crisp presence check once appraisal exhibits are captured as their own "
                "fields/attachments — condition: %r" % resp_short[:140])

    if NARRATIVE_JUDGMENT_RE.search(text):
        kw = NARRATIVE_JUDGMENT_RE.search(text).group(0)
        return ("RED", "-", "narrative-adequacy judgment on the appraiser's written commentary/analysis",
                "-",
                "Matched narrative-judgment vocabulary (%r) — requires reading and judging "
                "free-text commentary in the appraisal report body, which this pilot's "
                "regex-based field extractor does not capture and could not capture without "
                "full semantic parsing of the narrative sections; condition: %r"
                % (kw, resp_short[:140]))

    if BARE_CATCHALL_RE.match(resp_short) or (len(resp_short.split()) <= 6
                                              and "not met" in resp_short.lower()):
        return ("RED", "-", "open-ended catch-all with no single stated fact", "-",
                "Bare 'requirements not met' catch-all, same pattern as application-"
                "verification's VA-disclosure catch-all and assets' Community-Savings-"
                "System/IDA catch-alls — needs SME decomposition before any automation; "
                "condition: %r" % resp_short[:140])

    m = NUMERIC_THRESHOLD_RE.search(text)
    if m and not CONDO_COOP_PROJECT_RE.search(text):
        return ("YELLOW", "threshold math once the underlying date/percent field exists", "-",
                "a specific date/percentage field (%r) not currently in FIELD_SPECS/"
                "FACT_SPECS for any appraisal-adjacent document" % m.group(0),
                "Crisp threshold math (%r) once the field exists — not a judgment call, "
                "just an unbuilt field; condition: %r" % (m.group(0), resp_short[:140]))

    if CONDO_COOP_PROJECT_RE.search(text):
        kw = CONDO_COOP_PROJECT_RE.search(text).group(0)
        return ("YELLOW", "-", "-",
                "condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, "
                "project questionnaires, litigation/budget/reserve disclosures) — an entirely "
                "separate document family, absent from all 5 synthetic loans",
                "Matched project-documentation vocabulary (%r) — the single biggest fixture "
                "gap in this block: no condo/co-op/PUD project-review document of any kind "
                "exists in any of the 5 synthetic loans (each loan has exactly one appraisal "
                "summary PDF, no project-level HOA/questionnaire/litigation documentation); "
                "condition: %r" % (kw, resp_short[:140]))

    # Conservative default: this block is judgment-dominated: an appraisal-
    # review condition with no crisp form/threshold/project-doc signal is,
    # on the evidence of every other classified group, almost always a
    # narrative-commentary or holistic-compliance judgment call.
    return ("RED", "-", "no crisp extractable fact identified in this row's condition text", "-",
            "No form/threshold/project-doc/external-DB signal matched; defaulting to human "
            "review is the conservative choice for this narrative-heavy block rather than "
            "inventing an automation path — condition: %r" % resp_short[:140])


def main():
    with open(RULESET) as f:
        ruleset = json.load(f)
    rules = [r for r in ruleset["rules"] if r["block"] == BLOCK]
    source_csv = ruleset["source_csv"]
    with open(SG_INDEX) as f:
        sg = json.load(f)

    groups = OrderedDict()
    for r in sorted(rules, key=lambda x: (x["question_text"], x["response_text"])):
        groups.setdefault((r["question_text"], r["response_text"]), []).append(r)

    if len(groups) != EXPECTED_GROUPS:
        raise SystemExit("Expected %d unique groups for a fresh compile of %d rules; "
                         "got %d. Ruleset changed — re-review before trusting this "
                         "triage." % (EXPECTED_GROUPS, len(rules), len(groups)))

    out_groups, group_counter, rule_counter = [], Counter(), Counter()
    n_mechanical_notacheck = n_mechanical_green = n_override = n_family = 0

    for gid, ((q, resp), members) in enumerate(groups.items(), 1):
        agencies = sorted({m["agency"] for m in members})
        ecs = sorted({m["eval_class"] for m in members})
        all_blank_ec = all(m["exception_code"] == "" for m in members)
        exc_desc = " ".join(sorted({m["exception_description"] for m in members if m["exception_description"]}))

        method = None
        if all_blank_ec or PASS_RE.match(resp.strip()):
            bin_, machine, human, needs, rationale = (
                "NOT_A_CHECK", "-", "-", "-",
                "Pass/N-A/screening answer option, not a defect condition"
                + (" (blank Exception Code in source CSV confirms this is a screening/"
                   "applicability branch, not a scoreable defect)" if all_blank_ec else "") + ".")
            n_mechanical_notacheck += 1
            method = "mechanical"
        elif gid in OVERRIDES:
            # Hand overrides win even over the doc_presence-GREEN mechanical
            # signal below — G204 is exactly this case: eval_class is
            # doc_presence with eval_target "va_nov" (not the unreliable
            # generic "appraisal"), so it WOULD mechanically qualify as
            # GREEN, but manual review found the real missing fact is SAR
            # market-research evidence, not NOV presence (see the override's
            # own comment). Checked before the mechanical branch so a
            # verified human judgment always takes precedence over the
            # mechanical default.
            bin_, machine, human, needs, rationale = OVERRIDES[gid]
            n_override += 1
            method = "hand_override"
        elif ecs == ["doc_presence"] and all(m["eval_target"] != "appraisal" for m in members):
            # IMPORTANT DEVIATION from the reference scripts, found by manual
            # spot-check (see module docstring / decision 020): eval_class
            # doc_presence is NOT a trustworthy auto-GREEN signal in this
            # block when eval_target == "appraisal". amq_compiler.py's
            # DOC_KEYWORDS list uses the generic keyword "appraisal" as a
            # catch-most match (any appraisal-adjacent exception text ending
            # in "not provided/missing/not in file"), but the vast majority
            # of those rows are actually about a SPECIFIC sub-document,
            # exhibit, certification, or narrative analysis MISSING FROM
            # WITHIN an appraisal that is always otherwise present in this
            # pilot's synthetic corpus (every loan has exactly one Appraisal
            # Summary PDF) — a runtime check against generic appraisal-doc
            # presence would find the doc present and silently PASS every
            # one of these real defects, never firing. Verified empirically:
            # of the 35 doc_presence groups in this block, 33 rules target
            # generic "appraisal" (unreliable, re-routed to hand
            # classification below) vs only 3 target "va_nov" (a genuinely
            # distinct, correctly-modeled doc type — kept GREEN here).
            targets = sorted({m["eval_target"] for m in members})
            bin_, machine, human, needs, rationale = (
                "GREEN", "auto-compiled doc-presence check on: %s" % ", ".join(targets),
                "-", "-",
                "Auto-compiled by amq_compiler.py's doc_presence classifier against a "
                "genuinely distinct, already-modeled document type (not the generic "
                "'appraisal' catch-all — see module docstring) — already works.")
            n_mechanical_green += 1
            method = "mechanical"
        else:
            bin_, machine, human, needs, rationale = classify_family(q, resp, exc_desc, agencies)
            n_family += 1
            method = "family_classifier"

        fnm_or_generic = any(a in ("O-FNM", "GENERIC") for a in agencies)
        topics = (retrieve_topics(sg, q + " " + resp)
                  if fnm_or_generic and bin_ != "NOT_A_CHECK" else [])
        source_rows = sorted({n for m in members for n in m.get("source_rows", [])})

        g = {"group": gid, "question": q, "condition": resp,
             "agencies": agencies,
             "severities": sorted({m["severity"] for m in members if m["severity"]}),
             "codes": sorted({m["exception_code"] for m in members if m["exception_code"]}),
             "source_spreadsheet": source_csv,
             "source_rows": source_rows,
             "rule_count": len(members), "bin": bin_,
             "classification_method": method,
             "machine_checkable": machine, "stays_human": human,
             "needed_data": needs, "rationale": rationale,
             "guide_candidates": topics,
             "sme_status": "PENDING REVIEW"}
        out_groups.append(g)
        group_counter[bin_] += 1
        rule_counter[bin_] += len(members)

    result = {"block": BLOCK, "rules_total": len(rules),
              "unique_groups": len(groups),
              "bins_by_group": dict(group_counter),
              "bins_by_rule": dict(rule_counter),
              "classification_counts": {"mechanical_not_a_check": n_mechanical_notacheck,
                                        "mechanical_green_doc_presence": n_mechanical_green,
                                        "hand_override": n_override,
                                        "family_classifier": n_family},
              "classifier": "Claude (compile-time analyst), session 2026-07-30 — PENDING SME REVIEW",
              "groups": out_groups}
    with open(OUT_JSON, "w") as f:
        json.dump(result, f, indent=1, sort_keys=True)

    # ------------------------------------------------------------ SME packet
    lines = ["# SME Review Packet — property-appraisal-review block triage",
             "",
             "**%d rules / %d unique (question, condition) groups.** Every classification"
             % (len(rules), len(groups)),
             "below is a *proposal* pending your review — mark each check agree / correct.",
             "Bins: GREEN = automatable now · YELLOW = automatable after data/guide work ·",
             "RED = stays human · NOT_A_CHECK = pass/N-A answer option, not a defect rule.",
             "",
             "**Source workbook:** `%s` — row numbers below are Excel-style" % source_csv,
             "(header = row 1), so you can open the sheet and jump straight to each rule.",
             "",
             "**Note on this block vs the prior two:** dedup collapse is minimal (714 rules "
             "-> 696 groups, ~1.03x, matching asset-verification's ~1.02x, not application-"
             "verification's ~1.5x). Unlike either prior block, **zero** groups mechanically "
             "resolve to an already-`mapped` SHACL shape — all 7 existing property-appraisal "
             "shapes are wired to zero AMQ exception codes today (same latent bug already "
             "fixed for LargeDepositShape/GiftEvidenceShape in decisions 017/018) — and an "
             "explicit, row-by-row search for safe direct wires against all 7 found **none** "
             "(see decision 020: 3 of the 7 shapes have no matching AMQ row in this workbook "
             "at all; the other 4 have near-miss candidates that each test a materially "
             "different condition on close reading — flagged as YELLOW/worth-SME-review in "
             "this packet, not proposed as ready-to-build). Given the scale (%d groups needed "
             "individual classification), most are classified by a documented, auditable "
             "regex-family classifier (see `layer2_triage_property_appraisal.py`'s module "
             "docstring and `classify_family()`) rather than hand-typed one at a time — every "
             "row's rationale below still cites its own actual condition text, and the "
             "highest-value candidates (existing-shape near-misses, external-registry Bucket-C "
             "flags, and the appraisal-presence regex-widening gap) are individually hand-"
             "verified overrides, not classifier output." % n_family,
             ""]
    defect_groups = [g for g in out_groups if g["bin"] != "NOT_A_CHECK"]
    ng = len(defect_groups)
    lines.append("## Headline")
    lines.append("")
    lines.append("| Bin | Groups | Rules | % of defect groups |")
    lines.append("|---|---|---|---|")
    for b in ("GREEN", "YELLOW", "RED"):
        gc = group_counter[b]
        lines.append("| %s | %d | %d | %d%% |" % (b, gc, rule_counter[b],
                                                  round(100.0 * gc / ng)))
    lines.append("| NOT_A_CHECK | %d | %d | — |"
                 % (group_counter["NOT_A_CHECK"], rule_counter["NOT_A_CHECK"]))
    lines.append("")
    lines.append("## Existing-shape near-miss candidates (verified, NOT ready to build)")
    lines.append("")
    near_miss_gids = [151, 279, 375, 511, 275, 276, 281, 282, 283, 423, 485, 493,
                      40, 676, 677, 37, 39, 41, 96, 270, 204]
    for gid in near_miss_gids:
        g = next(x for x in out_groups if x["group"] == gid)
        lines.append("- **G%03d** (%s, row%s %s): %s"
                     % (gid, "/".join(g["agencies"]),
                        "s" if len(g["source_rows"]) > 1 else "",
                        ", ".join(str(n) for n in g["source_rows"]), g["rationale"]))
    lines.append("")
    for b in ("GREEN", "YELLOW", "RED", "NOT_A_CHECK"):
        lines.append("## %s" % b)
        lines.append("")
        for g in out_groups:
            if g["bin"] != b:
                continue
            lines.append("### G%03d — %s [%s]" % (g["group"],
                         ", ".join(g["codes"][:4]) + ("…" if len(g["codes"]) > 4 else ""),
                         "/".join(g["agencies"])))
            lines.append("- **Q:** %s" % g["question"])
            lines.append("- **Defect condition:** %s" % (g["condition"] or "(none)"))
            lines.append("- **Source:** %s, row%s %s"
                         % (g["source_spreadsheet"],
                            "s" if len(g["source_rows"]) > 1 else "",
                            ", ".join(str(n) for n in g["source_rows"])))
            if g["severities"]:
                lines.append("- **Severity:** %s" % "/".join(g["severities"]))
            if g["machine_checkable"] != "-":
                lines.append("- **Machine checks:** %s" % g["machine_checkable"])
            if g["stays_human"] != "-":
                lines.append("- **Stays human:** %s" % g["stays_human"])
            if g["needed_data"] != "-":
                lines.append("- **Data needed:** %s" % g["needed_data"])
            lines.append("- **Rationale:** %s" % g["rationale"])
            lines.append("- **Classified by:** %s" % g["classification_method"])
            for t in g["guide_candidates"]:
                lines.append("- **Guide candidate:** %s — %s (PDF p.%d)"
                             % (t["code"], t["title"], t["pdf_page"]))
            lines.append("- **SME:** [ ] agree [ ] correct: ______")
            lines.append("")
    with open(OUT_MD, "w") as f:
        f.write("\n".join(lines) + "\n")

    print("Triage: %d rules -> %d groups | by group: %s | by rule: %s"
          % (len(rules), len(groups), dict(group_counter), dict(rule_counter)))
    print("Classification methods: mechanical_not_a_check=%d mechanical_green=%d "
          "hand_override=%d family_classifier=%d"
          % (n_mechanical_notacheck, n_mechanical_green, n_override, n_family))
    print("Packet: %s" % os.path.relpath(OUT_MD, HERE))


if __name__ == "__main__":
    main()
