"""
002c real proof: builds a small, real FHA knowledge base, grounds one real
compile call against it, runs the judge panel, screens referential
integrity, and -- only if everything clears -- assembles and signs a real
`Ruleset`. Mirrors experiment_002a's precedent (a real, standalone,
non-throwaway proof kept outside the fast pytest suite, since it makes
real Bedrock calls) and matches spec.md US5's full acceptance criterion:
the end state must be "a signed, version-locked ruleset with full
provenance from source document through KB grounding through judge
verdicts to SME sign-off" -- not just the grounded-compile-and-judge steps
alone (an earlier version of this script stopped there; corrected here,
see RESULTS.md's own note on that).

Intentionally scoped to ONE program (FHA), one real row, and a handful of
real regulatory excerpts -- NOT the full 6-program corpus, which is a
separate, larger, cost-incurring operation requiring its own explicit
go-ahead (plan.md Scale/Scope). This proves the mechanism, including the
steps a prior version of this script skipped; it is not the production
KB-build/compile run.

Usage (from p0/, with AWS credentials configured):
    python3 experiment_002c/build_fha_kb.py
Writes RESULTS.md alongside this script -- the run's actual output,
persisted, not left as chat-only stdout.
Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict

HERE = os.path.dirname(os.path.abspath(__file__))
P0 = os.path.dirname(HERE)
sys.path.insert(0, P0)

from qc_engine.catalog import FieldCatalog, FieldCatalogEntry, ReferentialIntegrityError, \
    validate_referential_integrity
from qc_engine.compiler import compile_llm as C
from qc_engine.compiler import intake as I
from qc_engine.compiler import judge_panel as J
from qc_engine.compiler import knowledge_base as KB

FHA_GIFT_FUNDS_DOCUMENTS = [
    {
        "source_document": "HUD Handbook 4000.1, II.A.4.d.iv (Gifts)",
        "citation": "hud.gov/4000.1",
        "content": (
            "A gift may be provided by the borrower's family member, employer, labor union, "
            "close friend, charitable organization, or government agency. The gift must be "
            "evidenced by a gift letter, signed and dated by the donor and borrower, that "
            "specifies the dollar amount, states no repayment is required, and shows the "
            "donor's and borrower's names, addresses, telephone numbers, and the relationship "
            "of the donor to the borrower. The gift letter must be dated at or before closing "
            "and retained in the loan file."
        ),
    },
    {
        "source_document": "HUD Handbook 4000.1, II.A.4.d.iv (Verification of Gift Funds)",
        "citation": "hud.gov/4000.1",
        "content": (
            "The Mortgagee must verify and document the transfer of gift funds from the "
            "donor to the borrower, including evidence of the donor's ability and willingness "
            "to provide the gift (e.g. a bank statement showing sufficient funds and a "
            "withdrawal) and evidence the funds were transferred to the borrower's account "
            "or directly to the closing agent."
        ),
    },
]

REAL_ROW = {
    "row_id": "fha-gift-000", "qcode": "O-FHA-15206", "category": "Assets",
    "defect_text": ("Signed and dated gift letter not in the file or the letter "
                    "did not include all required information"),
    "engine_kind": "predicate", "significance": "Critical",
    "exception_code": "O-FHA-02257", "sql_criteria": "",
}


def run_intake_demo(program: str = "FHA", row: Dict[str, Any] = None) -> Dict[str, Any]:
    """The reusable orchestration function T032 originally called for --
    all 10 spec.md US5 steps, in order. Returns a full result dict; never
    silently stops partway through. `signed_by` values below are
    explicitly labeled as a stand-in for a real SME, matching 002a's own
    disclosure discipline when Claude stood in for Kayla -- never silently
    presented as a real human sign-off."""
    row = row or REAL_ROW
    result: Dict[str, Any] = {"steps": []}

    # Step 1: classify & gate (FR-011) -- halts here if unknown, never proceeds silently.
    I.classify_and_gate("HUD_HANDBOOK_EXCERPT", {"HUD_HANDBOOK_EXCERPT", "AMQ_WORKBOOK"})
    result["steps"].append("1_intake_gate: PASSED (known document type)")

    # Step 2 (+3, incremental-update path exists but unused on a first build):
    # build & sign the program KB.
    corpus = KB.sign(
        KB.build_corpus(program, FHA_GIFT_FUNDS_DOCUMENTS, version=1),
        signed_by="claude-standin-not-kayla@this-proof-script", signed_at="2026-07-20T00:00:00Z",
    )
    kb_path = os.path.join(C._KB_DIR, program, "v1.json")
    KB.save(corpus, kb_path)
    result["steps"].append(f"2_kb_build_and_sign: v{corpus.version}, {len(corpus.sections)} sections -> {kb_path}")

    # Step 5: grounded extraction -- a real Bedrock call.
    client = C._client()
    catalog = FieldCatalog(catalog_id="proof-catalog", version=1, entries=[])
    draft = C.compile_row(client, row, catalog)
    result["compiled_check"] = draft.check.to_dict() if draft.check else None
    result["grounding"] = (
        {"kb_program": draft.grounding.kb_program, "kb_version": draft.grounding.kb_version,
         "section_ids": draft.grounding.section_ids} if draft.grounding else None
    )
    result["steps"].append(f"5_grounded_extraction: {'OK' if draft.check else 'FAILED: ' + str(draft.parse_error)}")
    if draft.check is None:
        result["final_outcome"] = "FAILED_AT_EXTRACTION"
        return result

    # Step 6: multi-model judge panel -- 2 real judge calls.
    grounding_text = ""
    if draft.grounding:
        sections = [s for s in corpus.sections if s.id in draft.grounding.section_ids]
        grounding_text = "\n".join(f"- ({s.source_document}) {s.content}" for s in sections)
    verdicts = [J.judge_check(client, draft.check.to_dict(), draft.source_text, grounding_text, m)
               for m in J.DEFAULT_JUDGE_MODELS]
    judge_result = J.judge_batch_result(verdicts)
    result["judge_verdicts"] = judge_result["verdicts"]
    result["steps"].append(f"6_judge_panel: {judge_result['outcome']}")

    # Step 7: referential-integrity screen (existing 002b mechanism) --
    # add any proposed new field first, exactly what a real intake run
    # would need to do before validating.
    if draft.proposed_field_entry:
        catalog = FieldCatalog(catalog_id=catalog.catalog_id, version=catalog.version,
                               entries=catalog.entries + [draft.proposed_field_entry])
    from qc_engine.ruleset import Ruleset
    candidate_ruleset = Ruleset(ruleset_id="proof-002c-fha", version=1, checks=[draft.check])
    try:
        validate_referential_integrity(candidate_ruleset, catalog)
        integrity_ok = True
        result["steps"].append("7_integrity_screen: PASSED")
    except ReferentialIntegrityError as e:
        integrity_ok = False
        result["steps"].append(f"7_integrity_screen: BLOCKED -- {e}")

    # Step 8: route to exception queue if judge escalated OR integrity failed;
    # otherwise proceed to sign-off. Never silently skip this branch.
    needs_sme_review = (judge_result["outcome"] == "ESCALATED") or (not integrity_ok)
    result["steps"].append(f"8_exception_routing: {'NEEDS_SME_REVIEW' if needs_sme_review else 'AUTO_APPROVED_NO_REVIEW_NEEDED'}")

    if needs_sme_review:
        result["final_outcome"] = "ROUTED_TO_SME_EXCEPTION_QUEUE"
        result["steps"].append("9_sign_off: SKIPPED (exception queue, not auto-approved)")
        result["steps"].append("10_deploy: SKIPPED")
        return result

    # Step 9: sign-off & version-lock -- assembles a real, signed Ruleset.
    signed_ruleset = C.assemble_ruleset(
        [draft], ruleset_id="proof-002c-fha", version=1,
        signed_by="claude-standin-not-kayla@this-proof-script", signed_at="2026-07-20T00:00:00Z",
    )
    result["steps"].append(f"9_sign_off: signed, sha256={signed_ruleset.sha256()}")
    result["signed_ruleset_sha256"] = signed_ruleset.sha256()
    result["signed_ruleset"] = signed_ruleset.canonical_content()

    # Step 10: deploy-ready -- this proof stops short of actually deploying
    # (that's the engine's own run(), out of this feature's scope); the
    # signed, version-locked ruleset object existing IS the deliverable
    # spec.md US5's acceptance scenario names.
    result["steps"].append("10_deploy: signed ruleset is deploy-ready (not deployed by this proof script)")
    result["final_outcome"] = "SIGNED_RULESET_READY"
    return result


def _write_results_md(result: Dict[str, Any], path: str) -> None:
    lines = [
        "# 002c Real Proof — Results",
        "",
        "**Status: PROVISIONAL — Claude stood in for Kayla's sign-off (labeled explicitly in the "
        "signed_by field, never silently presented as a real SME).** This is a real, end-to-end "
        "run against real Bedrock calls and real HUD Handbook text, not a synthetic test.",
        "",
        "**Correction disclosed**: an earlier version of this script stopped after the judge panel "
        "(steps 1-6 of spec.md US5's 10-step sequence) and was reported as \"the full workflow\" -- "
        "it wasn't. This run adds the referential-integrity screen, exception-queue routing, and "
        "actual Ruleset sign-off (steps 7-10), closing that gap.",
        "",
        "## Sequence",
        "",
    ]
    for step in result["steps"]:
        lines.append(f"- {step}")
    lines.append("")
    lines.append(f"## Final outcome: `{result['final_outcome']}`")
    lines.append("")
    lines.append("## Full result")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(result, indent=2, default=str))
    lines.append("```")
    with open(path, "w") as f:
        f.write("\n".join(lines))


def main() -> None:
    result = run_intake_demo()
    print(json.dumps(result, indent=2, default=str))
    results_path = os.path.join(HERE, "RESULTS.md")
    _write_results_md(result, results_path)
    print(f"\n[written] {results_path}")


if __name__ == "__main__":
    main()
