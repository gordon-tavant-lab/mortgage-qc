#!/usr/bin/env python3
"""
Loan document extractor — demo/syn PDFs + MISMO XML -> extraction JSON with citations.

Per decision 002: the pilot extracts loan data itself, deterministically, via
`pdftotext -layout`. Every value carries a citation {doc_name, page, snippet}
(decision 003). Signature presence is recognized from the documents' signature
lines. The answer-key PDF (00_Loan_Summary_And_Answer_Key.pdf) is NEVER parsed.

Honesty rule: `*** ... ***` markers are stripped from extracted VALUES (the machine
never reads the stage directions), but the raw matched line is kept as the citation
snippet — the same line an auditor would see in the PDF.

USAGE:
  python3 extract_loan.py "<loan folder>" <output_json>
"""
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import date

ANSWER_KEY_RE = re.compile(r"00_Loan_Summary", re.I)

# ---------------------------------------------------------------- doc inventory
DOC_TYPES = [
    ("final_1003", r"Final_1003"),
    ("voe", r"Verification_of_Employment"),
    ("paystub", r"Paystub"),
    ("credit_report", r"Credit_Report"),
    ("bank_statement", r"Bank_Statement"),
    ("disclosure_index", r"Initial_Disclosure_Package_Index"),
    ("title_commitment", r"Title_Commitment"),
    ("closing_disclosure", r"Closing_Disclosure"),
    ("hud_92900a", r"HUD_92900A"),
    ("fhac_case_assignment", r"FHA_Connection"),
    ("gift_letter", r"Gift_Letter"),
    ("caivrs", r"CAIVRS"),
    ("va_coe", r"Certificate_of_Eligibility"),
    ("va_nov", r"Notice_of_Value"),
    ("payoff_statement", r"Payoff_Statement"),
    ("vom", r"Mortgage_Payment_History|VOM"),
    ("se_income_index", r"Self_Employed_Income"),
    ("gus_findings", r"GUS_Findings"),
    ("usda_property_elig", r"Property_Eligibility"),
    ("usda_ratio_waiver_doc", r"Debt_Ratios"),
    ("appraisal", r"Appraisal"),  # last: generic
]

# docs the program requires whose ABSENCE from the folder is itself a fact
# (weakest citation form — cited to the folder inventory; decision 003)
EXPECTED_DOCS_BY_PROGRAM = {
    "FHA": {
        "fha_amendatory_clause": r"Amendatory",
        "fha_form_442": r"442|Completion_Cert|Compliance_Inspection",
    },
    "VA": {
        "arm_program_disclosure": r"ARM_(Program_)?Disclosure|CHARM",
        "lbp_disclosure": r"Lead|LBP",
        "residual_income_worksheet": r"Residual",
    },
}

# ------------------------------------------------------- field specs (per doc)
MONEY = r"\$?([\d,]+(?:\.\d+)?)"
DATE_ = r"(\d{2}/\d{2}/\d{4})"

# (field_name, regex, kind)  kind in: str, money, date, pct
FIELD_SPECS = {
    "final_1003": [
        ("loan_number", r"Loan Number\s{2,}(\S+)", "str"),
        ("loan_program_1003", r"Loan Program\s{2,}(.+)", "str"),
        ("loan_purpose_1003", r"Loan Purpose(?: \(as stated\))?\s{2,}(.+)", "str"),
        ("property_state", r"Property Address\s+[^,]+,\s+[^,]+,\s+([A-Z]{2})\s+\d{5}", "str"),
        ("employment_start_date_1003", r"Employment Start(?: Date)?\s{2,}" + DATE_, "date"),
        ("base_monthly_income_1003", r"Base Monthly Income\s{2,}" + MONEY, "money"),
        ("title_vesting_1003", r"Title Vesting \(as stated on 1003\)\s+(.+)", "str"),
        ("fha_case_number_1003", r"FHA Case Number(?: \(per 1003\))?\s{2,}([\d-]+)", "str"),
        ("year_built_1003", r"Year Built\s{2,}(\d{4})", "str"),
        ("payoff_amount_1003", r"Payoff Amount \(existing 1st\)\s{2,}" + MONEY, "money"),
        ("cash_out_to_borrower_1003", r"Cash-Out to Borrower\s{2,}" + MONEY, "money"),
        ("borrower_signature_date_1003", r"Signatures.*?(\d{2}/\d{2}/\d{4})", "date"),
    ],
    "voe": [
        ("employment_start_date_voe", r"Date of Employment\s{2,}" + DATE_, "date"),
    ],
    "title_commitment": [
        ("title_vesting_commitment", r"Proposed Insured Owner\s{2,}(.+)", "str"),
    ],
    "closing_disclosure": [
        ("closing_date", r"Closing Date\s{2,}" + DATE_, "date"),
        ("loan_purpose_cd", r"Loan Purpose \(on CD\)\s+(.+)", "str"),
        ("payoff_cd", r"Payoff to \S+\s{2,}" + MONEY, "money"),
    ],
    "fhac_case_assignment": [
        ("fha_case_number_fhac", r"FHA Case Number \(per FHAC\)\s{2,}([\d-]+)", "str"),
    ],
    "payoff_statement": [
        ("payoff_statement_total", r"Total Payoff Amount\s{2,}" + MONEY, "money"),
    ],
    "va_nov": [
        ("nov_issue_date", r"NOV Issue Date\s{2,}" + DATE_, "date"),
    ],
    "appraisal": [
        ("appraisal_effective_date", r"Effective Date\s{2,}" + DATE_, "date"),
        ("appraised_value", r"Appraised Value\s{2,}" + MONEY, "money"),
        ("property_year_built", r"Year Built\s{2,}(\d{4})", "str"),
        ("year_built_appraisal", r"Year Built\s{2,}(\d{4})", "str"),
        ("site_value_pct", r"Site Value\s{2,}\$[\d,]+ \(([\d.]+)% of total value\)", "pct"),
        ("outbuildings", r"Outbuildings\s{2,}(.+)", "str"),
    ],
    "gus_findings": [
        ("usda_income_limit", r"Moderate Income Limit[^$]*" + MONEY, "money"),
        ("usda_adjusted_household_income",
         r"Adjusted Annual Household Income[^$]*" + MONEY, "money"),
    ],
    "usda_ratio_waiver_doc": [
        ("piti_ratio", r"PITI Ratio\s{2,}([\d.]+)%", "pct"),
        ("piti_guideline", r"PITI Ratio\s{2,}[\d.]+% \(guideline ([\d.]+)%\)", "pct"),
        ("dti_ratio", r"Total Debt Ratio\s{2,}([\d.]+)%", "pct"),
        ("dti_guideline", r"Total Debt Ratio\s{2,}[\d.]+% \(guideline ([\d.]+)%\)", "pct"),
    ],
}

# (fact_name, doc_type, regex, value_if_match, else_value_if_doc_present)
# else_value None => fact only emitted on match
FACT_SPECS = [
    # signatures (decision 002: text-rendered signature lines)
    ("sig_1003_borrowers_present", "final_1003", r"Signatures — .+", True, None),
    ("sig_voe_employer_present", "voe", r"Signed By\s{2,}\S.+", True, None),
    ("sig_nov_sar_present", "va_nov", r"SAR Signature\s{2,}\S.+", True, None),
    ("sig_gift_donor_present", "gift_letter", r"Donor Signature Date\s{2,}" + DATE_, True, None),
    ("sig_hud92900a_borrower_present", "hud_92900a",
     r"Section III — Borrower Certification.*UNSIGNED", False, True),
    # in-document "NOT IN FILE" statements (index/summary docs)
    ("gift_transfer_evidence_in_file", "gift_letter",
     r"Transfer Evidence in File\s+.*NOT PROVIDED", False, True),
    ("recert_of_value_in_file", "appraisal",
     r"Recertification of Value\s{2,}.*NOT IN FILE", False, None),
    ("termite_inspection_in_file", "appraisal",
     r"Termite[\s\S]{0,120}?NOT IN FILE", False, None),
    ("well_septic_inspection_in_file", "appraisal",
     r"Well/Septic\s{2,}.*none in file", False, None),
    ("usda_eligibility_screenprint_in_file", "usda_property_elig",
     r"Eligibility Determination\s+.*NOT IN FILE", False, None),
    ("ytd_pnl_in_file", "se_income_index",
     r"YTD Profit & Loss[\s\S]{0,80}?NOT IN FILE", False, None),
    ("ytd_balance_sheet_in_file", "se_income_index",
     r"YTD Balance Sheet[\s\S]{0,80}?NOT IN FILE", False, None),
    ("compensating_factors_documented", "usda_ratio_waiver_doc",
     r"Compensating Factors Documented.*NOT IN FILE", False, None),
    ("usda_ratio_waiver_in_file", "usda_ratio_waiver_doc",
     r"Waiver Request Form\s+.*NOT IN FILE", False, None),
    ("mpr_repair_required", "appraisal",
     r"Peeling paint[\s\S]{0,120}?YES", True, None),
    ("borrower_self_employed", "final_1003", r"self-employed", True, None),
    # appraisal addenda/explanation presence (loan 01 comp-distance check)
    ("comp_explanation_present", "appraisal",
     r"^(?:Addenda|Explanation)\b\s{2,}\S", True, None),
]

MARKER_RE = re.compile(r"\s*\*{2,}.*$")


def strip_marker(value):
    return MARKER_RE.sub("", value).strip()


def to_iso(mdy):
    m, d, y = mdy.split("/")
    return "%s-%s-%s" % (y, m, d)


def clean_money(s):
    return s.replace(",", "").replace("$", "")


def pdf_pages(path):
    """Return list of page texts via pdftotext -layout (deterministic)."""
    out = subprocess.run(
        ["pdftotext", "-layout", path, "-"],
        capture_output=True, text=True, check=True,
    ).stdout
    return out.split("\f")


def cite(doc, page, snippet):
    return {"doc_name": doc, "page": page, "snippet": snippet.strip()[:160]}


def match_line(pages, regex):
    """Search each page; return (match, page_num, line) or None."""
    rx = re.compile(regex, re.M)
    for i, page in enumerate(pages, 1):
        m = rx.search(page)
        if m:
            line_start = page.rfind("\n", 0, m.start()) + 1
            line_end = page.find("\n", m.end())
            line = page[line_start:line_end if line_end != -1 else None]
            return m, i, line
    return None


class LoanExtractor:
    def __init__(self, folder):
        self.folder = folder
        self.fields = {}
        self.facts = {}
        self.entities = {"bank_txns": [], "tradelines": [],
                         "urla_liabilities": [], "comps": [], "vom_rows": []}
        self.docs_present = {}
        self.doc_pages = {}

    def add_field(self, name, value, kind, doc, page, line):
        if name in self.fields:
            return  # first occurrence wins (borrower before co-borrower)
        raw = strip_marker(value)
        if kind == "money":
            typed = float(clean_money(raw))
        elif kind == "pct":
            typed = float(raw)
        elif kind == "date":
            typed = to_iso(raw)
        else:
            typed = raw
        self.fields[name] = {"value": typed, "kind": kind,
                             "citation": cite(doc, page, line)}

    def add_fact(self, name, value, doc, page, line):
        if name in self.facts:
            return
        self.facts[name] = {"value": value, "citation": cite(doc, page, line)}

    # ------------------------------------------------------------ inventory
    def inventory(self):
        for fn in sorted(os.listdir(self.folder)):
            if ANSWER_KEY_RE.search(fn):
                continue  # answer key is NEVER parsed (decision 002)
            full = os.path.join(self.folder, fn)
            if fn.lower().endswith(".pdf"):
                for dtype, rx in DOC_TYPES:
                    if re.search(rx, fn, re.I):
                        self.docs_present.setdefault(dtype, fn)
                        break
                self.doc_pages[fn] = pdf_pages(full)
            elif fn.lower().endswith(".xml"):
                self.docs_present.setdefault("mismo", fn)

    def pages_for(self, dtype):
        fn = self.docs_present.get(dtype)
        return (fn, self.doc_pages.get(fn)) if fn else (None, None)

    # ------------------------------------------------------------ extraction
    def extract_fields(self):
        for dtype, specs in FIELD_SPECS.items():
            fn, pages = self.pages_for(dtype)
            if not pages:
                continue
            for name, rx, kind in specs:
                hit = match_line(pages, rx)
                if hit:
                    m, pg, line = hit
                    self.add_field(name, m.group(1), kind, fn, pg, line)

    def extract_facts(self):
        for name, dtype, rx, val_on_match, val_default in FACT_SPECS:
            fn, pages = self.pages_for(dtype)
            if not pages:
                continue
            hit = match_line(pages, rx)
            if hit:
                _, pg, line = hit
                self.add_fact(name, val_on_match, fn, pg, line)
            elif val_default is not None:
                self.add_fact(name, val_default, fn, 1, "(pattern '%s' not present in document)" % rx[:60])

    def extract_coborrower_fields(self):
        """Co-borrower identity + employment (decision 015 / Bucket B): the
        extractor previously read these lines only to have add_field's
        first-occurrence-wins logic silently drop them in favor of the
        borrower's copy. Section 1 labels ("Co-Borrower Name/DOB") are
        unambiguous; Section 1b employment labels repeat the borrower's exact
        label text under a "(Co-Borrower)" sub-header, so those need a
        header-scoped search to avoid re-matching the borrower's line."""
        fn, pages = self.pages_for("final_1003")
        if not pages:
            return
        for pg_num, page in enumerate(pages, 1):
            for name, rx, kind in [
                ("co_borrower_name", r"Co-Borrower(?: Name)?\s{2,}(.+)", "str"),
                ("co_borrower_dob", r"Co-Borrower DOB\s{2,}" + DATE_, "date"),
            ]:
                m = re.search(rx, page)
                if m:
                    line_start = page.rfind("\n", 0, m.start()) + 1
                    line_end = page.find("\n", m.end())
                    self.add_field(name, m.group(1), kind, fn, pg_num,
                                  page[line_start: line_end if line_end != -1 else None])

            header_m = re.search(r"Section 1b.{0,40}\(Co-Borrower\)", page)
            if header_m:
                next_section = re.search(r"\nSection \d", page[header_m.end():])
                block_end = (header_m.end() + next_section.start()
                            if next_section else len(page))
                block = page[header_m.end():block_end]
                for name, rx, kind in [
                    ("employer_name_1003_coborrower", r"Employer\s{2,}(.+)", "str"),
                    ("employment_start_date_1003_coborrower",
                     r"Employment Start Date\s{2,}" + DATE_, "date"),
                    ("base_monthly_income_1003_coborrower",
                     r"Base Monthly Income\s{2,}" + MONEY, "money"),
                ]:
                    m = re.search(rx, block)
                    if m:
                        b_start = block.rfind("\n", 0, m.start()) + 1
                        b_end = block.find("\n", m.end())
                        self.add_field(name, m.group(1), kind, fn, pg_num,
                                      block[b_start: b_end if b_end != -1 else None])

            # inline co-borrower income format (no distinct sub-header) —
            # e.g. "Co-Borrower Employer ..." / "Co-Borrower Base Pay ($N/mo)"
            for name, rx, kind in [
                ("employer_name_1003_coborrower", r"Co-Borrower Employer\s{2,}(.+)", "str"),
                ("base_monthly_income_1003_coborrower",
                 r"Co-Borrower Base Pay\s{2,}\$[\d,]+\s*/\s*year\s*\(\$" + MONEY + r"/mo\)", "money"),
            ]:
                m = re.search(rx, page)
                if m:
                    line_start = page.rfind("\n", 0, m.start()) + 1
                    line_end = page.find("\n", m.end())
                    self.add_field(name, m.group(1), kind, fn, pg_num,
                                  page[line_start: line_end if line_end != -1 else None])

    def extract_coborrower_signature_fact(self):
        """Always resolves true/false when a co-borrower exists (decision 008:
        never let 'no signature line found' pass silently as an implicit
        PASS — that is indistinguishable from a genuine defect)."""
        fn, pages = self.pages_for("final_1003")
        if not pages:
            return
        co_name = self.fields.get("co_borrower_name", {}).get("value")
        if not co_name:
            return  # not applicable — this loan has no co-borrower
        hit = match_line(pages, r"Signat(?:ures?|ed):?\s*[—:-]\s*\S.+")
        if hit:
            _, pg, line = hit
            surname = co_name.split()[-1]
            self.add_fact("sig_coborrower_present", surname in line, fn, pg, line)
        else:
            self.add_fact("sig_coborrower_present", False, fn, 1,
                          "(no signature line found anywhere in the final 1003)")

    def extract_expected_doc_absences(self, mortgage_type):
        listing = ", ".join(sorted(self.doc_pages)) or "(empty folder)"
        expected = EXPECTED_DOCS_BY_PROGRAM.get(mortgage_type, {})
        for fact_base, rx in expected.items():
            present = any(re.search(rx, fn, re.I) for fn in self.doc_pages)
            self.add_fact("doc_present_" + fact_base, present,
                          "(loan folder inventory)", 0, listing)
        # large-deposit sourcing docs: only meaningful when a bank statement exists
        if "bank_statement" in self.docs_present:
            sourced = any(re.search(r"Gift_Letter|Source_of_Funds", fn, re.I)
                          for fn in self.doc_pages)
            self.add_fact("large_deposit_source_documented", sourced,
                          "(loan folder inventory)", 0, listing)

    # ------------------------------------------------------------ tables
    def extract_bank_txns(self):
        fn, pages = self.pages_for("bank_statement")
        if not pages:
            return
        for pg_num, page in enumerate(pages, 1):
            header = re.search(r"^(Date\s+Description\s+Credit\s+Debit\s+Balance)\s*$",
                               page, re.M)
            if not header:
                continue
            hline = header.group(1)
            c_credit, c_debit = hline.index("Credit"), hline.index("Debit")
            c_balance = hline.index("Balance")
            for m in re.finditer(r"^(\d{2}/\d{2}/\d{4})\s{2,}(.+)$", page, re.M):
                line = m.group(0)
                desc = line[len(m.group(1)):c_credit].strip()
                credit = line[c_credit - 2:c_debit].strip()
                debit = line[c_debit - 2:c_balance].strip()
                txn = {"date": to_iso(m.group(1)), "description": desc,
                       "citation": cite(fn, pg_num, line)}
                if credit.startswith("$"):
                    txn["credit_amount"] = float(clean_money(credit))
                if debit.startswith("$"):
                    txn["debit_amount"] = float(clean_money(debit))
                self.entities["bank_txns"].append(txn)

    def extract_tradelines(self):
        fn, pages = self.pages_for("credit_report")
        if not pages:
            return
        rx = re.compile(
            r"^([A-Za-z][\w .'&]+?)\s{2,}(Revolving|Installment|Student\w*)"
            r"\s{2,}\$([\d,]+)\s{2,}\$([\d,]+)\s{2,}(\w+)", re.M)
        for pg_num, page in enumerate(pages, 1):
            for m in rx.finditer(page):
                self.entities["tradelines"].append({
                    "creditor": m.group(1).strip(), "type": m.group(2),
                    "balance": float(clean_money(m.group(3))),
                    "monthly_payment": float(clean_money(m.group(4))),
                    "status": m.group(5),
                    "citation": cite(fn, pg_num, m.group(0))})

    def extract_urla_liabilities(self):
        fn, pages = self.pages_for("final_1003")
        if not pages:
            return
        rx = re.compile(
            r"^\s{0,4}([A-Za-z][\w .'&]+?)\s{2,}\*{3}\d+\s{2,}([A-Za-z ]+?)"
            r"\s{2,}\$([\d,]+)\s{2,}\$([\d,]+)\s*$", re.M)
        for pg_num, page in enumerate(pages, 1):
            if "Section 2c" not in page and "Liabilities" not in page:
                continue
            for m in rx.finditer(page):
                self.entities["urla_liabilities"].append({
                    "creditor": m.group(1).strip(), "type": m.group(2).strip(),
                    "monthly_payment": float(clean_money(m.group(3))),
                    "balance": float(clean_money(m.group(4))),
                    "citation": cite(fn, pg_num, m.group(0))})

    def extract_comps(self):
        fn, pages = self.pages_for("appraisal")
        if not pages:
            return
        rx = re.compile(
            r"^\s*(\d)\s{2,}(.+?)\s{2,}([\d.]+) mi\b[ *]*\s{2,}\$([\d,]+)"
            r"\s{2,}([\d,]+)\s{2,}\$([\d,]+)", re.M)
        for pg_num, page in enumerate(pages, 1):
            for m in rx.finditer(page):
                self.entities["comps"].append({
                    "comp_num": int(m.group(1)), "address": m.group(2).strip(),
                    "distance_miles": float(m.group(3)),
                    "sale_price": float(clean_money(m.group(4))),
                    "gla": float(clean_money(m.group(5))),
                    "adjusted_sale_price": float(clean_money(m.group(6))),
                    "citation": cite(fn, pg_num, m.group(0))})

    def extract_vom(self):
        fn, pages = self.pages_for("vom")
        if not pages:
            return
        rx = re.compile(
            r"^\s*(\d{2}/\d{4})\s{2,}\d{2}/\d{2}/\d{4}\s{2,}\d{2}/\d{2}/\d{4}\s{2,}(.+)$",
            re.M)
        late30 = 0
        late_cite = None
        for pg_num, page in enumerate(pages, 1):
            for m in rx.finditer(page):
                status = strip_marker(m.group(2))
                row = {"month": m.group(1), "status": status,
                       "citation": cite(fn, pg_num, m.group(0))}
                self.entities["vom_rows"].append(row)
                if re.search(r"30[- ]DAY LATE|30 days late", m.group(2), re.I):
                    late30 += 1
                    late_cite = (fn, pg_num, m.group(0))
        if self.entities["vom_rows"]:
            if late_cite:
                self.add_fact("mortgage_late30_count_12mo", late30, *late_cite)
            else:
                self.add_fact("mortgage_late30_count_12mo", 0, fn, 1,
                              "(no 30-day-late rows in 12-month VOM)")

    # ------------------------------------------------------------ MISMO XML
    def extract_mismo(self):
        fn = self.docs_present.get("mismo")
        if not fn:
            return
        path = os.path.join(self.folder, fn)
        tree = ET.parse(path)
        wanted = {"LoanIdentifier": "mismo_loan_id",
                  "MortgageType": "mismo_mortgage_type",
                  "AmortizationType": "mismo_amortization_type",
                  "TotalMonthlyIncomeAmount": "mismo_total_monthly_income",
                  "TotalLiabilitiesMonthlyPaymentAmount": "mismo_total_liabilities_pmt",
                  "NoteRatePercent": "mismo_note_rate"}
        for el in tree.iter():
            tag = el.tag.split("}")[-1]
            if tag == "LoanPurposeType":
                source = el.get("Source", "")
                name = ("mismo_loan_purpose_cd" if "Closing" in source
                        else "mismo_loan_purpose_1003" if "URLA" in source
                        else "mismo_loan_purpose")
                if name not in self.fields and el.text:
                    self.add_field(name, el.text.strip(), "str", fn, 0,
                                   "<LoanPurposeType Source=%r>%s" % (source, el.text.strip()))
            elif tag in wanted and el.text and el.text.strip():
                name = wanted[tag]
                if name not in self.fields:
                    kind = "money" if "Amount" in tag else "str"
                    self.add_field(name, el.text.strip(), kind, fn, 0,
                                   "<%s>%s</%s>" % (tag, el.text.strip(), tag))

    # ------------------------------------------------------------ derived
    def derive(self):
        # loan-purpose cash-out booleans (semantic compare, not string compare)
        for src, name in (("loan_purpose_1003", "purpose_cashout_1003"),
                          ("loan_purpose_cd", "purpose_cashout_cd")):
            f = self.fields.get(src)
            if f:
                is_co = bool(re.search(r"cash[- ]?out", str(f["value"]), re.I))
                self.add_fact(name, is_co, f["citation"]["doc_name"],
                              f["citation"]["page"], f["citation"]["snippet"])
        # appraisal age at closing (dual-cited derivation, decision 002)
        eff, clo = self.fields.get("appraisal_effective_date"), self.fields.get("closing_date")
        if eff and clo:
            d1 = date.fromisoformat(eff["value"])
            d2 = date.fromisoformat(clo["value"])
            days = (d2 - d1).days
            self.add_fact("appraisal_age_days_at_closing", days,
                          eff["citation"]["doc_name"], eff["citation"]["page"],
                          "derived: %s (closing, %s) - %s (effective, %s) = %d days"
                          % (clo["value"], clo["citation"]["doc_name"],
                             eff["value"], eff["citation"]["doc_name"], days))

    def run(self):
        self.inventory()
        self.extract_mismo()
        self.extract_fields()
        self.extract_coborrower_fields()
        self.extract_facts()
        self.extract_coborrower_signature_fact()
        mt = self.fields.get("mismo_mortgage_type", {}).get("value", "")
        self.extract_expected_doc_absences(mt)
        self.extract_bank_txns()
        self.extract_tradelines()
        self.extract_urla_liabilities()
        self.extract_comps()
        self.extract_vom()
        self.derive()
        loan_id = self.fields.get("mismo_loan_id", {}).get("value") \
            or self.fields.get("loan_number", {}).get("value") or "UNKNOWN"
        return {"loan_id": loan_id, "folder": self.folder,
                "docs_present": self.docs_present,
                "fields": self.fields, "facts": self.facts,
                "entities": self.entities}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    result = LoanExtractor(sys.argv[1]).run()
    with open(sys.argv[2], "w") as f:
        json.dump(result, f, indent=1, sort_keys=True)
    print("Extracted loan %s: %d fields, %d facts, %d/%d/%d/%d/%d entities"
          % (result["loan_id"], len(result["fields"]), len(result["facts"]),
             len(result["entities"]["bank_txns"]), len(result["entities"]["tradelines"]),
             len(result["entities"]["urla_liabilities"]), len(result["entities"]["comps"]),
             len(result["entities"]["vom_rows"])))
