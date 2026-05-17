# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

import json
import logging
import os
from collections.abc import Generator

import requests

logger = logging.getLogger("GroundingEngine")


class VertexGroundingEngine:
  """
  Executes grounded queries against the Google Developer Knowledge API
  via Gemini 2.5 Flash Lite streaming.
  """

  def __init__(self):
    # We must pull the raw API_KEY the user just pasted into .env
    self.api_key = os.getenv("API_KEY")
    if not self.api_key:
      raise ValueError("API_KEY is not set in .env")

    self.endpoint = f"https://aiplatform.googleapis.com/v1/publishers/google/models/gemini-3.1-flash-lite-preview:streamGenerateContent?key={self.api_key}"

  def stream_query(self, prompt: str) -> Generator[str, None, None]:
    """
    Streams a grounded response from Vertex AI using Gemini 2.5 Flash Lite.
    """
    payload = {
      "contents": [{"role": "user", "parts": [{"text": prompt}]}],
      # To explicitly enable Google web search grounding:
      "tools": [{"googleSearch": {}}],
    }

    headers = {"Content-Type": "application/json"}

    logger.info(f"Initiating Grounded Vertex Stream for query: '{prompt[:50]}...'")

    try:
      with requests.post(
        self.endpoint, json=payload, headers=headers, stream=True
      ) as response:
        response.raise_for_status()
        for line in response.iter_lines():
          if line:
            decoded_line = line.decode("utf-8")
            # The API returns Server-Sent Events (SSE) or a streaming JSON array
            if decoded_line.startswith("data: "):
              data_str = decoded_line[6:]
              if data_str == "[DONE]":
                break
              try:
                chunk = json.loads(data_str)
                if "candidates" in chunk and chunk["candidates"]:
                  text_chunk = chunk["candidates"][0]["content"]["parts"][0].get(
                    "text", ""
                  )
                  yield text_chunk
              except json.JSONDecodeError:
                pass
            elif decoded_line.startswith("{") or decoded_line.startswith("["):
              # Handle standard JSON array stream format
              try:
                # This handles the specific format `[` then `{},` then `]`
                clean_line = decoded_line.rstrip(",")
                if clean_line in ["[", "]"]:
                  continue
                chunk = json.loads(clean_line)
                if "candidates" in chunk and chunk["candidates"]:
                  text_chunk = chunk["candidates"][0]["content"]["parts"][0].get(
                    "text", ""
                  )
                  yield text_chunk
              except json.JSONDecodeError:
                pass
    except requests.exceptions.RequestException as e:
      logger.error(f"Vertex Grounding Execution Failed: {e}")
      yield f"[ERROR: Grounding Check Failed - {str(e)}]"


if __name__ == "__main__":
  # Test script block
  logging.basicConfig(level=logging.INFO)
  try:
    engine = VertexGroundingEngine()
    print("\n--- DEV KNOWLEDGE GROUNDING TEST ---")
    for text in engine.stream_query("Explain how AI works in a few words"):
      print(text, end="", flush=True)
    print("\n------------------------------------\n")
  except ValueError as e:
    logger.error(e)
