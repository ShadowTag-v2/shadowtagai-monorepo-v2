import os
import unittest

import requests

# Ensure we hit the local server
BASE_URL = "http://127.0.0.1:8001"


class TestHardening(unittest.TestCase):
    def setUp(self):
        self.api_key = os.environ.get("VERDICT_API_KEY", "dev-key")
        self.headers = {"X-API-Key": self.api_key}
        self.payload = {
            "title": "Rate Limit Test Task",
            "vertical": "workplace",
            "urgency": "green",
            "assigned_to_id": "user_001",
        }

    def test_01_health_check(self):
        """Ensure server is up"""
        try:
            r = requests.get(f"{BASE_URL}/health")
            self.assertEqual(r.status_code, 200)
        except requests.exceptions.ConnectionError:
            self.fail("Server is not running on port 8001. Start it first!")

    def test_02_auth_protection(self):
        """Ensure tasks endpoint requires API Key"""
        # No key
        r = requests.post(f"{BASE_URL}/tasks", json=self.payload)
        self.assertEqual(r.status_code, 401, "Should be 401 Unauthorized without key")

        # With key
        r = requests.post(f"{BASE_URL}/tasks", json=self.payload, headers=self.headers)
        if r.status_code == 422:
            print(f"Validation Error: {r.json()}")
        self.assertEqual(r.status_code, 201, "Should be 201 Created with valid key")

    def test_03_rate_limiting(self):
        """Blast the endpoint to trigger 429"""
        print("\n⚡️ BLASTING ENDPOINT FOR RATE LIMIT TEST...")
        # Reset limit by waiting? No, just surge.
        # Limit is 100/minute.
        success_count = 0
        blocked = False

        for i in range(120):
            payload = self.payload.copy()
            payload["title"] = f"Spam {i}"
            r = requests.post(f"{BASE_URL}/tasks", json=payload, headers=self.headers)
            if r.status_code == 201:
                success_count += 1
            elif r.status_code == 429:
                print(f"✅ BLOCKED at request #{i + 1}")
                blocked = True
                break
            else:
                print(f"⚠️ Unexpected status: {r.status_code} - {r.text}")

        self.assertTrue(blocked, "Rate limit did not trigger after 120 requests!")


if __name__ == "__main__":
    unittest.main()
