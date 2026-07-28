# Run 004: YAML Rules Output (Single-Tier Approach)

## Overview

**Single-tier architecture:** Parse 5,365 mortgage rules → YAML format → Execute deterministically.

No intermediate Check objects. YAML is the source of truth.

### Why YAML?

- **SME-readable** — Underwriters can read and verify rules
- **Git-friendly** — YAML diffs are human-readable, version-controllable
- **Auditable** — Who changed which rule, when, and why (git history)
- **Deterministic** — Same YAML → same Python execution → same results
- **Portable** — Can be compiled to Rego (OPA), Drools, or custom engine later

## Architecture

```
demo/rules/*.xlsx (5,365 rows)
    ↓ [Bedrock, temp=0]
YAML rules (compile_runs/run_004_yaml_output/rules/)
    ↓ [Python executor]
Loan dispositions (AUTO_CLEARED vs NEEDS_REVIEW)
```

## File Structure

```
run_004_yaml_output/
├── run_yaml.py              # Compile rules → YAML
├── RESULTS.md               # Compilation metrics
└── rules/
    ├── fannie_mae/
    │   ├── FM-APPR-001.yaml
    │   ├── FM-APPR-002.yaml
    │   └── ...
    ├── fha/
    ├── va/
    └── usda/
```

## YAML Rule Schema

```yaml
---
metadata:
  rule_id: "FM-APPR-001"
  source_file: "Private Bank Oct 2025.xlsx"
  source_row: 42
  program: "Fannie Mae"
  version: 1
  created_at: "2026-07-22T00:00:00Z"

rule:
  title: "Appraisal Value vs Purchase Price"
  kind: "predicate"  # predicate, ratio_threshold, reconcile
  regulatory_source: "Fannie Mae B3-3.1-01"
  description: "Appraisal must be ≥80% of purchase price"
  
  condition: |
    appraisal_value >= (purchase_price * 0.80)
  
  verdict: "PASS"  # PASS, FAIL, WARNING
  action: "AUTO_CLEAR"  # AUTO_CLEAR, FLAG_FOR_REVIEW
  reason_tags: ["APPRAISAL_LOW"]
  
  citation:
    document: "Appraisal Summary 1004"
    field: "market_value"
    page: 1
```

## Execution Flow

```python
from qc_engine.yaml_executor import YAMLRulesExecutor

executor = YAMLRulesExecutor("rules/")
disposition = executor.evaluate_loan(
    loan_id="loan 01",
    loan_data={...extracted + MISMO + LOS...},
    program="Fannie Mae"
)

print(disposition.status)  # AUTO_CLEARED or NEEDS_REVIEW
print(disposition.review_reasons)  # [APPRAISAL_LOW, DTI_HIGH, ...]
```

## Next Steps

1. **Run compile:** `python3 run_yaml.py` ($242, 2-3 hrs)
2. **Review YAML:** SMEs audit the generated rules
3. **Execute:** Apply to loans 01-05 with yaml_executor.py
4. **Validate:** Measure accuracy against known outcomes
5. **Productize:** If validated, YAML becomes production format

## Cost & Timeline

- **Compilation:** $242 (Bedrock, one final run)
- **Generation:** ~2-3 hours
- **Execution:** ~1 minute (5 loans × Python evaluation)
- **Total:** ~$242 + 1 day (includes SME review)

## Why Not OPA/Rego (for now)?

OPA is a future optimization, not an MVP requirement. YAML + Python is:
- ✅ Simpler (no translation layer)
- ✅ Faster to validate (direct cause/effect)
- ✅ Still deterministic and auditable
- ✅ Can compile to OPA later if performance requires

## Status

- [ ] Generate YAML from Bedrock
- [ ] SME review YAML rules
- [ ] Test executor against loans 01-05
- [ ] Validate accuracy
- [ ] Deploy as production format
