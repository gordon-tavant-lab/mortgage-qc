export const meta = {
  name: 'compile-fnm-gold-rules-remaining',
  description: 'Compile the 239 not-yet-done FNM cards in priority order (Income/Assets first, big categories split into batches last); then verify per unit',
  phases: [
    { title: 'Compile', detail: '18 units (2 categories already done are excluded), smaller batches for the 4 largest categories' },
    { title: 'Verify', detail: 'fresh-context citation + typing spot-check per unit' },
  ],
}

const ROOT = '/Users/9_0rdon/Documents/workspace/tmp/mortgage-qc'

// Priority order: flagship (income, assets) first, then small remaining categories,
// then the 4 largest categories split into 2 batches each (smaller blast radius if
// interrupted again). loan-documents + credit-liabilities already compiled+verified
// on disk from the first run — intentionally excluded, not re-spent on.
const UNITS = [
  { outId: 'income', cat: 'income', start: 0, end: 23, n: 23 },
  { outId: 'assets', cat: 'assets', start: 0, end: 25, n: 25 },
  { outId: 'closing', cat: 'closing', start: 0, end: 10, n: 10 },
  { outId: 'data-validation-svc-dvs', cat: 'data-validation-svc-dvs', start: 0, end: 9, n: 9 },
  { outId: 'epd', cat: 'epd', start: 0, end: 9, n: 9 },
  { outId: 'application', cat: 'application', start: 0, end: 8, n: 8 },
  { outId: 'atr-qm', cat: 'atr-qm', start: 0, end: 6, n: 6 },
  { outId: 'insurance', cat: 'insurance', start: 0, end: 6, n: 6 },
  { outId: 'information-integrity', cat: 'information-integrity', start: 0, end: 6, n: 6 },
  { outId: 'certification-endorsement-and-delivery', cat: 'certification-endorsement-and-delivery', start: 0, end: 3, n: 3 },
  { outId: 'underwriting.b1', cat: 'underwriting', start: 0, end: 15, n: 15 },
  { outId: 'underwriting.b2', cat: 'underwriting', start: 15, end: 29, n: 14 },
  { outId: 'fannie-mae-form-1033.b1', cat: 'fannie-mae-form-1033', start: 0, end: 15, n: 15 },
  { outId: 'fannie-mae-form-1033.b2', cat: 'fannie-mae-form-1033', start: 15, end: 30, n: 15 },
  { outId: 'product-specific.b1', cat: 'product-specific', start: 0, end: 17, n: 17 },
  { outId: 'product-specific.b2', cat: 'product-specific', start: 17, end: 34, n: 17 },
  { outId: 'property-appraisal.b1', cat: 'property-appraisal', start: 0, end: 21, n: 21 },
  { outId: 'property-appraisal.b2', cat: 'property-appraisal', start: 21, end: 41, n: 20 },
]

const SUMMARY_SCHEMA = {
  type: 'object',
  required: ['unit', 'cards_total', 'compiled', 'compiled_with_flags', 'failed', 'dominant_type_counts', 'failure_notes'],
  properties: {
    unit: { type: 'string' },
    cards_total: { type: 'integer' },
    compiled: { type: 'integer' },
    compiled_with_flags: { type: 'integer' },
    failed: { type: 'integer' },
    dominant_type_counts: { type: 'object', additionalProperties: { type: 'integer' } },
    failure_notes: { type: 'array', items: { type: 'object', required: ['card_id', 'category_or_flag', 'nuance'], properties: { card_id: { type: 'string' }, category_or_flag: { type: 'string' }, nuance: { type: 'string' } } } },
  },
}

const VERIFY_SCHEMA = {
  type: 'object',
  required: ['unit', 'cards_checked', 'citation_errors', 'typing_disputes', 'verdict'],
  properties: {
    unit: { type: 'string' },
    cards_checked: { type: 'integer' },
    citation_errors: { type: 'array', items: { type: 'string' } },
    typing_disputes: { type: 'array', items: { type: 'string' } },
    other_issues: { type: 'array', items: { type: 'string' } },
    verdict: { enum: ['clean', 'minor_issues', 'needs_recompile'] },
  },
}

const compilePrompt = (u) => `You are compiling mortgage QC audit rules into a deterministic rules-engine gold set. Work exactly within the established design — do not invent your own conventions.

READ FIRST (all under ${ROOT}):
1. docs/taxonomy.md — the 10 check types + structural findings. Follow it exactly.
2. schema/rule.schema.json — the target shape ($defs.card). Your output must validate against it.
3. data/by_category/${u.cat}.json — the full category array. YOUR ASSIGNMENT is only the 0-indexed slice [${u.start}, ${u.end}) of this array — that is ${u.n} cards. Ignore cards outside this range; another agent owns them.
4. guide/index.json — all 390 Selling Guide sections (section_id, title, effective_date, file). Citations MUST use section_ids from this index. To confirm a section covers the topic, read its text at guide/<file>. Use Grep over ${ROOT}/guide/sections/ to locate topics.

TASK — for each of your ${u.n} assigned cards produce a compiled card object per $defs.card:
- card_id, question_text, category verbatim from input; route "FNM"; status "draft"; version 1.
- applicability: translate the ACES SQL (Question Criteria) into the declarative all_of/any_of condition form; keep source_sql verbatim. Skip-logic: copy the raw skip-logic string into skip_logic_source when present.
- defect_options: for EVERY answer option with an exception_code, assign one check_type from the taxonomy, and carry finding {exception_code, severity, description, aor} verbatim. DEDUPE literal duplicate options (same exception_code + same response text) — keep one, note the dedup in card notes.
- type_profile: count of defect_options by check_type. dominant_type: the modal type.
- citations: 1-4 Selling Guide sections that govern this card's subject, from guide/index.json ONLY, with exact title + effective_date. Verify topical fit by reading/grepping the section text. Cards about lender-ops artifacts with no guide basis may have zero citations ONLY with compile flag lender_specific_no_guide_basis.
- decomposition: required=true iff the question is a catch-all bundle whose defect options do not enumerate every underlying guide requirement; status "pending"; target_sections = the section_ids its children will cite. Otherwise required=false, status "not_required".
- compile: status "compiled" | "compiled_with_flags" | "failed" (+ failure_category + nuance). Known flags to catch: scope_conflict, duplicate_card, citation issues, routing_context cards (0 defect options). The nuance string must be specific — it feeds a per-rule failure report the user explicitly requested.

OUTPUT: Write the JSON array of your ${u.n} compiled cards to ${ROOT}/data/compiled/${u.outId}.json (create dir if needed — this exact filename, not the category name, since this may be one of several batches for the category). Then return ONLY the summary object (unit="${u.outId}", counts, dominant_type_counts, failure_notes).

QUALITY BARS: severities/exception codes byte-identical to input. Citation section_ids must exist in index.json. Every compiled card must have >=1 citation or the lender_specific flag. Do not skip cards; cards_total in your summary must equal ${u.n}.`

const verifyPrompt = (u) => `Fresh-context adversarial verification of compiled mortgage-QC rule cards. You did NOT write these; try to find faults.

Files (under ${ROOT}): data/compiled/${u.outId}.json (compiled output — ${u.n} cards, a slice of the '${u.cat}' category), data/by_category/${u.cat}.json (full category source — your cards are the 0-indexed slice [${u.start}, ${u.end})), docs/taxonomy.md (type definitions), guide/index.json + guide/sections/ (Selling Guide text).

Check, sampling AT LEAST 60% of cards (all of them if <=10):
1. CITATIONS: for each sampled card, read the cited section text in guide/sections/ — does it actually govern the card's subject? Flag any citation where the section text does not support the card. Flag any section_id absent from index.json.
2. TYPING: does each sampled defect_option's check_type match the taxonomy definition? Dispute mis-typings with a one-line reason.
3. FIDELITY: spot-check 5 defect options against the source file — exception_code + severity must be byte-identical; flag drops/mutations.
4. FLAGS: were the known data-quality flags handled where applicable to this unit?

Return the summary object only (unit="${u.outId}"). verdict: clean | minor_issues | needs_recompile.`

phase('Compile')
const results = await pipeline(
  UNITS,
  (u) => agent(compilePrompt(u), { label: `compile:${u.outId}`, phase: 'Compile', schema: SUMMARY_SCHEMA }),
  (summary, u) => summary
    ? agent(verifyPrompt(u), { label: `verify:${u.outId}`, phase: 'Verify', schema: VERIFY_SCHEMA }).then(v => ({ summary, verify: v }))
    : null,
)

const ok = results.filter(Boolean)
log(`compile+verify complete for ${ok.length}/${UNITS.length} units`)
return {
  units: ok.map(r => ({
    unit: r.summary.unit,
    cards: r.summary.cards_total,
    compiled: r.summary.compiled,
    flagged: r.summary.compiled_with_flags,
    failed: r.summary.failed,
    dominant_types: r.summary.dominant_type_counts,
    failure_notes: r.summary.failure_notes,
    verify: r.verify,
  })),
  missing: UNITS.filter(u => !ok.some(r => r.summary.unit === u.outId)).map(u => u.outId),
}
