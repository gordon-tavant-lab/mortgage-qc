"""
FR-003 (002b, no dedicated User Story): detect likely duplicate vocabulary
within a compiled batch -- two or more drafted checks that appear to
reference the same underlying real-world concept under different
`field_name`s. Advisory only (does not block sign-off, unlike an unresolved
reference -- User Story 3).

Reuses `p0/qc_engine/ruleset.py`'s existing `_edit_distance` (Levenshtein)
helper for fuzzy field-name clustering -- no new dependency (research.md
Decision 3), a second independent use of a mechanism the codebase already
trusts (RuleProvenance's edit-distance metric).

Python 3.9 compatible.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Dict, List

_HERE = os.path.dirname(os.path.abspath(__file__))
if os.path.dirname(os.path.dirname(_HERE)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.dirname(_HERE)))

from qc_engine.ruleset import _edit_distance  # noqa: E402
from qc_engine.compiler.compile_llm import CompiledCheckDraft  # noqa: E402

# Two field names within this edit-distance (and neither an exact-duplicate,
# which is already a hard collision, not a "possible duplicate") are flagged
# as a likely duplicate-vocabulary risk. Chosen to catch near-misses like
# "borrower_dob" vs "borrowers_dob" without flagging genuinely distinct short
# field names (most catalog field names are >= 8 chars; a distance of 3 is a
# small fraction of that).
DUPLICATE_EDIT_DISTANCE_THRESHOLD = 3


@dataclass
class DuplicateVocabularyFlag:
    field_name_a: str
    field_name_b: str
    edit_distance: int
    check_ids: List[str] = field(default_factory=list)


@dataclass
class ConsistencyReport:
    batch_id: str
    duplicate_flags: List[DuplicateVocabularyFlag] = field(default_factory=list)


def build_consistency_report(batch_id: str, drafts: List[CompiledCheckDraft]) -> ConsistencyReport:
    """The reduce step (research.md Decision 1): cluster this batch's
    candidate field names by edit-distance, flagging near-duplicates."""
    by_field: Dict[str, List[str]] = {}
    for d in drafts:
        if d.check is None:
            continue
        by_field.setdefault(d.check.field_name, []).append(d.check.id)

    names = list(by_field.keys())
    flags: List[DuplicateVocabularyFlag] = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            dist = _edit_distance(a, b)
            if 0 < dist <= DUPLICATE_EDIT_DISTANCE_THRESHOLD:
                flags.append(DuplicateVocabularyFlag(
                    field_name_a=a, field_name_b=b, edit_distance=dist,
                    check_ids=by_field[a] + by_field[b],
                ))
    return ConsistencyReport(batch_id=batch_id, duplicate_flags=flags)
