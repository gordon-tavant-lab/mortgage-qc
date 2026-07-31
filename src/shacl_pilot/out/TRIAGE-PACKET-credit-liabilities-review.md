# SME Review Packet — credit-liabilities-review block triage

**386 rules / 382 unique (question, condition) groups.** Every classification
below is a *proposal* pending your review — mark each check agree / correct.
Bins: GREEN = automatable now · YELLOW = automatable after data/guide work ·
RED = stays human · NOT_A_CHECK = pass/N-A answer option, not a defect rule.

**Source workbook:** `PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv` — row numbers below are Excel-style
(header = row 1), so you can open the sheet and jump straight to each rule.

**Note on this block vs the other two:** dedup collapse is even smaller here (386 rules -> 382 groups, ~1.01x) than asset-verification's 304->297 (~1.02x) or application-verification's 81->54 (~1.5x). Two shapes are already mapped to this block (`UndisclosedLiabilityShape`, `CashoutMortgageLateShape`) but BOTH are wired to zero AMQ exception codes — this triage went looking for a real row each could safely extend (the decision-018 discipline) and found none that survives verification; see decision 019 for the full writeup of what was checked and rejected, and why.

## Headline

| Bin | Groups | Rules | % of defect groups |
|---|---|---|---|
| GREEN | 10 | 10 | 3% |
| YELLOW | 277 | 277 | 92% |
| RED | 15 | 15 | 5% |
| NOT_A_CHECK | 80 | 84 | — |

## GREEN

### G001 — O-FHA-02220 [O-FHA]
- **Q:** (FHA) Was a credit report in the loan file for each applicant responsible for loan repayment?
- **Defect condition:** A credit report is missing for at least one applicant
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 957
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: credit_report
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier (the exception text matches 'not in file/missing/not provided' and names a mappable document type already in the extraction contract) -- already works. Verified against the full exception_description text (decision-018 discipline): this IS a genuine 'credit report present for this applicant' presence fact, unlike 19 of its 24 doc_presence siblings in this block -- see decision 019's false-GREEN finding.
- **SME:** [ ] agree [ ] correct: ______

### G003 — O-FHA-58069 [O-FHA]
- **Q:** (FHA) Was a credit report in the loan file for each applicant responsible for loan repayment?
- **Defect condition:** There are no credit report(s) in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 963
- **Severity:** Critical
- **Machine checks:** credit_report doc presence via docs_present inventory
- **Rationale:** Trivially checkable (docs_present.get('credit_report')) -- functionally identical to amq_compiler.py's own doc_presence auto-compile, but this exact phrasing ('There are no credit report(s) in the file') isn't caught by its NOT_IN_FILE_RE regex (requires literal 'not in file'/'not provided'/'missing'). Flagged as a regex-coverage gap in amq_compiler.py for a human to patch -- not itself a triage-judgment problem, and not patched here (amq_compiler.py is off-limits for this exercise).
- **SME:** [ ] agree [ ] correct: ______

### G005 — O-FNM-00179 [O-FNM]
- **Q:** (Fannie Mae) Was a credit report in the loan file for each applicant responsible for loan repayment?
- **Defect condition:** No, a credit report is missing for at least one applicant(s)
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 958
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: credit_report
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier (the exception text matches 'not in file/missing/not provided' and names a mappable document type already in the extraction contract) -- already works. Verified against the full exception_description text (decision-018 discipline): this IS a genuine 'credit report present for this applicant' presence fact, unlike 19 of its 24 doc_presence siblings in this block -- see decision 019's false-GREEN finding.
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** D2-1-02 — Fannie Mae QC File Request and Submission Requirements (PDF p.1078)
- **Guide candidate:** A2-5-01 — Fannie Mae Trade Name and Trademarks (PDF p.102)
- **SME:** [ ] agree [ ] correct: ______

### G006 — O-FNM-58076 [O-FNM]
- **Q:** (Fannie Mae) Was a credit report in the loan file for each applicant responsible for loan repayment?
- **Defect condition:** No, there are no credit report(s) in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 964
- **Severity:** Critical
- **Machine checks:** credit_report doc presence via docs_present inventory
- **Rationale:** Trivially checkable (docs_present.get('credit_report')) -- functionally identical to amq_compiler.py's own doc_presence auto-compile, but this exact phrasing ('There are no credit report(s) in the file') isn't caught by its NOT_IN_FILE_RE regex (requires literal 'not in file'/'not provided'/'missing'). Flagged as a regex-coverage gap in amq_compiler.py for a human to patch -- not itself a triage-judgment problem, and not patched here (amq_compiler.py is off-limits for this exercise).
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **Guide candidate:** D2-1-02 — Fannie Mae QC File Request and Submission Requirements (PDF p.1078)
- **Guide candidate:** A2-5-01 — Fannie Mae Trade Name and Trademarks (PDF p.102)
- **SME:** [ ] agree [ ] correct: ______

### G008 — O-FRD-00144 [O-FRD]
- **Q:** (Freddie Mac) Was a credit report in the loan file for each applicant responsible for loan repayment?
- **Defect condition:** A credit report is missing for at least one applicant(s)
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 959, 960
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: credit_report
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier (the exception text matches 'not in file/missing/not provided' and names a mappable document type already in the extraction contract) -- already works. Verified against the full exception_description text (decision-018 discipline): this IS a genuine 'credit report present for this applicant' presence fact, unlike 19 of its 24 doc_presence siblings in this block -- see decision 019's false-GREEN finding.
- **SME:** [ ] agree [ ] correct: ______

### G009 — O-FRD-58199 [O-FRD]
- **Q:** (Freddie Mac) Was a credit report in the loan file for each applicant responsible for loan repayment?
- **Defect condition:** There are no credit report(s) in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 965
- **Severity:** Major
- **Machine checks:** credit_report doc presence via docs_present inventory
- **Rationale:** Trivially checkable (docs_present.get('credit_report')) -- functionally identical to amq_compiler.py's own doc_presence auto-compile, but this exact phrasing ('There are no credit report(s) in the file') isn't caught by its NOT_IN_FILE_RE regex (requires literal 'not in file'/'not provided'/'missing'). Flagged as a regex-coverage gap in amq_compiler.py for a human to patch -- not itself a triage-judgment problem, and not patched here (amq_compiler.py is off-limits for this exercise).
- **SME:** [ ] agree [ ] correct: ______

### G011 — O-RHS-02788 [O-RHS]
- **Q:** (RHS) Was a credit report in the loan file for each applicant responsible for loan repayment?
- **Defect condition:** No, a credit report is missing for at least one applicant(s)
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 961
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: credit_report
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier (the exception text matches 'not in file/missing/not provided' and names a mappable document type already in the extraction contract) -- already works. Verified against the full exception_description text (decision-018 discipline): this IS a genuine 'credit report present for this applicant' presence fact, unlike 19 of its 24 doc_presence siblings in this block -- see decision 019's false-GREEN finding.
- **SME:** [ ] agree [ ] correct: ______

### G012 — O-RHS-58227 [O-RHS]
- **Q:** (RHS) Was a credit report in the loan file for each applicant responsible for loan repayment?
- **Defect condition:** There are no credit report(s) in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 966
- **Severity:** Critical
- **Machine checks:** credit_report doc presence via docs_present inventory
- **Rationale:** Trivially checkable (docs_present.get('credit_report')) -- functionally identical to amq_compiler.py's own doc_presence auto-compile, but this exact phrasing ('There are no credit report(s) in the file') isn't caught by its NOT_IN_FILE_RE regex (requires literal 'not in file'/'not provided'/'missing'). Flagged as a regex-coverage gap in amq_compiler.py for a human to patch -- not itself a triage-judgment problem, and not patched here (amq_compiler.py is off-limits for this exercise).
- **SME:** [ ] agree [ ] correct: ______

### G014 — O-VA-00118 [O-VA]
- **Q:** (VA) Was a credit report in the loan file for each applicant responsible for loan repayment?
- **Defect condition:** No, a credit report is missing for at least one applicant(s)
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 962
- **Severity:** Critical
- **Machine checks:** auto-compiled doc-presence check on: credit_report
- **Rationale:** Auto-compiled by amq_compiler.py's doc_presence classifier (the exception text matches 'not in file/missing/not provided' and names a mappable document type already in the extraction contract) -- already works. Verified against the full exception_description text (decision-018 discipline): this IS a genuine 'credit report present for this applicant' presence fact, unlike 19 of its 24 doc_presence siblings in this block -- see decision 019's false-GREEN finding.
- **SME:** [ ] agree [ ] correct: ______

### G016 — O-VA-58294 [O-VA]
- **Q:** (VA) Was a credit report in the loan file for each applicant responsible for loan repayment?
- **Defect condition:** There are no credit report(s) in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 967
- **Severity:** Critical
- **Machine checks:** credit_report doc presence via docs_present inventory
- **Rationale:** Trivially checkable (docs_present.get('credit_report')) -- functionally identical to amq_compiler.py's own doc_presence auto-compile, but this exact phrasing ('There are no credit report(s) in the file') isn't caught by its NOT_IN_FILE_RE regex (requires literal 'not in file'/'not provided'/'missing'). Flagged as a regex-coverage gap in amq_compiler.py for a human to patch -- not itself a triage-judgment problem, and not patched here (amq_compiler.py is off-limits for this exercise).
- **SME:** [ ] agree [ ] correct: ______

## YELLOW

### G017 — O-FHA-02241 [O-FHA]
- **Q:** Were all AUS specific 30-day accounts requirements met?
- **Defect condition:** Documentation that outstanding balance is paid in full for the past 12 months on a 30-day account
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 757
- **Severity:** Critical
- **Rationale:** Needs 12 months of month-by-month payment history for a specific tradeline -- `extract_tradelines()` captures only a single current-status snapshot per tradeline (creditor/type/balance/monthly_payment/status), not a payment-history timeline; only the VOM (loan 04, one specific mortgage) has that depth in this corpus.
- **SME:** [ ] agree [ ] correct: ______

### G019 — O-FHA-51478 [O-FHA]
- **Q:** Were all AUS specific general liabilities and debt requirements met?
- **Defect condition:** Credit inquiries including new debts from material inquiries are not in the debt ratio
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 775
- **Severity:** Critical
- **Rationale:** Needs a parsed Inquiries table (already visible in the loan 01 credit report's text -- 'Inquiries (last 120 days)' with Date/Bureau/Requesting Party -- but not yet in FIELD_SPECS/entities) cross-referenced against whether new debt was opened; Bucket-B-style (deepen extraction of a section already present in the one document we have), not a missing document.
- **SME:** [ ] agree [ ] correct: ______

### G021 — O-FHA-02242 [O-FHA]
- **Q:** Were all AUS specific other liabilities requirements met?
- **Defect condition:** Business debt(s) not included in DTI or documentation debt(s) is paid by the business is missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 786
- **Severity:** Critical
- **Rationale:** Same business-debt-in-DTI family as O-FNM-50006 (FHA wording variant, adds a self-employment/cash-flow-analysis angle) -- MISCLASSIFIED by the same mechanical doc_presence false-positive.
- **SME:** [ ] agree [ ] correct: ______

### G023 — O-FHA-50009 [O-FHA]
- **Q:** Were all AUS specific revolving charge account requirements met?
- **Defect condition:** Account with 30 day late payment in 12 months evident; 5% of the balance not included in DTI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 758, 759
- **Severity:** Critical
- **Rationale:** The percentage-of-balance math (5%/1.5%/0.5% thresholds) is crisp arithmetic once the relevant balance is in hand, and `extract_tradelines()` already captures type/balance/monthly_payment per tradeline -- but confirming whether the LENDER actually included the computed amount in the final DTI needs a DTI worksheet this pilot doesn't derive (same gap as F_PITIA_DTI_REO); and month-by-month late-payment-in-12-months detection needs payment-history depth the tradeline snapshot (a single current 'Status' value) doesn't carry. Trigger data partly in hand; verification math not yet built.
- **SME:** [ ] agree [ ] correct: ______

### G025 — O-FHA-54668 [O-FHA]
- **Q:** Were all AUS specific student loan liabilities requirements met?
- **Defect condition:** Credit report payment or actual documented payment not used to calculate an outstanding student loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 764
- **Severity:** Critical
- **Rationale:** Student-loan payment-substitution math (0.5%/1% of balance when the credit report shows a $0 or missing payment) is crisp arithmetic, and `extract_tradelines()` already captures tradeline type/balance/monthly_payment (loan 01 has one Student tradeline) -- but verifying which qualifying-payment value the lender ACTUALLY used needs a DTI/qualifying-payment worksheet this pilot doesn't extract or derive from any document today. Trigger-detection is Bucket-B-close; the verification half is not.
- **SME:** [ ] agree [ ] correct: ______

### G027 — O-VA-00137 [O-VA]
- **Q:** Were all Automated Underwriting Cases (AUS) requirements met?
- **Defect condition:** Mortgage debt reported 30+ days late/12 months; AUS not downgraded to Refer
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 776
- **Severity:** Critical
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **SME:** [ ] agree [ ] correct: ______

### G028 — O-VA-00129 [O-VA]
- **Q:** Were all Automated Underwriting Cases (AUS) requirements met?
- **Defect condition:** Significant debt reported 90+ late is not updated within 90 days of the AUS report
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 778
- **Severity:** Critical
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **SME:** [ ] agree [ ] correct: ______

### G029 — O-VA-00130 [O-VA]
- **Q:** Were all Automated Underwriting Cases (AUS) requirements met?
- **Defect condition:** Significant debt reported 90+ late/not updated within 90 days of report; AUS not downgraded to Refer
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 777
- **Severity:** Critical
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **SME:** [ ] agree [ ] correct: ______

### G030 — O-VA-00132 [O-VA]
- **Q:** Were all Automated Underwriting Cases (AUS) requirements met?
- **Defect condition:** Undisclosed debt verification reflects 30-day late payment(s)/12 months; AUS not downgraded to Refer
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 779
- **Severity:** Critical
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **SME:** [ ] agree [ ] correct: ______

### G032 — O-FHA-01785 [O-FHA]
- **Q:** Were all Disputed Derogatory Credit Account requirements met?
- **Defect condition:** Disputed derogatory credit accounts exceed $1k but the loan was not downgraded to Refer
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 852
- **Severity:** Critical
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **SME:** [ ] agree [ ] correct: ______

### G033 — O-FHA-54821 [O-FHA]
- **Q:** Were all Disputed Derogatory Credit Account requirements met?
- **Defect condition:** Medical, ID/credit card theft, &/or unauth use disputed accts included in cumulative balance calc
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 851
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G035 — O-FHA-54822 [O-FHA]
- **Q:** Were all Disputed Derogatory Credit Account requirements met?
- **Defect condition:** The police report/creditor supporting docs not in the file to support excluded disputed derog credit
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 865
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G037 — O-FRD-51738 [O-FRD]
- **Q:** Were all Employee Relocation Program requirements met?
- **Defect condition:** Payments or debts associated with an EAH Benefit were excluded from ratios without all req's met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 859
- **Severity:** Critical
- **Rationale:** Employer Assisted Homeownership (EAH) benefit agreement -- same document family asset-verification's triage already flagged as absent from this corpus (G020/G022).
- **SME:** [ ] agree [ ] correct: ______

### G042 — O-FRD-56574 [O-FRD]
- **Q:** Were all Internal Revenue Service (IRS) installment agreement requirements met?
- **Defect condition:** IRS installment agreement verifying the payment terms, monthly payment & balance was not in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 895
- **Severity:** Critical
- **Rationale:** IRS installment-agreement document (payment terms/balance/lien notice) -- not a doc type in this corpus.
- **SME:** [ ] agree [ ] correct: ______

### G043 — O-FRD-56576 [O-FRD]
- **Q:** Were all Internal Revenue Service (IRS) installment agreement requirements met?
- **Defect condition:** Indications the IRS filed a Notice of Federal Tax Lien for taxes owed under the installment agrmt
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 898
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G045 — O-FRD-57132 [O-FRD]
- **Q:** Were all Internal Revenue Service (IRS) installment agreement requirements met?
- **Defect condition:** Pending IRS installment agrmt & greater of the monthly pymt or taxes owed divided by 72 not in DTI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 994
- **Severity:** Critical
- **Rationale:** IRS installment-agreement document (payment terms/balance/lien notice) -- not a doc type in this corpus.
- **SME:** [ ] agree [ ] correct: ______

### G046 — O-FRD-57131 [O-FRD]
- **Q:** Were all Internal Revenue Service (IRS) installment agreement requirements met?
- **Defect condition:** Pending IRS installment agrmt & the application w/ taxes owed & requested pymt terms not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 993
- **Severity:** Critical
- **Rationale:** IRS installment-agreement document (payment terms/balance/lien notice) -- not a doc type in this corpus.
- **SME:** [ ] agree [ ] correct: ______

### G047 — O-FRD-56573 [O-FRD]
- **Q:** Were all Internal Revenue Service (IRS) installment agreement requirements met?
- **Defect condition:** The IRS installment agreement has over 10 mos of payments remaining & was not included in the DTI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 896
- **Severity:** Critical
- **Rationale:** IRS installment-agreement document (payment terms/balance/lien notice) -- not a doc type in this corpus.
- **SME:** [ ] agree [ ] correct: ______

### G048 — O-FRD-56575 [O-FRD]
- **Q:** Were all Internal Revenue Service (IRS) installment agreement requirements met?
- **Defect condition:** The file did not verify the borrower is not past due per the terms of the IRS installment agreement
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 897
- **Severity:** Critical
- **Rationale:** IRS installment-agreement document (payment terms/balance/lien notice) -- not a doc type in this corpus.
- **SME:** [ ] agree [ ] correct: ______

### G049 — O-FRD-00162 [O-FRD]
- **Q:** Were all Loan Product Advisor® credit assessment requirements met?
- **Defect condition:** All LP requirements were not met in order to assess the transaction with no usable credit scores
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 972
- **Severity:** Critical
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **SME:** [ ] agree [ ] correct: ______

### G050 — O-FRD-58858 [O-FRD]
- **Q:** Were all Loan Product Advisor® credit assessment requirements met?
- **Defect condition:** Auth user of a tradeline in LPA Accept w/ feedback message requiring adtl documentation not obtained
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 917
- **Severity:** Critical
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **SME:** [ ] agree [ ] correct: ______

### G051 — O-FRD-56006 [O-FRD]
- **Q:** Were all Loan Product Advisor® credit assessment requirements met?
- **Defect condition:** Final verification report not in file where positive cash flow resulted in a risk class of Accept
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 969
- **Severity:** Critical
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **SME:** [ ] agree [ ] correct: ______

### G052 — O-FRD-56005 [O-FRD]
- **Q:** Were all Loan Product Advisor® credit assessment requirements met?
- **Defect condition:** Monthly cash flow was considered without at least 12 months of account data transmitted to LPA
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 968
- **Severity:** Critical
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **SME:** [ ] agree [ ] correct: ______

### G053 — O-FRD-56009 [O-FRD]
- **Q:** Were all Loan Product Advisor® credit assessment requirements met?
- **Defect condition:** No usable credit score & collections (not medical), judgments or tax liens present in last 24 mos
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 849
- **Severity:** Major
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **SME:** [ ] agree [ ] correct: ______

### G055 — O-FRD-54819 [O-FRD]
- **Q:** Were all Loan Product Advisor® credit assessment requirements met?
- **Defect condition:** The 1008/1077 or similar document was incomplete, incorrect or not in the LPA underwritten file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 918
- **Severity:** Major
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **SME:** [ ] agree [ ] correct: ______

### G056 — O-VA-00124 [O-VA]
- **Q:** Were all Residential Mortgage Credit Reports (RMCR) requirements met?
- **Defect condition:** A 24 month residency history was not provided on the credit report
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1019
- **Severity:** Major
- **Rationale:** MISCLASSIFIED (matched 'was not provided' + 'credit report' keyword) -- needs an RMCR-specific 24-month residency-history field, same F_RMCR_FORMAT family elsewhere in this block, not a bare presence check.
- **SME:** [ ] agree [ ] correct: ______

### G057 — O-VA-00122 [O-VA]
- **Q:** Were all Residential Mortgage Credit Reports (RMCR) requirements met?
- **Defect condition:** No, the RMCR in the file does not indicate that it includes all available public record information
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1020
- **Severity:** Critical
- **Rationale:** Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- **SME:** [ ] agree [ ] correct: ______

### G058 — O-VA-00126 [O-VA]
- **Q:** Were all Residential Mortgage Credit Reports (RMCR) requirements met?
- **Defect condition:** RMCR does not reflect 2 credit repositories for each applicant/area of residency/prior 2 years
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1021
- **Severity:** Critical
- **Rationale:** Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- **SME:** [ ] agree [ ] correct: ______

### G059 — O-VA-00123 [O-VA]
- **Q:** Were all Residential Mortgage Credit Reports (RMCR) requirements met?
- **Defect condition:** The RMCR in the file does not include the required credit information for each debt shown
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1022
- **Severity:** Critical
- **Rationale:** Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- **SME:** [ ] agree [ ] correct: ______

### G060 — O-VA-00121 [O-VA]
- **Q:** Were all Residential Mortgage Credit Reports (RMCR) requirements met?
- **Defect condition:** The RMCR in the file is not  in the proper format and appears altered
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1045
- **Severity:** Critical
- **Rationale:** Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- **SME:** [ ] agree [ ] correct: ______

### G062 — O-RHS-51059 [O-RHS]
- **Q:** Were all additional adverse or derogatory credit requirements met?
- **Defect condition:** Borr has unpaid tax lien w/out a valid repayment agreement with at least 3 regular payments made
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1052
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G063 — O-RHS-50561 [O-RHS]
- **Q:** Were all additional adverse or derogatory credit requirements met?
- **Defect condition:** Collections unpaid without documenting mitigating circumstances
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1050
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G065 — O-RHS-56097 [O-RHS]
- **Q:** Were all additional adverse or derogatory credit requirements met?
- **Defect condition:** Delinquent court ordered child support with admin offset was not brought current, PIF, or released
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 844
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G066 — O-RHS-50562 [O-RHS]
- **Q:** Were all additional adverse or derogatory credit requirements met?
- **Defect condition:** Disputed act w/ outstanding balance excluded from DTI & a justifiable dispute was not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 886
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G067 — O-RHS-02835 [O-RHS]
- **Q:** Were all additional adverse or derogatory credit requirements met?
- **Defect condition:** Loan approved without credit exception documentation for a short sale action within prior 3 years
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1002
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G070 — O-RHS-02832 [O-RHS]
- **Q:** Were all additional adverse or derogatory credit requirements met?
- **Defect condition:** Previous USDA loss w/in 7 yrs prior to the date of submission without an agency approved exception
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1003
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G071 — O-VA-50021 [O-VA]
- **Q:** Were all additional credit history requirements met?
- **Defect condition:** Approval does not evidence exception for foreclosure/deed-in-lieu reported within 2 years
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1027
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G073 — O-VA-50770 [O-VA]
- **Q:** Were all additional credit history requirements met?
- **Defect condition:** Open judgement not paid in full or in a repayment plan with a history of timely payments
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 899
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G075 — O-VA-50017 [O-VA]
- **Q:** Were all additional credit history requirements met?
- **Defect condition:** Satisfactory payment history/counseling agency approval missing for credit counseling participants
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 807
- **Severity:** Critical
- **Rationale:** Consumer credit counseling program enrollment/payout/agency-approval document -- not a doc type in this corpus.
- **SME:** [ ] agree [ ] correct: ______

### G077 — O-FRD-00154 [O-FRD]
- **Q:** Were all additional credit report requirements met?
- **Defect condition:** Accounts w/ a balance not updated with the creditor within 90 days of the date of the credit report
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 817
- **Severity:** Major
- **Rationale:** Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- **SME:** [ ] agree [ ] correct: ______

### G078 — O-FRD-00147 [O-FRD]
- **Q:** Were all additional credit report requirements met?
- **Defect condition:** No, the RMCR does not indicate that it includes all available public record information
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1007
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G079 — O-FRD-00150 [O-FRD]
- **Q:** Were all additional credit report requirements met?
- **Defect condition:** RMCR does not reflect 2 credit repositories for each applicant/area of residency/prior 2 years
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 834
- **Severity:** Critical
- **Rationale:** Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- **SME:** [ ] agree [ ] correct: ______

### G080 — O-FRD-00155 [O-FRD]
- **Q:** Were all additional credit report requirements met?
- **Defect condition:** Responsive statements concerning items on the report including trade and credit history are missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 835
- **Severity:** Critical
- **Rationale:** MISCLASSIFIED (matched 'not reflected' + 'credit report' keyword) -- same RMCR-format-field family as O-FRD-00149; 'responsive verification statements' aren't modeled in this corpus's credit report.
- **SME:** [ ] agree [ ] correct: ______

### G082 — O-FRD-00672 [O-FRD]
- **Q:** Were all additional manual underwriting credit assessment requirements met?
- **Defect condition:** Credit score in caution range with a high balance-to-limits or high overall use of revolving credit
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 790
- **Severity:** Critical
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **SME:** [ ] agree [ ] correct: ______

### G083 — O-FRD-00169 [O-FRD]
- **Q:** Were all additional manual underwriting credit assessment requirements met?
- **Defect condition:** Loan approved although a recent significant increase in open accounts is evidenced
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 919
- **Severity:** Critical
- **Rationale:** Needs tradeline open-date history (to detect a 'recent, significant increase in open accounts') this pilot doesn't parse, plus an undefined 'significant' threshold -- kept YELLOW rather than RED because a specific new-account count could ground it once an SME supplies the number; not purely a judgment call by wording alone.
- **SME:** [ ] agree [ ] correct: ______

### G084 — O-FRD-00170 [O-FRD]
- **Q:** Were all additional manual underwriting credit assessment requirements met?
- **Defect condition:** Loan approved with a pattern of high balance-to-limits or high overall use of revolving credit
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 951
- **Severity:** Critical
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **SME:** [ ] agree [ ] correct: ______

### G086 — O-FRD-50021 [O-FRD]
- **Q:** Were all additional monthly debt payment-to-income ratio liability evaluation requirements met?
- **Defect condition:** Business debt(s) not included in DTI or documentation debt(s) is paid by the business is missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 785
- **Severity:** Critical
- **Rationale:** Same business-debt-in-DTI family as O-FNM-50006 (FRD wording variant) -- MISCLASSIFIED by the same mechanical doc_presence false-positive.
- **SME:** [ ] agree [ ] correct: ______

### G087 — O-FRD-00173 [O-FRD]
- **Q:** Were all additional monthly debt payment-to-income ratio liability evaluation requirements met?
- **Defect condition:** Contingent liability without evidence another obligor has made payments for the last 12 months
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 804
- **Severity:** Critical
- **Rationale:** Needs a 12-month third-party-payment history (contingent-liability co-obligor, cosigner, or authorized-user account owner) -- `urla_liabilities`/`tradelines` capture the liability itself but not who else has been paying it or for how long; no such payment-history document exists in this corpus.
- **SME:** [ ] agree [ ] correct: ______

### G088 — O-FRD-00679 [O-FRD]
- **Q:** Were all additional monthly debt payment-to-income ratio liability evaluation requirements met?
- **Defect condition:** Housing or DTI ratio exceed the guidelines without a written explanation justifying the decision
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 863
- **Severity:** Critical
- **Rationale:** PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- **SME:** [ ] agree [ ] correct: ______

### G089 — Paystub Loans [O-FRD]
- **Q:** Were all additional monthly debt payment-to-income ratio liability evaluation requirements met?
- **Defect condition:** Loan/deductions listed on the paystubs were not addressed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 912
- **Severity:** Critical
- **Rationale:** Verified against the actual synthetic paystub (loan 01, `03_Paystub_Most_Recent.pdf`): its Deductions section lists only standard tax withholdings (Federal Withholding, Social Security, Medicare, NC State Tax) -- no loan-type deduction or military allotment line appears in any paystub in this corpus. Genuine Bucket-A-style fixture gap (the paystub doc type exists; the specific line item this rule needs does not), not a Bucket-B extraction-deepening candidate -- there is nothing yet to extract.
- **SME:** [ ] agree [ ] correct: ______

### G090 — O-FRD-56095 [O-FRD]
- **Q:** Were all additional monthly debt payment-to-income ratio liability evaluation requirements met?
- **Defect condition:** Other property owned expenses excluded & no evidence uninterested party made pymts for last 12 mos
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 990
- **Severity:** Critical
- **Rationale:** PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- **SME:** [ ] agree [ ] correct: ______

### G091 — O-FRD-03074 [O-FRD]
- **Q:** Were all additional monthly debt payment-to-income ratio liability evaluation requirements met?
- **Defect condition:** Solar panels under a lease/power purchase agreement were excluded and documentation of terms not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1029
- **Severity:** Critical
- **Rationale:** Needs a lease/HELOC/timeshare/solar-panel-agreement/virtual-currency-secured-loan document -- none of these niche liability-collateral document types exist in this corpus (same 'document family the synthetic corpus never modeled' pattern as several asset-verification YELLOW groups).
- **SME:** [ ] agree [ ] correct: ______

### G092 — Tax Liability [O-FRD]
- **Q:** Were all additional monthly debt payment-to-income ratio liability evaluation requirements met?
- **Defect condition:** There are federal income taxes due on the current year tax return and proof paid has not been obtain
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 880
- **Severity:** Critical
- **Rationale:** Current-year tax return + proof-of-payment documentation -- not a doc type in this corpus (identical condition text recurs across FHA/FRD/RHS/VA/FNM -- a single fixture gap, not five separate ones).
- **SME:** [ ] agree [ ] correct: ______

### G093 — O-FRD-00821 [O-FRD]
- **Q:** Were all additional monthly debt payment-to-income ratio liability evaluation requirements met?
- **Defect condition:** Updated credit report revealed impactful additional debts, not re-underwritten to include in DTI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1057
- **Severity:** Critical
- **Rationale:** PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- **SME:** [ ] agree [ ] correct: ______

### G095 — O-RHS-57146 [O-RHS]
- **Q:** Were all adverse or derogatory credit requirements met?
- **Defect condition:** Borr has delinquent federal tax/non-tax debt without a lender’s cert of the applicant eligibility
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 847
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G096 — O-RHS-02821 [O-RHS]
- **Q:** Were all adverse or derogatory credit requirements met?
- **Defect condition:** Disputed account reported does not qualify for an exception and not downgraded to Refer
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 885
- **Severity:** Critical
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **SME:** [ ] agree [ ] correct: ______

### G097 — O-RHS-02792 [O-RHS]
- **Q:** Were all adverse or derogatory credit requirements met?
- **Defect condition:** Foreclosure sale or deed in lieu in the last 3 years and a credit exception was not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1005
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G098 — O-RHS-02818 [O-RHS]
- **Q:** Were all adverse or derogatory credit requirements met?
- **Defect condition:** GUS-Outstanding collection $2k+ and documentation of no-impact to equity/ability to repay is missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 884
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G099 — O-RHS-02825 [O-RHS]
- **Q:** Were all adverse or derogatory credit requirements met?
- **Defect condition:** Late rental or mortgage payment reported/verified does not meet guidelines/exception not verified
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 903
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G100 — O-RHS-02793 [O-RHS]
- **Q:** Were all adverse or derogatory credit requirements met?
- **Defect condition:** Loan approval does not evidence exception for Chapter 7 bankruptcy reported within 3 years
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1004
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G101 — O-RHS-02794 [O-RHS]
- **Q:** Were all adverse or derogatory credit requirements met?
- **Defect condition:** Loan approved with open Chapter 13 bankruptcy and does not meet guidelines
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 791
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G102 — O-RHS-02817 [O-RHS]
- **Q:** Were all adverse or derogatory credit requirements met?
- **Defect condition:** MAN-Outstanding collection $2k+ and documentation of no-impact to equity/ability to repay is missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 922
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G104 — O-RHS-02819 [O-RHS]
- **Q:** Were all adverse or derogatory credit requirements met?
- **Defect condition:** Open non-federal judgment not PIF or have evidence of 3 timely non-lump sum pymts as per agreement
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 974
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G105 — O-RHS-02816 [O-RHS]
- **Q:** Were all adverse or derogatory credit requirements met?
- **Defect condition:** Outstanding collection reported and validation of monthly payment included in DTI is missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 794
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G106 — O-FHA-02236 [O-FHA]
- **Q:** Were all alimony, child support, and maintenance debt requirements met?
- **Defect condition:** Alimony/child support/maintenance payments is not in DTI and required documentation is missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 770
- **Severity:** Critical
- **Rationale:** Divorce decree / court order / separation agreement documenting alimony, child support, or maintenance payment terms -- not a doc type in this corpus.
- **SME:** [ ] agree [ ] correct: ______

### G108 — O-RHS-02823 [O-RHS]
- **Q:** Were all applicant(s) debt/liabilities requirements met?
- **Defect condition:** Authorized user account did not meet requirements and the loan was not downgraded to a Refer
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 883
- **Severity:** Critical
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **SME:** [ ] agree [ ] correct: ______

### G109 — O-RHS-02822 [O-RHS]
- **Q:** Were all applicant(s) debt/liabilities requirements met?
- **Defect condition:** Authorized user account was considered while it was not indicative of the applicants credit history
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 780
- **Severity:** Critical
- **Rationale:** Needs a 12-month third-party-payment history (contingent-liability co-obligor, cosigner, or authorized-user account owner) -- `urla_liabilities`/`tradelines` capture the liability itself but not who else has been paying it or for how long; no such payment-history document exists in this corpus.
- **SME:** [ ] agree [ ] correct: ______

### G110 — O-RHS-02837 [O-RHS]
- **Q:** Were all applicant(s) debt/liabilities requirements met?
- **Defect condition:** Credit report for non-purchase spouse not obtained in community property state for DTI analysis
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 975
- **Severity:** Critical
- **Rationale:** A second credit report (the non-borrowing/non-purchasing spouse's) plus the applicable state's community-property statute reference -- neither exists in this corpus; every loan extracts exactly one applicant-side credit report at most.
- **SME:** [ ] agree [ ] correct: ______

### G111 — O-RHS-02831 [O-RHS]
- **Q:** Were all applicant(s) debt/liabilities requirements met?
- **Defect condition:** Loan approved with delinquent federal non-tax debt without determining if account has been resolved
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 846
- **Severity:** Critical
- **Rationale:** Federal debt / delinquent federal (tax or non-tax) obligation documentation (repayment status, CAIVRS-adjacent) -- not modeled beyond loan 02's CAIVRS/LDP/GSA screenprint (a different, narrower fact).
- **SME:** [ ] agree [ ] correct: ______

### G112 — Paystub Loans [O-RHS]
- **Q:** Were all applicant(s) debt/liabilities requirements met?
- **Defect condition:** Loan/deductions listed on the paystubs were not addressed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 913
- **Severity:** Critical
- **Rationale:** Verified against the actual synthetic paystub (loan 01, `03_Paystub_Most_Recent.pdf`): its Deductions section lists only standard tax withholdings (Federal Withholding, Social Security, Medicare, NC State Tax) -- no loan-type deduction or military allotment line appears in any paystub in this corpus. Genuine Bucket-A-style fixture gap (the paystub doc type exists; the specific line item this rule needs does not), not a Bucket-B extraction-deepening candidate -- there is nothing yet to extract.
- **SME:** [ ] agree [ ] correct: ______

### G113 — O-RHS-02824 [O-RHS]
- **Q:** Were all applicant(s) debt/liabilities requirements met?
- **Defect condition:** Manual UW with a credit score below 680 did not verify 12 mos verification of rent as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1061
- **Severity:** Critical
- **Rationale:** Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- **SME:** [ ] agree [ ] correct: ______

### G114 — O-RHS-02826 [O-RHS]
- **Q:** Were all applicant(s) debt/liabilities requirements met?
- **Defect condition:** Recent non-disclosed significant debt on the credit report was not explained by the applicant(s)
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1013
- **Severity:** Critical
- **Rationale:** MISCLASSIFIED (matched 'was not' + 'credit report' keyword) -- same direction as UndisclosedLiabilityShape's real condition plus a borrower-explanation requirement, same family/caution as O-RHS-50563 above.
- **SME:** [ ] agree [ ] correct: ______

### G115 — O-RHS-50563 [O-RHS]
- **Q:** Were all applicant(s) debt/liabilities requirements met?
- **Defect condition:** Report has significant debt not on 1003 w/out explanation or added to DTI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 950
- **Severity:** Critical
- **Rationale:** MISCLASSIFIED (matched 'was not provided'/'not added' + 'credit report' keyword) -- same direction as UndisclosedLiabilityShape's real condition (credit report shows a debt the 1003 doesn't), but bundles an extra explanation/DTI-inclusion requirement our shape doesn't test -- same caution as the F_UNDISCLOSED_DEBT family and decision 019's verdict on that shape.
- **SME:** [ ] agree [ ] correct: ______

### G116 — O-RHS-50564 [O-RHS]
- **Q:** Were all applicant(s) debt/liabilities requirements met?
- **Defect condition:** Significant debt not considered by GUS & payment not added/loan resubmitted
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 887
- **Severity:** Critical
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **SME:** [ ] agree [ ] correct: ______

### G117 — Tax Liability [O-RHS]
- **Q:** Were all applicant(s) debt/liabilities requirements met?
- **Defect condition:** There are federal income taxes due on the current year tax return and proof paid has not been obtain
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 881
- **Severity:** Critical
- **Rationale:** Current-year tax return + proof-of-payment documentation -- not a doc type in this corpus (identical condition text recurs across FHA/FRD/RHS/VA/FNM -- a single fixture gap, not five separate ones).
- **SME:** [ ] agree [ ] correct: ______

### G118 — O-RHS-57144 [O-RHS]
- **Q:** Were all applicant(s) debt/liabilities requirements met?
- **Defect condition:** Undisclosed debt not on the application but found during processing not manually entered into GUS
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1048
- **Severity:** Critical
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **SME:** [ ] agree [ ] correct: ______

### G120 — O-FHA-02224 [O-FHA]
- **Q:** Were all bankruptcy requirements met?
- **Defect condition:** Bankruptcy in TOTAL credit report did not meet discharge time req's & was not downgraded to Refer
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 781
- **Severity:** Critical
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **SME:** [ ] agree [ ] correct: ______

### G122 — O-FRD-00171 [O-FRD]
- **Q:** Were all credit assessment requirements met?
- **Defect condition:** Applicant(s) housing pay history for at least the prior 12-months is not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 935
- **Severity:** Critical
- **Rationale:** Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- **SME:** [ ] agree [ ] correct: ______

### G123 — O-FRD-00152 [O-FRD]
- **Q:** Were all credit assessment requirements met?
- **Defect condition:** Inquiry in last 90 days did not document if new debt opened and/or new debt not considered in ratio
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 813
- **Severity:** Critical
- **Rationale:** PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- **SME:** [ ] agree [ ] correct: ______

### G124 — O-FRD-00175 [O-FRD]
- **Q:** Were all credit assessment requirements met?
- **Defect condition:** No verification was obtained by the creditor on accounts that only rate via mail with authorization
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 929
- **Severity:** Critical
- **Rationale:** 'Will rate by mail only'/'need written authorization' accounts need a separate written-verification document per account -- not a doc type this corpus models (the one credit report's tradelines don't carry a rate-by-mail flag either).
- **SME:** [ ] agree [ ] correct: ______

### G125 — O-FRD-00174 [O-FRD]
- **Q:** Were all credit assessment requirements met?
- **Defect condition:** Significant open debt from URLA is missing credit reference w/out a separate written verification
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 942
- **Severity:** Critical
- **Rationale:** MISCLASSIFIED (matched 'is missing' + 'credit report' keyword) -- the real condition is the REVERSE direction of UndisclosedLiabilityShape (a 1003 debt missing from the credit report, needing a separate written verification document), same family as F_APPLICATION_DEBT_NOT_ON_CREDIT elsewhere in this block -- not itself a credit-report-presence fact.
- **SME:** [ ] agree [ ] correct: ______

### G127 — O-VA-00128 [O-VA]
- **Q:** Were all credit history requirements met?
- **Defect condition:** RMCR does not reflect a reporting status <= 90 days of the report date for accounts with balances
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 816
- **Severity:** Major
- **Rationale:** Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- **SME:** [ ] agree [ ] correct: ______

### G128 — O-VA-00127 [O-VA]
- **Q:** Were all credit history requirements met?
- **Defect condition:** The RMCR does not list all inquiries made within the previous 90 days
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 815
- **Severity:** Critical
- **Rationale:** Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- **SME:** [ ] agree [ ] correct: ______

### G129 — O-VA-51062 [O-VA]
- **Q:** Were all credit history requirements met?
- **Defect condition:** The credit report was expired at the time of closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 769
- **Severity:** Critical
- **Rationale:** Bucket-B-close: the synthetic credit report's own text already shows 'Report Date 07/29/2025' (loan 01) and `closing_date` is already extracted from the closing disclosure -- a days-elapsed comparison is crisp arithmetic once `report_date` joins FIELD_SPECS['credit_report']. Not fully ready: the expiration threshold itself is agency-specific (RHS states 120 days explicitly; VA's 'expired' needs its own Guide-cited day count) and needs an SME/guide citation before hardcoding, not just a new field.
- **SME:** [ ] agree [ ] correct: ______

### G130 — O-VA-03097 [O-VA]
- **Q:** Were all credit history requirements met?
- **Defect condition:** Unpaid collection accounts with no documented re-established credit prior to approval
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 796
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G132 — O-RHS-02791 [O-RHS]
- **Q:** Were all credit report and credit history requirements met?
- **Defect condition:** Credit exception not in the file in a manually underwritten loan with unacceptable credit
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1043
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G133 — O-RHS-50011 [O-RHS]
- **Q:** Were all credit report and credit history requirements met?
- **Defect condition:** Determination of new debt from inquiries reported within 90-days of closing is not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 814
- **Severity:** Critical
- **Rationale:** Needs a parsed Inquiries table (already visible in the loan 01 credit report's text -- 'Inquiries (last 120 days)' with Date/Bureau/Requesting Party -- but not yet in FIELD_SPECS/entities) cross-referenced against whether new debt was opened; Bucket-B-style (deepen extraction of a section already present in the one document we have), not a missing document.
- **SME:** [ ] agree [ ] correct: ______

### G134 — O-RHS-02836 [O-RHS]
- **Q:** Were all credit report and credit history requirements met?
- **Defect condition:** Determination that participants in credit counseling meet program criteria/credit exceptions missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 926
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G135 — O-RHS-57148 [O-RHS]
- **Q:** Were all credit report and credit history requirements met?
- **Defect condition:** Housing payments for the last 12 months were not verified with acceptable documentation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 890
- **Severity:** Critical
- **Rationale:** Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- **SME:** [ ] agree [ ] correct: ______

### G136 — O-RHS-50007 [O-RHS]
- **Q:** Were all credit report and credit history requirements met?
- **Defect condition:** RMCR does not reflect a reporting status <= 90 days of the report date for accounts with balances
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 761
- **Severity:** Critical
- **Rationale:** Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- **SME:** [ ] agree [ ] correct: ______

### G137 — O-RHS-50560 [O-RHS]
- **Q:** Were all credit report and credit history requirements met?
- **Defect condition:** The appropriate rep credit score not used with scores of 640 or greater
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 836
- **Severity:** Critical
- **Rationale:** Deepen `credit_report` FIELD_SPECS: the doc's own text already shows 'Middle Score — Borrower 742' / 'Middle Score — Co-Borrower 758' (loan 01) but no score field is parsed today. Even once parsed, applying these rules needs a per-program minimum-score / representative-score-selection table that is a Selling-Guide business rule, not a fact derivable from any loan document -- Bucket-B on the extraction side, still needs an SME-sourced threshold table beyond that.
- **SME:** [ ] agree [ ] correct: ______

### G138 — O-RHS-50559 [O-RHS]
- **Q:** Were all credit report and credit history requirements met?
- **Defect condition:** The credit report was over 120 days old when the loan closed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 768
- **Severity:** Critical
- **Rationale:** Bucket-B-close: the synthetic credit report's own text already shows 'Report Date 07/29/2025' (loan 01) and `closing_date` is already extracted from the closing disclosure -- a days-elapsed comparison is crisp arithmetic once `report_date` joins FIELD_SPECS['credit_report']. Not fully ready: the expiration threshold itself is agency-specific (RHS states 120 days explicitly; VA's 'expired' needs its own Guide-cited day count) and needs an SME/guide citation before hardcoding, not just a new field.
- **SME:** [ ] agree [ ] correct: ______

### G139 — O-RHS-02789 [O-RHS]
- **Q:** Were all credit report and credit history requirements met?
- **Defect condition:** The necessary analysis to validate the credit score is usable for underwriting the loan is missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1058
- **Severity:** Critical
- **Rationale:** Deepen `credit_report` FIELD_SPECS: the doc's own text already shows 'Middle Score — Borrower 742' / 'Middle Score — Co-Borrower 758' (loan 01) but no score field is parsed today. Even once parsed, applying these rules needs a per-program minimum-score / representative-score-selection table that is a Selling-Guide business rule, not a fact derivable from any loan document -- Bucket-B on the extraction side, still needs an SME-sourced threshold table beyond that.
- **SME:** [ ] agree [ ] correct: ______

### G141 — O-FRD-52179 [O-FRD]
- **Q:** Were all credit report requirements met?
- **Defect condition:** A borrower has more than one of the national credit repositories with frozen credit information
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 877
- **Severity:** Critical
- **Rationale:** Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- **SME:** [ ] agree [ ] correct: ______

### G142 — CBR-Fraud Alerts-2 [O-FHA]
- **Q:** Were all credit report requirements met?
- **Defect condition:** Credit Alerts/Hawk Alerts &/or additional addresses have not been addressed and/or documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 819
- **Severity:** Major
- **Rationale:** Hawk Alert / Other Credit Alert flag -- this attribute doesn't appear anywhere in the one synthetic credit report's text; not modeled, not merely unextracted.
- **SME:** [ ] agree [ ] correct: ______

### G143 — O-FNM-00185 [O-FNM]
- **Q:** Were all credit report requirements met?
- **Defect condition:** Credit report not an original with all required identifying information &/or alterations noted
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 827
- **Severity:** Critical
- **Rationale:** Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- **Guide candidate:** B3-5.2-03 — Accuracy of Credit Information in a Credit Report (PDF p.482)
- **Guide candidate:** B3-2-09 — Erroneous Credit Report Data (PDF p.311)
- **Guide candidate:** B3-2-10 — Accuracy of DU Data, DU Tolerances, and Errors in the Credit Report (PDF p.313)
- **SME:** [ ] agree [ ] correct: ______

### G144 — O-FRD-57977 [O-FRD]
- **Q:** Were all credit report requirements met?
- **Defect condition:** Credit report used was not a hard pull generating an inquiry identified on subsequent credit reports
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 888
- **Severity:** Major
- **Rationale:** Needs a parsed Inquiries table (already visible in the loan 01 credit report's text -- 'Inquiries (last 120 days)' with Date/Bureau/Requesting Party -- but not yet in FIELD_SPECS/entities) cross-referenced against whether new debt was opened; Bucket-B-style (deepen extraction of a section already present in the one document we have), not a missing document.
- **SME:** [ ] agree [ ] correct: ______

### G145 — O-VA-50758 [O-VA]
- **Q:** Were all credit report requirements met?
- **Defect condition:** Credit reports do not meet RMCR standards &/or if multi reports, not all credit reports in the file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 822
- **Severity:** Major
- **Rationale:** Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- **SME:** [ ] agree [ ] correct: ______

### G146 — O-FNM-00182 [O-FNM]
- **Q:** Were all credit report requirements met?
- **Defect condition:** DU loan does not contain a three-in-file merged credit report for each applicant
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 857
- **Severity:** Critical
- **Rationale:** MISCLASSIFIED (matched 'not in the file' + 'credit report' keyword) -- Bucket-B-close, not a bare presence check: loan 01's synthetic credit report IS explicitly titled 'Tri-Merge Credit Report Summary — Bureaus: Equifax / Experian / TransUnion,' so the underlying fact may already be true in text, but no is_tri_merge / bureau-count field is parsed by FIELD_SPECS today -- needs extraction, not just a presence flag.
- **Guide candidate:** B3-2-09 — Erroneous Credit Report Data (PDF p.311)
- **Guide candidate:** B3-2-10 — Accuracy of DU Data, DU Tolerances, and Errors in the Credit Report (PDF p.313)
- **Guide candidate:** B3-5.1-02 — Determining the Credit Score for a Mortgage Loan (PDF p.474)
- **SME:** [ ] agree [ ] correct: ______

### G147 — O-FNM-00199 [O-FNM]
- **Q:** Were all credit report requirements met?
- **Defect condition:** Data entered into DU is inaccurate based on credit report/other credit documentation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 810
- **Severity:** Critical
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **Guide candidate:** B3-2-09 — Erroneous Credit Report Data (PDF p.311)
- **Guide candidate:** B3-2-10 — Accuracy of DU Data, DU Tolerances, and Errors in the Credit Report (PDF p.313)
- **Guide candidate:** B3-5.2-03 — Accuracy of Credit Information in a Credit Report (PDF p.482)
- **SME:** [ ] agree [ ] correct: ______

### G148 — O-FNM-50010 [O-FNM]
- **Q:** Were all credit report requirements met?
- **Defect condition:** Disputed account reported and DU has a disputed message that was not documented as resolved
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 854
- **Severity:** Critical
- **Rationale:** MISCLASSIFIED (matched 'not documented' + 'credit report' keyword) -- the real condition needs DU's own disputed-account message/resolution record, part of the same AUS-feedback-certificate gap as the F_AUS_EXPORT family (no DU export doc exists in this corpus).
- **Guide candidate:** B3-2-09 — Erroneous Credit Report Data (PDF p.311)
- **Guide candidate:** B3-2-10 — Accuracy of DU Data, DU Tolerances, and Errors in the Credit Report (PDF p.313)
- **Guide candidate:** B3-5.2-03 — Accuracy of Credit Information in a Credit Report (PDF p.482)
- **SME:** [ ] agree [ ] correct: ______

### G149 — O-FRD-50418 [O-FRD]
- **Q:** Were all credit report requirements met?
- **Defect condition:** Identifying info incorrect on credit report w/out credit being re-requested
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 825
- **Severity:** Critical
- **Rationale:** Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- **SME:** [ ] agree [ ] correct: ______

### G150 — O-FHA-00117 [O-FHA]
- **Q:** Were all credit report requirements met?
- **Defect condition:** New or changes in the debts were noted but not resubmitted to the AUS
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 970
- **Severity:** Critical
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **SME:** [ ] agree [ ] correct: ______

### G151 — O-FNM-00181 [O-FNM]
- **Q:** Were all credit report requirements met?
- **Defect condition:** Non-traditional credit was used; sufficient number of credit references warrants traditional credit
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 979
- **Severity:** Critical
- **Rationale:** Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- **Guide candidate:** B3-5.4-02 — Number and Types of Nontraditional Credit References (PDF p.506)
- **Guide candidate:** B3-2-09 — Erroneous Credit Report Data (PDF p.311)
- **Guide candidate:** B3-2-10 — Accuracy of DU Data, DU Tolerances, and Errors in the Credit Report (PDF p.313)
- **SME:** [ ] agree [ ] correct: ______

### G152 — O-FHA-50671 [O-FHA]
- **Q:** Were all credit report requirements met?
- **Defect condition:** Not all info from at least 2 repositories for credit, residence history & public records shown
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 830
- **Severity:** Critical
- **Rationale:** Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- **SME:** [ ] agree [ ] correct: ______

### G153 — O-FRD-00149 [O-FRD]
- **Q:** Were all credit report requirements met?
- **Defect condition:** Positive statement that the applicant's employment and income verification was attempted is missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 826
- **Severity:** Major
- **Rationale:** MISCLASSIFIED (matched 'did not confirm' + 'credit report' keyword) -- the real condition is whether the credit report documents that the reporting agency attempted employment/income verification, an RMCR-format field this pilot's synthetic credit report doesn't model at all.
- **SME:** [ ] agree [ ] correct: ______

### G154 — O-VA-00136 [O-VA]
- **Q:** Were all credit report requirements met?
- **Defect condition:** Prior housing history are not reported and verifications were not obtained for rental/mortgages
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 891
- **Severity:** Critical
- **Rationale:** Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- **SME:** [ ] agree [ ] correct: ______

### G155 — O-FNM-00189 [O-FNM]
- **Q:** Were all credit report requirements met?
- **Defect condition:** RMCR does not reflect a reporting status <= 90 days of the report date for accounts with balances
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 824
- **Severity:** Major
- **Rationale:** Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- **Guide candidate:** B3-2-09 — Erroneous Credit Report Data (PDF p.311)
- **Guide candidate:** B3-2-10 — Accuracy of DU Data, DU Tolerances, and Errors in the Credit Report (PDF p.313)
- **Guide candidate:** B3-5.2-03 — Accuracy of Credit Information in a Credit Report (PDF p.482)
- **SME:** [ ] agree [ ] correct: ______

### G156 — O-FNM-56945 [O-FNM]
- **Q:** Were all credit report requirements met?
- **Defect condition:** The borr's present address not within the U.S. or military address and was not manually underwritten
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 823
- **Severity:** Major
- **Rationale:** Needs a borrower current-address country/military-address classification -- `final_1003` extraction captures identity/employment/loan fields today, not a structured current-address country flag.
- **Guide candidate:** B3-2-09 — Erroneous Credit Report Data (PDF p.311)
- **Guide candidate:** B3-2-10 — Accuracy of DU Data, DU Tolerances, and Errors in the Credit Report (PDF p.313)
- **Guide candidate:** B3-5.2-03 — Accuracy of Credit Information in a Credit Report (PDF p.482)
- **SME:** [ ] agree [ ] correct: ______

### G157 — O-FRD-00148 [O-FRD]
- **Q:** Were all credit report requirements met?
- **Defect condition:** The credit report does not include the required credit information for each debt shown
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 828
- **Severity:** Critical
- **Rationale:** Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- **SME:** [ ] agree [ ] correct: ______

### G158 — O-FRD-57978 [O-FRD]
- **Q:** Were all credit report requirements met?
- **Defect condition:** The credit report submitted to LPA did not include trended credit data
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1042
- **Severity:** Major
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **SME:** [ ] agree [ ] correct: ______

### G159 — O-FRD-00146 [O-FRD]
- **Q:** Were all credit report requirements met?
- **Defect condition:** The report in the file is not  in the proper format with required information and/or appears altered
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 831
- **Severity:** Critical
- **Rationale:** Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- **SME:** [ ] agree [ ] correct: ______

### G162 — O-FRD-00671 [O-FRD]
- **Q:** Were all credit score requirements met?
- **Defect condition:** Credit scores used for eligibility in higher risk products did not meet the required minimum
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 956
- **Severity:** Critical
- **Rationale:** Deepen `credit_report` FIELD_SPECS: the doc's own text already shows 'Middle Score — Borrower 742' / 'Middle Score — Co-Borrower 758' (loan 01) but no score field is parsed today. Even once parsed, applying these rules needs a per-program minimum-score / representative-score-selection table that is a Selling-Guide business rule, not a fact derivable from any loan document -- Bucket-B on the extraction side, still needs an SME-sourced threshold table beyond that.
- **SME:** [ ] agree [ ] correct: ______

### G163 — O-FRD-50024 [O-FRD]
- **Q:** Were all credit score requirements met?
- **Defect condition:** Disputed account reporting without evidence of resolution and accuracy of credit score
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 853
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G164 — O-FNM-51042 [O-FNM]
- **Q:** Were all credit score requirements met?
- **Defect condition:** Minimum credit score requirements were not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 955
- **Severity:** Critical
- **Rationale:** Deepen `credit_report` FIELD_SPECS: the doc's own text already shows 'Middle Score — Borrower 742' / 'Middle Score — Co-Borrower 758' (loan 01) but no score field is parsed today. Even once parsed, applying these rules needs a per-program minimum-score / representative-score-selection table that is a Selling-Guide business rule, not a fact derivable from any loan document -- Bucket-B on the extraction side, still needs an SME-sourced threshold table beyond that.
- **Guide candidate:** B3-5.1-02 — Determining the Credit Score for a Mortgage Loan (PDF p.474)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-2-09 — Erroneous Credit Report Data (PDF p.311)
- **SME:** [ ] agree [ ] correct: ______

### G165 — O-FNM-55988 [O-FNM]
- **Q:** Were all credit score requirements met?
- **Defect condition:** Representative or average median score not used as req'd per number of borrowers in a manual UW
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 936
- **Severity:** Major
- **Rationale:** Deepen `credit_report` FIELD_SPECS: the doc's own text already shows 'Middle Score — Borrower 742' / 'Middle Score — Co-Borrower 758' (loan 01) but no score field is parsed today. Even once parsed, applying these rules needs a per-program minimum-score / representative-score-selection table that is a Selling-Guide business rule, not a fact derivable from any loan document -- Bucket-B on the extraction side, still needs an SME-sourced threshold table beyond that.
- **Guide candidate:** B3-5.1-02 — Determining the Credit Score for a Mortgage Loan (PDF p.474)
- **Guide candidate:** B3-5.4-02 — Number and Types of Nontraditional Credit References (PDF p.506)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G166 — O-FRD-00160 [O-FRD]
- **Q:** Were all credit score requirements met?
- **Defect condition:** The appropriate credit score was not used to analyze the applicant(s) credit reputation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 873
- **Severity:** Critical
- **Rationale:** Deepen `credit_report` FIELD_SPECS: the doc's own text already shows 'Middle Score — Borrower 742' / 'Middle Score — Co-Borrower 758' (loan 01) but no score field is parsed today. Even once parsed, applying these rules needs a per-program minimum-score / representative-score-selection table that is a Selling-Guide business rule, not a fact derivable from any loan document -- Bucket-B on the extraction side, still needs an SME-sourced threshold table beyond that.
- **SME:** [ ] agree [ ] correct: ______

### G167 — O-FNM-00192 [O-FNM]
- **Q:** Were all credit score requirements met?
- **Defect condition:** The incorrect representative credit score was used in a manually underwritten loan
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1017
- **Severity:** Critical
- **Rationale:** Deepen `credit_report` FIELD_SPECS: the doc's own text already shows 'Middle Score — Borrower 742' / 'Middle Score — Co-Borrower 758' (loan 01) but no score field is parsed today. Even once parsed, applying these rules needs a per-program minimum-score / representative-score-selection table that is a Selling-Guide business rule, not a fact derivable from any loan document -- Bucket-B on the extraction side, still needs an SME-sourced threshold table beyond that.
- **Guide candidate:** B3-5.1-02 — Determining the Credit Score for a Mortgage Loan (PDF p.474)
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **Guide candidate:** A2-3.2-01 — Loan Repurchases and Make Whole Payments Requested by Fannie Mae (PDF p.60)
- **SME:** [ ] agree [ ] correct: ______

### G169 — O-FHA-02234 [O-FHA]
- **Q:** Were all debt and liability evaluation requirements met?
- **Defect condition:** Undisclosed debt discovered and the actual payment amount was not verified and included in DTI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 949
- **Severity:** Critical
- **Rationale:** Closest textual match to the already-mapped (but zero-exception-code) `UndisclosedLiabilityShape` (credit-report tradeline with no matching 1003 Section 2c liability) -- verified NOT a safe direct wire (decision 019): this row bundles an additional requirement (borrower explanation obtained, and/or the payment verified and included in DTI) our shape doesn't test. Wiring it as-is would risk false negatives on loans where the undisclosed debt is present but the compound condition isn't met, or false positives once the explanation-documentation piece is added and our shape can't see it. Kept YELLOW pending that extra logic being built.
- **SME:** [ ] agree [ ] correct: ______

### G171 — O-FNM-00724 [O-FNM]
- **Q:** Were all debt-to-income (DTI) ratio requirements met?
- **Defect condition:** Loan approved with DTI over 36% and borrower does not meet credit and reserve requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 954
- **Severity:** Critical
- **Rationale:** PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-5.1-02 — Determining the Credit Score for a Mortgage Loan (PDF p.474)
- **Guide candidate:** B3-6-02 — Debt-to-Income Ratios (PDF p.514)
- **SME:** [ ] agree [ ] correct: ______

### G172 — O-FNM-00722 [O-FNM]
- **Q:** Were all debt-to-income (DTI) ratio requirements met?
- **Defect condition:** Not re-underwritten where additional debt or reduced income caused DTI to increase beyond tolerance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 856
- **Severity:** Critical
- **Rationale:** PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- **Guide candidate:** B3-6-02 — Debt-to-Income Ratios (PDF p.514)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-3.1-01 — General Income Information (PDF p.318)
- **SME:** [ ] agree [ ] correct: ______

### G174 — O-VA-50016 [O-VA]
- **Q:** Were all debts and obligations requirements met?
- **Defect condition:** A contingent liability or co-signed obligation was not  included in ratios
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 805
- **Severity:** Critical
- **Rationale:** Needs a 12-month third-party-payment history (contingent-liability co-obligor, cosigner, or authorized-user account owner) -- `urla_liabilities`/`tradelines` capture the liability itself but not who else has been paying it or for how long; no such payment-history document exists in this corpus.
- **SME:** [ ] agree [ ] correct: ______

### G175 — O-VA-00131 [O-VA]
- **Q:** Were all debts and obligations requirements met?
- **Defect condition:** A significant debt on the 1003 is not reported and verification of liability is missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1060
- **Severity:** Critical
- **Rationale:** MISCLASSIFIED (matched 'is not reported' + 'credit report' keyword) -- same reverse-direction family as O-FRD-00174 (F_APPLICATION_DEBT_NOT_ON_CREDIT), not a credit-report-presence fact.
- **SME:** [ ] agree [ ] correct: ______

### G176 — O-VA-00133 [O-VA]
- **Q:** Were all debts and obligations requirements met?
- **Defect condition:** An undisclosed debt was noted or discovered but an explanation was not obtained from the borrower
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1046
- **Severity:** Critical
- **Rationale:** Closest textual match to the already-mapped (but zero-exception-code) `UndisclosedLiabilityShape` (credit-report tradeline with no matching 1003 Section 2c liability) -- verified NOT a safe direct wire (decision 019): this row bundles an additional requirement (borrower explanation obtained, and/or the payment verified and included in DTI) our shape doesn't test. Wiring it as-is would risk false negatives on loans where the undisclosed debt is present but the compound condition isn't met, or false positives once the explanation-documentation piece is added and our shape can't see it. Kept YELLOW pending that extra logic being built.
- **SME:** [ ] agree [ ] correct: ______

### G177 — O-VA-58106 [O-VA]
- **Q:** Were all debts and obligations requirements met?
- **Defect condition:** Debts did not include child care (to age 12), significant commutes, &/or costs related to employment
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 793
- **Severity:** Major
- **Rationale:** VA job-related-expense debt (child care, commute costs) documentation -- not a doc type or field this corpus's single VA loan (03) models.
- **SME:** [ ] agree [ ] correct: ______

### G178 — Paystub Loans [O-VA]
- **Q:** Were all debts and obligations requirements met?
- **Defect condition:** Loan/deductions listed on the paystubs were not addressed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 914
- **Severity:** Critical
- **Rationale:** Verified against the actual synthetic paystub (loan 01, `03_Paystub_Most_Recent.pdf`): its Deductions section lists only standard tax withholdings (Federal Withholding, Social Security, Medicare, NC State Tax) -- no loan-type deduction or military allotment line appears in any paystub in this corpus. Genuine Bucket-A-style fixture gap (the paystub doc type exists; the specific line item this rule needs does not), not a Bucket-B extraction-deepening candidate -- there is nothing yet to extract.
- **SME:** [ ] agree [ ] correct: ______

### G179 — O-VA-00135 [O-VA]
- **Q:** Were all debts and obligations requirements met?
- **Defect condition:** No verification was obtained by the creditor on accounts that only rate via mail with authorization
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1025
- **Severity:** Critical
- **Rationale:** 'Will rate by mail only'/'need written authorization' accounts need a separate written-verification document per account -- not a doc type this corpus models (the one credit report's tradelines don't carry a rate-by-mail flag either).
- **SME:** [ ] agree [ ] correct: ______

### G180 — O-VA-58295 [O-VA]
- **Q:** Were all debts and obligations requirements met?
- **Defect condition:** Paystub/LES has an allotment without documenting it is related to a debt or other obligation(s)
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 992
- **Severity:** Critical
- **Rationale:** Verified against the actual synthetic paystub (loan 01, `03_Paystub_Most_Recent.pdf`): its Deductions section lists only standard tax withholdings (Federal Withholding, Social Security, Medicare, NC State Tax) -- no loan-type deduction or military allotment line appears in any paystub in this corpus. Genuine Bucket-A-style fixture gap (the paystub doc type exists; the specific line item this rule needs does not), not a Bucket-B extraction-deepening candidate -- there is nothing yet to extract.
- **SME:** [ ] agree [ ] correct: ______

### G181 — O-VA-03125 [O-VA]
- **Q:** Were all debts and obligations requirements met?
- **Defect condition:** Student loan(s) and correct monthly payment not used in analysis
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1037
- **Severity:** Critical
- **Rationale:** Student-loan payment-substitution math (0.5%/1% of balance when the credit report shows a $0 or missing payment) is crisp arithmetic, and `extract_tradelines()` already captures tradeline type/balance/monthly_payment (loan 01 has one Student tradeline) -- but verifying which qualifying-payment value the lender ACTUALLY used needs a DTI/qualifying-payment worksheet this pilot doesn't extract or derive from any document today. Trigger-detection is Bucket-B-close; the verification half is not.
- **SME:** [ ] agree [ ] correct: ______

### G182 — O-VA-50022 [O-VA]
- **Q:** Were all debts and obligations requirements met?
- **Defect condition:** Student loan(s) with payments due within 12 months of approval were not included in ratios
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1034
- **Severity:** Critical
- **Rationale:** Student-loan payment-substitution math (0.5%/1% of balance when the credit report shows a $0 or missing payment) is crisp arithmetic, and `extract_tradelines()` already captures tradeline type/balance/monthly_payment (loan 01 has one Student tradeline) -- but verifying which qualifying-payment value the lender ACTUALLY used needs a DTI/qualifying-payment worksheet this pilot doesn't extract or derive from any document today. Trigger-detection is Bucket-B-close; the verification half is not.
- **SME:** [ ] agree [ ] correct: ______

### G183 — O-VA-50769 [O-VA]
- **Q:** Were all debts and obligations requirements met?
- **Defect condition:** The non-borrowing veteran's spouse’s debts not considered in a community property state
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1032
- **Severity:** Critical
- **Rationale:** A second credit report (the non-borrowing/non-purchasing spouse's) plus the applicable state's community-property statute reference -- neither exists in this corpus; every loan extracts exactly one applicant-side credit report at most.
- **SME:** [ ] agree [ ] correct: ______

### G186 — O-FNM-57256 [O-FNM]
- **Q:** Were all debts paid off at or prior to closing requirements met?
- **Defect condition:** Debt paid off or paid down to qualify & source/sufficient assets remain for the loan not provided
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 991
- **Severity:** Critical
- **Rationale:** Needs a source-of-funds-for-payoff cross-reference against remaining total assets -- `payoff_amount_1003`/`cash_out_to_borrower_1003` and `bank_txns` exist independently, but the specific 'paid down solely to qualify, sufficient assets remain' derivation isn't built; related to asset-verification's net-sale-proceeds family (G004/G005).
- **Guide candidate:** B3-6-07 — Debts Paid Oﬀ At or Prior to Closing (PDF p.531)
- **Guide candidate:** B5-4.1-03 — Texas Section 50(a)(6) Loan Underwriting, Collateral, and Closing Considerations (PDF p.773)
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **SME:** [ ] agree [ ] correct: ______

### G187 — O-FNM-50004 [O-FNM]
- **Q:** Were all debts paid off at or prior to closing requirements met?
- **Defect condition:** Documentation of assets to cover a 30-day account, in excess of reserves/closing funds, is missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 760
- **Severity:** Critical
- **Rationale:** MISCLASSIFIED by amq_compiler.py's mechanical doc_presence rule (matched 'in excess' + 'credit report' keyword) -- the real condition is asset-sufficiency to cover a flagged 30-day account beyond reserves/closing funds, not credit-report presence. Needs a cross-reference of the flagged tradeline balance against total available assets (bank_txns) and reserve/closing-cost fields -- not yet derived anywhere in extract_loan.py.
- **Guide candidate:** B3-6-07 — Debts Paid Oﬀ At or Prior to Closing (PDF p.531)
- **Guide candidate:** D1-3-02 — Lender Post-Closing Quality Control Review of Approval Conditions, Underwriting Decisions, Data, and Documentation (PDF p.1068)
- **Guide candidate:** B3-2-04 — DU Documentation Requirements (PDF p.305)
- **SME:** [ ] agree [ ] correct: ______

### G188 — O-FNM-50007 [O-FNM]
- **Q:** Were all debts paid off at or prior to closing requirements met?
- **Defect condition:** Non-medical charge-offs on non-mtg accts of $250 or more or total balances exceed $1,000 not PIF
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 792
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **Guide candidate:** B3-6-07 — Debts Paid Oﬀ At or Prior to Closing (PDF p.531)
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **SME:** [ ] agree [ ] correct: ______

### G189 — O-FNM-50008 [O-FNM]
- **Q:** Were all debts paid off at or prior to closing requirements met?
- **Defect condition:** Non-medical collections on non-mtg accts of $250 or more or total balances exceed $1,000 not PIF
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 799
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **Guide candidate:** B3-6-07 — Debts Paid Oﬀ At or Prior to Closing (PDF p.531)
- **Guide candidate:** B2-2-02 — Non–U.S. Citizen Borrower Eligibility Requirements (PDF p.243)
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **SME:** [ ] agree [ ] correct: ______

### G191 — O-FNM-50014 [O-FNM]
- **Q:** Were all debts paid off at or prior to closing requirements met?
- **Defect condition:** UW did not require outstanding judgment(s) be satisfied prior to or at closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 900
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **Guide candidate:** B3-6-07 — Debts Paid Oﬀ At or Prior to Closing (PDF p.531)
- **Guide candidate:** B5-3.1-02 — Conversion of Construction-to-Permanent Financing: Single-Closing Transactions (PDF p.736)
- **Guide candidate:** B5-3.1-03 — Conversion of Construction-to-Permanent Financing: Two-Closing Transactions (PDF p.743)
- **SME:** [ ] agree [ ] correct: ______

### G192 — O-FHA-02239 [O-FHA]
- **Q:** Were all deferred obligation (excluding Student Loans) liabilities requirements met?
- **Defect condition:** A deferred obligation was not documented with the balance and terms from the creditor as required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 843
- **Severity:** Critical
- **Rationale:** Student-loan payment-substitution math (0.5%/1% of balance when the credit report shows a $0 or missing payment) is crisp arithmetic, and `extract_tradelines()` already captures tradeline type/balance/monthly_payment (loan 01 has one Student tradeline) -- but verifying which qualifying-payment value the lender ACTUALLY used needs a DTI/qualifying-payment worksheet this pilot doesn't extract or derive from any document today. Trigger-detection is Bucket-B-close; the verification half is not.
- **SME:** [ ] agree [ ] correct: ______

### G194 — O-FHA-00108 [O-FHA]
- **Q:** Were all delinquent federal non-tax debt requirements met?
- **Defect condition:** Loan approved with a delinquent federal non-tax debt without determining account resolution
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 872
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G196 — O-FHA-00109 [O-FHA]
- **Q:** Were all delinquent federal tax debt requirements met?
- **Defect condition:** Loan approved with a delinquent federal tax debt without IRS repay agreement/evidence of  payments
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 848
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G198 — O-VA-03095 [O-VA]
- **Q:** Were all derogatory/adverse account requirements met?
- **Defect condition:** Bankruptcy with no documented re-established credit prior to approval
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 782
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G199 — O-VA-00010 [O-VA]
- **Q:** Were all derogatory/adverse account requirements met?
- **Defect condition:** Documented resolution for discrepancies in obligations or other derogatory credit is missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 808
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G200 — O-VA-03096 [O-VA]
- **Q:** Were all derogatory/adverse account requirements met?
- **Defect condition:** FC or DIL with no documented re-established credit prior to approval
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 875
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G203 — O-VA-50760 [O-VA]
- **Q:** Were all derogatory/adverse account requirements met?
- **Defect condition:** Open judgements on credit report not on the URLA w/out explanation/documentation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 829
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G204 — CBR-Fraud Alerts-2 [O-FNM]
- **Q:** Were all erroneous credit report data requirements met?
- **Defect condition:** Credit Alerts/Hawk Alerts &/or additional addresses have not been addressed and/or documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 820, 821, 5012, 5013
- **Severity:** Major
- **Rationale:** Hawk Alert / Other Credit Alert flag -- this attribute doesn't appear anywhere in the one synthetic credit report's text; not modeled, not merely unextracted.
- **Guide candidate:** B3-2-09 — Erroneous Credit Report Data (PDF p.311)
- **Guide candidate:** B3-2-10 — Accuracy of DU Data, DU Tolerances, and Errors in the Credit Report (PDF p.313)
- **Guide candidate:** B3-5.2-03 — Accuracy of Credit Information in a Credit Report (PDF p.482)
- **SME:** [ ] agree [ ] correct: ______

### G205 — O-FNM-50245 [O-FNM]
- **Q:** Were all erroneous credit report data requirements met?
- **Defect condition:** Documentation of significant derog credit reporting error not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 862, 5052
- **Severity:** Critical
- **Rationale:** MISCLASSIFIED (matched 'not supported' + 'credit report' keyword) -- the real condition needs a credit-supplement/dispute-resolution document family, same as the F_DEROG_HISTORY YELLOW family elsewhere in this block, not in this corpus.
- **Guide candidate:** B3-2-09 — Erroneous Credit Report Data (PDF p.311)
- **Guide candidate:** B3-2-10 — Accuracy of DU Data, DU Tolerances, and Errors in the Credit Report (PDF p.313)
- **Guide candidate:** B3-5.2-03 — Accuracy of Credit Information in a Credit Report (PDF p.482)
- **SME:** [ ] agree [ ] correct: ______

### G207 — O-FNM-00183 [O-FNM]
- **Q:** Were all erroneous credit report data requirements met?
- **Defect condition:** The UW did not reconcile discrepancies between the credit report and the 1003 as required by DU
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 861, 5051
- **Severity:** Critical
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **Guide candidate:** B3-2-09 — Erroneous Credit Report Data (PDF p.311)
- **Guide candidate:** B3-2-10 — Accuracy of DU Data, DU Tolerances, and Errors in the Credit Report (PDF p.313)
- **Guide candidate:** B3-5.2-03 — Accuracy of Credit Information in a Credit Report (PDF p.482)
- **SME:** [ ] agree [ ] correct: ______

### G208 — O-VA-00637 [O-VA]
- **Q:** Were all federal debt requirements met?
- **Defect condition:** A delinquent/defaulted Federal debt & no documentation it is now current or is being repaid
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 845
- **Severity:** Critical
- **Rationale:** Federal debt / delinquent federal (tax or non-tax) obligation documentation (repayment status, CAIVRS-adjacent) -- not modeled beyond loan 02's CAIVRS/LDP/GSA screenprint (a different, narrower fact).
- **SME:** [ ] agree [ ] correct: ______

### G209 — O-FHA-02235 [O-FHA]
- **Q:** Were all federal debt requirements met?
- **Defect condition:** Federal debt under repayment agreement was not documented or included in the DTI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 871
- **Severity:** Critical
- **Rationale:** Federal debt / delinquent federal (tax or non-tax) obligation documentation (repayment status, CAIVRS-adjacent) -- not modeled beyond loan 02's CAIVRS/LDP/GSA screenprint (a different, narrower fact).
- **SME:** [ ] agree [ ] correct: ______

### G210 — O-VA-00083 [O-VA]
- **Q:** Were all federal debt requirements met?
- **Defect condition:** No evidence Vet asked at application if are, have, or will receive disability as per Search Reqm't
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1023
- **Severity:** Critical
- **Rationale:** Federal debt / delinquent federal (tax or non-tax) obligation documentation (repayment status, CAIVRS-adjacent) -- not modeled beyond loan 02's CAIVRS/LDP/GSA screenprint (a different, narrower fact).
- **SME:** [ ] agree [ ] correct: ______

### G212 — Tax Liability [O-VA]
- **Q:** Were all federal debt requirements met?
- **Defect condition:** There are federal income taxes due on the current year tax return and proof paid has not been obtain
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 882
- **Severity:** Critical
- **Rationale:** Federal debt / delinquent federal (tax or non-tax) obligation documentation (repayment status, CAIVRS-adjacent) -- not modeled beyond loan 02's CAIVRS/LDP/GSA screenprint (a different, narrower fact).
- **SME:** [ ] agree [ ] correct: ______

### G213 — O-FHA-51272 [O-FHA]
- **Q:** Were all federal tax lien requirements met?
- **Defect condition:** An unpaid federal tax lien was not subordinated to the subject mortgage
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1051
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G215 — Tax Liability [O-FHA]
- **Q:** Were all federal tax lien requirements met?
- **Defect condition:** There are federal income taxes due on the current year tax return and proof paid has not been obtain
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 878
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G216 — O-FHA-02228 [O-FHA]
- **Q:** Were all foreclosure requirements met?
- **Defect condition:** Loan approval does not evidence exception for foreclosure/deed-in-reported within 3 years
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 876
- **Severity:** Critical
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **SME:** [ ] agree [ ] correct: ______

### G218 — O-FHA-56985 [O-FHA]
- **Q:** Were all general liabilities and debt requirements met?
- **Defect condition:** Excluded cosigned liability without evidence the other party has made timely pymts the last 12 mos
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 806
- **Severity:** Critical
- **Rationale:** Needs a 12-month third-party-payment history (contingent-liability co-obligor, cosigner, or authorized-user account owner) -- `urla_liabilities`/`tradelines` capture the liability itself but not who else has been paying it or for how long; no such payment-history document exists in this corpus.
- **SME:** [ ] agree [ ] correct: ______

### G219 — O-FHA-50016 [O-FHA]
- **Q:** Were all general liabilities and debt requirements met?
- **Defect condition:** Lease payment(s) excluded from total monthly debt, regardless of lease term remaining
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 908
- **Severity:** Critical
- **Rationale:** Needs a lease/HELOC/timeshare/solar-panel-agreement/virtual-currency-secured-loan document -- none of these niche liability-collateral document types exist in this corpus (same 'document family the synthetic corpus never modeled' pattern as several asset-verification YELLOW groups).
- **SME:** [ ] agree [ ] correct: ______

### G220 — O-FHA-54570 [O-FHA]
- **Q:** Were all general liabilities and debt requirements met?
- **Defect condition:** Source of funds to pay off debts PTC not documented, were unacceptable &/or new debt not in DTI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1030
- **Severity:** Critical
- **Rationale:** PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- **SME:** [ ] agree [ ] correct: ______

### G222 — O-FHA-02230 [O-FHA]
- **Q:** Were all housing obligation/mortgage payment history requirements met?
- **Defect condition:** Housing delinquency within last 12 mos on TOTAL credit report and was not downgraded to a Refer
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 902
- **Severity:** Critical
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **SME:** [ ] agree [ ] correct: ______

### G224 — O-FHA-56074 [O-FHA]
- **Q:** Were all housing obligation/mortgage payment history requirements met?
- **Defect condition:** PITIA of all properties owned by the borrower were not included in DTI as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 986, 987
- **Severity:** Critical
- **Rationale:** PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- **SME:** [ ] agree [ ] correct: ______

### G225 — O-FHA-02238 [O-FHA]
- **Q:** Were all installment loan requirements met?
- **Defect condition:** Installment loan with payment in the credit report/loan agreement/statement is excluded from DTI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 893
- **Severity:** Critical
- **Rationale:** The percentage-of-balance math (5%/1.5%/0.5% thresholds) is crisp arithmetic once the relevant balance is in hand, and `extract_tradelines()` already captures type/balance/monthly_payment per tradeline -- but confirming whether the LENDER actually included the computed amount in the final DTI needs a DTI worksheet this pilot doesn't derive (same gap as F_PITIA_DTI_REO); and month-by-month late-payment-in-12-months detection needs payment-history depth the tradeline snapshot (a single current 'Status' value) doesn't carry. Trigger data partly in hand; verification math not yet built.
- **SME:** [ ] agree [ ] correct: ______

### G227 — O-FHA-02223 [O-FHA]
- **Q:** Were all judgment requirements met?
- **Defect condition:** A judgment was not verified as being paid off or resolved with payment included in DTI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 901
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G229 — O-FRD-00163 [O-FRD]
- **Q:** Were all manual underwriting adverse or derogatory credit requirements met?
- **Defect condition:** A bankruptcy was noted within the last 7 years and the required documentation was not obtained
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 921
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G230 — O-FRD-55386 [O-FRD]
- **Q:** Were all manual underwriting adverse or derogatory credit requirements met?
- **Defect condition:** Foreclosure not complete at least 24 mos from Ch 7 extenuating circumstances bankruptcy in manual UW
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 952
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G231 — O-FRD-55387 [O-FRD]
- **Q:** Were all manual underwriting adverse or derogatory credit requirements met?
- **Defect condition:** Foreclosure not complete at least 48 mos from Ch 7 financial mismanagement bankruptcy in manual UW
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 953
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G232 — O-FRD-50025 [O-FRD]
- **Q:** Were all manual underwriting adverse or derogatory credit requirements met?
- **Defect condition:** Late rental and/or payment reported/verified does not meet guidelines
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 905
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G233 — O-FRD-56946 [O-FRD]
- **Q:** Were all manual underwriting adverse or derogatory credit requirements met?
- **Defect condition:** Medical collections were considered adverse or derogatory credit information in a manual UW
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 947
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G236 — O-FRD-50417 [O-FRD]
- **Q:** Were all manual underwriting adverse or derogatory credit requirements met?
- **Defect condition:** Signed letter or email directly from the borrower not obtained for adverse or derogatory accounts
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 766
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G237 — O-FRD-50416 [O-FRD]
- **Q:** Were all manual underwriting adverse or derogatory credit requirements met?
- **Defect condition:** The recovery time period requirements not met for reestablishment of credit
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 940
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G238 — O-FRD-57267 [O-FRD]
- **Q:** Were all manual underwriting adverse or derogatory credit requirements met?
- **Defect condition:** Timeshare loan not considered an installment debt regardless of how it is shown on the credit report
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1041
- **Severity:** Major
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G240 — O-FRD-52255 [O-FRD]
- **Q:** Were all manual underwriting credit assessment requirements met?
- **Defect condition:** Alt source for noncredit accounts did not use allowable documentation to verify pay history
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 973
- **Severity:** Critical
- **Rationale:** Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- **SME:** [ ] agree [ ] correct: ______

### G241 — O-FRD-50414 [O-FRD]
- **Q:** Were all manual underwriting credit assessment requirements met?
- **Defect condition:** At least 1 qualifying borr did not meet minimum trad/non trad credit req's
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 937, 938
- **Severity:** Critical
- **Rationale:** Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- **SME:** [ ] agree [ ] correct: ______

### G242 — O-FRD-58857 [O-FRD]
- **Q:** Were all manual underwriting credit assessment requirements met?
- **Defect condition:** Auth user act considered w/out evidence co-borr/spouse owns it or borr paid last 12 mos & is in DTI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 944
- **Severity:** Critical
- **Rationale:** Needs a 12-month third-party-payment history (contingent-liability co-obligor, cosigner, or authorized-user account owner) -- `urla_liabilities`/`tradelines` capture the liability itself but not who else has been paying it or for how long; no such payment-history document exists in this corpus.
- **SME:** [ ] agree [ ] correct: ______

### G243 — O-FRD-50415 [O-FRD]
- **Q:** Were all manual underwriting credit assessment requirements met?
- **Defect condition:** Non-traditional credit used, completion homeownership education not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 933
- **Severity:** Critical
- **Rationale:** Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- **SME:** [ ] agree [ ] correct: ______

### G244 — O-FRD-00670 [O-FRD]
- **Q:** Were all manual underwriting credit assessment requirements met?
- **Defect condition:** The UW did not used the FICO scores with accompanying reason codes
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 931
- **Severity:** Critical
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **SME:** [ ] agree [ ] correct: ______

### G245 — O-FRD-00673 [O-FRD]
- **Q:** Were all manual underwriting credit assessment requirements met?
- **Defect condition:** The UW used factors reflected in the FICO score to offset the weaknesses in credit reputation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 924
- **Severity:** Critical
- **Rationale:** Deepen `credit_report` FIELD_SPECS: the doc's own text already shows 'Middle Score — Borrower 742' / 'Middle Score — Co-Borrower 758' (loan 01) but no score field is parsed today. Even once parsed, applying these rules needs a per-program minimum-score / representative-score-selection table that is a Selling-Guide business rule, not a fact derivable from any loan document -- Bucket-B on the extraction side, still needs an SME-sourced threshold table beyond that.
- **SME:** [ ] agree [ ] correct: ______

### G248 — O-FHA-02225 [O-FHA]
- **Q:** Were all manually underwritten bankruptcy requirements met?
- **Defect condition:** Where a bankruptcy is reported but is not documented that credit has been re-established
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 920
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G252 — O-FHA-50012 [O-FHA]
- **Q:** Were all manually underwritten consumer credit counseling program requirements met?
- **Defect condition:** Satisfactory payment history/counseling agency approval missing for credit counseling participants
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 925
- **Severity:** Critical
- **Rationale:** Consumer credit counseling program enrollment/payout/agency-approval document -- not a doc type in this corpus.
- **SME:** [ ] agree [ ] correct: ______

### G253 — O-FHA-50692 [O-FHA]
- **Q:** Were all manually underwritten debt and liability evaluation requirements met?
- **Defect condition:** Debt excluded, will not payoff in 10 mos or cumulative pymts exceed 5% of gross monthly income
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 864
- **Severity:** Critical
- **Rationale:** The percentage-of-balance math (5%/1.5%/0.5% thresholds) is crisp arithmetic once the relevant balance is in hand, and `extract_tradelines()` already captures type/balance/monthly_payment per tradeline -- but confirming whether the LENDER actually included the computed amount in the final DTI needs a DTI worksheet this pilot doesn't derive (same gap as F_PITIA_DTI_REO); and month-by-month late-payment-in-12-months detection needs payment-history depth the tradeline snapshot (a single current 'Status' value) doesn't carry. Trigger data partly in hand; verification math not yet built.
- **SME:** [ ] agree [ ] correct: ______

### G254 — O-FHA-50013 [O-FHA]
- **Q:** Were all manually underwritten debt and liability evaluation requirements met?
- **Defect condition:** Determination of new debt from inquiries reported within 90-days of closing is not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 927
- **Severity:** Critical
- **Rationale:** Needs a parsed Inquiries table (already visible in the loan 01 credit report's text -- 'Inquiries (last 120 days)' with Date/Bureau/Requesting Party -- but not yet in FIELD_SPECS/entities) cross-referenced against whether new debt was opened; Bucket-B-style (deepen extraction of a section already present in the one document we have), not a missing document.
- **SME:** [ ] agree [ ] correct: ______

### G256 — O-FHA-02234 [O-FHA]
- **Q:** Were all manually underwritten debt and liability evaluation requirements met?
- **Defect condition:** Undisclosed debt discovered and the actual payment amount was not verified and included in DTI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 948
- **Severity:** Critical
- **Rationale:** Closest textual match to the already-mapped (but zero-exception-code) `UndisclosedLiabilityShape` (credit-report tradeline with no matching 1003 Section 2c liability) -- verified NOT a safe direct wire (decision 019): this row bundles an additional requirement (borrower explanation obtained, and/or the payment verified and included in DTI) our shape doesn't test. Wiring it as-is would risk false negatives on loans where the undisclosed debt is present but the compound condition isn't met, or false positives once the explanation-documentation piece is added and our shape can't see it. Kept YELLOW pending that extra logic being built.
- **SME:** [ ] agree [ ] correct: ______

### G257 — O-FHA-02246 [O-FHA]
- **Q:** Were all manually underwritten disputed derogatory credit account requirements met?
- **Defect condition:** Disputed medical/derogatory credit was excluded without required supporting documentation
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 930
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G259 — O-FHA-02229 [O-FHA]
- **Q:** Were all manually underwritten foreclosure or deed-in-lieu of foreclosure requirements met?
- **Defect condition:** Loan approval does not evidence exception for foreclosure/deed-in-reported within 3 years
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 932
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G262 — O-FHA-02231 [O-FHA]
- **Q:** Were all manually underwritten housing obligation/mortgage payment requirements met?
- **Defect condition:** The housing payment history for the most recent 12 months was not determined and verified
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 934
- **Severity:** Critical
- **Rationale:** Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- **SME:** [ ] agree [ ] correct: ______

### G264 — O-FHA-02227 [O-FHA]
- **Q:** Were all manually underwritten pre-foreclosure sale (short sale) requirements met?
- **Defect condition:** Preforeclosure sale reported <3 years prior to FHA case number assignment; exception not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 943
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G265 — O-FHA-50691 [O-FHA]
- **Q:** Were all manually underwritten pre-foreclosure sale (short sale) requirements met?
- **Defect condition:** The borrower had a short sale in the last 3 yrs, documentation of an exception not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1026
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G266 — O-FHA-50011 [O-FHA]
- **Q:** Were all manually underwritten types of credit history requirements met?
- **Defect condition:** Credit report does not reflect creditor reporting status is w/in 90 days for accounts with balances
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 762
- **Severity:** Major
- **Rationale:** Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- **SME:** [ ] agree [ ] correct: ______

### G267 — O-FHA-02221 [O-FHA]
- **Q:** Were all manually underwritten types of credit history requirements met?
- **Defect condition:** Manual credit report did not meet all req's &/or did not show all req'd information for each borr
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 928
- **Severity:** Critical
- **Rationale:** Needs RMCR-specific compliance fields (repository count, per-account 'last updated' aging, original-vs-altered flag, identifying-info accuracy, public-records completeness) -- this pilot's `extract_tradelines()` captures only creditor/type/balance/monthly_payment/status; none of these format/compliance attributes are parsed, and the synthetic credit report's own text doesn't model them either.
- **SME:** [ ] agree [ ] correct: ______

### G268 — O-FHA-02222 [O-FHA]
- **Q:** Were all manually underwritten types of credit history requirements met?
- **Defect condition:** No credit score and non-traditional credit and/or verification of credit references is missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 939
- **Severity:** Critical
- **Rationale:** MISCLASSIFIED (matched 'did not meet' + 'credit report' keyword) -- same non-traditional-credit-report family as F_NONTRAD_VOR elsewhere in this block, not a bare presence check.
- **SME:** [ ] agree [ ] correct: ______

### G270 — O-FHA-50688 [O-FHA]
- **Q:** Were all manually underwritten types of payment histories requirements met?
- **Defect condition:** All housing/installment pmts not on time last 12 mths or had over 2 30 day late pmts in last 24 mths
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1054
- **Severity:** Critical
- **Rationale:** The percentage-of-balance math (5%/1.5%/0.5% thresholds) is crisp arithmetic once the relevant balance is in hand, and `extract_tradelines()` already captures type/balance/monthly_payment per tradeline -- but confirming whether the LENDER actually included the computed amount in the final DTI needs a DTI worksheet this pilot doesn't derive (same gap as F_PITIA_DTI_REO); and month-by-month late-payment-in-12-months detection needs payment-history depth the tradeline snapshot (a single current 'Status' value) doesn't carry. Trigger data partly in hand; verification math not yet built.
- **SME:** [ ] agree [ ] correct: ______

### G271 — O-FHA-50015 [O-FHA]
- **Q:** Were all manually underwritten types of payment histories requirements met?
- **Defect condition:** Documentation of significant late payments resulting from extenuating circumstances is missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 906
- **Severity:** Critical
- **Rationale:** MISCLASSIFIED (matched 'not adequately document' + 'credit report' keyword) -- the real condition needs an explanation-of-delinquency document establishing extenuating circumstances, a doc type this corpus doesn't have; presence of such a letter would be crisp once it exists, 'adequately' stays a partial human check.
- **SME:** [ ] agree [ ] correct: ______

### G273 — O-FHA-50689 [O-FHA]
- **Q:** Were all manually underwritten types of payment histories requirements met?
- **Defect condition:** The borrower had major derogatory credit on revolving accounts in the previous 12 months
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1053
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G275 — O-FNM-03139 [O-FNM]
- **Q:** Were all monthly debt obligations requirements met?
- **Defect condition:** A debt paid by someone other than the borrower was excluded without a 12 month timely pay history
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 840
- **Severity:** Critical
- **Rationale:** PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- **Guide candidate:** B3-6-05 — Monthly Debt Obligations (PDF p.522)
- **Guide candidate:** A2-1-01 — Contractual Obligations for Sellers/Servicers (PDF p.21)
- **Guide candidate:** A3-3-03 — Other Servicing Arrangements (PDF p.131)
- **SME:** [ ] agree [ ] correct: ______

### G276 — O-FNM-51834 [O-FNM]
- **Q:** Were all monthly debt obligations requirements met?
- **Defect condition:** AUS loan with alimony pymts reducing income in lieu of debt not in DU as own negative amt line item
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 771
- **Severity:** Major
- **Rationale:** Divorce decree / court order / separation agreement documenting alimony, child support, or maintenance payment terms -- not a doc type in this corpus.
- **Guide candidate:** B3-6-05 — Monthly Debt Obligations (PDF p.522)
- **Guide candidate:** B3-6-02 — Debt-to-Income Ratios (PDF p.514)
- **Guide candidate:** A2-1-01 — Contractual Obligations for Sellers/Servicers (PDF p.21)
- **SME:** [ ] agree [ ] correct: ______

### G277 — O-FNM-51833 [O-FNM]
- **Q:** Were all monthly debt obligations requirements met?
- **Defect condition:** Alimony, child support, or maintenance payments with over 10 months left was not considered in DTI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 773
- **Severity:** Critical
- **Rationale:** Divorce decree / court order / separation agreement documenting alimony, child support, or maintenance payment terms -- not a doc type in this corpus.
- **Guide candidate:** B3-3.4-02 — Alimony, Child Support, Equalization Payments, or Separate Maintenance (PDF p.352)
- **Guide candidate:** B3-6-05 — Monthly Debt Obligations (PDF p.522)
- **Guide candidate:** A2-1-01 — Contractual Obligations for Sellers/Servicers (PDF p.21)
- **SME:** [ ] agree [ ] correct: ______

### G278 — O-FNM-50017 [O-FNM]
- **Q:** Were all monthly debt obligations requirements met?
- **Defect condition:** Asset secured loan is not included in DTI or a copy of the Note reflecting the collateral is missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 915
- **Severity:** Critical
- **Rationale:** Needs a lease/HELOC/timeshare/solar-panel-agreement/virtual-currency-secured-loan document -- none of these niche liability-collateral document types exist in this corpus (same 'document family the synthetic corpus never modeled' pattern as several asset-verification YELLOW groups).
- **Guide candidate:** B3-6-05 — Monthly Debt Obligations (PDF p.522)
- **Guide candidate:** B3-4.3-15 — Borrowed Funds Secured by an Asset (PDF p.458)
- **Guide candidate:** B5-4.1-03 — Texas Section 50(a)(6) Loan Underwriting, Collateral, and Closing Considerations (PDF p.773)
- **SME:** [ ] agree [ ] correct: ______

### G279 — O-FNM-50006 [O-FNM]
- **Q:** Were all monthly debt obligations requirements met?
- **Defect condition:** Business debt(s) not included in DTI or documentation debt(s) is paid by the business is missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 784
- **Severity:** Critical
- **Rationale:** MISCLASSIFIED (matched 'not included'/'not documented' + 'credit report' keyword) -- the real condition is whether a business debt on the personal credit report is documented as company-paid and excluded from DTI accordingly. Needs a business-debt-payment documentation type this corpus doesn't have, plus DTI-inclusion logic not yet built.
- **Guide candidate:** B3-6-05 — Monthly Debt Obligations (PDF p.522)
- **Guide candidate:** A2-1-01 — Contractual Obligations for Sellers/Servicers (PDF p.21)
- **Guide candidate:** B3-2-04 — DU Documentation Requirements (PDF p.305)
- **SME:** [ ] agree [ ] correct: ______

### G280 — O-FNM-50009 [O-FNM]
- **Q:** Were all monthly debt obligations requirements met?
- **Defect condition:** Deferred non-student loan installment debt(s)/no payment is not documented and/or included in DTI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 842
- **Severity:** Critical
- **Rationale:** Mortgage forbearance/modification-plan document (terms, consecutive-payment count since granted) -- not a doc type in this corpus.
- **Guide candidate:** B3-6-05 — Monthly Debt Obligations (PDF p.522)
- **Guide candidate:** A2-1-01 — Contractual Obligations for Sellers/Servicers (PDF p.21)
- **Guide candidate:** A2-2-07 — Life-of-Loan Representations and Warranties (PDF p.48)
- **SME:** [ ] agree [ ] correct: ______

### G281 — O-FNM-50018 [O-FNM]
- **Q:** Were all monthly debt obligations requirements met?
- **Defect condition:** Deferred/forbearance student loan with no pymt reported & 1% of balance or documented pymt not used
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 841
- **Severity:** Critical
- **Rationale:** Mortgage forbearance/modification-plan document (terms, consecutive-payment count since granted) -- not a doc type in this corpus.
- **Guide candidate:** B3-6-05 — Monthly Debt Obligations (PDF p.522)
- **Guide candidate:** B5-1-01 — High-Balance Mortgage Loan Eligibility and Underwriting (PDF p.715)
- **Guide candidate:** A2-1-01 — Contractual Obligations for Sellers/Servicers (PDF p.21)
- **SME:** [ ] agree [ ] correct: ______

### G282 — O-FNM-50005 [O-FNM]
- **Q:** Were all monthly debt obligations requirements met?
- **Defect condition:** Divorce decree or equivalent not in file to document alimony, child support, or maintenance payments
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 772
- **Severity:** Critical
- **Rationale:** Divorce decree / court order / separation agreement documenting alimony, child support, or maintenance payment terms -- not a doc type in this corpus.
- **Guide candidate:** B3-3.4-02 — Alimony, Child Support, Equalization Payments, or Separate Maintenance (PDF p.352)
- **Guide candidate:** B3-6-05 — Monthly Debt Obligations (PDF p.522)
- **Guide candidate:** A2-1-01 — Contractual Obligations for Sellers/Servicers (PDF p.21)
- **SME:** [ ] agree [ ] correct: ______

### G283 — O-FNM-50016 [O-FNM]
- **Q:** Were all monthly debt obligations requirements met?
- **Defect condition:** Lease payment(s) excluded from total monthly debt, regardless of lease term remaining
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 909
- **Severity:** Critical
- **Rationale:** Needs a lease/HELOC/timeshare/solar-panel-agreement/virtual-currency-secured-loan document -- none of these niche liability-collateral document types exist in this corpus (same 'document family the synthetic corpus never modeled' pattern as several asset-verification YELLOW groups).
- **Guide candidate:** B3-6-05 — Monthly Debt Obligations (PDF p.522)
- **Guide candidate:** A2-1-01 — Contractual Obligations for Sellers/Servicers (PDF p.21)
- **Guide candidate:** B3-3.4-09 — Long-term Disability Income (PDF p.364)
- **SME:** [ ] agree [ ] correct: ______

### G284 — Paystub Loans [O-FNM]
- **Q:** Were all monthly debt obligations requirements met?
- **Defect condition:** Loans/deductions listed on the paystubs were not addressed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 911
- **Severity:** Critical
- **Rationale:** Verified against the actual synthetic paystub (loan 01, `03_Paystub_Most_Recent.pdf`): its Deductions section lists only standard tax withholdings (Federal Withholding, Social Security, Medicare, NC State Tax) -- no loan-type deduction or military allotment line appears in any paystub in this corpus. Genuine Bucket-A-style fixture gap (the paystub doc type exists; the specific line item this rule needs does not), not a Bucket-B extraction-deepening candidate -- there is nothing yet to extract.
- **Guide candidate:** B3-6-05 — Monthly Debt Obligations (PDF p.522)
- **Guide candidate:** A2-1-01 — Contractual Obligations for Sellers/Servicers (PDF p.21)
- **Guide candidate:** B2-1.4-01 — Fixed-Rate Loans (PDF p.206)
- **SME:** [ ] agree [ ] correct: ______

### G286 — Tax Liability [O-FNM]
- **Q:** Were all monthly debt obligations requirements met?
- **Defect condition:** There are federal income taxes due on the current year tax return and proof paid has not been obtain
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 879
- **Severity:** Critical
- **Rationale:** Current-year tax return + proof-of-payment documentation -- not a doc type in this corpus (identical condition text recurs across FHA/FRD/RHS/VA/FNM -- a single fixture gap, not five separate ones).
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-6-05 — Monthly Debt Obligations (PDF p.522)
- **Guide candidate:** B3-3.1-02 — Tax Return and Transcript Documentation Requirements (PDF p.320)
- **SME:** [ ] agree [ ] correct: ______

### G287 — O-FRD-53866 [O-FRD]
- **Q:** Were all monthly debt payment-to-income ratio liability evaluation requirements met?
- **Defect condition:** 1.5% of HELOC balance not used & monthly pymt amt not documented in the file or credit report
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 889, 5089
- **Severity:** Critical
- **Rationale:** Needs a lease/HELOC/timeshare/solar-panel-agreement/virtual-currency-secured-loan document -- none of these niche liability-collateral document types exist in this corpus (same 'document family the synthetic corpus never modeled' pattern as several asset-verification YELLOW groups).
- **SME:** [ ] agree [ ] correct: ______

### G288 — O-FRD-50017 [O-FRD]
- **Q:** Were all monthly debt payment-to-income ratio liability evaluation requirements met?
- **Defect condition:** 30 day account balance not added to DTI & funds to cover the account, closing/reserves not verified
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 756, 4952
- **Severity:** Critical
- **Rationale:** PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- **SME:** [ ] agree [ ] correct: ______

### G289 — O-FRD-50028 [O-FRD]
- **Q:** Were all monthly debt payment-to-income ratio liability evaluation requirements met?
- **Defect condition:** Asset secured loan is not included in DTI or a copy of the Note reflecting the collateral is missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 916, 5144
- **Severity:** Critical
- **Rationale:** Needs a lease/HELOC/timeshare/solar-panel-agreement/virtual-currency-secured-loan document -- none of these niche liability-collateral document types exist in this corpus (same 'document family the synthetic corpus never modeled' pattern as several asset-verification YELLOW groups).
- **SME:** [ ] agree [ ] correct: ______

### G290 — O-FRD-50019 [O-FRD]
- **Q:** Were all monthly debt payment-to-income ratio liability evaluation requirements met?
- **Defect condition:** Child support payments are not in DTI and required documentation is missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 774, 4964
- **Severity:** Critical
- **Rationale:** Divorce decree / court order / separation agreement documenting alimony, child support, or maintenance payment terms -- not a doc type in this corpus.
- **SME:** [ ] agree [ ] correct: ______

### G291 — O-FRD-50448 [O-FRD]
- **Q:** Were all monthly debt payment-to-income ratio liability evaluation requirements met?
- **Defect condition:** Current primary pending sale after Note date-executed sale contract missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1040, 5304
- **Severity:** Critical
- **Rationale:** Executed sales contract for a pending sale of the borrower's current residence -- not a doc type in this corpus; related to asset-verification's prior-home-sale settlement-statement family (G004/G005/G033).
- **SME:** [ ] agree [ ] correct: ______

### G292 — O-FRD-50027 [O-FRD]
- **Q:** Were all monthly debt payment-to-income ratio liability evaluation requirements met?
- **Defect condition:** Lease payment(s) excluded from total monthly debt, regardless of lease term remaining
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 910, 5123
- **Severity:** Critical
- **Rationale:** Needs a lease/HELOC/timeshare/solar-panel-agreement/virtual-currency-secured-loan document -- none of these niche liability-collateral document types exist in this corpus (same 'document family the synthetic corpus never modeled' pattern as several asset-verification YELLOW groups).
- **SME:** [ ] agree [ ] correct: ______

### G293 — O-FRD-55526 [O-FRD]
- **Q:** Were all monthly debt payment-to-income ratio liability evaluation requirements met?
- **Defect condition:** Monthly payments on debts secured by cryptocurrency was not included in the DTI ratio
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 837, 5016
- **Severity:** Critical
- **Rationale:** Needs a lease/HELOC/timeshare/solar-panel-agreement/virtual-currency-secured-loan document -- none of these niche liability-collateral document types exist in this corpus (same 'document family the synthetic corpus never modeled' pattern as several asset-verification YELLOW groups).
- **SME:** [ ] agree [ ] correct: ______

### G294 — O-FRD-50023 [O-FRD]
- **Q:** Were all monthly debt payment-to-income ratio liability evaluation requirements met?
- **Defect condition:** Non-Student/IRS installment debt not on credit report or in deferred/forbearance, missing pymt verif
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 894, 5110
- **Severity:** Critical
- **Rationale:** MISCLASSIFIED (matched 'not report' + 'credit report' keyword) -- needs a deferred/forbearance status flag per tradeline and a separate payment-verification document; `extract_tradelines()` doesn't model either today.
- **SME:** [ ] agree [ ] correct: ______

### G295 — O-FRD-50447 [O-FRD]
- **Q:** Were all monthly debt payment-to-income ratio liability evaluation requirements met?
- **Defect condition:** PITIA of other properties owned by the borrower were not included in DTI as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 989, 5218
- **Severity:** Critical
- **Rationale:** PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- **SME:** [ ] agree [ ] correct: ______

### G296 — O-FRD-53802 [O-FRD]
- **Q:** Were all monthly debt payment-to-income ratio liability evaluation requirements met?
- **Defect condition:** The loan file did not document all payments included in the monthly DTI as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 855, 5029
- **Severity:** Critical
- **Rationale:** PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- **SME:** [ ] agree [ ] correct: ______

### G298 — O-FRD-00514 [O-FRD]
- **Q:** Were all monthly housing expense-to-income ratio evaluation requirements met?
- **Defect condition:** Higher HTI ratio used for energy efficiency without the calculation & source offset being documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 860, 5049
- **Severity:** Critical
- **Rationale:** PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- **SME:** [ ] agree [ ] correct: ______

### G299 — O-FRD-53324 [O-FRD]
- **Q:** Were all monthly housing expense-to-income ratio evaluation requirements met?
- **Defect condition:** Monthly PITIA not calculated correctly &/or did not include all housing components
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 996, 5230
- **Severity:** Critical
- **Rationale:** PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- **SME:** [ ] agree [ ] correct: ______

### G300 — O-FRD-51771 [O-FRD]
- **Q:** Were all monthly housing expense-to-income ratio evaluation requirements met?
- **Defect condition:** PITI property tax amt was incorrect by transfer of ownership changing the amount or tax abatements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1011, 5254
- **Severity:** Critical
- **Rationale:** PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- **SME:** [ ] agree [ ] correct: ______

### G301 — O-FRD-51770 [O-FRD]
- **Q:** Were all monthly housing expense-to-income ratio evaluation requirements met?
- **Defect condition:** PITI real estate tax amount was not based on the value of improvements plus the value of the land
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1010, 5253
- **Severity:** Critical
- **Rationale:** PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- **SME:** [ ] agree [ ] correct: ______

### G302 — O-FRD-56577 [O-FRD]
- **Q:** Were all monthly housing expense-to-income ratio evaluation requirements met?
- **Defect condition:** Property taxes excluded from housing ratio & tax abatement documentation & continuance req's not met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1009, 5252
- **Severity:** Critical
- **Rationale:** PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- **SME:** [ ] agree [ ] correct: ______

### G303 — O-FRD-58103 [O-FRD]
- **Q:** Were all monthly housing expense-to-income ratio evaluation requirements met?
- **Defect condition:** Special assessments w/ more than 10 mos payments remaining not included in monthly housing expense
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1031, 5293
- **Severity:** Major
- **Rationale:** PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- **SME:** [ ] agree [ ] correct: ______

### G304 — O-FRD-53801 [O-FRD]
- **Q:** Were all monthly housing expense-to-income ratio evaluation requirements met?
- **Defect condition:** Subject 2nd or investment & borr rents current residence, rent not documented &/or in housing ratio
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1016, 5261
- **Severity:** Critical
- **Rationale:** PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- **SME:** [ ] agree [ ] correct: ______

### G305 — O-FRD-56578 [O-FRD]
- **Q:** Were all monthly housing expense-to-income ratio evaluation requirements met?
- **Defect condition:** Tax exemption related to disability/age have a predetermined exp date within 5 yrs of the Note date
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1012, 5255
- **Severity:** Critical
- **Rationale:** PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- **SME:** [ ] agree [ ] correct: ______

### G307 — O-FNM-51043 [O-FNM]
- **Q:** Were all monthly housing requirements met?
- **Defect condition:** Monthly PITIA not calculated correctly &/or did not include all housing components
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 995
- **Severity:** Critical
- **Rationale:** PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- **Guide candidate:** B3-6-03 — Monthly Housing Expense for the Subject Property (PDF p.518)
- **Guide candidate:** B2-2-06 — Homeownership Education and Housing Counseling (PDF p.253)
- **Guide candidate:** B2-3-02 — Special Property Eligibility and Underwriting Considerations: Factory-Built Housing (PDF p.261)
- **SME:** [ ] agree [ ] correct: ______

### G309 — O-FNM-56073 [O-FNM]
- **Q:** Were all monthly housing requirements met?
- **Defect condition:** PITIA of other properties owned by the borrower were not included in DTI as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 988
- **Severity:** Critical
- **Rationale:** PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- **Guide candidate:** B2-2-03 — Multiple Financed Properties for the Same Borrower (PDF p.244)
- **Guide candidate:** B3-6-03 — Monthly Housing Expense for the Subject Property (PDF p.518)
- **Guide candidate:** B3-6-06 — Qualifying Impact of Other Real Estate Owned (PDF p.529)
- **SME:** [ ] agree [ ] correct: ______

### G310 — O-FNM-55880 [O-FNM]
- **Q:** Were all monthly housing requirements met?
- **Defect condition:** Subject 2nd or investment & borr rents current residence, rent not documented &/or in housing ratio
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1015
- **Severity:** Critical
- **Rationale:** PITIA/DTI/housing-ratio computation from components already partly extracted (base_monthly_income_1003, urla_liabilities) is not yet derived anywhere in extract_loan.py (only loan 05's USDA ratio-waiver doc supplies a directly-extracted dti_ratio/piti_ratio, for that one program); other-REO-property PITIA needs a financed-properties/REO schedule this pilot doesn't parse from the 1003 at all -- same gap asset-verification's triage flagged (G240/G241, no REO-schedule entity).
- **Guide candidate:** B3-6-03 — Monthly Housing Expense for the Subject Property (PDF p.518)
- **Guide candidate:** B2-2-04 — Guarantors, Co-Signers, or Non-Occupant Borrowers on the Subject Transaction (PDF p.248)
- **Guide candidate:** B2-2-06 — Homeownership Education and Housing Counseling (PDF p.253)
- **SME:** [ ] agree [ ] correct: ______

### G311 — O-FHA-58953 [O-FHA]
- **Q:** Were all non-borrowing spouse debt requirements met?
- **Defect condition:** A credit report was not obtained for the non-borrowing spouse in a community property state
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 802
- **Severity:** Critical
- **Rationale:** A second credit report (the non-borrowing/non-purchasing spouse's) plus the applicable state's community-property statute reference -- neither exists in this corpus; every loan extracts exactly one applicant-side credit report at most.
- **SME:** [ ] agree [ ] correct: ______

### G312 — O-FHA-58785 [O-FHA]
- **Q:** Were all non-borrowing spouse debt requirements met?
- **Defect condition:** Comm property state non-borr spouse debts excluded without specific state law justifying exclusion
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 800
- **Severity:** Critical
- **Rationale:** A second credit report (the non-borrowing/non-purchasing spouse's) plus the applicable state's community-property statute reference -- neither exists in this corpus; every loan extracts exactly one applicant-side credit report at most.
- **SME:** [ ] agree [ ] correct: ______

### G313 — O-FHA-02237 [O-FHA]
- **Q:** Were all non-borrowing spouse debt requirements met?
- **Defect condition:** Non-borrowing spouse debts not included in DTI in community property state not excluded by state law
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 801
- **Severity:** Critical
- **Rationale:** A second credit report (the non-borrowing/non-purchasing spouse's) plus the applicable state's community-property statute reference -- neither exists in this corpus; every loan extracts exactly one applicant-side credit report at most.
- **SME:** [ ] agree [ ] correct: ______

### G315 — O-RHS-02790 [O-RHS]
- **Q:** Were all non-traditional credit report and credit history requirements met?_x000D_
- **Defect condition:** No credit score & a non-traditional credit report &/or non-traditional credit history not developed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 976
- **Severity:** Critical
- **Rationale:** Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- **SME:** [ ] agree [ ] correct: ______

### G316 — O-RHS-57770 [O-RHS]
- **Q:** Were all non-traditional credit report and credit history requirements met?_x000D_
- **Defect condition:** Non-traditional credit was used with no rent history, 3 eligible tradelines were not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 981
- **Severity:** Major
- **Rationale:** Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- **SME:** [ ] agree [ ] correct: ______

### G317 — O-RHS-57769 [O-RHS]
- **Q:** Were all non-traditional credit report and credit history requirements met?_x000D_
- **Defect condition:** Nontraditional credit w/ rent history, a VOR & 1 more recent tradeline w/12 mos history not in file
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 982
- **Severity:** Major
- **Rationale:** Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- **SME:** [ ] agree [ ] correct: ______

### G319 — O-FNM-57520 [O-FNM]
- **Q:** Were all nontraditional credit history requirements met?
- **Defect condition:** 12 mos reserves not verified where nontraditional credit was used for borr's w/out a housing history
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 983
- **Severity:** Critical
- **Rationale:** Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- **Guide candidate:** B3-5.4-03 — Documentation and Assessment of a Nontraditional Credit History (PDF p.509)
- **Guide candidate:** B3-5.4-01 — Eligibility Requirements for Loans with Nontraditional Credit (PDF p.504)
- **Guide candidate:** B3-5.4-02 — Number and Types of Nontraditional Credit References (PDF p.506)
- **SME:** [ ] agree [ ] correct: ______

### G320 — O-FNM-57519 [O-FNM]
- **Q:** Were all nontraditional credit history requirements met?
- **Defect condition:** An unacceptable source was used to verify the nontraditional housing payments
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1044
- **Severity:** Critical
- **Rationale:** Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- **Guide candidate:** B3-5.4-03 — Documentation and Assessment of a Nontraditional Credit History (PDF p.509)
- **Guide candidate:** B3-3.4-14 — Section 8 Housing Choice Voucher Homeownership Program Payments (PDF p.370)
- **Guide candidate:** B3-5.4-01 — Eligibility Requirements for Loans with Nontraditional Credit (PDF p.504)
- **SME:** [ ] agree [ ] correct: ______

### G321 — O-FNM-58788 [O-FNM]
- **Q:** Were all nontraditional credit history requirements met?
- **Defect condition:** Borr w/ credit score had 50% or less qual income & no non-trad credit for borr w/out a credit score
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 783
- **Severity:** Critical
- **Rationale:** Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- **Guide candidate:** B3-5.4-03 — Documentation and Assessment of a Nontraditional Credit History (PDF p.509)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-5.1-02 — Determining the Credit Score for a Mortgage Loan (PDF p.474)
- **SME:** [ ] agree [ ] correct: ______

### G322 — O-FNM-58787 [O-FNM]
- **Q:** Were all nontraditional credit history requirements met?
- **Defect condition:** Non-purchase/LCO of 1-4 unit, all bwrs occupy: No bwr had DU credit score or 1 credit/install acct
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 858
- **Severity:** Critical
- **Rationale:** Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- **Guide candidate:** B3-5.4-03 — Documentation and Assessment of a Nontraditional Credit History (PDF p.509)
- **Guide candidate:** B3-5.1-02 — Determining the Credit Score for a Mortgage Loan (PDF p.474)
- **Guide candidate:** B3-5.4-01 — Eligibility Requirements for Loans with Nontraditional Credit (PDF p.504)
- **SME:** [ ] agree [ ] correct: ______

### G323 — O-FNM-56149 [O-FNM]
- **Q:** Were all nontraditional credit history requirements met?
- **Defect condition:** Nontraditional credit used & loan was not a fixed rate meeting conforming baseline loan limits
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 977
- **Severity:** Critical
- **Rationale:** Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- **Guide candidate:** B3-5.4-03 — Documentation and Assessment of a Nontraditional Credit History (PDF p.509)
- **Guide candidate:** B2-1.4-01 — Fixed-Rate Loans (PDF p.206)
- **Guide candidate:** B2-1.5-01 — Loan Limits (PDF p.224)
- **SME:** [ ] agree [ ] correct: ______

### G324 — O-FNM-56147 [O-FNM]
- **Q:** Were all nontraditional credit history requirements met?
- **Defect condition:** Nontraditional credit was used for a subject property that is not a 1-4 unit principal residence
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 978
- **Severity:** Critical
- **Rationale:** Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- **Guide candidate:** B3-5.4-03 — Documentation and Assessment of a Nontraditional Credit History (PDF p.509)
- **Guide candidate:** B3-5.4-01 — Eligibility Requirements for Loans with Nontraditional Credit (PDF p.504)
- **Guide candidate:** B3-5.4-02 — Number and Types of Nontraditional Credit References (PDF p.506)
- **SME:** [ ] agree [ ] correct: ______

### G325 — O-FNM-56148 [O-FNM]
- **Q:** Were all nontraditional credit history requirements met?
- **Defect condition:** Nontraditional credit was used in a transaction other than a purchase or limited cash-out refinance
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 980
- **Severity:** Critical
- **Rationale:** Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- **Guide candidate:** B2-1.3-02 — Limited Cash-Out Reﬁnance Transactions (PDF p.192)
- **Guide candidate:** B3-5.4-03 — Documentation and Assessment of a Nontraditional Credit History (PDF p.509)
- **Guide candidate:** B5-4.2-02 — Disaster-Related Limited Cash-Out Reﬁnance Flexibilities (PDF p.778)
- **SME:** [ ] agree [ ] correct: ______

### G326 — O-FNM-56150 [O-FNM]
- **Q:** Were all nontraditional credit history requirements met?
- **Defect condition:** Nontraditional references not verified without DU allowing a 3rd party asset verification report
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1055
- **Severity:** Critical
- **Rationale:** Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- **Guide candidate:** B3-5.4-02 — Number and Types of Nontraditional Credit References (PDF p.506)
- **Guide candidate:** B3-5.4-03 — Documentation and Assessment of a Nontraditional Credit History (PDF p.509)
- **Guide candidate:** B3-2-09 — Erroneous Credit Report Data (PDF p.311)
- **SME:** [ ] agree [ ] correct: ______

### G328 — O-FNM-50269 [O-FNM]
- **Q:** Were all nontraditional credit history requirements met?
- **Defect condition:** The number of non-traditional accts insufficient or from an ineligible source
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 984
- **Severity:** Critical
- **Rationale:** Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- **Guide candidate:** B3-5.4-02 — Number and Types of Nontraditional Credit References (PDF p.506)
- **Guide candidate:** B3-5.4-03 — Documentation and Assessment of a Nontraditional Credit History (PDF p.509)
- **Guide candidate:** B3-5.4-01 — Eligibility Requirements for Loans with Nontraditional Credit (PDF p.504)
- **SME:** [ ] agree [ ] correct: ______

### G329 — O-FHA-02244 [O-FHA]
- **Q:** Were all other liabilities requirements met?
- **Defect condition:** Contingent liability without evidence another obligor has made payments for the last 12 months
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 803
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G330 — O-FHA-50017 [O-FHA]
- **Q:** Were all other liabilities requirements met?
- **Defect condition:** Contributions to private or pooled savings accounts are not included in the DTI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1006
- **Severity:** Critical
- **Rationale:** Pooled/private-savings-plan agreement -- same document family asset-verification's triage flagged as absent from this corpus (G196/G209 there).
- **SME:** [ ] agree [ ] correct: ______

### G332 — O-FHA-02245 [O-FHA]
- **Q:** Were all other liabilities requirements met?
- **Defect condition:** Outstanding collection account and 5% of the balance/amount on a payment agreement excluded from DTI
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 795
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **SME:** [ ] agree [ ] correct: ______

### G333 — O-FNM-00194 [O-FNM]
- **Q:** Were all other monthly debt obligations requirements met?
- **Defect condition:** Debts noted as “will rate by mail only” or “need written authorization” were not verified separately
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1024
- **Severity:** Critical
- **Rationale:** 'Will rate by mail only'/'need written authorization' accounts need a separate written-verification document per account -- not a doc type this corpus models (the one credit report's tradelines don't carry a rate-by-mail flag either).
- **Guide candidate:** B3-6-05 — Monthly Debt Obligations (PDF p.522)
- **Guide candidate:** A2-1-01 — Contractual Obligations for Sellers/Servicers (PDF p.21)
- **Guide candidate:** A3-3-03 — Other Servicing Arrangements (PDF p.131)
- **SME:** [ ] agree [ ] correct: ______

### G334 — O-FNM-55676 [O-FNM]
- **Q:** Were all other monthly debt obligations requirements met?
- **Defect condition:** Monthly payments on debts secured by virtual currency were not included in the DTI ratio
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1062
- **Severity:** Critical
- **Rationale:** Needs a lease/HELOC/timeshare/solar-panel-agreement/virtual-currency-secured-loan document -- none of these niche liability-collateral document types exist in this corpus (same 'document family the synthetic corpus never modeled' pattern as several asset-verification YELLOW groups).
- **Guide candidate:** B3-6-05 — Monthly Debt Obligations (PDF p.522)
- **Guide candidate:** B3-4.1-04 — Virtual Currency (PDF p.429)
- **Guide candidate:** A2-1-01 — Contractual Obligations for Sellers/Servicers (PDF p.21)
- **SME:** [ ] agree [ ] correct: ______

### G335 — O-FNM-00191 [O-FNM]
- **Q:** Were all other monthly debt obligations requirements met?
- **Defect condition:** No written verification for significant open debt(s) on the application but not on the credit report
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 833
- **Severity:** Critical
- **Rationale:** The REVERSE direction of `UndisclosedLiabilityShape`'s condition (that shape flags a credit-report tradeline missing from the 1003; this row flags a 1003 liability missing from the credit report) -- needs a separate written-verification document per unreported debt that isn't modeled in this corpus. Noted as textually adjacent to, but NOT the same real-world check as, the mapped shape -- do not conflate the two directions when this is eventually built.
- **Guide candidate:** B3-6-05 — Monthly Debt Obligations (PDF p.522)
- **Guide candidate:** B3-2-09 — Erroneous Credit Report Data (PDF p.311)
- **Guide candidate:** B3-2-10 — Accuracy of DU Data, DU Tolerances, and Errors in the Credit Report (PDF p.313)
- **SME:** [ ] agree [ ] correct: ______

### G337 — O-FNM-57257 [O-FNM]
- **Q:** Were all other monthly debt obligations requirements met?
- **Defect condition:** Student loan payment not on credit report and the monthly payment was not determined as required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1039
- **Severity:** Critical
- **Rationale:** Student-loan payment-substitution math (0.5%/1% of balance when the credit report shows a $0 or missing payment) is crisp arithmetic, and `extract_tradelines()` already captures tradeline type/balance/monthly_payment (loan 01 has one Student tradeline) -- but verifying which qualifying-payment value the lender ACTUALLY used needs a DTI/qualifying-payment worksheet this pilot doesn't extract or derive from any document today. Trigger-detection is Bucket-B-close; the verification half is not.
- **Guide candidate:** B3-6-05 — Monthly Debt Obligations (PDF p.522)
- **Guide candidate:** B3-2-09 — Erroneous Credit Report Data (PDF p.311)
- **Guide candidate:** B3-2-10 — Accuracy of DU Data, DU Tolerances, and Errors in the Credit Report (PDF p.313)
- **SME:** [ ] agree [ ] correct: ______

### G338 — O-FHA-55986 [O-FHA]
- **Q:** Were all positive rental payment history requirements met?
- **Defect condition:** Family rental - no signed lease & 12 mos cashed checks or bank stmts for positive rent pay history
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 870
- **Severity:** Critical
- **Rationale:** Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- **SME:** [ ] agree [ ] correct: ______

### G340 — O-FHA-55985 [O-FHA]
- **Q:** Were all positive rental payment history requirements met?
- **Defect condition:** Positive rent pay history - no signed lease & VOR, 12 mos checks/bank stmts, or landlord reference
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 998
- **Severity:** Critical
- **Rationale:** Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- **SME:** [ ] agree [ ] correct: ______

### G341 — O-FHA-55983 [O-FHA]
- **Q:** Were all positive rental payment history requirements met?
- **Defect condition:** Positive rental history used & borr is not a 1st time homebuyer in a purchase w/ MDCS of 620 or more
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 999
- **Severity:** Critical
- **Rationale:** Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- **SME:** [ ] agree [ ] correct: ______

### G342 — O-FHA-55984 [O-FHA]
- **Q:** Were all positive rental payment history requirements met?
- **Defect condition:** Positive rental payment history monthly payments of $300 or more for last 12 months not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 997
- **Severity:** Critical
- **Rationale:** Non-traditional credit report / Verification of Rent (VOR) / noncredit payment reference documentation -- no such doc type exists in this corpus; every loan's housing-payment history today comes only from the VOM (loan 04, mortgage-specific, not rental) or the one credit report's tradelines (loan 01).
- **SME:** [ ] agree [ ] correct: ______

### G344 — O-FHA-02226 [O-FHA]
- **Q:** Were all pre-foreclosure (short sale) requirements met?
- **Defect condition:** Preforeclosure sale reported <3 years prior to FHA case number assignment
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1000
- **Severity:** Critical
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **SME:** [ ] agree [ ] correct: ______

### G345 — O-FHA-53798 [O-FHA]
- **Q:** Were all requirements met where a previous mortgage forbearance was granted on the subject property or other residence?
- **Defect condition:** Case not downgraded to refer in a refi where borr did not make mtg forbearance pymts as agreed
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 787
- **Severity:** Critical
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **SME:** [ ] agree [ ] correct: ______

### G346 — O-FHA-53794 [O-FHA]
- **Q:** Were all requirements met where a previous mortgage forbearance was granted on the subject property or other residence?
- **Defect condition:** Forbearance plan inc & less than 3 consec pymts not made since as req'd for a credit qual streamline
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 818
- **Severity:** Critical
- **Rationale:** Mortgage forbearance/modification-plan document (terms, consecutive-payment count since granted) -- not a doc type in this corpus.
- **SME:** [ ] agree [ ] correct: ______

### G347 — O-FHA-53791 [O-FHA]
- **Q:** Were all requirements met where a previous mortgage forbearance was granted on the subject property or other residence?
- **Defect condition:** Forbearance plan not complete & 12 consecutive pymts not made since as req'd for CO refi
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 789
- **Severity:** Critical
- **Rationale:** Mortgage forbearance/modification-plan document (terms, consecutive-payment count since granted) -- not a doc type in this corpus.
- **SME:** [ ] agree [ ] correct: ______

### G348 — O-FHA-53793 [O-FHA]
- **Q:** Were all requirements met where a previous mortgage forbearance was granted on the subject property or other residence?
- **Defect condition:** Forbearance plan not complete & 3 consecutive pymts not made since as req'd for a no cash-out refi
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 971
- **Severity:** Critical
- **Rationale:** Mortgage forbearance/modification-plan document (terms, consecutive-payment count since granted) -- not a doc type in this corpus.
- **SME:** [ ] agree [ ] correct: ______

### G349 — O-FHA-53792 [O-FHA]
- **Q:** Were all requirements met where a previous mortgage forbearance was granted on the subject property or other residence?
- **Defect condition:** Forbearance plan not complete & 3 consecutive pymts not made since as req'd for a purchase
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1008
- **Severity:** Critical
- **Rationale:** Mortgage forbearance/modification-plan document (terms, consecutive-payment count since granted) -- not a doc type in this corpus.
- **SME:** [ ] agree [ ] correct: ______

### G350 — O-FHA-53797 [O-FHA]
- **Q:** Were all requirements met where a previous mortgage forbearance was granted on the subject property or other residence?
- **Defect condition:** Mtg forbearance will remain open after closing & the plan was not terminated prior to or at closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 985
- **Severity:** Critical
- **Rationale:** Mortgage forbearance/modification-plan document (terms, consecutive-payment count since granted) -- not a doc type in this corpus.
- **SME:** [ ] agree [ ] correct: ______

### G352 — O-FHA-53799 [O-FHA]
- **Q:** Were all requirements met where a previous mortgage forbearance was granted on the subject property or other residence?
- **Defect condition:** Refi w/ a mod/forbearance  w/in 12 mos without a copy of the mod/forbearance plan with terms
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 788
- **Severity:** Critical
- **Rationale:** Mortgage forbearance/modification-plan document (terms, consecutive-payment count since granted) -- not a doc type in this corpus.
- **SME:** [ ] agree [ ] correct: ______

### G353 — O-FHA-53795 [O-FHA]
- **Q:** Were all requirements met where a previous mortgage forbearance was granted on the subject property or other residence?
- **Defect condition:** The borrower did not make at least 6 payments after forbearance modification as req'd for str refi
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1033
- **Severity:** Critical
- **Rationale:** Mortgage forbearance/modification-plan document (terms, consecutive-payment count since granted) -- not a doc type in this corpus.
- **SME:** [ ] agree [ ] correct: ______

### G354 — O-FHA-53796 [O-FHA]
- **Q:** Were all requirements met where a previous mortgage forbearance was granted on the subject property or other residence?
- **Defect condition:** The pay history during the forbearance plan was not utilized in determining late housing payments
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 874
- **Severity:** Critical
- **Rationale:** Mortgage forbearance/modification-plan document (terms, consecutive-payment count since granted) -- not a doc type in this corpus.
- **SME:** [ ] agree [ ] correct: ______

### G356 — O-FHA-02240 [O-FHA]
- **Q:** Were all revolving charge account requirements met?
- **Defect condition:** Not all payments for revolving charge accounts were included to calculate the borrower’s debts
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1018
- **Severity:** Critical
- **Rationale:** The percentage-of-balance math (5%/1.5%/0.5% thresholds) is crisp arithmetic once the relevant balance is in hand, and `extract_tradelines()` already captures type/balance/monthly_payment per tradeline -- but confirming whether the LENDER actually included the computed amount in the final DTI needs a DTI worksheet this pilot doesn't derive (same gap as F_PITIA_DTI_REO); and month-by-month late-payment-in-12-months detection needs payment-history depth the tradeline snapshot (a single current 'Status' value) doesn't carry. Trigger data partly in hand; verification math not yet built.
- **SME:** [ ] agree [ ] correct: ______

### G357 — O-FRD-50881 [O-FRD]
- **Q:** Were all student loan evaluation requirements met?
- **Defect condition:** A student loan was excluded from the monthly DTI ratio without all requirements being met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 868
- **Severity:** Critical
- **Rationale:** Student-loan payment-substitution math (0.5%/1% of balance when the credit report shows a $0 or missing payment) is crisp arithmetic, and `extract_tradelines()` already captures tradeline type/balance/monthly_payment (loan 01 has one Student tradeline) -- but verifying which qualifying-payment value the lender ACTUALLY used needs a DTI/qualifying-payment worksheet this pilot doesn't extract or derive from any document today. Trigger-detection is Bucket-B-close; the verification half is not.
- **SME:** [ ] agree [ ] correct: ______

### G358 — O-FRD-50986 [O-FRD]
- **Q:** Were all student loan evaluation requirements met?
- **Defect condition:** Credit report pymt (not $0) or 0.5% of the student loan bal in repymt/deferment/forbearance not used
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1036
- **Severity:** Critical
- **Rationale:** Mortgage forbearance/modification-plan document (terms, consecutive-payment count since granted) -- not a doc type in this corpus.
- **SME:** [ ] agree [ ] correct: ______

### G359 — O-FRD-52174 [O-FRD]
- **Q:** Were all student loan evaluation requirements met?
- **Defect condition:** Excluded student loan w/out source documentation loan is approved to not be repaid as applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 867
- **Severity:** Critical
- **Rationale:** Student-loan payment-substitution math (0.5%/1% of balance when the credit report shows a $0 or missing payment) is crisp arithmetic, and `extract_tradelines()` already captures tradeline type/balance/monthly_payment (loan 01 has one Student tradeline) -- but verifying which qualifying-payment value the lender ACTUALLY used needs a DTI/qualifying-payment worksheet this pilot doesn't extract or derive from any document today. Trigger-detection is Bucket-B-close; the verification half is not.
- **SME:** [ ] agree [ ] correct: ______

### G361 — O-FHA-54669 [O-FHA]
- **Q:** Were all student loan liabilities requirements met?
- **Defect condition:** 0.5% of the outstanding student loan balance not used as the pymt where the credit report pymt is 0
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 832
- **Severity:** Critical
- **Rationale:** Student-loan payment-substitution math (0.5%/1% of balance when the credit report shows a $0 or missing payment) is crisp arithmetic, and `extract_tradelines()` already captures tradeline type/balance/monthly_payment (loan 01 has one Student tradeline) -- but verifying which qualifying-payment value the lender ACTUALLY used needs a DTI/qualifying-payment worksheet this pilot doesn't extract or derive from any document today. Trigger-detection is Bucket-B-close; the verification half is not.
- **SME:** [ ] agree [ ] correct: ______

### G362 — O-FHA-50672 [O-FHA]
- **Q:** Were all student loan liabilities requirements met?
- **Defect condition:** An outstanding student loan debt was not included regardless of payment type or status of payments
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1035
- **Severity:** Critical
- **Rationale:** Student-loan payment-substitution math (0.5%/1% of balance when the credit report shows a $0 or missing payment) is crisp arithmetic, and `extract_tradelines()` already captures tradeline type/balance/monthly_payment (loan 01 has one Student tradeline) -- but verifying which qualifying-payment value the lender ACTUALLY used needs a DTI/qualifying-payment worksheet this pilot doesn't extract or derive from any document today. Trigger-detection is Bucket-B-close; the verification half is not.
- **SME:** [ ] agree [ ] correct: ______

### G364 — O-FHA-54667 [O-FHA]
- **Q:** Were all student loan liabilities requirements met?
- **Defect condition:** Student debt excluded w/out documenting the loan balance was forgiven, canceled, discharged, or PIF
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 866
- **Severity:** Critical
- **Rationale:** Student-loan payment-substitution math (0.5%/1% of balance when the credit report shows a $0 or missing payment) is crisp arithmetic, and `extract_tradelines()` already captures tradeline type/balance/monthly_payment (loan 01 has one Student tradeline) -- but verifying which qualifying-payment value the lender ACTUALLY used needs a DTI/qualifying-payment worksheet this pilot doesn't extract or derive from any document today. Trigger-detection is Bucket-B-close; the verification half is not.
- **SME:** [ ] agree [ ] correct: ______

### G365 — O-FHA-02625 [O-FHA]
- **Q:** Were all student loan liabilities requirements met?
- **Defect condition:** Student loan monthly payment, payment status, &/or the outstanding balance/terms not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1038
- **Severity:** Critical
- **Rationale:** Student-loan payment-substitution math (0.5%/1% of balance when the credit report shows a $0 or missing payment) is crisp arithmetic, and `extract_tradelines()` already captures tradeline type/balance/monthly_payment (loan 01 has one Student tradeline) -- but verifying which qualifying-payment value the lender ACTUALLY used needs a DTI/qualifying-payment worksheet this pilot doesn't extract or derive from any document today. Trigger-detection is Bucket-B-close; the verification half is not.
- **SME:** [ ] agree [ ] correct: ______

### G368 — O-FNM-50267 [O-FNM]
- **Q:** Were all traditional credit history requirements met?
- **Defect condition:** Authorized user accts included without evidence borrower solely paid for last 12 mos in manual UW
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 945
- **Severity:** Critical
- **Rationale:** Needs a 12-month third-party-payment history (contingent-liability co-obligor, cosigner, or authorized-user account owner) -- `urla_liabilities`/`tradelines` capture the liability itself but not who else has been paying it or for how long; no such payment-history document exists in this corpus.
- **Guide candidate:** B3-5.3-06 — Authorized Users of Credit (PDF p.488)
- **Guide candidate:** B3-5.4-03 — Documentation and Assessment of a Nontraditional Credit History (PDF p.509)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G369 — O-FNM-00188 [O-FNM]
- **Q:** Were all traditional credit history requirements met?
- **Defect condition:** Determination of new debt from inquiries reported within 90-days of closing is not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 812
- **Severity:** Critical
- **Rationale:** Needs a parsed Inquiries table (already visible in the loan 01 credit report's text -- 'Inquiries (last 120 days)' with Date/Bureau/Requesting Party -- but not yet in FIELD_SPECS/entities) cross-referenced against whether new debt was opened; Bucket-B-style (deepen extraction of a section already present in the one document we have), not a missing document.
- **Guide candidate:** B3-5.3-04 — Inquiries: Recent Attempts to Obtain New Credit (PDF p.486)
- **Guide candidate:** B3-5.4-03 — Documentation and Assessment of a Nontraditional Credit History (PDF p.509)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G370 — O-FNM-50015 [O-FNM]
- **Q:** Were all traditional credit history requirements met?
- **Defect condition:** Late rental and/or mortgage payment reported/verified does not meet guidelines
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 904
- **Severity:** Critical
- **Rationale:** 'Does not meet guidelines' bundles a specific late-payment-count/severity threshold (defined per agency Selling Guide, not stated in the row itself) with the housing-payment-history depth this pilot's VOM only captures for one mortgage on one loan (loan 04) -- needs both a guide-sourced threshold and broader payment-history extraction; genuinely blocked on both counts, not a rule-clarity problem.
- **Guide candidate:** B3-5.3-03 — Previous Mortgage Payment History (PDF p.485)
- **Guide candidate:** B3-3.4-10 — Mortgage Credit Certiﬁcates (PDF p.366)
- **Guide candidate:** B3-5.1-02 — Determining the Credit Score for a Mortgage Loan (PDF p.474)
- **SME:** [ ] agree [ ] correct: ______

### G372 — O-FNM-00195 [O-FNM]
- **Q:** Were all traditional credit history requirements met?
- **Defect condition:** Mortgage not reported and verification of satisfactory pay history is missing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1001
- **Severity:** Critical
- **Rationale:** MISCLASSIFIED (matched 'does not provide' + 'credit report' keyword) -- needs 12 months of month-by-month mortgage payment history; `extract_tradelines()` captures only a single current-status snapshot, same gap as F_PAYMENT_HISTORY_DEPTH.
- **Guide candidate:** B3-3.4-10 — Mortgage Credit Certiﬁcates (PDF p.366)
- **Guide candidate:** B3-5.1-02 — Determining the Credit Score for a Mortgage Loan (PDF p.474)
- **Guide candidate:** B3-5.3-03 — Previous Mortgage Payment History (PDF p.485)
- **SME:** [ ] agree [ ] correct: ______

### G374 — O-FNM-00201 [O-FNM]
- **Q:** Were all traditional credit history requirements met?
- **Defect condition:** Re-established credit not documented where significant derogatory credit events are reported
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1014
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **Guide candidate:** B3-5.3-07 — Signiﬁcant Derogatory Credit Events — Waiting Periods and Re-establishing Credit (PDF p.489)
- **Guide candidate:** B3-5.3-08 — Extenuating Circumstances for Derogatory Credit (PDF p.494)
- **Guide candidate:** B3-5.4-03 — Documentation and Assessment of a Nontraditional Credit History (PDF p.509)
- **SME:** [ ] agree [ ] correct: ______

### G375 — O-FNM-00198 [O-FNM]
- **Q:** Were all traditional credit history requirements met?
- **Defect condition:** Required documentation missing for a bankruptcy/foreclosure action reported in the last 7 years
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1028
- **Severity:** Critical
- **Rationale:** Needs derogatory-credit history (bankruptcy/foreclosure/short sale/collections/judgments/disputed accounts/tax liens) or a credit-exception memo -- this corpus's ONE credit report (loan 01) shows 'None reported' under Public Records/Collections/Derogatory, and 4 of 5 loans have no credit report at all. Not a rule-clarity problem; the synthetic fixtures simply never modeled adverse credit.
- **Guide candidate:** B3-5.4-03 — Documentation and Assessment of a Nontraditional Credit History (PDF p.509)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **Guide candidate:** B3-2-04 — DU Documentation Requirements (PDF p.305)
- **SME:** [ ] agree [ ] correct: ______

### G376 — O-FNM-50266 [O-FNM]
- **Q:** Were all traditional credit history requirements met?
- **Defect condition:** The pattern of using revolving credit to the max limit credit mgt risk not evaluated in manual UW
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 946
- **Severity:** Critical
- **Rationale:** The percentage-of-balance math (5%/1.5%/0.5% thresholds) is crisp arithmetic once the relevant balance is in hand, and `extract_tradelines()` already captures type/balance/monthly_payment per tradeline -- but confirming whether the LENDER actually included the computed amount in the final DTI needs a DTI worksheet this pilot doesn't derive (same gap as F_PITIA_DTI_REO); and month-by-month late-payment-in-12-months detection needs payment-history depth the tradeline snapshot (a single current 'Status' value) doesn't carry. Trigger data partly in hand; verification math not yet built.
- **Guide candidate:** B3-2-03 — Risk Factors Evaluated by DU (PDF p.299)
- **Guide candidate:** B3-5.4-03 — Documentation and Assessment of a Nontraditional Credit History (PDF p.509)
- **Guide candidate:** B1-1-03 — Allowable Age of Credit Documents and Federal Income Tax Returns (PDF p.170)
- **SME:** [ ] agree [ ] correct: ______

### G377 — O-FHA-50687 [O-FHA]
- **Q:** Were all types of credit history requirements met?
- **Defect condition:** A debt on the application is not on the credit report without documenting the debt separately
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 811
- **Severity:** Major
- **Rationale:** The REVERSE direction of `UndisclosedLiabilityShape`'s condition (that shape flags a credit-report tradeline missing from the 1003; this row flags a 1003 liability missing from the credit report) -- needs a separate written-verification document per unreported debt that isn't modeled in this corpus. Noted as textually adjacent to, but NOT the same real-world check as, the mapped shape -- do not conflate the two directions when this is eventually built.
- **SME:** [ ] agree [ ] correct: ______

### G378 — O-FHA-50686 [O-FHA]
- **Q:** Were all types of credit history requirements met?
- **Defect condition:** Inconsistencies noted in file info & orig credit report without a updated credit report/supplement
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1056
- **Severity:** Major
- **Rationale:** Needs a second (updated) credit-report pull to compare against the original, plus a resubmission/rescoring record -- neither exists for any loan in this corpus (each loan has at most one credit report snapshot).
- **SME:** [ ] agree [ ] correct: ______

### G381 — O-FHA-02232 [O-FHA]
- **Q:** Were all undisclosed debt requirements met?
- **Defect condition:** Payment for undisclosed non-mortgage debt is not verified for resubmission requirements
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1047
- **Severity:** Critical
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **SME:** [ ] agree [ ] correct: ______

### G382 — O-FHA-02233 [O-FHA]
- **Q:** Were all undisclosed debt requirements met?
- **Defect condition:** Undisclosed mtg not in TOTAL w/ unacceptable pay history not downgraded to Refer/manual UW
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1049
- **Severity:** Critical
- **Rationale:** DU (Fannie)/LPA (Freddie)/TOTAL (FHA) AUS feedback-certificate or resubmission-log export -- no such document exists as a doc type in this pilot for any agency; RHS's GUS findings is parsed for loan 05 but only for USDA income-limit fields, not a downgrade/resubmission log. Same AUS-submission-export gap flagged in the asset-verification triage (decision 017, G037/G039/G095/G179/G243/G244).
- **SME:** [ ] agree [ ] correct: ______

## RED

### G039 — O-FCRA-52834 [GENERIC]
- **Q:** Were all FCRA underwriting requirements met?
- **Defect condition:** Reasonable steps or specified ph# not used to clear identity theft/fraud extended alert
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 869
- **Severity:** Critical
- **Stays human:** Reasonable steps or specified ph# not used to clear identity theft/fraud extended alert
- **Rationale:** FCRA identity-theft/active-duty/fraud-alert phone verification ('reasonable steps') has no bright-line test, and no alert flag exists anywhere in this corpus's one credit report (loan 01) regardless.
- **Guide candidate:** A2-3.2-02 — Enforcement Relief for Breaches of Certain Representations and Warranties Related to Underwriting and Eligibility (PDF p.65)
- **Guide candidate:** A3-4-03 — Preventing, Detecting, and Reporting Mortgage Fraud (PDF p.142)
- **Guide candidate:** B2-3-02 — Special Property Eligibility and Underwriting Considerations: Factory-Built Housing (PDF p.261)
- **SME:** [ ] agree [ ] correct: ______

### G040 — O-FCRA-51725 [GENERIC]
- **Q:** Were all FCRA underwriting requirements met?
- **Defect condition:** Reasonable steps or specified ph# not used to verify active duty alert from consumer credit report
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 763
- **Severity:** Critical
- **Stays human:** Reasonable steps or specified ph# not used to verify active duty alert from consumer credit report
- **Rationale:** FCRA identity-theft/active-duty/fraud-alert phone verification ('reasonable steps') has no bright-line test, and no alert flag exists anywhere in this corpus's one credit report (loan 01) regardless.
- **Guide candidate:** B3-2-09 — Erroneous Credit Report Data (PDF p.311)
- **Guide candidate:** B3-2-10 — Accuracy of DU Data, DU Tolerances, and Errors in the Credit Report (PDF p.313)
- **Guide candidate:** B3-2-11 — DU Underwriting Findings Report (PDF p.316)
- **SME:** [ ] agree [ ] correct: ______

### G041 — O-FCRA-51724 [GENERIC]
- **Q:** Were all FCRA underwriting requirements met?
- **Defect condition:** Reasonable steps or specified ph# not used to verify initial fraud alert from consumer credit report
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 892
- **Severity:** Critical
- **Stays human:** Reasonable steps or specified ph# not used to verify initial fraud alert from consumer credit report
- **Rationale:** FCRA identity-theft/active-duty/fraud-alert phone verification ('reasonable steps') has no bright-line test, and no alert flag exists anywhere in this corpus's one credit report (loan 01) regardless.
- **Guide candidate:** B3-2-09 — Erroneous Credit Report Data (PDF p.311)
- **Guide candidate:** B3-2-10 — Accuracy of DU Data, DU Tolerances, and Errors in the Credit Report (PDF p.313)
- **Guide candidate:** B3-2-11 — DU Underwriting Findings Report (PDF p.316)
- **SME:** [ ] agree [ ] correct: ______

### G064 — O-RHS-56096 [O-RHS]
- **Q:** Were all additional adverse or derogatory credit requirements met?
- **Defect condition:** Credit exception made w/out borr's explanation of extenuating circumstances & lender rationale
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 809
- **Severity:** Critical
- **Stays human:** Credit exception made w/out borr's explanation of extenuating circumstances & lender rationale
- **Rationale:** 'Extenuating circumstances' is inherently a narrative/judgment determination, same class as asset-verification's narrative-adequacy REDs (G012/G193).
- **SME:** [ ] agree [ ] correct: ______

### G069 — O-RHS-50009 [O-RHS]
- **Q:** Were all additional adverse or derogatory credit requirements met?
- **Defect condition:** Outstanding collection account was not analyzed to determine significance or if pay off required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1059
- **Severity:** Critical
- **Stays human:** Outstanding collection account was not analyzed to determine significance or if pay off required
- **Rationale:** Whether a derogatory/adverse event is 'significant' is an underwriter judgment call, not a bright-line test -- same class as prior REDs on significance/reasonableness determinations (application-verification G7/G11/G23, asset-verification G012/G053).
- **SME:** [ ] agree [ ] correct: ______

### G072 — O-VA-50019 [O-VA]
- **Q:** Were all additional credit history requirements met?
- **Defect condition:** Loan approval does not evidence analysis determining the significance of derogatory credit reporting
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 907
- **Severity:** Critical
- **Stays human:** Loan approval does not evidence analysis determining the significance of derogatory credit reporting
- **Rationale:** Whether a derogatory/adverse event is 'significant' is an underwriter judgment call, not a bright-line test -- same class as prior REDs on significance/reasonableness determinations (application-verification G7/G11/G23, asset-verification G012/G053).
- **SME:** [ ] agree [ ] correct: ______

### G074 — O-VA-50015 [O-VA]
- **Q:** Were all additional credit history requirements met?
- **Defect condition:** Outstanding collection account(s) was not analyzed to determine significance or if pay off required
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 798
- **Severity:** Critical
- **Stays human:** Outstanding collection account(s) was not analyzed to determine significance or if pay off required
- **Rationale:** Whether a derogatory/adverse event is 'significant' is an underwriter judgment call, not a bright-line test -- same class as prior REDs on significance/reasonableness determinations (application-verification G7/G11/G23, asset-verification G012/G053).
- **SME:** [ ] agree [ ] correct: ______

### G185 — DEBTS-PAID [O-FNM]
- **Q:** Were all debts paid off at or prior to closing requirements met?
- **Defect condition:** All debts were not paid off at or prior to closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 839
- **Severity:** Critical
- **Stays human:** All debts were not paid off at or prior to closing
- **Rationale:** Open-ended sweep across whatever debts were separately flagged 'required to be paid at closing' -- no single named debt or threshold stated; needs SME decomposition into the specific debts before any one fact is checkable, same pattern as application-verification's 'all disclosures per guidelines' and asset-verification's bare 'all requirements ... not met' catch-alls (G018/G023/G196/G265).
- **Guide candidate:** B3-6-07 — Debts Paid Oﬀ At or Prior to Closing (PDF p.531)
- **Guide candidate:** B5-3.1-02 — Conversion of Construction-to-Permanent Financing: Single-Closing Transactions (PDF p.736)
- **Guide candidate:** B5-3.1-03 — Conversion of Construction-to-Permanent Financing: Two-Closing Transactions (PDF p.743)
- **SME:** [ ] agree [ ] correct: ______

### G201 — O-VA-00143 [O-VA]
- **Q:** Were all derogatory/adverse account requirements met?
- **Defect condition:** Loan approval does not evidence satisfactory credit risk for serious adverse credit reported
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 765
- **Severity:** Critical
- **Stays human:** Loan approval does not evidence satisfactory credit risk for serious adverse credit reported
- **Rationale:** Holistic 'satisfactory credit risk'/'acceptable payment history' determination -- an underwriter judgment call across the whole file, not a single checkable fact.
- **SME:** [ ] agree [ ] correct: ______

### G234 — O-FRD-50026 [O-FRD]
- **Q:** Were all manual underwriting adverse or derogatory credit requirements met?
- **Defect condition:** Multiple late payments reporting without analysis determining significance of adverse/derog event
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 767
- **Severity:** Critical
- **Stays human:** Multiple late payments reporting without analysis determining significance of adverse/derog event
- **Rationale:** Whether a derogatory/adverse event is 'significant' is an underwriter judgment call, not a bright-line test -- same class as prior REDs on significance/reasonableness determinations (application-verification G7/G11/G23, asset-verification G012/G053).
- **SME:** [ ] agree [ ] correct: ______

### G235 — O-FRD-50022 [O-FRD]
- **Q:** Were all manual underwriting adverse or derogatory credit requirements met?
- **Defect condition:** Outstanding collection(s) reported  and determination of significance is not documented
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 797
- **Severity:** Critical
- **Stays human:** Outstanding collection(s) reported  and determination of significance is not documented
- **Rationale:** Whether a derogatory/adverse event is 'significant' is an underwriter judgment call, not a bright-line test -- same class as prior REDs on significance/reasonableness determinations (application-verification G7/G11/G23, asset-verification G012/G053).
- **SME:** [ ] agree [ ] correct: ______

### G249 — O-FHA-02314 [O-FHA]
- **Q:** Were all manually underwritten collection account requirements met?
- **Defect condition:** Loan approved and the borr's collection or charge off account not due to extenuating circumstances
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 923
- **Severity:** Critical
- **Stays human:** Loan approved and the borr's collection or charge off account not due to extenuating circumstances
- **Rationale:** 'Extenuating circumstances' is inherently a narrative/judgment determination, same class as asset-verification's narrative-adequacy REDs (G012/G193).
- **SME:** [ ] agree [ ] correct: ______

### G274 — O-FHA-02313 [O-FHA]
- **Q:** Were all manually underwritten types of payment histories requirements met?
- **Defect condition:** The loan was approved with an unacceptable payment history as per review of the credit report
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 941
- **Severity:** Critical
- **Stays human:** The loan was approved with an unacceptable payment history as per review of the credit report
- **Rationale:** Holistic 'satisfactory credit risk'/'acceptable payment history' determination -- an underwriter judgment call across the whole file, not a single checkable fact.
- **SME:** [ ] agree [ ] correct: ______

### G366 — DEBTS-PAID [GENERIC]
- **Q:** Were all the requirements met for debts paid off at or prior to closing?
- **Defect condition:** All debts were not paid of at or prior to closing
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 838
- **Severity:** Critical
- **Stays human:** All debts were not paid of at or prior to closing
- **Rationale:** Open-ended sweep across whatever debts were separately flagged 'required to be paid at closing' -- no single named debt or threshold stated; needs SME decomposition into the specific debts before any one fact is checkable, same pattern as application-verification's 'all disclosures per guidelines' and asset-verification's bare 'all requirements ... not met' catch-alls (G018/G023/G196/G265).
- **Guide candidate:** B3-6-07 — Debts Paid Oﬀ At or Prior to Closing (PDF p.531)
- **Guide candidate:** B5-3.1-02 — Conversion of Construction-to-Permanent Financing: Single-Closing Transactions (PDF p.736)
- **Guide candidate:** B5-3.1-03 — Conversion of Construction-to-Permanent Financing: Two-Closing Transactions (PDF p.743)
- **SME:** [ ] agree [ ] correct: ______

### G371 — O-FNM-00200 [O-FNM]
- **Q:** Were all traditional credit history requirements met?
- **Defect condition:** Loan approval does not evidence satisfactory credit risk for serious adverse credit reported
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 850
- **Severity:** Critical
- **Rationale:** MISCLASSIFIED (matched 'not provided' + 'credit report' keyword). Verified: this is the byte-for-byte-identical FNM wording variant of O-VA-00143 (group 201 below), which this triage independently classified RED for 'satisfactory credit risk' being a holistic underwriter judgment -- a clean demonstration of the bug: the exact same real-world condition got auto-GREENed here purely because amq_compiler.py's regex happened to fire, and correctly hand-classified RED there because it didn't.
- **Guide candidate:** B3-5.1-02 — Determining the Credit Score for a Mortgage Loan (PDF p.474)
- **Guide candidate:** B3-5.4-03 — Documentation and Assessment of a Nontraditional Credit History (PDF p.509)
- **Guide candidate:** A1-1-01 — Application and Approval of Seller/Servicer (PDF p.20)
- **SME:** [ ] agree [ ] correct: ______

## NOT_A_CHECK

### G002 —  [O-FHA]
- **Q:** (FHA) Was a credit report in the loan file for each applicant responsible for loan repayment?
- **Defect condition:** The loan program did not require a credit report to qualify
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1067, 1068
- **Rationale:** Screening/applicability answer branch (empty exception_code in the source row), not a defect condition -- same pattern as application-verification's LEP-applicability group and asset-verification's group 291.
- **SME:** [ ] agree [ ] correct: ______

### G004 —  [O-FHA]
- **Q:** (FHA) Which of the following special credit considerations apply to this loan?
- **Defect condition:** Alimony, Child Support, and Maintenance Debt
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1138, 1139, 1140, 1141, 1142, 1143, 1144, 1145, 1146, 1147, 1148, 1149, 1150, 1151, 1152, 1153, 1154
- **Rationale:** Screening/applicability answer branch (empty exception_code in the source row), not a defect condition -- same pattern as application-verification's LEP-applicability group and asset-verification's group 291.
- **SME:** [ ] agree [ ] correct: ______

### G007 —  [O-FNM]
- **Q:** (Fannie Mae) Was a credit report in the loan file for each applicant responsible for loan repayment?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1159, 1160
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G010 —  [O-FRD]
- **Q:** (Freddie Mac) Was a credit report in the loan file for each applicant responsible for loan repayment?
- **Defect condition:** Yes, a credit report is in the loan for each responsible applicant
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1178
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G013 —  [O-RHS]
- **Q:** (RHS) Was a credit report in the loan file for each applicant responsible for loan repayment?
- **Defect condition:** Yes, a credit report is in the file for each responsible applicant
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1197
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G015 —  [O-VA]
- **Q:** (VA) Was a credit report in the loan file for each applicant responsible for loan repayment?
- **Defect condition:** The loan program did not require a credit report to qualify
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1206, 1207
- **Rationale:** Screening/applicability answer branch (empty exception_code in the source row), not a defect condition -- same pattern as application-verification's LEP-applicability group and asset-verification's group 291.
- **SME:** [ ] agree [ ] correct: ______

### G018 —  [O-FHA]
- **Q:** Were all AUS specific 30-day accounts requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1132, 1133
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G020 —  [O-FHA]
- **Q:** Were all AUS specific general liabilities and debt requirements met?
- **Defect condition:** Yes, all  general liabilities and debt requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1127
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G022 —  [O-FHA]
- **Q:** Were all AUS specific other liabilities requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1134, 1135
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G024 —  [O-FHA]
- **Q:** Were all AUS specific revolving charge account requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1130, 1131
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G026 —  [O-FHA]
- **Q:** Were all AUS specific student loan liabilities requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1128, 1129
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G031 —  [O-VA]
- **Q:** Were all Automated Underwriting Cases (AUS) requirements met?
- **Defect condition:** Yes, all Automated Underwriting Cases (AUS) requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1217
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G034 —  [O-FHA]
- **Q:** Were all Disputed Derogatory Credit Account requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1076, 1077
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G036 —  [O-FRD]
- **Q:** Were all Employee Relocation Program requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1179, 1180
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G038 —  [GENERIC]
- **Q:** Were all FCRA underwriting requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1065, 1066
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G044 —  [O-FRD]
- **Q:** Were all Internal Revenue Service (IRS) installment agreement requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1195, 1196
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G054 —  [O-FRD]
- **Q:** Were all Loan Product Advisor® credit assessment requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1181, 1182
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G061 —  [O-VA]
- **Q:** Were all Residential Mortgage Credit Reports (RMCR) requirements met?
- **Defect condition:** Yes, all Residential Mortgage Credit Reports (RMCR) requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1216
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G068 —  [O-RHS]
- **Q:** Were all additional adverse or derogatory credit requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1202, 1203
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G076 —  [O-VA]
- **Q:** Were all additional credit history requirements met?
- **Defect condition:** Yes, all additional credit history requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1215
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G081 —  [O-FRD]
- **Q:** Were all additional credit report requirements met?
- **Defect condition:** Yes, all credit report requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1187
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G085 —  [O-FRD]
- **Q:** Were all additional manual underwriting credit assessment requirements met?
- **Defect condition:** Yes, all additional manual underwriting  credit assessment requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1185
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G094 —  [O-FRD]
- **Q:** Were all additional monthly debt payment-to-income ratio liability evaluation requirements met?
- **Defect condition:** Yes, all additional monthly debt payment-to-income ratio liability evaluation requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1193
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G103 —  [O-RHS]
- **Q:** Were all adverse or derogatory credit requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1200, 1201
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G107 —  [O-FHA]
- **Q:** Were all alimony, child support, and maintenance debt requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1093, 1094
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G119 —  [O-RHS]
- **Q:** Were all applicant(s) debt/liabilities requirements met?
- **Defect condition:** Yes, all applicant(s) debt/liabilities requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1199
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G121 —  [O-FHA]
- **Q:** Were all bankruptcy requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1080, 1081
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G126 —  [O-FRD]
- **Q:** Were all credit assessment requirements met?
- **Defect condition:** Yes, all credit assessment requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1194
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G131 —  [O-VA]
- **Q:** Were all credit history requirements met?
- **Defect condition:** Yes, all credit history requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1214
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G140 —  [O-RHS]
- **Q:** Were all credit report and credit history requirements met?
- **Defect condition:** Yes, all credit report and credit history requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1198
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G160 —  [O-FHA]
- **Q:** Were all credit report requirements met?
- **Defect condition:** Yes, all   credit report requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1075
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G161 —  [O-FNM/O-FRD/O-VA]
- **Q:** Were all credit report requirements met?
- **Defect condition:** Yes, all credit report requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1162, 1186, 1208
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G168 —  [O-FNM/O-FRD]
- **Q:** Were all credit score requirements met?
- **Defect condition:** Yes, all credit score requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1161, 1188
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G170 —  [O-FHA]
- **Q:** Were all debt and liability evaluation requirements met?
- **Defect condition:** Yes, all debt and liability evaluation requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1137
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G173 —  [O-FNM]
- **Q:** Were all debt-to-income (DTI) ratio requirements met?
- **Defect condition:** Yes, all debt-to-income (DTI) ratio requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1167
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G184 —  [O-VA]
- **Q:** Were all debts and obligations requirements met?
- **Defect condition:** Yes, all debts and obligations requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1209
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G190 —  [O-FNM]
- **Q:** Were all debts paid off at or prior to closing requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1172, 1173
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G193 —  [O-FHA]
- **Q:** Were all deferred obligation (excluding Student Loans) liabilities requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1097, 1098
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G195 —  [O-FHA]
- **Q:** Were all delinquent federal non-tax debt requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1069, 1070
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G197 —  [O-FHA]
- **Q:** Were all delinquent federal tax debt requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1071, 1072
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G202 —  [O-VA]
- **Q:** Were all derogatory/adverse account requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1210, 1211
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G206 —  [O-FNM]
- **Q:** Were all erroneous credit report data requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1174, 1175, 5463, 5464
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G211 —  [O-FHA/O-VA]
- **Q:** Were all federal debt requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1091, 1092, 1212, 1213
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G214 —  [O-FHA]
- **Q:** Were all federal tax lien requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1073, 1074
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G217 —  [O-FHA]
- **Q:** Were all foreclosure requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1084, 1085
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G221 —  [O-FHA]
- **Q:** Were all general liabilities and debt requirements met?
- **Defect condition:** Yes, all   general liabilities and debt requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1088
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G223 —  [O-FHA]
- **Q:** Were all housing obligation/mortgage payment history requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1086, 1087
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G226 —  [O-FHA]
- **Q:** Were all installment loan requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1101, 1102
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G228 —  [O-FHA]
- **Q:** Were all judgment requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1078, 1079
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G239 —  [O-FRD]
- **Q:** Were all manual underwriting adverse or derogatory credit requirements met?
- **Defect condition:** Yes, all manual underwriting  adverse or derogatory credit requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1184
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G246 —  [O-FRD]
- **Q:** Were all manual underwriting credit assessment requirements met?
- **Defect condition:** Yes, all manual underwriting  credit assessment requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1183
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G247 —  [O-FHA]
- **Q:** Were all manually underwritten bankruptcy requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1117, 1118
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G250 —  [O-FHA]
- **Q:** Were all manually underwritten collection account requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1113, 1114
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G251 —  [O-FHA]
- **Q:** Were all manually underwritten consumer credit counseling program requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1123, 1124
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G255 —  [O-FHA]
- **Q:** Were all manually underwritten debt and liability evaluation requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1125, 1126
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G258 —  [O-FHA]
- **Q:** Were all manually underwritten disputed derogatory credit account requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1115, 1116
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G260 —  [O-FHA]
- **Q:** Were all manually underwritten foreclosure or deed-in-lieu of foreclosure requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1119, 1120
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G261 —  [O-FHA]
- **Q:** Were all manually underwritten housing obligation/mortgage payment requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1111, 1112
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G263 —  [O-FHA]
- **Q:** Were all manually underwritten pre-foreclosure sale (short sale) requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1121, 1122
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G269 —  [O-FHA]
- **Q:** Were all manually underwritten types of credit history requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1107, 1108
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G272 —  [O-FHA]
- **Q:** Were all manually underwritten types of payment histories requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1109, 1110
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G285 —  [O-FNM]
- **Q:** Were all monthly debt obligations requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1170, 1171
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G297 —  [O-FRD]
- **Q:** Were all monthly debt payment-to-income ratio liability evaluation requirements met?
- **Defect condition:** Yes, all monthly debt payment-to-income ratio liability evaluation requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1192, 5486
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G306 —  [O-FRD]
- **Q:** Were all monthly housing expense-to-income ratio evaluation requirements met?
- **Defect condition:** Yes, all monthly housing expense-to-income ratio evaluation requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1191, 5484, 5485
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G308 —  [O-FNM]
- **Q:** Were all monthly housing requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1168, 1169
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G314 —  [O-FHA]
- **Q:** Were all non-borrowing spouse debt requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1095, 1096
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G318 —  [O-RHS]
- **Q:** Were all non-traditional credit report and credit history requirements met?_x000D_
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1204, 1205
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G327 —  [O-FNM]
- **Q:** Were all nontraditional credit history requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1165, 1166
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G331 —  [O-FHA]
- **Q:** Were all other liabilities requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1105, 1106
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G336 —  [O-FNM]
- **Q:** Were all other monthly debt obligations requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1176, 1177
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G339 —  [O-FHA]
- **Q:** Were all positive rental payment history requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1155, 1156
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G343 —  [O-FHA]
- **Q:** Were all pre-foreclosure (short sale) requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1082, 1083
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G351 —  [O-FHA]
- **Q:** Were all requirements met where a previous mortgage forbearance was granted on the subject property or other residence?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1157, 1158
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G355 —  [O-FHA]
- **Q:** Were all revolving charge account requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1103, 1104
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G360 —  [O-FRD]
- **Q:** Were all student loan evaluation requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1189, 1190
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G363 —  [O-FHA]
- **Q:** Were all student loan liabilities requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1099, 1100
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G367 —  [GENERIC]
- **Q:** Were all the requirements met for debts paid off at or prior to closing?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1063, 1064
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G373 —  [O-FNM]
- **Q:** Were all traditional credit history requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1163, 1164
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G379 —  [O-FHA]
- **Q:** Were all types of credit history requirements met?
- **Defect condition:** Yes, all types of credit history requirements were met
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, row 1136
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

### G380 —  [O-FHA]
- **Q:** Were all undisclosed debt requirements met?
- **Defect condition:** Not Applicable
- **Source:** PF and PC Sept 2025 AMQs - Retail - Post-Closing.csv, rows 1089, 1090
- **Rationale:** Pass/N-A answer option, not a defect condition.
- **SME:** [ ] agree [ ] correct: ______

