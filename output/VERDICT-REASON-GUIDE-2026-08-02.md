# Verdict Reason Guide — why every check is in the status it's in

**Date:** 2026-08-02. Companion to `output/gold/AUDIT-STAT-REPORT-p0-2026-08-02.md` and the
three RESOLVE reports (`RESOLVE6`/`RESOLVE7`/`RESOLVE8`) — this doc is the deep-dive answer to
"explain the reasons behind each verdict so I can understand better," covering all four
statuses, not just the two most complex ones. Real examples throughout are pulled directly
from `output/AUDIT-EXPORT-p0-loan-12607601215-2026-08-02.csv` (loan 12607601215).

**Current distribution (1,105 gold-ruleset checks):** PASS 133 · NEEDS_REVIEW 92 ·
NOT_APPLICABLE 443 · NOT_COMPILED 437.

---

## The core mental model

Two axes explain everything below. Once these are clear, every sub-category is just a detail.

**Axis 1 — did a runnable check exist, and was it evaluated against this loan?**

| | A real check exists | Evaluated against this specific loan |
|---|:---:|:---:|
| **PASS / NEEDS_REVIEW / FAIL** | ✅ | ✅ |
| **NOT_APPLICABLE** | ✅ (the check exists — its own precondition just doesn't hold) | ✅ |
| **NOT_COMPILED** | ❌ | never got the chance |

`NOT_COMPILED` is the odd one out: it's not a verdict about this loan at all — it's a
statement that the *engineering* to answer this question doesn't exist yet, for *any* loan.
Every other status is a real, per-loan answer from a real, running check.

**Axis 2 — once a check runs, what does the verdict actually mean?**

- **PASS** — the check's condition genuinely holds (or the demo has deliberately chosen to
  treat it as holding — see below).
- **NOT_APPLICABLE** — the check's own *trigger* doesn't apply to this loan at all (e.g. a
  refinance-only check on a purchase loan). This is different from PASS: PASS says "we
  checked, and the answer is good"; NOT_APPLICABLE says "this question was never relevant to
  this loan in the first place."
- **NEEDS_REVIEW** — the check ran, but the honest answer requires a human, either because no
  data source can ever decide it, or because the specific fact this loan needs isn't captured.
- **FAIL** — the loan's own data affirmatively violates the rule. (Only 1 of 1,105 today.)

Keep this distinction in your head throughout: **NOT_APPLICABLE means "the question doesn't
apply here"; NEEDS_REVIEW means "the question applies, and only a human can answer it";
NOT_COMPILED means "nobody has built a way to ask this question of any loan yet."**

---

## 1. NOT_COMPILED (437) — the engineering doesn't exist yet, for any loan

Every category below is a **compile-time** gap — the exact same 437 checks would show
NOT_COMPILED on *every* loan run through this engine, not just this one, because nothing
loan-specific is missing here. What's missing is either data the *vendor contract* has never
promised, ambiguous rule text an SME needs to interpret, or logic nobody has built.

| # | Category | Count | What it means |
|---|---|---:|---|
| 1 | Trigger-gated, needs fact machinery | 93 | The check only applies under a scenario (e.g. "borrower has Limited English Proficiency") that isn't derivable from any document |
| 2 | Presence-gate, needs conditional logic | 79 | Needs document *content* completeness, not just presence — 52 of these are Form 1004 appraisal-content checks |
| 3 | Not converted by design | 72 | Check type out of this build's scope (reverification, list screening), or date-math blocked on missing anchor dates |
| 4 | Cross-doc, no curated comparison | 62 | Needs comparing two different documents to each other — no curated logic exists yet |
| 5 | Threshold not parseable | 52 | Rule cites a limit but doesn't state it clearly enough to trust — the compiler refuses to guess |
| 6 | Computation not LTV/DTI | 48 | Needs a recalculation this project has only built for LTV and DTI so far |
| 7 | Demo-excluded | 20 | Deliberately dropped from *this demo's* scope — documented, reversible |
| 8 | Compound docs, needs multi-doc logic | 7 | Satisfiable by any of several alternative documents — no single one decides it |
| 9 | Pure-presence, reviewed and rejected | 4 | Individually reviewed; no safe document-type match exists in the vendor's vocabulary |

### 1.1 Trigger-gated, needs fact machinery — 93 checks

The check's *applicability* depends on a fact about the borrower or transaction that simply
isn't derivable from a document inventory — it might be verbal, or might never be written down
anywhere structured.

> **`O-CFPB-14500 / O-CFPB-54136`** — "(Best Practice) The borrower was not provided with a
> clear and timely Limited English Proficiency (LEP) disclosure..."
> **Why blocked:** "Only applies when the borrower is a Limited English Proficiency
> individual, a fact not knowable from the document inventory alone."

**Fixed by:** a new vendor data element (a language-preference field), not better extraction of
something that already exists somewhere.

### 1.2 Presence-gate, needs conditional logic — 79 checks

The rule needs more than "is document X present" — it needs to know something about the
document's *content*.

> **`Final URLA / URLA-Final-2`** — "The final 1003 application is inaccurate or incomplete."
> **Why blocked:** "The Final URLA/1003 must not only exist but have all sections completed
> and accurate; a completeness/accuracy content check goes beyond mere presence."

52 of these 79 are specifically Form 1004 appraisal-content checks — **the appraisal IS in the
file; nobody has extracted its interior fields (comps, GLA, condition rating) yet.** This is the
single largest concentrated unlock in the whole report if Touchless widens appraisal extraction.

### 1.3 Not converted by design — 72 checks

Two distinct things bundled under one label:

- **Scope decision**: check types (`reverification`, `list_screening`) this build never took
  on — a genuine engineering/product-scope call, not a discovered gap.
- **Date starvation**: date-window checks ("within 30 days of X") blocked because **every one
  of this loan's 62 documents has a null `documentDate`** — there's no anchor date anywhere to
  measure a window against.

> **`O-FED-14507 / O-TILA-54206`** — HPML appraisal-delivery-timing requirement.
> **Why blocked:** "Check type not in this build's scope."

### 1.4 Cross-doc, no curated comparison — 62 checks

Needs comparing two *different* documents against each other, and the comparison hasn't been
curated yet.

> **`Final URLA / URLA-Final-9`** — "The employment dates listed on the 1003 do not match other
> employment documentation in the file."
> **Why blocked:** "Rule requires comparing two documents to each other; no curated comparison
> logic exists yet."

**Fixed by:** mostly extraction — you need *both* sides of a comparison structured before you
can compare them. (11 of these were resolved during resolve6/7 once one side was already
extractable; the rest are still waiting on the second side.)

### 1.5 Threshold not parseable — 52 checks

The rule text cites *some* limit, but not clearly enough for the compiler to safely turn into a
number+direction. The compiler is deliberately conservative here — an honest "can't parse this"
beats inventing a number the source text doesn't actually state.

> **`Custodial Acct / Custodial Acct`** — "A custodial account that is an irrevocable trust...
> [is an] ineligible source [under certain conditions]."
> **Why blocked:** "Rule cites a threshold but the compiler could not extract one unambiguous
> number+direction from the text."

**39 of these 52 are genuinely ambiguous rule text** — this is the cheapest bucket left to
unlock, because it needs one conversation with an SME (confirm the real number from the Selling
Guide), not more engineering.

### 1.6 Computation not LTV/DTI — 48 checks

Needs a real recalculation this project has only built for two ratio types (LTV, DTI) so far.

> **`O-FNM-15332 / O-FNM-50255`** — "The reserves are insufficient to meet the amount needed..."
> **Why blocked:** "Rule requires a recomputation this project only builds for LTV/DTI today."

Most of these are additionally blocked because the *inputs* to that math (liability detail,
insurance coverage amounts) are null in the payload — so even building the computation logic
wouldn't immediately unlock most of them without a vendor extraction widening too.

### 1.7 Demo-excluded — 20 checks

A deliberate, documented, **reversible** decision for *this demo build specifically* — logged
in `demo_exclusions.json` with a named reason, not silently dropped.

> **`O-FNM-15350 / O-FNM-55916`** — "The loan file did not document sufficient funds for
> closing." **Reason:** `not_automatable_for_demo`.

### 1.8 Compound docs, needs multi-doc logic — 7 checks

The requirement can be satisfied by *any of several* alternative documents — no single named
document decides it.

> **`O-FNM-15336 / O-FNM-00235`** — gift funds must be verified via donor-account verification,
> OR proof of transfer to borrower, OR proof of transfer to closing agent.
> **Why blocked:** "Clearing this requires evidence from any of several alternative
> documentation paths, not a single named document."

### 1.9 Pure-presence, reviewed and rejected — 4 checks

Individually hand-reviewed, and a real match was **deliberately not made** because it risked a
false positive.

> **`O-BP-14663 / O-BP-54653`** — "Flood Insurance Subject to Change" disclosure.
> **Why blocked:** "The disclosure name doesn't exactly match any closed-list document type" —
> the closest candidates in Touchless's vocabulary were different documents entirely, and
> guessing would risk a false match.

This is a *closed*, reviewed gap — the review already happened and correctly said no, not an
open question waiting on more analysis.

---

## 2. NEEDS_REVIEW (92) — the check ran, and honestly needs a human

Unlike NOT_COMPILED, every one of these checks **exists and evaluated against this loan's real
data.** The honest conclusion was "a human needs to look at this," for one of six distinct
reasons.

| # | Category | Count | What it means |
|---|---|---:|---|
| 1 | Irreducible judgment | 39 | No field can ever answer this, even in principle |
| 2 | Extraction gap, doc present | 28 | The document IS in the file; the field inside it isn't extracted yet |
| 3 | Data never captured | 18 | No field or document exists anywhere in the vendor contract for this concept |
| 4 | Confirmed red flag | 3 | The loan's own data affirmatively shows the condition — the queue working correctly |
| 5 | Vendor data trust | 2 | A field exists but its value looks implausible or stale |
| 6 | Needs real logic built | 2 | A small, scoped computation this project hasn't built (e.g. geocoding) |

### 2.1 Irreducible judgment — 39 checks (the true, permanent floor)

> **`O-EPD-14459 / O-EPD-52931`** — "The subject photos reveal inconsistencies."
> **Why:** photo/visual review — no field will ever answer this.

> **`Form 1033 #26`** — "Comparable property characteristics were reported inaccurately...
> CU comparables tab was not reviewed" — requires reading appraiser narrative.

**Nothing fixes these except a human.** This is the honest, permanent floor — 42% of
NEEDS_REVIEW, and it should *stay* NEEDS_REVIEW forever, on every loan.

### 2.2 Extraction gap, doc present — 28 checks

> **`O-FNM-15306 / O-FNM-00181`** — credit report requirements.
> **Why:** "Credit Report doc present; `creditReportVendorName`/type fields null."

The document exists in the file — Touchless just hasn't typed out its specific fields yet.
**Fixed by**: vendor extraction widening. Zero new code needed here once that happens.

### 2.3 Data never captured — 18 checks

> **`O-FNM-15455 / O-FNM-58314`** — eNote Vault legal/technical compliance.
> **Why:** "zero electronic/eNote/eVault tokens in payload" — not even a concept for this exists
> in the data contract.

13 of these 18 hang on **one single missing fact**: was this closed as an electronic
transaction? One boolean field from the vendor would resolve 13 checks at once.

### 2.4 Confirmed red flag — 3 checks (the system working as intended)

This is the *good* kind of NEEDS_REVIEW — not a gap, a genuine catch.

> **`O-EPD-14458 / O-EPD-52922`** — "The down payment source is a gift... in lieu of coming
> from personal accounts."
> **Why:** the loan's own data shows `assetType=GIFT_OF_CASH`, `fundSourceType=RELATIVE` —
> exactly the pattern this check exists to flag. Correctly never auto-cleared.

### 2.5 Vendor data trust — 2 checks

> **`Closing Conditions / UW Condition-A`** — "Have all underwriting closing conditions been
> met?"
> **Why:** all conditions show status "OPEN" on a loan that's already closed and funded — looks
> like a stale pre-closing snapshot, but is *also* consistent with a genuine unresolved
> condition, so the engine can't safely resolve it either way.

### 2.6 Needs real logic built — 2 checks

> **`O-EPD-14457 / O-EPD-52919`** — "significant or unrealistic commute distance."
> **Why:** needs geocoding + distance math — a small, scoped build, not a data problem.

---

## 3. NOT_APPLICABLE (443) — the question doesn't apply to this loan

Every one of these checks exists and ran — its *own trigger condition* was proven false for
this specific loan. Each carries a cited fact from the real payload, not a guess.

| # | Category | Count | What it means |
|---|---|---:|---|
| 1 | Precondition not applicable (scenario-gated) | 418 | The check's trigger scenario is provably false, cited to a payload fact |
| 2 | Structural applicability | 19 | The card-level applicability rule (from the original AMQ) resolved false |
| 3 | Auto-pass system-check, also structurally not applicable | 6 | Would have needed DU/EPIC access, but the card doesn't even apply to this loan's structure |

### 3.1 Precondition not applicable — 418 checks

> **`Final URLA / URLA-Final-6`** — "The refinance type selected on the final 1003 does not
> match the final 1008 and/or the final DU."
> **Why NA:** "Refinance-type comparison triggers only on a refinance; `loanPurposeType='PURCHASE'`
> — a purchase loan has no refinance type on any document."

> **`O-FNM-15304 / O-FNM-58197`** — URLA Additional Borrower form completeness.
> **Why NA:** "Single borrower ('Andy America'), no co-borrower → no URLA Additional Borrower
> form is applicable."

This is the biggest single bucket in the whole report, and it's why NOT_APPLICABLE jumped from
43 (original audit) to 443 across the three resolve passes — most of these checks were never
actually about *this loan* to begin with (they're refinance-only, condo-only, ARM-only, etc.),
and a compiler bug used to prevent that "doesn't apply" answer from ever being recognized.

### 3.2 Structural applicability — 19 checks

> **`O-FNM-53855`** — "Form 1033 #20... project eligibility requirements... for the
> condominium project."
> **Why NA:** "Precondition not met: `Loans.PropertyType == 'Condominium'` does not hold for
> this loan" (it's a detached PUD).

### 3.3 Auto-pass, also structurally not applicable — 6 checks

A special case: these checks would have needed the DU/EPIC/Loan Delivery auto-pass treatment
(see §4 below) *except* the loan's structure means the card doesn't even apply, so
NOT_APPLICABLE wins over auto-pass.

> **`UGV Exception / PrivateBank`** — Underwriter Guideline Variance approval.
> **Why NA:** "`Loans.LoanType == 'Portfolio'` does not hold for this loan" (it's Conventional).

---

## 4. PASS (133) — real or simulated, and the difference matters

**This is the section most worth reading carefully.** Only 22 of 133 PASSes are a genuinely
verified match against real loan data. The other 111 (83%) are a deliberate, documented
simulation — indistinguishable in the output from a real PASS.

| # | Category | Count | What it is |
|---|---|---:|---|
| 1 | Auto-pass: DU not accessible | 74 | Can only be verified inside Fannie Mae's Desktop Underwriter — no connection to it |
| 2 | Auto-pass: DU-relief precondition not accessible | 27 | Applies only if DU granted a specific relief — equally unverifiable |
| 3 | Real data match | 22 | Genuinely resolved from real, populated loan data |
| 4 | Auto-pass: Loan Delivery/ULDD not accessible | 4 | Same pattern, Fannie Mae's delivery system |
| 5 | Auto-pass: CU not accessible | 4 | Same pattern, Collateral Underwriter |
| 6 | Auto-pass: UCD not accessible | 1 | Same pattern, Uniform Closing Dataset collection |
| 7 | Auto-pass: EPIC not accessible | 1 | Same pattern, an internal lender system |

### 4.1–4.2, 4.4–4.7 — Auto-pass, system not accessible (111 checks, 83% of all PASSes)

> **`O-FNM-15334 / O-FNM-50257`** — "The bank statements did not clearly identify the borrower
> as the account owner, include the account number..."
> **Why "PASS":** "auto-pass: requires verification inside `du_not_accessible`, which this
> project has no connection to (demo-scoped decision)."

**This is a deliberate, acknowledged departure from the project's own "never show a false
clean" discipline**, scoped explicitly to this demo. The decision, made explicitly by you
mid-session: *"we cannot call into the DU system to verify, we will simulate they pass"* — and
the output was deliberately chosen to be **indistinguishable** from a real, independently
verified PASS (documented in full in `autopass_no_system_access.json`'s `_meta` block).
**Anyone using PASS as a headline metric needs to know 83% of it is a policy decision, not a
verified outcome.**

### 4.3 Real data match — 22 checks

> **`CIP DATA POINTS / CIP data points`** — "The 4 Customer Identification Program (CIP) data
> points have not been provided or are inconsistent."
> **Why real PASS:** identity data genuinely cross-checked and matched across two independent
> documents (1003 application vs. Schedule C tax filing) — name and SSN agree.

> **`O-BP-14663 / O-BP-54652`** — Borrower Certification and Authorization to Release
> Information disclosure.
> **Why real PASS:** the document is confirmed present in the closed-world inventory, and the
> defect condition is a pure absence check — no compound clause left unproven.

These are the checks that survived the strictest bar in the whole system: a document-presence
check only becomes a real PASS when the rule text is a *pure* absence statement, and the
compound ones (round 3's review of 23 similar candidates rejected 21 for exactly this reason —
see `RESOLVE8-ROUND-3-2026-08-02.md`) don't qualify.

---

## Putting it all together — one table

| Status | Count | The honest one-line meaning |
|---|---:|---|
| **PASS** | 133 | "The condition holds — for real (22) or by deliberate demo-scoped simulation (111)." |
| **NEEDS_REVIEW** | 92 | "I ran the check; only a human can finish it — forever (39) or until more data lands (53)." |
| **NOT_APPLICABLE** | 443 | "This question was never relevant to this specific loan." |
| **NOT_COMPILED** | 437 | "Nobody has built a way to ask this question of *any* loan yet." |

And the fastest way to move each number, if that's ever useful to plan around:

- **Shrink NOT_COMPILED fastest** → an SME session on the ~55 ambiguous rule-text checks
  (threshold + date-window), zero new engineering required.
- **Shrink NOT_COMPILED biggest single lever** → Form 1004 appraisal field extraction from the
  vendor (~62+ checks depend on it across two categories).
- **Shrink NEEDS_REVIEW** → mostly the same vendor-extraction lever; only the 39
  irreducible-judgment checks are permanent.
- **Make PASS more honest** → connect to DU/EPIC/Loan Delivery for real, or accept the 83%
  simulated-PASS ratio as this demo's known, stated limitation.
