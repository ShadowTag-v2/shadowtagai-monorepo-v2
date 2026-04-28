# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import logging
import os

import requests


class PerplexityClient:
    def __init__(self):
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        self.base_url = "https://api.perplexity.ai/chat/completions"

    def search(self, query: str) -> dict:
        if not self.api_key:
            logging.warning("⚠️ Perplexity API Key missing. Using simulation.")
            return {"simulated": True, "result": f"Simulated search result for: {query}"}

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        payload = {
            "model": "llama-3-sonar-large-32k-online",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert RSTA Scout. Provide concise, high-value intelligence.",
                },
                {"role": "user", "content": query},
            ],
        }

        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.exception(f"❌ Perplexity API Error: {e}")
            return {"error": str(e)}
