# SME Review Queue

Items requiring Kayla's mortgage-domain sign-off before production use (per
CLAUDE.md Known Blocker #2). Everything here is safe for demo/bake-off use
today under the individual-hand-verification bar already applied — this
queue is what still needs an actual SME's judgment before it can be trusted
unsupervised in production.

## check_type reclassifications (A0)

| card_id | exception_code | original check_type | proposed check_type | rationale |
|---|---|---|---|---|
| `PC::CIP DATA POINTS` | `CIP data points` | `doc_presence` | `cross_doc_consistency` | The question is presence-framed ("Are the 4 CIP data points provided in file?") but the actual defect ("have not been provided **or are inconsistent**") is checking whether name/address/DOB/SSN agree consistently across every document in the file that carries them — not whether any single document exists. See `output/NODATA-ROOT-CAUSE-ANALYSIS-2026-07-31.md` and `storage/rules/gold/data/compiled/application.json`'s updated `notes` field for full detail. |

## PURE_PRESENCE document-check wiring (from `A` sidecar, when built)

*(Empty for now — today's 3 wired checks (ICPL, Borrowers Authorization,
Hazard Insurance policy) were reviewed and confirmed correct by Gordon
directly during the 2026-07-31 session; logged here for visibility, not as
open items needing further action.)*

| card_id | exception_code | wired field | status |
|---|---|---|---|
| `PC::ICPL` | `ICPL` | `doc_present_closing_protection_letter` | wired, hand-verified 2026-07-31 |
| `PC::O-BP-14663` | `O-BP-54652` | `doc_present_borrowers_authorization` | wired, hand-verified 2026-07-31 |
| `PC::O-FNM-15436` | `HOICoverage` | `doc_present_hazard_insurance` | wired, hand-verified 2026-07-31 |

## Scope decisions NOT requiring SME review

For completeness — these are Gordon's deployment-scope calls, not mortgage-
domain judgments, so they do not need Kayla's sign-off, only documentation
of the reason (see `demo_exclusions.json` and `autopass_no_system_access.json`):
- 21 checks excluded from this demo build (`demo_exclusions.json`) — either
  require a system this project has no connection to (eMortgage tamper-
  evident security), or are Gordon's direct "not needed for this demo" calls.
- 66 checks auto-passed for this demo build because they require DU, EPIC,
  or Loan Delivery system access this project has no connection to
  (`autopass_no_system_access.json`) — output is indistinguishable from a
  real PASS, a deliberate, documented departure from this project's
  "never show a false clean" discipline, scoped to this demo only.

## 2026-08-01 additions (resolve6 pass — six NOT_COMPILED buckets)

### New wired checks needing Kayla's confirmation before production use

| card_id | exception_code | wired field / mechanism | status |
|---|---|---|---|
| `PC::O-BP-14664` | `O-BP-54659` | `doc_present_occupancy_affidavit` — Occupancy Statement matched to the payload's "Occupancy Affidavit" documentType. Overturns an earlier rejection: the affidavit IS the sworn form of an occupancy statement (exact-or-narrower), and no sibling-form family exists in the Touchless vocabulary to false-FAIL against. | wired, hand-verified 2026-08-01 |
| `PC::CIP DATA POINTS` | `CIP data points` | `cip_identity_consistent_across_docs` — 1003 name+SSN vs Schedule C Proprietor_Name+SSN (case/digits-normalized). DOB + address legs NOT covered (no second machine-readable doc side; vendor ask). One-directional: mismatch → NEEDS_REVIEW, never FAIL. | wired, hand-verified 2026-08-01 |
| `PC::O-EPD-14458` | `O-EPD-52924` | `bank_account_holder_matches_borrower` — Bank Statement documentAnnotations holder name vs borrower; second-holder keys explicitly blank. One-directional. | wired, hand-verified 2026-08-01 |
| `PC::O-FNM-15334` | `O-FNM-00214` | `doc_present_vod_or_asset_statement` — loan-level disjunctive presence (VOD OR statements) over the closed-world inventory. Per-account granularity unverifiable (no depository roster in payload; vendor ask). | wired, hand-verified 2026-08-01 |
| `PC::O-BP-14664` | `O-BP-54660` | `doc_present_signature_name_affidavit_or_aka` — disjunctive presence (Signature Name Affidavit present satisfies the OR). | wired, hand-verified 2026-08-01 |
| `PC::O-FNM-15389` | `O-FNM-50196` | `cltv_recomputation_matches` — CLTV recompute (260,000 / 352,000 = 73.86 == reported). Premises: all value bases equal; subordinate financing corroborated zero (subordinateLienAmount, heloc, helocCreditLimitAmount all null). | wired, hand-verified 2026-08-01 |
| `PC::O-FNM-15389` | `O-FNM-50197` | `hcltv_recomputation_matches` — same premises, HELOC limits corroborated zero. | wired, hand-verified 2026-08-01 |
| `PC::O-FNM-15397` | `O-FNM-58597` | `borrower_ssn_present_valid_shape` — SHAPE only (9 digits); SSA validity deliberately NOT tested (demo loan uses a never-issued 999-area SSN). | wired, hand-verified 2026-08-01 |

### Reclassifications (source `check_type` corrections, same class as the CIP precedent)

All six were labeled document-presence/completeness questions in the source
classification but are really system-state or data-validation checks; patched
to `scripted_review` in `storage/rules/gold/data/compiled/` and revalidated:
`PC::O-FNM-15409/O-FNM-00824` (underwriter-conditions process; also repaired a
bookkeeping bug — the row was in neither the exclusion nor the autopass file
despite the reconciliation note), `PC::O-FNM-16190/O-FNM-57456` (ULDD
special-feature-code), `PC::UGV Exception/PrivateBank` + `UGV Identifier`
(EPIC/Notepad approval screens; joined their two siblings in the autopass
list), `PC::O-FNM-15381/O-FNM-59132` (CPM/DU message), `PC::O-FNM-15397/
O-FNM-58597` (per-borrower SSN validation, wired above).

### Deferred to SME / vendor — deliberately NOT wired

- `PC::O-FNM-15451/O-FNM-54125` (tax-return most-recent-year): the raw year
  gap (2023 return vs 2026 application) clears every B1-1-03 boundary
  interpretation, so a FAIL would be safe for THIS loan — but the general
  year-boundary date table must be SME-signed, not invented. Held.
- `PC::O-FNM-15304` final-URLA PASS candidate: the URLA documentType does not
  encode initial-vs-final; accepting the post-closing package's URLA set as
  "final" needs Kayla's call. Held.
- ROV process-disclosure absence findings (`O-FNM-59136`, `O-FNM-57786`): no
  ROV documentType exists in the closed-world inventory, but the payload is
  mid-pipeline — confirm with Touchless that their classifier can emit an ROV
  type before treating absence as a finding. Held.

### Scenario-table additions (provisional, per-loan)

93 rows added/flipped in `scenario_applicability_loan12607601215.json`
(tag `added: 2026-08-01-resolve6`), every one re-derived independently from
the raw payload with `verified_against` JSON paths; 3 candidates rejected
(2 rested on the ASSUMED demo DU fact, 1 on absence inference). Rows with
`flagged_for_spotcheck: true` should be reviewed first.

## 2026-08-01 additions (resolve7 pass — round 2)

### New wired check

| card_id | exception_code | wired field / mechanism | status |
|---|---|---|---|
| `PC::ATR-QM` | `O-FRD-54594` | `loan_term_months <= 360` — "loan term exceeded 30 years", number+direction verbatim (years→months unit conversion is why the auto-parser missed it). | wired, hand-verified 2026-08-01 |

### Scenario-table round 2 (provisional, per-loan)

151 rows appended + 9 UNKNOWN→NA flips (tag `added: 2026-08-01-resolve7`), all
adversarially verified; 8 candidates rejected. **One existing NA retracted**:
`PC::O-FNM-15358/O-FNM-00544` — its "no disaster impact" fact is contradicted by
FEMA DR-4909-HI in the payload's own disasterSummary; flipped to UNKNOWN.

Spot-check first (flagged rows): gift-of-equity pair (assetDetail is not
closed-world), EPD Freddie-sale, UGV portfolio-gate, ECOA consummation inference,
eMortgage conjunct. Also flagged on existing rows: the trust-account NA
(doc-granularity weakness — a UTMA statement would classify under generic "Bank
Statement") and both ADU NAs (rest on the demo-scoped ASSUMED fact).

### For Kayla — the ambiguous-text queue (the cheapest remaining unlock)

39 threshold rows + 4 date-window rows reference a limit/window without stating it
("did not meet requirements", "exceeds the maximum allowed", "timely",
"immediately"). The compiler refuses to guess these by design; each needs the real
number/window from the Selling Guide confirmed by an SME. Resolving these unlocks
~43 checks with no new engineering.

### Negative-control follow-up (silent-false-negative discipline)

The 9 UNKNOWN→NA flips rest on newly-used payload facts (amortizationType,
citizenshipResidencyType, propertyEstateType, SFHA indicator, gift fields). Each
should get a mutation fixture (flip the deciding fact, assert the check un-gates)
before these gates are trusted beyond the demo loan.
