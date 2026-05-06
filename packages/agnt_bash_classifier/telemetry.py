# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

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

    def track_security_check_failed(self, check_id: Any, command: str, message: str = ""):
        """
        Logs `tengu_bash_security_check_failed` — emitted when the 35-check
        pipeline blocks a command.
        """
        self.log_event(
            "tengu_bash_security_check_failed",
            {
                "check_id": int(check_id),
                "check_name": check_id.name if hasattr(check_id, "name") else str(check_id),
                "command": command,
                "message": message,
            },
        )

    def track_security_validated(self, command: str, checks_passed: int, duration_ms: float):
        """
        Logs `tengu_bash_security_validated` — emitted when a command passes
        all 35 security checks.
        """
        self.log_event(
            "tengu_bash_security_validated",
            {"command": command, "checks_passed": checks_passed, "duration_ms": duration_ms},
        )

    def track_jules_session_created(self, source_name: str, session_name: str, automation_mode: str):
        """Logs jules_session_created"""
        self.log_event(
            "jules_session_created",
            {"source_name": source_name, "session_name": session_name, "automation_mode": automation_mode},
        )

    def track_jules_plan_approved(self, session_name: str):
        """Logs jules_plan_approved"""
        self.log_event("jules_plan_approved", {"session_name": session_name})

    def track_jules_api_error(self, endpoint: str, error_msg: str):
        """Logs jules_api_error"""
        self.log_event(
            "jules_api_error",
            {"endpoint": endpoint, "error_msg": error_msg},
        )
