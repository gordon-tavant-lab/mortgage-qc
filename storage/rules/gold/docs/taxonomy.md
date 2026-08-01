# Check-Type Taxonomy v1 — derived from the 266 base cards (read in full, 2026-07-31)

Method: every base card (question text + applicability SQL + skip-logic + all answer options with
exception codes/severities) was examined in-context. The taxonomy below is what the data required —
not a prior imposed on it. Gordon's draft 5-type model (calculator / doc-presence / cross-doc /
judgment / external-verification) survives only partially; the corrections are listed at the end.

## Structural finding #1 — type lives at the ATOMIC level, not the card level

Most cards are multi-type bundles. Example: `PC::O-FNM-15319` (verbal VOE) mixes date-window checks
(10 business days standard / 120 calendar days self-employed / 35 days vendor-database / 15 business
days alt-doc), doc-presence checks (email exchange in file), and content-completeness checks (email
includes required info) — in ONE question. Typing a whole card would force a false choice.
Therefore: **atomic rules carry exactly one check_type; cards carry a type PROFILE** (the multiset of
their children's types). The compile pass types every defect-option (the proto-atomic unit) and rolls
up the profile.

## Structural finding #2 — severity attaches to the defect outcome, not the question

Significance (Critical / Major / Minor / Note / Critical-Pending SI) varies per answer-option within
a card. Atomic rules inherit severity from the exception code they map to. "Critical-Pending SI"
(suspicious-indicator pending) appears only on tax-transcript reverification outcomes.

## The 10 check types

| # | check_type | Definition (what executes deterministically) | Real examples from the base |
|---|---|---|---|
| 1 | `doc_presence` | Required artifact exists in the file (and is executed/signed/dated where specified) | appraisal in file (O-FNM-14370); final DU findings report in file (O-FNM-50243); gift letter in file (O-FNM-00234); 4506-C signed per borrower (O-FNM-00045) |
| 2 | `doc_completeness` | A present document's required fields/sections/signatures are complete and internally coherent | 1008 field checks (O-FNM-00715-A..F); URLA sections complete (URLA-Final-2); SFHDF completeness (O-FDPA-51090); VOE Form 1005 all fields (O-FNM-00334) |
| 3 | `cross_doc_consistency` | The same fact extracted from ≥2 documents matches (tolerance where defined) | the whole AUS Findings card (DTI/LTV/value/property-type AUS vs 1003 vs 1008); ICPL insurer vs title policy (ICPLInsure); seller name contract vs appraisal vs HUD-1 (SELLER NAME/CONTRACT); contract price vs sales-comparison section (O-FNM-53020); EPIC credit ref # vs AUS (Data Points-7) |
| 4 | `computation` | Recompute a derived value per a guide formula, compare to submitted value or bound | LTV/CLTV/HCLTV recompute (O-FNM-50195/-96/-97); PITIA (O-FNM-51043); rental income (O-FNM-50252); SSI gross-up % (O-FNM-57444); ARM qualifying-rate formulas (O-FNM-54579..87); points & fees ≤3%/5% (O-FRD-54595); LCO cash-back ≤ max(2%,$2k) (O-FNM-50211); RefiNow ≥50bp reduction (O-FNM-54320); insurance coverage ≥ lesser-of rule (O-FNM-00825) |
| 5 | `threshold_eligibility` | A single extracted attribute vs a fixed limit or eligibility enumeration (no derivation) | loan limits (O-FNM-50223); max financed properties (O-FNM-50234); min credit score (O-FNM-51042); term ≤30y (O-FRD-54594); CU ≤2.5 (O-FNM-50187); DTI ≤65% RefiNow (O-FNM-54327); commercial space ≤35% (O-FNM-53854); HOA delinquency ≤15% (O-FNM-56978) |
| 6 | `date_window` | Date arithmetic between two dated events vs a bound (calendar/business-day semantics) | VVOE windows (O-FNM-00351/-53031/-52165); paystub ≤30d (O-FNM-00335); title ≤90d/180d (Title 90Days); appraisal ≤4mo/12mo (O-FNM-00576); value-acceptance offer ≤4mo (O-FNM-56087); CO refi 12-mo seasoning (O-FNM-56146); ECOA 30-day notices (O-FNM-00582); first payment ≤2mo from disbursement (O-FNM-51016); energy report ≤24mo (O-FNM-58662) |
| 7 | `list_screening` | Party/property/instrument screened against a versioned external reference list | OFAC SDN (O-FNM-51688); GSA/LDP (O-FNM-52795); FHFA SCP (O-FNM-52794); FHLMC Exclusionary (O-FRD-02575); appraiser vs AQM list (Form 1033 #39, O-FNM-53852); DU vendor authorized list (O-FNM-50821); ARM Plan Matrix (O-FNM-50218); ENERGY STAR list (O-FNM-56090); NFIP community participation (O-FNM-56258) |
| 8 | `reverification` | Third-party re-verification obtained post-closing, compared against original file data (D1-3-03) | the entire O-FNM-15408 card: QC credit report vs original (O-FNM-50342); income/employment reverif (O-FNM-50340); asset reverif (O-FNM-50341); gift donor (O-FNM-59420); tax transcripts (O-FNM-50339, Critical-Pending SI); occupancy via insurance docs (O-FNM-50343); appraisal desk review (O-FNM-50346). EPD cards (new credit report post-close) share the shape |
| 9 | `scripted_review` | Qualitative judgment compiled to an explicit criteria checklist; runtime deterministically evaluates operator/extractor-confirmed criterion answers or emits REQUIRES_HUMAN_REVIEW with evidence pointers. Never a runtime LLM | most of the Form 1033 battery (photos confirm C/Q ratings O-FNM-54348; comps suitable substitutes O-FNM-54351; value adequately supported O-FNM-50297); income vs lifestyle plausibility (O-EPD-52920); layered-risk adequacy (O-FNM-00713); UDAAP (O-UDAAP-54639); discriminatory-language review (O-FNM-00537) |
| 10 | `routing_context` | Zero defect outputs; answers set loan-context flags that drive downstream applicability/skip-logic | all O-CNTL cards (income types used 14367, asset sources 14366, DVS relief 14386, ATR/QM subject 14502, e-closing 15941/16591); program selector O-FNM-15460 (21 options, 0 defects); LEP determination O-CFPB-14499 |

## Compile-time constructs (NOT runtime types)

- **Applicability predicate** — translated from ACES `Question Criteria` SQL (`Loans.QC_Policy`,
  `Loans.LoanPurposeType`, `Loans.PropertyType`, `Loans.Underwriting_Type`, `Loans.LoanType`,
  `Loans.AddressState`). Small closed vocabulary; trivially declarative.
- **Skip-logic** — `Question Criteria by Questions` (answer-dependent activation); compiles to
  dependencies on `routing_context` outputs.
- **Bundle decomposition** — catch-all cards ("were ALL X requirements met") decompose into atomic
  children; each child gets one type, one citation, inherits the exception code + severity of the
  defect option it operationalizes.
- **Procedural/workflow checks** (DU-resubmit-on-tolerance workflow O-FNM-00722, SSN-discrepancy
  resolution O-FNM-50233, OFAC 24-hour notification O-FNM-51688, Refer-w/-Caution steps O-FNM-00721)
  are not a type: they decompose into presence + date_window + consistency children.

## Corrections to the draft 5-type model (what the data forced)

1. "Calculator" split into `computation` vs `threshold_eligibility` — different build cost:
   thresholds need only extraction + a constant; computations need formula implementations (and the
   formulas are the flagship value: DTI, LTV, ARM quals, gross-ups).
2. `date_window` promoted to first-class — it is pervasive (30+ distinct windows found), has
   business-day vs calendar-day semantics, and its evidence (two dates) is unlike anything else.
3. "External verification" renamed and sharpened to `reverification` (D1-3-03's term) — the D1-3-03
   suite + EPD re-pulls are their own runtime dependency class (third-party responses post-closing).
4. `list_screening` carved out — versioned-reference-list lookups (OFAC/AQM/SCP/plan-matrix) are
   deterministic given a list snapshot, but their dependency (reference dataset + fuzzy name match)
   differs from doc extraction. Reference datasets (loan limits table, AMI limits, APOR) may also be
   *evidence* for computation/threshold checks.
5. `doc_presence` split from `doc_completeness` — presence is decidable from a doc inventory;
   completeness requires field-level extraction of that document.
6. `routing_context` added — 8+ cards have zero defect options and exist only to set context; the
   draft model had nowhere to put them.
7. "Judgment-as-decision-table" kept but renamed `scripted_review`, with the runtime contract made
   explicit: criteria checklist in, deterministic verdict or REQUIRES_HUMAN_REVIEW out.

## Base-data quality findings (feed the compile-stats failure taxonomy)

- **Duplicate cards**: O-FNM-15946 and O-FNM-55582 are both "GLA appraisal requirements" with
  overlapping defect options (same exception codes) — must dedupe at compile.
- **Duplicated defect rows** inside cards (O-FNM-15405 lists its 4 options twice — multi-policy rows;
  O-FNM-15410 has near-duplicate short-sale rows; O-FNM-15843 duplicate military-income rows).
- **Scope leaks via applicability SQL**: `PC::DebtsPaid` sits in the base by family but its SQL is
  `Loans.QC_Policy = 'Freddie Mac'` — family-cut and SQL-cut disagree; compile must flag
  `scope_conflict`. O-FNM-15405 (erroneous credit data) applies to ALL policies incl. FHA/VA/USDA.
- **Shared exception codes across cards** ("Income Breakdown" appears on 8+ income cards; DEBTS-PAID
  on two cards) — exception codes are many-to-many with questions; the schema must not assume 1:1.
- **Generic cards carrying Freddie-prefixed codes** (ATR-QM card → O-FRD-54593..99): code prefix ≠
  investor scope; do not re-derive scope from exception-code prefixes.
