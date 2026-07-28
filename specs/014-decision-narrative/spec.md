# Feature Specification: Decision Narrative (Per-Loan Explanatory Summary)

**Feature Branch**: `014-decision-narrative`
**Created**: 2026-07-27
**Status**: Implemented (2026-07-28 -- all 14 tasks, Phases 1-4 complete including the real Bedrock
proof; `p0/qc_engine/compiler/decision_narrative.py` new, `p0/qc_engine/engine.py`'s `to_dict()`
gains a generic `extra` param (never the literal artifact name, so FR-005's leaf-module structural
test holds against `engine.py`'s own source text, not just architecturally),
`p0/compile_runs/run_014_decision_narrative_panel/build_and_run.py` new driver. 24/24 new unit tests
green (mocked Bedrock only); full suite `pytest p0/tests -q`: 389 passed, 0 failed, 3 skipped -- zero
regressions (SC-004). Real 5-loan panel (reusing `run_013`'s comprehensive_e2e_v6 ruleset + v2 loan
profiles, signed `FactVocabulary` v7/18 facts): **5/5 loans pass validation on the FIRST attempt**
(SC-001) -- but only after two real bugs found and fixed mid-run, honestly recorded here rather than
smoothed over: (1) the initial prompt sent every one of a loan's ~2,600 real exceptions/needs_review
rows verbatim (~890K input tokens, ~$3/loan, 3/3 attempts exhausted with `narrative_text=None` on 1
of the first 2 loans tried) -- fixed by sampling deterministically per review_reason category
(`_sample_exceptions`, `_SAMPLE_PER_CATEGORY=3`) and handing the model a precomputed remainder count
instead of asking it to count thousands of rows itself (FR-008); (2) the Guide-citation regex
matched the word "citation" itself inside the model's own honest sentence ("no Fannie Mae Selling
Guide citation can be offered") as if it were a fabricated section code -- fixed by anchoring the
regex to the real code shape (`[A-Z]{1,2}[\d.\-]*\d`, e.g. `B3-2-02`/`E-3-03`) instead of "any
non-whitespace token." Final real numbers, all 5 loans, all valid on attempt 1: 5 LLM calls total,
12,617 input + 3,545 output tokens, **$0.1001 total** (Sonnet 4.6, "us." cross-region pricing) -- a
~30x cost reduction per loan vs. the pre-fix run, and none of this loan panel's touched fields
happened to carry a `guide_citations` entry in v7's 18 facts, so `referenced_guide_citations` is
honestly empty across all 5 (a real, current gap in fact/Guide-citation overlap for this specific
ruleset, not a validation bypass -- SC-006's fabricated-citation rejection path is proven by unit test
`test_invented_guide_section_fails`/`test_invented_citation_to_fill_an_honest_gap_fails`, not by this
panel, since no real citation was available to exercise honestly). Cost logged via
`qc_engine.eval_log.EvalLog.log_cost` per loan and run-level (FR-009); see
`storage/logs/run_014_decision_narrative_panel.jsonl` and
`result/qc_results/run_014_decision_narrative_panel_results.json` for the full record.

**Correction (2026-07-28, Gordon's direct review):** the panel above is a legitimate, deliberate
stress test (spec's own "hundreds of exceptions" edge case, FR-008) but a poor demonstration of the
feature's actual reviewer-facing value — `run_013`'s comprehensive_e2e_v6 ruleset (3,203 checks/loan)
is ~97% checks this 5-loan synthetic corpus was never going to have data for, so the real signal (the
25 known planted defects, `p0/fixtures/from_docs/defect_manifest.json`) drowns in noise, and the
narrative's own 3-per-category sampling had no reason to surface the specific known-defect checks by
name. A second driver, `build_and_run_validated_baseline.py`, generates the same artifact against
`result/loans/loan_0N.json` (canonical, fully-cited loan facts — confirmed byte-identical to
`p0/fixtures/from_docs/loan_0N.json`) run through `fixtures.ruleset_defects.defects_ruleset_for` — the
repo's own documented "proven, trusted rule set, 100% recall on the 25 known planted defects, 0
report drift" (`result/README.md`). Real 5-loan run: 5 LLM calls, $0.0930 total. Verified directly
against `p0/fixtures/from_docs/defect_manifest.json` and each loan's own
`demo/syn/loan 0N/00_Loan_Summary_And_Answer_Key.pdf` — loan 01 (Conventional): the validated
baseline resolves 4 of 5 known defects to a definitive `FAIL`/`EXCEPTION` (employment-date mismatch,
title-vesting mismatch, unsourced large deposit, appraisal comp-distance) with real per-document
citations, and the 5th (undisclosed Ally Bank liability) honestly resolves `NEEDS_REVIEW`/
`SOURCE_INCOMPLETE` because only one side of that comparison has a populated value — the narrative
correctly reports this as an open item rather than a confirmed catch, and every specific claim it
makes (the "5-mile urban guideline" figure included) traces to a real, source-coded check threshold,
not an invented number. Both driver scripts and both result artifacts are kept — the original
remains the SC-001 real-scale sampling proof; this one is the reviewer-facing demonstration artifact.
See `result/qc_results/run_014_decision_narrative_panel_validated_baseline_results.json` and
`storage/logs/run_014_decision_narrative_panel_validated_baseline.jsonl`.

**Input**: User description: "we also need a decision narrative at the end of the results" — a
human-readable prose summary appended to a loan's QC result, explaining *why* it received its
disposition, so a reviewer doesn't have to read hundreds of raw `CheckResult` rows to understand
what actually happened. Confirmed no existing spec covers this (`output/ROADMAP.md`'s 15 feature
entries were checked directly; the closest, `007-audit-trail-and-citation-of-record`, is about a
hash-chained tamper-evident *log*, not a reader-facing summary — a genuinely different concern).
Gordon confirmed (2026-07-27, explicit choice over a deterministic-template alternative) that the
narrative text itself should be LLM-authored, not hand-templated.

**Governs**: `output/ROADMAP.md` (new entry, `014`), `.specify/memory/constitution.md` Principle I
(determinism — see "Why an LLM narrative doesn't violate Non-Negotiable #1" below).
**Depends on**: `004-loan-disposition` (implemented — `RunResult.disposition`/`review_reasons` is
the narrative's primary input), `003a`/`003b`/`003c` (implemented — `CheckResult.citation`/`message`/
`status` are the narrative's per-exception evidence), `run_013`'s eval-log citation fix
(2026-07-27, same day — confirms `CheckResult.citation` is reliably populated end-to-end today),
`002g`/`002f` (the signed `FactVocabulary`, `storage/fact_vocabulary/v6.json` — its `guide_citations`
field is the narrative's source for *why* a rule exists, added 2026-07-27 per Gordon's direct
feedback that a narrative naming a failed check without the real Guide section behind it isn't
actually explaining anything to a reviewer).
**Foundation this builds on**: the engine already computes everything the narrative needs to
faithfully summarize — `RunResult.disposition`, `RunResult.review_reasons`, `RunResult.exceptions`
(the real `FAIL`/`WARNING` list), `RunResult.needs_review`, and every result's `citation`. This
feature adds a **read-only, one-way rendering step** downstream of a run that has already finished —
it does not touch, re-run, or in any way influence the deterministic verdict itself.

---

## Why this feature exists

`run_013`'s comprehensive run produced 16,020 individual check verdicts across 5 loans. The
structured summary (`status_counts`, `disposition`) tells a reviewer *how many* checks landed where;
`review_reasons` tells them *which categories* of concern exist. Neither tells a human, in one
paragraph, "here is what actually happened with this loan and what you should look at first" —
today getting that requires either reading the raw `CheckResult` list by hand (what this session did
manually, three times, to write `output/*.md` result summaries) or trusting a bare disposition tag
with no explanation. `RulesWorkbench`/`ExceptionReview` (this project's own front-end design
language, `CLAUDE.md`) already assumes a reviewer works loan-by-loan toward "I'm done with this loan,
next one" — that flow needs a synthesized decision narrative at the point a loan surfaces for
review, not a spreadsheet.

### Why an LLM-authored narrative doesn't violate Non-Negotiable #1

Non-Negotiable #1 ("same loan → same pass/fail, every time") governs the **verdict** — whether a
check is `PASS`/`FAIL`/`NOT_APPLICABLE`/`NEEDS_REVIEW`, and a loan's `disposition`. This feature
never computes, re-computes, or influences that verdict. It runs strictly **after** the deterministic
engine run has finished, reads that run's already-fixed output, and produces prose that describes it.
The four guardrails that keep this genuinely one-way (not a second, softer verdict channel):

1. **Compile-once, cache, never regenerate live.** The narrative is generated exactly once per
   `RunResult` and persisted alongside it (Key Entities, below) — never called again to "explain" the
   same already-computed result on a later page view. This bounds cost to one call per loan per run
   (Cost Transparency Requirement) and means a loan's stored narrative never silently drifts between
   two views of the same result.
2. **Validated closed-set grounding, same discipline as `draft_fact_names_llm.py` (002g).** Before a
   narrative is accepted, every check_id, citation, and review-reason it references is verified to
   exist verbatim in that loan's own `RunResult` — an invented check name, a citation not present in
   the real result, or a claimed reason tag not in `review_reasons` is a **validation failure**,
   causing a bounded retry (`draft_fact_names_llm.py`'s exact retry-then-explicit-failure shape, FR-
   004), never a silent pass-through of hallucinated content.
3. **Narrative text is presentation-only — read by humans, never read back by the engine.** No code
   path may parse a `decision_narrative` string to make a routing, gating, or pass/fail decision. This
   is the same one-way boundary `007`'s audit log already assumes for citations: explanatory, not
   authoritative.
4. **The prose MAY vary in wording if ever regenerated; the FACTS it asserts MUST NOT.** Re-running
   the narrative generator against the same `RunResult` (e.g. after a prompt change) can legitimately
   produce different phrasing — this is explicitly acceptable, unlike a check verdict — but
   guardrail 2's validation applies identically on every generation, so the *facts* stay pinned to
   what the deterministic run actually produced, even when the words describing them are not
   byte-identical run to run.

This mirrors `002c`'s already-accepted precedent exactly: an LLM interprets/organizes real,
already-fixed content at a point *after* the deterministic decision is made, never originates new
verdict content, and is validated before being trusted (`002c`'s KB-grounded compilation; `002g`'s
naming-proposal validation). No new exception to Non-Negotiable #1 is being requested — this is the
same boundary already drawn twice before.

### Why the narrative also needs the Guide, not just the run result

A narrative built only from `RunResult` can say *that* a check failed, but not *why the rule exists*
— "employment start date doesn't match the VOE" is a fact, not an explanation a reviewer can act on
with confidence. The same discipline the compiler already applies when grounding a fact
(`002c`/`002e`: citation adds context, it never originates new rule content) applies here too: the
narrative may draw on the signed fact vocabulary's `guide_citations` for any fact its own real
exceptions already reference, so it can say "...which the Fannie Mae Selling Guide's Personal Gifts
section (B3-4.3-04) requires be sourced and seasoned" — grounding the explanation in the same real
citation the compiler already attached, months before this loan was ever evaluated. This does not
widen FR-001's boundary in spirit — the guide citation is not new information invented for the
narrative, it is a real, already-signed artifact the fact itself carries — but it does mean the
narrative's input is `RunResult` **plus** the signed `FactVocabulary`'s citations for the facts
involved, not `RunResult` alone. See FR-001 and FR-010, below.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A reviewer reads one paragraph and knows what a loan needs (Priority: P1)

**Independent Test**: Run the 5-loan panel through the engine and generate a narrative for each
`RunResult`, then confirm a human reviewer (or an automated check standing in for one) can identify,
from the narrative alone, every `review_reason` tag and every real exception (`FAIL`/`WARNING`) the
loan actually carries — with zero items invented and zero real items omitted. Two panels satisfy
this independently, against two different rulesets, and both are kept: `run_013`'s comprehensive_e2e_v6
ruleset (3,203 checks/loan) proves the mechanism holds under real scale (Edge Cases' "hundreds of
exceptions" case); `fixtures.ruleset_defects.defects_ruleset_for` — this repo's own documented,
validated baseline ("100% recall on the 25 known planted defects, 0 report drift",
`result/README.md`) run against `result/loans/loan_0N.json` — is the one that actually demonstrates
this user story's reviewer-facing value, since it's the panel where a human can independently
cross-check the narrative against a known answer key (`p0/fixtures/from_docs/defect_manifest.json`,
each loan's own `demo/syn/loan 0N/00_Loan_Summary_And_Answer_Key.pdf`) rather than a synthetic
result too large for a person to sanity-check by hand. (Corrected 2026-07-28, Gordon's direct
review — the original proof used only the first panel, which technically satisfied SC-002 but
buried the real, checkable signal in ~97% noise from checks this test corpus has no data for.)

**Acceptance Scenarios**:

1. **Given** a loan with `disposition = AUTO_CLEARED` and empty `review_reasons`, **When** its
   narrative is generated, **Then** the narrative states the loan cleared with no exceptions — it
   MUST NOT invent a concern that doesn't exist just to have something to say.
2. **Given** a loan with `disposition = NEEDS_REVIEW` and a small, real set of known exceptions (the
   5 planted defects in `demo/syn/loan 01`, per its own `00_Loan_Summary_And_Answer_Key.pdf`), **When**
   its narrative is generated against the validated baseline result, **Then** it names each specific
   check, cites its `citation` (doc name + page), states the `review_reason` tag it contributes to,
   and — if the underlying fact carries a `guide_citations` entry — names the real Fannie Mae Selling
   Guide section that rule traces to, using the SAME check_id/citation/guide citation strings already
   present in the real `RunResult`/signed vocabulary, never a paraphrase that drops the traceability.
   **Actually executed and verified, not just illustrative** (2026-07-28): loan 01's real narrative
   names `chk-def-employment-dates-agree`, `chk-def-title-vesting-agree`, `chk-def-large-deposit`, and
   `chk-def-appraisal-comp-distance` by check_id, each with a real per-document citation (Wells Fargo
   statement, appraisal comp grid, VOE/paystub, 1003 Sections 1b/4/title commitment) — 4 of the 5
   known planted defects resolve to a confirmed `FAIL`; the 5th (`chk-def-liability-disclosed-agree`,
   the undisclosed Ally Bank liability) honestly resolves `NEEDS_REVIEW`/`SOURCE_INCOMPLETE` because
   only one comparison side has a populated value, and the narrative correctly reports it as open
   rather than a confirmed catch. See
   `result/qc_results/run_014_decision_narrative_panel_validated_baseline_results.json`.
3. **Given** a loan with multiple simultaneous `review_reasons` (e.g. `EXCEPTION` +
   `SOURCE_INCOMPLETE`, per `004`'s own multi-label design), **When** its narrative is generated,
   **Then** it addresses each distinct concern separately — it MUST NOT collapse two different reasons
   into one vague sentence that loses which is which.
4. **Given** a narrative-generation attempt that references a check_id not present in the loan's real
   `RunResult` (a validation failure, constructed for the test), **When** validation runs, **Then**
   the attempt is rejected and retried (bounded), never shipped — mirroring `draft_fact_names_llm.py`
   FR-004's exact retry-then-explicit-failure shape.

### Edge Cases

- A loan with hundreds of exceptions (e.g. `run_013`'s 3,203-check Retail rulebook, 1,600+ `FAIL`s per
  loan): the narrative MUST NOT attempt to enumerate every one — it summarizes by concern/category
  (grouped by `review_reason` and/or check archetype) and names a small, representative set of the
  highest-severity items, with an explicit count of the rest ("...and 1,637 more FAIL-status checks,
  see the full Check Detail export for the complete list"). Never silently drops the true count.
- A loan whose `RunResult` changes after a re-run (a real rule change, not a re-generation) MUST get
  a freshly generated narrative tied to the NEW result's hash — a stale narrative attached to a
  changed result is a worse failure mode than no narrative at all (silently wrong, not honestly
  absent).
- Narrative generation itself fails (API error, validation exhausts retries): the loan's structured
  result (`disposition`, `review_reasons`, exceptions) ships regardless — the narrative is additive,
  never a blocker to shipping the real, deterministic result. An explicit `decision_narrative: null`
  plus a logged failure reason, never a placeholder that reads as real content.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A narrative MUST be generated from one loan's already-computed `RunResult`
  (disposition, review_reasons, exceptions, citations) **plus** the signed `FactVocabulary`'s
  `guide_citations` for exactly the facts that loan's own real exceptions already reference — it
  MUST NOT be given access to other loans' results, the compiled ruleset's internals, an unsigned
  vocabulary, or any data not already present in one of those two real, already-fixed sources, so it
  cannot originate a claim (or a citation) that neither the deterministic run nor the signed
  vocabulary already made.
- **FR-002**: Generation MUST happen exactly once per `RunResult` (identified by the ruleset's
  `sha256` + loan_id + run timestamp) and the result MUST be persisted alongside the structured
  result — never regenerated on a later read of the same, unchanged result.
- **FR-003**: Before a generated narrative is accepted, every check_id, citation string, and
  review-reason tag it references MUST be validated against the real `RunResult` it was generated
  from. Any reference not found there is a validation failure. Bounded retry (2 additional attempts,
  matching `draft_fact_names_llm.py`'s precedent); after exhausting retries, ship the structured
  result with `decision_narrative: null` and a logged failure reason (Edge Cases) — never a narrative
  that failed validation.
- **FR-004**: The narrative generator MUST run at temperature 0 (matching every other LLM call in
  this project's compile-time pipeline, `compile_llm.MODEL_SONNET` precedent) — minimizing (not
  eliminating) run-to-run wording variance is still valuable even though FR-003's validation is the
  actual correctness guarantee, not wording stability.
- **FR-005**: This feature MUST NOT introduce any code path where `decision_narrative` text is parsed
  back into a routing, gating, or disposition decision — it is a leaf, output-only artifact. (Testable
  directly: no production code outside the rendering/export layer may import or reference the
  `decision_narrative` field.)
- **FR-006**: A loan with zero exceptions and an `AUTO_CLEARED` disposition MUST still receive a
  narrative (a short, honest "cleared cleanly" statement) — never silently skipped, so the absence of
  a narrative is never itself a signal a reviewer has to interpret.
- **FR-007**: The narrative MUST explicitly state the loan's `disposition` and enumerate every
  distinct `review_reason` tag present (Edge Case: multi-label) — it MUST NOT collapse a multi-label
  disposition into language implying a single, simpler cause.
- **FR-008**: For loans with more exceptions than are practical to enumerate individually (Edge
  Case), the narrative MUST name a representative sample plus an explicit true count of the
  remainder — never a silently truncated list that reads as complete.
- **FR-009**: Cost per narrative generation call MUST be logged (tokens, cost_usd) via the existing
  `qc_engine.eval_log.EvalLog.log_cost` mechanism (`run_013` precedent, 2026-07-27) — this is the one
  place in the current pipeline that spends real LLM cost per loan per run, and that cost must be
  visible, not folded into the "zero-LLM" claim the rest of the pipeline correctly makes.
- **FR-010**: For every named exception whose underlying fact carries one or more `guide_citations`
  in the signed `FactVocabulary`, the narrative MUST cite at least one of those real Guide sections
  when it explains that exception — never inventing a section number, date, or title, and never
  silently dropping a citation that exists for a fact it already names. If the underlying fact has
  **no** `guide_citations` yet (a real, current gap — 16 facts are signed, not all are Guide-cited),
  the narrative MUST say so honestly ("no Guide section is attached to this fact yet") rather than
  omitting the point or inventing one to fill the gap — same "honest UNSPECIFIED beats a confident
  invented number" discipline the compiler itself already follows (`CLAUDE.md` Non-Negotiable #1).

### Key Entities

- **DecisionNarrative** (new): `loan_id`, `ruleset_sha256`, `vocabulary_version` (which signed
  `FactVocabulary` version grounded this narrative's Guide citations — traceability if the vocabulary
  is later re-signed), `disposition`, `review_reasons: List[str]`, `narrative_text: str`,
  `referenced_check_ids: List[str]` (the closed set validated against the real result),
  `referenced_guide_citations: List[str]` (the closed set validated against the real, signed
  vocabulary — FR-010), `generated_at`, `model`, `validation_attempts: int`. Persisted as part of the
  run's results artifact (e.g. a new field on the `RunResult.to_dict()` output / `results.json`
  per-loan entries), never a separate untraceable side artifact.
- **RunResult** (existing, `engine.py`): unchanged in its own computation — gains a
  `decision_narrative: Optional[DecisionNarrative]` field on serialization only.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running the 5-loan panel produces exactly 5 narratives, one per loan, each passing
  FR-003's validation with zero unresolved references. Satisfied twice, deliberately, against two
  different rulesets: `run_013`'s comprehensive_e2e_v6 ruleset (real-scale stress test, 5/5 valid on
  attempt 1, $0.1001 total) and the validated `fixtures.ruleset_defects.defects_ruleset_for` baseline
  against `result/loans/loan_0N.json` (5/5 valid on attempt 1, $0.0930 total, added 2026-07-28).
- **SC-002**: A human reviewer given only the 5 narratives (not the raw `CheckResult` lists) can
  correctly state each loan's disposition and every `review_reason` tag it carries — verified by
  cross-checking the narrative's claims against the real `results.json`, not just reading the
  narrative for plausibility. **Most meaningfully proven against the validated-baseline panel**
  (2026-07-28 correction): a human reviewer can additionally cross-check loan 01's narrative directly
  against `p0/fixtures/from_docs/defect_manifest.json` and
  `demo/syn/loan 01/00_Loan_Summary_And_Answer_Key.pdf` — the independent, pre-existing answer key —
  and confirm 4 of 5 known defects are named with real citations and the 5th is honestly reported as
  an open data-completeness item, not silently dropped or fabricated as resolved. The original
  comprehensive-ruleset panel technically satisfies this criterion too (every claim it makes is
  verified accurate) but its ~3,203-check-per-loan scale is not something a human can practically
  spot-check against a known answer key by eye — which is exactly why the validated-baseline panel
  was added, not to replace this proof but to make it actually checkable.
- **SC-003**: Constructing a loan with a real exception, then testing a narrative-generation attempt
  that references a fabricated check_id not in that loan's result, confirms the validation step
  rejects it (FR-003) — proving the guardrail actually fires, not just exists in prose.
- **SC-006**: For every real exception whose fact has a `guide_citations` entry, the corresponding
  narrative names that real Guide section — verified by cross-checking each narrative's cited Guide
  sections against the real, signed `FactVocabulary`, not just reading for plausibility (FR-010).
  Constructing a narrative-generation attempt that invents a Guide section not present in the signed
  vocabulary confirms validation rejects it, the same way SC-003 proves FR-003.
- **SC-004**: Full existing test suite (`pytest p0/tests -v`) passes with zero regressions; new tests
  cover FR-001 through FR-009.
- **SC-005**: Per-loan generation cost is logged and, summed across the 5-loan panel, is reported
  explicitly in the run's cost summary — never silently merged into a "$0" claim.

---

## Assumptions

- This spec covers **generation and validation** of the narrative; it does NOT cover where/how it's
  rendered in `ExceptionReview` or exported to the xlsx/PDF Kayla-facing reports — that's a display
  concern for whichever feature owns those surfaces (out of scope here, same boundary `004`'s FR-007
  draws between disposition computation and routing/display).
- The model call is a genuinely new, per-loan-per-run LLM cost — unlike every other spec in this
  project's `002`/`003`/`004` families, which are compile-time-only or zero-LLM. This is a deliberate,
  disclosed exception (Gordon's explicit choice, 2026-07-27), not a silent departure from the
  project's cost-discipline pattern.
- Kayla has not reviewed any narrative this feature produces yet — same honest-placeholder posture
  every other LLM-touched artifact in this project carries until real SME review happens.

## Out of Scope

- Rendering/UI placement (`ExceptionReview`, xlsx/PDF export changes) — a later, separate feature.
- A run-level (all 5 loans) narrative, as opposed to per-loan — not requested; per-loan is this
  spec's exact scope ("a decision narrative at the end of the results" = at the end of each loan's
  result).
- Narrative generation for the compiled ruleset itself (a rule's own rationale) — a different
  concern from a loan's disposition narrative; not conflated here.
- Any change to `RunResult.disposition`/`review_reasons` computation — those stay exactly as `004`
  already defines them.
