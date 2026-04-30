import os
import json
from agnt_context_compactor.compactor import apply_context_compaction
from agnt_vcr.vcr import VCRReplay
from agnt_classifier.classifier import XMLClassifier
from agnt_bash_classifier.telemetry import BashTelemetryTracker


def test_context_compaction():
    context = {
        "messages": [
            {
                "role": "assistant",
                "content": [
                    {"type": "thinking", "thinking": "Let me think...", "signature": "xxx"},
                    {"type": "tool_use", "id": "1", "name": "clear_tool_uses", "input": {"foo": "bar"}},
                    {"type": "tool_use", "id": "2", "name": "run_command", "input": {"cmd": "ls"}},
                ],
            }
        ]
    }
    compacted = apply_context_compaction(context)
    content = compacted["messages"][0]["content"]
    assert len(content) == 3
    assert content[0]["type"] == "text"
    assert "Compacted" in content[0]["text"]
    assert content[1]["type"] == "text"
    assert "Compacted" in content[1]["text"]
    assert content[2]["type"] == "tool_use"  # keep regular tools


def test_vcr_record_replay(tmp_path):
    os.environ["AGNT_VCR_RECORD"] = "1"
    os.environ["AGNT_VCR_REPLAY"] = "0"
    vcr = VCRReplay(cassette_dir=str(tmp_path))

    def my_call():
        return {"result": "success"}

    res = vcr.intercept("test_call", {"arg": 1}, my_call)
    assert res == {"result": "success"}

    os.environ["AGNT_VCR_RECORD"] = "0"
    os.environ["AGNT_VCR_REPLAY"] = "1"
    vcr_replay = VCRReplay(cassette_dir=str(tmp_path))

    def fail_call():
        raise ValueError("Should not run")

    res_replayed = vcr_replay.intercept("test_call", {"arg": 1}, fail_call)
    assert res_replayed == {"result": "success"}


def test_xml_classifier():
    clf = XMLClassifier()
    assert clf.classify("<intent>sql</intent>") == "db_architect"
    assert clf.classify("<search>find user</search>") == "osint_agent"
    assert clf.classify("<unknown>value</unknown>") == "general_agent"
    assert clf.strip_xml("<intent>sql</intent> please query") == "please query"


def test_bash_telemetry(tmp_path):
    log_file = tmp_path / "telemetry.jsonl"
    tracker = BashTelemetryTracker(log_path=str(log_file))

    start = tracker.track_execution_started("echo test", "/cwd")
    tracker.track_execution_completed("echo test", "/cwd", start, 0, 5, 0)

    lines = log_file.read_text().strip().split("\n")
    assert len(lines) == 2

    start_event = json.loads(lines[0])
    assert start_event["event_type"] == "tengu_bash_execution_started"

    complete_event = json.loads(lines[1])
    assert complete_event["event_type"] == "tengu_bash_execution_completed"
    assert "duration_sec" in complete_event["data"]
