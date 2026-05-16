# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import sys

try:
  from google import genai

  print(f"✅ google-genai imported: {genai.__file__}")
except ImportError:
  print("❌ google-genai not found")
  sys.exit(1)

PROJECT_ID = "acquired-jet-478701-b3"
LOCATION = "us-central1"

print(f"Python: {sys.version}")
print(f"Testing Client init with project={PROJECT_ID}, location={LOCATION}")

try:
  client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=LOCATION,
    http_options={"api_version": "v1alpha"},
  )
  print("✅ Client initialized successfully")
  print(f"Client config: {client._api_client}")
except Exception as e:
  print(f"❌ Client init failed: {e}")
  # Print dir of error to see attributes
  # print(dir(e))
