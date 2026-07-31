# 015 — Bucket B: deepen final-1003 extraction; three groups, zero new fixtures needed

**Status:** Accepted 2026-07-29 (Gordon — "great to hear, we have them", re: rules that
only need deeper extraction from a document already in every loan folder)

## Decision
3 of the 16 YELLOW groups — **21, 24, 30** — all concern the **final** 1003/URLA, which
every loan (01–05) already has as `01_Final_1003_URLA.pdf`, and `extract_loan.py` already
parses it (doc type `final_1003`, 10 field specs today: `loan_number`,
`loan_program_1003`, `loan_purpose_1003`, `employment_start_date_1003`,
`base_monthly_income_1003`, `title_vesting_1003`, `fha_case_number_1003`,
`year_built_1003`, `payoff_amount_1003`, `cash_out_to_borrower_1003`). These three groups
are **actionable now** by extending the existing `final_1003` field/fact specs — no new
synthetic loan document required. (This is narrower than the original "verify: likely just
the final-URLA-sections group" assumption — investigation below shows all three
Additional-Borrower/section-completeness groups qualify, not only one.)

## The three groups
| Group | Row(s) | Condition | What's missing today |
|---|---|---|---|
| 21 | 20, 22, 23, 24 | "All sections of URLA Additional Borrower form not fully completed, correct &/or signed as applicable" (FHA/FRD/RHS/VA codes) | Co-borrower section fields aren't captured as their own fields |
| 24 | 29 | "Sections of the final URLA were incomplete, inaccurate &/or not signed by all parties" (FHA) | Per-section completeness isn't derived at all |
| 30 | 21 | Same as 21, Fannie Mae code variant (O-FNM-15304) | Same gap as 21 |

## Why these are Bucket B, not Bucket A (verified, not assumed)
The "Additional Borrower form" language reads like it could name a wholly separate
document (Fannie Mae does publish a standalone "URLA – Additional Borrower" form, used
when a loan has more borrowers than the main form's two slots). That would have been a
Bucket A fixture gap. Verification via `pdftotext` on the actual synthetic PDFs shows
otherwise for this pilot's fixtures:

```
loan 01: "Co-Borrower Name", "Co-Borrower SSN", "Co-Borrower DOB",
         "Section 1b — Current Employment (Co-Borrower)"
loan 05: "Co-Borrower", "Co-Borrower Employer", "Co-Borrower Base Pay",
         "Co-Borrower Overtime (avg last 2 yr)"
```

All of this lives **inside the single `01_Final_1003_URLA.pdf` file**, in the same
per-section layout (`Section 1 — Borrower Information`, `Section 1b — Current Employment
(Borrower)` / `(Co-Borrower)`) the extractor already reads for the Borrower's own fields.
The document — and the data the AMQ rule is asking about — is already in hand.

This is corroborated by the extractor's own current behavior: `extract_loan.py`'s
`add_field` (line 213) has an explicit "first occurrence wins (borrower before
co-borrower)" rule — meaning when a field regex matches both the Borrower's and the
Co-Borrower's line (e.g. two "Employment Start Date" lines), **only the Borrower's value
is kept today; the Co-Borrower's matching line is silently dropped.** That is exactly a
"deeper extraction from a document we already have" gap, not a missing-document gap: the
raw text is parsed and discarded, not absent.

## What we will do (spec for the follow-on code change — not performed here)
Extend `extract_loan.py`'s `final_1003` entry in `FIELD_SPECS` (and/or `FACT_SPECS`) to:
1. Capture co-borrower variants of the fields already captured for the primary borrower
   (e.g. `employment_start_date_1003_coborrower`, mirroring the existing
   `employment_start_date_1003` regex against the "(Co-Borrower)" section header instead
   of "(Borrower)"), removing the current "first occurrence wins" data loss for the
   co-borrower's own values.
2. Add a small set of per-section presence/signature facts (e.g.
   `sig_1003_section_1_present`, `sig_1003_section_1b_coborrower_present`) generalizing
   the existing `sig_1003_borrowers_present` fact (line 128) from "some signature line
   exists somewhere" to "the specific sections group 21/24/30 need are present and
   signed" — this is what makes "per-section completeness" (group 24's `machine_checkable`)
   and "Additional Borrower form presence + signature" (groups 21/30's) real, not just
   whole-document presence.
3. `stays_human` remains unchanged for all three groups: "fully completed, correct" /
   "inaccurate" — semantic correctness of section content is still a human judgment call;
   only presence/completeness-by-field and signature detection move to Bucket B/GREEN.

No new loan folder, no new PDF, no ruleset/`.py`/`.ttl` edit performed by this decision —
this document is the verified spec; a human session applies it.

## Implementation (applied same day, 2026-07-29)
Built exactly as specced above, with one deliberate adjustment and one honest surprise:

- `extract_loan.py`: added `extract_coborrower_fields()` (co_borrower_name/dob via
  unambiguous Section-1 labels; employer/start-date/income via a header-scoped search
  for `Section 1b...(Co-Borrower)`, plus a fallback for loan 05's inline
  `Co-Borrower Employer`/`Co-Borrower Base Pay` labels — its 1003 doesn't use the
  Section-1b sub-header pattern at all) and `extract_coborrower_signature_fact()`
  (always resolves true/false when a co-borrower exists — never left unset, per the
  decision-008 no-silent-pass discipline).
- **Adjustment:** dropped `employment_start_date_1003_coborrower` from the new shape's
  required fields. Loan 05's co-borrower section genuinely has no start date field at
  all — requiring it would invent a specificity the vague AMQ condition text
  ("not fully completed... as applicable") doesn't support. Kept: employer + income +
  signature only.
- New shape `CoBorrowerSectionCompleteShape` (`CHK-APP-008`, `blocks/application.ttl`),
  mapped in `amq_compiler.py` via **exception code**, not question code — this also
  fixed a latent collision bug (question code `O-FHA-15293` is shared by two different
  rows, 20 and 29; exception codes are unique per row and are now what `MAPPED_SHAPES`
  keys on throughout).
- **Honest surprise:** the new check fires on loan 05 as an unexpected extra — its
  final 1003 has no signature line anywhere (verified: zero matches for "Signat" in the
  whole document). This is a genuine, real gap the original hand-authored 5-defect
  answer key never captured, not a false positive. Recorded in `run_audit.py`'s
  `JUSTIFIED_EXTRAS` with the verification note, so it prints as `EXTRA(justified)`
  rather than silently passing or breaking the success bar. `OVERALL: PASS`,
  25/25 detected, 0 unexplained extras, 1 justified extra, deterministic
  (shapes manifest version 6).

## Cross-links
[[002]] (extraction from syn PDFs — the `final_1003` doc type these field specs extend),
[[009]] (two-layer compile — Layer 2 config-time widening), [[014]] (the sibling Bucket A
decision — the **initial**-URLA variants of these same conditions, which do *not*
qualify for this treatment because no initial-URLA document exists), [[016]] (the sibling
Bucket C decision).
