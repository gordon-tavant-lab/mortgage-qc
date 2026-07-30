# 007 — Loan 01 is the accuracy gauge; loans 02–05 are the generalization test

**Status:** Accepted 2026-07-29 (Gordon)

## Decision
- **Loan 01** (Conventional purchase, 5 defects in `p0/fixtures/from_docs/
  defect_manifest.json`) is the *gauge*: the pilot must hold 5/5 detection on it after
  every shapes change (regression baseline, analogous to p0's loan-01 defect gate).
- **Loans 02–05** (FHA / VA ARM / Freddie cash-out / USDA) are the *generalization
  test*, reconciled against Gordon's new answer key `demo/syn/Answers.md`
  (5 defects each, 20 total; 25 across all five loans).
- The pilot must audit **all five loans**, selecting the right route per loan
  (see decision 005) — cross-loan false positives count against it just as much as
  missed defects.

## Success bar
25/25 defects detected across loans 01–05, deterministic across double runs, zero
unexpected extra violations (or each extra individually justified), citations attached
to every finding.

## Evidence
- `demo/syn/Answers.md` — Gordon-authored ground truth for loans 02–05 (5 defects each).
- `src/shacl_pilot/answer_keys/loan_01_answers.md` — loan 01's 5 defects, transcribed into `src/` (decision 011 isolation; supersedes reading `p0/fixtures/from_docs/defect_manifest.json` at runtime, which the v1 runner `src/shacl_pilot/run_shacl_audit.py` did).
- `src/shacl_pilot/run_audit.py` — reconciles all five loans against both keys, counts MISSED and EXTRA (unexpected FAIL) findings, exits non-zero unless 25/25 with no extras and deterministic ("Exit 0 only if: 25/25 answer-key defects detected, no unexpected extra FAILs…", docstring line 19).
- `src/shacl_pilot/out/loan_01_extraction.json` … `loan_05_extraction.json` — all five loans extracted and audited, not just loan 01.
