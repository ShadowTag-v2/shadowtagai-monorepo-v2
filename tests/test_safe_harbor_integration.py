# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Integration tests for the Safe Harbor architecture packages.

Tests:
1. EgressProxy + CircuitBreakerRegistry integration
2. UDS transport round-trip (server → client → server)
3. AsyncVCR record/replay with cassette rotation
4. SubAgentCoordinator bounded-concurrency dispatch

All tests are self-contained — no external services, no network I/O.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
import time
import unittest

# Add packages to path
_PACKAGES_DIR = os.path.join(os.path.dirname(__file__), os.pardir, "packages")
sys.path.insert(0, os.path.abspath(_PACKAGES_DIR))

from agnt_coordinator import SubAgentCoordinator, TaskState
from agnt_upstreamproxy import EgressProxy
from agnt_vcr.async_vcr import AsyncVCR
from circuit_breaker import CircuitBreakerOpenError, CircuitBreakerRegistry


# ─── 1. EgressProxy + Circuit Breaker ─────────────────────────────────


class TestEgressProxyCircuitBreaker(unittest.TestCase):
    """EgressProxy wired to CircuitBreakerRegistry."""

    def setUp(self) -> None:
        self.registry = CircuitBreakerRegistry()
        self.proxy = EgressProxy(registry=self.registry)

    def test_pre_request_passes_for_allowed_url(self) -> None:
        """Allowed URL with CLOSED breaker should pass."""
        url = "https://generativelanguage.googleapis.com/v1/models"
        self.proxy.pre_request(url)
        # No exception = pass

    def test_pre_request_blocks_disallowed_url(self) -> None:
        """Disallowed URL should raise PermissionError."""
        url = "https://evil.example.com/steal-data"
        with self.assertRaises(PermissionError):
            self.proxy.pre_request(url)

    def test_circuit_breaker_trips_after_failures(self) -> None:
        """Host breaker should trip after repeated failures."""
        url = "https://generativelanguage.googleapis.com/v1/models"

        # Record 3 consecutive failures (default threshold)
        for _ in range(3):
            self.proxy.post_request(url, status=500, success=False)

        # Next pre_request should fail with CircuitBreakerOpenError
        with self.assertRaises(CircuitBreakerOpenError):
            self.proxy.pre_request(url)

    def test_circuit_breaker_recovers_after_success(self) -> None:
        """Breaker should recover when a success is recorded via reset."""
        url = "https://generativelanguage.googleapis.com/v1/models"
        host = self.proxy._host_from_url(url)

        # Trip the breaker by recording failures through the proxy
        for _ in range(3):
            self.proxy.post_request(url, status=500, success=False)

        # Verify it's open
        with self.assertRaises(CircuitBreakerOpenError):
            self.proxy.pre_request(url)

        # Reset via the proxy's own registry (same object)
        breaker = self.proxy.registry.get_or_create(host)
        breaker.reset()

        # Should pass again now that the breaker is CLOSED
        self.proxy.pre_request(url)

    def test_health_report_shows_all_hosts(self) -> None:
        """Health report should include all hosts that have been seen."""
        url1 = "https://generativelanguage.googleapis.com/v1/models"
        url2 = "https://firestore.googleapis.com/v1/projects"

        self.proxy.post_request(url1, status=200, success=True)
        self.proxy.post_request(url2, status=200, success=True)

        report = self.proxy.health_report()
        self.assertIn("generativelanguage.googleapis.com", report)
        self.assertIn("firestore.googleapis.com", report)

    def test_host_extraction(self) -> None:
        """Host extraction should handle malformed URLs gracefully."""
        self.assertEqual(self.proxy._host_from_url("https://foo.com/bar"), "foo.com")
        self.assertEqual(self.proxy._host_from_url("not-a-url"), "unknown")
        self.assertEqual(self.proxy._host_from_url(""), "unknown")


# ─── 2. UDS Transport Round-Trip ──────────────────────────────────────


class TestUDSTransportRoundTrip(unittest.TestCase):
    """Unix Domain Socket transport integration test."""

    def test_server_client_round_trip(self) -> None:
        """Start server, connect client, send message, verify echo."""
        from agnt_bridge._types import BridgeMessage
        from agnt_bridge.transport import UDSServer, UDSTransport

        async def _run() -> None:
            with tempfile.TemporaryDirectory() as tmpdir:
                sock_path = os.path.join(tmpdir, "test.sock")
                received: list[BridgeMessage] = []

                async def on_connection(
                    reader: asyncio.StreamReader,
                    writer: asyncio.StreamWriter,
                ) -> None:
                    """Server connection handler: read one message, echo it back."""
                    from agnt_bridge.transport import (
                        _HEADER_SIZE,
                        _decode_payload,
                        _encode_frame,
                    )
                    import struct

                    header = await reader.readexactly(_HEADER_SIZE)
                    (length,) = struct.unpack(">I", header)
                    payload_bytes = await reader.readexactly(length)
                    msg = _decode_payload(payload_bytes)
                    received.append(msg)

                    # Echo back with modified type
                    echo = BridgeMessage(
                        msg_type="echo_response",
                        session_id=msg.session_id,
                        payload=msg.payload,
                        msg_uuid=msg.msg_uuid,
                    )
                    writer.write(_encode_frame(echo))
                    await writer.drain()
                    writer.close()
                    await writer.wait_closed()

                # Start server
                server = UDSServer(sock_path)
                await server.start(on_connection)

                # Connect client and send message
                client = UDSTransport()
                await client.connect(sock_path)

                test_msg = BridgeMessage(
                    msg_type="test_request",
                    session_id="sess-001",
                    payload={"action": "ping", "data": "hello"},
                    msg_uuid="uuid-test-001",
                )
                await client.write(test_msg)

                # Read response
                response = await client.read()
                self.assertIsNotNone(response)
                self.assertEqual(response.msg_type, "echo_response")
                self.assertEqual(response.session_id, "sess-001")
                self.assertEqual(response.payload["action"], "ping")

                # Verify server received the original
                self.assertEqual(len(received), 1)
                self.assertEqual(received[0].msg_type, "test_request")

                await client.close()
                await server.stop()

        asyncio.run(_run())

    def test_connection_to_nonexistent_socket(self) -> None:
        """Connecting to a nonexistent socket should raise ConnectionError."""
        from agnt_bridge.transport import UDSTransport

        async def _run() -> None:
            client = UDSTransport()
            with self.assertRaises(ConnectionError):
                await client.connect("/tmp/nonexistent_socket_12345.sock")

        asyncio.run(_run())


# ─── 3. AsyncVCR ─────────────────────────────────────────────────────


class TestAsyncVCR(unittest.TestCase):
    """Async VCR record/replay with cassette rotation."""

    def test_record_and_replay(self) -> None:
        """Record a cassette, then replay it."""

        async def _run() -> None:
            with tempfile.TemporaryDirectory() as tmpdir:
                os.environ["AGNT_FC_OVERRIDES"] = json.dumps({"vcr_mode": "record"})
                try:
                    recorder = AsyncVCR(cassette_dir=tmpdir, max_age_s=3600)

                    call_count = 0

                    async def mock_api() -> dict:
                        nonlocal call_count
                        call_count += 1
                        return {"status": "ok", "call": call_count}

                    result1 = await recorder.async_intercept(
                        "test.method",
                        {"param": "value"},
                        mock_api,
                    )
                    self.assertEqual(result1["status"], "ok")
                    self.assertEqual(call_count, 1)
                    self.assertEqual(recorder.cassette_count(), 1)

                    # Switch to replay mode
                    os.environ["AGNT_FC_OVERRIDES"] = json.dumps({"vcr_mode": "replay"})
                    replayer = AsyncVCR(cassette_dir=tmpdir, max_age_s=3600)

                    result2 = await replayer.async_intercept(
                        "test.method",
                        {"param": "value"},
                        mock_api,
                    )
                    # Should get the recorded result, not a new call
                    self.assertEqual(result2["status"], "ok")
                    self.assertEqual(call_count, 1)  # Not incremented
                finally:
                    os.environ.pop("AGNT_FC_OVERRIDES", None)

        asyncio.run(_run())

    def test_stale_cassette_rotation(self) -> None:
        """Stale cassettes should be rotated on demand."""

        async def _run() -> None:
            with tempfile.TemporaryDirectory() as tmpdir:
                os.environ["AGNT_FC_OVERRIDES"] = json.dumps({"vcr_mode": "record"})
                try:
                    vcr = AsyncVCR(cassette_dir=tmpdir, max_age_s=0.001)

                    async def mock_api() -> dict:
                        return {"result": True}

                    await vcr.async_intercept("stale.method", {}, mock_api)
                    self.assertEqual(vcr.cassette_count(), 1)

                    # Wait for cassette to become stale
                    time.sleep(0.01)

                    rotated = vcr.rotate_stale()
                    self.assertEqual(rotated, 1)
                    self.assertEqual(vcr.cassette_count(), 0)
                finally:
                    os.environ.pop("AGNT_FC_OVERRIDES", None)

        asyncio.run(_run())

    def test_cassette_stats(self) -> None:
        """Stats should report cassette health."""

        async def _run() -> None:
            with tempfile.TemporaryDirectory() as tmpdir:
                os.environ["AGNT_FC_OVERRIDES"] = json.dumps({"vcr_mode": "record"})
                try:
                    vcr = AsyncVCR(cassette_dir=tmpdir, max_age_s=3600)

                    async def mock_api() -> dict:
                        return {"data": 1}

                    await vcr.async_intercept("stats.method", {}, mock_api)
                    stats = vcr.cassette_stats()
                    self.assertEqual(stats["total_cassettes"], 1)
                    self.assertEqual(stats["stale_cassettes"], 0)
                    self.assertEqual(stats["fresh_cassettes"], 1)
                finally:
                    os.environ.pop("AGNT_FC_OVERRIDES", None)

        asyncio.run(_run())


# ─── 4. SubAgentCoordinator ──────────────────────────────────────────


class TestSubAgentCoordinator(unittest.TestCase):
    """Bounded-concurrency sub-agent dispatch pool."""

    def test_single_dispatch(self) -> None:
        """Single task dispatch should complete."""

        async def _run() -> None:
            coord = SubAgentCoordinator(max_concurrency=2)

            async def simple_task(value: int) -> int:
                return value * 2

            result = await coord.dispatch(
                simple_task,
                task_id="double",
                kwargs={"value": 21},
            )
            self.assertEqual(result.state, TaskState.DONE)
            self.assertEqual(result.result, 42)
            self.assertGreater(result.elapsed_s, 0.0)

        asyncio.run(_run())

    def test_batch_dispatch(self) -> None:
        """Batch dispatch should execute all tasks in parallel."""

        async def _run() -> None:
            coord = SubAgentCoordinator(max_concurrency=4)

            async def square(n: int) -> int:
                await asyncio.sleep(0.01)
                return n * n

            tasks = [
                ("sq_1", square, {"n": 2}),
                ("sq_2", square, {"n": 3}),
                ("sq_3", square, {"n": 4}),
            ]
            results = await coord.dispatch_batch(tasks)
            self.assertEqual(len(results), 3)
            self.assertTrue(all(r.state == TaskState.DONE for r in results))
            values = sorted(r.result for r in results)
            self.assertEqual(values, [4, 9, 16])

        asyncio.run(_run())

    def test_task_timeout(self) -> None:
        """Task exceeding timeout should fail gracefully."""

        async def _run() -> None:
            coord = SubAgentCoordinator(max_concurrency=2, timeout_s=0.05)

            async def slow_task() -> str:
                await asyncio.sleep(10)
                return "never"

            result = await coord.dispatch(slow_task, task_id="slow")
            self.assertEqual(result.state, TaskState.FAILED)
            self.assertIn("Timeout", result.error)

        asyncio.run(_run())

    def test_task_error_isolation(self) -> None:
        """One failing task should not affect others."""

        async def _run() -> None:
            coord = SubAgentCoordinator(max_concurrency=4)

            async def good_task() -> str:
                return "ok"

            async def bad_task() -> str:
                msg = "intentional failure"
                raise RuntimeError(msg)

            tasks = [
                ("good_1", good_task, {}),
                ("bad_1", bad_task, {}),
                ("good_2", good_task, {}),
            ]
            results = await coord.dispatch_batch(tasks)
            states = {r.task_id: r.state for r in results}
            self.assertEqual(states["good_1"], TaskState.DONE)
            self.assertEqual(states["bad_1"], TaskState.FAILED)
            self.assertEqual(states["good_2"], TaskState.DONE)

        asyncio.run(_run())

    def test_bounded_concurrency(self) -> None:
        """Concurrency should be bounded by max_concurrency."""

        async def _run() -> None:
            coord = SubAgentCoordinator(max_concurrency=2)
            active_count = 0
            max_active = 0

            async def tracked_task() -> None:
                nonlocal active_count, max_active
                active_count += 1
                max_active = max(max_active, active_count)
                await asyncio.sleep(0.05)
                active_count -= 1

            tasks = [
                (f"t{i}", tracked_task, {}) for i in range(6)
            ]
            await coord.dispatch_batch(tasks)
            self.assertLessEqual(max_active, 2)

        asyncio.run(_run())

    def test_summary_statistics(self) -> None:
        """Summary should reflect task outcomes accurately."""

        async def _run() -> None:
            coord = SubAgentCoordinator(max_concurrency=4)

            async def ok() -> str:
                return "done"

            async def fail() -> str:
                msg = "boom"
                raise RuntimeError(msg)

            await coord.dispatch(ok, task_id="a")
            await coord.dispatch(ok, task_id="b")
            await coord.dispatch(fail, task_id="c")

            summary = coord.summary()
            self.assertEqual(summary["total_tasks"], 3)
            self.assertEqual(summary["done"], 2)
            self.assertEqual(summary["failed"], 1)
            self.assertAlmostEqual(summary["success_rate"], 2 / 3, places=2)

        asyncio.run(_run())


if __name__ == "__main__":
    unittest.main()
