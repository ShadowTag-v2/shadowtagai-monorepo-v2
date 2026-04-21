#!/usr/bin/env python3
"""GUARDIAN :: SELF-HEALING WATCHDOG
Monitors the n-autoresearch/Kosmos/BioAgents Server.
If it crashes, it captures the stack trace, consults Gemini (Simulated), patches the code, and restarts.
"""

import os
import subprocess
import sys
import time

# CONFIGURATION
SERVER_CMD = ["python3", "main.py"]  # Points to the new root main.py
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))

# ANSI COLORS
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"


def log(msg, tier="INFO"):
    timestamp = time.strftime("%H:%M:%S")
    color = GREEN
    if tier == "WARN":
        color = YELLOW
    if tier == "ERROR" or tier == "FATAL":
        color = RED
    if tier == "RECOVERY":
        color = CYAN

    print(f"{color}[GUARDIAN::{tier} @ {timestamp}] {msg}{RESET}")


def mock_gemini_fix(error_trace):
    """Simulates the 'Fix Selbst' loop.
    In production, this sends 'error_trace' to Gemini 1.5 Pro via Vertex AI.
    """
    log(
        f"Consulting Gemini 1.5 Pro for fix (trace length: {len(error_trace)} chars)...", "RECOVERY"
    )
    time.sleep(1)  # Simulate thinking
    log("Gemini suggests: 'Memory leak in Titan Engine. Patching...'", "RECOVERY")
    # Here we would file_writer.write(...) the fix.
    return True


def start_server():
    log(f"Ignition Sequence: {' '.join(SERVER_CMD)}")

    # Environment Setup
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    process = subprocess.Popen(
        SERVER_CMD,
        cwd=WORKING_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        bufsize=1,
        env=env,
        preexec_fn=os.setsid,  # Create new process group
    )
    return process


def monitor_loop():
    crashes = 0
    max_retries = 5

    log("Starting Guardian Watchdog. Tier 30 Active.", "INFO")

    while True:
        process = start_server()

        # Real-time Output Monitoring
        while True:
            # Non-blocking read needed for real robustness, but simplified here:
            output = process.stdout.readline()

            if output == "" and process.poll() is not None:
                break

            if output:
                line = output.strip()
                print(f"  [APP] {line}")

                # ANOMALY DETECTION
                if "ERROR" in line or "Exception" in line or "Traceback" in line:
                    log(f"Anomaly Detected: {line}", "WARN")

        # Process has died
        stderr = process.stderr.read()
        if stderr:
            print(f"{RED}[STDERR]{RESET}\n{stderr}")

        return_code = process.poll()
        log(f"Server Process Died (Exit Code: {return_code})", "ERROR")

        crashes += 1

        if crashes > max_retries:
            log("Maximum crash limit reached. Escalating to Human Operator.", "FATAL")
            sys.exit(1)

        # SELF-HEALING ROUTINE
        log("Initiating Self-Healing Protocol...", "RECOVERY")
        mock_gemini_fix(stderr)

        time.sleep(2)
        log("Restarting System...", "INFO")


if __name__ == "__main__":
    try:
        monitor_loop()
    except KeyboardInterrupt:
        log("Guardian Shutdown Requested.", "INFO")
