# Contract: Defect Verification Manifest

The ground-truth answer key this feature's accuracy gate (FR-005/FR-006, SC-001) checks against —
formalizing the 25 `<!-- DEFECT ... -->` comments already embedded in the 5 loans' MISMO XML files
into a machine-readable format, so verification is mechanical, not a human re-reading XML comments.

## Format (one entry per known defect, 25 entries total — 5 per loan)

```json
{
  "loan_id": "2025-0917-001",
  "defect_number": 4,
  "description": "Undisclosed liability. Ally Bank auto $412/mo NOT included in total; actual should be 1096.00",
  "field_name": "liability_disclosed_on_1003",
  "compare_field_name": "liability_amount_credit_report",
  "expected_relationship": "mismatch",
  "expected_values": {
    "doc_1003": null,
    "credit_report": "412.00"
  },
  "source_document": "04_Credit_Report_Summary.pdf"
}
```

- `field_name` / `compare_field_name` MUST resolve to entries in `field_catalog.json` (referential
  integrity, mirroring `001a`'s own rule) — an unresolved reference here is exactly the kind of silent
  no-op `001a`'s SAFE gate exists to catch, now surfaced at the verification-manifest boundary too.
- `expected_relationship` values map onto the real-rule archetypes from `taxonomy.json`:
  `mismatch` → MISMATCH, `missing` → MISSING, `threshold_breach` → THRESHOLD, `stale` → EXPIRED.
- `expected_values` states the exact value(s) the extraction must reproduce on each side of the
  documented discrepancy — this is the literal pass/fail assertion `verify_against_defects.py` runs.

## Verification semantics

- **Per-defect check**: for each of the 25 entries, load the corresponding generated `CanonicalLoan`
  fixture, resolve `field_name` (and `compare_field_name` if present), and assert the extracted
  values match `expected_values` exactly (or, for `missing`, that the field genuinely resolves to
  absent — not a fabricated placeholder).
- **Aggregate gate**: `25/25 matched` is the only passing state. `24/25` is a failure, not "mostly
  done" — no partial credit (FR-006, data-model.md `DefectVerificationResult`).
- **On failure**: the specific defect(s) that didn't reproduce are reported by loan/field, and the
  entire fixture set is withheld from downstream use (FR-006) — not just the one failing loan, since
  a broken extractor's failure mode on one field is grounds to distrust its output more broadly until
  fixed.

## Non-goals

- Does not attempt to verify anything beyond these 25 known, constructed defects — it is not a claim
  of general extraction accuracy against arbitrary real documents (spec.md footer note,
  `g-learn-ground-truth-by-construction` Step 6: label the residual loudly).
- Does not define the eventual `003c` reconcile check-kind that would consume doc-vs-doc field pairs
  at runtime — this manifest only proves the *fields* were extracted correctly; how the engine
  eventually compares them is out of scope here (research.md decision #4).
