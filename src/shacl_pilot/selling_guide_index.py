#!/usr/bin/env python3
"""
Selling Guide topic-index builder — the Layer-B grounding corpus (decision 012).

Deterministically parses the Fannie Mae Selling Guide PDF's table of contents into
a topic index: {code, title, effective_date, printed_page, pdf_page}. The topic
code itself encodes the hierarchy (B3-4.2-02 -> part B, subpart B3, chapter B3-4,
section B3-4.2), so the ontology graph is derived, not guessed.

Outputs:
  compiled/selling_guide_index.json   — the queryable index
  compiled/selling_guide_ontology.ttl — same content as an RDF topic graph

Also provides lookup(code) -> full topic text (pdftotext of its page range),
which is what the Layer-2 rule compiler uses to attach REAL guide citations to
AMQ rules instead of un-sourced interpretations.

USAGE:
  python3 selling_guide_index.py build
  python3 selling_guide_index.py lookup B3-4.2-02
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
PDF = os.path.join(REPO, "docs", "Selling-Guide_06-03-2026_highlighted.pdf")
OUT_JSON = os.path.join(HERE, "compiled", "selling_guide_index.json")
OUT_TTL = os.path.join(HERE, "compiled", "selling_guide_ontology.ttl")

TOC_FIRST, TOC_LAST = 3, 13

# topic line: "B3-4.2-02, Depository Accounts (05/04/2022) ..... 123"
TOPIC_RE = re.compile(
    r"^\s*([A-E]\d(?:-\d+(?:\.\d+)?)*-\d{2}),\s+(.+?)\s*"
    r"(?:\((\d{2}/\d{2}/\d{4})\))?\s*\.{4,}\s*(\d+)\s*$")


def pdf_text(first, last):
    return subprocess.run(
        ["pdftotext", "-f", str(first), "-l", str(last), "-layout", PDF, "-"],
        capture_output=True, text=True, check=True).stdout


def parse_toc():
    """Parse TOC pages; join wrapped entries before matching."""
    raw = pdf_text(TOC_FIRST, TOC_LAST)
    # join wrapped lines: a topic entry may wrap before its dotted page number
    joined, buf = [], ""
    for line in raw.splitlines():
        if not line.strip():
            continue
        buf = (buf + " " + line.strip()) if buf else line
        if re.search(r"\.{4,}\s*[\dIVXLC]+\s*$", buf):
            joined.append(buf)
            buf = ""
        elif re.match(r"^\s*(Part [A-E]|Subpart|Chapter|Section|Preface)", line):
            joined.append(line)
            buf = ""
        elif len(buf) > 400:
            buf = ""
    topics = []
    for line in joined:
        m = TOPIC_RE.match(line)
        if m:
            code, title, eff, page = m.groups()
            topics.append({"code": code, "title": re.sub(r"\s+", " ", title),
                           "effective_date": eff, "printed_page": int(page)})
    return topics


def find_page_offset(topics):
    """Printed page N lives at PDF page N + offset; locate via first topic."""
    first = topics[0]
    probe_text = first["code"] + ", "
    for pdf_page in range(TOC_LAST + 1, TOC_LAST + 30):
        txt = pdf_text(pdf_page, pdf_page)
        if probe_text in txt and not re.search(r"\.{4,}", txt):
            return pdf_page - first["printed_page"]
    raise SystemExit("Could not locate page offset for %s" % first["code"])


def hierarchy_of(code):
    part = code[0]
    subpart = code.split("-")[0]
    bits = code.split("-")
    chapter = "-".join(bits[:2]).split(".")[0]
    section = "-".join(bits[:-1])
    return part, subpart, chapter, section


def build():
    topics = parse_toc()
    offset = find_page_offset(topics)
    for i, t in enumerate(topics):
        t["pdf_page"] = t["printed_page"] + offset
        nxt = topics[i + 1]["printed_page"] + offset if i + 1 < len(topics) else None
        t["pdf_page_end"] = nxt if nxt and nxt >= t["pdf_page"] else t["pdf_page"]
        part, subpart, chapter, section = hierarchy_of(t["code"])
        t.update({"part": part, "subpart": subpart,
                  "chapter": chapter, "section": section})
    index = {"source_pdf": os.path.basename(PDF), "pages": 1188,
             "page_offset": offset, "topics_total": len(topics),
             "topics": topics}
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(index, f, indent=1, sort_keys=True)

    # RDF topic graph (authoring-time artifact; codes are IRI-safe)
    lines = ["@prefix sg: <http://mortgage.audit.ontology/selling-guide#> .",
             "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .", ""]
    for t in topics:
        iri = "sg:" + t["code"].replace(".", "_")
        title = t["title"].replace('"', "'")
        lines.append('%s a sg:GuideTopic ; rdfs:label "%s" ; sg:code "%s" ; '
                     'sg:effectiveDate "%s" ; sg:pdfPage %d ; sg:partOfSection "%s" ; '
                     'sg:partOfChapter "%s" ; sg:partOfSubpart "%s" .'
                     % (iri, title, t["code"], t["effective_date"] or "",
                        t["pdf_page"], t["section"], t["chapter"], t["subpart"]))
    with open(OUT_TTL, "w") as f:
        f.write("\n".join(lines) + "\n")

    print("Indexed %d topics (page offset %+d) -> %s"
          % (len(topics), offset, os.path.relpath(OUT_JSON, HERE)))
    return index


def lookup(code):
    with open(OUT_JSON) as f:
        index = json.load(f)
    hits = [t for t in index["topics"] if t["code"] == code]
    if not hits:
        # prefix search fallback
        hits = [t for t in index["topics"] if t["code"].startswith(code)]
    if not hits:
        raise SystemExit("No topic %s in index" % code)
    t = hits[0]
    text = pdf_text(t["pdf_page"], min(t["pdf_page_end"], t["pdf_page"] + 6))
    return t, text


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    if cmd == "build":
        build()
    elif cmd == "lookup":
        t, text = lookup(sys.argv[2])
        print("%(code)s — %(title)s (eff. %(effective_date)s, PDF p.%(pdf_page)d)" % t)
        print("-" * 70)
        print(text[:3000])
