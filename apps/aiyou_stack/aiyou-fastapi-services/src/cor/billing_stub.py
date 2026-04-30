"""Premium Edge Billing Stub.
Mocks metering for low-latency edge inference.
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class EdgeBilling:
    @staticmethod
    def record_usage(client_id: str, pod_id: str, duration_ms: int, tokens: int):
        """Record usage event for billing.
        Rate: $0.10 per 1M tokens + $0.05 per compute second.
        """
        cost = (tokens / 1_000_000 * 0.10) + (duration_ms / 1000 * 0.05)

        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "client_id": client_id,
            "pod_id": pod_id,
            "duration_ms": duration_ms,
            "tokens": tokens,
            "cost_usd": round(cost, 6),
        }

        logger.info(f"BILLING EVENT: {event}")
        return event
