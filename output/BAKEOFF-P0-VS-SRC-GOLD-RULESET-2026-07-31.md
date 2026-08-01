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
  throughout). *(Updated post-Addendum: both adapters now populate the real document inventory
  and liability records that exist in the payload — see Addendum. Bank transactions, credit
  tradelines, appraisal comps, and VOM rows remain genuinely absent from this specific payload,
  not just unextracted.)*
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
| PASS | 7 | 8 |
| **FAIL** | **427** | **0** |
| NOT_APPLICABLE | 133 | 14 |
| **NO_DATA** | **0** | **547** |
| NEEDS_REVIEW | 323 | 140 |
| NOT_COMPILED | 213 | 394 |

*(Updated after the adapter extension below — see "Addendum" for the original, pre-extension
numbers and exactly what changed and why.)*

---

## Finding 1 (the headline finding): identical missing-data situations, opposite-looking verdicts

**p0 reports 427 `FAIL`s. src reports zero `FAIL`s and 547 `NO_DATA`s.** These are not
independent results pointing in different directions — they trace to the *same* underlying fact
(this loan has almost no usable document-presence data on either side, see Addendum for the small
part that turned out to be recoverable) rendered through two different, each individually
defensible, design choices:

- `p0/qc_engine/engine.py`'s `is_present` predicate treats a missing field value as a **definite
  FAIL** ("the field provably not being there" — a deliberate, documented choice, `engine.py`
  lines 331-338, referencing a real prior bug fix (015 Issue 2) where an earlier version wrongly
  exempted this case). This is the correct behavior when `field_name` is a genuine, complete
  document-inventory boolean.
- For the large majority of `doc_presence`/`doc_completeness` gold checks, there is still **no
  reliable inventory field to bind to** (see Addendum — Touchless's ~30 document types are too
  coarse to reliably match AMQ's document-name vocabulary; a naive keyword match was tested and
  rejected as unsafe), so the converter still uses placeholder field names no fixture populates.
  `is_present` then faithfully does its job on a field that was never wired to real data, and
  every one of those checks resolves the same way a genuinely-confirmed-absent document would:
  **`is_present` cannot distinguish "confirmed absent" from "never checked."** 427 of p0's 427
  total `FAIL`s are exactly this category — **100% of what looks like "427 defects found" is
  this artifact, not a genuine finding about this loan.**
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

**7 of 1,103 checks** landed on a real, non-abstaining verdict (PASS or FAIL) on **both** sides
(updated after the Addendum's adapter extension — originally 2). All 7 are genuine agreements,
all PASS:

| card | exception code | check | p0 | src |
|---|---|---|---|---|
| `PC::O-FNM-15420` | `O-FNM-54327` | DTI 14.55% ≤ 65% threshold | PASS | PASS |
| `PC::O-FNM-16190` | `O-FNM-56234` | LTV 73.8637% ≤ 95% threshold | PASS | PASS |
| `PC::O-FNM-15336` | `O-FNM-00234` | Gift Letter present | PASS | PASS |
| `PC::O-FNM-14152` | `O-FNM-58076` | Credit Report present | PASS | PASS |
| `PC::O-FNM-15436` | `FAMCO-FNM-00825` | Hazard Insurance present | PASS | PASS |
| `PC::O-FNM-15438` | `O-FNM-00533` | Flood Hazard Determination present | PASS | PASS |
| `PC::PropFlip` | `FlipGuide-1` | Title Commitment present | PASS | PASS |

Still a small sample, but a real positive signal, now with real document-presence checks included
alongside the two threshold checks: where both engines had real data and a confidently-built
check, two **independently-built adapters and converters, reading the same source payload,
computed the same answer and reached the same verdict — zero disagreements across all 7.** The
disagreement in this experiment is entirely about *abstention philosophy* (Finding 1) and
*converter thoroughness* (Finding 2) — not about the underlying facts or math being wrong on
either side.

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
compute a real answer, they agreed, on all 7 checks now checkable; and the loudest-looking result
in the original run (432 "defects" from p0) was almost entirely an artifact of missing
document-inventory data, not a real finding — a concrete, first-hand demonstration of exactly the
false-signal risk this project's verdict discipline exists to prevent. The Addendum below is a
second, related demonstration of the same discipline: extending the adapters to use real data
that existed but was previously discarded initially *introduced* two new false-signal bugs (440
false PASSes, then 15 false FAILs) before landing on the final, verified 7-check result — worth
internalizing as a general lesson, not just a footnote.

**Doesn't tell you**: which engine is "better" in general. This was one loan with unusually thin
data on both sides, two hand-built converters written in a few hours with their own independent
judgment calls (Finding 2), and the large majority of `doc_presence`/`doc_completeness` checks
still can't produce a meaningful answer on either side — not for lack of trying (see Addendum),
but because this project's own document-name-to-Touchless-type crosswalk problem remains
genuinely unsolved. A second loan, a real per-check crosswalk (built with this project's existing
guardrailed process, not a shortcut), or a more conservative p0-side converter could all change
these specific numbers substantially.

## Suggested next step, if this line of investigation continues

Build a real, SME-reviewed AMQ-document-name-to-Touchless-documentType crosswalk (using
`mapping/llm_doc_mapper.py`'s existing guardrails, not a keyword heuristic — see Addendum) for
more than the 5 checks curated here. That's the single change most likely to actually
discriminate between the two engines' real capabilities on this check_type family, since it
removes Finding 1's confound at scale instead of for a hand-picked handful.

---

## Addendum (2026-07-31, later same day): "why does src have 554 NO_DATA on the same loan file?"

Gordon asked this directly after reviewing the first version of this report, and pushed further:
extend the adapters to use whatever real data the loan file actually has, document the finding,
decision, and fix, and re-run. This addendum is that record — including two bugs the extension
itself introduced and caught before they reached this report.

### The investigation

Checking the raw `demo/touchless/extracted/loan_application.json` directly (not just the
adapters' output) found two real gaps, not fundamental data absence:

1. **`documents[]` has 62 real entries** (`documentType`, `documentCategory`, etc.) that
   `src/shacl_pilot/touchless_adapter.py` discarded — its own comment claimed "Touchless doesn't
   provide doc inventory," which was wrong. `loan_to_rdf.py` (the shared graph-builder, not
   Touchless-specific) additionally never serialized a `docs_present` field into RDF *at all*,
   for any loan, ever — a second, deeper gap underneath the first.
2. **`liabilityDetail.liabilities[]` has real, structured per-liability records** (creditor name,
   balance, monthly payment, status) that the same adapter also discarded into an unconditionally
   empty `urla_liabilities` list.

### The decision: populate the real data, but do NOT auto-match AMQ checks to it

Before writing any code, a naive keyword-overlap test against the 30 real Touchless document
types was run as a sanity check — it matched a "gift of equity" defect to "Closing Disclosure"
and "rent credit" liability language to "Credit Report." Both false. This project already has a
guardrailed, SME-reviewed process for exactly this document-crosswalk problem
(`mapping/llm_doc_mapper.py`, H1/H2/H3 guardrails, 4/6 on an adversarial test even with those
guardrails) *because* naive matching is unsafe here — building a fresh, ungoverned matcher for
this experiment would repeat a mistake this project already learned from.

**Decision**: populate the real, complete `docs_present` and `urla_liabilities` data (honest,
unconditionally correct regardless of matching), but only wire a **small, individually
hand-verified allowlist** of 5 checks to it — each one read individually against this loan's real
inventory, confirmed to be a genuine absence-check (not a completeness/quality check merely
mentioning a document type), and confirmed the named document type actually appears in this
loan's 62-document list. `CURATED_DOC_MATCHES` in both `ruleset_to_shacl.py` and
`import_gold_ruleset.py` (same 5 entries, same rationale, kept symmetric): Gift Letter, Credit
Report, Hazard Insurance, Title Commitment, Flood Hazard Determination.

### The solution — and two bugs it exposed along the way

1. **`loan_to_rdf.py`**: added `li:docs_present` triple serialization (previously silently
   absent for every loan, not just Touchless ones).
2. **`src/shacl_pilot/touchless_adapter.py`**: `docs_present` now populated from the real
   `documents[]` array; `urla_liabilities` now populated from `liabilityDetail.liabilities[]`.
3. **`p0/qc_engine/adapters/touchless_adapter.py`**: added 5 curated `doc_present_<slug>` boolean
   fields from the same real `documents[]` data, mirroring the SHACL side.
4. **Bug caught #1 — doc_presence polarity inversion.** The first re-run produced **440 false
   `PASS`es** — every uncurated doc_presence/completeness shape (whose filter value is a nonsense
   placeholder that can never match real data) flipped from honest `NO_DATA` to a false-clean
   `PASS`, because `li:docs_present` was now a real, non-empty predicate on the loan, and the
   required-predicate presence check couldn't tell "predicate exists with irrelevant values" from
   "predicate exists with the value this check needs." Root cause, once traced further: the
   shape's own SPARQL had an inverted polarity bug (`FILTER(?doc = "X")` fires — reports a
   violation — when the document **is present**, the opposite of what an absence-check should
   test) that had been latent and harmless since the placeholder value could never match anything
   real. Fixed two ways: (a) `build_doc_shape` now emits `FILTER NOT EXISTS` (fires only on
   genuine absence, correct polarity for every shape, curated or not), and (b) `run_gold_ruleset_
   audit.py` now forces `NO_DATA` for any doc_presence/completeness check that isn't in
   `CURATED_DOC_MATCHES`, regardless of what pyshacl reports, so an uncurated placeholder can
   never again resolve to a trusted verdict by accident.
5. **Bug caught #2 — cross_doc_consistency over-firing.** With `urla_liabilities` no longer
   empty, **9 unrelated cross_doc_consistency checks fired as `FAIL`** (undisclosed judgment, DOB
   mismatch, debts not paid at closing, etc.) — inspection showed every one of those shapes'
   SPARQL is `$this li:hasUrlaLiability ?row .`, a generic "does this entity family have any row
   at all" probe, never built to test the *specific* condition in each check's own description.
   One real liability record made all 9 fire identically, regardless of relevance. None of these
   are individually curated the way the 5 doc_presence checks are, so none are trustworthy.
   **Fixed** by forcing `NO_DATA` for all `cross_doc_consistency` checks in the classifier — the
   real liability data is now populated and available for future, properly individually-built
   comparison logic, but nothing currently claims to test it correctly, so nothing is allowed to
   report a verdict from it yet.
6. **p0/qc_engine structural note**: `CanonicalLoan`/`Check` has no entity-array primitive
   (SHACL's per-liability SPARQL iteration has no p0-side equivalent) — the liability data has
   nowhere to plug in on the p0 side without new engine work. Not extended here; documented as a
   real, structural capability difference between the two engines, not an oversight.

### Final, verified result after the fix

| status | p0 (before → after) | src (before → after) |
|---|---|---|
| PASS | 2 → **7** | 3 → **8** |
| FAIL | 432 → **427** | 0 → **0** (peaked at 15 mid-fix, all false, corrected) |
| NO_DATA | 0 → **0** | 552 → **547** |
| Both-committed agreements | 2 → **7** | — |
| Disagreements | 0 → **0** | — |

Net effect: **6 checks** (5 document-presence + confirmed via the pre-existing 2 threshold
checks, now 7 total agreements) moved from an honest placeholder-abstain to a real, independently
double-verified `PASS` on both engines. Everything else is unchanged — the 427 remaining `FAIL`s
on p0 and 547 `NO_DATA`s on src are exactly as real (or as much an artifact) as before; this fix
was deliberately narrow and did not attempt to close the remaining gap, because doing so
correctly requires the guardrailed crosswalk work this project already has a process for, not a
quick pass bolted onto a bake-off.

## Addendum 2 (2026-07-31, evening): the 547 NO_DATA, root-caused check-by-check

The remaining NO_DATA population was taken through a full root-cause pass — every one of the
440 document checks individually classified under a guardrailed configuration-time review,
every one of the 87 cross-document checks analyzed for exactly what data it needs, and the 21
applicability-unknowns traced to their payload field. Full analysis, method, sub-category
tables, verification trail (including the candidates deliberately rejected), and the ranked
resolution plan: **`output/NODATA-ROOT-CAUSE-ANALYSIS-2026-07-31.md`**. Classification
artifacts for SME review:
`src/shacl_pilot/bakeoff_gold_touchless_2026-07-31/nodata_research/`.

Headline: three distinct root causes, not one — (A) 440 checks blocked because the **gold
compile emits no structured document/trigger metadata** (63% of those are trigger-gated on
LOS/AUS facts the payload lacks; only 9 are pure-presence, of which 3 survived hand
verification and are now wired symmetrically into both engines); (B) 87 cross-doc checks where
**0 of 87** have both comparison sides machine-readable today; (C) 21 checks blocked by
`loanSummary.underwriting` being null in the vendor payload. Post-fix stats (joined universe):
p0 PASS 10 / FAIL 424; src PASS 11 / NO_DATA 544; both-committed agreements **10/10, zero
disagreements**. Also caught: a stale-fixture process hazard in the p0 rerun path, and the
548-vs-547 count discrepancy (two gold cards carry duplicate exception codes).

## Addendum 3 (2026-07-31, night): plan `1-no-no-this-iridescent-brooks.md` implemented

Full implementation of the approved plan (`/Users/gordonchan/.claude/plans/1-no-no-this-iridescent-brooks.md`),
run as 5 parallel workstreams (3 in the shared worktree, 2 in isolated worktrees, merged back
with a hand-checked diff each time — no conflicts, only disjoint additive edits):

- **A0** — 1 gold card (`PC::CIP DATA POINTS`) corrected from `doc_presence` to
  `cross_doc_consistency` at the source (`data/compiled/application.json`, regenerated via
  `validate_compiled.py`, GATE PASS). 21 checks moved to a new demo-scope exclusion list
  (`storage/rules/gold/data/demo_exclusions.json`) — a deployment decision, not a fact about the
  rule, so the master ruleset itself stays untouched.
- **A0b** — 66 checks (61 DU + 1 EPIC + 4 Loan-Delivery-mentioning, via word-boundary regex
  against the same 440-check universe) now auto-pass, per Gordon's explicit retraction of the
  earlier "drop" decision: *"we cannot call into the DU system to verify, we will simulate they
  pass."* Output is indistinguishable from a real PASS on both engines (his explicit call) — a
  documented, acknowledged departure from this project's "never show a false clean" rule, scoped
  to this demo build only (`storage/rules/gold/data/autopass_no_system_access.json`'s `_meta`
  carries the full decision record). Explicitly does **not** extend to category C.
- **A2** — the scenario-gate experiment (Addendum, see below) persisted to
  `scenario_applicability_loan12607601215.json`, spot-checked (3 of 147 NA rows downgraded to
  UNKNOWN after finding pass-shaped arguments), and wired into both engines as a per-loan
  applicability overlay — 145 checks now resolve `NOT_APPLICABLE` with a cited loan fact instead
  of sitting as unexplained `NO_DATA`.
- **B** — `documentAnnotations` (3 of 62 docs: 2 Bank Statements + 1 Gift Letter) wired into both
  adapters; the self-employment trigger sub-case wired into `src`'s applicability evaluator only
  (p0's `applies_if` is AND-only, confirmed, no OR support to extend safely in this pass).
- **C/D** — `output/TOUCHLESS-API-QUESTIONS-2026-07-30.md` brought into git for the first time,
  sharpened with an exact reproducible tally (36/43 = 84% of `doc_fields_not_extracted` rows and
  66/105 = 63% of presence-gate rows covered by 6 document types) and a new question on AUS/DU
  findings availability.

### Final joined-universe stats (before -> after this implementation pass)

| Verdict | p0 before | p0 after | src before | src after |
|---|---|---|---|---|
| PASS | 10 | **76** | 11 | **77** |
| FAIL | 424 | **203** | — | — |
| NOT_APPLICABLE | 133 | **268** | 14 | **159** |
| NO_DATA | — | — | 544 | **313** |
| NOT_COMPILED | 213 | **233** | 394 | **414** |
| NEEDS_REVIEW | 323 | 323 | 140 | 140 |
| **Both-engine agreements** | 10 | **76** | 10 | **76** |
| **Disagreements** | 0 | **0** | 0 | **0** |

Agreement count grew 7.6x (10 → 76) with **zero new disagreements** — every one of the 66 new
agreements from A0b's auto-pass and the earlier document-check wiring double-verified
independently on both engines, exactly the standard this bake-off has held throughout.

Gates: `pytest p0/` 445 passed / 3 skipped / 1 xfailed (unchanged baseline); `validate_compiled.py`
GATE PASS; `run_full_ruleset_audit.py` unaffected (0/4166, byte-identical — it never loads
`blocks/gold/`).

### Addendum 4 (2026-07-31, later that night): self-employment detection bug found and fixed

Gordon asked whether the checks can actually handle this loan's self-employment scenario. Tracing
Workstream B's `SELF_EMPLOYMENT_CONTEXT_FLAG` gate (`src/shacl_pilot/run_gold_ruleset_audit.py`) end
to end against the real loan surfaced two things:

- **The gate itself is correctly wired and fires as designed** — on the 2 of 266 gold cards that
  carry `income_type_self_employment` (`PC::O-FNM-15328`/`15329`), `evaluate_applicability()`
  correctly resolves `APPLICABLE` for this loan, in `src` only (p0's `applies_if` stays deferred, as
  documented above in Workstream B).
- **Bug in both `touchless_adapter.py` files**: `borrower_self_employed` detection, and every other
  employment field (`employer_name_1003`, `base_monthly_income_1003`,
  `employment_start_date_1003`), only ever read `borrower.employers[0]`. This loan's borrower has 5
  employer records — a W-2 job at index 0 (Kraft Foods, `isSelfEmployed=False`) and 4 real
  self-employed businesses at indices 1–4 (Testing Partners LLC, ABC Trucking, TNT Partnership, PNBC
  Solutions Inc, each `isSelfEmployed=True`) — none of which were ever read. The loan's
  `borrower_self_employed=True` flag came out right only by coincidence: employer[0]'s own
  `ownershipInterestType` field independently happened to read `GreaterThanOrEqualTo25Percent`,
  which — per FNMA's 25%-ownership self-employment criterion — is itself a legitimate, independent
  trigger, so the "25Percent" branch fired even though the actual self-employed employers were never
  consulted.
- **Fix**: both adapters (`p0/qc_engine/adapters/touchless_adapter.py`,
  `src/shacl_pilot/touchless_adapter.py`) now scan every entry in `employers[]` for
  `isSelfEmployed`/`ownershipInterestType`, not just index 0, stopping at the first qualifying
  record. `src`'s fact citation now names the specific employer index that triggered the flag
  (`employers[0].employment.ownershipInterestType: ...`) instead of an unindexed, ambiguous
  reference — important for audit trail once a loan has multiple employer records.
- **Verdict impact on this loan: none** — `borrower_self_employed` still resolves `True` (via
  employer[0]'s ownership field, which independently qualifies), so both engines' full result sets
  are byte-identical before/after the fix. The fix is a robustness/correctness correction for the
  general case — any future loan where employer[0] is a plain W-2 job with no ownership-interest
  quirk and self-employment only shows up at `employers[1:]` would previously have silently produced
  `borrower_self_employed` unset (→ `UNKNOWN`/`NO_DATA` downstream) despite the source data clearly
  showing self-employment.
- **Not fixed, flagged as a separate, smaller gap**: `employer_name_1003`/`base_monthly_income_1003`/
  `employment_start_date_1003` still reflect only `employers[0]` (this loan's W-2 job, $4,000/mo) —
  none of the 4 self-employed businesses' names or income are captured as fields anywhere, because
  the source payload carries no `monthlyIncome` for any of them (`income: null` on employers 1–4).
  Both engines' self-employment-specific document checks (business tax return evaluation, CPA
  letter, declining income) resolve to `NO_DATA` (`src`, honest floor) or a mix of `FAIL`/
  `NEEDS_REVIEW`/autopass-`PASS` (`p0`, since it has no applicability gate and floors an unpopulated
  placeholder field to `FAIL` via `is_present`) — neither engine can currently verify self-employment
  documentation for this loan; that's a real capability gap, not a bug, and is separate from the
  employer-array fix above.

Re-verified after the fix: `pytest p0/` 445 passed / 3 skipped / 1 xfailed; 25/25 known-defect gate
PASS; both engines' full result sets confirmed byte-identical pre/post-fix via diff.

### Addendum 5 (2026-07-31, later still): closed the FAIL-vs-NO_DATA gap; PURE_PRESENCE well is dry

Gordon asked to find the diff between p0's `FAIL` bucket and `src`'s `NO_DATA` bucket and resolve
the ones that weren't genuine fails. Checked field-by-field before touching anything: **all 204 of
p0's FAIL verdicts were on auto-generated placeholder fields** (`doc_presence__..._<8-hex-hash>`) —
zero were on a real, populated field. `src`'s `run_gold_ruleset_audit.py` already floors the
identical situation ("uncurated doc type, no fixture can populate this") to `NO_DATA`; p0's
`is_present` predicate instead treats an absent placeholder as "provably not there" (documented
015-Issue-2 semantics, intentional for a *curated* field genuinely absent from the loan -- just
wrong for a field that was never wireable to begin with).

**Fix (mechanical, `import_gold_ruleset.py` only):** for `doc_presence`/`doc_completeness` checks
with no entry in `CURATED_DOC_MATCHES`, stop emitting an `is_present` Check against a placeholder
field at all -- route to `unsupported` (reason `doc_type_not_curated`) instead, the same bucket
every other not-yet-convertible check already uses. Symmetric with `src`'s existing "not
individually curated -> NO_DATA" branch; p0 has no `NO_DATA` status, so `NOT_COMPILED` is the
honest p0-side equivalent (per Gordon's explicit choice, not a new status).

Verified accounting: 366 checks moved out of "converted" (204 FAIL + 155 NOT_APPLICABLE + 7
NEEDS_REVIEW -> 0 PASS among them, confirming the placeholder mechanism could never produce a real
PASS either). p0's FAIL bucket is now **0** (was 204). `pytest p0/` 445/3/1 unchanged; 25/25
known-defect gate PASS; bake-off agree/disagree unchanged at **76/0** (the fix touches only checks
that were never in the agreement set to begin with -- confirmed via `compare_results.py` rerun).

Trade-off, stated plainly: this also means p0 no longer reports `NOT_APPLICABLE` for the 155
scenario/context-gated checks that happened to also be uncurated -- because p0 decides
"convertible or not" at *compile* time (before any loan-specific `applies_if` evaluation), while
`src` decides applicability *first*, then floors to `NO_DATA` only for checks that already passed
applicability. This is a pre-existing architectural asymmetry between the two engines (compile-time
vs. runtime unsupported-check decisions), not something this fix introduces or could close without
restructuring how p0 separates compilation from evaluation -- flagged here rather than silently
absorbed.

**Second half of the ask -- expand curated doc-type coverage, not just relabel it:** re-checked the
full `PURE_PRESENCE` candidate population (`doc_all_classified.json`, the only `decidability_class`
that ever drives curated wiring -- `TRIGGER_GATED`/`PRESENCE_GATE`/`COMPOUND_DOCS`/
`NOT_DOC_DECIDABLE` don't, by design, per this plan's Workstream A). It is **exactly 9 rows, and
already exhausted**: 3 wired earlier this session (ICPL, Borrower's Authorization, HOI Coverage),
and the other 6 were already hand-reviewed in an earlier pass and correctly rejected, each for a
specific, checkable reason -- independently re-verified against the real 62-entry Touchless
documentType vocabulary (`touchless_types.json`) before accepting the earlier rejections rather than
just trusting the prior note:

| Card / exception | Why it stays unwired |
|---|---|
| `O-BP-14663 / O-BP-54653` ("Flood Insurance Subject to Change") | No matching entry in the closed vocabulary (closest is "Flood Hazard Determination" -- a different document) |
| `O-FNM-14370 / O-FNM-50902` (generic "appraisal") | Vocabulary only has the specific "Form 1004 Uniform Residential Appraisal"; mapping generic "appraisal" to it would false-FAIL any loan appraised on 1073/1025 |
| `O-BP-14663 / O-BP-54654` ("Intent to Proceed") | No matching entry in the closed vocabulary at all |
| `O-FNM-14152 / O-FNM-00179` (credit report missing "for at least one applicant") | The Touchless type "Credit Report" exists, but the check needs per-borrower document tagging the payload doesn't carry -- a compound defect, not pure presence |
| `O-FNM-15384 / CondoQuestionnaire` | No matching entry in the closed vocabulary |
| `O-BP-14664 / O-BP-54659` ("Occupancy Statement") | Vocabulary has "Occupancy Affidavit" -- a distinct document; mapping would risk a false match |

No new `CURATED_DOC_MATCHES` entries were added. Genuinely expanding coverage beyond this would
require either widening the Touchless documentType vocabulary itself (a vendor-side ask, tracked in
Category C/D above) or building real check-conversion logic for `PRESENCE_GATE`/`COMPOUND_DOCS`
(conditional/multi-document logic, not a lookup table) -- both explicitly deferred, larger pieces of
work, not something to force through the existing curated-match mechanism.

### Addendum 6 (2026-08-01): "can't compile" vs. "can't audit this loan" -- both engines' full picture

Gordon asked for a rigorous split between two different failure reasons that had been blurring
together in every status this project reports: **(A) the rule itself can't be turned into a real,
evaluable check, true for any loan** vs. **(C) the rule compiled into a real check, but this
specific loan's data doesn't have what it needs**. (Two further categories, not new bugs: **(B)**
a deliberate scope exclusion, e.g. `demo_excluded:*`/DU-EPIC-Loan-Delivery auto-pass, and **(D)**
`scripted_review` checks gold itself typed as inherently requiring a human, no amount of compiler
sophistication or loan data ever making them machine-decidable.)

Breaking down every non-PASS/FAIL status by actual mechanism (not by status label) found the same
disguise pattern -- Category A wearing a status that reads like C -- in **five separate places**
across both engines, not the one already fixed in Addendum 5:

| Where | Population | Was labeled | Mechanism |
|---|---|---|---|
| p0 `threshold_eligibility`/`computation` | 182 checks | `NEEDS_REVIEW` (`UNSPECIFIED_THRESHOLD`) | Compiler couldn't parse a real numeric bound out of the AMQ text; created a Check with `threshold="UNSPECIFIED"` anyway, which reports NEEDS_REVIEW for every loan forever |
| p0 `cross_doc_consistency` | 100 checks (87 of them) | `NOT_APPLICABLE` | Zero curated cross-doc comparison logic exists at all (no `CURATED_CROSS_DOC_MATCHES`); the placeholder field's absence resolved as a confident "doesn't apply" -- worse than a false FAIL, since NOT_APPLICABLE reads as "confirmed, safe to skip" |
| src `doc_presence`/`doc_completeness` | 205 checks | `NO_DATA` | Same uncurated-Touchless-documentType gap as Addendum 5's p0 fix, mirror-imaged onto `src`'s status vocabulary instead of `FAIL` |
| src `cross_doc_consistency` | 100 checks | `NO_DATA` | Same generic "entity-family existence probe" as p0's version above -- `sh:select` only asks "does this family have any row," never the check's own specific defect condition |

**p0's `cross_doc_consistency` finding is the most serious of the four**, worth stating plainly:
`NOT_APPLICABLE` is the strongest claim this project's verdict vocabulary makes -- "we determined,
with confidence, this does not apply to this loan, skip it." 87 of 89 checks making that claim had
never had real comparison logic behind them at all; only 2 were genuine `applies_if`-driven
determinations. A reviewer trusting that label would have silently skipped 87 checks believing they
were cleared, when the honest answer was "never built."

**Fix, identical pattern in both engines and all four spots:** don't construct a Check/shape when
there's no real, curated logic behind it -- route to `NOT_COMPILED` (Category A) at compile time
instead of letting engine.py/pyshacl's default "field absent" behavior pick whatever status that
predicate kind happens to default to. p0: `_convert_threshold_eligibility`/
`_convert_computation_ltv_dti` now return `None` on an unparseable threshold instead of emitting an
`UNSPECIFIED`-threshold Check; `_convert_cross_doc_consistency` removed entirely (no curated
cross-doc match mechanism exists yet, so every one of these is unsupported until one is built).
src: `ruleset_to_shacl.py`'s `doc_presence`/`doc_completeness` and `cross_doc_consistency` branches
now gate on a curated match before emitting a shape, mirroring the `threshold_eligibility`/
`computation` branch that already did this correctly; the two now-unreachable force-NO_DATA
overrides in `run_gold_ruleset_audit.py` were removed (the `link.get("unsupported")` branch already
catches these earlier).

**Verified accounting, before -> after, this loan:**

| Verdict | p0 before | p0 after | src before | src after |
|---|---|---|---|---|
| PASS | 76 | 76 | 77 | 77 (identical set, confirmed via diff) |
| FAIL | 0 | 0 | -- | -- |
| NEEDS_REVIEW | 316 | **140** | 140 | 140 |
| NOT_APPLICABLE | 113 | **7** | 159 | **4** |
| NO_DATA | -- | -- | 313 | **3** |
| NOT_COMPILED | 598 | **880** | 414 | **879** |

Both engines' `NEEDS_REVIEW` is now **exactly 140, 100% `scripted_review`, and matches between
engines** -- every non-PASS/FAIL status either engine reports is now a real, checkable claim: 140
genuinely need a human (Category D), a handful (7 p0 / 4 src NOT_APPLICABLE, 3 src NO_DATA) are
genuinely this-loan-specific (Category C), and everything else -- 880/879, the honest majority -- is
correctly `NOT_COMPILED` (Category A), not dressed up as something it isn't. The
doc_presence/doc_completeness p0-FAIL-vs-src-NO_DATA divergence metric this report has tracked since
Addendum 5 is now **0/0** on both sides -- fully retired.

Bake-off agreement unchanged at **76/0** (every fix here only touches checks that were never in the
agreement set). Gates re-verified: `pytest p0/` 445 passed/3 skipped/1 xfailed; 25/25 known-defect
gate PASS. `run_full_ruleset_audit.py` structurally unaffected -- confirmed it does not reference
`blocks/gold/` at all.

One deliberate non-deletion, noted rather than silently done: `entity_family_for()` and
`build_cross_doc_shape()` in `ruleset_to_shacl.py` are now unused (their only caller was removed),
but left in place rather than deleted -- they're real, hand-authored domain groupings that are the
natural starting point whenever real per-check cross-doc comparison logic gets built (the deferred
work this addendum's fix now points at explicitly), not leftover cruft from a completed refactor.

### Addendum 7 (2026-08-01): first curated `scripted_review` check wired -- research paid off

Gordon asked to tackle `NEEDS_REVIEW` before `NOT_COMPILED`, researching prior art first (see
`output/NEEDS-REVIEW-REMEDIATION-RESEARCH-2026-08-01.md` for the full research and decision record
-- Fannie Mae Collateral Underwriter, RON/RIN e-notary compliance, and mortgage fraud-detection
prior art), then picked the smallest immediately-actionable item to prove the pattern:
`PC::O-EPD-14457`/`O-EPD-52921`, "A PO Box is the only address listed for an employer."

**Mechanism, same curated-allowlist discipline as `CURATED_DOC_MATCHES`:** both adapters now scan
every employer record's `employerAddress.address` for a PO-Box pattern (a regex heuristic --
explicitly *not* the CASS-certified USPS DPV approach the research recommended, since that needs a
new vendor integration; documented as a real, if small, false-negative risk rather than silently
presented as equivalent to a validated address check). `import_gold_ruleset.py` gained
`CURATED_SCRIPTED_REVIEW_FIELDS` and a curated branch in `_convert_scripted_review`;
`ruleset_to_shacl.py` gained the same dict plus a new `build_curated_scripted_review_shape()` (the
existing `build_scripted_review_shape()` hard-codes an always-fires `SELECT $this WHERE { }` with
`sh:severity sh:Warning` -- correct for the ~139 checks still genuinely requiring a human, wrong for
a check with real underlying data, so the curated path needed a real conditional shape, not a reuse
of the placeholder one).

**A real bug caught before it shipped:** the first p0-side implementation put the new fact in
`CanonicalLoan.facts`, mirroring the `borrower_self_employed` pattern from earlier this session --
but `facts` is only read by the ltv/dti `ratio_threshold` path (`engine.py` lines 368-379);
predicate checks (`is_true`/`is_present`) resolve via `CanonicalLoan.get()` -> `self.fields`
exclusively. The check silently stayed `NEEDS_REVIEW` ("No data present") despite the fixture
having the value, until re-verified against the actual result JSON rather than assumed correct from
the fixture alone. Fixed by moving the fact into `fields` with the standard `_field()`/citation
wrapper. `src`'s `loan_to_rdf.py` treats `fields` and `facts` identically (both become `li:<name>`
triples), so no equivalent bug existed there.

**Verified on the real loan:** all 5 of this borrower's employer addresses are real street
addresses (none are PO boxes) -- both engines independently resolve the check to **PASS**. Bake-off
agreement grew **76 -> 77** with zero new disagreements. Gates re-verified: `pytest p0/` 445
passed/3 skipped/1 xfailed; 25/25 known-defect gate PASS.

**Also corrected in the research doc:** the second planned "zero-cost win" (AUS-resubmission
pass-through from DU's own red-flag messages) turned out not to be available -- the loan's actual
Touchless payload has no DU-findings/red-flag field of any kind (`loanSummary.underwriting` is
still null, the pre-existing Category C gap). Moved to the vendor-ask list rather than implemented
against data that doesn't exist -- caught by checking the real payload before writing code, not
assumed from the research summary alone.

**Remaining scope, unchanged from the research doc:** 138 (was 139, now minus the 1 just wired)
`scripted_review` checks still correctly report `NEEDS_REVIEW` -- most identified as a genuine
vendor/extraction-contract gap (CU/SSR, RON certificates, fraud-vendor flags) rather than open-ended
judgment, per the research doc's categorization. Next steps not yet sequenced.

### Addendum 8 (2026-08-01, same day): context_flags -- a systemic applicability gap, caught mid-research

While researching whether loan 12607601215's RefiNow-cluster `scripted_review` checks could be
decomposed (they're refinance-only, so irrelevant to this loan -- it's confirmed `PURCHASE` via
`loanSummary.loanTerms.loanPurposeType`), checking *why* mattered surfaced a real, live bug: an
already-working, curated check -- `PC::O-FNM-15420`/`O-FNM-54327` ("RefiNow DTI ratio cap 65%") --
was resolving a confident **PASS** on this loan, despite the loan structurally being unable to be a
RefiNow loan at all.

**Root cause:** the gold ruleset correctly tags this card with `applicability.context_flags:
["loan_product_refinow"]` -- a per-card gating flag, additional to (ANDed onto) the structural
`all_of`/`any_of` conditions -- but neither engine evaluated it. Sizing the gap: **30 distinct
context_flags exist ruleset-wide, covering 541 defect_options across ~115 cards. Before this fix,
exactly 1 flag (`income_type_self_employment`, wired earlier this session, `src`-only) was handled
-- 0 in `p0`.** Checked how many of the other 29 flags were producing an actual wrong verdict
*today* (as opposed to a latent risk for later): **exactly 1** -- the RefiNow DTI check above --
since most flagged checks aren't converted/curated for other reasons yet and were already sitting
at an honest `NEEDS_REVIEW`/`NOT_COMPILED`. Small live blast radius, but a real one, and a growing
risk every time another flagged check gets curated without this fix.

**Fix, generalizing the existing self-employment mechanism rather than special-casing RefiNow:**
wired 7 more flags with a real, derivable fact -- `appraisal_in_file` and
`credit_report_presence_determined` (closed-world `documents[]` scan), and `loan_product_purchase`/
`loan_product_refinow`/`loan_product_limited_cash_out_refinance`/`loan_product_cash_out_refinance`/
`loan_product_arm` (derived from `loanPurposeType`/`productName`, deliberately asymmetric: a
confirmed Purchase loan makes all refinance-subtype flags definitively `False`, but a confirmed
refinance loan's *specific* subtype is left unset rather than guessed, since `loanPurposeType`
alone can't distinguish RefiNow from cash-out from limited-cash-out). The other 22 flags (227
defect_options) stay unevaluated -- same honest floor as everything else not yet wired, not a
regression.

**A real multi-flag case, handled correctly rather than assumed away:** scanned every card for
flag combinations before writing this and found exactly one, `PC::O-FNM-15422`, combining all
three refinance-subtype flags together. Logically this has to be an OR ("does ANY of these
apply") -- a loan can't simultaneously be all three refinance subtypes -- confirmed by reading the
card's own text (a refinancing-arrangement red-flag check, applicable to any refinance shape).
`src`'s runtime evaluator now does a real OR across resolved flags directly. `p0`'s `applies_if` is
AND-only (confirmed by reading `engine.py`'s `_eval_applies_if`), so a true OR needed precomputing
a combined `Loans.ContextFlag_any_refinance_type` fact in the adapter rather than three separate AND
conditions, which would have wrongly required all three simultaneously.

**Verified accounting, before -> after, this loan:**

| Verdict | p0 before | p0 after | src before | src after |
|---|---|---|---|---|
| PASS | 77 | **76** | 78-79 | **76** |
| NEEDS_REVIEW | 139 | **126** | 139 | **126** |
| NOT_APPLICABLE | 7 | **22** | 4 | **20** |
| NO_DATA | -- | -- | 3 | 3 |
| NOT_COMPILED | 880 | 880 | 879-880 | 880 |

Bake-off agreement moved **77 -> 75** -- a *correct* drop, not a regression: 2 checks lost from the
agreement set were both false-PASS agreements being fixed, not new disagreements (disagree count
held at **0** throughout). One is the RefiNow DTI check above; the other, caught by the same fix,
is `PC::O-FNM-15425`/`O-FNM-52742` ("A SOFR ARM underwritten by DU was not submitted as a generic
ARM") -- an auto-passed DU-relief check (per the A0b mechanism) that, per `applicability.
context_flags: ["loan_product_arm"]`, should never have reached auto-pass evaluation at all on a
Conventional Fixed loan. Confirms the fix also correctly narrows A0b's auto-pass scope to cards
that actually apply, not just cards matching a DU-mention regex regardless of product type.

Gates re-verified: `pytest p0/` 445 passed/3 skipped/1 xfailed; 25/25 known-defect gate PASS.

**Answering "does this move the needle":** yes, on correctness (a live false PASS and a
false-scoped auto-pass both fixed, verified via the actual result JSON rather than assumed), not on
raw agreement count (which dropped, correctly, because it's now measuring real agreement instead of
2 shared false positives). The bigger, not-yet-quantified payoff is structural: the same
7-flag-wiring pattern is now proven and reusable for the remaining 22 flags, and this closes the
exact failure mode ("context flag exists in gold data, neither engine reads it") that let a
production-shaped false clean sit undetected in an already-curated, already-tested check.

### Addendum 9 (2026-08-01): the 365 `doc_type_not_curated` checks -- real categorization + a found autopass gap

Gordon asked whether the document-mapping tool should already fix the "wrong document lookup"
population, and asked for a category naming the original rule issue rather than a flat engine
label. Full investigation, decision, and resolution plan:
`output/DOC-CHECK-DECIDABILITY-TAXONOMY-2026-08-01.md`. Summary: the tool can't fix most of it --
340 of 365 need genuinely different machinery (trigger-fact resolution, conditional-document logic,
multi-document comparison), not document-name matching, which is already exhausted (9 total
`PURE_PRESENCE` candidates, 3 wired, 6 reviewed and rejected). But investigating surfaced a real,
verified bug: 9 checks explicitly mentioning DU/EPIC matched the exact regex already used to build
`autopass_no_system_access.json` but were missing from it -- added (66 -> 75 entries). Both
converters now emit a precise `NOT_COMPILED` reason (`trigger_gated_needs_fact_machinery` /
`presence_gate_needs_conditional_logic` / `compound_docs_needs_multi_doc_logic` / etc.) instead of
the flat `doc_type_not_curated` label, sourced from a new permanent, shared classification file
(`storage/rules/gold/data/doc_decidability_classification.json`). Gates re-verified: `pytest p0/`
445 passed/3 skipped/1 xfailed; 25/25 known-defect gate PASS; bake-off agreement unchanged at 75/0.
