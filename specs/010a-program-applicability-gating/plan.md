# Implementation Plan: Program Applicability Gating

**Branch**: `010a-program-applicability-gating` | **Date**: 2026-07-20 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/010a-program-applicability-gating/spec.md`

## Summary

Unlike `003c` (pure proof, zero engine change), this feature makes a real, additive code change:
parse each real workbook row's Exception Code prefix into a program tag (`O-FHA-`→FHA, `O-VA-`→VA,
`O-RHS-`→USDA, `O-FRD-`→Freddie Mac, `O-FNM-`→Fannie Mae — the primary signal, 79% of real rows),
supplement it with the existing SQL WHERE-clause parsing where present (secondary signal, 615 rows),
attach the result to the compiled check as new applicability metadata, and gate a ruleset build for a
given loan against its own `loan_type`. Also fixes a small, separately-found bug: `taxonomy.py`
currently reads only the first sheet of each workbook file. This is the automated generalization of
`ruleset_defects.py`'s hand-derived `_check_applies`/`_PROGRAM_GATED` gating — same outcome, derived
from data instead of authored by hand, at real-workbook scale (~6,349 taggable rows vs. 4 hand-gated
checks today).

## Technical Context

**Language/Version**: Python 3.9-compatible (project-wide constraint).
**Primary Dependencies**: None new. Touches `p0/eval_synth/taxonomy.py` (fix: read every sheet, not
just `sheetnames[0]`), `p0/qc_engine/compiler/compile_llm.py` (new: parse Exception Code prefix +
SQL clause into applicability metadata on `CompiledCheckDraft`), and a new small gating module
(mirrors `p0/fixtures/ruleset_defects.py`'s `_check_applies` shape, generalized). No changes to
`engine.py`/`model.py`/`ruleset.py`/`reconcile.py`/`money.py` — this feature decides which checks
enter a `Ruleset` build, not how the engine evaluates them once included (the same "gating happens
before `run()`, not inside it" pattern `ruleset_defects.py`'s `defects_ruleset_for(loan)` already
establishes).
**Storage**: None new. The 5-entry prefix→program table and the SQL-clause field/value parser are
both pure code, not persisted config — same status as `ruleset_defects.py`'s existing
`_PROGRAM_GATED` dict.
**Testing**: New `p0/tests/test_program_applicability_gating.py` covering US1 (prefix→program
mapping, gated ruleset build correctness across all 5 programs), US2 (SQL-clause secondary
narrowing), US3 (both-sheets row loading). Fixtures constructed from the real Exception Code/SQL
clause values captured in `output/RULE-PROGRAM-GATING-FINDINGS.md` — not invented text — the same
"anchor on the real sampled row" discipline `003c` applied to `reconcile-01`.
**Target Platform**: Local execution, same as all of `p0/` — no service; the one external call this
feature's *consumer* (the eventual real test run, out of this feature's scope) will make is a
Bedrock call in `002b`, already implemented and unaffected by this feature.
**Project Type**: Small, additive parsing + gating feature — a new pure-function module plus one
field added to an existing dataclass, plus a one-line fix to a loop bound (read all sheets).
**Performance Goals**: N/A — parsing runs once per compiled row at (LLM) compile time, not per-loan
at evaluation time; gating itself is an O(checks × loans) filter, the same shape
`defects_ruleset_for` already runs today at 21-check scale.
**Constraints**: FR-005 (the Fannie/Freddie ambiguity must be inspectable, never silently guessed)
and FR-004 (untagged rows fail open, not closed) are the two safety-shaped constraints — getting
either wrong either open-gates a genuine mismatch (buyback risk, wrong direction) or silently
suppresses a check that should have applied (false-clear risk, the SAFE-gate direction this project
treats as the worse failure). Zero regression against `ruleset_defects.py`'s 21 hand-gated checks,
which this feature does not touch (spec.md FR-008).
**Scale/Scope**: The 5 confirmed program prefixes and the 5 confirmed SQL-clause field/value sets
(spec.md Assumptions) — not an open-ended parser for hypothetical future prefixes/values not yet
observed in the real data. Extending either table is a small, explicitly-named future change, not
assumed handled generically now.

## Constitution Check

*GATE: evaluated against `.specify/memory/constitution.md` v1.1.1.*

| Principle | Status | Note |
|---|---|---|
| I — Determinism of the correct computation | ✅ PASS | Prefix/clause parsing and the gating decision are pure string/data operations on already-extracted text — no float, no wall-clock, no network, no LLM at gating time. |
| II — Compile, then run | ✅ PASS | This feature only decides *which* compiled checks enter a ruleset build — it adds no runtime LLM call anywhere, and it operates on `002b`'s already-compiled output, not on raw rule text at evaluation time. |
| III — Eval is foundational | ✅ PASS | SC-001–005 make correctness, the ambiguity-surfacing requirement, and the honest scope boundaries (21%-untagged fail-open, no Jumbo tag found) explicit, testable gates — not asserted by inspection alone. |
| IV — Build the core, assume the periphery | ✅ PASS | This closes Known Blocker #3 ("assume all rules apply for now") — a core scoping gap the roadmap named from the start, not a peripheral concern. |
| V — Source independence | N/A this feature | Gating decides *whether* a check runs, not how doc-vs-system comparison works — untouched. |
| VI — Configurable by non-technical users | ⚠️ PASS, with a named limitation | The prefix→program and SQL-clause value tables are Python data, inspectable and small (5 entries each), but not yet SME-editable config the way `field_catalog.json` is — same honest boundary `004`'s plan.md named for its own tag vocabulary. A future `009a` surfacing of parsed gates at import time is the real fix; not built here. |
| VII — Configuration is authored data | ✅ PASS | The applicability metadata this feature attaches to a `CompiledCheckDraft` is derived from the real workbook's own authored content (the Exception Code, the SQL clause) — not invented judgment; the SME still signs off on the compiled check that carries it. |

**One named limitation (Principle VI), not a violation** — mirrors `004`'s own Constitution Check
entry for the same reason: the mechanism is real and correct; the *editability* of its small lookup
tables by a non-technical SME is a distinct, deferred concern (`009a`'s eventual job), named here as
a scope boundary rather than smoothed over.

## Project Structure

### Documentation (this feature)

```text
specs/010a-program-applicability-gating/
├── spec.md
├── plan.md                  # This file
└── tasks.md                 # Phase 2 output
```

No `data-model.md` — the one new entity (`ExceptionCodePrefix → Program`, spec.md Key Entities) is a
5-row static table, not a schema warranting its own design document; documented directly in spec.md.

### Source Code (repository root)

```text
p0/eval_synth/
└── taxonomy.py                # MODIFIED: load_rows() reads every sheet in a workbook
                              #   (wb.worksheets, not wb[wb.sheetnames[0]]) — fixes the
                              #   previously-unread Private Bank "Pre Funding Nov 2025" sheet.

p0/qc_engine/compiler/
├── program_gating.py           # NEW: the 5-entry prefix→program table, the SQL-clause
                              #   field/value parser (property type / QC_Policy / LoanPurposeType /
                              #   LoanType / AddressState), and applies_to(loan, applicability) —
                              #   the automated generalization of ruleset_defects.py's
                              #   _check_applies, built from real-row metadata instead of by hand.
└── compile_llm.py             # MODIFIED: CompiledCheckDraft gains an `applicability` field,
                              #   populated by program_gating.py from the source row's own
                              #   Exception Code + SQL clause (if any) at compile time.

p0/tests/
└── test_program_applicability_gating.py   # NEW — US1/US2/US3 coverage, fixtures anchored on the
                              #   real prefix/clause values captured in
                              #   output/RULE-PROGRAM-GATING-FINDINGS.md.
```

**Structure Decision**: A new, small, dedicated module (`program_gating.py`) rather than folding
prefix/clause parsing directly into `compile_llm.py` — keeps the compiler's LLM-facing code
unchanged in shape (same precedent as keeping `catalog_screen.py`/`consistency.py`/`pattern_flags.py`
as separate single-purpose modules in `002b`) and makes the 5-entry mapping tables independently
testable and independently extensible (spec.md Assumptions: a 6th program tag is a small, isolated
addition here, not a change scattered across the compiler).

## Complexity Tracking

*No entries — the one named limitation (Constitution Check, Principle VI) is a scope boundary
mirroring `004`'s own precedent, not a violation requiring justification.*

## Implementation Notes (post-hoc — what was actually built)

Implemented per `tasks.md`, with real amendments beyond the original plan — unlike `003c`'s
proof-only pass, this feature's own build surfaced two corrections to its own spec, both disclosed
in `output/RULE-PROGRAM-GATING-FINDINGS.md`'s revision history rather than silently absorbed.

- **`program_gating.py`** built as planned: `parse_exception_code_prefix` (now handling two real
  formats — dash-delimited for 5 programs, space-delimited for SONYMA, found only while wiring real
  test fixtures), `parse_sql_gating_clause`, `Applicability`, `applies_to()`, and the `AMBIGUOUS`
  sentinel (raises `TypeError` if used as a bare bool — a deliberate guard against the Fannie/Freddie
  ambiguity being silently resolved by careless caller code).
- **`taxonomy.py`'s `load_rows()` required a bigger rewrite than planned.** Beyond reading every
  sheet (US3, as planned), a real per-questionnaire column-mapping bug was found: "Post-Closing
  Private Bank Oct 2025" (802 rows) exports every field from "Question Code" onward one column left
  of the shared header. Fixed by detecting the shifted questionnaire via `Questionnaire Name` (the
  one field guaranteed correctly positioned) and applying a separate column map (`_SHIFTED_COLS` vs.
  `_STANDARD_COLS`). Also now captures each row's own SQL gating clause (`sql_criteria`) — a field
  `load_rows()` never returned before this feature, silently dropping the very data `program_gating.
  parse_sql_gating_clause` needs. Also fixed, found blocking a test run: `taxonomy.py`'s `main()`
  listed Excel's `~$`-prefixed lock/temp files as real workbooks (crashed with `BadZipFile` while
  Gordon had the source files open in Excel) — `sample.py` already excluded these; `taxonomy.py`
  did not.
- **`compile_llm.py`**: `CompiledCheckDraft` gained the `applicability` field; `compile_row()` now
  populates it from `row["exception_code"]`/`row["sql_criteria"]` via `program_gating` — no LLM call
  involved in this parsing, same "compile, then run" discretion Principle II requires.
- **Two rounds of self-correction, both disclosed**: the exception-code-prefix table grew from 5
  programs to 6 (SONYMA, added per Gordon's explicit direction though untested against a real
  fixture); the real total row count grew from 8,021 to 8,442 once the shifted questionnaire was
  read correctly; the originally-reported "615 standalone SQL-gating rows" turned out to be an
  artifact of that same column-shift bug, not a real row category (`sql_gating_rows_excluded` → 0
  after the fix).
- **Test count**: 16 new tests in `p0/tests/test_program_applicability_gating.py` (grew from the
  originally-planned ~13 across tasks.md — added mid-build: the SONYMA space-delimited-format test,
  the SONYMA-against-5-loans untested-but-verified-excluded test, and the shifted-schema correction
  test). Suite total: **144 passed** (was 128). `p0/harness.py`'s 1,000-run digest unchanged
  (`a3f702c12969f7eb657471796c95e2a493d459c4c55663fa8fc18ac31e8c1d09`) — zero regression, confirmed
  directly since this feature touches no `engine.py`/`model.py`/`ruleset.py` code.
  `verify_against_defects.py` still 25/25.
- **`engine.py`/`model.py`/`ruleset.py`/`reconcile.py` confirmed untouched** — this feature only
  added `program_gating.py`, extended `compile_llm.py`'s dataclass, and fixed `taxonomy.py`'s row
  loading, exactly as planned in Project Structure.
