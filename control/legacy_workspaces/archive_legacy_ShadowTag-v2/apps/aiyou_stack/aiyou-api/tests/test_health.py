# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["ok"] is True
