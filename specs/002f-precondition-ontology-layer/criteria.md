# Implementation Complete When

## Overall Exit Condition
- All tasks in `tasks.md` are marked `[X]`
- `python3 -m pytest p0/ -q` exits 0
- `python3 p0/harness.py` exits 0 with **no digest change** — this feature adds no new field to
  `Check`/`Ruleset` (that's `002e`'s job, consuming this layer's output); a digest change here would
  indicate an unintended `qc_engine` touch and should be treated as a red flag.

## Phase Gates (must pass before next phase starts)

### Phase 1 — Setup
Done when: `p0/ontology_extraction/` package exists and imports cleanly with zero `qc_engine`
references; the real-data fixture is checked in; test module skeletons collect zero tests cleanly.

### Phase 2 — User Story 1 (Layer 0 clustering)
Done when: Layer 0 reproduces the real 24-entry/3,255-row result against the actual Retail
Post-Closing data; an unparseable dependency expression is reported, not dropped; output is
byte-identical across repeated runs — all verified by test.

### Phase 3 — User Story 2 (Layer 1 extraction)
Done when: a real recompile shows deontic-modality + cross-reference-target classified as explicit,
separate signals; the gift-fund row extracts correctly with a traceable span; unconditional and
ambiguous rows correctly stay precondition-free.

### Phase 4 — User Story 3 (Layer 2 grounded extraction)
Done when: Layer 2 sources proposals only via `002c`'s existing KB retrieval (never synthesizes);
the automated grounding-verification check demonstrably rejects an unsupported-citation case before
judging runs; a Layer-2 proposal is never auto-approved even when the judge panel would normally
unanimously approve — mandatory human review, always, for this layer specifically.

### Phase 5 — Polish
Done when: the full 0→1→2 pipeline sequences correctly (no row double-processed); a malformed-LLM-
output case retries then produces an explicit `parse_failed` state, never a guessed default
(Onity-adopted, SC-007); a low-structure input set trips the coverage circuit-breaker and halts
Layer 1/2 expansion rather than proceeding silently (Onity-adopted, SC-008); the
zero-qc_engine-imports check passes as an automated test, not a manual read; `pytest p0/tests -v`
passes in full against `002c`'s pre-existing 164 tests plus this feature's new ones; Layer 0's real
coverage number is measured and reported (not assumed); `output/ROADMAP.md` is updated.

## Must Not Regress
- The two Onity-adopted mechanisms (bounded-retry-then-abstain, coverage circuit-breaker) are
  permanent parts of this package's contract, not demo-only conveniences to drop once the mortgage
  use case feels proven — they are precisely what makes reuse against an unseen rule source safe.
- `002c`'s existing 164 tests, `knowledge_base.py`/`judge_panel.py`'s existing behavior — this
  feature calls those modules, never modifies them.
- The reusability guarantee (spec FR-009/SC-005): `p0/ontology_extraction/` must remain importable
  with zero `qc_engine` dependency for the lifetime of this feature, enforced by a real automated
  check, not a one-time manual verification that can silently rot.
- The trust asymmetry (spec FR-007): Layer-2-sourced preconditions are **never** auto-approved,
  regardless of how the underlying judge panel scores them — this is a deliberate, permanent
  divergence from `002c`'s default policy for this one use case, not a temporary caution to relax
  once "enough" real-world evidence accumulates without an explicit spec revision.
- Layer sequencing (spec FR-008): a row resolved by Layer 0 must never be re-processed (and
  potentially re-priced in LLM cost) by Layer 1 or 2.
