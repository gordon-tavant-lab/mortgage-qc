"""
014 -- decision narrative: per-loan explanatory summary layered over an
already-deterministic RunResult, grounded in that RunResult plus the signed
FactVocabulary's guide_citations for exactly the facts this loan's own real
exceptions touch (spec.md FR-001/FR-010, plan.md).

This module (`qc_engine.compiler.decision_narrative`) does not exist yet --
every test below is the TDD red state the downstream LLM-generated
implementation must turn green. No test here makes a live LLM/Bedrock call;
`generate()`'s retry/failure/isolation/temperature tests all inject a fake
client, matching draft_fact_names_llm.py's own mocked-client test pattern.

Written against the CURRENT (2026-07-27, same-day-revised) spec/plan/criteria,
which added vocabulary_version / referenced_guide_citations / FR-010 / SC-006
on top of the original check-id/citation-only validation -- do not mistake an
older, pre-Guide-citation version of this spec for authoritative.
"""
from __future__ import annotations

import pytest

from qc_engine.compiler import fact_vocabulary as FV
from qc_engine.compiler import knowledge_base as KB
from qc_engine.engine import CheckResult, RunResult

# Module under test -- does not exist yet (TDD red state).
from qc_engine.compiler import decision_narrative  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _check_result(check_id, status, field_name="employment_start_date",
                   phase="QC", citation=None, message="", review_reason=None):
    return CheckResult(
        check_id=check_id, check_name=check_id, severity="HIGH", status=status,
        field_name=field_name, phase=phase,
        citation=citation or {"doc": "VOE.pdf", "page": 2, "segment": "start date: 2024-01-15"},
        message=message, review_reason=review_reason,
    )


def _run_result(loan_id="LN-014-001", results=None, ruleset_sha256="a" * 64):
    return RunResult(
        loan_id=loan_id, ruleset_id="t-014", ruleset_version=1,
        ruleset_sha256=ruleset_sha256, engine_version="test",
        results=results or [],
    )


def _canonical_fact(fact_id="employment_start_date", guide_citations=None):
    return FV.CanonicalFact(
        id=fact_id, canonical_field_name=fact_id, data_type="date",
        description="The employment start date the borrower reports on the 1003.",
        guide_citations=guide_citations if guide_citations is not None else [],
    )


def _signed_vocabulary(facts):
    vocab = FV.FactVocabulary(version=7, facts=facts)
    return KB.sign(vocab, signed_by="test-sme", signed_at="2026-07-27T00:00:00Z")


REAL_GUIDE_CITATION = "Fannie Mae Selling Guide B3-3.1-01 (Employment History)"


@pytest.fixture
def clean_loan_result():
    """AUTO_CLEARED: zero exceptions -- still gets a narrative (FR-006)."""
    return _run_result(results=[_check_result("chk-001", "PASS")])


@pytest.fixture
def single_exception_result():
    return _run_result(results=[
        _check_result(
            "chk-employment-001", "FAIL", field_name="employment_start_date",
            message="Employment start date on VOE does not match 1003.",
            review_reason="EXCEPTION",
        ),
    ])


@pytest.fixture
def cited_vocabulary():
    return _signed_vocabulary([
        _canonical_fact("employment_start_date", guide_citations=[REAL_GUIDE_CITATION]),
    ])


@pytest.fixture
def uncited_vocabulary():
    """The fact this loan's exception touches exists but has NO guide_citations
    yet -- a real, current gap the narrative must name honestly (FR-010)."""
    return _signed_vocabulary([
        _canonical_fact("employment_start_date", guide_citations=[]),
    ])


# ---------------------------------------------------------------------------
# T001 -- DecisionNarrative dataclass round-trip
# ---------------------------------------------------------------------------

class TestDecisionNarrativeDataclass:
    def test_round_trip_preserves_every_field_including_vocabulary_and_guide_citations(self):
        narrative = decision_narrative.DecisionNarrative(
            loan_id="LN-014-001", ruleset_sha256="a" * 64, vocabulary_version=7,
            disposition="NEEDS_REVIEW", review_reasons=["EXCEPTION"],
            narrative_text="This loan needs review because...",
            referenced_check_ids=["chk-employment-001"],
            referenced_guide_citations=[REAL_GUIDE_CITATION],
            generated_at="2026-07-27T00:00:00Z", model="anthropic.claude-sonnet",
            validation_attempts=1,
        )
        restored = decision_narrative.DecisionNarrative.from_dict(narrative.to_dict())
        assert restored == narrative
        assert restored.vocabulary_version == 7
        assert restored.referenced_guide_citations == [REAL_GUIDE_CITATION]

    def test_round_trip_with_narrative_text_none_on_exhausted_retries(self):
        narrative = decision_narrative.DecisionNarrative(
            loan_id="LN-014-002", ruleset_sha256="b" * 64, vocabulary_version=7,
            disposition="AUTO_CLEARED", review_reasons=[], narrative_text=None,
            referenced_check_ids=[], referenced_guide_citations=[],
            generated_at="2026-07-27T00:00:00Z", model="anthropic.claude-sonnet",
            validation_attempts=3,
        )
        restored = decision_narrative.DecisionNarrative.from_dict(narrative.to_dict())
        assert restored.narrative_text is None
        assert restored.validation_attempts == 3


# ---------------------------------------------------------------------------
# T002 -- _facts_for_run_result: narrowed set, never the full vocabulary
# ---------------------------------------------------------------------------

class TestFactsForRunResult:
    def test_returns_exactly_the_facts_this_loans_exceptions_touch(self):
        vocab = _signed_vocabulary([
            _canonical_fact("employment_start_date", guide_citations=[REAL_GUIDE_CITATION]),
            _canonical_fact("ltv_ratio", guide_citations=["Fannie Mae Selling Guide B2-1.1-01"]),
            _canonical_fact("flood_zone", guide_citations=[]),
        ])
        result = _run_result(results=[
            _check_result("chk-employment-001", "FAIL", field_name="employment_start_date",
                           review_reason="EXCEPTION"),
            _check_result("chk-ltv-001", "FAIL", field_name="ltv_ratio",
                           review_reason="EXCEPTION"),
        ])
        facts = decision_narrative._facts_for_run_result(result, vocab)
        assert set(facts.keys()) == {"employment_start_date", "ltv_ratio"}
        assert "flood_zone" not in facts

    def test_two_of_sixteen_signed_facts_returns_exactly_those_two(self):
        facts_pool = [
            _canonical_fact(f"fact_{i:02d}", guide_citations=[]) for i in range(16)
        ]
        facts_pool[3] = _canonical_fact("fact_03", guide_citations=["Guide X"])
        facts_pool[9] = _canonical_fact("fact_09", guide_citations=["Guide Y"])
        vocab = _signed_vocabulary(facts_pool)
        result = _run_result(results=[
            _check_result("chk-a", "FAIL", field_name="fact_03", review_reason="EXCEPTION"),
            _check_result("chk-b", "FAIL", field_name="fact_09", review_reason="EXCEPTION"),
        ])
        facts = decision_narrative._facts_for_run_result(result, vocab)
        assert set(facts.keys()) == {"fact_03", "fact_09"}
        assert len(facts) == 2


# ---------------------------------------------------------------------------
# T003 -- _validate: check_id/citation/reason cross-ref + Guide-citation cross-ref
# ---------------------------------------------------------------------------

class TestValidate:
    def test_real_reference_passes(self, single_exception_result, cited_vocabulary):
        text = (
            f"This loan needs review because check chk-employment-001 flagged the "
            f"employment start date (VOE.pdf, page 2), which {REAL_GUIDE_CITATION} requires "
            f"be consistent with the 1003. Review reason: EXCEPTION."
        )
        check_ids, guide_citations = decision_narrative._validate(
            single_exception_result, cited_vocabulary, text)
        assert check_ids == {"chk-employment-001"}
        assert guide_citations == {REAL_GUIDE_CITATION}

    def test_fabricated_check_id_fails(self, single_exception_result, cited_vocabulary):
        text = "This loan needs review because check chk-does-not-exist-999 flagged an issue."
        with pytest.raises(decision_narrative.ValidationError):
            decision_narrative._validate(single_exception_result, cited_vocabulary, text)

    def test_dropped_multi_label_reason_fails(self, cited_vocabulary):
        result = _run_result(results=[
            _check_result("chk-a", "FAIL", field_name="employment_start_date",
                           review_reason="EXCEPTION"),
            _check_result("chk-b", "NEEDS_REVIEW", status="NEEDS_REVIEW",
                           field_name="employment_start_date", review_reason="SOURCE_INCOMPLETE"),
        ])
        # Only mentions chk-a / EXCEPTION -- silently drops SOURCE_INCOMPLETE.
        text = "This loan needs review because check chk-a flagged an issue. Review reason: EXCEPTION."
        with pytest.raises(decision_narrative.ValidationError):
            decision_narrative._validate(result, cited_vocabulary, text)

    def test_over_limit_exceptions_without_explicit_remainder_count_fails(self, cited_vocabulary):
        many_results = [
            _check_result(f"chk-{i:03d}", "FAIL", field_name="employment_start_date",
                           review_reason="EXCEPTION")
            for i in range(15)
        ]
        result = _run_result(results=many_results)
        # Names only 3 of 15 real exceptions, no explicit remainder count.
        text = "Issues found: chk-000, chk-001, chk-002. Review reason: EXCEPTION."
        with pytest.raises(decision_narrative.ValidationError):
            decision_narrative._validate(result, cited_vocabulary, text)

    def test_invented_guide_section_fails(self, single_exception_result, cited_vocabulary):
        text = (
            "This loan needs review because check chk-employment-001 flagged an issue, "
            "per Fannie Mae Selling Guide B9-9.9-99, a section that does not exist. "
            "Review reason: EXCEPTION."
        )
        with pytest.raises(decision_narrative.ValidationError):
            decision_narrative._validate(single_exception_result, cited_vocabulary, text)

    def test_fact_with_no_guide_citations_honestly_flagged_as_uncited_passes(
            self, single_exception_result, uncited_vocabulary):
        text = (
            "This loan needs review because check chk-employment-001 flagged an issue. "
            "No Guide section is attached to this fact yet. Review reason: EXCEPTION."
        )
        check_ids, guide_citations = decision_narrative._validate(
            single_exception_result, uncited_vocabulary, text)
        assert check_ids == {"chk-employment-001"}
        assert guide_citations == set()

    def test_invented_citation_to_fill_an_honest_gap_fails(
            self, single_exception_result, uncited_vocabulary):
        # uncited_vocabulary's fact has NO real guide_citations -- inventing
        # one to "fill the gap" must fail exactly like any other fabrication.
        text = (
            "This loan needs review because check chk-employment-001 flagged an issue, "
            f"per {REAL_GUIDE_CITATION}. Review reason: EXCEPTION."
        )
        with pytest.raises(decision_narrative.ValidationError):
            decision_narrative._validate(single_exception_result, uncited_vocabulary, text)


# ---------------------------------------------------------------------------
# T005/T006 -- generate(): retry/failure path, unsigned-vocabulary guard
# ---------------------------------------------------------------------------

class _FakeBedrockClient:
    """Mimics compile_llm._client()'s .converse(...) call shape."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def converse(self, **kwargs):
        self.calls.append(kwargs)
        text = self._responses.pop(0)
        return {"output": {"message": {"content": [{"text": text}]}}}


class TestGenerate:
    def test_valid_first_try(self, single_exception_result, cited_vocabulary):
        valid_text = (
            f"This loan needs review because check chk-employment-001 flagged the employment "
            f"start date, per {REAL_GUIDE_CITATION}. Review reason: EXCEPTION."
        )
        client = _FakeBedrockClient([valid_text])
        narrative = decision_narrative.generate(
            single_exception_result, cited_vocabulary, client, max_retries=2)
        assert narrative.narrative_text == valid_text
        assert narrative.validation_attempts == 1
        assert narrative.vocabulary_version == cited_vocabulary.version

    def test_valid_on_retry(self, single_exception_result, cited_vocabulary):
        invalid_text = "This references check chk-fabricated-000, which does not exist."
        valid_text = (
            f"This loan needs review because check chk-employment-001 flagged the employment "
            f"start date, per {REAL_GUIDE_CITATION}. Review reason: EXCEPTION."
        )
        client = _FakeBedrockClient([invalid_text, valid_text])
        narrative = decision_narrative.generate(
            single_exception_result, cited_vocabulary, client, max_retries=2)
        assert narrative.narrative_text == valid_text
        assert narrative.validation_attempts == 2

    def test_exhausted_retries_ships_null_never_raises(self, single_exception_result, cited_vocabulary):
        always_invalid = "This references check chk-fabricated-000, which does not exist."
        client = _FakeBedrockClient([always_invalid] * 10)
        narrative = decision_narrative.generate(
            single_exception_result, cited_vocabulary, client, max_retries=2)
        assert narrative.narrative_text is None
        assert narrative.validation_attempts == 3  # max_retries + 1

    def test_unsigned_vocabulary_raises_before_any_model_call(self, single_exception_result):
        unsigned = FV.FactVocabulary(
            version=7, facts=[_canonical_fact("employment_start_date")])
        client = _FakeBedrockClient(["should never be reached"])
        with pytest.raises(FV.VocabularyNotSignedError):
            decision_narrative.generate(single_exception_result, unsigned, client)
        assert client.calls == []

    def test_zero_exception_auto_cleared_loan_still_gets_a_narrative(
            self, clean_loan_result, cited_vocabulary):
        # FR-006: AUTO_CLEARED loans get a short, honest narrative -- not skipped.
        text = "This loan is AUTO_CLEARED: every check passed, no exceptions found."
        client = _FakeBedrockClient([text])
        narrative = decision_narrative.generate(
            clean_loan_result, cited_vocabulary, client, max_retries=2)
        assert narrative.narrative_text == text
        assert narrative.referenced_check_ids == set() or narrative.referenced_check_ids == []


# ---------------------------------------------------------------------------
# FR-001 -- isolation: only THIS loan's RunResult + narrowed vocabulary lookup
# ---------------------------------------------------------------------------

class TestIsolation:
    def test_prompt_contains_no_other_loan_id_and_no_full_ruleset_internals(
            self, single_exception_result, cited_vocabulary):
        client = _FakeBedrockClient([
            f"This loan needs review because check chk-employment-001 flagged an issue, "
            f"per {REAL_GUIDE_CITATION}. Review reason: EXCEPTION."
        ])
        decision_narrative.generate(single_exception_result, cited_vocabulary, client, max_retries=2)
        assert len(client.calls) == 1
        sent_payload = str(client.calls[0])
        assert "LN-014-999-OTHER-LOAN" not in sent_payload
        assert single_exception_result.loan_id in sent_payload

    def test_narrowed_vocabulary_lookup_excludes_facts_this_loan_never_touched(
            self, single_exception_result):
        vocab = _signed_vocabulary([
            _canonical_fact("employment_start_date", guide_citations=[REAL_GUIDE_CITATION]),
            _canonical_fact("unrelated_fact", guide_citations=["Should never be sent to the model"]),
        ])
        client = _FakeBedrockClient([
            f"This loan needs review because check chk-employment-001 flagged an issue, "
            f"per {REAL_GUIDE_CITATION}. Review reason: EXCEPTION."
        ])
        decision_narrative.generate(single_exception_result, vocab, client, max_retries=2)
        sent_payload = str(client.calls[0])
        assert "Should never be sent to the model" not in sent_payload


# ---------------------------------------------------------------------------
# FR-004 -- temperature=0
# ---------------------------------------------------------------------------

class TestTemperatureZero:
    def test_generate_calls_the_model_at_temperature_zero(
            self, single_exception_result, cited_vocabulary):
        client = _FakeBedrockClient([
            f"This loan needs review because check chk-employment-001 flagged an issue, "
            f"per {REAL_GUIDE_CITATION}. Review reason: EXCEPTION."
        ])
        decision_narrative.generate(single_exception_result, cited_vocabulary, client, max_retries=2)
        assert len(client.calls) == 1
        call_kwargs = client.calls[0]
        inference_config = call_kwargs.get("inferenceConfig", {})
        assert inference_config.get("temperature") == 0


# ---------------------------------------------------------------------------
# FR-002 / Edge Case -- each generate() call stamps its own ruleset_sha256
# ---------------------------------------------------------------------------

class TestRulesetShaStamping:
    def test_narrative_stamps_the_run_results_own_ruleset_sha256_not_a_stale_value(
            self, cited_vocabulary):
        text = (
            f"This loan needs review because check chk-employment-001 flagged an issue, "
            f"per {REAL_GUIDE_CITATION}. Review reason: EXCEPTION."
        )
        result_a = _run_result(loan_id="LN-A", ruleset_sha256="a" * 64, results=[
            _check_result("chk-employment-001", "FAIL", review_reason="EXCEPTION"),
        ])
        result_b = _run_result(loan_id="LN-B", ruleset_sha256="c" * 64, results=[
            _check_result("chk-employment-001", "FAIL", review_reason="EXCEPTION"),
        ])
        client_a = _FakeBedrockClient([text])
        client_b = _FakeBedrockClient([text])
        narrative_a = decision_narrative.generate(result_a, cited_vocabulary, client_a, max_retries=2)
        narrative_b = decision_narrative.generate(result_b, cited_vocabulary, client_b, max_retries=2)
        assert narrative_a.ruleset_sha256 == "a" * 64
        assert narrative_b.ruleset_sha256 == "c" * 64


# ---------------------------------------------------------------------------
# FR-005 -- decision_narrative is a leaf, output-only module: no core engine
# module imports it (structural test, no engine changes required to run it).
# ---------------------------------------------------------------------------

class TestLeafModuleStructure:
    def test_no_core_engine_module_imports_decision_narrative(self):
        import pathlib
        engine_dir = pathlib.Path(__file__).resolve().parents[1] / "qc_engine"
        offenders = []
        for path in engine_dir.glob("*.py"):
            if path.name == "decision_narrative.py":
                continue
            text = path.read_text()
            if "decision_narrative" in text:
                offenders.append(str(path))
        assert offenders == [], (
            f"decision_narrative must stay a leaf/output-only artifact (FR-005) -- "
            f"unexpectedly referenced by: {offenders}"
        )


# ---------------------------------------------------------------------------
# Acceptance Scenarios 1-3 (content shape) -- exercised via _validate() only,
# since content shape is a real-model property beyond deterministic unit
# testing; these confirm the validator accepts/rejects the documented shapes.
# ---------------------------------------------------------------------------

class TestAcceptanceScenarioShapes:
    def test_scenario_1_auto_cleared_loan_narrative_names_no_invented_concern(
            self, clean_loan_result, cited_vocabulary):
        honest_text = "AUTO_CLEARED: every check passed. No exceptions or concerns found."
        check_ids, _ = decision_narrative._validate(clean_loan_result, cited_vocabulary, honest_text)
        assert check_ids == set()

    def test_scenario_2_single_exception_names_check_citation_and_reason(
            self, single_exception_result, cited_vocabulary):
        text = (
            f"Needs review: check chk-employment-001 (VOE.pdf, page 2) shows a mismatched "
            f"employment start date, per {REAL_GUIDE_CITATION}. Review reason: EXCEPTION."
        )
        check_ids, guide_citations = decision_narrative._validate(
            single_exception_result, cited_vocabulary, text)
        assert "chk-employment-001" in check_ids
        assert REAL_GUIDE_CITATION in guide_citations

    def test_scenario_3_multiple_review_reasons_addressed_separately_not_collapsed(
            self, cited_vocabulary):
        result = _run_result(results=[
            _check_result("chk-a", "FAIL", field_name="employment_start_date",
                           review_reason="EXCEPTION"),
            _check_result("chk-b", "NEEDS_REVIEW", status="NEEDS_REVIEW",
                           field_name="employment_start_date", review_reason="SOURCE_INCOMPLETE"),
        ])
        text = (
            "This loan needs review for two distinct reasons: (1) check chk-a is an "
            f"EXCEPTION per {REAL_GUIDE_CITATION}; and (2) check chk-b needs review because "
            "SOURCE_INCOMPLETE -- the underlying document was not fully legible."
        )
        check_ids, _ = decision_narrative._validate(result, cited_vocabulary, text)
        assert {"chk-a", "chk-b"} <= check_ids
