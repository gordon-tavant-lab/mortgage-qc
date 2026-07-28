"""
002g follow-on -- attaches real Fannie Mae Selling Guide citations onto the
seed fact vocabulary, closing the "guideline-phrased ontology" gap: each
`CanonicalFact` should point at the real Guide section(s) that define it,
not just carry its own hand-written description.

Uses `fact_vocabulary.attach_guide_citations()` (already built and tested)
against the SIGNED "Fannie Mae" corpus in `storage/knowledge_base/kb.sqlite3`
(real, ingested from the actual Selling Guide PDF -- see
`ingest_selling_guide.py`). Retrieval is citation-only: `attach_guide_
citations` stores `KBSection.citation` strings, never section content, so
this never originates new rule content -- it only points at where a fact's
existing description/bindings are already defined in the real Guide
(Non-Negotiable #1, "grounding adds context, never new rule content").

Reads the latest `storage/fact_vocabulary/v<N>.json` (currently v1) and
writes a NEW version -- never overwrites the input file (`save()`'s one-
file-per-version convention, 002c precedent). Re-signs the output with the
same honest placeholder signature `build_seed_fact_vocabulary.py` uses:
this proves the citation-attachment pipeline end-to-end but is NOT yet
SME-reviewed, exactly like the fact bindings it builds on.

**Disclosed same-day correction (2026-07-26)**: v1's fact description text
mixed AMQ-provenance detail ("QuestionID 570606", "362 dependent rows") into
the same string `attach_guide_citations()` uses as its retrieval query --
verified directly against the real corpus, this diluted the query enough
that the real defining section (B3-4.3-04, Personal Gifts) ranked 6th, not
top-3. v1's bindings/id/signature are untouched (the actual gating logic
Kayla reviews); this script overrides ONLY the description text with a
domain-focused version before running retrieval, for every fact it enriches
-- so v2+ carries correct citations without rewriting the committed v1
artifact. See `DESCRIPTION_OVERRIDES` below.

Refuses to write anything if the vocabulary or the signed KB corpus is
missing -- never a partial/half-enriched artifact on disk.

**Second disclosed correction (2026-07-27, expanding the vocabulary past
gift)**: promoting 16 more facts (`promote_naming_proposals.py`) surfaced the
same class of bug again on a new fact, `electronic_closing_used` -- its
description-only retrieval query ranked the real defining section (A2-4.1-03,
Electronic Records, Signatures, and Transactions) 5th, outside top_n=3,
verified directly by re-running both queries against the real corpus. The
generalizable fix: fold each fact's own `top_dependent_question_texts`
(already computed once, deterministically, by `discover_fact_candidates.py`
and stored in `candidates/v1.json`) into the retrieval query -- these are the
gated rules' own question text, the strongest self-describing signal
available, and folding them in moved the real section into top_n=3 for
`electronic_closing_used`. Applied generically to every fact with
`candidates/v1.json` data (not just this one), on top of the existing
per-fact `DESCRIPTION_OVERRIDES` mechanism (unchanged, still used for gift).
One fact (`lep_requirements_met`) still returns clearly off-topic sections
even after this fix -- verified by eye against the corpus, not silently
shipped: its citations are dropped and it's flagged in the resulting
artifact's `promotion_note` as "no confident Guide match in this corpus,"
per Non-Negotiable #1 (an honest gap beats a confident wrong citation).

**Third disclosed correction (2026-07-27, caught by a /g-os-judge review of
v4)**: v4 shipped `loan_product_type` -- its OWN description says "The
specific Freddie Mac loan product or program type applicable to this loan,"
and its real answer vocabulary lists actual Freddie Mac trademarked programs
(CHOICERenovation(R), GreenCHOICE(R) Mortgage) -- with THREE citations, all
from the Fannie Mae Selling Guide, because that is the only corpus ingested
(`store.list_versions(kb.sqlite3, "Freddie Mac")` returns `[]`, verified
directly). No score-based fix addresses this: the retrieval ranking could be
perfect and the citations would still be wrong, because the wrong GUIDE
entirely was searched. `_OTHER_INVESTOR_MISMATCH` below is a hard,
pre-retrieval guard -- if a fact's own (real, unboosted) description names an
investor the loaded corpus is not, citations are refused outright, same
disclosed-empty treatment as `lep_requirements_met`, regardless of what
retrieval would have returned.

Run: python3 p0/qc_engine/compiler/build_vocabulary_guide_citations.py

Python 3.9 compatible.
"""
from __future__ import annotations

import dataclasses
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_P0 = os.path.dirname(os.path.dirname(_HERE))
_REPO_ROOT = os.path.dirname(_P0)
if _P0 not in sys.path:
    sys.path.insert(0, _P0)

from qc_engine.compiler import fact_vocabulary as FV  # noqa: E402
from qc_engine.compiler import knowledge_base as KB  # noqa: E402
from qc_engine.compiler import knowledge_base_store as store  # noqa: E402

VOCAB_DIR = os.path.join(_REPO_ROOT, "storage", "fact_vocabulary")
KB_DB_PATH = os.path.join(_REPO_ROOT, "storage", "knowledge_base", "kb.sqlite3")
CANDIDATES_PATH = os.path.join(_REPO_ROOT, "storage", "fact_vocabulary",
                               "candidates", "v1.json")
KB_PROGRAM = "Fannie Mae"

SIGNED_BY = "NOT-A-REAL-SME-pending-kayla-review"
SIGNED_AT = "2026-07-26"

# Sections that read as clearly off-topic on manual inspection even after the
# dependent-question-text boost -- eyeballed against the real corpus, not
# assumed. These facts ship with NO guide_citations rather than a plausible-
# looking wrong one; the caller (main()) also appends a disclosure note.
NO_CONFIDENT_MATCH = {"fact-lep-requirements-met"}

# Other GSEs/investors with NO corpus ingested (verified: only "Fannie Mae"
# has a signed corpus in kb.sqlite3 as of 2026-07-27). If a fact's own real
# description names one of these, its citations are refused outright
# regardless of retrieval score -- searching the Fannie Mae Guide for a
# Freddie Mac product cannot produce a correct citation no matter how the
# query is phrased. Add to this set only investors confirmed to have no
# ingested corpus; do NOT add FHA/VA/USDA here -- Fannie's own Selling Guide
# legitimately discusses government-insured-program eligibility in several
# sections, so a mention of those programs is not automatically a mismatch.
_OTHER_INVESTORS_NO_CORPUS = {"freddie mac"}


def _investor_mismatch(fact: FV.CanonicalFact, corpus_program: str) -> bool:
    desc = fact.description.lower()
    return any(investor in desc and investor != corpus_program.lower()
               for investor in _OTHER_INVESTORS_NO_CORPUS)

# fact.id -> corrected, domain-focused description used ONLY for retrieval
# quality (module docstring: "Disclosed same-day correction"). A fact not
# listed here enriches with its vocabulary-file description unchanged
# (optionally boosted below with its own dependent question texts).
DESCRIPTION_OVERRIDES = {
    "fact-gift-funds-used": (
        "Gift funds: money given to the borrower by a donor -- typically "
        "a family member -- rather than earned or borrowed, requiring an "
        "acceptable donor, a signed gift letter, and documented transfer "
        "of the gift funds."
    ),
}


def _dependent_question_texts_by_qkey():
    if not os.path.exists(CANDIDATES_PATH):
        return {}
    with open(CANDIDATES_PATH) as f:
        candidates = json.load(f)["candidates"]
    return {c["question_key"]: c["top_dependent_question_texts"] for c in candidates}


def _boosted_query_description(fact: FV.CanonicalFact, qtexts_by_key) -> str:
    """The text used ONLY for retrieval query composition -- never written
    back as the fact's real description. DESCRIPTION_OVERRIDES wins OUTRIGHT
    (no qtext appended) -- that text was already manually verified against
    the real corpus (the original gift-fact fix). Appending dependent
    question texts on top of it re-introduces exactly the dilution bug that
    fix corrected: question 570606's texts are shared across ALL 17 answers
    (gift is only one), so boosting gift's already-correct query with them
    pushed B3-4.3-04 (Personal Gifts) out of top_n=3 again -- caught by
    direct comparison against the pre-boost output, not assumed safe.
    Everything else (no manual override yet) gets boosted: its own
    description plus the dependent question texts of every question it
    binds to -- the strongest self-describing signal available (per
    discover_fact_candidates.py)."""
    if fact.id in DESCRIPTION_OVERRIDES:
        return DESCRIPTION_OVERRIDES[fact.id]
    extra = []
    for binding in fact.question_bindings:
        extra.extend(qtexts_by_key.get(binding.question_key, []))
    if not extra:
        return fact.description
    return fact.description + " " + " ".join(dict.fromkeys(extra))  # de-dup, preserve order


def _query_only_vocab(vocab: FV.FactVocabulary) -> FV.FactVocabulary:
    """A throwaway copy used ONLY to drive retrieval -- descriptions here are
    boosted for query quality (dependent question texts folded in) and are
    NEVER what ships. The real, human-facing description is restored from
    `vocab` after citations are retrieved (see main())."""
    qtexts_by_key = _dependent_question_texts_by_qkey()
    facts = [
        dataclasses.replace(f, description=_boosted_query_description(f, qtexts_by_key))
        for f in vocab.facts
    ]
    return FV.FactVocabulary(version=vocab.version, facts=facts,
                             signed_by=vocab.signed_by, signed_at=vocab.signed_at)


def main() -> None:
    try:
        vocab = FV.load_latest(VOCAB_DIR)
    except FileNotFoundError as e:
        raise SystemExit(f"no fact vocabulary to enrich -- {e}")

    if not os.path.exists(KB_DB_PATH):
        raise SystemExit(
            f"KB store not found at {KB_DB_PATH!r} -- run "
            "ingest_selling_guide.py first, refusing to write a partial artifact")

    versions = store.list_versions(KB_DB_PATH, KB_PROGRAM)
    corpus = None
    for version in versions:
        candidate = store.load_from_db(KB_DB_PATH, KB_PROGRAM, version=version)
        if candidate is not None and KB.is_usable(candidate):
            corpus = candidate
            break
    if corpus is None:
        raise SystemExit(
            f"no SIGNED {KB_PROGRAM!r} corpus found in {KB_DB_PATH!r} "
            "(versions on disk: " + repr(versions) + ") -- refusing to write "
            "a partial artifact")

    query_source = _query_only_vocab(vocab)
    enriched = FV.attach_guide_citations(query_source, corpus, top_n=3)
    citations_by_id = {f.id: f.guide_citations for f in enriched.facts}

    final_facts = []
    for fact in vocab.facts:
        citations = citations_by_id.get(fact.id, [])
        note = fact.promotion_note
        if _investor_mismatch(fact, KB_PROGRAM):
            citations = []
            disclosure = (f"This fact's own description names an investor/GSE "
                         f"other than {KB_PROGRAM!r}, the only corpus ingested -- "
                         f"citations refused outright regardless of retrieval "
                         f"score (searching the wrong Guide cannot produce a "
                         f"correct citation). Flagged for SME sourcing against "
                         f"the correct Guide once ingested.")
            note = f"{note} {disclosure}" if note else disclosure
        elif fact.id in NO_CONFIDENT_MATCH:
            citations = []
            disclosure = ("No confident Guide-section match found in the "
                         "indexed Fannie Mae Selling Guide corpus (verified "
                         "by eye, not just by score) -- likely lives outside "
                         "this corpus (e.g. CFPB/fair-lending guidance). "
                         "Flagged for SME sourcing rather than shipping a "
                         "plausible-looking wrong citation.")
            note = f"{note} {disclosure}" if note else disclosure
        final_facts.append(dataclasses.replace(
            fact, description=DESCRIPTION_OVERRIDES.get(fact.id, fact.description),
            guide_citations=citations, promotion_note=note))

    new_version = vocab.version + 1
    out_path = os.path.join(VOCAB_DIR, "v{}.json".format(new_version))
    if os.path.exists(out_path):
        raise SystemExit(
            f"{out_path!r} already exists -- refusing to overwrite an "
            "existing version (one file per version, 002c convention)")

    out_vocab = FV.FactVocabulary(version=new_version, facts=final_facts)
    out_vocab = KB.sign(out_vocab, signed_by=SIGNED_BY, signed_at=SIGNED_AT)
    FV.save(out_vocab, out_path)

    print(f"wrote {out_path}: v{new_version}, {len(out_vocab.facts)} fact(s) "
          f"enriched against signed {KB_PROGRAM!r} corpus v{corpus.version} "
          f"({len(corpus.sections)} sections)")
    for fact in out_vocab.facts:
        print(f"  {fact.canonical_field_name} ({fact.id}):")
        if fact.guide_citations:
            for c in fact.guide_citations:
                print(f"    - {c}")
        else:
            print("    (no guide citations retrieved)")
    print("STATUS: signed_by is an explicit placeholder -- NOT yet SME-reviewed. "
          "Proves the citation-attachment pipeline; not yet trustworthy for a "
          "real compile. Citations are pointers only (section id/title strings) "
          "-- no Guide content was copied onto any fact.")


if __name__ == "__main__":
    main()
