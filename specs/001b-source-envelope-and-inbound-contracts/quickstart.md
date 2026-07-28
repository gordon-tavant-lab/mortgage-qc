# Quickstart: Source Envelope and Inbound Contracts

## Adding a new system source (the scaling bet this feature exists for)

1. No code change under `p0/qc_engine/*.py` is required to accept a new named source (FR-004).
2. Add the new source name to the relevant `001a` catalog entries' `expected_sources`, and (if it
   should take fallback priority over an existing source) to that field's `source_priority`.
3. Populate `SourceEnvelope.sources["<new_name>"]` for loans carrying that source.
4. Existing checks reading via `system_value()` pick it up automatically per the priority order —
   verify with the zero-regression suite (SC-001, SC-002).

## Verifying source independence in test fixtures

- Any new reconcile-check test fixture MUST construct `truth` and the relevant `sources` entry via
  genuinely separate value generation (mirroring `p0/eval_synth/generator.py`'s existing pattern) —
  run `assert_independently_constructed(...)` (data-model.md) over the fixture before trusting a
  reconcile test's result (SC-003).
- Remember: this is a **test-construction discipline**, not a runtime check on production data
  (research.md decision #2) — real Touchless/LOS data is independent by construction; the risk
  lives entirely in how synthetic test loans are built.

## Verifying a MISMO-only loan still works

- Build a test loan with `sources = {"mismo": <value>}` and no `"los"` key at all.
- Confirm `system_value()` (or its generalized equivalent) still resolves correctly (SC-005) —
  the exact scenario THESIS.md Point 2 names as the sticking point this feature must not regress.

## What this quickstart deliberately does not include

- No Touchless extractor or LOS connector build (Principle IV, contracts/inbound-contracts.md
  Non-goals).
- No multi-LOS reconciliation logic (v3 interface, roadmap feature 013).
