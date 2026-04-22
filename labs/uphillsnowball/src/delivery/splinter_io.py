"""Splinter Distribution Moat — Information Operations (J-39).

Every time Uphill Snowball's Judge 6.1 engine averts a Sullivan & Cromwell
disaster, this module automatically transforms the triumph into viral
enterprise content — broadcasting the failures of firms relying on naked AI
while proving our engine's superiority.

Distribution is the moat. The audience compounds. Every averted hallucination
is a marketing event.
"""

from __future__ import annotations

import json
import logging
import os

from google.cloud import tasks_v2
from temporalio import activity

logger = logging.getLogger("Splinter-IO")

# Narrative template — the S&C weapon.
_TRIUMPH_NARRATIVE = (
    "While Sullivan & Cromwell apologizes to federal judges for AI hallucinations, "
    "Uphill Snowball's Judge 6.1 engine just deterministically verified "
    "{citations_verified} legal citations via PACER API and intercepted "
    "{hallucinations_averted} hallucinations mid-flight before they left our "
    "secure enclave. Stop asking associates to 'verify everything.' "
    "Build a machine that can't lie. Agent-Native infrastructure is here."
)


class SplinterDistributionMoat:
    """Information Operations engine for Uphill Snowball.

    Uses Google Cloud Tasks (the EXCLUSIVE queue broker — BullMQ is banned)
    to syndicate outcome narratives to LinkedIn, X, and enterprise channels.
    """

    def __init__(self) -> None:
        self._project = os.environ.get(
            "GOOGLE_CLOUD_PROJECT", "pnkln-uphill-snowball-v1"
        )
        self._region = os.environ.get("REGION", "us-central1")
        self._queue = "splinter"

    @activity.defn(name="splinter_syndicate_triumph")
    def syndicate_triumph(self, alert: dict) -> dict:
        """Syndicate a triumph narrative to the distribution moat.

        Args:
            alert: Dict with action, tenant_id, citations_verified, etc.

        Returns:
            Dict with task_name confirming enqueue.
        """
        narrative = _TRIUMPH_NARRATIVE.format(
            citations_verified=alert.get("citations_verified", 0),
            hallucinations_averted=alert.get("hallucinations_averted", 0),
        )

        parent = (
            f"projects/{self._project}/locations/{self._region}/queues/{self._queue}"
        )

        task_body = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": "https://api.uphillsnowball.io/v5/media/syndicate/linkedin",
                "body": json.dumps(
                    {"narrative": narrative, "alert": alert}
                ).encode(),
                "headers": {"Content-Type": "application/json"},
            }
        }

        client = tasks_v2.CloudTasksClient()
        response = client.create_task(
            request={"parent": parent, "task": task_body}
        )

        logger.info(
            "📡 SPLINTER IO: Triumph syndicated → %s", response.name
        )
        return {"task_name": response.name, "status": "SYNDICATED"}
