# Implementation Complete When

## Overall Exit Condition
- All tasks in `tasks.md` are marked `[X]`
- `python3 -m pytest p0/ -q` exits 0 (this project has no separate lint step; `p0/` is the whole
  test surface)
- `python3 p0/harness.py` exits 0 and reports its 1000-run digest unchanged from
  `8510a0a8b4b6996e047fc8534e094394ba72aae396305b0d2ecad3d6924634db`
  **[Era note, 2026-07-26 audit: true at 003c's ship date; the baseline has since legitimately
  moved three times (004 → a3f702c1, 003d → 365dc672, 002e → 82175d07, the current anchor) — the
  full supersession chain is annotated in `p0/tests/test_p0.py`. As a living criterion, read this
  as "digest matches the current pinned baseline."]**

## Phase Gates (must pass before next phase starts)

### Phase 1 — Setup
Done when: `p0/tests/test_reconcile_archetypes.py` exists and collects zero tests cleanly
(`python -m pytest p0/tests/test_reconcile_archetypes.py --collect-only` exits 0).

### Phase 2 — User Story 1 (real archetype-scale proof)
Done when: the real `reconcile-01` SSN-discrepancy row produces `PASS` on agreement and `FLAG`
(never `FAIL`) on genuine divergence; representative `agree_categorical`/`agree_numeric` pairs and
the one-side-absent/both-absent cases all resolve correctly — all against **unmodified**
`engine.py` (no code changes expected or permitted in this feature).

### Phase 3 — User Story 2 (FLAG-vs-FAIL partition safety)
Done when: a mixed ruleset (reconcile + predicate + ratio_threshold) proves, across the full US1
sample, zero instances of a reconcile `FLAG` appearing in `qc_failures`/blocking `auto_cleared`, and
zero instances of a genuine QC failure being misclassified as a `FLAG`.

### Phase 4 — Polish
Done when: the full pre-existing suite (`p0/tests/test_p0.py`, `p0/eval_synth/test_properties.py`,
`p0/tests/test_fixture_generation.py`, `p0/tests/test_predicate_archetypes.py`,
`p0/tests/test_threshold_archetypes.py`) passes unmodified alongside the new
`test_reconcile_archetypes.py`, `harness.py`'s digest is confirmed unchanged, and `plan.md` carries
a post-hoc Implementation Notes section recording it.

## Must Not Regress
- `p0/harness.py`'s 1000-run bit-exact digest (`8510a0a8b4b6996e047fc8534e094394ba72aae396305b0d2ecad3d6924634db`) — pinned since `001a`, referenced by every spec since.
- `demo_ruleset()`'s 6 pre-existing reconcile checks (`chk-borrower-name`, `chk-borrower-ssn`,
  `chk-note-rate`, `chk-principal`, `chk-property-address`, `chk-flood-zone`) and
  `000-synthetic-fixture-generation`'s `chk-def-fha-case-number` — behavior byte-for-byte unchanged.
- `001b`'s existing reconcile tests (`test_reconcile_check_compares_independently_populated_sources`,
  `test_mismo_only_loan_resolves_system_value_unchanged`,
  `test_new_named_source_readable_with_zero_engine_changes`) — pass unmodified.
- **No engine code changes.** `p0/qc_engine/engine.py`, `reconcile.py`, `model.py`, `ruleset.py` must
  have zero diffs at the end of this feature (spec.md FR-005/FR-007; the mechanism already exists —
  this feature is proof-only).
- **No doc-vs-doc capability introduced.** This feature must not add a workaround for comparing two
  independently-named document sources — that gap stays named (`output/ROADMAP.md` Tension #5), not
  quietly patched in here.
- Zero-false-auto-clear discipline (constitution Principle III) — a reconcile `FLAG` must never be
  the sole cause of `auto_cleared=False` remaining `True`-when-it-shouldn't, and must never itself
  cause a false `auto_cleared=False` either (both directions, per US2).
