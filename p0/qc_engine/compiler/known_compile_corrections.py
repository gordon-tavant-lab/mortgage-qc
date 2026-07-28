"""
Known, SME-groundable compile-time corrections -- deterministic, zero-LLM,
applied at compile time (Non-Negotiable #1: compile, then run).

Two checks in the comprehensive ruleset were miscompiled as `agree_categorical`
(doc-vs-*system*, `compare_field_name: null`) when they are actually doc-vs-doc
comparisons: 1003 vs. VOE employment dates, and 1003 vs. Title Commitment
vesting. Both belong to `agree_doc_categorical` with a real `compare_field_name`
-- confirmed against loan 01's `defect_manifest.json` defects #1/#2, and against
`field_catalog.json`, which already catalogues both compare fields as real,
populated, doc-sourced fields.

Python 3.9 compatible.
"""
from __future__ import annotations

from typing import Dict, List

KNOWN_CORRECTIONS: Dict[str, Dict[str, str]] = {
    "employment-dates-1003-vs-docs-agree": {
        "kind": "agree_doc_categorical",
        "compare_field_name": "employment_start_date_voe",
    },
    "title-vesting-1003-vs-commitment": {
        "kind": "agree_doc_categorical",
        "compare_field_name": "title_vesting_commitment",
    },
}


def apply_known_compile_corrections(checks) -> List[str]:
    """Mutates matching Check objects in `checks` in place. Returns the ids
    of checks actually corrected (order-preserving, only ids present in both
    `checks` and KNOWN_CORRECTIONS)."""
    corrected = []
    for chk in checks:
        fix = KNOWN_CORRECTIONS.get(chk.id)
        if fix is None:
            continue
        for field_name, value in fix.items():
            setattr(chk, field_name, value)
        corrected.append(chk.id)
    return corrected
