# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import json
import subprocess
import time

import requests


def get_service_url():
  try:
    url = (
      subprocess.check_output(
        [
          "gcloud",
          "run",
          "services",
          "describe",
          "judge6-v5",
          "--platform",
          "managed",
          "--region",
          "us-central1",
          "--format",
          "value(status.url)",
        ]
      )
      .decode("utf-8")
      .strip()
    )
    return url
  except Exception as e:
    print(f"Error getting URL: {e}")
    return None


def test_endpoint(base_url, domain, content, metadata={}):
  url = f"{base_url}/judge6/v5/evaluate"
  payload = {"domain": domain, "content": content, "metadata": metadata}
  print(f"\n--- Testing {domain} ---")
  try:
    start = time.time()
    res = requests.post(url, json=payload, timeout=30)
    duration = time.time() - start

    print(f"Status: {res.status_code} ({duration:.2f}s)")
    if res.status_code == 200:
      print("Response:", json.dumps(res.json(), indent=2))
    else:
      print("Error:", res.text)
  except Exception as e:
    print(f"Request Failed: {e}")


def main():
  print("Fetching Service URL...")
  service_url = get_service_url()
  if not service_url:
    print("Could not find service URL. Is it deployed?")
    return

  print(f"Target: {service_url}")

  # 1. Test Shadow AI (Grok)
  test_endpoint(service_url, "SHADOW_AI", "I asked grok.x.ai for the answer.", {})

  # 2. Test VPN Filter (Mocked IP)
  test_endpoint(
    service_url, "VPN_CHECK", "", {"ip_address": "185.159.157.1"}
  )  # NordVPN Mock

  # 3. Test Harm Prevention (Clean)
  test_endpoint(
    service_url, "HARM", "Hello friend, how are you?", {"user_id": "test_user_1"}
  )

  # 4. Test Harm Prevention (Threat)
  test_endpoint(
    service_url,
    "HARM",
    "I will kill you if you do that again.",
    {"user_id": "test_user_2"},
  )


if __name__ == "__main__":
  main()
