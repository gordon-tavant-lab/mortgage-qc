"""
Golden fixtures — labeled loans with KNOWN expected outcomes (the eval ground
truth, Blocker 2). Ported from the AI-Studio prototype's sample loans.

IMPORTANT — this demo is DOC-vs-SYSTEM (a two-way), not a true three-way. The
`mismo` slot here is LOS-origin (a DU/LOS re-serialization, like the real demo
XML), so DOC is the only origin independent of the system. The genuinely
independent third origin — the title/settlement agent's UCD/Closing-Disclosure
data — is NOT in these files; it's what the extraction contract widens to later.
The labeled defects below are therefore all DOC-vs-SYSTEM disparities (judge
ruling #7: a real independent doc path is what makes the cross-source check meaningful):

  - clean_clear     : all three sources agree -> auto-clear
  - rate_mismatch   : doc note rate 6.125 vs system 6.25 -> FAIL (Marcus)
  - flood_unsigned  : doc flood AE vs LOS X (FAIL) + unsigned note (FAIL) (Liam)
  - ssn_addr        : SSN + address disparities -> FAIL (Sophia)
  - ltv_boundary    : LTV sits exactly on the 95.000% line -> the money demo

Each fixture carries `expected` = {check_id: expected_status} so the harness can
score precision/recall and prove the labeled defects are caught.

NOTE: these doc-side values are authored on a path SEPARATE from the system side
on purpose. For P0 this is hand-authored independence; the real eval depends on
Kayla's expert-labeled loans (we do not pretend synthetic data replaces that).
Python 3.9 compatible.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from qc_engine.model import CanonicalLoan, SourceValue, DocCitation


def _cite(doc: str, page: int, snip: str) -> DocCitation:
    return DocCitation(doc_name=doc, page_num=page, segment_snippet=snip)


def golden_loans() -> List[Tuple[CanonicalLoan, Dict[str, str]]]:
    loans: List[Tuple[CanonicalLoan, Dict[str, str]]] = []

    # --- 1. Clean clear: all three agree ----------------------------------
    clean = CanonicalLoan(loan_id="LN-10842", loan_type="Conv 30yr Purchase")
    clean.fields = {
        "borrower_name": SourceValue(doc="John Doe", los="John Doe",
            mismo="John Doe", doc_confidence=0.99,
            citation=_cite("Executed_Closing_Disclosure.pdf", 1, "Borrower: John Doe")),
        "borrower_ssn": SourceValue(doc="XXX-XX-1234", los="333-22-1234",
            mismo="333-22-1234", doc_confidence=0.97,
            citation=_cite("Executed_Closing_Disclosure.pdf", 1, "SSN: ***-**-1234")),
        "note_rate": SourceValue(doc="6.500", los="6.500", mismo="6.500",
            doc_confidence=0.98,
            citation=_cite("Promissory_Note.pdf", 1, "yearly rate of 6.500%")),
        "loan_amount": SourceValue(doc="350000", los="350000", mismo="350000",
            doc_confidence=0.99,
            citation=_cite("Promissory_Note.pdf", 1, "U.S. $350,000")),
        "property_address": SourceValue(doc="123 Maple Dr, Atlanta, GA 30301",
            los="123 Maple Dr, Atlanta, GA 30301",
            mismo="123 Maple Dr, Atlanta, GA 30301", doc_confidence=0.96,
            citation=_cite("Uniform_Appraisal_Report.pdf", 1, "123 Maple Dr")),
        "note_signed": SourceValue(doc=True, doc_confidence=0.99,
            citation=_cite("Promissory_Note.pdf", 3, "/s/ John Doe (Seal)")),
    }
    loans.append((clean, {
        "chk-borrower-name": "PASS", "chk-borrower-ssn": "PASS",
        "chk-note-rate": "PASS", "chk-principal": "PASS",
        "chk-property-address": "PASS", "chk-note-signed": "PASS",
    }))

    # --- 2. Rate mismatch (Marcus): doc 6.125 vs system 6.25 --------------
    marcus = CanonicalLoan(loan_id="LN-95301", loan_type="FHA Purchase")
    marcus.fields = {
        "borrower_name": SourceValue(doc="Marcus A. Vance", los="Marcus Vance",
            mismo="Marcus Vance", doc_confidence=0.98,
            citation=_cite("Executed_Closing_Disclosure.pdf", 1, "Marcus A. Vance")),
        "borrower_ssn": SourceValue(doc="XXX-XX-8819", los="222-11-8819",
            mismo="222-11-8819", doc_confidence=0.97,
            citation=_cite("Executed_Closing_Disclosure.pdf", 1, "***-**-8819")),
        "note_rate": SourceValue(doc="6.125", los="6.250", mismo="6.250",
            doc_confidence=0.98,
            citation=_cite("Promissory_Note.pdf", 1, "yearly rate of 6.125%")),
        "loan_amount": SourceValue(doc="285000", los="285000", mismo="285000",
            doc_confidence=0.99,
            citation=_cite("Promissory_Note.pdf", 1, "U.S. $285,000")),
        "note_signed": SourceValue(doc=True, doc_confidence=0.99,
            citation=_cite("Promissory_Note.pdf", 3, "/s/ Marcus A. Vance (Seal)")),
    }
    loans.append((marcus, {
        "chk-borrower-name": "PASS",  # normalizes to same
        "chk-borrower-ssn": "PASS",
        "chk-note-rate": "FLAG",      # Step 1: system out of sync (informational)
        "chk-principal": "PASS",
        "chk-note-signed": "PASS",
    }))

    # --- 3. Flood + unsigned (Liam): doc flood AE vs LOS X, note unsigned -
    liam = CanonicalLoan(loan_id="LN-73901", loan_type="Conv 15yr Refi")
    liam.fields = {
        "borrower_name": SourceValue(doc="Liam Chen", los="Liam Chen",
            mismo="Liam Chen", doc_confidence=0.99,
            citation=_cite("Executed_Closing_Disclosure.pdf", 1, "Liam Chen")),
        "note_rate": SourceValue(doc="5.750", los="5.750", mismo="5.750",
            doc_confidence=0.98,
            citation=_cite("Promissory_Note.pdf", 1, "yearly rate of 5.750%")),
        "flood_zone": SourceValue(doc="Zone AE", los="Zone X",
            doc_confidence=0.95,
            citation=_cite("FEMA_Flood_Determination.pdf", 1, "YES (Zone AE)")),
        "note_signed": SourceValue(doc=False, doc_confidence=0.93,
            citation=_cite("Promissory_Note.pdf", 3, "[SIGNATURE LINE BLANK]")),
    }
    loans.append((liam, {
        "chk-borrower-name": "PASS",
        "chk-note-rate": "PASS",
        "chk-flood-zone": "FLAG",     # Step 1: doc vs system out of sync (info)
        "chk-note-signed": "FAIL",    # Step 2 QC: unsigned note is a real defect
    }))

    # --- 4. SSN + address (Sophia): SSN mismatch, address normalizes equal -
    sophia = CanonicalLoan(loan_id="LN-48210", loan_type="Conv Refi Investment")
    sophia.fields = {
        "borrower_name": SourceValue(doc="Sophia Martinez", los="Sophia Martinez",
            mismo="Sophia Martinez", doc_confidence=0.99,
            citation=_cite("Executed_Closing_Disclosure.pdf", 1, "Sophia Martinez")),
        # doc shows last4 5521; both systems 5521 too -> PASS on last4
        "borrower_ssn": SourceValue(doc="XXX-XX-5521", los="444-55-5521",
            mismo="444-55-5521", doc_confidence=0.96,
            citation=_cite("Executed_Closing_Disclosure.pdf", 1, "***-**-5521")),
        # address: doc has "Apt 4C" + "Blvd", LOS "Boulevarde", mismo "Blvd"
        # -> after normalization the unit makes doc differ -> FAIL
        "property_address": SourceValue(
            doc="789 Oakhaven Blvd Apt 4C, Orlando, FL 32801",
            los="789 Oakhaven Boulevarde, Orlando, FL 32801",
            mismo="789 Oakhaven Blvd, Orlando, FL 32801", doc_confidence=0.9,
            citation=_cite("Uniform_Appraisal_Report.pdf", 1, "789 Oakhaven Blvd Apt 4C")),
        "note_signed": SourceValue(doc=True, doc_confidence=0.99,
            citation=_cite("Promissory_Note.pdf", 3, "/s/ Sophia Martinez (Seal)")),
    }
    loans.append((sophia, {
        "chk-borrower-name": "PASS",
        "chk-borrower-ssn": "PASS",      # last4 match
        "chk-property-address": "FLAG",  # Step 1: system out of sync (info)
        "chk-note-signed": "PASS",
    }))

    # --- 5. LTV boundary: the bit-exact money demo ------------------------
    # loan 332,500 / value 350,000 = 95.000% exactly, threshold <= 95.000
    boundary = CanonicalLoan(loan_id="LN-BOUNDARY", loan_type="Conv Purchase")
    boundary.facts = {"loan_amount": "332500.00", "property_value": "350000.00"}
    boundary.fields = {
        "note_signed": SourceValue(doc=True, doc_confidence=0.99,
            citation=_cite("Promissory_Note.pdf", 3, "/s/ signed (Seal)")),
    }
    loans.append((boundary, {
        "chk-ltv-max": "PASS",   # 95.000 <= 95.000 exactly
        "chk-note-signed": "PASS",
    }))

    # --- 6. Reconciles clean, FAILS QC: the two-step proof ----------------
    # Every doc value matches the system perfectly (Step 1 = no discrepancies),
    # but LTV = 343,000 / 350,000 = 98.000% > 95% program max -> Step 2 FAILS.
    # A perfect doc-vs-system match is NOT sufficient to auto-clear.
    qc_fail = CanonicalLoan(loan_id="LN-QCFAIL", loan_type="Conv Purchase")
    qc_fail.facts = {"loan_amount": "343000.00", "property_value": "350000.00"}
    qc_fail.fields = {
        "borrower_name": SourceValue(doc="Dana Reed", los="Dana Reed",
            mismo="Dana Reed", doc_confidence=0.99,
            citation=_cite("Executed_Closing_Disclosure.pdf", 1, "Dana Reed")),
        "note_rate": SourceValue(doc="6.750", los="6.750", mismo="6.750",
            doc_confidence=0.98,
            citation=_cite("Promissory_Note.pdf", 1, "yearly rate of 6.750%")),
        "loan_amount": SourceValue(doc="343000", los="343000", mismo="343000",
            doc_confidence=0.99,
            citation=_cite("Promissory_Note.pdf", 1, "U.S. $343,000")),
        "note_signed": SourceValue(doc=True, doc_confidence=0.99,
            citation=_cite("Promissory_Note.pdf", 3, "/s/ Dana Reed (Seal)")),
    }
    loans.append((qc_fail, {
        "chk-borrower-name": "PASS",   # Step 1: matches
        "chk-note-rate": "PASS",       # Step 1: matches
        "chk-principal": "PASS",       # Step 1: matches
        "chk-note-signed": "PASS",     # Step 2 policy: signed, ok
        "chk-ltv-max": "FAIL",         # Step 2 policy: 98% > 95% -> FAIL
    }))

    return loans
