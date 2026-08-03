#!/usr/bin/env python3
"""
Gold ruleset -> frontend Check/Block/Route catalog.

Reads storage/rules/gold/data/{rules_compiled.json,rules_atomic.json} directly and emits
frontend/src/data/goldCatalog.json. Independent of both p0/qc_engine (Pipeline B) and
src/shacl_pilot (Pipeline A) -- this is a pure data-shape translation for the rule-author
UI, not a compile-to-executable-logic step. Re-run whenever the gold data changes:

  python3 frontend/scripts/build_gold_catalog.py

Four routes (spec021 US3, 2026-08-02, superseding the 2026-08-01 "two routes only" call
above -- Gordon reversed that decision). spec024 US5 (2026-08-02, g-os-contrarian check)
then corrected FHA/VA/USDA to an honest zero-check placeholder (gold's own compiled data
is Fannie-Mae-specific, and no per-program AMQ compile pass existed at the time). spec024
US10 (2026-08-03, a second g-os-contrarian-style /grill-me check, Gordon's explicit,
informed override) reverses that specific display decision: FHA/VA/USDA now show real
per-program check counts imported directly from the raw AMQ Sept 2025 workbook (see
build_program_blocks_and_checks() below) -- every imported check is real (traceable to an
actual workbook row) but stays compileState=NOT_COMPILED / authorability=NOT_ASSESSED,
since none of them have been through this project's field-mapping/compile step the way
Conventional's checks have (Constitution Principle VII: the "real but not yet compiled"
distinction survives in the data even though the UI no longer visually flags it).
"""
import json
import re
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[2]  # demo-sites/mortgage-qc-prod/
GOLD_DIR = ROOT / "storage" / "rules" / "gold" / "data"
AMQ_XLSX_PATH = ROOT / "storage" / "rules" / "gold" / "source" / "amqs-sept-2025-retail.xlsx"
OUT_PATH = Path(__file__).resolve().parents[1] / "src" / "data" / "goldCatalog.json"

# spec024 US10: a raw AMQ row is scoped to a program via a `Loans.QC_Policy = 'X'` filter
# embedded in its "Question Criteria" column (a SQL-shaped precondition string, not an
# executable query -- this project never runs it, only parses the literal program tag out
# of it). A row can be tagged to more than one program (rare, ~45 rows via OR).
QC_POLICY_RE = re.compile(r"QC_Policy\s*=\s*'([^']*)'")

PROGRAM_QC_POLICY = {
    "fha": ["FHA"],
    "va": ["VA"],
    "usda": ["USDA"],
}

SEVERITY_MAP = {
    "Critical": "CRITICAL",
    "Critical-Pending SI": "CRITICAL",
    "Major": "WARNING",
    "Minor": "INFO",
    "Note": "INFO",
}

# check_type -> (kind, authorability, authorabilityReason template)
# "predicate" with operator="<=" / threshold="" is the established placeholder convention
# for kinds where operator/threshold don't conceptually apply (see mockData.ts precedent).
KIND_MAP = {
    "doc_presence": ("predicate", "is_present", "NEEDS_FIELDS",
                      "No evidence field resolved yet -- card-level defect option not yet "
                      "decomposed to atomic evidence."),
    "doc_completeness": ("predicate", "is_present", "NEEDS_FIELDS",
                          "No evidence field resolved yet -- card-level defect option not yet "
                          "decomposed to atomic evidence."),
    "threshold_eligibility": ("ratio_threshold", None, "NEEDS_FIELDS",
                              "Threshold value not yet parsed from logic.procedure into an executable operator/threshold."),
    "computation": ("ratio_threshold", None, "NEEDS_FIELDS",
                    "Computation formula not yet implemented as executable logic."),
    "cross_doc_consistency": ("agree_doc_categorical", None, "NEEDS_FIELDS",
                              "Comparison fields not yet resolved from evidence."),
    "date_window": ("predicate", "is_true", "NOT_MECHANIZABLE",
                    "Date-window logic (relative to an event date) has no engine kind yet."),
    "list_screening": ("predicate", "is_true", "NOT_MECHANIZABLE",
                       "Requires a versioned external reference-dataset lookup, not yet wired."),
    "reverification": ("predicate", "is_true", "NOT_MECHANIZABLE",
                       "Requires a re-verification data source not yet modeled."),
    "scripted_review": ("predicate", "is_true", "NEEDS_SME",
                        "Scripted review criteria require human judgment, by design."),
    "routing_context": ("predicate", "is_true", "NOT_MECHANIZABLE",
                        "Sets skip-logic context for other rules; not itself a decidable check."),
}


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def map_citation(c):
    return {
        "source": "Fannie Mae Selling Guide",
        "sectionId": c.get("section_id", ""),
        "title": c.get("title", ""),
        "revisionDate": c.get("effective_date", ""),
    }


def map_applies_if(applicability):
    conds = []
    for group in (applicability.get("all_of") or []) + (applicability.get("any_of") or []):
        conds.append({
            "fieldId": group.get("field", ""),
            "operator": group.get("op", "eq"),
            "value": str(group.get("value", "")),
        })
    return conds


def build_check(check_id, rule_id, card_id, category, check_type, finding, evidence, logic,
                 citations, applicability, question_text):
    kind, predicate, authorability, reason = KIND_MAP.get(
        check_type, ("predicate", "is_true", "NOT_MECHANIZABLE", f"Unrecognized check_type '{check_type}'.")
    )
    severity_raw = finding.get("severity", "Minor")
    field_id = "unmapped"
    if evidence:
        ev0 = evidence[0]
        field_id = ev0.get("field") or ev0.get("name") or "unmapped"
        if field_id != "unmapped" and authorability == "NEEDS_FIELDS":
            # a real evidence field exists (from an atomic rule) -- upgrade from the
            # generic "no fields resolved" reason to a real, buildable verdict.
            authorability, reason = "COMPILABLE", None

    check = {
        "id": check_id,
        "name": finding.get("exception_code", check_id),
        "kind": kind,
        "category": category,
        "fieldId": field_id,
        "operator": "<=",
        "threshold": "",
        "severity": severity_raw,  # raw AMQ casing; mapped to frontend enum by caller
        "description": finding.get("description", question_text),
        "messageFail": finding.get("description", ""),
        "appliesIf": map_applies_if(applicability) or None,
        "sourceCondition": question_text,
        "plainEnglish": logic.get("procedure") if logic else None,
        "questionCode": None,
        "questionText": question_text,
        "grounding": [map_citation(c) for c in citations] if citations else None,
        "sourceLocator": {"ruleId": rule_id, "cardId": card_id},
        # kept from spec019's original authorability concept (re-platformed onto gold,
        # not dropped) -- new optional fields, added alongside this mapper in Phase 2:
        "authorability": authorability,
        "authorabilityReason": reason,
        "compileState": "COMPILED" if authorability == "COMPILABLE" else "NOT_COMPILED",
        # Phase 4 (Built Checks tab, 2026-08-01): real gold field, dedupe since some
        # cards repeat the same AOR per defect option (e.g. ["Underwriter", "Underwriter"]).
        "aor": sorted(set(finding.get("aor") or [])) or None,
    }
    if predicate:
        check["predicate"] = predicate
    check["severity"] = SEVERITY_MAP.get(severity_raw, "INFO")
    return {k: v for k, v in check.items() if v is not None}


def load_amq_rows():
    """spec024 US10: raw AMQ Sept 2025 workbook rows, restricted to Post-Closing (matching
    Conventional's own scope -- both route descriptions already say "post-closing") and
    excluding the "Discarded" category (839 rows system-wide; not one of the 16 real blocks
    and never in scope for Conventional's own compile either).
    """
    wb = openpyxl.load_workbook(AMQ_XLSX_PATH, read_only=True, data_only=True)
    ws = wb["Report 1"]
    rows = list(ws.iter_rows(min_row=4, values_only=True))  # row 4 = header
    return [
        r for r in rows[1:]
        if r[1] is not None and r[1] != "Discarded"
        and r[0] == "Post-Closing AMQ Sept 2025 audits"
    ]


def programs_for_row(criteria):
    if not isinstance(criteria, str):
        return set()
    return set(QC_POLICY_RE.findall(criteria))


def build_program_blocks_and_checks(program_id, program_label, conv_blocks, amq_rows):
    """spec024 US10 (2026-08-03, Gordon's explicit, informed override of US5/FR-015 --
    confirmed via a /grill-me clarification pass): imports real per-program checks from the
    raw AMQ Sept 2025 workbook instead of showing an honest zero. Deduped by (category,
    Exception Code) -- the raw report repeats a row once per Question Response variant, so a
    naive per-row count overstates how many distinct exceptions actually exist; Exception
    Code is the stable identity a real check should key on (mirrors how Conventional's own
    checks are named after their gold exception code). Rows with no Exception Code are
    skipped -- they're Question rows with no defined exception outcome in this context, not
    a real, assertable check.

    Every imported check keeps compileState=NOT_COMPILED and authorability=NOT_ASSESSED --
    none of these rows have real field/operator data or have been through this project's
    compile step (FR-031). Categories with zero real rows for this program (e.g. ATR-QM, EPD,
    Data Validation Svc-DVS, and Fannie Mae Form 1033 are Fannie/Freddie-specific investor
    categories with no FHA/VA/USDA equivalent in the source) get no block at all for this
    program (2026-08-03, Gordon: remove rather than leave as an empty Available block) --
    not force-populated to make every category look non-zero, and not shown as a hollow
    placeholder either.
    """
    qc_policy_values = set(PROGRAM_QC_POLICY[program_id])
    seen = {}  # (category, exception_code) -> check dict; first row wins
    for row in amq_rows:
        (_, category, _, _, question_code, question_text, _, criteria,
         exception_code, severity_raw, description, aor1, aor2, _) = row
        if not exception_code:
            continue
        if not (programs_for_row(criteria) & qc_policy_values):
            continue
        key = (category, exception_code)
        if key in seen:
            continue
        seen[key] = {
            "id": f"{program_id}-amq-{slugify(exception_code)}",
            "name": exception_code,
            "kind": "predicate",
            "category": category,
            "fieldId": "",
            "predicate": "is_true",
            "operator": "<=",
            "threshold": "",
            "severity": SEVERITY_MAP.get(severity_raw, "INFO"),
            "description": description or question_text or exception_code,
            "sourceCondition": criteria,
            "questionCode": question_code,
            "questionText": question_text,
            "authorability": "NOT_ASSESSED",
            "authorabilityReason": (
                f"Raw AMQ Sept 2025 workbook row (Post-Closing, {program_label}) -- not yet "
                "field-mapped or compiled; no gold-ruleset compile pass has run over this "
                "program yet."
            ),
            "compileState": "NOT_COMPILED",
            "aor": sorted({a for a in (aor1, aor2) if a}) or None,
        }
    checks = [{k: v for k, v in c.items() if v is not None} for c in seen.values()]

    checks_by_category = {}
    for c in checks:
        checks_by_category.setdefault(c["category"], []).append(c["id"])

    blocks = []
    for conv_block in conv_blocks:
        cid = conv_block["id"][len("conv-"):]  # strip the "conv-" prefix to get the bare category slug
        category = conv_block["name"]
        check_ids = checks_by_category.get(category, [])
        if not check_ids:
            # No real rows for this category in this program -- omit the block
            # entirely rather than showing an empty placeholder.
            continue
        blocks.append({
            "id": f"{program_id}-{cid}",
            "name": category,
            "description": (
                f'AMQ category "{category}" ({program_label}, Post-Closing) -- real rows '
                "imported from the AMQ Sept 2025 workbook; not yet compiled into runnable "
                "logic."
            ),
            "checkIds": check_ids,
        })
    return blocks, checks


def main():
    compiled = json.loads((GOLD_DIR / "rules_compiled.json").read_text())
    atomic_doc = json.loads((GOLD_DIR / "rules_atomic.json").read_text())

    # defect_options.atomic_rule_ids is never populated in rules_compiled.json (decomposition
    # isn't merged back there) -- the reliable link is each atomic rule's own
    # provenance.parent_card_id, verified 1:1 against every compiled card_id.
    atomic_by_parent = {}
    for ar in atomic_doc["atomic_rules"]:
        atomic_by_parent.setdefault(ar["provenance"]["parent_card_id"], []).append(ar)

    checks = []
    categories = {}  # category -> list of check ids

    for card in compiled["cards"]:
        card_id = card["card_id"]
        category = card["category"]
        categories.setdefault(category, [])
        atomics = atomic_by_parent.get(card_id, [])
        if atomics:
            # this card has been decomposed -- the atomic rules are its real check-list,
            # more granular and field-resolved than the raw defect_options.
            for ar in atomics:
                rid = ar["rule_id"]
                check_id = slugify(rid)
                c = build_check(
                    check_id, rid, card_id, category, ar["check_type"], ar["finding"],
                    ar.get("evidence", []), ar.get("logic", {}), ar.get("citations", []),
                    ar.get("applicability", {}), ar["statement"],
                )
                checks.append(c)
                categories[category].append(check_id)
        else:
            for idx, opt in enumerate(card.get("defect_options", [])):
                rid = f"{card_id}#{idx}"
                check_id = slugify(rid)
                c = build_check(
                    check_id, rid, card_id, category, opt["check_type"], opt["finding"],
                    [], {}, card.get("citations", []), card.get("applicability", {}),
                    card["question_text"],
                )
                checks.append(c)
                categories[category].append(check_id)

    conv_blocks = []
    for category, check_ids in sorted(categories.items()):
        cid = slugify(category)
        conv_blocks.append({
            "id": f"conv-{cid}",
            "name": category,
            "description": f'AMQ category "{category}" (Conventional)',
            "checkIds": check_ids,
        })

    amq_rows = load_amq_rows()
    fha_blocks, fha_checks = build_program_blocks_and_checks("fha", "FHA", conv_blocks, amq_rows)
    va_blocks, va_checks = build_program_blocks_and_checks("va", "VA", conv_blocks, amq_rows)
    usda_blocks, usda_checks = build_program_blocks_and_checks("usda", "USDA", conv_blocks, amq_rows)
    program_checks = fha_checks + va_checks + usda_checks
    checks = checks + program_checks

    def total_checks(blocks):
        return sum(len(b["checkIds"]) for b in blocks)

    routes = [
        {
            "id": "conventional",
            "name": "Conventional",
            "description": "Fannie Mae + Freddie Mac, post-closing.",
            "blockIds": [b["id"] for b in conv_blocks],
        },
        {
            "id": "fha",
            "name": "FHA",
            "description": "FHA-insured, post-closing.",
            "blockIds": [b["id"] for b in fha_blocks],
        },
        {
            "id": "va",
            "name": "VA",
            "description": "VA-guaranteed, post-closing.",
            "blockIds": [b["id"] for b in va_blocks],
        },
        {
            "id": "usda",
            "name": "USDA",
            "description": "USDA Rural Development, post-closing.",
            "blockIds": [b["id"] for b in usda_blocks],
        },
    ]

    out = {
        "generated_from": "storage/rules/gold/data/{rules_compiled.json,rules_atomic.json} "
                           "(Conventional) + storage/rules/gold/source/amqs-sept-2025-retail.xlsx "
                           "(FHA/VA/USDA, spec024 US10)",
        "gold_schema_version": compiled.get("schema_version"),
        "checks": checks,
        "blocks": conv_blocks + fha_blocks + va_blocks + usda_blocks,
        "routes": routes,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2))
    print(f"Wrote {len(checks)} checks total ({len(checks) - len(program_checks)} conventional "
          f"compiled + {len(program_checks)} AMQ-imported not-yet-compiled), "
          f"{len(conv_blocks)} conventional blocks, {len(fha_blocks)} FHA blocks "
          f"({total_checks(fha_blocks)} checks), {len(va_blocks)} VA blocks "
          f"({total_checks(va_blocks)} checks), {len(usda_blocks)} USDA blocks "
          f"({total_checks(usda_blocks)} checks) to {OUT_PATH}")


if __name__ == "__main__":
    main()
