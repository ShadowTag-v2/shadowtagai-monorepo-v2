# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_checkout_session():
    """Ensure the /stripe/create-checkout-session endpoint returns the correct payload
    dictating the mock testing checkout session for the UI matrix.
    """
    payload = {"priceId": "price_1Mock123", "quantity": 1}

    response = client.post("/api/v1/stripe/create-checkout-session", json=payload)

    # Assert successful standard status
    assert response.status_code == 200

    # Assert deterministic fallback is functioning
    data = response.json()
    assert "id" in data
    assert "url" in data
    assert data["id"] == "cs_test_mock123456789"
    assert "checkout.stripe.com" in data["url"]
