"""
002g -- canonical loan-fact vocabulary: the signed, versioned bridge between
`002f`'s extracted precondition proposals and real catalog fields.

Why this exists (spec.md Gap 2): `002f` Layer 0 names its proposals after the
AMQ's own opaque question keys (`question_570606`), and Layer 1 lets an LLM
invent a fresh snake_case `field_name` per row. Nothing reconciled either onto
the field catalog's real vocabulary -- two rows about the same real fact could
gate on two different field names and, in principle, disagree about the same
loan. A `CanonicalFact` is that reconciliation, authored once and SME-signed:
which question/answer pairs and which extracted names all mean *this* catalog
field, and what canonical value each answer maps to.

Sign-off discipline is the KB corpus's, reused literally: `knowledge_base.sign`
/ `knowledge_base.is_usable` operate on this module's `FactVocabulary` too
(002g T001 made `sign` generic via `dataclasses.replace`), and resolution
against an unsigned vocabulary raises -- mirroring `CorpusNotSignedError`,
because a fact that gates real checks across the rulebook is at least as
load-bearing as a KB section.

The guide-citation attachment (`attach_guide_citations`) is the concept-index
decision recorded in spec.md's Assumptions: citation strings ONLY -- pointers
to verbatim Selling Guide sections via the signed KB's own `retrieve()` --
never content, staying on the right side of `010a`'s Guide-gates-never-
originates boundary.

Python 3.9 compatible.
"""
from __future__ import annotations

import glob
import json
import os
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from qc_engine.compiler import knowledge_base as KB


class VocabularyNotSignedError(Exception):
    """Raised when resolution is attempted against an unsigned vocabulary --
    a compiled check must never gate on a fact an SME hasn't reviewed."""


@dataclass
class QuestionBinding:
    """Maps a Layer-0 (question, answers) pair onto a canonical field value.
    The answers list is the exact AnswerText strings from the real workbook's
    decoded cluster -- never paraphrased."""
    question_key: str
    answers: List[str]
    canonical_value: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "QuestionBinding":
        return QuestionBinding(**d)


@dataclass
class CanonicalFact:
    id: str
    canonical_field_name: str
    data_type: str
    description: str
    name_synonyms: List[str] = field(default_factory=list)
    question_bindings: List[QuestionBinding] = field(default_factory=list)
    mismo_ldd_reference: Optional[str] = None
    source_citations: List[str] = field(default_factory=list)
    guide_citations: List[str] = field(default_factory=list)
    promotion_note: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "CanonicalFact":
        d = dict(d)
        d["question_bindings"] = [QuestionBinding.from_dict(b) for b in d.get("question_bindings", [])]
        return CanonicalFact(**d)


@dataclass
class FactVocabulary:
    """Versioned, program-agnostic. Unusable for resolution until signed --
    same shape as KnowledgeBaseCorpus so KB.sign/KB.is_usable apply as-is."""
    version: int
    facts: List[CanonicalFact] = field(default_factory=list)
    signed_by: Optional[str] = None
    signed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "facts": [f.to_dict() for f in self.facts],
            "signed_by": self.signed_by, "signed_at": self.signed_at,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "FactVocabulary":
        return FactVocabulary(
            version=d["version"],
            facts=[CanonicalFact.from_dict(f) for f in d["facts"]],
            signed_by=d.get("signed_by"), signed_at=d.get("signed_at"),
        )


def save(vocab: FactVocabulary, path: str) -> None:
    """One file per version, never overwritten in place (002c precedent)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(vocab.to_dict(), f, indent=2, sort_keys=True)


def load(path: str) -> FactVocabulary:
    with open(path) as f:
        return FactVocabulary.from_dict(json.load(f))


def load_latest(dir_path: str) -> FactVocabulary:
    """Finds the highest `v<N>.json` in `dir_path` and loads it -- the read
    side of `save()`'s one-file-per-version convention (002c precedent), so
    callers that just want "whatever's current" don't have to hardcode a
    version number that will go stale the next time this is regenerated."""
    candidates = glob.glob(os.path.join(dir_path, "v*.json"))
    versioned = []
    for path in candidates:
        m = re.match(r"^v(\d+)\.json$", os.path.basename(path))
        if m:
            versioned.append((int(m.group(1)), path))
    if not versioned:
        raise FileNotFoundError(
            f"no v<N>.json fact-vocabulary files found in {dir_path!r} -- "
            "nothing to load")
    versioned.sort(key=lambda t: t[0])
    _, latest_path = versioned[-1]
    return load(latest_path)


# --- Resolution --------------------------------------------------------------

@dataclass
class Resolution:
    """The outcome of resolving one PreconditionProposal against the signed
    vocabulary. Exactly one of `condition` / `reason` is meaningful:
    status == "resolved"        -> condition is the applies_if dict to attach
    status == "unresolved"      -> reason says which answer/name had no mapping
    status == "novel_candidate" -> reason carries the name to surface for
                                   SME review; NEVER auto-added (FR-002)."""
    status: str
    condition: Optional[Dict[str, str]] = None
    reason: Optional[str] = None
    fact_id: Optional[str] = None


def _require_signed(vocab: FactVocabulary) -> None:
    if not KB.is_usable(vocab):
        raise VocabularyNotSignedError(
            f"fact vocabulary v{vocab.version} is not signed -- "
            "cannot resolve preconditions against unreviewed facts")


def resolve_layer0(vocab: FactVocabulary, proposal: Any) -> Resolution:
    """Resolve a Layer-0 proposal (`field_name` like `question_570606`,
    values = raw AnswerText strings) onto a canonical field condition.

    Every answer must map through ONE fact's bindings for the same question
    key; any unmapped answer, or answers spanning two different facts, refuses
    resolution (never guesses) -- the row then compiles without `applies_if`
    and the draft is flagged for review (compile_llm.attach_preconditions)."""
    _require_signed(vocab)
    cond = proposal.condition
    if cond is None:
        return Resolution(status="unresolved", reason="proposal carries no condition")
    if not cond.field_name.startswith("question_"):
        return Resolution(status="unresolved",
                          reason=f"not a Layer-0 question field: {cond.field_name}")
    qkey = cond.field_name[len("question_"):]
    answers = cond.value if isinstance(cond.value, list) else [cond.value]

    matched_fact: Optional[CanonicalFact] = None
    canonical_values: List[str] = []
    for answer in answers:
        hit_fact = None
        hit_value = None
        for fact in vocab.facts:
            for binding in fact.question_bindings:
                if binding.question_key == qkey and answer in binding.answers:
                    hit_fact, hit_value = fact, binding.canonical_value
                    break
            if hit_fact is not None:
                break
        if hit_fact is None:
            return Resolution(status="unresolved",
                              reason=f"no signed binding for question {qkey} "
                                     f"answer {answer!r}")
        if matched_fact is not None and hit_fact.id != matched_fact.id:
            return Resolution(status="unresolved",
                              reason=f"answers for question {qkey} span two facts "
                                     f"({matched_fact.id}, {hit_fact.id}) -- SME must split")
        matched_fact = hit_fact
        if hit_value not in canonical_values:
            canonical_values.append(hit_value)

    if len(canonical_values) == 1:
        condition = {"field_name": matched_fact.canonical_field_name,
                     "operator": "==", "value": canonical_values[0]}
    else:
        # engine.py's `in` encoding: pipe-joined options (002e).
        condition = {"field_name": matched_fact.canonical_field_name,
                     "operator": "in", "value": "|".join(canonical_values)}
    return Resolution(status="resolved", condition=condition, fact_id=matched_fact.id)


def resolve_field_name(vocab: FactVocabulary, name: str) -> Resolution:
    """Resolve a Layer-1-extracted field name: exact canonical match reuses;
    a signed synonym resolves to its canonical name; anything else is a novel
    candidate for SME review -- never silently added (FR-002/US2)."""
    _require_signed(vocab)
    for fact in vocab.facts:
        if name == fact.canonical_field_name:
            return Resolution(status="resolved",
                              condition={"field_name": fact.canonical_field_name},
                              fact_id=fact.id)
    for fact in vocab.facts:
        if name in fact.name_synonyms:
            return Resolution(status="resolved",
                              condition={"field_name": fact.canonical_field_name},
                              fact_id=fact.id)
    return Resolution(status="novel_candidate", reason=name)


# --- Concept index (citation-only) -------------------------------------------

def attach_guide_citations(vocab: FactVocabulary, corpus: Any, top_n: int = 3) -> FactVocabulary:
    """For each fact, retrieve the signed Selling Guide sections that define
    it and store their CITATION STRINGS (never content) on the fact -- the
    concept-index decision (spec.md Assumptions). Retrieval goes through
    `KB.retrieve`, so an unsigned corpus raises `CorpusNotSignedError` before
    anything is attached. Returns a new vocabulary; input is not mutated."""
    new_facts = []
    for fact in vocab.facts:
        query = " ".join(
            [fact.canonical_field_name.replace("_", " "), fact.description]
            + [a for b in fact.question_bindings for a in b.answers]
        )
        sections = KB.retrieve(corpus, query, top_n=top_n)
        cited = [s.citation for s in sections if s.citation]
        new_facts.append(CanonicalFact(
            id=fact.id, canonical_field_name=fact.canonical_field_name,
            data_type=fact.data_type, description=fact.description,
            name_synonyms=list(fact.name_synonyms),
            question_bindings=list(fact.question_bindings),
            mismo_ldd_reference=fact.mismo_ldd_reference,
            source_citations=list(fact.source_citations),
            guide_citations=cited,
            promotion_note=fact.promotion_note,
        ))
    return FactVocabulary(version=vocab.version, facts=new_facts,
                          signed_by=vocab.signed_by, signed_at=vocab.signed_at)
