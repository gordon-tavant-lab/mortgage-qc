"""
extract_pdf.py — the DOC (truth) side adapter for synthetic-loan fixture generation.

Deterministic only: `pdftotext -layout` (subprocess) plus per-document-type,
label-anchored regex patterns in `doc_patterns/*.json` (data, not code-per-doc).
No LLM call on this path — every field in these 5 synthetic loans resolves via
pattern match against born-digital text (research.md decision #1). Never used
to populate the SYSTEM/mismo path (see qc_engine/mismo.py's own ruling #7 note —
the same one-directional discipline applies here, just the other side).

This is dev/test fixture generation, not the Touchless production extractor —
see README.md's disclaimers (FR-003).

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from typing import Any, Dict, List, Optional, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
DOC_PATTERNS_DIR = os.path.join(HERE, "doc_patterns")

# Priority order matters: more program-specific bundles (fha_docs/va_docs/usda_docs)
# must be checked before the generic appraisal_1004/urla_1003 patterns, since e.g.
# "06_FHA_Appraisal_Summary_1004_URAR.pdf" would otherwise also match the generic
# "Appraisal_Summary_1004" substring.
DOC_TYPE_PRIORITY = [
    "fha_docs",
    "va_docs",
    "usda_docs",
    "mortgage_payment_history",
    "self_employed_income_index",
    "payoff_statement",
    "bank_statement",
    "credit_report",
    "voe",
    "title_commitment",
    "closing_disclosure",
    "appraisal_1004",
    "urla_1003",
    "paystub",
    "disclosure_package_index",
]


def _load_doc_patterns() -> List[Tuple[str, Dict[str, Any]]]:
    patterns = []
    for name in DOC_TYPE_PRIORITY:
        path = os.path.join(DOC_PATTERNS_DIR, "{0}.json".format(name))
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                patterns.append((name, json.load(f)))
    return patterns


def _match_doc_type(filename: str, patterns: List[Tuple[str, Dict[str, Any]]]) -> Optional[Dict[str, Any]]:
    for _name, pattern in patterns:
        for substr in pattern.get("filename_contains", []):
            if substr in filename:
                return pattern
    return None


def _pdf_pages(path: str) -> List[str]:
    """Return per-page text via pdftotext -layout, splitting on the form-feed
    page separator pdftotext emits by default. Deterministic, offline, no OCR."""
    out = subprocess.run(
        ["pdftotext", "-layout", path, "-"],
        capture_output=True, text=True, check=True,
    ).stdout
    pages = out.split("\x0c")
    # pdftotext emits a trailing form feed after the last page; drop the
    # resulting empty tail segment rather than treating it as a real page.
    while pages and not pages[-1].strip():
        pages.pop()
    return pages


def _normalize_decimal(raw: str) -> str:
    cleaned = raw.replace("$", "").replace(",", "").strip()
    if "." not in cleaned:
        cleaned = cleaned + ".00"
    return cleaned


def _line_bounds(page_text: str, pos: int) -> Tuple[int, int]:
    """Start/end offsets of the line containing `pos` within page_text."""
    start = page_text.rfind("\n", 0, pos) + 1
    end = page_text.find("\n", pos)
    if end == -1:
        end = len(page_text)
    return start, end


def _snippet(page_text: str, match: "re.Match") -> str:
    """A short, human-readable citation snippet: the matched line, trimmed."""
    start, end = _line_bounds(page_text, match.start())
    return page_text[start:end].strip()


def _field_label(page_text: str, match: "re.Match") -> str:
    """The literal label text preceding the captured value on its line, e.g.
    "Employment Start Date" from "Employment Start Date    03/15/2018" --
    everything on the matched line up to where the value's own capture group
    begins, with any trailing punctuation the regex left dangling (e.g. a "$"
    matched outside the capture group for currency fields) stripped."""
    line_start, _ = _line_bounds(page_text, match.start())
    value_start = match.start(1) if match.lastindex else match.start()
    # A DOTALL-flag field's value can sit on a different line than its label
    # (e.g. a column-wrapped label spilling the value onto the next line), so
    # this substring can contain an embedded newline before the trailing
    # punctuation -- rstrip must include "\n" (not just " ") in its set, or a
    # trailing "label\n    $" only sheds the "$"/spaces and leaves "label\n".
    return page_text[line_start:value_start].strip().rstrip(" \n$:—-")


def _looks_like_a_header(line: str) -> bool:
    """These synthetic docs consistently lay out data as "Label<2+ spaces>
    Value" (pdftotext -layout preserves the source column spacing); section/
    subsection headers ("Section 1b -- Current Employment", "Subject
    Property", "Trade Lines (Borrower)") never have that multi-space split.
    A non-empty line with no run of 2+ spaces is, in this corpus, a header."""
    stripped = line.strip()
    if not stripped:
        return False
    return "  " not in stripped


def _document_title(pages: List[str]) -> Optional[str]:
    """The document's own displayed title -- the first non-empty line of the
    first page (every source PDF in this batch opens with one, e.g.
    "Uniform Residential Loan Application (Form 1003 / Fannie Mae Form 65)")."""
    for page_text in pages:
        for line in page_text.split("\n"):
            if line.strip():
                return line.strip()
    return None


def _nearest_section(page_text: str, match_start: int,
                      doc_title: Optional[str] = None) -> Optional[str]:
    """The closest preceding header-like line before the match, within the
    same page -- narrows "page 1" down to which part of that page a value
    came from (most of these documents are a single page). Excludes the
    document's own title (already carried separately as document_title) --
    a value with no true sub-section between it and the title is honestly
    "no section", not a redundant echo of the title."""
    line_start, _ = _line_bounds(page_text, match_start)
    preceding = page_text[:line_start].split("\n")
    for line in reversed(preceding):
        stripped = line.strip()
        if stripped and stripped == doc_title:
            continue
        if _looks_like_a_header(line):
            return stripped
    return None


def _extract_count_field(pages: List[str], field_def: Dict[str, Any],
                          doc_title: Optional[str] = None) -> Optional[Tuple[str, int, str, Optional[str], Optional[str]]]:
    """Aggregation fields (e.g. count of 30+ day mortgage lates in 12 months) —
    not a single label/value match, so handled distinctly from _extract_single_field.
    No single field_label applies to an aggregate across many matched lines
    (honestly None, not fabricated); section is the last contributing match's."""
    count_regex = field_def["count_regex"]
    min_days = field_def.get("count_min_days", 0)
    total = 0
    last_page = 1
    last_snippet = ""
    last_section = None
    for page_num, page_text in enumerate(pages, start=1):
        for m in re.finditer(count_regex, page_text):
            days = int(m.group(1))
            if days >= min_days:
                total += 1
                last_page = page_num
                last_snippet = _snippet(page_text, m)
                last_section = _nearest_section(page_text, m.start(), doc_title)
    if total == 0 and not last_snippet:
        return None
    return (str(total), last_page,
            last_snippet or "(no {0}+ day late payments found)".format(min_days),
            last_section, None)


def _extract_single_field(pages: List[str], field_def: Dict[str, Any],
                           doc_title: Optional[str] = None) -> Optional[Tuple[Any, int, str, Optional[str], Optional[str]]]:
    regex = field_def["regex"]
    flags = 0
    if "DOTALL" in field_def.get("flags", []):
        flags |= re.DOTALL
    for page_num, page_text in enumerate(pages, start=1):
        m = re.search(regex, page_text, flags)
        if m:
            snippet = _snippet(page_text, m)
            section = _nearest_section(page_text, m.start(), doc_title)
            label = _field_label(page_text, m)
            if field_def.get("boolean_false_if_found"):
                # A real Python bool, never the string "false" — field_catalog.json
                # declares data_type="boolean" for these fields, and a string is
                # truthy in Python (a silent landmine for any future `if sv.truth:`
                # consumer). json.dump serializes this as JSON `false`, not `"false"`.
                return (False, page_num, snippet, section, label)
            value = m.group(1).strip()
            if field_def.get("normalize") == "decimal":
                value = _normalize_decimal(value)
            return (value, page_num, snippet, section, label)
    return None


def _extract_simple_table(pages: List[str], table_def: Dict[str, Any],
                           doc_title: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """A repeating-row table where ONE regex match, via re.finditer, fully
    disambiguates every column (each named column is its own capture group,
    in order) -- used for the credit report's trade lines and the
    appraisal's comparable-sales grid, neither of which has an ambiguous
    "which column is this number in" case (unlike the bank ledger, below).
    Row index comes from an explicit capture group when the source document
    numbers its own rows (index_from_group, e.g. the appraisal's own "#"
    column), else a sequential 1-based counter."""
    row_regex = table_def["row_regex"]
    columns = table_def["columns"]
    field_prefix = table_def["field_prefix"]
    decimal_cols = set(table_def.get("decimal_columns", []))
    index_from_group = table_def.get("index_from_group")

    results: Dict[str, Dict[str, Any]] = {}
    seq = 0  # persists ACROSS pages -- a table's rows can straddle a page
    # break (e.g. loan 01's 1003 Assets table: "Checking" ends page 1,
    # "Savings"/"401(k)" start page 2); resetting per-page silently collided
    # row numbers and overwrote "Checking" with "Savings" under the same key.
    for page_num, page_text in enumerate(pages, start=1):
        for m in re.finditer(row_regex, page_text):
            seq += 1
            row_idx = int(m.group(index_from_group)) if index_from_group else seq
            snippet = _snippet(page_text, m)
            section = _nearest_section(page_text, m.start(), doc_title)
            for col_i, col_name in enumerate(columns, start=1):
                raw = m.group(col_i).strip()
                if not raw:
                    continue
                value = _normalize_decimal(raw) if col_name in decimal_cols else raw
                field_name = "{0}_{1:02d}_{2}".format(field_prefix, row_idx, col_name)
                results[field_name] = {
                    "value": value,
                    "citation": {
                        "doc_name": None,  # filled in by the caller, which knows the filename
                        "page_num": page_num,
                        "document_title": doc_title,
                        "section": section,
                        "field_label": None,  # a table cell has no single "label" line
                        "segment_snippet": snippet,
                    },
                    "doc_confidence": 0.98,
                }
    return results


def _extract_bank_ledger(pages: List[str], table_def: Dict[str, Any],
                          doc_title: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """The one table needing column-POSITION disambiguation: a bank
    statement's Credit and Debit columns are mutually exclusive per row (a
    transaction is one or the other, never both), and a plain regex capture
    can't tell which column the single present amount came from -- only its
    horizontal position (relative to the header's own column offsets) can,
    which is exactly what pdftotext -layout preserves and this reads."""
    header_regex = table_def["header_regex"]
    row_regex = table_def["row_regex"]
    field_prefix = table_def["field_prefix"]

    results: Dict[str, Dict[str, Any]] = {}
    row_idx = 0  # persists across pages -- same page-straddle risk as
    # _extract_simple_table's `seq` (see its comment); this table hasn't hit
    # it in this dataset (the one bank statement is single-page, verified by
    # test_bank_ledger_reconciles_to_the_penny), but resetting per-page would
    # silently collide row numbers the same way if a future statement spans
    # multiple pages.
    credit_off = debit_off = None  # once found, carries forward to
    # continuation pages that repeat data rows without re-printing the header
    for page_num, page_text in enumerate(pages, start=1):
        header_m = re.search(header_regex, page_text)
        if header_m:
            h_start, h_end = _line_bounds(page_text, header_m.start())
            header_line = page_text[h_start:h_end]
            found_credit = header_line.find("Credit")
            found_debit = header_line.find("Debit")
            if found_credit != -1 and found_debit != -1:
                credit_off, debit_off = found_credit, found_debit
        if credit_off is None or debit_off is None:
            continue  # no header seen yet on this or any prior page -- don't guess

        for m in re.finditer(row_regex, page_text):
            row_idx += 1
            line_start, _ = _line_bounds(page_text, m.start())
            amount_col = m.start(3) - line_start
            direction = "credit" if abs(amount_col - credit_off) < abs(amount_col - debit_off) else "debit"
            snippet = _snippet(page_text, m)
            section = _nearest_section(page_text, m.start(), doc_title)
            cells = {
                "date": m.group(1).strip(),
                "description": m.group(2).strip(),
                "{0}_amount".format(direction): _normalize_decimal(m.group(3)),
                "balance": _normalize_decimal(m.group(4)),
            }
            for col_name, value in cells.items():
                field_name = "{0}_{1:02d}_{2}".format(field_prefix, row_idx, col_name)
                results[field_name] = {
                    "value": value,
                    "citation": {
                        "doc_name": None,
                        "page_num": page_num,
                        "document_title": doc_title,
                        "section": section,
                        "field_label": None,
                        "segment_snippet": snippet,
                    },
                    "doc_confidence": 0.98,
                }
    return results


def extract_pdf_fields(loan_folder: str) -> Dict[str, Dict[str, Any]]:
    """Extract every pattern-matched field from every PDF in one loan's folder.

    Returns {field_name: {"value": str, "citation": {"doc_name", "page_num",
    "segment_snippet", "document_title", "section", "field_label"},
    "doc_confidence": float}} — the DOC (truth) side only. Deterministic
    pattern matching is the only path exercised by these 5 synthetic loans
    (research.md decision #1); no LLM fallback is invoked here.
    """
    patterns = _load_doc_patterns()
    results: Dict[str, Dict[str, Any]] = {}

    pdf_files = sorted(
        f for f in os.listdir(loan_folder)
        if f.lower().endswith(".pdf")
    )
    for filename in pdf_files:
        pattern = _match_doc_type(filename, patterns)
        if pattern is None:
            continue
        full_path = os.path.join(loan_folder, filename)
        pages = _pdf_pages(full_path)
        doc_title = _document_title(pages)

        for field_name, field_def in pattern.get("fields", {}).items():
            if field_name in results:
                # First matching document wins; do not overwrite (no loan in
                # this batch has the same field extractable from two distinct
                # PDFs of the same type).
                continue
            if "count_regex" in field_def:
                found = _extract_count_field(pages, field_def, doc_title)
            else:
                found = _extract_single_field(pages, field_def, doc_title)
            if found is None:
                continue
            value, page_num, snippet, section, label = found
            results[field_name] = {
                "value": value,
                "citation": {
                    "doc_name": filename,
                    "page_num": page_num,
                    "document_title": doc_title,
                    "section": section,
                    "field_label": label,
                    "segment_snippet": snippet,
                },
                # Deterministic, unambiguous label-anchored pattern match against
                # confirmed born-digital text (research.md decision #1) — high,
                # not a hardcoded flat default (research.md decision #6). No LLM
                # fallback path is exercised by these 5 loans, so this value is
                # never anything but this one honest constant on this feature.
                "doc_confidence": 0.98,
            }

        for table_name, table_def in pattern.get("tables", {}).items():
            table_kind = table_def.get("table_type", "simple_row")
            if table_kind == "bank_ledger":
                table_results = _extract_bank_ledger(pages, table_def, doc_title)
            else:
                table_results = _extract_simple_table(pages, table_def, doc_title)
            for field_name, entry in table_results.items():
                if field_name in results:
                    continue  # same "first document wins" rule as single fields
                entry["citation"]["doc_name"] = filename
                results[field_name] = entry
    return results


if __name__ == "__main__":
    import sys
    loan_dirs = sorted(
        d for d in os.listdir(os.path.join(HERE, "..", "..", "..", "demo", "syn"))
        if d.startswith("loan ")
    )
    base = os.path.normpath(os.path.join(HERE, "..", "..", "..", "demo", "syn"))
    for d in loan_dirs:
        folder = os.path.join(base, d)
        fields = extract_pdf_fields(folder)
        print(d, "->", json.dumps(fields, indent=2))
