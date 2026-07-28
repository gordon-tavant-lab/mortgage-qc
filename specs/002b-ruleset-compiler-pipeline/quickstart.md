# Quickstart: Ruleset Compiler Pipeline

**Feature**: `002b-ruleset-compiler-pipeline`

## Run sequence (once implemented)

1. **Sample** a batch of real workbook rows beyond `002a`'s 24 (`demo/rules/*.xlsx`, via
   `p0/eval_synth/taxonomy.py`'s existing classification — generalizes
   `p0/experiment_002a/sample_rows.py`'s pattern to a larger, non-throwaway sample).
2. **Map**: compile each row independently (`compiler/compile_llm.py`, generalized from
   `experiment_002a/compile_llm.py`) → one `CompiledCheckDraft` per row, one Bedrock call per row,
   Sonnet 4.6 at temperature=0 (same model `002a` validated for interpretation fidelity — G3 found
   Sonnet catches boundary-math failures Haiku misses, and this is a compile-time-only cost, not a
   per-loan runtime cost, so the more accurate model is the right default).
3. **Reduce**: run the consistency pass (`compiler/consistency.py`, FR-003) and pattern-flag pass
   (`compiler/pattern_flags.py`, FR-007/FR-008) across the whole batch.
4. **Pre-sign gate**: screen every draft's `field_name` (`compiler/catalog_screen.py`,
   User Story 3) — resolved / signable-pending-catalog-entry / blocked, per data-model.md §5.
5. **Assemble**: build a `batch-report-schema.md`-shaped report for SME review.
6. **Sign**: SME reviews the report, corrects `Check`/`FieldCatalogEntry` drafts as needed, signs
   (existing `RuleProvenance` mechanism, unmodified) — produces a `Ruleset` with `intent_records`
   populated (FR-011) and any newly-signed `FieldCatalogEntry` additions merged into the `001a`
   catalog.
7. **Verify**:
   - `Ruleset.sha256()` is stable across two runs on the same signed content (SC-001's determinism
     half).
   - `Ruleset.signoff_summary()`'s `unedited_rules()` flags a zero-edit batch loudly (SC-004).
   - Every `Check` in the signed `Ruleset` has a retrievable `RuleIntentRecord` via
     `Ruleset.intent_for(check_id)` (SC-006).
   - `qc_engine.engine.run` against a loan using this ruleset makes zero network/Bedrock calls
     (SC-005) — confirm by running with AWS credentials removed from the environment and observing
     no failure.

## What this feature does NOT do (reaffirmed from spec.md)

- No authoring UI (`009a/b/c`) — sign-off here is direct data inspection of the batch report, same
  procedural posture `001a`/`002a` already used.
- No product/program gating (`010a/b`).
- No runtime LLM call anywhere in `qc_engine.engine.run` — every LLM call in this feature happens in
  the map step (step 2 above), at compile time only.
