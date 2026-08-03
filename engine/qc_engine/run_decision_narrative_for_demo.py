#!/usr/bin/env python3
"""
live-demo-engine-wiring: single entry-point for the demo's decision narrative (spec014,
"we also need a decision narrative at the end of the results"). Re-runs the same real
audit (build_ruleset + adapt_loan + engine.run -- identical to
run_touchless_audit_for_demo.py, deterministic and cheap, <1s) to get a live RunResult
object, builds a real signed FactVocabulary from the gold ruleset's own Selling Guide
citations (gold_fact_vocabulary.py -- no fabrication), and calls decision_narrative.generate()
against a real Bedrock Sonnet call (bedrock_client.py) -- an actual, billed LLM call, so this
is invoked on-demand (a button), never automatically on every audit run.

Prints ONE JSON object to stdout: the DecisionNarrative's own to_dict() shape.

Usage:
    python3 run_decision_narrative_for_demo.py --loan path/to/loan_application.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ENGINE_ROOT = os.path.dirname(_HERE)
if _ENGINE_ROOT not in sys.path:
    sys.path.insert(0, _ENGINE_ROOT)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from qc_engine.engine import run as run_engine  # noqa: E402
from qc_engine.adapters.touchless_adapter import adapt_touchless_to_fixture  # noqa: E402
from qc_engine.compiler.import_gold_ruleset import build_ruleset, GOLD_RULES_PATH  # noqa: E402
from qc_engine.compiler import gold_fact_vocabulary  # noqa: E402
from qc_engine.compiler import decision_narrative  # noqa: E402
from qc_engine.compiler import bedrock_client  # noqa: E402

sys.path.insert(0, os.path.join(_ENGINE_ROOT, "fixtures", "from_docs"))
from fixture_loader import load_canonical_loan  # noqa: E402

from run_touchless_audit_for_demo import DEFAULT_EXTRACTED_DATA_PATH  # noqa: E402


def run_narrative(loan_application_path: str, extracted_data_path: str = DEFAULT_EXTRACTED_DATA_PATH) -> dict:
    import tempfile

    fixture = adapt_touchless_to_fixture(loan_application_path, extracted_data_path)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8",
    ) as tmp:
        json.dump(fixture, tmp)
        tmp_fixture_path = tmp.name
    try:
        loan = load_canonical_loan(tmp_fixture_path)
    finally:
        os.unlink(tmp_fixture_path)

    ruleset, mapping, _stats = build_ruleset()
    run_result = run_engine(loan, ruleset)

    with open(GOLD_RULES_PATH, "r", encoding="utf-8") as f:
        gold = json.load(f)
    vocabulary = gold_fact_vocabulary.build(gold, mapping)

    client = bedrock_client._client()
    narrative = decision_narrative.generate(run_result, vocabulary, client)
    return narrative.to_dict()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loan", required=True, help="Path to a pulled loan_application.json.")
    parser.add_argument("--extracted-data", default=DEFAULT_EXTRACTED_DATA_PATH)
    args = parser.parse_args()

    result = run_narrative(args.loan, args.extracted_data)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
