# Implementation Plan: Synthetic Loan Fixture Generation (Document-Derived, Dev-Mode)

**Branch**: `000-synthetic-fixture-generation` | **Date**: 2026-07-15 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/000-synthetic-fixture-generation/spec.md`

## Summary

Turn the 5 synthetic loan packages in `demo/syn/loan 0{1-5}/` (33 PDF documents + 5 MISMO exports —
38 files total, verified by direct count 2026-07-15 — each loan carrying 5 pre-documented defects) into `CanonicalLoan`/`SourceValue`-shaped JSON fixtures — the
engine's already-pinned contract (`001a`/`001b`), not a new shape. Extraction is deterministic
(`pdftotext` + per-document-type patterns for PDFs, the existing `qc_engine/mismo.py` for XML), the
field catalog is extended only where a real rule condition (`p0/eval_synth/taxonomy.json`) justifies
it, and no fixture is considered trustworthy until it reproduces all 25 embedded, pre-documented
defects exactly. This is dev/test tooling — mirroring `p0/eval_synth`'s existing convention — not the
Touchless production extractor (Principle IV).

## Technical Context

**Language/Version**: Python 3.9-compatible (project-wide constraint).
**Primary Dependencies**: `pdftotext` (poppler-utils, already available in this environment) invoked
as a subprocess for deterministic PDF text extraction; stdlib `xml.etree.ElementTree` via the
existing `qc_engine/mismo.py` for MISMO parsing; stdlib `re`/`json` for pattern matching and fixture
serialization. No new third-party Python packages. An LLM call (Bedrock, `temperature=0`) is
permitted only as a last-resort fallback when deterministic pattern matching cannot resolve a field —
never the primary path, and never at runtime after fixtures are generated.
**Storage**: Flat files only — the source PDFs/XML already in `demo/syn/`, and the generated
`CanonicalLoan` JSON fixtures written under `p0/fixtures/from_docs/`. No database.
**Testing**: `pytest`, extending `p0/tests/`. The feature's own acceptance gate is the 25/25
defect-reproduction check (`verify_against_defects.py`), which functions as an executable test, not
just documentation.
**Target Platform**: Local execution / CI, same as all of `p0/` — a one-time offline batch script,
never a deployed service, no network dependency on its primary path.
**Project Type**: Library-style addition to the existing `p0/` package (new `p0/fixtures/from_docs/`
subpackage), following the precedent of `p0/eval_synth/` and `p0/fixtures/golden.py`.
**Performance Goals**: N/A — a one-time batch over 38 source files; correctness dominates, not speed.
**Constraints**: Byte-deterministic (same source files → same output JSON, every run, on every
machine — mirrors Principle I's spirit even though this sits outside the engine itself); zero new
third-party dependency on the primary extraction path; must not be described or wired as the
Touchless production extractor (Principle IV).
**Scale/Scope**: Fixed and small by design — 5 loans, 38 source files (33 PDFs + 5 MISMO exports),
~33 catalog fields
(7 existing + ~26 new), 25 known defects to reproduce exactly. Not an attempt to build a
general-purpose document extractor for arbitrary lender files.

## Constitution Check

*GATE: evaluated against `.specify/memory/constitution.md` v1.1.1.*

| Principle | Status | Note |
|---|---|---|
| I — Determinism of the *correct* computation | ✅ PASS | The extraction script itself must be byte-deterministic (same source docs → same JSON, every run) — the primary path is pure text parsing + pattern matching, no model, no wall-clock. The one permitted LLM fallback runs at `temperature=0`, offline, and its output is still gated by the 25/25 defect check before any fixture is trusted — an unreliable fallback fails the gate rather than silently passing. |
| II — Compile, then run | ✅ PASS / N/A | Not a ruleset compiler, but the same shape: fixtures are generated once, offline (dev-mode), and verified before use — never regenerated or reinterpreted at runtime. No LLM freelances against a live loan. |
| III — Eval is foundational | ✅ PASS | This feature *is* eval infrastructure — it extends "ground truth by construction" (already the project's answer to Blocker 2) one layer earlier, from engine verdicts to extraction itself. The 25 embedded defects are the constructed labels; SC-001 makes zero-tolerance for a missed defect an explicit, executable gate. |
| IV — Build the core, assume the periphery | ⚠️ PASS, tension explicitly surfaced | Generating fixtures from documents looks adjacent to "build document extraction," which Principle IV forbids. Resolution (spec.md Assumptions, FR-003/FR-010): this is throwaway dev/test tooling operating over 5 already-available synthetic loans — the same category as `p0/eval_synth`, not the Touchless extractor, and it is not presented, documented, or wired as such. No claim is made about real-lender/real-document extraction accuracy (spec.md footer note). |
| V — Source independence | ✅ PASS, one gap flagged not silently resolved | Doc-vs-system fields (e.g. `fha_case_number` vs. the FHAC portal) follow the existing `truth`/`sources` shape untouched. Several real defects are doc-vs-**doc** (1003 vs. VOE, 1003 vs. title commitment) — today's model doesn't cover this. FR-007 requires this be modeled as two independent, separately-cited catalog fields rather than forced into `sources{}`, and the actual comparison mechanism is explicitly deferred to whoever specifies `003c` (reconcile checks) — a real gap, surfaced, not papered over. |
| VI — Configurable by non-technical users | N/A this feature | No authoring-surface change; this is a dev-mode data-generation script, not a Routes/Blocks/Checks change. |
| VII — Configuration is authored data | ✅ PASS | The field-catalog extension (`001a`'s artifact) rides entirely on `001a`'s existing authored-data mechanics (referential integrity, uniqueness, versioning) — FR-009/FR-004(001a) — no new governance invented here. |

**No unjustified violations. Complexity Tracking is empty — this feature adds one new subpackage
(`p0/fixtures/from_docs/`) at the same architectural layer as the existing `p0/eval_synth/` and
`p0/fixtures/golden.py`, not a new layer.**

## Project Structure

### Documentation (this feature)

```text
specs/000-synthetic-fixture-generation/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md         # Phase 1 output
├── contracts/            # Phase 1 output
│   └── defect-verification-manifest.md
└── tasks.md              # Phase 2 output (/speckit.tasks — not created by this command)
```

### Source Code (repository root)

```text
p0/
├── qc_engine/
│   ├── field_catalog.json      # EXTENDED (existing 7 fields + ~26 rule-grounded new fields)
│   └── mismo.py                # EXTENDED (field list only) — reused, not rewritten
├── fixtures/
│   ├── golden.py                # UNCHANGED — existing hand-authored fixtures remain
│   └── from_docs/                # NEW — this feature
│       ├── doc_patterns/         # per-document-type extraction patterns (data, not code-per-doc)
│       │   ├── urla_1003.yaml
│       │   ├── voe.yaml
│       │   ├── credit_report.yaml
│       │   ├── appraisal_1004.yaml
│       │   ├── title_commitment.yaml
│       │   ├── closing_disclosure.yaml
│       │   ├── fha_docs.yaml
│       │   ├── va_docs.yaml
│       │   └── usda_docs.yaml
│       ├── extract_pdf.py        # pdftotext + pattern application, deterministic
│       ├── extract_xml.py        # thin wrapper over qc_engine/mismo.py
│       ├── build_fixtures.py     # assembles 5 CanonicalLoan JSON fixtures
│       ├── defect_manifest.json  # the 25 known defects, machine-readable (contracts/ shape)
│       ├── verify_against_defects.py   # the 25/25 hard gate
│       └── README.md             # dev-only / not-Touchless label (Principle IV)
└── tests/
    └── test_fixture_generation.py   # pytest coverage for extract_pdf/extract_xml/build_fixtures/verify
```

**Structure Decision**: Single project (Option 1) — a new subpackage inside the existing `p0/`
package, at the same layer as `p0/eval_synth/` and `p0/fixtures/golden.py`. No frontend/backend split;
this has no UI and no service surface.

## Complexity Tracking

*No violations to justify — table intentionally empty.*

## Implementation Notes (post-hoc, added during a `/speckit-plan` re-verification pass, 2026-07-15)

All 28 tasks in `tasks.md` are marked complete. Re-verified against actual disk state (not just
checkboxes) before accepting that:

- `p0/fixtures/from_docs/` exists as specified, with 5 fixture JSON files, `defect_manifest.json`
  (25 entries), `verify_against_defects.py`, and 13 `doc_patterns/*.json` files (15 on disk after T032 added `paystub.json` + `disclosure_package_index.json` — count never updated; noted 2026-07-26, spec audit) (JSON, not the YAML
  named in this plan's original Project Structure sketch — a reasonable implementation deviation,
  not a defect).
- `field_catalog.json` grew from 7 to 39 entries (7 existing + 32 new — slightly more than
  research.md's ~26 estimate; every new entry's `description` cites a `taxonomy.json` archetype id).
- `qc_engine/mismo.py` grew from 100 to 115 lines, extending the field list only, as planned.
- `python3 p0/fixtures/from_docs/verify_against_defects.py` → **25/25 matched**.
- `python3 -m pytest p0/tests/ p0/eval_synth/test_properties.py -q` → **91 passed**.
- `python3 p0/harness.py` → bit-exact digest unchanged, zero regression against the P0 golden set.

**One real defect was found and fixed during this reconciliation, not just documented**: 8 of the 13
new boolean-typed catalog fields (`large_deposit_source_documented`, `hud92900a_certification_signed`,
`gift_funds_source_documented`, `lead_paint_completion_cert_present`,
`self_employed_pl_balance_sheet_present`, `usda_property_eligibility_documented`,
`well_septic_test_documented`, `termite_inspection_present`) were populated with the **literal string
`"false"`** instead of a real Python/JSON `False`, in `extract_pdf.py`'s
`boolean_false_if_found` path. `field_catalog.json` declares `data_type: "boolean"` for all of these —
a string value violates that contract, and — more seriously — a non-empty string is **truthy** in
Python, so any future `if sv.truth:` consumer would silently read a documented-absent/false field as
present/true. `verify_against_defects.py`'s original comparison (`str(actual).lower() == "false"`)
masked this by string-matching rather than requiring the real type, exactly the "scorer that can't
fail on a bad label is just confirming itself" trap `g-learn-ground-truth-by-construction` warns
against — the reported `25/25` was real in aggregate but was passing through a comparison that
couldn't have caught this specific defect.

**Fix applied**: `extract_pdf.py`'s `boolean_false_if_found` branch now returns a real `False`;
`verify_against_defects.py`'s `missing`-relationship check now requires `actual is False` (rejecting
a string) rather than a loose stringified comparison. Fixtures were regenerated
(`build_fixtures.py`), reconfirmed byte-deterministic across repeated runs, and re-verified at
**25/25 matched** with genuine `bool` types (`type(actual).__name__ == "bool"` for all 8, confirmed
directly, not inferred). Full suite and harness re-run clean after the fix (91 passed, digest
unchanged). No other string-typed stand-ins for `boolean`/`decimal`/`date` fields were found across
all 5 fixtures (checked directly, not sampled).

**T039, added post-implementation (2026-07-16) — wiring extracted fields into real engine checks**:
Gordon asked to "start wiring the new fields into actual checks" — connecting the now-375-entry field
catalog to actual `Check` objects producing real PASS/FAIL verdicts, not just sitting as inert
extracted data. Categorized all 25 known defects in `defect_manifest.json` by which check-kind they
need: 13 are pure presence/absence (`predicate`, kind already built by 003a), 4 are single-field
numeric floors/ceilings (`ratio_threshold` mode `field_value`, already built by 003b — one manifest
entry, the USDA PITI/DTI defect, names two independently checkable fields, so 5 `Check` objects come
from these 4 defects), 2 are date-order/date-age conditions needing a derived day-gap field (still
`ratio_threshold field_value` once derived — no new engine code), and 1 is a genuine doc-vs-system
mismatch (`fha_case_number_1003` vs its own `sources["mismo"]`) that the EXISTING `agree_categorical`
reconcile check-kind already handles verbatim (the field already carries a populated mismo slot from
T-prior work). The remaining 5 are genuine doc-vs-doc comparisons (two independently-extracted
document fields, e.g. `title_vesting_1003` vs `title_vesting_commitment`) with no check-kind built yet
— explicitly out of scope per spec 000's own research.md decision #4, deferred to whoever specifies
003c or a new doc-vs-doc kind. Not freelanced.

Built:
- `build_fixtures.py`: `_derive_date_diff_fields()` computes 2 new fields (`appraisal_staleness_days`,
  `nov_days_after_closing`) from already-resolved doc-truth date pairs (`appraisal_effective_date`/
  `closing_date`, `notice_of_value_date`/`closing_date`) — landed in `fields{}`, not `facts{}`, since
  `ratio_threshold`'s `field_value` mode reads `loan.get(field_name)` (the fields path), not
  `loan.facts`. No citation attached (computed from 2 documents, no single page/segment to cite) — a
  new `DERIVED_FIELD_NAMES` constant lets the 2 pre-existing citation-completeness tests exclude them
  by name rather than relaxing "truth implies citation" for every field.
- 2 new `field_catalog.json` entries for the derived fields (377 total, up from 375) — `expected_sources:
  ["doc"]`, `citation_required: false`, grounded by cross-reference to the taxonomy citations
  `appraisal_effective_date`/`notice_of_value_date` already carried (those entries already anticipated
  this exact derived-day-gap need in their own description text, written in an earlier round).
- **`p0/fixtures/ruleset_defects.py`** (new file, deliberately separate from `ruleset_demo.py` — that
  one's exact content is pinned in `harness.py`'s 1000-run zero-regression digest and must never be
  touched): 21 `Check` objects covering the 20 wirable defects, using only already-implemented kinds.
- Verified empirically, not assumed, that none of the new checks false-positive across the other 4
  loans: every single-field/derived-field check resolves `NOT_APPLICABLE` (not a spurious FAIL or
  PASS) on loans where the field/program doesn't apply — except `appraisal_staleness_days`, which
  loan01 also populates (a genuine 25-day gap, well under the 120-day limit) — a real PASS, not N/A,
  confirmed and asserted explicitly.
- Confirmed `chk-def-fha-case-number`'s verdict is `FLAG`, not `FAIL` — `engine.py`'s own
  RECONCILE-phase design treats doc-vs-system disagreement as informational (the closing doc is
  truth; QC runs against it regardless of system sync), correct pre-existing behavior surfaced by this
  check for the first time, not a defect in this task's wiring.
- 3 new tests in `test_fixture_generation.py`: referential integrity of the new ruleset against the
  catalog, all 20 wirable defects produce their correct verdict on the exact loan the manifest names,
  and the no-false-positive/NOT_APPLICABLE guarantee across the other 4 loans for every threshold
  check. 2 pre-existing citation-completeness tests updated to exclude `DERIVED_FIELD_NAMES`.

Zero regression: 25/25 defects, byte-identical fixtures, unchanged determinism digest
(`8510a0a8b4b6996e047fc8534e094394ba72aae396305b0d2ecad3d6924634db`), full suite now **103 passed**
(was 100).

**T040, added post-implementation (2026-07-16) — gating the 13 predicate checks by applicability**:
T039's own wiring surfaced a real product-quality gap: the 13 "missing document" predicate checks ran
unconditionally against all 5 loans, so e.g. loan 01 (Conventional) showed FAIL on "HUD-92900-A
signed," "USDA property eligibility documented," etc. — checks for programs it isn't. `is_true`'s
None-implies-FAIL is correct for the loan a check actually applies to (that's the whole point of the
MISSING archetype); the bug was applying every check to every loan regardless of relevance. This
reopens, narrowly, the scope Known Blocker #3 explicitly deferred ("assume all rules apply... don't
block the build on this") — done here only because Gordon asked to focus on exactly this, and only
for these 13 already-wired checks, not the full 800-rule/program mapping problem.

Investigated the 13 checks individually rather than assuming one uniform gate — they aren't
homogeneous:
- **7 are borrower/transaction conditions** (self-employment, a gift, an unexplained deposit, a
  program-specific inspection) — NOT tied to loan program (a self-employed VA borrower needs the same
  P&L check a self-employed Freddie-refi borrower does; program-gating these would be wrong, just
  coincidentally right for this 5-loan set). Gated by **document presence**: a new
  `_derive_document_presence_facts()` in `build_fixtures.py` checks the loan folder's own filenames
  (e.g. does `Bank_Statement`/`HUD_92900A`/`Gift_Letter` appear) and stores 7 booleans in `facts{}` —
  not `fields{}`, since these are routing metadata, never themselves a Check target, so they need no
  catalog entry or citation.
- **2 are property-age conditions** (both lead-paint checks) — gated by `year_built_appraisal` (already
  a real catalog field) < 1978, with a deliberately conservative default when that value is unknown:
  gate IN (apply the check), not out. Absence of contrary evidence should never silently clear a
  compliance check. Confirmed residual effect, not a bug: loans 02/04/05 have no year data at all, so
  both lead-paint checks fire for all three (loan 02's own labeled defect is only one of the two) —
  documented and asserted explicitly, not hidden.
- **4 have no PDF anywhere in any of the 5 loans** (`defect_manifest.json`'s own "note" field says so —
  MISMO's `InFileIndicator=false` is the only record) — document-presence gating can't work here (it
  would never resolve true even for the defect's own loan), so these fall back to loan `program`
  (`loan_type` string match). `arm_preloan_disclosure_present` is conceptually ARM-rate-specific, not
  VA-specific, but gated to VA here since that's this dataset's one ARM case and no rate-type field
  exists — flagged in-code as needing revisiting if a second ARM loan on a different program appears.

Implementation: `ruleset_defects.py` gained `defects_ruleset_for(loan) -> Ruleset`, the real evaluation
entrypoint — filters `defects_ruleset()`'s 21-check universe down to what applies to that specific
loan before calling `qc_engine.run()`. `defects_ruleset()` itself is kept as the unfiltered universe,
used only for referential-integrity validation. This is pure ruleset-assembly logic — zero changes to
`engine.py`, `model.py`, or the `Check`/`Ruleset` dataclasses; each loan effectively gets its own Route,
matching this product's own "point a route at a target set of checks" philosophy (CLAUDE.md) rather
than inventing new engine machinery.

Verified empirically (not assumed) across all 5 loans: loan 01 now shows exactly 1 of the 13 predicate
checks (its own large-deposit defect), down from all 13 firing unconditionally before this round; loan
04 shows 3 (self-employed + the 2 lead-paint residuals), down from 13. New test
`test_predicate_checks_are_gated_by_applicability_not_universal` locks in the exact expected-applicable
set per loan, including the documented lead-paint residual, so a future change to the conservative
default doesn't silently drift without a decision.

Zero regression: 25/25 defects, byte-identical fixtures, unchanged determinism digest
(`8510a0a8b4b6996e047fc8534e094394ba72aae396305b0d2ecad3d6924634db`), full suite now **104 passed**
(was 103).

**T038, added post-implementation (2026-07-16) — the last table: credit report inquiries**: Gordon
asked to keep expanding coverage, naming the credit report's inquiry table as an example (already
flagged as a known remaining gap in the prior round's own summary). 2 rows (Date/Bureau/Requesting
Party) — one is the borrower's own mortgage inquiry, the other is the Ally Bank auto inquiry, which
is itself part of the undisclosed-liability defect's paper trail (defect #4 — this inquiry record is
*why* the Ally Bank auto loan shows up on the credit report at all, corroborating
`liability_amount_credit_report`). Verified the regex against source text before wiring in (same
discipline as every prior round); no false positives against other date-bearing lines in the same
document. 6 new catalog fields (375 total, up from 369). Re-confirmed every other document across
all 5 loans is genuinely single-record — this appears to be the last repeating table in this dataset.
Zero regression: 25/25 defects, byte-identical fixtures, unchanged determinism digest, suite now 100
passed (was 99).

**T037, added post-implementation (2026-07-16) — checking loans 02-05 found 5 more tables, plus a
real page-break bug**: Gordon asked to check loans 02-05 specifically for the same class of untapped
bulk data T036 found on loan 01. A systematic per-document review found 5 more repeating-row tables
that had been sitting as single defect-narrow fields or unextracted entirely: loan 01's own 1003 has
an Assets table (Checking/Savings/401(k)) and a Liabilities table (Chase Sapphire/Capital One
Auto/Federal Direct Loans — notably *not* including the undisclosed Ally Bank line, consistent with
defect #4) that the earlier bulk-data round missed entirely; loan 02's FHA appraisal has a 3-row
MPR/Health & Safety Items table; loan 04's Mortgage Payment History has all 12 months' due/paid
dates and status (previously only an aggregate late-payment count); loan 04's Self-Employed Income
Documentation Index has an 8-row present-document checklist.

**Caught a real bug verifying the fix, not after shipping it**: `_extract_simple_table`'s row counter
reset to 0 at the start of every page. Loan 01's 1003 Assets table straddles a page break — pdftotext
inserted a page break right after "Checking" (page 1), with "Savings" and "401(k)" starting page 2 —
so the counter reset, "Savings" got assigned the SAME row index "01" that "Checking" already had, and
silently overwrote it. First build produced only 2 of the 3 asset rows, with "Checking" simply gone.
Fixed by making the counter persist across pages (the same latent risk existed in `_extract_bank_
ledger`, not yet triggered since that document happens to be single-page — fixed proactively there
too, so a future multi-page bank statement doesn't hit the identical bug). Added
`test_round4_tables_have_correct_row_counts_and_no_page_break_collisions`, which asserts
`asset_01_account_type == "Checking"` specifically — a regression here would silently show "Savings"
again.

108 more catalog fields (369 total, up from 261). Independent sanity check: the 1003's own 3
liabilities (excluding the deliberately-undisclosed Ally Bank one) sum to exactly $684.00/mo
(85+389+210) — matching the source document by hand-arithmetic, not just by trusting the regex.

Zero regression: 25/25 defects, byte-identical fixtures, unchanged determinism digest, suite now 99
passed (was 98).

**T036, added post-implementation (2026-07-16) — bulk line-item extraction (bank transactions,
credit trade lines, appraisal comparables)**: Gordon asked to extract the remaining bulk data
explicitly. The prior rounds stayed at aggregate/summary level by design (README's own stated
boundary); this round crosses it deliberately, on direct instruction.

The field-catalog schema (`001a`, governed, zero-regression-gated) only allows scalar
`data_type ∈ {string, decimal, date, boolean, enum}` — no array type. Rather than widen that pinned
enum, or collapse a table into one JSON-blob string field (losing per-row citations), each repeating
row is represented as its own set of indexed scalar fields (`bank_txn_03_debit_amount`,
`credit_tradeline_02_balance`, `appraisal_comp_02_distance_miles`, ...) — each independently cited to
its own table row, staying entirely within the existing schema.

Two new extraction primitives in `extract_pdf.py`: `_extract_simple_table()` (one regex match per
row via `re.finditer`, each named column its own capture group — used for credit trade lines and
appraisal comps, neither ambiguous) and `_extract_bank_ledger()` (the one genuinely hard case: a bank
statement's Credit and Debit columns are mutually exclusive per row, and no regex alone can tell
which one a lone captured amount belongs to — only its **character position** relative to the
header's own column offsets can, which is exactly what `pdftotext -layout` preserves and this reads).
Verified empirically before wiring in: header row gives `Credit` at column 79, `Debit` at column 92
in the actual PDF text; every transaction's dollar amount aligns to one or the other exactly.

Added a `"tables"` section (sibling to `"fields"`) to `bank_statement.json`/`credit_report.json`/
`appraisal_1004.json`, and 102 new catalog entries (261 total, up from 159) — derived from the actual
built fixture's field names, not predicted, since bank transaction field names depend on which
direction each row resolves to.

**The correctness proof that matters most here isn't spot-checking, it's an independent arithmetic
identity**: `beginning_balance + sum(credits) − sum(debits) = ending_balance`, to the penny
(`$18,240.00`), across all 16 extracted transactions. If even one row had been missed or
misclassified credit-vs-debit, this would not balance — added as
`test_bank_ledger_reconciles_to_the_penny`, a stronger guarantee than any individual value check.
Zero regression: 25/25 defects, byte-identical fixtures, unchanged determinism digest, suite now 98
passed (was 97).

**T035, added post-implementation (2026-07-16) — round-2 comprehensive coverage for the sparse
program-specific documents**: Gordon asked to keep expanding field coverage. A density review found
loan 01's documents (VOE, paystub, credit report, bank statement, title commitment, disclosure
index) had already gotten comprehensive treatment (79/80 fields populated), but loans 02-05's
program-specific documents (FHA Connection, Gift Letter, CAIVRS, VA COE, VA NOV, USDA GUS Findings,
USDA Property Eligibility, Payoff Statement, Self-Employed Income Index) still only carried their
original 1-2 defect-narrow fields each — real, substantive document content sitting unextracted.

Added 48 new fields (159 total, up from 111) across `fha_docs.json`, `va_docs.json`,
`usda_docs.json`, `payoff_statement.json`, `mortgage_payment_history.json`,
`self_employed_income_index.json`, `title_commitment.json`, and `closing_disclosure.json` — donor
identity/relationship/address for gift letters, CAIVRS screening codes and dates, VA COE
entitlement/service details, VA NOV case numbers and validity periods, USDA GUS recommendation and
income-limit detail, payoff statement escrow/fees/good-through-date, mortgage history report period,
title commitment's lender-side policy details, and closing-disclosure fields not yet captured
per-loan (disbursement date, loan term, loan type, seller concessions, UFMIP/MIP, VA funding fee on
the CD side, product, cash-to-borrower).

Field density jumped for the previously-sparse loans: loan 02 31→46, loan 03 28→41, loan 04 29→36,
loan 05 21→28 (loan 01 was already comprehensive: 71→79). All new values spot-checked directly
against source text before trusting them; correctly resolved `None` where a loan's specific document
genuinely lacks that line (e.g. loan 02's Closing Disclosure has no "Loan Term"/"Loan Type"/
"Disbursement Date" line at all — an honest absence, not an extraction miss). Zero dirty
`field_label`s or missing `document_title`s found across all 159 fields on a full sweep. Zero
regression: 25/25 defects, byte-identical fixtures, unchanged determinism digest, suite still 97
passed (no new tests needed — existing coverage tests already exercise the new fields' correctness
via the citation-quality and taxonomy-grounding sweeps, which check *every* catalog entry, not a
fixed list).

**T034, added post-implementation (2026-07-16) — property_value + facts{}**: Gordon asked to "pull
the doc-side truth into more of the seed fields." Audit found `property_value` had the exact same
gap `property_address` did (T033) — mismo-only truth, no doc pattern anywhere. Fixed by adding a
`property_value` field to all four appraisal-bearing pattern files (`appraisal_1004.json`,
`fha_docs.json`, `va_docs.json`, `usda_docs.json`), each reusing that document's own "Appraised
Value" regex — safe, since each loan's appraisal routes through exactly one of the four files.

A second, more consequential gap surfaced while checking `chk-ltv-max`: `engine.py`'s `ratio="ltv"`
branch reads `loan.facts`, an entirely separate data path from `loan.fields` that `build_fixtures.py`
had **always** left `{}` regardless of how complete `fields{}` was — so `chk-ltv-max` stayed
`NOT_APPLICABLE` on every document-derived loan no matter what got fixed in `fields`. Added
`_derive_facts()`: resolves `facts["loan_amount"]`/`facts["property_value"]` from the already-
extracted fields (doc truth preferred, mismo fallback, per Principle V) — no new extraction, purely
wiring already-resolved data into the path the LTV check actually reads. Sanity-checked against
loan 01's own answer key (states "LTV 80%"): `340000/425000 = 0.80` exactly.

**Two remaining seed fields cannot be fixed without new source documents** (flagging honestly, not
silently leaving undocumented): `flood_zone` (zero mentions of "flood" anywhere across all 38 source
documents — no flood-certification document exists in this loan set) and `note_signed` (no
promissory-note document exists in any of the 5 packages; the 1003's own signature block is a
*different* document's signature and would misrepresent the field if substituted). These are honest
absences of source data, not a pattern-writing gap — nothing left to "pull" without fabricating.

**Worth flagging, not a bug**: `chk-ltv-max` now correctly computes real LTVs, and `FAIL`s on loans
02/03/05 (97.7%/100%/101%) — but this is `demo_ruleset()` being a simplified single-program ruleset
with one hardcoded 95% cap, not an extraction defect. FHA/VA/USDA loans legitimately allow higher LTV
(VA/USDA routinely finance to 100%+ with guarantee/funding fees rolled in) — exactly the
rule-to-program gating CLAUDE.md's Blocker 3 already names as future work, surfacing here as
independent evidence the gap is real, not newly introduced. Zero regression: 25/25 defects,
byte-identical fixtures, unchanged determinism digest, suite now 97 passed (was 96).

**T033, added post-implementation (2026-07-16) — the original 7 seed fields' doc side**: Gordon
noticed `property_address`'s `truth` was `null` despite a clear address sitting in `sources.mismo`,
and asked why. Root cause: `extract_pdf.py` had never written a pattern for the 5 reconcilable
original seed fields (`property_address`, `note_rate`, `loan_amount`, `borrower_name`,
`borrower_ssn`) themselves — only for derivative/comprehensive fields under different names (e.g.
`property_address_appraisal`). `build_fixtures.py` already merges truth+sources per field name
correctly with zero changes needed; the gap was purely a missing pattern.

Added patterns for all 5 to `urla_1003.json`. Caught a real bug mid-fix: `borrower_name`'s "Borrower"
label alternative matched the substring "Borrower" inside the UNRELATED earlier line "Cash-Out to
Borrower                  $78,600" in loan 04's 1003, returning `"$78,600"` as the borrower's name.
Fixed by anchoring all three label alternatives (`Borrower Name`/`Name`/`Borrower`) to the start of a
line (`(?<=\n)[ \t]*`) rather than allowing a bare label word to match as the tail of an unrelated
phrase — the same fix applied to `borrower_ssn`.

This is more than a data-completeness fix — these 5 fields are exactly what the engine's
**already-built** `demo_ruleset()` checks (`chk-borrower-name`, `chk-note-rate`, `chk-principal`,
`chk-property-address`, `chk-borrower-ssn`) read. Running the 5 fixtures through `qc_engine.run()`
now produces genuine verdicts instead of blanket N/A: `chk-principal` correctly `FLAG`s on loans 02
and 05 (the 1003's stated loan amount includes UFMIP/GRH guarantee fees the system-side
`BaseLoanAmount` excludes — a real, legitimate reconciliation difference, not a bug).

**Known, adjacent, NOT fixed here** (flagging rather than silently leaving undocumented):
`chk-property-address`/`chk-borrower-ssn` resolve `NEEDS_REVIEW` for loans 02-05 because
`qc_engine/mismo.py`'s own address/SSN extraction (pre-existing, unrelated to this session's work)
doesn't populate those fields for those loans' MISMO exports — a separate, pre-existing `mismo.py`
gap, out of this fix's scope. `chk-note-signed` is `FAIL` on all 5 loans because none of the 5
synthetic packages include a promissory note document at all (confirmed by the file inventory — no
gap in extraction, there's genuinely nothing to extract). `chk-ltv-max`/`chk-flood-zone` stay
`NOT_APPLICABLE`: LTV needs `facts{}` (populated separately from `fields{}`), which
`build_fixtures.py` has always left empty, and no flood-certification document exists in this loan
set either. Zero regression: 25/25 defects, byte-identical fixtures, unchanged determinism digest,
suite still 95 passed (no new tests needed — existing coverage already exercises these fields).

**T032, added post-implementation (2026-07-16) — file-coverage audit**: Gordon asked directly: did we
extract from all the PDFs, is it comprehensive, does it align with the real rules questions? Audited
rather than asserted — wrote a filename-match sweep against every PDF in `demo/syn/loan 0{1-5}/` and
found 2 real documents with **zero** extraction coverage: `03_Paystub_Most_Recent.pdf` and
`05_Initial_Disclosure_Package_Index.pdf` (both loan 01). Checked the paystub gap's real-world
relevance directly against `demo/rules/PF and PC Sept 2025 AMQs - Retail.xlsx` (not assumed) — 43
distinct real conditions reference paystub content, confirming this wasn't a minor gap. Added
`paystub.json` and `disclosure_package_index.json`, plus 16 new catalog fields (111 total, up from
95). Caught and fixed two extraction bugs while verifying the new fields against source text: (1)
`employee_name_paystub` matched the document's own title line ("Employee Pay Statement") instead of
the data line, since both start with the word "Employee" — fixed by requiring the 2+-space
column-layout gap the title line doesn't have; (2) `field_label` for "Net Pay:" retained a trailing
colon because a single-pass `rstrip` on a fixed character set stopped at an intervening space before
reaching it — fixed by including whitespace in the same rstrip pass. Added
`test_every_real_loan_document_is_matched_by_a_doc_pattern` so 100% real-document coverage (32/32,
excluding only the answer-key meta-file) is a locked, machine-checked claim, not a one-time audit
result that could silently regress. Zero regression: 25/25 defects, unchanged determinism digest,
suite now 95 passed (was 94).

**T031, added post-implementation (2026-07-15) — richer citation metadata**: Gordon asked to include
"page number/section/titles/metadata for citation purposes" — `page_num` is nearly useless alone
since every source PDF here is a single page. Extended `qc_engine/model.py`'s `DocCitation` with
`document_title`/`section`/`field_label`, additive and optional. Deliberately made `to_dict()` only
emit the new keys when populated, specifically so `golden.py`'s hand-authored citations (which never
set them) serialize byte-identically to before — this was necessary, not incidental: the first
implementation emitted all three keys unconditionally and it changed `harness.py`'s determinism
digest, which is referenced as the "nothing has changed since 001a" baseline across 8 other spec
docs. Caught this via the full test suite before committing, redesigned to preserve the baseline
rather than bump a digest referenced that widely. `section` uses a corpus-specific heuristic (no
2+-space run = header, matching this dataset's consistent `Label  Value` layout) — documented as
such in README.md, not oversold as a general PDF-structure parser. Zero regression: 25/25 defects,
byte-identical fixtures, unchanged determinism digest, suite now 94 passed (was 93).

**T030, added post-implementation (2026-07-15) — comprehensive-coverage field expansion**: Gordon
asked for "the fields + the extracted data from the loan files, the actual data," pointed at
`examples/mortgage-qc/schemas/extraction/*.yaml` as the reference for extraction breadth. Read all
12 of its schemas plus every PDF in `demo/syn/` fresh, and added 56 new fields (95 total, up from
39) across every document type the 5 loans actually contain — a second, explicitly-distinct grounding
category from the original 32 rule-grounded fields (README.md's new "Comprehensive-coverage fields"
section has the full rationale). Caught and fixed a self-inflicted regex bug during spot-checking
(a greedy end-of-line capture swallowed a document's own `*** ... ***` annotation into the value for
one field/loan) before it shipped — tightened to stop at the first asterisk, verified clean across
all 5 loans. Updated `test_every_new_catalog_field_has_taxonomy_grounding_citation` (US3) to accept
either legitimate grounding category rather than weakening it to accept anything, and added
`test_comprehensive_coverage_fields_do_not_masquerade_as_rule_grounded` so the two categories can't
blur into each other. Zero regression maintained throughout (25/25 defects, byte-identical fixtures,
unchanged determinism digest, suite now 93 passed).

**T029, added post-implementation (2026-07-15)**: `quickstart.md` step 5 called for wiring the
fixtures into "`p0/eval_synth`/engine tests," but the only test that existed
(`test_fixtures_load_into_canonical_loan_and_score_with_zero_changes`, T014) proved compatibility
with `eval_synth`'s `score()` wrapper only, not the actual engine's own `qc_engine.run()` entry
point that `test_p0.py`'s golden-loan tests use. Added
`test_document_derived_loans_run_through_the_real_engine` to `test_p0.py` itself, running all 5
fixtures through `run()` alongside (not replacing) `golden_loans()`. Confirmed: no exceptions, a
well-formed result set, zero code changes to `run()`/`model.py`, and the pre-existing determinism
digest (`8510a0a8b4b6996e047fc8534e094394ba72aae396305b0d2ecad3d6924634db`) unchanged. As expected
(and stated in spec.md's Assumptions), most `demo_ruleset()` checks resolve N/A against these
fixtures — `extract_pdf.py` targeted the ~26 new defect-grounded fields, not the original 7 seed
fields' doc side, so there is nothing yet for `demo_ruleset()`'s existing checks to compare against
on these loans. Real coverage of the new fields is the `003c`/`003-series` engine work this feature
was never scoped to do (Principle IV boundary, restated). Suite now 92 passed (91 + 1).

## Implementation Notes (post-hoc — what was actually built)

Implemented per `tasks.md` (T001–T028, all 28 complete). `verify_against_defects.py` reaches
**25/25** on the real generated fixtures on the first full run against the as-built extractor —
no iteration cycle was needed against the real PDFs/MISMO once the field list and patterns were
worked out from a full read of all 33 PDFs + 5 MISMO XML files.

**Amendments discovered during implementation:**

1. **Two of the five MISMO XML files were invalid XML, unrelated to their intentional
   `<!-- DEFECT -->` content** — found before any code was written, by direct `ET.parse()` against
   all 5 files. `loan 01/09_Loan_Data_MISMO.xml`'s top-of-file explanatory comment illegally nested
   a literal `<!-- DEFECT -->` inside a real XML comment (reworded to remove the nesting, same
   information content). `loan 03/07_Loan_Data_MISMO.xml` had a genuinely mismatched tag
   (`<LoanIdentifier>...</LoanIdentifierType>`, missing the `</LoanIdentifier>` close) and a
   mismatched `DOCUMENT_SETS`/`DOCUMENT_SET` closing pair. Both are fixed in place (`demo/syn/` is
   gitignored — kept on disk, not tracked). These were accidental corruption in the fixture-authoring
   itself, not part of the intentional defect content, so fixing them is not "silently resolving a
   real defect" — all 5 files now parse cleanly and `qc_engine/mismo.py`'s original 7-field output is
   unchanged (verified before and after).
2. **32 new catalog fields, not the estimated ~26** — the real count once every one of the 25
   defects' field/compare_field pairs was worked out from the actual documents. `demo/syn/` holds 33
   PDFs + 5 MISMO exports (38 files total, not "38 PDFs" as originally written — see the plan.md/
   research.md/quickstart.md correction made before this phase began).
3. **`doc_patterns/*.json`, not `*.yaml` as originally planned.** PyYAML is not a dependency of this
   project (no `requirements.txt` declares it, and plan.md's own Primary Dependencies section already
   said "no new third-party Python packages" without listing a YAML library) — writing `.yaml` would
   have silently introduced one. Switched to JSON, following `001a`'s own precedent (its research.md
   chose JSON over YAML for the field catalog for the same reason: consistency with an all-JSON
   codebase, avoiding YAML's implicit type coercion). Same "data, not code" principle, different
   serialization.
4. **13 `doc_patterns/*.json` files, not 9** — `fha_docs`/`va_docs`/`usda_docs` bundle every
   program-specific document as planned; 4 more were needed for document types the plan didn't
   enumerate (`bank_statement`, `payoff_statement`, `mortgage_payment_history`,
   `self_employed_income_index`).
5. **`fha_case_number_1003`'s system side uses the existing `sources["mismo"]` slot, not a new
   `"fhac"` source name.** The first attempt (an `expected_sources: ["doc", "fhac"]` entry) broke 15
   existing tests: `qc_engine/catalog.py` pins `VALID_SOURCES = ("doc", "los", "mismo")` at load time
   (`001a`'s own zero-regression-gated validator — 001b generalized the *runtime* `SourceValue.sources`
   dict to an open map, but never widened this catalog-level vocabulary). Widening it would be exactly
   the kind of change to an already-implemented, zero-regression-gated feature that research.md
   decision #4 already ruled out of scope for a different reason (not relaxing 001b's guard) — the
   same reasoning applies here. Fixed by extracting the FHA Connection portal's case number from the
   MISMO XML's `Source="FHAC_Portal"`-attributed `LOAN_IDENTIFIER` entry into the *existing* `mismo`
   system-source slot instead (`qc_engine/mismo.py`'s only real extension this feature needed).
6. **`fixture_loader.py`** (not in the original file list) — a small loader reconstructing
   `CanonicalLoan`/`SourceValue`/`DocCitation` from a fixture JSON file, with zero changes to
   `model.py` itself (needed to make US1's "loads into the existing model" acceptance bar concretely
   testable, not just assumed).

**Zero regression confirmed**: full suite (`p0/tests/` including the 8 new
`test_fixture_generation.py` tests, `p0/eval_synth/test_properties.py`) — 91/91 passed (83 baseline +
8 new). `python3 p0/harness.py`'s 1000-run bit-exact digest is unchanged from its pre-feature value
(`8510a0a8...` — **corrected 2026-07-26, spec audit**: this note originally recorded the digest as
`fdab075f...`, a value that matches nothing anywhere in the repo; the real 001a-through-004-era
baseline, pinned in `p0/tests/test_p0.py` and cited consistently by every sibling document, is
`8510a0a8b4b6...`. Phantom value replaced, discrepancy disclosed rather than silently swapped),
confirming the catalog/mismo.py extensions altered nothing about the existing engine
behavior.
