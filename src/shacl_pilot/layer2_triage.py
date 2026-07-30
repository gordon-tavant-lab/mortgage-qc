#!/usr/bin/env python3
"""
Layer-2 triage — application-verification block (81 rules, 55 unique texts).

For every rule in the block, produce the three-bin classification (decision 009's
Layer-2, first executed here):

  GREEN        machine-checkable now: condition is crisp AND the data is (or is
               trivially) extractable. Some GREEN rules note a residual human part
               (e.g. "accuracy" of a section can't be automated; presence/signature
               can).
  YELLOW       checkable after work: condition is clear (or clear once the cited
               guide text is read) but needs extraction-contract widening (new doc
               types / fields / dates) or an external data source.
  RED          human territory: judgment calls ("appears the borrower needed more
               space"), open-ended catch-alls ("all disclosures per guidelines"),
               or file-wide discrepancy sweeps. A trustworthy system routes these
               to a reviewer; it does not fake them.
  NOT_A_CHECK  the row is a pass/"Not Applicable" answer OPTION of the
               questionnaire, not a defect condition (workbook is an
               answer-capture form — see the rules-clarity review).

Classifications below were authored by the compile-time analyst (Claude, this
session) and are PENDING SME REVIEW — that is the point of the output packet.
Guide-topic retrieval (Fannie/generic rules only) is deterministic token-overlap
scoring against compiled/selling_guide_index.json (decision 012).

Outputs:
  compiled/triage_application_verification.json
  out/TRIAGE-PACKET-application-verification.md   (the SME review packet)
"""
import json
import os
import re
import sys
from collections import OrderedDict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
RULESET = os.path.join(HERE, "compiled", "ruleset.json")
SG_INDEX = os.path.join(HERE, "compiled", "selling_guide_index.json")
OUT_JSON = os.path.join(HERE, "compiled", "triage_application_verification.json")
OUT_MD = os.path.join(HERE, "out", "TRIAGE-PACKET-application-verification.md")

BLOCK = "application-verification"

# ---------------------------------------------------------------------------
# Classifications by stable group number (deterministic sort order of unique
# (question_text, response_text) pairs — same numbering as the session review).
# Fields: bin, machine (what automates), human (what stays human), needs (data
# to add), rationale.
C = {
    1:  ("YELLOW", "presence of documented LEP preference record", "adequacy of the record",
         "LEP preference form/doc type in extraction contract", "Best-practice; presence checkable once doc type is captured."),
    2:  ("YELLOW", "LEP disclosure presence + provided-date vs application-date", "-",
         "LEP disclosure doc type + its date field", "Presence crisp; 'timely' needs both dates."),
    3:  ("RED", "-", "whether translated docs matched the applicant's LEP preference",
         "-", "Depends on shop practice and preference nuance — reviewer judgment."),
    4:  ("NOT_A_CHECK", "-", "-", "-", "Pass/N-A answer option, not a defect condition."),
    5:  ("GREEN", "all 4 CIP fields (name, address, DOB, SSN) present on 1003/file", "-",
         "-", "Pure field-presence test; fields already in the extraction contract."),
    6:  ("NOT_A_CHECK", "-", "-", "-", "Pass answer option."),
    7:  ("RED", "-", "file-wide 'discrepancies not explained' sweep",
         "-", "Open-ended cross-file judgment; specific discrepancies belong to specific checks."),
    8:  ("GREEN", "1003 employment dates vs VOE/paystub dates", "-",
         "-", "ALREADY BUILT: EmploymentStartDateShape (CHK-APP-001), proven on loan 01."),
    9:  ("NOT_A_CHECK", "-", "-", "-", "Pass answer option."),
    10: ("NOT_A_CHECK", "-", "-", "-", "Screening answer option (LEP applicability), not a defect."),
    11: ("RED", "-", "catch-all 'all disclosures per guidelines'",
         "-", "Needs SME decomposition into enumerable VA disclosures before any automation."),
    12: ("GREEN", "LBP notice presence gated on year_built < 1978", "'timely' timing",
         "LBP notice doc type", "Same pattern as built LbpDisclosureShape; FHA variant."),
    13: ("YELLOW", "HUD-92564-CN presence", "'timely'",
         "doc type + provided date", "Presence easy; timing needs dates."),
    14: ("GREEN", "ARM pre-loan disclosure presence gated on AdjustableRate", "'timely'",
         "-", "ALREADY BUILT: ArmDisclosureShape (CHK-APP-007), proven on loan 03."),
    15: ("YELLOW", "VA Counseling Checklist presence + signature", "-",
         "doc type in inventory", "Signature detection exists; needs the doc type added."),
    16: ("YELLOW", "Informed Consumer Choice Disclosure presence", "-",
         "doc type", "Straight presence once doc type captured."),
    17: ("GREEN", "LE provided-date within 3 business days of application date", "-",
         "LE date + application date fields", "Crisp TRID rule; business-day math is deterministic."),
    18: ("YELLOW", "HUD-92900-B presence + signature", "-",
         "doc type", "Presence + signature pattern, doc type not yet in contract."),
    19: ("NOT_A_CHECK", "-", "-", "-", "Pass answer option."),
    20: ("NOT_A_CHECK", "-", "-", "-", "Pass answer option."),
    21: ("GREEN", "co-borrower employer + income presence + co-borrower signature (final 1003)",
         "'fully completed, correct'", "-",
         "BUILT 2026-07-29 (decision 015): CoBorrowerSectionCompleteShape (CHK-APP-008). "
         "Was miscategorized as needing a separate 'Additional Borrower form' document — "
         "verified via pdftotext that the co-borrower's data is inline in the same final "
         "1003 every loan already has; extract_loan.py's own 'first occurrence wins' logic "
         "was silently discarding it. Fixed by extract_coborrower_fields()."),
    22: ("GREEN", "final 1003 presence + signed + dated by all parties", "'incomplete, incorrect'",
         "-", "Presence/signature/date already extractable; content-accuracy stays human."),
    23: ("RED", "-", "'appears the borrower needed more space'",
         "-", "Inherently a judgment about handwriting/space; route to reviewer."),
    24: ("GREEN", "co-borrower employer + income presence + co-borrower signature (final 1003)", "'inaccurate'",
         "-", "BUILT 2026-07-29 (decision 015): same shape as #21 (CoBorrowerSectionCompleteShape, "
              "CHK-APP-008) — this row's condition text ('sections... not signed by all parties') "
              "and #21's ('Additional Borrower form... not signed') describe the same underlying "
              "gap; one check covers both AMQ exception codes."),
    25: ("RED", "-", "same 'needed more space' judgment", "-", "As #23."),
    26: ("GREEN", "HUD-92900-A presence + signatures by section", "'incomplete, incorrect'",
         "-", "ALREADY BUILT (signature core): Hud92900aBorrowerSigShape, proven on loan 02."),
    27: ("GREEN", "final application presence in file", "-",
         "-", "Pure doc presence; already inventoried."),
    28: ("GREEN", "Unmarried Addendum presence gated on marital_status = Unmarried", "-",
         "marital status field (extractable) + addendum doc type", "Well-defined conditional presence."),
    29: ("NOT_A_CHECK", "-", "-", "-", "Pass answer option."),
    30: ("GREEN", "as #21 (FNM variant)", "'fully completed, correct'",
         "-", "BUILT 2026-07-29: same CoBorrowerSectionCompleteShape as #21."),
    31: ("GREEN", "as #22 (FNM variant)", "'incomplete, incorrect'", "-", "Same as #22."),
    32: ("RED", "-", "'needed more space' judgment (FNM variant)", "-", "As #23."),
    33: ("GREEN", "as #28 (FNM variant)", "-", "same as #28", "Same as #28."),
    34: ("NOT_A_CHECK", "-", "-", "-", "Pass answer option."),
    35: ("YELLOW", "initial-URLA Additional Borrower form presence + signature", "completeness/correctness",
         "doc type + fields", "Initial-application variant of #21."),
    36: ("GREEN", "initial application presence + signed + dated", "'incomplete, incorrect'",
         "initial-1003 doc type distinct from final", "Same pattern as #22 for the initial URLA."),
    37: ("RED", "-", "'needed more space' judgment (initial)", "-", "As #23."),
    38: ("NOT_A_CHECK", "-", "-", "-", "N-A answer option."),
    39: ("YELLOW", "initial URLA per-section completeness + signatures", "'inaccurate'",
         "section-level fields", "As #24 for initial URLA."),
    40: ("YELLOW", "as #39 (FHA wording variant)", "'inaccurate'", "as #39", "Same as #39."),
    41: ("RED", "-", "'needed more space' judgment (FRD initial)", "-", "As #23."),
    42: ("YELLOW", "Form 1103 (SCIF) presence", "'fully completed'",
         "doc type + its fields", "Presence easy; completeness needs field list."),
    43: ("GREEN", "initial HUD-92900-A presence + signatures", "'incomplete, incorrect'",
         "-", "Initial-doc variant of #26; same machinery."),
    44: ("GREEN", "initial application presence in file", "-",
         "initial-1003 doc type", "Pure presence (FRD, Minor severity)."),
    45: ("YELLOW", "URLA originator NMLS ID vs licensing data", "-",
         "external NMLS registry lookup", "Deterministic once the external data source is wired."),
    46: ("GREEN", "as #28 (initial URLA variant)", "-", "as #28", "Same as #28."),
    47: ("NOT_A_CHECK", "-", "-", "-", "Pass answer option."),
    48: ("YELLOW", "as #42 (FNM variant)", "'fully completed'", "as #42", "Same as #42."),
    49: ("NOT_A_CHECK", "-", "-", "-", "Pass answer option."),
    50: ("YELLOW", "ROV-process disclosure presence at application", "-",
         "ROV disclosure doc type + date", "New requirement; guide topic retrievable for citation."),
    51: ("NOT_A_CHECK", "-", "-", "-", "N-A answer option."),
    52: ("GREEN", "Borrower Certification & Authorization presence", "-",
         "-", "Doc presence; loan 01's disclosure-package index already lists this doc family."),
    53: ("GREEN", "Flood Insurance Coverage Disclosure presence", "-",
         "doc type (index row exists in disclosure package)", "Doc presence via disclosure index."),
    54: ("GREEN", "Intent to Proceed presence (+ signed date)", "-",
         "-", "Field intent_to_proceed_signed_date ALREADY extracted on loan 01."),
    55: ("NOT_A_CHECK", "-", "-", "-", "N-A answer option."),
}

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

    # decision 016 removed one row (old group 45, NMLS lookup) from compilation
    # entirely — every group after it shifts down by exactly one position.
    # Verified empirically 2026-07-29 (positions 1-44 unchanged; new 45..54
    # match old 46..55 byte-for-byte) rather than assumed.
    REMOVED_OLD_GID = 45
    def old_gid(new_gid):
        return new_gid if new_gid < REMOVED_OLD_GID else new_gid + 1

    if len(groups) != len(C) - 1:
        raise SystemExit("Group count %d != classification count %d (minus the one "
                         "discarded NMLS group) — ruleset changed; re-review "
                         "classifications and the remap." % (len(groups), len(C)))

    out_groups, group_counter, rule_counter = [], Counter(), Counter()
    for new_gid, ((q, resp), members) in enumerate(groups.items(), 1):
        gid = old_gid(new_gid)
        bin_, machine, human, needs, rationale = C[gid]
        agencies = sorted({m["agency"] for m in members})
        fnm_or_generic = any(a in ("O-FNM", "GENERIC") for a in agencies)
        topics = (retrieve_topics(sg, q + " " + resp)
                  if fnm_or_generic and bin_ not in ("NOT_A_CHECK",) else [])
        source_rows = sorted({n for m in members for n in m.get("source_rows", [])})
        blocked_on_fixture = any(m["eval_class"] == "blocked_on_missing_fixture"
                                for m in members)
        if blocked_on_fixture and bin_ != "NOT_A_CHECK":
            bin_ = "YELLOW"  # decision 014: legitimate rule, never RED/discarded
            rationale = ("BLOCKED ON MISSING FIXTURE (decision 014), not a "
                        "rule-clarity problem: " + rationale)
        g = {"group": new_gid, "question": q, "condition": resp,
             "agencies": agencies,
             "severities": sorted({m["severity"] for m in members if m["severity"]}),
             "codes": sorted({m["question_code"] for m in members}),
             "source_spreadsheet": source_csv,
             "source_rows": source_rows,
             "rule_count": len(members), "bin": bin_,
             "blocked_on_missing_fixture": blocked_on_fixture,
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
              "classifier": "Claude (compile-time analyst), session 2026-07-29 — PENDING SME REVIEW",
              "groups": out_groups}
    with open(OUT_JSON, "w") as f:
        json.dump(result, f, indent=1, sort_keys=True)

    # ------------------------------------------------------------ SME packet
    lines = ["# SME Review Packet — application-verification block triage",
             "",
             "**%d rules / %d unique (question, condition) groups.** Every classification"
             % (len(rules), len(groups)),
             "below is a *proposal* pending your review — mark each ✅ agree / ✏️ correct.",
             "Bins: GREEN = automatable now · YELLOW = automatable after data/guide work ·",
             "RED = stays human · NOT_A_CHECK = pass/N-A answer option, not a defect rule.",
             "",
             "**Source workbook:** `%s` — row numbers below are Excel-style" % source_csv,
             "(header = row 1), so you can open the sheet and jump straight to each rule.",
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
    for b in ("GREEN", "YELLOW", "RED", "NOT_A_CHECK"):
        lines.append("## %s" % b)
        lines.append("")
        for g in out_groups:
            if g["bin"] != b:
                continue
            lines.append("### G%02d — %s [%s]" % (g["group"],
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
            for t in g["guide_candidates"]:
                lines.append("- **Guide candidate:** %s — %s (PDF p.%d)"
                             % (t["code"], t["title"], t["pdf_page"]))
            lines.append("- **SME:** ☐ agree ☐ correct: ______")
            lines.append("")
    with open(OUT_MD, "w") as f:
        f.write("\n".join(lines) + "\n")

    print("Triage: %d rules -> %d groups | by group: %s | by rule: %s"
          % (len(rules), len(groups), dict(group_counter), dict(rule_counter)))
    print("Packet: %s" % os.path.relpath(OUT_MD, HERE))


if __name__ == "__main__":
    main()
