#!/usr/bin/env python3
"""
Gold ruleset -> frontend Check/Block/Route catalog.

Reads storage/rules/gold/data/{rules_compiled.json,rules_atomic.json} directly and emits
frontend/src/data/goldCatalog.json. Independent of both p0/qc_engine (Pipeline B) and
src/shacl_pilot (Pipeline A) -- this is a pure data-shape translation for the rule-author
UI, not a compile-to-executable-logic step. Re-run whenever the gold data changes:

  python3 frontend/scripts/build_gold_catalog.py

Four routes (spec021 US3, 2026-08-02, superseding the 2026-08-01 "two routes only" call
above -- Gordon reversed that decision): "conventional" (real, gold-sourced checks --
gold's data is Fannie-Mae-specific, but that provenance is invisible in the UI, never
surfaced as a Fannie/Freddie distinction), plus "fha" / "va" / "usda" (same 16-block
structure as Conventional, each with a SIMULATED non-zero check count -- gold still has
zero real FHA/VA/USDA coverage; see build_simulated_program_blocks() below for the
honesty discipline this simulation follows).
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


_SIM_SEVERITY_CYCLE = ["CRITICAL", "WARNING", "INFO"]


def build_simulated_program_blocks(program_id, program_label, conv_blocks):
    """spec021 US3 / FR-009 (2026-08-02): FHA/VA/USDA have zero real gold-ruleset
    coverage today, but Gordon explicitly wants each route to show a non-zero check
    count, presented with the SAME visual treatment as a real count -- no distinguishing
    badge in the UI (an explicit, informed override of this project's usual
    anti-false-clean convention, reasoned through and locked into
    specs/021-touchless-audit-run/spec.md's Assumptions before this code was written).

    Concretely: each simulated Check is a real, well-formed entry in checks[] (so
    BlockDetail.tsx and every other checks[]-by-id screen renders it exactly like a
    real check) -- but it is NEVER derived from gold data, and deliberately does NOT
    set `placeholder: true` (that field renders a distinguishing PlaceholderBadge
    elsewhere in the UI, which would violate the "no distinguishing badge" requirement
    above). The only place this simulation is disclosed is this comment and the id
    namespace below (`sim-<program>-...`) -- SIMULATED, not gold-sourced.

    Count formula: max(3, round(real_conv_count * 0.20)) per category -- 20% of
    Conventional's real per-block count, floored at 3 so no block ever shows a
    near-zero count. This mirrors "more real coverage in this category -> more
    simulated coverage in the same category" (a plausible relative shape) without
    claiming any specific fraction is load-bearing; the exact ratio is a cosmetic
    choice, not a modeled fact about FHA/VA/USDA rule density.
    """
    blocks = []
    simulated_checks = []
    for conv_block in conv_blocks:
        cid = conv_block["id"][len("conv-"):]  # strip the "conv-" prefix to get the bare category slug
        category = conv_block["name"]
        real_count = len(conv_block["checkIds"])
        sim_count = max(3, round(real_count * 0.20))

        block_check_ids = []
        for n in range(sim_count):
            check_id = f"sim-{program_id}-{cid}-{n}"
            severity = _SIM_SEVERITY_CYCLE[n % len(_SIM_SEVERITY_CYCLE)]
            check = {
                "id": check_id,
                "name": f"{program_label} {category} Check {n + 1}",
                "kind": "predicate",
                "category": category,
                "fieldId": f"sim_{program_id}_{cid}_{n}",
                "operator": "<=",
                "threshold": "",
                "severity": severity,
                "description": f"Simulated {program_label} post-closing QC check for {category}.",
                "messageFail": f"Simulated {program_label} {category} check failed.",
                "predicate": "is_present",
                "authorability": "COMPILABLE",
                "compileState": "COMPILED",
            }
            simulated_checks.append(check)
            block_check_ids.append(check_id)

        blocks.append({
            "id": f"{program_id}-{cid}",
            "name": category,
            "description": (
                f'AMQ category "{category}" ({program_label}) -- SIMULATED count '
                "(2026-08-02, spec021 FR-009): no real gold-ruleset coverage exists "
                "for this program yet; see build_simulated_program_blocks() docstring."
            ),
            "checkIds": block_check_ids,
        })
    return blocks, simulated_checks


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

    fha_blocks, fha_sim_checks = build_simulated_program_blocks("fha", "FHA", conv_blocks)
    va_blocks, va_sim_checks = build_simulated_program_blocks("va", "VA", conv_blocks)
    usda_blocks, usda_sim_checks = build_simulated_program_blocks("usda", "USDA", conv_blocks)
    checks = checks + fha_sim_checks + va_sim_checks + usda_sim_checks

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
                            "check counts are simulated (spec021 FR-009) -- see "
                            "build_simulated_program_blocks() in this script.",
            "blockIds": [b["id"] for b in fha_blocks],
        },
        {
            "id": "va",
            "name": "VA",
            "description": "VA-guaranteed, post-closing. Same block structure as Conventional; "
                            "check counts are simulated (spec021 FR-009) -- see "
                            "build_simulated_program_blocks() in this script.",
            "blockIds": [b["id"] for b in va_blocks],
        },
        {
            "id": "usda",
            "name": "USDA",
            "description": "USDA Rural Development, post-closing. Same block structure as "
                            "Conventional; check counts are simulated (spec021 FR-009) -- see "
                            "build_simulated_program_blocks() in this script.",
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
          f"{len(usda_blocks)} USDA blocks (all simulated non-zero) to {OUT_PATH}")


if __name__ == "__main__":
    main()
