# Compile Run 001 — 5-Loan Scope, First Real Tranche

**Status: real, unsigned, referential-integrity-screened candidate checks — NOT yet SME-reviewed or signed off.** Real Bedrock calls (Sonnet 4.6, temperature=0), real cost, real per-row parse results. First bounded tranche of the real rules-parsing process, drawn from the 5,365-row scope in `output/RULE-PROGRAM-GATING-FINDINGS.md` §8.

## Result

- Rows attempted: 39
- Compiled successfully: 39
- Parse failures: 0 (none)
- Grounded (had a signed KB to retrieve from — FHA only, from 002c): 8 (FHA-000, FHA-001, FHA-002, FHA-003, FHA-004, FHA-005, FHA-006, FHA-007)
- Referential integrity: **PASSED**
- New fields proposed: 39

## Real cost (measured, not estimated)

- Total input tokens: 531,049
- Total output tokens: 11,510
- Real spend this run: **$1.7658**
- Real cost per row: **$0.04528**

## Extrapolation to the full 5,365-row §8 scope

- Rows compiled so far: 39
- Rows remaining: 5326
- Estimated cost for the remaining rows: **$241.14**
- Estimated cost for the full 5,365-row scope: **$242.91**

This is a linear extrapolation off this run's real average — actual full-scope cost will vary with row length/complexity, but this is real measured data, not the earlier full-extraction-payload estimate from `THESIS.md` (which measured a different thing — running the QC engine over loan files, not compiling rule rows).

## Compiled checks (this tranche)

- `purchase-eligibility-requirements-met` (predicate, program=Fannie Mae)
- `homereready-borrower-income-limit-eligible` (predicate, program=Fannie Mae)
- `fnm-title-ownership-6mo` (predicate, program=Fannie Mae)
- `w2-rsu-two-year-present` (predicate, program=Fannie Mae)
- `voe-1005-all-fields-complete` (predicate, program=Fannie Mae)
- `mixed-use-appraisal-requirements-met` (predicate, program=Fannie Mae)
- `fnm-15939-single-close-const-ltv` (ratio_threshold, program=Fannie Mae)
- `qc-income-employment-reverification-validated` (predicate, program=Fannie Mae)
- `rsu-rs-stmt-present` (predicate, program=Fannie Mae)
- `fnm-nontraditional-credit-property-type` (predicate, program=Fannie Mae)
- `borrower-eligibility-not-applicable` (predicate, program=Fannie Mae)
- `secondary-seasonal-income-reqs-not-applicable` (predicate, program=Fannie Mae)
- `gla-ansi-ceiling-sqft-adj-compliant` (predicate, program=Fannie Mae)
- `ssi-grossup-pct-exceeds-15` (ratio_threshold, program=Fannie Mae)
- `poa-doc-present-when-atty-in-fact` (predicate, program=Fannie Mae)
- `fnm-income-calc-findings-present` (predicate, program=Fannie Mae)
- `foreign-assets-usd-verified` (predicate, program=Fannie Mae)
- `refinow-prior-use-flag` (predicate, program=Fannie Mae)
- `fnm-community-second-min-borrower-contribution` (ratio_threshold, program=Fannie Mae)
- `emp-income-doc-age-requirement` (predicate, program=Fannie Mae)
- `va-active-military-les-present` (predicate, program=VA)
- `va-appraisal-exhibits-present` (predicate, program=VA)
- `urla-continuation-sheet-present` (predicate, program=VA)
- `va-primary-residence-cert-present` (predicate, program=VA)
- `va-gift-letter-complete` (predicate, program=VA)
- `final-cd-present` (predicate, program=FHA) [grounded]
- `fha-mdcs-minimum-500` (ratio_threshold, program=FHA) [grounded]
- `fha-employer-housing-subsidy-verified` (predicate, program=FHA) [grounded]
- `fha-pace-obligation-satisfied-documented` (predicate, program=FHA) [grounded]
- `fha-appraisal-bias-prohibited-basis` (predicate, program=FHA) [grounded]
- `fha-appraisal-defective-condition-photos-present` (predicate, program=FHA) [grounded]
- `fha-pool-structure-condition` (predicate, program=FHA) [grounded]
- `fha-gift-xfer-closing-agent-donor-stmt-present` (predicate, program=FHA) [grounded]
- `appraisal-comp-concession-dollar-noted` (predicate, program=USDA)
- `rehab-repair-12mo-completion-doc` (predicate, program=USDA)
- `dti-auto-allowance-full-payment` (ratio_threshold, program=USDA)
- `usda-streamlined-assist-net-tangible-benefit` (predicate, program=USDA)
- `unpaid-collections-mitigating-circumstances-documented` (predicate, program=USDA)
- `appraisal-comps-similar-characteristics` (predicate, program=USDA)

## Next step

This tranche is unsigned. Before it (or the remaining 5326 rows) can run against real loans, an SME needs to review and sign off per the existing `002b`/`002c` provenance mechanism (`RuleProvenance`, `assemble_ruleset`) — not done by this script.
