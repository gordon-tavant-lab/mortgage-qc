# Three Blocking Scenario Fields — Investigation & Decision

**Date:** 2026-07-30 · **Loan:** 12607601215 · **Source:** `demo/touchless/loan_application.json`
**Question:** three missing fields block ~204 AMQ rules. Are they obtainable?

---

## Headline: the answer is better than expected on 2 of 3 — and the payload has integrity problems

| Sub-question | Verdict | Rules |
|---|---|---|
| Is this a **renovation / construction-to-perm** loan? | **DERIVABLE — PROOF (no)** | unblocks most of ~61 |
| Is this **Home Possible**? | **DERIVABLE — PROOF (no)** | contributes to ~50 |
| Is this **HomeReady**? | strong INFERENCE, **not proof** → needs doc | |
| Is this a **condominium**? | **NEEDS DOC EXTRACTION** | ~93 stay blocked |
| `constructionMethodType` (SiteBuilt/Manufactured)? | **NEEDS DOC EXTRACTION** — genuinely ambiguous | |
| AMI / income limits | **ABSENT ENTIRELY** — no such field in the schema | |
| VLIP / sweat equity | **ABSENT ENTIRELY** — zero fields, docs, or mentions | |

---

## Field 1 · Project type — the condo question stays blocked

**PUD status is provable.** Two independent sources: `pudIndicator = "Y"` and a `PUD Rider`
document (`documents[16]`) — a rider executed at closing only when the security instrument
encumbers a PUD unit.

**Condominium status is NOT derivable, and four tempting inferences are all unsound:**

- `attachmentType = "Detached"` does **not** rule out a condo. Detached/site condos are a
  recognized Fannie project type. Attachment is physical form; condominium is ownership form.
  They are orthogonal.
- `pudIndicator = "Y"` does **not** rule out a condo. A condo project can sit inside a master
  PUD; the owner then holds a condo interest *and* is subject to the PUD's master association.
- `propertyEstateType = "FeeSimple"` argues against co-op but does not prove it.
- **`condominiumIndicator = null` is silence, not denial.** This payload demonstrably writes
  explicit negatives when it knows them (`pudIndicator="Y"`,
  `fhaSecondaryResidenceIndicator="N"`), so a null is "never mapped", not "false".

⚠ **The closed-world document-inventory principle does NOT transfer to field nulls.** It
applies to the `documents[]` array (a complete classified inventory), not to unpopulated
indicator fields. Conflating the two would manufacture false verdicts —
see `docs/LOAN-SCENARIO-APPLICABILITY.md`.

### 🐛 DATA BUG — `projectLegalStructureType` carries the wrong enum

**Verified:**
```
projectLegalStructureType : 'Detached'
attachmentType            : 'Detached'      identical? True
```
MISMO's `ProjectLegalStructureType` enumeration is `Condominium | Cooperative |
PlannedUnitDevelopment`. **`"Detached"` is not a member** — it belongs to `AttachmentType`.
The two fields hold byte-identical values, and the three reference ULAD/DU exports in
`demo/*/` contain `<AttachmentType>Detached</AttachmentType>` but **no
`ProjectLegalStructureType` element at all**.

**Decision: treat `projectLegalStructureType` as NO_DATA. Never consume it.** Building a
gate on a field-copy bug would look like signal and be noise. Raise with Touchless.

**Three observationally identical worlds** — the data cannot distinguish them:
(a) detached home in a PUD, no condo regime · (b) detached condo unit within a master PUD ·
(c) condo project with the PUD flag set in error. The discriminator (`condominiumIndicator`)
is null in all three.

**Cheap disambiguator in the documents:** the `Security Instrument` rider set. PUD Rider
alone → (a). PUD Rider **and** Condominium Rider → (b). Condo Rider without PUD Rider → (c).
Only the PUD Rider appears in the 62-doc inventory, which *favours* (a) — but that is
inventory evidence, not field evidence.

---

## Field 2 · Construction — the renovation question IS answerable

**"Not a renovation / construction-to-perm loan" is PROOF**, on ~6 converging indicators:

- `loanPurposeType = "PURCHASE"` (not Construction / ConstructionToPermanent)
- `productName = "Conventional Fixed"`, `amortizationType = "FIXED"`, 360 months
- `purchasePriceAmount = propertyValuationAmount = 352000.0` — a rehab loan is sized on
  *as-completed* value and would show a renovation escrow; there is none
- `alterationsImprovementsOrRepairsAmount` null in both places it appears
- **Zero renovation machinery among the 62 documents** — no Renovation Loan Agreement, no
  draw schedule, no cost estimate, no completion certificate (1004D), no
  Construction-to-Permanent Conversion Rider. The catalog *recognizes* these doc types; they
  are absent. Closed-world inventory applies here (it is the `documents[]` array).

Honest caveat: this is proof by absence-of-every-expected-artifact plus affirmatively-stated
purpose/product — not one dispositive field. `renovationLoanIndicator` and
`constructionLoanIndicator` are null, not `"N"`.

**`constructionMethodType` (SiteBuilt vs Manufactured vs Modular) is NOT derivable — and do
NOT default it to SiteBuilt.** The property is at **15-1519 Railroad Ave, Keaau, HI 96749** —
Hawaii Island has a materially higher share of manufactured/modular housing than the
mainland, which *weakens* a SiteBuilt presumption rather than supporting it. All three
reference ULAD exports carry `<ConstructionMethodType>SiteBuilt</ConstructionMethodType>`,
so the upstream MISMO path normally populates it: **this is a Touchless mapping gap, not a
schema gap.**

---

## Field 3 · Program — "Conventional Fixed" is NOT proof

**It is a product/amortization descriptor, not a program field.** HomeReady and Home Possible
loans *are* conventional fixed-rate loans; a lender catalog will legitimately show a
HomeReady loan as "Conventional Fixed 30" while the program flag lives elsewhere. Reading
absence-of-program-name-in-`productName` as absence-of-program is exactly the inference the
rule-fidelity discipline warns against.

**Home Possible is excluded outright — PROOF.** `investorGuidelineName = "FNMA"`; Home
Possible is a **Freddie Mac** product. A Fannie-delivered loan cannot be Home Possible.

**HomeReady is strong inference, not proof** — 6 signals: LTV 73.86% and 26% down (these
programs exist to enable 97% LTV) · `loanSummary.affordability` is an empty container ·
no homebuyer-education certificate, income-limit doc, or DPA letter among 62 documents ·
borrower is not a first-time buyer (`homeOwnerPastThreeYearsType = "Yes"`, plus a financed
rental REO) · no MI certificate (consistent with no MI needed at 74% LTV) · income figure far
above any plausible 80%-AMI limit.

That last one is an *eligibility* argument resting on an AMI threshold **not present in the
payload** — under the grounding rule that number must come from an AMQ row or an SME, not
from us. **AMI/income limits: ABSENT ENTIRELY — no such field exists in this schema.**

---

## 🐛 DATA BUG — the DTI discrepancy is worse than first thought

Earlier flagged as an unexplained $780.75 gap. It is actually **three different numbers for
one concept**:

```
loanSummary.qualification.totalLiabilitiesMonthlyPaymentAmount            2,837.25
loanSummary.loans.loan[0].qualification.totalLiabilities…                428,361.00   ← 151×
sum of the 7 liabilityDetail[].monthlyPaymentAmount                        3,618.00
```

`428,361` looks like unpaid **balances** mis-summed into a monthly-**payment** slot.
**Any rule reading the `loans.loan[0]` path will be wrong.** This is a live correctness
hazard, not a curiosity.

---

## ⚠ The payload is a mid-pipeline snapshot, not a settled closed-loan record

Five independent signs, and this reframes every verdict above:

1. **The appraisal is both present and declared missing.** `documents[52]` is
   `Form 1004 Uniform Residential Appraisal`, yet `loanConditions.loanCondition[0]`
   (`CPGA_01_009`, severity **HIGH**, status OPEN) says *"Form 1004 Uniform Residential
   Appraisal is not available."*
2. **Same contradiction on flood.** Two flood-determination documents are present and
   `floodDeterminationDetail` is populated (`nfipFloodZoneIdentifier = "X"`), yet
   `CPGA_01_001` (HIGH) says a flood cert is required.
3. **All 62 documents have `active: false`**, `documentLocation: null`, `documentStatus: null`,
   `targetOCR: null`. The extraction path has not run.
4. **The entire `valuationReport` object is null** except a FEMA disaster block
   (`DR-4909-HI`, flooding). `documents[52].documentDate` is **2017-01-24** — nine years
   before the application date.
5. Metadata says `eventSource: "Income Verification"`, `modifiedBy: "dlf-income"`.

**Decision: confirm with Touchless before treating any of these three fields as a genuine
contract gap.** They may simply populate at a later pipeline stage. Asking for fields the
vendor already supplies later would waste the engagement's credibility.

⚠ **Also material to Non-Negotiable #3:** `documentSource = "LOS"` on 61 of 62 documents —
**nothing is sourced from the title company.** In this fixture the document path and the
system path are *not* independent, so doc-vs-system comparison is trivially identical. The
fixture cannot test the cross-source reconciliation the product is built on.

---

## Decision — what to do

**1 · Add two scenario gates now (both PROOF-grade).**
`renovation / construction-to-perm = absent` and `Home Possible = absent`. Each cites its
evidence field. Together they address the bulk of ~111 rules.

**2 · Do NOT gate on:** condominium (needs the Security Instrument rider set),
`constructionMethodType` (ambiguous, Hawaii location weakens any default), HomeReady
(inference only), AMI (field doesn't exist). These stay `NO_DATA` — visible and countable.

**3 · Never consume `projectLegalStructureType`** until the enum bug is fixed upstream.

**4 · Quarantine `loans.loan[0].qualification.totalLiabilitiesMonthlyPaymentAmount`.** A
151× wrong value in a DTI field is a correctness hazard; prefer
`loanSummary.qualification` and reconcile against `liabilityDetail`.

**5 · Two questions for the Touchless conversation** (cheaper and more specific than
"extract everything"):
- Is this payload final, or does a later stage populate `propertyInProjectIndicator`,
  `condominiumIndicator`, and `constructionMethodType`?
- Why do the open HIGH conditions contradict the document inventory, and why is
  `active: false` on all 62?

**6 · The cheapest unlock for the condo question is the `Security Instrument` rider set** —
one document, three-way discriminator, already present in the inventory.

---

## Related

- `docs/SCENARIO-GATE-EXPERIMENT-2026-07-30.md` — the gate, the disjunction bug, the tests
- `docs/LOAN-SCENARIO-APPLICABILITY.md` — three reasons a document is absent
- `src/gates/scenario_gate.py` · `src/gates/test_scenario_gate.py`
