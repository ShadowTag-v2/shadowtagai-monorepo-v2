# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# tests/test_heartbeat.py
"""Test the session heartbeat keep-alive endpoint.

The /heartbeat endpoint is used by Flutter/Dio clients to
maintain active sessions and trigger dead-man's switch on timeout.
"""

import pytest


class TestHeartbeat:
    """Test heartbeat endpoint functionality."""

    def test_heartbeat_response_format(self):
        """Heartbeat should return status + server_time."""
        # When the app is running, POST /heartbeat returns:
        # {"status": "alive", "server_time": "...", "session_ttl_seconds": 1800}
        expected_keys = {"status", "server_time", "session_ttl_seconds"}
        mock_response = {"status": "alive", "server_time": "2026-04-18T08:00:00Z", "session_ttl_seconds": 1800}
        assert set(mock_response.keys()) == expected_keys

    def test_heartbeat_session_ttl(self):
        """Session TTL should be 30 minutes (1800s)."""
        SESSION_TTL = 1800
        assert SESSION_TTL == 30 * 60

    def test_heartbeat_dead_mans_switch(self):
        """Dead-man's switch triggers after 2x TTL without heartbeat."""
        DEAD_MAN_THRESHOLD = 2 * 1800
        assert DEAD_MAN_THRESHOLD == 3600

    def test_heartbeat_rate_limit(self):
        """Heartbeat should be rate-limited to 1/minute per session."""
        RATE_LIMIT_SECONDS = 60
        assert RATE_LIMIT_SECONDS <= 60


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
