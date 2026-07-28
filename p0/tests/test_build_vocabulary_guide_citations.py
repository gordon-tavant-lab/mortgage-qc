"""Unit tests for the investor-mismatch guard in
build_vocabulary_guide_citations.py -- the fix for the cross-investor
citation bug a /g-os-judge review caught on v4's loan_product_type
(Freddie Mac fact, Fannie Mae citations)."""
import os
import sys

_P0 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _P0 not in sys.path:
    sys.path.insert(0, _P0)

from qc_engine.compiler import build_vocabulary_guide_citations as C  # noqa: E402
from qc_engine.compiler import fact_vocabulary as FV  # noqa: E402


def _fact(description):
    return FV.CanonicalFact(id="fact-x", canonical_field_name="x",
                            data_type="boolean", description=description)


def test_freddie_mac_description_flags_mismatch_against_fannie_corpus():
    fact = _fact("The specific Freddie Mac loan product or program type applicable.")
    assert C._investor_mismatch(fact, "Fannie Mae") is True


def test_fannie_mae_description_no_mismatch():
    fact = _fact("Whether Fannie Mae DU Validation Service relief applies.")
    assert C._investor_mismatch(fact, "Fannie Mae") is False


def test_fha_va_usda_mentions_are_not_treated_as_mismatch():
    """Fannie's own Selling Guide legitimately discusses government-insured
    program eligibility -- these must NOT trigger the guard."""
    for desc in (
        "The specific FHA loan purpose or product type classification.",
        "Whether VA residual income requirements were met.",
        "USDA household income within the moderate-income limit.",
    ):
        assert C._investor_mismatch(_fact(desc), "Fannie Mae") is False


def test_no_mismatch_when_description_is_silent_on_investor():
    fact = _fact("Indicates whether an appraisal report is present in the loan file.")
    assert C._investor_mismatch(fact, "Fannie Mae") is False


def test_guard_is_symmetric_if_corpus_were_freddie_mac():
    """Same investor named as the corpus itself -- no mismatch."""
    fact = _fact("The specific Freddie Mac loan product or program type applicable.")
    assert C._investor_mismatch(fact, "Freddie Mac") is False
