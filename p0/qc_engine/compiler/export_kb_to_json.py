"""
Read-only JSON mirror of storage/knowledge_base/kb.sqlite3, for human
inspection and git-diffability -- every other artifact under storage/
(fact_vocabulary/, rule_ontology/, loan_profiles/) is versioned JSON;
this SQLite file is the one binary exception, which makes it the one
thing in storage/ nobody can diff or read without a DB client.

This does NOT change the runtime store. `compile_llm.py` keeps reading
from kb.sqlite3 via `knowledge_base_store.py` -- that module's own
docstring explains why SQLite was chosen over scattered per-version JSON
files once the corpus passed a few hundred sections (416 today). This
script only derives a read-only mirror from it; the mirror is not a
second source of truth and is never read back by any caller. Regenerate
it any time kb.sqlite3 changes.

Output layout matches the per-program/per-version JSON shape
`compile_llm.py::_load_signed_kb_for_program` already expects as its
legacy fallback (`storage/knowledge_base/{program}/v{version}.json`),
via `knowledge_base.py`'s existing `save()` -- no new JSON shape invented.

Usage: python -m qc_engine.compiler.export_kb_to_json
"""
from __future__ import annotations

import os
import sqlite3
from contextlib import closing

from . import knowledge_base as KB
from . import knowledge_base_store as store

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_KB_DIR = os.path.join(_REPO_ROOT, "storage", "knowledge_base")
_DB_PATH = os.path.join(_KB_DIR, "kb.sqlite3")


def _all_programs(db_path: str):
    with closing(sqlite3.connect(db_path)) as conn:
        rows = conn.execute("SELECT DISTINCT program FROM kb_corpus ORDER BY program").fetchall()
    return [r[0] for r in rows]


def export_all(db_path: str = _DB_PATH, out_dir: str = _KB_DIR) -> list:
    """Writes one JSON file per (program, version) found in the DB.
    Returns the list of paths written."""
    written = []
    for program in _all_programs(db_path):
        for version in store.list_versions(db_path, program):
            corpus = store.load_from_db(db_path, program, version=version)
            if corpus is None:
                continue
            out_path = os.path.join(out_dir, program, f"v{version}.json")
            KB.save(corpus, out_path)
            written.append(out_path)
    return written


if __name__ == "__main__":
    for path in export_all():
        print(f"wrote {path}")
