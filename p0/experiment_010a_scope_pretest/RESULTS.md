# 010a Scope Pre-Test — Results

Real proof, zero new Bedrock spend: reuses the 24 already-compiled real
checks from `experiment_002a` (2026-07-01 compile-fidelity spike) and
runs `program_gating.py`'s real applicability mechanism against the 5
real synthetic loan fixtures, under the `RULE-PROGRAM-GATING-FINDINGS.md`
§8 pre-test assumption (loan 01 + loan 04 assumed Fannie Mae).

## Finding: a real fixture-label bug, surfaced by this pre-test

`program_gating._loan_program()` reads `CanonicalLoan.loan_type` — a
hand-typed descriptive string, not a value derived from the loan's real
MISMO data. Loan 04's label (`"Freddie Mac Cash-Out Refi"`, set in
`build_fixtures.py`'s `LOAN_PACKAGES`) happens to contain the substring
`"Freddie Mac"`, so **the code today resolves loan 04 to Freddie Mac
unambiguously — not `AMBIGUOUS`** — purely because of that label, even
though loan 04's real MISMO `<MortgageType>` is just `"Conventional"`,
identical in kind to loan 01's genuinely-ambiguous case. Loan 01's label
(`"Conventional Purchase"`) carries no GSE marker, so it correctly
resolves to `None`/ambiguous. The two loans are equally undetermined by
real data; only one of their fixture labels happens to leak an answer.

This pre-test does NOT fix that — it applies the §8 assumption via an
explicit override (`LOAN_PROGRAM_OVERRIDE` in this script) instead of
trusting the label, so the pre-test's own scope decision is honored
consistently for both loans. The underlying fixture-label bug is a
separate, real finding for `build_fixtures.py` — flagged, not fixed
here, since `010a`'s own test (`test_program_applicability_gating.py`)
explicitly mirrors this exact label as its Freddie-tagged test case and
a fix needs to account for that.

## Effective program per loan (this pre-test)

- `loan_01`: **Fannie Mae**
- `loan_02`: **FHA**
- `loan_03`: **VA**
- `loan_04`: **Fannie Mae**
- `loan_05`: **USDA**

## Result

- Real compiled checks available (from `002a`): 24
- Relevant to the 5 loans under this scope: **17**
- Dropped (untagged prefix, e.g. TILA/COVID19-FRD/FAMCO, or Freddie Mac now out of scope): 7

## Per-loan applicable-check counts (of the 24)

- `loan_01`: 8 checks
- `loan_02`: 5 checks
- `loan_03`: 1 checks
- `loan_04`: 8 checks
- `loan_05`: 3 checks

## Relevant checks (real compiled Check IDs, tied to real loans)

- `fha-refi-pay-history-req` (O-FHA-50724, FHA) -> applies to: loan_02
- `o-fnm-15430-homestyle-completion-cert` (O-FNM-50322, Fannie Mae) -> applies to: loan_01, loan_04
- `rov-disclosure-at-application` (O-FNM-59136, Fannie Mae) -> applies to: loan_01, loan_04
- `va-vet-paid-fees-invoice-missing` (O-VA-58591, VA) -> applies to: loan_03
- `o-fnm-15453-du-data-reliability` (O-FNM-00717, Fannie Mae) -> applies to: loan_01, loan_04
- `fnm-15438-cbrs-flood-insurance` (O-FNM-00574, Fannie Mae) -> applies to: loan_01, loan_04
- `sect8-voucher-income-used` (O-RHS-50569, USDA) -> applies to: loan_05
- `fha-family-loan-hud-criteria-documented` (O-FHA-00258, FHA) -> applies to: loan_02
- `fnm-15433-community-second-allowable-party` (O-FNM-50916, Fannie Mae) -> applies to: loan_01, loan_04
- `fha-military-les-present` (O-FHA-02283, FHA) -> applies to: loan_02
- `fnm-15438-flood-ins-deductible` (O-FNM-56261, Fannie Mae) -> applies to: loan_01, loan_04
- `fnm-15330-boarder-residency-docs` (O-FNM-00432, Fannie Mae) -> applies to: loan_01, loan_04
- `o-rhs-15667-mfg-home-warranty-docs-present` (O-RHS-02868, USDA) -> applies to: loan_05
- `o-fha-15265-min-credit-score-500` (O-FHA-50719, FHA) -> applies to: loan_02
- `o-fha-15191-rental-income-75pct-fmr` (O-FHA-51275, FHA) -> applies to: loan_02
- `o-rhs-15680-revolving-5pct-payment` (O-RHS-02838, USDA) -> applies to: loan_05
- `o-fnm-15397-sfc162-ssn-discrepancy` (O-FNM-56092, Fannie Mae) -> applies to: loan_01, loan_04

## Dropped checks (untagged prefix or out of pre-test scope)

- `covid19-frd-14443-employment-continuity-due-diligence` (COVID19-FRD-52435, program=None)
- `o-frd-16286-irs-installment-agreement-present` (O-FRD-56574, program=Freddie Mac)
- `o-fed-14351-payment-calc-greater-rate` (O-TILA-01676, program=None)
- `projected-income-60day-validation` (O-TILA-01718, program=None)
- `o-frd-15596-coverage-threshold` (FAMCO-FNM-00825, program=None)
- `o-frd-15463-auth-user-act-dti` (O-FRD-58857, program=Freddie Mac)
- `o-frd-15611-credit-conflict-resolved` (O-FRD-00014, program=Freddie Mac)
