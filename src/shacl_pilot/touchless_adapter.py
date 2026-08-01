#!/usr/bin/env python3
"""
Touchless data adapter — converts Touchless API format to SHACL pilot extraction format.

Input:
  - loan_application.json (structured MISMO-like loan data)
  - extracted_data_*.json (document extraction key-value pairs with confidence)

Output:
  - extraction JSON compatible with loan_to_rdf.py (fields, facts, entities, citations)
"""
import json
import sys
from datetime import datetime

def ts_to_date(ts_ms):
    """Convert timestamp in milliseconds to ISO date."""
    if not ts_ms:
        return None
    return datetime.fromtimestamp(ts_ms / 1000).strftime("%Y-%m-%d")

def cite_touchless(source, confidence=None):
    """Citation for Touchless-sourced data."""
    snippet = f"Touchless extraction: {source}"
    if confidence:
        snippet += f" (confidence: {confidence})"
    return {
        "doc_name": "Touchless API",
        "page": 0,
        "snippet": snippet[:160]
    }

def adapt_touchless_to_extraction(loan_app_path, extracted_data_path):
    """
    Convert Touchless data files to SHACL pilot extraction format.
    """
    with open(loan_app_path) as f:
        loan_app = json.load(f)

    with open(extracted_data_path) as f:
        extracted_data = json.load(f)

    # Build fields dict
    fields = {}
    facts = {}
    entities = {
        "bank_txns": [],       # genuinely absent from this payload -- only 1 of
                                # 62 documents has field-level extraction (a
                                # Schedule C), and it's not a bank statement.
                                # Real gap, not an adapter oversight.
        "tradelines": [],      # same: no per-tradeline structured data in this
                                # payload's creditDetail (only aggregate scores).
        "urla_liabilities": [],  # populated below from liabilityDetail.liabilities[]
                                  # -- added 2026-07-31, this data DOES exist in
                                  # the raw payload and was previously discarded.
                                  # See output/BAKEOFF-P0-VS-SRC-GOLD-TOUCHLESS-
                                  # 2026-07-31.md.
        "comps": [],            # genuinely absent -- no appraisal comparable
                                 # sales data in this payload.
        "vom_rows": []          # genuinely absent -- no verification-of-mortgage
                                 # line items in this payload.
    }

    # Extract loan ID
    loan_id = loan_app.get("loanSummary", {}).get("lenderCaseIdentifier", "UNKNOWN")

    # --- LOAN SUMMARY FIELDS ---
    loan_summary = loan_app.get("loanSummary", {})
    loan_terms = loan_summary.get("loanTerms", {})

    if loan_id:
        fields["loan_number"] = {
            "value": loan_id,
            "kind": "str",
            "citation": cite_touchless("loanSummary.lenderCaseIdentifier")
        }

    if loan_terms.get("loanPurposeType"):
        fields["loan_purpose_1003"] = {
            "value": loan_terms["loanPurposeType"],
            "kind": "str",
            "citation": cite_touchless("loanTerms.loanPurposeType")
        }

    if loan_terms.get("mortgageType"):
        fields["loan_program_1003"] = {
            "value": loan_terms["mortgageType"],
            "kind": "str",
            "citation": cite_touchless("loanTerms.mortgageType")
        }
        fields["mismo_mortgage_type"] = {
            "value": loan_terms["mortgageType"],
            "kind": "str",
            "citation": cite_touchless("loanTerms.mortgageType")
        }

    if loan_terms.get("baseLoanAmount"):
        fields["mismo_loan_amount"] = {
            "value": float(loan_terms["baseLoanAmount"]),
            "kind": "money",
            "citation": cite_touchless("loanTerms.baseLoanAmount")
        }

    if loan_terms.get("interestRate"):
        fields["mismo_note_rate"] = {
            "value": float(loan_terms["interestRate"]),
            "kind": "pct",
            "citation": cite_touchless("loanTerms.interestRate")
        }

    # Application date
    app_date_ts = loan_summary.get("applicationDate")
    if app_date_ts:
        fields["application_date"] = {
            "value": ts_to_date(app_date_ts),
            "kind": "date",
            "citation": cite_touchless("loanSummary.applicationDate")
        }

    # Qualification / ratios
    qual = loan_summary.get("qualification", {})
    if qual.get("totalMonthlyIncomeAmount"):
        fields["mismo_total_monthly_income"] = {
            "value": float(qual["totalMonthlyIncomeAmount"]),
            "kind": "money",
            "citation": cite_touchless("qualification.totalMonthlyIncomeAmount")
        }

    if qual.get("housingExpenseRatioPercent"):
        fields["housing_ratio"] = {
            "value": float(qual["housingExpenseRatioPercent"]),
            "kind": "pct",
            "citation": cite_touchless("qualification.housingExpenseRatioPercent")
        }

    if qual.get("totalDebtExpenseRatioPercent"):
        fields["dti_ratio"] = {
            "value": float(qual["totalDebtExpenseRatioPercent"]),
            "kind": "pct",
            "citation": cite_touchless("qualification.totalDebtExpenseRatioPercent")
        }

    # LTV
    ltv_ratio = loan_summary.get("ltvRatio", {})
    if ltv_ratio.get("ltv"):
        fields["ltv"] = {
            "value": float(ltv_ratio["ltv"]),
            "kind": "pct",
            "citation": cite_touchless("ltvRatio.ltv")
        }

    # FICO
    if loan_summary.get("fico"):
        fields["credit_score_1003"] = {
            "value": str(int(loan_summary["fico"])),
            "kind": "str",
            "citation": cite_touchless("loanSummary.fico")
        }

    # --- BORROWER DETAILS ---
    borrower_pairs = loan_app.get("borrowersDetail", {}).get("borrowerPairs", [])
    if borrower_pairs:
        borrowers_list = borrower_pairs[0].get("borrowers", [])
        if borrowers_list:
            borrower = borrowers_list[0]  # primary borrower

            # Name
            name_parts = []
            if borrower.get("firstName"):
                name_parts.append(borrower["firstName"])
            if borrower.get("middleName"):
                name_parts.append(borrower["middleName"])
            if borrower.get("lastName"):
                name_parts.append(borrower["lastName"])

            if name_parts:
                fields["borrower_name"] = {
                    "value": " ".join(name_parts),
                    "kind": "str",
                    "citation": cite_touchless("borrowersDetail.borrowerPairs[0].borrowers[0]")
                }

            # Employment
            employers = borrower.get("employers", [])
            if employers:
                emp = employers[0]

                if emp.get("employerName"):
                    fields["employer_name_1003"] = {
                        "value": emp["employerName"],
                        "kind": "str",
                        "citation": cite_touchless("employers[0].employerName")
                    }

                # Employment details
                employment = emp.get("employment", {})
                if employment.get("employmentStartDate"):
                    fields["employment_start_date_1003"] = {
                        "value": ts_to_date(employment["employmentStartDate"]),
                        "kind": "date",
                        "citation": cite_touchless("employers[0].employment.employmentStartDate")
                    }

                # Income
                income_list = emp.get("income", [])
                if income_list:
                    inc = income_list[0]
                    if inc.get("monthlyIncome"):
                        fields["base_monthly_income_1003"] = {
                            "value": float(inc["monthlyIncome"]),
                            "kind": "money",
                            "citation": cite_touchless("employers[0].income[0].monthlyIncome")
                        }

                # Self-employed check
                ownership = employment.get("ownershipInterestType", "")
                is_se = employment.get("isSelfEmployed")
                if is_se or "25Percent" in ownership:
                    facts["borrower_self_employed"] = {
                        "value": True,
                        "citation": cite_touchless(f"employment.ownershipInterestType: {ownership}, isSelfEmployed: {is_se}")
                    }

    # --- PROPERTY/COLLATERAL ---
    collateral = loan_app.get("collateralDetail", {}).get("collateral", [])
    if collateral:
        prop = collateral[0]

        # Address
        addr = prop.get("propertyAddress", {})
        if addr.get("state"):
            fields["property_state"] = {
                "value": addr["state"],
                "kind": "str",
                "citation": cite_touchless("collateralDetail.collateral[0].propertyAddress.state")
            }

        # Property value / appraisal
        appraisal = prop.get("appraisal", {})
        if appraisal.get("appraisedValue"):
            fields["appraised_value"] = {
                "value": float(appraisal["appraisedValue"]),
                "kind": "money",
                "citation": cite_touchless("appraisal.appraisedValue")
            }

        if appraisal.get("appraisalEffectiveDate"):
            fields["appraisal_effective_date"] = {
                "value": ts_to_date(appraisal["appraisalEffectiveDate"]),
                "kind": "date",
                "citation": cite_touchless("appraisal.appraisalEffectiveDate")
            }

        # Property details
        prop_detail = prop.get("propertyDetail", {})
        if prop_detail.get("yearBuilt"):
            fields["property_year_built"] = {
                "value": str(prop_detail["yearBuilt"]),
                "kind": "str",
                "citation": cite_touchless("propertyDetail.yearBuilt")
            }

    # --- EXTRACTED DOCUMENT DATA (Schedule C, tax forms, etc.) ---
    # Build a dict by field name
    extracted_by_field = {}
    for item in extracted_data:
        name = item.get("name")
        value = item.get("value")
        confidence = item.get("confidence")

        if name and value:  # only include non-empty values
            extracted_by_field[name] = {"value": value, "confidence": confidence}

    # Map key extracted fields to pilot schema
    if "Tax_Year" in extracted_by_field:
        fields["tax_year_schedule_c"] = {
            "value": extracted_by_field["Tax_Year"]["value"],
            "kind": "str",
            "citation": cite_touchless("Schedule C: Tax_Year", extracted_by_field["Tax_Year"]["confidence"])
        }

    if "Gross_Profit" in extracted_by_field:
        fields["gross_profit_schedule_c"] = {
            "value": float(extracted_by_field["Gross_Profit"]["value"]),
            "kind": "money",
            "citation": cite_touchless("Schedule C: Gross_Profit", extracted_by_field["Gross_Profit"]["confidence"])
        }

    if "Net_Profit" in extracted_by_field:
        fields["net_profit_schedule_c"] = {
            "value": float(extracted_by_field["Net_Profit"]["value"]),
            "kind": "money",
            "citation": cite_touchless("Schedule C: Net_Profit", extracted_by_field["Net_Profit"]["confidence"])
        }

    # --- CREDIT / LIABILITIES ---
    credit = loan_app.get("creditDetail", {})
    credit_score_data = credit.get("creditScore", [])
    if credit_score_data:
        # Use middle score if available
        scores = [s.get("creditRepositorySourceScore") for s in credit_score_data if s.get("creditRepositorySourceScore")]
        if len(scores) >= 2:
            scores_sorted = sorted([int(s) for s in scores])
            middle_score = scores_sorted[len(scores_sorted) // 2]
            fields["credit_score_bureau"] = {
                "value": str(middle_score),
                "kind": "str",
                "citation": cite_touchless(f"creditDetail.creditScore middle of {len(scores)} scores")
            }

    # --- DOCUMENT INVENTORY ---
    # Added 2026-07-31: `documents[]` DOES exist in this payload (62 real
    # entries with a documentType, e.g. "Gift Letter", "Credit Report") --
    # the prior "Touchless doesn't provide doc inventory" comment here was
    # incorrect. Populate docs_present from it. This alone does not make
    # every AMQ doc_presence check resolvable -- Touchless's ~30 document
    # types are coarser than AMQ's document-name vocabulary, and this
    # project already has a guardrailed process for that specific crosswalk
    # problem (mapping/llm_doc_mapper.py) precisely because naive matching
    # produces false positives (verified during this fix: keyword-matching
    # "gift of equity" to "Closing Disclosure"). This dict is honest, real
    # data; which gold checks actually reference it is a separate,
    # individually-curated decision (see ruleset_to_shacl.py's
    # CURATED_DOC_MATCHES).
    docs_present = {}
    for doc in loan_app.get("documents", []) or []:
        dtype = doc.get("documentType")
        if dtype:
            docs_present[dtype] = doc.get("documentId", True)

    # --- documentAnnotations (added, Workstream B of
    # .claude/plans/1-no-no-this-iridescent-brooks.md) ---------------------
    # `documents[]` entries carry an optional `documentAnnotations` field --
    # a list of {field, value} pairs -- non-null on exactly 3 of 62
    # documents for this loan (2 "Bank Statement", 1 "Gift Letter"). Mirrors
    # docs_present above (first document of a given type wins if more than
    # one exists) and the p0 bake-off counterpart
    # (p0/qc_engine/adapters/touchless_adapter.py) field-for-field, so both
    # engines see identical input. A field is only added to `fields` when
    # its annotation KEY is present in the source array -- an explicit
    # blank string ("") is preserved as value="" (distinct from the key
    # never appearing at all, which leaves the fixture field entirely
    # unset). Verified against the raw payload: the Gift Letter's
    # receiverFirstName, receiverLastName, and donarSignDate (source's own
    # spelling -- not "donorSignDate") are all present-but-blank; there is
    # no donor-name annotation key at all on this document (a genuine data
    # gap, not an adapter oversight -- not fabricated here).
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
    annotations_by_doc_type = {}
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
                fields[fixture_field] = {
                    "value": ann_by_field[source_field],
                    "kind": "str",
                    "citation": cite_touchless(
                        "documents[] entry (documentType=%s) documentAnnotations.%s" % (dtype, source_field))
                }

    # --- LIABILITIES (urla_liabilities entity family) ---
    # Added 2026-07-31: liabilityDetail.liabilities[] has real, structured
    # per-liability records (creditor name, balance, monthly payment,
    # status) that were previously discarded despite existing in the
    # payload. This is a direct structural mapping (no document-name
    # crosswalk ambiguity -- these are the borrower's actual liability
    # records), unlike docs_present above.
    for liab in (loan_app.get("liabilityDetail", {}) or {}).get("liabilities", []) or []:
        holder = liab.get("holder", {}) or {}
        entities["urla_liabilities"].append({
            "creditor": holder.get("fullName") or "UNKNOWN",
            "liability_type": liab.get("type"),
            "balance": liab.get("unpaidBalanceAmount"),
            "monthly_payment": liab.get("monthlyPaymentAmount"),
            "status": liab.get("status"),
            "citation": cite_touchless("liabilityDetail.liabilities[%s]" % liab.get("accountIdentifier", "?")),
        })

    # Build extraction result
    result = {
        "loan_id": loan_id,
        "folder": "Touchless API",
        "docs_present": docs_present,
        "fields": fields,
        "facts": facts,
        "entities": entities
    }

    return result


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__)
        print("\nUsage: python3 touchless_adapter.py <loan_application.json> <extracted_data.json> <output.json>")
        sys.exit(1)

    result = adapt_touchless_to_extraction(sys.argv[1], sys.argv[2])

    with open(sys.argv[3], "w") as f:
        json.dump(result, f, indent=1, sort_keys=True)

    print(f"Converted Touchless data to extraction format:")
    print(f"  Loan ID:      {result['loan_id']}")
    print(f"  Fields:       {len(result['fields'])}")
    print(f"  Facts:        {len(result['facts'])}")
    print(f"  Output:       {sys.argv[3]}")
