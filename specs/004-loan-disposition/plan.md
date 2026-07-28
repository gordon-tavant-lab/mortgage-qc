# Implementation Plan: Loan Disposition (Composition Layer)

**Branch**: `004-loan-disposition` | **Date**: 2026-07-16 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/004-loan-disposition/spec.md`

## Summary

Compose a loan's full `RunResult` into a binary `Disposition` (`AUTO_CLEARED`/`NEEDS_REVIEW`) plus an
open, multi-label `review_reasons` tag set that names *why* — `EXCEPTION` (a genuine QC-phase
failure), `LOW_CONFIDENCE` (the confidence gate withheld a `PASS`), `SOURCE_INCOMPLETE` (a reconcile
check with one side absent) are the three initial tags, each derived from a code path that already
exists and already knows its own reason. Unlike `003c` (zero engine touch), this feature makes one
small, deliberate addition to `p0/qc_engine/engine.py`: a `review_reason` field on `CheckResult`,
populated generically (by `phase`+`status`, not per-check-kind) so a future check-kind or gate gets
tagged automatically without this feature's aggregation logic ever changing. The binary split is
provably identical to the existing `auto_cleared` boolean — this is an additive, backward-compatible
change, not a redefinition.

## Technical Context

**Language/Version**: Python 3.9-compatible (project-wide constraint).
**Primary Dependencies**: None new. Touches `p0/qc_engine/engine.py` only: one new `CheckResult`
field (`review_reason: Optional[str] = None`), a small generic tagging block inserted once (not
per-check-kind) immediately after `_eval_check`'s main `if/elif` dispatch, one line added to the
existing confidence-gate block, and two new `RunResult` properties (`review_reasons`, `disposition`).
No changes to `model.py`, `ruleset.py`, `reconcile.py`, `money.py`, or `catalog.py`.
**Storage**: None new. Test fixtures are constructed in-memory, same pattern as `003a`/`003b`/`003c`.
**Testing**: New `p0/tests/test_loan_disposition.py` covering US1 (tag correctness per reason, both
individually and combined), US2 (FLAG never tags), US3 (a never-seen-before tag surfaces with zero
aggregation-code changes).
**Target Platform**: Local execution, same as all of `p0/` — no service.
**Project Type**: Small, additive engine change (one new dataclass field + ~6 lines across 2 existing
functions) + new composition properties + tests.
**Performance Goals**: N/A — `review_reasons`/`disposition` are O(n) over an already-computed
`results` list, no new I/O or loop-order-of-magnitude change.
**Constraints**: `auto_cleared`'s existing boundary MUST be preserved exactly (FR-006) — `bool(review_reasons)
== (bool(qc_failures) or bool(needs_review))` must hold by construction, not by coincidence (see Data
Model below for why the generic tagging rule guarantees this). A `FLAG` must never produce a tag
(FR-005) — guaranteed by construction too, since neither tagging condition matches `status == "FLAG"`.
**Scale/Scope**: Three initial tags from three already-existing review-worthy code paths — this
feature does not attempt to anticipate or pre-build tags for check-kinds that don't exist yet (e.g. a
future doc-vs-doc reconcile kind would tag itself at its own site, per Tension #5, not here).

## Constitution Check

*GATE: evaluated against `.specify/memory/constitution.md` v1.1.1.*

| Principle | Status | Note |
|---|---|---|
| I — Determinism of the correct computation | ✅ PASS | `review_reason` is a plain string literal assigned at existing deterministic branches (`phase`+`status`, already-computed values) — no float, no wall-clock, no network, no new randomness. |
| II — Compile, then run | ✅ PASS / N/A | No LLM touches this feature — pure post-processing of already-evaluated `CheckResult`s. |
| III — Eval is foundational | ✅ PASS | SC-001–005 make correctness, the FLAG-exclusion guarantee, the `auto_cleared` equivalence, and the open-vocabulary claim (SC-004) explicit, testable gates. |
| IV — Build the core, assume the periphery | ✅ PASS | This is the Apply-surface composition seam the roadmap named as its own feature — the core, not the periphery. |
| V — Source independence | ✅ PASS | Untouched: this feature reads `phase`/`status` (already correctly computed by `003a`/`003b`/`003c`) and does not re-derive or weaken the RECONCILE/QC boundary. FR-005's FLAG-exclusion is a direct expression of Principle V holding through the new composition. |
| VI — Configurable by non-technical users | N/A this feature | No authoring-surface change. |
| VII — Configuration is authored data | ⚠️ PASS, with a named limitation | The *aggregation mechanism* is genuinely open — adding a new tag never requires touching `review_reasons`/`disposition` (proven by SC-004). But the three initial tag *values* are still Python string literals at 2-3 engine.py sites, not an SME-editable config file the way `field_catalog.json`'s vocabulary is. Honest scope: this feature makes the mechanism extensible: it does not make the vocabulary externally authorable. That would be a real, separate future step (e.g. tags declared in the catalog itself) — not assumed or implied here. |

**No unjustified violations.** The Principle VII note is a named limitation, not a violation requiring
a Complexity Tracking entry — the constitution's own bar is "configuration IS authored data," and the
`Check`/`Ruleset` schema this feature reads remains exactly that; the new tag literals are engine
*labels* for existing, already-authored verdicts, not a new judgment-bearing decision surface.

## Project Structure

### Documentation (this feature)

```text
specs/004-loan-disposition/
├── spec.md
├── plan.md                  # This file
├── data-model.md            # Phase 1 output — Disposition/review_reason/review_reasons ARE new
│                             #   entities this feature introduces (unlike 003a/b/c's pure hardening),
│                             #   so unlike those specs this one warrants documenting them formally
└── tasks.md                 # Phase 2 output (/speckit-tasks)
```

No `contracts/` or `quickstart.md` — this feature exposes no external interface (no API, no CLI, no
UI); everything is an internal Python composition consumed by future in-process callers (`006`/`007`/
`008`), which is exactly why `data-model.md` (documenting the shape those future features will
consume) is the one Phase 1 artifact that earns its keep here, unlike `003a`/`003b`/`003c` which
skipped it entirely (no new entity to document).

### Source Code (repository root)

```text
p0/qc_engine/
└── engine.py                 # MODIFIED:
                              #   - CheckResult gains `review_reason: Optional[str] = None`
                              #   - `_eval_check`: one small generic block immediately after the
                              #     main kind dispatch (before the confidence-gate block):
                              #       if res.phase == PHASE_QC and res.status in ("FAIL", "WARNING"):
                              #           res.review_reason = "EXCEPTION"
                              #       elif res.phase == PHASE_RECONCILE and res.status == "NEEDS_REVIEW":
                              #           res.review_reason = "SOURCE_INCOMPLETE"
                              #   - confidence-gate block: one line added,
                              #     `res.review_reason = "LOW_CONFIDENCE"`, alongside the existing
                              #     `res.status = "NEEDS_REVIEW"` downgrade
                              #   - RunResult gains two new properties:
                              #       review_reasons -> {r.review_reason for r in results if r.review_reason}
                              #       disposition -> "NEEDS_REVIEW" if review_reasons else "AUTO_CLEARED"

p0/tests/
└── test_loan_disposition.py  # NEW — US1/US2/US3 coverage
```

**Structure Decision**: Single generic tagging rule (`phase`+`status` → tag) inserted once, not
duplicated per check-kind. This was a genuine simplification found while planning (not in the spec's
own FR wording, which only required "populated at the site that determines status" without specifying
*how many* sites) — `EXCEPTION` and `SOURCE_INCOMPLETE` both reduce to one condition each on the
already-computed `phase`/`status` pair, rather than needing separate insertions at every one of
`_eval_check`'s four `kind` branches. This is *more* aligned with the open-vocabulary intent than
scattering per-kind insertions would have been: a future fifth `kind` that produces a QC-phase `FAIL`
is tagged `EXCEPTION` automatically, with zero new code, the moment it exists.

## Complexity Tracking

*No entries — the one named limitation (Constitution Check, Principle VII) is a scope boundary, not
a violation requiring justification.*

## Implementation Notes (post-hoc — what was actually built)

Implemented per `tasks.md` (T001–T019 complete). No amendments to the design — the single generic
`phase`+`status` tagging rule worked exactly as planned, three touch points total in `engine.py`
(the new `CheckResult.review_reason` field, the generic tagging block, one line in the confidence-gate
block) plus two new `RunResult` properties.

- **The determinism digest changed — deliberately, for the first time since `001a`.** Every prior
  spec (`001b` through `003c`) proudly held `8510a0a8b4b6996e047fc8534e094394ba72aae396305b0d2ecad3d6924634db`
  byte-identical; `004` is the first feature that legitimately extends `CheckResult`/`RunResult`'s
  serialized shape (`review_reason`, `disposition`, `review_reasons`), so the full digest necessarily
  changes too. This is not a regression — it's proven mechanically, not just by code inspection:
  `test_004_review_reason_fields_are_purely_additive` strips the 3 new keys from the current output
  and asserts the result reproduces the **exact** old baseline. The two pre-existing digest tests
  (`test_zero_regression_full_suite_after_envelope_generalization`,
  `test_zero_regression_after_002b_ruleset_extension`) now compare against that same stripped
  reconstruction — their original historical claims (about `001b` and `002b` specifically) remain
  true and unbroken, rather than being silently reworded to also (incorrectly) claim "unaffected by
  004." A new test, `test_full_digest_matches_new_baseline_after_004_disposition`, records the new
  live baseline **`a3f702c12969f7eb657471796c95e2a493d459c4c55663fa8fc18ac31e8c1d09`** — this is what
  `005` and everything after must now hold byte-identical, the same role `8510a0a8...` played before.
- **Result**: 11 new tests in `p0/tests/test_loan_disposition.py` (US1/US2/US3 + the equivalence
  proof) **[corrected 2026-07-26, spec audit — this note originally said "13 in the file... = 15
  new"; the file contains exactly 11 test functions and 115 + 11 + 2 = 128, so the suite total was
  right and the per-file arithmetic wrong]** + 2 new digest-related tests in `test_p0.py`
  (`test_004_review_reason_fields_are_purely_additive`,
  `test_full_digest_matches_new_baseline_after_004_disposition`) = 13 new, on top of the
  2 existing tests updated to use the stripped comparison. Suite total: **128 passed** (was 115).
  `verify_against_defects.py` still reports 25/25; `p0/harness.py`'s 1000-run bit-exact check passes
  against the new baseline.
- **`auto_cleared`/`disposition` equivalence (FR-006) held on the first run**, with no edge case
  found needing a fix — the generic tagging rule's conditions (`qc_failures`'s own status check,
  `needs_review`'s own status check) were derived directly from `auto_cleared`'s existing formula, so
  the two were equivalent by construction rather than by coincidence (as `data-model.md` predicted).
