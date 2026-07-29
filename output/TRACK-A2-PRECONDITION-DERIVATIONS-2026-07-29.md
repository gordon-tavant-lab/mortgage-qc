# Track A2 — Precondition-Field Derivations (Proposed, Not Yet Implemented)

**Date:** 2026-07-29
**Status: PROPOSED ONLY.** Everything in this document is a design for the next phase of this run —
no code has been written, no `v5` derivation module exists yet, and no profile has been regenerated.
Treat every "would derive," "resolves to," and per-loan value below as a claim to be implemented and
then verified, not a change already in effect. Implementation is the next phase of this same run.

**Trigger:** a follow-on investigation to Track F (document-presence gating, landed in two rounds —
`run_019_track_f_document_presence_gating`, round 1 then round 2 same repo). Track F closed the gap
where `doc_present_*` facts existed in `loan.facts` but were never promoted into `loan.fields`, so
`applies_if` conditions referencing them (which only ever read `loan.get(field).doc`) could never
resolve. This investigation asked the mirror question for loan 01 (Fannie Mae + UNTAGGED scoped,
1,076 of the 3,203-check comprehensive ruleset, matching `run_018`'s scoped baseline): of the checks
still `NEEDS_REVIEW`, how many are blocked not by their own check logic or their own missing data, but
by an `applies_if` precondition on some *other* field that was never derived or populated in
`loan.fields` at all?

## The finding

718 of loan 01's checks are `NEEDS_REVIEW`. Of those, **271 sit behind an `applies_if` precondition on
a field that has no derivation anywhere in `build_loan_profiles_v3.py`/`v4.py` and no source-document
extraction anywhere in the fixtures** — the gate itself can never resolve, so the check can never reach
its own real pass/fail logic, regardless of what that logic would otherwise find.

Five precondition fields account for the large majority of those 271 blocked checks and — on
inspection of loan 01's already-extracted fields plus the other four real loan fixtures — look
plausibly derivable **with zero new document extraction**, using the same conservative,
presence-cascade discipline `build_loan_profiles_v3.py`/`v4.py` already establishes (derive a concrete
value only from a real, citable field; if the evidence doesn't match a known pattern, or no evidence
exists at all, return `underivable` — never guess, never infer from a bare document-presence fact
alone):

| Field | Checks blocked |
|---|---|
| `appraisal_waiver_type` | 90 |
| `borrower_income_type` | 45 |
| `du_validation_service_components_received` | 45 |
| `credit_report_present_for_all_applicants` | 41 |
| `closing_funds_asset_type` | 29 |

A key engine mechanic makes even a "wrong-token" derivation safe and useful: `engine.py`'s
`_eval_applies_if` treats a resolved-but-non-matching value as a **definite `NOT_APPLICABLE`**, not
`NEEDS_REVIEW`. So deriving any correct, well-grounded concrete value for one of these fields — even
one that doesn't match a specific check's token — correctly clears that check out of the "blocked by
missing precondition" limbo. Only an actual match lets the check proceed to its own real pass/fail
logic; a non-match still resolves cleanly to `NOT_APPLICABLE` instead of sitting at `NEEDS_REVIEW`
forever.

Below: one section per field, in descending impact order, followed by a summary table and a caveats
rollup.

---

## 1. `appraisal_waiver_type` — blocks 90 checks

**Issue.** 90 checks (73 gated on `== 'full_appraisal'`, 17 on `== 'value_acceptance_plus_property_data'`
— confirmed by grepping `result/rules/comprehensive_e2e_v8_ruleset.json`; no `in`-style variants exist
for this field) sit at `NEEDS_REVIEW` purely because `appraisal_waiver_type` was never derived or
populated in `loan.fields`, even though loan 01 (and 3 of the other 4 loans) already has real,
previously-extracted appraisal data that answers the question.

**Resolution.** Add `derive_appraisal_waiver_type` to a v5 `DERIVATIONS` tuple, mirroring v3's
`derive_income_type` presence-of-a-citable-field discipline — not v2's `derive_appraisal_in_file`,
which accepts a bare doc-presence fact as sufficient. That's too weak here: doc-presence alone can't
distinguish a full appraisal from a value-acceptance hybrid. The rule: check `loan.get(field).doc` in
order across `("appraiser_name", "fha_appraiser_name", "va_appraiser_name")`. A real named-and-licensed
"Appraiser" line on an Appraisal Summary/URAR is direct, citable evidence a licensed appraiser
performed a traditional inspection-based appraisal — as opposed to a value-acceptance waiver (no
appraisal at all) or a value-acceptance-plus-property-data hybrid (a non-appraiser property-data
collector visits, never a licensed "Appraiser" of record). If any of the three fields is populated,
derive `"full_appraisal"`.

No document-presence pattern for any waiver/PIW/PDC-type document exists anywhere in
`build_fixtures.py`'s `_DOCUMENT_PRESENCE_SUBSTRINGS` (confirmed by grep — zero matches for
waiver/value_acceptance/PDR/PIW across all 5 loans), so the `"value_acceptance_plus_property_data"`
token is never actually producible from current fixture data. That branch stays unexercised and
honestly disclosed — the same posture v3's `OCCUPANCY_MAP` already discloses for its own never-hit
"Second Home"/"Investment Property" tokens. If none of the three appraiser-name fields is present,
return `underivable` — never inferred from a bare `doc_present_*_appraisal` fact alone, since that
fact only proves an appraisal-related document exists, not which enum value applies.

**Why (grounding).**

| Loan | Value | Evidence |
|---|---|---|
| 01 | `full_appraisal` | `appraiser_name` = "Michael J. Torres, SRA — NC License 4188"; `06_Appraisal_Summary_1004.pdf`, field_label "Appraiser" |
| 02 | `full_appraisal` | `fha_appraiser_name` = "Angela K. Reid, SRA — FHA Roster #NC1804"; `06_FHA_Appraisal_Summary_1004_URAR.pdf` |
| 03 | `full_appraisal` | `va_appraiser_name` = "Douglas T. Byrne, Certified — VA Panel #NC-VP-2044"; `04_VA_Appraisal_Summary.pdf` |
| 04 | `full_appraisal` | `appraiser_name` = "Rita M. Colby, SRA — NC #3218"; `05_Appraisal_Summary_1004.pdf` |
| 05 | `underivable` | No `appraiser_name`/`fha_appraiser_name`/`va_appraiser_name` field exists in `loan_05.json` — only `usda_ratio_waiver_required` among appraisal-adjacent fields |

Loan 05 is one of the narrow, defect-targeted fixtures v2's own docstring already flags ("loan_05 has
28 total fields vs. loan_01's 216"). The raw source document (`04_Appraisal_Summary_USDA_502.pdf`,
read directly from `demo/syn/loan 05/` for this investigation) does show a real named appraiser
("Steven J. Nash — NC #4491") and site-value data, so loan 05 almost certainly also has a full
appraisal in reality — but that fact was never captured as a citable field in the fixture. Per the
"zero new document extraction" constraint on this phase, and this project's own conservative
precedent (v2's `derive_appraisal_in_file` docstring: "absence in a narrow, defect-targeted fixture
does not mean no appraisal exists ... honestly underivable, never defaulted"), loan 05 stays
underivable rather than being inferred from the raw PDF text or from the bare
`doc_present_usda_appraisal = true` fact alone.

**Confidence:** high.

**Caveats.** The 90-check impact figure is grounded in a direct grep of
`comprehensive_e2e_v8_ruleset.json`, not an end-to-end engine run: 73 checks use `== 'full_appraisal'`,
17 use `== 'value_acceptance_plus_property_data'`, no `in` variants. Given loan 01 derives to
`full_appraisal`, the 73 would proceed to their own real pass/fail logic (not automatic PASS — some
could still land on a different NEEDS_REVIEW for unrelated reasons) and the 17 would resolve to a
confirmed `NOT_APPLICABLE`. The engine has not been run end-to-end to confirm the 73's final
PASS/FAIL/NEEDS_REVIEW split — only that all 90 clear the "blocked by this specific missing
precondition" state, which is what was asked. Separately, the `value_acceptance_plus_property_data`
branch is permanently untested against real fixture data (no waiver/PDC document pattern exists in any
of the 5 fixtures today) — the same disclosed-but-accepted gap as v3's `OCCUPANCY_MAP` second-home/
investment tokens.

---

## 2. `borrower_income_type` — blocks 45 checks

**Issue.** 45 checks gate on `borrower_income_type` via `applies_if`, but no derivation for this field
exists anywhere in `build_loan_profiles_v3.py`/`v4.py` — it is absent from `loan.fields` for all 5
loans, so every one of those 45 checks resolves to `NEEDS_REVIEW` purely on a missing precondition,
never reaching its own real pass/fail logic.

**Resolution.** Add `derive_borrower_income_type`, reusing v3's exact presence-cascade shape and its
two existing signals unchanged (`years_self_employed_1003` present → `self_employment`; else
`voe_employer_name` present → `wage_earner`), then adding one new presence check specific to the
richer vocabulary: if `va_branch_of_service` is present (a field that exists only via the VA
Certificate of Eligibility, whose own field label is literally "Branch of Service") → `military`. If
none of the three fields is present, return `underivable` — refusing to guess among the remaining 7
tokens (`rental`, `trust`, `alimony_child_support_maintenance`, `overtime_bonus_commission`,
`social_security_retirement_disability`, `part_time_second_job_seasonal_unemployment`, `other`) since
none of the 5 real fixtures carries any citable signal for them.

**Why (grounding).**

| Loan | Value | Evidence |
|---|---|---|
| 01 | `wage_earner` | `voe_employer_name` populated: `02_Verification_of_Employment.pdf`, "Fannie Mae Form 1005 / Freddie Mac Form 90", field_label "Employer Name" = "ABC Manufacturing, Inc." — identical signal v3's `income_type_used_for_qualification` already uses |
| 02 | `underivable` | Only `base_monthly_income_1003`/`employer_name_1003`/`current_address_1003`/`employment_start_date_1003` present; no `years_self_employed_1003`, `voe_employer_name`, or `va_branch_of_service` anywhere in `loan_02.json` |
| 03 | `military` | `va_branch_of_service` populated: `02_VA_Certificate_of_Eligibility.pdf`, field_label "Branch of Service" = "U.S. Army" — corroborated (not contradicted) by `employer_name_1003` = "U.S. Army — 82nd Airborne" and `position_title_1003` = "Staff Sergeant / E-6" in the same fixture, though the derivation keys off the purpose-built VA COE field, not a substring parse of employer text |
| 04 | `self_employment` | `years_self_employed_1003` = "6 years 11 months", 1003 field_label "Years Self-Employed" — identical to v3 |
| 05 | `underivable` | No `years_self_employed_1003`, `voe_employer_name`, or `va_branch_of_service`; only `employer_name_1003` = "Prestige Auto Repair" and an aggregate `household_income_usda` figure exist, neither a citable income-type marker (`doc_present_self_employed_income` and `doc_present_business_tax_returns` are both `false` for this loan) |

**Confidence:** medium.

**Caveats.** A ruleset-wide grep of `comprehensive_e2e_v8_ruleset.json` shows the 45
`borrower_income_type` conditions split as: `wage_earner`=9, `other`=10, `self_employment`=6,
`rental`=6, `overtime_bonus_commission`=3, `part_time_second_job_seasonal_unemployment`=3,
`social_security_retirement_disability`=3, `alimony_child_support_maintenance`=2, `military`=2,
`trust`=1. For loan 01 (deriving `wage_earner`), that suggests roughly 9 of the 45 checks would have
this gate resolve to a match and the remaining ~36 would resolve to a confirmed non-match
(`NOT_APPLICABLE`) — but the engine has not been run end-to-end, so it is not confirmed that (a) all
45 ruleset-wide conditions are in loan 01's Fannie Mae + UNTAGGED scope, or (b) the 9
`wage_earner`-matching checks don't carry a second, still-unmet `applies_if` condition on a different
field that would keep them at `NEEDS_REVIEW` regardless. Also: the `military` path (loan 03) is proven
against exactly one real fixture; the other 6 vocabulary tokens (`rental`, `trust`, `alimony`,
`overtime/bonus/commission`, `social security`, `part-time/seasonal`, `other`) are untested against any
of the 5 real fixtures today — the same disclosed-limit posture already used for `OCCUPANCY_MAP`'s
`second_home`/`investment` paths.

---

## 3. `du_validation_service_components_received` — blocks 45 checks (no derivation proposed)

**Issue.** On loan 01, 45 `NEEDS_REVIEW` checks are blocked by an `applies_if` precondition on
`du_validation_service_components_received`, a field never populated in `loan.fields` for any of the 5
loans because no source document or extracted field speaks to it at all.

**Resolution.** **No derivation is proposed for this field.** Every one of the 373 unique field keys
across all 5 fixtures' `fields` was searched for anything DU/AUS/relief/validation-related, and it
turned up nothing — only appraisal-comparable fields (`appraisal_comp_*`), a USDA-specific
`usda_ratio_waiver_required` (a different concept), and a USDA `usda_gus_findings_date` (loan 05's GUS
findings date — a different program's AUS, not DU). The only related datum anywhere is the fact
`doc_present_du_uw_findings_report`, which reads `false` for all 5 loans. Per this project's own
established precedent in `build_loan_profiles_v2.py`'s `derive_appraisal_in_file` ("NEVER derived
false from absence ... absence in a narrow, defect-targeted fixture does not mean no appraisal exists
in the real file"), a `false` presence fact cannot be used to manufacture a substantive negative value
— it signals only that this fixture wasn't built to extract that document, not that the real closing
file lacks a DU findings report. This field should stay `underivable` for all 5 loans, matching the
honest disposition `build_loan_profiles_v2.py`'s own docstring already reached when it evaluated this
exact fact by name.

**Why (grounding).** `build_loan_profiles_v2.py`'s docstring (lines ~26–31) states directly: "The
other 13 facts in the vocabulary (income type, credit report presence, DU components, LEP, etc.) were
evaluated and found to have NO direct signal in these fixtures ... Not attempted here; tracked as a
real extraction-coverage gap." "DU components" names `du_validation_service_components_received`
directly. An independent re-check confirms this still holds — grepping all `fields` keys in
`loan_01.json` through `loan_05.json` for `du`/`aus`/`underwrit`/`validation`/`findings`/`relief`/
`waiver`/`value_accept` turned up nothing usable (only loan_05's `usda_gus_findings_date`, a different
program's AUS, not DU). Cross-checking `storage/fact_vocabulary/v8.json`'s own entry for this fact
(`fact-du-validation-service-components-received`) shows its `question_bindings` define only 5
positive relief tokens (`appraised_value_relief`, `asset_relief`, `employment_relief`, `income_relief`,
`rent_payment_history_credit_risk_assessment`), sourced from AMQ question 570809 — there is no "none
received" token in the vocabulary to map an absent report to, so even a sentinel "none" value would be
inventing a token the source vocabulary never defined, contra `CLAUDE.md`'s "grounding adds context,
never new rule content." And separately from vocabulary coverage,
`doc_present_du_uw_findings_report = false` for all 5 loans is exactly the kind of absence-only signal
`derive_appraisal_in_file`'s own comment says must not be turned into a derived negative claim, since 4
of 5 fixtures are deliberately narrow extractions built only around their own planted defects.

| Loan | Value | Evidence |
|---|---|---|
| 01 | `underivable` | No DU/AUS/relief-related field among 217 fields; only `doc_present_du_uw_findings_report = false` |
| 02 | `underivable` | No DU/AUS/relief-related field among 56 fields (FHA loan); only `doc_present_du_uw_findings_report = false` |
| 03 | `underivable` | No DU/AUS/relief-related field among 43 fields; only `doc_present_du_uw_findings_report = false` |
| 04 | `underivable` | No DU/AUS/relief-related field among 111 fields (Freddie Mac Conventional per `loan_program_1003`); only `doc_present_du_uw_findings_report = false` |
| 05 | `underivable` | Carries `usda_gus_findings_date` (USDA's GUS automated-underwriting findings, a *different* AUS system, not DU Validation Service evidence) — confirms this is a USDA/GUS loan, not a DU-eligible Fannie Mae loan, but supplies no `du_validation_service_components_received` value; `doc_present_du_uw_findings_report = false` here too |

**Confidence:** high (in the negative finding — no derivation exists to have a confidence level about).

**Caveats.** This is a negative finding: no honest derivation rule could be identified, so none is
proposed, and the 45 checks on loan 01 gated by this field remain blocked (still resolving to
`NEEDS_REVIEW` via the missing-precondition path), exactly as before — no impact/clearance to estimate
since no value is being introduced. Two distinct reasons compound to make this underivable, worth
keeping separate: (1) `doc_present_du_uw_findings_report = false` only tells us no such report was
captured in these narrow, defect-targeted fixtures, not that no such report exists in the real closing
file — the exact ambiguity `derive_appraisal_in_file`'s precedent was written for; and (2) even setting
that aside, "no DU findings report" would at most support "this loan wasn't processed through Fannie
Mae's DU Validation Service at all" (plausible for loan 05, which is USDA/GUS, and for FHA/VA loans
generally) — a conceptually different claim from "zero relief components were received," and the fact
vocabulary itself defines no token for either "not applicable" or "none received," so there is no
vocabulary-sanctioned value to assign even if the absence were confirmed real. The engine was not run
to independently confirm the current `NEEDS_REVIEW` disposition of these 45 checks; the investigation's
own framing (currently blocked by this precondition being unpopulated) was taken as given.

---

## 4. `credit_report_present_for_all_applicants` — blocks 41 checks

**Issue.** This `applies_if` precondition is never populated in any loan's `loan.fields` today, so all
41 checks gated on it (e.g. `adverse-credit-satisfactory-risk-evidenced`, `credit-report-staleness-120d`,
`borrower-frozen-credit-multi-bureau`, `credit-report-hard-pull-inquiry-confirmed`) stay stuck at
`NEEDS_REVIEW` purely because the gate itself can't resolve — independent of whether the check's own
real logic could otherwise run.

**Resolution.** Add a new v5-style derivation, following the `appraisal_in_file`/`derive_loan_program`
shape: (1) determine applicant count from presence of `co_borrower_name_1003` in `loan.fields`
(present ⇒ 2 applicants; absent ⇒ 1 — the only two shapes the field catalog models, since there is no
`co_borrower_2` field anywhere in the catalog); (2) for a single-applicant loan, derive `"true"` only
if `borrower_credit_score` is present (a citable credit-report-sourced score for the sole applicant),
else `underivable`; (3) for a two-applicant loan, derive `"true"` only if BOTH `borrower_credit_score`
AND `coborrower_credit_score` are present (both citably sourced from the same tri-merge credit-report
document, one line per role), else `underivable`. Mirroring `derive_appraisal_in_file`'s explicit
discipline ("NEVER derived false from absence, since 4 of 5 fixtures only extract fields their own
planted defects need"), absence of a credit-score field is never treated as a negative "false" signal
— only ever `underivable`, because these loans' sparse field counts (56/43/111/29 vs. loan 01's 217)
are the identical narrow-fixture pattern that discipline was written for.

**Why (grounding).**

| Loan | Value | Evidence |
|---|---|---|
| 01 | `true` | `co_borrower_name_1003` = "Jane M. Smith" (`01_Final_1003_URLA.pdf`, "Co-Borrower Name", Sec. 1) establishes 2 applicants; `borrower_credit_score` = 742 ("Middle Score — Borrower") and `coborrower_credit_score` = 758 ("Middle Score — Co-Borrower"), both from `04_Credit_Report_Summary.pdf` (Tri-Merge Credit Report Summary) — one document explicitly scoring both named roles |
| 02 | `underivable` | No `co_borrower_name_1003` (single applicant: Maria E. Sanchez); no `credit_*`-prefixed field of any kind. Confirmed against `demo/syn/loan 02/`: 1003, HUD-92900A, FHA Connection, Gift Letter, CAIVRS/LDP/GSA, FHA appraisal, Closing Disclosure — no credit report document exists in the file at all |
| 03 | `underivable` | No `co_borrower_name_1003` (single applicant: Marcus D. Johnson; `marital_status_1003` = "Married" but no co-applicant on the loan); no `credit_*` field. `demo/syn/loan 03/`: 1003, VA COE, VA NOV, VA appraisal, CD — no credit report document |
| 04 | `underivable` | No `co_borrower_name_1003` (single applicant: Anika R. Patel; married, no co-applicant); no `credit_*` field. `demo/syn/loan 04/`: 1003, payoff statement, VOM, self-employed income doc index, appraisal, CD — no credit report document |
| 05 | `underivable` | No `co_borrower_name_1003` (single applicant: Derrick T. Williams). Only credit-adjacent field is `usda_gus_credit_recommendation` = "Accept" (`02_USDA_GUS_Findings.pdf`, "Credit Recommendation") — a GUS AUS output, not a citation to a credit-report document or a borrower-attributed score; not treated as equivalent evidence. `demo/syn/loan 05/` has no dedicated credit report document |

**Confidence:** medium.

**Caveats.** Two real judgment calls, not settled facts. (1) Whether loans 02–05 should derive
`"false"` instead of `"underivable"` is genuinely debatable — independent verification against the
real `demo/syn` source directories confirms no credit report document exists in those 4 loans' files
at all (stronger evidence than a mere missing-field gap), and the field's own `applies_if` (`in
'false|true'`) lets either `true` or `false` unblock the check to real logic, so `"false"` would also
be a defensible resolution. `"underivable"` was chosen here to stay strictly consistent with this
project's explicit precedent (`derive_appraisal_in_file`'s docstring), which these 4 loans match on
sparse-field-count signature (56/43/111/29 fields vs. loan 01's 217) — but a reviewer could reasonably
override this to `"false"` for 02–05 given the extra source-directory verification, which goes beyond
what the derivation function itself can see from `loan.fields` alone. (2) Impact estimate: the engine
was not run. Deriving `"true"` for loan 01 will clear this field's `applies_if` for all 41 gated checks
on loan 01 (both `true`/`false` satisfy `in 'false|true'`, unlike the other 4 precondition fields where
a non-match yields `NOT_APPLICABLE`) — but that only means those 41 checks proceed to their own real
pass/fail/NEEDS_REVIEW logic, not that they all become clean PASS. Loan 01's fixture does carry real
`credit_tradeline_*`/`credit_inquiry_*`/`credit_report_date` fields many of these checks would need, so
a meaningful fraction plausibly resolve definitively, but no confirmed number without running the
compiled ruleset. Loans 02–05 stay `underivable` under this design, so their own checks gated on this
field are unaffected by this change.

---

## 5. `closing_funds_asset_type` — blocks 29 checks

**Issue.** 29 of loan 01's `NEEDS_REVIEW` checks are gated by an `applies_if` on
`closing_funds_asset_type`, which is never populated in `loan.fields` for any of the 5 real fixtures —
so those checks can never resolve past their precondition today, regardless of what their own check
logic would otherwise find.

**Resolution.** Proposed `derive_closing_funds_asset_type(loan)`, same shape as
`derive_occupancy_type`: (1) collect every `asset_NN_account_type` field present in `loan.fields`; (2)
map each literal text to a canonical token via an explicit `ASSET_TYPE_MAP` sourced verbatim from
`storage/fact_vocabulary/v8.json`'s `closing_funds_asset_type` `question_bindings` (spec 015 Phase B)
— e.g. "Checking"/"Savings" → `checking_savings`, "401(k)"/"IRA" → `retirement` — never fuzzy-matched;
any unrecognized text is `underivable`; (3) if exactly one distinct canonical token results across all
present `asset_NN` entries, derive it; (4) if more than one distinct token results (as with loan 01,
which has both `checking_savings` and `retirement` entries) or zero `asset_NN` fields exist at all,
return `underivable` — mirroring `derive_loan_program`'s precedent for "multiple candidate signals, no
field says which one" (the Conventional/Fannie-vs-Freddie ambiguity case). Gift funds are deliberately
NOT mapped to any token: "gift" is absent from the fact vocabulary's 16-token answer set for this
field, and forcing it to the `other` token would be an interpretive relabeling not grounded in any
document's literal text, so it stays `underivable` rather than guessed.

**Why (grounding).**

| Loan | Value | Evidence |
|---|---|---|
| 01 | `underivable` | 1003 Section 2 (Financial Information — Assets) discloses `asset_01` Checking + `asset_02` Savings (→ `checking_savings`) AND `asset_03` 401(k) (→ `retirement`) — two distinct canonical asset-source types present, no field says which is *the* closing-funds source (same ambiguity class as `derive_loan_program`'s Conventional/Fannie-vs-Freddie case) |
| 02 | `underivable` | `04_Gift_Letter.pdf`: entire down payment ($9,975 = `down_payment_amount_1003` exactly) is a gift from donor Roberto Sanchez (uncle) — "gift" is not among the 16 tokens in `fact_vocabulary` v8.json's `closing_funds_asset_type` bindings (question 570606); no `asset_NN` field present either |
| 03 | `underivable` | VA purchase, 43 fields total: zero `asset_NN` fields, zero down-payment/source-of-funds field of any kind |
| 04 | `underivable` | Freddie Mac cash-out refinance, 111 fields: zero `asset_NN` fields and zero source-of-funds field — cash flows *to* the borrower ($78,600 `cash_to_borrower_cd`), not from the borrower |
| 05 | `underivable` | USDA purchase, 29 fields: zero `asset_NN` fields and zero source-of-funds field — only USDA program/eligibility/DTI data present |

Verified loan-by-loan by listing every field in all 5 `from_docs` fixtures rather than assuming loan
01 generalizes.

**Confidence:** medium.

**Caveats.** Under this conservative design, all 5 real fixtures — including loan 01, the one under
investigation — come out `underivable`, so the best estimate is 0 of the 29 blocked checks on loan 01
resolve to `NOT_APPLICABLE`; all 29 stay `NEEDS_REVIEW`, unchanged, if this derivation is added as
designed. This differs from the other 4 fields in this batch and matches this field's flagged "lower
initial confidence." A less conservative alternative exists but was deliberately rejected: loan 01's
bank statement (`05_Bank_Statement_Wells_Fargo.pdf`) `ending_balance` ($18,240.00) exactly matches
`asset_01_balance` (the Checking account), which could be read as "only the checking account has an
actual verification document in file, so that's the real closing-funds source" → `checking_savings`.
This was not adopted because it requires cross-field value-matching between two different documents —
a kind of inference with no precedent in `build_loan_profiles_v3.py`/`v4.py` (which only ever read a
single field's literal text or check simple field presence) — flagged here as a design option for
explicit accept/reject in the next phase, not silently built in. The engine was not run against a
hypothetical profile to independently re-verify the 29-check count or confirm every one of those 29
checks' `applies_if` actually resolves to `NOT_APPLICABLE` the way the engine-behavior description
above implies; that description was taken as given, not independently re-derived from `engine.py`.

---

## Summary table

| Field | Checks blocked | Confidence | Proposed value type | Derivation proposed? |
|---|---|---|---|---|
| `appraisal_waiver_type` | 90 | high | enum (`full_appraisal` \| `value_acceptance_plus_property_data`) | Yes |
| `borrower_income_type` | 45 | medium | enum (10 tokens) | Yes |
| `du_validation_service_components_received` | 45 | high (negative finding) | enum (5 relief tokens) | **No — stays underivable, no vocabulary token for absence** |
| `credit_report_present_for_all_applicants` | 41 | medium | boolean | Yes |
| `closing_funds_asset_type` | 29 | medium | enum (16 tokens) | Yes (loan 01 itself still resolves `underivable` under the conservative design) |
| **Total** | **250 of 271** | | | (21 of the 271 are the remainder not covered by these 5 fields, out of scope for this document) |

Of the 250 checks covered by the 4 fields with a proposed derivation, loan 01 is expected to clear
221 out of the "blocked by missing precondition" state under the conservative designs above (90 +
9-ish of 45 + 41; `closing_funds_asset_type`'s 29 stay blocked). The `borrower_income_type` figure is
an estimate (~9 of 45 match `wage_earner` exactly, the rest resolve to a confirmed non-match) pending
an actual engine run — see that section's caveats. `du_validation_service_components_received`'s 45
checks remain blocked; no derivation is proposed for that field.

## What implementation will require (next phase)

1. A new `build_loan_profiles_v5.py` (or an addition to v4, per whatever versioning discipline the
   next phase decides — the existing convention pins each version's generator behavior via committed
   tests and artifacts, so a new file is likely, matching v1→v2→v3→v4's own pattern).
2. Four new derivation functions (`derive_appraisal_waiver_type`, `derive_borrower_income_type`,
   `derive_credit_report_present_for_all_applicants`, `derive_closing_funds_asset_type`), each
   returning either `derived_facts` or `underivable` per the existing contract — never both, never
   neither.
3. Regenerated `storage/loan_profiles/v5/loan_0{1-5}.json`.
4. A re-run of the relevant `run_018`/`run_019`-style comparison to confirm the actual before/after
   check-status deltas on loan 01 — every impact figure above is a grep-based estimate, not an
   engine-confirmed number, and should be replaced with real numbers once the engine actually runs
   against the new profile.
5. A decision, made explicitly rather than defaulted, on the `closing_funds_asset_type`
   cross-document-matching alternative flagged in §5, and on the `credit_report_present_for_all_applicants`
   underivable-vs-false judgment call flagged in §4.

---

**Status: PROPOSED ONLY — not yet implemented.** This document describes candidate derivations to
close 4 of the 5 highest-impact precondition gaps found in the 271-checks-blocked investigation.
Nothing here has been coded, run, or verified end-to-end against the real engine; the "why" sections
ground each proposal in real per-loan field/document evidence, but the actual before/after check-count
deltas remain estimates until implementation and a real engine run happen in the next phase of this run.
