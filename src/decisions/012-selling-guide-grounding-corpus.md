# 012 — Selling Guide topic-index ontology as the Layer-B grounding corpus

**Status:** Accepted 2026-07-29 (Gordon asked whether an ontology of the Selling Guide
PDF would improve rule understanding; answer: yes, in this specific form)

## Decision
Build a **citable topic index** of the Fannie Mae Selling Guide
(`docs/Selling-Guide_06-03-2026_highlighted.pdf`, 1,188 pp) rather than attempting a
semantic OWL model of the regulation text. `selling_guide_index.py` deterministically
parses the TOC into **386 topics** {code, title, effective date, printed page, PDF
page}, derives the Part/Subpart/Chapter/Section hierarchy **from the topic code
itself** (B3-4.2-02 → B / B3 / B3-4 / B3-4.2), and emits both a JSON index and an RDF
topic graph (`compiled/selling_guide_ontology.ttl`). `lookup(code)` returns the topic's
actual page text.

## Why index, not semantic model
The rules-clarity review (session 2026-07-29) showed the AMQ workbook presumes the
guide: only 1 of 4,167 rules cites a section. What closes that gap is *retrieval with
citations* — every compiled rule interpretation must point at the guide text an SME
can read beside it. Formalizing the guide's *meaning* into OWL axioms would re-create
the untraceable-interpretation problem one level down and violate the grounding
discipline (research interprets and cites; it never originates conditions).

## Proven leverage (first use, same day)
`lookup("B3-4.2-02")` → "A large deposit is defined as a single deposit that exceeds
50% of the total monthly qualifying income" — the real source of AMQ O-FNM-15334's 50%
threshold, now attached to `LargeDepositShape` as `caro:guideCitation`. The same page
also revealed a precondition the AMQ row never states: **large-deposit documentation
is not required for refinance transactions** — a purchase-only gate to add pending SME
confirmation. That discovery is exactly the "improved understanding" the corpus is for.

## How Layer-2 uses it
The rule compiler (decision 009) retrieves candidate topics per rule (keyword/section
retrieval from this index; LLM proposes the linkage at compile time), quotes the
governing sentence, and refuses to compile a threshold that no retrieved text supports
("UNSPECIFIED — needs SME"). SME reviews rule + quoted guide text side by side.

## Limits (stated, not hidden)
- Covers **Fannie Mae only** — grounds the 1,352 O-FNM+generic rules. FHA (HUD 4000.1),
  VA (Lenders Handbook), Freddie (Seller/Servicer Guide), USDA (HB-1-3555) need the
  same treatment; same builder pattern applies if PDFs are obtained.
- The guide is © Fannie Mae, licensed for mortgage professionals' own use — internal
  grounding is fine; do not redistribute extracted text externally.
- Topic text extraction is page-ranged (topic start to next topic), good enough for
  citation display; fine-grained anchor (paragraph) can come later.
