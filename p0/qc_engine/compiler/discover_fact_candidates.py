"""
002g follow-on -- SELF-DISCOVERY of canonical-fact candidates from the
project's own artifacts, answering "why does the vocabulary only have the
gift entry -- where is the rest?"

The rest was never missing -- it was undiscovered-but-derivable. The decoded
rule ontology (`storage/rule_ontology/v1.json`) already lists every question
the client's own rulebook gates on (24 questions, real answer vocabularies,
3,255 gated rows). This script turns each into a DRAFT CanonicalFact
candidate, assembled entirely from real data:

  - the question's real answer vocabulary (from the workbook, verbatim)
  - the dependent rows' own question texts (what the gated rules ask about
    -- the strongest self-describing signal)
  - real Selling Guide citations (pointer-only, via the signed KB corpus --
    same concept-index mechanism as `build_vocabulary_guide_citations.py`)
  - loan-application-side field suggestions (deterministic token overlap
    against the 379-entry field catalog -- which extraction fields this
    fact could plausibly read from)

What this deliberately does NOT do: name the facts. A canonical field name
("gift_funds_used") is semantic content someone must own -- candidates ship
as `NEEDS_NAMING`, and become real vocabulary entries only through the
existing review path (optionally LLM-proposed at compile time, MEDIUM trust
tier, never auto-approved -- 002f's discipline). Guide/catalog matches are
suggestions with their evidence attached, never auto-bindings.

Output: storage/fact_vocabulary/candidates/v1.json (deterministic).

Run: python3 p0/qc_engine/compiler/discover_fact_candidates.py
Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
_P0 = os.path.dirname(os.path.dirname(_HERE))
_REPO_ROOT = os.path.dirname(_P0)
if _P0 not in sys.path:
    sys.path.insert(0, _P0)

from qc_engine.compiler import fact_vocabulary as FV  # noqa: E402
from qc_engine.compiler import knowledge_base as KB  # noqa: E402
from qc_engine.compiler import knowledge_base_store as store  # noqa: E402

ONTOLOGY_PATH = os.path.join(_REPO_ROOT, "storage", "rule_ontology", "v1.json")
ROWS_PATH = os.path.join(_P0, "fixtures", "ontology_extraction",
                         "retail_post_closing_rows.json")
CATALOG_PATH = os.path.join(_P0, "qc_engine", "field_catalog.json")
KB_DB_PATH = os.path.join(_REPO_ROOT, "storage", "knowledge_base", "kb.sqlite3")
KB_PROGRAM = "Fannie Mae"
VOCAB_DIR = os.path.join(_REPO_ROOT, "storage", "fact_vocabulary")
OUT_PATH = os.path.join(VOCAB_DIR, "candidates", "v1.json")

# Boilerplate that appears in nearly every AMQ question text -- stripped from
# retrieval queries so the domain words (asset, credit report, HELOC...)
# carry the IDF weight, per the lesson already learned and disclosed in
# build_vocabulary_guide_citations.py (provenance/boilerplate noise pushed
# the real Personal Gifts section from rank 1 to rank 6).
_BOILERPLATE = re.compile(
    r"were all|requirements met|best practice|\(fha\)|\(va\)|\(usda\)|yes,?|n/?a,?|_x000d_",
    re.IGNORECASE)
_WORD = re.compile(r"[a-z]{3,}")

_STOP = {"the", "all", "for", "was", "were", "are", "and", "loan", "type",
         "there", "this", "that", "with", "not", "met", "yes", "each"}


def _tokens(text: str) -> set:
    return {w for w in _WORD.findall(text.lower()) if w not in _STOP}


def _clean_query(parts) -> str:
    joined = " ".join(parts)
    return _BOILERPLATE.sub(" ", joined)


def main() -> None:
    for path, what in ((ONTOLOGY_PATH, "rule ontology"), (ROWS_PATH, "fixture rows"),
                       (CATALOG_PATH, "field catalog")):
        if not os.path.exists(path):
            raise SystemExit(f"{what} missing at {path!r} -- refusing to write "
                             "a candidates artifact not derived from data")

    with open(ONTOLOGY_PATH) as f:
        ontology = json.load(f)
    with open(ROWS_PATH) as f:
        rows_by_id = {r["row_id"]: r for r in json.load(f)}
    with open(CATALOG_PATH) as f:
        catalog_fields = [e["field_name"] for e in json.load(f)["entries"]]
    catalog_tokens = {name: _tokens(name.replace("_", " ")) for name in catalog_fields}

    corpus = None
    if os.path.exists(KB_DB_PATH):
        for version in store.list_versions(KB_DB_PATH, KB_PROGRAM):
            candidate = store.load_from_db(KB_DB_PATH, KB_PROGRAM, version=version)
            if candidate is not None and KB.is_usable(candidate):
                corpus = candidate
                break

    # which (question, answer) pairs the current vocabulary already binds
    bound = {}
    try:
        vocab = FV.load_latest(VOCAB_DIR)
        for fact in vocab.facts:
            for b in fact.question_bindings:
                for a in b.answers:
                    bound[(b.question_key, a)] = fact.canonical_field_name
    except FileNotFoundError:
        pass

    candidates = []
    for entry in ontology["entries"]:
        qkey = entry["question_key"]
        answers = entry["answer_vocabulary"]
        dep_ids = entry["dependent_row_ids"]
        qtext_counts = Counter(
            rows_by_id[rid]["question_text"].replace("_x000D_", "").strip()
            for rid in dep_ids if rid in rows_by_id)
        top_qtexts = [t for t, _ in qtext_counts.most_common(3)]

        query = _clean_query(answers + top_qtexts)
        guide_citations = []
        if corpus is not None:
            guide_citations = [s.citation for s in KB.retrieve(corpus, query, top_n=3)]

        cand_tokens = _tokens(query)
        scored = sorted(
            ((len(cand_tokens & toks), name) for name, toks in catalog_tokens.items()
             if len(cand_tokens & toks) >= 2),
            key=lambda t: (-t[0], t[1]))
        field_suggestions = [{"field_name": name, "shared_tokens": n}
                             for n, name in scored[:3]]

        bound_answers = {a: bound[(qkey, a)] for a in answers if (qkey, a) in bound}
        candidates.append({
            "question_key": qkey,
            "status": ("PARTIALLY_BOUND" if bound_answers else "NEEDS_NAMING"),
            "already_bound_answers": bound_answers,
            "answer_vocabulary": answers,
            "dependent_row_count": entry["dependent_row_count"],
            "top_dependent_question_texts": top_qtexts,
            "guide_citation_suggestions": guide_citations,
            "catalog_field_suggestions": field_suggestions,
            "proposed_field_name": None,  # NEVER auto-filled -- naming is owned
        })

    out = {
        "version": 1,
        "note": ("DRAFT candidates self-discovered from the decoded rule ontology "
                 "-- every element traces to real workbook rows, real Guide "
                 "sections (pointers only), or real catalog fields. Nothing here "
                 "is a binding until named and signed through the vocabulary "
                 "review path (002f trust-tier discipline: never auto-approved)."),
        "derived_from": {"rule_ontology": "storage/rule_ontology/v1.json",
                          "kb_corpus": (f"{KB_PROGRAM} v{corpus.version}" if corpus else None),
                          "field_catalog_entries": len(catalog_fields)},
        "candidates": sorted(candidates, key=lambda c: -c["dependent_row_count"]),
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)

    total_rows = sum(c["dependent_row_count"] for c in candidates)
    print(f"wrote {OUT_PATH}: {len(candidates)} candidates covering "
          f"{total_rows} gated rows")
    for c in out["candidates"][:8]:
        tag = c["status"]
        print(f"  Q{c['question_key']} [{tag}] {c['dependent_row_count']} rows | "
              f"answers: {c['answer_vocabulary'][:2]}...")
    print("STATUS: candidates only -- no names proposed, no bindings created; "
          "naming requires the review path (SME, optionally LLM-drafted at "
          "MEDIUM trust tier, never auto-approved).")


if __name__ == "__main__":
    main()
