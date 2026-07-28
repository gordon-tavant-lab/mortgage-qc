"""
Mutation-based loan generator — ground truth BY CONSTRUCTION.

The eval gap said "we can't trust synthetic loans because we made up the answer."
This inverts that: **if WE inject the defect, we KNOW the answer — the mutation
IS the label.** No human adjudication, no real files required, for the question
that actually matters: *given the data, does the engine compute the right verdict
per the signed rule spec?*

Pipeline:
  1. build a CLEAN loan valid for the demo ruleset, with the document path and
     the system path as SEPARATE structures (so reconcile checks get genuinely
     independent inputs — the CLAUDE.md #3 independence trap, solved by control).
  2. apply a MUTATION OPERATOR (one per taxonomy archetype). Each returns
     (mutated_loan, {check_id: expected_status}) — the override is the label.
  3. compose: clean / single-defect / multi-defect / boundary samples.

Determinism: NO global random. Each loan is built from an integer seed via a
local random.Random(seed); same seed -> same loan -> same labels, forever. (The
engine itself is already bit-exact; the generator must not reintroduce
nondeterminism.)

Mutation -> archetype -> engine-kind mapping mirrors taxonomy.py, so coverage is
provably tied to the real 800-check workbook, not invented. The SME signs off
THIS mapping (a rules review), which closes Blocker 2 without real loans.

Python 3.9 compatible.
"""
from __future__ import annotations

import os
import random
import sys
from decimal import Decimal
from typing import Any, Callable, Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qc_engine.model import CanonicalLoan, SourceValue, DocCitation  # noqa: E402

# A labeled loan: the loan + the expected per-check verdicts (the ground truth)
# + provenance describing exactly which mutations produced it.
LabeledLoan = Tuple[CanonicalLoan, Dict[str, str], Dict[str, Any]]

CONF_FLOOR = 0.80   # mirror engine.DEFAULT_CONFIDENCE_FLOOR


def _cite(doc: str, page: int = 1, snip: str = "") -> DocCitation:
    return DocCitation(doc_name=doc, page_num=page, segment_snippet=snip or doc)


# --------------------------------------------------------------------------- #
# Clean loan: every check PASSES. Doc path and system path are SEPARATE values
# that happen to agree — so a mutation can diverge one without touching the
# other (true independence, not a shared origin).
# --------------------------------------------------------------------------- #
_FIRST = ["John", "Marcus", "Liam", "Sophia", "Dana", "Aisha", "Noah", "Mia"]
_LAST = ["Doe", "Vance", "Chen", "Martinez", "Reed", "Okafor", "Park", "Ali"]


def build_clean(seed: int) -> CanonicalLoan:
    rng = random.Random(seed)
    first = rng.choice(_FIRST)
    last = rng.choice(_LAST)
    name = f"{first} {last}"
    ssn_last4 = f"{rng.randint(1000, 9999)}"
    ssn_full = f"{rng.randint(100,899)}-{rng.randint(10,99)}-{ssn_last4}"
    rate = f"{rng.choice(['5.750','6.000','6.125','6.500','6.750','7.000'])}"
    # LTV comfortably under the 95.000 max for a clean loan.
    value = rng.choice([300000, 350000, 400000, 500000])
    ltv_pct = rng.choice([Decimal("70"), Decimal("80"), Decimal("85"),
                          Decimal("90")])
    amount = int((Decimal(value) * ltv_pct / Decimal("100")))
    addr = f"{rng.randint(100,9999)} {rng.choice(['Maple Dr','Oak Blvd','Pine Ln','Elm Ct'])}, " \
           f"{rng.choice(['Atlanta, GA 30301','Orlando, FL 32801','Austin, TX 78701'])}"

    loan = CanonicalLoan(loan_id=f"SYN-{seed:06d}", loan_type="Conv 30yr Purchase")
    loan.facts = {"loan_amount": f"{amount}.00", "property_value": f"{value}.00"}
    loan.fields = {
        "borrower_name": SourceValue(doc=name, los=name, mismo=name,
            doc_confidence=0.99, citation=_cite("Closing_Disclosure.pdf")),
        "borrower_ssn": SourceValue(doc=f"XXX-XX-{ssn_last4}", los=ssn_full,
            mismo=ssn_full, doc_confidence=0.97,
            citation=_cite("Closing_Disclosure.pdf")),
        "note_rate": SourceValue(doc=rate, los=rate, mismo=rate,
            doc_confidence=0.98, citation=_cite("Promissory_Note.pdf")),
        "loan_amount": SourceValue(doc=str(amount), los=str(amount),
            mismo=str(amount), doc_confidence=0.99,
            citation=_cite("Promissory_Note.pdf")),
        "property_address": SourceValue(doc=addr, los=addr, mismo=addr,
            doc_confidence=0.96, citation=_cite("Appraisal.pdf")),
        "flood_zone": SourceValue(doc="Zone X", los="Zone X",
            doc_confidence=0.95, citation=_cite("Flood_Determination.pdf")),
        "note_signed": SourceValue(doc=True, doc_confidence=0.99,
            citation=_cite("Promissory_Note.pdf", 3, "/s/ signed (Seal)")),
    }
    return loan


# All checks that a fully clean loan should PASS (matches demo_ruleset ids).
CLEAN_EXPECTED: Dict[str, str] = {
    "chk-borrower-name": "PASS", "chk-borrower-ssn": "PASS",
    "chk-note-rate": "PASS", "chk-principal": "PASS",
    "chk-property-address": "PASS", "chk-flood-zone": "PASS",
    "chk-note-signed": "PASS", "chk-ltv-max": "PASS",
}


# --------------------------------------------------------------------------- #
# Source-independence guard (001b, research.md decision #2): a test-
# CONSTRUCTION discipline, not a runtime data validator. The trap it exists to
# catch is NOT "a system value computed via a transform of truth" (a mutation
# deliberately perturbing truth to construct a controlled divergence is a
# legitimate, standard test-authoring technique -- see mut_mismatch_categorical
# below, which does exactly this). The real trap is a mutation that CLAIMS to
# construct a doc-vs-system divergence but silently fails to (e.g. a copy-paste
# bug leaves system == truth unchanged) -- which would make a reconcile check's
# "does it detect a real mismatch" test pass for the wrong reason, unnoticed.
# --------------------------------------------------------------------------- #
def assert_independently_constructed(truth: Any, sources: Dict[str, Any],
                                     expect_divergent_keys: Optional[List[str]] = None) -> None:
    """Verify a reconcile-mutation fixture's claimed divergence is real.

    `expect_divergent_keys`: the `sources` keys this fixture is constructing a
    genuine mismatch for (e.g. ["los", "mismo"]). Raises if any of them is
    equal to `truth` -- the mutation failed to actually diverge, silently
    collapsing the test into a same-source comparison (CLAUDE.md #3's trap).
    """
    if not expect_divergent_keys:
        return
    for key in expect_divergent_keys:
        if sources.get(key) == truth:
            raise ValueError(
                f"assert_independently_constructed: sources['{key}'] == truth "
                f"({truth!r}) -- this mutation was supposed to construct a "
                f"genuine divergence for a mismatch test, but the system value "
                f"was left unchanged (or accidentally reset to match truth). "
                f"A reconcile check scored against this fixture would test "
                f"nothing, silently.")


# --------------------------------------------------------------------------- #
# Mutation operators. Each: (loan) -> (loan, {check_id: expected_status}, label).
# The expected_status is the GROUND TRUTH — it's what we just made true.
# Archetype ids correspond to taxonomy.py.
# --------------------------------------------------------------------------- #
def mut_mismatch_categorical(loan: CanonicalLoan, seed: int) -> Tuple[Dict[str, str], str]:
    """MISMATCH archetype: diverge the SYSTEM value from the truth DOC on a
    categorical field -> reconcile FLAG (informational, not a QC failure)."""
    rng = random.Random(seed)
    sv = loan.fields["property_address"]
    # change only the system side; doc (truth) stays
    sv.los = str(sv.doc) + f" UNIT {rng.randint(1,9)}"
    sv.mismo = sv.los
    assert_independently_constructed(sv.doc, sv.sources, expect_divergent_keys=["los", "mismo"])
    return {"chk-property-address": "FLAG"}, "MISMATCH:address system desync"


def mut_mismatch_numeric(loan: CanonicalLoan, seed: int) -> Tuple[Dict[str, str], str]:
    """MISMATCH on a numeric field (note rate) beyond tolerance -> FLAG."""
    sv = loan.fields["note_rate"]
    bumped = str(Decimal(str(sv.doc)) + Decimal("0.125"))
    sv.los = bumped
    sv.mismo = bumped
    assert_independently_constructed(sv.doc, sv.sources, expect_divergent_keys=["los", "mismo"])
    return {"chk-note-rate": "FLAG"}, "MISMATCH:note_rate system desync"


def mut_inaccurate(loan: CanonicalLoan, seed: int) -> Tuple[Dict[str, str], str]:
    """INACCURATE archetype: system holds a wrong SSN last-4 vs the truth doc
    -> reconcile FLAG. The check normalizes to last-4, so the divergence MUST be
    in the last 4 digits to be a real mismatch (a different prefix alone still
    matches)."""
    from qc_engine.reconcile import norm_ssn_last4
    sv = loan.fields["borrower_ssn"]
    true_last4 = norm_ssn_last4(sv.doc)
    wrong_last4 = f"{(int(true_last4) + 1234) % 10000:04d}"
    wrong = f"555-66-{wrong_last4}"
    sv.los = wrong
    sv.mismo = wrong
    assert_independently_constructed(sv.doc, sv.sources, expect_divergent_keys=["los", "mismo"])
    return {"chk-borrower-ssn": "FLAG"}, "INACCURATE:ssn last4 wrong in system"


def mut_unsigned(loan: CanonicalLoan, seed: int) -> Tuple[Dict[str, str], str]:
    """UNSIGNED archetype: the note is not signed -> QC FAIL."""
    loan.fields["note_signed"] = SourceValue(
        doc=False, doc_confidence=0.95,
        citation=_cite("Promissory_Note.pdf", 3, "[SIGNATURE LINE BLANK]"))
    return {"chk-note-signed": "FAIL"}, "UNSIGNED:note signature absent"


def mut_threshold_over(loan: CanonicalLoan, seed: int) -> Tuple[Dict[str, str], str]:
    """THRESHOLD archetype: push LTV strictly over the 95.000 program max -> FAIL.
    e.g. 96% of value."""
    value = Decimal(loan.facts["property_value"])
    over_amt = (value * Decimal("96") / Decimal("100")).quantize(Decimal("1."))
    loan.facts["loan_amount"] = f"{over_amt}"
    loan.fields["loan_amount"] = SourceValue(
        doc=str(over_amt), los=str(over_amt), mismo=str(over_amt),
        doc_confidence=0.99, citation=_cite("Promissory_Note.pdf"))
    return {"chk-ltv-max": "FAIL", "chk-principal": "PASS"}, "THRESHOLD:LTV 96% > 95% max"


def mut_low_confidence(loan: CanonicalLoan, seed: int) -> Tuple[Dict[str, str], str]:
    """Confidence gate (judge ruling #8): a PASS relying on a low-confidence
    extraction must NOT auto-clear -> NEEDS_REVIEW. Tests the gate, not a defect
    archetype per se but a critical safety behavior."""
    sv = loan.fields["note_rate"]
    sv.doc_confidence = 0.55   # below the 0.80 floor
    return {"chk-note-rate": "NEEDS_REVIEW"}, "CONFIDENCE:note_rate extraction below floor"


# Boundary: LTV EXACTLY on 95.000 -> PASS (the bit-exact money case). Not a
# defect; included to stress the boundary the float-vs-Decimal demo cares about.
def mut_boundary_exact(loan: CanonicalLoan, seed: int) -> Tuple[Dict[str, str], str]:
    value = Decimal(loan.facts["property_value"])
    exact = (value * Decimal("95.000") / Decimal("100"))
    loan.facts["loan_amount"] = f"{exact}"
    loan.fields["loan_amount"] = SourceValue(
        doc=str(exact), los=str(exact), mismo=str(exact),
        doc_confidence=0.99, citation=_cite("Promissory_Note.pdf"))
    return {"chk-ltv-max": "PASS", "chk-principal": "PASS"}, "BOUNDARY:LTV exactly 95.000"


# Registry: archetype -> operator. Mirrors taxonomy archetypes that the demo
# ruleset can actually evaluate. (MISSING/EXPIRED/INCOMPLETE/POLICY all reduce to
# predicate FAILs; UNSIGNED is the concrete predicate the demo ruleset carries —
# additional predicate fields are added as the ruleset widens.)
MUTATIONS: Dict[str, Callable[[CanonicalLoan, int], Tuple[Dict[str, str], str]]] = {
    "MISMATCH_CAT": mut_mismatch_categorical,
    "MISMATCH_NUM": mut_mismatch_numeric,
    "INACCURATE": mut_inaccurate,
    "UNSIGNED": mut_unsigned,
    "THRESHOLD": mut_threshold_over,
    "CONFIDENCE": mut_low_confidence,
    "BOUNDARY": mut_boundary_exact,
}


def make_clean(seed: int) -> LabeledLoan:
    loan = build_clean(seed)
    return loan, dict(CLEAN_EXPECTED), {"kind": "clean", "mutations": []}


def make_single(seed: int, archetype: str) -> LabeledLoan:
    """A clean loan with exactly one mutation applied. Label = clean overridden
    by the mutation's expected verdicts."""
    loan = build_clean(seed)
    expected = dict(CLEAN_EXPECTED)
    overrides, label = MUTATIONS[archetype](loan, seed)
    expected.update(overrides)
    return loan, expected, {"kind": "single", "mutations": [label]}


def make_multi(seed: int, archetypes: List[str]) -> LabeledLoan:
    """Compose several independent mutations on distinct fields. Each override
    layers onto the label; later overrides on the same check_id win (we choose
    archetypes that touch distinct checks to avoid ambiguity)."""
    loan = build_clean(seed)
    expected = dict(CLEAN_EXPECTED)
    labels = []
    for a in archetypes:
        overrides, label = MUTATIONS[a](loan, seed)
        expected.update(overrides)
        labels.append(label)
    return loan, expected, {"kind": "multi", "mutations": labels}


# Archetypes that touch DISTINCT checks -> safe to compose in multi-defect loans.
_DISTINCT_FIELD_MUTS = ["MISMATCH_CAT", "UNSIGNED", "THRESHOLD"]


def generate(n: int, start_seed: int = 1000) -> List[LabeledLoan]:
    """Deterministic mix: ~40% clean, ~45% single-defect (round-robin across
    archetypes), ~15% multi-defect. Same (n, start_seed) -> same set."""
    loans: List[LabeledLoan] = []
    archs = list(MUTATIONS.keys())
    for i in range(n):
        seed = start_seed + i
        bucket = i % 20
        if bucket < 8:                       # 40% clean
            loans.append(make_clean(seed))
        elif bucket < 17:                    # 45% single-defect
            arch = archs[i % len(archs)]
            loans.append(make_single(seed, arch))
        else:                                # 15% multi-defect
            k = 2 + (i % 2)                  # 2 or 3 mutations
            loans.append(make_multi(seed, _DISTINCT_FIELD_MUTS[:k]))
    return loans


def main() -> int:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    loans = generate(n)
    from collections import Counter
    kinds = Counter(prov["kind"] for _, _, prov in loans)
    print(f"\n=== GENERATED {len(loans)} labeled loans (ground truth by construction) ===")
    print(f"  mix: {dict(kinds)}")
    for loan, expected, prov in loans[:8]:
        defects = [k for k, v in expected.items() if v != "PASS"]
        print(f"  {loan.loan_id}  {prov['kind']:<6}  "
              f"non-PASS: {defects if defects else '—'}  "
              f"{'; '.join(prov['mutations'])}")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
