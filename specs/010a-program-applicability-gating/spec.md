# Feature Specification: Program Applicability Gating

**Feature Branch**: `010a-program-applicability-gating`
**Created**: 2026-07-20
**Status**: Implemented (2026-07-26, commit `0741905` — 8,442 rows, column-shift fix, SONYMA; header corrected from stale "Draft" 2026-07-27, spec adversarial audit)
**Input**: User description: "010a-program-applicability-gating — parse the real AMQ workbook's
own machine-readable program signals (the Exception Code prefix, primary; the existing SQL gating
clauses, secondary) so a compiled check fires only for the loan program/situation it actually
applies to, replacing the hand-derived, non-scaling gating built once by hand for the 21-check demo
ruleset. Renamed from the roadmap's original `010a-honor-encoded-sql-gating` after direct inspection
of `demo/rules/*.xlsx` found the SQL-clause mechanism is real but secondary, not primary — see
`output/RULE-PROGRAM-GATING-FINDINGS.md` for the full evidence this spec is built on."

**Governs**: `output/ROADMAP.md` §010a, `output/RULE-PROGRAM-GATING-FINDINGS.md` (the evidence this
spec formalizes), `.specify/memory/constitution.md` Principle IV (build the core, assume the
periphery — this closes the "we don't want to run all 800 for every loan" gap named as Blocker 3),
Known Blocker #3 ("assume all rules apply for now" — this is the sanctioned mitigation's expiration).

**Post-hoc correction (2026-07-20, same day as initial spec — disclosed, not silently rewritten)**:
implementation surfaced two errors in this spec's original evidence, both corrected in
`output/RULE-PROGRAM-GATING-FINDINGS.md`'s revision history:
1. The primary Exception Code prefix table grows from **5 programs to 6** — `SONYMA` (State of New
   York Mortgage Agency) is real, confirmed by direct inspection and external research, and added to
   the mapping per Gordon's explicit direction even though no synthetic loan fixture exists to test
   it against (same posture as the already-named "no Jumbo tag found" case). SONYMA's own codes are
   **space-delimited** (`SONYMA`, `SONYMA HDFC`, `SONYMA Tax `), not dash-delimited like the other 5
   — a real format difference the parser must handle, not a uniform pattern.
2. **One entire questionnaire — "Post-Closing Private Bank Oct 2025," 802 rows, 100% of it — exports
   every column from "Question Code" onward one position left of the shared header** used by the
   other 3 real sources. Its true Exception Code lives where the header labels "Question Answers
   Exception Name," not "Exception Code." This was not anticipated in the original spec and required
   `taxonomy.py`'s row-loader to detect and correct for per-questionnaire, not assume one column
   mapping workbook-wide. Total real row count is **8,442** (not 8,021), and 6,349 of the original
   spec's cited "program-tagged" count was itself computed from the wrong column for this
   questionnaire — the corrected figure is **7,241 of 8,442 (85.8%)**.
3. **[Added 2026-07-26, spec audit — the third correction, previously disclosed only in plan.md]**
   The "**615 standalone SQL-gating rows**" figure US2 is still argued from below was itself an
   artifact of the same column-shift bug: after the fix, `sql_gating_rows_excluded` → 0 and the
   SQL-criteria mechanism turns out to be **workbook-pervasive, not narrow** — recomputed directly,
   **7,815 of 8,442 rows** carry a SELECT-style `sql_criteria` clause (see
   `output/RULE-PROGRAM-GATING-FINDINGS.md` revision history). US2's mechanism and design are
   unchanged and correct; its prevalence argument below understates reach by an order of magnitude
   and is left as-authored with this note. Additionally, the 7,241 (85.8%) tagged count above was
   computed **before** T028's space-delimited SONYMA extension landed; the shipped parser resolves
   **7,271 of 8,442 (86.1%)** — 7,225 dash-prefixed + 46 SONYMA-family.
**Depends on**: `002b-ruleset-compiler-pipeline` (implemented — this feature attaches applicability
metadata to what `002b` compiles; it does not compile anything itself). `003a`/`003b`/`003c`
(implemented — the engine that executes the gate). Not dependent on `009a` for its own correctness,
but `009a` (import UI) is where a human eventually reviews the parsed gates at sign-off time.
**Foundation this builds on** (proven, not re-specced): `p0/eval_synth/taxonomy.py`'s existing
row-loading and SQL-gating detection (`_SQL_GATING` regex, `sql_gating_rows_excluded` counter);
`p0/fixtures/ruleset_defects.py`'s `_check_applies`/`_DOC_PRESENCE_GATED`/`_PROPERTY_AGE_GATED`/
`_PROGRAM_GATED` — the same *shape* of gating this feature generalizes, but that code gates 21
hand-written checks by hand-inspection; this feature must derive the equivalent gate automatically
from data already in the real workbook, at ~6,349-row scale, not by a human reading each row.

**What this feature is fixing, precisely**: The gap named in `000-synthetic-fixture-generation`'s
own applicability-gating comment (`p0/fixtures/ruleset_defects.py` module docstring) was solved once,
by hand, for 21 checks tied to 5 known synthetic loans. That does not scale to the real workbook's
6,349+ program-taggable rows. Direct inspection (`output/RULE-PROGRAM-GATING-FINDINGS.md`) found the
real workbook already encodes program applicability in a way that scales: the **Exception Code
prefix** (`O-FHA-`, `O-VA-`, `O-RHS-`, `O-FRD-`, `O-FNM-`) on 79% of real rows, supplemented by 615
rows of SQL WHERE-clause criteria (property type, a blanket Fannie-Mae flag, purchase-only,
portfolio-only, one state). This feature parses both, maps them onto the loan's own `loan_type`, and
gates a compiled `Check` at evaluation time — the same *outcome* `_check_applies` already proves
correct at small scale, now *derived from data* instead of authored by hand.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A compiled check only fires for the loan program the real workbook actually tagged it for (Priority: P1)

Today, nothing gates a compiled check by program at all — `002b`'s pipeline compiles a `Check` from
a real row with no notion of which loan it should or shouldn't apply to. Running that check against
every loan (the "assume all rules apply for now" mitigation, Known Blocker #3) means an FHA-tagged
rule fires against a VA loan and vice versa — false-FAILs at real-workbook scale, the exact failure
`ruleset_defects.py`'s own module docstring documents finding and fixing once, by hand, for 21
checks.

**Why this priority**: This is the literal blocker named in the roadmap ("we don't want to run all
800 for every loan") and confirmed as a real, present-today risk the moment more than the current
21 hand-gated checks exist.

**Independent Test**: Compile a batch of real rows spanning at least 3 of the 5 tagged programs
(`O-FHA-`, `O-VA-`, `O-RHS-`, `O-FRD-`, `O-FNM-`); attach program-applicability metadata parsed from
each row's own Exception Code; run the resulting checks against all 5 synthetic loans; confirm each
check only produces a real verdict (PASS/FAIL/FLAG/NEEDS_REVIEW) on the loan(s) whose program
matches, and `NOT_APPLICABLE`-equivalent (excluded from the run, per this feature's gating — see FR-
002) on every other loan.

**Acceptance Scenarios**:

1. **Given** a compiled check derived from an `O-FHA-`-prefixed row, **When** the gated ruleset is
   built for an FHA loan, **Then** the check is included; **When** built for a VA, USDA, Freddie, or
   Conventional loan, **Then** the check is excluded.
2. **Given** a compiled check derived from an `O-VA-`-prefixed row, **When** the gated ruleset is
   built for the VA synthetic loan, **Then** it is included; excluded for the other 4.
3. **Given** the same for `O-RHS-` (USDA) and `O-FRD-` (Freddie), each against its own matching
   synthetic loan and excluded from the other 4.
4. **Given** an `O-FNM-`-prefixed row and the one synthetic loan whose `loan_type` is
   `"Conventional Purchase"` (not explicitly GSE-labeled), **When** gating runs, **Then** the
   mapping decision (Fannie-Mae-tagged rules apply to a generically-"Conventional" loan absent a
   more specific GSE label) is made explicitly and is inspectable — not a silent default (see Edge
   Cases; this is a genuinely ambiguous real-data case, not a clean 1:1 mapping like the other four).
5. **Given** a row carrying no Exception Code program prefix (the 21% untagged, or a regulation-
   category prefix like `O-TILA-`/`O-ECOA-`), **When** gating runs, **Then** the check is treated as
   applying to every program (fail-open on *program*, matching the current "assume applies" default)
   unless the secondary SQL-clause mechanism (FR-003) narrows it further.

---

### User Story 2 - The secondary SQL-clause mechanism narrows further where it's actually encoded (Priority: P2)

615 real rows carry an explicit `SELECT DISTINCT ... WHERE ...` clause narrowing applicability by
property type, a blanket `QC_Policy = 'Fannie Mae'` flag, purchase-vs-refi, portfolio-vs-agency, or
one state. Where present, this should further narrow a check beyond what the Exception Code prefix
alone determines — not replace it.

**Why this priority**: Real, but narrower in reach (615 of 8,021 rows, vs. 6,349 for the primary
mechanism) and only ever adds a *stricter* filter on top of the primary signal, never a
contradictory one in the data seen so far — lower priority than US1, not lower correctness bar.

**Independent Test**: Compile a row carrying both an Exception Code program prefix and a SQL
gating clause (e.g. `O-FNM-...` + `WHERE (Loans.QC_Policy = 'Fannie Mae') AND
(Loans.PropertyType = 'Condominium')`); confirm the resulting check applies only to a loan that is
both the right program *and* the right property type.

**Acceptance Scenarios**:

1. **Given** a row with a property-type-narrowed SQL clause, **When** gating runs against a loan of
   the matching program but a non-matching property type, **Then** the check is excluded.
2. **Given** a row with no SQL clause at all, **When** gating runs, **Then** applicability is
   determined by the Exception Code prefix alone (US1) — the absence of a secondary clause never
   blocks a check the primary signal says should apply.

---

### User Story 3 - Every rule row is actually read, not silently dropped by an unread sheet (Priority: P3)

`p0/eval_synth/taxonomy.py`'s `load_rows()` reads only the first sheet of each workbook file. The
Private Bank workbook's second sheet (`Pre Funding Nov 2025`) has never been read, classified, or
made available to gating at all.

**Why this priority**: Real but small (~9 rows) — correctness-affecting in principle, immaterial in
practice at today's data volume; sequenced last so it doesn't block US1/US2's larger-impact work.

**Independent Test**: Run the (fixed) row-loader against the Private Bank workbook; confirm rows
from both sheets are present in the output, including the previously-unread `PB-FormDoc` row.

**Acceptance Scenarios**:

1. **Given** the Private Bank workbook (2 sheets), **When** rows are loaded, **Then** the count
   reflects both sheets' real rows, not just the first sheet's.

---

### Edge Cases

- **The Fannie-vs-Freddie "Conventional" ambiguity** (US1 Scenario 4): the synthetic loans label one
  loan `"Conventional Purchase"` without naming a GSE investor. Real loans may carry the same
  ambiguity if the extracted data doesn't name Fannie vs. Freddie explicitly. This feature does not
  silently guess — it treats `O-FNM-` and `O-FRD-` as two *distinct* program tags and requires the
  loan's own program signal to disambiguate; where it cannot, the check is treated the same as an
  untagged row (fails open), and this is logged/inspectable, not hidden. Resolving this properly
  (e.g. requiring loan data to carry an explicit GSE investor field) is a genuinely open question,
  named here, not solved.
- **No `Jumbo`-tagged rows found** in either real workbook (0 keyword hits, per the findings doc).
  This feature does not invent a jumbo/non-conforming gate; if a future workbook batch contains one,
  it will need its own prefix mapping added — not assumed solved by this feature's initial 5-program
  table.
- **The ~13.9% of rows with no program-prefixed Exception Code** (~1,171/8,442, post-correction — the
  pre-correction 21% figure was computed from the wrong column for the Private Bank questionnaire; the
  corrected shipped parser resolves 7,271/8,442 = 86.1%; federal-regulation categories like
  `O-TILA-`/`O-ECOA-`/`O-HMDA-`, or genuinely untagged rows): treated as program-agnostic (apply to
  every loan) unless a secondary SQL clause narrows them — consistent with the current "assume
  applies" default, not a regression of it.
- **A row whose SQL clause and Exception Code prefix would disagree** (e.g. `O-FHA-` prefix but a
  clause naming `QC_Policy = 'Fannie Mae'`): not observed in the 615 real clauses sampled (every
  `QC_Policy` value seen was `'Fannie Mae'`, never paired against a contradicting FHA/VA/USDA prefix
  in this data) — but if found, this feature treats it as a real authoring inconsistency to surface
  at sign-off (`009a`), not silently resolve in either direction.
- **The `Question Criteria by Questions` column** (questionnaire branching logic, not program gating
  — findings doc §4): explicitly out of scope; must not be confused with or folded into this
  feature's program-applicability parsing.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST parse a compiled check's source row's Exception Code prefix into a
  program tag, using the six confirmed mappings (`O-FHA-`→FHA, `O-VA-`→VA, `O-RHS-`→USDA,
  `O-FRD-`→Freddie Mac, `O-FNM-`→Fannie Mae, `SONYMA`→SONYMA) as the primary applicability signal.
  Two real formats MUST both be handled: dash-delimited (the first 5) and space-delimited (SONYMA's
  own codes — `SONYMA`, `SONYMA HDFC`, `SONYMA Tax `, never dash-suffixed).
- **FR-002**: A gated ruleset build for a given loan MUST include a program-tagged check only when
  the loan's own `loan_type` maps to that same program, and MUST exclude it otherwise — the same
  outcome `ruleset_defects.py`'s hand-authored `_PROGRAM_GATED` proves at 4-check scale, now derived
  from data at real-row scale.
- **FR-003**: Where a row also carries a parseable SQL gating clause (property type / `QC_Policy` /
  `LoanPurposeType` / `LoanType` / `AddressState`), the system MUST apply it as an additional filter
  on top of FR-001/FR-002's program match — never as a replacement, and never loosening what FR-002
  already excluded.
- **FR-004**: A row with no program-prefixed Exception Code and no SQL clause MUST default to
  applying across every program (fail-open on program-applicability) — matching Known Blocker #3's
  existing "assume all rules apply for now" mitigation, not silently narrowing it.
- **FR-005**: The system MUST NOT silently resolve the Fannie-vs-Freddie "Conventional" ambiguity
  (Edge Cases) by guessing — an ambiguous case MUST be inspectable (surfaced in whatever report/log
  this feature produces), not hidden inside a default.
- **FR-006**: The system MUST read every sheet of every workbook file in `demo/rules/`, not only the
  first — fixing `taxonomy.py`'s current single-sheet limitation (US3).
- **FR-006a** *(added post-implementation — see spec preamble's "Post-hoc correction")*: The system
  MUST correctly read the "Post-Closing Private Bank Oct 2025" questionnaire's shifted column layout
  (every field from "Question Code" onward is one column left of the shared header) — detected by
  `Questionnaire Name`, not sheet name or position, since that field is the one guaranteed correctly
  positioned regardless of the shift. Also MUST NOT list Excel's `~$`-prefixed lock/temp files as
  real workbooks (found blocking this fix while Gordon had the source files open in Excel).
- **FR-007**: This feature MUST NOT derive gating dimensions the real workbook doesn't already
  encode (that is `010b`'s scope) — e.g. it must not invent owner-occupied-vs-investment gating from
  loan data if neither mechanism in this workbook encodes it.
- **FR-008**: This feature MUST NOT change `ruleset_defects.py`'s existing 21 hand-authored checks
  or their hand-derived gates — those remain as-is; this feature is additive, for checks compiled by
  `002b` from real rows, not a replacement of the existing demo-scale gating.
- **FR-009**: This feature MUST NOT parse or act on the `Question Criteria by Questions` column
  (questionnaire branching logic) — explicitly a different concern (Edge Cases).
- **FR-010**: This feature MUST NOT build the authoring-UI surfacing of parsed gates (`009a`) or the
  real-rule LLM compile run itself (`002b`, already implemented) — it supplies the gating metadata
  those consume.

### Key Entities

- **ExceptionCodePrefix → Program** (new, small static table): the 6 confirmed mappings (§ FR-001),
  extensible if a future workbook batch introduces a 7th program tag (e.g. Jumbo, 0 hits found so
  far) — not assumed closed at 6.
- **CompiledCheckDraft** (existing, `p0/qc_engine/compiler/compile_llm.py`): gains an applicability
  field carrying the parsed program tag(s) and any secondary SQL-derived filter, alongside the
  existing `check`/`source_text`/`extracted_intent` — additive, no existing field changed.
- **CanonicalLoan.loan_type** (existing, `p0/qc_engine/model.py`): read, not modified — the mapping
  target FR-002 gates against (confirmed real values across the 5 synthetic loans: `"Conventional
  Purchase"`, `"FHA Purchase"`, `"VA Purchase"`, `"Freddie Mac Cash-Out Refi"`, `"USDA RHS 502
  Guaranteed"`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Across a compiled batch spanning all 6 confirmed program prefixes, 100% of resulting
  checks apply only to the synthetic loan(s) whose program matches, and are excluded from the other
  4 tested programs (SONYMA is untested against a real fixture — no synthetic loan carries it,
  verified instead to be unambiguously excluded from all 5 existing loans) — verified by test, not
  spot-checked.
- **SC-002**: The Fannie-vs-Freddie ambiguity case (US1 Scenario 4) is surfaced inspectably in every
  test run that exercises it — zero instances of it being silently resolved either way.
- **SC-003**: The row-loader reads both sheets of the Private Bank workbook; the previously-unread
  `PB-FormDoc` row (or an equivalent second-sheet row) is present in its output.
- **SC-004**: Zero regression — `ruleset_defects.py`'s 21 checks, their existing hand-derived gates,
  and every pre-existing test in `p0/tests/`/`p0/eval_synth/` continue to pass unmodified; the P0
  determinism digest (`a3f702c12969f7eb657471796c95e2a493d459c4c55663fa8fc18ac31e8c1d09`, current
  post-004 baseline) is unchanged.
- **SC-005**: This spec's own text names the 21%-untagged fail-open default, the Fannie/Freddie
  ambiguity, and the "no Jumbo tag found" observation as explicit, inspectable scope boundaries —
  not silently absorbed into "gating solved."

## Assumptions

- The 6 confirmed Exception Code prefixes (`O-FHA-`, `O-VA-`, `O-RHS-`, `O-FRD-`, `O-FNM-`,
  `SONYMA`) are treated as the complete known set for this feature's first version — a 7th program
  tag appearing in a future workbook batch would need its own mapping added, not assumed covered.
- The SQL-clause mechanism's confirmed field set (`QC_Policy`, `PropertyType`, `Occupancy`,
  `Underwriting_Type`, `LoanType`, `LoanPurposeType`, `AddressState` — corrected from an earlier,
  narrower draft of this spec, see preamble) is treated as the complete known set from direct
  inspection of all 8,442 real rows — a future batch could introduce new fields/values this
  feature's parser would need to handle, not silently ignore. **Only `PropertyType` narrowing is
  implemented in this increment** — `Occupancy`/`Underwriting_Type`/`LoanType`/`LoanPurposeType` are
  confirmed real and parseable but deferred to a future increment of this same feature (§3 of the
  findings doc), not `010b`.
- Deriving gating dimensions **neither** mechanism already encodes is `010b`'s job, explicitly not
  this feature's — same split the roadmap already made, now with a narrower `010b` scope than
  originally assumed (Occupancy turned out to be encoded, not something to derive).
- The real "test run" (compiling real rows via `002b` and running them against the 5 synthetic
  loans) is sequenced to happen only after this feature exists — attempting it first would repeat,
  at ~7,241-row scale, the exact false-FAIL problem `ruleset_defects.py`'s module docstring already
  found and fixed once by hand at 21-check scale.
- AOR-based finding routing (`Underwriter`/`Processor`/`Closer`) and severity-taxonomy alignment
  (this workbook's Critical/Major/Minor vs. `engine.py`'s CRITICAL/WARNING/INFO) are both real,
  confirmed by domain research, and explicitly out of scope here — noted for whichever future spec
  (`006`/`008`) is positioned to use them, not built or assumed solved by this feature.
- `009a` (the authoring/import UI) does not exist yet; this feature's parsed applicability metadata
  is assumed to be consumed by a script/report for now, not a UI this feature builds.
