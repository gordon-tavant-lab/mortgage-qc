"""
002f T002: one-off extraction of the real Retail workbook's Post-Closing
sheet into a checked-in JSON fixture, so `p0/tests/test_ontology_extraction.py`
doesn't re-parse the live `.xlsx` on every run (mirrors the convention other
specs' fixtures already follow -- derived from `demo/rules/*.xlsx` once).

Captures every column Layer 0/1 need, including "Question Criteria by
Questions" (column 13), which `p0/eval_synth/taxonomy.py`'s existing
`load_rows()` does not read at all -- that omission is exactly why this
spec's Layer 0 didn't already exist as a byproduct of 010a's SQL-gating work.

Run once: `python3 p0/fixtures/ontology_extraction/build_fixture.py`

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os

import openpyxl

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
_XLSX_PATH = os.path.join(_REPO_ROOT, "demo", "rules", "PF and PC Sept 2025 AMQs - Retail.xlsx")
_OUT_PATH = os.path.join(_HERE, "retail_post_closing_rows.json")

_QUESTIONNAIRE_NAME = "Post-Closing AMQ Sept 2025 audits"


def extract() -> list:
    wb = openpyxl.load_workbook(_XLSX_PATH, read_only=True, data_only=True)
    ws = wb.worksheets[0]
    rows = []
    idx = 0
    for r in ws.iter_rows(min_row=5, values_only=True):
        if not r or len(r) < 14:
            continue
        if r[0] != _QUESTIONNAIRE_NAME:
            continue
        rows.append({
            "row_id": f"pc-retail-{idx:05d}",
            "category": r[1],
            "qcode": r[4],
            "question_text": r[5],
            "defect_text": str(r[6] or ""),
            "sql_criteria": str(r[7] or ""),
            "exception_code": r[8],
            "significance": r[9],
            "question_criteria_by_q": str(r[13] or "") if r[13] else "",
        })
        idx += 1
    wb.close()
    return rows


def main() -> None:
    rows = extract()
    with open(_OUT_PATH, "w") as f:
        json.dump(rows, f, indent=2)
    with_col13 = sum(1 for r in rows if r["question_criteria_by_q"])
    print(f"wrote {len(rows)} rows ({with_col13} with question_criteria_by_q) to {_OUT_PATH}")


if __name__ == "__main__":
    main()
