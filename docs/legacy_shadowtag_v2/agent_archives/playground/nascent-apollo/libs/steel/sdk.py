# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import logging
import os
import subprocess

logger = logging.getLogger("VelocityEngine")


class VelocityEngine:
    """
    ShadowTag Omega V7 Engine
    - auto_apply=True: Bypasses Human Confirmation
    - Headless: Runs in terminal/background
    """

    def __init__(self, agent_name="VelocityAgent", auto_apply=True):
        self.agent_name = agent_name
        self.auto_apply = auto_apply

    def run_shell(self, command):
        """Executes terminal commands without asking."""
        if self.auto_apply:
            logger.info(f"⚡ EXEC: {command}")
            # shell=True enables piping and complex args.
            # capture_output prevents it from hanging on stdin.
            result = subprocess.run(command, shell=True, text=True, capture_output=True)
            return result.stdout if result.returncode == 0 else result.stderr
        else:
            return "SKIPPED (Auto-Apply Disabled)"

    def write_file(self, path, content):
        """Writes files directly to disk (Bypasses VS Code Editor API)."""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            return f"✅ Wrote {path}"
        except Exception as e:
            return f"❌ Error: {e}"
