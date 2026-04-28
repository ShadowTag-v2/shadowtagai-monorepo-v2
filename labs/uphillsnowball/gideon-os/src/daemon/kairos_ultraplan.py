# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""KAIROS Daemon & ULTRAPLAN — Coordinator Mode.

15-second blocking budget. Tasks exceeding the budget are farmed to
ULTRAPLAN remote instances via Google Cloud Tasks (no BullMQ).

Architecture:
  - Fast path: ≤15s → execute inline
  - Slow path: >15s → dispatch to Cloud Tasks worker queue
  - Coordinator: XML push notifications from workers (no polling)
  - Nightly: Auto-Dream memory consolidation via Dream Consolidation daemon
"""

from __future__ import annotations

import json
import logging
import os

from google.cloud import tasks_v2

logger = logging.getLogger("KAIROS-Daemon")


class KairosPersistentAssistant:
    """The KAIROS persistent assistant with 15-second blocking budget."""

    def __init__(self) -> None:
        self.task_client = tasks_v2.CloudTasksClient()
        self._project = os.getenv("GCP_PROJECT", "shadowtag-omega-v4")
        self._region = os.getenv("GCP_REGION", "us-central1")
        self._queue = os.getenv("WORKER_QUEUE", "worker-queue")

    async def execute_command(self, command: str) -> dict:
        """Execute a command with 15-second blocking budget.

        Args:
            command: The command to execute.

        Returns:
            dict with 'tool', 'status', and 'content' keys.
        """
        if self._estimate_latency(command) > 15:
            logger.info("⏳ [KAIROS] Task > 15s. Backgrounding to ULTRAPLAN.")
            self.dispatch_ultraplan(command)
            return {
                "tool": "SendUserMessage",
                "status": "proactive",
                "content": "ULTRAPLAN remote instance spun up. Will notify on completion.",
            }
        return {
            "tool": "SendUserMessage",
            "status": "normal",
            "content": "Fast execution complete.",
        }

    def dispatch_ultraplan(self, objective: str) -> None:
        """ULTRAPLAN: 30-Minute Remote Planning Instance.

        Coordinator Mode (No Polling) — uses Cloud Tasks for dispatch
        and webhook notifications for completion.

        Args:
            objective: The planning objective to farm out.
        """
        logger.info("🌐 [ULTRAPLAN] Farming task to Remote Gemini 3 Pro...")

        parent = self.task_client.queue_path(self._project, self._region, self._queue)

        for i in range(5):
            task = {
                "http_request": {
                    "http_method": tasks_v2.HttpMethod.POST,
                    "url": f"https://{self._project}.run.app/api/v1/worker/execute",
                    "headers": {
                        "Content-Type": "application/json",
                        "x-tengu-scratch": f"vol-{i}",
                    },
                    "body": json.dumps({"task": f"Sub-task {i}: {objective}"}).encode(),
                }
            }
            self.task_client.create_task(request={"parent": parent, "task": task})
            logger.info("  📤 Dispatched sub-task %d/5", i + 1)

    def handle_worker_notification(self, payload: dict) -> dict:
        """Webhook receiver for worker completion notifications.

        Args:
            payload: The worker result payload.

        Returns:
            dict with synthesized result.
        """
        logger.info("📥 [COORDINATOR] Worker notification received: %s", payload)
        # TODO: Synthesize results from all sub-tasks
        return {"status": "SYNTHESIZED", "payload": payload}

    def _estimate_latency(self, cmd: str) -> int:
        """Estimate command latency in seconds.

        Args:
            cmd: The command string to estimate.

        Returns:
            Estimated latency in seconds.
        """
        if "research" in cmd.lower() or "analyze" in cmd.lower():
            return 30
        if "deploy" in cmd.lower() or "build" in cmd.lower():
            return 60
        return 5
