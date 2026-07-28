"""
012 User Story 1 (T010) -- FR-004's MappingGapReport.

A real loan's extracted field name that resolves to no `field_catalog.json`
entry is recorded here, named and structured -- never silently dropped, never
silently coerced into a null `SourceValue` (spec.md Edge Cases). This is a
plain data-holding module: `adapter.py` populates it, callers (SME review,
`p0/eval_real/README.md`'s manual quickstart) read it.

Python 3.9 compatible.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class MappingGap:
    """One real extracted field with no `field_catalog.json` counterpart."""
    field_name: str
    raw_value: Any = None
    # Where in the bundle this field came from -- e.g. "borrowers[0]",
    # "property", "loan_detail" -- an SME triaging the gap needs this to find
    # the field again without re-reading the whole bundle.
    source_section: Optional[str] = None


@dataclass
class MappingGapReport:
    """The full, named list of mapping gaps for one adaptation run
    (FR-004)."""
    loan_id: str
    gaps: List[MappingGap] = field(default_factory=list)

    def add(self, field_name: str, raw_value: Any = None,
            source_section: Optional[str] = None) -> None:
        self.gaps.append(MappingGap(field_name=field_name, raw_value=raw_value,
                                     source_section=source_section))

    @property
    def gap_count(self) -> int:
        return len(self.gaps)

    def to_dict(self):
        return {
            "loan_id": self.loan_id,
            "gap_count": self.gap_count,
            "gaps": [
                {"field_name": g.field_name, "source_section": g.source_section}
                for g in self.gaps
            ],
        }
