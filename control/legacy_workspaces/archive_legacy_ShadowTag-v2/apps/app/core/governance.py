# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Governance Core Utilities"""

import secrets
import time


class GovernanceTracer:
    """
    Manages audit trail traces and signed URLs.
    """

    def __init__(self):
        self._traces: dict[str, str] = {}
        self._expirations: dict[str, float] = {}

    def get_or_generate_trace(self, decision_id: str) -> str:
        """
        Get existing active trace URL or generate new one.
        Returns a mock signed URL for now.
        """
        now = time.time()

        # Check if existing valid trace
        if decision_id in self._traces:
            if self._expirations[decision_id] > now:
                return self._traces[decision_id]
            else:
                del self._traces[decision_id]
                del self._expirations[decision_id]

        # Generate new mock signed URL
        token = secrets.token_urlsafe(32)
        url = f"https://audit.shadowtag.ai/trace/{decision_id}?token={token}&expires=900"

        self._traces[decision_id] = url
        self._expirations[decision_id] = now + 900  # 15 mins

        return url
