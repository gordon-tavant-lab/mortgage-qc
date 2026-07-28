# Prior Art: Olav's "Ratio-Space Console" (scenario.agent-lab.io)

| | |
|---|---|
| **Date** | 2026-07-24 |
| **Subject** | `https://scenario.agent-lab.io` — Olav's live scenario-modeling demo, the one narrated in the Citizens Bank "Reimagine the Bank" call transcript (Ross's AI-assisted-risk-analysis pillars, Olav's screen-share of LTV/FICO scenario modeling and gift/guideline-extraction walkthrough). Accessed live (password-gated, shared Agent Lab portal credential already on file in this workspace's own intel docs — `agent-lab/INDEX.md`), not from source. |
| **Why this matters here** | Same problem class as `specs/002e-conditional-applicability-gating`: turning lender/agency guideline PDFs into machine-evaluable constraints, including a loan-fact conditional-applicability concept. This is closer, higher-confidence prior art than the external research in `output/RULE-COMPILER-FIX-PLAN-2026-07-24.md` — a sibling Tavant/Olav system solving the identical extraction problem, not just published literature. |
| **Status** | Findings only. One concrete revision to `002e`'s schema follows below (applied to the spec directly, not just noted here). |

---

## What the console is

A single declarative spec (`mortgage.yaml`) drives everything: eligibility polytope (LTV × FICO), a
PD (probability-of-default) surface, a D6/D7 deep-delinquency stress panel, and a credit-narrative
generator — all read by a backend `engine.py` the docs describe as "a pure interpreter of that spec
(no formulas of its own)... the model is data, not code." Same architectural bet as our own "compile,
then run" — independently arrived at.

The spec has two provenance classes: **guideline-derived** (`products`/`constraints` — change often,
come from lender overlays + agency guides) and **data/policy-derived** (`models`/`scenarios`/`shock` —
change rarely, fitted from loan-performance data or set by risk policy). Only the first class is
relevant to our compiler; the PD/D6-D7 modeling work is out of scope for anything we're doing.

## The guideline→spec pipeline (directly comparable to our compiler)

A 4-stage pipeline, all real, all inspectable in the demo's **Guidelines** tab:

1. **Ingest** — real extracted-guideline JSON files are loaded (`agency-combo-pennymac-overlay-
   compilation.json`, `cagencycreditoverlays.json`, `cms-conventional-guideline-overlays.json`,
   `underwriting-overlay-matrix.json`) — each reporting **N total rules, M machine-evaluable**
   (e.g. "44 rules · 17 machine-evaluable"). Extraction itself (locating each rule, anchoring it to a
   page) happens **upstream**, in what the docs call "the Citizens pipeline" — this console only
   consumes already-extracted output. Direct parallel to our own Non-Negotiable #2 (extraction is
   Touchless's job, not the engine's) — confirmed as the same discipline in a different Tavant system.
2. **Extract & Review** — each extracted rule is shown as: category (Credit/LTV-CLTV/DTI), a compact
   parsed form (`fico >= 620`), which AUS/program it applies to, a **numeric confidence score** (0.82–
   0.92 observed), the full quoted source sentence, a **`scope:`** annotation when the rule is
   conditionally gated (e.g. `scope: property_type == manufactured`), and a source citation with an
   actual page-image proof link (`/api/guidelines/docs/.../proof?rule_id=...`) — a citation-viewer
   discipline for *guideline* documents, mirroring what we already do for *loan* documents. Human
   review is per-rule: **✓ approve / ✕ reject** — nothing reaches the compiled spec unreviewed.
3. **Bridge** — a crosswalk (`bridge/mapping.yaml`) resolves three reconciliations: **field crosswalk**
   (agency canonical field → this spec's variable name, e.g. `reserves_months` → `reserves`; several
   fields explicitly "(dropped)" — no lever in this spec), **product roll-up** (many agency/AUS product
   names collapse many-to-one onto this spec's product ids, e.g. Desktop Underwriter + Loan Product
   Advisor + Agency Plus DU + HomeReady DU + ... all → `conf`), and **value crosswalk** (categorical
   value normalization, e.g. `primary_residence → Primary`). Explicitly named unmapped gaps too (no
   agency column for `jumbo`/`dscr`/`bsnq`; `VA`/`USDA`/`Texas 50(a)(6)` unmapped source columns).
4. **Propose** — the actual compiled YAML preview, e.g.:
   ```yaml
   - id: fha
     constraints:
       - { var: fico, op: ">=", limit: 640 }   # underwriting-overlay-matrix p1  (scope: amortization_type == arm)
   ```
   Every constraint carries an inline source-citation comment (doc + page) AND, when applicable, an
   inline `scope:` annotation — **a compound, multi-clause condition**, not a single field/value pair:
   `(scope: occupancy == primary_residence; units between [3, 4]; loan_purpose in ['purchase', 'rate_term_refinance'])`.
   Note the operator variety: `==`, `in [...]` (set membership), `between [...]` (range) — richer than
   a single equality/inequality triple.

**A named taxonomy for why a rule DOESN'T compile** (from the Bridge tab, "Why rules don't map"): the
majority (98 of ~162 unmapped) fail because *"field 'X' has no variable in this spec"* — a missing
catalog-field gap, directly analogous to our own `proposed_field_entry` flow. But two other named,
distinct categories are worth adopting as reporting practice: **"documentation — narrative, not a
constraint"** (33 — a rule that's descriptive prose, not an assertion at all) and **"prohibition —
would be a pick gate; not auto-mapped"** (9 — a rule that excludes an entire *product*, a coarser,
different shape than gating one *check*). Neither is "the LLM failed" — both are honest, named reasons
a real rule genuinely isn't the kind of thing this compiler compiles, surfaced as a breakdown rather
than a single opaque "gap" bucket.

## The applicability concept: confirms our design, but shows it's too narrow

The console's `scope:` field is functionally identical to what `002e` calls `applies_if` — a
loan-fact precondition on a compiled constraint, kept **separate** from the constraint's own
`{var, op, limit}` and from the coarser `applies_to[]` (program/AUS-level) gate. This is the exact
two-layer separation `002e`'s spec argues for (program gating vs. loan-fact gating), now independently
confirmed by a real, closely-adjacent Tavant system — not just XACML/DMN literature.

**But it's richer than `002e`'s current design.** `002e`'s spec.md (as drafted) defines `applies_if` as
one `{field_name, operator, value}` triple. This console's real `scope:` examples show **compound,
AND-combined, multi-operator** conditions are the norm, not the exception:
`occupancy == primary_residence; units between [3, 4]; loan_purpose in ['purchase', 'rate_term_refinance']`.
A single-triple `applies_if` cannot express this — it would force artificially splitting one real
precondition into multiple checks, or silently dropping clauses. **Revision applied directly to
`specs/002e-conditional-applicability-gating/spec.md`/`plan.md`** (see diff below): `applies_if`
becomes a list of conditions (implicitly AND-combined), and the operator vocabulary extends to include
`in` (set membership) and `between` (range), not just `==`/`!=`/`<=`/`>=`.

## The narrative pipeline (confirms, doesn't change, our own reconcile/citation discipline — noted, not adopted)

The **Narrative** tab shows a third authored artifact, `reasoning.yaml`: deterministic findings (PD,
binding constraint, stress deltas) feed rule-fired **reasoning points**, each human-reviewable
(**✓ agree / – not relevant / ✗ disagree**) before any LLM runs. Only then does the LLM compose prose
— strictly from the human-curated point set: *"Judgment lives in `reasoning.yaml` and in your
curation — not the LLM, which only composes the points you agreed to... the narrative cites nothing
you didn't approve."* This is not something `002e`/`002d` need — our project has no narrative-
generation surface yet — but it's a clean, minimal LLM-usage pattern worth remembering if/when a
credit-narrative or exception-summary feature is ever specced (a natural fit for `008`'s exception
queue, later, not now).

## What was NOT adopted, and why

- The console's own risk-model fitting (PD/D6-D7 logistic regression) — out of scope, a different
  problem (predictive risk scoring, not deterministic QC rule compilation).
- The full route/block/DAG runtime-agent architecture underlying it (same family as
  `examples/mortgage-qc`, per `docs/architecture/rule-compiler.md` §6) — not adopted for the same
  reason already documented there.
- `reasoning.yaml`'s narrative pattern — noted for a future feature, not built now.

## Concrete outcome

`specs/002e-conditional-applicability-gating/spec.md` and `plan.md` revised: `applies_if` is now
`List[Dict[str, str]]` (AND-combined), with `operator` extended to include `in`/`between` alongside
`==`/`!=`/`<=`/`>=`/`<`/`>` — directly citing this real prior art alongside the XACML/DMN research
already backing the feature.
