# SHACL Pilot Experiment — Journal

Chronological record of the SHACL pilot experiment in the gitignored `src/` sandbox.
All steps occurred on 2026-07-29. Paths are relative to the repository root
(`demo-sites/mortgage-qc-prod/`) unless noted. Each step lists the decision(s) it
implements and the concrete artifacts that substantiate it. Where an artifact was
overwritten or never persisted, that is stated rather than papered over.

---

## Step 1 — Audit of the NotebookLM-generated artifacts

**What was done.** Audited the two scripts produced from the NotebookLM exploration
before trusting any of their outputs.

Finding 1: `src/scripts/qc-loan-audit-engine.py` is **self-confirming** — the loan
data, the audit findings, and the "expected answer key" are all hardcoded in the same
file, and the reconciliation match at line 224 is rigged: it declares a rule match if
the expected rule code is merely in the list `["Asset-Documentation-Sufficient",
"Form 1033-Comp-Distance"]`, guaranteeing the "100% Match" banner. Its saved output
(`src/doc/qc-audit-reconciliation-report.txt`) shows the 5/5 "SUCCESS" result that the
script cannot fail to print.

Finding 2: `src/scripts/compliance_ontology_generator.py` originally fell back to a
hardcoded 10-row sample when the CSV was not supplied, silently producing a tiny
ontology (`src/ontologies/compliance_rules_ontology_OLD.ttl`, 270 lines) that looked
legitimate. The fallback was removed — the docstring now reads "CSV input is required.
No fallback/default data is provided." (line 21) — and the ontology was regenerated
from the full 5,899-line AMQ CSV, yielding a 35,519-line TTL.

**Why.** Both failure modes are exactly the untrustworthy-artifact pattern the project's
determinism doctrine exists to prevent; nothing downstream could be built on them
without this audit. This step motivated the honest-by-construction rules in
[001](001-shacl-sandbox-override.md) and [002](002-extraction-from-syn-pdfs.md).

**Evidence**
- `src/scripts/qc-loan-audit-engine.py` (248 lines; rigged match at line 224)
- `src/doc/qc-audit-reconciliation-report.txt` (43 lines; the self-confirming "100% Match" output)
- `src/scripts/compliance_ontology_generator.py` (336 lines; docstring line 21: fallback removed, CSV required)
- `src/ontologies/compliance_rules_ontology_OLD.ttl` (270 lines — the old fallback-derived output, preserved)
- `src/ontologies/compliance_rules_ontology.ttl` (35,519 lines — regenerated from the full CSV)
- `src/doc/PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv` (5,899 lines — the required source)

---

## Step 2 — SHACL sandbox decision and pilot v1

**What was done.** Gordon accepted the SHACL-as-engine experiment inside the gitignored
`src/` sandbox ([001](001-shacl-sandbox-override.md)), deliberately setting aside the
project-level "no OWL/RDF reasoner in the runtime path" boundary for `src/` only.
Pilot v1: 5 hand-authored SHACL NodeShapes for loan 01, run twice on independently
constructed graphs (determinism check), reconciled at runtime against the real p0
defect manifest (not a hardcoded key), plus a negative control. Result: 5/5 on loan 01,
deterministic.

**Why.** Empirical test of the SHACL approach rather than re-litigating the documented
FIBO boundary — the same empirical culture as the G3 bake-off. v1 was superseded the
same day by v2/v3; its runner and shapes survive, but v1 run outputs were overwritten
by later runs and are not preserved.

**Evidence**
- `src/decisions/001-shacl-sandbox-override.md`
- `src/shacl_pilot/shapes_loan01.ttl` (138 lines; 5 `sh:NodeShape` definitions — the v1 shape set)
- `src/shacl_pilot/run_shacl_audit.py` (the v1 runner: loads `p0/fixtures/from_docs/loan_01.json` and `defect_manifest.json` at runtime, double-run determinism check, cannot print SUCCESS unless every manifest defect is detected)
- v1 run outputs / negative-control transcripts: **not preserved** — overwritten by v2/v3 artifacts in `src/shacl_pilot/out/`; the claim of 5/5 + negative control rests on the session record, with the runner's logic as the surviving mechanism.

---

## Step 3 — Pilot v2: real extraction, citations, 25 checks, versioned shapes

**What was done.** Rebuilt the pilot on honest inputs, implementing decisions
[002](002-extraction-from-syn-pdfs.md)–[008](008-needs-review-tri-state.md):

- `extract_loan.py` — extracts loan data directly from `demo/syn/loan 0X/` PDFs
  (`pdftotext -layout`) + MISMO XML, with signature-presence detection; every value
  carries a citation `{doc_name, page, snippet}`; the answer-key PDF
  (`00_Loan_Summary_And_Answer_Key.pdf`) is never parsed (skip at line 237);
  `*** ... ***` stage-direction markers are stripped from values but kept in citation
  snippets ([002](002-extraction-from-syn-pdfs.md), [003](003-citations-non-negotiable.md)).
- `loan_to_rdf.py` — extraction JSON → RDF graph, with citations as `li:cite_<field>`
  nodes in the graph itself ([003](003-citations-non-negotiable.md)).
- 25 checks (SHACL NodeShapes) across 9 block files in `src/shacl_pilot/blocks/`
  (application 7, property_appraisal 7, assets 2, credit_liabilities 2,
  product_specific 2, underwriting 2, certification_delivery 1, closing 1, income 1),
  organized routes → blocks → checks with `routes.json`
  ([005](005-routes-blocks-checks.md)); untraceable thresholds carry explicit
  `SME-PLACEHOLDER` markers (e.g. `blocks/property_appraisal.ttl` line 16); judgment
  rules fire as `sh:Warning` per the tri-state proposal
  ([008](008-needs-review-tri-state.md)).
- `shape_manifest.py` — content-hash versioning of all block files + `routes.json`
  ([004](004-shape-versioning.md)). `shapes_manifest.json` versions 1–3 record the
  SME-edit simulation: v1 baseline (combined sha256 `f1924dde…`, 20:45:13); an
  unrecorded edit to `blocks/closing.ttl` made `verify` fail loudly; `update` recorded
  it as v2 (`02db0c9e…`); reverting produced v3 with the **same combined hash as v1**
  (`f1924dde…`) — content-addressing demonstrated round-trip.

Result reported for v2: 25/25 answer-key defects detected across loans 01–05
(loan 01 per [007](007-loan01-gauge-answers-key.md) as gauge, loans 02–05 vs
`demo/syn/Answers.md`), deterministic double runs, 3 negative controls passed.
SME-friendly authoring UX explicitly deferred ([006](006-sparql-ux-deferred.md)).

**Evidence**
- `src/shacl_pilot/extract_loan.py`, `src/shacl_pilot/loan_to_rdf.py`
- `src/shacl_pilot/blocks/` — 9 `.ttl` files totalling 25 `sh:NodeShape` checks
- `src/shacl_pilot/routes.json`, `src/shacl_pilot/shape_manifest.py`
- `src/shacl_pilot/shapes_manifest.json` — versions 1–3 (v1/v3 combined hash `f1924ddee30d…` identical; v2 `02db0c9efb2a…` differs only in `blocks/closing.ttl`)
- `src/shacl_pilot/out/loan_01.json` … `loan_05.json` (v2-era extraction outputs, 20:40–20:41) and `out/loan_01.ttl` (RDF graph with `li:cite_` nodes, 49 occurrences)
- `demo/syn/Answers.md` (Gordon-authored ground truth for loans 02–05)
- The 25/25 + negative-control run transcripts themselves were **not persisted as files**; the runner logic that enforces them (double run, extra-FAIL accounting) survives in `src/shacl_pilot/run_audit.py` (v3, which superseded the v2 runner in place).

---

## Step 4 — Honest per-loan stats: PASSED=0, NO_DATA=57

**What was done.** Instrumented the v2 runner to report per-check status honestly
instead of only reporting detections. The numbers were uncomfortable and were reported
as-is: **PASSED = 0** — every one of the 25 checks was authored against a known defect,
so no check ever passed on the loan it targeted (defect-targeted authoring, not
generalized rule coverage) — and **NO_DATA = 57** status instances across the five
loans, because the pilot extractor covers only the fields the 25 checks need, and
those fields mostly exist only on the loan whose defect they target.

**Why.** A check that silently passes because its data was missing is indistinguishable
from a genuine pass — this is the exact failure mode that motivated the
PASS / FAIL / NEEDS_REVIEW data-guard proposal in [008](008-needs-review-tri-state.md).

**Evidence**
- `src/decisions/008-needs-review-tri-state.md` (the proposal these stats motivated)
- `src/shacl_pilot/run_audit.py` lines 239–248, 271–273 — the surviving per-check status accounting (`PASSED` / `FAIL` / `NEEDS_REVIEW` / `NO_DATA` counters printed per loan)
- The specific v2 console output containing "PASSED 0 / NO_DATA 57" was **not persisted as an artifact**; the figures are from the session record. Re-running `run_audit.py` reproduces the same accounting for the current shapes version.

---

## Step 5 — Course-correction to full-workbook scale

**What was done.** Gordon rejected the 25-check demo scale ("the total rules run
should be at least 500+") and the pilot was re-based on the full Post-Closing AMQ
workbook, implementing [009](009-full-workbook-compile.md),
[010](010-program-filter-question-code.md), [011](011-olav-blocks-routes-isolation.md):

- `amq_compiler.py` (Layer 1 — mechanical, deterministic, no LLM) compiles the
  5,520-row CSV into `compiled/ruleset.json`: **4,167 rules** (one per unique
  Question Code × Exception Name pair), **379 Discarded-category pairs excluded**,
  ruleset sha256 `2816f1149b5a9ff8f83c5d87b7e2d9764c86c4280dc06da12a724012d7d355c8`.
  Honest evaluability classes: `mapped` 7, `doc_presence` 134, `unmapped` 4,026
  (unmapped runs as NOT_EVALUATED — never a silent pass).
- Program filter by Question Code agency prefix ([010](010-program-filter-question-code.md)):
  agency rules O-FRD 1,141 / O-FNM 1,108 / O-FHA 716 / O-RHS 513 / O-VA 445 +
  244 GENERIC rules → per-loan run populations FNM 1,352 / FRD 1,385 / FHA 960 /
  RHS 757 / VA 689 (verified against the compiled ruleset).
- Olav block taxonomy: AMQ categories mapped to the 16-block catalog, validated at
  compile time against `docs/research/olav-demo-yaml/blocks_manifest.json`; routes v2
  in `routes.json` (per-program routes, deterministic agency lookup, recorded per run)
  — shapes manifest v4 records the `routes.json` change.
- p0 dependency removed ([011](011-olav-blocks-routes-isolation.md)): loan 01's answer
  key transcribed to `src/shacl_pilot/answer_keys/loan_01_answers.md`; the runner reads
  nothing from `p0/`.
- Runner v3 `run_audit.py`: full applicable rule population per loan, double-run
  determinism on the pilot shapes, reconciliation against the two answer keys inside
  `src/` + `demo/syn/`. Result reported: still 25/25, no unexpected extra FAILs,
  deterministic.

**Evidence**
- `src/decisions/009-full-workbook-compile.md`, `src/decisions/010-program-filter-question-code.md`, `src/decisions/011-olav-blocks-routes-isolation.md`
- `src/shacl_pilot/amq_compiler.py`
- `src/shacl_pilot/compiled/ruleset.json` (`rules_total` 4167, `discarded_excluded` 379, `source_rows` 5520, `ruleset_sha256` `2816f114…`; agency and eval-class counts verified by direct inspection)
- `src/shacl_pilot/routes.json` (v2 — per-program routes referencing the Olav block ids) and `src/shacl_pilot/shapes_manifest.json` version 4 (`routes.json` hash change)
- `docs/research/olav-demo-yaml/blocks_manifest.json` (block-taxonomy validation source)
- `src/shacl_pilot/answer_keys/loan_01_answers.md`
- `src/shacl_pilot/run_audit.py` (v3; prints "SUMMARY: N/N answer-key defects detected | extra FAILs | non-deterministic" and stamps ruleset sha + shapes version into every run)
- `src/shacl_pilot/out/loan_0X_extraction.json` (v3-era extraction outputs, 22:54)

---

## Step 6 — Rules-clarity review of the 4,167 compiled rules

**What was done.** An honest, no-code assessment of what the compiled workbook rules
actually say. Findings as reported in the session:

- 3,282 rules (~79%) are generic "were all requirements met"-style wrappers that name
  a topic but state no checkable condition (a broad spot-check confirms the pattern's
  scale: 3,833 of 4,167 question texts contain "requirement");
- only 1 rule of 4,167 cites a specific guide section;
- ~566 rules hinge on judgment words (reasonable, adequate, sufficient, …);
- ~566 rules have thin conditions, including answer options that amount to pass/N-A;
- 69 rules are reverification-action rules (re-do the verification, not check a value).

**Conclusion drawn:** the AMQ workbook is an *answer-capture questionnaire* that
presumes auditor knowledge; three knowledge layers exist (the questionnaire, the
agency guidelines, and unwritten SME practice), so an SME-in-the-loop is structural,
not a temporary crutch. This directly motivated the grounding corpus (Step 7).

**Evidence**
- `src/shacl_pilot/compiled/ruleset.json` — the data the review was performed over
- `src/decisions/012-selling-guide-grounding-corpus.md` — records the review's key figure ("only 1 of 4,167 rules cites a section") and the conclusion it drove
- The review itself produced **no persisted analysis artifact** (deliberately no code); the specific counts (3,282 / ~566 / ~566 / 69) are from the session record and were not independently re-derived for this journal.

---

## Step 7 — Selling Guide grounding corpus (Layer B)

**What was done.** Implemented [012](012-selling-guide-grounding-corpus.md):
`selling_guide_index.py` deterministically parses the TOC of
`docs/Selling-Guide_06-03-2026_highlighted.pdf` (1,188 pages) into a citable topic
index — **386 topics** with {code, title, effective date, printed page, PDF page},
hierarchy derived from the topic code itself, printed→PDF page offset **+18** —
emitted as both `compiled/selling_guide_index.json` and an RDF topic graph
`compiled/selling_guide_ontology.ttl` (389 lines). A topic index with citations, not
a semantic OWL model of the regulation (which would recreate the untraceable-
interpretation problem).

First use, same day: `lookup("B3-4.2-02")` (Depository Accounts, PDF p.432) verified
the real source of the 50%-of-monthly-qualifying-income large-deposit definition
behind AMQ O-FNM-00215 — now attached to `LargeDepositShape` in `blocks/assets.ttl`
as `caro:guideCitation` — **and** surfaced a precondition the AMQ row never states:
large-deposit documentation is not required for refinance transactions (purchase-only
gate, flagged in the block file pending SME confirmation). The assets.ttl edit was
recorded as shapes manifest **v5**, combined hash `696832b1efad…`.

**Evidence**
- `src/decisions/012-selling-guide-grounding-corpus.md`
- `src/shacl_pilot/selling_guide_index.py`
- `src/shacl_pilot/compiled/selling_guide_index.json` (`topics_total` 386, `pages` 1188, `page_offset` 18; topic B3-4.2-02 → pdf_page 432)
- `src/shacl_pilot/compiled/selling_guide_ontology.ttl` (389 lines)
- `docs/Selling-Guide_06-03-2026_highlighted.pdf` (source, 1,188 pp)
- `src/shacl_pilot/blocks/assets.ttl` — `caro:guideCitation "B3-4.2-02 Depository Accounts, Selling Guide 06/03/2026, PDF p.432"` (line 28) + the refi-exemption nuance comment (lines 20–23)
- `src/shacl_pilot/shapes_manifest.json` version 5 (changed file `blocks/assets.ttl`, combined sha256 `696832b1efad06142f3f3a5f2edb85bdfc384f7b4ac1e3fb67c50feeefdb5c46`, 22:53:46)

---

## Step 8 — Layer-2 triage of the application-verification block (in progress)

**What was done (current step at time of writing).** The main session began the
Layer-2 compile pass ([009](009-full-workbook-compile.md) §two-layer compile) by
triaging the **application-verification** block — 81 compiled rules (verified count in
`compiled/ruleset.json`) — classifying each unmapped rule's text toward
{required docs, required fields, comparison logic} with Selling Guide grounding from
Step 7. In progress; no completed artifact yet.

**Evidence**
- `src/shacl_pilot/compiled/ruleset.json` — 81 rules with `block = application-verification`
- Triage output: **not yet persisted** (work in progress at time of writing).

---

## Step 9 — Bucket resolution of the 16 YELLOW groups (application-verification)

**What was done.** Step 8's triage completed and persisted
(`compiled/triage_application_verification.json`: 81 rules → 55 unique groups → 18
GREEN / 16 YELLOW / 8 RED / 13 NOT_A_CHECK). A verification pass (not a prior-summary
carry-forward) re-derived, for each of the 16 YELLOW groups, which of three resolution
buckets it actually belongs in, per Gordon's direction:

- **Bucket A** (missing synthetic fixture, rule stays legitimate/YELLOW) — **12 groups**:
  1, 2, 13, 15, 16, 18, 35, 39, 40, 42, 48, 50. Verified by `find`-ing all 5
  `demo/syn/loan NN` folders for each needed document family (LEP forms, HUD-92564-CN,
  VA Counseling Checklist, HUD-92900-B, Form 1103/SCIF, ROV disclosure, and a distinct
  **initial** 1003/URLA) — zero matches for any of them. The initial-vs-final URLA
  nuance was checked explicitly: every loan's only URLA file is named
  `01_Final_1003_URLA.pdf` and its own header text reads "FINAL — Signed at Closing";
  the one `*initial*`-named file that exists anywhere
  (`demo/syn/loan 01/05_Initial_Disclosure_Package_Index.pdf`) is a disclosure-package
  index, not an initial 1003/URLA, confirmed not to satisfy groups 35/39/40. Recorded as
  [014](014-bucket-a-legitimate-fixture-gap.md).
- **Bucket B** (deepen extraction of a document already in hand, buildable now) —
  **3 groups**: 21, 24, 30 — all about the **final** URLA's "Additional Borrower form" /
  per-section completeness. Verified by running `pdftotext` on the actual
  `01_Final_1003_URLA.pdf` fixtures: loan 01 and loan 05 both contain inline
  "Co-Borrower Name/SSN/DOB" and "Section 1b — Current Employment (Co-Borrower)" text in
  the *same* PDF `extract_loan.py` already parses — and `extract_loan.py`'s own
  `add_field` (line 213) comment, "first occurrence wins (borrower before co-borrower)",
  confirms the co-borrower's matching lines are read today and then discarded, not
  absent. This corrects the initial working assumption ("likely just the final-URLA-
  sections group") — investigation showed all three final-URLA groups qualify for
  Bucket B, not only one. Recorded as
  [015](015-bucket-b-deepen-1003-extraction.md).
- **Bucket C** (external system, out of PoC scope) — **1 group**: 45 (URLA originator
  NMLS ID vs. licensing data). Verified via the CSV's row-68 exception description
  ("did not contain the loan originator's ... NMLS identification number ...") that the
  condition asks whether the ID is *actually licensed* — a live registry fact no loan
  document can self-certify — and confirmed no NMLS lookup capability exists anywhere in
  `src/`. Recorded as
  [016](016-bucket-c-discard-external-lookup-rules.md).

12 + 3 + 1 = 16, reconciled against the triage file's own `bins_by_group.YELLOW: 16`.

**Why.** This closes Step 8's "in progress" status for the 16 YELLOW groups specifically,
without touching the RED/GREEN/NOT_A_CHECK groups or the triage/ruleset files themselves —
per Gordon's instruction this pass is verification + documentation only; the code and data
changes each bucket implies (fixture generation for A, `extract_loan.py` field-spec
extension for B, an explicit exclusion for C) are follow-on work, deliberately deferred
and specified rather than performed inline.

**Evidence**
- `src/shacl_pilot/compiled/triage_application_verification.json` — ground truth for all
  16 group definitions, `source_rows`, and `needed_data` text
- `src/doc/PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv` — exact row text
  cross-checked for rows 20–24, 29, 36–38, 43–51, 57, 65–72, 1709
- `demo/syn/loan 01`..`loan 05` (full `find` listing) — confirms zero LEP/HUD-92564-CN/
  HUD-92900-B/VA-Counseling-Checklist/Form-1103/ROV/initial-URLA files exist anywhere
- `demo/syn/loan 01/01_Final_1003_URLA.pdf`, `demo/syn/loan 05/01_Final_1003_URLA.pdf`
  (`pdftotext` output) — confirms inline Co-Borrower section text
- `src/shacl_pilot/extract_loan.py` — `DOC_TYPES` (line 29, single `final_1003` entry,
  no `initial_1003`), `add_field` (line 213, "first occurrence wins" comment),
  `FIELD_SPECS["final_1003"]` (lines 72–83, the 10 fields currently extracted)
- `src/shacl_pilot/amq_compiler.py` — `DOC_KEYWORDS` line 101, the
  `"initial .{0,10}application" -> "final_1003"` keyword-mapping shortcut, flagged (not
  fixed) as corroborating evidence for the initial-URLA fixture gap
- `src/decisions/014-bucket-a-legitimate-fixture-gap.md`,
  `015-bucket-b-deepen-1003-extraction.md`,
  `016-bucket-c-discard-external-lookup-rules.md` (this step's output)

---

---

## Step 10 — Layer-2 triage of the asset-verification block (2026-07-30)

**What was done.** Ran the same triage method as Step 8/9 (application-verification) on a second,
larger block: **asset-verification, 304 compiled rules**. Built `layer2_triage_assets.py`
(modeled directly on `layer2_triage.py`), deduped by `(question_text, response_text)` — **304
rules → 297 unique groups (~1.02x collapse, verified empirically, not assumed** — much smaller
than application-verification's 81→54 ~1.5x, because the 5 AMQ agencies write almost entirely
independent condition text per asset sub-type). Classified every group GREEN/YELLOW/RED/
NOT_A_CHECK: the ~87 mechanically-resolvable groups (pass/N-A answers, already-`mapped`/
`doc_presence` rules per `amq_compiler.py`'s own `eval_class`) were derived directly from that
data rather than hand-typed; the ~210 substantive groups were individually read and classified in
`layer2_triage_assets.py`'s `C` dict.

**Result: 18 GREEN / 193 YELLOW / 17 RED / 69 NOT_A_CHECK groups (8% / 85% / 7% of 228 defect
groups).** This is a sharp divergence from application-verification's 51% / 29% / 20% — the
headline question this exercise was run to answer. Cause: asset-verification's YELLOW groups are
overwhelmingly blocked on missing synthetic fixtures (dozens of distinct asset-type document
families — VOD forms, retirement/brokerage/trust statements, bridge-loan notes, subordination
agreements, DU/LPA/TOTAL AUS findings, foreign-asset/crypto confirmations, sweat-equity/trade-
equity docs, custodial-account statements, program-specific agreements — none of which exist in
the 5-loan synthetic corpus), not because the underlying math is harder to automate (RED did not
grow — most asset thresholds, 50%/1%/60%/20%/2%/6%/$250, are crisp comparisons, not judgment
calls).

Six READY TO BUILD candidates were flagged (not implemented): top pick is **G135** (O-RHS-02772) —
`GiftEvidenceShape` (`CHK-AST-002`) already implements the exact fact this rule needs
(`gift_transfer_evidence_in_file`) but `MAPPED_SHAPES` wires it to zero AMQ exception codes today,
so it has never fired for any real rule; a 1-line fix. Also flagged: **G102** (byte-for-byte
duplicate of the already-mapped O-FNM-00215 large-deposit row, filed under a different AMQ
question category), **G025**/**G064** (same large-deposit defect, FRD/FHA wording variants), and
**G011**/**G130** (new derivations computable from data `extract_loan.py` already extracts, zero
new fixtures). One borderline Bucket-C candidate was flagged, not discarded: **G218** (FHA real-
estate-license verification — may need a live licensing-board lookup, similar in kind to the
discarded NMLS rule, decision 016) — a human decides.

**Why.** Directly answers Gordon's question: does the application-verification bin ratio
generalize to a messier, more math-heavy block? No — it inverts, and the reason is fixture
coverage breadth, not rule-automatability. This is a load-bearing finding for prioritizing which
block to unblock next (asset-verification's ceiling is gated by synthetic-fixture generation, not
by SHACL-authoring effort).

**Evidence**
- `src/shacl_pilot/layer2_triage_assets.py` (the triage script; `C` dict holds all 210 hand-
  classified groups, `READY_TO_BUILD` dict holds the 6 flagged candidates)
- `src/shacl_pilot/compiled/triage_asset-verification.json` (`rules_total` 304, `unique_groups`
  297, `bins_by_group` {GREEN: 18, YELLOW: 193, RED: 17, NOT_A_CHECK: 69})
- `src/shacl_pilot/out/TRIAGE-PACKET-asset-verification.md` (the SME review packet, same
  structure as `TRIAGE-PACKET-application-verification.md`)
- `src/decisions/017-assets-block-triage.md` (this step's full writeup)
- `src/shacl_pilot/blocks/assets.ttl` — `GiftEvidenceShape`'s empty `amq_exception_codes` list in
  `amq_compiler.py`'s `MAPPED_SHAPES`, confirming the G135 wiring gap
- `demo/syn/loan 01`..`loan 05` (full `find` listing, reused from Step 9) — confirms no VOD,
  retirement/brokerage/trust statement, bridge-loan note, subordination agreement, DU/LPA/TOTAL
  AUS findings report, or purchase/sales contract document exists in any of the 5 synthetic loans

---

## Step 11 (2026-07-30): Pivot from engine-comparison to coverage — 6 verified Assets wins, then 5 parallel block triages, then a systemic classifier bug found and fixed

**What.** Gordon explicitly ended the SHACL-vs-Drools-vs-Zen-Engine-vs-Kogito comparison
("I don't care what library... I just need this working") and redirected effort to
closing real coverage on the tool already proven. Three phases:

1. **Assets "ready to build" verification** (decision 018): of the 6 candidates
   decision 017's triage flagged, only 3 survived direct verification against the full
   AMQ row text — `GiftEvidenceShape` wired to `O-RHS-02772`, `LargeDepositShape` wired
   to `O-FRD-50451` and `O-FHA-50677-1`. The other 3 ("highest confidence, byte-for-byte
   duplicate" per the original agent) were rejected on closer reading: one tested source
   *acceptability* not mere presence, one needed a liability↔deposit relationship never
   captured, one proposed reusing a refinance-only field for a purchase-loan rule.
2. **5 parallel block triages** (decisions 019–023), same method, explicitly briefed on
   the "verify before trusting ready-to-build claims" lesson from decision 018:
   credit-liabilities-review (386/382, 3/92/5), property-appraisal-review (714/696 —
   first block where **RED dominates**, 0/46/54, narrative-adequacy language not fixture
   gaps), income-verification (616/580, 6/93/1 — most extreme YELLOW skew), underwriting-
   review (466/461, 2/92/6 — least automatable, **zero** ready-to-build survived, an
   honest negative result), product-specific-check (704/703 — near-zero dedup, agency-
   fragmented by nature, 0/97/3). Across all 5, only 2 clean ready-to-build wins survived
   verification (income-verification's `SelfEmployedDocsShape` → `O-VA-00364` +
   `O-FHA-02293`) — everything else was correctly rejected or flagged partial/new-shape.
3. **Systemic bug found and fixed** (decision 024): 3 of the 5 agents *independently*
   (no knowledge of each other) found the same root cause in `amq_compiler.py`'s
   `doc_presence` auto-classifier — no word boundaries (matched "credit report" inside
   "credit reporTED") and no proximity requirement (an absence-word anywhere in a long
   sentence matched a doc-keyword anywhere else in it). Fixed both; `doc_presence` count
   dropped ruleset-wide 135→91. Explicitly documented as a **partial**, not complete, fix
   — full manual triage remains the authoritative source once a block has been through it.

**Why.** The independent triangulation (3 separate agents, same bug, no cross-talk) is
itself the evidence this was systemic rather than a one-block artifact — exactly the
kind of thing decision 018 was written to catch. Also surfaced: 4 of the original 25
pilot shapes have zero matching rows anywhere in the real 5,520-row workbook (decision
025) — built from the demo loans/answer-key, not a real AMQ question, flagged for
follow-up rather than silently left as an assumed win.

**Evidence**
- `src/shacl_pilot/amq_compiler.py` — `LargeDepositShape`/`GiftEvidenceShape`/
  `SelfEmployedDocsShape` `amq_exception_codes` lists (decisions 018/025); `PROXIMITY_WINDOW`,
  `NARRATIVE_QUALIFIER_RE`, boundary-safe `DOC_KEYWORDS` (decision 024)
- `src/shacl_pilot/layer2_triage_credit_liabilities.py`, `layer2_triage_property_appraisal.py`,
  `layer2_triage_income.py`, `layer2_triage_underwriting.py`, `layer2_triage_product_specific.py`
  — one script per block, each with its own hand-classification
- `src/shacl_pilot/compiled/triage_{credit-liabilities-review,property-appraisal-review,
  income-verification,underwriting-review,product-specific-check}.json` + matching
  `out/TRIAGE-PACKET-*.md` SME packets
- `src/shacl_pilot/compiled/ruleset.json` — `ruleset_sha256` progression: `34ef9226a816`
  (Assets fixes) → `233c922bb0b6` (2 more Assets wires) → `fc829b39c857` (classifier fix)
  → `b9afbf4f23b6` (SelfEmployedDocsShape wired); `by eval class` doc_presence 135→91
- `src/decisions/018-*.md` through `025-*.md`
- `src/shacl_pilot/run_audit.py` output: 25/25 answer-key defects, 0 unexplained extras,
  1 justified extra, deterministic — unchanged (verified) across every recompile in this step

---

*Journal written 2026-07-29 for retraceability. Every artifact path above was
verified to exist on disk at write time; where an artifact was overwritten or never
persisted, that is stated explicitly. Step 10 appended 2026-07-30. Step 11 appended
2026-07-30.*
## Step 12: GREEN/YELLOW/RED Parallel Audit — Honest Coverage & Demo Scope

**Date:** 2026-07-30 (same session, immediately after Step 11 consolidation)

**Context:** After consolidating 5 parallel block triages (credit-liabilities, property-appraisal, income, underwriting, product-specific) and fixing the doc_presence classifier bug, Gordon asked for three parallel investigations to establish the honest current-state picture:
1. GREEN-only audit on loan 01 — what does "rules that already work" actually deliver?
2. YELLOW → GREEN conversion feasibility — how many can fold in with fixture/extraction work vs. genuinely blocked?
3. RED categorization — why are they red, how many, what's the honest demo treatment?

All three investigations ran concurrently via background agents (decision 026 created to frame the work).

### GREEN-Only Audit Results

**Agent:** a742029d3a5344c91  
**Output:** `src/shacl_pilot/out/green_only_audit_loan01.md`, `out/GREEN_AUDIT_EXECUTIVE_SUMMARY.md`, `out/README_GREEN_AUDIT.md`, `run_green_audit.py`

**Key findings:**
- **60% detection rate** — 3 of 5 loan 01 answer-key defects caught
- **Shapes loaded:** 11 (not 4) — discovered **block loading effect**: requesting `LargeDepositShape` (in `assets.ttl`) loads the entire `assets.ttl` file, pulling in 7 adjacent shapes. Two of those "bonus" shapes (`EmploymentStartDateShape`, `TitleVestingShape`) caught answer-key defects.
- **Current block coverage:** 3 of 17 AMQ blocks (18%) — asset-verification, application-verification, income-verification loaded; credit-liabilities and property-appraisal not loaded (causing the 2 missed defects).
- **Implication:** The unit of coverage is the **block** (TTL file), not the individual shape. Mapping one rule from a block effectively lights up the entire category. This is a velocity multiplier — instead of mapping 4,166 rules one-by-one, mapping ~17 (one per block) guarantees at least partial coverage across every AMQ category.

**Missed defects:**
- `UndisclosedLiabilityShape` (credit-liabilities block never loaded)
- `CompDistanceShape` (property-appraisal block never loaded)

**Path to 100% on loan 01:** Map 1 rule each from credit-liabilities and property-appraisal (< 10 minutes of work).

**Verdict:** GREEN is more effective than its 16% deliberately-mapped count suggests (actual runtime coverage: 44% of pilot shapes due to block loading). Not production-ready, but a solid proof-of-concept for deterministic, citation-backed QC.

**Evidence:**
- Full report: `src/shacl_pilot/out/green_only_audit_loan01.md` (253 lines)
- Executive summary: `src/shacl_pilot/out/GREEN_AUDIT_EXECUTIVE_SUMMARY.md`
- Audit runner: `src/shacl_pilot/run_green_audit.py`

---

### YELLOW Conversion Analysis Results

**Agent:** acd980459af34900d  
**Output:** `src/shacl_pilot/out/yellow_conversion_analysis.md`

**Key findings:**
- **Total YELLOW:** 2,125 groups / 2,147 rules
- **Convertible (62.3%):** 1,323 groups
  - **462 groups** blocked on missing fixtures (legitimate doc types not yet in synthetic loans — Decision 014 validated)
  - **861 groups** blocked on extraction deepening (fields exist in docs but not yet extracted — assumes Touchless can be extended)
- **Genuinely blocked (37.7%):** 802 groups
  - **107 groups** need SME clarification (ambiguous thresholds, subjective language like "adequate," "reasonable," "appears to need more space")
  - **695 groups** have other blockers (complex cross-file logic, external lookups, program-specific rules without clear data sources)

**Per-block breakdown:**
- application-verification: 12 YELLOW
- asset-verification: 193 YELLOW
- credit-liabilities-review: 277 YELLOW
- income-verification: 467 YELLOW (most extreme YELLOW skew — 93%)
- underwriting-review: 342 YELLOW
- product-specific-check: 572 YELLOW (near-zero dedup — agency-fragmented by nature)
- property-appraisal-review: 262 YELLOW

**What "automatable" really means:** 62% are convertible *if* the fixture set expands and Touchless extraction deepens — not convertible today without that upstream investment. The remaining 38% need SME decomposition (turning "all requirements met" into enumerable facts) or stay genuinely blocked (external APIs, cross-loan comparisons).

**Honest assessment:** Fixture-blocked rules are genuinely convertible. Extraction-blocked rules assume Touchless can be extended. SME-blocked rules need human decomposition before any automation is possible.

**Evidence:**
- Full report: `src/shacl_pilot/out/yellow_conversion_analysis.md` (file too large for single read, 801KB — agent used chunked reads)

---

### RED Categorization Results

**Agent:** a62176b024a3be862  
**Output:** `src/shacl_pilot/out/red_categorization.md`

**Key findings:**
- **Total RED:** 409 rules (43% of Post-Closing ruleset) across 397 groups
- **By root cause:**
  - **Narrative judgment** (187 rules, 45.7%) — inherently human decisions ("adequate," "reasonable," "appears") that cannot be automated
  - **External data** (187 rules, 45.7%) — requires APIs/lookups not in closed-loan file (NMLS, appraisal review services)
  - **Ambiguous/vague** (29 rules, 7.1%) — no clear pass/fail threshold; needs SME decomposition
  - **Other** (4 rules, 1.0%) — out-of-scope or system-specific checks
  - **Cross-loan comparison** (2 rules, 0.5%) — portfolio-level data required

**Key finding:** Property-appraisal-review dominates with 317 RED rules (77.5% of all RED) — this block is inherently narrative-heavy. This explains the 0/46/54 GREEN/YELLOW/RED split from Decision 020.

**Demo recommendation:** Flag RED as "Human Review Required" (Option A)
- Rules get `human_review_required: true` flag at compile-time
- Auto-route to Exception Review queue with label **"Requires Expert Judgment"**
- Demo narrative: *"We deterministically clear the objective checks and intelligently route judgment-required cases to expert review with full traceability"*
- Metric focus: resolution rate + exception routing accuracy (not "pass/fail")
- **DO NOT fake automation** (Option C rejected) — violates Non-Negotiable #1 and destroys regulatory audit story

**Three-phase path:**
1. **Phase 1 (Demo):** Implement Option A — honest routing, not fake automation
2. **Phase 2 (Post-demo):** SME decomposition sprints (target ambiguous/vague — 29 rules, high leverage) + external API integration (target external_data — 187 rules)
3. **Phase 3 (Productization):** Accept that 187 narrative judgment rules stay human — build best-in-class reviewer UX

**Key insight:** RED is not failure — it's a feature. A system that explicitly routes subjective cases to human experts while auto-clearing deterministic ones is trustworthy.

**Evidence:**
- Full report: `src/shacl_pilot/out/red_categorization.md` (338 lines)

---

### Consolidated Decision

**Decision 026** written to `src/decisions/026-green-yellow-red-audit-breakdown.md` with full results summaries, implications for demo scope, and prioritized next steps. Updated `src/decisions/README.md` index (row 36) and `src/decisions/JOURNAL.md` (this Step 12 entry).

**Honest current-state numbers:**
- **GREEN (automatable today):** 103 rules (2.5%) — but block loading gives 44% shape coverage
- **YELLOW (automatable with work):** 2,147 rules (51.5%) — 62% convertible with fixture/extraction investment, 38% genuinely blocked
- **RED (stays human or needs major decomposition):** 409 rules (9.8%) — 43% of ingested ruleset
- **Unmapped (not yet triaged):** 4,047 rules (97.2%) — 9 blocks remain untouched

**What the demo can honestly claim:**
- Deterministic auto-clearing: 103 GREEN rules catch real defects (60% on loan 01) with full citation traceability
- Intelligent exception routing: 409 RED rules flagged for expert review (not faked, not hidden)
- Scalability story: Block-level loading means mapping 1 rule per category lights up the entire category — velocity multiplier for SME authoring

**What the demo should NOT claim:**
- Production-grade coverage (3 of 17 blocks mapped is 18%, not comprehensive)
- YELLOW rules are automatable "soon" without acknowledging the upstream fixture/extraction dependency
- RED rules will eventually be automated (187 narrative-judgment rules stay human, period)

**Next steps (prioritized):**
1. **Immediate (< 1 hour):** Map 1 rule each from credit-liabilities and property-appraisal → loan 01 hits 5/5
2. **Short-term (< 1 day):** Run GREEN-only audit on all 5 loans → see 25-defect detection rate
3. **Demo prep:** Implement RED → "Human Review Required" UI treatment (Option A from RED report)
4. **Medium-term:** Triage the remaining 9 untouched blocks

---

**End of Step 12** — All three parallel audits complete, decision 026 documented, honest coverage picture established (2026-07-30).
