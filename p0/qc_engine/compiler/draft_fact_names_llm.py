"""
The one LLM step in fact-vocabulary self-discovery: DRAFT names for the
24 deterministically-discovered candidates (`discover_fact_candidates.py`).

Everything upstream of this script is deterministic (decoded questions, real
answer vocabularies, Guide/catalog suggestions). Naming is the one step that
is genuinely semantic -- "gift_funds_used" is content someone must own -- so
it follows 002f's trust-tier discipline exactly:

  - LLM output here is MEDIUM_SME_REVIEW tier: it lands in a REVIEW ARTIFACT
    (`naming_proposals_v1.json` + a Kayla-facing markdown table), and is
    NEVER loaded by the resolver, the compiler, or anything else. The signed
    vocabulary (`v<N>.json`) changes only when a human promotes a proposal.
  - The prompt enforces honest abstention: every real answer must be either
    mapped or explicitly listed as unmapped-with-reason -- a dropped answer
    is a validation failure, not a silent gap. NEVER invent an answer string.
  - One-time compile-time cost (24 small calls, Sonnet, temp=0) -- zero
    runtime LLM, per Non-Negotiable #1.

Run: python3 p0/qc_engine/compiler/draft_fact_names_llm.py
Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_P0 = os.path.dirname(os.path.dirname(_HERE))
_REPO_ROOT = os.path.dirname(_P0)
if _P0 not in sys.path:
    sys.path.insert(0, _P0)

from qc_engine.compiler import compile_llm  # noqa: E402  (reuses _client/MODEL_SONNET)
from qc_engine.compiler import fact_vocabulary as FV  # noqa: E402

CANDIDATES_PATH = os.path.join(_REPO_ROOT, "storage", "fact_vocabulary",
                               "candidates", "v1.json")
CATALOG_PATH = os.path.join(_P0, "qc_engine", "field_catalog.json")
OUT_JSON = os.path.join(_REPO_ROOT, "storage", "fact_vocabulary", "candidates",
                        "naming_proposals_v1.json")
OUT_MD = os.path.join(_REPO_ROOT, "output",
                      "FACT-VOCABULARY-NAMING-PROPOSALS-2026-07-26.md")

SYSTEM_PROMPT = """You are drafting canonical loan-fact NAMES for a mortgage \
post-closing QC engine's fact vocabulary. You receive one decoded question from \
the client's own rule workbook: its real answer strings, the question texts of \
the rules it gates, and (as hints only) suggested existing catalog fields and \
Selling Guide sections.

Propose one or more canonical facts that this question's answers assert about a \
loan. Rules, non-negotiable:
1. NEVER invent an answer string. Every answer I give you must appear EXACTLY \
ONCE across your facts' answer_value_map keys, OR in unmapped_answers with a \
one-phrase reason. Verbatim strings only.
2. A fact's proposed_field_name is snake_case, loan-side, and describes what is \
TRUE OF THE LOAN (e.g. gift_funds_used), never the question mechanics.
3. If several answers are variants of one underlying fact value, map them to \
the same canonical_value. If answers describe genuinely different facts (e.g. \
different income types), propose SEPARATE facts, each owning its answers.
4. data_type is one of: boolean, enum, string, decimal, date. For boolean, \
canonical values are "true"/"false". For enum, canonical values are short \
snake_case tokens.
5. If you are not confident an answer maps cleanly, put it in unmapped_answers \
-- honest abstention beats a plausible guess. Under-mapping is the safe \
failure mode.
6. reuse_catalog_field: if one of the suggested catalog fields IS this fact, \
name it; else null.

Output ONLY a JSON object (no markdown fences):
{
  "facts": [
    {"proposed_field_name": "...", "data_type": "...", "description": "<one sentence>",
     "answer_value_map": {"<verbatim answer>": "<canonical value>", ...},
     "reuse_catalog_field": "<field_name or null>",
     "confidence": "high|medium|low", "rationale": "<one sentence>"}
  ],
  "unmapped_answers": {"<verbatim answer>": "<one-phrase reason>"}
}
"""


def _validate(candidate, parsed):
    """Every real answer accounted for exactly once; no invented answers."""
    real = set(candidate["answer_vocabulary"])
    seen = []
    for fact in parsed.get("facts", []):
        seen.extend(fact.get("answer_value_map", {}).keys())
    seen.extend(parsed.get("unmapped_answers", {}).keys())
    if sorted(seen) != sorted(set(seen)):
        raise ValueError("an answer is mapped more than once")
    if set(seen) != real:
        missing = real - set(seen)
        invented = set(seen) - real
        raise ValueError(f"missing={sorted(missing)[:3]} invented={sorted(invented)[:3]}")
    return parsed


def _call_one(client, candidate, max_retries=2):
    user_msg = json.dumps({
        "question_key": candidate["question_key"],
        "answers": candidate["answer_vocabulary"],
        "gated_rule_question_texts": candidate["top_dependent_question_texts"],
        "dependent_row_count": candidate["dependent_row_count"],
        "suggested_catalog_fields": [s["field_name"]
                                     for s in candidate["catalog_field_suggestions"]],
        "suggested_guide_sections": candidate["guide_citation_suggestions"],
    }, indent=2)
    last_err = None
    for _ in range(max_retries + 1):
        resp = client.converse(
            modelId=compile_llm.MODEL_SONNET,
            system=[{"text": SYSTEM_PROMPT}],
            messages=[{"role": "user", "content": [{"text": user_msg}]}],
            # 4000: the large-answer-vocabulary questions (570906: dozens of
            # income-type answers) produce big answer_value_maps -- 1500
            # truncated them mid-JSON on the first run (17/24 parse failures).
            inferenceConfig={"temperature": 0, "maxTokens": 4000},
        )
        raw = resp["output"]["message"]["content"][0]["text"].strip()
        # Despite the no-fences instruction, fenced output happens -- strip
        # rather than fail the whole proposal on formatting.
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw
            if raw.rstrip().endswith("```"):
                raw = raw.rstrip()[: -3]
        try:
            return _validate(candidate, json.loads(raw)), None
        except Exception as e:  # noqa: BLE001 -- any parse/validation failure retries
            last_err = f"{type(e).__name__}: {e}"
    return None, last_err


def main() -> None:
    if not os.path.exists(CANDIDATES_PATH):
        raise SystemExit(f"candidates artifact missing at {CANDIDATES_PATH!r} -- "
                         "run discover_fact_candidates.py first")
    with open(CANDIDATES_PATH) as f:
        candidates = json.load(f)["candidates"]
    with open(CATALOG_PATH) as f:
        catalog_names = {e["field_name"] for e in json.load(f)["entries"]}

    client = compile_llm._client()
    proposals, failures = [], []
    for cand in candidates:
        # exclude answers already bound in the signed vocabulary (gift)
        bound = set(cand.get("already_bound_answers", {}))
        answers = [a for a in cand["answer_vocabulary"] if a not in bound]
        if not answers:
            continue
        work = dict(cand)
        work["answer_vocabulary"] = answers
        parsed, err = _call_one(client, work)
        if parsed is None:
            failures.append({"question_key": cand["question_key"], "error": err})
            print(f"  Q{cand['question_key']}: PROPOSAL_FAILED ({err})")
            continue
        for fact in parsed["facts"]:
            fact["exists_in_catalog"] = fact["proposed_field_name"] in catalog_names
        proposals.append({
            "question_key": cand["question_key"],
            "dependent_row_count": cand["dependent_row_count"],
            "already_bound_answers": cand.get("already_bound_answers", {}),
            "llm_proposal": parsed,
        })
        names = [f["proposed_field_name"] for f in parsed["facts"]]
        print(f"  Q{cand['question_key']}: {len(parsed['facts'])} fact(s) proposed "
              f"({', '.join(names[:3])}{'...' if len(names) > 3 else ''}), "
              f"{len(parsed.get('unmapped_answers', {}))} abstained")

    out = {
        "version": 1,
        "trust_tier": "MEDIUM_SME_REVIEW",
        "model": compile_llm.MODEL_SONNET,
        "note": ("LLM-DRAFTED proposals for SME review -- consumed by NOTHING. "
                 "The signed vocabulary changes only when a human promotes a "
                 "proposal through the normal review path. Every real answer is "
                 "either mapped or explicitly abstained (validated per call)."),
        "proposals": proposals,
        "failures": failures,
    }
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)

    lines = [
        "# Fact-Vocabulary Naming Proposals — For SME Review",
        "",
        f"**Drafted by**: {compile_llm.MODEL_SONNET} (temp 0, one-time compile-time pass) · "
        "**Trust tier**: MEDIUM — nothing below is active until you approve it. "
        "The engine and the signed vocabulary are untouched by this document.",
        "",
        "Approving a row = that question's rules start gating automatically on the "
        "named loan fact (the same 5-minute review shape as the gift fact). "
        "Rejecting or editing costs nothing — these are drafts.",
        "",
    ]
    for p in sorted(proposals, key=lambda x: -x["dependent_row_count"]):
        lines.append(f"## Question {p['question_key']} — {p['dependent_row_count']} rules gated")
        if p["already_bound_answers"]:
            lines.append(f"*Already approved: {p['already_bound_answers']}*")
        lines.append("")
        lines.append("| Proposed fact | Type | Answers → value | In catalog? | Confidence |")
        lines.append("|---|---|---|---|---|")
        for fct in p["llm_proposal"]["facts"]:
            amap = "; ".join(f"\"{a}\" → {v}" for a, v in fct["answer_value_map"].items())
            lines.append(
                f"| `{fct['proposed_field_name']}` | {fct['data_type']} | {amap} | "
                f"{'yes' if fct['exists_in_catalog'] else 'NEW — needs catalog entry'} | "
                f"{fct['confidence']} |")
        unmapped = p["llm_proposal"].get("unmapped_answers", {})
        if unmapped:
            lines.append("")
            lines.append("Abstained (model declined to guess): "
                         + "; ".join(f"\"{a}\" ({r})" for a, r in unmapped.items()))
        lines.append("")
    if failures:
        lines.append("## Proposal failures (no guess recorded)")
        for f_ in failures:
            lines.append(f"- Q{f_['question_key']}: {f_['error']}")
    with open(OUT_MD, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"\nwrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(f"STATUS: {len(proposals)} question(s) drafted, {len(failures)} failed "
          "honestly. MEDIUM tier -- review artifact only; the signed vocabulary "
          "is unchanged by this run.")


if __name__ == "__main__":
    main()
