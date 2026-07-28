"""Self-discovered canonical-fact candidates: the artifact is real,
deterministic, refuses to name anything, and traces every element to real
data (rule ontology rows / signed KB / field catalog)."""
import json
import os
import subprocess
import sys

_P0 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_REPO_ROOT = os.path.dirname(_P0)
if _P0 not in sys.path:
    sys.path.insert(0, _P0)

CANDIDATES = os.path.join(_REPO_ROOT, "storage", "fact_vocabulary",
                          "candidates", "v1.json")
ONTOLOGY = os.path.join(_REPO_ROOT, "storage", "rule_ontology", "v1.json")
SCRIPT = os.path.join(_P0, "qc_engine", "compiler", "discover_fact_candidates.py")


def _load():
    with open(CANDIDATES) as f:
        return json.load(f)


def test_artifact_covers_every_decoded_question():
    with open(ONTOLOGY) as f:
        ontology = json.load(f)
    cand = _load()
    assert {c["question_key"] for c in cand["candidates"]} == \
        {e["question_key"] for e in ontology["entries"]}
    assert len(cand["candidates"]) == 24  # the real decoded count


def test_no_candidate_carries_an_auto_proposed_name():
    """The load-bearing refusal: discovery assembles evidence, it never
    names -- a canonical field name is owned semantic content (002f
    trust-tier discipline)."""
    for c in _load()["candidates"]:
        assert c["proposed_field_name"] is None, c["question_key"]


def test_gift_question_is_fully_bound_after_vocabulary_expansion():
    """2026-07-27: promote_naming_proposals.py bound the other 16 real
    answers of question 570606 to closing_funds_asset_type -- this question
    is now fully covered, not just the gift answer. Confirms the promotion
    closed the gap this candidate artifact originally surfaced."""
    cand = _load()
    q = next(c for c in cand["candidates"] if c["question_key"] == "570606")
    assert q["status"] == "PARTIALLY_BOUND"
    assert q["already_bound_answers"]["Yes - Gift"] == "gift_funds_used"
    assert set(q["already_bound_answers"].values()) == {
        "gift_funds_used", "closing_funds_asset_type"}
    unbound = set(q["answer_vocabulary"]) - set(q["already_bound_answers"])
    assert unbound == set()


def test_rebuild_is_byte_identical():
    with open(CANDIDATES, "rb") as f:
        before = f.read()
    subprocess.run([sys.executable, SCRIPT], check=True, capture_output=True)
    with open(CANDIDATES, "rb") as f:
        after = f.read()
    assert before == after


def test_guide_suggestions_are_citation_strings_only():
    for c in _load()["candidates"]:
        for g in c["guide_citation_suggestions"]:
            assert isinstance(g, str)
            assert g.startswith("Fannie Mae Selling Guide ")
            assert len(g) < 200  # a pointer, never section content
