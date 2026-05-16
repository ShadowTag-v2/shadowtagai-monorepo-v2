# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""
Prompt Cache Manager — Cache-bust detection for tool/system prompt changes.
Adapted from Claude Code's CacheManager pattern to detect when tools or
system prompts have changed between turns.
"""

import hashlib
import json


class CacheManager:
  """Detects prompt-level cache busts by tracking hash fingerprints of tools and system prompts."""

  def __init__(self):
    self._prev_hashes: dict[str, str] = {}

  def _hash_value(self, value) -> str:
    """SHA-256 hash of a JSON-serializable value."""
    raw = json.dumps(value, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

  def detect_break(self, tools: dict, system: str, token_count: int) -> list[str]:
    """
    Compares current tool/system fingerprints against previously recorded ones.
    Prints a warning for each detected change and returns the list of changed keys.

    Args:
        tools: Dict of tool definitions (name -> config).
        system: The system prompt string.
        token_count: Current token count (unused, reserved for future budget tracking).

    Returns:
        List of keys that changed (e.g. ["bash", "system"]).
    """
    changes = []

    # Check each tool
    for tool_name, tool_config in tools.items():
      current_hash = self._hash_value(tool_config)
      prev_hash = self._prev_hashes.get(f"tool:{tool_name}")

      if prev_hash is not None and current_hash != prev_hash:
        changes.append(tool_name)

      self._prev_hashes[f"tool:{tool_name}"] = current_hash

    # Check system prompt
    system_hash = self._hash_value(system)
    prev_system = self._prev_hashes.get("system")

    if prev_system is not None and system_hash != prev_system:
      changes.append("system")

    self._prev_hashes["system"] = system_hash

    return changes
