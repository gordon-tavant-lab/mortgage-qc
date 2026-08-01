# Touchless API — Questions for the Vendor Conversation

**Date:** 2026-07-30
**Occasion:** Colleague is granting API access to Touchless loan data
**Sources reviewed:** `demo/touchless/touchless_loan_extraction.json` (4 KB, 17 fields),
`demo/touchless/loan_application.json` (154 KB, loan 12607601215),
`demo/touchless/extracted_data_e59d57a9-…json` (60-field Schedule C extraction)

> Every question below is grounded in something **verified in the two files they gave you**, and
> tied to an open blocker already documented in this repo. Nothing here is speculative — the
> evidence line in each item is reproducible from the JSON.

---

## If you only get 20 minutes, ask these five

| # | Question | Why it's first |
|---|---|---|
| **A** | Is there a **document-extracted** value exposed separately from the **LOS** value for the same datapoint? | Our entire product thesis is cross-comparing three sources. Right now we cannot do it at all. |
| **B** | Can I retrieve an **immutable, as-of-a-point-in-time snapshot** of a loan, and is there a **post-closing / funded** state? | Determinism (same loan → same verdict) is the product's defining bet. A live mutable endpoint breaks it. |
| **C** | Which of your **54 document types** have field-level extraction models, and what's the call to get them? | Unblocks 466 backlog rules. Only 1 of 62 documents in the sample has an extraction payload. |
| **D** | What exactly does `documents[]` represent — and is it **complete**? | We built a closed-world assumption on it. Three open conditions in their own file contradict it. |
| **E** | What is the **confidence scale**? I'm seeing 0, 80, 100, **102, and 200**. | Blocks the confidence-gated auto-clear we already shipped. Unusable until defined. |

---

## Tier 1 — Architecture-breaking if the answer is wrong

### A · Is there a document-sourced value distinct from the LOS value?

**This is the most important question in the document.**

**Evidence.** In `touchless_loan_extraction.json`, every field we named as if it came from the
1003 PDF actually cites an **LOS JSON path**:

| Our field name | Its actual citation |
|---|---|
| `base_monthly_income_1003` | `employers[0].income[0].monthlyIncome` |
| `credit_score_1003` | `loanSummary.fico` |
| `loan_program_1003` | `loanTerms.mortgageType` |
| `mismo_loan_amount` | `loanTerms.baseLoanAmount` |
| `mismo_note_rate` | `loanTerms.interestRate` |

Note that `mismo_*` and `*_1003` fields resolve to **the same LOS nodes**. And in
`loan_application.json`, `documents[]` reports `documentSource: "LOS"` for **61 of 62** documents.

Meanwhile the file *does* contain `URLA - Borrower Information`, `URLA - Lender Loan
Information`, and `URLA - Continuation Sheet` PDFs — the document-side values exist as paper,
but nothing extracts them.

**Why it's load-bearing.** `CLAUDE.md` Non-Negotiable #3: a check must assert not "is this value
valid" but "do all three sources tell the same story," and warns explicitly that *"LOS-only data
makes the document-vs-system comparison trivially identical and untestable."* That is exactly the
state we are in. Roughly 21% of AMQ checks exist to find doc-vs-doc / doc-vs-system disagreement;
today all of them would compare a value to itself and pass.

**Ask precisely:**
1. For a datapoint like note rate or loan amount, can you return **the OCR'd value from the Note
   PDF** and **the LOS value** as two separate, separately-cited fields?
2. Is `documentSource` ever something other than `LOS`? What are the possible values?
3. Where does the **title company's** MISMO 3.4 file enter your pipeline — is it exposed at all?

---

### B · Immutable snapshot, and a post-closing loan state

**Evidence.** The payload is shaped like an **event**, not a query result:

```
timestamp:    1784635811000
modifiedBy:   dlf-income
eventSource:  Income Verification
dataSource:   TWN
```

And the loan is plainly **mid-process, not closed**:
- `loanStatus: null`, `milestone: null`, `loanApprovalDate: null`
- rate lock `lockStatusType: "5-Cancelled"`
- 3 `loanConditions` all `status: OPEN`, all `conditionPriorTo: "PTA"` (prior-to-approval)

**Why it's load-bearing.** Two separate problems. (1) **Determinism** — Non-Negotiable #1 requires
same loan → same pass/fail every time; if the API serves live mutable state, our verdicts drift
with no code change and the audit trail is worthless. (2) **Scope** — this is a *post-closing* QC
product. Prior-to-approval conditions and a cancelled lock are the wrong lifecycle stage.

**Ask precisely:**
1. Is the API **event-streamed**, **request/response snapshot**, or both? Can I re-request the
   identical bytes later (content hash stable)?
2. Is there an **as-of / version** parameter — "give me this loan as it stood at funding"?
3. Can you give me a **closed, funded, post-closing** loan? Ideally several.
4. Which of the three identifiers is the **stable primary key** —
   `applicationId: 0eb57730-…`, `loanId: {6a2d95d0-…}`, or `lenderCaseIdentifier: 12607601215`?
   (We're currently keyed on the third.)

---

### C · Field-level extraction coverage per document type

**Evidence.** 62 documents, spanning **54 distinct `documentType` values**. Of those:
- **1** has a full field-level extraction payload (the Schedule C — 60 fields, and it's a
  separate file they handed over out-of-band, not reachable from `loan_application.json`)
- **3** carry `documentAnnotations` (2 Bank Statements, 1 Gift Letter) — and those are metadata
  only (account number, statement period, institution), **not** document content
- **58** have nothing at all
- `documentLocation` is **null on all 62** — there is no visible way to fetch the actual PDF

**Why it's load-bearing.** This is open issue **O6** in `output/SESSION-REVIEW-2026-07-30.md`,
owned by you, blocking **466 backlog rules** plus `CHK-AST-003`/`CHK-AST-004` and the
large-deposit check. Per Non-Negotiable #2 we deliberately **do not build extraction** — it's
their contract. So the answer here sets a hard ceiling on our rule coverage.

**Ask precisely:**
1. Give me the **list of document types you have extraction models for**, and the roadmap for the rest.
2. What's the endpoint/call that returns an extraction payload for a given `documentId`?
   (`extracted_data_<guid>.json` implies one exists — is `e59d57a9-…` a document ID, a job ID,
   or an extraction ID? It doesn't match any `documentId` in `loan_application.json`.)
3. Can I **retrieve the source PDF bytes**? `documentLocation` is null throughout.
4. Priority order for us, by rule count — no longer a guess, now an exact tally against the
   2026-07-31 root-cause classification (`doc_all_classified.json` / `cross_doc_analysis.json`):
   **Appraisal, Title Commitment, Closing Disclosure, Purchase Agreement, Credit Report, and
   Hazard Insurance** alone jointly account for 36 of the 43 (84%) `doc_fields_not_extracted`
   cross-document-consistency rows and 66 of the 105 (63%) presence-gate document checks —
   extraction models for just those six document types would clear the majority of both
   backlogs before touching anything else. Next tier down: Note, URLA/1003, Paystub/W2, Bank
   Statement transactions.

---

### D · What `documents[]` actually means — and whether it's complete

**Evidence — a direct self-contradiction in their own file.** All three open `loanConditions`
are contradicted by `documents[]`:

| Condition | Severity | It says | `documents[]` actually contains |
|---|---|---|---|
| `CPGA_01_009` | HIGH | "Form 1004 Uniform Residential Appraisal **is not available**" | `Form 1004 Uniform Residential Appraisal` ✅ |
| `CPGA_01_001` | HIGH | "Provide a valid **Flood Zone Determination Certificate**" | `Flood Hazard Determination`, `Standard Flood Hazard Determination` ✅ |
| `CPGA_01_284` | MEDIUM | "Provide **homeowners property insurance declaration page**" | `Hazard Insurance`, `Hazard Insurance Information`, `Hazard Insurance Authorization And Disclosure` ✅ |

Plus unexplained flags: **`active: false` on all 62 documents**, `forClassification: false` on 61,
and `isDuplicate`, `containerId`, `containerTypes`, `losId` null throughout. `documentDate` is
populated on only **12 of 62**.

**Why it's load-bearing.** Decision **D3** (`closed-world-document-inventory`) states that
`documents[]` is complete, so **an absent document type is positive evidence of absence** — which
is what turns 47 document-presence checks from `NO_DATA` into real verdicts with no PDF reading.
If `documents[]` is *not* complete, or if `active: false` means these don't count, that decision
is invalid and those 47 verdicts are unsound. Conversely if it *is* complete, then the three open
conditions are themselves stale — and note the CD-vs-condition mismatch is precisely the defect
family our checks target.

**Ask precisely:**
1. Is `documents[]` the **complete** inventory for the loan, or a filtered/paged view?
2. What do **`active`**, `forClassification`, `isDuplicate`, `containerTypes` mean? Why is
   `active: false` on everything?
3. Why do 3 open HIGH/MEDIUM conditions name documents that are present? Are `loanConditions`
   evaluated against a **different** inventory, or are they simply stale?
4. Is the `Hazard Insurance` doc the **declaration page** specifically? (Our adversarial suite
   already failed on exactly this distinction — "Hazard Insurance Declaration Page" vs "Hazard
   Insurance" — see the H2 specificity guard in `CLAUDE.md`.)

---

## Tier 2 — Blocks gates we have already built

### E · The confidence scale is undefined and out of range

**Evidence** from the Schedule C extraction, 60 fields:

| Confidence | Count | Note |
|---|---|---|
| 100.0 | 39 | |
| **102.0** | 7 | **above 100** — `Gross_Profit`, `Gross_Income`, `Net_Profit_Or_Loss`… |
| 80.0 | 6 | |
| **200.0** | 4 | **double 100** — all four `Proprietor_*` name fields |
| 0.0 | 4 | |

Worse: **18 fields have an empty value `""` but `confidence: 100.0`.** And there's a *separate*
`DocumentType_Confidence: "99"` carried as a field-with-a-confidence-of-its-own.

**Why it's load-bearing.** Spec `006-confidence-gated-auto-clear` is **shipped** — it withholds a
PASS below a confidence floor. That gate is meaningless against an unbounded scale, and
"confidence 100 on an empty value" would let a blank field auto-clear.

**Ask precisely:** What is the scale and its bounds? What do **102** and **200** signify (a
different unit? a flag OR'd in? summed sub-scores?). What does confidence mean on an **empty**
value — high confidence the field is *genuinely blank*, or a default? And is `confidence: 0` on a
blank meaningfully different from `confidence: 100` on a blank? (Both appear.)

---

### F · Citation granularity, and fetching the page

**Evidence.** The Schedule C extraction has `InputFilePageNumber: "24"` — a page locator exists.
But there are **no bounding-box coordinates**, and the extraction file isn't linkable to a
`documentId`. Every citation our own pipeline currently emits is degenerate:

```json
"citation": { "doc_name": "Touchless API", "page": 0,
              "snippet": "Touchless extraction: loanSummary.applicationDate" }
```

**Why it's load-bearing.** **380 of 385** catalog fields are marked `citation_required: true`, and
the `PdfViewerModal` in the design language shows *doc name + page + highlighted segment*. Note
we also have an internal gap here — `citation_required` is defined but **never enforced** by the
engine (finding #5 in `output/CITATION-AND-COMPILER-GAPS-2026-07-29.md`), so this needs fixing on
both sides.

**Ask precisely:** Per extracted field, can you return `documentId` + page + **bounding box**? Can
I fetch a single page image or the PDF? Is `InputFilePageNumber` the page within the *original
combined package* or within the *split document*?

---

### G · Which aggregate is authoritative? Three different answers in one file

**Evidence — verified arithmetic.** The field `totalLiabilitiesMonthlyPaymentAmount` appears at
two nodes with wildly different values:

| Location | Value | What it actually equals |
|---|---|---|
| `loanSummary.qualification.totalLiabilitiesMonthlyPaymentAmount` | **2,837.25** | reproduces the stated DTI: 2837.25 / 19500 = **14.55%** ✅ |
| `loanSummary.loans.loan[0].qualification.totalLiabilitiesMonthlyPaymentAmount` | **428,361.00** | = the **sum of the 7 unpaid balances** (210279+210027+4665+1554+1357+450+29) — a *balance* total sitting in a field named *monthly payment* |
| sum of `liabilityDetail.liabilities[].monthlyPaymentAmount` | **3,618.00** | the actual monthly payments as listed |

So the file asserts a monthly liability total of 2,837.25 while its own liability rows sum to
3,618.00 — a **$780.75 unexplained gap** — and a same-named nested field holds a balance total.
Separately, all 7 liabilities have `liabilityType: null`, and `payoffStatusIndicator` /
`exclusionIndicator` are null on every one, so nothing in the data explains the exclusion.

**Why it's load-bearing.** Decision **D7**: money comparisons are **exact-match, no tolerance
bands** — $452.00 vs $452.13 is an exception. With three candidate totals we would produce three
different verdicts. This is open issue **O7**.

**Ask precisely:** Which node is authoritative for QC? Is the nested `loans.loan[0].qualification`
one a known mislabel? Where is the **$780.75 exclusion documented** — is there an
exclusion-reason field we're not seeing (payoff at closing? the `RetainForRental` REO?)? And is
`liabilityType` ever populated?

---

### H · Which field decides "self-employed"? They disagree.

**Evidence.** Our extraction emits `borrower_self_employed: true`, and its own citation is
self-contradictory:

```
"Touchless extraction: employment.ownershipInterestType:
 GreaterThanOrEqualTo25Percent, isSelfEmployed: False"
```

That's **employer[0], Kraft Foods** — `isSelfEmployed: **False**` but ownership ≥25%. And the
borrower has **5 employers**:

| Employer | `isSelfEmployed` | `ownershipInterestType` | Position |
|---|---|---|---|
| Kraft Foods | **False** | **GreaterThanOrEqualTo25Percent** | Assistant Project Manager |
| Testing Partners, LLC | **True** | null | President |
| ABC Trucking | **True** | null | Owner |
| TNT Partnership | **True** | null | — |
| PNBC SOLUTIONS INC | **True** | null | — |

All five are `employmentStatusType: Current`. Every `employmentStartDate`, `employmentEndDate`,
and `latestVerifiedDate` is **null**.

**Why it's load-bearing.** `docs/LOAN-SCENARIO-APPLICABILITY.md`: **every document-presence check
must gate on its scenario trigger first**, and self-employment is one of the biggest triggers —
it drives the whole YTD P&L / business-return / K-1 document family. Getting the trigger wrong
mis-fires or silently skips that entire family. Note the file *does* contain Schedule C, Form
1040, and Schedule K-1 documents, consistent with a self-employed borrower.

**Ask precisely:** Is `isSelfEmployed` or `ownershipInterestType` authoritative? Why does an
"Assistant Project Manager" at Kraft Foods carry ≥25% ownership — data error, or a real second
relationship? Should the borrower-level trigger be "**any** employer self-employed"? And are
employment dates ever populated? (`employmentStartDate` null blocks every employment-gap and
2-year-history check.)

---

### I · Which income figure qualifies the loan? And what is negative base pay?

**Evidence — the numbers only reconcile one way:**

| Source | Value |
|---|---|
| `qualification.totalMonthlyIncomeAmount` | 19,500.00 |
| `borrower.incomeAnalysis.qualifyingIncome` | 19,500.00 |
| sum of `employers[].income[].monthlyIncome` | **4,000.00** (only Kraft Foods has an income row; the 4 self-employed employers have **zero**) |
| sum of `borrower.currentIncome[].basePay` | **19,500.00** ✅ — `[6500, 6000, **-2000**, 5000, 4000]` |

So 19,500 comes from `currentIncome`, which contains a **negative base pay of −2,000** and no
labels — every entry has `incomeType: null`, `year: null`, `isCurrent: null`. There is no way to
map a `currentIncome` row to the employer it belongs to.

**Why it's load-bearing.** Income is the **3rd-largest AMQ category (339 uncompiled rules)** and
one of the three we sequenced first. Every income check needs one authoritative figure and a
documented derivation — a regulator auditing the math is the whole premise.

**Ask precisely:** Which is authoritative — `qualifyingIncome`, `totalMonthlyIncomeAmount`, or the
employer rows? What does **negative `basePay`** represent (a business loss? an offset?)? Can
`currentIncome` entries be **linked to an employer** and **typed** (base/OT/bonus/commission/
self-employment)? Why do the 4 self-employed employers carry no income rows at all?

---

### J · Was this loan underwritten by DU, LPA, or manually? The payload won't say.

**Evidence.** `loan_application.json`'s `loanSummary` carries three keys that are exactly the
shape we'd need — and all three are present-but-null:

```
loanSummary.underwriting:  null
loanSummary.duStatus:      null
loanSummary.lpaApproved:   null
```

We checked for a fallback: no other field in the payload carries AUS/DU signal either. A
key-name sweep for `du`/`aus`/`underwrit`/`lpa`/`findings`/`eligib` across the whole document
turns up 27 candidate keys, and every one of them is either a substring false-positive
(`loanProduct`, `residencyDurationInYears`, `isDuplicate` — matched on `du` inside "prod**u**ct,"
"**Du**ration," "**Du**plicate," not a real AUS field) or a genuinely null AUS-shaped field
(`excludeFromUnderwriting` on all 5 liability rows is also null). There is no populated field
anywhere in the sample that would let us infer DU vs. LPA vs. manual underwrite.

**Why it's load-bearing.** This is root-cause bucket **C** from today's NO_DATA analysis
(`output/NODATA-ROOT-CAUSE-ANALYSIS-2026-07-31.md`): 5 gold conditions gate on "Desktop
Underwriter," cascading over **21 checks** that today can only resolve to NO_DATA — not because
the check logic is missing, but because the loan's underwriting method itself is unknown. That's
a different failure mode from Tier 1's Question C (field-level content extraction): this isn't
"we can't read the DU findings report," it's "we don't know whether one exists." Downstream,
actual DU findings *content* (relief flags, verification waivers, condition text) would unblock a
further **~25–43 checks** beyond those 21 — real numbers pending the sidecar classification, but
the floor is already real and already blocking.

**Ask precisely:**
1. Does the API expose the AUS decision at all — DU, LPA, or manual — for a given loan? Which
   field, if not `loanSummary.underwriting`/`duStatus`/`lpaApproved`?
2. Is there a DU/LPA **findings report** (as a document, a structured payload, or both) we can
   retrieve — condition codes, relief flags, verification waivers?
3. If the AUS decision genuinely isn't captured for this loan, is that a data gap on your side or
   a real fact (e.g., a manually underwritten loan with no AUS run at all)? We need to be able to
   tell "unknown" from "none" — the same closed-world distinction Question D raises for documents.

---

## Tier 3 — Crosswalk, semantics, and operations

### K · Publish the document-type taxonomy (needed for the SME crosswalk)

The sample yields **54 `documentType` values** across 15 `documentCategory` values — and the
category vocabulary is visibly **inconsistent**, mixing casing conventions in one payload:
`Title` **and** `TITLE`; `Disclosure` **and** `INITIAL_DISCLOSURES`; plus `Property` vs
`SUBJECT_PROPERTY`, `CLOSING_DOCUMENTS`, `IDENTITY_VALIDATION`, `MISCELLANEOUS`, and
**`Unassigned`** (2 docs — both `Verification Of Assets`).

**Ask:** Is there a **published, versioned, closed** list of `documentCategory` /
`documentSubcategory` / `documentType`? Are `Title`/`TITLE` and `Disclosure`/`INITIAL_DISCLOSURES`
genuinely distinct or a normalization bug? What does `Unassigned` mean — classifier abstained, or
no rule matched? (We need an explicit **abstention** signal; per `CLAUDE.md` an abstention must
map to `NO_DATA`, never `FAIL`.)

This directly unblocks **O2** — the AMQ-name → Touchless-type crosswalk, which is Kayla's SME
session. Without a stable versioned list the crosswalk rots on their next release.

### L · Transaction-level and row-level entities

Our extraction schema has five entity collections and **all five are empty**: `bank_txns`,
`comps`, `tradelines`, `urla_liabilities`, `vom_rows`. The Bank Statement annotations give account
number, statement period, and institution — **but no transactions**. `creditResponse` exposes
`creditInquiries`, `creditPublicRecords`, `liabilityDetail` as keys but the sample carries only
`creditReportIdentifier`.

**Ask:** Do you extract **bank-statement transaction rows** (date/amount/description)?
**Credit tradelines**? **Appraisal comparables** from the 1004? These block the large-deposit
check, `CHK-AST-003`/`004`, and most of Property-Appraisal (418 uncompiled rules).

### M · Date and timezone anchoring

`applicationDate: 1784592000000` = **2026-07-21T00:00:00Z**, but our pipeline wrote
**2026-07-20** (local-timezone conversion of a midnight-UTC value). Date checks are exact-match,
so a one-day shift is a manufactured defect.

Also: `loanOriginatorSignedDate` = **2024-12-30**, roughly **19 months before** the 2026-07-21
application date. Either a genuine defect or stale test data — worth knowing which.

**Ask:** What timezone are epoch-millis dates anchored to? Are date-only fields midnight-UTC by
convention? Is the 2024 originator signature date real or test-fixture noise?

### N · Credit score selection

`creditScores`: Experian **742**, TransUnion **740**, Equifax **724**. `loanSummary.fico` =
**740.0** — the middle value. `creditResponse.estimatedCreditScore` also exists.

**Ask:** Is `fico` always the representative/middle score? Which field should a QC check compare
against, and is the selection rule documented? (Also: is `estimatedCreditScore` ever used, and
does "estimated" mean modeled rather than pulled?)

### O · Empty string vs null vs "not on the document"

The Gift Letter's annotations are **present but blank**:
`receiverFirstName: ""`, `receiverLastName: ""`, `donarSignDate: ""`.

Gift-letter completeness is a real AMQ check, and this is exactly the three-way distinction from
`docs/LOAN-SCENARIO-APPLICABILITY.md`: field genuinely blank on the document (→ **FAIL**, an
incomplete gift letter) vs. extraction couldn't read it (→ **NO_DATA**) vs. not applicable. Our
verdict differs in each case.

**Ask:** Does `""` mean "the document's field is blank" or "extraction found nothing"? Is `null`
distinct from `""`? Is there an explicit *not-present-on-document* signal? (Also note the field is
spelled **`donar`** — is that stable? We'd hardcode against it.)

### P · MISMO 3.4

Non-Negotiable #3 lists MISMO 3.4 XML from the title company as a **distinct third source**.
(Our own MISMO *canonicalization* was cancelled — decision D1 — but the three-source
reconciliation still needs the file as an independent input.)

**Ask:** Do you expose a MISMO 3.4 export? Is it the **title company's** file preserved as
received, or one you generate from the LOS record? Only the former has value to us — a
regenerated one is the LOS source wearing a different hat.

### Q · Operational and compliance

- **Auth model** — OAuth / API key / mTLS? Sandbox vs production environments?
- **Rate limits and bulk access** — can I pull **N loans in a batch**? This is directly our eval
  gap (Blocker 2): we need labeled, expert-validated loans with known outcomes.
- **PII.** The sample carries **cleartext SSN (`999603333`)**, date of birth, and full addresses.
  Is this synthetic (`999-60-3333` and "Andy America" suggest yes)? For real loans: what's the
  redaction/tokenization contract, and what are my obligations for data at rest? Worth settling
  **before** we start pulling production files.
- **Schema versioning and change notice** — how are breaking changes to this payload communicated?
  We compile against these paths; a silent rename produces wrong verdicts, not errors.
- **Is `documents[]` paged?** 62 documents in one response with no pagination cursor visible.

---

## Two things to *tell* them, not ask

1. **We are not building extraction, by design.** Non-Negotiable #2 — extraction accuracy is their
   contract, and its data contract is expected to **widen over time** as we review more data
   elements. Frame that as a tracked **interface**, not a one-time handoff. Getting them to accept
   "you will get requests to add fields" now avoids a fight later.

2. **What we'd feed back.** Our engine can tell them which extracted fields actually drive
   verdicts and which are never read — a real prioritization signal for their extraction roadmap.
   Cheap for us, valuable to them, and it makes the widening-contract ask reciprocal.

---

## Traceability — question → open blocker

| Q | Open item | Source |
|---|---|---|
| A | Non-Negotiable #3, three independent sources | `CLAUDE.md` |
| B | Non-Negotiable #1, determinism; post-closing scope | `CLAUDE.md` |
| C | **O6** — extraction gap, 466 rules blocked, owner: Gordon | `SESSION-REVIEW-2026-07-30.md` |
| D | **D3** — closed-world document inventory | memory `closed-world-document-inventory` |
| E | spec `006-confidence-gated-auto-clear` (shipped, now ungated) | repo |
| F | gap #5 — `citation_required` on 380/385 fields, unenforced | `CITATION-AND-COMPILER-GAPS-2026-07-29.md` |
| G | **O7** — $780.75 DTI discrepancy; **D7** exact-match money | `SESSION-REVIEW-2026-07-30.md` |
| H | scenario-trigger gating; 3 reasons a document is absent | `docs/LOAN-SCENARIO-APPLICABILITY.md` |
| I | Income = 339 uncompiled rules, sequenced first | `SESSION-REVIEW-2026-07-30.md` §7 |
| J | **C** (root-cause bucket) — `loanSummary.underwriting`/`duStatus`/`lpaApproved` all null, 21+ checks blocked | `output/NODATA-ROOT-CAUSE-ANALYSIS-2026-07-31.md` |
| K | **O2** — document-name crosswalk, owner: Kayla | `SESSION-REVIEW-2026-07-30.md` |
| L | `LargeDepositShape`, `CHK-AST-003`/`004`, Property-Appraisal 418 | `QC-AUDIT-TOUCHLESS-…md` |
| Q | Blocker 2 — no labeled test data (the eval gap) | `CLAUDE.md` |
