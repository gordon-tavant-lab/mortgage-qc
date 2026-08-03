#!/usr/bin/env python3
"""
Gold ruleset -> frontend Check/Block/Route catalog.

Reads storage/rules/gold/data/{rules_compiled.json,rules_atomic.json} directly and emits
frontend/src/data/goldCatalog.json. Independent of both p0/qc_engine (Pipeline B) and
src/shacl_pilot (Pipeline A) -- this is a pure data-shape translation for the rule-author
UI, not a compile-to-executable-logic step. Re-run whenever the gold data changes:

  python3 frontend/scripts/build_gold_catalog.py

Four routes (spec021 US3, 2026-08-02, superseding the 2026-08-01 "two routes only" call
above -- Gordon reversed that decision), corrected again by spec024 US5 (2026-08-02,
g-os-contrarian check): "conventional" (real, gold-sourced checks -- gold's data is
Fannie-Mae-specific, but that provenance is invisible in the UI, never surfaced as a
Fannie/Freddie distinction), plus "fha" / "va" / "usda" (same 16-block structure as
Conventional, each with an HONEST ZERO check count -- gold has no real FHA/VA/USDA
coverage today; see build_empty_program_blocks() below). This replaces spec021 FR-009's
simulated non-zero placeholder, which was an explicit, informed override of this
project's anti-fabrication convention -- spec024 corrects it back to honest.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # demo-sites/mortgage-qc-prod/
GOLD_DIR = ROOT / "storage" / "rules" / "gold" / "data"
OUT_PATH = Path(__file__).resolve().parents[1] / "src" / "data" / "goldCatalog.json"

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


def build_empty_program_blocks(program_id, program_label, conv_blocks):
    """spec024 US5 (2026-08-02, g-os-contrarian check): FHA/VA/USDA have zero real
    gold-ruleset coverage today -- the gold ruleset is compiled from the Fannie Mae
    Selling Guide and covers Conventional only. These routes keep the same 16-block
    structure as Conventional (so the category layout matches across programs) but
    each block gets an honest, empty checkIds list -- no fabricated check count,
    replacing spec021 FR-009's simulated non-zero placeholder.
    """
    blocks = []
    for conv_block in conv_blocks:
        cid = conv_block["id"][len("conv-"):]  # strip the "conv-" prefix to get the bare category slug
        category = conv_block["name"]
        blocks.append({
            "id": f"{program_id}-{cid}",
            "name": category,
            "description": (
                f'AMQ category "{category}" ({program_label}) -- no checks compiled '
                "yet; the gold ruleset covers Conventional only. This block exists so "
                "the category structure matches Conventional's."
            ),
            "checkIds": [],
        })
    return blocks


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

    fha_blocks = build_empty_program_blocks("fha", "FHA", conv_blocks)
    va_blocks = build_empty_program_blocks("va", "VA", conv_blocks)
    usda_blocks = build_empty_program_blocks("usda", "USDA", conv_blocks)

    routes = [
        {
            "id": "conventional",
            "name": "Conventional",
            "description": "Fannie Mae + Freddie Mac, post-closing. Sourced from the gold ruleset.",
            "blockIds": [b["id"] for b in conv_blocks],
        },
        {
            "id": "fha",
            "name": "FHA",
            "description": "FHA-insured, post-closing. Same block structure as Conventional; "
                            "no checks compiled yet -- the gold ruleset covers Conventional only.",
            "blockIds": [b["id"] for b in fha_blocks],
        },
        {
            "id": "va",
            "name": "VA",
            "description": "VA-guaranteed, post-closing. Same block structure as Conventional; "
                            "no checks compiled yet -- the gold ruleset covers Conventional only.",
            "blockIds": [b["id"] for b in va_blocks],
        },
        {
            "id": "usda",
            "name": "USDA",
            "description": "USDA Rural Development, post-closing. Same block structure as "
                            "Conventional; no checks compiled yet -- the gold ruleset covers "
                            "Conventional only.",
            "blockIds": [b["id"] for b in usda_blocks],
        },
    ]

    out = {
        "generated_from": "storage/rules/gold/data/{rules_compiled.json,rules_atomic.json}",
        "gold_schema_version": compiled.get("schema_version"),
        "checks": checks,
        "blocks": conv_blocks + fha_blocks + va_blocks + usda_blocks,
        "routes": routes,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2))
    print(f"Wrote {len(checks)} checks, {len(conv_blocks)} conventional blocks, "
          f"{len(fha_blocks)} FHA blocks, {len(va_blocks)} VA blocks, "
          f"{len(usda_blocks)} USDA blocks (FHA/VA/USDA carry 0 checks, honest -- "
          f"gold covers Conventional only) to {OUT_PATH}")


if __name__ == "__main__":
    main()
