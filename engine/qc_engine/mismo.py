"""
MISMO 3.4 (DU/ULAD wrapper) XML reader — the SYSTEM-side adapter.

Parses the real demo exports (demo/<id>/<id>-UladDuExport.xml) into the canonical
field map. This is one of the three INDEPENDENT source adapters; it must NEVER be
used to populate the doc-extracted path (judge ruling #7: that would collapse the
cross-source comparison into self-validation).

Targets the actual elements observed in the demo files:
  NoteRatePercent, BaseLoanAmount, LoanMaturityPeriodCount,
  PropertyValuationAmount / SalesContractAmount, PARTY(Borrower) FirstName/LastName,
  SUBJECT property AddressLineText/CityName/StateCode/PostalCode.

Uses ElementTree with namespace-agnostic local-name matching (the MISMO default
namespace makes tag names verbose otherwise). Python 3.9 compatible.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _first_text(root: ET.Element, name: str) -> Optional[str]:
    for el in root.iter():
        if _local(el.tag) == name and el.text and el.text.strip():
            return el.text.strip()
    return None


def _find_blocks(root: ET.Element, name: str) -> List[ET.Element]:
    return [el for el in root.iter() if _local(el.tag) == name]


def _child_text(block: ET.Element, name: str) -> Optional[str]:
    for el in block.iter():
        if _local(el.tag) == name and el.text and el.text.strip():
            return el.text.strip()
    return None


def parse_mismo(path: str) -> Dict[str, object]:
    """Return a flat dict of canonical-field -> value from a MISMO 3.4 export."""
    tree = ET.parse(path)
    root = tree.getroot()
    out: Dict[str, object] = {}

    note_rate = _first_text(root, "NoteRatePercent")
    if note_rate is not None:
        out["note_rate"] = note_rate
    base_amt = _first_text(root, "BaseLoanAmount")
    if base_amt is not None:
        out["loan_amount"] = base_amt
    term = _first_text(root, "LoanMaturityPeriodCount")
    if term is not None:
        out["term_months"] = term
    # property value: prefer appraisal/valuation, fall back to sales contract
    pv = _first_text(root, "PropertyValuationAmount") \
        or _first_text(root, "PropertyEstimatedValueAmount")
    if pv is not None:
        out["property_value"] = pv
    sca = _first_text(root, "SalesContractAmount")
    if sca is not None:
        out["purchase_price"] = sca

    # Borrower full name (first PARTY with PartyRoleType == Borrower)
    for party in _find_blocks(root, "PARTY"):
        roles = [el.text.strip() for el in party.iter()
                 if _local(el.tag) == "PartyRoleType" and el.text]
        if any(r == "Borrower" for r in roles):
            fn = _child_text(party, "FirstName")
            ln = _child_text(party, "LastName")
            if fn or ln:
                out["borrower_name"] = " ".join(x for x in (fn, ln) if x)
            ssn = _child_text(party, "TaxpayerIdentifierValue") \
                or _child_text(party, "TaxpayerIdentifier")
            if ssn:
                out["borrower_ssn"] = ssn
            break

    # Subject property address (first PROPERTY block)
    props = _find_blocks(root, "SUBJECT_PROPERTY") or _find_blocks(root, "PROPERTY")
    if props:
        p = props[0]
        line = _child_text(p, "AddressLineText")
        city = _child_text(p, "CityName")
        state = _child_text(p, "StateCode")
        zc = _child_text(p, "PostalCode")
        parts = [x for x in (line, (f"{city}, {state} {zc}" if city else None)) if x]
        if parts:
            out["property_address"] = ", ".join(parts)

    loan_id = _first_text(root, "LoanIdentifier")
    if loan_id:
        out["loan_id"] = loan_id

    # FHA case number, system-of-record side only (Source=FHAC_Portal) — the
    # doc-side (as stated on the 1003) is extracted from the PDF, never here
    # (judge ruling #7: this adapter must never populate the doc-extracted path).
    # Same catalog field (fha_case_number_1003) as the doc side; this becomes
    # its sources["mismo"] value, a genuine doc-vs-system comparison
    # (000-synthetic-fixture-generation research.md decision #4).
    for li in _find_blocks(root, "LOAN_IDENTIFIER"):
        if _child_text(li, "LoanIdentifierType") == "FHACaseNumber" \
                and _child_text(li, "Source") == "FHAC_Portal":
            fhac_case = _child_text(li, "LoanIdentifier")
            if fhac_case:
                out["fha_case_number_1003"] = fhac_case
            break

    return out
