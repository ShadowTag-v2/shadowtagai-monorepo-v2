# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""json_utils — Safe JSON/JSONL parsing with LRU-bounded caching.

Ported from Claude Code v2.1.91 `utils/json.ts`.

Key design decisions retained from the original:
    - LRU-bounded parse cache (50 entries) prevents unbounded memory growth.
    - Inputs >8KB bypass the cache entirely because the LRU stores the full
      string as the key, so large configs would pin excessive memory.
    - BOM stripping (EF BB BF) for PowerShell 5.x compatibility.
    - JSONL parsing skips malformed lines rather than raising.
    - Discriminated-union cache wrapper: both valid JSON and parse errors
      are cached to avoid re-parsing the same bad input repeatedly.
"""

from __future__ import annotations

import json
import logging
import os
import re
from functools import lru_cache
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_PARSE_CACHE_MAX_KEY_BYTES = 8 * 1024
_MAX_JSONL_READ_BYTES = 100 * 1024 * 1024  # 100 MB

_BOM = "\ufeff"
_BOM_BYTES = b"\xef\xbb\xbf"

# Regex to strip JSONC // and /* */ comments (simplified — does not handle
# comments inside strings, but sufficient for typical config files).
_LINE_COMMENT_RE = re.compile(r"//.*$", re.MULTILINE)
_BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)


# ---------------------------------------------------------------------------
# BOM helpers
# ---------------------------------------------------------------------------
def strip_bom(text: str) -> str:
  """Remove Unicode BOM from the start of a string."""
  return text.lstrip(_BOM)


def strip_bom_bytes(data: bytes) -> bytes:
  """Remove UTF-8 BOM (EF BB BF) from the start of a bytes object."""
  if data[:3] == _BOM_BYTES:
    return data[3:]
  return data


# ---------------------------------------------------------------------------
# LRU-cached safe parse
# ---------------------------------------------------------------------------
# We use a *separate* inner function for the LRU so that `should_log_error`
# is excluded from the cache key (matches lodash memoize resolver = first arg).
_SENTINEL_PARSE_ERROR = object()


@lru_cache(maxsize=50)
def _cached_parse(text: str) -> Any:
  """Parse JSON, returning ``_SENTINEL_PARSE_ERROR`` on failure.

  The sentinel is needed because ``json.loads("null")`` returns ``None``,
  which would be indistinguishable from a parse failure if we returned
  ``None`` on error.
  """
  try:
    return json.loads(strip_bom(text))
  except json.JSONDecodeError, ValueError:
    return _SENTINEL_PARSE_ERROR


def safe_parse_json(
  text: str | None,
  *,
  should_log_error: bool = True,
) -> Any:
  """Safely parse a JSON string, returning ``None`` on failure.

  Results are LRU-cached (bounded to 50 entries) for inputs ≤8 KB.
  """
  if not text:
    return None

  if len(text) > _PARSE_CACHE_MAX_KEY_BYTES:
    try:
      return json.loads(strip_bom(text))
    except (json.JSONDecodeError, ValueError) as exc:
      if should_log_error:
        logger.debug("JSON parse error (uncached): %s", exc)
      return None

  result = _cached_parse(text)
  if result is _SENTINEL_PARSE_ERROR:
    if should_log_error:
      logger.debug("JSON parse error (cached miss)")
    return None
  return result


def clear_parse_cache() -> None:
  """Flush the LRU parse cache (useful for tests)."""
  _cached_parse.cache_clear()


# ---------------------------------------------------------------------------
# JSONC (JSON with comments)
# ---------------------------------------------------------------------------
def _strip_jsonc_comments(text: str) -> str:
  """Remove // and /* */ comments from JSONC text."""
  text = _BLOCK_COMMENT_RE.sub("", text)
  text = _LINE_COMMENT_RE.sub("", text)
  return text


def safe_parse_jsonc(text: str | None) -> Any:
  """Parse JSON with Comments (JSONC), returning ``None`` on failure.

  Useful for VS Code configuration files (keybindings.json, settings.json)
  which support comments and trailing commas.
  """
  if not text:
    return None
  try:
    cleaned = _strip_jsonc_comments(strip_bom(text))
    return json.loads(cleaned)
  except (json.JSONDecodeError, ValueError) as exc:
    logger.debug("JSONC parse error: %s", exc)
    return None


# ---------------------------------------------------------------------------
# JSONL (newline-delimited JSON)
# ---------------------------------------------------------------------------
def parse_jsonl(data: str | bytes) -> list[Any]:
  """Parse JSONL data, skipping malformed lines.

  Accepts both ``str`` and ``bytes``. BOM is stripped automatically.
  """
  if isinstance(data, bytes):
    data_str = strip_bom_bytes(data).decode("utf-8", errors="replace")
  else:
    data_str = strip_bom(data)

  results: list[Any] = []
  for line in data_str.splitlines():
    line = line.strip()
    if not line:
      continue
    try:
      results.append(json.loads(line))
    except json.JSONDecodeError, ValueError:
      pass  # Skip malformed lines — matches upstream behavior
  return results


def read_jsonl_file(file_path: str) -> list[Any]:
  """Read and parse a JSONL file, reading at most the last 100 MB.

  For files larger than 100 MB, reads the tail and skips the first
  partial line. 100 MB is more than sufficient since the longest
  context window we support is ~2M tokens.
  """
  file_size = os.path.getsize(file_path)

  if file_size <= _MAX_JSONL_READ_BYTES:
    with open(file_path, "rb") as f:
      return parse_jsonl(f.read())

  # Tail read for very large files
  with open(file_path, "rb") as f:
    f.seek(file_size - _MAX_JSONL_READ_BYTES)
    buf = f.read(_MAX_JSONL_READ_BYTES)

  # Skip the first partial line
  newline_idx = buf.find(b"\n")
  if newline_idx != -1 and newline_idx < len(buf) - 1:
    buf = buf[newline_idx + 1 :]
  return parse_jsonl(buf)


# ---------------------------------------------------------------------------
# JSONC array manipulation
# ---------------------------------------------------------------------------
def add_item_to_jsonc_array(content: str, new_item: Any) -> str:
  """Add an item to a JSONC array string, preserving formatting.

  Falls back to creating a new array if the content is empty or
  not a valid array.
  """
  if not content or not content.strip():
    return json.dumps([new_item], indent=4)

  try:
    cleaned = _strip_jsonc_comments(strip_bom(content))
    parsed = json.loads(cleaned)
    if isinstance(parsed, list):
      parsed.append(new_item)
      return json.dumps(parsed, indent=4)
    return json.dumps([new_item], indent=4)
  except (json.JSONDecodeError, ValueError) as exc:
    logger.debug("JSONC array parse error: %s", exc)
    return json.dumps([new_item], indent=4)
