"""remove_out_of_scope_fact.py: dropping loan_product_type (Freddie Mac,
no Freddie Mac corpus to ever cite it from) from the vocabulary, 2026-07-27."""
import os
import sys

import pytest

_P0 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _P0 not in sys.path:
    sys.path.insert(0, _P0)

from qc_engine.compiler import fact_vocabulary as FV  # noqa: E402
from qc_engine.compiler import remove_out_of_scope_fact as R  # noqa: E402

_REPO_ROOT = os.path.dirname(_P0)
VOCAB_DIR = os.path.join(_REPO_ROOT, "storage", "fact_vocabulary")


def test_real_v6_artifact_no_longer_has_loan_product_type():
    v5 = FV.load(os.path.join(VOCAB_DIR, "v5.json"))
    v6 = FV.load(os.path.join(VOCAB_DIR, "v6.json"))
    assert "loan_product_type" in {f.canonical_field_name for f in v5.facts}
    assert "loan_product_type" not in {f.canonical_field_name for f in v6.facts}
    assert len(v6.facts) == len(v5.facts) - 1


def test_real_v6_every_other_fact_unchanged_from_v5():
    v5 = FV.load(os.path.join(VOCAB_DIR, "v5.json"))
    v6 = FV.load(os.path.join(VOCAB_DIR, "v6.json"))
    v5_by_name = {f.canonical_field_name: f for f in v5.facts}
    for fact in v6.facts:
        assert fact == v5_by_name[fact.canonical_field_name]


def test_real_v6_still_carries_honest_placeholder_signature():
    v6 = FV.load(os.path.join(VOCAB_DIR, "v6.json"))
    assert v6.signed_by == "NOT-A-REAL-SME-pending-kayla-review"


def test_removing_a_fact_not_present_refuses(tmp_path, monkeypatch):
    vocab = FV.FactVocabulary(version=1, facts=[
        FV.CanonicalFact(id="fact-other", canonical_field_name="other",
                         data_type="boolean", description="d"),
    ])
    dir_path = str(tmp_path / "fact_vocabulary")
    FV.save(vocab, os.path.join(dir_path, "v1.json"))
    monkeypatch.setattr(R, "VOCAB_DIR", dir_path)
    with pytest.raises(SystemExit):
        R.main()
