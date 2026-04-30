import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class TelemetryEventBus:
    """Real-time high-throughput event router using GCP Pub/Sub (simulated internally for MVP).
    Tracks every action for the Intelligence Pipeline and ROI modeling.
    """

    def __init__(self):
        self.subscribers: dict[str, list[Callable]] = {}
        self.audit_log: list[dict[str, Any]] = []

    def subscribe(self, topic: str, callback: Callable):
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)
        logger.info(f"Registered subscriber for topic: {topic}")

    async def publish(self, topic: str, payload: dict[str, Any]):
        """Publishes event and routes to all registered subscribers async."""
        event = {
            "id": f"evt_{datetime.utcnow().timestamp()}",
            "topic": topic,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": payload,
        }

        # Append to audit trail (SC.2 Immutable Backup equivalent for local tests)
        self.audit_log.append(event)

        logger.debug(f"Publishing event to {topic}: {event['id']}")

        if topic in self.subscribers:
            for callback in self.subscribers[topic]:
                try:
                    await callback(event)
                except Exception as e:
                    logger.error(f"Error in subscriber for {topic}: {e}")

    def get_audit_trail(self) -> list[dict[str, Any]]:
        return self.audit_log
