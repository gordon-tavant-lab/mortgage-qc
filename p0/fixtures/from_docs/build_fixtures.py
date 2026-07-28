"""
build_fixtures.py — merges extract_pdf.py's truth+citation output and
extract_xml.py's sources.mismo output into 5 CanonicalLoan JSON fixtures,
one per synthetic loan, populated only from that loan's own folder (no
cross-loan data leakage). Deterministic: same source documents -> same
output JSON, every run (plan.md Constraints).

Output shape mirrors qc_engine/model.py's CanonicalLoan/SourceValue/DocCitation
directly (fields[name] = {truth, sources, citation, doc_confidence}), so
loading a fixture back into CanonicalLoan requires zero changes to model.py —
see fixture_loader.py for the loader that does that reconstruction.

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from extract_pdf import extract_pdf_fields  # noqa: E402
from extract_xml import extract_mismo_fields  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
DEMO_SYN_DIR = os.path.join(REPO_ROOT, "demo", "syn")

# folder name -> (mismo filename, loan_type) — the only per-loan metadata not
# derivable purely from extraction; loan_type is descriptive only, never used
# by verify_against_defects.py's field-level checks.
#
# NOTE (2026-07-20, see output/RULE-PROGRAM-GATING-FINDINGS.md §8): loan 01's and
# loan 04's real MISMO <MortgageType> is just "Conventional" -- neither carries a
# GSE-investor field. Loan 04's "Freddie Mac" label below is this fixture's own
# descriptive choice, not derived from the loan's actual data; program_gating.py
# correctly returns AMBIGUOUS for both. For a bounded LLM-compile pre-test, both
# are being assumed Fannie Mae (documented, not silently baked in) -- 010b is
# where a real investor/AUS field would make this derivable instead of assumed.
LOAN_PACKAGES = {
    "loan 01": ("09_Loan_Data_MISMO.xml", "Conventional Purchase"),
    "loan 02": ("09_Loan_Data_MISMO.xml", "FHA Purchase"),
    "loan 03": ("07_Loan_Data_MISMO.xml", "VA Purchase"),
    "loan 04": ("07_Loan_Data_MISMO.xml", "Freddie Mac Cash-Out Refi"),
    "loan 05": ("06_Loan_Data_MISMO.xml", "USDA RHS 502 Guaranteed"),
}


def build_loan_fixture(loan_folder_name: str) -> Dict[str, Any]:
    """Build one loan's CanonicalLoan-shaped fixture dict, from that loan's
    own folder only (no cross-loan leakage — every value below comes from
    files under demo/syn/<loan_folder_name>/)."""
    mismo_filename, loan_type = LOAN_PACKAGES[loan_folder_name]
    loan_folder = os.path.join(DEMO_SYN_DIR, loan_folder_name)
    mismo_path = os.path.join(loan_folder, mismo_filename)

    doc_fields = extract_pdf_fields(loan_folder)
    mismo_fields = extract_mismo_fields(mismo_path)

    loan_id = mismo_fields.get("loan_id")

    all_field_names = set(doc_fields) | set(mismo_fields) - {"loan_id"}
    fields: Dict[str, Any] = {}
    for name in sorted(all_field_names):
        doc_entry = doc_fields.get(name)
        sources: Dict[str, Any] = {}
        if name in mismo_fields:
            sources["mismo"] = mismo_fields[name]
        fields[name] = {
            "truth": doc_entry["value"] if doc_entry else None,
            "sources": sources,
            "citation": doc_entry["citation"] if doc_entry else None,
            "doc_confidence": doc_entry["doc_confidence"] if doc_entry else None,
        }
    fields.update(_derive_date_diff_fields(fields))

    facts = _derive_facts(fields)
    facts.update(_derive_document_presence_facts(loan_folder))

    return {
        "loan_id": loan_id,
        "loan_type": loan_type,
        "fields": fields,
        "facts": facts,
    }


# filename substring -> fact name. Each names ONE specific physical document,
# not a bundled doc_patterns/*.json file (fha_docs.json alone bundles 5
# distinct documents under one pattern) -- ruleset_defects.py's per-loan
# gating needs to know whether THAT SPECIFIC supporting document exists in
# this loan's own package, the real precondition for "is a missing-document
# predicate check even meaningful here" (as opposed to loan_type/program,
# which is wrong for borrower/transaction-level conditions like self-employed
# income or an unexplained large deposit -- those can occur under any
# program, not just the one loan in this 5-loan set that happens to have it).
_DOCUMENT_PRESENCE_SUBSTRINGS = {
    "doc_present_bank_statement": ["Bank_Statement"],
    "doc_present_hud92900a": ["HUD_92900A"],
    "doc_present_gift_letter": ["Gift_Letter"],
    "doc_present_va_appraisal": ["VA_Appraisal"],
    "doc_present_self_employed_income": ["Self_Employed"],
    "doc_present_usda_appraisal": ["Appraisal_Summary_USDA"],
    "doc_present_usda_property_eligibility": ["USDA_Property_Eligibility"],
}


def _derive_document_presence_facts(loan_folder: str) -> Dict[str, str]:
    filenames = os.listdir(loan_folder)
    facts: Dict[str, str] = {}
    for fact_name, substrings in _DOCUMENT_PRESENCE_SUBSTRINGS.items():
        present = any(sub in fn for fn in filenames for sub in substrings)
        facts[fact_name] = "true" if present else "false"
    return facts


# Field names _derive_date_diff_fields() computes (not doc-extracted -- no
# citation applies). test_fixture_generation.py's citation-completeness
# invariants exclude these by name rather than relaxing "truth implies
# citation" for every field.
DERIVED_FIELD_NAMES = frozenset({
    "appraisal_staleness_days",
    "nov_days_after_closing",
})


def _parse_mmddyyyy(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%m/%d/%Y")
    except ValueError:
        return None


def _derive_date_diff_fields(fields: Dict[str, Any]) -> Dict[str, Any]:
    """Two engine check-kinds already built (003a predicate, 003b
    ratio_threshold field_value) can only compare a field's own truth value
    against a threshold -- neither computes a date difference between TWO
    doc-sourced date fields. Rather than add a new engine ratio mode for what
    is genuinely a fixture-side derivation (both inputs are already-resolved
    doc truth, no new extraction or engine logic needed), compute the day-gap
    as its own numeric field here -- same precedent as _derive_facts(), just
    landing in fields{} (not facts{}) so ratio_threshold's existing
    ratio="field_value" mode (which reads loan.get(field_name), i.e. fields,
    not facts) can check it with zero engine changes.

    No citation is attached: the value is computed from two documents, not
    read from one, so there is no single page/segment to cite (mirrors the
    DocCitation contract -- one citation, one source document)."""
    derived: Dict[str, Any] = {}

    appraisal_dt = _parse_mmddyyyy(
        (fields.get("appraisal_effective_date") or {}).get("truth"))
    closing_dt = _parse_mmddyyyy((fields.get("closing_date") or {}).get("truth"))
    if appraisal_dt is not None and closing_dt is not None:
        derived["appraisal_staleness_days"] = {
            "truth": str((closing_dt - appraisal_dt).days),
            "sources": {}, "citation": None, "doc_confidence": None,
        }

    nov_dt = _parse_mmddyyyy((fields.get("notice_of_value_date") or {}).get("truth"))
    if nov_dt is not None and closing_dt is not None:
        derived["nov_days_after_closing"] = {
            "truth": str((nov_dt - closing_dt).days),
            "sources": {}, "citation": None, "doc_confidence": None,
        }

    return derived


def _derive_facts(fields: Dict[str, Any]) -> Dict[str, Any]:
    """qc_engine/engine.py's ratio_threshold="ltv" check reads loan.facts, not
    loan.fields -- a distinct data path build_fixtures.py had always left
    empty, so chk-ltv-max resolved NOT_APPLICABLE for every document-derived
    loan regardless of how complete fields{} was. Derives the two facts keys
    golden.py's own boundary-loan fixtures use ("loan_amount", "property_value")
    from the already-resolved fields, preferring the document truth (Principle
    V) and falling back to the system side only if no doc value exists -- never
    fabricated, just resolved from data already extracted above."""
    facts: Dict[str, Any] = {}
    for fact_name, field_name in (("loan_amount", "loan_amount"),
                                   ("property_value", "property_value")):
        entry = fields.get(field_name)
        if not entry:
            continue
        value = entry["truth"] if entry["truth"] is not None else entry["sources"].get("mismo")
        if value is not None:
            facts[fact_name] = str(value)
    return facts


def build_all_fixtures() -> Dict[str, str]:
    """Build and write all 5 fixtures. Returns {loan_folder_name: output_path}."""
    written = {}
    for loan_folder_name in sorted(LOAN_PACKAGES):
        fixture = build_loan_fixture(loan_folder_name)
        out_name = "loan_{0}.json".format(loan_folder_name.split(" ")[1])
        out_path = os.path.join(HERE, out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(fixture, f, indent=2, sort_keys=True)
            f.write("\n")
        written[loan_folder_name] = out_path
    return written


if __name__ == "__main__":
    for name, path in build_all_fixtures().items():
        print("{0} -> {1}".format(name, path))
