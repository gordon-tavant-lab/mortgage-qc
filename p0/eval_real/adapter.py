"""
012 User Story 1 (T009) -- RealLoanAdapter (FR-001/002/004).

Converts one real loan's extraction bundle (`{loan}-ulad.json` +
`{loan}-citations.json` + `consolidated/*.json`, per the S3 layout confirmed
in spec.md's Foundation section) into a `CanonicalLoan` + the exact
`LabeledLoan` tuple shape `p0/eval_synth/test_properties.score()` already
accepts (`generator.py:43` -- `Tuple[CanonicalLoan, Dict[str, str],
Dict[str, Any]]`). No new type, no scorer signature change (FR-002).

The adapter is a pure format-conversion layer over already-extracted field
data -- it never infers or derives what a loan's correct QC verdict is
(FR-005). `expected_verdicts` is always the caller-supplied,
expert-adjudicated (or, in tests, hand-authored synthetic stand-in) label
set; the adapter passes it through unmodified.

Field mapping: the real bundle's ULAD-shaped summary nests borrower/property
values under keys that don't literally match this project's canonical field
vocabulary (`field_catalog.json`) -- e.g. `borrowers[0].full_name` ->
`borrower_name`, `property.address` -> `property_address`. A small, explicit
map covers those. Everything else (chiefly `loan_detail`'s own keys) is
checked directly against `field_catalog.json`'s existing canonical names
(pass-through) -- if a bundle field name already IS a canonical name, no
translation is needed; if it resolves to neither the explicit map nor an
existing catalog entry, it is recorded as a named `MappingGap` (FR-004),
never silently dropped and never silently coerced into a null `SourceValue`.

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qc_engine.catalog import FieldCatalog, load_catalog  # noqa: E402
from qc_engine.model import CanonicalLoan, DocCitation, SourceValue  # noqa: E402

from .mapping_gaps import MappingGapReport  # noqa: E402

DEFAULT_CATALOG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "qc_engine", "field_catalog.json",
)

# Explicit real-bundle-key -> canonical-field-name maps. Only needed where
# the bundle's own key name genuinely differs from field_catalog.json's
# canonical name -- everything else goes through pass-through matching.
BORROWER_FIELD_MAP: Dict[str, str] = {
    "full_name": "borrower_name",
    "ssn_last4": "borrower_ssn",
}
PROPERTY_FIELD_MAP: Dict[str, str] = {
    "address": "property_address",
}
LOAN_DETAIL_FIELD_MAP: Dict[str, str] = {
    # loan_detail's own keys (note_rate, loan_amount, ...) already match
    # field_catalog.json's canonical names in the confirmed real-bundle
    # shape -- pass-through handles them with no entry needed here. This map
    # exists for the rare case a real bundle's own key genuinely diverges.
}

# LabeledLoan tuple shape (generator.py:43) -- documented here, not
# re-imported, to avoid a hard dependency of eval_real on eval_synth beyond
# what test_properties.score() itself already requires at call time.
LabeledLoan = Tuple[CanonicalLoan, Dict[str, str], Dict[str, Any]]


def _read_json(path: str) -> Optional[Dict[str, Any]]:
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _map_section(raw: Dict[str, Any], field_map: Dict[str, str],
                 catalog: FieldCatalog, section_name: str,
                 fields_out: Dict[str, SourceValue],
                 gap_report: MappingGapReport) -> None:
    """Map one ULAD section's keys (e.g. `borrowers[0]`, `property`,
    `loan_detail`) onto canonical `CanonicalLoan.fields` entries.

    Resolution order per key: (1) the section's explicit field_map, (2)
    pass-through if the raw key name is already a `field_catalog.json`
    canonical name, (3) a named `MappingGap` -- never a silent drop, never a
    silently-null field."""
    for raw_key, value in raw.items():
        canonical_name: Optional[str] = field_map.get(raw_key)
        if canonical_name is None and catalog.get(raw_key) is not None:
            canonical_name = raw_key
        if canonical_name is None:
            gap_report.add(field_name=raw_key, raw_value=value,
                            source_section=section_name)
            continue
        fields_out[canonical_name] = SourceValue(truth=value)


class RealLoanAdapter:
    """FR-001/002: bundle -> `CanonicalLoan` + `LabeledLoan`-shaped tuple.

    `last_mapping_gap_report` holds the `MappingGapReport` (FR-004) from the
    most recent `.adapt()` call -- the same pattern this project's other
    single-call-then-inspect helpers (e.g. `qc_engine.catalog`'s validators)
    already use, rather than inventing a second return-value convention.
    """

    def __init__(self, catalog_path: Optional[str] = None) -> None:
        self.catalog: FieldCatalog = load_catalog(catalog_path or DEFAULT_CATALOG_PATH)
        self.last_mapping_gap_report: Optional[MappingGapReport] = None

    def adapt(self, bundle_dir: str, loan_id: str,
              expected_verdicts: Dict[str, str]) -> LabeledLoan:
        """Convert one loan's extraction bundle at `bundle_dir` into the
        `(CanonicalLoan, expected, prov)` tuple `score()` already accepts.

        `expected_verdicts` is passed through unmodified (FR-005) -- the
        adapter never invents or infers a verdict."""
        ulad = _read_json(os.path.join(bundle_dir, f"{loan_id}-ulad.json")) or {}
        citations = _read_json(os.path.join(bundle_dir, f"{loan_id}-citations.json")) or {}

        gap_report = MappingGapReport(loan_id=loan_id)
        fields: Dict[str, SourceValue] = {}

        borrowers = ulad.get("borrowers") or []
        if borrowers:
            _map_section(borrowers[0], BORROWER_FIELD_MAP, self.catalog,
                         "borrowers[0]", fields, gap_report)

        prop = ulad.get("property") or {}
        _map_section(prop, PROPERTY_FIELD_MAP, self.catalog, "property",
                     fields, gap_report)

        loan_detail = ulad.get("loan_detail") or {}
        _map_section(loan_detail, LOAN_DETAIL_FIELD_MAP, self.catalog,
                     "loan_detail", fields, gap_report)

        # Attach real-shaped doc citations + confidence (FR-001: populating
        # SourceValue.citation/doc_confidence from the bundle's own
        # discrepancy/confidence records) -- only for fields that resolved
        # to a canonical name above; an unmapped field's citation is moot
        # (it never became a CanonicalLoan field in the first place).
        for disc in citations.get("discrepancies", []) or []:
            canonical_name = disc.get("field")
            if not canonical_name or canonical_name not in fields:
                continue
            sv = fields[canonical_name]
            sv.citation = DocCitation(
                doc_name=disc.get("document", ""),
                page_num=disc.get("page", 0) or 0,
                segment_snippet=disc.get("text_snippet", "") or "",
            )
            if disc.get("confidence") is not None:
                sv.doc_confidence = disc["confidence"]

        loan = CanonicalLoan(loan_id=loan_id, loan_type="", fields=fields)
        self.last_mapping_gap_report = gap_report

        prov: Dict[str, Any] = {
            "mutations": [],
            "source": "expert-labeled",
            "loan_id": loan_id,
        }
        return loan, dict(expected_verdicts), prov
