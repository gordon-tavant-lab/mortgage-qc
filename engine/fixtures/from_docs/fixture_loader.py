"""
fixture_loader.py — loads a build_fixtures.py-generated JSON fixture into the
EXISTING qc_engine/model.py CanonicalLoan/SourceValue/DocCitation classes,
with zero changes to model.py itself (US1's own acceptance bar). This module
is fixture-generation-side code, not engine code.

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from qc_engine.model import CanonicalLoan, DocCitation, SourceValue  # noqa: E402


def load_canonical_loan(fixture_path: str) -> CanonicalLoan:
    with open(fixture_path, "r", encoding="utf-8") as f:
        data: Dict[str, Any] = json.load(f)

    fields = {}
    for name, entry in data.get("fields", {}).items():
        citation = None
        if entry.get("citation"):
            c = entry["citation"]
            citation = DocCitation(
                doc_name=c["doc_name"],
                page_num=c["page_num"],
                segment_snippet=c["segment_snippet"],
                document_title=c.get("document_title"),
                section=c.get("section"),
                field_label=c.get("field_label"),
                document_ids=c.get("document_ids"),
            )
        fields[name] = SourceValue(
            truth=entry.get("truth"),
            sources=dict(entry.get("sources") or {}),
            citation=citation,
            doc_confidence=entry.get("doc_confidence"),
        )

    return CanonicalLoan(
        loan_id=data["loan_id"],
        loan_type=data.get("loan_type", ""),
        fields=fields,
        facts=dict(data.get("facts") or {}),
    )
