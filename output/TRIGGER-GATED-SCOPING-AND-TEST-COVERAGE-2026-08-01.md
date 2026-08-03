# TRIGGER_GATED scoping + test-coverage gap: decision record

**Date:** 2026-08-01
**Status:** paused for decision, per Gordon's explicit "write this up first" — nothing in this doc
has been acted on.

## Part 1: the test-coverage gap

Gordon asked how today's changes (context_flags generalization, the autopass fix, the
categorization work — `output/BAKEOFF-P0-VS-SRC-GOLD-RULESET-2026-07-31.md` Addenda 7-9) were
actually tested, after I imprecisely described it as "tested against 25 loans" in a summary.

**Correction, verified by inspecting the actual test code:**
- The 25-known-defect gate (`p0/fixtures/from_docs/verify_against_defects.py`) runs against **5**
  synthetic fixture loans (`loan_01`-`loan_05`), not 25 -- "25" is the defect count, not the loan
  count. This gate tests `p0`'s core fixture-loading/field-resolution machinery. It does **not**
  exercise `import_gold_ruleset.py`, the `context_flags` mechanism, the autopass list, or any of
  today's actual changes -- confirmed by grep: zero references to any of today's changed functions
  anywhere in `p0/tests/`.
- The 445-test `pytest` suite passing means today's changes didn't break unrelated engine code. It
  is not evidence that today's *new* logic is correct.
- **The only real validation of everything built today is manual, single-loan, before/after
  comparison against loan 12607601215** (the Touchless demo loan) -- run, checked, and re-verified
  after every change this session, but never cross-checked against a second real loan with
  different characteristics (an actual refinance, an ARM, a loan with different documents).

**Decision, as given:** proceed with single-loan validation for now; the risk is accepted and
documented here, not silently carried. **New context that changes this going forward:** Gordon
reports an API is being built to fetch additional loans and documents. Once that exists, re-running
today's context_flags/autopass/categorization logic against a second, differently-shaped real loan
becomes the natural next validation step -- flagging here so it isn't forgotten once that API
lands.

## Part 2: TRIGGER_GATED (277 rows) scoping

Gordon asked to scope the biggest remaining bucket before deciding how to tackle it.

**The core finding: TRIGGER_GATED isn't one problem, it's two, and about half of it is a direct
extension of work already proven today, not new machinery.**

| Sub-bucket | Count | Nature |
|---|---:|---|
| Cards that already carry a `context_flags` entry in the gold data | **152** | Same mechanism as today's fix (`CONTEXT_FLAG_FACT_KEYS`/`CONTEXT_FLAG_APPLIES_IF_FIELD`) -- just needs more flags wired to a real fact |
| Cards with no `context_flags` at all | **125** | A different kind of gap -- someone needs to go back to the card and author a trigger condition, using the free-text `trigger` field in `doc_decidability_classification.json` as a starting point. Not an engine problem. |

### The 152, broken down by flag and actionability

| Flag(s) | Count | Assessment |
|---|---:|---|
| `income_type_employment_wage_based` | 16 | Likely derivable now from existing employer/income fields |
| 10 other `income_type_*` flags (rental, military, trust, restricted_stock, ss_retirement_disability, secondary_seasonal, alimony_nontaxable, housing_assistance, anticipated_eligible, auto_allowance, requires_employment_verification) | ~35 | **Promising lead, not verified.** The payload has a structured `borrowersDetail.borrowerPairs[].borrowers[].incomeAnalysis` object with explicit typed fields (`rental`, `militaryIncome`, `selfEmployed`, `wages`, etc.) -- for this loan, `rental`/`militaryIncome`/`otherIncomeDetail` are all `null`, suggesting these income types weren't used to qualify. **Not yet confirmed this field is genuinely exhaustive** (closed-world) the way `documents[]` was independently confirmed to be -- that confirmation is a prerequisite before trusting a `null` as real evidence of absence, not an assumption to make casually. |
| `income_type_any_qualifying_source` | 14 | Not yet read closely enough to know what it actually tests |
| `DU_INCOME_RELIEF_RECEIVED`, `DU_EMPLOYMENT_RELIEF_RECEIVED`, `DU_ASSET_RELIEF_RECEIVED`, `DU_APPRAISED_VALUE_RELIEF_RECEIVED`, `DU_RENT_PAYMENT_HISTORY_CREDIT_RISK` | 40 | **Not a code problem -- a policy question.** These preconditions are exactly as unverifiable as the DU/EPIC checks already on the autopass list (`storage/rules/gold/data/autopass_no_system_access.json`). Extending "we can't verify DU, so simulate pass" from *checks* to *preconditions gating other checks* is a real, further extension of the already-acknowledged false-clean tradeoff -- Gordon's call, not a technical one. |
| `value_acceptance_property_data_exercised` | 6 | May already be covered by the separate A2 per-loan scenario-gate sidecar (`scenario_applicability_loan12607601215.json`) -- needs checking against that table before assuming it's unhandled. |
| `lep_individual_present`, `closed_as_electronic_transaction` | 4 | Likely genuinely unavailable in this payload; not investigated further. |

### The 125 with no context_flags at all

Not scoped in detail yet. These need a card-by-card authoring pass (attach a real
`context_flags` entry to the gold card, grounded in its own `trigger` description) before any
engine-side wiring is even possible -- a prerequisite step, not something `import_gold_ruleset.py`/
`ruleset_to_shacl.py` can do on their own.

## Three open threads, not yet chosen between

1. **Verify `incomeAnalysis` is closed-world, then wire ~35 income-type flags** -- highest
   single-lead payoff, needs an evidence check first (confirm the field is exhaustive, e.g. via
   Touchless's own documentation or by inspecting a second loan once more are available).
2. **Decide the DU-relief-precondition policy question** -- 40 checks, answerable immediately
   without more investigation, purely a scope decision.
3. **Scope the 125 no-context-flags checks** -- a card-authoring gap, different shape of work
   entirely from 1 and 2.

None of these has been started. This document exists so the finding survives to the next
conversation, per Gordon's explicit "write this up first" instruction.
