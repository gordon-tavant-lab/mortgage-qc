"""
Step 2 of the 002a compile-fidelity spike: LLM compile at config time.

Reuses the Bedrock harness pattern already proven in p0/experiment_g3/llm_arm.py
(temperature=0, AWS profile gordon-chan, cross-region inference profile) rather
than inventing new infrastructure (research.md decision #2).

Model: Sonnet 4.6 — G3 found this the model that caught the boundary-math
failure Haiku missed; this spike measures compiler INTERPRETATION capability
under the best conditions we have, not conflated with using the cheap model.

Output conforms to contracts/compiled-rule-schema.md.

Python 3.9 compatible.
"""
from __future__ import annotations

import json
import os
import re
import sys

import boto3

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "qc_engine"))

os.environ.setdefault("AWS_CA_BUNDLE", "")
REGION = "us-east-1"
PROFILE = "gordon-chan"
MODEL_SONNET = "us.anthropic.claude-sonnet-4-6"

HERE = os.path.dirname(os.path.abspath(__file__))

SYSTEM_PROMPT = """You are compiling a mortgage post-closing QA/QC rule from a real \
lender AMQ (Audit Management Questionnaire) workbook row into a deterministic, \
executable check specification.

You will be given:
- question_text: the AMQ question category
- defect_text: the RESPONSE TEXT describing the defect condition (this is the \
thing you must compile into a rule — a check that FAILS/FLAGS when this \
condition is true)
- engine_kind: which check kind this MUST be (predicate | ratio_threshold | \
agree_categorical | agree_numeric) — determined upstream by classification; \
do not choose a different kind
- significance: the severity tag from the sheet

Output ONLY a JSON object (no markdown fences, no prose) with this exact shape:
{
  "check": {
    "id": "<short-slug-id>",
    "name": "<short human name>",
    "field_name": "<canonical snake_case field name this check reads, invented \
if no catalog exists yet>",
    "kind": "<must equal the given engine_kind>",
    "severity": "CRITICAL | WARNING | INFO",
    "phase": "QC | RECONCILE",
    "predicate": "is_true | is_present (ONLY if kind=predicate, else omit)",
    "ratio": "ltv | dti (ONLY if kind=ratio_threshold, else omit)",
    "threshold": "<Decimal string percent, ONLY if kind=ratio_threshold>",
    "operator": "<= | < | >= | > (ONLY if kind=ratio_threshold)",
    "normalizer": "identity (ONLY if kind=agree_categorical, else omit)",
    "tolerance": "<Decimal string, ONLY if kind=agree_numeric, else omit>",
    "message_pass": "<short pass message>",
    "message_fail": "<short fail/flag message>"
  },
  "plain_english_restatement": "<one sentence restating, in your own words, \
what this check does and when it fails/flags — this is read by a human \
subject-matter expert to judge whether you understood the source condition \
correctly, so be precise about WHAT is being checked>"
}

Constraints (hard):
- kind MUST exactly equal the given engine_kind. Do not substitute a different kind.
- If kind=ratio_threshold, ratio MUST be "ltv" or "dti" — these are the only \
two ratios the engine currently supports. If the defect_text is about a \
different ratio/metric entirely (e.g. credit score, not LTV/DTI), still pick \
whichever of ltv/dti is the closest structural analogue for the THRESHOLD \
MECHANISM being tested, and say so plainly in plain_english_restatement — do \
not silently pretend it is really an LTV/DTI check.
- If kind=predicate, predicate MUST be "is_true" or "is_present" — no other value.
- Never invent a runtime LLM call or free-text logic; this is a static, \
deterministic specification only.
"""


def _client():
    session = boto3.Session(profile_name=PROFILE, region_name=REGION)
    return session.client("bedrock-runtime")


def _extract_json(text: str) -> dict:
    text = text.strip()
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError(f"No JSON object found in LLM output: {text[:200]}")
    return json.loads(m.group(0))


def compile_row(client, row: dict) -> dict:
    user_msg = json.dumps({
        "question_text": row.get("qcode") or row.get("category") or "",
        "defect_text": row["defect_text"],
        "engine_kind": row["engine_kind"],
        "significance": row.get("significance"),
    }, indent=2)

    resp = client.converse(
        modelId=MODEL_SONNET,
        system=[{"text": SYSTEM_PROMPT}],
        messages=[{"role": "user", "content": [{"text": user_msg}]}],
        inferenceConfig={"temperature": 0, "maxTokens": 700},
    )
    raw_text = resp["output"]["message"]["content"][0]["text"]
    try:
        parsed = _extract_json(raw_text)
        parsed["row_id"] = row["row_id"]
        parsed["_parse_error"] = None
    except Exception as e:  # noqa: BLE001 — record, don't crash the batch
        parsed = {"row_id": row["row_id"], "_parse_error": str(e),
                  "_raw_text": raw_text, "check": None,
                  "plain_english_restatement": None}
    parsed["_source_row"] = row
    return parsed


def main() -> int:
    with open(os.path.join(HERE, "artifacts", "sampled_rows.json")) as fh:
        sampled = json.load(fh)

    client = _client()
    drafts = []
    for i, row in enumerate(sampled["rows"]):
        print(f"[{i+1}/{len(sampled['rows'])}] compiling {row['row_id']} "
              f"({row['archetype_id']})...")
        draft = compile_row(client, row)
        drafts.append(draft)

    out_path = os.path.join(HERE, "artifacts", "compiled_drafts.json")
    with open(out_path, "w") as fh:
        json.dump({"model": MODEL_SONNET, "temperature": 0, "drafts": drafts},
                  fh, indent=2, sort_keys=False)
    n_parse_fail = sum(1 for d in drafts if d.get("_parse_error"))
    print(f"\nCompiled {len(drafts)} rows -> {out_path}")
    print(f"Parse failures: {n_parse_fail}/{len(drafts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
