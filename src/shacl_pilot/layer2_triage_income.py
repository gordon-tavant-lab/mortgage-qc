#!/usr/bin/env python3
"""
Layer-2 triage — income-verification block (616 rules, 580 unique groups).

Same method and bin definitions as layer2_triage.py (application-verification,
81->54) and layer2_triage_assets.py (asset-verification, 304->297); read those
module docstrings for the GREEN/YELLOW/RED/NOT_A_CHECK definitions, unchanged
here. This is the third and largest block triaged so far.

Structural differences from the two reference scripts, all deliberate:

1. Dedup collapses only slightly: 616 rules -> 580 unique groups (~1.06x) —
   in between application-verification's ~1.5x and asset-verification's
   ~1.02x. The 5 AMQ agencies mostly write independent condition text per
   income sub-type, but a genuine set of literally-duplicated condition texts
   recurs across many different AMQ "Question Text" categories (see
   RECURRING_CODE_FAMILIES below) — the same duplicate-condition-under-a-
   different-question-category pattern asset-verification's G040/G081/G102
   triage found, just much more of it here (19 duplicate "Income Breakdown"
   groups alone).

2. GREEN and the one NOT_A_CHECK screening-answer override are derived
   mechanically from amq_compiler.py's own eval_class + a pass/N-A regex,
   exactly as asset-verification did. UNLIKE asset-verification, there is
   ZERO "mapped" eval_class in this block today: MAPPED_SHAPES lists
   "SelfEmployedDocsShape" for income-verification but wires it to
   amq_exception_codes: [] (same "shape exists, wired to nothing" bug pattern
   already fixed for GiftEvidenceShape/LargeDepositShape in decisions
   017/018) — so GREEN here is 100% doc_presence auto-compiles, 0% mapped.

3. Given the scale (474 groups needing real judgment, vs asset-verification's
   ~210), the "read every row, write one dict entry" approach used for the
   first two blocks does not scale token-for-token. Instead:
     a. Six recurring exception-code FAMILIES that appear verbatim under many
        different AMQ question categories (Income Breakdown x19, VVOE
        Inactive x7, 3rdParty x5, IncomeWork x5, plus five smaller ones) are
        classified ONCE by family, not once per repetition — each is read in
        full, the underlying fact and gap is stated honestly, and the same
        classification is applied everywhere that exact code recurs. This is
        the same principle asset-verification used for its duplicate-
        condition rows (G040/G081/G102), just applied to families that repeat
        far more than 2-3 times here.
     b. Six groups that are genuinely bare judgment calls or open-ended
        catch-alls (no nameable document, no threshold, no defined test) are
        individually hand-classified RED, each with its own rationale
        (RED_GROUPS below) — read in full against the actual condition text,
        not inferred from a keyword alone (several candidates that LOOK
        judgment-flavored on a keyword scan, e.g. "not supported and logical"
        attached to a stated 20% threshold, or "unreasonable" attached to a
        crisp presence-of-analysis fact, were read in full and reclassified
        YELLOW because a genuinely checkable fact survives the judgment
        wording — see decision 021 for the individual call-outs).
     c. Two groups (O-VA-00364, O-FHA-02293) are the verified READY_TO_BUILD
        candidates for wiring into the already-existing but zero-exception-
        code-wired SelfEmployedDocsShape — verified against the shape's
        actual SPARQL logic per the decision-018 discipline, see below.
     d. Every remaining group (the overwhelming majority) is classified
        YELLOW by a deterministic keyword scan of its own condition text
        against a curated list of income-document families (INCOME_DOC_
        FAMILIES below) — the classifier states, per group, which specific
        document/fact family the row is missing, grounded in the row's own
        text, not a generic placeholder. This mirrors, at larger scale, the
        same finding asset-verification made: the block's math is mostly
        well-defined by agency guides, but the SME's 5-loan synthetic corpus
        was built to cover one wage-earner + one self-employed + one USDA
        income profile, not the 20+ distinct income types (military,
        alimony, rental, trust, RSU, retirement, disability, foster care,
        Section 8, MCC, ...) this AMQ category spans.

READY_TO_BUILD verification (decision-018 discipline applied explicitly):
  SelfEmployedDocsShape (CHK-INC-001, blocks/income.ttl) fires when
  `borrower_self_employed = true` AND (`ytd_pnl_in_file = false` OR
  `ytd_balance_sheet_in_file = false`) — an OR/either-missing test, extracted
  today from loan 04's Self-Employed Income Documentation Index (both facts
  genuinely populate: that loan's index marks both YTD P&L and YTD balance
  sheet "NOT IN FILE"). Two AMQ rows describe exactly this same real-world
  condition, both read in full before being proposed:
    O-VA-00364:  response "File missing a YTD P&L and current balance sheet
                 as applicable or as per AUS for self-employed"; exception_
                 description "...the file did not contain a YTD profit and
                 loss statement and current balance sheet as applicable or
                 as per AUS."
    O-FHA-02293: response "A YTD profit and loss statement and balance sheet
                 were not provided"; exception_description "A YTD P&L and
                 balance sheet was required but not in the file where more
                 than a calendar quarter has elapsed..."
  Both describe the "required P&L+balance-sheet PACKAGE not in file" — the
  natural reading of "not in file"/"not provided" applied to a named pair of
  documents is that the package is incomplete if EITHER is absent, matching
  the shape's OR logic. A keyword sweep of the full 474-group text for every
  other agency's self-employed/business-income rows found no other row
  mentioning both "profit and loss" and "balance sheet" together — these two
  are the ONLY matches, not a guess. Kept YELLOW (not GREEN) because wiring
  is a proposed amq_compiler.py change, not yet made — matches asset-
  verification's own precedent (its G135/G102 READY_TO_BUILD candidates also
  stayed YELLOW pending a human decision).

Outputs:
  compiled/triage_income-verification.json
  out/TRIAGE-PACKET-income-verification.md
"""
import json
import os
import re
from collections import OrderedDict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
RULESET = os.path.join(HERE, "compiled", "ruleset.json")
SG_INDEX = os.path.join(HERE, "compiled", "selling_guide_index.json")
OUT_JSON = os.path.join(HERE, "compiled", "triage_income-verification.json")
OUT_MD = os.path.join(HERE, "out", "TRIAGE-PACKET-income-verification.md")

BLOCK = "income-verification"

PASS_RE = re.compile(r"^(Yes,|Not Applicable)", re.I)

# G580 ("What type of income was used to qualify the loan?" -> "Alimony,
# Child Support, Maintenance and/or Other Nontaxable Income") is a screening/
# categorization answer branch, not a defect condition — same pattern as
# application-verification's group 10 and asset-verification's group 291.
NOT_A_CHECK_OVERRIDES = {580}

# ---------------------------------------------------------------------------
# READY TO BUILD (task C): verified per decision-018 discipline against
# SelfEmployedDocsShape's actual SPARQL (blocks/income.ttl) — see module
# docstring. Flagged here, NOT implemented (amq_compiler.py untouched).
READY_TO_BUILD = {
    "O-VA-00364": ("WIRE, don't build — SelfEmployedDocsShape (CHK-INC-001) already "
        "checks exactly this fact (borrower_self_employed AND (ytd_pnl_in_file=false "
        "OR ytd_balance_sheet_in_file=false)), extracted today from loan 04's "
        "Self-Employed Income Documentation Index (both facts populate: that index "
        "marks both docs NOT IN FILE). MAPPED_SHAPES wires the shape to ZERO "
        "amq_exception_codes today. Row's exception_description ('the file did not "
        "contain a YTD profit and loss statement and current balance sheet') reads "
        "naturally as the same either-missing test the shape already implements."),
    "O-FHA-02293": ("WIRE, don't build — same fact as O-VA-00364, FHA wording variant "
        "('A YTD P&L and balance sheet was required but not in the file'). Verified: "
        "a full-text keyword sweep of every other self-employed/business-income row "
        "in this block found no other agency row mentioning both 'profit and loss' "
        "and 'balance sheet' together — these two are the only matches."),
}

# ---------------------------------------------------------------------------
# RED groups (task B self-check c): bare judgment calls / open-ended catch-
# alls with NO nameable document, threshold, or defined test surviving in the
# full condition text (question + response + exception_description all read).
# Several keyword-flagged candidates were read in full and reclassified
# YELLOW instead (see decision 021) because a genuinely checkable fact (a
# stated percentage, a presence-of-document fact) survived the judgment
# wording — these six did not.
RED_GROUPS = {
    25: ("RED", "-", "'not addressed by VA' undefined-income-type catch-all + "
         "'continuance was unreasonable' judgment", "-",
         "Income source not otherwise addressed by VA guidance is, by definition, "
         "not enumerable today — no defined document or threshold exists to check "
         "against until an SME decomposes what 'sufficiently documented' would even "
         "mean for an unnamed income type. Same catch-all pattern as asset-"
         "verification's G018/G023/G196 (VA/RHS bare 'all requirements' rows)."),
    122: ("RED", "-", "underwriter's own stability/continuance analysis judged "
          "'does not support' its conclusion — an adequacy-of-analysis judgment, "
          "not mere presence", "-",
          "Distinct from the many 'analysis not documented' rows elsewhere in this "
          "block (which are presence checks, kept YELLOW): here the analysis EXISTS "
          "and the question is whether its content 'supports' stability and "
          "continuance — a judgment on analytical adequacy with no defined bright-"
          "line test, same class as asset-verification's G228 (underwriter review-"
          "completeness sweep)."),
    168: ("RED", "-", "cross-file 'noted income discrepancies... resolved' sweep",
          "-", "Open-ended discrepancy-resolution judgment scoped to 'noted' "
          "discrepancies with no definition of which ones or what standard "
          "resolves them — same class as application-verification's G07 (file-wide "
          "discrepancies-not-explained catch-all)."),
    180: ("RED", "-", "'reasonable and stable' judgment on an asset-based income "
          "source, with no accompanying threshold or document named", "-",
          "Bare reasonableness/stability determination — exception_description adds "
          "no crisp element ('without determining that the source... and/or the "
          "amount... was reasonable and stable'). Same class as asset-verification's "
          "G035 (unreasonable-savings judgment with no computable data behind it "
          "either)."),
    310: ("RED", "-", "'necessary additional documentation... to evaluate, justify "
          "and explain the qualification' — fully open-ended, no specific document "
          "or fact named", "-",
          "Bare catch-all with zero stated specifics, same pattern as asset-"
          "verification's G101 ('third-party verification requirements', "
          "unspecified)."),
    538: ("RED", "-", "'self-employment income is not stable' — bare conclusion, no "
          "accompanying document or threshold", "-",
          "exception_description adds nothing beyond restating the conclusion "
          "('did not meet stability requirements'). Distinct from the many self-"
          "employed rows elsewhere in this block that name a specific document "
          "(tax returns, P&L, business credit report) — this one names none."),
}

# ---------------------------------------------------------------------------
# Recurring exception-code families: the SAME literal condition text recurs
# under many different AMQ "Question Text" categories (verified by grep, see
# decision 021) — classified once per family, applied to every repetition.
SPECIAL_CODE_FAMILIES = {
    "Income Breakdown": ("YELLOW", "-", "-",
        "a DU/LP (or equivalent AUS) findings export to compare against the "
        "per-income-type breakdown submitted, cross-referenced with the AUS-"
        "categorization amq_compiler.py would need to compute",
        "Recurs identically (verbatim condition text) under 19 different AMQ "
        "question categories (automobile allowance, alimony, disability, "
        "employment, general income, housing assistance, military, other income, "
        "retirement, self-employed, trust income, ...) — one underlying fact "
        "(AUS income-categorization accuracy), same AUS-submission-export gap "
        "already flagged in the asset-verification triage (no DU/LPA findings "
        "export exists in this pilot for FNM/FRD; only RHS's GUS findings are "
        "partially parsed, for loan 05)."),
    "VVOE Inactive": ("YELLOW", "-", "-",
        "a VVOE (verbal verification of employment) log/status fact — not "
        "currently modeled; the corpus has a written/signed VOE (loan 01) but no "
        "distinct verbal-VOE artifact with an active/inactive status field",
        "Recurs identically under 7 different AMQ question categories. The "
        "written VOE this pilot extracts (employment_start_date_voe) is a "
        "different document from a VVOE call/database log; no such artifact "
        "exists in any of the 5 synthetic loans."),
    "3rdParty": ("YELLOW", "-", "-",
        "a VOE-vendor-name field (e.g. Equifax/The Work Number) — not currently "
        "captured from any document",
        "Recurs identically under 5 different AMQ question categories. Crisp "
        "presence/identity check once a vendor-name field exists; no such field "
        "is in FIELD_SPECS['voe'] today."),
    "IncomeWork": ("YELLOW", "presence of an income-calculation worksheet",
        "'income discrepancies were not explained' clause (appended, open-ended)",
        "income-calculation-worksheet document type — not in the corpus",
        "Recurs identically under 5 different AMQ question categories. Presence "
        "half is crisp once the worksheet doc type is modeled; the appended "
        "discrepancy-explanation clause stays partly human, same pattern as "
        "asset-verification's G007 (crisp presence + appended open catch-all "
        "kept YELLOW, not RED)."),
    "DecliningIncDocument": ("YELLOW",
        "multi-year income trend detection (declining year-over-year) + "
        "presence of a written explanation", "-",
        "multi-year per-income-type income history (not currently extracted "
        "beyond a single point-in-time base_monthly_income_1003) + an "
        "explanation-document presence fact",
        "Recurs under 2 AMQ question categories (general employment income, "
        "self-employed). No judgment word in the condition itself ('declining' "
        "and 'no explanation provided' are both factual, not evaluative) — "
        "blocked purely on missing multi-year income data, not a rule-clarity "
        "problem."),
    "SE Deductions": ("YELLOW", "-", "-",
        "Schedule C 'meals & entertainment' and 'notes payable < 1 year' "
        "deduction line items — not in FIELD_SPECS for any self-employed doc "
        "type today",
        "Single AMQ row (O-FNM, self-employed block); crisp math once the two "
        "named Schedule C line items are extracted — genuinely a Schedule C tax-"
        "return field, not in the 5-loan corpus (loan 04's SE index tracks only "
        "P&L/balance-sheet presence, not line-item detail)."),
    "Income - Other": ("YELLOW", "-", "-",
        "SSI gross-up documentation fields — not currently captured",
        "Single AMQ row (O-FNM); presence/support check once the gross-up "
        "documentation field exists."),
    "EmploymentGaps": ("YELLOW", "presence of an employment-gap explanation", "-",
        "an employment-gap-explanation document/field — not currently captured",
        "Recurs under 2 AMQ question categories (FNM/VA); pure presence check, "
        "same pattern as many other 'X not addressed/documented' rows in this "
        "block."),
    "RentalCalcDoc": ("YELLOW", "presence of a net-rental-income/loss worksheet",
        "-", "net-rental-income worksheet document type — not in the corpus",
        "Single AMQ row (O-FNM); crisp presence check once the worksheet doc "
        "type is modeled; no rental-income document of any kind exists in the "
        "5-loan corpus today."),
    "Paystub Loans": ("YELLOW", "-", "-",
        "a paystub-level 'loans/deductions' line-item field — not in "
        "FIELD_SPECS['paystub'] today",
        "Single AMQ row (O-FRD); crisp cross-check against liabilities/DTI once "
        "the paystub deduction-line field exists."),
    "IncomeSEVerification": ("YELLOW", "presence of a third-party business-"
        "verification document (e.g. CPA letter)", "-",
        "CPA-letter/third-party-verification document type — not in the corpus",
        "Single AMQ row (O-FNM); exception_description names the specific "
        "missing artifact plainly ('CPA letter not provided') — crisp presence "
        "check once that doc type is modeled."),
    "Epic4506C": ("YELLOW", "-", "-",
        "a lender-system (EPIC) 4506-C screen-completeness fact — not derivable "
        "from any loan document; this is internal LOS/servicing-system screen "
        "data, not a document in the closed-loan file",
        "Recurs across all 5 agencies under 'IRS Form 4506-C requirements'; "
        "genuinely different in kind from the other 4506-C rows (which check "
        "the signed FORM itself) — this checks an internal system screen's "
        "state, closer to the Bucket-C external-system-state pattern flagged "
        "for the NMLS/RE-license rules (decisions 016/017) than a document-"
        "presence gap, though not itself a live external registry lookup. "
        "Kept YELLOW, flagged for a human to consider whether it belongs in "
        "scope at all."),
}

# ---------------------------------------------------------------------------
# Fallback keyword -> document/fact family, applied to every remaining group's
# own (question + response + exception_description) text. First match wins.
# Grounded in the row's own text — never invents a family the text doesn't
# itself point to (Non-Negotiable #1's grounding rule).
INCOME_DOC_FAMILIES = [
    (r"4506-c|8821", "IRS Form 4506-C/8821 tax-transcript consent form"),
    (r"verbal verification|\bvvoe\b|verbal verif", "verbal VOE (VVOE) call/database log"),
    (r"equifax|\btwn\b|third[- ]party voe|3rd party voe", "third-party VOE vendor identity field"),
    (r"leave and earnings statement|\bles\b\W|military", "military Leave & Earnings Statement (LES) / VA benefits award letter"),
    (r"schedule k-?1|\bk-1\b|\b1065\b|1120s", "K-1 / Form 1065 / 1120S business tax-return schedule"),
    (r"schedule c\b", "Schedule C business tax-return page"),
    (r"schedule e\b", "Schedule E rental-income tax-return page"),
    (r"\b1099\b|form 4137", "1099 (or Form 4137 tip-income) tax form"),
    (r"tax return|tax transcript|irs form 1040", "personal/business tax return or IRS transcript"),
    (r"trust agreement|trustee|trust income", "trust agreement/trustee statement"),
    (r"restricted stock|\brs/rsu\b|\brsu\b|vesting schedule", "RSU/restricted-stock vesting-schedule document"),
    (r"\blease\b|form 1007|form 1025|schedule e|rental income|boarder", "lease / Schedule E / Form 1007-1025 rental-income document"),
    (r"award letter|benefits letter|ssa-1099|social security administration|notice of award", "benefits/award letter (SSA, VA, pension, or disability payer)"),
    (r"401\(k\)|\bira\b|keogh|retirement account|pension", "retirement-account statement (401(k)/IRA/Keogh/pension)"),
    (r"disability", "disability-benefits payer statement"),
    (r"alimony|child support|maintenance|divorce decree|separation agreement|court order", "alimony/child-support legal decree or written agreement"),
    (r"foster care", "foster-care sponsoring-organization verification letter"),
    (r"mortgage credit certificate|\bmcc\b", "Mortgage Credit Certificate (MCC) document"),
    (r"section 8|housing choice voucher|housing voucher", "Section 8 / Housing Choice Voucher award letter"),
    (r"employer housing subsidy|housing allowance|parsonage", "employer housing-subsidy / parsonage agreement"),
    (r"employer.{0,15}assist|mortgage differential", "employer-subsidy / mortgage-differential agreement letter"),
    (r"auto(mobile)? allowance", "automobile-allowance employer letter"),
    (r"cryptocurrency|virtual currency", "cryptocurrency/virtual-currency income-conversion documentation (same gap flagged in the asset-verification triage)"),
    (r"notes receivable", "notes-receivable promissory note + deposit evidence"),
    (r"royalty", "royalty contract/agreement + tax-return schedule"),
    (r"capital gains", "capital-gains tax-return schedule (Schedule D) history"),
    (r"employment offer|employment contract|anticipated income|new employment", "employment offer/contract letter (anticipated/new-employment income)"),
    (r"w-?2s?\b", "W-2 form(s)"),
    (r"paystub", "paystub"),
    (r"income calculation worksheet|income calculator", "income-calculation worksheet/tool output"),
    (r"cash flow analysis|comparative income analysis|form 1084|form 1088|form 91", "self-employed income-analysis form (Form 91/1084/1088)"),
    (r"business tax return|business credit report|business existence|cpa letter", "business tax return / business credit report / business-existence verification"),
    (r"gus|residual income", "GUS findings / USDA residual-income worksheet field"),
    (r"employment.related asset|lump.sum distribution", "employment-related-asset / lump-sum-distribution qualifying-income documentation"),
    (r"deduction|elderly household|dependent deduction|child care expense", "RHS household-income deduction eligibility documentation"),
    (r"fluctuat", "multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure)"),
    (r"vom\b|mortgage payment history", "VOM (mortgage payment history) field"),
]

THRESHOLD_RE = re.compile(r"\b\d{1,3}%|\$[\d,]+|\b\d{1,2}[- ]?(?:year|yr|month|mo|day)s?\b", re.I)


def tokens(text):
    stop = set("were all the of and or a an is in to for was not on by with as at have "
               "been requirements met all any".split())
    return {w for w in re.findall(r"[a-z]{3,}", text.lower())} - stop


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


def classify_fallback(q, resp, desc):
    text = "%s %s %s" % (q, resp, desc)
    tl = text.lower()
    for pat, family in INCOME_DOC_FAMILIES:
        if re.search(pat, tl):
            has_threshold = bool(THRESHOLD_RE.search(text))
            machine = ("threshold/date comparison once the field exists"
                       if has_threshold else "-")
            needs = family + " — not among the doc/field types the 5-loan " \
                    "synthetic corpus extracts today"
            rationale = ("Crisp presence/%s check once %s is captured; this "
                         "income sub-type's documentation is absent from all 5 "
                         "synthetic loans (which cover one W-2 wage-earner "
                         "profile, one self-employed profile with only P&L/"
                         "balance-sheet presence tracked, and one USDA income-"
                         "limit profile) — same root cause as the asset-"
                         "verification triage's dominant finding, not a rule-"
                         "clarity problem."
                         % ("threshold" if has_threshold else "documentation",
                            family))
            return "YELLOW", machine, "-", needs, rationale
    # no document keyword matched at all: bare calculation/requirement text
    rationale = ("No document family is named in this row's own text (question, "
                "response, and exception description all read) — the condition "
                "reduces to a bare 'calculated/met requirements' statement. The "
                "underlying math or requirement IS defined by the relevant "
                "agency's Selling/AMQ guide for this income type (a citation, "
                "not a new number, per this project's grounding rule), but no "
                "income-type-specific source field for it exists in the 5-loan "
                "corpus yet — blocked on missing fixture/field breadth, not "
                "rule clarity.")
    return "YELLOW", "-", "-", "income-type-specific source fields (not yet in FIELD_SPECS)", rationale


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

    if len(groups) != 580:
        raise SystemExit("Expected 580 unique groups for a fresh compile of %d "
                         "income-verification rules; got %d. Ruleset changed — "
                         "re-review before trusting this triage." % (len(rules), len(groups)))

    out_groups, group_counter, rule_counter = [], Counter(), Counter()
    ready_hits = Counter()
    for gid, ((q, resp), members) in enumerate(groups.items(), 1):
        agencies = sorted({m["agency"] for m in members})
        ecs = sorted({m["eval_class"] for m in members})
        codes = sorted({m["exception_code"] for m in members})
        descs = " ".join(sorted({m.get("exception_description", "") for m in members
                                 if m.get("exception_description")}))
        blocked_on_fixture = any(m["eval_class"] == "blocked_on_missing_fixture"
                                for m in members)
        ready_note = None

        if gid in NOT_A_CHECK_OVERRIDES:
            bin_, machine, human, needs, rationale = (
                "NOT_A_CHECK", "-", "-", "-",
                "Screening/categorization answer branch ('what type of income was "
                "used'), not a defect condition — same pattern as application-"
                "verification's LEP-applicability screening group and asset-"
                "verification's group 291.")
        elif PASS_RE.match(resp.strip()):
            bin_, machine, human, needs, rationale = (
                "NOT_A_CHECK", "-", "-", "-",
                "Pass/N-A answer option, not a defect condition.")
        elif ecs == ["doc_presence"]:
            targets = sorted({m["eval_target"] for m in members})
            bin_, machine, human, needs, rationale = (
                "GREEN", "auto-compiled doc-presence check on: %s" % ", ".join(targets),
                "-", "-",
                "Auto-compiled by amq_compiler.py's doc_presence classifier — "
                "already works.")
        else:
            special = next((c for c in codes if c in SPECIAL_CODE_FAMILIES), None)
            ready = next((c for c in codes if c in READY_TO_BUILD), None)
            if gid in RED_GROUPS:
                bin_, machine, human, needs, rationale = RED_GROUPS[gid]
            elif ready:
                bin_, machine, human, needs, rationale = (
                    "YELLOW",
                    "SelfEmployedDocsShape's existing borrower_self_employed + "
                    "ytd_pnl_in_file/ytd_balance_sheet_in_file logic",
                    "-", "none if wired — see READY_TO_BUILD",
                    "READY TO BUILD candidate — verified per decision-018 "
                    "discipline; see module docstring / decision 021.")
                ready_note = READY_TO_BUILD[ready]
                ready_hits[ready] += 1
            elif special:
                bin_, machine, human, needs, rationale = SPECIAL_CODE_FAMILIES[special]
            else:
                bin_, machine, human, needs, rationale = classify_fallback(q, resp, descs)

        if blocked_on_fixture and bin_ not in ("NOT_A_CHECK", "GREEN"):
            bin_ = "YELLOW"
            rationale = ("BLOCKED ON MISSING FIXTURE (decision 014 principle), not a "
                        "rule-clarity problem: " + rationale)

        fnm_or_generic = any(a in ("O-FNM", "GENERIC") for a in agencies)
        topics = (retrieve_topics(sg, q + " " + resp)
                  if fnm_or_generic and bin_ != "NOT_A_CHECK" else [])
        source_rows = sorted({n for m in members for n in m.get("source_rows", [])})

        g = {"group": gid, "question": q, "condition": resp,
             "agencies": agencies,
             "severities": sorted({m["severity"] for m in members if m["severity"]}),
             "codes": codes,
             "source_spreadsheet": source_csv,
             "source_rows": source_rows,
             "rule_count": len(members), "bin": bin_,
             "blocked_on_missing_fixture": blocked_on_fixture,
             "machine_checkable": machine, "stays_human": human,
             "needed_data": needs, "rationale": rationale,
             "ready_to_build": ready_note,
             "guide_candidates": topics,
             "sme_status": "PENDING REVIEW"}
        out_groups.append(g)
        group_counter[bin_] += 1
        rule_counter[bin_] += len(members)

    result = {"block": BLOCK, "rules_total": len(rules),
              "unique_groups": len(groups),
              "bins_by_group": dict(group_counter),
              "bins_by_rule": dict(rule_counter),
              "classifier": "Claude (compile-time analyst), session 2026-07-30 — PENDING SME REVIEW",
              "groups": out_groups}
    with open(OUT_JSON, "w") as f:
        json.dump(result, f, indent=1, sort_keys=True)

    # ------------------------------------------------------------ SME packet
    lines = ["# SME Review Packet — income-verification block triage",
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
             "**Note on this block vs the first two:** dedup collapse (616 rules -> 580 "
             "groups, ~1.06x) sits between application-verification's ~1.5x and asset-"
             "verification's ~1.02x. GREEN is 100% doc_presence auto-compiles (0% "
             "'mapped' — the block's one hand-built shape, SelfEmployedDocsShape, is "
             "wired to zero AMQ exception codes today, the same latent-shape bug already "
             "fixed for GiftEvidenceShape/LargeDepositShape). Given ~474 groups needing "
             "real judgment (more than double asset-verification's ~210), six recurring "
             "exception-code families that repeat verbatim under many different AMQ "
             "question categories (Income Breakdown x19, VVOE Inactive x7, 3rdParty x5, "
             "IncomeWork x5, plus smaller ones) were classified once per family rather "
             "than once per repetition; the remaining groups were classified by a "
             "deterministic keyword scan of each row's own text against a curated list "
             "of income-document families, stating per group which specific document/"
             "fact family is missing — see `layer2_triage_income.py`'s module docstring "
             "for the full method and decision 021 for the six individually hand-"
             "verified RED calls and the two verified READY_TO_BUILD candidates.",
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
    lines.append("## READY TO BUILD candidates (flagged, not implemented)")
    lines.append("")
    for g in out_groups:
        if g["ready_to_build"]:
            lines.append("- **G%03d** (%s, row%s %s, codes %s): %s"
                         % (g["group"], "/".join(g["agencies"]),
                            "s" if len(g["source_rows"]) > 1 else "",
                            ", ".join(str(n) for n in g["source_rows"]),
                            ", ".join(g["codes"]), g["ready_to_build"]))
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
            if g["ready_to_build"]:
                lines.append("- **READY TO BUILD:** %s" % g["ready_to_build"])
            for t in g["guide_candidates"]:
                lines.append("- **Guide candidate:** %s — %s (PDF p.%d)"
                             % (t["code"], t["title"], t["pdf_page"]))
            lines.append("- **SME:** [ ] agree [ ] correct: ______")
            lines.append("")
    with open(OUT_MD, "w") as f:
        f.write("\n".join(lines) + "\n")

    print("Triage: %d rules -> %d groups | by group: %s | by rule: %s"
          % (len(rules), len(groups), dict(group_counter), dict(rule_counter)))
    print("Ready-to-build hits: %s" % dict(ready_hits))
    print("Packet: %s" % os.path.relpath(OUT_MD, HERE))


if __name__ == "__main__":
    main()
