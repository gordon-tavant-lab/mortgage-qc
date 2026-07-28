"""
apply_loan_profile.py -- promotes run_013_comprehensive_e2e_v6/build_and_run.py's
one-off `_panel_from_v2_profiles()` inline pattern (`SourceValue(doc=entry
["value"])`, guarded by `fact_name not in loan.fields`) into tested, reusable
`qc_engine` code (spec.md Gap 2, FR-006).

Distinct concern from build_loan_profiles_v3.py: that module *derives* a
fact's value (a batch, profile-build-time operation over a fixture);
`apply_derived_facts` *wires* an already-derived profile onto a specific,
already-loaded `CanonicalLoan` instance (a per-loan-load-time operation) --
the same single-purpose-module discipline `010a`'s own plan.md cited for
keeping `program_gating.py` separate from `compile_llm.py`.

Two invariants, both load-bearing (spec.md Edge Cases / FR-006):
  1. NEVER overwrite an existing `loan.fields` entry of the same name -- a
     derived fact only fills a gap, it never shadows a genuinely extracted
     field (Non-Negotiable #1: the document is the source of truth).
  2. `underivable` entries write NOTHING -- the existing 002e/NEEDS_REVIEW
     path already handles an absent field correctly; this function's job is
     only to promote what WAS derived, never to paper over what wasn't.

Inherits, does not resolve, 002g's own recorded "third provenance kind" gap:
a derived fact is written as `SourceValue(doc=value)` with `citation=None`,
since a derived fact was never extracted from a document page/segment.

Run (as a library, not a script): imported by qc_engine callers that load a
CanonicalLoan and want its build_loan_profiles_v3 profile wired onto it.
Python 3.9 compatible. Deterministic -- pure dict-merge, no network, no LLM.
"""
from __future__ import annotations

from typing import Any, Dict

from .model import CanonicalLoan, SourceValue


def apply_derived_facts(loan: CanonicalLoan, profile: Dict[str, Any]) -> CanonicalLoan:
    """Write every `profile["derived_facts"]` entry into `loan.fields`,
    skipping any fact_name already present (never shadows a real extracted
    field of the same name). `profile["underivable"]` entries are read but
    never written -- absence is the correct signal for 002e's existing
    NEEDS_REVIEW/APPLICABILITY_UNKNOWN path to act on downstream.

    Mutates `loan` in place and returns it (matching run_013's own
    `_panel_from_v2_profiles()` in-place-mutation shape), so callers may use
    either the return value or the original reference.
    """
    for fact_name, entry in profile.get("derived_facts", {}).items():
        if fact_name in loan.fields:
            continue
        loan.fields[fact_name] = SourceValue(doc=entry["value"])
    return loan
