# YELLOW Rule Conversion Analysis

## Executive Summary

- **Total YELLOW groups**: 2125
- **Total YELLOW rules**: 2147
- **Convertible with known next steps**: 1323 groups (62.3%)
  - Fixture expansion needed: 462
  - Extraction deepening needed: 861
- **Genuinely blocked**: 802 groups (37.7%)
  - SME clarification required: 107
  - Other blockers: 695

## Per-Block Summary

| Block | YELLOW Groups | YELLOW Rules |
|-------|---------------|--------------|
| application-verification | 12 | 16 |
| asset-verification | 193 | 193 |
| credit-liabilities-review | 277 | 277 |
| income-verification | 467 | 482 |
| underwriting-review | 342 | 344 |
| product-specific-check | 572 | 572 |
| property-appraisal-review | 262 | 263 |

## Detailed Breakdown by Blocker Type

### 1. Convertible via Fixture Expansion (462 groups)

These rules are unambiguous and automatable once the synthetic fixture set includes the missing document types.

**application-verification:1** (1 rules)
- Condition: (Best Practice) Documented and verifiable LEP preferences were not obtained from the applicant(s)
- What's needed: LEP preference form/doc type in extraction contract
- Machine-checkable: presence of documented LEP preference record

**application-verification:2** (1 rules)
- Condition: (Best Practice) Limited English Proficiency (LEP) disclosure not provided at the time of application
- What's needed: LEP disclosure doc type + its date field
- Machine-checkable: LEP disclosure presence + provided-date vs application-date

**application-verification:13** (1 rules)
- Condition: It was not evident HUD-92564-CN, For Your Protection: Get a Home Inspection, was provided timely
- What's needed: doc type + provided date
- Machine-checkable: HUD-92564-CN presence

**application-verification:15** (1 rules)
- Condition: No, the executed VA Counseling Checklist is missing or was not provided timely
- What's needed: doc type in inventory
- Machine-checkable: VA Counseling Checklist presence + signature

**application-verification:16** (1 rules)
- Condition: The Informed Consumer Choice Disclosure Notice is missing or was not provided timely
- What's needed: doc type
- Machine-checkable: Informed Consumer Choice Disclosure presence

**application-verification:18** (1 rules)
- Condition: The executed Important Notice to Homebuyers, HUD-92900-B is missing or was not provided timely
- What's needed: doc type
- Machine-checkable: HUD-92900-B presence + signature

**application-verification:35** (4 rules)
- Condition: All sections of URLA Additional Borrower form not fully completed, correct &/or signed as applicable
- What's needed: doc type + fields
- Machine-checkable: initial-URLA Additional Borrower form presence + signature

**application-verification:39** (1 rules)
- Condition: Sections of the initial URLA were incomplete and/or were inaccurate
- What's needed: section-level fields
- Machine-checkable: initial URLA per-section completeness + signatures

**application-verification:40** (1 rules)
- Condition: Sections of the initial URLA were incomplete, inaccurate and/or was not signed
- What's needed: as #39
- Machine-checkable: as #39 (FHA wording variant)

**application-verification:42** (1 rules)
- Condition: The file did not include a fully completed Supplemental Consumer Information Form (Form 1103)
- What's needed: doc type + its fields
- Machine-checkable: Form 1103 (SCIF) presence

**application-verification:47** (1 rules)
- Condition: The file did not include a fully completed Supplemental Consumer Information Form (Form 1103)
- What's needed: as #42
- Machine-checkable: as #42 (FNM variant)

**application-verification:49** (2 rules)
- Condition: A disclosure outlining the ROV process at the time of loan application was not provided
- What's needed: ROV disclosure doc type + date
- Machine-checkable: ROV-process disclosure presence at application

**product-specific-check:6** (1 rules)
- Condition: Final terms/tolerances and conditions for Port Exception were not met
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:8** (1 rules)
- Condition: The DTI exceeds the maximum 50%
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '50%'

**product-specific-check:9** (1 rules)
- Condition: The compensating factors were not met according to credit policy
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:12** (1 rules)
- Condition: Asset dissipation loan and assets were being counted in DU as both income and reserves
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:13** (1 rules)
- Condition: Capital losses reflected on tax returns not considered (A/I & manually UW loans)
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:15** (1 rules)
- Condition: Loan did not meet minimum tradeline requirements
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:16** (1 rules)
- Condition: Port exception granted w/o proper docs and/or no approval by Portfolio Dept located
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:19** (1 rules)
- Condition: The borrower is drawing on SSI and the social security award letter was not located
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:20** (1 rules)
- Condition: The loan closed in an LLC or Trust and all conditions weren't met
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:21** (1 rules)
- Condition: The loan outside of bank's footprint and conditions were not met
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:22** (1 rules)
- Condition: The self employed borrower's YTD P&L's/Balance sheets are not through the most recent quarter
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:23** (1 rules)
- Condition: There is evidence of Non-Arms Length transactions and additional conditions were not met
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:24** (1 rules)
- Condition: Using business accounts as assets, and all criteria was not met (see 3.15.4.7 of Port guides)
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:26** (1 rules)
- Condition: Construction Committee approval was not located or does not match final terms
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:27** (1 rules)
- Condition: Missing 1) CTP draw disb notification and/or CTP Indemnity
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:30** (1 rules)
- Condition: Qualifying RE taxes not calculated using proposed completed value
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:31** (1 rules)
- Condition: The ARB approval was not found
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:32** (1 rules)
- Condition: The CEC approval conditions were not met
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:34** (1 rules)
- Condition: The construction contract does not meet CTP requirements
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:37** (1 rules)
- Condition: No-U/W does not have proper lending auth for this loan amount/product & 2nd level review not found
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:42** (1 rules)
- Condition: The employer is not currently on the approved list
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:43** (1 rules)
- Condition: The loan did not close under one of the approved programs
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:44** (1 rules)
- Condition: RefiNow did not reduce interest rate by at least 50 basis points & the monthly mtg pymt not reduced
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:46** (1 rules)
- Condition: RefiNow all Note signors whose income is used not considered in determining income limit eligibility
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:47** (1 rules)
- Condition: RefiNow total income is not less than or equal to 100% of the AMI limit for the subject's location
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '100%'

**product-specific-check:49** (1 rules)
- Condition: The loan refinanced into a RefiNow was a high LTV refinance, DU Refi Plus loan, or Refi Plus loan
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:50** (1 rules)
- Condition: The loan refinanced into a RefiNow was not a conventional mortgage loan owned or securitized by FNMA
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:51** (1 rules)
- Condition: The loan refinanced into a RefiNow was not seasoned for at least 12 months
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '12 months'

**product-specific-check:52** (1 rules)
- Condition: The loan refinanced into a RefiNow was subject to recourse, repurchase, indem or credit enhancement
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:54** (1 rules)
- Condition: In a RefiNow using military income, the military leave and earnings statement not provided
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:55** (1 rules)
- Condition: RefiNow alimony/child support debt pymts & amount not documented with a divorce decree or equivalent
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:56** (1 rules)
- Condition: RefiNow file did not contain 1 recent statement showing asset balance verifying funds to close
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:57** (1 rules)
- Condition: RefiNow using alimony/child support/maintenance & divorce decree or equiv & 1 mo receipt missing
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:62** (1 rules)
- Condition: RefiNow loan project is a condo or co-op hotel, houseboat, timeshare or segmented ownership project
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:63** (1 rules)
- Condition: The RefiNow loan is not secured by a one-unit principal residence
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:67** (1 rules)
- Condition: Borrowers added/removed on RefiNow loan from the original loan without meeting applicable exceptions
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:68** (1 rules)
- Condition: RefiNow cash out exceeded $250 and/or any excess not applied as a curtailment as applicable
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '$250'

**product-specific-check:69** (1 rules)
- Condition: Subject loan closed as a RefiNow where the RefiNow option was previously used in a prior transaction
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:70** (1 rules)
- Condition: The RefiNow loan is ineligible as a Texas Section 50(a)(6) loan
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:71** (1 rules)
- Condition: The RefiNow loan is ineligible being subject to a temporary interest rate buydown
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:72** (1 rules)
- Condition: The RefiNow loan is not a fixed rate and/or did not meet maximum LTV, CLTV, and HCLTV ratios
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:73** (1 rules)
- Condition: The RefiNow loan is not a limited cash-out refinance
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:74** (1 rules)
- Condition: The RefiNow loan limit does not conform to the general loan limits
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:75** (1 rules)
- Condition: The RefiNow loan was combined with a HomeReady refinance transaction
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:77** (1 rules)
- Condition: New subordinate P&I increased from the existing subordinated loan in a RefiNow simultaneous refi
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:78** (1 rules)
- Condition: New subordinate financing permitted in a RefiNow that did not have existing subordinate financing
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:80** (1 rules)
- Condition: RefiNow has existing subordinate loan satisfied using loan proceeds &/or was not subordinated
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:82** (1 rules)
- Condition: A RefiNow was manually underwritten without LTV, DTI ratio and credit score requirements being met
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:83** (1 rules)
- Condition: No FNMA approval for the variance or exception impactful to underwriting/eligibility in a RefiNow
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:84** (1 rules)
- Condition: RefiNow original loan had a 30-day late in the last 6 mos &/or more than one 30-day late in mos 7-12
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '30-day'

**product-specific-check:85** (1 rules)
- Condition: RefiNow with a non-occupant borrower did not meet the maximum LTV, CLTV, and HCLTV ratio of 95%
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '95%'

**product-specific-check:87** (1 rules)
- Condition: The RefiNow DTI ratio exceeds 65%
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '65%'

**product-specific-check:89** (1 rules)
- Condition: 1 yr ARM with LTV of 95% or more, does not qualify with initial interest rate plus 1% point
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '95%'

**product-specific-check:90** (1 rules)
- Condition: Incorrect initial interest rate/margin per ARM type &/or initial interest rate adjustment incorrect
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:92** (1 rules)
- Condition: Cash-out loan proceeds allowed to be used for purposes not allowed as per FNMA requirements
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:93** (1 rules)
- Condition: Cash-out refinance with delayed financing did not document the source of funds for the purchase
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:94** (1 rules)
- Condition: Delayed financing cashout refi did not confirm a mtg not used to obtain the subject & no liens exist
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:95** (1 rules)
- Condition: First mtg PIF by subject CO refi not at least 12 mos old from prior note date to subject note date
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '12 months'

**product-specific-check:96** (1 rules)
- Condition: In a cash-out refi, no evidence the listed property was taken off the market prior to disbursement
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:97** (1 rules)
- Condition: Loan amt more than borr's initial purchase plus all costs to close in a CO refi w/ delayed financing
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:98** (1 rules)
- Condition: No borrower on title for at least 6 mos prior to disbursement & did not meet ownership exceptions
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '6 months'

**product-specific-check:99** (1 rules)
- Condition: Proceeds from the cash-out refinance were used to pay off an installment land contract
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:107** (1 rules)
- Condition: Ineligible for LCO as there is not an outstanding lien and not a con-perm
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:108** (1 rules)
- Condition: LCO inelig due to short term/consolidated refi to a new 1st mtg < 6 months
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '6 months'

**product-specific-check:110** (1 rules)
- Condition: Manual UW LCO financed payment of the subject's taxes over 60 days in arrears
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '60 days'

**product-specific-check:111** (1 rules)
- Condition: No borrower on the LCO was a current owner at the time of the initial app & does not meet exceptions
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '12 months'

**product-specific-check:112** (1 rules)
- Condition: Subject listed for sale w/out evidence it was off the market on/before disbursement of the new loan
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:115** (1 rules)
- Condition: The subordinate lien paid in LCO refi was not obtained to buy the property
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:119** (1 rules)
- Condition: Funds to close exceeded new streamline refi mtg pymt & were not verified
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:121** (1 rules)
- Condition: STR refi amortization period > than remaining amortization period of existing Mtg +12 yrs or 30 yrs
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '12 years'

**product-specific-check:122** (1 rules)
- Condition: Streamline refi transaction includes cash back in excess of minor adjustments exceeding $500
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '$500'

**product-specific-check:124** (1 rules)
- Condition: Streamline refinance - borrower did not receive a net tangible benefit
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:126** (1 rules)
- Condition: The subject streamline refinance PITI exceeds the original PITI by more than $50
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '$50'

**product-specific-check:127** (1 rules)
- Condition: The subject streamline refinance was not manually underwritten
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:129** (1 rules)
- Condition: All additional requirements not met based on LTV and/or loan type
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '95%'

**product-specific-check:130** (1 rules)
- Condition: Evidence all parties agreed to the terms of the short sale/pre-foreclosure
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:135** (1 rules)
- Condition: The borrower(s) received cash back in an amount exceeding purchase money transaction guidelines
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:137** (1 rules)
- Condition: The purchase price &/or any earnest money deposit was designated in virtual currency
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:138** (1 rules)
- Condition: LTV not calc by dividing the new loan amt by lesser of total acq cost or appraised value at closing
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:140** (1 rules)
- Condition: Subject not UW as a LCO when p/o of land contract was executed more than 12 mos before application
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '12 months'

**product-specific-check:141** (1 rules)
- Condition: Subject not UW as a purchase when p/o of land contract was executed within 12 mos before application
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '12 months'

**product-specific-check:144** (1 rules)
- Condition: File did not evidence the appraiser was provided a copy of the final sales contract & any amendments
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:148** (1 rules)
- Condition: All max CLTV and mortgage amount limits not met based on the refinance program type
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:149** (1 rules)
- Condition: Amount of the refund credit to reduce the UFMIP was incorrect for FHA to FHA refi within 3 years
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '3 years'

**product-specific-check:151** (1 rules)
- Condition: Subject refi is replacing a mtg that has been condemned or seized by a state or municipality
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:153** (1 rules)
- Condition: Land contract for deed considered no cashout refi but contract dated >12mos
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '12 months'

**product-specific-check:155** (1 rules)
- Condition: A CO refi with a note date 30 days or less before the application date of the subject LCO refi
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '30 days'

**product-specific-check:161** (1 rules)
- Condition: ARM with a lifetime floor, it does not equal the margin stated in the note
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:163** (1 rules)
- Condition: Section 4(D) of the ARM Note was incomplete or incorrect
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:165** (1 rules)
- Condition: The Note and Riders did not contain the updated index “fallback” language in a non-SOFR ARM loan
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:166** (1 rules)
- Condition: The lifetime floor was not equal to the margin stated in the Note in an ARM loan
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:167** (1 rules)
- Condition: The subject ARM did not use the 30-day Average SOFR Index
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '30-day'

**product-specific-check:168** (1 rules)
- Condition: The updated 30 day Average SOFR-index ARM Note and Rider was not used as applicable
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '30 day'

**product-specific-check:170** (1 rules)
- Condition: 3/6 month SOFR ARM qualifying rate not equal to the Note rate plus Life Cap (5%)
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '6 month'

**product-specific-check:171** (1 rules)
- Condition: 5/6 month SOFR ARM qualifying rate not equal to  greater of Note Rate + 2% or fully indexed rate
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '6 month'

**product-specific-check:172** (1 rules)
- Condition: 7/6 or 10/6 month HPCT/HPML SOFR ARM, qualifying rate not greater of Note Rate or fully indexed rate
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '6 month'

**product-specific-check:173** (1 rules)
- Condition: SOFR ARM 3/6, 5/6, 7/6 or 10/6 initial fixed rate period is not 36, 60, 84 or 120 mos as applicable
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '6 month'

**product-specific-check:175** (1 rules)
- Condition: Loan underwritten at the incorrect interest rate based on ARM type
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:176** (1 rules)
- Condition: The ARM product index is not a CMT rate
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:178** (1 rules)
- Condition: A SOFR ARM underwritten by DU was not submitted as a generic ARM
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:179** (1 rules)
- Condition: All characteristics in Standard ARM Plan Matrix not met
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:180** (1 rules)
- Condition: Fully indexed rate is not the index value in effect during the 90 days that precede the note date
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '90 days'

**product-specific-check:181** (1 rules)
- Condition: Fully indexed rate not the sum of the applicable index & the mtg margin rounded to the nearest 1/8%
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '8%'

**product-specific-check:182** (1 rules)
- Condition: One or more standard ARM requirements were not met
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:184** (1 rules)
- Condition: The Note and Riders did not contain the updated index “fallback” language in a non-SOFR ARM loan
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:187** (1 rules)
- Condition: ATR 3-year ARM qualifying rate is not equal to the Note Rate + 5%
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '3-year'

**product-specific-check:188** (1 rules)
- Condition: ATR 5-year ARM qualifying rate not equal to greater of fully indexed rate or Note Rate + 2%
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '5-year'

**product-specific-check:189** (1 rules)
- Condition: ATR 7 or 10-year ARM qualifying rate not equal to greater of fully indexed rate or Note Rate
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '10-year'

**product-specific-check:190** (1 rules)
- Condition: ATR covered 3 yr ARM maximum interest rate ceiling exceeds the note rate plus the lifetime cap
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '3 year'

**product-specific-check:191** (1 rules)
- Condition: ATR covered 5 yr ARM max interest rate ceiling exceeds the note rate plus the first rate change cap
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '5 year'

**product-specific-check:192** (1 rules)
- Condition: All eligibility requirements not met for Convertible ARM loans
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:193** (1 rules)
- Condition: Loan amt over term not used to calculate periodic pymts of P&I for short term ARM ATR covered loan
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:198** (1 rules)
- Condition: Alteration/repair loan, subject not owned & occupied or made to purchase the property
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:200** (1 rules)
- Condition: Affordable LTV was not calculated appropriately in subject community land trust purchase
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:202** (1 rules)
- Condition: Community second shared appreciation transaction did not meet repayment distribution requirements
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:203** (1 rules)
- Condition: Minimum borrower contribution requirement was not met for a transaction with a community second loan
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:205** (1 rules)
- Condition: The community second loan proceeds were used toward an unacceptable use of funds
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:206** (1 rules)
- Condition: The community second repayment structure is unacceptable
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:207** (1 rules)
- Condition: The community second shared appreciation transaction did not meet eligibility requirements
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:208** (1 rules)
- Condition: The community second shared appreciation transaction did not meet provider requirements
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:209** (1 rules)
- Condition: The subject's community ground lease is not based upon either the NCLTN or ICE ground lease models
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:212** (1 rules)
- Condition: Energy efficient loan file did not contain a copy of the home energy report
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:213** (1 rules)
- Condition: Verification the amount added to the mtg meets HUD energy efficient program requirements not in file
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:215** (1 rules)
- Condition: IRRRL w/ energy efficiency improvements missing documentation as required for amounts up to $6,000
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '$6,000'

**product-specific-check:220** (1 rules)
- Condition: All repair completion escrow requirements were not met in this Section 203(b) with repair escrow
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:221** (1 rules)
- Condition: HUD REO 203(k) or 203(b) using Good Neighbor Next Door or $100 Down did not meet all requirements
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '$100'

**product-specific-check:224** (1 rules)
- Condition: HUD-92544, Warranty of Completion of Construction, missing builder's name, address, and phone number
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:225** (1 rules)
- Condition: HUD-92544, Warranty of Completion of Construction, missing lender's name, address, and phone number
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:226** (1 rules)
- Condition: HUD-92544, Warranty of Completion of Construction, was missing manufacturer's info, as applicable
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:227** (1 rules)
- Condition: HUD-92544, Warranty of Completion of Construction, was missing the FHA Case Number
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:228** (1 rules)
- Condition: HUD-92544, Warranty of Completion of Construction, was missing the name of the purchaser/owner
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:229** (1 rules)
- Condition: HUD-92544, Warranty of Completion of Construction, was missing the property address
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:230** (1 rules)
- Condition: HUD-92544, Warranty of Completion of Construction, was missing the purchaser's signature and date
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:231** (1 rules)
- Condition: HUD-92544, Warranty of Completion of Construction, was missing warrantor's title, signature, & date
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:232** (1 rules)
- Condition: New construction loan file did not contain form HUD-92544, Warranty of Completion of Construction
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:234** (1 rules)
- Condition: A HomeReady and HomeStyle Renovation is combined without all mortgage insurance req's being met
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:236** (1 rules)
- Condition: Credit score insufficient and non-traditional credit requirements not met; FNMA HomeReady product
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:237** (1 rules)
- Condition: HomeReady borrower minimum contribution not met with LTV over 80%
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '80%'

**product-specific-check:238** (1 rules)
- Condition: HomeReady lender-funded grant terms & conditions of the grant program is not in the file
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:239** (1 rules)
- Condition: HomeReady lender-funded grant was funded through premium pricing or another way through the loan
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:240** (1 rules)
- Condition: HomeReady using boarder income, the boarder is obligated on the mtg or has an ownership interest
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:241** (1 rules)
- Condition: HomeReady-No homeowner education by 1 borr where all occupying borr's are 1st time homebuyers
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:242** (1 rules)
- Condition: Min 3% contribution from own funds/eligible source not made in a HomeReady w/ a lender-funded grant
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '3%'

**product-specific-check:243** (1 rules)
- Condition: The mortgage was ineligible under the HomeReady borrower income limits
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:246** (1 rules)
- Condition: HomeStyle Energy financed improvements that are not on the list of ENERGY STAR Efficient Products
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:247** (1 rules)
- Condition: HomeStyle Energy financing used to pay off energy-related debt did not pay the entire debt in full
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:248** (1 rules)
- Condition: HomeStyle alt documentation (besides an energy report) used w/out meeting qualified circumstances
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:249** (1 rules)
- Condition: HomeStyle energy report did not contain savings, recomm improvements, cost-effect &/or est cost
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:250** (1 rules)
- Condition: HomeStyle energy report did not meet HERS, DOE, or comparable independent and certified standards
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:251** (1 rules)
- Condition: HomeStyle loan missing an energy report or report was dated more than 24 mons before the note date
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '24 months'

**product-specific-check:254** (1 rules)
- Condition: HomeStyle Construction Contract and Loan Agrmt incomplete or unclear title
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:255** (1 rules)
- Condition: HomeStyle LCO, funds after reno not a curtailment or reimburse to borr for costs &/or no receipts
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:256** (1 rules)
- Condition: Homestyle LTV not from lesser of "as completed" or sale price + rehab costs
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:258** (1 rules)
- Condition: The cost of the renovations exceeded the allowable amount as per property and transaction type
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:259** (1 rules)
- Condition: The renovation escrow account did not meet all HomeStyle Renovation loan requirements
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:261** (1 rules)
- Condition: IRRRL surviving spouse funding fee exemption without documenting receipt of DIC & VA Form 26-8937
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:262** (1 rules)
- Condition: In an IRRRL transaction, a final signed Veteran's Statement was not in the file
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:263** (1 rules)
- Condition: Missing Veteran's cert of occupancy 1820 that they previously occupied the property as their home
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:267** (1 rules)
- Condition: IRRRL file did not contain supporting docs of the cure, completion date & already completed actions
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:268** (1 rules)
- Condition: IRRRL replacing the existing VA loan is not the 1st lien on the property w/out a subordination agrmt
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:269** (1 rules)
- Condition: No, in an IRRRL, the prior VA loan was not current on the day before closing
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:270** (1 rules)
- Condition: No, the IRRRL certification of prior VA loan non-delinquency status was not submitted to VA
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '30 days'

**product-specific-check:271** (1 rules)
- Condition: Noncompliant IRRRL has a curative action that resulted in additional costs to the borrower
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:273** (1 rules)
- Condition: Energy Efficient Mortgage dedicated funds not excluded from the statutory fee recoupment calculation
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:274** (1 rules)
- Condition: The fee recoupment was not calculated correctly
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:276** (1 rules)
- Condition: Fixed refi to ARM IRRRL and the interest rate was not at least 2% lower than the original rate
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '2%'

**product-specific-check:277** (1 rules)
- Condition: Fixed refi to fixed IRRRL and the interest rate was not at least 0.50% lower than the original rate
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '0.50%'

**product-specific-check:278** (1 rules)
- Condition: IRRRL resulted in lower P&I without certification of recoupment within 36 months from closing
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '36 months'

**product-specific-check:279** (1 rules)
- Condition: IRRRL resulted in same or higher  P&I pymt without certification only customary costs were incurred
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:280** (1 rules)
- Condition: Loan not closed at no cost to the Vet & monthly PI not reduced by the IRRRL from the original ARM PI
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:281** (1 rules)
- Condition: New IRRRL PITI increased 20% or more without certifying the Veteran qualifies for the new payment
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '20%'

**product-specific-check:282** (1 rules)
- Condition: New loan term exceeds the original being refinanced + 10 yrs/exceeded 30 years & 32 days
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '30 years'

**product-specific-check:284** (1 rules)
- Condition: Completed VA Form 26-8923, IRRRL Worksheet not in file &/or the ln amt calculated incorrectly
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:287** (1 rules)
- Condition: File missing Veteran certification that the refi to IRRRL Loan Comparison Statements were received
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:288** (1 rules)
- Condition: Final loan disclosure not uploaded during LGC process for recoupment period of 36 months or less
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '36 months'

**product-specific-check:289** (1 rules)
- Condition: IRRRL seasoning not met at least 210 days since 1st mtg pymt &/or not current last 6 consecutive mos
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '210 days'

**product-specific-check:290** (1 rules)
- Condition: Lender’s Certification not in the file for IRRRL as req'd if payment increased by 20% or more
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '20%'

**product-specific-check:291** (1 rules)
- Condition: Recoupment calculation not uploaded during LGC process for recoupment period greater than 36 months
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '36 months'

**product-specific-check:296** (1 rules)
- Condition: Borrower eligibility requirements not met for a loan with resale restrictions
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:297** (1 rules)
- Condition: Borrower ineligible for property with income-based resale restrictions as per subsidy provider
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:298** (1 rules)
- Condition: CLT ground lease does not include buyer specific income levels & max sales price limits restrictions
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:299** (1 rules)
- Condition: Fannie Mae does not have first claim to insurance settlements and condemnation proceeds
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:300** (1 rules)
- Condition: Financial obligation req's not met &/or not subordinate to first mtg subject to resale restrictions
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:301** (1 rules)
- Condition: LTV/TLTV/HTLTV incorrect per resale restrictions that survive or terminate foreclosure as applicable
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:303** (1 rules)
- Condition: Property subject to resale restrictions without any right of first refusal requirements being met
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:305** (1 rules)
- Condition: Resale restrictions survive foreclosure/deed-in-lieu & comps do not have similar resale restrictions
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:307** (1 rules)
- Condition: Source/terms of the resale restrictions not in public land records identifiable in a title search
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:308** (1 rules)
- Condition: Terms of the resale restrictions not in public land records discoverable by a routine title search
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:311** (1 rules)
- Condition: NY CEMA missing Form 3172, Consolidation, Extension & Modification Agmt, &/or other req'd exhibits
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:313** (1 rules)
- Condition: A copy of the tribe's lease for use on residential land is not in the file
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:314** (1 rules)
- Condition: Native American restricted land security interest was not approved by the Secretary of the Interior
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:315** (1 rules)
- Condition: Native American restricted trust or restricted land will not remain in trust or restricted status
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:316** (1 rules)
- Condition: No evidence the tribe has enacted legally binding and effective foreclosure/eviction procedures
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:317** (1 rules)
- Condition: No evidence the tribe has procedures ensuring the guaranteed loan will always have 1st lien priority
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:320** (1 rules)
- Condition: The mortgage does not cover both property improvements and the leasehold interest in the land
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:321** (1 rules)
- Condition: The tribe's lease does not meet lease requirements
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:322** (1 rules)
- Condition: An escrow of funds for postponed completion of improvements not established as required
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:325** (1 rules)
- Condition: Missing Vet acknowledgement that 1 yr builder warranty or 10 yr insured protection plan not provided
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:326** (1 rules)
- Condition: Missing no construction warranty where Veteran borr is general contractor building subject primary
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:328** (1 rules)
- Condition: Model home used to obtain value without stating the model home is the same plan type as the subject
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:330** (1 rules)
- Condition: VA LAPP new construction file did not document enrollment in a 10-year insured protection plan
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '10-year'

**product-specific-check:331** (1 rules)
- Condition: VA construction compliance inspection req's not met per stage in proposed/under construction
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:332** (1 rules)
- Condition: Veteran not given Form 26-1859, Warranty of Completion of Construction or 10 yr insurance warranty
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '1-year'

**product-specific-check:334** (1 rules)
- Condition: A Consolidated Note not in the file for a New York CEMA loan
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:335** (1 rules)
- Condition: All required exhibits (A-D) not provided for New York CEMA
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:336** (1 rules)
- Condition: NY CEMA consolidated note, original old & new money note was not a copy of the entire note
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:338** (1 rules)
- Condition: Sect 203(h)-Borr did not have a minimum credit score of 500 as required for the program
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:340** (1 rules)
- Condition: Sect 203(h)-No evidence prior home was PDMDA & damaged to req reconstruction/replacement
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:341** (1 rules)
- Condition: Sect 203(h)-The subject property is not the borrower’s principal residence
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:343** (1 rules)
- Condition: Sect 203(h)-All additional underwriting and eligibility requirements not met
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:346** (1 rules)
- Condition: Supplemental loan-improvements or repairs not for the purpose of improving basic livability/utility
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:349** (1 rules)
- Condition: Private Bank approved exceptions including all UGV
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:351** (1 rules)
- Condition: Unable to locate approval by Portfolio Rep in Epic and/or Notepad
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:352** (1 rules)
- Condition: Underwriter did not have proper lending authority & loan was not escalated to manager
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:353** (1 rules)
- Condition: Borr did not contribute min of 5% from own funds in HomeReady 2-4 w/ lender-funded grant/LTV over 80
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '5%'

**product-specific-check:354** (1 rules)
- Condition: HomeReady loan with sweat equity exceeded the maximum LTV of 95%
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '95%'

**product-specific-check:355** (1 rules)
- Condition: HomeReady sweat equity exceeded 2% of the lesser of the purchase price/appraised value in a 2-4 unit
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '2%'

**product-specific-check:356** (1 rules)
- Condition: LLPA applied & counseling not completed w/in 12 mos PTC & not submitted to DU &/or with SFC 184
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '12 months'

**product-specific-check:357** (1 rules)
- Condition: Loan closed with the temporary $2,500 LLPA credit & not delivered with the applicable 900 or 884 SFC
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '$2,500'

**product-specific-check:359** (1 rules)
- Condition: The HomeReady contributory value of the sweat equity was calculated incorrectly
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:360** (1 rules)
- Condition: The file did not contain the HomeReady sweat equity program provider log
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:361** (1 rules)
- Condition: The temporary $2,500 LLPA credit was given in a loan that was not an eligible HomeReady purchase
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '$2,500'

**product-specific-check:362** (1 rules)
- Condition: The temporary $2,500 LLPA credit was not provided directly to the borrower through the transaction
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '$2,500'

**product-specific-check:364** (1 rules)
- Condition: HomeStyle reno loan agreement not in the file or does not include all req'd elements/provisions
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:367** (1 rules)
- Condition: Min down payment req's not met based on resale-restricted price for income-based resale restrictions
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:368** (1 rules)
- Condition: Model Declaration not used as best practice for the subject income-based resale restricted property
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:370** (1 rules)
- Condition: Property type & occupancy requirements not met when subject to income-based resale restrictions
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:371** (1 rules)
- Condition: Resale restriction controls not administered by subsidy provider or program administrator as req'd
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:372** (1 rules)
- Condition: The product is ineligible for a property is subject to income-based resale restrictions
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:373** (1 rules)
- Condition: All construction exhibits including the survey/plot plan, plans & specs & elevations not in the file
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:375** (1 rules)
- Condition: Documentation not in file supporting acquisition costs included in a 1-time/2-time construction loan
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:376** (1 rules)
- Condition: Subject loan is a conversion to another loan type from a VA one-time or two-time construction loan
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:379** (1 rules)
- Condition: The maximum loan amount for the construction one-time or two-time was not calculated correctly
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:382** (1 rules)
- Condition: A draw and disbursement ledger was not in the file if applicable
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:383** (1 rules)
- Condition: A rehab and repair feature without documenting the home has been complete for 12 months or more
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '12 months'

**product-specific-check:384** (1 rules)
- Condition: Excess construction proceeds given as cash back and not applied as a principal reduction
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:387** (1 rules)
- Condition: Not all of the loan costs were eligible in a rehabilitation & repair loan
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:388** (1 rules)
- Condition: Single-close credit document(s) exceed age requirements as of the actual/scheduled closing date
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '120 days'

**product-specific-check:389** (1 rules)
- Condition: Structural repairs over $75,000 did not meet habitable timeline for PITI reserves w/o an extension
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '$75,000'

**product-specific-check:390** (1 rules)
- Condition: Subject included rehab & repair feature w/ financed amt for non-structural repairs exceeding $75,000
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '$75,000'

**product-specific-check:391** (1 rules)
- Condition: Subject not habitable w/in 30 days of closing w/ a rehab & repair feature for non-structural repairs
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '30 days'

**product-specific-check:392** (1 rules)
- Condition: The file did not contain the closing statement and/or it was incorrect
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:394** (1 rules)
- Condition: Commercial space exceeds max 20% square footage
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '20%'

**product-specific-check:395** (1 rules)
- Condition: Financial statements not obtained for the past 2 years with HDFC approval
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '2 years'

**product-specific-check:396** (1 rules)
- Condition: Flip tax exceeds 5% of the appraised value
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '5%'

**product-specific-check:397** (1 rules)
- Condition: Ground lease term expires prior to the 35 year requirement from loan closing
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '35 year'

**product-specific-check:398** (1 rules)
- Condition: Insider Units to existing tenants are ineligible for SONYMA
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:399** (1 rules)
- Condition: New conversion eviction plans are not eligible
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:400** (1 rules)
- Condition: No reserve limit found for a project with capital repairs
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:401** (1 rules)
- Condition: Project exceeds the minimum 500 square footage
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:402** (1 rules)
- Condition: Project is self managed and does not meet investor requirements
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:403** (1 rules)
- Condition: Prop Lease/Occup agreement does not have remaining term at least = the term of the loan
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:404** (1 rules)
- Condition: Tax abatement ( if applicable ) not obtained and/or expiration date is not provided
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:405** (1 rules)
- Condition: Terms of Underlying Mtg not provided and/or does not have at least 3 year remaining on term
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '3 year'

**product-specific-check:406** (1 rules)
- Condition: The owners maintenance payments exceeds the 15% maximum
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '15%'

**product-specific-check:407** (1 rules)
- Condition: The pro rata underlying mtg exceeds 35% of the lower of sales price or appraised value
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '35%'

**product-specific-check:408** (1 rules)
- Condition: The project exceeds the 10 Unit minimum
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:412** (1 rules)
- Condition: Single close construction perm did not use construction rider/modification agmt for perm conversion
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:414** (1 rules)
- Condition: Single-close construction perm credit docs over 4 months but under 12 months without all cond's met
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '4 months'

**product-specific-check:417** (1 rules)
- Condition: Cash-out refi not secured by first lien position on the property without a subordination agreement
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:419** (1 rules)
- Condition: Interest rate reduction req not met in VA-VA Type I refi as per the orig rate type & new rate type
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:421** (1 rules)
- Condition: LTV in a refinance transaction including the financed funding fee if applicable exceeded 100%
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '100%'

**product-specific-check:423** (1 rules)
- Condition: The fee recoupment was miscalculated in a VA-to-VA TYPE I cash-out refinance
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:424** (1 rules)
- Condition: The recoupment period exceeds 36 months in a VA-to-VA TYPE I cash-out refinance
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '36 months'

**product-specific-check:425** (1 rules)
- Condition: VA refinance seasoning requirement not met as applicable based on refi type and loan terms
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:426** (1 rules)
- Condition: Veteran was not provided a net tangible benefit test (NTB) as required in a refinance transaction
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:427** (1 rules)
- Condition: A single-close purchase was not coded as Construction Only in GUS/GLS
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:428** (1 rules)
- Condition: Additional funds disbursed at closing not covering the land cost in a construction single-close mtg
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:429** (1 rules)
- Condition: Construction Rider/Note Allonge or Construction Loan Agreement not included in a single-close mtg
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:430** (1 rules)
- Condition: Construction month pymt not paid by borr or an established interest reserve
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:432** (1 rules)
- Condition: Ineligible loan costs were included in the amount financed in a single-close mortgage
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:433** (1 rules)
- Condition: Single-close did not include PITI of subject & pending sale primary & exclusion conditions not met
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:434** (1 rules)
- Condition: Single-close mortgage, the construction contractor or builder did not meet RHS builder requirements
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:436** (1 rules)
- Condition: The property type was ineligible for a combination construction and permanent loan
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:437** (1 rules)
- Condition: The subject included a rehab and repair feature for a loan purpose that is prohibited
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:439** (1 rules)
- Condition: Borrowers written authorization not obtained for each draw prior to disbursement to the contractor
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:442** (1 rules)
- Condition: No title update after conversion evidencing property is free & clear of all liens other than the mtg
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:444** (1 rules)
- Condition: A CO or equivalent missing in construction perm unimproved lot and the construction of a residence
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:445** (1 rules)
- Condition: Construction perm FNMA uniform mtg instruments not used or altered for construction reference
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:447** (1 rules)
- Condition: Ineligible Conversion of Con-to-Perm Financing, lot not owned or acquired as part of transaction
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:449** (1 rules)
- Condition: The subject property type was ineligible for construction to permanent financing
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:450** (1 rules)
- Condition: Two-closing construction perm w/ cost overruns not paid directly to the builder at closing
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:453** (1 rules)
- Condition: 1 comp from outside & inside the subdivision/project not provided for the subject in new subdivision
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:456** (1 rules)
- Condition: Lender did not certify on HUD-92800.5B, the property is 100% complete and meets HUD’s MPR and MPS
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '100%'

**product-specific-check:457** (1 rules)
- Condition: New construction loan file did not contain form HUD-92544, Warranty of Completion of Construction
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:458** (1 rules)
- Condition: Safety, structural soundness incl not limited to flood areas, airport hazards not addressed
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:459** (1 rules)
- Condition: The Construction maximum mortgage amount was not calculated correctly
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:462** (1 rules)
- Condition: Construction less than 90% complete, floor plan, plot plan & size/finish exhibits not documented
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '90%'

**product-specific-check:463** (1 rules)
- Condition: HUD-92541, Builder’s Certification of Plans, Specifications, and Site was not in the loan file
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:464** (1 rules)
- Condition: HUD-NPMA-99-A is not in the file as required for all new construction
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:465** (1 rules)
- Condition: HUD-NPMA-99-B missing in new construction treated w/ termiticide, bait, field wood trtmt or barrier
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:466** (1 rules)
- Condition: ICC, RCI or CI not available & 2 inspections by a reg architect/structural engineer not in the file
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:467** (1 rules)
- Condition: Missing state/local certs of reg architect/engineer used due to lack of ICC certified RCI or CI
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:468** (1 rules)
- Condition: New construction inspections not by ICC, RCI or CI or registered architect/structural engineer
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:470** (1 rules)
- Condition: Termiticide soil treatment applied only around the foundation perimeter post construction
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:472** (1 rules)
- Condition: A licensed general contractor builder not hired to construct the dwelling for building on own land
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:473** (1 rules)
- Condition: Exist less than 1 year w/out bldg permit & CO or final inspection by local authority, ICC RCI or CI
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '1 year'

**product-specific-check:474** (1 rules)
- Condition: New construction- inspections/warranties as applicable per construction/property type not in file
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:476** (1 rules)
- Condition: Proposed construction-missing bldg permit & CO or footing, framing & final inspections by RCI or CI
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:477** (1 rules)
- Condition: Under construction-missing copies of the building permit and CO or final inspection by a RCI or CI
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:478** (1 rules)
- Condition: Income producing activity exceeds minimal &/or subject does not appear as predominantly residential
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:479** (1 rules)
- Condition: No, total closing costs including lender fees exceed 3% of the total loan amount
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '3%'

**product-specific-check:481** (1 rules)
- Condition: Seller or other interested party contributions exceed 6% of the loan amount
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '6%'

**product-specific-check:482** (1 rules)
- Condition: The transaction did not meet the eligibility requirements for loan discount points
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:486** (1 rules)
- Condition: Sales contract & all addenda not in the file, is incorrect or not signed by all parties
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:488** (1 rules)
- Condition: A net tangible benefit was not provided as applicable in a Streamlined-assist Section 502 refinance
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:489** (1 rules)
- Condition: All eligibility req's not met to qualify as a Section 502 refinance of a direct and guaranteed loan
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:490** (1 rules)
- Condition: Borr's from original loan, not deceased, was removed in a Section 502 Streamlined-assist refinance
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:492** (1 rules)
- Condition: Existing USDA loan being refinanced has a 30 days or more delinquency within previous 180-day period
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '30 days'

**product-specific-check:495** (1 rules)
- Condition: Refi ratios over 29/41, approved high repayment ratio exception not in file
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '29/41'

**product-specific-check:497** (1 rules)
- Condition: Streamlined-assist refi max income limit was exceeded due to not calculating annual income
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:498** (1 rules)
- Condition: FNMA doesn't have 1st claim to insurance settlements & condemnation proceeds in a shared equity loan
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:500** (1 rules)
- Condition: Private transfer fee doesn't qualify as a excepted transfer fee covenant under 12 C.F.R. § 1228.1(2)
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:501** (1 rules)
- Condition: The borrower does not meet the specific eligibility criteria set up by the shared equity program
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:502** (1 rules)
- Condition: The file did not evidence the required counseling for a shared equity loan
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:503** (1 rules)
- Condition: The property, occupancy, or loan type is ineligible for a shared equity loan
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:504** (1 rules)
- Condition: The shared equity community land trust did not meet the required legal documentation requirements
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:505** (1 rules)
- Condition: The shared equity community land trust is missing Form 2100 signed by the borrower
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:506** (1 rules)
- Condition: The shared equity income & price restrictions did not meet required legal documentation req's
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:507** (1 rules)
- Condition: The shared equity provider did not meet eligible provider requirements
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:508** (1 rules)
- Condition: Down payment requirements were not met for the subject single close construction perm purchase
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:509** (1 rules)
- Condition: Interim funds not used to buy lot/finance construction in single close construction perm purchase
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:510** (1 rules)
- Condition: Lot not owned by borr at 1st advance of interim financing in single close construction perm purchase
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:512** (1 rules)
- Condition: Single-close construction perm LTV, CLTV, HCLTV not calculated correctly as per property/loan type
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:513** (1 rules)
- Condition: Single-close construction perm credit docs older than 4 mos at conversion - permanent financing
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '4 months'

**product-specific-check:514** (1 rules)
- Condition: Single-close construction perm not UW based on permanent financing terms or was modified & not re-UW
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:515** (1 rules)
- Condition: Single-closing construction perm had a single period over 12 mos &/or total period exceeding 18 mos
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '12 months'

**product-specific-check:516** (1 rules)
- Condition: Single-closing construction perm loan term exceeded 30 years after conversion to permanent financing
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '30 years'

**product-specific-check:517** (1 rules)
- Condition: The terms of the single-closing construction-to-permanent modified were ineligible for modification
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:518** (1 rules)
- Condition: The terms of the single-closing construction-to-permanent were modified after the time of conversion
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:519** (1 rules)
- Condition: Solar & wind technologies policy used to increase base loan amt w/out meeting all eligibility req's
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:521** (1 rules)
- Condition: Weatherization product eligibility requirements not met for eligible energy related improvements
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:525** (1 rules)
- Condition: All renovation funds &/or contingency reserve acct requirements not met in a CHOICERenovation loan
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:527** (1 rules)
- Condition: CHOICEReno loan borrower is the general contractor & a plan detailing the work items not submitted
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:530** (1 rules)
- Condition: CHOICERenovation borr is the general contractor & loan proceeds reimbursed the borrower for labor
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:531** (1 rules)
- Condition: CHOICERenovation-Change order not agreed to by all parties &/or all applicable docs not in file
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:532** (1 rules)
- Condition: In a CHOICEReno, no evidence the home improvement store doing the renovation is financially able
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:533** (1 rules)
- Condition: The borrower is the general contractor in a CHOICERenovation loan and is not licensed/qualified
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:534** (1 rules)
- Condition: Unused CHOICERenovation funds not applied to UPB, addt'l reno, or disbursed to borr as applicable
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:536** (1 rules)
- Condition: All renovations not completed within 180 days of Note date in a CHOICEReno eXPress CHOICERenovation
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '180 days'

**product-specific-check:538** (1 rules)
- Condition: CHOICERenovation post-closing renovations were not completed within 450 days of the Note date
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '450 days'

**product-specific-check:539** (1 rules)
- Condition: CHOICERenovation-prior written approval not obtained if renovations not completed prior to closing
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:540** (1 rules)
- Condition: Reno extension not sent to Loan Status Hub w/ delay reason & Loan Status Hub granted ext not in file
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:541** (1 rules)
- Condition: The property type is ineligible for CHOICERenovation
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:543** (1 rules)
- Condition: CHOICEReno eXPress max financed renovation costs were exceeded for loan type && Duty to Serve area
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:546** (1 rules)
- Condition: CHOICERenovation proceeds PIF short-term financing for reno & validation of the cost not in the file
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:547** (1 rules)
- Condition: GreenCHOICE fee credit applied for renovations not related to energy/water efficiency
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:548** (1 rules)
- Condition: Loan proceeds paid off short-term financing used for renovation in a CHOICEReno eXPress loan
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:549** (1 rules)
- Condition: Over 50% of cost of materials advanced & borrower not acting as own contractor in CHOICERenovation
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '50%'

**product-specific-check:550** (1 rules)
- Condition: The CHOICERenovation proceeds were used for an ineligible purpose
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:551** (1 rules)
- Condition: The total cost of financed renovations exceeded the applicable limit for a CHOICERenovation
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:553** (1 rules)
- Condition: CHOICEReno In Progress/CHOICEReno eXPress missing lease &/or temporary rent not in DTI if applicable
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:554** (1 rules)
- Condition: CHOICERenovation mtg purpose is Construction or Construction-Perm in lieu of a purchase or refinance
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:555** (1 rules)
- Condition: Outstanding reno liens after completion of renovations not subordinate to subject CHOICERenovation
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:556** (1 rules)
- Condition: The CHOICERenovation proceeds were used for an inelligible purpose
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:558** (1 rules)
- Condition: Borrower eligibility & property improvements resale restrictions not met for a Community Land Trust
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:559** (1 rules)
- Condition: Community Land Trust 2 unit without borrower landlord education or 1 yr prior landlord experience
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '1-year'

**product-specific-check:560** (1 rules)
- Condition: Community Land Trust mtg is not secured by a 1 or 2 unit primary that is not a manufactured home
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:562** (1 rules)
- Condition: The Community Land Trust 2 unit property missing applicable landlord education certificate
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:563** (1 rules)
- Condition: The completed, executed, recorded Community Land Trust Ground Lease is not in the loan file
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:564** (1 rules)
- Condition: The loan purpose did not meet Community Land Trust mortgage eligibility requirements
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:565** (1 rules)
- Condition: The loan type did not meet Community Land Trust mortgage eligibility requirements
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:566** (1 rules)
- Condition: Construction Conversion & Renovation LTV not calculated correctly
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:568** (1 rules)
- Condition: Land ownership & disbursement req's not met for Construction Conv or Reno
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:569** (1 rules)
- Condition: No classification as construction conv or renovation mtg &/or no verification of completion costs
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:571** (1 rules)
- Condition: The subject was not an existing 1-4 unit site built home for this Renovation Mortgage
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:572** (1 rules)
- Condition: Tolerances were exceeded without resubmission on a Construction Conversion/Renovation
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:573** (1 rules)
- Condition: GreenCHOICE NCO energy improvements debt not PIF, balance re-amortized w/out Note & new pymt in file
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:575** (1 rules)
- Condition: GreenCHOICE energy report alt is missing invoices/receipts or other allowable alt documentation
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:576** (1 rules)
- Condition: GreenCHOICE no cashout financed energy improvements partially paid off, remaining debt not in DTI
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:577** (1 rules)
- Condition: GreenCHOICE no energy report missing, ineligible source, incomplete &/or not w/in 24 mos of closing
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '24 months'

**product-specific-check:579** (1 rules)
- Condition: GreenCHOICE proceeds for efficiency improvements not deposited into a completion escrow account
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:580** (1 rules)
- Condition: GreenCHOICE proceeds used to finance energy efficient improvements over 15% of as completed value
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '15%'

**product-specific-check:581** (1 rules)
- Condition: GreenCHOICE value used in a purchase not lesser of the as completed value & total acquisition cost
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:582** (1 rules)
- Condition: The as completed value was not used in a GreenCHOICE no cash-out refinance
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:584** (1 rules)
- Condition: 2 months reserves not documented for a 2-4 unit Home Possible mortgage
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '2 months'

**product-specific-check:585** (1 rules)
- Condition: Borr contribution req't not met as per property type & LTV, TLTV or HTLTV for Home Possible purchase
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:586** (1 rules)
- Condition: Home Possible 3% borr contribution not met & LTV, TLTV or HTLTV over 95% Home Possible 2-4 purchase
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '3%'

**product-specific-check:587** (1 rules)
- Condition: Home Possible borr did not have 3% own funds & a gift from seller who is the orig lender was rec'd
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '3%'

**product-specific-check:591** (1 rules)
- Condition: The Home Possible max LTV limits were exceeded as per applicable property type and loan purpose
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:592** (1 rules)
- Condition: The TLTV exceeded 105% in a Home Possible that included an Affordable Second
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '105%'

**product-specific-check:594** (1 rules)
- Condition: 2,500 VLIP credit given & borr income converted to an annual basis exceeds 50% of area median income
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '50%'

**product-specific-check:595** (1 rules)
- Condition: Home Possible 1 unit primary rental, the renter is a spouse/partner &/or has ownership interest
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:599** (1 rules)
- Condition: Confirmation borr's will occupy as required for Home Possible not in file
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:602** (1 rules)
- Condition: Home Possible Mtg w/temp subsidy buydown plan has 2nd loan not a fixed rate
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:603** (1 rules)
- Condition: Income used for this Home Possible loan exceeded 80% of area median income
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '80%'

**product-specific-check:604** (1 rules)
- Condition: The loan is not an eligible conventional product for the Home Possible program
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:605** (1 rules)
- Condition: The mortgage was ineligible under the Home Possible area median income limits
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:607** (1 rules)
- Condition: Evidence of landlord education &/or a cert of completion not in file for 2-4 Home Possible purchase
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:608** (1 rules)
- Condition: No evidence of homeownership education in a Home Possible using only noncredit payment references
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:609** (1 rules)
- Condition: No homeownership education in a Home Possible purchase where all occupying are first time homebuyers
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:612** (1 rules)
- Condition: The temporary $2,500 VLIP credit was not provided directly to the borrower through the transaction
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '$2,500'

**product-specific-check:613** (1 rules)
- Condition: The temporary VLIP $2,500 credit was applied to a loan that was not manually UW or an LPA Accept
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '$2,500'

**product-specific-check:615** (1 rules)
- Condition: Home Possible w/ RHS Leveraged Second Borr Cert of Eligibility, Form RD 1944.59 not in the file
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:616** (1 rules)
- Condition: Home Possible w/RHS Leveraged Second is not a 1st lien purchase of 1 unit primary w/ 30 year rate
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '30 year'

**product-specific-check:617** (1 rules)
- Condition: Home Possible with RHS Leveraged Second did not meet LTV limits and/or all RHS requirements not met
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:619** (1 rules)
- Condition: The initial fixed-rate period was under 5 years in a Home-Possible ARM with an Affordable Second
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '5 years'

**product-specific-check:620** (1 rules)
- Condition: All  HomeOne property and borrower eligibility requirements were not met
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:621** (1 rules)
- Condition: Confirmation that all borrowers will occupy as primary residence not in the file for a HomeOne mtg
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:622** (1 rules)
- Condition: No evidence at least 1 borr took homeownership education where all borr's are first-time homebuyers
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:623** (1 rules)
- Condition: The maximum HomeOne LTV limit was exceeded as per transaction type
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:624** (1 rules)
- Condition: The subject HomeOne was not underwritten by LPA or did not receive a risk class of Accept
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:626** (1 rules)
- Condition: Refi Possible condo or co-op appears to be a condotel or insurance requirements were not met
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:628** (1 rules)
- Condition: <1/1/22 Qualifying income converted to an annual basis exceeds 80% of the AMI for subject property
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '80%'

**product-specific-check:629** (1 rules)
- Condition: Borr on Note being refinanced is not on Refi Possible w/out req's met & at least 1 borr not retained
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:630** (1 rules)
- Condition: Borr(s) on the Refi Possible Note are not the same as is on the Note being refinanced
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:634** (1 rules)
- Condition: Refi Possible proceeds not used only to PIF the first mtg, closing costs &/or cash back over $250
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '$250'

**product-specific-check:638** (1 rules)
- Condition: Missing last 1 month receipt of alimony, child support &/or maintenance pymts in a Refi Possible
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '1 month'

**product-specific-check:640** (1 rules)
- Condition: No YTD military leave and earnings statement in a Refi Possible using military income
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:643** (1 rules)
- Condition: Refi Possible using alimony, child support &/or maintenance missing legal agmnt w/ amount & duration
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:645** (1 rules)
- Condition: Existing 2nd did not meet secondary financing req's &/or not subordinated to the Refi Possible mtg
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:646** (1 rules)
- Condition: Mtg refinanced to a Refi Possible has recourse/indemnification without meeting eligibility req's
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:647** (1 rules)
- Condition: Refi Possible is super-conforming, temporary interest buydown or TX Equity Section 50(a)(6)
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:648** (1 rules)
- Condition: The Refi Possible is not a fixed-rate
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:649** (1 rules)
- Condition: The Refi Possible is not secured by a one-unit primary residence
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:650** (1 rules)
- Condition: The new jr lien UPB is more than the UPB of jr lien being refinanced w/ the 1st to the Refi Possible
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:652** (1 rules)
- Condition: <1/1/22 Refi Possible mtg being refinanced not seasoned between 12 mos & 120 mos prior to Note
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '12 months'

**product-specific-check:653** (1 rules)
- Condition: Ineligible Refi Possible, refinanced mtg is Relief/Enhanced, Refi Possible, subject to repurch/indem
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:654** (1 rules)
- Condition: Mtg being refinanced to Refi Possible has 30 delinquent more than once &/or over 60 in last year
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '30 days'

**product-specific-check:655** (1 rules)
- Condition: Mtg being refinanced to a Refi Possible has been 30 days delinquent in the most recent six months
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '30 days'

**product-specific-check:656** (1 rules)
- Condition: Refi Possible mtg being refinanced is not a 1st lien conventional owned/securitized by Freddie Mac
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:658** (1 rules)
- Condition: No credit assessment in Refi Possible manual UW & credit reestablish req not met after derog credit
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:660** (1 rules)
- Condition: Refi Possible interest rate reduction is not at least 50 bps & no reduction to the mtg payment
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:661** (1 rules)
- Condition: Refi Possible maximum LTV, TLTV & HTLTV requirements were not met as per property/transaction type
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:662** (1 rules)
- Condition: Refi Possible significant derogatory event not documented the cause was beyond the borr’s control
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:663** (1 rules)
- Condition: The Refi Possible has a non-occupying borrower and the total DTI ratio exceeded 65%
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '65%'

**product-specific-check:668** (1 rules)
- Condition: Loan amt did not comply with min & max loan amts for Super Conforming mtg
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:670** (1 rules)
- Condition: Super Conforming was manually UW without a caution, invalid, ineligible or incomplete status by LPA
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:672** (1 rules)
- Condition: Remote ink-signed notarization (RIN) was utilized in a Texas Equity Section 50(a)(6) mortgage
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:674** (1 rules)
- Condition: Remote online notarization, (RON), was used in a Texas Equity Section 50(a)(6) Mortgage
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:676** (1 rules)
- Condition: The subject is an eMortgage which is not eligible for a Texas Section 50(a)(6)
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:678** (1 rules)
- Condition: Borr's not on title 6mos prior & did not meet requirements for cashout refi
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:679** (1 rules)
- Condition: Cash-out cooperative unit without at least 1 borr having held cooperative shares for at least 6 mos
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:680** (1 rules)
- Condition: Cash-out leasehold and at least 1 borrower not a lessee on ground/lease agmnt for at least 6 mos
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:681** (1 rules)
- Condition: Cash-out proceeds paid a 1st lien mtg seasoned less than 12 mos & didn't meet standards to not apply
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '12 months'

**product-specific-check:682** (1 rules)
- Condition: Delayed financing cash-out refi & borrowed funds to buy the subject not paid down/PIF as applicable
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:683** (1 rules)
- Condition: LLC/LP holds title & borr not majority owner & not put in borr's name prior to Note in a CO refi
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '6 months'

**product-specific-check:684** (1 rules)
- Condition: Special purpose cash-out doesn't meet limitations on the use of proceeds & ownership of the property
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:685** (1 rules)
- Condition: Title in LLC/LP not borr & did not meet the CO refi 6 mos on title req to qualify for an exception
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '6 months'

**product-specific-check:687** (1 rules)
- Condition: Cash-out exceeded 1% or $2,000 and/or any excess not applied as a principal curtailment
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '1%'

**product-specific-check:688** (1 rules)
- Condition: NCO proceeds over the greater of 1% or $2,000 were used to pay past due &/or delinquent taxes
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '1%'

**product-specific-check:690** (1 rules)
- Condition: Note date of the refi being PIF not at least 30 days prior to the Note date of the no cash-out refi
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '30 days'

**product-specific-check:691** (1 rules)
- Condition: Proceeds from the no cash-out transaction were used to pay off or pay down an unallowable debt/lien
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:693** (1 rules)
- Condition: Cash back or principal curtailment in a purchase transaction w/out meeting conditions to allow it
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:695** (1 rules)
- Condition: Prorated property tax credit not used to offset charge to establish the escrow account as applicable
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:696** (1 rules)
- Condition: Purchase VOD current balance exceeds avg balance over 50% qualifying income w/out supporting doc
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '50%'

**product-specific-check:697** (1 rules)
- Condition: Purchase cashback results in min contribution not met & principal curtailment not applied for excess
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:698** (1 rules)
- Condition: The UW did not ensure the original loan amount does not exceed the maximum loan limit for the area
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:699** (1 rules)
- Condition: At least 1 borr not on new loan, or title past year or legally awarded the subject being refinanced
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: -

**product-specific-check:700** (1 rules)
- Condition: Borr's not on loan being refinanced & no evidence they made pymts on the subject for last 12 mos
- What's needed: a document/data type not in extract_loan.py's DOC_TYPES at all
- Machine-checkable: explicit numeric/date threshold detected: '12 months'

### 2. Convertible via Extraction Deepening (861 groups)

These rules need fields that exist in the documents but aren't yet extracted.

**asset-verification:1** (1 rules)
- Condition: AUS UW-VOD or last 1 month bank statements do not verify funds on deposit
- What's needed: VOD doc type (not in any synthetic loan) or a bank_statement balance-vs-claimed-funds derivation
- Machine-checkable: -

**asset-verification:4** (1 rules)
- Condition: Current home sale proceeds not documented to verify sale, payoffs and sufficient net proceeds
- What's needed: prior-home-sale settlement statement + net-proceeds field (deepen closing_disclosure)
- Machine-checkable: -

**asset-verification:5** (1 rules)
- Condition: The amt of equity the applicant has accumulated for use of sale proceeds not documented
- What's needed: sale-proceeds equity-accumulation field, same doc gap as G004
- Machine-checkable: -

**asset-verification:9** (1 rules)
- Condition: A down pymt from borr's own resources not made for the difference in sales price & reasonable value
- What's needed: VA NOV reasonable-value + sales-price + down-payment fields (deepen va_nov/1003)
- Machine-checkable: -

**asset-verification:10** (1 rules)
- Condition: AUS Refer-sales price exceeds NOV without funds for the difference plus closing costs being verified
- What's needed: same fields as G009 (VA NOV reasonable value vs sales price)
- Machine-checkable: -

**asset-verification:16** (1 rules)
- Condition: Sales price exceeds VA reasonable value and documentation that HAP funds are a grant not provided
- What's needed: same VA-reasonable-value fields as G009/G010, plus a HAP-grant field
- Machine-checkable: -

**asset-verification:22** (1 rules)
- Condition: Terms of Employer Assisted Homeownership (EAH) Benefit to borr not in file
- What's needed: Employer Assisted Homeownership benefit agreement doc type (not in corpus)
- Machine-checkable: EAH benefit terms doc presence

**asset-verification:38** (1 rules)
- Condition: Borr was own realtor & the earned commission not on settlement stmt as a credit towards the mtg loan
- What's needed: realtor-commission-as-credit field on closing_disclosure (deepen extraction)
- Machine-checkable: -

**asset-verification:40** (1 rules)
- Condition: Earnest money deposit not entered correctly in DU based on if EMD cleared the borr's bank account
- What's needed: EMD amount field (1003/purchase contract) cross-referenced against bank_txns debit — same as G081
- Machine-checkable: -

**asset-verification:51** (1 rules)
- Condition: Business assets used as assets to close and the borrower is not listed as an owner of the account
- What's needed: account-ownership field on bank_statement (not currently captured)
- Machine-checkable: -

**asset-verification:57** (1 rules)
- Condition: Borr assets insufficient to meet MRI, closing costs/prepaids without seller real estate tax credit
- What's needed: MRI + closing-costs/prepaids + seller-tax-credit fields (deepen 1003/closing_disclosure)
- Machine-checkable: -

**asset-verification:61** (1 rules)
- Condition: The funds derived from the premium pricing were not used to reduce the principal balance
- What's needed: premium-pricing-credit-application field (deepen closing_disclosure)
- Machine-checkable: -

**asset-verification:66** (1 rules)
- Condition: The existence of & amounts in the borrower’s checking and savings accounts not verified & documented
- What's needed: aggregate 'current balance' fact derived from bank_txns (deepen extraction)
- Machine-checkable: -

**asset-verification:69** (1 rules)
- Condition: It was not ensured assets entered into GUS as reserves were available to the applicants post-closing
- What's needed: reserves field on gus_findings (deepen extraction — doc exists for loan 05, field does not)
- Machine-checkable: -

**asset-verification:75** (1 rules)
- Condition: Common customary costs paid by the borr outside of closing on credit card exceeds 2% of the loan amt
- What's needed: credit-card-paid-costs field + loan-amount comparison (2% threshold; deepen closing_disclosure/1003)
- Machine-checkable: -

**asset-verification:82** (1 rules)
- Condition: No, verification of earnest money on sales contract not provided
- What's needed: purchase/sales contract document (not present as a doc type in any synthetic loan)
- Machine-checkable: -

**asset-verification:84** (1 rules)
- Condition: No evidence earnest money deposit cleared the borr's account or written statement verifying receipt
- What's needed: EMD amount field cross-referenced against bank_txns debit (deepen extraction)
- Machine-checkable: -

**asset-verification:86** (1 rules)
- Condition: The EMD exceeded 1% or is deemed excessive without the source being documented and verified
- What's needed: EMD amount + sales price fields (1% threshold; deepen 1003/contract)
- Machine-checkable: -

**asset-verification:96** (1 rules)
- Condition: All req'd info not on asset internet printout downloaded by borrower or financial institution rep
- What's needed: asset-internet-printout document (distinct alt-doc type, not in corpus)
- Machine-checkable: -

**asset-verification:99** (1 rules)
- Condition: Minimum contribution not met or not from borrower's own personal funds
- What's needed: minimum-contribution + fund-source fields (deepen 1003/closing_disclosure)
- Machine-checkable: -

**asset-verification:100** (1 rules)
- Condition: New acct within 90 days - documentation verifying funds were from an acceptable source not provided
- What's needed: account-open-date field (deepen bank_statement)
- Machine-checkable: -

**asset-verification:107** (1 rules)
- Condition: A gift of equity was used as financial reserves
- What's needed: gift-of-equity/reserves designation field (deepen gift_letter)
- Machine-checkable: -

**asset-verification:108** (1 rules)
- Condition: Donor ability &/or the gift transfer to the borr’s account or to the closing agent not documented
- What's needed: donor-ability + transfer-method fields (deepen gift_letter)
- Machine-checkable: -

**asset-verification:110** (1 rules)
- Condition: Gift funds/gift of equity were received from an unacceptable donor
- What's needed: donor-relationship field (deepen gift_letter)
- Machine-checkable: -

**asset-verification:111** (1 rules)
- Condition: Gift of equity not documented with a signed gift letter &/or not included on the closing statement
- What's needed: equity amount cross-check against closing_disclosure (deepen extraction)
- Machine-checkable: -

**asset-verification:119** (1 rules)
- Condition: Gift funds provided were not from an acceptable donor
- What's needed: donor-relationship field (deepen gift_letter)
- Machine-checkable: -

**asset-verification:122** (1 rules)
- Condition: Graduation gift for 1st time homebuyer not deposited to borrower's acct w/in 90 days of graduation
- What's needed: graduation-date evidence + gift_letter/bank_statement date fields
- Machine-checkable: -

**asset-verification:125** (1 rules)
- Condition: The gift letter did not state the actual or the maximum amount of the gift funds or gift of equity
- What's needed: gift-amount-stated field (deepen gift_letter FIELD_SPECS)
- Machine-checkable: -

**asset-verification:130** (1 rules)
- Condition: Borrower received cash back at closing due to a gift of equity, sweat equity, or rent credits
- What's needed: cross-reference of cash_out_to_borrower_1003 (already extracted) against gift/sweat-equity/rent-credit facts (partial fixture gap for the latter)
- Machine-checkable: -

**asset-verification:131** (1 rules)
- Condition: Check/elec Xfer to the closing agent or the Closing Disclosure did not document the gift at closing
- What's needed: transfer-method field, same gift-transfer family as G108/G127
- Machine-checkable: -

**asset-verification:132** (1 rules)
- Condition: Gift of equity, sweat equity, or rent credits were not applied as a reduction to the purchase price
- What's needed: sale-price-reduction field cross-check (deepen closing_disclosure)
- Machine-checkable: -

**asset-verification:133** (1 rules)
- Condition: No, gift funds did not come from an acceptable source
- What's needed: donor-relationship field (deepen gift_letter)
- Machine-checkable: -

**asset-verification:138** (1 rules)
- Condition: Gift at closing, missing donor payment to closing agent with EFT, or bank certified/cashiers check
- What's needed: payment-method field (deepen gift_letter/closing_disclosure)
- Machine-checkable: -

**asset-verification:141** (1 rules)
- Condition: The donor of the gift of equity was not a family member
- What's needed: donor-relationship field (deepen gift_letter)
- Machine-checkable: -

**asset-verification:142** (1 rules)
- Condition: The gift funds were not provided by an acceptable source
- What's needed: donor-relationship field (deepen gift_letter)
- Machine-checkable: -

**asset-verification:148** (1 rules)
- Condition: Amount/source of interested party contribution not documented & shown on the Closing Disclosure
- What's needed: IPC amount/source field (deepen closing_disclosure)
- Machine-checkable: -

**asset-verification:149** (1 rules)
- Condition: Int party financing concessions used for purposes other than closing costs or up to 12 mos HOA dues
- What's needed: IPC-use classification field (deepen closing_disclosure)
- Machine-checkable: -

**asset-verification:150** (1 rules)
- Condition: Interested party financing concessions exceeded limits
- What's needed: IPC amount + applicable-limit fields (deepen closing_disclosure)
- Machine-checkable: -

**asset-verification:152** (1 rules)
- Condition: Sale price not reduced for contribution/reimbursement &/or LTV not calc using lower price/value
- What's needed: sale-price + IPC + LTV recalculation fields (deepen closing_disclosure/1003)
- Machine-checkable: -

**asset-verification:154** (1 rules)
- Condition: Financing concessions over limit are sales concessions not deducted from sales price/LTV not recalc
- What's needed: same IPC-limit fields as G150
- Machine-checkable: -

**asset-verification:155** (1 rules)
- Condition: IPC's were used for down payment, reserves req's, or to meet minimum borrower contribution
- What's needed: same IPC-use fields as G149
- Machine-checkable: -

**asset-verification:156** (1 rules)
- Condition: IPCs of non-realty items paid prior to, at or after closing were not considered as sales concessions
- What's needed: same IPC-use fields as G149
- Machine-checkable: -

**asset-verification:160** (1 rules)
- Condition: Lender incentive paying off a portion of the loan being refinanced & subject is not a high LTV refi
- What's needed: lender-incentive + LTV/refi-type fields (deepen closing_disclosure)
- Machine-checkable: -

**asset-verification:162** (1 rules)
- Condition: Premium pricing credit applied to down pymt &/or exceeded the amt needed to offset the closing costs
- What's needed: premium-pricing-credit field (deepen closing_disclosure)
- Machine-checkable: -

**asset-verification:163** (1 rules)
- Condition: Sale price not reduced when the loan amount is based on seller contributions or inducements over 6%
- What's needed: same IPC-limit fields as G150 (6% threshold)
- Machine-checkable: -

**asset-verification:164** (1 rules)
- Condition: The loan includes an interested party funded payment abatement
- What's needed: IPC-abatement field (deepen closing_disclosure)
- Machine-checkable: -

**asset-verification:171** (1 rules)
- Condition: No evidence of liquidation for applicable accounts that are less than 20% of the amt needed to close
- What's needed: 'amount needed to close' + liquidation-evidence fields (20% threshold; deepen extraction)
- Machine-checkable: -

**asset-verification:176** (1 rules)
- Condition: MRI was provided by a source other than the borr that was not a permissible source that meets req's
- What's needed: MRI-source field + SME-defined permissible-source list
- Machine-checkable: -

**asset-verification:179** (1 rules)
- Condition: Reserves are insufficient based on the subject loan characteristics or as was required by DU
- What's needed: DU reserve-requirement field (AUS-family, not in corpus)
- Machine-checkable: -

**asset-verification:180** (1 rules)
- Condition: The financial assets provided for reserves were from an unacceptable source
- What's needed: reserve-source field
- Machine-checkable: -

**asset-verification:182** (1 rules)
- Condition: Evidence does not exist indicating the borrower is entitled to net proceeds
- What's needed: prior-sale entitlement field (deepen closing_disclosure)
- Machine-checkable: -

**asset-verification:183** (1 rules)
- Condition: Net sale proceeds considered & not verified with a fully executed Closing Disclosure or similar
- What's needed: net-proceeds cross-check field (deepen closing_disclosure)
- Machine-checkable: -

**asset-verification:211** (1 rules)
- Condition: Prorated real estate tax credit by the seller was included in determining enough funds for closing
- What's needed: tax-proration-credit field (deepen closing_disclosure)
- Machine-checkable: -

**asset-verification:215** (1 rules)
- Condition: A dollar for dollar reduction for the inducement to purchase was not applied to the sales price
- What's needed: inducement-to-purchase field (deepen closing_disclosure)
- Machine-checkable: -

**asset-verification:218** (1 rules)
- Condition: Subject commission for cash to close without verifying borr RE license/commission entitlement
- What's needed: RE agent license copy (not in corpus) — possible Bucket-C candidate
- Machine-checkable: -

**asset-verification:233** (1 rules)
- Condition: Rent credit for option to purchase market rent was not determined by the subject property appraisal
- What's needed: market-rent determination field (deepen appraisal, or a rent-schedule addendum)
- Machine-checkable: -

**asset-verification:234** (1 rules)
- Condition: Rent credit not calculated using the difference between market rent & actual rent paid by the borr
- What's needed: market-rent + actual-rent fields (deepen appraisal/lease)
- Machine-checkable: -

**asset-verification:235** (1 rules)
- Condition: Rent-back credit used as source of funds for closing costs, down pymt, or reserves when qualifying
- What's needed: rent-back-credit field (deepen closing_disclosure)
- Machine-checkable: -

**asset-verification:240** (1 rules)
- Condition: Borr has 1 to 6 financed properties, including the subject, & 2 mos reserves for each not verified
- What's needed: financed-property count + reserve-months fields (not modeled — no REO-schedule entity today)
- Machine-checkable: -

**asset-verification:243** (1 rules)
- Condition: Reserves are insufficient based on the subject loan characteristics or as was required by LPA
- What's needed: LPA reserve-requirement field (AUS-family, not in corpus)
- Machine-checkable: -

**asset-verification:246** (1 rules)
- Condition: One month's PITI reserves were not verified and documented for a 1-2 property in a manual UW
- What's needed: PITI + reserve-months fields (deepen extraction)
- Machine-checkable: -

**asset-verification:252** (1 rules)
- Condition: Over 60% of the value of the retirement accounts was considered &/or loans not deducted
- What's needed: retirement-account value + outstanding-loan fields (60% threshold)
- Machine-checkable: -

**asset-verification:255** (1 rules)
- Condition: Retirement liquidation not required; vested amt used without evidence borr can make withdrawals
- What's needed: retirement vesting/withdrawal-evidence field
- Machine-checkable: -

**asset-verification:256** (1 rules)
- Condition: VOD or 1 month statement not provided for streamlined accept documentation of retirement accounts
- What's needed: retirement-account VOD (doc-presence-style, doc type absent from corpus)
- Machine-checkable: -

**asset-verification:271** (1 rules)
- Condition: The type/terms of subordinate financing unacceptable
- What's needed: subordinate-financing terms field
- Machine-checkable: -

**asset-verification:289** (1 rules)
- Condition: The bank statements did not include all account identifying information
- What's needed: account-identifying-information field (deepen bank_statement FIELD_SPECS)
- Machine-checkable: -

**asset-verification:295** (1 rules)
- Condition: The gift funds were not provided by an acceptable source
- What's needed: donor-relationship field (deepen gift_letter)
- Machine-checkable: -

**asset-verification:296** (1 rules)
- Condition: Transfer of gift funds not documented with bank statements or as being received by the closing agent
- What's needed: transfer-method field, same gift-transfer family as G108/G127/G131
- Machine-checkable: -

**income-verification:1** (1 rules)
- Condition: Alimony/child support/maintenance missing legal docs &/or history and continuance req's not met
- What's needed: alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:2** (1 rules)
- Condition: The alimony, child support and/or maintenance income was not calculated correctly
- What's needed: alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:4** (1 rules)
- Condition: Applicant is active military without a Military Leave and Earnings Statement provided
- What's needed: military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:5** (1 rules)
- Condition: Borr is in Nat'l Guard or Reserves, no analysis of impact to income due to activation in the file
- What's needed: military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:6** (1 rules)
- Condition: Service member within 12 mos of release from active duty, employment intentions were not documented
- What's needed: military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:7** (1 rules)
- Condition: The military income was not calculated correctly
- What's needed: military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:8** (1 rules)
- Condition: The type, amount, history of receipt not documented for other military allowances
- What's needed: military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:9** (1 rules)
- Condition: Verification of the military quarters allowance was not provided
- What's needed: military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:11** (1 rules)
- Condition: 2nd job, part-time, bonus used w/out supporting documents &/or history & continuance req's not met
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:12** (1 rules)
- Condition: The file does not contain evidence of the seasonal income
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:13** (1 rules)
- Condition: The file does not contain satisfactory evidence of the unemployment income
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:14** (1 rules)
- Condition: The part-time, second job, seasonal and/or unemployment income was not calculated correctly
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:16** (1 rules)
- Condition: No VA award letter, bank stmt or similar to document monthly retirement, pension &/or disability
- What's needed: benefits/award letter (SSA, VA, pension, or disability payer) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:17** (1 rules)
- Condition: Retirement, royalty, deposit accts used without all req'd docs &/or did not meet history/cont req's
- What's needed: disability-benefits payer statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:18** (1 rules)
- Condition: The social security, retirement and/or disability income was not calculated correctly
- What's needed: disability-benefits payer statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:20** (1 rules)
- Condition: A copy of the govn't issued Mortgage Credit Certificate not in file where MCC's were used
- What's needed: Mortgage Credit Certificate (MCC) document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:21** (1 rules)
- Condition: Car Allowance- Net amount by which the allowance exceeds the actual expense was not documented
- What's needed: automobile-allowance employer letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:22** (1 rules)
- Condition: Documentation verifying tax exempt income will continue & remain untaxed was not provided
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:23** (1 rules)
- Condition: File does not contain satisfactory evidence of total gross qualifying foster care income
- What's needed: foster-care sponsoring-organization verification letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:24** (1 rules)
- Condition: Income from public assistance was considered without documenting at least a 3-year continuance
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:27** (1 rules)
- Condition: Royalty payments used and the file does not contain satisfactory evidence of the income
- What's needed: royalty contract/agreement + tax-return schedule — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:28** (1 rules)
- Condition: The other income  used to qualify was not calculated correctly
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:29** (1 rules)
- Condition: The trust income history of receipt and at least 3 years continuance was not documented
- What's needed: trust agreement/trustee statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:30** (1 rules)
- Condition: Comm. income does not satisfy VA's requirement of having continued for 2 yrs to be considered stable
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:31** (1 rules)
- Condition: Income from OT, part-time, 2nd job or bonuses not verified for past 2 yrs or unlikely to continue
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:32** (1 rules)
- Condition: The file did not document the YTD, basis for payments & pay frequency for commission income
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:33** (1 rules)
- Condition: The overtime, bonus and/or commission income was not calculated correctly
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:35** (1 rules)
- Condition: Multi-unit property rental income used without documenting prior landlord experience
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:36** (1 rules)
- Condition: Rental income considered without a copy of the lease or rental agreement in the file
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:37** (1 rules)
- Condition: Rental income used to qualify was not calculated correctly
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:38** (1 rules)
- Condition: Two yrs rental income not documented w/ copies of signed tax returns/schedules
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:40** (1 rules)
- Condition: All income from employment was not verified for each individual contractually obligated on the loan
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:41** (1 rules)
- Condition: Current employment less than 12 mos & continued employment is unreasonable & analysis not documented
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:42** (1 rules)
- Condition: The wage income was not calculated correctly
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:43** (1 rules)
- Condition: Vendor for 3rd party VOE was not Equifax/TWN or manual process not followed
- What's needed: a VOE-vendor-name field (e.g. Equifax/The Work Number) — not currently captured from any document
- Machine-checkable: -

**income-verification:46** (1 rules)
- Condition: SE income calc incorrectly &/or Form 91/Income Calc Report/FHLMC Calc Cert or similar was missing
- What's needed: income-calculation worksheet/tool output — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:47** (1 rules)
- Condition: 1099 income less than 2 yrs without a written analysis & documentation justifying stability
- What's needed: 1099 (or Form 4137 tip-income) tax form — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:48** (1 rules)
- Condition: 1099 income not averaged correctly using the documented history & expense reduction as applicable
- What's needed: 1099 (or Form 4137 tip-income) tax form — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:49** (1 rules)
- Condition: 1099 income not documented as likely to continue for at least the next 3 years
- What's needed: 1099 (or Form 4137 tip-income) tax form — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:50** (1 rules)
- Condition: 1099 income not documented with 2 years 1099's, YTD paystubs/equivalent & pgs 1 & 2 tax returns
- What's needed: 1099 (or Form 4137 tip-income) tax form — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:52** (1 rules)
- Condition: Schedule C 1099 expenses exceed 5% of gross receipts or sales after deducting non-cash expenses
- What's needed: Schedule C business tax-return page — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:53** (1 rules)
- Condition: Schedule C does not reflect a 12-month history of 1099 income and reported expenses
- What's needed: Schedule C business tax-return page — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:54** (1 rules)
- Condition: Schedule C gross receipts or sales do not equal to the total amount(s) reported on IRS Form 1099(s)
- What's needed: Schedule C business tax-return page — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:55** (1 rules)
- Condition: Schedule C used for 1099 income is reported an amount for the cost of goods sold
- What's needed: Schedule C business tax-return page — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:58** (1 rules)
- Condition: Three years tax returns were not obtained to evaluate the borrower's earnings trend of capital gains
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:59** (1 rules)
- Condition: Business tax returns for the most recent 2 yrs, including all schedules, or an alt not provided
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:61** (1 rules)
- Condition: Alimony/child supp/maintenance not supported w/ legal docs &/or 6 mos history & continuance not met
- What's needed: alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:62** (1 rules)
- Condition: Alimony/maintenance payments with more than 10 mos left was not deducted from gross monthly income
- What's needed: alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:63** (1 rules)
- Condition: Foster income-2 yr history from organization verifying total gross qualifying income not provided
- What's needed: alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:67** (4 rules)
- Condition: 4506-C not completed & signed prior to or at closing for each borrower whose income used to qualify
- What's needed: IRS Form 4506-C/8821 tax-transcript consent form — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:68** (1 rules)
- Condition: A completed & signed 4506-C/8821 not in the file for each adult household member, as applicable
- What's needed: IRS Form 4506-C/8821 tax-transcript consent form — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:69** (5 rules)
- Condition: Non Code 10 IRS rejection & evidence of attempts to get a corrected & signed 4506-C not in the file
- What's needed: IRS Form 4506-C/8821 tax-transcript consent form — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:71** (2 rules)
- Condition: Steps not taken to confirm borr identity & escalated as applicable for IRS 4506-C Code 10 rejection
- What's needed: IRS Form 4506-C/8821 tax-transcript consent form — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:73** (1 rules)
- Condition: The signed IRS Form 4506-C or an alternate acceptable form was not retained in the file
- What's needed: IRS Form 4506-C/8821 tax-transcript consent form — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:75** (1 rules)
- Condition: Taxpayer’s consent form did not include all entities that information can be shared with
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:76** (1 rules)
- Condition: Taxpayer’s consent was required and the consent form is not in the file
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:77** (1 rules)
- Condition: 2nd job of 1 year but less than 2 years did not meet stability requirements
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:80** (1 rules)
- Condition: Seasonal unemployment history & continuance req's not met &/or no evidence of receipt for last 2 yrs
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:81** (1 rules)
- Condition: Borr not qualified on lesser of the future long-term or current short-term disability payments
- What's needed: disability-benefits payer statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:82** (1 rules)
- Condition: Future long-term disability used & no current short-term converting to long-term &/or not documented
- What's needed: disability-benefits payer statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:83** (1 rules)
- Condition: Future long-term disability used and the source, type, amount, and payment frequency not documented
- What's needed: disability-benefits payer statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:87** (1 rules)
- Condition: Retirement assets as income-Documentation verifying source, amt, frequency & receipt not provided
- What's needed: retirement-account statement (401(k)/IRA/Keogh/pension) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:89** (1 rules)
- Condition: SSA verification letter or evidence of receipt of benefit not in the file for Social Security income
- What's needed: 1099 (or Form 4137 tip-income) tax form — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:90** (1 rules)
- Condition: Adjusted annual income included a child care expense deduction without documenting eligibility
- What's needed: RHS household-income deduction eligibility documentation — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:91** (1 rules)
- Condition: Adjusted annual income included a dependent deduction without documenting the deduction is eligible
- What's needed: RHS household-income deduction eligibility documentation — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:92** (1 rules)
- Condition: Adjusted annual income included an elderly household deduction without documenting eligibility
- What's needed: RHS household-income deduction eligibility documentation — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:93** (1 rules)
- Condition: Adjusted annual income included elderly medical expenses deduction without documenting eligibility
- What's needed: RHS household-income deduction eligibility documentation — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:94** (1 rules)
- Condition: Borrower is ineligible for household member with disabilities deduction
- What's needed: RHS household-income deduction eligibility documentation — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:95** (1 rules)
- Condition: Income from trust funds for household annual income calculation purposes not documented & verified
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:96** (1 rules)
- Condition: Lump sum receipts, such as inheritance, capital gains or lottery wins not documented & verified
- What's needed: capital-gains tax-return schedule (Schedule D) history — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:98** (1 rules)
- Condition: Verification of real property equity/capital invest not documented for inclusion in annual income
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:99** (1 rules)
- Condition: A copy of the mortgage credit certificate was not provided
- What's needed: Mortgage Credit Certificate (MCC) document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:100** (1 rules)
- Condition: Appropriate docs for other non-employed income w/in last 12 mos not in file
- What's needed: 1099 (or Form 4137 tip-income) tax form — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:102** (1 rules)
- Condition: Employed by a family member/interested party & the most recent years tax returns were not provided
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:103** (1 rules)
- Condition: Entire amt non-taxable income used without addtl docs &/or grossed up income calculated incorrectly
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:104** (1 rules)
- Condition: Family/int party employed & tax return/transcript don't support current income & prior year not used
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:105** (1 rules)
- Condition: Foreign income used without obtaining US federal income tax returns
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:106** (1 rules)
- Condition: Foreign income was used without being translated to U.S. dollars
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:107** (1 rules)
- Condition: Household assets to annual income calculated incorrectly for cash value greater or less than $5,000
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:108** (1 rules)
- Condition: In a loan relying on capital gains, file does not contain signed tax returns for the past two years
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:109** (1 rules)
- Condition: Income amt of assets sold for less than value w/in the last 2 yrs incorrect
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:110** (1 rules)
- Condition: Interest/dividend-Tax rtrns verifying 2yr receipt & sufficient assets to support income not provided
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:111** (1 rules)
- Condition: K-1 income shows < 25% ownership and documentation demonstrating the income may be used not provided
- What's needed: K-1 / Form 1065 / 1120S business tax-return schedule — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:112** (1 rules)
- Condition: LTV over 70% or 80% if owner is at least 62 years old where employment related assets used as income
- What's needed: employment-related-asset / lump-sum-distribution qualifying-income documentation — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:113** (1 rules)
- Condition: Monthly amt of employment related assets as income calculated incorrectly &/or req's for use not met
- What's needed: employment-related-asset / lump-sum-distribution qualifying-income documentation — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:114** (1 rules)
- Condition: Mortgage credit certificate used and written documentation verifying the payments was not provided
- What's needed: Mortgage Credit Certificate (MCC) document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:115** (1 rules)
- Condition: Non-occupant borrower income used in manual UW with an unacceptable LTV and is a NOO residence
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:116** (1 rules)
- Condition: Non-taxable income was not grossed up 25% for repayment income as needed
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:118** (1 rules)
- Condition: Notes Receivable-Existence of the note & consistent pymts for last 12 mos not verified & documented
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:119** (1 rules)
- Condition: Public assistance-Documentation verifying amount, frequency and duration was not provided
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:120** (1 rules)
- Condition: Royalty-Tax returns, contract/alt documentation and 12 mo receipt with 3 yr continuance not provided
- What's needed: Schedule E rental-income tax-return page — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:121** (1 rules)
- Condition: Section 8 used to reduce PITI without documenting the benefit is paid directly to the servicer
- What's needed: Section 8 / Housing Choice Voucher award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:123** (1 rules)
- Condition: Tax returns for the past 2 yrs & evidence of sufficient assets to support capital gains not provided
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:124** (1 rules)
- Condition: Tax-exempt income was used without meeting all documentation/requirements
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:125** (1 rules)
- Condition: Temporary leave income used and the income does not meet Freddie Mac's requirements
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:126** (1 rules)
- Condition: The file did not contain 2 years tax returns including foreign income
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:127** (1 rules)
- Condition: The income has a sharp increase/decrease of 20% or more that was not supported and logical
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:128** (1 rules)
- Condition: Unreimbursed employee/business expenses deducted from annual income not deducted from repymt income
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:129** (1 rules)
- Condition: Virtual currency was considered as an asset based income type
- What's needed: cryptocurrency/virtual-currency income-conversion documentation (same gap flagged in the asset-verification triage) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:130** (1 rules)
- Condition: 2 mos rent or 1st mo & security dep not cashed/deposited, 3rd party xfer, or in escrow as applicable
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:131** (1 rules)
- Condition: A 12 month avg of boarder rental income not used where documented for only 9 of the last 12 months
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:132** (1 rules)
- Condition: Boarder rental income used as effective income exceeds 30% of the effective income used to qualify
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:133** (1 rules)
- Condition: Existing lease not current & fully executed for a subject property refinance or non-subject property
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:134** (1 rules)
- Condition: Investment purchase-multiple borr's live in same property w/out evidence at least 1 owns/rents
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:135** (1 rules)
- Condition: Lease used in lieu of a tax return for rental income w/out evidence the property was out of service
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:136** (1 rules)
- Condition: Long-term rental income did not meet the Option 1 criteria of the stability and continuance req's
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:137** (1 rules)
- Condition: New lease 1st rental pymt date is due after the 1st mtg pymt date in a refi or non-subject property
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:139** (1 rules)
- Condition: Primary converted to a rental & rental income added to monthly income and not just to offset PITI
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:140** (1 rules)
- Condition: Qualifying rental income based on the number of days in service as per Sch E without meeting req's
- What's needed: Schedule E rental-income tax-return page — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:141** (1 rules)
- Condition: Rental income not calculated correctly &/or negative rent not added to the borrower's liabilities
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:142** (1 rules)
- Condition: Short-term rental income did not meet the Option 2 criteria of the stability and continuance req's
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:143** (1 rules)
- Condition: Business debt excluded from DTI - no evidence business paid for last 12 mos
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:145** (1 rules)
- Condition: The file did not document that the business is operational within 30 days of the loan closing
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:146** (1 rules)
- Condition: The self employment income calculated incorrectly
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:147** (1 rules)
- Condition: Written analysis of income not in the file for self employment
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:148** (1 rules)
- Condition: “Business Owner” or “Self-Employed” selected in GUS & the borr's ownership interest is less than 25%
- What's needed: GUS findings / USDA residual-income worksheet field — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:149** (1 rules)
- Condition: Alimony/child support/maintenance missing legal docs &/or history and continuance req's not met
- What's needed: alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:150** (1 rules)
- Condition: An average of child support/maintenance was not used where the payments are inconsistent
- What's needed: alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:152** (1 rules)
- Condition: 2 yr avg not used for inconsistent court ordered alimony/child supp/maintenance pymts in last 3 mos
- What's needed: alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:153** (1 rules)
- Condition: 2 yr avg not used for inconsistent voluntary alimony, child support, maintenance pymts in last 6 mos
- What's needed: alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:154** (1 rules)
- Condition: Divorce decree, separation agreement, court order/voluntary pmt agreement with receipt not provided
- What's needed: alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:156** (1 rules)
- Condition: Alimony, child support, maintenance not on 1003 & not requested by borrower  to use as income
- What's needed: alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:157** (1 rules)
- Condition: Documentation verifying alimony/child support income will continue for at least 3 years not provided
- What's needed: alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:159** (1 rules)
- Condition: Minimum of 6 mos alimony/child support/maintenance full & timely pay history not provided
- What's needed: alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:161** (1 rules)
- Condition: Other types of nontaxable income were considered without documents to verify nontaxable status
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:162** (1 rules)
- Condition: The "grossed up" calculation for child support income was not calculated correctly
- What's needed: alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:163** (1 rules)
- Condition: The "grossed up" calculation of other nontaxable income was not calculated correctly
- What's needed: alimony/child-support legal decree or written agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:165** (1 rules)
- Condition: Net family assets that exceed $50,000 were not considered in the annual income calculation
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:166** (1 rules)
- Condition: No evidence employment gaps were analyzed determining income is stable and dependable
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:169** (1 rules)
- Condition: The applicant's adjusted annual household income exceeds applicable moderate income program limit
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:170** (1 rules)
- Condition: Time in college, tech school or career HS cert used toward annual repayment w/out a certificate
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:171** (1 rules)
- Condition: Verification of investment accounts used as income assets was not provided
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:172** (1 rules)
- Condition: Anticipated income-start date greater than 30 days prior to or greater than 90 days after Note date
- What's needed: employment offer/contract letter (anticipated/new-employment income) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:173** (1 rules)
- Condition: Anticipated income-w/out new paystub & loan feature, financial resource & reserve req's not met
- What's needed: employment offer/contract letter (anticipated/new-employment income) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:174** (1 rules)
- Condition: Employment start date is within 90 days after Note date missing an employment offer/contract
- What's needed: employment offer/contract letter (anticipated/new-employment income) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:177** (1 rules)
- Condition: The offer or contract for employment is by a family member or interested party to the transaction
- What's needed: employment offer/contract letter (anticipated/new-employment income) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:178** (1 rules)
- Condition: All req's not met relying on retirement assets as a basis for qualification
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:179** (1 rules)
- Condition: Assets from sale of business proceeds & no documentation borr was sole owner &/or doc req's not met
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:181** (1 rules)
- Condition: Cryptocurrency was considered as an asset based income type
- What's needed: cryptocurrency/virtual-currency income-conversion documentation (same gap flagged in the asset-verification triage) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:182** (1 rules)
- Condition: Eligibility requirements for asset qualification not met &/or the DTI calculation was incorrect
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:183** (1 rules)
- Condition: Eligible assets used as a basis for repayment of obligations not divided by 240 for the DTI ratio
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:185** (1 rules)
- Condition: Income that is paid to the borrower in cryptocurrency was used for qualification
- What's needed: cryptocurrency/virtual-currency income-conversion documentation (same gap flagged in the asset-verification triage) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:187** (1 rules)
- Condition: Verification of access to lump-sum distribution & assets are not a source of income not provided
- What's needed: retirement-account statement (401(k)/IRA/Keogh/pension) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:188** (1 rules)
- Condition: Auto allowance received from the employer for the previous two years was not verified and documented
- What's needed: automobile-allowance employer letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:189** (1 rules)
- Condition: Auto allowance was considered stable income & full amt of allowance was not added to monthly income
- What's needed: automobile-allowance employer letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:190** (1 rules)
- Condition: Documentation verifying borrower has received auto allowance for at least 2 yrs was not provided
- What's needed: automobile-allowance employer letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:191** (1 rules)
- Condition: Full lease/debt pymt not added to the debt obligations as applicable for an automobile allowance
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:195** (1 rules)
- Condition: Documentation verifying the applicant has received tip income for the previous 2 yrs not provided
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:196** (1 rules)
- Condition: File does not contain a completed VOE or the most recent paystub & two years W-2s or as per DU
- What's needed: W-2 form(s) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:197** (1 rules)
- Condition: Income used did not have 2 yr history & no comp factors given to offset the shorter income history
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:199** (1 rules)
- Condition: Verification that the OT/bonus income has been received for the last two years was not provided
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:200** (1 rules)
- Condition: 1 yr business tax returns used where business existence or at least 25% ownership is less than 5 yrs
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:201** (1 rules)
- Condition: Most recent 2yrs signed bus. tax returns, including all schedules/tax transcripts not provided
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:203** (1 rules)
- Condition: Underwriter did not provide a written analysis of the applicant's business income
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:206** (1 rules)
- Condition: Verification that commission income has been received for 1 yr and will continue was not provided
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:207** (1 rules)
- Condition: Borrower’s receipt of benefits from the disability insurance provider was not verified & documented
- What's needed: disability-benefits payer statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:208** (1 rules)
- Condition: Missing long term disability eligibility confirmation, amount, frequency & end date or as per DU
- What's needed: disability-benefits payer statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:210** (1 rules)
- Condition: VA disability not documented with VA's last benefits letter & acceptable evidence of receipt
- What's needed: benefits/award letter (SSA, VA, pension, or disability payer) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:212** (1 rules)
- Condition: The employer housing subsidy was used to offset the mortgage payment
- What's needed: employer housing-subsidy / parsonage agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:213** (1 rules)
- Condition: The existence and the amount of the employer housing subsidy was not verified and documented
- What's needed: employer housing-subsidy / parsonage agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:214** (1 rules)
- Condition: 3rd party employment verification was used but documentation does not meet Fannie Mae's requirements
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:215** (1 rules)
- Condition: Gaps in employment were not addressed as required
- What's needed: an employment-gap-explanation document/field — not currently captured
- Machine-checkable: presence of an employment-gap explanation

**income-verification:217** (1 rules)
- Condition: Paystub not within 30 days &/or did not have YTD earnings or sufficient pay info to calculate income
- What's needed: paystub — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:218** (1 rules)
- Condition: Paystubs and W2's source was not a third party ex: HR, payroll, personnel dept, payroll vendor etc
- What's needed: W-2 form(s) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:219** (1 rules)
- Condition: The W2's obtained did not cover the number of years that were required
- What's needed: W-2 form(s) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:220** (1 rules)
- Condition: The employer did not complete all required fields on the standard VOE form 1005
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:223** (1 rules)
- Condition: The paystubs and/or W2's were incomplete or were illegible
- What's needed: W-2 form(s) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:224** (1 rules)
- Condition: The paystubs/W2's did not clearly identify the borrower as the employee
- What's needed: W-2 form(s) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:226** (1 rules)
- Condition: Alternative employment req's not met w/ most recent YTD paystub, 2 years W2s & a completed VVOE
- What's needed: verbal VOE (VVOE) call/database log — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:227** (1 rules)
- Condition: Data on the electronic reverification of employment was not current w/in 30 days of the verification
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:228** (1 rules)
- Condition: Direct verification of the borrower's prior 2 years employment history was not obtained as required
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:229** (1 rules)
- Condition: Employed by a family member/interested party & the most recent years tax returns were not provided
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:230** (1 rules)
- Condition: Income calculation requirements were not met
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:231** (1 rules)
- Condition: Income has a defined expiration date & documentation verifying 3 year continuance was not provided
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:234** (1 rules)
- Condition: Income that is paid to the borrower in virtual currency was used for qualification
- What's needed: cryptocurrency/virtual-currency income-conversion documentation (same gap flagged in the asset-verification triage) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:235** (1 rules)
- Condition: No direct verification of past employment & OT, bonus &/or tip income used in lieu of only base pay
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:237** (1 rules)
- Condition: Not same employer for 2 yrs and no direct verification without meeting all req's for 2 yr history
- What's needed: IRS Form 4506-C/8821 tax-transcript consent form — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:238** (1 rules)
- Condition: Not the same employer for 2 yrs & 1 or more acceptable documents verifying 2 yr history not in file
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:240** (1 rules)
- Condition: The verbal verification of employment does not show borrower in an active status
- What's needed: a VVOE (verbal verification of employment) log/status fact — not currently modeled; the corpus has a written/signed VOE (loan 01) but no distinct verbal-VOE artifact with an active/inactive status field
- Machine-checkable: -

**income-verification:241** (1 rules)
- Condition: Traditional employment req's not met w/ a paystub & 2 year VOE or direct electronic VOE by a TPV
- What's needed: paystub — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:242** (1 rules)
- Condition: Variable income used, history of receipt, frequency and trending of the amount were not provided
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:243** (1 rules)
- Condition: Vendor for 3rd party VOE was not Equifax/TWN or manual process not followed
- What's needed: a VOE-vendor-name field (e.g. Equifax/The Work Number) — not currently captured from any document
- Machine-checkable: -

**income-verification:244** (1 rules)
- Condition: Documentation verifying that borrower is not an owner in the family-owned business was not provided
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:246** (1 rules)
- Condition: Signed personal tax returns/tax transcripts not obtained where employed by a family-owned business
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:247** (1 rules)
- Condition: At least 12 mos stable income not used when excluding a time period for an event unlikely to recur
- What's needed: multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:248** (1 rules)
- Condition: Fluctuating income calc based on shorter # of mos w/out written justification &/or supporting docs
- What's needed: multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:249** (1 rules)
- Condition: Fluctuation is > 10% but less than or = 30% without supporting documentation/additional analysis
- What's needed: multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:250** (1 rules)
- Condition: Income considered fluctuating earnings for minor base hour variations of an hour or less per week
- What's needed: multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:251** (1 rules)
- Condition: Income is fluctuating hourly employment earnings without a minimum employment history 12 months
- What's needed: multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:252** (1 rules)
- Condition: Min req'd hours considered non-fluctuating; additional hours not qualified as fluctuating earnings
- What's needed: multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:253** (1 rules)
- Condition: No addtl documentation provided to support using less than avg of recent year(s) & YTD to qualify
- What's needed: multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:255** (1 rules)
- Condition: The degree of fluctuation is > 30% with no addt'l analysis/documents for stability & calculation
- What's needed: multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:256** (1 rules)
- Condition: The income was calculated incorrectly for the borrower with income that is fluctuating in nature
- What's needed: multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:258** (1 rules)
- Condition: File does not contain required documentation of any previous employment needed to document 2 yrs
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:260** (1 rules)
- Condition: The employment verification service used did not  provide full verification data for all applicants
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:261** (1 rules)
- Condition: The file does not contain the required documentation of current employment
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:262** (1 rules)
- Condition: The file does not contain the required explanation for any gaps in employment
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:264** (1 rules)
- Condition: The residual income was insufficient as per family size and geographic region
- What's needed: GUS findings / USDA residual-income worksheet field — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:265** (1 rules)
- Condition: The verbal verification of employment does not show borrower in an active status
- What's needed: a VVOE (verbal verification of employment) log/status fact — not currently modeled; the corpus has a written/signed VOE (loan 01) but no distinct verbal-VOE artifact with an active/inactive status field
- Machine-checkable: -

**income-verification:267** (1 rules)
- Condition: Effective income used to qualify was calculated incorrectly
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:268** (1 rules)
- Condition: Income calculation requirements were not met
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:270** (1 rules)
- Condition: Income was included in qualifying that did not meet the definition of effective income
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:275** (1 rules)
- Condition: Full doc did not include 2 yrs W2s or tax trans, 1 mo paystubs & a 10 bus VVOE/other written verif
- What's needed: verbal VOE (VVOE) call/database log — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:276** (1 rules)
- Condition: IRS tax transcripts for validation of household income for 2 years was not obtained
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:278** (1 rules)
- Condition: Initial or reverification VVOE did not contain all required information
- What's needed: verbal VOE (VVOE) call/database log — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:280** (1 rules)
- Condition: Specific income types: Annual income, history, continuation, and/or documentation reqs were not met
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:282** (1 rules)
- Condition: The verbal verification of employment does not show borrower in an active status
- What's needed: a VVOE (verbal verification of employment) log/status fact — not currently modeled; the corpus has a written/signed VOE (loan 01) but no distinct verbal-VOE artifact with an active/inactive status field
- Machine-checkable: -

**income-verification:283** (1 rules)
- Condition: Housing/Parsonage income receipt for last 12 mths and/or continuance for next 3 years not documented
- What's needed: employer housing-subsidy / parsonage agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:286** (1 rules)
- Condition: Section 8 housing voucher income is nontaxable and an adjusted gross income was not developed
- What's needed: Section 8 / Housing Choice Voucher award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:287** (1 rules)
- Condition: Section 8 vouchers-Voucher from public housing agency stating payment amount & duration not obtained
- What's needed: Section 8 / Housing Choice Voucher award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:288** (1 rules)
- Condition: MCC-Documentation verifying governmental entity subsidizes the mortgage payments was not provided
- What's needed: Mortgage Credit Certificate (MCC) document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:290** (1 rules)
- Condition: Section 8 vouchers-Documentation verifying borrower receives Housing Choice subsidies not provided
- What's needed: Section 8 / Housing Choice Voucher award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:291** (1 rules)
- Condition: The amount of the mortgage credit certificate tax rebate was not documented and verified
- What's needed: Mortgage Credit Certificate (MCC) document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:292** (1 rules)
- Condition: The current mortgage credit certificate subsidy rate was not used to calculate the effective income
- What's needed: Mortgage Credit Certificate (MCC) document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:293** (1 rules)
- Condition: The public assistance income received from the government agency was not verified and documented
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:294** (1 rules)
- Condition: Calculation methods for base non-fluctuating employment earnings incorrect
- What's needed: multi-year fluctuating-income history (not currently extracted beyond a single point-in-time base income figure) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:295** (1 rules)
- Condition: Income calculation requirements were not met
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:299** (1 rules)
- Condition: The verbal verification of employment does not show borrower in an active status
- What's needed: a VVOE (verbal verification of employment) log/status fact — not currently modeled; the corpus has a written/signed VOE (loan 01) but no distinct verbal-VOE artifact with an active/inactive status field
- Machine-checkable: -

**income-verification:300** (1 rules)
- Condition: Analysis of income and/or asset qualification source and amount not in file
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:301** (1 rules)
- Condition: Change in line of work/change of employers over 3x in last 12 mos & income stability not documented
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:302** (1 rules)
- Condition: Employment gap 6 mos or more & not currently employed for at least 6 mos &/or no 2 yr history
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:303** (1 rules)
- Condition: Less than 2 yr employment history & documentation req's not met to justifying stable employment
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:304** (1 rules)
- Condition: Likeliness to continue not evaluated correct based on income/earnings type
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:306** (1 rules)
- Condition: Temp income reduction-Current income as effective income used w/out meeting all requirements
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:307** (1 rules)
- Condition: The income written analysis did not include all required topics
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:308** (1 rules)
- Condition: Email verification as a VVOE alt not dated w/in 10 business days &/or did not include all req'd info
- What's needed: verbal VOE (VVOE) call/database log — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:309** (1 rules)
- Condition: Military leave & earnings stmt used to meet the 10 day PCV requirement not dated within 120 days
- What's needed: military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:312** (1 rules)
- Condition: The required W2 or acceptable alternative was not in the file
- What's needed: W-2 form(s) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:313** (1 rules)
- Condition: The verbal verification of employment does not show borrower in an active status
- What's needed: a VVOE (verbal verification of employment) log/status fact — not currently modeled; the corpus has a written/signed VOE (loan 01) but no distinct verbal-VOE artifact with an active/inactive status field
- Machine-checkable: -

**income-verification:314** (1 rules)
- Condition: Third-party 10-day PCV used and name/contact information for the service provider not documented
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:315** (1 rules)
- Condition: VOE did not provide all required employment & earning information for most recent 1 or 2 yr period
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:316** (1 rules)
- Condition: VOE for prior employment did not contain all required employment/earnings information
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:318** (1 rules)
- Condition: VVOE or alternative missing or not dated w/in 10 business days of the Note &/or missing information
- What's needed: verbal VOE (VVOE) call/database log — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:319** (1 rules)
- Condition: Vendor for 3rd party VOE was not Equifax/TWN or manual process not followed
- What's needed: a VOE-vendor-name field (e.g. Equifax/The Work Number) — not currently captured from any document
- Machine-checkable: -

**income-verification:320** (1 rules)
- Condition: Verification of income from 3rd party was used, but did not meet 3rd party verification requirements
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:322** (1 rules)
- Condition: YTD paystub not last prior to Note date & paid through date over 15 business days prior to Note date
- What's needed: paystub — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:323** (1 rules)
- Condition: Interest & dividend-Most recent 2 yrs tax returns & most recent account statement were not provided
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:324** (1 rules)
- Condition: Investment-Not verified & documented with tax returns for previous 2yrs & most recent acct statement
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:326** (1 rules)
- Condition: Income grossed up, amount/source of the income & current tax rate applicable not documented
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:328** (1 rules)
- Condition: Manual underwrite of SE borrower missing last 2 yrs complete individual & business tax returns
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:330** (1 rules)
- Condition: Self employment income from a corporation used to qualify; a business credit report was not obtained
- What's needed: business tax return / business credit report / business-existence verification — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:331** (1 rules)
- Condition: "Other" military income (not base pay) was not documented as stable
- What's needed: military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:332** (1 rules)
- Condition: A copy of the military leave and earnings statement was not provided
- What's needed: military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:333** (1 rules)
- Condition: A verification from VA was not in the file to support the direct compensation from VA benefits
- What's needed: military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:335** (1 rules)
- Condition: Military LES not dated within 120 calendar days as req'd when used in lieu of a VVOE
- What's needed: verbal VOE (VVOE) call/database log — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:336** (1 rules)
- Condition: Military base pay & entitlements was not documented with the most recent leave & earnings statement
- What's needed: military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:337** (1 rules)
- Condition: Military base pay &/or entitlements not documented as likely to continue for at least the next 3 yrs
- What's needed: military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:338** (1 rules)
- Condition: Military base pay not documented w/ YTD Leave & Earnings Stmt or VOE with all YTD & 10-day PCV
- What's needed: military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:339** (1 rules)
- Condition: Military entitlements not documented w/ YTD Leave & Earnings Stmt or VOE with all YTD & 10-day PCV
- What's needed: military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:340** (1 rules)
- Condition: Military income was not verified as continuous, regular and likely to continue
- What's needed: military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:341** (1 rules)
- Condition: Military leave & earnings stmt used to meet the 10 day PCV requirement not dated within 120 days
- What's needed: military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:343** (1 rules)
- Condition: Reserve & Nat'l Guard income history of receipt for 1 yr &/or 3 yrs continuance was not documented
- What's needed: military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:344** (1 rules)
- Condition: Reserve and Nat'l Guard income not documented w/YTD L&E stmt & W-2 or VOE w/ all YTD & 10-day PCV
- What's needed: military Leave & Earnings Statement (LES) / VA benefits award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:348** (1 rules)
- Condition: All req's not met for new employment w/ income starting after the note date
- What's needed: employment offer/contract letter (anticipated/new-employment income) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:349** (1 rules)
- Condition: Ext absence, new to work or recent employment gaps w/out documentation supporting stable employment
- What's needed: employment offer/contract letter (anticipated/new-employment income) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:350** (1 rules)
- Condition: Income type unacceptable to use where employment history is more than 1 year but less than 2
- What's needed: employment offer/contract letter (anticipated/new-employment income) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:352** (1 rules)
- Condition: Qualifying income is future current employer salary increase not documented &/or all req's not met
- What's needed: employment offer/contract letter (anticipated/new-employment income) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:353** (1 rules)
- Condition: Guardianship/conservatorship income amount currently being received was not documented in the file
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:354** (1 rules)
- Condition: Most recent assets from applicants/household members at application not used in annual income review
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:356** (1 rules)
- Condition: Personal & business asset accounts are co-mingled & not included in calculation of net family assets
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:357** (1 rules)
- Condition: Section 8 Housing Vouchers not documented with a benefit/award letter verifying the subsidy amount
- What's needed: benefits/award letter (SSA, VA, pension, or disability payer) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:358** (1 rules)
- Condition: The mortgage credit certificate (MCC) amount used as qualifying income was calculated incorrectly
- What's needed: Mortgage Credit Certificate (MCC) document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:359** (1 rules)
- Condition: The mortgage credit certificate (MCC) award letter/contract with the rate of credit not in the file
- What's needed: benefits/award letter (SSA, VA, pension, or disability payer) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:360** (1 rules)
- Condition: 2 yr history of foster care, pymt &/or continuance not validated on written foster care verification
- What's needed: foster-care sponsoring-organization verification letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:361** (1 rules)
- Condition: A letter or distribution form from VA stating the benefits will continue for 3 yrs was not provided
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:363** (1 rules)
- Condition: A written verification of foster care payment was not obtained from the organization providing it
- What's needed: foster-care sponsoring-organization verification letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:364** (1 rules)
- Condition: Agreement from employer stating terms including scheduled amt & duration of payments not provided
- What's needed: employer-subsidy / mortgage-differential agreement letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:366** (1 rules)
- Condition: Auto allowance or expense acct payments considered without all history & continuance req's being met
- What's needed: automobile-allowance employer letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:367** (1 rules)
- Condition: Boarders-Documentation verifying history of shared residency/rent payment for 12 mos not provided
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:368** (1 rules)
- Condition: Consecutive 2 yr history receiving tip income & that it is likely to continue for 3 yrs not provided
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:369** (1 rules)
- Condition: Current employment less than 12 mos or notable earnings increase w/out documenting income stability
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:370** (1 rules)
- Condition: Employed by a family-owned bus. & evidence that applicant is not owner of the business not provided
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:371** (1 rules)
- Condition: Employer housing allowance was not documented as established &/or continuance requirements not met
- What's needed: employer housing-subsidy / parsonage agreement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:372** (1 rules)
- Condition: Foster care is considered without all required documentation and terms being met
- What's needed: foster-care sponsoring-organization verification letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:373** (1 rules)
- Condition: Govnt assistance funds used and not documented &/or history and continuance requirements not met
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:374** (1 rules)
- Condition: Homeownership Voucher history/cont req's not met &/or documentation did not provide required info
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:375** (1 rules)
- Condition: Income calculation requirements were not met
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:377** (1 rules)
- Condition: Interest & dividend-Copies of tax returns or account statements verifying 2 yrs receipt not provided
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:378** (1 rules)
- Condition: Interest/dividend income not a 2 yr avg less cash to close &/or history & continuance req's not met
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:379** (1 rules)
- Condition: Loans/deductions listed on the paystubs were not addressed
- What's needed: a paystub-level 'loans/deductions' line-item field — not in FIELD_SPECS['paystub'] today
- Machine-checkable: -

**income-verification:380** (1 rules)
- Condition: MCC income did not meet documentation &/or qualifying requirements
- What's needed: Mortgage Credit Certificate (MCC) document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:381** (1 rules)
- Condition: No 2 yr income history & the file did not document the analysis used supporting income stability
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:382** (1 rules)
- Condition: Non-employment/non-self-employment "other" income used was not calculated correctly
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:383** (1 rules)
- Condition: Non-taxable income grossed-up and income used to qualify was not adequately documented & supported
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:385** (2 rules)
- Condition: Notes Receivable-Existence of the note & consistent pymts for last 12 mos not verified & documented
- What's needed: notes-receivable promissory note + deposit evidence — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:386** (1 rules)
- Condition: Notes Receivable-Note & deposit slips/tax returns/bank stmts documenting 12 mo receipt not provided
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:387** (1 rules)
- Condition: Public assistance-Letters/exhibits from paying agency stating amt, frequency & duration not provided
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:388** (1 rules)
- Condition: Rental income from a live-in personal assistant for a disabled borrower exceeded 30% of gross income
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:389** (1 rules)
- Condition: Royalty-Tax returns, contract/alt documentation and 12 mo receipt with 3 yr continuance not provided
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:390** (1 rules)
- Condition: SSI has been grossed up without proper documentation supporting it
- What's needed: SSI gross-up documentation fields — not currently captured
- Machine-checkable: -

**income-verification:391** (1 rules)
- Condition: Sect 8 Homeownership Voucher not used as repayment income or offset to PITI
- What's needed: Section 8 / Housing Choice Voucher award letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:392** (1 rules)
- Condition: Temporary leave income used and the income does not meet Fannie Mae's requirements
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:393** (1 rules)
- Condition: The expected income was not verified and documented in writing with the employer
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:394** (1 rules)
- Condition: The file does not contain a written verification from the employer for the employer's subsidy
- What's needed: employer-subsidy / mortgage-differential agreement letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:395** (1 rules)
- Condition: The foster care income was not calculated using the lesser of last year or 2 year average
- What's needed: foster-care sponsoring-organization verification letter — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:396** (1 rules)
- Condition: The frequency, duration and amount of the trust distribution were not verified and documented
- What's needed: trust agreement/trustee statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:397** (1 rules)
- Condition: The job/increase in income not verified by employer in writing & scheduled to begin within 60 days
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:399** (1 rules)
- Condition: 2 consecutive year history of paying OT/bonus income along with 3 year continuance was not provided
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:400** (1 rules)
- Condition: Commission income considered without the analysis being documented to support the income is stable
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:401** (1 rules)
- Condition: Commission income was considered without history and continuance requirements being met
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:403** (1 rules)
- Condition: OT & bonus income used & written analysis supporting decision to use additional income not provided
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:405** (1 rules)
- Condition: Verification that the OT/bonus/tip income has been received for 1 yr and will continue not provided
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:408** (1 rules)
- Condition: Tip income used, Form 4137 and tax returns for the most recent two years were not provided
- What's needed: 1099 (or Form 4137 tip-income) tax form — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:411** (1 rules)
- Condition: Part-time, secondary, seasonal or unemployment income used without history and continuance req's met
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:412** (1 rules)
- Condition: Part-time, secondary, seasonal or unemployment is considered w/out analysis to support stable income
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:414** (1 rules)
- Condition: Verification the PT job has been uninterrupted for past 2 yrs and is likely to continue not provided
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:415** (1 rules)
- Condition: 2-4 OO or 1-4 NOO schedule E or lease rent not supported by current market rents without comment
- What's needed: Schedule E rental-income tax-return page — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:416** (1 rules)
- Condition: A lease was used in place of IRS Form 1040, Sch E, to document rental income without justification
- What's needed: Schedule E rental-income tax-return page — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:417** (1 rules)
- Condition: ADU rental income used as effective income exceeded 30% of the effective income used to qualify
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:418** (1 rules)
- Condition: Boarder income did not include 12 mos history & signed agrmnt w/ terms & intent to continue boarding
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:419** (1 rules)
- Condition: Correct documents not used to calculate rental income as per rent history, property & loan type
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:420** (1 rules)
- Condition: Existing lease in a purchase was not current & fully executed in the seller's name as the landlord
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:421** (1 rules)
- Condition: File did not document boarder rent received for at least 9 of the most recent 12 months
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:422** (1 rules)
- Condition: File did not document the req'd property management experience for investment property rental income
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:423** (1 rules)
- Condition: File did not verify boarder’s address is the same as borr’s address where boarder income was used
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:424** (1 rules)
- Condition: Form 1007/1025 not provided & lease terms were not in effect with receipt of 2 months rental pymts
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:425** (1 rules)
- Condition: Form 72/1000 or 2 mos rent/deposit & 1st mos rent multi unit/non-subj invest bought/rented last yr
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:426** (1 rules)
- Condition: Gross rents & expenses through a partnership or S corp & business return w/ form 8825 not provided
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:427** (1 rules)
- Condition: Investment property rental income not documented as req'd per length of ownership & property type
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:429** (1 rules)
- Condition: Lesser of monthly op income or 75% of fair market rent not used for subj rent with limited history
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:430** (1 rules)
- Condition: Long term rental income used without last 2 years tax returns including Schedule E &/or signed lease
- What's needed: Schedule E rental-income tax-return page — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:431** (1 rules)
- Condition: No lease with reasonable efforts determining lease availability or Form 72/1000 in a purchase
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:433** (1 rules)
- Condition: Proposed rental income was not documented with a URAR & a Single Family Comparable Rent Schedule
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:434** (1 rules)
- Condition: Purchase or rental start in last year & no purchase or conversion date &/or lease not used in refi
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:435** (1 rules)
- Condition: Rental income analysis & documentation based on the time the rental was in service was inappropriate
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:436** (1 rules)
- Condition: Rental income calculated incorrectly &/or not added to income or debts
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:437** (1 rules)
- Condition: Rental income eligibility &/or continuance req's not met as applicable per property/occupancy types
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:438** (1 rules)
- Condition: Rental income from a 1 unit w/ an ADU or 2-4 unit primary was not entered as Accessory Unit Income
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:439** (1 rules)
- Condition: Rental income from live-in-aide and documentation verifying income meets guidelines was not provided
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:440** (1 rules)
- Condition: Rental income received less than 24 mos was not excluded &/or the full debt not considered in ratios
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:441** (1 rules)
- Condition: Rental income req's for current housing exp & rental history for 1-4 or 2-4 transactions not met
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:442** (1 rules)
- Condition: Rental income used from the property being vacated by the borr who is not moving over 100 mi away
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:443** (1 rules)
- Condition: Subject rental income not documented as required as per the length of ownership and property type
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:444** (1 rules)
- Condition: The amount of rental income relied on is not within the maximum allowable net rental income
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:445** (1 rules)
- Condition: The file did not contain FNMA Form 1007 or Form 1025, as applicable, or did not meet all form req's
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:446** (1 rules)
- Condition: The lease transferred to the borr impacts first lien position or enforceability of the subject loan
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:448** (1 rules)
- Condition: ADU rental analysis did not include 3 comp rentals supporting market rent with 1 having a rented ADU
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:449** (1 rules)
- Condition: ADU rental income exceeded 30% of the total stable monthly income
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:450** (1 rules)
- Condition: An ACE appraisal offer was accepted where rental income from an ADU was used
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:451** (1 rules)
- Condition: Comparables in the Sales Comparison Approach section did not include at least 1 comp with an ADU
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:452** (1 rules)
- Condition: Min income documentation req's not met as applicable for a purchase/NCO refi with ADU rental income
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:454** (1 rules)
- Condition: Qualifying borr did not do landlord education or 1 yr landlord experience using ADU rental income
- What's needed: lease / Schedule E / Form 1007-1025 rental-income document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:455** (1 rules)
- Condition: 2 year history or 1 w/ supporting documentation of receipt of K-1 income w/ less than 25% ownership
- What's needed: K-1 / Form 1065 / 1120S business tax-return schedule — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:456** (1 rules)
- Condition: 2yrs K-1s not in the file where borrower receives income from business with less than 25% ownership
- What's needed: K-1 / Form 1065 / 1120S business tax-return schedule — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:457** (1 rules)
- Condition: Available YTD info not in the file where income is rec'd from business with less than 25% ownership
- What's needed: K-1 / Form 1065 / 1120S business tax-return schedule — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:458** (1 rules)
- Condition: Current business existence not documented for borrower with less than 25% ownership & K-1 income
- What's needed: K-1 / Form 1065 / 1120S business tax-return schedule — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:461** (1 rules)
- Condition: Missing IRS W-2s covering the most recent two-year period reflecting RSU/RS distributions
- What's needed: RSU/restricted-stock vesting-schedule document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:464** (1 rules)
- Condition: No documentation RSU/RS is publicly traded &/or is missing the current vesting schedule
- What's needed: RSU/restricted-stock vesting-schedule document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:465** (1 rules)
- Condition: No evidence RS/RSU is publicly traded, vesting schedule is in effect &/or previous year pay out
- What's needed: RSU/restricted-stock vesting-schedule document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:466** (1 rules)
- Condition: Non-recurring RS/RSU income did not have at least 3 yrs vesting & distribution left on vesting sch
- What's needed: RSU/restricted-stock vesting-schedule document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:468** (1 rules)
- Condition: Performance RS/RSU with employer is 12-24 mos & calculated using less time that was not supported
- What's needed: RSU/restricted-stock vesting-schedule document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:469** (1 rules)
- Condition: RS/RSU income awarded on a recurring basis was not likely to continue for at least 3 years
- What's needed: RSU/restricted-stock vesting-schedule document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:470** (1 rules)
- Condition: RS/RSU income not calculated correctly as per the form the vested RS or RSU are distributed
- What's needed: RSU/restricted-stock vesting-schedule document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:471** (1 rules)
- Condition: RS/RSU stock considered without meeting history/continuance, documentation reqs &/or 10 day PCV
- What's needed: RSU/restricted-stock vesting-schedule document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:472** (1 rules)
- Condition: Restricted stock was not documented as vested and distributed to the borrower without restrictions
- What's needed: RSU/restricted-stock vesting-schedule document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:473** (1 rules)
- Condition: The 200-day simple moving avg stock price as basis for calculating RS/RSU income not documented
- What's needed: RSU/restricted-stock vesting-schedule document — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:474** (1 rules)
- Condition: A Benefits Letter &/or likeliness to continue for 3 yrs not documented for social security income
- What's needed: 1099 (or Form 4137 tip-income) tax form — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:475** (1 rules)
- Condition: File is missing the SSA award letter, SSA-1099, last signed tax returns or proof of current receipt
- What's needed: 1099 (or Form 4137 tip-income) tax form — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:477** (1 rules)
- Condition: Incorrect percentage used to "gross up" the verified nontaxable social security income as applicable
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:478** (1 rules)
- Condition: Missing award letter, 3 yr cont & receipt of SSI drawn from another's acct or own to benefit another
- What's needed: benefits/award letter (SSA, VA, pension, or disability payer) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:479** (1 rules)
- Condition: More than 15% was used to "gross up" SSI without documentation to support the income is nontaxable
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:481** (1 rules)
- Condition: Recurring  receipt & likeliness to cont. for 3 yrs not documented for IRA/401(k) income
- What's needed: retirement-account statement (401(k)/IRA/Keogh/pension) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:482** (1 rules)
- Condition: Retirement income from a 401(k), IRA, or Keogh acct without 3 yr continuance
- What's needed: retirement-account statement (401(k)/IRA/Keogh/pension) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:483** (1 rules)
- Condition: Retirement, annuity or pension not verified using allowable documentation or as required by DU
- What's needed: retirement-account statement (401(k)/IRA/Keogh/pension) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:484** (1 rules)
- Condition: Retirement, annuity, pension income used w/out evidence borr has unrestricted access w/out penalty
- What's needed: retirement-account statement (401(k)/IRA/Keogh/pension) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:485** (1 rules)
- Condition: SSI from another person's acct or for a dependent was used to qualify w/out a 3- yr continuance
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:486** (1 rules)
- Condition: The borrower’s receipt of the retirement income was not verified and documented
- What's needed: benefits/award letter (SSA, VA, pension, or disability payer) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:488** (1 rules)
- Condition: Two year verification of seasonal work and that it is reasonably likely to continue was not provided
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:489** (1 rules)
- Condition: Unemployment income used & 2 yrs signed tax returns with evidence of continuance was not provided
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:490** (1 rules)
- Condition: Documentation verifying 2nd job income has been uninterrupted for the previous 2 yrs not provided
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:491** (1 rules)
- Condition: Last 2 years of seasonal work not documented or as per DU
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:493** (1 rules)
- Condition: Secondary employment has a gap of over 1 month in last 12 mos & employment not changed to seasonal
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:494** (1 rules)
- Condition: Business in existence 5+ years & most recent 1 yr signed tax return not provided or as per LP
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:495** (1 rules)
- Condition: Business in existence less than 5 years & last 2 years signed tax returns not provided or as per LP
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:496** (1 rules)
- Condition: Business structure owner interest % change so the business is no longer considered the same business
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:497** (1 rules)
- Condition: File is missing the required IRS confirmation transcripts not available for the prior year
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:499** (1 rules)
- Condition: Last two years business tax returns with all applicable schedules were not provided
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:500** (1 rules)
- Condition: Most recent year tax returns not filed and an extension from the IRS not documented
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:501** (1 rules)
- Condition: No Verification of existence of business from 3rd party/acceptable alt within 120 days of note date
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:502** (1 rules)
- Condition: No evaluation the current and prior business structures can be treated as the same business
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:504** (1 rules)
- Condition: SE < 2 yrs & no combined 2 yr history from current & prior in similar industry & stability analysis
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:505** (1 rules)
- Condition: SE < 2 yrs & qual income not the lesser of the stable monthly income from the new or previous income
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:506** (1 rules)
- Condition: The Freddie Mac Income Analysis Form was not provided in the file
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:507** (1 rules)
- Condition: 1 yr personal tax returns used where business existence or at least 25% ownership is less than 5 yrs
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:508** (1 rules)
- Condition: Corp or partnership missing 2 yrs signed business tax returns & all  schedules or as per AUS
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:509** (1 rules)
- Condition: Documentation demonstrating the K-1 income may be used to qualify was not provided
- What's needed: K-1 / Form 1065 / 1120S business tax-return schedule — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:511** (1 rules)
- Condition: Evidence of the borrower's ownership in a corporation or partnership not provided
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:513** (1 rules)
- Condition: Income calculation requirements were not met
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:516** (1 rules)
- Condition: Meals and Entertainment & Mtg < 1 Yr not deducted
- What's needed: Schedule C 'meals & entertainment' and 'notes payable < 1 year' deduction line items — not in FIELD_SPECS for any self-employed doc type today
- Machine-checkable: -

**income-verification:517** (1 rules)
- Condition: Missing 2 years signed individual tax returns or IRS transcripts including all applicable schedules
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:518** (1 rules)
- Condition: Most recent 2yrs signed tax returns, including all applicable schedules/tax transcripts not provided
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:520** (1 rules)
- Condition: Qualifying income used the amount calculated by Income Calculator, addt'l lender req's were not met
- What's needed: income-calculation worksheet/tool output — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:521** (1 rules)
- Condition: Self-employed income calculated incorrectly and the optional Income Calculator tool was not used
- What's needed: income-calculation worksheet/tool output — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:522** (1 rules)
- Condition: The Income Calculator was used, and qualifying income exceeded the amount calculated by the tool
- What's needed: income-calculation worksheet/tool output — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:523** (1 rules)
- Condition: The self-employment income was not calculated correctly
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:524** (1 rules)
- Condition: Underwriter did not provide a written analysis of the applicant's individual tax returns
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:525** (1 rules)
- Condition: Where the Income Calculator was used, the Income Calculator findings report was not in the file
- What's needed: income-calculation worksheet/tool output — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:527** (1 rules)
- Condition: 2 yrs business returns not in file & SE income not increasing, business assets used &/or is CO refi
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:528** (1 rules)
- Condition: 2 yrs business tax return with applicable schedules not in file as req'd
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:530** (1 rules)
- Condition: Additional business income for self-employed borr considered without written analysis to justify
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:531** (1 rules)
- Condition: An analysis establishing stability of income over the previous 2 years was not completed
- What's needed: self-employed income-analysis form (Form 91/1084/1088) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:532** (1 rules)
- Condition: Borr considered self-employ owns >25% w/out analysis stable/likely to cont
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:533** (1 rules)
- Condition: Complete tax returns for the most recent two years, including all schedules were not obtained
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:535** (1 rules)
- Condition: The UW did not analyze the tax returns to determine the borrower’s gross self-employment income
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:536** (1 rules)
- Condition: The borrower's self-employment income does not meet the income history requirements
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:537** (1 rules)
- Condition: The self-employment income history did not meet HUD's two-year requirement for effective income
- What's needed: income-type-specific source fields (not yet in FIELD_SPECS)
- Machine-checkable: -

**income-verification:540** (1 rules)
- Condition: Assets used included unallowable retirement accounts/pensions/Keogh accounts
- What's needed: retirement-account statement (401(k)/IRA/Keogh/pension) — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:541** (1 rules)
- Condition: File missing a disability benefits statement verifying the payment amount and payment frequency
- What's needed: disability-benefits payer statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:543** (1 rules)
- Condition: SSI used as repayment income was not documented to continue for at least 3 years into the mortgage
- What's needed: disability-benefits payer statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:544** (1 rules)
- Condition: The lender did not obtain documentation from the source verifying the retirement income
- What's needed: disability-benefits payer statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:545** (1 rules)
- Condition: 1-year history of receipt not documented for trust income with pre-determined fixed payment amounts
- What's needed: trust agreement/trustee statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:546** (1 rules)
- Condition: 2-year history of receipt not documented for trust income based on historical fluctuating payments
- What's needed: trust agreement/trustee statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:548** (1 rules)
- Condition: Missing Trust Agreement or trustee statement confirming amount, frequency, and 3 yrs continuance
- What's needed: trust agreement/trustee statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:550** (1 rules)
- Condition: Pre-determined fixed payment trust income did not meet all doc requirements
- What's needed: trust agreement/trustee statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:551** (1 rules)
- Condition: Trust agreement/trustee's stmt confirming the amount, frequency & duration of payments not provided
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:552** (1 rules)
- Condition: Employment-related assets were liquidated to a trust w/in 1 yr of application & did not meet req's
- What's needed: trust agreement/trustee statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:555** (1 rules)
- Condition: The trust verification documentation did not clearly identify the date the trust was created
- What's needed: trust agreement/trustee statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:556** (1 rules)
- Condition: The variable trust payment income was not calculated correctly
- What's needed: trust agreement/trustee statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:557** (1 rules)
- Condition: Trust agmt/trustee stmt/trust tax returns confirming amt, frequency & income type rec'd not provided
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:558** (1 rules)
- Condition: Trust income is a fixed payment from a depleting asset without documenting 3 years of continuance
- What's needed: trust agreement/trustee statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:559** (1 rules)
- Condition: Trust income pymts are fixed & 12 mos of receipt not documented & did not meet other conditions
- What's needed: trust agreement/trustee statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:560** (1 rules)
- Condition: Trust income pymts are variable & a 24 mos history of receipt not documented with 2 yrs tax returns
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:561** (1 rules)
- Condition: Variable trust income rec'd at least 1 yr but less than 2 yrs used w/out offsetting positive factors
- What's needed: trust agreement/trustee statement — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:563** (1 rules)
- Condition: Unemployment income used w/out 2 yrs signed tax returns documenting consistent receipt or as per DU
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:564** (1 rules)
- Condition: Unemployment income used was not clearly associated with seasonal income as per the tax returns
- What's needed: personal/business tax return or IRS transcript — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:565** (1 rules)
- Condition: A VVOE was not obtained or was not dated within 10 business days of the note date
- What's needed: verbal VOE (VVOE) call/database log — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:566** (1 rules)
- Condition: Alternative VOE method employer email did not include all required information
- What's needed: verbal VOE (VVOE) call/database log — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:567** (1 rules)
- Condition: File did not confirm the employer email address is accurate for an alternative VOE method
- What's needed: verbal VOE (VVOE) call/database log — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:570** (1 rules)
- Condition: The verbal verification of employment does not show borrower in an active status
- What's needed: a VVOE (verbal verification of employment) log/status fact — not currently modeled; the corpus has a written/signed VOE (loan 01) but no distinct verbal-VOE artifact with an active/inactive status field
- Machine-checkable: -

**income-verification:571** (1 rules)
- Condition: Third-party vendor database data used to obtain the VVOE was older than 35 days of the note date
- What's needed: verbal VOE (VVOE) call/database log — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: threshold/date comparison once the field exists

**income-verification:572** (1 rules)
- Condition: VVOE alt bank stmnts not within 15 business days before the note &/or do not contain all req'd info
- What's needed: verbal VOE (VVOE) call/database log — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:573** (1 rules)
- Condition: VVOE alt paystub not within 15 business days before the note &/or does not contain all req'd info
- What's needed: verbal VOE (VVOE) call/database log — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:574** (1 rules)
- Condition: VVOE not obtained or not dated within 120 calendar days of the note date for self-employed income
- What's needed: verbal VOE (VVOE) call/database log — not among the doc/field types the 5-loan synthetic corpus extracts today
- Machine-checkable: -

**income-verification:575** (1 rules)
- Condition: Vendor for 3rd party VOE was not Equifax/TWN or manual process not followed
- What's needed: a VOE-vendor-name field (e.g. Equifax/The Work Number) — not currently captured from any document
- Machine-checkable: -

**income-verification:577** (1 rules)
- Condition: The verbal verification of employment does not show borrower in an active status
- What's needed: a VVOE (verbal verification of employment) log/status fact — not currently modeled; the corpus has a written/signed VOE (loan 01) but no distinct verbal-VOE artifact with an active/inactive status field
- Machine-checkable: -

**income-verification:578** (1 rules)
- Condition: Vendor for 3rd party VOE was not Equifax/TWN or manual process not followed
- What's needed: a VOE-vendor-name field (e.g. Equifax/The Work Number) — not currently captured from any document
- Machine-checkable: -

**underwriting-review:1** (1 rules)
- Condition: LDP/GSA lists and SAM were not checked and/or determination not noted on form HUD-92900-LT
- What's needed: caivrs doc type already exists in DOC_TYPES and is present for loan 02 only (05_CAIVRS_LDP_GSA.pdf) but has zero FIELD_SPECS/FACT_SPECS entries -- no 'clear'/'hit' fact is extracted from it, and no loan 01/03/04/05 has this document at all
- Machine-checkable: -

**underwriting-review:2** (1 rules)
- Condition: One or more of the interested parties appeared on the GSA list
- What's needed: caivrs doc type already exists in DOC_TYPES and is present for loan 02 only (05_CAIVRS_LDP_GSA.pdf) but has zero FIELD_SPECS/FACT_SPECS entries -- no 'clear'/'hit' fact is extracted from it, and no loan 01/03/04/05 has this document at all
- Machine-checkable: -

**underwriting-review:3** (1 rules)
- Condition: One or more of the interested parties appeared on the LDP list
- What's needed: caivrs doc type already exists in DOC_TYPES and is present for loan 02 only (05_CAIVRS_LDP_GSA.pdf) but has zero FIELD_SPECS/FACT_SPECS entries -- no 'clear'/'hit' fact is extracted from it, and no loan 01/03/04/05 has this document at all
- Machine-checkable: -

**underwriting-review:4** (1 rules)
- Condition: Required parties per their specific role in the loan not checked against the FHLMC Exclusionary List
- What's needed: caivrs doc type already exists in DOC_TYPES and is present for loan 02 only (05_CAIVRS_LDP_GSA.pdf) but has zero FIELD_SPECS/FACT_SPECS entries -- no 'clear'/'hit' fact is extracted from it, and no loan 01/03/04/05 has this document at all
- Machine-checkable: -

**underwriting-review:5** (1 rules)
- Condition: The CAIVRS was not examined to determine whether any party to the transaction appears on either list
- What's needed: caivrs doc type already exists in DOC_TYPES and is present for loan 02 only (05_CAIVRS_LDP_GSA.pdf) but has zero FIELD_SPECS/FACT_SPECS entries -- no 'clear'/'hit' fact is extracted from it, and no loan 01/03/04/05 has this document at all
- Machine-checkable: -

**underwriting-review:6** (1 rules)
- Condition: The approving underwriter was not Direct Endorsement (DE) certified
- What's needed: caivrs doc type already exists in DOC_TYPES and is present for loan 02 only (05_CAIVRS_LDP_GSA.pdf) but has zero FIELD_SPECS/FACT_SPECS entries -- no 'clear'/'hit' fact is extracted from it, and no loan 01/03/04/05 has this document at all
- Machine-checkable: -

**underwriting-review:8** (1 rules)
- Condition: Cash to close on the final AUS doesn't match final 1003 or 1008
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:10** (1 rules)
- Condition: The property type on the final AUS does not match the property type listed on the appraisal
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:19** (1 rules)
- Condition: Condition for second job documentation when no second job applicable was not cleared
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:20** (1 rules)
- Condition: Secured funds were not entered correctly into DU and/or they were not identified separately
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:21** (1 rules)
- Condition: The declarations indicate borrower is a co-signor on a debt and unable to confirm this was addressed
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:23** (1 rules)
- Condition: All req's where the subject is being resold between 91 -180 days after the last acquisition not met
- What's needed: prior-acquisition/resale date fields (seller's acquisition date vs resale date) -- not modeled; no purchase-contract or prior-deed document exists in the corpus
- Machine-checkable: -

**underwriting-review:27** (1 rules)
- Condition: The subject property is being resold within 90 days of the seller's acquisition
- What's needed: seller's acquisition date vs resale date (90-day window) -- not modeled
- Machine-checkable: -

**underwriting-review:29** (1 rules)
- Condition: The appraiser name and/or license # field is incomplete or incorrect
- What's needed: 1008/1077 Uniform Underwriting and Transmittal Summary -- no such document/field exists for any agency in this pilot
- Machine-checkable: -

**underwriting-review:30** (1 rules)
- Condition: The final 1008 is incorrect or incomplete
- What's needed: 1008/1077 Uniform Underwriting and Transmittal Summary -- no such document/field exists for any agency in this pilot
- Machine-checkable: -

**underwriting-review:34** (1 rules)
- Condition: Notice of adverse action/commitment with new terms not found or incorrect
- What's needed: adverse-action/incompleteness notice + its mailing/received dates -- not in corpus
- Machine-checkable: -

**underwriting-review:35** (1 rules)
- Condition: Supplemental decision screen is missing rationale, discussion details and/or date/time stamps
- What's needed: AUS supplemental-decision-screen rationale/timestamp fields -- ties to the AUS-findings gap (no DU/LPA/GUS export exists in this pilot)
- Machine-checkable: -

**underwriting-review:36** (1 rules)
- Condition: DU Verifications/Conditions not met for income, assets, credit, &/or level of property fieldwork
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:37** (1 rules)
- Condition: Final complete DU UW Findings report &/or final UW Analysis report produced by DU not in the file
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:39** (1 rules)
- Condition: Accept/Ineligible-loan approved without clearing ineligibility issues or document the approval basis
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:40** (1 rules)
- Condition: All of the data elements entered in the AUS were not correct
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:41** (1 rules)
- Condition: DU Accept however, conditions exist for a downgrade but the loan was not manually underwritten
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:43** (1 rules)
- Condition: The Section 8 Housing Choice Voucher amount was deducted and is not paid directly to the servicer
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:44** (1 rules)
- Condition: The abated real estate tax amount was used without meeting documentation & continuance requirements
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:45** (1 rules)
- Condition: The monthly PITIA did not include all of the applicable housing components
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:47** (1 rules)
- Condition: In a Refer w/ Caution the UW did not follow suggested steps to resubmit or manually UW the loan
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:49** (1 rules)
- Condition: The loan was not manually UW when DU recommendation was "out of scope"
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:50** (1 rules)
- Condition: A Notice of Incompleteness (NOI) was not mailed within 30 days of the application date
- What's needed: adverse-action/incompleteness notice + its mailing/received dates -- not in corpus
- Machine-checkable: -

**underwriting-review:52** (1 rules)
- Condition: Applicant was not notified of action taken within 30 days after receiving a completed application
- What's needed: adverse-action/incompleteness notice + its mailing/received dates -- not in corpus
- Machine-checkable: -

**underwriting-review:53** (1 rules)
- Condition: ECOA notice missing reasons for action or disclosure of right to specific reasons within 30 days
- What's needed: adverse-action/incompleteness notice + its mailing/received dates -- not in corpus
- Machine-checkable: -

**underwriting-review:62** (1 rules)
- Condition: 2nd home or investment property not underwritten with DU &/or not an Approve/Eligible recommendation
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:63** (1 rules)
- Condition: 2nd home/investment not DU UW & not a high LTV refi w/ SFC 840 manual UW Alt Qualification Path
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:64** (1 rules)
- Condition: Automated UW case identifier did not include DU casefile ID in a second home or investment property
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:73** (1 rules)
- Condition: Accept/Eligible status but the loan did not meet all RHS-guarantee requirements
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:74** (1 rules)
- Condition: Accept/Ineligible decision approved without resolving the ineligibility issue & resubmitting to GUS
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:75** (1 rules)
- Condition: Adverse credit omitted rec'd Accept w/out explanation to support omission
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:76** (1 rules)
- Condition: Obligations disclosed by the borr not considered in DTI not listed in GUS & "omitted" as permitted
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:77** (1 rules)
- Condition: Refer w/ Caution was not manually UW &/or no approval compensating factors noted
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:78** (1 rules)
- Condition: The final GUS submission is not in the loan file
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:79** (1 rules)
- Condition: There was a material change in data & the loan was not resubmitted for an updated evaluation
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:81** (1 rules)
- Condition: LTV limit exceeded in a loan with a non-occupying co-borrower as per relationship &/or property type
- What's needed: loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; appraised_value already is)
- Machine-checkable: -

**underwriting-review:83** (1 rules)
- Condition: LTV ratio exceeds the maximum FHA mortgage amount that the applicant is eligible for
- What's needed: loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; appraised_value already is)
- Machine-checkable: -

**underwriting-review:85** (1 rules)
- Condition: The LTV limitation was exceeded based on the borrower's credit score
- What's needed: loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; appraised_value already is)
- Machine-checkable: -

**underwriting-review:86** (1 rules)
- Condition: LTV/TLTV/HTLTV calculated incorrect or info in LPA to calculate is wrong
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:87** (1 rules)
- Condition: The UW allowed the LTV ratio and total LTV ratio to be higher than Freddie Mac’s maximum
- What's needed: loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; appraised_value already is)
- Machine-checkable: -

**underwriting-review:91** (1 rules)
- Condition: All LPA Feedback messages were not resolved and/or documented
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:92** (1 rules)
- Condition: All of the data elements entered in the AUS were not correct
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:93** (1 rules)
- Condition: Borr has multiple loans in process & each doesn't have a separate application & different key number
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:94** (1 rules)
- Condition: Homeownership education req's not met for non-traditional credit borr's or purchase w/ LTV above 95%
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:95** (1 rules)
- Condition: Identifying info not entered in LPA correctly such as name, addresses, SS#, subject property, etc
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:96** (1 rules)
- Condition: Income, assets, debts, or loan amount changed beyond LPA allowable tolerances without resubmission
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:97** (1 rules)
- Condition: The 1008/1077 or similar document was incomplete, incorrect or not in the LPA underwritten file
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:98** (1 rules)
- Condition: The loan was resubmitted to LPA with the original key number that was removed by Freddie Mac
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:99** (1 rules)
- Condition: The key number from a previously closed loan was re-used to process or originate another mortgage
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:101** (1 rules)
- Condition: The minimum decision credit score (MDCS) utilized was incorrect and/or was less than 500
- What's needed: a credit_score field on credit_report (credit_report doc exists in every loan; no score field is extracted today -- only individual tradelines)
- Machine-checkable: -

**underwriting-review:102** (1 rules)
- Condition: The minimum decision credit score was not at least 580 to be eligible for maximum financing
- What's needed: a credit_score field on credit_report (credit_report doc exists in every loan; no score field is extracted today -- only individual tradelines)
- Machine-checkable: -

**underwriting-review:106** (1 rules)
- Condition: The PITIA housing ratio was calculated incorrectly and/or exceeded 34% of the repayment income
- What's needed: a general DTI/PITI(A) derivation from urla_liabilities/tradelines + income fields (piti_ratio/dti_ratio today are extracted ONLY from usda_ratio_waiver_doc, present for loan 05/USDA only)
- Machine-checkable: -

**underwriting-review:115** (1 rules)
- Condition: An encroachment was identified on the subject or neighboring property without an easement
- What's needed: specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- Machine-checkable: -

**underwriting-review:116** (1 rules)
- Condition: At least one borrower obligated on the Note was not on the title
- What's needed: specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- Machine-checkable: -

**underwriting-review:117** (1 rules)
- Condition: Exceptions were discovered during the title search not covered by the General Waiver
- What's needed: title-exception-vs-NOV cross-reference fields -- not modeled
- Machine-checkable: -

**underwriting-review:119** (1 rules)
- Condition: Per title, property not free of all liens other than the subject & 2nd liens permitted by FHA
- What's needed: specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- Machine-checkable: -

**underwriting-review:120** (1 rules)
- Condition: The lender required title insurance, however, all applicable requirements not met
- What's needed: specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- Machine-checkable: -

**underwriting-review:121** (2 rules)
- Condition: The loan amount, vesting, proposed insured or other "Red Flags" have not been addressed
- What's needed: specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- Machine-checkable: -

**underwriting-review:122** (2 rules)
- Condition: The title effective date is not within 90-days of the closing date or 180 days for new construction
- What's needed: a title-commitment effective_date field (title_commitment doc exists in loan 01; only title_vesting_commitment is currently extracted from it)
- Machine-checkable: -

**underwriting-review:124** (1 rules)
- Condition: Title has conditions/limitations not on NOV or considered by the appraiser or VA if prior to closing
- What's needed: title-exception-vs-NOV cross-reference fields -- not modeled
- Machine-checkable: -

**underwriting-review:126** (1 rules)
- Condition: All Title insurance and title requirements have not been met
- What's needed: specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- Machine-checkable: -

**underwriting-review:127** (1 rules)
- Condition: Attny Opinion Letter not prepared by acceptable attny &/or had exceptions not reviewed and resolved
- What's needed: specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- Machine-checkable: -

**underwriting-review:128** (1 rules)
- Condition: Lender not in 1st lien position or Jr lien exists w/out all req's being met
- What's needed: a first-lien-position fact on title_commitment (doc exists in loan 01 only; no such field/fact exists today)
- Machine-checkable: -

**underwriting-review:129** (1 rules)
- Condition: The loan amount, vesting, proposed insured or other "Red Flags" have not been addressed
- What's needed: specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- Machine-checkable: -

**underwriting-review:130** (1 rules)
- Condition: The title effective date is not within 90-days of the closing date or 180 days for new construction
- What's needed: a title-commitment effective_date field (title_commitment doc exists in loan 01; only title_vesting_commitment is currently extracted from it)
- Machine-checkable: -

**underwriting-review:131** (1 rules)
- Condition: Title policy amount of protection, insured party is incorrect &/or was written on an incorrect form
- What's needed: specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- Machine-checkable: -

**underwriting-review:132** (1 rules)
- Condition: Title policy did not provide marketable title &/or had title exceptions not reviewed and resolved
- What's needed: specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- Machine-checkable: -

**underwriting-review:134** (1 rules)
- Condition: An encroachment was identified on the subject or neighboring property without an easement
- What's needed: specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- Machine-checkable: -

**underwriting-review:135** (1 rules)
- Condition: Final TP, applicable endorsements or an attny's title opinion/certificate meeting req's not in file
- What's needed: specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- Machine-checkable: -

**underwriting-review:136** (1 rules)
- Condition: The loan amount, vesting, proposed insured or other "Red Flags" have not been addressed
- What's needed: specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- Machine-checkable: -

**underwriting-review:137** (1 rules)
- Condition: The title effective date is not within 90-days of the closing date or 180 days for new construction
- What's needed: a title-commitment effective_date field (title_commitment doc exists in loan 01; only title_vesting_commitment is currently extracted from it)
- Machine-checkable: -

**underwriting-review:138** (1 rules)
- Condition: The transfer of title is outside of company guidelines and not properly explained
- What's needed: specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- Machine-checkable: -

**underwriting-review:140** (1 rules)
- Condition: Title policy amount of protection, insured party is incorrect &/or was written on an incorrect form
- What's needed: specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- Machine-checkable: -

**underwriting-review:142** (1 rules)
- Condition: Attorney not insured against malpractice in giving opinions of title in an amt common for the area
- What's needed: specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- Machine-checkable: -

**underwriting-review:143** (1 rules)
- Condition: Attorney title opinion letter did not provide gap coverage between closing & recordation of the mtg
- What's needed: specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- Machine-checkable: -

**underwriting-review:144** (1 rules)
- Condition: Attorney title opinion letter did not state property is acceptable & mtg is a fee simple 1st lien
- What's needed: specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- Machine-checkable: -

**underwriting-review:145** (1 rules)
- Condition: Attorney title opinion letter was not addressed to the lender and all successors
- What's needed: specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- Machine-checkable: -

**underwriting-review:146** (1 rules)
- Condition: No, the file does not reflect evidence of acceptable title insurance
- What's needed: specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- Machine-checkable: -

**underwriting-review:148** (1 rules)
- Condition: Schedule B -  title requirements found that have not been appropriately addressed and/or cleared
- What's needed: specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- Machine-checkable: -

**underwriting-review:149** (1 rules)
- Condition: The attorney issuing the title opinion letter was not licensed where the subject property is located
- What's needed: specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- Machine-checkable: -

**underwriting-review:150** (1 rules)
- Condition: The attorney title opinion letter did not list all other liens and state they are subordinate
- What's needed: specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- Machine-checkable: -

**underwriting-review:151** (1 rules)
- Condition: The loan amount, vesting, proposed insured or other "Red Flags" have not been addressed
- What's needed: specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- Machine-checkable: -

**underwriting-review:152** (1 rules)
- Condition: The title effective date is not within 90-days of the closing date or 180 days for new construction
- What's needed: a title-commitment effective_date field (title_commitment doc exists in loan 01; only title_vesting_commitment is currently extracted from it)
- Machine-checkable: -

**underwriting-review:153** (1 rules)
- Condition: The transfer of title is outside of company guidelines and not properly explained
- What's needed: specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- Machine-checkable: -

**underwriting-review:154** (1 rules)
- Condition: Title insurer/reinsurer not approved &/or licensed to issue insurance in the subject property state
- What's needed: specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- Machine-checkable: -

**underwriting-review:155** (1 rules)
- Condition: Title revealed exceptions or impediments without all specific eligibility requirements being met
- What's needed: specific title-defect fields (exceptions, endorsements, attorney-opinion-letter details, encroachment survey) -- title_commitment doc exists in loan 01 only, and none of these specific sub-facts are in FIELD_SPECS
- Machine-checkable: -

**underwriting-review:156** (1 rules)
- Condition: Manual VA UW did not sign Form 26-6393 (Aug. 2022), which closed on a non-supervised automatic basis
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:168** (1 rules)
- Condition: The Certificate of Eligibility had conditions to receive a guaranty that were not met
- What's needed: COE entitlement-amount + guaranty-calculation fields (va_coe doc exists for loan 03 but only doc-presence is checked today, no entitlement-amount field is extracted)
- Machine-checkable: -

**underwriting-review:170** (1 rules)
- Condition: The current Cert of Eligibility is insufficient to allow for max 25% guaranty
- What's needed: COE entitlement-amount + guaranty-calculation fields (va_coe doc exists for loan 03 but only doc-presence is checked today, no entitlement-amount field is extracted)
- Machine-checkable: -

**underwriting-review:173** (1 rules)
- Condition: Account with 30 day late payment in 12 months evident; 5% of the balance not included in DTI
- What's needed: a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- Machine-checkable: -

**underwriting-review:174** (1 rules)
- Condition: Business debt on personal credit report omitted w/out evidence debt is paid through a business acct
- What's needed: a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- Machine-checkable: -

**underwriting-review:175** (1 rules)
- Condition: Contingent liability without evidence another obligor has made payments for the last 12 months
- What's needed: a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- Machine-checkable: -

**underwriting-review:176** (1 rules)
- Condition: Federal and/or State income tax repayment plan payments were not included in the monthly debt
- What's needed: a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- Machine-checkable: -

**underwriting-review:177** (1 rules)
- Condition: Installment accounts with more than 10 months remaining was not included in the DTI
- What's needed: a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- Machine-checkable: -

**underwriting-review:178** (1 rules)
- Condition: Judgment pymt w/ more than 10 pymts left not included with significant impact on mtg repayment
- What's needed: a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- Machine-checkable: -

**underwriting-review:179** (1 rules)
- Condition: Lease payments not included in the DTI regardless of months remaining to pay on the contract
- What's needed: a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- Machine-checkable: -

**underwriting-review:180** (1 rules)
- Condition: Short-term obligation was not included in DTI that will have a significant impact ability to repay
- What's needed: a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- Machine-checkable: -

**underwriting-review:181** (1 rules)
- Condition: The full monthly debt of the automobile or expense allowance was not included in the DTI
- What's needed: a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- Machine-checkable: -

**underwriting-review:182** (1 rules)
- Condition: There is a balloon/deferred payment due in the next 24 mos. that was not included in the DTI
- What's needed: a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- Machine-checkable: -

**underwriting-review:184** (1 rules)
- Condition: A material change occurred or was discovered and the loan was not resubmitted to the AUS
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:191** (1 rules)
- Condition: Accept decision but lender did not submit the abbreviated loan app with the required documentation
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:193** (1 rules)
- Condition: Manual UW approval or final GUS Underwriting Analysis is not in the file as applicable
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:195** (1 rules)
- Condition: The lender did not submit a complete loan application containing the required documentation
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:200** (1 rules)
- Condition: Active duty borr provided receipt of Purple Heart prior to/at closing & stat funding fee not waived
- What's needed: VA funding-fee / FHA MIP calculation fields (percentage tables, exemption status, loan amount) -- not extracted
- Machine-checkable: -

**underwriting-review:203** (1 rules)
- Condition: Borr is surviving spouse of Vet who died from a service disability & stat funding fee not waived
- What's needed: VA funding-fee / FHA MIP calculation fields (percentage tables, exemption status, loan amount) -- not extracted
- Machine-checkable: -

**underwriting-review:204** (1 rules)
- Condition: Borr owns another property without validating RHS loan will be primary
- What's needed: an occupancy-intent certification / military-orders / lease-review fact -- not currently modeled (no occupancy-related field or fact exists in FIELD_SPECS/FACT_SPECS)
- Machine-checkable: -

**underwriting-review:206** (1 rules)
- Condition: No GSA/SAM check evidence or GUS date found before commitment or 30 days pre-closing
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:210** (1 rules)
- Condition: The file does not document that the applicant intends to occupy the subject as their primary home
- What's needed: an occupancy-intent certification / military-orders / lease-review fact -- not currently modeled (no occupancy-related field or fact exists in FIELD_SPECS/FACT_SPECS)
- Machine-checkable: -

**underwriting-review:211** (1 rules)
- Condition: The number of household members was not certified by entering the number in GUS
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:212** (1 rules)
- Condition: The potentially exempt Vet was advised to finance the funding fee resulting in cashback
- What's needed: VA funding-fee / FHA MIP calculation fields (percentage tables, exemption status, loan amount) -- not extracted
- Machine-checkable: -

**underwriting-review:214** (1 rules)
- Condition: Vet gets disability or would be entitled retirement/active svc pay & stat funding fee not waived
- What's needed: VA funding-fee / FHA MIP calculation fields (percentage tables, exemption status, loan amount) -- not extracted
- Machine-checkable: -

**underwriting-review:221** (1 rules)
- Condition: The cosigner on the transaction did not sign the Note
- What's needed: co-signer/guarantor/non-occupying-borrower structured data (URLA parties exist as free text; no field distinguishes borrower role/occupancy intent)
- Machine-checkable: -

**underwriting-review:225** (1 rules)
- Condition: GSA List & CAIVRS not checked to determine applicant & other req'd parties eligibility
- What's needed: caivrs doc type already exists in DOC_TYPES and is present for loan 02 only (05_CAIVRS_LDP_GSA.pdf) but has zero FIELD_SPECS/FACT_SPECS entries -- no 'clear'/'hit' fact is extracted from it, and no loan 01/03/04/05 has this document at all
- Machine-checkable: -

**underwriting-review:228** (1 rules)
- Condition: ID # on the Credit report does not match the AUS report or EPIC screen
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:232** (1 rules)
- Condition: No evidence all internal participants involved in the mtg were checked against the GSA and LDP lists
- What's needed: caivrs doc type already exists in DOC_TYPES and is present for loan 02 only (05_CAIVRS_LDP_GSA.pdf) but has zero FIELD_SPECS/FACT_SPECS entries -- no 'clear'/'hit' fact is extracted from it, and no loan 01/03/04/05 has this document at all
- Machine-checkable: -

**underwriting-review:233** (1 rules)
- Condition: Property address submitted to DU does not match other documentation in the loan file
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:236** (1 rules)
- Condition: All eligibility requirements were not met for a non-streamlined refinance
- What's needed: RHS refinance-eligibility facts (existing-loan closing date, borrower-retention, rate comparison) -- not modeled; loan 04 is the pilot's only refi loan and it's a conventional cash-out, not an RHS streamline
- Machine-checkable: -

**underwriting-review:237** (1 rules)
- Condition: All eligibility requirements were not met for a streamlined refinance
- What's needed: RHS refinance-eligibility facts (existing-loan closing date, borrower-retention, rate comparison) -- not modeled; loan 04 is the pilot's only refi loan and it's a conventional cash-out, not an RHS streamline
- Machine-checkable: -

**underwriting-review:238** (1 rules)
- Condition: All the borrowers on the RHS refi of an RD Guaranteed loan to a Streamline-Assist were not retained
- What's needed: RHS refinance-eligibility facts (existing-loan closing date, borrower-retention, rate comparison) -- not modeled; loan 04 is the pilot's only refi loan and it's a conventional cash-out, not an RHS streamline
- Machine-checkable: -

**underwriting-review:239** (1 rules)
- Condition: Borr has a direct USDA loan, Statement of Loan Balance letter not obtained
- What's needed: RHS refinance-eligibility facts (existing-loan closing date, borrower-retention, rate comparison) -- not modeled; loan 04 is the pilot's only refi loan and it's a conventional cash-out, not an RHS streamline
- Machine-checkable: -

**underwriting-review:242** (1 rules)
- Condition: Interest rate not fixed and/or is higher than rate of loan being refinanced
- What's needed: RHS refinance-eligibility facts (existing-loan closing date, borrower-retention, rate comparison) -- not modeled; loan 04 is the pilot's only refi loan and it's a conventional cash-out, not an RHS streamline
- Machine-checkable: -

**underwriting-review:243** (1 rules)
- Condition: RHS refi of an RD Guaranteed loan-at least 1 of the borr's is not on the RD loan being refinanced
- What's needed: RHS refinance-eligibility facts (existing-loan closing date, borrower-retention, rate comparison) -- not modeled; loan 04 is the pilot's only refi loan and it's a conventional cash-out, not an RHS streamline
- Machine-checkable: -

**underwriting-review:244** (1 rules)
- Condition: Streamlined-Assist Refi - the transaction does not meet the eligibility requirements
- What's needed: RHS refinance-eligibility facts (existing-loan closing date, borrower-retention, rate comparison) -- not modeled; loan 04 is the pilot's only refi loan and it's a conventional cash-out, not an RHS streamline
- Machine-checkable: -

**underwriting-review:245** (1 rules)
- Condition: The refinance did not have a permissible purpose
- What's needed: RHS refinance-eligibility facts (existing-loan closing date, borrower-retention, rate comparison) -- not modeled; loan 04 is the pilot's only refi loan and it's a conventional cash-out, not an RHS streamline
- Machine-checkable: -

**underwriting-review:246** (1 rules)
- Condition: Unpaid fees, past-due interest & late fees/penalties included in new streamlined refi loan amount
- What's needed: RHS refinance-eligibility facts (existing-loan closing date, borrower-retention, rate comparison) -- not modeled; loan 04 is the pilot's only refi loan and it's a conventional cash-out, not an RHS streamline
- Machine-checkable: -

**underwriting-review:248** (1 rules)
- Condition: Borr down pymts, even if sales price exceeds reasonable value, not included in percentage down calc
- What's needed: VA down-payment/percentage-down calculation fields -- loan_amount and a stated-down-payment field are not currently extracted
- Machine-checkable: -

**underwriting-review:249** (1 rules)
- Condition: Construction loan equity in the property not used as a down payment for calculating the funding fee
- What's needed: VA funding-fee / FHA MIP calculation fields (percentage tables, exemption status, loan amount) -- not extracted
- Machine-checkable: -

**underwriting-review:250** (1 rules)
- Condition: Fees, charges or discount pts included in loan amount unallowable or not w/in limits per loan type
- What's needed: VA allowable-fee-limit table + loan_amount field -- neither exists today
- Machine-checkable: -

**underwriting-review:251** (1 rules)
- Condition: Funding fee exemption status was not established prior to closing
- What's needed: VA funding-fee / FHA MIP calculation fields (percentage tables, exemption status, loan amount) -- not extracted
- Machine-checkable: -

**underwriting-review:252** (1 rules)
- Condition: Funding fee incorrect due to the wrong percentage selected from the funding fee percentage table
- What's needed: VA funding-fee / FHA MIP calculation fields (percentage tables, exemption status, loan amount) -- not extracted
- Machine-checkable: -

**underwriting-review:253** (1 rules)
- Condition: Funding fee was not charged without verifying exempt status
- What's needed: VA funding-fee / FHA MIP calculation fields (percentage tables, exemption status, loan amount) -- not extracted
- Machine-checkable: -

**underwriting-review:254** (1 rules)
- Condition: Int rate increase over 1% & not re-uw &/or a new or corrected 1003 not completed, initialed & dated
- What's needed: interest-rate-at-application vs interest-rate-at-closing + re-underwrite tracking -- mismo_note_rate is extracted but no 'as originally submitted' comparison point exists
- Machine-checkable: -

**underwriting-review:256** (1 rules)
- Condition: Purchase/construction at least 5% down & percentage not included in total price or construction cost
- What's needed: VA down-payment-percentage calculation fields -- same gap as G248
- Machine-checkable: -

**underwriting-review:257** (1 rules)
- Condition: The funding fee was calculated incorrectly
- What's needed: VA funding-fee / FHA MIP calculation fields (percentage tables, exemption status, loan amount) -- not extracted
- Machine-checkable: -

**underwriting-review:258** (1 rules)
- Condition: The sales concessions exceeded 4% of the established reasonable value of the property
- What's needed: NOV reasonable-value field + sales-concessions field (4% threshold) -- va_nov doc exists (loan 03) with nov_issue_date extracted, but no reasonable-value or concessions-amount field
- Machine-checkable: -

**underwriting-review:261** (1 rules)
- Condition: MI ineligibility was not corrected to clear FHAC case warning/resubmission of file did not occur
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:262** (1 rules)
- Condition: The file does not contain the required evidence of the final underwriting decision
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:263** (1 rules)
- Condition: The final Form HUD-92900-LT, FHA Loan Underwriting and Transmittal Summary not in the file
- What's needed: Form HUD-92900-LT, FHA Loan Underwriting and Transmittal Summary (distinct from the HUD-92900-A Addendum already extracted for loan 02 -- no HUD-92900-LT document exists in any of the 5 loans)
- Machine-checkable: -

**underwriting-review:274** (1 rules)
- Condition: Annual income calculated incorrectly
- What's needed: RHS annual/household-income calculation derivation (income fields are extracted per-borrower on the 1003, but no RHS household-income aggregation/eligible-source-classification logic exists)
- Machine-checkable: -

**underwriting-review:275** (1 rules)
- Condition: Annual income used to qualify not from an eligible source
- What's needed: RHS annual/household-income calculation derivation (income fields are extracted per-borrower on the 1003, but no RHS household-income aggregation/eligible-source-classification logic exists)
- Machine-checkable: -

**underwriting-review:276** (1 rules)
- Condition: Income calculation requirements were not met
- What's needed: RHS annual/household-income calculation derivation (income fields are extracted per-borrower on the 1003, but no RHS household-income aggregation/eligible-source-classification logic exists)
- Machine-checkable: -

**underwriting-review:278** (1 rules)
- Condition: Income considered for student living away, all req's not met or income used exceeded the first $480
- What's needed: RHS annual/household-income calculation derivation (income fields are extracted per-borrower on the 1003, but no RHS household-income aggregation/eligible-source-classification logic exists)
- Machine-checkable: -

**underwriting-review:280** (1 rules)
- Condition: Projected household annual income calculation did not exclude qualified household deductions
- What's needed: RHS annual/household-income calculation derivation (income fields are extracted per-borrower on the 1003, but no RHS household-income aggregation/eligible-source-classification logic exists)
- Machine-checkable: -

**underwriting-review:281** (1 rules)
- Condition: Tax and insurance estimate used as part of the monthly mortgage payment is not accurate
- What's needed: a general DTI/PITI(A) derivation from urla_liabilities/tradelines + income fields (piti_ratio/dti_ratio today are extracted ONLY from usda_ratio_waiver_doc, present for loan 05/USDA only)
- Machine-checkable: -

**underwriting-review:282** (1 rules)
- Condition: The 1008/1077 or other similar document was incomplete, incorrect or not in file
- What's needed: 1008/1077 Uniform Underwriting and Transmittal Summary -- no such document/field exists for any agency in this pilot
- Machine-checkable: -

**underwriting-review:283** (1 rules)
- Condition: The underwriter did not include the eligible income of all adult household members
- What's needed: RHS annual/household-income calculation derivation (income fields are extracted per-borrower on the 1003, but no RHS household-income aggregation/eligible-source-classification logic exists)
- Machine-checkable: -

**underwriting-review:284** (1 rules)
- Condition: Verified changes of income amounts or sources in the ensuing 12 months was not documented
- What's needed: RHS annual/household-income calculation derivation (income fields are extracted per-borrower on the 1003, but no RHS household-income aggregation/eligible-source-classification logic exists)
- Machine-checkable: -

**underwriting-review:286** (1 rules)
- Condition: A CAIVRS screening was not conducted on all obligors on the loan
- What's needed: caivrs doc type already exists in DOC_TYPES and is present for loan 02 only (05_CAIVRS_LDP_GSA.pdf) but has zero FIELD_SPECS/FACT_SPECS entries -- no 'clear'/'hit' fact is extracted from it, and no loan 01/03/04/05 has this document at all
- Machine-checkable: -

**underwriting-review:289** (1 rules)
- Condition: DTI exceeds 41% or residual income is below VA's minimum and the UW did not justify the approval
- What's needed: a general DTI/PITI(A) derivation from urla_liabilities/tradelines + income fields (piti_ratio/dti_ratio today are extracted ONLY from usda_ratio_waiver_doc, present for loan 05/USDA only)
- Machine-checkable: -

**underwriting-review:291** (1 rules)
- Condition: GSA/LDP/VA non-procurement list not checked for excluded program participants
- What's needed: caivrs doc type already exists in DOC_TYPES and is present for loan 02 only (05_CAIVRS_LDP_GSA.pdf) but has zero FIELD_SPECS/FACT_SPECS entries -- no 'clear'/'hit' fact is extracted from it, and no loan 01/03/04/05 has this document at all
- Machine-checkable: -

**underwriting-review:292** (1 rules)
- Condition: Loan $144,000 or less w/ partial entitlement & guaranty not $36,000 minus the unrestored entitlement
- What's needed: VA loan-amount/entitlement/guaranty-calculation fields (loan_amount is not currently extracted at all; entitlement amount is not extracted from va_coe)
- Machine-checkable: -

**underwriting-review:293** (1 rules)
- Condition: Loan not identified as a caution at delivery via the key# for manual UW after an LPA caution
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:294** (1 rules)
- Condition: Loan over $144,000 & max guarantee amt was incorrect per the Blue Water Navy Vietnam Veterans Act
- What's needed: VA loan-amount/entitlement/guaranty-calculation fields (loan_amount is not currently extracted at all; entitlement amount is not extracted from va_coe)
- Machine-checkable: -

**underwriting-review:295** (1 rules)
- Condition: Loan over $144,000, married or joint Vets & max guaranty incorrect based on full/partial entitlement
- What's needed: VA loan-amount/entitlement/guaranty-calculation fields (loan_amount is not currently extracted at all; entitlement amount is not extracted from va_coe)
- Machine-checkable: -

**underwriting-review:296** (1 rules)
- Condition: Loan over $144,000, w/ full entitlement & max amt of guaranty was not 25% of the loan amount
- What's needed: VA loan-amount/entitlement/guaranty-calculation fields (loan_amount is not currently extracted at all; entitlement amount is not extracted from va_coe)
- Machine-checkable: -

**underwriting-review:297** (1 rules)
- Condition: Loan over $144,000, w/ partial entitlement & guaranty not 25% of CLL reduced by used entitlement
- What's needed: VA loan-amount/entitlement/guaranty-calculation fields (loan_amount is not currently extracted at all; entitlement amount is not extracted from va_coe)
- Machine-checkable: -

**underwriting-review:298** (1 rules)
- Condition: No, credit document(s) exceed age requirements as of the actual/scheduled closing date
- What's needed: verification-document source/date-of-receipt fields (VOE/VOD/VOM 'directly from source' + document date vs Note date) -- not modeled
- Machine-checkable: -

**underwriting-review:299** (1 rules)
- Condition: No, source is not clearly identified for faxed credit documentation
- What's needed: verification-document source/date-of-receipt fields (VOE/VOD/VOM 'directly from source' + document date vs Note date) -- not modeled
- Machine-checkable: -

**underwriting-review:300** (1 rules)
- Condition: No, verification document(s) were not delivered directly to/returned from source of verification
- What's needed: verification-document source/date-of-receipt fields (VOE/VOD/VOM 'directly from source' + document date vs Note date) -- not modeled
- Machine-checkable: -

**underwriting-review:301** (1 rules)
- Condition: Not manually UW as per req's for caution loans after being submitted & receiving a Caution from LPA
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:302** (1 rules)
- Condition: The LTV was calculated incorrectly
- What's needed: loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; appraised_value already is)
- Machine-checkable: -

**underwriting-review:305** (1 rules)
- Condition: YTD paystub used to verify income was dated over 30 days before the application received date
- What's needed: a paystub date field (paystub doc type exists in every loan but extract_loan.py has ZERO FIELD_SPECS entries for it today -- verified by reading the file directly)
- Machine-checkable: -

**underwriting-review:307** (1 rules)
- Condition: Manual UW non-occupant & occupying borr 5% down not own funds & LTV >80%/donated funds ineligible
- What's needed: loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; appraised_value already is)
- Machine-checkable: -

**underwriting-review:308** (1 rules)
- Condition: Max LTV, CLTV, HCLTV ratio not met as applicable in a loan with a co-signer or non-occupant borrower
- What's needed: loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; appraised_value already is)
- Machine-checkable: -

**underwriting-review:310** (1 rules)
- Condition: The guarantor or co-signer did not sign the mortgage or deed of trust note
- What's needed: co-signer/guarantor/non-occupying-borrower structured data (URLA parties exist as free text; no field distinguishes borrower role/occupancy intent)
- Machine-checkable: -

**underwriting-review:319** (1 rules)
- Condition: The subject's first lien position was not confirmed
- What's needed: a first-lien-position fact on title_commitment (doc exists in loan 01 only; no such field/fact exists today)
- Machine-checkable: -

**underwriting-review:320** (1 rules)
- Condition: Lender credit was not derived from an increase in the interest rate, or was not funded by the lender
- What's needed: special-assessment / lender-incentive fields on closing_disclosure (doc exists in every loan; these specific line items are not in FIELD_SPECS)
- Machine-checkable: -

**underwriting-review:321** (1 rules)
- Condition: Lender incentive not treated as a sales concession & lender is/affiliated with an interested party
- What's needed: special-assessment / lender-incentive fields on closing_disclosure (doc exists in every loan; these specific line items are not in FIELD_SPECS)
- Machine-checkable: -

**underwriting-review:323** (1 rules)
- Condition: The lender credit was used for a purpose other than as a credit towards the borrower's closing costs
- What's needed: special-assessment / lender-incentive fields on closing_disclosure (doc exists in every loan; these specific line items are not in FIELD_SPECS)
- Machine-checkable: -

**underwriting-review:324** (1 rules)
- Condition: The lender incentive cost or value was funded through the mtg transaction (e.g., premium pricing)
- What's needed: special-assessment / lender-incentive fields on closing_disclosure (doc exists in every loan; these specific line items are not in FIELD_SPECS)
- Machine-checkable: -

**underwriting-review:325** (1 rules)
- Condition: The lender incentive was considered in qualifying (e.g., as a source of funds for closing/reserves)
- What's needed: special-assessment / lender-incentive fields on closing_disclosure (doc exists in every loan; these specific line items are not in FIELD_SPECS)
- Machine-checkable: -

**underwriting-review:326** (1 rules)
- Condition: The mortgage loan included a lender incentive or lender credit that required repayment
- What's needed: special-assessment / lender-incentive fields on closing_disclosure (doc exists in every loan; these specific line items are not in FIELD_SPECS)
- Machine-checkable: -

**underwriting-review:327** (1 rules)
- Condition: Third party funds were used to provide a lender credit
- What's needed: special-assessment / lender-incentive fields on closing_disclosure (doc exists in every loan; these specific line items are not in FIELD_SPECS)
- Machine-checkable: -

**underwriting-review:330** (1 rules)
- Condition: The VA maximum loan amount was exceeded for the loan type
- What's needed: VA loan-amount/entitlement/guaranty-calculation fields (loan_amount is not currently extracted at all; entitlement amount is not extracted from va_coe)
- Machine-checkable: -

**underwriting-review:331** (1 rules)
- Condition: The maximum loan amount was not calculated correctly
- What's needed: VA loan-amount/entitlement/guaranty-calculation fields (loan_amount is not currently extracted at all; entitlement amount is not extracted from va_coe)
- Machine-checkable: -

**underwriting-review:332** (1 rules)
- Condition: Veteran certification that the subject property will be used as their primary residence not in file
- What's needed: an occupancy-intent certification / military-orders / lease-review fact -- not currently modeled (no occupancy-related field or fact exists in FIELD_SPECS/FACT_SPECS)
- Machine-checkable: -

**underwriting-review:334** (1 rules)
- Condition: The mtg did not meet the loan limits based on loan type as outlined by FNMA
- What's needed: the applicable conforming loan limit (by county/loan type) + loan_amount field -- neither is modeled
- Machine-checkable: -

**underwriting-review:336** (1 rules)
- Condition: Loan would have been granted w/out the RHS guarantee at the same rate-terms
- What's needed: RHS loan-term eligibility fields (note rate at closing vs at commitment, amortization term) -- mismo_note_rate is extracted but no 'rate at commitment' comparison point exists
- Machine-checkable: -

**underwriting-review:337** (1 rules)
- Condition: Proposed payment is significantly higher than current housing payment without a repayment analysis
- What's needed: current-housing-payment field + a repayment-analysis document -- neither modeled
- Machine-checkable: presence of a documented repayment analysis (RHS)

**underwriting-review:338** (1 rules)
- Condition: The interest rate increased prior to closing rendering the loan ineligible
- What's needed: RHS loan-term eligibility fields (note rate at closing vs at commitment, amortization term) -- mismo_note_rate is extracted but no 'rate at commitment' comparison point exists
- Machine-checkable: -

**underwriting-review:339** (1 rules)
- Condition: The loan does not have a term of 30 years
- What's needed: RHS loan-term eligibility fields (note rate at closing vs at commitment, amortization term) -- mismo_note_rate is extracted but no 'rate at commitment' comparison point exists
- Machine-checkable: -

**underwriting-review:340** (1 rules)
- Condition: The terms of the loan were ineligible for an RHS guaranteed loan
- What's needed: RHS loan-term eligibility fields (note rate at closing vs at commitment, amortization term) -- mismo_note_rate is extracted but no 'rate at commitment' comparison point exists
- Machine-checkable: -

**underwriting-review:342** (1 rules)
- Condition: Lender did not perform the level of underwriting review appropriate based on the credit score range
- What's needed: a credit_score field on credit_report (credit_report doc exists in every loan; no score field is extracted today -- only individual tradelines)
- Machine-checkable: -

**underwriting-review:343** (1 rules)
- Condition: Manual UW front ratio over 29% & 100% housing pymt increase w/ risk layers & no strong comp factors
- What's needed: a general DTI/PITI(A) derivation from urla_liabilities/tradelines + income fields (piti_ratio/dti_ratio today are extracted ONLY from usda_ratio_waiver_doc, present for loan 05/USDA only)
- Machine-checkable: -

**underwriting-review:344** (1 rules)
- Condition: Manually underwritten and submitted loan without the associated documents being uploaded via GUS
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:345** (1 rules)
- Condition: The 1008/1077 or similar document was incomplete, incorrect or not in the manually underwritten file
- What's needed: 1008/1077 Uniform Underwriting and Transmittal Summary -- no such document/field exists for any agency in this pilot
- Machine-checkable: -

**underwriting-review:350** (1 rules)
- Condition: Loan approved with ratio's exceeding guidelines & compensating factors not noted on the 92900-LT
- What's needed: Form HUD-92900-LT, FHA Loan Underwriting and Transmittal Summary (distinct from the HUD-92900-A Addendum already extracted for loan 02 -- no HUD-92900-LT document exists in any of the 5 loans)
- Machine-checkable: -

**underwriting-review:351** (1 rules)
- Condition: Loan or Borrower data elements changed without the loan being re-underwritten
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:354** (1 rules)
- Condition: The total PITIA/DTI ratios were not calculated correctly
- What's needed: a general DTI/PITI(A) derivation from urla_liabilities/tradelines + income fields (piti_ratio/dti_ratio today are extracted ONLY from usda_ratio_waiver_doc, present for loan 05/USDA only)
- Machine-checkable: -

**underwriting-review:357** (1 rules)
- Condition: The total amount financed exceeded the maximum loan amount limit
- What's needed: VA loan-amount/entitlement/guaranty-calculation fields (loan_amount is not currently extracted at all; entitlement amount is not extracted from va_coe)
- Machine-checkable: -

**underwriting-review:359** (1 rules)
- Condition: The base and/or total loan amount was not calculated correctly
- What's needed: loan_amount + adjusted-value fields (appraised_value is extracted; the loan amount itself and FHA's 'adjusted value' concept are not)
- Machine-checkable: -

**underwriting-review:360** (1 rules)
- Condition: The loan amount exceeds the maximum FHA mortgage amount
- What's needed: VA loan-amount/entitlement/guaranty-calculation fields (loan_amount is not currently extracted at all; entitlement amount is not extracted from va_coe)
- Machine-checkable: -

**underwriting-review:362** (1 rules)
- Condition: Minimum req'd investment (MRI) was not at least 3.5% of the adjusted value in a purchase
- What's needed: loan_amount + adjusted-value fields (appraised_value is extracted; the loan amount itself and FHA's 'adjusted value' concept are not)
- Machine-checkable: -

**underwriting-review:367** (1 rules)
- Condition: CLTV calculated incorrectly
- What's needed: loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; appraised_value already is)
- Machine-checkable: -

**underwriting-review:368** (1 rules)
- Condition: HCLTV calculated incorrectly
- What's needed: loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; appraised_value already is)
- Machine-checkable: -

**underwriting-review:370** (1 rules)
- Condition: The annual MIP was incorrect based on the LTV, term and product type
- What's needed: loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; appraised_value already is)
- Machine-checkable: -

**underwriting-review:371** (1 rules)
- Condition: The upfront mortgage insurance premium (UFMIP) charged was incorrect
- What's needed: VA funding-fee / FHA MIP calculation fields (percentage tables, exemption status, loan amount) -- not extracted
- Machine-checkable: -

**underwriting-review:374** (1 rules)
- Condition: The borrower exceeded the max limit of 2 financed properties including the subject in a HomeReady
- What's needed: a parsed real-estate-owned (REO) schedule entity from the 1003 (the extractor does not yet treat the 1003's REO section as its own entity)
- Machine-checkable: -

**underwriting-review:375** (1 rules)
- Condition: The file did not document sufficient assets to meet the reserve requirement
- What's needed: a parsed real-estate-owned (REO) schedule entity from the 1003 (the extractor does not yet treat the 1003's REO section as its own entity)
- Machine-checkable: -

**underwriting-review:376** (1 rules)
- Condition: The number of financed properties exceeded guidelines
- What's needed: a parsed real-estate-owned (REO) schedule entity from the 1003 (the extractor does not yet treat the 1003's REO section as its own entity)
- Machine-checkable: -

**underwriting-review:377** (1 rules)
- Condition: The subject loan is a second home or investment property & the loan was not DU underwritten
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:382** (1 rules)
- Condition: All borrowers were not individuals for a group home investment property leased to business entities
- What's needed: an occupancy-intent certification / military-orders / lease-review fact -- not currently modeled (no occupancy-related field or fact exists in FIELD_SPECS/FACT_SPECS)
- Machine-checkable: -

**underwriting-review:383** (1 rules)
- Condition: All occupancy eligibility requirements were not met for the occupancy type
- What's needed: an occupancy-intent certification / military-orders / lease-review fact -- not currently modeled (no occupancy-related field or fact exists in FIELD_SPECS/FACT_SPECS)
- Machine-checkable: -

**underwriting-review:384** (1 rules)
- Condition: LTV calculated incorrectly or info put in AUS to calculate LTV incorrect
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:386** (1 rules)
- Condition: The LTV ratio is higher than Fannie Mae’s maximum allowable ratio
- What's needed: loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; appraised_value already is)
- Machine-checkable: -

**underwriting-review:388** (1 rules)
- Condition: Employment, utilities, direct TPV docs do not evidence the subject as the primary in streamline refi
- What's needed: an occupancy-intent certification / military-orders / lease-review fact -- not currently modeled (no occupancy-related field or fact exists in FIELD_SPECS/FACT_SPECS)
- Machine-checkable: -

**underwriting-review:389** (1 rules)
- Condition: Evidence at least 1 borrower intends to occupy the subject as their primary home was not provided
- What's needed: an occupancy-intent certification / military-orders / lease-review fact -- not currently modeled (no occupancy-related field or fact exists in FIELD_SPECS/FACT_SPECS)
- Machine-checkable: -

**underwriting-review:392** (1 rules)
- Condition: The loan was not submitted to VA within 60 days of closing
- What's needed: a VA-submission-date fact -- not modeled (no field captures when the loan was submitted to VA post-closing)
- Machine-checkable: -

**underwriting-review:403** (1 rules)
- Condition: For a second home, all requirements not met and all required documentation not provided
- What's needed: an occupancy-intent certification / military-orders / lease-review fact -- not currently modeled (no occupancy-related field or fact exists in FIELD_SPECS/FACT_SPECS)
- Machine-checkable: -

**underwriting-review:406** (1 rules)
- Condition: Special assessments not PIF & mtg not reduced by amt of unpaid assessments
- What's needed: loan_amount + adjusted-value fields (appraised_value is extracted; the loan amount itself and FHA's 'adjusted value' concept are not)
- Machine-checkable: -

**underwriting-review:407** (1 rules)
- Condition: The file did not document the current/future installments of taxes and special assessments
- What's needed: special-assessment / lender-incentive fields on closing_disclosure (doc exists in every loan; these specific line items are not in FIELD_SPECS)
- Machine-checkable: -

**underwriting-review:409** (1 rules)
- Condition: LTV/or ratios calculated incorrect based on UW type with a non-occ borrower
- What's needed: loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; appraised_value already is)
- Machine-checkable: -

**underwriting-review:412** (1 rules)
- Condition: The maximum LTV ratio for a manually underwritten loan with a non-occupying borrower exceeds 90%
- What's needed: loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; appraised_value already is)
- Machine-checkable: -

**underwriting-review:413** (1 rules)
- Condition: The maximum LTV ratio for an Accept Mortgage with a non-occupying borrower exceeds 95%
- What's needed: loan_amount field on final_1003/closing_disclosure (not currently in FIELD_SPECS; appraised_value already is)
- Machine-checkable: -

**underwriting-review:414** (1 rules)
- Condition: The non-occupying borrower is an interested party, such as the builder, seller, realtor or broker
- What's needed: an occupancy-intent certification / military-orders / lease-review fact -- not currently modeled (no occupancy-related field or fact exists in FIELD_SPECS/FACT_SPECS)
- Machine-checkable: -

**underwriting-review:416** (1 rules)
- Condition: A 30-day account balance with late payment > 12 months; 5% of the payment is not included in DTI
- What's needed: a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- Machine-checkable: -

**underwriting-review:418** (1 rules)
- Condition: Borr is in a debt management plan & the monthly counseling plan payment was not included in the DTI
- What's needed: a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- Machine-checkable: -

**underwriting-review:419** (1 rules)
- Condition: Credit report did not report a payment on a revolving account and 5% of the balance was not used
- What's needed: a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- Machine-checkable: -

**underwriting-review:420** (1 rules)
- Condition: Late mtg pymts on borr's rental property within 12 mos prior to app & the  full PITIA not in DTI
- What's needed: a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- Machine-checkable: -

**underwriting-review:421** (1 rules)
- Condition: Outstanding student loan credit report/actual documented pymt not used or 0.5% of the balance if $0
- What's needed: a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- Machine-checkable: -

**underwriting-review:422** (1 rules)
- Condition: Payment amt used was not the credit report amt & no documentation to support the alternate amt used
- What's needed: a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- Machine-checkable: -

**underwriting-review:423** (1 rules)
- Condition: Student loan pymt not in DTI as req'd even if paid by another party or in a forgiveness loan program
- What's needed: a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- Machine-checkable: -

**underwriting-review:424** (1 rules)
- Condition: The DTI debt ratio was calculated incorrectly and/or the ratio did not meet requirements
- What's needed: a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- Machine-checkable: -

**underwriting-review:425** (1 rules)
- Condition: Unsatisfied prior mortgage not in DTI; evidence another obligor has made payments 12 months missing
- What's needed: a debt-type classification + DTI-inclusion derivation over tradelines/urla_liabilities (both entity types are already extracted for every loan; no logic classifies a specific liability by type -- 30-day-late, contingent, judgment, lease, balloon, business, student-loan, etc. -- or aggregates a DTI ratio from them)
- Machine-checkable: -

**underwriting-review:434** (1 rules)
- Condition: Approve/Accept - FHA TOTAL feedback cert was not included in the documentation in the FHA binder
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:435** (1 rules)
- Condition: Refer - DU underwriter did not underwrite the loan and sign the underwriter's certificate
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:436** (1 rules)
- Condition: Reserves, income and/or PITIA amounts changed and exceeded tolerance levels without resubmission
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:439** (1 rules)
- Condition: Repair costs were added to the sales price before calculating the mortgage without meeting all req's
- What's needed: loan_amount + adjusted-value fields (appraised_value is extracted; the loan amount itself and FHA's 'adjusted value' concept are not)
- Machine-checkable: -

**underwriting-review:447** (1 rules)
- Condition: Disaster documentation age flexibilities used exceeding 6 mos from FEMA disaster declaration date
- What's needed: FEMA disaster-declaration date + ACE/ACE+PDR waiver documentation -- not in corpus
- Machine-checkable: -

**underwriting-review:449** (1 rules)
- Condition: Subject w/ ACE waiver or ACE+PDR & disaster impact did not document damage was not safety/structural
- What's needed: FEMA disaster-declaration date + ACE/ACE+PDR waiver documentation -- not in corpus
- Machine-checkable: -

**underwriting-review:451** (1 rules)
- Condition: Exceeded max number of 10 financed properties or was over 6 without min score of 720 or LPA Accept
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:453** (1 rules)
- Condition: The subject investment property ARM was ineligible as it was not a 7/6-month or 10/6-month ARM
- What's needed: mismo_amortization_type value-format comparison (the field IS already extracted from MISMO XML; the specific '7/6 vs 10/6' ARM-type parsing/comparison logic does not exist yet)
- Machine-checkable: -

**underwriting-review:454** (1 rules)
- Condition: The subject is an investment property that was not underwritten with Loan Product Advisor
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**underwriting-review:455** (1 rules)
- Condition: Evidence at least 1 borrower intends to occupy the subject as their primary home was not provided
- What's needed: an occupancy-intent certification / military-orders / lease-review fact -- not currently modeled (no occupancy-related field or fact exists in FIELD_SPECS/FACT_SPECS)
- Machine-checkable: -

**underwriting-review:458** (1 rules)
- Condition: 2nd home unfit for full time occ &/or unavailable for borr's exclusive use
- What's needed: an occupancy-intent certification / military-orders / lease-review fact -- not currently modeled (no occupancy-related field or fact exists in FIELD_SPECS/FACT_SPECS)
- Machine-checkable: -

**underwriting-review:461** (1 rules)
- Condition: The subject is a second home that was not underwritten with Loan Product Advisor
- What's needed: DU/LPA/TOTAL/GUS AUS submission-and-findings report ingestion (this pilot has no DU, LPA, or TOTAL AUS export at all; GUS findings exist only for loan 05/USDA, and only 2 fields are extracted from it -- usda_income_limit, usda_adjusted_household_income)
- Machine-checkable: -

**product-specific-check:14** (1 rules)
- Condition: Loan amount >$2M and additional appraisal requirements were not met
- What's needed: a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: explicit numeric/date threshold detected: '$2'

**product-specific-check:29** (1 rules)
- Condition: Property acquired subject/land within 6 months of application & funds not sourced
- What's needed: land/property acquisition date field + funds-sourcing documentation (not in corpus)
- Machine-checkable: 6-month acquisition-to-application date comparison + funds-sourcing doc presence

**product-specific-check:33** (1 rules)
- Condition: The borrower does not have sufficient contingency reserves in addition to PITI reserves as required
- What's needed: CTP contingency-reserve requirement threshold (an SME-supplied constant, not stated in this row) + reserves fields
- Machine-checkable: contingency-reserves-vs-PITI-reserves math

**product-specific-check:35** (1 rules)
- Condition: The final Detailed Cost Breakdown does not match the final 1003 amount for Cost to Build
- What's needed: a field/fact on the existing 'final_1003' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:58** (1 rules)
- Condition: RefiNow using base pay only, YTD paystub not provided or date over 30 days prior to application date
- What's needed: a distinct '30-days-old-or-newer' recency fact on paystub (deepen extraction)
- Machine-checkable: -

**product-specific-check:59** (1 rules)
- Condition: RefiNow using base pay plus variable income, most recent paystub & last year W2 not provided
- What's needed: a W2 doc type (not in extract_loan.py's DOC_TYPES at all) + a 'covers the most recent one-year period' recency fact
- Machine-checkable: -

**product-specific-check:60** (1 rules)
- Condition: RefiNow using self-employment, missing 1 yr personal/business tax returns & terms to waive not met
- What's needed: a field/fact on the existing 'se_income_index' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:65** (1 rules)
- Condition: An appraisal was obtained in a RefiNow without evidence the $500 credit was passed to the borrower
- What's needed: a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: explicit numeric/date threshold detected: '$500'

**product-specific-check:79** (1 rules)
- Condition: New subordinate lien UPB is higher than original subordinate lien UPB in RefiNow simultaneous refi
- What's needed: a field/fact on the existing 'payoff_statement' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:86** (1 rules)
- Condition: Resolved COVID-19 forbearance missed payments considered delinquencies in RefiNow pay history req's
- What's needed: a field/fact on the existing 'vom' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:102** (1 rules)
- Condition: CO Refi not downgraded to Refer & a mortgage debt has delinquency w/in 12 mos of case# assignment
- What's needed: a field/fact on the existing 'fhac_case_assignment' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: explicit numeric/date threshold detected: '12 months'

**product-specific-check:103** (1 rules)
- Condition: Product specific pay history req's not met based on the type of refinance and length of time owned
- What's needed: a field/fact on the existing 'vom' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:104** (1 rules)
- Condition: Subject not owned & occupied by at least 1 borr for the last 12 mos prior to case# assignment date
- What's needed: a field/fact on the existing 'fhac_case_assignment' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: explicit numeric/date threshold detected: '12 months'

**product-specific-check:106** (1 rules)
- Condition: Equity buy out from ex-spouse or other co-borrower without adequate documentation of the equity
- What's needed: a legally-enforceable-agreement doc type for an ex-spouse/co-owner equity buyout (not in corpus)
- Machine-checkable: equity-buyout supporting-document presence

**product-specific-check:113** (1 rules)
- Condition: The borrower received loan proceeds exceeding 2% of the subject loan amount or $2,000 in a LCO refi
- What's needed: an LCO-refi cash-back-to-borrower field (distinct from the refi-specific cash_out_to_borrower_1003, which is populated only for actual cash-out refis, not LCO)
- Machine-checkable: cash-back-to-borrower vs 2%-of-loan-amount-or-$2,000 threshold

**product-specific-check:120** (1 rules)
- Condition: No credit report or all available credit scores not put in FHA Connection for credit qual STR Refi
- What's needed: a field/fact on the existing 'credit_report' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:123** (1 rules)
- Condition: Streamline refi w/out appraisal & new mtg exceeds lower of orig principal balance or existing debt
- What's needed: a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:125** (1 rules)
- Condition: Streamline refinance - seasoning and payment history requirements not met
- What's needed: a field/fact on the existing 'vom' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:136** (1 rules)
- Condition: The purchase agreement indicates personal property and/or repairs are included in the purchase price
- What's needed: a purchase agreement/contract doc type — NOT in this pilot's corpus at all (same systemic gap flagged in decision 017's asset triage: no purchase contract exists in any of loan 01-05)
- Machine-checkable: purchase-agreement clause detection (personal property/repairs bundled into price)

**product-specific-check:145** (1 rules)
- Condition: Final sales contract and all addendums not in the file &/or is incorrect or unacceptable
- What's needed: purchase/sales contract doc type (not in corpus)
- Machine-checkable: final-sales-contract-and-addendums presence (same missing-purchase-contract gap as G136)

**product-specific-check:150** (1 rules)
- Condition: Refinance Authorization number was not obtained for FHA to FHA refinance
- What's needed: a field/fact on the existing 'fhac_case_assignment' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:162** (1 rules)
- Condition: Qualifying rate used not appropriate for the ARM type
- What's needed: ARM sub-type + note rate/margin fields (mismo_note_rate already extracted; the specific qualifying-rate-per-ARM-type rule table is not)
- Machine-checkable: ARM-type-to-qualifying-rate rule lookup

**product-specific-check:164** (1 rules)
- Condition: Short term ARM qualifying interest rate not calculated using the required method in ATR covered loan
- What's needed: the required ATR-covered-ARM qualifying-rate method (an SME-supplied formula) + ARM-type/note-rate fields
- Machine-checkable: short-term-ARM qualifying-rate recompute (FRD variant)

**product-specific-check:185** (1 rules)
- Condition: The difference in the initial note rate and the fully indexed rate > 3%
- What's needed: note rate (mismo_note_rate extracted) + index/margin fields for the fully-indexed-rate computation
- Machine-checkable: initial-note-rate-vs-fully-indexed-rate > 3% threshold

**product-specific-check:194** (1 rules)
- Condition: Qualifying rate used not appropriate for an ATR covered 1 year ARM with a 1% annual cap
- What's needed: 'qualifying rate used' as its own field (mismo_note_rate exists; the rate UNDERWRITING actually qualified against, and the ARM's annual-cap sub-type, are not yet distinct fields)
- Machine-checkable: qualifying rate == Note rate + 5% for a 1-year 1%-annual-cap ATR ARM

**product-specific-check:195** (1 rules)
- Condition: Qualifying rate used not appropriate for an ATR covered 1 year ARM with a 2% annual cap
- What's needed: same fields as G194
- Machine-checkable: qualifying rate == Note rate + 6% for a 1-year 2%-annual-cap ATR ARM

**product-specific-check:201** (1 rules)
- Condition: Community Second mtg was not obtained from an allowable party and/or all requirements not met
- What's needed: second-mortgage source-party field + an allowable-party reference list (not in corpus)
- Machine-checkable: Community-Second source-party membership test

**product-specific-check:210** (1 rules)
- Condition: Title policy/endorsement missing specific req's for community land trust/shared equity transactions
- What's needed: a specific CLT/shared-equity clause WITHIN the title policy (deepen title_commitment extraction, not mere presence)
- Machine-checkable: -

**product-specific-check:211** (1 rules)
- Condition: Energy efficient improvements without 92900-LT demonstrating the mtg and property are FHA compliant
- What's needed: a field/fact on the existing 'hud_92900a' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:245** (1 rules)
- Condition: Energy-related improvement work not documented in a HomeStyle such as the energy report or similar
- What's needed: a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:253** (1 rules)
- Condition: Appraisal did not give "as completed" value for Homestyle Renovation mtg
- What's needed: a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:265** (1 rules)
- Condition: The transaction involves cash proceeds to the borrower or payoff of impermissible debts
- What's needed: a field/fact on the existing 'payoff_statement' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: explicit numeric/date threshold detected: '$6,000'

**product-specific-check:285** (1 rules)
- Condition: Discount points added to the loan amount in a fixed refi to ARM IRRRL without meeting all req's
- What's needed: a discount-points-in-IRRRL field (deepen closing_disclosure/1003)
- Machine-checkable: discount-points-added-to-principal trigger detection

**product-specific-check:286** (1 rules)
- Condition: Discount points charged in an IRRRL without an appraisal to determine LTV &/or max LTV was exceeded
- What's needed: a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:292** (1 rules)
- Condition: The WebLGY IRRRL Appraisal Case Initiated screen not reviewed to determine funding fee exemption
- What's needed: a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:304** (1 rules)
- Condition: Resale restrictions loan req's not met, including property type, amortization, &/or loan purpose
- What's needed: a resale-restriction-program eligibility rule table (SME-defined) + a property-type field (not currently modeled)
- Machine-checkable: 3 named compliance dimensions: property type, amortization type (mismo_amortization_type already extracted), loan purpose (loan_purpose_1003/loan_purpose_cd already extracted)

**product-specific-check:306** (1 rules)
- Condition: Resale restrictions terminate & appraisal value did not use comps that are not resale restricted
- What's needed: a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:309** (1 rules)
- Condition: The Appraisal did not include comment on the resale restrictions &/or include an impact analysis
- What's needed: a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:310** (1 rules)
- Condition: The appraisal did not reflect the market value of the property without resale restrictions
- What's needed: a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:319** (1 rules)
- Condition: The leasehold estate does not constitute real property and/or is not insured by a title policy
- What's needed: a field/fact on the existing 'title_commitment' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:339** (1 rules)
- Condition: Sect 203(h)-Case# not assigned within 1 yr of the Presidentially-Declared Major Disaster Area-PDMDA
- What's needed: a field/fact on the existing 'fhac_case_assignment' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:363** (1 rules)
- Condition: HomeStyle loan agreement not executed by the lender & borr at closing on the same date as the note
- What's needed: a HomeStyle loan agreement doc + execution date field (not in corpus)
- Machine-checkable: HomeStyle-loan-agreement-execution-date == note-date match

**product-specific-check:374** (1 rules)
- Condition: Appraisal wasn't ordered before the completion of the foundation in a one-time construction loan
- What's needed: a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:377** (1 rules)
- Condition: The appraisal was not ordered with the applicable loan use and/or building status
- What's needed: a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:378** (1 rules)
- Condition: The appraisal wasn't ordered upon 100% completion of the subject two-time construction loan
- What's needed: a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: explicit numeric/date threshold detected: '100%'

**product-specific-check:380** (1 rules)
- Condition: Veteran chose their own builder & a VA Builder ID was not obtained prior to the issuance of the NOV
- What's needed: a field/fact on the existing 'va_nov' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:410** (1 rules)
- Condition: Appraisal effective date is over 4 mos old from the note date of the single-close construction perm
- What's needed: a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:413** (1 rules)
- Condition: Single-close construction perm Form 1004D indicates decline & new appraisal not obtained/requalified
- What's needed: Form 1004D fields (not in corpus — same family as G415)
- Machine-checkable: Form 1004D decline-status + re-qualification-appraisal presence

**product-specific-check:415** (1 rules)
- Condition: Single-close construction perm missing completed Form 1004D is not in the file
- What's needed: Form 1004D (Appraisal Update/Completion Report) as its own field/doc-subtype — not the base appraisal doc
- Machine-checkable: -

**product-specific-check:418** (1 rules)
- Condition: Initial and final cash-out Loan Comparison Disclosure was not provided or was not timely
- What's needed: a VA Loan Comparison Disclosure doc type — NOT the final 1003
- Machine-checkable: -

**product-specific-check:420** (1 rules)
- Condition: LTV exceeds 90% of reasonable value in Type I refi of a fixed to ARM & over 1 discount point charged
- What's needed: same VA reasonable-value field gap as G416
- Machine-checkable: LTV vs 90%-of-reasonable-value + discount-point-count gate (Type I fixed-to-ARM refi)

**product-specific-check:431** (1 rules)
- Condition: Current rent excluded w/out verifying it won't have to be paid after the single-close construction
- What's needed: a field/fact on the existing 'usda_ratio_waiver_doc' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:440** (1 rules)
- Condition: Constr-Perm-borr owned the land for over 6 months prior to case number assignment
- What's needed: a field/fact on the existing 'fhac_case_assignment' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: explicit numeric/date threshold detected: '6 months'

**product-specific-check:446** (1 rules)
- Condition: Construction perm work not completed & paid that could result in a mechanic's/materialmen’s lien
- What's needed: a lien-waiver/payment-completion doc type (not in corpus)
- Machine-checkable: unpaid-contractor / lien-risk documentation presence

**product-specific-check:455** (1 rules)
- Condition: Land purchase not documented with Closing Disclosure or similar legal doc for building on own land
- What's needed: a field/fact on the existing 'closing_disclosure' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:469** (1 rules)
- Condition: New construction inspections not on form HUD-92051, CI Report or other state sanctioned form
- What's needed: HUD-92051/Compliance Inspection Report doc type (not in corpus — same new-construction-inspection family as G327/G442)
- Machine-checkable: HUD-92051 (or state-sanctioned equivalent) inspection-form presence

**product-specific-check:487** (1 rules)
- Condition: The approved debt ratio waiver is not in the file in a GUS refer/manual UW with ratios over 34/41
- What's needed: confirmation this row's stated '34/41' pair is what usda_ratio_waiver_doc's extracted guideline actually contains for the loans this row targets — loan 05 (this pilot's only RHS fixture) extracts 29/41, not 34/41
- Machine-checkable: PITI/DTI ratio vs guideline comparison + waiver-in-file check (RatioWaiverShape's exact logic, on paper)

**product-specific-check:494** (1 rules)
- Condition: Pay history of loan being refinanced did not meet the req's as per refi type for Sect 502 refinance
- What's needed: a field/fact on the existing 'vom' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:496** (1 rules)
- Condition: Sect 502 Streamline/Non-streamline refi with GUS Refer missing debt ratio waiver meeting guidelines
- What's needed: a field/fact on the existing 'gus_findings' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:524** (1 rules)
- Condition: Subordination Agreement not in file or title policy does not reflect the 2nd mtg is in Jr position
- What's needed: a Subordination Agreement doc type + a junior-lien-position clause within the title policy
- Machine-checkable: -

**product-specific-check:526** (1 rules)
- Condition: CHOICEReno home improvement store completing the renovation do not have licensed/insured contractors
- What's needed: a contractor-licensing-verification doc type (not in corpus)
- Machine-checkable: contractor licensing/insurance-verification presence

**product-specific-check:528** (1 rules)
- Condition: CHOICEReno missing contract between borr & home improvement store doing renos w/in reasonable time
- What's needed: a CHOICERenovation contract doc type + date field (not in corpus)
- Machine-checkable: renovation-contract execution date vs 180/365-day threshold

**product-specific-check:537** (1 rules)
- Condition: CHOICERenovation did not document the borrower will occupy w/in 60 days of last reno disbursement
- What's needed: occupancy-certification + disbursement-date fields (not in corpus)
- Machine-checkable: occupancy-within-60-days-of-disbursement date check

**product-specific-check:544** (1 rules)
- Condition: CHOICEReno proceeds PIF short-term reno financing for repairs not done prior to the appraisal/Note
- What's needed: a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:545** (1 rules)
- Condition: CHOICERenovation appraisal did not include as completed value based on final plans & specs
- What's needed: a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:567** (1 rules)
- Condition: Int/ext didn't include as completed value for Construction Conv and Reno Mtg
- What's needed: a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:578** (1 rules)
- Condition: GreenCHOICE not interior/exterior w/ as completed value for energy efficiency improvements
- What's needed: a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:588** (1 rules)
- Condition: Home Possible sweat equity not documented and certified by the appraiser
- What's needed: an appraiser sweat-equity-certification field (appraisal doc exists; this specific field does not) — same family as asset-verification's G219/G278
- Machine-checkable: sweat-equity appraiser-certification presence

**product-specific-check:589** (1 rules)
- Condition: HomePossible-Cash on hand appears borrowed &/or residual income for savings not a positive number
- What's needed: a residual-income-for-savings computation field (not in corpus)
- Machine-checkable: residual-income-for-savings sign test (positive/negative number)

**product-specific-check:590** (1 rules)
- Condition: Source of funds for a Home Possible is an unsecured loan that did not meet all requirements
- What's needed: an unsecured-loan-type flag on tradelines/urla_liabilities (both entities already extracted; the loan-type-is-unsecured classification is not)
- Machine-checkable: unsecured-loan-as-funds-source detection (cross-referenced against tradelines/urla_liabilities entities ALREADY extracted)

**product-specific-check:600** (1 rules)
- Condition: Desktop appraisal used in a Home Possible purchase that did not meet desktop eligibility req's
- What's needed: a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:601** (1 rules)
- Condition: Full appraisal not obtained in Home Possible loan & Feedback Cert did not offer an appraisal waiver
- What's needed: a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:633** (1 rules)
- Condition: Funds for closing are more than $500 in a Refi Possible without sufficient funds being documented
- What's needed: cash-to-close + funds-documentation fields (not in corpus)
- Machine-checkable: $500 cash-to-close threshold + funds-documentation presence

**product-specific-check:635** (1 rules)
- Condition: The appraisal cost offset credit was not passed to the borrower
- What's needed: a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:637** (1 rules)
- Condition: Missing individual & business tax returns for last year in Refi Possible using self-employed income
- What's needed: a field/fact on the existing 'se_income_index' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: explicit numeric/date threshold detected: '1 year'

**product-specific-check:639** (1 rules)
- Condition: No 3rd party business exists verif 120 days prior to Note in Refi Possible using SE income
- What's needed: a field/fact on the existing 'se_income_index' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: explicit numeric/date threshold detected: '120 days'

**product-specific-check:641** (1 rules)
- Condition: No YTD paystub & W2 or VOE & 10 day PCVVOE in Refi Possible using tip, bonus, OT &/or commission
- What's needed: a field/fact on the existing 'voe' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: explicit numeric/date threshold detected: '10 day'

**product-specific-check:642** (1 rules)
- Condition: No YTD paystub or VOE & 10 day PCVVOE in Refi Possible using base non-fluctuating primary employment
- What's needed: a field/fact on the existing 'voe' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: explicit numeric/date threshold detected: '10 day'

**product-specific-check:659** (1 rules)
- Condition: No credit assessment in Refi Possible manual UW & pay history req's not met for mtg being refinanced
- What's needed: a field/fact on the existing 'vom' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:664** (1 rules)
- Condition: The minimum indicator score is not at least 620 in the subject Refi Possible
- What's needed: a credit-score field on credit_report (the doc type exists generically but is absent from loan 05, this pilot's only RHS loan — needs BOTH a new field AND a new RHS-specific fixture)
- Machine-checkable: 620 minimum-credit-score threshold

**product-specific-check:666** (1 rules)
- Condition: All requirements not complied with for a Section 502 GRH Mortgage
- What's needed: an RHS modification/waiver-approval doc type (not in corpus)
- Machine-checkable: RHS-waiver-approval-letter presence

**product-specific-check:692** (1 rules)
- Condition: Cash back or a principal curtailment in a purchase not on the Settlement/Closing Disclosure
- What's needed: a field/fact on the existing 'closing_disclosure' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**product-specific-check:702** (1 rules)
- Condition: Value used was not the value reported as of the appraisal effective date as required in a refinance
- What's needed: a field/fact on the existing 'appraisal' doc type not yet in FIELD_SPECS/FACT_SPECS
- Machine-checkable: -

**property-appraisal-review:26** (2 rules)
- Condition: A disclosure outlining the ROV process not provided at the time the appraisal report was provided
- What's needed: ROV-process disclosure doc type (not in corpus)
- Machine-checkable: presence of a ROV-process disclosure at the time the appraisal was provided

**property-appraisal-review:37** (1 rules)
- Condition: LPA over 120 days, not resubmitted to confirm PIW offer still valid
- What's needed: LPA/PIW offer-validity date field (not modeled) — a different real-world expiration than appraisal-effective-date staleness
- Machine-checkable: -

**property-appraisal-review:40** (1 rules)
- Condition: Required appraisal update was not reported on Form 442, Appraisal Update and/or Completion Report
- What's needed: Form 442 (Freddie Mac 'Appraisal Update and/or Completion Report') doc type — NOT the FHA MPR-completion-cert fact our extractor models
- Machine-checkable: -

**property-appraisal-review:41** (1 rules)
- Condition: The appraisal was no longer valid as of the disbursement date without an updated or new appraisal
- What's needed: disbursement-date field (not modeled — our fact measures age at CLOSING, not at disbursement) + 'updated or new appraisal' fact
- Machine-checkable: -

**property-appraisal-review:96** (1 rules)
- Condition: Comparable sales were not closed within the last 12 months and no explanation provided for their use
- What's needed: comp sale-closing-date field (not currently extracted — comps entity has comp_num/address/distance_miles/sale_price/gla/adjusted_sale_price, no closing date) for the '12 months' half
- Machine-checkable: comp_explanation_present (ALREADY extracted) for the explanation half

**property-appraisal-review:151** (1 rules)
- Condition: Applicable termite form, NPMA-99-A, NPMA-99-B or NPMA-33 missing &/or not signed as applicable
- What's needed: NPMA-99-A/99-B/33 form-specific doc type + a signature fact (neither modeled today)
- Machine-checkable: -

**property-appraisal-review:154** (1 rules)
- Condition: Correction in writing signed, dated w/ supporting docs if applicable by appraiser not in file
- What's needed: appraisal-correction-letter doc type (not in corpus)
- Machine-checkable: presence of a signed/dated written correction by the appraiser

**property-appraisal-review:179** (1 rules)
- Condition: Appraisal transfer letter from original lender not in the file
- What's needed: appraisal-transfer-letter doc type (not in corpus)
- Machine-checkable: presence of an appraisal-transfer letter from the original lender

**property-appraisal-review:184** (1 rules)
- Condition: The location map, building sketch, subject &/or comp photos not included
- What's needed: appraisal exhibit fields (photos, sketch, location map, invoice) — not modeled; the appraisal summary PDF used in this pilot's synthetic loans does not include exhibit pages
- Machine-checkable: presence of the named exhibit (photos/sketch/map/invoice)

**property-appraisal-review:229** (1 rules)
- Condition: Disclosure of the ROV process not given to the borr at application & when the appraisal was provided
- What's needed: ROV-process disclosure doc type (not in corpus)
- Machine-checkable: presence of a ROV-process disclosure given at application and at appraisal delivery

**property-appraisal-review:236** (1 rules)
- Condition: The Appraisal Logging Results is not in the file
- What's needed: FHA Connection Appraisal Logging Results doc type (not in corpus)
- Machine-checkable: presence of the FHA Appraisal Logging Results screen-print

**property-appraisal-review:240** (1 rules)
- Condition: Subject photos missing front/rear view, street, kitchen, all baths, living & extra photos as needed
- What's needed: appraisal exhibit fields (photos, sketch, location map, invoice) — not modeled; the appraisal summary PDF used in this pilot's synthetic loans does not include exhibit pages
- Machine-checkable: presence of the named exhibit (photos/sketch/map/invoice)

**property-appraisal-review:241** (1 rules)
- Condition: The subject/comp photos, building sketch &/or location map not included in appraisal exhibits
- What's needed: appraisal exhibit fields (photos, sketch, location map, invoice) — not modeled; the appraisal summary PDF used in this pilot's synthetic loans does not include exhibit pages
- Machine-checkable: presence of the named exhibit (photos/sketch/map/invoice)

**property-appraisal-review:263** (1 rules)
- Condition: The exterior only appraisal did not include street map &/or subject photos
- What's needed: appraisal exhibit fields (photos, sketch, location map, invoice) — not modeled; the appraisal summary PDF used in this pilot's synthetic loans does not include exhibit pages
- Machine-checkable: presence of the named exhibit (photos/sketch/map/invoice)

**property-appraisal-review:267** (1 rules)
- Condition: Appraisal subject to completion or repairs is missing an inspection by a qualified professional
- What's needed: post-repair inspection-report doc type (not in corpus)
- Machine-checkable: presence of a qualified-professional inspection for a repairs-conditioned appraisal

**property-appraisal-review:268** (1 rules)
- Condition: Appraisal transfer approval letter from the original lender was not provided, where required
- What's needed: transfer-approval-letter doc type (not in corpus)
- Machine-checkable: presence of an appraisal-transfer approval letter from the original lender

**property-appraisal-review:281** (1 rules)
- Condition: The required well water test was not conducted and handled by a disinterested third-party
- What's needed: well-water-test doc type + a 'disinterested third-party' source-authority fact (not modeled)
- Machine-checkable: -

**property-appraisal-review:282** (1 rules)
- Condition: The required well water test was not in the file or was older than 180 days from disbursement date
- What's needed: well-water-test date field (180-day staleness, not modeled — presence-only fact today)
- Machine-checkable: -

**property-appraisal-review:283** (1 rules)
- Condition: Well water test was not from the local health authority or a lab qualified to conduct water testing
- What's needed: well-water-test source-authority field (lab/health-authority qualification, not modeled)
- Machine-checkable: -

**property-appraisal-review:344** (1 rules)
- Condition: Appraisal or PDR review required an inspection, an inspection report or repair invoices not in file
- What's needed: post-repair inspection/invoice doc type (not in corpus)
- Machine-checkable: presence of an inspection report or repair invoices

**property-appraisal-review:375** (1 rules)
- Condition: Termite/pest inspection not in file where req'd by the lender, appraiser, inspector, or State law
- What's needed: termite_inspection_in_file (fact already extracted) — but shape has no RHS/state-law conditionality to gate on, and the AMQ row's own trigger is conditional ('where req'd by the lender, appraiser, inspector, or State law')
- Machine-checkable: -

**property-appraisal-review:379** (1 rules)
- Condition: Appraisal did not include all exhibits including a location map, floor plan sketch &/or all photos
- What's needed: appraisal exhibit fields (photos, sketch, location map, invoice) — not modeled; the appraisal summary PDF used in this pilot's synthetic loans does not include exhibit pages
- Machine-checkable: presence of the named exhibit (photos/sketch/map/invoice)

**property-appraisal-review:381** (1 rules)
- Condition: Appraisal is missing the appraiser’s certification, statement of assumptions & limiting conditions
- What's needed: appraiser-certification exhibit flag (deepen appraisal extraction — not modeled)
- Machine-checkable: presence of the appraiser's certification / statement of assumptions section

**property-appraisal-review:391** (1 rules)
- Condition: The appraisal did not include a copy of the appraisal invoice
- What's needed: appraisal exhibit fields (photos, sketch, location map, invoice) — not modeled; the appraisal summary PDF used in this pilot's synthetic loans does not include exhibit pages
- Machine-checkable: presence of the named exhibit (photos/sketch/map/invoice)

**property-appraisal-review:417** (1 rules)
- Condition: The appraiser reported defective conditions without photos of those conditions being provided
- What's needed: appraisal exhibit fields (photos, sketch, location map, invoice) — not modeled; the appraisal summary PDF used in this pilot's synthetic loans does not include exhibit pages
- Machine-checkable: presence of the named exhibit (photos/sketch/map/invoice)

**property-appraisal-review:478** (1 rules)
- Condition: Subject prior sales/Xfers in last 3 yrs or last 1 yr for the comps &/or verification source missing
- What's needed: subject/comp 3-year sales-history + verification-source fields (not modeled)
- Machine-checkable: presence of a prior-sales/transfer-history field + verification source

**property-appraisal-review:493** (1 rules)
- Condition: The water analysis report is older than 180 days at the time of the loan closing
- What's needed: water-analysis-report date field (180-day staleness, not modeled)
- Machine-checkable: -

**property-appraisal-review:531** (1 rules)
- Condition: Building sketch, required photographs and/or a legible street map not included
- What's needed: appraisal exhibit fields (photos, sketch, location map, invoice) — not modeled; the appraisal summary PDF used in this pilot's synthetic loans does not include exhibit pages
- Machine-checkable: presence of the named exhibit (photos/sketch/map/invoice)

**property-appraisal-review:644** (1 rules)
- Condition: No, all the required exhibits were not provided and/or acceptable
- What's needed: appraisal exhibit fields (photos, sketch, location map, invoice) — not modeled; the appraisal summary PDF used in this pilot's synthetic loans does not include exhibit pages
- Machine-checkable: presence of the named exhibit (photos/sketch/map/invoice)

**property-appraisal-review:659** (1 rules)
- Condition: Appraisal pre-dates disaster and borrower certification of property condition is missing
- What's needed: disaster borrower-certification doc type (not in corpus)
- Machine-checkable: presence of borrower certification of pre-disaster property condition

**property-appraisal-review:660** (1 rules)
- Condition: Appraisal pre-dates disaster and inspection evidencing property is pre-disaster condition is missing
- What's needed: disaster pre-condition inspection doc type (not in corpus)
- Machine-checkable: presence of an inspection evidencing pre-disaster property condition

**property-appraisal-review:661** (1 rules)
- Condition: Appraisal pre-dates disaster and lender certification property is pre-disaster condition is missing
- What's needed: disaster lender-certification doc type (not in corpus)
- Machine-checkable: presence of lender certification of pre-disaster property condition

**property-appraisal-review:674** (1 rules)
- Condition: No repair final inspection/completion report dated prior to closing &/or no photos as applicable
- What's needed: appraisal exhibit fields (photos, sketch, location map, invoice) — not modeled; the appraisal summary PDF used in this pilot's synthetic loans does not include exhibit pages
- Machine-checkable: presence of the named exhibit (photos/sketch/map/invoice)

### 3. Blocked on SME Clarification (107 groups)

These rules have ambiguous thresholds, subjective language, or judgment calls that require SME decomposition before automation is possible.

**asset-verification:7** (1 rules)
- Condition: The loan terms of the second mortgage was not documented and/or all requirements not met
- Rationale: Presence half is crisp; the appended open-ended 'all requirements' clause stays human.
- Stays human: catch-all 'and/or all requirements not met'

**asset-verification:13** (1 rules)
- Condition: HAP fee to the buyer exceeded $250 and/or all VA, property & occupancy standards were not met
- Rationale: The $250 threshold is crisp math once the HAP fee is captured; the appended open-ended standards clause stays human.
- Stays human: catch-all 'all VA, property & occupancy standards were not met'

**asset-verification:31** (1 rules)
- Condition: Like-kind/1031 exchange assets not documented or not compliant with Internal Revenue Code Sect 1031
- Rationale: Presence is checkable once the doc exists; full IRC compliance stays a judgment call layered on top.
- Stays human: IRC Section 1031 compliance determination

**asset-verification:127** (1 rules)
- Condition: Transfer of gift from donor acct to borr acct, closing agent, realtor or builder not documented
- Rationale: Related to the gift_transfer_evidence_in_file family (see G135's READY-TO-BUILD note) but bundles multiple named-recipient variants (donor acct/borr acct/closing agent/realtor/builder) the existing boolean fact likely doesn't distinguish — needs SME review before wiring.
- Stays human: -

**asset-verification:153** (1 rules)
- Condition: Subject includes undisclosed int party contributions paid outside of closing or includes abatements
- Rationale: Harder than a simple presence check (detecting an UNDISCLOSED item by definition requires comparing multiple documents for inconsistency), but still a factual cross-document comparison, not subjective judgment — kept YELLOW, not RED.
- Stays human: -

**asset-verification:187** (1 rules)
- Condition: Sale of real prop not documented as arm's length trans & that borrower is entitled to net proceeds
- Rationale: 'Arm's length' is normally evidenced by a specific affidavit/settlement doc, not inherently a subjective call once that doc exists — kept YELLOW, not RED.
- Stays human: -

**credit-liabilities-review:33** (1 rules)
- Condition: Medical, ID/credit card theft, &/or unauth use disputed accts included in cumulative balance calc
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:35** (1 rules)
- Condition: The police report/creditor supporting docs not in the file to support excluded disputed derog credit
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:43** (1 rules)
- Condition: Indications the IRS filed a Notice of Federal Tax Lien for taxes owed under the installment agrmt
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:62** (1 rules)
- Condition: Borr has unpaid tax lien w/out a valid repayment agreement with at least 3 regular payments made
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:63** (1 rules)
- Condition: Collections unpaid without documenting mitigating circumstances
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:65** (1 rules)
- Condition: Delinquent court ordered child support with admin offset was not brought current, PIF, or released
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:66** (1 rules)
- Condition: Disputed act w/ outstanding balance excluded from DTI & a justifiable dispute was not documented
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:67** (1 rules)
- Condition: Loan approved without credit exception documentation for a short sale action within prior 3 years
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:70** (1 rules)
- Condition: Previous USDA loss w/in 7 yrs prior to the date of submission without an agency approved exception
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:71** (1 rules)
- Condition: Approval does not evidence exception for foreclosure/deed-in-lieu reported within 2 years
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:73** (1 rules)
- Condition: Open judgement not paid in full or in a repayment plan with a history of timely payments
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:78** (1 rules)
- Condition: No, the RMCR does not indicate that it includes all available public record information
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:83** (1 rules)
- Condition: Loan approved although a recent significant increase in open accounts is evidenced
- Rationale: Needs tradeline open-date history (to detect a 'recent, significant increase in open accounts') this pilot doesn't parse, plus an undefined 'significant' threshold -- kept YELLOW rather than RED because a specific new-account count could ground it once an SME supplies the number; not purely a judgment call by wording alone.
- Stays human: -

**credit-liabilities-review:95** (1 rules)
- Condition: Borr has delinquent federal tax/non-tax debt without a lender’s cert of the applicant eligibility
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:97** (1 rules)
- Condition: Foreclosure sale or deed in lieu in the last 3 years and a credit exception was not documented
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:98** (1 rules)
- Condition: GUS-Outstanding collection $2k+ and documentation of no-impact to equity/ability to repay is missing
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:99** (1 rules)
- Condition: Late rental or mortgage payment reported/verified does not meet guidelines/exception not verified
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:100** (1 rules)
- Condition: Loan approval does not evidence exception for Chapter 7 bankruptcy reported within 3 years
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:101** (1 rules)
- Condition: Loan approved with open Chapter 13 bankruptcy and does not meet guidelines
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:102** (1 rules)
- Condition: MAN-Outstanding collection $2k+ and documentation of no-impact to equity/ability to repay is missing
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:104** (1 rules)
- Condition: Open non-federal judgment not PIF or have evidence of 3 timely non-lump sum pymts as per agreement
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:105** (1 rules)
- Condition: Outstanding collection reported and validation of monthly payment included in DTI is missing
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:130** (1 rules)
- Condition: Unpaid collection accounts with no documented re-established credit prior to approval
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:132** (1 rules)
- Condition: Credit exception not in the file in a manually underwritten loan with unacceptable credit
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:134** (1 rules)
- Condition: Determination that participants in credit counseling meet program criteria/credit exceptions missing
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:163** (1 rules)
- Condition: Disputed account reporting without evidence of resolution and accuracy of credit score
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:188** (1 rules)
- Condition: Non-medical charge-offs on non-mtg accts of $250 or more or total balances exceed $1,000 not PIF
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:189** (1 rules)
- Condition: Non-medical collections on non-mtg accts of $250 or more or total balances exceed $1,000 not PIF
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:191** (1 rules)
- Condition: UW did not require outstanding judgment(s) be satisfied prior to or at closing
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:194** (1 rules)
- Condition: Loan approved with a delinquent federal non-tax debt without determining account resolution
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:196** (1 rules)
- Condition: Loan approved with a delinquent federal tax debt without IRS repay agreement/evidence of  payments
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:198** (1 rules)
- Condition: Bankruptcy with no documented re-established credit prior to approval
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:199** (1 rules)
- Condition: Documented resolution for discrepancies in obligations or other derogatory credit is missing
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:200** (1 rules)
- Condition: FC or DIL with no documented re-established credit prior to approval
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:203** (1 rules)
- Condition: Open judgements on credit report not on the URLA w/out explanation/documentation
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:213** (1 rules)
- Condition: An unpaid federal tax lien was not subordinated to the subject mortgage
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:215** (1 rules)
- Condition: There are federal income taxes due on the current year tax return and proof paid has not been obtain
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:227** (1 rules)
- Condition: A judgment was not verified as being paid off or resolved with payment included in DTI
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:229** (1 rules)
- Condition: A bankruptcy was noted within the last 7 years and the required documentation was not obtained
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:230** (1 rules)
- Condition: Foreclosure not complete at least 24 mos from Ch 7 extenuating circumstances bankruptcy in manual UW
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:231** (1 rules)
- Condition: Foreclosure not complete at least 48 mos from Ch 7 financial mismanagement bankruptcy in manual UW
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:232** (1 rules)
- Condition: Late rental and/or payment reported/verified does not meet guidelines
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:233** (1 rules)
- Condition: Medical collections were considered adverse or derogatory credit information in a manual UW
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:236** (1 rules)
- Condition: Signed letter or email directly from the borrower not obtained for adverse or derogatory accounts
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:237** (1 rules)
- Condition: The recovery time period requirements not met for reestablishment of credit
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:238** (1 rules)
- Condition: Timeshare loan not considered an installment debt regardless of how it is shown on the credit report
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:248** (1 rules)
- Condition: Where a bankruptcy is reported but is not documented that credit has been re-established
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:257** (1 rules)
- Condition: Disputed medical/derogatory credit was excluded without required supporting documentation
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:259** (1 rules)
- Condition: Loan approval does not evidence exception for foreclosure/deed-in-reported within 3 years
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:264** (1 rules)
- Condition: Preforeclosure sale reported <3 years prior to FHA case number assignment; exception not documented
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:265** (1 rules)
- Condition: The borrower had a short sale in the last 3 yrs, documentation of an exception not in file
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:273** (1 rules)
- Condition: The borrower had major derogatory credit on revolving accounts in the previous 12 months
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:329** (1 rules)
- Condition: Contingent liability without evidence another obligor has made payments for the last 12 months
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:332** (1 rules)
- Condition: Outstanding collection account and 5% of the balance/amount on a payment agreement excluded from DTI
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:374** (1 rules)
- Condition: Re-established credit not documented where significant derogatory credit events are reported
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**credit-liabilities-review:375** (1 rules)
- Condition: Required documentation missing for a bankruptcy/foreclosure action reported in the last 7 years
- Rationale: Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- Stays human: -

**income-verification:221** (1 rules)
- Condition: The income calculation worksheet is not located in the file or is incomplete/inaccurate
- Rationale: Recurs identically under 5 different AMQ question categories. Presence half is crisp once the worksheet doc type is modeled; the appended discrepancy-explanation clause stays partly human, same pattern as asset-verification's G007 (crisp presence + appended open catch-all kept YELLOW, not RED).
- Stays human: 'income discrepancies were not explained' clause (appended, open-ended)

**income-verification:232** (1 rules)
- Condition: Income is declining and no explanation has been provided
- Rationale: Recurs under 2 AMQ question categories (general employment income, self-employed). No judgment word in the condition itself ('declining' and 'no explanation provided' are both factual, not evaluative) — blocked purely on missing multi-year income data, not a rule-clarity problem.
- Stays human: -

**income-verification:263** (1 rules)
- Condition: The income calculation worksheet is not located in the file or is incomplete/inaccurate
- Rationale: Recurs identically under 5 different AMQ question categories. Presence half is crisp once the worksheet doc type is modeled; the appended discrepancy-explanation clause stays partly human, same pattern as asset-verification's G007 (crisp presence + appended open catch-all kept YELLOW, not RED).
- Stays human: 'income discrepancies were not explained' clause (appended, open-ended)

**income-verification:272** (1 rules)
- Condition: The income calculation worksheet is not located in the file or is incomplete/inaccurate
- Rationale: Recurs identically under 5 different AMQ question categories. Presence half is crisp once the worksheet doc type is modeled; the appended discrepancy-explanation clause stays partly human, same pattern as asset-verification's G007 (crisp presence + appended open catch-all kept YELLOW, not RED).
- Stays human: 'income discrepancies were not explained' clause (appended, open-ended)

**income-verification:281** (1 rules)
- Condition: The income calculation worksheet is not located in the file or is incomplete/inaccurate
- Rationale: Recurs identically under 5 different AMQ question categories. Presence half is crisp once the worksheet doc type is modeled; the appended discrepancy-explanation clause stays partly human, same pattern as asset-verification's G007 (crisp presence + appended open catch-all kept YELLOW, not RED).
- Stays human: 'income discrepancies were not explained' clause (appended, open-ended)

**income-verification:298** (1 rules)
- Condition: The income calculation worksheet is not located in the file or is incomplete/inaccurate
- Rationale: Recurs identically under 5 different AMQ question categories. Presence half is crisp once the worksheet doc type is modeled; the appended discrepancy-explanation clause stays partly human, same pattern as asset-verification's G007 (crisp presence + appended open catch-all kept YELLOW, not RED).
- Stays human: 'income discrepancies were not explained' clause (appended, open-ended)

**income-verification:514** (1 rules)
- Condition: Income is declining and no explanation has been provided
- Rationale: Recurs under 2 AMQ question categories (general employment income, self-employed). No judgment word in the condition itself ('declining' and 'no explanation provided' are both factual, not evaluative) — blocked purely on missing multi-year income data, not a rule-clarity problem.
- Stays human: -

**underwriting-review:240** (1 rules)
- Condition: Closing costs and lender fees were unreasonable and/or they exceeded the total loan amount
- Rationale: Compound condition ('and/or'): the second half (fees exceed total loan amount) is crisp math once loan_amount exists; only 'unreasonable' is a judgment call. Kept YELLOW, not RED, following the assets-triage precedent for compound crisp+judgment conditions (e.g. decision 017's G007).
- Stays human: 'unreasonable' fee-amount judgment

**underwriting-review:287** (1 rules)
- Condition: All additional approval condition by the UW were not met
- Rationale: Generic 'were UW conditions cleared' catch-all; needs the conditions to be enumerated per loan, which this pilot doesn't capture.
- Stays human: -

**product-specific-check:11** (1 rules)
- Condition: Asset dissipation appropriate income calculator was not completed accurately
- Rationale: 'Accurately' names a specific, re-computable formula (an asset-dissipation calculator), not an open-ended judgment — crisp math once the input fields exist.
- Stays human: -

**product-specific-check:117** (1 rules)
- Condition: Acceptable credit history and ability to repay is not documented on credit qualifying streamline
- Rationale: Compound: the borrower-carryover half names a specific, checkable fact; the credit-history-acceptability half is open-ended and stays human.
- Stays human: 'acceptable credit history and ability to repay' (unstated criteria)

**product-specific-check:133** (1 rules)
- Condition: Seller tax credit included in funds to close that does not meet exception to offset the escrow acct
- Rationale: Names a specific, structured exception test (tax credit vs escrow shortage) — crisp once fields exist, not an open-ended judgment.
- Stays human: -

**product-specific-check:134** (1 rules)
- Condition: Sufficient funds to meet minimum contribution from acceptable source not documented and/or verified
- Rationale: Comparison basis (a minimum-contribution percentage the mortgage type defines) is real and crisp; source-acceptability is a bounded, enumerable list, not free-form judgment.
- Stays human: -

**product-specific-check:142** (1 rules)
- Condition: Land contract for deed considered a purchase did not meet all requirements
- Rationale: All three conjuncts are crisp, named, checkable facts once the document exists — no judgment language in the actual test.
- Stays human: -

**product-specific-check:183** (1 rules)
- Condition: The ARM Plan index was unacceptable to FNMA
- Rationale: 'Unacceptable to FNMA' has a real comparison basis — a specific, enumerable list of approved indices — not open-ended judgment.
- Stays human: -

**product-specific-check:217** (1 rules)
- Condition: The Cost of Energy efficiency improvements not considered or properly documented
- Rationale: 'Properly documented' names a real, specific documentation requirement, not an open-ended judgment.
- Stays human: -

**product-specific-check:218** (1 rules)
- Condition: Nonresidential value of farm land ex barn, silo, farm equip or livestock etc included in loan amt
- Rationale: Crisp dollar-value exclusion test once the appraisal breakdown field exists — not a subjective call.
- Stays human: -

**product-specific-check:222** (1 rules)
- Condition: HUD REO-Form HUD-9548 & addenda setting the sale terms/eligibility not in file or did not meet req's
- Rationale: Presence half is crisp; the appended catch-all clause stays human — same pattern as G145.
- Stays human: 'did not meet all requirements' (unstated residual)

**product-specific-check:264** (1 rules)
- Condition: The IRRRL borrower(s) are not the same as on the original loan & is not an acceptable life event
- Rationale: Compound: the borrower-match half is a crisp fact once prior-loan data exists; the 'acceptable life event' half is a bounded-but-unstated-here judgment, same donor/source-acceptability pattern seen throughout asset-verification.
- Stays human: 'acceptable life event' (unstated criteria)

**product-specific-check:295** (1 rules)
- Condition: Two or more unmarried Veterans each using home entitlement req'd prior VA approval not obtained
- Rationale: Crisp approval-record presence check, not a subjective call.
- Stays human: -

**product-specific-check:323** (1 rules)
- Condition: Constr/constr perm loan- Written approval from the borr prior to each draw pymt not evident
- Rationale: Crisp doc-presence test, not a subjective call — 'not evident' names a specific missing record.
- Stays human: -

**product-specific-check:366** (1 rules)
- Condition: Renovation contract was not fully executed by both the contractor & the borrower prior to closing
- Rationale: Crisp signature/date test, not a subjective call.
- Stays human: -

**product-specific-check:385** (1 rules)
- Condition: File did not validate construction cost: contracts, loan agreement, plans, receipts, invoices, etc.
- Rationale: Row says 'for example' but DOES name concrete document families, unlike the truly bare catch-alls classified RED elsewhere in this block — crisp presence-bundle check once documents exist.
- Stays human: -

**product-specific-check:386** (1 rules)
- Condition: No, the guarantee fee was not collected prior to submission of request for guarantee
- Rationale: Crisp date-order test, not a subjective call.
- Stays human: -

**product-specific-check:416** (1 rules)
- Condition: C/O refi max ln amt incl funding fee &/or energy eff improv up to $6k over 100% of reasonable value
- Rationale: 'Reasonable value' is VA's defined term of art (the NOV amount), not a subjective judgment — crisp % math once the field exists.
- Stays human: -

**product-specific-check:435** (1 rules)
- Condition: The file did not contain an acceptable executed construction contract in a single-close mortgage
- Rationale: 'Acceptable' here means 'executed/signed' — crisp presence test, not a subjective quality call.
- Stays human: -

**product-specific-check:441** (1 rules)
- Condition: Construction escrow account not closed & remaining funds not applied as a principal curtailment
- Rationale: Crisp doc/field test, not a subjective call.
- Stays human: -

**product-specific-check:451** (1 rules)
- Condition: All requirements not met for high balance mtg and variance not provided
- Rationale: Variance-doc-presence half is crisp; the catch-all clause stays human — same pattern as G145/G222.
- Stays human: 'all requirements not met' (unstated residual)

**product-specific-check:454** (1 rules)
- Condition: Building On Own Land-file did not document source of borr paid options, itemization & cost per item
- Rationale: 'Acceptable source' + itemization are named, specific documentation requirements, not open-ended judgment.
- Stays human: -

**product-specific-check:529** (1 rules)
- Condition: CHOICEReno, home improvement store doing reno does not have a managed contractor approval process
- Rationale: Crisp presence test, not a subjective call.
- Stays human: -

**product-specific-check:574** (1 rules)
- Condition: GreenCHOICE NCO proceeds paid existing debt that financed efficiency improvements & all reqs not met
- Rationale: Trigger fact is named and crisp; catch-all residual stays human.
- Stays human: 'all requirements not met' (unstated residual)

**product-specific-check:596** (1 rules)
- Condition: Home Possible 1 unit rental income did not meet 12 mos history or continuance requirements
- Rationale: Explicit numeric threshold (12 months) stated in-row; the continuance-affirmation half is softer but still names a specific certification, not open-ended judgment — kept YELLOW.
- Stays human: 'will continue to reside together for the foreseeable future' (unstated criteria)

**product-specific-check:632** (1 rules)
- Condition: Excess Refi Possible proceeds not a principal curtailment &/or not on the Closing Disclosure Stmt
- Rationale: Crisp field-presence test, not a subjective call.
- Stays human: -

**property-appraisal-review:39** (1 rules)
- Condition: Prior appraisal was re-used dated over 120 days of the Note date &/or all other req's not met
- Rationale: NEAR-MISS vs StaleAppraisalShape — related family (a REUSED PRIOR appraisal over 120 days), but the row targets appraisal REUSE specifically (our fact only measures this loan's own appraisal's age at closing, not whether it was carried over from a prior transaction) plus a vague catch-all suffix — not a safe direct wire.
- Stays human: bare 'all other req's not met' catch-all appended to the reuse condition

**property-appraisal-review:120** (1 rules)
- Condition: The appraiser reports the property has non-residential use that exceeds 49% of the total floor area
- Rationale: Crisp threshold math ('49%') once the field exists — not a judgment call, just an unbuilt field; condition: 'The appraiser reports the property has non-residential use that exceeds 49% of the total floor area'
- Stays human: -

**property-appraisal-review:164** (1 rules)
- Condition: Subject's 3 year sales history & comps sales history for last 12 months not reported
- Rationale: Crisp threshold math ('12 months') once the field exists — not a judgment call, just an unbuilt field; condition: "Subject's 3 year sales history & comps sales history for last 12 months not reported"
- Stays human: -

**property-appraisal-review:231** (1 rules)
- Condition: A copy of the appraisal report was not provided at least 3 days prior to the closing
- Rationale: Crisp threshold math ('3 days') once the field exists — not a judgment call, just an unbuilt field; condition: 'A copy of the appraisal report was not provided at least 3 days prior to the closing'
- Stays human: -

**property-appraisal-review:257** (1 rules)
- Condition: Appraisal is missing the appraiser’s certification, statement of assumptions & limiting conditions
- Rationale: Exhibit-level presence check, same family as G263/G421/G531 (already YELLOW) — reclassified from the conservative-default RED, since this is a specific-component-missing fact, not a narrative-adequacy judgment.
- Stays human: -

**property-appraisal-review:277** (1 rules)
- Condition: No water purification system with maintenance contract & escrow acct for water deemed unsafe
- Rationale: Reclassified from the family classifier's default RED match (incidental word 'deemed'): the actual checkable condition is presence of a maintenance contract and escrow account for a water-purification system, once the antecedent ('water deemed unsafe') holds — a crisp presence check, not a narrative judgment.
- Stays human: -

**property-appraisal-review:411** (1 rules)
- Condition: Appraiser not provided sales contract, known property info &/or contract updates if applicable
- Rationale: Reclassified from the conservative-default RED: this is a presence check on the lender's input package to the appraiser, a crisp (if currently unmodeled) fact, not a narrative-adequacy judgment.
- Stays human: -

**property-appraisal-review:423** (1 rules)
- Condition: Community water/sewage system not documented to be sufficient in size, properly operated/maintained
- Rationale: Distinguishable from WellSepticShape by subject matter alone: WellSepticShape is USDA RD's PRIVATE well & septic check; this VA row is about a COMMUNITY water/sewage system's documented adequacy — a different real-world system, plus an 'adequately maintained' judgment word. Not a match.
- Stays human: adequacy of community water/sewage system operation & maintenance

**property-appraisal-review:426** (1 rules)
- Condition: Nonresidential use impairs residential character of the subject or exceeded 25% of total floor area
- Rationale: Crisp threshold math ('25%') once the field exists — not a judgment call, just an unbuilt field; condition: 'Nonresidential use impairs residential character of the subject or exceeded 25% of total floor area'
- Stays human: -

**property-appraisal-review:485** (1 rules)
- Condition: No documentation that the site has acceptable water and waste water disposal systems
- Rationale: Presence is the crisp half; 'acceptable' is the same acceptability-judgment trap as G281/G283 — kept YELLOW since documentation presence is still checkable once the doc exists, but flagged, not treated as a WellSepticShape extension.
- Stays human: 'acceptable' water/wastewater system judgment

**property-appraisal-review:667** (1 rules)
- Condition: The appraisal was dated over 180 days before the note date in a property affected by a disaster
- Rationale: Crisp threshold math ('180 days') once the field exists — not a judgment call, just an unbuilt field; condition: 'The appraisal was dated over 180 days before the note date in a property affected by a disaster'
- Stays human: -

**property-appraisal-review:668** (1 rules)
- Condition: UW docs, credit reports, income/asset verifications over 180 days prior to note in disaster area
- Rationale: Crisp threshold math ('180 days') once the field exists — not a judgment call, just an unbuilt field; condition: 'UW docs, credit reports, income/asset verifications over 180 days prior to note in disaster area'
- Stays human: -

### 4. Other Blockers (695 groups)

These rules have blockers that don't fit the above categories (external lookups, cross-loan comparisons, etc.).

**asset-verification:2** (1 rules)
- Condition: Manual UW-VOD or last 2 mos bank statements do not verify funds on deposit
- Rationale: Same defect as G001, Manual-UW track (2 months, not 1).
- What's needed: same as G001

**asset-verification:11** (1 rules)
- Condition: Borrower has a loan outstanding secured by funds on deposit and these funds were treated as an asset
- Rationale: READY TO BUILD candidate — see READY_TO_BUILD; both entity types this needs (tradelines, bank_txns) are already extracted for every loan.
- What's needed: cross-reference of tradelines/urla_liabilities against bank_txns (new derivation, no new fixture)

**asset-verification:15** (1 rules)
- Condition: Rental income was considered without the applicable amount of reserves being documented
- Rationale: Reserves-for-rental-income is a well-defined number once the worksheet exists; no such document in any of the 5 synthetic loans today.
- What's needed: VA residual-income/reserves worksheet (EXPECTED_DOCS_BY_PROGRAM's residual_income_worksheet entry exists for VA but is not yet a reserves fact)

**asset-verification:17** (1 rules)
- Condition: Sufficient assets not documented to cover closing costs & any down payment if applicable
- Rationale: Generic cash-to-close sufficiency; both source docs already exist in the corpus, the derived comparison does not.
- What's needed: closing-cost + down-payment + total-available-assets derivation (deepen 1003/closing_disclosure)

**asset-verification:25** (1 rules)
- Condition: Large deposit not from the borr's income, acceptable funds awarded to the borr, or eligible asset
- Rationale: READY TO BUILD candidate: same defect family as the already-mapped LargeDepositShape (O-FNM-00215) — FRD wording variant.
- What's needed: none if wired — see READY_TO_BUILD

**asset-verification:27** (1 rules)
- Condition: Credit card reward points were used without evidence of reward points ownership & their cash value
- Rationale: Crisp presence/valuation check; no such document exists in any synthetic loan.
- What's needed: credit-card-rewards statement (ownership + cash value), not in corpus

**asset-verification:28** (1 rules)
- Condition: No evidence credit card reward points were redeemed for cash prior to closing
- Rationale: Same family as G027 (redemption-timing variant).
- What's needed: same credit-card-rewards doc gap as G027

**asset-verification:30** (1 rules)
- Condition: Anticipated sale proceeds calculated incorrectly for an owned home listed for sale but not yet sold
- Rationale: Sale-proceeds calculation is deterministic math once the listing/contract exists; it doesn't today.
- What's needed: home-sale listing/contract doc (not in corpus)

**asset-verification:33** (1 rules)
- Condition: Settlement statement documenting sufficient net cash proceeds from a property sale not in the file
- Rationale: Same net-cash-proceeds-from-a-prior-sale family as G004/G033.
- What's needed: prior-sale settlement statement (distinct from this loan's closing_disclosure)

**asset-verification:34** (1 rules)
- Condition: Signed employee relocation buy-out agreement not in the file
- Rationale: Crisp doc-presence check; niche document, absent from all 5 synthetic loans.
- What's needed: employee relocation buy-out agreement (not in corpus)

**asset-verification:37** (1 rules)
- Condition: All assets were not submitted to DU correctly
- Rationale: This pilot has no AUS-submission export at all for FNM (the RHS-equivalent, GUS findings, IS already partially extracted for loan 05 — a natural next fixture, not built here).
- What's needed: DU (Fannie Mae AUS) findings report, not in corpus

**asset-verification:39** (1 rules)
- Condition: Depository assets were not documented as per DU
- Rationale: Same DU-submission family as G037.
- What's needed: same DU-findings gap as G037

**asset-verification:43** (1 rules)
- Condition: The loan file did not document sufficient funds for closing
- Rationale: Generic sufficiency check, same family as G073/G103.
- What's needed: total-closing-funds-needed vs total-assets-available derivation

**asset-verification:44** (1 rules)
- Condition: Virtual currency used as a source of funds was not verified in U.S. dollars prior to closing
- Rationale: Same virtual-currency family as G174/G200/G201/G205/G213.
- What's needed: cryptocurrency-to-USD exchange confirmation (not in corpus)

**asset-verification:45** (1 rules)
- Condition: Loan proceeds for cash to close without file documenting loan terms and that it is a secured loan
- Rationale: Crisp doc-presence check once the note exists; no such document in any loan today.
- What's needed: personal/secured loan note (not in corpus)

**asset-verification:47** (1 rules)
- Condition: Ability to make payments on the new & current home, bridge/swing loan & other debts not documented
- Rationale: Same bridge-loan family as G049/G198/G263.
- What's needed: bridge/swing loan payment-ability worksheet (not in corpus)

**asset-verification:49** (1 rules)
- Condition: The bridge loan was cross-collateralized against the new property
- Rationale: Same bridge-loan family as G047.
- What's needed: bridge loan security instrument (not in corpus)

**asset-verification:50** (1 rules)
- Condition: 2 mo balance avg not provided for a business account or lower of the 2 mo avg/current bal not used
- Rationale: bank_statement doc exists generically, but neither business-vs-personal account classification nor a multi-month average is modeled today.
- What's needed: business-account-type flag + 2-month-average-balance derivation (deepen bank_statement)

**asset-verification:52** (1 rules)
- Condition: Business assets used as down payment, closing costs or reserves & a cash flow analysis not completed
- Rationale: Same business-account family as G050/G051.
- What's needed: cash-flow-analysis worksheet (not in corpus)

**asset-verification:60** (1 rules)
- Condition: Qualifying borr did not do landlord education or 1 yr landlord experience using ADU rental income
- Rationale: Crisp presence/duration check once the document exists.
- What's needed: landlord education certificate / experience documentation (not in corpus)

**asset-verification:62** (1 rules)
- Condition: Cash value loan/surrender of life insurance used without documenting repayment and receipt of funds
- Rationale: Same life-insurance family as G167.
- What's needed: life insurance policy/surrender statement (not in corpus)

**asset-verification:64** (1 rules)
- Condition: Source of funds for new accounts & recent deposits over 50% of adjusted income not documented
- Rationale: READY TO BUILD candidate: FHA wording variant of the already-mapped LargeDepositShape defect.
- What's needed: none if wired — see READY_TO_BUILD

**asset-verification:65** (1 rules)
- Condition: TPV of assets did not cover the last month & data not current w/in 30 days of the verification
- Rationale: Crisp 30-day-currency check once the TPV report exists as a document type.
- What's needed: Third Party Verification (TPV) report doc (not in corpus)

**asset-verification:70** (1 rules)
- Condition: Lesser of current balance or previous month’s ending balance not used for required reserves
- Rationale: Needs either a second month's bank statement (each loan currently has one) or a running-balance derivation from the one statement in hand.
- What's needed: multi-statement balance comparison (deepen bank_statement, or a 2nd month's fixture)

**asset-verification:71** (1 rules)
- Condition: No, asset documentation not reviewed by lender for recent large or unusual deposits
- Rationale: Related to, but not identical to, the large-deposit family (G025/G064/G102/G287) — this asks whether the LENDER reviewed for large/unusual deposits (a process fact), not a specific dollar threshold, so it is not a blind extension of LargeDepositShape.
- What's needed: lender-review-completed flag (not currently modeled)

**asset-verification:72** (1 rules)
- Condition: Non-payroll deposits were not confirmed as not being from undisclosed income sources
- Rationale: bank_txns already extracts each transaction; a payroll/non-payroll categorization does not exist yet.
- What's needed: payroll-vs-non-payroll deposit classification (deepen bank_txns)

**asset-verification:73** (1 rules)
- Condition: Sufficient funds for closing were not documented in the file
- Rationale: Same generic-sufficiency family as G043.
- What's needed: same sufficiency derivation as G043/G103

**asset-verification:76** (1 rules)
- Condition: Credit card points converted to cash qualify as a large deposit missing source as credit card reward
- Rationale: Related to the large-deposit family but needs a credit-card-specific sourcing document, not present.
- What's needed: credit-card-reward-conversion sourcing doc (not in corpus)

**asset-verification:79** (1 rules)
- Condition: File did not document the charitable organization providing the down payment assistance is a 501c
- Rationale: Usually evidenced by a document (not a live registry, unlike NMLS) — kept YELLOW, but flagged as a borderline candidate worth a second look before ruling out Bucket C entirely if no such letter is ever produced in practice.
- What's needed: charitable-org / DPA-program documentation (IRS determination letter; not in corpus)

**asset-verification:81** (1 rules)
- Condition: Earnest money deposit not entered correctly in DU based on if EMD cleared the borr's bank account
- Rationale: Duplicate condition text to G040.
- What's needed: same as G040 (duplicate condition, different AMQ question category)

**asset-verification:88** (1 rules)
- Condition: Employer financing provided without the file documenting that the terms meet FNMA req’s
- Rationale: Presence is crisp; full guideline-compliance determination stays partly human.
- What's needed: employer-financing agreement doc (not in corpus)

**asset-verification:90** (1 rules)
- Condition: Employer assistance used for cash to close without verifying & documenting receipt of the assistance
- Rationale: Crisp presence/receipt check once the document exists.
- What's needed: employer-assistance award/receipt doc (not in corpus)

**asset-verification:92** (1 rules)
- Condition: Foreign funds were not verified in US dollars prior to closing
- Rationale: Same foreign-funds family as G191/G192/G200/G201/G205.
- What's needed: foreign-currency exchange confirmation (not in corpus)

**asset-verification:95** (1 rules)
- Condition: All assets were not submitted to LPA correctly
- Rationale: Same AUS-submission gap as G037/G039 (Fannie's DU) — neither AUS export exists in this pilot; RHS's GUS is the only AUS output currently parsed.
- What's needed: LPA (Freddie Mac AUS) findings report, not in corpus

**asset-verification:97** (1 rules)
- Condition: All required information not provided on standard VOD
- Rationale: Same VOD-family gap as G001/G002/G105/G256/G257/G286.
- What's needed: VOD form (distinct from bank_statement; not in corpus)

**asset-verification:102** (1 rules)
- Condition: Source of unknown deposit exceeding 50% of qualifying income not documented &/or account not reduced
- Rationale: READY TO BUILD candidate — highest confidence: condition text is a byte-for-byte duplicate of group 287 (already mapped to LargeDepositShape), just filed under a different AMQ question category.
- What's needed: none if wired — see READY_TO_BUILD

**asset-verification:103** (1 rules)
- Condition: The loan file did not document sufficient funds for closing
- Rationale: Same generic-sufficiency family as G043.
- What's needed: same sufficiency derivation as G043/G073

**asset-verification:104** (1 rules)
- Condition: The loan file did not include a written analysis of the asset qualification source and amount
- Rationale: Crisp presence check once the document exists.
- What's needed: underwriter asset-analysis worksheet (not in corpus)

**asset-verification:105** (1 rules)
- Condition: Third-party asset verif did not identify the account with minimum of last 2 digits of account number
- Rationale: Same VOD family as G097.
- What's needed: same VOD-format detail gap as G097

**asset-verification:109** (1 rules)
- Condition: Gift funds were not entered correctly into DU and/or they were not identified separately as a gift
- Rationale: DU-family gap, same as G037/G039.
- What's needed: same DU-submission gap as G037, plus a gift-identification flag

**asset-verification:112** (1 rules)
- Condition: Gift used as own funds by donor living w/ borr last 12 mos no evidence both will occupy as primary
- Rationale: Crisp presence check once the document exists; niche, absent from all 5 loans.
- What's needed: co-residency/occupancy certification doc (not in corpus)

**asset-verification:113** (1 rules)
- Condition: Pooled gift funds to meet down pymt req, no cert donor has lived w/ borr for 12 mos & will continue
- Rationale: Same family as G112 (pooled-gift-funds variant).
- What's needed: same co-residency certification gap as G112

**asset-verification:115** (1 rules)
- Condition: The grant funds are not submitted under borrower number 1
- Rationale: Same AUS-submission gap as G037/G039/G095.
- What's needed: DU borrower-number submission detail (AUS-family, not in corpus)

**asset-verification:116** (1 rules)
- Condition: The grant funds award letter or legal agreement and transfer of funds is not in the file
- Rationale: Crisp presence check once the document exists.
- What's needed: grant award letter / legal agreement (not in corpus)

**asset-verification:117** (1 rules)
- Condition: The grant funds were from an unacceptable entity
- Rationale: Presence of a stated entity is crisp; guide-based acceptability stays human.
- What's needed: grant award letter (not in corpus, same as G116)

**asset-verification:120** (1 rules)
- Condition: Gift of equity not on the Settlement/Closing Disclosure Statement or amount incorrect
- Rationale: Same family as G111 (FRD variant).
- What's needed: equity amount cross-check (deepen gift_letter + closing_disclosure)

**asset-verification:121** (1 rules)
- Condition: Graduation gift for 1st time homebuyer & diploma/transcripts not provided supporting graduation date
- Rationale: Crisp presence check; graduation-gift program docs don't exist in any synthetic loan.
- What's needed: diploma/transcript documentation (niche, not in corpus)

**asset-verification:124** (1 rules)
- Condition: The  gift or grant from an eligible agency was not documented as required
- Rationale: Crisp presence check once whatever 'eligible agency' documentation is defined exists.
- What's needed: agency-eligibility documentation (deepen gift_letter or a new doc, unclear which)

**asset-verification:126** (1 rules)
- Condition: The grant funds are not submitted under borrower number 1
- Rationale: Same family as G115 (FRD variant).
- What's needed: same DU/LPA borrower-number gap as G115

**asset-verification:128** (1 rules)
- Condition: Wedding gift funds not documented w/ marriage license &/or not deposited w/in 90 days of marriage
- Rationale: Crisp presence/timing check once the document exists.
- What's needed: marriage license document (niche, not in corpus)

**asset-verification:135** (1 rules)
- Condition: No, proof of transfer not provided
- Rationale: READY TO BUILD candidate — top pick: the check this row needs already exists in code (GiftEvidenceShape/CHK-AST-002) but is wired to zero AMQ exception codes today.
- What's needed: none — wire this exception code into MAPPED_SHAPES; see READY_TO_BUILD

**asset-verification:137** (1 rules)
- Condition: For gifts of land, proof of donor ownership and title transfer to the borrower was not obtained
- Rationale: Crisp presence check once the document exists.
- What's needed: land-gift title-transfer documentation (niche, not in corpus)

**asset-verification:144** (1 rules)
- Condition: Govnt bonds ownership not documented &/or value not based on lesser of sale price/redeemable value
- Rationale: Crisp ownership/valuation check once the document exists.
- What's needed: government bond certificate/statement (not in corpus)

**asset-verification:146** (1 rules)
- Condition: The borrower's receipt of the grant and terms of use were not verified and documented
- Rationale: Receipt-verification is crisp once the doc exists; terms-of-use compliance stays partly human.
- What's needed: grant award/terms documentation (not in corpus)

**asset-verification:158** (1 rules)
- Condition: Legal document in lieu of contract to document interested party contributions not given to appraiser
- Rationale: Crisp presence check once the document exists; touches appraisal workflow too.
- What's needed: 'legal document in lieu of contract' (niche IPC doc, not in corpus)

**asset-verification:159** (1 rules)
- Condition: Lender gave cash-like incentive that did not meet req's &/or did not document no repayment is req'd
- Rationale: Presence is crisp; full requirement-compliance stays partly human.
- What's needed: lender-incentive agreement (not in corpus)

**asset-verification:166** (1 rules)
- Condition: Total interested party contributions not on contract/legal doc, 92900-LT, &/or Closing Disclosure
- Rationale: hud_92900a doc type exists (loan 02) though the specific 92900-LT (loan-estimate side) form is distinct; same IPC family as G148.
- What's needed: cross-doc IPC total reconciliation (contract/92900-LT/CD)

**asset-verification:167** (1 rules)
- Condition: Life insurance used & stmt not provided with all req'd information &/or liquidation if applicable
- Rationale: Same life-insurance family as G062.
- What's needed: life insurance statement (not in corpus)

**asset-verification:169** (1 rules)
- Condition: Cryptocurrency was considered in the asset calculation to establish the DTI ratio
- Rationale: Same virtual-currency family as G044/G174/G200/G201/G205/G213.
- What's needed: cryptocurrency documentation (not in corpus)

**asset-verification:173** (1 rules)
- Condition: Sale proceeds not real estate/exchange-traded securities without a bill of sale or proof of receipt
- Rationale: Same personal-property-sale family as G185/G186/G195/G261.
- What's needed: bill-of-sale document (not in corpus)

**asset-verification:174** (1 rules)
- Condition: The file did not document that the cryptocurrency source of funds was exchanged for U.S. dollars
- Rationale: Same virtual-currency family as G169.
- What's needed: same cryptocurrency gap as G169

**asset-verification:175** (1 rules)
- Condition: Traded securities or vested stock used without 2 mos statements, VOD or alt document or as per LPA
- Rationale: Same stocks/bonds family as G144/G214/G262/G273/G275/G281/G283.
- What's needed: brokerage/stock statement (not in corpus)

**asset-verification:185** (1 rules)
- Condition: Ownership, transfer and receipt of proceeds from the sale of personal property not documented
- Rationale: Same family as G173/G186/G195.
- What's needed: bill-of-sale / personal-property-sale doc (not in corpus)

**asset-verification:186** (1 rules)
- Condition: Personal property sold-item value, bill of sale & borr's receipt/deposit of proceeds not documented
- Rationale: Same personal-property-sale family as G185.
- What's needed: same bill-of-sale gap as G185

**asset-verification:191** (1 rules)
- Condition: Foreign asset availability not verified & converted to English or accurate translation not in file
- Rationale: Same foreign-asset family as G092/G200/G201/G205.
- What's needed: foreign asset statement + translation (not in corpus)

**asset-verification:192** (1 rules)
- Condition: Foreign assets not exchanged to U.S. dollars & in a Federal or State regulated financial institution
- Rationale: Same foreign-asset family as G191.
- What's needed: same foreign-asset gap as G191

**asset-verification:195** (1 rules)
- Condition: Value of personal property held for investment purposes was not documented
- Rationale: Same family as G185/G186.
- What's needed: personal-property valuation doc (not in corpus)

**asset-verification:197** (1 rules)
- Condition: Borr access to trust & effect withdrawal has on qualifying trust income not documented as applicable
- Rationale: Same trust family as G214/G281/G283.
- What's needed: trust agreement / trustee statement (not in corpus)

**asset-verification:198** (1 rules)
- Condition: Bridge loan proceeds - evidence loan is secured by real property & receipt of proceeds not in file
- Rationale: Same bridge-loan family as G047/G049/G263.
- What's needed: bridge loan security/receipt doc (not in corpus)

**asset-verification:199** (1 rules)
- Condition: Corporate relocation program, the file does not contain a copy of the executed buyout agreement
- Rationale: Same family as G034.
- What's needed: same relocation buy-out agreement gap as G034

**asset-verification:200** (1 rules)
- Condition: Foreign asset documents was not completed in English or with a complete and accurate translation
- Rationale: Same foreign-asset family as G191/G201/G205.
- What's needed: foreign-asset translation doc (not in corpus)

**asset-verification:201** (1 rules)
- Condition: Foreign assets used as a source of funds was not verified in U.S. dollars prior to closing
- Rationale: Same foreign-funds family as G092/G200/G205.
- What's needed: same foreign-currency exchange gap as G092

**asset-verification:202** (1 rules)
- Condition: Funds for closing from credit card, cash advance or unsecured LOC did not meet requirements
- Rationale: Related to G027/G223 (unallowable-funds family).
- What's needed: credit-card/cash-advance/LOC documentation (not in corpus)

**asset-verification:203** (1 rules)
- Condition: HELOC closing funds not secured by the borrower’s real property &/or HELOC proceeds  not received
- Rationale: Crisp presence/security check once the document exists.
- What's needed: HELOC agreement + proceeds doc (not in corpus)

**asset-verification:204** (1 rules)
- Condition: No appraisal & copy of trade-in contract to document equity net proceeds of trade in of prior home
- Rationale: Same trade-equity family as G220/G221/G279.
- What's needed: trade-in contract doc (not in corpus)

**asset-verification:205** (1 rules)
- Condition: No evidence foreign assets were exchanged into U.S. dollars & held in a U.S./state regulated bank
- Rationale: Same foreign-funds family as G092/G201.
- What's needed: same foreign-currency exchange gap as G092/G201

**asset-verification:206** (1 rules)
- Condition: Non-property asset secured loan ineligible source/ownership, value, receipt of funds not documented
- Rationale: Related to G045 (personal/secured loan family).
- What's needed: secured-loan documentation (not in corpus)

**asset-verification:207** (1 rules)
- Condition: Nonprofit individual development acct used without documentation of deposits or program
- Rationale: Related to G023 (Individual Development Account family).
- What's needed: IDA program documentation (not in corpus)

**asset-verification:209** (1 rules)
- Condition: Pooled funds-File did not document that the participants and the source of funds are eligible
- Rationale: Related to G196 (pooled-savings family); presence is crisp, eligibility determination stays partly human.
- What's needed: pooled-funds agreement (not in corpus)

**asset-verification:210** (1 rules)
- Condition: Proceeds from a 1031 exchange was not documented and verified
- Rationale: Same family as G031.
- What's needed: same 1031-exchange documentation gap as G031

**asset-verification:212** (1 rules)
- Condition: Rent credited to sale price no rent-sale agmt or credit exceeds difference rent paid & market rent
- Rationale: Same rent-credit family as G217/G231-235.
- What's needed: rent-to-own agreement (not in corpus)

**asset-verification:213** (1 rules)
- Condition: The file did not document that the virtual currency source of funds was exchanged for U.S. dollars
- Rationale: Same virtual-currency family as G044/G169/G174.
- What's needed: same virtual-currency exchange gap as G044

**asset-verification:214** (1 rules)
- Condition: The file did not document the value of the trust account from the trust manager or the trustee
- Rationale: Same trust family as G197/G281/G283.
- What's needed: trust manager statement (not in corpus)

**asset-verification:217** (1 rules)
- Condition: Rent credits agreement, market rent value & receipt of rent payments not verified & documented
- Rationale: Same rent-credit family as G212/G231-235.
- What's needed: rent credit agreement (not in corpus)

**asset-verification:219** (1 rules)
- Condition: Sweat equity used as a source of funds without labor & materials being documented as required
- Rationale: Same family as G278.
- What's needed: sweat-equity labor/materials documentation (not in corpus)

**asset-verification:220** (1 rules)
- Condition: The trade-in transaction of manufactured housing and the trade equity not documented
- Rationale: Same trade-equity family as G204/G221/G279.
- What's needed: trade-in contract/appraisal doc (not in corpus)

**asset-verification:221** (1 rules)
- Condition: Trade Equity Transaction- Appraisal and the closing disclosure were not verified and documented
- Rationale: Same family as G220.
- What's needed: same trade-equity documentation gap as G220

**asset-verification:223** (1 rules)
- Condition: Unallowable funds used from a personal unsecured loan, credit card or overdraft protection
- Rationale: Related to G045/G202 (unallowable-funds family).
- What's needed: personal-loan/credit documentation (not in corpus)

**asset-verification:225** (1 rules)
- Condition: Private savings club used w/out documenting club duration, receipt of funds or reasonability
- Rationale: Two of the three listed conditions (club duration, receipt of funds) are crisp facts; only the appended 'reasonability' clause stays human — kept YELLOW, not RED, since it isn't the row's sole condition.
- What's needed: private-savings-club statement (not in corpus)

**asset-verification:231** (1 rules)
- Condition: Rent credit for option to purchase agmt w/ 12 mos term, rental amt & terms of the lease not in file
- Rationale: Same rent-credit family as G212/G217/G233-235.
- What's needed: lease/option-to-purchase agreement (not in corpus)

**asset-verification:236** (1 rules)
- Condition: Collateralized loan used was not documented w/ a copy of the Note and receipt of loan proceeds
- Rationale: Related to G045/G206 (secured-loan family).
- What's needed: collateralized-loan note (not in corpus)

**asset-verification:237** (1 rules)
- Condition: Disaster relief loan used without the promissory note being verified and documented
- Rationale: Crisp presence check once the document exists.
- What's needed: disaster-relief promissory note (niche, not in corpus)

**asset-verification:238** (1 rules)
- Condition: Existence and amounts in retirement accts and outstanding loan balance not documented and verified
- Rationale: Same retirement family as G249/G251/G252/G254-257.
- What's needed: retirement account statement (not in corpus)

**asset-verification:241** (1 rules)
- Condition: Borr has 7 to 10 financed properties, including the subject, & 8 mos reserves for each not verified
- Rationale: Same family as G240 (7-10 property tier).
- What's needed: same financed-property-schedule gap as G240

**asset-verification:244** (1 rules)
- Condition: All assets submitted to the AUS were not verified and documented
- Rationale: Same AUS-submission gap as G037/G039/G095/G179/G243.
- What's needed: AUS/TOTAL Scorecard findings (FHA's AUS, not in corpus)

**asset-verification:247** (1 rules)
- Condition: Rental income used for a 1 unit with an ADU & reserves equivalent to 2 months PITI were not verified
- Rationale: Same family as G246 (ADU-rental-income variant).
- What's needed: same PITI-reserves gap as G246

**asset-verification:248** (1 rules)
- Condition: Three months PITI reserves were not verified and documented for a 3-4 unit property
- Rationale: Same family as G246 (3-4 unit variant).
- What's needed: same PITI-reserves gap as G246

**asset-verification:249** (1 rules)
- Condition: No evidence vested funds for down pymt/closing/reserves are allowed regardless of employment status
- Rationale: Same retirement family as G238.
- What's needed: retirement-plan vesting-schedule doc (not in corpus)

**asset-verification:251** (1 rules)
- Condition: Evidence of liquidation of retirement funds needed for closing was not documented
- Rationale: Same family as G238.
- What's needed: same retirement-account-statement gap as G238

**asset-verification:254** (1 rules)
- Condition: Liquidation of retirement accts not provided & total was less than 20% of the amt needed to close
- Rationale: Same family as G238.
- What's needed: same retirement-account gap as G238 (20% threshold)

**asset-verification:257** (1 rules)
- Condition: VOD or 2 months statements not provided for standard documentation of retirement accounts
- Rationale: Same family as G256 (2-month standard-doc variant).
- What's needed: same retirement-VOD gap as G256

**asset-verification:260** (1 rules)
- Condition: Personal asset sale proceeds exceed 50% of monthly qualifying income w/out an independent valuation
- Rationale: The 50%-of-income comparison reuses base_monthly_income_1003 (already extracted), but the independent-valuation requirement is a genuinely separate, absent fixture — not a blind extension of LargeDepositShape.
- What's needed: independent valuation doc for a sold personal asset (not in corpus)

**asset-verification:261** (1 rules)
- Condition: Proceeds from the sale of a titled personal asset used without documenting the borrower’s ownership
- Rationale: Same personal-property-sale family as G173/G185/G186/G195.
- What's needed: title/ownership + bill-of-sale doc (not in corpus)

**asset-verification:262** (1 rules)
- Condition: Source of funds from stocks, bonds, mutual or trust funds used without documenting ownership & value
- Rationale: Same stocks/bonds/trust family as G144/G175/G214/G273/G275/G281/G283.
- What's needed: brokerage/trust statement (not in corpus)

**asset-verification:263** (1 rules)
- Condition: Bridge loan proceeds not documented and/or did not include the payment in the DTI as applicable
- Rationale: Same bridge-loan family as G047/G049/G198.
- What's needed: bridge loan documentation (not in corpus)

**asset-verification:266** (1 rules)
- Condition: File did not document that the terms of a family loan as source of funds met HUD's criteria
- Rationale: Presence is crisp; full HUD-criteria compliance stays partly human.
- What's needed: family loan note (not in corpus)

**asset-verification:267** (1 rules)
- Condition: Missing nonprofit secondary financing note/mtg, receipt of funds not documented or all req's not met
- Rationale: Same secondary-financing family as G007/G198/G236/G268-271.
- What's needed: nonprofit second-mortgage note (not in corpus)

**asset-verification:268** (1 rules)
- Condition: Source from nonprofit that is an instrumentality of govt and required documentation not provided
- Rationale: Same family as G267.
- What's needed: same nonprofit secondary-financing gap as G267

**asset-verification:269** (1 rules)
- Condition: Subordinate financing was allowed on a Co-op share loan without obtaining a policy exception
- Rationale: Presence of an approval record is crisp; whether an exception was properly granted stays partly human.
- What's needed: policy-exception approval doc (not in corpus)

**asset-verification:270** (1 rules)
- Condition: Subordinate lien not evidenced by a note, recorded mtg, &/or not clearly subordinate to 1st mtg lien
- Rationale: Same secondary-financing family as G267/G269/G271.
- What's needed: subordination agreement / recorded mortgage doc (not in corpus)

**asset-verification:273** (1 rules)
- Condition: A copy of the stock/bond certificate not provided for non-brokerage accounts
- Rationale: Same stocks/bonds family as G144/G175/G262/G275/G281/G283.
- What's needed: stock/bond certificate (not in corpus)

**asset-verification:275** (1 rules)
- Condition: Stocks or other investment funds not documented w/ stmt with vested balance/withdrawal conditions
- Rationale: Same family as G273.
- What's needed: same stock/bond statement gap as G273

**asset-verification:278** (1 rules)
- Condition: Sweat equity was considered on an unallowable transaction and eligibility requirements were not met
- Rationale: Same family as G219; documentation presence is crisp, transaction-type eligibility stays partly human.
- What's needed: sweat-equity documentation (not in corpus)

**asset-verification:279** (1 rules)
- Condition: No, documentation showing the trade equity meets Fannie Mae's requirements not provided
- Rationale: Same family as G220.
- What's needed: same trade-equity documentation gap as G204/G220/G221

**asset-verification:281** (1 rules)
- Condition: Evidence of receipt of trust funds needed to close not in the file
- Rationale: Same trust family as G197/G214/G283.
- What's needed: trust fund receipt evidence (not in corpus)

**asset-verification:283** (1 rules)
- Condition: Trust funds-No Trust Agmt/Trust Mgr Stmnt naming borr as beneficiary & amount available to disburse
- Rationale: Same trust family as G197/G214/G281.
- What's needed: trust agreement/trustee statement (not in corpus)

**asset-verification:284** (1 rules)
- Condition: Funds recently deposited in US bank by non-US citizen were not sourced
- Rationale: Related to the large-deposit family, but citizenship data isn't modeled at all — a genuinely separate, absent fixture.
- What's needed: citizenship/foreign-national documentation (not in corpus)

**asset-verification:286** (1 rules)
- Condition: No, a VOD or account statement verifying each account not provided
- Rationale: Same VOD family as G001/G002/G097/G105/G256/G257.
- What's needed: VOD form (not in corpus)

**asset-verification:292** (1 rules)
- Condition: Ineligible custodial account (UTMA) and/or (UGMA) was used to qualify
- Rationale: Crisp eligibility check once the document exists.
- What's needed: custodial account (UTMA/UGMA) statement (not in corpus)

**credit-liabilities-review:17** (1 rules)
- Condition: Documentation that outstanding balance is paid in full for the past 12 months on a 30-day account
- Rationale: Needs 12 months of month-by-month payment history for a specific tradeline -- `extract_tradelines()` captures only a single current-status snapshot per tradeline (creditor/type/balance/monthly_payment/status), not a payment-history timeline; only the VOM (loan 04, one specific mortgage) has that depth in this corpus.
- What's needed: -

**credit-liabilities-review:19** (1 rules)
- Condition: Credit inquiries including new debts from material inquiries are not in the debt ratio
- Rationale: Needs a parsed Inquiries table (already visible in the loan 01 credit report's text -- 'Inquiries (last 120 days)' with Date/Bureau/Requesting Party -- but not yet in FIELD_SPECS/entities) cross-referenced against whether new debt was opened; Bucket-B-style (deepen extraction of a section already present in the one document we have), not a missing document.
- What's needed: -

**credit-liabilities-review:21** (1 rules)
- Condition: Business debt(s) not included in DTI or documentation debt(s) is paid by the business is missing
- Rationale: Same business-debt-in-DTI family as O-FNM-50006 (FHA wording variant, adds a self-employment/cash-flow-analysis angle) -- MISCLASSIFIED by the same mechanical doc_presence false-positive.
- What's needed: -

**credit-liabilities-review:23** (1 rules)
- Condition: Account with 30 day late payment in 12 months evident; 5% of the balance not included in DTI
- Rationale: The percentage-of-balance math (5%/1.5%/0.5% thresholds) is crisp arithmetic once the relevant balance is in hand, and `extract_tradelines()` already captures type/balance/monthly_payment per tradeline -- but confirming whether the LENDER actually included the computed amount in the final DTI needs a DTI worksheet this pilot doesn't derive (same gap as F_PITIA_DTI_REO); and month-by-month late-payment-in-12-months detection needs payment-history depth the tradeline snapshot (a single current 'Status' value) doesn't carry. Trigger data partly in hand; verification math not yet built.
- What's needed: -

**credit-liabilities-review:25** (1 rules)
- Condition: Credit report payment or actual documented payment not used to calculate an outstanding student loan
- Rationale: Student-loan payment-substitution math (0.5%/1% of balance when the credit report shows a $0 or missing payment) is crisp arithmetic, and `extract_tradelines()` already captures tradeline type/balance/monthly_payment (loan 01 has one Student tradeline) -- but verifying which qualifying-payment value the lender ACTUALLY used needs a DTI/qualifying-payment worksheet this pilot doesn't extract or derive from any document today. Trigger-detection is Bucket-B-close; the verification half is not.
- What's needed: -

**credit-liabilities-review:27** (1 rules)
- Condition: Mortgage debt reported 30+ days late/12 months; AUS not downgraded to Refer
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**credit-liabilities-review:28** (1 rules)
- Condition: Significant debt reported 90+ late is not updated within 90 days of the AUS report
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**credit-liabilities-review:29** (1 rules)
- Condition: Significant debt reported 90+ late/not updated within 90 days of report; AUS not downgraded to Refer
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**credit-liabilities-review:30** (1 rules)
- Condition: Undisclosed debt verification reflects 30-day late payment(s)/12 months; AUS not downgraded to Refer
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**credit-liabilities-review:32** (1 rules)
- Condition: Disputed derogatory credit accounts exceed $1k but the loan was not downgraded to Refer
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**credit-liabilities-review:37** (1 rules)
- Condition: Payments or debts associated with an EAH Benefit were excluded from ratios without all req's met
- Rationale: Employer Assisted Homeownership (EAH) benefit agreement -- same document family asset-verification's triage already flagged as absent from this corpus (G020/G022).
- What's needed: -

**credit-liabilities-review:42** (1 rules)
- Condition: IRS installment agreement verifying the payment terms, monthly payment & balance was not in the file
- Rationale: IRS installment-agreement document (payment terms/balance/lien notice) -- not a doc type in this corpus.
- What's needed: -

**credit-liabilities-review:45** (1 rules)
- Condition: Pending IRS installment agrmt & greater of the monthly pymt or taxes owed divided by 72 not in DTI
- Rationale: IRS installment-agreement document (payment terms/balance/lien notice) -- not a doc type in this corpus.
- What's needed: -

**credit-liabilities-review:46** (1 rules)
- Condition: Pending IRS installment agrmt & the application w/ taxes owed & requested pymt terms not documented
- Rationale: IRS installment-agreement document (payment terms/balance/lien notice) -- not a doc type in this corpus.
- What's needed: -

**credit-liabilities-review:47** (1 rules)
- Condition: The IRS installment agreement has over 10 mos of payments remaining & was not included in the DTI
- Rationale: IRS installment-agreement document (payment terms/balance/lien notice) -- not a doc type in this corpus.
- What's needed: -

**credit-liabilities-review:48** (1 rules)
- Condition: The file did not verify the borrower is not past due per the terms of the IRS installment agreement
- Rationale: IRS installment-agreement document (payment terms/balance/lien notice) -- not a doc type in this corpus.
- What's needed: -

**credit-liabilities-review:49** (1 rules)
- Condition: All LP requirements were not met in order to assess the transaction with no usable credit scores
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**credit-liabilities-review:50** (1 rules)
- Condition: Auth user of a tradeline in LPA Accept w/ feedback message requiring adtl documentation not obtained
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**credit-liabilities-review:51** (1 rules)
- Condition: Final verification report not in file where positive cash flow resulted in a risk class of Accept
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**credit-liabilities-review:52** (1 rules)
- Condition: Monthly cash flow was considered without at least 12 months of account data transmitted to LPA
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**credit-liabilities-review:53** (1 rules)
- Condition: No usable credit score & collections (not medical), judgments or tax liens present in last 24 mos
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**credit-liabilities-review:55** (1 rules)
- Condition: The 1008/1077 or similar document was incomplete, incorrect or not in the LPA underwritten file
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**credit-liabilities-review:56** (1 rules)
- Condition: A 24 month residency history was not provided on the credit report
- Rationale: MISCLASSIFIED (matched 'was not provided' + 'credit report' keyword) -- needs an RMCR-specific 24-month residency-history field, same F_RMCR_FORMAT family elsewhere in this block, not a bare presence check.
- What's needed: -

**credit-liabilities-review:57** (1 rules)
- Condition: No, the RMCR in the file does not indicate that it includes all available public record information
- Rationale: Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- What's needed: -

**credit-liabilities-review:58** (1 rules)
- Condition: RMCR does not reflect 2 credit repositories for each applicant/area of residency/prior 2 years
- Rationale: Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- What's needed: -

**credit-liabilities-review:59** (1 rules)
- Condition: The RMCR in the file does not include the required credit information for each debt shown
- Rationale: Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- What's needed: -

**credit-liabilities-review:60** (1 rules)
- Condition: The RMCR in the file is not  in the proper format and appears altered
- Rationale: Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- What's needed: -

**credit-liabilities-review:75** (1 rules)
- Condition: Satisfactory payment history/counseling agency approval missing for credit counseling participants
- Rationale: Consumer credit counseling program enrollment/payout/agency-approval document -- not a doc type in this corpus.
- What's needed: -

**credit-liabilities-review:77** (1 rules)
- Condition: Accounts w/ a balance not updated with the creditor within 90 days of the date of the credit report
- Rationale: Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- What's needed: -

**credit-liabilities-review:79** (1 rules)
- Condition: RMCR does not reflect 2 credit repositories for each applicant/area of residency/prior 2 years
- Rationale: Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- What's needed: -

**credit-liabilities-review:80** (1 rules)
- Condition: Responsive statements concerning items on the report including trade and credit history are missing
- Rationale: MISCLASSIFIED (matched 'not reflected' + 'credit report' keyword) -- same RMCR-format-field family as O-FRD-00149; 'responsive verification statements' aren't modeled in this corpus's credit report.
- What's needed: -

**credit-liabilities-review:82** (1 rules)
- Condition: Credit score in caution range with a high balance-to-limits or high overall use of revolving credit
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**credit-liabilities-review:84** (1 rules)
- Condition: Loan approved with a pattern of high balance-to-limits or high overall use of revolving credit
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**credit-liabilities-review:86** (1 rules)
- Condition: Business debt(s) not included in DTI or documentation debt(s) is paid by the business is missing
- Rationale: Same business-debt-in-DTI family as O-FNM-50006 (FRD wording variant) -- MISCLASSIFIED by the same mechanical doc_presence false-positive.
- What's needed: -

**credit-liabilities-review:87** (1 rules)
- Condition: Contingent liability without evidence another obligor has made payments for the last 12 months
- Rationale: Needs a 12-month third-party-payment history (contingent-liability co-obligor, cosigner, or authorized-user account owner) -- `urla_liabilities`/`tradelines` capture the liability itself but not who else has been paying it or for how long; no such payment-history document exists in this corpus.
- What's needed: -

**credit-liabilities-review:88** (1 rules)
- Condition: Housing or DTI ratio exceed the guidelines without a written explanation justifying the decision
- Rationale: PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- What's needed: -

**credit-liabilities-review:89** (1 rules)
- Condition: Loan/deductions listed on the paystubs were not addressed
- Rationale: Verified against the actual synthetic paystub (loan 01, `03_Paystub_Most_Recent.pdf`): its Deductions section lists only standard tax withholdings (Federal Withholding, Social Security, Medicare, NC State Tax) -- no loan-type deduction or military allotment line appears in any paystub in this corpus. Genuine Bucket-A-style fixture gap (the paystub doc type exists; the specific line item this rule needs does not), not a Bucket-B extraction-deepening candidate -- there is nothing yet to extract.
- What's needed: -

**credit-liabilities-review:90** (1 rules)
- Condition: Other property owned expenses excluded & no evidence uninterested party made pymts for last 12 mos
- Rationale: PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- What's needed: -

**credit-liabilities-review:91** (1 rules)
- Condition: Solar panels under a lease/power purchase agreement were excluded and documentation of terms not met
- Rationale: Needs a lease/HELOC/timeshare/solar-panel-agreement/virtual-currency-secured-loan document -- none of these niche liability-collateral document types exist in this corpus (same 'document family the synthetic corpus never modeled' pattern as several asset-verification YELLOW groups).
- What's needed: -

**credit-liabilities-review:92** (1 rules)
- Condition: There are federal income taxes due on the current year tax return and proof paid has not been obtain
- Rationale: Current-year tax return + proof-of-payment documentation -- not a doc type in this corpus (identical condition text recurs across FHA/FRD/RHS/VA/FNM -- a single fixture gap, not five separate ones).
- What's needed: -

**credit-liabilities-review:93** (1 rules)
- Condition: Updated credit report revealed impactful additional debts, not re-underwritten to include in DTI
- Rationale: PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- What's needed: -

**credit-liabilities-review:96** (1 rules)
- Condition: Disputed account reported does not qualify for an exception and not downgraded to Refer
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**credit-liabilities-review:106** (1 rules)
- Condition: Alimony/child support/maintenance payments is not in DTI and required documentation is missing
- Rationale: Divorce decree / court order / separation agreement documenting alimony, child support, or maintenance payment terms -- not a doc type in this corpus.
- What's needed: -

**credit-liabilities-review:108** (1 rules)
- Condition: Authorized user account did not meet requirements and the loan was not downgraded to a Refer
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**credit-liabilities-review:109** (1 rules)
- Condition: Authorized user account was considered while it was not indicative of the applicants credit history
- Rationale: Needs a 12-month third-party-payment history (contingent-liability co-obligor, cosigner, or authorized-user account owner) -- `urla_liabilities`/`tradelines` capture the liability itself but not who else has been paying it or for how long; no such payment-history document exists in this corpus.
- What's needed: -

**credit-liabilities-review:110** (1 rules)
- Condition: Credit report for non-purchase spouse not obtained in community property state for DTI analysis
- Rationale: A second credit report (the non-borrowing/non-purchasing spouse's) plus the applicable state's community-property statute reference -- neither exists in this corpus; every loan extracts exactly one applicant-side credit report at most.
- What's needed: -

**credit-liabilities-review:111** (1 rules)
- Condition: Loan approved with delinquent federal non-tax debt without determining if account has been resolved
- Rationale: Federal debt / delinquent federal (tax or non-tax) obligation documentation (repayment status, CAIVRS-adjacent) -- not modeled beyond loan 02's CAIVRS/LDP/GSA screenprint (a different, narrower fact).
- What's needed: -

**credit-liabilities-review:112** (1 rules)
- Condition: Loan/deductions listed on the paystubs were not addressed
- Rationale: Verified against the actual synthetic paystub (loan 01, `03_Paystub_Most_Recent.pdf`): its Deductions section lists only standard tax withholdings (Federal Withholding, Social Security, Medicare, NC State Tax) -- no loan-type deduction or military allotment line appears in any paystub in this corpus. Genuine Bucket-A-style fixture gap (the paystub doc type exists; the specific line item this rule needs does not), not a Bucket-B extraction-deepening candidate -- there is nothing yet to extract.
- What's needed: -

**credit-liabilities-review:113** (1 rules)
- Condition: Manual UW with a credit score below 680 did not verify 12 mos verification of rent as applicable
- Rationale: Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- What's needed: -

**credit-liabilities-review:114** (1 rules)
- Condition: Recent non-disclosed significant debt on the credit report was not explained by the applicant(s)
- Rationale: MISCLASSIFIED (matched 'was not' + 'credit report' keyword) -- same direction as UndisclosedLiabilityShape's real condition plus a borrower-explanation requirement, same family/caution as O-RHS-50563 above.
- What's needed: -

**credit-liabilities-review:115** (1 rules)
- Condition: Report has significant debt not on 1003 w/out explanation or added to DTI
- Rationale: MISCLASSIFIED (matched 'was not provided'/'not added' + 'credit report' keyword) -- same direction as UndisclosedLiabilityShape's real condition (credit report shows a debt the 1003 doesn't), but bundles an extra explanation/DTI-inclusion requirement our shape doesn't test -- same caution as the F_UNDISCLOSED_DEBT family and decision 019's verdict on that shape.
- What's needed: -

**credit-liabilities-review:116** (1 rules)
- Condition: Significant debt not considered by GUS & payment not added/loan resubmitted
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**credit-liabilities-review:117** (1 rules)
- Condition: There are federal income taxes due on the current year tax return and proof paid has not been obtain
- Rationale: Current-year tax return + proof-of-payment documentation -- not a doc type in this corpus (identical condition text recurs across FHA/FRD/RHS/VA/FNM -- a single fixture gap, not five separate ones).
- What's needed: -

**credit-liabilities-review:118** (1 rules)
- Condition: Undisclosed debt not on the application but found during processing not manually entered into GUS
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**credit-liabilities-review:120** (1 rules)
- Condition: Bankruptcy in TOTAL credit report did not meet discharge time req's & was not downgraded to Refer
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**credit-liabilities-review:122** (1 rules)
- Condition: Applicant(s) housing pay history for at least the prior 12-months is not documented
- Rationale: Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- What's needed: -

**credit-liabilities-review:123** (1 rules)
- Condition: Inquiry in last 90 days did not document if new debt opened and/or new debt not considered in ratio
- Rationale: PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- What's needed: -

**credit-liabilities-review:124** (1 rules)
- Condition: No verification was obtained by the creditor on accounts that only rate via mail with authorization
- Rationale: 'Will rate by mail only'/'need written authorization' accounts need a separate written-verification document per account -- not a doc type this corpus models (the one credit report's tradelines don't carry a rate-by-mail flag either).
- What's needed: -

**credit-liabilities-review:125** (1 rules)
- Condition: Significant open debt from URLA is missing credit reference w/out a separate written verification
- Rationale: MISCLASSIFIED (matched 'is missing' + 'credit report' keyword) -- the real condition is the REVERSE direction of UndisclosedLiabilityShape (a 1003 debt missing from the credit report, needing a separate written verification document), same family as F_APPLICATION_DEBT_NOT_ON_CREDIT elsewhere in this block -- not itself a credit-report-presence fact.
- What's needed: -

**credit-liabilities-review:127** (1 rules)
- Condition: RMCR does not reflect a reporting status <= 90 days of the report date for accounts with balances
- Rationale: Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- What's needed: -

**credit-liabilities-review:128** (1 rules)
- Condition: The RMCR does not list all inquiries made within the previous 90 days
- Rationale: Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- What's needed: -

**credit-liabilities-review:129** (1 rules)
- Condition: The credit report was expired at the time of closing
- Rationale: Bucket-B-close: the synthetic credit report's own text already shows 'Report Date 07/29/2025' (loan 01) and `closing_date` is already extracted from the closing disclosure -- a days-elapsed comparison is crisp arithmetic once `report_date` joins FIELD_SPECS['credit_report']. Not fully ready: the expiration threshold itself is agency-specific (RHS states 120 days explicitly; VA's 'expired' needs its own Guide-cited day count) and needs an SME/guide citation before hardcoding, not just a new field.
- What's needed: -

**credit-liabilities-review:133** (1 rules)
- Condition: Determination of new debt from inquiries reported within 90-days of closing is not documented
- Rationale: Needs a parsed Inquiries table (already visible in the loan 01 credit report's text -- 'Inquiries (last 120 days)' with Date/Bureau/Requesting Party -- but not yet in FIELD_SPECS/entities) cross-referenced against whether new debt was opened; Bucket-B-style (deepen extraction of a section already present in the one document we have), not a missing document.
- What's needed: -

**credit-liabilities-review:135** (1 rules)
- Condition: Housing payments for the last 12 months were not verified with acceptable documentation
- Rationale: Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- What's needed: -

**credit-liabilities-review:136** (1 rules)
- Condition: RMCR does not reflect a reporting status <= 90 days of the report date for accounts with balances
- Rationale: Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- What's needed: -

**credit-liabilities-review:137** (1 rules)
- Condition: The appropriate rep credit score not used with scores of 640 or greater
- Rationale: Deepen `credit_report` FIELD_SPECS: the doc's own text already shows 'Middle Score — Borrower 742' / 'Middle Score — Co-Borrower 758' (loan 01) but no score field is parsed today. Even once parsed, applying these rules needs a per-program minimum-score / representative-score-selection table that is a Selling-Guide business rule, not a fact derivable from any loan document -- Bucket-B on the extraction side, still needs an SME-sourced threshold table beyond that.
- What's needed: -

**credit-liabilities-review:138** (1 rules)
- Condition: The credit report was over 120 days old when the loan closed
- Rationale: Bucket-B-close: the synthetic credit report's own text already shows 'Report Date 07/29/2025' (loan 01) and `closing_date` is already extracted from the closing disclosure -- a days-elapsed comparison is crisp arithmetic once `report_date` joins FIELD_SPECS['credit_report']. Not fully ready: the expiration threshold itself is agency-specific (RHS states 120 days explicitly; VA's 'expired' needs its own Guide-cited day count) and needs an SME/guide citation before hardcoding, not just a new field.
- What's needed: -

**credit-liabilities-review:139** (1 rules)
- Condition: The necessary analysis to validate the credit score is usable for underwriting the loan is missing
- Rationale: Deepen `credit_report` FIELD_SPECS: the doc's own text already shows 'Middle Score — Borrower 742' / 'Middle Score — Co-Borrower 758' (loan 01) but no score field is parsed today. Even once parsed, applying these rules needs a per-program minimum-score / representative-score-selection table that is a Selling-Guide business rule, not a fact derivable from any loan document -- Bucket-B on the extraction side, still needs an SME-sourced threshold table beyond that.
- What's needed: -

**credit-liabilities-review:141** (1 rules)
- Condition: A borrower has more than one of the national credit repositories with frozen credit information
- Rationale: Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- What's needed: -

**credit-liabilities-review:142** (1 rules)
- Condition: Credit Alerts/Hawk Alerts &/or additional addresses have not been addressed and/or documented
- Rationale: Hawk Alert / Other Credit Alert flag -- this attribute doesn't appear anywhere in the one synthetic credit report's text; not modeled, not merely unextracted.
- What's needed: -

**credit-liabilities-review:143** (1 rules)
- Condition: Credit report not an original with all required identifying information &/or alterations noted
- Rationale: Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- What's needed: -

**credit-liabilities-review:144** (1 rules)
- Condition: Credit report used was not a hard pull generating an inquiry identified on subsequent credit reports
- Rationale: Needs a parsed Inquiries table (already visible in the loan 01 credit report's text -- 'Inquiries (last 120 days)' with Date/Bureau/Requesting Party -- but not yet in FIELD_SPECS/entities) cross-referenced against whether new debt was opened; Bucket-B-style (deepen extraction of a section already present in the one document we have), not a missing document.
- What's needed: -

**credit-liabilities-review:145** (1 rules)
- Condition: Credit reports do not meet RMCR standards &/or if multi reports, not all credit reports in the file
- Rationale: Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- What's needed: -

**credit-liabilities-review:146** (1 rules)
- Condition: DU loan does not contain a three-in-file merged credit report for each applicant
- Rationale: MISCLASSIFIED (matched 'not in the file' + 'credit report' keyword) -- Bucket-B-close, not a bare presence check: loan 01's synthetic credit report IS explicitly titled 'Tri-Merge Credit Report Summary — Bureaus: Equifax / Experian / TransUnion,' so the underlying fact may already be true in text, but no is_tri_merge / bureau-count field is parsed by FIELD_SPECS today -- needs extraction, not just a presence flag.
- What's needed: -

**credit-liabilities-review:147** (1 rules)
- Condition: Data entered into DU is inaccurate based on credit report/other credit documentation
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**credit-liabilities-review:148** (1 rules)
- Condition: Disputed account reported and DU has a disputed message that was not documented as resolved
- Rationale: MISCLASSIFIED (matched 'not documented' + 'credit report' keyword) -- the real condition needs DU's own disputed-account message/resolution record, part of the same AUS-feedback-certificate gap as the F_AUS_EXPORT family (no DU export doc exists in this corpus).
- What's needed: -

**credit-liabilities-review:149** (1 rules)
- Condition: Identifying info incorrect on credit report w/out credit being re-requested
- Rationale: Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- What's needed: -

**credit-liabilities-review:150** (1 rules)
- Condition: New or changes in the debts were noted but not resubmitted to the AUS
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**credit-liabilities-review:151** (1 rules)
- Condition: Non-traditional credit was used; sufficient number of credit references warrants traditional credit
- Rationale: Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- What's needed: -

**credit-liabilities-review:152** (1 rules)
- Condition: Not all info from at least 2 repositories for credit, residence history & public records shown
- Rationale: Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- What's needed: -

**credit-liabilities-review:153** (1 rules)
- Condition: Positive statement that the applicant's employment and income verification was attempted is missing
- Rationale: MISCLASSIFIED (matched 'did not confirm' + 'credit report' keyword) -- the real condition is whether the credit report documents that the reporting agency attempted employment/income verification, an RMCR-format field this pilot's synthetic credit report doesn't model at all.
- What's needed: -

**credit-liabilities-review:154** (1 rules)
- Condition: Prior housing history are not reported and verifications were not obtained for rental/mortgages
- Rationale: Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- What's needed: -

**credit-liabilities-review:155** (1 rules)
- Condition: RMCR does not reflect a reporting status <= 90 days of the report date for accounts with balances
- Rationale: Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- What's needed: -

**credit-liabilities-review:156** (1 rules)
- Condition: The borr's present address not within the U.S. or military address and was not manually underwritten
- Rationale: Needs a borrower current-address country/military-address classification -- `final_1003` extraction captures identity/employment/loan fields today, not a structured current-address country flag.
- What's needed: -

**credit-liabilities-review:157** (1 rules)
- Condition: The credit report does not include the required credit information for each debt shown
- Rationale: Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- What's needed: -

**credit-liabilities-review:158** (1 rules)
- Condition: The credit report submitted to LPA did not include trended credit data
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**credit-liabilities-review:159** (1 rules)
- Condition: The report in the file is not  in the proper format with required information and/or appears altered
- Rationale: Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- What's needed: -

**credit-liabilities-review:162** (1 rules)
- Condition: Credit scores used for eligibility in higher risk products did not meet the required minimum
- Rationale: Deepen `credit_report` FIELD_SPECS: the doc's own text already shows 'Middle Score — Borrower 742' / 'Middle Score — Co-Borrower 758' (loan 01) but no score field is parsed today. Even once parsed, applying these rules needs a per-program minimum-score / representative-score-selection table that is a Selling-Guide business rule, not a fact derivable from any loan document -- Bucket-B on the extraction side, still needs an SME-sourced threshold table beyond that.
- What's needed: -

**credit-liabilities-review:164** (1 rules)
- Condition: Minimum credit score requirements were not met
- Rationale: Deepen `credit_report` FIELD_SPECS: the doc's own text already shows 'Middle Score — Borrower 742' / 'Middle Score — Co-Borrower 758' (loan 01) but no score field is parsed today. Even once parsed, applying these rules needs a per-program minimum-score / representative-score-selection table that is a Selling-Guide business rule, not a fact derivable from any loan document -- Bucket-B on the extraction side, still needs an SME-sourced threshold table beyond that.
- What's needed: -

**credit-liabilities-review:165** (1 rules)
- Condition: Representative or average median score not used as req'd per number of borrowers in a manual UW
- Rationale: Deepen `credit_report` FIELD_SPECS: the doc's own text already shows 'Middle Score — Borrower 742' / 'Middle Score — Co-Borrower 758' (loan 01) but no score field is parsed today. Even once parsed, applying these rules needs a per-program minimum-score / representative-score-selection table that is a Selling-Guide business rule, not a fact derivable from any loan document -- Bucket-B on the extraction side, still needs an SME-sourced threshold table beyond that.
- What's needed: -

**credit-liabilities-review:166** (1 rules)
- Condition: The appropriate credit score was not used to analyze the applicant(s) credit reputation
- Rationale: Deepen `credit_report` FIELD_SPECS: the doc's own text already shows 'Middle Score — Borrower 742' / 'Middle Score — Co-Borrower 758' (loan 01) but no score field is parsed today. Even once parsed, applying these rules needs a per-program minimum-score / representative-score-selection table that is a Selling-Guide business rule, not a fact derivable from any loan document -- Bucket-B on the extraction side, still needs an SME-sourced threshold table beyond that.
- What's needed: -

**credit-liabilities-review:167** (1 rules)
- Condition: The incorrect representative credit score was used in a manually underwritten loan
- Rationale: Deepen `credit_report` FIELD_SPECS: the doc's own text already shows 'Middle Score — Borrower 742' / 'Middle Score — Co-Borrower 758' (loan 01) but no score field is parsed today. Even once parsed, applying these rules needs a per-program minimum-score / representative-score-selection table that is a Selling-Guide business rule, not a fact derivable from any loan document -- Bucket-B on the extraction side, still needs an SME-sourced threshold table beyond that.
- What's needed: -

**credit-liabilities-review:169** (1 rules)
- Condition: Undisclosed debt discovered and the actual payment amount was not verified and included in DTI
- Rationale: Closest textual match to the already-mapped (but zero-exception-code) `UndisclosedLiabilityShape` (credit-report tradeline with no matching 1003 Section 2c liability) -- verified NOT a safe direct wire (decision 019): this row bundles an additional requirement (borrower explanation obtained, and/or the payment verified and included in DTI) our shape doesn't test. Wiring it as-is would risk false negatives on loans where the undisclosed debt is present but the compound condition isn't met, or false positives once the explanation-documentation piece is added and our shape can't see it. Kept YELLOW pending that extra logic being built.
- What's needed: -

**credit-liabilities-review:171** (1 rules)
- Condition: Loan approved with DTI over 36% and borrower does not meet credit and reserve requirements
- Rationale: PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- What's needed: -

**credit-liabilities-review:172** (1 rules)
- Condition: Not re-underwritten where additional debt or reduced income caused DTI to increase beyond tolerance
- Rationale: PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- What's needed: -

**credit-liabilities-review:174** (1 rules)
- Condition: A contingent liability or co-signed obligation was not  included in ratios
- Rationale: Needs a 12-month third-party-payment history (contingent-liability co-obligor, cosigner, or authorized-user account owner) -- `urla_liabilities`/`tradelines` capture the liability itself but not who else has been paying it or for how long; no such payment-history document exists in this corpus.
- What's needed: -

**credit-liabilities-review:175** (1 rules)
- Condition: A significant debt on the 1003 is not reported and verification of liability is missing
- Rationale: MISCLASSIFIED (matched 'is not reported' + 'credit report' keyword) -- same reverse-direction family as O-FRD-00174 (F_APPLICATION_DEBT_NOT_ON_CREDIT), not a credit-report-presence fact.
- What's needed: -

**credit-liabilities-review:176** (1 rules)
- Condition: An undisclosed debt was noted or discovered but an explanation was not obtained from the borrower
- Rationale: Closest textual match to the already-mapped (but zero-exception-code) `UndisclosedLiabilityShape` (credit-report tradeline with no matching 1003 Section 2c liability) -- verified NOT a safe direct wire (decision 019): this row bundles an additional requirement (borrower explanation obtained, and/or the payment verified and included in DTI) our shape doesn't test. Wiring it as-is would risk false negatives on loans where the undisclosed debt is present but the compound condition isn't met, or false positives once the explanation-documentation piece is added and our shape can't see it. Kept YELLOW pending that extra logic being built.
- What's needed: -

**credit-liabilities-review:177** (1 rules)
- Condition: Debts did not include child care (to age 12), significant commutes, &/or costs related to employment
- Rationale: VA job-related-expense debt (child care, commute costs) documentation -- not a doc type or field this corpus's single VA loan (03) models.
- What's needed: -

**credit-liabilities-review:178** (1 rules)
- Condition: Loan/deductions listed on the paystubs were not addressed
- Rationale: Verified against the actual synthetic paystub (loan 01, `03_Paystub_Most_Recent.pdf`): its Deductions section lists only standard tax withholdings (Federal Withholding, Social Security, Medicare, NC State Tax) -- no loan-type deduction or military allotment line appears in any paystub in this corpus. Genuine Bucket-A-style fixture gap (the paystub doc type exists; the specific line item this rule needs does not), not a Bucket-B extraction-deepening candidate -- there is nothing yet to extract.
- What's needed: -

**credit-liabilities-review:179** (1 rules)
- Condition: No verification was obtained by the creditor on accounts that only rate via mail with authorization
- Rationale: 'Will rate by mail only'/'need written authorization' accounts need a separate written-verification document per account -- not a doc type this corpus models (the one credit report's tradelines don't carry a rate-by-mail flag either).
- What's needed: -

**credit-liabilities-review:180** (1 rules)
- Condition: Paystub/LES has an allotment without documenting it is related to a debt or other obligation(s)
- Rationale: Verified against the actual synthetic paystub (loan 01, `03_Paystub_Most_Recent.pdf`): its Deductions section lists only standard tax withholdings (Federal Withholding, Social Security, Medicare, NC State Tax) -- no loan-type deduction or military allotment line appears in any paystub in this corpus. Genuine Bucket-A-style fixture gap (the paystub doc type exists; the specific line item this rule needs does not), not a Bucket-B extraction-deepening candidate -- there is nothing yet to extract.
- What's needed: -

**credit-liabilities-review:181** (1 rules)
- Condition: Student loan(s) and correct monthly payment not used in analysis
- Rationale: Student-loan payment-substitution math (0.5%/1% of balance when the credit report shows a $0 or missing payment) is crisp arithmetic, and `extract_tradelines()` already captures tradeline type/balance/monthly_payment (loan 01 has one Student tradeline) -- but verifying which qualifying-payment value the lender ACTUALLY used needs a DTI/qualifying-payment worksheet this pilot doesn't extract or derive from any document today. Trigger-detection is Bucket-B-close; the verification half is not.
- What's needed: -

**credit-liabilities-review:182** (1 rules)
- Condition: Student loan(s) with payments due within 12 months of approval were not included in ratios
- Rationale: Student-loan payment-substitution math (0.5%/1% of balance when the credit report shows a $0 or missing payment) is crisp arithmetic, and `extract_tradelines()` already captures tradeline type/balance/monthly_payment (loan 01 has one Student tradeline) -- but verifying which qualifying-payment value the lender ACTUALLY used needs a DTI/qualifying-payment worksheet this pilot doesn't extract or derive from any document today. Trigger-detection is Bucket-B-close; the verification half is not.
- What's needed: -

**credit-liabilities-review:183** (1 rules)
- Condition: The non-borrowing veteran's spouse’s debts not considered in a community property state
- Rationale: A second credit report (the non-borrowing/non-purchasing spouse's) plus the applicable state's community-property statute reference -- neither exists in this corpus; every loan extracts exactly one applicant-side credit report at most.
- What's needed: -

**credit-liabilities-review:186** (1 rules)
- Condition: Debt paid off or paid down to qualify & source/sufficient assets remain for the loan not provided
- Rationale: Needs a source-of-funds-for-payoff cross-reference against remaining total assets -- `payoff_amount_1003`/`cash_out_to_borrower_1003` and `bank_txns` exist independently, but the specific 'paid down solely to qualify, sufficient assets remain' derivation isn't built; related to asset-verification's net-sale-proceeds family (G004/G005).
- What's needed: -

**credit-liabilities-review:187** (1 rules)
- Condition: Documentation of assets to cover a 30-day account, in excess of reserves/closing funds, is missing
- Rationale: MISCLASSIFIED by amq_compiler.py's mechanical doc_presence rule (matched 'in excess' + 'credit report' keyword) -- the real condition is asset-sufficiency to cover a flagged 30-day account beyond reserves/closing funds, not credit-report presence. Needs a cross-reference of the flagged tradeline balance against total available assets (bank_txns) and reserve/closing-cost fields -- not yet derived anywhere in extract_loan.py.
- What's needed: -

**credit-liabilities-review:192** (1 rules)
- Condition: A deferred obligation was not documented with the balance and terms from the creditor as required
- Rationale: Student-loan payment-substitution math (0.5%/1% of balance when the credit report shows a $0 or missing payment) is crisp arithmetic, and `extract_tradelines()` already captures tradeline type/balance/monthly_payment (loan 01 has one Student tradeline) -- but verifying which qualifying-payment value the lender ACTUALLY used needs a DTI/qualifying-payment worksheet this pilot doesn't extract or derive from any document today. Trigger-detection is Bucket-B-close; the verification half is not.
- What's needed: -

**credit-liabilities-review:204** (1 rules)
- Condition: Credit Alerts/Hawk Alerts &/or additional addresses have not been addressed and/or documented
- Rationale: Hawk Alert / Other Credit Alert flag -- this attribute doesn't appear anywhere in the one synthetic credit report's text; not modeled, not merely unextracted.
- What's needed: -

**credit-liabilities-review:205** (1 rules)
- Condition: Documentation of significant derog credit reporting error not in file
- Rationale: MISCLASSIFIED (matched 'not supported' + 'credit report' keyword) -- the real condition needs a credit-supplement/dispute-resolution document family, same as the F_DEROG_HISTORY YELLOW family elsewhere in this block, not in this corpus.
- What's needed: -

**credit-liabilities-review:207** (1 rules)
- Condition: The UW did not reconcile discrepancies between the credit report and the 1003 as required by DU
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**credit-liabilities-review:208** (1 rules)
- Condition: A delinquent/defaulted Federal debt & no documentation it is now current or is being repaid
- Rationale: Federal debt / delinquent federal (tax or non-tax) obligation documentation (repayment status, CAIVRS-adjacent) -- not modeled beyond loan 02's CAIVRS/LDP/GSA screenprint (a different, narrower fact).
- What's needed: -

**credit-liabilities-review:209** (1 rules)
- Condition: Federal debt under repayment agreement was not documented or included in the DTI
- Rationale: Federal debt / delinquent federal (tax or non-tax) obligation documentation (repayment status, CAIVRS-adjacent) -- not modeled beyond loan 02's CAIVRS/LDP/GSA screenprint (a different, narrower fact).
- What's needed: -

**credit-liabilities-review:210** (1 rules)
- Condition: No evidence Vet asked at application if are, have, or will receive disability as per Search Reqm't
- Rationale: Federal debt / delinquent federal (tax or non-tax) obligation documentation (repayment status, CAIVRS-adjacent) -- not modeled beyond loan 02's CAIVRS/LDP/GSA screenprint (a different, narrower fact).
- What's needed: -

**credit-liabilities-review:212** (1 rules)
- Condition: There are federal income taxes due on the current year tax return and proof paid has not been obtain
- Rationale: Federal debt / delinquent federal (tax or non-tax) obligation documentation (repayment status, CAIVRS-adjacent) -- not modeled beyond loan 02's CAIVRS/LDP/GSA screenprint (a different, narrower fact).
- What's needed: -

**credit-liabilities-review:216** (1 rules)
- Condition: Loan approval does not evidence exception for foreclosure/deed-in-reported within 3 years
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**credit-liabilities-review:218** (1 rules)
- Condition: Excluded cosigned liability without evidence the other party has made timely pymts the last 12 mos
- Rationale: Needs a 12-month third-party-payment history (contingent-liability co-obligor, cosigner, or authorized-user account owner) -- `urla_liabilities`/`tradelines` capture the liability itself but not who else has been paying it or for how long; no such payment-history document exists in this corpus.
- What's needed: -

**credit-liabilities-review:219** (1 rules)
- Condition: Lease payment(s) excluded from total monthly debt, regardless of lease term remaining
- Rationale: Needs a lease/HELOC/timeshare/solar-panel-agreement/virtual-currency-secured-loan document -- none of these niche liability-collateral document types exist in this corpus (same 'document family the synthetic corpus never modeled' pattern as several asset-verification YELLOW groups).
- What's needed: -

**credit-liabilities-review:220** (1 rules)
- Condition: Source of funds to pay off debts PTC not documented, were unacceptable &/or new debt not in DTI
- Rationale: PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- What's needed: -

**credit-liabilities-review:222** (1 rules)
- Condition: Housing delinquency within last 12 mos on TOTAL credit report and was not downgraded to a Refer
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**credit-liabilities-review:224** (1 rules)
- Condition: PITIA of all properties owned by the borrower were not included in DTI as applicable
- Rationale: PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- What's needed: -

**credit-liabilities-review:225** (1 rules)
- Condition: Installment loan with payment in the credit report/loan agreement/statement is excluded from DTI
- Rationale: The percentage-of-balance math (5%/1.5%/0.5% thresholds) is crisp arithmetic once the relevant balance is in hand, and `extract_tradelines()` already captures type/balance/monthly_payment per tradeline -- but confirming whether the LENDER actually included the computed amount in the final DTI needs a DTI worksheet this pilot doesn't derive (same gap as F_PITIA_DTI_REO); and month-by-month late-payment-in-12-months detection needs payment-history depth the tradeline snapshot (a single current 'Status' value) doesn't carry. Trigger data partly in hand; verification math not yet built.
- What's needed: -

**credit-liabilities-review:240** (1 rules)
- Condition: Alt source for noncredit accounts did not use allowable documentation to verify pay history
- Rationale: Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- What's needed: -

**credit-liabilities-review:241** (1 rules)
- Condition: At least 1 qualifying borr did not meet minimum trad/non trad credit req's
- Rationale: Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- What's needed: -

**credit-liabilities-review:242** (1 rules)
- Condition: Auth user act considered w/out evidence co-borr/spouse owns it or borr paid last 12 mos & is in DTI
- Rationale: Needs a 12-month third-party-payment history (contingent-liability co-obligor, cosigner, or authorized-user account owner) -- `urla_liabilities`/`tradelines` capture the liability itself but not who else has been paying it or for how long; no such payment-history document exists in this corpus.
- What's needed: -

**credit-liabilities-review:243** (1 rules)
- Condition: Non-traditional credit used, completion homeownership education not in file
- Rationale: Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- What's needed: -

**credit-liabilities-review:244** (1 rules)
- Condition: The UW did not used the FICO scores with accompanying reason codes
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**credit-liabilities-review:245** (1 rules)
- Condition: The UW used factors reflected in the FICO score to offset the weaknesses in credit reputation
- Rationale: Deepen `credit_report` FIELD_SPECS: the doc's own text already shows 'Middle Score — Borrower 742' / 'Middle Score — Co-Borrower 758' (loan 01) but no score field is parsed today. Even once parsed, applying these rules needs a per-program minimum-score / representative-score-selection table that is a Selling-Guide business rule, not a fact derivable from any loan document -- Bucket-B on the extraction side, still needs an SME-sourced threshold table beyond that.
- What's needed: -

**credit-liabilities-review:252** (1 rules)
- Condition: Satisfactory payment history/counseling agency approval missing for credit counseling participants
- Rationale: Consumer credit counseling program enrollment/payout/agency-approval document -- not a doc type in this corpus.
- What's needed: -

**credit-liabilities-review:253** (1 rules)
- Condition: Debt excluded, will not payoff in 10 mos or cumulative pymts exceed 5% of gross monthly income
- Rationale: The percentage-of-balance math (5%/1.5%/0.5% thresholds) is crisp arithmetic once the relevant balance is in hand, and `extract_tradelines()` already captures type/balance/monthly_payment per tradeline -- but confirming whether the LENDER actually included the computed amount in the final DTI needs a DTI worksheet this pilot doesn't derive (same gap as F_PITIA_DTI_REO); and month-by-month late-payment-in-12-months detection needs payment-history depth the tradeline snapshot (a single current 'Status' value) doesn't carry. Trigger data partly in hand; verification math not yet built.
- What's needed: -

**credit-liabilities-review:254** (1 rules)
- Condition: Determination of new debt from inquiries reported within 90-days of closing is not documented
- Rationale: Needs a parsed Inquiries table (already visible in the loan 01 credit report's text -- 'Inquiries (last 120 days)' with Date/Bureau/Requesting Party -- but not yet in FIELD_SPECS/entities) cross-referenced against whether new debt was opened; Bucket-B-style (deepen extraction of a section already present in the one document we have), not a missing document.
- What's needed: -

**credit-liabilities-review:256** (1 rules)
- Condition: Undisclosed debt discovered and the actual payment amount was not verified and included in DTI
- Rationale: Closest textual match to the already-mapped (but zero-exception-code) `UndisclosedLiabilityShape` (credit-report tradeline with no matching 1003 Section 2c liability) -- verified NOT a safe direct wire (decision 019): this row bundles an additional requirement (borrower explanation obtained, and/or the payment verified and included in DTI) our shape doesn't test. Wiring it as-is would risk false negatives on loans where the undisclosed debt is present but the compound condition isn't met, or false positives once the explanation-documentation piece is added and our shape can't see it. Kept YELLOW pending that extra logic being built.
- What's needed: -

**credit-liabilities-review:262** (1 rules)
- Condition: The housing payment history for the most recent 12 months was not determined and verified
- Rationale: Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- What's needed: -

**credit-liabilities-review:266** (1 rules)
- Condition: Credit report does not reflect creditor reporting status is w/in 90 days for accounts with balances
- Rationale: Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- What's needed: -

**credit-liabilities-review:267** (1 rules)
- Condition: Manual credit report did not meet all req's &/or did not show all req'd information for each borr
- Rationale: Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- What's needed: -

**credit-liabilities-review:268** (1 rules)
- Condition: No credit score and non-traditional credit and/or verification of credit references is missing
- Rationale: MISCLASSIFIED (matched 'did not meet' + 'credit report' keyword) -- same non-traditional-credit-report family as F_NONTRAD_VOR elsewhere in this block, not a bare presence check.
- What's needed: -

**credit-liabilities-review:270** (1 rules)
- Condition: All housing/installment pmts not on time last 12 mths or had over 2 30 day late pmts in last 24 mths
- Rationale: The percentage-of-balance math (5%/1.5%/0.5% thresholds) is crisp arithmetic once the relevant balance is in hand, and `extract_tradelines()` already captures type/balance/monthly_payment per tradeline -- but confirming whether the LENDER actually included the computed amount in the final DTI needs a DTI worksheet this pilot doesn't derive (same gap as F_PITIA_DTI_REO); and month-by-month late-payment-in-12-months detection needs payment-history depth the tradeline snapshot (a single current 'Status' value) doesn't carry. Trigger data partly in hand; verification math not yet built.
- What's needed: -

**credit-liabilities-review:271** (1 rules)
- Condition: Documentation of significant late payments resulting from extenuating circumstances is missing
- Rationale: MISCLASSIFIED (matched 'not adequately document' + 'credit report' keyword) -- the real condition needs an explanation-of-delinquency document establishing extenuating circumstances, a doc type this corpus doesn't have; presence of such a letter would be crisp once it exists, 'adequately' stays a partial human check.
- What's needed: -

**credit-liabilities-review:275** (1 rules)
- Condition: A debt paid by someone other than the borrower was excluded without a 12 month timely pay history
- Rationale: PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- What's needed: -

**credit-liabilities-review:276** (1 rules)
- Condition: AUS loan with alimony pymts reducing income in lieu of debt not in DU as own negative amt line item
- Rationale: Divorce decree / court order / separation agreement documenting alimony, child support, or maintenance payment terms -- not a doc type in this corpus.
- What's needed: -

**credit-liabilities-review:277** (1 rules)
- Condition: Alimony, child support, or maintenance payments with over 10 months left was not considered in DTI
- Rationale: Divorce decree / court order / separation agreement documenting alimony, child support, or maintenance payment terms -- not a doc type in this corpus.
- What's needed: -

**credit-liabilities-review:278** (1 rules)
- Condition: Asset secured loan is not included in DTI or a copy of the Note reflecting the collateral is missing
- Rationale: Needs a lease/HELOC/timeshare/solar-panel-agreement/virtual-currency-secured-loan document -- none of these niche liability-collateral document types exist in this corpus (same 'document family the synthetic corpus never modeled' pattern as several asset-verification YELLOW groups).
- What's needed: -

**credit-liabilities-review:279** (1 rules)
- Condition: Business debt(s) not included in DTI or documentation debt(s) is paid by the business is missing
- Rationale: MISCLASSIFIED (matched 'not included'/'not documented' + 'credit report' keyword) -- the real condition is whether a business debt on the personal credit report is documented as company-paid and excluded from DTI accordingly. Needs a business-debt-payment documentation type this corpus doesn't have, plus DTI-inclusion logic not yet built.
- What's needed: -

**credit-liabilities-review:280** (1 rules)
- Condition: Deferred non-student loan installment debt(s)/no payment is not documented and/or included in DTI
- Rationale: Mortgage forbearance/modification-plan document (terms, consecutive-payment count since granted) -- not a doc type in this corpus.
- What's needed: -

**credit-liabilities-review:281** (1 rules)
- Condition: Deferred/forbearance student loan with no pymt reported & 1% of balance or documented pymt not used
- Rationale: Mortgage forbearance/modification-plan document (terms, consecutive-payment count since granted) -- not a doc type in this corpus.
- What's needed: -

**credit-liabilities-review:282** (1 rules)
- Condition: Divorce decree or equivalent not in file to document alimony, child support, or maintenance payments
- Rationale: Divorce decree / court order / separation agreement documenting alimony, child support, or maintenance payment terms -- not a doc type in this corpus.
- What's needed: -

**credit-liabilities-review:283** (1 rules)
- Condition: Lease payment(s) excluded from total monthly debt, regardless of lease term remaining
- Rationale: Needs a lease/HELOC/timeshare/solar-panel-agreement/virtual-currency-secured-loan document -- none of these niche liability-collateral document types exist in this corpus (same 'document family the synthetic corpus never modeled' pattern as several asset-verification YELLOW groups).
- What's needed: -

**credit-liabilities-review:284** (1 rules)
- Condition: Loans/deductions listed on the paystubs were not addressed
- Rationale: Verified against the actual synthetic paystub (loan 01, `03_Paystub_Most_Recent.pdf`): its Deductions section lists only standard tax withholdings (Federal Withholding, Social Security, Medicare, NC State Tax) -- no loan-type deduction or military allotment line appears in any paystub in this corpus. Genuine Bucket-A-style fixture gap (the paystub doc type exists; the specific line item this rule needs does not), not a Bucket-B extraction-deepening candidate -- there is nothing yet to extract.
- What's needed: -

**credit-liabilities-review:286** (1 rules)
- Condition: There are federal income taxes due on the current year tax return and proof paid has not been obtain
- Rationale: Current-year tax return + proof-of-payment documentation -- not a doc type in this corpus (identical condition text recurs across FHA/FRD/RHS/VA/FNM -- a single fixture gap, not five separate ones).
- What's needed: -

**credit-liabilities-review:287** (1 rules)
- Condition: 1.5% of HELOC balance not used & monthly pymt amt not documented in the file or credit report
- Rationale: Needs a lease/HELOC/timeshare/solar-panel-agreement/virtual-currency-secured-loan document -- none of these niche liability-collateral document types exist in this corpus (same 'document family the synthetic corpus never modeled' pattern as several asset-verification YELLOW groups).
- What's needed: -

**credit-liabilities-review:288** (1 rules)
- Condition: 30 day account balance not added to DTI & funds to cover the account, closing/reserves not verified
- Rationale: PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- What's needed: -

**credit-liabilities-review:289** (1 rules)
- Condition: Asset secured loan is not included in DTI or a copy of the Note reflecting the collateral is missing
- Rationale: Needs a lease/HELOC/timeshare/solar-panel-agreement/virtual-currency-secured-loan document -- none of these niche liability-collateral document types exist in this corpus (same 'document family the synthetic corpus never modeled' pattern as several asset-verification YELLOW groups).
- What's needed: -

**credit-liabilities-review:290** (1 rules)
- Condition: Child support payments are not in DTI and required documentation is missing
- Rationale: Divorce decree / court order / separation agreement documenting alimony, child support, or maintenance payment terms -- not a doc type in this corpus.
- What's needed: -

**credit-liabilities-review:291** (1 rules)
- Condition: Current primary pending sale after Note date-executed sale contract missing
- Rationale: Executed sales contract for a pending sale of the borrower's current residence -- not a doc type in this corpus; related to asset-verification's prior-home-sale settlement-statement family (G004/G005/G033).
- What's needed: -

**credit-liabilities-review:292** (1 rules)
- Condition: Lease payment(s) excluded from total monthly debt, regardless of lease term remaining
- Rationale: Needs a lease/HELOC/timeshare/solar-panel-agreement/virtual-currency-secured-loan document -- none of these niche liability-collateral document types exist in this corpus (same 'document family the synthetic corpus never modeled' pattern as several asset-verification YELLOW groups).
- What's needed: -

**credit-liabilities-review:293** (1 rules)
- Condition: Monthly payments on debts secured by cryptocurrency was not included in the DTI ratio
- Rationale: Needs a lease/HELOC/timeshare/solar-panel-agreement/virtual-currency-secured-loan document -- none of these niche liability-collateral document types exist in this corpus (same 'document family the synthetic corpus never modeled' pattern as several asset-verification YELLOW groups).
- What's needed: -

**credit-liabilities-review:294** (1 rules)
- Condition: Non-Student/IRS installment debt not on credit report or in deferred/forbearance, missing pymt verif
- Rationale: MISCLASSIFIED (matched 'not report' + 'credit report' keyword) -- needs a deferred/forbearance status flag per tradeline and a separate payment-verification document; `extract_tradelines()` doesn't model either today.
- What's needed: -

**credit-liabilities-review:295** (1 rules)
- Condition: PITIA of other properties owned by the borrower were not included in DTI as applicable
- Rationale: PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- What's needed: -

**credit-liabilities-review:296** (1 rules)
- Condition: The loan file did not document all payments included in the monthly DTI as applicable
- Rationale: PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- What's needed: -

**credit-liabilities-review:298** (1 rules)
- Condition: Higher HTI ratio used for energy efficiency without the calculation & source offset being documented
- Rationale: PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- What's needed: -

**credit-liabilities-review:299** (1 rules)
- Condition: Monthly PITIA not calculated correctly &/or did not include all housing components
- Rationale: PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- What's needed: -

**credit-liabilities-review:300** (1 rules)
- Condition: PITI property tax amt was incorrect by transfer of ownership changing the amount or tax abatements
- Rationale: PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- What's needed: -

**credit-liabilities-review:301** (1 rules)
- Condition: PITI real estate tax amount was not based on the value of improvements plus the value of the land
- Rationale: PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- What's needed: -

**credit-liabilities-review:302** (1 rules)
- Condition: Property taxes excluded from housing ratio & tax abatement documentation & continuance req's not met
- Rationale: PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- What's needed: -

**credit-liabilities-review:303** (1 rules)
- Condition: Special assessments w/ more than 10 mos payments remaining not included in monthly housing expense
- Rationale: PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- What's needed: -

**credit-liabilities-review:304** (1 rules)
- Condition: Subject 2nd or investment & borr rents current residence, rent not documented &/or in housing ratio
- Rationale: PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- What's needed: -

**credit-liabilities-review:305** (1 rules)
- Condition: Tax exemption related to disability/age have a predetermined exp date within 5 yrs of the Note date
- Rationale: PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- What's needed: -

**credit-liabilities-review:307** (1 rules)
- Condition: Monthly PITIA not calculated correctly &/or did not include all housing components
- Rationale: PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- What's needed: -

**credit-liabilities-review:309** (1 rules)
- Condition: PITIA of other properties owned by the borrower were not included in DTI as applicable
- Rationale: PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- What's needed: -

**credit-liabilities-review:310** (1 rules)
- Condition: Subject 2nd or investment & borr rents current residence, rent not documented &/or in housing ratio
- Rationale: PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- What's needed: -

**credit-liabilities-review:311** (1 rules)
- Condition: A credit report was not obtained for the non-borrowing spouse in a community property state
- Rationale: A second credit report (the non-borrowing/non-purchasing spouse's) plus the applicable state's community-property statute reference -- neither exists in this corpus; every loan extracts exactly one applicant-side credit report at most.
- What's needed: -

**credit-liabilities-review:312** (1 rules)
- Condition: Comm property state non-borr spouse debts excluded without specific state law justifying exclusion
- Rationale: A second credit report (the non-borrowing/non-purchasing spouse's) plus the applicable state's community-property statute reference -- neither exists in this corpus; every loan extracts exactly one applicant-side credit report at most.
- What's needed: -

**credit-liabilities-review:313** (1 rules)
- Condition: Non-borrowing spouse debts not included in DTI in community property state not excluded by state law
- Rationale: A second credit report (the non-borrowing/non-purchasing spouse's) plus the applicable state's community-property statute reference -- neither exists in this corpus; every loan extracts exactly one applicant-side credit report at most.
- What's needed: -

**credit-liabilities-review:315** (1 rules)
- Condition: No credit score & a non-traditional credit report &/or non-traditional credit history not developed
- Rationale: Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- What's needed: -

**credit-liabilities-review:316** (1 rules)
- Condition: Non-traditional credit was used with no rent history, 3 eligible tradelines were not documented
- Rationale: Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- What's needed: -

**credit-liabilities-review:317** (1 rules)
- Condition: Nontraditional credit w/ rent history, a VOR & 1 more recent tradeline w/12 mos history not in file
- Rationale: Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- What's needed: -

**credit-liabilities-review:319** (1 rules)
- Condition: 12 mos reserves not verified where nontraditional credit was used for borr's w/out a housing history
- Rationale: Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- What's needed: -

**credit-liabilities-review:320** (1 rules)
- Condition: An unacceptable source was used to verify the nontraditional housing payments
- Rationale: Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- What's needed: -

**credit-liabilities-review:321** (1 rules)
- Condition: Borr w/ credit score had 50% or less qual income & no non-trad credit for borr w/out a credit score
- Rationale: Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- What's needed: -

**credit-liabilities-review:322** (1 rules)
- Condition: Non-purchase/LCO of 1-4 unit, all bwrs occupy: No bwr had DU credit score or 1 credit/install acct
- Rationale: Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- What's needed: -

**credit-liabilities-review:323** (1 rules)
- Condition: Nontraditional credit used & loan was not a fixed rate meeting conforming baseline loan limits
- Rationale: Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- What's needed: -

**credit-liabilities-review:324** (1 rules)
- Condition: Nontraditional credit was used for a subject property that is not a 1-4 unit principal residence
- Rationale: Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- What's needed: -

**credit-liabilities-review:325** (1 rules)
- Condition: Nontraditional credit was used in a transaction other than a purchase or limited cash-out refinance
- Rationale: Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- What's needed: -

**credit-liabilities-review:326** (1 rules)
- Condition: Nontraditional references not verified without DU allowing a 3rd party asset verification report
- Rationale: Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- What's needed: -

**credit-liabilities-review:328** (1 rules)
- Condition: The number of non-traditional accts insufficient or from an ineligible source
- Rationale: Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- What's needed: -

**credit-liabilities-review:330** (1 rules)
- Condition: Contributions to private or pooled savings accounts are not included in the DTI
- Rationale: Pooled/private-savings-plan agreement -- same document family asset-verification's triage flagged as absent from this corpus (G196/G209 there).
- What's needed: -

**credit-liabilities-review:333** (1 rules)
- Condition: Debts noted as “will rate by mail only” or “need written authorization” were not verified separately
- Rationale: 'Will rate by mail only'/'need written authorization' accounts need a separate written-verification document per account -- not a doc type this corpus models (the one credit report's tradelines don't carry a rate-by-mail flag either).
- What's needed: -

**credit-liabilities-review:334** (1 rules)
- Condition: Monthly payments on debts secured by virtual currency were not included in the DTI ratio
- Rationale: Needs a lease/HELOC/timeshare/solar-panel-agreement/virtual-currency-secured-loan document -- none of these niche liability-collateral document types exist in this corpus (same 'document family the synthetic corpus never modeled' pattern as several asset-verification YELLOW groups).
- What's needed: -

**credit-liabilities-review:335** (1 rules)
- Condition: No written verification for significant open debt(s) on the application but not on the credit report
- Rationale: The REVERSE direction of `UndisclosedLiabilityShape`'s condition (that shape flags a credit-report tradeline missing from the 1003; this row flags a 1003 liability missing from the credit report) -- needs a separate written-verification document per unreported debt that isn't modeled in this corpus. Noted as textually adjacent to, but NOT the same real-world check as, the mapped shape -- do not conflate the two directions when this is eventually built.
- What's needed: -

**credit-liabilities-review:337** (1 rules)
- Condition: Student loan payment not on credit report and the monthly payment was not determined as required
- Rationale: Student-loan payment-substitution math (0.5%/1% of balance when the credit report shows a $0 or missing payment) is crisp arithmetic, and `extract_tradelines()` already captures tradeline type/balance/monthly_payment (loan 01 has one Student tradeline) -- but verifying which qualifying-payment value the lender ACTUALLY used needs a DTI/qualifying-payment worksheet this pilot doesn't extract or derive from any document today. Trigger-detection is Bucket-B-close; the verification half is not.
- What's needed: -

**credit-liabilities-review:338** (1 rules)
- Condition: Family rental - no signed lease & 12 mos cashed checks or bank stmts for positive rent pay history
- Rationale: Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- What's needed: -

**credit-liabilities-review:340** (1 rules)
- Condition: Positive rent pay history - no signed lease & VOR, 12 mos checks/bank stmts, or landlord reference
- Rationale: Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- What's needed: -

**credit-liabilities-review:341** (1 rules)
- Condition: Positive rental history used & borr is not a 1st time homebuyer in a purchase w/ MDCS of 620 or more
- Rationale: Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- What's needed: -

**credit-liabilities-review:342** (1 rules)
- Condition: Positive rental payment history monthly payments of $300 or more for last 12 months not documented
- Rationale: Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- What's needed: -

**credit-liabilities-review:344** (1 rules)
- Condition: Preforeclosure sale reported <3 years prior to FHA case number assignment
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**credit-liabilities-review:345** (1 rules)
- Condition: Case not downgraded to refer in a refi where borr did not make mtg forbearance pymts as agreed
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**credit-liabilities-review:346** (1 rules)
- Condition: Forbearance plan inc & less than 3 consec pymts not made since as req'd for a credit qual streamline
- Rationale: Mortgage forbearance/modification-plan document (terms, consecutive-payment count since granted) -- not a doc type in this corpus.
- What's needed: -

**credit-liabilities-review:347** (1 rules)
- Condition: Forbearance plan not complete & 12 consecutive pymts not made since as req'd for CO refi
- Rationale: Mortgage forbearance/modification-plan document (terms, consecutive-payment count since granted) -- not a doc type in this corpus.
- What's needed: -

**credit-liabilities-review:348** (1 rules)
- Condition: Forbearance plan not complete & 3 consecutive pymts not made since as req'd for a no cash-out refi
- Rationale: Mortgage forbearance/modification-plan document (terms, consecutive-payment count since granted) -- not a doc type in this corpus.
- What's needed: -

**credit-liabilities-review:349** (1 rules)
- Condition: Forbearance plan not complete & 3 consecutive pymts not made since as req'd for a purchase
- Rationale: Mortgage forbearance/modification-plan document (terms, consecutive-payment count since granted) -- not a doc type in this corpus.
- What's needed: -

**credit-liabilities-review:350** (1 rules)
- Condition: Mtg forbearance will remain open after closing & the plan was not terminated prior to or at closing
- Rationale: Mortgage forbearance/modification-plan document (terms, consecutive-payment count since granted) -- not a doc type in this corpus.
- What's needed: -

**credit-liabilities-review:352** (1 rules)
- Condition: Refi w/ a mod/forbearance  w/in 12 mos without a copy of the mod/forbearance plan with terms
- Rationale: Mortgage forbearance/modification-plan document (terms, consecutive-payment count since granted) -- not a doc type in this corpus.
- What's needed: -

**credit-liabilities-review:353** (1 rules)
- Condition: The borrower did not make at least 6 payments after forbearance modification as req'd for str refi
- Rationale: Mortgage forbearance/modification-plan document (terms, consecutive-payment count since granted) -- not a doc type in this corpus.
- What's needed: -

**credit-liabilities-review:354** (1 rules)
- Condition: The pay history during the forbearance plan was not utilized in determining late housing payments
- Rationale: Mortgage forbearance/modification-plan document (terms, consecutive-payment count since granted) -- not a doc type in this corpus.
- What's needed: -

**credit-liabilities-review:356** (1 rules)
- Condition: Not all payments for revolving charge accounts were included to calculate the borrower’s debts
- Rationale: The percentage-of-balance math (5%/1.5%/0.5% thresholds) is crisp arithmetic once the relevant balance is in hand, and `extract_tradelines()` already captures type/balance/monthly_payment per tradeline -- but confirming whether the LENDER actually included the computed amount in the final DTI needs a DTI worksheet this pilot doesn't derive (same gap as F_PITIA_DTI_REO); and month-by-month late-payment-in-12-months detection needs payment-history depth the tradeline snapshot (a single current 'Status' value) doesn't carry. Trigger data partly in hand; verification math not yet built.
- What's needed: -

**credit-liabilities-review:357** (1 rules)
- Condition: A student loan was excluded from the monthly DTI ratio without all requirements being met
- Rationale: Student-loan payment-substitution math (0.5%/1% of balance when the credit report shows a $0 or missing payment) is crisp arithmetic, and `extract_tradelines()` already captures tradeline type/balance/monthly_payment (loan 01 has one Student tradeline) -- but verifying which qualifying-payment value the lender ACTUALLY used needs a DTI/qualifying-payment worksheet this pilot doesn't extract or derive from any document today. Trigger-detection is Bucket-B-close; the verification half is not.
- What's needed: -

**credit-liabilities-review:358** (1 rules)
- Condition: Credit report pymt (not $0) or 0.5% of the student loan bal in repymt/deferment/forbearance not used
- Rationale: Mortgage forbearance/modification-plan document (terms, consecutive-payment count since granted) -- not a doc type in this corpus.
- What's needed: -

**credit-liabilities-review:359** (1 rules)
- Condition: Excluded student loan w/out source documentation loan is approved to not be repaid as applicable
- Rationale: Student-loan payment-substitution math (0.5%/1% of balance when the credit report shows a $0 or missing payment) is crisp arithmetic, and `extract_tradelines()` already captures tradeline type/balance/monthly_payment (loan 01 has one Student tradeline) -- but verifying which qualifying-payment value the lender ACTUALLY used needs a DTI/qualifying-payment worksheet this pilot doesn't extract or derive from any document today. Trigger-detection is Bucket-B-close; the verification half is not.
- What's needed: -

**credit-liabilities-review:361** (1 rules)
- Condition: 0.5% of the outstanding student loan balance not used as the pymt where the credit report pymt is 0
- Rationale: Student-loan payment-substitution math (0.5%/1% of balance when the credit report shows a $0 or missing payment) is crisp arithmetic, and `extract_tradelines()` already captures tradeline type/balance/monthly_payment (loan 01 has one Student tradeline) -- but verifying which qualifying-payment value the lender ACTUALLY used needs a DTI/qualifying-payment worksheet this pilot doesn't extract or derive from any document today. Trigger-detection is Bucket-B-close; the verification half is not.
- What's needed: -

**credit-liabilities-review:362** (1 rules)
- Condition: An outstanding student loan debt was not included regardless of payment type or status of payments
- Rationale: Student-loan payment-substitution math (0.5%/1% of balance when the credit report shows a $0 or missing payment) is crisp arithmetic, and `extract_tradelines()` already captures tradeline type/balance/monthly_payment (loan 01 has one Student tradeline) -- but verifying which qualifying-payment value the lender ACTUALLY used needs a DTI/qualifying-payment worksheet this pilot doesn't extract or derive from any document today. Trigger-detection is Bucket-B-close; the verification half is not.
- What's needed: -

**credit-liabilities-review:364** (1 rules)
- Condition: Student debt excluded w/out documenting the loan balance was forgiven, canceled, discharged, or PIF
- Rationale: Student-loan payment-substitution math (0.5%/1% of balance when the credit report shows a $0 or missing payment) is crisp arithmetic, and `extract_tradelines()` already captures tradeline type/balance/monthly_payment (loan 01 has one Student tradeline) -- but verifying which qualifying-payment value the lender ACTUALLY used needs a DTI/qualifying-payment worksheet this pilot doesn't extract or derive from any document today. Trigger-detection is Bucket-B-close; the verification half is not.
- What's needed: -

**credit-liabilities-review:365** (1 rules)
- Condition: Student loan monthly payment, payment status, &/or the outstanding balance/terms not documented
- Rationale: Student-loan payment-substitution math (0.5%/1% of balance when the credit report shows a $0 or missing payment) is crisp arithmetic, and `extract_tradelines()` already captures tradeline type/balance/monthly_payment (loan 01 has one Student tradeline) -- but verifying which qualifying-payment value the lender ACTUALLY used needs a DTI/qualifying-payment worksheet this pilot doesn't extract or derive from any document today. Trigger-detection is Bucket-B-close; the verification half is not.
- What's needed: -

**credit-liabilities-review:368** (1 rules)
- Condition: Authorized user accts included without evidence borrower solely paid for last 12 mos in manual UW
- Rationale: Needs a 12-month third-party-payment history (contingent-liability co-obligor, cosigner, or authorized-user account owner) -- `urla_liabilities`/`tradelines` capture the liability itself but not who else has been paying it or for how long; no such payment-history document exists in this corpus.
- What's needed: -

**credit-liabilities-review:369** (1 rules)
- Condition: Determination of new debt from inquiries reported within 90-days of closing is not documented
- Rationale: Needs a parsed Inquiries table (already visible in the loan 01 credit report's text -- 'Inquiries (last 120 days)' with Date/Bureau/Requesting Party -- but not yet in FIELD_SPECS/entities) cross-referenced against whether new debt was opened; Bucket-B-style (deepen extraction of a section already present in the one document we have), not a missing document.
- What's needed: -

**credit-liabilities-review:370** (1 rules)
- Condition: Late rental and/or mortgage payment reported/verified does not meet guidelines
- Rationale: 'Does not meet guidelines' bundles a specific late-payment-count/severity threshold (defined per agency Selling Guide, not stated in the row itself) with the housing-payment-history depth this pilot's VOM only captures for one mortgage on one loan (loan 04) -- needs both a guide-sourced threshold and broader payment-history extraction; genuinely blocked on both counts, not a rule-clarity problem.
- What's needed: -

**credit-liabilities-review:372** (1 rules)
- Condition: Mortgage not reported and verification of satisfactory pay history is missing
- Rationale: MISCLASSIFIED (matched 'does not provide' + 'credit report' keyword) -- needs 12 months of month-by-month mortgage payment history; `extract_tradelines()` captures only a single current-status snapshot, same gap as F_PAYMENT_HISTORY_DEPTH.
- What's needed: -

**credit-liabilities-review:376** (1 rules)
- Condition: The pattern of using revolving credit to the max limit credit mgt risk not evaluated in manual UW
- Rationale: The percentage-of-balance math (5%/1.5%/0.5% thresholds) is crisp arithmetic once the relevant balance is in hand, and `extract_tradelines()` already captures type/balance/monthly_payment per tradeline -- but confirming whether the LENDER actually included the computed amount in the final DTI needs a DTI worksheet this pilot doesn't derive (same gap as F_PITIA_DTI_REO); and month-by-month late-payment-in-12-months detection needs payment-history depth the tradeline snapshot (a single current 'Status' value) doesn't carry. Trigger data partly in hand; verification math not yet built.
- What's needed: -

**credit-liabilities-review:377** (1 rules)
- Condition: A debt on the application is not on the credit report without documenting the debt separately
- Rationale: The REVERSE direction of `UndisclosedLiabilityShape`'s condition (that shape flags a credit-report tradeline missing from the 1003; this row flags a 1003 liability missing from the credit report) -- needs a separate written-verification document per unreported debt that isn't modeled in this corpus. Noted as textually adjacent to, but NOT the same real-world check as, the mapped shape -- do not conflate the two directions when this is eventually built.
- What's needed: -

**credit-liabilities-review:378** (1 rules)
- Condition: Inconsistencies noted in file info & orig credit report without a updated credit report/supplement
- Rationale: Needs a second (updated) credit-report pull to compare against the original, plus a resubmission/rescoring record -- neither exists for any loan in this corpus (each loan has at most one credit report snapshot).
- What's needed: -

**credit-liabilities-review:381** (1 rules)
- Condition: Payment for undisclosed non-mortgage debt is not verified for resubmission requirements
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**credit-liabilities-review:382** (1 rules)
- Condition: Undisclosed mtg not in TOTAL w/ unacceptable pay history not downgraded to Refer/manual UW
- Rationale: DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- What's needed: -

**income-verification:64** (1 rules)
- Condition: Income submitted to AUS is not accurate - broken out and/or categorized correctly
- Rationale: Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- What's needed: a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute

**income-verification:72** (5 rules)
- Condition: The 4506C screen in EPIC is incomplete or incorrect (IE. Record of Account)
- Rationale: Recurs across all 5 agencies under 'IRS Form 4506-C requirements'; genuinely different in kind from the other 4506-C rows (which check the signed FORM itself) — this checks an internal system screen's state, closer to the Bucket-C external-system-state pattern flagged for the NMLS/RE-license rules (decisions 016/017) than a document-presence gap, though not itself a live external registry lookup. Kept YELLOW, flagged for a human to consider whether it belongs in scope at all.
- What's needed: a lender-system (EPIC) 4506-C screen-completeness fact — not derivable from any loan document; this is internal LOS/servicing-system screen data, not a document in the closed-loan file

**income-verification:84** (1 rules)
- Condition: Income submitted to AUS is not accurate - broken out and/or categorized correctly
- Rationale: Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- What's needed: a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute

**income-verification:158** (1 rules)
- Condition: Income submitted to AUS is not accurate - broken out and/or categorized correctly
- Rationale: Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- What's needed: a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute

**income-verification:184** (1 rules)
- Condition: Income submitted to AUS is not accurate - broken out and/or categorized correctly
- Rationale: Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- What's needed: a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute

**income-verification:192** (1 rules)
- Condition: Income submitted to AUS is not accurate - broken out and/or categorized correctly
- Rationale: Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- What's needed: a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute

**income-verification:222** (1 rules)
- Condition: The net rental income/loss worksheet was not utilized when applicable
- Rationale: Single AMQ row (O-FNM); crisp presence check once the worksheet doc type is modeled; no rental-income document of any kind exists in the 5-loan corpus today.
- What's needed: net-rental-income worksheet document type — not in the corpus

**income-verification:233** (1 rules)
- Condition: Income submitted to AUS is not accurate - broken out and/or categorized correctly
- Rationale: Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- What's needed: a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute

**income-verification:259** (1 rules)
- Condition: Income submitted to AUS is not accurate - broken out and/or categorized correctly
- Rationale: Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- What's needed: a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute

**income-verification:269** (1 rules)
- Condition: Income submitted to AUS is not accurate - broken out and/or categorized correctly
- Rationale: Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- What's needed: a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute

**income-verification:277** (1 rules)
- Condition: Income submitted to AUS is not accurate - broken out and/or categorized correctly
- Rationale: Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- What's needed: a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute

**income-verification:284** (1 rules)
- Condition: Income submitted to AUS is not accurate - broken out and/or categorized correctly
- Rationale: Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- What's needed: a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute

**income-verification:296** (1 rules)
- Condition: Income submitted to AUS is not accurate - broken out and/or categorized correctly
- Rationale: Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- What's needed: a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute

**income-verification:334** (2 rules)
- Condition: Income submitted to AUS is not accurate - broken out and/or categorized correctly
- Rationale: Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- What's needed: a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute

**income-verification:376** (1 rules)
- Condition: Income submitted to AUS is not accurate - broken out and/or categorized correctly
- Rationale: Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- What's needed: a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute

**income-verification:460** (2 rules)
- Condition: Income submitted to AUS is not accurate - broken out and/or categorized correctly
- Rationale: Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- What's needed: a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute

**income-verification:476** (1 rules)
- Condition: Income submitted to AUS is not accurate - broken out and/or categorized correctly
- Rationale: Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- What's needed: a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute

**income-verification:498** (1 rules)
- Condition: Income submitted to AUS is not accurate - broken out and/or categorized correctly
- Rationale: Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- What's needed: a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute

**income-verification:510** (1 rules)
- Condition: Documentation from a third party provider for the borrower’s business was not provided
- Rationale: Single AMQ row (O-FNM); exception_description names the specific missing artifact plainly ('CPA letter not provided') — crisp presence check once that doc type is modeled.
- What's needed: CPA-letter/third-party-verification document type — not in the corpus

**income-verification:512** (1 rules)
- Condition: File missing a YTD P&L and current balance sheet as applicable or as per AUS for self-employed
- Rationale: READY TO BUILD candidate — verified per decision-018 discipline; see module docstring / decision 021.
- What's needed: none if wired — see READY_TO_BUILD

**income-verification:515** (1 rules)
- Condition: Income submitted to AUS is not accurate - broken out and/or categorized correctly
- Rationale: Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- What's needed: a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute

**income-verification:529** (1 rules)
- Condition: A YTD profit and loss statement and balance sheet were not provided
- Rationale: READY TO BUILD candidate — verified per decision-018 discipline; see module docstring / decision 021.
- What's needed: none if wired — see READY_TO_BUILD

**income-verification:547** (1 rules)
- Condition: Income submitted to AUS is not accurate - broken out and/or categorized correctly
- Rationale: Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- What's needed: a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute

**income-verification:553** (1 rules)
- Condition: Income submitted to AUS is not accurate - broken out and/or categorized correctly
- Rationale: Recurs identically (verbatim condition text) under 19 different AMQ question categories (automobile allowance, alimony, disability, employment, general income, housing assistance, military, other income, retirement, self-employed, trust income, ...) — one underlying fact (AUS income-categorization accuracy), same AUS-submission-export gap already flagged in the asset-verification triage (no DU/LPA findings export exists in this pilot for FNM/FRD; only RHS's GUS findings are partially parsed, for loan 05).
- What's needed: a DU/LP (or equivalent AUS) findings export to compare against the per-income-type breakdown submitted, cross-referenced with the AUS-categorization amq_compiler.py would need to compute

**underwriting-review:11** (1 rules)
- Condition: Contract shows a private transfer, reconveyance, recovery/capital, or resale fee & is not cleared
- Rationale: Same missing-purchase-contract gap as asset-verification's earnest-money-deposit family (G040/G081/G084/G086, decision 017).
- What's needed: sales contract document (this pilot has NO purchase/sales contract document type in any of the 5 synthetic loans -- same systemic gap flagged in asset-verification's EMD family, decision 017)

**underwriting-review:13** (1 rules)
- Condition: Citizens FHA/VA overlay exception appr’d is missing commentary on FHA transmittal/VA loan analysis
- Rationale: Niche VA underwriting-analysis form; loan 03 (the pilot's only VA loan) does not contain this document.
- What's needed: VA Form 26-6393 (VA Loan Analysis) -- not in any synthetic loan folder

**underwriting-review:14** (1 rules)
- Condition: No, all parties were not checked against the exclusionary list or other applicable lists
- Rationale: Distinct from the CAIVRS/LDP/GSA family above -- no per-loan screenshot document for these specific lists exists anywhere in the corpus (not even one instance), a genuine Bucket-A fixture gap, not merely thin extraction.
- What's needed: OFAC SDN list / Freddie Mac Exclusionary List / FHFA Suspended Counterparty Program / BSA-AML screening record (no such document or fixture exists in any of the 5 synthetic loans)

**underwriting-review:18** (1 rules)
- Condition: The documentation in the tandem file does not match and/or is missing
- Rationale: Niche cross-file consistency check, absent from the corpus.
- What's needed: a 'tandem file' (co-issued/companion loan file) concept -- not modeled; no such document or cross-loan-file relationship exists in this pilot

**underwriting-review:24** (1 rules)
- Condition: Documentation the transaction does not violate HUD's rule against property flipping was not provided
- Rationale: Same FHA property-flipping family as G023/G027.
- What's needed: seller-of-record / property-flipping documentation -- not modeled

**underwriting-review:66** (1 rules)
- Condition: Form RD 3555-21 (Rev. 03-21) is missing, not fully completed &/or not signed by all required parties
- Rationale: USDA guarantee-request form; loan 05 (the pilot's only USDA loan) does not contain this document.
- What's needed: Form RD 3555-21 (Request for Single Family Housing Loan Guarantee) -- not in corpus

**underwriting-review:68** (1 rules)
- Condition: BSA, Money Laundering Control Act, USA PATRIOT Act & Anti-Money Laundering Act not complied with
- Rationale: Distinct from the CAIVRS/LDP/GSA family above -- no per-loan screenshot document for these specific lists exists anywhere in the corpus (not even one instance), a genuine Bucket-A fixture gap, not merely thin extraction.
- What's needed: OFAC SDN list / Freddie Mac Exclusionary List / FHFA Suspended Counterparty Program / BSA-AML screening record (no such document or fixture exists in any of the 5 synthetic loans)

**underwriting-review:69** (1 rules)
- Condition: Match on the OFAC SDN list, FHLMC not notified w/in 24 hrs & funds not blocked & segregated
- Rationale: Distinct from the CAIVRS/LDP/GSA family above -- no per-loan screenshot document for these specific lists exists anywhere in the corpus (not even one instance), a genuine Bucket-A fixture gap, not merely thin extraction.
- What's needed: OFAC SDN list / Freddie Mac Exclusionary List / FHFA Suspended Counterparty Program / BSA-AML screening record (no such document or fixture exists in any of the 5 synthetic loans)

**underwriting-review:70** (1 rules)
- Condition: No evidence all participants were checked against the FHFA Suspended Counterparty Program list
- Rationale: Distinct from the CAIVRS/LDP/GSA family above -- no per-loan screenshot document for these specific lists exists anywhere in the corpus (not even one instance), a genuine Bucket-A fixture gap, not merely thin extraction.
- What's needed: OFAC SDN list / Freddie Mac Exclusionary List / FHFA Suspended Counterparty Program / BSA-AML screening record (no such document or fixture exists in any of the 5 synthetic loans)

**underwriting-review:71** (1 rules)
- Condition: Required parties per their specific role in the loan not checked against the FHLMC Exclusionary List
- Rationale: Distinct from the CAIVRS/LDP/GSA family above -- no per-loan screenshot document for these specific lists exists anywhere in the corpus (not even one instance), a genuine Bucket-A fixture gap, not merely thin extraction.
- What's needed: OFAC SDN list / Freddie Mac Exclusionary List / FHFA Suspended Counterparty Program / BSA-AML screening record (no such document or fixture exists in any of the 5 synthetic loans)

**underwriting-review:82** (1 rules)
- Condition: LTV limit exceeded without meeting requirements based on identities of interest relationship type
- Rationale: Niche identity-of-interest family, absent from the corpus.
- What's needed: an identity-of-interest relationship fact (borrower's relationship to builder/developer/seller) -- not modeled

**underwriting-review:89** (1 rules)
- Condition: Lender’s Loan Quality Certification not in the file or not signed by an appropriate lender official
- Rationale: Post-closing VA certification document, absent from loan 03.
- What's needed: Lender's Loan Quality Certification (VA) -- not in corpus

**underwriting-review:104** (1 rules)
- Condition: Borr is a nonprofit not on approved HUD Nonprofit Agency Roster
- Rationale: Nonprofit-borrower-eligibility family; no roster document/fixture exists in this pilot's corpus.
- What's needed: HUD Nonprofit Agency Roster cross-reference -- an external roster lookup, not a loan-file fact (same kind of gap as CAIVRS/LDP/GSA, though evidenced by a roster listing rather than a per-loan screenshot)

**underwriting-review:109** (1 rules)
- Condition: Subject has a private transfer fee & is not a shared equity loan with a Note date on or after 7/1/23
- Rationale: Same missing-purchase-contract gap as asset-verification's earnest-money-deposit family (G040/G081/G084/G086, decision 017).
- What's needed: sales contract document (this pilot has NO purchase/sales contract document type in any of the 5 synthetic loans -- same systemic gap flagged in asset-verification's EMD family, decision 017)

**underwriting-review:110** (1 rules)
- Condition: The subject's private transfer fee is unacceptable under the Private Transfer Fee Regulation
- Rationale: Same missing-purchase-contract gap as asset-verification's earnest-money-deposit family (G040/G081/G084/G086, decision 017).
- What's needed: sales contract document (this pilot has NO purchase/sales contract document type in any of the 5 synthetic loans -- same systemic gap flagged in asset-verification's EMD family, decision 017)

**underwriting-review:111** (1 rules)
- Condition: A service provider not used to verify with the SSA where inconsistencies/multiple SSNs were noted
- Rationale: SSN-validation family; no such verification record exists in any of the 5 loans.
- What's needed: SSN-discrepancy resolution documentation (SSA verification letter, Form SSA-89/eCBSV) or identity-verification record -- not in corpus

**underwriting-review:114** (1 rules)
- Condition: All req's not met for a loan that includes a beneficial interest in a revocable Family Living Trust
- Rationale: None of the 5 synthetic loans involves a trust-held title; niche fixture gap.
- What's needed: Living Trust Agreement / inter-vivos-revocable-trust documentation -- not in corpus

**underwriting-review:118** (1 rules)
- Condition: Not all occupying/non-occupying borrowers took title in their name or a Living Trust
- Rationale: None of the 5 synthetic loans involves a trust-held title; niche fixture gap.
- What's needed: Living Trust Agreement / inter-vivos-revocable-trust documentation -- not in corpus

**underwriting-review:157** (1 rules)
- Condition: Monthly PITIA not calculated correctly &/or did not include all housing components
- Rationale: Niche VA underwriting-analysis form; loan 03 (the pilot's only VA loan) does not contain this document.
- What's needed: VA Form 26-6393 (VA Loan Analysis) -- not in any synthetic loan folder

**underwriting-review:158** (1 rules)
- Condition: More than one Social Security# was noted without explanation &/or validation from SSA
- Rationale: Niche VA underwriting-analysis form; loan 03 (the pilot's only VA loan) does not contain this document.
- What's needed: VA Form 26-6393 (VA Loan Analysis) -- not in any synthetic loan folder

**underwriting-review:159** (1 rules)
- Condition: PITIA of other properties owned by the borrower were not included in DTI as applicable
- Rationale: Niche VA underwriting-analysis form; loan 03 (the pilot's only VA loan) does not contain this document.
- What's needed: VA Form 26-6393 (VA Loan Analysis) -- not in any synthetic loan folder

**underwriting-review:160** (1 rules)
- Condition: The VA Loan Analysis, VA Form 26-6393 (Aug. 2022), was not fully completed or was incorrect
- Rationale: Niche VA underwriting-analysis form; loan 03 (the pilot's only VA loan) does not contain this document.
- What's needed: VA Form 26-6393 (VA Loan Analysis) -- not in any synthetic loan folder

**underwriting-review:161** (1 rules)
- Condition: The file did not contain a completed Loan Analysis, VA Form 26-639
- Rationale: Niche VA underwriting-analysis form; loan 03 (the pilot's only VA loan) does not contain this document.
- What's needed: VA Form 26-6393 (VA Loan Analysis) -- not in any synthetic loan folder

**underwriting-review:162** (1 rules)
- Condition: The income used to qualify was calculated incorrectly
- Rationale: Niche VA underwriting-analysis form; loan 03 (the pilot's only VA loan) does not contain this document.
- What's needed: VA Form 26-6393 (VA Loan Analysis) -- not in any synthetic loan folder

**underwriting-review:163** (1 rules)
- Condition: UW failed to include every known debt, judgment, bankruptcy, alimony or child support obligation
- Rationale: Niche VA underwriting-analysis form; loan 03 (the pilot's only VA loan) does not contain this document.
- What's needed: VA Form 26-6393 (VA Loan Analysis) -- not in any synthetic loan folder

**underwriting-review:164** (1 rules)
- Condition: VA underwriter ID number was not entered in box 52 on the Loan Analysis, VA Form 26-6393 (Aug. 2022)
- Rationale: Niche VA underwriting-analysis form; loan 03 (the pilot's only VA loan) does not contain this document.
- What's needed: VA Form 26-6393 (VA Loan Analysis) -- not in any synthetic loan folder

**underwriting-review:166** (1 rules)
- Condition: Most up-to-date version of Form 26-1817, is not in the file or is incomplete, incorrect or unsigned
- Rationale: Niche VA eligibility form, absent from loan 03.
- What's needed: VA Form 26-1817 (Unmarried Surviving Spouse eligibility) -- not in corpus

**underwriting-review:171** (1 rules)
- Condition: Veteran discharged from service & a copy of DD Form 214 not provided as  proof of military service
- Rationale: Military-service-verification family, absent from the corpus.
- What's needed: DD Form 214 / military orders documentation -- not in corpus

**underwriting-review:185** (1 rules)
- Condition: Expanded borrower demographic information not entered in FHA Connection as per HMDA regulations
- Rationale: Niche FHA Connection data-entry fact, absent from the corpus.
- What's needed: HMDA demographic-data entry fact (FHA Connection screen) -- not modeled

**underwriting-review:188** (1 rules)
- Condition: Case number was transferred from another lender without meeting all requirements
- Rationale: Niche FHA case-transfer fact, absent from the corpus.
- What's needed: case-number-transfer documentation between lenders -- not modeled

**underwriting-review:189** (1 rules)
- Condition: The borr's receipt of counseling by HUD-approved housing counseling agencies not evident
- Rationale: Niche counseling-completion document, absent from the corpus.
- What's needed: homeownership-education/housing-counseling completion certificate -- not in corpus

**underwriting-review:192** (1 rules)
- Condition: Conditional Commitment not in the loan file
- Rationale: USDA/RHS commitment document, absent from loan 05.
- What's needed: RHS Conditional Commitment -- not in corpus

**underwriting-review:194** (1 rules)
- Condition: The Conditional Commitment was not issued prior to the loan closing
- Rationale: USDA/RHS commitment document, absent from loan 05.
- What's needed: RHS Conditional Commitment -- not in corpus

**underwriting-review:197** (1 rules)
- Condition: An executed statement clearly expressing consent for use of applicant's information is missing
- Rationale: Niche FHA authorization form, absent from the corpus.
- What's needed: signed borrower-information-use consent statement -- not in corpus

**underwriting-review:198** (1 rules)
- Condition: Non-borrowing spouse's social security number &/or consent to verify with the SSA not in the file
- Rationale: SSN-validation family; no such verification record exists in any of the 5 loans.
- What's needed: SSN-discrepancy resolution documentation (SSA verification letter, Form SSA-89/eCBSV) or identity-verification record -- not in corpus

**underwriting-review:201** (1 rules)
- Condition: Active duty svc member has pre-discharge claim pending & proposed or memorandum rating not obtained
- Rationale: Niche VA eligibility sub-conditions, absent from the corpus.
- What's needed: VA pending-disability-claim / National-Guard-service-days documentation -- not modeled

**underwriting-review:202** (1 rules)
- Condition: Army or Air National Guard member does not have 90 cumulative &  30 consecutive days active duty
- Rationale: Niche VA eligibility sub-conditions, absent from the corpus.
- What's needed: VA pending-disability-claim / National-Guard-service-days documentation -- not modeled

**underwriting-review:205** (1 rules)
- Condition: Borrower is not a US citizen & documentation verifying qualified alien status not obtained
- Rationale: Citizenship/residency family; not modeled at all in this pilot (same gap flagged for asset-verification's G284, decision 017).
- What's needed: citizenship/residency-status documentation (USCIS determination, alien-registration evidence) -- not in corpus

**underwriting-review:208** (1 rules)
- Condition: Pre-discharge disability exam w/ memorandum rating pay eligibility & the stat funding fee not waived
- Rationale: Niche VA eligibility sub-conditions, absent from the corpus.
- What's needed: VA pending-disability-claim / National-Guard-service-days documentation -- not modeled

**underwriting-review:209** (1 rules)
- Condition: The active duty service member has a pending pre-discharge claim & VA Form 26-8937 was not submitted
- Rationale: Niche VA benefits-verification form, absent from loan 03.
- What's needed: VA Form 26-8937 (Verification of VA Benefits) -- not in corpus

**underwriting-review:213** (1 rules)
- Condition: The social security number for each applicant was not documented and/or verified
- Rationale: SSN-validation family; no such verification record exists in any of the 5 loans.
- What's needed: SSN-discrepancy resolution documentation (SSA verification letter, Form SSA-89/eCBSV) or identity-verification record -- not in corpus

**underwriting-review:216** (1 rules)
- Condition: All eligibility req's not met for  non-U.S. citizen borrower including DACA status recipients
- Rationale: Citizenship/residency family; not modeled at all in this pilot (same gap flagged for asset-verification's G284, decision 017).
- What's needed: citizenship/residency-status documentation (USCIS determination, alien-registration evidence) -- not in corpus

**underwriting-review:217** (1 rules)
- Condition: Citizenship evidence for borrowers from Micronesia, Marshall Islands, or Palau not in the file
- Rationale: Citizenship/residency family; not modeled at all in this pilot (same gap flagged for asset-verification's G284, decision 017).
- What's needed: citizenship/residency-status documentation (USCIS determination, alien-registration evidence) -- not in corpus

**underwriting-review:218** (1 rules)
- Condition: Documentation substantiating the refugee or asylee status granted by the USCIS was not obtained
- Rationale: Citizenship/residency family; not modeled at all in this pilot (same gap flagged for asset-verification's G284, decision 017).
- What's needed: citizenship/residency-status documentation (USCIS determination, alien-registration evidence) -- not in corpus

**underwriting-review:224** (1 rules)
- Condition: Delinq court order child support w/out admin offset & arrear not PIF, released or 3 timely repaymts
- Rationale: Niche RHS credit-eligibility sub-condition, absent from the corpus.
- What's needed: delinquent-child-support repayment-history documentation -- not modeled

**underwriting-review:227** (1 rules)
- Condition: All employees involved in the origination of the loan were not checked against the FHFA SCP list
- Rationale: Distinct from the CAIVRS/LDP/GSA family above -- no per-loan screenshot document for these specific lists exists anywhere in the corpus (not even one instance), a genuine Bucket-A fixture gap, not merely thin extraction.
- What's needed: OFAC SDN list / Freddie Mac Exclusionary List / FHFA Suspended Counterparty Program / BSA-AML screening record (no such document or fixture exists in any of the 5 synthetic loans)

**underwriting-review:230** (1 rules)
- Condition: Match on the OFAC SDN list, FNMA not notified w/in 24 hrs & funds not blocked & segregated
- Rationale: Distinct from the CAIVRS/LDP/GSA family above -- no per-loan screenshot document for these specific lists exists anywhere in the corpus (not even one instance), a genuine Bucket-A fixture gap, not merely thin extraction.
- What's needed: OFAC SDN list / Freddie Mac Exclusionary List / FHFA Suspended Counterparty Program / BSA-AML screening record (no such document or fixture exists in any of the 5 synthetic loans)

**underwriting-review:234** (1 rules)
- Condition: Required parties per their specific role in the loan not checked against the FHLMC Exclusionary List
- Rationale: Distinct from the CAIVRS/LDP/GSA family above -- no per-loan screenshot document for these specific lists exists anywhere in the corpus (not even one instance), a genuine Bucket-A fixture gap, not merely thin extraction.
- What's needed: OFAC SDN list / Freddie Mac Exclusionary List / FHFA Suspended Counterparty Program / BSA-AML screening record (no such document or fixture exists in any of the 5 synthetic loans)

**underwriting-review:241** (1 rules)
- Condition: Existing USDA loan being refinanced did not close at least 180 days before the req for Cond Commit
- Rationale: USDA/RHS commitment document, absent from loan 05.
- What's needed: RHS Conditional Commitment -- not in corpus

**underwriting-review:260** (1 rules)
- Condition: All eligibility and underwriting requirements not met for nonprofit borrower
- Rationale: Nonprofit-borrower-eligibility family; no roster document/fixture exists in this pilot's corpus.
- What's needed: HUD Nonprofit Agency Roster cross-reference -- an external roster lookup, not a loan-file fact (same kind of gap as CAIVRS/LDP/GSA, though evidenced by a roster listing rather than a per-loan screenshot)

**underwriting-review:267** (1 rules)
- Condition: Homeownership education req's not met for non-traditional credit borr's or purchase w/ LTV above 95%
- Rationale: Niche counseling-completion document, absent from the corpus.
- What's needed: homeownership-education/housing-counseling completion certificate -- not in corpus

**underwriting-review:269** (1 rules)
- Condition: SFC 162 not used where there was a discrepancy identified with the Social Security number
- Rationale: SSN-validation family; no such verification record exists in any of the 5 loans.
- What's needed: SSN-discrepancy resolution documentation (SSA verification letter, Form SSA-89/eCBSV) or identity-verification record -- not in corpus

**underwriting-review:270** (1 rules)
- Condition: SSN/ITIN discrepancy not resolved & documented using Form SSA–89, eCBSV or 3rd party vendor from SSA
- Rationale: SSN-validation family; no such verification record exists in any of the 5 loans.
- What's needed: SSN-discrepancy resolution documentation (SSA verification letter, Form SSA-89/eCBSV) or identity-verification record -- not in corpus

**underwriting-review:271** (1 rules)
- Condition: The file did not document that each borrower has a valid SS number or ITIN
- Rationale: SSN-validation family; no such verification record exists in any of the 5 loans.
- What's needed: SSN-discrepancy resolution documentation (SSA verification letter, Form SSA-89/eCBSV) or identity-verification record -- not in corpus

**underwriting-review:272** (1 rules)
- Condition: The identity of each borrower was not confirmed prior to the extension of credit
- Rationale: SSN-validation family; no such verification record exists in any of the 5 loans.
- What's needed: SSN-discrepancy resolution documentation (SSA verification letter, Form SSA-89/eCBSV) or identity-verification record -- not in corpus

**underwriting-review:273** (1 rules)
- Condition: Third-party homeownership education content not aligned w/ NIS or HUD's Housing Counseling Program
- Rationale: Niche counseling-completion document, absent from the corpus.
- What's needed: homeownership-education/housing-counseling completion certificate -- not in corpus

**underwriting-review:277** (1 rules)
- Condition: Income calculations not provided on Attachment 9-B, Uniform Transmittal Summary or equivalent form
- Rationale: Niche RHS income-documentation attachment, absent from loan 05.
- What's needed: Attachment 9-B, Uniform Transmittal Summary (RHS income-calculation form) -- not in corpus

**underwriting-review:279** (1 rules)
- Condition: One or more income sources were used to qualify that are to be excluded as per RHS guidelines
- Rationale: Same RHS income-underwriting family as the rhs_income_calc family (income-source eligibility sub-condition).
- What's needed: RHS eligible-income-source classification -- not modeled

**underwriting-review:290** (1 rules)
- Condition: Foreign origin documents were not filled out in English & were not translated into English
- Rationale: Niche compliance fact, absent from the corpus (no foreign-language document exists in any of the 5 loans).
- What's needed: a translation-attached fact for foreign-language documents -- not modeled

**underwriting-review:311** (1 rules)
- Condition: At least 1 inter vivos revocable trustee did not sign the loan documents in a primary residence
- Rationale: None of the 5 synthetic loans involves a trust-held title; niche fixture gap.
- What's needed: Living Trust Agreement / inter-vivos-revocable-trust documentation -- not in corpus

**underwriting-review:312** (1 rules)
- Condition: In a primary residence at least 1 inter vivos revocable trustee will not occupy the subject property
- Rationale: None of the 5 synthetic loans involves a trust-held title; niche fixture gap.
- What's needed: Living Trust Agreement / inter-vivos-revocable-trust documentation -- not in corpus

**underwriting-review:313** (1 rules)
- Condition: Income/assets of at least 1 person forming the inter vivos revocable trust was not used to qualify
- Rationale: None of the 5 synthetic loans involves a trust-held title; niche fixture gap.
- What's needed: Living Trust Agreement / inter-vivos-revocable-trust documentation -- not in corpus

**underwriting-review:315** (1 rules)
- Condition: Title insurance coverage contained exceptions for the inter vivos revocable trust or the trustees
- Rationale: None of the 5 synthetic loans involves a trust-held title; niche fixture gap.
- What's needed: Living Trust Agreement / inter-vivos-revocable-trust documentation -- not in corpus

**underwriting-review:316** (1 rules)
- Condition: Title is not vested in the inter vivos revocable trustee(s) and the individual borrower(s) names
- Rationale: None of the 5 synthetic loans involves a trust-held title; niche fixture gap.
- What's needed: Living Trust Agreement / inter-vivos-revocable-trust documentation -- not in corpus

**underwriting-review:318** (1 rules)
- Condition: Subject is rented & tenants rights could affect FNMA's interest
- Rationale: Niche landlord-tenant legal family, absent from the corpus.
- What's needed: a rental/lease agreement document -- not modeled

**underwriting-review:329** (1 rules)
- Condition: Property will be held in a living trust without all documentation requirements being met
- Rationale: None of the 5 synthetic loans involves a trust-held title; niche fixture gap.
- What's needed: Living Trust Agreement / inter-vivos-revocable-trust documentation -- not in corpus

**underwriting-review:348** (1 rules)
- Condition: Compensating factors were used to compensate for derogatory credit
- Rationale: Same hud_92900lt/va_26_6393 fixture family, compensating-factors sub-condition.
- What's needed: compensating-factors/extenuating-circumstances documentation on the FHA Transmittal (HUD-92900-LT) or VA Loan Analysis (26-6393) -- neither form is in corpus

**underwriting-review:349** (1 rules)
- Condition: Energy efficient stretch ratios used exceed limits &/or subject did not meet energy efficient req's
- Rationale: Niche FHA EEM program family, absent from the corpus.
- What's needed: Energy Efficient Mortgage (EEM) program documentation -- not modeled

**underwriting-review:352** (1 rules)
- Condition: Manual UW & no comp factors or ext circumstances (if applic) required by FHA on the FHA Transmittal
- Rationale: Same hud_92900lt/va_26_6393 fixture family, compensating-factors sub-condition.
- What's needed: compensating-factors/extenuating-circumstances documentation on the FHA Transmittal (HUD-92900-LT) or VA Loan Analysis (26-6393) -- neither form is in corpus

**underwriting-review:364** (1 rules)
- Condition: Mtg Modification changed the loan terms of original Note
- Rationale: Niche modified-loan-eligibility family, absent from the corpus.
- What's needed: a mortgage-modification agreement document -- not modeled

**underwriting-review:366** (1 rules)
- Condition: Debt paid down or PIF to qualify without the source of funds used being eligible and documented
- Rationale: Cross-block with asset-verification's sourcing-documentation gap; not a blind reuse of LargeDepositShape (different condition: paying off a debt vs. an unsourced deposit), flagged not wired.
- What's needed: source-of-funds-for-debt-payoff documentation -- ties to the asset-verification large-deposit/source-of-funds family (decisions 017/018)

**underwriting-review:378** (1 rules)
- Condition: A non-monthly payment option offered without a separate agreement
- Rationale: Niche FNM payment-collection family, absent from the corpus.
- What's needed: a non-standard-payment-option agreement document -- not modeled

**underwriting-review:381** (1 rules)
- Condition: The applicant is a non-US citizen not legally present in the United States
- Rationale: Citizenship/residency family; not modeled at all in this pilot (same gap flagged for asset-verification's G284, decision 017).
- What's needed: citizenship/residency-status documentation (USCIS determination, alien-registration evidence) -- not in corpus

**underwriting-review:385** (1 rules)
- Condition: Military orders not obtained evidencing active duty as reason borr unable to occupy as per the mtg
- Rationale: Military-service-verification family, absent from the corpus.
- What's needed: DD Form 214 / military orders documentation -- not in corpus

**underwriting-review:393** (1 rules)
- Condition: VA Form 26-1820 was not fully completed, executed, and dated by all applicable parties
- Rationale: Niche post-closing VA form, absent from loan 03.
- What's needed: VA Form 26-1820 (Report and Certification of Loan Disbursement) -- not in corpus

**underwriting-review:394** (1 rules)
- Condition: VA Form 26-1820, Report and Certification of Loan Disbursement is not in the file
- Rationale: Niche post-closing VA form, absent from loan 03.
- What's needed: VA Form 26-1820 (Report and Certification of Loan Disbursement) -- not in corpus

**underwriting-review:395** (1 rules)
- Condition: Form HUD-92561, Contract with Respect to Hotel and Transient Use, is req'd & not in the file
- Rationale: Niche FHA property-type form, absent from loan 02.
- What's needed: Form HUD-92561 (Hotel and Transient Use) -- not in corpus

**underwriting-review:396** (1 rules)
- Condition: Mixed-use -Less than 51%  sq ft residential &/or possible health/safety concerns
- Rationale: Niche FHA/FNM property-type family, absent from the corpus.
- What's needed: specific property-type/investment-eligibility facts (self-sufficiency rental income calc, multi-unit financial-interest count, mixed-use square footage) -- none modeled today

**underwriting-review:397** (1 rules)
- Condition: Net self-sufficiency rental Income was calculated incorrectly
- Rationale: Niche FHA/FNM property-type family, absent from the corpus.
- What's needed: specific property-type/investment-eligibility facts (self-sufficiency rental income calc, multi-unit financial-interest count, mixed-use square footage) -- none modeled today

**underwriting-review:399** (1 rules)
- Condition: The borr has a financial interest in more than 7 units w/in 2 blocks in an investment transaction
- Rationale: Niche FHA/FNM property-type family, absent from the corpus.
- What's needed: specific property-type/investment-eligibility facts (self-sufficiency rental income calc, multi-unit financial-interest count, mixed-use square footage) -- none modeled today

**underwriting-review:401** (1 rules)
- Condition: Residency status of the borrower was not determined using the 1003 & other applicable documentation
- Rationale: Citizenship/residency family; not modeled at all in this pilot (same gap flagged for asset-verification's G284, decision 017).
- What's needed: citizenship/residency-status documentation (USCIS determination, alien-registration evidence) -- not in corpus

**underwriting-review:402** (1 rules)
- Condition: The borrower(s) is a permanent resident alien, but permanent residency is not documented
- Rationale: Citizenship/residency family; not modeled at all in this pilot (same gap flagged for asset-verification's G284, decision 017).
- What's needed: citizenship/residency-status documentation (USCIS determination, alien-registration evidence) -- not in corpus

**underwriting-review:408** (1 rules)
- Condition: All title requirements not met when the borrower is a Living Trust
- Rationale: None of the 5 synthetic loans involves a trust-held title; niche fixture gap.
- What's needed: Living Trust Agreement / inter-vivos-revocable-trust documentation -- not in corpus

**underwriting-review:411** (1 rules)
- Condition: The applicant is a non-US citizen and does not have lawful residency status in the United States
- Rationale: Citizenship/residency family; not modeled at all in this pilot (same gap flagged for asset-verification's G284, decision 017).
- What's needed: citizenship/residency-status documentation (USCIS determination, alien-registration evidence) -- not in corpus

**underwriting-review:415** (1 rules)
- Condition: Trust Agreement not in the file where the borrower is a Living Trust
- Rationale: None of the 5 synthetic loans involves a trust-held title; niche fixture gap.
- What's needed: Living Trust Agreement / inter-vivos-revocable-trust documentation -- not in corpus

**underwriting-review:417** (1 rules)
- Condition: Alimony/child support/garnishments/other court ordered debts were excluded from DTI
- Rationale: Niche RHS credit-eligibility sub-condition, absent from the corpus.
- What's needed: delinquent-child-support repayment-history documentation -- not modeled

**underwriting-review:427** (1 rules)
- Condition: COE non-exempt & non-active duty borr w/ a pre-discharge claim pending & updated COE not obtained
- Rationale: Niche VA eligibility sub-conditions, absent from the corpus.
- What's needed: VA pending-disability-claim / National-Guard-service-days documentation -- not modeled

**underwriting-review:428** (1 rules)
- Condition: Manual UW & no comp factors or ext circumstances (if applic) required by VA on the VA Loan analysis
- Rationale: Niche VA underwriting-analysis form; loan 03 (the pilot's only VA loan) does not contain this document.
- What's needed: VA Form 26-6393 (VA Loan Analysis) -- not in any synthetic loan folder

**underwriting-review:429** (1 rules)
- Condition: No verif active duty funding fee exempt w/pend pre-discharge claim & no proposed/memorandum rating
- Rationale: Niche VA eligibility sub-conditions, absent from the corpus.
- What's needed: VA pending-disability-claim / National-Guard-service-days documentation -- not modeled

**underwriting-review:430** (1 rules)
- Condition: Non-supervised automatic lender & UW is not VA approved and/or registered as the lender's employee
- Rationale: Same institutional-staff-credential pattern as de_certification -- possible Bucket-C candidate, flagged not decided.
- What's needed: underwriter VA-approval/registration status (staff credential, not a loan fact)

**underwriting-review:432** (1 rules)
- Condition: VA Form 26-8937 was submitted to VA for information already listed on the COE
- Rationale: Niche VA benefits-verification form, absent from loan 03.
- What's needed: VA Form 26-8937 (Verification of VA Benefits) -- not in corpus

**underwriting-review:440** (1 rules)
- Condition: Non-profit entity funding the Affordable Second Section 501(c) determination not in file
- Rationale: Freddie Mac secondary-financing program family, absent from the corpus (same 501(c) document family flagged for asset-verification's G440, decision 017).
- What's needed: Affordable Second program documentation / IRS Section 501(c) determination letter -- not in corpus

**underwriting-review:442** (1 rules)
- Condition: The Affordable Second was provided by an unallowable agency
- Rationale: Freddie Mac secondary-financing program family, absent from the corpus (same 501(c) document family flagged for asset-verification's G440, decision 017).
- What's needed: Affordable Second program documentation / IRS Section 501(c) determination letter -- not in corpus

**underwriting-review:443** (1 rules)
- Condition: The source of the Affordable Second is the property seller or another interested party
- Rationale: Freddie Mac secondary-financing program family, absent from the corpus (same 501(c) document family flagged for asset-verification's G440, decision 017).
- What's needed: Affordable Second program documentation / IRS Section 501(c) determination letter -- not in corpus

**underwriting-review:444** (1 rules)
- Condition: The subject does not appear to be held in first lien position as required
- Rationale: Same secondary-financing family flagged in asset-verification (decision 017, G007/G267-271).
- What's needed: secondary/subordinate-financing note + terms documentation -- not in corpus

**underwriting-review:445** (1 rules)
- Condition: The subject has a seller funded affordable second without all eligibility requirements being met
- Rationale: Freddie Mac secondary-financing program family, absent from the corpus (same 501(c) document family flagged for asset-verification's G440, decision 017).
- What's needed: Affordable Second program documentation / IRS Section 501(c) determination letter -- not in corpus

**underwriting-review:446** (1 rules)
- Condition: The terms of the secondary financing were not provided
- Rationale: Same secondary-financing family flagged in asset-verification (decision 017, G007/G267-271).
- What's needed: secondary/subordinate-financing note + terms documentation -- not in corpus

**underwriting-review:450** (1 rules)
- Condition: Borr has an interest or employment w/ the builder, developer or seller in new construction purchase
- Rationale: Niche identity-of-interest family, absent from the corpus.
- What's needed: an identity-of-interest relationship fact (borrower's relationship to builder/developer/seller) -- not modeled

**underwriting-review:456** (1 rules)
- Condition: Military borrower unable to occupy prior to delivery & military orders not in the file to verify
- Rationale: Military-service-verification family, absent from the corpus.
- What's needed: DD Form 214 / military orders documentation -- not in corpus

**product-specific-check:36** (1 rules)
- Condition: The insurance policy does not include appropriate builder's risk coverage endorsement/riders
- Rationale: Comparison basis is a specific, named coverage type (builder's risk) — crisp presence check once the document exists; 'appropriate' is describing the pass/fail outcome, not the test itself.
- What's needed: a named insurance endorsement/rider doc (not in corpus)

**product-specific-check:39** (1 rules)
- Condition: Medical Professional guidelines are not met
- Rationale: Compound: the license-evidence half names a real, checkable document; the 'guidelines' half states no specific criteria and stays human — kept YELLOW per the crisp-half-survives convention (asset-verification G007's pattern).
- What's needed: medical-professional license verification doc (not in corpus)

**product-specific-check:109** (1 rules)
- Condition: LCO refi - All requirements not met for LTV over 95%
- Rationale: Has an explicit numeric threshold (95% LTV) as a bright-line gate; what else is specifically required beyond that isn't named in-row.
- What's needed: LCO-refi-over-95%-LTV requirement checklist (an SME-defined list)

**product-specific-check:118** (1 rules)
- Condition: Equity buy out from ex-spouse or other co-borrower without adequate documentation of the equity
- Rationale: Same family as G106 — FHA no-cash-out variant.
- What's needed: a legally-enforceable equity agreement doc (not in corpus)

**product-specific-check:146** (1 rules)
- Condition: The FHA/VA Amendatory Clause unsigned, not in the file or included in the sales contract
- Rationale: CONSIDERED for AmendatoryClauseShape (CHK-PRD-001), REJECTED as-is: this row (O-VA-50789, filed under agency O-VA even though the text says 'FHA/VA Amendatory Clause') tests THREE things — unsigned, not in file, not in the sales contract — while the shape's SPARQL only checks doc_present_fha_amendatory_clause AND mismo_mortgage_type=='FHA'. Two real gaps, not merely imprecision: (1) EXPECTED_DOCS_BY_PROGRAM only computes this fact for FHA loans — a VA loan never gets the fact at all, so the shape would silently never fire for VA loans regardless of wiring; (2) the shape has no signature test. Wiring this code today would be a false 'ready to build' of exactly the kind decision 018 warns against — needs real shape/extraction work first, not just an amq_exception_codes list edit.
- What's needed: shape needs widening to VA loans (fact is only computed when mismo_mortgage_type=='FHA' today; a VA loan never populates it) + a signature sub-check

**product-specific-check:156** (1 rules)
- Condition: Seller/servicer advanced pymts for the borr to then to refi after agreed pymts were advanced
- Rationale: Names a specific, checkable event sequence (advances, then refi) even though establishing 'agreed payments were advanced' as a defect still leans evidentiary.
- What's needed: servicer payment-advance records + refinance timing (not in corpus)

**product-specific-check:196** (1 rules)
- Condition: Short term ARM qualifying interest rate not calculated using the required method in ATR covered loan
- Rationale: Same family as G164 (FRD variant) — 'required method' names a real, defined calculation.
- What's needed: same as G164

**product-specific-check:235** (1 rules)
- Condition: All HomeReady req's for an LTV, CLTV, or HCLTV Ratio of 95.01 –97% not met
- Rationale: Same pattern as G109 — a genuine numeric band as the gate, the full requirement list unstated.
- What's needed: HomeReady 95.01-97% LTV-band requirement checklist (an SME-defined list)

**product-specific-check:327** (1 rules)
- Condition: Missing satisfactory inspection for required completion, repairs, alterations or conditions
- Rationale: eval_class=doc_presence targets 'appraisal' only because the condition text happens to contain the word 'appraisal' ('The appraisal was made subject to completion... an inspection certifying the repairs have been satisfactorily completed was not in the file') — the actual missing document is the completion INSPECTION, a distinct doc family absent from every synthetic loan. Presence of an ordinary appraisal (which every loan has) would false-PASS this.
- What's needed: a distinct 'satisfactory completion inspection' document — NOT the appraisal itself

**product-specific-check:329** (1 rules)
- Condition: New construction missing exhibits including 1992 CABO Model Energy Code (MEC) as applicable
- Rationale: Crisp, specific-document presence check.
- What's needed: a named specific compliance document (1992 CABO MEC exhibit, not in corpus)

**product-specific-check:461** (1 rules)
- Condition: Construction 90% or more complete missing components to be installed/completed after appraisal
- Rationale: Same generic-'appraisal'-keyword false positive as G327/G415 — the condition is specific to 90%-or-more-complete new construction, a gating fact this pilot doesn't track, and the missing list is not the appraisal document itself.
- What's needed: a components-to-be-completed list attached to the appraisal for 90%+-complete new construction — not modeled as a distinct fact

**product-specific-check:483** (1 rules)
- Condition: No supporting documentation of comp factors for debt ratio waiver in a purchase GUS refer/manual UW
- Rationale: See READY_TO_BUILD — the fact this row needs is already extracted and correctly populated; only a new shape + a purpose-type gate (to avoid colliding with G491's refinance sibling) is missing.
- What's needed: loan_purpose_1003 Purchase gate on a new shape (see READY_TO_BUILD)

**product-specific-check:485** (1 rules)
- Condition: Ratio thresholds not met in GUS refer/manual UW of a purchase to be eligible for a debt ratio waiver
- Rationale: CONSIDERED for RatioWaiverShape, NOT wired: this row's exact guideline pair (never stated numerically here) can't be confirmed against RatioWaiverShape's generic ratio>guideline test without an SME confirming 'ratio thresholds not met to be ELIGIBLE for a waiver' is the same real-world condition as 'ratios exceed the guideline and no waiver is on file' rather than a distinct maximum-ratio-ceiling-for-waiver-eligibility test. See G487 for the closer, still-rejected candidate and the decision doc's REJECTED section.
- What's needed: a purchase-vs-refi transaction-type gate on RatioWaiverShape (CHK-UND-002, currently ungated on transaction type) + confirmation this row's 'eligible for a waiver' test is the same as RatioWaiverShape's 'ratios exceed guideline' test, not a distinct waiver-eligibility-ceiling test

**product-specific-check:491** (1 rules)
- Condition: Comp factors to justify a debt ratio waiver not documented as required in a manual UW of a refinance
- Rationale: See READY_TO_BUILD — refinance sibling of G483, same fact, opposite purpose gate.
- What's needed: loan_purpose_1003 NOT-Purchase gate on a new shape (see READY_TO_BUILD)

**product-specific-check:598** (1 rules)
- Condition: Borr has ownership in another property, guidelines for HomePossible not met
- Rationale: 'Ownership interest in other residential property' is a crisp, named fact once an REO/owned-property schedule entity exists.
- What's needed: a financed/owned-properties schedule entity (not modeled — same systemic gap flagged in asset-verification's G240/G241)

**property-appraisal-review:2** (1 rules)
- Condition: No, the loan file did not contain an appraisal report as required
- Rationale: Same real check amq_compiler.py already auto-compiles as doc_presence for other rows in this block (appraisal doc type is already extracted) — this row's exact wording ('did not contain an appraisal report as required') just evades the compiler's NOT_IN_FILE_RE regex. A compiler regex-widening fix, not a data/fixture gap — kept YELLOW rather than blindly called GREEN, since the mechanism that would make it GREEN doesn't actually fire for this row today.
- What's needed: amq_compiler.py's NOT_IN_FILE_RE regex needs widening to also match 'did not contain ... as required' phrasing

**property-appraisal-review:4** (1 rules)
- Condition: No, the loan file did not contain an appraisal report as required
- Rationale: Same as G002 (FNM wording).
- What's needed: same regex-widening gap as G002

**property-appraisal-review:6** (1 rules)
- Condition: No, the loan file did not contain an appraisal report as required
- Rationale: Same as G002 (FRD wording).
- What's needed: same regex-widening gap as G002

**property-appraisal-review:8** (1 rules)
- Condition: No, the loan file did not contain an appraisal report as required
- Rationale: Same as G002 (RHS wording).
- What's needed: same regex-widening gap as G002

**property-appraisal-review:10** (1 rules)
- Condition: No, the loan file did not contain an appraisal report as required
- Rationale: Same as G002 (VA wording).
- What's needed: same regex-widening gap as G002

**property-appraisal-review:22** (1 rules)
- Condition: No comments found for existing adverse site conditions or external factors
- Rationale: Crisp presence check once 'Form 1033' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'No comments found for existing adverse site conditions or external factors'
- What's needed: 'Form 1033' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:57** (1 rules)
- Condition: Comparable sales do not have similar physical/legal characteristics when compared to subject
- Rationale: Crisp presence check once 'Form 1033' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Comparable sales do not have similar physical/legal characteristics when compared to subject'
- What's needed: 'Form 1033' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:65** (1 rules)
- Condition: Condo disaster impact assessment did not include damage to common elements, separate from unit
- Rationale: Matched project-documentation vocabulary ('Condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Condo disaster impact assessment did not include damage to common elements, separate from unit'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:72** (1 rules)
- Condition: CU score is =<2.5; prop is one unit detach, attach, condo & "data integrity" concerns not met
- Rationale: Bucket-C-style candidate (decision 016 precedent): references 'CU', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- What's needed: live lookup against an external system/database this pilot has no integration with ('CU')

**property-appraisal-review:74** (1 rules)
- Condition: Condo HOA receives income from leasing commercial parking that exceed 10% of its budgeted income
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Condo HOA receives income from leasing commercial parking that exceed 10% of its budgeted income'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:75** (1 rules)
- Condition: Condo is a timeshare, tenancy in common or unit ownership is identified as an investment opportunity
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Condo is a timeshare, tenancy in common or unit ownership is identified as an investment opportunity'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:77** (1 rules)
- Condition: Condo review revealed characteristics that would be considered a condotel or transient housing
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Condo review revealed characteristics that would be considered a condotel or transient housing'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:78** (1 rules)
- Condition: Documentation supporting project is not a condotel or similar transient housing not in the file
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Documentation supporting project is not a condotel or similar transient housing not in the file'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:79** (1 rules)
- Condition: Missing documentation to determine project is not a condotel
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Missing documentation to determine project is not a condotel'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:80** (1 rules)
- Condition: Project req/LTV limits not met to allow for streamlined project review
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Project req/LTV limits not met to allow for streamlined project review'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:81** (1 rules)
- Condition: Subject of action causing project to not exist/termination/deconversion/legal structure dissolution
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Subject of action causing project to not exist/termination/deconversion/legal structure dissolution'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:82** (1 rules)
- Condition: The condo HOA or mgt company/agent receives revenue or pays expenses for hotel type services
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The condo HOA or mgt company/agent receives revenue or pays expenses for hotel type services'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:83** (1 rules)
- Condition: The condominium HOA TIN was not obtained
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The condominium HOA TIN was not obtained'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:84** (1 rules)
- Condition: The project did not meet single entity ownership limits
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The project did not meet single entity ownership limits'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:85** (1 rules)
- Condition: Unable to locate the project approval certificate
- Rationale: Crisp presence check once 'project approval certificate' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Unable to locate the project approval certificate'
- What's needed: 'project approval certificate' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:90** (1 rules)
- Condition: CU comps tab messages & data alerts review reveal quality & condition ratings inconsistent to market
- Rationale: Bucket-C-style candidate (decision 016 precedent): references 'CU', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- What's needed: live lookup against an external system/database this pilot has no integration with ('CU')

**property-appraisal-review:91** (1 rules)
- Condition: Information provided in CU or other sources did not confirm the sales provided were appropriate
- Rationale: Bucket-C-style candidate (decision 016 precedent): references 'CU', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- What's needed: live lookup against an external system/database this pilot has no integration with ('CU')

**property-appraisal-review:92** (1 rules)
- Condition: No extra steps taken ensuring property characteristics reported correct regardless of CU risk score
- Rationale: Bucket-C-style candidate (decision 016 precedent): references 'CU', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- What's needed: live lookup against an external system/database this pilot has no integration with ('CU')

**property-appraisal-review:94** (1 rules)
- Condition: CU 2.6 + without ensuring comps appropriate, physically similar in site, GLA, & proper adjustments
- Rationale: Bucket-C-style candidate (decision 016 precedent): references 'CU', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- What's needed: live lookup against an external system/database this pilot has no integration with ('CU')

**property-appraisal-review:107** (1 rules)
- Condition: (Best Practice) Form 1076A not used to ensure project meets temp req's for condo & co-op projects
- Rationale: Crisp presence check once 'Project Questionnaire' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: "(Best Practice) Form 1076A not used to ensure project meets temp req's for condo & co-op projects"
- What's needed: 'Project Questionnaire' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:108** (1 rules)
- Condition: CPM Approved by FNMA in DU lost status due to credit report exp or changes to CPM ID/project/address
- Rationale: Crisp presence check once 'Project Questionnaire' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'CPM Approved by FNMA in DU lost status due to credit report exp or changes to CPM ID/project/address'
- What's needed: 'Project Questionnaire' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:109** (1 rules)
- Condition: CPM has a delivery restriction with a CPM Approved by FNMA msg in DU without evidence of compliance
- Rationale: Crisp presence check once 'Project Questionnaire' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'CPM has a delivery restriction with a CPM Approved by FNMA msg in DU without evidence of compliance'
- What's needed: 'Project Questionnaire' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:110** (1 rules)
- Condition: CPM project approved status not retained as of note date & CPM Approved by FNMA DU msg not received
- Rationale: Crisp presence check once 'Project Questionnaire' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'CPM project approved status not retained as of note date & CPM Approved by FNMA DU msg not received'
- What's needed: 'Project Questionnaire' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:111** (1 rules)
- Condition: Detached condo did not meet property/appraisal standards, insurance, &/or priority lien requirements
- Rationale: Crisp presence check once 'Project Questionnaire' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Detached condo did not meet property/appraisal standards, insurance, &/or priority lien requirements'
- What's needed: 'Project Questionnaire' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:112** (1 rules)
- Condition: Missing Condo Project Questionnaire, Form 1076, with deferred maintenance addendum as recommended
- Rationale: Crisp presence check once 'Project Questionnaire' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Missing Condo Project Questionnaire, Form 1076, with deferred maintenance addendum as recommended'
- What's needed: 'Project Questionnaire' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:114** (1 rules)
- Condition: Project review is waived without meeting all property eligibility requirements
- Rationale: Crisp presence check once 'Project Questionnaire' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Project review is waived without meeting all property eligibility requirements'
- What's needed: 'Project Questionnaire' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:115** (1 rules)
- Condition: Project review waiver exercised where project is terminating or involved in insolvency proceedings
- Rationale: Crisp presence check once 'Project Questionnaire' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Project review waiver exercised where project is terminating or involved in insolvency proceedings'
- What's needed: 'Project Questionnaire' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:116** (1 rules)
- Condition: The status of the subject condo or co-op project is “Unavailable” in Condo Project Manager, CPM
- Rationale: Crisp presence check once 'Project Questionnaire' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'The status of the subject condo or co-op project is “Unavailable” in Condo Project Manager, CPM'
- What's needed: 'Project Questionnaire' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:153** (1 rules)
- Condition: Compliance Inspection Report, VA Form 26-1839, including photographs not in file
- Rationale: Crisp presence check once 'Compliance Inspection Report' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Compliance Inspection Report, VA Form 26-1839, including photographs not in file'
- What's needed: 'Compliance Inspection Report' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:194** (1 rules)
- Condition: Conditional Commitment DE Statement of Appraised Value, form HUD-92800.5B, not in the file
- Rationale: Crisp presence check once 'HUD-92800.5B' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Conditional Commitment DE Statement of Appraised Value, form HUD-92800.5B, not in the file'
- What's needed: 'HUD-92800.5B' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:196** (1 rules)
- Condition: A fully completed Form HUD-9992 signed & dated by an eligible submission source is not in the file
- Rationale: Crisp presence check once 'HUD-9992' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'A fully completed Form HUD-9992 signed & dated by an eligible submission source is not in the file'
- What's needed: 'HUD-9992' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:197** (1 rules)
- Condition: Condo project percent individual own concentration & units in arrears for assoc fees req's not met
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: "Condo project percent individual own concentration & units in arrears for assoc fees req's not met"
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:199** (1 rules)
- Condition: Supporting documentation the condo project is not a condotel or other transient housing not in file
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Supporting documentation the condo project is not a condotel or other transient housing not in file'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:200** (1 rules)
- Condition: A cursory or comprehensive review of the appraisal & VeroSCORE not conducted as applicable
- Rationale: Bucket-C-style candidate (decision 016 precedent): references 'VeroSCORE', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- What's needed: live lookup against an external system/database this pilot has no integration with ('VeroSCORE')

**property-appraisal-review:202** (1 rules)
- Condition: The AMS had a critical, severe or high alert that was not addressed in WebLGY notes
- Rationale: Bucket-C-style candidate (decision 016 precedent): references 'AMS', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- What's needed: live lookup against an external system/database this pilot has no integration with ('AMS')

**property-appraisal-review:204** (1 rules)
- Condition: Vet req'd ROV after NOV was issued & submitted to RLC without market data research/recommendation
- Rationale: amq_compiler.py's DOC_KEYWORDS matched 'NOV' and pointed this at the va_nov doc type, but the ACTUAL missing thing per the full exception_description is evidence of the SAR's market-data research and recommendation to the RLC — the NOV itself already exists in this row's premise. Reclassified from the mechanical GREEN this eval_target would otherwise produce: a real compiler mis-mapping, not a genuine va_nov-presence check — same class of finding as the 'appraisal' generic-target issue this triage's module docstring documents at length.
- What's needed: a distinct 'SAR researched market data and provided a recommendation' evidence fact (not modeled — different from mere va_nov/NOV presence, which already exists)

**property-appraisal-review:206** (1 rules)
- Condition: All leasehold lease requirements were not met where the HOA or Co-op Corporation is the lessee
- Rationale: Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'All leasehold lease requirements were not met where the HOA or Co-op Corporation is the lessee'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:207** (1 rules)
- Condition: All leasehold lease requirements were not met where the borrower is the lessee
- Rationale: Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'All leasehold lease requirements were not met where the borrower is the lessee'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:209** (1 rules)
- Condition: Lease includes borr option to purchase & req's not met to establish the purchase price of the land
- Rationale: Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: "Lease includes borr option to purchase & req's not met to establish the purchase price of the land"
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:210** (1 rules)
- Condition: Loan not 1st lien in property improvements & the borrower's rights in leasehold interest in the land
- Rationale: Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: "Loan not 1st lien in property improvements & the borrower's rights in leasehold interest in the land"
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:222** (1 rules)
- Condition: Cost, income, &/or sales comparison approaches not used to determine the ADU contributory value
- Rationale: Matched project-documentation vocabulary ('ADU') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Cost, income, &/or sales comparison approaches not used to determine the ADU contributory value'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:228** (1 rules)
- Condition: Appraiser’s response to the ROV not included in a revised version of the appraisal & logged in FHAC
- Rationale: Bucket-C-style candidate (decision 016 precedent): references 'FHAC', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- What's needed: live lookup against an external system/database this pilot has no integration with ('FHAC')

**property-appraisal-review:247** (1 rules)
- Condition: The appraisal was not performed by an appraiser on the HUD roster
- Rationale: Bucket-C-style candidate (decision 016 precedent): references 'HUD roster', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- What's needed: live lookup against an external system/database this pilot has no integration with ('HUD roster')

**property-appraisal-review:253** (1 rules)
- Condition: 2-4 rental income property missing Form 1025, Small Residential Income Property Appraisal Report
- Rationale: Crisp presence check once 'Form 1025' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: '2-4 rental income property missing Form 1025, Small Residential Income Property Appraisal Report'
- What's needed: 'Form 1025' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:255** (1 rules)
- Condition: A hybrid appraisal was used in an ineligible transaction type
- Rationale: Matched project-documentation vocabulary ('hybrid appraisal') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'A hybrid appraisal was used in an ineligible transaction type'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:256** (1 rules)
- Condition: A hybrid appraisal was used that did not meet all of the required preconditions
- Rationale: Matched project-documentation vocabulary ('hybrid appraisal') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'A hybrid appraisal was used that did not meet all of the required preconditions'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:258** (1 rules)
- Condition: Appraisal is over 4 mos but under 12 mos on the date of closing without reinspection on Form 1004D
- Rationale: Crisp presence check once 'Form 1004D' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Appraisal is over 4 mos but under 12 mos on the date of closing without reinspection on Form 1004D'
- What's needed: 'Form 1004D' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:260** (1 rules)
- Condition: Desktop appraisal used in a loan that was not a primary SFR purchase with an LTV of 90% or less
- Rationale: Matched project-documentation vocabulary ('Desktop appraisal') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Desktop appraisal used in a loan that was not a primary SFR purchase with an LTV of 90% or less'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:261** (1 rules)
- Condition: Form 1007, comparable rent schedule not in file for 1 unit investment property
- Rationale: Crisp presence check once 'Form 1007' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Form 1007, comparable rent schedule not in file for 1 unit investment property'
- What's needed: 'Form 1007' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:270** (1 rules)
- Condition: The appraisal was not completed within 180 days of loan closing
- Rationale: WORTH SME REVIEW, closest near-miss in this entire block to an existing shape: RHS's 180-day appraisal-age rule tests the EXACT SAME fact StaleAppraisalShape already computes (appraisal_age_days_at_closing), just a different threshold (180, not 120) and — unlike StaleAppraisalShape — this RHS row states no recertification-of-value exception that would cure it. NOT proposed as a blind extension of StaleAppraisalShape (different threshold + different cure condition would change the shape's actual logic, not just its exception-code list) — flagged as the strongest build candidate in the block for a NEW, RHS-specific check reusing the same already-extracted field.
- What's needed: none for the age math itself — only the 180-vs-120-day threshold and the missing recertification-cures-it exception need SME confirmation before wiring

**property-appraisal-review:278** (1 rules)
- Condition: Public water supply unsafe per appraiser/health auth & evidence it's safe prior to close not in file
- Rationale: Reclassified from the family classifier's default RED match (incidental word 'deemed'): the checkable condition is presence of evidence the water supply was made safe prior to closing — a crisp presence check once the doc type exists.
- What's needed: safety-evidence documentation for a public water supply deemed unsafe (not modeled)

**property-appraisal-review:279** (1 rules)
- Condition: Soil poisoning used to treat termites without documentation it will not endanger water quality
- Rationale: Topically near TermiteInspectionShape (mentions 'termites') but tests a DIFFERENT fact — whether soil-poisoning treatment was shown not to endanger water quality — not termite-inspection-report presence. Not a match; kept as its own YELLOW group.
- What's needed: post-treatment water-safety documentation (not modeled; distinct from inspection presence)

**property-appraisal-review:289** (1 rules)
- Condition: Income not converted from ground lease to leased fee value correctly
- Rationale: Matched project-documentation vocabulary ('community land trust') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Income not converted from ground lease to leased fee value correctly'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:291** (1 rules)
- Condition: A completed, signed, and dated form HUD-9991, Condo Questionnaire,  is not in the file
- Rationale: Crisp presence check once 'HUD-9991' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'A completed, signed, and dated form HUD-9991, Condo Questionnaire,  is not in the file'
- What's needed: 'HUD-9991' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:292** (1 rules)
- Condition: Analysis of the unit, project amenities & HOA purpose not provided
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Analysis of the unit, project amenities & HOA purpose not provided'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:293** (1 rules)
- Condition: Condo project not on list of FHA Approved Condominium Projects at time of case number assignment
- Rationale: Bucket-C-style candidate (decision 016 precedent): references 'FHA Approved Condominium', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- What's needed: live lookup against an external system/database this pilot has no integration with ('FHA Approved Condominium')

**property-appraisal-review:295** (1 rules)
- Condition: Monthly PITIA not calculated correctly &/or did not include all housing components
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Monthly PITIA not calculated correctly &/or did not include all housing components'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:296** (1 rules)
- Condition: No condo documentation supporting project approval or acceptance by HUD, VA, FNMA or FHLMC
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'No condo documentation supporting project approval or acceptance by HUD, VA, FNMA or FHLMC'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:298** (1 rules)
- Condition: Project approval not done for site condo, waiver/exception not in the file
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Project approval not done for site condo, waiver/exception not in the file'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:299** (1 rules)
- Condition: Security Instrument did not include the required PUD/Condominium rider or the rider was not signed
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Security Instrument did not include the required PUD/Condominium rider or the rider was not signed'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:300** (1 rules)
- Condition: The FHA Condo ID was not entered in the FHA Connection (FHAC) Case Assignment screen
- Rationale: Bucket-C-style candidate (decision 016 precedent): references 'FHA Connection', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- What's needed: live lookup against an external system/database this pilot has no integration with ('FHA Connection')

**property-appraisal-review:301** (1 rules)
- Condition: The condo project was not approved under HRAP or DELRAP approval process
- Rationale: Bucket-C-style candidate (decision 016 precedent): references 'HRAP', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- What's needed: live lookup against an external system/database this pilot has no integration with ('HRAP')

**property-appraisal-review:302** (1 rules)
- Condition: The file did not document that the subject condo unit met the definition for a site condominium
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The file did not document that the subject condo unit met the definition for a site condominium'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:303** (1 rules)
- Condition: The percentage of owner-occupied units in the subject condominium project did not meet requirements
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The percentage of owner-occupied units in the subject condominium project did not meet requirements'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:304** (1 rules)
- Condition: The subject condominium is in an ineligible project
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The subject condominium is in an ineligible project'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:305** (1 rules)
- Condition: The subject property is in an ineligible condominium project type
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The subject property is in an ineligible condominium project type'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:306** (1 rules)
- Condition: The subject's condominium project was not approved as applicable
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: "The subject's condominium project was not approved as applicable"
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:307** (1 rules)
- Condition: Underwriting review of the condominium project not conducted as required
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Underwriting review of the condominium project not conducted as required'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:308** (1 rules)
- Condition: Condo/co-op financial documents not obtained to confirm the association has ability to fund repairs
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Condo/co-op financial documents not obtained to confirm the association has ability to fund repairs'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:309** (1 rules)
- Condition: Condo/co-op project has deferred maintenance or has regulatory directive to repair unsafe conditions
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Condo/co-op project has deferred maintenance or has regulatory directive to repair unsafe conditions'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:312** (1 rules)
- Condition: Project missing engineer/inspection report, COO, or other evidence of completed repairs/maintenance
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Project missing engineer/inspection report, COO, or other evidence of completed repairs/maintenance'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:314** (1 rules)
- Condition: Special assessment is safety/sound/structural or livability & repairs incomplete or adverse impact
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Special assessment is safety/sound/structural or livability & repairs incomplete or adverse impact'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:315** (1 rules)
- Condition: [Best Practice] Last 5 yrs project inspections/certifications not reviewed for deferred maintenance
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: '[Best Practice] Last 5 yrs project inspections/certifications not reviewed for deferred maintenance'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:316** (1 rules)
- Condition: [Best Practice] The past 6 months of a condo/co-op project’s HOA meeting minutes were not reviewed
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: '[Best Practice] The past 6 months of a condo/co-op project’s HOA meeting minutes were not reviewed'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:317** (1 rules)
- Condition: Condo or co-op project has recreational leases or mandatory memberships that require paying dues
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Condo or co-op project has recreational leases or mandatory memberships that require paying dues'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:320** (1 rules)
- Condition: Sponsor ownership/Coop shares not documented or outside of allotted %.  20%  Portfolio - 40% Agency
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Sponsor ownership/Coop shares not documented or outside of allotted %.  20%  Portfolio - 40% Agency'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:321** (1 rules)
- Condition: The condo/co-op project is subject of litigation without all eligible minor litigation criteria met
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The condo/co-op project is subject of litigation without all eligible minor litigation criteria met'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:322** (1 rules)
- Condition: The project did not meet single entity ownership limits
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The project did not meet single entity ownership limits'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:323** (1 rules)
- Condition: Total nonresidential or commercial space exceeds 35% in a condo or cooperative
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Total nonresidential or commercial space exceeds 35% in a condo or cooperative'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:324** (1 rules)
- Condition: A Questionnaire/Approval worksheet is not found in the file and is required
- Rationale: Crisp presence check once 'condo questionnaire' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'A Questionnaire/Approval worksheet is not found in the file and is required'
- What's needed: 'condo questionnaire' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:325** (1 rules)
- Condition: CPM was not used to conduct the condo project full review without being exempt or receiving a waiver
- Rationale: Bucket-C-style candidate (decision 016 precedent): references 'CPM', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- What's needed: live lookup against an external system/database this pilot has no integration with ('CPM')

**property-appraisal-review:326** (1 rules)
- Condition: Limited or full condo project review not conducted as applicable
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Limited or full condo project review not conducted as applicable'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:327** (1 rules)
- Condition: More than 15% of the total units in a project are 60 days or more past due on HOA fees
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'More than 15% of the total units in a project are 60 days or more past due on HOA fees'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:328** (1 rules)
- Condition: No evidence the project  assoc has a minimum annual budgeted replacement reserve allocation of 10%
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'No evidence the project  assoc has a minimum annual budgeted replacement reserve allocation of 10%'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:330** (1 rules)
- Condition: Over 15% of total units in a project are 60 days or more past due in pymts of special assessments
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Over 15% of total units in a project are 60 days or more past due in pymts of special assessments'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:331** (1 rules)
- Condition: Project subject to ground lease w/out protected lender financial interest in a condemnation/similar
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Project subject to ground lease w/out protected lender financial interest in a condemnation/similar'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:332** (1 rules)
- Condition: The Condo, CO-OP, or PUD does not meet the AUS project requirements
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The Condo, CO-OP, or PUD does not meet the AUS project requirements'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:333** (1 rules)
- Condition: The Pro Rata form is missing or is incomplete/inaccurate
- Rationale: Crisp presence check once 'Pro Rata form' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'The Pro Rata form is missing or is incomplete/inaccurate'
- What's needed: 'Pro Rata form' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:334** (1 rules)
- Condition: The co-op sellers affidavit was not located and/or properly executed
- Rationale: Crisp presence check once 'sellers affidavit' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'The co-op sellers affidavit was not located and/or properly executed'
- What's needed: 'sellers affidavit' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:335** (1 rules)
- Condition: The file did not contain a Co-op Corporation’s Recognition Agreement
- Rationale: Crisp presence check once 'Recognition Agreement' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'The file did not contain a Co-op Corporation’s Recognition Agreement'
- What's needed: 'Recognition Agreement' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:336** (1 rules)
- Condition: The file did not include the CPM decision and unexpired CPM Certification
- Rationale: Bucket-C-style candidate (decision 016 precedent): references 'CPM', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- What's needed: live lookup against an external system/database this pilot has no integration with ('CPM')

**property-appraisal-review:337** (1 rules)
- Condition: The stock cert is not found and/or does not match the # of shares on the loan security agreement
- Rationale: Crisp presence check once 'stock cert' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'The stock cert is not found and/or does not match the # of shares on the loan security agreement'
- What's needed: 'stock cert' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:339** (1 rules)
- Condition: Unit is not on a separate meter, no evidence this is common & project budget includes utility funds
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Unit is not on a separate meter, no evidence this is common & project budget includes utility funds'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:340** (1 rules)
- Condition: Condo exempt from review without being a 2-4, detached, Freddie owned NCO refi, or Refi Possible
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Condo exempt from review without being a 2-4, detached, Freddie owned NCO refi, or Refi Possible'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:341** (1 rules)
- Condition: Exempt from review & is a condotel, houseboat, timeshare, manufactured or segmented owner project
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Exempt from review & is a condotel, houseboat, timeshare, manufactured or segmented owner project'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:343** (1 rules)
- Condition: The condominium unit did not meet the glossary definition of a detached condominium unit
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The condominium unit did not meet the glossary definition of a detached condominium unit'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:359** (1 rules)
- Condition: A desktop appraisal was used in a loan that had an ineligible property or mortgage type
- Rationale: Matched project-documentation vocabulary ('desktop appraisal') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'A desktop appraisal was used in a loan that had an ineligible property or mortgage type'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:360** (1 rules)
- Condition: A desktop appraisal was used in a loan with an LTV over 90%
- Rationale: Matched project-documentation vocabulary ('desktop appraisal') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'A desktop appraisal was used in a loan with an LTV over 90%'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:361** (1 rules)
- Condition: A floor plan and a building sketch not provided as required for the use of desktop Guide Form 70D
- Rationale: Crisp presence check once 'Form 70D' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'A floor plan and a building sketch not provided as required for the use of desktop Guide Form 70D'
- What's needed: 'Form 70D' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:362** (1 rules)
- Condition: Desktop appraisal Guide Form 70D was not fully completed and/or was not in the file
- Rationale: Crisp presence check once 'Form 70D' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Desktop appraisal Guide Form 70D was not fully completed and/or was not in the file'
- What's needed: 'Form 70D' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:363** (1 rules)
- Condition: Desktop not upgraded to an interior/exterior where an adequate appraisal could not be developed
- Rationale: Matched project-documentation vocabulary ('desktop appraisal') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Desktop not upgraded to an interior/exterior where an adequate appraisal could not be developed'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:371** (1 rules)
- Condition: Form HUD-92564-CN not provided to the applicant with evidence maintained in the permanent loan file
- Rationale: Crisp presence check once 'HUD-92564' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Form HUD-92564-CN not provided to the applicant with evidence maintained in the permanent loan file'
- What's needed: 'HUD-92564' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:385** (1 rules)
- Condition: Appraiser not given Form 26-1805 & all other req'd documents on the same day the assignment was made
- Rationale: Crisp presence check once 'Form 26' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: "Appraiser not given Form 26-1805 & all other req'd documents on the same day the assignment was made"
- What's needed: 'Form 26' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:398** (1 rules)
- Condition: A default under the leasehold estate will terminate the sublease securing the mortgage
- Rationale: Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'A default under the leasehold estate will terminate the sublease securing the mortgage'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:399** (1 rules)
- Condition: Lease agreement or ground lease terms, restrictions & conditions not provided for leasehold property
- Rationale: Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Lease agreement or ground lease terms, restrictions & conditions not provided for leasehold property'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:400** (1 rules)
- Condition: Leasehold term not at least 5 yrs past maturity date & fee simple title not vested to borr earlier
- Rationale: Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Leasehold term not at least 5 yrs past maturity date & fee simple title not vested to borr earlier'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:401** (1 rules)
- Condition: Mtg subject to leasehold estate, conditions and lease requirements not met
- Rationale: Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Mtg subject to leasehold estate, conditions and lease requirements not met'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:403** (1 rules)
- Condition: Req's not met for establishing the purchase price of the land in leasehold with option to purchase
- Rationale: Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: "Req's not met for establishing the purchase price of the land in leasehold with option to purchase"
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:404** (1 rules)
- Condition: The leasehold estate & improvements did not constitute real property subject to the mortgage lien
- Rationale: Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The leasehold estate & improvements did not constitute real property subject to the mortgage lien'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:405** (1 rules)
- Condition: The leasehold estate & mortgage will be impaired by a merger of title between the lessor and lessee
- Rationale: Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The leasehold estate & mortgage will be impaired by a merger of title between the lessor and lessee'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:406** (1 rules)
- Condition: The leasehold estate lease payments/assessments were unpaid or were in default
- Rationale: Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The leasehold estate lease payments/assessments were unpaid or were in default'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:407** (1 rules)
- Condition: The property is subject to a leasehold estate and is an ineligible property type
- Rationale: Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The property is subject to a leasehold estate and is an ineligible property type'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:408** (1 rules)
- Condition: The provisions of the lease associated with the leasehold estate did not meet requirements
- Rationale: Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The provisions of the lease associated with the leasehold estate did not meet requirements'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:410** (1 rules)
- Condition: Appraiser indicated on Form 1004D that the property value has declined without a new appraisal
- Rationale: Crisp presence check once 'Form 1004D' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Appraiser indicated on Form 1004D that the property value has declined without a new appraisal'
- What's needed: 'Form 1004D' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:421** (1 rules)
- Condition: The subject section of the appraisal was missing components and/or contained incorrect information
- Rationale: Matched project-documentation vocabulary ('parcel') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The subject section of the appraisal was missing components and/or contained incorrect information'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:431** (1 rules)
- Condition: Subject has multiple parcels and appraisal not subject to all of the parcels being on one deed
- Rationale: Matched project-documentation vocabulary ('parcel') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Subject has multiple parcels and appraisal not subject to all of the parcels being on one deed'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:452** (1 rules)
- Condition: Appraiser did not include a description, general condition & room count for the ADU
- Rationale: Matched project-documentation vocabulary ('ADU') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Appraiser did not include a description, general condition & room count for the ADU'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:453** (1 rules)
- Condition: Comparable requirements not met for an ADU that is illegal & does not comply with zoning & land use
- Rationale: Matched project-documentation vocabulary ('ADU') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Comparable requirements not met for an ADU that is illegal & does not comply with zoning & land use'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:455** (1 rules)
- Condition: The subject is an ineligible property type to have an ADU
- Rationale: Matched project-documentation vocabulary ('ADU') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The subject is an ineligible property type to have an ADU'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:456** (1 rules)
- Condition: ADU does not comply with zoning requirements or meet the additional conditions to be eligible
- Rationale: Matched project-documentation vocabulary ('ADU') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'ADU does not comply with zoning requirements or meet the additional conditions to be eligible'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:457** (1 rules)
- Condition: ADU not subordinate in size to the primary dwelling &/or did not have the req'd separate features
- Rationale: Matched project-documentation vocabulary ('ADU') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: "ADU not subordinate in size to the primary dwelling &/or did not have the req'd separate features"
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:462** (1 rules)
- Condition: The ADU is a HUD Code manufactured home and the additional requirements applicable were not met
- Rationale: Matched project-documentation vocabulary ('ADU') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The ADU is a HUD Code manufactured home and the additional requirements applicable were not met'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:463** (1 rules)
- Condition: The ADU was included with the Gross Living Area calculation of the primary dwelling
- Rationale: Matched project-documentation vocabulary ('ADU') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The ADU was included with the Gross Living Area calculation of the primary dwelling'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:464** (1 rules)
- Condition: The subject is an ineligible property type to have an ADU
- Rationale: Matched project-documentation vocabulary ('ADU') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The subject is an ineligible property type to have an ADU'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:465** (1 rules)
- Condition: Ext-only/desktop with down pymt less than 20% & case unassigned by VA for less than 7 business days
- Rationale: Matched project-documentation vocabulary ('desktop appraisal') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Ext-only/desktop with down pymt less than 20% & case unassigned by VA for less than 7 business days'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:466** (1 rules)
- Condition: Exterior-only or desktop appraisal used in a purchase where the lender is not LAPP approved
- Rationale: Matched project-documentation vocabulary ('desktop appraisal') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Exterior-only or desktop appraisal used in a purchase where the lender is not LAPP approved'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:467** (1 rules)
- Condition: Exterior-only or desktop appraisal used where the purchase price exceeds the conforming loan limit
- Rationale: Matched project-documentation vocabulary ('desktop appraisal') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Exterior-only or desktop appraisal used where the purchase price exceeds the conforming loan limit'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:468** (1 rules)
- Condition: Exterior-only/desktop use in a condo, leasehold, or a SFR undergoing renovation
- Rationale: Matched project-documentation vocabulary ('desktop appraisal') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Exterior-only/desktop use in a condo, leasehold, or a SFR undergoing renovation'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:471** (1 rules)
- Condition: Rural designation changed to non-rural without meeting all criteria to be approved and guaranteed
- Rationale: Matched project-documentation vocabulary ('rural area designat') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Rural designation changed to non-rural without meeting all criteria to be approved and guaranteed'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:472** (1 rules)
- Condition: The subject property is not in an area designated as rural by RHS
- Rationale: Matched project-documentation vocabulary ('rural area designat') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The subject property is not in an area designated as rural by RHS'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:475** (1 rules)
- Condition: Comparable selection requirements not met for new PUD or new or recently converted Condo projects
- Rationale: Matched project-documentation vocabulary ('PUD') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Comparable selection requirements not met for new PUD or new or recently converted Condo projects'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:476** (1 rules)
- Condition: Comps not within subjects established PUD/Condo project when they are the best indicators of value
- Rationale: Matched project-documentation vocabulary ('PUD') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Comps not within subjects established PUD/Condo project when they are the best indicators of value'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:490** (1 rules)
- Condition: The subject accessory dwelling unit (ADU) is ineligible due to potentially creating rental income
- Rationale: Matched project-documentation vocabulary ('ADU') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The subject accessory dwelling unit (ADU) is ineligible due to potentially creating rental income'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:491** (1 rules)
- Condition: The subject property has multiple parcels without all requirements being met
- Rationale: Matched project-documentation vocabulary ('parcel') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The subject property has multiple parcels without all requirements being met'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:498** (1 rules)
- Condition: Each of the multiple parcels not conveyed in entirety with the mortgage being the first lien on each
- Rationale: Matched project-documentation vocabulary ('parcel') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Each of the multiple parcels not conveyed in entirety with the mortgage being the first lien on each'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:499** (1 rules)
- Condition: No documentation non-adjoining parcels without the residence cannot be improved with a dwelling
- Rationale: Matched project-documentation vocabulary ('parcel') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'No documentation non-adjoining parcels without the residence cannot be improved with a dwelling'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:500** (1 rules)
- Condition: Non-adjoining parcels are not separated due to a road, waterfront access or similar as allowable
- Rationale: Matched project-documentation vocabulary ('parcel') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Non-adjoining parcels are not separated due to a road, waterfront access or similar as allowable'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:503** (1 rules)
- Condition: The subject's additional parcels were not adjoining and/or did not have the same basic zoning
- Rationale: Matched project-documentation vocabulary ('parcel') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: "The subject's additional parcels were not adjoining and/or did not have the same basic zoning"
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:507** (1 rules)
- Condition: Cost, income, &/or sales comparison approaches not used to determine the ADU contributory value
- Rationale: Matched project-documentation vocabulary ('ADU') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Cost, income, &/or sales comparison approaches not used to determine the ADU contributory value'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:516** (1 rules)
- Condition: The appraisal did not report the property rights as fee simple or leasehold
- Rationale: Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The appraisal did not report the property rights as fee simple or leasehold'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:534** (1 rules)
- Condition: The appraiser did not identify the name of the PUD and/or check the PUD box on the appraisal form
- Rationale: Matched project-documentation vocabulary ('PUD') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The appraiser did not identify the name of the PUD and/or check the PUD box on the appraisal form'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:537** (1 rules)
- Condition: Special feature code 801 was not included at delivery where value acceptance was exercised
- Rationale: Matched project-documentation vocabulary ('value acceptance') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Special feature code 801 was not included at delivery where value acceptance was exercised'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:538** (1 rules)
- Condition: The loan had a characteristic that was not eligible for value acceptance
- Rationale: Matched project-documentation vocabulary ('value acceptance') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The loan had a characteristic that was not eligible for value acceptance'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:539** (1 rules)
- Condition: The value acceptance offer is over 4 months old on the Note date
- Rationale: Matched project-documentation vocabulary ('value acceptance') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The value acceptance offer is over 4 months old on the Note date'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:540** (1 rules)
- Condition: Value acceptance was exercised when rental income from the subject property is used
- Rationale: Matched project-documentation vocabulary ('value acceptance') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Value acceptance was exercised when rental income from the subject property is used'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:541** (1 rules)
- Condition: Value acceptance was exercised where an appraisal was obtained for the transaction
- Rationale: Matched project-documentation vocabulary ('value acceptance') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Value acceptance was exercised where an appraisal was obtained for the transaction'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:542** (1 rules)
- Condition: Value acceptance was exercised where it would have been prudent or required to obtain an appraisal
- Rationale: Matched project-documentation vocabulary ('value acceptance') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Value acceptance was exercised where it would have been prudent or required to obtain an appraisal'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:543** (1 rules)
- Condition: Data collection items fail eligibility & a professional report confirming eligibility not obtained
- Rationale: Matched project-documentation vocabulary ('value acceptance') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Data collection items fail eligibility & a professional report confirming eligibility not obtained'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:544** (1 rules)
- Condition: Form 1004D and Completion Alternatives is not in the file as applicable for repairs or alterations
- Rationale: Crisp presence check once 'Form 1004D' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Form 1004D and Completion Alternatives is not in the file as applicable for repairs or alterations'
- What's needed: 'Form 1004D' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:545** (1 rules)
- Condition: Property data collection was not obtained after the initial DU offer and prior to the note date
- Rationale: Matched project-documentation vocabulary ('value acceptance') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Property data collection was not obtained after the initial DU offer and prior to the note date'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:546** (1 rules)
- Condition: Property data collection was not submitted to the Property Data API prior to the note date
- Rationale: Bucket-C-style candidate (decision 016 precedent): references 'Property Data API', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- What's needed: live lookup against an external system/database this pilot has no integration with ('Property Data API')

**property-appraisal-review:547** (1 rules)
- Condition: Property data collector not trained with competent knowledge or vetted by an annual background check
- Rationale: Matched project-documentation vocabulary ('value acceptance') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Property data collector not trained with competent knowledge or vetted by an annual background check'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:548** (1 rules)
- Condition: Rep & warrant property conditions not met for property data collection needing repairs/completion
- Rationale: Matched project-documentation vocabulary ('value acceptance') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Rep & warrant property conditions not met for property data collection needing repairs/completion'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:549** (1 rules)
- Condition: SFC 774 was not included at delivery where value acceptance + property data was exercised
- Rationale: Matched project-documentation vocabulary ('value acceptance') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'SFC 774 was not included at delivery where value acceptance + property data was exercised'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:550** (1 rules)
- Condition: The loan had a characteristic that was not eligible for value acceptance + property data
- Rationale: Matched project-documentation vocabulary ('value acceptance') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The loan had a characteristic that was not eligible for value acceptance + property data'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:551** (1 rules)
- Condition: The property data collection did not meet FNMA's Property Data Standard minimum requirements
- Rationale: Matched project-documentation vocabulary ('value acceptance') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: "The property data collection did not meet FNMA's Property Data Standard minimum requirements"
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:552** (1 rules)
- Condition: The value acceptance + property data offer is over 4 months old on the Note date
- Rationale: Matched project-documentation vocabulary ('value acceptance') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The value acceptance + property data offer is over 4 months old on the Note date'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:555** (1 rules)
- Condition: The appraisal report was not submitted to the UCDP or did not receive a “successful” status
- Rationale: Bucket-C-style candidate (decision 016 precedent): references 'UCDP', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- What's needed: live lookup against an external system/database this pilot has no integration with ('UCDP')

**property-appraisal-review:557** (1 rules)
- Condition: Co-op comps outside the subject project not from projects with similar common elements/recreation
- Rationale: Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Co-op comps outside the subject project not from projects with similar common elements/recreation'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:559** (1 rules)
- Condition: Cooperative interest not reported on the appraisal and/or FNMA Form 1074 not attached as an addendum
- Rationale: Crisp presence check once 'Form 1074' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Cooperative interest not reported on the appraisal and/or FNMA Form 1074 not attached as an addendum'
- What's needed: 'Form 1074' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:561** (1 rules)
- Condition: The interior and exterior appraisal of the cooperative unit was not reported on Fannie Mae Form 2090
- Rationale: Crisp presence check once 'Form 2090' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'The interior and exterior appraisal of the\xa0cooperative unit\xa0was not reported on\xa0Fannie Mae Form 2090'
- What's needed: 'Form 2090' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:563** (1 rules)
- Condition: Applicable occupancy requirements for an established condo project were not met
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Applicable occupancy requirements for an established condo project were not met'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:564** (1 rules)
- Condition: CPA Feedback Cert or last Feedback Cert, whichever contains the last PAR findings is not in the file
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'CPA Feedback Cert or last Feedback Cert, whichever contains the last PAR findings is not in the file'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:565** (1 rules)
- Condition: Eligibility requirements were not met for an established manufactured home condo project review
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Eligibility requirements were not met for an established manufactured home condo project review'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:567** (1 rules)
- Condition: Note date not w/in 120 days of CPA Feedback Cert/last Feedback Cert whichever has last PAR findings
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Note date not w/in 120 days of CPA Feedback Cert/last Feedback Cert whichever has last PAR findings'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:568** (1 rules)
- Condition: Project review/eligibility req's not met where Condo Project Advisor has yellow or incomplete status
- Rationale: Bucket-C-style candidate (decision 016 precedent): references 'Condo Project Advisor', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- What's needed: live lookup against an external system/database this pilot has no integration with ('Condo Project Advisor')

**property-appraisal-review:569** (1 rules)
- Condition: The condo Project Assessment Request (PAR) received a Not Eligible status without evidence of appeal
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The condo Project Assessment Request (PAR) received a Not Eligible status without evidence of appeal'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:570** (1 rules)
- Condition: The condo project budget requirements were not met and/or it was not for the current fiscal year
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The condo project budget requirements were not met and/or it was not for the current fiscal year'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:571** (1 rules)
- Condition: The full review questionnaire was not dated within 180 days of the PCS request date
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The full review questionnaire was not dated within 180 days of the PCS request date'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:572** (1 rules)
- Condition: Condo or PUD-not ensured that mandatory HOA assessment is subordinate to the VA-guaranteed mtg
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Condo or PUD-not ensured that mandatory HOA assessment is subordinate to the VA-guaranteed mtg'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:573** (1 rules)
- Condition: Condominium project not VA approved
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Condominium project not VA approved'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:574** (1 rules)
- Condition: Litigation without meeting the eligible minor litigation criteria
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Litigation without meeting the eligible minor litigation criteria'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:578** (1 rules)
- Condition: Unable to locate the project approval certificate
- Rationale: Crisp presence check once 'project approval certificate' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Unable to locate the project approval certificate'
- What's needed: 'project approval certificate' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:579** (1 rules)
- Condition: 2-4 unit condo review waived, not all cond met
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: '2-4 unit condo review waived, not all cond met'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:580** (1 rules)
- Condition: Condo HOA litigation amt to exceed 10% of project funded reserves or is unallowable by laws and regs
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Condo HOA litigation amt to exceed 10% of project funded reserves or is unallowable by laws and regs'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:581** (1 rules)
- Condition: Condo Project Advisor used to obtain a PWR without all project eligibility requirements being met
- Rationale: Bucket-C-style candidate (decision 016 precedent): references 'Condo Project Advisor', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- What's needed: live lookup against an external system/database this pilot has no integration with ('Condo Project Advisor')

**property-appraisal-review:582** (1 rules)
- Condition: Condo project litigation impacts safety, structural or function of subject
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Condo project litigation impacts safety, structural or function of subject'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:583** (1 rules)
- Condition: File did not document project meets FNMA’s full review req's where CPM status is Certified by Lender
- Rationale: Bucket-C-style candidate (decision 016 precedent): references 'CPM', an external system this pilot cannot query from a static loan document. Flagged, not unilaterally discarded from the compiled ruleset — a human should decide, same as the RE-license and NMLS precedents.
- What's needed: live lookup against an external system/database this pilot has no integration with ('CPM')

**property-appraisal-review:585** (1 rules)
- Condition: Project Questionnaire not found (when required)
- Rationale: Crisp presence check once 'Project Questionnaire' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Project Questionnaire not found (when required)'
- What's needed: 'Project Questionnaire' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:586** (1 rules)
- Condition: Required condo project review not conducted or was incomplete
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Required condo project review not conducted or was incomplete'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:587** (1 rules)
- Condition: Subject 2-4 unit condominium project had over 4 units and/or more than 1 commercial unit
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Subject 2-4 unit condominium project had over 4 units and/or more than 1 commercial unit'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:589** (1 rules)
- Condition: The condominium project commercial or non-residential space was not calculated correctly
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The condominium project commercial or non-residential space was not calculated correctly'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:590** (1 rules)
- Condition: The project has over 35% commercial or non-residential space which is ineligible
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The project has over 35% commercial or non-residential space which is ineligible'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:591** (1 rules)
- Condition: Total number of condo units owned by same person/entity exceeds limits
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Total number of condo units owned by same person/entity exceeds limits'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:592** (1 rules)
- Condition: Unable to locate the projects HOA meeting minutes
- Rationale: Matched project-documentation vocabulary ('condo') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Unable to locate the projects HOA meeting minutes'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:594** (1 rules)
- Condition: Project review waiver exercised where project is terminating or involved in insolvency proceedings
- Rationale: Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Project review waiver exercised where project is terminating or involved in insolvency proceedings'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:595** (1 rules)
- Condition: The cooperative project does not meet eligibility requirements
- Rationale: Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The cooperative project does not meet eligibility requirements'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:596** (1 rules)
- Condition: The cooperative project review as applicable per project type is not in the file
- Rationale: Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The cooperative project review as applicable per project type is not in the file'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:597** (1 rules)
- Condition: The subject is a cooperative hotel or similar type of transient housing
- Rationale: Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The subject is a cooperative hotel or similar type of transient housing'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:600** (1 rules)
- Condition: Security Instrument legal desc leasehold did not refer to recorded lease
- Rationale: Matched project-documentation vocabulary ('leasehold') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Security Instrument legal desc leasehold did not refer to recorded lease'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:602** (1 rules)
- Condition: Co-op has been 30+ days delinq in last yr blanket mtg pymts, taxes, insurance &/or other obligations
- Rationale: Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Co-op has been 30+ days delinq in last yr blanket mtg pymts, taxes, insurance &/or other obligations'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:604** (1 rules)
- Condition: Over 15% of co-op shareholders are over 60 days delinq in maintenance fees/assessments
- Rationale: Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Over 15% of co-op shareholders are over 60 days delinq in maintenance fees/assessments'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:605** (1 rules)
- Condition: Subject of action causing project to not exist/termination/deconversion/legal structure dissolution
- Rationale: Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Subject of action causing project to not exist/termination/deconversion/legal structure dissolution'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:606** (1 rules)
- Condition: Subject of voluntary-invol bankruptcy/insolvency/liquidation/receivership proceeding or similar
- Rationale: Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Subject of voluntary-invol bankruptcy/insolvency/liquidation/receivership proceeding or similar'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:607** (1 rules)
- Condition: The co-op units & common areas are incomplete &/or are subject to addt'l phasing or annexation
- Rationale: Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: "The co-op units & common areas are incomplete &/or are subject to addt'l phasing or annexation"
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:608** (1 rules)
- Condition: The cooperative project does not consist of two or more 1-unit dwellings
- Rationale: Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The cooperative project does not consist of two or more 1-unit dwellings'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:609** (1 rules)
- Condition: The cooperative project's budget did not meet requirements
- Rationale: Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: "The cooperative project's budget did not meet requirements"
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:610** (1 rules)
- Condition: The maximum single-investor concentration limit for the cooperative projects was exceeded
- Rationale: Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The maximum single-investor concentration limit for\xa0the cooperative projects was exceeded'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:612** (1 rules)
- Condition: Co-op share loan did not meet IRS section 216 req's for co-op housing in effect as of delivery date
- Rationale: Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: "Co-op share loan did not meet IRS section 216 req's for co-op housing in effect as of delivery date"
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:614** (1 rules)
- Condition: The cooperative share loan did not comply with all eligibility requirements
- Rationale: Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'The cooperative share loan did not comply with all eligibility requirements'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:615** (1 rules)
- Condition: The pro rata cooperative share of the cooperative corporation's debt was not calculated correctly
- Rationale: Matched project-documentation vocabulary ('co-op') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: "The pro rata cooperative share of the cooperative corporation's debt was not calculated correctly"
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:641** (1 rules)
- Condition: Address,owner,county,legal, parcel ID,neighborhood &\or occupant et al is missing/incomplete
- Rationale: Matched project-documentation vocabulary ('parcel') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Address,owner,county,legal, parcel ID,neighborhood &\\or occupant et al is missing/incomplete'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:671** (1 rules)
- Condition: Appraisal subject to repairs is missing the appraiser's itemized list of repairs/other action needed
- Rationale: Crisp presence check once this specific exhibit is captured; reclassified from the conservative-default RED.
- What's needed: repair-itemization exhibit (not modeled)

**property-appraisal-review:673** (1 rules)
- Condition: Form 400, Warranty of Completion of Construction, used but not signed/dated by borr & builder's rep
- Rationale: Crisp presence check once 'Form 400' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: "Form 400, Warranty of Completion of Construction, used but not signed/dated by borr & builder's rep"
- What's needed: 'Form 400' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:676** (1 rules)
- Condition: The file did not contain Form 442 where the appraisal was made subject to repairs or alterations
- Rationale: Same program-mismatch rejection as G040.
- What's needed: as G040 — Freddie Form 442, not FHA MPR completion cert

**property-appraisal-review:677** (1 rules)
- Condition: The file did not contain Form 442, Form 400, or other similar form in a new or proposed construction
- Rationale: Same program-mismatch rejection as G040.
- What's needed: as G040 — Freddie Form 442/400, not FHA MPR completion cert

**property-appraisal-review:678** (1 rules)
- Condition: Appraiser did not use additional due diligence or Form 820.05 for lack of energy efficient comps
- Rationale: Crisp presence check once 'Form 820' exists as its own document type; a real fixture gap, not a rule-clarity problem — condition: 'Appraiser did not use additional due diligence or Form 820.05 for lack of energy efficient comps'
- What's needed: 'Form 820' as a distinct document type — not in any of the 5 synthetic loans (each has one 'Appraisal Summary' PDF only, no separate project/form documentation)

**property-appraisal-review:689** (1 rules)
- Condition: Each of the multiple parcels not conveyed in entirety with the being the first lien on each
- Rationale: Matched project-documentation vocabulary ('parcel') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Each of the multiple parcels not conveyed in entirety with the being the first lien on each'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:690** (1 rules)
- Condition: No documentation non-adjoining parcels without the residence cannot be improved with a dwelling
- Rationale: Matched project-documentation vocabulary ('parcel') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'No documentation non-adjoining parcels without the residence cannot be improved with a dwelling'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:691** (1 rules)
- Condition: Non-adjoining parcels are not separated due to a road, waterfront access or similar as allowable
- Rationale: Matched project-documentation vocabulary ('parcel') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Non-adjoining parcels are not separated due to a road, waterfront access or similar as allowable'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:693** (1 rules)
- Condition: Subject w/ more than 1 adjoining parcel file did not confirm parcels had no additional residence
- Rationale: Matched project-documentation vocabulary ('parcel') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: 'Subject w/ more than 1 adjoining parcel file did not confirm parcels had no additional residence'
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

**property-appraisal-review:694** (1 rules)
- Condition: The subject's additional parcels were not adjoining and/or did not have the same basic zoning
- Rationale: Matched project-documentation vocabulary ('parcel') — the single biggest fixture gap in this block: no condo/co-op/PUD project-review document of any kind exists in any of the 5 synthetic loans (each loan has exactly one appraisal summary PDF, no project-level HOA/questionnaire/litigation documentation); condition: "The subject's additional parcels were not adjoining and/or did not have the same basic zoning"
- What's needed: condo/co-op/PUD/leasehold/ADU project-level documentation (HOA financials, project questionnaires, litigation/budget/reserve disclosures) — an entirely separate document family, absent from all 5 synthetic loans

## Honest Assessment: What 'Automatable' Really Means

The conversion rate looks high on paper, but there are important caveats:

1. **Fixture-blocked rules (decision 014)** are legitimately automatable — the 16 exception codes identified are for documents this project just hasn't synthesized yet (VA Counseling Checklist, HUD-92564-CN, Form 1103, etc.). Once those doc types are added to the synthetic loan generator, the rules work deterministically.

2. **Extraction-blocked rules** assume the extraction infrastructure can be extended. Some fields (like 'timely' timing calculations) require both the document and its metadata (provided-date vs required-date). If Touchless doesn't return those dates, the 'automatable' label is misleading.

3. **'Completeness' and 'accuracy' gates** (e.g., 'fully completed, correct') are hybrid — presence/signature is automatable, but correctness often requires cross-field consistency checks that may not exist yet. These were classified as GREEN if the presence check exists, but the human reviewer still assesses 'correct.'

4. **SME-clarification rules** are genuinely blocked. 'Adequate,' 'reasonable,' 'appears to need more space' — these require either explicit thresholds from an SME or permanent routing to human judgment.

**Bottom line:** 1323/2125 (62.3%) are convertible with known, scoped work (fixture expansion + extraction deepening). The remaining 802 (37.7%) need either SME decomposition or permanent human routing.