# Criteria: 005 Eval Harness as Promotion Gate

Executable, not prose — each maps directly to spec.md's Success Criteria.

## SC-001 — A registered scenario-construction strategy for all 6 live check kinds

```bash
cd p0 && python3 -m pytest tests/test_scenario_construction.py -v
# expect: test_construct_scenario_predicate_is_true/is_present,
#         test_construct_scenario_ratio_threshold_ltv/dti,
#         test_construct_scenario_agree_categorical,
#         test_construct_scenario_agree_numeric,
#         test_construct_scenario_agree_doc_categorical/doc_numeric
#         all PASS -- one test per kind, zero hand-written per-field mutation
#         code in the test bodies (each Check is built generically from a
#         real field_catalog.json entry, not a fixed demo field).
```

```python
import scenario_construction as SC
assert set(SC.STRATEGIES.keys()) == {
    "predicate", "ratio_threshold", "agree_categorical", "agree_numeric",
    "agree_doc_categorical", "agree_doc_numeric",
}
```

## SC-002 — COVERAGE against a real compiled ruleset, zero hand-written mutation code

```python
import json, os
from qc_engine.ruleset import Check
import coverage_set

# result/rules/comprehensive_e2e_v6_ruleset.json (run_013) -- a real compiled
# artifact, not a synthetic stand-in.
with open("../result/rules/comprehensive_e2e_v6_ruleset.json") as f:
    content = json.load(f)["content"]
checks = [Check(**c) for c in content["checks"]]
from qc_engine.ruleset import Ruleset
ruleset = Ruleset(ruleset_id=content["ruleset_id"], version=content["version"], checks=checks)

result = coverage_set.compute_coverage(ruleset)
# every check in this artifact is predicate / ratio_threshold / agree_categorical
# (SC-001's covered kinds) -- coverage must be complete, no gaps.
assert result.checks_covered == result.checks_total
assert result.coverage_fraction == 1.0
print(f"COVERAGE: {result.checks_covered}/{result.checks_total} "
      f"({result.coverage_fraction:.1%}) on a real {result.checks_total}-check "
      f"compiled ruleset -- zero hand-written per-field mutation code added.")
```

```bash
cd p0 && python3 -m pytest tests/test_coverage_set.py -v
# expect: full coverage across all 6 kinds when registered, correct
# decrement + named gap when one kind's strategy is deliberately removed.
```

## SC-003 — An injected false-auto-clear defect blocks promotion, names the offender

```bash
cd p0 && python3 -m pytest tests/test_promotion_gate.py::test_injected_false_auto_clear_blocks_promotion -v
```

```python
import promotion_gate
result = promotion_gate.run_promotion_gate(candidate=miswired_ruleset, volume_loans=[...])
assert result.exit_code != 0
assert result.promotion_decision == "BLOCK"
named = result.false_auto_clears[0]
assert named["check_id"] and named["loan_id"] and named["expected"] == "FAIL" and named["actual"] == "PASS"
```

## SC-004 — A single flipped verdict is reported exactly once by GOLDEN

```bash
cd p0 && python3 -m pytest tests/test_golden_set.py::test_golden_replay_reports_exactly_one_flip -v
```

```python
import golden_set
result = golden_set.replay_golden_panel(candidate=candidate_rs, baseline=baseline_rs,
                                        panel=isolated_one_case_panel, panel_version="test-v0")
assert len(result.regressions) == 1
# no more, no fewer -- not aggregated into a bare count.
```

## SC-005 — VOLUME reports auto_clear_rate; zero on clean, non-zero (BLOCK) on defect-injected

```bash
cd p0 && python3 -m pytest tests/test_promotion_gate.py::test_volume_tier_reports_auto_clear_rate_and_zero_false_clears_on_clean_candidate tests/test_promotion_gate.py::test_volume_tier_false_auto_clear_count_nonzero_triggers_block -v
```

```python
clean = promotion_gate.run_promotion_gate(candidate=demo_ruleset(), volume_loans=G.generate(200))
assert clean.volume["false_auto_clear_count"] == 0
assert 0.0 <= clean.volume["auto_clear_rate"] <= 1.0

defective = promotion_gate.run_promotion_gate(candidate=miswired_ruleset, volume_loans=[bad_loan])
assert defective.volume["false_auto_clear_count"] > 0
assert defective.promotion_decision == "BLOCK"
```

## SC-006 — Full existing test suite passes, zero regressions

```bash
cd p0 && python3 -m pytest tests -v
python3 -m pytest eval_synth/test_properties.py -v
python3 harness.py
# expect: 0 failed across all three (this feature's own new modules
# gated separately -- see SC-001..SC-005 above); harness.py's bit-exact
# digest must be byte-identical to the pre-005 baseline (this feature adds
# NEW evaluation *of* rulesets, it must not change the engine's own
# evaluation behavior, spec.md Technical Context "Constraints").
```
