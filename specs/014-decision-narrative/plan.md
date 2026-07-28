# Implementation Plan: Decision Narrative (Per-Loan Explanatory Summary)

## Design

### 1. `p0/qc_engine/compiler/decision_narrative.py` (new)

- `DecisionNarrative` dataclass (spec Key Entities): `loan_id`, `ruleset_sha256`, `vocabulary_version`,
  `disposition`, `review_reasons`, `narrative_text`, `referenced_check_ids`,
  `referenced_guide_citations`, `generated_at`, `model`, `validation_attempts`. `to_dict()`/
  `from_dict()`, mirroring every other artifact in this project (`fact_vocabulary.py` precedent)
  rather than inventing a new serialization shape.
- `_facts_for_run_result(run_result, fact_vocabulary) -> Dict[str, CanonicalFact]`: resolves each
  exception's underlying field to its `CanonicalFact` in the signed vocabulary and returns exactly
  the facts (and their real `guide_citations`) this loan's own exceptions touch — never the full
  vocabulary, so the prompt can't accidentally ground the narrative in a fact this loan never hit.
- `generate(run_result: RunResult, fact_vocabulary: FactVocabulary, client, max_retries: int = 2) ->
  DecisionNarrative`: builds the LLM prompt from `run_result.to_dict()` (disposition, review_reasons,
  exceptions with check_id/citation/message, needs_review, status counts) **plus**
  `_facts_for_run_result()`'s narrowed guide-citation lookup, calls the model at temp=0
  (`compile_llm.MODEL_SONNET`, reused, not a new model choice), validates (below), retries on
  validation failure up to `max_retries`, and on exhaustion returns a `DecisionNarrative` with
  `narrative_text=None` and a logged failure reason (never raises — the structured result must still
  ship, per spec Edge Cases). Raises `VocabularyNotSignedError` up front if `fact_vocabulary` isn't
  signed — same refuse-outright posture every other consumer of the vocabulary already has.
- `_validate(run_result, fact_vocabulary, narrative_text) -> (Set[str], Set[str])` (referenced
  check_ids, referenced guide citations) or raises: extracts every check_id-looking token / quoted
  citation from the generated text (simple, deterministic string scan — no second LLM call to "check
  the first"), confirms each check_id/doc-citation exists in `run_result.exceptions`/
  `run_result.needs_review`, confirms every `review_reasons` tag is mentioned somewhere in the text
  (FR-007, no dropped multi-label reason), and confirms every quoted Guide section string matches a
  real `guide_citations` entry on one of `_facts_for_run_result()`'s facts (FR-010) — a Guide section
  not found there is a validation failure exactly like a fabricated check_id. Mirrors
  `draft_fact_names_llm.py::_validate`'s exact shape (validate before accept, bounded retry, never
  silently pass through).

### 2. System prompt (in-module, not a separate prompt-registry — matches `compile_llm.py`'s and
`draft_fact_names_llm.py`'s existing pattern of an inline `SYSTEM_PROMPT` constant)

Explicit, non-negotiable instructions baked into every call:
- Ground every claim ONLY in the provided `RunResult` data and the provided (narrowed) guide-citation
  lookup — never invent a check, a citation, a reason, a Guide section, or a number not present in
  the input.
- State the disposition explicitly and address every `review_reasons` tag separately (FR-007).
- For each named exception, cite the real Guide section from the provided lookup if one exists for
  its fact; if none exists, say so honestly rather than omitting the point or inventing one (FR-010).
- For loans with more than N (e.g. 10) exceptions, summarize by category/severity and give the exact
  remaining count (FR-008) — never enumerate all, never silently truncate without saying so.
- Zero-exception, `AUTO_CLEARED` loans still get a short, honest narrative (FR-006) — not skipped.

### 3. Wiring into the run pipeline

- `RunResult.to_dict()` (`engine.py`) gains an optional `decision_narrative` key, populated by a
  caller (not inside `run()` itself — `run()` stays synchronous/deterministic/zero-LLM; narrative
  generation is a separate, explicit, post-processing step a caller opts into, same separation
  `002g`'s precondition-attachment has from `run()` itself).
- A new thin driver (`p0/compile_runs/run_014_decision_narrative_panel/build_and_run.py`) loads the
  same signed `FactVocabulary` the run's compile step already used, calls
  `decision_narrative.generate()` once per loan after `run()` completes (passing that vocabulary
  through), and logs cost via `qc_engine.eval_log.EvalLog.log_cost` (FR-009) — reusing `run_013`'s
  already-proven `EvalLog` class, not a new logging mechanism. **Two instances of this driver exist,
  deliberately (2026-07-28 correction), differing only in which `RunResult` they feed the same
  `generate()` call:** the original runs `run()` against `run_013`'s comprehensive_e2e_v6 ruleset +
  `storage/loan_profiles/v2` derived facts (real-scale sampling stress test); a second,
  `build_and_run_validated_baseline.py`, runs `run()` against
  `fixtures.ruleset_defects.defects_ruleset_for(loan)` — the repo's validated, "100% recall on the 25
  known planted defects" baseline (`result/README.md`) — using `result/loans/loan_0N.json` directly
  (no derived-fact overlay needed; the validated baseline only references fields this extraction
  already populates). Both write to their own `results.json`/eval-log path; neither is a replacement
  for the other, since they serve different proof purposes (SC-001's scale test vs. SC-002's
  human-checkable-against-the-answer-key demonstration).

### 4. Persistence

- Narratives are written as part of the same `results.json` per-loan entry the structured
  disposition already lives in (spec Key Entities: "never a separate untraceable side artifact") —
  no new top-level storage directory needed; this is additive to an existing, already-committed
  artifact shape.

## What this plan deliberately does not do

- No change to `engine.py::run()`'s determinism or signature — narrative generation is strictly
  post-hoc and optional-to-call.
- No UI/export wiring (`ExceptionReview`, xlsx/PDF) — Out of Scope in spec.md, a later feature.
- No new prompt-testing framework — reuses `compile_llm.py`'s existing `_client()`/model-call
  pattern and `draft_fact_names_llm.py`'s validate-then-retry shape verbatim, rather than building a
  third variant of the same idea.
- No caching layer beyond "write it once into results.json" — FR-002's "generate once" requirement is
  satisfied by the driver simply not being re-invoked for an unchanged result, not by adding a new
  cache/invalidation mechanism.

## Test plan

- Unit tests for `_validate()`: real `RunResult` + real `FactVocabulary` + a narrative referencing
  only real check_ids/citations/reasons/guide-citations passes; a narrative referencing a fabricated
  check_id fails; a narrative that drops one of two `review_reasons` tags fails (FR-007); a narrative
  that invents a Guide section not on the underlying fact fails (FR-010); a narrative for a fact with
  no `guide_citations` that honestly says so passes, and one that invents a citation to fill the gap
  fails (FR-010's honest-gap case).
- Unit tests for `generate()`'s retry/failure path: mock a client that always returns an invalid
  narrative — confirm exactly `max_retries + 1` attempts, then `narrative_text=None` +
  logged failure, never a raised exception (Edge Cases: "narrative generation itself fails... ships
  regardless"). Also confirm `VocabularyNotSignedError` on an unsigned vocabulary, raised before any
  model call.
- Integration test: run the real 5-loan panel — both instances (`run_013`'s comprehensive_e2e_v6
  ruleset, and the validated `ruleset_defects.py` baseline against `result/loans/loan_0N.json`) — and
  its already-signed vocabulary, generate real narratives, assert SC-001/SC-002/SC-005/SC-006 directly
  against the output of each. The validated-baseline run is additionally cross-checked against
  `p0/fixtures/from_docs/defect_manifest.json` and each loan's own `demo/syn/loan 0N/
  00_Loan_Summary_And_Answer_Key.pdf` — the only one of the two panels small enough for that direct,
  human-verifiable cross-check (2026-07-28 correction).
- Full suite regression: `pytest p0/tests -v` zero-regression (SC-004).
