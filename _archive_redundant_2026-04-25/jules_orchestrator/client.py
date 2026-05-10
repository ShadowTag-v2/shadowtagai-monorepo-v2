# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Jules API Client — Orchestration layer for autonomous SDLC operations.

Wraps the Jules REST API (v1alpha) with:
  - Source enumeration
  - Session creation and polling (AUTO_CREATE_PR workflows)
  - Plan approval logic (:approvePlan)
  - Robust error handling and logging matching Tengu architecture
"""

from __future__ import annotations

import json
import logging
import os
import time
import urllib.request
import urllib.error
from typing import Any

logger = logging.getLogger(__name__)


class JulesAPIError(Exception):
  """Exception raised for Jules API errors."""

  pass


class JulesClient:
  """Client for the Jules REST API."""

  BASE_URL = "https://jules.googleapis.com/v1alpha"

  def __init__(self, api_key: str | None = None) -> None:
    self._api_key = api_key or os.environ.get("JULES_API_KEY", "")
    if not self._api_key:
      logger.warning("JULES_API_KEY is not set. API calls will fail.")

  def _request(
    self,
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
    max_retries: int = 3,
    retry_delay: float = 1.0,
  ) -> dict[str, Any]:
    """Perform an HTTP request to the Jules API."""
    url = f"{self.BASE_URL}{path}"
    headers = {
      "x-goog-api-key": self._api_key,
      "Content-Type": "application/json",
    }

    data = None
    if payload is not None:
      data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    for attempt in range(max_retries):
      try:
        with urllib.request.urlopen(req) as response:
          response_data = response.read()
          if response_data:
            return json.loads(response_data)
          return {}
      except urllib.error.HTTPError as e:
        error_text = e.read().decode("utf-8") if hasattr(e, "read") else str(e)
        if e.code == 503 and attempt < max_retries - 1:
          logger.warning(
            "Jules API 503 error, retrying attempt %d/%d in %s seconds...",
            attempt + 1,
            max_retries,
            retry_delay,
          )
          time.sleep(retry_delay)
          retry_delay *= 2  # Exponential backoff
          continue
        logger.error("Jules API error %s: %s", e.code, error_text)
        raise JulesAPIError(f"HTTP {e.code}: {error_text}") from e
      except urllib.error.URLError as e:
        logger.error("Jules network error: %s", e.reason)
        raise JulesAPIError(f"Network error: {e.reason}") from e

    raise JulesAPIError(
      f"Failed after {max_retries} attempts."
    )  # Should not reach here

  def list_sources(self) -> list[dict[str, Any]]:
    """List available sources (repositories)."""
    response = self._request("GET", "/sources")
    return response.get("sources", [])

  def create_session(
    self,
    source_name: str,
    automation_mode: str = "AUTO_CREATE_PR",
    task_description: str = "",
  ) -> dict[str, Any]:
    """Create a new Jules session within a source."""
    payload = {
      "automationMode": automation_mode,
      "taskDescription": task_description,
    }
    return self._request("POST", f"/{source_name}/sessions", payload=payload)

  def get_session(self, session_name: str) -> dict[str, Any]:
    """Retrieve a session by its full resource name."""
    return self._request("GET", f"/{session_name}")

  def list_sessions(self, source_name: str) -> list[dict[str, Any]]:
    """List sessions within a source."""
    response = self._request("GET", f"/{source_name}/sessions")
    return response.get("sessions", [])

  def approve_plan(self, session_name: str, message: str = "") -> dict[str, Any]:
    """Approve a pending plan for a session."""
    payload = {}
    if message:
      payload["message"] = message

    return self._request("POST", f"/{session_name}:approvePlan", payload=payload)

  def interact(self, session_name: str, text: str) -> dict[str, Any]:
    """Send an interaction to an active session."""
    payload = {"text": text}
    return self._request("POST", f"/{session_name}/activities", payload=payload)

  def poll_session(
    self, session_name: str, timeout: int = 300, interval: int = 5
  ) -> dict[str, Any]:
    """Poll a session until it reaches a terminal state or requires action."""
    start_time = time.time()
    while time.time() - start_time < timeout:
      session = self.get_session(session_name)
      state = session.get("state", "UNKNOWN")

      logger.info("Session %s state: %s", session_name, state)

      if state in ("COMPLETED", "FAILED", "NEEDS_APPROVAL", "ACTION_REQUIRED"):
        return session

      time.sleep(interval)

    raise JulesAPIError(f"Polling timeout after {timeout} seconds")
