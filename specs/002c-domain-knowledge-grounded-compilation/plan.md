# Implementation Plan: Domain-Knowledge-Grounded Rule Compilation & Intake Workflow

**Branch**: `002c-domain-knowledge-grounded-compilation` | **Date**: 2026-07-20 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/002c-domain-knowledge-grounded-compilation/spec.md`

## Summary

Four new mechanisms, each independently testable, composing into the intake workflow (spec.md US5):
a versioned, per-program, section-fingerprinted knowledge base (`knowledge_base.py`); grounding
retrieval against it, wired into `002b`'s existing `compile_llm.py`; a multi-model judge panel
(`judge_panel.py`) that escalates on any disagreement rather than majority-voting; and orchestration
tying them into the 10-step intake sequence. Live-API-calling code (KB-build-from-research,
judge-panel model calls) follows `002b`'s own established precedent: kept **outside** the fast
pytest suite, tested via synthetic fixtures for the deterministic logic (versioning, diffing,
retrieval ranking, escalation rules) and exercised for real only via a separate script.

## Technical Context

**Language/Version**: Python 3.9-compatible (project-wide constraint).
**Primary Dependencies**: None new. No vector database, no embeddings library — the KB is
curated/small-scale by construction (a handful of regulation summaries and guide excerpts per
program, not a bulk document corpus), so retrieval is a simple, fast, dependency-free keyword-
overlap ranking over `KBSection` text, not a similarity-search index. Revisit only if a real KB
build shows this doesn't scale — not assumed needed now (YAGNI, matching this project's existing
minimal-dependency discipline).
**Storage**: New JSON files under `p0/qc_engine/compiler/knowledge_base/<program>/` — one file per
corpus version (e.g. `FHA/v1.json`, `FHA/v2.json`), never overwritten in place, mirroring how
`Ruleset`/`FieldCatalog` are versioned and hashed today. No database.
**[SUPERSEDED 2026-07-26 — post-hoc note, flagged by spec audit]**: the storage layer described
above was replaced after implementation, in two moves this plan never recorded: (1) the KB moved to
a central `storage/knowledge_base/` directory at repo root (user-directed, 2026-07-25), with the
JSON layout retained only as a legacy fallback (`storage/knowledge_base/<program>/v<n>.json` — the
FHA stub lives there now); (2) a **SQLite store** (`storage/knowledge_base/kb.sqlite3`, via the new
`p0/qc_engine/compiler/knowledge_base_store.py` — `init_db`/`save_to_db`/`list_versions`/
`load_from_db`, tested in `p0/tests/test_knowledge_base_store.py`) became the primary lookup
(`compile_llm.py` checks it first), holding the real ingested Fannie Mae Selling Guide corpus (416
sections via `ingest_selling_guide.py`, deterministic PDF parse, signed with an honest
`NOT-A-REAL-SME-pending-kayla-review` placeholder). `retrieve()` was also upgraded from plain
keyword-overlap to IDF-weighted overlap (still pure/offline — FR-005 preserved). "No database" is
therefore no longer a true description of the shipped system; callers still see only
`KnowledgeBaseCorpus`/`KBSection` objects, so the interface contract this plan specified is intact.
**Testing**: New `p0/tests/test_knowledge_base.py` (versioning, section-diff-on-update, sign-off
gating, retrieval ranking — all pure/fast, no API calls) and `p0/tests/test_judge_panel.py`
(escalation-vs-auto-approve logic against synthetic `JudgeVerdict` fixtures — no live model calls,
same precedent `002b`'s `test_compile_batch_produces_n_valid_check_drafts_no_new_fields` set for
`CompiledCheckDraft`). Live Bedrock-calling code (`build_corpus_from_documents`'s real-research
variant, `judge_check`'s real model calls) is exercised via a standalone script outside the pytest
suite, exactly as `compile_row`/`compile_batch` already are.
**Target Platform**: Local execution + Bedrock API calls at KB-build time and judge time only —
never inside `qc_engine.engine.run` (Principle II, unchanged).
**Project Type**: Four new modules + one existing-file extension (`compile_llm.py`).
**Performance Goals**: N/A for the deterministic logic (versioning/diffing/ranking are all small,
in-memory operations over a curated, non-bulk corpus). Judge-panel cost is 2 extra model calls per
compiled row — deferred to a real pilot batch to measure (spec.md FR-010), not modeled here.
**Constraints**: FR-005 (zero live-search/research-agent calls in the per-row compile path) is
enforced by construction — `compile_llm.py`'s grounding step only ever calls
`knowledge_base.retrieve()`, a pure in-memory function, never a network call. FR-008 (any judge
disagreement escalates, never majority-vote auto-approve) is enforced by `judge_panel.py`'s
escalation function accepting no "N-of-M" parameter — unanimous-or-escalate is the only mode this
version implements, matching the conservative posture already agreed.
**Scale/Scope**: This increment builds the **mechanism** end-to-end (KB versioning, grounding,
judging, orchestration) and proves it with a small, real, hand-curated KB (one program, a handful of
real regulation excerpts) — not the full 6-program corpus built from live research agents, which is
a separate, larger, cost-incurring one-time operation flagged for explicit go-ahead before running
(same discipline as the real-rule-compile decision earlier this session).

## Constitution Check

*GATE: evaluated against `.specify/memory/constitution.md` v1.1.1.*

| Principle | Status | Note |
|---|---|---|
| I — Determinism of the correct computation | ✅ PASS | KB versioning/diffing/retrieval-ranking are pure functions over stored text — no float, wall-clock, or network in the deterministic path. |
| II — Compile, then run | ✅ PASS | Grounding and judging both happen at compile time only (`compile_llm.py`/`judge_panel.py`); `qc_engine.engine.run` is untouched — zero LLM calls added to the runtime evaluation path. |
| III — Eval is foundational | ✅ PASS | SC-001–006 make sign-off gating, version-anchoring, zero-live-calls-in-compile-path, and the "measure don't assume" auto-approve rate all explicit, testable gates. |
| IV — Build the core, assume the periphery | ✅ PASS | Extends the compile pipeline core (already the product's own "this is the product" surface per CLAUDE.md); does not touch extraction or LOS integration. |
| V — Source independence | N/A this feature | Grounding informs *interpretation* of a rule's text, not the doc-vs-system reconciliation comparison — untouched. |
| VI — Configurable by non-technical users | ⚠️ PASS, named limitation | The KB's SME sign-off gate (US1) is real and enforced, but the retrieval-ranking logic and judge-panel escalation rule are still Python code, not SME-editable config — same honest boundary `004`/`010a` already named for their own small lookup tables. |
| VII — Configuration is authored data | ✅ PASS | Every `KBSection` traces to a real source document + citation; every compiled check's `GroundingRecord` is inspectable data, not an opaque embedding. |

**One named limitation (Principle VI), consistent with `004`/`010a`'s own precedent — not a
violation.**

## Project Structure

### Documentation (this feature)

```text
specs/002c-domain-knowledge-grounded-compilation/
├── spec.md
├── plan.md                  # This file
└── tasks.md                 # Phase 2 output
```

### Source Code (repository root)

```text
p0/qc_engine/compiler/
├── knowledge_base.py          # NEW: KBSection, KnowledgeBaseCorpus dataclasses;
│                              #   build_corpus()/update_corpus() (section-level diff versioning);
│                              #   sign()/is_usable() (SME sign-off gate, mirrors RuleProvenance);
│                              #   retrieve() (pure keyword-overlap ranking, top-N sections).
├── judge_panel.py             # NEW: JudgeVerdict dataclass; judge_check() (real Bedrock calls,
│                              #   kept outside the fast test suite); escalate_or_approve()
│                              #   (pure logic: unanimous agreement -> auto-approve, ANY
│                              #   disagreement/low-confidence -> escalate, FR-008).
├── compile_llm.py             # MODIFIED: CompiledCheckDraft gains a `grounding` field
│                              #   (GroundingRecord); compile_row() calls
│                              #   knowledge_base.retrieve() (if a signed KB exists for the row's
│                              #   program) before building the compile prompt, falls back to
│                              #   today's ungrounded behavior otherwise (FR-006).
└── knowledge_base/            # NEW data directory: <program>/v<N>.json corpus files.

p0/tests/
├── test_knowledge_base.py      # NEW — US1/US2 coverage: sign-off gating, section-diff
│                              #   versioning, version-anchoring after update, retrieval ranking.
└── test_judge_panel.py         # NEW — US4 coverage: unanimous-agreement auto-approve,
│                              #   any-disagreement escalation, reasoning preserved on escalation.

p0/experiment_002c/             # NEW (mirrors experiment_002a's precedent): a standalone,
├── build_fha_kb.py             #   NOT-in-pytest script proving the real mechanism against a
│                              #   small, real, hand-curated FHA knowledge base (a handful of real
│                              #   regulation excerpts) — the "real proof" companion to the fast,
│                              #   synthetic-fixture unit tests above.
```

**Structure Decision**: Two new modules (`knowledge_base.py`, `judge_panel.py`) rather than folding
into `compile_llm.py` — same precedent as `002b`'s own `catalog_screen.py`/`consistency.py`/
`pattern_flags.py` split: each new capability is independently testable and independently
extensible. `compile_llm.py` gains only the minimal wiring (one new dataclass field, one new
retrieval call before the existing prompt-build step) — its own shape stays otherwise unchanged.

## Complexity Tracking

*No entries — the one named limitation (Constitution Check, Principle VI) is a scope boundary
consistent with prior specs' own precedent, not a violation requiring justification.*

## Implementation Notes (post-hoc — what was actually built)

Implemented per `tasks.md` (T001–T036 complete). **One real correction, caught and disclosed, not
smoothed over**: the first pass at US5's orchestration (`build_fha_kb.py`) stopped after the judge
panel and was marked `T032` complete without actually reaching the referential-integrity screen,
exception-queue routing, or real `Ruleset` sign-off — spec.md US5's own acceptance scenario requires
all of it ("a signed, version-locked ruleset with full provenance..."). Caught by a direct
code-vs-spec check (grep for `validate_referential_integrity`/`assemble_ruleset` in the proof
script — absent), not by re-reading my own summary. Fixed by rewriting the inline script into a
real `run_intake_demo()` function that runs the full 10-step sequence, and by persisting
`p0/experiment_002c/RESULTS.md` (also missing on the first pass — `002a`'s own precedent has one).

- **`knowledge_base.py`**: `KBSection`/`KnowledgeBaseCorpus`, `build_corpus`/`update_corpus`
  (section-level diff versioning), `sign`/`is_usable` (mirrors `RuleProvenance`'s shape exactly),
  `save`/`load` (one JSON file per version), `retrieve` (pure keyword-overlap ranking — confirmed by
  grep, zero `boto3`/network references anywhere in this module).
- **`judge_panel.py`**: `JudgeVerdict`, `escalate_or_approve` (unanimous-and-confident-only, no N-of-M
  path — proven by a dedicated test that a 2-of-3 majority still escalates), `judge_batch_result`
  (preserves every judge's individual reasoning), `judge_check` (the one real-Bedrock-call function,
  kept out of the fast suite). **Default judge pair confirmed accessible in this project's own AWS
  account** (verified via real `converse()` calls earlier this session): `mistral.mistral-large-3-
  675b-instruct` and `openai.gpt-oss-safeguard-120b` — chosen for genuine family diversity from the
  compiler (Claude) and from each other, plus the safeguard model's purpose-built fit for compliance
  classification.
- **`intake.py`**: `classify_and_gate` — the one hard, unconditional gate in this feature (US5,
  FR-011); everything else (grounding, judging) degrades gracefully when unavailable, this does not.
- **`compile_llm.py`**: `CompiledCheckDraft` gained `grounding: Optional[GroundingRecord]`;
  `compile_row()` resolves the row's program (reusing `010a`'s `program_gating`), loads a signed KB
  if one exists on disk, retrieves relevant sections, and includes them in the compile prompt under
  a new `grounding_context` field the system prompt explicitly instructs the model to defer to. Falls
  back to `002b`'s original ungrounded behavior with zero errors when no KB exists yet (verified by
  test).
- **Real, end-to-end proof run** (`p0/experiment_002c/build_fha_kb.py`, executed 2026-07-20 — not
  just written, actually run against real Bedrock): built and signed a small, real 2-section FHA
  knowledge base (verbatim HUD Handbook 4000.1 gift-fund excerpts); compiled a real row (Exception
  Code `O-FHA-02257`, verbatim from `demo/rules/*.xlsx`) grounded against it; ran the real 2-judge
  panel. **Result: grounding visibly improved the compile** — the source row's vague "did not include
  all required information" became a compiled check whose `message_fail` enumerates the exact
  required elements (dollar amount, no-repayment statement, donor/borrower names/addresses/phones,
  relationship), traceable directly to the retrieved HUD excerpt, not invented. Both judges
  independently agreed (confidence 0.95, 0.96), each explicitly citing the grounding in their
  reasoning — outcome `AUTO_APPROVED`. This is real evidence the mechanism works, not a synthetic
  test claiming it does.
- **Test count**: 20 new tests (9 `test_knowledge_base.py`, 6 `test_judge_panel.py`, 3
  `test_grounded_compilation.py`, 2 `test_intake_gate.py`). Suite total: **164 passed** (was 144
  before this feature, 128 at this session's start before `010a`). `p0/harness.py`'s digest
  unchanged (`a3f702c12969f7eb657471796c95e2a493d459c4c55663fa8fc18ac31e8c1d09`) — zero regression,
  confirmed directly since this feature touches no `engine.py`/`model.py`/`ruleset.py` code.
  `verify_against_defects.py` still 25/25.
- **Explicitly not done in this increment** (plan.md Scale/Scope, unchanged from the original plan):
  the full 6-program corpus built from live research agents — this remains a separate, larger,
  cost-incurring operation requiring its own explicit go-ahead before running, exactly as scoped.
