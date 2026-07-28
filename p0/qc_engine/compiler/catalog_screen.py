"""
User Story 3 (002b): screen a batch of CompiledCheckDraft against the 001a
field catalog BEFORE any is eligible for SME sign-off -- moving the existing
SAFE gate (`validate_referential_integrity`) earlier in the pipeline.

Wraps the existing validator per-candidate-check rather than modifying it
(research.md Decision 4): `validate_referential_integrity` raises on the
FIRST unresolved check in a whole Ruleset -- correct for its proven one-shot
use in `p0/harness.py`, but insufficient for reporting which of potentially
dozens of drafts in one batch are blocked. Calling it once per candidate
check via a throwaway single-check Ruleset gets per-check batch reporting
with zero changes to the existing function's contract.

Python 3.9 compatible.
"""
from __future__ import annotations

import os
import sys
from typing import Dict, List, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
if os.path.dirname(_HERE) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.dirname(_HERE)))

from qc_engine.catalog import FieldCatalog, ReferentialIntegrityError, validate_referential_integrity  # noqa: E402
from qc_engine.ruleset import Ruleset  # noqa: E402
from qc_engine.compiler.compile_llm import CompiledCheckDraft  # noqa: E402

# Per-check screen result buckets (contracts/batch-report-schema.md).
RESOLVED = "resolved"
SIGNABLE_PENDING_CATALOG_ENTRY = "signable_pending_catalog_entry"
BLOCKED = "blocked"


def screen_check(draft: CompiledCheckDraft, catalog: FieldCatalog) -> Dict[str, Optional[str]]:
    """Screen one draft. Returns {"status": ..., "reason": Optional[str]}."""
    if draft.check is None:
        return {"status": BLOCKED, "reason": f"draft {draft.row_id} failed to parse: {draft.parse_error}"}

    throwaway = Ruleset(ruleset_id="_screen", version=0, checks=[draft.check])
    try:
        validate_referential_integrity(throwaway, catalog)
        return {"status": RESOLVED, "reason": None}
    except ReferentialIntegrityError as e:
        if draft.proposed_field_entry is not None:
            return {"status": SIGNABLE_PENDING_CATALOG_ENTRY, "reason": str(e)}
        return {"status": BLOCKED, "reason": str(e)}


def screen_batch_referential_integrity(
    drafts: List[CompiledCheckDraft], catalog: FieldCatalog,
) -> Dict[str, Dict[str, Optional[str]]]:
    """check_id (or row_id, if unparseable) -> screen result, for the whole
    batch. Only BLOCKED entries are a hard stop on sign-off (User Story 3);
    SIGNABLE_PENDING_CATALOG_ENTRY becomes RESOLVED once its paired
    proposed_field_entry is itself signed into the catalog (research.md
    Decision 2)."""
    result: Dict[str, Dict[str, Optional[str]]] = {}
    for d in drafts:
        key = d.check.id if d.check is not None else d.row_id
        result[key] = screen_check(d, catalog)
    return result
