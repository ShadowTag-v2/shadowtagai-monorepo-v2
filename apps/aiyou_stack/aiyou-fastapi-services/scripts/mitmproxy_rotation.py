# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import random

from mitmproxy import http

# NOTE: Environment variables loaded via `source scripts/load_mcp_secrets.sh`
# or GCP Secret Manager in production. python-dotenv is banned (GEMINI.md §secrets).

# Load keys from GEMINI_API_KEYS (comma-separated)
# Fallback to single GEMINI_API_KEY if the list is empty
raw_keys = os.getenv("GEMINI_API_KEYS", "")
KEYS = [k.strip() for k in raw_keys.split(",") if k.strip()]

if not KEYS:
    single_key = os.getenv("GEMINI_API_KEY")
    if single_key:
        KEYS = [single_key]

print(f"Loaded {len(KEYS)} API keys for rotation.")


class KeyRotator:
    def request(self, flow: http.HTTPFlow) -> None:
        # Target Google Generative AI API
        if "generativelanguage.googleapis.com" in flow.request.pretty_host and KEYS:
            # Pick a random key
            key = random.choice(KEYS)

            # Replace in query parameters (common for Gemini)
            if "key" in flow.request.query:
                flow.request.query["key"] = key

            # Replace in headers (if used)
            if "x-goog-api-key" in flow.request.headers:
                flow.request.headers["x-goog-api-key"] = key

                # print(f"Rotated to key: ...{key[-4:]}")


addons = [KeyRotator()]
