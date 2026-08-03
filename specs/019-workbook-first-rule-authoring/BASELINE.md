> ⚠️ **Target superseded 2026-07-31, same day this was written** — see
> [decision 031](../../src/decisions/031-demo-target-is-touchless-not-synthetic-loans.md).
> The demo/audit target is now `demo/touchless/extracted/loan_application.json`, not
> `demo/syn/loan 01-05`. This document remains an accurate, reproducible record of what the
> synthetic-fixture pipeline does — it is **not** the baseline any future regression check
> should be measured against. Re-run Phase 0 against the Touchless loan before relying on one.

# Audit Baseline — restored 2026-07-31

**Phase 0 of `019-workbook-first-rule-authoring`.** `src/shacl_pilot/out/` had lost every
`loan_NN.json`/`loan_NN.ttl` it once ran against — only narrative `.md` reports survived. This
restores them and records the *real* number, per SC-001.

## Provenance

- Ruleset: `src/shacl_pilot/compiled/ruleset.json`, `ruleset_sha256`
  `6fa9840dc0205cb32401e8a4290341a9a67d5eb2d39113523cfdd8c85a26ccd6`, `rules_total: 4166`.
- Shapes: `src/shacl_pilot/shapes_manifest.json`, latest version (6th recorded) `combined_sha256`
  `9a24f2e9b5c0a419a40e4fde285e1566470a280123908596ef4b3c21414d7647`.
- Pipeline: `extract_loan.py` → `loan_to_rdf.py` → `run_full_ruleset_audit.py`, run against
  `demo/syn/loan 01`…`loan 05` (2026-07-30 synthetic fixtures).
- **Determinism verified**: each of the 5 audits was run twice; `diff` on the full stdout of both
  runs was empty for all 5 loans (byte-identical).

## The real number — NOT 25/25

Across all 5 loans, only **4 of 20,830 rule-loan pairs** (5 loans × 4,166 rules) reach a verdict —
**2 FAIL, 2 PASS**, all four on loan 01. Loans 02–05 reach **zero** verdicts each; every rule
resolves to `NOT_APPLICABLE`, `NO_DATA`, or `NOT_COMPILED`.

| Loan | FAIL | PASS | NOT_APPLICABLE | NO_DATA | NOT_COMPILED | Verdict reached / compiled+applicable |
|---|---|---|---|---|---|---|
| 01 | 2 | 2 | 1,673 (40.2%) | 47 (1.1%) | 2,442 (58.6%) | 4 / 51 |
| 02 | 0 | 0 | 3,207 (77.0%) | 23 (0.6%) | 936 (22.5%) | 0 / 23 |
| 03 | 0 | 0 | 3,477 (83.5%) | 18 (0.4%) | 671 (16.1%) | 0 / 18 |
| 04 | 0 | 0 | 1,673 (40.2%) | 51 (1.2%) | 2,442 (58.6%) | 0 / 51 |
| 05 | 0 | 0 | 3,922 (94.1%) | 2 (0.0%) | 242 (5.8%) | 0 / 2 |

The 2 FAILs (loan 01 only): **"Unsourced large deposit"** — `$15,000` on 2025-08-12 exceeds 50% of
monthly qualifying income (`$7,916...`), fired on both `O-FNM-00215` and `O-FRD-50451` (the same
underlying check, both a Fannie and a Freddie variant of the same Exception Code family). The 2
PASSes: `CoBorrowerSectionCompleteShape` did not fire (2 rules).

## What this means (per spec.md's own instruction: stop, don't proceed on a stale premise)

Whatever the prior "25/25" or similar figure referred to (CLAUDE.md's *separate* Standing Gate,
`p0/fixtures/from_docs/verify_against_defects.py`, is a different pipeline — Pipeline B / `p0/qc_engine`
— not this SHACL pilot; the two numbers should never be conflated), **this pipeline's real,
reproducible baseline is 4/20,830, concentrated entirely in loan 01**. Loans 02-05 currently exercise
zero compiled-and-applicable shapes with real data. This matches — and quantifies — spec.md's own
finding that only 4 of 28 authored shapes are reachable via `eval_target` (§ FR-015), and 20/28 use the
plain triple-pattern form Phase 5's compiler can template while the rest are hand-authored logic.

**This is the finding Phase 0 was designed to surface. Per plan.md: "report it and stop for a scope
decision rather than proceeding on a stale premise."** Restoring more loan coverage (getting shapes to
fire meaningfully on loans 02-05) is a distinct, larger body of work from Phases 1-5 of this spec
(which build the *authoring* pipeline, not new detection logic) — continuing into Phase 5's "did we
regress" comparison is valid against *this* baseline, but expanding loan coverage itself is out of
this spec's scope and needs its own decision.

## Raw artifacts

Full stdout of both determinism runs, and the restored `loan_NN.json`/`loan_NN.ttl` pairs, are in
`src/shacl_pilot/out/`.
