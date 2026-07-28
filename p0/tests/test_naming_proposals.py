"""Naming proposals (LLM-drafted, MEDIUM tier): structural guards on the
shipped review artifact -- NOT content pins (the artifact is model output;
its guarantee is process discipline, not byte determinism)."""
import json
import os
import sys

_P0 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_REPO_ROOT = os.path.dirname(_P0)
if _P0 not in sys.path:
    sys.path.insert(0, _P0)

from qc_engine.compiler import fact_vocabulary as FV  # noqa: E402

PROPOSALS = os.path.join(_REPO_ROOT, "storage", "fact_vocabulary", "candidates",
                         "naming_proposals_v1.json")
CANDIDATES = os.path.join(_REPO_ROOT, "storage", "fact_vocabulary", "candidates",
                          "v1.json")
VOCAB_DIR = os.path.join(_REPO_ROOT, "storage", "fact_vocabulary")


def _load():
    with open(PROPOSALS) as f:
        return json.load(f)


def test_artifact_is_marked_review_tier_and_consumed_by_nothing():
    d = _load()
    assert d["trust_tier"] == "MEDIUM_SME_REVIEW"
    assert "consumed by NOTHING" in d["note"]


def test_every_real_answer_is_mapped_or_abstained_never_dropped():
    """The per-call validation, re-verified against the shipped artifact:
    for each question, mapped + abstained + already-bound == the real answer
    vocabulary from the candidates artifact. No silent gaps, no invented
    answer strings."""
    with open(CANDIDATES) as f:
        by_key = {c["question_key"]: c for c in json.load(f)["candidates"]}
    d = _load()
    assert d["proposals"], "expected at least one proposal"
    for p in d["proposals"]:
        cand = by_key[p["question_key"]]
        real = set(cand["answer_vocabulary"])
        accounted = set(p["already_bound_answers"])
        for fact in p["llm_proposal"]["facts"]:
            accounted |= set(fact["answer_value_map"])
        accounted |= set(p["llm_proposal"].get("unmapped_answers", {}))
        assert accounted == real, (p["question_key"],
                                    sorted(real - accounted),
                                    sorted(accounted - real))


def test_drafting_proposals_alone_never_touches_the_vocabulary():
    """The original load-bearing boundary: DRAFTING proposals (this file's
    concern) must never itself mutate the signed vocabulary -- promotion is
    a separate, explicit, human-directed step (promote_naming_proposals.py,
    2026-07-27), not a side effect of the LLM naming pass. Re-verified here
    by checking naming_proposals_v1.json's own disclosure, since re-running
    the drafting LLM call isn't something a test should do."""
    d = _load()
    assert "consumed by NOTHING" in d["note"]


def test_promoted_vocabulary_still_carries_the_honest_placeholder_signature():
    """2026-07-27: Gordon explicitly directed promoting all 24 candidates'
    proposals into the real vocabulary (promote_naming_proposals.py ->
    build_vocabulary_guide_citations.py), so the vocabulary is no longer
    gift-only. The invariant that must still hold: promotion is NOT the same
    as SME review -- signed_by stays the same honest placeholder no matter
    how many facts get promoted, and every promoted fact discloses its
    LLM-drafted, not-yet-reviewed origin via promotion_note."""
    vocab = FV.load_latest(VOCAB_DIR)
    assert vocab.version >= 6
    # 17 promoted, then loan_product_type removed (2026-07-27, Gordon's call:
    # a Freddie Mac fact with no Freddie Mac corpus to ever cite it from --
    # see remove_out_of_scope_fact.py) -- 16 is the current honest count.
    assert len(vocab.facts) >= 16
    assert vocab.signed_by == "NOT-A-REAL-SME-pending-kayla-review"
    names = {f.canonical_field_name for f in vocab.facts}
    assert "gift_funds_used" in names
    promoted = [f for f in vocab.facts if f.canonical_field_name != "gift_funds_used"]
    assert promoted, "expected facts promoted beyond the original gift fact"
    for fact in promoted:
        assert fact.promotion_note, f"{fact.canonical_field_name} missing promotion_note"
        assert "NOT yet reviewed" in fact.promotion_note
