"""002g -- canonical-fact vocabulary: sign-gating, resolution, persistence,
and the citation-only concept index. Zero LLM calls anywhere (FR-009)."""
import os
import sys

import pytest

_P0 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _P0 not in sys.path:
    sys.path.insert(0, _P0)

from qc_engine.compiler import fact_vocabulary as FV  # noqa: E402
from qc_engine.compiler import knowledge_base as KB  # noqa: E402
from ontology_extraction.pipeline import PreconditionCondition, PreconditionProposal  # noqa: E402


def _gift_fact():
    return FV.CanonicalFact(
        id="fact-gift", canonical_field_name="gift_funds_used",
        data_type="boolean", description="Gift funds used on the loan.",
        name_synonyms=["gift_proceeds_present"],
        question_bindings=[FV.QuestionBinding(
            question_key="570606", answers=["Yes - Gift"], canonical_value="true")],
    )


def _signed_vocab(facts=None):
    vocab = FV.FactVocabulary(version=1, facts=facts or [_gift_fact()])
    return KB.sign(vocab, signed_by="test-sme", signed_at="2026-07-26")


def _layer0_proposal(field_name="question_570606", operator="==", value="Yes - Gift"):
    return PreconditionProposal(
        row_id="row-1", source_layer=0,
        condition=PreconditionCondition(field_name=field_name, operator=operator, value=value),
        provenance="ontology key 570606", trust_tier="HIGH_AUTO_ELIGIBLE",
    )


# --- US3: no sign-off, no use -------------------------------------------------

def test_unsigned_vocabulary_refuses_resolution():
    vocab = FV.FactVocabulary(version=1, facts=[_gift_fact()])  # unsigned
    with pytest.raises(FV.VocabularyNotSignedError):
        FV.resolve_layer0(vocab, _layer0_proposal())
    with pytest.raises(FV.VocabularyNotSignedError):
        FV.resolve_field_name(vocab, "gift_funds_used")


def test_kb_sign_and_is_usable_are_reused_not_reimplemented():
    """T001: the KB's own sign()/is_usable() work on a FactVocabulary --
    sign-off logic exists once (spec Key Entities)."""
    vocab = FV.FactVocabulary(version=1, facts=[])
    assert not KB.is_usable(vocab)
    signed = KB.sign(vocab, signed_by="s", signed_at="2026-07-26")
    assert KB.is_usable(signed)
    assert not KB.is_usable(vocab)  # original untouched (no mutation)


# --- FR-002: Layer-0 resolution ----------------------------------------------

def test_layer0_gift_proposal_resolves_to_canonical_condition():
    res = FV.resolve_layer0(_signed_vocab(), _layer0_proposal())
    assert res.status == "resolved"
    assert res.condition == {"field_name": "gift_funds_used",
                             "operator": "==", "value": "true"}
    assert res.fact_id == "fact-gift"


def test_layer0_unmapped_answer_refuses_never_guesses():
    proposal = _layer0_proposal(operator="in",
                                value=["Yes - Gift", "Yes - Checking/Savings"])
    res = FV.resolve_layer0(_signed_vocab(), proposal)
    assert res.status == "unresolved"
    assert "Yes - Checking/Savings" in res.reason


def test_layer0_answers_spanning_two_facts_refuse():
    grant_fact = FV.CanonicalFact(
        id="fact-grant", canonical_field_name="grant_funds_used",
        data_type="boolean", description="Grant funds used.",
        question_bindings=[FV.QuestionBinding(
            question_key="570606", answers=["Yes - Grant"], canonical_value="true")],
    )
    vocab = _signed_vocab(facts=[_gift_fact(), grant_fact])
    proposal = _layer0_proposal(operator="in", value=["Yes - Gift", "Yes - Grant"])
    res = FV.resolve_layer0(vocab, proposal)
    assert res.status == "unresolved"
    assert "span two facts" in res.reason


def test_layer0_multiple_answers_same_value_collapse_to_equality():
    fact = _gift_fact()
    fact.question_bindings[0].answers = ["Yes - Gift", "Yes- Gift"]
    res = FV.resolve_layer0(
        _signed_vocab(facts=[fact]),
        _layer0_proposal(operator="in", value=["Yes - Gift", "Yes- Gift"]))
    assert res.status == "resolved"
    assert res.condition["operator"] == "=="
    assert res.condition["value"] == "true"


# --- SC-002: name resolution (Layer-1 dedup axis) ----------------------------

def test_exact_name_reuses_canonical_fact():
    res = FV.resolve_field_name(_signed_vocab(), "gift_funds_used")
    assert res.status == "resolved" and res.fact_id == "fact-gift"


def test_synonym_resolves_to_same_canonical_name():
    res = FV.resolve_field_name(_signed_vocab(), "gift_proceeds_present")
    assert res.status == "resolved"
    assert res.condition["field_name"] == "gift_funds_used"
    assert res.fact_id == "fact-gift"


def test_novel_name_surfaces_as_candidate_never_added():
    vocab = _signed_vocab()
    before = len(vocab.facts)
    res = FV.resolve_field_name(vocab, "co_borrower_present")
    assert res.status == "novel_candidate"
    assert res.reason == "co_borrower_present"
    assert len(vocab.facts) == before  # nothing silently added


# --- Persistence -------------------------------------------------------------

def test_save_load_roundtrip_preserves_everything(tmp_path):
    vocab = _signed_vocab()
    path = str(tmp_path / "fact_vocabulary" / "v1.json")
    FV.save(vocab, path)
    loaded = FV.load(path)
    assert loaded.version == 1
    assert loaded.signed_by == "test-sme"
    fact = loaded.facts[0]
    assert fact.canonical_field_name == "gift_funds_used"
    assert fact.question_bindings[0].answers == ["Yes - Gift"]
    assert FV.resolve_layer0(loaded, _layer0_proposal()).status == "resolved"


def test_real_seed_artifact_loads_and_resolves():
    """criteria.md #7: the shipped v1 artifact is real, derives from the real
    570606 cluster, carries the honest placeholder signature, and resolves
    the real gift proposal shape."""
    repo_root = os.path.dirname(_P0)
    path = os.path.join(repo_root, "storage", "fact_vocabulary", "v1.json")
    vocab = FV.load(path)
    assert vocab.signed_by == "NOT-A-REAL-SME-pending-kayla-review"
    res = FV.resolve_layer0(vocab, _layer0_proposal())
    assert res.status == "resolved"
    assert res.condition["field_name"] == "gift_funds_used"


# --- Concept index (citation-only) -------------------------------------------

def _tiny_corpus(signed=True):
    corpus = KB.build_corpus("Fannie Mae", [
        {"source_document": "Selling Guide", "citation": "B3-4.3-04, Personal Gifts",
         "content": "Gift funds from an acceptable donor may be used. A gift letter is required."},
        {"source_document": "Selling Guide", "citation": "B3-4.1-01, Minimum Reserves",
         "content": "Reserves are measured in months of the full monthly payment amount."},
    ])
    if signed:
        corpus = KB.sign(corpus, signed_by="test-sme", signed_at="2026-07-26")
    return corpus


def test_attach_guide_citations_stores_citation_strings_only():
    vocab = _signed_vocab()
    enriched = FV.attach_guide_citations(vocab, _tiny_corpus(), top_n=1)
    cited = enriched.facts[0].guide_citations
    assert cited == ["B3-4.3-04, Personal Gifts"]
    # pointers only -- the section CONTENT never lands on the fact
    assert all("gift letter" not in c.lower() for c in cited)
    assert vocab.facts[0].guide_citations == []  # input not mutated


def test_attach_guide_citations_refuses_unsigned_corpus():
    with pytest.raises(KB.CorpusNotSignedError):
        FV.attach_guide_citations(_signed_vocab(), _tiny_corpus(signed=False))


# --- load_latest ---------------------------------------------------------

def test_load_latest_picks_highest_version(tmp_path):
    dir_path = str(tmp_path / "fact_vocabulary")
    FV.save(FV.FactVocabulary(version=1, facts=[_gift_fact()]),
            os.path.join(dir_path, "v1.json"))
    FV.save(FV.FactVocabulary(version=2, facts=[]),
            os.path.join(dir_path, "v2.json"))
    FV.save(FV.FactVocabulary(version=10, facts=[]),
            os.path.join(dir_path, "v10.json"))
    loaded = FV.load_latest(dir_path)
    assert loaded.version == 10  # not lexicographic ("v2" > "v10" as strings)


def test_load_latest_raises_when_dir_has_no_versions(tmp_path):
    dir_path = str(tmp_path / "empty_fact_vocabulary")
    os.makedirs(dir_path)
    with pytest.raises(FileNotFoundError):
        FV.load_latest(dir_path)


# --- real v2 artifact (build_vocabulary_guide_citations.py output) -------

def test_real_v2_artifact_loads_with_gift_fact_guide_citations():
    """The shipped v2 artifact (built by
    build_vocabulary_guide_citations.py against the real signed Fannie Mae
    KB corpus) carries the ACTUAL Guide section that defines gift funds --
    not just any non-empty citation. A same-day bug (caught by direct
    verification against the real corpus, not assumed fixed) had v2 citing
    Rental Income / Appraisal Report sections instead: the seed fact's
    description mixed AMQ-provenance detail into the retrieval query text,
    diluting it enough that the real defining section (B3-4.3-04, Personal
    Gifts) ranked 6th, not top-3. Fixed via a disclosed description
    override in build_vocabulary_guide_citations.py (DESCRIPTION_OVERRIDES)
    -- this test guards against that regressing silently."""
    repo_root = os.path.dirname(_P0)
    path = os.path.join(repo_root, "storage", "fact_vocabulary", "v2.json")
    vocab = FV.load(path)
    assert vocab.version == 2
    assert vocab.signed_by == "NOT-A-REAL-SME-pending-kayla-review"
    gift = next(f for f in vocab.facts if f.canonical_field_name == "gift_funds_used")
    assert len(gift.guide_citations) > 0
    assert all(isinstance(c, str) and c.strip() for c in gift.guide_citations)
    assert any("Personal Gifts" in c for c in gift.guide_citations), (
        f"expected the real 'Personal Gifts' section among the top citations, "
        f"got: {gift.guide_citations!r}")


# --- real v4 artifact (17 facts: gift + 16 promoted, build_vocabulary_guide_citations.py) ---

def test_real_v4_artifact_has_all_promoted_facts_with_disclosed_provenance():
    """2026-07-27: promote_naming_proposals.py + build_vocabulary_guide_citations.py
    expanded the vocabulary from 1 fact (gift) to 17. Every promoted fact must
    disclose its LLM-drafted, not-yet-SME-reviewed origin -- promotion is not
    a substitute for real sign-off."""
    repo_root = os.path.dirname(_P0)
    path = os.path.join(repo_root, "storage", "fact_vocabulary", "v4.json")
    vocab = FV.load(path)
    assert vocab.version == 4
    assert vocab.signed_by == "NOT-A-REAL-SME-pending-kayla-review"
    assert len(vocab.facts) == 17
    promoted = [f for f in vocab.facts if f.canonical_field_name != "gift_funds_used"]
    assert len(promoted) == 16
    for fact in promoted:
        assert fact.promotion_note and "NOT yet reviewed" in fact.promotion_note


def test_real_v4_electronic_closing_fact_cites_the_real_defining_section():
    """Guards the second disclosed citation-quality fix (2026-07-27):
    electronic_closing_used's description-only query ranked the real
    defining section (A2-4.1-03, Electronic Records, Signatures, and
    Transactions) 5th, outside top_n=3 -- folding in the fact's own
    dependent question texts (discover_fact_candidates.py's signal) fixed
    this, verified directly against the real corpus, not assumed."""
    repo_root = os.path.dirname(_P0)
    path = os.path.join(repo_root, "storage", "fact_vocabulary", "v4.json")
    vocab = FV.load(path)
    fact = next(f for f in vocab.facts if f.canonical_field_name == "electronic_closing_used")
    assert any("Electronic Records, Signatures" in c for c in fact.guide_citations), (
        f"expected the real defining section among top citations, got: {fact.guide_citations!r}")


def test_real_v4_lep_fact_honestly_ships_with_no_citation_not_a_wrong_one():
    """The corpus has no section on Limited English Proficiency requirements
    (verified by eye against every candidate section) -- rather than ship a
    plausible-looking wrong citation, this fact ships empty with an explicit
    disclosure, per Non-Negotiable #1 (honest gap beats confident invention)."""
    repo_root = os.path.dirname(_P0)
    path = os.path.join(repo_root, "storage", "fact_vocabulary", "v4.json")
    vocab = FV.load(path)
    fact = next(f for f in vocab.facts if f.canonical_field_name == "lep_requirements_met")
    assert fact.guide_citations == []
    assert "No confident Guide-section match" in fact.promotion_note


def test_real_v5_loan_product_type_refuses_cross_investor_citation():
    """Guards the third disclosed fix (2026-07-27, caught by a /g-os-judge
    review of v4): loan_product_type's own description says it's a Freddie
    Mac fact (real trademarked programs -- CHOICERenovation, GreenCHOICE --
    confirmed in its source questions), but v4 shipped it with 3 Fannie Mae
    Selling Guide citations because that's the only corpus ingested (checked
    directly: no Freddie Mac corpus exists). v5's investor-mismatch guard
    must refuse citations for this fact outright, no matter what retrieval
    would return, since the wrong Guide entirely was searched."""
    repo_root = os.path.dirname(_P0)
    path = os.path.join(repo_root, "storage", "fact_vocabulary", "v5.json")
    vocab = FV.load(path)
    assert vocab.version == 5
    fact = next(f for f in vocab.facts if f.canonical_field_name == "loan_product_type")
    assert fact.guide_citations == []
    assert "names an investor/GSE other than" in fact.promotion_note


def test_real_v5_other_facts_unaffected_by_investor_guard():
    """The investor-mismatch guard must be narrowly scoped -- every other
    fact (Fannie-appropriate or FHA/VA/USDA, which Fannie's own Guide
    legitimately discusses) keeps its citations exactly as v4 shipped them."""
    repo_root = os.path.dirname(_P0)
    v4 = FV.load(os.path.join(repo_root, "storage", "fact_vocabulary", "v4.json"))
    v5 = FV.load(os.path.join(repo_root, "storage", "fact_vocabulary", "v5.json"))
    v4_by_name = {f.canonical_field_name: f for f in v4.facts}
    for fact in v5.facts:
        if fact.canonical_field_name == "loan_product_type":
            continue
        assert fact.guide_citations == v4_by_name[fact.canonical_field_name].guide_citations


def test_real_v4_gift_fact_citation_unaffected_by_vocabulary_expansion():
    """Regression guard: boosting new facts' retrieval queries with their own
    dependent question texts must not also dilute gift's ALREADY-VERIFIED
    query (570606's dependent question texts are shared across all 17
    answers, not gift-specific) -- caught once during this same expansion
    (v4 first draft dropped Personal Gifts from top-3), fixed by having
    DESCRIPTION_OVERRIDES win outright with no boost applied on top."""
    repo_root = os.path.dirname(_P0)
    path = os.path.join(repo_root, "storage", "fact_vocabulary", "v4.json")
    vocab = FV.load(path)
    gift = next(f for f in vocab.facts if f.canonical_field_name == "gift_funds_used")
    assert any("Personal Gifts" in c for c in gift.guide_citations)
