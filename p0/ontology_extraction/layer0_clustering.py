"""
Layer 0 (spec.md US1, FR-001/FR-002/FR-012): deterministic cross-reference-
column clustering. Zero LLM calls, zero network calls -- a pure function of
its input rows.

Real evidence this was built against (`p0/fixtures/ontology_extraction/
retail_post_closing_rows.json`, extracted from the actual Retail workbook):
of 5,520 real Post-Closing rows, 3,255 carry a `Question Criteria by
Questions` expression of the form `QuestionID == N && AnswerText == "..."` --
a single row's own `N` looks like meaningless bookkeeping; the aggregate
answer-vocabulary across every row sharing the same `N` is a decoded
ontology entry. Confirmed: 24 distinct IDs.

Python 3.9 compatible.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Pattern, Set, Tuple

# Confirmed against the real Retail workbook's "Question Criteria by
# Questions" column. Callers may pass a different pattern entirely for a
# different rule source (spec.md Assumptions: "Layer 0's dependency-key
# pattern is configurable... not hardcoded to this project's specific
# syntax").
DEFAULT_DEPENDENCY_PATTERN: Pattern = re.compile(
    r'QuestionID\s*==\s*(\d+)\s*&&\s*AnswerText\s*==\s*"([^"]*)"'
)


@dataclass
class OntologyEntry:
    """One decoded dependency key -- the aggregate answer vocabulary and the
    full set of rows that reference it, reconstructed across the whole input
    set (spec.md Key Entities)."""
    key: str
    answer_vocabulary: List[str] = field(default_factory=list)
    dependent_row_ids: List[str] = field(default_factory=list)


@dataclass
class UnparsedDependency:
    """A row that HAS a dependency expression but it doesn't match the
    configured pattern (FR-002) -- reported, never silently dropped or
    partially matched. Distinct from a row with no expression at all, which
    simply isn't Layer 0's concern (it may still be resolved by Layer 1/2)."""
    row_id: str
    raw_text: str


@dataclass
class CoverageReport:
    """FR-012 / Onity's coverage circuit-breaker precedent: Layer 0's real
    coverage for this run, and whether it fell below a configurable floor."""
    total_rows: int
    resolved_rows: int
    coverage_pct: float
    below_floor: bool


@dataclass
class ClusterResult:
    entries: List[OntologyEntry]
    unparsed: List[UnparsedDependency]
    coverage: CoverageReport
    # row_id -> the set of (key, answer) pairs found in that row's own
    # expression -- pipeline.py uses this to build a PreconditionProposal
    # per resolved row without re-parsing.
    resolved_row_dependencies: Dict[str, List[Tuple[str, str]]] = field(default_factory=dict)


def cluster(
    rows: List[dict],
    dependency_field: str = "question_criteria_by_q",
    pattern: Pattern = DEFAULT_DEPENDENCY_PATTERN,
    coverage_floor: float = 0.0,
) -> ClusterResult:
    """FR-001: cluster every row sharing the same dependency key into one
    `OntologyEntry`, as a pure, deterministic function of `rows`.

    `rows`: plain dicts, each with at least `row_id` and `dependency_field`
    (may be empty/absent -- a row with nothing in that field simply isn't
    Layer 0's concern, not an error).

    A single row may reference more than one key (real example found in the
    fixture: an OR across several applicants' identical question, each a
    different QuestionID) -- it is added to every key's dependent-row set it
    references, not forced into exactly one.
    """
    entries_by_key: Dict[str, Dict[str, Set[str]]] = {}
    unparsed: List[UnparsedDependency] = []
    resolved_row_dependencies: Dict[str, List[Tuple[str, str]]] = {}

    for row in rows:
        raw = (row.get(dependency_field) or "").strip()
        if not raw:
            continue
        matches = pattern.findall(raw)
        if not matches:
            unparsed.append(UnparsedDependency(row_id=row["row_id"], raw_text=raw))
            continue
        row_id = row["row_id"]
        resolved_row_dependencies[row_id] = list(matches)
        for key, answer in matches:
            slot = entries_by_key.setdefault(key, {"answers": set(), "rows": set()})
            slot["answers"].add(answer)
            slot["rows"].add(row_id)

    entries = [
        OntologyEntry(
            key=key,
            answer_vocabulary=sorted(slot["answers"]),
            dependent_row_ids=sorted(slot["rows"]),
        )
        for key, slot in sorted(entries_by_key.items())
    ]

    total_rows = len(rows)
    resolved_rows = len(resolved_row_dependencies)
    coverage_pct = (resolved_rows / total_rows) if total_rows else 0.0
    coverage = CoverageReport(
        total_rows=total_rows, resolved_rows=resolved_rows,
        coverage_pct=coverage_pct, below_floor=coverage_pct < coverage_floor,
    )

    return ClusterResult(
        entries=entries, unparsed=unparsed, coverage=coverage,
        resolved_row_dependencies=resolved_row_dependencies,
    )
