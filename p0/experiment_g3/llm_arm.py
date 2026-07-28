"""
Arm B — the governed runtime-LLM, steelmanned.

Gives Claude (Bedrock, temperature=0, structured JSON) the SAME signed-ruleset
checks and the SAME canonical loan data the deterministic engine sees, and asks
it to return the per-check verdict. This is Olav's approach given its best fair
shot: low temperature, explicit rules, structured output, simple arithmetic.

We deliberately mirror the engine's semantics so the comparison is apples-to-
apples:
  - reconcile checks (agree_*)      -> PASS or FLAG  (doc=truth; mismatch = FLAG)
  - QC checks (predicate/ratio)     -> PASS or FAIL
The LLM is told these rules explicitly.

Python 3.9 compatible. Requires boto3 + AWS profile 'gordon-chan'.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import boto3
from botocore.config import Config

from qc_engine.model import CanonicalLoan
from qc_engine.ruleset import Check, Ruleset

# Known-good Bedrock setup for this workspace (see memory: AWS_CA_BUNDLE quirk).
os.environ.setdefault("AWS_CA_BUNDLE", "")
REGION = "us-east-1"
PROFILE = "gordon-chan"
# Cross-region inference profile prefix required on Bedrock ("us.").
MODEL_HAIKU = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
MODEL_SONNET = "us.anthropic.claude-sonnet-4-6"


def _client():
    session = boto3.Session(profile_name=PROFILE, region_name=REGION)
    return session.client(
        "bedrock-runtime",
        config=Config(retries={"max_attempts": 4, "mode": "adaptive"}),
        verify=False,  # mirrors the AWS_CA_BUNDLE="" workaround
    )


def _check_spec(chk: Check) -> Dict[str, Any]:
    """A compact, faithful description of one check for the prompt."""
    spec: Dict[str, Any] = {
        "id": chk.id, "name": chk.name, "kind": chk.kind,
        "phase": "RECONCILE" if chk.kind in ("agree_categorical", "agree_numeric")
                 else "QC",
        "field": chk.field_name,
    }
    if chk.kind == "agree_categorical":
        spec["rule"] = (f"Compare the document (truth) value vs the system value "
                        f"after normalizing as '{chk.normalizer}'. Equal -> PASS, "
                        f"else FLAG (informational, not a failure).")
    elif chk.kind == "agree_numeric":
        spec["rule"] = (f"Compare document (truth) vs system numerically within "
                        f"tolerance {chk.tolerance}. Within -> PASS, else FLAG.")
    elif chk.kind == "predicate":
        spec["rule"] = (f"QC policy: the document value for '{chk.field_name}' "
                        f"must be true ({chk.predicate}). True -> PASS else FAIL.")
    elif chk.kind == "ratio_threshold":
        spec["rule"] = (f"QC policy: compute {chk.ratio.upper()} = loan_amount / "
                        f"property_value * 100, then require {chk.ratio.upper()} "
                        f"{chk.operator} {chk.threshold}. Satisfied -> PASS else FAIL.")
    return spec


def _loan_payload(loan: CanonicalLoan) -> Dict[str, Any]:
    fields = {}
    for name, sv in loan.fields.items():
        fields[name] = {"doc": sv.doc, "system": sv.system_value()}
    return {"loan_id": loan.loan_id, "fields": fields, "facts": loan.facts}


SYSTEM_PROMPT = (
    "You are a deterministic mortgage QC engine. You evaluate a closed loan "
    "against a fixed set of checks. The closing DOCUMENT is the source of truth; "
    "the SYSTEM value is the lender's record. Follow each check's rule EXACTLY. "
    "Return ONLY valid JSON: a list of objects "
    '{"check_id": str, "status": one of "PASS"|"FAIL"|"FLAG"|"NOT_APPLICABLE"}. '
    "Reconcile checks yield PASS or FLAG; QC checks yield PASS or FAIL. If a "
    "required value is absent, use NOT_APPLICABLE. Do not explain. JSON only."
)


def build_prompt(loan: CanonicalLoan, ruleset: Ruleset) -> str:
    checks = [_check_spec(c) for c in ruleset.checks]
    payload = _loan_payload(loan)
    return (
        "CHECKS:\n" + json.dumps(checks, indent=2) +
        "\n\nLOAN DATA:\n" + json.dumps(payload, indent=2) +
        "\n\nReturn the JSON verdict list now."
    )


def _extract_json(text: str) -> List[Dict[str, Any]]:
    m = re.search(r"\[.*\]", text, re.S)
    if not m:
        return []
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return []


def evaluate_llm(loan: CanonicalLoan, ruleset: Ruleset,
                 model_id: str = MODEL_HAIKU
                 ) -> Tuple[Dict[str, str], Dict[str, int]]:
    """Return ({check_id: status}, {input_tokens, output_tokens})."""
    client = _client()
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "temperature": 0,            # steelman: maximally deterministic
        # NOTE: Haiku 4.5 on Bedrock rejects temperature+top_p together; we keep
        # temperature=0 (the determinism steelman) and omit top_p.
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": build_prompt(loan, ruleset)}],
    }
    resp = client.invoke_model(modelId=model_id, body=json.dumps(body))
    payload = json.loads(resp["body"].read())
    text = "".join(b.get("text", "") for b in payload.get("content", []))
    usage = payload.get("usage", {})
    verdicts = {row.get("check_id"): row.get("status")
                for row in _extract_json(text) if row.get("check_id")}
    tokens = {"input_tokens": usage.get("input_tokens", 0),
              "output_tokens": usage.get("output_tokens", 0)}
    return verdicts, tokens
