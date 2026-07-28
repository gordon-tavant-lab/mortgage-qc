"""Persisted Layer-0 rule-ontology artifact (`storage/rule_ontology/v1.json`):
proves it's a byte-deterministic reorganization of the real AMQ workbook rows,
never recomputed differently between runs, and internally self-consistent
(every dependent_row_id it claims actually exists in the source fixture).
Zero LLM calls anywhere."""
import json
import os
import sys

_P0 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _P0 not in sys.path:
    sys.path.insert(0, _P0)

from qc_engine.compiler.build_rule_ontology_artifact import (  # noqa: E402
    build_artifact, ROWS_PATH, OUT_PATH,
)

_REPO_ROOT = os.path.dirname(_P0)


def _load_shipped_artifact():
    with open(OUT_PATH) as f:
        return json.load(f)


def test_shipped_artifact_loads():
    artifact = _load_shipped_artifact()
    assert artifact["version"] == 1
    assert artifact["total_rows"] == 5520
    assert len(artifact["entries"]) == 24


def test_rebuild_from_fixture_is_byte_identical_to_shipped_artifact():
    """Determinism: re-running the builder against the same real fixture
    rows must reproduce the shipped artifact byte-for-byte."""
    rebuilt = build_artifact()
    with open(OUT_PATH) as f:
        shipped_raw = f.read()
    rebuilt_raw = json.dumps(rebuilt, indent=2, sort_keys=True) + "\n"
    assert rebuilt_raw == shipped_raw


def test_rebuild_twice_is_also_identical():
    """Pure function: two in-process rebuilds agree with each other too,
    not just with the file on disk."""
    first = build_artifact()
    second = build_artifact()
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_570606_entry_has_yes_gift_and_362_dependents():
    artifact = _load_shipped_artifact()
    entry = next(e for e in artifact["entries"] if e["question_key"] == "570606")
    assert "Yes - Gift" in entry["answer_vocabulary"]
    assert entry["dependent_row_count"] == 362
    assert len(entry["dependent_row_ids"]) == 362


def test_coverage_matches_real_cluster():
    artifact = _load_shipped_artifact()
    assert artifact["coverage"]["resolved_rows"] == 3255
    assert artifact["coverage"]["total_rows"] == 5520


def test_every_dependent_row_id_exists_in_the_fixture():
    artifact = _load_shipped_artifact()
    with open(ROWS_PATH) as f:
        rows = json.load(f)
    fixture_row_ids = {row["row_id"] for row in rows}
    for entry in artifact["entries"]:
        for row_id in entry["dependent_row_ids"]:
            assert row_id in fixture_row_ids, (
                f"artifact claims dependent row {row_id!r} for question "
                f"{entry['question_key']!r} but it is not in the fixture")


def test_every_unparsed_row_id_exists_in_the_fixture():
    artifact = _load_shipped_artifact()
    with open(ROWS_PATH) as f:
        rows = json.load(f)
    fixture_row_ids = {row["row_id"] for row in rows}
    for row_id in artifact["unparsed_row_ids"]:
        assert row_id in fixture_row_ids


def test_source_path_is_relative_to_repo_root():
    artifact = _load_shipped_artifact()
    resolved = os.path.join(_REPO_ROOT, artifact["source"])
    assert os.path.abspath(resolved) == os.path.abspath(ROWS_PATH)


def test_entries_sorted_by_question_key():
    artifact = _load_shipped_artifact()
    keys = [e["question_key"] for e in artifact["entries"]]
    assert keys == sorted(keys)


def test_answer_vocabulary_and_dependent_row_ids_sorted_within_each_entry():
    artifact = _load_shipped_artifact()
    for entry in artifact["entries"]:
        assert entry["answer_vocabulary"] == sorted(entry["answer_vocabulary"])
        assert entry["dependent_row_ids"] == sorted(entry["dependent_row_ids"])
        assert entry["dependent_row_count"] == len(entry["dependent_row_ids"])


def test_note_present_and_disclaims_sme_signature():
    artifact = _load_shipped_artifact()
    note = artifact["note"].lower()
    assert "deterministic" in note
    assert "no sme signature" in note or "needs no sme signature" in note
