"""
002c -- compile_row()'s grounding wiring (US3).

Proves compile_row() looks up a signed KB for the row's program and
populates `grounding` when one exists, and falls back to today's ungrounded
002b behavior (grounding=None) when it doesn't -- FR-006, additive, never a
hard blocker. Uses a STUBBED Bedrock client (no live network call) --
compile_row()'s own real-API-call behavior is exercised separately, same
precedent 002b's own compile_row()/compile_batch() already established
(see test_p0.py's 002b section comment).

Run from p0/:  python -m pytest tests/test_grounded_compilation.py -v
Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qc_engine.catalog import FieldCatalog
from qc_engine.compiler import compile_llm as C
from qc_engine.compiler import knowledge_base as KB


def _stub_bedrock_client(check_json):
    """A fake client whose .converse() returns a well-formed compile
    response, so compile_row()'s grounding wiring can be tested without a
    real network call."""
    client = MagicMock()
    response_text = json.dumps({
        "check": check_json,
        "plain_english_restatement": "test restatement",
    })
    client.converse.return_value = {
        "output": {"message": {"content": [{"text": response_text}]}}
    }
    return client


def _fha_check_json():
    return {
        "id": "chk-test-gift-funds", "name": "Gift funds documented",
        "field_name": "gift_funds_source_documented", "kind": "predicate",
        "predicate": "is_true", "severity": "CRITICAL", "phase": "QC",
        "message_pass": "Gift funds documented.",
        "message_fail": "Gift funds not documented.",
    }


def _empty_catalog():
    return FieldCatalog(catalog_id="test-catalog", version=1, entries=[])


# --- T017: grounding field defaults to None, existing sites unaffected ----
def test_compiled_check_draft_grounding_defaults_to_none():
    draft = C.CompiledCheckDraft(row_id="r1", check=None, source_text="x",
                                 extracted_intent="")
    assert draft.grounding is None


# --- T018: compile_row() populates grounding when a signed KB exists ------
def test_compile_row_populates_grounding_when_signed_kb_exists():
    kb_documents = [
        {"source_document": "HUD Handbook 4000.1, II.A.8.a",
         "citation": "hud.gov/4000.1",
         "content": "Gift funds must be documented with a signed gift letter and "
                     "evidence of the transfer of funds from the donor."},
    ]
    corpus = KB.sign(KB.build_corpus("FHA", kb_documents, version=1),
                     signed_by="kayla.sme@lender.example", signed_at="2026-07-20T10:00:00Z")

    with tempfile.TemporaryDirectory() as tmpdir:
        kb_dir = os.path.join(tmpdir, "FHA")
        KB.save(corpus, os.path.join(kb_dir, "v1.json"))

        original_kb_dir = C._KB_DIR
        C._KB_DIR = tmpdir
        try:
            client = _stub_bedrock_client(_fha_check_json())
            row = {
                "row_id": "predicate-000", "qcode": "Final URLA",
                "defect_text": "Gift funds source not documented in the file",
                "engine_kind": "predicate", "significance": "Critical",
                "exception_code": "O-FHA-15293", "sql_criteria": "",
            }
            draft = C.compile_row(client, row, _empty_catalog())

            assert draft.grounding is not None
            assert draft.grounding.kb_program == "FHA"
            assert draft.grounding.kb_version == 1
            assert len(draft.grounding.section_ids) >= 1

            # The retrieved grounding text actually reached the prompt sent
            # to the model -- not just recorded on the draft after the fact.
            sent_prompt = client.converse.call_args.kwargs["messages"][0]["content"][0]["text"]
            assert "signed gift letter" in sent_prompt
        finally:
            C._KB_DIR = original_kb_dir


# --- T018 (fallback half): no signed KB for the program -> grounding=None -
def test_compile_row_falls_back_ungrounded_when_no_kb_exists():
    with tempfile.TemporaryDirectory() as tmpdir:
        original_kb_dir = C._KB_DIR
        C._KB_DIR = tmpdir  # empty -- no program directories at all
        try:
            client = _stub_bedrock_client(_fha_check_json())
            row = {
                "row_id": "predicate-001", "qcode": "Final URLA",
                "defect_text": "Gift funds source not documented in the file",
                "engine_kind": "predicate", "significance": "Critical",
                "exception_code": "O-FHA-15293", "sql_criteria": "",
            }
            draft = C.compile_row(client, row, _empty_catalog())
            assert draft.grounding is None
            assert draft.check is not None  # compilation itself still succeeds
        finally:
            C._KB_DIR = original_kb_dir


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
