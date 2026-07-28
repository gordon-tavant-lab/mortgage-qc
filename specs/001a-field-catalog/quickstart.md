# Quickstart: Field Catalog

## For engineers extending coverage (the day-to-day workflow this feature exists for)

1. Add a new entry to `p0/qc_engine/field_catalog.json` (name, `data_type`, `expected_sources`,
   `citation_required`, `confidence_required`) — per `contracts/field-catalog-schema.md`. No file
   under `p0/qc_engine/*.py` needs to change (FR-005, SC-001).
2. Author checks (`p0/qc_engine/ruleset.py`'s `Check`) referencing that `field_name` as usual.
3. Before scoring any loan, run the referential-integrity validator against the `Ruleset` +
   `FieldCatalog` pair. A typo'd or renamed field reference fails loudly here — never silently at
   runtime (FR-003, FR-004).
4. Re-run `p0/harness.py` and `p0/eval_synth`'s test suite to confirm zero regression (SC-002).

## Verifying the catalog itself

- Hash the catalog file twice, unchanged — confirm identical SHA-256 (SC-005).
- Edit one entry, re-hash — confirm the digest changes.
- Add a synthetic field with no referencing check yet — confirm it's reported as an unused entry
  (FR-008), not rejected.

## What this quickstart deliberately does not include

- No authoring UI (`009` — unspecced, out of scope).
- No N-source generalization (`001b` — depends on this feature, not the reverse).
