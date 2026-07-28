# Implementation Plan: Real-Loan Distribution Eval

**Branch**: `012-real-loan-distribution-eval` | **Date**: 2026-07-27 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/012-real-loan-distribution-eval/spec.md`

## Summary

Ingest the 3 already-acquired real closed loans (`301224293`, `301224442`, `301224735`,
`s3://mortgage-qc-extraction/results/`) as an additional GOLDEN/VOLUME source into `005`'s tiered
promotion gate, via a new adapter that converts each loan's real extraction bundle into the exact
`LabeledLoan` tuple shape the scorer already accepts — no scorer rework beyond one narrow, disclosed
hardening (FR-003). Prove `007`'s already-built audit hash chain and citation trail against real
(not synthetic) citations for the first time (the mock-audit exit criterion). Re-run the G3 bake-off's
locked methodology against real loans once expert-adjudicated labels exist for at least one check, and
independently measure a real-payload cost/token figure that finally replaces the roadmap's own
"reasoned, not computed" $700-$3,500/10k-run estimate with an actual number. Loan *acquisition* is not
built here (confirmed already done by direct S3 inspection); expert-label *authoring* is not built here
either (G1, Kayla/SME) — this feature is the adapter, the audit proof, and the bake-off re-run
mechanics, plus the PII-handling discipline none of those three can responsibly ship without.

## Technical Context

**Language/Version**: Python 3.9-compatible (project-wide constraint).
**Primary Dependencies**: `boto3` (reused pattern from `p0/experiment_g3/llm_arm.py`'s existing
`PROFILE='gordon-chan'` Bedrock session setup) for read-only S3 access to the already-acquired real
loan bundles under `s3://mortgage-qc-extraction/results/`. No other new dependency — reuses
`qc_engine.model` (`CanonicalLoan`/`SourceValue`/`DocCitation`), `qc_engine.engine.run`,
`qc_engine.audit` (`AuditLog`/`verify_chain`), `qc_engine.ruleset`, `field_catalog.json`, and
`p0/experiment_g3/bakeoff.py`/`llm_arm.py` — all existing.
**Storage**: The real loan bundles remain in S3, read at run time, never copied wholesale into this
repository. A new local-only, `.gitignore`-excluded cache directory holds fetched raw bundles and any
report that would otherwise carry a real value; only redacted/aggregate artifacts (mapping-gap counts,
hash-only loan identities, cost/token numbers with no PII) land in git-tracked paths. No database.
**Testing**: `pytest p0/tests -v` (existing suite, zero-regression bar) plus new test modules covering
the adapter against a small, hand-authored **synthetic stand-in bundle** that mirrors the real S3
shape (so CI needs no live AWS credentials) — the live-bucket run is a documented, manual, non-CI
integration check, consistent with this project's existing pattern of keeping AWS-dependent runs
outside the default test suite (`p0/experiment_g3/llm_arm.py` is likewise not part of `pytest p0/tests`).
**Target Platform**: Local execution + local AWS profile (`gordon-chan`) for the manual real-bucket
run; no service, no specific CI vendor for the automated half.
**Project Type**: Library/CLI extension — a new `p0/eval_real/` package alongside the existing
`p0/eval_synth/`, plus one narrow, disclosed patch inside `p0/eval_synth/test_properties.py` (FR-003).
No UI.
**Performance Goals**: Adapting one real loan (up to 348 documents, 67 extracted fields) is a one-time,
offline conversion — no latency budget beyond "faster than a human reading the same bundle." The G3
real-loan re-run reuses `llm_arm.py`'s existing per-loan Bedrock call pattern; cost/token measurement
is the point of that call, not a performance target to optimize.
**Constraints**: Zero regression against the existing suite and `p0/harness.py`'s bit-exact digest
(SC-007) — this feature evaluates real loans, it does not change engine behavior. No runtime LLM call
inside the deterministic path (FR-014 — the only LLM call this feature makes is Arm B's own governed,
config-time-equivalent bake-off comparison, exactly mirroring `p0/experiment_g3`'s own precedent, never
inside `qc_engine.engine.run` itself). Python 3.9 syntax only. **Hard constraint, not a preference:**
no raw real-loan PII value may reach a git-tracked path (FR-012/SC-004).
**Scale/Scope**: 3 real loans, up to 348 documents/loan, 379-entry `field_catalog.json` as the mapping
target, 1 audit chain proof, 1 G3-methodology re-run (accuracy half conditional on labels; cost half
unconditional). Does not include building real-loan acquisition (done) or expert-label authoring (G1).

## Constitution Check

*GATE: evaluated against `.specify/memory/constitution.md` v1.1.1.*

| Principle | Status | Note |
|---|---|---|
| I — Determinism of the *correct* computation | PASS | The adapter and audit-trace tooling touch nothing at runtime inside `qc_engine.engine.run` — they consume its output. The G3 real-loan re-run's Arm B call is, like the original G3, a bake-off *comparison* artifact, not a runtime path the compiled engine depends on (Arm A remains the deterministic path under test). |
| II — Compile, then run | PASS | No LLM call is added to the compile-then-run pipeline itself. Arm B's bake-off call is explicitly the *alternative being measured against*, per G3's own precedent — not a new runtime dependency this feature introduces into the product. |
| III — Eval is foundational | PASS (this feature is the item III's own decomposition names as the honest residual) | Directly answers Principle III's third, real-loan-only question ("defect distribution + extraction/OCR realism") for the first time — while FR-015 explicitly preserves the synthetic eval as the regression floor, per Principle III's own closing sentence ("real loans... become the distribution check with no harness rework"). |
| IV — Build the core, assume the periphery | PASS | No document extraction is rebuilt — FR-006's extraction-pattern addition for the real bundles' *own already-classified* QC documents is a narrow, additive extension of the existing consumed-extraction-contract pattern (`001b`), not a rebuild of Touchless-equivalent extraction from scratch. |
| V — Source independence | PASS | The real loans' own `{loan}-citations.json` already carries genuinely independent doc-vs-XML discrepancy pairs (real closing-doc text vs. real system/XML value) — this is *stronger* independence evidence than synthetic construction, since it wasn't authored to be independent, it simply is (real doc extraction vs. real system export). |
| VI — Configurable by non-technical users | N/A this feature | No authoring-surface change — internal eval/audit mechanism. |
| VII — Configuration is authored data | PASS | The adapter's referential-integrity behavior (FR-004: an unresolved field name is named, never silently dropped) mirrors `005`'s own precedent of deferring to the existing SAFE-gate mechanism rather than reimplementing it. |

**One named tension, not a violation:** FR-012 (PII exclusion) is a genuinely new constraint this
project's constitution does not itself name (it predates any real-PII-bearing data path) — flagged
honestly in Complexity Tracking below as a scope addition this feature introduces to the project's own
practice, not a principle it stretches or bends.

## Project Structure

### Documentation (this feature)

```text
specs/012-real-loan-distribution-eval/
├── spec.md
├── plan.md                  # This file
├── tasks.md                 # Phase 2 output (/speckit-tasks)
└── checklists/
    └── requirements.md
```

No `research.md`/`data-model.md`/`contracts/` — deliberately omitted, following `005`'s own precedent:
this feature promotes an already-designed pattern (the `LabeledLoan` tuple seam, the already-built
audit chain, the already-locked G3 methodology) into a real-loan-facing adapter, rather than researching
a new mechanism from scratch. The "research" this plan would otherwise capture is the direct S3/code
inspection already recorded in spec.md's Foundation section.

### Source Code (repository root)

```text
p0/eval_real/                        # NEW package, sibling to p0/eval_synth/
├── adapter.py                       # RealLoanAdapter: S3 bundle -> CanonicalLoan +
│                                     #   LabeledLoan-shaped tuple (FR-001/002); reads
│                                     #   {loan}-ulad.json + {loan}-citations.json +
│                                     #   consolidated/*.json; maps real field names onto
│                                     #   field_catalog.json canonical names
├── mapping_gaps.py                  # NEW — MappingGapReport: records every real extracted
│                                     #   field with no field_catalog.json counterpart (FR-004)
├── qc_doc_extraction.py             # NEW — extraction patterns for the real bundles' own
│                                     #   already-classified, field-unextracted third-party QC
│                                     #   documents (Snapdocs report, DUAL AUS audit, FraudGuard
│                                     #   summary, etc. — FR-006); mirrors 000's own
│                                     #   doc_patterns/*.json label-anchored regex convention
├── audit_trace.py                   # NEW — ExaminerTraceReport builder (FR-007/008): runs
│                                     #   qc_engine.engine.run against an adapted real loan,
│                                     #   appends to a real qc_engine.audit.AuditLog, calls
│                                     #   verify_chain(), and renders a per-verdict human-
│                                     #   readable trace (rule id/version/hash, inputs,
│                                     #   rounding, verdict, real DocCitation)
├── bakeoff_real.py                  # NEW — re-runs p0/experiment_g3/bakeoff.py's locked
│                                     #   methodology against a real, adapted loan + whatever
│                                     #   expert-labeled subset exists (FR-009/011); measures
│                                     #   Arm B's real per-loan token count/cost independent of
│                                     #   labels (FR-010), reusing llm_arm.py's Bedrock session
├── pii_scan.py                      # NEW — SC-004's explicit scan/grep gate: checks a set of
│                                     #   git-tracked paths for real-loan PII patterns (borrower
│                                     #   names sourced from the loan bundle itself, ssn_last4
│                                     #   values, the real property address) before any commit
│                                     #   touching this feature's output
├── s3_client.py                     # NEW — thin boto3 wrapper (profile 'gordon-chan'),
│                                     #   mirroring llm_arm.py's existing session-setup pattern;
│                                     #   read-only, no write path to the source bucket
└── local_cache/                     # NEW, .gitignore-excluded — raw fetched S3 bundles land
                                     #   here only; never committed (FR-012)

p0/eval_synth/
└── test_properties.py               # MODIFIED (FR-003, minimal, disclosed) — one call site
                                     #   hardened: prov['mutations'] -> prov.get('mutations', [])
                                     #   inside score()'s mismatch-message formatting; no other
                                     #   change to score()'s signature or behavior

p0/experiment_g3/
├── bakeoff.py                       # UNMODIFIED — re-invoked by bakeoff_real.py, not edited
└── llm_arm.py                       # UNMODIFIED — its Bedrock session pattern is reused
                                     #   (imported), its own logic untouched

p0/qc_engine/audit.py                # UNMODIFIED — AuditLog/verify_chain consumed exactly as
                                     #   built by 007; this feature is the first real-loan proof
                                     #   of an already-complete mechanism, not a new one

p0/tests/
├── test_real_loan_adapter.py        # NEW — SC-001: a small, hand-authored SYNTHETIC stand-in
│                                     #   bundle mirroring the real S3 shape (so CI needs no
│                                     #   live AWS creds) proves adapter correctness + mapping-
│                                     #   gap reporting; the LIVE 3-real-loan run is a separate,
│                                     #   documented manual script (not part of `pytest p0/tests`)
├── test_real_loan_audit_trace.py    # NEW — SC-002/003: verify_chain() True/False (tamper
│                                     #   simulation) against a real-shaped AuditLog; examiner-
│                                     #   trace report structure checks
├── test_pii_scan_gate.py            # NEW — SC-004: confirms pii_scan.py actually detects a
│                                     #   planted PII-shaped string in a test fixture (a scan
│                                     #   gate that has never been proven to catch anything is
│                                     #   not a real gate)
└── test_p0.py                       # UNMODIFIED — existing regression suite, re-run for SC-007

.gitignore                          # MODIFIED — add `p0/eval_real/local_cache/` with a comment
                                     #   matching the existing `demo/` PII-risk convention
```

**Structure Decision**: New capability lands as a new sibling package (`p0/eval_real/`) to the existing
`p0/eval_synth/`, matching `005`'s own precedent of adding new modules to an existing package family
rather than a parallel top-level structure. The one existing-file edit (`test_properties.py`'s
`prov.get(...)` hardening) is deliberately the smallest possible surface area, consistent with `005`'s
own FR-013 precedent of not touching prior spike/production code beyond what's strictly necessary.
`p0/eval_real/local_cache/` is the one genuinely new structural element this feature requires that no
prior spec needed — a local-only real-data cache with its own `.gitignore` entry — because this is the
first feature in this repository's history to touch real, PII-bearing loan data at all.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| New PII-exclusion discipline (FR-012, `local_cache/`, `pii_scan.py`) not required by any prior spec | This is the first feature to ingest real, PII-bearing loan data into this repository's working tree at all | Skipping it (treating real loans exactly like synthetic ones, writing full artifacts straight to `p0/eval_real/`) was rejected outright — it would commit real borrower names/SSNs/addresses to git history, an irreversible mistake a `.gitignore` entry and a scan gate prevent for the cost of one small new module |
