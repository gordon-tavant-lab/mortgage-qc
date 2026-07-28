"""
002c -- versioned, per-program, section-fingerprinted knowledge base.

A static, curated corpus of domain context (regulation summaries, guide
excerpts) per loan program, built once, SME-signed before use, and updated
incrementally without breaking the provenance of rules already compiled
against a prior version. See spec.md US1/US2 and
output/RULE-PROGRAM-GATING-FINDINGS.md for the underlying 6-program
segmentation this corpus mirrors.

US1: a corpus is versioned, content-fingerprinted, and unusable until signed.
US2: an update re-fingerprints only changed/new sections; a rule grounded
against version N keeps resolving to version N's exact content after the
corpus advances to version N+1.
US3 (retrieval half only -- compile-path integration lives in
test_p0.py's 002c section): pure keyword-overlap ranking, no network.

Run from p0/:  python -m pytest tests/test_knowledge_base.py -v
Python 3.9 compatible.
"""
from __future__ import annotations

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qc_engine.compiler import knowledge_base as KB


def _fha_documents():
    return [
        {"source_document": "HUD Handbook 4000.1, II.A.1.b",
         "citation": "hud.gov/4000.1",
         "content": "The HUD-92900-A Section III Borrower Certification must be signed "
                     "by all borrowers and completed in full before closing."},
        {"source_document": "HUD Handbook 4000.1, II.A.8.a",
         "citation": "hud.gov/4000.1",
         "content": "Gift funds must be documented with a signed gift letter and evidence "
                     "of the transfer of funds from the donor to the borrower."},
    ]


# --- T004: building a corpus fingerprints every section, carries a version --
def test_build_corpus_fingerprints_every_section():
    corpus = KB.build_corpus("FHA", _fha_documents(), version=1)
    assert corpus.program == "FHA"
    assert corpus.version == 1
    assert len(corpus.sections) == 2
    for section in corpus.sections:
        assert section.content_fingerprint
        assert len(section.content_fingerprint) == 64  # sha256 hex digest


# --- T005: unsigned corpus is unusable; retrieve() refuses to use it -------
def test_unsigned_corpus_is_unusable():
    corpus = KB.build_corpus("FHA", _fha_documents(), version=1)
    assert KB.is_usable(corpus) is False


def test_retrieve_against_unsigned_corpus_raises():
    corpus = KB.build_corpus("FHA", _fha_documents(), version=1)
    try:
        KB.retrieve(corpus, "gift funds")
        assert False, "expected retrieve() to raise against an unsigned corpus"
    except KB.CorpusNotSignedError:
        pass


# --- T006: sign() makes is_usable() True, mirrors RuleProvenance's shape ---
def test_sign_makes_corpus_usable():
    corpus = KB.build_corpus("FHA", _fha_documents(), version=1)
    signed = KB.sign(corpus, signed_by="kayla.sme@lender.example", signed_at="2026-07-20T10:00:00Z")
    assert KB.is_usable(signed) is True
    assert signed.signed_by == "kayla.sme@lender.example"
    assert signed.signed_at == "2026-07-20T10:00:00Z"
    # sign() must not mutate the fingerprints of the sections it signs
    assert signed.sections[0].content_fingerprint == corpus.sections[0].content_fingerprint


# --- T010: save/load round-trips a corpus, one file per version -----------
def test_save_and_load_round_trip():
    corpus = KB.sign(KB.build_corpus("FHA", _fha_documents(), version=1),
                      signed_by="kayla.sme@lender.example", signed_at="2026-07-20T10:00:00Z")
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "FHA", "v1.json")
        KB.save(corpus, path)
        loaded = KB.load(path)
        assert loaded.program == corpus.program
        assert loaded.version == corpus.version
        assert loaded.signed_by == corpus.signed_by
        assert [s.content_fingerprint for s in loaded.sections] == \
               [s.content_fingerprint for s in corpus.sections]
        assert KB.is_usable(loaded) is True


# --- T012: update_corpus() re-fingerprints only changed/new sections -------
def test_update_corpus_preserves_unchanged_section_fingerprints():
    v1 = KB.sign(KB.build_corpus("FHA", _fha_documents(), version=1),
                 signed_by="kayla.sme@lender.example", signed_at="2026-07-20T10:00:00Z")

    docs_v2 = _fha_documents()
    # Only the gift-funds document changes; the HUD-92900-A one is untouched.
    docs_v2[1]["content"] = (
        "Gift funds must be documented with a signed gift letter, evidence of the "
        "transfer, AND the donor's ability to provide the gift (bank statement).")
    v2 = KB.update_corpus(v1, docs_v2, new_version=2)

    assert v2.version == 2
    unchanged = [s for s in v2.sections if s.source_document == "HUD Handbook 4000.1, II.A.1.b"]
    changed = [s for s in v2.sections if s.source_document == "HUD Handbook 4000.1, II.A.8.a"]
    assert unchanged[0].content_fingerprint == v1.sections[0].content_fingerprint
    assert changed[0].content_fingerprint != v1.sections[1].content_fingerprint


# --- T013: a version-N grounding record still resolves to version-N content
def test_prior_version_still_resolves_after_update():
    v1 = KB.sign(KB.build_corpus("FHA", _fha_documents(), version=1),
                 signed_by="kayla.sme@lender.example", signed_at="2026-07-20T10:00:00Z")
    with tempfile.TemporaryDirectory() as tmpdir:
        v1_path = os.path.join(tmpdir, "FHA", "v1.json")
        KB.save(v1, v1_path)

        docs_v2 = _fha_documents()
        docs_v2[1]["content"] = "A materially different gift-funds requirement."
        v2 = KB.sign(KB.update_corpus(v1, docs_v2, new_version=2),
                     signed_by="kayla.sme@lender.example", signed_at="2026-07-21T10:00:00Z")
        v2_path = os.path.join(tmpdir, "FHA", "v2.json")
        KB.save(v2, v2_path)

        # The v1 file on disk is untouched by writing v2 -- loading it still
        # gives the original gift-funds section content, not the new one.
        reloaded_v1 = KB.load(v1_path)
        gift_section = next(s for s in reloaded_v1.sections
                            if s.source_document == "HUD Handbook 4000.1, II.A.8.a")
        assert "ability to provide the gift" not in gift_section.content
        assert "signed gift letter" in gift_section.content


# --- T016: retrieve() ranks by keyword overlap, caps at top_n --------------
def test_retrieve_ranks_by_keyword_overlap_and_caps_at_top_n():
    corpus = KB.sign(KB.build_corpus("FHA", _fha_documents(), version=1),
                     signed_by="kayla.sme@lender.example", signed_at="2026-07-20T10:00:00Z")
    results = KB.retrieve(corpus, "gift letter donor funds", top_n=1)
    assert len(results) == 1
    assert results[0].source_document == "HUD Handbook 4000.1, II.A.8.a"


def test_retrieve_returns_empty_for_no_overlap():
    corpus = KB.sign(KB.build_corpus("FHA", _fha_documents(), version=1),
                     signed_by="kayla.sme@lender.example", signed_at="2026-07-20T10:00:00Z")
    results = KB.retrieve(corpus, "completely unrelated appraisal comp distance topic zzz")
    assert results == []


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
