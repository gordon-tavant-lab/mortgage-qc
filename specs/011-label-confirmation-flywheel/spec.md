# Feature Specification: Label Confirmation Flywheel

**Feature Branch**: `011-label-confirmation-flywheel`
**Created**: 2026-07-27
**Status**: DEFERRED (2026-07-27, same day as written) — Gordon's explicit scope call: this adds complexity not needed this round. The spec below is complete, adversarially reviewed, and evidence-grounded (see the two independent audit passes logged in `output/SPEC-DOUBLE-CHECK-FINDINGS.md`) — nothing here is wrong, it's simply not in scope for the current build round. Pick it back up as-is when the flywheel is actually wanted; re-verify the file:line citations first, since the codebase will have moved on by then.
**Input**: `output/ROADMAP.md` §011 — "The primary moat is the eval/labeled-outcome flywheel (PRD §9).
The engine's cited outputs become draft labels the SME confirms — compounding the corpus. Wire from
the first pilot loan." Scope handed down explicitly: capture an SME's confirm/correct action on a
cited engine output (a `CheckResult` a reviewer is looking at, in the eventual Output/exception-review
screen) → grow a labeled corpus from these confirmations over time → feed the growing corpus back
into `005`'s tiered eval sets. Instrument from day 1 of pilot, not as a big-bang build.

**Governs**: `output/ROADMAP.md` §011, `.specify/memory/constitution.md` Principle III (Eval is
foundational — NON-NEGOTIABLE; this feature is the mechanism that turns a machine verdict into
human-ratified ground truth), the Audit quality gate (a confirmation on a cited output is itself an
event that must be traceable, not an out-of-band side note), Principle I (determinism — this feature
must never let a human's confirmation *retroactively* change what the engine already computed; it
annotates, it never rewrites, the same "read-only, one-way" discipline `014`'s narrative already
established for a different downstream-of-the-verdict concern).

**Depends on**: `005-eval-harness-as-promotion-gate` (Drafted this session, same day — spec.md/plan.md/
tasks.md already written; its `FR-010` scorer contract — "(loan, expected_verdicts) pair whose
provenance is `expert-labeled` vs `constructed-by-mutation` scores identically" — is the exact seam
this feature's corpus must target). `007-audit-trail-and-citation-of-record` (**implemented**,
confirmed 2026-07-27 by direct code inspection — `p0/qc_engine/audit.py`'s hash-chained `AuditLog`;
a confirmation is itself an audited event and must carry the same tamper-evidence discipline).
`008-exception-queue-and-clear-next` (**not built** — the Output/`ExceptionReview` surface where an
SME would actually click "confirm"/"correct" in production does not exist yet, and building it is
explicitly out of scope for this whole planning pass per Gordon's direction). This is named honestly
as a real dependency tension, not silently worked around: `011`'s mechanism needs *some* interaction
surface to attach to, so it ships its own minimal, headless calling convention (FR-008) that `008`,
once built, calls into rather than reinventing.

**Foundation this builds on** (proven, not re-specced):
- `p0/qc_engine/engine.py`'s `CheckResult` (lines 46-85) already carries everything a confirmation
  needs to reference: `check_id`, `status`, `citation` (doc name + page + segment), `review_reason`
  (open-vocabulary tag from `004`, `None` for a clean `PASS`/`FLAG`), and `message`. `RunResult`
  (lines 423-503) composes these per loan and already exposes `disposition`/`review_reasons`/
  `ruleset_sha256`/`ruleset_version` — the exact coordinates (`loan_id` + `ruleset_sha256` +
  `check_id`) that uniquely identify *which* cited verdict a human is reacting to.
- `p0/qc_engine/audit.py`'s `AuditLog` (implemented) proves the hash-chain mechanics this feature
  reuses conceptually: `GENESIS` sentinel, `_digest(prev_hash, payload)` (SHA-256 of prior hash +
  canonical JSON), `append()` (chains a new record), `verify_chain()` (walks every record,
  recomputes hashes, detects tampering). `AuditLog.append()` is typed specifically to a `RunResult`
  (machine verdicts) — it is not shaped to append a human's confirmation, and this feature does not
  force it to; see Assumptions for the "reuse the primitives, add a sibling, don't reshape 007"
  decision.
- `p0/experiment_002a/build_review_package.py` + `apply_decision_rule.py` are the closest *existing*
  "capture a human's judgment as structured, auditable data" code in this repository — but for a
  **different artifact**. They assemble a markdown table (`sme_review_package.md`) for Kayla to fill
  in `verdict`/`correction`/`reviewer_note` per *compiled rule draft* (a plain-English restatement of
  one AMQ workbook row), then `apply_decision_rule.py` parses those filled-in fields, computes an
  `interpretation_fidelity_rate` against a **pre-registered, locked threshold**
  (`D1_INTERPRETATION_FIDELITY_THRESHOLD = 0.70`), and emits a one-time `PROCEED`/`RECONSIDER`/`KILL`
  spike verdict plus a mean edit-distance (reusing `qc_engine.ruleset._edit_distance`). This is a
  **compile-time, one-shot spike artifact** — it judges whether the compiler read a source row
  correctly, decoupled from any actual loan. `011` is a fundamentally different, **run-time,
  perpetual** mechanism: it judges whether a live, cited `CheckResult` a signed ruleset produced
  against a real loan was actually correct, and it never stops accumulating. The *shape* worth
  reusing — human fills in a verdict against a machine-produced artifact, verdict becomes structured
  data, an explicit "no verdict yet" state blocks silently guessing — is the only thing carried
  forward; the artifact, the trigger, and the lifecycle are not shared.
- `005-eval-harness-as-promotion-gate` (spec.md FR-010, Key Entity `ConstructedScenario`): the scorer
  this feature's corpus ultimately feeds is *already designed*, in the same session, to accept a
  provenance-tagged `(loan, expected_verdicts)` pair with no branch keyed on "how was this loan
  produced." `011`'s job is to *produce* that provenance-tagged pair from a human's action, not to
  modify how `005` consumes it.

**Gaps confirmed by direct inspection, not assumed**:
1. **Zero hits anywhere in `p0/` for "flywheel", "label_capture", or any mechanism that captures a
   human's confirm/correct reaction to a live, cited `CheckResult`.** Grepped directly, not inferred.
   Nothing exists to build on beyond the two adjacent-but-different artifacts named above.
2. **`AuditLog.append()` (`audit.py:58`) accepts only a `RunResult`.** There is no method, table, or
   schema anywhere that appends a *human* event to any audit trail in this codebase.
3. **`CheckResult.review_reason` (`004`, `engine.py:66`) is the natural anchor for "what is this
   confirmation about," but nothing today reads it for anything other than `RunResult.review_reasons`
   aggregation** — no consumer treats an individual tagged `CheckResult` as a unit a human reviews.
4. **`005`'s own `FR-010`/User Story 5 already anticipates this feature's exact interface** (a
   provenance-tagged `(loan, expected_verdicts)` triple, scored identically regardless of origin) —
   confirmed by reading `specs/005-eval-harness-as-promotion-gate/spec.md` directly, written earlier
   the same day. This is the one gap that is already closed on the *receiving* end; `011`'s job is
   entirely on the *producing* end.
5. **No versioned, human-curated "GOLDEN panel" promotion workflow exists** (`005`'s own Gap 3/Risk:
   `Ruleset.version` is hardcoded to `1` everywhere) — so this feature cannot assume there is a live
   event that automatically merges a confirmed label into `005`'s static `golden_panel.py`. That
   merge is necessarily a deliberate, human-curated step (see FR-007), not a real-time pipe.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Capture a single SME confirm/correct action as an audited, immutable event (Priority: P1)

A reviewer looking at one cited `CheckResult` (in the eventual `008` queue, or — until that exists —
via a minimal headless call from any interim review workflow) either agrees with the machine's
verdict ("confirm") or says it's wrong and supplies what it should have been ("correct"). That
reaction must be captured as a structured, tamper-evident record the moment it happens — not
buffered in a spreadsheet, not paraphrased into free text later.

**Why this priority**: This is the literal mechanism the roadmap names ("the engine's cited outputs
become draft labels the SME confirms") — without it, nothing downstream (corpus growth, feeding
`005`) has anything to consume.

**Independent Test**: Construct a completed `RunResult` for a loan (reusing existing fixtures, e.g.
`p0/fixtures/golden.py`), pick one `CheckResult` from it, call the capture entry point once with
`action="CONFIRM"` and once (a different check) with `action="CORRECT"` plus a `corrected_status`;
confirm both produce a `LabelConfirmation` record whose fields exactly identify the loan, ruleset,
and check being reacted to, and that both records are chained into an immutable log whose
`verify_chain()`-equivalent returns `True`.

**Acceptance Scenarios**:

1. **Given** a completed `RunResult` and one of its `CheckResult`s, **When** an SME confirms it,
   **Then** a `LabelConfirmation` record is captured naming `loan_id`, `ruleset_sha256`,
   `ruleset_version`, `check_id`, the check's `original_status`, `action="CONFIRM"`, and
   `corrected_status=None`.
2. **Given** the same setup, **When** an SME instead corrects it, **Then** the captured record has
   `action="CORRECT"` and a non-empty `corrected_status` naming what the check's status should have
   been.
3. **Given** two captured confirmations in sequence, **When** the confirmation log's chain is
   verified, **Then** verification succeeds; **When** any one historical record's payload is
   mutated post-hoc, **Then** verification fails from that point forward — proving tampering is
   detectable, mirroring `007`'s own `AuditLog.verify_chain()` proof.
4. **Given** a captured `LabelConfirmation`, **When** it is inspected, **Then** it names the exact
   `record_hash` of the originating run's entry in `007`'s `AuditLog` — a confirmation with no
   provable link back to the machine verdict it reacts to is not a valid record (FR-011).

---

### User Story 2 - The corpus grows durably across runs, and disagreement is preserved, not collapsed (Priority: P1)

Confirmations accumulate across many loans and many review sessions, surviving process restarts —
"compounding the corpus" per the roadmap's own framing. If two different SMEs (or the same SME twice)
react differently to the same cited check, both reactions are kept, not merged or overwritten — a
disagreement is itself a signal a later curation pass needs to see, not noise to average away.

**Why this priority**: Equal to US1 — a capture mechanism that doesn't durably grow, or that silently
collapses disagreement, delivers none of the "compounding" value the roadmap names as the entire
reason this feature exists (the primary moat).

**Independent Test**: Capture N confirmations across M distinct loans in one process, terminate the
process, start a new process, and confirm all N records are still present and unmodified; then
capture two different actions against the identical `(loan_id, ruleset_sha256, check_id)` coordinate
and confirm both persist as distinct records.

**Acceptance Scenarios**:

1. **Given** N confirmations captured in one process run, **When** a new process reads the corpus,
   **Then** all N records are present, in the order captured, with every field intact.
2. **Given** one `CheckResult` confirmed by reviewer A and corrected by reviewer B, **When** the
   corpus is queried for that `(loan_id, ruleset_sha256, check_id)` coordinate, **Then** both records
   are returned — neither overwrites nor is silently dropped in favor of the other.
3. **Given** a growing corpus, **When** queried by `action` (`CONFIRM` vs `CORRECT`) or by
   `check_id`, **Then** the query returns exactly the matching subset — a future curation pass must
   be able to isolate "loans a human explicitly said the machine got wrong" as its own distinct
   signal (FR-013).

---

### User Story 3 - A confirmed/corrected label converts into 005's scorer-compatible shape, with zero rework to that scorer (Priority: P2)

Once a label is captured, it needs to become something `005`'s GOLDEN/VOLUME tiers can actually score
— a `(CanonicalLoan, expected_verdicts, provenance)` triple, exactly the shape `005`'s own `FR-010`
already promises to accept without a code change.

**Why this priority**: Lower than US1/US2 because it is a pure conversion layer over a mechanism that
already exists on the receiving end (`005`, drafted the same day) — the value is real but it depends
entirely on capture (US1) and durable growth (US2) already working.

**Independent Test**: Take one captured `CONFIRM` record and one captured `CORRECT` record; convert
each into a `(CanonicalLoan, expected_verdicts, provenance)` triple; feed both through `005`'s actual
scorer function with no modification to that function's signature; confirm both score without error
and the `provenance` field distinguishes `"sme-confirmed"` / `"sme-corrected"` from
`"constructed-by-mutation"`.

**Acceptance Scenarios**:

1. **Given** a captured `CONFIRM` record, **When** it is converted, **Then** `expected_verdicts`
   for the confirmed check equals the check's original (machine-produced) status, and
   `provenance == "sme-confirmed"`.
2. **Given** a captured `CORRECT` record, **When** it is converted, **Then** `expected_verdicts` for
   that check equals the SME's `corrected_status` (not the original machine status), and
   `provenance == "sme-corrected"` — a correction's ground truth is the human's stated answer, never
   the machine's original one.
3. **Given** both converted triples, **When** each is passed to `005`'s scorer, **Then** neither call
   requires a code change to the scorer's signature (`005` spec.md FR-010) — the corpus is a new
   *source*, not a new *harness*.

---

### User Story 4 - Promotion into 005's permanent GOLDEN panel is a deliberate, curated step — never automatic (Priority: P2)

A single mistaken click (a rushed confirm, a fat-fingered correction) must never silently become a
permanent regression case every future ruleset is graded against. Promoting an accumulated corpus
entry into `005`'s version-controlled `golden_panel.py` requires an explicit human curation decision.

**Why this priority**: Equal-tier safety concern to US3 (not lower) — this is the mechanism that
prevents the flywheel itself from becoming a silent corruption vector for the eval harness it feeds.

**Independent Test**: Confirm that capturing N `LabelConfirmation`s, by itself, produces zero changes
to `005`'s `golden_panel.py` file; then run an explicit, separate promotion step naming specific
corpus entries and confirm only those entries land in the panel.

**Acceptance Scenarios**:

1. **Given** any number of freshly captured confirmations, **When** no explicit promotion step has
   been run, **Then** `005`'s `golden_panel.py` is byte-identical to its state before capture began.
2. **Given** an explicit promotion step naming a specific set of corpus entries, **When** it runs,
   **Then** exactly those entries (and no others) are merged into the GOLDEN panel, each tagged with
   its confirmation provenance so a later examiner can trace a panel case back to the specific
   `LabelConfirmation`/`reviewer_id`/`confirmed_at` that produced it.

---

### User Story 5 - The mechanism is usable headlessly from day one of pilot, without waiting on 008 (Priority: P3)

Per the roadmap's explicit "wire it early" mandate, this feature must not sit idle until `008`'s UI
ships. It needs a minimal, headless calling convention any interim review process — a CLI prompt, a
spreadsheet-driven script, even Kayla's own manual review pattern from `002a` — can invoke starting
with the very first pilot loan.

**Why this priority**: Lowest priority because it does not change the mechanism itself (US1-US4
already fully specify it) — it only confirms the mechanism is *reachable* without `008` existing,
which is the roadmap's stated intent, not a new capability.

**Independent Test**: Invoke the capture entry point directly (function call or CLI), with no UI, no
mock of `008`, and no dependency on any code that does not exist yet; confirm it succeeds identically
to how a future `008` screen would invoke it.

**Acceptance Scenarios**:

1. **Given** no `008` UI exists in this codebase, **When** the capture entry point is called directly
   (a plain function call or a CLI script), **Then** it produces an identical `LabelConfirmation`
   record to what a hypothetical UI-driven call would produce — the entry point's contract does not
   assume any particular caller.

---

### Edge Cases

- Two SMEs disagree on the same cited check (one confirms, one corrects it differently) → both
  captured as distinct records (US2 Acceptance Scenario 2); disagreement is a signal surfaced to a
  later curation pass (US4), never silently resolved by this feature (e.g. by majority vote or
  overwrite).
- The ruleset a confirmation was made against is later recompiled to a new `ruleset_sha256` → the
  confirmation stays pinned to the exact `(loan_id, ruleset_sha256, check_id)` it was made against;
  it is historical provenance for *that* ruleset version, never silently re-mapped to a newer one.
  A recompiled check that changed meaning gets its own fresh confirmations under its own hash.
- The loan's underlying extracted facts are later re-processed (Touchless re-runs, corrects an
  extraction) after a confirmation was captured → the confirmation remains valid evidence of what the
  SME actually judged *at that time*, because this feature pins an immutable snapshot of the
  `CanonicalLoan` facts as evaluated at confirmation time (FR-005) — it does not silently re-attach to
  whatever the loan's data looks like now.
- An SME confirms a `PASS` with no `review_reason` at all (a clean, auto-cleared check, not an
  exception) → still capturable. This feature does not restrict itself to `NEEDS_REVIEW`-tagged
  checks only; a spot-check confirmation on an auto-cleared check is equally valid corpus material
  (a machine-correct `PASS`, human-ratified, is exactly the kind of GOLDEN-tier regression case that
  proves a future ruleset change didn't quietly break something that used to work).
- What if a reviewer has *zero* corrections across an entire session (only confirms)? → Not blocked,
  but named as a real, honest risk (Risks, below) — the same "zero-edit-distance sign-off theater"
  smell `002a`'s own review process names for compile-time review applies structurally here too; this
  feature surfaces the confirm-vs-correct ratio per reviewer/session rather than treating an
  all-confirm session as proof of engine correctness.
- No `reviewer_id`/auth system exists yet in this pilot-stage codebase → accepted as a free-text
  string for the pilot (Assumptions); a real identity/auth system is later, industrial-build-out
  scope (Monish's team), not this feature's to build.
- What triggers promotion of a corpus entry into `005`'s permanent GOLDEN panel? → Deliberately left
  as an explicit, separately-invoked curation step this feature ships the *mechanism* for (FR-007)
  but does not itself define *who* runs it or *when* — named honestly as an open item, mirroring
  `005`'s own named-not-solved "what triggers a ruleset version bump" gap.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: WHEN an SME reviewer takes a `CONFIRM` or `CORRECT` action on a specific `CheckResult`
  from a completed `RunResult` THE system SHALL capture a `LabelConfirmation` record naming
  `loan_id`, `ruleset_id`, `ruleset_version`, `ruleset_sha256`, `check_id`, the check's
  `original_status`, the `action` taken, and — for `CORRECT` — the `corrected_status`.
- **FR-002**: The system SHALL append every captured `LabelConfirmation` to an immutable, hash-chained
  log (reusing `p0/qc_engine/audit.py`'s proven `GENESIS`/`_digest` chain mechanics as a sibling, not
  by modifying `AuditLog` itself) such that tampering with any historical confirmation record is
  detectable by a chain-verification pass, mirroring `007`'s `verify_chain()` proof.
- **FR-003**: IF `action == "CORRECT"` THEN THE system SHALL require a non-empty `corrected_status`
  before the record may be captured — an "I disagree but didn't say what it should be" reaction is
  rejected at capture time, never silently stored as an ambiguous label.
- **FR-004**: The system SHALL persist every captured `LabelConfirmation` into a durable, append-only,
  flat-file label corpus (no database for this artifact, consistent with this project's flat-file
  convention for human-inspectable, git-diffable records — e.g. `002a`'s own `sme_review_package.md`
  precedent) that survives process restarts and grows monotonically as more confirmations are
  captured — never truncated, never rewritten in place.
- **FR-005**: The system SHALL pin a `LabelConfirmation` to an immutable snapshot of the
  `CanonicalLoan` facts as evaluated at confirmation time (a `LoanSnapshot`, not merely a `loan_id`
  reference) — so a later re-extraction or correction of the loan's underlying data does not silently
  change what a human actually judged, mirroring the "previously known, pinned" discipline `005`'s
  own GOLDEN tier already establishes for its fixed panel.
- **FR-006**: The system SHALL provide a pure, deterministic conversion function from a
  `LabelConfirmation` (either action) into `005`'s scorer-compatible `(CanonicalLoan,
  expected_verdicts, provenance)` triple (`005` spec.md FR-010) with **zero changes to that scorer's
  signature** — `expected_verdicts` for a `CONFIRM` equals the check's original machine status;
  for a `CORRECT`, it equals the SME's `corrected_status`. `provenance` MUST distinguish
  `"sme-confirmed"` and `"sme-corrected"` from `005`'s existing `"constructed-by-mutation"`.
- **FR-007**: The system MUST NOT auto-promote a captured `LabelConfirmation` directly into `005`'s
  version-controlled `golden_panel.py` — promotion into the permanent regression panel MUST be a
  separate, explicitly-invoked, human-curated step naming which corpus entries are promoted (mirrors
  `005`'s own FR-007 "an unacknowledged flip blocks promotion" discipline: an unreviewed confirmation
  never silently becomes permanent ground truth).
- **FR-008**: WHERE no dedicated review UI (`008`) exists yet, THE system SHALL expose the capture
  mechanism as a minimal, headless callable (a plain function and/or CLI entry point) that any
  interim manual review process can invoke starting with the very first pilot loan — its contract
  MUST NOT assume any particular caller (a future `008` screen, a CLI script, and a test harness all
  call the identical entry point).
- **FR-009**: The system MUST NOT implement cross-customer learning — aggregating confirmations
  across different lender customers/tenants into one shared corpus is gated on a data-rights clause
  (roadmap Tension Q2, an external contract dependency) and is explicitly out of scope. Where more
  than one customer/tenant corpus exists, each MUST remain segregated by tenant/engagement identity;
  this feature does not merge them.
- **FR-010**: This feature MUST NOT build the exception-review/queue UI itself (`008`) — the capture
  mechanism attaches to whatever minimal interaction surface exists today; the full review queue
  experience is a separate, later feature that will call into this one.
- **FR-011**: Every captured `LabelConfirmation` MUST be traceable end-to-end back to its originating
  run's real entry in `007`'s `AuditLog` (naming that entry's `record_hash`) — a confirmation with no
  provable link to the machine verdict it confirms/corrects is not admissible provenance and MUST NOT
  be captured.
- **FR-012**: Label capture MUST be a pure function of already-computed engine output plus the
  human's explicit input — no re-running the engine, no new LLM/network call inside the capture path
  (Principle I); the record's timestamp MUST be injected by the caller (mirroring `audit.py`'s
  `signed_at` convention), never read from wall-clock inside deterministic code.
- **FR-013**: The corpus SHALL be queryable/filterable by `action` (`CONFIRM` vs `CORRECT`) and by
  `check_id` — a future curation pass or `012` (real-loan eval) needs to isolate "loans a human
  explicitly said the machine got wrong" as its own distinct signal, not blended anonymously into
  "all confirmations."
- **FR-014**: WHEN two or more `LabelConfirmation`s are captured against the identical
  `(loan_id, ruleset_sha256, check_id)` coordinate with differing actions or corrected statuses THE
  system SHALL retain all of them as distinct records — disagreement MUST NOT be merged, averaged, or
  silently overwritten by a "most recent wins" rule.
- **FR-015**: The system SHALL provide a rebuild function that regenerates the flat-file `LabelCorpus`
  (FR-004) from scratch by replaying every record in the `ConfirmationLog` (FR-002) from `GENESIS`
  forward — added 2026-07-27, constitution-alignment audit, to close the dual-write gap FR-004's
  design rationale now names explicitly: since the `ConfirmationLog` is the sole source of truth, a
  `LabelCorpus` write that fails or falls out of sync MUST be recoverable by this replay, never by
  re-deriving lost data from elsewhere or accepting a permanently incomplete corpus.

### Key Entities

- **LabelConfirmation** (new): the atomic captured event — `confirmation_id`, `loan_id`,
  `ruleset_id`/`ruleset_version`/`ruleset_sha256`, `check_id`, `original_status`, `action`
  (`"CONFIRM"` | `"CORRECT"`), `corrected_status` (required iff `action == "CORRECT"`),
  `reviewer_id` (free-text for pilot, per Assumptions), `reviewer_note` (optional), a link to the
  originating `007` `AuditLog` `record_hash` (FR-011), a link to the `LoanSnapshot` (FR-005), and an
  injected `confirmed_at` (never wall-clock, FR-012).
- **LoanSnapshot** (new): an immutable, hashed copy of the `CanonicalLoan` facts as they existed at
  confirmation time — decouples a confirmation's validity from any later re-extraction of the same
  loan (FR-005).
- **ConfirmationLog** (new): the hash-chained, tamper-evident append log of `LabelConfirmation`
  records — a sibling to `007`'s `AuditLog`, reusing its `GENESIS`/`_digest` primitives, not a
  modification of it (FR-002).
- **LabelCorpus** (new): the durable, append-only, flat-file, growing collection of captured
  `LabelConfirmation` + `LoanSnapshot` records — the artifact the roadmap calls "compounding the
  corpus" (FR-004). Single source of truth; `ConfirmedLabelCase` (below) is a derived view over it,
  never a second copy.
- **ConfirmedLabelCase** (new, derived — not separately persisted): the `(CanonicalLoan,
  expected_verdicts, provenance)` triple `005`'s scorer actually consumes, computed on demand from a
  `LabelConfirmation` + its `LoanSnapshot` (FR-006).
- **CheckResult / RunResult** (existing, `p0/qc_engine/engine.py`) and **AuditLog** (existing,
  `p0/qc_engine/audit.py`, implemented per `007`): read-only inputs this feature references and links
  to; unmodified by this feature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% round-trip fidelity: capturing N `LabelConfirmation`s across M loans in one process
  and re-reading the corpus from a fresh process yields exactly N records with every field intact —
  zero data loss, zero duplication (US2).
- **SC-002**: A deliberate tampering test against the `ConfirmationLog`'s chain (mutating one
  historical record's payload) is detected 100% of the time by chain verification — mirroring
  `007`'s own `AuditLog.verify_chain()` test discipline (US1 Acceptance Scenario 3).
- **SC-003**: 100% of constructed `CONFIRM` and `CORRECT` records convert to `005`'s scorer-compatible
  triple and score without error through `005`'s actual scorer function, with zero changes to that
  function's signature — proving the FR-010-in-`005` seam this feature targets is genuinely closed,
  not merely asserted (US3).
- **SC-004**: 100% of attempted `CORRECT` captures with an empty/missing `corrected_status` are
  rejected at capture time (FR-003) — never silently stored as an ambiguous label.
- **SC-005**: Zero unintended promotion: across any number of captured confirmations with no explicit
  promotion step invoked, `005`'s `golden_panel.py` remains byte-identical to its pre-capture state
  (US4 Acceptance Scenario 1).
- **SC-006**: Zero regression on the existing suite: `p0/tests/test_p0.py` and `007`'s existing
  `AuditLog` behavior/tests pass unmodified after this feature ships — this feature adds a sibling
  mechanism, it does not alter `audit.py`'s existing schema or behavior.

## Assumptions

- **Reuse the audit primitives, add a sibling, don't reshape 007.** `AuditLog.append()` is typed
  specifically to a `RunResult`; rather than widening its signature (which would touch an
  already-implemented, already-proven feature) or writing directly into its table, this feature
  imports `audit.py`'s `GENESIS`/`_digest` constants into a new, parallel `ConfirmationLog` class that
  cross-references `AuditLog` records by hash value (FR-011). This is a deliberate minimal-touch
  choice, matching the precedent `004`/`005` both set of leaving already-working code alone.
- **Dual persistence is deliberate, not redundant — but the two writes are NOT both required to
  succeed (revised 2026-07-27, constitution-alignment audit).** The `ConfirmationLog` (hash chain,
  FR-002) is the single source of truth for a captured confirmation; the flat-file `LabelCorpus`
  (FR-004) is a **derived, rebuildable projection** of it, not an independent write that must land
  atomically alongside the log. A capture is considered complete the moment the `ConfirmationLog`
  append succeeds — the `LabelCorpus` write happens next, and if it fails, that is a stale/incomplete
  projection, never a lost confirmation, because it can always be regenerated by replaying the
  `ConfirmationLog` from `GENESIS` forward (FR-015). This avoids building distributed-transaction
  machinery to make two independent files land together, and matches `007`'s own "chain is truth, flat
  artifact is a queryable view" split more precisely than treating both writes as equally load-bearing.
- No `reviewer_id`/auth system exists in this pilot-stage codebase; `reviewer_id` is accepted as a
  free-text string for now. A real identity/access system is later, industrial-build-out scope
  (`CLAUDE.md`'s "Where This Fits" — Monish's team), not built here.
- `008` (the review UI) does not exist and is not built by this feature (FR-010) — the headless entry
  point (FR-008) is this feature's honest substitute for a real interaction surface during pilot; any
  interim manual process (a CLI prompt, a spreadsheet-driven script mirroring `002a`'s own
  `build_review_package.py`/`apply_decision_rule.py` shape) can invoke it starting with the first
  pilot loan, per the roadmap's explicit "wire it early" mandate.
- What concretely triggers promotion of a corpus entry into `005`'s permanent `golden_panel.py` (who
  runs it, how often) is intentionally left undefined by this feature — it ships the promotion
  *mechanism* (FR-007) as a callable step, not a scheduled or automatic workflow, mirroring `005`'s
  own honest "no real trigger event yet" admission about `Ruleset.version` bumps.
- Cross-customer aggregation (FR-009) is a real, named future capability the roadmap itself flags as
  gated on a data-rights clause (Tension Q2) — this feature does not attempt a partial or provisional
  version of it; each tenant's corpus is fully segregated until that contract dependency resolves.
- `012-real-loan-distribution-eval` depends on this feature (per the roadmap's own sequencing,
  §011→§012), not the reverse — this feature does not require `012` or any real expert-labeled loan
  to exist; SC-003's scoring proof uses constructed stand-in confirmations, the same pattern `005`'s
  own User Story 5 already establishes for its own FR-010 proof.

## Risks

- **MEDIUM — confirmation is not proof of ground truth; an all-confirm reviewer session can look
  identical to a genuinely correct engine and to a rubber-stamping one.** This is the runtime analog
  of `002a`'s own named "zero-edit-distance is a sign-off-theater smell, not a win" finding. Mitigation:
  this feature surfaces the confirm-vs-correct ratio per reviewer/session in the corpus's queryable
  metadata (FR-013) so a curation pass can flag suspiciously all-confirm sessions for a second look —
  it does not attempt to algorithmically detect rubber-stamping itself, which is out of scope.
- **MEDIUM — the GOLDEN-panel promotion step (FR-007) has no defined owner or cadence.** Named
  honestly, not solved, mirroring `005`'s own equivalent risk about `Ruleset.version`. Mitigation:
  ship the promotion step as a directly-callable, auditable function now; a real curation
  workflow/cadence is a later ops decision, not a blocker to shipping the mechanism.
- **LOW-MEDIUM — without `008`, the headless entry point may see near-zero real usage during
  pilot**, since there is no UI affordance nudging a reviewer to click "confirm." Mitigation: per the
  roadmap's own "wire it early" framing, the intent is to attach the headless call to *whatever*
  minimal interim review process exists (even a manual spreadsheet-driven script) rather than wait
  for `008` — the mechanism working in isolation, proven by this feature's tests, is the actual
  deliverable; driving real pilot adoption of it is an operational follow-up, not a build gap.
- **HIGH (external, not this feature's to resolve) — cross-customer learning is explicitly walled off
  by a data-rights clause (Q2) that has not been signed.** Named per FR-009/Assumptions so it is never
  mistaken for a solvable engineering gap; it is a contract dependency the roadmap already tracks
  separately.
