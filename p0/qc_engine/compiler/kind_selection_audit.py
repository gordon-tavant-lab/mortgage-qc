"""
Finding #2 (the doc-vs-doc-vs-system compile-kind gap): a deterministic,
zero-LLM detector for checks compiled as `agree_categorical`/`agree_numeric`
(doc-vs-*system*) whose field structurally has NO system side to compare
against -- `field_catalog.json`'s `expected_sources == ["doc"]` -- and are
therefore always comparing against `sv.system_value()` returning `None`, a
silent wrong-verdict miscompile of the exact same class
`known_compile_corrections.py` already hand-fixed for two checks.

This is the general-purpose gate; `known_compile_corrections.py` is the
narrow, already-SME-confirmed subset of it (both corrected checks' target
`kind`/`compare_field_name` are SME-groundable facts, not guesses -- see
that module's own docstring). This module does NOT attempt the SME judgement
`compare_field_name` requires for the remaining suspects -- per the
constitution's zero-false-auto-clear gate, exclusion + reporting is the
correct behavior for an unaudited structural mismatch, not a guessed fix
(CLAUDE.md Non-Negotiable #1: "an honest UNSPECIFIED beats a confident
invented value").

Python 3.9 compatible.
"""
from __future__ import annotations

from typing import Any, Dict, List

_STRUCTURALLY_SYSTEMLESS_KINDS = ("agree_categorical", "agree_numeric")


def find_structural_kind_mismatches(checks, catalog) -> List[Dict[str, Any]]:
    """For every check compiled as `agree_categorical`/`agree_numeric` (doc-
    vs-system), look up its `field_name` in `catalog`. If the catalog entry
    exists and its `expected_sources` is exactly `["doc"]` (no "los"/"mismo"
    -- i.e. there is structurally no system value this field could ever be
    compared against), this check can never be a real doc-vs-system
    comparison; it is a miscompile of the same class
    `known_compile_corrections.py` already hand-fixed two instances of.

    A check whose `field_name` doesn't resolve in `catalog` at all is left
    to the separate referential-integrity gate (`catalog.py`'s
    `validate_referential_integrity`) -- not this detector's job, and not
    silently treated as a mismatch here (an unresolved reference is a
    different failure mode with its own dedicated screen).

    Pure and deterministic: same `checks`/`catalog` in, same result out,
    every time -- no LLM call, no mutation of either argument.

    Returns a list of `{"check_id": ..., "field_name": ...}` dicts, one per
    structural mismatch found, in the same order as `checks`."""
    mismatches: List[Dict[str, Any]] = []
    for chk in checks:
        if chk.kind not in _STRUCTURALLY_SYSTEMLESS_KINDS:
            continue
        entry = catalog.get(chk.field_name)
        if entry is None:
            continue
        if list(entry.expected_sources) == ["doc"]:
            mismatches.append({"check_id": chk.id, "field_name": chk.field_name})
    return mismatches
