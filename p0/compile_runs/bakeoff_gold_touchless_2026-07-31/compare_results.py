"""
compare_results.py -- join p0/qc_engine's and src/shacl_pilot's gold-ruleset
bake-off results on (card_id, exception_code) and report coverage, verdict
distribution, and agreement/disagreement on the intersection where both
produced a non-abstaining verdict.

See /Users/gordonchan/.claude/plans/1-no-no-this-iridescent-brooks.md section
4 ("Compare and write up") for the methodology this implements.

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

P0_MAPPING_PATH = os.path.join(HERE, "gold_to_check_mapping.json")
P0_RESULTS_PATH = os.path.join(HERE, "p0_results.json")
SRC_RESULTS_PATH = os.path.join(REPO_ROOT, "src", "shacl_pilot",
                                 "bakeoff_gold_touchless_2026-07-31", "shacl_results.json")
GOLD_RULES_PATH = os.path.join(REPO_ROOT, "storage", "rules", "gold", "data", "rules_compiled.json")

NON_ABSTAINING = {"PASS", "FAIL"}


def load_p0():
    with open(P0_MAPPING_PATH) as f:
        mapping = json.load(f)
    with open(P0_RESULTS_PATH) as f:
        run = json.load(f)

    by_check_id = {r["check_id"]: r for r in run["results"]}
    out = {}
    for check_id, m in mapping.items():
        key = (m["card_id"], m["exception_code"])
        r = by_check_id.get(check_id)
        out[key] = {
            "check_type": m["check_type"],
            "status": r["status"] if r else "NOT_COMPILED",
            "message": r["message"] if r else None,
        }
    return out, run


def load_src():
    with open(SRC_RESULTS_PATH) as f:
        run = json.load(f)
    out = {}
    for r in run["results"]:
        key = (r["card_id"], r["exception_code"])
        out[key] = {"check_type": r["check_type"], "status": r["status"], "message": r["message"]}
    return out, run


def load_gold_universe():
    """Every (card_id, exception_code) the gold ruleset actually defines --
    the full 1,105-1,106-check universe, independent of either conversion."""
    with open(GOLD_RULES_PATH) as f:
        gold = json.load(f)
    universe = {}
    for card in gold["cards"]:
        for opt in card["defect_options"]:
            key = (card["card_id"], opt["finding"]["exception_code"])
            universe[key] = opt["check_type"]
    return universe


def main():
    p0_by_key, p0_run = load_p0()
    src_by_key, src_run = load_src()
    universe = load_gold_universe()

    print("=" * 78)
    print("GOLD RULESET BAKE-OFF -- p0/qc_engine vs src/shacl_pilot")
    print("loan: %s (p0) / %s (src)" % (p0_run["loan_id"], src_run["summary"]["loan_id"]))
    print("gold ruleset universe: %d (card_id, exception_code) checks" % len(universe))
    print("p0 join keys: %d   src join keys: %d" % (len(p0_by_key), len(src_by_key)))
    print("=" * 78)

    # -- keys present in gold universe but missing from one side's output --
    missing_from_p0 = [k for k in universe if k not in p0_by_key]
    missing_from_src = [k for k in universe if k not in src_by_key]
    print("\ngold checks with NO p0 result at all: %d" % len(missing_from_p0))
    print("gold checks with NO src result at all: %d" % len(missing_from_src))

    # -- coverage by check_type: converted vs unsupported, per side --
    p0_cov = defaultdict(lambda: Counter())
    src_cov = defaultdict(lambda: Counter())
    for key, ct in universe.items():
        p0_status = p0_by_key.get(key, {}).get("status", "NOT_COMPILED")
        src_status = src_by_key.get(key, {}).get("status", "NOT_COMPILED")
        p0_cov[ct]["converted" if p0_status != "NOT_COMPILED" else "unsupported"] += 1
        src_cov[ct]["converted" if src_status != "NOT_COMPILED" else "unsupported"] += 1

    print("\ncoverage by check_type (converted / unsupported):")
    print("  %-24s %-18s %-18s" % ("check_type", "p0", "src"))
    for ct in sorted(set(universe.values())):
        p = p0_cov[ct]
        s = src_cov[ct]
        print("  %-24s conv=%-4d unsup=%-4d  conv=%-4d unsup=%-4d" % (
            ct, p["converted"], p["unsupported"], s["converted"], s["unsupported"]))

    # -- verdict distribution, per side, over the full gold universe --
    p0_dist = Counter(p0_by_key.get(k, {}).get("status", "NOT_COMPILED") for k in universe)
    src_dist = Counter(src_by_key.get(k, {}).get("status", "NOT_COMPILED") for k in universe)
    all_statuses = ["PASS", "FAIL", "NOT_APPLICABLE", "NO_DATA", "NEEDS_REVIEW", "NOT_COMPILED"]
    print("\nverdict distribution (over the full %d-check gold universe):" % len(universe))
    print("  %-16s %-10s %-10s" % ("status", "p0", "src"))
    for s in all_statuses:
        print("  %-16s %-10d %-10d" % (s, p0_dist.get(s, 0), src_dist.get(s, 0)))

    # -- agreement analysis: both sides produced a non-abstaining verdict --
    both_committed = []
    for key in universe:
        p0_status = p0_by_key.get(key, {}).get("status", "NOT_COMPILED")
        src_status = src_by_key.get(key, {}).get("status", "NOT_COMPILED")
        if p0_status in NON_ABSTAINING and src_status in NON_ABSTAINING:
            both_committed.append((key, p0_status, src_status))

    print("\n" + "=" * 78)
    print("checks where BOTH engines committed to PASS or FAIL: %d" % len(both_committed))
    print("=" * 78)
    agree, disagree = [], []
    for key, p0s, srcs in both_committed:
        (agree if p0s == srcs else disagree).append((key, p0s, srcs))
    print("agree: %d   disagree: %d" % (len(agree), len(disagree)))
    for key, p0s, srcs in both_committed:
        card_id, exc = key
        print("  %-14s %-30s p0=%-5s src=%-5s  %s" % (
            "AGREE" if p0s == srcs else "DISAGREE", f"{card_id} / {exc}", p0s, srcs,
            p0_by_key[key]["message"][:80] if p0_by_key[key]["message"] else ""))

    # -- the doc_presence/completeness p0-FAIL vs src-NO_DATA divergence --
    dp_dc_p0_fail = sum(
        1 for k, ct in universe.items()
        if ct in ("doc_presence", "doc_completeness") and p0_by_key.get(k, {}).get("status") == "FAIL")
    dp_dc_src_nodata = sum(
        1 for k, ct in universe.items()
        if ct in ("doc_presence", "doc_completeness") and src_by_key.get(k, {}).get("status") == "NO_DATA")
    print("\n" + "=" * 78)
    print("doc_presence/doc_completeness divergence (%d checks total, both sides "
          "have zero real document-inventory data for this loan):" % sum(
              1 for ct in universe.values() if ct in ("doc_presence", "doc_completeness")))
    print("  p0 reports FAIL on:     %d  (is_present's None -> FAIL semantics)" % dp_dc_p0_fail)
    print("  src reports NO_DATA on: %d  (required li:docs_present predicate absent)" % dp_dc_src_nodata)
    print("=" * 78)

    out = {
        "loan_id": p0_run["loan_id"],
        "gold_universe_size": len(universe),
        "missing_from_p0": len(missing_from_p0),
        "missing_from_src": len(missing_from_src),
        "coverage_by_check_type": {
            ct: {"p0": dict(p0_cov[ct]), "src": dict(src_cov[ct])} for ct in set(universe.values())
        },
        "verdict_distribution": {"p0": dict(p0_dist), "src": dict(src_dist)},
        "both_committed_count": len(both_committed),
        "agree_count": len(agree),
        "disagree_count": len(disagree),
        "disagreements": [
            {"card_id": k[0], "exception_code": k[1], "p0_status": p0s, "src_status": srcs,
             "check_type": universe[k], "p0_message": p0_by_key[k]["message"],
             "src_message": src_by_key[k]["message"]}
            for k, p0s, srcs in disagree
        ],
        "agreements": [
            {"card_id": k[0], "exception_code": k[1], "status": p0s, "check_type": universe[k]}
            for k, p0s, srcs in agree
        ],
        "doc_presence_completeness_divergence": {
            "total_checks": sum(1 for ct in universe.values() if ct in ("doc_presence", "doc_completeness")),
            "p0_fail": dp_dc_p0_fail,
            "src_no_data": dp_dc_src_nodata,
        },
    }
    out_path = os.path.join(HERE, "comparison_report.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print("\nwrote: %s" % out_path)


if __name__ == "__main__":
    main()
