# Feature Specification: Operator-Direction Consistency Gate

**Feature Branch**: `002d-operator-consistency-gate`
**Created**: 2026-07-24
**Status**: Implemented — Phase 1 (2026-07-25; all 45 known suspects reproduced + 3 same-pattern catches; header corrected from stale "Draft" 2026-07-26, spec audit)
**Input**: Surfaced on a live SME review call (Kayla + Gordon) of loan 01's QC output: Kayla manually
re-derived loan 01's LTV (exactly 80.0%) and found the tool's own two LTV/MI checks disagreed with
their own stated rule intent. Formalized in `output/SME-REVIEW-FINDINGS-2026-07-24.md` §2 and
`output/RULE-COMPILER-FIX-PLAN-2026-07-24.md` §2, after external research (arXiv:2411.01414,
arXiv:2604.25031) confirmed this is a documented, named LLM failure class ("Conditional Misalignment
Error"), not an anomaly specific to this prompt.

**Governs**: `output/ROADMAP.md` Tension 9 (partial — the operator-direction half; the conditional-
applicability half is `002e`/`002f`). `.specify/memory/constitution.md` Principle I (determinism/
correctness) and Principle II (compile, then run — this is a compile-time defect, fixed at compile
time).

**Cross-validated 2026-07-24**: `002f-precondition-ontology-layer`'s Layer 2 independently arrived at
the same shape this spec already used — an automated grounding/consistency check running *before*
any human review, not a substitute for one (source: ComplianceNLP, arXiv:2604.23585, whose MiniCheck-
style grounding-verification ablation shows removing that automated step drops accuracy 94.2%→86.7%).
This spec's User Story 2 (formalize the manual scan into a permanent, automatic gate) is the same
pattern applied to operator-direction consistency instead of citation-grounding — no design change
here, just an additional, independent citation for why this shape is correct.
**Depends on**: `002b-ruleset-compiler-pipeline` (implemented — this feature extends
`compile_llm.py`'s `SYSTEM_PROMPT` and adds one new validation pass; no new architecture).
**Foundation this builds on**: `p0/qc_engine/compiler/compile_llm.py`'s `compile_row()` (already
generates `message_pass`/`message_fail` and `operator`/`threshold` in the same LLM call — this
feature adds a comparison between them, not a new LLM call) and `p0/qc_engine/engine.py`'s
`ratio_threshold` evaluation (`res.status = "PASS" if ok else "FAIL"`, where `ok` is computed from
`chk.operator`/`chk.threshold` — confirmed correct and unchanged; the bug is entirely upstream, in
what the compiler writes into those fields).

**What this feature is fixing, precisely:** `engine.py`'s `ratio_threshold` evaluation treats
`operator` as the literal PASS-condition expression: `ok = (value <= thr) if op == "<=" ... else
(value > thr)`, `status = "PASS" if ok else "FAIL"`. `compile_llm.py`'s `SYSTEM_PROMPT` never states
this convention to the compiling LLM — it only says `"operator": "<= | < | >= | > (ONLY if
kind=ratio_threshold)"` with no guidance on which direction is expected. Where a source AMQ row's
`defect_text` phrases a FAIL-trigger condition ("if LTV **exceeds** 80%, MI is required"), the LLM has
transcribed the comparison word literally (`operator: ">"`) instead of inverting it to express the
PASS condition the engine actually needs (`operator: "<="`).

Confirmed concretely: `fnm-ltv-mi-required` and `ltv-exceeds-80-without-mi` (both real, compiled
checks in `result/rules/post_closing_only_ruleset.json`) carry `operator=">", threshold=80`, while
their own `message_pass` text states *"LTV is at or below 80%; MI not required..."* — i.e. PASS
should require `<=80`. Loan 01's real LTV is exactly 80.0% (`loan_amount=340,000.00`,
`property_value=425,000.00`); with the compiled (wrong) operator, `80.0 > 80` is `False`, so the
engine returns **FAIL** at the exact boundary the rule's own text says should PASS — a genuine false
positive, already reported to Gordon's colleague as a confirmed defect in
`output/LOAN-01-QC-RESULT-WITH-PROVENANCE-2026-07-24.pdf`.

A heuristic scan (`output/operator_inversion_suspects_2026-07-24.json`, re-run 2026-07-24; "script
persisted" was inaccurate — the ad-hoc scan script, `heuristic4.py`, was never committed, only its
JSON output; the logic now lives permanently in `operator_consistency_check()`. Corrected
2026-07-26, spec audit) found the same signature — operator direction contradicting the check's own `message_pass`
text — in **45 of 495** unique `ratio_threshold` checks in the current ruleset. This is a heuristic
lower bound keyed on 7 specific PASS-condition phrasings; the true count of inverted checks may be
higher.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - New compiles don't invert the operator (Priority: P1)

Today, `compile_llm.py`'s `SYSTEM_PROMPT` gives the compiling LLM no guidance on which direction
`operator` must express. After this feature, the prompt states the PASS-condition convention
explicitly, with few-shot examples of inverting a FAIL-framed source sentence, so future compiles of
FAIL-framed rows produce the correct (inverted) operator.

**Why this priority**: This is the root-cause fix — cheapest, addresses the actual defect, and
prevents the bug class recurring on any future recompile (e.g. `002e`'s eventual full-rulebook pass).

**Independent Test**: Recompile a small representative sample of known FAIL-framed `ratio_threshold`
rows (including the two confirmed-bad checks' source rows) with the updated prompt; confirm the
compiled `operator` now expresses the PASS condition matching `message_pass`.

**Acceptance Scenarios**:

1. **Given** a source row whose `defect_text` describes a FAIL-trigger comparison ("exceeds",
   "greater than", "more than" a threshold), **When** compiled, **Then** the emitted `operator`
   expresses the inverted PASS condition (e.g. `defect_text` says "exceeds 80%" → `operator: "<="`,
   not `">"`).
2. **Given** a source row whose `defect_text` already describes a PASS-trigger comparison directly
   (no inversion needed), **When** compiled, **Then** the emitted `operator` is unchanged from
   today's (already-correct) behavior — this feature must not introduce a NEW inversion bug in the
   opposite direction.

---

### User Story 2 - Already-compiled inconsistent checks are caught, not silently signed (Priority: P1)

Today, nothing checks a compiled check's `operator`/`threshold` against its own `message_pass`/
`message_fail` text for consistency — the 45 suspect checks compiled and would have been signed
without any automated flag. After this feature, every compile batch runs a deterministic consistency
gate comparing the two, and any check that fails it is held out of auto-sign and routed to SME
review.

**Why this priority**: Without this, the exact bug class that already shipped one confirmed false
positive recurs silently on every future compile — the SME review call is the only reason this batch
was caught. This makes the check permanent instead of a one-time manual scan.

**Independent Test**: Run the consistency gate against `post_closing_only_ruleset.json` (or an
equivalent fixture batch containing both known-bad checks and known-good ones); confirm both known-bad
checks are flagged and a representative sample of known-good checks are not (no false positives on
the common, correctly-compiled majority).

**Acceptance Scenarios**:

1. **Given** a compiled `ratio_threshold` check whose `operator` direction contradicts its own
   `message_pass` text (per the same phrase-matching heuristic already validated on the real
   ruleset), **When** the consistency gate runs, **Then** the check is flagged and excluded from
   auto-sign (`assemble_ruleset`'s signed set), routed to the SME exception queue instead.
2. **Given** a compiled `ratio_threshold` check whose `operator` direction is consistent with its
   `message_pass` text, **When** the gate runs, **Then** the check is not flagged and proceeds to
   sign-off normally — no regression on the ~450 already-correct checks in the current ruleset.
3. **Given** the gate's flagging heuristic, **When** measured against the current ruleset, **Then**
   it reproduces at least the 45 checks already found by the manual scan (a floor, not a ceiling —
   the gate may reasonably catch additional phrasings the manual heuristic didn't).

### Edge Cases

- What happens to a check whose `message_pass`/`message_fail` text doesn't contain any of the
  recognized comparison phrases (neither clearly PASS- nor FAIL-framed prose)? → The gate has no
  signal to check against; it does not flag the check (absence of a contradiction signal is not
  evidence of a contradiction) — consistent with this feature's scope being detection of a specific,
  named contradiction pattern, not a general correctness proof of every check.
- What happens to the two already-known-bad checks and the 45 flagged suspects in the currently-signed
  `post_closing_only_ruleset.json`? → Re-running the gate against the existing artifact is this
  feature's validation step (User Story 2), but re-signing a corrected ruleset and regenerating the
  already-shipped `LOAN-01-QC-RESULT-WITH-PROVENANCE-2026-07-24.pdf`/`loan01_with_provenance.json` is
  explicitly **out of scope** for this feature — a follow-up housekeeping action once this feature and
  `002e` both ship, tracked in `output/SME-REVIEW-FINDINGS-2026-07-24.md` §4.
- What happens if the gate itself has a bug and over-flags correct checks? → SC-002 requires measuring
  false-positive rate against a representative correct-check sample before this feature is considered
  done — an over-eager gate that blocks correct checks from sign-off is a real regression risk, not a
  free "err on the side of caution" move (it would defeat the purpose of automating a scan a human
  currently has to do by hand).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `compile_llm.py`'s `SYSTEM_PROMPT` MUST explicitly state that `operator`/`threshold`
  must always express the condition under which the loan PASSES, regardless of whether `defect_text`
  is phrased as a pass-trigger or fail-trigger condition, with at least 2 few-shot examples
  demonstrating the inversion of a FAIL-framed source sentence.
- **FR-002**: A new, deterministic (no LLM call) consistency-check function MUST exist that, given a
  compiled `ratio_threshold` Check's `operator`/`threshold`/`message_pass`/`message_fail`, returns
  whether the operator's direction is consistent with the natural-language PASS-condition phrasing —
  formalizing the existing heuristic scan (`output/operator_inversion_suspects_2026-07-24.json`'s
  script) into reusable, tested code, not a one-off script.
- **FR-003**: This consistency check MUST run automatically as part of the compile-batch pipeline
  (`compile_batch`/`assemble_ruleset` or an explicit step between them) — not require a human to
  remember to invoke a separate scan script.
- **FR-004**: A check flagged by the consistency gate MUST be excluded from `assemble_ruleset`'s
  signed set by default (i.e. treated the same as a `parse_error`d draft — present in the batch
  output for SME review, absent from the auto-signed `Ruleset`), never silently signed.
- **FR-005**: The gate MUST NOT require a second LLM call — it operates purely on fields already
  produced by the existing single `compile_row()` call (`operator`, `threshold`, `message_pass`,
  `message_fail`).
- **FR-006**: This feature MUST NOT change `engine.py`'s `ratio_threshold` evaluation logic — it is
  confirmed correct; the defect is entirely in what the compiler writes into `Check.operator`, not in
  how the engine reads it.
- **FR-007**: The gate's flagging heuristic MUST be measured for false positives against a
  representative sample of already-correct checks in the current ruleset before this feature ships
  (Edge Cases) — not assumed safe from the 45-check true-positive result alone.

### Key Entities

- `Check` (existing, `p0/qc_engine/ruleset.py`): **unchanged** — this feature adds a validation
  function operating on existing fields, no new `Check` field.
- `output/operator_inversion_suspects_2026-07-24.json` (existing artifact): the reference true-positive
  set (45 checks) this feature's formalized gate must at minimum reproduce.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The formalized consistency gate, run against `post_closing_only_ruleset.json`, flags
  both confirmed-bad checks (`fnm-ltv-mi-required`, `ltv-exceeds-80-without-mi`) and at least the 45
  checks the manual heuristic scan already found.
- **SC-002**: The gate's false-positive rate against a representative sample of already-correct
  `ratio_threshold` checks (checks NOT in the 45-suspect set) is measured and reported — target zero,
  but the number must be reported either way, not assumed.
- **SC-003**: A recompile of a small sample of known FAIL-framed source rows (including the two
  confirmed-bad checks' original source rows) with the updated `SYSTEM_PROMPT` produces the correctly-
  inverted `operator` for each.
- **SC-004**: `pytest p0/tests -v` passes in full — zero regressions to existing compiler/engine tests.

## Assumptions

- This feature does not re-sign or regenerate the currently-shipped `post_closing_only_ruleset.json`
  or any downstream report — that is explicitly out-of-scope housekeeping, tracked separately.
- The 7-phrase heuristic already validated (`output/operator_inversion_suspects_2026-07-24.json`'s
  script) is the starting point for FR-002's formalized function, not necessarily its final form —
  broadening phrase coverage is in-scope if it doesn't regress SC-002's false-positive measurement.
- This is a sibling of `002b`/`002c` in the compiler-family spec arc, numbered `002d` per
  `output/RULE-COMPILER-FIX-PLAN-2026-07-24.md`'s suggested sequencing (small, low-risk, can ship
  ahead of `002e`).
