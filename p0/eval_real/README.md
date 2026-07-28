# `eval_real` — real-loan distribution eval (012)

Sibling package to `p0/eval_synth/`. Ingests already-acquired real closed loans
as an additional GOLDEN/VOLUME source into `005`'s promotion gate, proves
`007`'s audit chain against real (not synthetic) citations, and re-runs the
G3 bake-off methodology once expert labels exist. See
`specs/012-real-loan-distribution-eval/` for the full spec/plan/tasks.

## What's here

| Module | Does |
|---|---|
| `adapter.py` | `RealLoanAdapter.adapt(bundle_dir, loan_id, expected_verdicts)` — converts one loan's extraction bundle (`{loan}-ulad.json` + `{loan}-citations.json` + `consolidated/*.json`) into the exact `LabeledLoan` tuple `eval_synth.test_properties.score()` already accepts. Unmapped field names land in `MappingGapReport`, never silently dropped. |
| `mapping_gaps.py` | `MappingGap`/`MappingGapReport` — the named list of extracted fields with no `field_catalog.json` counterpart. |
| `audit_trace.py` | `run_and_append(loan, ruleset, audit_log, signed_at)` runs the unmodified engine + appends to a real `AuditLog`; `build_examiner_trace(run_result, check_id)` renders a human-readable, examiner-walkable trace. |
| `bakeoff_real.py` | `run_bakeoff_real(loan, ruleset, expert_labels, evaluate_fn)` re-runs G3's locked D1/D2/D3 methodology (imports `experiment_g3.bakeoff`'s pricing table, unmodified) against one real loan. D2 (accuracy) reports `BLOCKED` when no expert labels exist yet; D3 (cost/token) always reports. |
| `pii_scan.py` | `scan_paths`/`assert_clean` — the PII scan gate (FR-012/SC-004). Never hardcode a real pattern into this module; load it from a local, gitignored file via `load_known_patterns_file`. |
| `s3_client.py` | Read-only `boto3` wrapper (profile `gordon-chan`) for `s3://mortgage-qc-extraction/results/`. Not part of `pytest p0/tests` — needs live AWS creds, mirrors `experiment_g3/llm_arm.py`'s own exclusion. |

## PII rule (FR-012), in plain language

The 3 real loans this feature targets carry real borrower names, SSN
fragments, and a real property address. **Never let a raw real value reach a
git-tracked file.** Concretely:

- Fetch real bundles with `s3_client.download_bundle(loan_id, "p0/eval_real/local_cache/<loan_id>")` — that directory is `.gitignore`-excluded.
- Before committing anything this package produces that might carry a real
  value (an adapted-loan dump, an eval report, an examiner-trace report),
  run `eval_real.pii_scan.assert_clean(paths, patterns)` against the exact
  real values named in `specs/012-real-loan-distribution-eval/spec.md`'s
  Foundation section (or a local pattern file loaded via
  `load_known_patterns_file`). It raises `PiiScanGateError` loudly if
  anything matches — fix it before committing, don't silence the gate.
- If you need to keep an example artifact in git (e.g. a redacted examiner
  trace), redact the PII substring only — never the rule id / hash / verdict
  fields, per FR-012's own limitation note (stable-but-not-salted redaction
  is an accepted, documented risk for this internal eval corpus; see
  spec.md FR-012's own caveat before widening this to a public artifact).

## Running the manual/live pieces (never part of `pytest p0/tests`)

```bash
cd p0
python3 -c "
from eval_real.s3_client import list_loan_prefixes, download_bundle, KNOWN_REAL_LOAN_IDS
print(list_loan_prefixes())
for loan_id in KNOWN_REAL_LOAN_IDS:
    download_bundle(loan_id, f'eval_real/local_cache/{loan_id}')
"
python3 -c "
from eval_real.adapter import RealLoanAdapter
a = RealLoanAdapter()
loan, expected, prov = a.adapt('eval_real/local_cache/301224293', '301224293', {})
print(loan.loan_id, len(loan.fields), 'fields;', a.last_mapping_gap_report.gap_count, 'gaps')
"
```

The G3 real-Bedrock cost measurement (`bakeoff_real.run_bakeoff_real` with
`llm_arm.evaluate_llm` as `evaluate_fn`) and the accuracy/D2 re-run both need,
respectively, live Bedrock credentials and an `ExpertLabelSet` that does not
exist yet (G1) — see spec.md's Assumptions/Risks for exactly what's gated on
which external dependency.
