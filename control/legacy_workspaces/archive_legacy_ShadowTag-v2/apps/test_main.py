# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
  response = client.get("/health")
  assert response.status_code == 200
  assert response.json() == {"status": "healthy"}
