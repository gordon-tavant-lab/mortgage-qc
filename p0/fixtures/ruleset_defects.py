"""
Builds the "known defects" verification ruleset -- checks wired against the
field_catalog.json fields extract_pdf.py pulls from the 5 synthetic loans in
demo/syn/, targeted at the 25 known <!-- DEFECT --> ground-truth conditions
in p0/fixtures/from_docs/defect_manifest.json.

This is a SEPARATE ruleset from ruleset_demo.py's demo_ruleset() -- that one
targets the original 7-field seed catalog and its exact content is pinned in
p0/harness.py's zero-regression digest (used by prove.py, run_demo.py,
eval_synth/generator.py). This file must never be imported by anything that
digest depends on.

Buckets A-E below use check-kinds the engine already implemented before this
task (predicate [003a], ratio_threshold [003b], agree_categorical /
agree_numeric [003c reconcile]); Bucket F (below) uses the two new kinds
003d added (agree_doc_categorical / agree_doc_numeric). All 25 known defects
are now wired (as 26 Check objects -- one manifest entry, USDA PITI/DTI,
names two independently checkable ratio fields):
  - 13 "missing" defects  -> kind=predicate, predicate=is_true
  -  4 single-field "threshold_breach" defects -> kind=ratio_threshold,
     ratio=field_value (5 Check objects: appraisal_comp_distance_miles,
     mortgage_late_payment_count_12mo, household_income_usda, piti_ratio,
     dti_ratio)
  -  2 date-diff "threshold_breach"/"stale" defects -> also ratio_threshold,
     ratio=field_value, against a field build_fixtures.py now derives
     (appraisal_staleness_days, nov_days_after_closing) since neither
     check-kind natively diffs two date fields
  -  1 doc-vs-system "mismatch" defect (fha_case_number_1003 vs its own
     sources.mismo) -> kind=agree_categorical, the EXISTING doc-vs-system
     reconcile path (not a new kind at all -- the field already carries a
     mismo source slot). Its verdict is FLAG, not FAIL: engine.py's own
     RECONCILE-phase design treats doc-vs-system disagreement as
     informational (the closing doc is truth; QC runs against it regardless
     of whether the lender's system has caught up) -- correct existing
     behavior, not a gap this task needs to change.

Bucket F (5 checks, added 2026-07-23 -- spec 003d): the remaining 5 known
defects (employment_start_date_1003/_voe, title_vesting_1003/_commitment,
liability_disclosed_on_1003/liability_amount_credit_report, loan_purpose_1003/
_cd, cd_payoff_amount/payoff_statement_amount) are genuine DOC-vs-DOC
comparisons -- two independently-extracted document fields, neither a system
source. 003c's own FR-005 explicitly declined to build this (forcing a second
document value into agree_categorical's sources{} slot would defeat 001b's
source-independence guard); 003d built the real fix instead: two new,
separate check kinds, agree_doc_categorical/agree_doc_numeric, that never
touch sources{} at all. QC phase (a doc-vs-doc mismatch is a genuine defect
in the closing package itself, not "system out of sync") -- resolves FAIL,
not the informational FLAG agree_categorical produces on doc-vs-system
disagreement. See p0/qc_engine/engine.py's _eval_check and
specs/003d-engine-doc-vs-doc-reconcile-checks/ for the full design.

Bucket E (6 checks, added 2026-07-23 -- NOT tied to any of the 25 known
defects, a direct extension of doc-vs-system reconciliation coverage): every
OTHER field across the 5 loans that carries BOTH a doc (PDF) value AND a
sources.mismo value -- confirmed by direct inspection of all 5 fixtures, not
assumed. Bucket D above already proved the doc-vs-MISMO reconcile path works
(fha_case_number_1003, loan 02); this bucket applies the same proven kind to
the rest: borrower_name, borrower_ssn, loan_amount, note_rate,
property_address, property_value. Universal fields present across every
program (not gated) -- a loan missing either side's value for a given field
self-gates to NOT_APPLICABLE/NEEDS_REVIEW via engine.py's own existing
agree_categorical/agree_numeric logic, same as Bucket D.

Normalizer/tolerance choices are NOT invented -- each is grounded in the
real doc-vs-mismo value pairs observed across all 5 loans before writing
these checks (2026-07-22 hallucination-prevention discipline: a normalizer
choice is itself a rule-authoring decision and must trace to evidence, not
a plausible-sounding guess):
  - borrower_name -> normalizer="name" (qc_engine/reconcile.py's norm_name,
    already implemented/tested): every one of the 5 loans shows the doc side
    carrying a middle initial the mismo side drops (e.g. "John A. Smith" vs
    "John Smith") -- confirmed this is name-formatting noise, not a real
    discrepancy signal, and norm_name's existing "drop single-letter middle
    initials" rule is designed for exactly this case.
  - property_address -> normalizer="address" (existing norm_address):
    loan 01 is the only one with both sides populated today and they match
    verbatim once normalized; ready for the other 4 loans if/when MISMO
    extraction adds this field for them.
  - borrower_ssn -> normalizer="ssn_last4" (existing norm_ssn_last4): SSNs in
    this dataset are masked to last-4 already (e.g. "xxx-xx-1234"); comparing
    on the last-4 slice is the correct, already-implemented primitive for
    that shape, not a new one invented for this task.
  - loan_amount / note_rate / property_value -> kind=agree_numeric,
    tolerance="0": confirmed empirically (M.within_tolerance) that a "0"
    tolerance correctly treats "6.750" and "6.75" as equal (pure formatting,
    Decimal-normalized) while still catching the two GENUINE dollar
    discrepancies this bucket found on first run -- loan 02's loan_amount
    ($278,375.00 doc vs $275,025.00 mismo, a real $3,350 gap) and loan 05's
    ($248,400.00 doc vs $245,940.00 mismo, a real $2,460 gap). Both are new,
    real findings this extension surfaces -- not previously checked.

Python 3.9 compatible.
"""
from __future__ import annotations

from qc_engine.model import CanonicalLoan
from qc_engine.ruleset import Check, Ruleset


def defects_ruleset() -> Ruleset:
    """The unfiltered universe: all 21 Check objects, unconditionally. Used
    for referential-integrity validation against the catalog (every
    field_name this ruleset could ever reference must resolve). Real
    evaluation should go through defects_ruleset_for(loan) below -- running
    THIS ruleset directly against a loan produces false FAILs for checks that
    don't apply to that loan's program/situation (see module docstring below
    the checks list for why each of the 13 predicate checks needs a gate)."""
    checks = [
        # --- Bucket A: "missing" defects, kind=predicate (13) ---------------
        Check(id="chk-def-large-deposit", name="Large deposit source documented",
              field_name="large_deposit_source_documented", kind="predicate",
              predicate="is_true", severity="CRITICAL", sources=["doc"],
              message_fail="Large unexplained deposit lacks source documentation."),
        Check(id="chk-def-hud92900a-signed", name="HUD-92900-A Section III certification signed",
              field_name="hud92900a_certification_signed", kind="predicate",
              predicate="is_true", severity="CRITICAL", sources=["doc"],
              message_fail="HUD-92900-A Section III Borrower Certification is unsigned."),
        Check(id="chk-def-gift-funds-documented", name="Gift funds source documented",
              field_name="gift_funds_source_documented", kind="predicate",
              predicate="is_true", severity="CRITICAL", sources=["doc"],
              message_fail="Gift funds paper trail (donor statement, transfer evidence) not in file."),
        Check(id="chk-def-lead-paint-cert", name="Lead-paint completion certification present",
              field_name="lead_paint_completion_cert_present", kind="predicate",
              predicate="is_true", severity="CRITICAL", sources=["doc"],
              message_fail="Peeling paint flagged on pre-1978 structure but no Form 442 completion cert in file."),
        Check(id="chk-def-fha-amendatory-clause", name="FHA Amendatory Clause present",
              field_name="fha_amendatory_clause_present", kind="predicate",
              predicate="is_true", severity="CRITICAL", sources=["doc"],
              message_fail="FHA Amendatory Clause / Real Estate Certification not in file."),
        Check(id="chk-def-arm-preloan-disclosure", name="ARM Pre-Loan Disclosure present",
              field_name="arm_preloan_disclosure_present", kind="predicate",
              predicate="is_true", severity="CRITICAL", sources=["doc"],
              message_fail="ARM Pre-Loan Disclosure missing."),
        Check(id="chk-def-termite-inspection", name="Termite inspection present",
              field_name="termite_inspection_present", kind="predicate",
              predicate="is_true", severity="CRITICAL", sources=["doc"],
              message_fail="Required termite inspection not in file."),
        Check(id="chk-def-lead-paint-disclosure", name="Lead-based paint disclosure present",
              field_name="lead_paint_disclosure_present", kind="predicate",
              predicate="is_true", severity="CRITICAL", sources=["doc"],
              message_fail="Pre-1978 property: Lead-Based Paint disclosure not in file."),
        Check(id="chk-def-va-residual-income", name="VA residual income documented",
              field_name="va_residual_income_documented", kind="predicate",
              predicate="is_true", severity="CRITICAL", sources=["doc"],
              message_fail="VA residual income calculation not documented for the borrower's family size/region."),
        Check(id="chk-def-self-employed-pl-bs", name="Self-employed P&L / balance sheet present",
              field_name="self_employed_pl_balance_sheet_present", kind="predicate",
              predicate="is_true", severity="CRITICAL", sources=["doc"],
              message_fail="YTD P&L and Balance Sheet not in file for self-employed borrower."),
        Check(id="chk-def-usda-property-eligibility", name="USDA property eligibility documented",
              field_name="usda_property_eligibility_documented", kind="predicate",
              predicate="is_true", severity="CRITICAL", sources=["doc"],
              message_fail="USDA property eligibility screen-print / determination not in file."),
        Check(id="chk-def-well-septic-test", name="Well & septic test documented",
              field_name="well_septic_test_documented", kind="predicate",
              predicate="is_true", severity="CRITICAL", sources=["doc"],
              message_fail="Private well/septic: RD-required water test + septic evaluation not in file."),
        Check(id="chk-def-site-value-justification", name="Site value justification documented",
              field_name="site_value_justification_documented", kind="predicate",
              predicate="is_true", severity="CRITICAL", sources=["doc"],
              message_fail="Borderline site value ratio: USDA site value analysis not documented."),

        # --- Bucket B: single-field threshold breaches (5) ------------------
        Check(id="chk-def-appraisal-comp-distance", name="Appraisal comp distance within guideline",
              field_name="appraisal_comp_distance_miles", kind="ratio_threshold",
              ratio="field_value", operator="<=", threshold="5",
              severity="CRITICAL",
              message_fail="Comparable sale distance exceeds the 5-mile urban guideline with no addenda explanation."),
        Check(id="chk-def-mortgage-late-payments", name="No 30+ day mortgage lates in trailing 12mo",
              field_name="mortgage_late_payment_count_12mo", kind="ratio_threshold",
              ratio="field_value", operator="<=", threshold="0",
              severity="CRITICAL",
              message_fail="Program requires 0x30 in the trailing 12 months; a late payment was reported."),
        Check(id="chk-def-usda-household-income", name="USDA household income within moderate-income limit",
              field_name="household_income_usda", kind="ratio_threshold",
              ratio="field_value", operator="<=", threshold="130850.00",
              severity="CRITICAL",
              message_fail="Household income exceeds the USDA moderate-income limit for this area."),
        Check(id="chk-def-usda-piti-ratio", name="USDA PITI ratio within guideline",
              field_name="piti_ratio", kind="ratio_threshold",
              ratio="field_value", operator="<=", threshold="29.0",
              severity="CRITICAL",
              message_fail="PITI ratio exceeds 29% with no waiver/compensating-factors documentation on file."),
        Check(id="chk-def-usda-dti-ratio", name="USDA total debt ratio within guideline",
              field_name="dti_ratio", kind="ratio_threshold",
              ratio="field_value", operator="<=", threshold="41.0",
              severity="CRITICAL",
              message_fail="Total debt ratio exceeds 41% with no waiver/compensating-factors documentation on file."),

        # --- Bucket C: derived date-diff threshold breaches (2) -------------
        Check(id="chk-def-appraisal-staleness", name="Appraisal not stale at closing",
              field_name="appraisal_staleness_days", kind="ratio_threshold",
              ratio="field_value", operator="<=", threshold="120",
              severity="CRITICAL",
              message_fail="Appraisal effective date exceeds the 120-day recertification limit as of closing."),
        Check(id="chk-def-nov-date-order", name="VA NOV issued on or before closing",
              field_name="nov_days_after_closing", kind="ratio_threshold",
              ratio="field_value", operator="<=", threshold="0",
              severity="CRITICAL",
              message_fail="VA Notice of Value is dated after the closing date -- invalid date order."),

        # --- Bucket D: doc-vs-system mismatch (1) ---------------------------
        Check(id="chk-def-fha-case-number", name="FHA case number (1003) agrees with FHAC",
              field_name="fha_case_number_1003", kind="agree_categorical",
              severity="CRITICAL", sources=["doc", "mismo"], normalizer="identity",
              message_fail="FHA case number on the 1003 does not match the FHA Connection case number."),

        # --- Bucket E: doc-vs-system reconciliation, universal fields (6) ---
        # Not tied to any of the 25 known defects -- extends the proven
        # Bucket D reconcile path to every other field with both a doc and
        # mismo value across the 5 loans (see module docstring for the
        # evidence behind each normalizer/tolerance choice).
        Check(id="chk-reconcile-borrower-name", name="Borrower name agrees with system of record",
              field_name="borrower_name", kind="agree_categorical",
              severity="INFO", sources=["doc", "mismo"], normalizer="name",
              message_fail="Borrower name on the closing documents does not match the system of record "
                            "(beyond an acceptable middle-initial variation)."),
        Check(id="chk-reconcile-borrower-ssn", name="Borrower SSN agrees with system of record",
              field_name="borrower_ssn", kind="agree_categorical",
              severity="INFO", sources=["doc", "mismo"], normalizer="ssn_last4",
              message_fail="Borrower SSN (last 4) on the closing documents does not match the system of record."),
        Check(id="chk-reconcile-property-address", name="Property address agrees with system of record",
              field_name="property_address", kind="agree_categorical",
              severity="INFO", sources=["doc", "mismo"], normalizer="address",
              message_fail="Subject property address on the closing documents does not match the system of record."),
        Check(id="chk-reconcile-loan-amount", name="Loan amount agrees with system of record",
              field_name="loan_amount", kind="agree_numeric",
              severity="INFO", sources=["doc", "mismo"], tolerance="0",
              message_fail="Loan amount on the closing documents does not match the system of record."),
        Check(id="chk-reconcile-note-rate", name="Note rate agrees with system of record",
              field_name="note_rate", kind="agree_numeric",
              severity="INFO", sources=["doc", "mismo"], tolerance="0",
              message_fail="Note rate on the closing documents does not match the system of record."),
        Check(id="chk-reconcile-property-value", name="Property value agrees with system of record",
              field_name="property_value", kind="agree_numeric",
              severity="INFO", sources=["doc", "mismo"], tolerance="0",
              message_fail="Property value on the closing documents does not match the system of record."),

        # --- Bucket F: doc-vs-doc mismatches (5) -- spec 003d ----------------
        # The 5 known defects agree_categorical/agree_numeric structurally
        # could not reach (neither field has a system source -- see module
        # docstring). QC phase, CRITICAL severity: a genuine mismatch here is
        # a real defect in the closing package, not an informational FLAG.
        Check(id="chk-def-employment-dates-agree", name="Employment start date agrees across documents",
              field_name="employment_start_date_1003", compare_field_name="employment_start_date_voe",
              kind="agree_doc_categorical", severity="CRITICAL", sources=["doc"], normalizer="identity",
              message_fail="Employment start date on the final 1003 does not match the VOE/paystub."),
        Check(id="chk-def-title-vesting-agree", name="Title vesting agrees between 1003 and title commitment",
              field_name="title_vesting_1003", compare_field_name="title_vesting_commitment",
              kind="agree_doc_categorical", severity="CRITICAL", sources=["doc"], normalizer="identity",
              message_fail="Manner in which title is held on the 1003 does not match the title commitment."),
        Check(id="chk-def-loan-purpose-agree", name="Loan purpose agrees between 1003 and closing disclosure",
              field_name="loan_purpose_1003", compare_field_name="loan_purpose_cd",
              kind="agree_doc_categorical", severity="CRITICAL", sources=["doc"], normalizer="identity",
              message_fail="Loan purpose selected on the final 1003 does not match the closing disclosure."),
        Check(id="chk-def-liability-disclosed-agree", name="Credit report liability disclosed on 1003",
              field_name="liability_disclosed_on_1003", compare_field_name="liability_amount_credit_report",
              kind="agree_doc_numeric", severity="CRITICAL", sources=["doc"], tolerance="0",
              message_fail="A liability appearing on the credit report is not disclosed on the final 1003."),
        Check(id="chk-def-cd-payoff-agree", name="CD payoff amount agrees with payoff statement",
              field_name="cd_payoff_amount", compare_field_name="payoff_statement_amount",
              kind="agree_doc_numeric", severity="CRITICAL", sources=["doc"], tolerance="0",
              message_fail="Closing Disclosure payoff amount does not match the payoff statement, with no reconciliation."),
    ]
    return Ruleset(ruleset_id="rs-defect-verification", version=1, checks=checks)


# --- Applicability gating (each of the 13 predicate checks only means
# something for a subset of loans) -------------------------------------------
#
# predicate's is_true correctly FAILs on a None (genuinely-absent) truth
# value -- that's the whole point of the MISSING archetype: a required
# document that isn't in the file must fail, not silently pass. But
# defects_ruleset()'s 13 predicate checks run unconditionally against every
# loan, and 4 of 5 loans simply don't have most of these document types at
# all -- not because the document is missing-and-should-fail, but because
# the check doesn't apply to that loan's program or situation. Confirmed
# empirically: running defects_ruleset() as-is against loan 01 (Conventional)
# shows FAIL on "HUD-92900-A signed," "USDA property eligibility documented,"
# etc. -- checks for programs it isn't. Three DIFFERENT gates are needed,
# because the 13 checks are not homogeneous:
#
# 1. DOCUMENT-PRESENCE gate (7 checks) -- the check is a borrower/transaction
#    condition (self-employment, a gift, an unexplained deposit, a
#    program-specific inspection), not tied to loan PROGRAM per se. Gating by
#    loan_type would be wrong here: a real self-employed VA borrower needs
#    the same P&L/balance-sheet check a self-employed Freddie-refi borrower
#    does -- it's a coincidence of this 5-loan set that self-employment only
#    appears on loan 04. The real precondition is "does this loan's package
#    include the specific supporting document the check is about" --
#    computed once, at build time, from the loan folder's own filenames
#    (build_fixtures.py's _derive_document_presence_facts), landing in
#    facts{} as doc_present_<x> (not fields{} -- this is routing metadata,
#    never itself a Check target, so it doesn't need catalog governance or a
#    citation).
#
# 2. PROPERTY-AGE gate (2 checks) -- lead-paint federal requirements trigger
#    on the property's construction year, not the loan program. Gates IN
#    (check applies) whenever year_built_appraisal is unknown (None) OR
#    < 1978 -- i.e. it only gates OUT when we affirmatively KNOW the
#    property is not pre-1978. Deliberately conservative: absence of
#    contrary evidence should never silently clear a compliance check.
#
# 3. PROGRAM gate (4 checks) -- for these, no PDF exists anywhere in ANY of
#    the 5 loans (defect_manifest.json's own "note" field says so for each --
#    MISMO's InFileIndicator=false is the only record). Document-presence
#    gating can't work here (it would never resolve true, even for the
#    defect's own loan), so these fall back to the loan's declared program.
#    arm_preloan_disclosure_present is conceptually ARM-rate-specific, not
#    VA-specific -- gated to VA here only because that's this dataset's one
#    ARM case and no rate-type field exists to gate on more precisely; a
#    real second ARM loan on a different program would need this revisited.

_DOC_PRESENCE_GATED = {
    "chk-def-large-deposit": "doc_present_bank_statement",
    "chk-def-hud92900a-signed": "doc_present_hud92900a",
    "chk-def-gift-funds-documented": "doc_present_gift_letter",
    "chk-def-termite-inspection": "doc_present_va_appraisal",
    "chk-def-self-employed-pl-bs": "doc_present_self_employed_income",
    "chk-def-well-septic-test": "doc_present_usda_appraisal",
    "chk-def-usda-property-eligibility": "doc_present_usda_property_eligibility",
}

_PROPERTY_AGE_GATED = {
    "chk-def-lead-paint-cert",
    "chk-def-lead-paint-disclosure",
}
_PRE_1978_CUTOFF_YEAR = 1978

_PROGRAM_GATED = {
    "chk-def-fha-amendatory-clause": "FHA Purchase",
    "chk-def-arm-preloan-disclosure": "VA Purchase",
    "chk-def-va-residual-income": "VA Purchase",
    "chk-def-site-value-justification": "USDA RHS 502 Guaranteed",
}


def _check_applies(chk: Check, loan: CanonicalLoan) -> bool:
    if chk.id in _DOC_PRESENCE_GATED:
        return loan.facts.get(_DOC_PRESENCE_GATED[chk.id]) == "true"
    if chk.id in _PROPERTY_AGE_GATED:
        year_built = loan.get("year_built_appraisal").doc
        if year_built is None:
            return True  # unknown -- conservative default, don't silently clear
        return int(year_built) < _PRE_1978_CUTOFF_YEAR
    if chk.id in _PROGRAM_GATED:
        return loan.loan_type == _PROGRAM_GATED[chk.id]
    return True  # buckets B/C/D/E/F already self-gate via NOT_APPLICABLE in engine.py


def defects_ruleset_for(loan: CanonicalLoan) -> Ruleset:
    """The real evaluation entrypoint: defects_ruleset()'s 21 checks, filtered
    to the subset that actually applies to this specific loan (see the
    applicability-gating comment above). Each loan effectively gets its own
    Route -- exactly this product's own "point a route at a target set of
    checks" model (CLAUDE.md), just computed here instead of hand-wired."""
    universe = defects_ruleset()
    applicable = [c for c in universe.checks if _check_applies(c, loan)]
    return Ruleset(ruleset_id=universe.ruleset_id, version=universe.version,
                   checks=applicable)
