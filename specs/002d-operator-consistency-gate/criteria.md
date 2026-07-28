# Implementation Complete When

## Overall Exit Condition
- All tasks in `tasks.md` are marked `[X]`
- `python3 -m pytest p0/ -q` exits 0
- `python3 p0/harness.py` exits 0 with **no digest change** — unlike `003d`, this feature adds no new
  `Check` field, so `Ruleset.sha256()` for any existing ruleset (including `demo_ruleset()`) is
  expected to be byte-identical. A digest change here would indicate an unintended schema touch and
  should be treated as a red flag, not routine.

## Phase Gates (must pass before next phase starts)

### Phase 1 — Setup
Done when: `p0/tests/test_operator_consistency.py` exists and collects zero tests cleanly.

### Phase 2 — User Story 1 (prevention: prompt fix)
Done when: `SYSTEM_PROMPT` states the PASS-condition convention with 2+ few-shot inversion examples;
a real recompile of the two confirmed-bad checks' source rows produces the correct (inverted)
operator; a recompile of already-correct PASS-framed rows shows no new inversion.

### Phase 3 — User Story 2 (detection: consistency gate)
Done when: `operator_consistency_check()` exists, deterministic, no new LLM call; flags both
confirmed-bad checks; flags a set that is a superset of the 45 known suspects
(`output/operator_inversion_suspects_2026-07-24.json`); false-positive rate against correct checks is
measured and reported (target zero); wired into the compile-batch pipeline so a flagged check is
excluded from `assemble_ruleset`'s signed set.

### Phase 4 — Polish
Done when: `pytest p0/tests -v` passes in full; `output/ROADMAP.md` Tension 9 updated to reflect the
operator-direction half closed.

## Must Not Regress
- `engine.py`'s `ratio_threshold` evaluation — zero diffs (spec FR-006; confirmed correct already,
  the defect is entirely upstream in the compiler).
- No new `Check` field, no digest change to any existing ruleset (see Overall Exit Condition) — this
  distinguishes this feature from `003d`'s legitimate, expected digest bump.
- The false-positive rate against already-correct checks (SC-002) — a gate that blocks correct checks
  from sign-off is a real regression, not a acceptable trade for catching the true positives. This
  must be measured, not assumed zero.
- This feature does not re-sign `post_closing_only_ruleset.json` or regenerate any downstream report —
  that is out-of-scope follow-up housekeeping (spec Edge Cases), not silently done here.
