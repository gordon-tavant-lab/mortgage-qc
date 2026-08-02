# Gold Ruleset Integration Plan — 2026-07-31

**Input:** `storage/rules/gold/` — the newly-compiled FNM conventional, post-closing gold rule
set (266 cards / 1,106 checks / 221 atomic rules, Selling-Guide-cited, `status: draft`
throughout). Relocated by Gordon out of `storage/rules/` root, which spec
`019-workbook-first-rule-authoring` reserves for SME-authored signed ruleset output
(`storage/rules/vN.json`) — that path is free again.

**Decision (Gordon, 2026-07-31):** target engine is **Pipeline B — `p0/qc_engine/`**. It's what
`frontend/` is already mocked against, and its `engine.py` already produces a real `NEEDS_REVIEW`
verdict (missing data / low confidence / uncited-pass), so the "honest abstention" contract this
gold set needs is already structurally present — no engine rewrite for that part.

**Existing state this plan builds on, not replaces:**
- `frontend/` already has a real route/block/check UI shell (`RouteList`, `RouteDetail`,
  `RoutesFlow`, `BlockDetail`, `LoanQueue`, `LoanDetail`, `ExceptionReview`, `ApplyView`,
  `ImportAndSignView`) on mock data, an open PR (`worktree-kayla-mockup`, PR #2), and a live
  6-item action-items backlog (`docs/frontend/ACTION-ITEMS-2026-07-30.md`).
- `docs/frontend/RULE-TO-CHECK-UI-MODEL.md` defines the target `Check`/`CheckResult`/`Block`/
  `Route` UI shapes. Written primarily against Pipeline A (SHACL), but the field-level contract
  (citation model, 5-status verdict, block coverage counts, exception-description-as-primary-label)
  is engine-agnostic and still applies.
- `frontend/src/lib/types.ts`'s `Check` already mirrors `p0/qc_engine/ruleset.py`'s `Check` closely
  — `grounding: GuidelineCitation[]` is *already* the exact shape of the gold set's `citations`
  array. That's the one field that needs zero redesign.
- Pipeline A (`src/shacl_pilot`) and Pipeline B were already flagged as unreconciled
  (`output/RULE-BACKLOG-COMPREHENSION-2026-07-30.md`) — out of scope here; this plan only touches B.

---

## Phase 0 — Reconciliation prerequisite (before writing any converter)

`p0/compile_runs/run_010_post_closing_only/ruleset.json` already contains FNM-conventional
checks compiled from the *same* AMQ workbook by the older Pipeline B compiler. The gold set is
almost certainly a partial re-derivation of that same slice, at higher fidelity (real Selling
Guide citations vs. whatever `compile_llm.py` produced before). **Do not simply add the gold set
on top — that produces duplicate/conflicting checks for the same `exception_code`.**

1. Build a mapping script keyed on `(question_code, exception_code)` — same anti-pattern the
   gold README already warns about for `card_id` drift — to identify which `run_010` checks the
   gold set's 266 cards supersede.
2. Produce a coverage report: for each gold card, does an equivalent already exist in `run_010`?
   Flag net-new vs. supersedes vs. no-equivalent-yet.
3. Decision this produces: gold set **replaces** its matching slice of `run_010` for FNM
   conventional; `run_010`'s other-program checks (FHA/VA/RHS/Freddie) are untouched and remain
   the only coverage those programs have until they get the same compile treatment.

## Phase 1 — Deterministic converter (gold → `ruleset.py` `Check`)

New script, no LLM involved (pure mapping, consistent with Non-Negotiable #1 — the gold set was
already LLM-compiled once; this step must not re-invoke one):

`p0/qc_engine/compiler/import_gold_ruleset.py`

| Gold `check_type` | Target `Check.kind` | Notes |
|---|---|---|
| `doc_presence` | `predicate` (`is_present`) | direct |
| `doc_completeness` | `predicate`, one per required field | a completeness card may expand to N checks |
| `threshold_eligibility` | `ratio_threshold`, `ratio="field_value"` | direct |
| `computation` (LTV/DTI/CLTV subset) | `ratio_threshold`, `ratio="ltv"\|"dti"` | direct |
| `computation` (other formulas: gross-ups, ARM quals, PITIA, points & fees) | — | **no engine primitive exists yet** — route to Phase 2 backlog, do not silently mis-map to `ratio_threshold` |
| `cross_doc_consistency` | `agree_categorical`/`agree_numeric`/`agree_doc_categorical`/`agree_doc_numeric` | pick by data type + whether a system source exists |
| `scripted_review` | `predicate` over an intentionally-unset checklist fact | resolves `NEEDS_REVIEW` today via `engine.py`'s existing unknown-predicate path (~line 339) — **no engine change needed**, just correct compilation |
| `routing_context` | not a `Check` | becomes a fact definition other checks' `applies_if` reads |
| `date_window`, `list_screening`, `reverification` | new placeholder kind → deterministic `NEEDS_REVIEW` | never FAIL/PASS on a kind the engine can't yet execute — see Phase 2 |

Also:
- `applicability.always/all_of/any_of` → `Check.applies_if` (already the same `{field, operator,
  value}` shape — direct copy).
- `citations` → `grounding: GuidelineCitation[]` (direct copy, per above).
- Preserve the gold set's `check_type` on the converted `Check` as a new **audit-only** field
  (`source_check_type`) so the richer taxonomy isn't silently lost where the `kind` mapping is
  lossy (e.g. two different gold types both landing on `predicate`).
- Preserve `rule_id`/`card_id` in `question_code`/a new locator field for full traceability back
  to `storage/rules/gold/data/`.

**Gate before this is trustworthy** (Standing Gates, CLAUDE.md): re-run
`p0/fixtures/from_docs/verify_against_defects.py` (25/25), the coverage gate
(`p0/compile_runs/run_016_coverage_gate/build_and_run.py` — extend it to also check the gold
set's `evidence[].field` values against `field_catalog.json`'s 446 entries, since the README
flags `evidence` as an unverified draft scaffold), and the loan01 defect-regression pytest gate.
Output: a new signed `result/rules/*.json` artifact via `ruleset.py`'s `Ruleset`/
`RuleProvenance`/hash model — same "compile once, sign, run by hash" discipline as everything
else in this repo.

## Phase 2 — Engine extensions (only what's genuinely missing, incremental)

Prioritize by check count (taxonomy distribution, §"Check-type distribution" in
`storage/rules/gold/reports/compile-stats.md`):
1. **`date_window`** kind (62 checks, 5.6%) — two dated fields vs. a bound, business/calendar-day
   semantics. Self-contained, no external dependency.
2. **Computation formula backlog** (gross-up %, ARM qualifying rate, PITIA, points & fees caps) —
   each a `money.py` Decimal formula; prioritize by which atomic rules in Income/Assets need them
   (already flagged in `rules_atomic.json`).
3. **`list_screening`** (20 checks, 1.8%) — needs a versioned reference-dataset loader (OFAC/GSA/
   AQM/plan-matrix lists) as a new engine dependency. Flag as its own follow-up track — real
   external-data-sourcing work, not just engine logic.
4. **`reverification`** (24 checks, 2.2%) — third-party re-pull vs. original; likely a new named
   `source` in `CanonicalLoan`'s source map (`"reverif"`), evaluated via existing `agree_*` kinds
   once populated. The re-pull itself is a vendor-integration question (Known Blocker territory),
   not engine logic — do not block Phase 1 on it.

Note: `doc_presence` + `doc_completeness` + `threshold_eligibility` + `cross_doc_consistency` +
`scripted_review` already cover **~80% of the 1,106 checks** and need **zero** engine changes —
Phase 1 alone ships real coverage for most of the gold set.

## Phase 3 — Frontend wiring (extends the Kayla-mockup PR, does not restart it)

1. `frontend/src/data/mockData.ts` → real loader reading the Phase 1 output (`result/rules/*.json`)
   — this is the same "loader function" shape action item #5 already planned for loan data;
   apply the identical pattern to rules.
2. Two small `types.ts` additions: `checklist?: string[]` on `Check` (so `scripted_review`-sourced
   checks render their criteria for a reviewer to answer in `ExceptionReview`), and
   `sourceCheckType?: string` (audit passthrough, per Phase 1's `source_check_type`).
3. `Block.counts` (already spec'd in `RULE-TO-CHECK-UI-MODEL.md` §5): extend from
   `{compiled, notCompiled}` to also carry `needsEngineWork` (checks converted but blocked on a
   Phase 2 kind) — the SME must see honest coverage, never a binary compiled/not.
4. **Loan-type scope honesty**: the gold set is FNM-conventional only. `LoanQueue`/`RouteList`
   must show zero available checks for FHA/VA/USDA/Freddie routes rather than falling back to
   mock data that implies coverage that doesn't exist yet.
5. Sequencing against the existing 6-item backlog (`docs/frontend/ACTION-ITEMS-2026-07-30.md`):
   items 1a/1b/6/3 are independent of this plan and can proceed in parallel; item 5 (real loan
   *fact* data, blocked on Sendhil) is complementary, not blocking — this plan wires real *rules*,
   item 5 wires real *loan data*; both are needed for a fully real run but neither blocks the other.

## Phase 4 — The QC audit process (operational flow, not just engine code)

1. **Apply** — SME assigns the "FNM Conventional Post-Closing" route (currently the only one
   with real coverage) to a loan → engine loads the signed ruleset by hash → runs deterministically
   → produces an `AuditRun` with full 5-verdict counts (PASS / FAIL / NOT_APPLICABLE / NEEDS_REVIEW
   / NOT_COMPILED).
2. **Auto-clear** — PASS + NOT_APPLICABLE collapse automatically (Non-Negotiable #4's "auto-clear
   the obvious"); only FAIL and NEEDS_REVIEW reach the reviewer.
3. **Exception Review** — reviewer works the FAIL/NEEDS_REVIEW queue, including answering
   `scripted_review` checklist items inline (new surface, needs Phase 3.2's `checklist` field),
   each resolved as UNRESOLVED/OVERRIDDEN/ESCALATED/SYSTEM_CORRECTED.
4. **Promotion gate (new, currently doesn't exist anywhere in the codebase)** — every gold card
   is `status: draft`. Before Phase 4.1 can run on a real loan, something must move cards through
   `draft → verified → active`. Recommend starting with a **CLI/script gate** (fast, unblocks
   everything else) rather than waiting on spec 019's full authoring UI — the authoring UI can
   subsume this later without changing the artifact shape.
5. **Standing gates as a documented pre-flight step** — re-run the four gates (25/25, coverage,
   loan01 regression, and the extended evidence-field check from Phase 1) any time the ruleset is
   recompiled. Make this a checklist step in the process doc, not tribal knowledge.

---

## Recommended sequencing

Phase 0 (reconciliation report) → Phase 1 (converter + gates + signed artifact) → Phase 3.1–3.4
(frontend wiring, parallel with Kayla items 1a/1b/6/3) → Phase 4.4 (promotion gate script) →
Phase 2 (engine extensions, incremental, prioritized by check count) → full Phase 4 loop.

Phase 0 and Phase 1 are read-only/deterministic analysis-and-conversion work — safe to start
immediately without further design decisions. Phase 2's `list_screening`/`reverification` tracks
need their own scoping (reference-dataset sourcing, vendor re-pull integration) before estimating.
