# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from google.genai import Client

# Force Project ID
PROJECT_ID = "shadowtag-omega-v2"
LOCATION = "us-central1"

client = Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

CANDIDATES = [
    "gemini-3.0-flash",
    "gemini-3.0-pro-exp",
    "gemini-3.1-flash-lite-preview-thinking-exp-1219",
    "gemini-3.1-flash-lite-preview",
    "gemini-3.1-flash-lite-preview",
]

print(f"--- PROBING INTELLIGENCE SPECTRUM ({PROJECT_ID}) ---")

for model in CANDIDATES:
    try:
        response = client.models.generate_content(
            model=model,
            contents="Confirm functional status.",
        )
        print(f"✅ {model}: ACTIVE")
    except Exception as e:
        error = str(e)
        if "404" in error:
            print(f"❌ {model}: NOT_FOUND")
        elif "403" in error:
            print(f"🚫 {model}: PERMISSION_DENIED")
        else:
            print(f"⚠️ {model}: ERROR ({error[:50]}...)")
