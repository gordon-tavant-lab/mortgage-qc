"""eval_log.py: structured JSONL logging for full pipeline runs."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qc_engine.eval_log import EvalLog, read_events  # noqa: E402


def test_log_writes_one_jsonl_line_per_event(tmp_path):
    log = EvalLog("test-run", log_dir=str(tmp_path))
    log.log("stage_a", "started", loans=5)
    log.log("stage_a", "finished", loans=5, elapsed_s=1.2)
    events = read_events(log.path)
    assert len(events) == 2
    assert events[0]["stage"] == "stage_a" and events[0]["event"] == "started"
    assert events[0]["details"] == {"loans": 5}
    assert events[1]["details"]["elapsed_s"] == 1.2


def test_every_event_carries_run_id_and_timestamp(tmp_path):
    log = EvalLog("run-xyz", log_dir=str(tmp_path))
    entry = log.log("stage", "event")
    assert entry["run_id"] == "run-xyz"
    assert "ts" in entry and entry["ts"].endswith("Z")


def test_log_evidence_chain_carries_input_method_verdict(tmp_path):
    log = EvalLog("test-run", log_dir=str(tmp_path))
    log.log_evidence_chain(entity_id="chk-001", input_={"field": "x", "value": "5"},
                           method="ratio_threshold", verdict="PASS")
    events = read_events(log.path)
    d = events[0]["details"]
    assert d["entity_id"] == "chk-001"
    assert d["input"] == {"field": "x", "value": "5"}
    assert d["method"] == "ratio_threshold"
    assert d["verdict"] == "PASS"


def test_log_cost_reports_zero_explicitly_not_omitted(tmp_path):
    log = EvalLog("test-run", log_dir=str(tmp_path))
    log.log_cost(llm_calls=0, cost_usd=0.0, deterministic_resolution_rate=1.0)
    events = read_events(log.path)
    d = events[0]["details"]
    assert d["llm_calls"] == 0
    assert d["cost_usd"] == 0.0
    assert d["deterministic_resolution_rate"] == 1.0


def test_crash_mid_run_leaves_a_readable_partial_log(tmp_path):
    """Never buffers -- each log() call is its own append+close."""
    log = EvalLog("test-run", log_dir=str(tmp_path))
    log.log("a", "one")
    with open(log.path) as f:
        content_after_one = f.read()
    assert content_after_one.count("\n") == 1
    json.loads(content_after_one.strip())  # already valid, complete JSON


def test_log_dir_created_if_missing(tmp_path):
    nested = str(tmp_path / "does" / "not" / "exist" / "yet")
    log = EvalLog("test-run", log_dir=nested)
    log.log("a", "b")
    assert os.path.isdir(nested)
