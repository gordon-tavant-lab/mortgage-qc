"""
002f: tests for the precondition ontology layer (Layer 0/1/2 + pipeline).

Layer 0 is tested against the real, checked-in Retail Post-Closing fixture
(`p0/fixtures/ontology_extraction/retail_post_closing_rows.json`, extracted
by `build_fixture.py` from the actual workbook). Layer 1/2's LLM-calling
paths are tested with a constructed fake `client` (no live Bedrock call) --
matching this project's convention of keeping live-model paths out of the
fast pytest suite (`compile_llm.py`'s own tests follow the same split).

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))
_P0 = os.path.join(_REPO_ROOT, "p0")
if _P0 not in sys.path:
    sys.path.insert(0, _P0)

import pytest  # noqa: E402

from ontology_extraction import layer0_clustering as L0  # noqa: E402
from ontology_extraction import layer1_extraction as L1  # noqa: E402
from ontology_extraction import layer2_grounded as L2  # noqa: E402
from ontology_extraction import pipeline  # noqa: E402
from qc_engine.compiler import knowledge_base as KB  # noqa: E402
from qc_engine.compiler import judge_panel as JP  # noqa: E402

_FIXTURE_PATH = os.path.join(
    _P0, "fixtures", "ontology_extraction", "retail_post_closing_rows.json"
)


@pytest.fixture(scope="module")
def real_rows():
    with open(_FIXTURE_PATH) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Layer 0
# ---------------------------------------------------------------------------

def test_layer0_reproduces_real_ontology(real_rows):
    """SC-001/T005: reproduces the 24-entry, 3,255-row result independently
    against the real Retail Post-Closing fixture."""
    result = L0.cluster(real_rows)
    assert len(result.entries) == 24
    assert result.coverage.resolved_rows == 3255
    assert result.coverage.total_rows == 5520


def test_layer0_unparsed_row_reported():
    """FR-002/T006: a row with a dependency expression that doesn't match
    the configured pattern is reported as unparsed, never silently dropped
    or partially matched."""
    rows = [
        {"row_id": "r1", "question_criteria_by_q": "QuestionID == 123 && AnswerText == \"Yes\""},
        {"row_id": "r2", "question_criteria_by_q": "IF SOME_OTHER_SYNTAX(456) THEN X"},
        {"row_id": "r3", "question_criteria_by_q": ""},
    ]
    result = L0.cluster(rows)
    assert len(result.entries) == 1
    assert result.entries[0].key == "123"
    assert [u.row_id for u in result.unparsed] == ["r2"]
    # r3 has no expression at all -- not unparsed, just not Layer 0's concern.
    assert result.coverage.resolved_rows == 1
    assert result.coverage.total_rows == 3


def test_layer0_deterministic(real_rows):
    """T007: byte-identical output across repeated runs -- pure function,
    no nondeterminism."""
    r1 = L0.cluster(real_rows)
    r2 = L0.cluster(real_rows)
    assert r1.entries == r2.entries
    assert r1.unparsed == r2.unparsed
    assert r1.coverage == r2.coverage


def test_layer0_multi_key_row_joins_every_referenced_key():
    """A row referencing more than one dependency key (real example in the
    fixture: an OR across several applicants' identical question, one
    QuestionID per applicant) is added to every key it references."""
    rows = [{
        "row_id": "multi",
        "question_criteria_by_q": (
            '(QuestionID == 1 && AnswerText == "Yes") OR '
            '(QuestionID == 2 && AnswerText == "Yes")'
        ),
    }]
    result = L0.cluster(rows)
    keys = {e.key for e in result.entries}
    assert keys == {"1", "2"}
    assert all("multi" in e.dependent_row_ids for e in result.entries)


# ---------------------------------------------------------------------------
# Layer 1 (fake client -- no live Bedrock call)
# ---------------------------------------------------------------------------

class _FakeLayer1Client:
    """Returns a fixed sequence of raw response texts, one per `.converse()`
    call -- lets a test simulate N-1 malformed attempts then a valid one, or
    permanently malformed output."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.call_count = 0

    def converse(self, **kwargs):
        text = self._responses[min(self.call_count, len(self._responses) - 1)]
        self.call_count += 1
        return {"output": {"message": {"content": [{"text": text}]}}}


def _l1_json(deontic="NONE", cross_ref=None, precondition=None, span=None):
    return json.dumps({
        "deontic_modality": deontic, "cross_reference_target": cross_ref,
        "precondition": precondition, "quoted_span": span,
    })


def test_layer1_extracts_stated_precondition():
    """Acceptance Scenario 1 (T009): a row whose own text names its topic
    clearly extracts the precondition with a traceable quoted span."""
    client = _FakeLayer1Client([_l1_json(
        deontic="OBLIGATION", cross_ref="gift funds",
        precondition={"field_name": "gift_funds_used", "operator": "==", "value": "Yes"},
        span="Were all gift and/or grant fund requirements met?",
    )])
    row = {"row_id": "gift-row", "question_text": "Were all gift and/or grant fund requirements met?",
           "defect_text": "Gift fund documentation is incomplete."}
    result = L1.extract_row(client, row)
    assert result.parse_failed is False
    assert result.condition.field_name == "gift_funds_used"
    assert result.condition.value == "Yes"
    assert result.quoted_span


def test_layer1_no_precondition_for_unconditional_row():
    """Acceptance Scenario 2: a row with no stated/implied precondition
    extracts none."""
    client = _FakeLayer1Client([_l1_json(deontic="OBLIGATION", cross_ref=None, precondition=None)])
    row = {"row_id": "plain-row", "question_text": "Is the note signed?", "defect_text": "Note is unsigned."}
    result = L1.extract_row(client, row)
    assert result.parse_failed is False
    assert result.condition is None


def test_layer1_ambiguous_defaults_to_no_precondition():
    """Acceptance Scenario 3 / T010 / FR-004: genuine ambiguity defaults to
    no precondition, never a guess."""
    client = _FakeLayer1Client([_l1_json(
        deontic="OBLIGATION", cross_ref="some referenced topic", precondition=None,
    )])
    row = {"row_id": "ambiguous-row", "question_text": "x", "defect_text": "vaguely gestures at a topic"}
    result = L1.extract_row(client, row)
    assert result.condition is None
    assert result.parse_failed is False


def test_layer1_malformed_output_retries_then_recovers():
    client = _FakeLayer1Client(["not json at all", "{also not json", _l1_json(deontic="NONE")])
    row = {"row_id": "recovers", "question_text": "x", "defect_text": "y"}
    result = L1.extract_row(client, row, max_retries=2)
    assert result.parse_failed is False
    assert client.call_count == 3


def test_layer1_malformed_output_exhausts_retries_then_parse_failed():
    """SC-007/FR-011 (T017a): permanently malformed output produces an
    explicit `parse_failed` state after retries exhaust -- never a
    silently-guessed default."""
    client = _FakeLayer1Client(["still not json"])
    row = {"row_id": "never-recovers", "question_text": "x", "defect_text": "y"}
    result = L1.extract_row(client, row, max_retries=2)
    assert result.parse_failed is True
    assert result.condition is None
    assert result.error is not None
    assert client.call_count == 3  # 1 initial + 2 retries


# ---------------------------------------------------------------------------
# Layer 2 (fake client + a real, signed, tiny KB corpus)
# ---------------------------------------------------------------------------

@pytest.fixture()
def signed_corpus():
    corpus = KB.build_corpus("retail", [
        {"source_document": "Selling Guide B3-4.3-04", "citation": "B3-4.3-04",
         "content": "Gift funds from a relative require a signed gift letter documenting "
                     "donor relationship, dollar amount, and no repayment expectation."},
    ])
    return KB.sign(corpus, signed_by="kayla", signed_at="2026-07-24")


class _FakeLayer2Client:
    def __init__(self, responses):
        self._responses = list(responses)
        self.call_count = 0

    def converse(self, **kwargs):
        text = self._responses[min(self.call_count, len(self._responses) - 1)]
        self.call_count += 1
        return {"output": {"message": {"content": [{"text": text}]}}}


def test_grounding_verification_accepts_real_excerpt(signed_corpus):
    """SC-003 positive case (T013): a claimed excerpt that genuinely appears
    in the cited section passes verification."""
    section = signed_corpus.sections[0]
    real_excerpt = "Gift funds from a relative require a signed gift letter"
    assert L2.verify_grounding(real_excerpt, section.content) is True


def test_grounding_verification_rejects_fabricated_excerpt(signed_corpus):
    """SC-003 negative case (T014): a claimed excerpt that does NOT actually
    appear in / match the cited section is rejected."""
    section = signed_corpus.sections[0]
    fabricated = "Appraisals must be no older than 90 days prior to closing per XYZ."
    assert L2.verify_grounding(fabricated, section.content) is False


def test_layer2_rejects_unsupported_citation_before_judging(signed_corpus):
    """SC-003 (T014), full flow: the LLM proposes a precondition citing a
    real section id, but the quoted excerpt doesn't actually match that
    section's content -- rejected before judging ever runs."""
    client = _FakeLayer2Client([json.dumps({
        "precondition": {"field_name": "gift_funds_used", "operator": "==", "value": "Yes"},
        "cited_section_id": signed_corpus.sections[0].id,
        "cited_excerpt": "Appraisals must be no older than 90 days -- completely unrelated text",
    })])
    row = {"row_id": "unsupported", "question_text": "Were gift funds used?", "defect_text": "Gift fund documentation is incomplete."}
    result = L2.propose(client, row, signed_corpus)
    assert result.grounding_verified is False
    assert result.condition is None
    assert result.rejected_reason is not None


def test_layer2_supported_citation_proceeds_to_judging(signed_corpus):
    """Acceptance Scenario 1 (T013): a genuinely supported citation passes
    grounding verification and proceeds."""
    section = signed_corpus.sections[0]
    client = _FakeLayer2Client([json.dumps({
        "precondition": {"field_name": "gift_funds_used", "operator": "==", "value": "Yes"},
        "cited_section_id": section.id,
        "cited_excerpt": "Gift funds from a relative require a signed gift letter",
    })])
    row = {"row_id": "supported", "question_text": "Were gift funds used?", "defect_text": "Gift fund documentation is incomplete."}
    result = L2.propose(client, row, signed_corpus, judge_verdicts_fn=lambda cond, r: [])
    assert result.grounding_verified is True
    assert result.condition.field_name == "gift_funds_used"


def test_layer2_never_auto_approves_even_on_unanimous_judges(signed_corpus):
    """SC-004/T016/FR-007: even a unanimous, high-confidence judge panel
    result is overridden to mandatory human review -- the stricter override
    this feature exists to enforce."""
    section = signed_corpus.sections[0]
    client = _FakeLayer2Client([json.dumps({
        "precondition": {"field_name": "gift_funds_used", "operator": "==", "value": "Yes"},
        "cited_section_id": section.id,
        "cited_excerpt": "Gift funds from a relative require a signed gift letter",
    })])
    row = {"row_id": "would-auto-approve", "question_text": "Were gift funds used?", "defect_text": "Gift fund documentation is incomplete."}
    unanimous_confident = lambda cond, r: [  # noqa: E731
        JP.JudgeVerdict(judge_model="mistral", agrees=True, confidence=0.99, reasoning="clear"),
        JP.JudgeVerdict(judge_model="gpt-oss", agrees=True, confidence=0.98, reasoning="clear"),
    ]
    result = L2.propose(client, row, signed_corpus, judge_verdicts_fn=unanimous_confident)
    # Sanity: the panel itself WOULD have auto-approved under 002c's default policy.
    assert JP.escalate_or_approve(unanimous_confident(None, None)) == "AUTO_APPROVED"
    # But Layer 2's override always forces mandatory human review regardless.
    assert result.final_outcome == L2.FORCED_HUMAN_REVIEW_OUTCOME


def test_layer2_malformed_output_exhausts_retries_then_parse_failed(signed_corpus):
    client = _FakeLayer2Client(["not json"])
    row = {"row_id": "l2-never-recovers", "question_text": "Were gift funds used?", "defect_text": "Gift fund documentation is incomplete."}
    result = L2.propose(client, row, signed_corpus, max_retries=2)
    assert result.parse_failed is True
    assert result.condition is None
    assert client.call_count == 3


# ---------------------------------------------------------------------------
# Pipeline sequencing + coverage circuit breaker
# ---------------------------------------------------------------------------

def test_pipeline_layer0_only_never_calls_layer1_or_2():
    """FR-008: rows Layer 0 resolves are never handed to Layer 1/2. Proven
    here by NOT passing layer1_client/layer2_client at all -- pipeline must
    not require them when unresolved rows remain, and must not error."""
    rows = [
        {"row_id": "r1", "question_criteria_by_q": 'QuestionID == 1 && AnswerText == "Yes"'},
        {"row_id": "r2", "question_criteria_by_q": ""},  # unresolved by Layer 0
    ]
    result = pipeline.run_layers(rows)
    assert len(result.proposals) == 1
    assert result.proposals[0].row_id == "r1"
    assert result.proposals[0].source_layer == 0
    assert result.halted_after_layer0 is False


def test_pipeline_resolved_row_not_reprocessed_by_layer1():
    """FR-008: a row Layer 0 resolves must not also reach Layer 1, even when
    a layer1_client IS supplied."""
    call_log = []

    class _CountingClient:
        def converse(self, **kwargs):
            call_log.append(1)
            return {"output": {"message": {"content": [{"text": _l1_json(deontic="NONE")}]}}}

    rows = [{"row_id": "r1", "question_criteria_by_q": 'QuestionID == 1 && AnswerText == "Yes"'}]
    result = pipeline.run_layers(rows, layer1_client=_CountingClient())
    assert len(call_log) == 0
    assert len(result.proposals) == 1
    assert result.proposals[0].source_layer == 0


def test_pipeline_halts_layer1_2_below_coverage_floor():
    """SC-008/T017b/FR-012: a low-structure input set (below the configured
    coverage floor) halts before Layer 1/2 -- proven by a Layer1 client that
    would raise if ever called."""
    class _ExplodingClient:
        def converse(self, **kwargs):
            raise AssertionError("Layer 1 must not be called when below_floor")

    rows = [
        {"row_id": f"r{i}", "question_criteria_by_q": ""}  # zero rows resolvable
        for i in range(10)
    ]
    result = pipeline.run_layers(
        rows, layer1_client=_ExplodingClient(), coverage_floor=0.3,
    )
    assert result.coverage.below_floor is True
    assert result.halted_after_layer0 is True
