# Data Model: Loan Disposition (Composition Layer)

Unlike `003a`/`003b`/`003c` (which hardened or proved already-existing evaluation branches with no
new entities), this feature genuinely introduces new shapes — the disposition and its reason tags are
what `006`/`007`/`008` will consume next. Documented here, not skipped, per plan.md's own rationale.

## Entities

### `CheckResult.review_reason` (extended, `p0/qc_engine/engine.py`)

| Field | Type | New? | Notes |
|---|---|---|---|
| `review_reason` | `Optional[str]` | **Yes** | `None` for `PASS`, `NOT_APPLICABLE`, and `FLAG` (FR-005 — a `FLAG` never gets a reason). Set to one of the initial vocabulary values (below) for `FAIL`/`WARNING` (QC phase) or `NEEDS_REVIEW` (either phase). |

**Population rule** (generic, not per-check-kind — see plan.md's Structure Decision):

```
if phase == QC and status in (FAIL, WARNING):
    review_reason = "EXCEPTION"
elif phase == RECONCILE and status == NEEDS_REVIEW:
    review_reason = "SOURCE_INCOMPLETE"
# confidence-gate downgrade (runs after, may overwrite a None with a
# reason on what was about to be a clean PASS in either phase):
if <confidence gate downgrades this result>:
    review_reason = "LOW_CONFIDENCE"
```

Note the confidence-gate line runs *after* the generic block and only fires on what was, a moment
earlier, a `PASS` (see `_eval_check`'s existing confidence-gate condition) — so it never collides
with the `EXCEPTION`/`SOURCE_INCOMPLETE` assignment above; a `FAIL`/`WARNING`/reconcile-`NEEDS_REVIEW`
result was never a `PASS` to begin with; low confidence never overwrites an already-set reason.

### Initial tag vocabulary (open, not closed — see spec.md US3/SC-004)

| Tag | Produced by | Meaning |
|---|---|---|
| `EXCEPTION` | Any `QC`-phase check (`predicate`, `ratio_threshold`) resolving `FAIL` or `WARNING` | A genuine compliance/policy defect — the loan's own data violates a rule. |
| `LOW_CONFIDENCE` | The existing confidence gate (ruling #8, `DEFAULT_CONFIDENCE_FLOOR`) downgrading what would otherwise be a `PASS` | Not a defect — the extraction backing this value isn't trusted enough to auto-clear on. |
| `SOURCE_INCOMPLETE` | A `RECONCILE`-phase check (`agree_categorical`, `agree_numeric`) where exactly one of doc/system is present | Not a defect — the comparison itself couldn't be made; more data is needed, not a judgment call. |

This table is the feature's *starting point*, not its ceiling. A future check-kind, gate, or archetype
introduces a new tag by setting `review_reason` at its own evaluation site — no change to the
aggregation logic below is required or permitted to be required (SC-004 tests this directly: a
never-seen-before tag value must surface correctly in `review_reasons` with zero aggregation-code
changes).

### `RunResult.review_reasons` (new property, `p0/qc_engine/engine.py`)

```python
@property
def review_reasons(self) -> Set[str]:
    return {r.review_reason for r in self.results if r.review_reason}
```

- **Type**: `Set[str]` — deduplicated by construction (US3 Scenario 2: the same tag from two checks
  surfaces once, not twice).
- **Multi-label**: a loan genuinely can carry more than one tag (US1 Scenario 5) — this is a set, not
  a single value, precedence chain, or ranked list. No tag is privileged over another at this layer;
  privileging (if a future consumer wants "show the most urgent concern first") is that consumer's
  concern, not this feature's.

### `RunResult.disposition` (new property, `p0/qc_engine/engine.py`)

```python
@property
def disposition(self) -> str:
    return "NEEDS_REVIEW" if self.review_reasons else "AUTO_CLEARED"
```

- **Type**: `Literal["AUTO_CLEARED", "NEEDS_REVIEW"]` (Python 3.9-compatible: a plain `str`, not a
  `typing.Literal`-enforced type, matching how `CheckResult.status` itself is already a plain `str`,
  not an enum — consistency with the existing codebase's own convention, not a new one introduced
  here).
- **Equivalence invariant (FR-006, SC-003)**: `auto_cleared is True` **iff**
  `disposition == "AUTO_CLEARED"`. This holds by construction: `review_reasons` is non-empty exactly
  when some `CheckResult` has `status in (FAIL, WARNING)` at `QC` phase (member of `qc_failures`) or
  `status == NEEDS_REVIEW` at any phase (member of `needs_review`) — the same two conditions
  `auto_cleared`'s own formula (`not qc_failures and not needs_review`) already tests. No new
  condition is introduced that could cause the two values to disagree.

## Relationships

```
CanonicalLoan ──run()──> RunResult ──.results[]──> CheckResult (gains .review_reason)
                              │
                              ├─.review_reasons  (NEW: set-union over .results[].review_reason)
                              └─.disposition     (NEW: binary derivation from .review_reasons)
                              │
                              └─.auto_cleared    (EXISTING, unchanged — provably ⟺ disposition)
```

No changes to `CanonicalLoan`, `SourceValue`, `DocCitation`, `Check`, or `Ruleset` — this feature is
entirely a `CheckResult`/`RunResult`-scoped addition.

## State transitions

None. `Disposition` is a pure, stateless derivation computed fresh on every `run()` call — there is no
persisted disposition that transitions between states over time (that would be a workflow/audit-trail
concern, `007`'s territory, not this feature's).
