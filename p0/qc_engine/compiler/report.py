"""
Assembles `contracts/batch-report-schema.md`'s shape -- the SME-reviewable
artifact combining the referential-integrity screen (User Story 3), the
consistency report (FR-003), and the pattern flags (User Story 4) into one
document, for a compiled batch prior to sign-off.

Python 3.9 compatible.
"""
from __future__ import annotations

import os
import sys
from typing import Any, Dict, List

_HERE = os.path.dirname(os.path.abspath(__file__))
if os.path.dirname(os.path.dirname(_HERE)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.dirname(_HERE)))

from qc_engine.catalog import FieldCatalog  # noqa: E402
from qc_engine.compiler.compile_llm import CompiledCheckDraft  # noqa: E402
from qc_engine.compiler.catalog_screen import (  # noqa: E402
    screen_batch_referential_integrity, RESOLVED, SIGNABLE_PENDING_CATALOG_ENTRY, BLOCKED,
)
from qc_engine.compiler.consistency import build_consistency_report  # noqa: E402
from qc_engine.compiler.pattern_flags import flag_batch  # noqa: E402


def build_batch_report(
    batch_id: str, drafts: List[CompiledCheckDraft], catalog: FieldCatalog,
) -> Dict[str, Any]:
    screen = screen_batch_referential_integrity(drafts, catalog)
    resolved = [k for k, v in screen.items() if v["status"] == RESOLVED]
    pending = [k for k, v in screen.items() if v["status"] == SIGNABLE_PENDING_CATALOG_ENTRY]
    blocked = [{"check_id": k, "reason": v["reason"]}
               for k, v in screen.items() if v["status"] == BLOCKED]

    consistency = build_consistency_report(batch_id, drafts)
    pattern_flags = flag_batch(drafts)

    return {
        "batch_id": batch_id,
        "rows_compiled": len(drafts),
        "referential_integrity": {
            "resolved": resolved,
            "signable_pending_catalog_entry": pending,
            "blocked": blocked,
        },
        "consistency_report": {
            "duplicate_flags": [
                {"field_name_a": f.field_name_a, "field_name_b": f.field_name_b,
                 "edit_distance": f.edit_distance, "check_ids": f.check_ids}
                for f in consistency.duplicate_flags
            ],
        },
        "pattern_flags": [
            {"check_id": f.check_id, "flag_type": f.flag_type, "reason": f.reason}
            for f in pattern_flags
        ],
    }
