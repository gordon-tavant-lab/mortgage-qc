"""002g FR-008 -- golden-panel replay over the 5 real from_docs loans:
a vocabulary/ruleset change ships only after the panel proves exactly what it
flips (Sanctioned's replay-all-personas precedent, spec Research source 5)."""
import copy
import os
import sys

_P0 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _P0 not in sys.path:
    sys.path.insert(0, _P0)
_FROM_DOCS = os.path.join(_P0, "fixtures", "from_docs")
if _FROM_DOCS not in sys.path:
    sys.path.insert(0, _FROM_DOCS)

from fixture_loader import load_canonical_loan  # noqa: E402
from qc_engine.model import SourceValue  # noqa: E402
from qc_engine.replay import replay  # noqa: E402
from qc_engine.ruleset import Check, Ruleset  # noqa: E402


def _panel():
    loans = []
    for n in ("01", "02", "03", "04", "05"):
        loan = load_canonical_loan(os.path.join(_FROM_DOCS, f"loan_{n}.json"))
        # The canonical gift fact isn't in the extraction contract yet
        # (002e's own documented assumption) -- inject per the known facts:
        # loan 01 really used no gift funds (doc_present_gift_letter=false).
        used = "false" if loan.facts.get("doc_present_gift_letter") == "false" else "true"
        loan.fields["gift_funds_used"] = SourceValue(doc=used)
        loans.append(loan)
    return loans


def _gift_check(applies_if=None):
    return Check(
        id="chk-gift-doc", name="Gift documentation complete",
        field_name="gift_funds_source_documented", kind="predicate",
        severity="CRITICAL", predicate="is_true", applies_if=applies_if,
        message_pass="Gift documentation complete.",
        message_fail="Gift funds paper trail not in file.",
    )


def _stable_check():
    return Check(
        id="chk-note-signed", name="Note is signed",
        field_name="note_signed", kind="predicate",
        severity="CRITICAL", predicate="is_true",
        message_pass="Note signed.", message_fail="Note not signed.",
    )


def _ruleset(checks, version):
    return Ruleset(ruleset_id="rs-replay-test", version=version, checks=checks)


def test_replay_names_exactly_the_expected_flips_and_nothing_else():
    """criteria.md #6: adding the gift applies_if flips exactly the no-gift
    loans' gift check (whatever it resolved to before -> NOT_APPLICABLE) and
    flips nothing else on the panel."""
    loans = _panel()
    old = _ruleset([_gift_check(applies_if=None), _stable_check()], version=1)
    new = _ruleset([_gift_check(applies_if=[
        {"field_name": "gift_funds_used", "operator": "==", "value": "true"},
    ]), _stable_check()], version=2)

    report = replay(loans, old, new)
    assert report.loans_replayed == 5
    assert report.only_in_old == [] and report.only_in_new == []

    no_gift_loans = {l.loan_id for l in loans
                     if l.fields["gift_funds_used"].doc == "false"}
    assert no_gift_loans, "panel must contain at least one no-gift loan (loan 01)"

    flipped = {(f.loan_id, f.check_id) for f in report.flips}
    # every no-gift loan's gift check flips to NOT_APPLICABLE...
    for loan_id in no_gift_loans:
        assert (loan_id, "chk-gift-doc") in flipped
    # ...and nothing else moves: no stable-check flips, no gift-loan flips
    for f in report.flips:
        assert f.check_id == "chk-gift-doc"
        assert f.loan_id in no_gift_loans
        assert f.new_status == "NOT_APPLICABLE"


def test_identical_rulesets_produce_zero_flips():
    loans = _panel()
    rs = _ruleset([_gift_check(), _stable_check()], version=1)
    report = replay(loans, rs, copy.deepcopy(rs))
    assert report.flips == []
    assert report.checks_compared == len(loans) * 2


def test_check_set_membership_changes_are_reported_not_hidden():
    loans = _panel()
    old = _ruleset([_gift_check(), _stable_check()], version=1)
    new = _ruleset([_stable_check()], version=2)  # gift check removed
    report = replay(loans, old, new)
    assert report.only_in_old == ["chk-gift-doc"]
    assert report.only_in_new == []
    assert all(f.check_id != "chk-gift-doc" for f in report.flips)
