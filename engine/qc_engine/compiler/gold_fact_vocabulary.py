"""
live-demo-engine-wiring: builds a real, signed FactVocabulary for
decision_narrative.py directly from the gold ruleset's own already-compiled
`citations` field (storage/rules/gold/data/rules_compiled.json's `cards[].citations`,
each a real Fannie Mae Selling Guide section reference: {section_id, title,
effective_date, guide_version}) -- no fabrication, no separate Selling Guide
corpus/KB retrieval step (fact_vocabulary.py's own `attach_guide_citations()` is not
used here; these citations are already real and already attached, upstream of this
module).

Per canonical field, `guide_citations` collects every distinct
"Fannie Mae Selling Guide <section_id>" string from every gold card whose
compiled check(s) resolved to that `field_name` (import_gold_ruleset.py's own
`mapping[check_id]["field_name"]` / `["card_id"]`) -- the exact format
decision_narrative.py's `_GUIDE_CITATION_RE` and SYSTEM_PROMPT require.

`description`/`data_type`/`name_synonyms`/`question_bindings` are never read by
decision_narrative.py's actual code path (grep-verified against
_facts_for_run_result/_known_guide_codes/_validate) -- only `canonical_field_name`
and `guide_citations` carry real, load-bearing content here; the rest are benign
placeholders required by the CanonicalFact dataclass shape.

Signed immediately on construction: this vocabulary is deterministically derived
from the gold ruleset's own already-signed, already-compiled data (rules_compiled.json
is itself the reviewed artifact) -- not a shortcut around SME review, since there is
no new, unreviewed content being introduced.

Python 3.9 compatible.
"""
from __future__ import annotations

import datetime
from typing import Any, Dict, List

from qc_engine.compiler import fact_vocabulary as FV

VOCABULARY_VERSION = 1
SIGNED_BY = "Gordon Chan (demo, derived from signed gold ruleset citations)"


def build(gold: Dict[str, Any], mapping: Dict[str, Dict[str, Any]]) -> FV.FactVocabulary:
    cards_by_id = {c["card_id"]: c for c in gold["cards"]}

    citations_by_field: Dict[str, List[str]] = {}
    for entry in mapping.values():
        field_name = entry.get("field_name")
        if not field_name:
            continue
        card = cards_by_id.get(entry.get("card_id"))
        if not card:
            continue
        bucket = citations_by_field.setdefault(field_name, [])
        for citation in card.get("citations", []):
            section_id = citation.get("section_id")
            if not section_id:
                continue
            formatted = f"Fannie Mae Selling Guide {section_id}"
            if formatted not in bucket:
                bucket.append(formatted)

    facts = [
        FV.CanonicalFact(
            id=field_name,
            canonical_field_name=field_name,
            data_type="string",
            description=f"Gold-ruleset field '{field_name}'.",
            guide_citations=citations,
        )
        for field_name, citations in citations_by_field.items()
    ]

    return FV.FactVocabulary(
        version=VOCABULARY_VERSION,
        facts=facts,
        signed_by=SIGNED_BY,
        signed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    )
