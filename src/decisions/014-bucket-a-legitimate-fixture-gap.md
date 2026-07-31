# 014 — Bucket A: YELLOW groups blocked on a missing synthetic fixture are still legitimate rules

**Status:** Accepted 2026-07-29 (Gordon — Bucket A rules "are still legitimate/valid, we just
never built a synthetic test loan containing that document")

## Decision
12 of the 16 YELLOW groups in `compiled/triage_application_verification.json`'s
application-verification triage are blocked because the document type the rule needs does
not exist as a file in any of `demo/syn/loan 01`..`loan 05` — **not** because the rule's
condition is unclear. These stay **YELLOW**, not RED, not silently dropped, and are tagged
with a distinct blocked-reason (`missing_fixture`, as opposed to `needs_sme_judgment`) so a
future reviewer never confuses "we haven't built the test document yet" with "the rule
itself doesn't make sense." No code or ruleset change is scheduled by this decision — see
[[013]] (this PoC does not gate on SME sign-off, but it also doesn't fake automation it
can't do yet).

## The corrected 12-group list (verified against actual files, not assumed)
Verified by `find`-ing every loan folder in `demo/syn/loan 01`..`loan 05` for the document
each group's `needed_data` names, and cross-reading the exact AMQ row text in
`doc/PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv`. Zero matches were found for any
of these document families in any of the 5 loan folders:

| Group | Row(s) | Condition (abridged) | Missing document |
|---|---|---|---|
| 1 | 66 | LEP preferences not obtained from applicant | LEP preference record/form |
| 2 | 65 | LEP disclosure not provided at application | LEP disclosure |
| 13 | 36 | HUD-92564-CN not evident timely | HUD-92564-CN (For Your Protection: Get a Home Inspection) |
| 15 | 71, 72 | VA Counseling Checklist missing/not timely | VA Form 26-0592 Counseling Checklist |
| 16 | 38 | Informed Consumer Choice Disclosure Notice missing | Informed Consumer Choice Disclosure |
| 18 | 37 | HUD-92900-B missing/not timely | HUD-92900-B (loan 02 has HUD-92900-**A**, a different form — verified distinct) |
| 35 | 48–51 | Initial URLA Additional Borrower form incomplete | a distinct **initial**-URLA document |
| 39 | 43, 44 | Initial URLA sections incomplete (VA) | a distinct **initial**-URLA document |
| 40 | 57 | Initial URLA sections incomplete (FHA) | a distinct **initial**-URLA document |
| 42 | 70 | Form 1103 (SCIF) not fully completed (FRD) | Form 1103 / Supplemental Consumer Information Form |
| 48 | 69, 1709 | Form 1103 (SCIF) not fully completed (FNM) | Form 1103 / Supplemental Consumer Information Form |
| 50 | 46, 47 | ROV-process disclosure not provided at application | Reconsideration-of-Value process disclosure |

## The initial-vs-final URLA nuance (verified carefully, per instruction)
Every loan folder contains exactly one URLA file, always named `01_Final_1003_URLA.pdf`
(literally the **FINAL**, signed-at-closing 1003 — confirmed by its own header text,
"FINAL — Signed at Closing"). No loan folder contains a distinct **initial** 1003/URLA.
`find -iname "*initial*"` across all 5 folders returns exactly one hit:
`demo/syn/loan 01/05_Initial_Disclosure_Package_Index.pdf` — per Gordon's explicit
clarification this is a disclosure-package **index** document, not an initial 1003/URLA
application, so it does not satisfy groups 35/39/40's need. This is corroborated by the
code itself: `extract_loan.py`'s `DOC_TYPES` list (line 29) has exactly one 1003-related
entry, `("final_1003", r"Final_1003")` — there is no `initial_1003` doc type anywhere in
the extractor. `amq_compiler.py`'s `DOC_KEYWORDS` (line 101) even maps the phrase
`"initial .{0,10}application"` to the **same** `final_1003` extractor doc type as a
same-file keyword shortcut — a latent bug that would silently point an "initial URLA"
rule at the final document if ever compiled naively. Groups 35, 39, 40, 42, 48 are
correctly Bucket A **because of this real gap**, not despite it — do not let the
`final_1003` keyword mapping bug paper over the fact that no initial-URLA document exists
to check against. (Not fixed here — see instruction not to touch `.py` files; flagged for
the human doing the follow-on code work.)

## What we will do
- Bucket A groups remain **YELLOW** in `triage_application_verification.json` (no
  downgrade to RED — the condition is clear; only the test data is missing).
- Add a `blocked_reason: "missing_fixture"` tag (or equivalent field) distinct from RED's
  implicit `needs_sme_judgment`, the next time the triage/ruleset artifacts are
  regenerated — this is a spec for that follow-on work, not performed here.
- The actual unblocking work — generating new synthetic fixture documents (LEP
  disclosure, VA Counseling Checklist, HUD-92900-B, Form 1103/SCIF, ROV disclosure, an
  Unmarried Addendum, an Additional Borrower form, and — largest lift — a genuinely
  distinct initial-URLA package per loan) — is **deferred, not scheduled**. It is real,
  legitimate future work, tracked here so it isn't lost or silently reprioritized away.

## Cross-links
[[009]] (full-workbook compile; these are among the "unmapped" applicable rules awaiting
Layer 2), [[013]] (no SME-gate on this PoC's progress — these stay pending-review, not
blocked-on-approval), [[015]] (the sibling Bucket B decision — the final-URLA groups that
do **not** have this fixture gap), [[016]] (the sibling Bucket C decision).
