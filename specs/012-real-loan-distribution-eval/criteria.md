# Criteria: 012 Real-Loan Distribution Eval

Executable, not prose — each maps directly to spec.md's Success Criteria.

**SAFETY NOTE (read before running anything real):** SC-001/SC-002/SC-003's *live* variants require
the 3 already-acquired real closed loans in S3 and carry real borrower PII (see spec.md's Foundation
section and Risks). Nothing below hardcodes a real loan id, real PII value, or real S3 path — every
snippet either (a) uses a hand-authored synthetic stand-in, runnable in CI with zero credentials, or
(b) is explicitly marked LIVE/MANUAL, requiring the `gordon-chan` AWS profile and never run as part of
`pytest p0/tests`.

## SC-001 — All 3 real loans convert + score with zero adapter crashes

CI-safe check (synthetic stand-ins, proves the adapter mechanism):
```bash
cd p0 && python3 -m pytest tests/test_real_loan_adapter.py -v
```
Live/manual check (the actual SC-001 claim, against the real loans):
```bash
# requires AWS profile 'gordon-chan' + read access to the real S3 bucket named
# in spec.md's Foundation section. NOT part of `pytest p0/tests`.
python3 p0/eval_real/run_real_loans_manual.py   # to be written per tasks.md T012/T027
# expect: "3/3 loans adapted, 0 crashes" in stdout
```

## SC-002 — verify_chain() True for a real AuditLog, False after tamper

```bash
cd p0 && python3 -m pytest tests/test_real_loan_audit_trace.py -v -k "verify_chain"
```
```python
# equivalent inline check, once eval_real.audit_trace exists:
from qc_engine import AuditLog
from eval_real.audit_trace import run_and_append
log = AuditLog(":memory:")
run_and_append(adapted_loan, ruleset, log, signed_at="2026-07-27T00:00:00Z")
assert log.verify_chain() is True
log.conn.execute("UPDATE audit_runs SET payload_json = ? WHERE seq = 1", ('{"tampered": true}',))
log.conn.commit()
assert log.verify_chain() is False
```

## SC-003 — >=2 examiner-trace reports (1 PASS, 1 FAIL/FLAG), independently walkable

```bash
cd p0 && python3 -m pytest tests/test_real_loan_audit_trace.py -v -k "examiner_trace"
```
```python
trace_pass = build_examiner_trace(run_result, "<check-id-that-passed>")
trace_fail = build_examiner_trace(run_result, "<check-id-that-failed>")
for t in (trace_pass, trace_fail):
    assert t["ruleset_version"] and t["ruleset_sha256"]
    assert t["inputs"]
    assert "narrative" in t and t["narrative"]
    if t.get("citation"):
        assert t["citation"]["doc_name"] and t["citation"]["page_num"] is not None
```

## SC-004 — Zero real PII values in any committed artifact

```bash
cd p0 && python3 -m pytest tests/test_pii_scan_gate.py -v
```
```python
# the actual gate, run against every path this feature's work touches:
from eval_real.pii_scan import assert_clean
assert_clean(changed_git_tracked_paths, patterns=known_real_pii_patterns_from_local_gitignored_file)
# raises PiiScanGateError (loud, not silent) if anything matches.
```

## SC-005 — G3 bake-off real-loan re-run: D1/D2 reported if labeled, else explicit BLOCKED

```bash
cd p0 && python3 -m pytest tests/test_bakeoff_real.py -v
```
```python
report = run_bakeoff_real(loan, ruleset, expert_labels=None, evaluate_fn=...)
assert report["d2_accuracy"]["status"] == "BLOCKED"
assert report["d2_accuracy"]["reason"]  # never silently omitted

report = run_bakeoff_real(loan, ruleset, expert_labels={"chk-x": "PASS"}, evaluate_fn=...)
assert report["d2_accuracy"]["status"] != "BLOCKED"
assert "exact_match_rate" in report["d2_accuracy"]
```

## SC-006 — Real, measured token count + cost-at-10k-loans figure

```bash
cd p0 && python3 -m pytest tests/test_bakeoff_real.py -v -k "d3_cost"
```
```python
report = run_bakeoff_real(loan, ruleset, expert_labels=None, evaluate_fn=...)
d3 = report["d3_cost"]
assert d3["token_count"] > 0
assert d3["cost_at_10k_loans_usd"] >= 0
```
Live/manual check (the actual measured number, against a real full-extraction payload):
```bash
# requires AWS profile 'gordon-chan'. NOT part of `pytest p0/tests`.
python3 p0/eval_real/bakeoff_real.py --loan <adapted-real-loan-path> --measure-cost-only
# expect: a real, non-"$700-$3,500 reasoned" token count + cost figure in stdout
```

## SC-007 — Zero regression against the existing suite + bit-exact digest

```bash
cd p0 && python3 -m pytest -q
cd p0 && python3 -m pytest eval_synth/test_properties.py -q
cd p0 && python3 harness.py   # bit-exact determinism digest
# expect: 0 failed in all three; harness.py's digest unchanged from its
# pre-012 committed value
```
