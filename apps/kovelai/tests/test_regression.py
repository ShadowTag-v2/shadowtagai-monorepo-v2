# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_check_operational():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "operational"


def test_tier_listing():
    response = client.get("/api/v1/tiers")
    assert response.status_code == 200
    tiers = response.json()
    assert "starter" in tiers
    assert "sovereign" in tiers


def test_magic_link_generation():
    payload = {"attorney_id": "attorney_001", "client_email": "client@example.com", "session_rate_cents": 1500, "session_ttl_seconds": 1800}
    response = client.post("/api/v1/magic-link", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "created"
    assert "magic_link" in data


def test_stripe_webhook_stub_accepts_payload():
    payload = {"id": "evt_test_webhook", "type": "payment_intent.succeeded", "data": {"object": {"id": "pi_test_123", "amount": 1500}}}
    response = client.post("/api/v1/stripe/webhook", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "processed"
