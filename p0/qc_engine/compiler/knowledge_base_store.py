"""
SQLite-backed persistence for `knowledge_base.py`'s `KnowledgeBaseCorpus`/
`KBSection` -- a proper, single-file, queryable store to replace scattered
per-version JSON files once a corpus stops being a handful of hand-authored
test sections and becomes hundreds/thousands of sections parsed from a real
source document (e.g. the 1,188-page Fannie Mae Selling Guide).

Deliberately does NOT touch `knowledge_base.py`'s existing dataclasses,
`build_corpus`/`sign`/`is_usable`/`retrieve` -- this module only changes
WHERE a corpus is persisted, never what it means or how it's used. Every
existing caller (`compile_llm.py`, `layer2_grounded.py`) keeps working
against the same in-memory `KnowledgeBaseCorpus` object either way.

Chosen over Postgres for this project's current scale (a few MB of guide
text): zero setup, no server process, no new credentials/account, built
into Python's standard library, and still a real relational store with
proper indexing -- not a pile of loose JSON files. A straightforward swap
to Postgres later is possible without touching any caller, since callers
only ever see `KnowledgeBaseCorpus`/`KBSection` objects, never SQL.

Python 3.9 compatible.
"""
from __future__ import annotations

import sqlite3
from contextlib import closing
from typing import List, Optional

from .knowledge_base import KBSection, KnowledgeBaseCorpus

_SCHEMA = """
CREATE TABLE IF NOT EXISTS kb_corpus (
    program TEXT NOT NULL,
    version INTEGER NOT NULL,
    signed_by TEXT,
    signed_at TEXT,
    PRIMARY KEY (program, version)
);

CREATE TABLE IF NOT EXISTS kb_section (
    id TEXT PRIMARY KEY,
    program TEXT NOT NULL,
    corpus_version INTEGER NOT NULL,
    content TEXT NOT NULL,
    source_document TEXT NOT NULL,
    citation TEXT NOT NULL,
    content_fingerprint TEXT NOT NULL,
    FOREIGN KEY (program, corpus_version) REFERENCES kb_corpus(program, version)
);

CREATE INDEX IF NOT EXISTS idx_kb_section_program_version
    ON kb_section (program, corpus_version);
"""


def init_db(db_path: str) -> None:
    with closing(sqlite3.connect(db_path)) as conn:
        conn.executescript(_SCHEMA)
        conn.commit()


def save_to_db(corpus: KnowledgeBaseCorpus, db_path: str) -> None:
    """One (program, version) row plus its sections -- never overwrites a
    prior version's rows (same provenance guarantee `knowledge_base.py`'s
    file-based `save()` already gives: `update_corpus()`'s new version number
    is a fresh primary key, not a mutation of the old one)."""
    init_db(db_path)
    with closing(sqlite3.connect(db_path)) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO kb_corpus (program, version, signed_by, signed_at) "
            "VALUES (?, ?, ?, ?)",
            (corpus.program, corpus.version, corpus.signed_by, corpus.signed_at),
        )
        conn.executemany(
            "INSERT OR REPLACE INTO kb_section "
            "(id, program, corpus_version, content, source_document, citation, content_fingerprint) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                (s.id, corpus.program, corpus.version, s.content, s.source_document,
                 s.citation, s.content_fingerprint)
                for s in corpus.sections
            ],
        )
        conn.commit()


def list_versions(db_path: str, program: str) -> List[int]:
    with closing(sqlite3.connect(db_path)) as conn:
        rows = conn.execute(
            "SELECT version FROM kb_corpus WHERE program = ? ORDER BY version DESC",
            (program,),
        ).fetchall()
    return [r[0] for r in rows]


def load_from_db(db_path: str, program: str, version: Optional[int] = None) -> Optional[KnowledgeBaseCorpus]:
    """Loads the given version, or the highest version on disk if `version`
    is None. Returns None if the program has no corpus at all (mirrors
    `compile_llm.py`'s existing fallback-to-None-is-fine contract -- a
    missing/unbuilt KB is never a hard error, just no grounding this run)."""
    with closing(sqlite3.connect(db_path)) as conn:
        if version is None:
            row = conn.execute(
                "SELECT version, signed_by, signed_at FROM kb_corpus "
                "WHERE program = ? ORDER BY version DESC LIMIT 1",
                (program,),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT version, signed_by, signed_at FROM kb_corpus "
                "WHERE program = ? AND version = ?",
                (program, version),
            ).fetchone()
        if row is None:
            return None
        resolved_version, signed_by, signed_at = row

        section_rows = conn.execute(
            "SELECT id, content, source_document, citation, content_fingerprint "
            "FROM kb_section WHERE program = ? AND corpus_version = ? ORDER BY id",
            (program, resolved_version),
        ).fetchall()

    sections = [
        KBSection(id=r[0], program=program, content=r[1], source_document=r[2],
                  citation=r[3], content_fingerprint=r[4])
        for r in section_rows
    ]
    return KnowledgeBaseCorpus(program=program, version=resolved_version, sections=sections,
                               signed_by=signed_by, signed_at=signed_at)
