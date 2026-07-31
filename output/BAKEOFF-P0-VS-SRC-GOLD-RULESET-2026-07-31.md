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
