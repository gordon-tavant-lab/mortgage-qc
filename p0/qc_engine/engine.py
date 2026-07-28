"""
The deterministic evaluation engine.

Runs a SIGNED ruleset (by hash) against a CanonicalLoan and emits, per check, a
regulator-grade audit record: the three input values, the normalized/derived
value actually compared, the rounding applied, the rule version, the verdict,
and the document citation. (Judge ruling #4: the audit record is a wrapper WE
build with field-level intermediates — not an opaque debug trace.)

NO floats touch a money/ratio decision: ratios go through qc_engine.money in
Decimal with a pinned rounding policy. NO network, NO model, NO wall-clock —
the engine is a pure function of (ruleset, loan). That is what makes
"same loan -> same verdict, every time, every machine" provable.

Python 3.9 compatible.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from . import money as M
from . import reconcile as R
from .model import CanonicalLoan, SourceValue
from .ruleset import Check, Ruleset

# Auto-clear is gated on extraction confidence (judge ruling #8): a
# confident-but-wrong extraction must never silently auto-clear a bad loan.
DEFAULT_CONFIDENCE_FLOOR = 0.80


PHASE_RECONCILE = "RECONCILE"
PHASE_QC = "QC"


def _phase_for(chk: Check) -> str:
    """Resolve the check's phase; infer from kind if not explicitly set."""
    if chk.phase:
        return chk.phase
    if chk.kind in ("agree_categorical", "agree_numeric"):
        return PHASE_RECONCILE
    return PHASE_QC


@dataclass
class CheckResult:
    check_id: str
    check_name: str
    severity: str
    status: str               # PASS | FAIL | WARNING | NEEDS_REVIEW
    field_name: str
    phase: str = ""           # RECONCILE | QC
    # field-level audit intermediates (the regulator's "show me the math")
    inputs: Dict[str, Any] = field(default_factory=dict)   # {doc, system}
    normalized: Dict[str, Any] = field(default_factory=dict)
    compared_value: Optional[str] = None    # the derived/normalized value
    rounding: Optional[str] = None
    tolerance: Optional[str] = None
    citation: Optional[Dict[str, Any]] = None
    doc_confidence: Optional[float] = None
    message: str = ""
    # 004: open-vocabulary reason a check contributes to NEEDS_REVIEW -- set
    # generically by phase+status (see _eval_check's post-dispatch block),
    # never per check-kind. None for PASS/NOT_APPLICABLE/FLAG (a FLAG never
    # gets a reason -- Principle V, the two-step model stays intact).
    review_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_id": self.check_id,
            "check_name": self.check_name,
            "severity": self.severity,
            "status": self.status,
            "field_name": self.field_name,
            "phase": self.phase,
            "inputs": self.inputs,
            "normalized": self.normalized,
            "compared_value": self.compared_value,
            "rounding": self.rounding,
            "tolerance": self.tolerance,
            "citation": self.citation,
            "doc_confidence": self.doc_confidence,
            "message": self.message,
            "review_reason": self.review_reason,
        }


_TRUE_STRINGS = ("true", "yes", "1")
_FALSE_STRINGS = ("false", "no", "0")


def _normalize_for_applies_if(v: Any) -> Optional[str]:
    if v is None:
        return None
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v).strip().lower()


def _applies_if_condition_holds(loan_value: Any, operator: str, raw_value: str) -> bool:
    """002e FR-002: evaluate one `applies_if` condition. `loan_value` is
    already confirmed non-None by the caller."""
    if operator in ("==", "!="):
        lv = _normalize_for_applies_if(loan_value)
        rv = raw_value.strip().lower()
        eq = lv == rv
        return eq if operator == "==" else not eq
    if operator == "in":
        options = {o.strip().lower() for o in raw_value.split("|")}
        return _normalize_for_applies_if(loan_value) in options
    if operator == "between":
        lo_s, hi_s = raw_value.split("|")
        lo, hi = M.to_decimal(lo_s), M.to_decimal(hi_s)
        val = M.to_decimal(loan_value)
        return lo <= val <= hi
    if operator in ("<=", ">=", "<", ">"):
        val = M.to_decimal(loan_value)
        thr = M.to_decimal(raw_value)
        return (val <= thr) if operator == "<=" else (val < thr) if operator == "<" \
            else (val >= thr) if operator == ">=" else (val > thr)
    raise ValueError(f"unknown applies_if operator '{operator}'")


def _eval_applies_if(loan: CanonicalLoan, chk: Check, res: CheckResult) -> bool:
    """002e FR-002/FR-003: evaluate every condition in `chk.applies_if`
    (AND-combined) before any kind-specific dispatch. Mutates `res` and
    returns True if the gate resolved the check (caller must return `res`
    immediately, never falling through to kind-dispatch); returns False if
    every condition holds (or `applies_if` is absent) and evaluation should
    proceed normally.

    A definite non-match on ANY condition short-circuits to NOT_APPLICABLE
    immediately (FR-002), even if an earlier condition's field was unknown --
    a confirmed non-match takes priority over an unknown one (FR-003's
    ordering: NEEDS_REVIEW only when NO condition has already definitively
    failed)."""
    if not chk.applies_if:
        return False
    unknown_field: Optional[str] = None
    for condition in chk.applies_if:
        field_name = condition["field_name"]
        loan_value = loan.get(field_name).doc
        if loan_value is None:
            if unknown_field is None:
                unknown_field = field_name
            continue
        if not _applies_if_condition_holds(loan_value, condition["operator"], condition["value"]):
            res.status = "NOT_APPLICABLE"
            res.message = (f"Precondition not met: {field_name} {condition['operator']} "
                           f"{condition['value']!r} does not hold for this loan.")
            return True
    if unknown_field is not None:
        res.status = "NEEDS_REVIEW"
        res.review_reason = "APPLICABILITY_UNKNOWN"
        res.message = (f"Cannot determine applicability of this check -- "
                       f"precondition field '{unknown_field}' is unknown on this loan.")
        return True
    return False


def _eval_check(loan: CanonicalLoan, chk: Check,
                confidence_floor: float) -> CheckResult:
    sv = loan.get(chk.field_name)
    citation = sv.citation.to_dict() if sv.citation else None
    res = CheckResult(
        check_id=chk.id, check_name=chk.name, severity=chk.severity,
        status="PASS", field_name=chk.field_name, phase=_phase_for(chk),
        citation=citation, doc_confidence=sv.doc_confidence,
    )

    if _eval_applies_if(loan, chk, res):
        return res

    if chk.kind == "agree_categorical":
        # DOC (truth) vs SYSTEM. Flag if they disagree.
        doc_v = sv.doc
        sys_v = sv.system_value()
        res.inputs = {"doc": doc_v, "system": sys_v}
        if doc_v is None and sys_v is None:
            res.status = "NOT_APPLICABLE"
            res.message = f"No data present for {chk.field_name}."
        elif doc_v is None:
            res.status = "NEEDS_REVIEW"
            res.message = (f"No truth document for {chk.field_name}; "
                           f"cannot verify system value '{sys_v}'.")
        elif sys_v is None:
            res.status = "NEEDS_REVIEW"
            res.message = f"No system value to check against the document."
        else:
            dn = R.normalize(chk.normalizer, doc_v)
            sn = R.normalize(chk.normalizer, sys_v)
            res.normalized = {"doc": dn, "system": sn}
            if dn == sn:
                res.status = "PASS"
                res.message = chk.message_pass or "Document matches system."
            else:
                # Reconcile mismatch is INFORMATIONAL: the loan docs are truth,
                # so we FLAG the data-sync difference but do NOT fail QC on it.
                res.status = "FLAG"
                res.severity = "INFO"
                res.message = chk.message_fail or (
                    f"{chk.field_name}: document (truth) says '{doc_v}' "
                    f"but system says '{sys_v}' — system data out of sync.")

    elif chk.kind == "agree_numeric":
        # DOC (truth) vs SYSTEM, within an authored tolerance.
        if chk.tolerance == "UNSPECIFIED":
            # The compiler honestly declined to invent a tolerance the
            # source AMQ row didn't state (2026-07-22 hallucination-
            # prevention fix) -- this is a rule-authoring gap, not a data
            # gap, so it must never resolve NOT_APPLICABLE (which would
            # silently hide it) or crash (M.to_decimal("UNSPECIFIED") is
            # not a valid Decimal). Surfaces to a human explicitly.
            res.status = "NEEDS_REVIEW"
            res.review_reason = "UNSPECIFIED_THRESHOLD"
            res.message = (f"Rule tolerance for {chk.field_name} was not stated in the "
                           f"source rule text -- needs SME input before this check can run.")
            return res
        doc_v = sv.doc
        sys_v = sv.system_value()
        res.inputs = {"doc": doc_v, "system": sys_v}
        res.tolerance = chk.tolerance
        res.normalized = {"doc": M.decimal_str(M.to_decimal(doc_v)),
                          "system": M.decimal_str(M.to_decimal(sys_v))}
        if doc_v is None and sys_v is None:
            res.status = "NOT_APPLICABLE"
            res.message = f"No data present for {chk.field_name}."
        elif doc_v is None:
            res.status = "NEEDS_REVIEW"
            res.message = (f"No truth document for {chk.field_name}; "
                           f"cannot verify system value '{sys_v}'.")
        elif sys_v is None:
            res.status = "NEEDS_REVIEW"
            res.message = f"No system value to check against the document."
        elif R.compare_numeric(doc_v, sys_v, chk.tolerance):
            res.status = "PASS"
            res.message = chk.message_pass or (
                f"Document matches system within {chk.tolerance}.")
        else:
            # Informational flag, not a QC failure (loan docs are truth).
            res.status = "FLAG"
            res.severity = "INFO"
            res.message = chk.message_fail or (
                f"{chk.field_name}: document (truth) says '{doc_v}' "
                f"but system says '{sys_v}' — system data out of sync.")

    elif chk.kind == "agree_doc_categorical":
        # 003d: two independently-extracted DOCUMENT values -- never a system
        # source on either side (that's what keeps 001b's source-independence
        # guard meaningful for agree_categorical; this kind simply never
        # reads sources{}). QC phase (see _phase_for -- this kind is absent
        # from its RECONCILE-inference tuple), so a genuine mismatch is a
        # real defect in the closing package itself, not "system out of
        # sync" -- FAIL, not the informational FLAG agree_categorical
        # produces on disagreement.
        sv2 = loan.get(chk.compare_field_name)
        doc_a, doc_b = sv.doc, sv2.doc
        res.inputs = {"doc": doc_a, "compare_doc": doc_b}
        if doc_a is None and doc_b is None:
            res.status = "NOT_APPLICABLE"
            res.message = f"No data present for {chk.field_name} or {chk.compare_field_name}."
        elif doc_a is None or doc_b is None:
            # Same honest "ambiguous absence -> human" semantics every other
            # kind uses. NOT automatic: the generic post-dispatch block below
            # only auto-tags RECONCILE-phase NEEDS_REVIEW; this kind is QC
            # phase, so review_reason MUST be set explicitly here or
            # disposition would silently disagree with this result's status.
            res.status = "NEEDS_REVIEW"
            res.review_reason = "SOURCE_INCOMPLETE"
            res.message = (f"Only one of {chk.field_name}/{chk.compare_field_name} "
                           f"has a value -- cannot compare.")
        else:
            dn = R.normalize(chk.normalizer, doc_a)
            dbn = R.normalize(chk.normalizer, doc_b)
            res.normalized = {"doc": dn, "compare_doc": dbn}
            if dn == dbn:
                res.status = "PASS"
                res.message = chk.message_pass or "Documents agree."
            else:
                res.status = "FAIL"
                res.message = chk.message_fail or (
                    f"{chk.field_name} says '{doc_a}' but {chk.compare_field_name} "
                    f"says '{doc_b}' -- documents disagree.")

    elif chk.kind == "agree_doc_numeric":
        # Numeric counterpart to agree_doc_categorical -- same UNSPECIFIED-
        # tolerance honesty guard as agree_numeric/ratio_threshold.
        if chk.tolerance == "UNSPECIFIED":
            res.status = "NEEDS_REVIEW"
            res.review_reason = "UNSPECIFIED_THRESHOLD"
            res.message = (f"Rule tolerance for {chk.field_name} was not stated in the "
                           f"source rule text -- needs SME input before this check can run.")
            return res
        sv2 = loan.get(chk.compare_field_name)
        doc_a, doc_b = sv.doc, sv2.doc
        res.inputs = {"doc": doc_a, "compare_doc": doc_b}
        res.tolerance = chk.tolerance
        if doc_a is None and doc_b is None:
            res.status = "NOT_APPLICABLE"
            res.message = f"No data present for {chk.field_name} or {chk.compare_field_name}."
        elif doc_a is None or doc_b is None:
            res.status = "NEEDS_REVIEW"
            res.review_reason = "SOURCE_INCOMPLETE"
            res.message = (f"Only one of {chk.field_name}/{chk.compare_field_name} "
                           f"has a value -- cannot compare.")
        else:
            res.normalized = {"doc": M.decimal_str(M.to_decimal(doc_a)),
                              "compare_doc": M.decimal_str(M.to_decimal(doc_b))}
            if R.compare_numeric(doc_a, doc_b, chk.tolerance):
                res.status = "PASS"
                res.message = chk.message_pass or (
                    f"Documents agree within {chk.tolerance}.")
            else:
                res.status = "FAIL"
                res.message = chk.message_fail or (
                    f"{chk.field_name} says '{doc_a}' but {chk.compare_field_name} "
                    f"says '{doc_b}' -- documents disagree beyond tolerance {chk.tolerance}.")

    elif chk.kind == "predicate":
        # 003a FR-001/002/003: a missing (None) truth value is NOT exempted
        # via a blanket NOT_APPLICABLE here -- it flows into is_true/is_present's
        # own logic below. (The prior blanket early-return was the bug
        # p0/experiment_002a/RESULTS.md found: it pre-empted is_present ever
        # seeing the exact missing-value case the MISSING archetype exists to
        # catch.)
        #
        # 015 Issue 2 (2026-07-28, specs/015-loan-data-capture-and-gating-fix):
        # the two predicates are NOT symmetric on None, and that's intentional.
        # is_present is checking for absence, so a genuinely-missing value
        # (None) correctly FAILs it -- that's the field provably not being
        # there. is_true is checking a truth value; a missing value there
        # means we don't know whether the condition is true or false, not
        # that it's false -- so it must resolve to NEEDS_REVIEW /
        # APPLICABILITY_UNKNOWN instead of a false-positive FAIL.
        res.inputs = {"doc": sv.doc}
        if chk.predicate == "is_true" and sv.doc is None:
            res.status = "NEEDS_REVIEW"
            res.review_reason = "APPLICABILITY_UNKNOWN"
            res.message = (f"No data present for {chk.field_name} -- cannot determine "
                            f"whether this condition is true or false; needs SME review.")
            return res
        if chk.predicate == "is_true":
            ok = sv.doc is True
        elif chk.predicate == "is_present":
            ok = sv.doc is not None and str(sv.doc).strip() != ""
        else:
            raise ValueError(f"unknown predicate '{chk.predicate}'")
        res.status = "PASS" if ok else "FAIL"
        res.message = (chk.message_pass if ok else chk.message_fail) or (
            "Predicate satisfied." if ok else f"Predicate failed: {chk.predicate}")

    elif chk.kind == "ratio_threshold":
        # The bit-exact money moment: a derived ratio compared to a boundary.
        if chk.threshold == "UNSPECIFIED":
            # Same honesty guard as agree_numeric's tolerance, above -- the
            # compiler correctly refused to invent a threshold the source
            # row didn't state. Must surface to a human, never
            # NOT_APPLICABLE (that reads as "no data," not "rule
            # incomplete") and never crash M.to_decimal("UNSPECIFIED").
            res.status = "NEEDS_REVIEW"
            res.review_reason = "UNSPECIFIED_THRESHOLD"
            res.message = (f"Rule threshold for {chk.field_name} was not stated in the "
                           f"source rule text -- needs SME input before this check can run.")
            return res
        if chk.ratio == "ltv":
            la = loan.facts.get("loan_amount")
            pv = loan.facts.get("property_value")
            if la is None or pv is None:
                res.status = "NOT_APPLICABLE"
                res.message = "LTV facts not present for this loan."
                return res
            value = M.ltv_percent(la, pv)
            res.inputs = {"loan_amount": M.decimal_str(M.money(la)),
                          "property_value": M.decimal_str(M.money(pv))}
        elif chk.ratio == "dti":
            md = loan.facts.get("monthly_debts")
            mi = loan.facts.get("monthly_income")
            if md is None or mi is None:
                res.status = "NOT_APPLICABLE"
                res.message = "DTI facts not present for this loan."
                return res
            value = M.dti_percent(md, mi)
            res.inputs = {"monthly_debts": M.decimal_str(M.money(md)),
                          "monthly_income": M.decimal_str(M.money(mi))}
        elif chk.ratio == "field_value":
            # 003b FR-001/002: a single-field numeric floor/ceiling (e.g. a
            # minimum credit score) is not a ratio -- compare the field's own
            # truth value directly against the threshold. No ratio is
            # computed, so no PERCENT_SCALE quantize (that scale is specific
            # to a computed LTV/DTI percent, not an arbitrary field value).
            if sv.doc is None:
                res.status = "NOT_APPLICABLE"
                res.message = f"No value present for {chk.field_name}."
                return res
            value = M.to_decimal(sv.doc)
            res.inputs = {chk.field_name: sv.doc}
        else:
            raise ValueError(f"unknown ratio '{chk.ratio}'")
        thr = M.to_decimal(chk.threshold)
        res.compared_value = M.decimal_str(value)
        res.rounding = "ROUND_HALF_EVEN"
        op = chk.operator
        ok = (value <= thr) if op == "<=" else (value < thr) if op == "<" \
            else (value >= thr) if op == ">=" else (value > thr)
        res.status = "PASS" if ok else "FAIL"
        res.tolerance = chk.threshold
        res.message = (chk.message_pass if ok else chk.message_fail) or (
            f"{chk.ratio.upper()} {value}% {op} {thr}%")

    else:
        raise ValueError(f"unknown check kind '{chk.kind}'")

    # 004: open-vocabulary review_reason, tagged generically by phase+status --
    # ONE rule here, not one per check-kind, so a future kind that produces a
    # QC-phase FAIL/WARNING or a RECONCILE-phase NEEDS_REVIEW is tagged
    # automatically with zero changes to this block. A FLAG never matches
    # either condition, so it never gets a reason (Principle V).
    if res.phase == PHASE_QC and res.status in ("FAIL", "WARNING"):
        res.review_reason = "EXCEPTION"
    elif res.phase == PHASE_RECONCILE and res.status == "NEEDS_REVIEW":
        res.review_reason = "SOURCE_INCOMPLETE"

    # Confidence gate (ruling #8): a PASS that relied on the truth document is
    # NOT auto-cleared if that extraction was low-confidence — it goes to a
    # human. Determinism must not confidently clear a loan whose truth value we
    # don't trust.
    if (res.status == "PASS" and sv.doc is not None
            and sv.doc_confidence is not None
            and sv.doc_confidence < confidence_floor):
        res.status = "NEEDS_REVIEW"
        res.review_reason = "LOW_CONFIDENCE"
        res.message = (f"Auto-clear withheld: extraction confidence "
                       f"{sv.doc_confidence} < floor {confidence_floor}.")
    return res


@dataclass
class RunResult:
    loan_id: str
    ruleset_id: str
    ruleset_version: int
    ruleset_sha256: str
    engine_version: str
    results: List[CheckResult] = field(default_factory=list)

    # --- the two product steps, made explicit ------------------------------
    @property
    def reconcile_results(self) -> List[CheckResult]:
        """Step 1: doc (truth) vs system comparisons."""
        return [r for r in self.results if r.phase == PHASE_RECONCILE]

    @property
    def qc_results(self) -> List[CheckResult]:
        """Step 2: policy/compliance rules."""
        return [r for r in self.results if r.phase == PHASE_QC]

    @property
    def flags(self) -> List[CheckResult]:
        """Step-1 informational flags: system data out of sync with the truth
        document. These DO NOT fail QC — the docs are truth, QC runs on them.
        They tell the lender to fix their system of record."""
        return [r for r in self.reconcile_results if r.status == "FLAG"]

    # Back-compat alias
    @property
    def discrepancies(self) -> List[CheckResult]:
        return self.flags

    @property
    def qc_failures(self) -> List[CheckResult]:
        """Step-2 rule failures (e.g. LTV over limit, note unsigned) — the ONLY
        pass/fail. These are the exceptions a human must judge."""
        return [r for r in self.qc_results if r.status in ("FAIL", "WARNING")]

    @property
    def exceptions(self) -> List[CheckResult]:
        """The real exceptions: QC failures only. Flags are not exceptions."""
        return self.qc_failures

    @property
    def needs_review(self) -> List[CheckResult]:
        return [r for r in self.results if r.status == "NEEDS_REVIEW"]

    @property
    def auto_cleared(self) -> bool:
        """Auto-clear requires QC to pass and nothing needing human review.
        Informational FLAGs (system out of sync with the truth doc) do NOT
        block auto-clear — the loan itself is fine; the lender's data isn't."""
        return not self.qc_failures and not self.needs_review

    # --- 004: the composed, per-loan disposition ----------------------------
    @property
    def review_reasons(self) -> Set[str]:
        """The open, multi-label set of reasons this loan needs review --
        deduplicated union of every contributing CheckResult.review_reason.
        A loan can carry more than one simultaneous concern; none is
        privileged over another at this layer (data-model.md)."""
        return {r.review_reason for r in self.results if r.review_reason}

    @property
    def disposition(self) -> str:
        """AUTO_CLEARED | NEEDS_REVIEW -- provably equivalent to auto_cleared
        by construction: review_reasons is non-empty exactly when qc_failures
        or needs_review is non-empty (spec.md FR-006)."""
        return "NEEDS_REVIEW" if self.review_reasons else "AUTO_CLEARED"

    def to_dict(self, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """`extra`: an optional caller-supplied mapping merged into the
        output (014, serialization-only). A later, read-only, per-loan
        explanatory-summary artifact is persisted this way -- the engine
        itself stays a pure function of (ruleset, loan); it never computes,
        names, or imports that artifact. Only the caller that generates it
        (outside this module) ever spells out the key it writes here, so
        this file carries zero coupling to that artifact's name or module --
        not merely "the engine doesn't call it" but "this file's source text
        doesn't even mention it", the strongest form of the one-way boundary
        that feature's own spec requires."""
        d = {
            "loan_id": self.loan_id,
            "ruleset_id": self.ruleset_id,
            "ruleset_version": self.ruleset_version,
            "ruleset_sha256": self.ruleset_sha256,
            "engine_version": self.engine_version,
            "results": [r.to_dict() for r in self.results],
            "disposition": self.disposition,
            "review_reasons": sorted(self.review_reasons),
            "summary": {
                "total": len(self.results),
                "reconcile_discrepancies": len(self.discrepancies),
                "qc_failures": len(self.qc_failures),
                "fail": sum(1 for r in self.results if r.status == "FAIL"),
                "warning": sum(1 for r in self.results if r.status == "WARNING"),
                "needs_review": len(self.needs_review),
                "auto_cleared": self.auto_cleared,
            },
        }
        if extra:
            d.update(extra)
        return d


def run(loan: CanonicalLoan, ruleset: Ruleset,
        confidence_floor: float = DEFAULT_CONFIDENCE_FLOOR) -> RunResult:
    """Evaluate every check in the signed ruleset against the loan.

    Pure, deterministic, ordered by the ruleset's check order. The ruleset is
    identified in the result BY HASH, so the exact rules that judged this loan
    are forever recoverable.
    """
    results = [_eval_check(loan, c, confidence_floor) for c in ruleset.checks]
    return RunResult(
        loan_id=loan.loan_id,
        ruleset_id=ruleset.ruleset_id,
        ruleset_version=ruleset.version,
        ruleset_sha256=ruleset.sha256(),
        engine_version=ruleset.engine_version,
        results=results,
    )
