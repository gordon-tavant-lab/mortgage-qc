"""
002g T008 -- builds the seed canonical-fact vocabulary (v1) from REAL data.

The gift binding is derived by actually re-clustering the real Retail
Post-Closing rows (002f Layer 0, deterministic, zero LLM) and reading
question 570606's real answer vocabulary -- never hand-typed answer strings
(criteria.md #7). Only the "Yes - Gift" answer is bound in v1; the other 16
real answers of question 570606 (checking/savings, retirement, grant, ...)
are honest future vocabulary work requiring their own catalog fields and SME
review -- binding them now with guessed field names would be exactly the
invented-content failure this project forbids.

Signed with the same honest placeholder as the ingested Selling Guide corpus
(`NOT-A-REAL-SME-pending-kayla-review`): proves the pipeline end-to-end, is
NOT yet trustworthy for a real compile until Kayla (or another real SME)
reviews and re-signs.

Run: python3 p0/qc_engine/compiler/build_seed_fact_vocabulary.py

Python 3.9 compatible.
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
from qc_engine.compiler import fact_vocabulary as FV  # noqa: E402
from qc_engine.compiler import knowledge_base as KB  # noqa: E402

ROWS_PATH = os.path.join(_P0, "fixtures", "ontology_extraction",
                         "retail_post_closing_rows.json")
OUT_PATH = os.path.join(_REPO_ROOT, "storage", "fact_vocabulary", "v1.json")

GIFT_QUESTION_KEY = "570606"
GIFT_ANSWER = "Yes - Gift"


def main() -> None:
    with open(ROWS_PATH) as f:
        rows = json.load(f)
    cluster = L0.cluster(rows)
    entry = next((e for e in cluster.entries if e.key == GIFT_QUESTION_KEY), None)
    if entry is None:
        raise SystemExit(f"question {GIFT_QUESTION_KEY} not found in the real cluster "
                         "-- refusing to write a vocabulary not derived from data")
    if GIFT_ANSWER not in entry.answer_vocabulary:
        raise SystemExit(f"answer {GIFT_ANSWER!r} not in question {GIFT_QUESTION_KEY}'s "
                         f"REAL answer vocabulary {sorted(entry.answer_vocabulary)!r} "
                         "-- refusing to bind an answer the data doesn't contain")

    gift_rows = sorted(entry.dependent_row_ids)
    fact = FV.CanonicalFact(
        id="fact-gift-funds-used",
        canonical_field_name="gift_funds_used",
        data_type="boolean",
        description=("Whether any borrower funds used on this loan are gift funds. "
                     "Derived from the AMQ workbook's own asset-type question "
                     f"(QuestionID {GIFT_QUESTION_KEY}), whose real decoded answer "
                     f"vocabulary contains {GIFT_ANSWER!r} gating "
                     f"{len(gift_rows)} dependent rows."),
        name_synonyms=["gift_proceeds_present", "gift_funds_present"],
        question_bindings=[FV.QuestionBinding(
            question_key=GIFT_QUESTION_KEY,
            answers=[GIFT_ANSWER],
            canonical_value="true",
        )],
        mismo_ldd_reference=None,  # candidate LDD term to be confirmed at SME review
        source_citations=[f"AMQ Retail Post-Closing row {r}" for r in gift_rows[:5]]
        + [f"... and {len(gift_rows) - 5} more rows sharing question {GIFT_QUESTION_KEY}"],
    )
    vocab = FV.FactVocabulary(version=1, facts=[fact])
    vocab = KB.sign(vocab, signed_by="NOT-A-REAL-SME-pending-kayla-review",
                    signed_at="2026-07-26")
    FV.save(vocab, OUT_PATH)

    print(f"wrote {OUT_PATH}: 1 fact, question {GIFT_QUESTION_KEY} binding "
          f"({GIFT_ANSWER!r} -> gift_funds_used=true), derived from "
          f"{len(gift_rows)} real dependent rows")
    print(f"Layer-0 full-sheet coverage: {cluster.coverage}")
    print("STATUS: signed_by is an explicit placeholder -- NOT yet SME-reviewed. "
          "Proves the pipeline; not yet trustworthy for a real compile.")


if __name__ == "__main__":
    main()
