# Criteria: 010b Derive the Remaining Gating Dimensions (Occupancy + Loan Program)

Executable, not prose — each maps directly to spec.md's Success Criteria.
Run everything from the repo root unless noted; `p0/` is the test root
(`cd p0 && python3 -m pytest ...`).

## SC-001 — `derive_occupancy_type` resolves `owner_occupied` for all 5 real loans, cited

```bash
cd p0 && python3 -m pytest tests/test_loan_profiles_v3.py \
  -k "derive_occupancy_type_all_five_real_loans or derive_occupancy_type_loan_02_real_fixture" -v
```

```python
from qc_engine.build_loan_profiles_v3 import derive_occupancy_type
from fixture_loader import load_canonical_loan

for n in ("01", "02", "03", "04", "05"):
    loan = load_canonical_loan(f"p0/fixtures/from_docs/loan_{n}.json")
    result = derive_occupancy_type(loan)
    entry = result["derived_facts"]["occupancy_type"]
    assert entry["value"] == "owner_occupied"
    assert entry["derived_from"]["field"] == "occupancy_1003"  # citable, not guessed
```

## SC-002 — the real compiled check gates correctly (owner-occupied vs. investment)

```bash
cd p0 && python3 -m pytest tests/test_occupancy_applicability_gating.py \
  -k "gated_evaluates_normally or gated_resolves_not_applicable" -v
```

```python
# owner-occupied (loan_02, real fixture) -> evaluates predicate normally, same as ungated
gated_result.status == ungated_result.status == "PASS"  # (or "FAIL", proven both ways)

# investment (constructed loan) -> NOT_APPLICABLE, never silently PASS/FAIL
result.status == "NOT_APPLICABLE"
result.review_reason is None
```

## SC-003 — `derive_loan_program` resolves 3/5, honestly `underivable` for 2/5 with distinct reasons

```bash
cd p0 && python3 -m pytest tests/test_loan_profiles_v3.py -k "derive_loan_program" -v
```

```python
from qc_engine.build_loan_profiles_v3 import derive_loan_program
from fixture_loader import load_canonical_loan

expected = {"02": "FHA", "03": "VA", "05": "USDA"}
for n, program in expected.items():
    loan = load_canonical_loan(f"p0/fixtures/from_docs/loan_{n}.json")
    entry = derive_loan_program(loan)["derived_facts"]["loan_program"]
    assert entry["value"] == program
    assert entry["derived_from"]  # citable, not guessed

loan_01 = load_canonical_loan("p0/fixtures/from_docs/loan_01.json")
loan_04 = load_canonical_loan("p0/fixtures/from_docs/loan_04.json")
reason_01 = derive_loan_program(loan_01)["underivable"]["loan_program"]["reason"]
reason_04 = derive_loan_program(loan_04)["underivable"]["loan_program"]["reason"]
assert "fannie" in reason_01.lower() and "freddie" in reason_01.lower()  # ambiguity, named
assert "ambig" not in reason_04.lower()  # distinct failure mode: no signal at all
assert reason_01.lower() != reason_04.lower()  # never conflated
```

## SC-004 — `validate_referential_integrity()` resolves both new fields without raising

```bash
cd p0 && python3 -m pytest tests/test_occupancy_applicability_gating.py \
  -k "referential_integrity or field_catalog_resolves" -v
```

```python
from qc_engine.catalog import load_catalog, validate_referential_integrity
from qc_engine.ruleset import Check, Ruleset

catalog = load_catalog("p0/qc_engine/field_catalog.json")
assert catalog.get("occupancy_type") is not None
assert catalog.get("loan_program") is not None

chk = Check(id="t", name="t", field_name="insurance_docs_support_owner_occupancy",
            kind="predicate", predicate="is_true", severity="CRITICAL",
            applies_if=[{"field_name": "occupancy_type", "operator": "==", "value": "owner_occupied"}])
rs = Ruleset(ruleset_id="t", version=1, checks=[chk])
validate_referential_integrity(rs, catalog)  # must not raise
```

## SC-005 — zero regressions on the existing suite

```bash
cd p0 && python3 -m pytest -q
# expect: 325 passed (this feature's own new test files are additive and, once
# implemented, all-green; they do not modify engine.py/model.py/ruleset.py, so
# no existing test's behavior changes)
python3 harness.py
# expect: digest 82175d076579e31a50971d8b20ea4b63848bea9f9b53c30dd96524071842e5ec unchanged
```

## Non-regression companions (FR-004, FR-010 — named in tasks.md T034/T035)

```bash
cd p0 && python3 -m pytest tests/test_loan_profiles_v2.py -v   # v3 does not modify v2
cd p0 && python3 -m pytest tests/test_conditional_applicability.py \
                          tests/test_program_applicability_gating.py -v
# expect: both suites green, untouched by this feature's new applies_if
# producer/consumer pairing (FR-010: the two gating layers compose)
```
