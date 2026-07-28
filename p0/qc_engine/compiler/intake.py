"""
002c -- intake gate: halt on a document type never seen before (US5, FR-011).

The first step of the 10-step intake workflow (spec.md US5). A document
type not already in the known set MUST halt for mandatory human triage
before any extraction happens -- never silently auto-processed. This is
intentionally the one piece of the intake workflow that IS a hard,
unconditional gate (unlike grounding/judging, which degrade gracefully) --
an unrecognized document type means nobody has decided yet what fields or
program it maps to, so there is nothing safe to do with it automatically.

Python 3.9 compatible.
"""
from __future__ import annotations

from typing import Iterable


class UnknownDocumentTypeError(Exception):
    """Raised when intake sees a document type not in the known set --
    the mandatory human-triage halt (FR-011)."""


def classify_and_gate(document_type: str, known_types: Iterable[str]) -> None:
    """Raises UnknownDocumentTypeError if `document_type` is not already
    known. Returns None (no exception) when it is -- intake may proceed."""
    if document_type not in set(known_types):
        raise UnknownDocumentTypeError(
            f"document type {document_type!r} has never been seen before -- "
            "halting for mandatory human triage before any extraction runs "
            "(spec.md FR-011); add it to the known-types set only after a "
            "human has reviewed and classified it."
        )
