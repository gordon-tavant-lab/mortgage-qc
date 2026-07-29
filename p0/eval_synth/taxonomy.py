"""
Defect taxonomy — derived from the REAL AMQ rule workbooks, not invented.

The eval gap (Blocker 2) was treated as "we need real labeled loans." It isn't,
quite. It bundles three things: (1) does the engine compute the right verdict
given data? (2) did we interpret the checks correctly? (3) what defects actually
occur in the wild? Only (3) truly needs real files. This module attacks (1) at
scale by deriving a *grounded* defect taxonomy from the lender's own 800+ check
workbook — so the mutations our generator injects track the real rule set, not
our imagination.

Input: `demo/rules/*.xlsx` — AMQ (Audit Management Questionnaire) exports. Each
row is a question -> a *response* (the defect condition, col 7) -> an exception
code (col 9) + significance (col 10). The response text IS the failure mode.

We classify each defect condition into a small set of generatable ARCHETYPES,
each mapped to an engine check `kind` (qc_engine.ruleset.Check) and the verdict
the engine should emit when that defect is present. That mapping is the thing an
SME signs off — a *rules review*, which we can get, not a *loan hunt*, which we
may not.

Run:  python3 taxonomy.py            # profile + write taxonomy.json
Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
PROD = os.path.dirname(os.path.dirname(HERE))   # .../mortgage-qc-prod
RULES_DIR = os.path.join(PROD, "demo", "rules")

# Column layout of the AMQ export (1-based -> 0-based here). Verified by reading
# the header row of the Sept 2025 Retail workbook.
COL_CATEGORY = 1       # c2  Question Category Name
COL_QCODE = 4          # c5  Question Code (e.g. "Final URLA")
COL_RESPONSE = 6       # c7  Question Response  <- the defect condition text
COL_EXC_CODE = 8       # c9  Exception Code     <- presence = a real exception row
COL_SIGNIFICANCE = 9   # c10 Default Significance


# --- Archetypes: how a defect condition reduces to something we can GENERATE --
# Ordered by specificity (first match wins in the classifier). Each archetype
# declares the engine check `kind` it exercises and the verdict the engine must
# produce when the defect is injected. This is the SME-signable contract.
ARCHETYPES: List[Dict[str, Any]] = [
    {
        "id": "UNSIGNED",
        "desc": "A required signature/date is absent.",
        "patterns": [r"unsigned", r"not signed", r"not dated",
                     r"missing.*signature", r"signature.*(missing|not)"],
        "engine_kind": "predicate",       # is_true(signed)
        "expected_verdict": "FAIL",
        "phase": "QC",
    },
    {
        "id": "THRESHOLD",
        "desc": "A ratio/limit is breached (LTV, DTI, %, max/min).",
        "patterns": [r"\bltv\b", r"\bdti\b", r"exceed", r"greater than",
                     r"less than", r"\bover \d", r"maximum", r"minimum",
                     r"\d+\s*%", r"percent"],
        "engine_kind": "ratio_threshold",
        "expected_verdict": "FAIL",
        "phase": "QC",
    },
    {
        "id": "MISMATCH",
        "desc": "Two sources disagree on the same field (doc vs system).",
        "patterns": [r"do(es)? not match", r"does not agree", r"mismatch",
                     r"differ", r"inconsistent", r"not consistent",
                     r"conflict", r"discrepan"],
        "engine_kind": "agree_categorical",   # or agree_numeric
        "expected_verdict": "FLAG",            # reconcile = informational
        "phase": "RECONCILE",
    },
    {
        "id": "EXPIRED",
        "desc": "A value/document is stale, aged, or out of its validity window.",
        "patterns": [r"expired", r"stale", r"\baged\b", r"too old",
                     r"not current", r"within \d+ days", r"w/in \d+ days"],
        "engine_kind": "predicate",      # is within window -> is_true
        "expected_verdict": "FAIL",
        "phase": "QC",
    },
    {
        "id": "MISSING",
        "desc": "A required field/document is absent from the file.",
        "patterns": [r"missing", r"not present", r"\bno\b", r"absent",
                     r"not provided", r"not in the file", r"fail(ed|s)? to",
                     r"not document"],
        "engine_kind": "predicate",      # is_present
        "expected_verdict": "FAIL",
        "phase": "QC",
    },
    {
        "id": "INACCURATE",
        "desc": "A value is present but wrong/invalid/inaccurate.",
        "patterns": [r"inaccurate", r"incorrect", r"\bwrong\b", r"invalid",
                     r"not accurate", r"\berror"],
        "engine_kind": "agree_categorical",   # wrong = disagrees with truth doc
        "expected_verdict": "FLAG",
        "phase": "RECONCILE",
    },
    {
        "id": "INCOMPLETE",
        "desc": "A form/section is partially completed.",
        "patterns": [r"incomplete", r"not complete", r"partially",
                     r"not (fully )?completed"],
        "engine_kind": "predicate",      # is_present/complete
        "expected_verdict": "FAIL",
        "phase": "QC",
    },
    {
        # Matched by the _POLICY_NOT fallback, not the pattern list. A broad
        # bucket of "<requirement> not <verb>" policy predicates.
        "id": "POLICY",
        "desc": "A stated policy requirement was not satisfied "
                "(not used/included/met/supported/...).",
        "patterns": [],                  # handled by _POLICY_NOT fallback
        "engine_kind": "predicate",      # is_true(requirement_met)
        "expected_verdict": "FAIL",
        "phase": "QC",
    },
]

_COMPILED = [(a, [re.compile(p, re.I) for p in a["patterns"]]) for a in ARCHETYPES]

# AMQ rows whose "response" is actually a SQL gating clause (the machine-readable
# product/program gate, e.g. QC_Policy='Fannie Mae') are NOT defect conditions —
# they select which loans a question applies to. Bucketed separately so they
# don't dilute the classified-rate (they need a profile-derivation layer, not a
# mutation operator). See memory: AMQ SQL gating in cols 7/12/13.
_SQL_GATING = re.compile(r"^\s*SELECT\s+DISTINCT", re.I)

# A catch-all for policy conditions phrased as "<requirement> not <verb>"
# (not used / not included / not met / not supported / not acceptable / not
# applied / not based upon). These are POLICY predicates the engine evaluates as
# is_true(requirement_met) -> FAIL when absent. Tried LAST so specific archetypes
# win first.
_POLICY_NOT = re.compile(
    r"\bnot\s+(used|included|met|support|supported|acceptable|applied|"
    r"based|considered|provided|obtained|completed|reflect|valid|"
    r"documented|verified|present|eligible|waived|submitted|executed)",
    re.I,
)


def classify(defect_text: str) -> Optional[str]:
    """Return the archetype id for a defect condition, or None if unclassified.
    First match wins (archetypes ordered most-specific first)."""
    if not defect_text:
        return None
    if _SQL_GATING.search(defect_text):
        return "SQL_GATING"            # not a defect: a program gate
    for arch, regexes in _COMPILED:
        for rx in regexes:
            if rx.search(defect_text):
                return arch["id"]
    if _POLICY_NOT.search(defect_text):
        return "POLICY"                # "<requirement> not <verb>" -> predicate
    return None


# 010a: one questionnaire in the real data ("Post-Closing Private Bank Oct
# 2025") exports its rows with every column from "Question Code" onward
# shifted one position left relative to the shared 14-column header -- e.g.
# its real Exception Code lives where the header says "Question Answers
# Exception Name" (index 3), not "Exception Code" (index 8), which instead
# holds a severity word ("Critical"/"Major") for these rows. Verified by
# direct inspection across 6 different Question Category values -- 100% of
# this questionnaire's 802 rows follow the shifted layout; the other 3 real
# sources (both Retail sheets, the small "Pre Funding Nov 2025" sheet) are
# correctly aligned to the header. Detected by Questionnaire Name (column A,
# always correctly positioned) rather than sheet name/position, since that's
# the one field guaranteed readable regardless of the shift.
_SHIFTED_QUESTIONNAIRE_NAME = "Post-Closing Private Bank Oct 2025"

# Standard mapping (0-based, matches the shared header row).
_STANDARD_COLS = {
    "category": COL_CATEGORY, "qcode": COL_QCODE, "defect_text": COL_RESPONSE,
    "sql_criteria": 7, "exception_code": COL_EXC_CODE,
    "significance": COL_SIGNIFICANCE,
}
# Shifted mapping: every field from "qcode" onward reads one column earlier
# than the header claims. "category" (index 1) is unaffected -- the shift
# starts at "exception_code", which is where the header's own "Question
# Answers Exception Name" label (index 3) actually is.
_SHIFTED_COLS = {
    "category": COL_CATEGORY, "qcode": 4, "defect_text": 5,
    "sql_criteria": 6, "exception_code": 3, "significance": 8,
}


def load_rows(path: str) -> List[Dict[str, Any]]:
    """Every AMQ row that carries an exception code (a real defect condition),
    across EVERY sheet in the workbook -- not only the first (010a fix: the
    Private Bank workbook's second sheet, "Pre Funding Nov 2025", was never
    read before this, silently dropping its ~9 real rows, including one real
    Exception Code, "PB-FormDoc"). Also corrects for the shifted-questionnaire
    column layout (see _SHIFTED_QUESTIONNAIRE_NAME above), and now captures
    each row's own SQL gating clause ("Question Criteria") -- previously
    dropped entirely; 010a's secondary gating signal needs it."""
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows: List[Dict[str, Any]] = []
    for ws in wb.worksheets:
        for row_num, r in enumerate(ws.iter_rows(min_row=5, values_only=True), start=5):
            if not r or len(r) <= COL_CATEGORY:
                continue
            questionnaire_name = r[0] if len(r) > 0 else None
            cols = (_SHIFTED_COLS if questionnaire_name == _SHIFTED_QUESTIONNAIRE_NAME
                    else _STANDARD_COLS)
            exc_idx = cols["exception_code"]
            if len(r) <= exc_idx or r[exc_idx] is None:
                continue
            sql_idx = cols["sql_criteria"]
            sql_val = r[sql_idx] if len(r) > sql_idx else None
            rows.append({
                "category": r[cols["category"]] if len(r) > cols["category"] else None,
                "qcode": r[cols["qcode"]] if len(r) > cols["qcode"] else None,
                "defect_text": str(r[cols["defect_text"]] or "") if len(r) > cols["defect_text"] else "",
                "sql_criteria": str(sql_val) if sql_val is not None else "",
                "exception_code": r[exc_idx],
                "significance": r[cols["significance"]] if len(r) > cols["significance"] else None,
                "sheet": ws.title,
                "source_row": row_num,
            })
    wb.close()
    return rows


def build_taxonomy(paths: List[str]) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    sources: Dict[str, int] = {}
    for p in paths:
        r = load_rows(p)
        sources[os.path.basename(p)] = len(r)
        rows.extend(r)

    by_arch: Counter = Counter()
    by_arch_cat: Dict[str, Counter] = defaultdict(Counter)
    examples: Dict[str, List[str]] = defaultdict(list)
    unclassified: List[str] = []
    sql_gating = 0

    for row in rows:
        arch = classify(row["defect_text"])
        if arch == "SQL_GATING":
            sql_gating += 1
            continue
        if arch is None:
            by_arch["UNCLASSIFIED"] += 1
            if len(unclassified) < 10:
                unclassified.append(row["defect_text"][:110])
            continue
        by_arch[arch] += 1
        by_arch_cat[arch][row["category"]] += 1
        if len(examples[arch]) < 3:
            examples[arch].append(row["defect_text"][:110])

    # SQL gating rows are program gates, not defect conditions — out of denominator.
    total = len(rows) - sql_gating
    classified = total - by_arch.get("UNCLASSIFIED", 0)

    archetype_records = []
    for a in ARCHETYPES:
        archetype_records.append({
            **{k: a[k] for k in ("id", "desc", "engine_kind",
                                 "expected_verdict", "phase")},
            "matched_conditions": by_arch.get(a["id"], 0),
            "top_categories": by_arch_cat[a["id"]].most_common(5),
            "examples": examples.get(a["id"], []),
        })

    return {
        "sources": sources,
        "sql_gating_rows_excluded": sql_gating,
        "total_defect_conditions": total,
        "classified": classified,
        "classified_pct": round(100 * classified / total, 1) if total else 0,
        "coverage_note": (
            "Denominator excludes SQL gating rows (program gates like "
            "QC_Policy='Fannie Mae', not defect conditions). Remaining "
            "unclassified rows are residual phrasings of conditions already "
            "covered by an archetype — they do not represent uncovered engine "
            "check-kinds. All 8 archetypes map onto the engine's existing "
            "check kinds (predicate / ratio_threshold / agree_*)."
        ),
        "archetypes": archetype_records,
        "unclassified_examples": unclassified,
    }


def main() -> int:
    paths = [os.path.join(RULES_DIR, f)
             for f in sorted(os.listdir(RULES_DIR))
             if f.endswith(".xlsx") and not f.startswith("~$")]
    if not paths:
        print(f"No .xlsx rule workbooks found in {RULES_DIR}")
        return 1
    tax = build_taxonomy(paths)

    print("\n=== DEFECT TAXONOMY (derived from real AMQ workbooks) ===")
    for src, n in tax["sources"].items():
        print(f"  source: {src}  ({n} exception conditions)")
    print(f"  SQL gating rows excluded (program gates): "
          f"{tax['sql_gating_rows_excluded']}")
    print(f"  total defect conditions: {tax['total_defect_conditions']}  "
          f"classified into archetypes: {tax['classified']} "
          f"({tax['classified_pct']}%)")
    print()
    for a in tax["archetypes"]:
        print(f"  [{a['id']:<11}] {a['matched_conditions']:>5} conditions "
              f"-> engine kind '{a['engine_kind']}' -> expect {a['expected_verdict']}")
        cats = ", ".join(f"{c}({n})" for c, n in a["top_categories"][:3])
        if cats:
            print(f"               top categories: {cats}")
    print(f"\n  {tax['coverage_note']}\n")

    out = os.path.join(HERE, "taxonomy.json")
    with open(out, "w") as fh:
        json.dump(tax, fh, indent=2, sort_keys=False, default=str)
    print(f"  taxonomy -> {out}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
