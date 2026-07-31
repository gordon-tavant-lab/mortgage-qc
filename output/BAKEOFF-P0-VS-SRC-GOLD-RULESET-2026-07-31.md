# Bake-off: `p0/qc_engine` vs `src/shacl_pilot` — Gold Ruleset × Real Loan

**Date**: 2026-07-31 · **Plan**: `.claude/plans/1-no-no-this-iridescent-brooks.md` · **Rules**:
`storage/rules/gold/data/rules_compiled.json` (266 cards, 1,103 checks after removing
duplicate-slot entries) · **Loan**: `demo/touchless/extracted/loan_application.json`
(`lenderCaseIdentifier` 12607601215, the same real Touchless-classified loan `output/QC-AUDIT-
TOUCHLESS-12607601215-2026-07-30.md` audited yesterday)

Full artifacts: `p0/compile_runs/bakeoff_gold_touchless_2026-07-31/` (converter, results,
comparison script + `comparison_report.json`) and `src/shacl_pilot/bakeoff_gold_touchless_2026-07-31/`
(results) + `src/shacl_pilot/blocks/gold/` (generated shapes + linkage table).

---

## Read this before the numbers

This is **one loan, converted by two fresh converters built in a few hours specifically for
this experiment.** It is not a verdict on either engine's production readiness — see the scope
limits below, all of which materialized exactly as anticipated:

- **This loan's real data is thin, symmetrically, on both sides.** Its document inventory has
  62 entries but only 1 is field-extracted; no PDF is fetchable (`documentLocation` null
  throughout); neither adapter populates the 5 entity-record families (bank transactions, credit
  tradelines, URLA liabilities, appraisal comps, VOM rows) or a real document-presence inventory.
- **`date_window`, `list_screening`, `reverification`, and non-LTV/DTI `computation` were
  deliberately not built on either side** — building that infrastructure wouldn't change which
  engine looks stronger, since neither has it. 213 of 1,103 checks (p0) / 279 of 1,103 (src)
  fall in these categories plus the harder end of `threshold_eligibility` (see below) and are
  honestly marked unsupported, not silently dropped.
- **Only 48 of 266 gold cards are unconditional** (`applicability.always`); the other 218 gate on
  five real fields (`LoanPurposeType`, `PropertyType`, `Underwriting_Type`, `LoanType`,
  `AddressState` — program/`QC_Policy` is fixed to Fannie Mae for both, a documented experiment
  assumption since the gold set is FNM-conventional-only). `Underwriting_Type` is genuinely
  unknown on this loan (`duStatus`/`underwriting`/`lpaApproved` are all null in the payload) —
  both converters treat that as "can't tell," never a guess, but resolve it to a **different**
  verdict (see Finding 2).

---

## Headline numbers

**Coverage** (converted to a real check vs. logged unsupported, out of 1,103 gold checks):

| check_type | gold count | p0 converted | p0 unsupported | src converted | src unsupported |
|---|---|---|---|---|---|
| doc_presence | 251 | 251 | 0 | 251 | 0 |
| doc_completeness | 209 | 209 | 0 | 209 | 0 |
| cross_doc_consistency | 99 | 99 | 0 | 99 | 0 |
| scripted_review | 147 | 147 | 0 | 147 | 0 |
| **threshold_eligibility** | **172** | **172** | **0** | **3** | **169** |
| computation | 117 | 12 | 105 | 0 | 117 |
| date_window | 62 | 0 | 62 | 0 | 62 |
| reverification | 24 | 0 | 24 | 0 | 24 |
| list_screening | 22 | 0 | 22 | 0 | 22 |
| **total** | **1,103** | **890** | **213** | **709** | **394** |

**Verdict distribution** (over the full 1,103-check gold universe — a check unsupported on one
side shows `NOT_COMPILED` there regardless of how the other side treats it):

| status | p0 | src |
|---|---|---|
| PASS | 2 | 3 |
| **FAIL** | **432** | **0** |
| NOT_APPLICABLE | 133 | 14 |
| **NO_DATA** | **0** | **552** |
| NEEDS_REVIEW | 323 | 140 |
| NOT_COMPILED | 213 | 394 |

---

## Finding 1 (the headline finding): identical missing-data situations, opposite-looking verdicts

**p0 reports 432 `FAIL`s. src reports zero `FAIL`s and 552 `NO_DATA`s.** These are not
independent results pointing in different directions — they trace to the *same* underlying fact
(this loan has no real document-presence data on either side) rendered through two different,
each individually defensible, design choices:

- `p0/qc_engine/engine.py`'s `is_present` predicate treats a missing field value as a **definite
  FAIL** ("the field provably not being there" — a deliberate, documented choice, `engine.py`
  lines 331-338, referencing a real prior bug fix (015 Issue 2) where an earlier version wrongly
  exempted this case). This is the correct behavior when `field_name` is a genuine, complete
  document-inventory boolean.
- In this experiment, `doc_presence`/`doc_completeness` gold checks had **no real inventory field
  to bind to** — neither the Touchless payload nor either adapter produces one for this loan — so
  the converter used placeholder field names that are never populated by any fixture.
  `is_present` then faithfully does its job on a field that was never wired to real data, and
  every one of those 460 checks (251 + 209) resolves the same way a genuinely-confirmed-absent
  document would: **`is_present` cannot distinguish "confirmed absent" from "never checked."**
  432 of p0's 432 total `FAIL`s are exactly this category — **100% of what looks like "432
  defects found" is this artifact, not a genuine finding about this loan.**
- `run_gold_ruleset_audit.py` (src) classifies the identical situation as `NO_DATA` — a required
  `li:` predicate is absent from the loan graph, so the check honestly abstains rather than
  reporting a defect.

**Why this matters beyond this one experiment**: this project's own standing doctrine
(`docs/frontend/RULE-TO-CHECK-UI-MODEL.md`, CLAUDE.md's four/five-verdict discipline) exists
precisely to prevent a "false-clean" result — a run that looks clean when it barely ran. This
experiment surfaces the *mirror-image* risk: a run that looks like it found **432 real defects**
when it actually checked **zero** of them. Had this converter's output been treated as a
production audit result without this scrutiny, it would have manufactured several hundred false
defect claims on a single loan. This is not evidence that `p0/qc_engine` is unsound — `is_present`'s
design is correct for its intended use (a genuine closed-world Touchless document inventory,
which this specific sample loan doesn't provide on either side) — but it is concrete evidence of
how easily that correct design can be misapplied when wired to an incomplete data source, and
that `src/shacl_pilot`'s classification pipeline is structurally more resistant to this exact
failure mode **in this experiment**, because its NO_DATA path is reached by checking real
predicate presence rather than trusting a single field's None-ness.

## Finding 2: the two converters made different coverage-vs-precision trade-offs

The `threshold_eligibility` row above (172 converted on p0 vs. 3 on src) is the largest single
divergence in the coverage table, and it is a genuine difference in how conservatively each
converter was built, not a difference between the engines themselves:

- The p0-side converter matched a card to a real field (`ltv`, `dti_ratio`, `housing_ratio`,
  `credit_score_1003`, etc.) more liberally, and where it couldn't confidently parse a numeric
  threshold from the finding description, emitted the check anyway with `threshold="UNSPECIFIED"`
  — such a check structurally resolves `NEEDS_REVIEW`, not a fabricated verdict, so this is
  honest, but it inflates the "converted" count relative to how much real logic backs it.
- The src-side converter only emitted a shape when it could confidently parse both the field
  match and a clear numeric bound, logging everything else as unsupported outright.

This also explains most of the `NOT_APPLICABLE` gap (p0: 133, src: 14): `src`'s classifier checks
`NOT_COMPILED` *before* applicability (confirmed directly in `run_gold_ruleset_audit.py`), so a
check marked unsupported never gets the chance to be excluded by applicability gating either —
it's simply `NOT_COMPILED`. p0 converted ~169 more `threshold_eligibility` checks than src, many
of which are applicability-gated, giving them the chance to resolve `NOT_APPLICABLE` on the p0
side that they never got on the src side. **Neither converter's choice is wrong** — one favors
recall (convert more, let downstream verdicts sort out confidence), the other favors precision
(convert only what's confidently parseable) — but it means the coverage table above measures the
two build efforts as much as it measures the two engines.

## Finding 3: on the few checks both sides could actually evaluate, they agree

Only **2 of 1,103 checks** landed on a real, non-abstaining verdict (PASS or FAIL) on **both**
sides — expected, given how thin this loan's real data is. Both are genuine agreements, both PASS:

| card | exception code | check | p0 | src |
|---|---|---|---|---|
| `PC::O-FNM-15420` | `O-FNM-54327` | DTI 14.55% ≤ 65% threshold | PASS | PASS |
| `PC::O-FNM-16190` | `O-FNM-56234` | LTV 73.8637% ≤ 95% threshold | PASS | PASS |

Small sample, but a real positive signal: where both engines had real data and a confidently-built
check, two **independently-built adapters and converters, reading the same source payload,
computed the same DTI and LTV figures and reached the same verdict.** The disagreement in this
experiment is entirely about *abstention philosophy* (Finding 1) and *converter thoroughness*
(Finding 2) — not about the underlying math being wrong on either side.

## Finding 4: applicability-unknown handling differs, by design, on both sides

Both converters treat a genuinely unknown loan fact (`Underwriting_Type`, null throughout this
payload) as "can't tell, never guess" — but map that to a **different** verdict: p0's
`applies_if` resolves it `NEEDS_REVIEW` (`APPLICABILITY_UNKNOWN`); src's fresh classifier
resolves it `NO_DATA` ("applicability itself can't be determined... follows this project's `NO_DATA`
convention for consistency," per the script's own docstring). Both are defensible, neither is a
bug — but it's one more contributor to the two engines' differing `NEEDS_REVIEW`/`NO_DATA` split
and worth normalizing before any future apples-to-apples run.

---

## What this experiment does and doesn't tell you

**Does tell you**: on the one real loan available, both engines can be pointed at the new gold
rule set with a modest amount of new (mostly mechanical, no-LLM) glue code; where they could both
compute a real answer, they agreed; and the loudest-looking result in the whole run (432 "defects"
from p0) is an artifact of missing document-inventory data, not a real finding — a concrete,
first-hand demonstration of exactly the false-signal risk this project's verdict discipline exists
to prevent, and a data point in `src/shacl_pilot`'s favor for *this specific failure mode*, on
*this specific check_type family*, in *this specific experiment*.

**Doesn't tell you**: which engine is "better" in general. This was one loan with unusually thin
data on both sides, two hand-built converters written in a few hours with their own independent
judgment calls (Finding 2), and 460 of 1,103 checks (42%) structurally couldn't produce a
meaningful answer on either side regardless of engine choice, because the underlying document
data doesn't exist yet for this loan. A second loan, a real document inventory, or a more
conservative p0-side converter could all change these specific numbers substantially.

## Suggested next step, if this line of investigation continues

Re-run this same harness once a loan with a **real, populated document inventory** is available
(closed-world `docs_present`, at minimum) — that's the single change most likely to actually
discriminate between the two engines' real capabilities, since it removes Finding 1's confound
entirely and lets `doc_presence`/`doc_completeness` (460 of 1,103 checks, 42%, the largest single
category) produce genuine verdicts on both sides instead of an artifact.
