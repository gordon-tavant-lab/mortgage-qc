# 020 — Layer-2 triage of the property-appraisal-review block: the largest block (714 rules), effectively zero GREEN, and the same false-GREEN amq_compiler.py bug found independently a second time

**Status:** Accepted 2026-07-30 (Gordon — triage the single largest AMQ block, property-appraisal-review,
714 compiled rules, using the same method as the three prior triages)

## Decision
Triaged all 714 compiled `property-appraisal-review` rules the same way as the prior three blocks
(`layer2_triage_property_appraisal.py`, modeled on `layer2_triage.py`/`layer2_triage_assets.py`):
dedup by `(question_text, response_text)` → 696 unique groups, classify every group GREEN/YELLOW/
RED/NOT_A_CHECK with real per-group rationale, emit `compiled/triage_property-appraisal-review.json`
+ `out/TRIAGE-PACKET-property-appraisal-review.md`. Result:

| Bin | Groups | Rules | % of defect groups | application-verification | asset-verification | credit-liabilities |
|---|---|---|---|---|---|---|
| GREEN | 2 | 2 | 0% | 51% | 8% | 3% |
| YELLOW | 262 | 263 | 46% | 29% | 85% | 92% |
| RED | 310 | 317 | 54% | 20% | 7% | 5% |
| NOT_A_CHECK | 122 | 132 | — | — | — | — |

**Headline: this is the first block where RED, not YELLOW, is the dominant bin — because appraisal
review is dominated by narrative-commentary-adequacy language, not documentation presence or crisp
math.** Unlike asset-verification and credit-liabilities-review (both YELLOW-dominated because the
5-loan synthetic corpus simply lacks the relevant document families), property-appraisal-review's
714 rows are saturated with phrases like "without comment," "no commentary," "not adequately
supported," "not analyzed," "inconsistent," "not addressed," "acceptable/unacceptable," and
open-ended "all requirements... not met" catch-alls — genuine human-judgment calls on the
appraiser's free-text narrative that this pilot's regex-based field extractor (`extract_loan.py`)
does not capture and could not capture without full semantic parsing of the appraisal's write-up
sections, a fundamentally different and much harder problem than presence/threshold checks. GREEN
is effectively **zero** (2 of 696 groups, both Notice-of-Value presence checks) — every one of the
7 pre-existing property-appraisal SHACL shapes was searched for a safe extension and found to have
none (see below).

## Method notes (deliberate, and disclosed up front — see the module docstring)
1. **Dedup**: 714 rules → 696 groups, ~1.03x — matches asset-verification's ~1.02x and credit-
   liabilities' ~1.01x, not application-verification's ~1.5x; verified, not assumed.
2. **Mechanical resolution, widened one more notch**: `PASS_RE` (`^(Yes\b|Not Applicable)`, widened
   to bare "Yes" without a comma — two real rows, G086 and G611, are literally just "Yes" and would
   otherwise slip through) **plus a second, independently useful mechanical signal**: every rule
   sharing a (question, condition) pair with a **blank Exception Code** in the source CSV is a
   screening/applicability branch, not a scoreable defect — confirmed on the "(FHA/FNM/FRD/RHS/VA)
   Is there an appraisal in the file? → No, an appraisal is not required" rows (G001/G003/G005/
   G007/G009), which are exempt-from-appraisal branches (e.g. value-acceptance waivers), not a
   pass/fail-able condition — the real defect is the sibling row ("...did not contain an appraisal
   report as required," non-blank Exception Code). Same screening-vs-defect pattern as application-
   verification's group 10 and asset-verification's group 291, found here via a cleaner mechanical
   signal (blank Exception Code) than either prior script used.
3. **Given the scale (696 groups, only 122 + 2 mechanically resolved), hand-authoring all ~570
   remaining entries at the same prose depth as the ~210-entry asset-verification `C` dict was not
   achievable at reviewable quality in the time available.** Disclosed method deviation: a small,
   individually-verified `OVERRIDES` dict (46 groups — every existing-shape near-miss, every
   Bucket-C flag, every doc_presence-mismap correction found by spot-check) plus a documented,
   auditable regex-family classifier (`classify_family()`) for the remaining ~526 — every row's
   rationale still cites its own actual condition text (not a canned string), and the classifier's
   priority order (external-DB → form-number → photo/exhibit → narrative-judgment → bare-catch-all
   → numeric-threshold → condo/co-op-project-doc → conservative-default-RED) is fully documented in
   the script. This is a real, disclosed method difference from the three prior triages, not a
   shortcut hidden from the SME — flagged prominently in the packet's own header note.
4. **Classifier spot-checked, not trusted blind**: sampled ~90 individual rows across four separate
   random draws and read each against its full condition text. Found and fixed four real
   classifier errors this way: (a) an "external-DB" false trigger where `exception_description`
   mentioned a submission channel (DELRAP) but the row's actual, primary condition was a plain
   Form HUD-9992 presence check — reordered the classifier so form-number signals win over
   incidental exception_description mentions; (b) two rows misrouted to RED by the incidental word
   "deemed" (G277/G278 — both are actually water-safety-evidence presence checks); (c) two rows
   misrouted to a "numeric threshold" YELLOW because a digit appeared in the **question** text, not
   the response (G020's property-flip catch-all, G353's neighborhood-section-completeness judgment)
   — both correctly RED on inspection; (d) the largest and most consequential — see below.

## The zero-exception-code shapes: searched exhaustively, found no safe match
`amq_compiler.py`'s `MAPPED_SHAPES` lists **seven** shapes already keyed to `property-appraisal-
review` — `CompDistanceShape`, `MprCompletionCertShape`, `TermiteInspectionShape`,
`StaleAppraisalShape`, `WellSepticShape`, `SiteValueJustificationShape`, `UsdaEligibilityDocShape`
— **all seven wired to zero `amq_exception_codes`**, the same latent bug decisions 017/018 found
and partly fixed for `LargeDepositShape`/`GiftEvidenceShape`, and decision 019 found unfixable for
`UndisclosedLiabilityShape`/`CashoutMortgageLateShape`. Every AMQ row in this block was searched
(by keyword — "mile," "termite"/"NPMA," "well"/"septic," "442"/"MPR"/"completion," "120 days"/
"recert," "site value," "USDA"/"rural"/"eligib" — cross-checked against the raw source CSV
directly, not just the compiled groups) for a real match to each shape's actual SPARQL logic (read
from `blocks/property_appraisal.ttl`, not guessed from the shape's name).

**Three of the seven have no matching AMQ row in this workbook at all.** Grepping the raw CSV
(`PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv`) for "mile" within the Property - Appraisal
category, for "site value," and for "rural eligib"/"eligib rural" — all **zero hits**. This
confirms what `CompDistanceShape`'s own SPARQL comment already says ("the 5.0-mile threshold is
NOT traceable to a source AMQ row... Status: UNSPECIFIED"): `CompDistanceShape`,
`SiteValueJustificationShape`, and `UsdaEligibilityDocShape` predate the full-workbook compile
(decision 009) and were authored directly against the loan-01 demo scenario with SME-placeholder
thresholds, not derived from any row in this 5,520-row workbook. This is a **permanent structural
fact**, not a temporary gap — there is no AMQ row to ever wire these three shapes to from this
sheet, only from an SME-supplied threshold or a future Pre-Funding-sheet ingestion (never done —
see the CLAUDE.md program-gate note).

**The other four (`TermiteInspectionShape`, `WellSepticShape`, `MprCompletionCertShape`,
`StaleAppraisalShape`) do have topically related AMQ rows — roughly 15 candidates found across
them — and every single one, read in full, tests a materially different real-world condition:**

- **Termite** (3 candidates): G151 (VA) names three specific NPMA form numbers plus an unmodeled
  "not signed" clause; G375 (RHS) is the closest match (same real fact — termite/pest inspection
  presence) but is conditioned on an unmodeled "where required by ... State law" applicability test
  the existing shape's SPARQL doesn't check (flagged WORTH SME REVIEW, not wired); G279 (FHA) tests
  post-treatment water-safety documentation, a different fact entirely.
- **Well/septic** (7 candidates): every one adds a qualifier our presence-only fact can't verify —
  source authority ("disinterested third party," "qualified lab," G281/G283 — the exact same
  acceptability-vs-presence trap decision 018 rejected O-FRD-58101 for), staleness (a 180-day age
  test, G282/G493 — our fact is presence-only, no date), or a different real-world system entirely
  (a COMMUNITY water/sewage system, G423, vs. the shape's PRIVATE well-and-septic scope).
- **MPR/Form 442** (3 candidates, G040/G676/G677, all Freddie Mac): rejected on the SAME "field
  would never populate for the loans this rule targets" ground decision 018 used for
  `O-RHS-57768` — `extract_loan.py`'s `doc_present_fha_form_442` fact is computed **only** for
  `mortgage_type == "FHA"` (`EXPECTED_DOCS_BY_PROGRAM` is keyed `"FHA"`/`"VA"` only); wiring a
  Freddie Mac exception code to `MprCompletionCertShape` would extend a shape whose fact never even
  gets computed for an FRD loan. Also a different real-world form use (appraisal-update
  revalidation vs. MPR-repair completion) — a double mismatch, not just a program-label mismatch.
- **Stale appraisal / 120 days** (3 candidates): G037 gates an AUS PIW **offer's** validity, not
  the appraisal's own age; G039 is about **reusing a prior** appraisal (our fact only measures this
  loan's own appraisal's age); G041 is keyed to **disbursement** date, which can post-date closing
  for construction/escrow loans (our `appraisal_age_days_at_closing` derivation is closing-date
  based). None is a safe direct wire.

**Net: zero "ready to build" shape-extension candidates in this round** — the same honest result
decision 019 reported for credit-liabilities-review, now a second consecutive block. This is
reported as the finding, not treated as a triage gap, per the explicit instruction to under-claim
rather than repeat the Assets round's mistake.

## Two candidates worth building as NEW checks (not shape extensions), flagged not implemented
- **G270 (O-RHS-appraisal-age, row 4134)** — the closest near-miss in the entire block: RHS's
  "appraisal not completed within 180 days of closing" rule tests the **exact same fact**
  `StaleAppraisalShape` already computes (`appraisal_age_days_at_closing`), just a different
  threshold (180, not 120) **and**, unlike the existing shape, states no recertification-of-value
  exception that would cure it. Not proposed as an extension of `StaleAppraisalShape` itself
  (different threshold + different cure condition would change the shape's actual logic, not just
  its exception-code list) — flagged as the strongest genuinely-new-check candidate in this block,
  reusing an already-extracted field.
- **G096 (O-FNM comp-recency, row 4157)** — "comp not closed within 12 months and no explanation
  provided" is a two-part condition: the explanation half reuses the SAME `comp_explanation_present`
  boolean `CompDistanceShape` already checks. Flagged WORTH SME REVIEW, not proposed as a blind
  wire: `comp_explanation_present` is a single generic "is there ANY addenda/explanation text"
  flag, not specific to WHICH condition it explains (comp distance vs. comp recency) — reusing it
  here risks the same over-general-fact trap as the assets triage's gift-transfer-evidence
  near-misses (G108/G127/G131/G296). The 12-months half also needs a new comp-closing-date field,
  which does not exist today (the `comps` entity has `comp_num`/`address`/`distance_miles`/
  `sale_price`/`gla`/`adjusted_sale_price` — no closing date).

## The consequential finding: amq_compiler.py's own doc_presence classifier has a false-GREEN bug here too — independently confirming decision 019's finding, not a one-off
Decision 019 (credit-liabilities-review, triaged by a separate parallel session) found that
`amq_compiler.py`'s mechanical `eval_class == "doc_presence"` signal — which both prior scripts
(application-verification, asset-verification) trusted as an automatic GREEN — silently
mis-classified 19 of 24 rows in that block as "document present" checks when the real condition was
a compound narrative/derivation fact that merely happened to share a keyword with a document type.
**The same bug, independently discovered here, is worse in this block: of the 35 rules `classify_eval()`
tags `doc_presence`, 33 target the generic `"appraisal"` document type — a document that is, in
this pilot's synthetic corpus, essentially always present (every one of the 5 loan folders has
exactly one Appraisal Summary PDF).** `amq_compiler.py`'s `DOC_KEYWORDS` list matches `"appraisal"`
as a broad, last-resort catch-all against any appraisal-adjacent exception text ending in "not
provided/missing/not in file," but the overwhelming majority of those 33 rows are actually about a
**specific sub-document, exhibit, certification, letter, or narrative analysis missing from
within** an appraisal report that itself always exists — a runtime check against generic
appraisal-doc presence would find the document present and **silently PASS every one of these real
defects, never firing**. Concretely: "Appraisal is missing the appraiser's certification,
statement of assumptions & limiting conditions" (G257/G381), "Building sketch, required
photographs... not included" (G531), "Correction in writing... by appraiser not in file" (G154),
and "Appraisal transfer letter from original lender not in the file" (G179) all mechanically
auto-classify `doc_presence` → target `"appraisal"` → would-be-GREEN, when the real fact needed is
a **specific missing exhibit/letter/certification**, not the whole document.

Only **2 of the 35** survive as genuine, already-working checks (`va_nov` target — a genuinely
distinct, correctly-modeled document type — G141 and G203). A third `va_nov`-target row, G204,
initially looked safe by the same eval_target test but turned out on full-text reading to require
evidence of the SAR's market-data research and recommendation — a fact `amq_compiler.py`'s `"NOV"`
keyword match pointed at the wrong document; reclassified to YELLOW. All 33 mismapped rows were
individually reclassified by hand (17 to YELLOW as genuine but differently-fixtured presence
checks; the rest RED where the real condition is narrative-adequacy, e.g. "Contract not analyzed
&/or analysis not provided," G173) — see `OVERRIDES` in `layer2_triage_property_appraisal.py`.
**`amq_compiler.py` itself was NOT modified** (off-limits for this exercise, same as decisions
017-019) — flagged here, alongside decision 019's report, for a human to patch: the
`doc_presence` branch of `classify_eval()` needs its generic, catch-most keywords (especially
`"appraisal"`, matched last and broadest in `DOC_KEYWORDS`) to require the missing-document
language to describe the WHOLE document, not any exhibit/section/certification/analysis within an
always-present one. **This is now the second independent triage session (credit-liabilities and
property-appraisal, run in parallel by different agents) to find the same class of bug in the same
function** — strong evidence this is a systemic `amq_compiler.py` design issue, not a one-off
misclassification, and should be prioritized accordingly when someone next touches that file.

A smaller, related compiler gap: the five "(agency) Is there an appraisal in the file? → No, the
loan file did not contain an appraisal report as required" rows (G002/G004/G006/G008/G010) are
conceptually the exact same doc-presence check `amq_compiler.py` already auto-compiles elsewhere in
this block, but this specific phrasing ("did not contain... as required") doesn't match
`NOT_IN_FILE_RE`'s substring list ("not in .{0,20}file|not provided|missing"), so they fall through
to `unmapped` instead. Classified YELLOW with the specific regex-widening fix named, not blindly
called GREEN, since the mechanism that would make it GREEN doesn't actually fire for these rows
today.

## Bucket-C-style external-registry candidates (decision 016 precedent — flagged, not discarded)
Several rows reference a live external system this pilot has no integration with: Condo Project
Manager (`CPM`), FHA Connection (`FHAC`), UCDP, DELRAP/HRAP, the HUD-approved-condominium-projects
list, VeroSCORE, WebLGY, and state real-estate/appraiser licensing-board status. All flagged YELLOW
with an explicit Bucket-C note in the packet, same as decision 016's NMLS precedent and decision
017's RE-license candidate — **not** unilaterally discarded from the compiled ruleset; a human
should decide.

## The single biggest fixture gap: an entire condo/co-op/PUD/leasehold/ADU project-documentation family, absent in full
147 of the 262 YELLOW groups trace to one root cause: **no condo/co-op/PUD project-review document
of any kind — HOA financial statements, project questionnaires (Form 1076/1076A, HUD-9991/9992),
litigation disclosures, budget/reserve data, CPM/PAR status — exists in any of the 5 synthetic
loans.** Each loan folder has exactly one Appraisal Summary PDF and nothing at the project level.
This is a larger single gap in scope than any one document family found in either prior triage
(asset-verification's VOD/AUS-findings gap or credit-liabilities' near-total absence of adverse
credit) — a natural next-fixture-generation priority if this block's YELLOW rate is ever to move,
though building it would still leave the RED-side narrative-commentary problem (54% of this block)
completely untouched, since that requires a different kind of solution entirely (semantic parsing
of free text, or accepting it as permanently human).

## Guide-grounding note
Confirmed `compiled/selling_guide_index.json` carries a full B4-1.x/"Appraisal Requirements" and
B4-2.x/"Project Standards" chapter set (50 `B4-` topics total — Unacceptable Appraisal Practices,
Appraisal Report Forms and Exhibits, Desktop/Hybrid Appraisals, the full Subject/Neighborhood/Site/
Improvements/Sales-Comparison/Cost-Income section-by-section chapters, Condo/Co-op/Leasehold/
Community-Land-Trust/Mixed-Use/Environmental-Hazard appraisal-requirements chapters) before citing
anything — the existing `retrieve_topics()` token-overlap function (unchanged from the reference
scripts) matches these titles well against this block's own question-text phrasing ("Were all
Neighborhood section... requirements met?" etc.), confirmed by spot-checking several GENERIC/O-FNM
groups' guide candidates in the packet.

## What was NOT done (per instruction)
No `.ttl`, `extract_loan.py`, `amq_compiler.py`, or `run_audit.py` edit was made. `README.md`/
`JOURNAL.md` were not touched (other parallel sessions own those). This is triage + documentation
only, identical scope to the three prior rounds.

## Cross-links
[[009]] (full-workbook compile), [[012]] (Selling Guide grounding corpus), [[014]]/[[015]]/[[016]]
(Bucket A/B/C precedents this triage's YELLOW/rejected-candidate reasoning follows), [[017]]/[[018]]
(the asset-verification triage and its ready-to-build verification discipline — the "test every
candidate against the full row text before calling it ready" method this triage applied even more
conservatively, arriving at zero survivors), [[019]] (credit-liabilities-review triage — the sibling
finding of the SAME `amq_compiler.py` doc_presence false-GREEN bug, discovered independently by a
parallel session on a different block, now confirmed as a systemic pattern rather than a one-off).
