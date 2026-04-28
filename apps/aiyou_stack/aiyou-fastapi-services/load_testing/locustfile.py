# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import random
import subprocess
import time

from locust import HttpUser, between, task


def get_id_token():
    """Fetch OIDC token using gcloud.
    In a real CI/CD env, this would use the metadata server.
    """
    try:
        # Check if we are running in Cloud Build/Run (metadata server available)
        # For local dev, use gcloud
        token = subprocess.check_output(
            ["gcloud", "auth", "print-identity-token"],
            text=True,
        ).strip()
        return token
    except Exception as e:
        print(f"Failed to get ID token: {e}")
        return None


class ShadowTagUser(HttpUser):
    wait_time = between(1, 3)
    token = None

    def on_start(self):
        """Initialize user with auth token."""
        if not ShadowTagUser.token:
            ShadowTagUser.token = get_id_token()

        self.device_id = f"emit_{random.randint(1000, 9999)}"
        # The service expects X-ShadowTag-Key for app logic,
        # AND Authorization header for Cloud Run IAM.
        self.api_key = "test-key-123"

    @task(3)
    def verify_chirp_valid(self):
        """Simulate a valid chirp emission."""
        payload = {
            "emitter_id": "emit_001",
            "chirp_data": "base64_encoded_chirp_data_simulated",
            "timestamp": time.time(),
            "location": {"lat": 37.7749, "lon": -122.4194},
        }

        headers = {"X-ShadowTag-Key": self.api_key, "Authorization": f"Bearer {self.token}"}

        with self.client.post(
            "/verify",
            json=payload,
            headers=headers,
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("verified") is True:
                    response.success()
                else:
                    response.failure(f"Verification failed: {data}")
            elif response.status_code == 403:
                response.failure("403 Forbidden - Check IAM permissions")
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(1)
    def verify_chirp_invalid(self):
        """Simulate a rogue/revoked device."""
        payload = {"emitter_id": "emit_002", "chirp_data": "rogue_data", "timestamp": time.time()}

        headers = {"X-ShadowTag-Key": self.api_key, "Authorization": f"Bearer {self.token}"}

        self.client.post("/verify", json=payload, headers=headers)

    @task(1)
    def health_check(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        self.client.get("/health", headers=headers)
