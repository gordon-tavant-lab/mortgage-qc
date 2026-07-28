"""
002g follow-on -- PROMOTE the MEDIUM-tier LLM naming proposals
(`storage/fact_vocabulary/candidates/naming_proposals_v1.json`) into the real,
signed fact vocabulary, closing the "why does the vocabulary only have gift"
gap for good: every one of the 24 decoded questions this project has already
extracted now gets a canonical fact, not just one.

This is a deliberate, disclosed PROMOTION step -- not a re-run of the LLM.
Nothing here calls a model; it deterministically converts already-drafted,
already-validated proposals (every real answer mapped-or-abstained, per
`draft_fact_names_llm.py`'s own validation) into `CanonicalFact` objects.

Two judgment calls made here, both disclosed on the resulting facts via
`promotion_note` (never silently decided):

1. NAME COLLISIONS ACROSS QUESTIONS. Three proposed names
   (`loan_transaction_type`, `appraisal_in_file`,
   `credit_report_present_for_all_applicants`) were independently proposed for
   MULTIPLE distinct AMQ question keys -- the client's own workbook asks the
   same real question under several different keys (by loan program /
   section). Verified directly (see `_find_contradictions` below): no answer
   string maps to two different canonical values across any of these groups,
   so merging them into ONE fact with multiple `question_bindings` is safe --
   this IS the dedup 002g exists to do. Had a contradiction been found, this
   script refuses to merge and raises rather than picking a winner silently
   (untested path today; no real collision needing it exists in this data).

2. STILL NOT SME-SIGNED. Every promoted fact keeps the same honest
   `signed_by` placeholder used by the seed gift fact -- promotion by this
   script is NOT a substitute for Kayla/SME review. `promotion_note` on every
   new fact says so explicitly, and points back at
   `naming_proposals_v1.json` for the full evidence trail (confidence,
   abstained answers, rationale) behind that specific fact.

Writes a NEW version (v3, never overwrites v1/v2 -- 002c precedent). Guide
citations are NOT attached here -- run `build_vocabulary_guide_citations.py`
after this to produce v4 with citations for every fact (it already enriches
"whatever's latest" generically).

Run: python3 p0/qc_engine/compiler/promote_naming_proposals.py
Python 3.9 compatible.
"""
from __future__ import annotations

import os
import sys
from collections import OrderedDict, defaultdict

_HERE = os.path.dirname(os.path.abspath(__file__))
_P0 = os.path.dirname(os.path.dirname(_HERE))
_REPO_ROOT = os.path.dirname(_P0)
if _P0 not in sys.path:
    sys.path.insert(0, _P0)

import json  # noqa: E402

from qc_engine.compiler import fact_vocabulary as FV  # noqa: E402
from qc_engine.compiler import knowledge_base as KB  # noqa: E402

PROPOSALS_PATH = os.path.join(_REPO_ROOT, "storage", "fact_vocabulary",
                              "candidates", "naming_proposals_v1.json")
ONTOLOGY_PATH = os.path.join(_REPO_ROOT, "storage", "rule_ontology", "v1.json")
VOCAB_DIR = os.path.join(_REPO_ROOT, "storage", "fact_vocabulary")

SIGNED_BY = "NOT-A-REAL-SME-pending-kayla-review"
SIGNED_AT = "2026-07-27"


class NameCollisionConflictError(Exception):
    """Two proposals share a field name but disagree about what an answer
    means -- refuses to guess which one is right (never auto-picked)."""


def _row_ids_by_question(ontology_path):
    with open(ontology_path) as f:
        entries = json.load(f)["entries"]
    return {e["question_key"]: e["dependent_row_ids"] for e in entries}


def _citation_for_question(qkey, row_ids_by_q):
    ids = row_ids_by_q.get(qkey, [])
    sample = ids[:5]
    cites = [f"AMQ Retail Post-Closing row {rid}" for rid in sample]
    if len(ids) > 5:
        cites.append(f"... and {len(ids) - 5} more rows sharing question {qkey}")
    return cites


def _group_facts_by_name(proposals):
    """Every (question_key, proposed fact) pair, grouped by proposed_field_name
    -- the raw material for either a single-question fact or a cross-question
    merge (see module docstring, point 1)."""
    groups = OrderedDict()
    for p in proposals:
        for fact in p["llm_proposal"]["facts"]:
            groups.setdefault(fact["proposed_field_name"], []).append(
                (p["question_key"], fact))
    return groups


def _find_contradictions(entries):
    """An answer string that maps to two different canonical values across
    entries sharing a proposed name -- these must NOT be silently merged."""
    seen = {}
    conflicts = []
    for _qkey, fact in entries:
        for answer, value in fact["answer_value_map"].items():
            if answer in seen and seen[answer] != value:
                conflicts.append((answer, seen[answer], value))
            seen[answer] = value
    dtypes = {fact["data_type"] for _qkey, fact in entries}
    if len(dtypes) > 1:
        conflicts.append(("__data_type__", dtypes, None))
    return conflicts


def _build_fact(name, entries, row_ids_by_q):
    conflicts = _find_contradictions(entries)
    if conflicts:
        raise NameCollisionConflictError(
            f"proposed name {name!r} shared across questions "
            f"{[q for q, _ in entries]} but entries disagree: {conflicts}")

    first_qkey, first_fact = entries[0]
    merged_across = sorted({q for q, _ in entries})

    # group each contributing question's answers by canonical_value into
    # QuestionBinding rows (one binding per (question, canonical_value)).
    bindings = []
    for qkey, fact in entries:
        by_value = defaultdict(list)
        for answer, value in fact["answer_value_map"].items():
            by_value[value].append(answer)
        for value, answers in by_value.items():
            bindings.append(FV.QuestionBinding(
                question_key=qkey, answers=sorted(answers), canonical_value=value))

    citations = []
    for qkey in merged_across:
        citations.extend(_citation_for_question(qkey, row_ids_by_q))

    note = (f"LLM-drafted proposal (Sonnet, temp=0) promoted from "
            f"naming_proposals_v1.json on {SIGNED_AT} -- NOT yet reviewed by a "
            f"domain SME. Verify against the source questions before treating "
            f"as ground truth.")
    if len(merged_across) > 1:
        note += (f" Merged across {len(merged_across)} AMQ question keys "
                 f"({', '.join(merged_across)}) that the client's own workbook "
                 f"asks separately but that resolve to the same real fact -- "
                 f"verified no contradicting answer-to-value mapping across "
                 f"them before merging.")

    return FV.CanonicalFact(
        id=f"fact-{name.replace('_', '-')}",
        canonical_field_name=name,
        data_type=first_fact["data_type"],
        description=first_fact["description"],
        question_bindings=bindings,
        source_citations=citations,
        promotion_note=note,
    )


def main() -> None:
    for path, what in ((PROPOSALS_PATH, "naming proposals"), (ONTOLOGY_PATH, "rule ontology")):
        if not os.path.exists(path):
            raise SystemExit(f"{what} missing at {path!r}")

    with open(PROPOSALS_PATH) as f:
        proposals_doc = json.load(f)
    row_ids_by_q = _row_ids_by_question(ONTOLOGY_PATH)

    try:
        current = FV.load_latest(VOCAB_DIR)
    except FileNotFoundError:
        current = FV.FactVocabulary(version=0, facts=[])

    groups = _group_facts_by_name(proposals_doc["proposals"])
    new_facts = [_build_fact(name, entries, row_ids_by_q)
                 for name, entries in groups.items()]

    existing_names = {f.canonical_field_name for f in current.facts}
    collisions = existing_names & {f.canonical_field_name for f in new_facts}
    if collisions:
        raise SystemExit(f"proposed name(s) {collisions} already exist in the "
                         f"signed vocabulary -- refusing to shadow an existing fact")

    all_facts = list(current.facts) + new_facts
    new_version = current.version + 1
    out_path = os.path.join(VOCAB_DIR, f"v{new_version}.json")
    if os.path.exists(out_path):
        raise SystemExit(f"{out_path!r} already exists -- refusing to overwrite")

    out_vocab = FV.FactVocabulary(version=new_version, facts=all_facts)
    out_vocab = KB.sign(out_vocab, signed_by=SIGNED_BY, signed_at=SIGNED_AT)
    FV.save(out_vocab, out_path)

    merged_groups = {n: len(e) for n, e in groups.items() if len(e) > 1}
    print(f"wrote {out_path}: v{new_version}, {len(all_facts)} total fact(s) "
          f"({len(current.facts)} carried over + {len(new_facts)} newly promoted)")
    print(f"  {len(groups)} distinct facts from {sum(len(e) for e in groups.values())} "
          f"proposed (question, fact) pairs across {len(proposals_doc['proposals'])} questions")
    if merged_groups:
        print("  merged across multiple question keys (same real fact, "
              "differently-keyed questions in the source workbook):")
        for name, n in merged_groups.items():
            print(f"    - {name}: {n} question keys")
    print("STATUS: signed_by is the same honest placeholder -- NOT yet "
          "SME-reviewed. Every new fact's promotion_note discloses this and "
          "points back at naming_proposals_v1.json. Run "
          "build_vocabulary_guide_citations.py next for Guide citations.")


if __name__ == "__main__":
    main()
