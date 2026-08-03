"""
The canonical loan model — DOC (truth) vs SYSTEM.

The QC job: the closing documents from the title company are the SOURCE OF
TRUTH. We check whether the lender's SYSTEM data matches that truth, and flag
any mismatch. That is the whole comparison — one direction, truth wins.

  - DOC    : closed-loan documents from the title company, extracted by
             Touchless. THE TRUTH. Every doc value is traceable (citation).
  - SYSTEM : the lender's data (the LOS export). A MISMO/ULAD/DU file is just
             the same lender data in another file format, so it feeds SYSTEM
             too — we do NOT compare the system against its own re-serialization
             (that proves nothing). If only a MISMO file is available, it is the
             system value.

(If the title/settlement agent ever provides an INDEPENDENT data feed — the
UCD / Closing Disclosure side — that becomes a second truth-side source the
contract can widen to. Not present today; the demo is DOC-vs-SYSTEM.)

Source-agnostic envelope (001b): a field's value is `{truth, sources: {name ->
value}}` — `truth` is always the document/closing-file side; `sources` is an
open, named map of system-side origins (today: "los", "mismo"; extensible to
N sources without a code change, e.g. a future settlement-agent feed).
`system_value()` resolves through `source_priority` (default ["los", "mismo"]),
preserving today's exact LOS-else-MISMO fallback as one named case of the
general mechanism. `doc`/`los`/`mismo` remain as read-write properties over
`truth`/`sources` — every existing call site (including the mutation-based
test-fixture builders in `p0/eval_synth/generator.py`, which read AND write
`.doc`/`.los`/`.mismo` post-construction) keeps working unchanged.

Python 3.9 compatible.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DocCitation:
    """Where a document-extracted value came from — the audit anchor.

    `document_title`/`section`/`field_label` are optional, additive metadata
    (000-synthetic-fixture-generation) — a reviewer or regulator re-deriving a
    value needs more than "page 1" when every source document in a batch is a
    single page; these narrow down exactly where on that page and under what
    heading. Backward compatible: existing call sites that only pass
    doc_name/page_num/segment_snippet are unaffected (all three default to
    None); to_dict() always emits the keys so consumers get a stable shape,
    null where not populated.

    A finer within-page position/span field (character offsets for PDF
    highlighting) was considered and explicitly deferred: every source doc
    in the demo/syn corpus is single-page, and document_title/section/
    field_label already narrow a citation enough for a reviewer to
    re-derive the value without character offsets. Don't re-propose this
    from scratch — if the corpus gains multi-page docs and offsets become
    load-bearing, design it as one finished change (edit here, regenerate
    fixtures, rerun the 25/25 + determinism harness, commit) in a single
    session rather than reopening this file to re-derive the same
    conclusion."""
    doc_name: str
    page_num: int
    segment_snippet: str
    document_title: Optional[str] = None
    section: Optional[str] = None
    field_label: Optional[str] = None
    # live-demo-engine-wiring (ported from p0/qc_engine's 021-touchless-audit-run
    # addition): the real Touchless documentId(s) this citation resolves to, when
    # known. Plural because a single check's evidence can span more than one real
    # document. Same additive, backward-compatible convention as document_title/
    # section/field_label above -- None by default, omitted from to_dict() unless
    # populated.
    document_ids: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "docName": self.doc_name,
            "pageNum": self.page_num,
            "segmentSnippet": self.segment_snippet,
        }
        # Only emit the new keys when populated -- golden.py's hand-authored
        # citations never set these, so their to_dict() stays byte-identical
        # to pre-000 output, preserving harness.py's bit-exact digest (which
        # only ever runs golden_loans(), never these document-derived
        # fixtures). Widening a shared, zero-regression-gated artifact must
        # not force every existing caller's serialized shape to change.
        if self.document_title is not None:
            d["documentTitle"] = self.document_title
        if self.section is not None:
            d["section"] = self.section
        if self.field_label is not None:
            d["fieldLabel"] = self.field_label
        if self.document_ids is not None:
            d["documentIds"] = self.document_ids
        return d


DEFAULT_SOURCE_PRIORITY = ["los", "mismo"]


@dataclass
class SourceValue:
    """A single field's value: `truth` (the document/closing-file side) plus
    a named map of system-side `sources` (001b's source-agnostic envelope,
    generalizing the old fixed `{doc, los, mismo}` attributes).

    `truth` is the source of truth (extracted from the title company's closing
    documents by Touchless, upstream — we consume it, we do not build it).

    `sources` holds the lender's system-side data under named keys. Today:
    `los` (the primary system value) and `mismo` (accepted as a fallback when
    only a MISMO/DU file is available — same lender data, different format).
    They are NOT compared against each other; `system_value()` resolves
    through `source_priority`, whichever is present first.

    Backward-compatible: `doc`, `los`, `mismo` are read-write properties over
    `truth`/`sources`, so `SourceValue(doc=X, los=Y)` and post-construction
    mutation (`sv.los = Y`) both continue to work exactly as before.
    """
    truth: Optional[Any] = None
    sources: Dict[str, Any] = field(default_factory=dict)
    citation: Optional[DocCitation] = None
    # Per-field extraction confidence (0..1) from the upstream extractor.
    # The judge's ruling #8: confident-but-wrong extraction is the dominant
    # residual risk — auto-clear is gated on this, below threshold -> human.
    doc_confidence: Optional[float] = None
    source_priority: List[str] = field(default_factory=lambda: list(DEFAULT_SOURCE_PRIORITY))

    def __init__(self, doc: Optional[Any] = None, los: Optional[Any] = None,
                 mismo: Optional[Any] = None, truth: Optional[Any] = None,
                 sources: Optional[Dict[str, Any]] = None,
                 citation: Optional[DocCitation] = None,
                 doc_confidence: Optional[float] = None,
                 source_priority: Optional[List[str]] = None) -> None:
        # `truth`/`sources` (the generalized envelope) win if both forms are
        # given; `doc`/`los`/`mismo` are the backward-compatible convenience
        # form most existing call sites still use.
        self.truth = truth if truth is not None else doc
        self.sources = dict(sources) if sources is not None else {}
        if los is not None:
            self.sources.setdefault("los", los)
        if mismo is not None:
            self.sources.setdefault("mismo", mismo)
        self.citation = citation
        self.doc_confidence = doc_confidence
        self.source_priority = list(source_priority) if source_priority else list(DEFAULT_SOURCE_PRIORITY)

    # --- backward-compatible read-write properties -------------------------
    @property
    def doc(self) -> Optional[Any]:
        return self.truth

    @doc.setter
    def doc(self, value: Optional[Any]) -> None:
        self.truth = value

    @property
    def los(self) -> Optional[Any]:
        return self.sources.get("los")

    @los.setter
    def los(self, value: Optional[Any]) -> None:
        self.sources["los"] = value

    @property
    def mismo(self) -> Optional[Any]:
        return self.sources.get("mismo")

    @mismo.setter
    def mismo(self, value: Optional[Any]) -> None:
        self.sources["mismo"] = value

    def system_value(self) -> Optional[Any]:
        """The lender's value: resolved through `source_priority` (default
        LOS, else MISMO) — the generalized N-source lookup. Preserves today's
        exact fallback behavior as the default-priority case."""
        for name in self.source_priority:
            v = self.sources.get(name)
            if v is not None:
                return v
        return None


@dataclass
class CanonicalLoan:
    """A loan as the engine sees it: an id, metadata, and a field map.

    The field map is keyed by canonical field name (e.g. "note_rate",
    "loan_amount", "property_value"). Adapters (LOS connector, MISMO XML
    parser, Touchless extraction) populate these slots; the engine never
    parses raw sources.
    """
    loan_id: str
    loan_type: str = ""
    fields: Dict[str, SourceValue] = field(default_factory=dict)
    # Optional pre-derived numeric facts (e.g. monthly income/debts) for ratio
    # checks where the three-way comparison is not the point.
    facts: Dict[str, Any] = field(default_factory=dict)

    def get(self, name: str) -> SourceValue:
        return self.fields.get(name, SourceValue())
