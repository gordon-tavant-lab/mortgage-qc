# FNM Post-Closing Gold Rule Set — Handoff README

**Read this file first. It is written for the next LLM agent picking up this project, not for a
human skimming a repo.** It tells you what exists, what it means, what's still open, and exactly
how to extend the pipeline without re-deriving decisions that were already made and verified.

---

## 1. What this project is

A deterministic rules-engine gold set for QC-auditing **Fannie Mae, conventional, post-closing**
mortgage loans. Source material: an ACES Managed-Questionnaire export (`source/amqs-sept-2025-retail.xlsx`,
10,345 rows) and the Fannie Mae Selling Guide (`source/selling-guide-2026-06-03.pdf`, 1,188 pages).
The pipeline turns human-audit questions into machine-checkable rules with:

- a **check-type taxonomy** derived from the data (not imposed), so every rule declares *how* it's
  decided (document lookup vs. recomputation vs. cross-document comparison vs. genuine judgment, etc.)
- **pinned citations** to specific, indexed Selling Guide sections (section ID + effective date),
  never "the guide" in general
- a hard architectural rule: **LLMs are used only at compile time** (to type, cite, and structure
  rules). The **runtime is 100% deterministic** — no rule ever calls an LLM to decide a real loan.
  Ambiguous cases compile to an explicit `REQUIRES_HUMAN_REVIEW` outcome, never a model call.

If you are extending this project, preserve that boundary. It is not a style preference — it's
the reason this rule set is auditable at all.

## 2. Directory map

```
source/                  Original AMQ xlsx + Selling Guide PDF. Read-only, do not edit.
guide/
  index.json              390 Selling Guide sections: {section_id, title, effective_date, page_start,
                           page_end, file, char_count}. THE canonical citation registry — a citation
                           is only valid if its section_id appears here.
  sections/<ID>.txt        Full text of each section (ID with '.' replaced by '_', e.g. B3-3.1-01.txt).
                           Grep this directory to verify a citation actually covers a topic — never
                           cite from memory / guide familiarity.
data/
  cards_all.json           EVERY question card from the xlsx (both Post-Closing and Pre-Funding
                           questionnaires, all investor families FNM/FRD/FHA/VA/RHS/etc.), scope-
                           tagged. Use this if you need to bring in a different route/family later.
  cards_base.json          The locked base scope: Post-Closing, Fannie-cut, live cards only (266).
                           This is what everything downstream is built from.
  by_category/<slug>.json  cards_base.json split by category (16 files) — input to the compile step.
  compiled/<unit>.json     Output of the compile step (see §4). One file per category, EXCEPT the
                           4 largest categories which are split into 2 batches each:
                           fannie-mae-form-1033.b1/b2, product-specific.b1/b2, property-appraisal.b1/b2,
                           underwriting.b1/b2. Always merge batches by simple concatenation — order
                           doesn't matter, card_id is the unique key.
  rules_compiled.json      MERGED, VALIDATED output of all 18 compile units — the deterministic
                           gate's product. This is the file to read if you want "all compiled cards"
                           in one place. Includes a validation_summary block.
  atomic/<category>.json   Atomic (fully decomposed) rules for categories that got flagship-depth
                           treatment. Currently: income.json (140 rules), assets.json (81 rules).
  rules_atomic.json        MERGED, VALIDATED output of all atomic decomposition — read this for
                           "all atomic rules" in one place.
  extract_summary.json     Stats from the deterministic extraction step (counts by scope/category/family).
  validation_report.json   Full hard/soft failure list from the last validate_compiled.py run.
schema/
  rule.schema.json          THE authoritative JSON Schema. $defs.card = card-level shape,
                           $defs.atomicRule = atomic-rule shape. Every compiled/atomic JSON file
                           must validate against this. If you change the data shape, change this
                           file first, then update the two validators.
docs/
  taxonomy.md               THE check-type taxonomy (10 types) with real examples, plus documented
                           base-data quality findings (duplicate cards, scope leaks, etc.). Read this
                           before typing anything — do not invent new types without extending it.
  cards_digest.md            Human-readable digest of all 266 base cards (question + applicability +
                           defect options), generated for the taxonomy derivation pass. Useful as a
                           quick reference, but data/cards_base.json is the source of truth.
  research-d1-3-notes.md    Verified (web + local-guide-grep) facts about the Selling Guide's D1-3
                           post-closing QC chapter structure, sampling rules, timing requirements.
pipeline/                  Deterministic Python scripts. No LLM calls. Run with plain `python3` or
                           `uv run --no-project --with <pkg> python3 <script>` if a dependency (openpyxl,
                           pypdf, jsonschema) isn't in your environment.
  extract_cards.py          xlsx -> cards_all.json / cards_base.json. Re-run only if the source xlsx changes.
  split_guide.py             PDF -> guide/index.json + guide/sections/*.txt. Slow (~5 min, extracts
                           text from all 1,188 pages). Re-run only if the source PDF changes.
  compile_units.json         The 18-unit compile plan (category, card-index slice, output id) used by
                           workflows/compile-remaining.js. Reference if you need to know exactly which
                           cards are in each batch.
  validate_compiled.py       THE compile-level gate. Schema-validates every compiled card, checks every
                           citation resolves in guide/index.json, checks exception_code/severity
                           round-trip fidelity against by_category source, merges everything into
                           rules_compiled.json. Run this after ANY change to data/compiled/*.json.
  validate_atomic.py         Same idea, one level down: gates data/atomic/*.json against schema +
                           citation index + fidelity vs. data/compiled/<category>.json. Merges into
                           rules_atomic.json. Run after any change to data/atomic/*.json.
  decompose_income.py        Reference implementation for atomic decomposition. Read this before writing
                           a decomposer for another category — see §6 for the pattern.
  decompose_assets.py        Second reference implementation — the "no bundles, mostly mechanical
                           promotion" case, contrast with decompose_income.py's "true bundles need a
                           manual citation-override map" case.
workflows/
  compile-remaining.js       The Workflow-tool script that ran the LLM compile+verify pass. Kept for
                           reference / re-run if you need to redo verify or extend to new categories.
                           NOT deterministic — spawns subagents. See §5 for how it works and its
                           current state.
reports/
  compile-stats.md           The stats report: start count, compiled/flagged/failed breakdown with
                           per-card nuance, check-type distribution, decomposition status. Read this
                           for the "what happened and why" narrative — this README is the "how to use
                           the data" reference.
STATUS.md                    Running log of session state, blockers, and resume points. Check the top
                           of this file for the most recent status before assuming anything is stale.
```

## 3. The data model (read `schema/rule.schema.json` for the ground truth; this is the guided tour)

Two shapes exist: **card** (question-level, always produced by compile) and **atomicRule**
(single-check-level, produced by decomposition, currently only for Income + Assets).

### 3.1 Card shape (`$defs.card`)

A card corresponds 1:1 to one ACES question code (`card_id`, e.g. `"PC::O-FNM-15320"` — the `PC::`
prefix means Post-Closing questionnaire, everything after is the ACES `Question Code` verbatim).

Key fields and how to read them:

- **`category`** — one of the 16 ACES category names (`"Income"`, `"Assets"`, `"Property - Appraisal"`,
  etc.), used as the sharding key for `by_category/` and `compiled/`.
- **`applicability`** — the condition under which this rule fires, translated from the ACES SQL
  applicability criteria. `always: true`, or `all_of`/`any_of` arrays of `{field, op, value}`
  conditions over a small closed vocabulary (`Loans.QC_Policy`, `Loans.LoanPurposeType`,
  `Loans.PropertyType`, `Loans.Underwriting_Type`, `Loans.LoanType`, `Loans.AddressState`).
  `source_sql` keeps the original ACES SQL string for audit. `context_flags` lists loan-context
  flags this card's applicability *depends on* (set by `routing_context`-type cards elsewhere —
  see below).
- **`skip_logic_source`** — the raw ACES answer-dependent skip logic, when present (e.g. a card only
  fires if a sibling "income type" question was answered "Rental").
- **`defect_options`** — the actual checks. Each has: `response` (the human-readable audit answer
  text, verbatim from ACES), `finding` (`exception_code`, `severity`, `description`, `aor` — all
  verbatim from ACES, this is the ground truth for what fires and how severe it is), `check_type`
  (one of the 10 taxonomy types — see §3.3), and `atomic_rule_ids` (empty `[]` unless this option
  has been decomposed — then it lists the `rule_id`(s) of its atomic children).
- **`type_profile`** — a `{check_type: count}` histogram over this card's defect_options.
  `dominant_type` — the modal type. **Cards are frequently multi-type bundles** — do not assume a
  card's `dominant_type` describes every option in it.
- **`citations`** — 1-4 Selling Guide sections (each `{section_id, title, effective_date,
  guide_version}`) that govern this card's subject, capped at 4 by compile convention. **This cap
  is exactly why decomposition exists** — a card whose defect options span more than 4 distinct
  guide sub-topics cannot represent that at the card level; see `decomposition`.
- **`decomposition`** — `{required: bool, status: "not_required"|"pending"|"in_progress"|"done",
  target_sections: [...]}`. When `required: true`, `target_sections` lists EVERY section_id the
  card's defect options actually need (a superset of `citations` when the cap was exceeded).
  **This field is your worklist if you're extending decomposition to more categories.**
- **`compile`** — `{status: "compiled"|"compiled_with_flags"|"failed", failure_category, nuance}`.
  `failure_category` is one of a fixed enum (`bundle_requires_decomposition`, `citation_drift`,
  `citation_not_found`, `duplicate_card`, `scope_conflict`, `lender_specific_no_guide_basis`,
  `ambiguous_question`, `evidence_unavailable_to_engine`, `other`). `nuance` is a free-text
  explanation — **read this before trusting a flagged card's citations or acting on a failed one**;
  it's usually a precise, specific reason (see docs/taxonomy.md and reports/compile-stats.md for
  the full catalog of what's been flagged and why).
- **`status`/`version`** — the editable-config lifecycle: `draft` → `verified` → `active` →
  `retired`. **A deterministic engine should only ever load `status: "active"` rules.** Everything
  produced so far is `status: "draft"` — nothing here has been promoted to `active` yet. That
  promotion step does not exist yet in this pipeline; you'll need to design it (see §7).
- **`route`** — always `"FNM"` in this dataset. The schema reserves this level so other investor
  routes (FRD/Freddie, FHA, VA) can be added later without a redesign — `data/cards_all.json`
  already has their cards, scope-tagged, extracted and waiting.

### 3.2 Atomic rule shape (`$defs.atomicRule`)

One decidable check, one (or a small set of) precise citation(s), fully self-contained for a
runtime engine. Only exists for Income (140) and Assets (81) so far.

- **`rule_id`** — stable ID, format `FNM-<3-letter category abbrev>-<4-digit serial>` (e.g.
  `FNM-INC-0087`, `FNM-AST-0002`). Never reuse or renumber an existing ID if you regenerate a
  category — treat these as permanent identifiers once created.
- **`check_type`** — inherited verbatim from the parent card's defect_option (already
  taxonomy-verified during compile+verify — do not re-derive).
- **`statement`** — currently set to the `finding.description` text (the human-readable statement
  of what "failing" this check means). Not yet rewritten into a positive/imperative check
  statement — that's a reasonable next polish step, not a blocker.
- **`applicability`** — copied verbatim from the parent card. (No further narrowing was done —
  every defect_option under a card fires under the same applicability condition as the card itself.)
- **`evidence`** — `[{kind, name, field?, notes?}]`, `kind` is one of `document`, `extracted_field`,
  `reference_dataset`, `third_party_response`, `loan_context_flag`. **In the current Income/Assets
  atomic files, `evidence` was generated by keyword-matching the finding description against a
  small lookup table** (see `EVIDENCE_KEYWORDS` in `pipeline/decompose_income.py` /
  `decompose_assets.py`) — it is a reasonable first-pass guess at what document/field the check
  needs, but **has not been individually verified per rule**. Treat `evidence` as a draft
  scaffold to review, not a certified fact, unlike `citations` and `finding` which ARE verified.
- **`logic.procedure`** — a templated plain-language statement of the check, built per check_type
  (see the `build_logic()` function in either decompose script for the exact templates). Same
  caveat as evidence: **mechanically generated, not individually hand-verified.** This is the field
  a downstream engineer would turn into actual executable logic — treat it as a structured starting
  point, not a spec to blindly implement.
- **`finding`** — verbatim from the parent card's defect_option. **This IS fully verified** — every
  atomic rule's `finding.exception_code` + `finding.severity` was checked to round-trip
  byte-identical against the original ACES source (`data/by_category/<cat>.json`) by
  `validate_atomic.py`. Trust this field completely.
- **`citations`** — usually inherited from the parent card's `citations` array, EXCEPT where a
  precision override was applied (see `provenance.notes` / the `notes` field on the rule itself —
  its presence signals an override happened). Overrides were only applied where the parent card's
  `compile.nuance` or the verify pass had *already* named the correct specific section — this was
  not fresh guessing, it's promoting already-established reasoning. **Can be an empty array** for
  the one legitimate `lender_specific_no_guide_basis` case (a rule whose subject is confirmed
  absent from the entire 390-section guide corpus by exhaustive grep) — this is intentional, not
  a bug; the schema explicitly permits `citations: []` only when `compile.failure_category ==
  "lender_specific_no_guide_basis"`.
- **`provenance`** — `{parent_card_id, source_defect_option, compiled_by}`. Always trace an atomic
  rule back to its parent card via `parent_card_id` if you need the full original context
  (applicability reasoning, sibling options, category-level compile nuance).

### 3.3 The 10 check types (full definitions + examples: `docs/taxonomy.md`)

`doc_presence`, `doc_completeness`, `cross_doc_consistency`, `computation`, `threshold_eligibility`,
`date_window`, `list_screening`, `reverification`, `scripted_review`, `routing_context`.

One-line intuition for each, in case you don't have taxonomy.md loaded: presence = "is the document
there"; completeness = "does the present document have the required field/content"; cross-doc =
"do two source documents agree"; computation = "recompute a value and compare"; threshold = "does
one extracted value cross a fixed line"; date_window = "date arithmetic against a bound";
list_screening = "name/entity against a versioned reference list (OFAC, approved-vendor, etc)";
reverification = "third-party re-pull post-closing compared to original"; scripted_review =
"genuine judgment against an explicit criteria checklist — compiles to a checklist + a
REQUIRES_HUMAN_REVIEW fallback, NEVER a runtime model call"; routing_context = "sets a context
flag other cards' skip_logic depends on, raises zero findings itself."

**Do not add an 11th type without a strong reason** — the 10 were derived from reading all 266
cards in full, not guessed. If you find something that genuinely doesn't fit while extending to a
new category, document why in `docs/taxonomy.md` the same way the original corrections were
documented (see the "Corrections to the draft 5-type model" section there for the standard).

## 4. The compile pipeline (how data/compiled/*.json came to exist)

1. `extract_cards.py` (deterministic, no LLM) reads the xlsx, groups rows by (questionnaire,
   question code), applies scope tagging, writes `cards_base.json` / `cards_all.json`.
2. `split_guide.py` (deterministic, no LLM) extracts every PDF page's text once, then slices by
   outline page ranges into `guide/sections/*.txt` + `guide/index.json`.
3. A human (or you) reads all base cards and derives/updates `docs/taxonomy.md`. **This step is
   LLM reasoning but should be done in-context by a capable model reading the actual data — not
   delegated to a template.** It was originally done by reading `docs/cards_digest.md` in full.
4. `schema/rule.schema.json` defines the target shape.
5. **Compile**: for each category (or category-batch, for the 4 largest), an LLM agent reads
   `docs/taxonomy.md` + `schema/rule.schema.json` + its `by_category/<cat>.json` slice +
   `guide/index.json`, assigns check_type + citations + applicability translation per card, and
   writes `data/compiled/<unit>.json`. This is what `workflows/compile-remaining.js` orchestrates
   (see §5).
6. **Verify**: a second, fresh-context LLM agent adversarially spot-checks each compiled unit —
   re-reads cited guide sections to confirm topical fit, disputes questionable typings, diffs
   fidelity against source. Also orchestrated by the same workflow script, one stage after compile.
7. `validate_compiled.py` (deterministic, no LLM) is the actual gate: schema validation +
   citation-index resolution + exception_code/severity fidelity + the "must have >=1 citation
   unless lender_specific_no_guide_basis" business rule. **This is the authority on whether
   compiled data is usable — the LLM verify pass is a quality layer on top, not the gate itself.**
   Run this after touching any file under `data/compiled/`.

## 5. The compile workflow script (`workflows/compile-remaining.js`)

This is a Workflow-tool script (see the platform's Workflow tool docs if you're not familiar —
it's a JS orchestration script that calls `agent()` to spawn subagent LLM calls, with a `pipeline()`
helper that runs compile→verify per unit with no barrier between units, so unit B's compile can
run while unit A's verify is still going).

**Current state**: compile finished for all 18 units (266/266 cards). Verify finished for 9/18
units at last count (check `STATUS.md` for the live number — this may have completed by the time
you read this). If verify is incomplete, that does NOT block using the compiled data — verify is
a quality-assurance layer, and the compiled data already passed the deterministic gate cleanly.

**If you need to re-run or extend this workflow**: it takes no `args` currently — the unit list
is hardcoded (`UNITS` array, mirrors `pipeline/compile_units.json`) in priority order (small/
high-value categories first, the 4 largest split into 2 batches each and compiled last, so a
mid-run interruption loses at most half a category). To resume a prior run:
`Workflow({scriptPath: "workflows/compile-remaining.js", resumeFromRunId: "<runId>"})` — completed
units replay from cache; only failed/new units actually re-execute. **Before assuming a resume
recovered nothing, always check `data/compiled/` on disk directly** — files persist independent
of the workflow engine's own cache behavior (this bit us once: a resume re-attempted 2
already-successful units instead of cache-hitting them, but the files on disk were untouched and
still valid).

**To extend to a new category or route**: copy the `UNITS` array pattern, point `cat` at a new
`data/by_category/<slug>.json` (you may need to run a modified `extract_cards.py` first if it's a
different investor route — see the `scope.route` field and the "route hierarchy" note in §3.1),
and re-run. The compile/verify prompts in the script are fairly self-contained templates — read
them before modifying; they encode real conventions (4-citation cap, dedup rules, known
data-quality flags to catch) that took real iteration to get right.

## 6. The decomposition pattern (how data/atomic/*.json came to exist)

Decomposition promotes each card's `defect_options` to standalone `atomicRule` objects. **This
was done directly in-context (no subagent spawn) because the hard part — matching each defect's
true topic to its precise guide section — was already done during compile and verify.**
Decomposition is mechanical assembly of already-verified reasoning, not fresh judgment. This
matters for cost: if you're extending decomposition to more categories, check whether the
category's cards were flagged `bundle_requires_decomposition` with a populated `target_sections`
list bigger than `citations` (a real gap needing a manual per-exception_code override map, like
Income's two "other income" bundles) versus cards where `citations` already fully covers
`target_sections` (mechanical 1:1 promotion suffices, like almost all of Assets). Check with:

```python
for card in category_cards:
    d = card['decomposition']
    if len(d.get('target_sections', [])) > len(card['citations']):
        # needs a manual override map entry — see decompose_income.py PRECISE_CITATION
```

Read `pipeline/decompose_income.py` (the "true bundles" case, has a `PRECISE_CITATION` override
dict built from the compile/verify nuance text) and `pipeline/decompose_assets.py` (the "mostly
mechanical" case) as your two reference implementations — copy whichever pattern matches your
target category, adjust `EVIDENCE_KEYWORDS` if the category's evidence types differ (e.g.
appraisal-specific artifacts for Property-Appraisal), and always run `pipeline/validate_atomic.py`
afterward. **Do not skip the validator** — it caught a real schema bug last time (atomic rules
requiring `citations.length >= 1` unconditionally, which broke on the one legitimate
zero-citation case) and will catch fidelity drift if your promotion logic has a bug.

`evidence` and `logic.procedure` on existing atomic rules are template-generated and marked as
such in this README (§3.2) — if you're building an execution engine, budget time to review/rewrite
these per-rule rather than trusting them as-is. `citations` and `finding` are fully verified and
safe to build on directly.

## 7. What's NOT done yet (don't assume otherwise)

- **No rule has ever been promoted to `status: "active"`.** Everything is `"draft"`. There is no
  promotion workflow (draft → verified → active) implemented — you'll need to design what
  "verified" means operationally (presumably: passed the deterministic gate + a human or
  sufficiently-adversarial LLM verify pass) and build the promotion step.
- **100 of 266 cards are `decomposition.status: "pending"`** outside Income/Assets (Property-
  Appraisal 20, Product-Specific 13, Underwriting 13, Loan-Documents 10, Credit-Liabilities 9,
  Form-1033 6, Application 2, ATR-QM 2, Certification 2, Closing 1). They're fully usable at the
  card level (typed, cited, gate-passed) — just not atomized. Extend using §6's pattern if needed.
- **No execution engine exists.** This project produces the rule *data*, not a runtime that loads
  and executes it against a loan file. `logic.procedure` is a structured starting point for that,
  not itself executable.
- **No frontend exists**, but the schema (`status`/`version` lifecycle, stable `rule_id`s) was
  explicitly designed so one can be built without a data-model redesign — an add/edit/remove UI
  should read/write individual `atomicRule` or `card` objects, bump `version`, and manage the
  `status` transitions.
- **Verify is complete for all 18 units** as of this writing (check `STATUS.md`'s timestamp if you
  need to confirm this is still current — this README describes the pipeline, not a live status
  snapshot). One real, undisclosed citation error was caught and fixed this way
  (`fannie-mae-form-1033.b1`, see `reports/compile-stats.md`) — a concrete example of why the
  deterministic gate alone is not sufficient: it validates that a citation *exists* in the guide
  index, not that it's topically correct. **If you skip the LLM verify pass when extending this
  pipeline to new categories, you are accepting that class of error silently.**
- **If you resume a `Workflow` run after an interruption, don't assume the cache is complete.**
  This bit the original build twice: a resume can silently re-execute compile (not just verify)
  for units that had already succeeded, producing independently-valid-but-different output.
  Concretely: after any resume, re-run the atomic-decomposition consistency check below before
  trusting `data/atomic/*.json` against the current `data/compiled/*.json` — key by
  `(parent_card_id, exception_code)`, not exception_code alone, since codes legitimately repeat
  across cards:
  ```python
  cur = {(c['card_id'], o['finding']['exception_code']): (o['check_type'], [x['section_id'] for x in c['citations']])
         for c in compiled_category for o in c['defect_options']}
  for r in atomic_rules:
      key = (r['provenance']['parent_card_id'], r['finding']['exception_code'])
      # compare r['check_type']/r['citations'] against cur[key]; 'notes' present on r means an
      # intentional citation override, don't flag those as drift.
  ```
  If drift turns up, just re-run the category's `decompose_*.py` against the current compiled data
  — don't hand-patch individual rules.
- **Only the FNM (Fannie Mae) route is populated.** FRD (Freddie Mac), FHA, VA, RHS/USDA cards
  exist in `data/cards_all.json` (scope-tagged, extracted, ready) but have never been compiled.
  FRD would need the Freddie Seller/Servicer Guide as a second citation source (not present in
  `source/` — the Selling Guide only covers Fannie Mae).
- **ACES licensing was explicitly out of scope for this build** (per direct instruction) — if this
  project is ever distributed externally (not just used internally), that should be revisited;
  the base rule text is derived from ACES-authored questionnaire content.

## 8. Practical notes for working in this directory

- This directory (`tmp/mortgage-qc/`) is **gitignored** relative to the parent workspace repo and
  is intentionally scratch/demo space, not tracked source — Serena MCP (if your environment has
  it and defaults to it) will refuse to touch files here with a "path is ignored" safety error;
  use plain file read/write tools instead.
- Python scripts assume `openpyxl` (xlsx), `pypdf` (PDF), and `jsonschema` (validation) are
  available. If not installed globally, run via `uv run --no-project --with <pkg> python3 <script>`.
- All JSON files are indented (`indent=1` or `indent=2`) and safe to diff/read directly — no
  minification anywhere in this pipeline.
- When in doubt about whether a fact in this README is still accurate, the deterministic
  validators (`validate_compiled.py`, `validate_atomic.py`) are ground truth — re-run them rather
  than trusting any narrative document, including this one and `reports/compile-stats.md`.
