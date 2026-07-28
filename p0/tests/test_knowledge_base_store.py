"""
Tests for the SQLite-backed KB persistence layer (`knowledge_base_store.py`)
-- replaces the flat-JSON-file store once a corpus scales past a handful of
hand-authored sections. Confirms round-trip fidelity and multi-version
provenance (a prior version's rows are untouched by writing a new one).

Python 3.9 compatible.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_P0 = os.path.dirname(_HERE)
if _P0 not in sys.path:
    sys.path.insert(0, _P0)

import pytest  # noqa: E402

from qc_engine.compiler.knowledge_base import KBSection, KnowledgeBaseCorpus, build_corpus, sign  # noqa: E402
from qc_engine.compiler import knowledge_base_store as store  # noqa: E402


@pytest.fixture()
def db_path(tmp_path):
    return str(tmp_path / "kb.sqlite3")


def _sample_corpus(program="TESTPROGRAM", version=1):
    corpus = build_corpus(program, [
        {"source_document": "Doc A", "citation": "A-1", "content": "Gift funds must be documented."},
        {"source_document": "Doc B", "citation": "B-2", "content": "Reserves must cover six months."},
    ], version=version)
    return sign(corpus, signed_by="test-sme", signed_at="2026-07-26")


def test_round_trip_preserves_every_field(db_path):
    corpus = _sample_corpus()
    store.save_to_db(corpus, db_path)
    loaded = store.load_from_db(db_path, "TESTPROGRAM")

    assert loaded is not None
    assert loaded.program == corpus.program
    assert loaded.version == corpus.version
    assert loaded.signed_by == corpus.signed_by
    assert loaded.signed_at == corpus.signed_at
    assert len(loaded.sections) == len(corpus.sections)
    by_id = {s.id: s for s in loaded.sections}
    for original in corpus.sections:
        loaded_section = by_id[original.id]
        assert loaded_section.content == original.content
        assert loaded_section.source_document == original.source_document
        assert loaded_section.citation == original.citation
        assert loaded_section.content_fingerprint == original.content_fingerprint


def test_missing_program_returns_none(db_path):
    store.init_db(db_path)
    assert store.load_from_db(db_path, "NOPE") is None


def test_load_defaults_to_highest_version(db_path):
    v1 = _sample_corpus(version=1)
    v2 = _sample_corpus(version=2)
    store.save_to_db(v1, db_path)
    store.save_to_db(v2, db_path)

    loaded = store.load_from_db(db_path, "TESTPROGRAM")
    assert loaded.version == 2


def test_prior_version_untouched_by_writing_a_new_one(db_path):
    """Same provenance guarantee the file-based store gives (US2, 002c): a
    rule compiled and signed against version N must still resolve version
    N's exact content after version N+1 is written."""
    v1 = _sample_corpus(version=1)
    store.save_to_db(v1, db_path)

    v2 = _sample_corpus(version=2)
    store.save_to_db(v2, db_path)

    reloaded_v1 = store.load_from_db(db_path, "TESTPROGRAM", version=1)
    assert reloaded_v1 is not None
    assert reloaded_v1.version == 1
    assert {s.id for s in reloaded_v1.sections} == {s.id for s in v1.sections}


def test_list_versions_descending(db_path):
    store.save_to_db(_sample_corpus(version=1), db_path)
    store.save_to_db(_sample_corpus(version=3), db_path)
    store.save_to_db(_sample_corpus(version=2), db_path)
    assert store.list_versions(db_path, "TESTPROGRAM") == [3, 2, 1]


def test_unsigned_corpus_round_trips_as_unsigned(db_path):
    unsigned = build_corpus("UNSIGNED", [
        {"source_document": "Doc", "citation": "C", "content": "text"},
    ])
    store.save_to_db(unsigned, db_path)
    loaded = store.load_from_db(db_path, "UNSIGNED")
    assert loaded.signed_by is None
    assert loaded.signed_at is None


def test_multiple_programs_isolated(db_path):
    store.save_to_db(_sample_corpus(program="FHA"), db_path)
    store.save_to_db(_sample_corpus(program="VA"), db_path)
    assert store.load_from_db(db_path, "FHA").program == "FHA"
    assert store.load_from_db(db_path, "VA").program == "VA"
    assert store.load_from_db(db_path, "USDA") is None
