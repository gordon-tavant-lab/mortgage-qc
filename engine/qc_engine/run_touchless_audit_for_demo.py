#!/usr/bin/env python3
"""
live-demo-engine-wiring: single entry-point for the demo's real audit run,
using the standalone engine/ pipeline (the definitive official QC audit
engine, per engine/README.md) instead of p0/qc_engine's earlier bake-off
copy. Ported from p0/qc_engine/run_touchless_audit_for_demo.py
(021-touchless-audit-run) -- same output contract, so the Node backend's
audit route needs only its AUDIT_SCRIPT_PATH changed, not its parsing
logic.

Compiles the gold ruleset (compiler/import_gold_ruleset.py's build_ruleset),
adapts a pulled Touchless loan_application.json payload plus this demo's
one fixed real loan's captured OCR extraction (adapters/touchless_adapter.py)
into the engine's canonical fixture format, runs the real deterministic
engine (engine.run), derives the severity-tiered loan status
(loan_status.py, ported unchanged -- engine.py's own RunResult.qc_failures/
needs_review properties are identical between the two pipelines), and
prints ONE JSON object to stdout: {loanStatus, compiledCheckCount,
excludedCheckCount, runResult} -- the same shape contracts/audit-run.md
(specs/021-touchless-audit-run) documents.

Why a fixed extracted-data fixture, not a live per-document OCR fetch: this
demo's live Touchless "pull application" always returns the same single
real loan (fixed applicationId) -- there is no loan-selection step. Its
extracted data was captured live against the real Touchless QA gateway
(see output/TOUCHLESS-API-LIVE-TEST-2026-08-01.md and the 2026-08-02
Gift-Letter/Purchase-Agreement follow-up) and checked in at
demo/touchless/extracted/ -- the same fixture engine/'s own bake-off
tooling already uses (engine/README.md step 1). Reusing it here is not
fabrication: it is this demo's one real loan's real OCR output, cached
exactly like every other cached document fetch in this app
(RetrievedDocumentViewer's fetch-once-no-retry pattern). If this demo ever
supports selecting among multiple live-pulled loans, this must change to a
live bulk OCR fetch per pulled applicationId -- do not silently keep using
this fixed fixture past that point.

Invoked from the Node backend via `child_process.execFile`, reads the
pulled loan payload from a file path (--loan), never shells out, never
touches the network itself (the Node layer already fetched the loan over
HTTP before calling this script).

Usage:
    python3 run_touchless_audit_for_demo.py --loan path/to/loan_application.json
    cat loan_application.json | python3 run_touchless_audit_for_demo.py
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
_ENGINE_ROOT = os.path.dirname(_HERE)
_REPO_ROOT = os.path.dirname(_ENGINE_ROOT)
if _ENGINE_ROOT not in sys.path:
    sys.path.insert(0, _ENGINE_ROOT)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from qc_engine.engine import run as run_engine  # noqa: E402
from qc_engine.loan_status import derive_loan_status  # noqa: E402
from qc_engine.adapters.touchless_adapter import adapt_touchless_to_fixture  # noqa: E402
from qc_engine.compiler.import_gold_ruleset import build_ruleset  # noqa: E402

sys.path.insert(0, os.path.join(_ENGINE_ROOT, "fixtures", "from_docs"))
from fixture_loader import load_canonical_loan  # noqa: E402

# This demo's one fixed real loan's captured OCR extraction (see module
# docstring for why a checked-in fixture, not a live per-document fetch).
DEFAULT_EXTRACTED_DATA_PATH = os.path.join(
    _REPO_ROOT, "demo", "touchless", "extracted",
    "extracted_data_e59d57a9-2b10-4f36-9206-36dd0e9cd473.json",
)


def run_audit(loan_application_path: str, extracted_data_path: str = DEFAULT_EXTRACTED_DATA_PATH) -> dict:
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

    ruleset, _mapping, stats = build_ruleset()
    run_result = run_engine(loan, ruleset)
    loan_status = derive_loan_status(run_result)

    return {
        "loanStatus": loan_status,
        "compiledCheckCount": stats["converted_total"],
        "excludedCheckCount": stats["unsupported_total"],
        "runResult": run_result.to_dict(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loan", help="Path to a pulled loan_application.json. Reads stdin if omitted.")
    parser.add_argument("--extracted-data", default=DEFAULT_EXTRACTED_DATA_PATH,
                         help="Path to this demo's captured Touchless OCR extraction fixture.")
    args = parser.parse_args()

    if args.loan:
        loan_application_path = args.loan
    else:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8",
        ) as tmp:
            tmp.write(sys.stdin.read())
            loan_application_path = tmp.name

    result = run_audit(loan_application_path, args.extracted_data)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
