"""
live-demo-engine-wiring: minimal Bedrock Converse client factory, extracted from
p0/qc_engine/compiler/compile_llm.py (that file is the AMQ-workbook-direct compiler --
~700 lines of unrelated compile-time rule-drafting logic, deliberately left out of engine/
per its own README's "only what the currently-exercised runtime path imports" discipline).
decision_narrative.py only ever needed `MODEL_SONNET` and a Bedrock client -- this is that,
and nothing else.

Python 3.9 compatible.
"""
from __future__ import annotations

REGION = "us-east-1"
PROFILE = "gordon-chan"
MODEL_SONNET = "us.anthropic.claude-sonnet-4-6"


def _client():
    import boto3
    session = boto3.Session(profile_name=PROFILE, region_name=REGION)
    return session.client("bedrock-runtime")
