"""Deterministic Selling Guide splitter: outline -> per-section text + index.

Pre-extracts every page's text once, then slices by outline page ranges.
Outputs guide/sections/<section_id>.txt and guide/index.json.
"""
import json
import re
import time
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'source' / 'selling-guide-2026-06-03.pdf'
OUT = ROOT / 'guide'
SEC_RE = re.compile(r'^([A-E]\d[\d.\-]*-\d{2}),\s*(.*?)(?:\s*\((\d{2}/\d{2}/\d{4})\))?$')


def main():
    t0 = time.time()
    r = PdfReader(SRC)
    n = len(r.pages)

    entries = []

    def walk(items, depth=0):
        for it in items:
            if isinstance(it, list):
                walk(it, depth + 1)
            else:
                try:
                    pg = r.get_destination_page_number(it)
                except Exception:
                    pg = None
                entries.append({'title': str(it.title).strip(), 'depth': depth, 'page': pg})

    walk(r.outline)
    print(f"outline entries: {len(entries)}; pages: {n}")

    pages = []
    for i, pg in enumerate(r.pages):
        try:
            pages.append(pg.extract_text() or '')
        except Exception as e:
            pages.append(f'[extract error p{i + 1}: {e}]')
        if (i + 1) % 200 == 0:
            print(f"  extracted {i + 1}/{n} pages ({time.time() - t0:.0f}s)")

    (OUT / 'sections').mkdir(parents=True, exist_ok=True)
    index = []
    for i, e in enumerate(entries):
        m = SEC_RE.match(e['title'])
        if not m or e['page'] is None:
            continue
        sec_id, title, eff = m.group(1), m.group(2), m.group(3)
        end = n - 1
        for j in range(i + 1, len(entries)):
            pj = entries[j]['page']
            if pj is not None and pj >= e['page']:
                end = min(n - 1, pj)  # inclusive: boundary page may hold section tail
                break
        text = '\n'.join(pages[e['page']:end + 1])
        fn = sec_id.replace('.', '_') + '.txt'
        (OUT / 'sections' / fn).write_text(
            f"SECTION: {sec_id}\nTITLE: {title}\nEFFECTIVE: {eff}\nPAGES: {e['page'] + 1}-{end + 1}\n---\n{text}")
        index.append({'section_id': sec_id, 'title': title, 'effective_date': eff,
                      'page_start': e['page'] + 1, 'page_end': end + 1, 'file': f'sections/{fn}',
                      'char_count': len(text)})

    (OUT / 'index.json').write_text(json.dumps(index, indent=1))
    print(f"sections written: {len(index)} in {time.time() - t0:.0f}s")


if __name__ == '__main__':
    main()
