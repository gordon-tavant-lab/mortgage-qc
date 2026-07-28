"""
010a -- program applicability gating.

Parses the real AMQ workbook's own machine-readable program signals -- the
Exception Code prefix (primary, 79% of real rows: O-FHA-/O-VA-/O-RHS-/O-FRD-/
O-FNM-) and the existing SQL WHERE-clause gating (secondary, 615 rows) -- so a
compiled check fires only for the loan program/situation it actually applies
to. Automated generalization of p0/fixtures/ruleset_defects.py's hand-derived
_check_applies/_PROGRAM_GATED gating, built from real-row metadata instead of
by hand. See output/RULE-PROGRAM-GATING-FINDINGS.md for the underlying
evidence every fixture below is anchored on.

US1: Exception Code prefix -> program mapping; a gated ruleset build for a
loan includes only checks whose program matches; the Fannie/Freddie
"Conventional" ambiguity is surfaced inspectably, never silently guessed.
US2: the secondary SQL-clause mechanism narrows further where encoded, never
loosens what the primary signal already excluded.
US3: taxonomy.py reads every sheet of a workbook, not only the first.

Run from p0/:  python -m pytest tests/test_program_applicability_gating.py -v
Python 3.9 compatible.
"""
from __future__ import annotations

import os
import sys

_P0 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _P0)
sys.path.insert(0, os.path.join(_P0, "eval_synth"))

from qc_engine.model import CanonicalLoan, SourceValue
from qc_engine.compiler import program_gating as G

# The 5 real loan_type strings actually used by the 5 synthetic loans
# (build_fixtures.py / demo/syn/loan 0{1-5}) -- not invented for this test.
LOAN_TYPES = {
    "conventional": "Conventional Purchase",
    "fha": "FHA Purchase",
    "va": "VA Purchase",
    "freddie": "Freddie Mac Cash-Out Refi",
    "usda": "USDA RHS 502 Guaranteed",
}


def _loan(kind: str) -> CanonicalLoan:
    return CanonicalLoan(loan_id=f"LN-GATE-{kind.upper()}", loan_type=LOAN_TYPES[kind])


# --- T003: Exception Code prefix -> program, all 5 confirmed mappings ------
def test_exception_code_prefix_maps_to_correct_program():
    # Real codes, verbatim from output/RULE-PROGRAM-GATING-FINDINGS.md.
    assert G.parse_exception_code_prefix("O-FHA-15293") == "FHA"
    assert G.parse_exception_code_prefix("O-VA-15751") == "VA"
    assert G.parse_exception_code_prefix("O-RHS-15627") == "USDA"
    assert G.parse_exception_code_prefix("O-FRD-14083") == "Freddie Mac"
    assert G.parse_exception_code_prefix("O-FNM-15304") == "Fannie Mae"


def test_exception_code_prefix_unrecognized_returns_none():
    # Regulation-category / administrative prefixes are not program tags.
    assert G.parse_exception_code_prefix("O-TILA-15100") is None
    assert G.parse_exception_code_prefix("Critical") is None


def test_sonyma_prefix_maps_correctly_despite_space_delimited_format():
    # SONYMA's real codes are space-delimited, never dash-suffixed -- a
    # distinct format from the other 5 (all dash-delimited). Real values,
    # verbatim from the workbook: "SONYMA", "SONYMA HDFC", "SONYMA Tax ".
    assert G.parse_exception_code_prefix("SONYMA") == "SONYMA"
    assert G.parse_exception_code_prefix("SONYMA HDFC") == "SONYMA"
    assert G.parse_exception_code_prefix("SONYMA Tax ") == "SONYMA"
    assert G.parse_exception_code_prefix("SONYMA Cap Repair") == "SONYMA"


# --- T004/T005: gated ruleset build -- applies only to the matching loan ---
def test_fha_tagged_check_applies_only_to_fha_loan():
    applicability = G.Applicability(program="FHA")
    for kind, loan in [(k, _loan(k)) for k in LOAN_TYPES]:
        expected = kind == "fha"
        assert G.applies_to(loan, applicability) == expected, kind


def test_va_tagged_check_applies_only_to_va_loan():
    applicability = G.Applicability(program="VA")
    for kind, loan in [(k, _loan(k)) for k in LOAN_TYPES]:
        assert G.applies_to(loan, applicability) == (kind == "va"), kind


def test_usda_tagged_check_applies_only_to_usda_loan():
    applicability = G.Applicability(program="USDA")
    for kind, loan in [(k, _loan(k)) for k in LOAN_TYPES]:
        assert G.applies_to(loan, applicability) == (kind == "usda"), kind


def test_freddie_tagged_check_applies_only_to_freddie_loan():
    # "conventional" (bare "Conventional Purchase", no named GSE) is excluded
    # from this loop -- it's the same Fannie/Freddie ambiguity as above, just
    # from the Freddie side, and is its own dedicated assertion below.
    applicability = G.Applicability(program="Freddie Mac")
    for kind in ("fha", "va", "usda", "freddie"):
        assert G.applies_to(_loan(kind), applicability) == (kind == "freddie"), kind


def test_freddie_tagged_check_against_conventional_loan_is_also_ambiguous():
    # The ambiguity cuts both ways: a bare "Conventional" loan_type could be
    # either GSE, so a Freddie-tagged check is exactly as ambiguous against it
    # as the Fannie-tagged case above -- not silently resolved to False either.
    applicability = G.Applicability(program="Freddie Mac")
    assert G.applies_to(_loan("conventional"), applicability) is G.AMBIGUOUS


# --- T006: the Fannie/Freddie "Conventional" ambiguity is surfaced, not guessed
def test_fannie_tagged_check_against_conventional_loan_is_ambiguous_not_guessed():
    applicability = G.Applicability(program="Fannie Mae")
    conventional = _loan("conventional")
    result = G.applies_to(conventional, applicability)
    # Must be an explicit, inspectable ambiguity marker -- never a bare bool.
    assert result is G.AMBIGUOUS
    assert result is not True and result is not False


def test_fannie_tagged_check_against_other_programs_is_unambiguously_excluded():
    applicability = G.Applicability(program="Fannie Mae")
    for kind in ("fha", "va", "usda", "freddie"):
        assert G.applies_to(_loan(kind), applicability) is False, kind


def test_sonyma_tagged_check_applies_to_none_of_the_5_synthetic_loans():
    # No synthetic loan is SONYMA-tagged (per Gordon's explicit direction,
    # 2026-07-20: add SONYMA to the table now, untested against a real
    # fixture -- same posture as the still-unconfirmed Jumbo tag). This test
    # proves the untested case still behaves correctly (unambiguously
    # excluded, not silently matched) rather than leaving it unverified.
    applicability = G.Applicability(program="SONYMA")
    for kind in LOAN_TYPES:
        assert G.applies_to(_loan(kind), applicability) is False, kind


# --- T007: untagged row (no program prefix, no SQL clause) fails open ------
def test_untagged_check_applies_to_every_program():
    applicability = G.Applicability(program=None)
    for kind in LOAN_TYPES:
        assert G.applies_to(_loan(kind), applicability) is True, kind


# --- T013: SQL clause narrows further on top of the program match ----------
def test_sql_clause_narrows_program_matched_check_by_property_type():
    # Real clause, verbatim: O-FNM- prefix + a property-type-narrowed WHERE.
    # Uses an UNAMBIGUOUSLY Fannie-Mae-tagged loan_type (not the
    # LOAN_TYPES["conventional"] fixture, which is the deliberately ambiguous
    # case covered by its own dedicated test above) so this test isolates
    # US2's narrowing behavior from US1's ambiguity-surfacing behavior.
    clause = ("SELECT DISTINCT Loans.LoanID FROM Loans  WHERE (Loans.QC_Policy "
              "= 'Fannie Mae') AND (Loans.PropertyType = 'Condominium')")
    parsed = G.parse_sql_gating_clause(clause)
    applicability = G.Applicability(program="Fannie Mae", sql_filters=parsed)

    fannie_condo = CanonicalLoan(loan_id="LN-GATE-FNM-CONDO", loan_type="Fannie Mae Purchase")
    fannie_condo.facts["property_type"] = "Condominium"
    assert G.applies_to(fannie_condo, applicability) is True

    fannie_sfr = CanonicalLoan(loan_id="LN-GATE-FNM-SFR", loan_type="Fannie Mae Purchase")
    fannie_sfr.facts["property_type"] = "Single Family"
    result = G.applies_to(fannie_sfr, applicability)
    assert result is False, result


def test_no_sql_clause_leaves_program_prefix_result_unchanged():
    applicability_no_clause = G.Applicability(program="VA", sql_filters={})
    va_loan = _loan("va")
    assert G.applies_to(va_loan, applicability_no_clause) is True


# --- spec 015 Issue 1 (2026-07-28): the derived loan_program fact takes
# priority over the loan_type-label string match, resolving the real
# Fannie/Freddie ambiguity for loans whose 1003 "Loan Program" line names the
# GSE directly (e.g. real loan 01 -> "Fannie Mae", loan 04 -> "Freddie Mac",
# via build_loan_profiles_v3.py's new derive_loan_program() branch), instead
# of falling into the AMBIGUOUS sentinel the bare-"Conventional" loan_type
# label alone forces below.
def test_derived_loan_program_fact_resolves_real_fannie_freddie_ambiguity():
    # Shaped like post-fix loan 01: a bare "Conventional Purchase" loan_type
    # (which alone would be AMBIGUOUS, per the tests above) but WITH the real
    # derived `loan_program` fact wired into loan.fields, exactly as run_015/
    # run_010/run_008 wire derived_facts before calling applies_to().
    loan_01_shaped = CanonicalLoan(
        loan_id="LN-GATE-LOAN01-SHAPED",
        loan_type=LOAN_TYPES["conventional"],
        fields={"loan_program": SourceValue(doc="Fannie Mae")},
    )

    fannie_tagged = G.Applicability(program="Fannie Mae")
    assert G.applies_to(loan_01_shaped, fannie_tagged) is True

    freddie_tagged = G.Applicability(program="Freddie Mac")
    assert G.applies_to(loan_01_shaped, freddie_tagged) is False


# --- T018: taxonomy.py reads every sheet, not only the first ---------------
def test_load_rows_reads_both_sheets_of_private_bank_workbook():
    import taxonomy as T  # p0/eval_synth/taxonomy.py

    path = os.path.join(T.RULES_DIR, "Private Bank Oct 2025 PC and Nov 2025 PF.xlsx")
    rows = T.load_rows(path)
    exception_codes = {r["exception_code"] for r in rows}
    # PB-FormDoc lives only on the "Pre Funding Nov 2025" sheet -- the one
    # taxonomy.py's single-sheet load_rows() never read before this feature.
    assert "PB-FormDoc" in exception_codes


# --- Schema-shift correction: "Post-Closing Private Bank Oct 2025" exports
# every column from "Question Code" onward one position left of the shared
# header (found by direct inspection across 6 different Question Category
# values, 2026-07-20 -- 100% of this questionnaire's 802 rows). Confirms
# load_rows() reads the TRUE exception_code/defect_text/sql_criteria for
# this questionnaire, not the header's nominal (wrong, for this one sheet)
# column positions.
def test_load_rows_corrects_the_shifted_private_bank_post_closing_schema():
    import taxonomy as T

    path = os.path.join(T.RULES_DIR, "Private Bank Oct 2025 PC and Nov 2025 PF.xlsx")
    rows = T.load_rows(path)
    row = next(r for r in rows if r["exception_code"] == "O-FNM-15339")
    assert row["defect_text"].startswith("Anticipated sale proceeds calculated incorrectly")
    assert "QC_Policy = 'Fannie Mae'" in row["sql_criteria"]
    assert row["significance"] == "Critical"


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
