"""
Step 4 of the 002a compile-fidelity spike: assemble the SME (Kayla) review
package, per specs/002a-compile-fidelity-spike/contracts/sme-review-package.md.

Produces a markdown table (source condition side-by-side with the compiled
rule's plain-English restatement) with empty verdict/correction/reviewer_note
columns for Kayla to fill in. This step has a human dependency this script
cannot complete -- it prepares the artifact, it does not judge interpretation
fidelity itself.

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> int:
    with open(os.path.join(HERE, "artifacts", "compiled_drafts.json")) as fh:
        compiled = json.load(fh)
    with open(os.path.join(HERE, "artifacts", "scored_drafts.json")) as fh:
        scores = {s["row_id"]: s for s in json.load(fh)["scores"]}

    lines = [
        "# 002a Compile-Fidelity Spike — SME Review Package",
        "",
        "**For: Kayla.** For each row, read `source_question` + `source_response` "
        "(the real AMQ workbook text) and judge whether `plain_english_restatement` "
        "correctly captures what that response means -- **not** whether the "
        "`constructed_label_score` passed (that only tests internal consistency, "
        "not whether the rule reads the row correctly; a rule can pass that and "
        "still misread the row's intent).",
        "",
        "Fill in **verdict** (correct / incorrect / ambiguous), **correction** "
        "(if not correct), and **reviewer_note** (optional) for every row.",
        "",
    ]

    for d in compiled["drafts"]:
        row_id = d["row_id"]
        src = d["_source_row"]
        s = scores.get(row_id, {})
        lines.append(f"## {row_id}  ({src['archetype_id']} / {src['engine_kind']})")
        lines.append("")
        lines.append(f"- **source_category**: {src.get('category', '')}")
        lines.append(f"- **source_qcode**: {src.get('qcode', '')}")
        lines.append(f"- **source_response** (the actual defect condition text): "
                     f"{src['defect_text']}")
        lines.append(f"- **plain_english_restatement** (what the compiled rule "
                     f"says it does): {d.get('plain_english_restatement', '')}")
        lines.append(f"- **constructed_label_score** (context only, not the "
                     f"answer): {s.get('constructed_label_score', 'n/a')}"
                     + (f" -- {s['error']}" if s.get('error') else ""))
        lines.append("- **verdict**: _[correct / incorrect / ambiguous]_")
        lines.append("- **correction**: _[if not correct]_")
        lines.append("- **reviewer_note**: _[optional]_")
        lines.append("")

    out_path = os.path.join(HERE, "artifacts", "sme_review_package.md")
    with open(out_path, "w") as fh:
        fh.write("\n".join(lines))
    print(f"SME review package ({len(compiled['drafts'])} rows) -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
