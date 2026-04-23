"""tests/unit/test_nexus_boundary.py — NexusDispatcher boundary case tests.

Tests the API Nexus WebSocket endpoint and /trigger_scraper route
for correct behavior under normal and edge conditions.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.api.nexus import app


@pytest.fixture
def client():
    """Create a TestClient for the Nexus FastAPI app."""
    return TestClient(app)


class TestTriggerScraper:
    """Tests for POST /trigger_scraper endpoint."""

    def test_trigger_scraper_returns_200(self, client: TestClient):
        """Endpoint exists and returns 200 with null body."""
        r = client.post("/trigger_scraper")
        assert r.status_code == 200

    def test_trigger_scraper_returns_null(self, client: TestClient):
        """POST /trigger_scraper should return null (pass body)."""
        r = client.post("/trigger_scraper")
        assert r.json() is None

    def test_trigger_scraper_rejects_get(self, client: TestClient):
        """GET /trigger_scraper should return 405 Method Not Allowed."""
        r = client.get("/trigger_scraper")
        assert r.status_code == 405

    def test_trigger_scraper_rejects_put(self, client: TestClient):
        """PUT /trigger_scraper should return 405 Method Not Allowed."""
        r = client.put("/trigger_scraper")
        assert r.status_code == 405


class TestWebSocket:
    """Tests for the WebSocket /ws endpoint.

    The nexus.py endpoint runs ``while True: receive_text()`` so closing the
    client side triggers ``WebSocketDisconnect`` on the server – this is
    expected and must be tolerated by the test harness (Starlette's
    TestClient silently swallows it when ``with`` block exits).
    """

    def test_websocket_connect_and_greeting(self, client: TestClient):
        """WS connection should succeed and send greeting."""
        with client.websocket_connect("/ws") as ws:
            data = ws.receive_text()
            assert "Hello" in data
            assert "Nexus" in data
            ws.close()

    def test_websocket_echo(self, client: TestClient):
        """WS should echo back the sent message."""
        with client.websocket_connect("/ws") as ws:
            _greeting = ws.receive_text()
            ws.send_text("test boundary input")
            response = ws.receive_text()
            assert "test boundary input" in response
            ws.close()

    def test_websocket_empty_message(self, client: TestClient):
        """WS should handle empty string without crashing."""
        with client.websocket_connect("/ws") as ws:
            _greeting = ws.receive_text()
            ws.send_text("")
            response = ws.receive_text()
            assert "Message text was: " in response
            ws.close()

    def test_websocket_large_payload(self, client: TestClient):
        """WS should handle a large payload (10KB)."""
        with client.websocket_connect("/ws") as ws:
            _greeting = ws.receive_text()
            large_msg = "x" * 10240
            ws.send_text(large_msg)
            response = ws.receive_text()
            assert large_msg in response
            ws.close()

    def test_websocket_special_characters(self, client: TestClient):
        """WS should handle special characters."""
        with client.websocket_connect("/ws") as ws:
            _greeting = ws.receive_text()
            special = '<script>alert("xss")</script>'
            ws.send_text(special)
            response = ws.receive_text()
            assert special in response
            ws.close()

    def test_websocket_unicode(self, client: TestClient):
        """WS should handle unicode characters properly."""
        with client.websocket_connect("/ws") as ws:
            _greeting = ws.receive_text()
            ws.send_text("日本語テスト 🔥")
            response = ws.receive_text()
            assert "日本語テスト 🔥" in response
            ws.close()


class TestAppMetadata:
    """Tests for FastAPI app configuration."""

    def test_app_exists(self):
        """The app object should be a FastAPI instance."""
        from fastapi import FastAPI

        assert isinstance(app, FastAPI)

    def test_routes_registered(self, client: TestClient):
        """Core routes should be registered."""
        routes = [r.path for r in app.routes]
        assert "/trigger_scraper" in routes
        assert "/ws" in routes

    def test_openapi_schema(self, client: TestClient):
        """OpenAPI schema should be generated properly."""
        r = client.get("/openapi.json")
        assert r.status_code == 200
        schema = r.json()
        assert "paths" in schema
        assert "/trigger_scraper" in schema["paths"]
