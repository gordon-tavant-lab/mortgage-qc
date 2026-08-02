# External Research: Automating the Three Unautomated Check Families

> Research date: 2026-08-01. Scope: presence-gate conditionals, computations beyond LTV/DTI, and
> cross-document field reconciliation in post-closing mortgage QC.
>
> **Grounding rule honored throughout:** everything below is *mechanism design guidance and
> citations*. No numeric threshold, percentage, date rule, or condition found in these sources may
> be inserted into a compiled rule. Rule content must always originate in the source AMQ row
> (per `output/RULE-FIDELITY-AUDIT-2026-07-22.md` and the compiler system prompt).

---

## Q1 — How established platforms structure automated cross-document reconciliation and conditional document-requirement rules

### 1.1 The two architectural lineages

The market splits cleanly into two lineages, and the split itself is instructive:

**(a) Questionnaire-heritage QC platforms (ACES).** ACES Quality Management — used by "70% of the
top 20 independent mortgage lenders" — is structured as **Audit Packs = Loan Quality Insight
Reports + Managed Questionnaires** per loan type (Origination, Servicing, Consumer, Specialty).
The Managed Questionnaires are auditor-answered question sets, **organized by category** —
Application, Initial Disclosures, Underwriting, Credit Liabilities, Income, Assets, Data
Validation Services, ATR-QM, Property Appraisal, Information Integrity, Loan Documents,
Insurance, At-or-Prior-to-Closing, etc. — a near-exact mirror of the AMQ workbook's category
column this project already uses for Blocks. ACES's compliance team updates the questionnaires
monthly against "more than 80 different sources," and the product supports **"dynamic questions"**
(conditional question display driven by prior answers/loan data) — i.e., presence-gating exists
in ACES, but as *questionnaire display logic*, not as autonomous evaluation. The automation value
is workflow, sampling, defect taxonomy reporting (Fannie Mae loan defect taxonomy), and
benchmarking — a human still answers most questions.
- https://www.acesquality.com/products
- https://www.acesquality.com/products/aces-quality-management-control/review
- https://www.acesquality.com/uploads/files/ACES-Managed-Questionnaires.pdf
- https://www.acesquality.com/resources/reports/q2-2025-aces-mortgage-qc-industry-trends

**(b) Data-extraction-heritage platforms (ICE Analyzers, Ocrolus, TRUE, Infrrd, Candor).** These
start from document extraction and push toward autonomous checks, converging on the same
three-part shape this project uses:

- **ICE Audit Analyzer** (Encompass 25.1, announced March 2025) is explicitly a post-closing QC
  automation: "Instead of relying on manual checklists, the tool uses automated technology to
  help identify **missing documents, data discrepancies and compliance risks**." Its sibling
  **Asset Analyzer** uses "data analysis and configurable logic … applying a standardized
  **checklist rules with 23 built-in protocols**" — i.e., a fixed library of deterministic
  checklist rules plus lender-configurable logic. **Income Analyzer** computes income from
  paystubs/W-2s/1040s/LES documents; ICE reports it uncovered errors in ~20% of loans reviewed
  (e.g., pay-frequency miscalculation) — evidence that the *computation* family is both
  automatable and high-value.
  - https://www.housingwire.com/articles/ice-mortgage-technology-debts-asset-and-audit-analysis-tools
  - https://mortgagetech.ice.com/blog/ice-adds-asset-verification-file-audit-automations-to-popular-mortgage-analyzer-offerings
  - https://mortgagetech.ice.com/products/mortgage-analyzers
  - https://mortgagetech.ice.com/blog/tackling-lending-challenges-with-precision-using-powerful-automation

- **Infrrd MortgageCheckai** (post-close audit QC) is the most explicit published statement of the
  cross-document reconciliation pattern: it "auto-detects over 60 common issues, such as missing
  documents, data mismatches, and expired CDs," "**automatically compares data between lender CD,
  title CD, and loan origination system (LOS)**," and "automatically **matches configured data
  fields across different documents and data sources** and flags mismatches." Note the phrase
  *configured data fields* — the field-pair list is configuration, not code.
  - https://www.infrrd.ai/blog/automation-101-post-close-mortgage-audit-qc

- **TRUE.ai** frames post-close automation as removing manual indexing and "**stare and
  compare**": validating "core data points against source docs," flagging "mismatches between
  docs and LOS fields, missing signatures, stale versions, and **gaps in required
  documentation**," and running QC continuously rather than as sampled batches (100% review).
  - https://true.ai/mortgage-qc-automation

- **Ocrolus Inspect** runs cross-document discrepancy detection at document intake and
  **generates conditions** in the LOS: "analyzing the data extracted across documents to identify
  discrepancies and generate conditions … remove bias and judgment with **systematic
  conditioning**." The reconciliation output is a *condition object with a lifecycle*, not just a
  pass/fail flag.
  - https://www.ocrolus.com/blog/clear-to-close-automation-mortgage-conditions-management
  - https://www.ocrolus.com/mortgage

- **Candor LES** (patented decision engine) "analyzes loan data and borrower docs against investor
  guidelines," and "**creates and clears conditions BEFORE the Underwriter touches the file**,"
  surfacing only exceptions as LOS conditions — the same auto-clear-and-isolate-exceptions
  philosophy as this project's Output surface.
  - https://www.candortechnology.com

- **Fannie Mae DU validation service (Day 1 Certainty)** is the GSE's own automation of the
  verification family: income, employment, and assets are validated by DU against electronic
  verification reports from approved vendors, with three deterministic outcomes — **validated /
  not validated / unable to be validated** — and validated components earn rep-and-warrant
  enforcement relief *and different QC/documentation treatment* (see Q3).
  - https://selling-guide.fanniemae.com/sel/b3-2-02/du-validation-service
  - https://singlefamily.fanniemae.com/learning-center/originating-and-underwriting/desktop-underwriter-learning-center/du-validation-service-resource-center-frequently-asked-questions
  - https://argyle.com/blog/day-1-certainty-faqs

### 1.2 Field pairs / document pairs that are standard to reconcile post-closing

Synthesizing the sources above plus the GSE guides (Q2/Q3), the industry-standard reconciliation
pairs are:

| Comparison | Fields typically reconciled | Source basis |
|---|---|---|
| **Note vs. Closing Disclosure** | loan amount, interest rate, loan term, product/loan type, borrower name(s) | CFPB CD explainer; UCD maps both concepts to shared data points (Q2) |
| **Closing Disclosure vs. Loan Estimate** | fees by tolerance category, loan terms table | TRID; CFPB "compare side by side; charges that can't change should match exactly" — note: the tolerance categories are *regulatory content*, so in this project they must come from the AMQ rows, never from this citation |
| **Lender CD vs. Title/Settlement CD vs. LOS** | full configured field set | Infrrd MortgageCheckai (explicitly this triple) |
| **Closing documents vs. underwriting decision** | final settlement statement and closing docs "consistent with the underwriting decision and final terms of the loan" | Fannie D1-3-02 (mandatory) |
| **Data submitted to DU vs. loan file documentation** | "all data submitted to DU is true, correct, and complete… documentation supporting all data submitted" | Fannie D1-3-02 (mandatory) — this is doc-presence + doc-vs-system in one requirement |
| **Reverification docs vs. origination docs** | asset amounts ("to authenticate the amounts used are accurate and to ensure no documentation alterations were made") | Fannie D1-3-03 |
| **Occupancy story across documents** | property insurance policy vs. appraisal vs. tax returns/transcripts vs. lease agreements | Fannie D1-3-03 occupancy assessment — a *categorical agreement across documents* check (relevant to the flagged `agree_doc_categorical` gap) |
| **Name/address consistency** | borrower name spelling, property address across Note/CD/URLA/appraisal | CFPB review-before-closing guidance; TRUE/Infrrd doc-vs-doc matching |

- https://www.consumerfinance.gov/owning-a-home/close/review-documents-before-closing/
- https://www.consumerfinance.gov/owning-a-home/closing-disclosure/
- https://selling-guide.fanniemae.com/sel/d1-3-02/lender-post-closing-quality-control-review-approval-conditions-underwriting-decisions-and
- https://selling-guide.fanniemae.com/sel/d1-3-03/lender-post-closing-quality-control-review-data-integrity

---

## Q2 — Do MISMO 3.4/3.6 or the UCD define canonical data points mapping both sides of Note-vs-CD-vs-URLA comparisons?

**Yes — this is precisely what the Uniform Mortgage Data Program (UMDP) datasets were built for.**
Three GSE datasets each pin one document to MISMO data points, giving canonical names for both
sides of most doc-vs-doc comparisons:

1. **UCD (Uniform Closing Dataset)** — pins the **Closing Disclosure** to **MISMO v3.3.0** (schema
   v3.3.0299; UCD v2.0 adds a `ucd:FEE_DETAIL_EXTENSION` schema). Key artifacts:
   - **Appendix B: Closing Disclosure Mapping to the MISMO v3.3 Reference Model** — maps every CD
     form field to equivalent MISMO data points.
   - **Appendix I: UCD Delivery Specification** — "ties each Closing Disclosure field to one or
     more MISMO v3.3.0 data points" with xPaths, in XML file order.
   - **Appendix C: Closing Disclosure reference numbers** and the GSE-published **"Numbered
     Closing Disclosures"** — sample CD forms with red **Form Field IDs superimposed on each
     field**, giving a stable per-field citation anchor on the document image itself.
   - **UCD Critical Edits Matrix** — data points categorized by implementation phase, with
     conditional requiredness (e.g., per the GSE FAQ, `gse:QualifiedMortgageShortResetARM_APRPercent`
     "is required for all ARMs with an adjustment within five years of the note date" — a
     published example of a *conditionally required data point*, i.e., a presence gate in the
     data domain).
   - **Every GSE-delivered loan requires a UCD submission**, and the UCD XML **must embed the
     Closing Disclosure PDF**; loans without a well-formed UCD get a critical/fatal edit and are
     ineligible for purchase. A key mapping principle from the GSE material: where an identical
     value appears in multiple places on the CD, it is "generally mapped using the same data
     points … and only have one instance in the XML file" — the dataset's own design says *one
     fact, one canonical data point*, though "there are instances where a value may be mapped
     using different xPaths."
   - https://singlefamily.fanniemae.com/delivering/uniform-mortgage-data-program/uniform-closing-dataset/faqs-uniform-closing-dataset
   - https://sf.freddiemac.com/tools-learning/uniform-mortgage-data-program/ucd
   - https://singlefamily.fanniemae.com/media/6596/display (UCD Specification)
   - https://sf.freddiemac.com/docs/pdf/fact-sheet/appendix_c_closing_disclosure_reference_numbers.pdf
   - https://sf.freddiemac.com/docs/pdf/ucd-v2.0-implementation-guide-v1.0.pdf

2. **ULAD (Uniform Loan Application Dataset)** — pins the **URLA (Form 1003/65)** to **MISMO
   v3.4**: "The ULAD Mapping Document provides a cross reference for **every field on the
   redesigned URLA to the equivalent data point(s) in the MISMO Version 3.4 Reference Model**."
   The GSE **AUS specs** (DU spec, LPA spec) layer *business requirements* on top — "conditionality,
   cardinality, implementation notes" — i.e., machine-readable statements of *when a data point is
   required*, per loan characteristics. **iLAD** (Industry Loan Application Dataset, MISMO-hosted)
   is the superset of ULAD + both AUS specs, deliberately *without* conditionality.
   - https://singlefamily.fanniemae.com/learning-center/delivering/faqs-uniform-residential-loan-application-uniform-loan-application-dataset
   - https://singlefamily.fanniemae.com/media/32201/display
   - https://sf.freddiemac.com/docs/pdf/requirements/ulad_data_relationships_using_xlink_mismo_arcroles_document.pdf
   - https://www.fhfa.gov/blog/insights/standardizing-mortgage-data-through-the-umdp

3. **Version skew is a real, known issue** — UCD is MISMO v3.3, ULAD is v3.4, ULDD (delivery) is
   v3.0. The MBA/MISMO note on v3.4 says the point of the version march is "consistency in the
   data collection throughout the loan manufacturing process," but cross-dataset joins today are
   by *data point name/concept*, not by a single shared schema instance. Data point names are
   largely stable across versions (the v3.x Logical Data Dictionary is additive), which is what
   makes name-level canonical mapping workable.
   - https://newslink.mba.org/servicing-newslink/2016/april/mismo-version-3-4-supports-a-new-gse-initiative
   - https://www.mismo.org/standards-resources/mismo-product/mismo-version-3-4

**Which data points?** The load-bearing shared concepts for Note-vs-CD-vs-URLA comparisons are the
loan-terms cluster that all three datasets carry (loan amount / note amount, note rate, loan term
/ maturity, loan purpose, loan type, amortization type, borrower name, property address), plus the
CD-specific fee/escrow/cash-to-close clusters (UCD only) and the application-side
income/asset/liability clusters (ULAD only). The authoritative per-field list is Appendix B +
Appendix I (UCD) and the ULAD Mapping Document — these are downloadable spreadsheets/PDFs and are
the right artifacts to build this project's canonical field-pair table from. (Exact MISMO data
point names should be lifted from those documents at implementation time, not from this summary.)

---

## Q3 — Fannie Mae Selling Guide D1-3 / D2-1: what's mandatory vs. discretionary, and what that says about prioritization

Structure of Part D as of the 2025–2026 reorganizations (Fact Sheet + SEL-2026-03):
**D1-3-01** selection (random + discretionary), **D1-3-02** review of approval conditions,
underwriting decisions, data, and documentation, **D1-3-03** reverifications. Former D1-3-04/05/06
are retired and folded into these.
- https://singlefamily.fanniemae.com/media/42741/display (Part D "Ensuring Quality Control" fact sheet)
- https://singlefamily.fanniemae.com/media/45171/display (SEL-2026-03)

**Mandatory for every loan in the post-closing QC sample:**

- **Selection & cadence (D1-3-01):** 10% random sample (or statistically valid sample) monthly;
  full QC cycle within 120 days of closing (30 selection / 60 review+rebuttal / 30 reporting).
  Discretionary samples targeting high-fraud-risk loans are *required to exist* but the targeting
  criteria are lender-chosen — that is the main "discretionary" element.
  - https://www.richeymay.com/wp-content/uploads/2015/10/Fannie-Maes-QC-Requirements.pdf
  - https://www.mqmresearch.com/blog/faq-fannie-mae-updated-quality-control-requirements
- **File review (D1-3-02), all mandatory:** confirm underwriting per Guide; confirm **all approval
  conditions were satisfied**; confirm **"the information on the closing documents, including the
  final settlement statement, is consistent with the underwriting decision and final terms of the
  loan"**; review DU findings and red-flag/alert messages ("ensure identified discrepancies are
  appropriately addressed"); **verification of data integrity** ("review the final terms of the
  loan to ensure they align with the data used to support the underwriting decisions"); for DU
  loans, "ensure **all data submitted to DU is true, correct, and complete**" with supporting
  documentation in file; Social Security number review; property & flood insurance review (moved
  forward into the credit-document set per the fact sheet); MI coverage adequacy where applicable.
  - https://selling-guide.fanniemae.com/sel/d1-3-02/lender-post-closing-quality-control-review-approval-conditions-underwriting-decisions-and
- **Reverifications (D1-3-03), mandatory but with automation-based relief:**
  - *Income & employment*: mandatory reverification through the closing date — **not required when
    validated by the DU validation service** (with rep/warrant relief conditions met).
  - *Tax transcripts*: mandatory when returns were relied on — waived if transcripts already
    obtained pre-closing.
  - *Assets*: mandatory reverification of **all sources of funds for down payment, closing costs,
    and reserves**, compared against origination docs to detect alterations — **not required when
    an automated asset verification came from an approved Fannie Mae vendor** (SEL-2026-03 also
    removed reverification where institutions systemically refuse, subject to logging).
  - *Credit history*: mandatory (new tri-merge or nontraditional references).
  - *Property eligibility & value*: mandatory collateral risk assessment; appraisal comp
    reverification waived under rep/warrant relief (CU); Freddie's parallel (Guide 3402.5(e))
    recently *tightened* — the options that let most sampled loans skip desk/field review were
    eliminated.
  - *Occupancy*: mandatory for **all** occupancy types (expanded 2024), assessed by reading
    documents against each other (insurance policy, appraisal, tax returns, leases) and
    investigating red flags.
  - https://selling-guide.fanniemae.com/sel/d1-3-03/lender-post-closing-quality-control-review-data-integrity
  - https://sf.freddiemac.com/faqs/in-house-post-closing-qc-for-appraisal-review-faq
  - https://guide.freddiemac.com/app/guide/section/3402.5

**Prioritization signal for the three families:**

1. **Cross-document reconciliation (family 3) sits inside the *mandatory* D1-3-02 core** —
   "closing documents consistent with underwriting decision and final terms" and "verification of
   data integrity" are required on every sampled loan, are pure data-vs-data work, and earn no
   vendor relief. Highest leverage to automate first.
2. **Presence gates (family 1) are the precondition layer for D1-3-02's "all approval conditions
   satisfied" and "documentation supporting all data submitted to DU"** — you cannot honestly
   auto-clear a data-integrity check without first deciding which documents were required for
   *this* loan. Second priority, and a prerequisite for honest NOT_APPLICABLE verdicts.
3. **Computations (family 2) are where the GSEs themselves are automating via relief** — DU
   validation service already gives income/employment/asset relief, meaning the marginal value of
   re-computing vendor-validated components is lower; the un-relieved computations (qualifying
   income assembly, reserves adequacy, points-and-fees, seasoning date math, PITI) are where a
   deterministic engine still adds unique value. ICE's ~20%-of-loans income-error finding shows
   the payoff. Third in sequence, but per-check value is high.

(D2-1 — Fannie's *own* post-purchase LQC review of lender loans — reinforces the same stakes:
defects found there drive repurchase; the lender-side D1-3 program is the mirror the tool
implements.)

---

## Q4 — Published prior art on "document presence gated on loan characteristics" as deterministic rules

**MISMO has formally adopted DMN as the standard for exactly this class of rule.** In 2019 MISMO
"recommended use of the Decision Model and Notation standard for documentation, implementation,
execution and exchange of business rules and decisions across the mortgage industry," explicitly
so that "lenders could instantly integrate investor guidelines or other partner requirements into
their business processes" — sharing *rules along with the data used by the rule* (MISMO data
points as DMN inputs).
- https://newslink.mba.org/servicing-newslink/2019/march/servicing-newslink-tuesday-4-2-19/mismo-recommends-dmn-standard
- https://www.trisotech.com/mismo (Trisotech ships DMN "Accelerators" pre-loaded with MISMO and FIBO data structures)

**Concrete published model:** the MISMO Decision Modeling Community of Practice's **Application
Threshold Decision Model and White Paper (final, January 2023)** — a shareable DMN model deciding
when RESPA's application threshold is crossed. That decision is structurally identical to a
presence gate: *given which of a defined set of items have been received, does a regulatory
obligation trigger?* It demonstrates the pattern of publishing a presence-gate decision as a
portable, deterministic DMN artifact.
- https://www.mismo.org/standards-resources/mismo-product/Application-Threshold_Decision_Model

**DMN decision tables themselves** (OMG standard) are the canonical encoding: inputs (loan
characteristics), outputs (required documents / applicable checks), explicit hit policies, and —
critically for this project's sign-off gate — **tool-verifiable completeness and overlap checking**
of the rule table before deployment. Drools and Camunda both execute DMN natively.
- https://www.omg.org/dmn
- https://docs.drools.org/latest/drools-docs/drools/DMN/index.html
- https://camunda.com/dmn
- https://en.wikipedia.org/wiki/Decision_Model_and_Notation

**LOS-embedded prior art (deployed at scale, not academic):**
- **Encompass plan codes / document sets**: "The plan code determines the documents that will be
  included in the package," and closing-document generation runs a **loan audit** ("document rules
  are run to confirm the required data is present and valid in the loan file") before docs can be
  generated — a deterministic presence/validity gate keyed to loan program.
  https://developer.icemortgagetechnology.com/developer-connect/docs/ordering-document-packages
- **Encompass business rules**: Field Data Entry rules conditioned on loan characteristics (e.g.,
  "Apply this rule only if: Loan Type is FHA" driving which forms/documents apply), and rules
  "that specify which documents must be received before a milestone can be marked as finished."
  **Dynamic Data Management** is a scenario-based rule engine keyed on loan-level data.
  https://www.scapartnering.com/blog/encompass-dynamic-data-management
  https://lendertoolkit.com/wp-content/uploads/2020/06/18-4-MR-Banker-version2.pdf
- **GSE AUS specs and UCD Critical Edits** encode conditional requiredness declaratively —
  "conditionality" statements per data point ("required when …", e.g., the short-reset-ARM QM APR
  data point) — the same gate pattern applied to data elements rather than documents.
  https://singlefamily.fanniemae.com/learning-center/delivering/faqs-uniform-residential-loan-application-uniform-loan-application-dataset
  https://singlefamily.fanniemae.com/delivering/uniform-mortgage-data-program/uniform-closing-dataset/faqs-uniform-closing-dataset
- **DU validation service messages** are themselves conditional documentation requirements: "DU
  will require [documentation], which may be different than the standard documentation required in
  this Guide," per validated component and loan situation — the GSE's production example of
  documentation requirements computed from loan characteristics.
  https://selling-guide.fanniemae.com/sel/b3-2-02/du-validation-service

No source found encodes presence gates via ontology reasoners at runtime; the industry pattern is
uniformly **decision tables / declarative conditionality evaluated by a deterministic engine**,
which is consistent with this project's no-runtime-reasoner boundary.

---

## Implications for mechanism design

1. **Encode presence gates as two-part decision-table rows — trigger predicate over loan facts →
   required-document assertion** — compiled into the same deterministic artifact as other checks.
   This is the industry-consensus shape (Encompass plan codes/doc rules, AUS conditionality, UCD
   critical edits, MISMO Application Threshold DMN). DMN is the MISMO-recommended interchange
   format; even if the engine stays JSON-native, keeping rows structurally DMN-equivalent (inputs,
   output, hit policy) preserves a future export path and enables table-level completeness/overlap
   verification at compile time — a mechanical addition to the sign-off gate.
2. **Presence gates are the prerequisite family, reconciliation is the priority family.** D1-3-02
   makes closing-doc-vs-underwriting consistency and data integrity *mandatory on every sampled
   loan* with no vendor relief — automate family 3 first for coverage, but ship the family-1 gate
   logic with it, because honest NOT_APPLICABLE verdicts on reconciliation checks depend on
   knowing whether the document was required at all (matches the existing "absent document: three
   reasons" memory).
3. **Use MISMO data point names (from UCD Appendix B/I and the ULAD Mapping Document) as the
   canonical join key for every doc-vs-doc field pair.** Both sides of Note-vs-CD-vs-URLA
   comparisons already have GSE-published canonical names; adopting them extends the existing
   FIBO naming discipline and gives auditors an industry-recognizable field catalog. Lift exact
   names from the published mapping spreadsheets at implementation time.
4. **One fact, one canonical data point, exact match.** The UCD's own design principle — identical
   values appearing in multiple CD locations map to a single data point instance — supports the
   project's exact-match-money stance: doc-vs-doc comparisons of the *same fact* should be exact;
   any tolerance is regulatory content that must originate in the AMQ row, never in this research.
5. **Reconciliation output should be a condition object with a lifecycle, not a bare FAIL.**
   Ocrolus ("systematic conditioning") and Candor (create/clear conditions before human touch)
   both model mismatches as conditions that can be auto-cleared, escalated, or human-resolved —
   directly validating the ExceptionReview mitigation-type model (UNRESOLVED / OVERRIDDEN /
   ESCALATED / SYSTEM_CORRECTED).
6. **Record validation provenance as a first-class fact that deterministically gates check
   applicability.** The GSEs' own QC regime downgrades reverification when a component was
   validated by an approved vendor (DU validation service, CU). The engine should mirror this: a
   `validated_by_*` fact suppressing or re-scoping specific checks is itself a deterministic gate
   — and is prior art for gating on *how* data was verified, not just what it says.
7. **The DU validation trichotomy (validated / not validated / unable to be validated) is GSE
   precedent for the four-verdict model** — "unable to be validated" ≙ NO_DATA, distinct from a
   failing check; keep the separation all the way to reporting.
8. **Closed-world document inventory is what makes missing-document checks deterministic.** ICE
   Audit Analyzer and Infrrd both treat "missing documents" as a computable finding, which is only
   sound because their intake classifies the complete package — consistent with the project's
   Touchless `documents[]`-is-complete memory. The presence-gate family should assert against the
   classified inventory, never against raw extraction success.
9. **For computations, target the relief gaps.** DU validation already covers vendor-verifiable
   income/employment/assets; the deterministic engine's unique ground is the un-relieved math —
   qualifying income assembly, reserves, points-and-fees, seasoning date arithmetic, PITI — where
   ICE's published ~20% income-error rate shows both feasibility and payoff. Formulas and
   thresholds still must come from the AMQ rows; what this research licenses is only the *choice
   of which computations to build next*.
10. **Occupancy consistency is a published template for `agree_doc_categorical`.** D1-3-03's
    occupancy assessment is defined as reading multiple documents (insurance policy, appraisal,
    tax returns, leases) for a consistent categorical story — GSE-mandated prior art for the
    doc-vs-doc categorical agreement check kind flagged as absent ruleset-wide on 2026-07-28.
11. **Adopt the numbered-CD citation anchor pattern.** The GSEs publish CD forms with per-field
    Form Field IDs superimposed; citing doc-sourced values by document + page + form-field ID (not
    just a text snippet) is an industry-recognizable strengthening of the PdfViewerModal citation
    contract.
12. **The AMQ-category Block decision is independently validated:** ACES — the market-leading QC
    platform — organizes its entire authoring surface as per-category managed questionnaires whose
    category list (Income, Assets, ATR-QM, Property Appraisal, Information Integrity, Loan
    Documents, Insurance…) mirrors the AMQ categories nearly one-to-one, and layers "dynamic
    questions" (conditional applicability) beneath the category grouping — the same
    Blocks-for-authoring / gates-for-runtime split this project already committed to.
