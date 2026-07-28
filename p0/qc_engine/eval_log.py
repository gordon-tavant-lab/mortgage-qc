"""
eval_log.py -- structured, append-only JSONL logging for full pipeline runs,
written to storage/logs/. Exists to satisfy this project's own CLAUDE.md
requirements ("Evidence Chain Requirement" / "Cost Transparency Requirement"):
every decision in the system should produce a traceable input -> method ->
verdict chain, and every run should report its LLM cost / deterministic-
resolution-rate honestly, not as an afterthought or only on request.

One JSONL file per run (storage/logs/<run_id>.jsonl), one line per event.
Every line carries: run_id, ts (wall-clock, real -- this module is plain
Python invoked directly, not a Workflow script, so datetime.now() is fine),
stage, event, and a `details` payload specific to that event. Never buffers
in memory -- each log() call opens, appends, and closes, so a crash mid-run
still leaves a readable, truthful partial log (audit trail over throughput).

Python 3.9 compatible.
"""
from __future__ import annotations

import datetime
import json
import os
from typing import Any, Dict, List

_HERE = os.path.dirname(os.path.abspath(__file__))
_P0 = os.path.dirname(_HERE)
REPO_ROOT = os.path.dirname(_P0)
LOG_DIR = os.path.join(REPO_ROOT, "storage", "logs")


class EvalLog:
    """One instance per run; wraps one JSONL file under storage/logs/."""

    def __init__(self, run_id: str, log_dir: str = LOG_DIR) -> None:
        self.run_id = run_id
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.path = os.path.join(log_dir, "{}.jsonl".format(run_id))

    def log(self, stage: str, event: str, **details: Any) -> Dict[str, Any]:
        entry = {
            "run_id": self.run_id,
            "ts": datetime.datetime.utcnow().isoformat() + "Z",
            "stage": stage,
            "event": event,
            "details": details,
        }
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, sort_keys=True) + "\n")
        return entry

    def log_evidence_chain(self, entity_id: str, input_: Any, method: str, verdict: str,
                            stage: str = "evidence_chain", **extra: Any) -> Dict[str, Any]:
        """CLAUDE.md's Evidence Chain Requirement: input -> method -> verdict,
        no black boxes. `entity_id` is e.g. a check_id or a derived-fact name."""
        return self.log(stage, "decision", entity_id=entity_id, input=input_,
                        method=method, verdict=verdict, **extra)

    def log_cost(self, llm_calls: int, cost_usd: float,
                 deterministic_resolution_rate: float, **extra: Any) -> Dict[str, Any]:
        """CLAUDE.md's Cost Transparency Requirement: every run reports this
        explicitly, even (especially) when it's zero -- a zero-LLM run stays
        silent about cost otherwise, which reads as an omission, not a fact."""
        return self.log("cost", "cost_summary", llm_calls=llm_calls, cost_usd=cost_usd,
                        deterministic_resolution_rate=deterministic_resolution_rate, **extra)


def read_events(path: str) -> List[Dict[str, Any]]:
    """Read a JSONL log file back as a list of dicts -- for tests/analysis."""
    events = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events
