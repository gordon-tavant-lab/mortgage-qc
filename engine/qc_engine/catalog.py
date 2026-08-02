"""
The field catalog — the vocabulary layer of the Authored Configuration Model
(constitution Principle VII).

Generalizes the engine's fixed loan field slots into a schema-driven, signed
vocabulary: every field the engine can reason about is declared once (name,
type, expected sources, citation/confidence requirements), so growing to the
800+ real checks is an authoring act, not an engine-code change.

Mirrors p0/qc_engine/ruleset.py's exact canonical-hashing pattern (sorted-key
JSON, SHA-256) rather than inventing a second signing mechanism — one model,
consistent mechanics, per the constitution's Authored Configuration Model.

Referential integrity (every Check.field_name resolves to a catalog entry) is
validated ONCE, at load time, before any loan is scored — never per-check at
runtime (see specs/001a-field-catalog/research.md decision #2 for why: a
missing reference is a load-time defect in the ruleset+catalog pairing, not a
per-loan runtime condition, and re-checking it 3,000+ times per eval run would
be redundant, not defense-in-depth).

Python 3.9 compatible.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .ruleset import Ruleset, ENGINE_VERSION

VALID_DATA_TYPES = ("string", "decimal", "date", "boolean", "enum")
VALID_SOURCES = ("doc", "los", "mismo")  # 001b generalizes this to a named map


@dataclass
class FieldCatalogEntry:
    """One vocabulary item — the unit of 'adding a data element as an
    authoring act' (spec.md FR-001, FR-005)."""
    field_name: str
    data_type: str
    expected_sources: List[str] = field(default_factory=list)
    citation_required: bool = False
    confidence_required: bool = False
    description: str = ""
    enum_values: Optional[List[str]] = None
    # 001b: per-field override of SourceValue's system-source resolution
    # order. None -> falls back to SourceValue's own default (["los", "mismo"]).
    source_priority: Optional[List[str]] = None

    def __post_init__(self) -> None:
        if self.data_type not in VALID_DATA_TYPES:
            raise ValueError(
                f"FieldCatalogEntry '{self.field_name}': unknown data_type "
                f"'{self.data_type}' (must be one of {VALID_DATA_TYPES})")
        if self.data_type == "enum" and not self.enum_values:
            raise ValueError(
                f"FieldCatalogEntry '{self.field_name}': data_type=enum "
                f"requires non-empty enum_values")
        if self.data_type != "enum" and self.enum_values:
            raise ValueError(
                f"FieldCatalogEntry '{self.field_name}': enum_values is only "
                f"valid when data_type=enum")
        for src in self.expected_sources:
            if src not in VALID_SOURCES:
                raise ValueError(
                    f"FieldCatalogEntry '{self.field_name}': unknown source "
                    f"'{src}' (must be one of {VALID_SOURCES} for this "
                    f"feature; 001b generalizes this)")

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "field_name": self.field_name,
            "data_type": self.data_type,
            "expected_sources": list(self.expected_sources),
            "citation_required": self.citation_required,
            "confidence_required": self.confidence_required,
            "description": self.description,
        }
        if self.enum_values:
            d["enum_values"] = list(self.enum_values)
        if self.source_priority:
            d["source_priority"] = list(self.source_priority)
        return d


@dataclass
class FieldCatalog:
    """The full, versioned, signed collection of FieldCatalogEntry — the
    vocabulary layer (spec.md FR-006)."""
    catalog_id: str
    version: int
    entries: List[FieldCatalogEntry] = field(default_factory=list)
    engine_version: str = ENGINE_VERSION

    def __post_init__(self) -> None:
        seen = set()
        for e in self.entries:
            if e.field_name in seen:
                raise ValueError(
                    f"FieldCatalog '{self.catalog_id}': duplicate field_name "
                    f"'{e.field_name}' — every entry must be unique (FR-009)")
            seen.add(e.field_name)

    def get(self, field_name: str) -> Optional[FieldCatalogEntry]:
        for e in self.entries:
            if e.field_name == field_name:
                return e
        return None

    # --- the canonical, hashable content ------------------------------------
    # Mirrors Ruleset.canonical_content()/sha256() exactly (research.md #1's
    # JSON-everywhere consistency; no second canonicalization scheme).
    def canonical_content(self) -> Dict[str, Any]:
        return {
            "catalog_id": self.catalog_id,
            "version": self.version,
            "engine_version": self.engine_version,
            "entries": [e.to_dict() for e in self.entries],
        }

    def sha256(self) -> str:
        blob = json.dumps(self.canonical_content(), sort_keys=True,
                          separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()

    def to_json(self) -> str:
        return json.dumps(self.canonical_content(), indent=2, sort_keys=True)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "FieldCatalog":
        return FieldCatalog(
            catalog_id=d["catalog_id"],
            version=d["version"],
            engine_version=d.get("engine_version", ENGINE_VERSION),
            entries=[FieldCatalogEntry(**e) for e in d.get("entries", [])],
        )


def load_catalog(path: str) -> FieldCatalog:
    """Load + validate a catalog file. A malformed file fails to load
    entirely -- never partially (FR-009, spec.md Edge Cases)."""
    with open(path) as fh:
        raw = json.load(fh)
    return FieldCatalog.from_dict(raw)


# --- referential integrity: the SAFE gate ----------------------------------

class ReferentialIntegrityError(ValueError):
    """A check's field_name does not resolve to any catalog entry -- a false-
    clear vector if allowed to run (constitution Principle VII / SAFE gate)."""


def validate_referential_integrity(ruleset: Ruleset, catalog: FieldCatalog) -> None:
    """Confirm every check's field_name resolves to a catalog entry.

    Runs ONCE, at load time, before any loan is scored (research.md decision
    #2) -- never re-checked per-check at runtime. Raises immediately, naming
    both the offending check and the missing field; never a silent no-op.
    """
    for chk in ruleset.checks:
        # ratio_threshold checks whose value is derived from loan.facts (not
        # loan.fields) legitimately carry no field_name -- model.py's own
        # docstring distinguishes "facts" (pre-derived numeric inputs for
        # ratio checks) from "fields" (the catalog's domain). Nothing to
        # resolve; not a referential-integrity gap.
        if chk.kind == "ratio_threshold" and not chk.field_name:
            continue
        if catalog.get(chk.field_name) is None:
            raise ReferentialIntegrityError(
                f"check '{chk.id}' ({chk.name}) references field "
                f"'{chk.field_name}', which does not exist in catalog "
                f"'{catalog.catalog_id}' -- unresolved reference; check "
                f"blocked from running (FR-004).")
        # 003d: agree_doc_categorical/agree_doc_numeric reference a SECOND
        # field -- resolve it too, same fail-fast pattern. Without this, a
        # typo'd compare_field_name would silently pass this gate and only
        # break at evaluation time instead of load time.
        if chk.compare_field_name and catalog.get(chk.compare_field_name) is None:
            raise ReferentialIntegrityError(
                f"check '{chk.id}' ({chk.name}) references compare_field_name "
                f"'{chk.compare_field_name}', which does not exist in catalog "
                f"'{catalog.catalog_id}' -- unresolved reference; check "
                f"blocked from running (FR-004).")
        # 002e FR-004: same fail-fast pattern for every applies_if condition's
        # field_name -- a typo'd precondition field must be caught at load
        # time, not silently pass and only break (or worse, silently read as
        # "always None" / always-unknown) at evaluation time.
        for condition in (chk.applies_if or []):
            cond_field = condition["field_name"]
            if catalog.get(cond_field) is None:
                raise ReferentialIntegrityError(
                    f"check '{chk.id}' ({chk.name}) references applies_if field "
                    f"'{cond_field}', which does not exist in catalog "
                    f"'{catalog.catalog_id}' -- unresolved reference; check "
                    f"blocked from running (FR-004).")


def unused_catalog_entries(ruleset: Ruleset, catalog: FieldCatalog) -> List[str]:
    """Catalog entries no check currently references -- visibility, not a
    failure (FR-008). The catalog may legitimately run ahead of the checks
    that will consume it as 003a/b/c land."""
    referenced = {chk.field_name for chk in ruleset.checks}
    return [e.field_name for e in catalog.entries if e.field_name not in referenced]
