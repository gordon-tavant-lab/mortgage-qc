"""
Touchless loan payload -> qc_engine fixture JSON (the shape
`p0/fixtures/from_docs/fixture_loader.py::load_canonical_loan()` reads).

Bake-off counterpart to `src/shacl_pilot/touchless_adapter.py` (Pipeline A's
adapter for the same input). Field-for-field mirrors that adapter's coverage
so both engines see identical input data from `demo/touchless/extracted/` --
that symmetry is the fairness requirement for the p0-vs-src bake-off
(see the plan at `/Users/gordonchan/.claude/plans/1-no-no-this-iridescent-brooks.md`).

Adds six applicability-gating fields (`Loans.QC_Policy` etc.) the gold
ruleset's `applicability.all_of`/`any_of` conditions read, which the SHACL
adapter has no equivalent of (that pipeline gates applicability outside the
adapter, in `run_full_ruleset_audit.py`'s Python layer).

`QC_Policy` is set to the literal "Fannie Mae" rather than left unknown: the
Touchless payload's `investor` field is null for this loan, but the gold
ruleset itself is scoped to Fannie Mae conventional only (the SME would only
ever assign this ruleset's route to a loan already known to be on that
program) -- this is a documented experiment assumption, not a guess made to
force checks to fire. `Underwriting_Type` is left genuinely unknown (the
payload's `duStatus`/`underwriting`/`lpaApproved` are all null) so
`applies_if` resolves it as `NEEDS_REVIEW` (APPLICABILITY_UNKNOWN), never a
silent guess -- matching this project's "never gate on a null field"
discipline.

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any, Dict, Optional

_PO_BOX_RE = re.compile(r"\bP\.?\s*O\.?\s*Box\b|\bPost\s+Office\s+Box\b", re.I)


def _ts_to_date(ts_ms: Optional[float]) -> Optional[str]:
    if not ts_ms:
        return None
    return datetime.fromtimestamp(ts_ms / 1000).strftime("%Y-%m-%d")


def _citation(source: str, confidence: Optional[float] = None) -> Dict[str, Any]:
    """Mirrors src/shacl_pilot/touchless_adapter.py::cite_touchless() --
    same honesty limits: this payload carries no PDF, no page, no bounding
    box (`documentLocation` is null throughout), so the citation is a
    JSON-path breadcrumb into the Touchless payload itself, not a real
    document/page. Never claim a page number that doesn't exist."""
    snippet = f"Touchless extraction: {source}"
    if confidence is not None:
        snippet += f" (confidence: {confidence})"
    return {
        "doc_name": "Touchless API",
        "page_num": 0,
        "segment_snippet": snippet[:200],
    }


def _field(value: Any, citation_source: str, confidence: Optional[float] = None) -> Dict[str, Any]:
    return {"truth": value, "sources": {}, "citation": _citation(citation_source, confidence)}


def adapt_touchless_to_fixture(loan_app_path: str, extracted_data_path: str) -> Dict[str, Any]:
    with open(loan_app_path, "r", encoding="utf-8") as f:
        loan_app = json.load(f)
    with open(extracted_data_path, "r", encoding="utf-8") as f:
        extracted_data = json.load(f)

    fields: Dict[str, Any] = {}
    facts: Dict[str, Any] = {}

    loan_summary = loan_app.get("loanSummary", {}) or {}
    loan_terms = loan_summary.get("loanTerms", {}) or {}
    loan_id = loan_summary.get("lenderCaseIdentifier") or loan_app.get("loanId") or "UNKNOWN"

    # --- loan terms ---------------------------------------------------
    if loan_terms.get("loanPurposeType"):
        fields["loan_purpose_1003"] = _field(loan_terms["loanPurposeType"], "loanTerms.loanPurposeType")
        # Loans.LoanPurposeType condition values are title-cased ("Purchase");
        # the payload's are upper-cased ("PURCHASE") -- normalize for the
        # applies_if gate, keep the raw value for the display field above.
        fields["Loans.LoanPurposeType"] = _field(
            str(loan_terms["loanPurposeType"]).title(), "loanTerms.loanPurposeType (normalized)")

    if loan_terms.get("mortgageType"):
        fields["loan_program_1003"] = _field(loan_terms["mortgageType"], "loanTerms.mortgageType")
        fields["mismo_mortgage_type"] = _field(loan_terms["mortgageType"], "loanTerms.mortgageType")
        fields["Loans.LoanType"] = _field(
            str(loan_terms["mortgageType"]).title(), "loanTerms.mortgageType (normalized)")

    if loan_terms.get("baseLoanAmount"):
        fields["mismo_loan_amount"] = _field(float(loan_terms["baseLoanAmount"]), "loanTerms.baseLoanAmount")

    if loan_terms.get("interestRate"):
        fields["mismo_note_rate"] = _field(float(loan_terms["interestRate"]), "loanTerms.interestRate")

    app_date_ts = loan_summary.get("applicationDate")
    if app_date_ts:
        fields["application_date"] = _field(_ts_to_date(app_date_ts), "loanSummary.applicationDate")

    # --- qualification / ratios ----------------------------------------
    qual = loan_summary.get("qualification", {}) or {}
    if qual.get("totalMonthlyIncomeAmount"):
        fields["mismo_total_monthly_income"] = _field(
            float(qual["totalMonthlyIncomeAmount"]), "qualification.totalMonthlyIncomeAmount")
    if qual.get("housingExpenseRatioPercent"):
        fields["housing_ratio"] = _field(
            float(qual["housingExpenseRatioPercent"]), "qualification.housingExpenseRatioPercent")
    if qual.get("totalDebtExpenseRatioPercent"):
        fields["dti_ratio"] = _field(
            float(qual["totalDebtExpenseRatioPercent"]), "qualification.totalDebtExpenseRatioPercent")

    ltv_ratio = loan_summary.get("ltvRatio", {}) or {}
    if ltv_ratio.get("ltv"):
        fields["ltv"] = _field(float(ltv_ratio["ltv"]), "ltvRatio.ltv")

    if loan_summary.get("fico"):
        fields["credit_score_1003"] = _field(str(int(loan_summary["fico"])), "loanSummary.fico")

    # --- borrower / employment ------------------------------------------
    borrower_pairs = (loan_app.get("borrowersDetail", {}) or {}).get("borrowerPairs", []) or []
    if borrower_pairs:
        borrowers_list = borrower_pairs[0].get("borrowers", []) or []
        if borrowers_list:
            borrower = borrowers_list[0]
            name_parts = [borrower.get(k) for k in ("firstName", "middleName", "lastName") if borrower.get(k)]
            if name_parts:
                fields["borrower_name"] = _field(" ".join(name_parts), "borrowersDetail.borrowerPairs[0].borrowers[0]")

            employers = borrower.get("employers", []) or []
            if employers:
                emp = employers[0]
                if emp.get("employerName"):
                    fields["employer_name_1003"] = _field(emp["employerName"], "employers[0].employerName")

                employment = emp.get("employment", {}) or {}
                if employment.get("employmentStartDate"):
                    fields["employment_start_date_1003"] = _field(
                        _ts_to_date(employment["employmentStartDate"]),
                        "employers[0].employment.employmentStartDate")

                income_list = emp.get("income", []) or []
                if income_list and income_list[0].get("monthlyIncome"):
                    fields["base_monthly_income_1003"] = _field(
                        float(income_list[0]["monthlyIncome"]), "employers[0].income[0].monthlyIncome")

                # borrower_self_employed must be detected across ALL employer
                # records, not just employers[0] -- a borrower can hold a W-2
                # job at employers[0] while self-employed elsewhere. Loan
                # 12607601215 exposed this: employers[0] (Kraft Foods,
                # isSelfEmployed=False) happened to carry a stale
                # ownershipInterestType value that incidentally tripped the
                # "25Percent" check, while the 4 real self-employed employers
                # (employers[1:4], each isSelfEmployed=True) were never read.
                for se_emp in employers:
                    se_employment = se_emp.get("employment", {}) or {}
                    se_ownership = se_employment.get("ownershipInterestType", "") or ""
                    if se_employment.get("isSelfEmployed") or "25Percent" in se_ownership:
                        facts["borrower_self_employed"] = True
                        break

                # 2026-08-01: PC::O-EPD-14457/O-EPD-52921 ("A PO Box is the
                # only address listed for an employer") -- curated wiring,
                # see NEEDS-REVIEW-REMEDIATION-RESEARCH-2026-08-01.md. Regex
                # heuristic, not a CASS-certified address validation (the
                # research-recommended approach is a USPS CASS DPV "PB"
                # footnote or a commercial address-validation API's
                # record_type field) -- acceptable for a single street-line
                # string field with no vendor integration, but a real false-
                # negative risk on unusual PO Box phrasing exists and should
                # be re-evaluated if this check starts mattering at scale.
                # A predicate Check (is_true) is resolved via
                # CanonicalLoan.get() -> self.fields, NOT self.facts (facts
                # is only read by the ltv/dti ratio_threshold path) -- must
                # go in `fields`, using the same _field() wrapper as every
                # other doc-sourced field, or engine.py sees an unresolved
                # SourceValue() and reports "No data present" regardless of
                # what's in `facts`. Only set when at least one employer has
                # address data -- absent correctly resolves NEEDS_REVIEW/
                # APPLICABILITY_UNKNOWN downstream, never a silent PASS
                # guess. True = compliant (no PO-box-only employer address
                # found); False = the defect condition itself.
                employer_addrs = [
                    (i, (e.get("employerAddress", {}) or {}).get("address"))
                    for i, e in enumerate(employers)
                ]
                employer_addrs = [(i, a) for i, a in employer_addrs if a]
                if employer_addrs:
                    po_box_hit = next((i for i, a in employer_addrs if _PO_BOX_RE.search(a)), None)
                    fields["employer_address_not_po_box_only"] = _field(
                        po_box_hit is None,
                        "employers[%s].employerAddress.address" % (
                            po_box_hit if po_box_hit is not None else
                            "/".join(str(i) for i, _ in employer_addrs)))

    # --- property / collateral ------------------------------------------
    collateral = (loan_app.get("collateralDetail", {}) or {}).get("collateral", []) or []
    if collateral:
        prop = collateral[0]
        prop_detail = prop.get("propertyDetail", {}) or {}
        addr = prop_detail.get("propertyAddress", {}) or {}

        if addr.get("stateCode"):
            fields["property_state"] = _field(addr["stateCode"], "propertyDetail.propertyAddress.stateCode")
            fields["Loans.AddressState"] = _field(addr["stateCode"], "propertyDetail.propertyAddress.stateCode")

        if prop_detail.get("attachmentType"):
            # Not a direct match to gold's PropertyType vocabulary (Condo/PUD/
            # Co-op/2-4 unit) -- "Detached"/"Attached" describes a different
            # axis (single-family structure type). Carried through honestly;
            # PropertyType-gated cards correctly resolve NOT_APPLICABLE for a
            # loan whose only signal is "Detached", rather than a guess.
            fields["Loans.PropertyType"] = _field(
                prop_detail["attachmentType"], "propertyDetail.attachmentType")

        appraisal = prop.get("appraisal", {}) or {}
        if appraisal.get("appraisedValue"):
            fields["appraised_value"] = _field(float(appraisal["appraisedValue"]), "appraisal.appraisedValue")
        if appraisal.get("appraisalEffectiveDate"):
            fields["appraisal_effective_date"] = _field(
                _ts_to_date(appraisal["appraisalEffectiveDate"]), "appraisal.appraisalEffectiveDate")

        # --- 2026-08-02: 3 scripted_review pre-wires, curated allowlist ----
        # (CURATED_SCRIPTED_REVIEW_FIELDS below). Each field can ONLY ever
        # assert True (confirmed no-defect) or leave the field unset (stays
        # NEEDS_REVIEW) -- never False. A confident False here would risk a
        # false FAIL: e.g. zoning "not Legal" doesn't itself prove the
        # defect (O-FNM-54534's real question is whether the appraiser
        # explained rebuild-ability, which we can't read); a comp value
        # outside the min/max range doesn't itself prove O-FNM-50297's
        # defect either (an adequate appraiser explanation would clear it).
        # UNTESTED against real non-null data -- every input below is null
        # for this loan, so only the null-safe fallback path is exercised
        # today. Verify against the first future loan where these populate.
        vr = ((loan_app.get("collateralDetail", {}) or {}).get("collateralService", {}) or {}
              ).get("valuationServices", [{}])
        vr = (vr[0] if vr else {}).get("valuationReport", {}) or {}
        comps = vr.get("comparables") or []
        comp_prices = [c.get("salePrice") for c in comps if isinstance(c, dict) and c.get("salePrice")]
        if comp_prices and appraisal.get("appraisedValue"):
            av = float(appraisal["appraisedValue"])
            if min(comp_prices) <= av <= max(comp_prices):
                fields["appraised_value_within_comp_range"] = _field(
                    True, "appraisal.appraisedValue within min/max of "
                          "valuationReport.comparables[].salePrice (%d comps)" % len(comp_prices))
            # else: outside range -- leave unset, stays NEEDS_REVIEW. An
            # out-of-range value doesn't itself prove O-FNM-50297's defect
            # (the rule's own text allows an adequate appraiser explanation
            # to clear it, which we can't read).

        zoning = prop_detail.get("siteZoningComplianceType")
        if zoning == "Legal":
            fields["zoning_legal_or_unknown"] = _field(
                True, "propertyDetail.siteZoningComplianceType == 'Legal'")
        # else (None or any non-Legal value): leave unset -- a confirmed
        # non-Legal zoning doesn't itself prove O-FNM-54534's defect (still
        # need to know whether the appraiser addressed rebuild-ability).

        credit_records = ((loan_app.get("creditDetail", {}) or {}).get("creditService", {}) or {}
                          ).get("creditResponse", {}) or {}
        pub_records = credit_records.get("creditPublicRecords")
        if pub_records is not None and isinstance(pub_records, list) and len(pub_records) == 0:
            fields["no_adverse_credit_public_records"] = _field(
                True, "creditDetail.creditService.creditResponse.creditPublicRecords == [] "
                      "(present, explicitly empty)")
        # else (None, or a non-empty list whose record-type shape is
        # unverified against any real example): leave unset. A non-empty
        # list isn't auto-flagged either -- O-EPD-52936 stays NEEDS_REVIEW
        # so a human judges materiality, same discipline as this session's
        # other CONFIRMED_RED_FLAG findings (never auto-escalate to FAIL).

        if prop_detail.get("yearBuilt"):
            fields["property_year_built"] = _field(str(prop_detail["yearBuilt"]), "propertyDetail.yearBuilt")

    # --- extracted document data (Schedule C) ---------------------------
    extracted_by_field: Dict[str, Dict[str, Any]] = {}
    for item in extracted_data:
        name, value, confidence = item.get("name"), item.get("value"), item.get("confidence")
        if name and value:
            extracted_by_field[name] = {"value": value, "confidence": confidence}

    if "Tax_Year" in extracted_by_field:
        fields["tax_year_schedule_c"] = _field(
            extracted_by_field["Tax_Year"]["value"], "Schedule C: Tax_Year",
            extracted_by_field["Tax_Year"]["confidence"])
    if "Gross_Profit" in extracted_by_field:
        fields["gross_profit_schedule_c"] = _field(
            float(extracted_by_field["Gross_Profit"]["value"]), "Schedule C: Gross_Profit",
            extracted_by_field["Gross_Profit"]["confidence"])
    if "Net_Profit" in extracted_by_field:
        fields["net_profit_schedule_c"] = _field(
            float(extracted_by_field["Net_Profit"]["value"]), "Schedule C: Net_Profit",
            extracted_by_field["Net_Profit"]["confidence"])

    # --- credit -----------------------------------------------------------
    credit = loan_app.get("creditDetail", {}) or {}
    credit_score_data = credit.get("creditScore", []) or []
    scores = [s.get("creditRepositorySourceScore") for s in credit_score_data if s.get("creditRepositorySourceScore")]
    if len(scores) >= 2:
        scores_sorted = sorted(int(s) for s in scores)
        middle_score = scores_sorted[len(scores_sorted) // 2]
        fields["credit_score_bureau"] = _field(str(middle_score), f"creditDetail.creditScore middle of {len(scores)} scores")

    # --- applicability-gating fields not covered above ------------------
    # QC_Policy: documented experiment assumption, see module docstring.
    fields["Loans.QC_Policy"] = _field("Fannie Mae", "experiment assumption: gold ruleset is FNM-conventional-only")
    # Underwriting_Type: genuinely unknown on this payload (duStatus/
    # underwriting/lpaApproved are all null). Gordon (2026-08-01, Category C
    # decision, superseding the earlier "stays NO_DATA pending a call"):
    # ASSUME DU-underwritten -- nearly all conventional FNMA loans are, and
    # the demo should not hold 10 checks hostage to one unpopulated vendor
    # field. This is a demo-scoped ASSUMED fact, not extracted data; the
    # AUS/DU-findings vendor question stays open in
    # output/TOUCHLESS-API-QUESTIONS-2026-07-30.md, and real data supersedes
    # this line the moment the payload carries it.
    fields["Loans.Underwriting_Type"] = _field(
        "Desktop Underwriter",
        "ASSUMED (demo-scoped, Gordon 2026-08-01): conventional FNMA loan "
        "presumed DU-underwritten; loanSummary.underwriting is null in payload")

    # --- curated document-presence fields (added 2026-07-31) ------------
    # Mirrors src/shacl_pilot/touchless_adapter.py's docs_present population
    # from the real documents[] inventory (62 entries, previously discarded
    # here too -- same finding, see output/BAKEOFF-P0-VS-SRC-GOLD-TOUCHLESS-
    # 2026-07-31.md). Only the 5 individually hand-verified matches in
    # p0/qc_engine/compiler/import_gold_ruleset.py's CURATED_DOC_MATCHES are
    # wired to a Check -- populate all 5 as real boolean-ish presence fields
    # here (`truth` = the real documentId when present, so is_present's
    # `sv.doc is not None` check resolves PASS; simply never set the field
    # for a document confirmed absent, so is_present's None-check correctly
    # resolves FAIL -- never set truth=False, since str(False) is a
    # non-empty string and would incorrectly resolve PASS under is_present's
    # actual semantics, engine.py line ~347).
    _CURATED_DOC_TYPES = {
        "doc_present_gift_letter": "Gift Letter",
        "doc_present_credit_report": "Credit Report",
        "doc_present_hazard_insurance": "Hazard Insurance",
        "doc_present_title_commitment": "Title Commitment",
        "doc_present_flood_hazard_determination": "Flood Hazard Determination",
        # added 2026-07-31 (NO_DATA root-cause pass; see import_gold_ruleset.py
        # CURATED_DOC_MATCHES comment for the verification trail):
        "doc_present_closing_protection_letter": "Closing Protection Letter",
        "doc_present_borrowers_authorization": "Borrowers Authorization",
        # added 2026-08-01 (context_flags gap -- see
        # output/BAKEOFF-P0-VS-SRC-GOLD-RULESET-2026-07-31.md Addendum 8):
        "doc_present_appraisal": "Form 1004 Uniform Residential Appraisal",
    }
    docs_by_type = {}
    for doc in loan_app.get("documents", []) or []:
        dtype = doc.get("documentType")
        if dtype:
            docs_by_type.setdefault(dtype, doc.get("documentId"))
    for field_name, doc_type in _CURATED_DOC_TYPES.items():
        if doc_type in docs_by_type:
            fields[field_name] = _field(
                docs_by_type[doc_type] or "present",
                "documents[] entry with documentType=%s" % doc_type)
        # else: deliberately not set -- is_present resolves FAIL, honestly.

    # --- context_flags gating fields (added 2026-08-01) -------------------
    # Traced end-to-end: the gold ruleset's applicability.context_flags is
    # completely unevaluated in p0 (zero handling, confirmed by grep before
    # this change) -- meaning EVERY context-flag-gated card silently falls
    # through to the structural all_of verdict alone (usually just
    # Loans.QC_Policy=="Fannie Mae", always true here), regardless of
    # whether the flag's condition actually holds for this loan. Caught a
    # live false PASS this way: PC::O-FNM-15420/O-FNM-54327 ("RefiNow DTI
    # ratio cap 65%") resolved a confident PASS on this loan even though
    # this loan is a PURCHASE (loanPurposeType), which can never be
    # RefiNow. 29 distinct context_flags exist ruleset-wide; only the ones
    # with a real, closed-world-derivable fact are wired here (mirrors
    # income_type_self_employment's existing src-side precedent, generalized
    # -- see import_gold_ruleset.py's CONTEXT_FLAG_APPLIES_IF_FIELD). Every
    # other flag stays unhandled -- same honest "not yet wired" floor as
    # every other not-yet-converted piece of this ruleset, not a guess.
    #
    # Closed-world doc-presence flags: docs_by_type is the FULL, closed-world
    # 62-entry inventory (see "closed-world document inventory" project
    # discipline) -- absence is real evidence of absence, so these are
    # always set True/False, never left unknown.
    fields["Loans.ContextFlag_appraisal_in_file"] = _field(
        "Form 1004 Uniform Residential Appraisal" in docs_by_type,
        "documents[] closed-world scan for documentType=Form 1004 Uniform Residential Appraisal")
    fields["Loans.ContextFlag_credit_report_presence_determined"] = _field(
        "Credit Report" in docs_by_type,
        "documents[] closed-world scan for documentType=Credit Report")

    # Loan-product-type flags: only set when genuinely determinable from
    # loanPurposeType -- a Purchase loan can never be any refinance subtype
    # (definitive False for all three refi flags), but a non-Purchase loan's
    # SPECIFIC refinance subtype (RefiNow vs. limited-cash-out vs. cash-out)
    # isn't derivable from loanPurposeType alone, so those stay unset
    # (unknown) rather than guessed for a non-purchase loan.
    purpose = (loan_terms.get("loanPurposeType") or "").strip().upper()
    if purpose == "PURCHASE":
        fields["Loans.ContextFlag_loan_product_purchase"] = _field(True, "loanTerms.loanPurposeType=PURCHASE")
        fields["Loans.ContextFlag_loan_product_refinow"] = _field(
            False, "loanTerms.loanPurposeType=PURCHASE (RefiNow is refinance-only)")
        fields["Loans.ContextFlag_loan_product_limited_cash_out_refinance"] = _field(
            False, "loanTerms.loanPurposeType=PURCHASE (LCO refi is refinance-only)")
        fields["Loans.ContextFlag_loan_product_cash_out_refinance"] = _field(
            False, "loanTerms.loanPurposeType=PURCHASE (cash-out refi is refinance-only)")
    elif purpose:
        fields["Loans.ContextFlag_loan_product_purchase"] = _field(
            False, "loanTerms.loanPurposeType=%s (not PURCHASE)" % purpose)
        # refi subtype flags deliberately left unset -- not derivable from
        # loanPurposeType alone for a non-purchase loan.

    # Rate-type flag: productName is free text but this payload's convention
    # is a plain "<program> Fixed"/"<program> ARM" string (verified against
    # the real value "Conventional Fixed" for this loan) -- only set when
    # one of those two literal words appears, never guessed otherwise.
    product_name = (loan_summary.get("loanProduct", {}) or {}).get("productName") or ""
    if "ARM" in product_name.upper().split():
        fields["Loans.ContextFlag_loan_product_arm"] = _field(True, "loanProduct.productName=%s" % product_name)
    elif "FIXED" in product_name.upper():
        fields["Loans.ContextFlag_loan_product_arm"] = _field(False, "loanProduct.productName=%s" % product_name)

    # Synthetic OR field for the one card (PC::O-FNM-15422) whose
    # context_flags combine all three refinance-subtype flags together --
    # p0's applies_if is AND-only (confirmed, see import_gold_ruleset.py's
    # module docstring), so a true multi-flag OR needs precomputing here
    # rather than in the applies_if DSL. Deliberately NOT derived as "not
    # purchase" -- loanPurposeType could in principle be something other
    # than Purchase/Refinance (e.g. Construction) that our schema knowledge
    # doesn't rule out, and "not purchase" would wrongly imply "is
    # refinance" in that case. Only set True when purpose is explicitly
    # refinance-shaped; False only for the confirmed-Purchase case (where
    # all three individual refi flags are already known False above).
    if purpose == "PURCHASE":
        fields["Loans.ContextFlag_any_refinance_type"] = _field(
            False, "loanTerms.loanPurposeType=PURCHASE")
    elif "REFINANCE" in purpose:
        fields["Loans.ContextFlag_any_refinance_type"] = _field(
            True, "loanTerms.loanPurposeType=%s" % purpose)
    # else: purpose unknown or neither Purchase nor Refinance-shaped --
    # deliberately left unset.

    # --- documentAnnotations (added, Workstream B of
    # .claude/plans/1-no-no-this-iridescent-brooks.md) ---------------------
    # `documents[]` entries carry an optional `documentAnnotations` field --
    # a list of {field, value} pairs -- non-null on exactly 3 of 62 documents
    # for this loan (2 "Bank Statement", 1 "Gift Letter"). Previously read
    # nowhere in this adapter (confirmed by grep before this change). Mirrors
    # the doc_present_* pattern immediately above: first document of a given
    # type wins if more than one exists (matching docs_by_type's setdefault
    # semantics), and a field is only set when its annotation KEY is present
    # in the source array -- an explicit blank string ("") is preserved as
    # truth="" (distinct from the field being absent from `fields` entirely
    # when the source never carried that annotation key at all). Verified
    # against the raw payload: the Gift Letter's receiverFirstName,
    # receiverLastName, and donarSignDate (source's own spelling -- not
    # "donorSignDate") are all present-but-blank; there is no donor-name
    # annotation key at all on this document (a genuine data gap, not an
    # adapter oversight -- not fabricated here).
    _ANNOTATION_FIELDS_BY_DOC_TYPE = {
        "Bank Statement": {
            "accountNumber": "bank_statement_account_number",
            "startDate": "bank_statement_start_date",
            "endDate": "bank_statement_end_date",
            "institutionName": "bank_statement_institution_name",
            "accountHolderFirstName": "bank_statement_account_holder_first_name",
            "accountHolderLastName": "bank_statement_account_holder_last_name",
        },
        "Gift Letter": {
            "receiverFirstName": "gift_letter_receiver_first_name",
            "receiverLastName": "gift_letter_receiver_last_name",
            "donarSignDate": "gift_letter_donor_sign_date",  # sic: source misspells "donor"
        },
    }
    annotations_by_doc_type: Dict[str, list] = {}
    for doc in loan_app.get("documents", []) or []:
        dtype = doc.get("documentType")
        anns = doc.get("documentAnnotations")
        if dtype in _ANNOTATION_FIELDS_BY_DOC_TYPE and anns and dtype not in annotations_by_doc_type:
            annotations_by_doc_type[dtype] = anns  # first doc of this type wins

    for dtype, field_map in _ANNOTATION_FIELDS_BY_DOC_TYPE.items():
        anns = annotations_by_doc_type.get(dtype)
        if not anns:
            continue
        ann_by_field = {a.get("field"): a.get("value") for a in anns if a.get("field")}
        for source_field, fixture_field in field_map.items():
            if source_field in ann_by_field:  # presence check, not truthiness -- keeps blanks
                fields[fixture_field] = _field(
                    ann_by_field[source_field],
                    "documents[] entry (documentType=%s) documentAnnotations.%s" % (dtype, source_field))

    # 2026-07-31, workstream A0b: an unconditional-True sentinel, NOT derived
    # from any loan data, used only by import_gold_ruleset.py's autopass
    # synthesis for the 66 checks that require verifying something inside
    # DU/EPIC/Loan Delivery (a system this project has no connection to).
    # Deliberately named to be self-explanatory in an audit -- see
    # storage/rules/gold/data/autopass_no_system_access.json's _meta for the
    # full decision record.
    fields["_demo_autopass_sentinel_true"] = _field(
        True, "synthetic: demo-scope auto-pass sentinel, not from any document or system source")

    # 2026-07-31, workstream A2: an unconditional-False sentinel used only by
    # import_gold_ruleset.py's scenario-gate overlay, to force NOT_APPLICABLE
    # (via the existing applies_if mechanism) on checks whose trigger was
    # determined provably false for THIS loan by the scenario-applicability
    # experiment. The per-check cited fact/reason lives in
    # storage/rules/gold/data/scenario_applicability_loan12607601215.json and
    # gold_to_check_mapping.json -- not reconstructable from this sentinel
    # alone, by design (one shared field keeps this loan-independent/reusable
    # rather than requiring one hardcoded field per check).
    fields["_demo_scenario_gate_always_false"] = _field(
        False, "synthetic: demo-scope scenario-gate sentinel, not from any document or system source")

    return {
        "loan_id": str(loan_id),
        "loan_type": "CONVENTIONAL",
        "fields": fields,
        "facts": facts,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print(__doc__)
        print("\nUsage: python3 touchless_adapter.py <loan_application.json> <extracted_data.json> <output.json>")
        sys.exit(1)

    result = adapt_touchless_to_fixture(sys.argv[1], sys.argv[2])
    with open(sys.argv[3], "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1, sort_keys=True)

    print("Converted Touchless data to qc_engine fixture format:")
    print(f"  Loan ID: {result['loan_id']}")
    print(f"  Fields:  {len(result['fields'])}")
    print(f"  Facts:   {len(result['facts'])}")
    print(f"  Output:  {sys.argv[3]}")
