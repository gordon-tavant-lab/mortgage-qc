"""
export_qc_results_xlsx.py -- quick, one-off Excel export of QC engine run
results, for Kayla to review in a tool she's already familiar with (per
Gordon's explicit direction: "quick script now," not a full spec'd feature
-- see conversation history 2026-07-16/17).

Runs the 5 document-derived synthetic loan fixtures through the per-loan
gated defects_ruleset_for() (p0/fixtures/ruleset_defects.py -- the most
complete real-defect-tied ruleset currently available), and writes one
workbook with two sheets:

  Summary      -- one row per loan: disposition (004), review_reasons (why a
                  human needs to look), and pass/fail/flag counts.
  Check Detail -- one row per (loan, check), rich enough for a human reviewer
                  to actually adjudicate the verdict without opening the
                  engine: the RULE (what question it's asking, and what
                  answer it requires to pass), the raw inputs by source
                  (document/truth vs system-of-record), the value the engine
                  actually compared, the verdict, and why. Revised 2026-07-17
                  after Gordon's explicit feedback that the first version
                  (verdict + message only) didn't give Kayla enough to
                  independently check the engine's work.

This is intentionally NOT wired into p0/tests/ or governed by the
zero-regression digest -- it's a reporting/consumption script over the
already-proven engine output, not engine logic itself. Re-run any time the
fixtures/ruleset change; nothing here is cached or persisted beyond the one
output file.

Usage (from repo root):  python3 p0/export_qc_results_xlsx.py
Python 3.9 compatible. Requires openpyxl (already present in this env).
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "fixtures", "from_docs"))

from qc_engine import run  # noqa: E402
from build_fixtures import build_all_fixtures  # noqa: E402
from fixture_loader import load_canonical_loan  # noqa: E402
from fixtures.ruleset_defects import defects_ruleset_for  # noqa: E402

OUTPUT_PATH = os.path.join(REPO_ROOT, "output", "QC_Engine_Results_for_Kayla_Review.xlsx")


def _rule_question_and_expected(chk):
    """Plain-language: what is this rule actually asking, and what answer
    does it require to PASS? Derived from the Check's own authored fields
    (kind/predicate/ratio/threshold/operator/normalizer/tolerance) -- the
    same fields the engine itself evaluates, not a separate description that
    could drift from what the code actually does."""
    if chk.kind == "predicate":
        if chk.predicate == "is_true":
            return (f"Is '{chk.field_name}' TRUE (e.g. signed / present / documented)?",
                    "TRUE")
        if chk.predicate == "is_present":
            return (f"Is '{chk.field_name}' present (not blank)?", "present / non-blank")
        return (chk.name, "")
    if chk.kind == "ratio_threshold":
        if chk.ratio == "ltv":
            return (f"Is LTV {chk.operator} {chk.threshold}%?", f"{chk.operator} {chk.threshold}%")
        if chk.ratio == "dti":
            return (f"Is DTI {chk.operator} {chk.threshold}%?", f"{chk.operator} {chk.threshold}%")
        if chk.ratio == "field_value":
            return (f"Is '{chk.field_name}' {chk.operator} {chk.threshold}?",
                    f"{chk.operator} {chk.threshold}")
        return (chk.name, "")
    if chk.kind in ("agree_categorical", "agree_numeric"):
        tol = f" (within tolerance {chk.tolerance})" if chk.kind == "agree_numeric" else ""
        return (f"Does '{chk.field_name}' agree between the closing document (truth) "
                f"and the system of record{tol}?", "document value == system value")
    return (chk.name, "")


def _doc_and_system_values(chk, r):
    """Splits CheckResult.inputs (shape varies by check kind -- see
    engine.py's _eval_check) into (truth/document value, system-of-record
    value) columns a reviewer can compare side by side. Blank, not fabricated,
    when a kind has no system-side input at all (predicate/field_value are
    doc-only by construction)."""
    inputs = r.inputs or {}
    if chk.kind in ("agree_categorical", "agree_numeric"):
        return (inputs.get("doc", ""), inputs.get("system", ""))
    if chk.kind == "predicate":
        return (inputs.get("doc", ""), "")
    if chk.kind == "ratio_threshold":
        if chk.ratio == "field_value":
            return (inputs.get(chk.field_name, ""), "")
        # ltv/dti: inputs holds the raw components (loan_amount/property_value
        # or monthly_debts/monthly_income), all doc-truth-derived facts.
        return (", ".join(f"{k}={v}" for k, v in inputs.items()), "")
    return ("", "")


def _collect_rows():
    """Runs every loan fixture through its own gated ruleset; returns
    (summary_rows, detail_rows) as lists of dicts, ready for a DataFrame."""
    summary_rows = []
    detail_rows = []

    written = build_all_fixtures()
    for loan_folder, path in sorted(written.items()):
        loan = load_canonical_loan(path)
        rs = defects_ruleset_for(loan)
        res = run(loan, rs)
        checks_by_id = {c.id: c for c in rs.checks}

        summary_rows.append({
            "Loan ID": loan.loan_id,
            "Loan Type": loan.loan_type,
            "Disposition": res.disposition,
            "Review Reasons (why)": ", ".join(sorted(res.review_reasons)) or "(none)",
            "Auto-Cleared": res.auto_cleared,
            "Total Checks Run": len(res.results),
            "Pass": sum(1 for r in res.results if r.status == "PASS"),
            "Fail": sum(1 for r in res.results if r.status == "FAIL"),
            "Warning": sum(1 for r in res.results if r.status == "WARNING"),
            "Flag (info only)": len(res.flags),
            "Needs Review": len(res.needs_review),
            "Not Applicable": sum(1 for r in res.results if r.status == "NOT_APPLICABLE"),
        })

        for r in res.results:
            chk = checks_by_id[r.check_id]
            citation = r.citation or {}
            question, expected = _rule_question_and_expected(chk)
            doc_value, system_value = _doc_and_system_values(chk, r)

            detail_rows.append({
                "Loan ID": loan.loan_id,
                "Loan Type": loan.loan_type,
                "Check ID": r.check_id,
                "Rule / Check Name": r.check_name,
                "Rule Question": question,
                "Check Kind": chk.kind,
                "Field": r.field_name,
                "Expected (to PASS)": expected,
                "Truth (Document/PDF/XML)": doc_value,
                "System of Record (LOS/MISMO)": system_value,
                "Actual Value Compared": r.compared_value if r.compared_value is not None else "",
                "Verdict": r.status,
                "Review Reason (why NEEDS_REVIEW)": r.review_reason or "",
                "Severity": r.severity,
                "Explanation (why this verdict)": r.message,
                "Doc Confidence": r.doc_confidence if r.doc_confidence is not None else "",
                # DocCitation.to_dict() (model.py) uses camelCase keys, and
                # document_title/section/field_label are only emitted when
                # populated (preserves harness.py's digest for golden.py's
                # own citations -- see model.py's own comment) -- .get()
                # with the exact camelCase names, not a snake_case guess.
                "Source Document": citation.get("docName", ""),
                "Page": citation.get("pageNum", ""),
                "Document Title": citation.get("documentTitle", ""),
                "Document Section": citation.get("section", ""),
                "Field Label (as printed on doc)": citation.get("fieldLabel", ""),
                "Cited Text Segment": citation.get("segmentSnippet", ""),
            })

    return summary_rows, detail_rows


def _autosize_and_filter(ws, df):
    """Freeze header row, add autofilter, and size columns to their content
    -- the minimum polish that makes a spreadsheet actually usable in Excel,
    not just technically an .xlsx file."""
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for col_idx, col_name in enumerate(df.columns, start=1):
        max_len = max(
            [len(str(col_name))] + [len(str(v)) for v in df[col_name].astype(str)]
        )
        ws.column_dimensions[ws.cell(row=1, column=col_idx).column_letter].width = min(
            max(max_len + 2, 10), 60)


def main():
    import pandas as pd

    summary_rows, detail_rows = _collect_rows()
    summary_df = pd.DataFrame(summary_rows)
    detail_df = pd.DataFrame(detail_rows)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with pd.ExcelWriter(OUTPUT_PATH, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        detail_df.to_excel(writer, sheet_name="Check Detail", index=False)
        _autosize_and_filter(writer.sheets["Summary"], summary_df)
        _autosize_and_filter(writer.sheets["Check Detail"], detail_df)

    print(f"Wrote {len(summary_rows)} loan(s), {len(detail_rows)} check row(s) -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
