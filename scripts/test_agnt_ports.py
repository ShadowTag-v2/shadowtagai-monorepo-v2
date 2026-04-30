import json
import os
import sys

# Add packages to path
sys.path.append(os.path.abspath("packages"))

print("--- Testing Context Compactor ---")
try:
    from agnt_context_compactor.compactor import apply_context_compaction

    context = {
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
            {
                "role": "assistant",
                "content": [
                    {"type": "thinking", "thinking": "Let me think...", "signature": "xxx"},
                    {"type": "tool_use", "id": "1", "name": "clear_tool_uses", "input": {"foo": "bar"}},
                    {"type": "tool_use", "id": "2", "name": "run_command", "input": {"cmd": "ls"}},
                ],
            },
        ]
    }
    compacted = apply_context_compaction(context)
    print(json.dumps(compacted, indent=2))
    print("Context Compactor test PASS\n")
except Exception as e:
    print(f"Context Compactor test FAIL: {e}\n")

print("--- Testing VCR Record/Replay ---")
try:
    from agnt_vcr.vcr import VCRReplay

    os.environ["AGNT_VCR_RECORD"] = "1"
    vcr = VCRReplay(cassette_dir=".beads/cassettes")

    def my_network_call():
        print("    -> Actual network call executed!")
        return {"data": "from network"}

    res = vcr.intercept("my_network_call", {"foo": "bar"}, my_network_call)
    print(f"Recorded response: {res}")

    os.environ["AGNT_VCR_RECORD"] = "0"
    os.environ["AGNT_VCR_REPLAY"] = "1"
    vcr2 = VCRReplay(cassette_dir=".beads/cassettes")

    def my_network_call_fail():
        raise Exception("This should not run because it is replaying!")

    res2 = vcr2.intercept("my_network_call", {"foo": "bar"}, my_network_call_fail)
    print(f"Replayed response: {res2}")
    print("VCR Record/Replay test PASS\n")
except Exception as e:
    print(f"VCR Record/Replay test FAIL: {e}\n")

print("--- Testing XML Classifier ---")
try:
    from agnt_classifier.classifier import XMLClassifier

    clf = XMLClassifier()
    query = "<intent>sql</intent> Can you query the database?"
    route = clf.classify(query)
    stripped = clf.strip_xml(query)
    print(f"Route: {route}")
    print(f"Stripped: {stripped}")
    print("XML Classifier test PASS\n")
except Exception as e:
    print(f"XML Classifier test FAIL: {e}\n")

print("--- Testing Bash Telemetry ---")
try:
    from agnt_bash_classifier.telemetry import BashTelemetryTracker

    tracker = BashTelemetryTracker(log_path=".beads/bash_telemetry_test.jsonl")
    start = tracker.track_execution_started("echo hello", "/tmp")
    tracker.track_execution_completed("echo hello", "/tmp", start, 0, 6, 0)
    with open(".beads/bash_telemetry_test.jsonl") as f:
        print(f.read().strip())
    print("Bash Telemetry test PASS\n")
except Exception as e:
    print(f"Bash Telemetry test FAIL: {e}\n")
