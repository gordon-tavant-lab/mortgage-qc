# Base digest: 266 cards

### PC::ATR Exempt | ATR-QM | ATR Exempt
Q: Were all exempt HELOC & CONV Investment property ATR & QM eligibility requirements met? (Review final compliance ease reports)
APPLIES: (always)
SKIP: yes | clean_opts: 1 | defect_opts: 2
  - [Critical] ATR exempt APR exceeds APOR by 6.5% or more &/or not calculated per the provisions of HOEPA in TILA -> O-FRD-54600
  - [Critical] The subject ATR exempt transaction charged points and fees exceed 5% of the total loan amount -> O-FRD-54596

### PC::ATR-QM | ATR-QM | ATR-QM
Q: Were all Ability to Repay (ATR) and Qualified Mortgage (QM) eligibility requirements met? (Review final compliance ease reports)
APPLIES: (always)
SKIP: yes | clean_opts: 1 | defect_opts: 6
  - [Critical] No, the subject ATR covered transaction is not fully amortizing -> O-FRD-54593
  - [Critical] The subject ATR covered transaction is not fully amortizing -> O-FRD-54593
  - [Critical] APR exceeds APOR by 2.25% or as per revised QM rule &/or was not calculated per the rule provisions -> O-FRD-54599
  - [Critical] The subject ATR covered transaction loan term exceeded 30 years -> O-FRD-54594
  - [Critical] ATR covered loan charged points and fees exceed 3% or as per the loan amount if less than $100,000 -> O-FRD-54595
  - [Critical] No, the total points and fees charged exceed five percent of the loan amount -> O-FRD-00816

### PC::AUS Findings | Underwriting | AUS Findings
Q: Do the final AUS findings match all other documentation in the file?
APPLIES: Loans.Underwriting_Type = 'Desktop Underwriter' OR Loans.Underwriting_Type = 'GUS' OR Loans.Underwriting_Type = 'Loan Product Advisor'
SKIP: no | clean_opts: 2 | defect_opts: 8
  - [Major] The property type on the final AUS does not match the property type listed on the appraisal -> Property Type/Appr
  - [Major] Cash to close on the final AUS doesn't match final 1003 or 1008 -> DUFindings-A
  - [Major] The appraised value on the Final AUS does not match the final 1003 and/or the final 1008 -> DUFindings-D
  - [Major] The DTI on the final AUS does not match the final 1003 and/or the final 1008 -> DUFindings-C
  - [Major] The LTV on the final AUS does not match the final 1003 and/or the final 1008 -> DUFindings-B
  - [Major] The property type on the final AUS findings do not match the final 1003 and/or the final 1008 -> DUFindings-E
  - [Major] The total verified assets submitted to AUS does not match the final 1003 & 1008 -> DUFindings-F
  - [Critical] Value Acceptance utilized with incorrect data submitted to AUS and may impact waiver approval -> Value acceptance

### PC::Asset | Assets | Asset
Q: Were all recurring payments reflected on bank statements addressed?
APPLIES: (always)
SKIP: no | clean_opts: 2 | defect_opts: 1
  - [Critical] All recurring payments that are reflected on bank statements were not addressed by the underwriter -> Asset-1

### PC::CIP DATA POINTS | Application | CIP DATA POINTS
Q: Are the 4 Customer Identification Program (CIP) data points provided in file: Name, Physical property address, DOB, SS#/Tax ID?
APPLIES: (always)
SKIP: no | clean_opts: 1 | defect_opts: 1
  - [Major] No, one or more of the CIP data points was not provided -> CIP data points

### PC::CU Score 2.5 | Property - Appraisal | CU Score 2.
Q: Was the appropriate level of appraisal review completed based on the CU score?
APPLIES: (always)
SKIP: no | clean_opts: 2 | defect_opts: 2
  - [Critical] CU score is =<2.5; prop is one unit detach, attach, condo & "data integrity" concerns not met -> Appraisal-Score=<2.5
  - [Critical] The CU score is >2.5 or Zero; 999 Score; 2 - 4 Unit prop; or COOP & unable to locate GAAR Worksheet -> Appraisal-Score>2.5

### PC::Closing Conditions | Closing | Closing Conditions
Q: Have all underwriting closing conditions been met?
APPLIES: (always)
SKIP: no | clean_opts: 2 | defect_opts: 3
  - [Major] No, underwriting closing conditions have not been met -> UW Condition-A
  - [Major] The closing condition for the 4506C is missing and/or incomplete -> UW-Conditions-2
  - [Major] The required condition for the borrower to sign and date letter(s) of explanation at closing is miss -> UW-Conditions-1

### PC::Contract | Loan Documents | Contract
Q: Were all sales contract requirements met?
APPLIES: Loans.LoanPurposeType = 'Purchase'
SKIP: no | clean_opts: 2 | defect_opts: 5
  - [Critical] Unable to locate proof the signer on the contract is an authorized individual -> ContractAuthSigner
  - [Critical] All Massachusetts (MA) Title 5 Septic requirements have not been met -> Sales Contract-2
  - [Major] All parties taking title to the property are not listed on the fully executed contract -> Title Party
  - [Critical] The sales contract indicates subject to completion or repairs, including safety, soundness or struct -> Sales Contract-1
  - [Major] Name of seller on sales contract does not match appraisal, HUD 1 and/or title commitment -> SELLER NAME/CONTRACT

### PC::Counter-offer | Underwriting | Counter-offer
Q: Was a counter-offer made (final terms were less favorable based on initial loan application & price/lock history screen)?
APPLIES: (always)
SKIP: no | clean_opts: 2 | defect_opts: 2
  - [Critical] Notice of adverse action/commitment with new terms not found or incorrect -> Adverse Action
  - [Major] Supplemental decision screen is missing rationale, discussion details and/or date/time stamps -> Dec Screen

### PC::Custodial Acct | Assets | Custodial Acct
Q: Were the funds from an acceptable source when a custodial account was utilized?
APPLIES: (always)
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] Ineligible custodial account (UTMA) and/or (UGMA) was used to qualify -> Custodial Acct

### PC::DATA-POINTS | Underwriting | DATA-POINTS
Q: Have all data points, including ULDD been verified as complete to avoid early check errors/defects?
APPLIES: (always)
SKIP: no | clean_opts: 1 | defect_opts: 1
  - [Major] The credit reference # in EPIC does not match AUS -> Data Points-7

### PC::DUValid | Underwriting | DUValid
Q: Have conditions required by DU been met?
APPLIES: Loans.Underwriting_Type = 'Desktop Underwriter'
SKIP: no | clean_opts: 1 | defect_opts: 9
  - [Critical] Condition for second job documentation when no second job applicable was not cleared -> DUValid-A
  - [Critical] Funds are required for closing; however, no funds submitted and/or short funds to close -> DUValid-B
  - [Critical] Loan registered as a HomeReady product; cannot locate income limits -> DUValid-C
  - [Critical] There are debts omitted from the DU incorrectly or without proper documentation (IE. Amex accounts) -> DUValid-G
  - [Critical] The required 12 month history for debt not properly reporting on credit was not obtained -> DUValid-E
  - [Critical] The standardized address used in approval of the PIW does not match the address submitted -> DUValid-F
  - [Critical] The total amount of the Seller Credits and/or CCA Lender combined credits exceeds the total estimate -> DUValid-D
  - [Critical] The declarations indicate borrower is a co-signor on a debt and unable to confirm this was addressed -> CoSignDebt
  - [Major] Secured funds were not entered correctly into DU and/or they were not identified separately -> DU Secured Funds

### PC::DebtsPaid | Credit - Liabilities | DebtsPaid
Q: Were all the requirements met for debts paid off at or prior to closing?
APPLIES: Loans.QC_Policy = 'Freddie Mac'
SKIP: no | clean_opts: 2 | defect_opts: 1
  - [Critical] All debts were not paid of at or prior to closing -> DEBTS-PAID

### PC::ESIGN | Loan Documents | ESIGN
Q: Where an electronic signature was utilized prior to closing was the proper documentation obtained?
APPLIES: (always)
SKIP: no | clean_opts: 2 | defect_opts: 1
  - [Major] No, unable to locate the notice of completion confirming a valid signature -> ESIGN

### PC::Final 1008 Transmittal | Underwriting | Final 1008 Transmittal
Q: Is the final 1008 Transmittal Summary accurate & complete?
APPLIES: Loans.LoanType = 'Conventional' OR Loans.LoanType = 'Portfolio'
SKIP: no | clean_opts: 2 | defect_opts: 7
  - [Major] The appraiser name and/or license # field is incomplete or incorrect -> O-FNM-00715-C
  - [Major] The Homebuyer Education Cert field is incomplete or incorrect -> O-FNM-00715-B
  - [Major] The level of property review field is incomplete or incorrect -> O-FNM-00715-D
  - [Major] The loan purpose field is incomplete or incorrect -> O-FNM-00715-E
  - [Major] The project review field is incorrect or incomplete -> O-FNM-00715-F
  - [Major] The final 1008 is incorrect or incomplete -> O-FNM-00715
  - [Major] The risk assessment field is incomplete/incorrect (AUS recommendation; DU Case #; AUS Key # - etc) -> O-FNM-00715-A

### PC::Final URLA | Application | Final URLA
Q: Have all sections of the Final 1003 been completed and accurate?
APPLIES: (always)
SKIP: no | clean_opts: 1 | defect_opts: 9
  - [Major] The employment dates listed on the 1003 do not match other employment documentation in the file -> URLA-Final-9
  - [Major] The final 1003 application is inaccurate or incomplete -> URLA-Final-2
  - [Major] The final 1003 is missing either a 2 year residency or employment history -> URLA-Final-4
  - [Major] The loan purpose selected on the final 1003 does not match the final 1008 and/or final DU -> URLA-Final-5
  - [Major] The manner in which title is held on the 1003 does not match the title commitment -> URLA-Final-8
  - [Major] The marital status is incomplete or appears inaccurate based on documentation in the file -> URLA-Final-7
  - [Major] The refinance type selected on the final 1003 does not match the final 1008 and/or the final DU -> URLA-Final-6
  - [Major] The title vesting on the final 1003 does not match the title commitment -> URLA-Final-3
  - [Major] Discrepancies in the file not explained or supporting docs provided -> Info Discrepancies

### PC::GAAR | Property - Appraisal | GAAR
Q: Was the GAAR worksheet completed in the file and all applicable conditions met?
APPLIES: Loans.LoanType = 'Conventional' OR Loans.LoanType = 'Portfolio'
SKIP: no | clean_opts: 2 | defect_opts: 1
  - [Major] Unable to locate the GAAR worksheet or confirm the conditions listed are met -> CRMReview

### PC::ICPL | Closing | ICPL
Q: Is the ICPL contained in the loan file accurate & complete?
APPLIES: (always)
SKIP: no | clean_opts: 2 | defect_opts: 4
  - [Major] The ICPL is not located in the file -> ICPL
  - [Major] The ICPL insurer does not match the title policy insurer -> ICPLInsure
  - [Major] The borrower information on the ICPL does not match the 1003 or LOS -> ICPLMatch
  - [Major] The mortgagee clause on the ICPL is incomplete or inaccurate -> ICPLMTGCLS

### PC::LendAuth | Product Specific | LendAuth
Q: Does the underwriter have the proper lending authority for this loan amount or product and the required second level review was not completed?
APPLIES: (always)
SKIP: no | clean_opts: 1 | defect_opts: 1
  - [Critical] No-U/W does not have proper lending auth for this loan amount/product & 2nd level review not found -> UWAuth

### PC::MaterialDisc | Underwriting | MaterialDisc
Q: Were all material discrepancies identified and the required documentation or commentary provided to address?
APPLIES: (always)
SKIP: no | clean_opts: 2 | defect_opts: 1
  - [Critical] Missing the required documentation or commentary addressing the material discrepancies identified -> UW-MatDiscrep/Other

### PC::MaxCash | Closing | MaxCash
Q: Is the max cash out condition present and accurate for the product?
APPLIES: (always)
SKIP: no | clean_opts: 2 | defect_opts: 1
  - [Major] The max cash out condition is missing and/or inaccurate for the product -> MaxCash

### PC::O-BP-14663 | Application | O-BP
Q: Were the following non-regulatory customary disclosures provided to the applicant in the initial disclosure package?
APPLIES: (always)
SKIP: no | clean_opts: 2 | defect_opts: 3
  - [Major] Borrower Certification and Authorization to Release Information was not provided -> O-BP-54652
  - [Major] Flood Insurance Coverage Disclosure was not provided -> O-BP-54653
  - [Major] Intent to Proceed with Application was not provided -> O-BP-54654

### PC::O-BP-14664 | Closing | O-BP
Q: Were the following non-regulatory customary disclosures provided to the applicant at closing?
APPLIES: (always)
SKIP: no | clean_opts: 2 | defect_opts: 2
  - [Major] Occupancy Statement was not provided -> O-BP-54659
  - [Major] Signature/Name Affidavit or AKA Notice was not provided -> O-BP-54660

### PC::O-BP-FED-16681 | Property - Appraisal | O-BP-FED
Q: Where there was an appraisal and AVM in the file, and the AVM value was used, was the AVM value based on appropriate valuation methods?
APPLIES: (always)
SKIP: no | clean_opts: 2 | defect_opts: 1
  - [Critical] (Best Practice) The use of the AVM value was based on inappropriate valuation methods -> O-BP-FED-59094

### PC::O-CFPB-14499 | Application | O-CFPB
Q: Is one or more consumers in the transaction a Limited English Proficient (LEP) individual, meaning an individual who does not speak English as their primary language and has a limited ability to read, speak, write, or understand English?
APPLIES: (always)
SKIP: no | clean_opts: 2 | defect_opts: 0

### PC::O-CFPB-14500 | Application | O-CFPB
Q: (Best Practice) Were all Limited English Proficiency (LEP) requirements met?
APPLIES: (always)
SKIP: yes | clean_opts: 2 | defect_opts: 3
  - [Minor] (Best Practice) Limited English Proficiency (LEP) disclosure not provided at the time of application -> O-CFPB-54136
  - [Minor] (Best Practice) Documented and verifiable LEP preferences were not obtained from the applicant(s) -> O-CFPB-54137
  - [Minor] (Best Practice) Standard/approved translated docs not issued based on the applicant(s) LEP pref. -> O-CFPB-54138

### PC::O-CFPB-14501 | Closing | O-CFPB
Q: (Best Practice) Were all Limited English Proficiency (LEP) requirements met?
APPLIES: (always)
SKIP: no | clean_opts: 1 | defect_opts: 1
  - [Critical] (Best Practice) Standard/approved translated docs not issued based on the applicant(s) LEP pref. -> O-CFPB-54139

### PC::O-CNTL-14366 | Assets | O-CNTL
Q: Were assets utilized from any of the following to qualify the loan?
APPLIES: (always)
SKIP: no | clean_opts: 18 | defect_opts: 0

### PC::O-CNTL-14367 | Income | O-CNTL
Q: What type of income was used to qualify the loan?
APPLIES: (always)
SKIP: no | clean_opts: 15 | defect_opts: 0

### PC::O-CNTL-14386 | Data Validation Svc-DVS | O-CNTL
Q: Does a component of this loan have DU Validation Reps & Warrants Relief?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 6 | defect_opts: 0

### PC::O-CNTL-14392 | Data Validation Svc-DVS | O-CNTL
Q: Does a component of this loan have LPA Reps & Warrants Relief?
APPLIES: (Loans.QC_Policy = 'Freddie Mac')
SKIP: no | clean_opts: 7 | defect_opts: 0

### PC::O-CNTL-14502 | ATR-QM | O-CNTL
Q: Is the loan program subject to ATR/QM?
APPLIES: (always)
SKIP: no | clean_opts: 2 | defect_opts: 0

### PC::O-CNTL-15941 | Loan Documents | O-CNTL
Q: Was the loan closed as an electronic transaction?
APPLIES: (always)
SKIP: no | clean_opts: 2 | defect_opts: 0

### PC::O-CNTL-16591 | Closing | O-CNTL
Q: Did the loan close as an electronic transaction?
APPLIES: (always)
SKIP: no | clean_opts: 2 | defect_opts: 0

### PC::O-EPD-14454 | EPD | O-EPD
Q: Did the EPD review reveal any borrower or other information discrepancy default indicators?
APPLIES: (always)
SKIP: no | clean_opts: 2 | defect_opts: 3
  - [Critical] There are address discrepancies within the loan file -> O-EPD-52909
  - [Critical] A purchaser was deleted from/added to the sales contract -> O-EPD-52908
  - [Critical] A mailed verification was returned as not deliverable -> O-EPD-52943

### PC::O-EPD-14455 | EPD | O-EPD
Q: Did the EPD review reveal any credit default indicators?
APPLIES: (always)
SKIP: no | clean_opts: 2 | defect_opts: 7
  - [Note] There were an excessive number of automated underwriting system submissions -> O-EPD-52913
  - [Critical] The review credit report contains new derogatory accounts after the loan closed -> O-EPD-52914
  - [Critical] DTI increased beyond allowable due to new/increased pymts as per the post-close review credit report -> O-EPD-52912
  - [Critical] Evidence of financial strain such as delinq taxes, judgements, default/modification recording, etc. -> O-EPD-52936
  - [Note] The review credit report revealed a significant number of inquiries after closing -> O-EPD-52910
  - [Critical] There is evidence of extreme payment shock -> O-EPD-52915
  - [Note] Significant new tradelines or increased debt added after the loan closed -> O-EPD-52911

### PC::O-EPD-14456 | EPD | O-EPD
Q: Did the EPD review reveal any occupancy default indicators?
APPLIES: (always)
SKIP: no | clean_opts: 2 | defect_opts: 3
  - [Critical] The billing address is not the property address in a primary residence transaction -> O-EPD-52917
  - [Critical] Borr occupying as primary in an investment purchase transaction that used rental income to qualify -> O-EPD-52918
  - [Critical] Post-closing occupancy could not be validated -> O-EPD-52916

### PC::O-EPD-14457 | EPD | O-EPD
Q: Did the EPD review reveal any income/employment default indicators?
APPLIES: (always)
SKIP: no | clean_opts: 2 | defect_opts: 3
  - [Critical] There is a significant or unrealistic commute distance -> O-EPD-52919
  - [Critical] A PO Box is the only address listed for an employer -> O-EPD-52921
  - [Critical] Income appears out of line with type of employment, applicant age, education, and/or lifestyle -> O-EPD-52920

### PC::O-EPD-14458 | EPD | O-EPD
Q: Did the EPD review reveal any asset default indicators?
APPLIES: (always)
SKIP: no | clean_opts: 2 | defect_opts: 3
  - [Critical] The bank account ownership includes an unknown party -> O-EPD-52924
  - [Critical] Down payment source is a gift, sale of personal property, etc in lieu of personal accounts -> O-EPD-52922
  - [Critical] The transaction is a cash-out refinance on a recently acquired property -> O-EPD-52923

### PC::O-EPD-14459 | EPD | O-EPD
Q: Did the EPD review reveal any property/value default indicators?
APPLIES: (always)
SKIP: no | clean_opts: 2 | defect_opts: 7
  - [Critical] The subject occupant is reported to be a tenant or unknown -> O-EPD-52927
  - [Critical] The appraisal was ordered by a party to the transaction -> O-EPD-52926
  - [Critical] Original value used to qualify not supported after a desk review, online search &/or retro appraisal -> O-EPD-52925
  - [Critical] The purchase price is substantially higher or lower than predominant market value -> O-EPD-52930
  - [Critical] The owner is someone other than the seller shown on sales contract -> O-EPD-52928
  - [Critical] The subject photos reveal inconsistencies -> O-EPD-52931
  - [Critical] The appraisal indicates the transaction is a refinance, but other documentation reflects a purchase -> O-EPD-52929

### PC::O-EPD-14460 | EPD | O-EPD
Q: Did the EPD review reveal any title default indicators?
APPLIES: (always)
SKIP: no | clean_opts: 2 | defect_opts: 4
  - [Critical] The chain of title includes an interested party -> O-EPD-52934
  - [Critical] The buyer has a pre-existing financial interest in the property -> O-EPD-52937
  - [Critical] The buyer and seller have the same surname indicating a concealed non-arm's length transaction -> O-EPD-52933
  - [Critical] The title policy was prepared for and/or was mailed to a party other than the lender -> O-EPD-52932

### PC::O-EPD-14461 | EPD | O-EPD
Q: Did the EPD review reveal any transaction/closing default indicators?
APPLIES: (always)
SKIP: no | clean_opts: 2 | defect_opts: 4
  - [Critical] Subject indicates compromised transaction such as a flip, foreclosure rescue, straw buyer refi etc -> O-EPD-52935
  - [Critical] Cash proceeds to the borrower were inconsistent with the final application and loan approval -> O-EPD-52940
  - [Critical] Undisclosed liens were paid off in a refinance transaction -> O-EPD-52938
  - [Critical] There are indications of payouts to unknown parties -> O-EPD-52939

### PC::O-EPD-14462 | EPD | O-EPD
Q: What additional observations were noted during the EPD review?
APPLIES: (always)
SKIP: no | clean_opts: 6 | defect_opts: 1
  - [Critical] EPD selection was not a risk-based sample that are 60 days or more past due in the first 6 months -> O-EPD-53874

### PC::O-FED-14309 | Certification, Endorsement, and Delivery | O-FED
Q: In a loan utilizing electronic delivery of documents, does the file evidence the consumer(s) consent to receive electronic delivery of documents and/or the consumer(s) and/or loan originators consent for electronic signatures prior to use?
APPLIES: (always)
SKIP: no | clean_opts: 2 | defect_opts: 2
  - [Critical] No, consent(s) for electronic signatures is not evidenced in the file -> O-ESIGN-50001
  - [Critical] No, consent(s) for electronic document delivery is not evidenced in the file -> O-ESIGN-50000

### PC::O-FED-14350 | Underwriting | O-FED
Q: Were all ECOA requirements met (part 1)?
APPLIES: (always)
SKIP: no | clean_opts: 1 | defect_opts: 7
  - [Critical] Alimony/child support/maintenance payments were included where not likely to be consistently made -> O-ECOA-53164
  - [Critical] Part time income/pension/annuity/retirement income was discounted or excluded from consideration -> O-ECOA-53163
  - [Critical] ECOA notice missing reasons for action or disclosure of right to specific reasons within 30 days -> O-ECOA-02035
  - [Critical] Applicant was not notified of action taken within 30 days after receiving a completed application -> O-ECOA-00582
  - [Critical] The applicant was not notified of action taken within 90 days of an unaccepted counteroffer -> O-ECOA-51103
  - [Critical] A Notice of Incompleteness (NOI) was not mailed within 30 days of the application date -> O-ECOA-51104
  - [Critical] Exceptions of creditworthiness that the UW used may constitute a discriminatory practice or effect -> O-ECOA-00584

### PC::O-FED-14351 | ATR-QM | O-FED
Q: Did the underwriter make a reasonable and good faith determination of the applicant(s) ability to repay in accordance with TILA requirements?
APPLIES: (always)
SKIP: yes | clean_opts: 1 | defect_opts: 2
  - [Critical] No, the payment calculation did not use monthly, fully amortizing, substantially equal payments -> O-TILA-55920
  - [Critical] No, the payment calculation did not use the greater of fully indexed rate/introductory interest rate -> O-TILA-01676

### PC::O-FED-14354 | ATR-QM | O-FED
Q: Does the loan satisfy all requirements for Qualified Mortgage (QM) status as defined by its relevant GSE?
APPLIES: (always)
SKIP: yes | clean_opts: 2 | defect_opts: 2
  - [Critical] No, the APR exceeded the price-based HPCT threshold for QM Safe Harbor -> O-TILA-56502
  - [Critical] No, the transaction does not meet the RHS qualified mortgage requirements -> O-TILA-56503

### PC::O-FED-14400 | Insurance | O-FED
Q: Are all federal flood insurance requirements met including minimum ratings?
APPLIES: (always)
SKIP: no | clean_opts: 2 | defect_opts: 12
  - [Critical] Loan approved even though the property is part of the Coastal Barrier Resource System -> O-FHA-00545
  - [Critical] No, the SFHDF does not correctly identify the borrowers/subject property address/lender/servicer -> O-FDPA-50004
  - [Critical] No, property is located in a SFHA and escrows were not established for collection of flood premiums -> O-FDPA-51089
  - [Critical] The flood insurance deductible requirements as per property type were not met -> O-FNM-56261
  - [Critical] No, the escrow account does not include premiums and fees for payment of the flood insurance policy -> O-FDPA-50001
  - [Critical] No, the Notice of Special Flood Hazard Area was not mailed or delivered to the borrower(s) -> O-FDPA-50002
  - [Critical] No, the SFHDF fee charged to the borrower exceeds the actual costs + life of loan monitoring fee -> O-FDPA-51091
  - [Critical] No, a complete and accurate SFHDF was not used to evaluate the loan for flood insurance requirements -> O-FDPA-51090
  - [Critical] No, sufficient flood coverage was not in effect as of the date of loan consummation -> O-FDPA-50000
  - [Critical] No, the Notice of Special Flood Hazard Area does not contain all required disclosure language -> O-FDPA-50003
  - [Critical] Private flood insurance policy does not meet the definition or include the prerequisite statement -> O-FDPA-51120
  - [Critical] Private flood policy discretionary acceptance requirements were not met -> O-FDPA-51800

### PC::O-FED-14466 | Closing | O-FED
Q: Were all ECOA closing requirements met?
APPLIES: (always)
SKIP: no | clean_opts: 2 | defect_opts: 2
  - [Critical] No, a copy of the appraisal was not provided promptly, or three business days prior to closing -> O-ECOA-00440
  - [Critical] No, a signed appraisal delivery waiver was not obtained at least 3 business days prior to closing -> O-ECOA-51099

### PC::O-FED-14507 | ATR-QM | O-FED
Q: Were all federal Higher-Priced Mortgage Loan (HPML) requirements met?
APPLIES: (always)
SKIP: yes | clean_opts: 2 | defect_opts: 5
  - [Critical] An escrow account was not established for mortgage-related taxes & insurance for this HPML -> O-TILA-50011
  - [Critical] A written appraisal was not obtained in a higher-priced mortgage loan transaction -> O-TILA-01776
  - [Critical] HPML on potential flipped property approved w/out 2 qualified appraisals to justify the sales price -> O-TILA-01777
  - [Critical] Consumer charged for the 2nd appraisal required in a HPML on a potentially flipped property -> O-TILA-58249
  - [Critical] A copy of each appraisal was not provided to the consumer no later than 3 bus days prior to closing -> O-TILA-54206

### PC::O-FED-15820 | Underwriting | O-FED
Q: Were all ECOA requirements met (part 2)?
APPLIES: (always)
SKIP: no | clean_opts: 1 | defect_opts: 4
  - [Critical] The UW decision was based on subjective standards that can result in discriminatory effects -> O-ECOA-00583
  - [Critical] Use of assumptions or aggregate statistics relating to child bearing was part of the evaluation -> O-ECOA-53162
  - [Critical] The UW evaluated married and unmarried applicants by different standards -> O-ECOA-00585
  - [Critical] The UW may have considered race, color, religion, national origin or sex in evaluating an applicant -> O-ECOA-00586

### PC::O-FED-15842 | Credit - Liabilities | O-FED
Q: Were all FCRA underwriting requirements met?
APPLIES: (always)
SKIP: yes | clean_opts: 2 | defect_opts: 3
  - [Critical] Reasonable steps or specified ph# not used to verify active duty alert from consumer credit report -> O-FCRA-51725
  - [Critical] Reasonable steps or specified ph# not used to clear identity theft/fraud extended alert -> O-FCRA-52834
  - [Critical] Reasonable steps or specified ph# not used to verify initial fraud alert from consumer credit report -> O-FCRA-51724

### PC::O-FNM-00525 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #8 - Was the appraisal completed on an acceptable report form as applicable?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-00525

### PC::O-FNM-00531 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #16, #17, #18 - Were all exhibits included in the appraisal as applicable including but not limited to the building sketch or floor plan including dimensions and calculations, location map, and the required number of photographs including, the living room, family room, dining room, all bedrooms, and all finished and unfinished areas of the basement?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-00531

### PC::O-FNM-00534 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #14 - Was it validated that the appraisal market trends were identified correctly?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-00534

### PC::O-FNM-00705 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #19 - Was a certification of completion/inspection provided where the appraisal is subject to completion per plans and specifications or subject to repairs or alterations?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-00705

### PC::O-FNM-14152 | Credit - Liabilities | O-FNM
Q: (Fannie Mae) Was a credit report in the loan file for each applicant responsible for loan repayment?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 2
  - [Critical] No, a credit report is missing for at least one applicant(s) -> O-FNM-00179
  - [Critical] No, there are no credit report(s) in the file -> O-FNM-58076

### PC::O-FNM-14370 | Property - Appraisal | O-FNM
Q: (Fannie Mae) Is there an appraisal in the file?
APPLIES: Loans.QC_Policy = 'Fannie Mae'
SKIP: no | clean_opts: 4 | defect_opts: 1
  - [Critical] No, the loan file did not contain an appraisal report as required -> O-FNM-50902

### PC::O-FNM-14387 | Data Validation Svc-DVS | O-FNM
Q: Were all general requirements met where components of the loan received DU Validation Reps & Warrants Relief?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 8
  - [Critical] Authorization from the borrower to receive the information from the vendor was not obtained -> O-FNM-50822
  - [Critical] The vendor report did not match the borrower information provided -> O-FNM-50823
  - [Critical] The information entered by the lender in DU was not properly documented -> O-FNM-50824
  - [Critical] The vendor report was not in the file -> O-FNM-50820
  - [Critical] The vendor report supplier/distributor was not on FNMA's listing of authorized suppliers -> O-FNM-50821
  - [Critical] All conflicting or contradictory information was not investigated and resolved -> O-FNM-50825
  - [Critical] Updated verification report not resubmitted or did not receive component validation message -> O-FNM-50828
  - [Critical] The most current version of the verification report was not used by the DU validation service -> O-FNM-50826

### PC::O-FNM-14388 | Data Validation Svc-DVS | O-FNM
Q: Were all income DU Validation requirements met to maintain Reps & Warrants Relief?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 10
  - [Critical] Income/employ validated with an asset verif report w/out 12 mos data from eligible 3rd party vendor -> O-FNM-57667
  - [Critical] Difference between DU calculated income & income provided by the lender exceed allowable tolerance -> O-FNM-50836
  - [Critical] File missing the Employment and Income Verification Report for validated commission income -> O-FNM-50830
  - [Critical] Missing Employment & Income Verification Report for validated base, bonus, OT or commission < 25% -> O-FNM-50829
  - [Critical] File missing a tax transcript where validated income is from retirement (annuities and pension) -> O-FNM-50831
  - [Critical] File missing tax transcript for validated self-employed income (1040, C or C-EZ sole propriet only) -> O-FNM-50833
  - [Critical] Validated SS (retire, disability, supp, survivor) missing tax transcript/addt'l docs per SSI type -> O-FNM-50832
  - [Critical] VOI was validated but VOE was not, the associated income not documented as per req's -> O-FNM-50835
  - [Critical] All income shown on the Income Verification Report was not reflected in U.S. dollars -> O-FNM-55909
  - [Critical] The full asset verification report used to validate income/employment is not in the file -> O-FNM-57668

### PC::O-FNM-14389 | Data Validation Svc-DVS | O-FNM
Q: Were all employment DU requirements met to maintain Reps & Warrants Relief?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 9
  - [Critical] Employment & income verification reports did not meet age of credit document requirements -> O-FNM-50837
  - [Critical] LoanBeam SEI 1084 not in the file &/or related DU msgs not met for SE calculation relief -> O-FNM-51716
  - [Critical] A manual verification report was used to achieve employment and income validation -> O-FNM-53786
  - [Critical] Req's not met to retain income validation where employment was reverified and not re-validated in DU -> O-FNM-50947
  - [Critical] Employment not validated by DU & the file did not contain a VVOE within 10 business days of closing -> O-FNM-50834
  - [Critical] All req'd information was not confirmed in manual review of the supplemental asset employment report -> O-FNM-58123
  - [Critical] Manual review of supplemental asset employ report not obtained in same timeframe req'd for a VVOE -> O-FNM-58122
  - [Critical] Employ validated w/ asset verif rep Close by Date exp & supplemental rep did not contain req'd info -> O-FNM-58120
  - [Critical] Supplemental asset employ verification obtained with contradictory/conflicting info not resolved -> O-FNM-58121

### PC::O-FNM-14390 | Data Validation Svc-DVS | O-FNM
Q: Were all asset DU requirements met to maintain Reps & Warrants Relief?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 11
  - [Critical] Actual funds to close exceeds funds in DU & assets to cover not in file &/or not resub if applicable -> O-FNM-50843
  - [Critical] Business act on verification report, no cash flow analysis to confirm use will not have neg impact -> O-FNM-50844
  - [Critical] Business asset not removed/Verif Report not updated/resub & cash analysis shows neg impact business -> O-FNM-50845
  - [Critical] VOA with gift funds and the gift not verified as per the DU validation message -> O-FNM-54170
  - [Critical] File missing the most recent quarter for accounts that are reported on a quarterly basis -> O-FNM-50841
  - [Critical] Purchase - account statements from the vendor did not cover most recent 60 days of account activity -> O-FNM-50840
  - [Critical] Refinance - account statements from the vendor did not cover most recent 30 days of account activity -> O-FNM-50839
  - [Critical] The asset verification report was not in the file -> O-FNM-55435
  - [Critical] Retirement account did not meet withdrawal requirements & were not removed and resubmitted to DU -> O-FNM-50846
  - [Critical] The assets entered for validation included amounts from employment related assets -> O-FNM-50838
  - [Critical] DU message that a large deposit requires documentation, the applicable documentation not in the file -> O-FNM-50842

### PC::O-FNM-14391 | Data Validation Svc-DVS | O-FNM
Q: Were all appraised value requirements met to maintain Reps & Warrants Relief?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 3
  - [Critical] The appraisal CU risk score was not 2.5 or lower or an appraisal waiver was not offered -> O-FNM-50849
  - [Critical] Basic appraisal information incomplete/inaccurate such as subject description, condition, photos -> O-FNM-50850
  - [Critical] Missing Cert of completion/Form 1004D where subject to completion & CU risk score of 2.5 or less -> O-FNM-50851

### PC::O-FNM-14797 | Data Validation Svc-DVS | O-FNM
Q: If the use of rent payment history was utilized in the DU credit risk assessment, were all requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 7
  - [Critical] Positive rent data used & the rent pymt in DU did not align with withdrawal amts in the VOA report -> O-FNM-55307
  - [Critical] Positive rent data used by DU without reviewing last 60 days of account activity for large deposits -> O-FNM-55101
  - [Critical] Positive rent data used & no asset verification report w/ 12 mos bank data by a DU validation vendor -> O-FNM-55100
  - [Critical] Positive rent data used by DU without at least 1 borr being a 1st time homebuyer with a credit score -> O-FNM-55097
  - [Critical] Positive rent data used by DU in a loan that is not a purchase secured by a principal residence -> O-FNM-55099
  - [Critical] Positive rent data used by DU & borr has not rented for at least 12 mos w/ rent of at least $300 -> O-FNM-55098
  - [Critical] Borr moved or had a rent pymt change, & the former address sect not used to enter the previous rent -> O-FNM-56237

### PC::O-FNM-15303 | Application | O-FNM
Q: Were all initial Uniform Residential Loan Application requirements met?
APPLIES: Loans.QC_Policy = 'Fannie Mae'
SKIP: no | clean_opts: 1 | defect_opts: 1
  - [Major] The file did not include a fully completed Supplemental Consumer Information Form (Form 1103) -> O-FNM-56132

### PC::O-FNM-15304 | Application | O-FNM
Q: Were all final Uniform Residential Loan Application requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 1 | defect_opts: 4
  - [Critical] Final application not in the file or is incomplete, incorrect or not dated & signed by all parties -> O-FNM-50002
  - [Major] All sections of URLA Additional Borrower form not fully completed, correct &/or signed as applicable -> O-FNM-58197
  - [Major] It appears the borr needed more space to complete the URLA & a continuation sheet not in the file -> O-FNM-58198
  - [Major] Unmarried Addendum not completed as applicable when borrower selects "unmarried" in section 1 -> O-FNM-58196

### PC::O-FNM-15305 | Credit - Liabilities | O-FNM
Q: Were all credit score requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 3
  - [Major] Representative or average median score not used as req'd per number of borrowers in a manual UW -> O-FNM-55988
  - [Critical] Minimum credit score requirements were not met -> O-FNM-51042
  - [Critical] The incorrect representative credit score was used in a manually underwritten loan -> O-FNM-00192

### PC::O-FNM-15306 | Credit - Liabilities | O-FNM
Q: Were all credit report requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 7
  - [Critical] Data entered into DU is inaccurate based on credit report/other credit documentation -> O-FNM-00199
  - [Major] The borr's present address not within the U.S. or military address and was not manually underwritten -> O-FNM-56945
  - [Major] RMCR does not reflect a reporting status <= 90 days of the report date for accounts with balances -> O-FNM-00189
  - [Critical] Credit report not an original with all required identifying information &/or alterations noted -> O-FNM-00185
  - [Critical] Disputed account reported and DU has a disputed message that was not documented as resolved -> O-FNM-50010
  - [Critical] DU loan does not contain a three-in-file merged credit report for each applicant -> O-FNM-00182
  - [Critical] Non-traditional credit was used; sufficient number of credit references warrants traditional credit -> O-FNM-00181

### PC::O-FNM-15307 | Credit - Liabilities | O-FNM
Q: Were all traditional credit history requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 8
  - [Critical] Determination of new debt from inquiries reported within 90-days of closing is not documented -> O-FNM-00188
  - [Critical] Loan approval does not evidence satisfactory credit risk for serious adverse credit reported -> O-FNM-00200
  - [Critical] Late rental and/or mortgage payment reported/verified does not meet guidelines -> O-FNM-50015
  - [Critical] Authorized user accts included without evidence borrower solely paid for last 12 mos in manual UW -> O-FNM-50267
  - [Critical] The pattern of using revolving credit to the max limit credit mgt risk not evaluated in manual UW -> O-FNM-50266
  - [Critical] Mortgage not reported and verification of satisfactory pay history is missing -> O-FNM-00195
  - [Critical] Re-established credit not documented where significant derogatory credit events are reported -> O-FNM-00201
  - [Critical] Required documentation missing for a bankruptcy/foreclosure action reported in the last 7 years -> O-FNM-00198

### PC::O-FNM-15308 | Credit - Liabilities | O-FNM
Q: Were all nontraditional credit history requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 9
  - [Critical] Borr w/ credit score had 50% or less qual income & no non-trad credit for borr w/out a credit score -> O-FNM-58788
  - [Critical] Non-purchase/LCO of 1-4 unit, all bwrs occupy: No bwr had DU credit score or 1 credit/install acct -> O-FNM-58787
  - [Critical] Nontraditional credit used & loan was not a fixed rate meeting conforming baseline loan limits -> O-FNM-56149
  - [Critical] Nontraditional credit was used for a subject property that is not a 1-4 unit principal residence -> O-FNM-56147
  - [Critical] Nontraditional credit was used in a transaction other than a purchase or limited cash-out refinance -> O-FNM-56148
  - [Critical] 12 mos reserves not verified where nontraditional credit was used for borr's w/out a housing history -> O-FNM-57520
  - [Critical] The number of non-traditional accts insufficient or from an ineligible source -> O-FNM-50269
  - [Critical] An unacceptable source was used to verify the nontraditional housing payments -> O-FNM-57519
  - [Critical] Nontraditional references not verified without DU allowing a 3rd party asset verification report -> O-FNM-56150

### PC::O-FNM-15309 | Credit - Liabilities | O-FNM
Q: Were all debt-to-income (DTI) ratio requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 2
  - [Critical] Not re-underwritten where additional debt or reduced income caused DTI to increase beyond tolerance -> O-FNM-00722
  - [Critical] Loan approved with DTI over 36% and borrower does not meet credit and reserve requirements -> O-FNM-00724

### PC::O-FNM-15310 | Credit - Liabilities | O-FNM
Q: Were all monthly housing requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 3
  - [Critical] PITIA of other properties owned by the borrower were not included in DTI as applicable -> O-FNM-56073
  - [Critical] Monthly PITIA not calculated correctly &/or did not include all housing components -> O-FNM-51043
  - [Critical] Subject 2nd or investment & borr rents current residence, rent not documented &/or in housing ratio -> O-FNM-55880

### PC::O-FNM-15311 | Credit - Liabilities | O-FNM
Q: Were all monthly debt obligations requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 11
  - [Major] AUS loan with alimony pymts reducing income in lieu of debt not in DU as own negative amt line item -> O-FNM-51834
  - [Critical] Divorce decree or equivalent not in file to document alimony, child support, or maintenance payments -> O-FNM-50005
  - [Critical] Alimony, child support, or maintenance payments with over 10 months left was not considered in DTI -> O-FNM-51833
  - [Critical] Business debt(s) not included in DTI or documentation debt(s) is paid by the business is missing -> O-FNM-50006
  - [Critical] A debt paid by someone other than the borrower was excluded without a 12 month timely pay history -> O-FNM-03139
  - [Critical] Deferred/forbearance student loan with no pymt reported & 1% of balance or documented pymt not used -> O-FNM-50018
  - [Critical] Deferred non-student loan installment debt(s)/no payment is not documented and/or included in DTI -> O-FNM-50009
  - [Critical] There are federal income taxes due on the current year tax return and proof paid has not been obtain -> Tax Liability
  - [Critical] Lease payment(s) excluded from total monthly debt, regardless of lease term remaining -> O-FNM-50016
  - [Critical] Loans/deductions listed on the paystubs were not addressed -> Paystub Loans
  - [Critical] Asset secured loan is not included in DTI or a copy of the Note reflecting the collateral is missing -> O-FNM-50017

### PC::O-FNM-15312 | Credit - Liabilities | O-FNM
Q: Were all debts paid off at or prior to closing requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 6
  - [Critical] Documentation of assets to cover a 30-day account, in excess of reserves/closing funds, is missing -> O-FNM-50004
  - [Critical] Non-medical charge-offs on non-mtg accts of $250 or more or total balances exceed $1,000 not PIF -> O-FNM-50007
  - [Critical] Non-medical collections on non-mtg accts of $250 or more or total balances exceed $1,000 not PIF -> O-FNM-50008
  - [Critical] All debts were not paid off at or prior to closing -> DEBTS-PAID
  - [Critical] UW did not require outstanding judgment(s) be satisfied prior to or at closing -> O-FNM-50014
  - [Critical] Debt paid off or paid down to qualify & source/sufficient assets remain for the loan not provided -> O-FNM-57256

### PC::O-FNM-15313 | Income | O-FNM
Q: Were all employment income requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 7
  - [Critical] Employed by a family member/interested party & the most recent years tax returns were not provided -> O-FNM-50011
  - [Critical] Income submitted to AUS is not accurate - broken out and/or categorized correctly -> Income Breakdown
  - [Critical] Income calculation requirements were not met -> O-FNM-50815
  - [Critical] Income is declining and no explanation has been provided -> DecliningIncDocument
  - [Critical] Income has a defined expiration date & documentation verifying 3 year continuance was not provided -> O-FNM-00439
  - [Critical] Variable income used, history of receipt, frequency and trending of the amount were not provided -> O-FNM-00352
  - [Critical] Income that is paid to the borrower in virtual currency was used for qualification -> O-FNM-55678

### PC::O-FNM-15314 | Income | O-FNM
Q: Were all employment documentation requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 10
  - [Critical] The paystubs/W2's did not clearly identify the borrower as the employee -> O-FNM-50250
  - [Critical] The paystubs and/or W2's were incomplete or were illegible -> O-FNM-52819
  - [Critical] Gaps in employment were not addressed as required -> EmploymentGaps
  - [Major] The income calculation worksheet is not located in the file or is incomplete/inaccurate -> IncomeWork
  - [Critical] The employer did not complete all required fields on the standard VOE form 1005 -> O-FNM-00334
  - [Critical] The W2's obtained did not cover the number of years that were required -> O-FNM-50249
  - [Critical] Paystub not within 30 days &/or did not have YTD earnings or sufficient pay info to calculate income -> O-FNM-00335
  - [Critical] Paystubs and W2's source was not a third party ex: HR, payroll, personnel dept, payroll vendor etc -> O-FNM-52820
  - [Major] The net rental income/loss worksheet was not utilized when applicable -> RentalCalcDoc
  - [Critical] 3rd party employment verification was used but documentation does not meet Fannie Mae's requirements -> O-FNM-00336

### PC::O-FNM-15315 | Income | O-FNM
Q: Were all base pay (salary and hourly), bonus, tip, and overtime income requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 5
  - [Critical] File does not contain a completed VOE or the most recent paystub & two years W-2s or as per DU -> O-FNM-00346
  - [Critical] Combination of paystub and previous 2 yrs W2s or a VOE to verify bonus and OT income not provided -> O-FNM-00347
  - [Critical] Income used did not have 2 yr history & no comp factors given to offset the shorter income history -> O-FNM-00333
  - [Critical] Verification that the OT/bonus income has been received for the last two years was not provided -> O-FNM-00338
  - [Critical] Documentation verifying the applicant has received tip income for the previous 2 yrs not provided -> O-FNM-00339

### PC::O-FNM-15316 | Income | O-FNM
Q: Were all commission income requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] Combination of paystub and previous 2 yrs W-2s or a VOE to verify commission income not provided -> O-FNM-00348

### PC::O-FNM-15317 | Income | O-FNM
Q: Were all secondary and seasonal employment income requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 3
  - [Critical] Secondary employment has a gap of over 1 month in last 12 mos & employment not changed to seasonal -> O-FNM-54120
  - [Critical] Last 2 years of seasonal work not documented or as per DU -> O-FNM-00341
  - [Critical] Documentation verifying 2nd job income has been uninterrupted for the previous 2 yrs not provided -> O-FNM-00340

### PC::O-FNM-15318 | Income | O-FNM
Q: Were all IRS Form 4506-C requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 4
  - [Critical] Steps not taken to confirm borr identity & escalated as applicable for IRS 4506-C Code 10 rejection -> O-FNM-55722
  - [Critical] Non Code 10 IRS rejection & evidence of attempts to get a corrected & signed 4506-C not in the file -> O-FNM-55308
  - [Major] The 4506C screen in EPIC is incomplete or incorrect (IE. Record of Account) -> Epic4506C
  - [Major] 4506-C not completed & signed prior to or at closing for each borrower whose income used to qualify -> O-FNM-00045

### PC::O-FNM-15319 | Income | O-FNM
Q: Were all verbal verification of employment requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 10
  - [Critical] Vendor for 3rd party VOE was not Equifax/TWN or manual process not followed -> 3rdParty
  - [Critical] Missing employer work email exchange dated within 10 business days PTC for alternative VOE method -> O-FNM-55906
  - [Critical] File did not confirm the employer email address is accurate for an alternative VOE method -> O-FNM-55907
  - [Critical] Alternative VOE method employer email did not include all required information -> O-FNM-55908
  - [Critical] VVOE not obtained or not dated within 120 calendar days of the note date for self-employed income -> O-FNM-53031
  - [Critical] Third-party vendor database data used to obtain the VVOE was older than 35 days of the note date -> O-FNM-52165
  - [Critical] The verbal verification of employment does not show borrower in an active status -> VVOE Inactive
  - [Critical] A VVOE was not obtained or was not dated within 10 business days of the note date -> O-FNM-00351
  - [Critical] VVOE alt bank stmnts not within 15 business days before the note &/or do not contain all req'd info -> O-FNM-57389
  - [Critical] VVOE alt paystub not within 15 business days before the note &/or does not contain all req'd info -> O-FNM-57388

### PC::O-FNM-15320 | Income | O-FNM
Q: Were all rental income requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 11
  - [Major] Rental income from a 1 unit w/ an ADU or 2-4 unit primary was not entered as Accessory Unit Income -> O-FNM-57986
  - [Critical] The file did not contain FNMA Form 1007 or Form 1025, as applicable, or did not meet all form req's -> O-FNM-57316
  - [Critical] Form 1007/1025 not provided & lease terms were not in effect with receipt of 2 months rental pymts -> O-FNM-57317
  - [Critical] The lease transferred to the borr impacts first lien position or enforceability of the subject loan -> O-FNM-52892
  - [Critical] Gross rents & expenses through a partnership or S corp & business return w/ form 8825 not provided -> O-FNM-55656
  - [Critical] Rental income analysis & documentation based on the time the rental was in service was inappropriate -> O-FNM-55655
  - [Critical] Where there is partial or no rental history, reconciliation &/or documentation req's were not met -> O-FNM-57318
  - [Critical] Rental income req's for current housing exp & rental history for 1-4 or 2-4 transactions not met -> O-FNM-51850
  - [Critical] Rental income calculated incorrectly &/or not added to income or debts -> O-FNM-50252
  - [Critical] Correct documents not used to calculate rental income as per rent history, property & loan type -> O-FNM-00433
  - [Critical] A lease was used in place of IRS Form 1040, Sch E, to document rental income without justification -> O-FNM-00434

### PC::O-FNM-15321 | Income | O-FNM
Q: Were all automobile allowance requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 4
  - [Critical] Documentation verifying borrower has received auto allowance for at least 2 yrs was not provided -> O-FNM-00342
  - [Critical] Full lease/debt pymt not added to the debt obligations as applicable for an automobile allowance -> O-FNM-55663
  - [Critical] Auto allowance was considered stable income & full amt of allowance was not added to monthly income -> O-FNM-55662
  - [Critical] Income submitted to AUS is not accurate - broken out and/or categorized correctly -> Income Breakdown

### PC::O-FNM-15322 | Income | O-FNM
Q: Were all retirement income requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 9
  - [Critical] Incorrect percentage used to "gross up" the verified nontaxable social security income as applicable -> O-FNM-57444
  - [Critical] More than 15% was used to "gross up" SSI without documentation to support the income is nontaxable -> O-FNM-57445
  - [Critical] Income submitted to AUS is not accurate - broken out and/or categorized correctly -> Income Breakdown
  - [Critical] Retirement, annuity or pension not verified using allowable documentation or as required by DU -> O-FNM-00420
  - [Critical] Retirement, annuity, pension income used w/out evidence borr has unrestricted access w/out penalty -> O-FNM-54029
  - [Critical] Retirement income from a 401(k), IRA, or Keogh acct without 3 yr continuance -> O-FNM-54030
  - [Critical] Missing award letter, 3 yr cont & receipt of SSI drawn from another's acct or own to benefit another -> O-FNM-55987
  - [Critical] SSI from another person's acct or for a dependent was used to qualify w/out a 3- yr continuance -> O-FNM-55660
  - [Critical] File is missing the SSA award letter, SSA-1099, last signed tax returns or proof of current receipt -> O-FNM-00419

### PC::O-FNM-15323 | Income | O-FNM
Q: Were all alimony, child support, maintenance, or other nontaxable income requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 7
  - [Critical] Documentation verifying alimony/child support income will continue for at least 3 years not provided -> O-FNM-00421
  - [Critical] Minimum of 6 mos alimony/child support/maintenance full & timely pay history not provided -> O-FNM-55661
  - [Critical] The "grossed up" calculation for child support income was not calculated correctly -> O-FNM-57443
  - [Critical] Income submitted to AUS is not accurate - broken out and/or categorized correctly -> Income Breakdown
  - [Critical] Alimony, child support, maintenance not on 1003 & not requested by borrower to use as income -> O-FNM-54027
  - [Critical] Other types of nontaxable income were considered without documents to verify nontaxable status -> O-FNM-58797
  - [Critical] The "grossed up" calculation of other nontaxable income was not calculated correctly -> O-FNM-58800

### PC::O-FNM-15324 | Income | O-FNM
Q: Were all unemployment income requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 2
  - [Critical] Unemployment income used was not clearly associated with seasonal income as per the tax returns -> O-FNM-52800
  - [Critical] Unemployment income used w/out 2 yrs signed tax returns documenting consistent receipt or as per DU -> O-FNM-00422

### PC::O-FNM-15325 | Income | O-FNM
Q: Were all disability income requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] Missing long term disability eligibility confirmation, amount, frequency & end date or as per DU -> O-FNM-00423

### PC::O-FNM-15326 | Income | O-FNM
Q: Were all housing assistance income requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 4
  - [Critical] Housing/Parsonage income receipt for last 12 mths and/or continuance for next 3 years not documented -> O-FNM-50013
  - [Critical] Income submitted to AUS is not accurate - broken out and/or categorized correctly -> Income Breakdown
  - [Critical] Section 8 vouchers-Voucher from public housing agency stating payment amount & duration not obtained -> O-FNM-50012
  - [Major] Section 8 housing voucher income is nontaxable and an adjusted gross income was not developed -> O-FNM-57790

### PC::O-FNM-15327 | Income | O-FNM
Q: Were all anticipated income requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 5
  - [Critical] Employment start date within 30 days prior to the Note date missing offer/contract & paystub or VVOE -> O-FNM-51829
  - [Critical] Employment start date is within 90 days after Note date missing an employment offer/contract -> O-FNM-51830
  - [Critical] Anticipated income-w/out new paystub & loan feature, financial resource & reserve req's not met -> O-FNM-51831
  - [Critical] Anticipated income-start date greater than 30 days prior to or greater than 90 days after Note date -> O-FNM-51832
  - [Critical] The offer or contract for employment is by a family member or interested party to the transaction -> O-FNM-57264

### PC::O-FNM-15328 | Income | O-FNM
Q: Were all business income requirements met?
APPLIES: Loans.QC_Policy = 'Fannie Mae'
SKIP: yes | clean_opts: 2 | defect_opts: 3
  - [Critical] Underwriter did not provide a written analysis of the applicant's business income -> O-FNM-00386
  - [Critical] Most recent 2yrs signed bus. tax returns, including all schedules/tax transcripts not provided -> O-FNM-00379
  - [Critical] 1 yr business tax returns used where business existence or at least 25% ownership is less than 5 yrs -> O-FNM-57320

### PC::O-FNM-15329 | Income | O-FNM
Q: Were all self-employed requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 13
  - [Critical] Income submitted to AUS is not accurate - broken out and/or categorized correctly -> Income Breakdown
  - [Critical] Income calculation requirements were not met -> O-FNM-50815
  - [Critical] Qualifying income used the amount calculated by Income Calculator, addt'l lender req's were not met -> O-FNM-57386
  - [Critical] Where the Income Calculator was used, the Income Calculator findings report was not in the file -> O-FNM-57385
  - [Critical] The Income Calculator was used, and qualifying income exceeded the amount calculated by the tool -> O-FNM-57387
  - [Critical] Income is declining and no explanation has been provided -> DecliningIncDocument
  - [Critical] Meals and Entertainment & Mtg < 1 Yr not deducted -> SE Deductions
  - [Major] Documentation from a third party provider for the borrower’s business was not provided -> IncomeSEVerification
  - [Critical] Self-employed income calculated incorrectly and the optional Income Calculator tool was not used -> O-FNM-59117
  - [Critical] Underwriter did not provide a written analysis of the applicant's individual tax returns -> O-FNM-00384
  - [Critical] 1 yr personal tax returns used where business existence or at least 25% ownership is less than 5 yrs -> O-FNM-57319
  - [Critical] Documentation demonstrating the K-1 income may be used to qualify was not provided -> O-FNM-02573
  - [Critical] Most recent 2yrs signed tax returns, including all applicable schedules/tax transcripts not provided -> O-FNM-00378

### PC::O-FNM-15330 | Income | O-FNM
Q: Were all other income requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 12
  - [Critical] Boarders-Documentation verifying history of shared residency/rent payment for 12 mos not provided -> O-FNM-00432
  - [Critical] Foster care is considered without all required documentation and terms being met -> O-FNM-00431
  - [Critical] Income submitted to AUS is not accurate - broken out and/or categorized correctly -> Income Breakdown
  - [Critical] Income calculation requirements were not met -> O-FNM-50815
  - [Critical] SSI has been grossed up without proper documentation supporting it -> Income - Other
  - [Critical] Interest & dividend-Copies of tax returns or account statements verifying 2 yrs receipt not provided -> O-FNM-00427
  - [Critical] The file does not contain a written verification from the employer for the employer's subsidy -> O-FNM-00429
  - [Critical] Notes Receivable-Note & deposit slips/tax returns/bank stmts documenting 12 mo receipt not provided -> O-FNM-00428
  - [Critical] Rental income from a live-in personal assistant for a disabled borrower exceeded 30% of gross income -> O-FNM-55664
  - [Critical] Public assistance-Letters/exhibits from paying agency stating amt, frequency & duration not provided -> O-FNM-00424
  - [Critical] Temporary leave income used and the income does not meet Fannie Mae's requirements -> O-FNM-00425
  - [Critical] A letter or distribution form from VA stating the benefits will continue for 3 yrs was not provided -> O-FNM-00430

### PC::O-FNM-15331 | Income | O-FNM
Q: Were all additional other income requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 10
  - [Critical] In a loan relying on capital gains, file does not contain signed tax returns for the past two years -> O-FNM-00436
  - [Critical] LTV over 70% or 80% if owner is at least 62 years old where employment related assets used as income -> O-FNM-51012
  - [Critical] Monthly amt of employment related assets as income calculated incorrectly &/or req's for use not met -> O-FNM-54028
  - [Critical] The file did not contain 2 years tax returns including foreign income -> O-FNM-55665
  - [Critical] Foreign income was used without being translated to U.S. dollars -> O-FNM-55666
  - [Critical] Virtual currency was considered as an asset based income type -> O-FNM-55677
  - [Critical] Non-occupant borrower income used in manual UW with an unacceptable LTV and is a NOO residence -> O-FNM-00438
  - [Critical] A copy of the mortgage credit certificate was not provided -> O-FNM-00435
  - [Critical] Royalty-Tax returns, contract/alt documentation and 12 mo receipt with 3 yr continuance not provided -> O-FNM-00437
  - [Critical] K-1 income shows < 25% ownership and documentation demonstrating the income may be used not provided -> O-FNM-02572

### PC::O-FNM-15332 | Assets | O-FNM
Q: Were all minimum reserve requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 2
  - [Critical] Reserves are insufficient based on the subject loan characteristics or as was required by DU -> O-FNM-50255
  - [Critical] The financial assets provided for reserves were from an unacceptable source -> O-FNM-50254

### PC::O-FNM-15333 | Assets | O-FNM
Q: Were all interested party contributions requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 9
  - [Critical] IPC's were used for down payment, reserves req's, or to meet minimum borrower contribution -> O-FNM-00833
  - [Critical] Interested party contribution does not reflect consistent fees/expenses/resolution of discrepancies -> O-FNM-00577
  - [Critical] IPCs of non-realty items paid prior to, at or after closing were not considered as sales concessions -> O-FNM-59274
  - [Critical] The loan includes an interested party funded payment abatement -> O-FNM-59273
  - [Critical] Lender gave cash-like incentive that did not meet req's &/or did not document no repayment is req'd -> O-FNM-55111
  - [Critical] Lender incentive paying off a portion of the loan being refinanced & subject is not a high LTV refi -> O-FNM-55112
  - [Critical] Financing concessions over limit are sales concessions not deducted from sales price/LTV not recalc -> O-FNM-00706
  - [Critical] Premium pricing credit applied to down pymt &/or exceeded the amt needed to offset the closing costs -> O-FNM-55630
  - [Critical] There is evidence of undisclosed IPC's resulting in the loan being ineligible for sale to Fannie Mae -> O-FNM-59271

### PC::O-FNM-15334 | Assets | O-FNM
Q: Were all verification of deposit assets requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 6
  - [Critical] The bank statements did not include all account identifying information -> O-FNM-50257
  - [Critical] Funds recently deposited in US bank by non-US citizen were not sourced -> O-FNM-50260
  - [Critical] Source of unknown deposit exceeding 50% of qualifying income not documented &/or account not reduced -> O-FNM-00215
  - [Critical] LCO or CO refinance missing the last 1 month of bank or investment portfolio statements -> O-FNM-54872
  - [Critical] The VOD form was incomplete or not provided direct from the depository -> O-FNM-50256
  - [Critical] No, a VOD or account statement verifying each account not provided -> O-FNM-00214

### PC::O-FNM-15335 | Assets | O-FNM
Q: Were all retirement account asset requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 2
  - [Critical] No evidence vested funds for down pymt/closing/reserves are allowed regardless of employment status -> O-FNM-00289
  - [Critical] Retirement statements were not most recent and vested bal/terms not noted -> O-FNM-50258

### PC::O-FNM-15336 | Assets | O-FNM
Q: Were all gift and/or grant asset requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 11
  - [Critical] Gift funds were not entered correctly into DU and/or they were not identified separately as a gift -> O-FNM-00240
  - [Critical] The gift letter was not in the file or was unsigned and/or all required information not provided -> O-FNM-00234
  - [Critical] Gift of equity not documented with a signed gift letter &/or not included on the closing statement -> O-FNM-00241
  - [Critical] A gift of equity was used as financial reserves -> O-FNM-53864
  - [Major] Gift used as own funds by donor living w/ borr last 12 mos no evidence both will occupy as primary -> O-FNM-55982
  - [Major] The grant funds award letter or legal agreement and transfer of funds is not in the file -> O-FNM-57880
  - [Major] The grant funds are not submitted under borrower number 1 -> FNM-GrantSub
  - [Critical] Pooled gift funds to meet down pymt req, no cert donor has lived w/ borr for 12 mos & will continue -> O-FNM-51038
  - [Critical] Donor ability &/or the gift transfer to the borr’s account or to the closing agent not documented -> O-FNM-00235
  - [Critical] The grant funds were from an unacceptable entity -> O-FNM-00237
  - [Critical] Gift funds/gift of equity were received from an unacceptable donor -> O-FNM-51037

### PC::O-FNM-15337 | Assets | O-FNM
Q: Were all employer assistance asset requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] Employer financing provided without the file documenting that the terms meet FNMA req’s -> O-FNM-00281

### PC::O-FNM-15338 | Assets | O-FNM
Q: Were all earnest money deposit asset requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae' AND Loans.LoanPurposeType = 'Purchase')
SKIP: yes | clean_opts: 2 | defect_opts: 3
  - [Critical] Earnest money deposit not entered correctly in DU based on if EMD cleared the borr's bank account -> O-FNM-00218
  - [Critical] The earnest money deposit was not verified as required -> O-FNM-50262
  - [Critical] The past 2 month average did not support the amount of the earnest money deposit paid -> O-FNM-50261

### PC::O-FNM-15339 | Assets | O-FNM
Q: Were all anticipated sales proceeds asset requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 4
  - [Critical] Anticipated sale proceeds calculated incorrectly for an owned home listed for sale but not yet sold -> O-FNM-00278
  - [Critical] Signed employee relocation buy-out agreement not in the file -> O-FNM-51041
  - [Critical] Like-kind/1031 exchange assets not documented or not compliant with Internal Revenue Code Sect 1031 -> O-FNM-51040
  - [Critical] Settlement statement documenting sufficient net cash proceeds from a property sale not in the file -> O-FNM-51039

### PC::O-FNM-15340 | Assets | O-FNM
Q: Were all trade equity asset requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No, documentation showing the trade equity meets Fannie Mae's requirements not provided -> O-FNM-00285

### PC::O-FNM-15341 | Assets | O-FNM
Q: Were all rent credit for option to purchase asset requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae' AND Loans.LoanPurposeType = 'Purchase')
SKIP: yes | clean_opts: 2 | defect_opts: 5
  - [Major] Rent credit for option to purchase agmt w/ 12 mos term, rental amt & terms of the lease not in file -> O-FNM-55669
  - [Critical] Rent-back credit used as source of funds for closing costs, down pymt, or reserves when qualifying -> O-FNM-58104
  - [Major] Rent credit for option to purchase market rent was not determined by the subject property appraisal -> O-FNM-55671
  - [Major] Rent credit for option to purchase canceled checks/money order receipts for last 12 mos not in file -> O-FNM-55670
  - [Critical] Rent credit not calculated using the difference between market rent & actual rent paid by the borr -> O-FNM-00277

### PC::O-FNM-15342 | Assets | O-FNM
Q: Were all sweat equity asset requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] Sweat equity was considered on an unallowable transaction and eligibility requirements were not met -> O-FNM-00288

### PC::O-FNM-15343 | Assets | O-FNM
Q: Were all bridge/swing loan asset requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 2
  - [Critical] Ability to make payments on the new & current home, bridge/swing loan & other debts not documented -> O-FNM-00282
  - [Critical] The bridge loan was cross-collateralized against the new property -> O-FNM-56360

### PC::O-FNM-15344 | Assets | O-FNM
Q: Were all borrowed funds secured by an asset requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] Loan proceeds for cash to close without file documenting loan terms and that it is a secured loan -> O-FNM-00279

### PC::O-FNM-15345 | Assets | O-FNM
Q: Were all credit card financing and rewards points asset requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 3
  - [Major] Common customary costs paid by the borr outside of closing on credit card exceeds 2% of the loan amt -> O-FNM-00290
  - [Critical] Credit card points converted to cash qualify as a large deposit missing source as credit card reward -> O-FNM-55108
  - [Critical] Credit card points not in borr acct & cash value verification & conversion to cash PTC not provided -> O-FNM-54871

### PC::O-FNM-15346 | Assets | O-FNM
Q: Were all personal unsecured loans asset requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] Unallowable funds used from a personal unsecured loan, credit card or overdraft protection -> O-FNM-50263

### PC::O-FNM-15347 | Assets | O-FNM
Q: Were all sale of personal assets requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 3
  - [Critical] Source of funds from stocks, bonds, mutual or trust funds used without documenting ownership & value -> O-FNM-00284
  - [Critical] Personal asset sale proceeds exceed 50% of monthly qualifying income w/out an independent valuation -> O-FNM-54032
  - [Critical] Proceeds from the sale of a titled personal asset used without documenting the borrower’s ownership -> O-FNM-54031

### PC::O-FNM-15348 | Assets | O-FNM
Q: Were all cash value of life insurance asset requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] Cash value loan/surrender of life insurance used without documenting repayment and receipt of funds -> O-FNM-00280

### PC::O-FNM-15349 | Assets | O-FNM
Q: Were all anticipated savings and cash-on-hand asset requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] Anticipated savings considered were unreasonable or calculated incorrectly -> O-FNM-50265

### PC::O-FNM-15350 | Assets | O-FNM
Q: Were all asset verification documentation requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 7
  - [Critical] The bank statements provided are incomplete and/or missing all required pages -> Bank Statements
  - [Critical] Depository assets were not documented as per DU -> O-FNM-00217
  - [Critical] All assets were not submitted to DU correctly -> DUAssets
  - [Major] Borr was own realtor & the earned commission not on settlement stmt as a credit towards the mtg loan -> O-FNM-56339
  - [Critical] Earnest money deposit not entered correctly in DU based on if EMD cleared the borr's bank account -> O-FNM-00218
  - [Critical] The loan file did not document sufficient funds for closing -> O-FNM-55916
  - [Critical] Virtual currency used as a source of funds was not verified in U.S. dollars prior to closing -> O-FNM-55675

### PC::O-FNM-15351 | Data Validation Svc-DVS | O-FNM
Q: Were all additional asset DU requirements met to maintain Reps & Warrants Relief?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 2
  - [Critical] Assets differ from amt in DU & amt on verification report not >= total funds to be verified in DU -> O-FNM-50848
  - [Critical] Earnest money cleared the borr’s acct - not entered as “Other Credit” in DU &/or source not verified -> O-FNM-50847

### PC::O-FNM-15354 | Property - Appraisal | O-FNM
Q: Were all appraisal delivery requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 1
  - [Critical] A copy of the appraisal report was not provided at least 3 days prior to the closing -> O-FNM-00542

### PC::O-FNM-15356 | Property - Appraisal | O-FNM
Q: Were all leasehold estate appraisal requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 9
  - [Critical] Lease agreement or ground lease terms, restrictions & conditions not provided for leasehold property -> O-FNM-50310
  - [Critical] The leasehold estate lease payments/assessments were unpaid or were in default -> O-FNM-55646
  - [Critical] The property is subject to a leasehold estate and is an ineligible property type -> O-FNM-58730
  - [Critical] The provisions of the lease associated with the leasehold estate did not meet requirements -> O-FNM-55645
  - [Critical] The leasehold estate & improvements did not constitute real property subject to the mortgage lien -> O-FNM-55642
  - [Critical] Req's not met for establishing the purchase price of the land in leasehold with option to purchase -> O-FNM-55647
  - [Critical] The leasehold estate & mortgage will be impaired by a merger of title between the lessor and lessee -> O-FNM-55641
  - [Critical] A default under the leasehold estate will terminate the sublease securing the mortgage -> O-FNM-55643
  - [Critical] Leasehold term not at least 5 yrs past maturity date & fee simple title not vested to borr earlier -> O-FNM-55644

### PC::O-FNM-15357 | Property - Appraisal | O-FNM
Q: Were all special property appraisal requirements met?
APPLIES: Loans.QC_Policy = 'Fannie Mae'
SKIP: yes | clean_opts: 2 | defect_opts: 8
  - [Critical] Appraiser did not enter "3D Printed Home" in the description field of the Sales Comp Approach grid -> O-FNM-57136
  - [Critical] Each of the multiple parcels not conveyed in entirety with the mortgage being the first lien on each -> O-FNM-54684
  - [Critical] The subject's additional parcels were not adjoining and/or did not have the same basic zoning -> O-FNM-54683
  - [Critical] The subject property is in Hawaiian Lava Zone 1 or 2 which is not eligible for delivery to FNMA -> O-FNM-50241
  - [Critical] All requirements for a mixed-use property were not met -> O-FNM-50240
  - [Critical] No documentation non-adjoining parcels without the residence cannot be improved with a dwelling -> O-FNM-54686
  - [Critical] Non-adjoining parcels are not separated due to a road, waterfront access or similar as allowable -> O-FNM-54685
  - [Critical] All requirements for non-owned solar panels were not met -> O-FNM-50242

### PC::O-FNM-15358 | Property - Appraisal | O-FNM
Q: Where a property has been affected by a disaster, were all appraisal requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 4
  - [Critical] The appraisal was dated over 180 days before the note date in a property affected by a disaster -> O-FNM-55653
  - [Critical] UW docs, credit reports, income/asset verifications over 180 days prior to note in disaster area -> O-FNM-55652
  - [Critical] No safety/soundness disaster impact but repair estimates & insurance proceeds not documented -> O-FNM-00544
  - [Critical] Property not repaired after disaster w/ uninsured damage affecting safety, soundness, or structure -> O-FNM-55651

### PC::O-FNM-15359 | Property - Appraisal | O-FNM
Q: Were all lender responsibilities requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 5
  - [Critical] The file does not contain documentation verifying the property seller is the owner of the property -> O-FNM-00703
  - [Critical] Appraiser indicated on Form 1004D that the property value has declined without a new appraisal -> O-FNM-55730
  - [Critical] Appraiser not provided sales contract, known property info &/or contract updates if applicable -> O-FNM-00530
  - [Critical] Appraiser comments indicate value may be based on discriminatory assumptions of subject/neighborhood -> O-FNM-00537
  - [Critical] Unfavorable environment or economic factors noted without comment &/or no comps with same condition -> O-FNM-00539

### PC::O-FNM-15360 | Property - Appraisal | O-FNM
Q: Were all appraiser selection criteria and information disclosure requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 2
  - [Critical] The appraiser's active state license as of the effective date of the appraisal was not documented -> O-FNM-00523
  - [Critical] Appraisal completed by trainee, unlicensed/uncertified appraiser w/out supervisory appraiser signing -> O-FNM-51044

### PC::O-FNM-15361 | Property - Appraisal | O-FNM
Q: Were all Collateral Risk Assessment requirements met?
APPLIES: Loans.QC_Policy = 'Fannie Mae'
SKIP: yes | clean_opts: 2 | defect_opts: 3
  - [Critical] No extra steps taken ensuring property characteristics reported correct regardless of CU risk score -> O-FNM-54344
  - [Critical] Information provided in CU or other sources did not confirm the sales provided were appropriate -> O-FNM-54352
  - [Critical] CU comps tab messages & data alerts review reveal quality & condition ratings inconsistent to market -> O-FNM-54349

### PC::O-FNM-15363 | Property - Appraisal | O-FNM
Q: Were all appraisal report form, age, and use requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 10
  - [Critical] Appraisal is over 4 mos but under 12 mos on the date of closing without reinspection on Form 1004D -> O-FNM-00576
  - [Critical] Appraiser certification &/or statement of assumptions & limiting conditions conflict w/ FNMA policy -> O-FNM-54356
  - [Critical] Appraisal is missing the appraiser’s certification, statement of assumptions & limiting conditions -> O-FNM-00528
  - [Critical] Desktop appraisal used in a loan that was not a primary SFR purchase with an LTV of 90% or less -> O-FNM-55729
  - [Critical] The exterior only appraisal did not include street map &/or subject photos -> O-FNM-50271
  - [Critical] A hybrid appraisal was used in an ineligible transaction type -> O-FNM-58350
  - [Critical] A hybrid appraisal was used that did not meet all of the required preconditions -> O-FNM-58351
  - [Critical] A 2nd appraisal obtained w/out basis deficiencies noted &/or most reliable appraisal not used -> O-FNM-50878
  - [Critical] Form 1007, comparable rent schedule not in file for 1 unit investment property -> O-FNM-51045
  - [Critical] 2-4 rental income property missing Form 1025, Small Residential Income Property Appraisal Report -> O-FNM-55654

### PC::O-FNM-15364 | Property - Appraisal | O-FNM
Q: Were all Subject and Contract sections of the appraisal requirements met?
APPLIES: Loans.QC_Policy = 'Fannie Mae'
SKIP: yes | clean_opts: 2 | defect_opts: 6
  - [Critical] The appraiser did not enter the contract date for the subject purchase transaction -> O-FNM-53021
  - [Critical] Contract not analyzed &/or analysis not provided in the contract section of the appraisal -> O-FNM-50274
  - [Critical] The appraiser did not indicate if the property seller is the owner of record -> O-FNM-53022
  - [Critical] Yes or No box not checked if subject listed in last year &/or no data source, offering price & date -> O-FNM-50273
  - [Critical] Contract price in the contract section did not match the contract/sales comparison approach section -> O-FNM-53020
  - [Critical] Appraisal did not note of monetary and non-monetary items paid by any party on behalf of the borr -> O-FNM-53023

### PC::O-FNM-15365 | Property - Appraisal | O-FNM
Q: Were all Neighborhood section of the appraisal requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 7
  - [Critical] Available land/degree of development, zoning/present land use not reported ensuring residential area -> O-FNM-50276
  - [Critical] Neighborhood boundaries, characteristics & marketability factors not reported on the appraisal -> O-FNM-50275
  - [Critical] Subject appears to be an over-improvement &/or is not in the comps adjustment grid without comment -> O-FNM-50278
  - [Critical] Age range & predominant age of the properties in the neighborhood not provided by the appraiser -> O-FNM-50279
  - [Critical] Price range/predominant price & area high/low prevailing price of same property type not reported -> O-FNM-50277
  - [Critical] The predominant age and predominant price were not given in whole numbers -> O-FNM-52895
  - [Critical] Indicators of market conditions including trend of values, supply & marketing time not reported -> O-FNM-59374

### PC::O-FNM-15366 | Property - Appraisal | O-FNM
Q: Were all Site sections of the appraisal requirements met?
APPLIES: Loans.QC_Policy = 'Fannie Mae'
SKIP: yes | clean_opts: 2 | defect_opts: 5
  - [Critical] No comment on adverse conds affecting the subject &/or adj properties impact to value/marketability -> O-FNM-54817
  - [Critical] Specific zoning class & a general statement to what the zoning permits not reported in the appraisal -> O-FNM-50281
  - [Critical] Legally enforceable maintenance agreement/covenant of community or private owned street as required -> O-FNM-50283
  - [Critical] The subject improvements are not considered the highest and best use of the site -> O-FNM-50282
  - [Critical] An encroachment was identified on the subject or neighboring property without an easement -> O-FNM-51474

### PC::O-FNM-15367 | Property - Appraisal | O-FNM
Q: Were all Improvements section of the appraisal requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 6
  - [Critical] The impact &/or commentary of an unpermitted addition was not provided -> O-FNM-50290
  - [Critical] Effective age is higher than the actual age indicating poor subject condition without comment -> O-FNM-50286
  - [Critical] Special energy saving items not noted on energy efficient property -> O-FNM-50287
  - [Critical] A description and impact of an outbuilding on the property not given -> O-FNM-50291
  - [Critical] Private road noted without condition of the road noted and/or a maintenance agreement was not found -> FNM-Private Rd
  - [Critical] Unique property w/out recent similar comps, sound adj for differences, or demonstrated marketability -> O-FNM-58599

### PC::O-FNM-15369 | Property - Appraisal | O-FNM
Q: Were all Sales Comparison Approach section of the appraisal requirements met?
APPLIES: Loans.QC_Policy = 'Fannie Mae'
SKIP: yes | clean_opts: 2 | defect_opts: 2
  - [Critical] Subject's 3 year sales history & comps sales history for last 12 months not reported -> O-FNM-50294
  - [Critical] The specific data and verification source for each comparable not given -> O-FNM-50293

### PC::O-FNM-15370 | Property - Appraisal | O-FNM
Q: Were all Comparable sales requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 7
  - [Critical] Comparable sales were not closed within the last 12 months and no explanation provided for their use -> O-FNM-00535
  - [Critical] CU 2.6 + without ensuring comps appropriate, physically similar in site, GLA, & proper adjustments -> O-FNM-54119
  - [Critical] Comps provided not from within & outside of the new condo, subdivision or PUD without explanation -> O-FNM-50296
  - [Critical] The comps do not reflect the same positive & negative location characteristics as the subject -> O-FNM-54816
  - [Critical] Comp time adj w/out explanation or analysis of market cond changes from their contract date-eff date -> O-FNM-58598
  - [Critical] No dollar amount given for comparables concessions &/or no adjustments made & explanation not given -> O-FNM-00536
  - [Critical] Comps do not have similar physical/legal characteristics as the subject without appraiser commentary -> O-FNM-58600

### PC::O-FNM-15371 | Property - Appraisal | O-FNM
Q: Were all cost and income approach to value requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 2
  - [Critical] Analysis in the cost approach is inconsistent to other areas of the report -> O-FNM-50299
  - [Critical] Income approach used without supporting comp rental/sales data & gross rent multiplier calculations -> O-FNM-50300

### PC::O-FNM-15374 | Property - Appraisal | O-FNM
Q: Were all condo appraisal requirements met?
APPLIES: Loans.QC_Policy = 'Fannie Mae' AND Loans.PropertyType = 'Condominium'
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] Analysis of the unit, project amenities & HOA purpose not provided -> O-FNM-50304

### PC::O-FNM-15377 | Property - Appraisal | O-FNM
Q: Were all community land trust appraisal requirements met?
APPLIES: Loans.QC_Policy = 'Fannie Mae'
SKIP: yes | clean_opts: 2 | defect_opts: 2
  - [Critical] Income not converted from ground lease to leased fee value correctly -> O-FNM-50312
  - [Critical] Ground lease leasehold interest held by community land trust not analyzed -> O-FNM-50311

### PC::O-FNM-15378 | Property - Appraisal | O-FNM
Q: Were all mixed-use properties appraisal requirements met?
APPLIES: Loans.QC_Policy = 'Fannie Mae'
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] One or more of the requirements for a mixed-use property appraisal was not met -> O-FNM-50313

### PC::O-FNM-15379 | Property - Appraisal | O-FNM
Q: Were all environmental hazards appraisal requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 3
  - [Critical] Hazardous condition noted without additional commentary -> O-FNM-50314
  - [Critical] Known environment hazard not disclosed to the borr & addt'l inspections not conducted as applicable -> O-FNM-00540
  - [Critical] Health & safety issues have been identified without being addressed and/or corrected -> HealthSafe

### PC::O-FNM-15380 | Property - Appraisal | O-FNM
Q: Were all value acceptance (appraisal waiver) requirements met?
APPLIES: Loans.QC_Policy = 'Fannie Mae'
SKIP: yes | clean_opts: 2 | defect_opts: 7
  - [Critical] Value acceptance was exercised where an appraisal was obtained for the transaction -> O-FNM-56086
  - [Critical] No acceptable home inspection in the file where a rural high-needs value acceptance was exercised -> O-FNM-55740
  - [Critical] The value acceptance offer is over 4 months old on the Note date -> O-FNM-56087
  - [Critical] Value acceptance was exercised where it would have been prudent or required to obtain an appraisal -> O-FNM-54874
  - [Critical] Value acceptance was exercised when rental income from the subject property is used -> O-FNM-54132
  - [Critical] Special feature code 801 was not included at delivery where value acceptance was exercised -> O-FNM-56088
  - [Major] The loan had a characteristic that was not eligible for value acceptance -> O-FNM-56089

### PC::O-FNM-15381 | Property - Appraisal | O-FNM
Q: Were all Condominium Project Questionnaire appraisal requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae') AND (Loans.PropertyType = 'Condominium')
SKIP: no | clean_opts: 2 | defect_opts: 9
  - [Critical] (Best Practice) Form 1076A not used to ensure project meets temp req's for condo & co-op projects -> O-FNM-55515
  - [Critical] Missing Condo Project Questionnaire, Form 1076, with deferred maintenance addendum as recommended -> O-FNM-53853
  - [Critical] The status of the subject condo or co-op project is “Unavailable” in Condo Project Manager, CPM -> O-FNM-55420
  - [Critical] CPM has a delivery restriction with a CPM Approved by FNMA msg in DU without evidence of compliance -> O-FNM-59132
  - [Critical] CPM project approved status not retained as of note date & CPM Approved by FNMA DU msg not received -> O-FNM-59133
  - [Critical] Detached condo did not meet property/appraisal standards, insurance, &/or priority lien requirements -> O-FNM-50876
  - [Critical] CPM Approved by FNMA in DU lost status due to credit report exp or changes to CPM ID/project/address -> O-FNM-59131
  - [Critical] Project review waiver exercised where project is terminating or involved in insolvency proceedings -> O-FNM-59348
  - [Critical] Project review is waived without meeting all property eligibility requirements -> O-FNM-51046

### PC::O-FNM-15382 | Property - Appraisal | O-FNM
Q: Were all condo or co-op ineligible projects appraisal requirements met?
APPLIES: Loans.QC_Policy = 'Fannie Mae' AND (Loans.PropertyType = 'Condominium' OR Loans.PropertyType = 'Cooperative')
SKIP: yes | clean_opts: 2 | defect_opts: 6
  - [Critical] The condo/co-op project is subject of litigation without all eligible minor litigation criteria met -> O-FNM-50877
  - [Major] Sponsor ownership/Coop shares not documented or outside of allotted %. 20% Portfolio - 40% Agency -> CoopDoc
  - [Critical] Indicators exist that the individually owned unit condo/co-op project operates as a condotel -> O-FNM-00541
  - [Critical] Total nonresidential or commercial space exceeds 35% in a condo or cooperative -> O-FNM-53854
  - [Critical] Condo or co-op project has recreational leases or mandatory memberships that require paying dues -> O-FNM-53863
  - [Critical] The project did not meet single entity ownership limits -> O-FNM-53789

### PC::O-FNM-15384 | Property - Appraisal | O-FNM
Q: Were all condo or co-op project review requirements met?
APPLIES: Loans.QC_Policy = 'Fannie Mae' AND (Loans.PropertyType = 'Condominium' OR Loans.PropertyType = 'Cooperative')
SKIP: no | clean_opts: 2 | defect_opts: 15
  - [Critical] The Condo, CO-OP, or PUD does not meet the AUS project requirements -> CondoAUS
  - [Critical] CPM was not used to conduct the condo project full review without being exempt or receiving a waiver -> O-FNM-56482
  - [Critical] A Questionnaire/Approval worksheet is not found in the file and is required -> CondoQuestionnaire
  - [Critical] Project subject to ground lease w/out protected lender financial interest in a condemnation/similar -> O-FNM-58745
  - [Major] The subject co-op occupancy intent is for investment purposes which is prohibited -> O-FNM-50317
  - [Major] The co-op sellers affidavit was not located and/or properly executed -> COOPPSA
  - [Critical] The file did not contain a Co-op Corporation’s Recognition Agreement -> O-FNM-53024
  - [Major] The stock cert is not found and/or does not match the # of shares on the loan security agreement -> COOPStkCert
  - [Critical] The file did not include the CPM decision and unexpired CPM Certification -> O-FNM-58744
  - [Critical] More than 15% of the total units in a project are 60 days or more past due on HOA fees -> O-FNM-56978
  - [Critical] Over 15% of total units in a project are 60 days or more past due in pymts of special assessments -> O-FNM-56979
  - [Critical] No evidence the project assoc has a minimum annual budgeted replacement reserve allocation of 10% -> O-FNM-53788
  - [Critical] Limited or full condo project review not conducted as applicable -> O-FNM-50315
  - [Critical] Unit is not on a separate meter, no evidence this is common & project budget includes utility funds -> O-FNM-56977
  - [Major] The Pro Rata form is missing or is incomplete/inaccurate -> ProRata

### PC::O-FNM-15386 | Underwriting | O-FNM
Q: Were all data quality, integrity, and fraud requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 1 | defect_opts: 8
  - [Critical] Property address submitted to DU does not match other documentation in the loan file -> BorrowerAddress
  - [Critical] Inconsistencies in the Income, asset, liability &/or credit documents were not addressed -> O-FNM-00578
  - [Critical] Material discrepancies noted in the credit information without documenting the resolution -> O-FNM-00016
  - [Critical] ID # on the Credit report does not match the AUS report or EPIC screen -> Credit Rept ID Match
  - [Critical] All employees involved in the origination of the loan were not checked against the FHFA SCP list -> O-FNM-52794
  - [Major] Required parties per their specific role in the loan not checked against the FHLMC Exclusionary List -> O-FRD-02575
  - [Critical] No evidence all internal participants involved in the mtg were checked against the GSA and LDP lists -> O-FNM-52795
  - [Critical] Match on the OFAC SDN list, FNMA not notified w/in 24 hrs & funds not blocked & segregated -> O-FNM-51688

### PC::O-FNM-15387 | Underwriting | O-FNM
Q: Were all Fannie Mae AUS requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae') AND (Loans.Underwriting_Type = 'Desktop Underwriter')
SKIP: no | clean_opts: 1 | defect_opts: 3
  - [Critical] Automated UW case identifier did not include DU casefile ID in a second home or investment property -> O-FNM-54338
  - [Critical] 2nd home or investment property not underwritten with DU &/or not an Approve/Eligible recommendation -> O-FNM-54259
  - [Critical] 2nd home/investment not DU UW & not a high LTV refi w/ SFC 840 manual UW Alt Qualification Path -> O-FNM-54260

### PC::O-FNM-15388 | Underwriting | O-FNM
Q: Were all occupancy type requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 1 | defect_opts: 5
  - [Critical] Military orders not obtained evidencing active duty as reason borr unable to occupy as per the mtg -> O-FNM-55439
  - [Critical] All borrowers were not individuals for a group home investment property leased to business entities -> O-FNM-55773
  - [Critical] LTV calculated incorrectly or info put in AUS to calculate LTV incorrect -> O-FNM-50195
  - [Critical] The LTV ratio is higher than Fannie Mae’s maximum allowable ratio -> O-FNM-00726
  - [Critical] All occupancy eligibility requirements were not met for the occupancy type -> O-FNM-50194

### PC::O-FNM-15389 | Underwriting | O-FNM
Q: Were all mortgage eligibility requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 1 | defect_opts: 2
  - [Critical] CLTV calculated incorrectly -> O-FNM-50196
  - [Critical] HCLTV calculated incorrectly -> O-FNM-50197

### PC::O-FNM-15390 | Underwriting | O-FNM
Q: Were all loan limit requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 1 | defect_opts: 1
  - [Critical] The mtg did not meet the loan limits based on loan type as outlined by FNMA -> O-FNM-50223

### PC::O-FNM-15391 | Underwriting | O-FNM
Q: Were all Private Transfer Fee Covenants eligibility requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 2
  - [Critical] Subject has a private transfer fee & is not a shared equity loan with a Note date on or after 7/1/23 -> O-FNM-57897
  - [Critical] The subject's private transfer fee is unacceptable under the Private Transfer Fee Regulation -> O-FNM-00881

### PC::O-FNM-15392 | Underwriting | O-FNM
Q: Were all special assessment eligibility requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 2
  - [Critical] Special assessments not PIF & mtg not reduced by amt of unpaid assessments -> O-FNM-50225
  - [Critical] The file did not document the current/future installments of taxes and special assessments -> O-FNM-55629

### PC::O-FNM-15393 | Underwriting | O-FNM
Q: Were all modified loan eligibility requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 1
  - [Critical] Mtg Modification changed the loan terms of original Note -> O-FNM-50226

### PC::O-FNM-15394 | Underwriting | O-FNM
Q: Were all nonstandard payment collection options eligibility requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 1
  - [Critical] A non-monthly payment option offered without a separate agreement -> O-FNM-50227

### PC::O-FNM-15395 | Underwriting | O-FNM
Q: Were all legal requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 2
  - [Critical] The subject's first lien position was not confirmed -> O-FNM-50228
  - [Critical] Subject is rented & tenants rights could affect FNMA's interest -> O-FNM-50229

### PC::O-FNM-15396 | Closing | O-FNM
Q: Were all escrow requirements met?
APPLIES: Loans.QC_Policy = 'Fannie Mae'
SKIP: no | clean_opts: 2 | defect_opts: 1
  - [Critical] An escrow account was not set up and an Escrow Waiver not in the file -> O-FNM-50230

### PC::O-FNM-15397 | Underwriting | O-FNM
Q: Were all general borrower eligibility requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 6
  - [Critical] The identity of each borrower was not confirmed prior to the extension of credit -> O-FNM-00043
  - [Critical] Homeownership education req's not met for non-traditional credit borr's or purchase w/ LTV above 95% -> O-FNM-00048
  - [Critical] Third-party homeownership education content not aligned w/ NIS or HUD's Housing Counseling Program -> O-FNM-55425
  - [Critical] SSN/ITIN discrepancy not resolved & documented using Form SSA–89, eCBSV or 3rd party vendor from SSA -> O-FNM-50233
  - [Critical] SFC 162 not used where there was a discrepancy identified with the Social Security number -> O-FNM-56092
  - [Critical] The file did not document that each borrower has a valid SS number or ITIN -> O-FNM-58597

### PC::O-FNM-15398 | Underwriting | O-FNM
Q: Were all non–U.S. citizen borrower eligibility requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 1
  - [Critical] The applicant is a non-US citizen not legally present in the United States -> O-FNM-00046

### PC::O-FNM-15399 | Underwriting | O-FNM
Q: Were all multiple financed properties eligibility requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 4
  - [Critical] The borrower exceeded the max limit of 2 financed properties including the subject in a HomeReady -> O-FNM-51486
  - [Critical] The number of financed properties exceeded guidelines -> O-FNM-50234
  - [Critical] The subject loan is a second home or investment property & the loan was not DU underwritten -> O-FNM-54873
  - [Critical] The file did not document sufficient assets to meet the reserve requirement -> O-FNM-50235

### PC::O-FNM-15400 | Underwriting | O-FNM
Q: Were all guarantors, co-signers, or non-occupant borrowers eligibility requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 3
  - [Critical] The guarantor or co-signer did not sign the mortgage or deed of trust note -> O-FNM-57446
  - [Critical] Manual UW non-occupant & occupying borr 5% down not own funds & LTV >80%/donated funds ineligible -> O-FNM-55631
  - [Critical] Max LTV, CLTV, HCLTV ratio not met as applicable in a loan with a co-signer or non-occupant borrower -> O-FNM-55632

### PC::O-FNM-15401 | Underwriting | O-FNM
Q: Were all inter vivos revocable trusts requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 5
  - [Critical] Income/assets of at least 1 person forming the inter vivos revocable trust was not used to qualify -> O-FNM-55634
  - [Critical] In a primary residence at least 1 inter vivos revocable trustee will not occupy the subject property -> O-FNM-55636
  - [Critical] At least 1 inter vivos revocable trustee did not sign the loan documents in a primary residence -> O-FNM-55635
  - [Critical] Title insurance coverage contained exceptions for the inter vivos revocable trust or the trustees -> O-FNM-55633
  - [Critical] Title is not vested in the inter vivos revocable trustee(s) and the individual borrower(s) names -> O-FNM-55637

### PC::O-FNM-15402 | Underwriting | O-FNM
Q: Were all comprehensive risk assessment requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 1
  - [Critical] UW did not adequately evaluate the layers of risk, significance of risk factors and overall risks -> O-FNM-00713

### PC::O-FNM-15403 | Underwriting | O-FNM
Q: Were DU documentation requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae') AND (Loans.Underwriting_Type = 'Desktop Underwriter')
SKIP: no | clean_opts: 1 | defect_opts: 2
  - [Critical] Final complete DU UW Findings report &/or final UW Analysis report produced by DU not in the file -> O-FNM-50243
  - [Critical] DU Verifications/Conditions not met for income, assets, credit, &/or level of property fieldwork -> O-FNM-00184

### PC::O-FNM-15404 | Underwriting | O-FNM
Q: Were all Approve/Ineligible, Refer with Caution, or Out of Scope recommendations requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 3
  - [Critical] Approve/Ineligible decision & additional layers of risk not considered in the approval -> O-FNM-00720
  - [Critical] The loan was not manually UW when DU recommendation was "out of scope" -> O-FNM-50244
  - [Critical] In a Refer w/ Caution the UW did not follow suggested steps to resubmit or manually UW the loan -> O-FNM-00721

### PC::O-FNM-15405 | Credit - Liabilities | O-FNM
Q: Were all erroneous credit report data requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae' OR Loans.QC_Policy = 'FHA' OR Loans.QC_Policy = 'Freddie Mac' OR Loans.QC_Policy = 'USDA' OR Loans.QC_Policy = 'VA')
SKIP: no | clean_opts: 4 | defect_opts: 8
  - [Major] Credit Alerts/Hawk Alerts &/or additional addresses have not been addressed and/or documented -> CBR-Fraud Alerts-2
  - [Major] There is a Date of Birth ( DOB ) discrepancy between credit report and 1003 -> CBR-Fraud Alerts-1
  - [Critical] The UW did not reconcile discrepancies between the credit report and the 1003 as required by DU -> O-FNM-00183
  - [Critical] Documentation of significant derog credit reporting error not in file -> O-FNM-50245
  - [Major] Credit Alerts/Hawk Alerts &/or additional addresses have not been addressed and/or documented -> CBR-Fraud Alerts-2
  - [Major] There is a Date of Birth ( DOB ) discrepancy between credit report and 1003 -> CBR-Fraud Alerts-1
  - [Critical] The UW did not reconcile discrepancies between the credit report and the 1003 as required by DU -> O-FNM-00183
  - [Critical] Documentation of significant derog credit reporting error not in file -> O-FNM-50245

### PC::O-FNM-15406 | Insurance | O-FNM
Q: Were all Mortgage Insurance/Loan Guaranty requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 4
  - [Critical] Borrower paid MI & the amount required not included in the cash to close or monthly mortgage payment -> O-FNM-50019
  - [Critical] Lender purchased MI master primary policies & related endorsements not on approved forms -> O-FNM-52258
  - [Critical] No, LTV exceeds 80% without MI issued by an approved insurer at the required coverage level -> O-FNM-00832
  - [Critical] The applicant was charged the incorrect mortgage insurance amount -> O-FNM-50020

### PC::O-FNM-15407 | Underwriting | O-FNM
Q: Were all Title Insurance requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 13
  - [Critical] Attorney title opinion letter did not state property is acceptable & mtg is a fee simple 1st lien -> O-FNM-55728
  - [Critical] Attorney title opinion letter did not provide gap coverage between closing & recordation of the mtg -> O-FNM-55726
  - [Critical] The attorney title opinion letter did not list all other liens and state they are subordinate -> O-FNM-55727
  - [Critical] Attorney title opinion letter was not addressed to the lender and all successors -> O-FNM-55725
  - [Critical] Title insurer/reinsurer not approved &/or licensed to issue insurance in the subject property state -> O-FNM-51712
  - [Critical] The title effective date is not within 90-days of the closing date or 180 days for new construction -> Title 90Days
  - [Critical] Title revealed exceptions or impediments without all specific eligibility requirements being met -> O-FNM-51047
  - [Critical] No, the file does not reflect evidence of acceptable title insurance -> O-FNM-00830
  - [Critical] Attorney not insured against malpractice in giving opinions of title in an amt common for the area -> O-FNM-55724
  - [Critical] The attorney issuing the title opinion letter was not licensed where the subject property is located -> O-FNM-55723
  - [Major] The loan amount, vesting, proposed insured or other "Red Flags" have not been addressed -> TitleRedFlags
  - [Major] Schedule B - title requirements found that have not been appropriately addressed and/or cleared -> Title-TitleReqmts
  - [Major] The transfer of title is outside of company guidelines and not properly explained -> Title-TransofTitle

### PC::O-FNM-15408 | Information Integrity | O-FNM
Q: Were all QC reverification requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 3 | defect_opts: 15
  - [Critical] Unable to obtain transcripts due to address on form not matching address in IRS records -> 4506CAddress
  - [Critical] Unable to obtain business transcripts due to missing 4506-C form for each business used to qualify -> 4506CBusiness
  - [Critical] Unable to obtain transcripts due to form not completed correctly (incorrect boxes checked on form) -> 4506CIncorrect
  - [Critical] QC asset reverification did not validate funds as submitted -> O-FNM-50341
  - [Critical] QC review credit report did not support the original credit report -> O-FNM-50342
  - [Critical] QC employment/income reverification did not validate income/employment as submitted -> O-FNM-50340
  - [Critical] QC reverification of the gift from the gift donor did not support the original information/amount -> O-FNM-59420
  - [Critical] QC credit report does not show HELOC paid & closed -> HelocPayClose
  - [Critical] QC review of insurance & other documents do not support owner occupancy -> O-FNM-50343
  - [Critical] A signed blanket authorization form to reverify credit information was not in the file -> O-FNM-50193
  - [Critical] QC reverif of 3rd-party asset report from the provider didn’t support original data used to qualify -> O-FNM-59419
  - [Critical] The review appraisal or desk review of the appraisal did not support the original appraised value -> O-FNM-50346
  - [Critical] SS, retirement/disability income not re-verified &/or reverification did not confirm info as correct -> O-FNM-51735
  - [Critical-Pending SI] QC Tax transcripts reverification did not validate income as submitted -> O-FNM-50339
  - [Critical-Pending SI] Tax transcripts show discrepancies, or rejected due to IRS code 10 -> TaxTranscriptsSI

### PC::O-FNM-15409 | Information Integrity | O-FNM
Q: Were all QC underwriting documents review requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 1 | defect_opts: 5
  - [Critical] All DU messages/conditions not resolved -> O-FNM-50337
  - [Critical] The loan did not close by the Close By Date stated in the DU validation message -> O-FNM-52994
  - [Critical] QC review: DU income/asset validation report ID mismatch &/or verification report expired -> O-FNM-59418
  - [Critical] Not all information & final loan terms on the closing documents are correct -> O-FNM-50338
  - [Critical] Closing conditions were not satisfied by the date of closing -> O-FNM-00824

### PC::O-FNM-15410 | Product Specific | O-FNM
Q: In a purchase transaction, were all eligibility requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 9
  - [Critical] All additional requirements not met based on LTV and/or loan type -> O-FNM-50202
  - [Critical] Sufficient funds to meet minimum contribution from acceptable source not documented and/or verified -> O-FNM-00725
  - [Critical] Not all Non-Arm's length requirements were met for existing or new homes -> O-FNM-50203
  - [Critical] Seller tax credit included in funds to close that does not meet exception to offset the escrow acct -> O-FNM-54035
  - [Critical] The purchase price &/or any earnest money deposit was designated in virtual currency -> O-FNM-55679
  - [Critical] The borrower(s) received cash back in an amount exceeding purchase money transaction guidelines -> O-FNM-00829
  - [Critical] Evidence all parties agreed to the terms of the short sale/pre-foreclosure -> O-FNM-50204
  - [Critical] Evidence all parties agreed to the terms of the short sale/preforeclosure -> O-FNM-50204
  - [Major] The purchase agreement indicates personal property and/or repairs are included in the purchase price -> UW-Documentation3

### PC::O-FNM-15411 | Product Specific | O-FNM
Q: In a limited cash-out refinance transaction, were all eligibility requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 10
  - [Critical] The borrower received loan proceeds exceeding 2% of the subject loan amount or $2,000 in a LCO refi -> O-FNM-50211
  - [Critical] Ineligible for LCO as there is not an outstanding lien and not a con-perm -> O-FNM-50209
  - [Critical] Manual UW LCO financed payment of the subject's taxes over 60 days in arrears -> O-FNM-50208
  - [Critical] LCO refi - All requirements not met for LTV over 95% -> O-FNM-50207
  - [Critical] LCO inelig due to short term/consolidated refi to a new 1st mtg < 6 months -> O-FNM-50210
  - [Critical] Subject listed for sale w/out evidence it was off the market on/before disbursement of the new loan -> O-FNM-50206
  - [Critical] The subordinate lien paid in LCO refi was not obtained to buy the property -> O-FNM-50205
  - [Critical] No borrower on the LCO was a current owner at the time of the initial app & does not meet exceptions -> O-FNM-56598
  - [Critical] The limited cash-out refinance was obtained for an unacceptable use -> O-FNM-56579
  - [Critical] Equity buy out from ex-spouse or other co-borrower without adequate documentation of the equity -> O-FNM-00728

### PC::O-FNM-15412 | Product Specific | O-FNM
Q: In a cash-out refinance transaction, were all eligibility requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 9
  - [Critical] First mtg PIF by subject CO refi not at least 12 mos old from prior note date to subject note date -> O-FNM-56146
  - [Critical] In a cash-out refi, no evidence the listed property was taken off the market prior to disbursement -> O-FNM-52249
  - [Critical] Proceeds from the cash-out refinance were used to pay off an installment land contract -> O-FNM-52251
  - [Critical] No borrower on title for at least 6 mos prior to disbursement & did not meet ownership exceptions -> O-FNM-52250
  - [Critical] The subject has a student loan cash-out refinance feature without all requirements being met -> O-FNM-52252
  - [Critical] Delayed financing cashout refi did not confirm a mtg not used to obtain the subject & no liens exist -> O-FNM-55648
  - [Critical] Loan amt more than borr's initial purchase plus all costs to close in a CO refi w/ delayed financing -> O-FNM-55650
  - [Critical] Cash-out refinance with delayed financing did not document the source of funds for the purchase -> O-FNM-55649
  - [Critical] Cash-out loan proceeds allowed to be used for purposes not allowed as per FNMA requirements -> O-FNM-00729

### PC::O-FNM-15413 | Product Specific | O-FNM
Q: In a RefiNow transaction, were all borrower eligibility requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 2
  - [Critical] RefiNow total income is not less than or equal to 100% of the AMI limit for the subject's location -> O-FNM-54305
  - [Critical] RefiNow all Note signors whose income is used not considered in determining income limit eligibility -> O-FNM-54306

### PC::O-FNM-15414 | Product Specific | O-FNM
Q: In a RefiNow transaction, were all income documentation requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 7
  - [Critical] RefiNow using alimony/child support/maintenance & divorce decree or equiv & 1 mo receipt missing -> O-FNM-54333
  - [Critical] RefiNow alimony/child support debt pymts & amount not documented with a divorce decree or equivalent -> O-FNM-54335
  - [Critical] RefiNow file did not contain 1 recent statement showing asset balance verifying funds to close -> O-FNM-54334
  - [Critical] RefiNow using base pay only, YTD paystub not provided or date over 30 days prior to application date -> O-FNM-54329
  - [Critical] RefiNow using base pay plus variable income, most recent paystub & last year W2 not provided -> O-FNM-54330
  - [Critical] In a RefiNow using military income, the military leave and earnings statement not provided -> O-FNM-54331
  - [Critical] RefiNow using self-employment, missing 1 yr personal/business tax returns & terms to waive not met -> O-FNM-54332

### PC::O-FNM-15415 | Product Specific | O-FNM
Q: In a RefiNow transaction, were all occupancy and property type documentation requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 2
  - [Critical] RefiNow loan project is a condo or co-op hotel, houseboat, timeshare or segmented ownership project -> O-FNM-54323
  - [Critical] The RefiNow loan is not secured by a one-unit principal residence -> O-FNM-54322

### PC::O-FNM-15416 | Product Specific | O-FNM
Q: In a RefiNow transaction, were all existing loan eligibility documentation requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 4
  - [Critical] The loan refinanced into a RefiNow was not a conventional mortgage loan owned or securitized by FNMA -> O-FNM-54307
  - [Critical] The loan refinanced into a RefiNow was a high LTV refinance, DU Refi Plus loan, or Refi Plus loan -> O-FNM-54310
  - [Critical] The loan refinanced into a RefiNow was not seasoned for at least 12 months -> O-FNM-54308
  - [Critical] The loan refinanced into a RefiNow was subject to recourse, repurchase, indem or credit enhancement -> O-FNM-54309

### PC::O-FNM-15417 | Product Specific | O-FNM
Q: In a RefiNow transaction, were all subject loan eligibility documentation requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 9
  - [Critical] Borrowers added/removed on RefiNow loan from the original loan without meeting applicable exceptions -> O-FNM-54316
  - [Critical] The RefiNow loan is not a limited cash-out refinance -> O-FNM-54315
  - [Critical] The RefiNow loan was combined with a HomeReady refinance transaction -> O-FNM-54319
  - [Critical] The RefiNow loan is ineligible being subject to a temporary interest rate buydown -> O-FNM-54318
  - [Critical] The RefiNow loan is ineligible as a Texas Section 50(a)(6) loan -> O-FNM-54317
  - [Critical] The RefiNow loan limit does not conform to the general loan limits -> O-FNM-54314
  - [Critical] RefiNow cash out exceeded $250 and/or any excess not applied as a curtailment as applicable -> O-FNM-54313
  - [Critical] Subject loan closed as a RefiNow where the RefiNow option was previously used in a prior transaction -> O-FNM-54676
  - [Critical] The RefiNow loan is not a fixed rate and/or did not meet maximum LTV, CLTV, and HCLTV ratios -> O-FNM-54311

### PC::O-FNM-15418 | Product Specific | O-FNM
Q: In a RefiNow transaction, were all subordinate financing requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 4
  - [Critical] RefiNow has existing subordinate loan satisfied using loan proceeds &/or was not subordinated -> O-FNM-54321
  - [Critical] New subordinate financing permitted in a RefiNow that did not have existing subordinate financing -> O-FNM-54673
  - [Critical] New subordinate P&I increased from the existing subordinated loan in a RefiNow simultaneous refi -> O-FNM-54672
  - [Critical] New subordinate lien UPB is higher than original subordinate lien UPB in RefiNow simultaneous refi -> O-FNM-54671

### PC::O-FNM-15419 | Product Specific | O-FNM
Q: In a RefiNow transaction, were all property valuation documentation requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 1
  - [Critical] An appraisal was obtained in a RefiNow without evidence the $500 credit was passed to the borrower -> O-FNM-54336

### PC::O-FNM-15420 | Product Specific | O-FNM
Q: In a RefiNow transaction, were all underwriting requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 6
  - [Critical] The RefiNow DTI ratio exceeds 65% -> O-FNM-54327
  - [Critical] A RefiNow was manually underwritten without LTV, DTI ratio and credit score requirements being met -> O-FNM-54324
  - [Critical] RefiNow with a non-occupant borrower did not meet the maximum LTV, CLTV, and HCLTV ratio of 95% -> O-FNM-54328
  - [Critical] RefiNow original loan had a 30-day late in the last 6 mos &/or more than one 30-day late in mos 7-12 -> O-FNM-54326
  - [Critical] Resolved COVID-19 forbearance missed payments considered delinquencies in RefiNow pay history req's -> O-FNM-54674
  - [Critical] No FNMA approval for the variance or exception impactful to underwriting/eligibility in a RefiNow -> O-FNM-54675

### PC::O-FNM-15421 | Product Specific | O-FNM
Q: In a RefiNow transaction, were all borrower benefit requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 1
  - [Critical] RefiNow did not reduce interest rate by at least 50 basis points & the monthly mtg pymt not reduced -> O-FNM-54320

### PC::O-FNM-15422 | Product Specific | O-FNM
Q: In a refinance transaction, were all prohibited practices requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 5
  - [Critical] Seller/servicer advanced pymts for the borr to then to refi after agreed pymts were advanced -> O-FNM-55627
  - [Critical] A CO refi with a note date 30 days or less before the application date of the subject LCO refi -> O-FNM-55110
  - [Critical] There are indicators that the refinance was the result of a conditional tender of payment procedure -> O-FNM-55628
  - [Critical] There are indicators the lender specifically targeted the Fannie Mae borrower to offer a refinance -> O-FNM-55626
  - [Critical] There are indicators in the file that the subject refinance is a prearranged refinancing agreement -> O-FNM-55109

### PC::O-FNM-15423 | Product Specific | O-FNM
Q: In a purchase transaction, were all payoff of installment land contracts requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 3
  - [Critical] LTV not calc by dividing the new loan amt by lesser of total acq cost or appraised value at closing -> O-FNM-57531
  - [Critical] Subject not UW as a LCO when p/o of land contract was executed more than 12 mos before application -> O-FNM-50214
  - [Critical] Subject not UW as a purchase when p/o of land contract was executed within 12 mos before application -> O-FNM-50213

### PC::O-FNM-15425 | Product Specific | O-FNM
Q: Were all Adjustable-Rate Mortgages (ARMs) general requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 8
  - [Critical] All characteristics in Standard ARM Plan Matrix not met -> O-FNM-50218
  - [Critical] The Note and Riders did not contain the updated index “fallback” language in a non-SOFR ARM loan -> O-FNM-53027
  - [Critical] The difference in the initial note rate and the fully indexed rate > 3% -> O-FNM-50219
  - [Critical] The ARM Plan index was unacceptable to FNMA -> O-FNM-50217
  - [Critical] Fully indexed rate is not the index value in effect during the 90 days that precede the note date -> O-FNM-55775
  - [Critical] Fully indexed rate not the sum of the applicable index & the mtg margin rounded to the nearest 1/8% -> O-FNM-55774
  - [Critical] A SOFR ARM underwritten by DU was not submitted as a generic ARM -> O-FNM-52742
  - [Critical] One or more standard ARM requirements were not met -> O-FNM-50216

### PC::O-FNM-15426 | Product Specific | O-FNM
Q: Were all Adjustable-Rate Mortgages (ARMs) program requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 10
  - [Critical] Qualifying rate used not appropriate for an ATR covered 1 year ARM with a 1% annual cap -> O-FNM-54583
  - [Critical] Qualifying rate used not appropriate for an ATR covered 1 year ARM with a 2% annual cap -> O-FNM-54584
  - [Critical] ATR 3-year ARM qualifying rate is not equal to the Note Rate + 5% -> O-FNM-54585
  - [Critical] ATR 5-year ARM qualifying rate not equal to greater of fully indexed rate or Note Rate + 2% -> O-FNM-54586
  - [Critical] ATR 7 or 10-year ARM qualifying rate not equal to greater of fully indexed rate or Note Rate -> O-FNM-54587
  - [Critical] ATR covered 3 yr ARM maximum interest rate ceiling exceeds the note rate plus the lifetime cap -> O-FNM-54581
  - [Critical] ATR covered 5 yr ARM max interest rate ceiling exceeds the note rate plus the first rate change cap -> O-FNM-54582
  - [Critical] All eligibility requirements not met for Convertible ARM loans -> O-FNM-50220
  - [Critical] Loan amt over term not used to calculate periodic pymts of P&I for short term ARM ATR covered loan -> O-FNM-54579
  - [Critical] Short term ARM qualifying interest rate not calculated using the required method in ATR covered loan -> O-FNM-54580

### PC::O-FNM-15428 | Product Specific | O-FNM
Q: Were all high-balance mortgage loan requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] All requirements not met for high balance mtg and variance not provided -> O-FNM-50318

### PC::O-FNM-15429 | Product Specific | O-FNM
Q: Were all conversion of construction-to-permanent (CP) mortgage loan financing requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 6
  - [Critical] Two-closing construction perm w/ cost overruns not paid directly to the builder at closing -> O-FNM-55772
  - [Critical] A CO or equivalent missing in construction perm unimproved lot and the construction of a residence -> O-FNM-55395
  - [Critical] Construction perm work not completed & paid that could result in a mechanic's/materialmen’s lien -> O-FNM-55394
  - [Critical] Construction perm FNMA uniform mtg instruments not used or altered for construction reference -> O-FNM-55396
  - [Critical] Ineligible Conversion of Con-to-Perm Financing, lot not owned or acquired as part of transaction -> O-FNM-50918
  - [Critical] The subject property type was ineligible for construction to permanent financing -> O-FNM-51736

### PC::O-FNM-15430 | Product Specific | O-FNM
Q: Were all HomeStyle Renovation mortgage requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 9
  - [Critical] HomeStyle Construction Contract and Loan Agrmt incomplete or unclear title -> O-FNM-50323
  - [Critical] The borrower has opted for the HomeStyle "Do It Yourself" option without all requirements being met -> O-FNM-50883
  - [Critical] HomeStyle LCO, funds after reno not a curtailment or reimburse to borr for costs &/or no receipts -> O-FNM-50884
  - [Critical] Homestyle LTV not from lesser of "as completed" or sale price + rehab costs -> O-FNM-50319
  - [Critical] Homestyle refi LTV not from original loan amt and "as completed" value -> O-FNM-50320
  - [Critical] Appraisal did not give "as completed" value for Homestyle Renovation mtg -> O-FNM-50321
  - [Critical] Certificate of Completion after Homestyle Renovations not in the file -> O-FNM-50322
  - [Critical] The cost of the renovations exceeded the allowable amount as per property and transaction type -> O-FNM-50882
  - [Critical] The renovation escrow account did not meet all HomeStyle Renovation loan requirements -> O-FNM-50951

### PC::O-FNM-15431 | Product Specific | O-FNM
Q: Were all HomeStyle Energy mortgage requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 7
  - [Critical] HomeStyle Energy financing used to pay off energy-related debt did not pay the entire debt in full -> O-FNM-52894
  - [Critical] Energy-related improvement work not documented in a HomeStyle such as the energy report or similar -> O-FNM-00538
  - [Critical] HomeStyle alt documentation (besides an energy report) used w/out meeting qualified circumstances -> O-FNM-58665
  - [Critical] HomeStyle energy report did not meet HERS, DOE, or comparable independent and certified standards -> O-FNM-58664
  - [Critical] HomeStyle Energy financed improvements that are not on the list of ENERGY STAR Efficient Products -> O-FNM-56090
  - [Critical] HomeStyle energy report did not contain savings, recomm improvements, cost-effect &/or est cost -> O-FNM-58663
  - [Critical] HomeStyle loan missing an energy report or report was dated more than 24 mons before the note date -> O-FNM-58662

### PC::O-FNM-15432 | Product Specific | O-FNM
Q: Where the loan is a Texas Equity Section 50(a)(6) loan, were all requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 3
  - [Critical] Remote online notarization, (RON), was used in a Texas Equity Section 50(a)(6) Mortgage -> O-FNM-52716
  - [Critical] TX Sect 50(a)(6) Mg didn't comply with TX Constitution and all requirements -> O-FNM-50324
  - [Critical] The subject is an eMortgage which is not eligible for a Texas Section 50(a)(6) -> O-FNM-51479

### PC::O-FNM-15433 | Product Specific | O-FNM
Q: Were all Community Seconds and Community Land Trusts requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 10
  - [Critical] Title policy/endorsement missing specific req's for community land trust/shared equity transactions -> O-FNM-56359
  - [Critical] Affordable LTV was not calculated appropriately in subject community land trust purchase -> O-FNM-54034
  - [Critical] The subject's community ground lease is not based upon either the NCLTN or ICE ground lease models -> O-FNM-54033
  - [Critical] Community Second mtg was not obtained from an allowable party and/or all requirements not met -> O-FNM-50916
  - [Critical] Minimum borrower contribution requirement was not met for a transaction with a community second loan -> O-FNM-56348
  - [Critical] The community second repayment structure is unacceptable -> O-FNM-56349
  - [Critical] The community second shared appreciation transaction did not meet eligibility requirements -> O-FNM-56351
  - [Critical] The community second shared appreciation transaction did not meet provider requirements -> O-FNM-56350
  - [Critical] Community second shared appreciation transaction did not meet repayment distribution requirements -> O-FNM-56352
  - [Critical] The community second loan proceeds were used toward an unacceptable use of funds -> O-FNM-56347

### PC::O-FNM-15434 | Product Specific | O-FNM
Q: Were all Loans with Resale Restrictions requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 6
  - [Critical] CLT ground lease does not include buyer specific income levels & max sales price limits restrictions -> O-FNM-56358
  - [Critical] Resale restrictions loan req's not met, including property type, amortization, &/or loan purpose -> O-FNM-50327
  - [Critical] The appraisal did not reflect the market value of the property without resale restrictions -> O-FNM-56353
  - [Critical] Borrower eligibility requirements not met for a loan with resale restrictions -> O-FNM-56354
  - [Critical] Source/terms of the resale restrictions not in public land records identifiable in a title search -> O-FNM-56980
  - [Critical] Fannie Mae does not have first claim to insurance settlements and condemnation proceeds -> O-FNM-56981

### PC::O-FNM-15435 | Product Specific | O-FNM
Q: Were all HomeReady requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 10
  - [Critical] HomeReady using boarder income, the boarder is obligated on the mtg or has an ownership interest -> O-FNM-51184
  - [Critical] All HomeReady req's for an LTV, CLTV, or HCLTV Ratio of 95.01 –97% not met -> O-FNM-50328
  - [Critical] HomeReady-No homeowner education by 1 borr where all occupying borr's are 1st time homebuyers -> O-FNM-50330
  - [Critical] A HomeReady and HomeStyle Renovation is combined without all mortgage insurance req's being met -> O-FNM-51185
  - [Critical] The mortgage was ineligible under the HomeReady borrower income limits -> O-FNM-50917
  - [Critical] HomeReady lender-funded grant was funded through premium pricing or another way through the loan -> O-FNM-55905
  - [Critical] Min 3% contribution from own funds/eligible source not made in a HomeReady w/ a lender-funded grant -> O-FNM-55904
  - [Critical] HomeReady lender-funded grant terms & conditions of the grant program is not in the file -> O-FNM-55903
  - [Critical] HomeReady borrower minimum contribution not met with LTV over 80% -> O-FNM-50329
  - [Critical] Credit score insufficient and non-traditional credit requirements not met; FNMA HomeReady product -> O-FNM-00193

### PC::O-FNM-15436 | Insurance | O-FNM
Q: Were all property insurance requirements met including minimum ratings?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 14
  - [Critical] CTP loan and insurance quote was not located to determine premium -> CTPQuote
  - [Critical] Minimum Coverage and/or deductible not met -> FAMCO-FNM-00825
  - [Critical] The insured, mortgagee, property address, type and/or effective dates of coverage are incorrect -> O-FNM-50331
  - [Critical] Ins coverage not the lesser of 100% replacement cost or the UPB at least 80% of the replacement cost -> O-FNM-00825
  - [Critical] The HOI policy cannot be located in the file -> HOICoverage
  - [Major] The premium; deductible; and/or Loan# is not listed on the HOI policy -> HOIData
  - [Minor] The HOI worksheet is missing or incomplete or incorrect -> HOIWork
  - [Critical] The property insurance policy did not provide for claims to be settled on a replacement cost basis -> O-FNM-56251
  - [Critical] The deductible for property insurance perils exceeds 5% of the property insurance coverage amount -> O-FNM-56252
  - [Critical] The property insurance carrier did not meet rating requirements or rating exception requirements -> O-FNM-55828
  - [Critical] Work-related exclusions/limits in coverage in loan-funded repairs, reno's, or energy improvements -> O-FNM-56257
  - [Critical] Policy limits or excludes req'd perils & a stand-alone policy not obtained with adequate coverage -> O-FNM-56250
  - [Critical] Short form cert of property insurance did not show all information and/or not signed by the insurer -> O-FNM-50873
  - [Critical] 1-4 unit property insurance not written on a "special" coverage form or equivalent -> O-FNM-56249

### PC::O-FNM-15437 | Insurance | O-FNM
Q: Were all Condo, Co-op, or PUD Projects property insurance requirements met including minimum ratings?
APPLIES: Loans.QC_Policy = 'Fannie Mae' AND (Loans.LoanType = 'Portfolio' OR Loans.LoanType = 'Portfolio DHM' OR Loans.PropertyType = 'Condminium' OR Loans.PropertyType = 'PUD' OR Loans.Pro
SKIP: no | clean_opts: 2 | defect_opts: 11
  - [Critical] The project fidelity/crime insurance policy not in place or had an improper amount of coverage -> O-FNM-50866
  - [Critical] Unit interior not included in the blanket policy & HO-6 policy not obtained with sufficient coverage -> O-FNM-50870
  - [Critical] The master policy was not written on a broad coverage form that includes the required language -> O-FNM-57522
  - [Critical] The master insurance policy does not provide for claims to be settled on a replacement cost basis -> O-FNM-57521
  - [Critical] Master policy deductible exceeds the 5% max due to a per unit peril deductible w/out an HO-6 policy -> O-FNM-57791
  - [Critical] Master ins doesn't cover 100% replacement value of project improvements/common elements/residences -> O-FNM-50868
  - [Critical] Central heat/cool project policy did not include boiler & machine/eqpt breakdown or was insufficient -> O-FNM-56256
  - [Critical] Policy did not include building ordinance/law coverage or inflation guard coverage as applicable -> O-FNM-56255
  - [Critical] NY purch MI not based on state law, using non-co-op appraised value/co-op sales price w/out IPC adj -> O-FNM-59134
  - [Critical] No evidence of project general liability insurance as applicable or insufficient required coverage -> O-FNM-56263
  - [Critical] Replacement cost coverage not met -> ReplacementCost

### PC::O-FNM-15438 | Insurance | O-FNM
Q: Were all standard flood hazard determination form (SFHDF) and, if required, federal flood insurance requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 3 | defect_opts: 12
  - [Critical] Date of Flood Hazard Determination not within 120 days of Note date and is not a life of loan cert -> O-FRD-00565
  - [Critical] No, loan approved where property is in a CBRS/OPA and not covered by private flood insurance -> O-FNM-00574
  - [Critical] Condo req's flood insurance without verification the HOA maintains a RCBAP or policy is insufficient -> O-FNM-56259
  - [Critical] Co-op req's flood ins - no verification of General Property Form policy/equivalent or insufficient -> O-FNM-56260
  - [Critical] No, a flood zone determination was not made on the SFHDF -> O-FNM-00533
  - [Critical] No, A standard life of loan flood certification is not in the file or ratings not met -> O-FNM-00533
  - [Critical] No, adequate flood insurance coverage was not in effect or applied for as of the date of closing -> O-FNM-00826
  - [Major] Flood insurance coverage calculator not used to determine minimum flood insurance coverage required -> O-BP-54670
  - [Critical] The flood insurance deductible requirements as per property type were not met -> O-FNM-56261
  - [Critical] Flood policy mortgagee clause, insured, or notice of cancellation were not present or were incorrect -> O-FNM-56262
  - [Critical] The residence or detached structure is in an SFHA and the community does not participate in the NFIP -> O-FNM-56258
  - [Critical] Private flood insurance terms/conditions not equal to NFIP &/or insurer did not meet ratings req's -> O-FNM-55380

### PC::O-FNM-15439 | Insurance | O-FNM
Q: Were all loss payee/mortgagee clause requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 2
  - [Major] MERS was named as the loss payee on the property insurance policy -> O-FNM-54105
  - [Critical] Hazard/flood mortgagee clause missing lender/servicer name & “successors and assigns,” as applicable -> O-FNM-54104

### PC::O-FNM-15440 | Loan Documents | O-FNM
Q: Were all electronic records requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 3
  - [Critical] The eMortgage is ineligible due to being a special purpose product that req's add'l legal documents -> O-FNM-51480
  - [Critical] The eMortgage electronic records were not valid and enforceable -> O-FNM-51481
  - [Critical] The electronic record used was in audio or video format -> O-FNM-53858

### PC::O-FNM-15441 | Loan Documents | O-FNM
Q: Were all electronic signature requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 2
  - [Critical] A single electronic signature was applied to multiple electronic records simultaneously -> O-FNM-54102
  - [Critical] E-sign docs disclosure, consent, signature, presentation, delivery, retention & state req's not met -> O-FNM-51482

### PC::O-FNM-15442 | Loan Documents | O-FNM
Q: Were all electronic notarization or Remote Online Notarization (RON) requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 11
  - [Critical] In person or E-notary act not legally valid &/or not in accordance with the subject's state law -> O-FNM-51484
  - [Critical] Remote online notary not licensed &/or not physically located in the state the notary act occurred -> O-FNM-53860
  - [Critical] The subject property county recorder does not accept remotely notarized documents for recording -> O-FNM-53861
  - [Critical] SFC 861 not assigned for remotely notarized security instrument or amendment -> O-FNM-53862
  - [Critical] RON used with a notary not licensed & physically located in the state where notarial act occurred -> O-FNM-52717
  - [Critical] RON recording of notary ceremony not to be maintained the greater of 10 yrs or minimum req'd by law -> O-FNM-52805
  - [Critical] File indicates the borr was required to use RON and other notary options were not provided -> O-FNM-52719
  - [Critical] The remote online notarization, (RON) system used did not meet minimum standards -> O-FNM-52718
  - [Critical] The title contained exceptions for the remotely notarized loan (RON) -> O-FNM-52806
  - [Critical] The subject Texas Section 50(a)(6) was electronically notarized -> O-FNM-51483
  - [Critical] eNotary not compliant with UETA & Electronic Signatures in Global & National Commerce Act -> O-FNM-53859

### PC::O-FNM-15443 | Loan Documents | O-FNM
Q: Were all remote ink-signed notarization (RIN) requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 11
  - [Critical] Remote ink-signed notarization utilized where RIN is not expressly authorized under applicable law -> O-FNM-54551
  - [Critical] RIN notarized documents not recordable by the county recorder of the subject property's state -> O-FNM-54557
  - [Critical] Reps & warrants not met ensuring loan is valid, effective & enforceable 1st lien using a RIN notary -> O-FNM-54558
  - [Critical] The entire remote ink-signed notarization (RIN) audiovisual notarial ceremony was not recorded -> O-FNM-54561
  - [Critical] Signer &/or the notary is not physically located in the state of the notarial act as req'd for RIN -> O-FNM-54553
  - [Critical] Loan not delivered with SFC 920 as required when closed using remote ink-signed notarization (RIN) -> O-FNM-54555
  - [Critical] RIN not legally valid under the state laws and regulations where/when the notarization was performed -> O-FNM-54552
  - [Critical] The RIN process &/or audio-visual communication technology utilized did not meet minimum standards -> O-FNM-54554
  - [Critical] The final title policy contains exceptions regarding documents notarized using a RIN process -> O-FNM-54559
  - [Critical] The RIN process did not include at least two-factor identity authentications -> O-FNM-54560
  - [Critical] Remote ink-signed notarization (RIN) was utilized in a Texas Equity Section 50(a)(6) mortgage -> O-FNM-54556

### PC::O-FNM-15444 | Loan Documents | O-FNM
Q: Were all contents of the application package requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 1 | defect_opts: 4
  - [Critical] The file did not contain escrow/closing or settlement instructions as applicable -> O-FNM-50907
  - [Critical] The final DU Underwriting Analysis Report was not in the file -> O-FNM-50190
  - [Critical] Note/Mtg & final 1003 signed by POA, no initial 1003 signed by the borr & POA doesn't meet exception -> O-FNM-51639
  - [Major] The 1008/1077 or other similar document was incomplete, incorrect or not in file -> O-FNM-00715

### PC::O-FNM-15445 | Loan Documents | O-FNM
Q: Were all security instrument requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 1 | defect_opts: 3
  - [Critical] Power of Attorney (POA) not provided when signed by Atty in fact -> O-FNM-50336
  - [Critical] All parties required to sign did not execute the Security Instrument -> O-FNM-50333
  - [Critical] The Security Instrument is missing or incorrect -> O-FNM-50332

### PC::O-FNM-15446 | Product Specific | O-FNM
Q: Were all NY CEMA Agreement requirements met?
APPLIES: Loans.QC_Policy = 'Fannie Mae' AND Loans.AddressState = 'NY'
SKIP: no | clean_opts: 2 | defect_opts: 1
  - [Critical] NY CEMA missing Form 3172, Consolidation, Extension & Modification Agmt, &/or other req'd exhibits -> O-FNM-54189

### PC::O-FNM-15447 | Loan Documents | O-FNM
Q: Were all note and rider requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 1 | defect_opts: 5
  - [Critical] No, the late charge exceeds the 5% maximum for conventional loans -> O-FNM-50003
  - [Critical] Signature on the Note differs significantly from the typed name & a name affidavit was not obtained -> O-FNM-54539
  - [Critical] No, the Note and/or Security Instrument type is not correct for this mortgage -> O-FNM-50001
  - [Critical] Not all parties req'd to execute the Note signed or did not sign as typed under the signature line -> O-FNM-50334
  - [Critical] A rider to the security instrument is not in the file as required or is unsigned -> O-FNM-50335

### PC::O-FNM-15448 | Loan Documents | O-FNM
Q: Were all Power of Attorney requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 4
  - [Critical] The attorney in fact was an ineligible agent for a power of attorney -> O-FNM-54185
  - [Critical] Required information was not present, was incorrect and/or the POA was not notarized -> O-FNM-54184
  - [Critical] A power of attorney was utilized in an ineligible transaction type -> O-FNM-54183
  - [Critical] POA is title insurer or issuing agent employee without a closing protection letter -> O-FNM-54182

### PC::O-FNM-15449 | Loan Documents | O-FNM
Q: Were all QC closing documents review requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 1 | defect_opts: 1
  - [Critical] No, data on the closing documents is not complete/accurate/compliance with eligibility requirements -> O-FNM-00839

### PC::O-FNM-15451 | Information Integrity | O-FNM
Q: Were all allowable age of credit documents and federal income tax return requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 1 | defect_opts: 4
  - [Critical] IRS 4506–C response or borr evidence that the applicable tax transcripts are unavailable not in file -> O-FNM-56356
  - [Critical] One or more of the credit documents did not meet the allowable age requirement -> O-FNM-00575
  - [Critical] Most recent tax return not filed & IRS Form 4868 w/ conf# and estimated income taxes not in the file -> O-FNM-54125
  - [Critical] Tax liability on Form 4868 was not compared to most recent year obtained for stability/continuance -> O-FNM-56355

### PC::O-FNM-15452 | Information Integrity | O-FNM
Q: Were all accuracy of DU data, DU tolerances, and errors in the credit report requirements met?
APPLIES: Loans.QC_Policy = 'Fannie Mae' AND Loans.Underwriting_Type = 'Desktop Underwriter'
SKIP: no | clean_opts: 1 | defect_opts: 4
  - [Critical] Material data elements entered in DU was not accurate as to how the loan closed -> O-FNM-50246
  - [Critical] The DU report contained "potential red flag" messages that were not addressed -> O-FNM-50248
  - [Critical] Verified income is less than what was submitted to DU and DTI changed more than permitted tolerances -> O-FNM-00350
  - [Critical] Credit report contained derogatory information DU did not recognize & added risk was not considered -> O-FNM-50247

### PC::O-FNM-15453 | Information Integrity | O-FNM
Q: Were all QC data integrity requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 1
  - [Critical] The file does not support that all data submitted to DU is reliable information -> O-FNM-00717

### PC::O-FNM-15454 | Closing | O-FNM
Q: Were all principal curtailment requirements met?
APPLIES: Loans.QC_Policy = 'Fannie Mae'
SKIP: no | clean_opts: 2 | defect_opts: 3
  - [Critical] Principal curtailment applied not used to refund overpayment or to reduce cash out to the borrower -> O-FNM-50231
  - [Critical] The amount of the principal curtailment was not clearly documented -> O-FNM-50232
  - [Critical] Principal curtailment modification original note/modified amount do not comply with loan limits -> O-FNM-55393

### PC::O-FNM-15455 | Closing | O-FNM
Q: Is the electronic closing documentation complete and accurate in accordance with agency/GSE requirements?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 6
  - [Critical] The file did not document who has the right to enforce the Authoritative Copy of the eNote -> O-FNM-58308
  - [Critical] The eNote did not contain a valid unique 18-digit Mortgage Identification Number (MIN) -> O-FNM-58312
  - [Critical] The subject loan had an eMortgage component without tamper-evident security -> O-FNM-58306
  - [Critical] The subject eNote did not contain an eNote clause -> O-FNM-58310
  - [Critical] The eNote Vault System used did not meet the legal, technological, and operational requirements -> O-FNM-58314
  - [Critical] The eNote was not registered with the MERS® eRegistry immediately upon execution by the borrower -> O-FNM-58316

### PC::O-FNM-15456 | Certification, Endorsement, and Delivery | O-FNM
Q: Were all contractual representations and warranties requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 5
  - [Critical] Collateral Underwriter has incorrect property description or inaccurate data -> O-FNM-03122
  - [Critical] The CU risk score exceeded 2.5 and/or other requirements were not met -> O-FNM-50187
  - [Critical] Closed loan data does not agree with final DU &/or omitted data impactful to the DU recommendation -> O-FNM-00579
  - [Critical] No, there are data inconsistencies in the final DU submission -> O-FNM-00876
  - [Critical] SE income calculated with a FNMA approved vendor tool without all req's being met to retain relief -> O-FNM-51067

### PC::O-FNM-15458 | Certification, Endorsement, and Delivery | O-FNM
Q: Were all loan data and document delivery requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 9
  - [Major] The loan has a standby commitment/builder forward commitment and was not delivered with SFC 887 -> O-FNM-57896
  - [Critical] The Note reflects that the 1st payment date is due beyond 2 months from the final disbursement date -> O-FNM-51016
  - [Major] Mtg sold on flow basis over 6 ms from 1st pymt date to purchase ready date or MBS pool issue date -> O-FNM-56599
  - [Major] Post-purchase data element corrections were not submitted timely using FNMA's ADE application -> O-FNM-00873
  - [Minor] No, Loan Delivery data is missing the applicable special feature code -> O-FNM-00872
  - [Major] Subject & separate mailing address not included for borr in Address Confidentiality Program -> O-FNM-55893
  - [Critical] All critical/fatal feedback messages returned by the UCD collection system not reviewed and resolved -> O-UCD-54699
  - [Critical] All specific new ULDD data points not collected on application received on or after 01/01/2019 -> O-ULDD-51108
  - [Minor] No, key loan delivery data was not delivered electronically using Loan Delivery -> O-FNM-00871

### PC::O-FNM-15460 | Product Specific | O-FNM
Q: (Fannie Mae) Was this loan originated under a specific product or program?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 21 | defect_opts: 0

### PC::O-FNM-15625 | Assets | O-FNM
Q: Were all other asset type requirements met?
APPLIES: Loans.QC_Policy = 'Fannie Mae'
SKIP: yes | clean_opts: 2 | defect_opts: 8
  - [Critical] No evidence foreign assets were exchanged into U.S. dollars & held in a U.S./state regulated bank -> O-FNM-55680
  - [Critical] Foreign assets used as a source of funds was not verified in U.S. dollars prior to closing -> O-FNM-55681
  - [Critical] Foreign asset documents was not completed in English or with a complete and accurate translation -> O-FNM-55682
  - [Critical] Nonprofit individual development acct used without documentation of deposits or program -> O-FNM-00291
  - [Critical] All requirements for a pooled savings were not met -> O-FNM-50259
  - [Major] The file did not document the value of the trust account from the trust manager or the trustee -> O-FNM-55667
  - [Major] Borr access to trust & effect withdrawal has on qualifying trust income not documented as applicable -> O-FNM-55668
  - [Critical] The file did not document that the virtual currency source of funds was exchanged for U.S. dollars -> O-FNM-55674

### PC::O-FNM-15843 | Income | O-FNM
Q: Were all military income requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 1 | defect_opts: 5
  - [Critical] Income submitted to AUS is not accurate - broken out and/or categorized correctly -> Income Breakdown
  - [Critical] Military base pay & entitlements was not documented with the most recent leave & earnings statement -> O-FNM-55391
  - [Critical] Military LES not dated within 120 calendar days as req'd when used in lieu of a VVOE -> O-FNM-55392
  - [Critical] "Other" military income (not base pay) was not documented as stable -> O-FNM-50251
  - [Critical] Other military income (not base pay) was not documented as stable -> O-FNM-50251

### PC::O-FNM-15844 | Property - Appraisal | O-FNM
Q: Were all condo or co-op project deferred maintenance requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae') AND (Loans.PropertyType = 'Condominium' OR Loans.PropertyType = 'Cooperative')
SKIP: no | clean_opts: 2 | defect_opts: 8
  - [Critical] [Best Practice] Last 5 yrs project inspections/certifications not reviewed for deferred maintenance -> O-FNM-55423
  - [Critical] [Best Practice] The past 6 months of a condo/co-op project’s HOA meeting minutes were not reviewed -> O-FNM-55422
  - [Critical] Condo/co-op project missing acceptable COO or failed local regulatory inspections or recertification -> O-FNM-55416
  - [Critical] Project missing engineer/inspection report, COO, or other evidence of completed repairs/maintenance -> O-FNM-55415
  - [Critical] Condo/co-op financial documents not obtained to confirm the association has ability to fund repairs -> O-FNM-55418
  - [Critical] Project reason/term of current or planned special assessments not documented to determine acceptable -> O-FNM-55417
  - [Critical] Special assessment is safety/sound/structural or livability & repairs incomplete or adverse impact -> O-FNM-55419
  - [Critical] Condo/co-op project has deferred maintenance or has regulatory directive to repair unsafe conditions -> O-FNM-55414

### PC::O-FNM-15845 | Product Specific | O-FNM
Q: Were all additional conversion of construction-to-permanent (CP) mortgage loan financing requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 10
  - [Critical] Single-close construction perm credit/appraisal docs over 18 mos at conversion - permanent financing -> O-FNM-55406
  - [Critical] Single-close construction perm credit docs/appraisal over 4 mos not over 18 mos without cond's met -> O-FNM-55407
  - [Critical] Down payment requirements were not met for the subject single close construction perm purchase -> O-FNM-55402
  - [Critical] Interim funds not used to buy lot/finance construction in single close construction perm purchase -> O-FNM-55400
  - [Critical] Single close construction perm did not use construction rider/modification agmt for perm conversion -> O-FNM-55408
  - [Critical] Single-close construction perm not UW based on permanent financing terms or was modified & not re-UW -> O-FNM-55405
  - [Critical] Single-close construction perm LTV, CLTV, HCLTV not calculated correctly as per property/loan type -> O-FNM-55401
  - [Critical] The terms of the single-closing construction-to-permanent modified were ineligible for modification -> O-FNM-55404
  - [Critical] The terms of the single-closing construction-to-permanent were modified after the time of conversion -> O-FNM-55403
  - [Critical] Two close construction perm permanent mtg is not a LCO or CO refinance transaction -> O-FNM-55409

### PC::O-FNM-15846 | Property - Appraisal | O-FNM
Q: Where the property has energy-efficient improvements, were all requirements met?
APPLIES: Loans.QC_Policy = 'Fannie Mae'
SKIP: no | clean_opts: 2 | defect_opts: 2
  - [Critical] Subject not built under the IRC as req'd for modular, prefabricated, panelized, or sectional housing -> O-FNM-55388
  - [Critical] The subject's solar panels were not valued properly based on the ownership structure of the panels -> O-FNM-53034

### PC::O-FNM-15928 | Product Specific | O-FNM
Q: Were all additional HomeStyle Renovation mortgage requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 3
  - [Critical] Renovation contract was not fully executed by both the contractor & the borrower prior to closing -> O-FNM-58738
  - [Critical] HomeStyle reno loan agreement not in the file or does not include all req'd elements/provisions -> O-FNM-55517
  - [Critical] HomeStyle loan agreement not executed by the lender & borr at closing on the same date as the note -> O-FNM-55518

### PC::O-FNM-15939 | Product Specific | O-FNM
Q: Were all single closing conversion of construction-to-permanent financing requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 10
  - [Critical] Single-closing construction perm had a single period over 12 mos &/or total period exceeding 18 mos -> O-FNM-55397
  - [Critical] Single-close construction perm credit docs older than 4 mos at conversion - permanent financing -> O-FNM-55406
  - [Critical] Down payment requirements were not met for the subject single close construction perm purchase -> O-FNM-55402
  - [Critical] Lot not owned by borr at 1st advance of interim financing in single close construction perm purchase -> O-FNM-55399
  - [Critical] Interim funds not used to buy lot/finance construction in single close construction perm purchase -> O-FNM-55400
  - [Critical] Single-close construction perm not UW based on permanent financing terms or was modified & not re-UW -> O-FNM-55405
  - [Critical] Single-closing construction perm loan term exceeded 30 years after conversion to permanent financing -> O-FNM-55398
  - [Critical] Single-close construction perm LTV, CLTV, HCLTV not calculated correctly as per property/loan type -> O-FNM-55401
  - [Critical] The terms of the single-closing construction-to-permanent modified were ineligible for modification -> O-FNM-55404
  - [Critical] The terms of the single-closing construction-to-permanent were modified after the time of conversion -> O-FNM-55403

### PC::O-FNM-15940 | Product Specific | O-FNM
Q: Were all additional single closing conversion of construction-to-permanent financing requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 5
  - [Critical] Single-close construction perm credit docs over 4 months but under 12 months without all cond's met -> O-FNM-55407
  - [Critical] Appraisal effective date is over 4 mos old from the note date of the single-close construction perm -> O-FNM-55603
  - [Critical] Single-close construction perm missing completed Form 1004D is not in the file -> O-FNM-55604
  - [Critical] Single-close construction perm Form 1004D indicates decline & new appraisal not obtained/requalified -> O-FNM-55605
  - [Critical] Single close construction perm did not use construction rider/modification agmt for perm conversion -> O-FNM-55408

### PC::O-FNM-15946 | Property - Appraisal | O-FNM
Q: Were all Gross Living Area (GLA) appraisal requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 7
  - [Critical] ANSI min ceiling height not met w/out explaining how ANSI standard was met & use of addt'l sq ft -> O-FNM-55584
  - [Critical] ANSI min ceiling height not met & addt'l sq ft not on addt'l line &/or appropriate adj not applied -> O-FNM-55583
  - [Critical] Detached structures finished square feet not put on a different line &/or not in reported GLA -> O-FNM-55582
  - [Critical] Square Footage Method: ANSI Z765-2021 not used to measure, calculate & report GLA /Non-GLA -> O-FNM-55579
  - [Critical] The finished above-grade GLA, below-grade square footage, &/or room count was inconsistent -> O-FNM-55580
  - [Critical] ANSI Z765-2021 standard not adhered to & explanation of non-compliance was not provided -> O-FNM-55586
  - [Critical] The appraiser's sketching or 3D scanning software output did not conform to ANSI Z765-2021 standards -> O-FNM-55581

### PC::O-FNM-15951 | Assets | O-FNM
Q: Were all secondary financing requirements met?
APPLIES: Loans.QC_Policy = 'Fannie Mae'
SKIP: yes | clean_opts: 1 | defect_opts: 4
  - [Critical] Subordinate financing was allowed on a Co-op share loan without obtaining a policy exception -> O-FNM-50199
  - [Critical] Subordinate lien not evidenced by a note, recorded mtg, &/or not clearly subordinate to 1st mtg lien -> O-FNM-50198
  - [Critical] All re-subordination requirements were not met for refinance transactions -> O-FNM-50201
  - [Critical] The type/terms of subordinate financing unacceptable -> O-FNM-50200

### PC::O-FNM-15952 | Assets | O-FNM
Q: Were all business account asset requirements met?
APPLIES: Loans.QC_Policy = 'Fannie Mae'
SKIP: yes | clean_opts: 1 | defect_opts: 3
  - [Critical] Business assets used as down payment, closing costs or reserves & a cash flow analysis not completed -> O-FNM-02212
  - [Critical] Business assets used as assets to close and the borrower is not listed as an owner of the account -> O-FNM-52793
  - [Critical] File did not document that withdrawal of business assets will not be detrimental to the business -> O-FNM-52792

### PC::O-FNM-16087 | Credit - Liabilities | O-FNM
Q: Were all other monthly debt obligations requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 4
  - [Critical] No written verification for significant open debt(s) on the application but not on the credit report -> O-FNM-00191
  - [Critical] Debts noted as “will rate by mail only” or “need written authorization” were not verified separately -> O-FNM-00194
  - [Critical] Student loan payment not on credit report and the monthly payment was not determined as required -> O-FNM-57257
  - [Critical] Monthly payments on debts secured by virtual currency were not included in the DTI ratio -> O-FNM-55676

### PC::O-FNM-16093 | Loan Documents | O-FNM
Q: Were all Sales Contract requirements met?
APPLIES: Loans.QC_Policy = 'Fannie Mae' AND Loans.LoanPurposeType = 'Purchase'
SKIP: no | clean_opts: 2 | defect_opts: 3
  - [Critical] The sales contract/addenda was incomplete or incorrect -> O-FNM-50192
  - [Critical] A copy of the final sales contract and/or all applicable addenda was not in the file -> O-FNM-50191
  - [Critical] The final sales contract/addenda was not signed by all parties -> O-FNM-50347

### PC::O-FNM-16190 | Product Specific | O-FNM
Q: Were all additional HomeReady requirements met?
APPLIES: Loans.QC_Policy = 'Fannie Mae'
SKIP: yes | clean_opts: 2 | defect_opts: 9
  - [Critical] Borr did not contribute min of 5% from own funds in HomeReady 2-4 w/ lender-funded grant/LTV over 80 -> O-FNM-56091
  - [Critical] LLPA applied & counseling not completed w/in 12 mos PTC & not submitted to DU &/or with SFC 184 -> O-FNM-57898
  - [Critical] HomeReady sweat equity exceeded 2% of the lesser of the purchase price/appraised value in a 2-4 unit -> O-FNM-56233
  - [Critical] HomeReady loan with sweat equity exceeded the maximum LTV of 95% -> O-FNM-56234
  - [Critical] The HomeReady contributory value of the sweat equity was calculated incorrectly -> O-FNM-56235
  - [Critical] The file did not contain the HomeReady sweat equity program provider log -> O-FNM-56236
  - [Critical] The temporary $2,500 LLPA credit was not provided directly to the borrower through the transaction -> O-FNM-57455
  - [Critical] The temporary $2,500 LLPA credit was given in a loan that was not an eligible HomeReady purchase -> O-FNM-57454
  - [Critical] Loan closed with the temporary $2,500 LLPA credit & not delivered with the applicable 900 or 884 SFC -> O-FNM-57456

### PC::O-FNM-16205 | Property - Appraisal | O-FNM
Q: Were all value acceptance + property data requirements met?
APPLIES: Loans.QC_Policy = 'Fannie Mae'
SKIP: yes | clean_opts: 1 | defect_opts: 10
  - [Critical] Property data collection was not obtained after the initial DU offer and prior to the note date -> O-FNM-56228
  - [Critical] Data collection items fail eligibility & a professional report confirming eligibility not obtained -> O-FNM-56231
  - [Critical] Rep & warrant property conditions not met for property data collection needing repairs/completion -> O-FNM-56230
  - [Critical] Property data collection was not submitted to the Property Data API prior to the note date -> O-FNM-57149
  - [Critical] Property data collector not trained with competent knowledge or vetted by an annual background check -> O-FNM-56225
  - [Critical] The property data collection did not meet FNMA's Property Data Standard minimum requirements -> O-FNM-56226
  - [Critical] The loan had a characteristic that was not eligible for value acceptance + property data -> O-FNM-56224
  - [Critical] The value acceptance + property data offer is over 4 months old on the Note date -> O-FNM-56229
  - [Critical] Form 1004D and Completion Alternatives is not in the file as applicable for repairs or alterations -> O-FNM-56232
  - [Critical] SFC 774 was not included at delivery where value acceptance + property data was exercised -> O-FNM-56227

### PC::O-FNM-16231 | Product Specific | O-FNM
Q: Were all shared equity transaction requirements met?
APPLIES: Loans.QC_Policy = 'Fannie Mae'
SKIP: yes | clean_opts: 2 | defect_opts: 9
  - [Critical] The shared equity provider did not meet eligible provider requirements -> O-FNM-56473
  - [Critical] The borrower does not meet the specific eligibility criteria set up by the shared equity program -> O-FNM-56480
  - [Critical] The shared equity community land trust did not meet the required legal documentation requirements -> O-FNM-56474
  - [Critical] The shared equity community land trust is missing Form 2100 signed by the borrower -> O-FNM-56476
  - [Critical] FNMA doesn't have 1st claim to insurance settlements & condemnation proceeds in a shared equity loan -> O-FNM-56478
  - [Critical] The shared equity income & price restrictions did not meet required legal documentation req's -> O-FNM-56475
  - [Major] Private transfer fee doesn't qualify as a excepted transfer fee covenant under 12 C.F.R. § 1228.1(2) -> O-FNM-56472
  - [Critical] The file did not evidence the required counseling for a shared equity loan -> O-FNM-56479
  - [Critical] The property, occupancy, or loan type is ineligible for a shared equity loan -> O-FNM-56481

### PC::O-FNM-16379 | Income | O-FNM
Q: Were all trust income requirements met?
APPLIES: Loans.QC_Policy = 'Fannie Mae'
SKIP: yes | clean_opts: 2 | defect_opts: 9
  - [Critical] Employment-related assets were liquidated to a trust w/in 1 yr of application & did not meet req's -> O-FNM-57140
  - [Critical] Income submitted to AUS is not accurate - broken out and/or categorized correctly -> Income Breakdown
  - [Major] The trust verification documentation did not clearly identify the date the trust was created -> O-FNM-57788
  - [Critical] Trust income is a fixed payment from a depleting asset without documenting 3 years of continuance -> O-FNM-57137
  - [Critical] Trust agmt/trustee stmt/trust tax returns confirming amt, frequency & income type rec'd not provided -> O-FNM-00426
  - [Critical] Trust income pymts are fixed & 12 mos of receipt not documented & did not meet other conditions -> O-FNM-57139
  - [Critical] Trust income pymts are variable & a 24 mos history of receipt not documented with 2 yrs tax returns -> O-FNM-57138
  - [Major] Variable trust income rec'd at least 1 yr but less than 2 yrs used w/out offsetting positive factors -> O-FNM-57789
  - [Critical] The variable trust payment income was not calculated correctly -> O-FNM-57141

### PC::O-FNM-16434 | Income | O-FNM
Q: Were all restricted stock units and restricted stock income requirements met?
APPLIES: Loans.QC_Policy = 'Fannie Mae'
SKIP: yes | clean_opts: 2 | defect_opts: 6
  - [Critical] Income submitted to AUS is not accurate - broken out and/or categorized correctly -> Income Breakdown
  - [Critical] Missing RSU/RS stmt showing previous year(s) distribution & number of vested shares/cash equivalent -> O-FNM-57392
  - [Critical] No documentation RSU/RS is publicly traded &/or is missing the current vesting schedule -> O-FNM-57391
  - [Critical] Missing completed VOE reflecting distributions or a recent paystub showing receipt of RSU/RS income -> O-FNM-57393
  - [Critical] Missing IRS W-2s covering the most recent two-year period reflecting RSU/RS distributions -> O-FNM-57394
  - [Critical] Restricted stock was not documented as vested and distributed to the borrower without restrictions -> O-FNM-57390

### PC::O-FNM-16446 | Property - Appraisal | O-FNM
Q: Does the appraisal evidence unacceptable appraisal practices?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 4
  - [Critical] A disclosure outlining the ROV process not provided at the time the appraisal report was provided -> O-FNM-57786
  - [Critical] The appraisal report contains unacceptable terms and phrases identified as prohibited language -> O-FNM-57524
  - [Critical] All documentation & communications related to the initiation & outcome of the ROV not in the file -> O-FNM-57787
  - [Critical] Review of the appraisal revealed unacceptable appraisal practices were used in the report -> O-FNM-57523

### PC::O-FNM-16519 | Property - Appraisal | O-FNM
Q: Were all requirements met for a property with an accessory dwelling unit?
APPLIES: Loans.QC_Policy = 'Fannie Mae'
SKIP: yes | clean_opts: 2 | defect_opts: 8
  - [Critical] An aged settled sale & an active listing/under contract sale not provided as a supplemental exhibit -> O-FNM-57985
  - [Critical] Appraisal did not include a description of the ADU & effect on value or marketability of the subject -> O-FNM-57984
  - [Critical] The ADU was included with the Gross Living Area calculation of the primary dwelling -> O-FNM-57983
  - [Critical] The ADU is a HUD Code manufactured home and the additional requirements applicable were not met -> O-FNM-57981
  - [Critical] ADU does not comply with zoning requirements or meet the additional conditions to be eligible -> O-FNM-57980
  - [Critical] The subject is an ineligible property type to have an ADU -> O-FNM-57979
  - [Critical] ADU not subordinate in size to the primary dwelling &/or did not have the req'd separate features -> O-FNM-57982
  - [Major] All requirements for a property with an accessory unit not met -> O-FNM-50289

### PC::O-FNM-16635 | Property - Appraisal | O-FNM
Q: Were all additional leasehold estate appraisal requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 6
  - [Critical] Lease includes borr option to purchase & req's not met to establish the purchase price of the land -> O-FNM-58737
  - [Critical] Loan not 1st lien in property improvements & the borrower's rights in leasehold interest in the land -> O-FNM-58734
  - [Critical] All leasehold lease requirements were not met where the HOA or Co-op Corporation is the lessee -> O-FNM-58735
  - [Critical] Appraiser did not comment on effects the lease agreement/ground lease has on value & marketability -> O-FNM-58732
  - [Critical] All leasehold lease requirements were not met where the borrower is the lessee -> O-FNM-58736
  - [Critical] New leasehold on or after 9/1/2025, subject to prior liens & no agreement to not disturb the lease -> O-FNM-58733

### PC::O-FNM-16691 | Application | O-FNM
Q: Were application disclosure requirements met?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 1
  - [Critical] A disclosure outlining the ROV process at the time of loan application was not provided -> O-FNM-59136

### PC::O-FNM-50272 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #1, #2, #3, #7 - Was the subject section of the appraisal complete and accurate including the subject property address, owner of record, county, legal description, parcel ID, as well as neighborhood and occupant information?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-50272

### PC::O-FNM-50280 | Property - Appraisal | O-FNM
Q: Did the appraiser address external influences impacting value or marketability, and did the comparables provided have similar external influences as per aerial image(s)?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No comments found for existing adverse site conditions or external factors -> O-FNM-50280

### PC::O-FNM-50284 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #12 - If a review of the aerial imagery reflects that the improvements do not conform to the neighborhood, did the appraiser provide an explanation?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-50284

### PC::O-FNM-50285 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #26, #27 - Was the GLA and site size of the comparables supported and applied reasonably and consistently across all comparables?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-50285

### PC::O-FNM-50292 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #24 - Did the appraiser assign the most appropriate correct condition/quality rating with report exhibits supporting the ratings, and reconcile to CU messages, if applicable on an appraisal required to be completed with the UAD?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-50292

### PC::O-FNM-50297 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #30 c-d - If the appraiser’s adjusted and unadjusted prices to the comparables do not support the final value indicating that the subject may not conform to the neighborhood, was the final value adequately supported and within the range of unadjusted and/or adjusted values?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-50297

### PC::O-FNM-50298 | Property - Appraisal | O-FNM
Q: Was it confirmed that the appraisal complies with B4-1.1-04, Unacceptable Appraisal Practices, and does not contain subjective or prohibited language?
APPLIES: Loans.QC_Policy = 'Fannie Mae'
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No, the appraisal has not complied with B4-1.1-04 -> O-FNM-50298

### PC::O-FNM-50346 | Property - Appraisal | O-FNM
Q: Did the review appraisal or desk review of the appraisal support the original appraised value?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No, the review appraisal or desk review does not support the original appraised value -> O-FNM-50346

### PC::O-FNM-53852 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #39 - Was it validated that the appraiser is not on Fannie Mae’s AQM list?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: no | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-53852

### PC::O-FNM-53855 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #20 - Were all project eligibility requirements met for the condominium project (e.g., commercial space requirements, owner occupancy, litigation, etc.)?
APPLIES: (Loans.QC_Policy = 'Fannie Mae') AND (Loans.PropertyType = 'Condominium')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-53855

### PC::O-FNM-54343 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #31 - If public sewer and/or water is unavailable, were community or private well and septic facilities available and utilized by the subject property, and was marketability addressed?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-54343

### PC::O-FNM-54346 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #10 - Did the appraisal report identify and describe physical deficiencies that could affect a property’s safety, soundness, or structural integrity?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-54346

### PC::O-FNM-54348 | Property - Appraisal | O-FNM
Q: Were the photos reviewed to confirm the quality and condition ratings meet rating definitions?
APPLIES: Loans.QC_Policy = 'Fannie Mae'
SKIP: no | clean_opts: 2 | defect_opts: 1
  - [Critical] No, the photos do not confirm the quality and conditions meet the rating definitions -> O-FNM-54348

### PC::O-FNM-54350 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #32 - Was a minimum of 3 closed comparables provided in the sales comparison approach?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-54350

### PC::O-FNM-54351 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #30 a-b - After a review of the comparables information reported and photos, are they suitable substitutes for the subject property appealing to the same buyers?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-54351

### PC::O-FNM-54353 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #29 - Where CU messages were present, did the lender ensure all items were resolved and provide comments explaining how they were resolved?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-54353

### PC::O-FNM-54354 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #40 - Did the post-closing QC collateral risk assessment reveal deficiencies noted as significant or findings?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] Yes -> O-FNM-54354

### PC::O-FNM-54358 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #37 -If the property is a cooperative, did the appraiser develop the co-op interest correctly using share price?
APPLIES: (Loans.QC_Policy = 'Fannie Mae') AND (Loans.PropertyType = 'Cooperative')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-54358

### PC::O-FNM-54534 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #15 - If zoning was other than legal, did the appraiser address the ability to rebuild?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-54534

### PC::O-FNM-54535 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #41 - If any deficiencies were noted, were they immaterial to the extent that they would not compromise the quality of the appraisal report or negatively impact the accuracy of the lending decision?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-54535

### PC::O-FNM-54818 | Property - Appraisal | O-FNM
Q: Were the comparable property characteristics reported accurately, comparables described accurately and was the CU comparables tab reviewed for messages and alerts?
APPLIES: Loans.QC_Policy = 'Fannie Mae'
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] Comparable characteristics reported/described inaccurately / CU tab not reviewed for messages/alerts -> O-FNM-54818

### PC::O-FNM-55582 | Property - Appraisal | O-FNM
Q: Were all Gross Living Area (GLA) appraisal requirements met?
APPLIES: Loans.QC_Policy = 'Fannie Mae'
SKIP: yes | clean_opts: 1 | defect_opts: 5
  - [Critical] ANSI min ceiling height not met w/out explaining how ANSI standard was met & use of addt'l sq ft -> O-FNM-55584
  - [Critical] ANSI min ceiling height not met & addt'l sq ft not on addt'l line &/or appropriate adj not applied -> O-FNM-55583
  - [Critical] Detached structures finished square feet not put on a different line &/or not in reported GLA -> O-FNM-55582
  - [Critical] The finished above-grade GLA, below-grade square footage, &/or room count was inconsistent -> O-FNM-55580
  - [Critical] The appraiser's sketching or 3D scanning software output did not conform to ANSI Z765-2021 standards -> O-FNM-55581

### PC::O-FNM-58521 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #34 - Did the appraisal for a 2 to 4-unit property include at least two sales of similar unit count and provide the like-for-like unit comparison or if not, was it addressed?
APPLIES: (Loans.QC_Policy = 'Fannie Mae') AND (Loans.PropertyType = '2-4 unit')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-58521

### PC::O-FNM-58522 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #11 - Were the subject property characteristics reported accurately, including but not limited to GLA, site size, outbuildings, etc.?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-58522

### PC::O-FNM-59378 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #9 - Does the property meet residential, structural, improvements, accessibility, utility, and year-round use eligibility requirements?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-59378

### PC::O-FNM-59379 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #13 - If there is a mix of residential and non-residential properties, was it shown that the mix does not impact the value/marketability of the subject property?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-59379

### PC::O-FNM-59380 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #21, #22 - As part of the collateral risk assessment analysis, was the appraisal reviewed for subjective language and/or unacceptable appraisal practices and was the appropriate exception cited? (Refer to O-FNM-57523 and/or O-FNM-57524 if an exception is applicable.)
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-59380

### PC::O-FNM-59381 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #23 - Was the subject property's description accurate and complete related to the subject property, and project, if applicable?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-59381

### PC::O-FNM-59382 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #25 - Where discrepancies are noted for condition, quality, and/or view/location, was the impact noted on the collateral risk assessment analysis?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-59382

### PC::O-FNM-59383 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #28 - If the subject property has an accessory dwelling unit and/or additional site features, did the appraisal provide comparable sales with similar or consistent accessory dwelling units and/or additional site features?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-59383

### PC::O-FNM-59384 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #33 - Were individual unit rentals supported in the market and did the comparable rents support the appraisers market rent and the gross rent multiplier as indicated by the provided sales?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-59384

### PC::O-FNM-59385 | Fannie Mae Form 1033 | O-FNM
Q: Form 1033 #38 - Did the appraisal report meet Fannie Mae appraisal requirements?
APPLIES: (Loans.QC_Policy = 'Fannie Mae')
SKIP: yes | clean_opts: 2 | defect_opts: 1
  - [Critical] No -> O-FNM-59385

### PC::O-IRS-14660 | Loan Documents | O-IRS
Q: Were all Taxpayer First Act documentation requirements met?
APPLIES: (always)
SKIP: no | clean_opts: 2 | defect_opts: 2
  - [Critical] The express purpose for the 4506-C process & taxpayer express permission to share not in file -> O-IRS-51858
  - [Critical] Indicators exist the tax information was used & information shared other than the purpose granted -> O-IRS-52229

### PC::O-UDAAP-14662 | Information Integrity | O-UDAAP
Q: During the course of the audit, did the file evidence an act that may constitute an unfair, deceptive or abusive practice?
APPLIES: (always)
SKIP: no | clean_opts: 1 | defect_opts: 1
  - [Critical] Yes, the file evidenced an act that may constitute an unfair, deceptive or abusive practice -> O-UDAAP-54639

### PC::Occupancy | Underwriting | Occupancy
Q: Is the occupancy type supported (primary, 2nd, investment) by all documentation in the loan file?
APPLIES: (always)
SKIP: no | clean_opts: 1 | defect_opts: 5
  - [Critical] Appraisal red flags present and were not addressed -> Appr Red Flags
  - [Critical] Insurance red flags present and were not addressed -> Ins Red Flags
  - [Critical] Location of property relative to employer address does not support primary residence -> Location
  - [Critical] Occupancy red flags present and were not addressed (General) -> Occupancy Red Flags
  - [Critical] Servicing billing address does not coincide with occupancy type -> Billing Address

### PC::PropFlip | Property - Appraisal | PropFlip
Q: Are all requirements met when the seller acquired the property within 180 days of the contract ( including Full Appraisal regardless of DU)?
APPLIES: (always)
SKIP: no | clean_opts: 2 | defect_opts: 3
  - [Critical] No, all requirements have not been met to satisfy potential property flip -> FlipGuide
  - [Critical] Assignments of contract sale and not a resale under employee relocation program so is not acceptable -> FlipGuide-2
  - [Critical] The title commitment was not reviewed to search for recorded options, contracts, or transfers -> FlipGuide-1

### PC::SalesContract | Underwriting | SalesContract
Q: Does the sales contract makes reference to a private transfer, reconveyance, recovery, capital recovery or resale fees?
APPLIES: Loans.LoanPurposeType = 'Purchase'
SKIP: no | clean_opts: 1 | defect_opts: 1
  - [Major] Contract shows a private transfer, reconveyance, recovery/capital, or resale fee & is not cleared -> Sales Con-TransFees

### PC::UGV Exception | Product Specific | UGV Exception
Q: Were all Underwriter Guideline Variances (UGV) procedures met?
APPLIES: Loans.LoanType = 'Portfolio'
SKIP: no | clean_opts: 2 | defect_opts: 5
  - [Note] Private Bank approved exceptions including all UGV -> PrivateBank
  - [Critical] Unable to locate approval by Portfolio Rep in Epic and/or Notepad -> UGVAPPRVL
  - [Critical] UGV exception is not properly reflected in EPIC - Expanded & UGV box -> UGV EPIC
  - [Critical] All UGV exceptions are not clearly identified/listed in the Portfolio exception screen -> UGV Identifier
  - [Critical] Underwriter did not have proper lending authority & loan was not escalated to manager -> UGVLendAuth