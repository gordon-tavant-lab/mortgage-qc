"""
User Story 4 (002b, FR-007/FR-008): flag, for human attention, the two
concrete failure patterns `002a`'s self-review found by hand at n=24 --
`predicate-08` (an opaque pre-computed boolean standing in for a real
computational comparison) and `reconcile-00`/`reconcile-01` (a policy/
compliance condition misclassified as a genuine doc-vs-system comparison).

Deterministic regex/keyword heuristics over `source_text` -- NOT a second LLM
call (keeps compile-time cost and Principle I/II's determinism story
unchanged), the same style already proven in `p0/eval_synth/taxonomy.py`'s
`ARCHETYPES` pattern-matching. Advisory only: routes to human attention,
never blocks sign-off on its own (spec.md Edge Cases; only an unresolved
field reference, User Story 3, is a hard block).

Python 3.9 compatible.
"""
from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from typing import List

_HERE = os.path.dirname(os.path.abspath(__file__))
if os.path.dirname(os.path.dirname(_HERE)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.dirname(_HERE)))

from qc_engine.compiler.compile_llm import CompiledCheckDraft  # noqa: E402

OPAQUE_BOOLEAN_RISK = "opaque_boolean_risk"
ARCHETYPE_MISMATCH_RISK = "archetype_mismatch_risk"

# FR-007: the predicate-08 pattern -- a two-value comparison condition
# compiled into a single is_true/is_present boolean the engine just reads,
# rather than a computed comparison the engine derives itself.
_TWO_VALUE_COMPARISON_RE = re.compile(
    r"greater of|lesser of|higher of|lower of|whichever is (greater|lesser|"
    r"higher|lower)|compare[ds]?\s+(to|with)|the (greater|lesser|higher|"
    r"lower) (rate|value|amount|of)",
    re.IGNORECASE,
)

# FR-008: the reconcile-00/01 pattern -- source text that reads as a policy/
# compliance condition ("was X done", "was Y applied") rather than a genuine
# two-independent-source disagreement.
_GENUINE_COMPARISON_RE = re.compile(
    r"does not match|differs from|discrepancy between|disagrees with|"
    r"does not agree|inconsistent (with|between)",
    re.IGNORECASE,
)
_POLICY_CONDITION_RE = re.compile(
    r"\bwas\b.{0,40}\b(investigated|applied|obtained|documented|completed|"
    r"performed|verified)\b|\bshould (have|has) been\b|\bfailure to\b|"
    r"\brequired to\b",
    re.IGNORECASE,
)


@dataclass
class PatternFlag:
    check_id: str
    flag_type: str
    reason: str


def _flag_opaque_boolean_risk(draft: CompiledCheckDraft) -> List[PatternFlag]:
    if draft.check is None or draft.check.kind != "predicate":
        return []
    if _TWO_VALUE_COMPARISON_RE.search(draft.source_text):
        return [PatternFlag(
            check_id=draft.check.id, flag_type=OPAQUE_BOOLEAN_RISK,
            reason=(
                f"source text describes comparing two values ('{draft.source_text[:80]}...'), "
                "but this predicate-kind check reads a pre-computed boolean rather than "
                "deriving the comparison itself -- the predicate-08 pattern (002a RESULTS.md)."
            ),
        )]
    return []


def _flag_archetype_mismatch_risk(draft: CompiledCheckDraft) -> List[PatternFlag]:
    # 003d: agree_doc_categorical/agree_doc_numeric are the same "genuine
    # two-source comparison" family as agree_categorical/agree_numeric (just
    # doc-vs-doc instead of doc-vs-system) -- a policy condition wrongly
    # compiled as one of these deserves the same human-attention flag.
    if draft.check is None or draft.check.kind not in (
        "agree_categorical", "agree_numeric",
        "agree_doc_categorical", "agree_doc_numeric",
    ):
        return []
    looks_like_policy = bool(_POLICY_CONDITION_RE.search(draft.source_text))
    looks_like_comparison = bool(_GENUINE_COMPARISON_RE.search(draft.source_text))
    if looks_like_policy and not looks_like_comparison:
        return [PatternFlag(
            check_id=draft.check.id, flag_type=ARCHETYPE_MISMATCH_RISK,
            reason=(
                f"source text ('{draft.source_text[:80]}...') reads as a policy/compliance "
                "condition, not a genuine two-independent-source comparison -- the "
                "reconcile-00/reconcile-01 pattern (002a RESULTS.md)."
            ),
        )]
    return []


def flag_batch(drafts: List[CompiledCheckDraft]) -> List[PatternFlag]:
    flags: List[PatternFlag] = []
    for d in drafts:
        flags.extend(_flag_opaque_boolean_risk(d))
        flags.extend(_flag_archetype_mismatch_risk(d))
    return flags
