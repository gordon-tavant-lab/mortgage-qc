"""Deterministic Mortgage QA/QC engine — P0 determinism proof."""
from .ruleset import Ruleset, Check, RuleProvenance, ENGINE_VERSION
from .model import CanonicalLoan, SourceValue, DocCitation
from .engine import run, RunResult, CheckResult
from .audit import AuditLog
from .catalog import (
    FieldCatalog, FieldCatalogEntry, load_catalog,
    validate_referential_integrity, unused_catalog_entries,
    ReferentialIntegrityError,
)

__all__ = [
    "Ruleset", "Check", "RuleProvenance", "ENGINE_VERSION",
    "CanonicalLoan", "SourceValue", "DocCitation",
    "run", "RunResult", "CheckResult", "AuditLog",
    "FieldCatalog", "FieldCatalogEntry", "load_catalog",
    "validate_referential_integrity", "unused_catalog_entries",
    "ReferentialIntegrityError",
]
