"""
010a -- program applicability gating.

Automated generalization of `p0/fixtures/ruleset_defects.py`'s hand-derived
`_check_applies`/`_PROGRAM_GATED` gating (built once, by hand, for 21 demo
checks) to real-workbook scale, using the two machine-readable program
signals `output/RULE-PROGRAM-GATING-FINDINGS.md` found by direct inspection
of `demo/rules/*.xlsx`:

  1. The Exception Code prefix (PRIMARY, 79% of real rows) -- O-FHA-/O-VA-/
     O-RHS-/O-FRD-/O-FNM-, a direct per-row program tag.
  2. The existing SQL WHERE-clause gating (SECONDARY, 615 rows) -- narrows by
     PropertyType / QC_Policy / LoanPurposeType / LoanType / AddressState, on
     top of (never instead of) the primary signal.

Gating happens BEFORE a Ruleset is built for a loan (the same "gate before
run(), not inside run()" pattern ruleset_defects.py's defects_ruleset_for()
already establishes) -- this module decides which compiled checks enter a
ruleset build; it does not change how engine.py evaluates a check once
included.

Python 3.9 compatible.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from ..model import CanonicalLoan

# --- Primary signal: Exception Code prefix -> program -----------------------
# The 6 confirmed mappings (output/RULE-PROGRAM-GATING-FINDINGS.md SS2),
# corrected 2026-07-20 after fixing taxonomy.py's per-sheet column-shift bug
# (the "Post-Closing Private Bank Oct 2025" questionnaire exports one column
# left of the shared header from "Question Code" onward). SONYMA (State of
# New York Mortgage Agency) is included per Gordon's explicit direction --
# added now even though no synthetic loan fixture exists to test it against
# yet (spec.md Edge Cases: same posture as the still-unconfirmed Jumbo tag).
# Extensible if a future workbook batch introduces a 7th program tag -- not
# assumed closed at 6 (spec.md Assumptions).
_PREFIX_TO_PROGRAM = {
    "O-FHA": "FHA",
    "O-VA": "VA",
    "O-RHS": "USDA",
    "O-FRD": "Freddie Mac",
    "O-FNM": "Fannie Mae",
    "SONYMA": "SONYMA",
}

_DASH_PREFIX_RE = re.compile(r"^([A-Za-z]+(?:-[A-Za-z]+)*)-")


def parse_exception_code_prefix(exception_code: str) -> Optional[str]:
    """Resolve an Exception Code's leading prefix to a program, or None if
    it's a regulation-category / administrative code, not a program tag.

    Two real formats exist in the workbook (found by direct inspection, not
    assumed uniform): dash-delimited (`O-FHA-15293`, the majority) and
    space-delimited (SONYMA's own codes -- `SONYMA`, `SONYMA HDFC`,
    `SONYMA Tax `, etc., never dash-suffixed at all)."""
    if not exception_code:
        return None
    code = str(exception_code).strip()

    m = _DASH_PREFIX_RE.match(code)
    if m:
        prefix = m.group(1)
        # Try progressively shorter dash-joined prefixes (e.g. "O-FHA" before
        # falling back) since some codes carry more than one dash-segment
        # before the numeric id.
        parts = prefix.split("-")
        for i in range(len(parts), 0, -1):
            candidate = "-".join(parts[:i])
            if candidate in _PREFIX_TO_PROGRAM:
                return _PREFIX_TO_PROGRAM[candidate]

    # Space-delimited fallback: the whole code, or just its first word.
    if code in _PREFIX_TO_PROGRAM:
        return _PREFIX_TO_PROGRAM[code]
    first_word = code.split(" ", 1)[0]
    if first_word in _PREFIX_TO_PROGRAM:
        return _PREFIX_TO_PROGRAM[first_word]
    return None


# --- Secondary signal: SQL gating clause -> field/value filters -------------
# The 5 confirmed field/value sets (findings doc SS3). A future batch could
# introduce new values this parser doesn't yet know -- not silently ignored,
# just not narrowed on (spec.md Assumptions).
_SQL_FIELD_VALUE_RE = re.compile(r"Loans\.(\w+)\s*=\s*'([^']*)'")


def parse_sql_gating_clause(clause_text: str) -> Dict[str, Any]:
    """Extract every Loans.<field> = '<value>' pair from a SQL WHERE clause
    into {field: {value, ...}} -- multiple OR'd values for the same field
    collect into one set (e.g. PropertyType's 10 distinct real values)."""
    filters: Dict[str, Any] = {}
    if not clause_text:
        return filters
    for field_name, value in _SQL_FIELD_VALUE_RE.findall(clause_text):
        filters.setdefault(field_name, set()).add(value)
    return filters


# --- The applicability record a compiled check carries ----------------------
@dataclass
class Applicability:
    """What a compiled check's real-row metadata says about who it applies
    to. `program=None` means no program-prefixed Exception Code was found
    (fails open, FR-004) -- NOT the same as an explicitly-tagged program."""
    program: Optional[str] = None
    sql_filters: Dict[str, Any] = field(default_factory=dict)


# A sentinel distinct from True/False -- the Fannie/Freddie "Conventional"
# ambiguity (spec.md FR-005) must be inspectable, never silently resolved
# into a bare bool in either direction.
class _Ambiguous:
    def __repr__(self) -> str:
        return "AMBIGUOUS"

    def __bool__(self) -> bool:
        raise TypeError(
            "AMBIGUOUS must be checked with `is G.AMBIGUOUS`, never used as a "
            "bare bool -- silently truthy/falsy would resolve the ambiguity "
            "this sentinel exists to surface (spec.md FR-005)."
        )


AMBIGUOUS = _Ambiguous()

# loan_type substrings that unambiguously identify a program. Order matters:
# more specific substrings first (none currently overlap, but FHA/VA/USDA all
# appear as their own word in loan_type, e.g. "FHA Purchase").
_LOAN_TYPE_PROGRAM_MARKERS = {
    "FHA": "FHA",
    "VA": "VA",
    "USDA RHS": "USDA",
    "Freddie Mac": "Freddie Mac",
    "Fannie Mae": "Fannie Mae",
    "SONYMA": "SONYMA",
}


def _loan_program(loan_type: str) -> Optional[str]:
    """Best-effort program read off CanonicalLoan.loan_type. Returns None for
    a generically-"Conventional" loan_type that names no specific GSE --
    that absence is exactly the Fannie/Freddie ambiguity (FR-005), not a
    program this function silently assigns."""
    if not loan_type:
        return None
    for marker, program in _LOAN_TYPE_PROGRAM_MARKERS.items():
        if marker in loan_type:
            return program
    return None


def _property_type_matches(loan: CanonicalLoan, sql_filters: Dict[str, Any]) -> bool:
    allowed = sql_filters.get("PropertyType")
    if not allowed:
        return True  # this SQL clause doesn't narrow on property type at all
    loan_property_type = loan.facts.get("property_type")
    return loan_property_type in allowed


def applies_to(loan: CanonicalLoan, applicability: Applicability):
    """The gate a ruleset build calls per compiled check. Returns True/False,
    or AMBIGUOUS for the named Fannie/Freddie "Conventional" edge case
    (spec.md FR-005) -- callers MUST handle AMBIGUOUS explicitly, never treat
    it as a bare bool (it raises TypeError if you try)."""
    if applicability.program is None:
        program_match = True  # untagged row: fail open (FR-004)
    else:
        loan_program = _loan_program(loan.loan_type)
        if loan_program is None:
            # Loan names no specific GSE (e.g. "Conventional Purchase") and
            # the check is tagged for a GSE program specifically -- genuinely
            # ambiguous, not a case this function resolves either way.
            if applicability.program in ("Fannie Mae", "Freddie Mac"):
                return AMBIGUOUS
            program_match = False
        else:
            program_match = loan_program == applicability.program

    if program_match is False:
        return False

    # Secondary signal narrows further, never loosens (FR-003).
    if applicability.sql_filters and not _property_type_matches(loan, applicability.sql_filters):
        return False

    return program_match
