# Scenario Applicability Gate — Experiment, Decision, and the Disjunction Bug

**Date:** 2026-07-30 · **Code:** `src/gates/scenario_gate.py`
**Prompted by:** Gordon's recall that a "missing document" may simply mean the loan's
program or scenario never required it.

---

## 1 · The question

The audit reports 2,442 conventional-applicable rules as `NOT_COMPILED`. How many of
those are not a coverage gap at all, because **this loan's scenario doesn't trigger them**?

The program gate (`docs/AMQ-PROGRAM-TAXONOMY.md`) only knows FHA/VA/USDA. A second layer
exists: a refinance rule cannot apply to a purchase, an ARM rule cannot apply to a
fixed-rate loan.

---

## 2 · Pre-registered hypotheses

Stated **before** running, so the goalposts could not move:

- **H1** — scenario fields prove some rules inapplicable on loan 12607601215.
- **H2 (the falsifier)** — the gate does **not** suppress those same rules on a loan where
  the scenario *is* present. If H2 fails, the gate is a silent-false-negative machine and
  must be discarded.
- **H3** — the gate does not wrongly exclude condo/project rules on a loan whose
  `pudIndicator` is `Y` (i.e. a project *does* exist).

Why H2 dominates: a wrongly-excluded rule produces a **clean audit with no artifact for
anyone to review**. It is invisible to the 25/25 defect gate (which tests defects that
*are* present), invisible to the field Coverage Gate (fields, not triggers), and invisible
to the SME (nothing appears to review). That is strictly worse than a false positive.

---

## 3 · Results

### H1 — PASS. 287 rules excluded, each citing its proving field.

| Absent scenario | Rules | Proving evidence |
|---|---|---|
| refinance / cash-out | 196 | `loanPurposeType=PURCHASE` |
| ARM / adjustable | 45 | `amortizationType=FIXED` |
| 2nd home / investment | 17 | `propertyUsageType=PrimaryResidence` |
| co-borrower / non-occupant | 12 | borrower count = 1 |
| 2-4 unit / multi-unit | 10 | `financedUnitCount=1` |
| manufactured / mobile | 7 | `propertyEstateType=FeeSimple`, `attachmentType=Detached` |

(287 spans the whole ruleset; the net reduction to the *uncompiled* backlog is ~191, ≈8%.)

### H2 — PASS, 11/11. The negative control holds.

Mutating the loan so each absent scenario becomes present collapses every exclusion:

```
purpose → CASHOUT_REFINANCE        196 excluded → 0
purpose → NO_CASH_OUT_REFINANCE    196 excluded → 0
amortizationType → ADJUSTABLE       45 excluded → 0
propertyUsageType → SecondHome      17 excluded → 0
propertyUsageType → Investment      17 excluded → 0
financedUnitCount → 3               10 excluded → 0
add a second borrower               12 excluded → 0
constructionMethodType → Manufactured 7 excluded → 0
```

Unknowable control — a null proving field must yield `NO_DATA`, never `NOT_APPLICABLE`:

```
null loanPurposeType   → NOT_APPLICABLE=0, NO_DATA=196
null amortizationType  → NOT_APPLICABLE=0, NO_DATA=45
null propertyUsageType → NOT_APPLICABLE=0, NO_DATA=17
```

### H3 — reported FAIL (18 rules), then adjudicated by hand.

**The test was wrong, not the gate — in 6 of the first 8 cases.** Keyword presence is not
the same as the rule's *trigger*:

| Rule text (abridged) | Excluded by | Adjudication |
|---|---|---|
| "The **cash-out refinance** property is a cooperative unit…" | refinance | ✅ correct — trigger is refi |
| "In a **RefiNow** loan, the project is a condo or co-op hotel…" | refinance | ✅ correct — RefiNow is a refi product |
| "**Refi Possible** condo or co-op appears to be a condotel…" | refinance | ✅ correct |
| "The subject **2-4 unit** condominium project had over 4 units…" | 2-4 unit | ✅ correct — 1-unit loan |
| "A project review was not conducted in a **2-4 unit** condominium…" | 2-4 unit | ✅ correct |
| "Eligibility … for an established **manufactured home** condo project review" | manufactured | ✅ correct |

A cash-out-refi rule that happens to mention co-ops is still a refi rule. My H3 test made
the same error that produced my original inflated "433 excludable" estimate.

**But 2 of the 18 are a genuine bug.** See §4.

---

## 4 · THE DISJUNCTION BUG (found 2026-07-30, fixed same day)

**Symptom.** A rule listing several *alternative* triggers was excluded after disproving
only **one** of them.

```
"An exterior-only or desktop appraisal was used in a purchase transaction for a
 manufactured home, condo, leasehold, or a SFR undergoing renovation."
```

Four alternative triggers joined by `or`. The gate matched "manufactured home", proved
`propertyEstateType=FeeSimple` (not manufactured), and excluded the rule — **while condo,
leasehold, and renovation remain live doors into the same rule.**

Second instance:

```
"The condo was exempt from review without meeting the criteria of being a 2-4 unit
 project, detached unit, Freddie owned no cash-out refinance or RefiPossible…"
```

Excluded on `loanPurposeType=PURCHASE`, but "**detached unit**" is an alternative
criterion — and this loan *is* `attachmentType=Detached`, so the rule may still apply.

**Severity: HIGH.** This is the silent-false-negative class. It produces a clean PASS with
no artifact, and no existing gate detects it.

**Root cause.** The gate treated *any* keyword hit as "this rule's trigger is X". Rule text
frequently enumerates alternatives; matching one alternative does not establish the rule's
applicability condition.

**Fix (implemented).** Before excluding, detect whether the matched scenario keyword sits
inside a disjunctive list (`A, B, C, or D`). If it does, the rule may be excluded **only if
every** alternative is independently disproven; otherwise the verdict is `NO_DATA` with the
reason recorded. Conservative by construction: an undecidable disjunction never excludes.

---

## 5 · Decision

**ADOPT the scenario gate, with these constraints — all load-bearing:**

1. **Exclude only on an explicit non-null field that proves absence.** A null field is
   `unknowable` → `NO_DATA`, never `NOT_APPLICABLE`.
2. **Every exclusion records the field and value it was derived from** (grounding
   statement, per `docs/LLM-GUARDRAIL-POLICY.md` Q7b).
3. **Disjunctive triggers require all alternatives disproven** (§4).
4. **Negative-control tests are a standing gate**, not a one-off. Without them the H2
   property silently rots.
5. **Do NOT gate on these three**, kept explicit in code as `DO_NOT_GATE` so nobody
   "helpfully" adds them:
   - **condominium / project** — `projectType` is null **and `pudIndicator=Y` means a
     project EXISTS**. 93 rules stay live.
   - **construction / renovation** — `constructionMethodType` is null. Unknowable. 61 rules.
   - **HomeReady / affordable** — `productName="Conventional Fixed"` is suggestive, not
     proof. Needs SME. 50 rules.

**Honest scale.** ~191 uncompiled rules excluded, ≈8% of the 2,442 backlog. Free (no vendor
work, no SME session, no new extraction) but **not transformative**. Do not present this as
a solution to the coverage problem.

**The more valuable by-product:** three fields — **project type, construction method,
product/affordable-program name** — would move **204 rules** out of limbo. That is a
specific, cheap ask for the Touchless conversation rather than "extract everything."

---

## 5a · The tests, and why they were mutation-verified

`src/gates/test_scenario_gate.py` — 22 tests, four opposed groups:

| Group | Guards against | Cases |
|---|---|---|
| **H2** | too-loose: scenario present but rule still excluded | 8 |
| **H2b** | unknowable: null proving field treated as absent | 3 |
| **H3** | the disjunction bug (§4) | 2 + 2 structural |
| **H3b** | over-correction: intra-trigger "or" wrongly spared | 3 |
| meta | `DO_NOT_GATE` scenarios silently added to the gate | 2 |

H3 and H3b are **deliberately opposed.** The disjunction guard can fail in two directions —
too loose suppresses real rules, too tight makes the gate useless. Testing only one side
would let the other rot.

**All 22 passed on first write, which is a warning sign, not a result.** A test that has
never failed has not been shown to test anything. So each protected property was verified
by mutation — breaking the code deliberately and confirming the suite objects:

| Mutant | Tests that failed |
|---|---|
| disjunction guard disabled (reintroduces the §4 bug) | 3 |
| `unknowable` → `NOT_APPLICABLE` (the silent-suppression bug) | 3 |
| `condominium` added to `SCENARIOS` (the forbidden change) | 2 |

Each mutant was reverted and the file diffed against a backup to confirm a clean restore.
Standing gates re-run after: 25/25 defects, 438 tests, 24 gate tests.

**Why mutation testing rather than coverage:** the failure mode here is a *missing*
finding. Line coverage cannot see it — the suppressed rule's code path is simply never
entered. Only an injected fault proves the assertion is load-bearing.

## 6 · Method note worth keeping

The H3 "failure" is the most instructive result of the experiment: **a test can be wrong in
the same direction as the code**. My H3 assertion and my original 433-rule estimate shared
one flawed premise (keyword ⇒ trigger). Hand-adjudicating the failures — rather than
accepting the test's verdict — is what separated the 6 correct exclusions from the 2 real
bugs. Automated tests bound behaviour; they do not establish correctness.

---

## Related

- `src/gates/scenario_gate.py` — implementation, `DO_NOT_GATE` list
- `src/gates/test_scenario_gate.py` — H2/H3 negative controls as pytest
- `docs/LOAN-SCENARIO-APPLICABILITY.md` — the three reasons a document is absent
- `docs/LLM-GUARDRAIL-POLICY.md` — grounding statements, abstention → `NO_DATA`
- `src/gates/literal_provenance_gate.py` — the sibling gate for invented numbers
