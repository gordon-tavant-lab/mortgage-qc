"""promote_naming_proposals.py: the deterministic conversion of MEDIUM-tier
LLM naming proposals into real CanonicalFact objects. No LLM call happens
here -- these tests exercise the merge/collision/disclosure logic directly."""
import os
import sys

import pytest

_P0 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _P0 not in sys.path:
    sys.path.insert(0, _P0)

from qc_engine.compiler import promote_naming_proposals as P  # noqa: E402


def _entry(question_key, data_type, answer_value_map):
    return (question_key, {"data_type": data_type, "answer_value_map": answer_value_map,
                            "description": "d", "proposed_field_name": "irrelevant-here"})


def test_no_contradiction_when_answers_agree_across_questions():
    entries = [
        _entry("q1", "boolean", {"Yes": "true"}),
        _entry("q2", "boolean", {"Yes": "true"}),
    ]
    assert P._find_contradictions(entries) == []


def test_contradiction_when_same_answer_maps_to_different_values():
    entries = [
        _entry("q1", "boolean", {"Yes": "true"}),
        _entry("q2", "boolean", {"Yes": "false"}),  # disagrees with q1
    ]
    conflicts = P._find_contradictions(entries)
    assert conflicts and conflicts[0][0] == "Yes"


def test_contradiction_when_data_types_disagree():
    entries = [
        _entry("q1", "boolean", {"Yes": "true"}),
        _entry("q2", "enum", {"Yes": "yes_value"}),
    ]
    conflicts = P._find_contradictions(entries)
    assert any(c[0] == "__data_type__" for c in conflicts)


def test_build_fact_refuses_to_merge_on_conflict():
    entries = [
        _entry("q1", "boolean", {"Yes": "true"}),
        _entry("q2", "boolean", {"Yes": "false"}),
    ]
    with pytest.raises(P.NameCollisionConflictError):
        P._build_fact("some_fact", entries, row_ids_by_q={})


def test_build_fact_merges_clean_cross_question_group_into_one_fact():
    entries = [
        _entry("q1", "boolean", {"Yes, present": "true", "No, missing": "false"}),
        _entry("q2", "boolean", {"Yes, present": "true"}),
    ]
    fact = P._build_fact("thing_present", entries, row_ids_by_q={})
    assert fact.canonical_field_name == "thing_present"
    assert fact.id == "fact-thing-present"
    qkeys = {b.question_key for b in fact.question_bindings}
    assert qkeys == {"q1", "q2"}
    # every (question, canonical_value) pair became its own binding
    values_by_q = {(b.question_key, b.canonical_value) for b in fact.question_bindings}
    assert ("q1", "true") in values_by_q and ("q1", "false") in values_by_q
    assert ("q2", "true") in values_by_q


def test_build_fact_discloses_llm_origin_and_pending_review():
    entries = [_entry("q1", "boolean", {"Yes": "true"})]
    fact = P._build_fact("thing", entries, row_ids_by_q={})
    assert "NOT yet reviewed" in fact.promotion_note
    assert "naming_proposals_v1.json" in fact.promotion_note


def test_build_fact_discloses_the_merge_when_multiple_questions_involved():
    entries = [
        _entry("q1", "boolean", {"Yes": "true"}),
        _entry("q2", "boolean", {"Yes": "true"}),
        _entry("q3", "boolean", {"Yes": "true"}),
    ]
    fact = P._build_fact("thing", entries, row_ids_by_q={})
    assert "Merged across 3 AMQ question keys" in fact.promotion_note


def test_citation_sampling_caps_at_five_with_overflow_note():
    row_ids_by_q = {"q1": [f"pc-retail-{i:05d}" for i in range(12)]}
    cites = P._citation_for_question("q1", row_ids_by_q)
    assert len(cites) == 6  # 5 sampled + 1 overflow line
    assert cites[-1] == "... and 7 more rows sharing question q1"
