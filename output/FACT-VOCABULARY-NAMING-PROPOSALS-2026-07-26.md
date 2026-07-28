# Fact-Vocabulary Naming Proposals — For SME Review

**Drafted by**: us.anthropic.claude-sonnet-4-6 (temp 0, one-time compile-time pass) · **Trust tier**: MEDIUM — nothing below is active until you approve it. The engine and the signed vocabulary are untouched by this document.

Approving a row = that question's rules start gating automatically on the named loan fact (the same 5-minute review shape as the gift fact). Rejecting or editing costs nothing — these are drafts.

## Question 570906 — 683 rules gated

| Proposed fact | Type | Answers → value | In catalog? | Confidence |
|---|---|---|---|---|
| `income_type_used_for_qualification` | enum | "Alimony, Child Support and/or Maintenance" → alimony_child_support_maintenance; "Alimony, Child Support, Maintenance and/or Other Nontaxable Income" → alimony_child_support_maintenance_nontaxable; "Auto Allowance" → auto_allowance; "Housing Assistance" → housing_assistance; "Military" → military; "Overtime, Bonus and Commission" → overtime_bonus_commission; "Part-Time, Second Job, Seasonal and/or Unemployment" → part_time_second_job_seasonal_unemployment; "Rental" → rental; "Restricted Stock" → restricted_stock; "Self-Employment" → self_employment; "Social Security, Retirement and/or Disability" → social_security_retirement_disability; "Trust" → trust; "Wage Earner" → wage_earner; "Other" → other | NEW — needs catalog entry | medium |

Abstained (model declined to guess): "Assets" (assets are not an income type and may represent a distinct asset-depletion or asset-based qualification fact requiring its own field)

## Question 570606 — 362 rules gated
*Already approved: {'Yes - Gift': 'gift_funds_used'}*

| Proposed fact | Type | Answers → value | In catalog? | Confidence |
|---|---|---|---|---|
| `closing_funds_asset_type` | enum | "Yes - Business Assets" → business_assets; "Yes - Cash on hand" → cash_on_hand; "Yes - Checking/Savings" → checking_savings; "Yes - Earnest Money Deposit" → earnest_money_deposit; "Yes - Employer Assistance" → employer_assistance; "Yes - Grant" → grant; "Yes - Interested Party Contributions" → interested_party_contributions; "Yes - Life Insurance" → life_insurance; "Yes - Net Proceeds" → net_proceeds; "Yes - Personal Loan/Sale of Assets" → personal_loan_sale_of_assets; "Yes - Retirement" → retirement; "Yes - Secondary Financing" → secondary_financing; "Yes - Stocks/Bonds" → stocks_bonds; "Yes - Trade or Sweat Equity" → trade_or_sweat_equity; "Yes - Trust Fund" → trust_fund; "Yes - Other" → other | NEW — needs catalog entry | high |

## Question 571198 — 283 rules gated

| Proposed fact | Type | Answers → value | In catalog? | Confidence |
|---|---|---|---|---|
| `appraisal_waiver_type` | enum | "Yes, there is an appraisal in the file" → full_appraisal; "No, value acceptance + property data was exercised" → value_acceptance_plus_property_data | NEW — needs catalog entry | high |

Abstained (model declined to guess): "Yes" (Ambiguous — 'Yes' could affirm appraisal presence or waiver exercise depending on rule context; cannot assign to a single canonical value without additional disambiguation.)

## Question 571083 — 258 rules gated

| Proposed fact | Type | Answers → value | In catalog? | Confidence |
|---|---|---|---|---|
| `loan_transaction_type` | enum | "Purchase" → purchase; "Cash-Out Refinance" → cash_out_refinance; "Limited Cash-Out Refinance" → limited_cash_out_refinance; "RefiNow" → refi_now; "Construction-to-Permanent (CP)" → construction_to_permanent; "Adjustable Rate Mortgage (ARM)" → arm; "Buydown" → buydown; "High-Balance Mortgage" → high_balance; "HomeReady" → home_ready; "HomeStyle Energy" → homestyle_energy; "HomeStyle Renovation" → homestyle_renovation; "MH Advantage" → mh_advantage; "Community Seconds or Community Land Trust" → community_seconds_or_clt; "Resale Restriction Loans" → resale_restriction; "Shared Equity Transaction" → shared_equity; "SONYMA Project Review" → sonyma_project_review; "Texas Section 50(a)(6)" → texas_50a6 | NEW — needs catalog entry | high |

## Question 571085 — 239 rules gated

| Proposed fact | Type | Answers → value | In catalog? | Confidence |
|---|---|---|---|---|
| `loan_product_type` | enum | "Adjustable Rate (ARM)" → adjustable_rate_arm; "Buydown Mortgage" → buydown_mortgage; "CHOICEHome" → choice_home; "CHOICERenovation Mortgage" → choice_renovation_mortgage; "Cash-Out Refinance" → cash_out_refinance; "Community Land Trust" → community_land_trust; "Construction Conversion and Renovation Mortgage" → construction_conversion_and_renovation_mortgage; "GreenCHOICE Mortgage" → green_choice_mortgage; "Home Possible Mortgage" → home_possible_mortgage; "HomeOne Mortgage" → home_one_mortgage; "Loans with Resale Restrictions" → loans_with_resale_restrictions; "No Cash-Out Refinance" → no_cash_out_refinance; "Purchase" → purchase; "Refi Possible Mortgage" → refi_possible_mortgage; "Section 502 GRH Mortgage" → section_502_grh_mortgage; "Seller-Owned Converted or Seller-Owned Modified Transaction" → seller_owned_converted_or_modified; "Super Conforming Mortgage" → super_conforming_mortgage; "Texas Equity Section 50(a)(6) " → texas_equity_section_50a6 | NEW — needs catalog entry | high |

## Question 571199 — 202 rules gated

| Proposed fact | Type | Answers → value | In catalog? | Confidence |
|---|---|---|---|---|
| `appraisal_in_file` | boolean | "Yes, there is an appraisal in the file" → true | NEW — needs catalog entry | high |

## Question 571200 — 114 rules gated

| Proposed fact | Type | Answers → value | In catalog? | Confidence |
|---|---|---|---|---|
| `appraisal_in_file` | boolean | "Yes, there is an appraisal in the file" → true | NEW — needs catalog entry | high |

## Question 570811 — 109 rules gated

| Proposed fact | Type | Answers → value | In catalog? | Confidence |
|---|---|---|---|---|
| `loan_collateral_advisor_relief_type` | enum | "Loan Collateral Advisor Reps & Warrants Relief with ACE + PDR" → lca_rw_relief_ace_pdr; "Loan Collateral Advisor Reps & Warrants Relief with an Accepted Appraisal Waiver" → lca_rw_relief_appraisal_waiver; "Loan Collateral Advisor Reps & Warrants Relief with an Appraisal" → lca_rw_relief_appraisal | NEW — needs catalog entry | high |
| `automated_assessment_type` | enum | "Automated Asset Assessment" → automated_asset_assessment; "Automated Employment Assessment" → automated_employment_assessment; "Automated Income Assessment" → automated_income_assessment | NEW — needs catalog entry | medium |

## Question 571087 — 105 rules gated

| Proposed fact | Type | Answers → value | In catalog? | Confidence |
|---|---|---|---|---|
| `loan_transaction_type` | enum | "Adjustable Rate Mortgage (ARM)" → arm; "Buydown Loan" → buydown; "Cash-Out Refinance" → cash_out_refinance; "Interest Rate Reduction Refinancing Loans (IRRRLs)" → irrrl; "Joint Loan" → joint_loan; "New Construction/Construction Permanent Home Loan" → new_construction_construction_permanent; "Purchase" → purchase; "Assumption" → assumption; "Energy Efficient Mortgage" → energy_efficient_mortgage; "Farm Residence Loan" → farm_residence_loan; "Supplemental Loan" → supplemental_loan; "Alternations and Repairs Loan" → alterations_and_repairs_loan | NEW — needs catalog entry | high |

## Question 571197 — 104 rules gated

| Proposed fact | Type | Answers → value | In catalog? | Confidence |
|---|---|---|---|---|
| `appraisal_in_file` | boolean | "Yes, there is an appraisal in the file" → true | NEW — needs catalog entry | high |

## Question 571084 — 99 rules gated

| Proposed fact | Type | Answers → value | In catalog? | Confidence |
|---|---|---|---|---|
| `fha_loan_purpose_type` | enum | "Assumption" → assumption; "Cash-Out Refinance" → cash_out_refinance; "Construction to Permanent (CP)" → construction_to_permanent; "Energy Efficient Mortgage (EEM)" → energy_efficient_mortgage; "HUD Real Estate Owned (REO) Property " → hud_reo_property; "New Construction" → new_construction; "No Cash-Out Refinance" → no_cash_out_refinance; "Purchase" → purchase; "Section 203(h) Mortgage Insurance for Disaster Victims" → section_203h_disaster_victims; "Section 251 Adjustable Rate Mortgage (ARM) " → section_251_arm; "Solar and Wind Technologies Product " → solar_wind_technologies; "Weatherization Product" → weatherization_product | NEW — needs catalog entry | high |

## Question 570730 — 89 rules gated

| Proposed fact | Type | Answers → value | In catalog? | Confidence |
|---|---|---|---|---|
| `credit_report_present_for_all_applicants` | boolean | "Yes, a credit report is in the file for each responsible applicant" → true; "A credit report is missing for at least one applicant" → false | NEW — needs catalog entry | high |

## Question 570729 — 73 rules gated

| Proposed fact | Type | Answers → value | In catalog? | Confidence |
|---|---|---|---|---|
| `credit_report_present_for_all_applicants` | boolean | "Yes, a credit report is in the file for each responsible applicant" → true; "A credit report is missing for at least one applicant(s)" → false | NEW — needs catalog entry | high |

## Question 570734 — 67 rules gated

| Proposed fact | Type | Answers → value | In catalog? | Confidence |
|---|---|---|---|---|
| `derogatory_credit_item_type` | enum | "Bankruptcy" → bankruptcy; "Collection Accounts" → collection_accounts; "Deed-in-Lieu (DIL)" → deed_in_lieu; "Deferred Obligations (Excluding Student Loans)" → deferred_obligations_non_student; "Delinquent Federal Non-Tax Debt" → delinquent_federal_non_tax_debt; "Delinquent Federal Tax Debt" → delinquent_federal_tax_debt; "Disputed Derogatory Credit Accounts" → disputed_derogatory_credit_accounts; "Federal Debt" → federal_debt; "Federal Tax Liens" → federal_tax_liens; "Foreclosure" → foreclosure; "Judgements" → judgments; "Non-Borrowing Spouse Debt" → non_borrowing_spouse_debt; "Pre-Foreclosure Sales (Short Sales)" → pre_foreclosure_short_sale; "Student Loan Liabilities" → student_loan_liabilities; "Undisclosed Debt" → undisclosed_debt | NEW — needs catalog entry | high |

## Question 570731 — 66 rules gated

| Proposed fact | Type | Answers → value | In catalog? | Confidence |
|---|---|---|---|---|
| `credit_report_present_for_all_applicants` | boolean | "Yes, a credit report is in the file for each responsible applicant" → true; "A credit report is missing for at least one applicant(s)" → false | NEW — needs catalog entry | high |

## Question 570834 — 64 rules gated

| Proposed fact | Type | Answers → value | In catalog? | Confidence |
|---|---|---|---|---|
| `borrower_income_type` | enum | "Wage Earner" → wage_earner; "Self-Employment" → self_employment; "Overtime, Bonus and Commission" → overtime_bonus_commission; "Part-Time, Second Job, Seasonal and/or Unemployment" → part_time_second_job_seasonal_unemployment; "Social Security, Retirement and/or Disability" → social_security_retirement_disability; "Rental" → rental; "Military" → military; "Alimony, Child Support and/or Maintenance" → alimony_child_support_maintenance; "Trust" → trust; "Other" → other | NEW — needs catalog entry | high |

## Question 571202 — 63 rules gated

| Proposed fact | Type | Answers → value | In catalog? | Confidence |
|---|---|---|---|---|
| `appraisal_in_file` | boolean | "Yes, there is an appraisal in the file" → true | NEW — needs catalog entry | high |

## Question 571086 — 61 rules gated

| Proposed fact | Type | Answers → value | In catalog? | Confidence |
|---|---|---|---|---|
| `loan_transaction_type` | enum | "Purchase" → purchase; "Refinance" → refinance; "Combination Construction to Permanent (CP)" → construction_to_permanent; "Buydown" → buydown; "Tribal Land" → tribal_land | NEW — needs catalog entry | medium |

## Question 570809 — 57 rules gated

| Proposed fact | Type | Answers → value | In catalog? | Confidence |
|---|---|---|---|---|
| `du_validation_service_components_received` | enum | "Appraised Value DU Validation Reps & Warrants Relief received" → appraised_value_relief; "Asset DU Validation Reps & Warrants Relief received" → asset_relief; "Employment DU Validation Reps & Warrants Relief received" → employment_relief; "Income DU Validation Reps & Warrants Relief received" → income_relief; "Rent Payment History DU Credit Risk Assessment" → rent_payment_history_credit_risk_assessment | NEW — needs catalog entry | high |

## Question 570680 — 55 rules gated

| Proposed fact | Type | Answers → value | In catalog? | Confidence |
|---|---|---|---|---|
| `hpml_atr_qm_review_required` | boolean | "Yes, all mtgs except HELOCs & CONV Investment properties" → true; "N/A, loan is a HELOC or CONV Investment property" → false | NEW — needs catalog entry | medium |

## Question 570733 — 53 rules gated

| Proposed fact | Type | Answers → value | In catalog? | Confidence |
|---|---|---|---|---|
| `credit_report_present_for_all_applicants` | boolean | "Yes, a credit report is in the file for each responsible applicant" → true; "A credit report is missing for at least one applicant(s)" → false | NEW — needs catalog entry | high |

## Question 570732 — 48 rules gated

| Proposed fact | Type | Answers → value | In catalog? | Confidence |
|---|---|---|---|---|
| `credit_report_present_for_all_applicants` | boolean | "Yes, a credit report is in the file for each responsible applicant" → true; "A credit report is missing for at least one applicant(s) " → false | NEW — needs catalog entry | high |

## Question 578782 — 16 rules gated

| Proposed fact | Type | Answers → value | In catalog? | Confidence |
|---|---|---|---|---|
| `electronic_closing_used` | boolean | "Yes" → true | NEW — needs catalog entry | medium |

## Question 570600 — 5 rules gated

| Proposed fact | Type | Answers → value | In catalog? | Confidence |
|---|---|---|---|---|
| `lep_requirements_met` | boolean | "Yes" → true | NEW — needs catalog entry | high |

