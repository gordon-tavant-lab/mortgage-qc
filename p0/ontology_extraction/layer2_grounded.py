"""
Layer 2 (spec.md US3, FR-005/FR-006/FR-007/FR-011): for the genuine residual
-- no Layer-0 match, no Layer-1 signal -- propose a precondition by
retrieval against a signed knowledge base (reusing `002c`'s
`knowledge_base.retrieve()` directly, FR-010), gated by an automated
grounding-verification check BEFORE any judging/human review, and routed
through `002c`'s judge panel with the outcome always overridden to mandatory
human review (FR-007) -- never auto-approved, regardless of judge
unanimity/confidence.

The ONLY `qc_engine` imports in this entire package live in this one file
(`qc_engine.compiler.knowledge_base`, `qc_engine.compiler.judge_panel`) --
an explicit, spec-sanctioned exception (FR-010; the reusability test,
`test_ontology_reusability.py`, enforces exactly this shape: zero imports
anywhere else in the package, and only these two names here).

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ontology_extraction._llm_retry import call_with_retry

_HERE = os.path.dirname(os.path.abspath(__file__))
_P0_ROOT = os.path.dirname(_HERE)
if _P0_ROOT not in sys.path:
    sys.path.insert(0, _P0_ROOT)

from qc_engine.compiler import knowledge_base as KB  # noqa: E402
from qc_engine.compiler import judge_panel as JP  # noqa: E402

REGION = "us-east-1"
PROFILE = "gordon-chan"
MODEL_SONNET = "us.anthropic.claude-sonnet-4-6"

# The stricter override this Edge Case exists for: a wrong Layer-2
# precondition silently suppresses a real defect, unlike a wrong
# interpretation inside an already-firing check (002c's default use case).
FORCED_HUMAN_REVIEW_OUTCOME = "MANDATORY_HUMAN_REVIEW"

SYSTEM_PROMPT = """You are proposing a mortgage QC rule's applicability precondition, \
sourced ONLY from the retrieved knowledge-base excerpts provided -- never from your own \
general/training knowledge.

You will be given:
- question_text / defect_text: the AMQ row with no stated precondition of its own
- kb_sections: retrieved knowledge-base excerpts (id, content) that may or may not actually \
support a precondition for this row

If, and ONLY if, a kb_section's content clearly and specifically supports a precondition for \
this row, propose it citing the exact kb_section id and quoting the specific supporting \
excerpt verbatim. If no section actually supports a specific precondition, output null -- do \
not propose one anyway.

Output ONLY a JSON object (no markdown fences, no prose):
{
  "precondition": {"field_name": "...", "operator": "==", "value": "..."} or null,
  "cited_section_id": "<the kb_section id you are citing, REQUIRED if precondition is \
non-null>",
  "cited_excerpt": "<the exact substring of that section's content that supports the claim, \
REQUIRED if precondition is non-null>"
}
"""


@dataclass
class PreconditionCondition:
    field_name: str
    operator: str
    value: Any


@dataclass
class Layer2Result:
    row_id: str
    condition: Optional[PreconditionCondition] = None
    kb_program: Optional[str] = None
    kb_version: Optional[int] = None
    cited_section_id: Optional[str] = None
    grounding_verified: bool = False
    judge_outcome: Optional[str] = None
    final_outcome: Optional[str] = None
    parse_failed: bool = False
    error: Optional[str] = None
    rejected_reason: Optional[str] = None


_WORD_RE = re.compile(r"[a-z0-9]+")


def _words(text: str) -> set:
    return set(_WORD_RE.findall((text or "").lower()))


def verify_grounding(cited_excerpt: str, section_content: str, min_overlap: float = 0.6) -> bool:
    """FR-006: an automated grounding-verification check, deterministic and
    testable -- confirms the LLM's claimed excerpt is genuinely a real
    (near-verbatim) substring of the section it claims to cite, not a
    fabricated or unrelated quote. Deliberately simple (keyword-overlap,
    the same style `knowledge_base.retrieve()` already uses) rather than a
    new ML dependency -- catches the concrete failure mode this gate exists
    for (a citation that doesn't actually say what's claimed), per the
    GASP/MiniCheck precedent cited in spec.md."""
    excerpt_words = _words(cited_excerpt)
    if not excerpt_words:
        return False
    overlap = len(excerpt_words & _words(section_content))
    return (overlap / len(excerpt_words)) >= min_overlap


def _extract_json(text: str) -> dict:
    text = text.strip()
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError(f"No JSON object found in LLM output: {text[:200]}")
    return json.loads(m.group(0))


def _parse_response(raw_text: str) -> dict:
    parsed = _extract_json(raw_text)
    cond_raw = parsed.get("precondition")
    if cond_raw and not parsed.get("cited_section_id"):
        raise ValueError("precondition proposed but cited_section_id missing")
    return parsed


def _client():
    import boto3
    session = boto3.Session(profile_name=PROFILE, region_name=REGION)
    return session.client("bedrock-runtime")


def propose(
    client, row: Dict[str, Any], corpus: "KB.KnowledgeBaseCorpus",
    judge_verdicts_fn=None, max_retries: int = 2,
) -> Layer2Result:
    """FR-005/006/007/011. `judge_verdicts_fn(condition, row) -> List[JudgeVerdict]` is
    injectable so callers (and tests) can supply constructed verdicts instead
    of making real judge-model calls."""
    row_id = row["row_id"]
    query_text = f"{row.get('question_text', '')} {row.get('defect_text', '')}"
    sections = KB.retrieve(corpus, query_text)
    if not sections:
        return Layer2Result(row_id=row_id, rejected_reason="no KB sections retrieved")

    sections_by_id = {s.id: s for s in sections}
    user_msg = json.dumps({
        "question_text": row.get("question_text") or "",
        "defect_text": row.get("defect_text") or "",
        "kb_sections": [{"id": s.id, "content": s.content} for s in sections],
    }, indent=2)

    def _call() -> str:
        resp = client.converse(
            modelId=MODEL_SONNET,
            system=[{"text": SYSTEM_PROMPT}],
            messages=[{"role": "user", "content": [{"text": user_msg}]}],
            inferenceConfig={"temperature": 0, "maxTokens": 400},
        )
        return resp["output"]["message"]["content"][0]["text"]

    succeeded, parsed, error = call_with_retry(_call, _parse_response, max_retries=max_retries)
    if not succeeded:
        return Layer2Result(row_id=row_id, parse_failed=True, error=error)

    cond_raw = parsed.get("precondition")
    if not cond_raw:
        return Layer2Result(row_id=row_id, rejected_reason="no supported precondition proposed")

    cited_id = parsed["cited_section_id"]
    cited_section = sections_by_id.get(cited_id)
    if cited_section is None:
        return Layer2Result(
            row_id=row_id, rejected_reason=f"cited_section_id {cited_id!r} not among retrieved sections",
        )

    grounded = verify_grounding(parsed.get("cited_excerpt", ""), cited_section.content)
    if not grounded:
        return Layer2Result(
            row_id=row_id, kb_program=corpus.program, kb_version=corpus.version,
            cited_section_id=cited_id, grounding_verified=False,
            rejected_reason="grounding verification failed -- cited excerpt not supported by section content",
        )

    condition = PreconditionCondition(**cond_raw)

    # FR-007: judge panel runs (for the audit record) but its outcome is
    # ALWAYS overridden -- never auto-approve, regardless of unanimity.
    verdicts: List["JP.JudgeVerdict"] = judge_verdicts_fn(condition, row) if judge_verdicts_fn else []
    judge_result = JP.judge_batch_result(verdicts) if verdicts else {"outcome": "ESCALATED", "verdicts": []}

    return Layer2Result(
        row_id=row_id, condition=condition, kb_program=corpus.program,
        kb_version=corpus.version, cited_section_id=cited_id, grounding_verified=True,
        judge_outcome=judge_result["outcome"], final_outcome=FORCED_HUMAN_REVIEW_OUTCOME,
    )
