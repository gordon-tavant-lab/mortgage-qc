# Implementation Complete When

## Overall Exit Condition
- All tasks in `tasks.md` are marked `[X]`
- `python3 -m pytest p0/ -q` exits 0
- `python3 p0/harness.py` exits 0. Following the `003d`/`004` precedent: the 1000-run digest is
  expected to legitimately MOVE (a new `applies_if` field on every check flows into
  `Ruleset.sha256()` via `asdict()`, regardless of whether `demo_ruleset()` itself uses the new
  field) — confirm both **"byte-identical across 1000 runs: YES"** (determinism unbroken) and
  precision/recall against labeled outcomes unchanged (the shift is schema-shape only, not
  behavioral drift), the same two invariants `003d`'s criteria already required.

## Phase Gates (must pass before next phase starts)

### Phase 1 — Setup
Done when: `Check` accepts `applies_if`; `p0/tests/test_conditional_applicability.py` (planned name `test_applicability_gating.py` — naming drift, noted 2026-07-26) exists and collects
zero tests cleanly.

### Phase 2 — User Story 1 (a conditionally-scoped check resolves NOT_APPLICABLE cleanly)
Done when: the applicability gate is evaluated before kind dispatch; precondition-doesn't-hold →
`NOT_APPLICABLE`; precondition-holds → unaffected normal evaluation; precondition-field-unknown →
`NEEDS_REVIEW` with an explicit `review_reason`; `applies_if=None` → byte-for-byte identical to
today — all verified by test. `validate_referential_integrity` rejects a bad `applies_if.field_name`.
The real loan-01 gift-fund fixture resolves `NOT_APPLICABLE` (T006) — the concrete case this feature
exists to fix.

### Phase 3 — User Story 2 (compiler extracts applicability only from a row's own text)
Done when: a real recompile of the gift-fund row produces a traceable `applies_if`; a representative
sample of unconditional rows still compiles with `applies_if=None`; an ambiguous-precondition row
defaults to `None` rather than guessing — all verified against real Bedrock calls, not asserted from
prompt wording alone.

### Phase 4 — Polish
Done when: the digest re-baseline is documented with a real (not placeholder) SHA-256 constant;
`pytest p0/tests -v` passes in full; the end-to-end loan-01 re-run (T014) confirms the fix at the
integration level, not just unit tests; `output/ROADMAP.md` Tension 9 is updated; `plan.md` carries a
post-hoc Implementation Notes section (per this project's convention, `003d`'s precedent).

## Must Not Regress
- `p0/harness.py`'s 1000-run **byte-identical-across-runs** property and precision=1.0/recall=1.0
  against labeled outcomes — the digest *value* legitimately moves once more here, as it did for
  `003d`/`004`.
- Every existing check with `applies_if=None` (the overwhelming majority) — zero behavioral change,
  proven by test (T004's regression case), not assumed from the field being optional.
- `010a`'s program-level gating — unchanged, untouched; the two gating layers compose (spec FR-009),
  neither supersedes the other.
- The safe-default asymmetry (spec FR-006): a false `NOT_APPLICABLE` (a real defect silently
  resolving as not-applicable because the compiler over-extracted a precondition that isn't really
  there) is the failure mode to guard hardest against — worse than today's status quo, not an
  acceptable trade for closing the false-positive gap this feature targets. SC-003's representative-
  sample measurement exists specifically to catch this before it ships.
- `002c`'s existing grounding discipline (grounding interprets, never originates) — extended, not
  weakened, by this feature's `applies_if` extraction rule (spec FR-005).
- ~~This feature does not decode the AMQ workbook's Question-ID column~~ **[REVERSED — stale,
  flagged 2026-07-26 spec audit: FR-008 now mandates decoding it via `002f` Layer 0 clustering; this
  criterion described the abandoned original design.]**
