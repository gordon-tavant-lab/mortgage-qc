"""
Generalized scenario construction -- the promoted, production successor to
`p0/experiment_002a/score_drafts.py`'s `SCORERS` dict (spec.md FR-001-004,
SC-001; 005 User Story 1).

`score_drafts.py` proved (at n=24, during the 002a spike) that a labeled
pass-case/fail-case loan pair can be built generically from a `Check` object
alone -- kind + field_name (+ operator/threshold/tolerance/normalizer) -- with
NO hand-written per-field mutation function, unlike
`p0/eval_synth/generator.py`'s 7 mutation operators (each hardcoded to one
specific demo field: `property_address`, `note_signed`, `loan_amount`/
`property_value`). That file's own docstring says explicitly it is an
adaptation, not a promoted component (FR-013 -- this module must never import
it).

This module promotes that pattern and extends it:
  - covers all 6 check kinds `qc_engine.engine` dispatches on today
    (`predicate`, `ratio_threshold`, `agree_categorical`, `agree_numeric`,
    `agree_doc_categorical`, `agree_doc_numeric` -- score_drafts.py covered
    only the first 4; `agree_doc_categorical`/`agree_doc_numeric` were added
    by 003d, after that spike was written -- Gap 4),
  - reads `field_catalog.json`'s `data_type` (via `qc_engine.catalog`)
    instead of assuming every field is a plain string (used for
    `predicate`/`is_present`'s "present" value and available to any future
    strategy that needs it),
  - sets every `applies_if` precondition (002e, added after the spike) on
    BOTH constructed loans, so the check is genuinely REACHED by the engine
    rather than short-circuited to `NOT_APPLICABLE` (FR-003),
  - constructs two independent DOCUMENT-only values (never touching
    `SourceValue.sources{}`) for the two doc-vs-doc kinds (FR-004).

An unregistered `Check.kind` (or an internal construction error) is recorded
as an explicit, structured `ConstructedScenario(ok=False, error=...)` --
`construct_scenario` never raises and never silently skips (FR-002); a
`coverage_set.py` run iterating hundreds of checks must survive one bad
check without losing the rest.

Python 3.9 compatible.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Callable, Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qc_engine.model import CanonicalLoan, SourceValue  # noqa: E402
from qc_engine.ruleset import Check  # noqa: E402
from qc_engine.catalog import load_catalog, FieldCatalog  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CATALOG_PATH = os.path.join(os.path.dirname(HERE), "qc_engine", "field_catalog.json")

_CATALOG: Optional[FieldCatalog] = None


def _catalog() -> FieldCatalog:
    """Lazy-loaded, process-wide singleton -- the catalog is a large (379-
    entry), immutable, version-controlled file; no reason to re-parse it once
    per constructed scenario."""
    global _CATALOG
    if _CATALOG is None:
        _CATALOG = load_catalog(CATALOG_PATH)
    return _CATALOG


@dataclass
class ConstructedScenario:
    """The (pass_loan, fail_loan, expected_..._status, provenance) tuple one
    strategy produces for one `Check` -- the generalized, per-check successor
    to `generator.py`'s fixed-ruleset `LabeledLoan` shape (spec.md Key
    Entities)."""
    check_id: str
    kind: str
    ok: bool
    pass_loan: Optional[CanonicalLoan] = None
    fail_loan: Optional[CanonicalLoan] = None
    expected_pass_status: Optional[str] = None
    expected_fail_status: Optional[str] = None
    provenance: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


def _failure(chk: Check, msg: str) -> ConstructedScenario:
    return ConstructedScenario(check_id=chk.id, kind=chk.kind, ok=False, error=msg)


# --------------------------------------------------------------------------- #
# applies_if precondition-setting (FR-003) -- generic across every kind, so
# it is applied centrally by construct_scenario() rather than duplicated
# inside each kind-specific strategy.
# --------------------------------------------------------------------------- #
def _satisfying_value(operator: str, raw_value: str) -> Any:
    """A value that makes `_applies_if_condition_holds` (qc_engine.engine)
    evaluate TRUE for this operator/raw_value pair -- the inverse of the
    engine's own condition check."""
    if operator == "==":
        return raw_value
    if operator == "!=":
        return f"{raw_value}__NOT_A_MATCH"
    if operator == "in":
        options = raw_value.split("|")
        return options[0] if options else raw_value
    if operator == "between":
        lo_s, hi_s = raw_value.split("|")
        lo, hi = Decimal(lo_s), Decimal(hi_s)
        return str((lo + hi) / Decimal(2))
    if operator in ("<=", "<"):
        return str(Decimal(raw_value) - Decimal("1"))
    if operator in (">=", ">"):
        return str(Decimal(raw_value) + Decimal("1"))
    raise ValueError(f"unknown applies_if operator '{operator}'")


def _apply_preconditions(chk: Check, loan: CanonicalLoan) -> None:
    """Set `loan`'s facts so every `chk.applies_if` condition holds -- the
    check is genuinely REACHED, never short-circuited to `NOT_APPLICABLE` by
    an unset precondition field (FR-003, US1 Acceptance Scenario 2)."""
    for cond in (chk.applies_if or []):
        precondition_field = cond["field_name"]
        value = _satisfying_value(cond["operator"], cond["value"])
        existing = loan.fields.get(precondition_field)
        if existing is not None:
            existing.truth = value
        else:
            loan.fields[precondition_field] = SourceValue(doc=value, doc_confidence=0.99)


# --------------------------------------------------------------------------- #
# Data-type-aware sample values -- generic, keyed by the catalog's
# `data_type` or the Check's own declared `normalizer`, never by a specific
# field name (that is the whole point of the generalization: no per-field
# mutation function).
# --------------------------------------------------------------------------- #
def _present_value_for_field(field_name: str) -> Any:
    entry = _catalog().get(field_name)
    data_type = entry.data_type if entry else "string"
    if data_type == "boolean":
        return True
    if data_type == "decimal":
        return "100.00"
    if data_type == "date":
        return "2026-01-01"
    return "present-value"


def _agree_pair_values(normalizer: str) -> Tuple[str, str]:
    """A (matching-shape, matching-shape) pair keyed by the Check's own
    declared `normalizer` -- generic (driven by an attribute every agree_*
    Check already carries), not a hand-picked field-specific pair. Chosen so
    the pair survives round-tripping through each normalizer's own
    transform (e.g. ssn_last4 strips non-digits -- a plain "VALUE_A"/"VALUE_B"
    pair would normalize to the SAME empty string on both sides and never
    diverge)."""
    if normalizer == "ssn_last4":
        return "111-11-1111", "222-22-2222"
    if normalizer == "address":
        return ("123 Main St, Springfield, IL 62704",
                "456 Oak Ave, Springfield, IL 62704")
    if normalizer == "flood_zone":
        return "Zone A", "Zone B"
    return "VALUE_A", "VALUE_B"


# --------------------------------------------------------------------------- #
# Kind-specific strategies -- ported from score_drafts.py's SCORERS (loan-
# pair-returning form, not score-returning), plus the 2 new doc-vs-doc
# strategies score_drafts.py never had (Gap 4).
# --------------------------------------------------------------------------- #
def _construct_predicate(chk: Check) -> ConstructedScenario:
    if chk.predicate == "is_true":
        pass_loan = CanonicalLoan(loan_id=f"{chk.id}-pass", fields={
            chk.field_name: SourceValue(doc=True, doc_confidence=0.99)})
        fail_loan = CanonicalLoan(loan_id=f"{chk.id}-fail", fields={
            chk.field_name: SourceValue(doc=False, doc_confidence=0.99)})
    elif chk.predicate == "is_present":
        present_value = _present_value_for_field(chk.field_name)
        pass_loan = CanonicalLoan(loan_id=f"{chk.id}-pass", fields={
            chk.field_name: SourceValue(doc=present_value, doc_confidence=0.99)})
        # "" (empty, non-None) rather than None -- a None truth value is NOT
        # exempted via NOT_APPLICABLE in the current engine (003a fixed the
        # blanket early-return score_drafts.py's own comment describes); ""
        # genuinely exercises is_present's own "not None and non-blank" logic.
        fail_loan = CanonicalLoan(loan_id=f"{chk.id}-fail", fields={
            chk.field_name: SourceValue(doc="", doc_confidence=0.99)})
    else:
        return _failure(chk, f"unknown predicate '{chk.predicate}'")
    return ConstructedScenario(
        check_id=chk.id, kind=chk.kind, ok=True,
        pass_loan=pass_loan, fail_loan=fail_loan,
        expected_pass_status="PASS", expected_fail_status="FAIL",
        provenance={"strategy": "predicate", "predicate": chk.predicate})


def _construct_ratio_threshold(chk: Check) -> ConstructedScenario:
    if not chk.threshold or chk.threshold == "UNSPECIFIED":
        return _failure(chk, "threshold is unset/UNSPECIFIED -- the compiler "
                              "honestly declined to invent one; no scenario "
                              "can be constructed for it")
    thr = Decimal(chk.threshold)
    op = chk.operator
    if op in ("<=", "<"):
        pass_val, fail_val = thr - Decimal("5"), thr + Decimal("5")
    else:  # >=, >
        pass_val, fail_val = thr + Decimal("5"), thr - Decimal("5")

    def _loan_for(value: Decimal, loan_id: str) -> CanonicalLoan:
        loan = CanonicalLoan(loan_id=loan_id)
        if chk.ratio == "ltv":
            loan.facts = {"property_value": "100.00", "loan_amount": str(value)}
        elif chk.ratio == "dti":
            loan.facts = {"monthly_income": "100.00", "monthly_debts": str(value)}
        elif chk.ratio == "field_value":
            loan.fields = {chk.field_name: SourceValue(doc=str(value), doc_confidence=0.99)}
        else:
            raise ValueError(f"unknown ratio '{chk.ratio}'")
        return loan

    try:
        pass_loan = _loan_for(pass_val, f"{chk.id}-pass")
        fail_loan = _loan_for(fail_val, f"{chk.id}-fail")
    except ValueError as e:
        return _failure(chk, str(e))
    return ConstructedScenario(
        check_id=chk.id, kind=chk.kind, ok=True,
        pass_loan=pass_loan, fail_loan=fail_loan,
        expected_pass_status="PASS", expected_fail_status="FAIL",
        provenance={"strategy": "ratio_threshold", "ratio": chk.ratio, "operator": op})


def _construct_agree_categorical(chk: Check) -> ConstructedScenario:
    val_a, val_b = _agree_pair_values(chk.normalizer)
    pass_loan = CanonicalLoan(loan_id=f"{chk.id}-pass", fields={
        chk.field_name: SourceValue(doc=val_a, los=val_a, doc_confidence=0.99)})
    fail_loan = CanonicalLoan(loan_id=f"{chk.id}-fail", fields={
        chk.field_name: SourceValue(doc=val_a, los=val_b, doc_confidence=0.99)})
    return ConstructedScenario(
        check_id=chk.id, kind=chk.kind, ok=True,
        pass_loan=pass_loan, fail_loan=fail_loan,
        expected_pass_status="PASS", expected_fail_status="FLAG",
        provenance={"strategy": "agree_categorical", "normalizer": chk.normalizer})


def _construct_agree_numeric(chk: Check) -> ConstructedScenario:
    if chk.tolerance == "UNSPECIFIED":
        return _failure(chk, "tolerance is UNSPECIFIED -- this resolves "
                              "NEEDS_REVIEW regardless of divergence; no "
                              "PASS/FLAG scenario can be constructed for it")
    tol = Decimal(chk.tolerance) if chk.tolerance else Decimal("0")
    base = Decimal("100.00")
    fail_val = base + tol + Decimal("5")
    pass_loan = CanonicalLoan(loan_id=f"{chk.id}-pass", fields={
        chk.field_name: SourceValue(doc=str(base), los=str(base), doc_confidence=0.99)})
    fail_loan = CanonicalLoan(loan_id=f"{chk.id}-fail", fields={
        chk.field_name: SourceValue(doc=str(base), los=str(fail_val), doc_confidence=0.99)})
    return ConstructedScenario(
        check_id=chk.id, kind=chk.kind, ok=True,
        pass_loan=pass_loan, fail_loan=fail_loan,
        expected_pass_status="PASS", expected_fail_status="FLAG",
        provenance={"strategy": "agree_numeric", "tolerance": chk.tolerance})


def _construct_agree_doc_categorical(chk: Check) -> ConstructedScenario:
    """003d's doc-vs-doc kind (Gap 4, new coverage): two independently-
    extracted DOCUMENT values, neither a system source -- `sources{}` MUST
    stay empty on both fields (FR-004), unlike agree_categorical above."""
    if not chk.compare_field_name:
        return _failure(chk, "agree_doc_categorical requires compare_field_name")
    val_a, val_b = _agree_pair_values(chk.normalizer)
    pass_loan = CanonicalLoan(loan_id=f"{chk.id}-pass", fields={
        chk.field_name: SourceValue(doc=val_a, doc_confidence=0.99),
        chk.compare_field_name: SourceValue(doc=val_a, doc_confidence=0.99)})
    fail_loan = CanonicalLoan(loan_id=f"{chk.id}-fail", fields={
        chk.field_name: SourceValue(doc=val_a, doc_confidence=0.99),
        chk.compare_field_name: SourceValue(doc=val_b, doc_confidence=0.99)})
    return ConstructedScenario(
        check_id=chk.id, kind=chk.kind, ok=True,
        pass_loan=pass_loan, fail_loan=fail_loan,
        # QC phase (003d): a doc-vs-doc mismatch is a genuine closing-package
        # defect -- resolves FAIL, not agree_categorical's informational FLAG.
        expected_pass_status="PASS", expected_fail_status="FAIL",
        provenance={"strategy": "agree_doc_categorical", "normalizer": chk.normalizer})


def _construct_agree_doc_numeric(chk: Check) -> ConstructedScenario:
    """Numeric counterpart to _construct_agree_doc_categorical (Gap 4, new
    coverage). Same UNSPECIFIED-tolerance honesty guard as agree_numeric."""
    if not chk.compare_field_name:
        return _failure(chk, "agree_doc_numeric requires compare_field_name")
    if chk.tolerance == "UNSPECIFIED":
        return _failure(chk, "tolerance is UNSPECIFIED -- this resolves "
                              "NEEDS_REVIEW regardless of divergence; no "
                              "PASS/FAIL scenario can be constructed for it")
    tol = Decimal(chk.tolerance) if chk.tolerance else Decimal("0")
    base = Decimal("100.00")
    fail_val = base + tol + Decimal("5")
    pass_loan = CanonicalLoan(loan_id=f"{chk.id}-pass", fields={
        chk.field_name: SourceValue(doc=str(base), doc_confidence=0.99),
        chk.compare_field_name: SourceValue(doc=str(base), doc_confidence=0.99)})
    fail_loan = CanonicalLoan(loan_id=f"{chk.id}-fail", fields={
        chk.field_name: SourceValue(doc=str(base), doc_confidence=0.99),
        chk.compare_field_name: SourceValue(doc=str(fail_val), doc_confidence=0.99)})
    return ConstructedScenario(
        check_id=chk.id, kind=chk.kind, ok=True,
        pass_loan=pass_loan, fail_loan=fail_loan,
        expected_pass_status="PASS", expected_fail_status="FAIL",
        provenance={"strategy": "agree_doc_numeric", "tolerance": chk.tolerance})


# The generalized, 6-kind successor to score_drafts.py's SCORERS dict
# (FR-001, SC-001).
STRATEGIES: Dict[str, Callable[[Check], ConstructedScenario]] = {
    "predicate": _construct_predicate,
    "ratio_threshold": _construct_ratio_threshold,
    "agree_categorical": _construct_agree_categorical,
    "agree_numeric": _construct_agree_numeric,
    "agree_doc_categorical": _construct_agree_doc_categorical,
    "agree_doc_numeric": _construct_agree_doc_numeric,
}


def construct_scenario(chk: Check) -> ConstructedScenario:
    """Look up `chk.kind` in `STRATEGIES`; on a registered kind, build a
    pass-case + fail-case `CanonicalLoan` and satisfy every
    `chk.applies_if` precondition on BOTH constructed loans (FR-003) before
    returning. On an unregistered kind -- or any internal construction
    error -- returns `ok=False` with a non-empty `error`; NEVER raises and
    NEVER silently skips (FR-002)."""
    strategy = STRATEGIES.get(chk.kind)
    if strategy is None:
        return _failure(chk, f"no registered scenario-construction strategy "
                              f"for kind '{chk.kind}'")
    try:
        scenario = strategy(chk)
    except Exception as e:  # noqa: BLE001 -- one bad check must never crash
                             # a whole coverage/gate run (FR-002).
        return _failure(chk, str(e))

    if scenario.ok and chk.applies_if:
        for loan in (scenario.pass_loan, scenario.fail_loan):
            if loan is not None:
                _apply_preconditions(chk, loan)

    return scenario
