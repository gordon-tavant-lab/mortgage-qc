"""
Layer 1 (spec.md US2, FR-003/FR-004/FR-011): for a row Layer 0 didn't
resolve, extract a precondition from the row's own text -- ONLY when it
states or clearly implies one -- using explicit, separate classification of
deontic modality and cross-reference target *before* extracting the
condition itself (source 2: GDPR deontic-rule-classification precedent),
not one flat "find the condition" prompt.

Reuses `compile_llm.py`'s proven Bedrock-call shape (Sonnet, temperature=0,
one row per call) -- generalized here rather than imported, since this
package has zero `qc_engine` dependency (FR-009) and `compile_llm.py` lives
inside `qc_engine.compiler`.

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional

from ontology_extraction._llm_retry import call_with_retry

REGION = "us-east-1"
PROFILE = "gordon-chan"
MODEL_SONNET = "us.anthropic.claude-sonnet-4-6"

DEONTIC_MODALITIES = ("OBLIGATION", "PERMISSION", "PROHIBITION", "RECOMMENDATION", "NONE")

SYSTEM_PROMPT = """You are analyzing one row from a mortgage post-closing QA/QC rule \
workbook to determine whether it has a stated or clearly-implied APPLICABILITY \
PRECONDITION -- a loan-fact condition that must hold before this row's check applies at \
all (distinct from the check's own pass/fail logic).

You will be given:
- question_text: the AMQ question this row belongs to
- defect_text: the row's own defect/response condition text

Perform THREE SEPARATE classification steps, in order -- do not skip directly to the \
precondition:

1. deontic_modality: classify the row's own normative force as exactly one of \
OBLIGATION (a requirement that must be met), PERMISSION (an allowance, not a requirement), \
PROHIBITION (something that must NOT occur), RECOMMENDATION (a best-practice, not a hard \
requirement), or NONE (the row states a fact/check with no normative language at all).
2. cross_reference_target: does defect_text or question_text name or clearly reference \
ANOTHER loan fact, document, or question whose answer determines whether THIS row's check \
even applies (e.g. "if gift funds were used...", "for borrowers with self-employment \
income...")? If yes, state the referenced topic in a few words. If no such reference exists, \
output null.
3. precondition: ONLY if cross_reference_target is non-null AND the text clearly states or \
unambiguously implies the specific condition (not merely that SOME condition might exist), \
extract it as {"field_name": "<snake_case name for the referenced loan fact>", "operator": \
"==" or "in", "value": "<the specific value(s) that trigger applicability, from the text>"}. \
If genuinely uncertain, or if the text only vaguely gestures at a topic without stating the \
actual triggering value, output null for precondition -- NEVER GUESS. Under-extraction (no \
precondition when one might exist) is the safe failure mode; a wrong/invented precondition \
is not.

Output ONLY a JSON object (no markdown fences, no prose):
{
  "deontic_modality": "OBLIGATION | PERMISSION | PROHIBITION | RECOMMENDATION | NONE",
  "cross_reference_target": "<short phrase or null>",
  "precondition": {"field_name": "...", "operator": "==", "value": "..."} or null,
  "quoted_span": "<the exact substring of defect_text/question_text that supports \
precondition -- REQUIRED if precondition is non-null, omit/null otherwise>"
}
"""


@dataclass
class PreconditionCondition:
    field_name: str
    operator: str
    value: Any


@dataclass
class Layer1Result:
    row_id: str
    deontic_modality: Optional[str] = None
    cross_reference_target: Optional[str] = None
    condition: Optional[PreconditionCondition] = None
    quoted_span: Optional[str] = None
    parse_failed: bool = False
    error: Optional[str] = None


def _extract_json(text: str) -> dict:
    text = text.strip()
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError(f"No JSON object found in LLM output: {text[:200]}")
    return json.loads(m.group(0))


def _parse_response(row_id: str, raw_text: str) -> Layer1Result:
    parsed = _extract_json(raw_text)
    modality = parsed.get("deontic_modality")
    if modality not in DEONTIC_MODALITIES:
        raise ValueError(f"unrecognized deontic_modality: {modality!r}")
    condition = None
    cond_raw = parsed.get("precondition")
    if cond_raw:
        condition = PreconditionCondition(
            field_name=cond_raw["field_name"], operator=cond_raw["operator"],
            value=cond_raw["value"],
        )
    return Layer1Result(
        row_id=row_id, deontic_modality=modality,
        cross_reference_target=parsed.get("cross_reference_target"),
        condition=condition, quoted_span=parsed.get("quoted_span"),
    )


def _client():
    import boto3
    session = boto3.Session(profile_name=PROFILE, region_name=REGION)
    return session.client("bedrock-runtime")


def extract_row(client, row: Dict[str, Any], max_retries: int = 2) -> Layer1Result:
    """One Bedrock call per row (FR-011: retries the call+parse cycle up to
    `max_retries` additional times on malformed output before giving up)."""
    user_msg = json.dumps({
        "question_text": row.get("question_text") or "",
        "defect_text": row.get("defect_text") or "",
    }, indent=2)

    def _call() -> str:
        resp = client.converse(
            modelId=MODEL_SONNET,
            system=[{"text": SYSTEM_PROMPT}],
            messages=[{"role": "user", "content": [{"text": user_msg}]}],
            inferenceConfig={"temperature": 0, "maxTokens": 400},
        )
        return resp["output"]["message"]["content"][0]["text"]

    succeeded, result, error = call_with_retry(
        _call, lambda raw: _parse_response(row["row_id"], raw), max_retries=max_retries,
    )
    if not succeeded:
        return Layer1Result(row_id=row["row_id"], parse_failed=True, error=error)
    return result
