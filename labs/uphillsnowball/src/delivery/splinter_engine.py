# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Splinter Engine — J-39 Information Operations.

95% of compute automates the distribution of our Alpha. Every
successful risk mitigation is a marketing event.

The Splinter Engine transforms J-6 audit receipts into distribution-
ready content and queues it for multi-platform syndication via
Google Cloud Tasks (the EXCLUSIVE queue broker — BullMQ is banned).

Syndication targets:
    - LinkedIn (thought leadership)
    - X/Twitter (real-time alerts)
    - Substack (deep analysis)
    - Client portal (direct value delivery)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

logger = logging.getLogger("J39-Splinter-Engine")


@dataclass
class SyndicationPayload:
    """A structured payload for multi-platform distribution.

    Attributes:
        headline: The syndication headline.
        body: The syndication body text.
        platforms: Target syndication platforms.
        entity: The entity this alert pertains to.
        risk_mitigated: Description of the risk that was mitigated.
        maturity_ring: Current maturity ring (R0-R4).
    """

    headline: str
    body: str
    platforms: list[str] = field(default_factory=lambda: ["linkedin", "x", "substack"])
    entity: str = ""
    risk_mitigated: str = ""
    maturity_ring: str = "R1"


class SplinterSyndication:
    """J-39 Information Operations engine.

    Transforms BoundedAlerts into distribution-ready content and
    queues them via Google Cloud Tasks for multi-platform syndication.

    Args:
        project_id: GCP project ID.
        location: GCP region.
        queue_name: Cloud Tasks queue name.
        delivery_url: The endpoint that handles syndication delivery.
    """

    def __init__(
        self,
        project_id: str = "shadowtag-omega-v4",
        location: str = "us-central1",
        queue_name: str = "splinter",
        delivery_url: str = "https://api.pnkln.io/v5/delivery/social_drip",
    ) -> None:
        self.project_id = project_id
        self.location = location
        self.queue_name = queue_name
        self.delivery_url = delivery_url

    def slice_and_syndicate(
        self,
        alert: dict,
        platforms: list[str] | None = None,
    ) -> dict:
        """Transform an alert into syndication tasks and queue them.

        Each platform gets its own Cloud Tasks entry for independent
        retry and rate limiting.

        Args:
            alert: The BoundedAlert dict from J-6 audit.
            platforms: Target platforms. Defaults to all.

        Returns:
            Dict with task creation status.
        """
        if platforms is None:
            platforms = ["linkedin", "x", "substack"]

        entity = alert.get("entity", {})
        entity_name = entity.get("name", "unknown") if isinstance(entity, dict) else str(entity)

        payload = SyndicationPayload(
            headline=f"pnkln mitigated risk in {entity_name}",
            body=f"Automated risk mitigation: {alert.get('action', 'N/A')}",
            platforms=platforms,
            entity=entity_name,
            risk_mitigated=alert.get("rationale", ""),
        )

        try:
            from google.cloud import tasks_v2

            client = tasks_v2.CloudTasksClient()
            parent = client.queue_path(self.project_id, self.location, self.queue_name)

            tasks_created = []
            for platform in platforms:
                task = {
                    "http_request": {
                        "http_method": tasks_v2.HttpMethod.POST,
                        "url": self.delivery_url,
                        "headers": {"Content-Type": "application/json"},
                        "body": json.dumps(
                            {
                                "payload": payload.headline,
                                "platform": platform,
                                "entity": payload.entity,
                                "body": payload.body,
                            }
                        ).encode(),
                    }
                }

                response = client.create_task(request={"parent": parent, "task": task})
                tasks_created.append(
                    {
                        "platform": platform,
                        "task_name": response.name,
                    }
                )

            logger.info(
                "📢 Splinter: Queued %d syndication tasks for %s",
                len(tasks_created),
                entity_name,
            )
            return {"success": True, "tasks": tasks_created}

        except ImportError:
            logger.warning("google-cloud-tasks not installed. Logging syndication payload.")
            logger.info("📢 Splinter (dry run): %s → %s", payload.headline, platforms)
            return {"success": False, "reason": "cloud_tasks_not_available"}
        except Exception as e:
            logger.error("Splinter syndication failed: %s", e)
            return {"success": False, "reason": str(e)}
