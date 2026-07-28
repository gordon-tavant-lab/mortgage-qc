# Phase 1 Data Model: Ruleset Compiler Pipeline

**Feature**: `002b-ruleset-compiler-pipeline` | **Date**: 2026-07-02

All entities below are additive to `p0/qc_engine/ruleset.py` (`Check`, `RuleProvenance`, `Ruleset`)
and `p0/qc_engine/catalog.py` (`FieldCatalogEntry`, `FieldCatalog`) — per spec.md's explicit
constraint (FR-001/FR-004/FR-005), **no existing dataclass field changes shape**; new dataclasses
attach alongside them. Python 3.9-compatible throughout.

## 1. `CompiledCheckDraft` (User Story 1, FR-001)

The unit the map step of Decision 1 (research.md) produces, one per source workbook row.

```python
@dataclass
class CompiledCheckDraft:
    row_id: str                    # source workbook row reference
    check: Check                   # existing p0/qc_engine/ruleset.py dataclass, UNCHANGED shape
    source_text: str               # FR-011(a) — the original defect_text/rule text compiled from
    extracted_intent: str          # FR-011(b) — LLM's plain-English restatement (002a's
                                    #   `plain_english_restatement` field, generalized to production)
    proposed_field_entry: Optional[FieldCatalogEntry] = None  # Decision 2 — set only when
                                                                # check.field_name doesn't yet
                                                                # resolve against the 001a catalog
    parse_error: Optional[str] = None   # non-None => compile_llm.py's malformed-output path
                                          # (mirrors experiment_002a/compile_llm.py's `_parse_error`)
```

`check` and `proposed_field_entry` are literally instances of the existing `Check` and
`FieldCatalogEntry` dataclasses — this entity is a wrapper carrying provenance/intent alongside them,
not a new schema for either.

## 2. `RuleIntentRecord` (User Story 5, FR-011)

The permanent audit triple — added to `Ruleset` as a new list field, **not** included in
`canonical_content()` (so `Ruleset.sha256()` is unaffected; only the deterministic `Check` logic is
signed/hashed, per FR-011's closing sentence that the engine reads only the logic, never this
record).

```python
@dataclass
class RuleIntentRecord:
    check_id: str              # foreign key into Ruleset.checks (by Check.id)
    source_text: str           # FR-011(a)
    extracted_intent: str      # FR-011(b)
    # (c), the deterministic logic, is Ruleset.checks[i] itself — not duplicated here.

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
```

`Ruleset` gains one new field:

```python
@dataclass
class Ruleset:
    ...  # existing fields unchanged
    intent_records: List[RuleIntentRecord] = field(default_factory=list)   # NEW, additive

    def intent_for(self, check_id: str) -> Optional[RuleIntentRecord]:     # NEW method
        return next((r for r in self.intent_records if r.check_id == check_id), None)
```

`to_json()`/`from_dict()` extend to persist/restore `intent_records`, exactly mirroring the existing
`provenance` list's persistence pattern — same mechanism, second list. `canonical_content()` is
**not** touched (still only `ruleset_id`/`version`/`engine_version`/`checks`), so every existing hash
in `001a`/`001b`'s test suite remains byte-identical; this is additive-only.

## 3. `ConsistencyReport` (FR-003)

The reduce-step output (research.md Decision 1 + 3) — cross-batch duplicate-vocabulary detection.

```python
@dataclass
class DuplicateVocabularyFlag:
    field_name_a: str
    field_name_b: str
    edit_distance: int          # via ruleset.py's existing _edit_distance — no new dependency
    check_ids: List[str]        # the drafts referencing each candidate name

@dataclass
class ConsistencyReport:
    batch_id: str
    duplicate_flags: List[DuplicateVocabularyFlag] = field(default_factory=list)
```

Advisory only (spec.md Edge Cases: this does not block sign-off; only an unresolved reference does,
per User Story 3).

## 4. `PatternFlag` (User Story 4, FR-007/FR-008)

Deterministic heuristic classification over `source_text` — **not a second LLM call** (keeps
compile-time cost and Principle I/II's determinism story unchanged; this is regex/keyword
classification, the same style already proven in `p0/eval_synth/taxonomy.py`'s `ARCHETYPES`
pattern-matching).

```python
@dataclass
class PatternFlag:
    check_id: str
    flag_type: str        # "opaque_boolean_risk" (FR-007, the predicate-08 pattern) |
                           # "archetype_mismatch_risk" (FR-008, the reconcile-00/01 pattern)
    reason: str            # human-readable explanation, cites the matched heuristic
```

**FR-007 heuristic** (`opaque_boolean_risk`): fires when `check.kind == "predicate"` and
`source_text` matches a two-value-comparison pattern (e.g. `r"greater of|lesser of|higher of|lower
of|compare[ds]?\s+to|whichever is"`) — the `predicate-08` pattern (`002a` RESULTS.md) found exactly
this shape ("use the greater of fully indexed rate/introductory rate").

**FR-008 heuristic** (`archetype_mismatch_risk`): fires when `check.kind` is
`agree_categorical`/`agree_numeric` and `source_text` does **not** match a genuine two-independent-
source comparison pattern (e.g. lacks `r"does not match|differs from|discrepancy between|disagrees
with"` alongside two distinguishable source references) — the `reconcile-00`/`reconcile-01` pattern
(policy/compliance conditions like "was X investigated" mis-classified as a reconcile archetype).
Both heuristics are advisory (route to human attention, per spec.md Edge Cases — never a hard block).

## 5. Referential-integrity batch screen (User Story 3, FR-002 — research.md Decision 4)

Not a new dataclass — a function that wraps the existing, unmodified
`catalog.validate_referential_integrity`:

```python
def screen_batch_referential_integrity(
    drafts: List[CompiledCheckDraft], catalog: FieldCatalog
) -> Dict[str, Optional[str]]:
    """check_id -> None (resolves) | error message (blocked). Calls the existing
    validate_referential_integrity once per candidate check (a throwaway single-check
    Ruleset per call) rather than modifying its raise-on-first-error contract."""
```

A draft whose `field_name` doesn't resolve is **not itself an error** in this feature if it carries a
`proposed_field_entry` (Decision 2) — it is `signable pending catalog-entry sign-off`, distinct from
`blocked` (no proposal, or the LLM couldn't infer one). This distinction is surfaced in the batch
report, not silently collapsed into a single "blocked" bucket.

## 6. `CompiledRuleset` (spec.md Key Entities)

Not a new dataclass — the existing `Ruleset` (now carrying `intent_records`, item 2 above), populated
from a batch of `CompiledCheckDraft.check` + `RuleProvenance` (existing, per drafted check) +
`RuleIntentRecord` (new, per drafted check). `Ruleset.sha256()`, `unedited_rules()`,
`signoff_summary()` are used unmodified — FR-006's batch-scale sign-off-theater flag is
`signoff_summary()` called on a `Ruleset` with dozens-to-hundreds of `provenance` entries instead of
8; no code change is needed for this to work at scale, since the method already iterates
`self.provenance` generically.

## Entity relationship summary

```
SampledWorkbookRow (existing, p0/experiment_002a/sample_rows.py pattern, generalized)
   |
   v  [map: compile_llm.py, one row per call]
CompiledCheckDraft { check, source_text, extracted_intent, proposed_field_entry? }
   |
   +--> [reduce: consistency.py]  ConsistencyReport (batch-wide)
   +--> [reduce: pattern_flags.py] PatternFlag* (per draft)
   +--> [pre-sign gate: screen_batch_referential_integrity]  per-check resolved/proposed/blocked
   |
   v  [SME sign-off, per draft + per proposed_field_entry]
Ruleset { checks, provenance, intent_records }  +  FieldCatalog (grown by signed proposals)
```
