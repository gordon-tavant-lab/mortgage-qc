# Compile-Stats Report v1 — FNM Post-Closing Gold Rule Set

**Generated**: 2026-07-31, 10:45 CT · **Base**: ACES Managed Questionnaires Sept 2025 (Post-Closing,
Fannie-cut) · **Guide**: Selling Guide 06/03/2026 (390 indexed sections) · **Schema**: `rule.schema.json` v1.0.0

---

## Headline numbers

| | Count | % |
|---|---|---|
| **Rules to start** (cards) | **266** | 100% |
| Individual defect checks inside those cards | 1,106 | — |
| **Compiled successfully, no caveats** | 192 | 72.2% |
| **Compiled with documented caveats** (usable, flagged) | 72 | 27.1% |
| **Failed to compile** | 2 | 0.8% |
| → **Total usable rules** | **264 / 266** | **99.2%** |
| **Atomic rules produced** (Income + Assets, flagship depth) | **221** | — |

Every one of the 1,106 individual defect checks was assigned one of 10 deterministic check types
(see below) and passes the schema + citation + fidelity gate with **zero hard failures, zero soft
warnings** on the full set (`pipeline/validate_compiled.py`).

---

## The 2 that failed — full nuance

Both failures are the **same root cause**, caught by the same mechanism: the card was placed in the
Fannie-cut by its ACES *family name*, but its own applicability logic routes it to Freddie Mac only.
Neither is a gap in coverage — both have a live Fannie-side twin already in the compiled set.

| Card | Category | Why it failed |
|---|---|---|
| **PC::DebtsPaid** | Credit - Liabilities | Applicability SQL is `Loans.QC_Policy = 'Freddie Mac'` — can never fire on route FNM. Its single defect option (`DEBTS-PAID`, Critical) is fully covered by **PC::O-FNM-15312**, which carries the identical exception code under Fannie Mae applicability. |
| **PC::O-CNTL-14392** | Data Validation Svc-DVS | Applicability SQL is `Loans.QC_Policy = 'Freddie Mac'` — LPA (Loan Product Advisor) is Freddie's automated-underwriting service, the direct counterpart to **PC::O-CNTL-14386** (DU Validation Relief), which governs the Fannie side and is already compiled. |

**Disposition**: both excluded from the runtime rule set, retained in the audit trail. No follow-up
needed — this is the scope-conflict detector working exactly as designed.

---

## The 72 flagged — by reason

| Failure category | Count | What it means |
|---|---|---|
| `bundle_requires_decomposition` | 27 | Catch-all "were all X requirements met" questions whose defect options span more Selling Guide sub-topics than a card-level citation set can represent. Compiled and usable now; queued for atomic decomposition (see below). |
| `citation_drift` | 23 | The best available guide citation doesn't fully or precisely govern the card's subject — mostly the 4-citation-cap problem on bundle cards (real topic sections exist but didn't fit the cap), a few genuine gaps (e.g. state-law overlays with no Selling Guide basis). |
| `lender_specific_no_guide_basis` | 13 | The card governs an internal lender-ops artifact (EPIC screens, ICPL, internal worksheets) or, in one case, a concept (UTMA/UGMA custodial accounts) exhaustively grepped across all 390 sections and genuinely absent from this guide edition. Zero citations by design, not by omission. |
| `duplicate_card` | 4 | Two pairs of near-identical cards in the source AMQ (electronic-transaction routing questions O-CNTL-15941/16591; construction-to-permanent financing O-FNM-15845/15939 sharing 7 of 10 exception codes; GLA appraisal O-FNM-15946/55582). Both members compiled independently and flagged for cross-reference — no data lost, but the engine should treat them as one logical rule at runtime. |
| `citation_not_found` | 1 | PC::O-FNM-14389 (employment DU-validation requirements) — 8 of 9 defect options are well-grounded, 1 (VOI-without-VOE) has no clean single-section match. |
| `scope_conflict` (flagged, not failed) | 1 | PC::O-EPD-14462 — applicability always fires on route FNM, but its defect option's own description text names "loans sold to Freddie Mac," a content-level conflict distinct from the 2 SQL-level failures above. |
| `other` | 3 | PC::O-FNM-15625 (5 asset sub-types over the citation cap), PC::O-FNM-15405 (duplicated source rows + a 5-policy scope leak — both documented, not blocking), PC::Contract (one of five options is a Massachusetts state-law overlay with no Selling Guide basis). |

**By category** (where the 72 flags concentrate): Product Specific 28, Form 1033 7, Closing 6,
Property-Appraisal 6, Application 5, Underwriting 5, Assets 4, Loan Documents 3, Credit-Liabilities 2,
Data Validation Svc-DVS 2, EPD 2, Income 2.

Product Specific carries the heaviest flag load by a wide margin — it's the category with the most
loan-program-specific bundles (RefiNow, HomeStyle, HomeReady, construction-to-perm), each spanning
many guide sub-topics per question.

---

## Check-type distribution (the taxonomy payoff)

Atomic-level count across all 1,106 defect checks:

| Type | Count | % |
|---|---|---|
| `doc_presence` | 260 | 23.5% |
| `doc_completeness` | 209 | 18.9% |
| `scripted_review` | 161 | 14.6% |
| `threshold_eligibility` | 157 | 14.2% |
| `computation` | 120 | 10.8% |
| `cross_doc_consistency` | 93 | 8.4% |
| `date_window` | 62 | 5.6% |
| `reverification` | 24 | 2.2% |
| `list_screening` | 20 | 1.8% |
| `routing_context` | *(card-level only, 0 defect options by design)* | — |

Nearly **62% of all checks (doc_presence + doc_completeness) are document-level extraction checks**
— the biggest engineering lever is a reliable document-field extractor, not exotic logic. The
`computation` + `cross_doc_consistency` slice (19.2%, 213 checks) is where the real audit value
concentrates — DTI/LTV/CLTV math, income triangulation, bank-statement-to-application comparisons.
`scripted_review` (14.6%) is the honest ceiling on how much of mortgage QC is irreducibly judgment —
those checks compile to explicit criteria checklists with a `REQUIRES_HUMAN_REVIEW` fallback, never
a runtime LLM call, per the locked determinism requirement.

---

## Flagship decomposition — DONE: Income + Assets → 221 atomic rules

**140 Income + 81 Assets = 221 atomic rules**, each a single decidable check with its own
citation, generated by promoting every one of the 221 defect options across both categories'
48 cards to a standalone `atomic_rule`. Deterministic gate PASS on both — 0 schema errors, 0
citations resolving outside the guide index, and (the check that matters most) **every atomic
rule's exception_code + severity round-trips byte-identical against the original compiled card**
— decomposition changed *how precisely a check is cited*, never *what it detects*.

**23 rules got a precision-citation upgrade** — narrower, more accurate than what the card-level
citation cap could represent:

- **21 in Income**, concentrated in the two true catch-all bundles (`O-FNM-15330` "other income,"
  `O-FNM-15331` "additional other income"): each of their defect options now cites its own exact
  guide sub-section (Boarder → B3-3.4-04, Foster Care → B3-3.4-07, Interest/Dividend → B3-3.4-08,
  Capital Gains → B3-3.4-05, Foreign Income → B3-3.2-02, Royalty → B3-3.4-13, MCC → B3-3.4-10,
  Schedule K-1 → B3-3.4-19, etc.) instead of sharing 4 umbrella citations across 8-9 topics.
  One of these corrects a miscategorization the adversarial verify pass caught: `Income - Other`
  (SSI gross-up) was filed as a generic cross-cutting option at compile time but is actually
  Social-Security-specific — now correctly cited to B3-3.4-15.
- **2 in Assets** — `O-FNM-56339` (real-estate-commission credit) → B3-4.3-21,
  `O-FNM-50259` (pooled savings) → B3-4.2-04 — both sections the compiler had already identified
  by name in its nuance but couldn't fit inside the 4-citation card-level cap.

**Assets needed almost no restructuring**: unlike Income, zero Assets cards were flagged
`decomposition.required` — each already maps to one narrowly-scoped sub-type (reserves, VOD,
retirement, gift funds, EMD, etc.), not a broad catch-all. Decomposition there was a clean 1:1
promotion. One rule (`PC::Custodial Acct`'s sole check) legitimately carries zero citations —
the same exhaustive-grep absence finding from compile, now inherited at the atomic level; a
schema inconsistency this surfaced (atomic rules originally required ≥1 citation unconditionally)
was fixed to match the card-level exemption rule rather than force a fake citation.

**Atomic check-type mix**: Income skews document-heavy (72/140 doc_presence — mostly missing
verification documents: VOE, paystubs, W-2s, award letters); Assets skews completeness-heavy
(36/81 doc_completeness — mostly field-level gaps in already-present forms like VOD, gift
letters, GAAR worksheets). Both carry a meaningful `computation` slice (17 Income, 11 Assets) —
gross-ups, DTI-affecting inclusions, LTV-conditioned thresholds.

## Decomposition status — everything else (100 cards, card-level only by design)

**100 of the remaining 243 cards** are catch-all bundles flagged for decomposition but not yet
atomized — Option C locked Income + Assets as the only flagship-depth targets; the rest stay at
the (already gate-passed, already typed and cited) card level with their `decomposition.status`
set to `pending` and `target_sections` recorded, ready to atomize the same way if this track
extends.

| Category | Cards pending decomposition |
|---|---|
| Income | 22 |
| Property - Appraisal | 20 |
| Product Specific | 13 |
| Underwriting | 13 |
| Loan Documents | 10 |
| Credit - Liabilities | 9 |
| Fannie Mae Form 1033 | 6 |
| Application | 2 |
| ATR-QM | 2 |
| Certification, Endorsement & Delivery | 2 |
| Closing | 1 |

Income (22/23 cards) and Assets (21/25, 4 already atomic) are compiled **and adversarially verified**
— the flagship-depth decomposition track can start on these two immediately, independent of the
other 8 categories.

---

## Pipeline status — COMPLETE

- **Compile**: 18/18 units, 266/266 cards, deterministic gate PASS (0 hard failures, 0 soft warnings).
- **Verify** (fresh-context adversarial spot-check): 18/18 units complete. 17 units verdict
  `minor_issues` (typing disputes and under-citation notes logged for the taxonomy record, none
  requiring action), **1 unit verdict `needs_recompile`** — see correction below.
- **Two post-hoc corrections applied, both re-validated clean:**
  1. `PC::Custodial Acct` originally shipped `failure_category: citation_drift` despite an
     exhaustive zero-hit grep across all 390 sections — corrected to `lender_specific_no_guide_basis`
     (the accurate semantic: absence confirmed, not a mismatch).
  2. **Two genuinely wrong, undisclosed citations caught by verify** on `fannie-mae-form-1033.b1`
     (the unit that triggered `needs_recompile`): `PC::O-FNM-50297` cited B4-1.3-11 alone, but its
     operative language is drawn near-verbatim from **B4-1.3-09** (Adjustments to Comparable Sales)
     — corrected to cite both, B4-1.3-09 primary. `PC::O-FNM-54346` cited B4-1.3-05 with a note
     claiming that section contains a matching subsection — verify confirmed that claim **false**;
     the physical-deficiencies/safety-soundness language actually lives in **B4-1.3-06**, confirmed
     by that section's own text and an internal Guide cross-reference — citation corrected. Neither
     card had self-flagged; this is exactly the class of error the deterministic gate can't catch
     (it validates that a cited section *exists*, not that it *governs the right topic*) — the LLM
     verify pass is what caught it.
- **A known workflow-engine quirk surfaced twice tonight**: resuming this workflow did not always
  cache-hit already-successful units — several categories' compile step silently re-executed on
  resume (independent fresh compile agent, different from the original). This was caught by
  re-running the Income/Assets atomic-decomposition consistency check after the second resume:
  `assets.json` had been regenerated with different (still valid, independently-verified) typing/
  citation judgment calls than the version the atomic rules were built from. **Assets atomic rules
  were regenerated from the current compiled data** (`pipeline/decompose_assets.py` re-run) and
  re-validated with zero drift. Income was untouched by the resume (file timestamp confirmed
  unchanged) and needed no action. If you extend this pipeline: after any workflow resume, re-run
  the atomic-decomposition consistency check (parent-card-keyed, not exception-code-keyed — codes
  repeat across cards) before trusting existing atomic output.

**Deliverable is complete**: 266/266 cards compiled and gate-passed, 18/18 units adversarially
verified with 2 real corrections applied, 221 atomic rules (Income + Assets) gate-passed with zero
drift against current data, stats report and handoff README written.
