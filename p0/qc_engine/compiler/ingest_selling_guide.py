"""
Deterministic parser: the real Fannie Mae Selling Guide PDF
(`docs/Selling-Guide_06-03-2026_highlighted.pdf`, 1,188 pages) into
`knowledge_base.py`-compatible `{source_document, citation, content}` dicts,
one per real Guide section (e.g. "B3-4.3-04, Personal Gifts (02/04/2026)").

Zero LLM involvement, by design (`knowledge_base.py`'s own hard constraint:
a KBSection must never be a source of new content, only a citation of
existing content). The Guide's own section numbering (Chapter-Part-Section,
e.g. B3-4.3-04) is regular and well-formed enough to parse structurally --
every section heading is its own line, `<id>, <title> (<MM/DD/YYYY>)`, so
this never needs to interpret meaning to find section boundaries, only to
recognize a fixed textual pattern. `content` is the VERBATIM text between
one heading and the next, after stripping repeated page-footer boilerplate
("Published <date>", bare page numbers) -- never summarized, never
paraphrased, so citing a section always means citing the Guide's own words.

Requires `pdftotext` (poppler-utils) on PATH -- the same tool already used
elsewhere in this project (000-synthetic-fixture-generation's Active
Technologies).

Run: python3 p0/qc_engine/compiler/ingest_selling_guide.py

Python 3.9 compatible.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from typing import Any, Dict, List, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
_P0 = os.path.dirname(os.path.dirname(_HERE))
_REPO_ROOT = os.path.dirname(_P0)
if _P0 not in sys.path:
    sys.path.insert(0, _P0)

from qc_engine.compiler import knowledge_base as KB  # noqa: E402
from qc_engine.compiler import knowledge_base_store as store  # noqa: E402

PDF_PATH = os.path.join(_REPO_ROOT, "docs", "Selling-Guide_06-03-2026_highlighted.pdf")
SOURCE_DOCUMENT = "Fannie Mae Selling Guide (06-03-2026)"
# Central storage location for this project's generated/derived stores --
# repo-root-level, not buried inside p0/qc_engine/compiler/ (matches
# compile_llm.py's _KB_DIR, which reads from this same location).
DB_PATH = os.path.join(_REPO_ROOT, "storage", "knowledge_base", "kb.sqlite3")

# A heading line, once page-break form-feeds are stripped, always starts at
# column 0 with "<id>, ". The revision date "(MM/DD/YYYY)" confirms it's a
# real heading and not an inline body reference ("...see A2-2-03, Document
# Warranties.") -- an inline reference doesn't repeat the revision date.
# Long titles wrap across pdftotext's fixed column width, so the date is
# searched across a short lookahead window, not required on the same line.
# The Guide uses two id shapes -- "B3-4.3-04" (letter+digit) for regular
# sections and "E-3-23" (letter-dash-digit) for the glossary/exhibits --
# the character class covers both. A plain capitalized word ("Note,") can
# also match this loosely, but the mandatory date-suffix confirmation below
# is what actually gates acceptance, so a broader id pattern here doesn't
# introduce false positives, only false CANDIDATES that fail the date check.
_ID_START_RE = re.compile(r'^([A-Z][\w.\-]*\d[\w.\-]*), (.+)$')
_DATE_END_RE = re.compile(r'\((\d{2}/\d{2}/\d{4})\)\s*$')
_MAX_TITLE_LOOKAHEAD_LINES = 3

# Repeated page-footer boilerplate to strip from section bodies -- this is
# formatting noise, not content; stripping it doesn't touch a single word of
# the Guide's actual regulatory text.
_FOOTER_RE = re.compile(r'^Published \w+ \d{1,2}, \d{4}\s*$')
_BARE_PAGE_NUMBER_RE = re.compile(r'^\d{1,4}\s*$')


def _extract_text(pdf_path: str) -> str:
    """pdftotext -layout preserves the Guide's column/heading structure --
    critical for the heading regex above to line up with real section
    starts, not reflowed prose."""
    result = subprocess.run(
        ["pdftotext", "-layout", pdf_path, "-"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.replace("\x0c", "")  # strip PDF page-break markers


def _find_headings(lines: List[str]) -> List[Tuple[int, str, str, str]]:
    """Returns (line_index, section_id, title, revision_date) for every real
    Guide section heading found -- deduplicated to each id's FIRST
    occurrence (a section id can be repeated later in the document as a
    cross-reference heading in an FAQ/appendix; the first occurrence is the
    section's actual home)."""
    headings: List[Tuple[int, str, str, str]] = []
    seen_ids = set()
    i = 0
    while i < len(lines):
        m = _ID_START_RE.match(lines[i])
        if m:
            section_id = m.group(1)
            joined = lines[i].strip()
            for extra in range(_MAX_TITLE_LOOKAHEAD_LINES):
                date_match = _DATE_END_RE.search(joined)
                if date_match:
                    if section_id not in seen_ids:
                        title = joined[len(section_id) + 2:]
                        title = _DATE_END_RE.sub("", title).strip()
                        headings.append((i, section_id, title, date_match.group(1)))
                        seen_ids.add(section_id)
                    break
                if i + extra + 1 >= len(lines):
                    break
                joined = joined + " " + lines[i + extra + 1].strip()
        i += 1
    return headings


def _clean_body(raw_lines: List[str]) -> str:
    kept = []
    for line in raw_lines:
        if _FOOTER_RE.match(line) or _BARE_PAGE_NUMBER_RE.match(line):
            continue
        kept.append(line)
    text = "\n".join(kept)
    # Collapse the runs of blank lines the footer-stripping leaves behind.
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_selling_guide(pdf_path: str = PDF_PATH) -> List[Dict[str, Any]]:
    """Returns one dict per real Guide section, ready for
    `knowledge_base.build_corpus()`: {"source_document", "citation",
    "content"}. `content` is verbatim Guide text, never LLM-touched."""
    raw_text = _extract_text(pdf_path)
    lines = raw_text.split("\n")
    headings = _find_headings(lines)

    documents = []
    for idx, (line_no, section_id, title, revision_date) in enumerate(headings):
        body_start = line_no + 1
        body_end = headings[idx + 1][0] if idx + 1 < len(headings) else len(lines)
        content = _clean_body(lines[body_start:body_end])
        if not content:
            continue  # a heading with no real body text isn't a citable section
        documents.append({
            "source_document": SOURCE_DOCUMENT,
            "citation": f"Fannie Mae Selling Guide {section_id}, {title} ({revision_date})",
            "content": content,
        })
    return documents


def main() -> None:
    documents = parse_selling_guide()
    print(f"parsed {len(documents)} real Guide sections from {PDF_PATH}")

    # "Fannie Mae" -- must exactly match program_gating.py's
    # _PREFIX_TO_PROGRAM value for the O-FNM exception-code prefix, since
    # that's the string compile_row() actually looks up a KB by.
    corpus = KB.build_corpus("Fannie Mae", documents, version=1)
    # Honest placeholder, mirroring 002c's own validation-proof precedent
    # (the FHA stub corpus this replaces used the same pattern) -- this is
    # NOT a real SME sign-off. Real use in a real compile requires Kayla (or
    # another real SME) to review this corpus and re-sign it before it's
    # trusted for grounding.
    corpus = KB.sign(corpus, signed_by="NOT-A-REAL-SME-pending-kayla-review",
                     signed_at="2026-07-26")

    store.save_to_db(corpus, DB_PATH)
    print(f"saved corpus '{corpus.program}' v{corpus.version} "
          f"({len(corpus.sections)} sections) to {DB_PATH}")
    print("STATUS: signed_by is an explicit placeholder -- this corpus is "
          "NOT yet SME-reviewed. It proves the pipeline end-to-end; it is "
          "not yet trustworthy for a real compile.")


if __name__ == "__main__":
    main()
