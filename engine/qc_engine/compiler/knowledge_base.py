"""
002c -- versioned, per-program, section-fingerprinted knowledge base.

A static, curated corpus of domain context (regulation summaries, guide
excerpts, glossary entries) per loan program -- built once, SME-signed
before any rule compiles against it, and updated incrementally (section-
level diffing) without breaking the provenance of rules already compiled
against a prior version. Retrieval is a pure, in-memory keyword-overlap
ranking -- NOT a live web search or research-agent call (spec.md FR-005) --
so grounding a compile call never introduces the reproducibility risk a
live-search design would (see spec.md preamble for the research this
design choice is built on).

Mirrors ruleset.py's RuleProvenance sign-off shape: a corpus is real data
the moment it's built, but UNUSABLE for grounding until an SME signs it
(is_usable() gates retrieve()) -- the same "no sign-off, no use" discipline
the compiled Ruleset itself already enforces.

BUILDING A CORPUS (hard constraint, applies to whoever/whatever authors a
KBSection's `content` -- a human, an agent, or web/research-assisted
drafting): research may ADD CONTEXT to a rule that already exists in the
source AMQ workbook -- e.g. citing the real regulation a defect_text
condition traces to, or clarifying ambiguous phrasing -- but must NEVER
introduce a new rule, threshold, or condition that has no textual basis in
the workbook itself. A KBSection is a citation and explanation of an
existing condition, never a source of new rule content. If research
surfaces a plausible-sounding industry-standard number (e.g. a commonly-
cited distance/ratio limit) that cannot be traced to an actual row in
demo/rules/*.xlsx, it does not belong in a KBSection at all -- flag it to
the SME as an open question instead of encoding it as grounding. This is
what keeps compile_llm.py's SYSTEM_PROMPT constraint ("never invent a
number, date, or condition") meaningful: an LLM correctly refusing to
invent a threshold is defeated if the KB it's told to trust already
smuggled that invented threshold in as "grounding."

Python 3.9 compatible.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import math
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class CorpusNotSignedError(Exception):
    """Raised when retrieve() is called against an unsigned corpus -- a
    compile step must never ground against material an SME hasn't
    reviewed yet."""


def _fingerprint(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


@dataclass
class KBSection:
    """One fingerprinted unit within a corpus version."""
    id: str
    program: str
    content: str
    source_document: str
    citation: str
    content_fingerprint: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "program": self.program, "content": self.content,
            "source_document": self.source_document, "citation": self.citation,
            "content_fingerprint": self.content_fingerprint,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "KBSection":
        return KBSection(**d)


@dataclass
class KnowledgeBaseCorpus:
    """A versioned, program-scoped corpus. Unusable for grounding until
    signed (mirrors RuleProvenance's signed_by/signed_at shape)."""
    program: str
    version: int
    sections: List[KBSection] = field(default_factory=list)
    signed_by: Optional[str] = None
    signed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "program": self.program, "version": self.version,
            "sections": [s.to_dict() for s in self.sections],
            "signed_by": self.signed_by, "signed_at": self.signed_at,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "KnowledgeBaseCorpus":
        return KnowledgeBaseCorpus(
            program=d["program"], version=d["version"],
            sections=[KBSection.from_dict(s) for s in d["sections"]],
            signed_by=d.get("signed_by"), signed_at=d.get("signed_at"),
        )


def build_corpus(program: str, documents: List[Dict[str, str]], version: int = 1) -> KnowledgeBaseCorpus:
    """Fingerprint each document into one KBSection. `documents` is a list
    of {"source_document", "citation", "content"} -- the output of a
    one-time, human-reviewed research/curation step (spec.md US1); this
    function does not itself fetch or research anything."""
    sections = []
    for i, doc in enumerate(documents):
        content = doc["content"]
        sections.append(KBSection(
            id=f"{program}-{version}-{i:03d}", program=program, content=content,
            source_document=doc["source_document"], citation=doc.get("citation", ""),
            content_fingerprint=_fingerprint(content),
        ))
    return KnowledgeBaseCorpus(program=program, version=version, sections=sections)


def update_corpus(prior: KnowledgeBaseCorpus, documents: List[Dict[str, str]],
                   new_version: int) -> KnowledgeBaseCorpus:
    """Section-level diff versioning (spec.md US2, FR-003): a document whose
    content is byte-identical to a prior section reuses that section's
    identity and fingerprint unchanged; a document whose content differs (or
    is new) gets a freshly fingerprinted section. Unchanged sections are
    never re-derived -- their content_fingerprint is provably the same
    object as before, not merely equal by coincidence."""
    prior_by_source = {s.source_document: s for s in prior.sections}
    sections = []
    for i, doc in enumerate(documents):
        content = doc["content"]
        existing = prior_by_source.get(doc["source_document"])
        if existing is not None and existing.content == content:
            sections.append(existing)  # carried forward unchanged, same fingerprint
        else:
            sections.append(KBSection(
                id=f"{prior.program}-{new_version}-{i:03d}", program=prior.program,
                content=content, source_document=doc["source_document"],
                citation=doc.get("citation", ""), content_fingerprint=_fingerprint(content),
            ))
    return KnowledgeBaseCorpus(program=prior.program, version=new_version, sections=sections)


def sign(corpus: Any, signed_by: str, signed_at: str) -> Any:
    """Marks a corpus usable. Returns a new object (same content) rather than
    mutating in place, matching this project's existing dataclass-construction
    discipline elsewhere. 002g refactor: `dataclasses.replace` instead of an
    explicit `KnowledgeBaseCorpus(...)` call — identical behavior for a
    KnowledgeBaseCorpus, and now reusable by any dataclass carrying the same
    `signed_by`/`signed_at` sign-off shape (`fact_vocabulary.FactVocabulary`),
    so sign-off logic exists exactly once."""
    return dataclasses.replace(corpus, signed_by=signed_by, signed_at=signed_at)


def is_usable(corpus: KnowledgeBaseCorpus) -> bool:
    return corpus.signed_by is not None and corpus.signed_at is not None


def save(corpus: KnowledgeBaseCorpus, path: str) -> None:
    """One file per version, never overwritten in place -- the same
    provenance guarantee US2 requires (a prior version's file is untouched
    by writing a later one)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(corpus.to_dict(), f, indent=2, sort_keys=True)


def load(path: str) -> KnowledgeBaseCorpus:
    with open(path) as f:
        return KnowledgeBaseCorpus.from_dict(json.load(f))


_WORD_RE = re.compile(r"[a-z0-9]+")


def _words(text: str) -> set:
    return set(_WORD_RE.findall(text.lower()))


def retrieve(corpus: KnowledgeBaseCorpus, query_text: str, top_n: int = 3) -> List[KBSection]:
    """Pure, in-memory ranking -- no embeddings, no network (FR-005: zero
    live calls in the compile path). IDF-weighted keyword overlap: a shared
    word that appears in only a few sections (e.g. "gift", "donor") counts
    for much more than one that appears in most of them (e.g. "loan",
    "borrower") -- plain unweighted overlap counting degrades once the
    corpus is real-scale (hundreds of sections, verified against the real
    380-section Fannie Mae Selling Guide corpus) rather than the handful of
    hand-curated sections this was originally validated against."""
    if not is_usable(corpus):
        raise CorpusNotSignedError(
            f"corpus {corpus.program} v{corpus.version} is not signed -- "
            "cannot retrieve from unreviewed material")
    query_words = _words(query_text)
    if not query_words:
        return []

    section_words = [(section, _words(section.content)) for section in corpus.sections]
    n_sections = len(section_words)
    doc_freq: Dict[str, int] = {}
    for _, sw in section_words:
        for term in query_words & sw:
            doc_freq[term] = doc_freq.get(term, 0) + 1

    scored = []
    for section, sw in section_words:
        overlap = query_words & sw
        if not overlap:
            continue
        # +1 smoothing: a term that (degenerately) appears in every section
        # still contributes a small positive weight rather than log(1) = 0.
        score = sum(math.log((n_sections + 1) / doc_freq[t]) for t in overlap)
        scored.append((score, section))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [section for _, section in scored[:top_n]]
