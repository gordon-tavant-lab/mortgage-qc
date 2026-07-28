"""
002c -- multi-model judge panel, escalate-on-any-disagreement.

Real Bedrock models, from a different model family than the compiler
(verified accessible in this project's own AWS account, 2026-07-20):
Mistral Large 3 (mistral.mistral-large-3-675b-instruct) and OpenAI's
gpt-oss-safeguard-120b (openai.gpt-oss-safeguard-120b, purpose-built for
policy/safety classification -- an unusually good fit for a compliance
judge role). See the session's model-access verification for the full
candidate list; these two are the spec's chosen default pair.

Deliberately conservative escalation rule (spec.md FR-008), not a
majority-vote scheme: research found judge panels have real, correlated
blind spots (a large panel yields far fewer truly-independent votes than
its size suggests), so this module never treats "most judges agree" as
good enough -- unanimous, confident agreement is the only path to
auto-approval.

Python 3.9 compatible.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# The two default judge models (spec.md, chosen for genuine family
# diversity from the compiler and from each other; both verified
# accessible in this project's Bedrock account). A future pilot batch may
# add a 3rd (spec.md Assumptions) -- not hardcoded as exactly 2 anywhere
# in this module's logic.
DEFAULT_JUDGE_MODELS = (
    "mistral.mistral-large-3-675b-instruct",
    "openai.gpt-oss-safeguard-120b",
)

DEFAULT_CONFIDENCE_THRESHOLD = 0.8


@dataclass
class JudgeVerdict:
    """One judge model's independent verdict on one compiled rule."""
    judge_model: str
    agrees: bool
    confidence: float
    reasoning: str

    def to_dict(self) -> Dict[str, Any]:
        return {"judge_model": self.judge_model, "agrees": self.agrees,
                "confidence": self.confidence, "reasoning": self.reasoning}


def escalate_or_approve(verdicts: List[JudgeVerdict],
                        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD) -> str:
    """"AUTO_APPROVED" only when every judge agrees AND every judge's
    confidence meets the threshold. ANY disagreement, or any single
    judge's low confidence, escalates -- deliberately no N-of-M majority
    path (FR-008). `confidence_threshold` is a real, tunable parameter,
    not a literature-derived constant (FR-010) -- callers set it from a
    real pilot batch's measured results, not an assumed number."""
    if not verdicts:
        return "ESCALATED"
    all_agree = all(v.agrees for v in verdicts)
    all_confident = all(v.confidence >= confidence_threshold for v in verdicts)
    return "AUTO_APPROVED" if (all_agree and all_confident) else "ESCALATED"


def judge_batch_result(verdicts: List[JudgeVerdict],
                       confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD) -> Dict[str, Any]:
    """The escalation outcome PLUS every judge's individual verdict
    preserved (FR-009) -- an escalated rule must never reach the SME queue
    as an opaque "needs review" with no reasoning attached."""
    return {
        "outcome": escalate_or_approve(verdicts, confidence_threshold),
        "verdicts": [v.to_dict() for v in verdicts],
    }


JUDGE_SYSTEM_PROMPT = """You are reviewing a compiled mortgage QA/QC rule for correctness \
against its source text and any supporting regulatory/guide context provided.

You will be given:
- source_text: the real AMQ workbook row this rule was compiled from
- compiled_check: the structured rule (field/kind/threshold/operator/etc.) a different \
model produced from that source text
- grounding: any retrieved regulatory/guide excerpts that informed the compile (may be empty)

Judge whether compiled_check correctly and completely captures what source_text requires. \
Output ONLY a JSON object (no markdown fences, no prose):
{
  "agrees": true or false,
  "confidence": <float 0.0-1.0, your own calibrated confidence in this verdict>,
  "reasoning": "<one or two sentences explaining your verdict, referencing source_text and/or grounding>"
}

Be skeptical by default -- your job is to catch a wrong rule selection or wrong math, not to \
rubber-stamp. If source_text is genuinely ambiguous even with the grounding provided, say so \
in reasoning and lower your confidence accordingly rather than guessing."""


def judge_check(client, check_dict: Dict[str, Any], source_text: str,
                grounding_text: str, judge_model_id: str) -> JudgeVerdict:
    """One real Bedrock call to one judge model. Kept out of the fast
    pytest suite (same precedent compile_llm.py's compile_row() set) --
    exercised via a standalone script, not unit-tested against a live API."""
    import json
    import re

    user_msg = json.dumps({
        "source_text": source_text,
        "compiled_check": check_dict,
        "grounding": grounding_text,
    }, indent=2)

    resp = client.converse(
        modelId=judge_model_id,
        system=[{"text": JUDGE_SYSTEM_PROMPT}],
        messages=[{"role": "user", "content": [{"text": user_msg}]}],
        inferenceConfig={"temperature": 0, "maxTokens": 500},
    )
    blocks = resp["output"]["message"]["content"]
    raw_text = next((b["text"] for b in blocks if "text" in b), "")
    match = re.search(r"\{.*\}", raw_text, re.S)
    if not match:
        return JudgeVerdict(judge_model=judge_model_id, agrees=False, confidence=0.0,
                            reasoning=f"judge output unparseable: {raw_text[:200]}")
    parsed = json.loads(match.group(0))
    return JudgeVerdict(judge_model=judge_model_id, agrees=bool(parsed.get("agrees", False)),
                        confidence=float(parsed.get("confidence", 0.0)),
                        reasoning=str(parsed.get("reasoning", "")))
