"""
Bash Classifier Telemetry Port
Brings Claude Code's bash execution telemetry tracking over to AGNT.
"""

import time
import json
import os
from typing import Any


class BashTelemetryTracker:
    def __init__(self, log_path: str = ".beads/bash_telemetry.jsonl"):
        self.log_path = log_path
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def log_event(self, event_type: str, data: dict[str, Any]):
        event = {"timestamp": time.time(), "event_type": event_type, "data": data}
        with open(self.log_path, "a") as f:
            f.write(json.dumps(event) + "\n")

    def track_execution_started(self, command: str, cwd: str):
        """
        Logs `tengu_bash_execution_started` equivalent.
        """
        self.log_event("tengu_bash_execution_started", {"command": command, "cwd": cwd})
        return time.time()

    def track_execution_completed(self, command: str, cwd: str, start_time: float, exit_code: int, stdout_len: int, stderr_len: int):
        """
        Logs `tengu_bash_execution_completed` equivalent.
        """
        duration = time.time() - start_time

        event_name = "tengu_bash_execution_completed" if exit_code == 0 else "tengu_bash_execution_failed"

        self.log_event(
            event_name,
            {"command": command, "cwd": cwd, "duration_sec": duration, "exit_code": exit_code, "stdout_len": stdout_len, "stderr_len": stderr_len},
        )
