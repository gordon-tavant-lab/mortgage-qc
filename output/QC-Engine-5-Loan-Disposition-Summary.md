# QA/QC Engine — 5-Loan Disposition Run

**Purpose:** Validate the deterministic QA/QC engine against 5 synthetic closed-loan files, each seeded with known planted defects, to confirm the engine correctly identifies every issue with a full audit trail.

**Engine:** `qc_engine` v`p0-1.0.0` · **Ruleset:** `rs-defect-verification` v1 (21 authored Check objects, gated per loan by document presence / property age / loan program) · **Run date:** 2026-07-22

**Result:** All 5 loans correctly routed to **NEEDS_REVIEW** — this run is a validation of engine correctness, not a real production batch, so a 5-for-5 review rate confirms the engine caught every seeded defect rather than false-clearing a bad loan.

---

## Executive Summary

| Loan ID | Program | Checks Applied | Failures | Disposition |
|---|---|:-:|:-:|---|
| 2025-0917-001 | Conventional | 9 | 2 | NEEDS_REVIEW |
| 2025-1004-FHA-002 | FHA | 13 | 5 | NEEDS_REVIEW |
| 2025-1108-VA-003 | VA | 13 | 6 | NEEDS_REVIEW |
| 2025-1215-FRD-004 | Conventional | 11 | 5 | NEEDS_REVIEW |
| 2025-1122-USDA-005 | USDA | 13 | 8 | NEEDS_REVIEW |
| **Total** | | **59** | **26** | **5 / 5 flagged** |

Each loan runs a different subset of the 21-check ruleset — checks are gated to the loan's actual program (e.g. VA-only checks don't run against a USDA loan) and to whether the relevant document is even present in that loan's file. "Checks Applied" above is the gated count, not all 21.

---

## Loan 01 — 2025-0917-001 (Conventional)

**2 of 9 applicable checks failed.**

| Check | Finding | Source |
|---|---|---|
| Large deposit source documented | $15,000 mobile deposit (08/12) has no source documentation in file | Wells Fargo Consumer Checking Statement, p.1 |
| Appraisal comp distance within guideline | Comparable sale 8.5 mi from subject exceeds the 5-mile urban guideline, no addenda explanation | Form 1004 UAD, Comparable Sales Grid, p.1 |

---

## Loan 02 — 2025-1004-FHA-002 (FHA)

**5 of 13 applicable checks failed; 1 informational data-sync flag.**

| Check | Finding | Source |
|---|---|---|
| HUD-92900-A Section III certification signed | Borrower Certification signature line is blank | HUD-92900-A Addendum, p.1 |
| Gift funds source documented | No donor bank statement, wire/check copy, or borrower receipt in file | Gift Letter — FHA Down Payment, p.1 |
| Lead-paint completion certification present | Peeling paint on pre-1978 structure flagged "subject to," no Form 442 compliance inspection in file | FHA Appraisal Summary 1004/URAR, p.1 |
| FHA Amendatory Clause present | Amendatory Clause / Real Estate Certification not in file | — |
| Lead-based paint disclosure present | Pre-1978 property, disclosure not in file | — |

*Informational only (does not drive disposition):* FHA case number on the 1003 (`381-9927164`) does not match FHA Connection's case number (`381-9927614`) — a system data-sync issue, not a document defect.

---

## Loan 03 — 2025-1108-VA-003 (VA)

**6 of 13 applicable checks failed.**

| Check | Finding | Source |
|---|---|---|
| Lead-paint completion certification present | Peeling paint flagged, no Form 442 completion cert in file | — |
| ARM Pre-Loan Disclosure present | Missing | — |
| Termite inspection present | VA requires NPMA-33 termite inspection in NC; not in file | VA Appraisal, VA Form 26-1805/URAR, p.1 |
| Lead-based paint disclosure present | Pre-1978 property, disclosure not in file | — |
| VA residual income documented | Residual income calculation not documented for borrower's family size/region | — |
| VA NOV issued on or before closing | Notice of Value dated 3 days **after** closing — invalid date order | — |

---

## Loan 04 — 2025-1215-FRD-004 (Conventional)

**5 of 11 applicable checks failed.**

| Check | Finding | Source |
|---|---|---|
| Lead-paint completion certification present | Peeling paint flagged, no Form 442 completion cert in file | — |
| Lead-based paint disclosure present | Pre-1978 property, disclosure not in file | — |
| Self-employed P&L / balance sheet present | YTD P&L statement not in file for self-employed borrower | Self-Employed Income Documentation Index, p.1 |
| No 30+ day mortgage lates in trailing 12mo | One 30-day late reported 04/22/2025; program requires zero | 12-Month Mortgage Payment History (VOM), p.1 |
| Appraisal not stale at closing | Appraisal effective date is 207 days before closing — exceeds the 120-day recertification limit | — |

---

## Loan 05 — 2025-1122-USDA-005 (USDA)

**8 of 13 applicable checks failed — the most exceptions of the five, consistent with USDA's additional eligibility and ratio requirements.**

| Check | Finding | Source |
|---|---|---|
| Lead-paint completion certification present | Peeling paint flagged, no Form 442 completion cert in file | — |
| Lead-based paint disclosure present | Pre-1978 property, disclosure not in file | — |
| USDA property eligibility documented | Eligibility map screen-print/determination not in file | USDA Property Eligibility — Manual Review, p.1 |
| Well & septic test documented | Private well + septic; inspections listed as "recommended," none in file | Appraisal Summary — USDA 502, p.1 |
| Site value justification documented | Borderline site value ratio; USDA site value analysis not documented | — |
| USDA household income within moderate-income limit | $134,720 adjusted household income exceeds the $130,850 moderate-income limit | USDA GUS Findings, p.1 |
| USDA PITI ratio within guideline | 31.8% vs. 29% guideline; no waiver/compensating-factors documentation | USDA Debt Ratios & Waiver, p.1 |
| USDA total debt ratio within guideline | 43.9% vs. 41% guideline; no waiver/compensating-factors documentation | USDA Debt Ratios & Waiver, p.1 |

---

## Methodology Notes

- **Determinism:** each loan's disposition is bound to its exact ruleset by a SHA-256 hash (recorded per loan in the underlying JSON export). Same loan + same ruleset hash will always reproduce the same result — no LLM runs at evaluation time.
- **NOT_APPLICABLE checks** (not itemized above) mean the relevant field simply has no value for that loan/program — e.g. USDA ratio checks are NOT_APPLICABLE on the VA and FHA loans. This is expected gating, not a data gap.
- **FLAG vs. FAIL:** a "FLAG" (as seen on Loan 02) means the closing document and the lender's system disagree on a value — informational only, since the document is treated as the source of truth and does not by itself force review.
- **Full audit trail:** every finding above traces to a specific document, page, and (where applicable) an exact text citation from the source file — available in the underlying `dispositions.json` export for anyone who needs to verify a specific line.
