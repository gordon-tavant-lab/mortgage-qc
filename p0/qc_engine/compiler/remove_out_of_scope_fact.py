"""
002g follow-on -- removes an out-of-scope fact from the vocabulary.

`loan_product_type` (question 571085) was promoted in v3/v4/v5 alongside the
other 16 facts, but its own description names it a FREDDIE MAC fact (real
trademarked programs -- CHOICERenovation, GreenCHOICE Mortgage) in a
vocabulary whose only signed KB corpus is Fannie Mae. Gordon's explicit
decision (2026-07-27, after reviewing the citation-mismatch fix in v5):
rather than carry an uncited, un-citable fact indefinitely, drop it -- it can
be re-added later, correctly cited, once/if a Freddie Mac Selling Guide
corpus is ever ingested. Nothing about the other 16 facts changes.

Deterministic, no LLM call. Writes a NEW version (v6, never overwrites v5 --
002c precedent).

Run: python3 p0/qc_engine/compiler/remove_out_of_scope_fact.py
Python 3.9 compatible.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_P0 = os.path.dirname(os.path.dirname(_HERE))
_REPO_ROOT = os.path.dirname(_P0)
if _P0 not in sys.path:
    sys.path.insert(0, _P0)

from qc_engine.compiler import fact_vocabulary as FV  # noqa: E402
from qc_engine.compiler import knowledge_base as KB  # noqa: E402

VOCAB_DIR = os.path.join(_REPO_ROOT, "storage", "fact_vocabulary")
SIGNED_BY = "NOT-A-REAL-SME-pending-kayla-review"
SIGNED_AT = "2026-07-27"

FACT_TO_REMOVE = "fact-loan-product-type"
REASON = ("Removed 2026-07-27 -- this fact's own description names it a "
         "Freddie Mac fact (CHOICERenovation, GreenCHOICE Mortgage), but no "
         "Freddie Mac Selling Guide corpus is ingested (only 'Fannie Mae' "
         "is signed), so it could never be correctly cited. Dropped rather "
         "than carried uncited indefinitely -- re-add once/if a Freddie Mac "
         "corpus exists. Question 571085 (239 AMQ rows) is unbound again "
         "until then.")


def main() -> None:
    vocab = FV.load_latest(VOCAB_DIR)
    removed = [f for f in vocab.facts if f.id == FACT_TO_REMOVE]
    if not removed:
        raise SystemExit(f"{FACT_TO_REMOVE!r} not found in v{vocab.version} -- nothing to remove")
    remaining = [f for f in vocab.facts if f.id != FACT_TO_REMOVE]

    new_version = vocab.version + 1
    out_path = os.path.join(VOCAB_DIR, f"v{new_version}.json")
    if os.path.exists(out_path):
        raise SystemExit(f"{out_path!r} already exists -- refusing to overwrite")

    out_vocab = FV.FactVocabulary(version=new_version, facts=remaining)
    out_vocab = KB.sign(out_vocab, signed_by=SIGNED_BY, signed_at=SIGNED_AT)
    FV.save(out_vocab, out_path)

    print(f"wrote {out_path}: v{new_version}, {len(remaining)} fact(s) "
          f"({len(vocab.facts)} - 1 removed)")
    print(f"removed: {removed[0].canonical_field_name} ({FACT_TO_REMOVE})")
    print(f"reason: {REASON}")


if __name__ == "__main__":
    main()
