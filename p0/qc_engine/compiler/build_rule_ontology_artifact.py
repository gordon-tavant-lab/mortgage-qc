"""
Persists the decoded Layer-0 cluster (`p0/ontology_extraction/layer0_clustering.py`)
as a first-class, inspectable artifact instead of recomputing it as a pure
function on every run.

The Layer-0 ontology is a deterministic reorganization of the client AMQ
workbook's own rows -- it originates no new content, so it needs no SME
signature (contrast with `build_seed_fact_vocabulary.py`, which BINDS a
decoded answer to a new canonical fact and therefore does require sign-off).

Run: python3 p0/qc_engine/compiler/build_rule_ontology_artifact.py

Python 3.9 compatible. Zero LLM calls, zero network calls.
"""
from __future__ import annotations

import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_P0 = os.path.dirname(os.path.dirname(_HERE))
_REPO_ROOT = os.path.dirname(_P0)
if _P0 not in sys.path:
    sys.path.insert(0, _P0)

from ontology_extraction import layer0_clustering as L0  # noqa: E402

ROWS_PATH = os.path.join(_P0, "fixtures", "ontology_extraction",
                          "retail_post_closing_rows.json")
ROWS_PATH_REL = os.path.relpath(ROWS_PATH, _REPO_ROOT)
OUT_PATH = os.path.join(_REPO_ROOT, "storage", "rule_ontology", "v1.json")

NOTE = ("this artifact is a deterministic reorganization of the client "
        "workbook's own rows -- it originates nothing and therefore needs "
        "no SME signature")


def build_artifact() -> dict:
    with open(ROWS_PATH) as f:
        rows = json.load(f)
    if not rows:
        raise SystemExit(f"{ROWS_PATH} is empty -- refusing to write an "
                          "ontology artifact not derived from real data")

    cluster = L0.cluster(rows)

    entries = [
        {
            "question_key": e.key,
            "answer_vocabulary": sorted(e.answer_vocabulary),
            "dependent_row_count": len(e.dependent_row_ids),
            "dependent_row_ids": sorted(e.dependent_row_ids),
        }
        for e in sorted(cluster.entries, key=lambda e: e.key)
    ]

    unparsed_row_ids = sorted(u.row_id for u in cluster.unparsed)

    artifact = {
        "version": 1,
        "source": ROWS_PATH_REL,
        "total_rows": cluster.coverage.total_rows,
        "coverage": {
            "resolved_rows": cluster.coverage.resolved_rows,
            "total_rows": cluster.coverage.total_rows,
            "coverage_pct": cluster.coverage.coverage_pct,
        },
        "entries": entries,
        "unparsed_count": len(unparsed_row_ids),
        "unparsed_row_ids": unparsed_row_ids,
        "note": NOTE,
    }
    return artifact


def main() -> None:
    artifact = build_artifact()

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(artifact, f, indent=2, sort_keys=True)
        f.write("\n")

    print(f"wrote {OUT_PATH}")
    print(f"  entries: {len(artifact['entries'])}")
    print(f"  coverage: {artifact['coverage']['resolved_rows']}/"
          f"{artifact['coverage']['total_rows']} rows "
          f"({artifact['coverage']['coverage_pct']:.4f})")
    print(f"  unparsed: {artifact['unparsed_count']}")


if __name__ == "__main__":
    main()
