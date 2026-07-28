# Tasks: Decision Narrative (Per-Loan Explanatory Summary)

## Phase 1 — Data model + validation (zero LLM cost, fully testable without a model call)

- T001: `DecisionNarrative` dataclass + `to_dict()`/`from_dict()` in
  `p0/qc_engine/compiler/decision_narrative.py` — now including `vocabulary_version` and
  `referenced_guide_citations`.
- T002: `_facts_for_run_result(run_result, fact_vocabulary)` — resolves the narrowed set of
  `CanonicalFact`s this loan's own exceptions touch. Unit tests: a loan touching 2 of 16 facts
  returns exactly those 2, never the full vocabulary.
- T003: `_validate(run_result, fact_vocabulary, narrative_text)` — check_id/citation/review-reason
  cross-reference against a real `RunResult`, **plus** Guide-citation cross-reference against the
  facts `_facts_for_run_result()` returns. Unit tests: real reference passes; fabricated check_id
  fails; dropped multi-label reason fails; over-limit exception count without an explicit remainder
  count fails (FR-008); invented Guide section fails (FR-010); a fact with no `guide_citations` that
  the narrative honestly flags as uncited passes, one that invents a citation to fill the gap fails.

## Phase 2 — Generation + retry/failure path

- T004: `SYSTEM_PROMPT` (grounding rules, FR-001/006/007/008/010 encoded explicitly).
- T005: `generate(run_result, fact_vocabulary, client, max_retries=2)` — raises
  `VocabularyNotSignedError` up front on an unsigned vocabulary; builds prompt from
  `run_result.to_dict()` plus `_facts_for_run_result()`'s guide-citation lookup, calls
  `compile_llm._client()`/`MODEL_SONNET` at temp=0, validates, retries, returns
  `narrative_text=None` + logged reason on exhaustion (never raises).
- T006: Unit tests with a mocked client: valid-first-try path; valid-on-retry path;
  exhausted-retries path (assert `validation_attempts == max_retries + 1`, `narrative_text is None`);
  unsigned-vocabulary path (raises before any model call).

## Phase 3 — Wiring + cost logging

- T007: `RunResult.to_dict()` gains an optional `decision_narrative` key (serialization-only change,
  `engine.py`) — `run()` itself untouched.
- T008: Cost logging via `qc_engine.eval_log.EvalLog.log_cost` for every real generation call
  (FR-009) — extend `run_013`'s driver (which already loads the signed vocabulary for compilation;
  the narrative driver reuses that same load) or add a small standalone driver script, per plan.md §3.

## Phase 4 — Proof (real 5-loan panel, reusing run_013's fixtures and its signed vocabulary)

- T009: Generate real narratives for all 5 loans; assert SC-001 (5/5 pass validation).
- T010: Manual/automated cross-check of narrative claims against `results.json` (SC-002).
- T011: Constructed-fabrication test proving the validation guardrail actually rejects invented
  content (SC-003) — not just asserted safe in prose.
- T012: Constructed-fabrication test proving an invented Guide section is rejected, and that an
  honest "no Guide section attached yet" statement is accepted (SC-006, FR-010).
- T013: Full suite regression (`pytest p0/tests -v`) — zero regressions (SC-004).
- T014: Cost summary reported explicitly (tokens + cost_usd per loan, summed) — never folded into a
  "$0" claim (SC-005).
