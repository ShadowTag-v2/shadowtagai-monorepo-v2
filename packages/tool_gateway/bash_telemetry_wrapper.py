"""
Bash Telemetry Wrapper
Integrates BashTelemetryTracker directly into the command execution pipeline.
"""
from typing import Callable, Any
from agnt_bash_classifier.telemetry import BashTelemetryTracker
import time
import subprocess

def run_command_with_telemetry(command: str, cwd: str, execute_fn: Callable) -> Any:
    tracker = BashTelemetryTracker()
    start_time = tracker.track_execution_started(command, cwd)
    
    try:
        result = execute_fn(command, cwd)
        exit_code = getattr(result, "returncode", 0)
        stdout_len = len(getattr(result, "stdout", ""))
        stderr_len = len(getattr(result, "stderr", ""))
    except Exception as e:
        exit_code = 1
        stdout_len = 0
        stderr_len = len(str(e))
        raise
    finally:
        tracker.track_execution_completed(command, cwd, start_time, exit_code, stdout_len, stderr_len)
        
    return result
