# Implementation Complete When

## Overall Exit Condition
- All tasks in `tasks.md` are marked `[X]`
- `python3 -m pytest p0/ -q` exits 0 (this project has no separate lint step; `p0/` is the whole
  test surface)
- `python3 p0/harness.py` exits 0. **Confirmed by actually running it (2026-07-23), not assumed in
  advance**: the 1000-run digest legitimately MOVES to `365dc672e73e8cbb16deb82cd4395afeba7f7e3ed
  642616d1d25e4ba4e425f56` (= `POST_003D_BASELINE` in `test_p0.py` **at 003d's ship date — since the 2026-07-24 002e re-baseline, all three POST_* constants hold the current anchor `82175d07...`; 365dc672 is preserved in test_p0.py's historical comments** — era note, 2026-07-26 audit) — because `Check.to_dict()`'s
  `asdict()` emits the new `compare_field_name` field for every check regardless of kind, which
  flows into `Ruleset.sha256()` even though `demo_ruleset()` itself never uses the new kinds. The
  real invariants, both confirmed: **"byte-identical across 1000 runs: YES"** (determinism itself
  is unbroken) and **precision=1.0/recall=1.0** against labeled outcomes (zero behavioral drift in
  `demo_ruleset()`'s actual check content — the shift is purely schema-shape, not a regression).

## Phase Gates (must pass before next phase starts)

### Phase 1 — Setup
Done when: `Check` accepts `compare_field_name`; `p0/tests/test_doc_vs_doc_reconcile.py` exists and
collects zero tests cleanly.

### Phase 2 — User Story 1 (doc-vs-doc mismatch caught as a real defect)
Done when: `agree_doc_categorical`/`agree_doc_numeric` produce correct verdicts across agreement,
genuine divergence, one-side-absent (`NEEDS_REVIEW`/`SOURCE_INCOMPLETE`), both-absent
(`NOT_APPLICABLE`), and numeric tolerance boundaries + the `UNSPECIFIED` honesty guard — all
verified by test, not asserted. `validate_referential_integrity` rejects a bad `compare_field_name`.

### Phase 3 — User Story 2 (FAIL not FLAG)
Done when: a lone doc-vs-doc mismatch produces `qc_failures` non-empty, `disposition ==
"NEEDS_REVIEW"`, `review_reasons == {"EXCEPTION"}` — proven by test to be the QC-failure path, not
the reconcile-`FLAG` path `agree_categorical` uses for the analogous doc-vs-system case.

### Phase 4 — Polish
Done when: the compiler emits `compare_field_name`/the new kinds correctly given `expected_sources`
context (T010-T012); `pattern_flags.py`'s mismatch-risk gate covers the new kinds; all 5 known
doc-vs-doc defects are hand-authored in `ruleset_defects.py` and resolve their correct expected
status (`test_fixture_generation.py`, 25/25); the digest re-baseline is documented with a real
`POST_003D_BASELINE` constant (not a placeholder); `pytest p0/tests -v` passes in full; `output/
ROADMAP.md` Tension #5 is updated; `plan.md` carries a post-hoc Implementation Notes section.

## Must Not Regress
- `p0/harness.py`'s 1000-run **byte-identical-across-runs** property (determinism itself) and its
  precision=1.0/recall=1.0 against labeled outcomes — the digest *value* legitimately moved once
  more here (see Overall Exit Condition), the same way it legitimately moved once for `004`.
- `demo_ruleset()`'s 6 pre-existing reconcile checks, `000`'s `chk-def-fha-case-number`, and
  `003c`'s reconcile-archetype proof suite — behavior byte-for-byte unchanged.
- `001b`'s existing reconcile tests — pass unmodified.
- **`SourceValue`/`model.py` unchanged.** Zero diffs (spec FR-009) — the new kinds' whole design
  point is not needing to touch the source-independence guard.
- **`agree_categorical`/`agree_numeric`'s existing semantics unchanged** — still doc-vs-system,
  still `RECONCILE` phase, still `FLAG`-not-`FAIL` on divergence. This feature adds a new, separate
  path; it does not modify the old one.
- A doc-vs-doc mismatch must never be misclassified as an informational `FLAG` (would silently
  under-report a real defect — the exact failure mode this feature exists to close), and a genuine
  doc-vs-system reconcile disagreement must never be misclassified as a doc-vs-doc `FAIL` either
  (both directions, mirroring `003c`'s own SAFE-gate discipline for its partition).
- The digest change itself is expected and required (not a thing to avoid) — but it must be the
  *only* thing that changes: re-running `p0/harness.py`'s content-level checks (score/precision/
  recall against `demo_ruleset()`) must still pass, confirming the digest moved because of schema
  shape only, not because of any behavioral drift in existing checks.
