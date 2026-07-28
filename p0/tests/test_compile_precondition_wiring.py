"""002g -- compile-time precondition wiring: 002f's pipeline output resolved
through the signed vocabulary into compiled checks' `applies_if`.

SC-001's entire path runs against REAL Retail rows with ZERO LLM calls (the
real gift rows are Layer-0 rows -- question 570606); the fake Layer-1 client
below exercises the never-auto-attach trust-tier policy without any network.
"""
import json
import os
import sys

_P0 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _P0 not in sys.path:
    sys.path.insert(0, _P0)
_FROM_DOCS = os.path.join(_P0, "fixtures", "from_docs")
if _FROM_DOCS not in sys.path:
    sys.path.insert(0, _FROM_DOCS)

from fixture_loader import load_canonical_loan  # noqa: E402
from qc_engine.compiler import compile_llm  # noqa: E402
from qc_engine.compiler import fact_vocabulary as FV  # noqa: E402
from qc_engine.compiler import knowledge_base as KB  # noqa: E402
from qc_engine.engine import run  # noqa: E402
from qc_engine.model import SourceValue  # noqa: E402
from qc_engine.ruleset import Check, Ruleset  # noqa: E402

ROWS_PATH = os.path.join(_P0, "fixtures", "ontology_extraction",
                         "retail_post_closing_rows.json")
LOAN_01_FIXTURE = os.path.join(_FROM_DOCS, "loan_01.json")

# Real data shape (verified 2026-07-26): only 00161 gates on "Yes - Gift"
# alone; 00099/00146 gate on "Yes - Gift" OR "Yes - Grant", and v1's
# vocabulary deliberately binds only Gift ("Yes - Grant" needs its own
# SME-reviewed fact) -- so those two rows exercise the REAL refusal path.
GIFT_ONLY_ROW_IDS = ("pc-retail-00161",)
GIFT_OR_GRANT_ROW_IDS = ("pc-retail-00099", "pc-retail-00146")


def _rows_by_ids(ids):
    with open(ROWS_PATH) as f:
        rows = json.load(f)
    return [r for r in rows if r["row_id"] in ids]


def _gift_check(row_id: str) -> Check:
    return Check(
        id=f"chk-{row_id}", name=f"Gift check for {row_id}",
        field_name="gift_funds_source_documented", kind="predicate",
        severity="CRITICAL", predicate="is_true",
        message_pass="Gift documentation complete.",
        message_fail="Gift documentation incomplete.",
    )


def _drafts_for(rows):
    return [compile_llm.CompiledCheckDraft(
        row_id=r["row_id"], check=_gift_check(r["row_id"]),
        source_text=r["defect_text"], extracted_intent="gift documentation",
    ) for r in rows]


def _vocab():
    repo_root = os.path.dirname(_P0)
    return FV.load(os.path.join(repo_root, "storage", "fact_vocabulary", "v1.json"))


def _ruleset(checks):
    return Ruleset(ruleset_id="rs-002g-test", version=1, checks=checks)


# --- FR-001/SC-001: real rows, real Layer 0, zero LLM ------------------------

def test_real_gift_only_row_gets_applies_if_from_real_layer0():
    rows = _rows_by_ids(GIFT_ONLY_ROW_IDS)
    assert len(rows) == 1
    drafts = _drafts_for(rows)
    report = compile_llm.attach_preconditions(drafts, rows, _vocab())
    assert report.rows_attempted == 1
    d = drafts[0]
    assert d.check.applies_if is not None
    conds = {c["field_name"]: c for c in d.check.applies_if}
    assert conds["gift_funds_used"]["operator"] == "=="
    assert conds["gift_funds_used"]["value"] == "true"
    assert "fact-gift-funds-used" in d.applies_if_provenance
    assert report.attached == 1


def test_real_gift_or_grant_rows_refuse_because_grant_is_unbound():
    """FR-002 on REAL rows: 00099/00146 gate on Gift OR Grant; v1 binds only
    Gift, so resolution must refuse (never guess that Grant means gift) --
    the row compiles unconditionally and is flagged for SME review. This is
    the designed workflow for extending the vocabulary, not a failure."""
    rows = _rows_by_ids(GIFT_OR_GRANT_ROW_IDS)
    assert len(rows) == 2
    drafts = _drafts_for(rows)
    report = compile_llm.attach_preconditions(drafts, rows, _vocab())
    for d in drafts:
        assert d.check.applies_if is None
        assert "Yes - Grant" in d.applies_if_review
    assert report.flagged_for_review == 2


def test_sc001_real_loan_01_resolves_not_applicable_via_wired_check():
    """The full 002g promise on real data: real AMQ row -> real Layer-0
    cluster -> signed vocabulary -> compiled applies_if -> real loan 01
    fixture (no gift funds) -> NOT_APPLICABLE. Zero LLM calls anywhere."""
    rows = _rows_by_ids(GIFT_ONLY_ROW_IDS)
    drafts = _drafts_for(rows)
    compile_llm.attach_preconditions(drafts, rows, _vocab())

    loan = load_canonical_loan(LOAN_01_FIXTURE)
    assert loan.facts.get("doc_present_gift_letter") == "false"  # really loan 01
    loan.fields["gift_funds_used"] = SourceValue(doc="false")

    ruleset = _ruleset([d.check for d in drafts])
    result = run(loan, ruleset)
    assert len(result.results) == 1
    res = result.results[0]
    assert res.status == "NOT_APPLICABLE", (res.check_id, res.status, res.message)
    assert "gift_funds_used" in res.message


def test_gift_using_loan_still_evaluates_the_check():
    """The inverse guard: a loan that DID use gift funds must not be skipped
    -- the gate passes through to normal kind-dispatch."""
    rows = _rows_by_ids(GIFT_ONLY_ROW_IDS)
    drafts = _drafts_for(rows)
    compile_llm.attach_preconditions(drafts, rows, _vocab())
    loan = load_canonical_loan(LOAN_01_FIXTURE)
    loan.fields["gift_funds_used"] = SourceValue(doc="true")
    loan.fields["gift_funds_source_documented"] = SourceValue(doc=True)
    ruleset = _ruleset([d.check for d in drafts])
    for res in run(loan, ruleset).results:
        assert res.status == "PASS"


# --- FR-005: same canonical field -> identical gate outcome -------------------

def test_two_checks_on_same_canonical_field_evaluate_identically():
    rows = _rows_by_ids(GIFT_ONLY_ROW_IDS)
    drafts = _drafts_for(rows)
    compile_llm.attach_preconditions(drafts, rows, _vocab())
    wired = drafts[0].check
    sibling = _gift_check("sibling-row")
    sibling.applies_if = [dict(c) for c in wired.applies_if]  # same canonical fact
    loan = load_canonical_loan(LOAN_01_FIXTURE)
    loan.fields["gift_funds_used"] = SourceValue(doc="false")
    statuses = {r.status for r in run(loan, _ruleset([wired, sibling])).results}
    assert statuses == {"NOT_APPLICABLE"}  # never disagree about the same loan


# --- FR-002 refusal paths -----------------------------------------------------

def test_unmapped_answer_flags_draft_and_attaches_nothing():
    """A row gated on a 570606 answer the vocabulary doesn't bind (e.g.
    'Yes - Retirement') must compile WITHOUT applies_if and carry a review
    flag -- never a guessed gate."""
    with open(ROWS_PATH) as f:
        all_rows = json.load(f)
    retirement_rows = [
        r for r in all_rows
        if "Yes - Retirement" in (r.get("question_criteria_by_q") or "")
        and "Yes - Gift" not in (r.get("question_criteria_by_q") or "")
    ]
    assert retirement_rows, "expected real retirement-gated rows in the sheet"
    rows = retirement_rows[:2]
    drafts = _drafts_for(rows)
    report = compile_llm.attach_preconditions(drafts, rows, _vocab())
    for d in drafts:
        assert d.check.applies_if is None
        assert d.applies_if_review is not None
        assert "unresolved" in d.applies_if_review
    assert report.flagged_for_review >= len(rows)


def test_unsigned_vocabulary_fails_loudly_not_silently():
    import pytest
    rows = _rows_by_ids(GIFT_ONLY_ROW_IDS)
    drafts = _drafts_for(rows)
    unsigned = FV.FactVocabulary(version=99, facts=_vocab().facts)
    with pytest.raises(FV.VocabularyNotSignedError):
        compile_llm.attach_preconditions(drafts, rows, unsigned)


# --- Trust tiers: Layer 1 is never auto-attached ------------------------------

class _FakeLayer1Client:
    """Deterministic stand-in for Bedrock: returns a well-formed Layer-1
    response proposing a NOVEL field name. No network, no LLM (FR-009)."""
    def converse(self, **kwargs):
        text = json.dumps({
            "deontic_modality": "OBLIGATION",
            "cross_reference_target": None,
            "precondition": {"field_name": "co_borrower_present",
                            "operator": "==", "value": "true"},
            "quoted_span": "when a co-borrower is present",
        })
        return {"output": {"message": {"content": [{"text": text}]}}}


def test_layer1_proposal_is_flagged_never_auto_attached_and_novel_name_surfaces():
    row = {"row_id": "synthetic-l1-row", "question_text": "Is the co-borrower documented?",
           "defect_text": "Co-borrower documentation missing when a co-borrower is present",
           "question_criteria_by_q": None}
    drafts = _drafts_for([row])
    report = compile_llm.attach_preconditions(
        drafts, [row], _vocab(), layer1_client=_FakeLayer1Client())
    d = drafts[0]
    assert d.check.applies_if is None          # never auto-attached
    assert "MEDIUM_SME_REVIEW" in d.applies_if_review
    assert report.novel_fact_candidates == ["co_borrower_present"]  # surfaced for review
