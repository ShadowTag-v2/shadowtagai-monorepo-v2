# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Cor.Cursor Cinematic Visual Verification Agent.

Removes human QA. Boots Xvfb, records UI via FFmpeg, and self-critiques
using Gemini 3.1 Flash-Lite multimodal vision.

Agent 3 (The Tester) in the Swarm Architecture:
  1. Boot invisible monitor (Xvfb)
  2. Record screen interaction (FFmpeg)
  3. Execute UI test (Playwright / Node script)
  4. Upload recording to Gemini multimodal
  5. Self-critique → PASS or KICKBACK
"""

from __future__ import annotations

import logging
import subprocess
import time

from google import genai

logger = logging.getLogger("Cor-Cursor-Verification")


class CinematicTesterAgent:
    """Agent 3 (The Tester) utilizing Xvfb, Playwright, FFmpeg, and Multimodal Gemini."""

    def __init__(self, tenant_id: str) -> None:
        self.client = genai.Client()
        self.tenant_id = tenant_id

    async def execute_visual_proof(self, task_id: str, _branch_name: str, run_script: str) -> dict:
        """Execute cinematic visual verification for a UI change.

        Args:
            task_id: Unique identifier for the verification task.
            branch_name: Git branch containing the UI change.
            run_script: Path to the Playwright/Node script to execute.

        Returns:
            dict with 'status' ('CLEARED' or 'KICKBACK') and optional 'reason'.
        """
        logger.info("🎬 [COR.CURSOR] Booting Ghost Desktop for %s", task_id)

        video_path = f"/tmp/demo_{task_id}.mp4"

        # 1. Boot Invisible Monitor (Xvfb) & Screen Recorder (FFmpeg)
        xvfb_proc = subprocess.Popen(
            ["Xvfb", ":99", "-screen", "0", "1920x1080x24"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(1)  # Wait for Xvfb to initialize

        ffmpeg_proc = subprocess.Popen(
            [
                "ffmpeg",
                "-y",
                "-f",
                "x11grab",
                "-video_size",
                "1920x1080",
                "-i",
                ":99.0",
                "-preset",
                "ultrafast",
                "-pix_fmt",
                "yuv420p",
                video_path,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        try:
            # 2. Execute UI interaction (Playwright / Node script)
            env = {"DISPLAY": ":99", "PATH": "/usr/bin:/usr/local/bin"}
            subprocess.run(["node", run_script], env=env, timeout=120, check=False)
            time.sleep(2)

        finally:
            # Ensure cleanup of background processes
            ffmpeg_proc.terminate()
            ffmpeg_proc.wait(timeout=10)
            xvfb_proc.terminate()
            xvfb_proc.wait(timeout=10)

        # 3. Multimodal Self-Critique (Gemini 3.1 Flash-Lite)
        logger.info("👁️ [COR.CURSOR] Uploading .mp4 for Multimodal Self-Critique...")
        video_file = self.client.files.upload(file=video_path)

        prompt = (
            "[FEDERAL SUPREMACY PROTOCOL: ACTIVE MITIGATION]\n"
            "You are the QA Reviewer. Watch this UI recording of the feature.\n"
            "Check: Did the modal open correctly? Any CSS glitches or broken states?\n"
            'Respond strictly with JSON: {"status": "PASS|FAIL", "critique": "reasoning"}'
        )
        verdict = self.client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents=[video_file, prompt],
        )

        if "FAIL" in verdict.text.upper():
            logger.warning("❌ Visual Critique Failed. Executing Temporal-Reversal.")
            subprocess.run(["git", "reset", "--hard", "latest-stable"], check=False)
            return {"status": "KICKBACK", "reason": verdict.text}

        logger.info("✅ [COR.CURSOR] Visual verification PASSED for %s", task_id)
        return {"status": "CLEARED"}
